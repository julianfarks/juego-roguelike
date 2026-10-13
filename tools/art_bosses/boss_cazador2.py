import math
import numpy as np
from kit import *
from shapes import *
from anim import *
from fxlib import *
from boss_common import *

FUR = auto('#3c3042', shadow=(12, 8, 46), warm=(156, 112, 150), n=6, dk=0.26)
FURP = auto('#9a8ea4', shadow=(44, 34, 92), warm=(245, 228, 240), n=6, dk=0.3)
FLESH = auto('#94505e', shadow=(40, 14, 62), warm=(255, 176, 160), n=6, dk=0.26)
BONE = auto('#d2c6ac', shadow=(64, 42, 92), warm=(255, 250, 226), n=6, dk=0.3)
CLOTH = auto('#2c1e2c', shadow=(10, 6, 40), warm=(160, 96, 130), n=6, dk=0.3)
CLOTHR = auto('#82142a', shadow=(30, 6, 50), warm=(255, 110, 110), n=6, dk=0.26)
VOID = ramp((8, 2, 8), (24, 6, 14), (70, 16, 28), 6)
BLOODG = [(60, 6, 20), (150, 16, 44), (232, 44, 76), (255, 150, 150), (255, 240, 236)]
MATS = {'fur': Mat(FUR, texamt=0.7, gain=1.0), 'furp': Mat(FURP, texamt=0.7, gain=1.0), 'flesh': Mat(FLESH, glow=BLOODG, texamt=0.6, gain=1.0),
        'bone': Mat(BONE, gain=1.2, texamt=0.5), 'cloth': Mat(CLOTH, texamt=0.65), 'clothr': Mat(CLOTHR, texamt=0.65),
        'void': Mat(VOID, glow=BLOODG, gain=0.5, texamt=0.2), 'eye': Mat(CLOTHR, glow=BLOODG, texamt=0.2),
        'hat': Mat(auto('#241a26', shadow=(8, 6, 36), warm=(130, 90, 140)), texamt=0.6)}


def build_parts():
    P = []

    def add(*a, **k):
        p = Part(*a, **k); P.append(p); return p
    add('root', None, (96, 156), ghost=True)
    # cola
    t1 = add('tail1', 'root', (-12, -42), z=1.5, mat='fur', depth=4.6, noise=0.5, seed=71)
    t1.tube([(0, 0), (-9, 5), (-18, 4)], 6.4, 4.4)
    fur_edge(t1, [(0, -6), (-9, -1), (-18, -1)], -1, 4, (3, 5), 2.4, 72, mat='bone', raise_=0.5)
    t2 = add('tail2', 'tail1', (-18, 4), z=1.5, mat='fur', depth=3.6, noise=0.5, seed=73)
    t2.tube([(0, 0), (-8, 4), (-16, 12), (-20, 22)], 4.2, 0.8)
    t2.hatch(2, 80, v=0.25, w=0.5, jit=0.4)
    hip = add('hip', 'root', (0, -46), z=4, mat='fur', depth=7.4, noise=0.8, seed=5, tnoise=0.3)
    hip.spl([(-16, -6), (-6, -11), (10, -9), (18, -1), (18, 9), (8, 13), (-8, 13), (-18, 5)])
    hip.hatch(2.0, 70, v=0.28, w=0.5, jit=0.6)
    fur_edge(hip, [(-18, 4), (-16, -6), (-6, -11)], -1, 4, (3, 5), 2.6, 5)
    for nm, x, z, dim in (('b', -9, 2, -0.24), ('f', 7, 5, 0.0)):
        th = add('thigh_' + nm, 'hip', (x, 2), z=z, mat='fur', depth=8.0, noise=0.8, seed=10, dim=dim, tnoise=0.25)
        th.tube([(0, 0), (2, 11), (4, 23)], 10.5, 6.5)
        th.hatch(2.0, 80, v=0.28, w=0.5, jit=0.6)
        fur_edge(th, [(-9, 0), (-7, 10), (-2, 22)], -1, 5, (3, 5.5), 2.6, 11 + (x > 0))
        th.poly([(2, 20), (10, 21), (8, 28), (3, 27)], mat='bone', raise_=0.6, edge=0.1)
        th.blotch('furp', 0.7, 3.0, 12)
        sh = add('shin_' + nm, 'thigh_' + nm, (4, 23), z=z, mat='fur', depth=5.4, noise=0.6, seed=13, dim=dim, tnoise=0.25)
        sh.tube([(0, 0), (-2, 12), (-1, 24)], 6.8, 4.2)
        sh.hatch(2.0, 80, v=0.28, w=0.5, jit=0.6)
        fur_edge(sh, [(-6, 2), (-8, 12), (-5, 22)], -1, 4, (2.5, 4.5), 2.4, 14)
        ft = add('foot_' + nm, 'shin_' + nm, (-1, 24), z=z, mat='fur', depth=3.6, noise=0.5, seed=15, dim=dim)
        ft.spl([(-6, -5), (3, -6), (9, -3), (16, 0), (21, 3), (19, 6), (-7, 6)])
        for k in range(3):
            ft.poly([(15 + k * 2.2, 0.5 + k * 1.2), (19 + k * 2.2, 1.5 + k * 1.2), (26 + k * 1.4, 4 + k * 0.4), (19 + k * 2.2, 4.4 + k * 1.2)], mat='bone', raise_=0.5, edge=0.1)
    # torso
    to = add('torso', 'hip', (2, -6), z=6, mat='fur', depth=11.0, noise=1.4, nscale=3.5, seed=20, tnoise=0.3)
    to.spl([(-18, 0), (-25, -14), (-23, -32), (-13, -46), (4, -51), (19, -45), (27, -31), (29, -15), (20, -1), (4, 3)])
    to.hatch(2.2, 75, v=0.27, w=0.5, jit=0.6)
    to.spl([(8, -3), (21, -6), (29, -17), (26, -31), (16, -33), (10, -20)], mat='flesh', raise_=0.7, edge=0.2)
    to.cracks(10, 9, v=0.1, w=0.7, seed=21, emit=1.0)
    to.blotch('furp', 0.68, 3.2, 22)
    for k in range(4):
        to.line(bez((6, -8 - k * 6), (16, -11 - k * 6), (26, -9 - k * 6), n=7), 0.7, op='tex', v=0.1)
    fur_edge(to, [(-16, 0), (-24, -14), (-22, -32), (-12, -46), (4, -51)], -1, 11, (5, 9), 3.4, 23, drift=0.6)
    fur_edge(to, [(-14, -4), (-22, -16), (-20, -32), (-10, -46)], -1, 6, (4, 6), 2.2, 24, mat='bone', raise_=0.6)
    to.cracks(3, 8, v=0.1, w=0.6, seed=25)
    # mane
    ma = add('mane', 'torso', (-4, -44), z=4.5, mat='furp', depth=4.0, noise=0.8, seed=26, tnoise=0.3)
    ma.poly([(6, 2), (-12, -2), (-26, -10), (-22, -16), (-30, -18), (-22, -24), (-26, -30), (-14, -28), (-4, -34), (8, -22), (12, -6)])
    ma.hatch(2.0, 70, v=0.25, w=0.5, jit=0.6)
    # harapos del abrigo
    for nm, par, at, sd in (('rag1', 'torso', (-6, -40), 28), ('rag2', 'rag1', (-4, 22), 29)):
        r = add(nm, par, at, z=7.2, mat='cloth', depth=2.4, noise=0.4, seed=sd)
        if nm == 'rag1':
            r.spl([(-3, -2), (6, -2), (8, 10), (6, 22), (-2, 24), (-6, 12)])
            r.spl([(0, 0), (5, 0), (6, 12), (4, 20), (0, 14)], mat='clothr', raise_=0.3, edge=0.2)
        else:
            r.poly([(-4, -2), (6, -2), (5, 8), (7, 16), (2, 12), (0, 20), (-3, 10)])
        r.hatch(2.6, 84, v=0.3, w=0.5, jit=0.4)
    # cabeza
    hd = add('head', 'torso', (14, -46), z=12, mat='fur', depth=7.4, noise=0.6, seed=30, tnoise=0.25)
    hd.spl([(-10, -4), (-12, -14), (-4, -22), (8, -22), (18, -14), (28, -8), (34, -3), (33, 2), (22, 4), (8, 5), (-4, 5)])
    hd.spl([(-6, -2), (4, 0), (24, 0), (31, -1), (31, 3), (22, 4), (6, 4)], mat='bone', raise_=0.3, edge=0.3)
    hd.hatch(2.0, 40, v=0.28, w=0.5, jit=0.6)
    hd.spl([(8, -2), (30, 0), (28, 4), (10, 4)], mat='void', raise_=-0.5)
    hd.ell(7, -12, 3.6, 2.6, rot=-12, mat='void', raise_=-0.5)
    hd.ell(7.4, -12, 2.4, 1.6, rot=-12, mat='eye'); hd.ell(7.4, -12, 2.0, 1.3, rot=-12, op='emit', v=1.0, soft=0.3)
    hd.ell(-1, -14.5, 1.8, 1.4, mat='eye'); hd.ell(-1, -14.5, 1.4, 1.1, op='emit', v=0.9, soft=0.2)
    hd.ell(14, -14, 1.6, 1.3, mat='eye'); hd.ell(14, -14, 1.2, 1.0, op='emit', v=0.9, soft=0.2)
    hd.line([(1, -17), (8, -18), (17, -13)], 1.4, op='tex', v=0.08)
    for k in range(5):
        hd.poly([(10 + k * 4, 3.5), (12.6 + k * 4, 3.5), (11.6 + k * 4 + (k > 3) * 1.5, 9 - (k % 2) * 2)], mat='bone', raise_=0.6, edge=0.1)
    hd.line([(22, -6), (28, -5)], 0.7, op='tex', v=0.1)
    hd.blotch('furp', 0.7, 2.6, 31)
    fur_edge(hd, [(-10, -4), (-12, -14), (-4, -22)], -1, 4, (3, 5), 2.2, 32)
    jw = add('jaw', 'head', (6, 3), z=11.5, mat='fur', depth=4.4, noise=0.5, seed=34)
    jw.spl([(-6, 0), (16, -1), (27, 1), (26, 5), (14, 10), (2, 11), (-6, 7)])
    for k in range(4):
        jw.poly([(13 + k * 3.6, 0), (15.4 + k * 3.6, 0), (14.4 + k * 3.6, -5.5 + (k % 2))], mat='bone', raise_=0.6, edge=0.1)
    jw.spl([(0, 1), (16, 0), (24, 2), (22, 5), (10, 8), (0, 6)], mat='void', raise_=-0.4)
    jw.hatch(2.2, 60, v=0.28, w=0.5, jit=0.6)
    # cuernos
    for nm, x, z, dim, sd in (('b', -5, 11.2, -0.2, 40), ('f', 3, 12.4, 0.0, 41)):
        hr = add('horn_' + nm, 'head', (x, -19), z=z, mat='bone', depth=4.2, noise=0.3, seed=sd, dim=dim, tnoise=0.2)
        hr.tube([(0, 0), (-8, -9), (-8, -23), (0, -34), (12, -37)], 5.6, 0.8)
        for k in range(6):
            hr.line([(-5 - k * 0.2, -5 - k * 5), (-10, -4 - k * 5)], 0.7, op='tex', v=0.15)
        hr.cracks(2, 6, v=0.12, w=0.5, seed=sd + 3)
    ht = add('hat', 'horn_b', (10, -36), z=13, mat='hat', depth=2.6, noise=0.2, seed=44)
    ht.spl([(-10, 3), (-4, 0), (6, 0), (14, -2), (18, 2), (10, 5), (-2, 6)], per=5)
    ht.spl([(-4, 0), (-4, -6), (2, -9), (8, -5), (8, 0)], per=5)
    ht.poly([(-4, -1), (8, -1), (8, 1.2), (-4, 1.2)], mat='clothr', raise_=0.5, edge=0.1)
    # brazos
    for nm, x, z, dim in (('b', 4, 3, -0.26), ('f', 18, 10, 0.0)):
        ua = add('uarm_' + nm, 'torso', (x, -37), z=z, mat='fur', depth=9.0, noise=0.9, seed=50, dim=dim, tnoise=0.25)
        ua.tube([(0, 0), (2, 15), (1, 30)], 12.0, 8.6)
        ua.hatch(2.0, 80, v=0.27, w=0.5, jit=0.6)
        fur_edge(ua, [(-11, 0), (-9, 14), (-8, 28)], -1, 5, (3, 6), 2.8, 51)
        fur_edge(ua, [(10, 0), (9, 14), (8, 28)], 1, 4, (3, 5), 2.6, 52)
        ua.poly([(-8, 2), (-2, -12), (4, 2)], mat='bone', raise_=0.7, edge=0.1)
        ua.blotch('flesh', 0.74, 2.8, 53)
        fa = add('farm_' + nm, 'uarm_' + nm, (1, 30), z=z, mat='fur', depth=7.6, noise=0.8, seed=54, dim=dim, tnoise=0.25)
        fa.tube([(0, 0), (0, 16), (1, 32)], 9.2, 7.4)
        fa.hatch(2.0, 80, v=0.27, w=0.5, jit=0.6)
        fur_edge(fa, [(-8, 0), (-8, 16), (-6, 30)], -1, 4, (3, 5.5), 2.6, 55)
        fa.poly([(-6, 22), (6, 22), (6, 26), (-6, 26)], mat='bone', raise_=0.6, edge=0.1)
        fa.blotch('flesh', 0.76, 2.6, 56)
        hn = add('hand_' + nm, 'farm_' + nm, (1, 32), z=z + 0.2, mat='fur', depth=5.0, noise=0.5, seed=57, dim=dim)
        hn.spl([(-8, -3), (8, -3), (10, 6), (7, 14), (-6, 14), (-10, 6)])
        for k in range(4):
            xx = -6 + k * 4.2
            hn.tube([(xx, 10), (xx + 1.2, 17), (xx + 3.4, 24 + (k % 2) * 2)], 2.4, 0.5, mat='bone', raise_=0.6, edge=0.1)
        hn.hatch(2, 70, v=0.27, w=0.5, jit=0.5)
    return P


def make(anims, fxhook):
    return Boss('cazador2', (192, 160), (96, 156), (46, 108), build_parts(), MATS, anims, fxhook,
                outline=(10, 4, 16), rim=(255, 90, 110), rimk=0.38, dis_col=(255, 60, 70), seed=61, scale=0.86)


# ====================================================================== animaciones
def PZ(*ds):
    return merge(*ds)


def L(thf, shf, thb, shb):
    return {'thigh_f': thf, 'shin_f': shf, 'foot_f': -(thf + shf) * 0.95, 'thigh_b': thb, 'shin_b': shb, 'foot_b': -(thb + shb) * 0.95}


def A(uf, ff, hf, ub, fb, hb):
    return {'uarm_f': uf, 'farm_f': ff, 'hand_f': hf, 'uarm_b': ub, 'farm_b': fb, 'hand_b': hb}


def rags(f, n, amp=1.0, base=0.0, ph=0.0):
    return {'rag1': base * 0.5 + amp * 3.0 * S(f, n, ph), 'rag2': base + amp * 5.0 * S(f, n, ph + 0.15),
            'tail1': amp * 3 * S(f, n, ph + 0.3), 'tail2': amp * 6 * S(f, n, ph + 0.45), 'hat': amp * 2 * S(f, n, ph)}


STAND = PZ(L(-26, 46, -22, 40), A(-8, 6, 0, 4, 8, 0), {'torso': 22, 'head': -12, 'jaw': 5})


def idle_pose(f):
    b = S(f, 6)
    return PZ(STAND, {'root.y': -1.2 * b, 'torso': 1.6 * b, 'torso.sx': 1 + 0.018 * b, 'torso.sy': 1 + 0.018 * b, 'head': -2.5 * b, 'jaw': 4 + 4 * b, 'uarm_f': -2 * b, 'uarm_b': 2 * b, 'hand_f': 3 * b},
              rags(f, 6, 1.0, 2))


def walk_pose(f):
    ph = 2 * math.pi * f / 8
    s = math.sin(ph); c = math.cos(ph)
    return PZ(L(-26 + 20 * s, 46 - 14 * max(0, c) + 10 * s * s, -22 - 20 * s, 40 - 14 * max(0, -c)),
              A(-8 - 26 * s, 6 + 10 * max(0, -s), 0, 4 + 26 * s, 8 + 10 * max(0, s), 0),
              {'torso': 24 + 3 * c, 'head': -12 - 3 * c, 'root.y': -2.5 * abs(c) + 1.5, 'jaw': 6 + 3 * c}, rags(f, 8, 1.6, 5))


WIND1 = [(0, STAND),
         (1, PZ(L(-26, 46, -22, 40), A(-70, -30, 0, 14, 10, 0), {'torso': 12, 'head': -20, 'jaw': 12, 'root.y': 1})),
         (2, PZ(L(-22, 40, -18, 34), A(-130, -34, 4, 18, 10, 0), {'torso': 0, 'head': -26, 'jaw': 20, 'root.y': -2, 'root.x': -3})),
         (3, PZ(L(-20, 36, -16, 30), A(-134, -26, 8, 20, 10, 0), {'torso': -8, 'head': -30, 'jaw': 28, 'root.y': -5, 'root.x': -5})),
         (4, PZ(L(-18, 34, -14, 28), A(-140, -22, 10, 22, 10, 0), {'torso': -12, 'head': -32, 'jaw': 32, 'root.y': -6, 'root.x': -6}))]
wind1k = K(WIND1)


def wind1(f):
    return PZ(wind1k(f), rags(f, 5, 0.8, 3 + f))


ATK1 = [(0, WIND1[-1][1], 'sm'),
        (1, PZ(L(-26, 44, -22, 38), A(-120, -34, 4, 20, 10, 0), {'torso': 2, 'head': -20, 'jaw': 20, 'root.y': -4, 'root.x': 0}), 'snap'),
        (2, PZ(L(-30, 50, -26, 42), A(-64, -20, 0, 20, 10, 0), {'torso': 26, 'head': -10, 'jaw': 10, 'root.y': 0, 'root.x': 8}), 'snap'),
        (3, PZ(L(-34, 56, -28, 46), A(-18, -4, -10, 18, 10, 0), {'torso': 40, 'head': -4, 'jaw': 6, 'root.y': 4, 'root.x': 14}), 'snap'),
        (4, PZ(L(-34, 56, -28, 46), A(-12, 0, -10, 18, 10, 0), {'torso': 42, 'head': -4, 'jaw': 6, 'root.y': 5, 'root.x': 15}), 'out'),
        (5, PZ(L(-32, 52, -26, 44), A(-12, 4, -6, 14, 10, 0), {'torso': 36, 'head': -6, 'root.y': 4, 'root.x': 12}), 'sm'),
        (6, PZ(L(-28, 48, -24, 42), A(-10, 6, -2, 8, 8, 0), {'torso': 28, 'head': -10, 'root.y': 2, 'root.x': 5}), 'sm'),
        (7, STAND, 'sm')]
atk1k = K(ATK1)


def atk1(f):
    return PZ(atk1k(f), rags(f, 8, 1.4, 8 - f * 0.6, 0.2))


WIND2 = [(0, STAND),
         (1, PZ(L(-40, 70, -36, 66), A(10, 20, 0, 24, 20, 0), {'torso': 30, 'head': -6, 'jaw': 10, 'root.y': 8, 'root.x': -3})),
         (2, PZ(L(-52, 94, -48, 90), A(30, 30, 0, 40, 30, 0), {'torso': 38, 'head': -2, 'jaw': 16, 'root.y': 16, 'root.x': -6})),
         (3, PZ(L(-58, 108, -54, 104), A(44, 36, 0, 54, 36, 0), {'torso': 42, 'head': 2, 'jaw': 24, 'root.y': 22, 'root.x': -9})),
         (4, PZ(L(-60, 112, -56, 108), A(50, 40, 0, 60, 40, 0), {'torso': 44, 'head': 4, 'jaw': 28, 'root.y': 24, 'root.x': -10}))]
wind2k = K(WIND2)


def wind2(f):
    return PZ(wind2k(f), rags(f, 5, 0.5, -2 - f * 2, 0.3))


ATK2 = [(0, WIND2[-1][1], 'sm'),
        (1, PZ(L(20, 20, 30, 10), A(-60, -20, 0, -50, -20, 0), {'torso': 56, 'head': -18, 'jaw': 30, 'root.y': -12, 'root.x': 10}), 'snap'),
        (2, PZ(L(40, 10, 46, 6), A(-100, -10, 6, -96, -10, 6), {'torso': 74, 'head': -34, 'jaw': 34, 'root.y': -22, 'root.x': 22}), 'snap'),
        (3, PZ(L(44, 8, 50, 4), A(-104, -6, 6, -100, -6, 6), {'torso': 78, 'head': -38, 'jaw': 34, 'root.y': -22, 'root.x': 25}), 'out'),
        (4, PZ(L(36, 12, 42, 8), A(-96, -8, 6, -90, -8, 6), {'torso': 74, 'head': -34, 'jaw': 30, 'root.y': -16, 'root.x': 25}), 'sm'),
        (5, PZ(L(-10, 30, -6, 24), A(-70, -20, 4, -64, -20, 4), {'torso': 56, 'head': -24, 'jaw': 20, 'root.y': -2, 'root.x': 24}), 'sm'),
        (6, PZ(L(-28, 48, -24, 42), A(-30, -4, 0, -20, 0, 0), {'torso': 38, 'head': -16, 'jaw': 10, 'root.y': 4, 'root.x': 15}), 'sm'),
        (7, STAND, 'sm')]
atk2k = K(ATK2)


def atk2(f):
    return PZ(atk2k(f), rags(f, 8, 2.0, -16 + f * 2, 0.0))


WIND3 = [(0, STAND),
         (1, PZ(L(-40, 72, -36, 68), A(10, 20, 0, 20, 20, 0), {'torso': 28, 'head': -6, 'jaw': 10, 'root.y': 8})),
         (2, PZ(L(-50, 90, -46, 86), A(-70, -30, 0, -60, -30, 0), {'torso': 12, 'head': -20, 'jaw': 20, 'root.y': 4})),
         (3, PZ(L(-18, 30, -14, 26), A(-122, -30, 8, -118, -30, 8), {'torso': -6, 'head': -30, 'jaw': 30, 'root.y': -22})),
         (4, PZ(L(-8, 14, -6, 12), A(-130, -24, 10, -126, -24, 10), {'torso': -14, 'head': -34, 'jaw': 34, 'root.y': -22})),
         (5, PZ(L(-6, 12, -4, 10), A(-134, -22, 10, -130, -22, 10), {'torso': -16, 'head': -36, 'jaw': 36, 'root.y': -24}))]
wind3k = K(WIND3)


def wind3(f):
    return PZ(wind3k(f), rags(f, 6, 1.0, 6 - f, 0.3))


ATK3 = [(0, WIND3[-1][1], 'sm'),
        (1, PZ(L(-10, 20, -8, 18), A(-124, -24, 8, -120, -24, 8), {'torso': -4, 'head': -30, 'jaw': 30, 'root.y': -20}), 'sm'),
        (2, PZ(L(-22, 36, -18, 32), A(-80, -16, 0, -76, -16, 0), {'torso': 22, 'head': -16, 'jaw': 16, 'root.y': -16}), 'in'),
        (3, PZ(L(-30, 52, -26, 46), A(-26, -4, -10, -22, -4, -10), {'torso': 40, 'head': -6, 'jaw': 6, 'root.y': 2, 'root.x': 8}), 'snap'),
        (4, PZ(L(-36, 66, -32, 60), A(-14, 2, -12, -10, 2, -12), {'torso': 44, 'head': -4, 'jaw': 6, 'root.y': 8, 'root.x': 10}), 'snap'),
        (5, PZ(L(-36, 66, -32, 60), A(-12, 4, -12, -8, 4, -12), {'torso': 46, 'head': -4, 'jaw': 6, 'root.y': 9, 'root.x': 10}), 'sm'),
        (6, PZ(L(-34, 62, -30, 56), A(-12, 4, -8, -8, 4, -8), {'torso': 42, 'head': -6, 'root.y': 8, 'root.x': 9}), 'sm'),
        (7, PZ(L(-30, 54, -26, 48), A(-10, 6, -4, 0, 6, -2), {'torso': 32, 'head': -8, 'root.y': 4, 'root.x': 4}), 'sm'),
        (8, STAND, 'sm')]
atk3k = K(ATK3)


def atk3(f):
    return PZ(atk3k(f), rags(f, 9, 2.0, -10 if f in (1, 2, 3) else 6, 0.0))


CAST = K([(0, STAND),
          (1, PZ(L(-26, 46, -22, 40), A(-20, 0, 0, 8, 8, 0), {'torso': 16, 'head': -22, 'jaw': 14, 'root.y': 1})),
          (2, PZ(L(-24, 44, -20, 38), A(-50, -14, 0, -30, -14, 0), {'torso': 4, 'head': -36, 'jaw': 28, 'root.y': -2}), 'sm'),
          (3, PZ(L(-22, 40, -18, 34), A(-70, -20, 0, -56, -20, 0), {'torso': -4, 'head': -44, 'jaw': 38, 'root.y': -3}), 'sm'),
          (4, PZ(L(-22, 40, -18, 34), A(-76, -22, 0, -62, -22, 0), {'torso': -6, 'head': -48, 'jaw': 42, 'root.y': -3, 'root.x': -2}), 'snap'),
          (5, PZ(L(-24, 42, -20, 36), A(-60, -18, 0, -50, -18, 0), {'torso': 2, 'head': -40, 'jaw': 34, 'root.y': -2}), 'out'),
          (6, PZ(L(-26, 46, -22, 40), A(-30, -6, 0, -10, 0, 0), {'torso': 14, 'head': -22, 'jaw': 14}), 'sm'),
          (7, STAND, 'sm')])


def cast(f):
    return PZ(CAST(f), rags(f, 8, 1.8, 4, 0.0))


def hurt(f):
    d = [PZ(L(-22, 42, -18, 36), A(-4, 14, 0, 10, 16, 0), {'torso': 10, 'head': -26, 'jaw': 24, 'root.x': -4, 'root.y': 1, 'tint': ((255, 255, 255), 0.5)}),
         PZ(L(-24, 44, -20, 38), A(-6, 10, 0, 8, 12, 0), {'torso': 16, 'head': -18, 'jaw': 14, 'root.x': -2, 'tint': ((255, 255, 255), 0.2)})][int(f)]
    return PZ(d, rags(f, 2, 1, 6 + 4 * (1 - f)))


PHASE = K([(0, STAND),
           (1, PZ(L(-34, 60, -30, 54), A(10, 20, 0, 20, 20, 0), {'torso': 34, 'head': -4, 'jaw': 6, 'root.y': 5}), 'sm'),
           (2, PZ(L(-40, 72, -36, 66), A(30, 30, 0, 40, 30, 0), {'torso': 42, 'head': 4, 'jaw': 10, 'root.y': 9}), 'sm'),
           (3, PZ(L(-22, 38, -18, 34), A(-60, -20, 0, -56, -20, 0), {'torso': 8, 'head': -20, 'jaw': 22, 'root.y': -4}), 'out'),
           (4, PZ(L(-12, 20, -8, 18), A(-132, -10, 10, -128, -10, 10), {'torso': -14, 'head': -46, 'jaw': 44, 'root.y': -12, 'torso.sx': 1.06, 'torso.sy': 1.05}), 'snap'),
           (5, PZ(L(-10, 16, -6, 14), A(-140, -6, 14, -136, -6, 14), {'torso': -18, 'head': -52, 'jaw': 48, 'root.y': -14, 'torso.sx': 1.08, 'torso.sy': 1.07}), 'sm'),
           (6, PZ(L(-10, 16, -6, 14), A(-140, -6, 14, -136, -6, 14), {'torso': -18, 'head': -50, 'jaw': 46, 'root.y': -13, 'torso.sx': 1.07, 'torso.sy': 1.06}), 'sm'),
           (7, PZ(L(-16, 28, -12, 24), A(-100, -14, 6, -96, -14, 6), {'torso': -4, 'head': -34, 'jaw': 30, 'root.y': -6}), 'in'),
           (8, PZ(L(-24, 42, -20, 36), A(-40, 0, 0, -30, 0, 0), {'torso': 16, 'head': -20, 'jaw': 14, 'root.y': 1}), 'snap'),
           (9, STAND, 'sm')])


def phase(f):
    p = PHASE(f)
    if 4 <= f <= 7:
        p['tint'] = ((255, 90, 120), 0.22 * (1 - abs(f - 5.5) / 2.0))
    p['root.x'] = p.get('root.x', 0) + (1.4 if (f in (5, 6) and int(f) % 2) else (-1.4 if f in (5, 6) else 0))
    return PZ(p, rags(f, 10, 2.4, -8 if 3 <= f <= 7 else 4, 0.0))


def intro(f):
    i = int(f)
    rise = [150, 150, 150, 150, 120, 96, 72, 50, 34, 20, 10, 4, 0, 0][i] if f == i else None
    arr = [150, 150, 150, 150, 120, 96, 72, 50, 34, 20, 10, 4, 0, 0]
    ry = arr[i] + (arr[min(13, i + 1)] - arr[i]) * (f - i)
    up = clamp01((f - 6) / 5.0)
    p = PZ(STAND, {'root.y': ry * 0.42, 'head': -30 * (1 - up) + (-18 if 10 <= i <= 12 else 0), 'jaw': 30 * clamp01((i - 9) / 2.0) * (1 if i < 13 else 0.2),
                   'torso': 22 + 30 * (1 - up) - 8 * (1 if 10 <= i <= 12 else 0)},
           A(-8 - 70 * (1 - up) + (-50 if 10 <= i <= 12 else 0), 6, 0, 4 + 40 * (1 - up), 8, 0),
           L(-26 - 30 * (1 - up), 46 + 40 * (1 - up), -22 - 30 * (1 - up), 40 + 40 * (1 - up)), rags(f, 14, 1.6, 6))
    p['clip'] = (0, 0, 192, 157) if i >= 3 else (0, 0, 0, 0)
    return p


DEATH = K([(0, PZ(L(-22, 42, -18, 36), A(-4, 14, 0, 10, 16, 0), {'torso': 10, 'head': -26, 'jaw': 24, 'root.x': -4, 'tint': ((255, 255, 255), 0.5)}), 'out'),
           (1, PZ(L(-22, 48, -18, 42), A(-30, -10, 0, 0, 0, 0), {'torso': 4, 'head': -34, 'jaw': 32, 'root.x': -6, 'tint': ((255, 255, 255), 0.2)}), 'sm'),
           (2, PZ(L(-30, 60, -26, 54), A(-70, -20, 0, -40, -10, 0), {'torso': -6, 'head': -44, 'jaw': 42, 'root.x': -6, 'root.y': 6, 'tint': ((255, 255, 255), 0.0)}), 'sm'),
           (3, PZ(L(-40, 84, -34, 78), A(-40, -10, 0, -20, 0, 0), {'torso': 14, 'head': -20, 'jaw': 24, 'root.x': -4, 'root.y': 16}), 'sm'),
           (4, PZ(L(-50, 110, -46, 104), A(-10, 14, 0, 10, 14, 0), {'torso': 30, 'head': 0, 'jaw': 10, 'root.x': -2, 'root.y': 28}), 'sm'),
           (5, PZ(L(-58, 124, -54, 118), A(10, 20, 0, 16, 20, 0), {'torso': 42, 'head': 10, 'jaw': 6, 'root.x': 0, 'root.y': 36}), 'sm'),
           (6, PZ(L(-62, 132, -58, 126), A(20, 24, 0, 24, 24, 0), {'torso': 52, 'head': 22, 'jaw': 4, 'root.x': 2, 'root.y': 42}), 'sm'),
           (7, PZ(L(-62, 134, -58, 128), A(26, 26, 0, 30, 26, 0), {'torso': 62, 'head': 28, 'jaw': 3, 'root.x': 4, 'root.y': 46}), 'in'),
           (13, PZ(L(-62, 134, -58, 128), A(30, 28, 0, 34, 28, 0), {'torso': 70, 'head': 32, 'jaw': 2, 'root.x': 6, 'root.y': 50}), 'lin')])


def death(f):
    p = DEATH(f)
    d = clamp01((f - 6.5) / 5.5)
    if d > 0:
        p['dis'] = d * 1.12
        p['dis_dir'] = 1.0
    c = clamp01((f - 3.0) / 4.0)
    p['hat.y'] = 0 if f < 3 else 6 * c
    p.update(rags(f, 14, 0.5, 6 + f * 2))
    return p


# ====================================================================== efectos
def moon(fx, x, y, r, a=1.0, layer='back'):
    fx.glow(x, y, r * 1.8, (230, 20, 50), 0.45 * a)
    fx.ell(x, y, r + 1.5, r + 1.5, (90, 10, 30), a, layer)
    fx.ell(x, y, r, r, (196, 28, 52), a, layer)
    fx.ell(x - r * 0.15, y - r * 0.15, r * 0.8, r * 0.8, (226, 60, 70), a, layer)
    fx.ell(x - r * 0.3, y - r * 0.3, r * 0.4, r * 0.4, (240, 100, 100), a * 0.8, layer)


def fxhook(ctx):
    n, i, fx, W = ctx.name, ctx.i, ctx.fx, ctx.W
    ax, ay = ctx.pivot
    rng = ctx.rng
    claw = lambda f=None: ctx.anchor('hand_f', (1, 22)) if f is None else ctx.anchor_at(f, 'hand_f', (1, 22))
    mouth = lambda: ctx.anchor('jaw', (24, 2))
    for (pt, bn) in (((7.4, -12), 'head'), ((-1, -14.5), 'head'), ((14, -14), 'head')):
        ex, ey = ctx.anchor(bn, pt)
        if n != 'death' or i < 5:
            fx.glow(ex, ey, 6 if pt[0] == 7.4 else 4, (255, 40, 60), 0.6)
    bx, by = ctx.anchor('torso', (18, -18))
    if n not in ('death',):
        fx.glow(bx, by, 16, (255, 40, 70), 0.22 + 0.08 * math.sin(i * 1.3))
    if n not in ('intro', 'death'):
        wisps(ctx, ax - 6, ay - 60, 60, 80, 6, [(255, 80, 110), (255, 190, 200)], seed=3, a=0.7, rise=16)
    mx, my = mouth()
    if n in ('idle', 'walk', 'windup1', 'windup2', 'windup3', 'cast', 'phase'):
        fx.glow(mx - 4, my + 1, 8, (255, 40, 60), 0.35)
    if n == 'windup1':
        t = i / 4.0
        cx_, cy_ = claw()
        fx.glow(cx_, cy_, 8 + 10 * t, (255, 60, 90), 0.4 * t + 0.1)
    if n == 'attack1':
        trail(ctx, 'hand_f', (1, 26), (1, 8), 0, 4, (255, 235, 235), (170, 20, 50), steps=12, span=3.2, mid=(240, 60, 90), a=0.85)
        trail(ctx, 'hand_f', (-5, 26), (-5, 8), 0, 4, (255, 215, 215), (120, 10, 40), steps=12, span=3.2, a=0.6)
        if 3 <= i <= 6:
            cx_, cy_ = claw(3.4)
            tt = (i - 3) / 3.0
            gx = min(cx_, W - 6)
            dust(ctx, gx, ay, tt, (100, 70, 90), 12, 28, 10)
            shock(ctx, gx, ay, tt, (255, 100, 130), 40, 5)
            fx.glow(gx, ay - 4, 14 * (1 - tt * 0.5), (255, 80, 110), 0.8 * (1 - tt))
            if i == 3:
                fx.sparks(rng, gx, ay - 3, 14, 16, [(255, 255, 255), (255, 90, 110)], 'front', 8)
    if n == 'windup2':
        t = i / 4.0
        fx.glow(ax, ay - 30, 30 + 10 * t, (255, 40, 60), 0.3 * t, rx=36, ry=24)
        wisps(ctx, ax, ay - 3, 60, 6, 8, [(130, 80, 100)], t=t, seed=5, rise=12, a=0.8)
    if n == 'attack2' and 1 <= i <= 6:
        x1, y1 = ctx.anchor('torso', (0, -26))
        t = clamp01((i - 1) / 5.0)
        for k in range(7):
            yy = ay - 12 - k * 13
            x0 = x1 - 26 - ((i * 9 + k * 17) % 18)
            fx.line((x0, yy), (x0 - 20 - 5 * k, yy), 1 + (k % 2), (240, 50, 80), 0.7 * (1 - t * 0.4), 'front')
        dust(ctx, ax + ctx.pose.get('root.x', 0) * 0.4 - 8, ay, clamp01((i - 1) / 4.0), (110, 80, 100), 10, 24, 8, a=0.6)
        cx_, cy_ = claw()
        if 2 <= i <= 4:
            fx.glow(min(W - 6, cx_ + 2), cy_, 12, (255, 120, 140), 0.8)
            impact_star(ctx, min(W - 8, cx_ + 4), cy_, (i - 2) / 2.0, (255, 200, 210), 14, 8)
    if n == 'windup3':
        t = i / 5.0
        rays(ctx, ax, ay - 2, t * 0.6, (230, 30, 60), 6, 6, 30, 0.18, 0.4 * t, 0.4, 'back')
        wisps(ctx, ax, ay - 3, 60, 6, 8, [(255, 70, 100)], t=t, seed=5, rise=26, a=0.7)
    if n == 'attack3':
        if 4 <= i <= 8:
            t = (i - 4) / 4.0
            gx = ax + 40
            ground_cracks(ctx, gx, ay + 1, t, (30, 6, 20), (255, 70, 100), 9, 64, 11)
            shock(ctx, gx, ay, t, (255, 120, 140), 76, 8, 2)
            dust(ctx, gx, ay, t, (110, 80, 100), 16, 46, 14, 3.2)
            if i <= 6:
                fx.glow(gx, ay - 6, 24 * (1 - t * 0.5), (255, 80, 110), 0.9 * (1 - t))
                for k in range(7):
                    ang = math.pi * (0.1 + 0.8 * rng.random())
                    r = 8 + 36 * t * rng.random()
                    px = gx + math.cos(ang) * r * (1 if k % 2 else -1); py = ay - math.sin(ang) * r * 0.9
                    fx.poly([(px - 2, py + 2), (px + 2, py + 2), (px + 0.5, py - 3 - 3 * rng.random())], (70, 54, 74), 1.0, 'front', ss=2)
    if n == 'cast':
        if 1 <= i <= 3:
            for k in range(3):
                r = 10 + 14 * ((i * 0.5 + k * 0.33) % 1)
                fx.ring(mx + 4, my, r, r * 0.8, 1, (255, 120, 140), 0.7 * (1 - r / 26), 'front', a0=-50, a1=50)
        if i >= 4:
            tt = (i - 4) / 3.0
            for k in range(3):
                sx_ = mx + 6 + tt * (46 + k * 12)
                sy_ = my - 4 + (k - 1) * 12 * tt
                if sx_ < W - 5:
                    fx.glow(sx_, sy_, 9, (255, 50, 90), 0.85)
                    fx.poly([(sx_ - 3, sy_ - 3), (sx_ + 6, sy_), (sx_ - 3, sy_ + 3)], (200, 24, 56), 1.0, 'front')
                    fx.poly([(sx_ - 1, sy_ - 1.4), (sx_ + 4, sy_), (sx_ - 1, sy_ + 1.4)], (255, 170, 180), 1.0, 'front')
                    fx.polyline([(sx_ - 4, sy_), (sx_ - 14, sy_), (sx_ - 24, sy_)], 2, (230, 30, 64), 0.5, 'front')
            for k in range(2):
                r = 6 + 22 * ((tt + k * 0.5) % 1)
                fx.ring(mx + 2, my, r, r * 0.8, 1, (255, 150, 160), 0.7 * (1 - r / 28), 'front', a0=-60, a1=60)
    if n == 'phase':
        t = clamp01((i - 3) / 5.0)
        if 3 <= i <= 9:
            fx.glow(ax, ay - 60, 70 * t + 14, (255, 30, 70), 0.5 * (1 - abs(t - 0.5) * 1.2), rx=60 * t + 16, ry=70 * t + 16)
            rays(ctx, ax, ay - 66, t, (255, 70, 100), 16, 14, 90, 0.1, 0.5, i * 0.1, 'back')
            shock(ctx, ax, ay, clamp01((i - 4) / 5.0), (255, 90, 120), 66, 7, 2)
        if 4 <= i <= 8:
            cx0, cy0 = ctx.anchor('torso', (6, -26))
            for k in range(6):
                a = k * 1.05 + i
                x2, y2 = cx0 + math.cos(a) * (14 + 6 * t), cy0 + math.sin(a) * (16 + 6 * t)
                fx.line((cx0, cy0), (x2, y2), 1, (200, 190, 255), 0.9, 'front')
            starfield(ctx, cx0, cy0, 30, 34, 14, 5, i / 10.0, 1.0)
            wisps(ctx, ax, ay - 56, 52, 80, 16, [(255, 100, 130), (255, 235, 235)], t=(i - 4) / 6.0, seed=21, rise=40, a=1.0)
    if n == 'death':
        if 2 <= i <= 9:
            cx0, cy0 = ctx.anchor('torso', (8, -24))
            for k in range(5):
                a = rng.random() * 6.28
                fx.line((cx0, cy0), (cx0 + math.cos(a) * 18, cy0 + math.sin(a) * 18), 1, (255, 110, 130), 0.8, 'front')
            fx.glow(cx0, cy0, 14, (255, 60, 90), 0.5)
        if i >= 6:
            t = clamp01((i - 6) / 7.0)
            pool(ctx, ax + 8, ay - 1, 14 + 40 * t, 3 + 2 * t, [(60, 6, 24), (130, 14, 40), (190, 26, 56)], 0.95)
            for k in range(3 + int(18 * t)):
                fx.dots([(ax - 20 + k * 4 + 7 * math.sin(i + k), ay - 10 - k * 3 - 22 * t)], (255, 100, 120), 0.9, 'front', 2)
    if n == 'intro':
        intro_fx(ctx)


def intro_fx(ctx):
    i, fx, ax, ay = ctx.i, ctx.fx, ctx.pivot[0], ctx.pivot[1]
    t = i / 13.0
    moon(fx, ax + 40, 38, 24, 0.6 + 0.4 * clamp01(i / 8.0), 'back')
    fogband(ctx, ay - 4, 30, [(130, 50, 80), (90, 28, 60), (50, 14, 40)], t, 4, 0.7, 'back', n=7)
    # prendas del cazador en el suelo, abultandose
    k = clamp01(1 - (i - 4) / 6.0)
    sw = 1 + 0.12 * math.sin(i * 1.7)
    fx.ell(ax + 4, ay - 3, 22 * sw, 6 * sw, (24, 16, 28), 1.0, 'back')
    fx.ell(ax + 2, ay - 6, 15 * sw, 7 * sw, (50, 30, 46), 1.0, 'back')
    fx.ell(ax - 4, ay - 8, 7, 4, (130, 20, 44), 1.0, 'back')
    # sombrero
    hx, hy = ax + 24, ay - 4
    fx.ell(hx, hy, 11, 2.4, (24, 18, 28), 1.0, 'back')
    fx.ell(hx - 1, hy - 3, 5, 3.6, (24, 18, 28), 1.0, 'back')
    fx.poly([(hx - 5, hy - 2), (hx + 4, hy - 2), (hx + 4, hy - 0.6), (hx - 5, hy - 0.6)], (130, 20, 44), 1.0, 'back')
    if i < 8:
        for q in range(6):
            a = q * 1.1 + i * 0.7
            fx.line((ax + 2, ay - 6), (ax + 2 + math.cos(a) * 22 * (1 - k * 0.3), ay - 6 - abs(math.sin(a)) * 40 * (1 - k * 0.2)), 1, (255, 70, 100), 0.5 + 0.4 * (1 - k), 'front')
    if 4 <= i <= 10:
        fx.glow(ax, ay - 20, 30, (255, 30, 60), 0.35, rx=34, ry=26)
        dust(ctx, ax, ay, clamp01((i - 4) / 6.0), (110, 60, 80), 12, 44, 10, a=0.6)
    fogband(ctx, ay - 1, 18, [(150, 60, 90), (90, 26, 60)], t + 0.5, 6, 0.6, 'front', n=7)


def hit_boxes():
    return {
        'attack1': dict(hit=[2, 4], box=[6, -84, 78, 84]),
        'attack2': dict(hit=[1, 5], box=[6, -78, 126, 66]),
        'attack3': dict(hit=[4, 6], box=[-74, -58, 168, 58]),
        'cast': dict(rel=4, muzzle_src=('jaw', (24, 2))),
    }


def spec():
    fns = dict(idle=idle_pose, walk=walk_pose, windup1=wind1, attack1=atk1, windup2=wind2, attack2=atk2, windup3=wind3,
               attack3=atk3, cast=cast, hurt=hurt, phase=phase, intro=intro, death=death)
    hb = hit_boxes()
    return {k: dict(pose=v, **hb.get(k, {})) for k, v in fns.items()}


def build():
    return make(spec(), fxhook)
