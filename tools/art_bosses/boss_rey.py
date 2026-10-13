import math
import numpy as np
from kit import *
from shapes import *
from anim import *
from fxlib import *

BONE = auto('#d3c9a4', shadow=(52, 44, 100), warm=(255, 246, 205), n=6)
IRON = auto('#4d535f', shadow=(22, 22, 58), warm=(200, 215, 225), n=6, dk=0.24)
RUST = auto('#8c4a2a', shadow=(40, 20, 50), warm=(255, 190, 110), n=6)
GOLD = auto('#b4953a', shadow=(60, 30, 60), warm=(255, 244, 160), n=6)
CLOTH = auto('#2f3a50', shadow=(16, 14, 52), warm=(110, 170, 170), n=6, dk=0.3)
CLOTH2 = auto('#43324f', shadow=(20, 12, 50), warm=(170, 140, 190), n=6, dk=0.3)
VOID = ramp((4, 6, 12), (10, 14, 22), (30, 38, 52), 6)
SOULG = [(8, 54, 40), (20, 120, 76), (58, 220, 130), (150, 255, 190), (236, 255, 244)]
MATS = {
    'bone': Mat(BONE, texamt=0.45), 'iron': Mat(IRON, gain=1.25, texamt=0.5), 'rust': Mat(RUST, gain=1.1),
    'gold': Mat(GOLD, gain=1.3), 'cloth': Mat(CLOTH, gain=0.9, texamt=0.7), 'cloth2': Mat(CLOTH2, gain=0.9, texamt=0.7),
    'void': Mat(VOID, gain=0.5), 'soul': Mat(BONE, glow=SOULG, texamt=0.3),
}
SOULC = (90, 255, 160)


def build_parts():
    P = []

    def add(*a, **k):
        p = Part(*a, **k); P.append(p); return p
    add('root', None, (96, 156), ghost=True)
    hip = add('hip', 'root', (0, -44), z=4, mat='iron', depth=4.5, noise=0.5, seed=5)
    hip.spl([(-9, -4), (-4, -7), (6, -7), (10, -3), (12, 4), (8, 9), (2, 6), (-2, 10), (-7, 8), (-11, 3)])
    hip.blotch('rust', 0.78, 2.5, 9)
    hip.line([(-11, -2), (11, -2)], 0.8, op='tex', v=0.1)
    hip.ell(2.5, -2, 3.4, 3.4, mat='gold', raise_=0.8, edge=0.08)
    hip.ell(2.5, -2, 1.4, 1.7, mat='void')
    for nm, x, z, dim in (('b', -4, 2, -0.2), ('f', 4, 5, 0.0)):
        th = add('thigh_' + nm, 'hip', (x, 3), z=z, mat='bone', depth=4.0, noise=0.3, seed=10, dim=dim, tnoise=0.15)
        th.tube([(0, 0), (1, 9), (1, 19)], 4.8, 3.6)
        th.spl([(-5.0, 0), (5.4, 0), (5.6, 13), (-4.2, 14)], mat='iron', raise_=1.2, edge=0.1)
        th.ell(0.8, 19, 5.4, 4.4, mat='iron', raise_=1.6, edge=0.1)
        th.ell(1.6, 19, 1.2, 1.2, mat='bone')
        th.blotch('rust', 0.8, 2.4, 12)
        sh = add('shin_' + nm, 'thigh_' + nm, (1, 19), z=z, mat='bone', depth=3.4, noise=0.3, seed=11, dim=dim, tnoise=0.15)
        sh.tube([(0, 0), (0, 8), (-0.5, 17)], 3.9, 2.8)
        sh.spl([(-4.2, 2), (4.6, 2), (4.0, 15), (-3.0, 15)], mat='iron', raise_=1.2, edge=0.1)
        sh.line([(0.4, 3), (0.2, 13)], 0.7, op='tex', v=0.92)
        sh.blotch('rust', 0.8, 2.2, 13)
        ft = add('foot_' + nm, 'shin_' + nm, (-0.5, 17), z=z, mat='iron', depth=2.8, noise=0.3, seed=12, dim=dim)
        ft.spl([(-5, -4), (2, -5), (5.5, -1), (11, 1.5), (14, 3.6), (11, 5.4), (-5.5, 5.4)])
        ft.line([(6, 0.8), (10, 3)], 0.6, op='tex', v=0.1)
        ft.blotch('rust', 0.78, 2.0, 14)
    # ---------------- torso: cavidad oscura + costillas de hueso
    to = add('torso', 'hip', (0, -2), z=6, mat='void', depth=7.0, noise=0.3, seed=20, tnoise=0.12)
    to.spl([(-8, -2), (-11, -12), (-10, -23), (-4, -29), (6, -28), (12, -20), (12, -9), (8, -2), (-3, -1)])
    to.spl([(3, -21), (8, -20), (9, -14), (6.5, -9), (3, -11), (2, -16)], mat='soul')
    to.spl([(4, -19), (7, -18.4), (7.6, -14.5), (6, -11.5), (4, -14)], op='emit', v=1.0, soft=1.0)
    to.line([(-3, -28), (-3.6, -2)], 2.6, op='mat', mat='bone', raise_=0.9, edge=0.08)
    for k in range(5):
        y = -24 + k * 4.6
        to.tube(bez((-3, y), (4, y - 5), (11, y + 1), n=9), 1.15, 1.0, mat='bone', raise_=1.0, edge=0.08)
    to.tube([(10.5, -26), (11, -18), (10, -8)], 1.1, mat='bone', raise_=1.0, edge=0.08)
    to.spl([(-10, -9), (-12, -20), (-8, -27), (-2, -27), (-5, -20), (0, -15), (-3, -8)], mat='iron', raise_=1.6, edge=0.1)
    to.blotch('rust', 0.76, 2.6, 21, within=None)
    gorget = add('gorget', 'torso', (0, -27), z=6.5, mat='iron', depth=3.2, noise=0.4, seed=23)
    gorget.spl([(-6, -3), (4, -5), (11, -2), (13, 3), (4, 6), (-5, 4)])
    gorget.blotch('rust', 0.78, 2.2, 24)
    gorget.line([(-5, 2), (11, 0)], 0.8, op='tex', v=0.12)
    tb = add('tabard', 'hip', (1, 4), z=5.5, mat='cloth2', depth=3.0, noise=0.4, seed=23)
    tb.poly([(-8, -1), (9, -1), (10, 9)] + rag(10, -9, 14, 5, 9, 2, 1) + [(-9, 8)])
    tb.hatch(2.0, 90, v=0.28, w=0.6, jit=0.3)
    tb.line([(0, 0), (0, 20)], 0.7, op='tex', v=0.2)
    tb.ell(2, 8, 1.5, 2.3, op='sub')
    # ---------------- cabeza
    hd = add('head', 'torso', (4, -30), z=12, mat='bone', depth=6.0, noise=0.3, seed=30, tnoise=0.10)
    hd.spl([(-8, -3), (-8.5, -11), (-3, -17), (4, -17.5), (9.5, -13), (12, -7), (11, -2.5), (9, 1), (4, 3), (-3, 2.5)])
    # cavidad de la boca (visible al abrir la mandibula)
    hd.spl([(1, 0), (10, -0.5), (11, 3), (6, 5.5), (1, 4)], mat='void', raise_=-0.3)
    # orbitas
    hd.spl([(1.5, -9.5), (6, -10.6), (10, -8.4), (10.4, -3.6), (7.5, -1.8), (3.2, -3.2)], mat='void', raise_=-0.6)
    hd.ell(7.0, -6.0, 2.0, 2.1, rot=10, mat='soul')
    hd.ell(7.0, -6.0, 1.55, 1.6, op='emit', v=1.0, soft=0.4)
    # ceja, pomulo, nariz
    hd.line([(1, -11), (6, -12.4), (11, -9.5)], 1.1, op='tex', v=0.95)
    hd.line([(3, -2), (7, -0.6), (11, -2)], 0.9, op='tex', v=0.14)
    hd.poly([(10.4, -2.2), (12.6, 1.2), (9.6, 0.8)], mat='void')
    hd.line([(-6, -12), (-1, -6), (1, -2)], 0.8, op='tex', v=0.1)
    hd.cracks(2, 6, v=0.1, w=0.6, seed=31)
    hd.line([(2, -1), (10, -1.6)], 1.0, op='tex', v=0.9)
    jw = add('jaw', 'head', (-0.5, 2.0), z=11.5, mat='bone', depth=3.2, noise=0.2, seed=32)
    jw.spl([(-3, -1), (8, -1.5), (12, 0.5), (11, 4), (6, 7.5), (0, 8), (-3, 4)])
    jw.poly([(1, -1), (11, -1.5), (11, 0.6), (1, 1)], mat='void', grow=False) if False else None
    for k in range(6):
        jw.poly([(1.4 + k * 1.75, -1.2), (2.9 + k * 1.75, -1.2), (2.4 + k * 1.75, 2.1), (1.6 + k * 1.75, 2.1)], mat='bone', raise_=0.7, edge=0.35)
    jw.line([(0, 3.5), (10, 3)], 0.8, op='tex', v=0.2)
    cr = add('crown', 'head', (1.5, -16), z=13, mat='gold', depth=2.6, noise=0.3, seed=33)
    cr.spl([(-10, 4), (-10, 0), (-9, -6), (-6, -1), (-4, -13), (-1, -2), (2, -10), (5, -1), (8, -6), (10, 0), (11, 4), (0, 6)])
    cr.line([(-10, 3), (11, 3)], 0.9, op='tex', v=0.12)
    cr.ell(1, 3, 1.5, 1.5, mat='soul'); cr.ell(1, 3, 1.2, 1.2, op='emit', v=1.0, soft=0.4)
    cr.ell(-5, 3, 1.1, 1.1, mat='soul'); cr.ell(-5, 3, 0.9, 0.9, op='emit', v=0.8, soft=0.3)
    cr.ell(7, 3, 1.1, 1.1, mat='soul'); cr.ell(7, 3, 0.9, 0.9, op='emit', v=0.8, soft=0.3)
    # ---------------- brazos
    for nm, x, z, dim in (('b', -9, 3, -0.2), ('f', 9, 10, 0.0)):
        ua = add('uarm_' + nm, 'torso', (x, -25), z=z, mat='bone', depth=3.6, noise=0.3, seed=40, dim=dim, tnoise=0.15)
        ua.tube([(0, 0), (1.5, 9), (1, 17)], 3.8, 2.9)
        ua.spl([(-3.4, 8), (3.8, 8), (3.6, 18), (-2.8, 18)], mat='iron', raise_=1.2, edge=0.1)
        fa = add('farm_' + nm, 'uarm_' + nm, (1, 17), z=z, mat='bone', depth=3.2, noise=0.3, seed=41, dim=dim, tnoise=0.15)
        fa.tube([(0, 0), (0.5, 8), (0.5, 15)], 2.9, 2.3)
        fa.spl([(-3.2, 3), (3.4, 3), (3.1, 15), (-2.6, 15)], mat='iron', raise_=1.2, edge=0.1)
        fa.line([(0, 4), (0, 13)], 0.6, op='tex', v=0.92)
        hn = add('hand_' + nm, 'farm_' + nm, (0.5, 15), z=z + 0.2, mat='bone', depth=2.4, noise=0.2, seed=42, dim=dim)
        hn.spl([(-2.8, -1), (2.8, -1), (3.6, 3.5), (1.8, 6), (-1.8, 6), (-3.2, 2.5)])
        for k in range(3):
            hn.line([(-1.7 + k * 1.7, 3.5), (-1.9 + k * 1.7, 6.5)], 0.6, op='tex', v=0.05)
    for nm, z, dim in (('f', 11, 0.0), ('b', 3.4, -0.2)):
        pf = add('pauld_' + nm, 'uarm_' + nm, (0, -1), z=z, mat='iron', depth=5.0, noise=0.6, seed=44, dim=dim)
        pf.spl([(-11, 5), (-11, -3), (-5, -9), (4, -9.5), (11, -4), (11, 4), (5, 9), (-3, 9)])
        pf.line([(-9, 1), (-2, -4), (8, -3)], 0.9, op='tex', v=0.1)
        pf.line([(-9, 4.5), (0, 7), (9, 3.5)], 0.9, op='tex', v=0.1)
        pf.poly([(-8, -6), (-14, -16), (-3, -9)], mat='bone', raise_=0.8, edge=0.1)
        pf.poly([(-2, -9), (-3, -22), (4, -9.5)], mat='bone', raise_=0.8, edge=0.1)
        pf.poly([(5, -8.5), (13, -17), (11.5, -3)], mat='bone', raise_=0.8, edge=0.1)
        pf.ell(1, 0, 3.0, 3.0, mat='gold', raise_=1.0, edge=0.08)
        pf.ell(1, 0, 1.2, 1.2, mat='soul')
        pf.blotch('rust', 0.74, 2.2, 45)
        pf.cracks(2, 6, v=0.1, w=0.6, seed=46)
    # ---------------- capa (cadena de 3)
    c1 = add('cape1', 'torso', (-8, -27), z=1, mat='cloth', depth=6.0, noise=0.5, seed=1)
    c1.spl([(-6, -1), (2, -3), (9, 0), (10, 9), (9, 18), (8, 25), (-6, 26), (-16, 25), (-14, 17), (-11, 8)], per=6)
    c1.hatch(2.3, 80, v=0.3, w=0.6, jit=0.4)
    c1.cracks(3, 8, v=0.15, w=0.7, seed=4)
    c1.line(bez((-6, 2), (-9, 14), (-8, 24), n=8), 1.0, op='tex', v=0.1)
    c1.line(bez((3, 2), (2, 14), (4, 24), n=8), 1.0, op='tex', v=0.1)
    c1.spl([(6, 0), (9, 1), (10, 9), (9, 18), (8, 25), (4, 25), (5, 16), (4, 7)], mat='cloth2', raise_=0.5, edge=0.2)
    c1.ell(-9, 14, 1.4, 2.2, op='sub')
    c2 = add('cape2', 'cape1', (-4, 23), z=1, mat='cloth', depth=5.0, noise=0.5, seed=2)
    c2.spl([(12, -2), (-11, -2), (-14, 8), (-17, 20), (-18, 26)], closed=False, per=6, op='add') if False else None
    c2.poly([(12, -3), (-11, -3), (-15, 8), (-18, 20)] + rag(-18, 12, 24, 6, 11, 3, 1) + [(13, 10)])
    c2.hatch(2.4, 78, v=0.28, w=0.6, jit=0.4)
    c2.line(bez((-5, 0), (-9, 14), (-8, 24), n=8), 1.0, op='tex', v=0.1)
    c2.line(bez((4, 0), (3, 14), (5, 24), n=8), 1.0, op='tex', v=0.1)
    c3 = add('cape3', 'cape2', (-4, 22), z=1, mat='cloth', depth=3.5, noise=0.4, seed=3)
    c3.poly([(13, -3), (-12, -3), (-17, 6), (-19, 14)] + rag(-19, 13, 14, 5, 15, 5, 1) + [(14, 8)])
    c3.hatch(2.4, 76, v=0.28, w=0.6, jit=0.4)
    # ---------------- espadon
    sw = add('sword', 'hand_f', (0, 2), z=10.5, mat='iron', depth=3.0, noise=0.4, seed=50)
    sw.poly([(-3.4, 5), (3.4, 5), (5, 12), (4.8, 54), (0, 66), (-4.8, 54), (-5, 12)])
    sw.line([(0, 10), (0, 56)], 1.6, op='tex', v=0.12)
    sw.line([(1.6, 12), (1.6, 52)], 0.8, op='tex', v=0.99)
    sw.poly([(-7, 4), (7, 4), (7, 7.5), (-7, 7.5)], mat='gold', raise_=1.0, edge=0.1)
    sw.spl([(-12, 2), (-6, 3), (-6, 8), (-10, 10), (-14, 6)], mat='gold', raise_=0.9, edge=0.1)
    sw.spl([(12, 2), (6, 3), (6, 8), (10, 10), (14, 6)], mat='gold', raise_=0.9, edge=0.1)
    sw.poly([(-1.1, 14), (1.1, 14), (1.1, 46), (-1.1, 46)], mat='soul')
    sw.line([(0, 14), (0, 46)], 1.2, op='emit', v=0.8, soft=0.5)
    sw.blotch('rust', 0.78, 2.2, 51)
    sw.poly([(-2.2, -10), (2.2, -10), (2.4, 3), (-2.4, 3)], mat='cloth', raise_=0.6, edge=0.1)
    sw.ell(0, -11.5, 3.4, 3.4, mat='bone', raise_=1.2, edge=0.1)
    for yy, side in ((22, 1), (32, -1), (42, 1), (50, -1)):
        sw.poly([(side * 5, yy), (side * 3.2, yy + 1.3), (side * 5.4, yy + 2.6)], op='sub')
    return P


def post(boss, pose):
    if pose.get('free_b', 0) < 0.5:
        tgt = boss.anchor(pose, 'sword', (0, pose.get('grip2', -5.5)))
        pose = dict(pose)
        pose.update(boss.ik(pose, 'uarm_b', 'farm_b', (0.5, 15), tgt, flip=pose.get('bend', 1)))
        for n in ('uarm_b', 'farm_b'):
            pose[n + '.z'] = 10.4
        pose['hand_b.z'] = 10.6
        # la mano se orienta como la espada
    return pose


def make(anims, fxhook):
    parts = build_parts()
    return Boss('rey_exanime', (192, 160), (96, 156), (30, 94), parts, MATS, anims, fxhook,
                outline=(8, 10, 18), rim=(80, 235, 150), rimk=0.4, dis_col=(110, 255, 170), seed=11, post=post, scale=1.0)


# ====================================================================== animaciones
def H(t, u, f, w):
    """Pose de tronco + brazo delantero con la espada orientada al angulo de mundo w (0=abajo,-90=adelante,180=arriba)."""
    return {'torso': t, 'uarm_f': u, 'farm_f': f, 'sword': w - (t + u + f)}


def L(thf, shf, thb, shb, ff=None, fb=None):
    return {'thigh_f': thf, 'shin_f': shf, 'foot_f': -(thf + shf) * 0.9 if ff is None else ff,
            'thigh_b': thb, 'shin_b': shb, 'foot_b': -(thb + shb) * 0.9 if fb is None else fb}


def PZ(*ds):
    return merge(*ds)


STAND = PZ(L(-9, 12, 10, -8), H(2, -35, -45, -12), {'head': -1})


def cape(f, n, amp=1.0, base=0.0, ph=0.0):
    return {'cape1': base * 0.5 + amp * 3.0 * S(f, n, ph), 'cape2': base + amp * 4.5 * S(f, n, ph + 0.12),
            'cape3': base * 1.4 + amp * 6.0 * S(f, n, ph + 0.25), 'tabard': amp * 2 * S(f, n, ph + 0.1)}


def idle_pose(f):
    b = S(f, 6)
    return PZ(STAND, {'root.y': -0.9 * b, 'torso': 1.3 * b, 'head': -1.8 * b - 1, 'jaw': 1.5 + b,
                      'uarm_f': -0.8 * b, 'sword': 1.2 * S(f, 6, 0.1)}, cape(f, 6, 1.0, 1.5))


def walk_pose(f):
    ph = 2 * math.pi * f / 8
    s = math.sin(ph); c = math.cos(ph)
    thf = 20 * s - 6
    thb = -20 * s + 6
    shf = 14 + 24 * max(0, -c * 0.9 + 0.1) * (1 if s < 0.3 else 0.3) + 6 * max(0, c)
    shb = 14 + 24 * max(0, c * 0.9 + 0.1) * (1 if s > -0.3 else 0.3) + 6 * max(0, -c)
    return PZ(L(thf, shf * 0.8, thb, shb * 0.8), H(5, -35 + 2 * s, -45, -12 + 3 * s), {
        'root.y': -2.2 * abs(c) + 1, 'root.x': 0, 'head': -2 + 2 * c, 'torso': 1.5 * c, 'hip': 1.5 * s,
        'jaw': 1 + c}, cape(f, 8, 1.4, 5, 0.0))


WIND1 = [(0, STAND),
         (1, PZ(L(-12, 14, 11, -7), H(-2, -70, -40, -80), {'root.y': 1})),
         (2, PZ(L(-14, 16, 12, -6), H(-6, -92, -42, -170), {'root.y': 1.5, 'head': -6})),
         (3, PZ(L(-16, 18, 13, -6), H(-9, -100, -40, -232), {'root.y': 2, 'head': -9, 'jaw': 8})),
         (4, PZ(L(-16, 18, 13, -6), H(-11, -102, -40, -248), {'root.y': 2.5, 'head': -10, 'jaw': 10}))]
wind1k = K(WIND1)


def wind1(f):
    p = wind1k(f)
    return PZ(p, cape(f, 5, 0.6, 3 + f), {'sword': 0.8 * math.sin(f * 5) if f > 3 else 0})


W1END = PZ(L(-16, 18, 13, -6), H(-11, -102, -40, -248), {'root.y': 2.5, 'head': -10, 'jaw': 10})
ATK1 = [(0, W1END, 'sm'),
        (1, PZ(L(-22, 26, 14, -6), H(2, -100, -40, -170), {'root.y': 2, 'root.x': 3, 'head': 0, 'jaw': 6}), 'snap'),
        (2, PZ(L(-26, 30, 16, -8), H(12, -80, -42, -98), {'root.y': 2.5, 'root.x': 6, 'head': 4}), 'snap'),
        (3, PZ(L(-28, 34, 17, -8), H(18, -62, -42, -38), {'root.y': 3, 'root.x': 8, 'head': 5}), 'snap'),
        (4, PZ(L(-28, 34, 17, -8), H(18, -56, -42, -30), {'root.y': 3, 'root.x': 8, 'head': 5}), 'out'),
        (5, PZ(L(-24, 30, 15, -8), H(14, -48, -44, -26), {'root.y': 2.5, 'root.x': 6, 'head': 3}), 'sm'),
        (6, PZ(L(-16, 20, 12, -8), H(8, -40, -44, -18), {'root.y': 1.5, 'root.x': 3}), 'sm'),
        (7, PZ(STAND), 'sm')]
atk1k = K(ATK1)


def atk1(f):
    return PZ(atk1k(f), cape(f, 8, 1.2, 8 - f * 0.5, 0.2))


WIND2 = [(0, STAND),
         (1, PZ(L(-10, 16, 11, -8), H(0, -10, -50, -70), {'root.y': 1})),
         (2, PZ(L(-12, 22, 13, -12), H(-6, 10, -60, -85), {'root.y': 2.5, 'head': -4})),
         (3, PZ(L(-14, 28, 15, -16), H(-12, 24, -66, -88), {'root.y': 3.5, 'root.x': -3, 'head': -7, 'jaw': 6})),
         (4, PZ(L(-14, 28, 15, -16), H(-14, 28, -68, -90), {'root.y': 4, 'root.x': -5, 'head': -8, 'jaw': 8}))]
wind2k = K(WIND2)


def wind2(f):
    return PZ(wind2k(f), cape(f, 5, 0.5, -2 - f * 2, 0.3))


ATK2 = [(0, PZ(L(-14, 28, 15, -16), H(-14, 28, -68, -90), {'root.y': 4, 'root.x': -5, 'head': -8, 'jaw': 8}), 'sm'),
        (1, PZ(L(-30, 24, 24, -14), H(14, -58, -34, -92), {'root.y': 2, 'root.x': 8, 'head': 4}), 'snap'),
        (2, PZ(L(-36, 22, 28, -12), H(20, -76, -14, -90), {'root.y': 1, 'root.x': 14, 'head': 6}), 'snap'),
        (3, PZ(L(-36, 22, 28, -12), H(22, -80, -10, -90), {'root.y': 1, 'root.x': 16, 'head': 7}), 'out'),
        (4, PZ(L(-34, 22, 26, -12), H(21, -78, -12, -90), {'root.y': 1, 'root.x': 16, 'head': 7}), 'sm'),
        (5, PZ(L(-30, 22, 22, -12), H(18, -72, -18, -86), {'root.y': 1.5, 'root.x': 14, 'head': 5}), 'sm'),
        (6, PZ(L(-18, 18, 14, -10), H(10, -50, -34, -50), {'root.y': 1.5, 'root.x': 8}), 'sm'),
        (7, PZ(STAND), 'sm')]
atk2k = K(ATK2)


def atk2(f):
    return PZ(atk2k(f), cape(f, 8, 1.6, -14 + f * 1.5, 0.0))


WIND3 = [(0, STAND),
         (1, PZ(L(-26, 52, 24, -34), H(8, -60, -60, -70), {'root.y': 3.5, 'head': -2})),
         (2, PZ(L(-30, 62, 28, -42), H(0, -86, -50, -170), {'root.y': 5, 'head': -6})),
         (3, PZ(L(-32, 66, 30, -46), H(-6, -98, -42, -236), {'root.y': 6.5, 'head': -10, 'jaw': 8})),
         (4, PZ(L(-34, 70, 32, -50), H(-10, -102, -40, -250), {'root.y': 7.5, 'head': -12, 'jaw': 12})),
         (5, PZ(L(-34, 70, 32, -50), H(-12, -104, -40, -254), {'root.y': 8, 'head': -13, 'jaw': 14}))]
wind3k = K(WIND3)


def wind3(f):
    return PZ(wind3k(f), cape(f, 6, 0.5, 4 + f, 0.3))


ATK3 = [(0, PZ(L(-34, 70, 32, -50), H(-12, -104, -40, -254), {'root.y': 8, 'head': -13, 'jaw': 14}), 'sm'),
        (1, PZ(L(-6, 8, 6, -4), H(-4, -104, -40, -250), {'root.y': -13, 'head': -8, 'jaw': 10, 'torso.sy': 1.04}), 'out'),
        (2, PZ(L(-12, 26, 12, -20), H(2, -104, -40, -246), {'root.y': -17, 'head': -4, 'jaw': 10}), 'sm'),
        (3, PZ(L(-18, 28, 14, -26), H(12, -92, -44, -150), {'root.y': -8, 'head': 4}), 'in'),
        (4, PZ(L(-30, 48, 24, -34), H(22, -62, -52, -18), {'root.y': 5, 'root.x': 4, 'head': 6}), 'snap'),
        (5, PZ(L(-32, 52, 26, -38), H(24, -60, -54, -8), {'root.y': 6, 'root.x': 4, 'head': 7}), 'sm'),
        (6, PZ(L(-30, 48, 22, -34), H(20, -58, -54, -8), {'root.y': 5, 'root.x': 4, 'head': 6}), 'sm'),
        (7, PZ(L(-18, 28, 14, -18), H(10, -48, -48, -12), {'root.y': 3, 'root.x': 2}), 'sm'),
        (8, PZ(STAND), 'sm')]
atk3k = K(ATK3)


def atk3(f):
    return PZ(atk3k(f), cape(f, 9, 1.8, -10 if f in (1, 2, 3) else 6, 0.0))


CAST = K([(0, STAND),
          (1, PZ(L(-10, 14, 11, -8), H(-2, -64, -50, -90), {'root.y': 1, 'head': -4})),
          (2, PZ(L(-12, 16, 12, -8), H(-6, -88, -52, -140), {'root.y': 1.5, 'head': -8, 'jaw': 6}), 'sm'),
          (3, PZ(L(-12, 16, 12, -8), H(-8, -92, -54, -150), {'root.y': 1, 'head': -10, 'jaw': 10}), 'sm'),
          (4, PZ(L(-14, 18, 14, -8), H(6, -84, -46, -126), {'root.y': 2, 'root.x': 3, 'head': 0, 'jaw': 12}), 'snap'),
          (5, PZ(L(-16, 20, 14, -8), H(8, -76, -44, -108), {'root.y': 2, 'root.x': 3}), 'out'),
          (6, PZ(L(-12, 16, 12, -8), H(6, -60, -44, -60), {'root.y': 1}), 'sm'),
          (7, PZ(STAND), 'sm')])


def cast(f):
    return PZ(CAST(f), cape(f, 8, 1.4, 4, 0.0))


def hurt(f):
    d = [PZ(L(-6, 14, 12, -6), H(-12, -30, -50, 4), {'head': -12, 'root.x': -3, 'root.y': 1, 'jaw': 10, 'tint': ((255, 255, 255), 0.5)}),
         PZ(L(-8, 14, 11, -6), H(-6, -32, -48, -4), {'head': -6, 'root.x': -2, 'tint': ((255, 255, 255), 0.2)})][int(f)]
    return PZ(d, cape(f, 2, 1, 6 + 4 * (1 - f)))


PSTAND = PZ(L(-9, 12, 10, -8), H(2, -30, -50, -8), {'free_b': 1})
PHASE = K([(0, PZ(STAND, {'free_b': 1, 'uarm_b': 0, 'farm_b': -10})),
           (1, PZ(L(-16, 30, 16, -20), H(8, -20, -50, -30), {'root.y': 3, 'head': 8, 'free_b': 1, 'uarm_b': 10, 'farm_b': -30}), 'sm'),
           (2, PZ(L(-22, 44, 22, -30), H(14, -14, -56, -10), {'root.y': 6, 'head': 12, 'free_b': 1, 'uarm_b': 24, 'farm_b': -50}), 'sm'),
           (3, PZ(L(-14, 22, 16, -14), H(6, -30, -52, -8), {'root.y': 1, 'head': -2, 'free_b': 1, 'uarm_b': -60, 'farm_b': -40}), 'out'),
           (4, PZ(L(-8, 8, 10, -4), H(-10, -36, -52, -8), {'root.y': -4, 'head': -22, 'jaw': 28, 'free_b': 1, 'uarm_b': -150, 'farm_b': -20, 'torso.sy': 1.04}), 'snap'),
           (5, PZ(L(-8, 8, 10, -4), H(-12, -36, -52, -8), {'root.y': -5, 'head': -26, 'jaw': 32, 'free_b': 1, 'uarm_b': -156, 'farm_b': -16, 'torso.sy': 1.05}), 'sm'),
           (6, PZ(L(-8, 8, 10, -4), H(-12, -36, -52, -8), {'root.y': -4.5, 'head': -24, 'jaw': 30, 'free_b': 1, 'uarm_b': -154, 'farm_b': -18}), 'sm'),
           (7, PZ(L(-14, 18, 12, -10), H(0, -34, -52, -8), {'root.y': -1, 'head': -8, 'jaw': 14, 'free_b': 1, 'uarm_b': -100, 'farm_b': -30}), 'in'),
           (8, PZ(L(-12, 16, 11, -9), H(2, -34, -48, -10), {'root.y': 1, 'head': 2, 'free_b': 1, 'uarm_b': -40, 'farm_b': -30}), 'snap'),
           (9, PZ(STAND, {'free_b': 0}), 'sm')])


def phase(f):
    p = PHASE(f)
    if 4 <= f <= 7:
        p['tint'] = ((120, 255, 180), 0.22 * (1 - abs(f - 5.5) / 2.0))
    p['root.x'] = p.get('root.x', 0) + (1.0 if (f in (5, 6) and int(f) % 2) else (-1.0 if f in (5, 6) else 0))
    if f >= 9:
        p['free_b'] = 0
    return PZ(p, cape(f, 10, 2.0, -8 if 3 <= f <= 7 else 4, 0.0))


INTRO_RISE = [92, 90, 90, 90, 80, 68, 56, 44, 33, 22, 12, 5, 0, 0]


def intro(f):
    i = int(f)
    ry = INTRO_RISE[i] if f == i else INTRO_RISE[i] + (INTRO_RISE[min(13, i + 1)] - INTRO_RISE[i]) * (f - i)
    lift = clamp01((f - 8) / 4.0)
    base = PZ(STAND, {'root.y': ry})
    arms = PZ(H(2 - 8 * (1 - lift), -35 - 55 * (1 - lift), -45 - 25 * (1 - lift), -12 - 42 * (1 - lift)), {'head': -10 * (1 - lift)})
    p = PZ(base, arms, cape(f, 14, 1.4, 10 * (1 - lift)))
    if i < 4:
        p['clip'] = (0, 0, 0, 0)
    return p


def clamp01(t):
    return max(0.0, min(1.0, t))


DEATH = K([(0, PZ(L(-6, 14, 12, -6), H(-12, -30, -50, 4), {'head': -12, 'root.x': -3, 'jaw': 10, 'tint': ((255, 255, 255), 0.5)}), 'out'),
           (2, PZ(L(-6, 26, 16, -16), H(2, -8, -20, 30), {'head': 4, 'root.x': -4, 'root.y': 3, 'jaw': 6, 'tint': ((255, 255, 255), 0.0)}), 'sm'),
           (1, PZ(L(-4, 18, 14, -8), H(-8, -20, -30, 16), {'head': -8, 'root.x': -5, 'jaw': 12, 'tint': ((255, 255, 255), 0.2)}), 'sm'),
           (3, PZ(L(-20, 56, 20, -50), H(8, 4, -12, 60), {'head': 12, 'root.x': -2, 'root.y': 10, 'jaw': 4}), 'sm'),
           (4, PZ(L(-40, 100, 26, -92), H(14, 14, -6, 70), {'head': 20, 'root.y': 20, 'root.x': 0, 'jaw': 2}), 'sm'),
           (5, PZ(L(-50, 120, 30, -110), H(20, 24, 0, 80), {'head': 28, 'root.y': 26, 'root.x': 2}), 'sm'),
           (6, PZ(L(-60, 130, 32, -120), H(30, 30, 6, 90), {'head': 32, 'root.y': 29, 'root.x': 6, 'torso': 38}), 'sm'),
           (7, PZ(L(-60, 130, 32, -120), H(40, 40, 8, 100), {'head': 36, 'root.y': 31, 'root.x': 10, 'torso': 52}), 'in'),
           (13, PZ(L(-60, 130, 32, -120), H(48, 44, 8, 100), {'head': 38, 'root.y': 33, 'root.x': 12, 'torso': 60}), 'lin')])


def death(f):
    p = DEATH(f)
    p['free_b'] = 1 if f >= 2 else 0
    if f >= 2:
        p['uarm_b'] = 10 + 4 * f; p['farm_b'] = -10 - 3 * f
    d = clamp01((f - 6.5) / 5.5)
    if d > 0:
        p['dis'] = d * 1.12
        p['dis_dir'] = 1.0
    c = clamp01((f - 3.0) / 4.0)
    p['crown.y'] = 0 if f < 4 else 10 * c * c * 4
    p['crown.x'] = 0 if f < 4 else 6 * c
    p['crown'] = 40 * c
    p['sword.y'] = 0 if f < 5 else 12 * clamp01((f - 5) / 3.0)
    p.update(cape(f, 14, 0.5, 6 + f * 2))
    return p


# ====================================================================== efectos
GR = [(20, 120, 76), (60, 220, 130), (150, 255, 190), (236, 255, 244)]


def fxhook(ctx):
    n, i, fx, W = ctx.name, ctx.i, ctx.fx, ctx.W
    ax, ay = ctx.pivot
    rng = ctx.rng
    tip = lambda f=None: ctx.anchor('sword', (0, 66)) if f is None else ctx.anchor_at(f, 'sword', (0, 66))
    # llamas de alma en la corona y volutas (siempre)
    if n not in ('intro',) or i >= 4:
        hx, hy = ctx.anchor('crown', (1, -8))
        k = 1.0
        if n == 'death':
            k = max(0, 1 - i / 8.0)
        if n == 'phase':
            k = 2.4 if 4 <= i <= 7 else 1.3
        if k > 0.05:
            for j, ox in enumerate((-5, -1, 3)):
                flame_tuft_local(ctx, hx + ox, hy + 3, (6 + 3 * (j == 1)) * k, 2.0, i * 0.37 + j)
            fx.glow(hx, hy + 2, 12 * k, (60, 255, 150), 0.35 * k)
    ex, ey = ctx.anchor('head', (6.4, -4.4))
    if n != 'death' or i < 5:
        fx.glow(ex, ey, 7, (90, 255, 170), 0.45)
    cx_, cy_ = ctx.anchor('torso', (6, -16))
    if n != 'death' or i < 6:
        fx.glow(cx_, cy_, 12, (60, 255, 150), 0.30 + 0.08 * math.sin(i * 1.3))
    sx0, sy0 = ctx.anchor('sword', (0, 30))
    fx.glow(sx0, sy0, 22, (60, 255, 150), 0.18, rx=10, ry=26)
    if n not in ('intro', 'death'):
        wisps(ctx, ax - 6, ay - 40, 46, 80, 9, [(120, 255, 180), (200, 255, 225)], seed=3, a=0.8, rise=22)
    # --- anim especificas
    if n == 'windup1':
        t = i / 4.0
        tx, ty = tip()
        fx.glow(tx, ty, 10 + 12 * t, (80, 255, 160), 0.5 * t + 0.1)
        wisps(ctx, tx, ty + 6, 14, 14, 6, [(150, 255, 190), (236, 255, 244)], t=t * 0.9, seed=8, rise=8)
    if n == 'attack1':
        trail(ctx, 'sword', (0, 68), (0, 50), 0, 4, (236, 255, 244), (30, 150, 90), steps=12, span=3.0, mid=(70, 220, 130), a=0.7)
        if 3 <= i <= 6:
            tx, ty = tip(3.6)
            tt = (i - 3) / 3.0
            dust(ctx, min(tx, W - 6), ay, tt, (130, 150, 150), 9, 22, 8)
            shock(ctx, min(tx, W - 6), ay, tt, (190, 255, 215), 28, 4)
            fx.glow(tx, ay - 4, 14 * (1 - tt * 0.5), (120, 255, 190), 0.8 * (1 - tt))
            if i == 3:
                fx.sparks(rng, tx, ay - 3, 10, 14, [(255, 255, 255), (150, 255, 190)], 'front', 6)
    if n == 'windup2':
        t = i / 4.0
        tx, ty = tip()
        fx.glow(tx, ty, 8 + 14 * t, (80, 255, 160), 0.4 * t + 0.1)
        for k in range(3):
            fx.line((tx + 8 + k * 6, ty + (k - 1) * 2), (tx + 2, ty + (k - 1) * 1.5), 1, (180, 255, 210), 0.5 * t, 'front', mode='add')
    if n == 'attack2':
        if 1 <= i <= 6:
            tx, ty = tip()
            t = (i - 1) / 5.0
            ln = min(86, W - 6 - tx) * (ease_out(clamp01(i / 2.0))) * (1 - 0.4 * clamp01((i - 4) / 3.0))
            y0 = ty
            wv = 7 * (1 - 0.35 * t)
            pts = [(tx - 2, y0), (tx + ln * 0.5, y0 - wv), (tx + ln, y0), (tx + ln * 0.5, y0 + wv)]
            fx.poly(pts, (40, 170, 100), 0.55 * (1 - t * 0.6), 'front', ss=2)
            pts2 = [(tx - 2, y0), (tx + ln * 0.5, y0 - wv * 0.55), (tx + ln * 0.95, y0), (tx + ln * 0.5, y0 + wv * 0.55)]
            fx.poly(pts2, (150, 255, 195), 0.75 * (1 - t * 0.5), 'front', ss=2)
            fx.line((tx, y0), (tx + ln * 0.9, y0), 1, (255, 255, 255), 0.95 * (1 - t * 0.5), 'front')
            for k in range(4):
                yy = y0 + (k - 1.5) * 5
                x0 = tx - 4 - ((i * 7 + k * 13) % 14)
                fx.line((x0, yy), (x0 - 10 - 4 * k, yy), 1, (110, 255, 170), 0.6 * (1 - t * 0.5), 'front')
        if 1 <= i <= 5:
            dust(ctx, ctx.pivot[0] - 6, ay, clamp01((i - 1) / 4.0), (130, 150, 150), 8, 18, 6, a=0.6)
    if n == 'windup3':
        t = i / 5.0
        tx, ty = tip()
        fx.glow(tx, ty, 10 + 16 * t, (80, 255, 160), 0.5 * t + 0.1)
        wisps(ctx, ax, ay - 3, 40, 6, 8, [(150, 255, 190)], t=t, seed=5, rise=26, a=0.7)
        rays(ctx, ax, ay - 2, t * 0.6, (80, 255, 160), 6, 6, 26, 0.18, 0.4 * t, 0.4, 'back')
    if n == 'attack3':
        tx, ty = tip()
        if 1 <= i <= 4:
            trail(ctx, 'sword', (0, 68), (0, 50), 2, 4, (236, 255, 244), (30, 150, 90), steps=12, span=2.6, mid=(70, 220, 130), a=0.7)
        if i in (1, 2):
            fx.glow(ax, ay - 8, 22, (60, 255, 150), 0.25)
        if 4 <= i <= 8:
            t = (i - 4) / 4.0
            gx = max(ax + 24, min(tx, W - 10))
            ground_cracks(ctx, gx, ay + 1, t, (14, 14, 22), (110, 255, 170), 8, 56, 11)
            shock(ctx, gx, ay, t, (190, 255, 215), 62, 7, 2)
            dust(ctx, gx, ay, t, (120, 140, 140), 14, 40, 14, 3.0)
            if i <= 6:
                fx.glow(gx, ay - 6, 20 * (1 - t * 0.5), (120, 255, 190), 0.8 * (1 - t))
                for k in range(5):
                    px = gx - 28 + k * 14 + (k % 2) * 2
                    h = (26 + 8 * (k % 3)) * (1 - t * 0.7)
                    flame_tuft_local(ctx, px, ay + 1, h, 3.0, i * 0.4 + k, back=False)
    if n == 'cast':
        tx, ty = tip()
        if 1 <= i <= 4:
            t = i / 4.0
            for k in range(7):
                ang = i * 0.9 + k * 0.9
                r = 16 * (1 - t * 0.5) + 2
                px = tx + math.cos(ang) * r; py = ty + math.sin(ang) * r * 0.8
                fx.glow(px, py, 4, (110, 255, 170), 0.8)
                fx.dots([(px, py)], (230, 255, 240), 1.0, 'front')
            fx.glow(tx, ty, 8 + 10 * t, (80, 255, 160), 0.6)
        if i >= 4:
            tt = (i - 4) / 3.0
            for k in range(3):
                sx_ = tx + 6 + tt * (40 + k * 12) - 4
                sy_ = ty + (k - 1) * 12 + tt * (k - 1) * 8 + math.sin(i + k) * 2
                if sx_ < W - 4:
                    skull_orb(ctx, sx_, sy_, 1.0 - tt * 0.3)
    if n == 'phase':
        t = clamp01((i - 3) / 5.0)
        if 3 <= i <= 9:
            fx.glow(ax, ay - 40, 52 * t + 12, (60, 255, 150), 0.5 * (1 - abs(t - 0.5) * 1.2), rx=40 * t + 14, ry=60 * t + 14)
            rays(ctx, ax, ay - 46, t, (110, 255, 180), 14, 14, 70, 0.1, 0.5, i * 0.1, 'back', 'over')
            shock(ctx, ax, ay, clamp01((i - 4) / 5.0), (150, 255, 200), 58, 7, 2)
        if 4 <= i <= 8:
            wisps(ctx, ax, ay - 40, 52, 70, 16, [(150, 255, 190), (236, 255, 244)], t=(i - 4) / 6.0, seed=21, rise=40, a=1.0)
    if n == 'death':
        if i >= 8:
            t = clamp01((i - 8) / 5.0)
            pile(ctx, ax + 10, ay + 1, 46, 8 + 4 * t, [(206, 196, 164), (150, 142, 124), (96, 92, 98)], 12 + int(26 * t), seed=6)
            # corona en el suelo
            cx0, cy0 = ax + 4, ay - 2
            fx.poly([(cx0 - 5, cy0), (cx0 - 5, cy0 - 3), (cx0 - 3, cy0 - 1), (cx0 - 1, cy0 - 5), (cx0 + 1, cy0 - 1), (cx0 + 3, cy0 - 3), (cx0 + 5, cy0 - 1), (cx0 + 5, cy0)], (190, 160, 60), 1.0, 'back')
            # espada clavada
            sx_ = ax + 26
            fx.poly([(sx_ - 2, ay - 38), (sx_ + 2, ay - 38), (sx_ + 3, ay + 1), (sx_ - 3, ay + 1)], (44, 50, 60), 1.0, 'back')
            fx.line((sx_, ay - 34), (sx_, ay - 2), 1, (100, 255, 170), 0.9, 'back')
            fx.poly([(sx_ - 9, ay - 38), (sx_ + 9, ay - 38), (sx_ + 9, ay - 35), (sx_ - 9, ay - 35)], (160, 130, 50), 1.0, 'back')
            wisps(ctx, ax + 14, ay - 6, 40, 14, 10, [(120, 255, 180), (220, 255, 235)], t=(i - 8) / 6.0, seed=7, rise=30, a=0.9)
    if n == 'intro':
        intro_fx(ctx)


def skull_orb(ctx, x, y, s=1.0):
    fx = ctx.fx
    fx.glow(x, y, 9 * s, (70, 255, 160), 0.9)
    fx.ell(x, y, 4 * s, 4 * s, (200, 255, 225), 1.0, 'front')
    fx.ell(x + 0.5, y + 2.6 * s, 2.5 * s, 1.8 * s, (180, 235, 205), 1.0, 'front')
    fx.dots([(x - 1.8 * s, y - 0.5), (x + 1.6 * s, y - 0.5)], (10, 40, 30), 1.0, 'front')
    fx.polyline([(x - 4 * s, y + 1), (x - 11 * s, y + 3), (x - 20 * s, y + 2)], 2, (60, 230, 130), 0.5, 'front')


def flame_tuft_local(ctx, x, y, h, w, ph, back=False):
    cols = [(30, 170, 100), (90, 240, 150), (190, 255, 215)]
    flame_tuft(ctx, x, y, h, w, cols, ph, 0.95, 'back' if back else 'front')


def intro_fx(ctx):
    i, fx, ax, ay = ctx.i, ctx.fx, ctx.pivot[0], ctx.pivot[1]
    f = ctx.i
    x0, x1 = ax - 42, ax + 42
    top = ay - 26
    sink = clamp01((f - 9) / 4.0)
    shake = (1 if i % 2 else -1) * (1 if 1 <= i <= 3 else 0)
    topy = top + 26 * sink
    if sink < 1:
        fx.poly([(x0 + 3, topy - 5), (x1 - 3, topy - 5), (x1 - 1, topy), (x0 + 1, topy)], (18, 22, 28), 1.0, 'back')
        glow_in = clamp01(i / 6.0) if i < 11 else max(0, 1 - (i - 10) / 3.0)
        fx.poly([(x0 + 6, topy - 3), (x1 - 6, topy - 3), (x1 - 8, topy + 1), (x0 + 8, topy + 1)], (60, 255, 150), 0.7 * glow_in, 'back')
        block(ctx, x0 + shake, topy, x1 + shake, ay + 2, (74, 78, 94), (150, 158, 176), (34, 36, 50), 'front', seed=3, brick=(14, 8), cracks=4)
        for k in range(5):
            rx = x0 + 14 + k * 14 + shake
            al = 0.6 * glow_in if i < 12 else 0.2
            fx.line((rx, topy + 7), (rx + 5, topy + 7), 1, (60, 255, 150), al, 'front')
            fx.line((rx + 2, topy + 7), (rx + 2, topy + 13), 1, (60, 255, 150), al, 'front')
    if i < 5:
        for k in range(4):
            px = x0 + 10 + k * 19
            fx.line((px, top - 1), (px + (k - 1.5) * 2, top - 6 - i * 3), 1, (120, 255, 190), 0.4 + 0.1 * i, 'front', mode='add')
    if i < 5:
        lx = 0; ly = 0
        if i == 2:
            ly = -1
        if i == 3:
            lx = 3; ly = -3
        if i == 4:
            lx = 22; ly = -12
        T = top
        fx.poly([(x0 - 2 + lx, T - 9 + ly), (x1 + 2 + lx, T - 9 + ly), (x1 + 2 + lx, T + ly), (x0 - 2 + lx, T + ly)], (10, 10, 16), 1.0, 'front')
        fx.poly([(x0 - 1 + lx, T - 8 + ly), (x1 + 1 + lx, T - 8 + ly), (x1 + 1 + lx, T - 1 + ly), (x0 - 1 + lx, T - 1 + ly)], (92, 96, 112), 1.0, 'front')
        fx.poly([(x0 - 1 + lx, T - 8 + ly), (x1 + 1 + lx, T - 8 + ly), (x1 + 1 + lx, T - 6 + ly), (x0 - 1 + lx, T - 6 + ly)], (160, 168, 186), 1.0, 'front')
        fx.poly([(x0 - 1 + lx, T - 3 + ly), (x1 + 1 + lx, T - 3 + ly), (x1 + 1 + lx, T - 1 + ly), (x0 - 1 + lx, T - 1 + ly)], (46, 48, 64), 1.0, 'front')
        fx.line((ax + lx, T - 8 + ly), (ax + lx, T - 1 + ly), 1, (50, 52, 70), 1.0, 'front')
        fx.line((ax - 10 + lx, T - 5 + ly), (ax + 10 + lx, T - 5 + ly), 1, (50, 52, 70), 1.0, 'front')
        if i >= 2:
            fx.polyline([(ax - 24 + lx, T - 8 + ly), (ax - 20 + lx, T - 5 + ly), (ax - 23 + lx, T - 2 + ly)], 1, (110, 255, 170), 0.9, 'front')
    if i == 4:
        for k in range(5):
            px = ax - 4 + k * 12; py = top - 14 - (k % 3) * 8 + 2
            fx.poly([(px, py), (px + 5, py - 1), (px + 4, py + 4), (px - 1, py + 3)], (110, 114, 130), 1.0, 'front')
    if 5 <= i <= 9:
        fx.poly([(x1 + 4, ay - 6), (x1 + 38, ay - 6), (x1 + 34, ay), (x1 + 6, ay)], (10, 10, 16), 1.0, 'back')
        fx.poly([(x1 + 5, ay - 5), (x1 + 36, ay - 5), (x1 + 33, ay - 1), (x1 + 7, ay - 1)], (92, 96, 112), 1.0, 'back')
    if i < 13:
        g = 0.8 if i < 10 else 0.4
        fx.glow(ax, top - 4, 30, (60, 255, 150), 0.40 * g, rx=40, ry=16)
        wisps(ctx, ax, top - 8, 50, 20, 14, [(120, 255, 180), (220, 255, 235)], t=i / 13.0, seed=2, rise=34, a=0.9)
    if 4 <= i <= 12:
        dust(ctx, ax, ay - 1, clamp01((i - 4) / 6.0), (120, 140, 140), 12, 52, 10, a=0.55)
    if i >= 10:
        pile(ctx, ax, ay, 100, 5, [(74, 78, 94), (110, 114, 130), (46, 48, 64)], 10 + 6 * (i - 10), seed=12, layer='back')


S_ = None


def hit_boxes():
    return {
        'attack1': dict(hit=[2, 4], box=[6, -88, 70, 88]),
        'attack2': dict(hit=[1, 5], box=[8, -66, 118, 50]),
        'attack3': dict(hit=[4, 6], box=[-74, -54, 152, 56]),
        'cast': dict(rel=4, muzzle_src=('sword', (0, 66))),
    }


def spec():
    fns = dict(idle=idle_pose, walk=walk_pose, windup1=wind1, attack1=atk1, windup2=wind2, attack2=atk2, windup3=wind3,
               attack3=atk3, cast=cast, hurt=hurt, phase=phase, intro=intro, death=death)
    hb = hit_boxes()
    return {k: dict(pose=v, **hb.get(k, {})) for k, v in fns.items()}


def build():
    return make(spec(), fxhook)
