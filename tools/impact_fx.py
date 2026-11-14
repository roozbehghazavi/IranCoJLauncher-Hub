"""Writes IranCoJ Graphics' bullet impacts on surfaces (all authored here).

The weapons' hit tables (WeaponHit.scr, WeaponHitShotgun.scr) name a sequence per surface: Hitground, Hitsand, Hitwood,
Hitstone, Hitmetal and the shotgun's SHit* versions. These replace them by name - water and leaf hits keep the game's:
  - a dust puff in the surface's colour (the smoke flipbook): kicked up and gone in about a second
  - debris thrown out of the surface: clusters of clods, splinters or chips (big sprites: small ones vanish at range),
    falling under gravity
  - sparks off stone and metal
The hit's local +Y faces back out of the surface (towards the shooter), as the gore found.

usage: python tools/impact_fx.py mods/IranCoJGraphics        (writes <mod>/CoJ2/Data/FX/...)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gore_fx import keys  # noqa: E402

N = '\r\n'
files = {}
OUT = (0, 1, 0)


def put(rel, text):
    files[rel] = text.strip('\n').replace('\n', N) + N


def fx_mat(name, tex, blend, note):
    put('IranCoJImpacts/%s.mat' % name, '''
import "fx.mtt"

// IranCoJ Graphics: %s
sub material()
{
    use mtt_fx(
        e_blend_mode = %s,
        s_clr = "%s"
    );
}
''' % (note, blend, tex))


fx_mat('IRN_ImpactDust_particleBLEND', 'IRN_SmokeAnim.dds', 'e_bm_lerp', 'impact dust (the smoke flipbook, tinted per surface)')
for kind in ('Dirt', 'Wood', 'Stone'):
    fx_mat('IRN_Debris%s_particleBLEND' % kind, 'IRN_Debris%s.dds' % kind, 'e_bm_lerp', 'bullet debris: %s' % kind.lower())


def emitter(count, speed, rand, life, direction=OUT):
    e = 'EmiterDef()\n{\n' + keys('LifeTime', [(0, life)]) + '\n\tGenType("one_time")\n\n'
    e += keys('NumParticles', [(0,) + (count if isinstance(count, tuple) else (count,))], 'randf' if isinstance(count, tuple) else 'keyf')
    e += '\n' + keys('StartVelocity', [(0, speed)]) + '\n' + keys('StartVelocityRand', [(0,) + rand], 'keyv')
    e += '\n' + keys('Direction', [(0,) + direction], 'keyv') + '\n\tGenArea("point")\n}\n'
    return e


def particle(life, size, color, material, rect, play, grav=0.0, drag=1.0, wind=0.0, trail=False, size_fn=None):
    p = 'ParticleDef()\n{\n' + keys('LifeTime', [(0, life)]) + '\n' + keys('GravityMul', [(0, grav)]) + '\n'
    p += keys('Drag', [(0, drag)]) + '\n' + keys('WindInfluence', [(0, wind)]) + '\n' + keys('Color', color, 'keyv4') + '\n'
    p += keys('Size', size, size_fn or ('randf' if len(size[0]) == 3 else 'keyf')) + '\n'
    if trail:
        p += '\tTrail()\n\n'
    else:
        p += keys('Rotation', [(0, 0, 360)], 'randf') + '\n'
    p += '\tMaterial("%s", "%s")\n' % (material, material)
    if rect:
        p += '\n\tTexMultiRect(%s)\n\tTexPlayMode(%s)\n' % (rect, play)
    return p + '}\n'


# surface: dust colour, debris atlas (None: no debris), sparks
# (the colours set clearly apart: lit by the sun, close ones all read as the same beige dust)
SURFACES = {
    'ground': ((0.58, 0.42, 0.30), 'Dirt', 0),    # reddish-brown earth
    'sand':   ((0.86, 0.76, 0.52), 'Dirt', 0),    # pale yellow sand
    'wood':   ((0.60, 0.44, 0.27), 'Wood', 0),    # warm brown wood dust
    'stone':  ((0.74, 0.74, 0.73), 'Stone', 6),   # pale grey stone dust
    'metal':  ((0.40, 0.40, 0.42), None, 16),     # dark grey
}


def layers(srf, heavy):
    colour, deb, sparks = SURFACES[srf]
    k = 1.6 if heavy else 1.0   # the shotgun's hits: more of everything
    tag = '%s%s' % (srf, 'Heavy' if heavy else '')
    out = []
    r, g, b = colour
    life = 0.9 * (1.2 if heavy else 1.0)   # gone in about a second, like the gun smoke (at 2 s it lingered)
    out.append(('IRN_Impact_%sDust' % tag, emitter(int(round(4 * k)), 180, (110, 60, 110), life),   # lives as long as its dust (it dies with it)
                particle(life, [(0, 10 * k), (0.2, 30 * k), (life, 65 * k)],
                         [(0, r, g, b, 0), (0.04, r, g, b, 0.7), (0.35, r, g, b, 0.5), (life * 0.5, r, g, b, 0.2), (life, r, g, b, 0)],
                         'IRN_ImpactDust_particleBLEND.mat', '4, 4, 16', '"forward", %g' % round(16 / life, 2),
                         grav=0.05, drag=4.0, wind=1.0), 'dust'))
    if deb:
        out.append(('IRN_Impact_%sDebris' % tag, emitter((int(5 * k), int(9 * k)), 420, (240, 220, 240), 1.3),
                    particle(1.3, [(0, 18, 32)], [(0, 1, 1, 1, 1), (0.9, 1, 1, 1, 1), (1.3, 1, 1, 1, 0)],
                             'IRN_Debris%s_particleBLEND.mat' % deb, '2, 2, 4', '"random_once", 1', grav=1.7, drag=0.6),
                    'debris'))
    if sparks:
        out.append(('IRN_Impact_%sSparks' % tag, emitter(int(sparks * k), 850, (420, 300, 420), 0.35),
                    particle(0.35, [(0, 5, 0.04, 0)], [(0, 1, 0.9, 0.6, 1), (0.35, 1, 0.5, 0.15, 0)], 'Spark_particleADD.mat',
                             None, None, grav=1.0, drag=1.2, trail=True, size_fn='keyv'), 'sparks'))
    return out


SEQUENCES = {
    'gun_hits/Hitground': ('ground', False), 'special/D/Hitsand': ('sand', False), 'gun_hits/Hitwood': ('wood', False),
    'gun_hits/Hitstone': ('stone', False), 'gun_hits/Hitmetal': ('metal', False),
    'gun_hits/RemingtonHit/SHitground': ('ground', True), 'gun_hits/RemingtonHit/SHitwood': ('wood', True),
    'gun_hits/RemingtonHit/SHitstone': ('stone', True), 'gun_hits/RemingtonHit/SHitmetal': ('metal', True),
}
written = set()
for path, (srf, heavy) in SEQUENCES.items():
    parts = layers(srf, heavy)
    seq = 'SequenceDef()\n{\n' + keys('LifeTime', [(0, 2.3)]) + '\n\tRepeat(1)\n'
    for name, e, p, note in parts:
        if name not in written:
            put('IranCoJImpacts/%s_emiter.fx' % name, e)
            put('IranCoJImpacts/%s_particle.fx' % name, p)
            written.add(name)
        seq += '\n\tDelay(0)\n\n\tSpawn()\n\t{\n\t\tParticleEmiter("%s_emiter.fx", "%s_particle.fx")    // IranCoJ Graphics: %s\n\t}\n' % (name, name, note)
    put('FX360/szliniutest/%s_sequence.fx' % path, seq + '}\n')

if __name__ == '__main__':
    fx = os.path.join(sys.argv[1], 'CoJ2', 'Data', 'FX')
    for rel, text in files.items():
        p = os.path.join(fx, rel.replace('/', os.sep))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='latin1', newline='').write(text)
    print(len(files), 'files')
