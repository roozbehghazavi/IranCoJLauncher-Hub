"""Art for the Edition's main menu (Persepolis Dust palette), written into edition/files/CoJ2/Data/Menu.

    python tools/edition_menu_art.py tools/art/menu_background.jpg <out: edition/files/CoJ2/Data/Menu> [--no-video]

- textures/irancoj_band.dds   the focused button's band (dark smoke, gold bar on the left), 9-sliced by the game
- textures/irancoj_logo.dds   the "IRANCOJ / EDITION" header
- textures/irancoj_bg.dds     the profile pages' background (the image, softened and darkened)
- textures/irancoj_panel.dds  dialog and list panels (dark smoke, thin wood border), tiled like the game's frame_a.dds
- Movies/MenuMovie_0.wmv      the background: the image with a slow push-in and back (seamless 60 s loop),
                              darkened on the left behind the buttons; silent audio like the original
Needs Pillow, numpy and ffmpeg. Windows fonts: Georgia Bold, Bahnschrift.
"""

import math
import os
import struct
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

INK = (14, 13, 11)
SMOKE = (29, 29, 26)
GOLD = (226, 177, 94)
PARCH = (243, 235, 221)
DUST = (185, 172, 152)
FONTS = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
W, H, FPS, LOOP = 1280, 720, 25, 60


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def write_dds(image, path):
    """Uncompressed 32-bit A8R8G8B8 DDS (bytes B, G, R, A), no mipmaps."""
    image = image.convert("RGBA")
    w, h = image.size
    flags = 0x1 | 0x2 | 0x4 | 0x8 | 0x1000  # caps, height, width, pitch, pixelformat
    pixel_format = struct.pack("<II4sIIIII", 32, 0x41, b"\0\0\0\0", 32,  # RGB | alpha
                               0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
    # size, flags, height, width, pitch, depth, mipmaps, 11 reserved
    header = struct.pack("<4sIIIIIII", b"DDS ", 124, flags, h, w, w * 4, 0, 0) + b"\0" * 44 + pixel_format
    header += struct.pack("<IIIII", 0x1000, 0, 0, 0, 0)  # caps: texture
    assert len(header) == 128
    r, g, b, a = image.split()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(header + Image.merge("RGBA", (b, g, r, a)).tobytes())
    print("wrote", path)


HIGHLIGHT = (64, 55, 42)  # warm, lighter than the panels so a selected row reads on them too


def band():
    """256x64, sliced with 32 px corners: gold bar inside the left corner, a warm band that fades out at the right."""
    im = Image.new("RGBA", (256, 64))
    px = im.load()
    for x in range(256):
        alpha = 225 if x < 224 else int(225 * (255 - x) / 32)
        for y in range(64):
            px[x, y] = (GOLD + (255,)) if x < 4 else (HIGHLIGHT + (alpha,))
    return im


WOOD = (92, 79, 64)


def panel():
    """256x256 in frame_a.dds's layout: 86 px corners and edges around an 84x84 middle tile."""
    im = Image.new("RGBA", (256, 256))
    d = ImageDraw.Draw(im)
    d.rectangle([10, 10, 245, 245], fill=SMOKE + (238,), outline=WOOD + (255,), width=2)
    d.rectangle([10, 10, 245, 12], fill=GOLD + (255,))  # gold top edge
    return im


def flat():
    """64x16 white, tinted by the game: flat title strips."""
    return Image.new("RGBA", (64, 16), (255, 255, 255, 235))


def still(source):
    """1024x512 (stretched back to 16:9 on screen): the background, softened and darkened, for the profile pages."""
    from PIL import ImageFilter
    im = Image.open(source).convert("RGB").resize((1024, 512), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2))
    return Image.eval(im, lambda v: int(v * 0.5)).convert("RGBA")


def logo():
    """512x256; placed at (76, 90) on the 1280x720 menu."""
    im = Image.new("RGBA", (512, 256))
    d = ImageDraw.Draw(im)
    d.text((4, 6), "CALL OF JUAREZ  ·  BOUND IN BLOOD", font=font("bahnschrift.ttf", 17), fill=DUST + (255,))
    d.text((0, 28), "IRANCOJ", font=font("georgiab.ttf", 64), fill=PARCH + (255,))
    d.text((4, 106), "EDITION", font=font("bahnschrift.ttf", 22), fill=GOLD + (255,))
    d.line([(4, 146), (74, 146)], fill=GOLD + (255,), width=2)
    return im


def shade():
    """Darkness multiplier (H, W, 1): left side behind the buttons, and the bottom edge."""
    x = np.arange(W, dtype=np.float32)[None, :]
    y = np.arange(H, dtype=np.float32)[:, None]
    left = 0.92 * np.clip(1 - x / 620, 0, 1) ** 1.6
    bottom = 0.6 * np.clip((y - 520) / 200, 0, 1) ** 1.5
    keep = (1 - left) * (1 - bottom)
    return keep[:, :, None]


def video(source, path, ffmpeg="ffmpeg"):
    im = Image.open(source).convert("RGB")
    cover = max(W / im.width, H / im.height)
    focus_x, focus_y = 0.55, 0.62  # the riders
    keep = shade()
    frames = FPS * LOOP
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cmd = [ffmpeg, "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-f", "lavfi", "-t", str(LOOP), "-i", "anullsrc=r=44100:cl=stereo",
           "-c:v", "msmpeg4", "-vtag", "MP43", "-q:v", "3", "-g", str(FPS * 2),
           "-c:a", "wmav2", "-b:a", "64k", "-shortest", "-f", "asf", path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(frames):
        zoom = 1 + 0.10 * (0.5 - 0.5 * math.cos(2 * math.pi * i / frames))
        scale = cover * zoom
        bw, bh = W / scale, H / scale
        cx = im.width * focus_x + (im.width / 2 - im.width * focus_x) * (1 - (zoom - 1) / 0.10)
        cy = im.height * focus_y + (im.height / 2 - im.height * focus_y) * (1 - (zoom - 1) / 0.10)
        left = min(max(cx - bw / 2, 0), im.width - bw)
        top = min(max(cy - bh / 2, 0), im.height - bh)
        frame = im.resize((W, H), Image.BICUBIC, box=(left, top, left + bw, top + bh))
        pixels = (np.asarray(frame, dtype=np.float32) * keep).astype(np.uint8)
        proc.stdin.write(pixels.tobytes())
        if i % 250 == 0:
            print(f"frame {i}/{frames}")
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print("wrote", path, os.path.getsize(path) // 1024, "KB")


if __name__ == "__main__":
    source, out = sys.argv[1], sys.argv[2]
    write_dds(band(), os.path.join(out, "textures", "irancoj_band.dds"))
    write_dds(logo(), os.path.join(out, "textures", "irancoj_logo.dds"))
    write_dds(panel(), os.path.join(out, "textures", "irancoj_panel.dds"))
    write_dds(flat(), os.path.join(out, "textures", "irancoj_flat.dds"))
    write_dds(still(source), os.path.join(out, "textures", "irancoj_bg.dds"))
    if "--no-video" not in sys.argv:
        video(source, os.path.join(out, "Movies", "MenuMovie_0.wmv"))
