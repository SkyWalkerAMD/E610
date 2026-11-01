#!/bin/bash
# Run inside a disposable, network-disabled container with the actual ISO
# mounted read-only at /media and the exact original kernel at /fixture.
set -Eeuo pipefail
export LC_ALL=C
kver=${1:?kernel}
expected=${2:?expected module sha or native}
kind=${3:?baseline, external, imported or native}
. /etc/os-release
if command -v gcc || command -v make; then exit 1; fi
mkdir -p /lib/modules /boot /run/lock /var/lock
cp -a /fixture/lib/modules/"$kver" /lib/modules/
rm -rf -- /lib/modules/"$kver"/updates/e610
depmod -a "$kver"
if [[ $ID == ubuntu || $ID == debian ]]; then
    image=/boot/initrd.img-$kver
    cp /fixture/boot/config-"$kver" /boot/
    mkinitramfs -o "$image" "$kver"
else
    image=/boot/initramfs-$kver.img
    dracut --force --no-hostonly --kver "$kver" "$image"
fi
original=$(sha256sum "$image" | awk '{print $1}')
cd /media
sha256sum --status -c SHA256SUMS
run=/media/E610-MultiOS-6.4.5-r3.run
cache=/opt/e610-offline/multios-6.4.5-r3
bash "$run" --list
test ! -e "$cache"
cp "$run" /tmp/corrupt.run
printf corrupt >> /tmp/corrupt.run
if bash /tmp/corrupt.run --kernel "$kver" --check; then exit 1; fi
test ! -e "$cache"
if bash /media/install.sh --kernel 0.0.0-unsupported; then exit 1; fi
cp /etc/os-release /tmp/os-release.original
printf 'ID=e610-unsupported-test\nVERSION_ID=1\n' > /etc/os-release
if bash /media/install.sh --kernel "$kver" --check; then exit 1; fi
cp /tmp/os-release.original /etc/os-release
mkdir /tmp/extracted
tar -xzf /release/E610-MultiOS-6.4.5-r3.tar.gz -C /tmp/extracted
bash /tmp/extracted/E610-MultiOS-6.4.5-r3/install.sh --kernel "$kver" --check
bash /media/install.sh --kernel "$kver" --check
test "$(sha256sum "$image" | awk '{print $1}')" = "$original"
if [[ $expected == native ]]; then
    bash /media/install.sh --kernel "$kver" | tee /tmp/native.log
    grep -q "E610_NATIVE_SUPPORT kernel=$kver" /tmp/native.log
    test "$(sha256sum "$image" | awk '{print $1}')" = "$original"
    echo "E610_MEDIA_TEST_PASS kernel=$kver native"
    exit 0
fi
state=/var/lib/e610-ixgbe/coverage-$ID-$kver
saved_backup=
if [[ $kind == baseline ]]; then
    case "$ID:$kver" in
        ubuntu:5.15.0-78-generic) state=/var/lib/e610-ixgbe/ubuntu22-$kver ;;
        ubuntu:6.8.0-31-generic) state=/var/lib/e610-ixgbe/ubuntu24-$kver ;;
        centos:3.10.*) state=/var/lib/e610-ixgbe/$kver ;;
        *) state=/var/lib/e610-ixgbe/expanded-$ID-$kver ;;
    esac
    bash "$cache/baseline/install.sh" --kernel "$kver"
    saved_backup=$(readlink -f "$state/latest")
fi
bash /media/install.sh --kernel "$kver"
dest=$(modinfo -k "$kver" -n ixgbe)
test "$(sha256sum "$dest" | awk '{print $1}')" = "$expected"
backup=$(readlink -f "$state/latest")
[[ -z $saved_backup ]] || test "$backup" = "$saved_backup"
installed=$(sha256sum "$image" | awk '{print $1}')
bash "$run" --kernel "$kver"
test "$(readlink -f "$state/latest")" = "$backup"
test "$(sha256sum "$image" | awk '{print $1}')" = "$installed"
cp "$cache/install.sh" /tmp/good-dispatch
printf corrupt >> "$cache/install.sh"
if bash "$run" --kernel "$kver" --check; then exit 1; fi
cp /tmp/good-dispatch "$cache/install.sh"
bash "$cache/install.sh" --kernel "$kver" --rollback
test "$(sha256sum "$image" | awk '{print $1}')" = "$original"
test -z "$(find /opt/e610-offline -maxdepth 1 -name '.stage.*' -print)"
echo "E610_MEDIA_TEST_PASS kernel=$kver $kind"
