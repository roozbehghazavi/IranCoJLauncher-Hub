"""Design mockups (not shipped): class selection and scoreboard in Persepolis Dust.

    python tools/mockups/ingame_mockups.py <class-screen screenshot 1600x900> <out folder>
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OSWALD = os.path.join(HERE, "..", "fonts", "Oswald.ttf")

INK = (14, 13, 11)
SMOKE = (29, 29, 26)
WOOD = (92, 79, 64)
SAND = (165, 137, 103)
GOLD = (226, 177, 94)
PARCH = (243, 235, 221)
DUST = (185, 172, 152)
HIGHLIGHT = (64, 55, 42)
RED = (196, 72, 52)
BLUE = (76, 140, 190)
W, H = 1600, 900


def font(size, weight=500):
    f = ImageFont.truetype(OSWALD, size)
    f.set_variation_by_axes([weight])
    return f


def backdrop(shot):
    """The live game view, softened and darkened so panels and text read on it."""
    im = shot.convert("RGB").filter(ImageFilter.GaussianBlur(6))
    return Image.eval(im, lambda v: int(v * 0.5)).convert("RGBA")


def panel(d, box, title=None, accent=GOLD):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=SMOKE + (246,), outline=WOOD + (255,), width=2)
    d.rectangle([x0, y0, x1, y0 + 3], fill=accent + (255,))
    if title:
        d.text((x0 + 22, y0 + 16), title, font=font(18, 600), fill=DUST + (255,))


def star(d, cx, cy, r, color):
    import math
    pts = [(cx + (r if i % 2 == 0 else r * 0.45) * math.sin(i * math.pi / 5),
            cy - (r if i % 2 == 0 else r * 0.45) * math.cos(i * math.pi / 5)) for i in range(10)]
    d.polygon(pts, fill=color + (255,))


def stars(d, x, cy, filled, r=7, gap=17):
    for i in range(3):
        star(d, x + r + i * gap, cy, r, GOLD if i < filled else WOOD)


def text(d, xy, s, size, color, weight=500, anchor="la"):
    d.text(xy, s, font=font(size, weight), fill=color + (255,), anchor=anchor)


def top_bar(d, right_items):
    d.rectangle([0, 0, W, 104], fill=INK + (200,))
    d.line([(0, 104), (W, 104)], fill=WOOD + (255,), width=2)
    text(d, (80, 26), "TOMBSTONE", 44, PARCH, 600)
    text(d, (318, 44), "MANHUNT", 22, GOLD, 500)
    x = W - 80
    for label, value, color in reversed(right_items):
        vw = d.textlength(value, font=font(30, 600))
        text(d, (x, 34), value, 30, color, 600, "ra")
        text(d, (x - vw - 12, 44), label, 18, DUST, 500, "ra")
        x -= vw + 12 + d.textlength(label, font=font(18)) + 48


def key(d, x, y, k, label):
    kw = d.textlength(k, font=font(16, 600)) + 18
    d.rounded_rectangle([x, y, x + kw, y + 28], radius=4, outline=SAND + (255,), width=1)
    text(d, (x + kw / 2, y + 14), k, 16, SAND, 600, "mm")
    text(d, (x + kw + 10, y + 14), label, 18, DUST, 500, "lm")
    return x + kw + 10 + d.textlength(label, font=font(18)) + 30


CLASSES = ["Gunslinger", "Miner", "Rifleman", "Sniper", "Native", "Scout", "Trapper", "Gunsmith", "Hombre",
           "Spy", "Officer", "Duelist", "Veteran"]


def class_screen(shot, out):
    im = backdrop(shot)
    ov = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(ov)
    top_bar(d, [("CASH", "$0", GOLD), ("TEAM", "OUTLAWS", RED)])

    # class list
    panel(d, (80, 132, 500, 736), "CHOOSE CLASS")
    icons = shot.crop((100, 140, 160, 720)).resize((60, 580))
    for i, name in enumerate(CLASSES):
        y = 176 + i * 42
        if i == 0:
            d.rectangle([90, y - 4, 490, y + 36], fill=HIGHLIGHT + (235,))
            d.rectangle([90, y - 4, 94, y + 36], fill=GOLD + (255,))
        ov.alpha_composite(icons.crop((0, i * 44.6, 60, i * 44.6 + 40)).convert("RGBA").resize((34, 34)), (108, y - 1))
        stars(d, 156, y + 16, 1)
        text(d, (222, y + 16), name, 24, GOLD if i == 0 else PARCH, 500 if i else 600, "lm")

    # character: portrait only (the game's labels over it go), then the loadout as a readable list
    panel(d, (516, 132, 924, 736), "GUNSLINGER  ·  LEVEL 1")
    char = shot.crop((520, 185, 920, 590)).convert("RGBA")
    soft = char.filter(ImageFilter.GaussianBlur(22))
    mask = Image.new("L", char.size, 0)  # the game's labels + weapon icons, in crop space, feathered
    for box in ((70, 130, 275, 190), (110, 215, 275, 270), (270, 110, 375, 300)):
        ImageDraw.Draw(mask).rectangle(box, fill=255)
    char = Image.composite(soft, char, mask.filter(ImageFilter.GaussianBlur(16)))
    fade = Image.linear_gradient("L").resize((400, 405))  # portrait fades into the panel at the bottom
    char.putalpha(Image.eval(fade, lambda v: 255 if v < 150 else int(255 * (255 - v) / 105)))
    ov.alpha_composite(char, (520, 176))
    loadout = [("Quickshooter", 2, shot.crop((800, 312, 882, 388))), ("Dynamite", 2, shot.crop((796, 394, 884, 470)))]
    d.text((540, 556), "LOADOUT", font=font(16, 600), fill=DUST + (255,))
    for i, (name, count, icon) in enumerate(loadout):
        y = 584 + i * 46
        d.rectangle([536, y - 4, 904, y + 38], fill=(255, 255, 255, 10))
        ov.alpha_composite(icon.convert("RGBA").resize((40, 36)), (546, y - 1))
        text(d, (600, y + 17), name, 24, PARCH, 500, "lm")
        text(d, (890, y + 17), f"× {count}", 24, GOLD, 600, "rm")
    d.line([(540, 682), (900, 682)], fill=WOOD + (255,), width=1)
    text(d, (540, 708), "NEXT UPGRADE", 18, DUST, 500, "lm")
    stars(d, 664, 708, 2)
    text(d, (900, 708), "$400", 24, GOLD, 600, "rm")

    # map + objective
    panel(d, (940, 132, 1520, 736), "MANHUNT")
    m = shot.crop((995, 150, 1460, 620)).resize((380, 384))
    ov.alpha_composite(m.convert("RGBA"), (1040, 176))
    text(d, (1230, 600), "One player is Wanted.", 22, PARCH, 500, "ma")
    text(d, (1230, 632), "His team must protect him to score.", 22, DUST, 400, "ma")

    # action bar
    d.rectangle([0, 770, W, H], fill=INK + (215,))
    d.line([(0, 770), (W, 770)], fill=WOOD + (255,), width=2)
    x = 80
    for label in ("QUIT GAME", "OPTIONS", "SPECTATE"):
        text(d, (x, 816), label, 24, PARCH, 500, "lm")
        x += d.textlength(label, font=font(24)) + 48
    key(d, 80, 850, "TAB", "Scoreboard")
    d.rectangle([1150, 794, 1330, 838], outline=SAND + (255,), width=2)
    text(d, (1240, 816), "CHANGE TEAM", 22, PARCH, 500, "mm")
    d.rectangle([1346, 794, 1520, 838], fill=GOLD + (255,))
    text(d, (1433, 816), "SPAWN", 26, INK, 600, "mm")
    Image.alpha_composite(im, ov).convert("RGB").save(out)
    print("wrote", out)


def team(d, box, name, color, score, rows):
    x0, y0, x1, y1 = box
    panel(d, box, accent=color)
    d.rectangle([x0 + 2, y0 + 4, x1 - 2, y0 + 64], fill=color + (52,))
    text(d, (x0 + 24, y0 + 34), name, 30, color, 600, "lm")
    text(d, (x1 - 24, y0 + 34), str(score), 40, PARCH, 600, "rm")
    cols = [("PLAYER", x0 + 24, "l"), ("ACC", x1 - 330, "r"), ("K / D", x1 - 250, "r"), ("BOUNTY", x1 - 160, "r"),
            ("WALLET", x1 - 80, "r"), ("PING", x1 - 24, "r")]
    for label, cx, a in cols:
        text(d, (cx, y0 + 88), label, 16, DUST, 600, "la" if a == "l" else "ra")
    d.line([(x0 + 20, y0 + 114), (x1 - 20, y0 + 114)], fill=WOOD + (255,), width=1)
    for i, row in enumerate(rows):
        y = y0 + 124 + i * 40
        me = row[0] == "Edition-Test"
        if me:
            d.rectangle([x0 + 6, y, x1 - 6, y + 36], fill=HIGHLIGHT + (235,))
            d.rectangle([x0 + 6, y, x0 + 10, y + 36], fill=GOLD + (255,))
        elif i % 2:
            d.rectangle([x0 + 6, y, x1 - 6, y + 36], fill=(255, 255, 255, 8))
        for (label, cx, a), value in zip(cols, row):
            c = GOLD if me else PARCH
            if label == "PING":
                c = (120, 190, 110) if int(value) < 60 else (220, 170, 80)
            text(d, (cx, y + 18), value, 22, c, 600 if me else 500, "lm" if a == "l" else "rm")


def scoreboard(shot, out):
    im = backdrop(shot)
    ov = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(ov)
    top_bar(d, [("POINTS", "No limit", PARCH), ("PLAYERS", "5 / 26", PARCH), ("TIME", "09:04", GOLD)])
    team(d, (80, 132, 790, 700), "LAWMEN", BLUE, 3, [
        ("[bot]Sundance Kid", "40%", "2/0", "$125", "$220", "12"),
        ("[bot]Jesse James", "—", "4/5", "$100", "$0", "14"),
        ("[bot]Wyatt Earp", "—", "1/1", "$100", "$0", "11")])
    team(d, (810, 132, 1520, 700), "OUTLAWS", RED, 1, [
        ("Edition-Test", "—", "0/0", "$100", "$0", "41"),
        ("[bot]Butch Cassidy", "0%", "1/1", "$100", "$0", "13")])
    d.rectangle([0, 770, W, H], fill=INK + (215,))
    d.line([(0, 770), (W, 770)], fill=WOOD + (255,), width=2)
    text(d, (W / 2, 812), "Waiting for one more player to start", 26, GOLD, 500, "mm")
    key(d, 80, 850, "TAB", "Close")
    Image.alpha_composite(im, ov).convert("RGB").save(out)
    print("wrote", out)


if __name__ == "__main__":
    shot = Image.open(sys.argv[1]).convert("RGB").resize((W, H))
    os.makedirs(sys.argv[2], exist_ok=True)
    class_screen(shot, os.path.join(sys.argv[2], "ingame_class_selection.png"))
    scoreboard(shot, os.path.join(sys.argv[2], "ingame_scoreboard.png"))
