#!/usr/bin/env python3
"""Arte de las armas secundarias: sprites de mano (Shared/assets/sprites/wpn_hold.png) e iconos 16x16 de las armas nuevas.

Cada arma se describe una vez como un conjunto de piezas vectoriales (hoja, mango, disco, poligono...) en coordenadas locales (px, apuntando a la derecha,
la empuñadura en (0,0)). De ahi salen:
  * sprite de mano 48x16, empuñadura en (10,8)           -> wpn_hold.png / wpn_hold.json  (todas las armas, ids 1..36)
  * icono 16x16 (arma en diagonal, a escala 0.5)        -> se AÑADEN al final de ui/icons.png (+ nombres en icons.json) solo los que no existen
Se rasteriza al tamaño final (sin rotar mapas de bits), con contorno oscuro y paleta del juego. Idempotente.
Uso: python3 tools/art/make_weapons.py [--preview /tmp/w.png]
"""
import json, math, os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import gen_arsenal_art as G   # paleta y utilidades (solo se importan, no se ejecuta main)

ROOT = os.path.join(HERE, '..', '..', 'Shared', 'assets')
PAL = G.PAL
K = G.K

# ---- piezas por arma (id -> (nombre de icono, piezas)). Coordenadas locales: x hacia delante, y hacia abajo, empuñadura en (0,0).
W = {}


def blade(x0, y0, x1, y1, w=2, c='l', e='m'):
    return ('blade', x0, y0, x1, y1, w, c, e)


def pole(x0, y0, x1, y1, c='B', c2='b'):
    return ('pole', x0, y0, x1, y1, c, c2)


def disc(cx, cy, r, c, h=None):
    return ('disc', cx, cy, r, c, h)


def poly(pts, c, e=None):
    return ('poly', pts, c, e)


def dots(x0, y0, x1, y1, n, c):
    return ('dots', x0, y0, x1, y1, n, c)


# ---- originales (1-10)
W[1] = ('w_knife', [pole(-3, 0, 1, 0), ('line', 1, -2, 1, 2, 'g'), blade(2, 0, 13, 0, 1)])
W[2] = ('w_bolt', [pole(-4, 1, 9, 1, 'B', 'b'), poly([(8, -1), (13, 1), (8, 3)], 'd'), ('line', 5, -6, 8, 1, 'd'), ('line', 5, 8, 8, 1, 'd'), ('line', 5, -6, 5, 8, 'y'),
                   ('line', 3, 1, 12, 1, 'G')])
W[3] = ('w_axe', [pole(-4, 0, 12, 0), poly([(9, -7), (17, -5), (17, 5), (9, 7), (12, 0)], 'm', 'l'), ('line', 17, -5, 17, 5, 'w')])
W[4] = ('w_orb', [disc(6, 0, 5, 'p', 'P'), disc(4, -2, 1, 'w'), ('ring', 6, 0, 3, 4, 'q')])
W[5] = ('w_bow', [('arc', 6, 0, 8, 'B'), ('line', 6, -8, 4, 0, 'w'), ('line', 6, 8, 4, 0, 'w'), pole(-3, 0, 12, 0, 'N', 'n')])
W[6] = ('w_chakram', [('ring', 7, 0, 5, 7, 'm'), ('ring', 7, 0, 5, 5.5, 'l'), disc(7, 0, 1, 'C')])
W[7] = ('w_wand', [pole(-3, 0, 12, 0, 'P', 'p'), disc(14, 0, 3, 'R', 'Y'), disc(14, 0, 1, 'w')])
W[8] = ('w_spear', [pole(-6, 0, 22, 0), poly([(22, -2), (30, 0), (22, 2)], 'l', 'm')])
W[9] = ('w_ember', [poly([(-3, -2), (10, -3), (10, 3), (-3, 3)], 'd', 'm'), poly([(10, -4), (16, -4), (16, 4), (10, 4)], 'o', 'O'), disc(16, 0, 2, 'Y')])
W[10] = ('w_summon', [pole(-4, 0, 14, 0, 'g', 'b'), disc(16, 0, 3, 'T', 'w'), ('ring', 16, 0, 4, 5, 't')])

# ---- cuerpo a cuerpo rapido
W[11] = ('w_dknives', [pole(-3, 0, 1, 0), ('line', 1, -3, 1, 3, 'g'), blade(2, -1, 13, -5, 1), blade(2, 1, 13, 5, 1)])
W[12] = ('w_twins', [pole(-3, 0, 1, 0, 'b', 'e'), ('line', 1, -2, 1, 2, 'G'), blade(2, 0, 12, -2, 1, 'C', 'c'), blade(-2, 0, -9, 3, 1, 'C', 'c')])
W[13] = ('w_stiletto', [pole(-3, 0, 1, 0, 'g', 'b'), disc(1, 0, 1.5, 'G'), blade(2, 0, 19, 0, 1, 'w', 'l')])
W[14] = ('w_claws', [disc(1, 0, 3, 'p', 'P'), blade(3, -3, 13, -7, 1, 'P', 'p'), blade(3, 0, 14, 0, 1, 'P', 'p'), blade(3, 3, 13, 7, 1, 'P', 'p')])
W[15] = ('w_tonfa', [pole(-6, -1, 13, -1, 'B', 'b'), pole(1, -1, 1, 5, 'y', 'b'), disc(13, -1, 1, 'd')])
W[16] = ('w_gauntlet', [poly([(-2, -5), (7, -5), (8, 5), (-2, 5)], 'g', 'G'), ('line', 7, -4, 9, -4, 'm'), ('line', 8, -1, 10, -1, 'm'), ('line', 8, 2, 10, 2, 'm'), ('line', 7, 5, 9, 5, 'm')])

# ---- cuerpo a cuerpo medio
W[17] = ('w_lance', [pole(-8, 0, 24, 0), poly([(24, -2), (33, 0), (24, 2)], 'l', 'm'), ('line', 23, -3, 23, 3, 'g')])
W[18] = ('w_halberd', [pole(-8, 0, 23, 0), poly([(17, -9), (25, -6), (25, 0), (17, 0)], 'm', 'l'), poly([(23, 0), (32, 0), (23, 2)], 'l', 'm')])
W[19] = ('w_scythe', [pole(-8, 0, 19, 0, 'b', 'e'), poly([(19, 0), (22, -7), (30, -9), (32, -6), (25, -5), (22, 0)], 'P', 'p')])
W[20] = ('w_whip', [pole(-3, 0, 3, 0, 'b', 'e'), ('curve', [(3, 0), (10, -4), (18, 3), (25, -3), (32, 0)], 'B')])
W[21] = ('w_chain', [pole(-3, 0, 2, 0, 'b', 'e'), dots(3, 0, 19, 0, 6, 'd'), poly([(19, 0), (24, -4), (31, 0), (24, 4)], 'l', 'm')])
W[22] = ('w_shortsword', [pole(-3, 0, 2, 0), disc(-3, 0, 1.5, 'G'), ('line', 2, -3, 2, 3, 'g'), blade(3, 0, 19, 0, 2)])
W[23] = ('w_warhammer', [pole(-6, 0, 20, 0), poly([(16, -7), (25, -7), (25, 7), (16, 7)], 'd', 'm'), poly([(25, -6), (27, -6), (27, 6), (25, 6)], 'l')])

# ---- a distancia (reserva)
W[24] = ('w_tdagger', [pole(-3, 0, 1, 0), disc(-4, 0, 1.2, 'G'), ('line', 1, -2, 1, 2, 'g'), blade(2, 0, 14, 0, 1)])
W[25] = ('w_shuriken', [poly([(5, -6), (7, -1), (12, 0), (7, 1), (5, 6), (3, 1), (-2, 0), (3, -1)], 'm', 'l'), disc(5, 0, 1.2, 'd')])
W[26] = ('w_alchbomb', [disc(5, 1, 5, 'o', 'O'), disc(3, -1, 1, 'Y'), pole(5, -5, 5, -8, 'l', 'm'), pole(4, -9, 6, -9, 'b', 'b')])
W[27] = ('w_stickybomb', [disc(5, 0, 5, 'c', 'C'), dots(0, -5, 10, 5, 3, 'w'), ('line', 5, -5, 5, -8, 'd'), disc(5, -9, 1.2, 'R')])

# ---- magicas
W[28] = ('w_elemwand', [pole(-3, 0, 12, 0, 'y', 'b'), disc(14, -3, 2, 'O', 'Y'), disc(15, 0, 2, 'C', 'w'), disc(14, 3, 2, 'Y', 'w')])
W[29] = ('w_firewand', [pole(-3, 0, 12, 0, 'r', 'e'), poly([(12, 0), (15, -4), (19, 0), (15, 4)], 'O', 'o'), disc(15, 0, 1.5, 'Y')])
W[30] = ('w_icewand', [pole(-3, 0, 12, 0, 'c', 'e'), poly([(12, 0), (16, -5), (21, 0), (16, 5)], 'C', 'c'), ('line', 14, 0, 20, 0, 'w')])
W[31] = ('w_stormwand', [pole(-3, 0, 11, 0, 'g', 'b'), ('line', 11, 0, 14, -4, 'Y'), ('line', 14, -4, 15, 1, 'Y'), ('line', 15, 1, 19, -3, 'Y'), disc(14, 0, 1, 'w')])
W[32] = ('w_darkorb', [disc(6, 0, 5, 'q', 'p'), disc(5, -1, 2, 'P'), ('ring', 6, 0, 5, 6.3, 'P')])
W[33] = ('w_venomcat', [disc(6, 2, 4.5, 'n', 'N'), pole(6, -3, 6, -6, 'l', 'm'), pole(5, -7, 7, -7, 'b', 'b'), disc(4, 1, 1, 'T'), disc(8, 3, 1, 'T')])
W[34] = ('w_bloodscepter', [pole(-3, 0, 14, 0, 'r', 'e'), disc(16, 0, 3, 'R', 'w'), ('line', 16, -4, 16, -6, 'r'), ('line', 16, 4, 16, 6, 'r'), ('line', 19, 0, 21, 0, 'r')])
W[35] = ('w_crystal', [poly([(4, 0), (9, -6), (14, 0), (9, 6)], 'P', 'p'), poly([(4, 0), (9, -6), (9, 0)], 'w'), ('line', -2, 0, 4, 0, 'y')])
W[36] = ('w_talisman', [poly([(2, -6), (11, -6), (11, 6), (2, 6)], 'Y', 'y'), ('line', 4, -3, 9, -3, 'R'), ('line', 6, -3, 6, 4, 'R'), ('line', 4, 1, 9, 1, 'R'), ('line', 7, 3, 9, 4, 'R')])


# ------------------------------------------------------------------ rasterizado
def _pt(x, y, ox, oy, s, c, sn):
    return ox + (x * c - y * sn) * s, oy + (x * sn + y * c) * s


def _inpoly(px, py, pts):
    n = len(pts); inside = False
    j = n - 1
    for i in range(n):
        xi, yi = pts[i]; xj, yj = pts[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi + 1e-9) + xi:
            inside = not inside
        j = i
    return inside


def render(parts, w, h, ox, oy, s, ang):
    cv = G.Cv(w, h)
    c, sn = math.cos(ang), math.sin(ang)

    def T(x, y):
        return _pt(x, y, ox, oy, s, c, sn)

    for p in parts:
        k = p[0]
        if k == 'pole':
            _, x0, y0, x1, y1, c1, c2 = p
            ax, ay = T(x0, y0); bx, by = T(x1, y1)
            cv.line(ax, ay, bx, by, c1)
            if s >= 1:
                nx, ny = -(by - ay), (bx - ax); L = math.hypot(nx, ny) or 1
                cv.line(ax + nx / L, ay + ny / L, bx + nx / L, by + ny / L, c2)
        elif k == 'line':
            _, x0, y0, x1, y1, col = p
            ax, ay = T(x0, y0); bx, by = T(x1, y1)
            cv.line(ax, ay, bx, by, col)
        elif k == 'blade':
            _, x0, y0, x1, y1, bw, col, edge = p
            ax, ay = T(x0, y0); bx, by = T(x1, y1)
            L = math.hypot(bx - ax, by - ay) or 1
            nx, ny = -(by - ay) / L, (bx - ax) / L
            cv.line(ax, ay, bx, by, col)
            if bw >= 2 and s >= 1:
                cv.line(ax + nx, ay + ny, bx + nx, by + ny, edge)
                cv.line(ax - nx, ay - ny, bx - nx, by - ny, col)
            cv.set(bx, by, 'w')
        elif k == 'disc':
            _, cx, cy, r, col, hl = p
            px, py = T(cx, cy)
            rr = max(0.9, r * s) if s < 1 else r
            cv.disc(px, py, rr, col)
            if hl and rr >= 2:
                cv.set(px - rr * 0.35, py - rr * 0.35, hl); cv.set(px - rr * 0.35 + 1, py - rr * 0.35, hl)
        elif k == 'ring':
            _, cx, cy, r0, r1, col = p
            px, py = T(cx, cy)
            cv.ring(px, py, r0 * s if s < 1 else r0, r1 * s if s < 1 else r1, col)
        elif k == 'arc':
            _, cx, cy, r, col = p
            for i in range(-20, 21):
                a = i / 20 * 1.25
                x, y = cx + math.cos(a) * r * 0.55 + 2, cy + math.sin(a) * r
                px, py = T(x, y)
                cv.set(px, py, col)
        elif k == 'poly':
            _, pts, col, edge = p
            tp = [T(x, y) for x, y in pts]
            xs = [q[0] for q in tp]; ys = [q[1] for q in tp]
            for yy in range(int(min(ys)) - 1, int(max(ys)) + 2):
                for xx in range(int(min(xs)) - 1, int(max(xs)) + 2):
                    if _inpoly(xx + 0.0, yy + 0.0, tp):
                        cv.set(xx, yy, col)
            if edge and s >= 1:
                for i in range(len(tp)):
                    a = tp[i]; b = tp[(i + 1) % len(tp)]
                    cv.line(a[0], a[1], b[0], b[1], edge)
        elif k == 'dots':
            _, x0, y0, x1, y1, n, col = p
            for i in range(n):
                f = i / max(1, n - 1)
                px, py = T(x0 + (x1 - x0) * f, y0 + (y1 - y0) * f)
                cv.set(px, py, col)
        elif k == 'curve':
            _, pts, col = p
            tp = [T(x, y) for x, y in pts]
            for i in range(len(tp) - 1):
                cv.line(tp[i][0], tp[i][1], tp[i + 1][0], tp[i + 1][1], col)
    cv.outline()
    return cv


def bbox(parts):
    xs, ys = [], []
    for p in parts:
        k = p[0]
        if k in ('pole', 'line', 'blade'):
            xs += [p[1], p[3]]; ys += [p[2], p[4]]
        elif k in ('disc', 'ring'):
            r = p[3] if k == 'disc' else p[4]
            xs += [p[1] - r, p[1] + r]; ys += [p[2] - r, p[2] + r]
        elif k == 'poly':
            for x, y in p[1]:
                xs.append(x); ys.append(y)
        elif k == 'curve':
            for x, y in p[1]:
                xs.append(x); ys.append(y)
        elif k == 'arc':
            xs += [p[1], p[1] + p[3]]; ys += [p[2] - p[3], p[2] + p[3]]
        elif k == 'dots':
            xs += [p[1], p[3]]; ys += [p[2], p[4]]
    return min(xs), min(ys), max(xs), max(ys)


def hold(parts):
    return render(parts, 48, 16, 10, 8, 1.0, 0.0).image()


def icon(parts):
    x0, y0, x1, y1 = bbox(parts)
    ang = -math.radians(40)
    s = 0.5
    # centrar el rectangulo ya rotado en 16x16
    c, sn = math.cos(ang), math.sin(ang)
    corners = [(x, y) for x in (x0, x1) for y in (y0, y1)]
    rp = [((x * c - y * sn) * s, (x * sn + y * c) * s) for x, y in corners]
    mx = (min(q[0] for q in rp) + max(q[0] for q in rp)) / 2
    my = (min(q[1] for q in rp) + max(q[1] for q in rp)) / 2
    return render(parts, 16, 16, 8 - mx, 8 - my, s, ang).image()


def main():
    prev = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
    n = max(W) + 1
    names = [''] * n
    sheet = Image.new('RGBA', (48 * 4, 16 * ((n + 3) // 4)), (0, 0, 0, 0))
    icons = {}
    for i in range(1, n):
        nm, parts = W[i]
        names[i] = nm
        sheet.paste(hold(parts), ((i % 4) * 48, (i // 4) * 16))
        icons[nm] = icon(parts)
    sheet.save(os.path.join(ROOT, 'sprites', 'wpn_hold.png'))
    json.dump({'cell': [48, 16], 'cols': 4, 'grip': [10, 8], 'names': names}, open(os.path.join(ROOT, 'sprites', 'wpn_hold.json'), 'w'), ensure_ascii=False)
    # iconos nuevos (no se tocan los existentes)
    ui = os.path.join(ROOT, 'ui')
    ij = json.load(open(os.path.join(ui, 'icons.json')))
    im = Image.open(os.path.join(ui, 'icons.png')).convert('RGBA')
    new = [nm for nm in icons if nm not in ij['names']]
    if new:
        total = len(ij['names']) + len(new)
        rows = (total + ij['cols'] - 1) // ij['cols']
        if rows * 16 > im.height:
            big = Image.new('RGBA', (im.width, rows * 16), (0, 0, 0, 0)); big.paste(im, (0, 0)); im = big
        for nm in new:
            k = len(ij['names']); ij['names'].append(nm)
            im.paste(icons[nm], ((k % ij['cols']) * 16, (k // ij['cols']) * 16))
        im.save(os.path.join(ui, 'icons.png'))
        json.dump(ij, open(os.path.join(ui, 'icons.json'), 'w'), ensure_ascii=False)
    if prev:
        S = 4
        out = Image.new('RGBA', (4 * 48 * S, ((n + 3) // 4) * (16 + 16) * S), (50, 50, 60, 255))
        for i in range(1, n):
            h = hold(W[i][1]); ic = icons[W[i][0]]
            gx, gy = (i % 4) * 48 * S, (i // 4) * 32 * S
            out.alpha_composite(h.resize((48 * S, 16 * S), Image.NEAREST), (gx, gy))
            out.alpha_composite(ic.resize((16 * S, 16 * S), Image.NEAREST), (gx, gy + 16 * S))
        out.convert('RGB').save(prev)


if __name__ == '__main__':
    main()
