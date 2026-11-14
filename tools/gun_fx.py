"""Writes IranCoJ Graphics' gunfire effects: black-powder muzzle flashes and smoke (all authored here).

The game fires a sequence per weapon (WeaponsParams.scr FXFireName "Schofield#Schofield#aishot": first person, third
person, AI) and a lingering barrel smoke (FXFireBarrelName "schofieldSmoke3s#..."). These replace them by name:
  - a flash: a short additive bloom from the flash atlas, sized by the gun (derringer .. shotgun)
  - embers: a few sparks stretched along their flight
  - the black-powder cloud: puffs blasted downrange that billow, rise and are gone in about a second (the smoke flipbook
    plays over each puff's life): a brief puff, then nearly invisible - longer or thicker smoke hung in the sightline
  - the barrel wisps: a thin smoke trickling from the barrel for a couple of seconds
Vanilla barrel effects fire along the emitter's local -X in world space; that is kept.

usage: python tools/gun_fx.py mods/IranCoJGraphics        (writes <mod>/CoJ2/Data/FX/...)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gore_fx import keys  # noqa: E402  (the same writer helpers)

N = '\r\n'
files = {}
BARREL = (-1, 0, 0)


def put(rel, text):
    files[rel] = text.strip('\n').replace('\n', N) + N


def fx_mat(name, tex, blend, note):
    put('IranCoJGuns/%s.mat' % name, '''
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


fx_mat('IRN_MuzzleFlash_particleADD', 'IRN_MuzzleFlash.dds', 'e_bm_add', 'the muzzle flash')
fx_mat('IRN_GunSmoke_particleBLEND', 'IRN_SmokeAnim.dds', 'e_bm_lerp', 'black-powder smoke (a flipbook, lit by the scene)')


def emitter(count, speed, rand, life, direction=BARREL, continuous=None, position=None):
    e = 'EmiterDef()\n{\n\tSpace("world")\n\n' + keys('LifeTime', [(0, life)]) + '\n'
    if continuous:
        e += '\tGenType("continous")\n\n' + keys('ParticleRate', continuous)
    else:
        e += '\tGenType("one_time")\n\n' + keys('NumParticles', [(0, count)])
    e += '\n' + keys('StartVelocity', [(0, speed)]) + '\n' + keys('StartVelocityRand', [(0,) + rand], 'keyv')
    if position:
        e += '\n' + keys('Position', [(0,) + position], 'keyv')
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


# per gun class: flash size (start, end), smoke puffs, throw speed, puff size (start, swell, end), smoke life, embers
CLASSES = {
    'derringer': dict(flash=(10, 22), puffs=3, speed=650, size=(8, 22, 55), life=0.8, embers=5),
    'pistol':    dict(flash=(14, 30), puffs=5, speed=800, size=(10, 28, 70), life=0.9, embers=8),
    'rifle':     dict(flash=(20, 40), puffs=6, speed=950, size=(12, 34, 85), life=1.0, embers=10),
    'shotgun':   dict(flash=(30, 60), puffs=8, speed=1000, size=(16, 45, 105), life=1.2, embers=16),
    'gatling':   dict(flash=(16, 30), puffs=2, speed=600, size=(10, 26, 55), life=0.8, embers=3),   # fires fast
}
# the game's fire sequences (FXFireName) by gun class
GUNS = {
    'gun': 'pistol',   # the Peacemaker's (the game ships no gun_sequence: it had no muzzle effect)
    'Border': 'pistol', 'Schofield': 'pistol', 'Walker': 'pistol', 'cogswell': 'pistol', 'aishot': 'pistol',
    'Peacemaker': 'pistol', 'Classic': 'pistol', 'Ranger': 'pistol',
    'Derringer': 'derringer',
    'Rifle': 'rifle', 'Springfield': 'rifle', 'Sharps': 'rifle', 'AISpringfield': 'rifle', 'LegoSpringfield': 'rifle',
    'Shotgun': 'shotgun', 'ShotgunShort': 'shotgun',
    'Gatling': 'gatling',
}

for cls, c in CLASSES.items():
    name = 'IRN_Gun_%s' % cls
    put('IranCoJGuns/%sFlash_emiter.fx' % name, emitter(2, 0, (0, 0, 0), 0.07))
    put('IranCoJGuns/%sFlash_particle.fx' % name, particle(
        0.07, [(0, c['flash'][0]), (0.07, c['flash'][1])], [(0, 1, 1, 1, 1), (0.03, 1, 1, 1, 0.8), (0.07, 1, 1, 1, 0)],
        'IRN_MuzzleFlash_particleADD.mat', '2, 2, 4', '"random_once", 1'))
    put('IranCoJGuns/%sEmbers_emiter.fx' % name, emitter(c['embers'], 700, (120, 260, 260), 0.4))
    put('IranCoJGuns/%sEmbers_particle.fx' % name, particle(
        0.4, [(0, 4, 0.03, 0)], [(0, 1, 0.85, 0.6, 1), (0.4, 1, 0.5, 0.2, 0)], 'Spark_particleADD.mat', None, None,
        grav=0.6, drag=1.5, trail=True, size_fn='keyv'))
    s0, s1, s2 = c['size']
    life = c['life']
    put('IranCoJGuns/%sSmoke_emiter.fx' % name, emitter(c['puffs'], c['speed'], (c['speed'] * 0.15, c['speed'] * 0.3, c['speed'] * 0.3), life))   # the emitter lives as long as its puffs (they die with it)
    put('IranCoJGuns/%sSmoke_particle.fx' % name, particle(
        life, [(0, s0), (0.3, s1), (life, s2)],
        # a brief puff, then nearly gone (about the game's own 0.8 s): longer or thicker smoke hung in the sightline
        # when firing from a standstill
        [(0, 0.86, 0.85, 0.83, 0), (0.04, 0.86, 0.85, 0.83, 0.25), (0.15, 0.86, 0.85, 0.83, 0.16),
         (life * 0.55, 0.86, 0.85, 0.83, 0.05), (life, 0.86, 0.85, 0.83, 0)],
        'IRN_GunSmoke_particleBLEND.mat', '4, 4, 16', '"forward", %g' % round(16 / life, 2),
        grav=-0.1, drag=2.5, wind=1.5))   # carried downrange with the blast (as real smoke is), rising

for gun, cls in GUNS.items():
    seq = 'SequenceDef()\n{\n' + keys('LifeTime', [(0, CLASSES[cls]['life'])]) + '\n\tRepeat(1)\n'
    parts = [('Flash', 'the flash'), ('Embers', 'embers'), ('Smoke', 'the black-powder cloud')]
    if cls in ('rifle', 'shotgun'):   # these guns have no barrel smoke of their own (WeaponsParams): wisps at the muzzle
        parts.append(('Wisps', 'wisps from the muzzle'))
    for part, note in parts:
        n = 'IRN_Gun_%s%s' % (cls, part)
        seq += '\n\tDelay(0)\n\n\tSpawn()\n\t{\n\t\tParticleEmiter("%s_emiter.fx", "%s_particle.fx")    // IranCoJ Graphics: %s\n\t}\n' % (n, n, note)
    put('FX360/szliniutest/guns/%s_sequence.fx' % gun, seq + '}\n')

# the barrel wisps (FXFireBarrelName): a thin smoke trickling from the muzzle (the game's own offsets put it 10-30 cm
# back along the gun, out of the body - asked for at the muzzle); the emitter outlives the trickle by the wisps' life
WISPS = {'gunsmoke3s': 3.0, 'SchofieldSmoke3s': 2.0, 'WalkerSmoke3s': 3.0, 'derringerSmoke3s': 3.0, 'derringersmoke4s': 2.0,
         'IranCoJGuns/IRN_Gun_rifleWisps': 1.5, 'IranCoJGuns/IRN_Gun_shotgunWisps': 1.8}
for name, life in WISPS.items():
    path = name if '/' in name else 'FX360/szliniutest/guns/' + name
    put('%s_emiter.fx' % path, emitter(
        0, 8, (4, 4, 4), life + 2.0, direction=(0, 0, 1), continuous=[(0, 7), (life * 0.6, 4), (life * 0.75, 0)]))
    put('%s_particle.fx' % path, particle(
        2.0, [(0, 3), (2.0, 20)], [(0, 0.88, 0.87, 0.85, 0), (0.1, 0.88, 0.87, 0.85, 0.18), (2.0, 0.88, 0.87, 0.85, 0)],
        'IRN_GunSmoke_particleBLEND.mat', '4, 4, 16', '"forward", 8', grav=-0.06, drag=2.0, wind=1.0))

# The repeat/reload smoke (FXRepeteSeqName / FXReloadSeqName): working a lever or breaking a shotgun after a shot puffs a
# little smoke from the action - restyled to the same small, faint, quick puff (the game's own read as an extra cloud).
for name in ('rifleReload', 'volcanicReload', 'SharpsReload', 'shotgunreload', 'shotgunshortreload'):
    put('FX360/szliniutest/guns/%s_emiter.fx' % name, emitter(3, 60, (40, 40, 40), 0.9, direction=(0, 0, 1)))
    put('FX360/szliniutest/guns/%s_particle.fx' % name, particle(
        0.9, [(0, 6), (0.9, 26)], [(0, 0.88, 0.87, 0.85, 0), (0.06, 0.88, 0.87, 0.85, 0.16), (0.9, 0.88, 0.87, 0.85, 0)],
        'IRN_GunSmoke_particleBLEND.mat', '4, 4, 16', '"forward", 18', grav=-0.08, drag=3.0, wind=1.0))

# The older per-gun barrel effects (Weapon/Barrel/<gun>Comb and <gun>Smoke, see the game's readme there): silenced, so no
# vanilla flash or smoke ever plays next to these. The cannon keeps its own.
OLD_BARREL = ['PistolBulletTime', 'PistolDerringer', 'PistolFrontier', 'PistolLemant', 'PistolPeacemaker', 'PistolSchofield',
              'PistolVolcanic', 'PistolWalker', 'RifleCogswell', 'RifleLemant', 'RifleWinchester', 'RifleWinchesterScope',
              'ShotgunRemington', 'ShotgunRemingtonSawOff']
for gun_name in OLD_BARREL:
    for part in ('Comb', 'Smoke'):
        put('Weapon/Barrel/%s%s_emiter.fx' % (gun_name, part), emitter(0, 0, (0, 0, 0), 0.1))

if __name__ == '__main__':
    fx = os.path.join(sys.argv[1], 'CoJ2', 'Data', 'FX')
    for rel, text in files.items():
        p = os.path.join(fx, rel.replace('/', os.sep))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='latin1', newline='').write(text)
    print(len(files), 'files')
