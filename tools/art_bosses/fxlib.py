"""Efectos reutilizables que dibujan en el Fx del fotograma (coordenadas de celda, 1x)."""
import math
import numpy as np
from kit import lerp


def plerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def ease_out(t):
    return 1 - (1 - t) ** 2.5


def clamp01(t):
    return max(0.0, min(1.0, t))


def trail(ctx, bone, tip, base, f0, f1, hi, lo, steps=7, span=3.2, a=0.9, layer='front', width_scale=1.0, mid=None):
    """Estela de arma: barrido del segmento base-punta entre frames; visible en f0..f1+2."""
    i = ctx.i
    if i < f0 or i > f1 + 2:
        return
    A = []; B = []
    for k in range(steps):
        ff = i - k * span / (steps - 1)
        if ff < f0 - 1:
            break
        p = ctx.pose_at(max(0.0, ff))
        ta = ctx.anchor(bone, tip, p); tb = ctx.anchor(bone, base, p)
        A.append(ta); B.append(tb)
    if len(A) < 2:
        return
    fade = 1.0 if i <= f1 else max(0.0, 1.0 - (i - f1) / 3.0)
    ctx.fx.smear(A, B, hi, lo, a * fade, layer)
    if mid is not None:
        ctx.fx.smear([plerp(a_, b_, 0.35) for a_, b_ in zip(A, B)], [plerp(a_, b_, 0.65) for a_, b_ in zip(A, B)], hi, mid, a * fade * 0.7, layer, core=False)


def dust(ctx, x, y, t, col=(150, 140, 150), n=10, spread=26, rise=10, size=2.4, layer='front', a=0.7):
    rng = np.random.default_rng(int(x * 13 + y * 7) + 5)
    for k in range(n):
        ang = math.pi * (0.1 + 0.8 * rng.random()) * (1 if k % 2 else -1)
        side = 1 if k % 2 else -1
        d = spread * ease_out(t) * (0.35 + 0.65 * rng.random())
        px = x + side * d
        py = y - rise * ease_out(t) * rng.random() * 1.4 - 1
        r = size * (0.6 + 0.8 * rng.random()) * (1 - 0.5 * t) + 0.6
        ctx.fx.ell(px, py, r * 1.2, r, col, a * (1 - t * 0.8), layer)


def shock(ctx, x, y, t, col=(200, 255, 220), rx=50, ry=6, w=2, a=0.9, layer='front'):
    r = ease_out(t)
    ctx.fx.ring(x, y, rx * r + 2, ry * r + 1, w, col, a * (1 - t * 0.75), layer)
    ctx.fx.ring(x, y, rx * r * 0.8 + 1, ry * r * 0.8, 1, (255, 255, 255), a * (1 - t) * 0.8, layer)


def ground_cracks(ctx, x, y, t, col=(20, 18, 28), glow=None, n=7, length=40, seed=3, layer='back'):
    rng = np.random.default_rng(seed)
    for k in range(n):
        side = 1 if k % 2 == 0 else -1
        ang = (rng.random() * 0.5 + 0.02) * side
        L = length * (0.45 + 0.55 * rng.random()) * clamp01(t * 1.6)
        pts = [(x, y)]
        px, py = x, y
        for s in range(6):
            px += side * L / 6 * (0.8 + 0.4 * rng.random())
            py += (rng.random() - 0.35) * 2.0 + abs(ang) * 3
            pts.append((px, min(py, y + 4)))
        ctx.fx.polyline(pts, 1.6, col, 0.95, layer)
        if glow is not None:
            ctx.fx.polyline(pts, 1, glow, 0.9 * (1 - t * 0.6), layer)


def rays(ctx, x, y, t, col=(200, 255, 220), n=12, r0=8, r1=60, w=0.12, a=0.6, rot=0.0, layer='back', mode='over'):
    rng = np.random.default_rng(int(n * 31))
    for k in range(n):
        ang = rot + 2 * math.pi * k / n + (rng.random() - 0.5) * 0.15
        rr = r1 * (0.55 + 0.45 * rng.random()) * ease_out(clamp01(t))
        d = w * (0.6 + 0.8 * rng.random())
        p1 = (x + math.cos(ang - d) * r0, y + math.sin(ang - d) * r0)
        p2 = (x + math.cos(ang + d) * r0, y + math.sin(ang + d) * r0)
        p3 = (x + math.cos(ang) * (r0 + rr), y + math.sin(ang) * (r0 + rr))
        ctx.fx.poly([p1, p3, p2], col, a * (1 - 0.4 * t), layer, mode=mode)


def wisps(ctx, x, y, w, h, n, cols, t=None, seed=1, layer='front', a=0.9, rise=14, size=1):
    """particulas flotantes que suben; posicion dependiente del frame para dar movimiento."""
    rng = np.random.default_rng(seed)
    tt = (ctx.i / max(1, ctx.n)) if t is None else t
    for k in range(n):
        ph = rng.random()
        px = x + (rng.random() - 0.5) * w + math.sin((tt + ph) * 6.28 * 2) * 2
        life = (tt * 2 + ph) % 1.0
        py = y + (rng.random() - 0.5) * h - life * rise
        al = math.sin(life * math.pi) * a
        ctx.fx.dots([(px, py)], cols[k % len(cols)], al, layer, size)


def bolt(ctx, x0, y0, x1, y1, col=(210, 235, 255), w=2.0, seed=0, amp=5.0, n=9, glow=(90, 160, 255), layer='front', a=1.0, branch=True):
    rng = np.random.default_rng(seed)
    pts = [(x0, y0)]
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) + 1e-6
    nx, ny = -dy / L, dx / L
    for k in range(1, n):
        t = k / n
        o = (rng.random() - 0.5) * 2 * amp
        pts.append((x0 + dx * t + nx * o, y0 + dy * t + ny * o))
    pts.append((x1, y1))
    ctx.fx.polyline(pts, w + 3, glow, 0.35 * a, layer)
    ctx.fx.polyline(pts, w + 1, glow, 0.7 * a, layer)
    ctx.fx.polyline(pts, w, col, a, layer)
    ctx.fx.polyline(pts, max(1, w - 1), (255, 255, 255), a, layer)
    if branch:
        for k in (2, 5):
            if k < len(pts) - 1:
                bx, by = pts[k]
                ex = bx + (rng.random() - 0.3) * 14; ey = by + rng.random() * 10 + 4
                ctx.fx.polyline([(bx, by), ((bx + ex) / 2 + 2, (by + ey) / 2 - 1), (ex, ey)], 1, col, 0.8 * a, layer)


def pile(ctx, x, y, w, h, cols, n=26, seed=4, layer='back', alpha=1.0, outline=(10, 8, 16)):
    """monton de escombros/huesos en el suelo (poligonos con luz arriba-izquierda)."""
    rng = np.random.default_rng(seed)
    for k in range(n):
        px = x + (rng.random() - 0.5) * w
        prof = 1 - abs(px - x) / (w / 2 + 1e-6)
        py = y - rng.random() * h * prof * 0.9
        r = 1.2 + rng.random() * 2.6 * (0.5 + prof)
        ang = rng.random() * 6.28
        pts = [(px + math.cos(ang + j * 2.1) * r * (0.7 + 0.5 * rng.random()), py + math.sin(ang + j * 2.1) * r * 0.7) for j in range(3 + int(rng.random() * 2))]
        c = cols[int(rng.random() * len(cols))]
        ctx.fx.poly(pts, outline, alpha, layer)
        sh = [(a_ + 0.0, b_ + 0.0) for a_, b_ in pts]
        cx_ = sum(p[0] for p in pts) / len(pts); cy_ = sum(p[1] for p in pts) / len(pts)
        ins = [(cx_ + (a_ - cx_) * 0.62, cy_ + (b_ - cy_) * 0.62) for a_, b_ in pts]
        ctx.fx.poly(ins, c, alpha, layer)
        hi = [(a_ - 0.4, b_ - 0.5) for a_, b_ in ins[:2]]
        ctx.fx.dots(hi[:1], lerp(c, (255, 255, 255), 0.45), alpha, layer)


def flame_tuft(ctx, x, y, h, w, cols, phase=0.0, a=0.9, layer='front', mode='over'):
    """llama estilizada (gota) con 3 capas."""
    for j, c in enumerate(cols):
        k = 1 - j * 0.28
        sway = math.sin(phase * 6.28 + j) * 1.2
        pts = [(x - w * k, y), (x - w * k * 0.7, y - h * k * 0.45), (x + sway, y - h * k), (x + w * k * 0.7, y - h * k * 0.45), (x + w * k, y)]
        ctx.fx.poly(pts, c, a, layer, mode=mode, ss=2)


def glow_cols(base, k=1.0):
    return tuple(min(255, int(c * k)) for c in base)


def flash_tint(pose_key_amt):
    return pose_key_amt


def block(ctx, x0, y0, x1, y1, base, hi, lo, layer='front', seed=0, brick=(10, 6), a=1.0, outline=(10, 10, 16), cracks=3):
    """losa/bloque de piedra con luz arriba-izquierda, juntas y grietas."""
    f = ctx.fx
    f.poly([(x0 - 1, y0 - 1), (x1 + 1, y0 - 1), (x1 + 1, y1), (x0 - 1, y1)], outline, a, layer)
    f.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], base, a, layer)
    f.poly([(x0, y0), (x1, y0), (x1, y0 + 2), (x0, y0 + 2)], hi, a, layer)
    f.poly([(x0, y0), (x0 + 1.5, y0), (x0 + 1.5, y1), (x0, y1)], lerp(base, hi, 0.5), a, layer)
    f.poly([(x1 - 2, y0), (x1, y0), (x1, y1), (x1 - 2, y1)], lo, a, layer)
    f.poly([(x0, y1 - 3), (x1, y1 - 3), (x1, y1), (x0, y1)], lo, a, layer)
    rng = np.random.default_rng(seed)
    bw, bh = brick
    yy = y0 + bh
    j = 0
    while yy < y1 - 1:
        f.line((x0, yy), (x1, yy), 1, lerp(base, lo, 0.7), 0.9, layer)
        off = (j % 2) * bw / 2
        xx = x0 + off + bw
        while xx < x1 - 1:
            f.line((xx, yy - bh), (xx, yy), 1, lerp(base, lo, 0.7), 0.9, layer)
            xx += bw + rng.random() * 2
        yy += bh; j += 1
    for k in range(cracks):
        sx = x0 + rng.random() * (x1 - x0); sy = y0 + rng.random() * (y1 - y0)
        pts = [(sx, sy)]
        for s in range(4):
            sx += (rng.random() - 0.5) * 6; sy += rng.random() * 4
            pts.append((sx, min(sy, y1)))
        f.polyline(pts, 1, lo, 0.95, layer)


def tele(ctx, x, y, t, col=(255, 200, 120), r=14, n=8, seed=0, layer='front'):
    """telegrafo de ataque: halo que crece + lineas que convergen al punto (lectura clara del windup)."""
    fx = ctx.fx
    fx.glow(x, y, r * (0.5 + t), col, 0.25 + 0.55 * t)
    rng = np.random.default_rng(seed + ctx.i * 3)
    for k in range(n):
        ang = rng.random() * 6.283
        d0 = r * (2.2 - 1.6 * t) + rng.random() * 4
        d1 = d0 - 5 - 3 * t
        fx.line((x + math.cos(ang) * d0, y + math.sin(ang) * d0), (x + math.cos(ang) * d1, y + math.sin(ang) * d1), 1, (255, 255, 255), 0.5 + 0.4 * t, layer)
    if t > 0.7:
        fx.dots([(x, y)], (255, 255, 255), 1.0, layer, 2)


def impact_star(ctx, x, y, t, col=(255, 240, 200), r=16, n=8, layer='front'):
    fx = ctx.fx
    for k in range(n):
        ang = 6.283 * k / n + 0.2
        r0 = r * 0.25 * t; r1 = r * (0.5 + 0.5 * ease_out(t))
        fx.line((x + math.cos(ang) * r0, y + math.sin(ang) * r0), (x + math.cos(ang) * r1, y + math.sin(ang) * r1), 1 + (k % 2), col, 1 - t * 0.8, layer)
    fx.glow(x, y, r * 0.8, col, 0.9 * (1 - t))
