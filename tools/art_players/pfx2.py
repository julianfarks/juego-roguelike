"""Particulas / efectos de los reposos AFK 5..10 (se estampan sobre el fotograma ya reducido)."""
import math
import numpy as np
from pfx import *
from pfx import rnd, put, disk, star4, plus, seg, bolt, rise, ring, crystal, leaf, flower, fade, tip, blade, head_front, foot_pts, ph, dust, sweat, bang


# ---------------------------------------------------------------- piezas
def note(c, x, y, col):
    for k in range(5):
        put(c, x + 1, y - k, col)
    put(c, x + 2, y - 4, col); put(c, x + 3, y - 3, col)
    put(c, x, y, col); put(c, x, y + 1, col); put(c, x + 1, y + 1, col)


def zed(c, x, y, col, s=1):
    for k in range(3 * s):
        put(c, x + k, y, col); put(c, x + k, y - 2 * s, col)
    for k in range(2 * s + 1):
        put(c, x + 2 * s - k * s, y - k, col)


def puff(c, x, y, k, col=(236, 238, 246), dk=(190, 196, 214)):
    """nube pequeña que crece con k (0..3)."""
    r = 1 + k * .7
    disk(c, x + k * 1.6, y - k * .6, r, col, rim=dk)


def sprite(c, x, y, rows, cmap):
    """dibuja un patron de caracteres con centro (x, y)."""
    h = len(rows); w = max(len(r) for r in rows)
    for j, r in enumerate(rows):
        for k, ch in enumerate(r):
            if ch in cmap:
                put(c, x - w // 2 + k, y - h // 2 + j, cmap[ch])


def butterfly(c, x, y, col, i, dk=(60, 40, 90)):
    if i % 2 == 0:
        sprite(c, x, y, ["ww.k.ww", "wwwkwww", ".ww.ww."], {'w': col, 'k': dk})
    else:
        sprite(c, x, y, ["..wkw..", "..wkw..", "..wkw.."], {'w': col, 'k': dk})


def bird(c, x, y, i, body=(70, 140, 220), belly=(250, 240, 200), fly=False):
    wing = (40, 90, 170)
    rows = [".bbbb.", "bbbbbby", "bbbbbb.", ".wwww..", "..l.l.."] if not fly else \
           ([".bbbb.", "bbbbbby", "bbbbbb.", ".wwww..", "..l.l.."] if i % 2 else [".bbbb.", "bbbbbby", "bbbbbb.", ".wwww..", "......."])
    sprite(c, x, y, rows, {'b': body, 'y': (245, 190, 60), 'w': belly, 'l': (200, 150, 60)})
    if fly:
        for k in range(3):
            put(c, x - 3 + k, y - 3 - (1 if i % 2 else 0) + k * (0 if i % 2 else 1), wing)
    else:
        put(c, x - 3, y - 1, wing); put(c, x - 2, y - 1, wing)
    put(c, x + 1, y - 1, (20, 20, 30))


def orb(c, x, y, r, col, rim, hi=(255, 255, 255)):
    disk(c, x, y, r, col, rim=rim)
    put(c, x - r * .3, y - r * .3, hi)


def dots(c, pts, col):
    for p in pts:
        put(c, p[0], p[1], col)


def clink(c, x, y, col=(255, 240, 180)):
    star4(c, x, y, col, (255, 255, 255))


def snow_burst(c, x, y, i, i0, i1, cols, n=7, spd=1.2):
    if i0 <= i <= i1:
        t = i - i0
        for k in range(n):
            a = -0.5 + k / (n - 1) * 1.6 + rnd(k, 3) * .3
            put(c, x + math.cos(a) * (3 + t * 2.4) * spd, y + math.sin(a) * (3 + t * 2.4) * .8 + t * .6 * (k % 2), cols[k % len(cols)])


# ---------------------------------------------------------------- paladin
def f_paladin(c, name):
    i, sk = c.i, c.sk
    g, gl = (255, 210, 90), (255, 246, 200)
    if name == 'idle5':
        if 4 <= i <= 12:
            t = tip(c, 22)
            a = min(1, (i - 3) / 2, (13 - i) / 2)
            hgt = int(52 * a)
            for yy in range(int(t[1]), int(t[1]) - hgt, -1):
                if yy < -AN.XPIVOT[1] + 3: break
                if (t[1] - yy) > 36 and rnd(yy, i) < (t[1] - yy - 36) / 18: continue
                for dx in (-2, -1, 0, 1, 2):
                    if abs(dx) == 2 and (yy + i) % 2: continue
                    put(c, t[0] + dx, yy, gl if abs(dx) < 1 else g)
            star4(c, t[0], t[1], gl, (255, 255, 255), size=2)
            rise(c, [(t[0], t[1] + 4)], 2, [gl, g, (230, 160, 40)], life=7, count=3, speed=1.0, spread=4, start=4)
    elif name == 'idle6':
        if i in (3, 4, 6, 7):
            s = sk.shF
            for k in range(6):
                put(c, s[0] + 2 + rnd(i, k) * 7 - 1, s[1] + 4 + rnd(i, k, 1) * 6 - 3, g if k % 2 else gl)
    elif name == 'idle7':
        if 4 <= i <= 9 and i % 2 == 0:
            h = sk.handB
            star4(c, h[0] + 4, h[1] - 4, gl, (255, 255, 255))
        if i in (10, 11):
            hf = head_front(c)
            star4(c, hf[0] + 1, hf[1] - 1, gl, (255, 255, 255), size=2)
    elif name == 'idle8':
        if 5 <= i <= 8:
            hf = head_front(c)
            puff(c, hf[0] + 1, hf[1] + 1, i - 5)
        if i in (5, 6):
            clink(c, sk.shF[0] - 5, sk.shF[1] - 1, g); clink(c, sk.shF[0] + 6, sk.shF[1], g)
        if i in (2, 3, 4):
            put(c, sk.head[0] + 3, sk.head[1] - 7, (255, 200, 200))
    elif name == 'idle9':
        if 2 <= i <= 11:
            t = tip(c, 22)
            if i % 2 == 0: star4(c, t[0], t[1] - 2, gl, (255, 255, 255))
        if i in (11, 12):
            bang(c, sk.head[0] + 1, sk.head[1] - 9)
    elif name == 'idle10':
        if i in (3, 6, 9):
            clink(c, sk.ankF[0] + 3, sk.ankF[1] - 9, g); clink(c, sk.ankB[0] - 3, sk.ankB[1] - 10, g)
        if i >= 9:
            sweat(c, sk.head[0] - 4, sk.head[1] - 2, (i - 9) % 5)


# ---------------------------------------------------------------- shadow
def f_shadow(c, name):
    i, sk = c.i, c.sk
    v, vl = (176, 96, 255), (226, 190, 255)
    if name == 'idle5':
        for k, ang in enumerate((0.0, 1.9)):                         # dagas en el aire
            pass
        for k in range(2):
            t = (i * (0.5 if k == 0 else 0.5) + k * 3.1) % 6.0
            x = 6 + k * 6 + math.sin(i * .7 + k * 3) * 3
            y = -40 - 10 * abs(math.sin(t / 6 * math.pi)) - 3 * k
            seg(c, x - 1, y - 3, x + 1, y + 3, (190, 200, 224)); put(c, x - 1, y - 3, vl); put(c, x + 1, y + 4, v)
    elif name == 'idle6':
        a = 1.0
        if 3 <= i <= 4: a = 1 - (i - 2.5) / 2
        elif 5 <= i <= 9: a = 0.28 + 0.1 * math.sin(i)
        elif 10 <= i <= 11: a = 0.28 + (i - 9.5) * .3
        fade(c, a)
        if 4 <= i <= 10:
            rise(c, [(sk.head[0], sk.head[1] + 8), (sk.head[0] + 2, sk.head[1] + 20)], 3, [vl, v, (110, 50, 190)], life=6, count=3, speed=.8, spread=7, start=4)
            for k in (0, 1):
                put(c, sk.head[0] + 3 + k * 2, sk.head[1] - 1, (255, 255, 255))   # ojos brillan
    elif name == 'idle7':
        if i % 4 in (0, 1) and 4 <= i <= 12:
            note(c, sk.head[0] + 8 + (i - 4) * .7, sk.head[1] - 6 - (i - 4) * .8, vl if i % 2 else v)
        if i in (11, 12):
            put(c, sk.head[0] + 5, sk.head[1] + 3, (255, 160, 160))
    elif name == 'idle8':
        if 4 <= i <= 9:
            h = sk.handB
            for k in range(3):
                orb(c, h[0] + 3 + k * 1.5, h[1] - 2 - k * .6 + ((i + k) % 2), 1.4, (255, 214, 96), (190, 130, 30))
            if i % 2 == 0: star4(c, h[0] + 5, h[1] - 7, (255, 246, 190))
        if i in (7, 8): bang(c, sk.head[0] + 1, sk.head[1] - 9, (255, 214, 96))
    elif name == 'idle9':
        if 4 <= i <= 11:
            hf = head_front(c)
            put(c, hf[0] + 1, hf[1] - 1, (255, 255, 255)); put(c, hf[0] + 3, hf[1] - 1, (255, 255, 255))
            if i % 2 == 0: seg(c, hf[0] - 3, hf[1] - 5, hf[0] - 1, hf[1] - 7, v)
    elif name == 'idle10':
        if i in (3, 5, 7):
            x, y = sk.handF[0] + 4, 0
            put(c, x, y - 1, (190, 200, 224)); star4(c, x + 3, y - 3, vl, (255, 255, 255))
            for dx in (-3, 3): put(c, x + dx, y, (110, 90, 100))


# ---------------------------------------------------------------- flame
def fball(c, x, y, r):
    disk(c, x, y, r, (255, 150, 40), rim=(255, 90, 24)); disk(c, x, y + .3, r * .55, (255, 235, 150))


def f_flame(c, name):
    i, sk = c.i, c.sk
    cols = [(255, 240, 160), (255, 192, 64), (255, 110, 30), (170, 40, 20)]
    if name == 'idle5':
        h = sk.handB
        for k in range(3):
            a = (i * 0.9 + k * 2.1)
            ph_ = (math.sin(a) + 1) / 2
            x = h[0] + 3 + math.cos(a * .8 + k) * 7
            y = h[1] - 6 - ph_ * 24
            fball(c, x, y, 2.0)
            rise(c, [(x, y - 2)], 11 + k, cols, life=4, count=1, speed=1.1, spread=.8)
    elif name == 'idle6':
        pts = blade(c, [6, 12, 18, 24, 30])
        if 4 <= i <= 8:
            rise(c, pts, 4, cols, life=6, count=int(2 + (i - 3) * 1.6), speed=1.8, spread=1.5, start=4)
            if i == 4:
                star4(c, *tip(c, 32), (255, 220, 120), (255, 255, 255), size=2)
        if i in (9, 10, 11):
            dots(c, [(p[0] + 1, p[1] - 1 - (i - 9)) for p in pts[::2]], cols[min(3, i - 9 + 1)])
        if i in (11, 12):
            for k in range(4):
                put(c, sk.head[0] + 5 + (i - 11) * 3, sk.head[1] + 5 + k - (i - 11), (180, 180, 190))      # humito
    elif name == 'idle7':
        t = tip(c, 30)
        if 3 <= i <= 12:
            rise(c, blade(c, [10, 20, 30]), 6, cols, life=3, count=1, speed=.9, spread=1.0, start=3)
            if i < 11:
                disk(c, t[0] + 2, t[1], 2.2, (252, 244, 232), rim=(230, 200, 170))   # malvavisco
                tone = min(2, max(0, (i - 5) // 2))
                if i >= 6: put(c, t[0] + 2, t[1], [(252, 244, 232), (222, 170, 90), (130, 80, 40)][tone])
                if i >= 8: put(c, t[0] + 1, t[1] - 1, (140, 90, 50)); put(c, t[0] + 3, t[1] + 1, (110, 70, 40))
            else:
                disk(c, t[0] + 2, t[1], 2.2, (120, 76, 40), rim=(60, 40, 24))
                put(c, t[0] + 3, t[1] - 1, (255, 255, 255)) if i == 11 else None
        if i in (10, 11, 12):
            star4(c, sk.head[0] + 4, sk.head[1] - 8, (255, 220, 120))
    elif name == 'idle8':
        if i in (3, 6, 9):
            hf = head_front(c)
            for k in range(5):
                put(c, hf[0] + 1 + k * 1.5, hf[1] - 1 - k * .7, cols[k % 3])
            fball(c, hf[0] + 8, hf[1] - 5, 1.2)
        if i in (4, 7, 10):
            hf = head_front(c)
            put(c, hf[0] + 1, hf[1] - 5, (120, 120, 130)); put(c, hf[0] + 2, hf[1] - 6, (150, 150, 160))
    elif name == 'idle9':
        a = min(1, (i - 2) / 2, (12 - i) / 2)
        if a > 0:
            cx, cy = sk.head[0], -22
            rise(c, [(cx - 7, -2), (cx + 7, -2), (cx, -2), (cx - 12, -2), (cx + 12, -2)], 7, cols, life=14, count=int(2 + 5 * a), speed=2.4, spread=2, start=2)
            for k in range(7):
                aa = k / 7 * 2 * math.pi + i * .4
                put(c, cx + math.cos(aa) * 13, cy + math.sin(aa) * 9, cols[k % 3])
        if i in (4, 5): ring(c, 0, -1, 8 + (i - 4) * 6, (255, 150, 40))
    elif name == 'idle10':
        for j in range(14):
            ii = i - j * 0.3
            if ii < 1.5: break
            q = c.cls.blade_pts(c.seq.at(ii), [(30, 0)])[0]
            col = cols[min(3, j // 4)]
            put(c, q[0], q[1], col)
            if j < 4: put(c, q[0] + 1, q[1], col)


# ---------------------------------------------------------------- storm
Z = (77, 200, 255); ZC = (230, 250, 255)


def f_storm(c, name):
    i, sk = c.i, c.sk
    if name == 'idle5':
        if 3 <= i <= 8:
            for j, p in enumerate(c.cls.blade_pts(c.p, [(10, 0), (20, 0), (30, 0)])):
                put(c, p[0], p[1], Z)
            t = tip(c, 30)
            star4(c, t[0], t[1], Z, ZC)
        if 3 <= i <= 8:
            ring(c, 0, -2, 8 + (i - 3) * 2, Z)
    elif name == 'idle6':
        if 3 <= i <= 10:
            h = sk.handF
            for k in range(2):
                bolt(c, (h[0] + 2, h[1] - 1), (h[0] + 2 + (rnd(i, k) - .5) * 14, h[1] - 7 - rnd(i, k, 3) * 7), i * 3 + k, Z, ZC, jag=1.4)
        if i >= 10:
            for k in range(6):
                a = k / 6 * 2 * math.pi + i
                bolt(c, (sk.head[0], sk.head[1] - 5), (sk.head[0] + math.cos(a) * 11, sk.head[1] - 6 + math.sin(a) * 11), i + k, Z, ZC, jag=1.2)
    elif name == 'idle7':
        a = min(1, (i - 3) / 2, (13 - i) / 2)
        if a > 0:
            cx, cy = sk.head[0] + 1, sk.head[1] - 20
            for (dx, dy, r) in ((-6, 1, 4.0), (0, -2, 5.0), (6, 1, 4.0), (0, 2, 4.5)):
                disk(c, cx + dx, cy + dy, r * min(1, a + .2), (96, 104, 130), rim=(60, 66, 90))
            disk(c, cx, cy - 1, 3.0 * a, (150, 160, 188))
            if i >= 6 and i <= 11:
                for k in range(3):
                    put(c, cx - 5 + k * 5 + (i % 2), cy + 7 + ((i * 2 + k * 3) % 18), Z)
                if i % 3 == 0: bolt(c, (cx, cy + 5), (cx + 1, cy + 22), i, Z, ZC, jag=1.5)
    elif name == 'idle8':
        if 2 <= i <= 4:
            bolt(c, (sk.head[0] + 10, -72), (sk.handB[0] + 2, sk.handB[1] - 2), i, Z, ZC, jag=3)
        if 5 <= i <= 10:
            h = sk.handB
            cx, cy = h[0] + 3, h[1] - 4
            orb(c, cx, cy, 2.4, ZC, Z)
            for k in range(3):
                a = i * 1.7 + k * 2.1
                put(c, cx + math.cos(a) * 4, cy + math.sin(a) * 4, Z)
        if i in (10, 11):
            star4(c, sk.handB[0] + 4, sk.handB[1] - 5, Z, ZC)
    elif name == 'idle9':
        # la Z
        zs = [(2.8, 4.2, ((-9, -2), (9, -2))), (5.0, 5.6, ((9, -2), (-9, 10))), (6.9, 7.8, ((-9, 10), (9, 10)))]
        for (a0, a1, (p0, p1)) in zs:
            if i >= a0:
                t = min(1, (i - a0) / (a1 - a0))
                x0, y0 = sk.head[0] + 14 + p0[0], -60 + p0[1]
                x1, y1 = sk.head[0] + 14 + p1[0], -60 + p1[1]
                seg(c, x0, y0, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, ZC if i < a1 + 1 else Z)
        if 3 <= i <= 8:
            star4(c, *tip(c, 30), Z, ZC)
    elif name == 'idle10':
        for dx, side in ((sk.ankF, 1), (sk.ankB, -1)):
            if (i + (side > 0)) % 2 == 0:
                dust(c, dx[0], dx[1], (150, 190, 210), t=(i % 3) * .3)
        if i % 2 == 0:
            put(c, sk.head[0] - 8, sk.head[1] + 4, Z); put(c, sk.head[0] - 11, sk.head[1] + 6, ZC)


# ---------------------------------------------------------------- frost
I1 = (128, 228, 255); I2 = (210, 245, 255); I3 = (70, 140, 220)


def snowman(c, x, y, s):
    disk(c, x, y - 3.2 * s, 3.4 * s, (240, 246, 255), rim=(150, 190, 235))
    disk(c, x, y - 8.2 * s, 2.6 * s, (240, 246, 255), rim=(150, 190, 235))
    if s > .7:
        put(c, x - 1, y - 8.8 * s, (30, 40, 70)); put(c, x + 1, y - 8.8 * s, (30, 40, 70))
        put(c, x + 2.4, y - 8 * s, (255, 130, 40)); put(c, x + 3.4, y - 7.6 * s, (255, 130, 40))
        put(c, x, y - 3.4 * s, (40, 40, 60)); put(c, x, y - 5 * s, (40, 40, 60))
        for k in range(-2, 3): put(c, x + k, y - 11 * s, (50, 60, 120)) if abs(k) < 2 else None
        put(c, x, y - 12 * s, (50, 60, 120))


def f_frost(c, name):
    i, sk = c.i, c.sk
    if name == 'idle5':
        if i >= 4:
            s = min(1.0, (i - 3) / 5)
            x = 30
            snowman(c, x, 0, max(.4, s * 1.25))
            if i >= 10: star4(c, x + 3, -10, I2, (255, 255, 255))
        if 3 <= i <= 9: rise(c, [(30, -3)], 5, [I2, I1, I3], life=6, count=3, speed=.6, spread=4, start=3)
    elif name == 'idle6':
        if 1 <= i <= 12:
            for r in (6, 11, 15):
                ring(c, 0, 0, r, (150, 215, 245)) if r == 6 + (i % 3) * 4 else None
            for d in (sk.ankF, sk.ankB):
                if i % 2 == 0: put(c, d[0] - 4, d[1], I2); put(c, d[0] - 6, d[1] + 1, I1)
            for k in range(-14, 15):
                if abs(k) % 3 == 0 or i % 2: put(c, k, 1, (150, 215, 245))
    elif name == 'idle7':
        if 5 <= i <= 9:
            hf = head_front(c)
            t = i - 5
            for k in range(9):
                a = -.5 + k / 8 * 1.4
                x, y = hf[0] + 2 + math.cos(a) * (3 + t * 3), hf[1] + math.sin(a) * (2 + t * 2.5) + t * .8 * (k % 3)
                put(c, x, y, I2)
                if k % 2 == 0: plus(c, x + 1, y + 1, I1)
        if 2 <= i <= 4:
            put(c, sk.head[0] + 3, sk.head[1] - 7, (170, 200, 240))
    elif name == 'idle8':
        h = sk.handB
        if 3 <= i <= 11:
            bx = h[0] + 4 + (math.sin(i * .9) * 8 * max(0, 1 - (i - 3) / 3)) * (1 if i < 7 else 0)
            by = h[1] - 4 - max(0, 8 - (i - 3) * 3) if i < 7 else h[1] - 4
            if i < 8: butterfly(c, bx, by, (255, 150, 220), i)
            else: butterfly(c, bx, by, I2, 0, dk=I3)
            if i >= 8:
                star4(c, bx + 3, by - 3, I2, (255, 255, 255)) if i % 2 else None
        if i == 12: bird_ = None
    elif name == 'idle9':
        if 5 <= i <= 12:
            h = sk.handB
            L = (i - 4) * 3
            for k in range(L):
                put(c, h[0] + 3 + k * .9, 0 if True else 0, I1); put(c, h[0] + 3 + k * .9, 1, I3)
            if i % 2: put(c, h[0] + 3 + L * .9, -2, I2)
            if i >= 10: star4(c, h[0] + 3 + L * .9 * .5, -5, I2, (255, 255, 255))
    elif name == 'idle10':
        if i in (5, 6, 7) or i in (10, 11):
            zed(c, sk.head[0] + 6 + (i - 5) * 2, sk.head[1] - 6 - (i - 5) * 2, I2, 2 if i < 8 else 2)
        if i >= 7:
            put(c, sk.head[0] + 4, sk.head[1] + 3, I3)
        if i in (5, 6, 7, 8, 9, 10):
            for k in range(2): put(c, sk.head[0] + 3, sk.head[1] + 4 + (i - 5) * .8 + k, (150, 205, 255)) if i % 2 else None
        if i == 6 or i == 11:
            put(c, sk.head[0] + 9, sk.head[1] - 14, I2)


# ---------------------------------------------------------------- verdant
G1 = (138, 222, 100); G2 = (72, 166, 68); G3 = (36, 108, 50); BR = (120, 80, 44)


def f_verdant(c, name):
    i, sk = c.i, c.sk
    if name == 'idle5':
        h = sk.handB
        x = h[0] + 5
        if 3 <= i <= 4: put(c, x, 0, BR); put(c, x + 1, 0, BR)
        if 5 <= i <= 7:
            for k in range(4):
                put(c, x - 1 + k * .8, h[1] + 1 + (i - 5) * 2 + k, (120, 200, 255)); 
            put(c, x, -1, (90, 60, 40))
        if i >= 7:
            hgt = int(min(10, 2 + (i - 7) * 1.6))
            flower(c, x, 0, hgt, (255, 130, 180) if i >= 11 else G1, (255, 230, 120) if i >= 11 else G2)
            if i < 11:
                leaf(c, x - 2, -hgt // 2, G1, G3)
    elif name == 'idle6':
        t = tip(c, 30)
        if 3 <= i <= 12:
            by = t[1] - 8 - (4 - abs(i - 6)) * 1.2 if i < 5 else t[1] - 2
            bx = t[0] + 2 - (4 - i) * 3 if i < 5 else t[0] - 2
            if i >= 12: by = t[1] - 4 - (i - 12) * 4; bx = t[0] + (i - 11) * 3
            butterfly(c, bx, by, (255, 190, 60), i, dk=(70, 40, 20))
        if 5 <= i <= 10 and i % 2 == 0:
            star4(c, t[0] - 4, t[1] - 5, G1)
    elif name == 'idle7':
        if 4 <= i <= 12:
            t = min(1, (i - 3.5) / 5)
            for k, (dx, c1) in enumerate(((-16, (255, 130, 180)), (-8, (255, 230, 90)), (6, (255, 255, 255)), (14, (180, 130, 255)), (22, (255, 130, 180)))):
                flower(c, sk.handB[0] + dx + 4, 0, int(1 + t * (5 + k % 3)), c1, (255, 220, 90))
            rise(c, [(sk.handB[0] + 4, -2)], 8, [G1, G2], life=6, count=3, speed=.8, spread=14, start=4)
    elif name == 'idle8':
        if 3 <= i <= 11:
            cx = sk.head[0] + 12; cy = -62
            disk(c, cx, cy, 2.6, (255, 240, 130), rim=(255, 200, 60))
            for k in range(8):
                a = k / 8 * 2 * math.pi + i * .15
                put(c, cx + math.cos(a) * 5.5, cy + math.sin(a) * 5.5, (255, 220, 90))
            rise(c, [(sk.shF[0] + 2, sk.shF[1]), (sk.shB[0] - 2, sk.shB[1]) if hasattr(sk, 'shB') else (sk.shF[0] - 6, sk.shF[1])], 3, [(220, 255, 170), G1, G2], life=8, count=4, speed=1.2, spread=4, start=3)
        if i >= 5:
            for k in range(3):
                leaf(c, sk.handB[0] + 2 - k * 3, sk.handB[1] - 2 + k, G1, G3) if i % 3 == k else None
    elif name == 'idle9':
        h = sk.handB
        if 3 <= i <= 12:
            bx, by = (h[0] + 14 - (i - 2) * 2.5, h[1] - 14 + (i - 2) * 1.6) if i < 6 else (h[0] + 4, h[1] - 4) if i < 11 else (h[0] + 4 + (i - 10) * 5, h[1] - 6 - (i - 10) * 6)
            bird(c, bx, by, i, fly=(i < 6 or i >= 11))
        if 7 <= i <= 10 and i % 2:
            note(c, h[0] + 8, h[1] - 12 - (i - 7), (255, 240, 130))
    elif name == 'idle10':
        if 5 <= i <= 9:
            hf = head_front(c); t = i - 5
            for k in range(7):
                x = hf[0] + 2 + t * 2.2 + rnd(k, i) * 4; y = hf[1] - 2 + (rnd(k, i, 2) - .5) * 6 + t * .5
                plus(c, x, y, (255, 235, 100)) if k % 3 == 0 else put(c, x, y, (255, 250, 190))
        if 3 <= i <= 4:
            put(c, sk.head[0] + 3, sk.head[1] - 7, (255, 235, 100))
        if i >= 9:
            dots(c, [(sk.head[0] + 10 + k * 2, sk.head[1] - 8 - (i - 9) * 2 + (k % 2) * 3) for k in range(3)], (255, 245, 170))


# ---------------------------------------------------------------- blood
R1 = (255, 106, 124); R2 = (200, 30, 50); R3 = (120, 12, 36)


def f_blood(c, name):
    i, sk = c.i, c.sk
    if name == 'idle5':
        if 2 <= i <= 13:
            t = tip(c, 30)
            for j in range(5):
                ii = i - j
                if ii < 1: break
                p = c.cls.blade_pts(c.seq.at(ii), [(30, 0)])[0]
                put(c, p[0], p[1], (R1, R2, R2, R3, R3)[j])
        if i % 4 == 1:
            star4(c, sk.head[0] - 8, sk.head[1] - 6 - (i % 3), R1)
    elif name == 'idle6':
        t = tip(c, 30)
        if 4 <= i <= 12:
            for d in range(2):
                k = (i * 1.3 + d * 2.0) % 5
                put(c, t[0] - 1 + d, t[1] + 2 + k * 3, R2); put(c, t[0] - 1 + d, t[1] + 3 + k * 3, R1)
            put(c, t[0], 1, R2) if i % 2 else None
        if 4 <= i <= 12 and i % 2 == 0:
            put(c, sk.handB[0] + 6, sk.handB[1] - 3 + (i % 4), (255, 255, 255))
    elif name == 'idle7':
        if i in (7, 8):
            bang(c, sk.head[0] + 1, sk.head[1] - 9, R1)
        if 4 <= i <= 6 or 11 <= i <= 12:
            h = sk.handB; star4(c, h[0] + 4, h[1] - 3, (255, 255, 255)) if i % 2 == 0 else None
        if 4 <= i <= 12:
            put(c, sk.head[0] + 4 + i % 2, sk.head[1] + 4, (230, 230, 240))
    elif name == 'idle8':
        if 3 <= i <= 11:
            cx, cy = sk.handF[0] + 12, sk.handF[1] - 16
            for k in range(16):
                a = k / 16 * 2 * math.pi
                if k / 16 <= min(1, (i - 2.5) / 5):
                    put(c, cx + math.cos(a) * 10, cy + math.sin(a) * 10, R2)
            for k in range(3):
                a = k / 3 * 2 * math.pi + math.pi / 2
                pts = [(cx + math.cos(a + 2 * math.pi * j / 3) * 10, cy + math.sin(a + 2 * math.pi * j / 3) * 10) for j in range(3)] if k == 0 else []
            if i >= 7:
                for j in range(3):
                    a1 = j / 3 * 2 * math.pi + math.pi / 2; a2 = (j + 1) / 3 * 2 * math.pi + math.pi / 2
                    seg(c, cx + math.cos(a1) * 10, cy + math.sin(a1) * 10, cx + math.cos(a2) * 10, cy + math.sin(a2) * 10, R1)
            if i >= 10: star4(c, cx, cy, R1, (255, 255, 255), size=2)
    elif name == 'idle9':
        if 3 <= i <= 9:
            hf = head_front(c)
            h = sk.handB
            if i in (4, 7, 8): seg(c, hf[0] - 3, hf[1] + 5, hf[0] + 3, hf[1] + 5, (235, 235, 245))
        if i in (10, 11, 12):
            h = sk.handB
            star4(c, h[0] + 7, h[1] - 3, R1)
        if 4 <= i <= 9 and i % 2:
            put(c, sk.head[0] + 5, sk.head[1] - 1, (255, 255, 255))
    elif name == 'idle10':
        # mosca: zumbido en trayectoria
        if 2 <= i <= 12:
            fx = sk.head[0] + 6 + math.sin(i * 1.7) * 10 + (i - 2) * .5
            fy = sk.head[1] - 6 + math.cos(i * 2.3) * 7
            if i in (5, 10): fx, fy = tip(c, 28)[0], tip(c, 28)[1]
            put(c, fx, fy, (30, 20, 20)); put(c, fx - 1, fy - 1, (200, 210, 230)); put(c, fx + 1, fy - 1, (200, 210, 230))
            if i in (4, 5, 9, 10):
                seg(c, fx - 6, fy - 3, fx - 4, fy - 2, (170, 170, 180)); seg(c, fx + 4, fy - 3, fx + 6, fy - 4, (170, 170, 180))
        if i in (6, 11):
            star4(c, tip(c, 28)[0], tip(c, 28)[1], R1)
            put(c, tip(c, 28)[0] + 3, tip(c, 28)[1] + 3, (30, 20, 20))


# ---------------------------------------------------------------- earth
E1 = (255, 210, 122); E2 = (170, 140, 90); E3 = (108, 102, 110)


def rock(c, x, y, r=2.2):
    disk(c, x, y, r, (140, 134, 130), rim=(80, 76, 84)); put(c, x - r * .4, y - r * .4, (200, 196, 190))


def f_earth(c, name):
    i, sk = c.i, c.sk
    if name == 'idle5':
        if 2 <= i <= 13:
            rock(c, 14 + 0, -1, 2.0)
        if i in (11, 12):
            bang(c, sk.head[0] + 1, sk.head[1] - 9, E1) if i == 11 else star4(c, sk.head[0] + 3, sk.head[1] - 9, E1)
        if 3 <= i <= 8 and i % 2: put(c, sk.head[0] - 3, sk.head[1] - 7, (200, 190, 180))
        if 4 <= i <= 10:
            put(c, sk.head[0] + 4, sk.head[1] - 7 - (i % 2), (255, 255, 255)) if False else None
        if i in (9, 10, 11):
            put(c, sk.head[0] + 6, sk.head[1] - 11, E1); put(c, sk.head[0] + 6, sk.head[1] - 10, E1); put(c, sk.head[0] + 6, sk.head[1] - 8, E1)   # ?
    elif name == 'idle6':
        h = sk.handB
        if i <= 4: rock(c, 15, -2, 2.4)
        elif i in (5, 6, 7, 8):
            y = -8 - (i - 5) * 9 + ((i - 5) ** 2) * 1.2
            rock(c, h[0] + 3, y, 2.6)
        elif i >= 9: rock(c, h[0] + 3, h[1] - 3, 2.6)
        if i in (3, 4):
            dust(c, 14, 0, (170, 150, 120), t=1)
        if i in (9, 10): clink(c, h[0] + 6, h[1] - 6, E1)
    elif name == 'idle7':
        if i in (3, 5):
            dust(c, 4, -20, (200, 190, 170), t=1)
            ring(c, sk.shF[0] + 4, sk.shF[1] + 4, 4, E1)
        if 7 <= i <= 10:
            hf = head_front(c)
            seg(c, hf[0] + 1, hf[1] + 2, hf[0] + 4, hf[1] + 4, (40, 20, 20))
            for k in range(4): put(c, hf[0] + 8 + k * 2, hf[1] - 2 + (k % 2) * 3 - (i % 2), E1)
            ring(c, 0, -20, 12 + (i - 7) * 3, (255, 230, 170))
    elif name == 'idle8':
        h = sk.handB
        x = 16
        n_ = [0, 0, 1, 1, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3][i]
        for k in range(n_):
            rock(c, x + (k % 2 - .5) * (.8 if i > 7 else .4 * k), -2 - k * 3.6, 2.8 - k * .5)
        if i in (6, 8): star4(c, x + 6, -10, E1)
        if i >= 11 and i <= 12: clink(c, x + 6, -14, (255, 255, 255))
    elif name == 'idle9':
        if 4 <= i <= 10:
            for r in (4, 9, 14):
                rr = r + (i * 2) % 8
                ring(c, sk.handB[0] + 3, 1, rr, (150, 130, 100))
            if i % 2: put(c, 22 + i % 3, -1 - i % 2, E2)
        if i in (4, 7, 10):
            dust(c, sk.handB[0] + 3, 0, (150, 130, 100), t=1)
        if i in (11, 12): bang(c, sk.head[0] + 1, sk.head[1] - 9, E1)
    elif name == 'idle10':
        if i in (4, 5):
            dust(c, sk.ankF[0] + 4, sk.ankF[1], (170, 150, 120), t=i - 4); ring(c, 0, 1, 6 + (i - 4) * 5, E2)
        if 5 <= i <= 8:
            y = -66 + (i - 5) * 21
            if i < 8: rock(c, sk.head[0] + 1, y, 3.0)
        if i >= 8 and i <= 11:
            for k in range(3):
                a = k / 3 * 2 * math.pi + i * 1.1
                star4(c, sk.head[0] + math.cos(a) * 6, sk.head[1] - 9 + math.sin(a) * 2, (255, 230, 90))
        if i == 8: rock(c, sk.head[0] + 6, sk.head[1] + 12, 2.0)


# ---------------------------------------------------------------- astral
A1 = (255, 79, 208); A2 = (255, 170, 240); A3 = (130, 90, 255)


def f_astral(c, name):
    i, sk = c.i, c.sk
    if name == 'idle5':
        h = sk.handB
        if 3 <= i <= 12:
            cx, cy = h[0] + 5, h[1] - 6
            disk(c, cx, cy, 1.8, (255, 220, 120), rim=(255, 170, 60))
            for k, (r, col, sp) in enumerate(((5, A1, .9), (8, A3, .6), (11, (120, 220, 255), .4))):
                a = i * sp + k * 2
                orb(c, cx + math.cos(a) * r, cy + math.sin(a) * r * .5, 1.0 + (k == 1) * .4, col, col)
                ring(c, cx, cy, r, (60, 40, 110)) if False else None
            for k, r in enumerate((5, 8, 11)):
                for q in range(0, 20, 4): put(c, cx + math.cos(q / 20 * 6.28) * r, cy + math.sin(q / 20 * 6.28) * r * .5, (80, 60, 140))
    elif name == 'idle6':
        h = sk.handB
        if 2 <= i <= 5:
            x = sk.head[0] + 22 - (i - 2) * 9; y = -70 + (i - 2) * 10
            for k in range(7): put(c, x + k * 1.4, y - k * .9, A2 if k < 3 else A3)
            star4(c, x, y, A2, (255, 255, 255), size=2)
        if 6 <= i <= 11:
            star4(c, h[0] + 4, h[1] - 4, A2, (255, 255, 255), size=2 if i % 2 else 1)
            for k in range(4):
                a = i * 1.3 + k * 1.57; put(c, h[0] + 4 + math.cos(a) * 5, h[1] - 4 + math.sin(a) * 4, A1)
    elif name == 'idle7':
        if 4 <= i <= 10:
            hf = head_front(c)
            for k in range(8):
                x = hf[0] + 10 + k * 3 + rnd(k, i) * 2; y = hf[1] - 10 - k * 3 + (rnd(k, i, 1) - .5) * 3
                if k % 3 == 0: star4(c, x, y, A2, (255, 255, 255)) if i % 2 == k % 2 else put(c, x, y, A2)
                else: put(c, x, y, A3)
        if 3 <= i <= 4 and False: pass
    elif name == 'idle8':
        al = {4: .6, 5: .2, 6: 0, 7: .3, 8: .8, 10: .6, 11: .1, 12: .3, 13: .8}
        a = al.get(i, 1.0)
        if i in (5, 7, 11): ring(c, sk.head[0], -15, 7 + (i % 3) * 3, A1)
        if a < 1: fade(c, a)
        if 5 <= i <= 7 or 11 <= i <= 12:
            for k in range(8):
                ang = k / 8 * 2 * math.pi + i; put(c, sk.head[0] + math.cos(ang) * (5 + (i % 3) * 2), -16 + math.sin(ang) * 9, A2 if k % 2 else A1)
            star4(c, sk.head[0], -16, A2, (255, 255, 255), size=2)
    elif name == 'idle9':
        if 3 <= i <= 12:
            h = sk.handB
            cx, cy = h[0] + 14, -26
            t = min(1, (i - 2.5) / 4)
            for k in range(24):
                if k / 24 <= t:
                    a = k / 24 * 2 * math.pi - math.pi / 2
                    put(c, cx + math.cos(a) * 10, cy + math.sin(a) * 13, A1 if k % 2 else A2)
            if i >= 7:
                for dy in range(-10, 11, 2):
                    w = int((1 - abs(dy) / 11) * 7)
                    for dx in range(-w, w + 1):
                        if (dx + dy + i) % 3 == 0: put(c, cx + dx, cy + dy * 1.1, A3)
            if i >= 10: star4(c, cx, cy, (255, 255, 255), A2, size=2)
    elif name == 'idle10':
        if 3 <= i <= 10:
            for k in range(9):
                x = sk.head[0] + (rnd(k, 1) - .5) * 14; y = sk.head[1] - 8 + ((i * 1.8 + k * 3) % 26)
                put(c, x, y, A2 if k % 3 else (255, 255, 255)); 
                if k % 4 == 0: plus(c, x, y, A1)


# ---------------------------------------------------------------- steel
S1 = (255, 154, 60); S2 = (255, 220, 120); S3 = (150, 160, 180)


def f_steel(c, name):
    i, sk = c.i, c.sk
    if name == 'idle5':
        for d in ((sk.handF, 3, 7, 5), (sk.shF, 2, 6, 3)):
            pass
        if 2 <= i <= 11:
            p = sk.handF if i < 7 else sk.handB
            if i % 2 == 0:
                for k in range(5): put(c, sk.shF[0] + 3 + (rnd(i, k) - .5) * 6, sk.shF[1] + 6 + (rnd(i, k, 1) - .5) * 8, S2 if k % 2 else S1)
        if 3 <= i <= 9 and i % 3 == 0:
            drop = sk.shF; put(c, drop[0] + 2, drop[1] + 8 + (i % 3), (60, 60, 70)); put(c, drop[0] + 2, drop[1] + 9, (30, 30, 36))
        if i in (6, 7): clink(c, sk.handF[0] + 3, sk.handF[1] - 2, S2)
    elif name == 'idle6':
        if i in (3, 5):
            hf = head_front(c)
            for k in range(5):
                a = k / 5 * 2 * math.pi
                put(c, sk.head[0] + 2 + math.cos(a) * 6, sk.head[1] - 1 + math.sin(a) * 6, S2 if k % 2 else (255, 255, 255))
            star4(c, hf[0] + 2, hf[1] - 4, S2, (255, 255, 255), size=2)
        if 4 <= i <= 9:
            for k in range(2): put(c, sk.head[0] + 1 + k * 3, sk.head[1] - 1 + (i % 2) * 2, (60, 255, 140) if i % 2 else (255, 80, 60))
        if 6 <= i <= 8:
            for k in range(6): put(c, sk.head[0] - 8 + k * 3, sk.head[1] - 14 + (k * i) % 3, (200, 210, 220) if (k + i) % 2 else (90, 100, 110))
    elif name == 'idle7':
        if 4 <= i <= 9:
            s = sk.shF
            if i % 2 == 0: star4(c, s[0] + 5, s[1] + 2, (255, 255, 255), S2, size=2)
            else: star4(c, s[0] + 8, s[1] - 3, S2, (255, 255, 255))
            for k in range(3): put(c, s[0] + 3 + k * 3, s[1] - 6 - ((i + k) % 2), S2)
        if i in (4, 8): bang(c, sk.head[0] + 1, sk.head[1] - 9, S1)
    elif name == 'idle8':
        if i in (2, 3, 5, 6, 8, 9, 11, 12):
            pass
        if i in (3, 6, 9, 12):
            put(c, sk.head[0] + 6, sk.head[1] - 9, S3); put(c, sk.head[0] + 6, sk.head[1] - 10, S3)
            note(c, sk.head[0] + 8, sk.head[1] - 12, S2) if False else None
        if 2 <= i <= 12:
            hf = head_front(c)
            put(c, hf[0] + 2, hf[1] - 1, (60, 255, 140) if (i // 3) % 2 == 0 else (255, 180, 60))
        if i in (2, 5, 8, 11):
            put(c, sk.head[0] + 9, sk.head[1] - 12, S2); put(c, sk.head[0] + 10, sk.head[1] - 12, S2)
    elif name == 'idle9':
        if 4 <= i <= 12:
            p = blade(c, [10 + (i - 4) * 2.5])[0]
            if i % 2 == 0: star4(c, p[0], p[1] - 1, (255, 255, 255), (255, 240, 180), size=2)
            for k in range(8): put(c, p[0] + (rnd(i, k) - .5) * 10, p[1] - 2 + rnd(i, k, 1) * 8, S2 if k % 2 else S1)
            rise(c, [(p[0], p[1])], 9, [S2, S1, (170, 60, 20)], life=5, count=2, speed=1.2, spread=3, start=4)
        if i == 12: put(c, sk.head[0] + 5, sk.head[1] - 9, (200, 200, 210))
    elif name == 'idle10':
        k = [0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 4, 4][i]
        if i in (3, 6, 9, 12):
            star4(c, sk.head[0] + 8, sk.head[1] - 6, S2, (255, 255, 255))
        if i % 3 == 0:
            put(c, sk.ankF[0] - 4, sk.ankF[1] - 1, (140, 140, 150)); put(c, sk.ankB[0] + 3, sk.ankB[1] - 1, (140, 140, 150))
        if 3 <= i <= 12:
            for j in range(2): put(c, sk.head[0] - 7 + j * 2, sk.head[1] - 6 + (i % 2) * (-2), (60, 255, 140) if (i + j) % 2 else (255, 80, 60))


FN2 = dict(paladin=f_paladin, shadow=f_shadow, flame=f_flame, storm=f_storm, frost=f_frost, verdant=f_verdant, blood=f_blood,
           earth=f_earth, astral=f_astral, steel=f_steel)
