<div align="center">
  <img src="icons/hicolor/128x128/apps/com.google.Antigravity.png" alt="Antigravity" width="88" height="88" />

  <h1>Google Antigravity for Linux (Flatpak)</h1>

  <p>Flatpak packaging and a software repository for Google's Antigravity IDE.</p>

  <p>
    <a href="https://github.com/jhuang6451/antigravity-flatpak/actions/workflows/build-and-deploy.yml"><img src="https://img.shields.io/github/actions/workflow/status/jhuang6451/antigravity-flatpak/build-and-deploy.yml?branch=master&label=build&labelColor=1f1f1f&color=0b57d0" alt="Build status" /></a>
    <a href="https://github.com/jhuang6451/antigravity-flatpak/actions/workflows/check-update.yml"><img src="https://img.shields.io/github/actions/workflow/status/jhuang6451/antigravity-flatpak/check-update.yml?branch=master&label=upstream%20check&labelColor=1f1f1f&color=0b57d0" alt="Upstream check status" /></a>
    <a href="https://github.com/jhuang6451/antigravity-flatpak/releases/latest"><img src="https://img.shields.io/github/v/release/jhuang6451/antigravity-flatpak?label=release&labelColor=1f1f1f&color=0b57d0" alt="Latest release" /></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-0b57d0?labelColor=1f1f1f" alt="License" /></a>
  </p>

  <p>English · <a href="README.zh-CN.md">简体中文</a></p>

  <p>
    <a href="https://jhuang6451.github.io/antigravity-flatpak/">Website</a> ·
    <a href="https://github.com/jhuang6451/antigravity-flatpak/releases/latest">Offline bundle</a> ·
    <a href="#known-limitations">Known limitations</a>
  </p>
</div>

## Overview

[Google Antigravity](https://antigravity.google/) is an Electron-based IDE with built-in AI agents. Google ships it for Linux as a tarball. This project wraps that tarball in a Flatpak and publishes it as a GPG-signed OSTree repository on GitHub Pages, so `flatpak update` keeps it current.

The build downloads the tarball from Google, checks the SHA-256 recorded in the manifest, and unpacks it. The only binary change is a patch to `webm_encoder` so that screen recording works inside the sandbox; [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) explains it.

- The launcher detects Wayland and enables the matching Ozone flags. A config file can add more Electron flags.
- `flatpak-spawn --host` gives the integrated terminal and agents access to host tools.
- Credentials are stored in GNOME Keyring or KDE Wallet.
- GitHub Actions checks Google's release API every 6 hours. When a new version appears, it updates the manifest, builds, and publishes.

| | |
| --- | --- |
| App ID | `com.google.Antigravity` |
| Branch | `stable` |
| Runtime | `org.freedesktop.Platform//25.08`, `org.electronjs.Electron2.BaseApp//25.08` |
| Repository | `https://jhuang6451.github.io/antigravity-flatpak/repo` |

Only **x86_64** is built and published, because Google publishes only x86_64 Linux builds.

Read [Permissions and security](#permissions-and-security) before installing. The default sandbox gives the app read and write access to your whole home directory, and it can run commands on the host.

## Installation

### From the repository (recommended)

```bash
flatpak remote-add --if-not-exists antigravity https://jhuang6451.github.io/antigravity-flatpak/antigravity.flatpakrepo
flatpak install antigravity com.google.Antigravity
flatpak run com.google.Antigravity
```

Once the remote is added, `flatpak update` updates Antigravity along with your other apps. The runtime comes from Flathub, so add Flathub first if it isn't enabled:

```bash
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
```

### From a `.flatpakref`

Download [antigravity.flatpakref](https://jhuang6451.github.io/antigravity-flatpak/antigravity.flatpakref) and open it with GNOME Software or KDE Discover, or run `flatpak install antigravity.flatpakref`. The file includes the Flathub URL, so the runtime is installed too.

### From the offline bundle

Download `com.google.Antigravity.flatpak` from [Releases](https://github.com/jhuang6451/antigravity-flatpak/releases/latest):

```bash
flatpak install --user com.google.Antigravity.flatpak
```

The bundle doesn't update itself. To upgrade, download a new one.

### Repository signing

Commits, appstream branches, and the summary file are signed with GPG. The published `antigravity.flatpakrepo` and `antigravity.flatpakref` embed the public key as `GPGKey=`, so Flatpak refuses unsigned or wrongly signed content. The signing key is:

```text
AGY Flatpak Repo
67EC 8F65 529D BB99 F120  757B B3AF C4AE F302 7676
```

The public key is also committed as [`pubkey.b64`](pubkey.b64) (base64). Use the `.flatpakrepo` and `.flatpakref` from the website or a release: the copies in this git repository are templates with `gpg-verify=false`, and CI adds the key to the published copies.

The offline bundle is not covered by this verification, so download it only from this repository's Releases page.

### Uninstalling

```bash
flatpak uninstall com.google.Antigravity
flatpak remote-delete antigravity
```

Add `--delete-data` to the first command to also remove `~/.var/app/com.google.Antigravity`. Files in your home directory are never touched.

## Usage

### Launch flags

The launcher reads extra Chromium or Electron flags from the file below, one flag per line. Blank lines and lines starting with `#` are ignored.

```text
~/.var/app/com.google.Antigravity/config/antigravity-flags.conf
```

Inside the sandbox this path is `$XDG_CONFIG_HOME`, not `~/.config`. For example:

```text
--ozone-platform=x11
--enable-features=VaapiVideoDecoder
```

On Wayland sessions the launcher adds `--ozone-platform-hint=auto` and `--enable-features=WaylandWindowDecorations` by default. If your config file also sets `--enable-features=...`, the launcher merges it with the defaults, because Chromium only honors the last `--enable-features` flag.

The launcher also sets `TMPDIR` to `~/.var/app/com.google.Antigravity/cache/tmp`.

### Host tools

Programs installed system-wide on the host are not on the sandbox `PATH`. Tools installed under your home directory (for example in `~/.local/bin`) work. For anything else, use `flatpak-spawn --host <command>`, which also covers `docker`, `podman`, `qemu`, and `adb` without extra permissions.

## Permissions and security

This Flatpak has weak sandbox isolation. Read this before installing.

- `--filesystem=home` includes `~/.ssh`, `~/.gnupg`, browser profiles, and everything else in `$HOME`. Antigravity's agents can read and change all of it.
- `org.freedesktop.Flatpak` permits `flatpak-spawn --host`, which runs any command outside the sandbox with your user's rights. The narrower settings only limit what the app touches by accident, and they don't stop a command that goes through `flatpak-spawn --host`.
- Anything an agent runs in the integrated terminal has the same access as the app itself.
- `--socket=ssh-auth` lets the app use every key loaded in your SSH agent.

Run `flatpak info --show-permissions com.google.Antigravity` to see what is granted on your system. The manifest requests:

| Permission | Purpose |
| --- | --- |
| `--socket=wayland`, `--socket=fallback-x11`, `--share=ipc` | Display. Wayland when available, X11 otherwise; `ipc` is for X11 shared memory |
| `--share=network` | Model APIs, extension marketplace, Git remotes, update checks |
| `--device=dri` | GPU acceleration |
| `--socket=pulseaudio`, `--filesystem=xdg-run/pipewire-0` | Audio, and PipeWire for screen capture |
| `--filesystem=home` | Read and write the home directory, including dotfiles |
| `--socket=ssh-auth` | Host SSH agent for Git over SSH and remote development |
| `--allow=devel` | `ptrace` and `perf` for debuggers such as gdb, lldb, and strace |
| `--talk-name=org.freedesktop.Flatpak` | Run commands on the host with `flatpak-spawn --host` |
| `--talk-name=org.freedesktop.Notifications` | Notifications |
| `--talk-name=org.freedesktop.secrets`, `org.kde.kwalletd5`, `org.kde.kwalletd6` | Keyring |
| `--talk-name=com.canonical.AppMenu.Registrar` (and `.*`) | Global menu |
| `--system-talk-name=org.freedesktop.login1` | Suspend, resume, and shutdown events for Electron's power monitor |
| `--env=XCURSOR_PATH=…` | Host cursor theme |
| `--env=ELECTRON_TRASH=gio` | Move deleted files to the desktop trash |

### Tightening

User overrides take precedence over the manifest. Use [Flatseal](https://flathub.org/apps/com.github.tchx84.Flatseal) or the command line:

```bash
# Only one project directory instead of all of $HOME
flatpak override --user --nofilesystem=home --filesystem=~/Projects com.google.Antigravity

# Drop host command execution (the integrated terminal then stays inside the sandbox)
flatpak override --user --no-talk-name=org.freedesktop.Flatpak com.google.Antigravity

# Drop the SSH agent
flatpak override --user --nosocket=ssh-auth com.google.Antigravity

# Undo every override
flatpak override --user --reset com.google.Antigravity
```

If you remove `home`, the app no longer sees `~/.gitconfig`, `~/.ssh`, or tools in `~/.local/bin` unless you add them back with `--filesystem`.

### Widening

These are off by default:

```bash
# /dev/kvm for QEMU and the Android emulator (needs a recent Flatpak)
flatpak override --user --device=kvm com.google.Antigravity

# USB and serial devices (/dev/bus/usb, /dev/ttyUSB*). This exposes every device node.
flatpak override --user --device=all com.google.Antigravity

# External disks and other top-level paths
flatpak override --user --filesystem=/mnt --filesystem=/run/media --filesystem=/media com.google.Antigravity
flatpak override --user --filesystem=/srv --filesystem=/opt com.google.Antigravity

# Podman and Docker sockets
flatpak override --user --filesystem=xdg-run/podman com.google.Antigravity
flatpak override --user --filesystem=/run/docker.sock com.google.Antigravity
```

Access to the Docker socket is equivalent to root on the host.

## Known limitations

- **x86_64 only.** Upstream publishes only x86_64 Linux builds.
- **No device access by default.** With only `--device=dri`, the sandbox has no `/dev/kvm`, USB (`/dev/bus/usb`), or serial ports (`/dev/ttyUSB*`). Hardware flashing, `adb` over USB, and hardware-accelerated emulators fail inside the sandbox until you [widen](#widening) access.
- **Paths outside home are hidden.** `/mnt`, `/media`, `/run/media`, `/srv`, `/opt`, and `/var/www` are not visible.
- **Container sockets are hidden.** Tools that talk to the Docker or Podman daemon directly can't reach it until you grant access.
- **Hardcoded `/home/...` paths fail on Fedora Atomic and Silverblue.** There your home is `/var/home/<user>`, and `/home` is a symlink that doesn't exist inside the sandbox. Use `$HOME` or `~`.
- **The built-in updater is untested.** The app directory is read-only in Flatpak. Update through Flatpak and ignore any in-app update prompt.
- **No upstream checksums.** Google doesn't publish checksums for the tarball. CI records the SHA-256 of the file it downloaded, which pins the build to those bytes but doesn't prove they are what Google intended to publish.
- **The offline bundle doesn't install the runtime.** Enable Flathub before installing it.

Verified inside the sandbox with the default permissions: GPU acceleration (including NVIDIA device nodes), audio, screen recording through the patched `webm_encoder`, reading and writing under `$HOME`, `~/.gitconfig`, `~/.ssh`, and running tools from `~/.local/bin`.

## Building locally

You need `flatpak` and `flatpak-builder`. The script installs the runtimes if they are missing.

```bash
git clone https://github.com/jhuang6451/antigravity-flatpak.git
cd antigravity-flatpak

# Check upstream without changing anything
python3 scripts/update-checker.py --check

# Update the manifest and metainfo to the latest upstream version
python3 scripts/update-checker.py --update

# Build, export to ./repo and create a bundle
./scripts/build-local.sh
flatpak install --user --bundle com.google.Antigravity.flatpak
```

Pass `--force --update` to the checker to recompute the SHA-256 of the current version.

## Automatic updates

1. `check-update.yml` runs `scripts/update-checker.py` every 6 hours and queries Google's release API.
2. When there is a new version, the script downloads the tarball, records its SHA-256 in `com.google.Antigravity.yaml`, adds a release entry to `com.google.Antigravity.metainfo.xml`, and commits to `master`.
3. The commit triggers `build-and-deploy.yml`, which builds the Flatpak, signs the repository, creates a GitHub Release, and publishes the OSTree repository and the website through GitHub Pages.

A new upstream release therefore reaches the repository after the next check plus the build time. Each release is built from an empty repository, so the remote holds only the latest commit. OSTree addresses files by content, and clients download only the objects they don't already have. The repository keeps no history and offers no deltas from older versions.

How the pipeline, the signing, and the `webm_encoder` patch work is described in [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md).

## License and trademarks

The packaging files in this repository (manifest, scripts, workflows, web pages) are released under the [MIT License](LICENSE). Antigravity is proprietary software that belongs to Google LLC and is covered by its own terms. Antigravity and the Antigravity logo are trademarks of Google LLC. This project is not affiliated with or endorsed by Google.
