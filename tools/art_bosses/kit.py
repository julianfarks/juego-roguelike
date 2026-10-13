"""Kit de arte para jefes: partes jerarquicas con altura/textura/emision, render supermuestreado,
sombreado volumetrico por mapa de altura, rampas de color, contorno selectivo y capa de FX."""
import math, json, os, zlib
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

SS = 3
HS = 24.0          # escala de empaquetado de altura
LIGHT = np.array([-0.55, -0.66, 0.52]); LIGHT = LIGHT / np.linalg.norm(LIGHT)
BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) + 0.5) / 16.0 - 0.5


# ---------------------------------------------------------------- color
def C(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def clampc(c):
    return tuple(int(round(max(0, min(255, v)))) for v in c)


def ramp(dark, mid, light, n=6):
    cols = []
    for i in range(n):
        t = i / (n - 1)
        c = lerp(dark, mid, t / 0.5) if t <= 0.5 else lerp(mid, light, (t - 0.5) / 0.5)
        cols.append(clampc(c))
    return cols


def auto(mid, shadow=(34, 22, 78), warm=(255, 236, 176), n=6, dk=0.26, lk=0.38, boost=1.32):
    mid = C(mid) if isinstance(mid, str) else mid
    shadow = C(shadow) if isinstance(shadow, str) else shadow
    warm = C(warm) if isinstance(warm, str) else warm
    dark = lerp(tuple(v * dk for v in mid), shadow, 0.30)
    light = lerp(tuple(min(255, v * boost + 6) for v in mid), warm, lk)
    return ramp(dark, mid, light, n)


def glowramp(*cols):
    cols = [C(c) if isinstance(c, str) else c for c in cols]
    return cols


class Mat:
    def __init__(self, rmp, glow=None, gain=1.0, texamt=0.55, rim=True, spec=0.0):
        self.ramp = rmp; self.glow = glow; self.gain = gain; self.texamt = texamt; self.rim = rim; self.spec = spec


# ---------------------------------------------------------------- ruido
def fbm(h, w, scale, octs=3, seed=0):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32); amp = 1.0; tot = 0.0
    for o in range(octs):
        s = max(1.0, scale / (2 ** o))
        gh = max(2, int(h / s) + 2); gw = max(2, int(w / s) + 2)
        g = rng.random((gh, gw)).astype(np.float32)
        z = np.asarray(Image.fromarray(g, 'F').resize((w, h), Image.BICUBIC), np.float32)
        out += z * amp; tot += amp; amp *= 0.5
    out /= tot
    lo, hi = out.min(), out.max()
    return (out - lo) / max(1e-6, hi - lo)


# ---------------------------------------------------------------- geometria
def ell_pts(cx, cy, rx, ry, rot=0.0, n=44):
    a = np.linspace(0, 2 * math.pi, n, endpoint=False)
    x = np.cos(a) * rx; y = np.sin(a) * ry
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return np.stack([cx + x * c - y * s, cy + x * s + y * c], 1)


def catmull(pts, closed=False, per=8):
    p = np.asarray(pts, np.float64)
    n = len(p)
    if n < 3:
        return p
    out = []
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = p[(i - 1) % n] if (closed or i > 0) else p[0] * 2 - p[1]
        p1 = p[i]; p2 = p[(i + 1) % n]
        p3 = p[(i + 2) % n] if (closed or i + 2 < n) else p[-1] * 2 - p[-2]
        for k in range(per):
            t = k / per
            t2 = t * t; t3 = t2 * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    if not closed:
        out.append(p[-1])
    return np.array(out)


def bez(p0, p1, p2, p3=None, n=14):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2 = [np.asarray(q, float) for q in (p0, p1, p2)]
    if p3 is None:
        return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2
    p3 = np.asarray(p3, float)
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3


def tube_prims(pts, r0, r1=None, spline=True, rs=None):
    pts = np.asarray(pts, float)
    if spline and len(pts) > 2:
        path = catmull(pts, False, 8)
    else:
        path = pts
    # remuestreo por longitud
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(path, axis=0).T))]
    L = d[-1]
    if L < 1e-6:
        return [('c', path[0][0], path[0][1], r0)]
    m = max(2, int(L / 0.6))
    s = np.linspace(0, L, m)
    x = np.interp(s, d, path[:, 0]); y = np.interp(s, d, path[:, 1])
    if rs is not None:
        rr = np.interp(s / L, np.linspace(0, 1, len(rs)), rs)
    else:
        r1 = r0 if r1 is None else r1
        rr = r0 + (r1 - r0) * (s / L)
    return [('c', x[i], y[i], rr[i]) for i in range(m)]


class Part:
    def __init__(self, name, parent=None, at=(0, 0), z=0, mat=None, depth=4.0, noise=0.0, nscale=3.0,
                 tnoise=0.25, tscale=2.5, dim=0.0, seam=True, seed=0, ghost=False, rimk=1.0):
        self.name = name; self.parent = parent; self.at = at; self.z = z; self.mat = mat
        self.depth = depth; self.noise = noise; self.nscale = nscale; self.tnoise = tnoise; self.tscale = tscale
        self.dim = dim; self.seam = seam; self.seed = seed; self.ghost = ghost; self.rimk = rimk
        self.ops = []; self.built = False; self.matnames = [mat]

    # ---- construccion de operaciones
    def _op(self, ch, prims, v=1.0, soft=0.0, mat=None, raise_=0.0, edge=None, grow=True):
        if mat is not None:
            if grow:
                self.ops.append(('add', prims, 1.0, (0, 0, None)))
            if mat not in self.matnames:
                self.matnames.append(mat)
            ch = 'mat'; v = self.matnames.index(mat)
        self.ops.append((ch, prims, v, (soft, raise_, edge))); return self

    def poly(self, pts, op='add', v=1.0, soft=0.0, **kw):
        return self._op(op, [('p', np.asarray(pts, float))], v, soft, **kw)

    def ell(self, cx, cy, rx, ry, rot=0.0, op='add', v=1.0, soft=0.0, **kw):
        return self._op(op, [('p', ell_pts(cx, cy, rx, ry, rot))], v, soft, **kw)

    def spl(self, pts, closed=True, op='add', v=1.0, soft=0.0, per=7, **kw):
        return self._op(op, [('p', catmull(pts, closed, per))], v, soft, **kw)

    def tube(self, pts, r0, r1=None, op='add', v=1.0, soft=0.0, spline=True, rs=None, **kw):
        return self._op(op, tube_prims(pts, r0, r1, spline, rs), v, soft, **kw)

    def line(self, pts, w=1.0, op='tex', v=0.1, soft=0.0, spline=False, **kw):
        return self._op(op, tube_prims(pts, w / 2.0, None, spline), v, soft, **kw)

    def fn(self, f):
        self.ops.append(('fn', f, 0, (0, 0, None))); return self

    # ---- patrones
    def brick(self, bw, bh, v=0.18, w=0.8, jit=0.18, seed=1, skew=0.5):
        def f(ctx):
            rng = np.random.default_rng(seed + self.seed)
            T = ctx['T']; mask = ctx['mask']
            Hh, Ww = T.shape
            im = Image.new('F', (Ww, Hh), 0.0)
            ox, oy = ctx['ox'], ctx['oy']
            rows = int(Hh / SS / bh) + 2
            for j in range(rows):
                y0 = oy + j * bh
                off = (j % 2) * bw * skew
                nx = int(Ww / SS / bw) + 3
                for i in range(-1, nx):
                    x0 = ox + i * bw + off
                    val = 0.5 + (rng.random() - 0.5) * 2 * jit
                    X0, Y0 = (x0 - ox) * SS, (y0 - oy) * SS
                    ImageDraw.Draw(im).rectangle([X0, Y0, X0 + bw * SS, Y0 + bh * SS], fill=float(val))
            arr = np.asarray(im)
            T[:] = np.where(arr > 0, arr * 0.5 + T * 0.5, T)
            # juntas
            dr = Image.new('L', (Ww, Hh), 0); d = ImageDraw.Draw(dr)
            for j in range(rows + 1):
                yy = (j * bh) * SS
                d.line([0, yy, Ww, yy], fill=255, width=max(1, int(w * SS)))
                off = (j % 2) * bw * skew
                for i in range(-1, int(Ww / SS / bw) + 3):
                    xx = (i * bw + off) * SS
                    d.line([xx, yy, xx, yy + bh * SS], fill=255, width=max(1, int(w * SS)))
            m = np.asarray(dr) > 0
            T[m] = v
        return self.fn(f)

    def scales(self, r, v=0.2, w=0.8, rows_off=0.5):
        def f(ctx):
            T = ctx['T']; Hh, Ww = T.shape
            im = Image.new('L', (Ww, Hh), 0); d = ImageDraw.Draw(im)
            ny = int(Hh / SS / (r * 0.8)) + 2
            nx = int(Ww / SS / (r * 2)) + 2
            for j in range(ny):
                for i in range(-1, nx):
                    cx = (i * r * 2 + (j % 2) * r) * SS; cy = j * r * 0.8 * SS
                    d.arc([cx - r * SS, cy - r * SS, cx + r * SS, cy + r * SS], 10, 170, fill=255, width=max(1, int(w * SS)))
            T[np.asarray(im) > 0] = v
        return self.fn(f)

    def hatch(self, sp, ang=60, v=0.2, w=0.7, jit=0.0, seed=2):
        def f(ctx):
            T = ctx['T']; Hh, Ww = T.shape
            im = Image.new('L', (Ww, Hh), 0); d = ImageDraw.Draw(im)
            rng = np.random.default_rng(seed + self.seed)
            a = math.radians(ang); dx, dy = math.cos(a), math.sin(a)
            diag = math.hypot(Ww, Hh)
            k = -diag
            while k < diag:
                px, py = Ww / 2 + (-dy) * k, Hh / 2 + dx * k
                d.line([px - dx * diag, py - dy * diag, px + dx * diag, py + dy * diag], fill=255, width=max(1, int(w * SS)))
                k += sp * SS * (1 + (rng.random() - 0.5) * jit)
            T[np.asarray(im) > 0] = v
        return self.fn(f)

    def cracks(self, n=5, length=14, v=0.05, w=0.8, seed=3, emit=0.0, branch=0.5, soft=0.0, spread=0.6):
        def f(ctx):
            rng = np.random.default_rng(seed + self.seed)
            mask = ctx['mask']; Hh, Ww = mask.shape
            ys, xs = np.nonzero(mask)
            if len(xs) == 0:
                return
            im = Image.new('L', (Ww, Hh), 0); d = ImageDraw.Draw(im)

            def walk(x, y, ang, ln, depth):
                pts = [(x, y)]
                steps = max(2, int(ln))
                for _ in range(steps):
                    ang += (rng.random() - 0.5) * spread * 2
                    x += math.cos(ang) * SS * 1.1; y += math.sin(ang) * SS * 1.1
                    if not (0 <= int(x) < Ww and 0 <= int(y) < Hh) or not mask[int(y), int(x)]:
                        break
                    pts.append((x, y))
                    if depth < 2 and rng.random() < branch * 0.12:
                        walk(x, y, ang + (rng.random() - 0.5) * 2.2, ln * 0.5, depth + 1)
                if len(pts) > 1:
                    d.line(pts, fill=255, width=max(1, int(w * SS)))
            for _ in range(n):
                k = rng.integers(len(xs))
                walk(float(xs[k]), float(ys[k]), rng.random() * 6.28, length, 0)
            m = np.asarray(im, np.float32) / 255
            if soft:
                m = ndi.gaussian_filter(m, soft * SS)
            ctx['T'][:] = ctx['T'] * (1 - m) + v * m
            if emit > 0:
                m2 = ndi.gaussian_filter(m, 0.6 * SS) if soft == 0 else m
                ctx['E'][:] = np.maximum(ctx['E'], np.clip(m2 * 1.6, 0, 1) * emit)
        return self.fn(f)

    def blotch(self, mat, thr=0.66, scale=3.0, seed=7, raise_=0.0, tmod=None, within=None):
        if mat not in self.matnames:
            self.matnames.append(mat)
        idx = self.matnames.index(mat)

        def f(ctx):
            T = ctx['T']; Hh, Ww = T.shape
            nz = fbm(Hh, Ww, scale * SS, 3, seed + self.seed * 3)
            sel = (nz > thr) & ctx['mask']
            if within is not None:
                sel &= ctx['sub'] == within
            ctx['sub'][sel] = idx
            if raise_:
                ctx['bump'][sel] += raise_
        return self.fn(f)

    def speckle(self, dens=0.04, v=0.85, seed=5, size=1.0):
        def f(ctx):
            rng = np.random.default_rng(seed + self.seed)
            T = ctx['T']; mask = ctx['mask']
            r = rng.random(T.shape) < dens / (SS * SS) * 3
            r = ndi.binary_dilation(r, iterations=max(0, int(size * SS / 3)))
            T[r & mask] = v
        return self.fn(f)

    # ---- construccion
    def build(self):
        if self.built:
            return
        pts = []
        for ch, pr, v, _sf in self.ops:
            if ch == 'add':
                for p in pr:
                    if p[0] == 'p':
                        pts.append(p[1])
                    else:
                        pts.append(np.array([[p[1] - p[3], p[2] - p[3]], [p[1] + p[3], p[2] + p[3]]]))
        if not pts:
            self.built = True; self.empty = True; return
        allp = np.vstack(pts)
        x0 = math.floor(allp[:, 0].min()) - 2; y0 = math.floor(allp[:, 1].min()) - 2
        x1 = math.ceil(allp[:, 0].max()) + 2; y1 = math.ceil(allp[:, 1].max()) + 2
        self.empty = False
        self.ox, self.oy = x0, y0
        W, H = int((x1 - x0) * SS), int((y1 - y0) * SS)
        self.size = (W, H)
        mask_im = Image.new('L', (W, H), 0)
        bump = np.zeros((H, W), np.float32)
        T = 0.5 + (fbm(H, W, self.tscale * SS, 3, self.seed + 11) - 0.5) * 2 * self.tnoise
        T = T.astype(np.float32)
        E = np.zeros((H, W), np.float32)

        def draw(dr, prims, fill):
            for p in prims:
                if p[0] == 'p':
                    q = [((float(a) - x0) * SS, (float(b) - y0) * SS) for a, b in p[1]]
                    if len(q) >= 3:
                        dr.polygon(q, fill=fill)
                    elif len(q) == 2:
                        dr.line(q, fill=fill, width=SS)
                else:
                    cx, cy, r = (p[1] - x0) * SS, (p[2] - y0) * SS, p[3] * SS
                    dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
        md = ImageDraw.Draw(mask_im)
        sub = np.zeros((H, W), np.uint8)
        for ch, pr, v, (soft, raise_, edge) in self.ops:
            if ch == 'add':
                draw(md, pr, 255)
            elif ch == 'sub':
                draw(md, pr, 0)
            elif ch == 'fn':
                pr({'T': T, 'E': E, 'mask': np.asarray(mask_im) > 0, 'ox': x0, 'oy': y0, 'bump': bump, 'sub': sub})
            else:
                tmp = Image.new('L', (W, H), 0)
                draw(ImageDraw.Draw(tmp), pr, 255)
                m = np.asarray(tmp, np.float32) / 255
                if ch == 'mat':
                    mb = (m > 0.5) & (np.asarray(mask_im) > 0)
                    sub[mb] = int(v)
                    if raise_:
                        bump += raise_ * ndi.gaussian_filter(mb.astype(np.float32), 0.7 * SS)
                    if edge is not None:
                        er = mb & ~ndi.binary_erosion(mb, iterations=int(SS * 0.9))
                        T[er] = edge
                    continue
                if soft:
                    m = ndi.gaussian_filter(m, soft * SS)
                    m = np.clip(m * (1 + soft * 0.6), 0, 1)
                if ch == 'bump':
                    bump += v * m
                elif ch == 'tex':
                    T[:] = T * (1 - m) + v * m
                elif ch == 'emit':
                    E[:] = np.maximum(E, v * m)
                elif ch == 'texmul':
                    T[:] = T * (1 - m * (1 - v))
        mask = np.asarray(mask_im) > 0
        d = ndi.distance_transform_edt(mask) / SS
        x = np.clip(d / max(0.01, self.depth), 0, 1)
        h = self.depth * np.sqrt(x * (2 - x)) + bump
        if self.noise > 0:
            h = h + (fbm(H, W, self.nscale * SS, 3, self.seed + 5) - 0.5) * 2 * self.noise * np.clip(d, 0, 1.5) / 1.5
        R = np.clip((h + 2) * HS, 0, 255).astype(np.uint8)
        G = np.clip(T * 255, 0, 255).astype(np.uint8)
        B = np.clip(E * 255, 0, 255).astype(np.uint8)
        A = np.where(mask, 1 + sub, 0).astype(np.uint8)
        self.img = Image.fromarray(np.dstack([R, G, B, A]), 'RGBA')


# ---------------------------------------------------------------- matrices
def trs(tx, ty, ang, sx=1.0, sy=1.0):
    a = math.radians(ang); c, s = math.cos(a), math.sin(a)
    return np.array([[c * sx, -s * sy, tx], [s * sx, c * sy, ty], [0, 0, 1]], np.float64)


# ---------------------------------------------------------------- FX
class Fx:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.back = np.zeros((H, W, 4), np.float32)
        self.front = np.zeros((H, W, 4), np.float32)
        self.light = np.zeros((H, W, 3), np.float32)
        yy, xx = np.mgrid[0:H, 0:W]
        self.xx = xx.astype(np.float32) + 0.5; self.yy = yy.astype(np.float32) + 0.5

    def _m(self, f, soft=0.0, ss=1):
        if ss == 1:
            im = Image.new('L', (self.W, self.H), 0); f(ImageDraw.Draw(im), 1)
            m = np.asarray(im, np.float32) / 255
        else:
            im = Image.new('L', (self.W * ss, self.H * ss), 0); f(ImageDraw.Draw(im), ss)
            m = np.asarray(im.resize((self.W, self.H), Image.BOX), np.float32) / 255
        if soft:
            m = ndi.gaussian_filter(m, soft)
        return m

    def over(self, layer, m, col, a=1.0):
        L = self.back if layer == 'back' else self.front
        c = np.array(col, np.float32) / 255.0
        mm = (m * a)[..., None]
        L[..., :3] = c * mm + L[..., :3] * (1 - mm)
        L[..., 3:] = mm + L[..., 3:] * (1 - mm)

    def add(self, m, col, a=1.0):
        c = np.array(col, np.float32) / 255.0
        self.light += c * (m * a)[..., None]

    def poly(self, pts, col, a=1.0, layer='front', soft=0.0, mode='over', ss=1):
        pts = [(float(x), float(y)) for x, y in pts]
        m = self._m(lambda d, s: d.polygon([(x * s, y * s) for x, y in pts], fill=255), soft, ss)
        self.over(layer, m, col, a) if mode == 'over' else self.add(m, col, a)

    def line(self, p0, p1, w, col, a=1.0, layer='front', soft=0.0, mode='over'):
        m = self._m(lambda d, s: d.line([(p0[0] * s, p0[1] * s), (p1[0] * s, p1[1] * s)], fill=255, width=max(1, int(w * s))), soft)
        self.over(layer, m, col, a) if mode == 'over' else self.add(m, col, a)

    def polyline(self, pts, w, col, a=1.0, layer='front', soft=0.0, mode='over'):
        pts = [(float(x), float(y)) for x, y in pts]
        m = self._m(lambda d, s: d.line([(x * s, y * s) for x, y in pts], fill=255, width=max(1, int(w * s))), soft)
        self.over(layer, m, col, a) if mode == 'over' else self.add(m, col, a)

    def ell(self, cx, cy, rx, ry, col, a=1.0, layer='front', soft=0.0, mode='over'):
        rx = max(0.01, rx); ry = max(0.01, ry)
        m = self._m(lambda d, s: d.ellipse([(cx - rx) * s, (cy - ry) * s, (cx + rx) * s, (cy + ry) * s], fill=255), soft)
        self.over(layer, m, col, a) if mode == 'over' else self.add(m, col, a)

    def ring(self, cx, cy, rx, ry, w, col, a=1.0, layer='front', soft=0.0, mode='over', a0=0, a1=360):
        rx = max(0.01, rx); ry = max(0.01, ry)
        def f(d, s):
            d.arc([(cx - rx) * s, (cy - ry) * s, (cx + rx) * s, (cy + ry) * s], a0, a1, fill=255, width=max(1, int(w * s)))
        m = self._m(f, soft)
        self.over(layer, m, col, a) if mode == 'over' else self.add(m, col, a)

    def glow(self, x, y, r, col, k=1.0, rx=None, ry=None):
        rx = rx or r; ry = ry or r
        d2 = ((self.xx - x) / rx) ** 2 + ((self.yy - y) / ry) ** 2
        g = np.exp(-d2 * 2.2)
        self.add(g, col, k)

    def dots(self, pts, col, a=1.0, layer='front', size=1):
        m = np.zeros((self.H, self.W), np.float32)
        for x, y in pts:
            xi, yi = int(math.floor(x)), int(math.floor(y))
            for dx in range(size):
                for dy in range(size):
                    if 0 <= xi + dx < self.W and 0 <= yi + dy < self.H:
                        m[yi + dy, xi + dx] = 1
        if layer == 'light':
            self.add(m, col, a)
        else:
            self.over(layer, m, col, a)

    def smear(self, A, B, col_hi, col_lo, a=0.85, layer='front', core=True):
        """A, B: listas de puntos [nuevo ... viejo] (punta y base). Franja que se afina y desvanece."""
        n = len(A)
        for k in range(n - 1):
            f = 1.0 - k / max(1, n - 1)
            col = lerp(col_lo, col_hi, f ** 1.3)
            # se estrecha hacia el pasado: la base se acerca a la punta
            t0 = 0.55 * (1 - f); t1 = 0.55 * (1 - (1 - (k + 1) / max(1, n - 1)))
            b0 = (B[k][0] + (A[k][0] - B[k][0]) * t0, B[k][1] + (A[k][1] - B[k][1]) * t0)
            b1 = (B[k + 1][0] + (A[k + 1][0] - B[k + 1][0]) * t1, B[k + 1][1] + (A[k + 1][1] - B[k + 1][1]) * t1)
            self.poly([A[k], A[k + 1], b1, b0], col, a * (0.2 + 0.8 * f ** 1.2), layer, mode='over')
        if core:
            self.polyline(A[:5] if n > 5 else A, 1.0, (255, 255, 255), min(1, a + .15), layer)

    def sparks(self, rng, x, y, n, rmax, cols, layer='front', up=0.0, a=1.0):
        pts = []
        for _ in range(n):
            ang = rng.random() * 6.283; r = rmax * (0.25 + 0.75 * rng.random())
            pts.append((x + math.cos(ang) * r, y + math.sin(ang) * r * 0.8 - up * rng.random()))
        for i, p in enumerate(pts):
            self.dots([p], cols[i % len(cols)], a, layer)


# ---------------------------------------------------------------- jefe
def lanczos_ss(arr):
    return arr


class Ctx:
    pass


class Boss:
    def __init__(self, bid, cell, pivot, body, parts, mats, anims, fxhook=None, outline=(14, 10, 22),
                 rim=(120, 150, 220), rimk=0.35, dis_col=(255, 160, 60), seed=1, halo=0.55, lit=1.0, post=None, scale=1.0, base=0.44, gain=1.25):
        self.id = bid; self.cell = cell; self.pivot = pivot; self.body = body
        self.parts = parts; self.mats = mats; self.anims = anims; self.fxhook = fxhook
        self.outline = outline; self.rim = rim; self.rimk = rimk; self.dis_col = dis_col; self.seed = seed
        self.halo = halo; self.lit = lit; self.post = post; self.scale = scale; self.base = base; self.gain = gain
        for p in parts:
            p.build()
        self.index = {p.name: i for i, p in enumerate(parts)}
        W, H = cell
        self.dn = fbm(H, W, 5, 3, seed + 99)
        rr = np.random.default_rng(seed + 7)
        self.r1 = rr.random((H, W)).astype(np.float32); self.r2 = rr.random((H, W)).astype(np.float32); self.r3 = rr.random((H, W)).astype(np.float32)
        self.mlist = list(mats.keys())

    # ---- cinematica directa
    def fk(self, pose):
        M = {}
        for p in self.parts:
            par = M[p.parent] if p.parent else np.eye(3)
            n = p.name
            s = pose.get(n + '.s', 1.0) * (self.scale if p.parent is None else 1.0)
            loc = trs(p.at[0] + pose.get(n + '.x', 0.0), p.at[1] + pose.get(n + '.y', 0.0), pose.get(n, 0.0),
                      pose.get(n + '.sx', 1.0) * s, pose.get(n + '.sy', 1.0) * s)
            M[n] = par @ loc
        return M

    def pose_at(self, name, f):
        p = self.anims[name]['pose'](f)
        if self.post:
            p = self.post(self, p)
        return p

    def part_of(self, lid):
        return self.parts[(lid - 1) // 8]

    def mat_of(self, lid):
        p = self.parts[(lid - 1) // 8]
        return self.mats[p.matnames[(lid - 1) % 8]]

    def ik(self, pose, upper, fore, hand_pt, target, flip=1):
        """Devuelve angulos de upper y fore para que hand_pt (local de fore) llegue a target (mundo)."""
        P = {k: v for k, v in pose.items() if k not in (upper, fore)}
        Mw = self.fk(P)
        pu = self.parts[self.index[upper]]; pf = self.parts[self.index[fore]]
        par = Mw[pu.parent]
        sh = par @ np.array([pu.at[0] + pose.get(upper + '.x', 0), pu.at[1] + pose.get(upper + '.y', 0), 1.0])
        sh = sh[:2]
        pr = math.atan2(par[1, 0], par[0, 0])
        l1v = np.array(pf.at, float); l2v = np.array(hand_pt, float)
        L1 = float(np.hypot(*l1v)); L2 = float(np.hypot(*l2v))
        tv = np.array(target, float) - sh
        d = float(np.hypot(*tv)); d = min(max(d, abs(L1 - L2) + 0.01), L1 + L2 - 0.01)
        base = math.atan2(tv[1], tv[0])
        a1 = math.acos(max(-1, min(1, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))))
        a2 = math.acos(max(-1, min(1, (L1 * L1 + L2 * L2 - d * d) / (2 * L1 * L2))))
        up_dir = base - flip * a1
        r1 = math.atan2(l1v[1], l1v[0]); r2 = math.atan2(l2v[1], l2v[0])
        # direccion del antebrazo: el codo gira (pi - a2) respecto a la direccion del brazo
        fore_dir = up_dir + flip * (math.pi - a2)
        ua = up_dir - pr - r1
        # fore dir (mundo) = pr + ua + (rotacion del joint) ... el eje del antebrazo es hand_pt en su local
        fa = fore_dir - (pr + ua) - r2
        deg = lambda v: (math.degrees(v) + 180) % 360 - 180
        return {upper: deg(ua), fore: deg(fa)}

    def anchor(self, pose, bone, pt):
        M = self.fk(pose)[bone]
        v = M @ np.array([pt[0], pt[1], 1.0])
        return (float(v[0]), float(v[1]))

    # ---- render del cuerpo
    def render_body(self, pose):
        W, H = self.cell
        SW, SH = W * SS, H * SS
        Mw = self.fk(pose)
        lab = np.zeros((SH, SW), np.int16)
        Hb = np.zeros((SH, SW), np.float32); Tb = np.zeros((SH, SW), np.float32); Eb = np.zeros((SH, SW), np.float32)
        order = sorted(range(len(self.parts)), key=lambda i: (pose.get(self.parts[i].name + '.z', self.parts[i].z), i))
        zrank = {}
        for rank, i in enumerate(order):
            p = self.parts[i]
            if p.empty or p.ghost or pose.get(p.name + '.v', 1) <= 0:
                continue
            M = Mw[p.name]
            A = M[:2, :2]; t = M[:2, 2]
            w, h = p.size
            corners = np.array([[0, 0], [w, 0], [0, h], [w, h]], float) / SS + [p.ox, p.oy]
            wc = (corners @ A.T + t) * SS
            X0 = int(max(0, math.floor(wc[:, 0].min()) - 1)); Y0 = int(max(0, math.floor(wc[:, 1].min()) - 1))
            X1 = int(min(SW, math.ceil(wc[:, 0].max()) + 1)); Y1 = int(min(SH, math.ceil(wc[:, 1].max()) + 1))
            if X1 <= X0 or Y1 <= Y0:
                continue
            try:
                Ai = np.linalg.inv(A)
            except np.linalg.LinAlgError:
                continue
            off = -SS * (Ai @ t + np.array([p.ox, p.oy]))
            off = off + Ai @ np.array([X0, Y0], float)
            coef = (Ai[0, 0], Ai[0, 1], off[0], Ai[1, 0], Ai[1, 1], off[1])
            out = p.img.transform((X1 - X0, Y1 - Y0), Image.AFFINE, coef, Image.NEAREST)
            o = np.asarray(out)
            m = o[..., 3] > 0
            if not m.any():
                continue
            sl = (slice(Y0, Y1), slice(X0, X1))
            lab[sl][m] = (i * 8 + o[..., 3][m].astype(np.int16)).astype(np.int16)
            Hb[sl][m] = o[..., 0][m] / HS - 2
            Tb[sl][m] = o[..., 1][m] / 255.0
            Eb[sl][m] = o[..., 2][m] / 255.0
            zrank[i] = rank
        clip = pose.get('clip')
        if clip is not None:
            cx0, cy0, cx1, cy1 = [int(v * SS) for v in clip]
            keep = np.zeros_like(lab, bool)
            keep[max(0, cy0):cy1, max(0, cx0):cx1] = True
            lab[~keep] = 0
        return self._shade(lab, Hb, Tb, Eb, pose, zrank, Mw)

    def _shade(self, lab, Hb, Tb, Eb, pose, zrank, Mw):
        W, H = self.cell
        k = SS * SS
        # reduccion por mayoria
        def blocks(a):
            return a.reshape(H, SS, W, SS).transpose(0, 2, 1, 3).reshape(H, W, k)
        LB = blocks(lab)
        nz = LB > 0
        cnt = np.zeros(LB.shape, np.float32)
        for j in range(k):
            cnt += ((LB == LB[..., j:j + 1]) & nz).astype(np.float32)
        cnt = cnt + LB.astype(np.float32) * 1e-3
        cnt[~nz] = -1
        win = np.argmax(cnt, axis=2)
        lab1 = np.take_along_axis(LB, win[..., None], axis=2)[..., 0].astype(np.int32)
        cover = nz.sum(2)
        lab1[cover < (k // 2 + 1)] = 0
        eq = (LB == lab1[..., None]) & (lab1[..., None] > 0)
        den = np.maximum(eq.sum(2), 1)
        H1 = (blocks(Hb) * eq).sum(2) / den
        T1 = (blocks(Tb) * eq).sum(2) / den
        E1 = (blocks(Eb) * eq).sum(2) / den
        valid = lab1 > 0
        # multiplicadores de emision (retrocompatibles): pose['emit'] global y pose['<parte>.e'] por parte
        _em = pose.get('emit')
        if _em is not None:
            E1 = E1 * _em
        _pe = [(i * 8, pose.get(p.name + '.e')) for i, p in enumerate(self.parts) if pose.get(p.name + '.e') is not None]
        if _pe:
            _lut = np.ones(len(self.parts) * 8 + 1, np.float32)
            for _b, _v in _pe:
                _lut[_b + 1:_b + 9] = _v
            E1 = E1 * _lut[lab1]
        # ---- normales
        def sh(a, dy, dx, fill):
            out = np.full_like(a, fill)
            ys = slice(max(0, dy), H + min(0, dy)); yd = slice(max(0, -dy), H + min(0, -dy))
            xs = slice(max(0, dx), W + min(0, dx)); xd = slice(max(0, -dx), W + min(0, -dx))
            out[yd, xd] = a[ys, xs]
            return out

        def nbh(dy, dx):
            hl = sh(H1, dy, dx, 0.0); ll = sh(lab1, dy, dx, 0)
            return np.where(ll == lab1, hl, np.where(ll == 0, -0.3, H1))
        gx = (nbh(0, 1) - nbh(0, -1)) * 0.5
        gy = (nbh(1, 0) - nbh(-1, 0)) * 0.5
        nrm = np.sqrt(gx * gx + gy * gy + 1)
        lam = (-gx * LIGHT[0] + -gy * LIGHT[1] + LIGHT[2]) / nrm
        lam0 = LIGHT[2]
        # ---- tabla por parte
        nparts = len(self.parts)
        NL = nparts * 8 + 1
        N = 6
        rgb = np.zeros((H, W, 3), np.float32)
        glowcol = np.zeros((H, W, 3), np.float32)
        isglow = np.zeros((H, W), bool)
        bay = np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W]
        zr = np.zeros((H, W), np.float32)
        zlut = np.zeros(NL, np.float32)
        for pi, r in zrank.items():
            zlut[pi * 8 + 1:pi * 8 + 9] = r
        zr = zlut[lab1]
        idx_img = np.zeros((H, W), np.int32)
        for lid in np.unique(lab1):
            if lid == 0:
                continue
            p = self.part_of(lid)
            mat = self.mat_of(lid)
            sel = lab1 == lid
            n = len(mat.ramp)
            s = self.base + mat.gain * self.gain * (lam - lam0) * self.lit + (T1 - 0.5) * mat.texamt + p.dim + pose.get(p.name + '.dim', 0.0)
            s = s + pose.get('lit', 0.0)
            idx = np.floor(s * n + bay * 0.42 + 0.5).astype(np.int32)
            idx = np.clip(idx, 0, n - 1)
            idx_img = np.where(sel, idx, idx_img)
            rmp = np.array(mat.ramp, np.float32)
            rgb = np.where(sel[..., None], rmp[idx], rgb)
        # seams: oscurecer la parte inferior junto a una superior
        seam = np.zeros((H, W), bool)
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            ll = sh(lab1, dy, dx, 0)
            zz = zlut[ll]
            seam |= (ll > 0) & (ll != lab1) & (zz > zr) & valid
        sp = np.array([self.part_of(l).seam if l > 0 else False for l in range(NL)])
        seam &= sp[lab1]
        if seam.any():
            for lid in np.unique(lab1[seam]):
                p = self.part_of(lid); mat = self.mat_of(lid)
                sel = seam & (lab1 == lid)
                n = len(mat.ramp)
                ii = np.clip(idx_img - 2, 0, n - 1)
                rgb = np.where(sel[..., None], np.array(mat.ramp, np.float32)[ii], rgb)
        # emision
        halo_src = np.zeros((H, W, 3), np.float32)
        for lid in np.unique(lab1):
            if lid == 0:
                continue
            p = self.part_of(lid); mat = self.mat_of(lid)
            if mat.glow is None:
                continue
            sel = (lab1 == lid) & (E1 > 0.14)
            if not sel.any():
                continue
            g = np.array(mat.glow, np.float32)
            gi = np.clip(np.floor(E1 * (len(g) - 0.01) + 0.15 + bay * 0.2).astype(np.int32), 0, len(g) - 1)
            rgb = np.where(sel[..., None], g[gi], rgb)
            isglow |= sel
            halo_src += np.where((lab1 == lid)[..., None], (E1[..., None] * g[len(g) // 2]), 0)
        # rim light (borde derecho/inferior)
        right = sh(valid, 0, 1, False); down = sh(valid, 1, 0, False)
        edge = valid & (~right | ~down) & ~isglow
        rimcol = np.array(self.rim, np.float32)
        rimsel = np.array([self.part_of(l).rimk if l > 0 else 0 for l in range(NL)], np.float32)[lab1]
        mk = edge & (lam < lam0 + 0.05)
        rgb = np.where(mk[..., None], rgb * (1 - self.rimk * rimsel[..., None]) + rimcol * self.rimk * rimsel[..., None], rgb)
        # halo de luz de las zonas emisivas sobre el cuerpo
        if self.halo > 0 and halo_src.any():
            hh = np.stack([ndi.gaussian_filter(halo_src[..., c], 2.0) for c in range(3)], -1)
            hh = np.clip(hh, 0, 255)
            rgb = np.where((valid & ~isglow)[..., None], np.clip(rgb + hh * self.halo * 0.55, 0, 255), rgb)
        alpha = valid.copy()
        # flash / tinte global
        tint = pose.get('tint')
        if tint is not None:
            col, amt = tint
            rgb = rgb * (1 - amt) + np.array(col, np.float32) * amt
        # disolver
        extra = None
        dis = pose.get('dis', 0.0)
        fade = pose.get('fade', 1.0)
        if dis > 0 or fade < 1.0:
            ys = np.arange(H, dtype=np.float32)[:, None] / H
            ymin = np.where(valid.any(1))[0]
            y0 = ymin.min() / H if len(ymin) else 0.0
            hh_ = (ymin.max() - ymin.min() + 1) / H if len(ymin) else 1.0
            yn = np.clip((ys - y0) / max(0.05, hh_), 0, 1)
            if pose.get('dis_dir', 1.0) < 0:
                yn = 1 - yn
            D = np.clip(self.dn * 0.7 + yn * 0.3, 0, 1)
            thr = dis * 1.1 - 0.05
            gone = valid & (D < thr)
            edgeb = valid & ~gone & (D < thr + 0.07)
            rgb = np.where(edgeb[..., None], np.array(self.dis_col, np.float32), rgb)
            # copos que ascienden
            alpha = valid & ~gone
            if fade < 1.0:
                keepf = (bay + 0.5) < fade
                alpha &= keepf
            fl = gone & (self.r1 < 0.16)
            if fl.any():
                yy, xx = np.nonzero(fl)
                amt = (thr - D[yy, xx])
                ny = (yy - amt * 38 * (0.5 + self.r2[yy, xx])).astype(int)
                nx = (xx + (self.r3[yy, xx] - 0.25) * amt * 34).astype(int)
                ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W) & (amt < 0.6)
                extra = (ny[ok], nx[ok], rgb[yy[ok], xx[ok]] * (1 - amt[ok, None] * 0.9), amt[ok])
        # contorno
        a8 = alpha
        dil = ndi.binary_dilation(a8, structure=ndi.generate_binary_structure(2, 1))
        ol = dil & ~a8
        # color de contorno: media de vecinos oscurecida
        sm = np.zeros((H, W, 3), np.float32); sc = np.zeros((H, W), np.float32)
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            shr = np.stack([sh(rgb[..., c], dy, dx, 0.0) for c in range(3)], -1)
            sha = sh(a8, dy, dx, False)
            sm += shr * sha[..., None]; sc += sha
        sm /= np.maximum(sc, 1)[..., None]
        oc = np.array(self.outline, np.float32)
        olc = sm * 0.20 + oc * 0.62
        out = np.zeros((H, W, 4), np.float32)
        out[..., :3] = np.where(a8[..., None], rgb, 0)
        out[..., 3] = a8
        out[..., :3] = np.where(ol[..., None], olc, out[..., :3])
        out[..., 3] = np.where(ol, 1.0, out[..., 3])
        if extra is not None:
            ny, nx, cc, amt = extra
            fre = (out[ny, nx, 3] == 0)
            out[ny[fre], nx[fre], :3] = cc[fre]
            out[ny[fre], nx[fre], 3] = 1.0
        return out, dict(emit=E1 * (lab1 > 0), halo=halo_src, valid=valid, M=Mw)

    # ---- composicion con FX
    def frame(self, name, f, n, pose, rng_seed=0):
        W, H = self.cell
        body, info = self.render_body(pose)
        fx = Fx(W, H)
        ctx = Ctx()
        ctx.boss = self; ctx.name = name; ctx.i = f; ctx.n = n; ctx.t = f / max(1, n - 1); ctx.pose = pose
        ctx.fx = fx; ctx.rng = np.random.default_rng(self.seed * 1000 + (zlib.crc32(name.encode()) % 997) * 31 + int(f * 7) + rng_seed)
        ctx.body = body; ctx.info = info; ctx.W = W; ctx.H = H
        ctx.pivot = self.pivot
        ctx.anchor = lambda bone, pt, p=None: self.anchor(pose if p is None else p, bone, pt)
        ctx.pose_at = lambda ff: self.pose_at(name, ff)
        ctx.anchor_at = lambda ff, bone, pt: self.anchor(self.pose_at(name, ff), bone, pt)
        if self.fxhook:
            self.fxhook(ctx)
        # composicion: back, body, front, light
        P = fx.back[..., :3].copy(); A = fx.back[..., 3].copy()
        ba = body[..., 3]
        P = body[..., :3] / 255.0 * ba[..., None] + P * (1 - ba[..., None])
        A = ba + A * (1 - ba)
        fa = fx.front[..., 3]
        P = fx.front[..., :3] + P * (1 - fa[..., None])
        A = fa + A * (1 - fa)
        P = P + fx.light
        lum = np.clip(fx.light.max(2), 0, 1)
        A = np.maximum(A, lum)
        A = np.clip(A, 0, 1)
        # alfa posterizado (con dither ordenado) fuera del cuerpo
        solid = A >= 0.999
        bay = np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W]
        lv = np.array([0, 0.3, 0.55, 0.8, 1.0])
        Ad = np.clip(A + bay * 0.24, 0, 1)
        Aq = np.where(solid, 1.0, lv[np.abs(Ad[..., None] - lv).argmin(-1)])
        Aq = np.where(A < 0.08, 0, Aq)
        rgbs = np.clip(P / np.maximum(A, 1e-4)[..., None], 0, 1)
        res = np.zeros((H, W, 4), np.uint8)
        res[..., :3] = (rgbs * 255).astype(np.uint8)
        res[..., 3] = (Aq * 255).astype(np.uint8)
        res[res[..., 3] == 0, :3] = 0
        return res
