"""Herramientas para fondos parallax teselables (512x288)."""
import numpy as np
from PIL import Image, ImageDraw
from kit import hexrgb, fbm, vnoise, rng, BAYER

W, H = 512, 288
YY, XX = np.mgrid[0:H, 0:W]
BAY = np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W]


def C(h):
    return hexrgb(h)


def grad(stops):
    """Gradiente vertical: stops [(t, '#hex'), ...] -> (H,W,3)."""
    ts = [s[0] for s in stops]
    cols = np.array([hexrgb(s[1]) for s in stops])
    t = np.linspace(0, 1, H)
    col = np.stack([np.interp(t, ts, cols[:, i]) for i in range(3)], 1)
    return np.repeat(col[:, None, :], W, 1).astype(np.float32)


def noise(cx, cy, octv=4, seed=0, gain=.5):
    return fbm(W, H, cx, cy, octv, seed, gain).astype(np.float32)


def wrapdx(cx):
    d = np.abs(XX - cx)
    return np.minimum(d, W - d)


def glow_add(img, cx, cy, r, col, k=1.0, power=2.0, sy=1.0):
    d = np.sqrt(wrapdx(cx) ** 2 + ((YY - cy) / sy) ** 2)
    f = np.clip(1 - d / r, 0, 1) ** power * k
    img += f[..., None] * (hexrgb(col) if isinstance(col, str) else col)
    return img


def ridge(cx, seed, octv=3, gain=.5):
    return fbm(W, 1, cx, 1, octv, seed, gain)[0].astype(np.float32)


class Mask:
    """Mascara de formas con envoltura horizontal."""

    def __init__(self):
        self.im = Image.new('L', (W, H), 0)
        self.d = ImageDraw.Draw(self.im)

    def poly(self, pts, v=255):
        xs = [p[0] for p in pts]
        for ox in (-W, 0, W):
            if max(xs) + ox >= 0 and min(xs) + ox < W:
                self.d.polygon([(x + ox, y) for x, y in pts], fill=v)
        return self

    def rect(self, x0, y0, x1, y1, v=255):
        for ox in (-W, 0, W):
            self.d.rectangle([x0 + ox, y0, x1 - 1 + ox, y1 - 1], fill=v)
        return self

    def ell(self, cx, cy, rx, ry, v=255):
        for ox in (-W, 0, W):
            self.d.ellipse([cx - rx + ox, cy - ry, cx + rx + ox, cy + ry], fill=v)
        return self

    def line(self, pts, w=1, v=255):
        for ox in (-W, 0, W):
            self.d.line([(x + ox, y) for x, y in pts], fill=v, width=w)
        return self

    def heightfield(self, base_y, hf, amp):
        """Rellena desde un perfil hf[x] (0..1) hasta abajo."""
        ys = base_y - hf * amp
        for x in range(W):
            self.d.line([(x, int(ys[x])), (x, H)], fill=255)
        return self

    def arr(self):
        return np.asarray(self.im) > 127


def shift(m, dy=0, dx=0):
    out = np.roll(np.roll(m, dy, 0), dx, 1)
    return out


class Layer:
    """Capa RGBA en float."""

    def __init__(self, opaque_rgb=None):
        if opaque_rgb is not None:
            self.rgb = opaque_rgb.astype(np.float32).copy()
            self.a = np.ones((H, W), np.float32)
        else:
            self.rgb = np.zeros((H, W, 3), np.float32)
            self.a = np.zeros((H, W), np.float32)

    def paint(self, mask, col, alpha=1.0):
        m = mask
        if isinstance(col, str):
            col = hexrgb(col)
        col = np.asarray(col, np.float32)
        if col.ndim == 1:
            self.rgb[m] = col
        else:
            self.rgb[m] = col[m]
        if isinstance(alpha, np.ndarray):
            self.a[m] = alpha[m]
        else:
            self.a[m] = alpha
        return self

    def blend(self, mask_f, col, k=1.0):
        """Mezcla suave: mask_f float 0..1 sobre lo existente (y crea alfa)."""
        if isinstance(col, str):
            col = hexrgb(col)
        col = np.asarray(col, np.float32)
        f = np.clip(mask_f * k, 0, 1)
        newa = self.a + f * (1 - self.a)
        w = np.where(newa > 0, f / np.maximum(newa, 1e-6), 0)
        c = col if col.ndim == 3 else col[None, None, :]
        self.rgb = self.rgb * (1 - w[..., None]) + c * w[..., None]
        self.a = newa
        return self

    def tint_inside(self, mask, col, k):
        if isinstance(col, str):
            col = hexrgb(col)
        self.rgb[mask] = self.rgb[mask] * (1 - k) + np.asarray(col) * k
        return self

    def rim(self, mask, col, up=True, left=True, k=1.0, ex=None):
        """Luz de borde en bordes superior/izquierdo de la silueta."""
        if isinstance(col, str):
            col = hexrgb(col)
        e = np.zeros_like(mask)
        if up:
            e |= mask & ~shift(mask, 1, 0)
        if left:
            e |= mask & ~shift(mask, 0, 1)
        if ex is not None:
            e &= ex
        self.rgb[e] = self.rgb[e] * (1 - k) + np.asarray(col) * k
        return self

    def glowlit(self, mask, col, k=1.0):
        if isinstance(col, str):
            col = hexrgb(col)
        self.rgb[mask] = np.asarray(col)
        self.a[mask] = 1.0
        return self

    def haze(self, col, y0, y1, amount):
        """Mezcla el RGB existente hacia 'col' con gradiente vertical (neblina de lejania)."""
        if isinstance(col, str):
            col = hexrgb(col)
        t = np.clip((YY - y0) / max(1, (y1 - y0)), 0, 1)
        f = (t * amount)[..., None]
        self.rgb = self.rgb * (1 - f) + np.asarray(col) * f
        return self

    def fog(self, ycenter, height, col, amount, seed, cx=3, alpha_cap=.7, stretch=1.0):
        n = fbm(W, H, cx, 2, 4, seed, .55).astype(np.float32)
        prof = np.exp(-((YY - ycenter) / height) ** 2)
        f = np.clip((n * 1.5 - .35) * prof * amount, 0, alpha_cap)
        return self.blend(f, col)

    def to_img(self, colors=64, alevels=5, dither=True):
        rgb = np.clip(self.rgb, 0, 255)
        a = np.clip(self.a, 0, 1)
        if dither:
            q = np.floor(a * (alevels - 1) + .5 + BAY * .95) / (alevels - 1)
            a = np.clip(q, 0, 1)
            # evita que el borde solido pierda opacidad por el dither: lo solido sigue solido
            a = np.where(self.a > .97, 1.0, a)
        out = np.zeros((H, W, 4), np.uint8)
        out[..., :3] = rgb.astype(np.uint8)
        out[..., 3] = (a * 255 + .5).astype(np.uint8)
        out[out[..., 3] == 0, :3] = 0
        return out


def posterize(rgb, levels=12, amp=.9):
    """Dither ordenado -> pocos tonos (pixel art limpio)."""
    step = 255.0 / levels
    v = rgb / step + BAY[..., None] * amp
    return np.clip(np.floor(v + .5) * step, 0, 255)


def finish_opaque(rgb, path, colors=56, levels=14):
    from kit import save_quant
    p = posterize(rgb, levels)
    im = Image.fromarray(p.astype(np.uint8), 'RGB')
    save_quant(im, path, colors)


def finish_alpha(layer, path, colors=56):
    from kit import save_quant
    arr = layer.to_img()
    im = Image.fromarray(arr, 'RGBA')
    save_quant(im, path, colors)


def stars(rgb, n, seed, ymax=.6, bright=(120, 255), tint=(1, 1, 1), big=.12):
    r = rng(seed)
    for _ in range(n):
        x = r.randint(0, W)
        y = int(r.rand() ** 1.3 * H * ymax)
        b = r.randint(*bright)
        col = np.array(tint, np.float32) * b
        rgb[y, x] = np.maximum(rgb[y, x], col)
        if r.rand() < big:
            for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx = (x + dx) % W
                yy = min(H - 1, max(0, y + dy))
                rgb[yy, xx] = np.maximum(rgb[yy, xx], col * .45)
    return rgb


def ordered_threshold(f, levels):
    """f float 0..1 -> niveles discretos con dither."""
    return np.clip(np.floor(f * levels + .5 + BAY * .9), 0, levels) / levels
