#!/usr/bin/env python3
"""Release gate: require every candidate-media check before final checksums."""
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
for name in ('release', 'local_tests', 'cloud_tests'):
    p.add_argument('--' + name.replace('_', '-'), type=Path, required=True)
p.add_argument('--cloud-run', required=True)
args = p.parse_args()
release = args.release.resolve()
sp.run(['sha256sum', '--status', '-c', 'SHA256SUMS'], cwd=release, check=True)
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
iso_sha = sha(release / 'E610-MultiOS-6.4.5-r3.iso')
manifest = json.loads((release / 'manifest.json').read_text())
imports = json.loads((args.local_tests / 'imported-media-validation.json').read_text())
expected_imports = {t['id'] for t in manifest['targets'] if t['kind'] == 'imported'}
assert {t['id'] for t in imports} == expected_imports
assert len(imports) == len(expected_imports)
for t in imports:
    assert t['passed'] and t['iso_sha256'] == iso_sha
    assert sha(args.local_tests / (t['id'] + '.log')) == t['log_sha256']
expected_cloud = {
    ('ubuntu', '5.4.0-144-generic'), ('ubuntu', '5.15.0-67-generic'),
    ('debian', '5.10.0-32-amd64'), ('almalinux', '4.18.0-553.el8_10.x86_64'),
    ('almalinux', '5.14.0-70.13.1.el9_0.x86_64'), ('almalinux', '5.14.0-687.5.3.el9_8.x86_64'),
    ('almalinux', '6.12.0-55.9.1.el10_0.x86_64'), ('rocky', '6.12.0-55.12.1.el10_0.x86_64'),
    ('rocky', '6.12.0-211.16.1.el10_2.0.1.x86_64'), ('ubuntu', '5.15.0-78-generic'),
    ('ubuntu', '6.2.0-26-generic'), ('ubuntu', '6.8.0-31-generic'),
    ('rocky', '4.18.0-553.el8_10.x86_64'), ('centos', '3.10.0-1160.el7.x86_64'),
    ('centos', '3.10.0-1160.119.1.el7.x86_64'),
}
cloud = []
for system, kernel in sorted(expected_cloud):
    files = list(args.cloud_tests.glob(f'**/media-{system}-{kernel}.log'))
    assert len(files) == 1, (system, kernel, files)
    log = files[0]
    assert f'E610_MEDIA_TEST_PASS kernel={kernel}' in log.read_text()
    cloud.append({'os': system, 'kernel': kernel, 'passed': True, 'log_sha256': sha(log)})
evidence = release.parent / 'final-media-evidence'
evidence.mkdir(exist_ok=False)
shutil.copytree(args.local_tests, evidence / 'original-media-tests')
shutil.copytree(args.cloud_tests, evidence / 'cloud-tests')
sp.run(['tar', '-czf', str(release / 'MEDIA-TEST-LOGS.tar.gz'), '-C', str(evidence), '.'], check=True)
report = {'package': manifest['package'], 'candidate_iso_sha256': iso_sha,
          'cloud_run': 'https://github.com/SkyWalkerAMD/E610/actions/runs/' + args.cloud_run,
          'cloud_media_cases': cloud, 'original_media_cases': imports,
          'all_passed': True, 'network_during_installation': False, 'compiler_on_target': False,
          'physical_e610': 'not_tested'}
(release / 'MEDIA-VALIDATION.json').write_text(json.dumps(report, indent=2) + '\n')
checksums(release)
print(f'E610_RELEASE_GATE_PASS targets={len(manifest["targets"])} media_cases={len(cloud) + len(imports)} iso_sha256={iso_sha}')
