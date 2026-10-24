"""Builds the hub's generated files. Run by .github/workflows/hub.yml.

1. Mirrors every map in MapsNet/ to the "maps" GitHub Release (uploads new or changed ones).
2. Writes catalog.json  - read by launcher v3: maps from the release, mods from this repo.
3. Writes manifest.json - read by launcher v2.0.1 (legacy): maps stored in git only.

Needs the `gh` CLI with GH_TOKEN set, and GITHUB_REPOSITORY ("owner/name").
"""
import hashlib
import json
import os
import subprocess
import sys

REPO = os.environ["GITHUB_REPOSITORY"]
BRANCH = os.environ.get("HUB_BRANCH", "main")
MAPS_DIR = "MapsNet"
MAPS_RELEASE = "maps"
MOD_VERSION_FILE = "version.txt"
LFS_PREFIX = b"version https://git-lfs.github.com/spec/v1"


def gh(*args, capture=True):
    result = subprocess.run(["gh", *args], check=True, text=True,
                            stdout=subprocess.PIPE if capture else None)
    return result.stdout if capture else None


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def is_lfs_pointer(path):
    with open(path, "rb") as f:
        return f.read(len(LFS_PREFIX)) == LFS_PREFIX


def lfs_tracked_files():
    try:
        out = subprocess.run(["git", "lfs", "ls-files", "-n"], check=True, text=True,
                             stdout=subprocess.PIPE).stdout
        return {os.path.normpath(p) for p in out.splitlines() if p.strip()}
    except (OSError, subprocess.CalledProcessError):
        return set()


def release_assets():
    """name -> asset JSON for the maps release, creating the release if needed."""
    try:
        data = json.loads(gh("api", f"repos/{REPO}/releases/tags/{MAPS_RELEASE}"))
    except subprocess.CalledProcessError:
        gh("release", "create", MAPS_RELEASE, "--target", BRANCH, "--title", "Maps",
           "--notes", "All IranCoJ maps. Managed by the hub workflow - see README.md.",
           capture=False)
        data = json.loads(gh("api", f"repos/{REPO}/releases/tags/{MAPS_RELEASE}"))

    assets = {}
    page = 1
    while True:
        batch = json.loads(gh("api", f"repos/{REPO}/releases/{data['id']}/assets?per_page=100&page={page}"))
        for a in batch:
            assets[a["name"]] = a
        if len(batch) < 100:
            return assets
        page += 1


def asset_sha256(asset):
    digest = asset.get("digest") or ""
    return digest.split(":", 1)[1] if digest.startswith("sha256:") else None


def git_map_files():
    if not os.path.isdir(MAPS_DIR):
        return []
    return sorted(n for n in os.listdir(MAPS_DIR) if os.path.isfile(os.path.join(MAPS_DIR, n)))


def sync_maps_to_release():
    assets = release_assets()
    for name in git_map_files():
        path = os.path.join(MAPS_DIR, name)
        if is_lfs_pointer(path):
            print(f"skip {name}: LFS pointer (checkout without LFS content)")
            continue
        local = sha256_of(path)
        if name in assets and asset_sha256(assets[name]) == local:
            continue
        print(f"upload {name}")
        gh("release", "upload", MAPS_RELEASE, path, "--clobber", capture=False)
    return release_assets()


def build_catalog(assets):
    maps = []
    for name, a in sorted(assets.items(), key=lambda kv: kv[0].lower()):
        sha = asset_sha256(a)
        if not sha:
            print(f"warning: {name} has no digest yet, left out of the catalog", file=sys.stderr)
            continue
        maps.append({"file": name, "size": a["size"], "sha256": sha,
                     "url": a["browser_download_url"]})

    mods = []
    for folder in sorted(os.listdir("."), key=str.lower):
        version_path = os.path.join(folder, MOD_VERSION_FILE)
        if folder.startswith(".") or not os.path.isfile(version_path):
            continue
        with open(version_path, encoding="utf-8-sig") as f:
            version = f.read().strip()
        files = []
        for root, _, names in os.walk(folder):
            for n in names:
                full = os.path.join(root, n)
                rel = os.path.relpath(full, folder).replace(os.sep, "/")
                if rel == MOD_VERSION_FILE:
                    continue
                files.append({"path": rel, "size": os.path.getsize(full), "sha256": sha256_of(full)})
        files.sort(key=lambda f: f["path"].lower())
        mods.append({"id": folder, "version": version, "type": "copy",
                     "baseUrl": f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{folder}/",
                     "files": files})

    return {"schema": 1, "maps": maps, "mods": mods}


def build_legacy_manifest():
    # v2.0.1 downloads from raw.githubusercontent.com, which only serves files stored in
    # git itself. LFS files would arrive as pointer text, so they are left out.
    lfs = lfs_tracked_files()
    manifest = {}
    for name in git_map_files():
        path = os.path.join(MAPS_DIR, name)
        if os.path.normpath(path) in lfs or is_lfs_pointer(path):
            continue
        manifest[name] = sha256_of(path)
    return manifest


def write_json(path, data):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    assets = sync_maps_to_release()
    write_json("catalog.json", build_catalog(assets))
    write_json("manifest.json", build_legacy_manifest())
