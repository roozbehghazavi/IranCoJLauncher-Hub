"""Crosshair styles for the launcher's Crosshair setting, written into New Classes' HUD textures.

    python tools/crosshairs.py <out: .../CoJ2/Data/Menu/Hud/Textures> [preview.png]

The game draws its crosshair from two pieces of hud_new.dds: "hud_crosshair_helper" (the 32x32 centre ring) and
"hud_crosshair" (the 22x4 bar it draws four times as the spread ticks). New Classes' hud_new.scr points both at
irancoj_crosshair.dds instead (128x64: the ring at 0,0-64,64 and the bar at 64,0-108,8 - twice the on-screen size,
sharp at 1440p). Each style here is one such texture, irancoj_crosshair_<id>.dds; the launcher copies the chosen
one to irancoj_crosshair.dds before the game starts. Our own drawings (the idea from CoJ2 Online's sub-mod
switcher: dot, circle, ticks only, none, and green versions).
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edition_menu_art import write_dds  # noqa: E402

SS = 8                       # drawn this much larger, then scaled down (smooth edges)
RING, BAR = (64, 64), (44, 8)
WHITE, GREEN = (255, 255, 255), (70, 235, 70)

# id -> (ring drawing, bar drawn, colour). Order = the launcher's list.
STYLES = {
    "classic": ("classic", True, WHITE),
    "dot": ("dot", False, WHITE),
    "dot_green": ("dot", False, GREEN),
    "circle": ("circle", False, WHITE),
    "circle_green": ("circle", False, GREEN),
    "ticks": (None, True, WHITE),
    "ticks_green": (None, True, GREEN),
    "none": (None, False, WHITE),
}


def outlined(shape, color):
    """The shape (an L mask) in colour over a soft dark edge, so it reads on bright sky too."""
    edge = shape.filter(ImageFilter.MaxFilter(2 * SS + 1)).filter(ImageFilter.GaussianBlur(SS))
    out = Image.new("RGBA", shape.size, (0, 0, 0, 0))
    out.putalpha(edge.point(lambda v: v * 110 // 255))
    top = Image.new("RGBA", shape.size, color + (255,))
    top.putalpha(shape)
    out.alpha_composite(top)
    return out


def ring(kind):
    w, h = RING[0] * SS, RING[1] * SS
    m = Image.new("L", (w, h))
    d = ImageDraw.Draw(m)
    c = w // 2
    if kind == "classic":  # ring broken at the four ticks, a centre dot
        r, t = 23 * SS, int(2.2 * SS)
        for a in range(4):
            d.arc([c - r, c - r, c + r, c + r], a * 90 + 12, a * 90 + 78, fill=255, width=t)
        d.ellipse([c - 2 * SS, c - 2 * SS, c + 2 * SS, c + 2 * SS], fill=255)
    elif kind == "dot":
        d.ellipse([c - 3 * SS, c - 3 * SS, c + 3 * SS, c + 3 * SS], fill=255)
    elif kind == "circle":
        r, t = 9 * SS, int(2.2 * SS)
        d.ellipse([c - r, c - r, c + r, c + r], outline=255, width=t)
        d.ellipse([c - int(1.6 * SS), c - int(1.6 * SS), c + int(1.6 * SS), c + int(1.6 * SS)], fill=255)
    return m


def bar():
    w, h = BAR[0] * SS, BAR[1] * SS
    m = Image.new("L", (w, h))
    ImageDraw.Draw(m).rounded_rectangle([3 * SS, 2 * SS, w - 3 * SS, h - 2 * SS], radius=2 * SS, fill=255)
    return m


def style(kind, with_bar, color):
    tex = Image.new("RGBA", (128, 64), (0, 0, 0, 0))
    if kind:
        tex.alpha_composite(outlined(ring(kind), color).convert("RGBa").resize(RING, Image.LANCZOS).convert("RGBA"))
    if with_bar:
        tex.alpha_composite(outlined(bar(), color).convert("RGBa").resize(BAR, Image.LANCZOS).convert("RGBA"), (64, 0))
    return tex


def preview(textures, path):
    """Each style as the game shows it: the ring with four ticks around it, on light and dark ground."""
    cell = 150
    sheet = Image.new("RGB", (cell * len(textures), cell * 2 + 24), (30, 30, 30))
    d = ImageDraw.Draw(sheet)
    for i, (sid, tex) in enumerate(textures.items()):
        for row, ground in enumerate(((40, 40, 38), (190, 185, 170))):
            box = Image.new("RGBA", (cell, cell), ground + (255,))
            r = tex.crop((0, 0, 64, 64))
            box.alpha_composite(r, ((cell - 64) // 2, (cell - 64) // 2))
            b = tex.crop((64, 0, 108, 8))
            c = cell // 2
            for x, y, rot in ((c - 66, c - 4, False), (c + 22, c - 4, False), (c - 4, c - 66, True), (c - 4, c + 22, True)):
                box.alpha_composite(b.rotate(90, expand=True) if rot else b, (x, y))
            sheet.paste(box.convert("RGB"), (i * cell, 24 + row * cell))
        d.text((i * cell + 6, 6), sid, fill=(230, 230, 230))
    sheet.save(path)


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    textures = {sid: style(*spec) for sid, spec in STYLES.items()}
    for sid, tex in textures.items():
        write_dds(tex, os.path.join(out, f"irancoj_crosshair_{sid}.dds"))
    if len(sys.argv) > 2:
        preview(textures, sys.argv[2])
    print("wrote", len(textures), "styles to", out)
