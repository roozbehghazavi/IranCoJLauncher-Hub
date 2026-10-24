"""Design concepts, round 2 (not shipped): class screen with an upgrade on offer, and the in-game HUD.

    python tools/mockups/ingame_mockups_v2.py <class screen shot> <gameplay shot> <out folder>
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ingame_mockups import (BLUE, DUST, GOLD, H, HIGHLIGHT, INK, PARCH, RED, SAND, W, WOOD, backdrop, font,  # noqa: E402
                            panel, star, stars, text, top_bar)


def erase(im, boxes, radius=18):
    """Paints over the game's own graphics in a screenshot (concepts only)."""
    soft = im.filter(ImageFilter.GaussianBlur(radius))
    mask = Image.new("L", im.size, 0)
    for b in boxes:
        ImageDraw.Draw(mask).rounded_rectangle(b, radius=10, fill=255)
    return Image.composite(soft, im, mask.filter(ImageFilter.GaussianBlur(10)))


def patch(im, dst, dy, dx=0):
    """Covers dst with the scene dx/dy pixels away (concepts only: hides markings and the game's graphics)."""
    x0, y0, x1, y1 = dst
    src = im.crop((x0 - dx, y0 - dy, x1 - dx, y1 - dy))
    mask = Image.new("L", src.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((12, 12, src.width - 12, src.height - 12), radius=20, fill=255)
    im.paste(src, (x0, y0), mask.filter(ImageFilter.GaussianBlur(10)))
    return im


def button(d, box, label, kind="text", focused=False, size=24):
    x0, y0, x1, y1 = box
    if kind == "primary":
        d.rectangle(box, fill=GOLD + (255,))
        text(d, ((x0 + x1) / 2, (y0 + y1) / 2), label, size, INK, 600, "mm")
    elif kind == "outline":
        d.rectangle(box, outline=SAND + (255,), width=2)
        text(d, ((x0 + x1) / 2, (y0 + y1) / 2), label, size, PARCH, 500, "mm")
    else:
        if focused:
            d.rectangle(box, fill=HIGHLIGHT + (235,))
            d.rectangle([x0, y0, x0 + 4, y1], fill=GOLD + (255,))
        text(d, (x0 + 18, (y0 + y1) / 2), label, size, GOLD if focused else PARCH, 500, "lm")


def class_screen_v2(shot, out):
    im = backdrop(shot)
    ov = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(ov)
    top_bar(d, [("CASH", "$1000", GOLD), ("TEAM", "OUTLAWS", RED)])

    panel(d, (80, 132, 484, 736), "CHOOSE CLASS")
    icons = shot.crop((100, 140, 160, 720))
    names = ["Rifleman", "Sniper", "Native", "Scout", "Trapper", "Gunsmith", "Hombre", "Spy", "Officer", "Duelist",
             "Veteran", "Rancher", "Redneck"]
    for i, name in enumerate(names):
        y = 172 + i * 43.5
        if name == "Redneck":
            d.rectangle([110, y - 6, 474, y + 34], fill=(120, 40, 30, 235))
            d.rectangle([110, y - 6, 114, y + 34], fill=RED + (255,))
        ov.alpha_composite(icons.crop((0, i * 44.4, 60, i * 44.4 + 40)).convert("RGBA").resize((34, 34)), (124, int(y) - 3))
        stars(d, 172, y + 14, 1)
        text(d, (236, y + 14), name, 24, PARCH, 600 if name == "Redneck" else 500, "lm")
    # themed scrollbar: a slim wood track at the panel's left edge, gold thumb - clear of the icons
    d.rectangle([94, 172, 98, 712], fill=WOOD + (255,))
    d.rectangle([92, 172, 100, 330], fill=GOLD + (255,))

    panel(d, (500, 132, 924, 736), "REDNECK  ·  LEVEL 1")
    char = shot.crop((580, 178, 748, 450)).convert("RGBA")
    ov.alpha_composite(char.resize((150, 243)), (600, 168))
    ov.alpha_composite(shot.crop((748, 214, 890, 270)).convert("RGBA"), (766, 186))
    d.text((520, 418), "LOADOUT", font=font(16, 600), fill=DUST + (255,))
    for i, (name, icon) in enumerate((("Springfield Musket", shot.crop((522, 522, 566, 562))),
                                      ("Tomahawk", shot.crop((522, 574, 566, 614))))):
        y = 446 + i * 44
        d.rectangle([516, y - 4, 908, y + 36], fill=(255, 255, 255, 10))
        ov.alpha_composite(icon.convert("RGBA").resize((36, 34)), (526, y - 1))
        text(d, (574, y + 16), name, 22, PARCH, 500, "lm")
    # upgrade block: label + stars and cost on one line, what it adds under it, then the button
    d.line([(520, 548), (904, 548)], fill=WOOD + (255,), width=1)
    text(d, (520, 572), "NEXT UPGRADE", 18, DUST, 500, "lm")
    stars(d, 646, 572, 2)
    text(d, (904, 572), "$1000", 24, GOLD, 600, "rm")
    text(d, (520, 606), "+", 22, PARCH, 500, "lm")
    ov.alpha_composite(shot.crop((678, 676, 700, 702)).convert("RGBA").resize((22, 24)), (540, 594))
    text(d, (572, 606), "+1 health", 18, DUST, 400, "lm")
    d.rectangle([516, 640, 908, 690], outline=GOLD + (255,), width=2)
    text(d, (712, 665), "UPGRADE  ·  $1000", 22, GOLD, 600, "mm")

    panel(d, (940, 132, 1520, 736), "MANHUNT")
    m = shot.crop((995, 150, 1460, 620)).resize((380, 384))
    ov.alpha_composite(m.convert("RGBA"), (1040, 176))
    text(d, (1230, 600), "One player is Wanted.", 22, PARCH, 500, "ma")
    text(d, (1230, 632), "His team must protect him to score.", 22, DUST, 400, "ma")

    # bottom bar, two rows, both inside it: Cancel over Quit Game, Change Team over Spawn
    d.rectangle([0, 760, W, H], fill=INK + (215,))
    d.line([(0, 760), (W, 760)], fill=WOOD + (255,), width=2)
    button(d, (80, 772, 320, 812), "Cancel", size=20)
    button(d, (80, 832, 320, 880), "Quit Game")
    button(d, (420, 832, 660, 880), "Options", focused=True)
    button(d, (760, 832, 1000, 880), "Spectate")
    button(d, (1290, 772, 1520, 812), "CHANGE TEAM", "outline", size=20)
    button(d, (1290, 832, 1520, 880), "SPAWN", "primary", size=26)
    text(d, (W / 2, 792), "TAB  Scoreboard", 18, DUST, 500, "mm")
    Image.alpha_composite(im, ov).convert("RGB").save(out)
    print("wrote", out)


def hud(shot, out):
    im = shot.convert("RGB")
    im = patch(im, (460, 655, 800, 890), 0, 380)
    im = patch(im, (780, 655, 1135, 890), 0, 720)
    im = patch(im, (1270, 25, 1550, 210), -200)
    im = erase(im, [(70, 50, 200, 110), (740, 40, 950, 110)]).convert("RGBA")
    ov = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(ov)

    def chip(box, alpha=200, outline=WOOD):
        d.rounded_rectangle(box, radius=6, fill=INK + (alpha,), outline=outline + (255,), width=1)

    # round timer (instead of the hourglass)
    chip((64, 52, 214, 104))
    d.ellipse([80, 64, 106, 90], outline=GOLD + (255,), width=3)
    d.line([(93, 77), (93, 68)], fill=GOLD + (255,), width=3)
    d.line([(93, 77), (100, 80)], fill=GOLD + (255,), width=3)
    text(d, (120, 78), "14:16", 30, PARCH, 600, "lm")

    # team score, blue | red, with the round countdown under it (instead of the pocket watch)
    d.rounded_rectangle((690, 44, 910, 104), radius=8, fill=INK + (215,), outline=WOOD + (255,), width=1)
    d.rectangle([692, 46, 799, 102], fill=BLUE + (70,))
    d.rectangle([801, 46, 908, 102], fill=RED + (70,))
    text(d, (745, 74), "0", 40, PARCH, 600, "mm")
    text(d, (855, 74), "0", 40, PARCH, 600, "mm")
    d.line([(800, 52), (800, 96)], fill=WOOD + (255,), width=2)
    chip((760, 112, 840, 146), 190)
    text(d, (800, 129), "0:23", 22, GOLD, 600, "mm")

    # team badge and Wanted (instead of the crossed revolvers and the stamp)
    chip((1330, 50, 1536, 104), 200, RED)
    star(d, 1360, 77, 14, RED)
    text(d, (1386, 77), "OUTLAWS", 26, PARCH, 600, "lm")
    d.rounded_rectangle((1376, 114, 1536, 154), radius=4, fill=GOLD + (255,))
    star(d, 1398, 134, 10, INK)
    text(d, (1416, 134), "WANTED", 22, INK, 600, "lm")

    # ammo (instead of the black brush strip)
    chip((1180, 786, 1536, 856), 205)
    d.rectangle([1181, 787, 1185, 855], fill=GOLD + (255,))
    text(d, (1206, 806), "SPRINGFIELD", 16, DUST, 600, "lm")
    text(d, (1206, 836), "Musket", 20, PARCH, 500, "lm")
    text(d, (1440, 821), "1", 44, PARCH, 600, "rm")
    text(d, (1452, 830), "/ 45", 22, DUST, 500, "lm")

    # notices: a clean pill instead of the black strip; info line without a box
    d.rounded_rectangle((640, 770, 960, 812), radius=20, fill=INK + (205,), outline=WOOD + (255,), width=1)
    text(d, (800, 791), "No ammo", 22, PARCH, 500, "mm")
    text(d, (64, 860), "You have joined the OUTLAWS team.", 20, DUST, 500, "lm")
    Image.alpha_composite(im, ov).convert("RGB").save(out)
    print("wrote", out)


if __name__ == "__main__":
    cshot = Image.open(sys.argv[1]).convert("RGB").resize((W, H))
    hshot = Image.open(sys.argv[2]).convert("RGB").resize((W, H))
    os.makedirs(sys.argv[3], exist_ok=True)
    class_screen_v2(cshot, os.path.join(sys.argv[3], "ingame_class_selection_v2.png"))
    hud(hshot, os.path.join(sys.argv[3], "ingame_hud.png"))
