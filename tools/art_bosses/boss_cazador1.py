import math
import numpy as np
from kit import *
from shapes import *
from anim import *
from fxlib import *
from boss_common import *

SKIN = auto('#cdc6d8', shadow=(66, 44, 118), warm=(255, 236, 232), n=6, dk=0.3, boost=1.15)
COAT = auto('#2c1e2c', shadow=(10, 6, 40), warm=(160, 96, 130), n=6, dk=0.3)
COATR = auto('#82142a', shadow=(30, 6, 50), warm=(255, 110, 110), n=6, dk=0.26)
HAT = auto('#241a26', shadow=(8, 6, 36), warm=(130, 90, 140), n=6, dk=0.3)
LEATH = auto('#3c2a2a', shadow=(14, 8, 40), warm=(200, 130, 110), n=6, dk=0.3)
STEEL = auto('#7a8098', shadow=(26, 24, 66), warm=(240, 246, 255), n=6, dk=0.24)
BRASS = auto('#b8923c', shadow=(60, 30, 60), warm=(255, 240, 160), n=6)
HAIR = auto('#aaa4b8', shadow=(50, 40, 100), warm=(255, 250, 255), n=6, dk=0.3)
BLOODG = [(60, 6, 20), (150, 16, 44), (232, 44, 76), (255, 150, 150), (255, 240, 236)]
MATS = {'skin': Mat(SKIN, texamt=0.4, gain=1.1), 'coat': Mat(COAT, texamt=0.65, gain=1.0), 'coatr': Mat(COATR, texamt=0.65, gain=0.95),
        'hat': Mat(HAT, texamt=0.6), 'leath': Mat(LEATH, texamt=0.6), 'steel': Mat(STEEL, glow=BLOODG, gain=1.3, texamt=0.45),
        'brass': Mat(BRASS, gain=1.3), 'hair': Mat(HAIR, texamt=0.6), 'eye': Mat(COATR, glow=BLOODG, texamt=0.2),
        'cloth': Mat(auto('#e8e0e4', shadow=(70, 50, 120), warm=(255, 255, 255)), texamt=0.5)}


def build_parts():
    P = []

    def add(*a, **k):
        p = Part(*a, **k); P.append(p); return p
    add('root', None, (96, 156), ghost=True)
    hip = add('hip', 'root', (0, -50), z=4, mat='coat', depth=4.2, noise=0.3, seed=5)
    hip.spl([(-8, -4), (-4, -7), (6, -7), (9, -3), (10, 4), (6, 8), (0, 6), (-6, 8), (-9, 3)])
    hip.poly([(-9, -5), (10, -5), (10, -2), (-9, -2)], mat='leath', raise_=0.8, edge=0.1)
    hip.ell(2.5, -3.5, 2.6, 2.6, mat='brass', raise_=0.8, edge=0.1)
    for nm, x, z, dim in (('b', -3.5, 2, -0.22), ('f', 3.5, 5, 0.0)):
        th = add('thigh_' + nm, 'hip', (x, 3), z=z, mat='coat', depth=3.6, noise=0.2, seed=10, dim=dim, tnoise=0.12)
        th.tube([(0, 0), (1, 11), (1, 22)], 4.6, 3.4)
        th.line([(0.5, 2), (1.2, 20)], 0.7, op='tex', v=0.16)
        sh = add('shin_' + nm, 'thigh_' + nm, (1, 22), z=z, mat='leath', depth=3.2, noise=0.2, seed=11, dim=dim, tnoise=0.12)
        sh.tube([(0, 0), (0, 10), (-0.5, 21)], 3.6, 2.8)
        sh.spl([(-5, -3), (5, -3), (5.6, 3), (-3.8, 3)], mat='leath', raise_=0.9, edge=0.1)
        sh.line([(0, 4), (0, 19)], 0.7, op='tex', v=0.9)
        sh.ell(0.5, 12, 1.1, 1.1, mat='brass', raise_=0.6)
        sh.ell(0.5, 17, 1.1, 1.1, mat='brass', raise_=0.6)
        ft = add('foot_' + nm, 'shin_' + nm, (-0.5, 21), z=z, mat='leath', depth=2.6, noise=0.2, seed=12, dim=dim)
        ft.spl([(-4, -4), (2, -5), (4.5, -1), (10, 1.5), (14, 3.4), (10, 5), (-5, 5)])
        ft.line([(5, 0.8), (10, 3)], 0.6, op='tex', v=0.9)
    # faldones del abrigo
    c1 = add('coat1', 'hip', (-3, -3), z=3.8, mat='coat', depth=4.5, noise=0.4, seed=1)
    c1.spl([(-5, -1), (4, -2), (10, 4), (12, 18), (10, 30), (2, 36), (-8, 32), (-10, 18), (-8, 6)], per=6)
    c1.spl([(2, 0), (8, 2), (11, 14), (10, 30), (5, 33), (5, 18)], mat='coatr', raise_=0.3, edge=0.2)
    c1.hatch(3.0, 84, v=0.3, w=0.5, jit=0.4)
    c1.line([(-2, 0), (-3, 34)], 0.7, op='tex', v=0.14)
    c2 = add('coat2', 'coat1', (-1, 30), z=3.8, mat='coat', depth=3.6, noise=0.4, seed=2)
    c2.poly([(-10, -2), (11, -2), (13, 6)] + rag(13, -12, 12, 5, 8, 3, 1) + [(-11, 5)])
    c2.poly([(0, -1), (12, -1), (13, 6), (4, 12)], mat='coatr', raise_=0.3, edge=0.2)
    c2.hatch(3.0, 84, v=0.3, w=0.5, jit=0.4)
    c3 = add('coat3', 'hip', (-6, 0), z=3.4, mat='coat', depth=3.0, noise=0.4, seed=3)
    c3.poly([(2, -2), (-6, -1), (-12, 10), (-16, 26), (-14, 38), (-9, 34), (-7, 40), (-3, 32), (0, 12)])
    c3.hatch(3.0, 80, v=0.3, w=0.5, jit=0.4)
    sa = add('sash', 'hip', (4, -2), z=6.2, mat='coatr', depth=2.0, noise=0.3, seed=4)
    sa.spl([(-2, 0), (3, 0), (4, 10), (2, 20), (4, 28), (0, 24), (-2, 12)])
    sa.line([(0.5, 2), (1.5, 24)], 0.6, op='tex', v=0.2)
    # torso
    to = add('torso', 'hip', (0, -2), z=6, mat='coat', depth=5.0, noise=0.3, seed=20, tnoise=0.15)
    to.spl([(-6, -1), (-8, -10), (-7.5, -24), (-3, -31), (5, -30), (8.5, -22), (8.5, -10), (6, -1)])
    to.spl([(0, -30), (7, -26), (8, -12), (5, -2), (1, -3), (1.5, -15)], mat='coatr', raise_=0.4, edge=0.2)
    to.poly([(2.5, -28), (7.4, -25), (6.4, -9), (3, -9)], mat='cloth', raise_=0.3)
    for k in range(4):
        to.ell(4.4, -24 + k * 5, 0.8, 0.8, mat='brass', raise_=0.7)
    to.line([(-2, -28), (-3, -2)], 0.7, op='tex', v=0.14)
    to.line([(0, -30), (-1, -10), (3, -2)], 0.7, op='tex', v=0.1)
    to.cracks(2, 6, v=0.14, w=0.5, seed=21)
    co = add('collar', 'torso', (1, -29), z=7, mat='coat', depth=2.4, noise=0.2, seed=24)
    co.poly([(-5, 3), (-6, -4), (-3, -9), (1, -3), (6, -6), (9, 0), (7, 4)])
    co.poly([(1, -3), (6, -6), (9, 0), (5, 1)], mat='coatr', raise_=0.3, edge=0.2)
    hd = add('head', 'torso', (3, -32), z=12, mat='skin', depth=5.4, noise=0.2, seed=30, tnoise=0.1)
    hd.spl([(-5.5, -2), (-6, -9), (-2, -14), (4, -14.5), (8, -10), (9, -5), (9.2, -3), (11, -1.4), (8, -0.4), (7.4, 1.5), (4.5, 3.4), (0, 4), (-4, 3)])
    hd.poly([(2.4, -8.2), (8.4, -8.6), (8, -6.2), (2.8, -5.8)], mat='hat', raise_=-0.3)
    hd.poly([(3.2, -7.8), (7.6, -8), (7.4, -6.6), (3.4, -6.4)], mat='eye')
    hd.poly([(3.2, -7.8), (7.6, -8), (7.4, -6.6), (3.4, -6.4)], op='emit', v=1.0, soft=0.4)
    hd.line([(3, 0.6), (7, 0.4)], 0.7, op='tex', v=0.08)
    hd.line([(-2, -4), (1, 1.8)], 0.7, op='tex', v=0.2)
    hd.line([(3, -9.5), (9, -9.8)], 0.7, op='tex', v=0.1)
    for nm, par, at, sd in (('hair1', 'head', (-3, -10), 36), ('hair2', 'hair1', (-4, 14), 37)):
        h = add(nm, par, at, z=3.6, mat='hair', depth=2.6, noise=0.4, seed=sd, tnoise=0.3)
        if nm == 'hair1':
            h.spl([(4, -3), (-3, -5), (-8, 2), (-10, 14), (-8, 24), (-4, 20), (-1, 10), (3, 2)])
        else:
            h.poly([(3, -3), (-4, -2), (-9, 6), (-10, 16), (-6, 26), (-4, 18), (-2, 28), (0, 12), (2, 2)])
        h.hatch(2.2, 100, v=0.2, w=0.5, jit=0.5)
    ht = add('hat', 'head', (1, -13), z=13, mat='hat', depth=3.4, noise=0.2, seed=33)
    ht.spl([(-19, -3), (-12, 1), (-3, 0), (6, 0), (14, 0), (23, -6), (20, 2), (12, 5), (2, 6), (-9, 6), (-17, 4)], per=5)
    ht.spl([(-7, 0), (-8, -6), (-4, -10), (3, -11), (8, -6), (8, 0)], per=6)
    ht.poly([(-7.4, -2), (8.4, -2), (8.2, 0.8), (-7.6, 0.8)], mat='coatr', raise_=0.6, edge=0.1)
    ht.ell(1, -0.6, 1.6, 1.6, mat='brass', raise_=0.6)
    ht.line([(-15, 3.8), (-3, 0.4), (6, -0.4)], 0.8, op='tex', v=0.9)
    ht.tube([(-5, -9), (-10, -14), (-16, -14), (-19, -8)], 1.4, 0.5, mat='coatr', raise_=0.5)
    for nm, x, z, dim in (('b', -3, 3, -0.22), ('f', 4, 10, 0.0)):
        ua = add('uarm_' + nm, 'torso', (x, -26), z=z, mat='coat', depth=2.8, noise=0.2, seed=40, dim=dim, tnoise=0.1)
        ua.tube([(0, 0), (1, 7), (0.5, 14)], 3.2, 2.7)
        ua.line([(0.2, 1), (0.8, 13)], 0.6, op='tex', v=0.16)
        fa = add('farm_' + nm, 'uarm_' + nm, (0.5, 14), z=z, mat='coat', depth=2.6, noise=0.2, seed=41, dim=dim, tnoise=0.1)
        fa.tube([(0, 0), (0.3, 7), (0.3, 14)], 2.7, 2.2)
        fa.poly([(-3.4, 10), (3.4, 10), (3.8, 15), (-3.4, 15)], mat='coatr', raise_=0.6, edge=0.1)
        hn = add('hand_' + nm, 'farm_' + nm, (0.3, 14), z=z + 0.2, mat='leath', depth=2.0, noise=0.1, seed=42, dim=dim)
        hn.spl([(-2.2, -1), (2.2, -1), (3, 3.5), (1.5, 6.5), (-1.5, 6.5), (-2.6, 3)])
    # sierra-latigo
    sw = add('saw', 'hand_f', (0, 3), z=10.5, mat='steel', depth=2.6, noise=0.3, seed=50)
    sw.poly([(-1.8, -9), (1.8, -9), (2.0, 5), (-2.0, 5)], mat='leath')
    sw.poly([(-2.2, -10), (2.2, -10), (2.2, -7), (-2.2, -7)], mat='brass', raise_=0.7, edge=0.1)
    sw.poly([(-5, 5), (5, 5), (5, 8), (-5, 8)], mat='brass', raise_=0.9, edge=0.1)
    pts = [(-3.6, 8), (3.6, 8), (4.4, 13)]
    # hoja segmentada (cuatro placas) con dientes al frente
    segs = [(8, 19), (20, 31), (32, 43), (44, 52)]
    sw.poly([(-3.8, 8), (3.8, 8), (4.2, 52), (0, 60), (-4.2, 52)])
    for (a0, a1) in segs:
        sw.poly([(-3.4, a0 + 0.8), (3.4, a0 + 0.8), (3.6, a1 - 0.8), (-3.6, a1 - 0.8)], mat='steel', raise_=1.0, edge=0.1)
    sw.line([(0, 9), (0, 54)], 0.8, op='tex', v=0.14)
    for k in range(10):
        yy = 11 + k * 4.6
        sw.poly([(3.6, yy), (8.2, yy + 2.6), (3.6, yy + 4.4)], mat='steel', raise_=0.8, edge=0.1)
    sw.poly([(-1, 12), (1, 12), (1, 48), (-1, 48)], mat='eye')
    sw.line([(0, 14), (0, 46)], 0.9, op='emit', v=0.55, soft=0.5)
    sw.cracks(2, 6, v=0.9, w=0.5, seed=51)
    # pistola
    pi = add('pistol', 'hand_b', (0, 3), z=10.4, mat='brass', depth=2.0, noise=0.2, seed=60)
    pi.poly([(-1.8, -4), (2.0, -4), (2.4, 4), (-1.6, 4)], mat='leath')
    pi.poly([(-2.6, 3), (3, 3), (3, 12), (-2.6, 12)], mat='steel', raise_=0.9, edge=0.1)
    pi.poly([(-1.4, 11), (1.6, 11), (1.4, 30), (-1.2, 30)], mat='steel', raise_=0.9, edge=0.1)
    pi.poly([(-2, 28), (2.4, 28), (2.2, 31), (-1.8, 31)], mat='brass', raise_=0.7, edge=0.1)
    pi.ell(0.2, 8, 1.2, 1.2, mat='eye'); pi.ell(0.2, 8, 0.9, 0.9, op='emit', v=1.0, soft=0.2)
    pi.poly([(-2.2, 2), (-3.8, -1), (-1.6, 0.5)], mat='steel')
    return P


H = make_H(wp='saw')
B = make_H('torso', 'uarm_b', 'farm_b', 'pistol')


def post(boss, pose):
    return pose


def make(anims, fxhook):
    return Boss('cazador1', (192, 160), (96, 156), (26, 104), build_parts(), MATS, anims, fxhook,
                outline=(10, 6, 18), rim=(255, 90, 120), rimk=0.4, dis_col=(230, 40, 70), seed=51, post=post, scale=1.2)


# ====================================================================== animaciones
def L(thf, shf, thb, shb, ff=None, fb=None):
    return {'thigh_f': thf, 'shin_f': shf, 'foot_f': -(thf + shf) * 0.9 if ff is None else ff,
            'thigh_b': thb, 'shin_b': shb, 'foot_b': -(thb + shb) * 0.9 if fb is None else fb}


def PZ(*ds):
    return merge(*ds)


def PIS(t, u, f, w):
    d = B(t, u, f, w)
    d.pop('torso')
    return d


def coat(f, n, amp=1.0, base=0.0, ph=0.0):
    return {'coat1': base * 0.5 + amp * 2.6 * S(f, n, ph), 'coat2': base + amp * 4.2 * S(f, n, ph + 0.12), 'coat3': base * 0.8 + amp * 3.4 * S(f, n, ph + 0.2),
            'sash': base * 0.8 + amp * 4 * S(f, n, ph + 0.3), 'hair1': base * 0.5 + amp * 2.6 * S(f, n, ph + 0.25), 'hair2': amp * 4 * S(f, n, ph + 0.4)}


STAND = PZ(L(-6, 9, 8, -7), H(2, -12, -22, -12), PIS(2, 8, -20, 30), {'head': -1})


def idle_pose(f):
    b = S(f, 6)
    return PZ(STAND, {'root.y': -0.8 * b, 'torso': 1.2 * b, 'head': -1.4 * b, 'uarm_f': -0.8 * b, 'saw': 1.0 * S(f, 6, 0.1), 'hat': 0.6 * b}, coat(f, 6, 1.0, 1.5))


def walk_pose(f):
    ph = 2 * math.pi * f / 8
    s = math.sin(ph); c = math.cos(ph)
    thf = 22 * s - 6; thb = -22 * s + 6
    shf = 12 + 26 * max(0, -c * 0.9 + 0.1) * (1 if s < 0.3 else 0.3) + 6 * max(0, c)
    shb = 12 + 26 * max(0, c * 0.9 + 0.1) * (1 if s > -0.3 else 0.3) + 6 * max(0, -c)
    return PZ(L(thf, shf * 0.8, thb, shb * 0.8), H(5, -14 + 8 * s, -24, -14 + 4 * s), PIS(5, 10 - 8 * s, -20, 30),
              {'root.y': -2.0 * abs(c) + 1, 'head': -2 + 2 * c, 'torso': 1.5 * c, 'hip': 1.5 * s}, coat(f, 8, 1.6, 7))


WIND1 = [(0, STAND),
         (1, PZ(L(-10, 14, 10, -8), H(-2, -60, -50, -80), PIS(-2, 14, -20, 30), {'root.y': 1})),
         (2, PZ(L(-12, 16, 12, -8), H(-6, -90, -54, -170), PIS(-6, 18, -22, 34), {'root.y': 1.5, 'head': -6})),
         (3, PZ(L(-14, 18, 13, -8), H(-9, -100, -52, -222), PIS(-9, 20, -22, 36), {'root.y': 2, 'head': -9})),
         (4, PZ(L(-14, 18, 13, -8), H(-11, -104, -50, -240), PIS(-11, 22, -22, 38), {'root.y': 2.5, 'head': -10, 'root.x': -2}))]
wind1k = K(WIND1)


def wind1(f):
    return PZ(wind1k(f), coat(f, 5, 0.6, 3 + f))


ATK1 = [(0, WIND1[-1][1], 'sm'),
        (1, PZ(L(-20, 24, 12, -8), H(2, -100, -48, -170), PIS(2, 10, -20, 30), {'root.y': 2, 'root.x': 3, 'head': 0}), 'snap'),
        (2, PZ(L(-24, 28, 15, -8), H(12, -82, -46, -100), PIS(12, 8, -20, 30), {'root.y': 2.5, 'root.x': 6, 'head': 4}), 'snap'),
        (3, PZ(L(-26, 32, 16, -8), H(18, -64, -44, -34), PIS(18, 8, -20, 30), {'root.y': 3, 'root.x': 8, 'head': 5}), 'snap'),
        (4, PZ(L(-26, 32, 16, -8), H(18, -58, -44, -26), PIS(18, 8, -20, 30), {'root.y': 3, 'root.x': 8, 'head': 5}), 'out'),
        (5, PZ(L(-22, 28, 15, -8), H(14, -50, -44, -22), PIS(14, 8, -20, 30), {'root.y': 2.5, 'root.x': 6, 'head': 3}), 'sm'),
        (6, PZ(L(-14, 20, 12, -8), H(8, -40, -40, -14), PIS(8, 8, -20, 30), {'root.y': 1.5, 'root.x': 3}), 'sm'),
        (7, STAND, 'sm')]
atk1k = K(ATK1)


def atk1(f):
    return PZ(atk1k(f), coat(f, 8, 1.4, 8 - f * 0.5, 0.2))


WIND2 = [(0, STAND),
         (1, PZ(L(-10, 16, 11, -8), H(0, -20, -60, 60), PIS(0, 10, -20, 30), {'root.y': 1})),
         (2, PZ(L(-12, 22, 13, -12), H(-6, 14, -70, 80), PIS(-6, 12, -20, 30), {'root.y': 2.5, 'head': -4})),
         (3, PZ(L(-14, 28, 15, -16), H(-12, 30, -80, 90), PIS(-12, 14, -20, 30), {'root.y': 3.5, 'root.x': -4, 'head': -7})),
         (4, PZ(L(-14, 28, 15, -16), H(-14, 36, -84, 92), PIS(-14, 14, -20, 30), {'root.y': 4, 'root.x': -6, 'head': -8}))]
wind2k = K(WIND2)


def wind2(f):
    return PZ(wind2k(f), coat(f, 5, 0.5, -2 - f * 2, 0.3))


ATK2 = [(0, WIND2[-1][1], 'sm'),
        (1, PZ(L(-30, 24, 24, -14), H(14, -62, -40, -84), PIS(14, 20, -20, 30), {'root.y': 2, 'root.x': 2, 'head': 4}), 'snap'),
        (2, PZ(L(-36, 22, 28, -12), H(20, -82, -14, -90), PIS(20, 24, -20, 30), {'root.y': 1, 'root.x': 3, 'head': 6}), 'snap'),
        (3, PZ(L(-36, 22, 28, -12), H(22, -86, -8, -92), PIS(22, 26, -20, 30), {'root.y': 1, 'root.x': 4, 'head': 7}), 'out'),
        (4, PZ(L(-34, 22, 26, -12), H(21, -84, -10, -92), PIS(21, 26, -20, 30), {'root.y': 1, 'root.x': 4, 'head': 7}), 'sm'),
        (5, PZ(L(-30, 22, 22, -12), H(18, -78, -18, -88), PIS(18, 24, -20, 30), {'root.y': 1.5, 'root.x': 3, 'head': 5}), 'sm'),
        (6, PZ(L(-18, 18, 14, -10), H(10, -52, -40, -40), PIS(10, 14, -20, 30), {'root.y': 1.5, 'root.x': 1}), 'sm'),
        (7, STAND, 'sm')]
atk2k = K(ATK2)


def atk2(f):
    return PZ(atk2k(f), coat(f, 8, 1.6, -14 + f * 1.5, 0.0))


WIND3 = [(0, STAND),
         (1, PZ(L(-26, 52, 24, -34), H(8, -60, -60, -50), PIS(8, 20, -40, 30), {'root.y': 3.5, 'head': -2})),
         (2, PZ(L(-30, 62, 28, -42), H(0, -86, -50, -160), PIS(0, 30, -40, 30), {'root.y': 5, 'head': -6})),
         (3, PZ(L(-32, 66, 30, -46), H(-6, -100, -44, -230), PIS(-6, 40, -40, 30), {'root.y': 6.5, 'head': -10})),
         (4, PZ(L(-34, 70, 32, -50), H(-10, -104, -42, -250), PIS(-10, 50, -40, 30), {'root.y': 7.5, 'head': -12})),
         (5, PZ(L(-34, 70, 32, -50), H(-12, -106, -42, -254), PIS(-12, 54, -40, 30), {'root.y': 8, 'head': -13}))]
wind3k = K(WIND3)


def wind3(f):
    return PZ(wind3k(f), coat(f, 6, 0.5, 4 + f, 0.3))


ATK3 = [(0, WIND3[-1][1], 'sm'),
        (1, PZ(L(-6, 8, 6, -4), H(-4, -106, -42, -250), PIS(-4, 40, -40, 30), {'root.y': -20, 'head': -8}), 'out'),
        (2, PZ(L(-12, 26, 12, -20), H(2, -106, -42, -246), PIS(2, 30, -40, 30), {'root.y': -28, 'head': -4}), 'sm'),
        (3, PZ(L(-18, 28, 14, -26), H(12, -94, -44, -150), PIS(12, 20, -30, 30), {'root.y': -14, 'head': 4}), 'in'),
        (4, PZ(L(-30, 48, 24, -34), H(22, -62, -52, -18), PIS(22, 10, -20, 30), {'root.y': 5, 'root.x': 4, 'head': 6}), 'snap'),
        (5, PZ(L(-32, 52, 26, -38), H(24, -60, -54, -8), PIS(24, 10, -20, 30), {'root.y': 6, 'root.x': 4, 'head': 7}), 'sm'),
        (6, PZ(L(-30, 48, 22, -34), H(20, -58, -54, -8), PIS(20, 10, -20, 30), {'root.y': 5, 'root.x': 4, 'head': 6}), 'sm'),
        (7, PZ(L(-18, 28, 14, -18), H(10, -48, -48, -12), PIS(10, 8, -20, 30), {'root.y': 3, 'root.x': 2}), 'sm'),
        (8, STAND, 'sm')]
atk3k = K(ATK3)


def atk3(f):
    return PZ(atk3k(f), coat(f, 9, 1.8, -10 if f in (1, 2, 3) else 6, 0.0))


CAST = K([(0, STAND),
          (1, PZ(L(-10, 14, 11, -8), H(-2, -20, -40, -20), PIS(-2, -50, -40, -70), {'root.y': 1, 'head': -2})),
          (2, PZ(L(-12, 16, 12, -8), H(-4, -20, -40, -20), PIS(-4, -80, -20, -90), {'root.y': 1.5, 'head': -4}), 'sm'),
          (3, PZ(L(-12, 16, 12, -8), H(-5, -20, -40, -20), PIS(-5, -92, -4, -92), {'root.y': 1, 'head': -6}), 'sm'),
          (4, PZ(L(-14, 18, 14, -8), H(2, -20, -40, -20), PIS(2, -96, -2, -108), {'root.y': 2, 'root.x': -3, 'head': -2}), 'snap'),
          (5, PZ(L(-14, 18, 14, -8), H(2, -20, -40, -20), PIS(2, -96, -4, -112), {'root.y': 2, 'root.x': -3}), 'out'),
          (6, PZ(L(-12, 16, 12, -8), H(4, -16, -30, -16), PIS(4, -60, -30, -50), {'root.y': 1}), 'sm'),
          (7, STAND, 'sm')])


def cast(f):
    return PZ(CAST(f), coat(f, 8, 1.4, 4, 0.0))


def hurt(f):
    d = [PZ(L(-6, 14, 12, -6), H(-12, -20, -30, -6), PIS(-12, 20, -10, 20), {'head': -12, 'root.x': -3, 'root.y': 1, 'tint': ((255, 255, 255), 0.5)}),
         PZ(L(-8, 14, 11, -6), H(-6, -16, -26, -8), PIS(-6, 12, -14, 24), {'head': -6, 'root.x': -2, 'tint': ((255, 255, 255), 0.2)})][int(f)]
    return PZ(d, coat(f, 2, 1, 6 + 4 * (1 - f)))


PHASE = K([(0, STAND),
           (1, PZ(L(-16, 30, 16, -20), H(8, -20, -30, -10), PIS(8, 10, -20, 20), {'root.y': 3, 'head': 8}), 'sm'),
           (2, PZ(L(-22, 44, 22, -30), H(14, -14, -26, -6), PIS(14, 16, -20, 20), {'root.y': 6, 'head': 12}), 'sm'),
           (3, PZ(L(-14, 22, 16, -14), H(6, -30, -30, -10), PIS(6, -60, -30, 0), {'root.y': 1, 'head': -2}), 'out'),
           (4, PZ(L(-8, 8, 10, -4), H(-10, -110, -20, -170), PIS(-10, -150, -20, -180), {'root.y': -5, 'head': -26, 'torso.sy': 1.04}), 'snap'),
           (5, PZ(L(-8, 8, 10, -4), H(-12, -116, -20, -176), PIS(-12, -156, -16, -184), {'root.y': -6, 'head': -30, 'torso.sy': 1.05}), 'sm'),
           (6, PZ(L(-8, 8, 10, -4), H(-12, -116, -20, -176), PIS(-12, -156, -16, -184), {'root.y': -5.5, 'head': -28}), 'sm'),
           (7, PZ(L(-14, 18, 12, -10), H(0, -80, -26, -120), PIS(0, -100, -24, -130), {'root.y': -1, 'head': -10}), 'in'),
           (8, PZ(L(-12, 16, 11, -9), H(2, -30, -24, -20), PIS(2, -20, -22, 0), {'root.y': 1, 'head': 2}), 'snap'),
           (9, STAND, 'sm')])


def phase(f):
    p = PHASE(f)
    if 4 <= f <= 7:
        p['tint'] = ((255, 90, 120), 0.25 * (1 - abs(f - 5.5) / 2.0))
    p['root.x'] = p.get('root.x', 0) + (1.0 if (f in (5, 6) and int(f) % 2) else (-1.0 if f in (5, 6) else 0))
    p['hat.y'] = -4 * clamp01((f - 5) / 3.0) if 5 <= f <= 8 else 0
    return PZ(p, coat(f, 10, 2.4, -8 if 3 <= f <= 7 else 4, 0.0))


def intro(f):
    i = int(f)
    d = clamp01((i - 2) / 7.0)
    lit = clamp01((i - 9) / 4.0)
    walkx = -14 * (1 - clamp01((i - 4) / 7.0))
    s = math.sin(f * 1.1); c = math.cos(f * 1.1)
    moving = 1 if 4 <= i <= 10 else 0
    thf = (18 * s - 6) * moving + -6 * (1 - moving); thb = (-18 * s + 6) * moving + 8 * (1 - moving)
    p = PZ(L(thf, (12 + 14 * max(0, -c)) * moving + 9 * (1 - moving), thb, (12 + 14 * max(0, c)) * moving - 7 * (1 - moving)),
           H(2 + 2 * moving, -12, -22, -12), PIS(2, 8, -20, 30), {'root.x': walkx, 'root.y': -1.5 * abs(c) * moving, 'head': -4 * (1 - lit)},
           coat(f, 14, 1.8, 8 if moving else 2))
    p['dis'] = max(0.0, (1 - d) * 1.12) if i >= 2 else 1.2
    p['dis_dir'] = -1.0
    if i < 2:
        p['clip'] = (0, 0, 0, 0)
    return p


DEATH = K([(0, PZ(L(-6, 14, 12, -6), H(-12, -20, -30, -6), PIS(-12, 20, -10, 20), {'head': -12, 'root.x': -3, 'tint': ((255, 255, 255), 0.5)}), 'out'),
           (1, PZ(L(-4, 18, 14, -8), H(-8, -24, -30, 0), PIS(-8, 30, -20, 20), {'head': -8, 'root.x': -5, 'tint': ((255, 255, 255), 0.2)}), 'sm'),
           (2, PZ(L(-6, 26, 16, -16), H(2, -8, -20, 20), PIS(2, 20, -10, 40), {'head': 4, 'root.x': -4, 'root.y': 3, 'tint': ((255, 255, 255), 0.0)}), 'sm'),
           (3, PZ(L(-20, 56, 20, -50), H(8, 4, -12, 40), PIS(8, 10, -10, 60), {'head': 12, 'root.x': -2, 'root.y': 10}), 'sm'),
           (4, PZ(L(-40, 100, 26, -92), H(14, 14, -6, 60), PIS(14, 14, -6, 70), {'head': 20, 'root.y': 20}), 'sm'),
           (5, PZ(L(-50, 120, 30, -110), H(20, 24, 0, 70), PIS(20, 24, 0, 80), {'head': 28, 'root.y': 26, 'root.x': 2}), 'sm'),
           (6, PZ(L(-60, 130, 32, -120), H(30, 30, 6, 80), PIS(30, 30, 6, 90), {'head': 32, 'root.y': 29, 'root.x': 6, 'torso': 30}), 'sm'),
           (7, PZ(L(-60, 130, 32, -120), H(40, 40, 8, 90), PIS(40, 40, 8, 100), {'head': 36, 'root.y': 31, 'root.x': 10, 'torso': 50}), 'in'),
           (13, PZ(L(-60, 130, 32, -120), H(48, 44, 8, 100), PIS(48, 44, 8, 110), {'head': 38, 'root.y': 33, 'root.x': 12, 'torso': 58}), 'lin')])


def death(f):
    p = DEATH(f)
    d = clamp01((f - 6.5) / 5.5)
    if d > 0:
        p['dis'] = d * 1.12
        p['dis_dir'] = 1.0
    c = clamp01((f - 3.0) / 4.0)
    p['hat.y'] = 0 if f < 3 else 12 * c * c * 4
    p['hat.x'] = 0 if f < 3 else 8 * c
    p['hat'] = 50 * c
    p.update(coat(f, 14, 0.5, 6 + f * 2))
    return p


# ====================================================================== efectos
def moon(fx, x, y, r, a=1.0, layer='back'):
    fx.glow(x, y, r * 1.8, (230, 20, 50), 0.45 * a)
    fx.ell(x, y, r + 1.5, r + 1.5, (90, 10, 30), a, layer)
    fx.ell(x, y, r, r, (196, 28, 52), a, layer)
    fx.ell(x - r * 0.15, y - r * 0.15, r * 0.8, r * 0.8, (226, 60, 70), a, layer)
    fx.ell(x - r * 0.3, y - r * 0.3, r * 0.4, r * 0.4, (240, 100, 100), a * 0.8, layer)
    for (cx_, cy_, rr) in ((0.3, 0.2, 0.18), (-0.1, 0.45, 0.14), (0.45, -0.25, 0.1)):
        fx.ell(x + r * cx_, y + r * cy_, r * rr, r * rr, (150, 18, 42), a * 0.9, layer)


def whip(ctx, p0, ext, t, amp=7.0, n=14, seg=7.5, hi=(235, 240, 255)):
    pts = []
    for k in range(n + 1):
        u = k / n
        if u > ext:
            break
        x = p0[0] + k * seg
        y = p0[1] + math.sin(u * 7.0 - t * 5.0) * amp * u * (1 - 0.3 * ext)
        pts.append((x, y))
    return pts


def fxhook(ctx):
    n, i, fx, W = ctx.name, ctx.i, ctx.fx, ctx.W
    ax, ay = ctx.pivot
    rng = ctx.rng
    sawtip = lambda f=None: ctx.anchor('saw', (2, 56)) if f is None else ctx.anchor_at(f, 'saw', (2, 56))
    ex, ey = ctx.anchor('head', (5.6, -7))
    if n != 'death' or i < 6:
        fx.glow(ex, ey, 6, (255, 40, 70), 0.55)
    if n not in ('intro', 'death'):
        fx.glow(*ctx.anchor('saw', (0, 30)), 14, (230, 30, 60), 0.18)
    if n == 'windup1':
        t = i / 4.0
        tx, ty = sawtip()
        fx.glow(tx, ty, 8 + 12 * t, (255, 50, 80), 0.4 * t + 0.1)
        wisps(ctx, tx, ty + 6, 14, 14, 6, [(255, 150, 160), (255, 235, 235)], t=t * 0.9, seed=8, rise=8)
    if n == 'attack1':
        trail(ctx, 'saw', (3, 58), (3, 24), 0, 4, (255, 240, 240), (170, 20, 50), steps=12, span=3.0, mid=(240, 70, 90), a=0.8)
        if 3 <= i <= 6:
            tx, ty = ctx.anchor_at(3.6, 'saw', (2, 50))
            tt = (i - 3) / 3.0
            gx = min(tx, W - 6)
            dust(ctx, gx, ay, tt, (130, 100, 110), 9, 22, 8)
            shock(ctx, gx, ay, tt, (255, 120, 140), 28, 4)
            fx.glow(gx, ay - 4, 12 * (1 - tt * 0.5), (255, 80, 110), 0.8 * (1 - tt))
            if i == 3:
                fx.sparks(rng, gx, ay - 3, 12, 14, [(255, 255, 255), (255, 90, 110)], 'front', 6)
    if n == 'windup2':
        t = i / 4.0
        tx, ty = sawtip()
        fx.glow(tx, ty, 8 + 12 * t, (255, 50, 80), 0.4 * t + 0.1)
        for k in range(4):
            fx.line((tx + 10 + k * 5, ty + (k - 1.5) * 2), (tx + 2, ty + (k - 1.5) * 1.5), 1, (255, 170, 190), 0.5 * t, 'front', mode='add')
    if n == 'attack2' and 1 <= i <= 6:
        tx, ty = sawtip()
        ext = clamp01(i / 3.0) * (1 - 0.5 * clamp01((i - 4) / 3.0))
        pts = whip(ctx, (tx - 2, ty), ext, i * 0.35, 6.0, 14, min(8.0, (W - 4 - tx) / 13.0))
        if len(pts) > 1:
            link_chain(ctx, pts, 3.4, a=1.0 - 0.3 * clamp01((i - 4) / 3.0))
            ex_, ey_ = pts[-1]
            if i in (3, 4):
                fx.glow(ex_, ey_, 12, (255, 200, 210), 0.9)
                impact_star(ctx, ex_, ey_, (i - 3) / 2.0, (255, 220, 230), 12, 8)
            fx.polyline([(tx, ty - 3), (tx + (pts[-1][0] - tx) * 0.5, ty - 6), pts[-1]], 1, (255, 90, 120), 0.5, 'front')
        for k in range(4):
            yy = ay - 20 - k * 14
            x0 = ax + 8 - ((i * 7 + k * 13) % 14)
            fx.line((x0, yy), (x0 - 10 - 2 * k, yy), 1, (255, 150, 170), 0.4, 'front', mode='add')
    if n == 'windup3':
        t = i / 5.0
        tx, ty = sawtip()
        fx.glow(tx, ty, 10 + 14 * t, (255, 50, 80), 0.5 * t + 0.1)
        wisps(ctx, ax, ay - 3, 36, 6, 8, [(255, 90, 110)], t=t, seed=5, rise=26, a=0.7)
        rays(ctx, ax, ay - 2, t * 0.6, (230, 30, 60), 6, 6, 26, 0.18, 0.4 * t, 0.4, 'back')
    if n == 'attack3':
        tx, ty = sawtip()
        if 1 <= i <= 4:
            trail(ctx, 'saw', (3, 58), (3, 24), 2, 4, (255, 240, 240), (170, 20, 50), steps=12, span=2.6, mid=(240, 70, 90), a=0.8)
        if 4 <= i <= 8:
            t = (i - 4) / 4.0
            gx = max(ax + 24, min(tx, W - 10))
            ground_cracks(ctx, gx, ay + 1, t, (30, 6, 20), (255, 70, 100), 8, 56, 11)
            shock(ctx, gx, ay, t, (255, 120, 140), 64, 7, 2)
            dust(ctx, gx, ay, t, (130, 100, 110), 14, 40, 14, 3.0)
            if i <= 6:
                fx.glow(gx, ay - 6, 20 * (1 - t * 0.5), (255, 80, 110), 0.8 * (1 - t))
                for k in range(5):
                    px = gx - 28 + k * 14 + (k % 2) * 2
                    h = (34 + 12 * (k % 3)) * (1 - t * 0.6)
                    fx.poly([(px - 3, ay), (px + 1, ay - h), (px + 3, ay)], (220, 30, 64), 0.85, 'front', ss=2)
                    fx.poly([(px - 1, ay), (px + 1, ay - h * 0.9), (px + 1.4, ay)], (255, 180, 190), 0.9, 'front', ss=2)
    if n == 'cast':
        px, py = ctx.anchor('pistol', (0.5, 31))
        if 1 <= i <= 3:
            t = i / 3.0
            fx.glow(px, py, 6 + 6 * t, (255, 60, 90), 0.5 * t)
        if i == 4:
            fx.glow(px, py, 14, (255, 200, 200), 1.0)
            for k in range(7):
                a = -0.6 + 1.2 * k / 6
                fx.line((px, py), (px + math.cos(a) * 16, py + math.sin(a) * 12), 1 + (k % 2), (255, 230, 210), 0.9, 'front')
            fx.ell(px + 4, py, 6, 3, (255, 255, 240), 1.0, 'front')
        if i >= 4:
            tt = (i - 4) / 3.0
            for k in range(3):
                sx_ = px + 6 + tt * (44 + k * 14)
                sy_ = py + (k - 1) * 9 * tt + 1
                if sx_ < W - 4:
                    fx.glow(sx_, sy_, 8, (255, 40, 80), 0.85)
                    fx.ell(sx_, sy_, 3.4, 3.4, (170, 14, 48), 1.0, 'front')
                    fx.ell(sx_ - 0.6, sy_ - 0.6, 1.8, 1.8, (255, 160, 170), 1.0, 'front')
                    fx.polyline([(sx_ - 3, sy_), (sx_ - 12, sy_), (sx_ - 22, sy_)], 2, (230, 30, 64), 0.5, 'front')
    if n == 'phase':
        t = clamp01((i - 3) / 5.0)
        mx, my = ax + 4, 40
        if 3 <= i <= 9:
            moon(fx, mx, my, 12 + 22 * t, 0.9 * clamp01(1.0 - abs(t - 0.6) * 0.4), 'back')
            fx.glow(ax, ay - 56, 60 * t + 12, (255, 30, 70), 0.5 * (1 - abs(t - 0.5) * 1.2), rx=48 * t + 14, ry=64 * t + 14)
            rays(ctx, ax, ay - 62, t, (255, 70, 100), 16, 14, 84, 0.1, 0.5, i * 0.1, 'back')
            shock(ctx, ax, ay, clamp01((i - 4) / 5.0), (255, 90, 120), 58, 7, 2)
        if 4 <= i <= 8:
            wisps(ctx, ax, ay - 56, 52, 80, 16, [(255, 100, 130), (255, 235, 235)], t=(i - 4) / 6.0, seed=21, rise=40, a=1.0)
    if n == 'death':
        if 3 <= i <= 9:
            hx_, hy_ = ctx.anchor('torso', (2, -18))
            for k in range(5):
                a = -1.2 + 2.4 * rng.random()
                fx.ell(hx_ + 6 + 12 * rng.random(), hy_ + 24 * (rng.random() - 0.3), 1.4, 2.6, (200, 20, 50), 0.9, 'front')
        if i >= 7:
            t = clamp01((i - 7) / 6.0)
            pool(ctx, ax + 6, ay - 1, 10 + 34 * t, 3 + 2 * t, [(60, 6, 24), (130, 14, 40), (190, 26, 56)], 0.95)
            pile(ctx, ax + 4, ay, 36, 5, [(30, 22, 34), (60, 40, 56), (110, 20, 40)], 10 + int(10 * t), seed=4)
            for k in range(2 + int(10 * t)):
                fx.dots([(ax - 14 + k * 5 + 6 * math.sin(i + k), ay - 8 - k * 5 - 16 * t)], (255, 90, 120), 0.9, 'front', 2)
        if i >= 5:
            hx0 = ax + 26; hy0 = ay - 1
            fx.ell(hx0, hy0 - 2, 11, 2.4, (24, 18, 28), 1.0, 'back')
            fx.ell(hx0 - 1, hy0 - 5, 5, 4, (24, 18, 28), 1.0, 'back')
            fx.poly([(hx0 - 5, hy0 - 3), (hx0 + 5, hy0 - 3), (hx0 + 5, hy0 - 1.6), (hx0 - 5, hy0 - 1.6)], (130, 20, 44), 1.0, 'back')
    if n == 'intro':
        intro_fx(ctx)


def intro_fx(ctx):
    i, fx, ax, ay = ctx.i, ctx.fx, ctx.pivot[0], ctx.pivot[1]
    t = i / 13.0
    mf = 1.0 if i < 9 else max(0.0, 1 - (i - 8) / 5.0)
    moon(fx, ax + 36, 40, 26, 0.9 * mf + 0.1, 'back')
    fogband(ctx, ay - 4, 34, [(150, 70, 90), (110, 40, 70), (60, 20, 50)], t, 1, 0.75 * (1 - 0.5 * clamp01((i - 8) / 5.0)), 'back', n=7)
    fogband(ctx, ay - 12, 30, [(190, 100, 120), (130, 50, 80)], t + 0.3, 2, 0.5 * mf, 'back', n=6, amp=5)
    fogband(ctx, ay - 2, 22, [(170, 80, 100), (100, 30, 60)], t + 0.6, 3, 0.7, 'front', n=7)
    if 2 <= i <= 5:
        ex, ey = ax - 14 + 4 * (i - 2), ay - 84 + 1
        a = clamp01((i - 1) / 2.0)
        fx.glow(ex, ey, 6, (255, 40, 70), 0.9 * a)
        fx.glow(ex + 6, ey - 0.5, 6, (255, 40, 70), 0.9 * a)
        fx.dots([(ex, ey), (ex + 6, ey - 0.5)], (255, 220, 220), a, 'front')
    for k in range(8):
        px = ax - 60 + k * 17 + 4 * math.sin(i * 0.5 + k)
        py = ay - 8 - (k % 3) * 8 - 20 * mf * (k % 2)
        fx.glow(px, py, 12, (200, 60, 90), 0.2 * mf)


def hit_boxes():
    return {
        'attack1': dict(hit=[2, 4], box=[4, -76, 62, 76]),
        'attack2': dict(hit=[1, 5], box=[6, -62, 118, 46]),
        'attack3': dict(hit=[4, 6], box=[-66, -50, 140, 50]),
        'cast': dict(rel=4, muzzle_src=('pistol', (0.5, 31))),
    }


def spec():
    fns = dict(idle=idle_pose, walk=walk_pose, windup1=wind1, attack1=atk1, windup2=wind2, attack2=atk2, windup3=wind3,
               attack3=atk3, cast=cast, hurt=hurt, phase=phase, intro=intro, death=death)
    hb = hit_boxes()
    return {k: dict(pose=v, **hb.get(k, {})) for k, v in fns.items()}


def build():
    return make(spec(), fxhook)
