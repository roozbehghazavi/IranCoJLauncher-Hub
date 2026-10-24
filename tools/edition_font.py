"""The Edition's fonts: Oswald (SIL Open Font License, tools/fonts/OFL.txt) in place of the game's fonts.

The game draws text from pre-rendered atlases (white glyphs, coverage in alpha; it adds outlines itself) and text
metrics files listing Char(code, advance, x0, y0, x1, y1). Loose files in CoJ2/Data/Panel override the paks, so
writing both under a game font's name changes every text that uses it, menus and in game alike:

    Clarendon Condensed_32   menus, dialogs, lists
    Typodermic_24            in-game headers and HUD texts (map, mode, cash, team, notices)
    Typodermic_36            big HUD digits

    python tools/edition_font.py <game>/CoJ2 tools/fonts/Oswald.ttf <out: edition/files/CoJ2/Data/Panel>

Each font's character list, atlas size, cell height, baseline and cap height are read from the player's own
game files, so Oswald sits where the original did.
"""

import io
import os
import re
import sys
import zipfile

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edition_menu_art import write_dds  # noqa: E402

# Space between glyphs: the game samples a little past each glyph box when it scales text, so neighbours
# packed tight bleed in - the row below showed as a faint "reflection" under the text.
GAP_X, GAP_Y = 3, 6

FONTS = {  # game font -> Oswald weight, horizontal gap
    "Clarendon Condensed_32": (500, GAP_X),
    "Typodermic_24": (500, GAP_X),
    "Typodermic_36": (500, 1),  # big digits in a 256x128 atlas: tight sideways, the rows still apart
}


def game_file(coj2, name):
    """The newest copy of Data/<name> in the game's paks."""
    for n in (3, 2, 1, 0):
        path = os.path.join(coj2, f"Data{n}.pak")
        if not os.path.isfile(path):
            continue
        archive = zipfile.ZipFile(path)
        for entry in archive.namelist():
            if entry.lower() == ("data/" + name).lower():
                return archive.read(entry)
    raise SystemExit(f"{name} not found in the game's paks")


def metrics(fm):
    def value(key):
        return int(re.search(key + r"\((\d+)\)", fm).group(1))

    chars = {int(c): tuple(map(int, rest)) for c, *rest in
             re.findall(r"^Char\((\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)", fm, re.M)}
    specials = [(int(c), int(adv), tuple(map(int, box)), note.strip()) for c, adv, *box, note in re.findall(
        r"^SpecialChar\((\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)\s*(?://\s*(.*))?$", fm, re.M)]
    return value("MapWidth"), value("MapHeight"), value("FontHeight"), chars, specials


def measure(atlas, chars):
    """Baseline and cap height of the original, from its 'H' (or '0' in digit-only fonts)."""
    alpha = atlas.split()[3]
    for probe in ("H", "0"):
        if ord(probe) in chars and chars[ord(probe)][0] > 0:
            _, x0, y0, x1, y1 = chars[ord(probe)]
            box = alpha.crop((x0, y0, x1, y1)).getbbox()
            if box:
                return box[3], box[3] - box[1], probe
    raise SystemExit("no H or 0 to measure")


def oswald(path, weight, cap_height, probe):
    f = ImageFont.truetype(path, 100)
    f.set_variation_by_axes([weight])
    box = f.getbbox(probe, anchor="ls")
    f = ImageFont.truetype(path, round(100 * cap_height / (box[3] - box[1])))
    f.set_variation_by_axes([weight])
    return f


def arrow(draw, box, directions):
    x0, y0, x1, y1 = box
    cx, cy, r = (x0 + x1) / 2, (y0 + y1) / 2, min(11, (y1 - y0) / 4)
    shapes = {
        "left": [(cx - r, cy), (cx + r * 0.6, cy - r), (cx + r * 0.6, cy + r)],
        "right": [(cx + r, cy), (cx - r * 0.6, cy - r), (cx - r * 0.6, cy + r)],
        "up": [(cx, cy - r), (cx - r, cy + r * 0.6), (cx + r, cy + r * 0.6)],
        "down": [(cx, cy + r), (cx - r, cy - r * 0.6), (cx + r, cy - r * 0.6)],
    }
    for d in directions:
        pts = shapes[d]
        if len(directions) == 2:  # two arrows side by side / stacked
            dx, dy = {"left": (-9, 0), "right": (9, 0), "up": (0, -9), "down": (0, 9)}[d]
            pts = [(x + dx, y + dy) for x, y in pts]
        draw.polygon(pts, fill=(255, 255, 255, 255))


ARROWS = {"[ArrowLeftRight]": ["left", "right"], "[ArrowUpDown]": ["up", "down"], "[ArrowDown]": ["down"],
          "[ArrowUp]": ["up"], "[ArrowLeft]": ["left"], "[ArrowRight]": ["right"]}


def build(coj2, ttf, out, name, weight, gap_x):
    fm = game_file(coj2, f"Panel/{name}.fm").decode("latin1")
    original = Image.open(io.BytesIO(game_file(coj2, f"Panel/{name}.dds"))).convert("RGBA")
    map_w, map_h, cell, chars, specials = metrics(fm)
    baseline, cap_height, probe = measure(original, chars)
    font = oswald(ttf, weight, cap_height, probe)
    # Icon glyphs (gamepad buttons, arrows) sit in reserved rects; keep glyphs above them.
    reserved = min([box[1] for _, _, box, _ in specials], default=map_h)

    atlas = Image.new("RGBA", (map_w, map_h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(atlas)
    family = re.search(r'Name\("([^"]*)"\)', fm).group(1)
    lines = [f'Name("{family}")', "", f"MapWidth({map_w})", f"MapHeight({map_h})", f"FontHeight({cell})", "",
             "// IranCoJ Edition: Oswald (SIL Open Font License)", ""]
    x = y = 0
    for code, (advance, *_) in chars.items():
        ch = chr(code)
        if advance == 0 or not ch.isprintable():
            lines.append(f"Char({code}, 0, 0, 0, 0, 0)")
            continue
        width = max(1, round(font.getlength(ch))) + 2
        if x + width > map_w:
            x, y = 0, y + cell + GAP_Y
            if y + cell > reserved:
                raise SystemExit(f"{name}: atlas full")
        draw.text((x + 1, y + baseline), ch, font=font, anchor="ls", fill=(255, 255, 255, 255))
        lines.append(f"Char({code}, {width}, {x}, {y}, {x + width}, {y + cell})")
        x += width + gap_x

    if specials:
        lines.append("")
    for code, adv, box, note in specials:
        if note in ARROWS:
            arrow(draw, box, ARROWS[note])
        lines.append(f"SpecialChar({code}, {adv}, {box[0]}, {box[1]}, {box[2]}, {box[3]})" + (f"\t// {note}" if note else ""))

    os.makedirs(out, exist_ok=True)
    write_dds(atlas, os.path.join(out, name + ".dds"))
    with open(os.path.join(out, name + ".fm"), "w", encoding="latin1", newline="\r\n") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {name}: {len(chars)} chars, cell {cell}, baseline {baseline}, cap {cap_height}")


if __name__ == "__main__":
    coj2, ttf, out = sys.argv[1:4]
    for name, (weight, gap_x) in FONTS.items():
        build(coj2, ttf, out, name, weight, gap_x)
