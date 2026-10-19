#!/usr/bin/env python3
"""Compara las hojas pl_*.png actuales con las originales (commit base) y verifica que:
 - cada fotograma original sigue intacto (solo se inserto un fotograma smear por animacion);
 - las cajas de golpe ('box') no cambiaron y 'hit' se desplazo exactamente +1;
 - las demas filas (idle, run, hurt...) son identicas."""
import json, subprocess, sys, io, glob, os
from PIL import Image, ImageChops
BASE = '8e44cff'
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
CW, CH = 64, 48
def git(path):
    return subprocess.run(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, capture_output=True, check=True).stdout
bad = 0
for png in sorted(glob.glob(os.path.join(ROOT, 'Shared/assets/sprites/pl_*.png'))):
    rel = os.path.relpath(png, ROOT); name = os.path.basename(png)
    old = Image.open(io.BytesIO(git(rel))).convert('RGBA'); new = Image.open(png).convert('RGBA')
    od = json.loads(git(rel[:-4] + '.json')); nd = json.load(open(png[:-4] + '.json'))
    errs = []
    if old.size != new.size: errs.append('tamano de hoja distinto')
    for an, o in od['anims'].items():
        n = nd['anims'][an]
        sm = n.get('smear', -1)
        add = 1 if sm >= 0 else 0
        if n['n'] != o['n'] + add: errs.append(f'{an}: n {o["n"]}->{n["n"]}')
        if n.get('box') != o.get('box'): errs.append(f'{an}: box cambio')
        if 'hit' in o and n['hit'] != [o['hit'][0] + add, o['hit'][1] + add]: errs.append(f'{an}: hit mal desplazado')
        lim = o['hit'][0] if 'hit' in o else (o['rel'] if 'rel' in o else 1)
        if sm >= 0 and not (0 <= sm <= lim): errs.append(f'{an}: smear fuera de lugar')
        if 'rel' in o and n.get('rel') != o['rel'] + add: errs.append(f'{an}: rel mal desplazado')
        for i in range(n['n']):
            if i == sm: continue
            j = i - 1 if (sm >= 0 and i > sm) else i
            a = old.crop((j * CW, o['row'] * CH, (j + 1) * CW, (o['row'] + 1) * CH)); b = new.crop((i * CW, n['row'] * CH, (i + 1) * CW, (n['row'] + 1) * CH))
            if ImageChops.difference(a, b).getbbox(): errs.append(f'{an}: fotograma {i} distinto del original')
        if sm >= 0:   # el smear conserva la paleta del sprite (sin colores nuevos) y no esta vacio
            f = new.crop((sm * CW, n['row'] * CH, (sm + 1) * CW, (n['row'] + 1) * CH)); orig = set(p for p in old.crop((0, o['row'] * CH, old.size[0], (o['row'] + 1) * CH)).getdata())
            opaque = [p for p in f.getdata() if p[3] == 255]
            if not opaque: errs.append(f'{an}: smear vacio')
            if any(p not in orig for p in opaque): errs.append(f'{an}: smear con colores fuera de la paleta del sprite')
    if errs: bad += 1; print('FALLA', name, errs[:6])
    else: print('OK   ', name, 'fotogramas originales intactos, cajas de golpe iguales, smear con paleta propia')
sys.exit(1 if bad else 0)
