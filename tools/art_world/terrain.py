"""Terreno autotile (4 vecinos) con 3 variantes, periodico para que las variantes encajen."""
import numpy as np
from kit import *

N, E, S, W = 1, 2, 4, 8


def walk_crack(r, x, y, n, ang=None, wobble=.7):
    m = np.zeros((16, 16), bool)
    a = r.rand() * 6.28 if ang is None else ang
    for _ in range(n):
        xi, yi = int(round(x)), int(round(y))
        if 2 <= xi <= 13 and 2 <= yi <= 13:
            m[yi, xi] = True
        a += (r.rand() - .5) * wobble * 2
        x += np.cos(a)
        y += np.sin(a)
    return m


def blob_mask(r, cx, cy, rad):
    yy, xx = np.mgrid[0:16, 0:16]
    return (xx - cx) ** 2 + (yy - cy) ** 2 < rad * rad


# ----------------------------------------------------------------- texturas -> (H, T, A)
def tex_bricks(cfg, v):
    p = cfg['bricks']
    d, bid, strad, rowi = bricks(p['rows'], p['bw'], p.get('offsets'), p.get('mortar', 1))
    r = rng(cfg['seed'] * 7 + v * 13)
    r0 = rng(cfg['seed'] * 7)
    nbk = 16 // p['bw'] + 1
    tone_v = r.rand(16 // p['rows'], nbk)
    tone_0 = r0.rand(16 // p['rows'], nbk)
    T = np.where(strad, tone_0[rowi, bid], tone_v[rowi, bid])
    T = .5 + (T - .5) * p.get('tonevar', .55)
    # grano
    grain = fbm(16, 16, 4, 4, 2, cfg['seed'] + 5)
    gv = vnoise(16, 16, 8, 8, cfg['seed'] * 3 + v * 17)
    T = T + (grain - .5) * .35 + (gv - .5) * .35
    bev = np.minimum(d, p.get('bevel', 2)) / p.get('bevel', 2)
    H = bev * .8 + (grain - .5) * .4 + (gv - .5) * .25
    H = np.where(d == 0, -.4, H)
    T = np.where(d == 0, p.get('mortar_tone', .05), T)
    A = np.zeros((16, 16))
    return H, T, A, d


def tex_cobble(cfg, v):
    p = cfg['cobble']
    # voronoi con semilla fija de 'esqueleto' + variacion de tono por variante
    bid, d1, edge = voronoi(p['n'], cfg['seed'] + 3, jitter=.7)
    r = rng(cfg['seed'] * 5 + v * 11)
    r0 = rng(cfg['seed'] * 5)
    T = .5 + (r.rand(400)[bid] - .5) * .6
    grain = fbm(16, 16, 4, 4, 2, cfg['seed'] + 9)
    gv = vnoise(16, 16, 8, 8, cfg['seed'] * 3 + v * 19)
    cell = np.clip(edge / 2.2, 0, 1)
    H = cell * .8 + (1 - np.clip(d1 / 5, 0, 1)) * .45 + (grain - .5) * .15 + (gv - .5) * .1
    H = np.where(edge < .6, -.4, H)
    T = T + (grain - .5) * .15 + (gv - .5) * .12
    T = np.where(edge < .6, .05, T)
    return H, T, np.zeros((16, 16)), edge


def tex_wood(cfg, v):
    p = cfg['wood']
    xs = np.arange(16)
    # tablones verticales con juntas fijas
    seams = p['seams']
    pl = np.zeros(16, int)
    for s in seams:
        pl[xs >= s] += 1
    r = rng(cfg['seed'] * 3 + v * 7)
    r0 = rng(cfg['seed'] * 3)
    tone = r0.rand(8)
    grainx = vnoise(16, 16, 8, 2, cfg['seed'] + v * 31)  # vetas verticales
    grain0 = vnoise(16, 16, 4, 2, cfg['seed'] + 41)
    T = .5 + (tone[pl][None, :] - .5) * .5 + (grainx - .5) * .6 + (grain0 - .5) * .3
    H = (grainx - .5) * .5 + (grain0 - .5) * .3
    sm = np.zeros((16, 16), bool)
    for s in seams:
        sm[:, (s - 1) % 16] = True
    H = np.where(sm, -.5, H)
    T = np.where(sm, .05, T)
    # nudos
    kn = np.zeros((16, 16))
    yy, xx = np.mgrid[0:16, 0:16]
    for (kx, ky) in p.get('knots', [(7, 8), (3, 4), (11, 12)])[v:v + 1]:
        dd = np.hypot(xx - kx, (yy - ky) * .6)
        H += np.where(dd < 2.2, -.5 * (1 - dd / 2.2), 0)
        T += np.where(dd < 2.2, -.35, 0)
    return H, T, np.zeros((16, 16)), sm


def tex_plates(cfg, v):
    offs = [0, 8]
    d, bid, strad, rowi = bricks(8, 16, offs, 1)
    r = rng(cfg['seed'] * 5 + v * 3)
    r0 = rng(cfg['seed'] * 5)
    tv = r.rand(2, 2)
    t0 = r0.rand(2, 2)
    T = .5 + (np.where(strad, t0[rowi, bid], tv[rowi, bid]) - .5) * .4
    grain = fbm(16, 16, 4, 4, 2, cfg['seed'] + 5)
    gv = vnoise(16, 16, 8, 8, cfg['seed'] * 3 + v * 17)
    drip = vnoise(16, 16, 8, 2, cfg['seed'] + v * 5)
    T = T + (grain - .5) * .3 + (gv - .5) * .15
    bev = np.minimum(d, 2) / 2
    H = bev * .6 + (gv - .5) * .2
    H = np.where(d == 0, -.4, H)
    T = np.where(d == 0, .05, T)
    riv = np.zeros((16, 16), bool)
    yy, xx = np.mgrid[0:16, 0:16]
    for y in range(16):
        for x in range(16):
            ly = y % 8
            lx = (x - offs[y // 8]) % 16
            if ly in (2, 5) and lx in (2, 12):
                riv[y, x] = True
    return H, T, np.zeros((16, 16)), (d, riv, drip, bid, rowi)


def tex_ice(cfg, v):
    bid, d1, edge = voronoi(cfg['ice']['n'], cfg['seed'] + v * 2 + 1, jitter=.9)
    # facetas con pendiente propia
    r = rng(cfg['seed'] * 9)
    sl = r.rand(64, 2) - .5
    yy, xx = np.mgrid[0:16, 0:16]
    H = (sl[bid, 0] * (xx % 16 - 8) + sl[bid, 1] * (yy % 16 - 8)) * .06
    H = (H - H.min()) / (np.ptp(H) + 1e-6) * .6
    H += np.clip(edge / 2, 0, 1) * .35
    H = np.where(edge < .5, -.3, H)
    gv = vnoise(16, 16, 8, 8, cfg['seed'] * 3 + v * 19)
    T = .5 + (sl[bid, 0] + sl[bid, 1]) * .35 + (gv - .5) * .3
    # vetas blancas diagonales
    A = np.zeros((16, 16))
    return H, T, A, edge


def tex_slab(cfg, v):
    d, bid, strad, rowi = bricks(8, 16, [0, 8], 1)
    r = rng(cfg['seed'] * 5 + v * 3)
    r0 = rng(cfg['seed'] * 5)
    tv = r.rand(2, 2)
    t0 = r0.rand(2, 2)
    grain = fbm(16, 16, 4, 4, 2, cfg['seed'] + 5)
    gv = vnoise(16, 16, 8, 8, cfg['seed'] * 3 + v * 17)
    T = .5 + (np.where(strad, t0[rowi, bid], tv[rowi, bid]) - .5) * .3 + (grain - .5) * .35 + (gv - .5) * .2
    bev = np.minimum(d, 2) / 2
    H = bev * .7 + (grain - .5) * .3
    H = np.where(d == 0, -.4, H)
    T = np.where(d == 0, .04, T)
    return H, T, np.zeros((16, 16)), (d, bid, rowi, strad)


def tex_obsidian(cfg, v):
    n = cfg['obs']['n']
    bid, d1, edge = voronoi(n, cfg['seed'] + 5, jitter=.8)
    r = rng(cfg['seed'] * 9)
    sl = r.rand(64, 2) - .5
    yy, xx = np.mgrid[0:16, 0:16]
    H = (sl[bid, 0] * (xx - 8) + sl[bid, 1] * (yy - 8)) * .08
    H = (H - H.min()) / (np.ptp(H) + 1e-6) * .5 + np.clip(edge / 2, 0, 1) * .4
    gv = vnoise(16, 16, 8, 8, cfg['seed'] * 3 + v * 19)
    T = .5 + (sl[bid, 0] - sl[bid, 1]) * .5 + (gv - .5) * .25
    H = np.where(edge < .5, -.3, H)
    return H, T, np.zeros((16, 16)), (edge, bid)


# ----------------------------------------------------------------- detalles por bioma
def detail(cfg, v, H, T, A, aux, img):
    """Aplica detalles especificos; devuelve img rgb modificado."""
    return img


def build_interior(cfg, v):
    kind = cfg['kind']
    H, T, A, aux = globals()['tex_' + kind](cfg, v)
    R = cfg['stone']
    n = len(R)
    lum = .5 + lights(H) * cfg.get('sh', 1.0) + (T - .5) * cfg.get('tn', .8)
    lum = lum * cfg.get('gain', 1.0) + cfg.get('lift', 0.0)
    idx = dither_idx(np.clip(lum, 0, 1), n, 0, 0, cfg.get('dith', .5))
    img = R[idx].copy()
    hook = cfg.get('detail')
    mods = np.zeros((16, 16), bool)
    if hook:
        img = hook(cfg, v, H, T, aux, img, idx)
    return img


# ----------------------------------------------------------------- perfiles de borde
def make_profiles(cfg, v):
    r = rng(cfg['seed'] * 31 + v * 977)
    pr = cfg.get('chip', .35)
    prof = {}
    for k in 'WES':
        a = np.zeros(16, int)
        for i in range(3, 13):
            if r.rand() < pr * .5:
                a[i] = 1
        prof[k] = a
    lipr = cfg.get('lip_rough', 1)
    base = cfg.get('lip_h', 3)
    prof['lip'] = np.full(16, base)
    t = vnoise(16, 1, 5, 1, cfg['seed'] * 11 + v * 5)[0]
    for i in range(16):
        prof['lip'][i] = base + int(np.floor((t[i] - .5) * 2 * lipr + .5))
    prof['lip'][[0, 15]] = base
    prof['lip'][[1, 14]] = np.clip(prof['lip'][[1, 14]], base - 1, base + 1)
    # gotas largas
    dr = np.zeros(16, int)
    for i in range(2, 14):
        if r.rand() < cfg.get('drip', 0):
            dr[i] = 1 + int(r.randint(1, 1 + cfg.get('drip_len', 3)))
    prof['drip'] = dr
    tc = np.zeros(16, int)
    for i in range(1, 15):
        if r.rand() < cfg.get('tips', 0):
            tc[i] = 1
    prof['tip'] = tc
    prof['mpos'] = r.rand(16)
    return prof


def terrain_tile(cfg, mask, v, cache={}):
    key = (cfg['name'], v)
    if key not in cache:
        cache[key] = (build_interior(cfg, v), make_profiles(cfg, v))
    inter, pr = cache[key]
    img = inter.copy()
    ok = np.ones((16, 16), bool)
    nN, nE, nS, nW = [bool(mask & b) for b in (N, E, S, W)]
    R = cfg['stone']
    L = cfg['lip']
    # ---- recortes (alpha)
    if not nW:
        for y in range(16):
            ok[y, :pr['W'][y]] = False
    if not nE:
        for y in range(16):
            if pr['E'][y]:
                ok[y, 16 - pr['E'][y]:] = False
    if not nS:
        for x in range(16):
            if pr['S'][x]:
                ok[16 - pr['S'][x]:, x] = False
    if not nN:
        for x in range(16):
            if pr['tip'][x]:
                ok[0, x] = False
    if not nN and not nW:
        ok[0, 0] = False
        ok[1, 0] = False if cfg.get('round', 1) > 1 else ok[1, 0]
    if not nN and not nE:
        ok[0, 15] = False
        ok[1, 15] = False if cfg.get('round', 1) > 1 else ok[1, 15]
    if not nS and not nW:
        ok[15, 0] = False
    if not nS and not nE:
        ok[15, 15] = False
    # ---- sombras de cara (AO) antes del labio
    def shade(ys, xs, k):
        img[ys, xs] = np.clip(img[ys, xs] * k, 0, 255)
    if not nE:
        shade(slice(0, 16), slice(13, 16), .78)
        shade(slice(0, 16), slice(14, 16), .8)
    if not nS:
        shade(slice(13, 16), slice(0, 16), .78)
        shade(slice(14, 16), slice(0, 16), .8)
    if not nW:
        shade(slice(0, 16), slice(0, 1), .85)
    if not nN:
        # sombra bajo el labio
        pass
    # ---- labio superior
    lipmask = np.zeros((16, 16), bool)
    if not nN:
        lipH = pr['lip']
        dr = pr['drip']
        for x in range(16):
            top = 1 if pr['tip'][x] else 0
            for y in range(top, 16):
                if y < lipH[x]:
                    rel = y - top
                    if rel == 0:
                        c = L[0]
                    elif y == lipH[x] - 1 and lipH[x] - top > 2:
                        c = L[3]
                    elif rel == 1:
                        c = L[1] if (x + y) % 3 else L[2]
                    else:
                        c = L[2] if (x * 3 + y) % 4 else L[1]
                    if rel >= 1 and x in cfg.get('lip_seams', ()) and rel < lipH[x] - top:
                        c = L[3] if rel > 1 else L[2]
                    img[y, x] = c
                    lipmask[y, x] = True
                elif dr[x] and y < lipH[x] + dr[x]:
                    img[y, x] = L[3] if y == lipH[x] + dr[x] - 1 else L[2]
                    lipmask[y, x] = True
                elif y == lipH[x] + dr[x]:
                    img[y, x] = img[y, x] * .78
                else:
                    break
    # ---- contorno oscuro en caras W/E/S (y huecos de chips)
    pad = np.pad(ok, 1, constant_values=False)
    if nW:
        pad[:, 0] = True
    if nE:
        pad[:, -1] = True
    if nS:
        pad[-1, :] = True
    if nN:
        pad[0, :] = True
    out_col = R[0] * .55 + np.array(cfg.get('outline_tint', (6, 6, 14)), np.float32) * .45
    for y in range(16):
        for x in range(16):
            if not ok[y, x]:
                continue
            l = pad[y + 1, x]
            r_ = pad[y + 1, x + 2]
            d_ = pad[y + 2, x + 1]
            if not (l and r_ and d_):
                if lipmask[y, x] and (not d_ or True):
                    if not l or not r_:
                        img[y, x] = L[3]
                    elif not d_:
                        img[y, x] = L[3]
                else:
                    img[y, x] = out_col
    # realce de la cara W (luz) : 1 px junto al contorno
    if not nW:
        for y in range(2, 16):
            if ok[y, 1] and (nN or y >= pr['lip'][1]) and ok[y, 0]:
                i = np.argmin(np.abs(R - img[y, 1]).sum(1))
                img[y, 1] = R[min(i + 1, len(R) - 1)]
    out = np.zeros((16, 16, 4), np.uint8)
    out[..., :3] = np.clip(img + .5, 0, 255).astype(np.uint8)
    out[..., 3] = np.where(ok, 255, 0)
    out[~ok, :3] = 0
    return out
