"""Sets the Edition's version everywhere it shows: edition.json, the main menu's corner text and the credits.

    python tools/edition_version.py 0.7.1

The main menu shows the text "IrnEditionVersion" (a string the Edition adds to the game's compiled texts,
COJ2 Voices&Texts.bin, next to New Classes' strings), so a new version needs no menu pack compile.
Then rebuild the credits: python tools/edition_credits.py
"""

import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "..", "edition.json")
BASE_COUNT = 8327  # strings in the game's own COJ2 Voices&Texts.bin
KEY = "IrnEditionVersion"


def entry(key, text):
    return (struct.pack("<H", len(key)) + key.encode("latin1") + struct.pack("<H", len(text)) + text.encode("utf-16-le")).decode("latin1")


def parse_entries(blob):
    out, i = [], 0
    while i < len(blob):
        kl = struct.unpack_from("<H", blob, i)[0]; i += 2
        k = blob[i:i + kl].decode("latin1"); i += kl
        n = struct.unpack_from("<H", blob, i)[0]; i += 2
        out.append((k, blob[i:i + 2 * n].decode("utf-16-le"))); i += 2 * n
    return out


def main(version):
    e = json.load(open(SPEC, encoding="utf-8"))
    e["version"] = version
    texts = next(r for r in e["rewrite"] if r["path"].endswith("Voices&Texts.bin"))
    tail = next(x for x in texts["replace"] if x[0] == "\\z")
    added = [(k, v) for k, v in parse_entries(tail[1].encode("latin1")) if k != KEY] + [(KEY, f"IranCoJ Edition {version}")]
    tail[1] = "".join(entry(k, v) for k, v in added)
    count = next(x for x in texts["replace"] if x[0].startswith("\\A"))
    count[1] = "\x01\x00\x00\x00" + struct.pack("<I", BASE_COUNT + len(added)).decode("latin1")
    open(SPEC, "w", encoding="utf-8").write(json.dumps(e, indent=2, ensure_ascii=False) + "\n")
    print(f"version {version}; {len(added)} strings added to the game's texts")


if __name__ == "__main__":
    if len(sys.argv) != 2 or not re.fullmatch(r"\d+\.\d+(\.\d+)?", sys.argv[1]):
        raise SystemExit("usage: python tools/edition_version.py <version, e.g. 0.7.1>")
    main(sys.argv[1])
