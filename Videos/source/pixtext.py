"""Texto animado con la fuente pixel REAL del juego (Shared/assets/font/font_b.png): dorado oscuro con brillo carmesi.
Todo el escalado es por vecino mas cercano (pixeles nitidos)."""
import json, os
import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
FONT_DIR = os.path.join(ROOT, 'Shared', 'assets', 'font')
_meta = json.load(open(os.path.join(FONT_DIR, 'font_b.json'), encoding='utf-8'))
_atlas = np.array(Image.open(os.path.join(FONT_DIR, 'font_b.png')).convert('RGBA'))
CW, CH, COLS, BASE, SPC = _meta['cellW'], _meta['cellH'], _meta['cols'], _meta['baseline'], _meta['spacing']
CHARS, WIDTHS = _meta['chars'], _meta['widths']


def missing(text):
    return sorted({c for c in text if c not in CHARS})


def mask(text):
    """Mascara alfa (alto CH) del texto a tamano nativo."""
    bad = missing(text)
    if bad:
        raise ValueError('caracteres sin glifo: %r' % bad)
    w = sum(WIDTHS[CHARS.index(c)] + SPC for c in text)
    out = np.zeros((CH, max(w, 1)), np.uint8)
    x = 0
    for c in text:
        i = CHARS.index(c)
        cx, cy = (i % COLS) * CW, (i // COLS) * CH
        g = np.where(_atlas[cy:cy + CH, cx:cx + CW, 3] > 0, np.where(_atlas[cy:cy + CH, cx:cx + CW, 0] > 100, 255, 128), 0).astype(np.uint8)
        ww = min(CW, out.shape[1] - x)
        out[:, x:x + ww] = np.maximum(out[:, x:x + ww], g[:, :ww])
        x += WIDTHS[i] + SPC
    return out


def render(text, scale, top=(255, 232, 150), bot=(214, 120, 30), edge=(70, 6, 16), glow=(255, 60, 40), glow_r=0.0):
    """RGBA (numpy) del texto: relleno degradado dorado, contorno oscuro de 1 px nativo y sombra; glow opcional."""
    m = mask(text)
    pad = 2
    mp = np.pad(m, ((pad, pad + 1), (pad, pad + 1)))
    solid = (mp > 200)           # relleno claro; los pixeles 128 son el contorno oscuro que ya trae el atlas
    shape = (mp > 0)
    # contorno: dilatacion 1 px nativo (8 vecinos) + sombra desplazada
    d = shape.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            d |= np.roll(np.roll(shape, dy, 0), dx, 1)
    sh = np.roll(np.roll(d, 2, 0), 1, 1)
    H, W = solid.shape
    img = np.zeros((H, W, 4), np.uint8)
    img[sh] = (20, 0, 4, 200)
    img[d] = (*edge, 255)
    t = np.linspace(0, 1, H)[:, None, None]
    grad = (np.array(top) * (1 - t) + np.array(bot) * t).astype(np.uint8)
    grad = np.broadcast_to(grad, (H, W, 3))
    img[solid, :3] = grad[solid]
    img[solid, 3] = 255
    im = Image.fromarray(img, 'RGBA').resize((W * scale, H * scale), Image.NEAREST)
    if glow_r > 0:
        a = np.array(im)[:, :, 3]
        g = Image.fromarray(a).filter(ImageFilter.GaussianBlur(glow_r))
        ga = (np.array(g).astype(np.float32) * 0.9).clip(0, 255).astype(np.uint8)
        gl = np.zeros((*ga.shape, 4), np.uint8)
        gl[..., :3] = glow
        gl[..., 3] = ga
        base = Image.fromarray(gl, 'RGBA')
        base.alpha_composite(im)
        im = base
    return np.array(im)


def width_px(text, scale):
    return (sum(WIDTHS[CHARS.index(c)] + SPC for c in text) + 5) * scale


def blit(frame, rgba, cx, cy, alpha=1.0, scale_f=1.0, dx=0, dy=0):
    """Compone rgba centrado en (cx,cy) sobre frame (uint8 HxWx3, in place). scale_f reescala con vecino mas cercano."""
    if alpha <= 0:
        return
    if abs(scale_f - 1.0) > 1e-3:
        h, w = rgba.shape[:2]
        im = Image.fromarray(rgba, 'RGBA').resize((max(1, int(w * scale_f)), max(1, int(h * scale_f))), Image.NEAREST)
        rgba = np.array(im)
    h, w = rgba.shape[:2]
    x0 = int(cx - w / 2 + dx); y0 = int(cy - h / 2 + dy)
    fh, fw = frame.shape[:2]
    sx0, sy0 = max(0, -x0), max(0, -y0)
    ex, ey = min(w, fw - x0), min(h, fh - y0)
    if ex <= sx0 or ey <= sy0:
        return
    src = rgba[sy0:ey, sx0:ex]
    a = (src[:, :, 3:4].astype(np.float32) / 255.0) * alpha
    dst = frame[y0 + sy0:y0 + ey, x0 + sx0:x0 + ex]
    dst[:] = (dst * (1 - a) + src[:, :, :3] * a).astype(np.uint8)
