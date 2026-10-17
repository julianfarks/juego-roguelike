#!/usr/bin/env python3
"""Anade a los atlas font_s / font_b los caracteres franceses que faltan (a, e, i, o, u con grave/circunflejo/dieresis, ç, Ç, ...).
Se construyen sobre el glifo base con acentos de pixel-art coherentes con los de 'é'/'É'. Idempotente. Œ/œ se escriben 'OE'/'oe'."""
import json, os
from PIL import Image
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'app', 'src', 'main', 'assets', 'font')
BASES = {'À': ('A', 'grave'), 'Â': ('A', 'circ'), 'Ä': ('A', 'diae'), 'È': ('E', 'grave'), 'Ê': ('E', 'circ'), 'Ë': ('E', 'diae'),
         'Î': ('I', 'circ'), 'Ï': ('I', 'diae'), 'Ô': ('O', 'circ'), 'Ù': ('U', 'grave'), 'Û': ('U', 'circ'), 'Ç': ('C', 'cedil'),
         'à': ('a', 'grave'), 'â': ('a', 'circ'), 'ä': ('a', 'diae'), 'è': ('e', 'grave'), 'ê': ('e', 'circ'), 'ë': ('e', 'diae'),
         'î': ('i', 'circ'), 'ï': ('i', 'diae'), 'ô': ('o', 'circ'), 'ù': ('u', 'grave'), 'û': ('u', 'circ'), 'ç': ('c', 'cedil')}

def build(name, big):
    jp = os.path.join(A, name + '.json'); j = json.load(open(jp, encoding='utf8'))
    im = Image.open(os.path.join(A, name + '.png')).convert('RGBA')
    cw, ch, cols = j['cellW'], j['cellH'], j['cols']; chars = j['chars']; widths = list(j['widths'])
    FILL = (235, 235, 235, 255) if big else (255, 255, 255, 255); OUT = (22, 12, 28, 255)
    def cell(c):
        i = chars.index(c); x0, y0 = (i % cols) * cw, (i // cols) * ch
        return im.crop((x0, y0, x0 + cw, y0 + ch)), widths[i]
    new = []
    for g, (b, kind) in BASES.items():
        if g in chars: continue
        src, w = cell(b)
        px = src.load()
        fill = {(x, y) for y in range(ch) for x in range(cw) if px[x, y][3] and sum(px[x, y][:3]) > 600}
        if b == 'i':   # sin punto
            fill = {p for p in fill if p[1] >= (6 if big else 3)}
        t = min(y for x, y in fill)
        cap = b.isupper()
        c = (w // 2 - (1 if (big and not cap) else 0)) if kind != 'cedil' else w // 2
        if b == 'i': c = w // 2 - (0 if big else 0)
        acc = set()
        if kind == 'cedil':
            bot = max(y for x, y in fill)
            acc = {(c, bot + 1), (c - 1, bot + 2)} if not big else {(c, bot + 1), (c, bot + 2), (c - 1, bot + 3)}
        elif cap and not big:      # una sola fila (como en 'É')
            acc = {'grave': {(c - 1, 0)}, 'circ': {(c, 0)}, 'diae': {(c - 1, 0), (c + 1, 0)}}[kind]
        else:
            r1, r0 = (t - 2, t - 3) if (cap and big) else (t - 1, t - 2)   # fila baja / fila alta
            acc = {'grave': {(c - 1, r0), (c, r1)}, 'circ': {(c, r0), (c - 1, r1), (c + 1, r1)}, 'diae': {(c - 1, r0), (c + 1, r0), (c - 1, r1), (c + 1, r1)} if big else {(c - 1, r0), (c + 1, r0)}}[kind]
        if big and kind == 'diae' and not cap: acc = {(c - 1, t - 3), (c + 1, t - 3), (c - 1, t - 2), (c + 1, t - 2)}
        fill |= {p for p in acc if 0 <= p[0] < cw and 0 <= p[1] < ch}
        out = Image.new('RGBA', (cw, ch), (0, 0, 0, 0)); o = out.load()
        for (x, y) in fill: o[x, y] = FILL
        for (x, y) in list(fill):
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < cw and 0 <= yy < ch and (xx, yy) not in fill: o[xx, yy] = OUT
        new.append((g, out, w))
    if not new: return 0
    total = len(chars) + len(new); rows = (total + cols - 1) // cols
    atlas = Image.new('RGBA', (cols * cw, rows * ch), (0, 0, 0, 0)); atlas.paste(im, (0, 0))
    for k, (g, out, w) in enumerate(new):
        i = len(chars) + k; atlas.paste(out, ((i % cols) * cw, (i // cols) * ch)); widths.append(w)
    j['chars'] = chars + ''.join(g for g, _, _ in new); j['widths'] = widths
    atlas.save(os.path.join(A, name + '.png'), optimize=True)
    json.dump(j, open(jp, 'w', encoding='utf8'), ensure_ascii=False)
    return len(new)

for n, big in (('font_s', False), ('font_b', True)): print(n, build(n, big))
