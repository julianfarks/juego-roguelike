"""bs_devorador_vacio: El ojo que todo lo consume. Ojo gigante flotante con boca de dientes, tentaculos y pupila purpura."""
import math
import numpy as np
from kit import *
from shapes import *
from anim import *
from fxlib import *

FLESH = auto('#5a2f7c', shadow=(16, 6, 74), warm=(226, 140, 240), n=6, dk=0.24, lk=0.32)
FLESH2 = auto('#43245f', shadow=(12, 4, 64), warm=(190, 110, 230), n=6, dk=0.24, lk=0.3)
SCL = auto('#d9cdee', shadow=(70, 34, 130), warm=(255, 246, 255), n=6, dk=0.34, lk=0.42, boost=1.12)
IRS = ramp((28, 6, 70), (110, 34, 190), (200, 120, 255), 6)
OBS = auto('#2a1c42', shadow=(10, 4, 44), warm=(176, 110, 250), n=6, dk=0.2, lk=0.34)
TOOTH = auto('#e8dcb6', shadow=(80, 40, 110), warm=(255, 252, 224), n=6, dk=0.34, lk=0.4)
PUP = ramp((2, 0, 8), (12, 4, 30), (50, 16, 100), 6)
VOIDM = ramp((2, 0, 8), (8, 2, 20), (30, 8, 56), 6)
VG = [(34, 6, 76), (92, 24, 168), (176, 76, 255), (228, 158, 255), (255, 236, 255)]
MATS = {
    'flesh': Mat(FLESH, glow=VG, texamt=0.6, gain=1.25),
    'flesh2': Mat(FLESH2, glow=VG, texamt=0.6, gain=1.2),
    'scl': Mat(SCL, glow=VG, texamt=0.35, gain=1.1),
    'ir': Mat(IRS, glow=VG, texamt=0.2, gain=1.0),
    'obs': Mat(OBS, glow=VG, texamt=0.4, gain=1.5),
    'tooth': Mat(TOOTH, texamt=0.35, gain=1.2),
    'pup': Mat(PUP, glow=VG, texamt=0.1, gain=0.6),
    'void': Mat(VOIDM, gain=0.3),
    'gl': Mat(IRS, glow=[(255, 255, 255)] * 3, texamt=0.0),
}
VIO = (176, 76, 255)
TX = [-34, -24, -13, -2, 10, 22, 33]
TY = [24, 31, 35, 37, 36, 32, 26]
TZ = [1.0, 1.2, 1.4, 1.6, 5.2, 5.25, 5.3]


def build_parts():
    P = []

    def add(*a, **k):
        p = Part(*a, **k); P.append(p); return p
    add('root', None, (96, 156), ghost=True)
    add('body', 'root', (0, -90), ghost=True)
    # ------------------------------------------------ tentaculos
    for k in range(7):
        parent = 'body'
        at = (TX[k], TY[k])
        L = [15, 14, 13, 12]
        r = [(6.4, 5.2), (5.2, 4.0), (4.0, 2.8), (2.8, 0.8)]
        for j in range(4):
            nm = 't%d_%d' % (k, j)
            tn = add(nm, parent, at, z=TZ[k] + j * 0.01, mat='flesh2' if k < 4 else 'flesh', depth=5.0 - j * 0.6, noise=0.4, seed=70 + k * 5 + j, tnoise=0.25, dim=(-0.12 if k < 4 else 0))
            tn.tube([(0, 0), (0, L[j] * 0.5), (0.4 * (1 if k % 2 else -1), L[j])], r[j][0], r[j][1], spline=False)
            tn.ell(0, 0, r[j][0] * 0.95, r[j][0] * 0.95)
            tn.cracks(1, 5, v=0.06, w=0.6, seed=80 + k * 3 + j, emit=0.45)
            if j < 3:
                for u in (0.32, 0.72):
                    tn.ell(1.8 * (1 - 0.2 * j), L[j] * u, 1.0, 1.0, op='emit', v=0.8, soft=0.3)
            parent = nm
            at = (0.4 * (1 if k % 2 else -1), L[j])
    # ------------------------------------------------ cuernos / espinas obsidiana
    hn = add('horns', 'body', (0, 0), z=2, mat='obs', depth=4.0, noise=0.4, seed=90, tnoise=0.25)
    for ang, ln, wd in ((-96, 24, 8), (-68, 24, 9), (-40, 22, 9), (-12, 19, 8), (16, 22, 8), (44, 24, 7), (70, 20, 6)):
        a = math.radians(ang)
        ux, uy = math.sin(a), -math.cos(a)
        px, py = -uy, ux
        bx, by = ux * 36, uy * 36
        tip = (ux * (36 + ln) + px * ln * 0.22, uy * (36 + ln) + py * ln * 0.22)
        hn.poly([(bx - px * wd * 0.5 - ux * 8, by - py * wd * 0.5 - uy * 8), (bx - px * wd * 0.6 + ux * ln * 0.5 + px * 3, by - py * wd * 0.6 + uy * ln * 0.5 + py * 3), tip,
                 (bx + px * wd * 0.6 + ux * ln * 0.4, by + py * wd * 0.6 + uy * ln * 0.4), (bx + px * wd * 0.5 - ux * 8, by + py * wd * 0.5 - uy * 8)])
    hn.cracks(5, 9, v=0.05, w=0.7, seed=91, emit=0.5)
    # ------------------------------------------------ carne
    fl = add('flesh', 'body', (0, 0), z=4, mat='flesh', depth=24.0, noise=1.0, seed=5, tnoise=0.35)
    fl.ell(0, 0, 42, 41)
    fl.spl([(-38, 10), (-20, 15), (0, 17), (22, 15), (38, 9), (33, 24), (-33, 24)], mat='void', raise_=-2.0)
    fl.poly([(-60, 24), (60, 24), (60, 80), (-60, 80)], op='sub')
    fl.hatch(3.2, 20, v=0.32, w=0.7, jit=0.6, seed=3)
    fl.cracks(9, 18, v=0.08, w=0.9, seed=6, emit=0.5, branch=0.9, spread=0.9)
    fl.blotch('flesh2', 0.64, 4.0, 7, raise_=0.5)
    for k in range(8):
        x = -31 + k * 8.9
        h = 8 + (k % 3) * 2
        fl.poly([(x - 3.3, 14), (x + 3.3, 14), (x + 0.4 * (k - 3.5) * 0.3, 14 + h)], mat='tooth', raise_=0.8, edge=0.1)
    # ------------------------------------------------ mandibula
    hx, hy = -34, 18
    ex = 42 * math.sqrt(1 - (20 / 41.0) ** 2)
    arc = []
    a0 = math.asin(20 / 41.0)
    for a in np.linspace(a0, math.pi - a0, 22):
        arc.append((42 * math.cos(a) - hx, 41 * math.sin(a) - hy + 1.0))
    jw = add('jaw', 'flesh', (hx, hy), z=5.5, mat='flesh', depth=12.0, noise=0.7, seed=95, tnoise=0.3)
    jw.poly(arc + [(-ex - hx, 20 - hy), (ex - hx, 20 - hy)][::-1][::-1])
    jw.hatch(3.2, 20, v=0.32, w=0.7, jit=0.6, seed=4)
    jw.cracks(4, 12, v=0.08, w=0.9, seed=96, emit=0.5)
    for k in range(7):
        x = -26 + k * 9.6 - hx
        h = 8 + (k % 2) * 3
        jw.poly([(x - 3.4, 20 - hy + 2), (x + 3.4, 20 - hy + 2), (x + 0.3, 20 - hy - h)], mat='tooth', raise_=0.8, edge=0.1)
    jw.poly([(-ex - hx + 4, 22 - hy), (ex - hx - 4, 22 - hy), (ex - hx - 6, 25 - hy), (-ex - hx + 6, 25 - hy)], op='emit', v=0.35, soft=0.7)
    # ------------------------------------------------ ojo
    ey = add('eye', 'flesh', (3, -12), z=4.6, mat='scl', depth=17.0, noise=0.3, seed=100, tnoise=0.15)
    ey.ell(0, 0, 28, 27)
    for a0_, a1_, c in ((200, 280, 0), (250, 350, 1), (110, 160, 2), (150, 190, 3), (310, 20, 4)):
        a = math.radians(a0_)
        b = math.radians(a1_)
        ey.line(bez((math.cos(a) * 27, math.sin(a) * 26), (math.cos((a + b) / 2) * 20 + c, math.sin((a + b) / 2) * 20 - c), (math.cos(b) * 13, math.sin(b) * 13), n=8), 0.8, op='tex', v=0.22)
    ey.cracks(4, 10, v=0.14, w=0.6, seed=101, emit=0.0)
    ir = add('iris', 'eye', (8, -1), z=4.7, mat='ir', depth=8.0, noise=0.2, seed=102, tnoise=0.1)
    ir.ell(0, 0, 16, 16)
    ir.ell(0, 0, 13.5, 13.5, op='emit', v=0.42, soft=1.2)
    ir.ell(0, 0, 8, 8, op='emit', v=0.62, soft=1.0)
    for k in range(18):
        a = k * math.pi * 2 / 18
        ir.line([(math.cos(a) * 6.5, math.sin(a) * 6.5), (math.cos(a + 0.12) * 14.5, math.sin(a + 0.12) * 14.5)], 0.7, op='emit', v=0.9, soft=0.15)
    pu = add('pupil', 'iris', (1.5, 0), z=4.8, mat='pup', depth=5.0, noise=0.1, seed=103)
    pu.ell(0, 0, 5.2, 11.5)
    pu.ell(0, 0, 3.0, 8.5, op='emit', v=0.5, soft=1.2)
    pu.ell(0, 0, 1.2, 4.5, op='emit', v=0.9, soft=0.8)
    gl = add('glint', 'iris', (-6.5, -7), z=4.9, mat='gl', depth=1.0)
    gl.ell(0, 0, 2.6, 2.2)
    gl.ell(0, 0, 2.4, 2.0, op='emit', v=1.0)
    gl.ell(3.5, 4.5, 1.1, 1.1, op='emit', v=0.7)
    gl.ell(3.5, 4.5, 1.1, 1.1)
    lt = add('lid_t', 'eye', (0, 0), z=5.6, mat='flesh', depth=6.0, noise=0.5, seed=104, tnoise=0.3)
    lt.spl([(-32, -2), (-30, -18), (-16, -32), (4, -35), (22, -29), (32, -12), (33, -3), (26, -14), (12, -21), (-4, -23), (-18, -17)])
    lt.hatch(3.0, 15, v=0.32, w=0.7, jit=0.5, seed=5)
    lt.cracks(2, 7, v=0.08, w=0.8, seed=105, emit=0.5)
    lb = add('lid_b', 'eye', (0, 0), z=5.6, mat='flesh', depth=5.0, noise=0.5, seed=106, tnoise=0.3)
    lb.spl([(-31, 4), (-22, 20), (-6, 30), (14, 30), (28, 18), (33, 6), (24, 16), (10, 22), (-8, 22), (-22, 14)])
    lb.hatch(3.0, 15, v=0.32, w=0.7, jit=0.5, seed=6)
    # ------------------------------------------------ ojos menores
    for k, (x, y) in enumerate(((-34, -4), (-21, -29), (-33, 12), (37, -4))):
        se = add('seye%d' % k, 'flesh', (x, y), z=5.0, mat='ir', depth=3.0, noise=0.1, seed=110 + k)
        se.ell(0, 0, 5.2, 4.2)
        se.ell(0, 0, 4.6, 3.6, op='emit', v=0.7, soft=0.5)
        se.ell(0.8, 0, 1.0, 3.2, mat='pup')
    return P


def make(anims, fxhook):
    parts = build_parts()
    return Boss('devorador_vacio', (192, 160), (96, 156), (84, 128), parts, MATS, anims, fxhook,
                outline=(10, 4, 24), rim=(210, 120, 255), rimk=0.42, dis_col=(200, 110, 255), seed=41, post=None, scale=1.0, base=0.46)


# ====================================================================== animacion
def PZ(*ds):
    return merge(*ds)


def ten(f, n, amp=1.0, base=1.0, lag=0.11, spd=1, curl=0.0, spread=0.0, ph=0.0, drag=0.0, lift=0.0):
    d = {}
    for k in range(7):
        sgn = -1 if TX[k] < 0 else 1
        bk = -(TX[k] / 36.0) * 24 * base
        for j in range(4):
            wave = amp * (5 + 3.2 * j) * math.sin(2 * math.pi * (spd * f / n - lag * j + k * 0.13 + ph))
            ang = wave
            if j == 0:
                ang += bk + drag - sgn * spread - sgn * lift * 0.5
                ang += curl * 3
            else:
                ang += curl * 9 - sgn * lift * 0.18 * (4 - j) * 0.5
            d['t%d_%d' % (k, j)] = ang
    return d


def eyes_open(a=0.0):
    k = 0.12 + 0.88 * a
    return {'seye%d.sy' % i: k for i in range(4)}


def look(x=0.0, y=0.0):
    return {'iris.x': x, 'iris.y': y}


def idle_pose(f):
    b = S(f, 6)
    return PZ({'body.y': -3.5 * b, 'jaw': 3 + 2 * b, 'body': 1.0 * b, 'horns.s': 1, 'lid_t.y': 0.5 * b}, ten(f, 6, 0.9, 1.0), eyes_open(0.0), look(0.8 * S(f, 6, 0.3), 0.5 * b),
              {'pupil.sx': 1 + 0.1 * b, 'iris.e': 1 + 0.1 * b})


def walk_pose(f):
    ph = 2 * math.pi * f / 8
    s = math.sin(ph); c = math.cos(ph)
    return PZ({'body.y': -4 * s - 2, 'body': 5 + 2 * c, 'jaw': 5 + 3 * c, 'body.x': 2 * c}, ten(f, 8, 1.4, 0.8, drag=18, spd=1), eyes_open(0.0), look(2, 0), {'lid_t.y': 1})


W1 = K([(0, PZ({}, {'jaw': 3})),
        (1, PZ({'body.x': -4, 'body': -4, 'jaw': 14, 'body.y': -3}, {'pupil.sx': 0.9, 'lid_t.y': 2})),
        (2, PZ({'body.x': -9, 'body': -8, 'jaw': 26, 'body.y': -7}, {'pupil.sx': 0.7, 'lid_t.y': 4, 'lid_b.y': -2})),
        (3, PZ({'body.x': -13, 'body': -11, 'jaw': 36, 'body.y': -9}, {'pupil.sx': 0.5, 'lid_t.y': 6, 'lid_b.y': -3})),
        (4, PZ({'body.x': -15, 'body': -13, 'jaw': 42, 'body.y': -10}, {'pupil.sx': 0.45, 'lid_t.y': 7, 'lid_b.y': -4}))])


def wind1(f):
    t = f / 4.0
    return PZ(W1(f), ten(f, 5, 0.6, 1.0, spread=-10 * t, curl=-1.4 * t, drag=16 * t), eyes_open(0), look(1 + 2 * t, 0), {'iris.e': 1 + 0.5 * t})


A1 = K([(0, PZ({'body.x': -15, 'body': -13, 'jaw': 42, 'body.y': -10}, {'pupil.sx': 0.45, 'lid_t.y': 7, 'lid_b.y': -4}), 'sm'),
        (1, PZ({'body.x': 8, 'body': 4, 'jaw': 44, 'body.y': -4}, {'pupil.sx': 0.5, 'lid_t.y': 7}), 'snap'),
        (2, PZ({'body.x': 28, 'body': 10, 'jaw': 22, 'body.y': 0}, {'pupil.sx': 0.6, 'lid_t.y': 6}), 'snap'),
        (3, PZ({'body.x': 36, 'body': 12, 'jaw': -2, 'body.y': 2}, {'pupil.sx': 0.8, 'lid_t.y': 6}), 'snap'),
        (4, PZ({'body.x': 36, 'body': 12, 'jaw': -2, 'body.y': 2}, {'pupil.sx': 0.8, 'lid_t.y': 6}), 'out'),
        (5, PZ({'body.x': 28, 'body': 9, 'jaw': 12, 'body.y': 0}), 'sm'),
        (6, PZ({'body.x': 14, 'body': 4, 'jaw': 8, 'body.y': -2}), 'sm'),
        (7, PZ({'jaw': 3}), 'sm')])


def atk1(f):
    return PZ(A1(f), ten(f, 8, 1.2, 1.0, drag=-20 * (1 if f < 6 else 0.3), spread=6, spd=1), eyes_open(0), look(3, 0))


W2 = K([(0, PZ({'jaw': 3})),
        (1, PZ({'body.x': -4, 'body.y': -5, 'body': -3, 'jaw': 8}, {'pupil.sx': 1.5})),
        (2, PZ({'body.x': -8, 'body.y': -9, 'body': -5, 'jaw': 14}, {'pupil.sx': 1.9})),
        (3, PZ({'body.x': -11, 'body.y': -12, 'body': -6, 'jaw': 20}, {'pupil.sx': 1.4})),
        (4, PZ({'body.x': -13, 'body.y': -13, 'body': -7, 'jaw': 24}, {'pupil.sx': 0.6}))])


def wind2(f):
    t = f / 4.0
    return PZ(W2(f), ten(f, 5, 0.9, 1.0, spread=14 * t, curl=0.4), eyes_open(t), look(3, 0), {'iris.e': 1 + 0.9 * t, 'lid_t.y': -3 * t, 'lid_b.y': 2 * t})


A2 = K([(0, PZ({'body.x': -13, 'body.y': -13, 'body': -7, 'jaw': 24}, {'pupil.sx': 0.6}), 'sm'),
        (1, PZ({'body.x': -17, 'body.y': -13, 'body': -9, 'jaw': 32}, {'pupil.sx': 0.35}), 'snap'),
        (2, PZ({'body.x': -22, 'body.y': -12, 'body': -10, 'jaw': 34}, {'pupil.sx': 0.3}), 'sm'),
        (3, PZ({'body.x': -22, 'body.y': -12, 'body': -10, 'jaw': 34}, {'pupil.sx': 0.3}), 'sm'),
        (4, PZ({'body.x': -22, 'body.y': -12, 'body': -9, 'jaw': 34}, {'pupil.sx': 0.35}), 'sm'),
        (5, PZ({'body.x': -20, 'body.y': -11, 'body': -8, 'jaw': 30}, {'pupil.sx': 0.5}), 'sm'),
        (6, PZ({'body.x': -10, 'body.y': -6, 'body': -4, 'jaw': 14}, {'pupil.sx': 0.9}), 'sm'),
        (7, PZ({'jaw': 3}), 'sm')])


def atk2(f):
    return PZ(A2(f), ten(f, 8, 1.4, 1.0, spread=14 * (1 - 0.7 * clamp01((f - 5) / 2.0)), curl=0.4, spd=2), eyes_open(1.0 if f < 6 else 0.5), look(3, 0), {'iris.e': 1.9, 'lid_t.y': -3, 'lid_b.y': 2})


W3 = K([(0, PZ({'jaw': 3})),
        (1, PZ({'body.y': -6, 'body': -3, 'jaw': 10})),
        (2, PZ({'body.y': -14, 'body': -5, 'jaw': 16})),
        (3, PZ({'body.y': -22, 'body': -6, 'jaw': 22})),
        (4, PZ({'body.y': -28, 'body': -6, 'jaw': 28})),
        (5, PZ({'body.y': -32, 'body': -7, 'jaw': 32}))])


def wind3(f):
    t = f / 5.0
    return PZ(W3(f), ten(f, 6, 0.9, 1.0, lift=50 * t, spread=10 * t, curl=1.4 * t, spd=1), eyes_open(t), look(1, -1), {'iris.e': 1 + 0.6 * t, 'lid_t.y': 1 * t})


A3 = K([(0, PZ({'body.y': -32, 'body': -7, 'jaw': 32}), 'sm'),
        (1, PZ({'body.y': -34, 'body': -4, 'jaw': 36}), 'sm'),
        (2, PZ({'body.y': -16, 'body': 4, 'jaw': 30}), 'in'),
        (3, PZ({'body.y': 14, 'body': 6, 'jaw': 22}), 'in'),
        (4, PZ({'body.y': 34, 'body': 4, 'jaw': 16, 'body.sy': 0.93, 'body.sx': 1.06}), 'snap'),
        (5, PZ({'body.y': 36, 'body': 3, 'jaw': 14, 'body.sy': 0.92, 'body.sx': 1.07}), 'sm'),
        (6, PZ({'body.y': 32, 'body': 2, 'jaw': 12, 'body.sy': 0.95, 'body.sx': 1.05}), 'sm'),
        (7, PZ({'body.y': 14, 'body': 0, 'jaw': 8}), 'sm'),
        (8, PZ({'jaw': 3}), 'sm')])


def atk3(f):
    i = f
    slam = clamp01((f - 2.0) / 2.0) * (1 - clamp01((f - 6.0) / 2.0))
    up = 1 - clamp01((f - 1.5) / 1.5)
    return PZ(A3(f), ten(f, 9, 0.8 * (1 - slam) + 0.3, 1.0, spread=70 * slam + 10 * up, lift=50 * up, curl=-0.4 * slam + 1.0 * up, spd=1, drag=0), eyes_open(1 if f < 7 else 0.4), look(1, 1), {'iris.e': 1.5})


CAST = K([(0, PZ({'jaw': 3})),
          (1, PZ({'body.y': -4, 'body': -2, 'jaw': 8})),
          (2, PZ({'body.y': -9, 'body': -5, 'jaw': 14}), 'sm'),
          (3, PZ({'body.y': -12, 'body': -7, 'jaw': 20}), 'sm'),
          (4, PZ({'body.y': -10, 'body': 3, 'body.x': 8, 'jaw': 30}), 'snap'),
          (5, PZ({'body.y': -8, 'body': 2, 'body.x': 5, 'jaw': 22}), 'out'),
          (6, PZ({'body.y': -4, 'body': 0, 'jaw': 10}), 'sm'),
          (7, PZ({'jaw': 3}), 'sm')])


def cast(f):
    up = clamp01(f / 3.0) * (1 - clamp01((f - 5) / 2.0))
    return PZ(CAST(f), ten(f, 8, 1.0, 1.0, lift=44 * up, curl=1.2 * up, spd=1), eyes_open(up), look(2, -1), {'iris.e': 1 + 0.9 * up, 'pupil.sx': 1.0 + 0.4 * up})


def hurt(f):
    i = int(f)
    d = [PZ({'body.x': -8, 'body': -8, 'body.y': 2, 'jaw': 24, 'lid_t.y': 12, 'lid_b.y': -8, 'tint': ((255, 230, 255), 0.55)}),
         PZ({'body.x': -4, 'body': -4, 'body.y': 0, 'jaw': 12, 'lid_t.y': 7, 'lid_b.y': -4, 'tint': ((255, 230, 255), 0.18)})][i]
    return PZ(d, ten(f, 2, 1.0, 1.0, spread=-18 + 8 * i, curl=-1.2 + 0.6 * i, spd=1), eyes_open(0.0), {'pupil.sx': 0.5})


PHK = K([(0, PZ({'jaw': 3})),
         (1, PZ({'body.s': 0.92, 'body.y': 2, 'jaw': 0, 'body': 4}, {'lid_t.y': 4}), 'sm'),
         (2, PZ({'body.s': 0.88, 'body.y': 4, 'jaw': 0, 'body': 6}, {'lid_t.y': 6, 'pupil.sx': 0.4}), 'sm'),
         (3, PZ({'body.s': 1.18, 'body.y': -12, 'jaw': 46, 'body': -8}, {'lid_t.y': -6, 'lid_b.y': 4, 'pupil.sx': 2.2, 'eye.s': 1.1}), 'snap'),
         (4, PZ({'body.s': 1.22, 'body.y': -14, 'jaw': 50, 'body': -10}, {'lid_t.y': -7, 'lid_b.y': 5, 'pupil.sx': 0.4, 'eye.s': 1.14}), 'sm'),
         (5, PZ({'body.s': 1.24, 'body.y': -15, 'jaw': 52, 'body': -9}, {'lid_t.y': -7, 'lid_b.y': 5, 'pupil.sx': 2.0, 'eye.s': 1.16}), 'sm'),
         (6, PZ({'body.s': 1.22, 'body.y': -14, 'jaw': 50, 'body': -10}, {'lid_t.y': -7, 'lid_b.y': 5, 'pupil.sx': 0.4, 'eye.s': 1.14}), 'sm'),
         (7, PZ({'body.s': 1.14, 'body.y': -10, 'jaw': 36, 'body': -6}, {'lid_t.y': -3, 'pupil.sx': 1.4, 'eye.s': 1.08}), 'sm'),
         (8, PZ({'body.s': 1.06, 'body.y': -6, 'jaw': 16, 'body': -2}, {'pupil.sx': 1.0, 'eye.s': 1.03}), 'sm'),
         (9, PZ({'jaw': 3}), 'sm')])


def phase(f):
    p = PHK(f)
    i = int(f)
    ex = [0, 0.1, 0.1, 1, 1, 1, 1, 1, 0.6, 0.2][i]
    fl = [0, 0, 0, 0.8, 1.2, 1.6, 1.4, 1.0, 0.6, 0.2][i]
    q = PZ(p, ten(f, 10, 1.4 + fl, 1.0, lift=60 * fl, curl=-0.8 * (1 - fl) + 0.6 * fl, spread=6 * fl, spd=2), eyes_open(ex), {'iris.e': 1 + fl, 'horns.s': 1 + 0.25 * fl, 'emit': 1 + 0.9 * fl})
    if 4 <= f <= 7:
        q['body.x'] = (1.2 if i % 2 else -1.2)
        q['tint'] = ((230, 150, 255), 0.16)
    return q


def intro(f):
    i = int(f)
    sc = [0.12, 0.12, 0.12, 0.14, 0.22, 0.3, 0.4, 0.52, 0.64, 0.78, 0.92, 1.08, 1.04, 1.0][i]
    if f != i and i < 13:
        sc2 = [0.12, 0.12, 0.12, 0.14, 0.22, 0.3, 0.4, 0.52, 0.64, 0.78, 0.92, 1.08, 1.04, 1.0][i + 1]
        sc = sc + (sc2 - sc) * (f - i)
    t = clamp01((f - 4) / 7.0)
    p = PZ({'body.s': sc, 'jaw': 3 + 38 * clamp01((f - 9) / 2.0) * (1 - clamp01((f - 12) / 1.5)), 'body.y': 0 if f < 11 else -2 * (f - 11)},
           ten(f, 14, 1.4, 1.0, spd=2, lift=40 * (1 - t), curl=1.5 * (1 - t)), eyes_open(clamp01((f - 9) / 3.0) * (1 - clamp01((f - 12) / 1.5))),
           look(2, 0), {'iris.e': 0.6 + 0.4 * t + (0.9 if 10 <= f <= 12 else 0), 'emit': 1 + (0.7 if 10 <= f <= 12 else 0)})
    if f < 4:
        p['clip'] = (0, 0, 0, 0)
    if 10 <= f <= 12:
        p['tint'] = ((235, 180, 255), 0.22)
    return p


DEATH = K([(0, PZ({'body.x': -8, 'body': -8, 'jaw': 24, 'lid_t.y': 12, 'lid_b.y': -8, 'tint': ((255, 230, 255), 0.6)}), 'out'),
           (1, PZ({'body.x': -6, 'body': -6, 'jaw': 30, 'body.y': 0, 'lid_t.y': 8, 'lid_b.y': -4, 'tint': ((255, 230, 255), 0.3)}), 'sm'),
           (2, PZ({'body.x': -2, 'body': -4, 'jaw': 38, 'body.y': -6, 'lid_t.y': 2, 'tint': ((255, 230, 255), 0.0)}), 'sm'),
           (4, PZ({'body.x': 0, 'body': 4, 'jaw': 44, 'body.y': -2, 'lid_t.y': -4, 'lid_b.y': 4, 'body.s': 1.08}), 'sm'),
           (6, PZ({'body.x': 0, 'body': -4, 'jaw': 50, 'body.y': 4, 'lid_t.y': -6, 'lid_b.y': 6, 'body.s': 1.2}), 'sm'),
           (7, PZ({'body.x': 0, 'body': 0, 'jaw': 54, 'body.y': 6, 'lid_t.y': -8, 'lid_b.y': 8, 'body.s': 1.28}), 'in'),
           (9, PZ({'body.x': 0, 'body': 0, 'jaw': 54, 'body.y': 10, 'body.s': 0.5}), 'in'),
           (13, PZ({'body.x': 0, 'body': 0, 'jaw': 54, 'body.y': 14, 'body.s': 0.06}), 'sm')])


def death(f):
    p = dict(DEATH(f))
    wob = (1.4 if int(f) % 2 else -1.4) if 2 <= f <= 6 else 0
    p['body.x'] = p.get('body.x', 0) + wob
    k = clamp01((f - 2) / 5.0)
    p['pupil.sx'] = 1 + 1.6 * k if f <= 7 else 2.6
    p['emit'] = 1 + 1.6 * k if f <= 8 else 2.6 * (1 - clamp01((f - 8) / 3.0)) + 0.4
    p['eye.s'] = 1 + 0.2 * k
    sag = clamp01((f - 1) / 4.0)
    p.update(ten(f, 14, 1.6 * (1 - sag) + 0.5, 1.0, lift=-30 * sag, curl=-1.6 * sag, spd=2))
    p.update(eyes_open(clamp01(1 - abs(f - 4) / 3.0)))
    p['horns.s'] = 1 + 0.1 * k
    if f >= 7.5:
        p['dis'] = clamp01((f - 7.5) / 4.0) * 1.12
        p['dis_dir'] = -1.0
    return p


# ====================================================================== efectos
def void_spike(ctx, x, y, h, w, a=1.0, layer='front', tilt=0.0):
    fx = ctx.fx
    tx = x + tilt
    fx.poly([(x - w - 1, y + 1), (tx, y - h - 1.5), (x + w + 1, y + 1)], (6, 2, 16), a, layer, ss=2)
    fx.poly([(x - w, y), (tx, y - h), (x + w, y)], (46, 18, 84), a, layer, ss=2)
    fx.poly([(x - w, y), (tx, y - h), (x - w * 0.2, y - h * 0.1)], (110, 50, 180), a, layer, ss=2)
    fx.polyline([(x - w * 0.7, y - 1), (tx - 0.5, y - h * 0.94)], 1, (226, 150, 255), a * 0.9, layer)
    fx.glow(x, y - h * 0.3, w * 2.5, (160, 70, 240), 0.35 * a)


def void_orb(ctx, x, y, s=1.0, ph=0.0):
    fx = ctx.fx
    fx.glow(x, y, 13 * s, (176, 76, 255), 0.85)
    fx.ell(x, y, 6.2 * s, 6.2 * s, (230, 150, 255), 1.0, 'front')
    fx.ell(x + 0.6, y + 0.6, 5.2 * s, 5.2 * s, (24, 8, 54), 1.0, 'front')
    fx.ell(x + 1.0, y + 1.0, 3.4 * s, 3.4 * s, (4, 0, 12), 1.0, 'front')
    fx.dots([(x - 2.6 * s, y - 2.8 * s)], (255, 240, 255), 1.0, 'front')
    fx.polyline([(x - 6 * s, y), (x - 16 * s, y + 1), (x - 28 * s, y + 0.5)], 3, (150, 60, 230), 0.45, 'front')
    fx.polyline([(x - 6 * s, y), (x - 14 * s, y), (x - 22 * s, y)], 1, (236, 190, 255), 0.7, 'front')


def rift(ctx, cx, cy, w, h, seed=3, a=1.0, glow=1.0, layer='back', stars=14, t=0.0):
    fx = ctx.fx
    if w < 0.8 or h < 2:
        return
    rng = np.random.default_rng(seed)
    n = 11
    jr = [rng.random() for _ in range(n)]
    jl = [rng.random() for _ in range(n)]

    def lens(k, inset=0.0):
        pts = []
        for u in range(n):
            uu = u / (n - 1)
            xx = (w / 2 - inset) * (math.sin(math.pi * uu) ** 0.7) * (0.75 + 0.5 * jr[u])
            pts.append((cx + xx, cy - h / 2 + h * uu))
        for u in range(n - 1, -1, -1):
            uu = u / (n - 1)
            xx = (w / 2 - inset) * (math.sin(math.pi * uu) ** 0.7) * (0.75 + 0.5 * jl[u])
            pts.append((cx - xx, cy - h / 2 + h * uu))
        return pts
    fx.glow(cx, cy, max(w, h * 0.5) * 0.9, (176, 76, 255), 0.5 * glow * a, rx=w * 0.8 + 6, ry=h * 0.6)
    fx.poly(lens(0, -2.0), (236, 150, 255), a, layer)
    fx.poly(lens(0, 0.5), (60, 16, 110), a, layer)
    fx.poly(lens(0, 3.0), (14, 4, 36), a, layer)
    fx.poly(lens(0, 6.0), (4, 0, 14), a, layer)
    # estrellas y remolino
    for k in range(stars):
        sx = cx + (rng.random() - 0.5) * w * 0.6
        sy = cy + (rng.random() - 0.5) * h * 0.7
        fx.dots([(sx, sy)], [(255, 255, 255), (214, 160, 255), (160, 90, 255)][k % 3], a * (0.5 + 0.5 * ((k + t * 5) % 2 > 1)), layer)
    fx.ring(cx, cy, max(1, w * 0.22), max(1, h * 0.25), 1, (120, 50, 210), 0.7 * a, layer, a0=20 + t * 200, a1=200 + t * 200)


def fxhook(ctx):
    n, i, fx = ctx.name, ctx.i, ctx.fx
    ax, ay = ctx.pivot
    W = ctx.W
    rng = ctx.rng
    px, py = ctx.anchor('pupil', (0, 0))
    ek = ctx.pose.get('emit', 1.0)
    bx, by = ctx.anchor('flesh', (0, 0))
    bs = ctx.pose.get('body.s', 1.0)
    if n not in ('intro', 'death') or (n == 'intro' and i >= 4) or (n == 'death' and i < 9):
        # aura oscura y resplandor del iris
        fx.ell(bx, by, 52 * bs, 50 * bs, (30, 10, 60), 0.35, 'back', soft=4.0)
        fx.glow(px, py, 16 * bs, (200, 110, 255), min(1.0, 0.5 * ek))
    if n not in ('intro', 'death'):
        wisps(ctx, bx, by - 6, 100, 100, 14, [(214, 160, 255), (176, 76, 255), (255, 255, 255)], seed=4, a=0.9, rise=-26)
        wisps(ctx, bx, by + 10, 90, 80, 10, [(40, 14, 70), (70, 26, 120)], seed=9, a=0.75, rise=24, size=2, layer='back')
    # --- ataque 1
    if n == 'windup1':
        t = i / 4.0
        mx, my = ctx.anchor('jaw', (30, 10))
        fx.glow(mx, my, 10 + 14 * t, (200, 100, 255), 0.35 + 0.5 * t)
        for k in range(6):
            ang = i * 0.8 + k * 1.05
            r = (22 - 12 * t) + 2
            fx.dots([(mx + math.cos(ang) * r, my + math.sin(ang) * r * 0.7)], (236, 190, 255), 0.9, 'front')
    if n == 'attack1':
        if 1 <= i <= 4:
            mx, my = ctx.anchor('jaw', (36, 4))
            tt = (i - 1) / 3.0
            fx.poly([(mx - 14, my - 24), (mx + 22, my - 8 * tt), (mx + 6, my + 14)], (236, 180, 255), 0.35 * (1 - tt * 0.3), 'front', ss=2)
            trail(ctx, 'flesh', (46, 6), (6, 6), 0, 4, (255, 240, 255), (110, 40, 200), steps=9, span=2.6, mid=(190, 100, 255), a=0.7)
        if 3 <= i <= 6:
            tt = (i - 3) / 3.0
            mx, my = ctx.anchor('jaw', (36, 4))
            impact_star(ctx, mx + 6, my + 2, tt, (240, 200, 255), 22)
            dust(ctx, min(mx + 6, W - 20), ay, tt, (120, 80, 170), 8, 30, 8, 2.4, a=0.7)
    # --- ataque 2: rayo del vacio
    if n == 'windup2':
        t = i / 4.0
        fx.glow(px, py, 12 + 18 * t, (210, 120, 255), 0.4 + 0.5 * t)
        for k in range(10):
            ang = i * 0.6 + k * 0.63 + k * 0.1
            d0 = 38 * (1 - 0.7 * t) + 6
            fx.dots([(px + math.cos(ang) * d0 * 1.4, py + math.sin(ang) * d0)], (236, 190, 255), 0.95, 'front')
            fx.line((px + math.cos(ang) * d0 * 1.4, py + math.sin(ang) * d0), (px + math.cos(ang) * (d0 - 6) * 1.4, py + math.sin(ang) * (d0 - 6)), 1, (190, 100, 255), 0.7, 'front')
        if i >= 3:
            fx.ell(px + 4, py, 2 + 3 * (i - 3), 2 + 3 * (i - 3), (255, 255, 255), 0.9, 'front', mode='over')
    if n == 'attack2':
        if 1 <= i <= 6:
            tt = clamp01((i - 1) / 5.0)
            ln = (W - 6 - px) * ease_out(clamp01(i / 2.0))
            wv = 11 * (1 - 0.45 * tt) * (1 + 0.1 * math.sin(i * 3.1))
            pts_u = [(px + k * ln / 12, py - wv * (0.55 + 0.45 * math.sin(k * 0.9 + i)) * (1 - 0.25 * k / 12)) for k in range(13)]
            pts_d = [(px + k * ln / 12, py + wv * (0.55 + 0.45 * math.sin(k * 0.9 + i + 2)) * (1 - 0.25 * k / 12)) for k in range(13)]
            fx.poly(pts_u + pts_d[::-1], (92, 24, 168), 0.7 * (1 - tt * 0.4), 'front', ss=2)
            f1u = [(x, py + (y - py) * 0.62) for x, y in pts_u]; f1d = [(x, py + (y - py) * 0.62) for x, y in pts_d]
            fx.poly(f1u + f1d[::-1], (190, 100, 255), 0.9 * (1 - tt * 0.3), 'front', ss=2)
            f2u = [(x, py + (y - py) * 0.28) for x, y in pts_u]; f2d = [(x, py + (y - py) * 0.28) for x, y in pts_d]
            fx.poly(f2u + f2d[::-1], (255, 240, 255), 0.95, 'front', ss=2)
            fx.glow(px + ln * 0.5, py, ln * 0.5, (176, 76, 255), 0.4 * (1 - tt * 0.5), rx=ln * 0.55, ry=16)
            fx.glow(px + ln, py, 16, (236, 180, 255), 0.8 * (1 - tt * 0.4))
            for k in range(6):
                xx = px + ((i * 17 + k * 41) % max(8, int(ln)))
                fx.line((xx, py + (k - 2.5) * 6), (xx - 12, py + (k - 2.5) * 6), 1, (236, 190, 255), 0.7 * (1 - tt * 0.5), 'front')
            fx.glow(px, py, 22, (255, 255, 255), 0.9 * (1 - tt * 0.5))
            rays(ctx, px, py, tt, (220, 150, 255), 10, 8, 30, 0.1, 0.5, i * 0.4, 'front', 'over')
    # --- ataque 3
    if n == 'windup3':
        t = i / 5.0
        fx.glow(bx, by, 40 + 20 * t, (176, 76, 255), 0.2 + 0.3 * t, rx=50, ry=46)
        wisps(ctx, ax, ay - 4, 80, 6, 10, [(176, 76, 255), (236, 190, 255)], t=t, seed=5, rise=-30, a=0.9)
    if n == 'attack3':
        if 4 <= i <= 8:
            t = (i - 4) / 4.0
            gx = ax
            ground_cracks(ctx, gx + 10, ay + 1, t, (10, 4, 24), (210, 120, 255), 10, 84, 61)
            ground_cracks(ctx, gx - 10, ay + 1, t, (10, 4, 24), (210, 120, 255), 8, 70, 63)
            shock(ctx, gx, ay, t, (214, 150, 255), 90, 9, 2)
            dust(ctx, gx, ay, t, (110, 70, 160), 14, 60, 16, 3.0)
            if i <= 7:
                for k, off in enumerate((-78, -62, -46, -30, 34, 50, 66, 82)):
                    pxx = gx + off + (k % 2) * 3
                    hh = (26 + 12 * ((k * 5) % 3)) * clamp01((i - 3.6 + abs(off) * 0.006) * 1.8) * (1 - t * 0.45)
                    if 5 < pxx < W - 5 and hh > 2:
                        void_spike(ctx, pxx, ay + 1, hh, 4.4, 1.0, 'front', tilt=(k % 3 - 1) * 2)
            if i == 4:
                fx.sparks(rng, gx, ay - 4, 24, 36, [(255, 255, 255), (220, 150, 255), (176, 76, 255)], 'front', 20)
    # --- cast: grieta y orbes
    if n == 'cast':
        up = clamp01(i / 3.0) * (1 - clamp01((i - 5) / 2.0))
        rift(ctx, ax - 22, ay - 112, 20 * up, 78 * up, seed=7, a=0.95, stars=10, t=i / 8.0)
        if 1 <= i <= 4:
            t = i / 4.0
            fx.glow(px, py, 14 + 14 * t, (220, 130, 255), 0.5 + 0.5 * t)
            for k in range(8):
                ang = i * 0.9 + k * 0.8
                r = 26 * (1 - t * 0.6) + 2
                fx.dots([(px + math.cos(ang) * r * 1.2, py + math.sin(ang) * r * 0.8)], (255, 235, 255), 1.0, 'front')
        if i >= 4:
            tt = (i - 4) / 3.0
            for k in range(4):
                ang = (k - 1.5) * 0.3
                d = 10 + tt * (44 + k * 8)
                sx_ = px + math.cos(ang) * d
                sy_ = py + math.sin(ang) * d * 0.7 + (k - 1.5) * 2 * tt - (k % 2) * 6 * tt
                if sx_ < W - 10:
                    void_orb(ctx, sx_, sy_, 0.95 - tt * 0.1, i * 0.7 + k)
    # --- fase
    if n == 'phase':
        t = clamp01((i - 3) / 4.0)
        if 3 <= i <= 9:
            fx.glow(bx, by, 62 * t + 20, (176, 76, 255), 0.6 * (1 - abs(t - 0.5) * 1.1), rx=70 * t + 20, ry=70 * t + 20)
            rays(ctx, bx, by, t, (214, 150, 255), 18, 20, 90, 0.08, 0.6, i * 0.14, 'back', 'over')
            shock(ctx, ax, ay, clamp01((i - 3) / 5.0), (214, 150, 255), 84, 8, 2)
            ring_r = 30 + 60 * ease_out(t)
            fx.ring(bx, by, ring_r, ring_r * 0.9, 2, (236, 190, 255), 0.7 * (1 - t * 0.7), 'front')
        if 4 <= i <= 8:
            wisps(ctx, bx, by, 150, 120, 34, [(214, 160, 255), (255, 255, 255), (176, 76, 255)], t=(i - 3) / 6.0, seed=22, rise=-50, a=1.0)
            rift(ctx, bx - 56, by - 6, 8 * t, 44 * t, seed=2, a=0.9, stars=6)
            rift(ctx, bx + 62, by - 14, 8 * t, 40 * t, seed=3, a=0.9, stars=6)
    if n == 'intro':
        intro_fx(ctx)
    if n == 'death':
        death_fx(ctx)


def intro_fx(ctx):
    i, fx, ax, ay = ctx.i, ctx.fx, ctx.pivot[0], ctx.pivot[1]
    rng = ctx.rng
    cx, cy = ax, ay - 92
    # apertura de la grieta
    openk = clamp01(i / 7.0)
    close = clamp01((i - 11) / 3.0)
    h = (14 + 96 * ease_out(openk)) * (1 - 0.92 * close)
    w = (2 + 76 * ease_out(clamp01((i - 2) / 6.0))) * (1 - 0.95 * close)
    a = 1.0 - 0.5 * close
    # arcos de energia al abrir
    if i < 6:
        for k in range(5):
            ang = rng.random() * 6.283
            fx.polyline([(cx, cy), (cx + math.cos(ang) * 30 * openk, cy + math.sin(ang) * 40 * openk)], 1, (230, 160, 255), 0.7, 'front')
    rift(ctx, cx, cy, w, h, seed=5, a=a, glow=1.2, stars=18, t=i / 14.0)
    if 3 <= i <= 12:
        rays(ctx, cx, cy, clamp01((i - 3) / 5.0), (190, 110, 255), 14, 20, 90, 0.07, 0.4, i * 0.1, 'back', 'over')
    if 4 <= i <= 12:
        wisps(ctx, cx, cy, 90, 100, 18, [(214, 160, 255), (176, 76, 255), (255, 255, 255)], t=(i - 4) / 8.0, seed=3, rise=-34, a=0.9)
    if 10 <= i <= 13:
        t = (i - 10) / 3.0
        shock(ctx, ax, ay, t, (214, 150, 255), 76, 8, 2)
        dust(ctx, ax, ay, t, (110, 70, 160), 10, 44, 10, 2.6)


def death_fx(ctx):
    i, fx, ax, ay = ctx.i, ctx.fx, ctx.pivot[0], ctx.pivot[1]
    rng = ctx.rng
    cx, cy = ax, ay - 92
    if 2 <= i <= 8:
        # grietas de luz del vacio sobre el cuerpo
        k = clamp01((i - 1) / 6.0)
        bx, by = ctx.anchor('flesh', (0, 0))
        rr = np.random.default_rng(17)
        for j in range(int(5 + 12 * k)):
            a = rr.random() * 6.283
            L = (14 + 36 * rr.random()) * clamp01(k * 1.5)
            x0, y0 = bx + math.cos(a) * 10, by + math.sin(a) * 10
            x1, y1 = bx + math.cos(a) * (10 + L), by + math.sin(a) * (10 + L)
            mx_, my_ = (x0 + x1) / 2 + (rr.random() - 0.5) * 6, (y0 + y1) / 2 + (rr.random() - 0.5) * 6
            fx.polyline([(x0, y0), (mx_, my_), (x1, y1)], 1, (255, 235, 255), 0.95, 'front')
            fx.polyline([(x0, y0), (mx_, my_), (x1, y1)], 3, (176, 76, 255), 0.35, 'front')
        fx.glow(bx, by, 30 + 30 * k, (220, 130, 255), 0.4 * k)
    if 7 <= i <= 8:
        k7 = 1.0 if i == 7 else 0.5
        fx.glow(cx, cy, 56 * k7 + 10, (240, 200, 255), 0.7 * k7)
        rays(ctx, cx, cy, 0.9, (255, 235, 255), 20, 8, 90, 0.06, 0.6 * k7, 0.2, 'front', 'add')
    if i >= 8:
        t = clamp01((i - 8) / 5.0)
        # particulas que espiralan hacia la singularidad
        r2 = np.random.default_rng(23)
        for k in range(40):
            a0 = r2.random() * 6.283
            r0 = 20 + 66 * r2.random()
            u = clamp01(t * 1.2 - 0.1 * r2.random())
            r = r0 * (1 - u)
            a = a0 + u * 5.0
            xx = cx + math.cos(a) * r * 1.2
            yy = cy + math.sin(a) * r * 0.9
            if r > 1:
                fx.dots([(xx, yy)], [(255, 255, 255), (214, 160, 255), (176, 76, 255)][k % 3], 0.95 * (1 - 0.3 * u), 'front', 1 + (k % 6 == 0))
        # la grieta residual que se cierra
        rw = max(0.0, 26 * (1 - t) ** 1.3)
        rift(ctx, cx, cy, rw, 70 * (1 - 0.5 * t) + 6, seed=8, a=1.0, stars=6, t=t)
        fx.glow(cx, cy, 20 * (1 - t) + 6, (214, 150, 255), 0.8 * (1 - t * 0.5))
        shock(ctx, cx, ay - 4, t, (176, 76, 255), 70, 6, 1, 0.8)
        # restos: motas flotantes y un diente
        wisps(ctx, cx, cy + 30, 70, 70, 12, [(214, 160, 255), (176, 76, 255)], t=t, seed=31, rise=-20, a=0.9)
        if t > 0.4:
            q = clamp01((t - 0.4) / 0.4)
            fx.poly([(ax + 10, ay - 1), (ax + 14, ay - 1), (ax + 12.4, ay - 8)], (232, 220, 182), q, 'back')
            fx.poly([(ax - 14, ay - 1), (ax - 10, ay - 1), (ax - 11.6, ay - 6)], (232, 220, 182), q, 'back')
            fx.glow(ax, ay - 2, 30, (176, 76, 255), 0.25 * q, rx=36, ry=5)


def hit_boxes():
    return {
        'attack1': dict(hit=[2, 4], box=[6, -138, 96, 130]),
        'attack2': dict(hit=[2, 5], box=[20, -124, 160, 48]),
        'attack3': dict(hit=[4, 6], box=[-92, -70, 188, 70]),
        'cast': dict(rel=4, muzzle_src=('pupil', (4, 0))),
    }


def spec():
    fns = dict(idle=idle_pose, walk=walk_pose, windup1=wind1, attack1=atk1, windup2=wind2, attack2=atk2, windup3=wind3,
               attack3=atk3, cast=cast, hurt=hurt, phase=phase, intro=intro, death=death)
    hb = hit_boxes()
    return {k: dict(pose=v, **hb.get(k, {})) for k, v in fns.items()}


def build():
    return make(spec(), fxhook)
