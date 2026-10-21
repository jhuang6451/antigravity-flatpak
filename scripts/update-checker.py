#!/usr/bin/env python3
"""
Antigravity Flatpak Automated Update Checker

Checks the upstream Google Antigravity release API for new versions,
computes the SHA256 checksum for the new tarball, updates the Flatpak manifest
(com.google.Antigravity.yaml) and AppStream metadata (com.google.Antigravity.metainfo.xml).
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

API_URL = "https://antigravity-hub-auto-updater-974169037036.us-central1.run.app/releases"
MANIFEST_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "com.google.Antigravity.yaml")
METAINFO_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "com.google.Antigravity.metainfo.xml")


def fetch_upstream_releases():
    """Fetch the list of releases from Google Antigravity auto-updater."""
    req = urllib.request.Request(
        API_URL,
        headers={"User-Agent": "Antigravity-Flatpak-Updater/1.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Failed to fetch releases: HTTP {resp.status}")
        return json.loads(resp.read().decode("utf-8"))


def parse_current_manifest():
    """Parse the current version, execution_id, and sha256 from the manifest."""
    if not os.path.exists(MANIFEST_PATH):
        raise FileNotFoundError(f"Manifest not found: {MANIFEST_PATH}")

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Match URL pattern: .../antigravity-hub/<version>-<execution_id>/linux-x64/Antigravity.tar.gz
    url_match = re.search(r"url:\s*https://storage\.googleapis\.com/antigravity-public/antigravity-hub/([^/-]+)-([^/]+)/linux-x64/Antigravity\.tar\.gz", content)
    sha_match = re.search(r"sha256:\s*([a-f0-9]{64})", content)

    if not url_match or not sha_match:
        raise ValueError("Could not parse current version or sha256 from manifest")

    return {
        "version": url_match.group(1),
        "execution_id": url_match.group(2),
        "sha256": sha_match.group(1),
        "url": url_match.group(0).replace("url:", "").strip(),
        "content": content
    }


def compute_sha256(url):
    """Download the artifact stream and compute its SHA256 checksum."""
    print(f"Downloading and calculating SHA256 for: {url}")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Antigravity-Flatpak-Updater/1.0"}
    )
    h = hashlib.sha256()
    total_bytes = 0
    with urllib.request.urlopen(req, timeout=120) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Failed to download tarball: HTTP {resp.status}")
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
            total_bytes += len(chunk)
            print(f"\r  Downloaded {total_bytes / (1024 * 1024):.1f} MB...", end="", flush=True)

    print("\n  Download complete.")
    return h.hexdigest()


def update_manifest(old_content, new_url, new_sha):
    """Replace URL and sha256 in manifest."""
    content = re.sub(
        r"url:\s*https://storage\.googleapis\.com/antigravity-public/antigravity-hub/[^/]+/linux-x64/Antigravity\.tar\.gz",
        f"url: {new_url}",
        old_content
    )
    content = re.sub(
        r"sha256:\s*[a-f0-9]{64}",
        f"sha256: {new_sha}",
        content
    )
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated manifest at {MANIFEST_PATH}")


def update_metainfo(new_version, release_date=None):
    """Add new release to com.google.Antigravity.metainfo.xml if not present."""
    if not os.path.exists(METAINFO_PATH):
        print(f"Metainfo file not found: {METAINFO_PATH}, skipping metainfo update.")
        return

    with open(METAINFO_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if f'release version="{new_version}"' in content:
        print(f"Metainfo already has release entry for version {new_version}")
        return

    if release_date is None:
        release_date = datetime.date.today().isoformat()

    new_release_tag = (
        f'    <release version="{new_version}" date="{release_date}">\n'
        f'      <description>\n'
        f'        <p>Upstream Antigravity IDE version {new_version}.</p>\n'
        f'      </description>\n'
        f'    </release>'
    )

    # Insert right after <releases>
    if "<releases>" in content:
        content = content.replace("<releases>", f"<releases>\n{new_release_tag}", 1)
        with open(METAINFO_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Added release {new_version} to {METAINFO_PATH}")


def set_github_output(outputs):
    """Write outputs to $GITHUB_OUTPUT file if in GitHub Actions."""
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output and os.path.exists(gh_output):
        with open(gh_output, "a", encoding="utf-8") as f:
            for k, v in outputs.items():
                f.write(f"{k}={v}\n")


def main():
    parser = argparse.ArgumentParser(description="Antigravity Flatpak update checker")
    parser.add_argument("--check", action="store_true", help="Only check for updates without modifying files")
    parser.add_argument("--update", action="store_true", help="Perform the update if new version found")
    parser.add_argument("--force", action="store_true", help="Force recalculation and update even if up to date")
    parser.add_argument("--ci", action="store_true", help="Output GitHub Actions step variables")

    args = parser.parse_args()

    print("Fetching upstream releases from Google API...")
    releases = fetch_upstream_releases()
    if not releases:
        print("No releases found from upstream API.")
        if args.ci:
            set_github_output({"updated": "false"})
        return 1

    latest = releases[0]
    latest_version = latest["version"]
    latest_exec_id = latest["execution_id"]
    print(f"Upstream latest release: version {latest_version} (execution_id: {latest_exec_id})")

    curr = parse_current_manifest()
    print(f"Current manifest release: version {curr['version']} (execution_id: {curr['execution_id']})")

    needs_update = (
        latest_version != curr["version"]
        or latest_exec_id != curr["execution_id"]
        or args.force
    )

    if not needs_update:
        print(f"Manifest is already up-to-date with latest release {latest_version}.")
        if args.ci:
            set_github_output({
                "updated": "false",
                "version": curr["version"],
                "execution_id": curr["execution_id"]
            })
        return 0

    new_url = f"https://storage.googleapis.com/antigravity-public/antigravity-hub/{latest_version}-{latest_exec_id}/linux-x64/Antigravity.tar.gz"
    print(f"Update available: {curr['version']} -> {latest_version}")
    print(f"Target URL: {new_url}")

    if args.check:
        print("Check mode only. Manifest not updated.")
        if args.ci:
            set_github_output({
                "updated": "true",
                "version": latest_version,
                "execution_id": latest_exec_id,
                "tar_url": new_url
            })
        return 0

    new_sha256 = compute_sha256(new_url)
    print(f"Computed SHA256: {new_sha256}")

    update_manifest(curr["content"], new_url, new_sha256)
    update_metainfo(latest_version)

    if args.ci:
        set_github_output({
            "updated": "true",
            "version": latest_version,
            "execution_id": latest_exec_id,
            "tar_url": new_url,
            "sha256": new_sha256
        })

    print("Successfully updated files for new release.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
