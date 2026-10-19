#!/usr/bin/env python3
"""Comparacion antes (HEAD) / despues (disco) de un jefe, frames clave a escala 2x. Uso: cmp_boss.py rey_exanime [anim:frame ...]"""
import io, json, os, subprocess, sys
from PIL import Image
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
BG = (34, 28, 48, 255)
name = sys.argv[1]
picks = [a.split(':') for a in sys.argv[2:]] or [['idle', '0'], ['walk', '2'], ['attack1', '3'], ['attack2', '3'], ['windup1', '3'], ['cast', '4'], ['phase', '4'], ['death', '6']]
rel = 'Shared/assets/sprites/bs_%s.png' % name
d = json.load(open(os.path.join(ROOT, rel[:-4] + '.json')))
cw, ch = d['cell']
old = Image.open(io.BytesIO(subprocess.run(['git', 'show', 'HEAD:' + rel], cwd=ROOT, capture_output=True, check=True).stdout)).convert('RGBA')
new = Image.open(os.path.join(ROOT, rel)).convert('RGBA')
S = 2
cols = 4
rows = (len(picks) + cols - 1) // cols
W = Image.new('RGB', (cols * cw * S, rows * ch * S * 2 + rows * 4), (0, 0, 0))
for k, (a, f) in enumerate(picks):
    A = d['anims'][a]; f = int(f)
    for r, im in enumerate((old, new)):
        t = Image.new('RGBA', (cw, ch), BG); t.alpha_composite(im.crop((f * cw, A['row'] * ch, f * cw + cw, A['row'] * ch + ch)))
        W.paste(t.resize((cw * S, ch * S), Image.NEAREST).convert('RGB'), ((k % cols) * cw * S, (k // cols) * (ch * S * 2 + 4) + r * ch * S))
out = os.path.join(ROOT, 'docs/capturas_arte/jefe_%s_antes_arriba_despues_abajo.png' % name)
W.save(out); print(out)
