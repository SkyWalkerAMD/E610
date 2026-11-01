#!/usr/bin/env python3
"""Assemble a fail-closed unified package from completed, hash-checked tests."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess as sp
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from expanded.stage import checksums

NAME = 'E610-MultiOS-6.4.5-r3'
BASE = 'E610-MultiOS-6.4.5-r2'
BASE_SHA = '8a3b65589e4b55afef48f6fd797f8c8b08bdb2ec342c3954adfc45d44b686c94'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(path, marker):
    if marker not in path.read_text():
        raise ValueError(f'Missing validation {marker}: {path}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs', type=Path, action='append', required=True)
    for name in ('baseline', 'source', 'work', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    assert sha(args.baseline) == BASE_SHA, 'Original r2 package checksum'
    work, output = args.work.resolve(), args.output.resolve()
    work.mkdir(parents=True, exist_ok=False)
    output.mkdir(parents=True, exist_ok=False)
    bundle = work / NAME
    bundle.mkdir()
    sp.run(['tar', '-xzf', str(args.baseline.resolve()), '-C', str(work)], check=True)
    baseline = bundle / 'baseline'
    shutil.move(str(work / BASE), baseline)
    sp.run(['sha256sum', '--status', '-c', 'SHA256SUMS'], cwd=baseline, check=True)
    records = json.loads((baseline / 'manifest.json').read_text())['targets']
    rows, known = [], set()
    for item in records:
        key = item['os'], item['version'], item['kernel']
        assert key not in known
        known.add(key)
        item['baseline_kind'] = item['kind']
        item['kind'] = 'baseline'
        item['original_release'] = 'v6.4.5-multios-r2'
        rows.append((*key, 'baseline', 'baseline'))

    completed, imported = {}, {}
    for folder in args.inputs:
        for marker in folder.glob('**/media-result.json'):
            data = json.loads(marker.read_text())
            if data.get('complete'):
                completed[data['id']] = (data, marker.parent)
        for marker in folder.glob('**/import-complete.json'):
            data = json.loads(marker.read_text())
            if data.get('complete'):
                imported[data['id']] = marker.parent

    def add(item, directory, imported_module=False):
        key = item['os'], item['version'], item['kernel']
        assert key not in known, key
        known.add(key)
        kernel = item['kernel']
        native = item['native']
        kind = 'native' if native else ('imported' if imported_module else 'external')
        if imported_module:
            assert item['previous_kernel_load'] == 'passed'
            assert item['previous_manual_and_pxe_installation'] == 'passed'
            require(directory / 'installer-test.log', f'E610_INSTALLER_TEST_PASS kernel={kernel}')
            assert json.loads((directory / 'import-complete.json').read_text())['installer_template_sha256'] == sha(HERE / 'install.sh.in')
        else:
            require(directory / 'boot.log', f'E610_KERNEL_LOAD_PASS kernel={kernel} kind={"native" if native else "external"}')
            if not native:
                require(directory / 'secure-boot.log', f'E610_SECURE_BOOT_LOAD_PASS kernel={kernel}')
                require(directory / 'installer-test.log', f'E610_INSTALLER_TEST_PASS kernel={kernel}')
        path = '-'
        if not native:
            payload = directory / 'payload'
            assert sha(payload / 'ixgbe.ko') == item['module_sha256']
            if item.get('certificate_sha256', 'unsigned') != 'unsigned':
                assert sha(payload / 'E610-MOK.der') == item['certificate_sha256']
            sp.run(['sha256sum', '--status', '-c', 'SHA256SUMS'], cwd=payload, check=True)
            path = f'payloads/{item["os"]}-{item["version"]}-{kernel}'
            shutil.copytree(payload, bundle / path)
        evidence = bundle / 'evidence' / item['id'] / kernel
        evidence.mkdir(parents=True)
        for p in directory.iterdir():
            if p.is_file() and p.suffix in ('.log', '.txt', '.json'):
                shutil.copyfile(p, evidence / p.name)
        item['kind'] = kind
        rows.append((*key, kind, path))
        records.append(item)

    inventory = json.loads((HERE / 'inventory.json').read_text())
    for target in inventory:
        assert target['id'] in completed, f'Incomplete media: {target["id"]}'
        data, directory = completed[target['id']]
        assert set(data['kernels']) == {k['kernel'] for k in target['kernels']}
        for kernel in data['kernels']:
            item = json.loads((directory / kernel / 'target.json').read_text())
            assert item['id'] == target['id'] and item['kernel'] == kernel
            add(item, directory / kernel)
    for target in json.loads((HERE / 'imported-inventory.json').read_text()):
        assert target['id'] in imported, f'Incomplete imported installer: {target["id"]}'
        directory = imported[target['id']]
        item = json.loads((directory / 'target.json').read_text())
        for field in ('os', 'version', 'kernel', 'module_sha256', 'certificate_sha256', 'source_sha256'):
            assert item[field] == target[field], (target['id'], field)
        add(item, directory, imported_module=True)

    (bundle / 'targets.tsv').write_text(''.join('\t'.join(row) + '\n' for row in rows))
    shutil.copyfile(HERE / 'dispatch.sh', bundle / 'install.sh')
    for name in ('INSTALL.zh-CN.md', 'VALIDATION.zh-CN.md', 'inventory.json', 'imported-inventory.json'):
        shutil.copyfile(HERE / name, bundle / name)
    (bundle / 'source').mkdir()
    shutil.copyfile(args.source, bundle / 'source/E610-source.tar.gz')
    shutil.copyfile(baseline / 'source/ixgbe-6.4.5.tar.gz', bundle / 'source/ixgbe-6.4.5.tar.gz')
    table = '# E610 多系统 r3 精确支持清单\n\n仅支持 x86_64 / amd64；不升级系统内核。未列出的系统或更新内核不等同于已验证。\n\n'
    table += '| 系统 / 安装版本 | 精确内核 | 处理方式 |\n| --- | --- | --- |\n'
    labels = {'baseline': '沿用 r2 原包、证书和备份', 'external': '离线驱动；已验证 Secure Boot',
              'imported': '沿用 ISO Kit 模块；关闭 Secure Boot', 'native': '原生支持，无需安装'}
    for item in records:
        kind = 'native' if item.get('baseline_kind') == 'native' else item['kind']
        table += f'| {item["os"]} {item["release"]} | `{item["kernel"]}` | {labels[kind]} |\n'
    table += '\nRHEL 10 尚未取得原版镜像验证；Oracle Linux / UEK、其他架构及任意更新内核不在本包已验证范围。\n'
    (bundle / 'SUPPORTED-SYSTEMS.zh-CN.md').write_text(table)
    manifest = {'package': NAME, 'architecture': 'x86_64', 'targets': records,
                'commit': os.environ['E610_SOURCE_COMMIT'], 'source_archive_sha256': sha(args.source),
                'baseline_archive_sha256': BASE_SHA, 'kernel_replaced': False,
                'compiler_required_on_target': False, 'network_required_on_target': False,
                'media_type': 'nonbootable driver data ISO', 'physical_e610': 'not_tested'}
    (bundle / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    checksums(bundle)
    archive = output / (NAME + '.tar.gz')
    sp.run(['tar', '--owner=0', '--group=0', '--numeric-owner', '-czf', str(archive), '-C', str(work), NAME], check=True)
    header = (ROOT / 'multios/launcher.sh.in').read_text().replace('6.4.5-r1', '6.4.5-r3')
    start, end = header.index("    echo '自动识别系统"), header.index('    exit 0')
    header = header[:start] + "    cat <<'E610_SUPPORTED_MATRIX'\n" + table + 'E610_SUPPORTED_MATRIX\n' + header[end:]
    header = header.replace('@ARCHIVE_SHA256@', sha(archive))
    header = header.replace('@PAYLOAD_LINE@', str(header.count('\n') + 1))
    installer = output / (NAME + '.run')
    installer.write_bytes(header.encode() + archive.read_bytes())
    installer.chmod(0o755)
    media = work / 'iso-root'
    media.mkdir()
    shutil.copyfile(installer, media / installer.name)
    (media / 'install.sh').write_text('#!/bin/bash\nset -e\nhere=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)\nexec bash "$here/' + NAME + '.run" "$@"\n')
    for name in ('INSTALL.zh-CN.md', 'SUPPORTED-SYSTEMS.zh-CN.md', 'VALIDATION.zh-CN.md', 'manifest.json'):
        shutil.copyfile(bundle / name, media / name)
        shutil.copyfile(bundle / name, output / name)
    checksums(media)
    sp.run(['xorriso', '-as', 'mkisofs', '-iso-level', '3', '-r', '-J', '-joliet-long', '-V', 'E610_MULTIOS',
            '-o', str(output / (NAME + '.iso')), str(media)], check=True)
    checksums(output)
    print(f'E610_COVERAGE_BUNDLE_PASS targets={len(records)}')


if __name__ == '__main__':
    main()
