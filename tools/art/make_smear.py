#!/usr/bin/env python3
"""Smear frames pixel-art para las hojas pl_*.png (10 clases, mismo formato 64x48 x 10 columnas).

Inserta UN fotograma de smear en ataque1/2/3, ataque aereo y esquiva (justo antes del contacto / en la aceleracion):
  - cuerpo estirado a lo largo del movimiento (vecino mas cercano, sin desenfoque), anclado a los pies;
  - estela de la pose anterior en 2 tonos de la propia paleta del sprite (tramado en damero, sin alfa intermedio nuevo);
  - 3 lineas de velocidad de 1 px.
Despues escribe en el JSON: n+1, hit desplazado, "ft" (peso de duracion por fotograma: anticipacion lenta, smear 1 tic, recuperacion con peso)
y "smear" (indice del fotograma smear). El area de golpe (box) y los fotogramas de golpe NO cambian: el danio sigue en la misma pose.
Idempotente: si el JSON ya tiene "smear" en la animacion, se omite.
"""
import json, glob, os, sys
from PIL import Image
from collections import Counter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Shared', 'assets', 'sprites')
CW, CH = 64, 48

# anim -> (indice de insercion relativo: 'h0' = antes del primer fotograma de golpe, o entero, pesos tras insertar, sx, sy)
PLAN = {
    'attack1': ('h0', [1.1, 1.2, 0.45, 0.7, 0.8, 1.0, 1.3], 1.22, 0.96),
    'attack2': ('h0', [1.1, 1.2, 0.45, 0.7, 0.8, 1.0, 1.3], 1.22, 0.96),
    'attack3': ('h0', [1.3, 1.5, 1.2, 0.45, 0.8, 1.0, 1.3, 1.7], 1.32, 0.94),
    'airatk':  ('h0', [1.2, 0.45, 0.8, 0.8, 0.9, 1.4], 1.20, 0.96),
    'skill':   ('rel', [1.2, 1.3, 1.1, 0.4, 0.9, 0.9, 1.0, 1.4], 1.20, 0.97),
    'hurt':    ('imp', [0.5, 0.8, 1.6], 0.86, 1.08),
    'roll':    (1,    [0.7, 0.45, 0.9, 1.0, 1.0, 1.1, 1.2, 1.5], 1.36, 0.88),
}

def stretch(im, sx, sy, px=32, py=44):
    out = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    src, dst = im.load(), out.load()
    for y in range(CH):
        for x in range(CW):
            xs = int(round(px + (x - px) / sx)); ys = int(round(py + (y - py) / sy))
            if 0 <= xs < CW and 0 <= ys < CH:
                dst[x, y] = src[xs, ys]
    return out

def lum(c): return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]

def palette_tones(im):
    px = [p for p in im.getdata() if p[3] == 255]
    if not px: return (200, 200, 210, 255), (110, 110, 130, 255)
    cnt = Counter(px)
    cols = sorted(cnt, key=lum)
    hi = [c for c in cols if lum(c) > 150] or cols[-3:]
    mid = [c for c in cols if 70 < lum(c) <= 150] or cols
    top = max(hi, key=lambda c: cnt[c]); m = max(mid, key=lambda c: cnt[c])
    return (top[0], top[1], top[2], 255), (m[0], m[1], m[2], 255)

def silhouette(im, color, shift, dither):
    out = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); s, d = im.load(), out.load()
    for y in range(CH):
        for x in range(CW):
            if s[x, y][3] >= 200:
                nx = x - shift
                if 0 <= nx < CW and (not dither or (nx + y) % 2 == 0): d[nx, y] = color
    return out

def make_smear(prev, cur, sx, sy):
    hi, mid = palette_tones(cur)
    body = stretch(cur, sx, sy)
    out = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    # eco de la pose anterior: silueta tramada y rala (1 de cada 3 px), nunca una mancha solida
    ghost = silhouette(prev, mid, 7, True); g, o = ghost.load(), out.load()
    for y in range(CH):
        for x in range(CW):
            if g[x, y][3] and (x + 2 * y) % 3 == 0: o[x, y] = g[x, y]
    b = body.load()
    for y in range(CH):                       # el cuerpo manda; los arcos semitransparentes no se mezclan con el eco (evita colores nuevos)
        for x in range(CW):
            if b[x, y][3] >= 200 or (b[x, y][3] > 0 and o[x, y][3] == 0): o[x, y] = b[x, y]
    # estelas de velocidad: una linea de 1 px por cada 2 filas, saliendo del borde izquierdo de la silueta (el sprite mira a la derecha)
    for y in range(12, 46, 2):
        xs = [x for x in range(CW) if b[x, y][3] >= 200]
        if not xs: continue
        x0 = min(xs); ln = 4 + (y * 7) % 10
        col = hi if ln >= 9 else mid
        for x in range(max(0, x0 - ln), x0):
            if o[x, y][3] == 0 and (x + y) % 4 != 1: o[x, y] = col
    return out

def impact_frame(cur, sx, sy):
    """Pose de impacto recibido: comprimido, estirado en vertical, desplazado 2 px hacia atras y con contorno de 1 px en el tono mas claro del sprite."""
    hi, _ = palette_tones(cur)
    b = stretch(cur, sx, sy); out = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); o, s_ = out.load(), b.load()
    for y in range(CH):
        for x in range(CW):
            if s_[x, y][3] >= 200 and x - 2 >= 0: o[x - 2, y] = s_[x, y]
    edge = []
    for y in range(CH):
        for x in range(CW):
            if o[x, y][3] == 0 and any(0 <= x + dx < CW and 0 <= y + dy < CH and o[x + dx, y + dy][3] == 255 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))): edge.append((x, y))
    for x, y in edge: o[x, y] = hi
    return out

def process(png):
    jpath = png[:-4] + '.json'
    d = json.load(open(jpath)); im = Image.open(png).convert('RGBA')
    changed = False
    for name, (ins, weights, sx, sy) in PLAN.items():
        a = d['anims'].get(name)
        if not a or 'smear' in a: continue
        n, row = a['n'], a['row']
        if n + 1 > im.size[0] // CW: print('sin espacio', png, name); continue
        frames = [im.crop((i * CW, row * CH, (i + 1) * CW, (row + 1) * CH)) for i in range(n)]
        pos = a['hit'][0] if ins == 'h0' else (a['rel'] if ins == 'rel' else (0 if ins == 'imp' else ins))
        sm = impact_frame(frames[0], sx, sy) if ins == 'imp' else make_smear(frames[pos - 1], frames[pos], sx, sy)
        frames.insert(pos, sm)
        # limpiar la fila y reescribir
        im.paste((0, 0, 0, 0), (0, row * CH, im.size[0], (row + 1) * CH))
        for i, f in enumerate(frames): im.paste(f, (i * CW, row * CH))
        a['n'] = n + 1
        if 'hit' in a: a['hit'] = [a['hit'][0] + 1, a['hit'][1] + 1]
        if 'rel' in a and a['rel'] >= pos: a['rel'] += 1
        a['smear'] = pos
        a['ft'] = weights
        assert len(weights) == a['n'], (name, len(weights), a['n'])
        changed = True
    if changed:
        im.save(png); json.dump(d, open(jpath, 'w'), indent=1)
    return changed

if __name__ == '__main__':
    for png in sorted(glob.glob(os.path.join(ROOT, 'pl_*.png'))):
        print(os.path.basename(png), 'ok' if process(png) else 'sin cambios')
