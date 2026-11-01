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

    def chip(box, outline=GOLD, width=2):
        """A capsule (design/Persepolis Dust_ Outlaw Showdown.png): fully round ends, a thin coloured rim."""
        x0, y0, x1, y1 = box
        d.rounded_rectangle([v * s for v in box], radius=(y1 - y0 + 1) * s // 2, fill=INK + (225,),
                            outline=outline + (255,), width=width * s)

    def clock_at(x, y, size):
        atlas.alpha_composite(clock().resize((size * s, size * s), Image.LANCZOS), (x * s, y * s))

    chip((0, 0, 131, 51))                                   # irn_hud_timer: 132x52 (the clock + "00:00", even gaps)
    clock_at(17, 12, 28)
    chip((0, 56, 95, 91))                                   # irn_hud_countdown: 96x36
    clock_at(11, 63, 21)
    chip((100, 56, 195, 91))                                # irn_hud_num: 96x36, numbers only (team timers)
    for y, color, name in ((96, RED, "OUTLAWS"), (154, BLUE, "LAWMEN")):  # irn_badge_red / _blue: 196x54 (OUTLAWS + the round end)
        chip((0, y, 195, y + 53), color, 3)
        emblem = EMBLEM[color](36 * s, color)
        atlas.alpha_composite(emblem, (16 * s, (y + 9) * s))
        d.text((60 * s, (y + 27) * s), name, font=font(28 * s), fill=PARCH + (255,), anchor="lm")
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


PLATE_W, PLATE_H = 1024, 200   # irn_score_plate: drawn at the HUD element's shape (288x56)


def score_plate():
    """1024x256 (the plate in the top 1024x200) behind the team score in team modes (design/ingame_hud.png): a
    Lawmen-blue half and an Outlaws-red half, the gold sheriff's star on a dark disc between them. The html
    puts the two scores at either side of the disc."""
    ss = 2
    w, h = PLATE_W * ss, PLATE_H * ss
    im = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(im)
    r = 22 * ss
    pad = 8 * ss
    blue, red = (46, 84, 122), (128, 44, 36)
    d.rounded_rectangle([0, pad, w // 2 + r, h - pad - 1], radius=r, fill=blue + (235,))
    d.rounded_rectangle([w // 2 - r, pad, w - 1, h - pad - 1], radius=r, fill=red + (235,))
    d.rectangle([w // 2 - 2 * ss, pad, w // 2 + 2 * ss, h - pad - 1], fill=INK + (255,))   # the seam
    d.rounded_rectangle([0, pad, w - 1, h - pad - 1], radius=r, outline=INK + (255,), width=4 * ss)
    badge = disc(sheriff_star, h, GOLD)
    im.alpha_composite(badge, ((w - badge.width) // 2, 0))
    plate = im.resize((PLATE_W, PLATE_H), Image.LANCZOS)
    out = Image.new("RGBA", (1024, 256))
    out.alpha_composite(plate, (0, 0))
    return out


def _smooth(v):
    v = min(1.0, max(0.0, v))
    return v * v * (3 - 2 * v)


def score_bits():
    """512x256, the team score of design/Persepolis Dust_ Outlaw Showdown.png: irn_score_star (0,0,128,128) and
    irn_score_skull (128,0,256,128) - the team emblems on dark discs at the bar's ends; irn_bar_red
    (0,144,256,160) - the whole bar; irn_bar_blue (264,144,280,160) - a flat piece, laid over it in steps for
    the Lawmen's share; irn_bar_blue_cap (288,144,304,160) - the first piece, rounded at the left."""
    ss = 4
    im = Image.new("RGBA", (512 * ss, 256 * ss))
    d = ImageDraw.Draw(im)
    d.ellipse([4 * ss, 4 * ss, 124 * ss, 124 * ss], fill=INK + (230,))
    star(d, 64 * ss, 66 * ss, 40 * ss, GOLD)                                  # Lawmen: a plain gold star
    d.ellipse([132 * ss, 4 * ss, 252 * ss, 124 * ss], fill=INK + (230,))
    e = skull_hat(74 * ss, RED)                                              # Outlaws: the skull under a hat
    im.alpha_composite(e, (192 * ss - e.width // 2, 64 * ss - e.height // 2))
    blue, red = (76, 140, 200), (205, 62, 48)
    d.rounded_rectangle([0, 144 * ss, 256 * ss - 1, 160 * ss - 1], radius=8 * ss, fill=red + (255,))
    d.rectangle([264 * ss, 144 * ss, 280 * ss - 1, 160 * ss - 1], fill=blue + (255,))
    d.rounded_rectangle([288 * ss, 144 * ss, 312 * ss - 1, 160 * ss - 1], radius=8 * ss, fill=blue + (255,))
    d.rectangle([304 * ss, 144 * ss, 312 * ss, 160 * ss], fill=(0, 0, 0, 0))   # only the left end is round
    return im.resize((512, 256), Image.LANCZOS)


def killfeed_panel():
    """512x128 body behind the kill feed lines: dark, strongest at the right, gone at the left. Stretched to the
    lines; the gold rules above and below are their own images (irn_rule_star)."""
    im = Image.new("RGBA", (512, 128), INK + (0,))
    px = im.load()
    for x in range(512):
        a = int(165 * _smooth(x / 340.0))
        for y in range(128):
            px[x, y] = INK + (a,)
    return im


RULE_W, RULE_H = 1024, 46   # irn_rule_star: drawn at its HUD element's shape (440x20), so the star stays round


def rule_star():
    """1024x64 (the rule in the top 1024x46): a thin gold rule fading out to both ends, a small gold star in its
    middle (above and below the kill feed)."""
    ss = 2
    w, hh = RULE_W * ss, RULE_H * ss
    im = Image.new("RGBA", (w, hh))
    d = ImageDraw.Draw(im)
    for x in range(0, w, ss):
        a = int(255 * _smooth(min(x, w - x) / (260.0 * ss)))
        d.rectangle([x, hh // 2 - 2 * ss, x + ss - 1, hh // 2 + 2 * ss], fill=GOLD + (a,))
    star(d, w // 2, hh // 2, 21 * ss, GOLD)
    out = Image.new("RGBA", (1024, 64))
    out.alpha_composite(im.resize((RULE_W, RULE_H), Image.LANCZOS), (0, 0))
    return out


def chat_panel():
    """512x128 body behind the chat, between its two gold rims (irn_chat_top / irn_chat_bottom): a soft dark,
    full on the left, fading out over the right third - no hard box edge, no extra shade at top and bottom."""
    im = Image.new("RGBA", (512, 128), INK + (0,))
    px = im.load()
    for x in range(512):
        a = int(195 * _smooth(x / 18.0) * _smooth((511 - x) / 170.0))
        for y in range(128):
            px[x, y] = INK + (a,)
    return im


def chat_rim(bottom=False):
    """512x32 rim of the chat frame (top and bottom alike): a thin gold line fading to both ends, a small gold
    star in its middle; nothing else - the body (chat_panel) is the shade."""
    ss = 4
    im = Image.new("RGBA", (512 * ss, 32 * ss))
    d = ImageDraw.Draw(im)
    for x in range(0, 512 * ss, ss):
        a = int(255 * _smooth(min(x, 512 * ss - x) / (120.0 * ss)))
        d.rectangle([x, 15 * ss, x + ss - 1, 17 * ss - 1], fill=GOLD + (a,))
    star(d, 256 * ss, 16 * ss, 10 * ss, GOLD)
    return im.resize((512, 32), Image.LANCZOS)


KILL_PILLS = [(440, 22 + 32 * n) for n in range(1, 6)]    # the kill feed's shades, by its line count
CHAT_PILLS = [(320, 20 + 23 * n) for n in range(1, 16)]   # the chat's, by its rows


def pill_atlas(sizes, alpha, columns, size, dark_side="left"):
    """The pill shades of one HUD element, each at its exact size (stretching one would bend the round ends):
    rounded panels, dark on dark_side and fading out over the far 45%, laid out in columns of a size x size
    atlas. Returns the atlas and each pill's rect."""
    im = Image.new("RGBA", (size, size))
    rects, x, y, col_w = [], 0, 0, max(w for w, _ in sizes) + 8
    per_col = -(-len(sizes) // columns)
    for i, (w, hh) in enumerate(sizes):
        if i and i % per_col == 0:
            x, y = x + col_w, 0
        mask = Image.new("L", (w * 4, hh * 4))
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, w * 4 - 1, hh * 4 - 1], radius=min(18, hh // 2) * 4, fill=255)
        mask = mask.resize((w, hh), Image.LANCZOS)
        pill = Image.new("RGBA", (w, hh), INK + (0,))
        px, mk = pill.load(), mask.load()
        for xx in range(w):
            f = xx / (w - 1) if dark_side == "left" else 1 - xx / (w - 1)    # 0 at the dark side
            fade = 1.0 - _smooth((f - 0.55) / 0.45)
            for yy in range(hh):
                px[xx, yy] = INK + (int(alpha * fade * mk[xx, yy] / 255),)
        im.alpha_composite(pill, (x, y))
        rects.append((x, y, x + w, y + hh))
        y += hh + 8
    return im, rects


EDIT_PILL = (620, 36)   # the chat's typing box (HUD_Net.xui NetChatEdit I_Background)
SHADE_ALPHA = {"kill": 150, "chat": 160, "edit": 170}


def hint_pill(w=700, hh=40):
    """1024x64 (the pill in the top w x hh): the hint window's back ("You can now afford to upgrade ..."): round
    ends, dark in the middle and fading out towards both ends, drawn at the window's size."""
    mask = Image.new("L", (w * 4, hh * 4))
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w * 4 - 1, hh * 4 - 1], radius=hh * 2, fill=255)
    mask = mask.resize((w, hh), Image.LANCZOS)
    pill = Image.new("RGBA", (w, hh), INK + (0,))
    px, mk = pill.load(), mask.load()
    for x in range(w):
        f = abs(x - (w - 1) / 2) / ((w - 1) / 2)
        fade = 1.0 - _smooth((f - 0.5) / 0.5)
        for y in range(hh):
            px[x, y] = INK + (int(185 * fade * mk[x, y] / 255),)
    out = Image.new("RGBA", (1024, 64))
    out.alpha_composite(pill, (0, 0))
    return out


def standing_pill(w=400, hh=50):
    """512x64 (the capsule in the top w x hh): behind the Shootout / Wanted standing line ("You're 3rd ($195 loss)")
    - dark, a thin gold rim, round ends, like the timer."""
    ss = 4
    im = Image.new("RGBA", (w * ss, hh * ss))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, w * ss - 1, hh * ss - 1], radius=hh * ss // 2, fill=INK + (215,),
                                         outline=GOLD + (255,), width=2 * ss)
    out = Image.new("RGBA", (512, 64))
    out.alpha_composite(im.resize((w, hh), Image.LANCZOS), (0, 0))
    return out


STANDING_BAND = (280, 66)   # the Shootout / Wanted standing block (HUD_Net.xui I_IrnPointsShade)


def standing_band():
    """1024x128: irn_standing_band (0,0,280,66) - the standing block's back: round ends, darkest in the middle and
    fading out to both sides, a little softer at top and bottom; irn_gold_line (0,112,256,116) - the short gold rule
    under the place."""
    w, hh = STANDING_BAND
    mask = Image.new("L", (w * 4, hh * 4))
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w * 4 - 1, hh * 4 - 1], radius=hh * 2, fill=255)
    mask = mask.resize((w, hh), Image.LANCZOS)
    band = Image.new("RGBA", (w, hh), INK + (0,))
    px, mk = band.load(), mask.load()
    for x in range(w):
        f = abs(x - (w - 1) / 2) / ((w - 1) / 2)
        fade = 1.0 - _smooth((f - 0.45) / 0.55)
        for y in range(hh):
            px[x, y] = INK + (int(SHADE_ALPHA["chat"] * fade * mk[x, y] / 255),)
    out = Image.new("RGBA", (1024, 128))
    out.alpha_composite(band, (0, 0))
    d = ImageDraw.Draw(out)
    for x in range(256):
        a = int(255 * _smooth(min(x, 255 - x) / 40.0))
        d.line([(x, 112), (x, 115)], fill=GOLD + (a,))
    return out


def notice_strip():
    """512x96 strip of the bottom-right notice (weapon names, pickups): dark, a gold rim, the left end slanted."""
    ss = 4
    im = Image.new("RGBA", (512 * ss, 96 * ss))
    d = ImageDraw.Draw(im)
    pts = [(44 * ss, 4 * ss), (510 * ss, 4 * ss), (510 * ss, 92 * ss), (4 * ss, 92 * ss)]
    d.polygon(pts, fill=INK + (225,))
    d.line(pts + [pts[0]], fill=GOLD + (255,), width=3 * ss, joint="curve")
    return im.resize((512, 96), Image.LANCZOS)


def center_shade():
    """512x128 soft shade behind the top-centre score / standing line: darkest in the middle, fading to both
    sides and to top and bottom, so any width of text sits in it."""
    def smooth(v):
        v = min(1.0, max(0.0, v))
        return v * v * (3 - 2 * v)

    im = Image.new("RGBA", (512, 128), INK + (0,))
    px = im.load()
    for y in range(128):
        fy = smooth(y / 34.0) * smooth((127 - y) / 34.0)
        for x in range(512):
            fx = smooth(min(x, 511 - x) / 170.0)
            px[x, y] = INK + (int(200 * fx * fy),)
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
                        ("irancoj_chat_shade", chat_shade()), ("irancoj_center_shade", center_shade()),
                        ("irancoj_score_plate", score_plate()), ("irancoj_score_bits", score_bits()),
                        ("irancoj_killfeed_panel", killfeed_panel()), ("irancoj_rule_star", rule_star()),
                        ("irancoj_chat_panel", chat_panel()), ("irancoj_chat_top", chat_rim()),
                        ("irancoj_chat_bottom", chat_rim(True)), ("irancoj_notice_strip", notice_strip())):
        write_dds(image, os.path.join(out, name + ".dds"))
