# E610 多系统离线安装包 r3

同一个包自动识别系统和精确内核，无需联网、make、编译器或内核头文件，不升级官方内核。支持范围请查同目录 `SUPPORTED-SYSTEMS.zh-CN.md`；只支持 x86_64 / amd64。

## 最方便：运行 .run

将文件复制到目标系统，然后执行：

```bash
sudo bash E610-MultiOS-6.4.5-r3.run
```

完成后在维护窗口重启。安装过程不会主动卸载正在使用的网卡驱动，也不会自动重启或修改网络配置。

```bash
ip -br link
cat /sys/module/ixgbe/version
```

原生支持的内核会显示无需安装。未知内核若未检测到 E610 支持，会停止并保留系统原状；请提供 `cat /etc/os-release` 和 `uname -rm` 输出补包。

## KVM 挂载 ISO

这是驱动数据光盘，不是系统安装盘，也不能作为启动盘。通过带外 KVM 的虚拟光驱挂载 ISO，登录已经安装好的系统：

```bash
sudo mkdir -p /mnt/e610
sudo mount -o ro /dev/sr0 /mnt/e610
sudo bash /mnt/e610/install.sh
```

有多个光驱时，先用 `lsblk -f` 找到卷标 `E610_MULTIOS`，用其设备名替换 `/dev/sr0`。

## 使用 tar.gz

```bash
tar -xzf E610-MultiOS-6.4.5-r3.tar.gz
cd E610-MultiOS-6.4.5-r3
sudo bash install.sh
```

## 预检查、Secure Boot 和回退

预检查不会安装驱动：

```bash
sudo bash E610-MultiOS-6.4.5-r3.run --check
```

新增外部模块已经过 Secure Boot 内核加载测试。开启 Secure Boot 的机器首次安装通常需要注册包内公钥：按提示设置一次性密码，重启进入 Enroll MOK → Continue → Yes → 输入密码 → Reboot，随后再次运行安装命令。此交互不能在所有固件上自动完成。

从 ISO Kit 导入的历史模块尚未完成本次 Secure Boot 验证，统一包要求关闭 Secure Boot；原有 CentOS 7.9 模块也未签名。原 r2 的其他组合保留原证书及原安装行为。

安装会备份原模块、配置和启动镜像。重复安装相同包会保留第一次备份。回退命令：

```bash
sudo bash E610-MultiOS-6.4.5-r3.run --rollback
```

通过 .run / ISO 安装后，文件保存在 `/opt/e610-offline/multios-6.4.5-r3`，卸载虚拟光驱后仍可使用：

```bash
sudo bash /opt/e610-offline/multios-6.4.5-r3/install.sh --rollback
```

回退后需要重启；不会自动删除已经注册的 MOK 公钥。安装原 r2 支持的系统时，会继续使用原 r2 / 原独立包的备份，避免覆盖历史回退点。

## 校验下载

从同一 Release 下载 `SHA256SUMS`，与产物放在同一目录。下载完整产物时执行：

```bash
sha256sum -c SHA256SUMS
```

只下载 .run 时可使用：

```bash
grep '  E610-MultiOS-6.4.5-r3.run$' SHA256SUMS | sha256sum -c -
```

安装器还会核对内嵌压缩包、驱动和证书。内核升级后必须重新匹配；本包不提供任意内核的自动编译服务。

下载入口：<https://github.com/SkyWalkerAMD/E610/releases>。
