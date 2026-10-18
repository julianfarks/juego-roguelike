#!/usr/bin/env python3
"""Regenera todos los sprites de jugador: python3 tools/art_players/build_all.py [clase ...] [--only anim,anim] [--nopreview]"""
import os, sys, json, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from multiprocessing import Pool
import anims as AN
from kit import reset_mats
from rig import skeleton, simulate
from common import render_frame

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'Shared/assets/sprites')
PREV = os.path.join(ROOT, 'tools/previews/art_players')
CLASSES = ['paladin', 'shadow', 'flame', 'storm', 'frost', 'verdant', 'blood', 'earth', 'astral', 'steel']
CELL = (64, 48)
PIVOT = [32, 44]


def load(cid):
    mod = importlib.import_module('cls_' + cid)
    for v in vars(mod).values():
        if isinstance(v, type) and getattr(v, 'id', None) == cid:
            return v()
    raise KeyError(cid)


def build_class(args):
    cid, only, do_splash = args
    reset_mats()
    cls = load(cid)
    cls.init_mats()
    frames = {}
    meta = {}
    for name in AN.ORDER + AN.EXT:
        if only and name not in only:
            continue
        seq = cls.seq(name)
        n = AN.N[name]
        loop = AN.LOOP.get(name, False)
        rb = simulate(cls.ribbons, seq.at, lambda p: skeleton(p, cls.D), n, loop=loop)
        hit = cls.attacks[name][1] if name in cls.attacks else None
        fr = []
        for i in range(n):
            tr = (lambda X, i=i: cls.trail_draw(X, seq, i, hit)) if hit else None
            if name in AN.EXT:
                f = render_frame(cls, seq, rb, i, n, name, trail=tr, size=AN.XCELL, origin=(AN.XPIVOT[0], AN.XPIVOT[1]))
                import pfx
                f = pfx.post(cls, name, i, n, f, seq)
                fr.append(f)
            else:
                fr.append(render_frame(cls, seq, rb, i, n, name, trail=tr))
        frames[name] = fr
        d = {'row': AN.ORDER.index(name) if name in AN.ORDER else -1, 'n': n, 'fps': AN.FPS[name], 'loop': bool(loop)}
        if hit:
            box, reach = cls.box_for(seq, hit, n, name)
            d['hit'] = list(hit)
            d['box'] = box
            meta[name] = reach
        if name == 'skill' or name == 'ult':
            rel = 3 if name == 'skill' else 5
            d['rel'] = rel
            mz = cls.blade_pts(seq.at(rel), [(cls.muzzle_x, 0)])[0]
            d['muzzle'] = [int(round(mz[0])), int(round(mz[1]))]
        meta[name + '_d'] = d
    stat = {}
    if only is None or 'static' in (only or []):
        import static
        stat['splash'] = static.splash(cls)
        stat['portrait'] = static.portrait(cls)
    return cid, frames, meta, stat


def write_class(cid, frames, meta):
    cls = load(cid)
    W = max(AN.N[k] for k in AN.ORDER) * CELL[0]
    H = len(AN.ORDER) * CELL[1]
    sheet = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    anims = {}
    for name in AN.ORDER:
        if name not in frames:
            continue
        for i, f in enumerate(frames[name]):
            sheet.paste(Image.fromarray(f, 'RGBA'), (i * CELL[0], AN.ORDER.index(name) * CELL[1]))
        anims[name] = meta[name + '_d']
    js = {'cell': list(CELL), 'pivot': PIVOT, 'body': list(cls.body), 'anims': anims}
    return sheet, js


def write_x(cid, frames, meta):
    """Hoja de personalidad pl_x_<clase>: celda mas alta (64x64), mismo contrato JSON."""
    cls = load(cid)
    cw, ch = AN.XCELL
    W = max(AN.N[k] for k in AN.EXT) * cw
    H = len(AN.EXT) * ch
    sheet = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    anims = {}
    for r, name in enumerate(AN.EXT):
        if name not in frames:
            continue
        for i, f in enumerate(frames[name]):
            sheet.paste(Image.fromarray(f, 'RGBA'), (i * cw, r * ch))
        anims[name] = {'row': r, 'n': AN.N[name], 'fps': AN.FPS[name], 'loop': bool(AN.LOOP.get(name, False))}
    js = {'cell': [cw, ch], 'pivot': AN.XPIVOT, 'body': list(cls.body), 'anims': anims}
    return sheet, js


def contact(cid, frames, scale=4, bg=(30, 26, 44)):
    rows = [n for n in AN.ORDER + AN.EXT if n in frames]
    cwh = lambda n: AN.XCELL if n in AN.EXT else CELL
    cw0, ch0 = max(cwh(n)[0] for n in rows), max(cwh(n)[1] for n in rows)
    W = max(len(frames[n]) for n in rows) * cw0
    H = len(rows) * ch0
    CELL_ = (cw0, ch0)
    im = Image.new('RGBA', (W, H), bg + (255,))
    for r, n in enumerate(rows):
        for i, f in enumerate(frames[n]):
            im.alpha_composite(Image.fromarray(f, 'RGBA'), (i * CELL_[0], r * CELL_[1] + CELL_[1] - f.shape[0]))
    return im.resize((W * scale // 2, H * scale // 2), Image.NEAREST)


def main():
    argv = sys.argv[1:]
    only = None
    ext_out = False
    nopreview = False
    classes = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--only':
            only = argv[i + 1].split(',')
            i += 1
        elif a == '--static':
            only = ['static']
        elif a == '--ext':
            only = list(AN.EXT)
            ext_out = True
        elif a == '--nopreview':
            nopreview = True
        else:
            classes.append(a)
        i += 1
    classes = classes or CLASSES
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    jobs = [(c, only, True) for c in classes]
    with Pool(2) as pool:
        for cid, frames, meta, stat in pool.imap_unordered(build_class, jobs):
            if ext_out:
                xs, xj = write_x(cid, frames, meta)
                xs.save(os.path.join(OUT, f'plx_{cid}.png'), optimize=True)
                json.dump(xj, open(os.path.join(OUT, f'plx_{cid}.json'), 'w'), indent=1)
                print(cid, 'plx ok')
            if only is None:
                sheet, js = write_class(cid, frames, meta)
                sheet.save(os.path.join(OUT, f'pl_{cid}.png'), optimize=True)
                json.dump(js, open(os.path.join(OUT, f'pl_{cid}.json'), 'w'), indent=1)
                xs, xj = write_x(cid, frames, meta)
                xs.save(os.path.join(OUT, f'plx_{cid}.png'), optimize=True)
                json.dump(xj, open(os.path.join(OUT, f'plx_{cid}.json'), 'w'), indent=1)
                print(cid, 'ok', {k: round(v, 1) for k, v in meta.items() if not k.endswith('_d')})
            if stat:
                stat['splash'].save(os.path.join(OUT, f'splash_{cid}.png'), optimize=True)
                stat['portrait'].save(os.path.join(OUT, f'portrait_{cid}.png'), optimize=True)
            if frames:
                contact(cid, frames).save(os.path.join(PREV, f'sheet_{cid}.png'))
            if only:
                for n in [o for o in only if o != 'static']:
                    if n in frames:
                        contact(cid, {n: frames[n]}, scale=6).save(os.path.join(PREV, f'anim_{cid}_{n}.png'))


def static_sheet():
    W = Image.new('RGBA', (128 * 5 * 2 + 20, (176 + 32) * 2 * 2), (30, 26, 44, 255))
    for k, c in enumerate(CLASSES):
        sp = Image.open(os.path.join(OUT, f'splash_{c}.png'))
        pt = Image.open(os.path.join(OUT, f'portrait_{c}.png'))
        x, y = (k % 5) * 256, (k // 5) * 416
        W.alpha_composite(sp.resize((256, 352), Image.NEAREST), (x, y))
        W.alpha_composite(pt.resize((64, 64), Image.NEAREST), (x, y + 352))
    W.save(os.path.join(PREV, 'statics.png'))


def _main():
    main()
    static_sheet()


if __name__ == '__main__':
    _main()
