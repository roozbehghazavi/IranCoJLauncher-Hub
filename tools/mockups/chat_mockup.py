"""Design concept (not shipped): in-game chat.

    python tools/mockups/chat_mockup.py <gameplay shot> <out folder>
"""

import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ingame_mockups import BLUE, DUST, GOLD, H, INK, PARCH, RED, SAND, W, WOOD, font, text  # noqa: E402
from ingame_mockups_v2 import patch  # noqa: E402


def chat(shot, out):
    im = patch(shot.convert("RGB"), (240, 600, 560, 730), 0, -330).convert("RGBA")
    ov = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(ov)

    # message log, bottom left above the input: a soft smoke column, newest at the bottom, older lines fade
    x0, y_bottom = 64, 744
    lines = [("[RR] Shadow", RED, "gg, rematch on Frisco?", 0.45), ("Edition-Test", BLUE, "ninj", 0.7),
             ("Edition-Test", BLUE, "kiris chit", 0.85), ("SERVER", GOLD, "Round starts in 10 seconds", 1.0)]
    back = Image.new("RGBA", (520, 30 * len(lines) + 20))
    bd = ImageDraw.Draw(back)
    for x in range(back.width):
        a = int(150 * max(0.0, 1 - x / back.width) ** 1.3)
        bd.line([(x, 0), (x, back.height)], fill=INK + (a,))
    ov.alpha_composite(back, (x0 - 16, y_bottom - back.height + 6))
    for i, (name, color, msg, alpha) in enumerate(lines):
        y = y_bottom - (len(lines) - i) * 30 + 14
        a = int(255 * alpha)
        d.rectangle([x0 - 8, y - 10, x0 - 5, y + 10], fill=color + (a,))
        nw = d.textlength(name, font=font(20, 600))
        d.text((x0, y), name, font=font(20, 600), fill=color + (a,), anchor="lm")
        d.text((x0 + nw + 10, y), msg, font=font(20, 400), fill=PARCH + (a,), anchor="lm")

    # input: a dark field with a wood frame, the channel as a chip, a gold caret, the send key
    fy = 770
    d.rounded_rectangle((x0 - 8, fy, x0 + 600, fy + 44), radius=6, fill=INK + (225,), outline=WOOD + (255,), width=1)
    d.rounded_rectangle((x0, fy + 8, x0 + 70, fy + 36), radius=4, fill=GOLD + (255,))
    text(d, (x0 + 35, fy + 22), "ALL", 16, INK, 600, "mm")
    text(d, (x0 + 86, fy + 22), "see you at the bank", 20, PARCH, 400, "lm")
    cx = x0 + 86 + d.textlength("see you at the bank", font=font(20, 400)) + 4
    d.rectangle([cx, fy + 11, cx + 2, fy + 33], fill=GOLD + (255,))
    text(d, (x0 + 588, fy + 22), "ENTER  send   ·   TAB  team", 14, SAND, 500, "rm")
    text(d, (x0, fy + 62), "T  all chat     Y  team chat", 14, DUST, 500, "lm")
    Image.alpha_composite(im, ov).convert("RGB").save(out)
    print("wrote", out)


if __name__ == "__main__":
    shot = Image.open(sys.argv[1]).convert("RGB").resize((W, H))
    chat(shot, os.path.join(sys.argv[2], "ingame_chat.png"))
