#!/usr/bin/env python3
"""Exercise the actual read-only release ISO for all imported OS/kernel pairs."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess as sp

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--work', type=Path, required=True)
p.add_argument('--release', type=Path, required=True)
p.add_argument('--jobs', type=int, default=3)
args = p.parse_args()
work, release = args.work.resolve(), args.release.resolve()
sp.run(['sha256sum', '--status', '-c', 'SHA256SUMS'], cwd=release, check=True)
records = [t for t in json.loads((release / 'manifest.json').read_text())['targets'] if t['kind'] == 'imported']
expected = json.loads((ROOT / 'coverage/imported-inventory.json').read_text())
assert {t['id'] for t in records} == {t['id'] for t in expected}
media = work / 'release-media'
media.mkdir(exist_ok=True)
logs = work / 'media-results'
logs.mkdir(exist_ok=True)
iso = release / 'E610-MultiOS-6.4.5-r3.iso'
iso_sha = hashlib.sha256(iso.read_bytes()).hexdigest()
sp.run(['mount', '-o', 'loop,ro,nosuid,nodev', str(iso), str(media)], check=True)


def test(item):
    testroot = work / 'import-tests' / item['id']
    command = ['podman', '--root', str(work / 'containers'), '--runroot', '/run/e610-coverage-20261101',
               'run', '--rm', '--network', 'none', '--security-opt', 'label=disable',
               '-v', f'{media}:/media:ro', '-v', f'{release}:/release:ro',
               '-v', f'{testroot}/root:/fixture:ro', '-v', f'{ROOT}/coverage:/tests:ro']
    if item['os'] == 'rhel':
        command += ['--rootfs', str(testroot / 'rootfs') + ':O', 'bash']
    else:
        command += ['--entrypoint', 'bash', f'localhost/e610-test-{item["os"]}-{item["version"]}']
    command += ['/tests/test-media.sh', item['kernel'], item['module_sha256'], 'imported']
    logfile = logs / (item['id'] + '.log')
    with logfile.open('w') as log:
        result = sp.run(command, stdout=log, stderr=sp.STDOUT)
    passed = result.returncode == 0 and f'E610_MEDIA_TEST_PASS kernel={item["kernel"]} imported' in logfile.read_text()
    record = {'id': item['id'], 'kernel': item['kernel'], 'passed': passed,
              'iso_sha256': iso_sha, 'log_sha256': hashlib.sha256(logfile.read_bytes()).hexdigest()}
    print('IMPORTED_MEDIA', item['id'], 'PASS' if passed else 'FAIL', flush=True)
    return record


try:
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(test, records))
finally:
    sp.run(['umount', str(media)], check=True)
(logs / 'imported-media-validation.json').write_text(json.dumps(results, indent=2) + '\n')
assert all(r['passed'] for r in results), 'One or more imported media tests failed; see logs'
print(f'E610_IMPORTED_MEDIA_ALL_PASS count={len(results)} iso_sha256={iso_sha}')
