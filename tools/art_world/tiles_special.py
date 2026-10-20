"""Ensamblado de la hoja de baldosas completa de cada bioma."""
import numpy as np
from kit import *
from lib_props import *
import lib_props as L
from terrain import terrain_tile, build_interior, walk_crack
from biomes import CFG, BIOMES
import copy


def base_P(stone):
    return dict(rockramp=stone, bone=BONE, wood=WOOD, metal=IRON, gold=GOLD, flame=FL_ORANGE, glow=FL_ORANGE,
                eye=FL_GREEN, moss=MOSS, liquid=FL_GREEN, wax=BONE, skin=ramp('#3a4a40', '#6a806c', '#94a88a', '#bccaa8'),
                cap=ramp('#4a1e08', '#9a4a14', '#e08a2a', '#ffc860'), cap2=ramp('#0a3a3a', '#1a7a72', '#3ac8b0', '#9cffe4'),
                crystal=ICE, ice=ICE, snow=ramp('#7aa0d0', '#b8d4f0', '#e0f0ff', '#f6fbff', '#ffffff'), bloom=FL_AMBER,
                thorn=ramp('#1a1208', '#3a2a14', '#5a4020', '#86602c'), copper=COPPER, meat=ramp('#2a0a10', '#5a1020', '#8a1c30', '#b8304a'),
                cloth=CLOTH_R, hilt=GOLD, batcol=ramp('#120a1c', '#2a1a3c', '#42285a', '#5c3a7c'),
                feather=ramp('#0a0810', '#181420', '#2a2436', '#403a52'), beak=ramp('#2a2010', '#5a4420', '#8a6a30', '#b89a48'),
                book1=CLOTH_R, book2=CLOTH_B, book3=CLOTH_G, urnramp=WOOD, paint=ramp('#14101c', '#2a2038', '#4a3a60', '#9a88b8'),
                moon=ramp('#3a3a4a', '#7a7a90', '#b8b8d0', '#e8e8f8', '#ffffff'), gl_ramp=FL_AMBER, shroom_stalk=BONE)


def dark_ramp(R, k=.55):
    return R * k


def wall_cfg(cfg):
    w = copy.deepcopy(cfg)
    R = cfg['stone']
    lo, hi = R[0] * .5 + 2, R[3] * .42 + 4
    w['stone'] = np.stack([lo + (hi - lo) * t for t in np.linspace(0, 1, 6)])
    w['sh'] = .55
    w['tn'] = .45
    w['dith'] = .2
    w['detail'] = None
    w['name'] = cfg['name'] + '_wall'
    return w


def compose(base_rgb, cv):
    out = base_rgb.copy()
    a = cv.a
    out[a] = cv.rgb[a]
    return out


def to_rgba(rgb, alpha=None):
    out = np.zeros((16, 16, 4), np.uint8)
    out[..., :3] = np.clip(rgb + .5, 0, 255).astype(np.uint8)
    out[..., 3] = 255 if alpha is None else np.where(alpha, 255, 0)
    return out


def wall_tile(wcfg, v):
    return build_interior(wcfg, v)


def tile_arch(P, wcfg, cfg):
    base = wall_tile(wcfg, 0)
    R = cfg['stone']
    c = Canvas()
    outer = ply((.5, 16), (.5, 9), (2.5, 5), (8, 1), (13.5, 5), (15.5, 9), (15.5, 16))
    inner = ply((3, 16), (3, 9.5), (4.5, 6.8), (8, 3.8), (11.5, 6.8), (13, 9.5), (13, 16))
    c.shape(outer, R, base=.42, shade=.9)
    deep = R[0] * .55
    yy, xx = np.mgrid[0:16, 0:16]
    c.fill(inner, deep)
    # degradado interior
    g = inner & (yy > 10)
    c.fill(g & ((xx + yy) % 2 == 0), R[0] * .4)
    # dovelas
    c.fill(outer & ~inner & ((np.arctan2(yy - 11, xx - 8) * 8 // 1).astype(int) % 2 == 0) & (yy < 9), R[3] * .9)
    return to_rgba(compose(base, c))


def tile_window(P, wcfg, cfg, glass):
    base = wall_tile(wcfg, 1)
    c = w_window(P, glass)
    return to_rgba(compose(base, c))


def tile_column(P, wcfg, cfg):
    base = wall_tile(wcfg, 2)
    R = cfg['stone']
    c = Canvas()
    prof = [0, 1, 2, 3, 4, 4, 3, 3, 2, 2, 1, 1, 0, 0]
    cols = [(3, 0), (4, 2), (5, 3), (6, 4), (7, 4), (8, 3), (9, 3), (10, 2), (11, 2), (12, 1), (13, 0)]
    r = rng(cfg['seed'] * 3)
    n = fbm(16, 16, 4, 4, 2, 5)
    for (x, k) in cols:
        for y in range(16):
            kk = k + (1 if n[y, x] > .66 else 0) - (1 if n[y, x] < .3 else 0)
            c.px(x, y, R[int(np.clip(kk, 0, len(R) - 1))])
    for y in (0, 15):
        for (x, k) in cols:
            c.px(x, y, R[max(0, min(len(R) - 1, k - 1))])
    c.px(3, 8, R[0])
    c.px(13, 8, R[0])
    out = compose(base, c)
    # sombra proyectada en el muro
    for y in range(16):
        out[y, 14] *= .78
        out[y, 2] *= .88
    return to_rgba(out)


def tile_crack(P, wcfg, cfg):
    base = wall_tile(wcfg, 3).copy()
    r = rng(cfg['seed'] * 17)
    R = cfg['stone']
    m = walk_crack(r, 8, 2, 14, ang=1.6, wobble=.9)
    m |= walk_crack(r, 8, 8, 6, ang=.2, wobble=.9)
    base[m] = R[0] * .5
    hl = np.roll(m, 1, 1) & ~m
    base[hl] = np.clip(base[hl] * 1.35 + 6, 0, 255)
    return to_rgba(base)


def platform_tiles(P, kind):
    """Fila 3 col 0..3: suelta, cap izq, centro, cap der. 6 px superiores."""
    R = P['plat']  # rampa 5
    acc = P.get('plat_acc')
    out = []
    for t in range(4):
        c = np.zeros((16, 16, 4), np.uint8)
        xs = np.arange(16)
        for y in range(6):
            for x in range(16):
                lx = x
                if t == 0 and (x < 1 or x > 14) and y in (0, 1, 5):
                    continue
                if t == 1 and x < 1 and y in (0, 5):
                    continue
                if t == 3 and x > 14 and y in (0, 5):
                    continue
                if y == 0:
                    col = R[4]
                elif y == 1:
                    col = R[3]
                elif y == 5:
                    col = R[0]
                elif y == 4:
                    col = R[1]
                else:
                    col = R[2]
                # costuras / remaches periodicos
                if kind in ('stone', 'slab') and x % 8 == 7 and 1 < y < 5:
                    col = R[1]
                if kind == 'plank' and x % 5 == 4 and 1 < y < 5:
                    col = R[1]
                if kind == 'grate' and y in (2, 3) and x % 4 in (1, 2):
                    col = R[0]
                if kind == 'metal' and y == 3 and x % 8 == 3:
                    col = R[4]
                if kind == 'ice' and y in (2, 3) and (x + y) % 6 == 0:
                    col = R[4]
                if kind == 'glow' and y == 5:
                    col = acc[2]
                c[y, x, :3] = np.clip(col, 0, 255)
                c[y, x, 3] = 255
        if t in (1, 0):
            for y in range(1, 5):
                c[y, 1, :3] = np.clip(R[1] if y > 1 else R[3], 0, 255)
                c[y, 2, :3] = np.clip(R[3] if y == 1 else R[2] * 1.0, 0, 255)
        if t in (3, 0):
            for y in range(1, 5):
                c[y, 14, :3] = np.clip(R[1], 0, 255)
                c[y, 13, :3] = np.clip(R[3] if y == 1 else R[2], 0, 255)
        # terminaciones: caps con ménsula
        if t in (1, 0):
            for y in range(1, 5):
                c[y, 0, :3] = np.clip(R[0] * 1.2 + 6, 0, 255)
        if t in (3, 0):
            for y in range(1, 5):
                c[y, 15, :3] = np.clip(R[0] * 1.2 + 6, 0, 255)
        if t == 1 or t == 0:
            c[1, 1, :3] = np.clip(R[4], 0, 255)
        # sombra inferior (soporte)
        if kind in ('stone', 'slab', 'plank', 'metal', 'grate'):
            pass
        out.append(c)
    return out


DANGER = [(18, 4, 10), (74, 14, 30), (170, 34, 52), (232, 72, 86), (255, 226, 214)]   # rojo peligro, igual en todos los biomas
IRON = [(12, 4, 8), (38, 30, 46), (92, 84, 108), (150, 142, 166)]


def spikes(P, up=True, body=None, tip=None, base_col=None, blood=False):
    """Pinchos de alto contraste: puntas rojas con borde oscuro y punta casi blanca sobre placa de hierro.
    Misma paleta en todos los biomas (no se confunden con el suelo); caja de colision = la baldosa completa."""
    D = DANGER
    out = np.zeros((16, 16, 4), np.uint8)
    pix = {}

    def setp(x, y, col):
        if 0 <= x < 16 and 0 <= y < 16:
            pix[(x, y)] = col
    for x in range(16):                       # placa base (y=15 es la base)
        setp(x, 15, IRON[0]); setp(x, 14, IRON[1])
        setp(x, 13, IRON[3] if x % 4 == 2 else IRON[2])
        if x % 4 == 0: setp(x, 14, D[3])      # remache rojo
    body_px = set()
    for cx in (4, 12):                        # 2 puntas triangulares por baldosa: silueta clara de lejos
        ytip, ybase = 1, 12
        for y in range(ytip, ybase + 1):
            t = (y - ytip) / (ybase - ytip)
            hw = 0.5 + 2.9 * t
            xl = int(round(cx - hw)); xr = int(round(cx + hw))
            for x in range(xl, xr):
                if x < cx - 1: col = D[2]
                elif x < cx: col = D[3]
                elif x == cx: col = D[2]
                else: col = D[1]
                if y <= ytip + 2: col = D[4] if x < cx else D[3]
                setp(x, y, col); body_px.add((x, y))
    for (x, y) in list(body_px):              # contorno oscuro para la silueta
        for dx, dy in ((-1, 0), (1, 0), (0, -1)):
            q = (x + dx, y + dy)
            if q not in pix and 0 <= q[0] < 16 and 0 <= q[1] < 16:
                pix[q] = D[0]
    for (x, y), col in pix.items():
        yy = y if up else 15 - y
        out[yy, x, :3] = np.clip(col, 0, 255); out[yy, x, 3] = 255
    return out


def hazard_tiles(P):
    """cols 6,7: liquido/hazard brillante, 2 fotogramas, teselable."""
    Lq = P['haz']
    out = []
    for f in range(2):
        c = np.zeros((16, 16, 4), np.uint8)
        n = fbm(16, 16, 4, 2, 2, 31)
        for x in range(16):
            ph = 2 * np.pi * x / 16
            top = 4 + int(round(np.sin(ph + f * np.pi) * 1.0 + np.sin(ph * 2 + f * 1.3) * .5))
            for y in range(top, 16):
                d = y - top
                if d == 0:
                    col = Lq[4]
                elif d == 1:
                    col = Lq[3]
                else:
                    k = 2 if n[y, (x + f * 3) % 16] > .5 else 1
                    k = 2 - (d > 5) if k == 2 else 1
                    col = Lq[k] if not (d > 8 and n[y, x] < .5) else Lq[0]
                    if (x * 3 + y * 5 + f * 7) % 17 == 0 and d > 2:
                        col = Lq[3]
                c[y, x, :3] = np.clip(col, 0, 255)
                c[y, x, 3] = 255
        out.append(c)
    return out


def build_sheet(name, P, spec):
    cfg = CFG[name]
    wcfg = wall_cfg(cfg)
    sheet = np.zeros((128, 256, 4), np.uint8)
    # terreno
    for v in range(3):
        for m in range(16):
            put(sheet, m, v, terrain_tile(cfg, m, v))
    # fila 3
    for i, t in enumerate(platform_tiles(P, spec['plat_kind'])):
        put(sheet, i, 3, t)
    put(sheet, 4, 3, spikes(P, True, blood=spec.get('blood', False)))
    put(sheet, 5, 3, spikes(P, False, blood=spec.get('blood', False)))
    for i, t in enumerate(hazard_tiles(P)):
        put(sheet, 6 + i, 3, t)
    for v in range(4):
        put(sheet, 8 + v, 3, to_rgba(wall_tile(wcfg, v)))
    put(sheet, 12, 3, tile_arch(P, wcfg, cfg))
    put(sheet, 13, 3, tile_window(P, wcfg, cfg, spec['glass']))
    put(sheet, 14, 3, tile_column(P, wcfg, cfg))
    put(sheet, 15, 3, tile_crack(P, wcfg, cfg))
    # fila 4: antorchas + luz alternativa + colgantes
    for f in range(4):
        put(sheet, f, 4, spec['torch'](P, f).to_img())
        put(sheet, 4 + f, 4, spec['alt'](P, f).to_img())
    for i, fn in enumerate(spec['hang']):
        put(sheet, 8 + i, 4, fn(P).to_img())
    for i, fn in enumerate(spec['props']):
        put(sheet, i, 5, fn(P).to_img())
    for i, fn in enumerate(spec['wall']):
        put(sheet, i, 6, fn(P).to_img())
    return sheet
