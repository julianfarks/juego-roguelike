import math
from props_kit import *
from props_arch import GOLDG, SOULF

HEART = [rgb(c) for c in ('#3c0a22', '#8a1030', '#d41e3c', '#ff5a64', '#ffc0c0')]
GLASS = [rgb(c) for c in ('#2a3858', '#5a78a0', '#9cc0dc', '#e0f4ff')]
POT = [rgb(c) for c in ('#4a0a2a', '#a01438', '#e8304c', '#ff8090', '#ffd8d8')]


def sheet_gold():
    sh = PSheet('pick_gold', 8, 8, [4, 4], [6, 6])

    def fr(c, i, n):
        w = [2.6, 1.8, 0.7, 1.8][i]
        cx, cy = 4, 4
        if w < 1:
            c.flat(c.rect(3, 1, 5, 7), GOLDG[2])
            c.px(3, 2, GOLDG[4]); c.px(3, 3, GOLDG[3])
            c.vline(4, 1, 7, GOLDG[1])
            return
        m = c.ell(cx, cy, w, 3.0)
        c.paint(m, GOLDG, bevel=1.6, bias=0.6, rim=True, dark_edge=True, dith=0.2, light=(-0.9 if i != 3 else 0.9, -0.5))
        if i in (0, 1, 3):
            inner = c.ell(cx, cy, max(0.6, w - 1.3), 1.7)
            c.paint(inner, GOLDG, bevel=1.0, bias=0.45, rim=False, dark_edge=False, dith=0.0)
        if i == 0:
            c.px(2, 2, GOLDG[4], top=True)
        if i == 1:
            c.px(3, 2, GOLDG[4], top=True)
        if i == 3:
            c.px(5, 5, GOLDG[3], top=True)
    sh.anim('idle', 4, 10, True, fr, outline=True)
    return sh


def sheet_soul():
    sh = PSheet('pick_soul', 10, 10, [5, 5], [8, 8])

    def fr(c, i, n):
        ph = i / n * 2 * math.pi
        flame(c, 5, 8, 8 + round(math.sin(ph)), 3.0, ph, SOULF, sway=1.0, lick=1.2, pw=0.8)
        # cuerpo/nucleo del alma
        c.paint(c.ell(5, 6.3, 2.6, 2.4), SOULF, bevel=2.0, bias=0.75, rim=False, dark_edge=False, dith=0.2)
        c.px(4, 5, SOULF[4]); c.px(5, 5, SOULF[4])
        # ojitos
        c.px(4, 6, SOULF[0]); c.px(6, 6, SOULF[0])
        # chispa
        c.px(8 - (i % 3), 1 + (i * 2) % 5, SOULF[3], top=True)
        c.px(1 + (i * 3) % 4, 2 + i % 3, SOULF[2], top=True)
    sh.anim('idle', 6, 10, True, fr)
    return sh


def heart_mask(c, cx, cy, s):
    x = (c.xx + 0.5 - cx) / s
    y = -(c.yy + 0.5 - cy) / s
    return ((x * x + y * y - 1) ** 3 - x * x * y ** 3) <= 0


def sheet_heart():
    sh = PSheet('pick_heart', 10, 10, [5, 5], [8, 8])

    def fr(c, i, n):
        s = 3.0 if i == 0 else 3.45
        m = heart_mask(c, 5, 5.2 + (0.2 if i else 0), s)
        c.paint(m, HEART, bevel=2.4, bias=0.58, rim=True, dith=0.3, light=(-0.9, -0.7))
        c.px(3, 3, HEART[4]); c.px(2, 4, HEART[3]) if i == 0 else c.px(2, 3, HEART[3])
        if i == 1:
            c.px(0, 1, HEART[3], top=True); c.px(9, 2, HEART[3], top=True)
    sh.anim('idle', 2, 4, True, fr)
    return sh


def sheet_potion():
    sh = PSheet('pick_potion', 10, 12, [5, 6], [8, 10])

    def fr(c, i, n):
        # frasco de cristal
        body = c.ell(5, 8, 3.6, 3.4)
        neck = c.rect(4, 3, 7, 6)
        c.paint(body | neck, GLASS, bevel=1.8, bias=0.5, rim=True, dith=0.2)
        # liquido
        top = 6 if i == 0 else 6
        liq = (body & (c.yy >= top)) & ~c.rect(0, 0, 10, 0)
        liq = c.ell(5, 8, 2.8, 2.6) & (c.yy >= 6)
        c.paint(liq, POT, bevel=1.8, bias=0.6, rim=False, dark_edge=False, dith=0.2)
        c.hline(3 + i, 6 + i, 6, POT[3])
        # corcho
        c.paint(c.rect(4, 1, 7, 3), R('#a8743c', 4, 0.2), bevel=0.8, bias=0.6)
        c.px(3, 8, POT[4]) if i == 0 else c.px(3, 7, POT[4])
        c.px(2, 7, GLASS[3]) if i == 0 else c.px(2, 8, GLASS[3])
        if i == 1:
            c.px(5, 5, POT[3], top=False)
            c.px(8, 2, (255, 200, 210), top=True)
    sh.anim('idle', 2, 4, True, fr)
    return sh


def sheet_relic():
    sh = PSheet('pick_relic', 16, 16, [8, 8], [12, 12])
    GEM = [rgb(c) for c in ('#3a0a40', '#8a1a9a', '#d03ae0', '#ff90ff', '#ffe8ff')]

    def fr(c, i, n):
        t = i / n
        ph = t * 2 * math.pi
        bob = round(math.sin(ph) * 0.5)
        cy = 8 + bob
        # anillo/amuleto dorado: octogono con hueco-gema
        oct_ = c.poly([(5, cy - 4), (11, cy - 4), (14, cy - 1), (14, cy + 2), (11, cy + 5), (5, cy + 5), (2, cy + 2), (2, cy - 1)])
        c.paint(oct_, GOLDG, bevel=1.8, bias=0.72, grad=0.1, rim=True, dith=0.3, light=(-0.9, -0.8))
        inner = c.poly([(6, cy - 2), (10, cy - 2), (12, cy), (10, cy + 3), (6, cy + 3), (4, cy)])
        c.paint(inner, GOLDG, bevel=1.0, bias=0.35, rim=False, dark_edge=True, dith=0.0)
        sphere(c, 8, cy + 0.5, 2.6, GEM, hl=(-0.4, -0.5))
        c.px(7, cy - 1, GEM[4]); c.px(8, cy - 1, GEM[3])
        # destello que barre en diagonal
        sweep = (t * 2.0 - 0.5) * 22 - 6
        for k in range(16):
            for l in range(16):
                if abs((k + l) - sweep) < 1.0 and c.a[l, k] and (k + l) % 1 == 0:
                    c.c[l, k] = mix(tuple(int(v) for v in c.c[l, k]), (255, 250, 220), 0.75)
        c.lightpass(8, cy, 7, (255, 230, 140), 0.25)
        # brillo estrella en esquinas
        pts = [(2, 2), (13, 3), (3, 13), (12, 13), (8, 1)]
        for k, (x, y) in enumerate(pts):
            tw = (t * 3 + k * 0.37) % 1.0
            if tw < 0.16:
                c.px(x, y, (255, 250, 220), top=True)
                if tw < 0.1:
                    c.px(x - 1, y, GOLDG[3], top=True); c.px(x + 1, y, GOLDG[3], top=True)
                    c.px(x, y - 1, GOLDG[3], top=True); c.px(x, y + 1, GOLDG[3], top=True)
            elif tw < 0.3:
                c.px(x, y, GOLDG[2], top=True)
    sh.anim('idle', 6, 8, True, fr)
    return sh


SHEETS = [sheet_gold, sheet_soul, sheet_heart, sheet_potion, sheet_relic]
