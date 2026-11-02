# E610 网卡的 Linux 适配与验证

**[E610 ISO 镜像制作包 6.4.5 r1](https://github.com/SkyWalkerAMD/E610/releases/tag/v6.4.5-iso-kit-r1)**：普通手动安装和 PXE 自动安装共用直接内置驱动的 ISO，安装结束自动持久化驱动。包含 38 套精确 ABI 模块、源码和 43 个独立镜像的验证记录（86 项隔离安装与重启）。[制作与使用说明](pxe-media/RELEASE.zh-CN.md)。本轮无 E610 实卡，物理链路、收发及机器 Secure Boot 信任登记仍待验收。

**推荐：[多系统统一离线包 r4](https://github.com/SkyWalkerAMD/E610/releases/tag/v6.4.5-multios-r4)**。
共 93 个精确系统/内核组合，整合 Ubuntu 20/22/24/25/26、Debian 10–13、AlmaLinux 8–10、Rocky 8–10，以及已有 CentOS / RHEL 适配。已核对指定镜像库的 52 张 Linux ISO，补齐 Debian 10.11 和 Ubuntu 25.04 / 26.04 的统一入口。
自动匹配系统与精确内核，需要时安装预编译驱动，已经原生支持时提示无需安装，不升级目标内核。
提供 `tar.gz`、`.run` 和 KVM 驱动 ISO；[中文安装说明](mirror/INSTALL.zh-CN.md)、[验证范围](mirror/VALIDATION.zh-CN.md)。

```bash
sudo bash E610-MultiOS-6.4.5-r4.run
```

<!-- E610-R4-SUPPORT-MATRIX:BEGIN -->

## 完整系统与内核支持清单（r4）

**共 93 个精确系统/内核组合：77 个需要安装驱动，16 个原生支持。** 仅适用于 x86_64 / amd64；安装包不升级系统内核。

- **原生支持**：该精确内核的系统自带 ixgbe 已包含 E610 支持，无需安装本项目的额外驱动。
- **需要安装驱动**：使用本 Release 的离线安装包安装匹配的 ixgbe 6.4.5；目标系统无需联网或编译。
- **当前镜像库**：“是”表示已核对的 52 张 Linux 安装镜像中包含该内核；“额外覆盖”表示安装包也支持该组合，但当前镜像库没有对应镜像/内核。

### 当前镜像库覆盖情况

2026-11-02 复核的镜像库共 52 张 Linux ISO：43 张至少有一个内核需要安装驱动，另外 9 张的已核对内核全部原生支持。43 张需驱动镜像涉及 47 个“镜像 × 内核”选项，均已覆盖。下表按 ISO 计数；后面的完整清单按精确系统/内核组合计数，两者不同。

| 系统 | Linux ISO 数 | 至少一个内核需安装驱动 | 所有已核对内核原生支持 |
| --- | ---: | ---: | ---: |
| CentOS | 8 | 8 | 0 |
| RHEL | 8 | 8 | 0 |
| Rocky Linux | 14 | 10 | 4 |
| AlmaLinux | 2 | 2 | 0 |
| Debian | 7 | 7 | 0 |
| Ubuntu | 13 | 8 | 5 |
| **合计** | **52** | **43** | **9** |

**同一发行版可能因内核不同而得出不同结论。** 例如 Ubuntu Server 24.04.3 的 `6.8.0-71-generic` 需要安装驱动，而 `6.14.0-27-generic` 原生支持。请先用 `cat /etc/os-release` 和 `uname -rm` 核对系统及完整内核版本。

[清单数据：manifest.json](https://github.com/SkyWalkerAMD/E610/releases/download/v6.4.5-multios-r4/manifest.json) · [逐镜像核对记录：MIRROR-COVERAGE.json](https://github.com/SkyWalkerAMD/E610/releases/download/v6.4.5-multios-r4/MIRROR-COVERAGE.json)

### CentOS

9 个组合：9 个需要安装驱动，0 个原生支持。

| 系统 / 安装版本 | 精确内核 | E610 支持方式 | 当前镜像库 |
| --- | --- | --- | --- |
| CentOS 7.6 | `3.10.0-957.el7.x86_64` | 需要安装驱动 | 是 |
| CentOS 7.9 | `3.10.0-1160.119.1.el7.x86_64` | 需要安装驱动 | 额外覆盖 |
| CentOS 7.9 | `3.10.0-1160.el7.x86_64` | 需要安装驱动 | 是 |
| CentOS 8.0 | `4.18.0-80.el8.x86_64` | 需要安装驱动 | 是 |
| CentOS 8.4.2105 | `4.18.0-305.3.1.el8.x86_64` | 需要安装驱动 | 是 |
| CentOS 8.5.2111 | `4.18.0-348.el8.x86_64` | 需要安装驱动 | 是 |
| CentOS Stream 8 | `4.18.0-532.el8.x86_64` | 需要安装驱动 | 是 |
| CentOS Stream 9 | `5.14.0-383.el9.x86_64` | 需要安装驱动 | 是 |
| CentOS Stream 10 | `6.12.0-54.el10.x86_64` | 需要安装驱动 | 是 |

### RHEL

8 个组合：8 个需要安装驱动，0 个原生支持。

| 系统 / 安装版本 | 精确内核 | E610 支持方式 | 当前镜像库 |
| --- | --- | --- | --- |
| RHEL 7.6 | `3.10.0-957.el7.x86_64` | 需要安装驱动 | 是 |
| RHEL 7.9 | `3.10.0-1160.el7.x86_64` | 需要安装驱动 | 是 |
| RHEL 8.0 | `4.18.0-80.el8.x86_64` | 需要安装驱动 | 是 |
| RHEL 8.1 | `4.18.0-147.el8.x86_64` | 需要安装驱动 | 是 |
| RHEL 8.6 | `4.18.0-372.9.1.el8.x86_64` | 需要安装驱动 | 是 |
| RHEL 8.10 | `4.18.0-553.el8_10.x86_64` | 需要安装驱动 | 是 |
| RHEL 9.2 | `5.14.0-284.11.1.el9_2.x86_64` | 需要安装驱动 | 是 |
| RHEL 9.4 | `5.14.0-427.13.1.el9_4.x86_64` | 需要安装驱动 | 是 |

### Rocky Linux

20 个组合：15 个需要安装驱动，5 个原生支持。

| 系统 / 安装版本 | 精确内核 | E610 支持方式 | 当前镜像库 |
| --- | --- | --- | --- |
| Rocky Linux 8.4 | `4.18.0-305.3.1.el8_4.x86_64` | 需要安装驱动 | 额外覆盖 |
| Rocky Linux 8.5 | `4.18.0-348.el8.0.2.x86_64` | 需要安装驱动 | 额外覆盖 |
| Rocky Linux 8.6 | `4.18.0-372.9.1.el8.x86_64` | 需要安装驱动 | 是 |
| Rocky Linux 8.7 | `4.18.0-425.3.1.el8.x86_64` | 需要安装驱动 | 是 |
| Rocky Linux 8.8 | `4.18.0-477.10.1.el8_8.x86_64` | 需要安装驱动 | 额外覆盖 |
| Rocky Linux 8.9 | `4.18.0-513.5.1.el8_9.x86_64` | 需要安装驱动 | 是 |
| Rocky Linux 8.10 | `4.18.0-553.el8_10.x86_64` | 需要安装驱动 | 是 |
| Rocky Linux 9.0 | `5.14.0-70.13.1.el9_0.x86_64` | 需要安装驱动 | 额外覆盖 |
| Rocky Linux 9.1 | `5.14.0-162.6.1.el9_1.0.1.x86_64` | 需要安装驱动 | 额外覆盖 |
| Rocky Linux 9.1 | `5.14.0-162.6.1.el9_1.x86_64` | 需要安装驱动 | 是 |
| Rocky Linux 9.2 | `5.14.0-284.11.1.el9_2.x86_64` | 需要安装驱动 | 是 |
| Rocky Linux 9.3 | `5.14.0-362.8.1.el9_3.x86_64` | 需要安装驱动 | 是 |
| Rocky Linux 9.4 | `5.14.0-427.13.1.el9_4.x86_64` | 需要安装驱动 | 是 |
| Rocky Linux 9.5 | `5.14.0-503.14.1.el9_5.x86_64` | 需要安装驱动 | 是 |
| Rocky Linux 9.6 | `5.14.0-570.17.1.el9_6.x86_64` | 原生支持 | 是 |
| Rocky Linux 9.7 | `5.14.0-611.5.1.el9_7.x86_64` | 原生支持 | 是 |
| Rocky Linux 9.8 | `5.14.0-687.10.1.el9_8.0.1.x86_64` | 原生支持 | 是 |
| Rocky Linux 10.0 | `6.12.0-55.12.1.el10_0.x86_64` | 需要安装驱动 | 是 |
| Rocky Linux 10.1 | `6.12.0-124.8.1.el10_1.x86_64` | 原生支持 | 额外覆盖 |
| Rocky Linux 10.2 | `6.12.0-211.16.1.el10_2.0.1.x86_64` | 原生支持 | 是 |

### AlmaLinux

13 个组合：9 个需要安装驱动，4 个原生支持。

| 系统 / 安装版本 | 精确内核 | E610 支持方式 | 当前镜像库 |
| --- | --- | --- | --- |
| AlmaLinux 8.10 | `4.18.0-553.el8_10.x86_64` | 需要安装驱动 | 是 |
| AlmaLinux 9.0 | `5.14.0-70.13.1.el9_0.x86_64` | 需要安装驱动 | 额外覆盖 |
| AlmaLinux 9.1 | `5.14.0-162.6.1.el9_1.x86_64` | 需要安装驱动 | 额外覆盖 |
| AlmaLinux 9.2 | `5.14.0-284.11.1.el9_2.x86_64` | 需要安装驱动 | 额外覆盖 |
| AlmaLinux 9.3 | `5.14.0-362.8.1.el9_3.x86_64` | 需要安装驱动 | 额外覆盖 |
| AlmaLinux 9.4 | `5.14.0-427.13.1.el9_4.x86_64` | 需要安装驱动 | 额外覆盖 |
| AlmaLinux 9.5 | `5.14.0-503.11.1.el9_5.x86_64` | 需要安装驱动 | 是 |
| AlmaLinux 9.6 | `5.14.0-570.12.1.el9_6.x86_64` | 需要安装驱动 | 额外覆盖 |
| AlmaLinux 9.7 | `5.14.0-611.5.1.el9_7.x86_64` | 原生支持 | 额外覆盖 |
| AlmaLinux 9.8 | `5.14.0-687.5.3.el9_8.x86_64` | 原生支持 | 额外覆盖 |
| AlmaLinux 10.0 | `6.12.0-55.9.1.el10_0.x86_64` | 需要安装驱动 | 额外覆盖 |
| AlmaLinux 10.1 | `6.12.0-124.8.1.el10_1.x86_64` | 原生支持 | 额外覆盖 |
| AlmaLinux 10.2 | `6.12.0-211.7.3.el10_2.x86_64` | 原生支持 | 额外覆盖 |

### Debian

8 个组合：8 个需要安装驱动，0 个原生支持。

| 系统 / 安装版本 | 精确内核 | E610 支持方式 | 当前镜像库 |
| --- | --- | --- | --- |
| Debian 10.11.0 | `4.19.0-18-amd64` | 需要安装驱动 | 是 |
| Debian 11.4.0 | `5.10.0-16-amd64` | 需要安装驱动 | 是 |
| Debian 11.11.0 | `5.10.0-32-amd64` | 需要安装驱动 | 额外覆盖 |
| Debian 12.5.0 | `6.1.0-18-amd64` | 需要安装驱动 | 是 |
| Debian 12.8.0 | `6.1.0-27-amd64` | 需要安装驱动 | 是 |
| Debian 12.15.0 | `6.1.0-50-amd64` | 需要安装驱动 | 是 |
| Debian 13.0.0 | `6.12.38+deb13-amd64` | 需要安装驱动 | 是 |
| Debian 13.4.0 | `6.12.73+deb13-amd64` | 需要安装驱动 | 是 |

### Ubuntu

35 个组合：28 个需要安装驱动，7 个原生支持。

| 系统 / 安装版本 | 精确内核 | E610 支持方式 | 当前镜像库 |
| --- | --- | --- | --- |
| Ubuntu Server 20.04 | `5.4.0-26-generic` | 需要安装驱动 | 额外覆盖 |
| Ubuntu Server 20.04.1 | `5.4.0-42-generic` | 需要安装驱动 | 额外覆盖 |
| Ubuntu Server 20.04.2 | `5.4.0-65-generic` | 需要安装驱动 | 额外覆盖 |
| Ubuntu Server 20.04.2 | `5.8.0-41-generic` | 需要安装驱动 | 额外覆盖 |
| Ubuntu Server 20.04.3 | `5.4.0-81-generic` | 需要安装驱动 | 是 |
| Ubuntu Server 20.04.3 | `5.11.0-27-generic` | 需要安装驱动 | 是 |
| Ubuntu Server 20.04.4 | `5.4.0-100-generic` | 需要安装驱动 | 额外覆盖 |
| Ubuntu Server 20.04.4 | `5.13.0-30-generic` | 需要安装驱动 | 额外覆盖 |
| Ubuntu Server 20.04.5 | `5.4.0-125-generic` | 需要安装驱动 | 额外覆盖 |
| Ubuntu Server 20.04.5 | `5.15.0-46-generic` | 需要安装驱动 | 额外覆盖 |
| Ubuntu Server 20.04.6 | `5.4.0-144-generic` | 需要安装驱动 | 额外覆盖 |
| Ubuntu Server 20.04.6 | `5.15.0-67-generic` | 需要安装驱动 | 额外覆盖 |
| Ubuntu Server 22.04 | `5.15.0-25-generic` | 需要安装驱动 | 额外覆盖 |
| Ubuntu Server 22.04.1 | `5.15.0-43-generic` | 需要安装驱动 | 额外覆盖 |
| Ubuntu Server 22.04.2 | `5.15.0-60-generic` | 需要安装驱动 | 额外覆盖 |
| Ubuntu Server 22.04.2 | `5.19.0-32-generic` | 需要安装驱动 | 额外覆盖 |
| Ubuntu Server 22.04.3 | `5.15.0-78-generic` | 需要安装驱动 | 是 |
| Ubuntu Server 22.04.3 | `6.2.0-26-generic` | 需要安装驱动 | 是 |
| Ubuntu Server 22.04.4 | `5.15.0-94-generic` | 需要安装驱动 | 是 |
| Ubuntu Server / Desktop 22.04.4 | `6.5.0-18-generic` | 需要安装驱动 | 是 |
| Ubuntu Server 22.04.5 | `5.15.0-119-generic` | 需要安装驱动 | 是 |
| Ubuntu Server 22.04.5 | `6.8.0-40-generic` | 需要安装驱动 | 是 |
| Ubuntu Server 24.04 | `6.8.0-31-generic` | 需要安装驱动 | 是 |
| Ubuntu Server 24.04.1 | `6.8.0-41-generic` | 需要安装驱动 | 额外覆盖 |
| Ubuntu Server 24.04.2 | `6.8.0-53-generic` | 需要安装驱动 | 额外覆盖 |
| Ubuntu Server 24.04.2 | `6.11.0-17-generic` | 需要安装驱动 | 额外覆盖 |
| Ubuntu Server 24.04.3 | `6.8.0-71-generic` | 需要安装驱动 | 是 |
| Ubuntu Server 24.04.3 | `6.14.0-27-generic` | 原生支持 | 是 |
| Ubuntu Server 24.04.4 | `6.8.0-100-generic` | 原生支持 | 是 |
| Ubuntu Server 24.04.4 | `6.17.0-14-generic` | 原生支持 | 是 |
| Ubuntu Server 24.04.5 | `6.8.0-139-generic` | 原生支持 | 是 |
| Ubuntu Server 24.04.5 | `7.0.0-31-generic` | 原生支持 | 是 |
| Ubuntu Server 24.10 | `6.11.0-8-generic` | 需要安装驱动 | 是 |
| Ubuntu Server 25.04 | `6.14.0-15-generic` | 原生支持 | 是 |
| Ubuntu Server / Desktop 26.04 | `7.0.0-14-generic` | 原生支持 | 是 |

### 安装与验证范围

需要驱动的组合使用同一套 [.run](https://github.com/SkyWalkerAMD/E610/releases/download/v6.4.5-multios-r4/E610-MultiOS-6.4.5-r4.run)、[tar.gz](https://github.com/SkyWalkerAMD/E610/releases/download/v6.4.5-multios-r4/E610-MultiOS-6.4.5-r4.tar.gz) 或 [KVM 驱动数据 ISO](https://github.com/SkyWalkerAMD/E610/releases/download/v6.4.5-multios-r4/E610-MultiOS-6.4.5-r4.iso)。KVM ISO 用于已安装系统中的驱动安装，不是操作系统启动安装盘。

```bash
sudo bash E610-MultiOS-6.4.5-r4.run
```

从 ISO Kit 导入的历史模块（包括 Debian 10.11）要求关闭 Secure Boot；原 CentOS 7.9 模块未签名。其他签名模块按安装说明登记对应公钥。原有模块、证书及首次安装的回退备份继续沿用。

以上是精确内核适配与原生支持检查结果，不表示已对全部系统逐一完成 E610 实卡链路、吞吐、PTP、SR-IOV 或长期稳定性测试。镜像核对也不等于重新完成 52 次系统安装。

**未列出的更新内核、其他架构、RHEL 10、Oracle Linux / UEK 不在本版已验证范围内。** 不能仅凭发行版大版本或内核主版本判断支持情况。

[中文安装说明](https://github.com/SkyWalkerAMD/E610/releases/download/v6.4.5-multios-r4/INSTALL.zh-CN.md) · [SHA-256 校验值](https://github.com/SkyWalkerAMD/E610/releases/download/v6.4.5-multios-r4/SHA256SUMS) · [验证说明](https://github.com/SkyWalkerAMD/E610/releases/download/v6.4.5-multios-r4/VALIDATION.zh-CN.md) · [最终介质验证记录](https://github.com/SkyWalkerAMD/E610/releases/download/v6.4.5-multios-r4/MEDIA-VALIDATION.json)

<!-- E610-R4-SUPPORT-MATRIX:END -->

**[已适配系统、下载与验证汇总](SUPPORTED-SYSTEMS.zh-CN.md)**：包含精确内核清单、原生支持检测、
中文说明、SHA-256 校验和验证边界。系统大版本相同不代表后续全部安全更新内核均可混用。
原 r3 支持组合的安装器、证书和备份继续沿用。指定镜像库没有 RHEL 10 原版镜像；Oracle Linux / UEK、其他架构及任意更新内核不在已验证范围。

Ubuntu Server 22.04.3 GA 的构建、镜像适配和验证说明见 [ubuntu22-e610](ubuntu22-e610/README.zh-CN.md)。各系统的编译与实机结果分别记录，不能互相替代。

以下为已发布的 CentOS 7.9 适配。

**CentOS 推荐安装方式：**下载 [CentOS 7.9 Release](https://github.com/SkyWalkerAMD/E610/releases/tag/v6.4.5-centos7.9-r2)
中的 r2 完整包，解压后运行 `sudo bash install.sh`。安装器自动选模块、校验、备份并
更新 initramfs；回退使用 `sudo bash uninstall.sh`。具体步骤见
[简化安装说明](INSTALL.zh-CN.md)。下文保留源码构建和手动部署细节。

本项目使用 Intel 官方 ixgbe 6.4.5，目标架构为 x86_64。原始附件与
[Intel 官方发布包](https://github.com/intel/ethernet-linux-ixgbe/releases/tag/v6.4.5)
的 SHA-256 一致：

```text
8d23f2c329e0b93055236e67ffbf1de99d8dce32ccc75beb759774c7c24d7ed4
```

云端直接下载公开发布包，不上传本地附件。源码已经包含 E610 的 PCI ID：
`8086:57ae`、`8086:57af`、`8086:57b0`、`8086:57b1`、`8086:57b2`。

## 验证范围

目标内核为 `3.10.0-1160.el7.x86_64` 和
`3.10.0-1160.119.1.el7.x86_64`。使用 CentOS 7.9 用户空间、GCC 4.8.5
以及与目标内核完全匹配的 `kernel-devel` 构建。容器宿主机内核不作为目标内核。

编译后检查驱动版本、vermagic、E610 PCI 别名；随后在 QEMU 中启动对应的真实
CentOS 内核，以最小 BusyBox initramfs 加载依赖、加载 ixgbe，再卸载 ixgbe。
每个内核重复三次加载/卸载，并检查 XArray 兼容层的 slab 缓存已释放。
此项验证覆盖内核模块兼容性，不代表完整 CentOS 系统验收。

当前没有 E610 实卡，尚未验证 probe、链路、收发、吞吐、PTP、SR-IOV 或固件交互。
源码中存在这些功能不等于本次已验证这些功能。

## 在目标机器上使用

先检查：

```sh
uname -r
uname -m
lspci -nn | grep -i ethernet
```

仅使用与 `uname -r` 完全相同的构建产物。其他内核版本需要用其对应的
`kernel-devel` 重新编译，不应强制加载不匹配的模块。

云端测试完成后，将所需内核的构建目录复制到目标机器，在该目录检查：

```sh
test "$(uname -m)" = x86_64
test "$(modinfo -F vermagic ./ixgbe.ko | awk '{print $1}')" = "$(uname -r)"
modinfo ./ixgbe.ko
```

安装前备份现有 ixgbe 模块和 initramfs。首次切换驱动请使用本地或带外控制台，
因为 ixgbe 也管理同机上的其他 Intel 网口，卸载或重启可能中断 SSH。确认内核
版本匹配且有恢复途径后，手工安装：

```sh
KVER=$(uname -r)
sudo install -D -m 0644 ./ixgbe.ko "/lib/modules/$KVER/updates/drivers/net/ethernet/intel/ixgbe/ixgbe.ko"
sudo depmod -a "$KVER"
modinfo -n ixgbe
modinfo -F version ixgbe
sudo dracut -f --kver "$KVER"
```

确认 `modinfo -n ixgbe` 解析到新安装的文件，再安排维护窗口重启。以上命令不会
主动卸载正在使用的驱动。本项目生成的模块未签名；若目标机强制验证模块签名，
需按目标机已有的信任链完成签名后安装。

重启后检查网口（将 `IFACE` 替换为实际网口）：

```sh
ethtool -i IFACE
ethtool IFACE
ip -s link show dev IFACE
dmesg | grep -Ei 'ixgbe|firmware|unknown symbol|invalid module'
```

再进行同网段 ping、双向 iperf3、多队列、VLAN/MTU 和长时间收发测试。
PTP、SR-IOV 等功能如需使用，应逐项单独验收。

如需回退，应从带外控制台恢复备份的模块和 initramfs，重新生成对应内核的
depmod 索引，并在维护窗口重启。

## 重现云端测试

在 Linux Docker 主机执行：

```sh
mkdir -p output
docker build --build-arg KVER=3.10.0-1160.119.1.el7.x86_64 -f ci/Dockerfile -t e610-c7 .
docker run --rm -v "$PWD/output:/output" e610-c7
# 主机需有 qemu-system-x86、busybox-static 和 cpio：
bash ci/smoke.sh output
```

日志和模块保存在 `output/`。编译日志有 `E610_BUILD_PASS`、退出码为 0，
且启动日志有 `E610_CLOUD_MODULE_LOAD_PASS`，才算该内核的测试通过。

补丁存放于 `patches/`，按文件名顺序、以 `patch -p1` 应用于官方源码。
完整测试结果以实际云端任务和最终交付的验证报告为准。

## 源码补丁与本机编译

补丁按顺序应用：

1. `0001-centos7-compat.patch`：修正 RHEL 扩展 TC 接口检测、旧 GFP 标志、
   GCC 属性回退、eventfd 头文件及重复 Kconfig 定义。
2. `0002-e610-ptp-compat.patch`：补齐 PTP 延迟工作回退，使用兼容旧版
   `ktime_t` 的时间操作接口。
3. `0003-xarray-lifecycle.patch`：初始化失败或卸载时清理 XArray 缓存，
   清理前等待 RCU 回调完成。

如从官方压缩包构建，在本仓库目录下执行：

```sh
tar -xzf ixgbe-6.4.5.tar.gz
for p in patches/*.patch; do
    patch --batch --fuzz=0 -d ixgbe-6.4.5 -p1 < "$p" || exit 1
done
make -C ixgbe-6.4.5/src -j2 BUILD_KERNEL="$(uname -r)" KSRC="/usr/src/kernels/$(uname -r)"
```

先安装 GCC、make、perl、patch、elfutils-libelf-devel 和与 `uname -r`
完全匹配的 kernel-devel。仅安装 kernel-headers 不能替代 kernel-devel。
`ci/CentOS-Vault.repo` 提供固定的 CentOS 7.9 归档源配置。

本地交付的 `ixgbe-6.4.5-centos7-source.tar.gz` 已应用全部补丁，解压后可直接
运行上述 make 命令，不要再次应用补丁。驱动报告的版本仍为 6.4.5，具体适配
版本通过验证报告中的提交号、补丁 SHA-256 和模块 SHA-256 区分。
