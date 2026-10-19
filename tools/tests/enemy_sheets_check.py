#!/usr/bin/env python3
"""Comprueba (automatico, sin dispositivo) las hojas de enemigos/jefes frente a una base git: JSON funcional identico,
mismo tamano de hoja, ningun fotograma vacio, pies (pivote) y caja de silueta estables y cambio de silueta acotado.
Uso: enemy_sheets_check.py [BASE]   (BASE por defecto: d9017b6 = antes de la fase de enemigos)"""
import glob, io, json, os, subprocess, sys
from PIL import Image, ImageChops
BASE = sys.argv[1] if len(sys.argv) > 1 else 'd9017b6'
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
def git(path):
    return subprocess.run(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, capture_output=True, check=True).stdout
bad = 0; n_ok = 0
for png in sorted(glob.glob(os.path.join(ROOT, 'Shared/assets/sprites/en_*.png')) + glob.glob(os.path.join(ROOT, 'Shared/assets/sprites/bs_*.png'))):
    rel = os.path.relpath(png, ROOT); name = os.path.basename(png)
    try:
        old = Image.open(io.BytesIO(git(rel))).convert('RGBA'); oj = git(rel[:-4] + '.json')
    except subprocess.CalledProcessError:
        print('NUEVO ', name); continue
    new = Image.open(png).convert('RGBA'); nj = open(png[:-4] + '.json', 'rb').read()
    errs = []
    if oj != nj: errs.append('JSON funcional distinto')
    if new.size != old.size: errs.append(f'tamano de hoja {old.size}->{new.size}')
    else:
        d = json.loads(nj); cw, ch = d['cell']
        for an, a in d['anims'].items():
            for i in range(a['n']):
                box = (i * cw, a['row'] * ch, (i + 1) * cw, (a['row'] + 1) * ch)
                o, nw = old.crop(box).getchannel('A'), new.crop(box).getchannel('A')
                bo, bn = o.getbbox(), nw.getbbox()
                if bn is None and bo is not None: errs.append(f'{an}[{i}] fotograma vacio'); continue
                if bo and bn and (abs(bo[3] - bn[3]) > 2 or abs(bo[1] - bn[1]) > 6 or abs(bo[0] - bn[0]) > 6 or abs(bo[2] - bn[2]) > 6): errs.append(f'{an}[{i}] caja de silueta {bo}->{bn}')
                npx = max(1, sum(1 for v in o.getdata() if v)); dpx = sum(1 for v in ImageChops.difference(o, nw).getdata() if v)
                if dpx / npx > 0.35: errs.append(f'{an}[{i}] silueta cambia {dpx * 100 // npx}%')
    if errs: bad += 1; print('FALLA', name, '; '.join(errs[:4]))
    else: n_ok += 1
print(f'ENEMY SHEETS ok={n_ok} fallos={bad}')
sys.exit(1 if bad else 0)
