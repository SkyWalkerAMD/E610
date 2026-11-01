#!/usr/bin/env python3
"""Resolve official installation-media kernels; never substitute update kernels."""
import argparse
import concurrent.futures
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def get(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'E610-media-audit/1.0'})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def text(url):
    return get(url).decode()


def ubuntu(version):
    spec = importlib.util.spec_from_file_location('previous_inventory', ROOT / 'expanded/discover.py')
    previous = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(previous)
    return previous.ubuntu(version)


def debian(version):
    base = f'https://cdimage.debian.org/mirror/cdimage/archive/{version}/amd64/'
    name = f'debian-{version}-amd64-DVD-1'
    sums = text(base + 'iso-dvd/SHA256SUMS')
    digest = next(line.split()[0] for line in sums.splitlines()
                  if line.split()[-1].lstrip('*') == name + '.iso')
    list_url = base + 'list-dvd/' + name + '.list.gz'
    listing_bytes = get(list_url)
    listing = gzip.decompress(listing_bytes).decode().splitlines()
    paths = ['/' + s.strip().lstrip('./') for s in listing if s.strip().endswith('.deb')]
    kernels = []
    for path in paths:
        match = re.search(r'/linux-image-(\d[^_/]*-amd64)_[^/]+\.deb$', path)
        if not match:
            continue
        kernel = match[1]
        abi = kernel.removesuffix('-amd64')
        major_minor = '.'.join(kernel.split('.')[:2])
        packages = [p for p in paths if any(Path(p).name.startswith(prefix) for prefix in (
            'linux-image-' + kernel + '_', 'linux-headers-' + kernel + '_',
            'linux-headers-' + abi + '-common_', 'linux-kbuild-' + major_minor + '_',
            'linux-kbuild-' + abi + '_'))]
        kernels.append({'kernel': kernel, 'paths': sorted(set(packages))})
    if not kernels:
        raise ValueError('No signed Debian image packages found')
    return {'id': 'debian-' + version, 'os': 'debian', 'version': version.split('.')[0],
            'release': version, 'iso_url': base + 'iso-dvd/' + name + '.iso',
            'iso_sha256': digest, 'listing_url': list_url,
            'listing_sha256': hashlib.sha256(listing_bytes).hexdigest(), 'kernels': kernels}


def el(os_id, version):
    major = version.split('.')[0]
    if os_id == 'almalinux':
        bases = [f'https://repo.almalinux.org/almalinux/{version}/',
                 f'https://vault.almalinux.org/{version}/']
    else:
        bases = [f'https://dl.rockylinux.org/pub/rocky/{version}/',
                 f'https://dl.rockylinux.org/vault/rocky/{version}/']
    errors = []
    for base in bases:
        try:
            core = base + 'BaseOS/x86_64/kickstart/Packages/'
            try:
                listing = text(core + 'k/')
                core += 'k/'
            except Exception:
                listing = text(core)
            kernels = sorted(set(re.findall(r'href="kernel-core-([^"/]+\.x86_64)\.rpm"', listing)))
            if not kernels:
                raise ValueError('No original installation kernel in kickstart repository')
            devel, devlisting = core, listing
            if major != '8':
                devel = base + 'AppStream/x86_64/kickstart/Packages/'
                try:
                    devlisting = text(devel + 'k/')
                    devel += 'k/'
                except Exception:
                    devlisting = text(devel)
            entries = []
            for kernel in kernels:
                if f'kernel-devel-{kernel}.rpm' not in devlisting:
                    raise ValueError('No exact kernel-devel: ' + kernel)
                urls = [core + f'{package}-{kernel}.rpm' for package in
                        ('kernel-core', 'kernel-modules', 'kernel-modules-core')
                        if f'{package}-{kernel}.rpm' in listing]
                urls.append(devel + f'kernel-devel-{kernel}.rpm')
                entries.append({'kernel': kernel, 'urls': urls})
            return {'id': os_id + '-' + version, 'os': os_id, 'version': major,
                    'release': version, 'repository': base, 'kernels': entries}
        except Exception as exc:
            errors.append(str(exc))
    raise RuntimeError(f'{os_id} {version}: {errors}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    tasks = [(ubuntu, (f'20.04' + ('.' + str(n) if n else ''),)) for n in range(7)]
    tasks += [(debian, (version,)) for version in ('11.11.0',)]
    tasks += [(el, ('almalinux', version)) for version in
              ['8.10'] + [f'9.{n}' for n in range(9)] + [f'10.{n}' for n in range(3)]]
    tasks += [(el, ('rocky', f'10.{n}')) for n in range(3)]
    targets, failures = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(fn, *values): values for fn, values in tasks}
        for future in concurrent.futures.as_completed(futures):
            values = futures[future]
            try:
                item = future.result()
                targets.append(item)
                print(item['id'], ','.join(k['kernel'] for k in item['kernels']), flush=True)
            except Exception as exc:
                failures.append({'target': values, 'error': str(exc)})
                print('DISCOVERY_FAILED', values, str(exc), flush=True)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'inventory.json').write_text(json.dumps(sorted(targets, key=lambda x: x['id']), indent=2) + '\n')
    (args.output / 'discovery-errors.json').write_text(json.dumps(failures, indent=2) + '\n')
    print(f'DISCOVERY_COMPLETED media={len(targets)} errors={len(failures)}', flush=True)
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
