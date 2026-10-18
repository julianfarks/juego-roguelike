"""Kit minimo de pixel art para los recursos del centro de operaciones (paleta compartida con los props existentes)."""
import json, os, math
from PIL import Image, ImageDraw

A = os.path.join(os.path.dirname(__file__), '..', '..', 'Shared', 'assets', 'sprites')

def H(s):
    s = s.lstrip('#'); return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), 255)

# rampas (oscuro -> claro), sacadas de los props existentes
OUT = H('110f1a')
STONE = [H(c) for c in ('201f2c', '383541', '4f4d63', '696385', '87849d', '9f9bae', 'b6b2c0')]
WOOD = [H(c) for c in ('3c201a', '4a2019', '643323', '7d4a2e', '97603b', 'b0754b', 'c98f5c')]
GOLD = [H(c) for c in ('7a3a1a', 'c0742a', 'f2b43c', 'ffd45a', 'ffe27a', 'fff2b0')]
STEEL = [H(c) for c in ('242633', '363a4c', '5a6078', '87849d', 'b8b7c7', 'e4e4ee', 'ffffff')]
CLOTH_R = [H(c) for c in ('300f20', '561c35', '7a2a46', '9f3d5b', 'c05a78')]
CLOTH_B = [H(c) for c in ('1c1840', '2e2860', '4a3a6e', '6d5293', '9275ad', 'b8a0d0')]
GREEN = [H(c) for c in ('12281c', '1d3a2a', '2f5a3a', '4a8a4a', '7acb6a', 'b8f08a')]
FIRE = [H(c) for c in ('7a1a0a', 'c8400a', 'f0641a', 'ffb43a', 'fff2a8')]
ICE = [H(c) for c in ('14284a', '24508a', '3a86c8', '7ac8f0', 'c8f0ff')]
VIOL = [H(c) for c in ('1c0c38', '3e1c7a', '6a3cd6', 'aa6eff', 'dec4ff')]
PAPER = [H(c) for c in ('7a6a4a', 'b0a078', 'd8ccb0', 'e8dcc0', 'f8f0dc')]
SHADOW = [H(c) for c in ('0c0814', '1c1230', '3a2a5a', '5a448a', '8a70c0')]


class Cv:
    def __init__(s, w, h):
        s.w, s.h = w, h
        s.im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        s.d = ImageDraw.Draw(s.im)

    def px(s, x, y, c):
        if 0 <= x < s.w and 0 <= y < s.h: s.im.putpixel((int(x), int(y)), c)

    def get(s, x, y):
        return s.im.getpixel((int(x), int(y))) if 0 <= x < s.w and 0 <= y < s.h else (0, 0, 0, 0)

    def rect(s, x0, y0, x1, y1, c):  # inclusivo
        s.d.rectangle([x0, y0, x1, y1], fill=c)

    def line(s, x0, y0, x1, y1, c):
        s.d.line([x0, y0, x1, y1], fill=c)

    def poly(s, pts, c):
        s.d.polygon(pts, fill=c)

    def ell(s, x0, y0, x1, y1, c):
        s.d.ellipse([x0, y0, x1, y1], fill=c)

    def box(s, x0, y0, x1, y1, ramp, lo=1, mid=3, hi=5):
        """Caja sombreada: cara media, borde superior/izquierdo claro, inferior/derecho oscuro."""
        s.rect(x0, y0, x1, y1, ramp[mid])
        s.line(x0, y0, x1, y0, ramp[hi]); s.line(x0, y0, x0, y1, ramp[min(hi, mid + 1)])
        s.line(x0, y1, x1, y1, ramp[lo]); s.line(x1, y0, x1, y1, ramp[max(lo, mid - 1)])

    def dither(s, x0, y0, x1, y1, c, alpha_only=True):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if (x + y) % 2 == 0 and (not alpha_only or s.get(x, y)[3] > 0): s.px(x, y, c)

    def outline(s, c=OUT, diag=False):
        src = s.im.copy(); W, Hh = s.w, s.h
        for y in range(Hh):
            for x in range(W):
                if src.getpixel((x, y))[3] == 0:
                    nb = [(1, 0), (-1, 0), (0, 1), (0, -1)] + ([(1, 1), (-1, -1), (1, -1), (-1, 1)] if diag else [])
                    for dx, dy in nb:
                        xx, yy = x + dx, y + dy
                        if 0 <= xx < W and 0 <= yy < Hh and src.getpixel((xx, yy))[3] > 200:
                            s.im.putpixel((x, y), c); break


def sheet(frames, rows=None):
    """frames: lista de listas (filas de animacion) de Cv. Devuelve imagen."""
    rows = frames
    cw, ch = rows[0][0].w, rows[0][0].h
    n = max(len(r) for r in rows)
    im = Image.new('RGBA', (cw * n, ch * len(rows)), (0, 0, 0, 0))
    for ri, r in enumerate(rows):
        for fi, f in enumerate(r): im.paste(f.im, (fi * cw, ri * ch))
    return im


def save(name, rows, anims, pivot=None, body=None, scale_prev=4):
    cw, ch = rows[0][0].w, rows[0][0].h
    im = sheet(rows)
    im.save(os.path.join(A, name + '.png'))
    meta = {'cell': [cw, ch], 'pivot': pivot or [cw // 2, ch - 1], 'body': body or [cw - 8, ch - 8], 'anims': anims}
    json.dump(meta, open(os.path.join(A, name + '.json'), 'w'), indent=1)
    return im
