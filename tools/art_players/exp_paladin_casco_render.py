#!/usr/bin/env python3
"""Muestra EXPERIMENTAL: Paladin actual vs yelmo cerrado, misma pose (idle 0), escala/celda originales (64x48). No toca el juego."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import anims as AN
from kit import reset_mats
from rig import skeleton, simulate
from common import render_frame
import cls_paladin, exp_paladin_casco
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'art'))
import polish

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'tools/experimental/paladin_casco_cerrado')


def frames(cls, name):
    seq = cls.seq(name); n = AN.N[name]; loop = AN.LOOP.get(name, False)
    rb = simulate(cls.ribbons, seq.at, lambda p: skeleton(p, cls.D), n, loop=loop)
    res = []
    for i in range(n):
        a = render_frame(cls, seq, rb, i, n, name, size=(64, 48), S=4, scale=1.0, origin=(32, 44))
        res.append(Image.fromarray(polish.polish_array(np.array(Image.fromarray(a, 'RGBA'))), 'RGBA'))
    return res


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {}
    for key, C in (('actual', cls_paladin.Paladin), ('cerrado', exp_paladin_casco.PaladinCasco)):
        reset_mats(); c = C(); c.init_mats()
        res[key] = {nm: frames(c, nm) for nm in ('idle', 'run', 'attack1')}
    # hojas experimentales (idle/run/attack1) solo del casco cerrado
    for nm, fr in res['cerrado'].items():
        sh = Image.new('RGBA', (64 * len(fr), 48), (0, 0, 0, 0))
        for i, f in enumerate(fr): sh.paste(f, (i * 64, 0))
        sh.save(os.path.join(OUT, 'casco_cerrado_%s.png' % nm))
    # comparacion: mismas poses, mismo tamano (x8, nearest)
    BG = (34, 28, 48, 255); S = 8
    def tile(im):
        b = Image.new('RGBA', im.size, BG); b.alpha_composite(im); return b.resize((im.width * S, im.height * S), Image.NEAREST).convert('RGB')
    rows = (('idle', 0), ('idle', 2), ('run', 2), ('attack1', 2))
    W = Image.new('RGB', (64 * S * 2 + 12, 48 * S * len(rows) + 6 * (len(rows) - 1)), (0, 0, 0))
    for r, (nm, i) in enumerate(rows):
        y = r * (48 * S + 6)
        W.paste(tile(res['actual'][nm][i]), (0, y)); W.paste(tile(res['cerrado'][nm][i]), (64 * S + 12, y))
    W.save(os.path.join(OUT, 'comparacion_actual_izq_cerrado_der.png'))
    # a escala de juego (x3, tamano real en pantalla) idle
    S2 = 3
    G = Image.new('RGB', (64 * S2 * 2 + 8, 48 * S2), (0, 0, 0))
    for k, key in enumerate(('actual', 'cerrado')):
        b = Image.new('RGBA', (64, 48), BG); b.alpha_composite(res[key]['idle'][0]); G.paste(b.resize((64 * S2, 48 * S2), Image.NEAREST).convert('RGB'), (k * (64 * S2 + 8), 0))
    G.save(os.path.join(OUT, 'comparacion_escala_juego_x3.png'))
    print('ok')


main()
