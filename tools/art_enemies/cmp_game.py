#!/usr/bin/env python3
"""Comparacion antes (HEAD) / despues (disco) A ESCALA DE JUEGO: 1 pixel de sprite = 1 pixel logico (la vista del juego es 480x270; los
fondos miden 512x288), sobre el fondo real del bioma, sin filtros ni ampliacion. Izquierda = antes, derecha = despues; en cada lado
reposo + fotograma de ataque (+ dano). Salida 1:1 y una copia x3 (vecino mas cercano) solo para poder verla en pantalla.
Uso: cmp_game.py en|bs nombre bioma [anim:frame ...]"""
import io, json, os, subprocess, sys
from PIL import Image
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
kind, name, bioma = sys.argv[1:4]
picks = [a.split(':') for a in sys.argv[4:]] or [['idle', '0'], ['attack', '2'], ['hurt', '0']]
rel = 'Shared/assets/sprites/%s_%s.png' % (kind, name)
d = json.load(open(os.path.join(ROOT, rel[:-4] + '.json')))
cw, ch = d['cell']; px, py = d['pivot']
old = Image.open(io.BytesIO(subprocess.run(['git', 'show', 'HEAD:' + rel], cwd=ROOT, capture_output=True, check=True).stdout)).convert('RGBA')
new = Image.open(os.path.join(ROOT, rel)).convert('RGBA')
bg = Image.new('RGBA', (512, 288), (20, 16, 28, 255))
for k in range(3):
    p = os.path.join(ROOT, 'Shared/assets/bg/bg_%s_%d.png' % (bioma, k))
    if os.path.exists(p): bg.alpha_composite(Image.open(p).convert('RGBA'))
GY = 236
n = len(picks); slot = 256 // n
out = bg.copy()
for side, im in enumerate((old, new)):
    for k, (a, f) in enumerate(picks):
        A = d['anims'][a]; f = int(f)
        c = im.crop((f * cw, A['row'] * ch, f * cw + cw, A['row'] * ch + ch))
        x = side * 256 + k * slot + slot // 2 - px
        out.alpha_composite(c, (int(x), GY - py))
b = os.path.join(ROOT, 'docs/capturas_arte/escala_juego_%s_%s_antes_izq_despues_der' % (kind, name))
out.convert('RGB').save(b + '_1x.png')
out.convert('RGB').resize((512 * 3, 288 * 3), Image.NEAREST).save(b + '_3x.png')
print(b + '_1x.png')
