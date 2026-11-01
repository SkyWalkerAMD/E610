#!/usr/bin/env python3
"""Validate newly covered official media, including offline installation recovery."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess as sp
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from expanded.prepare import download, extract_iso, sha, run, SOURCE_SHA, IDS
from coverage.stage import stage


def image(target):
    return {'ubuntu': 'ubuntu', 'debian': 'debian', 'almalinux': 'almalinux',
            'rocky': 'rockylinux/rockylinux'}[target['os']] + ':' + target['version']


def fixtures(target, work):
    apt = target['os'] in ('ubuntu', 'debian')
    run('docker', 'build', '--build-arg', 'IMAGE=' + image(target), '-f',
        HERE / 'test.Dockerfile', '-t', 'e610-offline-test', ROOT)
    sources = {}
    if apt:
        iso = work / 'original.iso'
        download(target['iso_url'], iso, target['iso_sha256'])
        tree = sp.check_output(['xorriso', '-indev', str(iso), '-find', '/', '-type', 'f'], text=True)
        files = [line.strip().strip("'") for line in tree.splitlines()]
        if target['os'] == 'ubuntu':
            bootfiles = [p for p in files if p.lower().endswith(('/bootx64.efi', '/grubx64.efi'))]
            if len(bootfiles) == 2:
                (work / 'original-efi').mkdir()
                for path in bootfiles:
                    extract_iso(iso, path, work / 'original-efi' / Path(path).name.lower())
        for entry in target['kernels']:
            kernel = entry['kernel']
            kw = work / kernel
            for area in ('root', 'packages'):
                (kw / area).mkdir(parents=True, exist_ok=True)
            source = {'iso_url': target['iso_url'], 'iso_sha256': target['iso_sha256'], 'packages': {}}
            for path in entry['paths']:
                if path not in files:
                    matches = [p for p in files if Path(p).name == Path(path).name]
                    if len(matches) != 1:
                        raise ValueError(f'Package must resolve uniquely in verified ISO: {path}: {matches}')
                    path = matches[0]
                package = kw / 'packages' / Path(path).name
                extract_iso(iso, path, package)
                source['packages'][path] = sha(package)
                run('dpkg-deb', '-x', package, kw / 'root')
            sources[kernel] = source
    else:
        run('docker', 'build', '--build-arg', 'IMAGE=' + image(target), '-f',
            HERE / 'el-build.Dockerfile', '-t', 'e610-el-build', ROOT)
        for entry in target['kernels']:
            kernel = entry['kernel']
            kw = work / kernel
            for area in ('root', 'packages'):
                (kw / area).mkdir(parents=True, exist_ok=True)
            source = {'repository': target['repository'], 'packages': {}}
            for url in entry['urls']:
                package = kw / 'packages' / url.rsplit('/', 1)[1]
                download(url, package)
                source['packages'][url] = sha(package)
            run('docker', 'run', '--rm', '--network', 'none', '-v', f'{kw}:{kw}', 'e610-el-build', 'bash', '-c',
                'set -euo pipefail; for key in /etc/pki/rpm-gpg/RPM-GPG-KEY-*; do rpmkeys --import "$key"; done; '
                'for p in "$1"/packages/*.rpm; do rpmkeys --checksig "$p"; '
                '(cd "$1/root"; rpm2cpio "$p" | cpio -idm --quiet); done', 'bash', kw)
            run('sudo', 'chown', '-R', f'{os.getuid()}:{os.getgid()}', kw)
            sources[kernel] = source
    for kernel in sources:
        root = work / kernel / 'root'
        if not (root / 'lib').exists():
            (root / 'lib').symlink_to('usr/lib')
    return sources


def validate(target, work, output, kernel, source):
    kw, out = work / kernel, output / kernel
    root = kw / 'root'
    out.mkdir(parents=True)
    candidates = list((root / 'lib/modules' / kernel).glob('kernel/drivers/net/ethernet/intel/ixgbe/ixgbe.ko*'))
    if len(candidates) != 1:
        raise ValueError(f'Expected one stock ixgbe for {kernel}: {candidates}')
    stock = candidates[0]
    info = sp.check_output(['modinfo', str(stock)], text=True)
    (out / 'stock-modinfo.txt').write_text(info)
    native_ids = [i for i in IDS if f'v00008086d0000{i}' in info]
    native = len(native_ids) == len(IDS)
    record = {key: target[key] for key in ('id', 'os', 'version', 'release')}
    record.update(kernel=kernel, native=native, native_pci_ids=native_ids, source=source,
                  stock_module_sha256=sha(stock), commit=os.environ['GITHUB_SHA'], run_id=os.environ['GITHUB_RUN_ID'])
    if not native:
        shutil.copyfile(work / 'ixgbe-6.4.5.tar.gz', kw / 'ixgbe-6.4.5.tar.gz')
        if target['os'] in ('ubuntu', 'debian'):
            run('sudo', 'cp', '-a', str(root / 'usr/src') + '/.', '/usr/src/')
            for kbuild in (root / 'usr/lib').glob('linux-kbuild-*'):
                run('sudo', 'cp', '-a', kbuild, '/usr/lib/')
            headers = Path('/usr/src') / ('linux-headers-' + kernel)
            run('bash', HERE / 'build-driver.sh', kw, out, kernel, headers, 'gcc-11')
        else:
            run('docker', 'run', '--rm', '--network', 'none', '-v', f'{work}:{work}', '-v', f'{output}:{output}',
                '-v', f'{ROOT}:/repo:ro', 'e610-el-build', 'bash', '-c',
                'set -e; rpm -ivh --nodeps "$1"; bash /repo/coverage/build-driver.sh "$2" "$3" "$4" "/usr/src/kernels/$4"',
                'bash', next((kw / 'packages').glob('kernel-devel-*.rpm')), kw, out, kernel)
            run('sudo', 'chown', '-R', f'{os.getuid()}:{os.getgid()}', kw, out)
        dest = root / 'lib/modules' / kernel / 'updates/e610/ixgbe.ko'
        dest.parent.mkdir(parents=True)
        shutil.copyfile(out / 'ixgbe.ko', dest)
        record.update(module_sha256=sha(out / 'ixgbe.ko'), certificate_sha256=sha(out / 'E610-MOK.der'))
    run('depmod', '-b', root, '-a', kernel)
    (out / 'load-order.txt').write_text(sp.check_output(['modprobe', '-d', str(root), '-S', kernel,
                                                      '--show-depends', 'ixgbe'], text=True))
    (out / 'target.json').write_text(json.dumps(record, indent=2) + '\n')
    run('sudo', 'bash', ROOT / 'expanded/smoke.sh', kw, out, kernel, 'native' if native else 'external')
    if not native:
        (kw / 'mok-tools').mkdir()
        run('docker', 'run', '--rm', '--network', 'none', '-v', f'{kw}/mok-tools:/export',
            '-v', f'{ROOT}/expanded:/tests:ro', 'e610-offline-test', '/tests/export-mok.sh')
        run('sudo', 'bash', HERE / 'secure-smoke.sh', kw, out, kernel, target['os'])
        stage(out, record, out / 'payload')
        with (out / 'installer-test.log').open('w') as log:
            result = sp.run(['docker', 'run', '--rm', '--network', 'none', '-v', f'{out}/payload:/package:ro',
                             '-v', f'{root}:/fixture:ro', '-v', f'{HERE}:/tests:ro',
                             'e610-offline-test', '/tests/test-install.sh', kernel], stdout=log, stderr=sp.STDOUT)
        print((out / 'installer-test.log').read_text(), flush=True)
        result.check_returncode()
    print('E610_COVERAGE_TARGET_PASS', target['id'], kernel, flush=True)


def main():
    if os.environ.get('GITHUB_ACTIONS') != 'true' and not Path('/root/E610-DISPOSABLE-BUILDER').is_file():
        raise SystemExit('Run only in an ephemeral CI runner or an explicitly marked disposable build VM')
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--fixtures-only', action='store_true')
    args = parser.parse_args()
    target = next(t for t in json.loads((HERE / 'inventory.json').read_text()) if t['id'] == args.id)
    work, out = args.work.resolve(), args.output.resolve()
    work.mkdir(parents=True)
    out.mkdir(parents=True)
    sources = fixtures(target, work)
    if args.fixtures_only:
        return
    download('https://github.com/intel/ethernet-linux-ixgbe/releases/download/v6.4.5/ixgbe-6.4.5.tar.gz',
             work / 'ixgbe-6.4.5.tar.gz', SOURCE_SHA)
    for kernel, source in sources.items():
        validate(target, work, out, kernel, source)
    (out / 'media-result.json').write_text(json.dumps({'id': target['id'], 'complete': True,
                                                     'kernels': list(sources)}, indent=2) + '\n')


if __name__ == '__main__':
    main()
