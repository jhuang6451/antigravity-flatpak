<div align="center">
  <img src="icons/hicolor/128x128/apps/com.google.Antigravity.png" alt="Antigravity" width="88" height="88" />

  <h1>Google Antigravity for Linux (Flatpak)</h1>

  <p>Google Antigravity IDE 的 Flatpak 打包与软件源。</p>

  <p><a href="README.md">English</a> · 简体中文</p>

  <p>
    <a href="https://github.com/jhuang6451/antigravity-flatpak/actions/workflows/build-and-deploy.yml"><img src="https://img.shields.io/github/actions/workflow/status/jhuang6451/antigravity-flatpak/build-and-deploy.yml?branch=master&label=build&labelColor=1f1f1f&color=0b57d0" alt="构建状态" /></a>
    <a href="https://github.com/jhuang6451/antigravity-flatpak/actions/workflows/check-update.yml"><img src="https://img.shields.io/github/actions/workflow/status/jhuang6451/antigravity-flatpak/check-update.yml?branch=master&label=upstream%20check&labelColor=1f1f1f&color=0b57d0" alt="上游检查状态" /></a>
    <a href="https://github.com/jhuang6451/antigravity-flatpak/releases/latest"><img src="https://img.shields.io/github/v/release/jhuang6451/antigravity-flatpak?label=release&labelColor=1f1f1f&color=0b57d0" alt="最新版本" /></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-0b57d0?labelColor=1f1f1f" alt="许可证" /></a>
  </p>

  <p>
    <a href="https://jhuang6451.github.io/antigravity-flatpak/">项目主页</a> ·
    <a href="https://github.com/jhuang6451/antigravity-flatpak/releases/latest">下载离线包</a> ·
    <a href="#已知限制">已知限制</a>
  </p>
</div>

## 简介

[Google Antigravity](https://antigravity.google/) 是基于 Electron、内置 AI 智能体的 IDE。Google 为 Linux 提供的是压缩包。本项目把这个压缩包打成 Flatpak,以带 GPG 签名的 OSTree 软件源形式发布在 GitHub Pages 上,之后用 `flatpak update` 即可更新。

构建流程从 Google 下载压缩包,核对清单中记录的 SHA-256 后解包。唯一的二进制改动是给 `webm_encoder` 打补丁,让录屏能在沙箱里工作,详见 [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)。

主要特性:

- 启动脚本会检测 Wayland 并启用对应的 Ozone 参数,也支持用配置文件追加 Electron 参数。
- 通过 `flatpak-spawn --host`,集成终端和智能体可以使用宿主系统上的工具。
- 凭据保存在 GNOME Keyring 或 KDE Wallet 中。
- GitHub Actions 每 6 小时查询一次 Google 的发布接口,发现新版本后自动更新清单、构建并发布。

| | |
| --- | --- |
| 应用 ID | `com.google.Antigravity` |
| 分支 | `stable` |
| Runtime | `org.freedesktop.Platform//25.08`、`org.electronjs.Electron2.BaseApp//25.08` |
| 软件源 | `https://jhuang6451.github.io/antigravity-flatpak/repo` |

当前只构建和发布 **x86_64**,因为 Google 只发布 x86_64 的 Linux 版本。

安装前请先读[权限与安全](#权限与安全)。默认沙箱允许应用读写整个用户目录,也能在宿主系统上执行命令。

## 安装

### 通过软件源安装(推荐)

```bash
flatpak remote-add --if-not-exists antigravity https://jhuang6451.github.io/antigravity-flatpak/antigravity.flatpakrepo
flatpak install antigravity com.google.Antigravity
flatpak run com.google.Antigravity
```

添加软件源后,`flatpak update` 会和其他应用一起更新 Antigravity。应用 Runtime 来自 Flathub,没有启用 Flathub 的系统需要先添加:

```bash
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
```

### 通过 `.flatpakref` 安装

下载 [antigravity.flatpakref](https://jhuang6451.github.io/antigravity-flatpak/antigravity.flatpakref),用 GNOME 软件或 KDE Discover 打开,或者执行 `flatpak install antigravity.flatpakref`。这个文件带有 Flathub 的地址,Runtime 会一并安装。

### 通过离线包安装

在 [Releases](https://github.com/jhuang6451/antigravity-flatpak/releases/latest) 下载 `com.google.Antigravity.flatpak`:

```bash
flatpak install --user com.google.Antigravity.flatpak
```

离线包不会自动更新,升级时需要重新下载。

### 软件源签名

软件源的提交、appstream 分支和 summary 都用 GPG 签名。发布的 `antigravity.flatpakrepo` 和 `antigravity.flatpakref` 以 `GPGKey=` 内嵌了公钥,Flatpak 会拒绝未签名或签名错误的内容。签名密钥:

```text
AGY Flatpak Repo
67EC 8F65 529D BB99 F120  757B B3AF C4AE F302 7676
```

公钥也以 base64 形式保存在 [`pubkey.b64`](pubkey.b64) 中。请使用网站或发布页上的 `.flatpakrepo` 和 `.flatpakref`:git 仓库里的两份只是模板,里面是 `gpg-verify=false`,CI 会在发布的副本里加入公钥。

离线包 `com.google.Antigravity.flatpak` 不走这套校验,请从本仓库的 Releases 页面下载。

### 卸载

```bash
flatpak uninstall com.google.Antigravity
flatpak remote-delete antigravity
```

第一条命令加上 `--delete-data` 会同时删除 `~/.var/app/com.google.Antigravity`。用户目录里你自己的文件不会被动。

## 使用

### 启动参数

启动脚本从下面的文件读取额外的 Chromium 或 Electron 参数,每行一个,空行和以 `#` 开头的行会被忽略。

```text
~/.var/app/com.google.Antigravity/config/antigravity-flags.conf
```

路径在沙箱内对应 `$XDG_CONFIG_HOME`,所以不是 `~/.config`。例如:

```text
--ozone-platform=x11
--enable-features=VaapiVideoDecoder
```

在 Wayland 会话中,启动脚本默认加上 `--ozone-platform-hint=auto` 和 `--enable-features=WaylandWindowDecorations`。你文件里的 `--enable-features=...` 会与默认值合并,因为 Chromium 只认最后一个 `--enable-features` 参数。

启动脚本还会把 `TMPDIR` 设为 `~/.var/app/com.google.Antigravity/cache/tmp`。

### 宿主工具

装在宿主机系统目录里的程序不在沙箱的 `PATH` 中。装在用户目录下的工具(如 `~/.local/bin`)可以直接用。其他程序用 `flatpak-spawn --host <命令>` 调用,`docker`、`podman`、`qemu`、`adb` 也可以这样用,不需要额外权限。

## 权限与安全

这个 Flatpak 的沙箱隔离很弱,请在安装前了解这一点。

- `--filesystem=home` 包含 `~/.ssh`、`~/.gnupg`、浏览器配置目录以及 `$HOME` 下的其他一切。Antigravity 的智能体可以读取并修改这些内容。
- `org.freedesktop.Flatpak` 允许 `flatpak-spawn --host`,即以你的用户权限在沙箱外执行任意命令。其他较窄的设置只能减少应用无意间碰到的范围,拦不住经由 `flatpak-spawn --host` 执行的命令。
- 智能体在集成终端里运行的任何命令,权限都与应用本身相同。
- `--socket=ssh-auth` 让应用能使用 SSH agent 里加载的所有密钥。

执行 `flatpak info --show-permissions com.google.Antigravity` 可以查看你的系统上实际授予的权限。清单申请的权限如下:

| 权限 | 用途 |
| --- | --- |
| `--socket=wayland`、`--socket=fallback-x11`、`--share=ipc` | 显示。有 Wayland 用 Wayland,否则用 X11;`ipc` 用于 X11 共享内存 |
| `--share=network` | 模型 API、扩展市场、Git 远程仓库、更新检查 |
| `--device=dri` | GPU 加速 |
| `--socket=pulseaudio`、`--filesystem=xdg-run/pipewire-0` | 音频,以及用于屏幕捕获的 PipeWire |
| `--filesystem=home` | 读写用户目录,包括点文件 |
| `--socket=ssh-auth` | 转发宿主 SSH agent,用于 SSH 方式的 Git 和远程开发 |
| `--allow=devel` | 允许 `ptrace` 和 `perf`,供 gdb、lldb、strace 等调试器使用 |
| `--talk-name=org.freedesktop.Flatpak` | 通过 `flatpak-spawn --host` 在宿主系统运行命令 |
| `--talk-name=org.freedesktop.Notifications` | 通知 |
| `--talk-name=org.freedesktop.secrets`、`org.kde.kwalletd5`、`org.kde.kwalletd6` | 密钥环 |
| `--talk-name=com.canonical.AppMenu.Registrar`(含 `.*`) | 全局菜单 |
| `--system-talk-name=org.freedesktop.login1` | Electron 电源监控获取挂起、恢复和关机事件 |
| `--env=XCURSOR_PATH=…` | 宿主光标主题 |
| `--env=ELECTRON_TRASH=gio` | 把删除的文件移到桌面回收站 |

### 收紧权限

用户覆盖优先于清单。可以用 [Flatseal](https://flathub.org/apps/com.github.tchx84.Flatseal) 或命令行:

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

以下内容默认关闭:

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

## 已知限制

- **仅 x86_64。** 上游只发布 x86_64 的 Linux 版本。
- **默认没有设备访问。** 只有 `--device=dri` 时,沙箱里没有 `/dev/kvm`、USB(`/dev/bus/usb`)和串口(`/dev/ttyUSB*`)。刷写硬件、通过 USB 使用 `adb`、硬件加速的模拟器都无法在沙箱内运行,需要先[放宽权限](#放宽权限)。
- **看不到用户目录以外的路径。** `/mnt`、`/media`、`/run/media`、`/srv`、`/opt` 和 `/var/www` 不可见。
- **看不到容器套接字。** 直接连接 Docker 或 Podman 守护进程的工具,要先授权才能访问。
- **Fedora Atomic 和 Silverblue 上写死的 `/home/...` 路径会失败。** 这类系统的用户目录是 `/var/home/<用户名>`,`/home` 是符号链接,沙箱里没有它。请改用 `$HOME` 或 `~`。
- **内置更新器未经测试。** Flatpak 里应用目录是只读的。请通过 Flatpak 更新,忽略应用内的更新提示。
- **上游不提供校验和。** Google 没有公布压缩包的校验和。CI 记录的是它下载到的文件的 SHA-256,只能把构建固定到这份文件,不能证明它就是 Google 想发布的内容。
- **离线包的 Runtime 不会自动安装。** 安装前需要启用 Flathub。

在默认权限下,从沙箱内部验证过的功能有:GPU 加速(含 NVIDIA 设备节点)、音频、通过打过补丁的 `webm_encoder` 录屏、读写 `$HOME`、`~/.gitconfig`、`~/.ssh`,以及运行 `~/.local/bin` 里的工具。

## 本地构建

需要 `flatpak` 和 `flatpak-builder`,缺少 Runtime 时脚本会自动安装:

```bash
git clone https://github.com/jhuang6451/antigravity-flatpak.git
cd antigravity-flatpak

# 只检查上游版本,不改动任何文件
python3 scripts/update-checker.py --check

# 把清单和 metainfo 更新到上游最新版本
python3 scripts/update-checker.py --update

# 构建、导出到 ./repo 并生成离线包
./scripts/build-local.sh
flatpak install --user --bundle com.google.Antigravity.flatpak
```

给检查脚本加上 `--force --update`,可以重新计算当前版本的 SHA-256。

## 自动更新流程

1. `check-update.yml` 每 6 小时运行 `scripts/update-checker.py`,查询 Google 的发布接口。
2. 有新版本时,脚本下载压缩包,把 SHA-256 写入 `com.google.Antigravity.yaml`,并在 `com.google.Antigravity.metainfo.xml` 里添加版本记录,然后提交到 `master`。
3. 提交触发 `build-and-deploy.yml`:构建 Flatpak,签名软件源,创建 GitHub Release,并通过 GitHub Pages 发布 OSTree 仓库和项目主页。

所以上游发布新版本后,要等下一次检查加上构建时间,软件源才会跟进。每次发布都会从空仓库重新构建,软件源里只有最新一个提交。OSTree 按文件内容寻址,客户端更新时只下载本地没有的对象,但仓库不保存历史版本,也不提供从旧版本出发的增量包。

流水线、签名和 `webm_encoder` 补丁的工作方式见 [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)(英文)。

## 许可证与商标

本仓库的打包文件(清单、脚本、工作流、网页)以 [MIT 许可证](LICENSE)发布。Antigravity 是 Google LLC 的专有软件,适用其自身的条款。Antigravity 及其标志是 Google LLC 的商标,本项目与 Google 没有隶属关系,也未获其背书。
