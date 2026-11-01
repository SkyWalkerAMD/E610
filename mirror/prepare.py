#!/usr/bin/env python3
"""Validate mirror-only additions in private containers and diskless VMs."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess as sp
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from coverage.stage import stage
spec = importlib.util.spec_from_file_location('imports', ROOT / 'coverage/import-existing.py')
imports = importlib.util.module_from_spec(spec)
spec.loader.exec_module(imports)
digest, run = imports.digest, imports.run
IDS = ('57AE', '57AF', '57B0', '57B1', '57B2')


def modinfo(path):
    text = sp.check_output(['modinfo', str(path)], text=True)
    return text, [i for i in IDS if 'v00008086d0000' + i in text]


def main():
    p = argparse.ArgumentParser()
    for name in ('work', 'originals', 'live', 'kit', 'busybox', 'audit'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--only')
    a = p.parse_args()
    work = a.work.resolve()
    assert not work.is_relative_to(a.live.resolve())
    assert not work.is_relative_to(a.originals.resolve())
    work.mkdir(parents=True, exist_ok=True)
    records = json.loads((ROOT / 'mirror/inventory.json').read_text())
    audited = {r['iso']: r for r in json.loads(a.audit.read_text())}
    kit_modules = {r['kernel']: r for r in json.loads((a.kit / 'release-manifest.json').read_text())['modules']}
    for record in records:
        if a.only and record['id'] != a.only:
            continue
        t = dict(record)
        k = t['kernel']
        kw = work / 'fixtures' / t['id']
        out = work / 'validated' / t['id']
        out.mkdir(parents=True, exist_ok=True)
        source_root = a.live if t['native'] else a.originals
        iso = (source_root / t['source_iso']).resolve()
        assert iso.is_relative_to(source_root.resolve())
        assert digest(iso) == t['source_sha256'], t['source_iso']
        root = imports.fixture(t, iso, kw)
        stock = list((root / 'lib/modules' / k).glob('kernel/drivers/net/ethernet/intel/ixgbe/ixgbe.ko*'))
        assert len(stock) == 1, stock
        info, ids = modinfo(stock[0])
        (out / 'stock-modinfo.txt').write_text(info)
        t.update(native_pci_ids=ids, stock_module_sha256=digest(stock[0]), physical_e610='not_tested')
        assert (len(ids) == 5) == t['native'], (k, ids)
        for other in t.get('additional_media', []):
            image = a.live / other['iso']
            assert digest(image) == other['sha256']
            audit = audited[other['iso']]
            assert audit['boots']
            for boot in audit['boots']:
                assert boot['modules']
                for module in boot['modules']:
                    assert module['kernel'] == k and module['all_e610_ids']
                    assert module['sha256'] == t['stock_module_sha256'], 'Desktop/server stock module mismatch'
            (out / 'additional-media.json').write_text(json.dumps(t['additional_media'], indent=2) + '\n')
        if not t['native']:
            module = a.kit / 'work/drivers' / k
            assert digest(module / 'ixgbe.ko') == kit_modules[k]['files']['ixgbe.ko'] == t['module_sha256']
            assert digest(module / 'E610-MOK.der') == t['certificate_sha256']
            stage(module, t, out / 'payload')
            target = root / 'lib/modules' / k / 'updates/e610/ixgbe.ko'
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(module / 'ixgbe.ko', target)
        run('depmod', '-b', root, '-a', k)
        order = sp.check_output(['modprobe', '-d', str(root), '-S', k, '--show-depends', 'ixgbe'], text=True)
        (out / 'load-order.txt').write_text(order)
        # Use the checked-in smoke test, adapting only tool locations and the
        # machine accelerator for this host. No disks or network devices exist.
        smoke = (ROOT / 'expanded/smoke.sh').read_text()
        smoke = smoke.replace('/usr/bin/busybox', str(a.busybox.resolve()))
        smoke = smoke.replace('qemu-system-x86_64 -machine pc,accel=tcg -cpu max',
                              '/usr/libexec/qemu-kvm -machine q35,accel=kvm -cpu host')
        smoke = smoke.replace('"$(dirname "$0")/smoke-init.sh"', '"' + str(ROOT / 'expanded/smoke-init.sh') + '"')
        launcher = kw / 'smoke-host.sh'
        launcher.write_text(smoke)
        run('bash', launcher, kw, out, k, 'native' if t['native'] else 'external')
        if not t['native']:
            command = ['podman', '--root', str(work / 'containers'), '--runroot', str(work / 'runroot'),
                       'run', '--rm', '--network', 'none', '--security-opt', 'label=disable',
                       '-v', f'{out}/payload:/package:ro', '-v', f'{root}:/fixture:ro',
                       '-v', f'{ROOT}/coverage:/tests:ro', '--entrypoint', 'bash',
                       'localhost/e610-test-debian-10', '/tests/test-install.sh', k]
            with (out / 'installer-test.log').open('w') as log:
                run(*command, stdout=log, stderr=sp.STDOUT)
            assert f'E610_INSTALLER_TEST_PASS kernel={k}' in (out / 'installer-test.log').read_text()
            t['installer_validation'] = 'passed'
        shutil.copyfile(kw / 'fixture-complete.json', out / 'fixture-source.json')
        (out / 'target.json').write_text(json.dumps(t, indent=2) + '\n')
        (out / 'complete.json').write_text(json.dumps({'complete': True, 'id': t['id'],
            'installer_template_sha256': digest(ROOT / 'coverage/install.sh.in')}) + '\n')
        print('E610_MIRROR_TARGET_PASS', t['id'], k, flush=True)


if __name__ == '__main__':
    main()
