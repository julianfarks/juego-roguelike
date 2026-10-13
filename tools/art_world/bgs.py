"""Fondos parallax de los 9 biomas: (capa0 RGB opaca, capa1 RGBA, capa2 RGBA)."""
import numpy as np
from scipy import ndimage as ndi
from kit import rng
from bgkit import *


def blur(m, s):
    return ndi.gaussian_filter(m.astype(np.float32), s, mode=('nearest', 'wrap'))


# ------------------------------------------------------------------ formas
def gothic_opening(m, xa, xb, spring, base, v=255):
    """Apertura de arco apuntado (se talla con v=0 o se rellena con v=255)."""
    w = xb - xa
    pts = [(xa, base), (xa, spring)]
    for th in np.linspace(0, np.pi / 3, 8)[1:]:
        pts.append((xb - w * np.cos(th), spring - w * np.sin(th)))
    for th in np.linspace(np.pi / 3, 0, 8)[1:-1]:
        pts.append((xa + w * np.cos(th), spring - w * np.sin(th)))
    pts += [(xb, spring), (xb, base)]
    m.poly(pts, v)


def round_opening(m, xa, xb, spring, base, v=255):
    w = (xb - xa) / 2
    pts = [(xa, base), (xa, spring)]
    for th in np.linspace(np.pi, 0, 12)[1:-1]:
        pts.append((xa + w + w * np.cos(th), spring - w * np.sin(th)))
    pts += [(xb, spring), (xb, base)]
    m.poly(pts, v)


def spire(m, cx, base, w, h, v=255):
    m.poly([(cx - w / 2, base), (cx, base - h), (cx + w / 2, base)], v)


def pinnacled_tower(m, cx, base, w, h, roof=None, v=255):
    roof = roof if roof is not None else w * 1.6
    m.rect(cx - w / 2, base - h, cx + w / 2, base, v)
    spire(m, cx, base - h, w * 1.25, roof, v)
    # contrafuertes pequenos
    m.rect(cx - w / 2 - 2, base - h + 4, cx - w / 2, base - h + 10, v)
    m.rect(cx + w / 2, base - h + 4, cx + w / 2 + 2, base - h + 10, v)


def crenellated(m, x0, x1, ytop, base, v=255, step=6):
    m.rect(x0, ytop, x1, base, v)
    x = x0
    k = 0
    while x < x1:
        if k % 2 == 0:
            m.rect(x, ytop - 5, min(x + step, x1), ytop, v)
        x += step
        k += 1


def column(m, cx, y0, y1, w, v=255, capital=True):
    m.rect(cx - w / 2, y0, cx + w / 2, y1, v)
    if capital:
        m.rect(cx - w / 2 - 3, y0, cx + w / 2 + 3, y0 + 5, v)
        m.rect(cx - w / 2 - 2, y1 - 5, cx + w / 2 + 2, y1, v)


def stalactite(m, x, top, w, h, v=255, jag=0.0):
    m.poly([(x - w / 2, top), (x + jag, top + h), (x + w / 2, top)], v)


def stalagmite(m, x, base, w, h, v=255):
    m.poly([(x - w / 2, base), (x, base - h), (x + w / 2, base)], v)


def chain_line(m, x, y0, y1, w=2, v=255, sway=0):
    pts = [(x + np.sin((y - y0) * .05) * sway, y) for y in range(int(y0), int(y1), 3)]
    m.line(pts, w, v)
    for y in range(int(y0), int(y1), 7):
        m.ell(x + np.sin((y - y0) * .05) * sway, y, w + 1.5, 3.2, v)


def tentacle(m, pts, w0, v=255):
    n = len(pts) - 1
    for i in range(n):
        w = max(1, w0 * (1 - i / n))
        m.line([pts[i], pts[i + 1]], int(round(w)), v)
        m.ell(pts[i][0], pts[i][1], w / 2, w / 2, v)


def wavy(cx, y0, length, amp, freq, phase=0, step=4):
    return [(cx + np.sin(phase + (i * step) * freq) * amp * (i * step / length) ** .7, y0 + i * step) for i in range(int(length / step) + 1)]


def pine(m, cx, base, h, w, v=255):
    pts = [(cx, base - h)]
    levels = 6
    for i in range(levels):
        y = base - h + (i + 1) * h / levels * .98
        ww = w / 2 * (i + 1) / levels
        pts.append((cx + ww, y))
        pts.append((cx + ww * .45, y - h / levels * .35))
    left = []
    for i in range(levels - 1, -1, -1):
        y = base - h + (i + 1) * h / levels * .98
        ww = w / 2 * (i + 1) / levels
        left.append((cx - ww * .45, y - h / levels * .35))
        left.append((cx - ww, y))
    m.poly(pts + left[::-1][::-1][:0] + left, v)
    m.rect(cx - 1.5, base - 6, cx + 1.5, base, v)


def broad_tree(m, cx, base, h, w, trunk_w, seed, v=255):
    r = rng(seed)
    m.poly([(cx - trunk_w / 2, base), (cx - trunk_w * .35, base - h * .5), (cx + trunk_w * .35, base - h * .5), (cx + trunk_w / 2, base)], v)
    for _ in range(9):
        a = r.rand() * 6.28
        d = r.rand() * w * .38
        m.ell(cx + np.cos(a) * d, base - h * .72 + np.sin(a) * d * .7, w * (.18 + r.rand() * .12), w * (.14 + r.rand() * .1), v)


def gear_shape(m, cx, cy, r, teeth=10, v=255, hole=None):
    for k in range(teeth):
        a = k * 2 * np.pi / teeth
        m.poly([(cx + np.cos(a - .13) * r * .85, cy + np.sin(a - .13) * r * .85),
                (cx + np.cos(a - .09) * r * 1.2, cy + np.sin(a - .09) * r * 1.2),
                (cx + np.cos(a + .09) * r * 1.2, cy + np.sin(a + .09) * r * 1.2),
                (cx + np.cos(a + .13) * r * .85, cy + np.sin(a + .13) * r * .85)], v)
    m.ell(cx, cy, r, r, v)
    if hole:
        m.ell(cx, cy, hole, hole, 0)


def shade_by_height(base_col, top_col, y0, y1):
    t = np.clip((YY - y0) / max(1, y1 - y0), 0, 1)[..., None]
    return np.asarray(hexrgb(top_col) if isinstance(top_col, str) else top_col) * (1 - t) + np.asarray(hexrgb(base_col) if isinstance(base_col, str) else base_col) * t


def motes(rgb, n, seed, col, ymin=.1, ymax=.9, k=1.0):
    r = rng(seed)
    c = hexrgb(col) if isinstance(col, str) else col
    for _ in range(n):
        x = r.randint(0, W)
        y = int(H * (ymin + (ymax - ymin) * r.rand()))
        b = (.4 + .6 * r.rand()) * k
        rgb[y, x] = np.maximum(rgb[y, x], c * b)
        if r.rand() < .25:
            rgb[y, (x + 1) % W] = np.maximum(rgb[y, (x + 1) % W], c * b * .5)
    return rgb


def emissive_points(layer, pts, col, r=3, k=.5):
    m = np.zeros((H, W), np.float32)
    for (x, y) in pts:
        m[int(y) % H, int(x) % W] = 1
    g = blur(m, r) * (r * r * 6)
    layer.blend(np.clip(g, 0, 1) * k, col)
    for (x, y) in pts:
        layer.glowlit(np.eye(1, dtype=bool) if False else _pt(x, y), col)


def _pt(x, y):
    m = np.zeros((H, W), bool)
    m[int(y) % H, int(x) % W] = True
    return m


def windows(layer, rects, col, halo=4, k=.55, hot=None):
    m = np.zeros((H, W), bool)
    for (x0, y0, x1, y1) in rects:
        for ox in (-W, 0, W):
            xa, xb = int(x0 + ox), int(x1 + ox)
            if xb <= 0 or xa >= W:
                continue
            m[int(y0):int(y1), max(0, xa):min(W, xb)] = True
    g = blur(m, halo) * 2.2
    layer.blend(np.clip(g, 0, 1) * k, col)
    layer.glowlit(m, col)
    if hot is not None:
        mh = m & ~shift(m, 1, 0) & False
    return m


def rays(rgb, cx, cy, col, k, seed, n=14, length=400, spread=1.0):
    ang = np.arctan2(YY - cy, np.minimum(np.abs(XX - cx), W - np.abs(XX - cx)) * np.sign(XX - cx + .5 + 1e-6))
    r = rng(seed)
    f = np.zeros((H, W), np.float32)
    d = np.sqrt(wrapdx(cx) ** 2 + (YY - cy) ** 2)
    for _ in range(n):
        a0 = r.rand() * 6.28
        wd = .03 + r.rand() * .05
        da = np.abs(((ang - a0 + np.pi) % (2 * np.pi)) - np.pi)
        f += np.clip(1 - da / wd, 0, 1) * (r.rand() * .6 + .4)
    f *= np.clip(1 - d / length, 0, 1) ** 1.5
    rgb += f[..., None] * hexrgb(col) * k
    return rgb


# ================================================================== CATACUMBAS
def bg_catacumbas():
    r0 = grad([(0, '#04070e'), (.35, '#0a1422'), (.72, '#0e1e2a'), (1, '#12303a')])
    n = noise(8, 5, 4, 11)
    # ladrillos tenues
    br = ((YY % 12 == 0) | (((XX + (YY // 12 % 2) * 16) % 32) == 0))
    r0 *= np.where(br, .8, 1.0)[..., None]
    r0 *= (.9 + .2 * n)[..., None]
    # grandes arcos con aperturas de bruma
    mo = Mask()
    for k in range(4):
        xa = k * 128 + 14
        gothic_opening(mo, xa, xa + 100, 120, 330)
    op = mo.arr()
    t = np.clip((YY - 60) / 220, 0, 1)[..., None]
    openc = np.asarray(hexrgb('#0c1a2a')) * (1 - t) + np.asarray(hexrgb('#1f5a55')) * t
    r0 = np.where(op[..., None], openc * (.8 + .4 * noise(5, 4, 3, 5)[..., None]), r0)
    # reborde claro del arco
    edge = op & ~shift(op, 1, 0) | op & ~shift(op, 0, 1)
    r0[edge] = r0[edge] * .5 + hexrgb('#4a7a90') * .5
    # rayos de luz de ventanas
    for x0 in (60, 330):
        poly = Mask().poly([(x0, 0), (x0 + 36, 0), (x0 + 130, 288), (x0 + 40, 288)])
        f = blur(poly.arr(), 5) * .12
        r0 += f[..., None] * hexrgb('#8ad8ff')
    glow_add(r0, 256, 290, 260, '#2a9a70', .15, 1.6, sy=.5)
    stars(r0, 40, 4, .8, (60, 140), (.4, 1, .7), big=.0)
    motes(r0, 36, 7, '#5cff9a', .25, .95, .8)
    # --- capa 1: arcada y lapidas
    L1 = Layer()
    m = Mask()
    # nervaduras del techo (arcos colgantes)
    for k in range(3):
        xa = int(k * 170.67) + 8
        xb = xa + 155
        m.rect(xa - 12, 0, xb + 12, 38)
        gothic_opening(m, xa, xb, 78, 0, 0)
        # pilares laterales
        m.rect(xa - 11, 0, xa + 6, 288)
        column(m, xa - 3, 36, 288, 17, capital=True)
    # lapidas y cruces bajas
    r = rng(3)
    for x in (70, 140, 250, 330, 420, 480):
        h = r.randint(14, 26)
        m.rect(x - 7, 280 - h, x + 7, 288)
        m.ell(x, 280 - h, 7, 6)
    for x in (110, 300, 450):
        m.rect(x - 2, 256, x + 2, 288)
        m.rect(x - 8, 262, x + 8, 266)
    sil = m.arr()
    base = shade_by_height('#0e1a28', '#0a1420', 0, 288)
    L1.paint(sil, base)
    L1.haze('#173c46', 80, 288, .4)
    L1.rim(sil, '#5ad8a0', k=.5)
    L1.tint_inside(sil & (YY < 40), '#0a121c', .35)
    L1.fog(235, 40, '#2e8a78', .8, 21, alpha_cap=.32)
    L1.fog(120, 50, '#2a5a6a', .5, 22, alpha_cap=.25)
    # almas flotantes
    pts = [(60, 200), (190, 150), (300, 220), (420, 130), (470, 210)]
    emissive_points(L1, pts, '#8affc0', 3, .35)
    # --- capa 2
    L2 = Layer()
    m = Mask()
    for x, w in ((58, 30), (352, 26)):
        m.rect(x - w / 2, 0, x + w / 2, 288)
        m.rect(x - w / 2 - 4, 0, x + w / 2 + 4, 10)
        m.rect(x - w / 2 - 3, 50, x + w / 2 + 3, 58)
    cols = m.arr()
    m2 = Mask()
    for x in (160, 164, 226, 440):
        chain_line(m2, x, 0, [110, 90, 140, 70][[160, 164, 226, 440].index(x)], 2)
    for x, w, h in ((120, 30, 40), (200, 22, 28), (300, 36, 52), (400, 20, 30), (470, 26, 36)):
        stalactite(m2, x, 0, w, h)
    ch = m2.arr()
    L2.paint(cols, '#04070c', .88)
    L2.paint(ch, '#05080e', .95)
    L2.rim(cols | ch, '#3a8a7a', k=.5, up=False)
    L2.fog(250, 36, '#2e8a78', .7, 31, alpha_cap=.25)
    return r0, L1, L2


# ================================================================== FORJA
def bg_forja():
    r0 = grad([(0, '#07030a'), (.4, '#1a0910'), (.72, '#4a1410'), (1, '#8a2c0c')])
    n = noise(4, 3, 5, 3)
    smoke = np.clip((n - .42) * 2.2, 0, 1)
    r0 = r0 * (1 - smoke[..., None] * .35) + smoke[..., None] * hexrgb('#1c0c10') * .5
    # volcanes lejanos
    hf = ridge(3, 5, 4)
    mm = Mask().heightfield(235, hf, 110)
    mt = mm.arr()
    mcol = shade_by_height('#2a0c0e', '#12060a', 120, 290)
    r0 = np.where(mt[..., None], mcol, r0)
    # venas de lava
    ml = Mask()
    r = rng(8)
    for _ in range(18):
        x = r.randint(0, W)
        y = int(235 - hf[x] * 110) + r.randint(4, 30)
        pts = [(x, y)]
        for k in range(r.randint(3, 6)):
            pts.append((pts[-1][0] + r.randint(-6, 6), pts[-1][1] + r.randint(4, 12)))
        ml.line(pts, 1)
    lv = ml.arr() & mt
    r0[lv] = hexrgb('#ff7a1a') * .85
    r0 = r0 + blur(lv, 2.5)[..., None] * hexrgb('#ff5a10') * .5
    # rio de lava en el horizonte
    band = np.exp(-((YY - 268) / 14.0) ** 2) * (.6 + .6 * noise(10, 3, 3, 9))
    r0 += band[..., None] * hexrgb('#ff7a22') * .5
    glow_add(r0, 150, 130, 180, '#ff5a14', .35, 2.2, sy=.8)
    glow_add(r0, 400, 150, 150, '#ff4a10', .28, 2.2, sy=.8)
    motes(r0, 90, 6, '#ffa040', .25, 1.0, .9)
    # --- capa 1: industria
    L1 = Layer()
    m = Mask()
    r = rng(14)
    xs = [30, 100, 175, 240, 330, 395, 460]
    for i, x in enumerate(xs):
        w = r.randint(36, 60)
        h = r.randint(60, 110)
        m.rect(x - w / 2, 288 - h, x + w / 2, 288)
        m.poly([(x - w / 2, 288 - h), (x - w / 4, 288 - h - 14), (x + w / 4, 288 - h - 14), (x + w / 2, 288 - h)])
    for x, h, w in ((68, 150, 14), (205, 175, 16), (365, 140, 14), (500, 160, 15)):
        m.rect(x - w / 2, 288 - h, x + w / 2, 288)
        m.poly([(x - w / 2 - 3, 288 - h), (x - w / 2, 288 - h - 7), (x + w / 2, 288 - h - 7), (x + w / 2 + 3, 288 - h)])
    gear_shape(m, 140, 190, 30, 12, hole=9)
    gear_shape(m, 300, 210, 22, 10, hole=6)
    m.rect(0, 150, 512, 154)  # pasarela
    for x in range(0, 512, 32):
        m.rect(x, 154, x + 2, 170)
    sil = m.arr()
    L1.paint(sil, shade_by_height('#1a0b10', '#0e0609', 40, 288))
    L1.haze('#4a1812', 100, 288, .32)
    L1.rim(sil, '#ff8a2a', k=.55)
    rects = []
    rr_ = rng(77)
    for i, x in enumerate(xs):
        if rr_.rand() < .6:
            rects.append((x - 6, 288 - 70 + (i % 3) * 8, x + 2, 288 - 62 + (i % 3) * 8))
        if rr_.rand() < .4:
            rects.append((x + 10, 288 - 50, x + 16, 288 - 44))
    windows(L1, rects, '#ffb040', 3, .5)
    # humo
    for x, h in ((68, 150), (205, 175), (365, 140), (500, 160)):
        sm = np.exp(-(((XX - x - 12 * np.sin((YY) * .04)) % W) ** 2 if False else (wrapdx(x) - 0) ** 2) / (2 * (10 + (288 - h - YY) * -.06) ** 2)) * (YY < 288 - h) * .5
        sm *= (.5 + .8 * noise(8, 5, 3, int(x))).astype(np.float32)
        L1.blend(np.clip(sm, 0, .45) * (YY > 20), '#3a1a1a')
    L1.fog(250, 36, '#c04818', .7, 41, alpha_cap=.28)
    # --- capa 2
    L2 = Layer()
    m = Mask()
    for x, y1 in ((60, 96), (62, 70), (250, 130), (400, 110), (402, 80)):
        chain_line(m, x, 0, y1, 3)
    m.rect(0, 0, 512, 16)
    for x in range(20, 512, 96):
        m.rect(x, 16, x + 8, 30)
    m.rect(150, 28, 360, 40)  # tuberia
    m.rect(150, 22, 160, 44)
    m.rect(350, 22, 360, 44)
    gear_shape(m, 450, 6, 36, 12, hole=10)
    ch = m.arr()
    L2.paint(ch, '#0a0507', .95)
    L2.rim(ch, '#ff7a1a', k=.55, up=False, left=True)
    L2.fog(266, 24, '#c04818', .7, 51, alpha_cap=.28)
    return r0, L1, L2


# ================================================================== HELADO
def bg_helado():
    r0 = grad([(0, '#030818'), (.3, '#0a1c44'), (.62, '#163e78'), (.85, '#2a6a9c'), (1, '#3e84ac')])
    stars(r0, 160, 2, .55, (110, 255), (.8, .9, 1), big=.2)
    # aurora
    for (yb, amp, ph, col, k, cx) in [(95, 24, 0, '#4cffa0', .55, 2), (70, 18, 2, '#4ae0ff', .38, 3), (120, 20, 4, '#a060ff', .3, 2)]:
        yc = yb + amp * np.sin(XX / W * 2 * np.pi * cx + ph) + 8 * np.sin(XX / W * 2 * np.pi * (cx * 3) + ph * 2)
        dy = YY - yc
        profile = np.where(dy < 0, np.exp(-(dy / 36.0) ** 2), np.exp(-(dy / 6.0) ** 2))
        streak = .55 + .6 * vnoise(W, 1, 40, 1, int(ph * 10 + 3))[0][None, :] * np.ones((H, 1))
        vert = np.clip(1 + dy / 90.0, 0, 1)
        f = profile * streak * vert
        r0 += f[..., None] * hexrgb(col) * k
    # luna
    glow_add(r0, 90, 60, 55, '#a8d0ff', .35, 2.0)
    mm = Mask().ell(90, 60, 11, 11)
    r0[mm.arr()] = hexrgb('#e8f4ff')
    # montanas lejanas
    hf = ridge(4, 9, 4)
    mt = Mask().heightfield(250, hf, 90).arr()
    r0 = np.where(mt[..., None], shade_by_height('#0c2a56', '#2a5a98', 130, 290), r0)
    top = mt & ~shift(mt, 1, 0)
    snow = mt & (YY < (250 - hf * 90 + 5)[None, :])
    r0[snow] = r0[snow] * .4 + hexrgb('#c8e8ff') * .6
    glow_add(r0, 256, 290, 300, '#a0e0ff', .1, 1.6, sy=.5)
    # --- capa 1
    L1 = Layer()
    m = Mask()
    hf2 = ridge(6, 17, 5, .6)
    m.heightfield(260, hf2, 75)
    r = rng(19)
    for x, h, w in ((50, 150, 22), (170, 125, 18), (290, 170, 24), (410, 135, 20)):
        m.poly([(x - w / 2, 288), (x - w * .3, 288 - h * .7), (x - 2, 288 - h), (x + w * .1, 288 - h * .9), (x + w * .35, 288 - h * .55), (x + w / 2, 288)])
    for x in range(10, 512, 37):
        if r.rand() < .6:
            pine(m, x + r.randint(-6, 6), 290, r.randint(40, 70), r.randint(18, 28))
    sil = m.arr()
    L1.paint(sil, shade_by_height('#10285a', '#0a1c44', 100, 288))
    L1.haze('#2a5a90', 120, 288, .35)
    L1.rim(sil, '#e0f4ff', k=.7)
    L1.fog(240, 40, '#a8d8f0', .7, 61, alpha_cap=.28)
    pts = [(50, 150), (170, 180), (290, 125), (410, 170)]
    emissive_points(L1, pts, '#d8f8ff', 2, .35)
    # --- capa 2
    L2 = Layer()
    m = Mask()
    r = rng(23)
    x = 0
    while x < W:
        w = r.randint(10, 26)
        h = r.randint(18, 70)
        if r.rand() < .65:
            stalactite(m, x + w / 2, 0, w, h, jag=r.randint(-2, 2))
        x += r.randint(14, 40)
    m.rect(0, 0, 512, 6)
    for xc, h in ((120, 110), (380, 90)):
        m.poly([(xc - 12, 288), (xc - 9, 288 - h * .7), (xc, 288 - h), (xc + 10, 288 - h * .6), (xc + 13, 288)])
    ch = m.arr()
    L2.paint(ch, '#061030', .88)
    L2.rim(ch, '#7ae8ff', k=.65)
    L2.fog(262, 22, '#b8e4f8', .7, 71, alpha_cap=.25)
    return r0, L1, L2


# ================================================================== VACIO
def bg_vacio():
    r0 = grad([(0, '#020008'), (.5, '#0b0420'), (1, '#1a0838')])
    n = noise(3, 2, 5, 5)
    neb = np.clip((n - .45) * 2.2, 0, 1) ** 1.4
    r0 += neb[..., None] * hexrgb('#5a24a0') * .55
    n2 = noise(4, 3, 4, 17)
    r0 += (np.clip((n2 - .55) * 2.5, 0, 1) ** 1.6)[..., None] * hexrgb('#c03cc0') * .3
    stars(r0, 320, 9, .85, (80, 255), (.8, .75, 1), big=.12)
    # orbe del vacio
    cx, cy, rr = 340, 118, 58
    d = np.sqrt(wrapdx(cx) ** 2 + (YY - cy) ** 2)
    ring = np.exp(-((d - rr) / 5.0) ** 2)
    r0 += ring[..., None] * hexrgb('#c070ff') * .65
    r0 += (np.exp(-((d - rr) / 22.0) ** 2) * (d > rr))[..., None] * hexrgb('#6a2ab0') * .5
    disc = d < rr
    r0[disc] = hexrgb('#02000a') * (1 + .5 * noise(6, 6, 3, 4)[disc][:, None])
    # anillo / disco de acrecion
    dx = XX - cx
    ell = (dx / 1.7) ** 2 + (YY - cy) ** 2
    acc = np.exp(-((np.sqrt(ell) - rr * .95) / 3.0) ** 2) * (np.abs(YY - cy) < 20)
    r0 += acc[..., None] * hexrgb('#e8b0ff') * .55 * (dx < 90)[..., None] * (np.abs(dx) < 130)[..., None]
    # grietas del vacio
    mc = Mask()
    r = rng(2)
    for _ in range(6):
        x, y = r.randint(0, W), r.randint(10, 140)
        pts = [(x, y)]
        for k in range(r.randint(5, 9)):
            pts.append((pts[-1][0] + r.randint(-10, 10), pts[-1][1] + r.randint(4, 14)))
        mc.line(pts, 1)
    cr = mc.arr()
    r0 += blur(cr, 2.5)[..., None] * hexrgb('#a050ff') * .8
    r0[cr] = hexrgb('#e8c0ff')
    glow_add(r0, 256, 290, 280, '#5a20a0', .15, 1.6, sy=.45)
    # --- capa 1: islas flotantes
    L1 = Layer()
    m = Mask()
    r = rng(7)
    for (x, y, w) in ((60, 110, 70), (190, 170, 50), (300, 80, 40), (420, 150, 80), (500, 200, 40), (130, 60, 36)):
        top = [(x - w / 2, y), (x - w * .25, y - 6), (x + w * .2, y - 8), (x + w / 2, y)]
        bot = [(x + w * .42, y + 8), (x + w * .2, y + w * .35), (x + 4, y + w * .7), (x - 2, y + w * .5), (x - w * .25, y + w * .3), (x - w * .4, y + 8)]
        m.poly(top + bot)
        for k in range(3):
            xx = x - w * .3 + k * w * .3
            stalagmite(m, xx, y - 5, 8, r.randint(8, 20))
    hf = ridge(5, 4, 4, .6)
    m.heightfield(268, hf, 50)
    sil = m.arr()
    L1.paint(sil, shade_by_height('#0a0620', '#0e0830', 60, 288))
    L1.haze('#2e1456', 80, 288, .4)
    L1.rim(sil, '#b070ff', k=.65)
    # brillo inferior de las islas (energia)
    under = sil & ~shift(sil, -1, 0) & (YY < 250)
    L1.rgb[under] = L1.rgb[under] * .4 + hexrgb('#8a40d8') * .6
    L1.fog(245, 36, '#6a30b0', .7, 81, alpha_cap=.3)
    pts = [(80, 100), (200, 160), (310, 70), (430, 140)]
    emissive_points(L1, pts, '#d8a0ff', 3, .35)
    # --- capa 2: tentaculos y ojos
    L2 = Layer()
    m = Mask()
    r = rng(9)
    for x in (30, 150, 270, 400, 480):
        L = r.randint(60, 120)
        pts = wavy(x, 0, L, r.randint(14, 26), .07, r.rand() * 6)
        tentacle(m, pts, 9)
    for (x, y1) in ((90, 40), (350, 50)):
        stalactite(m, x, 0, 30, y1 + 30)
    ch = m.arr()
    L2.paint(ch, '#04010c', .92)
    L2.rim(ch, '#a050ff', k=.6, up=False)
    ey = []
    for (x, y) in ((60, 150), (330, 170), (460, 100)):
        ey += [(x, y), (x + 6, y)]
    emissive_points(L2, ey, '#e8a0ff', 3, .3)
    return r0, L1, L2


# ================================================================== BOSQUE
def bg_bosque():
    r0 = grad([(0, '#040a0a'), (.4, '#0b1f1c'), (.75, '#12302a'), (1, '#173a2c')])
    glow_add(r0, 380, 70, 130, '#8ad0a8', .38, 2.0)
    mm = Mask().ell(380, 70, 12, 12)
    r0[mm.arr()] = hexrgb('#d8f8d0')
    r = rng(5)
    for depth, (col, wr, cnt) in enumerate([('#0b1e1c', (4, 7), 30), ('#09181a', (6, 10), 20)]):
        m = Mask()
        for _ in range(cnt):
            x = r.randint(0, W)
            w = r.randint(*wr)
            m.rect(x, 0, x + w, 288)
        t = m.arr()
        r0 = np.where(t[..., None], hexrgb(col) * (.85 + .3 * noise(8, 4, 2, 3)[..., None]), r0)
    # niebla
    r0 += (noise(3, 3, 4, 13) * np.exp(-((YY - 220) / 55.0) ** 2))[..., None] * hexrgb('#4aa088') * .2
    # copa superior
    cn = noise(10, 2, 4, 6)
    crown = (YY < 30 + cn * 40) & (cn > .35)
    r0[crown] = hexrgb('#05100e') * (.8 + .5 * cn[crown][:, None])
    motes(r0, 40, 3, '#ffc24a', .2, .95, .8)
    # --- capa 1
    L1 = Layer()
    m = Mask()
    r = rng(12)
    for x, w in ((40, 26), (150, 34), (270, 22), (370, 30), (470, 26)):
        m.poly([(x - w / 2, 288), (x - w * .4, 200), (x - w * .3, 40), (x + w * .3, 40), (x + w * .4, 200), (x + w / 2, 288)])
        # raices
        m.poly([(x - w / 2 - 14, 288), (x - w / 2 + 2, 250), (x - w * .3, 262), (x - w * .5, 288)])
        m.poly([(x + w / 2 + 14, 288), (x + w / 2 - 2, 250), (x + w * .3, 262), (x + w * .5, 288)])
        # ramas
        m.line([(x, 90), (x + 40, 60), (x + 70, 66)], 5)
        m.line([(x, 120), (x - 40, 92), (x - 66, 98)], 4)
    # copas
    for x in range(0, 512, 38):
        m.ell(x + r.randint(-8, 8), r.randint(0, 22), r.randint(22, 36), r.randint(14, 26))
    sil = m.arr()
    L1.paint(sil, shade_by_height('#0b1c16', '#07120f', 40, 288))
    L1.haze('#183c30', 100, 288, .4)
    L1.rim(sil, '#8ad060', k=.4)
    L1.fog(235, 38, '#4aa088', .8, 91, alpha_cap=.28)
    # hongos luminosos
    hm = Mask()
    for x in (90, 210, 320, 440):
        for k in range(3):
            hx = x + k * 9 - 9
            hh = [8, 14, 6][k]
            hm.rect(hx - 1, 288 - hh, hx + 1, 288)
            hm.ell(hx, 288 - hh, 5 - k % 2, 3)
    mush = hm.arr()
    L1.paint(mush, '#ffc24a', 1.0)
    L1.blend(blur(mush, 4) * 2.2, '#ffa030', .5)
    L1.rgb[mush & (YY % 2 == 0)] = hexrgb('#ffe698')
    fl = [(60, 150), (130, 100), (230, 180), (300, 120), (400, 190), (470, 90), (350, 60)]
    emissive_points(L1, fl, '#ffd870', 2, .3)
    # --- capa 2
    L2 = Layer()
    m = Mask()
    for x, w in ((20, 44), (330, 50)):
        m.poly([(x - w / 2, 288), (x - w * .42, 150), (x - w * .35, 0), (x + w * .35, 0), (x + w * .42, 160), (x + w / 2, 288)])
        m.poly([(x - w / 2 - 24, 288), (x - w / 2 + 4, 236), (x - w * .3, 252), (x - w * .5, 288)])
    r = rng(15)
    for x in (110, 160, 230, 400, 450, 490):
        L = r.randint(50, 130)
        pts = wavy(x, 0, L, 8, .09, r.rand() * 6)
        m.line(pts, 2)
        for i in range(2, len(pts), 3):
            m.ell(pts[i][0] + 2, pts[i][1], 3, 2)
    m.rect(0, 0, 512, 5)
    for x in range(0, 512, 52):
        m.ell(x + 10, 6, 22, 10)
    ch = m.arr()
    L2.paint(ch, '#030a08', .9)
    L2.rim(ch, '#6aa850', k=.35, up=False)
    L2.fog(264, 24, '#4aa088', .7, 101, alpha_cap=.25)
    return r0, L1, L2


# ================================================================== TORMENTA
def bg_tormenta():
    r0 = grad([(0, '#060c14'), (.4, '#12243a'), (.75, '#224650'), (1, '#386e6c')])
    n = noise(5, 3, 5, 3)
    cl = np.clip((n - .4) * 2.6, 0, 1)
    shade = np.clip(1 - (YY / 288.0) * 1.2, 0, 1)
    r0 = r0 * (1 - cl[..., None] * .5) + (cl * .5)[..., None] * hexrgb('#0a1620')
    n2 = noise(6, 4, 4, 9)
    hl = np.clip((n2 - .5) * 2.4, 0, 1) * cl * .6
    r0 += hl[..., None] * hexrgb('#4a7a8a') * .5
    glow_add(r0, 150, 90, 200, '#a8e0ff', .3, 1.8, sy=.8)
    # rayo
    ml = Mask()
    r = rng(4)
    x, y = 150, 0
    pts = [(x, y)]
    while y < 210:
        x += r.randint(-9, 9)
        y += r.randint(8, 18)
        pts.append((x, y))
    ml.line(pts, 2)
    for k in (4, 8):
        bx, by = pts[k]
        bp = [(bx, by)]
        for _ in range(4):
            bx += r.randint(2, 11) * (1 if k == 4 else -1)
            by += r.randint(5, 12)
            bp.append((bx, by))
        ml.line(bp, 1)
    lt = ml.arr()
    r0 += blur(lt, 5)[..., None] * hexrgb('#80c8ff') * 1.2
    r0[lt] = hexrgb('#f0fcff')
    # mar/horizonte
    hf = ridge(8, 6, 3, .5)
    mt = Mask().heightfield(262, hf, 14).arr()
    r0 = np.where(mt[..., None], hexrgb('#0a1a20'), r0)
    # --- capa 1: fortaleza
    L1 = Layer()
    m = Mask()
    hf2 = ridge(3, 11, 4, .55)
    m.heightfield(250, hf2, 70)
    r = rng(8)
    for x, w, h in ((60, 40, 140), (160, 30, 110), (250, 50, 170), (360, 34, 120), (450, 44, 150)):
        crenellated(m, x - w / 2, x + w / 2, 288 - h, 288)
        m.poly([(x - w / 2 - 4, 288 - h - 5), (x, 288 - h - 36), (x + w / 2 + 4, 288 - h - 5)])
        m.rect(x - 1, 288 - h - 50, x + 1, 288 - h - 34)
    m.rect(78, 160, 142, 166)
    m.rect(180, 140, 232, 146)
    m.rect(270, 150, 345, 156)
    sil = m.arr()
    L1.paint(sil, shade_by_height('#0e1c24', '#08121a', 60, 288))
    L1.haze('#2a5a62', 110, 288, .55)
    L1.rim(sil, '#58b8e8', k=.55)
    rects = []
    for (x, h) in ((60, 140), (160, 110), (250, 170), (360, 120), (450, 150)):
        for k in range(3):
            rects.append((x - 5, 288 - h + 16 + k * 22, x - 1, 288 - h + 22 + k * 22))
            rects.append((x + 5, 288 - h + 28 + k * 22, x + 9, 288 - h + 34 + k * 22))
    windows(L1, rects, '#b8f0ff', 3, .45)
    L1.fog(230, 40, '#4a8a90', .8, 111, alpha_cap=.3)
    # --- capa 2
    L2 = Layer()
    m = Mask()
    r = rng(21)
    for x, w in ((100, 22), (390, 26)):
        m.rect(x - w / 2, 0, x + w / 2, 288)
        m.rect(x - w / 2 - 3, 60, x + w / 2 + 3, 66)
        for yy in range(80, 288, 40):
            m.rect(x - w / 2 - 1, yy, x + w / 2 + 1, yy + 3)
    for (x0, x1, y0) in ((100, 390, 10), (390, 612, 14)):
        pts = []
        for i in range(0, 21):
            t = i / 20
            pts.append((x0 + (x1 - x0) * t, y0 + 38 * np.sin(np.pi * t)))
        m.line(pts, 2)
    m.rect(0, 0, 512, 4)
    ch = m.arr()
    L2.paint(ch, '#040a10', .9)
    L2.rim(ch, '#58b8e8', k=.5, up=False)
    # lluvia
    rain = np.zeros((H, W), np.float32)
    for _ in range(140):
        x, y = r.randint(0, W), r.randint(0, H)
        ln_ = r.randint(8, 18)
        for k in range(ln_):
            rain[(y + k) % H, (x - k // 3) % W] = .5 * (1 - k / ln_)
    L2.blend(rain, '#9ad0e8')
    return r0, L1, L2


# ================================================================== SANGRE
def bg_sangre():
    r0 = grad([(0, '#0a0208'), (.4, '#280812'), (.8, '#420e16'), (1, '#5a1218')])
    cx, cy = 300, 112
    d = np.sqrt(wrapdx(cx) ** 2 + (YY - cy) ** 2)
    ang = np.arctan2(YY - cy, XX - cx)
    glow_add(r0, cx, cy, 190, '#d02040', .5, 1.8)
    R_ = 66
    disc = d < R_
    seg = (np.floor((ang + np.pi) / (2 * np.pi) * 12).astype(int)) % 3
    ring = np.floor(d / 22).astype(int)
    pal = [hexrgb('#c01c38'), hexrgb('#f05a30'), hexrgb('#8a1a6a')]
    col = np.zeros((H, W, 3), np.float32)
    for k in range(3):
        col += (seg == k)[..., None] * pal[(k + ring) % 3][None, None, :] if False else 0
    sel = (seg + ring) % 3
    cols = np.array(pal)
    col = cols[sel] * (.7 + .5 * np.clip(1 - d / R_, 0, 1))[..., None]
    lead = ((np.abs(((ang + np.pi) / (2 * np.pi) * 12) % 1 - .0) < .04) | (np.abs(d % 22) < 1.2) | (np.abs(d - R_) < 2.5))
    col = np.where(lead[..., None], hexrgb('#1a0408'), col)
    core = d < 9
    col = np.where(core[..., None], hexrgb('#ffd8a0'), col)
    r0 = np.where(disc[..., None], col, r0)
    # petalos pequenos
    for k in range(8):
        a = k * np.pi / 4
        px, py = cx + np.cos(a) * 44, cy + np.sin(a) * 44
        dd = np.sqrt((XX - px) ** 2 + (YY - py) ** 2)
        r0[dd < 7] = r0[dd < 7] * .6 + hexrgb('#ff8a60') * .5
    # rayos de luz sobre el suelo
    for x0, wd in ((200, 30), (300, 40), (390, 28)):
        poly = Mask().poly([(x0 - 14, 150), (x0 + 14, 150), (x0 + wd + 60, 288), (x0 - wd - 20, 288)])
        r0 += (blur(poly.arr(), 4) * .11)[..., None] * hexrgb('#ff4a5a')
    # arcos tenues de la nave
    mo = Mask()
    for k in range(4):
        gothic_opening(mo, k * 128 + 10, k * 128 + 112, 150, 340)
    op = mo.arr()
    e = op & ~shift(op, 1, 0) | op & ~shift(op, 0, 1)
    r0[e & (d > R_ + 4)] *= 1.5
    r0 += (noise(3, 3, 4, 23) * np.exp(-((YY - 240) / 50.0) ** 2))[..., None] * hexrgb('#c02840') * .22
    motes(r0, 50, 5, '#ff6a7c', .2, .95, .7)
    # --- capa 1: lanceta y pilares
    L1 = Layer()
    m = Mask()
    for k in range(4):
        xa = k * 128 + 16
        m.rect(xa - 14, 0, xa + 8, 288)
        m.rect(xa - 18, 0, xa + 12, 14)
        m.rect(xa - 17, 160, xa + 11, 168)
        m.rect(xa + 8, 0, xa + 128 - 14, 44)
        gothic_opening(m, xa + 12, xa + 128 - 24, 96, 0, 0)
    sil = m.arr()
    # vitrales en las lancetas
    L1.paint(sil, shade_by_height('#1c0610', '#12040a', 40, 288))
    L1.haze('#3a0c16', 100, 288, .35)
    L1.rim(sil, '#ff6a7c', k=.45)
    rects = []
    for k in range(4):
        xa = k * 128 + 16
        rects.append((xa + 36, 150, xa + 40, 262 - 40))
    wm = Mask()
    for k in range(4):
        xa = k * 128 + 16
        gothic_opening(wm, xa + 22, xa + 52, 190, 250)
    wmask = wm.arr() & ~sil
    cols_ = np.array([hexrgb('#d02040'), hexrgb('#a02a8a'), hexrgb('#f06a30'), hexrgb('#c01c38'), hexrgb('#e8506a')])
    wxs = np.zeros((H, W), int)
    for k in range(4):
        wxs[:, k * 128 + 16 + 22:k * 128 + 16 + 52] = k
    lx = (XX - (wxs * 128 + 16 + 22))
    cell_x = lx // 10
    cell_y = (YY - 150) // 12
    idx = (cell_x * 2 + cell_y * 3 + wxs) % 5
    wc = cols_[idx] * (.75 + .4 * np.clip((YY - 150) / 110.0, 0, 1))[..., None]
    lead = (lx % 10 == 9) | ((YY - 150) % 12 == 11) | (lx % 10 == 0) & False
    wc = np.where(lead[..., None], hexrgb('#1a0408'), wc)
    L1.blend(blur(wmask, 5) * 1.6, '#c02040', .45)
    L1.rgb[wmask] = wc[wmask]
    L1.a[wmask] = 1
    L1.fog(235, 40, '#8a1a2a', .8, 121, alpha_cap=.3)
    # --- capa 2
    L2 = Layer()
    m = Mask()
    for x, w in ((64, 36), (350, 40)):
        m.rect(x - w / 2, 0, x + w / 2, 288)
        m.rect(x - w / 2 - 5, 0, x + w / 2 + 5, 12)
        m.rect(x - w / 2 - 4, 90, x + w / 2 + 4, 98)
    r = rng(31)
    for x in (140, 210, 440):
        pts = [(x - 20, 0), (x + 20, 0)]
        L = r.randint(60, 120)
        for i in range(0, 9):
            pts.append((x + 20 - i * 5 + (4 if i % 2 else -4), L * (i / 8) * .15 + L * .85))
        m.poly([(x - 18, 0), (x + 18, 0), (x + 14, L * .5), (x + 20, L), (x + 8, L - 8), (x, L + 6), (x - 8, L - 10), (x - 16, L), (x - 12, L * .5)])
    ch = m.arr()
    L2.paint(ch, '#060104', .9)
    L2.rim(ch, '#ff3a50', k=.45, up=False)
    L2.fog(262, 24, '#8a1a2a', .7, 131, alpha_cap=.28)
    return r0, L1, L2


# ================================================================== ECLIPSE
def bg_eclipse():
    r0 = grad([(0, '#03030a'), (.5, '#0c0c24'), (.85, '#1c1a3c'), (1, '#2a2450')])
    stars(r0, 220, 6, .8, (90, 255), (1, .95, .8), big=.15)
    # sol eclipsado
    cx, cy, rr = 212, 100, 34
    d = np.sqrt(wrapdx(cx) ** 2 + (YY - cy) ** 2)
    glow_add(r0, cx, cy, 200, '#f0c050', .45, 2.2)
    corona = np.exp(-((d - rr) / 7.0) ** 2) * (d > rr)
    r0 += corona[..., None] * hexrgb('#fff0b0') * 1.1
    r0 = rays(r0, cx, cy, '#ffd070', .55, 3, n=22, length=240)
    r0[d <= rr] = hexrgb('#020207')
    # anillo de diamante
    dd = np.sqrt((XX - (cx + 24)) ** 2 + (YY - (cy - 24)) ** 2)
    r0 += (np.exp(-(dd / 4.0) ** 2))[..., None] * hexrgb('#ffffff') * 1.2
    # luna
    mx, my, mr = 340, 150, 24
    d2 = np.sqrt(wrapdx(mx) ** 2 + (YY - my) ** 2)
    glow_add(r0, mx, my, 80, '#9aa8d8', .3, 2.0)
    moon = d2 < mr
    mcol = hexrgb('#c8cce8') * (.7 + .4 * noise(10, 10, 3, 5)[..., None])
    shadow = np.sqrt((XX - (mx + 11)) ** 2 + (YY - (my - 3)) ** 2) < mr * .95
    r0 = np.where(moon[..., None], np.where(shadow[..., None], hexrgb('#101028'), mcol), r0)
    r0 += (np.exp(-((d2 - mr) / 2.5) ** 2) * (~shadow))[..., None] * hexrgb('#e8ecff') * .5
    glow_add(r0, 256, 290, 280, '#6a4ab0', .14, 1.6, sy=.45)
    motes(r0, 50, 3, '#f0d070', .1, .95, .6)
    # --- capa 1: templo
    L1 = Layer()
    m = Mask()
    for k in range(4):
        x = 20 + k * 128
        column(m, x, 44, 288, 22)
    m.rect(0, 30, 512, 44)
    m.rect(0, 24, 512, 30)
    m.poly([(60, 24), (90, 4), (124, 24)])
    m.poly([(330, 24), (352, 8), (386, 24)])
    # obeliscos flotantes
    for (x, y, h) in ((110, 150, 40), (290, 180, 34), (460, 140, 44)):
        m.poly([(x - 7, y + h), (x - 5, y), (x, y - 12), (x + 5, y), (x + 7, y + h)])
    sil = m.arr()
    L1.paint(sil, shade_by_height('#0e0e22', '#0a0a1a', 40, 288))
    L1.haze('#2a2458', 80, 288, .4)
    L1.rim(sil, '#f0c050', k=.6)
    L1.fog(240, 40, '#6a4a98', .8, 141, alpha_cap=.28)
    pts = [(60, 140), (140, 200), (250, 120), (330, 210), (420, 100), (490, 180)]
    emissive_points(L1, pts, '#f8dc78', 2, .35)
    # --- capa 2
    L2 = Layer()
    m = Mask()
    for x, w in ((70, 34), (360, 38)):
        m.rect(x - w / 2, 0, x + w / 2, 288)
        m.rect(x - w / 2 - 4, 0, x + w / 2 + 4, 14)
        m.rect(x - w / 2 - 3, 120, x + w / 2 + 3, 126)
    r = rng(33)
    for x, y1 in ((170, 90), (250, 120), (452, 70)):
        chain_line(m, x, 0, y1, 2)
    ch = m.arr()
    L2.paint(ch, '#05050c', .9)
    L2.rim(ch, '#f0c050', k=.6, up=False)
    gl = np.zeros((H, W), bool)
    for x, w in ((70, 34), (360, 38)):
        for y in (16, 118, 128):
            gl[y:y + 1, int(x - w / 2):int(x + w / 2)] = True
    L2.glowlit(gl & ch, '#b88a30')
    L2.fog(264, 24, '#6a4a98', .7, 151, alpha_cap=.25)
    return r0, L1, L2


# ================================================================== CAZADOR
def bg_cazador():
    r0 = grad([(0, '#0a0412'), (.35, '#280a22'), (.7, '#561428'), (1, '#782030')])
    stars(r0, 60, 5, .5, (60, 160), (1, .8, .8), big=.0)
    cx, cy, rr = 330, 112, 78
    d = np.sqrt(wrapdx(cx) ** 2 + (YY - cy) ** 2)
    glow_add(r0, cx, cy, 210, '#ff4050', .5, 1.8)
    glow_add(r0, cx, cy, 120, '#ff6a60', .3, 2.2)
    moon = d < rr
    nz = noise(8, 8, 4, 3)
    mcol = shade_by_height('#8a1020', '#d02a34', cy - rr, cy + rr)
    mcol = mcol * (.75 + .5 * nz[..., None])
    # crateres
    r = rng(2)
    for _ in range(9):
        px, py, pr = cx + r.randint(-50, 50), cy + r.randint(-50, 50), r.randint(5, 13)
        dd = np.sqrt((XX - px) ** 2 + (YY - py) ** 2)
        mcol = np.where((dd < pr)[..., None], mcol * .72, mcol)
        mcol = np.where(((dd >= pr - 1.5) & (dd < pr) & (XX < px))[..., None], mcol * 1.25, mcol)
    r0 = np.where(moon[..., None], mcol, r0)
    r0 += (np.exp(-((d - rr) / 3.0) ** 2) * (d > rr))[..., None] * hexrgb('#ff7a70') * .6
    # nubes
    cl = noise(6, 3, 4, 7)
    band = np.exp(-((YY - 130) / 40.0) ** 2)
    cm = np.clip((cl - .5) * 3, 0, 1) * band
    r0 = r0 * (1 - cm[..., None] * .75) + cm[..., None] * hexrgb('#1a0614') * .75
    cl2 = noise(5, 2, 4, 17)
    cm2 = np.clip((cl2 - .55) * 3, 0, 1) * np.exp(-((YY - 60) / 30.0) ** 2)
    r0 = r0 * (1 - cm2[..., None] * .6) + cm2[..., None] * hexrgb('#2a0c26') * .6
    glow_add(r0, 256, 290, 300, '#b02838', .2, 1.5, sy=.45)
    # --- capa 1: ciudad gotica
    L1 = Layer()
    m = Mask()
    r = rng(5)
    x = 0
    kinds = []
    while x < W:
        w = r.randint(34, 70)
        h = r.randint(70, 150)
        kind = r.choice(['gable', 'mansard', 'flat', 'tower'])
        kinds.append((x, w, h, kind))
        x += w + r.randint(0, 6)
    for (x, w, h, kind) in kinds:
        m.rect(x, 288 - h, x + w, 288)
        if kind == 'gable':
            m.poly([(x - 3, 288 - h), (x + w / 2, 288 - h - w * .6), (x + w + 3, 288 - h)])
        elif kind == 'mansard':
            m.poly([(x - 2, 288 - h), (x + 8, 288 - h - 16), (x + w - 8, 288 - h - 16), (x + w + 2, 288 - h)])
        elif kind == 'tower':
            spire(m, x + w / 2, 288 - h, w * .8, w * 1.8)
        m.rect(x + w * .2, 288 - h - 24, x + w * .2 + 6, 288 - h)
        m.rect(x + w * .2 - 1, 288 - h - 28, x + w * .2 + 7, 288 - h - 24)
    # catedral
    cxn = 130
    m.rect(cxn - 40, 150, cxn + 40, 288)
    pinnacled_tower(m, cxn - 30, 288, 22, 190, 70)
    pinnacled_tower(m, cxn + 30, 288, 22, 190, 70)
    spire(m, cxn, 150, 26, 60)
    # arbotantes
    m.poly([(cxn - 40, 160), (cxn - 70, 200), (cxn - 70, 288), (cxn - 40, 288)])
    m.poly([(cxn + 40, 160), (cxn + 70, 200), (cxn + 70, 288), (cxn + 40, 288)])
    sil = m.arr()
    L1.paint(sil, shade_by_height('#14081c', '#0c0412', 60, 288))
    L1.haze('#481222', 100, 288, .4)
    L1.rim(sil, '#ff4a5a', k=.45)
    rects = []
    for (x, w, h, kind) in kinds:
        for k in range(2):
            if r.rand() < .55:
                rects.append((x + 6 + k * 18, 288 - h + 14 + (k * 7) % 20, x + 11 + k * 18, 288 - h + 22 + (k * 7) % 20))
    windows(L1, rects, '#ffb040', 3, .45)
    rose = Mask().ell(cxn, 170, 8, 8).arr()
    L1.glowlit(rose, '#e03048')
    L1.fog(238, 40, '#a02434', .8, 161, alpha_cap=.32)
    # --- capa 2
    L2 = Layer()
    m = Mask()
    for x in (60, 300, 450):
        m.rect(x - 1.5, 80, x + 1.5, 288)
        m.rect(x - 5, 76, x + 5, 80)
        m.rect(x - 4, 60, x + 4, 76)
        m.poly([(x - 6, 60), (x, 50), (x + 6, 60)])
        m.rect(x - 5, 270, x + 5, 288)
    # reja baja
    for x in range(0, 512, 12):
        m.rect(x, 250, x + 2, 288)
        m.poly([(x - 1, 250), (x + 1, 242), (x + 3, 250)])
    m.rect(0, 258, 512, 261)
    m.rect(0, 276, 512, 279)
    # ramas secas arriba
    r = rng(3)
    for x in (30, 200, 380):
        pts = [(x, 0)]
        for k in range(5):
            pts.append((pts[-1][0] + r.randint(-14, 18), pts[-1][1] + r.randint(14, 24)))
        m.line(pts, 3)
        for p in pts[2:]:
            m.line([p, (p[0] + r.randint(-26, 26), p[1] + r.randint(10, 26))], 1)
    # gargola
    for gx in (120,):
        m.poly([(gx - 14, 0), (gx + 14, 0), (gx + 12, 22), (gx + 4, 30), (gx - 4, 30), (gx - 12, 22)])
        m.poly([(gx - 14, 8), (gx - 34, 20), (gx - 12, 24)])
    ch = m.arr()
    L2.paint(ch, '#05020a', .92)
    L2.rim(ch, '#ff3a50', k=.4, up=False)
    lamp = Mask()
    for x in (60, 300, 450):
        lamp.rect(x - 3, 62, x + 3, 74)
    lm = lamp.arr()
    L2.blend(blur(lm, 6) * 2.5, '#ffa040', .6)
    L2.glowlit(lm, '#ffc860')
    L2.fog(262, 22, '#a02434', .7, 171, alpha_cap=.25)
    # cuervos
    cm = Mask()
    for (x, y) in ((220, 120), (236, 132), (210, 140)):
        cm.poly([(x - 6, y), (x, y - 3), (x + 6, y), (x, y + 1)])
    L2.paint(cm.arr(), '#05020a', 1.0)
    return r0, L1, L2


BGS = dict(catacumbas=bg_catacumbas, forja=bg_forja, helado=bg_helado, vacio=bg_vacio, bosque=bg_bosque,
           tormenta=bg_tormenta, sangre=bg_sangre, eclipse=bg_eclipse, cazador=bg_cazador)
