"""Draws IranCoJ Graphics' effect textures - gore, muzzle flashes, smoke (all original, procedural) - as DDS.

  IRN_BloodSplat.dds  2x2 atlas of splatter decals: a dense centre, a directional spray of drops and streaks
  IRN_BloodDrop.dds   2x2 atlas of round drops (stretched into streaks along their flight by the particles' Trail)
  IRN_BloodMist.dds   2x2 atlas of soft mist puffs
  IRN_Wound.dds       2x2 atlas of entry wounds (on bodies)
  IRN_BloodGush.dds   4x1 strip of blood streams (the top of a cell is its flight)
  IRN_BloodCluster.dds 2x2 atlas of drop clusters (one sprite reads as dozens of drops)
  IRN_BloodLine.dds   4x1 strip of long thin streaks
  IRN_MuzzleFlash.dds 2x2 atlas of muzzle flashes (additive)
  IRN_Debris*.dds     2x2 atlases of bullet debris: dirt clods, wood splinters, stone chips
  IRN_SmokeAnim.dds   4x4 flipbook: a black-powder puff billowing out and fraying (played over a particle's life)

usage: python tools/fx_textures.py <output folder>      (needs numpy, Pillow and NVIDIA Texture Tools' nvtt_export)
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image

NVTT = r'C:\Program Files\NVIDIA Corporation\NVIDIA Texture Tools\nvtt_export.exe'
rng = np.random.default_rng(1873)   # fixed: the same textures every run

# blood: thin films are bright red, thick pools nearly black-red
THIN = np.array([0.58, 0.05, 0.035])
THICK = np.array([0.24, 0.008, 0.008])
AIR = np.array([0.30, 0.012, 0.010])   # flying drops and mist (lit by the scene: darker than a film)


def grid(n):
    y, x = np.mgrid[0:n, 0:n].astype(np.float32)
    return (x + 0.5) / n * 2 - 1, (y + 0.5) / n * 2 - 1


def blur(a, r):
    """Separable box blur, three passes (close to a gaussian)."""
    if r < 1:
        return a
    k = np.ones(2 * r + 1, np.float32) / (2 * r + 1)
    for _ in range(3):
        a = np.apply_along_axis(lambda v: np.convolve(np.pad(v, r, mode='edge'), k, 'valid'), 0, a)
        a = np.apply_along_axis(lambda v: np.convolve(np.pad(v, r, mode='edge'), k, 'valid'), 1, a)
    return a


def noise(n, scale, octaves=4):
    """Fractal value noise in [0, 1]."""
    out = np.zeros((n, n), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        s = max(2, int(scale * 2 ** o))
        g = rng.random((s + 1, s + 1)).astype(np.float32)
        img = Image.fromarray((g * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC)
        out += np.asarray(img, np.float32) / 255 * amp
        tot += amp
        amp *= 0.5
    return out / tot


def ellipse(x, y, cx, cy, rx, ry, ang):
    c, s = np.cos(ang), np.sin(ang)
    u = ((x - cx) * c + (y - cy) * s) / rx
    v = (-(x - cx) * s + (y - cy) * c) / ry
    return 1.0 - (u * u + v * v)


def splat(n, seed_dir):
    """One splatter: an irregular centre, then drops and streaks thrown along a direction."""
    x, y = grid(n)
    field = np.full((n, n), -1.0, np.float32)
    # the centre: overlapping lumps, ragged by noise
    for _ in range(5):
        cx, cy = rng.normal(0, 0.06, 2)
        r = rng.uniform(0.07, 0.16)
        field = np.maximum(field, ellipse(x, y, cx, cy, r, r * rng.uniform(0.6, 1.0), rng.uniform(0, np.pi)))
    field += (noise(n, 10, 5) - 0.5) * 1.6
    # the spray: drops thrown out along the direction (spreading), smaller and more stretched further out
    ang = seed_dir
    for _ in range(140):
        a = ang + rng.normal(0, 0.55)
        d = 0.12 + rng.exponential(0.28)
        if d > 0.92:
            continue
        cx, cy = np.cos(a) * d, np.sin(a) * d
        r = max(0.006, 0.05 * (1.0 - d) ** 1.6 * rng.uniform(0.3, 1.2))
        stretch = 1.0 + d * rng.uniform(1.0, 4.0)
        field = np.maximum(field, ellipse(x, y, cx, cy, r * stretch, r, a))
    # a few long streaks from the centre outwards, thick at the root
    for _ in range(5):
        a = ang + rng.normal(0, 0.35)
        length = rng.uniform(0.35, 0.7)
        for t in np.linspace(0.1, length, 40):
            r = 0.035 * (1.0 - t / length) + 0.004
            field = np.maximum(field, ellipse(x, y, np.cos(a) * t, np.sin(a) * t, r * 1.6, r, a))
    # fine mist of tiny dots all around
    for _ in range(160):
        a = ang + rng.normal(0, 0.9)
        d = rng.uniform(0.15, 0.95)
        field = np.maximum(field, ellipse(x, y, np.cos(a) * d, np.sin(a) * d, 0.006, 0.006, 0) * 0.9)
    field = np.where(x * x + y * y > 0.97, -1.0, field)   # nothing at the cell's edge (no bleeding into the next)
    mask = np.clip(field * 18.0 + 0.5, 0, 1)              # crisp edges, a pixel of anti-aliasing
    thick = np.clip(blur(mask, n // 40) * 1.25 - 0.15, 0, 1) ** 2.2
    rgb = THIN[None, None, :] * (1 - thick[..., None]) + THICK[None, None, :] * thick[..., None]
    rgb *= (0.85 + 0.3 * noise(n, 24, 3))[..., None]       # dried, uneven film
    return np.dstack([rgb, mask])


def drop(n):
    """A round drop (the particles' Trail stretches it into a streak along its flight, whatever the direction)."""
    x, y = grid(n)
    r = np.sqrt(x * x + y * y) + (noise(n, 4, 2) - 0.5) * 0.15
    m = np.clip((0.62 - r) * 9.0, 0, 1)
    rgb = AIR * np.ones((n, n, 3))
    hl = np.clip(ellipse(x, y, -0.18, -0.18, 0.12, 0.09, 0.6) * 4, 0, 1)
    rgb = rgb * (1 - hl[..., None] * 0.35) + np.array([0.6, 0.25, 0.22]) * hl[..., None] * 0.35
    return np.dstack([rgb, m])


def mist(n):
    x, y = grid(n)
    r = np.sqrt(x * x + y * y)
    a = np.clip(1 - r, 0, 1) ** 1.8 * (0.35 + 0.65 * noise(n, 5))
    a = np.clip(a * 1.1, 0, 0.8)
    rgb = AIR[None, None, :] * np.ones((n, n, 1))
    return np.dstack([rgb, a])


def wound(n):
    x, y = grid(n)
    r = np.sqrt(x * x + y * y) + (noise(n, 8) - 0.5) * 0.12
    hole = np.clip((0.16 - r) * 30, 0, 1)
    ring = np.clip((0.42 - r) * 12, 0, 1)
    spatter = np.zeros((n, n), np.float32)
    for _ in range(40):
        a, d = rng.uniform(0, 2 * np.pi), rng.uniform(0.35, 0.85)
        spatter = np.maximum(spatter, np.clip(ellipse(x, y, np.cos(a) * d, np.sin(a) * d, 0.03 + 0.03 * (1 - d), 0.02, a) * 8, 0, 1))
    a = np.clip(np.maximum(ring, spatter), 0, 1)
    rgb = THIN[None, None, :] * (1 - ring[..., None] * 0.5) * np.ones((n, n, 1))
    rgb = rgb * (1 - hole[..., None]) + np.array([0.05, 0.0, 0.0]) * hole[..., None]
    return np.dstack([rgb, a])


def drops_field(x, y, centres, sizes, stretch, angles):
    """Max-union of stretched drops (a crisp mask through the caller's threshold)."""
    f = np.full(x.shape, -1.0, np.float32)
    for (cx, cy), r, k, a in zip(centres, sizes, stretch, angles):
        f = np.maximum(f, ellipse(x, y, cx, cy, r * k, r, a))
    return f


def colour(mask, n):
    thick = np.clip(blur(mask, max(1, n // 48)) * 1.2 - 0.1, 0, 1) ** 1.8
    rgb = AIR[None, None, :] * (1 - thick[..., None]) * 1.25 + THICK[None, None, :] * thick[..., None]
    return np.dstack([rgb, mask])


def gush(w, h):
    """A stream of blood thrown upwards (the top of the cell is its flight): a thick root that breaks into drops."""
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    x = (x + 0.5) / w * 2 - 1
    y = 1 - (y + 0.5) / h * 2                    # +1 at the top
    t = (y + 1) / 2                              # 0 root .. 1 tip
    wob = (noise(max(w, h), 5)[:h, :w] - 0.5) * 0.25
    width = 0.10 + 0.55 * t ** 1.3
    body = 1 - np.abs(x + wob * t) / np.maximum(width, 1e-3)
    # the stream erodes into blobs towards the tip (no hard end): ragged by noise, thinning with distance
    erode = np.clip((t - 0.3) / 0.45, 0, 1)
    body = body - erode * 1.1 + (noise(max(w, h), 14)[:h, :w] - 0.5) * (0.4 + 1.2 * erode)
    k = 90
    cs = [(rng.normal(0, 0.18 + 0.4 * tt), -1 + 2 * tt) for tt in rng.uniform(0.35, 0.98, k)]
    rs = [0.012 + 0.05 * rng.random() * (1 - abs(cy) * 0.3) for _, cy in cs]
    f = np.maximum(body, drops_field(x, y, cs, rs, [rng.uniform(1.2, 3.0) for _ in cs], [np.pi / 2 + rng.normal(0, 0.2) for _ in cs]))
    f = np.where((np.abs(x) > 0.96) | (y > 0.97) | (y < -0.97), -1.0, f)
    return colour(np.clip(f * 14 + 0.5, 0, 1), max(w, h))


def cluster(n):
    """A burst of dozens of drops, densest in the middle (one sprite reads as many drops)."""
    x, y = grid(n)
    k = 70
    d = np.clip(np.abs(rng.normal(0, 0.42, k)), 0, 0.9)
    a = rng.uniform(0, 2 * np.pi, k)
    cs = list(zip(np.cos(a) * d, np.sin(a) * d))
    rs = list(np.clip(0.11 * (1 - d) ** 1.5 * rng.uniform(0.35, 1.2, k), 0.012, None))
    f = drops_field(x, y, cs, rs, list(1 + d * rng.uniform(0.5, 2.5, k)), list(a))
    f = np.where(x * x + y * y > 0.95, -1.0, f)
    return colour(np.clip(f * 16 + 0.5, 0, 1), n)


def line(w, h):
    """A long thin streak (the top is its flight), beads along it and drops at the tip."""
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    x = (x + 0.5) / w * 2 - 1
    y = 1 - (y + 0.5) / h * 2
    t = (y + 1) / 2
    width = 0.06 + 0.22 * np.sin(np.clip(t, 0, 1) * np.pi) ** 0.7
    wob = (noise(max(w, h), 4)[:h, :w] - 0.5) * 0.2
    body = 1 - np.abs(x + wob) / np.maximum(width, 1e-3)
    body = np.where((t > 0.05) & (t < 0.85), body, -1)
    cs = [(rng.normal(0, 0.12), rng.uniform(0.55, 0.95)) for _ in range(14)]
    rs = [rng.uniform(0.04, 0.12) for _ in cs]
    f = np.maximum(body, drops_field(x, y, cs, rs, [1.6] * len(cs), [np.pi / 2] * len(cs)))
    f = np.where((np.abs(x) > 0.96) | (np.abs(y) > 0.97), -1.0, f)
    return colour(np.clip(f * 12 + 0.5, 0, 1), max(w, h))


def strip(cells):
    return np.hstack(cells)


def flash(n):
    """A muzzle flash: a hot core and a few wide flame lobes, ragged by noise, through yellow to orange (additive)."""
    x, y = grid(n)
    r = np.sqrt(x * x + y * y)
    ang = np.arctan2(y, x)
    k = int(rng.integers(4, 6))
    phase = rng.uniform(0, 2 * np.pi)
    lobes = np.abs(np.cos((ang + phase) * k / 2)) ** 2.2
    flame = noise(n, 7, 4)
    reach = 0.32 + 0.6 * lobes * (0.6 + 0.8 * flame)
    i = np.clip(1 - r / np.maximum(reach, 0.05), 0, 1) ** 1.4 * (0.75 + 0.5 * flame)
    core = np.clip(1 - r / 0.26, 0, 1) ** 1.5
    i = np.clip(i * 0.9 + core, 0, 1)
    hot = np.array([1.0, 0.96, 0.85])
    warm = np.array([1.0, 0.6, 0.16])
    edge = np.array([0.8, 0.25, 0.04])
    t = i[..., None]
    rgb = np.where(t > 0.5, warm + (hot - warm) * ((t - 0.5) / 0.5), edge + (warm - edge) * (t / 0.5))
    return np.dstack([rgb * t, i])


def smoke_frame(n, f, frames, billows, detail):
    """One frame of a black-powder puff: soft billows that spread and thin out (density -> a feathered alpha)."""
    x, y = grid(n)
    u = f / (frames - 1)
    dens = np.zeros((n, n), np.float32)
    spread = 0.18 + 0.42 * u
    for (bx, by, br, bw) in billows:
        cx, cy = bx * spread / 0.6, by * spread / 0.6 - 0.08 * u      # drifting up a little as it spreads
        rr = br * (0.8 + 0.9 * u)
        dens += bw * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * rr * rr))
    d0, d1 = detail
    dens *= np.clip(0.2 + 1.6 * (d0 * (1 - u) + d1 * u) - 0.35 * u, 0, None)
    dens *= (1.0 - 0.88 * u) * 1.15
    alpha = 1 - np.exp(-np.clip(dens, 0, None) * 1.6)
    alpha *= np.clip((0.98 - (x * x + y * y)) / 0.3, 0, 1)   # feathered at the cell's edge, never a hard circle
    # soft light from above: the top of the puff a little brighter, its underside a little greyer
    lit = 0.82 + 0.12 * np.clip(-y, -1, 1) + 0.06 * (d0 - 0.5)
    rgb = np.dstack([lit * 0.94, lit * 0.93, lit * 0.91])
    return np.dstack([np.clip(rgb, 0, 1), np.clip(alpha, 0, 1)])


def smoke_flipbook(n, frames=16):
    billows = [(rng.normal(0, 0.45), rng.normal(0, 0.38), rng.uniform(0.07, 0.2), rng.uniform(0.4, 1.0)) for _ in range(18)]
    detail = (noise(n, 5, 5), noise(n, 5, 5))
    cells = [smoke_frame(n, f, frames, billows, detail) for f in range(frames)]
    side = int(np.sqrt(frames))
    rows = [np.hstack(cells[r * side:(r + 1) * side]) for r in range(side)]
    return np.vstack(rows)

def debris(n, kind):
    """A cluster of debris thrown by a bullet: dirt clods, wood splinters or stone chips (grey-brown, tinted per surface
    by the particle colour), shaded from the top left."""
    x, y = grid(n)
    f = np.full((n, n), -1.0, np.float32)
    count = {'dirt': 26, 'wood': 14, 'stone': 22}[kind]
    for _ in range(count):
        d = min(abs(rng.normal(0, 0.35)), 0.8)
        a = rng.uniform(0, 2 * np.pi)
        cx, cy = np.cos(a) * d, np.sin(a) * d
        if kind == 'wood':      # long thin splinters
            r = rng.uniform(0.015, 0.035)
            f = np.maximum(f, ellipse(x, y, cx, cy, r * rng.uniform(4, 9), r, rng.uniform(0, np.pi)))
        elif kind == 'stone':   # angular chips: squashed, rotated, ragged
            r = rng.uniform(0.025, 0.07) * (1 - d * 0.6)
            f = np.maximum(f, ellipse(x, y, cx, cy, r * rng.uniform(1, 1.8), r, rng.uniform(0, np.pi)) - noise(n, 20, 2) * 0.6)
        else:                   # round, lumpy clods
            r = rng.uniform(0.02, 0.07) * (1 - d * 0.6)
            f = np.maximum(f, ellipse(x, y, cx, cy, r, r * rng.uniform(0.7, 1.0), rng.uniform(0, np.pi)) - noise(n, 14, 2) * 0.4)
    mask = np.clip(f * 14 + 0.5, 0, 1)
    gy, gx = np.gradient(blur(mask, max(1, n // 128)))
    shade = np.clip(0.72 + (-gx - gy) * n * 0.05, 0.4, 1.0) * (0.85 + 0.3 * noise(n, 18, 3))
    base = {'dirt': (0.62, 0.55, 0.46), 'wood': (0.82, 0.70, 0.52), 'stone': (0.66, 0.65, 0.63)}[kind]
    rgb = np.dstack([shade * base[0], shade * base[1], shade * base[2]])
    return np.dstack([np.clip(rgb, 0, 1), mask])


def atlas(cells):
    top = np.hstack(cells[:2])
    bottom = np.hstack(cells[2:])
    return np.vstack([top, bottom])


def save(arr, path_png):
    Image.fromarray((np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGBA').save(path_png)


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    textures = {
        'IRN_BloodSplat': atlas([splat(512, a) for a in (0.3, 2.1, 3.6, 5.0)]),
        'IRN_BloodDrop': atlas([drop(128) for _ in range(4)]),
        'IRN_BloodMist': atlas([mist(256) for _ in range(4)]),
        'IRN_Wound': atlas([wound(128) for _ in range(4)]),
        'IRN_BloodGush': strip([gush(256, 1024) for _ in range(4)]),
        'IRN_BloodCluster': atlas([cluster(512) for _ in range(4)]),
        'IRN_BloodLine': strip([line(128, 512) for _ in range(4)]),
        'IRN_MuzzleFlash': atlas([flash(256) for _ in range(4)]),
        'IRN_SmokeAnim': smoke_flipbook(256),
        'IRN_DebrisDirt': atlas([debris(256, 'dirt') for _ in range(4)]),
        'IRN_DebrisWood': atlas([debris(256, 'wood') for _ in range(4)]),
        'IRN_DebrisStone': atlas([debris(256, 'stone') for _ in range(4)]),
    }
    for name, arr in textures.items():
        png = os.path.join(out, name + '.png')
        save(arr, png)
        dds = os.path.join(out, name + '.dds')
        subprocess.run([NVTT, png, '-o', dds, '-f', 'bc3', '-q', 'production', '--mip-filter', 'kaiser'], check=True,
                       stdout=subprocess.DEVNULL)
        print(name, arr.shape[:2], os.path.getsize(dds), 'bytes')


if __name__ == '__main__':
    main()
