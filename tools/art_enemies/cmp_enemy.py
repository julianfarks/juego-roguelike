#!/usr/bin/env python3
"""Comparacion antes (HEAD) / despues (disco) de enemigos a escala de juego (x3) y ampliada (x6).
Uso: cmp_enemy.py nombre [nombre...] ; salida docs/capturas_arte/enemigos_<primero>_..."""
import io, json, os, subprocess, sys
from PIL import Image
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
BG = (34, 28, 48, 255)
names = sys.argv[1:]
def load(rel, head):
    if head:
        return Image.open(io.BytesIO(subprocess.run(['git', 'show', 'HEAD:' + rel], cwd=ROOT, capture_output=True, check=True).stdout)).convert('RGBA')
    return Image.open(os.path.join(ROOT, rel)).convert('RGBA')
pick = ['idle', 'walk', 'windup', 'attack', 'hurt', 'death']
rows = []
for n in names:
    rel = 'Shared/assets/sprites/en_%s.png' % n
    d = json.load(open(os.path.join(ROOT, rel[:-4] + '.json')))
    cw, ch = d['cell']
    old, new = load(rel, True), load(rel, False)
    for key in ('idle', 'attack', 'death'):
        a = d['anims'][key]; f = {'idle': 0, 'attack': a['n'] // 2, 'death': min(2, a['n'] - 1)}[key]
        rows.append((old, new, a['row'], f, cw, ch))
S = 5
W = Image.new('RGB', (max(r[4] for r in rows) * S * 2 + 8, sum(r[5] for r in rows) * S + 3 * len(rows)), (0, 0, 0))
y = 0
for old, new, row, f, cw, ch in rows:
    for k, im in enumerate((old, new)):
        t = Image.new('RGBA', (cw, ch), BG); t.alpha_composite(im.crop((f * cw, row * ch, f * cw + cw, row * ch + ch)))
        W.paste(t.resize((cw * S, ch * S), Image.NEAREST).convert('RGB'), (k * (cw * S + 8), y))
    y += ch * S + 3
out = os.path.join(ROOT, 'docs/capturas_arte/enemigos_%s_antes_izq_despues_der.png' % '_'.join(names[:3]))
W.save(out); print(out)
