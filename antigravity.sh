#!/bin/bash
set -euo pipefail

FLAGS=()
FEATURES=()

# Wayland auto-detection
if [ -n "${WAYLAND_DISPLAY:-}" ] || [ "${XDG_SESSION_TYPE:-}" = "wayland" ]; then
    FLAGS+=(--ozone-platform-hint=auto)
    FEATURES+=(WaylandWindowDecorations)
fi

# Allow user custom flags via ~/.config/antigravity-flags.conf
# Chromium only honours the last --enable-features, so merge them into one.
CONFIG_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/antigravity-flags.conf"
if [ -f "$CONFIG_FILE" ]; then
    while IFS= read -r line; do
        case "$line" in
            --enable-features=*) FEATURES+=("${line#--enable-features=}") ;;
            *) FLAGS+=("$line") ;;
        esac
    done < <(grep -Ev '^\s*$|^\s*#' "$CONFIG_FILE" || true)
fi

if [ "${#FEATURES[@]}" -gt 0 ]; then
    FEATURES_JOINED=$(IFS=,; echo "${FEATURES[*]}")
    FLAGS+=("--enable-features=${FEATURES_JOINED}")
fi

# Temporary directory inside the app cache
export TMPDIR="${XDG_CACHE_HOME:-$HOME/.cache}/tmp"
mkdir -p "$TMPDIR"

# Execute using zypak-wrapper (from org.electronjs.Electron2.BaseApp)
exec zypak-wrapper /app/antigravity/antigravity "${FLAGS[@]}" "$@"
