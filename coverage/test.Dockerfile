ARG IMAGE=ubuntu:20.04
FROM ${IMAGE}
ENV DEBIAN_FRONTEND=noninteractive
RUN if command -v apt-get; then \
      . /etc/os-release; \
      if [ "$ID:$VERSION_ID" = debian:10 ] || [ "$ID:$VERSION_ID" = debian:11 ]; then \
        codename=bullseye; security=bullseye-security; \
        if [ "$VERSION_ID" = 10 ]; then codename=buster; security=buster/updates; fi; \
        rm -f /etc/apt/sources.list.d/*.sources /etc/apt/sources.list.d/*.list; \
        printf 'deb http://archive.debian.org/debian %s main\ndeb http://archive.debian.org/debian-security %s main\n' "$codename" "$security" > /etc/apt/sources.list; \
        printf 'Acquire::Check-Valid-Until "false";\n' > /etc/apt/apt.conf.d/99-e610-archive; \
      fi; \
      if [ "$ID:$VERSION_ID" = ubuntu:24.10 ] || [ "$ID:$VERSION_ID" = ubuntu:25.04 ]; then \
        sed -i -E 's@https?://([a-z.]*archive.ubuntu.com|security.ubuntu.com)/ubuntu/?@http://old-releases.ubuntu.com/ubuntu/@g' /etc/apt/sources.list.d/*.sources; \
      fi; \
      apt-get update && apt-get install -y --no-install-recommends initramfs-tools kmod zstd xz-utils mokutil util-linux ca-certificates && rm -rf /var/lib/apt/lists/*; \
    else \
      . /etc/os-release; \
      if [ "$ID:$VERSION_ID" = centos:7 ] || [ "$ID:$VERSION_ID" = centos:8 ]; then \
        rm -f /etc/yum.repos.d/*.repo; \
        if [ "$VERSION_ID" = 7 ]; then \
          printf '[base]\nname=CentOS vault\nbaseurl=https://vault.centos.org/7.9.2009/os/x86_64/\ngpgcheck=1\ngpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7\n' > /etc/yum.repos.d/vault.repo; \
        else \
          printf '[base]\nname=CentOS vault\nbaseurl=https://vault.centos.org/8.5.2111/BaseOS/x86_64/os/\ngpgcheck=1\ngpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial\n[appstream]\nname=CentOS vault AppStream\nbaseurl=https://vault.centos.org/8.5.2111/AppStream/x86_64/os/\ngpgcheck=1\ngpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial\n' > /etc/yum.repos.d/vault.repo; \
        fi; \
      fi; \
      yum install -y dracut kmod mokutil util-linux tar gzip xz cpio findutils diffutils && yum clean all; \
    fi
ENTRYPOINT ["bash"]
