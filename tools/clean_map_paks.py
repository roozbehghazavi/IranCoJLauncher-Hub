"""Removes what a map pak should not ship, keeping every other entry byte for byte (compressed data copied as is).

    python tools/clean_map_paks.py [pak ...]      (default: every pak in MapsNet)

A map pak may carry Data/MapsNet/... and a map-named .scr at its root (e.g. "Red Hideout.scr": water and fog).
Everything else goes: server config (ServerAdmins.scr - the game reads it from any pak, so a list in one map made
its accounts admins on every server with that map), player profiles (out/), editor leftovers
(FightNodesGenDefaults.scr, Data/Wizard/...) and copies of the game's own files (the map editor exports
Data/Characters and Data/Creatures skins with variants commented out, which overrode the game's for everyone).
build_hub.py fails the build on a pak that breaks this rule (check_map_pak).
"""

import os
import struct
import sys
import zipfile

MAPS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "MapsNet")
NOT_MAP_FILES = ("serveradmins.scr", "fightnodesgendefaults.scr")


def allowed(name):
    path = name.replace("\\", "/").lower()
    if path.startswith("data/mapsnet/"):
        return True
    return "/" not in path and path.endswith(".scr") and path not in NOT_MAP_FILES


def clean(path):
    """Rewrites the pak without the entries allowed() rejects; returns the names removed."""
    with zipfile.ZipFile(path) as source:
        infos = source.infolist()
    drop = [i.filename for i in infos if not i.filename.endswith("/") and not allowed(i.filename)]
    if not drop:
        return []

    temp = path + ".new"
    with open(path, "rb") as raw, zipfile.ZipFile(temp, "w") as target:
        for info in infos:
            if info.filename in drop:
                continue
            # Local header + compressed data (+ data descriptor), copied unchanged.
            raw.seek(info.header_offset)
            header = raw.read(30)
            name_len, extra_len = struct.unpack("<HH", header[26:30])
            size = 30 + name_len + extra_len + info.compress_size
            if info.flag_bits & 0x08:
                raw.seek(info.header_offset + size)
                size += 16 if raw.read(4) == b"PK\x07\x08" else 12
            raw.seek(info.header_offset)
            copy = zipfile.ZipInfo(info.filename, info.date_time)
            for field in ("compress_type", "flag_bits", "CRC", "compress_size", "file_size", "external_attr",
                          "internal_attr", "create_system", "create_version", "extract_version", "extra", "comment"):
                setattr(copy, field, getattr(info, field))
            copy.header_offset = target.fp.tell()
            target.fp.write(raw.read(size))
            target.filelist.append(copy)
            target.NameToInfo[copy.filename] = copy
        target.start_dir = target.fp.tell()

    with zipfile.ZipFile(path) as before, zipfile.ZipFile(temp) as after:
        kept = [n for n in before.namelist() if n not in drop]
        if after.namelist() != kept or any(before.read(n) != after.read(n) for n in kept):
            os.remove(temp)
            raise SystemExit(f"{path}: the cleaned copy differs - left as it was")
    os.replace(temp, path)
    return drop


if __name__ == "__main__":
    paks = sys.argv[1:] or sorted(os.path.join(MAPS_DIR, n) for n in os.listdir(MAPS_DIR) if n.lower().endswith(".pak"))
    for pak in paks:
        before = os.path.getsize(pak)
        removed = clean(pak)
        if removed:
            print(f"{os.path.basename(pak)}: removed {len(removed)} ({before - os.path.getsize(pak):,} bytes smaller)")
