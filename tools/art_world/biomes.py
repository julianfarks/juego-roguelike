"""Configuracion de cada bioma: paletas, terreno, ganchos de detalle."""
import numpy as np
from kit import *
from terrain import walk_crack, blob_mask

BIOMES = ['catacumbas', 'forja', 'helado', 'vacio', 'bosque', 'tormenta', 'sangre', 'eclipse', 'cazador']


def setpx(img, mask, col):
    img[mask] = col


def darker(img, mask, k):
    img[mask] = np.clip(img[mask] * k, 0, 255)


def nearest_idx(R, c):
    return int(np.argmin(np.abs(R - c).sum(1)))


# ------------------------------------------------------------------ catacumbas
def det_cata(cfg, v, H, T, aux, img, idx):
    R, A = cfg['stone'], cfg['acc']
    d = aux
    r = rng(100 + v * 7)
    if v >= 0:
        for _ in range(2 if v == 2 else 1):
            c = walk_crack(r, r.randint(3, 12), r.randint(2, 9), r.randint(5, 9), wobble=.8)
            c &= d > 0
            img[c] = R[0] * .9
            # reborde claro bajo la grieta
            c2 = np.roll(c, 1, 0) & ~c & (d > 0)
            img[c2] = np.clip(img[c2] * 1.25, 0, 255)
    if v == 99:
        bone = ramp('#3a3c48', '#6a6e78', '#9a9c98', '#c2c0b0')
        pts = {(5, 3): 3, (6, 3): 3, (4, 4): 2, (5, 4): 2, (6, 4): 2, (7, 4): 1, (5, 5): 1, (6, 5): 1}
        for (x, y), i in pts.items():
            if d[y, x] > 0:
                img[y, x] = bone[i]
        img[4, 5] = ramp('#0a0c14')[0]
        img[4, 4] = bone[3]
        # hueso largo en el otro bloque
    # musgo espectral
    if v in (0, 2):
        yy, xx = np.mgrid[0:16, 0:16]
        n = fbm(16, 16, 3, 3, 2, 40 + v)
        m = (n > .7) & (d > 0)
        img[m] = A[1][None, :] * (.5 + .25 * (n[m] - .7) * 6)[:, None]
    return img


# ------------------------------------------------------------------ forja
def det_forja(cfg, v, H, T, aux, img, idx):
    R, A = cfg['stone'], cfg['acc']
    d = aux
    r = rng(200 + v * 7)
    if v == 0:
        c = walk_crack(r, r.randint(3, 12), r.randint(3, 10), 7, wobble=.9)
        img[c & (d > 0)] = R[0]
    else:
        c = walk_crack(r, r.randint(4, 11), r.randint(4, 10), 5 + 4 * (v == 2), wobble=.8)
        ys, xs = np.nonzero(c)
        for y, x in zip(ys, xs):
            img[y, x] = A[3 if (x + y) % 3 == 0 else 2]
        halo = (np.roll(c, 1, 0) | np.roll(c, -1, 0) | np.roll(c, 1, 1) | np.roll(c, -1, 1)) & ~c
        img[halo] = img[halo] * .55 + A[1] * .5
    n = fbm(16, 16, 4, 4, 2, 77 + v)
    img[(n < .3) & (d > 0)] *= .72
    return img


# ------------------------------------------------------------------ helado
def det_helado(cfg, v, H, T, aux, img, idx):
    R, A = cfg['stone'], cfg['acc']
    d = aux
    r = rng(300 + v)
    yy, xx = np.mgrid[0:16, 0:16]
    # destello diagonal por bloque
    for (bx, by) in [(2, 1), (7, 9), (13, 9)][: 1 + v % 2]:
        ox = (bx + r.randint(0, 3)) % 14
        oy = by + r.randint(0, 3)
        for k in range(4):
            x, y = ox + k, oy + 3 - k
            if 0 <= x < 16 and 0 <= y < 16 and d[y, x] > 1:
                img[y, x] = A[3] if k in (1, 2) else A[1]
    # grietas azul claro
    if v >= 1:
        c = walk_crack(r, r.randint(4, 11), r.randint(3, 9), r.randint(4, 7), wobble=.9)
        img[c & (d > 0)] = R[1]
        h2 = np.roll(c, 1, 0) & ~c & (d > 0)
        img[h2] = A[2]
    # motas de escarcha
    n = fbm(16, 16, 4, 4, 2, 31 + v)
    m = (n > .72) & (d > 1)
    img[m] = img[m] * .5 + A[1] * .5
    return img


# ------------------------------------------------------------------ vacio
def det_vacio(cfg, v, H, T, aux, img, idx):
    R, A = cfg['stone'], cfg['acc']
    edge, bid = aux
    r = rng(400 + v)
    for _ in range(1 + (v == 2)):
        c = walk_crack(r, r.randint(3, 12), r.randint(3, 10), r.randint(6, 10), wobble=.6)
        img[c] = A[1]
        halo = (np.roll(c, 1, 0) | np.roll(c, -1, 0) | np.roll(c, 1, 1) | np.roll(c, -1, 1)) & ~c
        img[halo] = img[halo] * .7 + A[0] * .35
        ys, xs = np.nonzero(c)
        for k, (y, x) in enumerate(zip(ys, xs)):
            if k % 3 == 1:
                img[y, x] = A[2]
            if k % 7 == 3:
                img[y, x] = A[3]
    for k in range(2):
        x, y = r.randint(2, 14), r.randint(2, 14)
        img[y, x] = ramp('#6a58b0')[0]
    return img


# ------------------------------------------------------------------ bosque
def det_bosque(cfg, v, H, T, aux, img, idx):
    R, A = cfg['stone'], cfg['acc']
    sm = aux
    r = rng(500 + v)
    n = fbm(16, 16, 3, 3, 2, 55 + v)
    m = (n > .74) & ~sm
    img[m] = A[1][None, :] * (.7 + .5 * (n[m] - .74) * 3)[:, None]
    # musgo con borde claro
    top = m & ~np.roll(m, 1, 0)
    img[top] = A[2]
    if v == 1:  # hongos luminosos incrustados
        for (x, y) in [(5, 6), (10, 10)]:
            img[y, x] = ramp('#ffd070')[0]
            img[y, x - 1] = img[y, x + 1] = ramp('#a86a24')[0]
            img[y + 1, x] = ramp('#6b4020')[0]
    if v == 2:
        c = walk_crack(r, 8, 3, 9, ang=1.5, wobble=.6)
        img[c & ~sm] = R[0]
    return img


# ------------------------------------------------------------------ tormenta
def det_torm(cfg, v, H, T, aux, img, idx):
    R, A = cfg['stone'], cfg['acc']
    d, riv, drip, bid, rowi = aux
    r = rng(600 + v)
    # borde de cobre en cada placa
    bd = (d == 1)
    yy, xx = np.mgrid[0:16, 0:16]
    topleft = bd & (((yy % 8) == 0))
    botright = bd & ~topleft & ((yy % 8) == 6)
    img[topleft] = A[2]
    img[botright] = A[0]
    # remaches
    img[riv] = A[3]
    r2 = np.roll(np.roll(riv, 1, 0), 1, 1)
    img[r2 & ~riv & (d > 0)] = A[0]
    img[np.roll(riv, -1, 0) & ~riv & (d > 0)] = A[4] if False else A[3]
    # patina turquesa escurrida
    pat = ramp('#27685c', '#368c78', '#5cc0a4')
    for x in r.choice(np.arange(1, 15), 2, replace=False):
        y0 = r.randint(1, 7)
        ln = r.randint(3, 6)
        for k in range(ln):
            y = (y0 + k)
            if y < 15 and d[y, x] > 0:
                img[y, x] = pat[1 if k < ln - 1 else 0] if k else pat[2]
    # rayo / chamusquina
    if v == 2:
        c = walk_crack(r, 8, 3, 8, ang=1.3, wobble=1.1)
        img[c & (d > 0)] = ramp('#c8f0ff')[0]
    return img


# ------------------------------------------------------------------ sangre
def det_sangre(cfg, v, H, T, aux, img, idx):
    R, A = cfg['stone'], cfg['acc']
    d = aux
    r = rng(700 + v)
    # churretones de sangre desde las juntas
    for x in r.choice(np.arange(1, 15), 3 if v else 2, replace=False):
        y0 = int(r.choice([3, 7, 11]))
        ln = r.randint(3, 6)
        for k in range(ln):
            y = y0 + k
            if 0 <= y < 16 and d[y, x] > 0 and (y < 16):
                img[y, x] = A[2] if k < ln - 1 else A[1]
        if y0 + ln < 16 and d[min(15, y0 + ln - 1), x] > 0:
            pass
    if v == 99:
        bone = ramp('#5a4a4a', '#9a8a80', '#d0c2b0', '#f0e6d4')
        pts = {(5, 4): 2, (6, 4): 3, (7, 4): 3, (8, 4): 2, (5, 5): 2, (6, 5): 1, (7, 5): 1, (8, 5): 2, (6, 6): 2, (7, 6): 2}
        for (x, y), i in pts.items():
            if d[y, x] > 0:
                img[y, x] = bone[i]
        img[5, 6] = img[5, 7] = R[0] * .5
    if v == 2:
        c = walk_crack(r, 5, 3, 8, wobble=.8)
        img[c & (d > 0)] = R[0]
    return img


# ------------------------------------------------------------------ eclipse
def det_eclipse(cfg, v, H, T, aux, img, idx):
    R, A = cfg['stone'], cfg['acc']
    d, bid, rowi, strad = aux
    r = rng(900 + v)
    for row in (0, 1):
        y0 = row * 8
        off = 0 if row == 0 else 8
        # coordenadas locales: lx = (x-off)%16 ; la losa ocupa lx 0..14
        def X(lx):
            return (lx + off) % 16
        if v == 0:   # filete de oro con rombo central
            for lx in range(3, 12):
                img[y0 + 3, X(lx)] = A[1]
            img[y0 + 3, X(7)] = A[3]
            img[y0 + 2, X(7)] = A[2]
            img[y0 + 4, X(7)] = A[2]
            img[y0 + 3, X(6)] = A[2]
            img[y0 + 3, X(8)] = A[2]
        elif v == 1:  # muescas de oro en los extremos
            for lx in (2, 12):
                img[y0 + 2, X(lx)] = A[1]
                img[y0 + 3, X(lx)] = A[2] if row == 0 else A[1]
                img[y0 + 4, X(lx)] = A[1]
            img[y0 + 3, X(7)] = A[1]
        else:
            if row == 0:
                for lx in range(4, 11):
                    img[y0 + 4, X(lx)] = A[0]
                img[y0 + 4, X(7)] = A[2]
    if v == 2:
        c = walk_crack(r, r.randint(3, 12), r.randint(3, 9), 8, wobble=.8)
        img[c & (d > 0)] = R[0]
    return img


# ------------------------------------------------------------------ cazador
def det_cazador(cfg, v, H, T, aux, img, idx):
    R, A = cfg['stone'], cfg['acc']
    edge = aux
    r = rng(800 + v)
    # reflejo rojizo de la luna en el borde superior-izq de cada adoquin
    up = (edge > .6) & (np.roll(edge, 1, 0) < .6)
    lf = (edge > .6) & (np.roll(edge, 1, 1) < .6)
    m = (up | lf) & (fbm(16, 16, 4, 4, 2, 31 + v) > .66)
    img[m] = A[0] * .8 + R[3] * .4
    # charcos / humedad oscura
    n = fbm(16, 16, 3, 3, 2, 12 + v)
    img[(n < .28) & (edge > .6)] *= .75
    # musgo ceniciento
    if v == 2:
        mm = (fbm(16, 16, 4, 4, 2, 66) > .66) & (edge > .6)
        img[mm] = ramp('#3a4a40')[0]
    if v == 1:
        c = walk_crack(r, r.randint(4, 11), r.randint(3, 10), 7, wobble=.8)
        img[c & (edge > .5)] = R[0]
    return img


def mk(name, **kw):
    kw['name'] = name
    kw.setdefault('seed', BIOMES.index(name) + 1)
    return kw


CFG = {}

CFG['catacumbas'] = mk('catacumbas', kind='bricks',
    bricks=dict(rows=8, bw=16, offsets=[0, 8], mortar=1, bevel=2, tonevar=.6),
    stone=ramp('#0f1524', '#192238', '#27344f', '#3a4a6b', '#55698c', '#7d92b2'),
    lip=ramp('#eef6fa', '#c0d2e2', '#86a0bc', '#3a4d70'),
    acc=ramp('#14402e', '#38a878', '#5cff9a', '#c4ffe0'),
    sh=1.1, tn=.6, dith=.3, lip_h=4, lip_rough=1, lip_seams=(7,), drip=.1, drip_len=2, tips=.0, chip=.5, detail=det_cata,
    outline_tint=(4, 8, 20))

CFG['forja'] = mk('forja', kind='bricks',
    bricks=dict(rows=4, bw=8, offsets=[0, 4, 0, 4], mortar=1, bevel=1, tonevar=.7, mortar_tone=.0),
    stone=ramp('#09050a', '#140a0f', '#230f16', '#37161a', '#52211d', '#72341f'),
    lip=ramp('#ffd49a', '#b09480', '#72605e', '#382c34'),
    acc=ramp('#5a1008', '#c8340c', '#ff7a1a', '#ffd870'),
    sh=1.2, tn=.55, dith=.25, lip_h=4, lip_rough=1, lip_seams=(3,11), drip=.0, chip=.5, detail=det_forja,
    outline_tint=(14, 4, 6))

CFG['helado'] = mk('helado', kind='bricks',
    bricks=dict(rows=8, bw=16, offsets=[0, 8], mortar=1, bevel=2, tonevar=.5),
    stone=ramp('#0c1a38', '#142a52', '#1d4070', '#2b5e92', '#4284b8', '#78b4de'),
    lip=ramp('#ffffff', '#e4f8ff', '#a6d8f4', '#4a7ab4'),
    acc=ramp('#5a98d0', '#a0daf8', '#d8f6ff', '#ffffff'),
    sh=1.1, tn=.6, dith=.3, lip_h=4, lip_rough=1, drip=.14, drip_len=3, tips=.2, chip=.45, detail=det_helado,
    outline_tint=(6, 14, 40))

CFG['vacio'] = mk('vacio', kind='obsidian', obs=dict(n=4),
    stone=ramp('#06040f', '#0d0820', '#160d30', '#22144a', '#33206a', '#4c3290'),
    lip=ramp('#e6b4ff', '#a066e8', '#5a34a0', '#2a1660'),
    acc=ramp('#3a1470', '#7a30d0', '#c068ff', '#f4c8ff'),
    sh=1.0, tn=.5, dith=.2, lip_h=3, lip_rough=1, drip=.0, tips=.0, chip=.6, detail=det_vacio,
    outline_tint=(6, 2, 22))

CFG['bosque'] = mk('bosque', kind='wood', wood=dict(seams=[5, 11, 16], knots=[(8, 8), (4, 5), (11, 10)]),
    stone=ramp('#0d0a08', '#1a130e', '#2b2016', '#42301e', '#5e4528', '#82602f'),
    lip=ramp('#d6f27a', '#8cc84a', '#47963c', '#1f4c2c'),
    acc=ramp('#16301a', '#2a5c28', '#5aa63c', '#a4e060'),
    sh=.8, tn=.6, dith=.25, lip_h=4, lip_rough=1, drip=.18, drip_len=3, tips=.35, chip=.7, detail=det_bosque,
    outline_tint=(8, 8, 4))

CFG['tormenta'] = mk('tormenta', kind='plates', plates={},
    stone=ramp('#0c1618', '#16282c', '#223e42', '#335c58', '#4a8478', '#72b8a0'),
    lip=ramp('#ffe0a8', '#eeaa5c', '#b86c34', '#5c3226'),
    acc=ramp('#3a1e1c', '#7a4228', '#c07038', '#ec9c54', '#ffd69a'),
    sh=1.2, tn=.9, lip_h=3, lip_rough=1, drip=.15, drip_len=2, tips=.0, chip=.3, detail=det_torm,
    outline_tint=(4, 12, 14))

CFG['sangre'] = mk('sangre', kind='bricks',
    bricks=dict(rows=8, bw=8, offsets=[0, 4], mortar=1, bevel=2, tonevar=.6, mortar_tone=.0),
    stone=ramp('#0f030a', '#1c0810', '#2e0c16', '#46121e', '#621a28', '#842a36'),
    lip=ramp('#ff9aa8', '#d0304c', '#841a34', '#3e0c20'),
    acc=ramp('#4a0614', '#8a0e24', '#c41e3c', '#f0506a'),
    sh=1.1, tn=.6, dith=.3, lip_h=4, lip_rough=1, drip=.3, drip_len=4, tips=.0, chip=.4, detail=det_sangre,
    outline_tint=(14, 2, 8))

CFG['eclipse'] = mk('eclipse', kind='slab', slab={},
    stone=ramp('#07070d', '#0f0f19', '#191926', '#262638', '#383852', '#51516f'),
    lip=ramp('#fff6c4', '#f0cc68', '#b08830', '#503c1a'),
    acc=ramp('#3a2c14', '#9a7428', '#d8a840', '#f8dc78', '#fff6c4'),
    sh=1.3, tn=.8, lip_h=3, lip_rough=0, drip=.0, tips=.0, chip=.25, detail=det_eclipse,
    outline_tint=(8, 6, 14))

CFG['cazador'] = mk('cazador', kind='cobble', cobble=dict(n=4),
    stone=ramp('#0b0913', '#171320', '#262031', '#3a3248', '#524863', '#756888'),
    lip=ramp('#e6aab4', '#a58ca6', '#625a7e', '#2c2845'),
    acc=ramp('#4a1020', '#a0283c', '#e04458', '#ff8a96'),
    sh=1.2, tn=.6, dith=.3, lip_h=4, lip_rough=1, lip_seams=(5,), drip=.0, tips=.0, chip=.55, detail=det_cazador,
    outline_tint=(10, 4, 14))
