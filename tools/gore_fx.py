"""Writes the IranCoJ Gore mod's effects, materials and surface tables (all authored here).

A hit is a layered sequence, the way modern Chrome Engine games build it: big sprites whose textures carry many drops
(tools/fx_textures.py) - a stream thrown out of the exit side, a radial burst, drop clusters, long streaks, a quick
spray puff and a faint haze - the elongated ones stretched along their flight (Trail: an Align("on_start") sprite lies
flat along its flight in this engine, edge-on to the camera and nearly invisible), falling under gravity, opaque for a
moment and then a faint trace. Clusters and heavy gobs leave splatter decals where they land; the game's blood trace
table puts big splatters on the surface behind the target; bodies get an entry wound instead of a bullet hole.

usage: python tools/gore_fx.py mods/IranCoJGraphics        (writes <mod>/CoJ2/Data/FX/...; part of IranCoJ Graphics since 1.7.0)
"""
import os
import sys

N = '\r\n'
files = {}


def put(rel, text):
    files[rel] = text.strip('\n').replace('\n', N) + N


def keys(name, items, fn='keyf'):
    body = '\n'.join('\t\t%s(%s)' % (fn, ', '.join('%g' % v for v in it)) for it in items)
    return '\t%s()\n\t{\n%s\n\t}\n' % (name, body)


# --- materials ---------------------------------------------------------------------------------------------------
def fx_mat(name, tex, note):
    put('IranCoJGore/%s.mat' % name, '''
import "fx.mtt"

// IranCoJ Gore: %s
sub material()
{
    use mtt_fx(
        e_blend_mode = e_bm_lerp,
        s_clr = "%s"
    );
}
''' % (note, tex))


def trace_mat(name, tex, note):
    put('IranCoJGore/%s.mat' % name, '''
import "trace.mtt"

// IranCoJ Gore: %s
sub material()
{
    use mtt(s_clr = "%s");
}
''' % (note, tex))


trace_mat('IRN_BloodSplat_trace', 'IRN_BloodSplat.dds', 'blood splatter decals on the world (like the bullet holes, lit by the map)')
trace_mat('IRN_Wound_trace', 'IRN_Wound.dds', 'entry wounds on bodies')
fx_mat('IRN_BloodGush_particleBLEND', 'IRN_BloodGush.dds', 'a stream of blood (the texture\'s top is its flight)')
fx_mat('IRN_BloodCluster_particleBLEND', 'IRN_BloodCluster.dds', 'a cluster of drops')
fx_mat('IRN_BloodLine_particleBLEND', 'IRN_BloodLine.dds', 'a long thin streak')
fx_mat('IRN_BloodBurst_particleBLEND', 'IRN_BloodSplat.dds', 'a radial burst (the splatter shape, in the air)')
fx_mat('IRN_BloodMist_particleBLEND', 'IRN_BloodMist.dds', 'spray puff and haze')
fx_mat('IRN_BloodDrop_particleBLEND', 'IRN_BloodDrop.dds', 'heavy gobs')


# --- decals ------------------------------------------------------------------------------------------------------
def trace(size, life, count, material, fade=12.0):
    return ('TraceDef()\n{\n' + keys('LifeTime', [(0, life)]) + '\n' + keys('Size', [(0,) + size], 'randf') +
            '\n\tMaxNumTraces(%d)\n\n' % count +
            keys('Color', [(0, 1, 1, 1, 1), (life - fade, 1, 1, 1, 1), (life, 1, 1, 1, 0)], 'keyv4') + '\n' +
            keys('Rotation', [(0, 0, 360)], 'randf') +
            '\n\tMaterial("%s")\n\n\tTexPlayMode("random_once", 0)\n\tTexMultiRect(2, 2, 0, 0)\n}\n' % material)


# lifetimes (s): splatters leave after a while (asked for: at 90-120 s they stayed for the whole match)
put('IranCoJGore/IRN_BloodSplatter_trace.fx', trace((16, 40), 25, 160, 'IRN_BloodSplat_trace.mat', fade=8))
for srf in ('Ground', 'Wood', 'Stone', 'Metal'):
    put('Weapon/Hit/BulletBloodTrace%s_trace.fx' % srf, trace((40, 90), 40, 60, 'IRN_BloodSplat_trace.mat', fade=10))
put('Weapon/Hit/BulletHitFleshTrace.fx', trace((5, 8), 30, 60, 'IRN_Wound_trace.mat', fade=8))
put('Weapon/Hit/BulletTraceFlesh_trace.fx', trace((5, 8), 30, 60, 'IRN_Wound_trace.mat', fade=8))


# --- emitters and particles ----------------------------------------------------------------------------------------
EXIT = (0, -1, 0)   # the hit's local -Y: out of the exit side, away from the shooter
BACK = (0, 1, 0)


def emitter(count, speed, rand, direction, life, trace_fx=None, probability=0.0):
    e = 'EmiterDef()\n{\n' + keys('LifeTime', [(0, life)]) + '\n\tGenType("one_time")\n\n'
    e += keys('NumParticles', [(0,) + (count if isinstance(count, tuple) else (count,))], 'randf' if isinstance(count, tuple) else 'keyf')
    e += '\n' + keys('StartVelocity', [(0, speed)]) + '\n' + keys('StartVelocityRand', [(0,) + rand], 'keyv')
    e += '\n' + keys('Direction', [(0,) + direction], 'keyv') + '\n\tGenArea("point")\n'
    if trace_fx:
        e += '\n\tCollisionAction("spawn_fx")\n\t{\n\t\tTrace("%s")\n\t\tProbability(%g)\n\t}\n' % (trace_fx, probability)
    return e + '}\n'


def particle(life, size, color, material, rect, grav=(1.0, 1.0), drag=(1.0, 1.0), aspect=None, align=False, spin=True,
             trail=False):
    p = 'ParticleDef()\n{\n' + keys('LifeTime', [(0, life)]) + '\n'
    p += keys('GravityMul', [(0,) + grav], 'randf') + '\n' + keys('Drag', [(0,) + drag], 'randf') + '\n'
    p += keys('Color', color, 'keyv4') + '\n' + keys('Size', size, 'randf' if len(size[0]) == 3 else 'keyf') + '\n'
    if trail:
        p += '\tTrail()\n\n'
    if align:
        p += '\tAlign("on_start")\n\n'
    if aspect:
        p += keys('AspectRatio', [(0,) + aspect], 'randf') + '\n'
    if spin and not align and not trail:
        p += keys('Rotation', [(0, 0, 360)], 'randf') + '\n'
    p += '\tMaterial("%s", "%s")\n\n\tTexMultiRect(%s)\n\tTexPlayMode("random_once", 1)\n}\n' % (material, material, rect)
    return p


# The flying blood is lit by the sun and its soft edges blend with a bright ground: untinted it bloomed bright red to
# pink next to the splatters. The particles' colour darkens it to the splatters' deep red (the mist the most).
DROP_TINT = 0.55
MIST_TINT = 0.45


def tint(items, k):
    return [(t, r * k, g * k, b * k, a) for t, r, g, b, a in items]


def fade(peak=1.0, hold=0.17, mid=0.5, tail=0.12, end=1.5, k=DROP_TINT):
    """Opaque for a moment, then quickly to a faint trace that lingers."""
    return tint([(0, 1, 1, 1, peak), (hold, 1, 1, 1, peak * 0.86), (hold * 1.6, 1, 1, 1, peak * mid),
                 (end * 0.6, 1, 1, 1, peak * tail), (end, 1, 1, 1, 0)], k)


layers = [
    # name, emitter, particle, note
    ('IRN_BloodGush', emitter(1, 260, (0, 90, 0), EXIT, 2.2),
     particle(2.2, [(0, 50), (0.2, 58), (2.5, 165)], fade(end=2.2), 'IRN_BloodGush_particleBLEND.mat', '4, 1, 4',
              grav=(1.0, 1.4), drag=(1.0, 2.0), trail=True), 'the stream out of the exit side'),
    ('IRN_BloodBurst', emitter(1, 450, (0, 0, 0), EXIT, 1.3),
     particle(1.3, [(0, 34), (1.3, 62)], fade(0.5, end=1.3), 'IRN_BloodBurst_particleBLEND.mat', '2, 2, 4',
              grav=(1.6, 1.8), drag=(9, 10)), 'the radial burst'),
    ('IRN_BloodCluster', emitter((12, 18), 520, (55, 240, 55), EXIT, 1.8, 'IRN_BloodSplatter_trace.fx', 0.5),
     particle(1.8, [(0, 26), (0.4, 32), (1.8, 55)], fade(end=1.8), 'IRN_BloodCluster_particleBLEND.mat', '2, 2, 4',
              grav=(1.5, 2.0), drag=(1.0, 2.0)), 'drop clusters, splatting where they land'),
    ('IRN_BloodLine', emitter((2, 4), 255, (240, 0, 240), EXIT, 1.5),
     particle(1.5, [(0, 45, 70)], fade(end=1.5), 'IRN_BloodLine_particleBLEND.mat', '4, 1, 4',
              grav=(0.7, 1.0), drag=(1.0, 2.0), trail=True), 'long streaks'),
    ('IRN_BloodPuff', emitter(5, 300, (200, 200, 200), EXIT, 0.6),
     particle(0.6, [(0, 30, 42)], tint([(0, 1, 1, 1, 0.2), (0.03, 1, 1, 1, 0.4), (0.35, 1, 1, 1, 0.38), (0.6, 1, 1, 1, 0)], MIST_TINT),
              'IRN_BloodMist_particleBLEND.mat', '2, 2, 4', grav=(0, 0), drag=(5, 10)), 'a quick spray puff'),
    ('IRN_BloodHaze', emitter(4, 1200, (200, 200, 200), EXIT, 0.6),
     particle(0.6, [(0, 80, 115)], tint([(0, 1, 1, 1, 0.02), (0.02, 1, 1, 1, 0.13), (0.35, 1, 1, 1, 0.08), (0.6, 1, 1, 1, 0)], MIST_TINT),
              'IRN_BloodMist_particleBLEND.mat', '2, 2, 4', grav=(0, 0), drag=(10, 15)), 'a big faint haze'),
]
seq = 'SequenceDef()\n{\n' + keys('LifeTime', [(0, 2.2)]) + '\n\tRepeat(1)\n'
for name, e, p, note in layers:
    put('IranCoJGore/%s_emiter.fx' % name, e)
    put('IranCoJGore/%s_particle.fx' % name, p)
    seq += '\n\tDelay(0)\n\n\tSpawn()\n\t{\n\t\tParticleEmiter("%s_emiter.fx", "%s_particle.fx")    // IranCoJ Gore: %s\n\t}\n' % (name, name, note)
put('FX360/szliniutest/gun_hits/Hitflesh_sequence.fx', seq + '}\n')

# The shotgun's flesh hit (its own hit table below): every pellet that lands spawns one, so a close blast is 8+ of these
# together - per pellet a second stream, a wider throw and more streaks, a lighter puff and no haze (eight hazes were a
# red cloud). The particles are the pistol's; only the emitters differ.
heavy = [
    ('IRN_BloodGushHeavy', emitter(2, 300, (120, 120, 120), EXIT, 2.2), 'IRN_BloodGush', 'two streams'),
    ('IRN_BloodBurst', None, 'IRN_BloodBurst', 'the radial burst'),
    ('IRN_BloodClusterHeavy', emitter((8, 12), 560, (160, 260, 160), EXIT, 1.8, 'IRN_BloodSplatter_trace.fx', 0.5),
     'IRN_BloodCluster', 'drop clusters, a wider throw'),
    ('IRN_BloodLineHeavy', emitter((3, 5), 300, (300, 60, 300), EXIT, 1.5), 'IRN_BloodLine', 'more streaks'),
    ('IRN_BloodPuffHeavy', emitter(3, 300, (220, 220, 220), EXIT, 0.6), 'IRN_BloodPuff', 'a lighter puff'),
]
seq = 'SequenceDef()\n{\n' + keys('LifeTime', [(0, 2.2)]) + '\n\tRepeat(1)\n'
for name, e, part, note in heavy:
    if e:
        put('IranCoJGore/%s_emiter.fx' % name, e)
    seq += '\n\tDelay(0)\n\n\tSpawn()\n\t{\n\t\tParticleEmiter("%s_emiter.fx", "%s_particle.fx")    // IranCoJ Gore: %s\n\t}\n' % (name, part, note)
put('FX360/szliniutest/gun_hits/RemingtonHit/SHitFlesh_sequence.fx', seq + '}\n')
put('Weapon/Hit/WeaponHitShotgun.scr', '''
!include("FXSurface.def")

// IranCoJ Graphics: the shotgun's hit effects by surface - its own flesh hit (SHitFlesh, per pellet)
SRF_UNKNOWN( "SHitground" )
SRF_WATER( "SHitwater" )
SRF_GRASS( "SHitground" )
SRF_GROUND( "SHitground" )
SRF_MUD( "SHitground" )
SRF_GRAVEL( "Hitsand" )
SRF_FLESH( "SHitFlesh" )
SRF_WOOD( "SHitwood" )
SRF_METAL( "SHitmetal" )
SRF_STONE( "SHitstone" )
SRF_GROUND_W( "SHitGroundW" )
SRF_LEAF_GREEN( "SHittree" )
SRF_LEAF_YELLOW( "SHittree" )
SRF_LEAF_NEEDLE( "SHittree2" )
''')

# the game's own flesh-hit emitters: heavy gobs that splat (BulletHitFleshDirt), a back-spray puff (BulletHitFleshSmoke)
put('Weapon/Hit/BulletHitFleshDirt_emiter.fx', emitter(8, 320, (180, 220, 180), EXIT, 1.5, 'IRN_BloodSplatter_trace.fx', 0.8))
put('Weapon/Hit/BulletHitFleshDirt_particle.fx',
    particle(1.5, [(0, 9, 15)], fade(end=1.5), 'IRN_BloodDrop_particleBLEND.mat', '2, 2, 4', grav=(1.3, 1.3), drag=(0.4, 0.4)))
put('Weapon/Hit/BulletHitFleshSmoke_emiter.fx', emitter(3, 160, (120, 120, 120), BACK, 0.45))
put('Weapon/Hit/BulletHitFleshSmoke_particle.fx',
    particle(0.45, [(0, 18), (0.45, 45)], tint([(0, 1, 1, 1, 0.35), (0.45, 1, 1, 1, 0)], MIST_TINT), 'IRN_BloodMist_particleBLEND.mat',
             '2, 2, 4', grav=(0.05, 0.05), drag=(3, 3)))

# --- tables ------------------------------------------------------------------------------------------------------
put('Weapon/Hit/WeaponBloodTrace.scr', '''
!include("FXSurface.def")

// IranCoJ Gore: the splatter on the surface behind a hit, by that surface
SRF_UNKNOWN( "BulletBloodTraceGround" )
SRF_GRASS( "BulletBloodTraceGround" )
SRF_GROUND( "BulletBloodTraceGround" )
SRF_MUD( "BulletBloodTraceGround" )
SRF_GRAVEL( "BulletBloodTraceGround" )
SRF_FLESH( "BulletBloodTraceGround" )
SRF_WOOD( "BulletBloodTraceWood" )
SRF_METAL( "BulletBloodTraceMetal" )
SRF_STONE( "BulletBloodTraceStone" )
''')
put('Weapon/Hit/WeaponTrace.scr', '''
!include("FXSurface.def")

// IranCoJ Gore: bullet holes by surface - bodies get a wound, not a hole in the ground
SRF_UNKNOWN( "BulletTraceGround" )
SRF_WATER( "BulletTraceWater" )
SRF_GRASS( "BulletTraceGround" )
SRF_GROUND( "BulletTraceGround" )
SRF_MUD( "BulletTraceGround" )
SRF_FLESH( "BulletTraceFlesh" )
SRF_WOOD( "BulletTraceWood" )
SRF_METAL( "BulletTraceMetal" )
SRF_STONE( "BulletTraceStone" )
''')

if __name__ == '__main__':
    fx = os.path.join(sys.argv[1], 'CoJ2', 'Data', 'FX')
    for rel, text in files.items():
        p = os.path.join(fx, rel.replace('/', os.sep))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='latin1', newline='').write(text)
    print(len(files), 'files')
