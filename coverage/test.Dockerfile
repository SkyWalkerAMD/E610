ARG IMAGE=ubuntu:20.04
FROM ${IMAGE}
ENV DEBIAN_FRONTEND=noninteractive
RUN if command -v apt-get; then \
      . /etc/os-release; \
      if [ "$ID:$VERSION_ID" = debian:11 ]; then \
        rm -f /etc/apt/sources.list.d/*.sources /etc/apt/sources.list.d/*.list; \
        printf 'deb http://archive.debian.org/debian bullseye main\ndeb http://archive.debian.org/debian-security bullseye-security main\n' > /etc/apt/sources.list; \
        printf 'Acquire::Check-Valid-Until "false";\n' > /etc/apt/apt.conf.d/99-e610-archive; \
      fi; \
      apt-get update && apt-get install -y --no-install-recommends initramfs-tools kmod zstd mokutil util-linux ca-certificates && rm -rf /var/lib/apt/lists/*; \
    else \
      dnf install -y dracut kmod mokutil util-linux tar gzip xz cpio findutils diffutils && dnf clean all; \
    fi
ENTRYPOINT ["bash"]
