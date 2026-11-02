同一套 **tar.gz、.run 和 KVM 驱动数据 ISO**，自动匹配系统和精确内核。目标机器无需联网、make、编译器或内核头文件，不升级官方内核。

本版按指定镜像库核对 **52 张 Linux ISO**，补齐此前缺少的 4 张镜像对应的 3 个内核组合，总计 **93 个精确系统/内核组合**：77 个提供离线驱动，16 个检查原生支持。

| 本次补齐 | 精确内核 | 处理方式 |
| --- | --- | --- |
| Debian 10.11 | `4.19.0-18-amd64` | 离线安装 ixgbe 6.4.5，要求关闭 Secure Boot |
| Ubuntu 25.04 Server | `6.14.0-15-generic` | 检查原生 E610 支持，无需额外驱动 |
| Ubuntu 26.04 Server / Desktop | `7.0.0-14-generic` | 检查原生 E610 支持，无需额外驱动 |

原 r3 的 90 个组合完整保留，包括 Ubuntu 20/22/24、Debian 11–13、CentOS、RHEL 7–9、AlmaLinux 和 Rocky 的已验证内核。原模块、证书及回退备份继续沿用。[完整支持清单](https://github.com/SkyWalkerAMD/E610/blob/main/mirror/SUPPORTED-SYSTEMS.zh-CN.md) · [逐镜像核对记录](https://github.com/SkyWalkerAMD/E610/releases/download/v6.4.5-multios-r4/MIRROR-COVERAGE.json)

最简安装：

```bash
sudo bash E610-MultiOS-6.4.5-r4.run
```

KVM 挂载 ISO 后，在已安装的 Linux 系统中运行光盘里的 `install.sh`。这是驱动数据盘，不是可启动的系统安装盘。支持 `--check` 和 `--rollback`，详见[中文安装说明](https://github.com/SkyWalkerAMD/E610/releases/download/v6.4.5-multios-r4/INSTALL.zh-CN.md)。

验证：3 个新增内核完成真实模块加载/卸载；Debian 10.11 通过离线安装、重复安装、回退、损坏备份拒绝及故障恢复。最终产物通过 **6 项实际只读 ISO / tar.gz / .run 入口与回退测试**，包含 Debian 11、RHEL 8 从原 r3 包升级后的备份保留检查。镜像库核对是逐启动内核和模块检查，不表示重新完成了 52 次系统安装。

范围以指定镜像库为准：其中没有 **RHEL 10 或 Oracle Linux/UEK**，因此本版不宣称覆盖这两类系统。仅支持清单内 x86_64/amd64 内核；Windows、内存测试镜像、其他架构和清单外更新内核不在范围内。本轮没有 E610 实卡，未验证实机链路、吞吐、PTP、SR-IOV 或长期稳定性。

[SHA256SUMS](https://github.com/SkyWalkerAMD/E610/releases/download/v6.4.5-multios-r4/SHA256SUMS) · [最终介质验证记录](https://github.com/SkyWalkerAMD/E610/releases/download/v6.4.5-multios-r4/MEDIA-VALIDATION.json) · [测试日志](https://github.com/SkyWalkerAMD/E610/releases/download/v6.4.5-multios-r4/MEDIA-TEST-LOGS.tar.gz)

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
