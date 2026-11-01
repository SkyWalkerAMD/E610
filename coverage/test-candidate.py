#!/usr/bin/env python3
"""Validate the candidate media inside offline disposable userspaces."""
import json
import os
from pathlib import Path
import subprocess as sp

root = Path.cwd()
temp = Path(os.environ['RUNNER_TEMP'])
series, media_id = os.environ['SERIES'], os.environ['MEDIA_ID']
records = json.loads((root / 'candidate/manifest.json').read_text())['targets']
if series == 'centos':
    system, version = 'centos', '7'
    kernels = ['3.10.0-1160.el7.x86_64', '3.10.0-1160.119.1.el7.x86_64']
else:
    item = next(t for t in json.loads((root / series / 'inventory.json').read_text()) if t['id'] == media_id)
    system, version = item['os'], item['version']
    kernels = sorted(p.name for p in (temp / 'fixtures').iterdir() if (p / 'root/lib/modules' / p.name).is_dir())
assert kernels
for kernel in kernels:
    matches = [t for t in records if (t['os'], t['version'], t['kernel']) == (system, version, kernel)]
    assert len(matches) == 1, (system, version, kernel)
    item = matches[0]
    native = item['kind'] == 'native' or item.get('baseline_kind') == 'native'
    expected = 'native' if native else item.get('module_sha256')
    if expected is None:
        expected = {
            '3.10.0-1160.el7.x86_64': '4139a6de9813f4b686e980165e4dfb108f36df015dbe855fbaa014a750aaa341',
            '3.10.0-1160.119.1.el7.x86_64': 'db2df6bce892243e338dfa870dfc5119808a97d4cce5ea7f964828847a1e6a3f',
            '5.15.0-78-generic': '43afae311f0a21975f327e809c6136deb56eda51d73ca972c0f4d88a292ab78f',
            '6.8.0-31-generic': '846e8c45328507d3474019611e5ce4f1c40a7f20875b2b05c4645a15358ca9e1',
        }[kernel]
    command = ['docker', 'run', '--rm', '--network', 'none', '--entrypoint', 'bash',
               '-v', f'{temp}/media:/media:ro', '-v', f'{root}/candidate:/release:ro',
               '-v', f'{root}/coverage:/tests:ro']
    if series == 'centos':
        sp.run(['docker', 'build', '--build-arg', 'KVER=' + kernel, '-f', 'centos7-media/Dockerfile', '-t', 'e610-c7-media', '.'], check=True)
        command += ['e610-c7-media', '-c', 'mkdir -p /fixture/lib; cp -a /lib/modules /fixture/lib/; exec bash /tests/test-media.sh "$@"',
                    'bash', kernel, expected, item['kind']]
    else:
        command += ['-v', f'{temp}/fixtures/{kernel}/root:/fixture:ro', 'e610-offline-test',
                    '/tests/test-media.sh', kernel, expected, item['kind']]
    logfile = root / 'output' / f'media-{system}-{kernel}.log'
    with logfile.open('w') as log:
        result = sp.run(command, stdout=log, stderr=sp.STDOUT)
    print(logfile.read_text()[-5000:], flush=True)
    result.check_returncode()
    assert f'E610_MEDIA_TEST_PASS kernel={kernel}' in logfile.read_text()
print('E610_CANDIDATE_MEDIA_PASS', media_id)
