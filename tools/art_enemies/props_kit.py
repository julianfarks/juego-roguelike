"""Kit 1x para atrezo: mascaras + sombreado por altura con rampas, bordes biselados, contorno selout,
capa superior de particulas y luz aditiva punteada. Alfa siempre 0/255."""
import math, json, os
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from px import R, rgb, mix, BAY

OUT = '/home/claude/juego-roguelike/app/src/main/assets/sprites'
PREV = '/home/claude/juego-roguelike/tools/previews/art_enemies'
INK = (16, 12, 26)


def hnoise(x, y, seed=0):
    n = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0


class Cv:
    def __init__(s, W, H, pivot):
        s.W, s.H, s.pivot = W, H, pivot
        s.c = np.zeros((H, W, 3), np.uint8)
        s.a = np.zeros((H, W), bool)
        s.tc = np.zeros((H, W, 3), np.uint8)
        s.ta = np.zeros((H, W), bool)
        s.yy, s.xx = np.mgrid[0:H, 0:W]

    # ---- mascaras
    def _m(s, fn):
        im = Image.new('L', (s.W, s.H), 0)
        fn(ImageDraw.Draw(im))
        return np.array(im) > 127

    def rect(s, x0, y0, x1, y1):
        m = np.zeros((s.H, s.W), bool)
        m[max(0, int(y0)):max(0, int(y1)), max(0, int(x0)):max(0, int(x1))] = True
        return m

    def ell(s, cx, cy, rx, ry):
        return (((s.xx + 0.5 - cx) / rx) ** 2 + ((s.yy + 0.5 - cy) / ry) ** 2) <= 1.0

    def poly(s, pts):
        return s._m(lambda d: d.polygon([(float(x), float(y)) for x, y in pts], fill=255))

    def line(s, p0, p1, w=1):
        return s._m(lambda d: d.line([p0, p1], fill=255, width=w))

    def arch(s, x0, y0, x1, y1, rise):
        """rectangulo con arco apuntado/redondo arriba: y0 es la clave del arco."""
        m = s.rect(x0, y0 + rise, x1, y1)
        cx, hw = (x0 + x1) / 2, (x1 - x0) / 2
        top = ((s.xx + 0.5 - cx) / hw) ** 2 + ((s.yy + 0.5 - (y0 + rise)) / rise) ** 2 <= 1.0
        return m | (top & (s.yy < y0 + rise))

    # ---- pintura
    def paint(s, m, ramp, bevel=2.0, bias=0.55, grad=0.0, tex=0.0, rim=True, dark_edge=True, dith=0.5,
              light=(-0.7, -0.7), seed=1, emi=0.0, lumfn=None):
        if not m.any():
            return
        n = len(ramp)
        pad = np.pad(m, 1)
        d = ndi.distance_transform_edt(pad)[1:-1, 1:-1]
        hgt = np.minimum(d, bevel) / max(bevel, 0.01)
        hgt = ndi.gaussian_filter(hgt * m, 0.7)
        gy, gx = np.gradient(hgt)
        lum = bias + 1.15 * (-(gx * light[0] + gy * light[1])) * bevel * 0.9
        ys = np.where(m)[0]
        y0, y1 = ys.min(), ys.max() + 1
        lum = lum + grad * (0.5 - (s.yy - y0) / max(1, (y1 - y0)))
        if tex:
            nz = np.vectorize(lambda x, y: hnoise(x, y, seed))(s.xx, s.yy)
            lum = lum + (nz - 0.5) * tex
        if lumfn is not None:
            lum = lum + lumfn(s.xx, s.yy)
        bay = BAY[s.yy % 4, s.xx % 4] - 0.5
        idx = np.clip(np.floor(lum * (n - 1) + 0.5 + bay * dith), 0, n - 1).astype(int)
        ra = np.array(ramp, np.uint8)
        col = ra[idx]
        up = np.pad(m, ((1, 0), (0, 0)))[:-1]
        lf = np.pad(m, ((0, 0), (1, 0)))[:, :-1]
        dn = np.pad(m, ((0, 1), (0, 0)))[1:]
        rt = np.pad(m, ((0, 0), (0, 1)))[:, 1:]
        if rim:
            tl = m & (~up | ~lf)
            col[tl & (idx < n - 1)] = ra[min(n - 1, 3 if n > 3 else n - 1)] if n > 2 else ra[-1]
            tl2 = m & ~up
            col[tl2] = ra[min(n - 1, n - 2)]
        if dark_edge:
            br = m & (~dn | ~rt)
            col[br] = ra[0]
        s.c[m] = col[m]
        s.a[m] = True

    def flat(s, m, col):
        s.c[m] = col
        s.a[m] = True

    def px(s, x, y, col, top=False):
        x, y = int(x), int(y)
        if 0 <= x < s.W and 0 <= y < s.H:
            if top:
                s.tc[y, x] = col; s.ta[y, x] = True
            else:
                s.c[y, x] = col; s.a[y, x] = True

    def hline(s, x0, x1, y, col, top=False):
        for x in range(int(x0), int(x1)):
            s.px(x, y, col, top)

    def vline(s, x, y0, y1, col, top=False):
        for y in range(int(y0), int(y1)):
            s.px(x, y, col, top)

    def lightpass(s, cx, cy, r, col, strength=0.6, under=None):
        """Tine los pixeles opacos cercanos hacia col (luz emisiva) con punteado ordenado."""
        dist = np.sqrt((s.xx + 0.5 - cx) ** 2 + (s.yy + 0.5 - cy) ** 2)
        f = np.clip(1 - dist / r, 0, 1) * strength
        bay = BAY[s.yy % 4, s.xx % 4]
        on = s.a & (f > bay * 0.55)
        t = np.clip(f * 1.4, 0, 0.9)[..., None]
        newc = (s.c * (1 - t) + np.array(col) * t).astype(np.uint8)
        s.c[on] = newc[on]

    def halo(s, cx, cy, r, col, dens=0.5, top=True):
        """Brillo en el aire: pixeles sueltos punteados (alfa binario)."""
        dist = np.sqrt((s.xx + 0.5 - cx) ** 2 + (s.yy + 0.5 - cy) ** 2)
        f = np.clip(1 - dist / r, 0, 1) ** 1.7 * dens
        bay = BAY[s.yy % 4, s.xx % 4]
        on = (f > bay * 0.9) & ~s.a
        tgt_c, tgt_a = (s.tc, s.ta) if top else (s.c, s.a)
        tgt_c[on] = col
        tgt_a[on] = True

    def outline(s, strength=0.62, skip=None):
        a = s.a
        pad = np.pad(a, 1)
        nb = pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]
        edge = nb & ~a
        # color: oscurecido del vecino mas oscuro/cercano
        cp = np.pad(s.c.astype(float), ((1, 1), (1, 1), (0, 0)))
        ap = pad
        acc = np.zeros((s.H, s.W, 3)); cnt = np.zeros((s.H, s.W))
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            sub = cp[1 + dy:1 + dy + s.H, 1 + dx:1 + dx + s.W]
            sa = ap[1 + dy:1 + dy + s.H, 1 + dx:1 + dx + s.W]
            acc += sub * sa[..., None]; cnt += sa
        avg = acc / np.maximum(cnt, 1)[..., None]
        oc = avg * (1 - strength) + np.array(INK) * strength
        oc = oc * 0.8
        s.c[edge] = oc[edge].astype(np.uint8)
        s.a = a | edge

    def finish(s, outline=True):
        if outline:
            s.outline()
        c, a = s.c.copy(), s.a.copy()
        c[s.ta] = s.tc[s.ta]
        a |= s.ta
        out = np.zeros((s.H, s.W, 4), np.uint8)
        out[..., :3] = c
        out[..., 3] = np.where(a, 255, 0)
        out[~a, :3] = 0
        return Image.fromarray(out, 'RGBA')


class PSheet:
    def __init__(s, name, W, H, pivot, body):
        s.name, s.W, s.H, s.pivot, s.body = name, W, H, pivot, body
        s.rows = []

    def anim(s, name, n, fps, loop, fn, outline=True):
        fr = []
        for i in range(n):
            c = Cv(s.W, s.H, s.pivot)
            fn(c, i, n)
            fr.append(c.finish(outline))
        s.rows.append((name, n, fps, loop, fr))

    def save(s):
        maxn = max(r[1] for r in s.rows)
        im = Image.new('RGBA', (maxn * s.W, len(s.rows) * s.H), (0, 0, 0, 0))
        anims = {}
        for ri, (name, n, fps, loop, fr) in enumerate(s.rows):
            for i, f in enumerate(fr):
                im.paste(f, (i * s.W, ri * s.H))
            anims[name] = {'row': ri, 'n': n, 'fps': fps, 'loop': loop}
        os.makedirs(OUT, exist_ok=True)
        im.save(os.path.join(OUT, s.name + '.png'), optimize=True)
        json.dump({'cell': [s.W, s.H], 'pivot': list(s.pivot), 'body': list(s.body), 'anims': anims},
                  open(os.path.join(OUT, s.name + '.json'), 'w'), indent=1)
        os.makedirs(PREV, exist_ok=True)
        z = max(2, min(12, 900 // (maxn * s.W) if maxn * s.W < 900 else 2))
        z = max(4, min(14, 1000 // (maxn * s.W)))
        bg = Image.new('RGBA', im.size, (34, 30, 44, 255))
        bg.alpha_composite(im)
        big = bg.resize((im.width * z, im.height * z), Image.NEAREST)
        d = ImageDraw.Draw(big)
        for ri in range(len(s.rows)):
            for i in range(maxn):
                d.rectangle([i * s.W * z, ri * s.H * z, (i + 1) * s.W * z - 1, (ri + 1) * s.H * z - 1], outline=(70, 64, 90))
        big.convert('RGB').save(os.path.join(PREV, s.name + '.png'))
        return im


def sm(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def sphere(c, cx, cy, r, ramp, hl=(-0.4, -0.4)):
    """Esfera sombreada radialmente (luz arriba-izquierda), sin sesgo de borde."""
    m = c.ell(cx, cy, r, r)
    d = np.sqrt((c.xx + 0.5 - cx - hl[0] * r) ** 2 + (c.yy + 0.5 - cy - hl[1] * r) ** 2) / (r * 1.6)
    v = 1 - np.clip(d, 0, 1)
    bay = BAY[c.yy % 4, c.xx % 4] - 0.5
    n = len(ramp)
    idx = np.clip(np.floor(v * (n - 1) + 0.5 + bay * 0.5), 0, n - 1).astype(int)
    col = np.array(ramp, np.uint8)[idx]
    c.c[m] = col[m]; c.a[m] = True


def flame(c, cx, base_y, h, hw, ph, ramp, sway=1.0, lick=0.0, seed=0, hard=False, pw=1.5):
    """Llama vertical: ramp[0] borde ... ramp[-1] nucleo. Se pinta en la capa base."""
    n = len(ramp)
    for y in range(int(base_y - h), int(base_y) + 1):
        t = (base_y - y) / float(h)
        if t < 0 or t > 1:
            continue
        sx = math.sin(ph + t * 3.2) * t * 1.6 * sway + math.sin(ph * 2 + t * 7 + seed) * t * 0.7 * lick
        w = hw * (1 - t ** pw) ** 0.85 + 0.0
        w += math.sin(ph * 3 + y * 0.9 + seed) * 0.5 * (1 - t)
        for x in range(int(cx - hw - 4), int(cx + hw + 5)):
            u = abs(x + 0.5 - (cx + sx)) / max(w, 0.3)
            if u > 1.0:
                continue
            v = (1 - u) * 0.8 + (1 - t) * 0.35 - 0.1
            bay = BAY[y % 4, x % 4] - 0.5
            i = int(max(0, min(n - 1, math.floor(v * (n - 1) * 1.15 + 0.35 + bay * 0.6))))
            c.px(x, y, ramp[i])
