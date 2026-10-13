"""bs_ent_ancestral: arbol colosal podrido con rostro, ramas como brazos, hongos y musgo, raices."""
import math
import numpy as np
from kit import *
from shapes import *
from anim import *
from fxlib import *

BARK = auto('#52392b', shadow=(26, 12, 54), warm=(255, 204, 136), n=6, dk=0.24, lk=0.34)
WOOD = auto('#86633f', shadow=(40, 20, 62), warm=(255, 226, 160), n=6, dk=0.26, lk=0.4)
ROT = auto('#2e2028', shadow=(14, 8, 44), warm=(190, 150, 120), n=6, dk=0.28, lk=0.3)
ROOT = auto('#3f2c24', shadow=(18, 10, 48), warm=(230, 170, 110), n=6, dk=0.25, lk=0.3)
MOSS = auto('#4a6c2c', shadow=(14, 36, 70), warm=(236, 255, 150), n=6, dk=0.26, lk=0.36)
LEAF = auto('#c0902c', shadow=(60, 22, 50), warm=(255, 240, 150), n=6, dk=0.28, lk=0.4)
FUNG = auto('#e29a2c', shadow=(80, 24, 50), warm=(255, 244, 170), n=6, dk=0.3, lk=0.4)
STEM = auto('#d9c9a0', shadow=(70, 44, 90), warm=(255, 252, 226), n=6, dk=0.32, lk=0.4)
VOIDM = ramp((6, 4, 10), (16, 10, 18), (44, 28, 30), 6)
AMB = [(80, 34, 6), (170, 88, 12), (255, 176, 40), (255, 224, 112), (255, 248, 204)]
MATS = {
    'bark': Mat(BARK, glow=AMB, texamt=0.65, gain=1.25),
    'wood': Mat(WOOD, glow=AMB, texamt=0.55, gain=1.2),
    'rot': Mat(ROT, glow=AMB, texamt=0.6, gain=1.1),
    'root': Mat(ROOT, glow=AMB, texamt=0.6, gain=1.2),
    'moss': Mat(MOSS, texamt=0.7, gain=1.15),
    'leaf': Mat(LEAF, glow=AMB, texamt=0.4, gain=1.2),
    'fung': Mat(FUNG, glow=AMB, texamt=0.3, gain=1.1),
    'stem': Mat(STEM, texamt=0.3, gain=1.1),
    'void': Mat(VOIDM, gain=0.3),
}
AMBC = (255, 180, 50)


def leafcl(p, x, y, n, r, seed, spread=1.0):
    rng = np.random.default_rng(seed)
    for k in range(n):
        a = rng.random() * 6.283
        d = r * math.sqrt(rng.random())
        lx, ly = x + math.cos(a) * d * spread, y + math.sin(a) * d * 0.8
        ang = rng.random() * 6.283
        L = 3.2 + rng.random() * 1.8
        p.poly([(lx + math.cos(ang) * L, ly + math.sin(ang) * L), (lx + math.cos(ang + 1.6) * 1.8, ly + math.sin(ang + 1.6) * 1.8),
                (lx - math.cos(ang) * L * 0.5, ly - math.sin(ang) * L * 0.5), (lx + math.cos(ang - 1.6) * 1.8, ly + math.sin(ang - 1.6) * 1.8)], mat='leaf', raise_=0.6, edge=0.1)


def shroom(p, x, y, r, h, tilt=0.0):
    p.poly([(x - 0.9, y), (x + 0.9, y), (x + 0.7 + tilt, y - h), (x - 0.7 + tilt, y - h)], mat='stem', raise_=0.5)
    pts = [(x + tilt + math.cos(math.radians(a)) * r, y - h + math.sin(math.radians(a)) * r * 0.62) for a in range(180, 361, 30)]
    p.poly(pts, mat='fung', raise_=1.0, edge=0.08)
    p.ell(x + tilt - r * 0.15, y - h - r * 0.22, r * 0.55, r * 0.28, op='emit', v=0.8, soft=0.4)


def build_parts():
    P = []

    def add(*a, **k):
        p = Part(*a, **k); P.append(p); return p
    add('root', None, (96, 156), ghost=True)
    # ------------------------------------------------ raices del suelo
    rt = add('roots', 'root', (0, 0), z=0.3, mat='root', depth=3.0, noise=0.4, seed=3, tnoise=0.25)
    for sgn in (-1, 1):
        for k, (L, h, w) in enumerate(((52, 8, 4.2), (74, 3, 3.4), (36, 14, 3.4))):
            pts = bez((sgn * 14, 1), (sgn * (14 + L * 0.5), 3 - h), (sgn * (14 + L), 2 - h * 0.2), n=10)
            rt.tube(pts, w, w * 0.25, spline=False)
    rt.hatch(3.0, 80, v=0.1, w=0.7, jit=0.5, seed=1)
    # ------------------------------------------------ cadera y piernas
    hip = add('hip', 'root', (0, -44), z=4, mat='bark', depth=9.0, noise=0.8, seed=5, tnoise=0.3)
    hip.spl([(-22, -6), (-10, -9), (10, -9), (23, -5), (27, 6), (19, 14), (0, 16), (-19, 14), (-27, 6)])
    hip.hatch(3.2, 88, v=0.08, w=0.8, jit=0.6, seed=2)
    hip.cracks(3, 8, v=0.04, w=0.8, seed=4, emit=0.4)
    hip.blotch('moss', 0.7, 3.0, 5, raise_=0.5)
    for nm, x, z, dim in (('b', -13, 2, -0.22), ('f', 13, 5, 0.0)):
        th = add('thigh_' + nm, 'hip', (x, 5), z=z, mat='bark', depth=8.0, noise=0.8, seed=10, dim=dim, tnoise=0.3)
        th.spl([(-11, -4), (-4, -7), (7, -7), (12, -2), (13, 10), (9, 22), (-7, 22), (-12, 10)])
        th.hatch(3.0, 90, v=0.07, w=0.8, jit=0.6, seed=3)
        th.cracks(2, 9, v=0.04, w=0.8, seed=11, emit=0.45)
        th.blotch('moss', 0.72, 3.0, 12, raise_=0.5)
        sh = add('shin_' + nm, 'thigh_' + nm, (0, 19), z=z + 0.1, mat='bark', depth=7.0, noise=0.8, seed=14, dim=dim, tnoise=0.3)
        sh.spl([(-10, -4), (9, -4), (11, 6), (7, 16), (-6, 16), (-10, 6)])
        sh.hatch(3.0, 92, v=0.07, w=0.8, jit=0.6, seed=4)
        sh.cracks(1, 8, v=0.04, w=0.8, seed=15, emit=0.45)
        sh.ell(2, 4, 3.4, 3.0, mat='rot', raise_=-0.8, edge=0.08)
        ft = add('foot_' + nm, 'shin_' + nm, (0, 14), z=z + 0.2, mat='root', depth=5.0, noise=0.6, seed=18, dim=dim, tnoise=0.3)
        ft.spl([(-12, -3), (6, -4), (14, 0), (24, 5), (32, 11), (22, 10), (27, 15), (14, 11), (9, 14), (-3, 10), (-13, 13), (-16, 4)], per=5)
        ft.hatch(3.0, 20, v=0.07, w=0.7, jit=0.5, seed=5)
    # ------------------------------------------------ ramas traseras
    br = add('branch_b', 'hip', (-14, -14), z=0.5, mat='bark', depth=4.0, noise=0.6, seed=22, tnoise=0.25)
    br.tube(bez((0, 0), (-18, -22), (-26, -52), (-20, -76), n=14), 8, 2.4, spline=False)
    br.tube(bez((-14, -34), (-24, -42), (-40, -46), n=8), 4.2, 1.2, spline=False)
    br.tube(bez((-23, -58), (-32, -66), (-36, -82), n=8), 3.6, 1.0, spline=False)
    br.tube(bez((-16, -62), (-10, -76), (-12, -92), n=8), 3.0, 1.0, spline=False)
    br.hatch(3.0, 80, v=0.08, w=0.7, jit=0.5, seed=6)
    leafcl(br, -38, -48, 9, 8, 3)
    leafcl(br, -35, -84, 8, 7, 4)
    leafcl(br, -12, -93, 7, 6, 5)
    leafcl(br, -20, -76, 6, 7, 6)
    # ------------------------------------------------ torso
    to = add('torso', 'hip', (0, -8), z=6, mat='bark', depth=13.0, noise=1.0, seed=20, tnoise=0.3)
    to.spl([(-20, 8), (-26, -8), (-30, -26), (-26, -42), (-14, -52), (8, -54), (24, -46), (30, -30), (27, -10), (21, 8), (0, 12)], per=6)
    to.hatch(3.4, 88, v=0.07, w=0.9, jit=0.7, seed=7)
    to.hatch(7.0, 84, v=0.03, w=0.8, jit=0.6, seed=8)
    to.blotch('moss', 0.68, 3.4, 21, raise_=0.6)
    to.blotch('rot', 0.76, 3.0, 22, raise_=-0.4)
    to.cracks(7, 16, v=0.04, w=0.9, seed=23, emit=0.55, branch=0.9, spread=0.6)
    # hueco del pecho con hongos
    to.spl([(-11, -28), (-5, -38), (5, -38), (11, -29), (9, -12), (-9, -12)], mat='void', raise_=-2.0)
    to.line([(-12, -12), (12, -12)], 1.0, op='tex', v=0.05)
    shroom(to, -4, -12, 4.0, 7)
    shroom(to, 3, -12, 3.2, 11, 1)
    shroom(to, 7.5, -12, 2.4, 5)
    shroom(to, -7.5, -12, 2.2, 4, -1)
    to.ell(0, -22, 6, 8, op='emit', v=0.35, soft=1.4)
    # hongos de repisa
    for sx, sy, r, z_ in ((-27, -24, 8, 1), (28, -14, 7, 1), (-24, -4, 6, 1), (26, -36, 6, 1)):
        side = -1 if sx < 0 else 1
        to.poly([(sx, sy + 2), (sx + side * r, sy + 1), (sx + side * r * 0.8, sy - 3), (sx, sy - 4)], mat='fung', raise_=1.2, edge=0.08)
        to.ell(sx + side * r * 0.4, sy - 1, r * 0.4, 1.0, op='emit', v=0.7, soft=0.4)
    shroom(to, 14, -50, 3.2, 6, 1)
    shroom(to, -16, -48, 2.6, 5, -1)
    # ------------------------------------------------ cabeza y cara
    hd = add('head', 'torso', (4, -48), z=9, mat='wood', depth=8.0, noise=0.7, seed=30, tnoise=0.25)
    hd.spl([(-14, 4), (-16, -8), (-10, -18), (4, -23), (17, -17), (21, -5), (17, 6), (4, 10), (-8, 9)])
    hd.hatch(3.0, 80, v=0.08, w=0.8, jit=0.6, seed=9)
    hd.blotch('moss', 0.72, 3.0, 31, raise_=0.5)
    hd.spl([(-1, -13), (8, -15), (14, -10), (9, -4.5), (0, -7)], mat='void', raise_=-1.2)
    hd.spl([(-13, -9), (-7, -13), (-3, -9), (-8, -5.5)], mat='void', raise_=-1.0)
    hd.ell(8.5, -9.5, 3.8, 3.0, op='emit', v=1.0, soft=0.25)
    hd.ell(-7, -9, 2.4, 2.0, op='emit', v=0.9, soft=0.3)
    hd.poly([(-4, -17), (9, -20), (19, -14), (17, -11), (8, -15.5), (-3, -13)], mat='bark', raise_=1.5, edge=0.08)
    hd.poly([(10, -6), (15, -2), (12, 3), (8, 0)], mat='bark', raise_=1.5, edge=0.08)
    hd.line([(-9, -3), (-4, 3)], 1.0, op='tex', v=0.06)
    hd.cracks(3, 8, v=0.05, w=0.7, seed=32, emit=0.5)
    hd.spl([(-3, 2), (14, 1), (18, 5), (11, 9), (0, 9), (-4, 6)], mat='void', raise_=-1.2)
    hd.poly([(0, 1.5), (3, 1.5), (1.5, 5)], mat='wood', raise_=1.0)
    hd.poly([(6, 1.5), (9, 1.5), (7.5, 4.5)], mat='wood', raise_=1.0)
    hd.poly([(12, 1.5), (15, 1.5), (13.5, 4)], mat='wood', raise_=1.0)
    jw = add('jaw', 'head', (2, 6), z=8.5, mat='wood', depth=4.0, noise=0.5, seed=33, tnoise=0.2)
    jw.spl([(-6, -1), (16, -1), (19, 3), (14, 9), (4, 12), (-5, 8)])
    jw.hatch(3.0, 70, v=0.08, w=0.8, jit=0.6, seed=10)
    for k in range(4):
        jw.poly([(-1 + k * 4.6, -1), (1.8 + k * 4.6, -1), (0.6 + k * 4.6, -5.5 + (k % 2))], mat='wood', raise_=0.8, edge=0.1)
    ms = add('moss', 'jaw', (2, 8), z=8.4, mat='moss', depth=3.5, noise=0.6, seed=34, tnoise=0.35)
    ms.poly([(-6, -2), (12, -2), (13, 7), (9, 14), (10, 22), (6, 16), (3, 25), (0, 17), (-3, 23), (-6, 14), (-8, 8)])
    ms.hatch(2.0, 84, v=0.2, w=0.6, jit=0.6, seed=11)
    ms.cracks(2, 8, v=0.15, w=0.7, seed=35)
    cr = add('crown', 'head', (0, -20), z=3.5, mat='bark', depth=4.0, noise=0.6, seed=36, tnoise=0.25)
    for (x0, x1, ex, ey, w0) in ((-6, -14, -30, -46, 4.6), (2, 2, -4, -50, 4.0), (8, 16, 26, -42, 4.4), (12, 22, 40, -28, 3.6), (-10, -24, -44, -20, 3.4)):
        cr.tube(bez((x0, 2), (x1, -16), (ex * 0.7, ey * 0.8), (ex, ey), n=12), w0, 1.0, spline=False)
    cr.tube(bez((-14, -34), (-20, -40), (-30, -40), n=6), 2.4, 0.8, spline=False)
    cr.tube(bez((12, -34), (20, -42), (28, -48), n=6), 2.6, 0.8, spline=False)
    cr.hatch(2.6, 80, v=0.08, w=0.7, jit=0.5, seed=12)
    leafcl(cr, -30, -46, 7, 7, 8)
    leafcl(cr, -4, -50, 6, 6, 9)
    leafcl(cr, 26, -42, 8, 7, 10)
    leafcl(cr, 40, -28, 5, 5, 11)
    leafcl(cr, -42, -20, 6, 6, 12)
    # ------------------------------------------------ brazos de rama
    for nm, x, z, dim in (('b', -27, 2.5, -0.22), ('f', 28, 10, 0.0)):
        ua = add('uarm_' + nm, 'torso', (x, -36), z=z, mat='bark', depth=7.0, noise=0.8, seed=44, dim=dim, tnoise=0.3)
        ua.spl([(-11, -8), (-2, -11), (9, -9), (12, -2), (10, 12), (7, 24), (-5, 24), (-9, 12), (-13, 0)])
        ua.hatch(3.0, 84, v=0.07, w=0.8, jit=0.6, seed=13)
        ua.blotch('moss', 0.7, 3.0, 45, raise_=0.5)
        ua.cracks(2, 9, v=0.04, w=0.8, seed=46, emit=0.45)
        ua.poly([(-7, 6), (-17, 0), (-10, 11)], mat='bark', raise_=0.8, edge=0.08)
        leafcl(ua, -17, -1, 4, 4, 47 + (nm == 'f'))
        fa = add('farm_' + nm, 'uarm_' + nm, (0, 22), z=z + 0.1, mat='bark', depth=6.5, noise=0.8, seed=48, dim=dim, tnoise=0.3)
        fa.spl([(-9, -4), (8, -4), (10, 8), (8, 20), (5, 28), (-4, 28), (-8, 18), (-10, 6)])
        fa.hatch(3.0, 88, v=0.07, w=0.8, jit=0.6, seed=14)
        fa.cracks(2, 9, v=0.04, w=0.8, seed=49, emit=0.45)
        fa.ell(0, 0, 8.5, 6.5, mat='wood', raise_=1.2, edge=0.08)
        fa.poly([(7, 10), (15, 8), (10, 16)], mat='bark', raise_=0.8, edge=0.08)
        fa.poly([(-7, 14), (-14, 20), (-6, 21)], mat='bark', raise_=0.8, edge=0.08)
        hn = add('hand_' + nm, 'farm_' + nm, (0, 26), z=z + 0.2, mat='bark', depth=5.0, noise=0.6, seed=50, dim=dim, tnoise=0.3)
        hn.spl([(-8, -3), (8, -3), (11, 5), (7, 11), (-6, 11), (-11, 4)])
        for k, (fx_, dx, L) in enumerate(((-7, -4, 24), (-2.5, -1, 28), (2.5, 2, 28), (7, 5, 22))):
            hn.tube(bez((fx_, 6), (fx_ + dx * 0.4, 6 + L * 0.5), (fx_ + dx, 6 + L), n=8), 3.1, 0.7, spline=False)
        hn.tube(bez((-9, 2), (-16, 8), (-18, 16), n=6), 2.6, 0.7, spline=False)
        hn.hatch(2.4, 85, v=0.07, w=0.6, jit=0.5, seed=15)
        hn.blotch('moss', 0.78, 2.5, 51, raise_=0.4)
    return P


def make(anims, fxhook):
    parts = build_parts()
    return Boss('ent_ancestral', (192, 160), (96, 156), (60, 118), parts, MATS, anims, fxhook,
                outline=(14, 8, 12), rim=(255, 190, 90), rimk=0.36, dis_col=(255, 190, 70), seed=51, post=None, scale=0.82, base=0.44)


# ====================================================================== animacion
def LG(thf, shf, thb, shb):
    return {'thigh_f': thf, 'shin_f': shf, 'foot_f': -(thf + shf), 'thigh_b': thb, 'shin_b': shb, 'foot_b': -(thb + shb)}


def AR(uf, ff, ub, fb, hf=0, hb=0):
    return {'uarm_f': uf, 'farm_f': ff, 'hand_f': hf, 'uarm_b': ub, 'farm_b': fb, 'hand_b': hb}


def T(torso=0, head=0, jaw=0, ry=0, rx=0, hip=0):
    return {'torso': torso, 'head': head, 'jaw': jaw, 'root.y': ry, 'root.x': rx, 'hip': hip}


def PZ(*ds):
    return merge(*ds)


STAND = PZ(LG(-4, 8, 6, -2), AR(-6, -10, 12, -4), T(3, 0, 0, 0))


def sway(f, n, amp=1.0, base=0.0, ph=0.0):
    return {'moss': base + amp * 4.0 * S(f, n, ph), 'crown': amp * 1.6 * S(f, n, ph + 0.1), 'branch_b': amp * 1.4 * S(f, n, ph + 0.2) + base * 0.3}


def idle_pose(f):
    b = S(f, 6)
    return PZ(STAND, {'root.y': -0.6 * b, 'torso': 1.0 * b, 'head': -1.4 * b, 'jaw': 2 + 1.5 * b, 'uarm_f': 1.4 * b, 'uarm_b': -1.0 * b, 'farm_f': 1.8 * b, 'hand_f': 3 * b, 'hand_b': -2 * b}, sway(f, 6, 1.0))


def walk_pose(f):
    ph = 2 * math.pi * f / 8
    s = math.sin(ph); c = math.cos(ph)
    thf = 16 * s - 3
    thb = -16 * s + 3
    shf = 8 + 16 * max(0, -c * 0.9 + 0.1) * (1 if s < 0.3 else 0.3) + 4 * max(0, c)
    shb = 8 + 16 * max(0, c * 0.9 + 0.1) * (1 if s > -0.3 else 0.3) + 4 * max(0, -c)
    return PZ(LG(thf, shf, thb, shb), AR(-8 - 16 * s, -12 - 10 * s, 12 + 16 * s, -4 + 8 * s, 6 * s, -6 * s),
              T(4 + 2 * c, -2 + c, 2 + c, -2.6 * abs(c) + 1, 0, 1.5 * s), {'torso': 3 * s}, sway(f, 8, 1.4, 6))


W1 = K([(0, STAND),
        (1, PZ(LG(-8, 12, 8, -5), AR(-60, -60, 12, -6), T(-3, -3, 3, 1, -2))),
        (2, PZ(LG(-10, 16, 10, -8), AR(-114, -50, 12, -8), T(-8, -6, 8, 2, -4))),
        (3, PZ(LG(-12, 18, 12, -10), AR(-148, -34, 12, -8), T(-13, -9, 14, 3, -6), {'hand_f': 20})),
        (4, PZ(LG(-12, 18, 12, -10), AR(-158, -28, 12, -8), T(-16, -11, 18, 3.5, -7), {'hand_f': 28}))])


def wind1(f):
    t = f / 4.0
    return PZ(W1(f), sway(f, 5, 0.8, -4 * t), {'emit': 1 + 0.15 * f})


W1E = PZ(LG(-12, 18, 12, -10), AR(-158, -28, 12, -8), T(-16, -11, 18, 3.5, -7), {'hand_f': 28})
A1 = K([(0, W1E, 'sm'),
        (1, PZ(LG(-14, 20, 14, -10), AR(-132, -36, 12, -8), T(-6, -5, 12, 3, -2), {'hand_f': 10}), 'snap'),
        (2, PZ(LG(-20, 26, 18, -12), AR(-66, -26, 12, -10), T(12, 6, 4, 4, 7), {'hand_f': -6}), 'snap'),
        (3, PZ(LG(-24, 30, 20, -14), AR(-32, -16, 14, -12), T(22, 12, 2, 5, 12), {'hand_f': -10}), 'snap'),
        (4, PZ(LG(-24, 30, 20, -14), AR(-28, -12, 14, -12), T(22, 12, 2, 5, 12), {'hand_f': -10}), 'out'),
        (5, PZ(LG(-20, 26, 16, -12), AR(-26, -12, 12, -10), T(18, 10, 3, 4.5, 10)), 'sm'),
        (6, PZ(LG(-12, 18, 10, -8), AR(-14, -12, 10, -8), T(8, 4, 2, 2.5, 4)), 'sm'),
        (7, STAND, 'sm')])


def atk1(f):
    return PZ(A1(f), sway(f, 8, 1.2, -8 + f))


W2 = K([(0, STAND),
        (1, PZ(LG(-8, 14, 8, -6), AR(-30, -50, -20, -50), T(-4, -2, 6, 1, -2))),
        (2, PZ(LG(-12, 20, 12, -10), AR(-10, -70, -4, -76), T(-9, -5, 12, 3, -5))),
        (3, PZ(LG(-14, 24, 14, -12), AR(10, -86, 12, -92), T(-14, -8, 18, 5, -8))),
        (4, PZ(LG(-14, 26, 14, -14), AR(14, -96, 16, -100), T(-17, -10, 22, 7, -10)))])


def wind2(f):
    t = f / 4.0
    return PZ(W2(f), sway(f, 5, 0.6, 4 * t), {'emit': 1 + 0.15 * f})


W2E = PZ(LG(-14, 26, 14, -14), AR(14, -96, 16, -100), T(-17, -10, 22, 7, -10))
A2 = K([(0, W2E, 'sm'),
        (1, PZ(LG(-22, 28, 16, -14), AR(-70, -40, -60, -50), T(4, 0, 12, 5, 4)), 'snap'),
        (2, PZ(LG(-30, 36, 22, -18), AR(-100, -4, -92, -8), T(20, 8, 6, 7, 18)), 'snap'),
        (3, PZ(LG(-32, 38, 24, -18), AR(-104, 0, -96, -4), T(26, 10, 4, 8, 24)), 'out'),
        (4, PZ(LG(-32, 38, 24, -18), AR(-104, 0, -96, -4), T(26, 10, 4, 8, 24)), 'sm'),
        (5, PZ(LG(-28, 34, 22, -16), AR(-90, -6, -80, -8), T(22, 8, 4, 7, 20)), 'sm'),
        (6, PZ(LG(-16, 22, 12, -10), AR(-40, -14, -10, -10), T(10, 3, 4, 4, 8)), 'sm'),
        (7, STAND, 'sm')])


def atk2(f):
    return PZ(A2(f), sway(f, 8, 1.4, -12 + f * 1.5))


W3 = K([(0, STAND),
        (1, PZ(LG(-26, 50, 24, -44), AR(-70, -40, -62, -40), T(8, 2, 2, 12, -2))),
        (2, PZ(LG(-30, 62, 28, -54), AR(-110, -30, -104, -34), T(2, -2, 8, 18, -4))),
        (3, PZ(LG(-32, 70, 30, -60), AR(-136, -30, -130, -34), T(-6, -6, 14, 22, -5))),
        (4, PZ(LG(-34, 72, 30, -62), AR(-148, -34, -142, -38), T(-12, -10, 20, 24, -6))),
        (5, PZ(LG(-34, 72, 30, -62), AR(-152, -36, -146, -40), T(-14, -12, 24, 25, -6)))])


def wind3(f):
    t = f / 5.0
    return PZ(W3(f), sway(f, 6, 1.0, -6 * t), {'emit': 1 + 0.2 * f})


W3E = PZ(LG(-34, 72, 30, -62), AR(-152, -36, -146, -40), T(-14, -12, 24, 25, -6))
A3 = K([(0, W3E, 'sm'),
        (1, PZ(LG(-8, 12, 8, -6), AR(-146, -36, -140, -40), T(-6, -6, 14, -10, 2)), 'out'),
        (2, PZ(LG(-6, 8, 6, -6), AR(-134, -40, -128, -44), T(0, 0, 10, -22, 4)), 'sm'),
        (3, PZ(LG(-10, 14, 10, -10), AR(-100, -30, -96, -34), T(12, 6, 6, -12, 8)), 'in'),
        (4, PZ(LG(-26, 50, 24, -44), AR(-30, -18, -26, -20), T(32, 16, 2, 12, 10)), 'snap'),
        (5, PZ(LG(-30, 56, 28, -50), AR(-22, -14, -18, -16), T(36, 18, 0, 16, 10)), 'sm'),
        (6, PZ(LG(-28, 52, 26, -46), AR(-22, -14, -18, -16), T(34, 16, 0, 14, 10)), 'sm'),
        (7, PZ(LG(-18, 30, 14, -24), AR(-14, -12, -8, -12), T(18, 8, 2, 6, 5)), 'sm'),
        (8, STAND, 'sm')])


def atk3(f):
    return PZ(A3(f), sway(f, 9, 1.4, 10 if f in (1, 2, 3) else -4))


CAST = K([(0, STAND),
          (1, PZ(LG(-8, 12, 8, -6), AR(-30, -40, -26, -40), T(-3, -3, 6, 1, -1))),
          (2, PZ(LG(-10, 16, 10, -8), AR(-70, -50, -64, -50), T(-8, -8, 12, 2, -2)), 'sm'),
          (3, PZ(LG(-12, 18, 12, -10), AR(-100, -34, -94, -36), T(-12, -12, 20, 3, -3)), 'sm'),
          (4, PZ(LG(-12, 20, 12, -10), AR(-90, -30, -86, -32), T(-2, -14, 34, 3, -1)), 'snap'),
          (5, PZ(LG(-10, 16, 10, -8), AR(-84, -26, -82, -28), T(0, -8, 26, 2, 0)), 'out'),
          (6, PZ(LG(-8, 12, 8, -6), AR(-50, -20, -40, -20), T(2, -2, 10, 1.5, 0)), 'sm'),
          (7, STAND, 'sm')])


def cast(f):
    k = 0.2 + 0.5 * (1 if 2 <= f <= 5 else 0)
    return PZ(CAST(f), sway(f, 8, 1.4, 0), {'emit': 1 + 0.9 * clamp01(1 - abs(f - 4) / 3.0)})


def hurt(f):
    i = int(f)
    d = [PZ(LG(-4, 8, 6, -2), AR(-14, -18, 18, 0), T(-10, -8, 10, 1, -4), {'tint': ((255, 236, 210), 0.5)}),
         PZ(LG(-4, 8, 6, -2), AR(-8, -12, 14, -4), T(-4, -4, 5, 0.5, -2), {'tint': ((255, 236, 210), 0.15)})][i]
    return PZ(d, sway(f, 2, 1.5, 8 - 5 * i))


PHK = K([(0, STAND),
         (1, PZ(LG(-8, 14, 8, -6), AR(-20, -60, -16, -60), T(-6, -6, 8, 2, -1)), 'sm'),
         (2, PZ(LG(-12, 20, 12, -10), AR(-110, -50, -104, -50), T(-12, -10, 14, 4, -2)), 'sm'),
         (3, PZ(LG(-14, 24, 14, -14), AR(-150, -30, -144, -34), T(-20, -16, 36, 6, -3)), 'snap'),
         (4, PZ(LG(-14, 24, 14, -14), AR(-158, -26, -152, -30), T(-24, -20, 40, 6, -3)), 'sm'),
         (5, PZ(LG(-14, 24, 14, -14), AR(-160, -24, -154, -28), T(-26, -22, 42, 6, -3)), 'sm'),
         (6, PZ(LG(-16, 30, 16, -18), AR(-70, -90, -60, -90), T(14, 6, 28, 2, 2)), 'in'),
         (7, PZ(LG(-18, 30, 16, -18), AR(-30, -100, -24, -96), T(18, 8, 30, 2, 3)), 'snap'),
         (8, PZ(LG(-14, 22, 12, -14), AR(-60, -80, -50, -80), T(10, 2, 16, 2, 1)), 'sm'),
         (9, STAND, 'sm')])


def phase(f):
    p = PHK(f)
    i = int(f)
    fl = [0, 0.2, 0.3, 1.0, 1.4, 1.7, 1.5, 1.2, 0.7, 0.3][i]
    q = PZ(p, sway(f, 10, 2.0 + fl, 0), {'emit': 1 + 1.2 * fl, 'crown.s': 1 + 0.18 * fl, 'branch_b.s': 1 + 0.2 * fl})
    if 4 <= f <= 7:
        q['root.x'] = (1.2 if i % 2 else -1.2)
        q['tint'] = ((255, 190, 80), 0.12)
    return q


INTRO_RISE = [120, 120, 112, 98, 82, 64, 48, 34, 22, 12, 5, 1, 0, 0]


def intro(f):
    i = int(f)
    ry = INTRO_RISE[i] if f == i else INTRO_RISE[i] + (INTRO_RISE[min(13, i + 1)] - INTRO_RISE[i]) * (f - i)
    lift = clamp01((f - 8) / 4.0)
    p = PZ(STAND, {'root.y': ry}, AR(-6 - 70 * (1 - lift), -10 - 30 * (1 - lift), 12 + 20 * (1 - lift), -4 - 20 * (1 - lift)),
           T(3 - 3 * (1 - lift) + 0, 6 * (1 - lift), 0), sway(f, 14, 1.4, 10 * (1 - lift)))
    p['crown.s'] = 0.3 + 0.7 * clamp01((f - 6) / 5.0)
    p['branch_b.s'] = 0.3 + 0.7 * clamp01((f - 6) / 5.0)
    p['jaw'] = 3 + 30 * clamp01((f - 9) / 2.0) * (1 - clamp01((f - 12) / 1.5))
    p['emit'] = 0.3 + 0.7 * clamp01((f - 5) / 5.0) + (0.6 if 10 <= f <= 12 else 0)
    p['clip'] = (0, 0, 192, 156)
    if f < 2:
        p['clip'] = (0, 0, 0, 0)
    return p


DEATH = K([(0, PZ(LG(-4, 8, 6, -2), AR(-14, -18, 18, 0), T(-10, -8, 10, 1, -4), {'tint': ((255, 236, 210), 0.55)}), 'out'),
           (1, PZ(LG(-8, 14, 8, -6), AR(-30, -24, 24, 10), T(-14, -12, 24, 2, -6), {'tint': ((255, 236, 210), 0.25)}), 'sm'),
           (2, PZ(LG(-12, 24, 10, -12), AR(-70, -26, 40, 20), T(-14, -14, 36, 4, -8), {'tint': ((255, 236, 210), 0.0)}), 'sm'),
           (3, PZ(LG(-18, 40, 14, -26), AR(-110, -20, 56, 28), T(-6, -14, 40, 10, -10)), 'sm'),
           (4, PZ(LG(-28, 62, 20, -46), AR(-130, -10, 70, 34), T(8, -4, 34, 18, -8)), 'in'),
           (5, PZ(LG(-38, 84, 26, -66), AR(-100, -4, 84, 36), T(26, 12, 26, 28, -2)), 'in'),
           (6, PZ(LG(-46, 100, 30, -80), AR(-70, 0, 70, 30), T(44, 26, 20, 36, 4)), 'sm'),
           (8, PZ(LG(-50, 110, 32, -90), AR(-50, 0, 54, 24), T(62, 38, 16, 42, 10)), 'sm'),
           (13, PZ(LG(-52, 116, 34, -96), AR(-40, 0, 44, 20), T(70, 44, 12, 44, 12)), 'lin')])

FALL = {'head': (14, 1, 20), 'crown': (10, 1, 22), 'branch_b': (-8, -1, 12), 'uarm_f': (10, 1, 14), 'farm_f': (16, 1, 20), 'hand_f': (22, 1, 24),
        'uarm_b': (-10, -1, 12), 'farm_b': (-14, -1, 18), 'hand_b': (-20, -1, 22), 'moss': (6, 1, 10)}


def death(f):
    p = dict(DEATH(f))
    sap = max(0.0, 1.0 - clamp01((f - 1) / 6.0))
    p['emit'] = 0.12 + 0.88 * sap + (1.0 if 1 <= f <= 3 else 0)
    p['lit'] = -0.1 * clamp01((f - 3) / 5.0)
    if f >= 4:
        p['tint'] = ((76, 62, 56), 0.4 * clamp01((f - 4) / 5.0))
    p.update(sway(min(f, 7), 14, 0.6, 8 + f))
    p['crown.s'] = 1 - 0.3 * clamp01((f - 4) / 6.0)
    for nm, (dx, sgn, dy) in FALL.items():
        t = clamp01((f - 4.0) / 6.0)
        g = t * t
        p[nm + '.x'] = p.get(nm + '.x', 0) + dx * g * 0.5
        p[nm + '.y'] = p.get(nm + '.y', 0) + dy * g * 0.5
        p[nm] = p.get(nm, 0) + sgn * 30 * g
    if f >= 9:
        d = clamp01((f - 9.0) / 4.8)
        p['dis'] = d * 1.12
        p['dis_dir'] = -1.0
    return p


# ====================================================================== efectos
def root_spike(ctx, x, y, h, w, a=1.0, layer='front', sway_=0.0, seed=0):
    fx = ctx.fx
    rng = np.random.default_rng(seed)
    bend = (rng.random() - 0.5) * 14 + sway_
    pts = bez((x, y), (x + bend * 0.2, y - h * 0.5), (x + bend, y - h * 0.8), (x + bend * 0.6 + (rng.random() - 0.5) * 6, y - h), n=9)
    L = []; R = []
    for k, (px, py) in enumerate(pts):
        u = k / (len(pts) - 1)
        ww = w * (1 - u * 0.88) + 0.3
        L.append((px - ww, py)); R.append((px + ww, py))
    outline = [(px - 1.2, py + (0.8 if k == 0 else 0)) for k, (px, py) in enumerate(L)] + [(px + 1.2, py + (0.8 if k == 0 else 0)) for k, (px, py) in list(enumerate(R))[::-1]]
    fx.poly(outline, (22, 12, 14), a, layer, ss=2)
    fx.poly(L + R[::-1], (96, 66, 44), a, layer, ss=2)
    hl = [(px - ww_ * 0.95, py) for (px, py), ww_ in zip(pts, [w * (1 - k / 8 * 0.88) for k in range(len(pts))])]
    hl2 = [(px - ww_ * 0.15, py) for (px, py), ww_ in zip(pts, [w * (1 - k / 8 * 0.88) for k in range(len(pts))])]
    fx.poly(hl + hl2[::-1], (170, 124, 76), a * 0.9, layer, ss=2)
    rr = [(px + ww_ * 0.2, py) for (px, py), ww_ in zip(pts, [w * (1 - k / 8 * 0.88) for k in range(len(pts))])]
    rr2 = [(px + ww_ * 0.95, py) for (px, py), ww_ in zip(pts, [w * (1 - k / 8 * 0.88) for k in range(len(pts))])]
    fx.poly(rr + rr2[::-1], (52, 34, 30), a * 0.9, layer, ss=2)
    fx.polyline(pts[1:-2], 1, (255, 176, 48), a * 0.55, layer)
    # espina lateral
    mid = pts[len(pts) // 2]
    fx.poly([(mid[0] + w * 0.6, mid[1]), (mid[0] + w * 3.2, mid[1] - 5), (mid[0] + w * 0.6, mid[1] - 3)], (96, 66, 44), a, layer, ss=2)


def leaf_fall(ctx, x, y, w, h, n, t, seed=1, a=0.95, layer='front', cols=None):
    rng = np.random.default_rng(seed)
    cols = cols or [(214, 150, 40), (180, 110, 30), (130, 140, 50), (240, 190, 70)]
    for k in range(n):
        ph = rng.random()
        life = (t * 1.3 + ph) % 1.0
        px = x + (rng.random() - 0.5) * w + math.sin((life + ph) * 9) * 4
        py = y + life * h
        c = cols[k % len(cols)]
        rot = life * 9 + k
        L = 2.4 + rng.random() * 1.4
        pts = [(px + math.cos(rot) * L, py + math.sin(rot) * L * 0.6), (px + math.cos(rot + 1.7) * 1.2, py + math.sin(rot + 1.7) * 0.8),
               (px - math.cos(rot) * L * 0.6, py - math.sin(rot) * L * 0.4), (px + math.cos(rot - 1.7) * 1.2, py + math.sin(rot - 1.7) * 0.8)]
        ctx.fx.poly(pts, c, a * math.sin(life * math.pi) ** 0.5, layer, ss=2)


def moth(ctx, x, y, flap, s=1.0, a=1.0):
    fx = ctx.fx
    w = 3.4 * s * (0.35 + 0.65 * abs(math.sin(flap)))
    fx.glow(x, y, 6 * s, (255, 190, 70), 0.55 * a)
    fx.poly([(x, y), (x - w, y - 2.4 * s), (x - w * 0.9, y + 1.2 * s)], (255, 214, 120), a, 'front', ss=2)
    fx.poly([(x, y), (x + w, y - 2.4 * s), (x + w * 0.9, y + 1.2 * s)], (255, 190, 70), a, 'front', ss=2)
    fx.dots([(x, y)], (120, 70, 30), a, 'front')


def spore_ball(ctx, x, y, s=1.0, ph=0.0):
    fx = ctx.fx
    fx.glow(x, y, 12 * s, (255, 176, 40), 0.8)
    fx.ell(x, y, 5.6 * s, 5.0 * s, (70, 40, 20), 1.0, 'front')
    fx.ell(x - 0.4, y - 0.4, 4.6 * s, 4.2 * s, (150, 100, 40), 1.0, 'front')
    fx.ell(x - 0.9, y - 0.9, 3.0 * s, 2.6 * s, (255, 190, 60), 1.0, 'front')
    fx.ell(x - 1.2, y - 1.2, 1.3 * s, 1.1 * s, (255, 250, 210), 1.0, 'front')
    for k in range(6):
        a = ph + k * 1.1
        fx.dots([(x - 6 * s - k * 2.4 + math.cos(a), y + math.sin(a) * 4 + (k % 3 - 1) * 2)], [(255, 220, 110), (255, 176, 40), (190, 220, 90)][k % 3], 0.9, 'front')
    fx.polyline([(x - 4 * s, y), (x - 12 * s, y + 1), (x - 22 * s, y + 1)], 3, (255, 150, 30), 0.4, 'front')


def spores(ctx, x, y, w, h, n, t=None, seed=1, a=0.9, rise=-18, layer='front'):
    wisps(ctx, x, y, w, h, n, [(255, 224, 120), (255, 176, 40), (200, 230, 100)], t=t, seed=seed, a=a, rise=rise, layer=layer)


def fxhook(ctx):
    n, i, fx = ctx.name, ctx.i, ctx.fx
    ax, ay = ctx.pivot
    W = ctx.W
    rng = ctx.rng
    ek = ctx.pose.get('emit', 1.0)
    hand = lambda nm='hand_f', f=None: ctx.anchor(nm, (0, 22)) if f is None else ctx.anchor_at(f, nm, (0, 22))
    ex, ey = ctx.anchor('head', (8.5, -9.5))
    ex2, ey2 = ctx.anchor('head', (-7, -9))
    cx_, cy_ = ctx.anchor('torso', (0, -22))
    if n != 'death' or i < 8:
        fx.glow(ex, ey, 8, (255, 176, 40), min(1.0, 0.6 * ek))
        fx.glow(ex2, ey2, 5, (255, 176, 40), min(1.0, 0.35 * ek))
        fx.glow(cx_, cy_, 14, (255, 160, 30), min(1.0, 0.4 * ek))
    if n not in ('intro', 'death'):
        spores(ctx, ax - 2, ay - 84, 90, 100, 12, seed=4, a=0.85, rise=-22)
        for k in range(3):
            ph = 2 * math.pi * (i / ctx.n + k / 3.0)
            moth(ctx, ax + math.cos(ph) * (48 + k * 6), ay - 90 + math.sin(ph * 2) * 12 - k * 14, i * 1.9 + k * 2, 0.9)
    if n == 'walk' and i in (1, 5):
        gx = ax + (14 if i == 1 else -14)
        dust(ctx, gx, ay, 0.35, (96, 74, 56), 6, 16, 5, 2.2, a=0.6)
    # --- ataque 1
    if n == 'windup1':
        t = i / 4.0
        x, y = hand()
        fx.glow(x, y, 12 + 14 * t, (255, 190, 70), 0.3 + 0.4 * t)
        leaf_fall(ctx, x, y - 14, 30, 30, 6, t, seed=3)
    if n == 'attack1':
        trail(ctx, 'hand_f', (0, 26), (0, 0), 0, 4, (255, 232, 160), (150, 90, 20), steps=12, span=3.2, mid=(230, 150, 40), a=0.75)
        if 2 <= i <= 6:
            x, y = hand(f=3.0)
            t = (i - 2) / 4.0
            gx = max(ax + 36, min(x + 4, W - 20))
            dust(ctx, gx, ay, t, (96, 74, 56), 12, 36, 12, 3.0, a=0.75)
            shock(ctx, gx, ay, t, (255, 200, 110), 40, 5, 2)
            for k, off in enumerate((-12, -4, 6, 14)):
                hh = (14 + 6 * (k % 2)) * clamp01(1.6 - t) * clamp01((i - 1.5) * 1.5)
                root_spike(ctx, gx + off, ay + 1, hh, 3.2, 0.95, 'front', seed=k + 2)
            leaf_fall(ctx, gx, ay - 24, 30, 24, 8, t, seed=5)
            if i == 2:
                fx.sparks(rng, gx, ay - 3, 12, 16, [(255, 240, 190), (255, 176, 40)], 'front', 10)
    # --- ataque 2
    if n == 'windup2':
        t = i / 4.0
        for nm in ('hand_f', 'hand_b'):
            x, y = hand(nm)
            fx.glow(x, y, 10 + 12 * t, (255, 190, 70), 0.3 + 0.5 * t)
        spores(ctx, ax, ay - 4, 70, 6, 10, t=t, seed=7, rise=-26)
    if n == 'attack2':
        if 1 <= i <= 6:
            tt = clamp01((i - 1) / 5.0)
            hx_, hy_ = hand()
            front = max(hx_, ax + 20)
            m = 9
            for k in range(m):
                px = front + 4 + k * 14 - 4
                prog = clamp01((i - 1 - k * 0.35) / 1.6)
                hh = (34 - k * 2.0 + (k % 3) * 6) * prog * (1 - tt * 0.45)
                if hh > 2 and px < W - 6:
                    root_spike(ctx, px, ay + 1, hh, 4.4 - k * 0.15, 1.0, 'front', sway_=(k % 3 - 1) * 4, seed=k + 20)
            dust(ctx, front + 20, ay, tt, (96, 74, 56), 10, 40, 8, 2.6, a=0.7)
            fx.glow(front + 10, ay - 8, 22, (255, 176, 40), 0.35 * (1 - tt))
            for k in range(3):
                yy = ay - 30 - k * 14
                fx.line((ax + 10, yy), (ax - 14 - k * 4, yy), 1, (255, 200, 110), 0.5 * (1 - tt), 'front')
        if 1 <= i <= 5:
            dust(ctx, ax - 8, ay, clamp01((i - 1) / 4.0), (96, 74, 56), 8, 18, 6, a=0.6)
    # --- ataque 3
    if n == 'windup3':
        t = i / 5.0
        fx.glow(ax, ay - 90, 30 + 26 * t, (255, 176, 40), 0.2 + 0.3 * t, rx=36, ry=50)
        spores(ctx, ax, ay - 4, 70, 6, 12, t=t, seed=5, rise=-34)
        leaf_fall(ctx, ax, ay - 130, 80, 70, 8, t, seed=9)
        for sgn in (-1, 1):
            for k in range(3):
                fx.line((ax + sgn * (30 + k * 14), ay), (ax + sgn * (30 + k * 14), ay - 6 * t * (k + 1)), 2, (96, 66, 44), 0.9 * t, 'back')
    if n == 'attack3':
        if 3 <= i <= 4:
            for nm in ('hand_f', 'hand_b'):
                trail(ctx, nm, (0, 26), (0, 0), 3, 4, (255, 232, 160), (150, 90, 20), steps=9, span=2.2, mid=(230, 150, 40), a=0.7)
        if 4 <= i <= 8:
            t = (i - 4) / 4.0
            gx = ax + 20
            ground_cracks(ctx, gx, ay + 1, t, (20, 12, 12), (255, 176, 40), 9, 76, 41)
            ground_cracks(ctx, ax - 24, ay + 1, t, (20, 12, 12), (255, 176, 40), 7, 58, 43)
            shock(ctx, gx, ay, t, (255, 200, 110), 86, 9, 2)
            dust(ctx, gx, ay, t, (96, 74, 56), 16, 58, 18, 3.4)
            if i <= 7:
                for k, off in enumerate((-80, -62, -44, -26, -8, 14, 32, 50, 68)):
                    px = gx + off + (k % 2) * 3
                    hh = (30 + 14 * ((k * 7) % 3)) * clamp01(1.5 - t * 0.4) * clamp01((i - 3.6 + abs(off) * 0.006) * 2)
                    if 5 < px < W - 5 and hh > 2:
                        root_spike(ctx, px, ay + 1, hh, 4.6, 1.0, 'front', sway_=(k % 3 - 1) * 5, seed=k + 60)
            leaf_fall(ctx, gx, ay - 70, 120, 70, 14, t, seed=11)
            if i == 4:
                fx.sparks(rng, gx, ay - 4, 22, 30, [(255, 240, 190), (255, 176, 40), (200, 150, 60)], 'front', 20)
    # --- cast
    if n == 'cast':
        mx, my = ctx.anchor('jaw', (10, 4))
        if 1 <= i <= 4:
            t = i / 4.0
            fx.glow(mx, my, 12 + 14 * t, (255, 176, 40), 0.4 + 0.5 * t)
            for k in range(8):
                ang = i * 0.9 + k * 0.8
                r = 24 * (1 - t * 0.6) + 2
                px = mx + math.cos(ang) * r; py = my + math.sin(ang) * r * 0.8
                fx.glow(px, py, 4, (255, 190, 60), 0.8)
                fx.dots([(px, py)], (255, 244, 190), 1.0, 'front')
            spores(ctx, cx_, cy_, 26, 30, 8, t=t, seed=2, rise=-14)
        if i >= 4:
            tt = (i - 4) / 3.0
            for k in range(3):
                sx_ = mx + 6 + tt * (44 + k * 14)
                sy_ = my - 4 + (k - 1) * 12 - tt * (k - 1) * -8 + math.sin(i + k) * 2
                if sx_ < W - 8:
                    spore_ball(ctx, sx_, sy_, 1.0 - tt * 0.25, i * 0.7 + k)
    # --- fase
    if n == 'phase':
        t = clamp01((i - 3) / 4.0)
        if 3 <= i <= 9:
            fx.glow(ax, ay - 70, 60 * t + 20, (255, 176, 40), 0.5 * (1 - abs(t - 0.5) * 1.1), rx=60 * t + 20, ry=76 * t + 14)
            rays(ctx, ax, ay - 74, t, (255, 200, 90), 16, 14, 82, 0.1, 0.55, i * 0.12, 'back', 'over')
            shock(ctx, ax, ay, clamp01((i - 3) / 5.0), (255, 200, 110), 76, 8, 2)
        if 4 <= i <= 8:
            for k, off in enumerate((-60, -40, -24, 24, 40, 60)):
                hh = (26 + 12 * (k % 2)) * clamp01((i - 3) / 2.0) * (1 - clamp01((i - 7) / 3.0) * 0.6)
                root_spike(ctx, ax + off, ay + 1, hh, 3.8, 0.95, 'front', sway_=(k % 3 - 1) * 4, seed=k + 80)
            spores(ctx, ax, ay - 70, 110, 110, 30, t=(i - 3) / 6.0, seed=22, rise=-48, a=1.0)
            leaf_fall(ctx, ax, ay - 130, 110, 110, 18, (i - 3) / 6.0, seed=13)
    if n == 'intro':
        intro_fx(ctx)
    if n == 'death':
        death_fx(ctx)


def mound(ctx, x, y, w, h, a=1.0, seed=3):
    fx = ctx.fx
    pts = [(x - w / 2, y + 1)]
    rng = np.random.default_rng(seed)
    for k in range(1, 9):
        u = k / 9.0
        pts.append((x - w / 2 + w * u, y - h * math.sin(math.pi * u) ** 0.8 + (rng.random() - 0.5) * 1.5))
    pts.append((x + w / 2, y + 1))
    fx.poly([(px, py - 1.2) for px, py in pts[:-1]] + [(pts[-1][0], pts[-1][1])], (24, 16, 16), a, 'back')
    fx.poly(pts, (82, 60, 44), a, 'back')
    fx.poly([(px - 1, py + 1.5) for px, py in pts[1:5]] + [(x - w / 4, y)], (130, 98, 66), a * 0.9, 'back')
    pile(ctx, x, y, w * 0.9, h * 0.8, [(96, 72, 52), (66, 48, 38), (120, 92, 62)], 12, seed=seed + 4, layer='back', outline=(20, 12, 12))


def intro_fx(ctx):
    i, fx, ax, ay = ctx.i, ctx.fx, ctx.pivot[0], ctx.pivot[1]
    rng = ctx.rng
    # montículo y raíces que brotan
    grow = clamp01(i / 3.0)
    mw = 110 * (0.5 + 0.5 * grow)
    flat = clamp01((i - 10) / 4.0)
    mound(ctx, ax, ay, mw, 16 * grow * (1 - 0.8 * flat), 1.0, 3)
    for k, off in enumerate((-48, -32, 30, 46)):
        hh = (18 + 8 * (k % 2)) * clamp01((i - 0.5) / 2.5) * (1 - clamp01((i - 7) / 5.0) * 0.8)
        if hh > 2:
            root_spike(ctx, ax + off, ay + 1, hh, 3.4, 1.0, 'front', sway_=(k - 1.5) * 3, seed=k + 5)
    if 2 <= i <= 11:
        t = clamp01((i - 2) / 8.0)
        dust(ctx, ax, ay - 2, t, (96, 74, 56), 14, 56, 14, 3.0, a=0.8)
        # terrones cayendo del tronco
        for k in range(10):
            r2 = np.random.default_rng(k + 90)
            px = ax + (r2.random() - 0.5) * 70
            py0 = ay - 40 - r2.random() * 60
            u = clamp01((t * 1.4 + r2.random() * 0.4) % 1.0)
            py = min(ay - 1, py0 + u * 80)
            if py < ay - 2:
                fx.ell(px, py, 1.8, 1.4, (96, 72, 52), 0.95, 'front')
    if 4 <= i <= 13:
        spores(ctx, ax, ay - 60, 70, 100, 12, t=(i - 4) / 9.0, seed=3, rise=-30)
    if 9 <= i <= 12:
        t = (i - 9) / 3.0
        fx.glow(ax, ay - 70, 50 * t + 20, (255, 190, 90), 0.4 * (1 - t * 0.5), rx=50 * t + 20, ry=60 * t + 20)
        rays(ctx, ax, ay - 70, t, (255, 190, 90), 12, 16, 70, 0.09, 0.4, i * 0.2, 'back', 'over')
        shock(ctx, ax, ay, t, (255, 200, 120), 70, 7, 2)
    if i >= 8:
        leaf_fall(ctx, ax, ay - 130, 100, 100, 12, (i - 8) / 6.0, seed=6)


def death_fx(ctx):
    i, fx, ax, ay = ctx.i, ctx.fx, ctx.pivot[0], ctx.pivot[1]
    rng = ctx.rng
    if 1 <= i <= 9:
        leaf_fall(ctx, ax, ay - 140, 100, 150, 16, i / 10.0, seed=3)
        # savia que gotea y se apaga
        if i <= 5:
            px, py = ctx.anchor('torso', (0, -20))
            fx.dots([(px + (k - 1) * 8, py + 6 + (i * 4 + k * 3) % 14) for k in range(3)], (255, 176, 40), 0.9, 'front')
    if 3 <= i <= 6:
        t = (i - 3) / 3.0
        cx, cy = ctx.anchor('torso', (0, -22))
        fx.glow(cx, cy, 34 * (0.4 + t), (255, 190, 80), 0.8 * (1 - t * 0.6))
        impact_star(ctx, cx, cy, t, (255, 230, 160), 28)
    if i >= 6:
        t = clamp01((i - 6) / 7.0)
        # tocon quebrado
        k = clamp01((i - 6) / 3.0)
        sx0, sy0 = ax - 2, ay
        fx.poly([(sx0 - 17, sy0 + 1), (sx0 - 15, sy0 - 12 * k), (sx0 - 10, sy0 - 20 * k), (sx0 - 6, sy0 - 15 * k), (sx0 - 1, sy0 - 24 * k), (sx0 + 5, sy0 - 16 * k), (sx0 + 10, sy0 - 21 * k), (sx0 + 15, sy0 - 10 * k), (sx0 + 18, sy0 + 1)], (22, 12, 14), 1.0, 'back', ss=2)
        fx.poly([(sx0 - 15, sy0), (sx0 - 13, sy0 - 12 * k), (sx0 - 9, sy0 - 19 * k), (sx0 - 5, sy0 - 14 * k), (sx0 - 1, sy0 - 22 * k), (sx0 + 4, sy0 - 15 * k), (sx0 + 9, sy0 - 19 * k), (sx0 + 13, sy0 - 9 * k), (sx0 + 15, sy0)], (92, 64, 44), 1.0, 'back', ss=2)
        fx.poly([(sx0 - 15, sy0), (sx0 - 13, sy0 - 12 * k), (sx0 - 9, sy0 - 19 * k), (sx0 - 7, sy0 - 12 * k), (sx0 - 8, sy0)], (150, 108, 70), 1.0, 'back', ss=2)
        fx.poly([(sx0 + 9, sy0), (sx0 + 9, sy0 - 19 * k), (sx0 + 13, sy0 - 9 * k), (sx0 + 15, sy0)], (50, 34, 30), 1.0, 'back', ss=2)
        fx.poly([(sx0 - 6, sy0 - 21 * k), (sx0 - 1, sy0 - 24 * k), (sx0 + 4, sy0 - 15.5 * k), (sx0 - 1, sy0 - 19 * k)], (205, 170, 112), 1.0, 'back', ss=2)
        # troncos y escombro
        pile(ctx, ax - 6, ay, 90, 9 * k + 2, [(92, 64, 44), (60, 42, 34), (130, 94, 62), (86, 110, 50)], int(10 + 26 * k), seed=15, layer='back', outline=(20, 12, 12))
        for (lx, ly, ll, ang) in ((ax - 38, ay - 3, 22, -4), (ax + 30, ay - 2, 26, 3), (ax + 8, ay - 7, 16, -10)):
            kk = clamp01((i - 7) / 3.0)
            if kk > 0:
                dx, dy = math.cos(math.radians(ang)) * ll * 0.5, math.sin(math.radians(ang)) * ll * 0.5
                fx.polyline([(lx - dx, ly - dy), (lx + dx, ly + dy)], 6, (22, 12, 14), kk, 'back')
                fx.polyline([(lx - dx, ly - dy - 0.5), (lx + dx, ly + dy - 0.5)], 4, (86, 60, 42), kk, 'back')
                fx.polyline([(lx - dx, ly - dy - 1.5), (lx + dx, ly + dy - 1.5)], 1, (150, 108, 70), kk, 'back')
        # hongos que brotan + brote nuevo
        q = clamp01((t - 0.3) / 0.5)
        for (mx, my, r, h) in ((ax - 22, ay - 2, 4, 7), (ax + 22, ay - 2, 3.4, 5), (ax - 30, ay - 1, 2.6, 4), (ax + 34, ay - 1, 3, 4)):
            if q > 0:
                hh = h * q
                fx.poly([(mx - 0.9, my), (mx + 0.9, my), (mx + 0.7, my - hh), (mx - 0.7, my - hh)], (216, 200, 160), 1.0, 'back')
                fx.ell(mx, my - hh, r * q + 0.5, r * 0.6 * q + 0.4, (226, 150, 44), 1.0, 'back')
                fx.ell(mx - r * 0.2, my - hh - 0.5, r * 0.4 * q + 0.3, r * 0.2 * q + 0.2, (255, 232, 140), 1.0, 'back')
                fx.glow(mx, my - hh, 6, (255, 176, 40), 0.5 * q)
        if t > 0.5:
            s2 = clamp01((t - 0.5) / 0.4)
            fx.polyline([(ax - 1, sy0 - 24 * k + 1), (ax - 1.5, sy0 - 24 * k - 7 * s2), (ax - 0.5, sy0 - 24 * k - 12 * s2)], 1, (110, 170, 60), 1.0, 'front')
            fx.poly([(ax - 0.5, sy0 - 24 * k - 12 * s2), (ax + 5 * s2, sy0 - 24 * k - 14 * s2), (ax + 1, sy0 - 24 * k - 9 * s2)], (150, 210, 80), 1.0, 'front', ss=2)
            fx.poly([(ax - 1.5, sy0 - 24 * k - 8 * s2), (ax - 7 * s2, sy0 - 24 * k - 11 * s2), (ax - 2, sy0 - 24 * k - 5 * s2)], (110, 170, 60), 1.0, 'front', ss=2)
            fx.glow(ax, sy0 - 24 * k - 8, 12, (200, 255, 120), 0.4 * s2)
        spores(ctx, ax, ay - 20, 70, 40, 14, t=t, seed=8, rise=-50, a=0.95)
        for k2 in range(3):
            ph = 2 * math.pi * (t * 0.6 + k2 / 3.0)
            moth(ctx, ax + math.cos(ph) * 40, ay - 30 - 40 * t - k2 * 12 + math.sin(ph * 2) * 6, i * 2.1 + k2 * 2, 0.9, 1.0)
        fx.glow(ax, ay - 3, 40, (255, 176, 40), 0.15 * (1 - t * 0.4), rx=50, ry=6)


def hit_boxes():
    return {
        'attack1': dict(hit=[2, 4], box=[8, -120, 84, 120]),
        'attack2': dict(hit=[2, 5], box=[12, -76, 150, 76]),
        'attack3': dict(hit=[4, 6], box=[-88, -62, 184, 62]),
        'cast': dict(rel=4, muzzle_src=('jaw', (10, 4))),
    }


def spec():
    fns = dict(idle=idle_pose, walk=walk_pose, windup1=wind1, attack1=atk1, windup2=wind2, attack2=atk2, windup3=wind3,
               attack3=atk3, cast=cast, hurt=hurt, phase=phase, intro=intro, death=death)
    hb = hit_boxes()
    return {k: dict(pose=v, **hb.get(k, {})) for k, v in fns.items()}


def build():
    return make(spec(), fxhook)
