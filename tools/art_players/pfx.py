"""Particulas de pixel-art nitido: se estampan sobre el fotograma ya reducido (sin suavizado) en las animaciones de
personalidad. Coordenadas de mundo con el pivote en (0,0) y y negativa hacia arriba; pixel = XPIVOT + (x, y)."""
import math
import numpy as np
from rig import skeleton
import anims as AN

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16.0


def hexc(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rnd(*a):
    h = 2166136261
    for v in a:
        h = ((h ^ (int(v) & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 0x5bd1e995) & 0xFFFFFFFF
    h ^= h >> 15
    return (h & 0xFFFF) / 65535.0


class C:     # contexto de un fotograma
    pass


def put(c, x, y, col, a=255):
    px, py = int(round(AN.XPIVOT[0] + x)), int(round(AN.XPIVOT[1] + y))
    H, W = c.f.shape[:2]
    if 0 <= px < W and 0 <= py < H:
        c.f[py, px, :3] = col
        c.f[py, px, 3] = max(int(c.f[py, px, 3]), a) if a < 255 else 255


def disk(c, x, y, r, col, rim=None):
    R = int(math.ceil(r))
    for dy in range(-R, R + 1):
        for dx in range(-R, R + 1):
            d = math.hypot(dx, dy)
            if d <= r:
                put(c, x + dx, y + dy, rim if (rim and d > r - 1.0) else col)


def plus(c, x, y, col, big=False):
    put(c, x, y, col)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        put(c, x + dx, y + dy, col)
    if big:
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            put(c, x + dx, y + dy, col)


def star4(c, x, y, col, core=(255, 255, 255), size=1):
    plus(c, x, y, col, big=size > 1)
    put(c, x, y, core)


def seg(c, x0, y0, x1, y1, col):
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for k in range(n + 1):
        t = k / max(1, n)
        put(c, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, col)


def bolt(c, p0, p1, seed, col, core=(255, 255, 255), jag=2.2):
    top = -AN.XPIVOT[1] + 3
    p0 = (p0[0], max(top, p0[1]))
    p1 = (p1[0], max(top, p1[1]))
    pts = [p0]
    n = 5
    for k in range(1, n):
        t = k / n
        pts.append((p0[0] + (p1[0] - p0[0]) * t + (rnd(seed, k) - .5) * 2 * jag, p0[1] + (p1[1] - p0[1]) * t + (rnd(seed, k, 9) - .5) * jag))
    pts.append(p1)
    for a, b in zip(pts, pts[1:]):
        seg(c, a[0], a[1], b[0], b[1], col)
    for a, b in zip(pts[::2], pts[1::2]):
        put(c, (a[0] + b[0]) / 2, (a[1] + b[1]) / 2, core)


def rise(c, pts, seed, cols, life=7, count=4, speed=1.6, spread=2.0, drift=0.0, start=0, grav=0.0):
    """Particulas que nacen en puntos, suben y se apagan. Determinista por (fotograma, semilla)."""
    for j in range(count):
        for age in range(life):
            birth = c.i - age
            if birth < start:
                continue
            if rnd(seed, j, birth) > 0.55:
                continue
            p = pts[int(rnd(seed, j, birth, 3) * len(pts)) % len(pts)]
            x = p[0] + (rnd(seed, j, birth, 1) - .5) * 2 * spread + drift * age
            y = p[1] - speed * age + grav * age * age
            col = cols[min(len(cols) - 1, int(age / life * len(cols)))]
            put(c, x, y, col)
            break


def bang(c, x, y, col=(255, 230, 90)):
    for k in range(5):
        put(c, x, y - 4 + k, col)
        put(c, x + 1, y - 4 + k, col)
    put(c, x, y + 2, col)
    put(c, x + 1, y + 2, col)


def sweat(c, x, y, k):
    col = (170, 225, 255)
    put(c, x, y + k, col)
    put(c, x, y + k + 1, (235, 250, 255))
    put(c, x - 1, y + k + 1, col)
    put(c, x + 1, y + k + 1, col)


def ring(c, x, y, r, col, a=255):
    for k in range(20):
        t = k / 20 * 2 * math.pi
        put(c, x + math.cos(t) * r, y + math.sin(t) * r * .55, col)


def crystal(c, x, y, h, cols):
    """cristal vertical: base en (x, y), altura h."""
    w = max(1, int(h * .28))
    for k in range(int(h)):
        t = k / max(1, h - 1)
        ww = w * (1 - abs(t * 2 - 1)) if t > .3 else w * t / .3
        for dx in range(-int(ww), int(ww) + 1):
            put(c, x + dx, y - k, cols[0] if dx < 0 else cols[1] if dx == 0 else cols[2])
    put(c, x, y - h + 1, (255, 255, 255))


def leaf(c, x, y, col, dk):
    put(c, x, y, col)
    put(c, x + 1, y, col)
    put(c, x, y + 1, dk)


def flower(c, x, y, h, petal, core, stem=(60, 150, 70)):
    for k in range(int(h)):
        put(c, x, y - k, stem)
    if h >= 3:
        put(c, x + 1, y - int(h * .5), stem)
        put(c, x + 2, y - int(h * .5) - 1, stem)
    top = y - int(h)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        put(c, x + dx, top + dy, petal)
    put(c, x, top, core)


def fade(c, alpha):
    """Desvanecer con trama ordenada (sin semitransparencias): alpha 1 = opaco."""
    H, W = c.f.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    keep = alpha > BAYER[yy % 4, xx % 4]
    c.f[..., 3] = np.where(keep, c.f[..., 3], 0)


def shake_px(c, dx, dy=0):
    c.f[:] = np.roll(c.f, (dy, dx), axis=(0, 1))


# ------------------------------------------------------------------ puntos utiles
def tip(c, L=30):
    return c.cls.blade_pts(c.p, [(L, 0)])[0]


def blade(c, xs):
    return c.cls.blade_pts(c.p, [(x, 0) for x in xs])


def head_front(c):
    s = c.sk
    return (s.head[0] + s.hf[0] * 4, s.head[1] + s.hf[1] * 4)


def foot_pts(c):
    return [(c.sk.ankF[0], c.sk.ankF[1]), (c.sk.ankB[0], c.sk.ankB[1])]


def ph(c, a, b):
    """progreso 0..1 del fotograma dentro de [a, b]."""
    return max(0.0, min(1.0, (c.i - a) / max(1e-6, b - a)))


def dust(c, x, y, col=(200, 190, 180), t=0):
    for dx in (-3, -2, 2, 3):
        put(c, x + dx * (1 + t * .6), y - 1 - t * (1 if abs(dx) == 2 else .5), col)


# ================================================================== efectos por personaje
def f_paladin(c, name):
    i, sk = c.i, c.sk
    g, gl = (255, 210, 90), (255, 246, 200)
    if name == 'idle1':          # destellos recorriendo el filo mientras lo pule
        if 2 <= i <= 12:
            xs = blade(c, [4, 8, 12, 16, 19])
            k = (i * 2) % 5
            star4(c, xs[k][0], xs[k][1], g, gl, size=1)
        if i in (12, 13):
            t = tip(c, 20)
            star4(c, t[0], t[1], g, gl, size=2)
    elif name == 'idle2':        # chispas del escudo al golpearlo
        if i in (3, 4, 5, 6):
            h = sk.handB
            for d in ((3, -3), (5, 0), (3, 3)):
                put(c, h[0] + d[0] + (i - 3) * .6, h[1] + d[1], g)
            put(c, h[0] + 2, h[1], gl)
    elif name == 'idle3':        # plegaria: motas de luz suben
        if i >= 8:
            rise(c, [(sk.head[0] + k, sk.head[1] - 2) for k in (-3, 0, 3)], 1, [gl, g, (230, 160, 40)], life=8, count=3, speed=1.4, spread=3, start=8)
    elif name == 'idle4':        # suspiro: pequeña nube
        if i in (11, 12, 13):
            hf = head_front(c)
            for k in range(3):
                put(c, hf[0] + (i - 10) * 1.2 + k, hf[1] - 1 - (i - 11) * .5, (225, 225, 235))
    elif name == 'victory':
        if 4 <= i <= 12:
            t = (sk.head[0], sk.head[1] - 3)
            for k in range(8):
                a = k / 8 * 2 * math.pi + i * .3
                r = 7 + (i % 3)
                put(c, t[0] + math.cos(a) * r, t[1] + math.sin(a) * r * .8 - 6, g if k % 2 else gl)
            star4(c, *tip(c, 20), g, gl, size=2)
    elif name == 'awe':
        if 2 <= i <= 8:
            star4(c, *tip(c, 20), g, gl, size=2)


def f_shadow(c, name):
    i, sk = c.i, c.sk
    pu, dk = (176, 96, 255), (90, 30, 160)
    if name == 'idle1':          # estela de la daga lanzada
        if 4 <= i <= 8:
            t = tip(c, 12)
            for k in range(3):
                put(c, t[0] - (k + 1) * .5, t[1] + (k + 1) * 2, pu if k == 0 else dk)
    elif name == 'idle2':        # se desvanece a medias mirando la oscuridad
        a = 1.0
        if 5 <= i <= 12:
            a = 0.35 + 0.65 * abs(math.cos((i - 5) / 7 * math.pi * 1.5)) * 0.9
            a = max(0.3, min(1, a))
        fade(c, a)
        if 5 <= i <= 12:   # ojos en la oscuridad
            x = sk.head[0] - 22
            put(c, x, sk.head[1] - 3, (255, 70, 90)); put(c, x + 2, sk.head[1] - 3, (255, 70, 90))
            if i % 4 == 0:
                put(c, x, sk.head[1] - 3, dk); put(c, x + 2, sk.head[1] - 3, dk)
    elif name == 'idle3':        # chispas del roce de las dagas
        if 3 <= i <= 10 and i % 2 == 1:
            h = sk.handF
            for d in ((2, -2), (3, 1), (1, -4)):
                put(c, h[0] + d[0] + 2, h[1] + d[1], (255, 235, 180))
    elif name == 'idle4':        # destello de la daga al girar
        if i in (6, 8, 10):
            t = tip(c, 12)
            star4(c, t[0], t[1], pu, (255, 255, 255))
    elif name == 'victory':
        if i >= 6:
            fade(c, 1.0 if i % 5 else 0.7)
            rise(c, [(sk.hip[0] + k, -2) for k in (-6, -3, 0, 3, 6)], 2, [pu, dk, (50, 20, 90)], life=8, count=3, speed=1.0, spread=2, start=6)
    elif name == 'awe':
        if 1 <= i <= 3:
            for k in range(4):
                put(c, sk.hip[0] - 5 - k * 2, sk.hip[1] - 2 + (k % 2), dk)


def f_flame(c, name):
    i, sk = c.i, c.sk
    cols = [(255, 240, 160), (255, 192, 64), (255, 110, 30), (170, 40, 20)]
    if name == 'idle1':
        h = sk.handB
        if 3 <= i <= 11:
            r = [0.5, 1.2, 1.8, 2.2, 2.4, 2.6, 2.6, 2.7, 2.7][i - 3] if i - 3 < 9 else 2.7
            cx, cy = h[0] + 2.5, h[1] - 5 - (math.sin(i * 1.3) * .8)
            disk(c, cx, cy, r, (255, 150, 40), rim=(255, 90, 24))
            disk(c, cx, cy + .3, r * .55, (255, 235, 150))
            rise(c, [(cx, cy - r)], 3, cols, life=5, count=2, speed=1.3, spread=1.2, start=3)
        elif i in (12, 13, 14):
            k = i - 11
            cx, cy = h[0] + 2.5 + k * 1.2, h[1] - 5 - k * 6
            disk(c, cx, cy, max(.6, 2.6 - k * .7), (255, 150, 40), rim=(255, 90, 24))
            star4(c, cx, cy, (255, 220, 120)) if k == 2 else None
    elif name == 'idle2':
        if 3 <= i <= 11:
            pts = blade(c, [6, 12, 18, 24, 30])
            rise(c, pts, 4, cols, life=6, count=4, speed=1.8, spread=1.5, start=3)
        if i in (10, 11):
            t = tip(c, 32)
            star4(c, t[0], t[1], (255, 192, 64), (255, 245, 190), size=2)
    elif name == 'idle3':
        h = sk.handB
        if 3 <= i <= 9 and i % 2 == 0:
            for d in ((3, -2), (4, 1), (2, -4), (5, -3)):
                put(c, h[0] + d[0], h[1] + d[1], cols[(i + d[0]) % 3])
        if i >= 10:
            hf = head_front(c)
            for k in range(5):
                put(c, hf[0] + 1 + (i - 10) * 2 + k * .6, hf[1] + 2 - k * .6 + (rnd(i, k) - .5) * 2, cols[1 + k % 2])
    elif name == 'idle4':
        if i in (5, 8, 11, 12):
            ax, ay = sk.ankF if i in (5, 8) else sk.ankB
            dust(c, ax, ay, (110, 90, 80), t=(0 if i in (5, 8) else 1))
            for k in range(4):
                put(c, ax + (k - 1.5) * 2, ay - 2 - rnd(i, k) * 3, cols[1 + k % 2])
    elif name == 'chest':
        if i >= 4:
            for k in range(5):
                star4(c, 15 + (k - 2) * 3, -6 - (i - 4) * 1.6 - (k % 2) * 3, (255, 210, 90))
    elif name == 'victory':
        if 4 <= i <= 11:
            pts = blade(c, [4, 10, 16, 22, 28])
            rise(c, pts, 5, cols, life=8, count=5, speed=2.2, spread=3, start=4)
            rise(c, [(sk.head[0], sk.head[1] - 4)], 6, cols, life=7, count=3, speed=1.6, spread=5, start=4)
    elif name == 'awe':
        if 1 <= i <= 5:
            rise(c, [(sk.shF[0], sk.shF[1])], 7, cols, life=5, count=3, speed=1.5, spread=5, start=1)


def f_storm(c, name):
    i, sk = c.i, c.sk
    b, w = (77, 200, 255), (240, 252, 255)
    if name == 'idle1':          # arcos entre los dedos
        h = sk.handB
        if 4 <= i <= 12:
            for k in range(2):
                bolt(c, (h[0] + 1, h[1] - 1), (h[0] + 3 + (rnd(i, k) * 5), h[1] - 3 - (rnd(i, k, 2) * 5)), i * 3 + k, b, w, jag=1.4)
    elif name == 'idle2':        # destello del estoque en la estocada
        if i in (5, 6):
            t = tip(c, 30)
            star4(c, t[0], t[1], b, w, size=2)
            seg(c, t[0] - 8, t[1], t[0] - 2, t[1], w)
        if i in (9, 10):
            t = tip(c, 30)
            star4(c, t[0], t[1], b, w)
    elif name == 'idle3':        # chispitas al despegar
        if i in (3, 6, 9, 12):
            for ax, ay in foot_pts(c):
                put(c, ax, ay + 1, w)
                put(c, ax + 2, ay - 1, b)
    elif name == 'idle4':
        if i in (3, 4, 10, 11):
            bolt(c, (sk.head[0] - 1, sk.head[1] - 5), (sk.head[0] + 3 + rnd(i) * 3, sk.head[1] - 9), i, b, w, jag=1.2)
    elif name == 'victory':
        if 3 <= i <= 6:                      # el rayo cae sobre el estoque
            t = tip(c, 30)
            bolt(c, (t[0] + 1, t[1] - 28), t, i * 5, b, w, jag=3.2)
            bolt(c, (t[0] - 1, t[1] - 28), (t[0], t[1] + 2), i * 5 + 1, b, w, jag=2.6)
        if i >= 5:
            t = tip(c, 30)
            for k in range(4):
                put(c, t[0] + (rnd(i, k) - .5) * 10, t[1] + (rnd(i, k, 3) - .5) * 10, w if k % 2 else b)
            for k in range(3):
                bolt(c, (sk.hip[0], sk.hip[1] - 8), (sk.hip[0] + (rnd(i, k, 7) - .5) * 24, sk.hip[1] - 8 + (rnd(i, k, 8) - .5) * 20), i * 9 + k, b, w, jag=1.2)
    elif name == 'awe':
        if i <= 5:
            for k in range(3):
                bolt(c, (sk.shF[0], sk.shF[1] - 4), (sk.shF[0] + (rnd(i, k) - .5) * 16, sk.shF[1] - 4 + (rnd(i, k, 2) - .5) * 14), i * 7 + k, b, w, jag=1.2)


def f_frost(c, name):
    i, sk = c.i, c.sk
    ic = [(210, 245, 255), (128, 228, 255), (70, 150, 220)]
    if name == 'idle1':          # cristal que crece sobre la palma
        h = sk.handB
        if 4 <= i <= 12:
            hh = [2, 3, 5, 6, 7, 8, 8, 8, 6][i - 4] if i - 4 < 9 else 6
            crystal(c, h[0] + 1.5, h[1] - 2, hh, ic)
            if i % 2: put(c, h[0] + 5, h[1] - 6, (255, 255, 255))
        if i in (11, 12):
            star4(c, h[0] + 6, h[1] - 9, ic[1], (255, 255, 255))
    elif name == 'idle2':        # vaho de la respiracion y escalofrio
        hf = head_front(c)
        if i in (3, 5, 7, 9, 11):
            k = (i - 3) // 2
            for j in range(3):
                put(c, hf[0] + 1 + j + k * .6, hf[1] + 2 - k * .8 - j * .4, (225, 240, 250))
        if i % 2 == 0 and 3 <= i <= 11:
            put(c, sk.head[0] - 6, sk.head[1] + 3, ic[1])
    elif name == 'idle3':        # soplo de escarcha en el filo
        if 6 <= i <= 10:
            t = blade(c, [10, 16, 22])
            for k, q in enumerate(t):
                put(c, q[0], q[1] - 1 - (i - 6) * .6, ic[k % 3])
                put(c, q[0] + 1, q[1] - 2 - (i - 6) * .4, (255, 255, 255))
        if i in (11, 12):
            star4(c, *tip(c, 22), ic[1], (255, 255, 255))
    elif name == 'idle4':
        if i in (5, 7, 9, 11):
            ax, ay = sk.bfy if False else sk.ankB
            for k in range(3):
                put(c, ax + (k - 1) * 2, ay + 1, ic[k])
    elif name == 'victory':
        if i >= 5:                           # cristales emergen alrededor del sable clavado
            k = min(1.0, (i - 5) / 4)
            for dx, hh in ((-9, 7), (-5, 10), (10, 8), (14, 5), (-13, 4)):
                crystal(c, dx + 12, -1, max(2, int(hh * k)), ic)
            if i % 3 == 0:
                star4(c, 6 + (i % 5) * 3, -18 - (i % 4) * 2, ic[1], (255, 255, 255))
    elif name == 'awe':
        if 2 <= i <= 8:
            star4(c, sk.head[0] + 6, sk.head[1] - 6, ic[1], (255, 255, 255))
            star4(c, sk.head[0] - 6, sk.head[1] - 3, ic[0], (255, 255, 255))


def f_verdant(c, name):
    i, sk = c.i, c.sk
    gr, lt, dk = (79, 217, 106), (200, 255, 154), (40, 120, 60)
    if name == 'idle1':          # brota una flor frente a el
        if i >= 5:
            h = min(8, 2 + (i - 5) * 1.3)
            x = sk.handB[0] + 6
            flower(c, x, -1, h, (255, 130, 200) if i < 11 else (255, 190, 90), (255, 240, 120))
            if i in (9, 10):
                star4(c, x, -1 - h - 3, lt, (255, 255, 255))
    elif name == 'idle2':        # hojas que brotan de la espada
        if i >= 3:
            pts = blade(c, [6, 12, 18, 24, 30])
            for k, q in enumerate(pts):
                if i >= 3 + k:
                    leaf(c, q[0], q[1] - 2, gr if k % 2 else lt, dk)
            if i in (10, 11):
                star4(c, *tip(c, 30), lt, (255, 255, 255))
    elif name == 'idle3':        # hojitas caen al estirarse
        if 5 <= i <= 12:
            for k in range(3):
                x = sk.head[0] - 8 + k * 7
                y = sk.head[1] - 10 + (i - 5) * 2.4 + k * 2
                leaf(c, x + math.sin(i + k) * 2, y, gr, dk)
    elif name == 'idle4':        # ondas de sonido del bosque
        if 3 <= i <= 9:
            ring(c, sk.head[0] + 3, sk.head[1], 5 + (i - 3) * .9, lt)
    elif name == 'victory':
        if i >= 3:
            k = min(1.0, (i - 3) / 5)
            for dx, hh in ((-12, 5), (-8, 8), (12, 6), (16, 9), (-16, 4), (8, 3)):
                flower(c, dx + 4, -1, max(2, int(hh * k)), [(255, 130, 200), (255, 190, 90), (190, 150, 255)][dx % 3], (255, 240, 120))
            for j in range(4):
                a = (i * .5 + j * 1.6)
                leaf(c, math.cos(a) * 12, -20 + math.sin(a * 1.3) * 6 - (i % 5), gr, dk)
    elif name == 'awe':
        if 2 <= i <= 8:
            star4(c, sk.head[0] + 5, sk.head[1] - 8, lt, (255, 255, 255))


def f_blood(c, name):
    i, sk = c.i, c.sk
    r, lr = (196, 18, 44), (255, 106, 124)
    if name == 'idle1':          # estela roja al girar la guadaña
        if 3 <= i <= 11:
            for L in (22, 28):
                t = tip(c, L)
                put(c, t[0], t[1], lr)
                put(c, t[0] - 1, t[1] + 1, r)
    elif name == 'idle2':        # gota que cae del filo
        if 5 <= i <= 12:
            t = tip(c, 18)
            y = t[1] + 2 + (i - 5) * 3.2
            put(c, t[0], y, r); put(c, t[0], y + 1, lr)
            if y > -2:
                for dx in (-2, -1, 1, 2):
                    put(c, t[0] + dx, -1, r)
    elif name == 'idle3':        # aura siniestra
        if 3 <= i <= 11:
            rise(c, [(sk.head[0] - 3 + k, sk.head[1] - 3) for k in (0, 3, 6)], 8, [lr, r, (110, 8, 30)], life=6, count=3, speed=1.2, spread=2, start=3)
    elif name == 'idle4':        # chispa al golpetear el suelo
        if i in (4, 6, 8, 10):
            t = tip(c, 2) if False else (sk.handF[0] + 1, -1)
            put(c, t[0], t[1], lr); put(c, t[0] + 2, t[1], r)
    elif name == 'victory':
        if 4 <= i <= 11:
            for L in (20, 26, 32):
                t = tip(c, L)
                put(c, t[0], t[1], lr); put(c, t[0] - 1, t[1] + 1, r)
        if i >= 8:
            rise(c, [(sk.head[0], sk.head[1] - 2)], 9, [lr, r], life=5, count=3, speed=-1.2, spread=8, start=8)
    elif name == 'awe':
        if i >= 2:
            put(c, sk.head[0] + 3, sk.head[1] + 4 + (i - 2) * 1.3, r)


def f_earth(c, name):
    i, sk = c.i, c.sk
    st, sd = (180, 150, 110), (110, 85, 55)
    if name == 'idle1':
        if 5 <= i <= 8:
            hf = head_front(c)
            put(c, hf[0] + 1, hf[1] + 3, (40, 20, 20)); put(c, hf[0] + 2, hf[1] + 3, (40, 20, 20))
    elif name == 'idle2':        # polvo al flexionar
        if i in (4, 8):
            for dx in (-6, -4, 5, 7):
                put(c, dx, -2 - (i == 8), st)
    elif name == 'idle3':        # guijarro que cae al golpear
        if i >= 5:
            y = -26 + (i - 5) * 4.5
            if y < -1:
                disk(c, 6, y, 1.1, st, rim=sd)
            else:
                dust(c, 6, -1, st, t=(i - 8) * .4)
        if i in (5, 6):
            dust(c, sk.handF[0] + 2, -1, st, t=i - 5)
    elif name == 'idle4':
        if i in (5, 6, 11, 12):
            ax, ay = (sk.ankF if i < 9 else sk.ankB)
            dust(c, ax, ay, st, t=(i % 2))
            for dx in (-2, 1):
                disk(c, ax + dx * 3, ay - 3 - (i % 2) * 2, .8, sd)
    elif name == 'victory':
        if i in (3, 4, 5):
            for dx, hh in ((-10, 3), (-6, 2), (14, 3), (18, 2)):
                disk(c, dx + 4, -2 - (i - 3) * 3 - hh, 1.2, st, rim=sd)
            dust(c, -6, -1, st, t=i - 3); dust(c, 16, -1, st, t=i - 3)
        if i in (7, 10):
            dust(c, sk.hip[0], sk.hip[1] - 12, (160, 130, 90), t=0)
    elif name == 'awe':
        if i in (4, 5):
            dust(c, 4, -1, st, t=i - 4)


def f_astral(c, name):
    i, sk = c.i, c.sk
    pk, vi, wh = (255, 79, 208), (138, 108, 255), (255, 240, 255)
    if name == 'idle1':          # estrellas titilando en lo alto
        if 3 <= i <= 12:
            for k, (x, y) in enumerate(((-10, -42), (4, -48), (14, -40), (-2, -36), (20, -46))):
                if (i + k) % 3:
                    star4(c, sk.hip[0] + x, y + 6, pk if k % 2 else vi, wh)
    elif name == 'idle2':        # constelación: puntos unidos por lineas
        pts = [(12, -36), (20, -42), (26, -34), (18, -28), (24, -22)]
        k = max(0, min(len(pts) - 1, (i - 3) // 2))
        for j in range(k + 1):
            star4(c, pts[j][0], pts[j][1] + 4, pk if j % 2 else vi, wh)
            if j:
                seg(c, pts[j - 1][0], pts[j - 1][1] + 4, pts[j][0], pts[j][1] + 4, vi)
        if i >= 12:
            for j in range(len(pts)):
                if (i + j) % 2:
                    star4(c, pts[j][0], pts[j][1] + 4, pk, wh)
    elif name == 'idle3':        # polvo de estrellas bajo los pies
        if 3 <= i <= 12:
            rise(c, [(k, -1) for k in (-5, 0, 5)], 10, [wh, pk, vi], life=7, count=3, speed=-0.8, spread=3, start=3, grav=0.0)
    elif name == 'idle4':
        if i in (5, 6, 7, 8):
            put(c, sk.head[0] + 5 + (i - 5), sk.head[1] - 3, wh)
    elif name == 'victory':
        if i >= 3:
            for j in range(6):
                a = i * .45 + j / 6 * 2 * math.pi
                star4(c, math.cos(a) * 15, -26 + math.sin(a) * 6, pk if j % 2 else vi, wh)
            if i in (6, 7):
                star4(c, sk.hip[0], -42, pk, wh, size=2)
    elif name == 'awe':
        if 2 <= i <= 9:
            for j in range(4):
                star4(c, math.cos(i * .8 + j * 1.6) * 11, -26 + math.sin(i * .8 + j * 1.6) * 9, pk if j % 2 else vi, wh)


def f_steel(c, name):
    i, sk = c.i, c.sk
    o, s = (255, 154, 60), (201, 212, 232)
    if name == 'idle1':          # destellos metalicos al ajustar
        if i in (4, 6, 8, 10):
            put(c, sk.shF[0] + 2, sk.shF[1] - 3, (255, 255, 255)); put(c, sk.shF[0] + 3, sk.shF[1] - 4, s)
    elif name == 'idle2':
        if i in (6, 7):
            star4(c, sk.head[0] + 2, sk.head[1] - 4, s, (255, 255, 255))
    elif name == 'idle3':        # destello del saludo
        if i in (5, 6):
            star4(c, *tip(c, 24), o, (255, 245, 210), size=2)
        if 5 <= i <= 7:
            seg(c, tip(c, 12)[0], tip(c, 12)[1], tip(c, 26)[0], tip(c, 26)[1], (255, 255, 255))
    elif name == 'idle4':
        if i in (5, 7, 9, 11):
            ax, ay = sk.ankF
            put(c, ax + 3, ay, s); put(c, ax + 4, ay - 1, (255, 255, 255))
    elif name == 'victory':
        if i >= 5:
            star4(c, *tip(c, 24), o, (255, 245, 210), size=2)
            for j in range(4):
                if (i + j) % 2:
                    q = tip(c, 8 + j * 6)
                    put(c, q[0] + 2, q[1], (255, 255, 255))
    elif name == 'awe':
        if i in (2, 3, 4):
            put(c, sk.head[0] + 2, sk.head[1] - 6 - (i - 2), o)


FN = dict(paladin=f_paladin, shadow=f_shadow, flame=f_flame, storm=f_storm, frost=f_frost, verdant=f_verdant, blood=f_blood,
          earth=f_earth, astral=f_astral, steel=f_steel)

# colores de ambiente genericos (cofre / contacto) por clase
TINT = dict(paladin=(255, 210, 90), shadow=(176, 96, 255), flame=(255, 150, 40), storm=(77, 200, 255), frost=(128, 228, 255),
            verdant=(79, 217, 106), blood=(255, 106, 124), earth=(255, 210, 122), astral=(255, 79, 208), steel=(255, 154, 60))


def generic(c, name):
    i, sk = c.i, c.sk
    tc = TINT[c.cls.id]
    if name == 'chest' and c.cls.id != 'flame':
        if i >= 4:                          # destello de tesoro
            for k in range(4):
                star4(c, 15 + (k - 1.5) * 3.2, -5 - (i - 4) * 1.5 - (k % 2) * 3, (255, 214, 96), (255, 250, 220))
    if name == 'touch':
        if 2 <= i <= 5:
            h = sk.handB if c.cls.id not in ('shadow', 'flame', 'blood', 'earth', 'steel') else sk.handB
            ring(c, h[0] + 6, h[1], 3 + (i - 2) * 2, tc)
    if name == 'awe' and c.cls.id not in ('shadow', 'steel', 'blood'):
        if 1 <= i <= 6:
            bang(c, sk.head[0] + 1, sk.head[1] - 8 - (1 if i % 2 else 0))
    if name == 'awe' and c.cls.id == 'shadow':
        if 1 <= i <= 4:
            bang(c, sk.head[0] + 1, sk.head[1] - 8)
    if name == 'weary':
        k = (i % 6)
        sweat(c, sk.head[0] - 4, sk.head[1] - 2, k)
        if i % 3 == 0:
            put(c, sk.head[0] + 5, sk.head[1] + 4, (225, 225, 235))


def post(cls, name, i, n, f, seq):
    c = C()
    c.cls, c.i, c.n, c.f = cls, i, n, f.copy()
    c.p = seq.at(i)
    c.sk = skeleton(c.p, cls.D)
    FN[cls.id](c, name)
    generic(c, name)
    return c.f
