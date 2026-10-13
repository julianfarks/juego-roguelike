"""bs_reina_escarcha: Reina de hielo con vestido de cristal, corona de caramhanos y cetro. Flota."""
import math
import numpy as np
from kit import *
from shapes import *
from anim import *
from fxlib import *

ICE = auto('#7cc2ea', shadow=(28, 36, 120), warm=(244, 252, 255), n=6, dk=0.26, lk=0.5, boost=1.24)
ICED = auto('#3c6cb0', shadow=(18, 20, 90), warm=(180, 230, 255), n=6, dk=0.26, lk=0.4)
SKIN = auto('#cfe0f0', shadow=(40, 52, 130), warm=(255, 252, 255), n=6, dk=0.34, lk=0.5, boost=1.15)
HAIR = auto('#e6f2fb', shadow=(60, 80, 170), warm=(255, 255, 255), n=6, dk=0.4, lk=0.4, boost=1.06)
CLOAK = auto('#2b4378', shadow=(12, 14, 70), warm=(130, 190, 250), n=6, dk=0.3, lk=0.35)
STEEL = auto('#8fa6c4', shadow=(30, 36, 100), warm=(255, 255, 255), n=6, dk=0.26, lk=0.5)
VOID = ramp((4, 8, 24), (10, 18, 44), (30, 52, 96), 6)
CYAN = [(10, 56, 110), (28, 130, 200), (86, 214, 250), (190, 250, 255), (255, 255, 255)]
MATS = {
    'ice': Mat(ICE, glow=CYAN, texamt=0.5, gain=1.35),
    'iced': Mat(ICED, glow=CYAN, texamt=0.5, gain=1.2),
    'skin': Mat(SKIN, texamt=0.25, gain=1.0),
    'hair': Mat(HAIR, texamt=0.5, gain=1.0),
    'cloak': Mat(CLOAK, glow=CYAN, texamt=0.7, gain=0.95),
    'steel': Mat(STEEL, glow=CYAN, texamt=0.45, gain=1.3),
    'void': Mat(VOID, gain=0.4),
    'gem': Mat(ICE, glow=CYAN, texamt=0.1),
}
ICEC = (120, 220, 255)


def shard(P, name, parent, at, z, mat, pts, **k):
    p = Part(name, parent, at, z=z, mat=mat, **k); P.append(p)
    p.poly(pts)
    return p


def wid(pts, k):
    return [(x * (1 + (k - 1) * min(1, max(0, (y - 2) / 30.0))), y) for x, y in pts]


def build_parts():
    P = []

    def add(*a, **k):
        p = Part(*a, **k); P.append(p); return p
    add('root', None, (96, 156), ghost=True)
    hip = add('hip', 'root', (0, -50), z=4, mat='iced', depth=4.0, noise=0.3, seed=5)
    hip.spl([(-8, -4), (0, -6), (9, -4), (10, 3), (0, 6), (-10, 3)])
    # ------------------------------------------------ capa trasera
    cp = add('cape1', 'hip', (-4, -6), z=0.5, mat='cloak', depth=5.0, noise=0.5, seed=1, tnoise=0.3)
    cp.poly([(-4, -26), (8, -26), (6, -10), (4, 14)] + rag(4, -24, 38, 7, 8, 3, 1) + [(-24, 14), (-18, -8)])
    cp.hatch(2.6, 82, v=0.28, w=0.6, jit=0.4)
    cp.cracks(3, 8, v=0.14, w=0.7, seed=4, emit=0.4)
    cp2 = add('cape2', 'cape1', (-12, 38), z=0.4, mat='cloak', depth=4.0, noise=0.5, seed=2, tnoise=0.3)
    cp2.poly([(14, -6), (-16, -6), (-22, 6)] + rag(-22, 16, 22, 6, 9, 6, 1) + [(18, 4)])
    cp2.hatch(2.6, 80, v=0.28, w=0.6, jit=0.4)
    # ------------------------------------------------ alas de hielo
    for nm, z, dim, at in (('b', 0.8, -0.25, (-6, -22)), ('f', 1.2, -0.1, (-4, -24))):
        w = add('wing_' + nm, 'hip', at, z=z, mat='ice', depth=5.0, noise=0.3, seed=7, dim=dim, tnoise=0.2)
        blades = [(-120, 46, 7), (-95, 56, 8), (-68, 62, 8), (-42, 54, 7), (-18, 40, 6)]
        for ang, ln, wd in blades:
            a = math.radians(ang)
            dx, dy = math.sin(a), -math.cos(a)
            px, py = -dy, dx
            w.poly([(px * wd * 0.5, py * wd * 0.5), (dx * ln * 0.5 + px * wd, dy * ln * 0.5 + py * wd), (dx * ln, dy * ln),
                    (dx * ln * 0.5 - px * wd * 0.8, dy * ln * 0.5 - py * wd * 0.8), (-px * wd * 0.5, -py * wd * 0.5)])
        w.ell(0, 0, 7, 7)
        w.hatch(4.0, 40, v=0.9, w=0.5, jit=0.3, seed=3)
        w.cracks(5, 12, v=0.1, w=0.7, seed=8, emit=0.55, branch=0.7)
    # ------------------------------------------------ falda de cristal
    sk2 = add('skirt2', 'hip', (-3, 0), z=2, mat='iced', depth=6.0, noise=0.5, seed=9, tnoise=0.3)
    WX = 1.22
    sk2.poly(wid([(-9, -2), (9, -2), (16, 10), (28, 26), (38, 44)] + [(40, 58), (30, 50), (26, 64), (18, 52), (10, 66), (2, 54), (-6, 68), (-14, 54), (-22, 66), (-30, 52), (-40, 60), (-42, 50)] + [(-36, 40), (-24, 22), (-14, 8)], WX))
    sk2.hatch(5.0, 82, v=0.85, w=0.5, jit=0.4, seed=11)
    sk2.cracks(3, 12, v=0.1, w=0.7, seed=12, emit=0.45)
    sk = add('skirt', 'hip', (0, 2), z=3, mat='ice', depth=7.0, noise=0.6, seed=13, tnoise=0.3)
    sk.poly(wid([(-9, -2), (9, -2), (14, 8), (21, 22), (28, 38), (33, 50)] + [(30, 56), (24, 50), (20, 62), (13, 52), (8, 60), (3, 52), (-3, 62), (-9, 52), (-16, 60), (-22, 50), (-28, 58), (-32, 52)] + [(-28, 38), (-20, 22), (-14, 8)], WX))
    sk.hatch(4.4, 84, v=0.88, w=0.5, jit=0.5, seed=14)
    sk.blotch('iced', 0.72, 3.0, 15, raise_=0.3)
    sk.cracks(4, 14, v=0.1, w=0.7, seed=16, emit=0.5, branch=0.8)
    sk.line(bez((0, 0), (-1, 24), (0, 50), n=9), 1.0, op='emit', v=0.5, soft=0.5)
    sk.ell(0, 6, 3.4, 3.4, mat='gem', raise_=1.0, edge=0.1)
    sk.ell(0, 6, 2.6, 2.6, op='emit', v=0.95, soft=0.4)
    for k, x in enumerate((-22, -12, 0, 12, 22)):
        ln = 30 - abs(x) * 0.35
        pt = add('petal%d' % k, 'skirt', (x, 22 + abs(x) * 0.35), z=4.5, mat='ice', depth=3.5, noise=0.3, seed=20 + k, tnoise=0.2)
        pt.poly([(-4.4, -4), (4.4, -4), (3.4, 6), (0.4, ln)] + [(-3.2, 6)])
        pt.line([(0, -2), (0.2, ln - 6)], 0.8, op='tex', v=0.96)
        pt.line([(0, 0), (0, ln * 0.7)], 0.9, op='emit', v=0.45, soft=0.4)
    # ------------------------------------------------ torso
    to = add('torso', 'hip', (0, -3), z=6, mat='ice', depth=6.0, noise=0.4, seed=30, tnoise=0.25)
    to.spl([(-6, 5), (-8, -4), (-7, -14), (-9, -22), (-5, -28), (6, -28), (10, -22), (8, -14), (9, -4), (6, 5)])
    to.hatch(4.0, 70, v=0.9, w=0.5, jit=0.4, seed=31)
    to.poly([(-6, 4), (6, 4), (3, -6), (0, -2), (-3, -6)], mat='iced', raise_=0.8, edge=0.1)
    to.spl([(-3, -12), (1, -18), (5, -12), (1, -6)], mat='gem', raise_=1.2, edge=0.1)
    to.spl([(-1.6, -12), (1, -16), (3.6, -12), (1, -8)], op='emit', v=0.95, soft=0.4)
    to.cracks(3, 8, v=0.1, w=0.6, seed=32, emit=0.5)
    # collar de cristal
    co = add('collar', 'torso', (0, -25), z=2.5, mat='ice', depth=3.5, noise=0.3, seed=33)
    for ang, ln, wd in ((-100, 18, 4.2), (-70, 26, 4.6), (-40, 22, 4.2), (-14, 14, 3.6), (-130, 12, 3.6)):
        a = math.radians(ang); dx, dy = math.sin(a), -math.cos(a)
        co.poly([(-dy * wd + 0, dx * wd), (dx * ln, dy * ln), (dy * wd, -dx * wd)])
    co.ell(0, 0, 8, 4)
    co.hatch(3.5, 60, v=0.9, w=0.5, jit=0.3, seed=34)
    # ------------------------------------------------ cabeza y cabello
    hr = add('hair', 'torso', (2, -30), z=5.2, mat='hair', depth=5.0, noise=0.5, seed=35, tnoise=0.3)
    hr.poly([(-5, -14), (3, -17), (9, -13), (6, -8), (2, 0), (-8, 6), (-14, 18), (-12, 30), (-8, 22), (-4, 12), (-2, 4), (-10, -4)])
    hr.hatch(2.2, 80, v=0.25, w=0.6, jit=0.5, seed=36)
    hr2 = add('hair2', 'hair', (-10, 22), z=5.1, mat='hair', depth=4.0, noise=0.5, seed=37, tnoise=0.3)
    hr2.poly([(-5, -6), (3, -6), (5, 6), (4, 20), (0, 36), (-3, 24), (-8, 30), (-9, 14), (-8, 2)])
    hr2.hatch(2.2, 82, v=0.25, w=0.6, jit=0.5, seed=38)
    hr3 = add('hair3', 'hair2', (-2, 30), z=5.0, mat='hair', depth=3.0, noise=0.5, seed=39, tnoise=0.3)
    hr3.poly([(-4, -4), (3, -4), (3, 10), (0, 22), (-3, 12), (-6, 14), (-5, 2)])
    hd = add('head', 'torso', (2, -30), z=11, mat='skin', depth=5.0, noise=0.2, seed=40, tnoise=0.1)
    hd.spl([(-6, 2), (-7, -6), (-4, -13), (3, -15.5), (8, -11), (9.5, -4), (8, 1), (5, 6), (1, 7.5), (-2, 6)])
    hd.spl([(-1, -7.4), (3.5, -8.4), (7.5, -6.8), (7.4, -4.0), (4, -3.4), (0.4, -4.6)], mat='void', raise_=-0.5)
    hd.ell(4.6, -5.8, 1.3, 1.3, op='emit', v=1.0, soft=0.3)
    hd.ell(4.6, -5.8, 1.5, 1.5, mat='gem')
    hd.line([(2, -10.4), (5, -11.4), (9, -9.6)], 0.9, op='tex', v=0.2)
    hd.line([(3, 2.6), (7, 2.2)], 0.8, op='tex', v=0.15)
    hd.poly([(8.5, -2), (10.6, 0.6), (8, 0.4)], mat='skin', raise_=0.8)
    hd.line([(-4, -10), (-5, -3)], 0.8, op='tex', v=0.35)
    cr = add('crown', 'head', (1, -14), z=12.5, mat='ice', depth=3.0, noise=0.3, seed=41)
    cr.poly([(-9, 3), (-9, -1), (-8, -4), (-6, 0), (-6.5, -9), (-4, -1), (-3, -15), (-1, -2), (1, -22), (3, -2), (5, -13), (6.5, -1), (8, -8), (9, -1), (10, 3), (0, 5)])
    cr.line([(-9, 2), (10, 2)], 0.9, op='tex', v=0.15)
    cr.line([(1, -3), (1, -20)], 0.8, op='emit', v=0.55, soft=0.4)
    cr.ell(1, 2, 1.7, 1.7, mat='gem'); cr.ell(1, 2, 1.3, 1.3, op='emit', v=1.0, soft=0.3)
    # ------------------------------------------------ brazos y cetro
    for nm, x, z, dim in (('b', -5, 3.5, -0.2), ('f', 6, 10, 0.0)):
        ua = add('uarm_' + nm, 'torso', (x, -24), z=z, mat='skin', depth=2.8, noise=0.2, seed=44, dim=dim, tnoise=0.1)
        ua.tube([(0, 0), (0.6, 7), (0.4, 14)], 2.8, 2.3)
        ua.poly([(-5, -5), (5, -5), (6, 3), (0, 6), (-6, 3)], mat='ice', raise_=1.2, edge=0.1)
        ua.poly([(-3, -4), (-1, -12), (2, -4)], mat='ice', raise_=1.2, edge=0.1)
        fa = add('farm_' + nm, 'uarm_' + nm, (0.4, 14), z=z, mat='skin', depth=2.4, noise=0.2, seed=45, dim=dim, tnoise=0.1)
        fa.tube([(0, 0), (0, 7), (0, 13)], 2.3, 1.8)
        fa.poly([(-3, 3), (3, 3), (3.4, 13), (-2.8, 13)], mat='ice', raise_=1.0, edge=0.1)
        hn = add('hand_' + nm, 'farm_' + nm, (0, 13), z=z + 0.2, mat='skin', depth=2.0, noise=0.1, seed=46, dim=dim)
        hn.spl([(-2, -1), (2, -1), (3, 3), (1.4, 6), (-1.4, 6), (-2.6, 3)])
        for k in range(3):
            hn.line([(-1.2 + k * 1.2, 3.5), (-1.3 + k * 1.2, 6.5)], 0.5, op='tex', v=0.2)
    sc = add('scepter', 'hand_f', (0, 2), z=10.5, mat='steel', depth=2.2, noise=0.2, seed=50)
    sc.poly([(-1.5, -16), (1.5, -16), (1.4, 54), (-1.4, 54)])
    sc.line([(0, -10), (0, 52)], 0.8, op='tex', v=0.9)
    sc.ell(0, 10, 2.8, 2.2, mat='ice', raise_=1.0, edge=0.1)
    sc.poly([(-3.4, 50), (3.4, 50), (4.8, 56), (-4.8, 56)], mat='ice', raise_=1.0, edge=0.1)
    for ang, ln in ((-50, 17), (-22, 22), (0, 30), (22, 22), (50, 17)):
        a = math.radians(ang)
        dx, dy = math.sin(a), math.cos(a)
        sc.poly([(dx * 0 - 3.4 * dy, 56 + 3.4 * dx * 0 - 0), (dx * ln, 56 + dy * ln), (3.4 * dy, 56)])
    sc.ell(0, 64, 5.0, 5.4, mat='gem', raise_=1.4, edge=0.08)
    sc.ell(0, 64, 4.0, 4.4, op='emit', v=0.9, soft=0.5)
    sc.cracks(2, 6, v=0.08, w=0.6, seed=51, emit=0.4)
    # ------------------------------------------------ cristales orbitales
    for k in range(3):
        o = add('orb%d' % k, 'root', (0, -64), z=13, mat='ice', depth=3.0, noise=0.2, seed=60 + k)
        r = 6 - k
        o.poly([(0, -r * 1.7), (r * 0.7, 0), (0, r * 1.7), (-r * 0.7, 0)])
        o.line([(0, -r * 1.2), (0, r * 1.2)], 0.7, op='emit', v=0.7, soft=0.3)
        o.line([(-0.5, -r), (-0.2, r)], 0.5, op='tex', v=0.95)
    return P


def make(anims, fxhook):
    parts = build_parts()
    return Boss('reina_escarcha', (192, 160), (96, 156), (34, 100), parts, MATS, anims, fxhook,
                outline=(10, 14, 40), rim=(180, 240, 255), rimk=0.4, dis_col=(190, 240, 255), seed=31, post=None, scale=1.0, base=0.46)


# ====================================================================== animacion
def PZ(*ds):
    return merge(*ds)


def H(t, u, f, w):
    return {'torso': t, 'uarm_f': u, 'farm_f': f, 'scepter': w - (t + u + f)}


def B(u, f, hn=0):
    return {'uarm_b': u, 'farm_b': f, 'hand_b': hn}


def swayfx(f, n, amp=1.0, base=0.0, ph=0.0, hair=1.0):
    s = lambda o: S(f, n, ph + o)
    d = {'skirt': base + amp * 2.2 * s(0), 'skirt2': base * 1.3 + amp * 3.2 * s(0.1),
         'cape1': base * 0.8 + amp * 3.0 * s(0.05), 'cape2': base * 1.4 + amp * 6.0 * s(0.2),
         'hair': (base * 0.5 + amp * 3.0 * s(0.0)) * hair, 'hair2': (base * 0.7 + amp * 5.0 * s(0.12)) * hair,
         'hair3': (base * 0.9 + amp * 8.0 * s(0.25)) * hair}
    for k in range(5):
        d['petal%d' % k] = base * 0.6 + amp * 3.0 * s(0.1 + 0.08 * k) + (k - 2) * 1.2
    return d


WING_IDLE = {'wing_b.sx': 0.38, 'wing_b.sy': 0.4, 'wing_f.sx': 0.42, 'wing_f.sy': 0.44, 'wing_b': 8, 'wing_f': 3}


def wings(open_=0.0, beat=0.0):
    k = 0.4 + 0.6 * open_
    return {'wing_b.sx': k * 0.95, 'wing_b.sy': k, 'wing_f.sx': (k + 0.05) * 0.95, 'wing_f.sy': k + 0.05, 'wing_b': 8 - 20 * open_ + beat,
            'wing_f': 3 - 28 * open_ + beat * 1.3}


def orbit(f, n, rx=40, ry=10, cy=-72, spd=1.0, rad=1.0, ph=0.0):
    d = {}
    for k in range(3):
        a = 2 * math.pi * (spd * f / n + k / 3.0 + ph)
        d['orb%d.x' % k] = math.cos(a) * rx * rad
        d['orb%d.y' % k] = cy + 64 + math.sin(a) * ry + 6 * math.sin(a * 2 + k)
        d['orb%d.z' % k] = 13 if math.sin(a) > 0 else 0.3
        d['orb%d' % k] = 14 * math.cos(a)
    return d


FLOAT = -11
STAND = PZ({'root.y': FLOAT}, H(1, -14, -26, 176), B(10, -26, 0), {'head': -1})


def idle_pose(f):
    b = S(f, 6)
    return PZ(STAND, {'root.y': -2.4 * b, 'torso': 0.8 * b, 'head': -1.2 * b, 'uarm_f': -0.8 * b, 'uarm_b': 0.8 * b}, swayfx(f, 6, 1.0, 1.5), WING_IDLE, orbit(f, 6, 40, 10))


def walk_pose(f):
    ph = 2 * math.pi * f / 8
    s = math.sin(ph); c = math.cos(ph)
    return PZ(STAND, {'root.y': -2.2 * s, 'torso': 5 + 1.2 * c, 'head': -3, 'uarm_b': 12 + 4 * s, 'hip': 2}, H(6 + 1.2 * c, -22 + 3 * s, -30, 4), swayfx(f, 8, 1.4, 9), wings(0.2, 4 * s), orbit(f, 8, 42, 10))


W1 = K([(0, STAND),
        (1, PZ({'root.y': FLOAT - 1}, H(-3, -40, -60, 150), B(14, -30))),
        (2, PZ({'root.y': FLOAT - 2}, H(-8, -70, -80, 190), B(18, -30))),
        (3, PZ({'root.y': FLOAT - 3}, H(-12, -84, -86, 214), B(24, -34))),
        (4, PZ({'root.y': FLOAT - 3}, H(-14, -88, -88, 222), B(28, -36)))])


def wind1(f):
    t = f / 4
    return PZ(W1(f), swayfx(f, 5, 0.6, -4), wings(0.5 * t), orbit(f, 5, 40 - 10 * t, 10, spd=1.5), {'head': -4 * t})


A1 = K([(0, PZ({'root.y': FLOAT - 3}, H(-14, -88, -88, 222), B(28, -36)), 'sm'),
        (1, PZ({'root.y': FLOAT - 1, 'root.x': 3}, H(-4, -86, -74, 150), B(20, -30)), 'snap'),
        (2, PZ({'root.y': FLOAT, 'root.x': 8}, H(8, -52, -40, 60), B(8, -20)), 'snap'),
        (3, PZ({'root.y': FLOAT + 1, 'root.x': 12}, H(14, -30, -34, 8), B(-4, -14)), 'snap'),
        (4, PZ({'root.y': FLOAT + 1, 'root.x': 12}, H(14, -28, -32, 2), B(-6, -14)), 'out'),
        (5, PZ({'root.y': FLOAT, 'root.x': 10}, H(12, -26, -32, 0), B(-2, -16)), 'sm'),
        (6, PZ({'root.y': FLOAT, 'root.x': 5}, H(6, -20, -28, 0), B(6, -22)), 'sm'),
        (7, STAND, 'sm')])


def atk1(f):
    return PZ(A1(f), swayfx(f, 8, 1.2, -10 + f), wings(0.5), orbit(f, 8, 40, 10))


W2 = K([(0, STAND),
        (1, PZ({'root.y': FLOAT, 'root.x': -2}, H(-4, -30, -40, 108), B(30, -40))),
        (2, PZ({'root.y': FLOAT - 1, 'root.x': -5}, H(-9, -22, -50, 100), B(40, -50))),
        (3, PZ({'root.y': FLOAT - 1, 'root.x': -8}, H(-12, -14, -60, 96), B(50, -60))),
        (4, PZ({'root.y': FLOAT - 1, 'root.x': -10}, H(-14, -8, -66, 94), B(56, -66)))])


def wind2(f):
    t = f / 4
    return PZ(W2(f), swayfx(f, 5, 0.5, 4 + 4 * t), wings(0.6 * t), orbit(f, 5, 40 - 20 * t, 10, spd=1.5, rad=1.0))


A2 = K([(0, PZ({'root.y': FLOAT - 1, 'root.x': -10}, H(-14, -8, -66, 94), B(56, -66)), 'sm'),
        (1, PZ({'root.y': FLOAT, 'root.x': 4}, H(4, -50, -32, 78), B(30, -40)), 'snap'),
        (2, PZ({'root.y': FLOAT + 1, 'root.x': 14}, H(14, -74, -14, 84), B(14, -20)), 'snap'),
        (3, PZ({'root.y': FLOAT + 1, 'root.x': 16}, H(16, -78, -10, 86), B(10, -16)), 'out'),
        (4, PZ({'root.y': FLOAT + 1, 'root.x': 16}, H(16, -78, -10, 86), B(10, -16)), 'sm'),
        (5, PZ({'root.y': FLOAT, 'root.x': 14}, H(12, -70, -16, 84), B(12, -20)), 'sm'),
        (6, PZ({'root.y': FLOAT, 'root.x': 8}, H(8, -40, -30, 60), B(18, -24)), 'sm'),
        (7, STAND, 'sm')])


def atk2(f):
    return PZ(A2(f), swayfx(f, 8, 1.2, -12 + f * 1.5), wings(0.7 if f < 6 else 0.3), orbit(f, 8, 20, 8, spd=1.5))


W3 = K([(0, STAND),
        (1, PZ({'root.y': FLOAT - 6}, H(-4, -50, -60, 150), B(-80, -80))),
        (2, PZ({'root.y': FLOAT - 14}, H(-8, -100, -60, 190), B(-130, -60))),
        (3, PZ({'root.y': FLOAT - 22}, H(-10, -128, -50, 198), B(-150, -40))),
        (4, PZ({'root.y': FLOAT - 28}, H(-14, -140, -46, 200), B(-156, -34))),
        (5, PZ({'root.y': FLOAT - 32}, H(-16, -146, -44, 202), B(-160, -30)))])


def wind3(f):
    t = f / 5
    return PZ(W3(f), swayfx(f, 6, 0.8, -6 * t), wings(t, -5 * t), orbit(f, 6, 40 - 10 * t, 10, cy=-72 - 30 * t, spd=1.5))


A3 = K([(0, PZ({'root.y': FLOAT - 32}, H(-16, -146, -44, 202), B(-160, -30)), 'sm'),
        (1, PZ({'root.y': FLOAT - 30}, H(-18, -150, -40, 206), B(-162, -28)), 'sm'),
        (2, PZ({'root.y': FLOAT - 20}, H(2, -120, -50, 180), B(-120, -30)), 'in'),
        (3, PZ({'root.y': FLOAT - 6}, H(14, -70, -40, 120), B(-60, -30)), 'in'),
        (4, PZ({'root.y': FLOAT + 2, 'root.x': 8}, H(22, -34, -26, 20), B(-20, -26)), 'snap'),
        (5, PZ({'root.y': FLOAT + 3, 'root.x': 8}, H(24, -30, -24, 6), B(-14, -22)), 'sm'),
        (6, PZ({'root.y': FLOAT + 2, 'root.x': 8}, H(22, -30, -26, 6), B(-14, -22)), 'sm'),
        (7, PZ({'root.y': FLOAT}, H(10, -24, -30, 0), B(0, -24)), 'sm'),
        (8, STAND, 'sm')])


def atk3(f):
    return PZ(A3(f), swayfx(f, 9, 1.4, 12 if 2 <= f <= 4 else -4), wings(1.0 if f < 5 else 0.6), orbit(f, 9, 50, 10, cy=-80, spd=2, rad=1.1))


CAST = K([(0, STAND),
          (1, PZ({'root.y': FLOAT - 2}, H(-2, -40, -56, 120), B(-40, -50))),
          (2, PZ({'root.y': FLOAT - 4}, H(-6, -90, -66, 160), B(-80, -50)), 'sm'),
          (3, PZ({'root.y': FLOAT - 6}, H(-10, -108, -60, 176), B(-100, -50)), 'sm'),
          (4, PZ({'root.y': FLOAT - 6, 'root.x': 4}, H(4, -92, -52, 130), B(-60, -50)), 'snap'),
          (5, PZ({'root.y': FLOAT - 4, 'root.x': 4}, H(6, -90, -46, 126), B(-40, -50)), 'out'),
          (6, PZ({'root.y': FLOAT - 2}, H(2, -50, -40, 70), B(-10, -40)), 'sm'),
          (7, STAND, 'sm')])


def cast(f):
    return PZ(CAST(f), swayfx(f, 8, 1.2, -2), wings(0.6 if 1 <= f <= 6 else 0.2), orbit(f, 8, 36, 10, spd=1.5))


def hurt(f):
    i = int(f)
    d = [PZ({'root.y': FLOAT + 1, 'root.x': -5}, H(-10, -8, -30, 40), B(24, -10), {'head': -10, 'tint': ((255, 255, 255), 0.55)}),
         PZ({'root.y': FLOAT, 'root.x': -3}, H(-5, -12, -28, 20), B(18, -18), {'head': -5, 'tint': ((255, 255, 255), 0.2)})][i]
    return PZ(d, swayfx(f, 2, 1.0, 10 - 6 * i), WING_IDLE, orbit(f, 2, 40, 10))


PHK = K([(0, STAND),
         (1, PZ({'root.y': FLOAT + 3}, H(6, -40, -60, 90), B(30, -40), {'head': 6}), 'sm'),
         (2, PZ({'root.y': FLOAT + 6}, H(10, -50, -60, 80), B(46, -50), {'head': 10}), 'sm'),
         (3, PZ({'root.y': FLOAT - 6}, H(-4, -110, -60, 180), B(-110, -50), {'head': -10}), 'snap'),
         (4, PZ({'root.y': FLOAT - 20}, H(-14, -150, -40, 206), B(-150, -30), {'head': -22}), 'snap'),
         (5, PZ({'root.y': FLOAT - 26}, H(-16, -156, -40, 208), B(-156, -30), {'head': -26}), 'sm'),
         (6, PZ({'root.y': FLOAT - 26}, H(-16, -156, -40, 208), B(-156, -30), {'head': -24}), 'sm'),
         (7, PZ({'root.y': FLOAT - 18}, H(-8, -130, -40, 200), B(-130, -30), {'head': -12}), 'sm'),
         (8, PZ({'root.y': FLOAT - 8}, H(0, -70, -40, 120), B(-60, -30), {'head': -4}), 'sm'),
         (9, STAND, 'sm')])


def phase(f):
    p = PHK(f)
    i = int(f)
    open_ = [0, 0.1, 0.1, 0.5, 1.0, 1.3, 1.3, 1.1, 0.8, 0.4][i]
    cr = [1, 1, 1, 1.1, 1.4, 1.7, 1.7, 1.5, 1.3, 1.1][i]
    flare = [0, 0.4, 0.4, 0.8, 1.2, 1.6, 1.6, 1.2, 0.8, 0.3][i]
    d = swayfx(f, 10, 2.0 + flare, 0, 0.0)
    for k in range(5):
        d['petal%d' % k] += (k - 2) * 9 * flare
    d['skirt.sx'] = 1 + 0.12 * flare
    d['skirt2.sx'] = 1 + 0.16 * flare
    d['crown.sx'] = cr; d['crown.sy'] = cr
    q = PZ(p, d, wings(open_, 4 * math.sin(f * 2.3)), orbit(f, 10, 44 + 16 * flare, 12, spd=3, rad=1.0))
    q['emit'] = 1 + 0.7 * flare
    if 4 <= f <= 7:
        q['tint'] = ((200, 245, 255), 0.18 * (1 - abs(f - 5.5) / 2.0))
        q['root.x'] = q.get('root.x', 0) + (1.0 if i % 2 else -1.0)
    return q


def intro(f):
    i = int(f)
    land = 11
    # descenso: desde fuera de celda hasta flotar
    ry = [-160, -150, -120, -92, -70, -52, -38, -26, -16, -8, -2, 4, 0, 0][i]
    ry2 = ry + (f - i) * (([-160, -150, -120, -92, -70, -52, -38, -26, -16, -8, -2, 4, 0, 0][min(13, i + 1)]) - ry) if f != i else ry
    t = clamp01((f - 9) / 3.0)
    arms = PZ(H(2 + 6 * (1 - t), -50 * (1 - t) - 14 * t, -50, 190 * (1 - t) + 0), B(40 * (1 - t) + 10 * t, -30))
    op = clamp01(1 - abs(f - 8) / 6.0) * 1.0
    p = PZ(STAND, {'root.y': FLOAT + ry2}, arms, swayfx(f, 14, 1.4 + 2 * (1 - t), -14 * (1 - t) - 4), wings(0.9 * (1 - t) + 0.2, 0), orbit(f, 14, 40, 10, spd=2))
    if f < 2:
        p['clip'] = (0, 0, 0, 0)
    if f >= 10:
        p['tint'] = ((255, 255, 255), 0.2 * clamp01(1 - (f - 10) / 3.0))
    return p


DEATH = K([(0, PZ({'root.y': FLOAT + 1, 'root.x': -5}, H(-10, -8, -30, 40), B(24, -10), {'head': -10, 'tint': ((255, 255, 255), 0.6)}), 'out'),
           (1, PZ({'root.y': FLOAT, 'root.x': -4}, H(-12, -20, -40, 60), B(30, -20), {'head': -12, 'tint': ((255, 255, 255), 0.3)}), 'sm'),
           (2, PZ({'root.y': FLOAT - 3}, H(-8, -30, -40, 80), B(24, -30), {'head': -14}), 'sm'),
           (4, PZ({'root.y': FLOAT - 4}, H(-8, -40, -50, 110), B(30, -30), {'head': -16}), 'sm'),
           (6, PZ({'root.y': FLOAT - 5}, H(-9, -44, -50, 120), B(32, -30), {'head': -18}), 'sm'),
           (7, PZ({'root.y': FLOAT - 5}, H(-9, -44, -50, 120), B(32, -30), {'head': -18}), 'lin'),
           (13, PZ({'root.y': FLOAT - 5}, H(-9, -44, -50, 120), B(32, -30), {'head': -18}), 'lin')])

SHAT = {'head': (-8, -34, 40), 'crown': (-16, -42, -50), 'hair': (-20, -10, 24), 'hair2': (-26, 4, 30), 'hair3': (-28, 14, 36),
        'torso': (-4, -6, 10), 'skirt': (6, 18, -10), 'skirt2': (-10, 20, -14), 'cape1': (-22, 6, 20), 'cape2': (-28, 22, 30),
        'wing_b': (-30, -20, -40), 'wing_f': (24, -26, 40), 'uarm_f': (22, -14, 40), 'farm_f': (34, -8, 50), 'scepter': (46, 6, 70),
        'uarm_b': (-16, -10, -50), 'farm_b': (-24, 0, -60), 'collar': (-6, -26, 30)}


def death(f):
    p = dict(DEATH(f))
    fr = clamp01(f / 5.0)
    p['tint'] = ((190, 235, 255), 0.55 * fr) if f >= 2 else p.get('tint', ((255, 255, 255), 0))
    if f < 2:
        p['tint'] = DEATH(f)['tint']
    p.update(swayfx(min(f, 6), 10, 0.5 * (1 - fr), 4))
    p.update(wings(0.3, 0)); p.update(orbit(f * 0.3, 10, 40, 10))
    if f >= 7:
        t = clamp01((f - 6.8) / 6.0)
        g = t
        for nm, (dx, dy, rot) in SHAT.items():
            p[nm + '.x'] = p.get(nm + '.x', 0) + dx * g * 1.1
            p[nm + '.y'] = p.get(nm + '.y', 0) + dy * g * 1.1 + 70 * g * g * (1 if nm not in ('head', 'crown') else 0.6)
            p[nm] = p.get(nm, 0) + rot * g
        p['dis'] = clamp01((f - 7.0) / 4.5) * 1.12
        p['dis_dir'] = 1.0
        p['emit'] = 1.0
    return p


# ====================================================================== efectos
def ice_spike(ctx, x, y, h, w, a=1.0, layer='front', tilt=0.0, tone=0):
    fx = ctx.fx
    lt = [(226, 248, 255), (180, 232, 255)][tone]
    md = [(120, 200, 245), (90, 170, 235)][tone]
    dk = [(52, 100, 190), (40, 76, 170)][tone]
    tx = x + tilt
    fx.poly([(x - w - 1, y + 1), (tx, y - h - 1.5), (x + w + 1, y + 1)], (14, 20, 56), a, layer, ss=2)
    fx.poly([(x - w, y), (tx, y - h), (x, y - h * 0.15)], lt, a, layer, ss=2)
    fx.poly([(x - w, y), (x, y - h * 0.15), (x, y)], md, a, layer, ss=2)
    fx.poly([(tx, y - h), (x + w, y), (x, y)], dk, a, layer, ss=2)
    fx.poly([(tx, y - h), (x + w * 0.4, y - h * 0.4), (x, y - h * 0.1)], md, a, layer, ss=2)
    fx.dots([(x - w * 0.5, y - h * 0.4)], (255, 255, 255), a, layer)


def frost_ring(ctx, x, y, t, rx=70, ry=8, a=0.9):
    shock(ctx, x, y, t, (200, 245, 255), rx, ry, 2, a)


def snow(ctx, x, y, w, h, n, t=None, seed=1, a=0.95, rise=-20, layer='front', size=1):
    wisps(ctx, x, y, w, h, n, [(255, 255, 255), (200, 240, 255), (150, 215, 250)], t=t, seed=seed, a=a, rise=rise, layer=layer, size=size)


def ice_shot(ctx, x, y, s=1.0, tail=1.0):
    fx = ctx.fx
    fx.glow(x, y, 10 * s, (110, 210, 255), 0.8)
    fx.polyline([(x - 4, y), (x - 14 * tail, y + 0.5), (x - 26 * tail, y)], 3, (130, 220, 255), 0.45, 'front')
    fx.polyline([(x - 4, y), (x - 12 * tail, y), (x - 22 * tail, y)], 1, (240, 255, 255), 0.8, 'front')
    pts = [(x - 7 * s, y), (x - 1 * s, y - 3 * s), (x + 8 * s, y), (x - 1 * s, y + 3 * s)]
    fx.poly([(px, py) for px, py in [(x - 8 * s, y), (x - 1 * s, y - 3.6 * s), (x + 9 * s, y), (x - 1 * s, y + 3.6 * s)]], (20, 36, 90), 1.0, 'front', ss=2)
    fx.poly(pts, (170, 230, 255), 1.0, 'front', ss=2)
    fx.poly([(x - 7 * s, y), (x - 1 * s, y - 3 * s), (x + 8 * s, y)], (240, 255, 255), 1.0, 'front', ss=2)


def fxhook(ctx):
    n, i, fx = ctx.name, ctx.i, ctx.fx
    ax, ay = ctx.pivot
    W = ctx.W
    rng = ctx.rng
    tip = lambda f=None: ctx.anchor('scepter', (0, 66)) if f is None else ctx.anchor_at(f, 'scepter', (0, 66))
    ek = ctx.pose.get('emit', 1.0)
    # orbes brillantes
    tx, ty = tip()
    if n != 'intro' or i >= 4:
        fx.glow(tx, ty, 14, (110, 220, 255), min(1.0, 0.55 * ek))
    ex, ey = ctx.anchor('head', (4.6, -5.8))
    if n != 'death' or i < 6:
        fx.glow(ex, ey, 6, (150, 240, 255), min(1.0, 0.5 * ek))
    cr_x, cr_y = ctx.anchor('crown', (1, -10))
    fx.glow(cr_x, cr_y, 12, (140, 230, 255), 0.25 * ek)
    for k in range(3):
        ox, oy = ctx.anchor('orb%d' % k, (0, 0))
        fx.glow(ox, oy, 7, (130, 225, 255), 0.5)
    if n not in ('intro', 'death'):
        snow(ctx, ax - 4, ay - 70, 90, 120, 16, seed=3, rise=-22)
        # niebla de escarcha bajo el vestido
        fx.glow(ax, ay - 2, 36, (170, 225, 255), 0.18, rx=44, ry=7)
    if n == 'walk':
        snow(ctx, ax - 18, ay - 6, 40, 8, 6, seed=6, rise=10, layer='back')
    # --- ataque 1
    if n == 'windup1':
        t = i / 4.0
        fx.glow(tx, ty, 10 + 14 * t, (130, 230, 255), 0.4 + 0.4 * t)
        snow(ctx, tx, ty, 26, 24, 8, t=t, seed=8, rise=-12)
    if n == 'attack1':
        trail(ctx, 'scepter', (0, 70), (0, 30), 0, 4, (240, 255, 255), (50, 130, 220), steps=12, span=3.4, mid=(130, 220, 255), a=0.85)
        if 2 <= i <= 6:
            t = (i - 2) / 4.0
            gx = max(ax + 30, min(tx + 6, W - 24))
            frost_ring(ctx, gx, ay, t, 40, 5)
            for k, off in enumerate((-14, -5, 5, 14)):
                hh = (16 + 6 * (k % 2)) * (1 - t * 0.5) * clamp01(1.6 - t)
                ice_spike(ctx, gx + off, ay + 1, hh, 3.2, 1.0 - t * 0.4, 'front', tone=k % 2)
            dust(ctx, gx, ay, t, (200, 235, 250), 8, 26, 10, 2.4, a=0.8)
            if i == 2:
                fx.sparks(rng, gx, ay - 6, 12, 16, [(255, 255, 255), (150, 225, 255)], 'front', 10)
    # --- ataque 2
    if n == 'windup2':
        t = i / 4.0
        fx.glow(tx, ty, 10 + 18 * t, (130, 230, 255), 0.4 + 0.5 * t)
        for k in range(4):
            ang = i * 1.0 + k * 1.57
            r = 20 * (1 - 0.6 * t)
            fx.dots([(tx + math.cos(ang) * r, ty + math.sin(ang) * r * 0.8)], (240, 255, 255), 0.9, 'front')
        # lanza de cristal que se forma frente al cetro
        if i >= 2:
            L = 10 + 14 * (i - 2)
            fx.poly([(tx + 2, ty - 3), (tx + 2 + L, ty), (tx + 2, ty + 3)], (200, 240, 255), 0.85, 'front', ss=2)
    if n == 'attack2':
        sx, sy = tx, ty
        if 1 <= i <= 6:
            tt = clamp01((i - 1) / 5.0)
            ln = min(W - 8 - sx, 120) * ease_out(clamp01(i / 2.0)) * (1 - 0.35 * clamp01((i - 4) / 3.0))
            wv = 6.5 * (1 - 0.3 * tt)
            fx.poly([(sx, sy - 1.5), (sx + ln * 0.45, sy - wv), (sx + ln, sy), (sx + ln * 0.45, sy + wv), (sx, sy + 1.5)], (24, 60, 150), 0.6 * (1 - tt * 0.5), 'front', ss=2)
            fx.poly([(sx, sy - 1), (sx + ln * 0.45, sy - wv * 0.6), (sx + ln * 0.98, sy), (sx + ln * 0.45, sy + wv * 0.6), (sx, sy + 1)], (150, 225, 255), 0.85 * (1 - tt * 0.4), 'front', ss=2)
            fx.poly([(sx, sy - 0.6), (sx + ln * 0.45, sy - wv * 0.25), (sx + ln, sy), (sx + ln * 0.45, sy)], (255, 255, 255), 0.9 * (1 - tt * 0.4), 'front', ss=2)
            fx.glow(sx + ln, sy, 14, (150, 235, 255), 0.8 * (1 - tt * 0.5))
            # carambanos de suelo en fila
            m = int(ln / 14)
            for k in range(m):
                px = sx + 10 + k * 14
                hh = (22 - k * 1.2) * clamp01((i - 1 - k * 0.3) / 1.5) * (1 - tt * 0.5)
                if hh > 2 and px < W - 6:
                    ice_spike(ctx, px, ay + 1, hh, 3.6, 0.95, 'front', tilt=1.5, tone=k % 2)
            for k in range(4):
                yy = sy + (k - 1.5) * 5
                x0 = sx - 6 - ((i * 7 + k * 13) % 12)
                fx.line((x0, yy), (x0 - 12 - 4 * k, yy), 1, (200, 245, 255), 0.6 * (1 - tt * 0.5), 'front')
    # --- ataque 3
    if n == 'windup3':
        t = i / 5.0
        fx.glow(ax, ay - 70 - 20 * t, 30 + 26 * t, (130, 230, 255), 0.2 + 0.3 * t, rx=36 + 20 * t, ry=40)
        snow(ctx, ax, ay - 10, 70, 100, 18, t=t, seed=5, rise=-30)
        tx3, ty3 = tip()
        fx.glow(tx3, ty3, 14 + 14 * t, (140, 235, 255), 0.5 + 0.4 * t)
    if n == 'attack3':
        if 2 <= i <= 4:
            trail(ctx, 'scepter', (0, 70), (0, 30), 2, 4, (240, 255, 255), (50, 130, 220), steps=10, span=2.6, mid=(130, 220, 255), a=0.8)
        if 4 <= i <= 8:
            t = (i - 4) / 4.0
            gx = ax + 24
            frost_ring(ctx, gx, ay, t, 86, 9)
            ground_cracks(ctx, gx, ay + 1, t, (30, 60, 130), (190, 245, 255), 9, 70, 51)
            fx.glow(gx, ay - 6, 24 * (1 - t * 0.5), (190, 245, 255), 0.85 * (1 - t))
            if i <= 7:
                for k, off in enumerate((-84, -66, -50, -34, -18, 0, 16, 32, 50, 68)):
                    px = gx + off + (k % 2) * 3
                    hh = (30 + 14 * ((k * 7) % 3)) * clamp01(1.5 - t * 0.5) * clamp01((i - 3.4 + abs(off) * 0.008) * 2) * (1 - t * 0.35)
                    if px < W - 5 and px > 5 and hh > 2:
                        ice_spike(ctx, px, ay + 1, hh, 4.6, 1.0, 'front', tilt=(k % 3 - 1) * 2, tone=k % 2)
            dust(ctx, gx, ay, t, (210, 240, 255), 14, 54, 16, 3.0)
            if i == 4:
                fx.sparks(rng, gx, ay - 4, 22, 30, [(255, 255, 255), (170, 235, 255), (110, 200, 250)], 'front', 20)
        if i in (1, 2, 3):
            snow(ctx, ax, ay - 40, 60, 80, 12, seed=7, rise=-24)
    # --- cast
    if n == 'cast':
        if 1 <= i <= 4:
            t = i / 4.0
            fx.glow(tx, ty, 14 + 14 * t, (140, 235, 255), 0.5 + 0.5 * t)
            for k in range(8):
                ang = i * 0.9 + k * 0.8
                r = 24 * (1 - t * 0.6) + 2
                px = tx + math.cos(ang) * r; py = ty + math.sin(ang) * r * 0.8
                fx.poly([(px - 1, py), (px, py - 3), (px + 1, py), (px, py + 3)], (225, 250, 255), 0.95, 'front')
        if i >= 4:
            tt = (i - 4) / 3.0
            for k in range(5):
                ang = (k - 2) * 0.22
                d = 6 + tt * (46 + k * 6)
                sx_ = tx + math.cos(ang) * d
                sy_ = ty + math.sin(ang) * d * 0.6 + (k - 2) * 3 * tt
                if sx_ < W - 8:
                    ice_shot(ctx, sx_, sy_, 0.9 - tt * 0.1, 1.0)
    # --- fase
    if n == 'phase':
        t = clamp01((i - 3) / 4.0)
        if 3 <= i <= 9:
            fx.glow(ax, ay - 70, 60 * t + 20, (140, 235, 255), 0.55 * (1 - abs(t - 0.5) * 1.1), rx=64 * t + 20, ry=76 * t + 14)
            rays(ctx, ax, ay - 74, t, (190, 245, 255), 16, 14, 84, 0.09, 0.5, i * 0.14, 'back', 'over')
            frost_ring(ctx, ax, ay, clamp01((i - 3) / 5.0), 80, 8)
        if 3 <= i <= 9:
            snow(ctx, ax, ay - 60, 120, 110, 40, t=(i - 3) / 6.0, seed=22, rise=-48, size=1)
            for k, off in enumerate((-60, -40, 40, 60)):
                hh = (26 + 12 * (k % 2)) * clamp01((i - 3.5) / 2.0) * (1 - clamp01((i - 7) / 3.0) * 0.6)
                if hh > 2:
                    ice_spike(ctx, ax + off, ay + 1, hh, 4.0, 0.95, 'back', tone=k % 2)
    if n == 'intro':
        intro_fx(ctx)
    if n == 'death':
        death_fx(ctx)


def intro_fx(ctx):
    i, fx, ax, ay = ctx.i, ctx.fx, ctx.pivot[0], ctx.pivot[1]
    rng = ctx.rng
    # ventisca: nieve en diagonal + nube arriba
    for k in range(3):
        fx.glow(ax + (k - 1) * 40, 10, 40, (150, 190, 235), 0.4 * clamp01(1 - (i - 10) / 4.0), rx=50, ry=18)
    st = clamp01(1 - (i - 11) / 3.0)
    for k in range(34):
        r = np.random.default_rng(k + 40)
        x0 = r.random() * 192
        yy = ((r.random() * 160) + i * (14 + 10 * r.random())) % 160
        xx = (x0 - yy * 0.5 + 10 * math.sin(i * 0.8 + k)) % 192
        fx.dots([(xx, yy)], [(255, 255, 255), (200, 235, 255)][k % 2], 0.95 * st + 0.0, 'front', 1 + (k % 5 == 0))
        if k % 3 == 0:
            fx.line((xx, yy), (xx - 5, yy - 3), 1, (210, 240, 255), 0.6 * st, 'front')
    # columna de luz/helada que acompana el descenso
    if 1 <= i <= 9:
        fx.poly([(ax - 18, 0), (ax + 18, 0), (ax + 40, 150), (ax - 40, 150)], (150, 215, 255), 0.12, 'back', ss=1)
    if 9 <= i <= 13:
        t = clamp01((i - 9) / 4.0)
        frost_ring(ctx, ax, ay, t, 70, 7)
        dust(ctx, ax, ay, t, (210, 240, 255), 12, 46, 14, 2.8)
        fx.glow(ax, ay - 8, 26 * (1 - t * 0.5), (190, 245, 255), 0.6 * (1 - t))
        for k, off in enumerate((-40, -26, 26, 40)):
            hh = (16 + 8 * (k % 2)) * clamp01(1.5 - t) * clamp01((i - 9 + 1) / 1.5)
            ice_spike(ctx, ax + off, ay + 1, hh, 3.2, 0.95, 'back', tone=k % 2)


def death_fx(ctx):
    i, fx, ax, ay = ctx.i, ctx.fx, ctx.pivot[0], ctx.pivot[1]
    rng = ctx.rng
    # congelacion: escarcha y grietas
    if 1 <= i <= 7:
        k = clamp01(i / 6.0)
        cx, cy = ctx.anchor('torso', (0, -12))
        rr = np.random.default_rng(7)
        for j in range(int(3 + 9 * k)):
            a = rr.random() * 6.283; L = (6 + 22 * rr.random()) * clamp01(k * 1.4)
            x1 = cx + math.cos(a) * L * 0.8; y1 = cy + math.sin(a) * L * 1.4
            fx.polyline([(cx, cy), ((cx + x1) / 2 + 2, (cy + y1) / 2), (x1, y1)], 1, (240, 255, 255), 0.9, 'front')
        fx.glow(cx, cy, 24 * k + 8, (190, 245, 255), 0.4 * k)
    if i == 7:
        cx, cy = ctx.anchor('torso', (0, -12))
        fx.glow(cx, cy, 60, (255, 255, 255), 0.9)
        rays(ctx, cx, cy, 0.8, (255, 255, 255), 18, 6, 80, 0.07, 0.9, 0.3, 'front', 'add')
    if i >= 7:
        t = clamp01((i - 7) / 6.0)
        # esquirlas volando
        r2 = np.random.default_rng(11)
        for k in range(26):
            a = r2.random() * 6.283
            spd = 16 + 50 * r2.random()
            cx, cy = ax + (r2.random() - 0.5) * 30, ay - 36 - r2.random() * 50
            tt = ease_out(clamp01(t * 1.3))
            px = cx + math.cos(a) * spd * tt
            py = cy + math.sin(a) * spd * tt * 0.7 + 60 * t * t * (0.5 + r2.random())
            py = min(py, ay - 1 - (k % 4))
            s = 1.5 + 2.5 * r2.random()
            al = 1.0 if t < 0.8 else max(0.3, (1 - t) * 4)
            rot = r2.random() * 3
            fx.poly([(px, py - s * 1.6), (px + s * 0.7, py), (px, py + s * 1.6), (px - s * 0.7, py)], (210, 240, 255) if k % 2 else (130, 200, 245), al, 'front', ss=2)
        # monton de cristales + corona + cetro
        pile(ctx, ax, ay, 96, 14 + 10 * t, [(200, 236, 252), (130, 200, 245), (80, 140, 215), (240, 252, 255)], int(14 + 56 * t), seed=14, layer='back', outline=(14, 20, 56))
        if t > 0.35:
            q = clamp01((t - 0.35) / 0.4)
            cx0, cy0 = ax + 6, ay - 3
            fx.poly([(cx0 - 6, cy0 + 1), (cx0 - 6, cy0 - 3), (cx0 - 3.5, cy0), (cx0 - 1.5, cy0 - 6), (cx0, cy0 - 1), (cx0 + 2, cy0 - 7), (cx0 + 3.5, cy0 - 1), (cx0 + 6, cy0 - 4), (cx0 + 6, cy0 + 1)], (180, 230, 255), q, 'back')
            sx0 = ax - 18
            fx.poly([(sx0 - 22, ay - 3), (sx0 + 16, ay - 5), (sx0 + 16, ay - 2.4), (sx0 - 22, ay - 1.2)], (120, 140, 175), q, 'back')
            fx.glow(sx0 - 22, ay - 2, 6, (130, 225, 255), 0.7 * q)
        snow(ctx, ax, ay - 50, 90, 90, 22, t=t, seed=9, rise=10 + 20 * (1 - t), a=0.9)
        fx.glow(ax, ay - 3, 40, (170, 225, 255), 0.25 * (1 - t * 0.5), rx=50, ry=7)


def hit_boxes():
    return {
        'attack1': dict(hit=[2, 4], box=[8, -100, 76, 104]),
        'attack2': dict(hit=[2, 5], box=[8, -72, 150, 62]),
        'attack3': dict(hit=[4, 6], box=[-84, -70, 176, 70]),
        'cast': dict(rel=4, muzzle_src=('scepter', (0, 66))),
    }


def spec():
    fns = dict(idle=idle_pose, walk=walk_pose, windup1=wind1, attack1=atk1, windup2=wind2, attack2=atk2, windup3=wind3,
               attack3=atk3, cast=cast, hurt=hurt, phase=phase, intro=intro, death=death)
    hb = hit_boxes()
    return {k: dict(pose=v, **hb.get(k, {})) for k, v in fns.items()}


def build():
    return make(spec(), fxhook)
