import math
import numpy as np
from kit import *
from shapes import *
from anim import *
from fxlib import *
from boss_common import *

STEEL = auto('#36343f', shadow=(12, 10, 46), warm=(176, 166, 214), n=6, dk=0.24)
GOLD = auto('#c8a03a', shadow=(66, 30, 62), warm=(255, 246, 172), n=6)
GOLDD = auto('#7a5a22', shadow=(40, 20, 50), warm=(230, 190, 100), n=6)
CLOTH = auto('#3a2f2c', shadow=(16, 10, 42), warm=(200, 160, 110), n=6, dk=0.3)
CLOTHG = auto('#7c5e26', shadow=(36, 18, 48), warm=(240, 200, 120), n=6, dk=0.3)
VOID = ramp((4, 4, 12), (12, 10, 22), (36, 30, 52), 6)
SUNG = [(70, 44, 8), (170, 120, 24), (242, 196, 64), (255, 242, 176), (255, 253, 235)]
MATS = {'steel': Mat(STEEL, gain=1.25, texamt=0.5), 'gold': Mat(GOLD, gain=1.3, texamt=0.4), 'goldd': Mat(GOLDD, gain=1.1),
        'cloth': Mat(CLOTH, gain=0.9, texamt=0.7), 'clothg': Mat(CLOTHG, gain=0.9, texamt=0.7), 'void': Mat(VOID, gain=0.5),
        'sun': Mat(GOLD, glow=SUNG, texamt=0.2), 'steelg': Mat(STEEL, glow=SUNG, gain=1.25, texamt=0.5)}
SUNC = (255, 214, 96)


def trim(p, pts, w=0.8):
    p.line(pts, w, op='tex', v=0.96)


def build_parts():
    P = []

    def add(*a, **k):
        p = Part(*a, **k); P.append(p); return p
    add('root', None, (96, 156), ghost=True)
    hip = add('hip', 'root', (0, -48), z=4, mat='steel', depth=4.8, noise=0.4, seed=5)
    hip.spl([(-10, -4), (-5, -7), (7, -7), (11, -3), (13, 4), (8, 9), (2, 7), (-2, 10), (-8, 8), (-12, 3)])
    hip.poly([(-11, -5), (12, -5), (12, -1), (-11, -1)], mat='gold', raise_=0.9, edge=0.1)
    hip.ell(2.5, -3, 3.6, 3.6, mat='gold', raise_=1.0, edge=0.1)
    hip.ell(2.5, -3, 1.6, 1.6, mat='sun'); hip.ell(2.5, -3, 1.2, 1.2, op='emit', v=1.0, soft=0.3)
    ts = add('tasset', 'hip', (1, 4), z=5.5, mat='steel', depth=3.4, noise=0.4, seed=8)
    ts.poly([(-9, 0), (11, 0), (12, 12), (6, 18), (0, 13), (-6, 18), (-10, 12)])
    ts.poly([(-10, 11), (12, 11), (6, 18), (0, 13), (-6, 18)], mat='gold', raise_=0.7, edge=0.1)
    ts.line([(0, 0), (0, 12)], 0.7, op='tex', v=0.1)
    for nm, x, z, dim in (('b', -4, 2, -0.22), ('f', 4, 5, 0.0)):
        th = add('thigh_' + nm, 'hip', (x, 3), z=z, mat='steel', depth=4.2, noise=0.3, seed=10, dim=dim, tnoise=0.15)
        th.tube([(0, 0), (1, 10), (1, 20)], 5.4, 4.2)
        th.spl([(-5.2, 0), (5.8, 0), (5.8, 14), (-4.6, 14)], mat='steel', raise_=1.1, edge=0.1)
        th.line([(-5, 1), (6, 1)], 0.8, op='tex', v=0.95)
        th.ell(1, 20, 5.6, 4.8, mat='gold', raise_=1.6, edge=0.1)
        th.ell(1.5, 20, 1.3, 1.3, mat='steel')
        sh = add('shin_' + nm, 'thigh_' + nm, (1, 20), z=z, mat='steel', depth=3.6, noise=0.3, seed=11, dim=dim, tnoise=0.15)
        sh.tube([(0, 0), (0, 9), (-0.5, 18)], 4.4, 3.2)
        sh.spl([(-4.4, 3), (4.8, 3), (4.0, 16), (-3.2, 16)], mat='steel', raise_=1.1, edge=0.1)
        sh.line([(0.4, 4), (0.2, 14)], 0.8, op='tex', v=0.95)
        sh.line([(-4, 15), (4, 15)], 0.8, op='tex', v=0.95)
        ft = add('foot_' + nm, 'shin_' + nm, (-0.5, 18), z=z, mat='steel', depth=3.0, noise=0.3, seed=12, dim=dim)
        ft.spl([(-5, -4), (2, -5), (5.5, -1), (11, 1.5), (15, 3.6), (11, 5.4), (-5.5, 5.4)])
        ft.line([(6, 0.8), (11, 3.4)], 0.7, op='tex', v=0.95)
    to = add('torso', 'hip', (0, -2), z=6, mat='steel', depth=6.5, noise=0.4, seed=20, tnoise=0.15)
    to.spl([(-8, -2), (-11, -12), (-10.5, -24), (-5, -31), (6, -30), (12, -22), (13, -10), (9, -2), (-3, -1)])
    to.ell(4, -17, 6.2, 6.2, mat='gold', raise_=1.1, edge=0.1)
    to.ell(4, -17, 4.6, 4.6, mat='void', raise_=-0.2)
    to.ell(4, -17, 5.4, 5.4, op='emit', v=0.0)
    to.ell(3.6, -17, 3.6, 3.6, mat='steel')
    to.ell(7.2, -18.2, 4.0, 4.0, mat='sun', raise_=0.5)
    to.ell(7.2, -18.2, 3.0, 3.0, op='emit', v=0.7, soft=0.6)
    for k in range(8):
        a = k * 0.785
        to.poly([(4 + math.cos(a - 0.15) * 6.6, -17 + math.sin(a - 0.15) * 6.6), (4 + math.cos(a) * 9.4, -17 + math.sin(a) * 9.4), (4 + math.cos(a + 0.15) * 6.6, -17 + math.sin(a + 0.15) * 6.6)], mat='gold', raise_=0.8, edge=0.1)
    to.line([(-9, -8), (11, -9)], 0.8, op='tex', v=0.95)
    to.line([(-10, -26), (-4, -29), (8, -28)], 0.8, op='tex', v=0.95)
    to.cracks(2, 6, v=0.1, w=0.6, seed=22)
    go = add('gorget', 'torso', (0, -29), z=6.5, mat='steel', depth=3.2, noise=0.3, seed=23)
    go.spl([(-6, -3), (4, -5), (11, -2), (13, 3), (4, 6), (-5, 4)])
    go.line([(-5, 2), (11, 0)], 0.8, op='tex', v=0.95)
    hd = add('head', 'torso', (4, -31), z=12, mat='steel', depth=6.2, noise=0.3, seed=30, tnoise=0.12)
    hd.spl([(-8, -2), (-9, -12), (-4, -19), (4, -20), (10, -15), (12, -7), (11, -2), (8, 2), (3, 3.5), (-3, 3)])
    hd.poly([(3, -10), (12, -10.5), (12, -7.5), (3, -7)], mat='void', raise_=-0.4)
    hd.poly([(3.6, -9.6), (11.6, -10), (11.6, -8.2), (3.6, -7.8)], mat='sun')
    hd.poly([(3.6, -9.6), (11.6, -10), (11.6, -8.2), (3.6, -7.8)], op='emit', v=1.0, soft=0.4)
    hd.poly([(6.4, -10), (8.2, -10), (8.2, -1), (6.4, -1)], mat='void', raise_=-0.3)
    hd.poly([(7, -9), (7.6, -9), (7.6, -2), (7, -2)], op='emit', v=0.7, soft=0.3)
    hd.poly([(-8, -14), (12, -16), (12, -13), (-8, -11)], mat='gold', raise_=0.8, edge=0.1)
    for k in range(4):
        hd.line([(5 + k * 1.8, -2.5), (5 + k * 1.8, 1.8)], 0.5, op='tex', v=0.08)
    hd.line([(-8, -5), (11, -6)], 0.8, op='tex', v=0.95)
    cr = add('crown', 'head', (1, -19), z=13, mat='gold', depth=2.0, noise=0.2, seed=33)
    cr.poly([(-9, 2), (-8, -6), (-6, 0), (-4, -12), (-1.5, -1), (1, -15), (3.5, -1), (6, -11), (8, 0), (10, -5), (11, 2), (0, 3.5)])
    for nm, x, z, dim in (('f', 9, 11, 0.0), ('b', -9, 3, -0.2)):
        pf = add('pauld_' + nm, 'torso', (x, -26), z=z, mat='steel', depth=5.2, noise=0.4, seed=44, dim=dim)
        pf.spl([(-11, 5), (-11, -3), (-5, -9), (4, -9.5), (11, -4), (11, 4), (5, 9), (-3, 9)])
        pf.poly([(-12, 3), (-12, -4), (-6, -8), (-6, 4)], mat='gold', raise_=0.8, edge=0.1)
        pf.line([(-9, 1), (-2, -4), (8, -3)], 0.8, op='tex', v=0.95)
        pf.line([(-9, 5), (0, 7.5), (9, 4)], 0.8, op='tex', v=0.95)
        pf.poly([(-6, -8), (-10, -18), (-2, -9)], mat='gold', raise_=0.8, edge=0.1)
        pf.poly([(2, -9), (3, -22), (7, -8.5)], mat='gold', raise_=0.8, edge=0.1)
        pf.ell(1, 0, 2.6, 2.6, mat='sun', raise_=0.8, edge=0.1)
        pf.ell(1, 0, 1.6, 1.6, op='emit', v=0.9, soft=0.3)
    for nm, x, z, dim in (('b', -9, 3, -0.2), ('f', 9, 10, 0.0)):
        ua = add('uarm_' + nm, 'torso', (x, -25), z=z, mat='steel', depth=3.8, noise=0.3, seed=40, dim=dim, tnoise=0.12)
        ua.tube([(0, 0), (1.5, 9), (1, 17)], 4.4, 3.4)
        ua.spl([(-3.8, 8), (4.2, 8), (4.0, 18), (-3.2, 18)], mat='steel', raise_=1.1, edge=0.1)
        ua.line([(-3.6, 9), (4, 9)], 0.7, op='tex', v=0.95)
        fa = add('farm_' + nm, 'uarm_' + nm, (1, 17), z=z, mat='steel', depth=3.4, noise=0.3, seed=41, dim=dim, tnoise=0.12)
        fa.tube([(0, 0), (0.5, 8), (0.5, 16)], 3.4, 2.8)
        fa.spl([(-3.4, 3), (3.6, 3), (3.4, 16), (-2.8, 16)], mat='steel', raise_=1.1, edge=0.1)
        fa.poly([(-3.8, 12), (3.8, 12), (3.8, 16), (-3.8, 16)], mat='gold', raise_=0.7, edge=0.1)
        hn = add('hand_' + nm, 'farm_' + nm, (0.5, 16), z=z + 0.2, mat='steel', depth=2.6, noise=0.2, seed=42, dim=dim)
        hn.spl([(-3, -1), (3, -1), (3.8, 3.5), (2, 6.5), (-2, 6.5), (-3.4, 3)])
    c1 = add('cape1', 'torso', (-8, -27), z=1, mat='cloth', depth=6.0, noise=0.5, seed=1)
    c1.spl([(-6, -1), (2, -3), (9, 0), (10, 9), (9, 18), (8, 25), (-6, 26), (-16, 25), (-14, 17), (-11, 8)], per=6)
    c1.hatch(2.5, 80, v=0.28, w=0.6, jit=0.4)
    c1.spl([(6, 0), (9, 1), (10, 9), (9, 18), (8, 25), (4, 25), (5, 16), (4, 7)], mat='clothg', raise_=0.5, edge=0.2)
    c1.line(bez((-6, 2), (-9, 14), (-8, 24), n=8), 1.0, op='tex', v=0.12)
    c2 = add('cape2', 'cape1', (-4, 23), z=1, mat='cloth', depth=5.0, noise=0.5, seed=2)
    c2.poly([(12, -3), (-11, -3), (-15, 8), (-18, 20)] + rag(-18, 12, 24, 6, 11, 3, 1) + [(13, 10)])
    c2.hatch(2.5, 78, v=0.28, w=0.6, jit=0.4)
    c2.poly([(-12, 20), (13, 20), (13, 24), (-16, 24)], mat='clothg', raise_=0.3, edge=0.2)
    c3 = add('cape3', 'cape2', (-4, 22), z=1, mat='cloth', depth=3.5, noise=0.4, seed=3)
    c3.poly([(13, -3), (-12, -3), (-17, 6), (-19, 14)] + rag(-19, 13, 14, 5, 15, 5, 1) + [(14, 8)])
    c3.hatch(2.5, 76, v=0.28, w=0.6, jit=0.4)
    # alabarda
    hb = add('halberd', 'hand_f', (0, 3), z=10.5, mat='steel', depth=2.6, noise=0.3, seed=50)
    hb.poly([(-2.0, -26), (2.0, -26), (2.2, 56), (-2.2, 56)])
    hb.line([(0, -24), (0, 54)], 0.9, op='tex', v=0.16)
    for yy in (-14, 10, 34):
        hb.poly([(-3, yy), (3, yy), (3, yy + 3), (-3, yy + 3)], mat='gold', raise_=0.8, edge=0.1)
    hb.poly([(-2.2, 56), (2.2, 56), (0, 94)], mat='gold', raise_=1.0, edge=0.1)
    hb.poly([(-6, 52), (6, 52), (6, 56), (-6, 56)], mat='gold', raise_=1.0, edge=0.1)
    # cuchilla creciente (luna)
    hb.spl([(2, 48), (13, 46), (26, 52), (34, 66), (32, 82), (22, 74), (20, 64), (12, 58), (2, 58)], mat='steel', raise_=1.2, edge=0.08)
    hb.spl([(14, 49), (26, 55), (32, 66), (31, 78), (26, 71), (24, 63), (16, 57)], mat='gold', raise_=1.0, edge=0.1)
    hb.spl([(6, 52), (16, 54), (22, 62), (21, 70), (14, 62)], mat='sun', raise_=0.2)
    hb.spl([(8, 53), (15, 55), (19, 61), (18, 66), (13, 61)], op='emit', v=0.9, soft=0.5)
    hb.spl([(-2, 52), (-10, 52), (-14, 60), (-12, 66), (-6, 60), (-2, 60)], mat='steel', raise_=1.0, edge=0.1)
    hb.ell(0, 52, 3, 3, mat='sun', raise_=0.6)
    hb.ell(0, 52, 2, 2, op='emit', v=1.0, soft=0.3)
    hb.poly([(-2, -26), (2, -26), (1.4, -34), (-1.4, -34)], mat='gold', raise_=0.8, edge=0.1)
    hb.cracks(2, 6, v=0.1, w=0.5, seed=51)
    # escudo
    sd = add('shield', 'hand_b', (4, 2), z=12.5, mat='steel', depth=4.2, noise=0.3, seed=60)
    sd.spl([(-3, -22), (8, -24), (18, -20), (20, -4), (16, 12), (8, 26), (-1, 30), (-8, 14), (-9, -6)])
    sd.spl([(-1, -19), (7, -21), (15, -17), (17, -4), (13, 9), (7, 21), (0, 24), (-5, 11), (-6, -5)], mat='steel', raise_=-0.4, edge=0.9)
    sd.spl([(-3, -22), (8, -24), (18, -20), (20, -4), (16, 12), (8, 26), (-1, 30), (-8, 14), (-9, -6)], op='tex', v=0.9, soft=0.0)
    sd.ell(6, 1, 9.5, 9.5, mat='gold', raise_=1.2, edge=0.1)
    sd.ell(6, 1, 7.2, 7.2, mat='void', raise_=-0.2)
    sd.ell(9, -0.6, 6.2, 6.2, mat='sun', raise_=0.4)
    sd.ell(9, -0.6, 5.0, 5.0, op='emit', v=0.55, soft=1.0)
    sd.ell(4.6, 2, 6.0, 6.0, mat='steel', raise_=0.9)
    for k in range(8):
        a = k * 0.785 + 0.4
        sd.poly([(6 + math.cos(a - 0.12) * 9.4, 1 + math.sin(a - 0.12) * 9.4), (6 + math.cos(a) * 13, 1 + math.sin(a) * 13), (6 + math.cos(a + 0.12) * 9.4, 1 + math.sin(a + 0.12) * 9.4)], mat='gold', raise_=0.7, edge=0.1)
    sd.line([(-3, -22), (-8, 14)], 0.9, op='tex', v=0.95)
    sd.cracks(2, 6, v=0.1, w=0.6, seed=61)
    return P


H = make_H(wp='halberd')


def post(boss, pose):
    pose = dict(pose)
    pose['shield.s'] = pose.get('shield.s', 1.0) * 0.72
    return pose


def make(anims, fxhook):
    return Boss('guardian_eclipse', (192, 160), (96, 156), (34, 104), build_parts(), MATS, anims, fxhook,
                outline=(8, 6, 14), rim=(255, 220, 120), rimk=0.4, dis_col=(255, 214, 110), seed=41, post=post, scale=1.0)


# ====================================================================== animaciones
def L(thf, shf, thb, shb, ff=None, fb=None):
    return {'thigh_f': thf, 'shin_f': shf, 'foot_f': -(thf + shf) * 0.9 if ff is None else ff,
            'thigh_b': thb, 'shin_b': shb, 'foot_b': -(thb + shb) * 0.9 if fb is None else fb}


def PZ(*ds):
    return merge(*ds)


def SH(u, f, h=0):
    """brazo del escudo."""
    return {'uarm_b': u, 'farm_b': f, 'hand_b': h}


def cape(f, n, amp=1.0, base=0.0, ph=0.0):
    return {'cape1': base * 0.5 + amp * 3.0 * S(f, n, ph), 'cape2': base + amp * 4.5 * S(f, n, ph + 0.12),
            'cape3': base * 1.4 + amp * 6.0 * S(f, n, ph + 0.25)}


STAND = PZ(L(-9, 12, 10, -8), H(2, -26, -50, 168), SH(-12, -52, -10), {'head': -1, 'shield.z': 12.5})


def idle_pose(f):
    b = S(f, 6)
    return PZ(STAND, {'root.y': -0.9 * b, 'torso': 1.2 * b, 'head': -1.6 * b, 'uarm_f': -0.8 * b, 'halberd': 1.0 * S(f, 6, 0.1), 'uarm_b': 1.0 * b},
              cape(f, 6, 1.0, 1.5))


def walk_pose(f):
    ph = 2 * math.pi * f / 8
    s = math.sin(ph); c = math.cos(ph)
    thf = 20 * s - 6; thb = -20 * s + 6
    shf = 14 + 24 * max(0, -c * 0.9 + 0.1) * (1 if s < 0.3 else 0.3) + 6 * max(0, c)
    shb = 14 + 24 * max(0, c * 0.9 + 0.1) * (1 if s > -0.3 else 0.3) + 6 * max(0, -c)
    return PZ(L(thf, shf * 0.8, thb, shb * 0.8), H(5, -26 + 2 * s, -50, 168 + 3 * s), SH(-12 - 4 * s, -52, -10),
              {'root.y': -2.2 * abs(c) + 1, 'head': -2 + 2 * c, 'torso': 1.5 * c, 'hip': 1.5 * s}, cape(f, 8, 1.4, 5, 0.0))


WIND1 = [(0, STAND),
         (1, PZ(L(-12, 14, 11, -7), H(-2, -60, -50, 200), SH(-30, -60, -10), {'root.y': 1})),
         (2, PZ(L(-14, 16, 12, -6), H(-6, -90, -50, 226), SH(-34, -60, -10), {'root.y': 1.5, 'head': -6})),
         (3, PZ(L(-16, 18, 13, -6), H(-9, -104, -48, 244), SH(-38, -60, -10), {'root.y': 2, 'head': -9})),
         (4, PZ(L(-16, 18, 13, -6), H(-11, -108, -46, 252), SH(-40, -60, -10), {'root.y': 2.5, 'head': -10}))]
wind1k = K(WIND1)


def wind1(f):
    return PZ(wind1k(f), cape(f, 5, 0.6, 3 + f))


ATK1 = [(0, WIND1[-1][1], 'sm'),
        (1, PZ(L(-22, 26, 14, -6), H(2, -104, -46, 170), SH(-30, -62, -10), {'root.y': 2, 'root.x': 3, 'head': 0}), 'snap'),
        (2, PZ(L(-26, 30, 16, -8), H(12, -84, -44, 100), SH(-24, -62, -10), {'root.y': 2.5, 'root.x': 6, 'head': 4}), 'snap'),
        (3, PZ(L(-28, 34, 17, -8), H(18, -62, -44, 38), SH(-20, -64, -10), {'root.y': 3, 'root.x': 8, 'head': 5}), 'snap'),
        (4, PZ(L(-28, 34, 17, -8), H(18, -56, -44, 30), SH(-20, -64, -10), {'root.y': 3, 'root.x': 8, 'head': 5}), 'out'),
        (5, PZ(L(-24, 30, 15, -8), H(14, -48, -46, 26), SH(-22, -62, -10), {'root.y': 2.5, 'root.x': 6, 'head': 3}), 'sm'),
        (6, PZ(L(-16, 20, 12, -8), H(8, -40, -48, 70), SH(-24, -62, -10), {'root.y': 1.5, 'root.x': 3}), 'sm'),
        (7, STAND, 'sm')]
atk1k = K(ATK1)


def atk1(f):
    return PZ(atk1k(f), cape(f, 8, 1.2, 8 - f * 0.5, 0.2))


WIND2 = [(0, STAND),
         (1, PZ(L(-10, 16, 11, -8), H(0, -20, -60, 60), SH(-30, -62, -10), {'root.y': 1})),
         (2, PZ(L(-12, 22, 13, -12), H(-6, 4, -70, 82), SH(-36, -60, -10), {'root.y': 2.5, 'head': -4})),
         (3, PZ(L(-14, 28, 15, -16), H(-12, 20, -74, 90), SH(-40, -60, -10), {'root.y': 3.5, 'root.x': -4, 'head': -7})),
         (4, PZ(L(-14, 28, 15, -16), H(-14, 24, -76, 92), SH(-42, -60, -10), {'root.y': 4, 'root.x': -6, 'head': -8}))]
wind2k = K(WIND2)


def wind2(f):
    return PZ(wind2k(f), cape(f, 5, 0.5, -2 - f * 2, 0.3))


ATK2 = [(0, WIND2[-1][1], 'sm'),
        (1, PZ(L(-30, 24, 24, -14), H(14, -62, -34, -80), SH(-26, -62, -10), {'root.y': 2, 'root.x': 8, 'head': 4}), 'snap'),
        (2, PZ(L(-36, 22, 28, -12), H(20, -80, -20, -86), SH(-22, -62, -10), {'root.y': 1, 'root.x': 12, 'head': 6}), 'snap'),
        (3, PZ(L(-36, 22, 28, -12), H(22, -84, -14, -88), SH(-22, -62, -10), {'root.y': 1, 'root.x': 14, 'head': 7}), 'out'),
        (4, PZ(L(-34, 22, 26, -12), H(21, -82, -16, -88), SH(-22, -62, -10), {'root.y': 1, 'root.x': 14, 'head': 7}), 'sm'),
        (5, PZ(L(-30, 22, 22, -12), H(18, -76, -22, -84), SH(-24, -62, -10), {'root.y': 1.5, 'root.x': 12, 'head': 5}), 'sm'),
        (6, PZ(L(-18, 18, 14, -10), H(10, -52, -40, 20), SH(-24, -62, -10), {'root.y': 1.5, 'root.x': 7}), 'sm'),
        (7, STAND, 'sm')]
atk2k = K(ATK2)


def atk2(f):
    return PZ(atk2k(f), cape(f, 8, 1.6, -14 + f * 1.5, 0.0))


WIND3 = [(0, STAND),
         (1, PZ(L(-26, 52, 24, -34), H(8, -60, -60, 150), SH(-40, -60, -10), {'root.y': 3.5, 'head': -2})),
         (2, PZ(L(-30, 62, 28, -42), H(0, -86, -50, 190), SH(-50, -50, -10), {'root.y': 5, 'head': -6})),
         (3, PZ(L(-32, 66, 30, -46), H(-6, -100, -46, 230), SH(-60, -44, -10), {'root.y': 6.5, 'head': -10})),
         (4, PZ(L(-34, 70, 32, -50), H(-10, -104, -44, 248), SH(-70, -40, -10), {'root.y': 7.5, 'head': -12})),
         (5, PZ(L(-34, 70, 32, -50), H(-12, -106, -44, 252), SH(-74, -40, -10), {'root.y': 8, 'head': -13}))]
wind3k = K(WIND3)


def wind3(f):
    return PZ(wind3k(f), cape(f, 6, 0.5, 4 + f, 0.3))


ATK3 = [(0, WIND3[-1][1], 'sm'),
        (1, PZ(L(-6, 8, 6, -4), H(-4, -106, -44, 250), SH(-74, -40, -10), {'root.y': -22, 'head': -8}), 'out'),
        (2, PZ(L(-12, 26, 12, -20), H(2, -106, -44, 244), SH(-60, -40, -10), {'root.y': -28, 'head': -4}), 'sm'),
        (3, PZ(L(-18, 28, 14, -26), H(12, -94, -46, 150), SH(-40, -50, -10), {'root.y': -14, 'head': 4}), 'in'),
        (4, PZ(L(-30, 48, 24, -34), H(22, -62, -52, 20), SH(-26, -60, -10), {'root.y': 5, 'root.x': 4, 'head': 6}), 'snap'),
        (5, PZ(L(-32, 52, 26, -38), H(24, -60, -54, 8), SH(-24, -60, -10), {'root.y': 6, 'root.x': 4, 'head': 7}), 'sm'),
        (6, PZ(L(-30, 48, 22, -34), H(20, -58, -54, 8), SH(-24, -60, -10), {'root.y': 5, 'root.x': 4, 'head': 6}), 'sm'),
        (7, PZ(L(-18, 28, 14, -18), H(10, -48, -48, 20), SH(-24, -62, -10), {'root.y': 3, 'root.x': 2}), 'sm'),
        (8, STAND, 'sm')]
atk3k = K(ATK3)


def atk3(f):
    return PZ(atk3k(f), cape(f, 9, 1.8, -10 if f in (1, 2, 3) else 6, 0.0))


CAST = K([(0, STAND),
          (1, PZ(L(-10, 14, 11, -8), H(-2, -64, -50, 190), SH(-50, -70, -10), {'root.y': 1, 'head': -4})),
          (2, PZ(L(-12, 16, 12, -8), H(-6, -100, -50, 190), SH(-90, -60, -10), {'root.y': 1.5, 'head': -8}), 'sm'),
          (3, PZ(L(-12, 16, 12, -8), H(-8, -120, -50, 186), SH(-112, -56, -10), {'root.y': 1, 'head': -10}), 'sm'),
          (4, PZ(L(-14, 18, 14, -8), H(6, -110, -46, 160), SH(-120, -50, -10), {'root.y': 2, 'root.x': 2, 'head': 0}), 'snap'),
          (5, PZ(L(-16, 20, 14, -8), H(8, -100, -44, 170), SH(-100, -50, -10), {'root.y': 2, 'root.x': 2}), 'out'),
          (6, PZ(L(-12, 16, 12, -8), H(6, -60, -44, 180), SH(-50, -60, -10), {'root.y': 1}), 'sm'),
          (7, STAND, 'sm')])


def cast(f):
    return PZ(CAST(f), cape(f, 8, 1.4, 4, 0.0))


def hurt(f):
    d = [PZ(L(-6, 14, 12, -6), H(-12, -30, -50, 176), SH(-40, -50, -10), {'head': -12, 'root.x': -3, 'root.y': 1, 'tint': ((255, 255, 255), 0.5)}),
         PZ(L(-8, 14, 11, -6), H(-6, -28, -48, 172), SH(-30, -56, -10), {'head': -6, 'root.x': -2, 'tint': ((255, 255, 255), 0.2)})][int(f)]
    return PZ(d, cape(f, 2, 1, 6 + 4 * (1 - f)))


PHASE = K([(0, STAND),
           (1, PZ(L(-16, 30, 16, -20), H(8, -20, -50, 150), SH(-10, -40, -10), {'root.y': 3, 'head': 8}), 'sm'),
           (2, PZ(L(-22, 44, 22, -30), H(14, -14, -56, 130), SH(0, -30, -10), {'root.y': 6, 'head': 12}), 'sm'),
           (3, PZ(L(-14, 22, 16, -14), H(6, -50, -52, 160), SH(-60, -50, -10), {'root.y': 1, 'head': -2}), 'out'),
           (4, PZ(L(-8, 8, 10, -4), H(-10, -110, -44, 236), SH(-150, -30, -10), {'root.y': -4, 'head': -22, 'torso.sy': 1.04}), 'snap'),
           (5, PZ(L(-8, 8, 10, -4), H(-12, -116, -44, 240), SH(-156, -26, -10), {'root.y': -5, 'head': -26, 'torso.sy': 1.05}), 'sm'),
           (6, PZ(L(-8, 8, 10, -4), H(-12, -116, -44, 240), SH(-154, -28, -10), {'root.y': -4.5, 'head': -24}), 'sm'),
           (7, PZ(L(-14, 18, 12, -10), H(0, -90, -48, 210), SH(-110, -40, -10), {'root.y': -1, 'head': -8}), 'in'),
           (8, PZ(L(-12, 16, 11, -9), H(2, -50, -50, 180), SH(-50, -56, -10), {'root.y': 1, 'head': 2}), 'snap'),
           (9, STAND, 'sm')])


def phase(f):
    p = PHASE(f)
    if 4 <= f <= 7:
        p['tint'] = ((255, 230, 150), 0.22 * (1 - abs(f - 5.5) / 2.0))
    p['root.x'] = p.get('root.x', 0) + (1.0 if (f in (5, 6) and int(f) % 2) else (-1.0 if f in (5, 6) else 0))
    return PZ(p, cape(f, 10, 2.0, -8 if 3 <= f <= 7 else 4, 0.0))


def intro(f):
    i = int(f)
    # camina desde la puerta (izquierda) hacia su sitio
    walkx = -46 * (1 - clamp01((i - 4) / 8.0))
    ph = f * 0.9
    s = math.sin(ph * 2.2); c = math.cos(ph * 2.2)
    moving = 1 if (4 <= i <= 11) else 0
    thf = (20 * s - 6) * moving + (-9) * (1 - moving); thb = (-20 * s + 6) * moving + 10 * (1 - moving)
    shf = (14 + 18 * max(0, -c)) * moving + 12 * (1 - moving); shb = (14 + 18 * max(0, c)) * moving + -8 * (1 - moving)
    p = PZ(L(thf, shf * 0.8 if moving else shf, thb, shb * 0.8 if moving else shb), H(3, -26, -50, 168 + 8 * (1 - clamp01((i - 11) / 2.0))), SH(-24, -62, -10),
           {'root.x': walkx, 'root.y': (-1.8 * abs(c) if moving else 0), 'head': -1})
    p = PZ(p, cape(f, 14, 1.4, 8 if moving else 2))
    if i < 4:
        p['clip'] = (0, 0, 0, 0)
    return p


DEATH = K([(0, PZ(L(-6, 14, 12, -6), H(-12, -30, -50, 176), SH(-40, -50, -10), {'head': -12, 'root.x': -3, 'tint': ((255, 255, 255), 0.5)}), 'out'),
           (1, PZ(L(-4, 18, 14, -8), H(-8, -20, -30, 150), SH(-30, -40, -10), {'head': -8, 'root.x': -5, 'tint': ((255, 255, 255), 0.2)}), 'sm'),
           (2, PZ(L(-6, 26, 16, -16), H(2, -8, -20, 120), SH(-10, -20, -10), {'head': 4, 'root.x': -4, 'root.y': 3, 'tint': ((255, 255, 255), 0.0)}), 'sm'),
           (3, PZ(L(-20, 56, 20, -50), H(8, 4, -12, 90), SH(0, -10, -10), {'head': 12, 'root.x': -2, 'root.y': 10}), 'sm'),
           (4, PZ(L(-40, 100, 26, -92), H(14, 14, -6, 60), SH(10, 0, -10), {'head': 20, 'root.y': 20}), 'sm'),
           (5, PZ(L(-50, 120, 30, -110), H(20, 24, 0, 40), SH(20, 4, -10), {'head': 28, 'root.y': 26, 'root.x': 2}), 'sm'),
           (6, PZ(L(-60, 130, 32, -120), H(30, 30, 6, 20), SH(30, 8, -10), {'head': 32, 'root.y': 29, 'root.x': 6, 'torso': 30}), 'sm'),
           (7, PZ(L(-60, 130, 32, -120), H(40, 40, 8, 10), SH(40, 10, -10), {'head': 36, 'root.y': 31, 'root.x': 10, 'torso': 50}), 'in'),
           (13, PZ(L(-60, 130, 32, -120), H(48, 44, 8, 5), SH(46, 12, -10), {'head': 38, 'root.y': 33, 'root.x': 12, 'torso': 58}), 'lin')])


def death(f):
    p = DEATH(f)
    d = clamp01((f - 6.5) / 5.5)
    if d > 0:
        p['dis'] = d * 1.12
        p['dis_dir'] = 1.0
    c = clamp01((f - 3.0) / 4.0)
    p['crown.y'] = 0 if f < 4 else 10 * c * c * 4
    p['crown.x'] = 0 if f < 4 else 6 * c
    p['crown'] = 40 * c
    p['shield.y'] = 0 if f < 5 else 10 * clamp01((f - 5) / 3.0)
    p.update(cape(f, 14, 0.5, 6 + f * 2))
    return p


# ====================================================================== efectos
def halo(ctx, k=1.0, spin=0.0, total=0.0, a=1.0):
    """halo de eclipse tras la cabeza: sol dorado con corona, luna negra que lo cubre."""
    fx, i = ctx.fx, ctx.i
    hx, hy = ctx.anchor('head', (-1, -8))
    hx -= 3; hy -= 6
    R = 21 * k
    fx.glow(hx, hy, R * 1.9, (255, 200, 70), 0.34 * a)
    ang0 = spin
    rays(ctx, hx, hy, 1.0, (255, 210, 100), 18, R * 0.9, R * 0.9, 0.05, 0.28 * a, ang0, 'back', 'over')
    fx.ell(hx, hy, R + 2.4, R + 2.4, (110, 70, 14), 0.9 * a, 'back')
    fx.ell(hx, hy, R, R, (226, 170, 52), 0.98 * a, 'back')
    fx.ell(hx - 1, hy - 1, R - 2.6, R - 2.6, (255, 226, 130), 0.98 * a, 'back')
    fx.ell(hx - 2, hy - 2, R - 7, R - 7, (255, 246, 200), 0.9 * a, 'back')
    off = 6.5 * (1 - total)
    mx, my = hx + 4 * off / 6.5 * (1 if total < 1 else 0) + 1.0 * off, hy - 2 * off / 6.5
    fx.ell(mx, my, R - 3.5, R - 3.5, (14, 10, 22), a, 'back')
    fx.ell(mx - 1, my - 1, R - 5, R - 5, (28, 22, 40), a, 'back')
    fx.ring(hx, hy, R + 5, R + 5, 1, (255, 224, 140), 0.6 * a, 'back')
    fx.ring(hx, hy, R + 5 + 1.5, R + 5 + 1.5, 1, (255, 196, 80), 0.35 * a, 'back', a0=(i * 30) % 360, a1=(i * 30) % 360 + 120)
    fx.glow(hx + R * 0.6, hy - R * 0.5, 6, (255, 244, 200), 0.8 * a * (1 - 0.5 * total))
    return hx, hy


def fxhook(ctx):
    n, i, fx, W = ctx.name, ctx.i, ctx.fx, ctx.W
    ax, ay = ctx.pivot
    rng = ctx.rng
    tip = lambda f=None: ctx.anchor('halberd', (0, 90)) if f is None else ctx.anchor_at(f, 'halberd', (0, 90))
    blade = lambda f=None: ctx.anchor('halberd', (24, 66)) if f is None else ctx.anchor_at(f, 'halberd', (24, 66))
    k = 1.0; total = 0.0; a = 1.0
    if n == 'intro':
        k = 1.0 if i >= 5 else 0.0
        a = clamp01((i - 4) / 3.0)
    if n == 'death':
        k = max(0.0, 1 - max(0, i - 3) / 7.0); a = k
    if n == 'phase':
        total = clamp01((i - 3) / 2.5) if i <= 7 else clamp01(1 - (i - 7) / 2.0)
        k = 1.0 + 0.5 * total
    if k > 0.05 and a > 0.02:
        halo(ctx, k, spin=i * 0.05, total=total, a=a)
    # runas / brillo de la hoja
    bx, by = blade()
    if n not in ('intro', 'death'):
        fx.glow(bx, by, 14, (255, 210, 90), 0.3 + 0.08 * math.sin(i * 1.4))
        wisps(ctx, ax - 6, ay - 50, 46, 90, 8, [(255, 214, 110), (255, 246, 210)], seed=3, a=0.8, rise=22)
    ex, ey = ctx.anchor('head', (8, -9))
    if n != 'death' or i < 5:
        fx.glow(ex, ey, 6, (255, 214, 100), 0.55)
    if n == 'windup1':
        t = i / 4.0
        tx, ty = tip()
        fx.glow(tx, ty, 10 + 14 * t, (255, 220, 110), 0.45 * t + 0.1)
        wisps(ctx, tx, ty + 6, 14, 14, 6, [(255, 240, 180), (255, 255, 240)], t=t * 0.9, seed=8, rise=8)
    if n == 'attack1':
        trail(ctx, 'halberd', (24, 70), (0, 56), 0, 4, (255, 250, 220), (200, 130, 30), steps=12, span=3.0, mid=(255, 214, 100), a=0.8)
        trail(ctx, 'halberd', (0, 92), (0, 60), 0, 4, (255, 255, 240), (150, 100, 30), steps=12, span=3.0, a=0.5)
        if 3 <= i <= 6:
            tx, ty = ctx.anchor_at(3.6, 'halberd', (14, 64))
            tt = (i - 3) / 3.0
            gx = min(tx, W - 6)
            dust(ctx, gx, ay, tt, (150, 140, 120), 9, 22, 8)
            shock(ctx, gx, ay, tt, (255, 232, 160), 30, 4)
            fx.glow(gx, ay - 4, 14 * (1 - tt * 0.5), (255, 220, 120), 0.8 * (1 - tt))
            if i == 3:
                fx.sparks(rng, gx, ay - 3, 12, 14, [(255, 255, 255), (255, 214, 100)], 'front', 6)
    if n == 'windup2':
        t = i / 4.0
        tx, ty = tip()
        fx.glow(tx, ty, 8 + 14 * t, (255, 220, 110), 0.4 * t + 0.1)
        for kk in range(3):
            fx.line((tx + 8 + kk * 6, ty + (kk - 1) * 2), (tx + 2, ty + (kk - 1) * 1.5), 1, (255, 235, 170), 0.5 * t, 'front', mode='add')
    if n == 'attack2':
        if 1 <= i <= 6:
            tx, ty = tip()
            t = (i - 1) / 5.0
            x0 = ctx.anchor('hand_f', (0, 0))[0]
            ln = min(90, W - 6 - x0) * ease_out(clamp01(i / 2.0)) * (1 - 0.4 * clamp01((i - 4) / 3.0))
            y0 = ctx.anchor('hand_f', (0, 0))[1] - 2
            wv = 8 * (1 - 0.35 * t)
            fx.poly([(x0, y0), (x0 + ln * 0.5, y0 - wv), (x0 + ln, y0), (x0 + ln * 0.5, y0 + wv)], (200, 130, 30), 0.5 * (1 - t * 0.6), 'front', ss=2)
            fx.poly([(x0, y0), (x0 + ln * 0.5, y0 - wv * 0.55), (x0 + ln * 0.95, y0), (x0 + ln * 0.5, y0 + wv * 0.55)], (255, 226, 140), 0.75 * (1 - t * 0.5), 'front', ss=2)
            fx.line((x0, y0), (x0 + ln * 0.9, y0), 1, (255, 255, 255), 0.95 * (1 - t * 0.5), 'front')
            for kk in range(4):
                yy = y0 + (kk - 1.5) * 6
                xs = x0 - 10 - ((i * 7 + kk * 13) % 14)
                fx.line((xs, yy), (xs - 10 - 4 * kk, yy), 1, (255, 214, 110), 0.6 * (1 - t * 0.5), 'front')
        if 1 <= i <= 5:
            dust(ctx, ax + 4, ay, clamp01((i - 1) / 4.0), (150, 140, 120), 8, 18, 6, a=0.6)
    if n == 'windup3':
        t = i / 5.0
        tx, ty = tip()
        fx.glow(tx, ty, 10 + 16 * t, (255, 220, 110), 0.5 * t + 0.1)
        wisps(ctx, ax, ay - 3, 40, 6, 8, [(255, 226, 140)], t=t, seed=5, rise=26, a=0.7)
        rays(ctx, ax, ay - 2, t * 0.6, (255, 214, 100), 6, 6, 26, 0.18, 0.4 * t, 0.4, 'back')
    if n == 'attack3':
        if 1 <= i <= 4:
            trail(ctx, 'halberd', (24, 70), (0, 56), 2, 4, (255, 250, 220), (200, 130, 30), steps=12, span=2.6, mid=(255, 214, 100), a=0.8)
        if 4 <= i <= 8:
            t = (i - 4) / 4.0
            tx, ty = tip()
            gx = max(ax + 24, min(tx, W - 10))
            ground_cracks(ctx, gx, ay + 1, t, (20, 16, 24), (255, 214, 110), 8, 56, 11)
            shock(ctx, gx, ay, t, (255, 232, 160), 66, 7, 2)
            dust(ctx, gx, ay, t, (140, 130, 110), 14, 40, 14, 3.0)
            if i <= 6:
                fx.glow(gx, ay - 6, 20 * (1 - t * 0.5), (255, 226, 140), 0.8 * (1 - t))
                for kk in range(5):
                    px = gx - 28 + kk * 14 + (kk % 2) * 2
                    h = (40 + 14 * (kk % 3)) * (1 - t * 0.6)
                    fx.poly([(px - 3, ay), (px, ay - h), (px + 3, ay)], (255, 214, 100), 0.7, 'front', ss=2)
                    fx.poly([(px - 1.2, ay), (px, ay - h * 0.9), (px + 1.2, ay)], (255, 250, 220), 0.9, 'front', ss=2)
    if n == 'cast':
        tx, ty = tip()
        if 1 <= i <= 4:
            t = i / 4.0
            for kk in range(7):
                ang = i * 0.9 + kk * 0.9
                r = 16 * (1 - t * 0.5) + 2
                px = tx + math.cos(ang) * r; py = ty + math.sin(ang) * r * 0.8
                fx.glow(px, py, 4, (255, 214, 100), 0.8)
                fx.dots([(px, py)], (255, 248, 220), 1.0, 'front')
            fx.glow(tx, ty, 8 + 10 * t, (255, 220, 110), 0.7)
        if i >= 4:
            tt = (i - 4) / 3.0
            for kk in range(3):
                sx_ = tx + 6 + tt * (40 + kk * 12)
                sy_ = ty + 6 + (kk - 1) * 14 + tt * (kk - 1) * 8
                if sx_ < W - 4:
                    fx.glow(sx_, sy_, 10, (255, 214, 100), 0.85)
                    if kk % 2 == 0:
                        fx.ell(sx_, sy_, 4.2, 4.2, (255, 232, 140), 1.0, 'front')
                        fx.ell(sx_ - 1, sy_ - 1, 2.4, 2.4, (255, 252, 230), 1.0, 'front')
                    else:
                        fx.ell(sx_, sy_, 4.2, 4.2, (24, 18, 34), 1.0, 'front')
                        fx.ring(sx_, sy_, 4.8, 4.8, 1, (255, 214, 100), 1.0, 'front')
                    fx.polyline([(sx_ - 4, sy_), (sx_ - 14, sy_ + 1), (sx_ - 24, sy_)], 2, (255, 200, 80), 0.5, 'front')
    if n == 'phase':
        t = clamp01((i - 3) / 5.0)
        if 3 <= i <= 9:
            fx.glow(ax, ay - 56, 60 * t + 12, (255, 200, 70), 0.5 * (1 - abs(t - 0.5) * 1.2), rx=48 * t + 14, ry=64 * t + 14)
            rays(ctx, ax, ay - 62, t, (255, 226, 140), 14, 14, 70, 0.1, 0.5, i * 0.1, 'back', 'over')
            shock(ctx, ax, ay, clamp01((i - 4) / 5.0), (255, 226, 150), 58, 7, 2)
        if 4 <= i <= 8:
            wisps(ctx, ax, ay - 56, 52, 80, 16, [(255, 226, 140), (255, 252, 230)], t=(i - 4) / 6.0, seed=21, rise=40, a=1.0)
    if n == 'death':
        if i >= 8:
            t = clamp01((i - 8) / 5.0)
            pile(ctx, ax + 10, ay + 1, 46, 8 + 4 * t, [(60, 56, 70), (110, 100, 130), (196, 160, 60)], 12 + int(26 * t), seed=6)
            sx_ = ax + 26
            fx.poly([(sx_ - 1.6, ay - 70), (sx_ + 1.6, ay - 70), (sx_ + 2, ay + 1), (sx_ - 2, ay + 1)], (50, 46, 60), 1.0, 'back')
            fx.poly([(sx_ - 2, ay - 70), (sx_ + 2, ay - 70), (sx_, ay - 90)], (200, 160, 60), 1.0, 'back')
            fx.poly([(sx_ + 2, ay - 74), (sx_ + 14, ay - 66), (sx_ + 12, ay - 54), (sx_ + 2, ay - 60)], (210, 170, 64), 1.0, 'back')
            fx.line((sx_ - 0.5, ay - 66), (sx_ - 0.5, ay - 2), 1, (150, 130, 80), 0.9, 'back')
            wisps(ctx, ax + 14, ay - 6, 40, 14, 10, [(255, 226, 140), (255, 252, 230)], t=(i - 8) / 6.0, seed=7, rise=30, a=0.9)
        if 3 <= i <= 9:
            hx, hy = ctx.anchor('head', (0, -8))
            fx.sparks(rng, hx - 3, hy - 6, 6, 24, [(255, 226, 140), (255, 252, 230)], 'front', 4, 0.9)
    if n == 'intro':
        intro_fx(ctx)


def intro_fx(ctx):
    i, fx, ax, ay = ctx.i, ctx.fx, ctx.pivot[0], ctx.pivot[1]
    dx = ax - 54
    # puerta gotica a la izquierda
    open_t = 0.0 if i < 3 else (clamp01((i - 3) / 1.4))
    sh = (1 if i % 2 else -1) * (1 if 1 <= i <= 2 else 0)
    fx.poly([(dx - 22 + sh, ay), (dx - 22 + sh, ay - 78), (dx - 14 + sh, ay - 96), (dx + 0 + sh, ay - 104), (dx + 14 + sh, ay - 96), (dx + 22 + sh, ay - 78), (dx + 22 + sh, ay)], (10, 8, 14), 1.0, 'back')
    fx.poly([(dx - 19 + sh, ay), (dx - 19 + sh, ay - 77), (dx - 12 + sh, ay - 93), (dx + sh, ay - 101), (dx + 12 + sh, ay - 93), (dx + 19 + sh, ay - 77), (dx + 19 + sh, ay)], (60, 54, 70), 1.0, 'back')
    # interior luminoso
    inner = 16 * open_t
    if open_t > 0:
        fx.poly([(dx - inner, ay), (dx - inner, ay - 74), (dx, ay - 90 * (0.7 + 0.3 * open_t)), (dx + inner, ay - 74), (dx + inner, ay)], (255, 226, 130), 0.95, 'back')
        fx.poly([(dx - inner * 0.6, ay), (dx - inner * 0.6, ay - 70), (dx, ay - 84 * (0.7 + 0.3 * open_t)), (dx + inner * 0.6, ay - 70), (dx + inner * 0.6, ay)], (255, 252, 232), 0.95, 'back')
        fx.glow(dx, ay - 46, 50, (255, 214, 100), 0.55 * open_t * (1 if i < 12 else 0.5), rx=40, ry=64)
        rays(ctx, dx, ay - 50, 1.0, (255, 236, 160), 12, 10, 80, 0.07, 0.35 * open_t * (1 if i < 9 else max(0, 1 - (i - 9) / 4.0)), 0.3, 'back', 'over')
    else:
        fx.poly([(dx - 17, ay), (dx - 17, ay - 74), (dx, ay - 90), (dx + 17, ay - 74), (dx + 17, ay)], (28, 24, 36), 1.0, 'back')
        fx.line((dx, ay - 92), (dx, ay), 1, (10, 8, 14), 1.0, 'back')
    if 3 <= i <= 4:
        # hojas de la puerta abiertas de golpe hacia los lados
        w = 6 + 3 * (i - 3)
        fx.poly([(dx - 19, ay), (dx - 19 - w, ay - 6), (dx - 19 - w, ay - 80), (dx - 19, ay - 76)], (40, 36, 50), 1.0, 'back')
        fx.poly([(dx + 19, ay), (dx + 19 + w, ay - 6), (dx + 19 + w, ay - 80), (dx + 19, ay - 76)], (40, 36, 50), 1.0, 'front')
    if i >= 5:
        fx.poly([(dx - 26, ay), (dx - 26, ay - 4), (dx - 19, ay - 76), (dx - 19, ay)], (40, 36, 50), 1.0, 'back')
        fx.poly([(dx + 19, ay), (dx + 19, ay - 76), (dx + 26, ay - 4), (dx + 26, ay)], (40, 36, 50), 1.0, 'front')
    if 3 <= i <= 7:
        dust(ctx, dx + 4, ay, clamp01((i - 3) / 5.0), (150, 140, 120), 12, 40, 12, a=0.7)
    if 3 <= i <= 9:
        for kk in range(10):
            fx.sparks(ctx.rng, dx, ay - 40, 1, 30, [(255, 240, 180)], 'front', 14, 0.8)


def hit_boxes():
    return {
        'attack1': dict(hit=[2, 4], box=[6, -92, 74, 92]),
        'attack2': dict(hit=[1, 5], box=[8, -70, 124, 54]),
        'attack3': dict(hit=[4, 6], box=[-74, -58, 152, 58]),
        'cast': dict(rel=4, muzzle_src=('halberd', (0, 90))),
    }


def spec():
    fns = dict(idle=idle_pose, walk=walk_pose, windup1=wind1, attack1=atk1, windup2=wind2, attack2=atk2, windup3=wind3,
               attack3=atk3, cast=cast, hurt=hurt, phase=phase, intro=intro, death=death)
    hb = hit_boxes()
    return {k: dict(pose=v, **hb.get(k, {})) for k, v in fns.items()}


def build():
    return make(spec(), fxhook)
