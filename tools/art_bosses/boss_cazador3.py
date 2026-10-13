import math
import numpy as np
from kit import *
from shapes import *
from anim import *
from fxlib import *
from boss_common import *

COSMOS = auto('#2c2250', shadow=(8, 4, 38), warm=(130, 90, 180), n=6, dk=0.3)
TENT = auto('#43305c', shadow=(10, 6, 44), warm=(170, 120, 200), n=6, dk=0.28)
FLESH = auto('#9a8eb6', shadow=(46, 34, 104), warm=(240, 220, 236), n=6, dk=0.3, boost=1.15)
BONE = auto('#d8ccd2', shadow=(70, 44, 100), warm=(255, 244, 240), n=6, dk=0.3)
SUCK = auto('#d8b8c8', shadow=(90, 40, 90), warm=(255, 230, 230), n=6, dk=0.3)
VOID = ramp((6, 2, 14), (18, 6, 30), (60, 20, 70), 6)
STARG = [(90, 24, 70), (180, 60, 130), (250, 140, 190), (255, 214, 232), (255, 255, 255)]
BLOODG = [(60, 6, 24), (150, 16, 50), (232, 44, 90), (255, 160, 170), (255, 244, 244)]
MATS = {'cosmos': Mat(COSMOS, glow=STARG, texamt=0.8, gain=0.95), 'tent': Mat(TENT, glow=STARG, texamt=0.6, gain=1.0),
        'flesh': Mat(FLESH, glow=BLOODG, texamt=0.5, gain=1.1), 'bone': Mat(BONE, glow=BLOODG, gain=1.2, texamt=0.5),
        'suck': Mat(SUCK, gain=1.1, texamt=0.4), 'void': Mat(VOID, glow=BLOODG, gain=0.5, texamt=0.2),
        'rift': Mat(auto('#a01838', shadow=(40, 6, 60), warm=(255, 160, 160)), glow=BLOODG, texamt=0.2)}


def stars(p, dens=0.012, seed=1, lo=0.3):
    def f(ctx):
        rng = np.random.default_rng(seed + p.seed)
        E = ctx['E']; mask = ctx['mask']
        r = rng.random(E.shape) < dens / 3.0
        v = lo + (1 - lo) * rng.random(E.shape)
        sel = r & mask
        E[sel] = np.maximum(E[sel], v[sel])
    return p.fn(f)


def build_parts():
    P = []

    def add(*a, **k):
        p = Part(*a, **k); P.append(p); return p
    add('root', None, (96, 156), ghost=True)
    # ---------------- capa de vacio (detras)
    cp = []
    c1 = add('cape1', 'root', (-18, -108), z=0.6, mat='cosmos', depth=7.0, noise=0.7, seed=1)
    c1.spl([(-8, -2), (6, -6), (14, 2), (14, 16), (12, 30), (4, 44), (-12, 46), (-24, 40), (-26, 24), (-18, 10)], per=6)
    c1.hatch(3.0, 80, v=0.3, w=0.5, jit=0.4)
    stars(c1, 0.02, 3)
    c2 = add('cape2', 'cape1', (-8, 40), z=0.6, mat='cosmos', depth=6.0, noise=0.7, seed=2)
    c2.poly([(16, -4), (-16, -4), (-26, 8), (-30, 22)] + rag(-30, 18, 34, 7, 14, 3, 1) + [(18, 12)])
    c2.hatch(3.0, 78, v=0.3, w=0.5, jit=0.4)
    stars(c2, 0.02, 4)
    c3 = add('cape3', 'cape2', (-6, 30), z=0.6, mat='cosmos', depth=4.5, noise=0.6, seed=3)
    c3.poly([(18, -4), (-18, -4), (-28, 8), (-32, 18)] + rag(-32, 18, 24, 6, 18, 5, 1) + [(18, 10)])
    c3.hatch(3.0, 76, v=0.3, w=0.5, jit=0.4)
    stars(c3, 0.02, 5)
    # ---------------- cadera / cuerpo
    hip = add('hip', 'root', (0, -62), z=4, mat='cosmos', depth=9.0, noise=0.8, seed=5)
    hip.spl([(-24, -8), (-10, -14), (12, -12), (26, -4), (28, 8), (14, 14), (0, 10), (-14, 14), (-28, 6)])
    hip.hatch(3.0, 90, v=0.3, w=0.5, jit=0.4)
    stars(hip, 0.02, 6)
    hip.cracks(4, 9, v=0.1, w=0.7, seed=7, emit=0.9)
    # ---------------- tentaculos
    xs = [(-25, 1.5, -0.3), (-14, 2.6, -0.2), (-3, 3.4, -0.1), (8, 4.6, 0.0), (19, 5.4, 0.05), (28, 6.0, 0.1)]
    for k, (x, z, dim) in enumerate(xs):
        a = add(f't{k}a', 'hip', (x, 6), z=z, mat='tent', depth=7.0, noise=0.7, seed=80 + k, dim=dim, tnoise=0.25)
        a.tube([(0, 0), (1.5, 10), (0, 21)], 8.4, 6.0)
        a.hatch(2.6, 90, v=0.3, w=0.5, jit=0.5)
        stars(a, 0.012, 90 + k)
        for j in range(3):
            a.line([(-6, 5 + j * 6), (6, 6 + j * 6)], 0.6, op='tex', v=0.14)
        b = add(f't{k}b', f't{k}a', (0, 21), z=z, mat='tent', depth=5.2, noise=0.6, seed=100 + k, dim=dim, tnoise=0.25)
        b.tube([(0, 0), (-1, 9), (1, 19)], 6.0, 3.8)
        b.hatch(2.6, 90, v=0.3, w=0.5, jit=0.5)
        for j in range(4):
            b.ell(3.2 - j * 0.2, 3 + j * 4.6, 1.3, 1.3, mat='suck', raise_=0.6, edge=0.1)
        c = add(f't{k}c', f't{k}b', (1, 19), z=z, mat='tent', depth=3.6, noise=0.5, seed=110 + k, dim=dim)
        c.tube([(0, 0), (1.5, 8), (5, 15), (10, 19)], 3.8, 0.6)
        for j in range(3):
            c.ell(2.6 + j * 1.8, 3 + j * 4.4, 0.95, 0.95, mat='suck', raise_=0.5, edge=0.1)
    # ---------------- torso
    to = add('torso', 'hip', (0, -4), z=6, mat='cosmos', depth=11.0, noise=1.0, nscale=3.5, seed=20, tnoise=0.3)
    to.spl([(-22, -2), (-28, -16), (-26, -34), (-16, -48), (0, -54), (16, -48), (26, -34), (28, -16), (22, -2)])
    to.hatch(3.0, 84, v=0.3, w=0.5, jit=0.4)
    stars(to, 0.03, 21)
    # grieta del pecho
    to.spl([(3, -18), (8, -28), (4, -40), (-1, -30), (0, -22)], mat='rift', raise_=-1.4)
    to.spl([(4, -22), (6.4, -28), (4, -35), (1.5, -29)], op='emit', v=0.9, soft=0.8)
    to.cracks(7, 11, v=0.1, w=0.7, seed=22, emit=1.0)
    for k in range(7):
        to.poly([(-4 + k * 0.5 - 1, -18 + (k % 2) * 2), (-4 + k * 0.5 + 1, -18 + (k % 2) * 2), (-3 + k * 0.5, -23 - k * 3)], mat='bone', raise_=0.5, edge=0.1) if False else None
    # costillas de hueso
    for k in range(4):
        to.tube(bez((-4, -12 - k * 7), (10, -16 - k * 7), (22, -10 - k * 7), n=9), 1.6, 1.2, mat='bone', raise_=0.9, edge=0.1)
    to.blotch('flesh', 0.72, 3.4, 23)
    # collar de espinas
    for k in range(7):
        a = -2.8 + k * 0.45
        to.poly([(12 * math.cos(a) - 2, -50 + 6 * math.sin(a)), (12 * math.cos(a) + 2, -50 + 6 * math.sin(a)), (14 * math.cos(a), -58 + 5 * math.sin(a) - 4)], mat='bone', raise_=0.7, edge=0.1)
    # ---------------- cabeza
    hd = add('head', 'torso', (2, -52), z=12, mat='flesh', depth=8.0, noise=0.5, seed=30, tnoise=0.15)
    hd.spl([(-12, -4), (-14, -18), (-8, -30), (4, -34), (14, -28), (19, -16), (19, -6), (13, 4), (3, 9), (-6, 7)])
    hd.line([(-8, -28), (-3, -12), (-6, 2)], 0.8, op='tex', v=0.1)
    hd.line([(8, -30), (13, -20), (15, -8)], 0.8, op='tex', v=0.1)
    hd.spl([(8, -4), (17, -3), (16, 3), (9, 6)], mat='void', raise_=-0.8)
    hd.spl([(9, -2), (15.5, -1.6), (15, 1.6), (10, 3.6)], op='emit', v=0.8, soft=0.7)
    for k in range(5):
        hd.poly([(9.5 + k * 1.4, -3), (10.8 + k * 1.4, -3), (10.2 + k * 1.4, 1)], mat='bone', raise_=0.5, edge=0.1)
    hd.cracks(4, 8, v=0.1, w=0.6, seed=31, emit=0.9)
    hd.blotch('bone', 0.74, 2.8, 32)
    cr = add('crown', 'head', (0, -30), z=11, mat='bone', depth=3.0, noise=0.3, seed=33)
    for (x1, y1, x2, y2, x3, y3) in ((-8, 2, -16, -16, -12, -32), (-2, 0, -4, -20, 2, -36), (5, 0, 10, -18, 20, -30), (11, 2, 20, -10, 30, -14), (-12, 4, -26, -6, -32, -18)):
        cr.tube([(x1, y1), (x2, y2), (x3, y3)], 2.8, 0.5, mat='bone', raise_=0.6, edge=0.1)
    cr.poly([(-12, 6), (14, 6), (12, -2), (0, -4), (-10, -2)])
    cr.tube([(-6, -14), (-12, -20), (-18, -22)], 1.6, 0.4, mat='bone', raise_=0.6)
    cr.tube([(8, -14), (14, -22), (22, -24)], 1.6, 0.4, mat='bone', raise_=0.6)
    for nm, par, at, sd in (('beard1', 'head', (4, 4), 36), ('beard2', 'head', (10, 5), 37), ('beard3', 'head', (-2, 5), 38)):
        bd = add(nm, par, at, z=11.5, mat='tent', depth=2.6, noise=0.3, seed=sd)
        bd.tube([(0, 0), (1, 8), (0, 15), (2, 22)], 3.0, 0.6)
        for j in range(3):
            bd.ell(1.4, 5 + j * 5.5, 0.8, 0.8, mat='suck', raise_=0.4)
    # ---------------- hombros creciente + brazos
    for nm, x, z, dim in (('b', -22, 3, -0.2), ('f', 22, 11, 0.0)):
        sh = add('sh_' + nm, 'torso', (x, -46), z=z, mat='bone', depth=6.0, noise=0.3, seed=44, dim=dim)
        sh.ell(0, 0, 14, 14)
        sh.ell(-5 if nm == 'f' else -4, -5, 11.5, 11.5, op='sub')
        sh.poly([(-6, -12), (-10, -22), (-2, -14)], mat='bone', raise_=0.6, edge=0.1)
        sh.poly([(0, -13), (0, -26), (6, -12)], mat='bone', raise_=0.6, edge=0.1)
        sh.ell(4, 4, 3.0, 3.0, mat='rift', raise_=0.6, edge=0.1)
        sh.ell(4, 4, 2.2, 2.2, op='emit', v=0.9, soft=0.3)
        sh.cracks(2, 6, v=0.1, w=0.5, seed=45)
    for nm, x, z, dim in (('b', -16, 3, -0.2), ('f', 18, 10, 0.0)):
        ua = add('uarm_' + nm, 'torso', (x, -42), z=z, mat='flesh', depth=5.4, noise=0.4, seed=40, dim=dim, tnoise=0.15)
        ua.tube([(0, 0), (2, 14), (1, 28)], 7.0, 5.2)
        ua.line([(-1, 4), (1, 26)], 0.8, op='tex', v=0.1)
        ua.spl([(-5, 18), (5.6, 18), (5, 28), (-4.4, 28)], mat='cosmos', raise_=0.7, edge=0.1)
        ua.cracks(2, 8, v=0.1, w=0.5, seed=46, emit=0.8)
        fa = add('farm_' + nm, 'uarm_' + nm, (1, 28), z=z, mat='flesh', depth=4.6, noise=0.4, seed=41, dim=dim, tnoise=0.15)
        fa.tube([(0, 0), (0.5, 16), (0.5, 32)], 5.4, 4.0)
        fa.line([(0, 3), (0.5, 30)], 0.8, op='tex', v=0.1)
        fa.cracks(2, 8, v=0.1, w=0.5, seed=47, emit=0.8)
        hn = add('hand_' + nm, 'farm_' + nm, (0.5, 32), z=z + 0.2, mat='flesh', depth=3.4, noise=0.3, seed=42, dim=dim)
        hn.spl([(-5, -2), (5, -2), (6.5, 4), (4, 9), (-4, 9), (-6.5, 4)])
        for k in range(5):
            xx = -4.4 + k * 2.2
            ln = 26 - abs(k - 2) * 2.6
            hn.tube([(xx, 7), (xx * 1.3 + 0.6, 7 + ln * 0.35), (xx * 1.8 + 1.4, 7 + ln * 0.7), (xx * 2.2 + 3.4, 7 + ln)], 1.9, 0.4, mat='bone', raise_=0.5, edge=0.1)
    return P


def make(anims, fxhook):
    return Boss('cazador3', (192, 160), (96, 156), (60, 140), build_parts(), MATS, anims, fxhook,
                outline=(8, 2, 16), rim=(255, 90, 140), rimk=0.4, dis_col=(255, 120, 190), seed=71, scale=0.8)


# ====================================================================== animaciones
def PZ(*ds):
    return merge(*ds)


def A(uf, ff, hf, ub, fb, hb):
    return {'uarm_f': uf, 'farm_f': ff, 'hand_f': hf, 'uarm_b': ub, 'farm_b': fb, 'hand_b': hb}


GROUND = {0: (6, -10, 24), 1: (-6, 8, 30), 2: (4, -6, 26), 3: (-4, 8, 28), 4: (8, -6, 20), 5: (-4, 10, 24)}


def tent(f, n, amp=1.0, ph=0.0, ground=1.0, over=None, spd=1):
    """ondulacion de los 6 tentaculos; over: {k: (a,b,c)} fija los angulos (sin ondulacion)."""
    d = {}
    for k in range(6):
        if over and k in over:
            a, b, c = over[k]
            d[f't{k}a'] = a; d[f't{k}b'] = b; d[f't{k}c'] = c
            continue
        g = GROUND[k]
        w = S(f, n, ph + k * 0.17, spd)
        d[f't{k}a'] = g[0] * ground + amp * 5 * w
        d[f't{k}b'] = g[1] * ground + amp * 8 * S(f, n, ph + k * 0.17 + 0.12, spd)
        d[f't{k}c'] = g[2] * ground + amp * 14 * S(f, n, ph + k * 0.17 + 0.24, spd)
    return d


def cape(f, n, amp=1.0, base=0.0, ph=0.0):
    return {'cape1': base * 0.5 + amp * 2.6 * S(f, n, ph), 'cape2': base + amp * 4.5 * S(f, n, ph + 0.12), 'cape3': base * 1.2 + amp * 6.0 * S(f, n, ph + 0.25),
            'crown': amp * 1.5 * S(f, n, ph + 0.1), 'beard1': amp * 4 * S(f, n, ph + 0.3), 'beard2': amp * 4 * S(f, n, ph + 0.42), 'beard3': amp * 4 * S(f, n, ph + 0.55)}


STAND = PZ(A(-6, -4, 6, 8, -4, 4), {'torso': 1, 'head': -1})


def idle_pose(f):
    b = S(f, 6)
    return PZ(STAND, {'root.y': -5 - 1.6 * b, 'torso': 1.4 * b, 'head': -1.6 * b, 'uarm_f': -1.4 * b, 'uarm_b': 1.2 * b, 'hand_f': 3 * b, 'hand_b': -3 * b},
              tent(f, 6, 1.0, 0.0), cape(f, 6, 1.0, 1.5))


def walk_pose(f):
    ph = 2 * math.pi * f / 8
    s = math.sin(ph); c = math.cos(ph)
    return PZ(STAND, {'root.y': -6 - 2.5 * abs(s), 'torso': 5 + 1.5 * c, 'head': -2 + 2 * c, 'uarm_f': -14 + 8 * s, 'uarm_b': 16 - 8 * s, 'hand_f': 6 * c},
              tent(f, 8, 2.2, 0.0, 0.9, spd=1), cape(f, 8, 1.8, 6))


WIND1 = [(0, STAND),
         (1, PZ(A(-60, -40, 10, 12, -8, 4), {'torso': -2, 'head': -4, 'root.y': -6})),
         (2, PZ(A(-120, -30, 14, 16, -10, 4), {'torso': -6, 'head': -8, 'root.y': -8})),
         (3, PZ(A(-122, -20, 18, 18, -10, 4), {'torso': -10, 'head': -12, 'root.y': -10, 'root.x': -3})),
         (4, PZ(A(-128, -16, 20, 20, -10, 4), {'torso': -12, 'head': -14, 'root.y': -11, 'root.x': -4}))]
wind1k = K(WIND1)


def wind1(f):
    return PZ(wind1k(f), tent(f, 5, 1.2, 0.0), cape(f, 5, 0.8, 3 + f))


ATK1 = [(0, WIND1[-1][1], 'sm'),
        (1, PZ(A(-120, -30, 14, 16, -10, 4), {'torso': 2, 'head': -6, 'root.y': -8, 'root.x': 3}), 'snap'),
        (2, PZ(A(-64, -16, 6, 16, -10, 4), {'torso': 14, 'head': 0, 'root.y': -6, 'root.x': 8}), 'snap'),
        (3, PZ(A(-24, -4, 2, 14, -10, 4), {'torso': 22, 'head': 4, 'root.y': -5, 'root.x': 12}), 'snap'),
        (4, PZ(A(-16, 0, 0, 14, -10, 4), {'torso': 24, 'head': 5, 'root.y': -4, 'root.x': 12}), 'out'),
        (5, PZ(A(-14, -2, 2, 12, -8, 4), {'torso': 18, 'head': 3, 'root.y': -5, 'root.x': 9}), 'sm'),
        (6, PZ(A(-10, -4, 4, 10, -6, 4), {'torso': 8, 'root.y': -5, 'root.x': 4}), 'sm'),
        (7, STAND, 'sm')]
atk1k = K(ATK1)


def atk1(f):
    return PZ(atk1k(f), tent(f, 8, 1.2, 0.0), cape(f, 8, 1.4, 8 - f * 0.5, 0.2))


FRONT_BACK = {4: (14, 30, 20), 5: (22, 40, 30)}
WIND2 = [(0, STAND),
         (1, PZ(A(-20, -20, 0, 20, -10, 4), {'torso': -4, 'head': -3, 'root.y': -6})),
         (2, PZ(A(0, -30, 0, 36, -10, 4), {'torso': -8, 'head': -6, 'root.y': -5, 'root.x': -3})),
         (3, PZ(A(10, -36, 0, 50, -10, 4), {'torso': -12, 'head': -8, 'root.y': -4, 'root.x': -6})),
         (4, PZ(A(14, -40, 0, 56, -10, 4), {'torso': -14, 'head': -10, 'root.y': -4, 'root.x': -8}))]
wind2k = K(WIND2)


def wind2(f):
    t = f / 4.0
    ov = {4: (14 + 40 * t, 30 + 30 * t, 20 + 20 * t), 5: (22 + 44 * t, 40 + 30 * t, 30 + 20 * t)}
    return PZ(wind2k(f), tent(f, 5, 0.8, 0.0, 1.0, over=ov), cape(f, 5, 0.5, -2 - f * 2, 0.3))


ATK2 = [(0, WIND2[-1][1], 'sm'),
        (1, PZ(A(-30, -30, 0, -20, -20, 0), {'torso': 12, 'head': 4, 'root.y': -6, 'root.x': 8}), 'snap'),
        (2, PZ(A(-40, -24, 0, -30, -24, 0), {'torso': 22, 'head': 6, 'root.y': -6, 'root.x': 12}), 'snap'),
        (3, PZ(A(-44, -22, 0, -34, -22, 0), {'torso': 24, 'head': 8, 'root.y': -6, 'root.x': 14}), 'out'),
        (4, PZ(A(-40, -22, 0, -30, -22, 0), {'torso': 22, 'head': 6, 'root.y': -6, 'root.x': 14}), 'sm'),
        (5, PZ(A(-30, -20, 0, -20, -20, 0), {'torso': 16, 'head': 4, 'root.y': -6, 'root.x': 10}), 'sm'),
        (6, PZ(A(-16, -8, 2, 0, -10, 4), {'torso': 8, 'root.y': -5, 'root.x': 5}), 'sm'),
        (7, STAND, 'sm')]
atk2k = K(ATK2)


def atk2(f):
    spear = {4: (-84, -4, -2), 5: (-72, -2, 0)}
    if f > 4.5:
        k = clamp01((f - 4.5) / 2.5)
        ov = {4: (-84 * (1 - k) + 14 * k, -4 * (1 - k) + 30 * k, -2 * (1 - k) + 20 * k), 5: (-72 * (1 - k) + 22 * k, -2 * (1 - k) + 40 * k, 30 * k)}
    elif f < 1:
        ov = {4: (54 * (1 - f) - 84 * f, 60 * (1 - f) - 4 * f, 40 * (1 - f)), 5: (66 * (1 - f) - 72 * f, 70 * (1 - f) - 2 * f, 50 * (1 - f))}
    else:
        ov = spear
    return PZ(atk2k(f), tent(f, 8, 1.2, 0.0, 1.0, over=ov), cape(f, 8, 1.6, -14 + f * 1.5, 0.0))


WIND3 = [(0, STAND),
         (1, PZ(A(-30, -20, 0, -20, -20, 0), {'torso': 4, 'head': 2, 'root.y': 0})),
         (2, PZ(A(-110, -20, 10, -100, -20, 10), {'torso': -4, 'head': -8, 'root.y': -12})),
         (3, PZ(A(-118, -14, 14, -114, -14, 14), {'torso': -8, 'head': -14, 'root.y': -20})),
         (4, PZ(A(-126, -10, 16, -122, -10, 16), {'torso': -10, 'head': -18, 'root.y': -24})),
         (5, PZ(A(-130, -8, 18, -126, -8, 18), {'torso': -12, 'head': -20, 'root.y': -26}))]
wind3k = K(WIND3)


def wind3(f):
    t = clamp01(f / 4.0)
    ov = {k: (-20 * t + GROUND[k][0] * (1 - t), -6 * t + GROUND[k][1] * (1 - t), -30 * t + GROUND[k][2] * (1 - t)) for k in range(6)}
    return PZ(wind3k(f), tent(f, 6, 1.4, 0.0, 1.0, over=ov), cape(f, 6, 1.0, 6 - f, 0.3))


ATK3 = [(0, WIND3[-1][1], 'sm'),
        (1, PZ(A(-128, -8, 14, -124, -8, 14), {'torso': 0, 'head': -16, 'root.y': -30}), 'sm'),
        (2, PZ(A(-90, -10, 4, -86, -10, 4), {'torso': 20, 'head': 2, 'root.y': -16}), 'in'),
        (3, PZ(A(-30, -4, 0, -26, -4, 0), {'torso': 34, 'head': 8, 'root.y': -4, 'root.x': 4}), 'in'),
        (4, PZ(A(-12, 2, -4, -8, 2, -4), {'torso': 38, 'head': 10, 'root.y': 2, 'root.x': 6}), 'snap'),
        (5, PZ(A(-8, 4, -4, -4, 4, -4), {'torso': 40, 'head': 10, 'root.y': 3, 'root.x': 6}), 'sm'),
        (6, PZ(A(-8, 4, -2, -4, 4, -2), {'torso': 34, 'head': 8, 'root.y': 2, 'root.x': 5}), 'sm'),
        (7, PZ(A(-10, 0, 2, 0, 0, 2), {'torso': 18, 'head': 2, 'root.y': -3, 'root.x': 2}), 'sm'),
        (8, STAND, 'sm')]
atk3k = K(ATK3)


def atk3(f):
    t = clamp01(f / 3.0)
    up = 1 - clamp01((f - 3.0) / 1.5)
    ov = {k: ((-20 * up + 40 * (1 - up)) * 1.0 + (0 if up > 0 else (k - 2.5) * 6), -6 * up + 10 * (1 - up), -30 * up + 50 * (1 - up)) for k in range(6)}
    if f >= 6:
        w = clamp01((f - 6) / 2.0)
        ov = {k: (ov[k][0] * (1 - w) + GROUND[k][0] * w, ov[k][1] * (1 - w) + GROUND[k][1] * w, ov[k][2] * (1 - w) + GROUND[k][2] * w) for k in range(6)}
    return PZ(atk3k(f), tent(f, 9, 1.4, 0.0, 1.0, over=ov), cape(f, 9, 1.8, -10 if f in (1, 2, 3) else 6, 0.0))


CAST = K([(0, STAND),
          (1, PZ(A(-30, -30, 0, -20, -30, 0), {'torso': -2, 'head': -6, 'root.y': -7})),
          (2, PZ(A(-80, -30, 10, -70, -30, 10), {'torso': -5, 'head': -12, 'root.y': -9}), 'sm'),
          (3, PZ(A(-100, -24, 14, -90, -24, 14), {'torso': -8, 'head': -16, 'root.y': -11}), 'sm'),
          (4, PZ(A(-96, -20, 16, -86, -20, 16), {'torso': -4, 'head': -8, 'root.y': -10, 'root.x': 2}), 'snap'),
          (5, PZ(A(-86, -16, 14, -76, -16, 14), {'torso': -2, 'head': -4, 'root.y': -9}), 'out'),
          (6, PZ(A(-40, -10, 6, -30, -10, 6), {'torso': 0, 'root.y': -7}), 'sm'),
          (7, STAND, 'sm')])


def cast(f):
    return PZ(CAST(f), tent(f, 8, 1.4, 0.0), cape(f, 8, 1.6, 4, 0.0))


def hurt(f):
    d = [PZ(A(-14, 14, 0, 20, 10, 0), {'torso': -12, 'head': -12, 'root.x': -4, 'root.y': -4, 'tint': ((255, 255, 255), 0.5)}),
         PZ(A(-10, 6, 4, 12, 0, 4), {'torso': -6, 'head': -6, 'root.x': -2, 'root.y': -5, 'tint': ((255, 255, 255), 0.2)})][int(f)]
    return PZ(d, tent(f, 2, 2.0), cape(f, 2, 1, 6 + 4 * (1 - f)))


PHASE = K([(0, STAND),
           (1, PZ(A(14, -20, 0, 20, -20, 0), {'torso': 10, 'head': 8, 'root.y': -3}), 'sm'),
           (2, PZ(A(30, -10, 4, 36, -10, 4), {'torso': 16, 'head': 12, 'root.y': -2}), 'sm'),
           (3, PZ(A(-40, -20, 8, -30, -20, 8), {'torso': 0, 'head': -4, 'root.y': -10}), 'out'),
           (4, PZ(A(-120, -10, 20, -116, -10, 20), {'torso': -14, 'head': -26, 'root.y': -22, 'torso.sx': 1.06, 'torso.sy': 1.05}), 'snap'),
           (5, PZ(A(-130, -6, 24, -126, -6, 24), {'torso': -18, 'head': -30, 'root.y': -24, 'torso.sx': 1.08, 'torso.sy': 1.07}), 'sm'),
           (6, PZ(A(-130, -6, 24, -126, -6, 24), {'torso': -18, 'head': -28, 'root.y': -23, 'torso.sx': 1.07, 'torso.sy': 1.06}), 'sm'),
           (7, PZ(A(-96, -14, 12, -90, -14, 12), {'torso': -6, 'head': -14, 'root.y': -14}), 'in'),
           (8, PZ(A(-30, -8, 4, -22, -8, 4), {'torso': 0, 'head': -4, 'root.y': -7}), 'snap'),
           (9, STAND, 'sm')])


def phase(f):
    p = PHASE(f)
    if 4 <= f <= 7:
        p['tint'] = ((255, 110, 150), 0.22 * (1 - abs(f - 5.5) / 2.0))
    p['root.x'] = p.get('root.x', 0) + (1.4 if (f in (5, 6) and int(f) % 2) else (-1.4 if f in (5, 6) else 0))
    amp = 3.0 if 3 <= f <= 8 else 1.2
    return PZ(p, tent(f, 10, amp, 0.0, 1.0, spd=2 if 3 <= f <= 8 else 1), cape(f, 10, 2.6, -8 if 3 <= f <= 7 else 4, 0.0))


def intro(f):
    i = int(f)
    up = clamp01((f - 8) / 4.0)
    d = clamp01((f - 3) / 7.0)
    p = PZ(STAND, {'root.y': -5 - 10 * (1 - up), 'head': -10 * (1 - up) + (-14 if 11 <= i <= 12 else 0), 'torso': 8 * (1 - up) - (6 if 11 <= i <= 12 else 0)},
           A(-6 - 80 * (1 - up) * 0 + (-60 if 11 <= i <= 12 else 0), -4, 6, 8 + 20 * (1 - up), -4, 4),
           tent(f, 14, 2.4 * (1 - up) + 1.0, 0.0, 0.6 + 0.4 * up), cape(f, 14, 1.8, 8 * (1 - up)))
    p['dis'] = max(0.0, (1 - d) * 1.12) if i >= 3 else 1.2
    p['dis_dir'] = 1.0
    if i < 3:
        p['clip'] = (0, 0, 0, 0)
    return p


DEATH = K([(0, PZ(A(-14, 14, 0, 20, 10, 0), {'torso': -12, 'head': -12, 'root.x': -4, 'root.y': -4, 'tint': ((255, 255, 255), 0.5)}), 'out'),
           (1, PZ(A(-40, 10, 0, -20, 10, 0), {'torso': -8, 'head': -16, 'root.x': -5, 'root.y': -8, 'tint': ((255, 255, 255), 0.2)}), 'sm'),
           (2, PZ(A(-100, 0, 10, -90, 0, 10), {'torso': -14, 'head': -26, 'root.x': -4, 'root.y': -14, 'tint': ((255, 255, 255), 0.0)}), 'sm'),
           (3, PZ(A(-130, -6, 14, -120, -6, 14), {'torso': -16, 'head': -32, 'root.x': -2, 'root.y': -18}), 'sm'),
           (4, PZ(A(-90, -20, 8, -80, -20, 8), {'torso': -4, 'head': -16, 'root.x': 0, 'root.y': -12}), 'sm'),
           (5, PZ(A(-40, -30, 0, -30, -30, 0), {'torso': 10, 'head': 6, 'root.x': 2, 'root.y': -4}), 'sm'),
           (6, PZ(A(-10, -20, -4, 0, -20, -4), {'torso': 22, 'head': 18, 'root.x': 4, 'root.y': 2}), 'sm'),
           (7, PZ(A(6, -6, -6, 14, -6, -6), {'torso': 30, 'head': 24, 'root.x': 6, 'root.y': 6}), 'in'),
           (13, PZ(A(14, 0, -6, 20, 0, -6), {'torso': 36, 'head': 28, 'root.x': 8, 'root.y': 10}), 'lin')])


def death(f):
    p = DEATH(f)
    d = clamp01((f - 5.0) / 7.0)
    if d > 0:
        p['dis'] = d * 1.12
        p['dis_dir'] = -1.0
    amp = 3.0 if f < 8 else 1.0
    p.update(tent(f, 14, amp, 0.0, 1.0 - 0.6 * clamp01((f - 5) / 5), spd=2))
    p.update(cape(f, 14, 1.4, 6 + f))
    p['crown.y'] = 0 if f < 6 else -4 * clamp01((f - 6) / 4)
    return p


# ====================================================================== efectos
EYES = [('head', (7, -18), 4.4, 3.0, 0.0), ('head', (-4, -24), 2.8, 2.0, 0.3), ('head', (12, -27), 2.6, 1.9, 0.6), ('head', (-9, -14), 2.2, 1.7, 0.15),
        ('head', (15, -12), 2.0, 1.5, 0.45), ('head', (2, -30), 1.8, 1.4, 0.8), ('torso', (3, -31), 7.0, 4.4, 0.5), ('sh_f', (3, 3), 2.2, 1.8, 0.2),
        ('farm_f', (0.5, 14), 2.2, 1.8, 0.7), ('farm_b', (0.5, 14), 2.0, 1.6, 0.4), ('sh_b', (3, 3), 2.0, 1.6, 0.9)]


def blink(ctx, ph):
    i = ctx.i
    c = ((i * 0.37 + ph * 7) % 3.0)
    return 0.9 if c < 0.18 else 0.0


def draw_eyes(ctx, lid=None, mult=1.0, show=None):
    for k, (bone, pt, rx, ry, ph) in enumerate(EYES):
        if show is not None and k not in show:
            continue
        x, y = ctx.anchor(bone, pt)
        l = blink(ctx, ph) if lid is None else lid
        s = ctx.boss.scale
        col = (255, 50, 70) if k != 6 else (255, 90, 90)
        eye(ctx.fx, x, y, rx * s * mult, ry * s * mult, col, (30, 4, 20), 0.6, 1.0, 'front', l, 0.45)


def halo(ctx, r=30, a=1.0, crack=0.0, spin=0.0):
    fx, i = ctx.fx, ctx.i
    hx, hy = ctx.anchor('head', (0, -14))
    hx -= 3; hy -= 4
    s = ctx.boss.scale
    R = r * s
    fx.glow(hx, hy, R * 1.9, (255, 30, 60), 0.42 * a)
    # espinas alrededor
    for k in range(18):
        ang = spin + k * 6.283 / 18
        l = R * (0.28 + 0.14 * ((k * 7) % 3))
        p1 = (hx + math.cos(ang - 0.07) * R, hy + math.sin(ang - 0.07) * R)
        p2 = (hx + math.cos(ang + 0.07) * R, hy + math.sin(ang + 0.07) * R)
        p3 = (hx + math.cos(ang) * (R + l), hy + math.sin(ang) * (R + l))
        fx.poly([p1, p3, p2], (140, 14, 40), 0.9 * a, 'back')
    fx.ell(hx, hy, R + 2, R + 2, (70, 6, 28), a, 'back')
    fx.ell(hx, hy, R, R, (176, 22, 50), a, 'back')
    fx.ell(hx - R * 0.12, hy - R * 0.12, R * 0.84, R * 0.84, (222, 52, 68), a, 'back')
    fx.ell(hx - R * 0.26, hy - R * 0.26, R * 0.48, R * 0.48, (244, 96, 96), a * 0.85, 'back')
    for (cx_, cy_, rr) in ((0.34, 0.2, 0.2), (-0.1, 0.5, 0.15), (0.5, -0.3, 0.12), (-0.45, 0.1, 0.1)):
        fx.ell(hx + R * cx_, hy + R * cy_, R * rr, R * rr, (140, 14, 40), a * 0.9, 'back')
    fx.ring(hx, hy, R + 5, R + 5, 1, (255, 90, 120), 0.7 * a, 'back')
    fx.ring(hx, hy, R + 9, R + 9, 1, (255, 60, 100), 0.4 * a, 'back', a0=(i * 40) % 360, a1=(i * 40) % 360 + 140)
    if crack > 0:
        rng = np.random.default_rng(5)
        for k in range(7):
            ang = rng.random() * 6.283
            pts = [(hx, hy)]
            x, y = hx, hy
            for j in range(5):
                ang += (rng.random() - 0.5) * 1.0
                x += math.cos(ang) * R * 0.22 * crack * 1.6; y += math.sin(ang) * R * 0.22 * crack * 1.6
                pts.append((x, y))
            fx.polyline(pts, 1, (20, 2, 14), 0.95 * a, 'back')
            fx.polyline(pts, 1, (255, 200, 200), 0.6 * a, 'back', mode='add')
    return hx, hy, R


def fxhook(ctx):
    n, i, fx, W = ctx.name, ctx.i, ctx.fx, ctx.W
    ax, ay = ctx.pivot
    rng = ctx.rng
    s = ctx.boss.scale
    claw = lambda f=None: ctx.anchor('hand_f', (6, 30)) if f is None else ctx.anchor_at(f, 'hand_f', (6, 30))
    r = 30; a = 1.0; crack = 0.0; lid = None; spin = i * 0.05
    show = None
    if n == 'phase':
        r = 30 + 18 * clamp01((i - 3) / 2.0) * (1 if i <= 7 else clamp01(1 - (i - 7) / 2.5))
        lid = 0.0
    if n == 'cast':
        r = 30 + 6 * (1 if 3 <= i <= 5 else 0)
    if n == 'intro':
        a = clamp01((i - 7) / 4.0); r = 30 * clamp01((i - 6) / 4.0) + 4
        lid = max(0.0, 1.0 - (i - 8) / 3.0) if i >= 8 else 1.0
        show = [k for k in range(len(EYES)) if k <= max(0, (i - 7) * 2)]
    if n == 'death':
        crack = clamp01((i - 2) / 5.0)
        a = 1.0 if i < 8 else max(0.0, 1.0 - (i - 8) / 4.0)
        lid = clamp01((i - 3) / 5.0) if i >= 3 else None
        show = [k for k in range(len(EYES)) if k < len(EYES) - max(0, (i - 5))]
    if n == 'hurt':
        lid = 0.55
    if a > 0.02:
        halo(ctx, r, a, crack, spin)
    # cuerpo: brillo de la grieta
    cx0, cy0 = ctx.anchor('torso', (3, -30))
    if n != 'death' or i < 8:
        fx.glow(cx0, cy0, 16 * s, (255, 40, 90), 0.4)
    if n not in ('death',) or i < 9:
        if n != 'intro' or i >= 7:
            draw_eyes(ctx, lid, 1.0, show)
    starfield(ctx, ax, ay - 70, 90, 130, 14, 8, i / 8.0, 0.9)
    if n == 'windup1':
        t = i / 4.0
        cx_, cy_ = claw()
        fx.glow(cx_, cy_, 8 + 12 * t, (255, 60, 100), 0.4 * t + 0.1)
        wisps(ctx, cx_, cy_ + 6, 14, 14, 6, [(255, 150, 190), (255, 235, 245)], t=t * 0.9, seed=8, rise=8)
    if n == 'attack1':
        trail(ctx, 'hand_f', (3, 34), (3, 12), 0, 4, (255, 235, 245), (170, 20, 70), steps=12, span=3.2, mid=(240, 70, 120), a=0.85)
        trail(ctx, 'hand_f', (-3, 30), (-3, 12), 0, 4, (255, 215, 235), (120, 10, 60), steps=12, span=3.2, a=0.6)
        if 3 <= i <= 6:
            cx_, cy_ = claw(3.4)
            tt = (i - 3) / 3.0
            gx = min(cx_, W - 6)
            dust(ctx, gx, ay, tt, (110, 70, 110), 12, 30, 10)
            shock(ctx, gx, ay, tt, (255, 110, 160), 42, 5)
            fx.glow(gx, ay - 4, 14 * (1 - tt * 0.5), (255, 80, 130), 0.8 * (1 - tt))
            if i == 3:
                fx.sparks(rng, gx, ay - 3, 14, 16, [(255, 255, 255), (255, 90, 140)], 'front', 8)
    if n == 'windup2':
        t = i / 4.0
        tx, ty = ctx.anchor('t5c', (10, 19))
        fx.glow(tx, ty, 8 + 12 * t, (255, 60, 100), 0.4 * t + 0.1)
        for k in range(4):
            fx.line((tx + 10 + k * 5, ty + (k - 1.5) * 2), (tx + 2, ty + (k - 1.5) * 1.5), 1, (255, 170, 210), 0.5 * t, 'front', mode='add')
    if n == 'attack2' and 1 <= i <= 6:
        t = clamp01((i - 1) / 5.0)
        for k in (4, 5):
            tx, ty = ctx.anchor(f't{k}c', (10, 19))
            hx_, hy_ = ctx.anchor(f't{k}a', (0, 0))
            fx.poly([(hx_, hy_ - 5), (tx + 4, ty), (hx_, hy_ + 5)], (170, 30, 110), 0.3 * (1 - t * 0.6), 'front', ss=2)
            fx.glow(tx, ty, 10, (255, 120, 170), 0.8 * (1 - t * 0.5))
            if 2 <= i <= 4 and k == 5:
                impact_star(ctx, min(W - 8, tx + 3), ty, (i - 2) / 2.0, (255, 210, 230), 14, 8)
        bx, by = ctx.anchor('torso', (14, -20))
        for k in range(6):
            yy = ay - 14 - k * 14
            x0 = bx - 14 - ((i * 9 + k * 17) % 18)
            fx.line((x0, yy), (x0 - 18 - 5 * k, yy), 1 + (k % 2), (240, 60, 130), 0.6 * (1 - t * 0.4), 'front')
        dust(ctx, ax + 6, ay, clamp01((i - 1) / 4.0), (110, 70, 110), 8, 20, 6, a=0.6)
    if n == 'windup3':
        t = i / 5.0
        rays(ctx, ax, ay - 2, t * 0.6, (230, 30, 80), 7, 6, 30, 0.18, 0.4 * t, 0.4, 'back')
        wisps(ctx, ax, ay - 3, 70, 6, 10, [(255, 70, 120)], t=t, seed=5, rise=30, a=0.7)
    if n == 'attack3':
        if 4 <= i <= 8:
            t = (i - 4) / 4.0
            gx = ax + 34
            ground_cracks(ctx, gx, ay + 1, t, (24, 4, 24), (255, 80, 140), 10, 72, 11)
            shock(ctx, gx, ay, t, (255, 120, 170), 86, 8, 2)
            dust(ctx, gx, ay, t, (110, 70, 110), 18, 50, 14, 3.2)
            if i <= 7:
                fx.glow(gx, ay - 6, 28 * (1 - t * 0.5), (255, 80, 130), 0.9 * (1 - t))
                for k in range(6):
                    px = gx - 44 + k * 18 + (k % 2) * 3
                    h = (48 + 16 * (k % 3)) * (1 - t * 0.6)
                    fx.poly([(px - 4, ay), (px + 1, ay - h), (px + 4, ay)], (230, 30, 90), 0.85, 'front', ss=2)
                    fx.poly([(px - 1.4, ay), (px + 1, ay - h * 0.92), (px + 1.8, ay)], (255, 190, 215), 0.9, 'front', ss=2)
    if n == 'cast':
        hx, hy = ctx.anchor('head', (7, -18))
        if 1 <= i <= 4:
            t = i / 4.0
            for k in range(6):
                ang = i * 0.9 + k * 1.05
                rr = 16 * (1 - t * 0.5) + 2
                px = hx + math.cos(ang) * rr; py = hy + math.sin(ang) * rr * 0.8
                fx.glow(px, py, 4, (255, 90, 140), 0.8)
                fx.dots([(px, py)], (255, 235, 245), 1.0, 'front')
            fx.glow(hx, hy, 10 + 12 * t, (255, 60, 100), 0.8)
        if i >= 4:
            tt = (i - 4) / 3.0
            for k in range(3):
                sx_ = hx + 6 + tt * (40 + k * 14)
                sy_ = hy + (k - 1) * 14 * tt + (k - 1) * 4
                if sx_ < W - 4:
                    fx.glow(sx_, sy_, 10, (255, 50, 100), 0.9)
                    fx.ell(sx_, sy_, 4.4, 4.4, (140, 12, 52), 1.0, 'front')
                    fx.ell(sx_ - 0.6, sy_ - 0.6, 3.0, 3.0, (240, 70, 110), 1.0, 'front')
                    fx.ell(sx_ - 1.2, sy_ - 1.2, 1.4, 1.4, (255, 220, 235), 1.0, 'front')
                    fx.polyline([(sx_ - 4, sy_), (sx_ - 14, sy_), (sx_ - 26, sy_)], 2, (230, 30, 90), 0.5, 'front')
    if n == 'phase':
        t = clamp01((i - 3) / 5.0)
        if 3 <= i <= 9:
            fx.glow(ax, ay - 76, 80 * t + 16, (255, 30, 90), 0.5 * (1 - abs(t - 0.5) * 1.2), rx=70 * t + 18, ry=80 * t + 18)
            rays(ctx, ax, ay - 80, t, (255, 90, 140), 18, 16, 96, 0.09, 0.45, i * 0.1, 'back')
            shock(ctx, ax, ay, clamp01((i - 4) / 5.0), (255, 100, 150), 74, 8, 2)
        if 4 <= i <= 8:
            starfield(ctx, ax, ay - 74, 120, 140, 40, 21, i / 6.0, 1.0)
            wisps(ctx, ax, ay - 70, 70, 100, 18, [(255, 120, 160), (255, 240, 245)], t=(i - 4) / 6.0, seed=21, rise=44, a=1.0)
    if n == 'death':
        if 2 <= i <= 9:
            cx1, cy1 = ctx.anchor('torso', (4, -26))
            for k in range(6):
                ang = rng.random() * 6.28
                fx.line((cx1, cy1), (cx1 + math.cos(ang) * 22, cy1 + math.sin(ang) * 22), 1, (255, 150, 190), 0.8, 'front')
        if 6 <= i:
            # esquirlas de la luna
            hx, hy = ctx.anchor('head', (0, -14))
            t = clamp01((i - 6) / 7.0)
            for k in range(10):
                ang = k * 0.63 + 0.3
                dx_ = math.cos(ang) * (16 + 22 * t) * 1.0; dy_ = math.sin(ang) * (14 + 10 * t) + 40 * t * t * (1 + (k % 3) * 0.4)
                px, py = hx + dx_, hy + dy_
                sh_ = 4.5 - 2 * t
                fx.poly([(px - sh_, py + sh_ * 0.6), (px + sh_ * 0.4, py - sh_), (px + sh_, py + sh_ * 0.5)], (200, 30, 62), 1 - t * 0.7, 'front', ss=2)
                fx.poly([(px - sh_ * 0.6, py + sh_ * 0.4), (px + sh_ * 0.3, py - sh_ * 0.6), (px + sh_ * 0.5, py + sh_ * 0.3)], (250, 110, 120), 1 - t * 0.7, 'front', ss=2)
        if i >= 8:
            t = clamp01((i - 8) / 5.0)
            starfield(ctx, ax, ay - 40 - 20 * t, 90, 100, 24, 31, i / 6.0, 1 - 0.4 * t)
            pool(ctx, ax + 6, ay - 1, 14 + 40 * t, 3 + 2 * t, [(60, 6, 34), (130, 14, 60), (200, 30, 90)], 0.95)
            for k in range(2 + int(14 * t)):
                fx.dots([(ax - 18 + k * 5 + 7 * math.sin(i + k), ay - 10 - k * 4 - 26 * t)], (255, 110, 170), 0.9, 'front', 2)
    if n == 'intro':
        intro_fx(ctx)


def intro_fx(ctx):
    i, fx, ax, ay = ctx.i, ctx.fx, ctx.pivot[0], ctx.pivot[1]
    t = i / 13.0
    # estrellas: el cielo se oscurece
    starfield(ctx, ax, ay - 80, 170, 150, 26, 77, t, 0.9)
    mid = (ax + 2, ay - 82)
    # grieta vertical
    o = clamp01((i - 1) / 5.0)
    ln = 70 * clamp01(i / 3.0) + 20 * o
    wd = 1 + 14 * o * (1 if i < 10 else max(0.0, 1 - (i - 9) / 4.0))
    if i < 13:
        pts = [(mid[0], mid[1] - ln)] + [(mid[0] + (wd * 0.5 + 1) * (1 if k % 2 else -1) * (0.4 + 0.6 * math.sin(k / 6.0 * math.pi)), mid[1] - ln + k * ln / 3.0) for k in range(1, 7)] + [(mid[0], mid[1] + ln)]
        left = [(mid[0] - (wd * 0.5) * math.sin(k / 8.0 * math.pi) - (1.5 if k % 2 else 0), mid[1] - ln + k * 2 * ln / 8.0) for k in range(9)]
        right = [(mid[0] + (wd * 0.5) * math.sin(k / 8.0 * math.pi) + (1.5 if k % 3 == 0 else 0), mid[1] - ln + k * 2 * ln / 8.0) for k in range(9)]
        fx.poly(left + right[::-1], (255, 70, 110), 0.95, 'back', ss=2)
        fx.poly([(x * 0.6 + mid[0] * 0.4, y) for x, y in left] + [(x * 0.6 + mid[0] * 0.4, y) for x, y in right[::-1]], (255, 235, 240), 0.9, 'back', ss=2)
        fx.glow(mid[0], mid[1], 30 + 20 * o, (255, 40, 90), 0.5, rx=14 + 30 * o, ry=ln)
    if 3 <= i <= 9:
        rays(ctx, mid[0], mid[1], 1.0, (255, 100, 150), 14, 6, 70 * o, 0.07, 0.35, i * 0.1, 'back', 'over')
    # tentaculos sombra asomando
    if 4 <= i <= 8:
        for k in range(3):
            xx = mid[0] - 20 + k * 20
            fx.poly([(xx - 3, ay), (xx + 1, ay - 20 - 10 * (i - 4) * (k % 2 + 1)), (xx + 4, ay)], (60, 36, 90), 0.9, 'back', ss=2)
    if 9 <= i <= 12:
        shock(ctx, ax, ay, clamp01((i - 9) / 3.0), (255, 110, 160), 70, 7, 2)
        dust(ctx, ax, ay, clamp01((i - 9) / 3.0), (110, 70, 110), 12, 40, 10, a=0.6)


def hit_boxes():
    return {
        'attack1': dict(hit=[2, 4], box=[8, -108, 86, 108]),
        'attack2': dict(hit=[1, 5], box=[10, -80, 136, 70]),
        'attack3': dict(hit=[4, 6], box=[-84, -66, 188, 66]),
        'cast': dict(rel=4, muzzle_src=('head', (10, -14))),
    }


def spec():
    fns = dict(idle=idle_pose, walk=walk_pose, windup1=wind1, attack1=atk1, windup2=wind2, attack2=atk2, windup3=wind3,
               attack3=atk3, cast=cast, hurt=hurt, phase=phase, intro=intro, death=death)
    hb = hit_boxes()
    return {k: dict(pose=v, **hb.get(k, {})) for k, v in fns.items()}


def build():
    return make(spec(), fxhook)
