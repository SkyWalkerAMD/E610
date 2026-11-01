#!/usr/bin/env python3
"""Mount the exact r4 ISO and test new targets plus real r3 upgrade state."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess as sp

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
for name in ('work', 'release', 'previous_work'):
    p.add_argument('--' + name.replace('_', '-'), type=Path, required=True)
a = p.parse_args()
work, release, previous = a.work.resolve(), a.release.resolve(), a.previous_work.resolve()
sp.run(['sha256sum', '--status', '-c', 'SHA256SUMS'], cwd=release, check=True)
manifest = json.loads((release / 'manifest.json').read_text())
new = json.loads((ROOT / 'mirror/inventory.json').read_text())
tests = []
for t in new:
    tests.append(dict(t, kind='native' if t['native'] else 'imported',
        fixture=str(work / 'fixtures' / t['id'] / 'root'), image=f'localhost/e610-test-{t["os"]}-{t["version"]}'))
    if t.get('additional_media'):
        tests.append(dict(tests[-1], id=t['id'] + '-desktop', additional_iso=t['additional_media'][0]['iso']))
for system, version, kernel in [('debian', '11', '5.10.0-16-amd64'), ('rhel', '8', '4.18.0-553.el8_10.x86_64')]:
    t = next(t for t in manifest['targets'] if t['os'] == system and t['version'] == version and t['kernel'] == kernel)
    folder = previous / 'import-tests' / t['id']
    test = dict(t, id='r3-upgrade-' + system + '-' + kernel, kind='inherited', fixture=str(folder / 'root'),
                state='/var/lib/e610-ixgbe/coverage-' + system + '-' + kernel)
    if system == 'rhel':
        test['rootfs'] = str(folder / 'rootfs')
    else:
        test['image'] = 'localhost/e610-test-debian-11'
    tests.append(test)
media = work / 'final-media'
media.mkdir(exist_ok=True)
logs = work / 'final-media-logs'
logs.mkdir(exist_ok=False)
iso = release / 'E610-MultiOS-6.4.5-r4.iso'
iso_sha = hashlib.sha256(iso.read_bytes()).hexdigest()
sp.run(['mount', '-o', 'loop,ro,nosuid,nodev', str(iso), str(media)], check=True)
results = []
try:
    for t in tests:
        command = ['podman', '--root', str(work / 'containers'), '--runroot', str(work / 'runroot'),
                   'run', '--rm', '--network', 'none', '--security-opt', 'label=disable',
                   '-e', 'E610_TEST_RELEASE=6.4.5-r4', '-e', 'E610_TEST_STATE=' + t.get('state', ''),
                   '-v', f'{media}:/media:ro', '-v', f'{release}:/release:ro',
                   '-v', f'{previous}/candidate-r3:/prior-release:ro',
                   '-v', t['fixture'] + ':/fixture:ro', '-v', f'{ROOT}/coverage:/tests:ro']
        if 'rootfs' in t:
            command += ['--rootfs', t['rootfs'] + ':O', 'bash']
        else:
            command += ['--entrypoint', 'bash', t['image']]
        command += ['/tests/test-media.sh', t['kernel'], 'native' if t.get('native') else t['module_sha256'], t['kind']]
        logfile = logs / (t['id'] + '.log')
        with logfile.open('w') as log:
            result = sp.run(command, stdout=log, stderr=sp.STDOUT)
        passed = result.returncode == 0 and f'E610_MEDIA_TEST_PASS kernel={t["kernel"]}' in logfile.read_text()
        results.append({'id': t['id'], 'kernel': t['kernel'], 'kind': t['kind'], 'passed': passed,
            'iso_sha256': iso_sha, 'log_sha256': hashlib.sha256(logfile.read_bytes()).hexdigest()})
        print('E610_R4_MEDIA_CASE', t['id'], 'PASS' if passed else 'FAIL', flush=True)
finally:
    sp.run(['umount', str(media)], check=True)
(logs / 'media-validation.json').write_text(json.dumps(results, indent=2) + '\n')
assert len(results) == 6 and all(t['passed'] for t in results)
print('E610_R4_MEDIA_ALL_PASS', len(results), iso_sha)
