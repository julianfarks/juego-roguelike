import math
from px import *

OUT = '/home/claude/juego-roguelike/Shared/assets/sprites'
PREV = '/home/claude/juego-roguelike/tools/previews/art_enemies'

WHITE = (255, 255, 255)


def bone(c, p0, p1, r, mat, knob=1.25):
    with c.part(mat, bevel=1.0) as p:
        p.limb(p0, p1, r * 0.8, r * 0.8)
        p.ell(p0[0], p0[1], r * knob)
        p.ell(p1[0], p1[1], r * knob)


def leg(c, hip, foot, l1, l2, r0, r1, mat, bend=-1, footmat=None, footlen=3.0, footh=1.8, line=0.5):
    knee = ik2(hip, foot, l1, l2, bend)
    with c.part(mat, line=line, bevel=1.3) as p:
        p.limb(hip, knee, r0, r0 * 0.9)
        p.limb(knee, foot, r0 * 0.9, r1)
    fm = footmat or mat
    with c.part(fm, line=line, bevel=1.0) as p:
        p.poly([(foot[0] - 1.4, foot[1] - footh), (foot[0] + footlen * 0.45, foot[1] - footh * 0.9),
                (foot[0] + footlen, foot[1] + 0.3), (foot[0] - 1.4, foot[1] + 0.3)])
    return knee


def arc_trail(c, cx, cy, r0, r1, a0, a1, mat, fade_pow=0.8, steps=18):
    """Estela en media luna. Angulos en rad (y hacia abajo). El extremo a1 es la punta brillante."""
    pts_o, pts_i = [], []
    for k in range(steps + 1):
        a = a0 + (a1 - a0) * k / steps
        w = k / steps
        pts_o.append((cx + math.cos(a) * r1, cy + math.sin(a) * r1))
        ri = r0 + (r1 - r0) * (1 - w) * 0.55
        pts_i.append((cx + math.cos(a) * ri, cy + math.sin(a) * ri))
    da = a1 - a0

    def fade(lx, ly):
        ang = np.arctan2(ly - cy, lx - cx)
        if da > 0:
            u = ((ang - a0) % (2 * math.pi)) / da
        else:
            u = ((a0 - ang) % (2 * math.pi)) / (-da)
        return np.where(u > 1.0, 0.0, np.clip(u, 0, 1) ** fade_pow * 1.15)
    with c.part(mat, fade=fade, bevel=1.6) as p:
        p.poly(pts_o + pts_i[::-1])


def hurt_state(i):
    return [(-3.0, -0.30, 0.45), (-1.5, -0.14, 0.12)][min(i, 1)]


def draw_bits(c, bits, u):
    for (d, x, y, a) in bits.state(u):
        with c.at(x, y, a):
            d['fn'](c)
