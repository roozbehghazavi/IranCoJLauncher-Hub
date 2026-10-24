"""The Edition's menu font: Oswald (SIL Open Font License, tools/fonts/OFL.txt) in place of Clarendon Condensed.

The game draws text from a pre-rendered atlas (white glyphs, coverage in alpha; it adds outlines itself) and a
text metrics file listing Char(code, advance, x0, y0, x1, y1). Loose files in CoJ2/Data/Panel override the
paks, so writing both under Clarendon's name changes every text that uses it, menus and in game alike.

    python tools/edition_font.py <game>/CoJ2/Data0.pak tools/fonts/Oswald.ttf <out: edition/files/CoJ2/Data/Panel>

The character list is read from the player's own Data0.pak so the same codes stay covered.
"""

import os
import re
import sys
import zipfile

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edition_menu_art import write_dds  # noqa: E402

NAME = "Clarendon Condensed_32"
MAP_W, MAP_H, CELL = 1024, 512, 52
BASELINE, CAP_HEIGHT = 41, 30  # where Clarendon sits in its 52 px cell
ICON_ROW = 408  # icon glyphs live below this row
WEIGHT = 500


def font_for_cap_height(path):
    probe = ImageFont.truetype(path, 100)
    probe.set_variation_by_axes([WEIGHT])
    top, bottom = probe.getbbox("H", anchor="ls")[1], probe.getbbox("H", anchor="ls")[3]
    size = round(100 * CAP_HEIGHT / (bottom - top))
    f = ImageFont.truetype(path, size)
    f.set_variation_by_axes([WEIGHT])
    return f


def arrow(draw, box, direction):
    x0, y0, x1, y1 = box
    cx, cy, r = (x0 + x1) / 2, (y0 + y1) / 2, 11
    shapes = {
        "left": [(cx - r, cy), (cx + r * 0.6, cy - r), (cx + r * 0.6, cy + r)],
        "right": [(cx + r, cy), (cx - r * 0.6, cy - r), (cx - r * 0.6, cy + r)],
        "up": [(cx, cy - r), (cx - r, cy + r * 0.6), (cx + r, cy + r * 0.6)],
        "down": [(cx, cy + r), (cx - r, cy - r * 0.6), (cx + r, cy - r * 0.6)],
    }
    for d in direction:
        pts = shapes[d]
        if len(direction) == 2:  # two arrows side by side / stacked
            dx, dy = {"left": (-9, 0), "right": (9, 0), "up": (0, -9), "down": (0, 9)}[d]
            pts = [(x + dx, y + dy) for x, y in pts]
        draw.polygon(pts, fill=(255, 255, 255, 255))


def main(pak, ttf, out):
    original = zipfile.ZipFile(pak).read(f"Data/Panel/{NAME}.fm").decode("latin1")
    codes = [int(c) for c in re.findall(r"^Char\((\d+),", original, re.M)]
    specials = [(int(c), int(adv), tuple(map(int, box)), note.strip())
                for c, adv, *box, note in re.findall(
                    r"^SpecialChar\((\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)\s*//\s*(.*)$", original, re.M)]

    font = font_for_cap_height(ttf)
    atlas = Image.new("RGBA", (MAP_W, MAP_H), (255, 255, 255, 0))
    draw = ImageDraw.Draw(atlas)
    lines = [f'Name("Clarendon Condensed")', "", f"MapWidth({MAP_W})", f"MapHeight({MAP_H})", f"FontHeight({CELL})", "",
             "// IranCoJ Edition: Oswald (SIL Open Font License)", ""]

    x = y = 0
    for code in codes:
        ch = chr(code)
        if code == 255 or not ch.isprintable() and code != 32:
            lines.append(f"Char({code}, 0, 0, 0, 0, 0)")
            continue
        advance = max(1, round(font.getlength(ch))) + 2
        if x + advance > MAP_W:
            x, y = 0, y + CELL + 1
            if y + CELL > ICON_ROW:
                raise SystemExit("atlas full")
        draw.text((x + 1, y + BASELINE), ch, font=font, anchor="ls", fill=(255, 255, 255, 255))
        lines.append(f"Char({code}, {advance}, {x}, {y}, {x + advance}, {y + CELL})")
        x += advance + 1

    arrows = {"[ArrowLeftRight]": "lr", "[ArrowUpDown]": "ud", "[ArrowDown]": "d", "[ArrowUp]": "u",
              "[ArrowLeft]": "l", "[ArrowRight]": "r"}
    names = {"l": "left", "r": "right", "u": "up", "d": "down"}
    lines.append("")
    for code, adv, box, note in specials:
        if note in arrows:
            arrow(draw, box, [names[c] for c in arrows[note]])
        lines.append(f"SpecialChar({code}, {adv}, {box[0]}, {box[1]}, {box[2]}, {box[3]})\t// {note}")

    os.makedirs(out, exist_ok=True)
    write_dds(atlas, os.path.join(out, NAME + ".dds"))
    with open(os.path.join(out, NAME + ".fm"), "w", encoding="latin1", newline="\r\n") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", os.path.join(out, NAME + ".fm"), len(codes), "chars")


if __name__ == "__main__":
    main(*sys.argv[1:4])
