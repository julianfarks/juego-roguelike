"""Helpers de formas reutilizables."""
import math
import numpy as np
from kit import catmull, bez


def rag(x_from, x_to, y, n, amp, seed=0, slope=0.0, pointy=True):
    """Borde inferior desgarrado de x_from a x_to (zigzag irregular)."""
    rng = np.random.default_rng(seed)
    pts = []
    for k in range(n * 2 + 1):
        t = k / (n * 2)
        x = x_from + (x_to - x_from) * t
        yy = y + slope * t
        if k % 2 == 1:
            yy += amp * (0.45 + 0.55 * rng.random())
        else:
            yy += amp * 0.12 * rng.random()
        pts.append((x, yy))
    return pts


def spikes(cx, cy, r, n, h0, h1, a0=0, a1=360, seed=0, w=0.35):
    """Pinchos radiales alrededor de un punto: lista de triangulos."""
    rng = np.random.default_rng(seed)
    out = []
    for k in range(n):
        a = math.radians(a0 + (a1 - a0) * (k + 0.5) / n)
        h = h0 + (h1 - h0) * rng.random()
        da = w / max(r, 1) * 1.0
        p1 = (cx + math.cos(a - da) * r, cy + math.sin(a - da) * r)
        p2 = (cx + math.cos(a + da) * r, cy + math.sin(a + da) * r)
        p3 = (cx + math.cos(a) * (r + h), cy + math.sin(a) * (r + h))
        out.append([p1, p3, p2])
    return out


def mirror_x(pts):
    return [(-x, y) for x, y in pts][::-1]


def blob(cx, cy, rx, ry, n=10, jit=0.2, seed=0):
    rng = np.random.default_rng(seed)
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        r = 1 + (rng.random() - 0.5) * 2 * jit
        pts.append((cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r))
    return pts


def jag_line(p0, p1, n=6, amp=2.0, seed=0):
    rng = np.random.default_rng(seed)
    p0 = np.array(p0, float); p1 = np.array(p1, float)
    d = p1 - p0; L = np.hypot(*d) + 1e-6
    nx, ny = -d[1] / L, d[0] / L
    pts = [tuple(p0)]
    for k in range(1, n):
        t = k / n
        o = (rng.random() - 0.5) * 2 * amp
        pts.append((p0[0] + d[0] * t + nx * o, p0[1] + d[1] * t + ny * o))
    pts.append(tuple(p1))
    return pts
