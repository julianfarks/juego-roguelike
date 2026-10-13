"""Helpers de dibujo y pipeline de render por fotograma."""
import math
from types import SimpleNamespace as NS
import numpy as np
from kit import Canvas, Overlay, outline, composite, reset_mats, hexc, mat
from rig import Seq, skeleton, simulate, ribbon_poly, dirv, add


class Ctx:
    pass


def circ(X, c, r, m, **kw):
    X.cv.add([('c', c, r)], m, **kw)


def cap(X, a, b, r0, r1, m, **kw):
    X.cv.add([('l', a, b, r0, r1)], m, **kw)


def poly(X, pts, m, **kw):
    X.cv.add([('p', pts)], m, **kw)


def ell(X, c, rx, ry, ang, m, **kw):
    X.cv.add([('e', c, rx, ry, ang)], m, **kw)


def tp(X, uv):
    return [X.sk.T(u * X.D.k, v * X.D.k) for u, v in uv]


def hp(X, uv, s=1.0):
    """puntos en el marco de la cabeza (u adelante, v arriba) desde el centro de la cabeza."""
    c, f, up = X.sk.head, X.sk.hf, X.sk.hv
    k = X.D.k * s
    return [(c[0] + f[0] * u * k + up[0] * v * k, c[1] + f[1] * u * k + up[1] * v * k) for u, v in uv]


def hpt(X, u, v, s=1.0):
    return hp(X, [(u, v)], s)[0]


def wpt(X, x, y, hand=None):
    """punto en el marco del arma (x a lo largo del filo desde la mano, y perpendicular), mano delantera."""
    h = hand or X.sk.handF
    k = X.D.k
    return (h[0] + X.sk.wv[0] * x * k + X.sk.wn[0] * y * k, h[1] + X.sk.wv[1] * x * k + X.sk.wn[1] * y * k)


def wpoly(X, uvs, hand=None):
    return [wpt(X, x, y, hand) for x, y in uvs]


def boot(X, ank, pitch, m_boot, m_cuff=None, length=4.4, hgt=2.6, sole=None):
    a = math.radians(pitch)
    f = (math.cos(a), math.sin(a))
    n = (-f[1], f[0])
    k = X.D.k
    heel = (ank[0] - f[0] * 1.6 * k + n[0] * 0.9 * k, ank[1] - f[1] * 1.6 * k + n[1] * 0.9 * k)
    toe = (ank[0] + f[0] * (length - 1.6) * k + n[0] * 0.7 * k, ank[1] + f[1] * (length - 1.6) * k + n[1] * 0.7 * k)
    top = (ank[0] - n[0] * 1.0 * k, ank[1] - n[1] * 1.0 * k)
    X.cv.add([('l', heel, toe, 1.35 * k, 1.1 * k), ('l', top, ank, 1.5 * k, 1.5 * k)], m_boot, dome=2.0)


def leg(X, hip, knee, ank, r0, r1, r2, m, m_boot=None, pitch=0, boot_fn=None, kneepad=None, greave=None):
    X.cv.add([('l', hip, knee, r0 * X.D.k, r1 * X.D.k), ('l', knee, ank, r1 * X.D.k, r2 * X.D.k)], m, dome=2.2)
    if greave:
        mid = ((knee[0] + ank[0]) / 2, (knee[1] + ank[1]) / 2)
        X.cv.add([('l', (knee[0] * 0.8 + ank[0] * 0.2, knee[1] * 0.8 + ank[1] * 0.2), (ank[0] * 0.85 + knee[0] * 0.15, ank[1] * 0.85 + knee[1] * 0.15),
                   (r1 + 0.5) * X.D.k, (r2 + 0.35) * X.D.k)], greave, dome=1.6)
    if kneepad:
        circ(X, knee, (r1 + 0.7) * X.D.k, kneepad, dome=1.6)
    if m_boot:
        boot(X, ank, pitch, m_boot)


def arm(X, sh, el, hand, r0, r1, r2, m, glove=None, bracer=None, hand_r=1.35):
    k = X.D.k
    X.cv.add([('l', sh, el, r0 * k, r1 * k), ('l', el, hand, r1 * k, r2 * k)], m, dome=2.0)
    if bracer:
        a = (el[0] * 0.55 + hand[0] * 0.45, el[1] * 0.55 + hand[1] * 0.45)
        b = (el[0] * 0.1 + hand[0] * 0.9, el[1] * 0.1 + hand[1] * 0.9)
        X.cv.add([('l', a, b, (r2 + 0.6) * k, (r2 + 0.45) * k)], bracer, dome=1.5)
    circ(X, hand, hand_r * k, glove or m, dome=1.5)


def lerp_pt(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def ribbons_draw(X, name, m, **kw):
    pts = X.rb[name]
    r = X.cls.rib_by_name[name]
    poly(X, ribbon_poly(pts, [w * X.D.k for w in r.widths]), m, **kw)


# -------------------------------------------------------------------- render
def render_frame(cls, seq, rb, i, n, name, mode='sprite', t=None, size=(64, 48), S=4, scale=1.0, origin=(32, 44),
                 shift=(0, 0), trail=None, pose=None):
    p = pose if pose is not None else seq.at(i if t is None else t)
    sk = skeleton(p, cls.D)
    cv = Canvas(size[0], size[1], S=S, scale=scale, origin=origin, rot=p.rot, rot_c=(p.hx, -10 + p.hy * 0.5), shift=shift)
    X = Ctx()
    X.cv, X.p, X.sk, X.D, X.cls = cv, p, sk, cls.D, cls
    X.ob, X.of = Overlay(cv), Overlay(cv)
    X.rb = {k: v[i] for k, v in rb.items()} if rb else {}
    X.mode = mode
    X.detail = 2 if mode == 'splash' else (1.5 if mode == 'portrait' else 1)
    X.name, X.i, X.n = name, i, n
    X.sc = scale
    cls.draw(X)
    cls.fx(X, name, i, n)
    if trail is not None:
        trail(X)
    rgba, ids = cv.reduce()
    rgba = outline(rgba)
    return composite(X.ob.reduce(), rgba, X.of.reduce())


def wfr(X, hand, ang, x, y):
    """punto en un marco de arma arbitrario (mano, angulo)."""
    d = dirv(ang)
    n = (d[1], -d[0])
    k = X.D.k
    return (hand[0] + d[0] * x * k + n[0] * y * k, hand[1] + d[1] * x * k + n[1] * y * k)


def wfpoly(X, hand, ang, uvs):
    return [wfr(X, hand, ang, x, y) for x, y in uvs]


def spark4(X, c, r, m, tone=5):
    """destello de 4 puntas."""
    x, y = c
    poly(X, [(x, y - r), (x + r * 0.28, y - r * 0.28), (x + r, y), (x + r * 0.28, y + r * 0.28), (x, y + r),
             (x - r * 0.28, y + r * 0.28), (x - r, y), (x - r * 0.28, y - r * 0.28)], m, emissive=True)
