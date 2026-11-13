#!/usr/bin/env bash
# Sign all OSTree commits (app and appstream branches) and summary of a Flatpak repo with a GPG key.
#
# Usage: GPG_PRIVATE_KEY=<armored key> scripts/sign-repo.sh <repo-dir> <app-id> <branch>
#
# If GPG_PRIVATE_KEY is empty the script does nothing (unsigned repo).
# On success it writes the base64 public key to <repo-dir>/../gpg-public.b64
# so that the deploy job can embed it into .flatpakrepo / .flatpakref.
set -euo pipefail

REPO="${1:?repo dir}"
APP_ID="${2:?app id}"
BRANCH="${3:?branch}"

if [ -z "${GPG_PRIVATE_KEY:-}" ]; then
  echo "GPG_PRIVATE_KEY not set; leaving repository unsigned."
  exit 0
fi

GNUPGHOME="$(mktemp -d)"
export GNUPGHOME
chmod 700 "$GNUPGHOME"
trap 'rm -rf "$GNUPGHOME"' EXIT

printf '%s\n' "$GPG_PRIVATE_KEY" | gpg --batch --import
KEY_ID="$(gpg --batch --list-secret-keys --with-colons | awk -F: '/^sec/{print $5; exit}')"
[ -n "$KEY_ID" ] || { echo "No secret key found after import" >&2; exit 1; }

has_gpg_sig() {
  ostree --repo="$REPO" show --list-detached-metadata-keys "$1" 2>/dev/null | grep -qx 'ostree\.gpgsigs'
}

flatpak build-sign --gpg-sign="$KEY_ID" --gpg-homedir="$GNUPGHOME" "$REPO" "$APP_ID" "$BRANCH"

# flatpak-builder exports unsigned appstream/appstream2 commits beforehand, and
# flatpak build-update-repo skips committing when the tree is unchanged. Sign
# any remaining unsigned refs (notably appstream/* and appstream2/*) directly.
while IFS= read -r ref; do
  [ -n "$ref" ] || continue
  if ! has_gpg_sig "$ref"; then
    ostree gpg-sign --repo="$REPO" --gpg-homedir="$GNUPGHOME" "$ref" "$KEY_ID"
  fi
done < <(ostree refs --repo="$REPO")

flatpak build-update-repo --gpg-sign="$KEY_ID" --gpg-homedir="$GNUPGHOME" "$REPO"

while IFS= read -r ref; do
  [ -n "$ref" ] || continue
  if ! has_gpg_sig "$ref"; then
    echo "Error: ref '$ref' is still unsigned after signing." >&2
    exit 1
  fi
done < <(ostree refs --repo="$REPO")

gpg --batch --export "$KEY_ID" | base64 -w0 > "$(dirname "$REPO")/gpg-public.b64"
echo "Repository signed with key $KEY_ID."
