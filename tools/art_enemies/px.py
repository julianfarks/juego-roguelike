"""Mini motor de pixel art: partes poligonales con sombreado por mapa de altura,
supermuestreo xS y reduccion por color mayoritario, contorno selectivo 1px."""
import numpy as np, math, colorsys, json, os, contextlib
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

S = 4
BAY = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16.0
BAY8 = None


def _bay8():
    global BAY8
    if BAY8 is None:
        m = np.array([[0]])
        for _ in range(3):
            m = np.block([[4 * m, 4 * m + 2], [4 * m + 3, 4 * m + 1]])
        BAY8 = (m + 0.5) / 64.0
    return BAY8


def rgb(h):
    if not isinstance(h, str):
        return tuple(h)
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hexc(c):
    return '#%02x%02x%02x' % tuple(int(v) for v in c)


def mix(a, b, t):
    a, b = rgb(a), rgb(b)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def R(base, n=5, spread=0.26, hs=0.10, sat=1.0):
    r, g, b = [v / 255 for v in rgb(base)]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    m = (n - 1) * 0.5
    out = []
    for i in range(n):
        t = (i - m) / m
        ll = min(0.95, max(0.04, l + t * spread * (1.0 if t > 0 else 0.9)))
        tgt = 0.72 if t < 0 else 0.13
        d = ((tgt - h + 0.5) % 1.0) - 0.5
        hh = (h + d * abs(t) * hs * (1.2 if t < 0 else 0.8)) % 1.0
        ss = min(1, max(0, s * sat * (1 - 0.18 * max(t, 0) + 0.10 * max(-t, 0))))
        rr, gg, bb = colorsys.hls_to_rgb(hh, ll, ss)
        out.append((int(rr * 255 + .5), int(gg * 255 + .5), int(bb * 255 + .5)))
    return out


class Mat:
    def __init__(s, base=None, n=5, bevel=2.2, tex=0.0, dith=0.45, emi=False, spread=0.26, hs=0.10,
                 outcol=None, ramp=None, sat=1.0, ts=1.0, bias=0.35, nooutline=False, seed=1):
        if ramp is not None:
            s.ramp = np.array([rgb(c) for c in ramp], np.uint8)
        else:
            s.ramp = np.array(R(base, n, spread, hs, sat), np.uint8)
        s.bevel, s.tex, s.dith, s.emi, s.ts, s.bias, s.seed = bevel, tex, dith, emi, ts, bias, seed
        s.outcol = rgb(outcol) if outcol else None
        s.noout = nooutline


def _hash(ix, iy, seed):
    h = (ix.astype(np.int64) * 73856093) ^ (iy.astype(np.int64) * 19349663) ^ (seed * 83492791)
    h = (h ^ (h >> 13)) * 1274126177
    h = h ^ (h >> 16)
    return (h & 0xFFFF) / 65535.0


LV = np.array([-0.55, -0.65, 0.55])
LV = LV / np.linalg.norm(LV)


class Part:
    def __init__(s, c, mat, line=0.0, fade=None, bevel=None):
        s.c, s.mat, s.line, s.fade = c, mat, line, fade
        s.bev = bevel
        s.img = Image.new('L', (c.hw, c.hh), 0)
        s.d = ImageDraw.Draw(s.img)

    def _pts(s, pts):
        return [s.c.P(x, y) for x, y in pts]

    def poly(s, pts, v=255):
        s.d.polygon(s._pts(pts), fill=v)
        return s

    def ell(s, cx, cy, rx, ry=None, rot=0.0, v=255, n=28):
        ry = rx if ry is None else ry
        ca, sa = math.cos(rot), math.sin(rot)
        pts = []
        for i in range(n):
            a = 2 * math.pi * i / n
            ex, ey = rx * math.cos(a), ry * math.sin(a)
            pts.append((cx + ex * ca - ey * sa, cy + ex * sa + ey * ca))
        return s.poly(pts, v)

    def rect(s, x0, y0, x1, y1, v=255):
        return s.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], v)

    def limb(s, p0, p1, r0, r1=None, v=255):
        r1 = r0 if r1 is None else r1
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy) or 1e-6
        nx, ny = -dy / L, dx / L
        s.poly([(p0[0] + nx * r0, p0[1] + ny * r0), (p1[0] + nx * r1, p1[1] + ny * r1),
                (p1[0] - nx * r1, p1[1] - ny * r1), (p0[0] - nx * r0, p0[1] - ny * r0)], v)
        s.ell(p0[0], p0[1], r0, v=v, n=16)
        s.ell(p1[0], p1[1], r1, v=v, n=16)
        return s

    def tube(s, pts, r0, r1=None, v=255):
        r1 = r0 if r1 is None else r1
        n = len(pts) - 1
        for i in range(n):
            a = r0 + (r1 - r0) * i / max(n, 1)
            b = r0 + (r1 - r0) * (i + 1) / max(n, 1)
            s.limb(pts[i], pts[i + 1], a, b, v)
        return s

    def line_(s, p0, p1, w=1.0, v=255):
        return s.limb(p0, p1, w / 2, w / 2, v)

    def __enter__(s):
        return s

    def __exit__(s, *a):
        s.finish()

    def finish(s):
        c, mat = s.c, s.mat
        m = np.array(s.img) > 127
        ys, xs = np.where(m)
        if len(ys) == 0:
            return
        y0, y1 = max(ys.min() - 2, 0), min(ys.max() + 3, c.hh)
        x0, x1 = max(xs.min() - 2, 0), min(xs.max() + 3, c.hw)
        sub = m[y0:y1, x0:x1]
        d = ndi.distance_transform_edt(np.pad(sub, 1))[1:-1, 1:-1]
        bev = (s.bev if s.bev is not None else mat.bevel) * S
        t = np.minimum(d, bev) / bev
        ny_, nx_ = np.mgrid[y0:y1, x0:x1]
        yn = (ny_ - ys.min()) / max(ys.max() - ys.min(), 1)
        xn = (nx_ - xs.min()) / max(xs.max() - xs.min(), 1)
        if mat.emi:
            v = 0.12 + 0.95 * (t ** 0.75) - 0.1 * yn
        else:
            h = np.sin(t * np.pi / 2) * bev * 0.9
            hs_ = ndi.gaussian_filter(h, 0.5 * S)
            gy, gx = np.gradient(hs_)
            nz = 1 / np.sqrt(gx * gx + gy * gy + 1)
            L = (-gx * nz) * LV[0] + (-gy * nz) * LV[1] + nz * LV[2]
            v = (L - 0.15) / 0.8 + mat.bias * (0.5 - yn) * 0.8 + mat.bias * (0.5 - xn) * 0.4
        nlev = len(mat.ramp)
        tf = v * (nlev - 1) + 0.5
        gxp = nx_ // S
        gyp = ny_ // S
        tf = tf + (BAY[gyp % 4, gxp % 4] - 0.5) * mat.dith * 2
        if mat.tex:
            lx = (nx_ + 0.5) / S - c.px
            ly = (ny_ + 0.5) / S - c.py
            Mi = c.Minv()
            qx = Mi[0][0] * lx + Mi[0][1] * ly + Mi[0][2]
            qy = Mi[1][0] * lx + Mi[1][1] * ly + Mi[1][2]
            nz_ = _hash(np.floor(qx * mat.ts), np.floor(qy * mat.ts), mat.seed)
            tf = tf + (nz_ - 0.5) * 2 * mat.tex
        tone = np.clip(np.floor(tf), 0, nlev - 1).astype(int)
        cols = mat.ramp[tone]
        keep = sub
        if s.fade is not None:
            lx = (nx_ + 0.5) / S - c.px
            ly = (ny_ + 0.5) / S - c.py
            al = s.fade(lx, ly)
            keep = sub & (al > _bay8()[(ny_ // S) % 8, (nx_ // S) % 8])
        reg = c.rgb[y0:y1, x0:x1]
        ra = c.a[y0:y1, x0:x1]
        ro = c.oid[y0:y1, x0:x1]
        if s.line > 0:
            it = max(1, int(s.line * S))
            er = ndi.binary_erosion(sub, iterations=it)
            band = sub & ~er
            prior = ndi.binary_dilation(ra, iterations=it + 1)
            band &= prior
            cols = np.where(band[..., None], mat.ramp[0], cols)
        reg[keep] = cols[keep]
        ra[keep] = True
        ro[keep] = c.oid_of(mat)


class Ctx:
    def __init__(s, W, H, px, py, tint=(24, 16, 34)):
        s.W, s.H, s.px, s.py = W, H, px, py
        s.hw, s.hh = W * S, H * S
        s.rgb = np.zeros((s.hh, s.hw, 3), np.uint8)
        s.a = np.zeros((s.hh, s.hw), bool)
        s.oid = np.zeros((s.hh, s.hw), np.uint8)
        s.tint = np.array(tint, float)
        s.M = np.eye(3)
        s.stack = []
        s.otab = {}
        s.glows = []
        s.dots = []
        s.flash_ = None
        s.dissolve_ = None
        s.under = []  # sin uso

    def oid_of(s, mat):
        if mat.noout:
            return 255
        if mat.outcol is None:
            return 0
        k = id(mat)
        if k not in s.otab:
            s.otab[k] = (len(s.otab) + 1, mat.outcol)
        return s.otab[k][0]

    def P(s, x, y):
        M = s.M
        X = M[0, 0] * x + M[0, 1] * y + M[0, 2]
        Y = M[1, 0] * x + M[1, 1] * y + M[1, 2]
        return ((s.px + X) * S, (s.py + Y) * S)

    def T(s, x, y):  # punto local -> logico (relativo al pivote)
        M = s.M
        return (M[0, 0] * x + M[0, 1] * y + M[0, 2], M[1, 0] * x + M[1, 1] * y + M[1, 2])

    def Minv(s):
        return np.linalg.inv(s.M)

    @contextlib.contextmanager
    def at(s, x=0, y=0, a=0.0, sx=1.0, sy=1.0):
        old = s.M
        ca, sa = math.cos(a), math.sin(a)
        N = np.array([[ca * sx, -sa * sy, x], [sa * sx, ca * sy, y], [0, 0, 1]])
        s.M = old @ N
        try:
            yield
        finally:
            s.M = old

    def part(s, mat, line=0.0, fade=None, bevel=None):
        return Part(s, mat, line, fade, bevel)

    # efectos 1x
    def glow(s, x, y, r, color, amt=0.6):
        gx, gy = s.T(x, y)
        s.glows.append((gx, gy, r, rgb(color), amt))

    def dot(s, x, y, color):
        gx, gy = s.T(x, y)
        s.dots.append((gx, gy, rgb(color)))

    def dotw(s, x, y, color):  # sin transformar (coords del mundo)
        s.dots.append((x, y, rgb(color)))

    def flash(s, color, amt):
        s.flash_ = (rgb(color), amt)

    def dissolve(s, amt, up=0.5, seed=0):
        s.dissolve_ = (amt, up, seed)

    def finish(s):
        W, H = s.W, s.H
        rgbb = s.rgb.reshape(H, S, W, S, 3).transpose(0, 2, 1, 3, 4).reshape(H, W, S * S, 3)
        a = s.a.reshape(H, S, W, S).transpose(0, 2, 1, 3).reshape(H, W, S * S)
        oid = s.oid.reshape(H, S, W, S).transpose(0, 2, 1, 3).reshape(H, W, S * S)
        rr = rgbb.astype(np.int32)
        pk = (rr[..., 0] << 16) | (rr[..., 1] << 8) | rr[..., 2]
        eq = (pk[..., :, None] == pk[..., None, :]) & a[..., None, :]
        cnt = np.where(a, eq.sum(-1), -1)
        w = cnt.argmax(-1)
        col = np.take_along_axis(rgbb, w[..., None, None], 2)[:, :, 0, :].astype(float)
        oi = np.take_along_axis(oid, w[..., None], 2)[..., 0]
        al = a.sum(-1) >= (S * S) // 2
        col[~al] = 0
        # brillos aditivos (solo sobre pixeles opacos)
        yy, xx = np.mgrid[0:H, 0:W]
        for (gx, gy, r, gc, amt) in s.glows:
            cx, cy = s.px + gx - 0.5, s.py + gy - 0.5
            dd = np.hypot(xx - cx, yy - cy)
            f = np.clip(1 - dd / r, 0, 1)
            f = np.where(f > 0.55, 1.0, np.where(f > 0.0, 0.45 * (f > 0.2) + 0.2 * (f > 0.05), 0))
            f = f * amt
            col = col + np.array(gc, float)[None, None, :] * f[..., None] * al[..., None]
        if s.flash_:
            fc, fa = s.flash_
            col = np.where(al[..., None], col + (np.array(fc, float) - col) * fa, col)
        col = np.clip(col, 0, 255)
        # contorno 1px selectivo
        cand = np.clip(col * 0.30 + s.tint[None, None, :] * 0.62, 0, 255)
        valid = al & (oi != 255)
        for k, (i, oc) in s.otab.items():
            msk = al & (oi == i)
            cand[msk] = np.array(oc, float)
        sumc = np.zeros((H, W, 3))
        n = np.zeros((H, W))
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sv = np.roll(valid, (dy, dx), (0, 1))
            sc = np.roll(cand, (dy, dx), (0, 1))
            # anular wrap
            if dy == 1: sv[0, :] = False
            if dy == -1: sv[-1, :] = False
            if dx == 1: sv[:, 0] = False
            if dx == -1: sv[:, -1] = False
            sumc += sc * sv[..., None]
            n += sv
        edge = (~al) & (n > 0)
        oc_ = sumc / np.maximum(n, 1)[..., None]
        out = np.zeros((H, W, 4), np.uint8)
        out[..., :3] = np.where(al[..., None], col, 0).astype(np.uint8)
        out[..., 3] = np.where(al, 255, 0)
        out[edge, :3] = oc_[edge].astype(np.uint8)
        out[edge, 3] = 255
        for (gx, gy, cc) in s.dots:
            x, y = int(math.floor(s.px + gx)), int(math.floor(s.py + gy))
            if 0 <= x < W and 0 <= y < H:
                out[y, x] = (*cc, 255)
        if s.dissolve_:
            amt, up, seed = s.dissolve_
            b8 = _bay8()
            thr = b8[(yy + seed) % 8, (xx + seed * 3) % 8]
            thr = thr + (yy / H - 0.5) * up * 0.0 + (1 - yy / H) * 0 
            bias = (yy / H) * up   # abajo se disuelve antes? (up>0: arriba antes)
            thr = np.clip(thr * (1 - up) + (1 - yy / H) * up * 0.999, 0, 1)
            out[thr < amt] = 0
        return Image.fromarray(out, 'RGBA')


# ---------- utilidades de animacion ----------
def sm(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def kf(t, pts, smooth=True):
    if t <= pts[0][0]:
        return pts[0][1]
    for i in range(len(pts) - 1):
        t0, v0 = pts[i]
        t1, v1 = pts[i + 1]
        if t <= t1:
            u = (t - t0) / max(t1 - t0, 1e-9)
            return lerp(v0, v1, sm(u) if smooth else u)
    return pts[-1][1]


def ik2(hip, foot, l1, l2, bend=1):
    dx, dy = foot[0] - hip[0], foot[1] - hip[1]
    d = math.hypot(dx, dy)
    d = min(max(d, abs(l1 - l2) + 0.01), l1 + l2 - 0.01)
    a = math.atan2(dy, dx)
    cosb = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)
    b = math.acos(max(-1, min(1, cosb)))
    ang = a + bend * b
    knee = (hip[0] + l1 * math.cos(ang), hip[1] + l1 * math.sin(ang))
    # reposicionar pie si fuera de alcance
    return knee


def fk(p, a1, l1, a2, l2):
    e = (p[0] + l1 * math.cos(a1), p[1] + l1 * math.sin(a1))
    h = (e[0] + l2 * math.cos(a1 + a2), e[1] + l2 * math.sin(a1 + a2))
    return e, h


def gait(ph, stride, lift):
    """pie en fase ph (0..1): (dx, dy) relativo a la cadera en reposo; dy<=0 es elevar"""
    a = 2 * math.pi * ph
    return stride * math.cos(a), -lift * max(0.0, -math.sin(a))


class Bits:
    """Fragmentos con fisica simple para muertes (huesos, trozos, armaduras)."""

    def __init__(s, items, seed=3, g=1.0, T=1.0, floor=0.0):
        import random
        rnd = random.Random(seed)
        s.items = []
        for it in items:
            d = dict(it)
            d.setdefault('vx', rnd.uniform(-5, 5))
            d.setdefault('vy', rnd.uniform(-9, -3))
            d.setdefault('spin', rnd.uniform(-5, 5))
            d.setdefault('rest', None)
            d.setdefault('r', 2.0)
            d.setdefault('bounce', 0.3)
            s.items.append(d)
        s.g, s.T, s.floor = g, T, floor

    def state(s, u):
        out = []
        steps = 24
        for d in s.items:
            x, y, a = d['x'], d['y'], d.get('a', 0.0)
            vx, vy = d['vx'] * 6.0, d['vy'] * 6.0
            landed = False
            dt = s.T * u / steps if steps else 0
            for _ in range(steps):
                if landed:
                    break
                vy += s.g * 120.0 * dt
                x += vx * dt
                y += vy * dt
                a += d['spin'] * dt * 2
                fl = s.floor - d['r']
                if y >= fl:
                    y = fl
                    if abs(vy) > 14 and d['bounce'] > 0:
                        vy = -vy * d['bounce']
                        vx *= 0.6
                        d['spin'] *= 0.5
                    else:
                        landed = True
                        if d['rest'] is not None:
                            a = d['rest']
            out.append((d, x, y, a))
        return out


class Sheet:
    def __init__(s, name, W, H, pivot, body, tint=(24, 16, 34)):
        s.name, s.W, s.H, s.pivot, s.body, s.tint = name, W, H, pivot, body, tint
        s.rows = []
        s.meta = {}

    def anim(s, name, n, fps, loop, drawfn, **extra):
        frames = []
        for i in range(n):
            c = Ctx(s.W, s.H, s.pivot[0], s.pivot[1], s.tint)
            drawfn(c, name, i, n)
            frames.append(c.finish())
        s.rows.append((name, n, fps, loop, frames, extra))

    def save(s, outdir, prevdir=None):
        maxn = max(r[1] for r in s.rows)
        im = Image.new('RGBA', (maxn * s.W, len(s.rows) * s.H), (0, 0, 0, 0))
        anims = {}
        for ri, (name, n, fps, loop, frames, extra) in enumerate(s.rows):
            for i, f in enumerate(frames):
                im.paste(f, (i * s.W, ri * s.H))
            d = {'row': ri, 'n': n, 'fps': fps, 'loop': loop}
            d.update(extra)
            anims[name] = d
        # cuantizar a paleta limitada manteniendo alfa binario
        os.makedirs(outdir, exist_ok=True)
        im.save(os.path.join(outdir, s.name + '.png'), optimize=True)
        js = {'cell': [s.W, s.H], 'pivot': list(s.pivot), 'body': list(s.body), 'anims': anims}
        json.dump(js, open(os.path.join(outdir, s.name + '.json'), 'w'), indent=1)
        if prevdir:
            os.makedirs(prevdir, exist_ok=True)
            z = 4
            bg = Image.new('RGBA', im.size, (34, 30, 44, 255))
            # cuadricula del pivote
            bg.alpha_composite(im)
            big = bg.resize((im.width * z, im.height * z), Image.NEAREST)
            dr = ImageDraw.Draw(big)
            for ri in range(len(s.rows)):
                for i in range(maxn):
                    x0, y0 = i * s.W * z, ri * s.H * z
                    dr.rectangle([x0, y0, x0 + s.W * z - 1, y0 + s.H * z - 1], outline=(70, 64, 90))
                    dr.line([x0 + s.pivot[0] * z - 4, y0 + s.pivot[1] * z, x0 + s.pivot[0] * z + 4, y0 + s.pivot[1] * z], fill=(255, 0, 255))
            big.convert('RGB').save(os.path.join(prevdir, s.name + '.png'))
        return im
