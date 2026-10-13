"""Biblioteca de sprites 16x16: props de suelo, colgantes, decoracion de pared, antorchas."""
import numpy as np
from kit import *

# ----------------------------------------------------------------- rampas genericas (oscuro -> claro)
BONE = ramp('#2a2630', '#625e6c', '#a09c92', '#d4d0bc', '#f2eed8')
WOOD = ramp('#1a120e', '#36251a', '#58401f', '#80602c', '#a88442')
IRON = ramp('#12141a', '#262a36', '#414858', '#646e86', '#929eb8')
RUST = ramp('#2a1410', '#52261a', '#7e3e22', '#a85e30', '#d08848')
GOLD = ramp('#34280e', '#74561c', '#b88c28', '#e8c04c', '#fff0a0')
COPPER = ramp('#2a1614', '#5a2e20', '#94502c', '#c8783a', '#f0a860')
VERD = ramp('#0e2428', '#1c4a44', '#2e7468', '#48a890', '#80dcc0')
MOSS = ramp('#0e220e', '#1d461a', '#357a28', '#5eb43a', '#9ee468')
ICE = ramp('#10284e', '#1c4880', '#3276b2', '#60aada', '#b4e6fa')
OBS = ramp('#080512', '#140c28', '#22154a', '#38236e', '#5a3ca0')
STONE_G = ramp('#14161e', '#252936', '#3a4052', '#566078', '#7c88a2')
CLOTH_R = ramp('#2a0a14', '#561224', '#861c36', '#b82c48', '#e0586c')
CLOTH_P = ramp('#180a2c', '#32185a', '#52288a', '#7a40b8', '#a870e0')
CLOTH_G = ramp('#0e2410', '#1c4a24', '#2e7a38', '#4cae52', '#88e088')
CLOTH_B = ramp('#0c1a38', '#183468', '#2656a0', '#4482d0', '#80b8f0')
CLOTH_Y = ramp('#3a280c', '#74501a', '#b88428', '#e8b840', '#fff0a0')
GLASS_W = ramp('#202838', '#486088', '#78a0d0', '#b8dcff', '#ffffff')

FL_ORANGE = ramp('#7a1e08', '#d8501a', '#ff9a2a', '#ffd860', '#fffbe0')
FL_BLUE = ramp('#14307a', '#2e74e0', '#6ac8ff', '#c0f0ff', '#ffffff')
FL_PURPLE = ramp('#34106a', '#8036d0', '#c064ff', '#eaaaff', '#fff2ff')
FL_AMBER = ramp('#6a3a08', '#c07a1c', '#ffbe48', '#ffe698', '#fffbe8')
FL_RED = ramp('#4a0818', '#a8122c', '#e83048', '#ff8a98', '#fff0f0')
FL_GOLD = ramp('#6a4a10', '#c4901c', '#f6cc44', '#fff09e', '#ffffff')
FL_GREEN = ramp('#0a3a24', '#1e8a56', '#4cf090', '#b4ffd4', '#ffffff')
FL_ELEC = ramp('#0e3a58', '#2e98d4', '#80dcff', '#dcf8ff', '#ffffff')
FL_WARM = ramp('#6a3010', '#d07020', '#ffb040', '#ffe090', '#fffbe8')


def ell(cx, cy, rx, ry):
    return ellipse_mask(cx, cy, rx, ry)


def circ(cx, cy, r):
    return ellipse_mask(cx, cy, r, r)


def ply(*pts):
    return poly_mask(pts)


def ln(x0, y0, x1, y1, w=1.0):
    return line_mask(x0, y0, x1, y1, w)


def rc(x0, y0, x1, y1):
    return rect_mask(x0, y0, x1, y1)


# ================================================================= PROPS DE SUELO
def skull(P, glow=False, tilt=0):
    B = P['bone']
    c = Canvas()
    c.shape(ell(8, 9.2, 4.6, 4.2), B)
    c.shape(rc(6, 11.5, 11, 14), B, base=.38)
    dark = B[0] * .45
    for x in (6, 9):
        c.px(x, 9, dark)
        c.px(x, 10, dark)
        c.px(x + 1, 10, dark)
    c.px(8, 11, dark)
    for x in (7, 9):
        c.px(x, 13, B[1])
    if glow:
        c.px(6, 9, P['eye'][3], True)
        c.px(9, 9, P['eye'][3], True)
    return c.outline()


def bone_at(c, B, x0, y0, x1, y1):
    c.shape(ln(x0, y0, x1, y1, 1.5), B, base=.6, shade=.6)
    for (x, y) in ((x0, y0), (x1, y1)):
        c.shape(circ(x, y, 1.3), B, base=.62, shade=.5)


def bones(P):
    B = P['bone']
    c = Canvas()
    bone_at(c, B, 2.5, 13.2, 11.5, 11.2)
    bone_at(c, B, 4, 10.5, 13, 13.4)
    bone_at(c, B, 6.5, 8.6, 9.5, 12.5)
    c.shape(circ(5, 12.2, 1.2), B, base=.5)
    return c.outline()


def ribs(P):
    B = P['bone']
    c = Canvas()
    c.shape(rc(7, 3, 9, 14), B, base=.45, shade=.4)
    for i, y in enumerate((5, 7.5, 10, 12.5)):
        w = 3 + (1.5 if i in (1, 2) else 0) - (i == 3) * .5
        c.shape(ply((8, y - .2), (8 - w - 1, y + 1), (8 - w - 1, y + 2.2), (8, y + 1.2)), B, base=.6)
        c.shape(ply((8, y - .2), (8 + w + 1, y + 1), (8 + w + 1, y + 2.2), (8, y + 1.2)), B, base=.35)
    return c.outline()


def mushroom(P, cap, spots, tall=7, cx=8, w=4.5, c=None, glow=None):
    own = c is None
    c = c or Canvas()
    S = P['shroom_stalk'] if 'shroom_stalk' in P else P['bone']
    top = 14 - tall
    c.shape(ply((cx - 1.2, 14), (cx - 1.0, top + 2), (cx + 1.0, top + 2), (cx + 1.2, 14)), S, base=.55)
    c.shape(ply((cx - w, top + 3.2), (cx - w + 1.4, top + .8), (cx - 2, top - .2), (cx + 2, top - .2), (cx + w - 1.4, top + .8), (cx + w, top + 3.2)), cap, base=.55)
    for (dx, dy) in spots:
        c.px(int(cx + dx), int(top + dy), cap[-1], glow is not None)
    return c.outline() if own else c


def shroom_small(P):
    return mushroom(P, P['cap'], [(-2, 1), (1, .5), (2, 2)], tall=6, w=4)


def shroom_tall(P):
    return mushroom(P, P['cap2'], [(-1, 1), (2, 2)], tall=9, w=3.5)


def shroom_cluster(P):
    c = Canvas()
    mushroom(P, P['cap'], [(-1, 1)], tall=5, cx=4.5, w=3.4, c=c)
    mushroom(P, P['cap2'], [(1, 1)], tall=9, cx=9, w=3.6, c=c)
    mushroom(P, P['cap'], [(0, 1)], tall=4, cx=12.5, w=2.8, c=c)
    return c.outline()


def grass(P, tall=8, n=5):
    G = P['moss']
    c = Canvas()
    r = rng(5 + tall)
    for i in range(n):
        x = 3 + i * 2 + r.randint(-1, 1)
        h = tall - r.randint(0, 3)
        lean = (i - n / 2) * .8
        c.shape(ply((x - .9, 14), (x + lean, 14 - h), (x + .9, 14)), G, base=.5, shade=.6)
    return c.outline()


def crystals(P, ramp_=None, h=(9, 12, 7), glow=True):
    R = ramp_ if ramp_ is not None else P['crystal']
    c = Canvas()
    spec = [(4.5, h[2], 2.3, -.6), (11.5, h[1] - 3, 2.2, .7), (8, h[0] + 2, 3.0, .2)]
    for (x, hh, w, lean) in sorted(spec, key=lambda s: s[1]):
        top = 14 - hh
        tx = x + lean * 2
        left = ply((x - w, 14), (x - w, top + 3), (tx, top), (x, 14))
        right = ply((x, 14), (tx, top), (x + w, top + 3), (x + w, 14))
        c.fill(left, R[3])
        c.fill(right, R[1])
        c.fill(ply((x - w, top + 3), (tx, top), (tx, top + 2.5), (x - w + .6, top + 4)), R[4])
        c.px(int(x), 13, R[0])
        c.fill(rc(int(x), top + 4, int(x) + 1, 13), R[2])
    return c.outline()


def rock(P, big=True):
    R = P['rockramp']
    c = Canvas()
    if big:
        c.shape(ell(6.5, 10.5, 5.2, 3.6), R, base=.5)
        c.shape(ell(11.5, 12, 3.2, 2.3), R, base=.45)
    else:
        c.shape(ell(5, 12, 3, 2), R, base=.5)
        c.shape(ell(10, 12.2, 2.4, 1.8), R, base=.5)
        c.shape(ell(8, 10.5, 1.8, 1.4), R, base=.55)
    return c.outline()


def barrel(P):
    W, M = P['wood'], P['metal']
    c = Canvas()
    c.shape(ply((4, 14), (3.4, 10), (4, 5), (12, 5), (12.6, 10), (12, 14)), W, base=.5)
    for y in (6, 12):
        c.fill(rc(4, y, 12, y + 1), M[2])
        c.fill(rc(4, y, 6, y + 1), M[3])
    c.fill(rc(4, 5, 12, 6), W[3])
    c.px(8, 9, W[0])
    c.px(8, 10, W[0])
    return c.outline()


def crate(P):
    W, M = P['wood'], P['metal']
    c = Canvas()
    c.shape(rc(3, 6, 13, 14), W, base=.5, shade=.7)
    c.fill(rc(3, 6, 13, 7), W[4])
    for x in (3, 12):
        c.fill(rc(x, 7, x + 1, 14), W[1])
    c.fill(ln(3.5, 7, 12.5, 14, 1), W[1])
    c.fill(ln(12.5, 7, 3.5, 14, 1), W[2])
    return c.outline()


def puddle(P, col=None):
    R = col if col is not None else P['liquid']
    c = Canvas()
    c.fill(ell(8, 13.2, 6.5, 1.8), R[1])
    c.fill(ell(8, 13, 5, 1.1), R[2])
    c.fill(ell(6.5, 12.7, 2, .6), R[4], True)
    c.px(10, 13, R[3], True)
    return c.outline(f=.5)


def candle_cluster(P):
    c = Canvas()
    W = P['wax'] if 'wax' in P else BONE
    FL = P['flame']
    for (x, h) in ((4, 5), (8, 8), (12, 4)):
        c.shape(rc(x - 1, 14 - h, x + 1, 14), W, base=.55)
        c.fill(rc(x - 1, 14 - h, x + 1, 15 - h), W[4])
        c.px(x - 1, 14 - h + 2, W[2])
        c.px(x, 14 - h - 1, FL[2], True)
        c.px(x, 14 - h - 2, FL[3], True)
        c.px(x, 14 - h - 3, FL[4] if h > 4 else FL[3], True)
    c.fill(ell(8, 14, 6.5, .7), W[1])
    return c.outline()


def tomb(P, cross=False):
    R = P['rockramp']
    c = Canvas()
    if cross:
        c.shape(rc(7, 2, 10, 14), R, base=.5, shade=.7)
        c.shape(rc(3, 5, 14, 8), R, base=.5, shade=.7)
    else:
        c.shape(ply((3.5, 14), (3.5, 6), (5, 3.4), (8, 2.4), (11, 3.4), (12.5, 6), (12.5, 14)), R, base=.5)
        c.fill(rc(7, 5, 9, 9), R[0])
        c.fill(rc(5.5, 6.5, 10.5, 8), R[0])
    c.px(5, 12, P['moss'][2])
    c.px(6, 12, P['moss'][2])
    c.px(5, 11, P['moss'][3])
    return c.outline()


def urn(P):
    R = P['urnramp'] if 'urnramp' in P else P['wood']
    c = Canvas()
    c.shape(ply((5.5, 14), (4, 10), (4.5, 7), (6, 5.5), (6.5, 4), (9.5, 4), (10, 5.5), (11.5, 7), (12, 10), (10.5, 14)), R, base=.5)
    c.fill(rc(6, 4, 10, 5), R[0])
    c.fill(rc(5, 9, 11, 10), R[3])
    return c.outline()


def chain_pile(P):
    M = P['metal']
    c = Canvas()
    for (x, y) in [(3, 12.5), (6, 11.5), (9, 12.7), (12, 11.8), (7, 13.3)]:
        c.shape(ell(x, y, 2.2, 1.4), M, base=.5, shade=.5, dither=False)
        c.erase(ell(x, y, 1.0, .5))
    return c.outline()


def embers(P):
    R = P['rockramp']
    FL = P['flame']
    c = Canvas()
    c.shape(ell(7, 12, 5.5, 2.6), R, base=.3)
    c.shape(ell(11.5, 12.8, 3, 1.6), R, base=.35)
    for (x, y, k) in ((5, 11, 3), (7, 12, 2), (9, 11, 3), (11, 12, 2), (6, 13, 2), (10, 13, 3), (8, 10, 4)):
        c.px(x, y, FL[k], True)
    return c.outline()


def snow_mound(P):
    S = P['snow']
    c = Canvas()
    c.shape(ply((1, 14), (2, 11), (5, 9), (8, 8.5), (11, 9.5), (14, 12), (15, 14)), S, base=.62, shade=.5)
    c.fill(ln(3, 11.5, 6, 9.8, 1), S[4])
    return c.outline(f=.55)


def stump(P):
    W = P['wood']
    c = Canvas()
    c.shape(ply((3, 14), (4.5, 9), (4, 6), (12, 6), (11.5, 9), (13, 14)), W, base=.5, shade=.7)
    c.fill(ell(8, 6.2, 4, 1.4), W[3])
    c.fill(ell(8, 6.2, 2.4, .8), W[2])
    c.px(8, 6, W[1])
    for x in (5, 7, 10):
        c.px(x, 10, W[1])
        c.px(x, 11, W[1])
    return c.outline()


def vines(P):
    G = P['moss']
    c = Canvas()
    for x, h in ((4, 10), (8, 7), (11, 9)):
        c.shape(ln(x, 14, x + (1 if x < 8 else -1), 14 - h, 1.2), G, base=.5, shade=.4, dither=False)
        for k in range(2, h, 3):
            c.px(x + 1, 14 - k, G[3])
            c.px(x - 1, 13 - k, G[2])
    return c.outline()


def flowers(P):
    G = P['moss']
    FL = P['bloom']
    c = Canvas()
    for x, h in ((4, 6), (8, 9), (12, 5)):
        c.fill(ln(x, 14, x, 14 - h, 1), G[2])
        c.px(x - 1, 14 - h // 2, G[3])
        c.px(x, 14 - h, FL[3], True)
        c.px(x - 1, 14 - h, FL[2], True)
        c.px(x + 1, 14 - h, FL[2], True)
        c.px(x, 14 - h - 1, FL[2], True)
        c.px(x, 15 - h, FL[4], True)
    return c.outline()


def anvil(P):
    M = P['metal']
    c = Canvas()
    c.shape(ply((2, 6), (14, 6), (13, 8), (10, 8.5), (10, 11), (12, 14), (4, 14), (6, 11), (6, 8.5), (3, 8)), M, base=.55)
    c.fill(rc(2, 6, 14, 7), M[4])
    c.fill(ln(1, 6.5, 4, 8, 1), M[3])
    return c.outline()


def gargoyle(P):
    R = P['rockramp']
    c = Canvas()
    c.shape(ply((4, 14), (4, 9), (6, 7), (6, 4), (8, 2.5), (10, 4), (10, 7), (12, 9), (12, 14)), R, base=.5)
    c.shape(ply((4, 9), (1, 5), (3, 7), (5, 8)), R, base=.4)
    c.shape(ply((12, 9), (15, 5), (13, 7), (11, 8)), R, base=.3)
    c.px(7, 5, P['eye'][3], True)
    c.px(9, 5, P['eye'][3], True)
    c.px(6, 3, R[4])
    c.px(10, 3, R[3])
    return c.outline()


def lamp_post(P):
    M = P['metal']
    FL = P['flame']
    c = Canvas()
    c.shape(rc(7, 7, 9, 14), M, base=.45, shade=.6)
    c.shape(rc(5, 13, 11, 14.5), M, base=.45)
    c.shape(ply((5, 7), (11, 7), (10, 3), (6, 3)), M, base=.4)
    c.fill(rc(6, 4, 10, 7), FL[2], True)
    c.fill(rc(7, 4, 9, 6), FL[3], True)
    c.px(8, 5, FL[4], True)
    c.fill(rc(5, 2, 11, 3), M[3])
    c.fill(rc(7, 1, 9, 2), M[2])
    return c.outline()


def bench(P):
    W, M = P['wood'], P['metal']
    c = Canvas()
    c.shape(rc(2, 8, 14, 10), W, base=.55, shade=.6)
    c.shape(rc(3, 4, 13, 6), W, base=.5, shade=.6)
    for x in (3, 12):
        c.shape(rc(x, 10, x + 1, 14), M, base=.4)
        c.shape(rc(x, 6, x + 1, 8), M, base=.4)
    return c.outline()


def thorns(P):
    G = P['thorn']
    c = Canvas()
    for (x, y, x2, y2) in [(2, 14, 7, 4), (6, 14, 8, 2), (10, 14, 13, 5), (13, 14, 14, 9), (4, 14, 2, 8), (8, 14, 11, 8)]:
        c.shape(ply((x - .8, y), (x2, y2), (x + .8, y)), G, base=.5, shade=.5, dither=False)
    return c.outline()


def books(P):
    c = Canvas()
    cols = [P['book1'], P['book2'], P['book3']]
    y = 14
    for i, (w, h) in enumerate([(10, 2), (8, 3), (9, 2)]):
        x0 = 3 + (i % 2)
        c.shape(rc(x0, y - h, x0 + w, y), cols[i], base=.5, shade=.7)
        c.fill(rc(x0, y - h, x0 + 1, y), cols[i][1])
        c.fill(rc(x0 + 1, y - 1, x0 + w, y), BONE[2])
        y -= h
    return c.outline()


def coffin(P):
    W = P['wood']
    c = Canvas()
    c.shape(ply((7, 3), (11, 6), (12, 14), (4, 14), (5, 6)), W, base=.5, shade=.7)
    c.fill(rc(7, 5, 9, 11), W[3])
    c.fill(rc(5.5, 7, 10.5, 8.2), W[3])
    return c.outline()


def sword_ground(P):
    M = P['metal']
    c = Canvas()
    c.shape(rc(7.2, 2, 8.8, 11), M, base=.6, shade=.6, dither=False)
    c.fill(rc(7, 1, 9, 2), M[4])
    c.fill(rc(4, 10.5, 12, 12), P['hilt'][3])
    c.fill(rc(4, 10.5, 12, 11), P['hilt'][4])
    c.fill(rc(7, 12, 9, 14), P['hilt'][2])
    return c.outline()


def brazier(P):
    M = P['metal']
    FL = P['flame']
    c = Canvas()
    c.shape(ply((4, 8), (12, 8), (10.5, 11), (9, 11), (10, 14), (6, 14), (7, 11), (5.5, 11)), M, base=.5)
    c.fill(rc(3, 7, 13, 8.5), M[3])
    for (x, y, k) in ((6, 6, 2), (8, 5, 3), (10, 6, 2), (7, 4, 2), (9, 3, 3), (8, 2, 2)):
        c.px(x, y, FL[k], True)
    c.fill(rc(7, 4, 10, 7), FL[2], True)
    c.px(8, 5, FL[4], True)
    c.px(8, 6, FL[3], True)
    return c.outline()


def crow(P):
    R = P['rockramp']
    c = Canvas()
    c.shape(ell(8, 12.2, 5, 2.4), R, base=.5)
    c.shape(ell(6.5, 7.5, 2.6, 3.2), P['feather'], base=.5)
    c.shape(ply((9, 8), (14, 9), (9, 11)), P['feather'], base=.4)
    c.shape(ply((6, 5), (4, 6), (6, 6.6)), P['beak'], base=.6)
    c.px(7, 6, P['eye'][3], True)
    return c.outline()


def col_stub(P):
    R = P['rockramp']
    c = Canvas()
    c.shape(ply((4, 14), (5, 12), (5, 5), (6, 3.5), (9, 4.5), (11, 4), (11, 12), (12, 14)), R, base=.5, shade=.8)
    c.fill(rc(4, 12.5, 12, 14), R[2])
    c.fill(rc(6, 3.5, 9, 4.5), R[4])
    c.fill(ln(8, 5, 7, 9, 1), R[1])
    return c.outline()


def void_tendril(P):
    R = P['rockramp']
    G = P['glow']
    c = Canvas()
    pts = [(8, 14), (7, 11), (9, 8), (7, 5), (9, 2.5)]
    for i in range(len(pts) - 1):
        c.shape(ln(*pts[i], *pts[i + 1], 2.2 - i * .4), R, base=.4, shade=.5, dither=False)
    c.px(9, 2, G[3], True)
    c.px(7, 7, G[2], True)
    c.shape(ell(4, 13, 2.2, 1.5), R, base=.4)
    c.shape(ell(12, 13, 2, 1.4), R, base=.4)
    c.px(4, 12, G[2], True)
    return c.outline()


def gold_pile(P):
    G = P['gold']
    c = Canvas()
    c.shape(ply((1, 14), (3, 10), (6, 7), (9, 6), (12, 9), (15, 14)), G, base=.55, shade=.6)
    for (x, y) in ((5, 10), (8, 8), (11, 11), (7, 12), (3, 13), (12, 13)):
        c.px(x, y, G[4], True)
        c.px(x + 1, y, G[1])
    c.shape(circ(10.5, 7.2, 1.4), G, base=.7)
    return c.outline()


def bell(P):
    G = P['gold']
    c = Canvas()
    c.shape(ply((4, 14), (5, 9), (6, 5), (8, 3), (10, 5), (11, 9), (12, 14)), G, base=.55)
    c.fill(rc(7, 1, 9, 3), G[2])
    c.fill(rc(4, 12, 12, 14), G[2])
    c.fill(ln(6, 6, 6, 11, 1), G[4])
    c.px(8, 13, G[0])
    return c.outline()


def tesla_coil(P):
    M = P['metal']
    C = P['copper']
    FL = P['flame']
    c = Canvas()
    c.shape(rc(5, 12, 11, 14.5), M, base=.45)
    for i, y in enumerate((11, 9, 7, 5)):
        w = 3.2 - i * .4
        c.shape(rc(8 - w, y, 8 + w, y + 1.6), C, base=.55)
    c.fill(rc(7.5, 4, 8.5, 12), M[3])
    c.shape(circ(8, 3, 1.8), C, base=.6)
    c.px(5, 2, FL[3], True)
    c.px(4, 1, FL[4], True)
    c.px(11, 2, FL[3], True)
    c.px(12, 3, FL[2], True)
    c.px(8, 1, FL[4], True)
    return c.outline()


def gear(P):
    M = P['metal']
    c = Canvas()
    for k in range(8):
        a = k * np.pi / 4
        c.shape(circ(8 + 5 * np.cos(a), 8.5 + 5 * np.sin(a), 1.5), M, base=.5, dither=False)
    c.shape(circ(8, 8.5, 4.6), M, base=.55)
    c.erase(circ(8, 8.5, 1.4))
    c.px(8, 8, M[0])
    return c.outline()


def valve(P):
    M = P['metal']
    c = Canvas()
    c.shape(rc(2, 11, 14, 14), M, base=.5, shade=.7)
    c.shape(rc(7, 7, 9, 11), M, base=.45)
    c.shape(rc(4, 6, 12, 7.6), P['copper'], base=.55)
    c.px(2, 12, M[4])
    c.px(13, 12, M[4])
    c.px(8, 10, P['flame'][2], True)
    return c.outline()


def hand(P):
    B = P['skin']
    c = Canvas()
    c.shape(ply((6, 14), (6.4, 9), (10, 9), (10.6, 14)), B, base=.5, dither=False)
    for (x, h) in ((5.6, 6), (7.2, 4.4), (8.8, 4), (10.4, 5)):
        c.shape(rc(x - .6, 14 - h - 3, x + .6, 10), B, base=.55, dither=False)
    return c.outline()


def fence(P):
    M = P['metal']
    c = Canvas()
    for x in (2, 6, 10, 14):
        c.shape(rc(x - .5, 4, x + .5, 14), M, base=.5, shade=.6, dither=False)
        c.fill(ply((x - 1, 4), (x, 1.5), (x + 1, 4)), M[3])
    c.fill(rc(1, 7, 15.5, 8.4), M[3])
    c.fill(rc(1, 11, 15.5, 12.2), M[2])
    return c.outline()


def orb_pedestal(P):
    R = P['rockramp']
    FL = P['flame']
    c = Canvas()
    c.shape(ply((5, 14), (6, 10), (10, 10), (11, 14)), R, base=.5)
    c.shape(rc(4, 9, 12, 10.6), R, base=.55)
    c.shape(circ(8, 6, 3.2), FL, base=.6, shade=.7)
    c.fill(circ(7, 5, 1), FL[4], True)
    return c.outline()


def cocoon(P):
    c = Canvas()
    S = P['bone']
    c.shape(ell(8, 9, 3.6, 5), S, base=.6, shade=.6)
    for y in (7, 9, 11):
        c.fill(ln(5, y, 11, y + 1, 1), S[2])
    c.fill(ell(8, 14, 5, .8), P['moss'][1])
    return c.outline()


def cauldron(P):
    M = P['metal']
    FL = P['flame']
    c = Canvas()
    c.shape(ell(8, 10, 5.5, 4.2), M, base=.5)
    c.fill(rc(3, 7, 13, 8.4), M[3])
    c.fill(ell(8, 7.7, 4.4, 1.0), FL[2], True)
    c.px(7, 7, FL[4], True)
    c.shape(rc(4, 13, 6, 14.5), M, base=.4)
    c.shape(rc(10, 13, 12, 14.5), M, base=.4)
    return c.outline()


def bush_dead(P):
    W = P['wood']
    c = Canvas()
    for (x, y, x2, y2, w) in [(8, 14, 8, 6, 1.6), (8, 10, 3, 5, 1.2), (8, 9, 13, 4, 1.2), (6, 8, 4, 2.5, .9), (10, 8, 12, 2, .9)]:
        c.shape(ln(x, y, x2, y2, w), W, base=.5, shade=.5, dither=False)
    return c.outline()


def ice_spikes(P):
    R = P['ice']
    c = Canvas()
    for (x, hh, w) in ((3, 7, 1.6), (6, 12, 2.0), (9.5, 9, 1.8), (13, 6, 1.5), (7.5, 5, 1.3)):
        top = 14 - hh
        c.fill(ply((x - w, 14), (x, top), (x, 14)), R[3])
        c.fill(ply((x, 14), (x, top), (x + w, 14)), R[1])
        c.px(int(x) - 1 if w > 1.4 else int(x), top + 2, R[4])
    c.fill(rc(1, 13.5, 15, 14.6), R[2])
    return c.outline()


# ================================================================= COLGANTES (pegados arriba)
def h_chain(P, links=7, ox=8):
    M = P['metal']
    c = Canvas()
    for i in range(links):
        y = i * 2.1
        if i % 2 == 0:
            c.shape(ell(ox, y + 1.2, 1.5, 1.4), M, base=.5, dither=False)
            c.erase(ell(ox, y + 1.2, .6, .6))
        else:
            c.shape(rc(ox - .5, y, ox + .5, y + 2.4), M, base=.55, dither=False)
    return c.outline()


def h_chain_hook(P):
    M = P['metal']
    c = h_chain(P, 5, 8)
    c2 = Canvas()
    c2.shape(ln(8, 10, 8, 12, 1), M, base=.5, dither=False)
    c2.shape(ply((8, 12), (11, 13), (10, 15), (7, 14.5)), M, base=.5, dither=False)
    c2.erase(circ(9, 13.5, .6))
    c.blit(c2.outline())
    return c


def h_chains2(P):
    c = Canvas()
    c.blit(h_chain(P, 8, 4))
    c.blit(h_chain(P, 5, 11))
    return c


def h_stalactite(P, ramp_=None, w=5.5, hh=12, ox=8):
    R = ramp_ if ramp_ is not None else P['rockramp']
    c = Canvas()
    c.shape(ply((ox - w, 0), (ox + w, 0), (ox + w * .45, hh * .55), (ox + .6, hh), (ox - .3, hh), (ox - w * .5, hh * .5)), R, base=.5, shade=1.0)
    c.fill(rc(ox - w, 0, ox + w, 1), R[1])
    return c.outline()


def h_stalactites(P, ramp_=None):
    R = ramp_ if ramp_ is not None else P['rockramp']
    c = Canvas()
    c.blit(h_stalactite(P, R, 3.2, 9, 3.5))
    c.blit(h_stalactite(P, R, 4, 14, 9.5))
    c.blit(h_stalactite(P, R, 2.4, 6, 14))
    return c


def h_roots(P):
    W = P['wood']
    c = Canvas()
    for (x, x2, y2, w) in [(3, 1.5, 14, 1.4), (7, 8.5, 11, 1.8), (11, 10, 15, 1.2), (14, 15, 9, 1.0)]:
        c.shape(ply((x - w, 0), (x + w, 0), (x2 + .5, y2), (x2 - .5, y2)), W, base=.5, shade=.6, dither=False)
    return c.outline()


def h_vines(P):
    G = P['moss']
    c = Canvas()
    for (x, h) in ((3, 11), (7, 14), (11, 8), (14, 12)):
        for y in range(h):
            xx = x + int(round(np.sin(y * .6 + x) * 1.0))
            c.px(xx, y, G[2] if y % 3 else G[3])
            if y % 4 == 2:
                c.px(xx + 1, y, G[3])
                c.px(xx - 1, y + 1, G[1])
        c.px(x, h, G[4])
    return c.outline()


def h_web(P):
    c = Canvas()
    W = P['bone']
    for (x2, y2) in ((0, 12), (3, 13), (7, 10), (11, 8), (15, 6)):
        c.fill(ln(0, 0, x2, y2, .7), W[2])
    for r_ in (4, 7, 10):
        pts = [(r_ * np.cos(a), r_ * np.sin(a)) for a in np.linspace(0, 1.57, 5)]
        for i in range(len(pts) - 1):
            c.fill(ln(*pts[i], *pts[i + 1], .7), W[3])
    return c.outline(f=.5)


def h_banner(P, cloth=None, emb=None):
    C = cloth if cloth is not None else P['cloth']
    c = Canvas()
    c.fill(rc(2, 0, 14, 1.3), P['metal'][3])
    c.shape(ply((3, 1.3), (13, 1.3), (13, 12), (8, 14.5), (3, 12)), C, base=.5, shade=.7)
    c.fill(rc(3, 1.3, 4, 12), C[3])
    c.fill(rc(12, 1.3, 13, 12), C[1])
    if emb == 'cross':
        c.fill(rc(7.2, 3, 8.8, 11), P['gold'][3])
        c.fill(rc(5, 5, 11, 6.4), P['gold'][3])
    elif emb == 'eye':
        c.fill(ell(8, 7, 3, 1.7), P['gold'][3])
        c.fill(circ(8, 7, 1), C[0])
    elif emb == 'sun':
        c.fill(circ(8, 7, 2), P['gold'][4])
        for (dx, dy) in ((0, -3), (0, 3), (-3, 0), (3, 0)):
            c.px(8 + dx, 7 + dy, P['gold'][3])
    return c.outline()


def h_lantern(P):
    M = P['metal']
    FL = P['flame']
    c = Canvas()
    c.fill(rc(7.5, 0, 8.5, 3), M[3])
    c.shape(ply((5, 3.5), (11, 3.5), (12, 5), (4, 5)), M, base=.5)
    c.shape(rc(4.5, 5, 11.5, 12), M, base=.4)
    c.fill(rc(5.5, 6, 10.5, 11), FL[2], True)
    c.fill(rc(6.5, 7, 9.5, 10), FL[3], True)
    c.px(8, 8, FL[4], True)
    c.shape(rc(4, 12, 12, 13.5), M, base=.45)
    c.px(8, 14, M[3])
    return c.outline()


def h_bones(P):
    c = Canvas()
    c.blit(h_chain(P, 3, 8))
    c.blit(skull(P), 0, 1)
    c.erase(rc(0, 15, 16, 16))
    return c


def h_ribs(P):
    B = P['bone']
    c = Canvas()
    c.fill(rc(7.5, 0, 8.5, 12), B[2])
    for i, y in enumerate((2, 4.5, 7, 9.5)):
        w = 3.5
        c.shape(ply((8, y), (8 - w, y + 1.5), (8 - w, y + 2.7), (8, y + 1.2)), B, base=.6)
        c.shape(ply((8, y), (8 + w, y + 1.5), (8 + w, y + 2.7), (8, y + 1.2)), B, base=.4)
    return c.outline()


def h_drips(P, liquid=None):
    L = liquid if liquid is not None else P['liquid']
    c = Canvas()
    for (x, h) in ((3, 6), (6, 11), (10, 8), (13, 5)):
        for y in range(h):
            c.px(x, y, L[2] if y < h - 1 else L[3])
        c.px(x, h, L[4], True)
    c.fill(rc(0, 0, 16, 2), L[1])
    c.fill(rc(0, 0, 16, 1), L[2])
    return c.outline(f=.5)


def h_icicles(P):
    return h_stalactites(P, P['ice'])


def h_cables(P):
    M = P['metal']
    c = Canvas()
    for (x, h, s) in ((3, 12, 1), (8, 15, -1), (12, 9, 1)):
        for y in range(h):
            xx = x + int(round(np.sin(y * .5 + x) * 1.2 * s))
            c.px(xx, y, M[2] if y % 2 else M[1])
        c.px(x, h - 1, P['flame'][3], True)
    c.fill(rc(0, 0, 16, 1), M[3])
    return c.outline()


def h_moss(P):
    G = P['moss']
    c = Canvas()
    c.shape(ply((0, 0), (16, 0), (15, 3), (12, 6), (9, 4), (7, 8), (4, 5), (1, 4)), G, base=.5, shade=.7)
    for (x, h) in ((3, 9), (9, 11), (13, 7)):
        c.fill(rc(x, 5, x + 1, h), G[2])
        c.px(x, h, G[4])
    return c.outline()


def h_hooks(P):
    M = P['metal']
    c = Canvas()
    for (x, h) in ((4, 7), (11, 10)):
        c.fill(rc(x, 0, x + 1, h), M[3])
        c.fill(ln(x + .5, h, x + 2.5, h + 2.5, 1), M[3])
        c.fill(ln(x + 2.5, h + 2.5, x - .5, h + 4, 1), M[2])
    c.shape(ell(11.5, 14, 2.4, 1.3), P['meat'], base=.5)
    c.fill(rc(11, 10, 12, 13), P['metal'][2])
    return c.outline()


def h_tendrils(P):
    R = P['rockramp']
    G = P['glow']
    c = Canvas()
    for (x, h, s) in ((3, 11, 1), (7, 15, -1), (11, 9, 1), (14, 13, -1)):
        for y in range(h):
            xx = x + int(round(np.sin(y * .45 + x) * 1.6 * s))
            wd = 1.0 if y < h * .6 else 0.5
            c.fill(rc(xx - wd, y, xx + wd, y + 1), R[2] if y % 2 else R[1])
        c.px(x, h, G[3], True)
    c.fill(rc(0, 0, 16, 2), R[1])
    return c.outline()


def h_stars(P):
    G = P['gold']
    c = Canvas()
    c.fill(rc(0, 0, 16, 1), P['metal'][2])
    for (x, h) in ((3, 8), (8, 12), (13, 6)):
        c.fill(rc(x, 1, x + 1, h), P['metal'][2])
        c.px(x, h + 1, G[4], True)
        c.px(x - 1, h + 1, G[3], True)
        c.px(x + 1, h + 1, G[3], True)
        c.px(x, h + 2, G[3], True)
        c.px(x, h, G[3], True)
    return c.outline()


def h_pipe(P):
    M = P['metal']
    c = Canvas()
    c.shape(rc(0, 0, 16, 4), M, base=.5, shade=.8)
    for x in (3, 12):
        c.fill(rc(x, 0, x + 2, 4), M[3])
    c.shape(rc(7, 4, 9, 9), M, base=.45)
    c.px(8, 10, P['liquid'][3], True)
    c.px(8, 12, P['liquid'][2], True)
    return c.outline()


def h_bell(P):
    G = P['gold']
    c = Canvas()
    c.fill(rc(7.5, 0, 8.5, 2.5), P['metal'][3])
    c.shape(ply((4, 12), (5, 7), (6, 4), (8, 2.5), (10, 4), (11, 7), (12, 12)), G, base=.55)
    c.fill(rc(4, 11, 12, 12.6), G[2])
    c.fill(ln(6, 5, 6, 10, 1), G[4])
    c.shape(circ(8, 13.5, 1.2), G, base=.5)
    return c.outline()


def h_bat(P):
    B = P['batcol']
    c = Canvas()
    c.fill(rc(4, 0, 12, 1), P['metal'][2])
    c.shape(ell(8, 6.5, 2.6, 3.8), B, base=.45)
    c.shape(ply((5.5, 3), (1, 5), (2, 11), (4, 9.5), (5.5, 11), (5.5, 7)), B, base=.35, dither=False)
    c.shape(ply((10.5, 3), (15, 5), (14, 11), (12, 9.5), (10.5, 11), (10.5, 7)), B, base=.3, dither=False)
    c.px(7, 5, P['eye'][3], True)
    c.px(9, 5, P['eye'][3], True)
    return c.outline()


def h_gargoyle_drain(P):
    R = P['rockramp']
    c = Canvas()
    c.shape(rc(0, 0, 16, 3), R, base=.5, shade=.7)
    c.shape(ply((4, 3), (12, 3), (12, 8), (9, 12), (7, 12), (4, 8)), R, base=.5)
    c.px(6, 6, P['eye'][3], True)
    c.px(10, 6, P['eye'][3], True)
    c.fill(rc(7, 9, 9, 12), R[0])
    return c.outline()


def h_cloth(P):
    C = P['cloth']
    c = Canvas()
    c.shape(ply((0, 0), (16, 0), (15, 6), (13, 9), (11, 6), (9, 12), (7, 7), (5, 10), (3, 6), (1, 8)), C, base=.45, shade=.9)
    for x in (3, 7, 11):
        c.fill(rc(x, 1, x + 1, 5), C[3])
    return c.outline()


def h_crystal(P, ramp_=None):
    R = ramp_ if ramp_ is not None else P['crystal']
    c = Canvas()
    for (x, hh, w) in ((4, 8, 2.4), (8.5, 14, 3.0), (12.5, 6, 2.0)):
        c.fill(ply((x - w, 0), (x, 0), (x + .5, hh)), R[3])
        c.fill(ply((x, 0), (x + w, 0), (x + .5, hh)), R[1])
        c.fill(ln(x - .3, 0, x + .3, hh - 3, .8), R[4], True)
    return c.outline()


# ================================================================= DECORACION DE PARED
def w_shield(P, c1=None):
    C = c1 if c1 is not None else P['cloth']
    M = P['metal']
    c = Canvas()
    c.shape(ply((3, 2), (13, 2), (13, 8), (8, 14.5), (3, 8)), M, base=.5)
    c.shape(ply((4.2, 3.2), (11.8, 3.2), (11.8, 8), (8, 12.8), (4.2, 8)), C, base=.5)
    c.fill(rc(7.2, 3.2, 8.8, 12), P['gold'][3])
    c.fill(rc(4.2, 6, 11.8, 7.2), P['gold'][3])
    return c.outline()


def w_rune(P, g=1):
    R = P['rockramp']
    G = P['glow']
    c = Canvas()
    c.shape(rc(2, 1, 14, 15), R, base=.45, shade=.5)
    pts = [[(5, 4), (8, 3), (11, 4), (8, 8), (5, 12), (11, 12)],
           [(8, 3), (8, 12), (5, 6), (11, 6)],
           [(5, 4), (11, 4), (5, 12), (11, 12), (8, 8)],
           [(6, 3), (6, 12), (10, 3), (10, 12), (6, 7)]][g % 4]
    for i in range(len(pts) - 1):
        c.fill(ln(*pts[i], *pts[i + 1], 1), G[2], True)
    for (x, y) in pts[::2]:
        c.px(int(x), int(y), G[4], True)
    return c.outline()


def w_skull_plaque(P):
    R = P['rockramp']
    c = Canvas()
    c.shape(rc(2, 2, 14, 15), R, base=.45, shade=.5)
    c.blit(skull(P), 0, 0)
    return c.outline()


def w_window(P, glass, arch=True):
    R = P['rockramp']
    c = Canvas()
    if arch:
        c.shape(ply((2, 15), (2, 6), (4, 3), (8, 1), (12, 3), (14, 6), (14, 15)), R, base=.5)
        inner = ply((3.5, 15), (3.5, 6.5), (5, 4.5), (8, 3), (11, 4.5), (12.5, 6.5), (12.5, 15))
    else:
        c.shape(rc(2, 2, 14, 15), R, base=.5)
        inner = rc(3.5, 3.5, 12.5, 15)
    c.fill(inner, glass[2], True)
    c.fill(rc(7.2, 3, 8.8, 15) & inner, R[1])
    c.fill(rc(3.5, 8.6, 12.5, 9.6) & inner, R[1])
    c.fill(rc(3.5, 10, 7.2, 14) & inner, glass[3], True)
    c.fill(rc(9, 11, 12.5, 15) & inner, glass[1], True)
    return c.outline()


def w_vitral(P, cols):
    R = P['rockramp']
    c = Canvas()
    c.shape(ply((2, 15), (2, 6), (4, 3), (8, 1), (12, 3), (14, 6), (14, 15)), R, base=.5)
    inner = ply((3.5, 15), (3.5, 6.5), (5, 4.5), (8, 3), (11, 4.5), (12.5, 6.5), (12.5, 15))
    yy, xx = np.mgrid[0:16, 0:16]
    cell = ((xx - 3) // 3 + ((yy - 3) // 3) * 3) % len(cols)
    for ky in range(len(cols)):
        m = inner & (cell == ky)
        c.fill(m, cols[ky][2], True)
        c.fill(m & ((xx + yy) % 5 == 0), cols[ky][3], True)
    c.fill(rc(7.4, 3, 8.6, 15) & inner, R[0])
    c.fill(rc(3.5, 8.5, 12.5, 9.5) & inner, R[0])
    return c.outline()


def w_chains(P):
    M = P['metal']
    c = Canvas()
    c.shape(ell(8, 2, 1.5, 1.2), M, base=.6)
    for i in range(5):
        y = 3 + i * 2.2
        if i % 2:
            c.shape(rc(7.5, y, 8.5, y + 2.4), M, base=.55, dither=False)
        else:
            c.shape(ell(8, y + 1.2, 1.5, 1.3), M, base=.5, dither=False)
            c.erase(ell(8, y + 1.2, .5, .5))
    c.shape(rc(4, 13, 12, 15), M, base=.45)
    return c.outline()


def w_swords(P):
    M = P['metal']
    c = Canvas()
    for sgn in (1, -1):
        x0, x1 = (3, 13) if sgn > 0 else (13, 3)
        c.shape(ln(x0, 2, x1, 13, 1.5), M, base=.6, shade=.5, dither=False)
        c.fill(ln(x0 + sgn * .6, 9.5, x1 - sgn * 2.2, 8, 1), P['hilt'][3])
    c.shape(circ(8, 7.5, 1.4), P['gold'], base=.6)
    return c.outline()


def w_eye(P):
    R = P['rockramp']
    G = P['glow']
    c = Canvas()
    c.shape(ell(8, 8, 6.6, 6), R, base=.45, shade=.5)
    c.fill(ell(8, 8, 4.6, 2.6), G[1], True)
    c.fill(ell(8, 8, 3.2, 2.4), G[3], True)
    c.fill(rc(7.2, 6.4, 8.8, 9.6), R[0])
    c.px(7, 7, G[4], True)
    return c.outline()


def w_sun(P):
    G = P['gold']
    c = Canvas()
    for k in range(8):
        a = k * np.pi / 4
        c.shape(ply((8 + 4 * np.cos(a - .3), 8 + 4 * np.sin(a - .3)), (8 + 7.2 * np.cos(a), 8 + 7.2 * np.sin(a)), (8 + 4 * np.cos(a + .3), 8 + 4 * np.sin(a + .3))), G, base=.6, dither=False)
    c.shape(circ(8, 8, 4), G, base=.65)
    c.fill(circ(8, 8, 2), P['rockramp'][0])
    return c.outline()


def w_moon(P):
    G = P['moon']
    c = Canvas()
    c.shape(circ(8, 8, 6), G, base=.6, shade=.7)
    c.erase(circ(11, 7, 5))
    return c.outline()


def w_cross(P):
    B = P['bone']
    c = Canvas()
    c.shape(rc(7, 1, 9, 15), B, base=.55, shade=.7)
    c.shape(rc(3, 4, 13, 6), B, base=.55, shade=.7)
    return c.outline()


def w_bonepile(P):
    c = Canvas()
    B = P['bone']
    c.shape(rc(2, 2, 14, 15), P['rockramp'], base=.35, shade=.4)
    for (x0, y0, x1, y1) in ((3, 4, 13, 5), (3, 8, 13, 9), (3, 12, 13, 13)):
        bone_at(c, B, x0, y0, x1, y1)
    return c.outline()


def w_tattered(P):
    C = P['cloth']
    c = Canvas()
    c.fill(rc(3, 0, 13, 1.4), P['metal'][3])
    c.shape(ply((4, 1.4), (12, 1.4), (12, 10), (10.5, 8.5), (9, 13), (7.5, 9), (6, 12), (4, 9)), C, base=.45, shade=.9)
    c.fill(rc(4, 1.4, 5, 8), C[3])
    return c.outline()


def w_painting(P):
    c = Canvas()
    G = P['gold']
    c.shape(rc(2, 2, 14, 14), G, base=.55)
    inner = rc(4, 4, 12, 12)
    c.fill(inner, P['paint'][1])
    c.fill(rc(4, 9, 12, 12), P['paint'][0])
    c.fill(circ(8, 7, 1.5) & inner, P['paint'][3], True)
    return c.outline()


def w_sign(P):
    c = Canvas()
    W = P['wood']
    c.shape(rc(2, 3, 14, 11), W, base=.5, shade=.7)
    c.fill(rc(3, 5, 13, 6), W[1])
    c.fill(rc(3, 8, 11, 9), W[1])
    c.fill(rc(7.5, 11, 8.5, 15), W[2])
    return c.outline()


def w_blood_hand(P):
    c = Canvas()
    L = P['liquid']
    R = P['rockramp']
    c.shape(rc(1, 1, 15, 15), R, base=.4, shade=.4)
    c.fill(ply((4, 12), (4, 7), (5, 5), (6, 7), (6, 4), (7.5, 4), (7.5, 7), (9, 3), (10, 3.5), (10, 8), (12, 6), (12.5, 8), (11, 12)), L[2])
    c.fill(rc(5, 9, 11, 11), L[3])
    return c.outline()


# ================================================================= ANTORCHAS / LUCES (animadas)
def flame(c, cx, by, f, FL, h=8, w=2.6, sway=1.0):
    hh = [h, h + 1.6, h - 1.4, h + .6][f % 4]
    sx = [0, 1.6, .2, -1.6][f % 4] * (sway / 1.0)
    ww = w * [1.0, .88, 1.1, .94][f % 4]
    lean = [0, .8, 0, -.8][f % 4]
    pts = [(cx - ww, by), (cx - ww * 1.15 + lean * .4, by - hh * .35), (cx - ww * .55 + lean * .8, by - hh * .72), (cx + sx, by - hh),
           (cx + ww * .55 + lean * .8, by - hh * .72), (cx + ww * 1.15 + lean * .4, by - hh * .35), (cx + ww, by)]
    c.fill(ply(*pts), FL[1], True)
    c.fill(ply(*[(cx + (x - cx) * .72 + lean * .3, by + (y - by) * .8) for x, y in pts]), FL[2], True)
    c.fill(ply(*[(cx + (x - cx) * .44, by + (y - by) * .55) for x, y in pts]), FL[3], True)
    c.fill(ply(*[(cx + (x - cx) * .22, by + (y - by) * .3) for x, y in pts]), FL[4], True)
    r = rng(f * 7 + 3)
    for k in range(2):
        x = cx + (r.rand() - .5) * 5
        y = by - hh - 1 - r.rand() * 3 - (f % 2)
        if 0 <= y < 16:
            c.px(int(x), int(y), FL[3 - k % 2], True)


def torch_generic(P, f):
    FL = P['flame']
    M = P['metal']
    c = Canvas()
    c.shape(ply((5, 9), (11, 9), (10, 12), (6, 12)), M, base=.5)
    c.fill(rc(5, 9, 11, 10), M[4])
    c.shape(rc(7, 12, 9, 15), M, base=.45)
    c.shape(rc(5, 14, 11, 16), M, base=.4)
    flame(c, 8, 9, f, FL, h=7)
    return c.outline()


def torch_bone(P, f):
    B = P['bone']
    FL = P['flame']
    c = Canvas()
    c.shape(ell(8, 11.5, 3.6, 3), B, base=.55)
    c.shape(rc(6, 13.5, 10, 15.5), B, base=.4)
    c.px(6, 11, B[0] * .4)
    c.px(9, 11, B[0] * .4)
    c.px(7, 13, B[0])
    c.px(8, 13, B[0])
    c.fill(rc(5.5, 8, 10.5, 9.5), B[3])
    flame(c, 8, 9, f, FL, h=7, w=2.4)
    return c.outline()


def torch_brazier(P, f):
    FL = P['flame']
    M = P['metal']
    c = Canvas()
    c.shape(ply((3, 9), (13, 9), (11.5, 12), (4.5, 12)), M, base=.5)
    c.fill(rc(3, 9, 13, 10), M[4])
    for x in (5, 8, 11):
        c.fill(rc(x, 10, x + 1, 12), M[1])
    c.shape(rc(7, 12, 9, 15), M, base=.45)
    c.shape(rc(4, 14, 12, 16), M, base=.4)
    flame(c, 8, 9, f, FL, h=8, w=3.4)
    return c.outline()


def floating_flame(P, f):
    FL = P['flame']
    c = Canvas()
    oy = [0, -1, 0, 1][f % 4]
    c.shape(ply((6, 15), (10, 15), (9, 12 + oy), (7, 12 + oy)), P['rockramp'], base=.4)
    flame(c, 8, 11 + oy, f, FL, h=8, w=2.8, sway=1.5)
    return c.outline()


def torch_wood(P, f):
    FL = P['flame']
    W = P['wood']
    c = Canvas()
    c.shape(rc(7, 8, 9, 15), W, base=.5, shade=.7)
    c.shape(ply((6, 6.5), (10, 6.5), (9, 9), (7, 9)), W, base=.45)
    c.fill(rc(6, 6.5, 10, 7.5), P['metal'][3])
    flame(c, 8, 7, f, FL, h=7, w=2.6)
    return c.outline()


def candelabra(P, f):
    FL = P['flame']
    M = P['metal']
    W = P['wax'] if 'wax' in P else BONE
    c = Canvas()
    c.shape(rc(7, 8, 9, 15), M, base=.5)
    c.shape(ply((3, 8), (13, 8), (13, 9.5), (8, 11), (3, 9.5)), M, base=.5)
    c.shape(rc(5, 14, 11, 16), M, base=.4)
    for x, ph in ((4, 1), (8, 0), (12, 2)):
        top = 5 if x != 8 else 3
        c.shape(rc(x - 1, top + 2, x + 1, 8), W, base=.55)
        c.fill(rc(x - 1, top + 2, x + 1, top + 3), W[4])
        ff = (f + ph) % 4
        c.px(x, top + 1, FL[2], True)
        c.px(x, top, FL[3], True)
        if ff in (1, 3):
            c.px(x, top - 1, FL[3], True)
            c.px(x, top - 2, FL[4], True)
        else:
            c.px(x, top - 1, FL[4], True)
    return c.outline()


def gas_lamp(P, f):
    FL = P['flame']
    M = P['metal']
    c = Canvas()
    c.shape(rc(7, 10, 9, 15), M, base=.5)
    c.shape(rc(4, 14, 12, 16), M, base=.4)
    c.shape(ply((5, 4), (11, 4), (12, 5), (11.5, 10), (4.5, 10), (4, 5)), M, base=.4)
    c.fill(rc(5.5, 5.5, 10.5, 9.5), FL[1 + (f % 2 == 0)], True)
    c.fill(rc(6.5, 6, 9.5, 9), FL[2], True)
    c.fill(rc(7, 6.5, 9, 8.5), FL[3], True)
    c.px(8, 7, FL[4], True)
    c.fill(rc(5, 2.5, 11, 4), M[3])
    c.fill(rc(7, 1, 9, 2.5), M[2])
    return c.outline()


def sun_brazier(P, f):
    FL = P['flame']
    G = P['gold']
    c = Canvas()
    c.shape(ply((4, 10), (12, 10), (10.5, 13), (5.5, 13)), G, base=.5)
    c.fill(rc(4, 10, 12, 11), G[4])
    c.shape(rc(7, 13, 9, 15), G, base=.45)
    c.shape(rc(4.5, 14.5, 11.5, 16), G, base=.4)
    flame(c, 8, 10, f, FL, h=8, w=3.0)
    return c.outline()


def tesla_torch(P, f):
    C = P['copper']
    M = P['metal']
    FL = P['flame']
    c = Canvas()
    c.shape(rc(4, 13.5, 12, 16), M, base=.45)
    c.shape(rc(7, 8, 9, 14), C, base=.55)
    for y in (10, 12):
        c.fill(rc(6, y, 10, y + 1), C[3])
    c.shape(circ(8, 7, 2.6), C, base=.62)
    r = rng(f * 29 + 11)
    c.fill(circ(8, 7, 1) , FL[3], True)
    dirs = [(-1, -1), (1, -1), (0, -1), (-1, 0), (1, 0), (-1, 1) if False else (1, -1)]
    chosen = r.choice(len(dirs), 3, replace=False)
    for ci in chosen:
        dx, dy = dirs[ci]
        x, y = 8 + dx * 3, 7 + dy * 3
        for s_ in range(r.randint(3, 5)):
            if 0 <= x < 16 and 0 <= y < 16:
                c.px(int(x), int(y), FL[4] if s_ % 2 == 0 else FL[3], True)
            x += dx + r.randint(-1, 1) * (1 if dx == 0 else 0) * 1
            y += dy + r.randint(-1, 1) * (1 if dy == 0 else 0) * 1
    return c.outline()


def crystal_pulse(P, f, ramp_=None):
    R = ramp_ if ramp_ is not None else P['crystal']
    c = Canvas()
    k = [0, 1, 2, 1][f % 4]
    c.shape(ply((4, 15), (5, 12.5), (11, 12.5), (12, 15)), P['rockramp'], base=.4)
    for (x, hh, w, lean) in ((5, 7, 1.9, -.6), (11, 6, 1.7, .6), (8, 11, 2.4, 0)):
        top = 13 - hh
        tx = x + lean * 2
        lft = ply((x - w, 13), (x - w, top + 3), (tx, top), (x, 13))
        rgt = ply((x, 13), (tx, top), (x + w, top + 3), (x + w, 13))
        c.fill(lft, R[3 if k < 2 else 4], True)
        c.fill(rgt, R[1 + (k > 0)], True)
        c.fill(ply((x - w, top + 3), (tx, top), (tx, top + 2), (x - w + .5, top + 4)), R[4], True)
        c.px(int(x), 12, R[0])
    if k == 2:
        for (x, y) in ((8, 1), (7, 2), (9, 2), (8, 3)):
            c.px(x, y, R[4] if (x, y) == (8, 2) or y == 1 else R[3], True)
    elif k == 1:
        c.px(8, 2, R[3], True)
    return c.outline()


def orb_light(P, f):
    FL = P['flame']
    k = [0, 1, 2, 1][f % 4]
    c = Canvas()
    c.shape(ply((5, 15), (6, 12), (10, 12), (11, 15)), P['rockramp'], base=.4)
    c.shape(circ(8, 8, 3.8 + (k == 2) * .4), FL, base=.65, shade=.5)
    c.fill(circ(7, 7, 1.2), FL[4], True)
    if k == 2:
        c.px(8, 2, FL[3], True)
        c.px(2, 8, FL[3], True)
        c.px(14, 8, FL[3], True)
    return c.outline()


def mushroom_light(P, f):
    c = Canvas()
    k = [0, 1, 2, 1][f % 4]
    G = P['gl_ramp']
    mushroom(P, G, [(-1, 1), (1, 2)], tall=6, cx=5, w=3.4, c=c, glow=True)
    mushroom(P, G, [(0, 1)], tall=9, cx=10, w=3.8, c=c, glow=True)
    if k:
        for (x, y) in ((3, 6), (12, 3), (8, 4)):
            c.px(x, y, G[4], True)
    return c.outline()


def w_bolt(P):
    R = P['rockramp']
    G = P['glow']
    c = Canvas()
    c.shape(ell(8, 8, 6.6, 6.6), R, base=.45, shade=.5)
    c.fill(ply((9.5, 2), (5.5, 8.5), (8, 8.5), (6.5, 14), (11, 6.5), (8.5, 6.5)), G[2], True)
    c.fill(ply((9, 4), (7, 8), (8.5, 8), (7.7, 11), (9.6, 7), (8.2, 7)), G[4], True)
    return c.outline()
