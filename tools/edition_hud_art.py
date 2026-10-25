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


def mix(a, b, t):
    return tuple(round(x * (1 - t) + y * t) for x, y in zip(a, b))


def pill():
    """256x64 for html backgrounds (they take a tileset laid out like the game's button_tile: left cap 0-40,
    stretched middle 40-216, right cap 216-256, all full height): a square dark chip with a wood edge and a gold
    bar on the left. It fills the whole image: html backgrounds ignore transparency (rounded corners came out as
    a black box around the pill)."""
    im = Image.new("RGBA", (256, 64), INK + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 255, 63], outline=WOOD + (255,), width=2)
    d.rectangle([10, 14, 13, 49], fill=GOLD + (255,))
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


def chips():
    """256x256: round timer chip (clock + room for the time), round countdown chip, team badges (concept)."""
    atlas = Image.new("RGBA", (256, 256))
    d = ImageDraw.Draw(atlas)

    def chip(box, outline=WOOD):
        d.rounded_rectangle(box, radius=6, fill=INK + (215,), outline=outline + (255,), width=1)

    chip((0, 0, 159, 51))                                   # irn_hud_timer: 160x52
    d.ellipse([12, 13, 38, 39], outline=GOLD + (255,), width=3)
    d.line([(25, 26), (25, 17)], fill=GOLD + (255,), width=3)
    d.line([(25, 26), (32, 29)], fill=GOLD + (255,), width=3)
    chip((0, 56, 95, 91))                                   # irn_hud_countdown: 96x36
    d.ellipse([9, 64, 28, 83], outline=GOLD + (255,), width=2)
    d.line([(18, 74), (18, 68)], fill=GOLD + (255,), width=2)
    d.line([(18, 74), (23, 76)], fill=GOLD + (255,), width=2)
    chip((100, 56, 195, 91))                                # irn_hud_num: 96x36, numbers only (team timers)
    for y, color, name in ((96, RED, "OUTLAWS"), (154, BLUE, "LAWMEN")):  # irn_badge_red / _blue: 206x54
        chip((0, y, 205, y + 53), color)
        d.rectangle([1, y + 1, 204, y + 52], outline=color + (255,), width=2)
        star(d, 30, y + 27, 14, color)
        d.text((56, y + 27), name, font=font(28), fill=PARCH + (255,), anchor="lm")
    return atlas


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
    for name, image in (("irancoj_hud_strip", strip()), ("irancoj_hud_pill", pill()), ("irancoj_hud_icons", icons()),
                        ("irancoj_hud_chips", chips())):
        write_dds(image, os.path.join(out, name + ".dds"))
