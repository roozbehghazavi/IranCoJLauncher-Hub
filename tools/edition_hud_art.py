"""Art for the Edition's in-game HUD (Persepolis Dust), written into edition/files/CoJ2/Data/Menu/textures.

    python tools/edition_hud_art.py <out: edition/files/CoJ2/Data/Menu>

The HUD screens (HUD_Net.xui, HUD_Common.xui) use these by name through HUDTextures.def (see edition.json).
"""

import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edition_menu_art import GOLD, INK, PARCH, WOOD, write_dds  # noqa: E402

OSWALD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "Oswald.ttf")
RED = (196, 72, 52)
BLUE = (76, 140, 190)


def font(size, weight=600):
    f = ImageFont.truetype(OSWALD, size)
    f.set_variation_by_axes([weight])
    return f


def star(d, cx, cy, r, color):
    pts = [(cx + (r if i % 2 == 0 else r * 0.45) * math.sin(i * math.pi / 5),
            cy - (r if i % 2 == 0 else r * 0.45) * math.cos(i * math.pi / 5)) for i in range(10)]
    d.polygon(pts, fill=color + (255,))


def strip():
    """64x64, stretched behind notices, info windows and counters: dark smoke, wood edges, soft ends."""
    im = Image.new("RGBA", (64, 64))
    px = im.load()
    for x in range(64):
        a = min(1.0, min(x, 63 - x) / 10)
        for y in range(64):
            edge = y < 2 or y > 61
            px[x, y] = (WOOD + (int(255 * a),)) if edge else (INK + (int(215 * a),))
    return im


def clock():
    """64x64 gold clock: the round timer and the round countdown (were an hourglass and a pocket watch)."""
    im = Image.new("RGBA", (64, 64))
    d = ImageDraw.Draw(im)
    d.ellipse([6, 6, 57, 57], outline=GOLD + (255,), width=6)
    d.line([(32, 32), (32, 16)], fill=GOLD + (255,), width=6)
    d.line([(32, 32), (44, 38)], fill=GOLD + (255,), width=6)
    return im


def score():
    """256x64 plate behind the team score: blue half, red half, wood divider."""
    im = Image.new("RGBA", (256, 64), INK + (215,))
    d = ImageDraw.Draw(im)
    d.rectangle([2, 2, 126, 61], fill=BLUE + (90,))
    d.rectangle([130, 2, 253, 61], fill=RED + (90,))
    d.rectangle([127, 6, 128, 57], fill=WOOD + (255,))
    d.rectangle([0, 0, 255, 63], outline=WOOD + (255,), width=2)
    return im


def team(color):
    """128x128 team emblem (was the crossed revolvers): a dark disc in a team-colour ring with a star."""
    im = Image.new("RGBA", (128, 128))
    d = ImageDraw.Draw(im)
    d.ellipse([6, 6, 121, 121], fill=INK + (225,), outline=color + (255,), width=7)
    star(d, 64, 66, 36, color)
    return im


def wanted():
    """256x70 gold tag (was the stamp): dark star and WANTED."""
    im = Image.new("RGBA", (256, 70))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([4, 4, 251, 65], radius=8, fill=GOLD + (255,))
    star(d, 42, 35, 17, INK)
    d.text((70, 35), "WANTED", font=font(40), fill=INK + (255,), anchor="lm")
    return im


# The game draws these icons by name on every screen (HUD, class screen, scoreboard); they are rects in the
# HUD atlas hud_new.dds. Defined again after it (edition.json, both texture lists) they come from this atlas
# instead: x, y, w, h at twice the original size.
ICONS = {"hud_team_red": (0, 0, 140, 140), "hud_team_blue": (142, 0, 140, 140), "icon_team_timer": (284, 0, 56, 70),
         "icon_timer": (342, 0, 42, 76), "hud_wanted": (0, 142, 308, 84)}


def icons():
    atlas = Image.new("RGBA", (512, 256))
    art = {"hud_team_red": team(RED), "hud_team_blue": team(BLUE), "icon_team_timer": clock(), "icon_timer": clock(),
           "hud_wanted": wanted()}
    for name, (x, y, w, h) in ICONS.items():
        im = art[name]
        im.thumbnail((w, h), Image.LANCZOS)  # keep the art's shape, centred in the game's box
        atlas.alpha_composite(im, (x + (w - im.width) // 2, y + (h - im.height) // 2))
    return atlas


if __name__ == "__main__":
    out = os.path.join(sys.argv[1], "textures")
    for name, image in (("irancoj_hud_strip", strip()), ("irancoj_hud_score", score()), ("irancoj_hud_icons", icons())):
        write_dds(image, os.path.join(out, name + ".dds"))
