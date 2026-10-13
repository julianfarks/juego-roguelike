"""Kit de pixel art procedural para el mundo (tilesets + fondos)."""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + .5) / 16 - .5


def hexrgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def ramp(*hs):
    return np.stack([hexrgb(h) for h in hs])


def mix(a, b, t):
    return a + (b - a) * t


def rng(seed):
    return np.random.RandomState(seed & 0x7fffffff)


def vnoise(w, h, cx, cy, seed):
    """Ruido de valor periodico en x e y."""
    g = rng(seed).rand(cy, cx)
    xs = np.arange(w) / w * cx
    ys = np.arange(h) / h * cy
    x0 = np.floor(xs).astype(int)
    y0 = np.floor(ys).astype(int)
    fx = xs - x0
    fy = ys - y0
    fx = fx * fx * (3 - 2 * fx)
    fy = fy * fy * (3 - 2 * fy)
    x1 = (x0 + 1) % cx
    y1 = (y0 + 1) % cy
    x0 %= cx
    y0 %= cy
    a = g[np.ix_(y0, x0)]
    b = g[np.ix_(y0, x1)]
    c = g[np.ix_(y1, x0)]
    d = g[np.ix_(y1, x1)]
    top = a + (b - a) * fx[None, :]
    bot = c + (d - c) * fx[None, :]
    return top + (bot - top) * fy[:, None]


def fbm(w, h, cx, cy, octv=4, seed=0, gain=.5):
    tot = np.zeros((h, w))
    amp = 1.0
    s = 0
    for i in range(octv):
        tot += amp * vnoise(w, h, cx * 2 ** i, cy * 2 ** i, seed + i * 101)
        s += amp
        amp *= gain
    return tot / s


def dither_idx(lum, n, ox=0, oy=0, amp=1.0):
    """lum 0..1 -> indice de rampa con dither Bayer."""
    h, w = lum.shape
    b = np.tile(BAYER, (h // 4 + 2, w // 4 + 2))[oy % 4:oy % 4 + h, ox % 4:ox % 4 + w]
    return np.clip(np.floor(lum * (n - 1) + .5 + b * amp * .9), 0, n - 1).astype(int)


def lights(H, wrap=True):
    """Brillo por pendiente con luz arriba-izquierda. H altura."""
    if wrap:
        gx = (np.roll(H, -1, 1) - np.roll(H, 1, 1)) / 2
        gy = (np.roll(H, -1, 0) - np.roll(H, 1, 0)) / 2
    else:
        gy, gx = np.gradient(H)
    return gx + gy  # >0 => cara hacia la luz


def darken(c, f):
    return np.clip(np.asarray(c, np.float32) * f, 0, 255)


def shift_hue_cool(c, k=.2):
    c = np.asarray(c, np.float32)
    return np.clip(c * (1 - k) + np.array([40, 40, 90]) * k, 0, 255)


# ---------------------------------------------------------------- patrones periodicos 16x16
def bricks(rows, bw, offsets=None, mortar=1, W=16, H=16):
    """Devuelve (dist_al_mortar, id_ladrillo, straddle, row). Periodico en W,H.
    rows: alto de cada hilada (H%rows==0). bw: ancho del ladrillo (W%bw==0)."""
    nr = H // rows
    if offsets is None:
        offsets = [(i % 2) * (bw // 2) for i in range(nr)]
    d = np.zeros((H, W), np.float32)
    bid = np.zeros((H, W), int)
    strad = np.zeros((H, W), bool)
    rowi = np.zeros((H, W), int)
    for y in range(H):
        r = y // rows
        ly = y % rows
        off = offsets[r]
        for x in range(W):
            xx = (x - off) % W
            k = xx // bw
            lx = xx % bw
            xs = (k * bw + off) % W
            strad[y, x] = (xs + bw > W)
            bid[y, x] = k
            rowi[y, x] = r
            # mortero en la ultima fila y ultima columna del ladrillo
            dxm = min(lx, bw - 1 - lx - (mortar - 1)) if mortar else min(lx, bw - 1 - lx)
            dym = min(ly, rows - 1 - ly - (mortar - 1)) if mortar else min(ly, rows - 1 - ly)
            if mortar:
                if lx >= bw - mortar or ly >= rows - mortar:
                    d[y, x] = 0
                else:
                    d[y, x] = 1 + min(lx, bw - mortar - 1 - lx, ly, rows - mortar - 1 - ly)
            else:
                d[y, x] = 1 + min(lx, bw - 1 - lx, ly, rows - 1 - ly)
    return d, bid, strad, rowi


def voronoi(n, seed, W=16, H=16, jitter=1.0):
    """Celdas voronoi periodicas: (id, dist1, dist2-dist1 (borde))."""
    r = rng(seed)
    side = int(np.ceil(np.sqrt(n)))
    pts = []
    for j in range(side):
        for i in range(side):
            px = (i + .5 + (r.rand() - .5) * jitter) * W / side
            py = (j + .5 + (r.rand() - .5) * jitter) * H / side
            pts.append((px, py))
    pts = np.array(pts)
    yy, xx = np.mgrid[0:H, 0:W]
    best = np.full((H, W), 1e9)
    sec = np.full((H, W), 1e9)
    bid = np.zeros((H, W), int)
    for k, (px, py) in enumerate(pts):
        for ox in (-W, 0, W):
            for oy in (-H, 0, H):
                d = np.hypot(xx + .5 - px - ox, yy + .5 - py - oy)
                m = d < best
                sec = np.where(m, best, np.where(d < sec, d, sec))
                bid = np.where(m, k, bid)
                best = np.where(m, d, best)
    return bid, best, sec - best


# ---------------------------------------------------------------- sprites con forma
SS = 8


def poly_mask(points, w=16, h=16, ss=SS):
    im = Image.new('L', (w * ss, h * ss), 0)
    ImageDraw.Draw(im).polygon([(x * ss, y * ss) for x, y in points], fill=255)
    a = np.asarray(im.resize((w, h), Image.BOX), np.float32) / 255
    return a > .5


def ellipse_mask(cx, cy, rx, ry, w=16, h=16, ss=SS):
    im = Image.new('L', (w * ss, h * ss), 0)
    ImageDraw.Draw(im).ellipse([(cx - rx) * ss, (cy - ry) * ss, (cx + rx) * ss - 1, (cy + ry) * ss - 1], fill=255)
    a = np.asarray(im.resize((w, h), Image.BOX), np.float32) / 255
    return a > .5


def line_mask(x0, y0, x1, y1, wd=1.0, w=16, h=16, ss=SS):
    im = Image.new('L', (w * ss, h * ss), 0)
    ImageDraw.Draw(im).line([(x0 * ss, y0 * ss), (x1 * ss, y1 * ss)], fill=255, width=max(1, int(wd * ss)))
    a = np.asarray(im.resize((w, h), Image.BOX), np.float32) / 255
    return a > .45


def rect_mask(x0, y0, x1, y1, w=16, h=16):
    m = np.zeros((h, w), bool)
    m[int(y0):int(y1), int(x0):int(x1)] = True
    return m


class Canvas:
    def __init__(self, w=16, h=16):
        self.w, self.h = w, h
        self.rgb = np.zeros((h, w, 3), np.float32)
        self.a = np.zeros((h, w), bool)
        self.glow = np.zeros((h, w), bool)  # pixeles que no llevan contorno

    def shape(self, mask, rmp, shade=1.0, base=None, light=(-1, -1), rim=True, flat=None, dither=True, noline=False):
        """Rellena mascara con volumen: rampa rmp (n,3)."""
        mask = mask & True
        if not mask.any():
            return self
        n = len(rmp)
        if flat is not None:
            idx = np.full(mask.shape, flat)
        else:
            dist = ndi.distance_transform_edt(np.pad(mask, 1))[1:-1, 1:-1]
            hgt = np.minimum(dist, 3.0) / 3.0
            hgt = ndi.gaussian_filter(np.pad(hgt, 2, mode='edge'), .6)[2:-2, 2:-2]
            gy, gx = np.gradient(hgt)
            l = -(gx * light[0] + gy * light[1]) * -1
            lum = (base if base is not None else .55) + (gx * -light[0] + gy * -light[1]) * 1.6 * shade * -1
            # luz: superficie que sube hacia la derecha/abajo (gx>0) mira a izquierda => iluminada
            lum = (base if base is not None else .5) + (gx + gy) * .9 * shade + (hgt - .5) * .25
            idx = dither_idx(lum, n, 0, 0, .6 if dither else 0)
        ys, xs = np.nonzero(mask)
        self.rgb[ys, xs] = rmp[np.clip(idx[ys, xs], 0, n - 1)]
        self.a[ys, xs] = True
        if noline:
            self.glow[ys, xs] = True
        return self

    def fill(self, mask, col, noline=False):
        ys, xs = np.nonzero(mask)
        self.rgb[ys, xs] = col
        self.a[ys, xs] = True
        if noline:
            self.glow[ys, xs] = True
        return self

    def px(self, x, y, col, noline=False):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.rgb[y, x] = col
            self.a[y, x] = True
            if noline:
                self.glow[y, x] = True
        return self

    def erase(self, mask):
        self.a[mask] = False
        return self

    def outline(self, f=.38, tint=(10, 8, 24), skip_top=False):
        pad = np.pad(self.a, 1)
        solid = pad[1:-1, 1:-1]
        nb = np.zeros_like(solid)
        cols = np.zeros((self.h, self.w, 3), np.float32)
        cnt = np.zeros((self.h, self.w), np.float32)
        rgbp = np.pad(self.rgb, ((1, 1), (1, 1), (0, 0)))
        ap = pad.astype(np.float32)
        gp = np.pad(self.glow, 1)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            sh = pad[1 + dy:1 + dy + self.h, 1 + dx:1 + dx + self.w]
            g = gp[1 + dy:1 + dy + self.h, 1 + dx:1 + dx + self.w]
            use = sh & ~g
            nb |= use
            cols += rgbp[1 + dy:1 + dy + self.h, 1 + dx:1 + dx + self.w] * use[..., None]
            cnt += use
        new = nb & ~solid
        c = cols / np.maximum(cnt, 1)[..., None]
        c = c * f + np.array(tint, np.float32) * (1 - f) * .35
        ys, xs = np.nonzero(new)
        self.rgb[ys, xs] = c[ys, xs]
        self.a[ys, xs] = True
        return self

    def to_img(self):
        out = np.zeros((self.h, self.w, 4), np.uint8)
        out[..., :3] = np.clip(self.rgb + .5, 0, 255).astype(np.uint8)
        out[..., 3] = np.where(self.a, 255, 0)
        out[~self.a, :3] = 0
        return out

    def blit(self, other, ox=0, oy=0):
        for y in range(other.h):
            for x in range(other.w):
                if other.a[y, x]:
                    self.px(x + ox, y + oy, other.rgb[y, x], other.glow[y, x])
        return self


def put(sheet, col, row, arr):
    sheet[row * 16:(row + 1) * 16, col * 16:(col + 1) * 16] = arr


def save_png(arr, path):
    Image.fromarray(arr, 'RGBA').save(path, optimize=True)


def save_quant(img, path, colors=64):
    """Cuantiza (RGB u RGBA) preservando alfa y guarda optimizado."""
    if img.mode == 'RGBA':
        q = img.quantize(colors=colors, method=Image.FASTOCTREE, dither=Image.NONE)
    else:
        q = img.quantize(colors=colors, method=Image.MEDIANCUT, dither=Image.NONE)
    q.save(path, optimize=True)
