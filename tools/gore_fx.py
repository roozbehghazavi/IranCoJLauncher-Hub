"""Writes the IranCoJ Gore mod's effects, materials and surface tables (all authored here).

A hit is a layered sequence, the way modern Chrome Engine games build it: big sprites whose textures carry many drops
(tools/fx_textures.py) - a stream thrown out of the exit side, a radial burst, drop clusters, long streaks, a quick
spray puff and a faint haze - the elongated ones drawn along their flight (Align("always") with a world-space material,
e_type_fx_ws, as the game's own blood streaks: with a plain material aligned and Trail() particles were invisible),
falling under gravity, opaque for a moment and then a faint trace. Clusters and heavy gobs leave splatter decals where they land; the game's blood trace
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
def fx_mat(name, tex, note, aligned=False):
    """aligned: a world-space particle (e_type_fx_ws), drawn along its flight by Align() - the engine draws aligned
    particles only with such a material (the game's own blood streaks: BloodSmall / BloodBig); with a plain one they
    were invisible, as were Trail() ones."""
    put('IranCoJGore/%s.mat' % name, '''
import "fx.mtt"

// IranCoJ Gore: %s
sub material()
{
    use mtt_fx(
        e_blend_mode = e_bm_lerp,%s
        s_clr = "%s"
    );
}
''' % (note, '\n        e_type = e_type_fx_ws,' if aligned else '', tex))


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
fx_mat('IRN_BloodGush_particleBLEND', 'IRN_BloodGush.dds', 'a stream of blood (drawn along its flight)', aligned=True)
fx_mat('IRN_BloodCluster_particleBLEND', 'IRN_BloodCluster.dds', 'a cluster of drops')
fx_mat('IRN_BloodLine_particleBLEND', 'IRN_BloodLine.dds', 'a long thin streak (drawn along its flight)', aligned=True)
fx_mat('IRN_BloodMist_particleBLEND', 'IRN_BloodMist.dds', 'spray puff and haze')
fx_mat('IRN_BloodDrop_particleBLEND', 'IRN_BloodDrop.dds', 'heavy gobs')


# --- decals ------------------------------------------------------------------------------------------------------
def trace(size, life, count, material, fade=12.0, fade_in=0.0):
    """A decal: fades out over its last `fade` seconds; with `fade_in`, it soaks in over its first seconds (no pop)."""
    colour = [(0, 1, 1, 1, 1)] if not fade_in else [(0, 1, 1, 1, 0), (fade_in, 1, 1, 1, 1)]
    return ('TraceDef()\n{\n' + keys('LifeTime', [(0, life)]) + '\n' + keys('Size', [(0,) + size], 'randf') +
            '\n\tMaxNumTraces(%d)\n\n' % count +
            keys('Color', colour + [(life - fade, 1, 1, 1, 1), (life, 1, 1, 1, 0)], 'keyv4') + '\n' +
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
    if trail:   # drawn along its flight every frame, as the game's own blood streaks (needs an aligned material)
        p += '\tAlign("always")\n\n'
        if not aspect:   # narrow: at full width the streams read as thick ribbons (the game's own water streaks: 0.3)
            aspect = (0.25, 0.35)
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
    # Liquid, not sprites that swell: the stream out of the exit side stretched along its flight, a spray of streaks
    # thrown out of the exit at different speeds (a line of them per direction reads as jets breaking up - the old
    # radial burst sprite growing in the air looked cartoony), a little back-spatter towards the shooter, clusters of
    # drops that keep their size.
    ('IRN_BloodGush', emitter(1, 260, (0, 90, 0), EXIT, 2.2),
     particle(2.2, [(0, 18), (0.2, 24), (2.2, 40)], fade(end=2.2), 'IRN_BloodGush_particleBLEND.mat', '4, 1, 4',
              grav=(1.0, 1.4), drag=(1.0, 2.0), trail=True), 'the stream out of the exit side'),
    ('IRN_BloodSpray', emitter((7, 10), 380, (90, 220, 90), EXIT, 1.4, 'IRN_BloodDrip_trace.fx', 0.6),
     particle(1.4, [(0, 14, 22)], fade(end=1.4), 'IRN_BloodLine_particleBLEND.mat', '4, 1, 4',
              grav=(1.2, 1.6), drag=(0.5, 1.0), trail=True), 'a spray of streaks out of the exit'),
    ('IRN_BloodBack', emitter((2, 4), 170, (60, 50, 60), BACK, 1.0, 'IRN_BloodDrip_trace.fx', 0.6),
     particle(1.0, [(0, 9, 14)], fade(end=1.0), 'IRN_BloodLine_particleBLEND.mat', '4, 1, 4',
              grav=(1.3, 1.6), drag=(0.8, 1.2), trail=True), 'back-spatter towards the shooter'),
    ('IRN_BloodCluster', emitter((8, 12), 520, (55, 240, 55), EXIT, 1.8, 'IRN_BloodSplatter_trace.fx', 0.5),
     particle(1.8, [(0, 20, 30)], fade(end=1.8), 'IRN_BloodCluster_particleBLEND.mat', '2, 2, 4',
              grav=(1.5, 2.0), drag=(1.0, 2.0)), 'drop clusters, splatting where they land'),
    ('IRN_BloodLine', emitter((2, 4), 255, (240, 0, 240), EXIT, 1.5),
     particle(1.5, [(0, 22, 35)], fade(end=1.5), 'IRN_BloodLine_particleBLEND.mat', '4, 1, 4',
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
    ('IRN_BloodSprayHeavy', emitter((9, 13), 420, (160, 240, 160), EXIT, 1.4, 'IRN_BloodDrip_trace.fx', 0.6),
     'IRN_BloodSpray', 'a wider spray of streaks'),
    ('IRN_BloodClusterHeavy', emitter((6, 9), 560, (160, 260, 160), EXIT, 1.8, 'IRN_BloodSplatter_trace.fx', 0.5),
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
    # thrown liquid: streaks along their flight, not round discs - the streak strip at a size that still reads at range
    # (the drop sprite at real size, 3-5 cm, was invisible)
    particle(1.5, [(0, 12, 18)], fade(end=1.5), 'IRN_BloodLine_particleBLEND.mat', '4, 1, 4', grav=(1.3, 1.3), drag=(0.4, 0.4),
             trail=True))
put('Weapon/Hit/BulletHitFleshSmoke_emiter.fx', emitter(3, 160, (120, 120, 120), BACK, 0.45))
put('Weapon/Hit/BulletHitFleshSmoke_particle.fx',
    particle(0.45, [(0, 18), (0.45, 45)], tint([(0, 1, 1, 1, 0.35), (0.45, 1, 1, 1, 0)], MIST_TINT), 'IRN_BloodMist_particleBLEND.mat',
             '2, 2, 4', grav=(0.05, 0.05), drag=(3, 3)))

# --- spawned by irancojfx.dll (no game table names these moments: see IranCoJMods_Sc/Graphics_mod/irancoj_gore.cpp) --
# Each is spawned with the world's up as its local +Y (drips, pools) or with the flesh hit's own direction (headshot).
trace_mat('IRN_BloodPool_trace', 'IRN_BloodPool.dds', 'pools of blood under bodies')
trace_mat('IRN_BloodDripSplat_trace', 'IRN_BloodDripSplat.dds', 'drops of blood fallen to the ground (wet beads)')
put('IranCoJGore/IRN_BloodDrip_trace.fx', trace((4, 9), 30, 300, 'IRN_BloodDripSplat_trace.mat', fade=8, fade_in=0.25))
put('IranCoJGore/IRN_BloodPool_trace.fx', trace((35, 60), 45, 120, 'IRN_BloodPool_trace.mat', fade=12, fade_in=0.6))

# A wounded player drips from his wounds: drops let go one after another, falling and landing as small wet beads (a
# trail as he moves). Each drop is the falling-drop sprite - a round head and the blur of its fall - drawn upright and
# facing the camera (Trail() drops from this slow, continuous, world-space emitter never showed in the air; the round
# drop sprite at 6-9 cm looked cartoony). Light wounds trickle; three hits and more run as a heavier, longer stream
# (irancoj_gore.cpp picks by his hits).
fx_mat('IRN_BloodFall_particleBLEND', 'IRN_BloodFall.dds', 'a falling drop (its head and the blur of its fall)')


def drip(name, rate, speed, size, note):
    put('IranCoJGore/%s_emiter.fx' % name, 'EmiterDef()\n{\n\tSpace("world")\n\n' + keys('LifeTime', [(0, 1.8)]) +
        '\n\tGenType("continous")\n\n' + keys('ParticleRate', rate) + '\n' +
        keys('StartVelocity', [(0, speed)]) + '\n' + keys('StartVelocityRand', [(0, 10, 20, 10)], 'keyv') + '\n' +
        keys('Direction', [(0, 0, -1, 0)], 'keyv') + '\n\tGenArea("point")\n\n'
        '\tCollisionAction("spawn_fx")\n\t{\n\t\tTrace("IRN_BloodDrip_trace.fx")\n\t\tProbability(1)\n\t}\n}\n')
    put('IranCoJGore/%s_particle.fx' % name,
        particle(1.2, [(0,) + size], tint([(0, 1, 1, 1, 1), (1.2, 1, 1, 1, 0.95)], 0.8), 'IRN_BloodFall_particleBLEND.mat',
                 '4, 1, 4', grav=(1.0, 1.0), drag=(0.05, 0.1), aspect=(0.22, 0.28), spin=False))
    put('IranCoJGore/%s_sequence.fx' % name, 'SequenceDef()\n{\n' + keys('LifeTime', [(0, 1.8)]) + '\n\tRepeat(1)\n'
        '\n\tDelay(0)\n\n\tSpawn()\n\t{\n\t\tParticleEmiter("%s_emiter.fx", "%s_particle.fx")    // IranCoJ Gore: %s\n\t}\n}\n'
        % (name, name, note))


# A fresh wound pulses with the heartbeat: on every beat a jet out of it (spawned along the way out of the wound, its
# local +Y, aimed a little differently each beat by irancoj_gore.cpp), arcing down under gravity and landing as beads
# away from the body - strong for the first seconds, then weaker, then only the drips. A stream, not drops hanging in
# the air (the upright falling-drop sprite always points down - right for a slow drip only), and not a handful of
# pieces (a one-time burst of 8-12 read as steps): the wound pours for the length of the pulse - thin overlapping
# streaks at a high rate, each drawn along its flight (Align, aligned material) - its force dying within the pulse, so
# the stream is one unbroken line that arcs down, thins out and falls short at its end. Local space: the stream leaves
# along the way out of the wound.
def spurt(name, speed, rate, pulse, note):
    put('IranCoJGore/%s_emiter.fx' % name, 'EmiterDef()\n{\n' + keys('LifeTime', [(0, pulse + 1.4)]) +
        '\n\tGenType("continous")\n\n' + keys('ParticleRate', [(0, rate), (pulse * 0.8, rate * 0.75), (pulse, 0)]) + '\n' +
        keys('StartVelocity', [(0, speed), (pulse * 0.5, speed * 0.85), (pulse, speed * 0.6)]) + '\n' +
        keys('StartVelocityRand', [(0, speed * 0.04, speed * 0.05, speed * 0.04)], 'keyv') + '\n' +
        keys('Direction', [(0,) + BACK], 'keyv') + '\n\tGenArea("point")\n\n'
        '\tCollisionAction("spawn_fx")\n\t{\n\t\tTrace("IRN_BloodDrip_trace.fx")\n\t\tProbability(0.25)\n\t}\n}\n')
    put('IranCoJGore/%s_sequence.fx' % name, 'SequenceDef()\n{\n' + keys('LifeTime', [(0, pulse + 1.4)]) + '\n\tRepeat(1)\n'
        '\n\tDelay(0)\n\n\tSpawn()\n\t{\n\t\tParticleEmiter("%s_emiter.fx", "IRN_GoreSpurtStreak_particle.fx")    // IranCoJ Gore: %s\n\t}\n}\n'
        % (name, note))


put('IranCoJGore/IRN_GoreSpurtStreak_particle.fx',
    particle(1.4, [(0, 8, 12)], tint([(0, 1, 1, 1, 1), (0.6, 1, 1, 1, 0.9), (1.4, 1, 1, 1, 0.6)], 0.75),
             'IRN_BloodLine_particleBLEND.mat', '4, 1, 4', grav=(1.0, 1.1), drag=(0.3, 0.5), trail=True, aspect=(0.2, 0.3)))
spurt('IRN_GoreSpurt', 190, 160, 0.18, 'a jet with the heartbeat (fresh wound)')
spurt('IRN_GoreSpurtWeak', 110, 110, 0.14, 'a weaker jet (the pressure dropping)')

drip('IRN_GoreDrip',[(0, 22), (0.35, 16), (0.4, 0)], 70, (4, 7), 'a trickle from a wound')
drip('IRN_GoreDripHeavy', [(0, 40), (0.6, 30), (0.7, 0)], 110, (5, 8), 'a stream from bad wounds')

# A body: blood pours out and spreads - drops let fall from the body to the ground beneath (unseen: only where they land
# matters), further out as it goes on (the throw widens over the emitter's life), each laying a piece of the pool that
# soaks in - many small pieces, so the pool grows instead of popping in. Quick: all of it within about 1.5 s (at 5 s the
# game took the body away while its pool was still growing).
pool_e = ('EmiterDef()\n{\n\tSpace("world")\n\n' + keys('LifeTime', [(0, 2.5)]) + '\n\tGenType("continous")\n\n' +
          keys('ParticleRate', [(0, 30), (0.7, 24), (1.3, 14), (1.5, 0)]) + '\n' + keys('StartVelocity', [(0, 30)]) + '\n' +
          keys('StartVelocityRand', [(0, 15, 0, 15), (0.6, 45, 0, 45), (1.4, 85, 0, 85)], 'keyv') + '\n' +
          keys('Direction', [(0, 0, -1, 0)], 'keyv') +
          '\n\tGenArea("point")\n\n\tCollisionAction("spawn_fx")\n\t{\n\t\tTrace("IRN_BloodPool_trace.fx")\n\t\tProbability(1)\n\t}\n}\n')
put('IranCoJGore/IRN_GorePool_emiter.fx', pool_e)
put('IranCoJGore/IRN_GorePool_particle.fx',
    particle(1.0, [(0, 4)], [(0, 1, 1, 1, 0), (1.0, 1, 1, 1, 0)], 'IRN_BloodDrop_particleBLEND.mat', '2, 2, 4', grav=(1.5, 1.5),
             drag=(0.5, 0.5)))
put('IranCoJGore/IRN_GorePool_sequence.fx', 'SequenceDef()\n{\n' + keys('LifeTime', [(0, 2.5)]) + '\n\tRepeat(1)\n'
    '\n\tDelay(0)\n\n\tSpawn()\n\t{\n\t\tParticleEmiter("IRN_GorePool_emiter.fx", "IRN_GorePool_particle.fx")    // IranCoJ Gore: a pool spreading under a body\n\t}\n}\n')

# A headshot: on top of the hit's own layers, two more streams, a heavy spray of streaks, clusters and gobs that splat behind the
# head, more streaks and a short red puff (gone in half a second: it must never hide anyone).
headshot = [
    ('IRN_HeadGush', emitter(2, 320, (120, 120, 120), EXIT, 2.2), 'IRN_BloodGush', 'two more streams'),
    ('IRN_HeadSpray', emitter((12, 16), 450, (200, 260, 200), EXIT, 1.4, 'IRN_BloodDrip_trace.fx', 0.6),
     'IRN_BloodSpray', 'a heavy spray of streaks'),
    ('IRN_HeadClusters', emitter((18, 26), 600, (220, 260, 220), EXIT, 1.8, 'IRN_BloodSplatter_trace.fx', 0.6),
     'IRN_BloodCluster', 'a wide throw of drop clusters'),
    ('IRN_HeadGobs', emitter(12, 420, (220, 260, 220), EXIT, 1.5, 'IRN_BloodSplatter_trace.fx', 0.7),
     'BulletHitFleshDirt', 'heavy gobs'),
    ('IRN_HeadLines', emitter((5, 7), 330, (320, 80, 320), EXIT, 1.5), 'IRN_BloodLine', 'more streaks'),
    ('IRN_HeadPuff', emitter(3, 380, (240, 240, 240), EXIT, 0.5),
     particle(0.5, [(0, 36, 50)], tint([(0, 1, 1, 1, 0.25), (0.03, 1, 1, 1, 0.45), (0.25, 1, 1, 1, 0.3), (0.5, 1, 1, 1, 0)], MIST_TINT),
              'IRN_BloodMist_particleBLEND.mat', '2, 2, 4', grav=(0, 0), drag=(6, 10)), 'a short red puff'),
]
seq = 'SequenceDef()\n{\n' + keys('LifeTime', [(0, 1.8)]) + '\n\tRepeat(1)\n'
for name, e, p, note in headshot:
    put('IranCoJGore/%s_emiter.fx' % name, e)
    if not p.startswith('ParticleDef'):   # another layer's particle, by name
        part = p
    else:
        put('IranCoJGore/%s_particle.fx' % name, p)
        part = name
    seq += '\n\tDelay(0)\n\n\tSpawn()\n\t{\n\t\tParticleEmiter("%s_emiter.fx", "%s_particle.fx")    // IranCoJ Gore: %s\n\t}\n' % (name, part, note)
put('IranCoJGore/IRN_GoreHeadshot_sequence.fx', seq + '}\n')

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
