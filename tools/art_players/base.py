"""Clase base de personaje: animaciones, estelas, cajas de golpe."""
import math
from types import SimpleNamespace as NS
import numpy as np
from rig import Seq, Dims, skeleton, simulate, dirv, add
import anims as AN
from kit import hexc


class PClass:
    id = 'x'
    c1 = '#ffffff'
    c2 = '#ffffff'
    body = (12, 28)
    trail_span = (8, 20)       # (x interior, x exterior) a lo largo del arma para la estela
    trail_len = 1.25
    tcore = None
    trail_mode = 'blade'
    reach_pts = ((19, 0),)     # puntos del arma (marco arma) usados para calcular el box

    def __init__(self):
        self.D = Dims()
        self.carry = dict(afA=30, afE=0.85, abA=-18, abE=0.8, wa=60)
        self.ribbons = []
        self.attacks = {}      # nombre -> (keys, hit)
        self.over = {}         # nombre -> keys
        self.setup()
        self.rib_by_name = {r.name: r for r in self.ribbons}
        self.col1, self.col2 = hexc(self.c1), hexc(self.c2)
        self.core = hexc(self.tcore or self.c2)

    def setup(self):
        pass

    def init_mats(self):
        pass

    # ------------------------------------------------------------------ anim
    def keys(self, name):
        if name in self.over:
            return self.over[name]
        if name in self.attacks:
            return self.attacks[name][0]
        a = AN.build(self.carry)
        if name in a:
            return a[name]
        if name == 'skill':
            return AN.cast_keys(self.carry, self.skill_kind, AN.N['skill'], 3)
        if name == 'ult':
            return AN.cast_keys(self.carry, 'sky', AN.N['ult'], 5, big=True)
        raise KeyError(name)

    def seq(self, name):
        return Seq(self.carry_base(), self.keys(name))

    def carry_base(self):
        return {k: v for k, v in self.carry.items() if isinstance(v, (int, float))}

    skill_kind = "thrust"
    muzzle_x = 20

    # ------------------------------------------------------------------ arma
    def blade_pts(self, p, xs):
        """Puntos (mundo) a lo largo del eje del arma para xs=[(x,y),...]."""
        sk = skeleton(p, self.D)
        k = self.D.k
        h = sk.handF
        return [(h[0] + sk.wv[0] * x * k + sk.wn[0] * y * k, h[1] + sk.wv[1] * x * k + sk.wn[1] * y * k) for x, y in xs]

    def trail_draw(self, X, seq, i, hit):
        """Estela semitransparente en el fotograma i."""
        h0, h1 = hit
        if i < h0 or i > h1 + 1:
            return
        fade = 1.0 if i <= h1 else 0.5
        tl = self.trail_len
        ns = 14
        samples = []
        for s in range(ns + 1):
            tt = i - tl + tl * s / ns
            if tt < 0:
                continue
            pp = seq.at(tt)
            a, b = self.blade_pts(pp, [(self.trail_span[0], 0), (self.trail_span[1], 0)])
            samples.append((a, b))
        ov = X.of
        c1, c2 = self.col1, self.core
        m = len(samples)

        def lp(a, b, t):
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        for j in range(m - 1):
            f = (j + 1) / (m - 1)
            a0, b0 = samples[j]
            a1, b1 = samples[j + 1]
            for (t0, col, al) in ((0.0, c1, 0.20 * f), (0.45, c1, 0.30 * f ** 1.2), (0.78, c2, 0.75 * f ** 1.8)):
                ov.poly([lp(a0, b0, t0), b0, b1, lp(a1, b1, t0)], col, al * fade)
        a, b = samples[-1]
        ov.line(lp(a, b, 0.55), b, c2, 0.9 * fade, width=0.8)

    reach_rng = (26, 32)

    def box_for(self, seq, hit, n, name='attack1'):
        h0, h1 = hit
        xs, ys = [], []
        t = h0 - 0.5
        while t <= h1 + 0.51:
            pp = seq.at(max(0, t))
            pts = self.blade_pts(pp, list(self.reach_pts))
            for q in pts:
                xs.append(q[0])
                ys.append(q[1])
            t += 0.25
        comp = max(xs)
        fr = dict(attack1=0.3, attack2=0.5, attack3=1.0, airatk=0.4).get(name, 0.5)
        x1 = min(comp, self.reach_rng[0] + (self.reach_rng[1] - self.reach_rng[0]) * fr)
        x0 = 3
        y0 = max(-32, min(ys) - 1)
        y1 = min(0, max(ys) + 1)
        if y1 - y0 < 8:
            y0 = max(-32, y1 - 8)
        return [int(round(x0)), int(round(y0)), int(round(x1 - x0)), int(round(y1 - y0))], x1

    def fx(self, X, name, i, n):
        pass


def aura_fx(cls, X, name, i, n):
    """Aura/explosion generica para skill/ult segun p.aura / p.burst."""
    p = X.p
    ov_b, ov_f = X.ob, X.of
    c1, c2 = cls.col1, cls.core
    a, b = p.aura, p.burst
    if a <= 0.02 and b <= 0.02:
        return
    cx, cy = p.hx + 0.5, -15 + p.hy * 0.3
    ov_b.glow((cx, cy), 9 + 9 * a, 13 + 11 * a, c1, 0.55 * min(1, a * 1.1), power=1.6)
    ov_b.glow((cx, cy), 5 + 4 * a, 9 + 6 * a, c2, 0.35 * a, power=1.4)
    # chispas ascendentes
    for j in range(7):
        ph = (i * 0.37 + j * 0.61) % 1.0
        x = cx + math.sin(j * 2.3 + i) * (6 + 5 * a)
        y = cy + 14 - ph * (30 + 8 * a)
        ov_f.dot((x, y), c2, 0.85 * a * (1 - ph) + 0.1, r=0.55)
    if b > 0.05:
        r = 6 + 20 * (1 - b * 0.6) if False else 6 + 22 * b
        pts = [(cx + math.cos(t / 20 * 2 * math.pi) * r, cy + 4 + math.sin(t / 20 * 2 * math.pi) * r * 0.45) for t in range(21)]
        for q in range(20):
            ov_f.line(pts[q], pts[q + 1], c2, 0.8 * b, width=1.0)
        ov_f.glow((cx, cy), r * 0.9, r * 0.5, c1, 0.25 * b, power=1.2)


PClass.fx_default = aura_fx
