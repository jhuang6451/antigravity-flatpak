#!/usr/bin/env bash
# Sign the OSTree commit and summary of a Flatpak repo with a GPG key.
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

flatpak build-sign --gpg-sign="$KEY_ID" --gpg-homedir="$GNUPGHOME" "$REPO" "$APP_ID" "$BRANCH"
flatpak build-update-repo --gpg-sign="$KEY_ID" --gpg-homedir="$GNUPGHOME" "$REPO"

gpg --batch --export "$KEY_ID" | base64 -w0 > "$(dirname "$REPO")/gpg-public.b64"
echo "Repository signed with key $KEY_ID."
