"""bs_coloso_magma: El corazon de la Forja. Golem de basalto con venas de lava, pecho abierto con nucleo ardiente."""
import math
import numpy as np
from kit import *
from shapes import *
from anim import *
from fxlib import *

BAS = auto('#3c3849', shadow=(20, 12, 52), warm=(255, 196, 150), n=6, dk=0.22, lk=0.34)
BRK = auto('#7a3d38', shadow=(34, 12, 44), warm=(255, 170, 110), n=6, dk=0.24)
OBS = auto('#2a2438', shadow=(10, 6, 34), warm=(190, 150, 230), n=6, dk=0.2, lk=0.3)
IRN = auto('#625650', shadow=(26, 14, 40), warm=(255, 210, 160), n=6, dk=0.24)
VOID = ramp((6, 2, 6), (16, 6, 10), (44, 14, 14), 6)
LAVAG = [(70, 8, 8), (190, 36, 8), (255, 104, 18), (255, 178, 52), (255, 236, 150), (255, 252, 226)]
COREG = [(150, 30, 6), (255, 90, 14), (255, 170, 40), (255, 230, 120), (255, 250, 214), (255, 255, 255)]
MATS = {
    'bas': Mat(BAS, glow=LAVAG, texamt=0.62, gain=1.2),
    'brk': Mat(BRK, glow=LAVAG, texamt=0.6, gain=1.2),
    'obs': Mat(OBS, glow=LAVAG, texamt=0.35, gain=1.5),
    'irn': Mat(IRN, glow=LAVAG, texamt=0.5, gain=1.3),
    'void': Mat(VOID, gain=0.4),
    'core': Mat(BRK, glow=COREG, texamt=0.1),
}
LAVAC = (255, 120, 24)


def facet(pts, amp=1.2, seed=0, sub=2):
    rng = np.random.default_rng(seed)
    out = []
    n = len(pts)
    for i in range(n):
        a = np.array(pts[i], float); b = np.array(pts[(i + 1) % n], float)
        out.append(tuple(a))
        for k in range(1, sub):
            t = k / sub
            q = a + (b - a) * t
            out.append((q[0] + (rng.random() - 0.5) * 2 * amp, q[1] + (rng.random() - 0.5) * 2 * amp))
    return out


def veins(p, n, length, seed, emit=0.55, v=0.04, w=0.9, spread=0.7):
    p.cracks(n, length, v=v, w=w, seed=seed, emit=emit, branch=0.9, spread=spread)
    return p


def build_parts():
    P = []

    def add(*a, **k):
        p = Part(*a, **k); P.append(p); return p
    add('root', None, (96, 156), ghost=True)
    # ------------------------------------------------ pelvis
    hip = add('hip', 'root', (0, -50), z=4, mat='bas', depth=8.0, noise=0.7, seed=5, tnoise=0.3)
    hip.poly(facet([(-19, -8), (-8, -13), (9, -13), (19, -8), (23, 2), (16, 11), (0, 14), (-15, 11), (-22, 2)], 1.0, 5))
    hip.brick(7, 5, 0.1, 0.8, 0.22, 3)
    hip.blotch('brk', 0.8, 3.0, 9, raise_=0.4)
    veins(hip, 4, 9, 6)
    hip.ell(2, 0, 5.5, 4.5, mat='irn', raise_=1.4, edge=0.1)
    hip.ell(2, 0, 2.4, 2.0, op='emit', v=0.85, soft=0.5)
    # ------------------------------------------------ piernas
    for nm, x, z, dim in (('b', -14, 2, -0.22), ('f', 14, 5, 0.0)):
        th = add('thigh_' + nm, 'hip', (x, 4), z=z, mat='bas', depth=8.0, noise=0.7, seed=10, dim=dim, tnoise=0.3)
        th.poly(facet([(-12, -5), (-5, -8), (7, -8), (13, -3), (14, 10), (12, 22), (-10, 23), (-14, 10)], 1.1, 11))
        th.hatch(5.0, 90, v=0.08, w=0.9, jit=0.5, seed=4)
        th.blotch('brk', 0.8, 3.0, 12, raise_=0.4)
        veins(th, 3, 11, 13)
        sh = add('shin_' + nm, 'thigh_' + nm, (0, 19), z=z + 0.1, mat='bas', depth=8.0, noise=0.7, seed=14, dim=dim, tnoise=0.3)
        sh.poly(facet([(-11, -5), (11, -5), (14, 6), (12, 20), (-10, 20), (-14, 8)], 1.1, 15))
        sh.hatch(5.0, 90, v=0.08, w=0.9, jit=0.5, seed=5)
        sh.blotch('brk', 0.8, 3.0, 16, raise_=0.4)
        veins(sh, 2, 10, 17)
        sh.poly([(2, -8), (9, -4), (14, 2), (7, 3), (3, -2)], mat='obs', raise_=1.2, edge=0.1)  # rodillera con pincho
        sh.poly([(-10, 12), (11, 12), (12, 15), (-11, 15)], mat='irn', raise_=1.0, edge=0.1)
        ft = add('foot_' + nm, 'shin_' + nm, (0, 18), z=z + 0.2, mat='bas', depth=5.0, noise=0.6, seed=18, dim=dim, tnoise=0.3)
        ft.poly(facet([(-13, -3), (8, -4), (20, 2), (26, 8), (24, 12), (-14, 12)], 0.9, 19))
        ft.hatch(4.0, 90, v=0.08, w=0.8, jit=0.5, seed=6)
        ft.poly([(16, 0), (22, 4), (25, 8), (19, 8)], mat='obs', raise_=0.9, edge=0.1)
        veins(ft, 1, 7, 20, emit=0.5)
    # ------------------------------------------------ espinas dorsales (detras)
    sp = add('spines', 'hip', (-12, -14), z=0.5, mat='obs', depth=4.0, noise=0.5, seed=24, tnoise=0.25)
    sp.poly([(-2, 12), (-14, -2), (-26, -20), (-24, -38), (-14, -30), (-18, -50), (-6, -38), (2, -24), (12, -8), (14, 14)])
    sp.line([(-4, 8), (-16, -10), (-24, -34)], 0.9, op='tex', v=0.85)
    sp.cracks(2, 9, v=0.04, w=0.8, seed=25, emit=0.5)
    # ------------------------------------------------ torso
    to = add('torso', 'hip', (0, -6), z=6, mat='bas', depth=12.0, noise=0.9, seed=20, tnoise=0.3)
    to.poly(facet([(-17, 7), (-24, -8), (-30, -28), (-22, -41), (-7, -46), (10, -46), (24, -40), (32, -28), (27, -10), (19, 7), (0, 11)], 1.3, 20, 3))
    to.brick(8, 6, 0.1, 0.8, 0.25, 7, 0.4)
    to.blotch('brk', 0.68, 3.4, 21, raise_=0.5)
    veins(to, 6, 13, 22, spread=0.9)
    # cavidad pectoral
    to.spl([(-3, -33), (11, -35), (20, -25), (19, -10), (8, -4), (-5, -10), (-9, -22)], mat='void', raise_=-1.2)
    to.line([(-2, -2), (-12, 2)], 1.0, op='tex', v=0.06)
    # placas pectorales superiores
    to.poly(facet([(-14, -30), (4, -42), (14, -36), (2, -30), (-6, -24)], 0.7, 23), mat='obs', raise_=1.6, edge=0.1)
    # ------------------------------------------------ nucleo
    co = add('core', 'torso', (7, -20), z=6.6, mat='core', depth=7.0, noise=0.2, seed=30, tnoise=0.2)
    co.ell(0, 0, 9.5, 10.5)
    co.ell(0, 0, 7.5, 8.2, op='emit', v=0.62, soft=0.8)
    co.ell(-1, -1, 4.4, 4.8, op='emit', v=0.95, soft=0.9)
    co.cracks(5, 6, v=0.05, w=0.7, seed=31, emit=0.2)
    ri = add('ribs', 'torso', (7, -20), z=6.9, mat='bas', depth=4.0, noise=0.4, seed=32, tnoise=0.25)
    for sx in (-1, 1):
        ri.poly([(sx * 11, -15), (sx * 14, -4), (sx * 11, 8), (sx * 7.5, 2), (sx * 8.5, -6), (sx * 6.5, -13)])
    ri.poly([(-9, -14), (-2, -17), (3, -13), (-3, -12)])
    ri.poly([(-12, 11), (-5, 6), (0, 9), (5, 6), (12, 11), (6, 14), (0, 12), (-6, 14)])
    ri.cracks(2, 5, v=0.05, w=0.7, seed=33, emit=0.5)
    # ------------------------------------------------ cabeza
    hd = add('head', 'torso', (10, -44), z=9, mat='bas', depth=6.0, noise=0.5, seed=34, tnoise=0.25)
    hd.poly(facet([(-14, 4), (-15, -9), (-8, -19), (6, -22), (18, -16), (22, -5), (19, 5), (8, 9), (-6, 8)], 0.8, 35))
    hd.hatch(4.0, 90, v=0.08, w=0.8, jit=0.5, seed=7)
    hd.poly([(-4, -15), (8, -18), (21, -11), (20, -7), (7, -11), (-5, -10)], mat='obs', raise_=1.3, edge=0.1)  # ceja
    hd.poly([(6, -5), (17, -6.4), (18, -2.6), (7, -1.2)], mat='void', raise_=-0.4)
    hd.poly([(7.5, -4.4), (16.5, -5.6), (17, -3.4), (8, -2)], op='emit', v=1.0, soft=0.25)
    hd.poly([(-9, -9), (-3, -9), (-3, -5), (-9, -5)], op='emit', v=0.6, soft=0.5)
    veins(hd, 2, 6, 36, emit=0.5)
    jw = add('jaw', 'head', (0, 5), z=8.5, mat='bas', depth=4.0, noise=0.3, seed=37)
    jw.poly(facet([(-9, 0), (11, -1), (16, 2), (13, 8), (3, 12), (-6, 9), (-10, 5)], 0.6, 38))
    for k in range(5):
        jw.poly([(-3 + k * 3.6, 0), (-1 + k * 3.6, 0), (-1.8 + k * 3.6, 3)], op='emit', v=0.95, soft=0.2)
    veins(jw, 1, 5, 39, emit=0.6)
    for nm, x, a0, z, dim in (('b', -9, -1, 7.5, -0.2), ('f', 2, 1, 9.5, 0.0)):
        hr = add('horn_' + nm, 'head', (x, -17), z=z, mat='obs', depth=3.5, noise=0.3, seed=40, dim=dim)
        hr.poly(facet(list(bez((-4, 2), (-8, -4), (-12, -12), n=6)) + list(bez((-12, -12), (-3, -8), (3, 2), n=6)), 0.4, 41, 1))
        hr.line([(-5, 0), (-8, -5), (-11, -11)], 0.8, op='tex', v=0.85)
    # ------------------------------------------------ hombros y brazos
    for nm, x, z, dim in (('b', -23, 2.5, -0.22), ('f', 27, 8.5, 0.0)):
        ua = add('uarm_' + nm, 'torso', (x, -31), z=z, mat='bas', depth=8.0, noise=0.7, seed=44, dim=dim, tnoise=0.3)
        ua.poly(facet([(-11, -6), (-3, -9), (8, -8), (12, -2), (12, 12), (11, 24), (-9, 25), (-12, 12)], 1.1, 45))
        ua.hatch(5.0, 90, v=0.08, w=0.9, jit=0.5, seed=8)
        ua.blotch('brk', 0.8, 3.0, 46, raise_=0.4)
        veins(ua, 3, 10, 47)
        fa = add('farm_' + nm, 'uarm_' + nm, (0, 22), z=z + 0.1, mat='bas', depth=8.0, noise=0.7, seed=48, dim=dim, tnoise=0.3)
        fa.poly(facet([(-9, -4), (9, -4), (13, 6), (14, 20), (-13, 20), (-12, 7)], 1.1, 49))
        fa.hatch(5.0, 90, v=0.08, w=0.9, jit=0.5, seed=9)
        fa.blotch('brk', 0.8, 3.0, 50, raise_=0.4)
        veins(fa, 3, 10, 51)
        fa.poly([(-13, 13), (14, 13), (15, 18), (-14, 18)], mat='irn', raise_=1.2, edge=0.1)
        fa.poly([(-13, 14.5), (14, 14.5), (14, 16.5), (-13, 16.5)], op='emit', v=0.55, soft=0.4)
        fi = add('fist_' + nm, 'farm_' + nm, (0, 19), z=z + 0.2, mat='bas', depth=8.0, noise=0.7, seed=52, dim=dim, tnoise=0.3)
        fi.poly(facet([(-14, -1), (14, -1), (18, 9), (16, 21), (6, 27), (-8, 27), (-17, 19), (-17, 7)], 1.2, 53))
        fi.brick(6, 6, 0.1, 0.8, 0.25, 9, 0.4)
        fi.blotch('brk', 0.8, 2.6, 54, raise_=0.4)
        for kx in (-6, 0, 6):
            fi.line([(kx, 14), (kx + 0.8, 25)], 0.9, op='tex', v=0.03)
            fi.line([(kx, 16), (kx + 0.4, 23)], 0.7, op='emit', v=0.6, soft=0.2)
        fi.poly([(-10, 24), (10, 24), (12, 27), (-10, 27)], op='emit', v=0.5, soft=0.5)
        veins(fi, 2, 8, 55)
        fi.poly([(-11, 1), (-8, -4), (-5, 1)], mat='obs', raise_=1.0, edge=0.1)
        fi.poly([(4, 1), (7, -4), (10, 1)], mat='obs', raise_=1.0, edge=0.1)
    for nm, x, z, dim in (('b', -25, 3.0, -0.2), ('f', 27, 8.8, 0.0)):
        pd = add('pauld_' + nm, 'torso', (x, -33), z=z, mat='bas', depth=9.0, noise=0.8, seed=60, dim=dim, tnoise=0.3)
        pd.poly(facet([(-14, 6), (-15, -4), (-8, -12), (4, -14), (14, -7), (15, 3), (9, 10), (-5, 11)], 1.0, 61))
        pd.hatch(5.0, 75, v=0.08, w=0.9, jit=0.4, seed=10)
        pd.poly([(-8, -9), (-13, -22), (-3, -13)], mat='obs', raise_=1.0, edge=0.1)
        pd.poly([(-1, -13), (0, -28), (6, -12)], mat='obs', raise_=1.0, edge=0.1)
        pd.poly([(8, -10), (17, -20), (14, -5)], mat='obs', raise_=1.0, edge=0.1)
        pd.blotch('brk', 0.8, 2.6, 62, raise_=0.4)
        veins(pd, 2, 8, 63)
    return P


def make(anims, fxhook):
    parts = build_parts()
    return Boss('coloso_magma', (192, 160), (96, 156), (56, 112), parts, MATS, anims, fxhook,
                outline=(14, 6, 14), rim=(255, 130, 50), rimk=0.38, dis_col=(255, 140, 40), seed=21, post=None, scale=1.0, base=0.42)


# ====================================================================== animacion
def LG(thf, shf, thb, shb):
    return {'thigh_f': thf, 'shin_f': shf, 'foot_f': -(thf + shf), 'thigh_b': thb, 'shin_b': shb, 'foot_b': -(thb + shb)}


def AR(uf, ff, ub, fb, fif=0, fib=0):
    return {'uarm_f': uf, 'farm_f': ff, 'fist_f': fif, 'uarm_b': ub, 'farm_b': fb, 'fist_b': fib}


def T(torso=0, head=0, jaw=0, ry=0, rx=0, hip=0):
    return {'torso': torso, 'head': head, 'jaw': jaw, 'root.y': ry, 'root.x': rx, 'hip': hip}


def PZ(*ds):
    return merge(*ds)


STAND = PZ(LG(-4, 8, 6, -2), AR(-18, -16, 18, 6), T(6, 2, 0, 0))


def pulse(f, n, k=0.12, ph=0.0):
    return {'core.s': 1 + k * S(f, n, ph), 'ribs.s': 1}


def idle_pose(f):
    b = S(f, 6)
    return PZ(STAND, {'root.y': -0.8 * b + 0.4, 'torso': 1.2 * b, 'head': -1.5 * b, 'jaw': 1 + b,
                      'uarm_f': 1.2 * b, 'uarm_b': -1.2 * b, 'farm_f': 1.8 * b, 'farm_b': -1.2 * b, 'pauld_f.y': -0.7 * b, 'pauld_b.y': -0.7 * b}, pulse(f, 6, 0.12))


def walk_pose(f):
    ph = 2 * math.pi * f / 8
    s = math.sin(ph); c = math.cos(ph)
    thf = 17 * s - 3
    thb = -17 * s + 3
    shf = 8 + 18 * max(0, -c * 0.9 + 0.1) * (1 if s < 0.3 else 0.3) + 4 * max(0, c)
    shb = 8 + 18 * max(0, c * 0.9 + 0.1) * (1 if s > -0.3 else 0.3) + 4 * max(0, -c)
    return PZ(LG(thf, shf, thb, shb), AR(-4 - 18 * s, -14 - 8 * s, 6 + 18 * s, -6 + 6 * s),
              T(3 + 2 * c, -2 + 1 * c, 1 + c, -3.2 * abs(c) + 1.2, 0, 1.5 * s), pulse(f, 8, 0.14), {'torso': 2.5 * s})


def kf(keys):
    return K(keys)


W1 = [(0, STAND),
      (1, PZ(LG(-8, 12, 8, -5), AR(-40, -70, 8, -10), T(-4, -4, 2, 1, -2))),
      (2, PZ(LG(-10, 16, 10, -8), AR(-100, -70, 10, -12), T(-9, -8, 5, 2, -4))),
      (3, PZ(LG(-12, 18, 12, -10), AR(-130, -50, 10, -12), T(-14, -12, 10, 3, -6))),
      (4, PZ(LG(-12, 18, 12, -10), AR(-140, -50, 10, -12), T(-17, -14, 14, 3.5, -7)))]
w1k = kf(W1)


def wind1(f):
    p = w1k(f)
    return PZ(p, pulse(f, 5, 0.10 + 0.04 * f), {'emit': 1 + 0.08 * f})


W1E = PZ(LG(-12, 18, 12, -10), AR(-140, -50, 10, -12), T(-17, -14, 14, 3.5, -7))
A1 = [(0, W1E, 'sm'),
      (1, PZ(LG(-14, 20, 14, -10), AR(-140, -34, 10, -12), T(-8, -6, 8, 3, -3)), 'snap'),
      (2, PZ(LG(-20, 26, 18, -12), AR(-70, -26, 12, -14), T(12, 6, 3, 4, 7)), 'snap'),
      (3, PZ(LG(-24, 30, 20, -14), AR(-34, -18, 14, -16), T(22, 12, 2, 5, 12)), 'snap'),
      (4, PZ(LG(-24, 30, 20, -14), AR(-30, -14, 14, -16), T(22, 12, 2, 5, 12)), 'out'),
      (5, PZ(LG(-20, 26, 16, -12), AR(-28, -14, 12, -14), T(18, 10, 3, 4.5, 10)), 'sm'),
      (6, PZ(LG(-12, 18, 10, -8), AR(-14, -12, 8, -8), T(8, 4, 2, 2.5, 4)), 'sm'),
      (7, PZ(STAND), 'sm')]
a1k = kf(A1)


def atk1(f):
    return PZ(a1k(f), pulse(f, 8, 0.1))


W2 = [(0, STAND),
      (1, PZ(LG(-8, 12, 8, -6), AR(-30, -40, -20, -40), T(-4, 0, 2, 1, -2))),
      (2, PZ(LG(-12, 18, 12, -10), AR(-4, -76, -44, -56, 0, 0), T(-10, -4, 6, 2.5, -5))),
      (3, PZ(LG(-14, 22, 14, -12), AR(12, -100, -60, -66), T(-16, -6, 10, 3.5, -8))),
      (4, PZ(LG(-14, 24, 14, -12), AR(18, -116, -64, -70), T(-19, -8, 14, 4, -10)))]
w2k = kf(W2)


def wind2(f):
    return PZ(w2k(f), pulse(f, 5, 0.1 + 0.04 * f), {'emit': 1 + 0.1 * f, 'fist_f.e': 1 + 0.12 * f})


W2E = PZ(LG(-14, 24, 14, -12), AR(18, -116, -64, -70), T(-19, -8, 14, 4, -10))
A2 = [(0, W2E, 'sm'),
      (1, PZ(LG(-20, 26, 16, -12), AR(-70, -40, -50, -50), T(2, 0, 8, 3, 0)), 'snap'),
      (2, PZ(LG(-28, 32, 20, -16), AR(-90, -2, -40, -30), T(14, 6, 4, 3, 12)), 'snap'),
      (3, PZ(LG(-30, 34, 22, -16), AR(-92, 0, -36, -26), T(18, 8, 2, 3, 16)), 'out'),
      (4, PZ(LG(-30, 34, 22, -16), AR(-92, 0, -36, -26), T(18, 8, 2, 3, 16)), 'sm'),
      (5, PZ(LG(-26, 30, 20, -14), AR(-80, -4, -30, -24), T(16, 6, 3, 3, 14)), 'sm'),
      (6, PZ(LG(-16, 20, 12, -10), AR(-30, -14, 4, -10), T(8, 3, 3, 2.5, 6)), 'sm'),
      (7, PZ(STAND), 'sm')]
a2k = kf(A2)


def fist_ext(f):
    """distancia extra del puño f (a lo largo del antebrazo) en attack2"""
    tab = [0, 4, 52, 74, 78, 56, 18, 0]
    i = int(f)
    if f == i:
        return tab[i]
    return tab[i] + (tab[min(7, i + 1)] - tab[i]) * (f - i)


def atk2(f):
    p = a2k(f)
    p['fist_f.y'] = fist_ext(f)
    return PZ(p, pulse(f, 8, 0.1))


W3 = [(0, STAND),
      (1, PZ(LG(-30, 56, 28, -50), AR(-70, -30, -60, -30), T(8, 2, 2, 12, -2))),
      (2, PZ(LG(-34, 70, 32, -60), AR(-110, -30, -104, -34), T(2, -2, 6, 18, -4))),
      (3, PZ(LG(-36, 76, 34, -66), AR(-138, -30, -134, -34), T(-6, -6, 10, 22, -5))),
      (4, PZ(LG(-38, 80, 34, -70), AR(-130, -50, -126, -54), T(-12, -10, 16, 24, -6))),
      (5, PZ(LG(-38, 80, 34, -70), AR(-132, -52, -128, -56), T(-14, -12, 18, 25, -6)))]
w3k = kf(W3)


def wind3(f):
    return PZ(w3k(f), pulse(f, 6, 0.1 + 0.04 * f), {'emit': 1 + 0.1 * f})


W3E = PZ(LG(-38, 80, 34, -70), AR(-132, -52, -128, -56), T(-14, -12, 18, 25, -6))
A3 = [(0, W3E, 'sm'),
      (1, PZ(LG(-8, 12, 8, -6), AR(-118, -50, -114, -54), T(-6, -6, 12, -6, 2)), 'out'),
      (2, PZ(LG(-6, 8, 6, -6), AR(-112, -56, -108, -60), T(0, 0, 8, -14, 4)), 'sm'),
      (3, PZ(LG(-10, 14, 10, -10), AR(-100, -36, -96, -40), T(12, 6, 4, -8, 8)), 'in'),
      (4, PZ(LG(-26, 50, 24, -44), AR(-26, -16, -22, -18), T(30, 16, 2, 12, 10)), 'snap'),
      (5, PZ(LG(-30, 56, 28, -50), AR(-18, -12, -14, -14), T(34, 18, 0, 16, 10)), 'sm'),
      (6, PZ(LG(-28, 52, 26, -46), AR(-18, -12, -14, -14), T(32, 16, 0, 14, 10)), 'sm'),
      (7, PZ(LG(-18, 30, 14, -24), AR(-12, -10, -6, -10), T(18, 8, 2, 6, 5)), 'sm'),
      (8, PZ(STAND), 'sm')]
a3k = kf(A3)


def atk3(f):
    return PZ(a3k(f), pulse(f, 9, 0.12))


CAST = K([(0, STAND),
          (1, PZ(LG(-8, 12, 8, -6), AR(-30, -30, -26, -30), T(-4, -4, 4, 1, -1))),
          (2, PZ(LG(-10, 16, 10, -8), AR(-70, -50, -64, -50), T(-8, -8, 8, 2, -2)), 'sm'),
          (3, PZ(LG(-12, 18, 12, -10), AR(-104, -34, -98, -36), T(-12, -12, 12, 3, -3)), 'sm'),
          (4, PZ(LG(-12, 20, 12, -10), AR(-96, -30, -92, -32), T(-6, -14, 20, 3, -2)), 'snap'),
          (5, PZ(LG(-10, 16, 10, -8), AR(-90, -26, -88, -28), T(-2, -8, 18, 2, 0)), 'out'),
          (6, PZ(LG(-8, 12, 8, -6), AR(-60, -20, -50, -20), T(2, -2, 8, 1.5, 0)), 'sm'),
          (7, PZ(STAND), 'sm')])


def cast(f):
    p = CAST(f)
    k = 0.1 + 0.3 * (1 if 2 <= f <= 5 else 0)
    return PZ(p, {'core.s': 1 + k * S(f, 4), 'ribs.s': 1}, {'emit': 1.0 + (0.5 if 3 <= f <= 5 else 0.15 * f)})


def hurt(f):
    i = int(f)
    d = [PZ(LG(-4, 8, 6, -2), AR(-10, -16, 14, 0), T(-10, -8, 8, 1, -4), {'tint': ((255, 240, 220), 0.5)}),
         PZ(LG(-4, 8, 6, -2), AR(-6, -12, 10, -4), T(-4, -4, 4, 0.5, -2), {'tint': ((255, 240, 220), 0.15)})][i]
    return PZ(d, pulse(f, 2, 0.15))


PH = K([(0, STAND),
        (1, PZ(LG(-8, 14, 8, -6), AR(-20, -60, -16, -60), T(-6, -6, 6, 2, -1)), 'sm'),
        (2, PZ(LG(-12, 20, 12, -10), AR(-110, -50, -104, -50), T(-12, -10, 10, 4, -2)), 'sm'),
        (3, PZ(LG(-14, 24, 14, -14), AR(-146, -36, -142, -40), T(-20, -16, 24, 10, -3)), 'snap'),
        (4, PZ(LG(-14, 24, 14, -14), AR(-150, -40, -146, -44), T(-24, -20, 30, 12, -3)), 'sm'),
        (5, PZ(LG(-14, 24, 14, -14), AR(-152, -40, -148, -44), T(-26, -22, 32, 12, -3)), 'sm'),
        (6, PZ(LG(-16, 30, 16, -18), AR(-60, -90, -50, -90), T(14, 6, 20, 2, 2)), 'in'),
        (7, PZ(LG(-18, 30, 16, -18), AR(-30, -120, -20, -118), T(18, 8, 24, 2, 3)), 'snap'),
        (8, PZ(LG(-14, 22, 12, -14), AR(-60, -90, -50, -90), T(10, 2, 14, 2, 1)), 'sm'),
        (9, PZ(STAND), 'sm')])


def phase(f):
    p = PH(f)
    em = [1.0, 1.1, 1.3, 1.6, 2.0, 2.4, 2.2, 1.9, 1.5, 1.2][int(f)]
    p['emit'] = em
    if 4 <= f <= 7:
        p['root.x'] = p.get('root.x', 0) + (1.2 if int(f) % 2 else -1.2)
        p['tint'] = ((255, 170, 70), 0.14)
    p['core.s'] = [1, 1.05, 1.15, 1.3, 1.55, 1.7, 1.45, 1.3, 1.15, 1.05][int(f)]
    p['ribs.s'] = 1
    return p


# -------- intro: se arma pieza a pieza desde la lava. Cada pieza: (parte, frame_inicio, dx0, dy0)
ASSEM = {'foot_b': (0, 0, 40), 'shin_b': (1, 0, 40), 'foot_f': (1, 0, 40), 'shin_f': (2, 0, 40), 'thigh_b': (2, 0, 40),
         'thigh_f': (3, 0, 40), 'hip': (3, 0, 40), 'spines': (4, -10, -30), 'torso': (4, 0, 50),
         'ribs': (6, 0, 0), 'core': (6, 0, 0), 'pauld_b': (5, -30, -40), 'pauld_f': (5, 30, -40), 'uarm_b': (6, -44, -20),
         'uarm_f': (6, 44, -20), 'farm_b': (7, -44, -10), 'farm_f': (7, 44, -10), 'fist_b': (8, -40, 0), 'fist_f': (8, 40, 0),
         'head': (9, 0, -60), 'jaw': (9, 0, -60), 'horn_b': (10, -10, -40), 'horn_f': (10, 10, -40)}


def intro(f):
    base = PZ(STAND)
    p = {}
    for nm, (t0, dx, dy) in ASSEM.items():
        t = clamp01((f - t0) / 2.0)
        if f < t0:
            p[nm + '.v'] = 0
            continue
        e = 1 - (1 - t) ** 3
        if t < 1:
            p[nm + '.x'] = dx * (1 - e)
            p[nm + '.y'] = dy * (1 - e)
    core_e = clamp01((f - 6) / 5.0)
    p['emit'] = 0.4 + 0.6 * core_e + (0.8 if 10 <= f <= 11 else 0)
    p['core.s'] = 1 + 0.35 * (1 if 10 <= f <= 11 else 0) + 0.1 * S(f, 4)
    p['ribs.s'] = 1
    p['clip'] = (0, 0, 192, 156)
    fl = clamp01((f - 9) / 3.0) * clamp01((13 - f) / 2.0)
    if fl > 0:
        p['tint'] = ((255, 220, 140), 0.25 * fl)
    s = PZ(base, p)
    # los miembros inferiores se fijan a pose de pie
    s['root.y'] = 0
    if f >= 12:
        s['torso'] = s.get('torso', 0) + 3 * (13 - f)
        s['uarm_f'] = s.get('uarm_f', 0) - 30 * (13 - f) * 0.5
    return s


DEATH = K([(0, PZ(LG(-4, 8, 6, -2), AR(-10, -16, 14, 0), T(-10, -8, 8, 1, -4), {'tint': ((255, 240, 220), 0.6)}), 'out'),
           (1, PZ(LG(-8, 14, 8, -6), AR(-30, -20, 20, 10), T(-16, -12, 20, 2, -6), {'tint': ((255, 240, 220), 0.3)}), 'sm'),
           (2, PZ(LG(-14, 24, 12, -12), AR(-70, -30, 30, 20), T(-20, -16, 26, 4, -8), {'tint': ((255, 240, 220), 0.0)}), 'sm'),
           (3, PZ(LG(-20, 40, 16, -24), AR(-110, -20, 50, 30), T(-24, -18, 28, 8, -10)), 'sm'),
           (4, PZ(LG(-30, 60, 22, -42), AR(-140, -10, 70, 40), T(-12, -10, 24, 16, -8)), 'in'),
           (5, PZ(LG(-40, 84, 28, -62), AR(-120, -6, 90, 36), T(8, 0, 18, 26, -4)), 'in'),
           (6, PZ(LG(-48, 100, 32, -78), AR(-60, -4, 70, 30), T(30, 12, 10, 34, 2)), 'sm'),
           (8, PZ(LG(-50, 110, 34, -90), AR(-30, -2, 40, 20), T(48, 22, 6, 40, 8)), 'sm'),
           (13, PZ(LG(-52, 116, 36, -96), AR(-20, 0, 30, 16), T(52, 26, 4, 42, 10)), 'lin')])

FALL = {'head': (24, -1, 28), 'jaw': (26, -1, 30), 'horn_f': (10, 1, 26), 'horn_b': (-6, -1, 24), 'pauld_f': (12, 1, 34),
        'pauld_b': (-14, -1, 30), 'fist_f': (30, 1, 34), 'fist_b': (-26, -1, 36), 'farm_f': (18, 1, 30), 'farm_b': (-16, -1, 32),
        'uarm_f': (10, 1, 20), 'uarm_b': (-10, -1, 20), 'spines': (-20, -1, 18), 'shin_f': (8, 1, 12), 'shin_b': (-6, -1, 12)}


def death(f):
    p = DEATH(f)
    p = dict(p)
    em = max(0.0, 1.0 - clamp01((f - 3) / 7.0))
    p['emit'] = em * (1 + (1.4 if 2 <= f <= 4 else 0)) + 0.02
    if f >= 3:
        p['core.s'] = 1 + (0.8 if f < 5 else 0) * S(f, 3)
    if f >= 5:
        p['core.s'] = max(0.01, 1.0 - clamp01((f - 5) / 3.0))
        p['ribs.s'] = 1
    for nm, (dx, sgn, dy) in FALL.items():
        t = clamp01((f - 3.0) / 6.0)
        g = t * t
        p[nm + '.x'] = p.get(nm + '.x', 0) + dx * g * 0.5
        p[nm + '.y'] = p.get(nm + '.y', 0) + dy * g * 0.5
        p[nm] = p.get(nm, 0) + sgn * 40 * g
    if f >= 9:
        d = clamp01((f - 9.0) / 4.8)
        p['dis'] = d * 1.12
        p['dis_dir'] = -1.0
    p['pauld_f.y'] = p.get('pauld_f.y', 0) + (0)
    return p


# ====================================================================== efectos
def ember_col(k):
    return [(255, 200, 80), (255, 130, 30), (255, 240, 190)][k % 3]


def magma_ball(ctx, x, y, s=1.0, ph=0.0):
    fx = ctx.fx
    fx.glow(x, y, 12 * s, (255, 110, 20), 0.9)
    fx.ell(x, y, 5.5 * s, 5.0 * s, (120, 22, 10), 1.0, 'front')
    fx.ell(x - 0.5, y - 0.5, 4.4 * s, 4.0 * s, (255, 100, 20), 1.0, 'front')
    fx.ell(x - 1.0, y - 1.0, 2.8 * s, 2.5 * s, (255, 190, 60), 1.0, 'front')
    fx.ell(x - 1.4, y - 1.4, 1.2 * s, 1.1 * s, (255, 250, 210), 1.0, 'front')
    for k in range(3):
        a = ph + k * 2.1
        fx.dots([(x - 6 * s - k * 3 + math.cos(a) * 1.0, y + math.sin(a) * 3 + (k - 1) * 3)], (255, 140, 40), 0.9, 'front')
    fx.polyline([(x - 4 * s, y + 1), (x - 13 * s, y + 3), (x - 24 * s, y + 2)], 3, (255, 90, 20), 0.5, 'front')
    fx.polyline([(x - 4 * s, y + 1), (x - 12 * s, y + 2), (x - 20 * s, y + 2)], 1, (255, 220, 120), 0.7, 'front')


def lava_spout(ctx, x, y, h, w, t, seed=0, a=0.95, layer='front'):
    """chorro de lava (columna con gotas)"""
    fx = ctx.fx
    rng = np.random.default_rng(seed)
    cols = [(150, 30, 8), (255, 100, 20), (255, 190, 70), (255, 245, 200)]
    for j, c in enumerate(cols):
        k = 1 - j * 0.26
        top = y - h * k
        fx.poly([(x - w * k, y), (x - w * k * 0.55, y - h * k * 0.6), (x + (rng.random() - 0.5) * 2, top), (x + w * k * 0.55, y - h * k * 0.6), (x + w * k, y)], c, a, layer, ss=2)
    for k in range(5):
        px = x + (rng.random() - 0.5) * w * 4.5
        py = y - h * (0.4 + 0.9 * rng.random()) * (1 - 0.3 * t)
        fx.dots([(px, py)], ember_col(k), a, layer, 1 + (k % 2))


def lava_pool(ctx, x, y, w, t=1.0, bub=0.0, layer='back', a=1.0):
    fx = ctx.fx
    h = 5 * t + 1
    fx.ell(x, y, w / 2 + 2, h + 1, (60, 12, 12), a, layer)
    fx.ell(x, y - 0.5, w / 2, h, (200, 40, 8), a, layer)
    fx.ell(x, y - 1.2, w / 2 - 4, h * 0.65, (255, 110, 20), a, layer)
    fx.ell(x - 3, y - 1.8, w / 2 - 14, h * 0.4, (255, 200, 90), a, layer)
    fx.glow(x, y - 2, w * 0.7, (255, 100, 20), 0.5 * a, rx=w * 0.7, ry=12)
    rng = np.random.default_rng(int(bub * 10) + 5)
    for k in range(7):
        bx = x + (rng.random() - 0.5) * w * 0.8
        by = y - 1 - rng.random() * h * 0.6
        r = 0.8 + 1.8 * ((bub + k * 0.37) % 1.0)
        fx.ring(bx, by, r, r * 0.6, 1, (255, 235, 150), 0.8 * (1 - (bub + k * 0.37) % 1.0), layer)


def fxhook(ctx):
    n, i, fx = ctx.name, ctx.i, ctx.fx
    ax, ay = ctx.pivot
    W = ctx.W
    rng = ctx.rng
    fist = lambda f=None, nm='fist_f': ctx.anchor(nm, (0, 14)) if f is None else ctx.anchor_at(f, nm, (0, 14))
    # nucleo: resplandor siempre (salvo muerte avanzada)
    ccx, ccy = ctx.anchor('core', (0, 0))
    ek = ctx.pose.get('emit', 1.0)
    cs = ctx.pose.get('core.s', 1.0)
    if n != 'intro' or i >= 6:
        fx.glow(ccx, ccy, 22 * cs, (255, 110, 24), min(1.0, 0.5 * ek * (cs ** 0.5)))
        fx.glow(ccx, ccy, 9 * cs, (255, 230, 150), min(1.0, 0.6 * ek))
    hx, hy = ctx.anchor('head', (10, -3))
    if n not in ('death',) or i < 4:
        fx.glow(hx, hy, 9, (255, 140, 40), min(1.0, 0.5 * ek))
    if n not in ('intro', 'death'):
        # brasas ascendentes y humo desde la espalda
        wisps(ctx, ax - 6, ay - 100, 70, 90, 14, [(255, 190, 80), (255, 120, 30), (255, 235, 170)], seed=4, a=0.95, rise=26)
        sx, sy = ctx.anchor('spines', (-18, -40))
        wisps(ctx, sx, sy - 6, 14, 10, 6, [(60, 50, 62), (96, 80, 84)], seed=12, a=0.7, rise=22, size=2, layer='back')
    if n == 'walk' and i in (1, 5):
        gx = ax + (14 if i == 1 else -14)
        dust(ctx, gx, ay, 0.35, (110, 96, 100), 6, 16, 5, 2.2, a=0.6)
        fx.dots([(gx + (k - 2) * 4, ay - 2 - k % 2) for k in range(5)], (255, 150, 40), 0.9, 'front')
    # ---- ataque 1
    if n == 'windup1':
        t = i / 4.0
        x, y = fist(nm='fist_f')
        fx.glow(x, y, 12 + 14 * t, (255, 120, 30), 0.35 + 0.4 * t)
        wisps(ctx, x, y + 8, 22, 22, 7, [(255, 190, 80), (255, 240, 180)], t=t, seed=8, rise=12)
    if n == 'attack1':
        trail(ctx, 'fist_f', (0, 26), (0, 0), 0, 4, (255, 240, 190), (190, 50, 12), steps=12, span=3.2, mid=(255, 130, 30), a=0.8)
        if 2 <= i <= 6:
            x, y = fist(3.0)
            t = (i - 2) / 4.0
            gx = max(ax + 36, min(x + 8, W - 20))
            dust(ctx, gx, ay, t, (112, 98, 104), 12, 34, 12, 3.0, a=0.7)
            shock(ctx, gx, ay, t, (255, 190, 100), 40, 5, 2)
            ground_cracks(ctx, gx, ay + 1, t, (20, 10, 14), (255, 130, 30), 6, 36, 31)
            fx.glow(gx, ay - 6, 20 * (1 - t * 0.5), (255, 160, 60), 0.85 * (1 - t))
            if i == 2:
                fx.sparks(rng, gx, ay - 3, 14, 16, [(255, 255, 220), (255, 170, 60), (255, 110, 30)], 'front', 10)
    # ---- ataque 2
    if n == 'windup2':
        t = i / 4.0
        x, y = fist(nm='fist_f')
        fx.glow(x, y, 12 + 16 * t, (255, 130, 40), 0.35 + 0.5 * t)
        for k in range(4):
            ang = i * 1.1 + k * 1.57
            r = 18 * (1 - 0.5 * t)
            fx.dots([(x + math.cos(ang) * r, y + math.sin(ang) * r * 0.8)], (255, 230, 150), 0.9, 'front')
    if n == 'attack2':
        ext = ctx.pose.get('fist_f.y', 0)
        fx0, fy0 = ctx.anchor('farm_f', (0, 10))
        fx1, fy1 = ctx.anchor('fist_f', (0, 4))
        if ext > 6:
            L = math.hypot(fx1 - fx0, fy1 - fy0)
            kk = max(2, int(L / 7))
            for k in range(kk):
                u = k / kk
                lx = fx0 + (fx1 - fx0) * u; ly = fy0 + (fy1 - fy0) * u
                fx.ell(lx, ly, 3.2, 2.0 + 0.6 * (k % 2), (36, 20, 28), 1.0, 'back')
                fx.ell(lx - 0.3, ly - 0.3, 2.4, 1.3, (255, 100, 20) if k % 2 else (190, 70, 20), 1.0, 'back')
            fx.polyline([(fx0, fy0), (fx1, fy1)], 4, (255, 90, 20), 0.35, 'back')
        if 1 <= i <= 5:
            x, y = ctx.anchor('fist_f', (0, 12))
            tt = (i - 1) / 4.0
            # estela larga ardiente tras el puño
            ln = min(60, x - fx0)
            for k in range(3):
                yy = y + (k - 1) * 8
                fx.line((x - 10, yy), (x - 10 - ln * (0.5 + 0.2 * k), yy), 2 - (k == 1) * 0 + 0, (255, 130, 30), 0.55 * (1 - tt * 0.5), 'back')
            fx.glow(x + 8, y, 18, (255, 150, 50), 0.9 * (1 - tt * 0.4))
            fx.poly([(x + 16, y - 14), (x + 28, y), (x + 16, y + 14), (x + 22, y)], (255, 235, 170), 0.7 * (1 - tt), 'front', ss=2)
            if i in (2, 3):
                dust(ctx, min(x + 18, W - 14), ay, 0.4, (112, 98, 104), 8, 20, 6, 2.4, a=0.6)
        if 1 <= i <= 5:
            dust(ctx, ax - 8, ay, clamp01((i - 1) / 4.0), (112, 98, 104), 8, 18, 6, a=0.6)
    # ---- ataque 3
    if n == 'windup3':
        t = i / 5.0
        fx.glow(ctx.anchor('torso', (0, -20))[0], ay - 90, 40 * t + 20, (255, 100, 20), 0.2 + 0.3 * t, rx=36, ry=50)
        wisps(ctx, ax, ay - 4, 56, 6, 10, [(255, 170, 60), (255, 120, 30)], t=t, seed=5, rise=34, a=0.9)
        for k in range(2):
            x, y = ctx.anchor('fist_f' if k == 0 else 'fist_b', (0, 14))
            fx.glow(x, y, 10 + 14 * t, (255, 130, 40), 0.3 + 0.5 * t)
    if n == 'attack3':
        if 2 <= i <= 4:
            for nm in ('fist_f', 'fist_b'):
                trail(ctx, nm, (0, 26), (0, 0), 3, 4, (255, 240, 190), (190, 50, 12), steps=9, span=2.2, mid=(255, 130, 30), a=0.7)
        if 4 <= i <= 8:
            t = (i - 4) / 4.0
            gx = ax + 22
            ground_cracks(ctx, gx, ay + 1, t, (20, 10, 14), (255, 130, 30), 10, 74, 41)
            ground_cracks(ctx, ax - 24, ay + 1, t, (20, 10, 14), (255, 130, 30), 8, 56, 43)
            shock(ctx, gx, ay, t, (255, 190, 100), 84, 9, 2)
            dust(ctx, gx, ay, t, (112, 98, 104), 16, 56, 18, 3.4)
            if i <= 7:
                fx.glow(gx, ay - 6, 26 * (1 - t * 0.5), (255, 160, 60), 0.85 * (1 - t))
                for k, off in enumerate((-60, -34, -12, 14, 38, 62)):
                    px = gx + off + (k % 2) * 3
                    lava_spout(ctx, px, ay + 1, (34 + 12 * (k % 3)) * (1 - t * 0.55) * clamp01(1.4 - t * 0.2), 4.6, t, seed=k + 3)
            if i == 4:
                fx.sparks(rng, gx, ay - 4, 22, 30, [(255, 255, 220), (255, 170, 60), (255, 110, 30)], 'front', 20)
        if i in (1, 2, 3):
            wisps(ctx, ax, ay - 6, 40, 30, 8, [(255, 170, 60)], seed=7, rise=20)
    # ---- cast
    if n == 'cast':
        if 1 <= i <= 4:
            t = i / 4.0
            fx.glow(ccx, ccy, 18 + 18 * t, (255, 150, 50), 0.4 + 0.5 * t)
            for k in range(7):
                ang = i * 0.9 + k * 0.9
                r = 24 * (1 - t * 0.55) + 2
                px = ccx + math.cos(ang) * r; py = ccy + math.sin(ang) * r * 0.8
                fx.glow(px, py, 4, (255, 150, 40), 0.8)
                fx.dots([(px, py)], (255, 240, 190), 1.0, 'front')
        if i >= 4:
            tt = (i - 4) / 3.0
            for k in range(3):
                sx_ = ccx + 12 + tt * (46 + k * 14)
                sy_ = ccy - 6 + (k - 1) * 12 - tt * (k - 1) * -6 + math.sin(i + k) * 2 - (1 - tt) * 4
                if sx_ < W - 8:
                    magma_ball(ctx, sx_, sy_, 1.0 - tt * 0.25, i * 0.7 + k)
    # ---- fase
    if n == 'phase':
        t = clamp01((i - 3) / 4.0)
        if 3 <= i <= 9:
            fx.glow(ax, ay - 70, 60 * t + 20, (255, 100, 20), 0.5 * (1 - abs(t - 0.5) * 1.1), rx=60 * t + 20, ry=76 * t + 14)
            rays(ctx, ax, ay - 70, t, (255, 170, 60), 16, 14, 82, 0.1, 0.55, i * 0.12, 'back', 'over')
            shock(ctx, ax, ay, clamp01((i - 3) / 5.0), (255, 190, 100), 76, 8, 2)
        if 4 <= i <= 8:
            for k, off in enumerate((-46, -24, 24, 48)):
                lava_spout(ctx, ax + off, ay + 1, (24 + 12 * (k % 2)) * clamp01((i - 3) / 2.0) * (1 - clamp01((i - 7) / 3.0) * 0.6), 2.6, t, seed=k + 20)
            sx, sy = ctx.anchor('pauld_f', (0, -12)); sx2, sy2 = ctx.anchor('pauld_b', (0, -12))
            lava_spout(ctx, sx, sy + 6, 26, 2.6, t, seed=70, a=0.9)
            lava_spout(ctx, sx2, sy2 + 6, 22, 2.6, t, seed=71, a=0.9)
            wisps(ctx, ax, ay - 70, 90, 100, 22, [(255, 190, 80), (255, 240, 180), (255, 120, 30)], t=(i - 3) / 6.0, seed=22, rise=48, a=1.0)
    # ---- intro / muerte
    if n == 'intro':
        intro_fx(ctx)
    if n == 'death':
        death_fx(ctx)


def intro_fx(ctx):
    i, fx, ax, ay = ctx.i, ctx.fx, ctx.pivot[0], ctx.pivot[1]
    rng = ctx.rng
    # charco de lava creciente
    grow = clamp01((i + 1) / 4.0) if i < 11 else max(0.0, 1 - (i - 10) / 3.0) * 0 + 1
    shrink = clamp01((i - 10) / 4.0)
    wpool = 120 * (0.4 + 0.6 * grow)
    lava_pool(ctx, ax, ay - 1, wpool, 1.0 - 0.6 * shrink, bub=i * 0.21, layer='back')
    # geiseres puntuales al encajar cada pieza
    for nm, (t0, dx, dy) in ASSEM.items():
        if i == t0 or i == t0 + 1:
            part = ctx.boss.parts[ctx.boss.index[nm]]
            if nm in ('foot_b', 'foot_f', 'shin_b', 'shin_f', 'thigh_b', 'thigh_f', 'hip', 'torso'):
                px, py = ctx.anchor(nm, (0, 4))
                if py > ay - 10:
                    py = ay
                lava_spout(ctx, px, py + 1, 18 + 4 * (i - t0 == 0), 2.4, 0.4, seed=hash(nm) % 97, a=0.9, layer='front')
            else:
                px, py = ctx.anchor(nm, (0, 4))
                fx.glow(px, py, 12, (255, 200, 100), 0.7)
                fx.sparks(rng, px, py, 6, 10, [(255, 255, 220), (255, 170, 60)], 'front', 4)
    if i >= 3:
        wisps(ctx, ax, ay - 20, 70, 40, 8, [(255, 190, 80), (255, 120, 30)], seed=3, a=0.9, rise=30)
    if 9 <= i <= 12:
        t = (i - 9) / 3.0
        fx.glow(ax, ay - 70, 50 * t + 20, (255, 200, 120), 0.5 * (1 - t * 0.5), rx=50 * t + 20, ry=60 * t + 20)
        rays(ctx, ax, ay - 70, t, (255, 190, 90), 14, 16, 70, 0.09, 0.5, i * 0.2, 'back', 'over')
        shock(ctx, ax, ay, t, (255, 200, 120), 70, 7, 2)


def death_fx(ctx):
    i, fx, ax, ay = ctx.i, ctx.fx, ctx.pivot[0], ctx.pivot[1]
    rng = ctx.rng
    # fugas de lava y explosion de nucleo
    if 1 <= i <= 6:
        for k in range(3):
            px, py = ctx.anchor('torso', (-18 + k * 18, -10 - 8 * (k % 2)))
            fx.dots([(px + (rng.random() - 0.5) * 6, py + j * 5 + (i % 3)) for j in range(3)], (255, 160, 50), 0.9, 'front')
    if 3 <= i <= 6:
        t = (i - 3) / 3.0
        cx, cy = ctx.anchor('core', (0, 0))
        fx.glow(cx, cy, 40 * (0.4 + t), (255, 190, 90), 0.9 * (1 - t * 0.6))
        rays(ctx, cx, cy, t, (255, 220, 140), 14, 8, 66, 0.1, 0.8 * (1 - t * 0.4), i * 0.3, 'front', 'add')
        impact_star(ctx, cx, cy, t, (255, 240, 200), 36)
    if i >= 7:
        t = clamp01((i - 7) / 6.0)
        pool = clamp01((i - 6) / 4.0)
        # charco de lava que se enfria
        cool = clamp01((i - 9) / 4.0)
        a = 1.0
        w = 84 * pool
        if w > 4:
            fx.ell(ax, ay - 1, w / 2 + 2, 5, (30, 14, 18), 1.0, 'back')
            c1 = lerp((200, 40, 8), (70, 24, 24), cool)
            c2 = lerp((255, 110, 20), (110, 40, 28), cool)
            c3 = lerp((255, 200, 90), (150, 70, 40), cool)
            fx.ell(ax, ay - 1.5, w / 2, 4.2, c1, 1.0, 'back')
            fx.ell(ax, ay - 2, w / 2 - 5, 2.8, c2, 1.0, 'back')
            fx.ell(ax - 4, ay - 2.5, w / 2 - 18, 1.4, c3, 1.0, 'back')
            fx.glow(ax, ay - 2, w * 0.7, (255, 100, 20), 0.4 * (1 - cool), rx=w * 0.7, ry=10)
        # escombro basaltico
        pile(ctx, ax - 4, ay, 64, 11 * pool, [(74, 70, 88), (112, 104, 124), (44, 40, 56), (122, 66, 60)], int(10 + 26 * pool), seed=9, layer='back')
        for k in range(4):
            px = ax - 26 + k * 18
            fx.dots([(px, ay - 2 - 4 * k % 3)], (255, 140, 40), 0.9 * (1 - cool * 0.5), 'back', 2)
        wisps(ctx, ax, ay - 14, 60, 18, 10, [(255, 190, 80), (255, 120, 30), (255, 240, 170)], t=t, seed=8, rise=40, a=0.9)
        wisps(ctx, ax, ay - 24, 40, 18, 6, [(70, 60, 70), (100, 88, 92)], t=t, seed=13, rise=40, a=0.8, size=2)


def hit_boxes():
    return {
        'attack1': dict(hit=[2, 4], box=[10, -112, 84, 112]),
        'attack2': dict(hit=[2, 5], box=[10, -92, 150, 70]),
        'attack3': dict(hit=[4, 6], box=[-82, -58, 172, 58]),
        'cast': dict(rel=4, muzzle_src=('core', (6, 0))),
    }


def spec():
    fns = dict(idle=idle_pose, walk=walk_pose, windup1=wind1, attack1=atk1, windup2=wind2, attack2=atk2, windup3=wind3,
               attack3=atk3, cast=cast, hurt=hurt, phase=phase, intro=intro, death=death)
    hb = hit_boxes()
    return {k: dict(pose=v, **hb.get(k, {})) for k, v in fns.items()}


def build():
    return make(spec(), fxhook)
