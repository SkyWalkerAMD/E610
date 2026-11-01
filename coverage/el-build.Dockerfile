ARG IMAGE=almalinux:9
FROM ${IMAGE}
RUN dnf install -y gcc make elfutils-libelf-devel openssl-devel openssl kmod cpio rpm-build diffutils findutils which patch \
    && dnf clean all
