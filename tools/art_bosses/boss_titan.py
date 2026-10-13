import math
import numpy as np
from kit import *
from shapes import *
from anim import *
from fxlib import *
from boss_common import *

IRON = auto('#4a4f5e', shadow=(18, 20, 56), warm=(190, 208, 225), n=6, dk=0.24)
RUST = auto('#8a4a2c', shadow=(40, 18, 50), warm=(255, 182, 100), n=6)
COPPER = auto('#a8603a', shadow=(48, 22, 64), warm=(255, 208, 150), n=6, dk=0.26)
VERD = auto('#3aa89c', shadow=(14, 32, 74), warm=(200, 255, 225), n=6, dk=0.3)
CLOUD = auto('#586a8c', shadow=(18, 22, 66), warm=(190, 210, 240), n=6, dk=0.22)
CLOUDD = auto('#2c364e', shadow=(10, 12, 44), warm=(120, 150, 200), n=6, dk=0.3)
VOID = ramp((4, 6, 14), (10, 14, 26), (30, 40, 62), 6)
STORMG = [(8, 26, 84), (28, 84, 196), (79, 168, 255), (176, 228, 255), (252, 254, 255)]
MATS = {
    'iron': Mat(IRON, glow=STORMG, gain=1.25, texamt=0.5), 'rust': Mat(RUST, gain=1.1), 'cu': Mat(COPPER, gain=1.3, texamt=0.45),
    'verd': Mat(VERD, gain=1.2, texamt=0.5), 'cloud': Mat(CLOUD, glow=STORMG, gain=1.0, texamt=0.7),
    'cloudd': Mat(CLOUDD, glow=STORMG, gain=1.0, texamt=0.7), 'void': Mat(VOID, gain=0.5),
    'core': Mat(CLOUD, glow=STORMG, texamt=0.2),
}
BOLT = (150, 215, 255)


def rivets(p, pts, r=0.85, mat='iron', raise_=0.7):
    for x, y in pts:
        p.ell(x, y, r, r, mat=mat, raise_=raise_, edge=0.9)


def build_parts():
    P = []

    def add(*a, **k):
        p = Part(*a, **k); P.append(p); return p
    add('root', None, (96, 156), ghost=True)
    # --------------------------------------------- manto de nubes (detras)
    cl1 = add('cloud1', 'root', (-14, -102), z=0.5, mat='cloudd', depth=9, noise=1.0, nscale=2.5, seed=61)
    for (x, y, rx, ry) in ((-10, 0, 13, 11), (-22, -10, 11, 10), (-4, -14, 12, 10), (-16, -24, 10, 9), (-26, 4, 9, 8), (4, 2, 10, 9), (-10, 12, 10, 8)):
        cl1.ell(x, y, rx, ry)
    cl1.blotch('cloud', 0.62, 2.8, 62, raise_=0.5)
    cl1.cracks(4, 12, v=0.1, w=0.8, seed=63, emit=1.0)
    cl2 = add('cloud2', 'cloud1', (-16, 6), z=0.4, mat='cloudd', depth=8, noise=1.0, nscale=2.5, seed=64)
    for (x, y, rx, ry) in ((-6, 6, 12, 9), (-18, 2, 10, 9), (-12, 18, 9, 8), (2, 14, 8, 7), (-24, 14, 7, 6)):
        cl2.ell(x, y, rx, ry)
    cl2.blotch('cloud', 0.6, 2.6, 65, raise_=0.5)
    cl2.cracks(3, 10, v=0.1, w=0.8, seed=66, emit=1.0)
    # --------------------------------------------- pelvis
    hip = add('hip', 'root', (0, -58), z=4, mat='iron', depth=6, noise=0.6, seed=5)
    hip.spl([(-17, -6), (-9, -10), (10, -10), (19, -5), (21, 3), (13, 11), (3, 8), (-4, 12), (-14, 9), (-20, 3)])
    hip.poly([(-19, -6), (20, -6), (20, 0), (-19, 0)], mat='cu', raise_=1.1, edge=0.1)
    hip.ell(3, -3, 5.5, 5.5, mat='core', raise_=0.8, edge=0.9)
    hip.ell(3, -3, 3.4, 3.4, op='emit', v=1.0, soft=0.6)
    rivets(hip, [(-14, -3), (-8, -3), (14, -3)], 0.9, 'iron')
    hip.blotch('rust', 0.74, 2.6, 7)
    hip.line([(-12, 5), (-6, 9)], 0.8, op='tex', v=0.1)
    # faldar de placas
    fa = add('fauld', 'hip', (2, 5), z=5.5, mat='cu', depth=3.5, noise=0.5, seed=8)
    fa.poly([(-11, 0), (13, 0), (14, 11), (7, 17), (0, 12), (-6, 18), (-12, 11)])
    fa.line([(-11, 5), (13, 5)], 0.9, op='tex', v=0.1)
    fa.line([(-2, 5), (-2, 13)], 0.9, op='tex', v=0.1)
    rivets(fa, [(-8, 2.5), (-2, 2.5), (4, 2.5), (10, 2.5)], 0.7, 'iron')
    fa.blotch('verd', 0.74, 4.0, 9)
    # --------------------------------------------- piernas
    for nm, x, z, dim in (('b', -9, 2, -0.22), ('f', 9, 5, 0.0)):
        th = add('thigh_' + nm, 'hip', (x, 4), z=z, mat='iron', depth=6.2, noise=0.4, seed=10, dim=dim, tnoise=0.15)
        th.tube([(0, 0), (1, 12), (1, 24)], 9.0, 7.0)
        th.spl([(-8.5, -1), (9, -1), (8.6, 14), (-7.5, 14)], mat='cu', raise_=1.4, edge=0.1)
        th.line([(-8, 6), (9, 6)], 0.8, op='tex', v=0.12)
        th.ell(1, 24, 8.6, 7.4, mat='cu', raise_=1.9, edge=0.1)
        th.ell(1.5, 24, 2.6, 2.6, mat='verd', raise_=0.6, edge=0.9)
        rivets(th, [(-5, 24), (8, 24), (1, 18)], 0.8, 'iron')
        th.blotch('verd', 0.74, 4.0, 12)
        sh = add('shin_' + nm, 'thigh_' + nm, (1, 24), z=z, mat='iron', depth=5.2, noise=0.4, seed=11, dim=dim, tnoise=0.15)
        sh.tube([(0, 0), (0, 11), (-1, 22)], 7.0, 5.2)
        sh.spl([(-6.6, 3), (7, 3), (5.8, 19), (-5.4, 19)], mat='cu', raise_=1.3, edge=0.1)
        sh.line([(0.5, 5), (0.2, 17)], 0.8, op='tex', v=0.12)
        sh.line([(-6, 11), (6.5, 11)], 0.8, op='tex', v=0.12)
        rivets(sh, [(-4.5, 5), (5, 5), (-3.5, 16), (4, 16)], 0.7, 'iron')
        sh.blotch('verd', 0.74, 4.0, 13)
        sh.blotch('rust', 0.8, 2.0, 14)
        ft = add('foot_' + nm, 'shin_' + nm, (-1, 22), z=z, mat='iron', depth=3.6, noise=0.4, seed=12, dim=dim)
        ft.spl([(-8, -7), (3, -8), (8, -4), (17, -1), (23, 2), (20, 6), (-9, 6)])
        ft.poly([(11, -2), (22, 2), (20, 6), (10, 6)], mat='cu', raise_=1.0, edge=0.1)
        ft.line([(8, -5), (8, 6)], 0.8, op='tex', v=0.1)
        ft.blotch('rust', 0.74, 2.0, 15)
    # --------------------------------------------- torso
    to = add('torso', 'hip', (0, -4), z=6, mat='iron', depth=9, noise=0.5, seed=20, tnoise=0.2)
    to.spl([(-16, -2), (-22, -14), (-23, -30), (-17, -42), (-5, -49), (11, -48), (21, -40), (26, -26), (24, -11), (16, -2), (0, 1)])
    to.spl([(3, -35), (12, -36), (18, -29), (16, -19), (9, -14), (2, -18), (0, -27)], mat='cloud', raise_=-1.2)
    to.ell(5, -30, 3.8, 3.2, mat='cloudd', raise_=0.3)
    to.ell(11, -23, 4.4, 3.6, mat='cloudd', raise_=0.3)
    to.ell(9, -25, 7, 6, op='emit', v=0.85, soft=1.8)
    to.cracks(6, 11, v=0.1, w=0.8, seed=21, emit=1.0)
    to.spl([(-21, -26), (-6, -34), (-2, -46), (-13, -46), (-22, -38)], mat='cu', raise_=1.5, edge=0.1)
    to.spl([(22, -34), (12, -42), (11, -48), (20, -42)], mat='cu', raise_=1.5, edge=0.1)
    to.spl([(-20, -10), (-6, -13), (-4, -20), (-20, -22)], mat='cu', raise_=1.3, edge=0.1)
    to.line([(-22, -4), (24, -6)], 0.9, op='tex', v=0.1)
    to.line([(-21, -9), (26, -10)], 0.9, op='tex', v=0.12)
    rivets(to, [(-17, -39), (-9, -41), (-14, -16), (-8, -17), (-18, -29), (16, -44), (20, -39)], 0.8, 'iron')
    to.blotch('verd', 0.74, 4.0, 22)
    to.blotch('rust', 0.8, 2.4, 23)
    # --------------------------------------------- cabeza
    hd = add('head', 'torso', (6, -46), z=12, mat='iron', depth=6.5, noise=0.4, seed=30, tnoise=0.15)
    hd.spl([(-10, -2), (-11, -13), (-6, -21), (3, -24), (11, -19), (14, -10), (13, -3), (8, 3), (-3, 4)])
    hd.poly([(-9, -17), (12, -19), (13, -13), (-10, -11)], mat='cu', raise_=1.2, edge=0.1)
    hd.poly([(3, -11), (14, -11.5), (14, -7.5), (2, -7)], mat='void', raise_=-0.5)
    hd.poly([(5, -10.6), (14, -10.8), (14, -8.6), (4, -8.2)], mat='core')
    hd.poly([(5, -10.6), (14, -10.8), (14, -8.6), (4, -8.2)], op='emit', v=1.0, soft=0.4)
    for k in range(4):
        hd.line([(3 + k * 2.4, -4.5), (3 + k * 2.4, 2)], 0.7, op='tex', v=0.08)
    hd.line([(-9, -3), (13, -4)], 0.8, op='tex', v=0.1)
    rivets(hd, [(-6, -15), (0, -16), (6, -17)], 0.7, 'iron')
    hd.blotch('verd', 0.74, 4.0, 31)
    rod1 = add('rod1', 'head', (-4, -21), z=11.5, mat='cu', depth=1.2, seed=35)
    rod1.tube([(0, 0), (-1, -9), (-2, -17)], 1.7, 0.9)
    rod1.ell(-2, -18, 2.0, 2.0, mat='core'); rod1.ell(-2, -18, 1.4, 1.4, op='emit', v=1.0, soft=0.3)
    rod2 = add('rod2', 'head', (5, -23), z=11.5, mat='cu', depth=1.2, seed=36)
    rod2.tube([(0, 0), (1, -10), (3, -19)], 1.7, 0.9)
    rod2.ell(3, -20, 2.0, 2.0, mat='core'); rod2.ell(3, -20, 1.4, 1.4, op='emit', v=1.0, soft=0.3)
    # --------------------------------------------- hombreras
    for nm, x, z, dim in (('f', 16, 11, 0.0), ('b', -17, 3, -0.2)):
        pf = add('pauld_' + nm, 'torso', (x, -41), z=z, mat='cu', depth=8.0, noise=0.5, seed=44, dim=dim)
        pf.spl([(-15, 5), (-14, -5), (-6, -12), (6, -13), (14, -7), (16, 4), (9, 11), (-6, 10)])
        pf.line([(-12, 1), (-3, -6), (11, -4)], 0.9, op='tex', v=0.1)
        pf.line([(-12, 6), (0, 8), (12, 4)], 0.9, op='tex', v=0.1)
        pf.ell(1, 0, 4.2, 4.2, mat='iron', raise_=1.2, edge=0.1)
        pf.ell(1, 0, 2.0, 2.0, mat='core'); pf.ell(1, 0, 1.4, 1.4, op='emit', v=1.0, soft=0.3)
        rivets(pf, [(-9, -5), (9, -7), (-10, 3), (12, 3)], 0.8, 'iron')
        pf.blotch('verd', 0.74, 4.0, 45)
        pf.blotch('rust', 0.8, 2.2, 46)
        pf.poly([(-6, -11), (-4, -30), (-2, -11)], mat='iron', raise_=0.8, edge=0.1)
        pf.poly([(5, -12), (8, -27), (9, -11)], mat='iron', raise_=0.8, edge=0.1)
    # --------------------------------------------- brazos
    for nm, x, z, dim in (('b', -14, 3, -0.22), ('f', 15, 10, 0.0)):
        ua = add('uarm_' + nm, 'torso', (x, -40), z=z, mat='iron', depth=6.2, noise=0.4, seed=40, dim=dim, tnoise=0.15)
        ua.tube([(0, 0), (2, 15), (1, 29)], 8.4, 7.0)
        ua.spl([(-6.8, 14), (7.6, 14), (7.2, 30), (-5.8, 30)], mat='cu', raise_=1.3, edge=0.1)
        ua.line([(-6, 20), (7, 20)], 0.8, op='tex', v=0.12)
        rivets(ua, [(-4, 17), (5, 17), (-3, 27), (5, 27)], 0.7, 'iron')
        ua.blotch('verd', 0.74, 4.0, 41)
        fa_ = add('farm_' + nm, 'uarm_' + nm, (1, 29), z=z, mat='iron', depth=5.4, noise=0.4, seed=41, dim=dim, tnoise=0.15)
        fa_.tube([(0, 0), (0.5, 12), (0.5, 25)], 7.2, 6.0)
        fa_.spl([(-6.2, 4), (6.6, 4), (6.2, 25), (-5.0, 25)], mat='cu', raise_=1.3, edge=0.1)
        fa_.line([(0.5, 6), (0.5, 23)], 0.8, op='tex', v=0.12)
        rivets(fa_, [(-3.5, 8), (4, 8), (-3, 20), (4, 20)], 0.7, 'iron')
        fa_.blotch('verd', 0.74, 4.0, 42)
        hn = add('hand_' + nm, 'farm_' + nm, (0.5, 25), z=z + 0.2, mat='iron', depth=4.4, noise=0.3, seed=43, dim=dim)
        hn.spl([(-6, -2), (6.2, -2), (8, 5), (6, 11), (-5, 11), (-7.5, 4)])
        hn.line([(-5, 4), (7, 4)], 0.8, op='tex', v=0.1)
        hn.poly([(-6, -2), (6.2, -2), (6.5, 3), (-6, 3)], mat='cu', raise_=0.9, edge=0.1)
        rivets(hn, [(-3, 0.5), (3, 0.5)], 0.6, 'iron')
        hn.blotch('rust', 0.76, 2.0, 44)
    # --------------------------------------------- martillo
    hm = add('hammer', 'hand_f', (0, 4), z=10.5, mat='iron', depth=3.4, noise=0.4, seed=50)
    hm.poly([(-3.2, -18), (3.2, -18), (3.4, 48), (-3.4, 48)])
    hm.poly([(-4.6, -19), (4.6, -19), (4.6, -13), (-4.6, -13)], mat='cu', raise_=0.9, edge=0.1)
    for yy in (6, 18, 30):
        hm.poly([(-4.4, yy), (4.4, yy), (4.4, yy + 3.4), (-4.4, yy + 3.4)], mat='cu', raise_=0.9, edge=0.1)
    hm.line([(0, -10), (0, 44)], 1.2, op='tex', v=0.14)
    hm.blotch('rust', 0.78, 2.0, 51)
    hm.spl([(-21, 40), (-17, 37), (17, 37), (21, 40), (22, 64), (18, 69), (-18, 69), (-22, 64)], mat='iron', raise_=1.4, edge=0.08)
    hm.spl([(-24, 38), (-17, 36), (-15, 71), (-24, 68)], mat='cu', raise_=1.8, edge=0.1)
    hm.spl([(24, 38), (17, 36), (15, 71), (24, 68)], mat='cu', raise_=1.8, edge=0.1)
    hm.spl([(-9, 42), (9, 42), (10, 52), (9, 63), (-9, 63), (-10, 52)], mat='core', raise_=-0.6)
    hm.spl([(-7, 45), (7, 45), (8, 52), (7, 60), (-7, 60), (-8, 52)], op='emit', v=0.9, soft=0.9)
    hm.line([(-13, 40), (-13, 66)], 0.8, op='tex', v=0.1)
    hm.line([(13, 40), (13, 66)], 0.8, op='tex', v=0.1)
    rivets(hm, [(-20, 42), (-20, 64), (20, 42), (20, 64)], 0.9, 'iron')
    hm.poly([(-3, 69), (0, 84), (3, 69)], mat='iron', raise_=0.8, edge=0.1)
    hm.ell(0, 85, 2.2, 2.2, mat='core'); hm.ell(0, 85, 1.6, 1.6, op='emit', v=1.0, soft=0.3)
    hm.cracks(3, 8, v=0.1, w=0.7, seed=52, emit=1.0)
    hm.blotch('verd', 0.74, 4.0, 53)
    return P


make_H(wp='hammer')
H = make_H(wp='hammer')
post = make_post('hammer', 'uarm_b', 'farm_b', 'hand_b', (0.5, 25), -12)


def make(anims, fxhook):
    return Boss('titan_tormenta', (192, 160), (96, 156), (46, 120), build_parts(), MATS, anims, fxhook,
                outline=(8, 10, 22), rim=(110, 190, 255), rimk=0.42, dis_col=(120, 200, 255), seed=21, post=post, scale=0.85)


# ====================================================================== animaciones
def L(thf, shf, thb, shb, ff=None, fb=None):
    return {'thigh_f': thf, 'shin_f': shf, 'foot_f': -(thf + shf) * 0.9 if ff is None else ff,
            'thigh_b': thb, 'shin_b': shb, 'foot_b': -(thb + shb) * 0.9 if fb is None else fb}


def PZ(*ds):
    return merge(*ds)


def cloudsway(f, n, amp=1.0, base=0.0, ph=0.0):
    return {'cloud1': base * 0.5 + amp * 3.0 * S(f, n, ph), 'cloud2': base + amp * 5.0 * S(f, n, ph + 0.15),
            'rod1': amp * 3 * S(f, n, ph + 0.3), 'rod2': amp * 3 * S(f, n, ph + 0.5)}


STAND = PZ(L(-7, 10, 8, -6), H(3, -14, -34, -10), {'head': -1})


def idle_pose(f):
    b = S(f, 6)
    return PZ(STAND, {'root.y': -0.9 * b, 'torso': 1.0 * b, 'head': -1.6 * b, 'uarm_f': -0.6 * b, 'hammer': 0.8 * S(f, 6, 0.1)},
              cloudsway(f, 6, 1.0, 1.0))


def walk_pose(f):
    ph = 2 * math.pi * f / 8
    s = math.sin(ph); c = math.cos(ph)
    thf = 18 * s - 5; thb = -18 * s + 5
    shf = 12 + 22 * max(0, -c * 0.9 + 0.1) * (1 if s < 0.3 else 0.3) + 5 * max(0, c)
    shb = 12 + 22 * max(0, c * 0.9 + 0.1) * (1 if s > -0.3 else 0.3) + 5 * max(0, -c)
    return PZ(L(thf, shf * 0.8, thb, shb * 0.8), H(5, -14 + 3 * s, -34, -12 + 4 * s),
              {'root.y': -2.8 * abs(c) + 1.5, 'head': -2 + 2 * c, 'torso': 1.8 * c, 'hip': 1.8 * s}, cloudsway(f, 8, 1.4, 4))


WIND1 = [(0, STAND),
         (1, PZ(L(-10, 14, 9, -7), H(-2, -64, -42, -76), {'root.y': 1.5})),
         (2, PZ(L(-13, 18, 11, -8), H(-8, -92, -44, -150), {'root.y': 2.5, 'head': -6})),
         (3, PZ(L(-15, 20, 12, -8), H(-12, -102, -42, -196), {'root.y': 3.5, 'head': -9})),
         (4, PZ(L(-15, 20, 12, -8), H(-14, -104, -42, -212), {'root.y': 4, 'head': -10, 'root.x': -2}))]
wind1k = K(WIND1)


def wind1(f):
    return PZ(wind1k(f), cloudsway(f, 5, 0.8, 3 + f))


W1END = WIND1[-1][1]
ATK1 = [(0, W1END, 'sm'),
        (1, PZ(L(-22, 26, 12, -8), H(2, -102, -42, -160), {'root.y': 3, 'root.x': 4, 'head': 0}), 'snap'),
        (2, PZ(L(-28, 32, 15, -8), H(14, -82, -44, -100), {'root.y': 3, 'root.x': 8, 'head': 4}), 'snap'),
        (3, PZ(L(-32, 38, 17, -8), H(22, -62, -46, -22), {'root.y': 4, 'root.x': 11, 'head': 6}), 'snap'),
        (4, PZ(L(-32, 38, 17, -8), H(22, -58, -46, -14), {'root.y': 4, 'root.x': 11, 'head': 6}), 'out'),
        (5, PZ(L(-28, 34, 16, -8), H(18, -52, -46, -16), {'root.y': 3.5, 'root.x': 9, 'head': 4}), 'sm'),
        (6, PZ(L(-18, 22, 12, -8), H(10, -40, -42, -20), {'root.y': 2, 'root.x': 4}), 'sm'),
        (7, STAND, 'sm')]
atk1k = K(ATK1)


def atk1(f):
    return PZ(atk1k(f), cloudsway(f, 8, 1.4, 8 - f * 0.6, 0.2))


WIND2 = [(0, STAND),
         (1, PZ(L(-10, 18, 10, -10), H(8, -20, -30, 30), {'root.y': 2, 'head': -2})),
         (2, PZ(L(-14, 26, 14, -18), H(18, -10, -20, 60), {'root.y': 4, 'root.x': -3, 'head': -4})),
         (3, PZ(L(-18, 32, 18, -22), H(26, 0, -14, 80), {'root.y': 6, 'root.x': -6, 'head': -6})),
         (4, PZ(L(-20, 34, 20, -24), H(28, 4, -12, 84), {'root.y': 7, 'root.x': -8, 'head': -8}))]
wind2k = K(WIND2)


def wind2(f):
    return PZ(wind2k(f), cloudsway(f, 5, 0.5, -2 - f * 2, 0.3))


ATK2 = [(0, WIND2[-1][1], 'sm'),
        (1, PZ(L(-34, 24, 26, -16), H(24, -40, -50, 50), {'root.y': 3, 'root.x': 10, 'head': 4}), 'snap'),
        (2, PZ(L(-40, 20, 30, -12), H(28, -70, -40, 0), {'root.y': 2, 'root.x': 20, 'head': 8}), 'snap'),
        (3, PZ(L(-40, 20, 30, -12), H(30, -80, -34, -32), {'root.y': 2, 'root.x': 24, 'head': 9}), 'out'),
        (4, PZ(L(-38, 22, 28, -12), H(30, -82, -32, -50), {'root.y': 2, 'root.x': 26, 'head': 9}), 'sm'),
        (5, PZ(L(-32, 22, 24, -12), H(26, -74, -34, -50), {'root.y': 2, 'root.x': 26, 'head': 7}), 'sm'),
        (6, PZ(L(-22, 20, 16, -10), H(14, -50, -40, -36), {'root.y': 2, 'root.x': 13}), 'sm'),
        (7, STAND, 'sm')]
atk2k = K(ATK2)


def atk2(f):
    return PZ(atk2k(f), cloudsway(f, 8, 1.6, -14 + f * 1.5, 0.0))


WIND3 = [(0, STAND),
         (1, PZ(L(-26, 54, 24, -36), H(8, -60, -60, -66), {'root.y': 5, 'head': -2})),
         (2, PZ(L(-30, 64, 28, -44), H(0, -90, -50, -150), {'root.y': 7, 'head': -6})),
         (3, PZ(L(-32, 68, 30, -48), H(-6, -100, -44, -200), {'root.y': 9, 'head': -10})),
         (4, PZ(L(-34, 72, 32, -52), H(-10, -104, -42, -214), {'root.y': 10, 'head': -12})),
         (5, PZ(L(-34, 72, 32, -52), H(-12, -106, -42, -220), {'root.y': 11, 'head': -13}))]
wind3k = K(WIND3)


def wind3(f):
    return PZ(wind3k(f), cloudsway(f, 6, 0.5, 4 + f, 0.3))


ATK3 = [(0, WIND3[-1][1], 'sm'),
        (1, PZ(L(-6, 8, 6, -4), H(-4, -106, -42, -218), {'root.y': -22, 'head': -8}), 'out'),
        (2, PZ(L(-12, 26, 12, -20), H(2, -106, -42, -212), {'root.y': -28, 'head': -4}), 'sm'),
        (3, PZ(L(-18, 28, 14, -26), H(14, -94, -46, -150), {'root.y': -14, 'head': 4}), 'in'),
        (4, PZ(L(-30, 50, 24, -36), H(26, -64, -54, -16), {'root.y': 7, 'root.x': 5, 'head': 7}), 'snap'),
        (5, PZ(L(-32, 56, 26, -40), H(28, -60, -56, -6), {'root.y': 8, 'root.x': 5, 'head': 8}), 'sm'),
        (6, PZ(L(-30, 52, 22, -36), H(24, -58, -56, -6), {'root.y': 7, 'root.x': 5, 'head': 7}), 'sm'),
        (7, PZ(L(-18, 30, 14, -20), H(12, -46, -48, -14), {'root.y': 4, 'root.x': 2}), 'sm'),
        (8, STAND, 'sm')]
atk3k = K(ATK3)


def atk3(f):
    return PZ(atk3k(f), cloudsway(f, 9, 1.8, -10 if f in (1, 2, 3) else 6, 0.0))


CAST = K([(0, STAND),
          (1, PZ(L(-9, 14, 10, -8), H(-2, -66, -50, -92), {'root.y': 1.5, 'head': -4})),
          (2, PZ(L(-12, 18, 12, -8), H(-8, -92, -52, -136), {'root.y': 2.5, 'head': -9}), 'sm'),
          (3, PZ(L(-12, 18, 12, -8), H(-12, -102, -52, -150), {'root.y': 2, 'head': -12}), 'sm'),
          (4, PZ(L(-14, 20, 14, -8), H(-14, -110, -50, -156), {'root.y': 3, 'head': -10}), 'snap'),
          (5, PZ(L(-14, 20, 14, -8), H(-14, -112, -50, -158), {'root.y': 3, 'head': -8}), 'out'),
          (6, PZ(L(-12, 16, 12, -8), H(-4, -90, -46, -140), {'root.y': 2}), 'sm'),
          (7, STAND, 'sm')])


def cast(f):
    return PZ(CAST(f), cloudsway(f, 8, 1.8, 4, 0.0))


def hurt(f):
    d = [PZ(L(-4, 12, 8, -6), H(-10, -34, -44, -6), {'head': -10, 'root.x': -4, 'root.y': 1, 'tint': ((255, 255, 255), 0.5)}),
         PZ(L(-6, 11, 8, -6), H(-3, -24, -38, -14), {'head': -5, 'root.x': -2, 'tint': ((255, 255, 255), 0.2)})][int(f)]
    return PZ(d, cloudsway(f, 2, 1, 6 + 4 * (1 - f)))


PHASE = K([(0, PZ(STAND, {'free_b': 1, 'uarm_b': 0, 'farm_b': -10})),
           (1, PZ(L(-16, 32, 16, -22), H(8, -30, -50, -20), {'root.y': 4, 'head': 8, 'free_b': 1, 'uarm_b': 14, 'farm_b': -30}), 'sm'),
           (2, PZ(L(-22, 46, 22, -32), H(14, -14, -50, 0), {'root.y': 7, 'head': 12, 'free_b': 1, 'uarm_b': 30, 'farm_b': -50}), 'sm'),
           (3, PZ(L(-14, 22, 16, -14), H(4, -60, -40, -80), {'root.y': 1, 'head': -4, 'free_b': 1, 'uarm_b': -70, 'farm_b': -40}), 'out'),
           (4, PZ(L(-8, 8, 10, -4), H(-10, -104, -30, -170), {'root.y': -6, 'head': -22, 'free_b': 1, 'uarm_b': -120, 'farm_b': -30, 'torso.sy': 1.04}), 'snap'),
           (5, PZ(L(-8, 8, 10, -4), H(-12, -110, -30, -176), {'root.y': -8, 'head': -26, 'free_b': 1, 'uarm_b': -140, 'farm_b': -24, 'torso.sy': 1.05}), 'sm'),
           (6, PZ(L(-8, 8, 10, -4), H(-12, -110, -30, -176), {'root.y': -7, 'head': -24, 'free_b': 1, 'uarm_b': -140, 'farm_b': -26}), 'sm'),
           (7, PZ(L(-14, 18, 12, -10), H(0, -70, -40, -110), {'root.y': -2, 'head': -8, 'free_b': 1, 'uarm_b': -90, 'farm_b': -30}), 'in'),
           (8, PZ(L(-12, 16, 11, -9), H(2, -40, -40, -50), {'root.y': 1, 'head': 2, 'free_b': 1, 'uarm_b': -40, 'farm_b': -30}), 'snap'),
           (9, PZ(STAND, {'free_b': 0}), 'sm')])


def phase(f):
    p = PHASE(f)
    if 4 <= f <= 7:
        p['tint'] = ((140, 200, 255), 0.25 * (1 - abs(f - 5.5) / 2.0))
    p['root.x'] = p.get('root.x', 0) + (1.2 if (f in (5, 6) and int(f) % 2) else (-1.2 if f in (5, 6) else 0))
    if f >= 9:
        p['free_b'] = 0
    return PZ(p, cloudsway(f, 10, 2.4, -8 if 3 <= f <= 7 else 4, 0.0))


def intro(f):
    i = int(f)
    ry = [-150, -150, -150, -85, -38, 0, 0, 0, 0, 0, 0, 0, 0, 0][i]
    land = clamp01(1 - abs(i - 5.5) / 1.6) * (1 if 5 <= i <= 6 else 0)
    # 5-6: agachado de impacto; 7-9 se incorpora; 10-12 alza el martillo; 13 reposo
    crouch = {5: 1.0, 6: 0.9, 7: 0.6, 8: 0.35, 9: 0.15}.get(i, 0.0)
    lift = {10: 0.5, 11: 1.0, 12: 0.5}.get(i, 0.0)
    base = PZ(STAND, {'root.y': ry + 10 * crouch})
    leg = PZ(L(-26 * crouch, 50 * crouch, 26 * crouch, -40 * crouch))
    arms = PZ(H(2 + 12 * crouch - 10 * lift, -16 - 30 * crouch - 70 * lift, -36 - 10 * crouch - 6 * lift, -24 - 30 * crouch - 190 * lift * 0 - 120 * lift), {'head': 10 * crouch - 8 * lift})
    p = PZ(base, leg, arms, cloudsway(f, 14, 1.4, 6))
    if i in (3, 4):
        p['tint'] = ((235, 245, 255), 0.95 if i == 3 else 0.55)
    if i == 5:
        p['tint'] = ((235, 245, 255), 0.35)
    if i < 3:
        p['clip'] = (0, 0, 0, 0)
    return p


DEATH = K([(0, PZ(L(-4, 12, 8, -6), H(-10, -34, -44, -6), {'head': -10, 'root.x': -4, 'tint': ((255, 255, 255), 0.5)}), 'out'),
           (1, PZ(L(-4, 16, 10, -8), H(-8, -30, -40, 0), {'head': -8, 'root.x': -5, 'tint': ((255, 255, 255), 0.2)}), 'sm'),
           (2, PZ(L(-6, 30, 14, -20), H(4, -20, -30, 10), {'head': 6, 'root.x': -4, 'root.y': 4, 'tint': ((200, 225, 255), 0.0)}), 'sm'),
           (3, PZ(L(-20, 56, 20, -50), H(12, -10, -24, 14), {'head': 14, 'root.x': -2, 'root.y': 14}), 'sm'),
           (4, PZ(L(-36, 100, 24, -88), H(18, -6, -20, 16), {'head': 22, 'root.x': 0, 'root.y': 26}), 'sm'),
           (5, PZ(L(-50, 124, 28, -112), H(26, 4, -16, 18), {'head': 30, 'root.x': 2, 'root.y': 36}), 'sm'),
           (6, PZ(L(-58, 134, 30, -122), H(36, 14, -10, 18), {'head': 36, 'root.x': 4, 'root.y': 41, 'torso': 12}), 'sm'),
           (7, PZ(L(-60, 136, 32, -124), H(44, 24, -4, 18), {'head': 40, 'root.x': 6, 'root.y': 44, 'torso': 22}), 'in'),
           (13, PZ(L(-60, 136, 32, -124), H(52, 30, 0, 18), {'head': 44, 'root.x': 8, 'root.y': 46, 'torso': 30}), 'lin')])


def death(f):
    p = DEATH(f)
    p['free_b'] = 1 if f >= 3 else 0
    if f >= 3:
        p['uarm_b'] = 6 + 3 * f; p['farm_b'] = -12 - 2 * f
    d = clamp01((f - 6.5) / 5.5)
    if d > 0:
        p['dis'] = d * 1.12
        p['dis_dir'] = 1.0
    p['hammer.v'] = 0 if f >= 6 else 1
    p['pauld_f.y'] = 0 if f < 5 else 5 * clamp01((f - 5) / 3)
    p['head'] = p.get('head', 0)
    p.update(cloudsway(f, 14, 0.5, 6 + f * 2))
    return p


# ====================================================================== efectos
def sparkle_body(ctx, k=1.0):
    """arcos pequenos recorriendo el cuerpo y las varillas."""
    fx, i, rng = ctx.fx, ctx.i, ctx.rng
    for nm, pt in (('rod1', (-2, -19)), ('rod2', (3, -21))):
        x, y = ctx.anchor(nm, pt)
        fx.glow(x, y, 6, (110, 190, 255), 0.5 * k)
        if (i + (1 if nm == 'rod2' else 0)) % 2 == 0 and k > 0.3:
            bolt(ctx, x, y, x + (rng.random() - 0.3) * 16, y - 6 - rng.random() * 8, (220, 240, 255), 1.0, int(i * 7 + (3 if nm == 'rod2' else 0)), 2.5, 5, (80, 150, 255), 'front', 0.9, False)
    cx_, cy_ = ctx.anchor('torso', (9, -25))
    fx.glow(cx_, cy_, 14, (80, 160, 255), (0.32 + 0.1 * math.sin(i * 1.7)) * k)
    if k > 0.3 and i % 2 == 1:
        a = rng.random() * 6.28
        bolt(ctx, cx_, cy_, cx_ + math.cos(a) * 16, cy_ + math.sin(a) * 16, (200, 230, 255), 1.0, int(i * 11), 2.5, 5, (80, 150, 255), 'front', 0.85, False)
    hx, hy = ctx.anchor('head', (10, -9.5))
    fx.glow(hx, hy, 6, (120, 200, 255), 0.5 * k)


def hammer_head_pt(ctx, pose_f=None):
    return ctx.anchor('hammer', (0, 56)) if pose_f is None else ctx.anchor_at(pose_f, 'hammer', (0, 56))


def fxhook(ctx):
    n, i, fx, W = ctx.name, ctx.i, ctx.fx, ctx.W
    ax, ay = ctx.pivot
    rng = ctx.rng
    tip = lambda f=None: ctx.anchor('hammer', (0, 56)) if f is None else ctx.anchor_at(f, 'hammer', (0, 56))
    k = 1.0
    if n == 'intro':
        k = 0 if i < 4 else 1.0
    if n == 'death':
        k = max(0, 1 - i / 7.0)
    if n == 'phase':
        k = 2.2 if 4 <= i <= 7 else 1.2
    if k > 0:
        sparkle_body(ctx, k)
    hx, hy = tip()
    if n not in ('intro', 'death') or (n == 'intro' and i >= 5):
        fx.glow(hx, hy, 18, (80, 160, 255), 0.22 + 0.06 * math.sin(i * 1.9), rx=22, ry=14)
    # nubes: motas
    if n not in ('intro', 'death'):
        wisps(ctx, ax - 24, ay - 100, 50, 40, 6, [(100, 170, 255), (220, 240, 255)], seed=4, a=0.8, rise=12)
    if n == 'windup1':
        t = i / 4.0
        tx, ty = tip()
        fx.glow(tx, ty, 14 + 16 * t, (90, 170, 255), 0.5 * t + 0.1)
        wisps(ctx, tx, ty + 4, 22, 20, 7, [(170, 225, 255), (255, 255, 255)], t=t * 0.9, seed=8, rise=10)
        if i >= 2:
            bolt(ctx, tx, ty, tx + 14 * math.sin(i), ty - 12, (220, 240, 255), 1.0, i * 3, 3, 5, (80, 150, 255), 'front', 0.8, False)
    if n == 'attack1':
        trail(ctx, 'hammer', (0, 70), (0, 46), 0, 4, (235, 248, 255), (40, 100, 220), steps=12, span=3.0, mid=(90, 170, 255), a=0.75)
        if 3 <= i <= 6:
            tx, ty = tip(3.6)
            tt = (i - 3) / 3.0
            gx = min(tx, W - 8)
            dust(ctx, gx, ay, tt, (110, 125, 150), 11, 28, 10)
            shock(ctx, gx, ay, tt, (170, 220, 255), 40, 5)
            fx.glow(gx, ay - 4, 18 * (1 - tt * 0.5), (130, 200, 255), 0.85 * (1 - tt))
            if i == 3:
                fx.sparks(rng, gx, ay - 3, 14, 18, [(255, 255, 255), (130, 200, 255)], 'front', 8)
                bolt(ctx, gx, ay - 2, gx - 18, ay - 20, (220, 240, 255), 1.0, 5, 3, 5, (80, 150, 255), 'front')
            if i in (3, 4):
                for b in (-1, 1):
                    bolt(ctx, gx + b * 6, ay, gx + b * 26, ay - 8 - rng.random() * 8, (200, 230, 255), 1.0, i + b, 2.5, 5, (80, 150, 255), 'front', 0.9, False)
    if n == 'windup2':
        t = i / 4.0
        sx_, sy_ = ctx.anchor('torso', (24, -30))
        fx.glow(sx_, sy_, 14 + 14 * t, (90, 170, 255), 0.4 * t + 0.1)
        for kk in range(5):
            yy = ay - 20 - kk * 14
            x0 = ax + 54 - ((i * 7 + kk * 13) % 12)
            fx.line((x0, yy), (x0 - 10 - 2 * kk, yy), 1, (180, 220, 255), 0.35 + 0.3 * t, 'front', mode='add')
        if i >= 2:
            tx, ty = tip()
            fx.glow(tx, ty, 14 + 8 * t, (90, 170, 255), 0.4)
    if n == 'attack2':
        if 1 <= i <= 6:
            bx, by = ctx.anchor('torso', (24, -30))
            t = clamp01((i - 1) / 5.0)
            for kk in range(6):
                yy = ay - 14 - kk * 15
                x0 = bx - 10 - ((i * 9 + kk * 17) % 18)
                fx.line((x0, yy), (x0 - 18 - 4 * kk, yy), 1 + (kk % 2), (150, 210, 255), 0.7 * (1 - t * 0.4), 'front')
            x1 = ctx.anchor('torso', (28, -26))[0]
            ln = min(60, W - 4 - x1) * ease_out(clamp01(i / 2.0)) * (1 - 0.4 * clamp01((i - 4) / 3.0))
            fx.poly([(x1, by - 16), (x1 + ln, by), (x1, by + 16)], (60, 130, 255), 0.35 * (1 - t * 0.6), 'front', ss=2)
            fx.poly([(x1, by - 8), (x1 + ln * 0.9, by), (x1, by + 8)], (170, 225, 255), 0.55 * (1 - t * 0.5), 'front', ss=2)
            if i in (2, 3, 4):
                for b in range(3):
                    bolt(ctx, x1 + 4, by + (b - 1) * 10, x1 + 20 + b * 8, by + (b - 1) * 20, (210, 235, 255), 1.0, i * 5 + b, 3, 5, (80, 150, 255), 'front', 0.9, False)
        if 1 <= i <= 5:
            dust(ctx, ax - 6 + ctx.pose.get('root.x', 0) * 0.4, ay, clamp01((i - 1) / 4.0), (110, 125, 150), 9, 20, 6, a=0.6)
    if n == 'windup3':
        t = i / 5.0
        tx, ty = tip()
        fx.glow(tx, ty, 14 + 20 * t, (90, 170, 255), 0.5 * t + 0.1)
        wisps(ctx, ax, ay - 3, 50, 6, 8, [(170, 225, 255)], t=t, seed=5, rise=30, a=0.7)
        rays(ctx, ax, ay - 2, t * 0.6, (90, 170, 255), 6, 6, 30, 0.18, 0.4 * t, 0.4, 'back')
        if i >= 2:
            for b in range(2):
                bolt(ctx, tx, ty, tx + (b * 2 - 1) * 20, ty - 14 - 6 * b, (220, 240, 255), 1.0, i * 2 + b, 3, 5, (80, 150, 255), 'front', 0.85, False)
    if n == 'attack3':
        tx, ty = tip()
        if 1 <= i <= 4:
            trail(ctx, 'hammer', (0, 70), (0, 46), 2, 4, (235, 248, 255), (40, 100, 220), steps=12, span=2.6, mid=(90, 170, 255), a=0.75)
        if i in (1, 2):
            fx.glow(ax, ay - 8, 26, (80, 160, 255), 0.25)
        if 4 <= i <= 8:
            t = (i - 4) / 4.0
            gx = max(ax + 30, min(tx, W - 12))
            ground_cracks(ctx, gx, ay + 1, t, (10, 14, 26), (140, 210, 255), 9, 64, 13)
            shock(ctx, gx, ay, t, (170, 220, 255), 72, 8, 2)
            dust(ctx, gx, ay, t, (110, 125, 150), 16, 46, 14, 3.2)
            if i <= 7:
                fx.glow(gx, ay - 6, 26 * (1 - t * 0.5), (130, 200, 255), 0.9 * (1 - t))
                # rayos del cielo
                for b in range(4):
                    px = gx - 56 + b * 34 + (b % 2) * 5
                    if i - 4 == (b % 2) or i == 5:
                        bolt(ctx, px + 3, 6, px, ay, (225, 242, 255), 3.0, i * 4 + b, 6, 11, (70, 140, 255), 'front', 0.95, True)
                        fx.glow(px, ay - 4, 14, (140, 210, 255), 0.8)
    if n == 'cast':
        tx, ty = ctx.anchor('hammer', (0, 84))
        if 1 <= i <= 4:
            t = i / 4.0
            for kk in range(8):
                ang = i * 0.9 + kk * 0.8
                r = 18 * (1 - t * 0.5) + 2
                px = tx + math.cos(ang) * r; py = ty + math.sin(ang) * r * 0.8
                fx.glow(px, py, 4, (110, 190, 255), 0.8)
                fx.dots([(px, py)], (230, 245, 255), 1.0, 'front')
            fx.glow(tx, ty, 10 + 12 * t, (90, 170, 255), 0.7)
        if i >= 4:
            tt = (i - 4) / 3.0
            for b in range(5):
                px = ax + 30 + b * 22 + (b % 2) * 6
                if (i + b) % 3 != 0 or i == 4:
                    bolt(ctx, px + 8 * math.sin(b + i), 4, px, ay - 4 * (b % 2), (225, 242, 255), 2.0, i * 3 + b, 6, 11, (70, 140, 255), 'front', 0.95 - 0.2 * tt, True)
                    fx.glow(px, ay - 6, 10, (130, 200, 255), 0.6 * (1 - tt * 0.5))
        if i >= 4:
            beam(ctx, (tx, ty), (min(W - 4, tx + 30 + 40 * (i - 4) / 3.0), ty + 6), 4, (200, 235, 255), (60, 130, 255), 0.7)
    if n == 'phase':
        t = clamp01((i - 3) / 5.0)
        if 3 <= i <= 9:
            fx.glow(ax, ay - 70, 70 * t + 14, (70, 150, 255), 0.5 * (1 - abs(t - 0.5) * 1.2), rx=56 * t + 16, ry=84 * t + 16)
            rays(ctx, ax, ay - 76, t, (130, 200, 255), 16, 16, 90, 0.1, 0.5, i * 0.1, 'back', 'over')
            shock(ctx, ax, ay, clamp01((i - 4) / 5.0), (170, 220, 255), 80, 8, 2)
        if 4 <= i <= 8:
            wisps(ctx, ax, ay - 70, 70, 100, 18, [(150, 210, 255), (240, 250, 255)], t=(i - 4) / 6.0, seed=21, rise=44, a=1.0)
            for b in range(5):
                px = ax + (b - 2) * 30
                bolt(ctx, px, 2, px + (rng.random() - 0.5) * 20, ay - 2, (225, 242, 255), 2.0, i * 6 + b, 6, 11, (70, 140, 255), 'front', 0.9, True)
    if n == 'death':
        if 3 <= i <= 9:
            for b in range(2 + (i % 2)):
                a = rng.random() * 6.28
                cx_, cy_ = ctx.anchor('torso', (4, -20))
                bolt(ctx, cx_, cy_, cx_ + math.cos(a) * (24 + 10 * rng.random()), cy_ + math.sin(a) * 26, (220, 240, 255), 1.4, i * 8 + b, 3, 6, (80, 150, 255), 'front', 0.95, True)
        if i >= 7:
            t = clamp01((i - 7) / 6.0)
            pile(ctx, ax + 12, ay + 1, 60, 10 + 6 * t, [(110, 120, 140), (70, 76, 94), (180, 110, 70), (60, 160, 150)], 14 + int(30 * t), seed=6)
            sx_ = ax + 34
            fx.poly([(sx_ - 3, ay - 54), (sx_ + 3, ay - 54), (sx_ + 3.5, ay + 1), (sx_ - 3.5, ay + 1)], (50, 54, 66), 1.0, 'back')
            fx.line((sx_ - 1, ay - 50), (sx_ - 1, ay - 2), 1, (110, 120, 140), 1.0, 'back')
            fx.poly([(sx_ - 19, ay - 78), (sx_ + 19, ay - 78), (sx_ + 20, ay - 52), (sx_ - 20, ay - 52)], (20, 22, 34), 1.0, 'back')
            fx.poly([(sx_ - 18, ay - 77), (sx_ + 18, ay - 77), (sx_ + 19, ay - 53), (sx_ - 19, ay - 53)], (74, 78, 96), 1.0, 'back')
            fx.poly([(sx_ - 18, ay - 77), (sx_ + 18, ay - 77), (sx_ + 18, ay - 74), (sx_ - 18, ay - 74)], (150, 160, 182), 1.0, 'back')
            fx.poly([(sx_ - 22, ay - 78), (sx_ - 15, ay - 78), (sx_ - 15, ay - 52), (sx_ - 22, ay - 52)], (150, 88, 52), 1.0, 'back')
            fx.poly([(sx_ + 15, ay - 78), (sx_ + 22, ay - 78), (sx_ + 22, ay - 52), (sx_ + 15, ay - 52)], (110, 62, 40), 1.0, 'back')
            fx.glow(sx_, ay - 65, 12, (90, 170, 255), 0.5 * (1 - t))
            wisps(ctx, ax + 14, ay - 8, 56, 16, 12, [(130, 200, 255), (230, 245, 255)], t=t, seed=7, rise=34, a=0.9)
    if n == 'intro':
        intro_fx(ctx)


def intro_fx(ctx):
    i, fx, ax, ay = ctx.i, ctx.fx, ctx.pivot[0], ctx.pivot[1]
    rng = ctx.rng
    # nubarron en lo alto
    cl = [(40, 12, 38, 12), (88, 8, 44, 14), (140, 12, 40, 12), (20, 24, 26, 9), (160, 26, 28, 10), (112, 22, 36, 9)]
    for (x, y, rx, ry) in cl:
        a = 0.9 if i < 7 else 0.9 * clamp01(1 - (i - 6) / 5.0)
        if a > 0.02:
            fx.ell(x, y + 3, rx + 2, ry + 2, (10, 14, 28), a, 'back', soft=1.5)
            fx.ell(x - 2, y, rx, ry, (36, 46, 72), a, 'back', soft=1.5)
            fx.ell(x - 6, y - 3, rx * 0.6, ry * 0.5, (70, 90, 130), a * 0.8, 'back', soft=1.2)
    if 1 <= i <= 2:
        fx.glow(ax, 18, 30, (90, 170, 255), 0.3 + 0.2 * i, rx=60, ry=14)
        for b in range(2):
            bolt(ctx, ax - 16 + b * 30, 14, ax - 10 + b * 16 + rng.random() * 8, 14 + 20 * i, (200, 230, 255), 1.0, i * 3 + b, 3, 5, (80, 150, 255), 'front', 0.7, False)
    if i == 2:
        fx.glow(ax, ay - 20, 30, (130, 200, 255), 0.3, rx=18, ry=90)
    if i == 3:
        # rayo grueso que cae con el titan
        bolt(ctx, ax + 2, 0, ax, ay, (240, 250, 255), 9.0, 3, 5, 12, (90, 170, 255), 'back', 1.0, True)
        bolt(ctx, ax - 6, 0, ax - 2, ay, (240, 250, 255), 4.0, 6, 3, 12, (90, 170, 255), 'back', 0.9, True)
        fx.glow(ax, ay - 40, 60, (150, 215, 255), 0.7, rx=40, ry=90)
    if i == 4:
        bolt(ctx, ax + 3, 0, ax, ay - 40, (240, 250, 255), 6.0, 7, 4, 12, (90, 170, 255), 'back', 0.9, True)
        for kk in range(7):
            px = ax - 36 + kk * 12
            fx.line((px, 6), (px + 1, 60 + (kk % 3) * 18), 1, (210, 235, 255), 0.6, 'front')
    if i == 5:
        # impacto
        fx.poly([(ax - 70, ay + 1), (ax + 70, ay + 1), (ax + 60, ay - 2), (ax - 60, ay - 2)], (16, 20, 34), 0.9, 'back')
        shock(ctx, ax, ay, 0.15, (200, 235, 255), 90, 9, 3)
        fx.glow(ax, ay - 6, 40, (160, 220, 255), 0.9, rx=60, ry=20)
        ground_cracks(ctx, ax, ay + 1, 0.5, (10, 14, 26), (150, 215, 255), 10, 70, 5)
        fx.sparks(rng, ax, ay - 4, 22, 40, [(255, 255, 255), (130, 200, 255)], 'front', 14)
        dust(ctx, ax, ay, 0.15, (110, 125, 150), 14, 54, 12, 3.0)
    if 6 <= i <= 10:
        t = clamp01((i - 5) / 5.0)
        ground_cracks(ctx, ax, ay + 1, 0.5 + t * 0.5, (10, 14, 26), (120, 190, 255), 10, 70, 5)
        shock(ctx, ax, ay, t, (170, 220, 255), 90, 9, 2)
        dust(ctx, ax, ay, t, (110, 125, 150), 14, 60, 12, 3.0, a=0.6)
        if i <= 8:
            fx.glow(ax, ay - 8, 30, (130, 200, 255), 0.5 * (1 - t))
    if i >= 11:
        wisps(ctx, ax, ay - 50, 80, 90, 6, [(130, 200, 255)], t=i / 14.0, seed=9, rise=20, a=0.7)
    if 10 <= i <= 12:
        tx, ty = ctx.anchor('hammer', (0, 84))
        bolt(ctx, tx, ty, tx + 6, 8, (230, 245, 255), 3.0, i, 6, 12, (80, 150, 255), 'front', 0.95, True)
        fx.glow(tx, ty, 16, (140, 210, 255), 0.8)


def hit_boxes():
    return {
        'attack1': dict(hit=[2, 4], box=[8, -96, 86, 96]),
        'attack2': dict(hit=[1, 5], box=[6, -86, 132, 86]),
        'attack3': dict(hit=[4, 6], box=[-90, -62, 184, 62]),
        'cast': dict(rel=4, muzzle_src=('hammer', (0, 84))),
    }


def spec():
    fns = dict(idle=idle_pose, walk=walk_pose, windup1=wind1, attack1=atk1, windup2=wind2, attack2=atk2, windup3=wind3,
               attack3=atk3, cast=cast, hurt=hurt, phase=phase, intro=intro, death=death)
    hb = hit_boxes()
    return {k: dict(pose=v, **hb.get(k, {})) for k, v in fns.items()}


def build():
    return make(spec(), fxhook)
