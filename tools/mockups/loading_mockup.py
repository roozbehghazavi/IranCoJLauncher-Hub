"""Design concept (not shipped): the multiplayer loading screen.

    python tools/mockups/loading_mockup.py <map's loading picture (colour)> <current loading screenshot> <out folder>

Left: the map's story in the Edition's type (mode, name, place and date, description). Right: the objectives map
on a card. The map's own loading picture fills the back in colour (no sepia, no brush frame), darkened on the
left for the text. A slim gold spinner and "LOADING" replace the revolver drum.
"""

import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ingame_mockups import DUST, GOLD, H, INK, PARCH, SAND, SMOKE, W, WOOD, font, text  # noqa: E402

DESC = ("The High Fives gang will attempt a bank robbery. Outlaws will try to break into the local bank, make "
        "their way to a cash vault and open a safe inside. Next they will capture the stables. From there they'll "
        "head for Skeleton Canyon, where they can make their getaway.")


def wrap(d, s, f, width):
    lines, line = [], ""
    for word in s.split():
        test = (line + " " + word).strip()
        if d.textlength(test, font=f) > width and line:
            lines.append(line)
            line = word
        else:
            line = test
    return lines + [line]


def loading(picture, shot, out):
    # back: the map's picture in colour, softly blurred, darker towards the left and the bottom
    im = picture.convert("RGB").resize((W, H)).filter(ImageFilter.GaussianBlur(3)).convert("RGBA")
    import numpy as np
    xs = np.arange(W, dtype=np.float32)[None, :]
    ys = np.arange(H, dtype=np.float32)[:, None]
    left = 40 + 195 * np.clip(1 - xs / (W * 0.62), 0, 1) ** 0.9
    bottom = 200 * np.clip((ys - (H - 220)) / 220, 0, 1) ** 1.6
    alpha = np.maximum(left, bottom).clip(0, 235).astype(np.uint8)
    shade = Image.new("RGBA", (W, H), INK + (0,))
    shade.putalpha(Image.fromarray(alpha))
    im.alpha_composite(shade)
    d = ImageDraw.Draw(im)

    # left: the story
    x = 120
    text(d, (x, 168), "WILD WEST LEGENDS", 22, GOLD, 600)
    text(d, (x, 196), "NOGALES", 86, PARCH, 600)
    text(d, (x, 312), "Arizona territory  ·  August 6, 1895", 24, SAND, 500)
    d.rectangle([x, 362, x + 64, 365], fill=GOLD + (255,))
    f = font(25, 400)
    for i, line in enumerate(wrap(d, DESC, f, 560)):
        d.text((x, 392 + i * 38), line, font=f, fill=PARCH + (235,))

    # right: the objectives map on a card (the map art itself is the game's)
    mx0, my0, size = 930, 150, 520
    d.rectangle([mx0 - 14, my0 - 14, mx0 + size + 14, my0 + size + 54], fill=SMOKE + (240,), outline=WOOD + (255,), width=2)
    d.rectangle([mx0 - 14, my0 - 14, mx0 + size + 14, my0 - 11], fill=GOLD + (255,))
    minimap = shot.convert("RGB").resize((W, H)).crop((818, 138, 1424, 744)).resize((size, size))
    im.paste(minimap, (mx0, my0))
    d = ImageDraw.Draw(im)
    text(d, (mx0, my0 + size + 12), "OBJECTIVES MAP", 16, DUST, 600)
    text(d, (mx0 + size, my0 + size + 8), "Canyon", 22, PARCH, 500, "ra")

    # bottom right: spinner + loading
    cx, cy, r = W - 150, H - 92, 20
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=WOOD + (255,), width=4)
    for k in range(40):
        a0 = -90 + k * 6
        a1 = a0 + 6
        alpha = int(255 * (k / 40))
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=GOLD + (alpha,), width=4)
    text(d, (cx - r - 18, cy), "LOADING", 22, PARCH, 600, "rm")

    im.convert("RGB").save(out)
    print("wrote", out)


if __name__ == "__main__":
    picture = Image.open(sys.argv[1])
    shot = Image.open(sys.argv[2])
    loading(picture, shot, os.path.join(sys.argv[3], "loading_screen.png"))
