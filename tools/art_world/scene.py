"""Escena de prueba: fondo + terreno autotileado + decoracion + luces."""
import sys, os
import numpy as np
from PIL import Image
A = '/home/claude/juego-roguelike/app/src/main/assets'
PREV = '/home/claude/juego-roguelike/tools/previews/art_world'
N, E, S, W = 1, 2, 4, 8


def mapgrid():
    g = np.zeros((17, 40), bool)
    g[14:, :] = True
    g[:2, :] = True
    g[:, :2] = True
    g[:, 38:] = True
    g[14:, 14:17] = False
    g[15:, 27:29] = False
    g[9:11, 6:10] = True
    g[5:14, 21:23] = True
    g[12:14, 10:13] = True
    g[11:14, 30:34] = True
    g[2:5, 30:36] = True
    g[8:10, 14:19] = True
    g[6:8, 26:29] = True
    return g


def auto(g, r, c):
    def s(rr, cc):
        return rr < 0 or cc < 0 or rr >= g.shape[0] or cc >= g.shape[1] or g[rr, cc]
    return (1 if s(r - 1, c) else 0) | (2 if s(r, c + 1) else 0) | (4 if s(r + 1, c) else 0) | (8 if s(r, c - 1) else 0)


def tile(sheet, col, row):
    return sheet.crop((col * 16, row * 16, col * 16 + 16, row * 16 + 16))


def load_bg(b, w=640, h=272):
    base = Image.new('RGBA', (w, h), (20, 20, 30, 255))
    for i in range(3):
        p = f'{A}/bg/bg_{b}_{i}.png'
        if os.path.exists(p):
            im = Image.open(p).convert('RGBA')
            for ox in range(0, w + 512, 512):
                base.alpha_composite(im, (ox - 0, -8)) if False else None
            canvas = Image.new('RGBA', (1024, 288))
            canvas.paste(im, (0, 0))
            canvas.paste(im, (512, 0))
            crop = canvas.crop((64, 8, 64 + w, 8 + h))
            base.alpha_composite(crop)
    return base


def render(b, frame=0, seed=3, with_bg=True):
    sheet = Image.open(f'{A}/tiles/tiles_{b}.png').convert('RGBA')
    g = mapgrid()
    im = load_bg(b) if with_bg else Image.new('RGBA', (640, 272), (20, 20, 30, 255))
    rs = np.random.RandomState(seed)
    # muro de fondo detras de las zonas interiores (franja central), con huecos abiertos
    wallzone = np.zeros_like(g)
    wallzone[2:14, 2:38] = True
    wallzone[2:14, 9:25] = False
    for r in range(17):
        for c in range(40):
            if wallzone[r, c] and not g[r, c] and (r > 11 or c < 9 or c > 25) and not (c > 34):
                im.alpha_composite(tile(sheet, 8 + rs.randint(4), 3), (c * 16, r * 16))
    # decoracion de pared
    for (c, r, k) in [(5, 11, 12), (17, 11, 13), (24, 11, 14), (24, 7, 14), (24, 9, 14), (33, 9, 12), (8, 11, 15), (35, 12, 13)]:
        if not g[r, c]:
            im.alpha_composite(tile(sheet, k, 3), (c * 16, r * 16))
    # antorchas, luces y decoracion de fila 6
    for (c, r, k) in [(4, 9, 0), (12, 9, 0), (28, 9, 0), (36, 9, 0), (15, 11, 4), (31, 9, 4)]:
        if not g[r, c]:
            im.alpha_composite(tile(sheet, k + frame % 4, 4), (c * 16, r * 16))
    for (c, r, k) in [(3, 6, 0), (7, 12, 1), (19, 8, 2), (27, 11, 3), (36, 5, 4), (29, 6, 5), (11, 5, 6), (33, 12, 7)]:
        if not g[r, c]:
            im.alpha_composite(tile(sheet, k, 6), (c * 16, r * 16))
    # colgantes de techo
    for c in range(2, 38):
        if g[1, c] and not g[2, c] and rs.rand() < .35:
            im.alpha_composite(tile(sheet, 8 + rs.randint(8), 4), (c * 16, 2 * 16))
    for c in range(30, 36):
        if rs.rand() < .5:
            im.alpha_composite(tile(sheet, 8 + rs.randint(8), 4), (c * 16, 5 * 16))
    # terreno
    for r in range(17):
        for c in range(40):
            if g[r, c]:
                m = auto(g, r, c)
                v = rs.randint(3)
                im.alpha_composite(tile(sheet, m, v), (c * 16, r * 16))
    # plataformas atravesables
    for (c0, c1, r) in [(3, 6, 8), (24, 26, 10), (33, 37, 6)]:
        for c in range(c0, c1 + 1):
            k = 0 if c0 == c1 else (1 if c == c0 else (3 if c == c1 else 2))
            im.alpha_composite(tile(sheet, k, 3), (c * 16, r * 16))
    # peligros
    for c in (15, 16):
        im.alpha_composite(tile(sheet, 4, 3), (c * 16, 13 * 16 + 0)) if False else None
    for c in (14, 15, 16):
        im.alpha_composite(tile(sheet, 6 + (frame % 2), 3), (c * 16, 15 * 16))
        im.alpha_composite(tile(sheet, 6 + (frame % 2), 3), (c * 16, 16 * 16))
    for c in (27, 28):
        im.alpha_composite(tile(sheet, 4, 3), (c * 16, 14 * 16))
    for c in (31, 32):
        im.alpha_composite(tile(sheet, 5, 3), (c * 16, 14 * 16)) if False else None
    for c in (31, 32, 33):
        im.alpha_composite(tile(sheet, 5, 3), (c * 16, 5 * 16))
    # props de suelo sobre las superficies
    tops = [(c, r) for r in range(1, 16) for c in range(2, 38) if (not g[r - 1, c]) and g[r, c]]
    rs2 = np.random.RandomState(seed + 5)
    for (c, r) in tops:
        if rs2.rand() < .42:
            im.alpha_composite(tile(sheet, rs2.randint(16), 5), (c * 16, (r - 1) * 16 + 1 - 1 + 0))
    return im


if __name__ == '__main__':
    names = sys.argv[1:]
    Z = 2
    ims = [render(b).resize((640 * Z, 272 * Z), Image.NEAREST) for b in names]
    out = Image.new('RGBA', (640 * Z, 272 * Z * len(ims)))
    for i, m in enumerate(ims):
        out.paste(m, (0, i * 272 * Z))
    out.save(f'{PREV}/scene.png')
