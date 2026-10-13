"""Retratos 32x32 y splash 128x176 con el mismo rig a mayor resolucion."""
import numpy as np
from PIL import Image
from rig import Seq, skeleton, simulate
from common import render_frame
from kit import hexc

HERO = dict(lean=7, hy=1.5, ffx=7.0, bfx=-5.5, wx=-0.5, hd=0)


def _pose(cls, extra, wind=-0.5):
    base = cls.carry_base()
    base.update(HERO)
    base.update(getattr(cls, 'splash', {}))
    base.update(extra)
    base['wx'] = wind
    return Seq(base, [(0, {})])


def _rb(cls, seq):
    return simulate(cls.ribbons, seq.at, lambda p: skeleton(p, cls.D), 1, loop=False, pre=80)


def _alpha_bbox(img):
    a = img[..., 3] > 20
    ys, xs = np.nonzero(a)
    return xs.min(), xs.max(), ys.min(), ys.max()


def rim(img, col, amt=0.6):
    a = img[..., 3] > 0
    H, W = a.shape
    pa = np.pad(a, 1)
    up = ~pa[0:H, 1:W + 1]
    left = ~pa[1:H + 1, 0:W]
    edge = a & (up | left)
    out = img.copy()
    c = np.array(col, np.float32)
    out[edge, :3] = (out[edge, :3] * (1 - amt) + c * amt).astype(np.uint8)
    return out


def splash(cls):
    seq = _pose(cls, {})
    rb = _rb(cls, seq)
    # pasada 1 para encuadrar
    S1 = 4.0
    im1 = render_frame(cls, seq, rb, 0, 1, 'splash', mode='splash', size=(300, 400), S=2, scale=S1, origin=(150, 340))
    x0, x1, y0, y1 = _alpha_bbox(im1)
    bw, bh = (x1 - x0 + 1), (y1 - y0 + 1)
    s = min(118.0 / bw, 164.0 / bh) * S1
    s = min(s, 5.4)
    cx, bot = (x0 + x1) / 2 - 150, y1 + 1 - 340
    ox, oy = 64 - cx * s / S1, 171 - bot * s / S1
    im = render_frame(cls, seq, rb, 0, 1, 'splash', mode='splash', size=(128, 176), S=4, scale=s, origin=(ox, oy))
    im = rim(im, cls.core, 0.55)
    return Image.fromarray(im, 'RGBA')


def portrait(cls):
    seq = _pose(cls, dict(lean=3, hy=0, ffx=4, bfx=-4), wind=-0.1)
    rb = _rb(cls, seq)
    sk = skeleton(seq.at(0), cls.D)
    hx, hy = sk.head
    s = 1.62
    ox, oy = 14.5 - hx * s, 15.0 - hy * s
    im = render_frame(cls, seq, rb, 0, 1, 'portrait', mode='portrait', size=(32, 32), S=6, scale=s, origin=(ox, oy))
    im = rim(im, cls.core, 0.45)
    return Image.fromarray(im, 'RGBA')
