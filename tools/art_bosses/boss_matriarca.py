import math
import numpy as np
from kit import *
from shapes import *
from anim import *
from fxlib import *
from boss_common import *

SKIN = auto('#c2b6d2', shadow=(64, 40, 116), warm=(255, 232, 226), n=6, dk=0.3, boost=1.15)
DRESS = auto('#9a1830', shadow=(34, 8, 56), warm=(255, 120, 112), n=6, dk=0.24)
DRESSD = auto('#4a0c22', shadow=(20, 6, 50), warm=(190, 60, 90), n=6, dk=0.3)
BLACK = auto('#2a1e36', shadow=(10, 6, 40), warm=(150, 110, 190), n=6, dk=0.3)
WING = auto('#6a1436', shadow=(24, 6, 52), warm=(230, 90, 120), n=6, dk=0.26)
WINGB = auto('#3a1a2c', shadow=(14, 8, 40), warm=(190, 120, 150), n=6, dk=0.3)
GOLD = auto('#c4a24c', shadow=(60, 26, 60), warm=(255, 244, 170), n=6)
CLAW = auto('#e8dcd0', shadow=(90, 40, 90), warm=(255, 255, 240), n=6, dk=0.4)
LIP = auto('#7a1a38', shadow=(30, 8, 50), warm=(220, 90, 110), n=6)
BLOODG = [(60, 6, 20), (150, 16, 44), (232, 44, 76), (255, 150, 150), (255, 240, 236)]
MATS = {'skin': Mat(SKIN, texamt=0.4, gain=1.1), 'dress': Mat(DRESS, texamt=0.65, gain=1.0), 'dressd': Mat(DRESSD, texamt=0.65, gain=0.9),
        'black': Mat(BLACK, texamt=0.7, gain=1.0), 'wing': Mat(WING, glow=BLOODG, texamt=0.7, gain=0.95), 'wingb': Mat(WINGB, texamt=0.5),
        'gold': Mat(GOLD, gain=1.3), 'claw': Mat(CLAW, gain=1.2), 'lip': Mat(LIP), 'eye': Mat(DRESS, glow=BLOODG, texamt=0.2),
        'gem': Mat(DRESS, glow=BLOODG, texamt=0.2)}


def scallop(p, q, depth, k=3, toward=(0, 0)):
    p = np.array(p, float); q = np.array(q, float)
    out = []
    d = q - p; L = np.hypot(*d) + 1e-6
    n = np.array([-d[1], d[0]]) / L
    c = np.array(toward, float) - (p + q) / 2
    if np.dot(n, c) < 0:
        n = -n
    for j in range(1, k * 2):
        t = j / (k * 2)
        # arco concavo hacia 'toward'
        out.append(tuple(p + d * t + n * depth * math.sin(t * math.pi)))
    return [tuple(p)] + out


def wing_parts(add, nm, z, dim, seed):
    wa = add('wa_' + nm, 'torso', (-3, -27), z=z, mat='wingb', depth=2.2, noise=0.2, seed=seed, dim=dim)
    wa.tube([(0, 0), (-4, -13), (-10, -26)], 3.0, 2.0)
    wa.poly([(0, 2), (-10, -26), (4, 30), (2, 14)], mat='wing', raise_=-0.2)
    wa.line([(-2, -2), (-3, 30)], 0.8, op='tex', v=0.2)
    wf = add('wf_' + nm, 'wa_' + nm, (-10, -26), z=z + 0.01, mat='wing', depth=3.2, noise=0.4, seed=seed + 1, dim=dim, tnoise=0.3)
    F = [(-40, -36), (-60, -18), (-63, 6), (-50, 28)]
    body = (6, 64)
    pts = [(0, 0), F[0]]
    cen = (-26, 6)
    for a, b in zip(F[:-1], F[1:]):
        pts += scallop(a, b, 5.0, 2, cen)[1:]
    pts.append(F[-1])
    pts += scallop(F[-1], body, 6.0, 3, cen)[1:]
    pts.append(body); pts.append((12, 28))
    wf.poly(pts)
    for f in F:
        wf.tube([(0, 0), (f[0] * 0.5, f[1] * 0.5 - 3), f], 1.8, 0.6, mat='wingb', raise_=0.9, edge=0.1)
    wf.tube([(0, 0), (-16, -8), (-30, -10)], 2.6, 1.8, mat='wingb', raise_=0.9, edge=0.1)
    for k in range(6):
        wf.line([(-26 + k * 2, -8 + k * 4), (-8 + k * 2.5, 26 + k * 6)], 0.7, op='tex', v=0.2)
    wf.blotch('wingb', 0.78, 2.4, seed + 2)
    wf.cracks(3, 8, v=0.9, w=0.6, seed=seed + 3)
    wf.poly([(-44, -34), (-52, -44), (-40, -37)], mat='claw', raise_=0.5)
    return wf


def build_parts():
    P = []

    def add(*a, **k):
        p = Part(*a, **k); P.append(p); return p
    add('root', None, (96, 156), ghost=True)
    hip = add('hip', 'root', (0, -52), z=4, mat='dress', depth=4.5, noise=0.3, seed=5)
    hip.spl([(-8, -4), (8, -4), (10, 4), (-9, 5)])
    # faldas
    sk = add('skirt', 'hip', (0, 0), z=5, mat='dress', depth=6.0, noise=0.5, seed=6, tnoise=0.12)
    sk.spl([(-8, -2), (9, -2), (13, 10), (18, 26), (0, 27), (-19, 26), (-13, 10)])
    sk.hatch(3.4, 84, v=0.34, w=0.5, jit=0.4)
    sk.spl([(2, 0), (8, 0), (12, 12), (14, 26), (6, 26), (4, 12)], mat='dressd', raise_=0.4, edge=0.2)
    sk.line([(-3, 0), (-8, 26)], 0.7, op='tex', v=0.15)
    sk2 = add('skirt2', 'skirt', (0, 24), z=5, mat='dress', depth=5.0, noise=0.5, seed=8, tnoise=0.12)
    sk2.poly([(-20, -2), (19, -2), (22, 8)] + rag(22, -24, 18, 7, 10, 3, 1) + [(-23, 8)])
    sk2.hatch(3.4, 84, v=0.34, w=0.5, jit=0.4)
    sk2.spl([(4, -2), (14, -2), (18, 10), (20, 20), (10, 22)], mat='dressd', raise_=0.4, edge=0.2)
    sk2.blotch('dressd', 0.74, 2.4, 10)
    # torso
    to = add('torso', 'hip', (0, -2), z=6, mat='dress', depth=5.2, noise=0.3, seed=20, tnoise=0.2)
    to.spl([(-7, -1), (-8.5, -9), (-8, -20), (-5, -29), (0, -32), (6, -30), (8.5, -22), (8, -12), (6, -2)])
    to.spl([(0, -28), (6, -24), (7, -14), (5, -4), (1, -6), (0, -16)], mat='dressd', raise_=0.3, edge=0.2)
    for k in range(5):
        to.line([(-5, -5 - k * 4.4), (6, -7 - k * 4.4)], 0.6, op='tex', v=0.85)
    to.line([(1, -30), (1, -2)], 0.7, op='tex', v=0.1)
    to.spl([(2, -33), (8, -30), (9, -26), (3, -25)], mat='skin', raise_=0.4, edge=0.2)  # escote
    to.ell(2.5, -22, 1.8, 1.8, mat='gem', raise_=0.6, edge=0.1)
    to.ell(2.5, -22, 1.2, 1.2, op='emit', v=1.0, soft=0.3)
    wing_parts(add, 'b', 1.0, -0.28, 70)
    wing_parts(add, 'f', 2.0, -0.08, 80)
    # cuello y collar
    co = add('collar', 'torso', (-1, -29), z=3.5, mat='black', depth=3.0, noise=0.3, seed=24)
    co.poly([(-6, 4), (-16, -10), (-8, -24), (-4, -10), (1, -28), (3, -9), (9, -22), (9, 4)])
    co.spl([(-4, 2), (-8, -8), (-4, -16), (0, -8), (2, -4)], mat='dress', raise_=0.3, edge=0.2)
    # cabeza
    hd = add('head', 'torso', (2, -33), z=12, mat='skin', depth=6.5, noise=0.2, seed=30, tnoise=0.12)
    hd.spl([(-6, -2), (-7, -10), (-3, -16), (4, -17), (8, -12), (9.5, -6), (8.5, -2), (5.5, 2.5), (0, 3.5), (-4, 2)])
    hd.poly([(-1, 3), (3, 3), (3, 8), (-1, 8)], mat='skin')
    hd.poly([(2.4, -11.2), (9.4, -12.2), (9, -7.4), (2.6, -7)], mat='black', raise_=-0.4)
    hd.poly([(3.2, -10), (8.8, -10.8), (8.4, -8.6), (3, -8.2)], mat='eye', raise_=-0.2)
    hd.poly([(3.2, -10), (8.8, -10.8), (8.4, -8.6), (3, -8.2)], op='emit', v=0.7, soft=0.3)
    hd.line([(2, -12.5), (9, -12.8)], 0.9, op='tex', v=0.05)
    hd.line([(4, -0.4), (7.2, -0.8)], 1.0, op='tex', v=0.08)
    hd.poly([(4.2, 0.2), (7.2, -0.2), (5.8, 1.4)], mat='lip', raise_=0.2)
    hd.line([(5.0, 0.4), (5.2, 2.2)], 0.5, op='tex', v=0.95)
    hd.line([(-4, -6), (-1, -2)], 0.7, op='tex', v=0.2)
    hd.line([(8.6, -7), (9.6, -5)], 0.6, op='tex', v=0.1)
    ti = add('tiara', 'head', (1, -15), z=13, mat='gold', depth=1.8, noise=0.1, seed=33)
    ti.poly([(-6, 2), (-5, -1), (-3.5, -4), (-2, -1), (0, -7), (2, -1), (3.5, -4), (5, -1), (7, 2), (3, 3), (-3, 3)])
    ti.ell(0, 0.5, 1.2, 1.2, mat='gem'); ti.ell(0, 0.5, 0.9, 0.9, op='emit', v=1.0, soft=0.2)
    # pelo
    for nm, par, at, z, sd in (('hair1', 'head', (-4, -14), 4, 36), ('hair2', 'hair1', (-9, 14), 4, 37)):
        h = add(nm, par, at, z=z, mat='black', depth=3.4, noise=0.4, seed=sd, tnoise=0.3)
        if nm == 'hair1':
            h.spl([(6, -4), (-3, -6), (-10, 2), (-14, 14), (-12, 26), (-6, 24), (-2, 14), (2, 6), (8, 0)])
            h.hatch(2.0, 100, v=0.8, w=0.5, jit=0.5)
        else:
            h.poly([(4, -4), (-6, -3), (-12, 6), (-14, 16), (-9, 26), (-6, 18), (-4, 28), (-1, 14), (2, 4)])
            h.hatch(2.0, 100, v=0.8, w=0.5, jit=0.5)
    # brazos
    for nm, x, z, dim in (('b', -4, 3, -0.25), ('f', 5, 10, 0.0)):
        ua = add('uarm_' + nm, 'torso', (x, -27), z=z, mat='skin', depth=2.8, noise=0.2, seed=40, dim=dim, tnoise=0.1)
        ua.tube([(0, 0), (1, 8), (0.5, 16)], 2.8, 2.3)
        ua.spl([(-3.6, -3), (3.8, -3), (4.4, 6), (-3.6, 7)], mat='dress', raise_=0.7, edge=0.2)
        fa = add('farm_' + nm, 'uarm_' + nm, (0.5, 16), z=z, mat='skin', depth=2.6, noise=0.2, seed=41, dim=dim, tnoise=0.1)
        fa.tube([(0, 0), (0.3, 9), (0.3, 16)], 2.3, 1.8)
        fa.poly([(-3.2, 0), (3.2, 0), (5.5, 10), (6, 18)] + rag(6, -6, 19, 3, 5, 4 + (nm == 'f'), 1) + [(-6.5, 8)], mat='dress', raise_=0.8, edge=0.15)
        fa.hatch(2.4, 80, v=0.2, w=0.6, jit=0.4)
        hn = add('hand_' + nm, 'farm_' + nm, (0.3, 16), z=z + 0.2, mat='skin', depth=1.8, noise=0.1, seed=42, dim=dim)
        hn.spl([(-2.4, -1), (2.4, -1), (3.4, 4), (1.8, 8), (-1.8, 8), (-3, 4)])
        for k in range(4):
            xx = -2.0 + k * 1.35
            hn.poly([(xx - 0.6, 7), (xx + 0.6, 7), (xx + 0.4 + (k - 1.5) * 0.6, 17 + (k % 2) * 2.5)], mat='claw', raise_=0.5, edge=0.1)
    return P


H_ = lambda *a: {}
post = None


def make(anims, fxhook):
    return Boss('matriarca_sangre', (192, 160), (96, 156), (30, 100), build_parts(), MATS, anims, fxhook,
                outline=(14, 6, 20), rim=(255, 110, 150), rimk=0.4, dis_col=(255, 70, 90), seed=31, post=post, scale=1.0)


# ====================================================================== animaciones
def PZ(*ds):
    return merge(*ds)


def wings(o, fl=0.0, spread=0.0):
    """o: apertura 0 (plegadas contra la espalda) .. 1 (extendidas arriba/atras). fl: aleteo en grados."""
    a = -62 * (1 - o)
    f = -80 * (1 - o)
    return {'wa_f': a + fl, 'wf_f': f + fl * 1.4 + spread, 'wa_b': a * 0.9 + 8 - fl * 0.8, 'wf_b': f * 0.9 + 8 - fl * 1.1 + spread * 0.6}


def skirt(f, n, amp=1.0, base=0.0, ph=0.0):
    return {'skirt': base * 0.4 + amp * 2.0 * S(f, n, ph), 'skirt2': base + amp * 4.0 * S(f, n, ph + 0.14),
            'hair1': base * 0.5 + amp * 3.0 * S(f, n, ph + 0.2), 'hair2': amp * 5.0 * S(f, n, ph + 0.35)}


def arms(uf, ff, hf, ub, fb, hb):
    return {'uarm_f': uf, 'farm_f': ff, 'hand_f': hf, 'uarm_b': ub, 'farm_b': fb, 'hand_b': hb}


STAND = PZ(arms(-14, -30, -4, 10, -22, 0), {'head': -1, 'torso': 1}, wings(0.55))


def idle_pose(f):
    b = S(f, 6)
    return PZ(STAND, {'root.y': -4 - 1.8 * b, 'torso': 1.5 + 1.0 * b, 'head': -1.5 * b, 'uarm_f': -1.5 * b, 'farm_b': 1.5 * b},
              wings(0.55 + 0.05 * b, 3 * b), skirt(f, 6, 1.0, 1.5))


def walk_pose(f):
    ph = 2 * math.pi * f / 8
    s = math.sin(ph); c = math.cos(ph)
    return PZ(STAND, {'root.y': -5 - 2.5 * abs(s), 'torso': 8, 'hip': -2, 'head': -3 + 2 * c, 'uarm_f': -20 + 8 * s, 'farm_f': -34 + 6 * c,
                      'uarm_b': 18 - 8 * s}, wings(0.35 + 0.1 * c, 6 * s), skirt(f, 8, 1.8, 7))


WIND1 = [(0, STAND),
         (1, PZ(arms(-60, -50, -10, 14, -26, 0), {'torso': -3, 'root.y': -5, 'head': -4}, wings(0.8))),
         (2, PZ(arms(-120, -60, -20, 16, -30, 0), {'torso': -8, 'root.y': -7, 'head': -8}, wings(1.0))),
         (3, PZ(arms(-150, -50, -30, 18, -30, 0), {'torso': -12, 'root.y': -9, 'head': -10}, wings(1.0, -4))),
         (4, PZ(arms(-158, -48, -34, 18, -30, 0), {'torso': -14, 'root.y': -10, 'head': -11, 'root.x': -3}, wings(1.05, -6)))]
wind1k = K(WIND1)


def wind1(f):
    return PZ(wind1k(f), skirt(f, 5, 0.6, 3 + f))


ATK1 = [(0, WIND1[-1][1], 'sm'),
        (1, PZ(arms(-110, -64, -20, 16, -30, 0), {'torso': 4, 'root.y': -7, 'root.x': 4, 'head': 0}, wings(0.9, 6)), 'snap'),
        (2, PZ(arms(-50, -20, 10, 18, -34, 0), {'torso': 16, 'root.y': -5, 'root.x': 10, 'head': 6}, wings(0.7, 10)), 'snap'),
        (3, PZ(arms(-24, 0, 24, 18, -34, 0), {'torso': 22, 'root.y': -3, 'root.x': 14, 'head': 8}, wings(0.55, 8)), 'snap'),
        (4, PZ(arms(-18, 4, 30, 18, -34, 0), {'torso': 22, 'root.y': -3, 'root.x': 14, 'head': 8}, wings(0.5, 0)), 'out'),
        (5, PZ(arms(-18, -6, 20, 16, -30, 0), {'torso': 16, 'root.y': -4, 'root.x': 10, 'head': 5}, wings(0.5)), 'sm'),
        (6, PZ(arms(-14, -20, 6, 12, -24, 0), {'torso': 8, 'root.y': -4, 'root.x': 4}, wings(0.5)), 'sm'),
        (7, STAND, 'sm')]
atk1k = K(ATK1)


def atk1(f):
    return PZ(atk1k(f), skirt(f, 8, 1.6, 8 - f * 0.8, 0.2))


WIND2 = [(0, STAND),
         (1, PZ(arms(10, -16, 0, 30, -14, 0), {'torso': -6, 'root.y': -3, 'head': -3, 'root.x': -2}, wings(0.9))),
         (2, PZ(arms(22, -8, 4, 44, -6, 0), {'torso': -12, 'root.y': -2, 'head': -6, 'root.x': -6}, wings(1.1, 0, 10))),
         (3, PZ(arms(30, 0, 8, 52, 0, 0), {'torso': -16, 'root.y': -1, 'head': -8, 'root.x': -10}, wings(1.15, 0, 14))),
         (4, PZ(arms(34, 4, 10, 56, 4, 0), {'torso': -18, 'root.y': 0, 'head': -9, 'root.x': -13}, wings(1.15, -4, 16)))]
wind2k = K(WIND2)


def wind2(f):
    return PZ(wind2k(f), skirt(f, 5, 0.5, -2 - f * 2, 0.3))


ATK2 = [(0, WIND2[-1][1], 'sm'),
        (1, PZ(arms(-70, -20, 0, -56, -24, 0), {'torso': 34, 'root.y': -9, 'root.x': 20, 'head': 10, 'hip': 6}, wings(0.1, 0)), 'snap'),
        (2, PZ(arms(-82, -4, 0, -66, -10, 0), {'torso': 52, 'root.y': -10, 'root.x': 44, 'head': 12, 'hip': 10}, wings(0.0, 0)), 'snap'),
        (3, PZ(arms(-86, -2, 0, -70, -8, 0), {'torso': 54, 'root.y': -10, 'root.x': 54, 'head': 12, 'hip': 10}, wings(0.0, 0)), 'out'),
        (4, PZ(arms(-84, -2, 0, -68, -8, 0), {'torso': 52, 'root.y': -9, 'root.x': 56, 'head': 12, 'hip': 10}, wings(0.05, 0)), 'sm'),
        (5, PZ(arms(-70, -12, 0, -50, -14, 0), {'torso': 40, 'root.y': -8, 'root.x': 54, 'head': 10, 'hip': 8}, wings(0.2, 0)), 'sm'),
        (6, PZ(arms(-40, -20, 0, -20, -18, 0), {'torso': 22, 'root.y': -6, 'root.x': 34, 'head': 5, 'hip': 4}, wings(0.4, 0)), 'sm'),
        (7, STAND, 'sm')]
atk2k = K(ATK2)


def atk2(f):
    return PZ(atk2k(f), skirt(f, 8, 2.2, -16 + f * 2, 0.0))


WIND3 = [(0, STAND),
         (1, PZ(arms(10, -20, 0, 20, -20, 0), {'torso': 4, 'root.y': 2, 'head': 0, 'skirt2.sy': 0.9}, wings(0.3))),
         (2, PZ(arms(-30, -30, 0, -10, -30, 0), {'torso': -4, 'root.y': -10, 'head': -4}, wings(0.9, 6))),
         (3, PZ(arms(-100, -30, 0, -90, -30, 0), {'torso': -8, 'root.y': -18, 'head': -8}, wings(1.1, -8, 8))),
         (4, PZ(arms(-140, -20, 0, -130, -20, 0), {'torso': -10, 'root.y': -28, 'head': -10}, wings(1.15, 0, 10))),
         (5, PZ(arms(-160, -10, 0, -150, -12, 0), {'torso': -12, 'root.y': -32, 'head': -12}, wings(1.15, -6, 12)))]
wind3k = K(WIND3)


def wind3(f):
    return PZ(wind3k(f), skirt(f, 6, 1.0, 6 - f, 0.3))


ATK3 = [(0, WIND3[-1][1], 'sm'),
        (1, PZ(arms(-150, -14, 0, -140, -16, 0), {'torso': 10, 'root.y': -34, 'head': -4}, wings(1.0, 10, 10)), 'sm'),
        (2, PZ(arms(-50, -10, 20, -30, -14, 20), {'torso': 36, 'root.y': -24, 'root.x': 8, 'head': 8, 'hip': 6}, wings(0.7, 12)), 'in'),
        (3, PZ(arms(-14, 4, 30, -4, 4, 30), {'torso': 44, 'root.y': -8, 'root.x': 14, 'head': 12, 'hip': 8}, wings(0.5, 14)), 'in'),
        (4, PZ(arms(-6, 6, 36, 0, 6, 36), {'torso': 42, 'root.y': 6, 'root.x': 14, 'head': 12, 'hip': 8, 'skirt2.sy': 0.9}, wings(0.9, 0, 10)), 'snap'),
        (5, PZ(arms(-6, 8, 36, 0, 8, 36), {'torso': 36, 'root.y': 6, 'root.x': 14, 'head': 10, 'hip': 6}, wings(1.0, -4, 12)), 'sm'),
        (6, PZ(arms(-10, 0, 26, 0, 0, 26), {'torso': 28, 'root.y': 2, 'root.x': 12, 'head': 6}, wings(0.9, 0, 8)), 'sm'),
        (7, PZ(arms(-12, -14, 10, 4, -12, 4), {'torso': 14, 'root.y': -2, 'root.x': 6}, wings(0.7)), 'sm'),
        (8, PZ(STAND), 'sm')]
atk3k = K(ATK3)


def atk3(f):
    return PZ(atk3k(f), skirt(f, 9, 2.0, -12 if f in (1, 2, 3) else 8, 0.0))


CAST = K([(0, STAND),
          (1, PZ(arms(-50, -50, 0, -30, -50, 0), {'torso': -4, 'root.y': -6, 'head': -4}, wings(0.8))),
          (2, PZ(arms(-100, -40, 10, -90, -40, 10), {'torso': -8, 'root.y': -10, 'head': -8}, wings(1.0, 4)), 'sm'),
          (3, PZ(arms(-110, -30, 20, -106, -30, 20), {'torso': -10, 'root.y': -12, 'head': -10}, wings(1.1, -4, 8)), 'sm'),
          (4, PZ(arms(-70, -20, 30, -64, -20, 30), {'torso': 4, 'root.y': -10, 'root.x': 3, 'head': 2}, wings(0.9, 6)), 'snap'),
          (5, PZ(arms(-56, -14, 30, -50, -14, 30), {'torso': 6, 'root.y': -8, 'root.x': 3}, wings(0.8, 0)), 'out'),
          (6, PZ(arms(-30, -24, 10, -20, -24, 10), {'torso': 4, 'root.y': -6}, wings(0.6)), 'sm'),
          (7, STAND, 'sm')])


def cast(f):
    return PZ(CAST(f), skirt(f, 8, 1.6, 4, 0.0))


def hurt(f):
    d = [PZ(arms(-40, 20, 0, 20, 10, 0), {'torso': -14, 'head': -14, 'root.x': -4, 'root.y': -3, 'tint': ((255, 255, 255), 0.5)}, wings(0.9)),
         PZ(arms(-30, 0, 0, 14, -10, 0), {'torso': -6, 'head': -6, 'root.x': -2, 'root.y': -4, 'tint': ((255, 255, 255), 0.2)}, wings(0.7))][int(f)]
    return PZ(d, skirt(f, 2, 1, 6 + 4 * (1 - f)))


PHASE = K([(0, STAND),
           (1, PZ(arms(14, -30, 0, 20, -30, 0), {'torso': 8, 'root.y': -3, 'head': 8}, wings(0.3)), 'sm'),
           (2, PZ(arms(26, -14, 4, 30, -14, 4), {'torso': 14, 'root.y': -2, 'head': 14}, wings(0.1)), 'sm'),
           (3, PZ(arms(-40, -30, 10, -40, -30, 10), {'torso': 0, 'root.y': -10, 'head': 0}, wings(0.9, 6)), 'out'),
           (4, PZ(arms(-110, -20, 30, -110, -20, 30), {'torso': -16, 'root.y': -18, 'head': -24}, wings(1.25, 0, 14)), 'snap'),
           (5, PZ(arms(-120, -14, 36, -120, -14, 36), {'torso': -18, 'root.y': -20, 'head': -28}, wings(1.3, -6, 18)), 'sm'),
           (6, PZ(arms(-120, -14, 36, -120, -14, 36), {'torso': -18, 'root.y': -19, 'head': -26}, wings(1.3, 6, 18)), 'sm'),
           (7, PZ(arms(-90, -20, 20, -90, -20, 20), {'torso': -10, 'root.y': -18, 'head': -14}, wings(1.1, -4, 10)), 'in'),
           (8, PZ(arms(-40, -26, 8, -30, -26, 8), {'torso': -2, 'root.y': -9, 'head': -3}, wings(0.8)), 'snap'),
           (9, STAND, 'sm')])


def phase(f):
    p = PHASE(f)
    if 4 <= f <= 7:
        p['tint'] = ((255, 90, 120), 0.2 * (1 - abs(f - 5.5) / 2.0))
    return PZ(p, skirt(f, 10, 2.4, -8 if 3 <= f <= 7 else 4, 0.0))


def intro(f):
    i = int(f)
    d = clamp01((i - 3) / 7.0)
    lit = clamp01((i - 9) / 4.0)
    p = PZ(STAND, {'root.y': -4 - 6 * (1 - lit), 'head': -4 * (1 - lit)}, wings(0.55 + 0.45 * (1 - lit) * 0 + 0.3 * (1 - lit)),
           arms(-14 - 40 * (1 - lit), -30 - 20 * (1 - lit), -4, 10, -22, 0), skirt(f, 14, 1.8, 6))
    p['dis'] = max(0.0, (1 - d) * 1.12) if i >= 3 else 1.2
    p['dis_dir'] = -1.0
    if i < 3:
        p['clip'] = (0, 0, 0, 0)
    return p


DEATH = K([(0, PZ(arms(-40, 20, 0, 20, 10, 0), {'torso': -14, 'head': -14, 'root.x': -4, 'root.y': -3, 'tint': ((255, 255, 255), 0.5)}, wings(0.9)), 'out'),
           (1, PZ(arms(-60, 10, 0, 40, 0, 0), {'torso': -10, 'head': -16, 'root.x': -5, 'root.y': -8}, wings(1.0, 6)), 'sm'),
           (2, PZ(arms(-100, 0, 20, 60, 0, 20), {'torso': -14, 'head': -22, 'root.x': -5, 'root.y': -14}, wings(1.1, -6, 10)), 'sm'),
           (3, PZ(arms(-80, -30, 10, -60, -30, 10), {'torso': 4, 'head': -8, 'root.x': -3, 'root.y': -10}, wings(0.7)), 'sm'),
           (4, PZ(arms(-50, -80, 0, -40, -80, 0), {'torso': 14, 'head': 8, 'root.x': -2, 'root.y': -4}, wings(0.2)), 'sm'),
           (5, PZ(arms(-40, -100, 0, -30, -100, 0), {'torso': 24, 'head': 20, 'root.x': 0, 'root.y': 0}, wings(-0.3)), 'sm'),
           (6, PZ(arms(-30, -110, 0, -24, -110, 0), {'torso': 30, 'head': 28, 'root.x': 2, 'root.y': 2, 'skirt2.sy': 0.85}, wings(-0.5)), 'sm'),
           (13, PZ(arms(-30, -112, 0, -24, -112, 0), {'torso': 34, 'head': 32, 'root.x': 2, 'root.y': 3, 'skirt2.sy': 0.8}, wings(-0.55)), 'lin')])


def death(f):
    p = DEATH(f)
    if 4 <= f <= 12:
        for n in ('wa_f', 'wf_f', 'wa_b', 'wf_b'):
            p[n + '.z'] = 14
    d = clamp01((f - 6.5) / 5.5)
    if d > 0:
        p['dis'] = d * 1.12
        p['dis_dir'] = -1.0 if False else 1.0
    p['tiara.y'] = 0 if f < 4 else 8 * clamp01((f - 4) / 4)
    p.update(skirt(f, 14, 0.6, 6 + f))
    return p


# ====================================================================== efectos
def blood_cols():
    return [(70, 8, 28), (160, 20, 48), (230, 50, 80), (255, 160, 160)]


def fxhook(ctx):
    n, i, fx, W = ctx.name, ctx.i, ctx.fx, ctx.W
    ax, ay = ctx.pivot
    rng = ctx.rng
    claw = lambda f=None: ctx.anchor('hand_f', (0.5, 17)) if f is None else ctx.anchor_at(f, 'hand_f', (0.5, 17))
    ex, ey = ctx.anchor('head', (6, -9.5))
    if n != 'death' or i < 5:
        fx.glow(ex, ey, 6, (255, 50, 80), 0.6)
    if n not in ('intro', 'death'):
        wisps(ctx, ax - 6, ay - 50, 50, 80, 6, [(255, 80, 110), (255, 190, 200)], seed=3, a=0.7, rise=18)
    if n in ('idle', 'walk'):
        for k in range(3):
            bx = ax - 40 + k * 30 + 10 * math.sin(i * 0.8 + k * 2); by = ay - 120 + (k % 2) * 18 + 4 * math.sin(i + k)
            bat(fx, bx, by, 0.9, (i / 6.0 + k * 0.3) % 1, a=0.9)
    if n == 'windup1':
        t = i / 4.0
        cx_, cy_ = claw()
        fx.glow(cx_, cy_, 8 + 10 * t, (255, 60, 90), 0.4 * t + 0.1)
        if i >= 2:
            for k in range(5):
                fx.line((cx_ - 4 + k * 2, cy_ - 2), (cx_ - 5 + k * 2, cy_ + 8 + 2 * t), 1, (255, 190, 200), 0.4 + 0.4 * t, 'front')
    if n == 'attack1':
        trail(ctx, 'hand_f', (0.5, 18), (0.5, 6), 0, 4, (255, 235, 235), (170, 20, 50), steps=12, span=3.2, mid=(240, 60, 90), a=0.85)
        trail(ctx, 'hand_f', (-1.5, 18), (-1.5, 6), 0, 4, (255, 210, 215), (120, 10, 40), steps=12, span=3.2, a=0.6)
        if 3 <= i <= 6:
            cx_, cy_ = claw(3.4)
            t = (i - 3) / 3.0
            for k in range(7):
                a = -0.5 + 1.8 * rng.random()
                r = 6 + 16 * t * rng.random()
                fx.dots([(cx_ + math.cos(a) * r, cy_ + math.sin(a) * r * 0.8 + 3 * t)], (230, 30, 60), 1 - t * 0.6, 'front', 2)
    if n == 'windup2':
        t = i / 4.0
        fx.glow(ax, ay - 40, 24 + 12 * t, (255, 40, 80), 0.3 * t, rx=24, ry=44)
        for k in range(4):
            x0 = ax + 46 - ((i * 7 + k * 13) % 14)
            yy = ay - 20 - k * 14
            fx.line((x0, yy), (x0 - 8, yy), 1, (255, 150, 170), 0.4 * t, 'front', mode='add')
    if n == 'attack2' and 1 <= i <= 6:
        x1, y1 = ctx.anchor('torso', (0, -16))
        t = clamp01((i - 1) / 5.0)
        for k in range(6):
            yy = ay - 14 - k * 13
            x0 = x1 - 14 - ((i * 9 + k * 17) % 18)
            fx.line((x0, yy), (x0 - 18 - 5 * k, yy), 1 + (k % 2), (240, 50, 80), 0.7 * (1 - t * 0.4), 'front')
        cx_, cy_ = claw()
        fx.poly([(cx_ - 30, cy_ - 8), (cx_ + 8, cy_), (cx_ - 30, cy_ + 8)], (200, 20, 60), 0.4 * (1 - t * 0.6), 'front', ss=2)
        fx.poly([(cx_ - 24, cy_ - 4), (cx_ + 6, cy_), (cx_ - 24, cy_ + 4)], (255, 170, 180), 0.5 * (1 - t * 0.5), 'front', ss=2)
        if 2 <= i <= 4:
            fx.glow(min(W - 6, cx_ + 4), cy_, 10, (255, 120, 140), 0.8)
        dust(ctx, ax + ctx.pose.get('root.x', 0) * 0.4 - 8, ay, clamp01((i - 1) / 4.0), (120, 50, 70), 8, 18, 6, a=0.5)
    if n == 'windup3':
        t = i / 5.0
        rays(ctx, ax, ay - 2, t * 0.6, (230, 30, 60), 6, 6, 26, 0.18, 0.35 * t, 0.4, 'back')
        wisps(ctx, ax, ay - 3, 40, 6, 8, [(255, 70, 100)], t=t, seed=5, rise=26, a=0.7)
        if i >= 3:
            fx.glow(ax, ay - 80, 30, (255, 40, 80), 0.3 * t)
    if n == 'attack3':
        if 2 <= i <= 4:
            cx_, cy_ = claw()
            for k in range(6):
                fx.line((cx_ - 6 + k, cy_ - 30 - 8 * k), (cx_ - 4 + k, cy_ - 6), 1, (255, 150, 170), 0.5, 'front')
        if 4 <= i <= 8:
            t = (i - 4) / 4.0
            gx = ax + 18
            shock(ctx, gx, ay, t, (255, 90, 120), 76, 8, 2)
            ground_cracks(ctx, gx, ay + 1, t, (40, 6, 22), (240, 40, 70), 8, 60, 21)
            pool(ctx, gx, ay - 1, 36 * clamp01(t * 1.5 + 0.2), 4, [(70, 8, 28), (150, 16, 44), (200, 30, 60)], 0.95)
            if i <= 6:
                fx.glow(gx, ay - 6, 22, (255, 50, 90), 0.8 * (1 - t))
                for k in range(8):
                    ang = math.pi * (0.1 + 0.8 * rng.random())
                    r = 10 + 40 * t * rng.random()
                    px = gx + math.cos(ang) * r * (1 if k % 2 else -1); py = ay - math.sin(ang) * r * 0.9
                    fx.ell(px, py, 1.6, 2.6, (225, 30, 62), 0.95, 'front')
    if n == 'cast':
        cx_, cy_ = claw()
        if 1 <= i <= 4:
            t = i / 4.0
            fx.glow(cx_, cy_ - 6, 10 + 12 * t, (255, 40, 80), 0.8)
            for hx_, hy_ in (claw(), ctx.anchor('hand_b', (0.5, 17))):
                fx.ell(hx_, hy_ - 6, 3 + 3 * t, 3 + 3 * t, (170, 14, 48), 1.0, 'front')
                fx.ell(hx_ - 0.8, hy_ - 7, 1.6 + 1.6 * t, 1.6 + 1.6 * t, (255, 110, 130), 1.0, 'front')
        if i >= 4:
            tt = (i - 4) / 3.0
            for k in range(3):
                sx_ = cx_ + 6 + tt * (44 + k * 14)
                sy_ = cy_ - 6 + (k - 1) * 14 + tt * (k - 1) * 6
                if sx_ < W - 5:
                    fx.glow(sx_, sy_, 9, (255, 50, 90), 0.85)
                    fx.ell(sx_, sy_, 4, 4, (150, 12, 44), 1.0, 'front')
                    fx.ell(sx_ - 0.8, sy_ - 0.8, 2.4, 2.4, (255, 120, 140), 1.0, 'front')
                    fx.polyline([(sx_ - 4, sy_), (sx_ - 14, sy_ + 1), (sx_ - 24, sy_)], 2, (220, 30, 64), 0.5, 'front')
    if n == 'phase':
        t = clamp01((i - 3) / 5.0)
        if 3 <= i <= 9:
            fx.glow(ax, ay - 70, 70 * t + 14, (255, 30, 70), 0.5 * (1 - abs(t - 0.5) * 1.2), rx=60 * t + 16, ry=70 * t + 16)
            rays(ctx, ax, ay - 76, t, (255, 70, 100), 16, 14, 84, 0.1, 0.5, i * 0.1, 'back')
            shock(ctx, ax, ay, clamp01((i - 4) / 5.0), (255, 90, 120), 62, 7, 2)
        if 3 <= i <= 9:
            for k in range(10):
                a = (k / 10.0) * 6.283 + i * 0.5
                r = 24 + 52 * t
                bat(fx, ax + math.cos(a) * r, ay - 74 + math.sin(a) * r * 0.7, 1.0, (i * 0.4 + k * 0.17) % 1, a=1.0)
    if n == 'death':
        if 4 <= i <= 7:
            hx_, hy_ = ctx.anchor('head', (-2, -4))
        if i >= 6:
            t = clamp01((i - 6) / 7.0)
            pool(ctx, ax + 4, ay - 1, 12 + 30 * t, 3 + 2 * t, [(60, 6, 24), (130, 14, 40), (190, 26, 56)], 0.95)
            for k in range(2 + int(14 * t)):
                a = k * 0.9 + i * 0.3
                bat(fx, ax - 10 + k * 3 + 5 * math.sin(a), ay - 20 - k * (4 + 4 * t) - 20 * t, 0.9, (i * 0.3 + k * 0.13) % 1, a=1 - 0.5 * t * (k % 3 == 0))
        if i >= 8:
            cx0 = ax + 22
            fx.poly([(cx0 - 5, ay), (cx0 - 5, ay - 3), (cx0 - 3, ay - 1), (cx0, ay - 5), (cx0 + 3, ay - 1), (cx0 + 5, ay - 3), (cx0 + 5, ay)], (196, 164, 76), 1.0, 'back')
            fx.dots([(cx0, ay - 3)], (255, 60, 90), 1.0, 'back')
    if n == 'intro':
        intro_fx(ctx)


def intro_fx(ctx):
    i, fx, ax, ay = ctx.i, ctx.fx, ctx.pivot[0], ctx.pivot[1]
    t = i / 13.0
    mid = (ax, ay - 56)
    fx.glow(mid[0], mid[1], 40, (230, 20, 60), 0.35 * (1 - clamp01((i - 9) / 4.0)), rx=36, ry=56)
    n_b = 26
    for k in range(n_b):
        rng = np.random.default_rng(100 + k)
        ang0 = rng.random() * 6.283
        r0 = 54 + rng.random() * 30
        sp = 0.5 + rng.random() * 0.8
        # los murcielagos orbitan cerrandose hacia el cuerpo y luego se disipan hacia arriba
        conv = clamp01(i / 8.0)
        r = r0 * (1 - 0.8 * conv) + 6
        if i >= 9:
            r = 6 + (i - 9) * 12
        a = ang0 + i * sp * 0.8
        x = mid[0] + math.cos(a) * r * 1.2
        y = mid[1] + math.sin(a) * r * 0.9 - (max(0, i - 9)) * 6 * rng.random()
        al = 1.0 if i < 11 else max(0.0, 1 - (i - 10) / 3.5)
        if 0 <= x < ctx.W and al > 0.05:
            bat(fx, x, y, 0.9 + rng.random() * 0.4, (i * 0.37 + rng.random()) % 1, a=al, layer='front' if k % 2 else 'back')


def hit_boxes():
    return {
        'attack1': dict(hit=[2, 4], box=[4, -78, 52, 70]),
        'attack2': dict(hit=[1, 5], box=[6, -66, 118, 60]),
        'attack3': dict(hit=[4, 6], box=[-62, -48, 130, 50]),
        'cast': dict(rel=4, muzzle_src=('hand_f', (0.5, 6))),
    }


def spec():
    fns = dict(idle=idle_pose, walk=walk_pose, windup1=wind1, attack1=atk1, windup2=wind2, attack2=atk2, windup3=wind3,
               attack3=atk3, cast=cast, hurt=hurt, phase=phase, intro=intro, death=death)
    hb = hit_boxes()
    return {k: dict(pose=v, **hb.get(k, {})) for k, v in fns.items()}


def build():
    return make(spec(), fxhook)
