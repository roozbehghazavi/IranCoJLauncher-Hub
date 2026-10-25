"""Team emblems for the Edition, drawn as shapes (no fonts or bitmaps): Lawmen and Outlaws, several styles.

Each function draws one emblem centred in a square RGBA image of `size` px, in `color`, drawn 4x larger and scaled
down for smooth edges. Holes (eyes, the star's centre) are real transparency, so the emblem sits on any backdrop.
"""

import math

from PIL import Image, ImageDraw

SS = 4  # supersampling


def _canvas(size):
    im = Image.new("RGBA", (size * SS, size * SS))
    return im, ImageDraw.Draw(im), size * SS


def _done(im, size):
    return im.resize((size, size), Image.LANCZOS)


def _star_points(cx, cy, r_out, r_in, points, rotation=-90):
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rotation + i * 180 / points)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


HOLE = (0, 0, 0, 0)


def sheriff_star(size, color):
    """Six-point sheriff's star with ball tips and a ringed centre."""
    im, d, s = _canvas(size)
    c, r = s / 2, s * 0.40
    d.polygon(_star_points(c, c, r, r * 0.52, 6), fill=color + (255,))
    for x, y in _star_points(c, c, r, r * 0.52, 6)[::2]:
        b = s * 0.055
        d.ellipse([x - b, y - b, x + b, y + b], fill=color + (255,))
    ring = r * 0.36
    d.ellipse([c - ring, c - ring, c + ring, c + ring], fill=HOLE)
    inner = ring * 0.72
    d.ellipse([c - inner, c - inner, c + inner, c + inner], fill=color + (255,))
    d.polygon(_star_points(c, c, inner * 0.8, inner * 0.36, 5), fill=HOLE)
    return _done(im, size)


def shield(size, color):
    """Marshal's shield with a five-point star cut out of it."""
    im, d, s = _canvas(size)
    c = s / 2
    w, top, bottom = s * 0.36, s * 0.12, s * 0.90
    d.polygon([(c - w, top + s * 0.06), (c - w * 0.5, top), (c, top + s * 0.05), (c + w * 0.5, top), (c + w, top + s * 0.06),
               (c + w, s * 0.50), (c, bottom), (c - w, s * 0.50)], fill=color + (255,))
    d.polygon(_star_points(c, s * 0.46, s * 0.20, s * 0.08, 5), fill=HOLE)
    return _done(im, size)


def deputy(size, color):
    """Round deputy badge: a ring with a five-point star inside it."""
    im, d, s = _canvas(size)
    c, r = s / 2, s * 0.42
    d.ellipse([c - r, c - r, c + r, c + r], fill=color + (255,))
    d.ellipse([c - r * 0.80, c - r * 0.80, c + r * 0.80, c + r * 0.80], fill=HOLE)
    d.polygon(_star_points(c, c * 1.02, r * 0.74, r * 0.30, 5), fill=color + (255,))
    return _done(im, size)


def _skull_into(d, s, cx, cy, scale, color):
    k = s * scale
    d.ellipse([cx - k * 0.40, cy - k * 0.46, cx + k * 0.40, cy + k * 0.24], fill=color + (255,))     # cranium
    d.rounded_rectangle([cx - k * 0.24, cy + k * 0.08, cx + k * 0.24, cy + k * 0.40], radius=k * 0.06, fill=color + (255,))  # jaw
    for side in (-1, 1):                                                                              # eyes
        ex = cx + side * k * 0.16
        d.ellipse([ex - k * 0.11, cy - k * 0.16, ex + k * 0.11, cy + k * 0.06], fill=HOLE)
    d.polygon([(cx, cy + k * 0.08), (cx - k * 0.05, cy + k * 0.18), (cx + k * 0.05, cy + k * 0.18)], fill=HOLE)  # nose
    for i in (-1, 0, 1):                                                                              # teeth
        tx = cx + i * k * 0.08
        d.rectangle([tx - k * 0.012, cy + k * 0.27, tx + k * 0.012, cy + k * 0.40], fill=HOLE)


def skull(size, color):
    """A plain skull."""
    im, d, s = _canvas(size)
    _skull_into(d, s, s / 2, s * 0.54, 1.0, color)
    return _done(im, size)


def skull_bones(size, color):
    """Skull over crossed bones."""
    im, d, s = _canvas(size)
    c = s / 2
    for a in (45, -45):
        r = math.radians(a)
        dx, dy = math.cos(r) * s * 0.40, math.sin(r) * s * 0.40
        d.line([(c - dx, c + s * 0.06 - dy), (c + dx, c + s * 0.06 + dy)], fill=color + (255,), width=int(s * 0.08))
        for x, y in ((c - dx, c + s * 0.06 - dy), (c + dx, c + s * 0.06 + dy)):
            for o in (-1, 1):
                b = s * 0.045
                ox, oy = -math.sin(r) * o * b, math.cos(r) * o * b
                d.ellipse([x + ox - b, y + oy - b, x + ox + b, y + oy + b], fill=color + (255,))
    _skull_into(d, s, c, s * 0.48, 0.78, color)
    return _done(im, size)


def skull_hat(size, color):
    """Skull under a cowboy hat."""
    im, d, s = _canvas(size)
    c = s / 2
    _skull_into(d, s, c, s * 0.60, 0.80, color)
    d.ellipse([c - s * 0.44, s * 0.30, c + s * 0.44, s * 0.42], fill=color + (255,))                  # brim
    d.rounded_rectangle([c - s * 0.22, s * 0.10, c + s * 0.22, s * 0.36], radius=s * 0.08, fill=color + (255,))  # crown
    d.line([(c - s * 0.10, s * 0.11), (c + s * 0.10, s * 0.11)], fill=HOLE, width=int(s * 0.03))       # crease
    d.rectangle([c - s * 0.22, s * 0.29, c + s * 0.22, s * 0.32], fill=HOLE)                            # band
    return _done(im, size)


def disc(emblem, size, color, ink=(14, 13, 11)):
    """The emblem on a dark disc in a team-colour ring (the frame the game's team icons have now)."""
    im = Image.new("RGBA", (size, size))
    d = ImageDraw.Draw(im)
    pad = max(2, size // 20)
    d.ellipse([pad, pad, size - pad - 1, size - pad - 1], fill=ink + (225,), outline=color + (255,), width=max(3, size // 18))
    e = emblem(int(size * 0.62), color)
    im.alpha_composite(e, ((size - e.width) // 2, (size - e.height) // 2))
    return im
