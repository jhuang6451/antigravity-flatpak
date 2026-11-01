# Project context

Notes for maintainers. User-facing documentation is in [README.md](README.md).

## Upstream distribution

Google does not publish Antigravity through a package repository. The Linux build is a tarball on a public storage bucket, and a small auto-updater service lists releases as JSON.

- Release list: `https://antigravity-hub-auto-updater-974169037036.us-central1.run.app/releases`. Each entry has a `version` and an `execution_id`.
- Tarball: `https://storage.googleapis.com/antigravity-public/antigravity-hub/<version>-<execution_id>/linux-x64/Antigravity.tar.gz`, with the application in a single top-level directory (`strip-components: 1`).
- Only linux-x64 is published, so the manifest uses `only-arches: [x86_64]`.
- No checksums or signatures are published. `scripts/update-checker.py` downloads the tarball, computes the SHA256 and writes it into the manifest. The first download is trusted.
- The release list is not guaranteed to be ordered. The checker picks the entry with the highest numeric version.
- The tarball's `Last-Modified` header is used as the release date in the AppStream metadata. If it is missing, the current date is used.

## Manifest

`com.google.Antigravity.yaml` builds with `buildsystem: simple`. It copies the tarball contents to `/app/antigravity`, installs `antigravity.sh` as `/app/bin/antigravity`, and installs the desktop file, metainfo and icons.

Base and runtime: `org.freedesktop.Platform//25.08` with `org.electronjs.Electron2.BaseApp//25.08`. The base app provides `zypak-wrapper`.

### zypak

Chromium's setuid `chrome-sandbox` cannot work in an unprivileged Flatpak. `zypak-wrapper` routes Chromium's sandbox through Flatpak's sandbox instead. The launcher runs `exec zypak-wrapper /app/antigravity/antigravity ...`, and the build deletes `chrome-sandbox` because it is unused.

### webm_encoder patch

`resources/bin/webm_encoder` is an ELF binary whose interpreter path points at Google's internal toolchain: `/usr/grte/v5/lib64/ld-linux-x86-64.so.2`. That path does not exist on ordinary systems, so the encoder fails to start with `No such file or directory` and screen recording does not work.

The build replaces the interpreter string in place with `/lib64/ld-linux-x86-64.so.2`, padded with NUL bytes to the original length so no offsets in the file move. If a future upstream version changes or removes the string, the build prints a warning and continues. Check the build log after each upstream update.

### Launcher

`antigravity.sh` runs with `set -euo pipefail`.

- Wayland is detected from `WAYLAND_DISPLAY` or `XDG_SESSION_TYPE`. It then adds `--ozone-platform-hint=auto` and the `WaylandWindowDecorations` feature.
- Extra flags are read from `$XDG_CONFIG_HOME/antigravity-flags.conf`. Inside the sandbox that directory is `~/.var/app/com.google.Antigravity/config`. All `--enable-features=` values are merged into one flag.
- `TMPDIR` is `$XDG_CACHE_HOME/tmp`.

### Sandbox permissions

The permission list and its reasoning are in the README. The decision record:

- `--filesystem=host` and `--device=all` were replaced with `--filesystem=home` and `--device=dri`. The narrower set was tested by running Antigravity inside the sandbox. GPU (including NVIDIA), audio, the `webm_encoder` patch, `$HOME` access, `~/.ssh`, `~/.gitconfig` and `~/.local/bin` tools worked. KVM, USB, serial, `/mnt`, `/media`, `/run/media`, `/srv`, `/opt`, `/var/www` and the Docker and Podman sockets did not. These are documented as opt-in overrides.
- `org.freedesktop.Flatpak` stays. It is what makes `flatpak-spawn --host` possible, so the sandbox is not a hard boundary, and the README says so.
- `--allow=devel` and `--system-talk-name=org.freedesktop.login1` are kept and not yet tested for removal.

## CI

Two workflows in `.github/workflows/`.

`check-update.yml` runs every 6 hours and on demand.

1. Runs `scripts/update-checker.py --ci --update`.
2. If a new version exists, commits the manifest and metainfo to `master`.
3. Starts `build-and-deploy.yml` with `gh workflow run`. A push made with `GITHUB_TOKEN` does not trigger other workflows, which is why the explicit dispatch is needed. The workflow needs `actions: write` for that.

`build-and-deploy.yml` runs on pushes to the files that affect the package or the site, and on demand. A concurrency group serializes runs.

1. Build job, in the `flatpak-github-actions:freedesktop-25.08` container with `--privileged`. It extracts the version from the manifest URL and fails if it cannot, installs the runtimes from Flathub, runs `flatpak-builder` for an OSTree repo and a bundle, then runs `scripts/sign-repo.sh`.
2. Deploy job. It unpacks the repo into `deploy/repo`, copies `web/`, takes copies of the `.flatpakrepo` and `.flatpakref`, removes `gpg-verify=` from them and appends `GPGKey=<base64 public key>`, uploads the result as a Pages artifact, and deploys it. It then deletes any existing release with the same tag and creates a new one, so re-packaging the same upstream version moves the tag.

Release assets: `com.google.Antigravity.flatpak`, `ostree-repo.tar.gz`, `antigravity.flatpakref`, `antigravity.flatpakrepo`.

The repository settings must have Pages source set to GitHub Actions. The old `gh-pages` branch is no longer used.

### The repository is rebuilt from scratch

Each run starts with an empty repo, so there is no earlier commit to diff against. Static deltas and `--prune` would have no effect and are not used. Clients still download only objects they do not already have.

### Signing

`scripts/sign-repo.sh` imports `GPG_PRIVATE_KEY` into a temporary keyring, signs the commit with `flatpak build-sign`, regenerates the summary with `flatpak build-update-repo --gpg-sign`, and writes the base64 public key to `gpg-public.b64`. If the secret is missing, it exits without signing and the deploy leaves `gpg-verify=false` in place.

- Secret: `GPG_PRIVATE_KEY` (armored private key, no passphrase).
- Key: `67EC 8F65 529D BB99 F120 757B B3AF C4AE F302 7676`. The public key is in `pubkey.b64`.
- The files in git keep `gpg-verify=false`. Only the deployed copies carry the key.

## Local tooling

- `scripts/update-checker.py`: `--check` (read only), `--update`, `--force`, `--ci` (writes step outputs).
- `scripts/build-local.sh`: builds with `--default-branch=stable`, exports to `./repo`, and creates a bundle with `--runtime-repo` pointing at Flathub.

## Repository layout

```text
.github/workflows/    check-update.yml, build-and-deploy.yml
icons/hicolor/        icon set, 16 to 512 px
scripts/              update-checker.py, build-local.sh, sign-repo.sh
web/                  GitHub Pages site (index.html, zh-CN.html, style.css, app.js)
antigravity.sh        launcher
antigravity.flatpakref, antigravity.flatpakrepo   templates, patched in CI
com.google.Antigravity.yaml, .desktop, .metainfo.xml, .png
pubkey.b64            repository signing key (public)
TODO.md               open items
```

## Open items

See [TODO.md](TODO.md). The remaining one is testing Antigravity's built-in updater inside the read-only `/app` and disabling it if it misbehaves.
