"""Kit de render pixel-art: partes rellenas, sombreado por mapa de altura, supermuestreo + voto de mayoria."""
import math
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

# ---------------------------------------------------------------- color utils
def hexc(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


import colorsys


def _hshift(h, target, amt):
    d = ((target - h + 0.5) % 1.0) - 0.5
    return (h + d * amt) % 1.0


def mk_ramp(base, hl=None, **kw):
    """6 tonos: 0 contorno, 1 sombra profunda, 2 sombra, 3 base, 4 luz, 5 brillo. Cambio de matiz: sombras hacia
    magenta (calidos) o azul-violeta (frios), luces hacia amarillo."""
    r, g, b = [c / 255.0 for c in base]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    warm = (h < 0.2 or h > 0.9)
    sh_t = 0.93 if warm else 0.72
    out = []
    spec = [(0.20, 1.10, 0.30, sh_t), (0.40, 1.10, 0.22, sh_t), (0.68, 1.04, 0.10, sh_t)]
    for vm, sm, ha, tg in spec:
        hh = _hshift(h, tg, ha)
        ss = min(1.0, s * sm + 0.05)
        out.append(colorsys.hsv_to_rgb(hh, ss, v * vm))
    out.append((r, g, b))
    hh = _hshift(h, 0.13, 0.12)
    out.append(colorsys.hsv_to_rgb(hh, s * 0.80, min(1.0, v * 1.12 + 0.06)))
    if hl is not None:
        out.append(tuple(c / 255.0 for c in hl))
    else:
        out.append(colorsys.hsv_to_rgb(_hshift(h, 0.14, 0.2), s * 0.38, min(1.0, v * 1.15 + 0.2)))
    return [tuple(int(max(6, min(255, round(c * 255)))) for c in t) for t in out]


PAL = [(0, 0, 0)]      # id 0 = transparente
MATS = {}


def mat(name, base, hl=None, **kw):
    if isinstance(base, str):
        base = hexc(base)
    if isinstance(hl, str):
        hl = hexc(hl)
    r = mk_ramp(base, hl, **kw)
    if name in MATS:
        idx = MATS[name]['idx']
        for t in range(6):
            PAL[idx * 8 + t + 1] = r[t]
    else:
        idx = len(MATS)
        MATS[name] = {'idx': idx, 'ramp': r}
        while len(PAL) < idx * 8 + 9:
            PAL.append((0, 0, 0))
        for t in range(6):
            PAL[idx * 8 + t + 1] = r[t]
    return name


def mat_back(name, k=0.70):
    """Version oscura (miembros lejanos) de un material."""
    b = MATS[name]['ramp'][3]
    c = lerp(tuple(b), (30, 22, 64), 1 - k)
    return mat(name + '_b', tuple(int(x) for x in c), hl=tuple(int(x) for x in lerp(MATS[name]['ramp'][4], (60, 50, 110), 0.35)))


def reset_mats():
    global PAL
    PAL.clear()
    PAL.append((0, 0, 0))
    MATS.clear()


BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], dtype=np.float32) / 16.0

L = np.array([-0.55, -0.66, 0.52], dtype=np.float32)
L /= np.linalg.norm(L)


class Canvas:
    def __init__(self, W, H, S=4, scale=1.0, origin=(32, 44), rot=0.0, rot_c=(0, -12), shift=(0, 0)):
        self.W, self.H, self.S = W, H, S
        self.scale = scale
        self.ox, self.oy = origin
        self.rot = math.radians(rot)
        self.rc = rot_c
        self.sh = shift
        self.ids = np.zeros((H * S, W * S), np.int32)
        self.parts_meta = []

    # world -> hi-res
    def tf1(self, x, y):
        x += self.sh[0]
        y += self.sh[1]
        if self.rot:
            cx, cy = self.rc[0] + self.sh[0], self.rc[1] + self.sh[1]
            dx, dy = x - cx, y - cy
            c, s = math.cos(self.rot), math.sin(self.rot)
            x, y = cx + dx * c - dy * s, cy + dx * s + dy * c
        return ((x * self.scale + self.ox) * self.S, (y * self.scale + self.oy) * self.S)

    def tfw(self, x, y):
        """world -> 1x canvas coords (float)"""
        a, b = self.tf1(x, y)
        return a / self.S, b / self.S

    def _mask(self, shapes):
        S = self.S
        pts_all = []
        prim = []
        for sh in shapes:
            k = sh[0]
            if k == 'p':
                pp = [self.tf1(*p) for p in sh[1]]
                prim.append(('p', pp))
                pts_all += pp
            elif k == 'c':
                c = self.tf1(*sh[1])
                r = sh[2] * self.scale * S
                prim.append(('c', c, r, r))
                pts_all += [(c[0] - r, c[1] - r), (c[0] + r, c[1] + r)]
            elif k == 'e':  # elipse (centro, rx, ry, angulo grados) -> poligono
                cx, cy = sh[1]
                rx, ry = sh[2], sh[3]
                ang = math.radians(sh[4]) if len(sh) > 4 else 0
                pp = []
                for i in range(24):
                    a = i / 24 * 2 * math.pi
                    px, py = rx * math.cos(a), ry * math.sin(a)
                    pp.append(self.tf1(cx + px * math.cos(ang) - py * math.sin(ang),
                                       cy + px * math.sin(ang) + py * math.cos(ang)))
                prim.append(('p', pp))
                pts_all += pp
            elif k == 'l':  # capsula ahusada
                a = self.tf1(*sh[1])
                b = self.tf1(*sh[2])
                r0 = sh[3] * self.scale * S
                r1 = sh[4] * self.scale * S
                dx, dy = b[0] - a[0], b[1] - a[1]
                ln = math.hypot(dx, dy)
                if ln < 1e-6:
                    prim.append(('c', a, max(r0, r1), max(r0, r1)))
                    pts_all += [(a[0] - r0, a[1] - r0), (a[0] + r0, a[1] + r0)]
                    continue
                nx, ny = -dy / ln, dx / ln
                prim.append(('p', [(a[0] + nx * r0, a[1] + ny * r0), (b[0] + nx * r1, b[1] + ny * r1),
                                   (b[0] - nx * r1, b[1] - ny * r1), (a[0] - nx * r0, a[1] - ny * r0)]))
                prim.append(('c', a, r0, r0))
                prim.append(('c', b, r1, r1))
                pts_all += [(a[0] - r0, a[1] - r0), (a[0] + r0, a[1] + r0), (b[0] - r1, b[1] - r1), (b[0] + r1, b[1] + r1)]
        if not pts_all:
            return None
        xs = [p[0] for p in pts_all]
        ys = [p[1] for p in pts_all]
        x0 = max(0, int(math.floor(min(xs))) - 3)
        y0 = max(0, int(math.floor(min(ys))) - 3)
        x1 = min(self.W * S, int(math.ceil(max(xs))) + 4)
        y1 = min(self.H * S, int(math.ceil(max(ys))) + 4)
        if x1 <= x0 or y1 <= y0:
            return None
        im = Image.new('L', (x1 - x0, y1 - y0), 0)
        dr = ImageDraw.Draw(im)
        for pr in prim:
            if pr[0] == 'p':
                dr.polygon([(x - x0, y - y0) for x, y in pr[1]], fill=255)
            else:
                c, rx, ry = pr[1], pr[2], pr[3]
                dr.ellipse([c[0] - rx - x0, c[1] - ry - y0, c[0] + rx - x0, c[1] + ry - y0], fill=255)
        return np.asarray(im) > 127, x0, y0

    def add(self, shapes, m, dome=3.0, tone=None, emissive=False, dith=1.0, rim=True, edge=True, gain=1.15, bias=0.0,
            speck=0.0, under=False, grad=0.24):
        """Dibuja una parte. tone=int -> relleno plano de ese tono (decal). emissive -> tono 5 plano."""
        r = self._mask(shapes)
        if r is None:
            return
        mask, x0, y0 = r
        S = self.S
        h, w = mask.shape
        base = MATS[m]['idx'] * 8 + 1
        reg = self.ids[y0:y0 + h, x0:x0 + w]
        if under:
            mask = mask & (reg == 0)
        if emissive:
            reg[mask] = base + 5
            return
        if tone is not None:
            reg[mask] = base + tone
            return
        d = ndi.distance_transform_edt(mask)
        dmax = d.max()
        if dmax <= 0:
            return
        rad = max(1.0, min(dmax, dome * self.scale * S))
        hh = np.minimum(d / rad, 1.0)
        hh = 1 - (1 - hh) ** 2
        hs = ndi.gaussian_filter(hh, 0.45 * S)
        gy, gx = np.gradient(hs)
        k = rad * 0.95
        nx, ny = -gx * k, -gy * k
        nz = np.ones_like(nx)
        nn = np.sqrt(nx * nx + ny * ny + nz * nz)
        lit = (nx * L[0] + ny * L[1] + nz * L[2]) / nn
        v = (lit - 0.52) * gain + 0.5 + bias
        yy, xx = np.mgrid[y0:y0 + h, x0:x0 + w]
        if grad:
            ys_, xs_ = np.nonzero(mask)
            cx_, cy_ = (xs_.min() + xs_.max()) / 2.0, (ys_.min() + ys_.max()) / 2.0
            hx_, hy_ = max(1.0, (xs_.max() - xs_.min()) / 2.0), max(1.0, (ys_.max() - ys_.min()) / 2.0)
            xn_, yn_ = (xx - x0 - cx_) / hx_, (yy - y0 - cy_) / hy_
            v = v + grad * (-0.6 * xn_ - 0.8 * yn_)
        bay = BAYER[(yy // S) % 4, (xx // S) % 4] - 0.5
        vv = v + bay * 0.09 * dith
        idx = 1 + (vv > 0.16).astype(np.int32) + (vv > 0.40) + (vv > 0.66) + (vv > 0.93)
        if speck:
            hsh = ((xx // S) * 73856093 ^ (yy // S) * 19349663) & 1023
            idx = idx - (hsh < speck * 1024) * 1
        idx = np.clip(idx, 1, 5).astype(np.int32)
        if edge:
            ew = 0.95 * S
            e = d < ew
            if rim:
                idx = np.where(e & (lit > 0.76), 5, idx)
            idx = np.where(e & (lit < 0.40), 0, idx)
        reg[mask] = (base + idx)[mask]

    # --------------------------------------------------------------- reduccion
    def reduce(self, alpha_thr=0.4):
        S, H, W = self.S, self.H, self.W
        ids = self.ids.reshape(H, S, W, S).transpose(0, 2, 1, 3).reshape(H, W, S * S)
        nz = (ids > 0).sum(-1)
        best = np.zeros((H, W), np.int32)
        bc = np.zeros((H, W), np.int32)
        for u in np.unique(ids):
            if u == 0:
                continue
            c = (ids == u).sum(-1)
            upd = c > bc
            best = np.where(upd, u, best)
            bc = np.where(upd, c, bc)
        best = np.where(nz >= alpha_thr * S * S, best, 0)
        pal = np.array(PAL, np.uint8)
        rgb = pal[best]
        a = np.where(best > 0, 255, 0).astype(np.uint8)
        return np.dstack([rgb, a[..., None]]), best


def outline(rgba, dark=0.27, lite=0.5, tint=(22, 10, 44)):
    """Contorno exterior 1px selectivo: oscuro abajo/derecha, mas claro arriba/izquierda."""
    a = rgba[..., 3] > 0
    H, W = a.shape
    pa = np.pad(a, 1)
    prgb = np.pad(rgba[..., :3].astype(np.float32), ((1, 1), (1, 1), (0, 0)))
    out = rgba.copy()
    ext = ~a
    acc = np.zeros((H, W, 3), np.float32)
    cnt = np.zeros((H, W), np.float32)
    lowside = np.zeros((H, W), bool)
    for dy, dx, low in ((1, 0, False), (-1, 0, True), (0, 1, False), (0, -1, True)):
        # vecino en (y+dy, x+dx)
        nb = pa[1 + dy:1 + dy + H, 1 + dx:1 + dx + W]
        col = prgb[1 + dy:1 + dy + H, 1 + dx:1 + dx + W]
        acc += col * nb[..., None]
        cnt += nb
        if low:  # el vecino esta arriba/izquierda -> el exterior esta abajo/derecha
            lowside |= nb
    m = ext & (cnt > 0)
    avg = acc / np.maximum(cnt, 1)[..., None]
    f = np.where(lowside, dark, lite)[..., None]
    c = avg * f + np.array(tint, np.float32) * 0.35 * (1 - f * 0.5)
    c = np.clip(c, 6, 255).astype(np.uint8)
    out[m, :3] = c[m]
    out[m, 3] = 255
    return out


# ------------------------------------------------------------------ overlays
class Overlay:
    """Capa RGBA semitransparente a alta resolucion (premultiplicada), para estelas y brillos."""

    def __init__(self, cv):
        self.cv = cv
        self.S = cv.S
        self.rgb = np.zeros((cv.H * cv.S, cv.W * cv.S, 3), np.float32)
        self.a = np.zeros((cv.H * cv.S, cv.W * cv.S), np.float32)

    def _over(self, mask01, color, alpha):
        m = mask01 * alpha
        # premult over
        self.rgb = np.array(color, np.float32)[None, None, :] * m[..., None] + self.rgb * (1 - m[..., None])
        self.a = m + self.a * (1 - m)

    def poly(self, pts, color, alpha, world=True, blur=0.0):
        S = self.S
        H, W = self.a.shape
        pp = [self.cv.tf1(*p) if world else (p[0] * S, p[1] * S) for p in pts]
        im = Image.new('L', (W, H), 0)
        ImageDraw.Draw(im).polygon(pp, fill=255)
        m = np.asarray(im, np.float32) / 255.0
        if blur:
            m = ndi.gaussian_filter(m, blur * S)
        self._over(m, color, alpha)

    def glow(self, c, rx, ry, color, alpha, power=2.0):
        H, W = self.a.shape
        cx, cy = self.cv.tf1(*c)
        sc = self.cv.scale * self.S
        yy, xx = np.mgrid[0:H, 0:W]
        r = np.sqrt(((xx - cx) / (rx * sc)) ** 2 + ((yy - cy) / (ry * sc)) ** 2)
        m = np.clip(1 - r, 0, 1) ** power
        self._over(m, color, alpha)

    def line(self, p0, p1, color, alpha, width=1.0):
        a = self.cv.tf1(*p0)
        b = self.cv.tf1(*p1)
        H, W = self.a.shape
        im = Image.new('L', (W, H), 0)
        ImageDraw.Draw(im).line([a, b], fill=255, width=max(1, int(width * self.S * self.cv.scale)))
        self._over(np.asarray(im, np.float32) / 255.0, color, alpha)

    def dot(self, p, color, alpha, r=0.6):
        c = self.cv.tf1(*p)
        H, W = self.a.shape
        im = Image.new('L', (W, H), 0)
        rr = r * self.S * self.cv.scale
        ImageDraw.Draw(im).ellipse([c[0] - rr, c[1] - rr, c[0] + rr, c[1] + rr], fill=255)
        self._over(np.asarray(im, np.float32) / 255.0, color, alpha)

    def reduce(self):
        S = self.S
        H, W = self.cv.H, self.cv.W
        a = self.a.reshape(H, S, W, S).mean((1, 3))
        rgb = self.rgb.reshape(H, S, W, S, 3).mean((1, 3))  # ya premultiplicado
        return rgb, a


def composite(back, sprite_rgba, front, shadow_mix=True):
    """back/front: (rgb_premult, a). Devuelve RGBA uint8."""
    H, W = sprite_rgba.shape[:2]
    out_rgb = np.zeros((H, W, 3), np.float32)
    out_a = np.zeros((H, W), np.float32)

    def over_pm(rgb_pm, a):
        nonlocal out_rgb, out_a
        out_rgb = rgb_pm + out_rgb * (1 - a[..., None])
        out_a = a + out_a * (1 - a)

    if back is not None:
        over_pm(*back)
    sa = (sprite_rgba[..., 3] > 0).astype(np.float32)
    over_pm(sprite_rgba[..., :3].astype(np.float32) * sa[..., None], sa)
    if front is not None:
        over_pm(*front)
    rgb = np.where(out_a[..., None] > 1e-4, out_rgb / np.maximum(out_a[..., None], 1e-4), 0)
    res = np.dstack([np.clip(rgb, 0, 255), np.clip(out_a, 0, 1) * 255]).round().astype(np.uint8)
    # evita semitransparencia muy tenue (ruido)
    res[..., 3] = np.where(res[..., 3] < 10, 0, res[..., 3])
    return res
