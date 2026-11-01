#!/usr/bin/env python3
"""Retest released modules against original media without modifying the mirror.

All writes, mounts and container storage are confined to --work. RHEL user
spaces are assembled offline from the caller's licensed original installation
DVD. No RHEL media or credentials are included in the output artifacts.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess as sp
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from coverage.stage import stage


def run(*args, **kwargs):
    return sp.run([str(a) for a in args], check=True, **kwargs)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def extract(iso, source, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    run('xorriso', '-osirrox', 'on', '-indev', iso, '-extract', source, dest,
        stdout=sp.DEVNULL, stderr=sp.DEVNULL)


def fixture(item, iso, work):
    kernel = item['kernel']
    root = work / 'root'
    if (work / 'fixture-complete.json').exists():
        assert json.loads((work / 'fixture-complete.json').read_text())['iso_sha256'] == item['source_sha256']
        return root
    root.mkdir(parents=True, exist_ok=True)
    tree = sp.check_output(['xorriso', '-indev', str(iso), '-find', '/', '-type', 'f'],
                           text=True, stderr=sp.DEVNULL)
    paths = [p.strip().strip("'") for p in tree.splitlines()]
    if item['os'] in ('debian', 'ubuntu'):
        pattern = r'(?:linux-image|linux-modules|linux-modules-extra)-' + re.escape(kernel) + r'_[^/]+\.deb'
    else:
        pattern = r'(?:kernel|kernel-core|kernel-modules|kernel-modules-core|kernel-modules-extra)-' + re.escape(kernel) + r'\.rpm'
    packages = [p for p in paths if re.fullmatch(pattern, Path(p).name)]
    assert packages, (item['id'], 'original kernel packages absent')
    sums = {}
    for name in packages:
        package = work / 'packages' / Path(name).name
        extract(iso, name, package)
        sums[name] = digest(package)
        if name.endswith('.rpm'):
            run('bash', '-o', 'pipefail', '-c', 'cd "$1"; rpm2cpio "$2" | cpio -idm --quiet',
                'bash', root, package)
        else:
            # dpkg is not required on the mirror host. ar and tar extract the
            # data member without running any package installation scripts.
            members = sp.check_output(['ar', 't', str(package)], text=True).splitlines()
            member = next(m for m in members if m.startswith('data.tar.'))
            run('bash', '-o', 'pipefail', '-c', 'ar p "$1" "$2" | tar -x -C "$3"',
                'bash', package, member, root)
    if not (root / 'lib').exists():
        (root / 'lib').symlink_to('usr/lib')
    run('depmod', '-b', root, '-a', kernel)
    (work / 'fixture-complete.json').write_text(json.dumps({'iso_sha256': item['source_sha256'], 'packages': sums}, indent=2))
    return root


def rhel_root(item, iso, work):
    root = work / 'rootfs'
    if (work / 'rootfs-complete').exists():
        return root
    mount = work / 'dvd'
    mount.mkdir(parents=True, exist_ok=True)
    root.mkdir(exist_ok=True)
    run('mount', '-o', 'loop,ro,nosuid,nodev', iso, mount)
    try:
        repos = [mount] if item['version'] == '7' else [mount / 'BaseOS', mount / 'AppStream']
        args = ['dnf', '--noplugins', '-y', '--installroot=' + str(root), '--releasever=' + item['release'],
                '--disablerepo=*', '--setopt=install_weak_deps=False', '--setopt=keepcache=False', '--nogpgcheck']
        for n, repo in enumerate(repos):
            args += ['--repofrompath=dvd' + str(n) + ',file://' + str(repo)]
        args += ['install', 'bash', 'coreutils', 'grep', 'sed', 'gawk', 'findutils', 'util-linux',
                 'kmod', 'dracut', 'gzip', 'tar', 'xz', 'cpio', 'diffutils', 'mokutil', 'redhat-release']
        run(*args)
        (work / 'rootfs-complete').write_text(item['source_sha256'] + '\n')
    finally:
        run('umount', mount)
    return root


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--originals', type=Path, required=True)
    p.add_argument('--kit', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--only-os')
    p.add_argument('--prepare-only', action='store_true')
    args = p.parse_args()
    work, output = args.work.resolve(), args.output.resolve()
    work.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    items = json.loads((ROOT / 'coverage/imported-inventory.json').read_text())
    modules = {m['kernel']: m for m in json.loads((args.kit / 'release-manifest.json').read_text())['modules']}
    checked = {}
    for item in items:
        if args.only_os and item['os'] not in args.only_os.split(','):
            continue
        item = dict(item)
        kw = work / item['id']
        out = output / item['id'] / item['kernel']
        if (out / 'import-complete.json').exists():
            continue
        iso = (args.originals / item['source_iso']).resolve()
        assert iso.is_relative_to(args.originals.resolve()) and iso.is_file(), iso
        if iso not in checked:
            checked[iso] = digest(iso)
        assert checked[iso] == item['source_sha256'], f'Original ISO checksum mismatch: {item["source_iso"]}'
        module = args.kit / 'work/drivers' / item['kernel']
        assert digest(module / 'ixgbe.ko') == modules[item['kernel']]['files']['ixgbe.ko'] == item['module_sha256']
        if not (out / 'payload').exists():
            stage(module, item, out / 'payload')
        root = fixture(item, iso, kw)
        (out / 'target.json').write_text(json.dumps(item, indent=2) + '\n')
        shutil.copyfile(kw / 'fixture-complete.json', out / 'fixture-source.json')
        if args.prepare_only:
            print('E610_IMPORT_FIXTURE_READY', item['id'], flush=True)
            continue
        command = ['podman', '--root', str(work.parent / 'containers'), '--runroot', '/run/e610-coverage-20261101',
                   'run', '--rm', '--network', 'none', '--security-opt', 'label=disable',
                   '-v', f'{out}/payload:/package:ro', '-v', f'{root}:/fixture:ro',
                   '-v', f'{ROOT}/coverage:/tests:ro']
        if item['os'] == 'rhel':
            userland = rhel_root(item, iso, kw)
            command += ['--rootfs', str(userland) + ':O', 'bash']
        else:
            command += ['--entrypoint', 'bash', 'localhost/e610-test-' + item['os'] + '-' + item['version']]
        command += ['/tests/test-install.sh', item['kernel']]
        with (out / 'installer-test.log').open('w') as log:
            result = sp.run(command, stdout=log, stderr=sp.STDOUT)
        if result.returncode:
            print((out / 'installer-test.log').read_text()[-5000:], flush=True)
            result.check_returncode()
        assert f'E610_INSTALLER_TEST_PASS kernel={item["kernel"]}' in (out / 'installer-test.log').read_text()
        item['installer_validation'] = 'passed'
        item['test_user_space'] = 'original RHEL DVD' if item['os'] == 'rhel' else item['os'] + ':' + item['version']
        (out / 'target.json').write_text(json.dumps(item, indent=2) + '\n')
        (out / 'import-complete.json').write_text(json.dumps({'id': item['id'], 'complete': True}) + '\n')
        print('E610_IMPORTED_INSTALLER_PASS', item['id'], flush=True)


if __name__ == '__main__':
    main()
