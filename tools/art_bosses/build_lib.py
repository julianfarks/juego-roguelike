import os, sys, json
import numpy as np
from PIL import Image, ImageDraw

ROOT = '/home/claude/juego-roguelike'
A = ROOT + '/app/src/main/assets'
PREV = ROOT + '/tools/previews/art_bosses'
ORDER = [('idle', 6, 8, True), ('walk', 8, 10, True), ('windup1', 5, 12, False), ('attack1', 8, 16, False),
         ('windup2', 5, 12, False), ('attack2', 8, 16, False), ('windup3', 6, 12, False), ('attack3', 9, 14, False),
         ('cast', 8, 12, False), ('hurt', 2, 10, False), ('phase', 10, 10, False), ('intro', 14, 10, False),
         ('death', 14, 9, False)]


def render_boss(boss, only=None):
    frames = {}
    for name, n, fps, loop in ORDER:
        if only and name not in only:
            continue
        a = boss.anims[name]
        fr = []
        for i in range(n):
            pose = boss.pose_at(name, i)
            fr.append(boss.frame(name, i, n, pose))
        frames[name] = fr
    return frames


def quantize_sheet(sheet):
    a = np.asarray(sheet)
    alpha = a[..., 3]
    rgb = Image.fromarray(a[..., :3], 'RGB')
    q = rgb.quantize(colors=255, method=Image.MEDIANCUT, dither=Image.NONE)
    qa = np.asarray(q)
    pa = np.array(q.getpalette()[:765], np.uint8).reshape(-1, 3)
    out = np.zeros(a.shape, np.uint8)
    out[..., :3] = pa[qa]
    out[..., 3] = alpha
    out[alpha == 0, :3] = 0
    return Image.fromarray(out, 'RGBA')


def write_sheet(boss, frames, outdir=A + '/sprites', quant=False):
    W, H = boss.cell
    maxn = max(n for _, n, _, _ in ORDER)
    sheet = Image.new('RGBA', (maxn * W, len(ORDER) * H), (0, 0, 0, 0))
    js = {'cell': [W, H], 'pivot': list(boss.pivot), 'body': list(boss.body), 'anims': {}}
    for r, (name, n, fps, loop) in enumerate(ORDER):
        for i, fr in enumerate(frames[name]):
            sheet.paste(Image.fromarray(fr, 'RGBA'), (i * W, r * H))
        d = {'row': r, 'n': n, 'fps': fps, 'loop': loop}
        an = boss.anims[name]
        for k in ('hit', 'box', 'rel', 'muzzle'):
            if k in an:
                d[k] = an[k]
        if 'muzzle_src' in an:
            bone, pt = an['muzzle_src']
            p = boss.pose_at(name, an['rel'])
            x, y = boss.anchor(p, bone, pt)
            d['muzzle'] = [int(round(x - boss.pivot[0])), int(round(y - boss.pivot[1]))]
        js['anims'][name] = d
    os.makedirs(outdir, exist_ok=True)
    if quant:
        sheet = quantize_sheet(sheet)
    sheet.save(f'{outdir}/bs_{boss.id}.png', optimize=True)
    json.dump(js, open(f'{outdir}/bs_{boss.id}.json', 'w'), indent=1)
    return sheet


def strip(boss, fr, sc=3, bg=(34, 30, 46, 255)):
    W, H = boss.cell
    n = len(fr)
    im = Image.new('RGBA', (n * W, H), bg)
    d = ImageDraw.Draw(im)
    for i, f in enumerate(fr):
        d.line([(i * W, boss.pivot[1] + 1), (i * W + W, boss.pivot[1] + 1)], fill=(70, 62, 90, 255))
        im.alpha_composite(Image.fromarray(f, 'RGBA'), (i * W, 0))
    return im.resize((n * W * sc, H * sc), Image.NEAREST)


def previews(boss, frames, sc=3, names=None):
    os.makedirs(PREV, exist_ok=True)
    for name in (names or frames.keys()):
        strip(boss, frames[name], sc).save(f'{PREV}/{boss.id}_{name}.png')


def contact(boss, frames, picks, sc=2, cols=8):
    """picks: lista de (anim, frame)"""
    W, H = boss.cell
    rows = (len(picks) + cols - 1) // cols
    im = Image.new('RGBA', (cols * W, rows * H), (34, 30, 46, 255))
    d = ImageDraw.Draw(im)
    for k, (a, i) in enumerate(picks):
        x, y = (k % cols) * W, (k // cols) * H
        d.line([(x, y + boss.pivot[1] + 1), (x + W, y + boss.pivot[1] + 1)], fill=(70, 62, 90, 255))
        im.alpha_composite(Image.fromarray(frames[a][i], 'RGBA'), (x, y))
    return im.resize((cols * W * sc, rows * H * sc), Image.NEAREST)
