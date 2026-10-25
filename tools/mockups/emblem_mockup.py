"""Design concepts (not shipped): team emblems. python tools/mockups/emblem_mockup.py <out folder>

Three pairs, each shown as the team icon (end-of-round screen, class screen) and as the HUD team badge.
"""

import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from edition_emblems import deputy, disc, sheriff_star, shield, skull, skull_bones, skull_hat  # noqa: E402
from ingame_mockups import DUST, GOLD, INK, PARCH, SMOKE, WOOD, font, text  # noqa: E402

RED, BLUE = (196, 72, 52), (76, 140, 190)
CONCEPTS = [
    ("A", "Sheriff star  /  Skull", sheriff_star, skull),
    ("B", "Marshal shield  /  Skull & bones", shield, skull_bones),
    ("C", "Deputy badge  /  Skull in a hat", deputy, skull_hat),
]


def badge(emblem, color, name):
    """The HUD team badge (206x54 in game), drawn at 2x."""
    im = Image.new("RGBA", (412, 108))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 411, 107], radius=12, fill=INK + (225,), outline=color + (255,), width=4)
    e = emblem(76, color)
    im.alpha_composite(e, (16, 16))
    d.text((112, 54), name, font=font(56, 600), fill=PARCH + (255,), anchor="lm")
    return im


def sheet(out):
    W, H = 1600, 1080
    im = Image.new("RGBA", (W, H), SMOKE + (255,))
    d = ImageDraw.Draw(im)
    text(d, (80, 50), "TEAM EMBLEMS", 22, GOLD, 600)
    text(d, (80, 80), "Pick one pair: each shown as the team icon and as the HUD badge", 30, PARCH, 500)
    for row, (key, title, law, outlaw) in enumerate(CONCEPTS):
        y = 170 + row * 300
        d.rectangle([60, y - 20, W - 60, y + 260], fill=INK + (200,), outline=WOOD + (255,), width=2)
        text(d, (90, y), key, 64, GOLD, 600)
        text(d, (90, y + 84), title, 24, DUST, 500)
        for i, (emblem, color, name) in enumerate(((law, BLUE, "LAWMEN"), (outlaw, RED, "OUTLAWS"))):
            x = 400 + i * 560
            im.alpha_composite(disc(emblem, 140, color), (x, y + 30))
            im.alpha_composite(badge(emblem, color, name).resize((309, 81), Image.LANCZOS), (x + 165, y + 60))
            text(d, (x + 70, y + 190), name.title(), 22, PARCH, 500, "ma")
    im.convert("RGB").save(out)
    print("wrote", out)


if __name__ == "__main__":
    sheet(os.path.join(sys.argv[1], "team_emblems.png"))
