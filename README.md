# Antigravity Flatpak

English | [简体中文](README.zh-CN.md)

[![Build and deploy](https://img.shields.io/github/actions/workflow/status/jhuang6451/antigravity-flatpak/build-and-deploy.yml?branch=master&label=build)](https://github.com/jhuang6451/antigravity-flatpak/actions/workflows/build-and-deploy.yml)
[![Update check](https://img.shields.io/github/actions/workflow/status/jhuang6451/antigravity-flatpak/check-update.yml?branch=master&label=update%20check)](https://github.com/jhuang6451/antigravity-flatpak/actions/workflows/check-update.yml)
[![Latest release](https://img.shields.io/github/v/release/jhuang6451/antigravity-flatpak?label=release)](https://github.com/jhuang6451/antigravity-flatpak/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Unofficial Flatpak package of [Google Antigravity](https://antigravity.google/), the Electron-based IDE with built-in AI agents. The project takes Google's Linux tarball, wraps it in a Flatpak, and publishes it as a GPG-signed repository on GitHub Pages, so `flatpak update` keeps it current. It is not affiliated with or endorsed by Google.

| | |
|---|---|
| App ID | `com.google.Antigravity` |
| Branch | `stable` |
| Architecture | x86_64 only |
| Runtime | `org.freedesktop.Platform//25.08`, `org.electronjs.Electron2.BaseApp//25.08` |
| Repository | https://jhuang6451.github.io/antigravity-flatpak/repo |
| Website | https://jhuang6451.github.io/antigravity-flatpak/ |

Read [Permissions](#permissions) before installing. The default sandbox gives the app read and write access to your whole home directory, and it can run commands on the host.

## Install

You need Flatpak and the Flathub remote. Flathub supplies the runtime. If Flathub is not configured, use method 2: the `.flatpakref` file adds it for you.

### 1. From the repository (receives updates)

```bash
flatpak remote-add --if-not-exists antigravity https://jhuang6451.github.io/antigravity-flatpak/antigravity.flatpakrepo
flatpak install antigravity com.google.Antigravity
flatpak run com.google.Antigravity
```

### 2. From a .flatpakref file (receives updates)

Download `antigravity.flatpakref` from the [website](https://jhuang6451.github.io/antigravity-flatpak/) or the [latest release](https://github.com/jhuang6451/antigravity-flatpak/releases/latest), then open it in GNOME Software or KDE Discover, or run:

```bash
flatpak install antigravity.flatpakref
```

### 3. From an offline bundle (no updates)

Download `com.google.Antigravity.flatpak` from the [latest release](https://github.com/jhuang6451/antigravity-flatpak/releases/latest):

```bash
flatpak install com.google.Antigravity.flatpak
```

Use the `.flatpakrepo` and `.flatpakref` files from the website or from a release. The copies in this git repository are templates with `gpg-verify=false`. CI adds the public key to the published copies.

## Update

```bash
flatpak update com.google.Antigravity
```

A scheduled workflow checks Google's release API every 6 hours. When it finds a new version, it updates the manifest and starts a build. A new upstream release therefore reaches the repository after the next check plus the build time.

## Uninstall

```bash
flatpak uninstall com.google.Antigravity
flatpak remote-delete antigravity
```

Add `--delete-data` to the first command to also remove `~/.var/app/com.google.Antigravity`. Files in your home directory are never touched.

## Permissions

Run `flatpak info --show-permissions com.google.Antigravity` to see what is granted on your system. The manifest requests the following.

| Permission | Reason |
|---|---|
| `--socket=wayland`, `--socket=fallback-x11`, `--share=ipc` | Display. Wayland is used when available, X11 otherwise. `ipc` is needed for X11 shared memory. |
| `--share=network` | Model APIs, extension marketplace, Git remotes, update checks. |
| `--device=dri` | GPU access for hardware acceleration. |
| `--socket=pulseaudio`, `--filesystem=xdg-run/pipewire-0` | Audio, and PipeWire for screen capture. |
| `--filesystem=home` | Read and write access to your home directory, including dotfiles. Projects and tools live there. |
| `--socket=ssh-auth` | Forwards the host SSH agent for Git over SSH and remote development. |
| `--allow=devel` | Allows `ptrace` and `perf`, which debuggers such as gdb, lldb and strace need. |
| `--talk-name=org.freedesktop.Flatpak` | Lets the app run `flatpak-spawn --host`, which is how you get a host shell or call host tools. |
| `--talk-name=org.freedesktop.Notifications` | Desktop notifications. |
| `--talk-name=org.freedesktop.secrets`, `org.kde.kwalletd5`, `org.kde.kwalletd6` | Stores credentials in GNOME Keyring or KWallet. |
| `--talk-name=com.canonical.AppMenu.Registrar` (and `.*`) | Global menu bar on desktops that provide one. |
| `--system-talk-name=org.freedesktop.login1` | Electron's power monitor reads suspend, resume and shutdown events from logind. |
| `--env=XCURSOR_PATH=…` | Finds the host cursor theme. |
| `--env=ELECTRON_TRASH=gio` | Moves deleted files to the desktop trash. |

### What the sandbox does and does not protect

- `--filesystem=home` includes `~/.ssh`, `~/.gnupg`, browser profiles and everything else in `$HOME`. Antigravity's agents can read and change all of it.
- `org.freedesktop.Flatpak` permits `flatpak-spawn --host`, which runs any command outside the sandbox with your user's rights. This removes the isolation that the narrower `home` and `dri` settings would otherwise give. Those settings only limit what the app touches by accident, and they will not stop a command that goes through `flatpak-spawn --host`.
- Anything an agent runs in the integrated terminal has the same access as the app itself.
- `--socket=ssh-auth` lets the app use every key loaded in your SSH agent.

### Tightening

User overrides take precedence over the manifest. Examples:

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

If you remove `home`, the app no longer sees `~/.gitconfig`, `~/.ssh` or tools in `~/.local/bin` unless you add them back with `--filesystem`.

### Widening

The default grants stay narrow, so these are opt-in:

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

Without any of these, `flatpak-spawn --host docker ...` (or `podman`, `qemu`, `adb`) still works through the `org.freedesktop.Flatpak` permission.

## Known limitations

- Devices. With only `--device=dri`, the sandbox has no `/dev/kvm`, no USB (`/dev/bus/usb`) and no serial ports (`/dev/ttyUSB*`). Hardware flashing, `adb` over USB and hardware-accelerated emulators fail inside the sandbox. See [Widening](#widening).
- Paths outside home. `/mnt`, `/media`, `/run/media`, `/srv`, `/opt` and `/var/www` are not visible.
- Container sockets. The Docker and Podman sockets are not visible. Anything that talks to the daemon directly cannot reach it until you grant access.
- Hardcoded `/home/...` paths on Fedora Atomic and Silverblue. On those systems your home is `/var/home/<user>`, and `/home` is a symlink on the host. Inside the sandbox the symlink does not exist, so a path written as `/home/<user>/...` fails. Use `$HOME` or `~`.
- Host tools. Programs installed system-wide on the host are not on the sandbox `PATH`. Tools installed under your home (for example in `~/.local/bin`) work. For anything else use `flatpak-spawn --host <command>`.
- Built-in updater. Antigravity ships its own update mechanism. The app directory is read-only in Flatpak, and the behavior of that updater there has not been tested. Update through Flatpak and ignore any in-app update prompt.
- Architecture. Upstream publishes only x86_64 Linux builds, so there is no aarch64 package.
- No upstream checksums. Google does not publish checksums for the tarball. CI downloads the file and records its SHA256 in the manifest, so the hash pins the build to the bytes CI saw. It does not prove that those bytes match what Google intended to publish.

Verified from inside the sandbox with the default permissions: GPU acceleration (including NVIDIA device nodes), audio, screen recording through the patched `webm_encoder`, reading and writing under `$HOME`, `~/.gitconfig`, `~/.ssh`, and running tools from `~/.local/bin`.

## Configuration

To pass extra Chromium or Electron flags, create `~/.var/app/com.google.Antigravity/config/antigravity-flags.conf` with one flag per line. Blank lines and lines starting with `#` are ignored.

```text
# Example
--ozone-platform=x11
--enable-features=VaapiVideoDecoder
```

On Wayland the launcher adds `--ozone-platform-hint=auto` and the `WaylandWindowDecorations` feature. Any `--enable-features=` line in your file is merged with those, because Chromium only honors the last `--enable-features` flag.

The launcher sets `TMPDIR` to `~/.var/app/com.google.Antigravity/cache/tmp`.

## Verify the repository

The repository and its commits are signed with this key:

```text
AGY Flatpak Repo
67EC 8F65 529D BB99 F120  757B B3AF C4AE F302 7676
```

The public key is committed as [`pubkey.b64`](pubkey.b64) (base64) and embedded in the published `.flatpakrepo` and `.flatpakref` as `GPGKey=`. Flatpak refuses unsigned or wrongly signed content from the remote.

## Build locally

```bash
# Check upstream without changing anything
python3 scripts/update-checker.py --check

# Update the manifest and metainfo to the latest upstream version
python3 scripts/update-checker.py --update

# Build, export to ./repo and create a bundle (installs the runtimes if needed)
./scripts/build-local.sh
flatpak install --user --bundle com.google.Antigravity.flatpak
```

Pass `--force --update` to the checker to recompute the SHA256 of the current version.

How the pipeline, the signing and the `webm_encoder` patch work is described in [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md).

## License

The packaging files in this repository (manifest, scripts, workflows, web pages) are released under the [MIT License](LICENSE). Antigravity is proprietary software that belongs to Google LLC and is covered by its own terms. Antigravity and the Antigravity logo are Google trademarks.
