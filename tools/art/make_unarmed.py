#!/usr/bin/env python3
"""Genera, para las 10 clases, las filas "sin arma" (idle/run/jump/fall) y la capa de la espada guardada a la espalda.

El arma principal esta dibujada dentro de cada fotograma de pl_<clase>.png. Para poder mostrar la espada a la espalda y un arma 2ª en la mano
sin duplicados, este script SOLO AÑADE filas al final de cada hoja (las 14 originales no se tocan):
  fila 14-17: idle_u run_u jump_u fall_u  (personaje sin el arma de la clase; la mano queda vacia)
  fila 18-21: idle_s run_s jump_s fall_s  (capa trasera: la espada guardada a la espalda, alineada con cada fotograma)
y añade al JSON las animaciones y "hand" (anclaje de la mano por fotograma, px en la celda) para colocar el arma 2ª.
Metodo: cada clase define regiones (corte vertical o capsula) donde vive el arma; los pixeles del arma se borran y, si estaban rodeados por el cuerpo
(hoja que cruza el torso), se rellenan con el color vecino (relleno por vecindad); los que sobresalen quedan transparentes.
Idempotente: siempre parte de las filas 0-3 originales. Uso: python3 tools/art/make_unarmed.py [--preview /tmp/p.png] [--only steel]
"""
import json, math, os, sys
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Shared', 'assets', 'sprites')
CW, CH = 64, 48
SRC_ROWS = {'idle': 0, 'run': 1, 'jump': 2, 'fall': 3}
NEW_ROW = {'idle': 14, 'run': 15, 'jump': 16, 'fall': 17}
STOW_ROW = {'idle': 18, 'run': 19, 'jump': 20, 'fall': 21}
TOTAL_ROWS = 22

# reglas por clase y grupo de filas: A = idle/run, B = jump/fall.  ('cut', x0, y0, y1) = x>=x0 con y0<=y<=y1; ('cap', x0, y0, x1, y1, r)
# 'hand' = anclaje por defecto (A, B) por si no se puede deducir.  'self' = el arma ya esta a la espalda (no se dibuja capa).
DEF = {
    'steel':   {'A': [('cut', 43, 0, 47)], 'B': [('cut', 43, 0, 47)], 'hand': ((42, 28), (42, 22))},
    'storm':   {'A': [('cut', 42, 0, 47)], 'B': [('cut', 42, 0, 47)], 'hand': ((41, 25), (41, 20))},
    'frost':   {'A': [('cut', 40, 22, 47)], 'B': [('cut', 42, 0, 47)], 'hand': ((40, 27), (42, 20))},
    'astral':  {'A': [('cap', 33, 31, 60, 40, 4.5), ('cut', 38, 26, 47)], 'B': [('cut', 42, 0, 47)], 'hand': ((36, 31), (42, 22))},
    'blood':   {'A': [('cut', 36, 27, 47)], 'B': [('cut', 41, 0, 47)], 'hand': ((36, 27), (41, 20))},
    'earth':   {'A': [('cut', 38, 28, 47)], 'B': [('cut', 44, 0, 47)], 'hand': ((38, 28), (44, 22)), 'self': True},
    'flame':   {'A': [], 'B': [], 'hand': ((41, 26), (40, 22)), 'self': True},
    'paladin': {'A': [('cap', 26, 28, 60, 43, 2.6), ('cut', 40, 30, 47)], 'B': [('cut', 42, 0, 47)], 'hand': ((34, 31), (42, 21))},
    'shadow':  {'A': [('cut', 38, 20, 35)], 'B': [('cut', 40, 0, 47)], 'hand': ((38, 28), (40, 22))},
    'verdant': {'A': [('cap', 26, 29, 60, 43, 3.0), ('cut', 40, 30, 47)], 'B': [('cut', 40, 16, 32)], 'hand': ((35, 33), (40, 24))},
}


def seg_dist(px, py, x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - x0) * dx + (py - y0) * dy) / L))
    return math.hypot(px - (x0 + t * dx), py - (y0 + t * dy))


def erase_mask(rules, fr):
    M = set()
    for y in range(CH):
        for x in range(CW):
            if fr.getpixel((x, y))[3] == 0:
                continue
            for r in rules:
                if r[0] == 'cut' and x >= r[1] and r[2] <= y <= r[3]:
                    M.add((x, y)); break
                if r[0] == 'cap' and seg_dist(x, y, r[1], r[2], r[3], r[4]) <= r[5]:
                    M.add((x, y)); break
    return M


def unarm(fr, M):
    out = fr.copy()
    px = fr.load(); o = out.load()
    R = {(x, y) for y in range(CH) for x in range(CW) if px[x, y][3] > 0 and (x, y) not in M}
    filled = {}
    for passn in range(2):
        for (x, y) in sorted(M):
            if (x, y) in filled:
                continue
            found = {}
            for name, dx, dy in (('l', -1, 0), ('r', 1, 0), ('u', 0, -1), ('d', 0, 1)):
                for k in range(1, 4):
                    q = (x + dx * k, y + dy * k)
                    if q in R or q in filled:
                        found[name] = (k, q); break
            inside = ('l' in found and 'r' in found) or ('u' in found and 'd' in found) or len(found) >= 3
            if inside:
                best = min(found.values(), key=lambda v: v[0])[1]
                filled[(x, y)] = px[best] if best in R else filled[best]
        # (segunda pasada deja que el relleno alcance bandas mas gruesas)
    for (x, y) in M:
        if (x, y) in filled:
            o[x, y] = filled[(x, y)]
        else:
            o[x, y] = (0, 0, 0, 0)
    return out


def hand_of(M, default):
    if not M:
        return default
    # extremo de la zona borrada mas cercano al cuerpo: el mas a la izquierda; entre empates, el mas cercano a la mano por defecto
    xs = sorted(M, key=lambda p: (p[0] - default[0]) ** 2 + (p[1] - default[1]) ** 2)
    near = xs[:3]
    hx = sum(p[0] for p in near) / len(near); hy = sum(p[1] for p in near) / len(near)
    if math.hypot(hx - default[0], hy - default[1]) > 8:
        return default
    return (round(hx), round(hy))


def build_stow(weapon, body, hilt_ref):
    """Capa de la espada a la espalda: arma rotada (hilo arriba-atras, punta abajo-delante) con la empuñadura sobre el hombro de este fotograma."""
    out = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    if not weapon:
        return out
    pts = list(weapon.keys())
    n = len(pts)
    mx = sum(p[0] for p in pts) / n; my = sum(p[1] for p in pts) / n
    sxx = sum((p[0] - mx) ** 2 for p in pts); syy = sum((p[1] - my) ** 2 for p in pts); sxy = sum((p[0] - mx) * (p[1] - my) for p in pts)
    ang = 0.5 * math.atan2(2 * sxy, sxx - syy)
    ux, uy = math.cos(ang), math.sin(ang)
    proj = [((p[0] - mx) * ux + (p[1] - my) * uy, p) for p in pts]
    a = min(proj)[1]; b = max(proj)[1]
    hilt, tip = (a, b) if a[0] < b[0] else (b, a)
    th0 = math.atan2(tip[1] - hilt[1], tip[0] - hilt[0])
    # cabeza del cuerpo: borde superior y centro horizontal de las 10 primeras filas
    ys = [p[1] for p in body]
    top = min(ys)
    head = [p for p in body if p[1] < top + 9]
    hcx = sum(p[0] for p in head) / len(head)
    target = (hcx + 3, top + 4)
    phi = math.radians(148)                     # empuñadura sobre el hombro delantero, punta asomando por la espalda (abajo-izquierda)
    d = phi - th0
    c, s = math.cos(d), math.sin(d)
    L = math.hypot(tip[0] - hilt[0], tip[1] - hilt[1])
    maxL = 27.0
    k = min(1.0, maxL / max(1.0, L))             # espadas muy largas: se acortan para que quepan en la celda
    # muestreo inverso (vecino mas cercano) para no desenfocar
    R = int(max(L, 12) * 1.2) + 4
    for yy in range(-R, R + 1):
        for xx in range(-R, R + 1):
            # punto destino relativo a la empuñadura -> origen
            ox_, oy_ = xx / k, yy / k
            sx = ox_ * c + oy_ * s; sy = -ox_ * s + oy_ * c
            q = (int(round(hilt[0] + sx)), int(round(hilt[1] + sy)))
            if q in weapon:
                tx, ty = int(round(target[0] + xx)), int(round(target[1] + yy))
                if 0 <= tx < CW and 0 <= ty < CH:
                    out.putpixel((tx, ty), weapon[q])
    return out


def process(cls, preview_rows):
    path = os.path.join(ROOT, 'pl_' + cls)
    img = Image.open(path + '.png').convert('RGBA')
    js = json.load(open(path + '.json'))
    base = img.crop((0, 0, img.width, 14 * CH))
    sheet = Image.new('RGBA', (img.width, TOTAL_ROWS * CH), (0, 0, 0, 0))
    sheet.paste(base, (0, 0))
    d = DEF[cls]
    hands = {}
    prev = []
    fr0 = base.crop((0, 0, CW, CH))
    canon = {p: fr0.getpixel(p) for p in erase_mask(d['A'], fr0)}     # la misma espada guardada en todos los fotogramas (forma coherente)
    for an, row in SRC_ROWS.items():
        n = js['anims'][an]['n']
        grp = 'A' if an in ('idle', 'run') else 'B'
        rules = d[grp]
        hdef = d['hand'][0 if grp == 'A' else 1]
        hl = []
        for f in range(n):
            fr = base.crop((f * CW, row * CH, f * CW + CW, row * CH + CH))
            M = erase_mask(rules, fr)
            ua = unarm(fr, M)
            sheet.paste(ua, (f * CW, NEW_ROW[an] * CH))
            body = [(x, y) for y in range(CH) for x in range(CW) if ua.getpixel((x, y))[3] > 0]
            weapon = canon
            stow = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)) if d.get('self') else build_stow(weapon, body, hdef)
            sheet.paste(stow, (f * CW, STOW_ROW[an] * CH))
            hl.append(list(hand_of(M, hdef)))
            if f in preview_rows.get(an, []):
                prev.append((cls, an, f, fr, ua, stow))
        hands[an] = hl
    sheet.save(path + '.png')
    for an, row in SRC_ROWS.items():
        a = dict(js['anims'][an])
        for k in ('hit', 'box', 'rel', 'muzzle', 'smear', 'ft'):
            a.pop(k, None)
        b = dict(a); b['row'] = NEW_ROW[an]; b['hand'] = hands[an]
        js['anims'][an + '_u'] = b
        c = dict(a); c['row'] = STOW_ROW[an]
        js['anims'][an + '_s'] = c
    json.dump(js, open(path + '.json', 'w'), separators=(',', ':'))
    return prev


def main():
    args = sys.argv[1:]
    only = args[args.index('--only') + 1] if '--only' in args else None
    pv = args[args.index('--preview') + 1] if '--preview' in args else None
    rows = {'idle': [0, 3], 'run': [0, 4], 'jump': [1], 'fall': [0]}
    allp = []
    for cls in DEF:
        if only and cls != only:
            continue
        allp += process(cls, rows)
    if pv:
        S = 3
        cols = 6
        by = {}
        for p in allp:
            by.setdefault(p[0], []).append(p)
        H = len(by) * CH * S
        im = Image.new('RGBA', (cols * CW * S, H), (50, 50, 60, 255))
        for i, (c, lst) in enumerate(by.items()):
            for j, (cls, an, f, fr, ua, stow) in enumerate(lst[:cols]):
                comp = Image.new('RGBA', (CW, CH), (50, 50, 60, 255))
                comp.alpha_composite(stow); comp.alpha_composite(ua)
                im.paste(comp.resize((CW * S, CH * S), Image.NEAREST), (j * CW * S, i * CH * S))
        im.convert('RGB').save(pv)


if __name__ == '__main__':
    main()
