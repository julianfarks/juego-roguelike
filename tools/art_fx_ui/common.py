"""Utilidades comunes del kit art_fx_ui: ruido, render de calor->rampa, lienzo de paleta con supermuestreo, hojas, previews."""
import os, json, math
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

ROOT = '/home/claude/juego-roguelike'
A = ROOT + '/Shared/assets'
PREV = ROOT + '/tools/previews/art_fx_ui'


def ensure(p):
    os.makedirs(p, exist_ok=True)


def hx(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def RS(seed):
    return np.random.RandomState(seed)


BAY = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], float) / 16 - 0.5


def bayer_field(H, W):
    return np.tile(BAY, (H // 4 + 1, W // 4 + 1))[:H, :W]


def grid(W, H, cx=None, cy=None):
    cx = W / 2 if cx is None else cx
    cy = H / 2 if cy is None else cy
    ys, xs = np.mgrid[0:H, 0:W]
    return xs + 0.5 - cx, ys + 0.5 - cy


# ---------------- ruido ----------------
def _h(ix, iy, seed):
    n = (ix.astype(np.uint32) * np.uint32(374761393) + iy.astype(np.uint32) * np.uint32(668265263)
         + np.uint32((seed * 2246822519 + 3266489917) & 0xffffffff))
    n = (n ^ (n >> np.uint32(13))) * np.uint32(1274126177)
    n = n ^ (n >> np.uint32(16))
    return (n & np.uint32(0xffff)).astype(np.float64) / 65535.0


def vnoise(X, Y, seed=0, px=None):
    x0 = np.floor(X)
    y0 = np.floor(Y)
    fx = X - x0
    fy = Y - y0
    fx = fx * fx * (3 - 2 * fx)
    fy = fy * fy * (3 - 2 * fy)
    ix = x0.astype(np.int64)
    iy = y0.astype(np.int64)

    def g(a, b):
        if px:
            a = a % px
        return _h(a, b, seed)
    a = g(ix, iy) * (1 - fx) + g(ix + 1, iy) * fx
    b = g(ix, iy + 1) * (1 - fx) + g(ix + 1, iy + 1) * fx
    return a * (1 - fy) + b * fy


def fbm(X, Y, seed=0, octs=3, px=None):
    t = 0
    amp = 1.0
    tot = 0
    f = 1
    for o in range(octs):
        t = t + amp * vnoise(X * f, Y * f, seed + o * 17, (px * f) if px else None)
        tot += amp
        amp *= 0.5
        f *= 2
    return t / tot


# ---------------- campos ----------------
def capsule(X, Y, x0, y0, x1, y1, r0, r1=None):
    r1 = r0 if r1 is None else r1
    vx, vy = x1 - x0, y1 - y0
    L2 = vx * vx + vy * vy + 1e-9
    t = np.clip(((X - x0) * vx + (Y - y0) * vy) / L2, 0, 1)
    d = np.hypot(X - (x0 + t * vx), Y - (y0 + t * vy))
    r = r0 + (r1 - r0) * t
    return np.clip(1 - d / np.maximum(r, 1e-3), 0, 1)


def disc(X, Y, cx, cy, r):
    return np.clip(1 - np.hypot(X - cx, Y - cy) / max(r, 1e-3), 0, 1)


def ring(X, Y, cx, cy, r, w):
    return np.clip(1 - np.abs(np.hypot(X - cx, Y - cy) - r) / max(w, 1e-3), 0, 1)


def star4(X, Y, cx, cy, ax, ay=None, p=0.5):
    ay = ax if ay is None else ay
    return np.clip(1 - ((np.abs(X - cx) / max(ax, 1e-3)) ** p + (np.abs(Y - cy) / max(ay, 1e-3)) ** p), 0, 1)


def smooth(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = min(max(t, 0), 1)
    return 1 - (1 - t) ** 2.2


# ---------------- render ----------------
def ramp_arr(ramp):
    return np.array([c[:3] for c in ramp], float)


def heat_rgba(heat, ramp, thr=0.10, glow=0.0, dith=0.12, mul=1.0):
    H, W = heat.shape
    h = heat + bayer_field(H, W) * dith
    L = len(ramp)
    on = h >= thr
    idx = np.clip(((h - thr) / (1.0001 - thr) * L).astype(int), 0, L - 1)
    ra = ramp_arr(ramp)
    out = np.zeros((H, W, 4))
    out[..., :3] = ra[idx]
    out[..., 3] = np.where(on, 255.0, 0) * mul
    if glow > 0:
        g = (~on) & (h >= thr * 0.45)
        out[g, :3] = ra[0]
        out[g, 3] = 255 * glow * mul
    return out


def blank(W, H):
    return np.zeros((H, W, 4))


def over(dst, src):
    sa = src[..., 3:4] / 255.0
    da = dst[..., 3:4] / 255.0
    oa = sa + da * (1 - sa)
    rgb = (src[..., :3] * sa + dst[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-6)
    return np.concatenate([rgb, oa * 255], -1)


def to_u8(img):
    a = np.clip(np.rint(img), 0, 255).astype(np.uint8)
    a[a[..., 3] == 0] = 0
    return a


def outline(img, factor=0.30, tint=(0.9, 0.85, 1.15), diag=False, alpha_min=200):
    """Contorno exterior de 1 px (selout): color del vecino oscurecido. img float RGBA."""
    a = img[..., 3] >= alpha_min
    k = np.ones((3, 3), bool) if diag else np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)
    dil = ndi.binary_dilation(a, k)
    edge = dil & ~a & (img[..., 3] < 20)
    # color: promedio de vecinos opacos
    out = img.copy()
    wsum = np.zeros(a.shape)
    csum = np.zeros(a.shape + (3,))
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if (dx == 0 and dy == 0) or (not diag and dx != 0 and dy != 0):
                continue
            s = np.roll(np.roll(a, dy, 0), dx, 1)
            c = np.roll(np.roll(img[..., :3], dy, 0), dx, 1)
            wsum += s
            csum += c * s[..., None]
    avg = csum / np.maximum(wsum, 1)[..., None]
    col = avg * factor * np.array(tint)
    out[edge, :3] = col[edge]
    out[edge, 3] = 255
    return out


# ---------------- lienzo de paleta con supermuestreo ----------------
class PC:
    def __init__(self, W, H, S=3, cov=0.45):
        self.W, self.H, self.S, self.cov = W, H, S, cov
        self.pal = [(0, 0, 0, 0)]
        self.im = Image.new('L', (W * S, H * S), 0)
        self.d = ImageDraw.Draw(self.im)

    def c(self, col):
        col = tuple(int(v) for v in col)
        if len(col) == 3:
            col = col + (255,)
        if col not in self.pal:
            self.pal.append(col)
        return self.pal.index(col)

    def _p(self, pts):
        return [(x * self.S, y * self.S) for x, y in pts]

    def poly(self, pts, col):
        self.d.polygon(self._p(pts), fill=self.c(col))

    def line(self, p0, p1, col, w=1.0):
        S = self.S
        self.d.line([(p0[0] * S, p0[1] * S), (p1[0] * S, p1[1] * S)], fill=self.c(col), width=max(1, int(round(w * S))))

    def lines(self, pts, col, w=1.0):
        for a, b in zip(pts[:-1], pts[1:]):
            self.line(a, b, col, w)
            r = w / 2
            self.circ(b[0], b[1], r, col)
        self.circ(pts[0][0], pts[0][1], w / 2, col)

    def ell(self, cx, cy, rx, ry, col):
        S = self.S
        self.d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S - 1, (cy + ry) * S - 1], fill=self.c(col))

    def circ(self, cx, cy, r, col):
        self.ell(cx, cy, r, r, col)

    def rect(self, x0, y0, x1, y1, col):
        S = self.S
        if x1 <= x0 or y1 <= y0:
            return
        self.d.rectangle([x0 * S, y0 * S, max(x0 * S, x1 * S - 1), max(y0 * S, y1 * S - 1)], fill=self.c(col))

    def px(self, x, y, col):
        self.rect(x, y, x + 1, y + 1, col)

    def out(self):
        S = self.S
        arr = np.array(self.im)
        H, W = self.H, self.W
        blk = arr.reshape(H, S, W, S).transpose(0, 2, 1, 3).reshape(H, W, S * S)
        n = len(self.pal)
        cnt = np.stack([(blk == k).sum(-1) for k in range(n)], -1)
        solid = S * S - cnt[..., 0]
        cnt2 = cnt.copy()
        cnt2[..., 0] = -1
        best = cnt2.argmax(-1)
        on = solid >= max(1, int(math.ceil(self.cov * S * S)))
        palarr = np.array(self.pal, float)
        out = palarr[best]
        out[~on] = 0
        return out


def shade_mask(mask, ramp, light=(-0.55, -0.7), bias=0.0, rim=True, strength=1.4):
    """Sombreado por distancia al borde: devuelve rgb para cada pixel de mask. ramp: lista de colores oscuro->claro."""
    d = ndi.distance_transform_edt(np.pad(mask, 1))[1:-1, 1:-1]
    ds = ndi.gaussian_filter(np.minimum(d, 3.5), 0.6)
    gy, gx = np.gradient(ds)
    nz = 1.0 / strength
    nx, ny = -gx, -gy
    ln = np.sqrt(nx * nx + ny * ny + nz * nz)
    lx, ly = light
    lz = math.sqrt(max(0.05, 1 - lx * lx - ly * ly))
    dot = (nx * lx + ny * ly + nz * lz) / ln
    t = np.clip((dot - 0.35) / 0.65, 0, 1)
    t = np.clip(t + bias + 0.12 * np.minimum(d, 3) / 3, 0, 0.999)
    L = len(ramp)
    idx = (t * L).astype(int)
    ra = np.array([c[:3] for c in ramp], float)
    return ra[idx], idx


# ---------------- hojas ----------------
def save_sheet(folder, name, W, H, rows, pivot, body=None, extra=None):
    maxn = max(len(r[1]) for r in rows)
    sheet = np.zeros((len(rows) * H, maxn * W, 4), np.uint8)
    anims = {}
    for ri, row in enumerate(rows):
        an, frames, fps, loop = row[:4]
        for fi, f in enumerate(frames):
            sheet[ri * H:(ri + 1) * H, fi * W:(fi + 1) * W] = to_u8(f)
        anims[an] = {"row": ri, "n": len(frames), "fps": fps, "loop": bool(loop)}
        if len(row) > 4:
            anims[an].update(row[4])
    d = {"cell": [W, H], "pivot": list(pivot), "body": list(body or [W // 2, H // 2]), "anims": anims}
    if extra:
        d.update(extra)
    p = os.path.join(A, folder)
    ensure(p)
    Image.fromarray(sheet, 'RGBA').save(os.path.join(p, name + '.png'), optimize=True)
    json.dump(d, open(os.path.join(p, name + '.json'), 'w'), indent=1)


def _label(d, xy, txt, col=(200, 200, 220)):
    d.text(xy, txt, fill=col)


def preview_sheets(folder, names, out, scale=3, bg=(22, 18, 32), maxw=1900):
    """Apila hojas ampliadas sobre fondo oscuro con etiquetas."""
    blocks = []
    for nm in names:
        im = Image.open(os.path.join(A, folder, nm + '.png')).convert('RGBA')
        d = json.load(open(os.path.join(A, folder, nm + '.json')))
        W, H = d['cell']
        for an, a in d['anims'].items():
            n = a['n']
            row = Image.new('RGBA', (n * (W * scale + 4) + 90, H * scale + 4), bg + (255,))
            dr = ImageDraw.Draw(row)
            dr.text((2, 2), nm.replace('fx_', ''), fill=(255, 220, 120))
            dr.text((2, 14), an, fill=(180, 200, 255))
            for i in range(n):
                fr = im.crop((i * W, a['row'] * H, (i + 1) * W, (a['row'] + 1) * H))
                fr = fr.resize((W * scale, H * scale), Image.NEAREST)
                x = 90 + i * (W * scale + 4)
                dr.rectangle([x - 1, 1, x + W * scale, H * scale + 2], outline=(50, 46, 70))
                px, py = int(d['pivot'][0] * scale), int(d['pivot'][1] * scale)
                row.alpha_composite(fr, (x, 2))
                dr.point((x + px, 2 + py), fill=(255, 0, 255))
            blocks.append(row)
    # empaquetar en columnas
    Wt = max(b.width for b in blocks)
    cols = max(1, maxw // Wt)
    colh = [0] * cols
    pos = []
    for b in blocks:
        c = colh.index(min(colh))
        pos.append((c * Wt, colh[c]))
        colh[c] += b.height + 2
    sheet = Image.new('RGBA', (cols * Wt, max(colh)), (10, 8, 16, 255))
    for b, p in zip(blocks, pos):
        sheet.alpha_composite(b, p)
    ensure(os.path.dirname(out))
    sheet.convert('RGB').save(out)
