#!/usr/bin/env python3
"""Stage one exact OS/kernel installer with its original signing certificate."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from expanded.stage import checksums


def stage(module_dir, target, destination):
    destination.mkdir(parents=True, exist_ok=False)
    module = module_dir / 'ixgbe.ko'
    module_sha = hashlib.sha256(module.read_bytes()).hexdigest()
    if module_sha != target['module_sha256']:
        raise ValueError('Module does not match verified target')
    shutil.copyfile(module, destination / module.name)
    cert_sha = target.get('certificate_sha256', 'unsigned')
    if cert_sha != 'unsigned':
        cert = module_dir / 'E610-MOK.der'
        if hashlib.sha256(cert.read_bytes()).hexdigest() != cert_sha:
            raise ValueError('Certificate does not match verified target')
        shutil.copyfile(cert, destination / cert.name)
    shutil.copyfile(HERE.parent / 'expanded/mok-status.sh', destination / 'mok-status.sh')
    replacements = {'KERNEL': target['kernel'], 'OS': target['os'], 'VERSION': target['version'],
                    'LABEL': f"{target['os']} {target['release']}",
                    'MODULE_SHA256': module_sha, 'CERT_SHA256': cert_sha,
                    'SB_VALIDATED': target.get('secure_boot_validation', 'passed')}
    script = (HERE / 'install.sh.in').read_text()
    for key, value in replacements.items():
        script = script.replace('@' + key + '@', value)
    (destination / 'install.sh').write_text(script)
    if target['os'] in ('ubuntu', 'debian'):
        hook = (HERE.parent / 'ubuntu22-offline/initramfs-hook').read_text().replace('5.15.0-78-generic', target['kernel'])
    else:
        hook = '# E610 exact-kernel offline driver\nadd_drivers+=" ixgbe "\n'
    (destination / 'initramfs-hook').write_text(hook)
    (destination / 'target.json').write_text(json.dumps(target, indent=2) + '\n')
    checksums(destination)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--module-dir', type=Path, required=True)
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    stage(args.module_dir, json.loads(args.target.read_text()), args.output)
