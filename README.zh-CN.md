# Antigravity Flatpak

[English](README.md) | 简体中文

[![构建](https://img.shields.io/github/actions/workflow/status/jhuang6451/antigravity-flatpak/build-and-deploy.yml?branch=master&label=build)](https://github.com/jhuang6451/antigravity-flatpak/actions/workflows/build-and-deploy.yml)
[![更新检查](https://img.shields.io/github/actions/workflow/status/jhuang6451/antigravity-flatpak/check-update.yml?branch=master&label=update%20check)](https://github.com/jhuang6451/antigravity-flatpak/actions/workflows/check-update.yml)
[![最新版本](https://img.shields.io/github/v/release/jhuang6451/antigravity-flatpak?label=release)](https://github.com/jhuang6451/antigravity-flatpak/releases/latest)
[![许可证: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

[Google Antigravity](https://antigravity.google/) 的非官方 Flatpak 包。Antigravity 是基于 Electron、内置 AI 智能体的 IDE。本项目取 Google 发布的 Linux 压缩包,打成 Flatpak,以带 GPG 签名的软件源形式发布在 GitHub Pages 上,之后用 `flatpak update` 即可更新。项目与 Google 无关联,也未获得 Google 认可。

| | |
|---|---|
| 应用 ID | `com.google.Antigravity` |
| 分支 | `stable` |
| 架构 | 仅 x86_64 |
| 运行时 | `org.freedesktop.Platform//25.08`、`org.electronjs.Electron2.BaseApp//25.08` |
| 软件源 | https://jhuang6451.github.io/antigravity-flatpak/repo |
| 网站 | https://jhuang6451.github.io/antigravity-flatpak/ |

安装前请先读[权限](#权限)。默认沙箱允许应用读写整个家目录,也能在宿主机上执行命令。

## 安装

需要 Flatpak 和 Flathub 软件源,运行时从 Flathub 获取。没有配置 Flathub 的话,请用方式 2,`.flatpakref` 文件会帮你添加。

### 1. 从软件源安装(可接收更新)

```bash
flatpak remote-add --if-not-exists antigravity https://jhuang6451.github.io/antigravity-flatpak/antigravity.flatpakrepo
flatpak install antigravity com.google.Antigravity
flatpak run com.google.Antigravity
```

### 2. 用 .flatpakref 文件安装(可接收更新)

从[网站](https://jhuang6451.github.io/antigravity-flatpak/)或[最新发布](https://github.com/jhuang6451/antigravity-flatpak/releases/latest)下载 `antigravity.flatpakref`,用 GNOME Software 或 KDE Discover 打开,或者执行:

```bash
flatpak install antigravity.flatpakref
```

### 3. 用离线安装包安装(不会更新)

从[最新发布](https://github.com/jhuang6451/antigravity-flatpak/releases/latest)下载 `com.google.Antigravity.flatpak`:

```bash
flatpak install com.google.Antigravity.flatpak
```

请使用网站或发布页上的 `.flatpakrepo` 和 `.flatpakref`。git 仓库里的那两份只是模板,里面是 `gpg-verify=false`,CI 会在发布的副本里加入公钥。

## 更新

```bash
flatpak update com.google.Antigravity
```

定时工作流每 6 小时查询一次 Google 的发布接口。发现新版本后,它会更新清单并触发构建。所以上游发布新版本后,要等下一次检查加上构建时间,软件源才会跟进。

## 卸载

```bash
flatpak uninstall com.google.Antigravity
flatpak remote-delete antigravity
```

第一条命令加上 `--delete-data` 会同时删除 `~/.var/app/com.google.Antigravity`。家目录里你自己的文件不会被动。

## 权限

执行 `flatpak info --show-permissions com.google.Antigravity` 可以查看你的系统上实际授予了哪些权限。清单申请的权限如下。

| 权限 | 用途 |
|---|---|
| `--socket=wayland`、`--socket=fallback-x11`、`--share=ipc` | 显示。有 Wayland 用 Wayland,否则用 X11。`ipc` 用于 X11 共享内存。 |
| `--share=network` | 访问模型 API、扩展市场、Git 远程仓库和更新检查。 |
| `--device=dri` | 使用 GPU 做硬件加速。 |
| `--socket=pulseaudio`、`--filesystem=xdg-run/pipewire-0` | 音频,以及用于屏幕捕获的 PipeWire。 |
| `--filesystem=home` | 读写家目录,包括点文件。项目和工具都放在这里。 |
| `--socket=ssh-auth` | 转发宿主机的 SSH agent,用于 SSH 方式的 Git 和远程开发。 |
| `--allow=devel` | 允许 `ptrace` 和 `perf`,gdb、lldb、strace 等调试器需要它们。 |
| `--talk-name=org.freedesktop.Flatpak` | 允许应用执行 `flatpak-spawn --host`,借此打开宿主机 shell 或调用宿主机上的工具。 |
| `--talk-name=org.freedesktop.Notifications` | 桌面通知。 |
| `--talk-name=org.freedesktop.secrets`、`org.kde.kwalletd5`、`org.kde.kwalletd6` | 把凭据存进 GNOME Keyring 或 KWallet。 |
| `--talk-name=com.canonical.AppMenu.Registrar`(含 `.*`) | 在提供全局菜单的桌面上显示全局菜单栏。 |
| `--system-talk-name=org.freedesktop.login1` | Electron 的电源监控通过 logind 获取挂起、恢复和关机事件。 |
| `--env=XCURSOR_PATH=…` | 找到宿主机的光标主题。 |
| `--env=ELECTRON_TRASH=gio` | 把删除的文件移到桌面回收站。 |

### 沙箱能防什么,不能防什么

- `--filesystem=home` 包含 `~/.ssh`、`~/.gnupg`、浏览器配置目录以及 `$HOME` 下的其他一切。Antigravity 的智能体可以读取并修改这些内容。
- `org.freedesktop.Flatpak` 允许 `flatpak-spawn --host`,即以你的用户权限在沙箱外执行任意命令。这等于抵消了把权限收窄到 `home` 和 `dri` 所带来的隔离。收窄只能减少应用无意间碰到的范围,拦不住经由 `flatpak-spawn --host` 执行的命令。
- 智能体在集成终端里运行的任何命令,权限都与应用本身相同。
- `--socket=ssh-auth` 让应用能使用 SSH agent 里加载的所有密钥。

### 收紧权限

用户覆盖优先于清单。例如:

```bash
# 只开放一个项目目录,不开放整个 $HOME
flatpak override --user --nofilesystem=home --filesystem=~/Projects com.google.Antigravity

# 去掉宿主机命令执行(集成终端随之留在沙箱内)
flatpak override --user --no-talk-name=org.freedesktop.Flatpak com.google.Antigravity

# 去掉 SSH agent
flatpak override --user --nosocket=ssh-auth com.google.Antigravity

# 撤销所有覆盖
flatpak override --user --reset com.google.Antigravity
```

去掉 `home` 后,应用看不到 `~/.gitconfig`、`~/.ssh` 和 `~/.local/bin` 里的工具,需要的话用 `--filesystem` 单独加回来。

### 放宽权限

默认权限保持较窄,以下内容需要自行开启:

```bash
# /dev/kvm,用于 QEMU 和 Android 模拟器(需要较新的 Flatpak)
flatpak override --user --device=kvm com.google.Antigravity

# USB 和串口(/dev/bus/usb、/dev/ttyUSB*)。这会暴露所有设备节点。
flatpak override --user --device=all com.google.Antigravity

# 外接磁盘和其他顶层路径
flatpak override --user --filesystem=/mnt --filesystem=/run/media --filesystem=/media com.google.Antigravity
flatpak override --user --filesystem=/srv --filesystem=/opt com.google.Antigravity

# Podman 和 Docker 套接字
flatpak override --user --filesystem=xdg-run/podman com.google.Antigravity
flatpak override --user --filesystem=/run/docker.sock com.google.Antigravity
```

能访问 Docker 套接字就等于拥有宿主机的 root 权限。

不开启这些也行:`org.freedesktop.Flatpak` 权限让 `flatpak-spawn --host docker ...`(或 `podman`、`qemu`、`adb`)照样可用。

## 已知限制

- 设备。只有 `--device=dri` 时,沙箱里没有 `/dev/kvm`、USB(`/dev/bus/usb`)和串口(`/dev/ttyUSB*`)。刷写硬件、通过 USB 使用 `adb`、硬件加速的模拟器,都无法在沙箱内运行。见[放宽权限](#放宽权限)。
- 家目录以外的路径。`/mnt`、`/media`、`/run/media`、`/srv`、`/opt` 和 `/var/www` 看不到。
- 容器套接字。Docker 和 Podman 的套接字看不到。直接连接守护进程的工具,要先授权才能访问。
- Fedora Atomic 和 Silverblue 上写死的 `/home/...` 路径。这类系统的家目录是 `/var/home/<用户名>`,宿主机上 `/home` 是指向它的符号链接,沙箱里没有这个链接,所以 `/home/<用户名>/...` 形式的路径会失败。请改用 `$HOME` 或 `~`。
- 宿主机工具。装在宿主机系统目录里的程序不在沙箱的 `PATH` 中。装在家目录下的工具(如 `~/.local/bin`)可以用。其他情况请用 `flatpak-spawn --host <命令>`。
- 内置更新器。Antigravity 自带更新机制,而 Flatpak 里应用目录是只读的,这个更新器在其中的表现尚未测试。请通过 Flatpak 更新,应用内的更新提示可以忽略。
- 架构。上游只发布 x86_64 的 Linux 版本,所以没有 aarch64 包。
- 上游不提供校验和。Google 没有公布压缩包的校验和。CI 下载文件后把 SHA256 记入清单,这个哈希只能保证构建用的是 CI 当时拿到的那份文件,不能证明那份文件就是 Google 想发布的内容。

在默认权限下,从沙箱内部验证过的功能有:GPU 加速(含 NVIDIA 设备节点)、音频、通过打过补丁的 `webm_encoder` 录屏、读写 `$HOME`、`~/.gitconfig`、`~/.ssh`,以及运行 `~/.local/bin` 里的工具。

## 配置

要给 Chromium 或 Electron 传额外参数,创建 `~/.var/app/com.google.Antigravity/config/antigravity-flags.conf`,每行写一个参数。空行和以 `#` 开头的行会被忽略。

```text
# 示例
--ozone-platform=x11
--enable-features=VaapiVideoDecoder
```

在 Wayland 下,启动脚本会加上 `--ozone-platform-hint=auto` 和 `WaylandWindowDecorations` 特性。你文件里的 `--enable-features=` 行会与它们合并,因为 Chromium 只认最后一个 `--enable-features` 参数。

启动脚本把 `TMPDIR` 设为 `~/.var/app/com.google.Antigravity/cache/tmp`。

## 验证软件源

软件源及其提交由下面这把密钥签名:

```text
AGY Flatpak Repo
67EC 8F65 529D BB99 F120  757B B3AF C4AE F302 7676
```

公钥以 base64 形式保存在 [`pubkey.b64`](pubkey.b64) 中,并作为 `GPGKey=` 写入发布的 `.flatpakrepo` 和 `.flatpakref`。软件源里未签名或签名错误的内容,Flatpak 会拒绝。

## 本地构建

```bash
# 只检查上游版本,不改动任何文件
python3 scripts/update-checker.py --check

# 把清单和 metainfo 更新到上游最新版本
python3 scripts/update-checker.py --update

# 构建、导出到 ./repo 并生成安装包(缺少运行时会自动安装)
./scripts/build-local.sh
flatpak install --user --bundle com.google.Antigravity.flatpak
```

给检查脚本加上 `--force --update`,可以重新计算当前版本的 SHA256。

流水线、签名和 `webm_encoder` 补丁的工作方式见 [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)(英文)。

## 许可证

本仓库的打包文件(清单、脚本、工作流、网页)以 [MIT 许可证](LICENSE)发布。Antigravity 是 Google LLC 的专有软件,适用其自身的条款。Antigravity 及其标志是 Google 的商标。
