"""Builds the hub's generated files. Run by .github/workflows/hub.yml.

1. Lists every map in the "maps" GitHub Release (maps are uploaded there by hand; there is no copy in git).
2. Zips every folder mod (mods/<Id>.json with "folder": "mods/<Id>") and uploads it to the "mods" release.
3. Writes catalog.json - read by the launcher: maps, mod packages, the Edition and news.

Needs the `gh` CLI with GH_TOKEN set, and GITHUB_REPOSITORY ("owner/name").
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from clean_map_paks import allowed as map_file_allowed  # noqa: E402

REPO = os.environ["GITHUB_REPOSITORY"]
BRANCH = os.environ.get("HUB_BRANCH", "main")
MAPS_RELEASE = "maps"
MODS_DIR = "mods"
MODS_RELEASE = "mods"
EDITION_FILES_DIR = os.path.join("edition", "files")
EDITION_RELEASE = "edition"
MOD_VERSION_FILE = "version.txt"
CATALOG_SCHEMA = 2

# Fields copied from mods/<Id>.json into the catalog as they are.
MOD_FIELDS = ("exclude", "loadDll", "shared", "disable", "patch")


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


# ---------- releases ----------

def release_assets(tag, title, notes):
    """name -> asset JSON for a release, creating the release if needed."""
    try:
        data = json.loads(gh("api", f"repos/{REPO}/releases/tags/{tag}"))
    except subprocess.CalledProcessError:
        gh("release", "create", tag, "--target", BRANCH, "--title", title, "--notes", notes, capture=False)
        data = json.loads(gh("api", f"repos/{REPO}/releases/tags/{tag}"))

    assets = {}
    page = 1
    while True:
        batch = json.loads(gh("api", f"repos/{REPO}/releases/{data['id']}/assets?per_page=100&page={page}"))
        for a in batch:
            assets[a["name"]] = a
        if len(batch) < 100:
            return assets
        page += 1


def maps_assets():
    return release_assets(MAPS_RELEASE, "Maps",
                          "All IranCoJ maps. Managed by the hub workflow - see README.md.")


def mods_assets():
    return release_assets(MODS_RELEASE, "Mods",
                          "Mod packages for the launcher. Folder mods are zipped by the hub workflow; "
                          "other mods are uploaded here by hand - see README.md.")


def asset_sha256(asset):
    digest = asset.get("digest") or ""
    return digest.split(":", 1)[1] if digest.startswith("sha256:") else None


def asset_name(path):
    """The name GitHub gives an uploaded file: spaces become dots (e.g. "Clarendon Condensed_32.dds")."""
    return os.path.basename(path).replace(" ", ".")


def upload_if_changed(tag, path, assets):
    name = asset_name(path)
    if name in assets and asset_sha256(assets[name]) == sha256_of(path):
        return False
    print(f"upload {tag}/{name}")
    gh("release", "upload", tag, path, "--clobber", capture=False)
    return True


def package_entry(asset):
    return {"file": asset["name"], "size": asset["size"], "sha256": asset_sha256(asset),
            "url": asset["browser_download_url"]}


# ---------- maps ----------

def checked_maps():
    """sha256 of the maps the last catalog lists: those passed check_map_pak already."""
    try:
        with open("catalog.json", encoding="utf-8") as f:
            return {m["sha256"] for m in json.load(f).get("maps", [])}
    except (OSError, ValueError, KeyError):
        return set()


def check_map_pak(name, path):
    """A map pak may only carry Data/MapsNet/... and a map-named .scr at its root (tools/clean_map_paks.py removes
    the rest): the game reads every pak, so server config (ServerAdmins.scr), a player's out/ folder or copies of
    the game's own files in one map override them for everyone. A map that breaks this fails the build."""
    if not name.lower().endswith(".pak"):
        return
    with zipfile.ZipFile(path) as z:
        bad = [n for n in z.namelist() if not n.endswith("/") and not map_file_allowed(n)]
    if bad:
        sys.exit(f"maps release: {name} ships files a map must not ({', '.join(bad[:5])}"
                 f"{'...' if len(bad) > 5 else ''}) - clean it with python tools/clean_map_paks.py {name}, "
                 "then upload it to the maps release again")


def catalog_maps(assets):
    """Every map in the maps release; a new or changed one is downloaded and checked first."""
    checked = checked_maps()
    maps = []
    for name, a in sorted(assets.items(), key=lambda kv: kv[0].lower()):
        sha = asset_sha256(a)
        if not sha:
            print(f"warning: {name} has no digest yet, left out of the catalog", file=sys.stderr)
            continue
        if sha not in checked:
            with tempfile.TemporaryDirectory() as tmp:
                print(f"check {MAPS_RELEASE}/{name}")
                gh("release", "download", MAPS_RELEASE, "--pattern", name, "--dir", tmp, capture=False)
                check_map_pak(name, os.path.join(tmp, name))
        maps.append({"file": name, "size": a["size"], "sha256": sha, "url": a["browser_download_url"]})
    return maps


# ---------- mods ----------

def load_mod_manifests():
    if not os.path.isdir(MODS_DIR):
        return []
    mods = []
    for name in sorted(os.listdir(MODS_DIR), key=str.lower):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(MODS_DIR, name), encoding="utf-8-sig") as f:
            mod = json.load(f)
        if mod.get("id") != name[:-5]:
            sys.exit(f"{MODS_DIR}/{name}: \"id\" must match the file name")
        if bool(mod.get("folder")) == bool(mod.get("package")):
            sys.exit(f"{MODS_DIR}/{name}: set exactly one of \"folder\" or \"package\"")
        mods.append(mod)
    return mods


def folder_version(folder):
    path = os.path.join(folder, MOD_VERSION_FILE)
    if not os.path.isfile(path):
        sys.exit(f"{folder}: missing {MOD_VERSION_FILE}")
    with open(path, encoding="utf-8-sig") as f:
        return f.read().strip()


def zip_folder(folder, out_path):
    """Zips a mod folder reproducibly (sorted entries, fixed timestamps), so an unchanged
    folder always gives the same SHA-256 and is not uploaded again."""
    files = []
    for root, dirs, names in os.walk(folder):
        dirs.sort()
        for n in sorted(names):
            full = os.path.join(root, n)
            rel = os.path.relpath(full, folder).replace(os.sep, "/")
            if rel != MOD_VERSION_FILE:
                files.append((rel, full))
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel, full in sorted(files, key=lambda f: f[0].lower()):
            info = zipfile.ZipInfo(rel, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            with open(full, "rb") as f:
                z.writestr(info, f.read())


def check_patches(mod):
    """Each byte patch must match its file in the mod folder exactly once. After the mod is updated a patch can
    stop matching (the launcher then installs the file unpatched): redo it for the new build."""
    for patch in mod["patch"]:
        path = os.path.join(mod["folder"], patch["path"])
        find, replace = bytes.fromhex(patch["find"]), bytes.fromhex(patch["replace"])
        if len(find) != len(replace):
            sys.exit(f"mod {mod['id']}: patch for {patch['path']}: find and replace differ in length")
        if not os.path.isfile(path):
            sys.exit(f"mod {mod['id']}: patch for {patch['path']}: no such file in {mod['folder']}")
        with open(path, "rb") as f:
            count = f.read().count(find)
        if count != 1:
            sys.exit(f"mod {mod['id']}: patch for {patch['path']} ({patch.get('why', '')}) matches {count} times, "
                     "not once - the mod was probably updated; redo the patch for the new build")


def build_mods():
    manifests = load_mod_manifests()
    assets = mods_assets()
    changed = False

    with tempfile.TemporaryDirectory() as tmp:
        for mod in manifests:
            if mod.get("folder"):
                mod["version"] = mod.get("version") or folder_version(mod["folder"])
                if mod.get("patch"):
                    check_patches(mod)
                    # Installs carry the patches: a new set must reach players as an update.
                    mod["version"] += "+p" + hashlib.sha256(json.dumps(mod["patch"], sort_keys=True).encode()).hexdigest()[:8]
                mod["package"] = f"{mod['id']}-{mod['version']}.zip"
                path = os.path.join(tmp, mod["package"])
                zip_folder(mod["folder"], path)
                changed |= upload_if_changed(MODS_RELEASE, path, assets)

    if changed:
        assets = mods_assets()

    mods = []
    for mod in manifests:
        asset = assets.get(mod["package"])
        if not asset or not asset_sha256(asset):
            print(f"warning: mod {mod['id']}: {mod['package']} is not in the '{MODS_RELEASE}' release yet, "
                  "left out of the catalog", file=sys.stderr)
            continue
        entry = {"id": mod["id"], "name": mod.get("name", mod["id"]), "version": mod.get("version", ""),
                 "description": mod.get("description", ""), "package": package_entry(asset)}
        for field in MOD_FIELDS:
            entry[field] = mod.get(field, [])
        if "installer" in mod:
            entry["installer"] = mod["installer"]
        if mod.get("optional"):
            entry["optional"] = True

        # Per-platform overrides of any field above, e.g. a Windows-only installer package.
        platforms = {}
        for p in ("windows", "linux"):
            if p not in mod:
                continue
            override = dict(mod[p])
            if isinstance(override.get("package"), str):
                asset = assets.get(override["package"])
                if not asset or not asset_sha256(asset):
                    sys.exit(f"mod {mod['id']}: {p} package {override['package']} is not in the '{MODS_RELEASE}' release")
                override["package"] = package_entry(asset)
            platforms[p] = override
        if platforms:
            entry["platforms"] = platforms
        mods.append(entry)
    prune_old_packages(manifests, assets)
    return mods


def prune_old_packages(manifests, assets):
    """Only each mod's current package stays in the mods release: an older "<Id>-<version>.zip" of a mod that is
    still listed is deleted (the catalog never points at it again). Files of other names are left alone."""
    keep, ids = set(), []
    for mod in manifests:
        ids.append(mod["id"])
        keep.add(mod["package"])
        for p in ("windows", "linux"):
            if isinstance(mod.get(p, {}).get("package"), str):
                keep.add(mod[p]["package"])
    for name in sorted(assets):
        if name in keep or not name.lower().endswith(".zip"):
            continue
        owner = next((i for i in ids if name.startswith(i + "-") and name[len(i) + 1:len(i) + 2].isdigit()), None)
        if owner:
            print(f"delete {MODS_RELEASE}/{name} (older {owner})")
            gh("release", "delete-asset", MODS_RELEASE, name, "-y", capture=False)


# ---------- edition ----------

def edition_files():
    """edition/files/<path in the Edition> -> uploaded to the edition release, listed in the catalog."""
    if not os.path.isdir(EDITION_FILES_DIR):
        return []
    local = []
    for root, _, names in os.walk(EDITION_FILES_DIR):
        for name in names:
            path = os.path.join(root, name)
            local.append((os.path.relpath(path, EDITION_FILES_DIR).replace(os.sep, "/"), path))
    names = [asset_name(p) for _, p in local]
    dupes = {n for n in names if names.count(n) > 1}
    if dupes:
        sys.exit(f"edition/files: release asset names must be unique, duplicated: {sorted(dupes)}")

    assets = release_assets(EDITION_RELEASE, "Edition files",
                            "IranCoJ's own files for the Edition. Managed by the hub workflow - see README.md.")
    if any([upload_if_changed(EDITION_RELEASE, p, assets) for _, p in local]):
        assets = release_assets(EDITION_RELEASE, "", "")
    files = []
    for rel, path in sorted(local):
        a = assets[asset_name(path)]
        files.append({"path": rel, "size": a["size"], "sha256": asset_sha256(a) or sha256_of(path),
                      "url": a["browser_download_url"]})
    return files


def load_optional_json(path):
    """edition.json / news.json: copied into the catalog as they are (validated as JSON)."""
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def write_json(path, data):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    catalog = {"schema": CATALOG_SCHEMA,
               "maps": catalog_maps(maps_assets()),
               "mods": build_mods()}
    edition = load_optional_json("edition.json")
    if edition:
        # Everything but the human notes goes to the launcher (new keys must not need a script change).
        catalog["edition"] = {key: value for key, value in edition.items() if key != "notes"}
        catalog["edition"]["files"] = edition_files()
    news = load_optional_json("news.json")
    if news:
        catalog["news"] = news
    write_json("catalog.json", catalog)
