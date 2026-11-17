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
# the burst (2026-11-17, after CoJ Gunslinger): big sprites laid along their flight - clusters of drops and splats
fx_mat('IRN_BloodClusterWS_particleBLEND', 'IRN_BloodCluster.dds', 'a cluster of drops flying out (drawn along its flight)', aligned=True)
fx_mat('IRN_BloodSplatWS_particleBLEND', 'IRN_BloodSplat.dds', 'a splash flying out (drawn along its flight)', aligned=True)


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
put('IranCoJGore/IRN_BloodSplatter_trace.fx', trace((16, 40), 25, 400, 'IRN_BloodSplat_trace.mat', fade=8))
for srf in ('Ground', 'Wood', 'Stone', 'Metal'):
    put('Weapon/Hit/BulletBloodTrace%s_trace.fx' % srf, trace((40, 90), 40, 60, 'IRN_BloodSplat_trace.mat', fade=10))
put('Weapon/Hit/BulletHitFleshTrace.fx', trace((5, 8), 30, 60, 'IRN_Wound_trace.mat', fade=8))
put('Weapon/Hit/BulletTraceFlesh_trace.fx', trace((5, 8), 30, 60, 'IRN_Wound_trace.mat', fade=8))


# --- emitters and particles ----------------------------------------------------------------------------------------
EXIT = (0, -1, 0)   # the hit's local -Y: out of the exit side, away from the shooter
BACK = (0, 1, 0)


def emitter(count, speed, rand, direction, life, trace_fx=None, probability=0.0, pos=None):
    """pos: where the particles start, in the hit's local space (the burst's big sprites start a little out of the body,
    so they do not cover it)."""
    e = 'EmiterDef()\n{\n' + keys('LifeTime', [(0, life)]) + '\n\tGenType("one_time")\n\n'
    e += keys('NumParticles', [(0,) + (count if isinstance(count, tuple) else (count,))], 'randf' if isinstance(count, tuple) else 'keyf')
    e += '\n' + keys('StartVelocity', [(0, speed)]) + '\n' + keys('StartVelocityRand', [(0,) + rand], 'keyv')
    if pos:
        e += '\n' + keys('Position', [(0,) + pos], 'keyv')
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


def gs_fade(life, k=DROP_TINT, peak=1.0):
    """The burst's fade (after CoJ Gunslinger): solid for a blink, half gone in a quarter of a second, then a faint
    trace while it falls and grows."""
    pts = [(0, peak), (0.17, peak * 0.86), (0.27, peak * 0.53), (0.47, peak * 0.25), (1.0, peak * 0.12)]
    pts = [p for p in pts if p[0] < life * 0.8] + [(life * 0.8, peak * 0.1), (life, 0)]
    return tint([(t, 1, 1, 1, a) for t, a in pts], k)


def sequence(path, life, spawns):
    """spawns: (emitter name, particle name, note, probability)"""
    s = 'SequenceDef()\n{\n' + keys('LifeTime', [(0, life)]) + '\n\tRepeat(1)\n'
    for e, p, note, prob in spawns:
        s += '\n\tDelay(0)\n\n\tSpawn()\n\t{\n\t\tParticleEmiter("%s_emiter.fx", "%s_particle.fx")    // IranCoJ Gore: %s\n' % (e, p, note)
        if prob < 1:
            s += '\t\tProbability(%g)\n' % prob
        s += '\t}\n'
    put(path, s + '}\n')


def build(path, life, layers):
    """layers: (name, emitter text or None, particle text or another layer's name, note, probability)"""
    spawns = []
    for name, e, p, note, prob in layers:
        if e:
            put('IranCoJGore/%s_emiter.fx' % name, e)
        if p.startswith('ParticleDef'):
            put('IranCoJGore/%s_particle.fx' % name, p)
            part = name
        else:
            part = p
        spawns.append((name, part, note, prob))
    sequence(path, life, spawns)


# A hit is a burst, the way CoJ Gunslinger builds it (its fx studied, nothing of it shipped): a few big sprites laid along
# their flight - clusters of drops and splashes, 50-70 cm at the start, growing to 1.5-2 m while they fade - thrown out
# of the exit side, falling under up to twice the gravity and slowed by the air; a throw of a dozen or more smaller drop
# clusters; a few long streaks thrown wide; a quick puff of spray and a faint haze (gone in 0.7 s: never hides anyone).
# Solid for a blink, half gone in a quarter of a second: a pop of blood that arcs down, not a cloud. Everything that
# lands leaves its mark, as the bleeding does: big clusters a small puddle, drops splatters, streaks and the slow
# drops wet beads - blood all over the ground and walls around a fight.
CLUSTER = 'IRN_BloodClusterWS_particleBLEND.mat'
SPLASH = 'IRN_BloodSplatWS_particleBLEND.mat'
LINE = 'IRN_BloodLine_particleBLEND.mat'
MIST = 'IRN_BloodMist_particleBLEND.mat'
burst = [
    ('IRN_BurstCluster', emitter(1, 250, (0, 100, 0), EXIT, 3.0, 'IRN_BloodPuddle_trace.fx', 1, pos=(2, -45, 0)),
     particle(3.0, [(0, 60), (0.2, 70), (3.0, 180)], gs_fade(3.0), CLUSTER, '2, 2, 4', grav=(1.0, 1.4), drag=(1, 2),
              align=True, aspect=(0.5, 0.55)), 'a big cluster of drops flying out', 0.8),
    ('IRN_BurstClusterClose', emitter(1, 250, (0, 0, 0), EXIT, 2.0, 'IRN_BloodSplatter_trace.fx', 1, pos=(2, -25, 0)),
     particle(2.0, [(0, 52), (0.2, 64), (2.0, 150)], gs_fade(2.0), CLUSTER, '2, 2, 4', grav=(1.0, 1.4), drag=(1, 2),
              align=True, aspect=(0.5, 0.6)), 'the same, close to the body', 1),
    ('IRN_BurstCluster2', emitter(1, 250, (0, 0, 0), EXIT, 3.0, 'IRN_BloodPuddle_trace.fx', 1, pos=(2, 0, 0)),
     particle(3.0, [(0, 66), (0.19, 74), (3.0, 190)], gs_fade(3.0), CLUSTER, '2, 2, 4', grav=(1.0, 1.4), drag=(1, 2),
              align=True, aspect=(0.3, 0.4)), 'a second, narrower cluster', 1),
    ('IRN_BurstSplash', emitter(1, 550, (0, 0, 0), EXIT, 1.5, 'IRN_BloodSplatter_trace.fx', 0.8, pos=(0, 15, 0)),
     particle(1.5, [(0, 42), (1.5, 74)], gs_fade(1.5, peak=0.46), SPLASH, '2, 2, 4', grav=(1.6, 1.8), drag=(9, 10),
              align=True, aspect=(1, 1)), 'a splash bursting out (stops in the air)', 1),
    ('IRN_BurstSplashClose', emitter(1, 250, (0, 0, 0), EXIT, 0.7, 'IRN_BloodDrip_trace.fx', 1, pos=(0, -25, 0)),
     particle(0.7, [(0, 20), (0.7, 60)], gs_fade(0.7, peak=0.5), SPLASH, '2, 2, 4', grav=(0.4, 0.6), drag=(1, 2),
              align=True, aspect=(0.6, 0.6)), 'a splash at the wound', 1),
    ('IRN_BurstDrops', emitter((12, 22), 550, (55, 250, 55), EXIT, 2.0, 'IRN_BloodSplatter_trace.fx', 0.6, pos=(2, 0, 0)),
     particle(2.0, [(0, 34), (0.42, 42), (2.0, 68)], gs_fade(2.0), CLUSTER, '2, 2, 4', grav=(1.5, 2.0), drag=(1, 2),
              align=True, aspect=(1, 1)), 'a throw of drops', 1),
    ('IRN_BurstDropsClose', emitter((6, 10), 400, (40, 150, 40), EXIT, 1.5, 'IRN_BloodDrip_trace.fx', 1, pos=(2, 0, 0)),
     particle(1.5, [(0, 30), (1.5, 55)], gs_fade(1.5), CLUSTER, '2, 2, 4', grav=(0.7, 1.0), drag=(3, 4),
              align=True, aspect=(0.5, 1)), 'a slower throw of drops', 1),
    ('IRN_BurstLines', emitter((2, 5), 255, (255, 0, 255), EXIT, 1.5, 'IRN_BloodDrip_trace.fx', 0.7, pos=(2, 0, 0)),
     particle(1.5, [(0, 55, 85)], gs_fade(1.5), LINE, '4, 1, 4', grav=(0.7, 1.0), drag=(1, 2), align=True,
              aspect=(0.1, 0.2)), 'streaks thrown wide', 1),
    ('IRN_BurstLinesClose', emitter((2, 5), 122, (333, 0, 0), EXIT, 1.5, 'IRN_BloodDrip_trace.fx', 0.7, pos=(2, 0, 0)),
     particle(1.5, [(0, 45, 55)], gs_fade(1.5), LINE, '4, 1, 4', grav=(0.7, 1.0), drag=(3, 4), align=True,
              aspect=(0.1, 0.2)), 'short streaks', 1),
    ('IRN_BurstPuff', emitter(6, 300, (200, 200, 200), EXIT, 0.7),
     particle(0.7, [(0, 36, 50)], tint([(0, 1, 1, 1, 0.17), (0.03, 1, 1, 1, 0.36), (0.39, 1, 1, 1, 0.39), (0.7, 1, 1, 1, 0)], MIST_TINT),
              MIST, '2, 2, 4', grav=(0, 0), drag=(5, 10)), 'a puff of spray', 1),
    ('IRN_BurstHaze', emitter(6, 1400, (200, 200, 200), EXIT, 0.7),
     particle(0.7, [(0, 100, 140)], tint([(0, 1, 1, 1, 0.015), (0.012, 1, 1, 1, 0.12), (0.4, 1, 1, 1, 0.074), (0.7, 1, 1, 1, 0)], MIST_TINT),
              MIST, '2, 2, 4', grav=(0, 0), drag=(10, 15)), 'a faint red haze', 1),
]
build('FX360/szliniutest/gun_hits/Hitflesh_sequence.fx', 3.0, burst)

# The shotgun's flesh hit (its own hit table below): every pellet that lands spawns one, so a close blast is 8+ of these
# together - per pellet a smaller burst (drops, streaks, sometimes a splash or a cluster, a light puff, no haze: eight
# full bursts were a red wall). The particles are the burst's; only the emitters differ.
pellet = [
    ('IRN_BurstDropsPellet', emitter((5, 8), 480, (60, 220, 60), EXIT, 2.0, 'IRN_BloodSplatter_trace.fx', 0.5, pos=(2, 0, 0)),
     'IRN_BurstDrops', 'a throw of drops', 1),
    ('IRN_BurstSplash', None, 'IRN_BurstSplash', 'a splash', 0.5),
    ('IRN_BurstLinesPellet', emitter((1, 3), 255, (255, 0, 255), EXIT, 1.5, 'IRN_BloodDrip_trace.fx', 0.7, pos=(2, 0, 0)), 'IRN_BurstLines', 'streaks', 1),
    ('IRN_BurstClusterClose', None, 'IRN_BurstClusterClose', 'a cluster', 0.3),
    ('IRN_BurstPuffPellet', emitter(3, 300, (200, 200, 200), EXIT, 0.7), 'IRN_BurstPuff', 'a light puff', 1),
]
build('FX360/szliniutest/gun_hits/RemingtonHit/SHitFlesh_sequence.fx', 2.0, pellet)
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
put('IranCoJGore/IRN_BloodDrip_trace.fx', trace((4, 9), 30, 500, 'IRN_BloodDripSplat_trace.mat', fade=8, fade_in=0.25))
# where a big cluster of the burst lands: a small puddle that soaks in (the pool's texture, smaller)
put('IranCoJGore/IRN_BloodPuddle_trace.fx', trace((25, 45), 35, 160, 'IRN_BloodPool_trace.mat', fade=10, fade_in=0.4))
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

# A headshot: on top of the hit's own burst, a wider throw of drops, another big cluster, two more splashes, heavy gobs
# that splat behind the head, more streaks and a short red puff (gone in half a second: it must never hide anyone).
headshot = [
    ('IRN_HeadDrops', emitter((18, 26), 600, (220, 260, 220), EXIT, 2.0, 'IRN_BloodSplatter_trace.fx', 0.8, pos=(2, 0, 0)),
     'IRN_BurstDrops', 'a wide throw of drops', 1),
    ('IRN_HeadCluster', emitter(1, 300, (0, 120, 0), EXIT, 3.0, 'IRN_BloodPuddle_trace.fx', 1, pos=(2, -40, 0)),
     'IRN_BurstCluster2', 'another big cluster', 1),
    ('IRN_HeadSplash', emitter(2, 600, (120, 0, 120), EXIT, 1.5, 'IRN_BloodSplatter_trace.fx', 0.8, pos=(0, 10, 0)), 'IRN_BurstSplash', 'two more splashes', 1),
    ('IRN_HeadGobs', emitter(12, 420, (220, 260, 220), EXIT, 1.5, 'IRN_BloodSplatter_trace.fx', 0.7),
     'BulletHitFleshDirt', 'heavy gobs', 1),
    ('IRN_HeadLines', emitter((5, 7), 330, (320, 80, 320), EXIT, 1.5, 'IRN_BloodDrip_trace.fx', 0.7), 'IRN_BurstLines', 'more streaks', 1),
    ('IRN_HeadPuff', emitter(3, 380, (240, 240, 240), EXIT, 0.5),
     particle(0.5, [(0, 36, 50)], tint([(0, 1, 1, 1, 0.25), (0.03, 1, 1, 1, 0.45), (0.25, 1, 1, 1, 0.3), (0.5, 1, 1, 1, 0)], MIST_TINT),
              MIST, '2, 2, 4', grav=(0, 0), drag=(6, 10)), 'a short red puff', 1),
]
build('IranCoJGore/IRN_GoreHeadshot_sequence.fx', 3.0, headshot)

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
