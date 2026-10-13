"""Utilidades comunes (solo anade) para los jefes de la parte 2: poses de arma a dos manos, FX extra."""
import math
import numpy as np
from kit import *
from anim import *
from fxlib import *


def clamp01(t):
    return max(0.0, min(1.0, t))


def make_H(torso='torso', uf='uarm_f', ff='farm_f', wp='weapon'):
    def H(t, u, f, w):
        return {torso: t, uf: u, ff: f, wp: w - (t + u + f)}
    return H


def make_post(weapon, ub, fb, hand_b, hand_pt, grip_default, zb=10.4, zh=10.6):
    """IK de la mano trasera hacia el arma (a dos manos) salvo pose['free_b']."""
    def post(boss, pose):
        if pose.get('free_b', 0) < 0.5:
            tgt = boss.anchor(pose, weapon, (0, pose.get('grip2', grip_default)))
            pose = dict(pose)
            pose.update(boss.ik(pose, ub, fb, hand_pt, tgt, flip=pose.get('bend', 1)))
            for n in (ub, fb):
                pose[n + '.z'] = zb
            pose[hand_b + '.z'] = zh
        return pose
    return post


# ---------------------------------------------------------------- FX extra
def bat(fx, x, y, s=1.0, ph=0.0, col=(30, 8, 24), edge=(120, 20, 44), a=1.0, layer='front'):
    """murcielago pequeno visto de frente con aleteo (ph en 0..1)."""
    fl = math.sin(ph * 6.283)
    wy = -3.2 * s * fl
    L = [(x, y), (x - 3.5 * s, y + wy - 1.5 * s), (x - 7.5 * s, y + wy * 1.4 + 0.5 * s), (x - 6 * s, y + 1.5 * s), (x - 4 * s, y + 0.6 * s), (x - 2.5 * s, y + 2 * s)]
    R = [(x, y), (x + 3.5 * s, y + wy - 1.5 * s), (x + 7.5 * s, y + wy * 1.4 + 0.5 * s), (x + 6 * s, y + 1.5 * s), (x + 4 * s, y + 0.6 * s), (x + 2.5 * s, y + 2 * s)]
    fx.poly(L, edge, a, layer)
    fx.poly(R, edge, a, layer)
    fx.poly([(x - 1.6 * s, y - 1 * s), (x + 1.6 * s, y - 1 * s), (x + 1.2 * s, y + 3 * s), (x - 1.2 * s, y + 3 * s)], col, a, layer)
    fx.poly([(x - 1.5 * s, y - 1 * s), (x - 1.0 * s, y - 3 * s), (x - 0.4 * s, y - 1 * s)], col, a, layer)
    fx.poly([(x + 1.5 * s, y - 1 * s), (x + 1.0 * s, y - 3 * s), (x + 0.4 * s, y - 1 * s)], col, a, layer)
    fx.dots([(x - 0.8 * s, y)], (255, 80, 90), a, layer)


def fogband(ctx, y, h, cols, t, seed=0, a=0.5, layer='back', x0=0, x1=None, n=7, amp=3.0):
    """banda de niebla ondulante hecha de elipses grandes con alfa bajo."""
    fx = ctx.fx
    x1 = ctx.W if x1 is None else x1
    rng = np.random.default_rng(seed)
    for k in range(n):
        px = x0 + (x1 - x0) * (k + rng.random() * 0.6) / n
        px += math.sin((t + rng.random()) * 6.283) * amp
        py = y + (rng.random() - 0.5) * h * 0.5
        rx = (x1 - x0) / n * (0.9 + rng.random() * 0.8)
        ry = h * (0.35 + rng.random() * 0.35)
        fx.ell(px, py, rx, ry, cols[k % len(cols)], a * (0.6 + 0.4 * rng.random()), layer, soft=2.0)


def eye(fx, x, y, rx, ry, col=(255, 60, 70), rim=(40, 6, 14), look=0.0, a=1.0, layer='front', lid=0.0, glow=0.5):
    """ojo almendrado con pupila rasgada y brillo. lid 0 abierto..1 cerrado."""
    ry2 = max(0.4, ry * (1 - lid))
    fx.ell(x, y, rx + 0.8, ry2 + 0.8, rim, a, layer)
    fx.ell(x, y, rx, ry2, (250, 238, 220), a, layer)
    fx.ell(x + look * rx * 0.4, y, rx * 0.6, ry2 * 0.95, col, a, layer)
    fx.ell(x + look * rx * 0.4, y, max(0.4, rx * 0.16), ry2 * 0.9, (20, 0, 8), a, layer)
    fx.dots([(x - rx * 0.3, y - ry2 * 0.35)], (255, 255, 255), a, layer)
    if glow > 0:
        fx.glow(x, y, rx * 2.4, col, glow * a)


def starfield(ctx, x, y, w, h, n, seed=1, t=0.0, a=1.0, cols=((255, 255, 255), (200, 210, 255), (255, 190, 200)), layer='front'):
    rng = np.random.default_rng(seed)
    for k in range(n):
        px = x + (rng.random() - 0.5) * w; py = y + (rng.random() - 0.5) * h
        tw = 0.5 + 0.5 * math.sin((t + rng.random()) * 6.283 * 2)
        ctx.fx.dots([(px, py)], cols[k % len(cols)], a * (0.35 + 0.65 * tw), layer)
        if tw > 0.9 and k % 3 == 0:
            ctx.fx.dots([(px - 1, py), (px + 1, py), (px, py - 1), (px, py + 1)], cols[k % len(cols)], a * 0.5, layer)


def beam(ctx, p0, p1, w, hi, lo, a=0.9, layer='front'):
    fx = ctx.fx
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) + 1e-6
    nx, ny = -dy / L, dx / L
    for k, (ww, c, al) in enumerate(((w * 1.0, lo, 0.45), (w * 0.62, hi, 0.8), (w * 0.28, (255, 255, 255), 1.0))):
        fx.poly([(p0[0] + nx * ww / 2, p0[1] + ny * ww / 2), (p1[0] + nx * ww / 3, p1[1] + ny * ww / 3),
                 (p1[0] - nx * ww / 3, p1[1] - ny * ww / 3), (p0[0] - nx * ww / 2, p0[1] - ny * ww / 2)], c, a * al, layer, ss=2)


def pool(ctx, x, y, rx, ry, cols, a=1.0, layer='back'):
    """charco / mancha plana en el suelo (elipses concentricas)."""
    for j, c in enumerate(cols):
        k = 1 - j * 0.26
        ctx.fx.ell(x - j * 0.6, y - j * 0.3, rx * k, ry * k, c, a, layer)


def squash_pose(sy, sx=None):
    sx = 1.0 / sy if sx is None else sx
    return {'torso.sy': sy, 'torso.sx': sx}


def link_chain(ctx, pts, w=3.0, base=(150, 156, 176), hi=(235, 240, 255), edge=(30, 20, 40), teeth=(220, 40, 70), layer='front', a=1.0, toothevery=2):
    """cadena/latigo de eslabones (sierra-latigo): pts lista de puntos."""
    fx = ctx.fx
    for k in range(len(pts) - 1):
        x0, y0 = pts[k]; x1, y1 = pts[k + 1]
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) + 1e-6
        nx, ny = -dy / L, dx / L
        ww = w * (1 - 0.45 * k / max(1, len(pts) - 1))
        quad = [(x0 + nx * ww / 2, y0 + ny * ww / 2), (x1 + nx * ww / 2, y1 + ny * ww / 2), (x1 - nx * ww / 2, y1 - ny * ww / 2), (x0 - nx * ww / 2, y0 - ny * ww / 2)]
        fx.poly([(px + nx * 0.0, py) for px, py in quad], edge, a, layer)
        inner = [(x0 + nx * (ww / 2 - 0.8), y0 + ny * (ww / 2 - 0.8)), (x1 + nx * (ww / 2 - 0.8), y1 + ny * (ww / 2 - 0.8)),
                 (x1 - nx * (ww / 2 - 0.8), y1 - ny * (ww / 2 - 0.8)), (x0 - nx * (ww / 2 - 0.8), y0 - ny * (ww / 2 - 0.8))]
        fx.poly(inner, base if k % 2 else hi, a, layer)
        if k % toothevery == 0:
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            fx.poly([(mx - dx / L * 1.2 + nx * ww / 2, my - dy / L * 1.2 + ny * ww / 2), (mx + dx / L * 1.2 + nx * ww / 2, my + dy / L * 1.2 + ny * ww / 2),
                     (mx + nx * (ww / 2 + 2.6), my + ny * (ww / 2 + 2.6))], teeth, a, layer)


def fur_edge(p, curve, side=1, n=10, ln=(3.0, 6.0), w=2.4, seed=0, drift=0.5, mat=None, **kw):
    """pelos/pinchos a lo largo de una curva (lista de puntos): triangulos que salen hacia 'side' (+1/-1 = normal izq/der)."""
    rng = np.random.default_rng(seed)
    c = catmull(curve, False, 8) if len(curve) > 2 else np.asarray(curve, float)
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(c, axis=0).T))]
    L = d[-1]
    for k in range(n):
        s = (k + 0.5 + (rng.random() - 0.5) * 0.5) / n * L
        x = np.interp(s, d, c[:, 0]); y = np.interp(s, d, c[:, 1])
        x2 = np.interp(min(L, s + 0.8), d, c[:, 0]); y2 = np.interp(min(L, s + 0.8), d, c[:, 1])
        tx, ty = x2 - x, y2 - y
        tl = math.hypot(tx, ty) + 1e-6
        tx, ty = tx / tl, ty / tl
        nx, ny = -ty * side, tx * side
        l = ln[0] + (ln[1] - ln[0]) * rng.random()
        ww = w * (0.7 + 0.6 * rng.random())
        tri = [(x - tx * ww / 2 - nx * 1.2, y - ty * ww / 2 - ny * 1.2), (x + tx * ww / 2 - nx * 1.2, y + ty * ww / 2 - ny * 1.2),
               (x + nx * l + tx * l * drift, y + ny * l + ty * l * drift)]
        if mat is None:
            p.poly(tri, **kw)
        else:
            p.poly(tri, mat=mat, **kw)
