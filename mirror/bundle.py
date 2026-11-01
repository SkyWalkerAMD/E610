#!/usr/bin/env python3
"""Preserve the exact r3 tree and add only validated mirror coverage gaps."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess as sp
import sys

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'mirror'
sys.path.insert(0, str(ROOT))
from expanded.stage import checksums

NAME = 'E610-MultiOS-6.4.5-r4'
BASE = 'E610-MultiOS-6.4.5-r3'
BASE_SHA = '81860c8afc9c74778c05d3f2e7a64c491da8d37c7084a1efeb08391b74cc3680'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def native(t):
    return t.get('native', False) or t['kind'] == 'native' or t.get('baseline_kind') == 'native'


def catalog(audit, targets):
    lookup = {(t['os'], t['version'], t['kernel']): t for t in targets}
    families = {'AlmaLinux': 'almalinux', 'CentOS': 'centos', 'Debian': 'debian',
                'RHEL': 'rhel', 'Rocky': 'rocky', 'Ubuntu': 'ubuntu'}
    rows = []
    for r in json.loads(audit.read_text()):
        assert r['status'] != 'audit-error', r['iso']
        family, filename = r['iso'].split('/', 1)
        os_id = families[family]
        version = re.search(r'\d+\.\d+' if os_id == 'ubuntu' else r'\d+', filename).group()
        kernels = {}
        for boot in r['boots']:
            assert boot['modules'], r['iso']
            for module in boot['modules']:
                key = os_id, version, module['kernel']
                assert key in lookup, ('Uncovered live ISO kernel', r['iso'], key)
                assert module['all_e610_ids'], ('Live ISO boot driver lacks E610 IDs', r['iso'])
                entry = kernels.setdefault(module['kernel'], {'kernel': module['kernel'],
                    'package_target': lookup[key]['id'], 'action': 'native' if native(lookup[key]) else 'offline-driver',
                    'boot_paths': []})
                entry['boot_paths'].append({'initrd': boot['initrd'], 'kernel_sha256': boot['kernel_sha256'],
                    'initrd_sha256': boot['initrd_sha256'], 'ixgbe_sha256': module['sha256'],
                    'pci_ids': module['pci_ids']})
        assert kernels
        rows.append({'iso': r['iso'], 'size': r['size'], 'os': os_id, 'version': version,
                     'kernels': list(kernels.values())})
    return {'scope': 'Linux installation ISOs in the user-designated mirror',
            'verification': 'Read-only extraction of boot kernels and ixgbe PCI aliases; no full-ISO digest claimed',
            'linux_iso_count': len(rows), 'all_kernel_entries_covered': True,
            'rhel10_or_oracle_media_present': False, 'images': rows}


def main():
    p = argparse.ArgumentParser()
    for name in ('baseline', 'validated', 'audit', 'source', 'work', 'output'):
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    assert sha(a.baseline) == BASE_SHA
    work, output = a.work.resolve(), a.output.resolve()
    work.mkdir(parents=True, exist_ok=False)
    output.mkdir(parents=True, exist_ok=False)
    bundle = work / NAME
    bundle.mkdir()
    sp.run(['tar', '-xzf', str(a.baseline.resolve()), '-C', str(work)], check=True)
    baseline = bundle / 'baseline'
    shutil.move(str(work / BASE), baseline)
    sp.run(['sha256sum', '--status', '-c', 'SHA256SUMS'], cwd=baseline, check=True)
    targets = json.loads((baseline / 'manifest.json').read_text())['targets']
    rows = []
    for t in targets:
        t['native'] = bool(native(t))
        t['inherited_kind'] = t['kind']
        t['kind'] = 'baseline'
        t['delegated_release'] = 'v6.4.5-multios-r3'
        rows.append((t['os'], t['version'], t['kernel'], 'baseline', 'baseline'))
    for expected in json.loads((HERE / 'inventory.json').read_text()):
        out = a.validated / expected['id']
        completed = json.loads((out / 'complete.json').read_text())
        assert completed['complete'] and completed['id'] == expected['id']
        t = json.loads((out / 'target.json').read_text())
        for field in expected:
            assert t[field] == expected[field], (expected['id'], field)
        k = t['kernel']
        assert f'E610_KERNEL_LOAD_PASS kernel={k} kind={"native" if t["native"] else "external"}' in (out / 'boot.log').read_text()
        kind, path = ('native', '-') if t['native'] else ('imported', 'payloads/' + t['id'])
        if not t['native']:
            assert completed['installer_template_sha256'] == sha(ROOT / 'coverage/install.sh.in')
            assert f'E610_INSTALLER_TEST_PASS kernel={k}' in (out / 'installer-test.log').read_text()
            assert sha(out / 'payload/ixgbe.ko') == t['module_sha256']
            assert sha(out / 'payload/E610-MOK.der') == t['certificate_sha256']
            sp.run(['sha256sum', '--status', '-c', 'SHA256SUMS'], cwd=out / 'payload', check=True)
            shutil.copytree(out / 'payload', bundle / path)
        evidence = bundle / 'evidence' / t['id']
        evidence.mkdir(parents=True)
        for item in out.iterdir():
            if item.is_file() and item.suffix in ('.log', '.json', '.txt'):
                shutil.copyfile(item, evidence / item.name)
        t['kind'] = kind
        targets.append(t)
        rows.append((t['os'], t['version'], k, kind, path))
    assert len({tuple(r[:3]) for r in rows}) == len(rows)
    live = catalog(a.audit, targets)
    (bundle / 'MIRROR-COVERAGE.json').write_text(json.dumps(live, indent=2) + '\n')
    (bundle / 'targets.tsv').write_text(''.join('\t'.join(r) + '\n' for r in rows))
    shutil.copyfile(HERE / 'dispatch.sh', bundle / 'install.sh')
    for name in ('INSTALL.zh-CN.md', 'VALIDATION.zh-CN.md', 'inventory.json'):
        shutil.copyfile(HERE / name, bundle / name)
    (bundle / 'source').mkdir()
    shutil.copyfile(a.source, bundle / 'source/E610-source.tar.gz')
    shutil.copyfile(baseline / 'source/ixgbe-6.4.5.tar.gz', bundle / 'source/ixgbe-6.4.5.tar.gz')
    table = '# E610 多系统 r4 精确支持清单\n\n仅支持 x86_64 / amd64，不升级内核。未列出的更新内核不等同于已验证。\n\n'
    table += '| 系统 / 安装版本 | 精确内核 | 处理方式 |\n| --- | --- | --- |\n'
    for t in targets:
        label = '原生支持，无需安装' if t['native'] else ('沿用 r3 原模块、证书及回退点' if t['kind'] == 'baseline' else '离线驱动；关闭 Secure Boot')
        table += f'| {t["os"]} {t["release"]} | `{t["kernel"]}` | {label} |\n'
    table += f'\n本次核对镜像库中的 {live["linux_iso_count"]} 张 Linux ISO，全部已识别内核均有对应入口。\n'
    table += 'RHEL 10 和 Oracle Linux/UEK 在指定镜像库中不存在，本轮未验证；Windows、内存测试镜像及其他架构不在本项目 Linux 包范围。\n'
    (bundle / 'SUPPORTED-SYSTEMS.zh-CN.md').write_text(table)
    manifest = {'package': NAME, 'architecture': 'x86_64', 'targets': targets,
        'commit': os.environ['E610_SOURCE_COMMIT'], 'source_archive_sha256': sha(a.source),
        'baseline_archive_sha256': BASE_SHA, 'kernel_replaced': False,
        'network_required_on_target': False, 'compiler_required_on_target': False,
        'media_type': 'nonbootable driver data ISO', 'physical_e610': 'not_tested',
        'mirror_linux_iso_count': live['linux_iso_count']}
    (bundle / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    checksums(bundle)
    archive = output / (NAME + '.tar.gz')
    sp.run(['tar', '--owner=0', '--group=0', '--numeric-owner', '-czf', str(archive), '-C', str(work), NAME], check=True)
    header = (ROOT / 'multios/launcher.sh.in').read_text().replace('6.4.5-r1', '6.4.5-r4')
    begin, end = header.index("    echo '自动识别系统"), header.index('    exit 0')
    header = header[:begin] + "    cat <<'E610_SUPPORTED_MATRIX'\n" + table + 'E610_SUPPORTED_MATRIX\n' + header[end:]
    header = header.replace('@ARCHIVE_SHA256@', sha(archive)).replace('@PAYLOAD_LINE@', str(header.count('\n') + 1))
    installer = output / (NAME + '.run')
    installer.write_bytes(header.encode() + archive.read_bytes())
    installer.chmod(0o755)
    media = work / 'iso-root'
    media.mkdir()
    shutil.copyfile(installer, media / installer.name)
    (media / 'install.sh').write_text('#!/bin/bash\nset -e\nhere=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)\nexec bash "$here/' + NAME + '.run" "$@"\n')
    for name in ('INSTALL.zh-CN.md', 'SUPPORTED-SYSTEMS.zh-CN.md', 'VALIDATION.zh-CN.md', 'manifest.json', 'MIRROR-COVERAGE.json'):
        shutil.copyfile(bundle / name, media / name)
        shutil.copyfile(bundle / name, output / name)
    checksums(media)
    sp.run(['xorriso', '-as', 'mkisofs', '-iso-level', '3', '-r', '-J', '-joliet-long', '-V', 'E610_MULTIOS',
            '-o', str(output / (NAME + '.iso')), str(media)], check=True)
    checksums(output)
    print(f'E610_MIRROR_BUNDLE_PASS targets={len(targets)} linux_isos={live["linux_iso_count"]}')


if __name__ == '__main__':
    main()
