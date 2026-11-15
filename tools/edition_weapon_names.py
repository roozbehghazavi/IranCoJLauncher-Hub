"""Gives the guns their real names in the Edition's texts (class screen, weapon wheel, pick-up and switch notices).

    python tools/edition_weapon_names.py [path to the game's DataEn.pak]

The Edition builds its COJ2 Voices&Texts.bin from the player's own DataEn.pak by the rules in edition.json (that
file's "rewrite"). This adds one exact replace rule per weapon string - every variant: plain, Prime, Superb, Rusty,
the upgraded "+" guns and the multiplayer ...Net keys - swapping only the gun's old name for its real one, so the
quality word in front and the "+" stay. The strings are entries of <u16 key length><key><u16 text length><UTF-16
text>; a rule matches a whole entry (both lengths included), so it can only ever hit that one string. Keys the
Edition already rewrites (New Classes reuses some upgrade keys for its own weapons: the throwing knife, tomahawk,
Springfield musket) are left alone. Running it again replaces its own rules.

Then bump the Edition (tools/edition_version.py, tools/edition_credits.py) so players' Editions rebuild the texts.
"""

import json
import os
import struct
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "..", "edition.json")
ENTRY = "Data/COJ2 Voices&Texts.bin"
DEFAULT_PAK = r"C:\Games\IranCoJ Edition\CoJ2\DataEn.pak"

# the weapon's script name (after "N_" / "Name_") -> (the game's name, the real gun: the model, per IMFDB's
# Call of Juarez: Bound in Blood page). Names of models the optional IranCoJ Guns mod swaps in are its own rewrite.
NAMES = {
    "WeaponPistolWalker": ("Ranger", "Colt Walker 1847"),
    "WeaponPistolPeacemaker": ("Classic Gun", "Remington 1890"),
    "WeaponPistolSchofield": ("Quickshooter", "Schofield Model 3"),
    "WeaponPistolCogswell": ("Peppergun", "Lefaucheux Pepperbox"),
    "WeaponPistolDerringer": ("Ladies Gun", "Remington 1866 Derringer"),
    "WeaponPistolLemant": ("Hybrid Gun", "LeMat 1869 Revolver"),
    "WeaponPistolVolcanic": ("Volcano Gun", "Volcanic Pistol"),
    "WeaponPistolFrontier": ("Border Gun", "Colt Model 1878"),
    "WeaponRifleWinchester": ("Classic Rifle", "Winchester 1892"),   # "Repeater" made it wrap on the class screen
    "WeaponRifleWinchesterScope": ("Classic Scoped", "Winchester 1892 Scoped"),
    "WeaponRifleSharps": ("Heavy Rifle", "Sharps 1874"),
    "WeaponRifleSharpsScope": ("Heavy Scoped", "Sharps 1874 Scoped"),
    "WeaponRifleRemington": ("Shotgun", "Remington 1889 Shotgun"),
    "WeaponRifleRemingtonSawOff": ("Sawed-Off", "Remington 1889 Sawed-Off"),
    "WeaponGatling": ("Gatling", "Gatling Gun"),
    # the bow keeps its name
}
SUFFIXES = {"", "Net", "Alpha", "Beta", "Rusty", "Indian", "AlphaNet", "BetaNet", "Upgrade", "UpgradeNet"}
# New Classes' own weapons in the guns' upgrade slots (the Edition names them in its tail: Springfield musket,
# throwing knife, tomahawk): never given a gun's name
SKIP = {"WeaponPistolFrontierUpgrade", "WeaponPistolFrontierUpgradeNet", "WeaponPistolDerringerUpgrade",
        "WeaponPistolDerringerUpgradeNet", "WeaponPistolLemantUpgrade", "WeaponPistolLemantUpgradeNet"}


def parse(blob):
    """(key, text, start, end) of every entry after the 8-byte header."""
    out, i = [], 8
    while i < len(blob):
        start = i
        kl = struct.unpack_from("<H", blob, i)[0]; i += 2
        key = blob[i:i + kl].decode("latin1"); i += kl
        n = struct.unpack_from("<H", blob, i)[0]; i += 2
        text = blob[i:i + 2 * n].decode("utf-16-le"); i += 2 * n
        out.append((key, text, start, i))
    return out


def entry(key, text):
    return struct.pack("<H", len(key)) + key.encode("latin1") + struct.pack("<H", len(text)) + text.encode("utf-16-le")


def pattern(raw):
    """A .NET regex matching exactly these bytes (read as Latin-1, as the launcher does)."""
    return "".join(chr(b) if chr(b).isalnum() and b < 128 else "\\x%02x" % b for b in raw)


def weapon_of(key):
    for prefix in ("N_", "Name_"):
        if key.startswith(prefix):
            rest = key[len(prefix):]
            if rest in SKIP:
                return None
            # the longest name that fits (WeaponRifleWinchesterScope before WeaponRifleWinchester)
            for base in sorted(NAMES, key=len, reverse=True):
                if rest.startswith(base) and rest[len(base):] in SUFFIXES:
                    return base
    return None


def main(pak):
    blob = zipfile.ZipFile(pak).read(ENTRY)
    e = json.load(open(SPEC, encoding="utf-8"))
    rule = next(r for r in e["rewrite"] if r["path"].endswith("Voices&Texts.bin"))

    entries = parse(blob)
    ours = {}
    for key, text, start, end in entries:
        base = weapon_of(key)
        if not base:
            continue
        old, new = NAMES[base]
        if old not in text:
            continue
        # .NET Regex.Replace (the launcher) reads "$" in a replacement as a substitution: a length byte can be 0x24
        ours[pattern(blob[start:end])] = (key, entry(key, text.replace(old, new)).decode("latin1").replace("$", "$$"))

    # keys other rules already rewrite (or the tail adds) stay as they are
    kept = [r for r in rule["replace"] if r[0] not in ours]   # our own rules from an earlier run go
    others = " ".join(r[0] for r in kept if r[0] != "\\z")
    tail = next((r[1] for r in kept if r[0] == "\\z"), "")
    added = []
    for pat, (key, rep) in ours.items():
        kl = struct.pack("<H", len(key)).decode("latin1")
        if key + "\\x" in others or (kl + key) in tail:   # an Edition rule already on this string, or the tail adds it
            print("  kept as the Edition has it:", key)
            continue
        added.append([pat, rep])
    # before the header count and the tail (those must stay last)
    at = next(i for i, r in enumerate(kept) if r[0].startswith("\\A") or r[0] == "\\z")
    rule["replace"] = kept[:at] + added + kept[at:]
    open(SPEC, "w", encoding="utf-8").write(json.dumps(e, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(added)} weapon strings renamed")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PAK)
