#!/usr/bin/env python3
"""Comparacion antes (HEAD) / despues (disco) de una clase a escala de juego x3 y ampliada x6. Uso: cmp_class.py shadow"""
import io, os, subprocess, sys
from PIL import Image
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
c = sys.argv[1]
rel = 'Shared/assets/sprites/pl_%s.png' % c
old = Image.open(io.BytesIO(subprocess.run(['git', 'show', 'HEAD:' + rel], cwd=ROOT, capture_output=True, check=True).stdout)).convert('RGBA')
new = Image.open(os.path.join(ROOT, rel)).convert('RGBA')
import json
rows = json.load(open(os.path.join(ROOT, rel[:-4] + '.json')))['anims']
BG = (34, 28, 48, 255)
def cell(im, row, col):
    b = Image.new('RGBA', (64, 48), BG); b.alpha_composite(im.crop((col * 64, row * 48, col * 64 + 64, row * 48 + 48))); return b
picks = [('idle', 0), ('run', 2), ('attack1', 2), ('attack3', 2)]
S = 6
W = Image.new('RGB', (64 * S * 2 + 10, 48 * S * len(picks) + 4 * (len(picks) - 1)), (0, 0, 0))
for r, (an, f) in enumerate(picks):
    row = rows[an]['row']
    for k, im in enumerate((old, new)):
        W.paste(cell(im, row, f).resize((64 * S, 48 * S), Image.NEAREST).convert('RGB'), (k * (64 * S + 10), r * (48 * S + 4)))
out = os.path.join(ROOT, 'docs/capturas_arte/%s_grupo2_antes_izq_despues_der.png' % c)
W.save(out)
G = Image.new('RGB', (64 * 3 * 2 + 6, 48 * 3), (0, 0, 0))
for k, im in enumerate((old, new)):
    G.paste(cell(im, rows['idle']['row'], 0).resize((192, 144), Image.NEAREST).convert('RGB'), (k * 198, 0))
G.save(out.replace('antes_izq_despues_der', 'escala_juego_x3'))
print(out)
