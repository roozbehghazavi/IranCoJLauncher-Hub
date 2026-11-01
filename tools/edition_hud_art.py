"""Art for the Edition's in-game HUD (Persepolis Dust), written into edition/files/CoJ2/Data/Menu/textures.

    python tools/edition_hud_art.py <out: edition/files/CoJ2/Data/Menu>

The HUD screens (HUD_Net.xui, HUD_Common.xui) use these by name through HUDTextures.def (see edition.json).
"""

import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edition_emblems import disc, sheriff_star, skull_hat  # noqa: E402
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
    """Gold clock for the round countdown (was a pocket watch), drawn large so it scales down sharp."""
    im = Image.new("RGBA", (256, 256))
    d = ImageDraw.Draw(im)
    d.ellipse([24, 24, 231, 231], outline=GOLD + (255,), width=24)
    d.line([(128, 128), (128, 64)], fill=GOLD + (255,), width=24)
    d.line([(128, 128), (176, 152)], fill=GOLD + (255,), width=24)
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


EMBLEM = {RED: skull_hat, BLUE: sheriff_star}  # Outlaws: a skull under a cowboy hat; Lawmen: a sheriff's star


def team(color):
    """128x128 team emblem (was the crossed revolvers): the team's emblem on a dark disc in a team-colour ring."""
    return disc(EMBLEM[color], 128, color)


def wanted():
    """256x70 gold tag (was the stamp): dark star and WANTED."""
    im = Image.new("RGBA", (256, 70))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([4, 4, 251, 65], radius=8, fill=GOLD + (255,))
    star(d, 42, 35, 17, INK)
    d.text((70, 35), "WANTED", font=font(40), fill=INK + (255,), anchor="lm")
    return im


CHIPS_REAL = 2   # irancoj_hud_chips.dds is 512x512 but declared 256x256: twice as sharp, same rects
CHIPS_SS = 4     # drawn this much larger again, then scaled down (smooth edges)


def chips():
    """Round timer chip (a clock + room for the time), round countdown chip, team badges. Laid out in the
    declared 256x256 space; the file is CHIPS_REAL times that."""
    s = CHIPS_REAL * CHIPS_SS
    atlas = Image.new("RGBA", (256 * s, 256 * s))
    d = ImageDraw.Draw(atlas)

    def chip(box, outline=WOOD, width=1):
        d.rounded_rectangle([v * s for v in box], radius=6 * s, fill=INK + (215,), outline=outline + (255,),
                            width=width * s)

    def clock_at(x, y, size):
        atlas.alpha_composite(clock().resize((size * s, size * s), Image.LANCZOS), (x * s, y * s))

    chip((0, 0, 121, 51))                                   # irn_hud_timer: 122x52 (the clock + "00:00")
    clock_at(11, 12, 28)
    chip((0, 56, 95, 91))                                   # irn_hud_countdown: 96x36
    clock_at(8, 63, 21)
    chip((100, 56, 195, 91))                                # irn_hud_num: 96x36, numbers only (team timers)
    for y, color, name in ((96, RED, "OUTLAWS"), (154, BLUE, "LAWMEN")):  # irn_badge_red / _blue: 180x54 (fits OUTLAWS)
        chip((0, y, 179, y + 53), color)
        d.rectangle([1 * s, (y + 1) * s, 178 * s, (y + 52) * s], outline=color + (255,), width=2 * s)
        emblem = EMBLEM[color](38 * s, color)
        atlas.alpha_composite(emblem, (11 * s, (y + 8) * s))
        d.text((56 * s, (y + 27) * s), name, font=font(28 * s), fill=PARCH + (255,), anchor="lm")
    return atlas.resize((256 * CHIPS_REAL, 256 * CHIPS_REAL), Image.LANCZOS)


def killfeed_shade():
    """512x256 soft shade behind the kill feed (its html can't draw boxes): darkest at the right edge, where the
    lines end, fading out to the left, up and down - no edge reads as a box. Shown and hidden with the feed's
    own group."""
    def smooth(v):
        v = min(1.0, max(0.0, v))
        return v * v * (3 - 2 * v)

    im = Image.new("RGBA", (512, 256), INK + (0,))
    px = im.load()
    for y in range(256):
        fy = smooth(y / 48.0) * smooth((255 - y) / 48.0)     # soft top and bottom: stretched to the lines shown
        for x in range(512):
            fx = smooth(x / 511.0) ** 1.4                     # strongest at the right, gone before the left
            a = 215 * fx * fy
            px[x, y] = INK + (int(a),)
    return im


def chat_shade():
    """The kill feed's shade mirrored, for the chat: darkest at the left, where the lines start."""
    return killfeed_shade().transpose(Image.FLIP_LEFT_RIGHT)


# The game draws these icons by name on every screen (HUD, class screen, scoreboard); they are rects in the
# HUD atlas hud_new.dds. Defined again after it (edition.json, both texture lists) they come from this atlas
# instead: x, y, w, h at twice the original size.
ICONS = {"hud_team_red": (0, 0, 140, 140), "hud_team_blue": (142, 0, 140, 140), "icon_team_timer": (284, 0, 56, 70),
         "icon_timer": (342, 0, 42, 76), "hud_wanted": (0, 142, 308, 84)}


def icons():
    atlas = Image.new("RGBA", (512, 256))
    # icon_timer (the scoreboard's and the class screen's time) stays empty: the time alone, no clock
    art = {"hud_team_red": team(RED), "hud_team_blue": team(BLUE), "icon_team_timer": clock(),
           "icon_timer": Image.new("RGBA", (42, 76)), "hud_wanted": wanted()}
    for name, (x, y, w, h) in ICONS.items():
        im = art[name]
        im.thumbnail((w, h), Image.LANCZOS)  # keep the art's shape, centred in the game's box
        atlas.alpha_composite(im, (x + (w - im.width) // 2, y + (h - im.height) // 2))
    return atlas


if __name__ == "__main__":
    out = os.path.join(sys.argv[1], "textures")
    for name, image in (("irancoj_hud_strip", strip()), ("irancoj_hud_pill", pill()), ("irancoj_hud_icons", icons()),
                        ("irancoj_hud_chips", chips()), ("irancoj_killfeed_shade", killfeed_shade()),
                        ("irancoj_chat_shade", chat_shade())):
        write_dds(image, os.path.join(out, name + ".dds"))
