"""Atlas de 127 iconos 16x16."""
from common import *

YY, XX = np.mgrid[0:16, 0:16] + 0.5


def R5(*c):
    return [tuple(x) for x in c]


RP = {
    'steel': R5((36, 40, 64), (84, 94, 126), (138, 152, 184), (196, 208, 232), (244, 248, 255)),
    'gold': R5((88, 50, 22), (156, 102, 36), (222, 166, 54), (255, 212, 96), (255, 246, 170)),
    'red': R5((56, 6, 24), (120, 12, 36), (188, 26, 46), (240, 68, 68), (255, 150, 130)),
    'fire': R5((110, 22, 20), (200, 58, 20), (250, 118, 24), (255, 184, 60), (255, 238, 150)),
    'ice': R5((28, 54, 128), (58, 118, 200), (108, 188, 240), (178, 236, 255), (244, 255, 255)),
    'yel': R5((110, 72, 8), (200, 150, 16), (255, 212, 40), (255, 242, 120), (255, 255, 224)),
    'green': R5((18, 56, 32), (36, 108, 50), (72, 166, 68), (138, 222, 100), (214, 255, 160)),
    'purple': R5((34, 14, 70), (78, 36, 138), (128, 68, 204), (182, 124, 250), (236, 200, 255)),
    'pink': R5((76, 12, 72), (146, 28, 126), (218, 58, 188), (255, 118, 220), (255, 200, 246)),
    'wood': R5((38, 24, 20), (78, 50, 32), (122, 82, 46), (170, 120, 68), (214, 166, 104)),
    'stone': R5((32, 30, 38), (68, 64, 74), (108, 102, 110), (152, 144, 148), (198, 190, 188)),
    'bone': R5((78, 68, 70), (138, 126, 118), (194, 184, 168), (232, 224, 206), (255, 250, 236)),
    'dark': R5((12, 8, 22), (30, 20, 46), (54, 38, 76), (82, 60, 108), (120, 94, 148)),
    'white': R5((108, 114, 148), (168, 176, 204), (212, 218, 240), (240, 244, 255), (255, 255, 255)),
    'blue': R5((22, 44, 120), (40, 84, 196), (70, 140, 250), (132, 196, 255), (214, 240, 255)),
    'cyan': R5((12, 70, 100), (24, 130, 160), (60, 200, 216), (140, 240, 240), (230, 255, 255)),
    'orange': R5((120, 50, 14), (190, 90, 24), (240, 140, 40), (255, 190, 80), (255, 232, 160)),
    'copper': R5((70, 34, 24), (130, 70, 40), (190, 112, 60), (230, 160, 90), (255, 208, 140)),
    'teal': R5((14, 56, 60), (28, 104, 100), (60, 164, 140), (126, 222, 180), (210, 255, 226)),
    'lava': R5((60, 20, 20), (130, 30, 16), (230, 70, 16), (255, 150, 30), (255, 226, 110)),
}


class Ic:
    def __init__(s):
        s.img = np.zeros((16, 16, 4))

    def L(s, mask, ramp, edge=True, bias=0.0):
        mask = mask.astype(bool)
        if not mask.any():
            return
        ramp = RP[ramp] if isinstance(ramp, str) else ramp
        rgb, idx = shade_mask(mask, ramp, bias=bias)
        d = ndi.distance_transform_edt(np.pad(mask, 1))[1:-1, 1:-1]
        if edge and d.max() >= 2.0:
            er = ndi.binary_erosion(mask, np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool))
            bd = mask & ~er
            right = bd & ~np.roll(mask, -1, 1)
            down = bd & ~np.roll(mask, -1, 0)
            rgb = rgb.copy()
            rgb[right | down] = ramp[0] if d.max() >= 2.6 else ramp[1]
        s.img[mask, :3] = rgb[mask]
        s.img[mask, 3] = 255

    def _pc(s):
        return PC(16, 16, 4, cov=0.5)

    def poly(s, pts, ramp, **k):
        pc = s._pc()
        pc.poly(pts, (255, 255, 255))
        s.L(pc.out()[..., 3] > 0, ramp, **k)

    def circ(s, cx, cy, r, ramp, **k):
        s.L(((XX - cx) ** 2 + (YY - cy) ** 2) <= r * r, ramp, **k)

    def ell(s, cx, cy, rx, ry, ramp, **k):
        s.L((((XX - cx) / rx) ** 2 + ((YY - cy) / ry) ** 2) <= 1, ramp, **k)

    def rect(s, x0, y0, x1, y1, ramp, **k):
        s.L((XX >= x0) & (XX < x1) & (YY >= y0) & (YY < y1), ramp, **k)

    def line(s, p0, p1, w, ramp, **k):
        pc = s._pc()
        pc.line(p0, p1, (255, 255, 255), w)
        pc.circ(p0[0], p0[1], w / 2, (255, 255, 255))
        pc.circ(p1[0], p1[1], w / 2, (255, 255, 255))
        s.L(pc.out()[..., 3] > 0, ramp, **k)

    def lines(s, pts, w, ramp, **k):
        pc = s._pc()
        pc.lines(pts, (255, 255, 255), w)
        s.L(pc.out()[..., 3] > 0, ramp, **k)

    def arc(s, cx, cy, r0, r1, a0, a1, ramp, **k):
        d = np.hypot(XX - cx, YY - cy)
        a = np.degrees(np.arctan2(YY - cy, XX - cx))
        q = ((a - a0) % 360) <= ((a1 - a0) % 360)
        s.L((d >= r0) & (d <= r1) & q, ramp, **k)

    def ring(s, cx, cy, r0, r1, ramp, **k):
        d = np.hypot(XX - cx, YY - cy)
        s.L((d >= r0) & (d <= r1), ramp, **k)

    def bmp(s, rows, cmap, ox=0, oy=0):
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch in cmap:
                    c = cmap[ch]
                    if isinstance(c, tuple) and isinstance(c[0], str):
                        c = RP[c[0]][c[1]]
                    s.img[oy + y, ox + x, :3] = c[:3]
                    s.img[oy + y, ox + x, 3] = 255

    def px(s, x, y, col):
        if isinstance(col, tuple) and isinstance(col[0], str):
            col = RP[col[0]][col[1]]
        s.img[int(y), int(x), :3] = col[:3]
        s.img[int(y), int(x), 3] = 255

    def hl(s, pts, col):
        for p in pts:
            s.px(p[0], p[1], col)

    def finish(s):
        return outline(s.img, 0.26, tint=(0.9, 0.8, 1.15), diag=False, alpha_min=200)


# ---------- piezas reutilizables ----------
def flame(ic, cx, base, h, w, ramp='fire', inner='yel'):
    top = base - h
    pts = [(cx, top), (cx + w * .45, top + h * .35), (cx + w, top + h * .62), (cx + w * .7, base - h * .02), (cx, base + h * .02), (cx - w * .7, base - h * .02), (cx - w, top + h * .66), (cx - w * .5, top + h * .38), (cx - w * .25, top + h * .2)]
    ic.poly(pts, ramp)
    if inner:
        h2, w2 = h * .55, w * .5
        t2 = base - h2
        ic.poly([(cx, t2), (cx + w2, t2 + h2 * .6), (cx + w2 * .6, base - .4), (cx - w2 * .6, base - .4), (cx - w2, t2 + h2 * .6)], inner, edge=False)


def drop(ic, cx, cy, s, ramp='red'):
    ic.poly([(cx, cy - s * 1.5), (cx + s * .85, cy + s * .1), (cx - s * .85, cy + s * .1)], ramp)
    ic.circ(cx, cy + s * .35, s * .95, ramp)
    ic.px(cx - s * .45, cy + s * .1, RP[ramp][4])


def star5(ic, cx, cy, Ro, ri, ramp='gold', rot=-90):
    pts = []
    for k in range(10):
        a = math.radians(rot + k * 36)
        r = Ro if k % 2 == 0 else ri
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    ic.poly(pts, ramp)


def heart(ic, cx, cy, s, ramp='red'):
    ic.circ(cx - s * .5, cy - s * .35, s * .55, ramp)
    ic.circ(cx + s * .5, cy - s * .35, s * .55, ramp)
    ic.poly([(cx - s * 1.05, cy - s * .15), (cx + s * 1.05, cy - s * .15), (cx, cy + s * 1.0)], ramp)


def bolt(ic, cx=8, cy=8, s=1.0, ramp='yel'):
    pts = [(cx + 2 * s, cy - 7 * s), (cx - 3.5 * s, cy + .8 * s), (cx - .3 * s, cy + .8 * s), (cx - 2 * s, cy + 7 * s), (cx + 4 * s, cy - 1.8 * s), (cx + .8 * s, cy - 1.8 * s)]
    ic.poly(pts, ramp)


def snowflake(ic, cx, cy, r, ramp='ice', w=1.0):
    for k in range(3):
        a = math.radians(k * 60 + 90)
        p0 = (cx + r * math.cos(a), cy + r * math.sin(a))
        p1 = (cx - r * math.cos(a), cy - r * math.sin(a))
        ic.line(p0, p1, w, ramp, edge=False)
    for k in range(6):
        a = math.radians(k * 60 + 90)
        bx, by = cx + r * .62 * math.cos(a), cy + r * .62 * math.sin(a)
        for sg in (-1, 1):
            b = a + sg * math.radians(55)
            ic.line((bx, by), (bx + r * .3 * math.cos(b), by + r * .3 * math.sin(b)), 0.9, ramp, edge=False)


def wings(ic, cx, cy, s, ramp='white', mirror=True):
    for sg in (-1, 1):
        pts = [(cx + sg * 1.2 * s, cy + 1.2 * s), (cx + sg * 3 * s, cy - 3.2 * s), (cx + sg * 6.2 * s, cy - 4.8 * s), (cx + sg * 5.8 * s, cy - 2 * s), (cx + sg * 6.4 * s, cy), (cx + sg * 4.6 * s, cy + .5 * s), (cx + sg * 4.4 * s, cy + 2.6 * s), (cx + sg * 2.6 * s, cy + 2 * s)]
        ic.poly(pts, ramp)


def skull(ic, cx=8, cy=7.5, s=1.0, ramp='bone', eyes='dark'):
    ic.ell(cx, cy - .5 * s, 5.2 * s, 4.6 * s, ramp)
    ic.rect(cx - 2.8 * s, cy + 2.5 * s, cx + 2.8 * s, cy + 5.6 * s, ramp)
    ic.ell(cx - 2.1 * s, cy - .4 * s, 1.5 * s, 1.7 * s, eyes, edge=False)
    ic.ell(cx + 2.1 * s, cy - .4 * s, 1.5 * s, 1.7 * s, eyes, edge=False)
    ic.px(cx - .5, cy + 1.6 * s, RP[eyes][0])
    ic.px(cx, cy + 1.6 * s, RP[eyes][0])
    for k in (-1.4, 0, 1.4):
        ic.px(cx + k * s - .5 + .5, cy + 4.5 * s, RP[ramp][1])


def shield_shape(cx, top, w, h):
    return [(cx - w, top), (cx + w, top), (cx + w, top + h * .5), (cx + w * .6, top + h * .8), (cx, top + h), (cx - w * .6, top + h * .8), (cx - w, top + h * .5)]


def sword_diag(ic, x0, y0, x1, y1, w=2.4, blade='steel', guard='gold', grip='wood'):
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    ic.line((x0, y0), (x1 - ux * 1.2, y1 - uy * 1.2), w, blade)
    ic.poly([(x1 - ux * 2, y1 - uy * 2 + 0) if False else (x1 - ux * 2 + px * w / 2, y1 - uy * 2 + py * w / 2), (x1 + ux * 1.4, y1 + uy * 1.4), (x1 - ux * 2 - px * w / 2, y1 - uy * 2 - py * w / 2)], blade, edge=False)


def sword(ic, x0, y0, x1, y1, w=2.2, blade='steel', guard='gold', grip='wood', glen=2.6):
    """Espada de pomo (x0,y0) a punta (x1,y1)."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    gx, gy = x0 + ux * 3.2, y0 + uy * 3.2
    ic.line((gx, gy), (x1 - ux * 1.5, y1 - uy * 1.5), w, blade)
    tx, ty = x1 - ux * 2.2, y1 - uy * 2.2
    ic.poly([(tx + px * w / 2, ty + py * w / 2), (x1, y1), (tx - px * w / 2, ty - py * w / 2)], blade, edge=False)
    ic.line((x0 + ux * .5, y0 + uy * .5), (gx, gy), 1.7, grip)
    ic.line((gx - px * glen, gy - py * glen), (gx + px * glen, gy + py * glen), 1.7, guard)
    ic.circ(x0, y0, 1.2, guard, edge=False)


def hammer(ic, cx, cy, ramp='stone'):
    ic.line((4, 13), (10, 6), 2.0, 'wood')
    ic.rect(8, 2.5, 14, 8, ramp)
    ic.rect(8, 2.5, 14, 4, ramp, edge=False)


def gear(ic, cx, cy, ramp='steel'):
    d = np.hypot(XX - cx, YY - cy)
    a = np.arctan2(YY - cy, XX - cx)
    teeth = (np.cos(a * 8) > 0.25) & (d <= 7.0)
    m = ((d <= 5.4) | teeth) & (d > 2.1)
    ic.L(m, ramp)


# ---------- definiciones ----------
I = {}


def reg(name):
    def deco(f):
        I[name] = f
        return f
    return deco


@reg('attack')
def _(ic):
    sword(ic, 3, 13, 13.5, 2.5, 2.4)


@reg('jump')
def _(ic):
    ic.poly([(8, 1.5), (13.6, 8.2), (10.2, 8.2), (10.2, 13), (5.8, 13), (5.8, 8.2), (2.4, 8.2)], 'white')
    ic.px(7, 4, RP['white'][4]); ic.px(6, 5, RP['white'][4])


@reg('roll')
def _(ic):
    ic.arc(8, 8, 3.6, 6.2, 60, 330, 'white')
    ic.poly([(8.5, 2.2), (13, 4.4), (8.8, 7.2)], 'white')


@reg('pause')
def _(ic):
    ic.rect(3.5, 3, 7, 13, 'white'); ic.rect(9, 3, 12.5, 13, 'white')


@reg('play')
def _(ic):
    ic.poly([(4, 2.5), (13.5, 8), (4, 13.5)], 'white')


@reg('settings')
def _(ic):
    gear(ic, 8, 8, 'steel')


def speaker(ic, ramp='steel'):
    ic.poly([(2, 6), (5, 6), (8.5, 2.8), (8.5, 13.2), (5, 10), (2, 10)], ramp)


@reg('sound_on')
def _(ic):
    speaker(ic)
    ic.arc(8.5, 8, 2.6, 4.0, -50, 50, 'white', edge=False)
    ic.arc(8.5, 8, 5.2, 6.6, -55, 55, 'white', edge=False)


@reg('sound_off')
def _(ic):
    speaker(ic, 'stone')
    ic.line((10.5, 5.2), (14.2, 10.8), 1.6, 'red'); ic.line((14.2, 5.2), (10.5, 10.8), 1.6, 'red')


def note(ic, ramp='white'):
    ic.ell(5.2, 11.5, 2.6, 2.0, ramp)
    ic.rect(7, 3, 8.4, 11.5, ramp, edge=False)
    ic.poly([(8.4, 3), (12.8, 5.5), (12.8, 8), (8.4, 6)], ramp)


@reg('music_on')
def _(ic):
    note(ic)


@reg('music_off')
def _(ic):
    note(ic, 'stone'); ic.line((3, 3), (13, 13), 1.6, 'red')


@reg('back')
def _(ic):
    ic.poly([(2, 7), (7.5, 2.2), (7.5, 5.2), (13, 5.2), (13, 12.5), (10.5, 12.5), (10.5, 8.4), (7.5, 8.4), (7.5, 11.8)], 'white')


@reg('close')
def _(ic):
    ic.line((3.5, 3.5), (12.5, 12.5), 2.4, 'red'); ic.line((12.5, 3.5), (3.5, 12.5), 2.4, 'red')


@reg('lock')
def _(ic):
    ic.arc(8, 6.5, 2.6, 4.6, 180, 360, 'steel')
    ic.rect(4.6, 5.5, 6.6, 7.5, 'steel', edge=False); ic.rect(9.4, 5.5, 11.4, 7.5, 'steel', edge=False)
    ic.rect(3, 7.5, 13, 14, 'gold')
    ic.rect(7.2, 9.4, 8.8, 12, 'dark', edge=False)


@reg('star')
def _(ic):
    star5(ic, 8, 8.4, 7, 3.1)


@reg('coin')
def _(ic):
    ic.circ(8, 8, 6, 'gold')
    ic.ring(8, 8, 3.4, 4.4, 'gold', edge=False)
    ic.rect(7.2, 5.4, 8.8, 10.6, 'gold', edge=False)
    ic.px(5, 4.6, RP['gold'][4]); ic.px(6, 4, RP['gold'][4])


@reg('soul')
def _(ic):
    ic.poly([(8, 1.5), (11.4, 6), (12.6, 10.2), (10.6, 13.6), (8, 12.2), (5.4, 13.6), (3.4, 10.2), (4.6, 6)], 'cyan')
    ic.poly([(8, 5), (9.8, 8.2), (8, 11), (6.2, 8.2)], 'white', edge=False)
    ic.px(6, 7, RP['dark'][0]); ic.px(10, 7, RP['dark'][0])


@reg('heart')
def _(ic):
    heart(ic, 8, 7.4, 4.6)
    ic.px(4, 5, RP['red'][4]); ic.px(5, 4, RP['red'][4])


@reg('potion')
def _(ic):
    ic.rect(6.2, 1.6, 9.8, 4.2, 'wood')
    ic.rect(6.6, 3.6, 9.4, 6.2, 'white', edge=False)
    ic.poly([(6.6, 5.8), (9.4, 5.8), (13.4, 11), (12.2, 14.2), (3.8, 14.2), (2.6, 11)], 'white')
    ic.poly([(4.2, 9.4), (11.8, 9.4), (13, 11.4), (12, 13.6), (4, 13.6), (3, 11.4)], 'red', edge=False)
    ic.px(5, 11, RP['red'][4]); ic.px(6, 10, RP['red'][4])


@reg('key')
def _(ic):
    ic.ring(5, 5, 1.7, 3.8, 'gold')
    ic.line((7.2, 7.2), (13, 13), 2.0, 'gold')
    ic.rect(10.4, 11.6, 12.4, 14.4, 'gold', edge=False); ic.rect(12.4, 10.2, 14.2, 12.2, 'gold', edge=False)


@reg('skull')
def _(ic):
    skull(ic)


@reg('relic')
def _(ic):
    ic.ring(8, 3.8, 1.2, 2.8, 'gold')
    ic.poly([(8, 5.4), (13, 8.8), (8, 15), (3, 8.8)], 'cyan')
    ic.poly([(8, 5.4), (13, 8.8), (8, 9.6), (3, 8.8)], 'cyan', edge=False, bias=0.25)
    ic.px(6, 8, RP['cyan'][4]); ic.px(5, 8, RP['cyan'][4])


@reg('door')
def _(ic):
    ic.poly([(3, 14.5), (3, 6), (4.2, 3.6), (6.4, 2.2), (9.6, 2.2), (11.8, 3.6), (13, 6), (13, 14.5)], 'wood')
    ic.rect(4.6, 7, 11.4, 14.5, 'wood', edge=False, bias=-0.1)
    ic.line((8, 3), (8, 14.5), 0.9, 'dark', edge=False)
    ic.rect(3, 9, 13, 10.2, 'steel', edge=False)
    ic.px(10, 11, RP['gold'][3]); ic.px(10, 12, RP['gold'][2])


@reg('altar')
def _(ic):
    ic.rect(3.5, 11, 12.5, 14.5, 'stone')
    ic.rect(5.2, 7.5, 10.8, 11.2, 'stone')
    ic.rect(4, 6.3, 12, 8, 'stone')
    ic.circ(8, 3.8, 2.4, 'cyan'); ic.px(7, 3, RP['cyan'][4]); ic.px(8, 2.5, RP['cyan'][4])


@reg('forge')
def _(ic):
    ic.poly([(2, 5), (12.5, 5), (14.6, 7.2), (10.8, 8.2), (10, 10.4), (11.6, 12.2), (11.6, 14), (4.4, 14), (4.4, 12.2), (6, 10.4), (6, 8.2), (2, 7.6)], 'steel')
    ic.px(5, 6, RP['steel'][4]); ic.px(6, 6, RP['steel'][4]); ic.px(7, 6, RP['steel'][4])
    ic.px(4, 2, RP['fire'][3]); ic.px(7, 1.5, RP['fire'][4]); ic.px(9, 3, RP['fire'][2])


@reg('shop')
def _(ic):
    ic.poly([(5.4, 3), (10.6, 3), (9.4, 5.6), (13.6, 10), (12.4, 14.4), (3.6, 14.4), (2.4, 10), (6.6, 5.6)], 'wood')
    ic.rect(5.4, 3, 10.6, 4.4, 'wood', edge=False, bias=.2)
    ic.circ(8, 10, 2.5, 'gold', edge=False); ic.px(7, 9, RP['gold'][4])


@reg('fountain')
def _(ic):
    ic.poly([(2, 9), (14, 9), (12.4, 14), (3.6, 14)], 'stone')
    ic.rect(7, 6, 9, 9.6, 'stone', edge=False)
    ic.line((8, 6), (8, 2.4), 1.4, 'cyan', edge=False)
    ic.line((8, 3), (4.6, 6.6), 1.2, 'cyan', edge=False); ic.line((8, 3), (11.4, 6.6), 1.2, 'cyan', edge=False)
    ic.rect(3.4, 9.2, 12.6, 10.6, 'cyan', edge=False)


@reg('chest')
def _(ic):
    ic.poly([(2, 7), (3, 3.6), (13, 3.6), (14, 7)], 'wood')
    ic.rect(2, 7, 14, 14, 'wood')
    ic.rect(2, 7, 14, 8.2, 'gold', edge=False); ic.rect(7, 6.2, 9, 10.4, 'gold', edge=False)
    ic.rect(2, 3.8, 3.4, 14, 'gold', edge=False); ic.rect(12.6, 3.8, 14, 14, 'gold', edge=False)
    ic.px(7.5, 8.5, RP['dark'][1])


@reg('elite')
def _(ic):
    ic.poly([(2, 7), (3.8, 2.4), (5.6, 5), (5.6, 8)], 'bone')
    ic.poly([(14, 7), (12.2, 2.4), (10.4, 5), (10.4, 8)], 'bone')
    skull(ic, 8, 8.6, 0.88, 'red', 'dark')


@reg('boss')
def _(ic):
    ic.poly([(1.4, 9), (1.6, 3), (4, 6), (5.4, 8)], 'bone')
    ic.poly([(14.6, 9), (14.4, 3), (12, 6), (10.6, 8)], 'bone')
    skull(ic, 8, 8.6, 0.9, 'purple', 'yel')
    ic.px(5.5, 8, RP['yel'][4]); ic.px(10.5, 8, RP['yel'][4])


@reg('treasure')
def _(ic):
    ic.circ(5.5, 10.5, 3.6, 'gold')
    ic.rect(4.8, 8.4, 6.2, 12.6, 'gold', edge=False)
    ic.poly([(10, 3.2), (14, 6.6), (10, 13.4), (6.4, 6.6)], 'cyan')
    ic.poly([(10, 3.2), (14, 6.6), (10, 7.4), (6.4, 6.6)], 'cyan', edge=False, bias=.25)
    ic.px(9, 5, RP['cyan'][4])


@reg('secret')
def _(ic):
    ic.circ(8, 8, 6.5, 'dark')
    ic.bmp(['.222.', '22.22', '...22', '..22.', '..2..', '.....', '..2..'], {'2': ('gold', 3)}, 5.5 if False else 5, 4)
    ic.px(5, 4, RP['gold'][4])


@reg('map')
def _(ic):
    ic.poly([(2, 3.4), (6, 2.4), (10, 3.8), (14, 2.6), (14, 12.6), (10, 13.8), (6, 12.4), (2, 13.6)], 'bone')
    ic.line((6, 2.6), (6, 12.6), 0.8, 'bone', edge=False, bias=-.4); ic.line((10, 3.8), (10, 13.8), 0.8, 'bone', edge=False, bias=-.4)
    ic.line((4, 10), (7.5, 7), 1.0, 'red', edge=False); ic.line((7.5, 7), (11, 9.6), 1.0, 'red', edge=False)
    ic.line((10, 4.8), (12.6, 7.4), 1.1, 'red', edge=False); ic.line((12.6, 4.8), (10, 7.4), 1.1, 'red', edge=False)


@reg('burn')
def _(ic):
    flame(ic, 8, 14, 12, 4.6)


@reg('freeze')
def _(ic):
    snowflake(ic, 8, 8, 6.2, 'ice', 1.3)
    ic.circ(8, 8, 1.4, 'white', edge=False)


@reg('poison')
def _(ic):
    drop(ic, 8, 9, 4.4, 'green')
    ic.circ(6.4, 10.6, .9, 'green', edge=False, bias=.6)
    ic.circ(10, 9, .7, 'dark', edge=False)


@reg('bleed')
def _(ic):
    drop(ic, 8, 8.8, 4.6, 'red')


@reg('shock')
def _(ic):
    bolt(ic, 8, 8, 1.0, 'yel')


@reg('curse')
def _(ic):
    ic.poly([(1.5, 8), (4.6, 4.4), (8, 3.4), (11.4, 4.4), (14.5, 8), (11.4, 11.6), (8, 12.6), (4.6, 11.6)], 'purple')
    ic.circ(8, 8, 2.8, 'yel', edge=False)
    ic.rect(7.4, 5.8, 8.6, 10.2, 'dark', edge=False)


@reg('shield')
def _(ic):
    ic.poly(shield_shape(8, 1.8, 5.8, 12.4), 'steel')
    ic.rect(7, 3.4, 9, 12, 'gold', edge=False); ic.rect(4, 6, 12, 7.8, 'gold', edge=False)


@reg('crown')
def _(ic):
    ic.poly([(2, 12.6), (2.4, 4.4), (5.4, 8), (8, 3), (10.6, 8), (13.6, 4.4), (14, 12.6)], 'gold')
    ic.rect(2, 11, 14, 13.4, 'gold', edge=False, bias=-.2)
    ic.px(8, 10, RP['red'][3]); ic.px(5, 11, RP['cyan'][3]); ic.px(11, 11, RP['cyan'][3])
    ic.px(8, 4.4, RP['gold'][4])


# ---------- bendiciones ----------
@reg('b_filo')
def _(ic):
    sword(ic, 3.4, 13.4, 12.6, 3.4, 2.4)
    ic.px(13, 2, RP['white'][4]); ic.px(14, 1, RP['white'][4]); ic.px(12, 1, RP['white'][3]); ic.px(14, 3, RP['white'][3])


@reg('b_corazon')
def _(ic):
    heart(ic, 8, 8, 4.8)
    ic.rect(7.2, 5.6, 8.8, 10.4, 'white', edge=False); ic.rect(5.6, 7.2, 10.4, 8.8, 'white', edge=False)


@reg('b_alas')
def _(ic):
    wings(ic, 8, 8, 1.1, 'white')
    ic.circ(8, 8.5, 1.6, 'gold', edge=False)


@reg('b_furia')
def _(ic):
    for k, x in enumerate((3.4, 7, 10.6)):
        ic.poly([(x, 2), (x + 2.4, 2.4), (x + 2.8, 14), (x + .8, 11), (x - .8, 6)], 'red')


@reg('b_sangre')
def _(ic):
    drop(ic, 8, 8.6, 5.2, 'red')
    ic.rect(7.2, 9, 8.8, 13, 'bone', edge=False) if False else None
    ic.px(10, 10, RP['red'][1])


@reg('b_brasas')
def _(ic):
    ic.ell(8, 11.5, 6, 3, 'stone')
    ic.circ(5.2, 10.4, 2.0, 'lava', edge=False); ic.circ(9.6, 10, 2.4, 'lava', edge=False); ic.circ(7.6, 12.4, 1.6, 'lava', edge=False)
    flame(ic, 8, 8.6, 7, 2.6, 'fire', 'yel')
    ic.px(4, 4, RP['fire'][4]); ic.px(12, 3, RP['fire'][3])


@reg('b_glacial')
def _(ic):
    ic.poly([(8, 1.4), (11.6, 6), (10.4, 14.4), (5.6, 14.4), (4.4, 6)], 'ice')
    ic.poly([(8, 1.4), (11.6, 6), (8, 14.4)], 'ice', edge=False, bias=-.25)
    ic.px(6, 6, RP['ice'][4]); ic.px(6, 8, RP['ice'][4])


@reg('b_chispa')
def _(ic):
    bolt(ic, 8, 8, .95, 'yel')
    ic.px(2, 3, RP['yel'][4]); ic.px(13, 12, RP['yel'][4]); ic.px(13, 3, RP['ice'][4]); ic.px(3, 12, RP['ice'][4])


@reg('b_espinas')
def _(ic):
    for k in range(8):
        a = math.radians(k * 45 + 22)
        x, y = 8 + 4.2 * math.cos(a), 8 + 4.2 * math.sin(a)
        ic.poly([(x + 1.5 * math.cos(a + 1.57), y + 1.5 * math.sin(a + 1.57)), (x + 6.4 * math.cos(a), y + 6.4 * math.sin(a)), (x - 1.5 * math.cos(a + 1.57), y - 1.5 * math.sin(a + 1.57))], 'bone', edge=False)
    ic.ring(8, 8, 2.6, 5.0, 'green')


@reg('b_piedra')
def _(ic):
    ic.poly([(2, 10), (3.4, 5), (7, 2.6), (11.4, 3.4), (14, 8), (13, 12.6), (8, 14), (3.4, 13)], 'stone')
    ic.poly([(3.4, 5), (7, 2.6), (11.4, 3.4), (8, 7)], 'stone', edge=False, bias=.3)
    ic.line((8, 7), (8.6, 12), 0.8, 'stone', edge=False, bias=-.5)


@reg('b_fantasma')
def _(ic):
    ic.poly([(3, 14), (3, 7), (5, 3.2), (8, 2), (11, 3.2), (13, 7), (13, 14), (11.4, 12.2), (9.8, 14), (8, 12.2), (6.2, 14), (4.6, 12.2)], 'white')
    ic.ell(6, 7.6, 1.2, 1.6, 'dark', edge=False); ic.ell(10, 7.6, 1.2, 1.6, 'dark', edge=False)
    ic.ell(8, 10.6, 1.0, 1.0, 'dark', edge=False)


@reg('b_doble_salto')
def _(ic):
    for dy, r in ((0, 'white'), (5.6, 'cyan')):
        ic.poly([(8, 1.8 + dy), (13.4, 7 + dy), (11, 8.2 + dy), (8, 5.4 + dy), (5, 8.2 + dy), (2.6, 7 + dy)], r)


@reg('b_critico')
def _(ic):
    star5(ic, 8, 8, 7.2, 2.6, 'red', -90)
    ic.circ(8, 8, 2.0, 'yel', edge=False)
    ic.px(7.5, 7.5, RP['yel'][4])


@reg('b_alma')
def _(ic):
    ic.ring(8, 8.6, 4.4, 6, 'cyan', edge=False)
    ic.poly([(8, 2.4), (10.6, 6.6), (9.4, 11), (8, 10), (6.6, 11), (5.4, 6.6)], 'white')
    ic.px(7, 6, RP['dark'][0]); ic.px(9, 6, RP['dark'][0])


@reg('b_fortuna')
def _(ic):
    for (x, y) in ((5.6, 5.6), (10.4, 5.6), (5.6, 10.4), (10.4, 10.4)):
        ic.circ(x, y, 2.8, 'green')
    ic.line((8, 8), (11.8, 14), 1.6, 'wood', edge=False)
    ic.circ(8, 8, 1.6, 'green', edge=False, bias=.3)


@reg('b_escudo_estelar')
def _(ic):
    ic.poly(shield_shape(8, 1.8, 5.8, 12.6), 'blue')
    star5(ic, 8, 7.2, 3.6, 1.5, 'yel')


@reg('b_enfriamiento')
def _(ic):
    ic.circ(8, 8, 6.2, 'ice')
    ic.circ(8, 8, 4.6, 'white', edge=False, bias=.2)
    ic.line((8, 8), (8, 4.2), 1.2, 'blue', edge=False); ic.line((8, 8), (11, 9.6), 1.2, 'blue', edge=False)


@reg('b_habilidad')
def _(ic):
    ic.poly([(2.6, 3), (8, 4.4), (13.4, 3), (13.4, 13.4), (8, 14.4), (2.6, 13.4)], 'purple')
    ic.line((8, 4.4), (8, 14.2), 0.9, 'dark', edge=False)
    star5(ic, 5.4, 8.6, 2.4, 1.0, 'yel'); star5(ic, 10.6, 8.6, 2.0, .9, 'yel')


@reg('b_ejecutor')
def _(ic):
    ic.line((4, 14), (11, 4), 1.8, 'wood')
    ic.poly([(9, 2.4), (14, 3.6), (13.2, 9), (10.4, 7.4), (10.8, 5.6)], 'steel')
    ic.px(12, 4, RP['steel'][4]); ic.px(13, 4, RP['steel'][4])


@reg('b_iman')
def _(ic):
    ic.arc(8, 8.6, 3.2, 6.4, 180, 360, 'steel') if False else None
    ic.arc(8, 8, 3.0, 6.2, 180, 360, 'red')
    ic.rect(1.8, 7.6, 5, 12.4, 'red'); ic.rect(11, 7.6, 14.2, 12.4, 'red')
    ic.rect(1.8, 10.2, 5, 12.4, 'white', edge=False); ic.rect(11, 10.2, 14.2, 12.4, 'white', edge=False)


@reg('b_venganza')
def _(ic):
    ic.poly([(8, 14.4), (5.8, 8), (6.4, 2), (9.6, 2), (10.2, 8)], 'steel')
    ic.rect(4, 7, 12, 8.6, 'gold', edge=False)
    drop(ic, 8, 11, 2.0, 'red')


@reg('b_segunda')
def _(ic):
    ic.ring(8, 4.2, 1.4, 3.2, 'gold')
    ic.rect(7, 6.8, 9, 14.4, 'gold'); ic.rect(3.4, 8.4, 12.6, 10.2, 'gold')


@reg('b_onda')
def _(ic):
    ic.circ(8, 8, 1.8, 'ice', edge=False)
    ic.arc(8, 8, 3.6, 4.8, 150, 210, 'ice', edge=False); ic.arc(8, 8, 3.6, 4.8, -30, 30, 'ice', edge=False)
    ic.arc(8, 8, 6.2, 7.6, 140, 220, 'white', edge=False); ic.arc(8, 8, 6.2, 7.6, -40, 40, 'white', edge=False)


@reg('b_egida')
def _(ic):
    ic.circ(8, 8, 6.4, 'gold')
    ic.circ(8, 8, 4.4, 'steel', edge=False)
    ic.circ(8, 8, 1.8, 'gold', edge=False)
    for k in range(4):
        a = math.radians(k * 90 + 45)
        ic.px(8 + 3.2 * math.cos(a) - .0, 8 + 3.2 * math.sin(a), RP['gold'][3])


@reg('b_sabio')
def _(ic):
    ic.poly([(3, 3), (5.4, 5), (10.6, 5), (13, 3), (13.6, 10), (11, 14), (5, 14), (2.4, 10)], 'wood')
    ic.circ(5.8, 8, 2.4, 'bone', edge=False); ic.circ(10.2, 8, 2.4, 'bone', edge=False)
    ic.circ(5.8, 8, 1.1, 'dark', edge=False); ic.circ(10.2, 8, 1.1, 'dark', edge=False)
    ic.poly([(7.2, 9.6), (8.8, 9.6), (8, 11.6)], 'gold', edge=False)


@reg('b_gigante')
def _(ic):
    ic.rect(3.4, 6, 12.6, 14, 'gold')
    for k, x in enumerate((3.4, 6.2, 9, 11.2)):
        ic.rect(x, 3.2 + (k % 2) * .8, x + 2.2, 7, 'gold')
    ic.rect(2, 8, 4.4, 11.4, 'gold')
    ic.px(5, 5, RP['gold'][4])


@reg('b_sombra')
def _(ic):
    ic.poly([(8, 1.6), (12, 5), (13.4, 14), (8, 12), (2.6, 14), (4, 5)], 'dark')
    ic.ell(8, 7.4, 3.2, 3.4, 'purple', edge=False, bias=-.5)
    ic.px(6, 7, RP['yel'][3]); ic.px(10, 7, RP['yel'][3]); ic.px(6, 6.6, RP['yel'][4]); ic.px(10, 6.6, RP['yel'][4])


@reg('b_eclipse')
def _(ic):
    ic.ring(8, 8, 5.2, 7.2, 'gold', edge=False)
    ic.circ(8, 8, 5.4, 'dark')
    ic.px(3, 5, RP['gold'][4]); ic.px(4, 4, RP['gold'][4]); ic.px(13, 11, RP['gold'][3])


# ---------- habilidades ----------
@reg('s_paladin_1')
def _(ic):
    ic.line((3, 13), (12, 4), 2.0, 'gold')
    ic.poly([(10.4, 2.4), (14, 1.8), (13.4, 5.6)], 'white')
    ic.line((2.6, 13.4), (5.4, 10.6), 2.6, 'wood', edge=False)
    ic.px(5, 3, RP['white'][4]); ic.px(13, 9, RP['white'][4]); ic.px(2, 8, RP['yel'][3])


@reg('s_paladin_2')
def _(ic):
    wings(ic, 8, 8.4, 1.1, 'white')
    ic.poly(shield_shape(8, 5, 2.8, 7.6), 'gold')


@reg('s_paladin_3')
def _(ic):
    ic.rect(6, 1.4, 10, 8, 'yel', edge=False, bias=-.3)
    sword(ic, 8, 1.6, 8, 14.2, 2.2, glen=3.2) if False else None
    ic.line((8, 3), (8, 12), 2.4, 'steel')
    ic.poly([(6.8, 11), (9.2, 11), (8, 14.6)], 'steel', edge=False)
    ic.rect(4.6, 4.2, 11.4, 5.8, 'gold', edge=False)
    ic.px(3, 2, RP['yel'][4]); ic.px(13, 2, RP['yel'][4]); ic.px(2, 7, RP['yel'][3]); ic.px(14, 7, RP['yel'][3])


@reg('s_paladin_4')
def _(ic):
    for k in range(7):
        a = math.radians(180 + k * 30)
        ic.line((8 + 4.4 * math.cos(a), 11 + 4.4 * math.sin(a)), (8 + 7 * math.cos(a), 11 + 7 * math.sin(a)), 1.2, 'yel', edge=False)
    ic.L(((XX - 8) ** 2 + (YY - 11.2) ** 2 <= 17) & (YY <= 11.6), 'gold')
    ic.rect(1.6, 11.6, 14.4, 13.6, 'wood')


@reg('s_shadow_1')
def _(ic):
    ic.poly([(3, 8), (8, 3), (8, 6), (13, 6), (13, 10), (8, 10), (8, 13)], 'purple')
    for y in (4.6, 8, 11.4):
        ic.px(1, y, RP['purple'][3]); ic.px(2, y, RP['purple'][2])


@reg('s_shadow_2')
def _(ic):
    ic.poly([(12.6, 2), (14, 5), (10.6, 11), (5, 13.4), (7, 9.6), (9.6, 5)], 'white')
    ic.line((3.6, 14), (6.2, 11.2), 2.0, 'purple', edge=False)
    ic.px(12, 4, RP['purple'][4])


@reg('s_shadow_3')
def _(ic):
    for sg in (1, -1):
        ic.poly([(8 + sg * 6.4, 2.4), (8 + sg * 7.2, 4), (8 + sg * 1.6, 12.2), (8 + sg * .2, 10.4)], 'steel')
        ic.line((8 - sg * 1, 13), (8 + sg * 1.6, 10.8), 1.8, 'purple', edge=False)
    ic.circ(8, 8, 1.2, 'yel', edge=False)


@reg('s_shadow_4')
def _(ic):
    ic.ell(8, 8, 3.2, 6.6, 'purple')
    ic.ell(8, 8, 1.6, 5, 'dark', edge=False)
    ic.line((13.6, 2.4), (2.6, 13.6), 1.8, 'white')
    ic.px(8, 8, RP['yel'][4])


@reg('s_flame_1')
def _(ic):
    ic.circ(10, 6.4, 4.4, 'fire')
    ic.circ(10, 6.4, 2.4, 'yel', edge=False)
    ic.poly([(7, 4), (1.6, 13.4), (8, 9.6)], 'fire', edge=False)
    ic.poly([(8, 5.4), (4, 11.4), (8.6, 9)], 'orange', edge=False, bias=.3)


@reg('s_flame_2')
def _(ic):
    flame(ic, 3.6, 14, 8, 2.6); flame(ic, 8, 14, 12, 3.2); flame(ic, 12.4, 14, 8.6, 2.6)
    ic.rect(1.6, 13.4, 14.4, 15, 'stone', edge=False)


@reg('s_flame_3')
def _(ic):
    for k, (y, w) in enumerate(((2.6, 6.4), (5.8, 5.2), (9, 3.8), (12.2, 2.2))):
        ic.ell(8 + (k % 2) * 1 - .5, y + 1, w, 1.6, 'fire' if k % 2 == 0 else 'orange')
    ic.px(12, 2, RP['yel'][4]); ic.px(3, 12.4, RP['yel'][3])


@reg('s_flame_4')
def _(ic):
    ic.poly([(2, 5), (6, 2.6), (11, 3), (14, 6.4), (14.6, 9), (10, 8.6), (8, 10.6), (4, 9.6), (2, 7.6)], 'red')
    ic.poly([(5, 2.8), (3.8, .8), (7, 2)], 'bone', edge=False)
    ic.px(5, 5, RP['yel'][4]); ic.px(6, 5, RP['yel'][3])
    flame(ic, 9, 14.4, 6, 3.6, 'fire', 'yel')


@reg('s_storm_1')
def _(ic):
    bolt(ic, 9, 8, .9, 'yel')
    for y in (4, 8, 12):
        ic.px(1, y, RP['ice'][3]); ic.px(2, y, RP['ice'][4]); ic.px(3, y, RP['ice'][3])


@reg('s_storm_2')
def _(ic):
    ic.line((2.6, 13.4), (13.4, 3.2), 1.5, 'steel')
    ic.line((2, 14), (5, 11), 2.0, 'ice', edge=False)
    ic.px(10, 2, RP['yel'][4]); ic.px(13, 7, RP['yel'][4]); ic.px(6, 5, RP['yel'][3]); ic.px(11, 10, RP['yel'][3]); ic.px(4, 9, RP['yel'][4])
    bolt(ic, 11, 10, .4, 'yel')


@reg('s_storm_3')
def _(ic):
    ic.poly([(2.4, 8), (2.2, 5.6), (4.6, 4), (6.2, 2.4), (9.6, 2.4), (11.2, 4.2), (13.4, 5), (14, 7.6), (13, 9), (3.6, 9)], 'stone')
    bolt(ic, 8.4, 11.6, .55, 'yel')


@reg('s_storm_4')
def _(ic):
    ic.poly([(2, 6), (3, 3), (6, 1.8), (10, 1.8), (13, 3.4), (14, 6), (13, 6.8), (3, 6.8)], 'dark')
    bolt(ic, 8.6, 9.2, .95, 'yel')
    ic.px(3, 12, RP['ice'][4]); ic.px(13, 11, RP['ice'][4])


@reg('s_frost_1')
def _(ic):
    for ang, L in ((-35, 11), (0, 13), (35, 11)):
        a = math.radians(ang)
        cx, cy = 3 + .0, 8
        tx, ty = cx + L * math.cos(a), cy + L * math.sin(a) * .9 + 0
        ic.poly([(cx, cy), (cx + L * .45 * math.cos(a) - 1.6 * math.sin(a), cy + L * .45 * math.sin(a) + 1.6 * math.cos(a)), (tx, ty), (cx + L * .45 * math.cos(a) + 1.6 * math.sin(a), cy + L * .45 * math.sin(a) - 1.6 * math.cos(a))], 'ice')


@reg('s_frost_2')
def _(ic):
    ic.poly([(2.6, 5), (8, 2.4), (13.4, 5), (13.4, 12), (8, 14.6), (2.6, 12)], 'ice')
    ic.poly([(2.6, 5), (8, 7.6), (13.4, 5), (8, 2.4)], 'white', edge=False, bias=.2)
    ic.line((8, 7.6), (8, 14.4), 0.8, 'ice', edge=False, bias=-.5)
    ic.px(4, 9, RP['white'][4]); ic.px(4, 10, RP['white'][3])


@reg('s_frost_3')
def _(ic):
    snowflake(ic, 8, 8, 5.6, 'white', 1.1)
    ic.arc(8, 8, 6.4, 7.6, 200, 300, 'ice', edge=False)
    ic.arc(8, 8, 6.4, 7.6, 20, 120, 'ice', edge=False)


@reg('s_frost_4')
def _(ic):
    ic.ring(8, 8, 5.8, 7.2, 'ice', edge=False)
    ic.poly([(8, 1.6), (10.2, 6), (14.4, 8), (10.2, 10), (8, 14.4), (5.8, 10), (1.6, 8), (5.8, 6)], 'white')
    ic.circ(8, 8, 1.4, 'ice', edge=False)


@reg('s_verdant_1')
def _(ic):
    ic.lines([(2.4, 13), (5, 8), (8.4, 9.4), (10, 4.6), (13.4, 3.4)], 2.0, 'green')
    for (x, y, dx, dy) in ((4.6, 8.6, -1.6, -2), (9.6, 7.6, 2.2, 1.8), (6.6, 9.8, 0, 2.6)):
        ic.poly([(x, y), (x + dx, y + dy), (x + dx * .4 + .8, y + dy * .4 + .8)], 'bone', edge=False)


@reg('s_verdant_2')
def _(ic):
    ic.line((8, 14), (8, 8.6), 1.6, 'green')
    for k in range(5):
        a = math.radians(-90 + (k - 2) * 62)
        ic.ell(8 + 3.2 * math.cos(a), 6.6 + 3.2 * math.sin(a), 2.1, 2.1, 'pink', edge=True)
    ic.circ(8, 6.6, 1.8, 'yel', edge=False)


@reg('s_verdant_3')
def _(ic):
    ic.rect(1.6, 12.6, 14.4, 14.6, 'wood')
    for x, h in ((3.6, 7), (7, 10), (10.6, 8), (13, 5)):
        ic.lines([(x, 13), (x + (1 if x < 8 else -1), 13 - h * .6), (x + (-1 if x < 8 else 1.4), 13 - h)], 1.8, 'wood')
    ic.px(7, 3.6, RP['green'][3]); ic.px(8, 4.6, RP['green'][3])


@reg('s_verdant_4')
def _(ic):
    ic.rect(7, 8, 9.4, 14.4, 'wood')
    ic.poly([(7, 13), (3, 14.6), (7, 12)], 'wood', edge=False); ic.poly([(9.4, 13), (13.4, 14.6), (9.4, 12)], 'wood', edge=False)
    for (x, y, r) in ((8, 4.4, 4.2), (4.4, 7.2, 3.0), (11.8, 7.2, 3.0)):
        ic.circ(x, y, r, 'green')
    ic.px(6, 3, RP['yel'][3]); ic.px(10, 5, RP['yel'][3])


@reg('s_blood_1')
def _(ic):
    ic.arc(10, 8, 6, 8.4, 130, 260, 'red', edge=False)
    ic.poly([(2.4, 10.4), (3.6, 4), (10.8, 2.2), (6, 6), (4.6, 12)], 'red')
    drop(ic, 12, 11.4, 1.7, 'red')
    ic.px(5, 5, RP['red'][4])


@reg('s_blood_2')
def _(ic):
    ic.poly([(3.4, 3.6), (12.6, 3.6), (11.8, 8), (9.2, 10), (6.8, 10), (4.2, 8)], 'steel')
    ic.rect(7, 9.8, 9, 12.4, 'steel', edge=False); ic.rect(4.6, 12.2, 11.4, 14, 'gold')
    ic.rect(4.4, 3.6, 11.6, 5.4, 'red', edge=False)
    drop(ic, 8, 3.4, 1.4, 'red')


@reg('s_blood_3')
def _(ic):
    ic.arc(8, 8, 4.4, 6.4, -20, 250, 'red', edge=False)
    ic.poly([(14, 6), (11.4, 4.4), (11, 8)], 'bone')
    ic.line((8, 8), (3, 13.4), 1.6, 'wood')
    ic.poly([(2.6, 3), (7.2, 2.8), (9, 5)], 'steel', edge=False)
    ic.px(2, 7, RP['red'][4])


@reg('s_blood_4')
def _(ic):
    ic.ring(8, 8, 5.0, 7.4, 'red', edge=False)
    ic.circ(8, 8, 5.4, 'dark')
    ic.px(4, 4, RP['red'][4]); ic.px(5, 3, RP['red'][4]); ic.px(12, 12, RP['red'][3])


@reg('s_earth_1')
def _(ic):
    ic.rect(3.6, 7, 12.4, 14, 'stone')
    for x in (3.6, 6.2, 8.8, 11):
        ic.rect(x, 3.6, x + 2.2, 7.6, 'stone')
    ic.px(5, 5, RP['stone'][4]); ic.px(6, 10, RP['green'][3]); ic.px(10, 12, RP['green'][2])


@reg('s_earth_2')
def _(ic):
    ic.poly(shield_shape(8, 1.8, 6, 12.4), 'stone')
    ic.line((8, 4), (6.6, 8), 0.8, 'stone', edge=False, bias=-.6); ic.line((6.6, 8), (8.4, 11), 0.8, 'stone', edge=False, bias=-.6)
    ic.px(10, 4, RP['green'][3]); ic.px(11, 5, RP['green'][2])


@reg('s_earth_3')
def _(ic):
    ic.rect(1.6, 9.4, 14.4, 14.6, 'wood')
    ic.lines([(8, 3), (6.6, 6), (9.2, 8), (7, 10), (8.4, 13)], 1.3, 'dark', edge=False)
    ic.poly([(2, 9.4), (3.8, 6), (5.6, 9.4)], 'stone'); ic.poly([(10.4, 9.4), (12.4, 5.6), (14, 9.4)], 'stone')


@reg('s_earth_4')
def _(ic):
    ic.line((4, 14), (9, 5), 2.2, 'wood')
    ic.rect(6.4, 1.8, 14.4, 7.8, 'stone')
    ic.rect(6.4, 1.8, 14.4, 3.4, 'stone', edge=False, bias=.3)
    ic.px(12, 5, RP['lava'][3]); ic.px(11, 6, RP['lava'][2]); ic.px(9, 4, RP['lava'][3])
    ic.px(2, 13, RP['stone'][3]); ic.px(14, 12, RP['stone'][3]); ic.px(12, 14, RP['stone'][2])


@reg('s_astral_1')
def _(ic):
    star5(ic, 10.4, 5.6, 4.6, 2.0, 'pink')
    ic.poly([(7, 6.4), (1.4, 13.6), (8.2, 9)], 'purple', edge=False)
    ic.px(3, 8, RP['pink'][4]); ic.px(6, 12, RP['pink'][3])


@reg('s_astral_2')
def _(ic):
    ic.circ(8, 8, 6.6, 'purple', edge=False)
    ic.ring(8, 8, 3.4, 5.6, 'pink', edge=False)
    ic.circ(8, 8, 2.8, 'dark')
    ic.arc(8, 8, 5, 6.6, 20, 140, 'white', edge=False)


@reg('s_astral_3')
def _(ic):
    ic.poly([(2, 12), (10, 4.4), (11, 6.4), (14.4, 3), (13.6, 9), (11.4, 8.4), (4.4, 14)], 'pink')
    star5(ic, 13, 3.4, 2.4, 1.0, 'white')
    ic.px(2, 5, RP['white'][4]); ic.px(6, 2, RP['purple'][4])


@reg('s_astral_4')
def _(ic):
    ic.poly([(8, 0.6), (9.6, 5.4), (15, 4.6), (10.8, 8), (13.4, 14), (8, 10.6), (2.6, 14), (5.2, 8), (1, 4.6), (6.4, 5.4)], 'pink')
    ic.circ(8, 8, 2.6, 'white', edge=False)


@reg('s_steel_1')
def _(ic):
    for ang, ox in ((-26, 0), (0, 0), (26, 0)):
        a = math.radians(ang)
        x0, y0 = 2.6, 8 + 0
        x1, y1 = x0 + 11.6 * math.cos(a), y0 + 11.6 * math.sin(a)
        ic.line((x0, y0), (x1 - 1.4 * math.cos(a), y1 - 1.4 * math.sin(a)), 1.7, 'steel')
        ic.poly([(x1 - 2.4 * math.cos(a) - 1.0 * math.sin(a), y1 - 2.4 * math.sin(a) + 1.0 * math.cos(a)), (x1 + .6 * math.cos(a), y1 + .6 * math.sin(a)), (x1 - 2.4 * math.cos(a) + 1.0 * math.sin(a), y1 - 2.4 * math.sin(a) - 1.0 * math.cos(a))], 'steel', edge=False)
    ic.rect(1.6, 6.6, 3.4, 9.4, 'orange', edge=False)


@reg('s_steel_2')
def _(ic):
    ic.circ(8, 8, 6.4, 'steel')
    ic.ring(8, 8, 4.2, 5.2, 'steel', edge=False, bias=-.5)
    ic.rect(7, 3, 9, 13, 'orange', edge=False); ic.rect(3, 7, 13, 9, 'orange', edge=False)
    ic.circ(8, 8, 1.8, 'steel', edge=False, bias=.3)


@reg('s_steel_3')
def _(ic):
    sword(ic, 3, 11, 13.6, 4.6, 2.2)
    for y in (5, 8, 11.6):
        ic.line((1.6, y + 1), (5, y + 1), 1.0, 'orange', edge=False)
    flame(ic, 3.4, 14.2, 4, 1.6, 'fire', None)


@reg('s_steel_4')
def _(ic):
    for k in range(8):
        a = math.radians(k * 45 - 90)
        ic.line((8 + 2.4 * math.cos(a), 8 + 2.4 * math.sin(a)), (8 + 6.4 * math.cos(a), 8 + 6.4 * math.sin(a)), 1.4, 'steel', edge=False)
    ic.circ(8, 8, 2.2, 'orange')
    ic.px(7, 7, RP['orange'][4])


# ---------- reliquias ----------
@reg('r_rey_exanime')
def _(ic):
    ic.poly([(2, 12), (2.4, 4.4), (5.4, 8), (8, 3), (10.6, 8), (13.6, 4.4), (14, 12)], 'bone')
    ic.line((9, 4), (7.6, 12), 1.0, 'dark', edge=False)
    ic.px(5, 11, RP['teal'][3]); ic.px(11, 11, RP['teal'][3]); ic.px(8, 9, RP['teal'][4])
    ic.rect(2, 11, 14, 13, 'bone', edge=False, bias=-.3)


@reg('r_coloso_magma')
def _(ic):
    ic.poly([(2, 9), (4, 3.6), (10, 2.4), (14, 6), (13, 12.6), (7, 14.4), (3, 12.6)], 'dark')
    ic.circ(8, 8.4, 3.8, 'lava', edge=False)
    ic.circ(8, 8.4, 1.8, 'yel', edge=False)


@reg('r_reina_escarcha')
def _(ic):
    ic.rect(3, 11, 13, 13.4, 'ice')
    for x, h in ((3.4, 6), (6.2, 9), (8, 11), (9.8, 9), (12.6, 6)):
        ic.poly([(x - 1.4, 11.4), (x, 12 - h), (x + 1.4, 11.4)], 'white' if h == 11 else 'ice')
    ic.px(8, 8, RP['ice'][4])


@reg('r_devorador_vacio')
def _(ic):
    ic.poly([(1, 8), (4.6, 4), (8, 3), (11.4, 4), (15, 8), (11.4, 12), (8, 13), (4.6, 12)], 'purple')
    ic.circ(8, 8, 3.4, 'white', edge=False)
    ic.ell(8, 8, 1.3, 2.6, 'dark', edge=False)
    ic.px(7, 6, RP['white'][4])


@reg('r_ent_ancestral')
def _(ic):
    ic.poly([(8, 14.4), (2.4, 9), (3.6, 4.6), (8, 2.6), (12.4, 4.6), (13.6, 9)], 'wood')
    ic.line((8, 14), (8, 6), 1.0, 'dark', edge=False)
    ic.poly([(8, 7), (13.4, 1.8), (13, 7.4)], 'green')
    ic.px(5, 7, RP['yel'][3]); ic.px(11, 10, RP['yel'][3])


@reg('r_titan_tormenta')
def _(ic):
    ic.line((4, 14), (9, 6), 2.0, 'copper')
    ic.rect(6, 2, 14, 7.4, 'copper')
    ic.rect(6, 2, 14, 3.4, 'copper', edge=False, bias=.3)
    bolt(ic, 10.4, 5.2, .36, 'ice')


@reg('r_matriarca_sangre')
def _(ic):
    ic.poly([(3, 3), (13, 3), (12, 8), (9, 10), (7, 10), (4, 8)], 'gold')
    ic.rect(4.4, 3, 11.6, 6, 'red', edge=False)
    ic.rect(7, 9.8, 9, 12.4, 'gold', edge=False); ic.rect(4.6, 12.2, 11.4, 14, 'gold')
    ic.px(6, 4, RP['red'][4])


@reg('r_guardian_eclipse')
def _(ic):
    ic.circ(8, 8, 6.6, 'gold')
    ic.circ(9.2, 8, 5.2, 'dark', edge=False)
    ic.px(4, 5, RP['gold'][4]); ic.px(3, 7, RP['gold'][4])


@reg('r_sello_final')
def _(ic):
    pts = [(8 + 7 * math.cos(math.radians(22.5 + k * 45)), 8 + 7 * math.sin(math.radians(22.5 + k * 45))) for k in range(8)]
    ic.poly(pts, 'gold')
    ic.circ(8, 8, 4.4, 'red', edge=False)
    ic.circ(9.2, 8, 3.4, 'dark', edge=False)
    ic.px(5, 5, RP['gold'][4])


# ---------- clases (emblemas) ----------
def badge(ic, col_bg, col_ring):
    ic.circ(8, 8, 6.9, col_ring)
    ic.circ(8, 8, 5.4, col_bg, edge=False)


@reg('c_paladin')
def _(ic):
    badge(ic, 'dark', 'gold')
    ic.rect(7, 3.6, 9, 12.4, 'yel', edge=False); ic.rect(4.6, 6, 11.4, 7.8, 'yel', edge=False)


@reg('c_shadow')
def _(ic):
    badge(ic, 'dark', 'purple')
    ic.arc(8.6, 8, 2.8, 4.6, 90, 270, 'white', edge=False)
    ic.px(10, 8, RP['purple'][4])


@reg('c_flame')
def _(ic):
    badge(ic, 'dark', 'orange')
    flame(ic, 8, 12, 8, 3, 'fire', 'yel')


@reg('c_storm')
def _(ic):
    badge(ic, 'dark', 'blue')
    bolt(ic, 8, 8, .6, 'yel')


@reg('c_frost')
def _(ic):
    badge(ic, 'dark', 'ice')
    snowflake(ic, 8, 8, 3.8, 'white', 1.0)


@reg('c_verdant')
def _(ic):
    badge(ic, 'dark', 'green')
    ic.poly([(8, 3.2), (11.6, 7), (8, 12.6), (4.4, 7)], 'green', edge=False, bias=.2)
    ic.line((8, 4), (8, 12.4), 0.8, 'dark', edge=False)


@reg('c_blood')
def _(ic):
    badge(ic, 'dark', 'red')
    ic.arc(8, 8.4, 2.6, 4.2, 180, 330, 'red', edge=False)
    ic.line((5, 8.4), (5, 12), 1.0, 'bone', edge=False)


@reg('c_earth')
def _(ic):
    badge(ic, 'dark', 'copper')
    ic.poly([(3.6, 11.6), (7, 4.4), (9, 8), (10.4, 6.4), (12.6, 11.6)], 'stone', edge=False)


@reg('c_astral')
def _(ic):
    badge(ic, 'dark', 'pink')
    star5(ic, 8, 8.2, 3.9, 1.6, 'white')


@reg('c_steel')
def _(ic):
    badge(ic, 'dark', 'steel')
    ic.line((4.6, 11.6), (11.6, 4.4), 1.4, 'white', edge=False)
    ic.line((4.6, 4.4), (11.6, 11.6), 1.4, 'white', edge=False)


NAMES = ['attack', 'jump', 'roll', 'pause', 'play', 'settings', 'sound_on', 'sound_off', 'music_on', 'music_off', 'back', 'close', 'lock', 'star', 'coin', 'soul', 'heart', 'potion', 'key', 'skull', 'relic', 'door', 'altar', 'forge', 'shop', 'fountain', 'chest', 'elite',
         'boss', 'treasure', 'secret', 'map', 'burn', 'freeze', 'poison', 'bleed', 'shock', 'curse', 'shield', 'crown',
         'b_filo', 'b_corazon', 'b_alas', 'b_furia', 'b_sangre', 'b_brasas', 'b_glacial', 'b_chispa', 'b_espinas', 'b_piedra', 'b_fantasma', 'b_doble_salto', 'b_critico', 'b_alma', 'b_fortuna', 'b_escudo_estelar', 'b_enfriamiento', 'b_habilidad', 'b_ejecutor', 'b_iman', 'b_venganza', 'b_segunda', 'b_onda', 'b_egida', 'b_sabio', 'b_gigante', 'b_sombra', 'b_eclipse']
for c in ['paladin', 'shadow', 'flame', 'storm', 'frost', 'verdant', 'blood', 'earth', 'astral', 'steel']:
    NAMES += [f's_{c}_{i}' for i in (1, 2, 3, 4)]
NAMES += ['r_rey_exanime', 'r_coloso_magma', 'r_reina_escarcha', 'r_devorador_vacio', 'r_ent_ancestral', 'r_titan_tormenta', 'r_matriarca_sangre', 'r_guardian_eclipse', 'r_sello_final']
NAMES += [f'c_{c}' for c in ['paladin', 'shadow', 'flame', 'storm', 'frost', 'verdant', 'blood', 'earth', 'astral', 'steel']]


def render(name):
    ic = Ic()
    I[name](ic)
    return ic.finish()


def build():
    assert len(NAMES) == 127, len(NAMES)
    missing = [n for n in NAMES if n not in I]
    assert not missing, missing
    atlas = np.zeros((128, 256, 4))
    for i, n in enumerate(NAMES):
        atlas[(i // 16) * 16:(i // 16) * 16 + 16, (i % 16) * 16:(i % 16) * 16 + 16] = render(n)
    ensure(A + '/ui')
    Image.fromarray(to_u8(atlas), 'RGBA').save(A + '/ui/icons.png', optimize=True)
    json.dump({"cell": 16, "cols": 16, "names": NAMES}, open(A + '/ui/icons.json', 'w'))


def preview(scale=6):
    im = Image.open(A + '/ui/icons.png').convert('RGBA')
    bg = Image.new('RGBA', im.size, (30, 26, 40, 255))
    bg.alpha_composite(im)
    big = bg.resize((im.width * scale, im.height * scale), Image.NEAREST)
    d = ImageDraw.Draw(big)
    for i in range(128):
        x, y = (i % 16) * 16 * scale, (i // 16) * 16 * scale
        d.rectangle([x, y, x + 16 * scale - 1, y + 16 * scale - 1], outline=(44, 40, 60))
    big.convert('RGB').save(PREV + '/icons.png')
    # tamaño real x1 (legibilidad)
    small = bg.resize((im.width * 2, im.height * 2), Image.NEAREST)
    small.convert('RGB').save(PREV + '/icons_x2.png')


if __name__ == '__main__':
    build()
    preview()
