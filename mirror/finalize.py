#!/usr/bin/env python3
"""Publish checksums only after the exact final r4 media passes every case."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess as sp
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from expanded.stage import checksums

p = argparse.ArgumentParser()
for name in ('work', 'release'):
    p.add_argument('--' + name, type=Path, required=True)
a = p.parse_args()
work, release = a.work.resolve(), a.release.resolve()
sp.run(['sha256sum', '--status', '-c', 'SHA256SUMS'], cwd=release, check=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = json.loads((release / 'manifest.json').read_text())
iso_sha = sha(release / 'E610-MultiOS-6.4.5-r4.iso')
cases = json.loads((work / 'final-media-logs/media-validation.json').read_text())
expected = {'mirror-debian-10.11.0', 'mirror-ubuntu-25.04', 'mirror-ubuntu-26.04',
            'mirror-ubuntu-26.04-desktop', 'r3-upgrade-debian-5.10.0-16-amd64',
            'r3-upgrade-rhel-4.18.0-553.el8_10.x86_64'}
assert len(cases) == len(expected) and {t['id'] for t in cases} == expected
for case in cases:
    logfile = work / 'final-media-logs' / (case['id'] + '.log')
    assert case['passed'] and case['iso_sha256'] == iso_sha and sha(logfile) == case['log_sha256']
    assert f'E610_MEDIA_TEST_PASS kernel={case["kernel"]}' in logfile.read_text()
catalog = json.loads((release / 'MIRROR-COVERAGE.json').read_text())
assert catalog['all_kernel_entries_covered'] and catalog['linux_iso_count'] == 52
assert len(manifest['targets']) == 93
evidence = work / 'final-evidence'
evidence.mkdir(exist_ok=False)
shutil.copytree(work / 'final-media-logs', evidence / 'final-media')
for target in json.loads((ROOT / 'mirror/inventory.json').read_text()):
    source = work / 'validated' / target['id']
    output = evidence / 'kernels' / target['id']
    output.mkdir(parents=True)
    for item in source.iterdir():
        if item.is_file() and item.suffix in ('.log', '.json', '.txt'):
            shutil.copyfile(item, output / item.name)
sp.run(['tar', '-czf', str(release / 'MEDIA-TEST-LOGS.tar.gz'), '-C', str(evidence), '.'], check=True)
report = {'package': manifest['package'], 'candidate_iso_sha256': iso_sha,
          'kernel_target_count': 93, 'mirror_linux_iso_count': 52, 'media_cases': cases,
          'all_passed': True, 'network_during_installation': False, 'compiler_on_target': False,
          'physical_e610': 'not_tested', 'rhel10_or_oracle_media_present': False,
          'previous_release': 'https://github.com/SkyWalkerAMD/E610/releases/tag/v6.4.5-multios-r3'}
(release / 'MEDIA-VALIDATION.json').write_text(json.dumps(report, indent=2) + '\n')
checksums(release)
print('E610_R4_RELEASE_GATE_PASS targets=93 linux_isos=52 media_cases=6 iso_sha256=' + iso_sha)
