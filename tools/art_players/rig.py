"""Esqueleto 2D con cinematica directa/IK, interpolacion de poses y simulacion de cintas (capa, bufanda, pelo)."""
import math
from types import SimpleNamespace as NS

DEF = dict(hx=0.0, hy=0.0, lean=4.0, hd=0.0,
           afA=25.0, afE=0.8, abA=-18.0, abE=0.8, wa=60.0, wb=20.0,
           ffx=4.0, ffy=-1.2, bfx=-4.0, bfy=-1.2, ffa=0.0, bfa=0.0,
           rot=0.0, wx=0.0, wy=0.0, aura=0.0, burst=0.0, two=0.0, sq=0.0, ex=0.0)


def ease(name, t):
    if name == 'in':
        return t * t
    if name == 'in3':
        return t * t * t
    if name == 'out':
        return 1 - (1 - t) ** 2
    if name == 'io':
        return t * t * (3 - 2 * t)
    return t


class Seq:
    """Secuencia continua de poses a partir de claves (t, dict, ease_de_llegada)."""

    def __init__(self, base, keys):
        self.keys = []
        cur = dict(DEF)
        cur.update(base)
        bf = dict(cur)
        for k in keys:
            t, d = k[0], k[1]
            e = k[2] if len(k) > 2 else 'io'
            cur = dict(bf) if d.get('_base') else dict(cur)
            cur.update({a: b for a, b in d.items() if a != '_base'})
            self.keys.append((t, cur, e))
        self.keys.sort(key=lambda k: k[0])

    def at(self, t):
        ks = self.keys
        if t <= ks[0][0]:
            return NS(**ks[0][1])
        if t >= ks[-1][0]:
            return NS(**ks[-1][1])
        for i in range(len(ks) - 1):
            if ks[i][0] <= t <= ks[i + 1][0]:
                a, b = ks[i], ks[i + 1]
                u = (t - a[0]) / max(1e-6, b[0] - a[0])
                u = ease(b[2], u)
                return NS(**{k: a[1][k] + (b[1][k] - a[1][k]) * u for k in a[1]})
        return NS(**ks[-1][1])


# ------------------------------------------------------------------- geometry
def dirv(a):
    r = math.radians(a)
    return (math.sin(r), math.cos(r))


def add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def ln(a):
    return math.hypot(a[0], a[1])


def arm_ik(sh, tgt, L1, L2):
    d = sub(tgt, sh)
    r = max(0.4 * (L1 + L2), min(ln(d), (L1 + L2) * 0.995))
    ang = math.atan2(d[0], d[1])
    dv = (math.sin(ang), math.cos(ang))
    hand = add(sh, dv, r)
    a = (L1 * L1 - L2 * L2 + r * r) / (2 * r)
    h = math.sqrt(max(0.0, L1 * L1 - a * a))
    best = None
    for s in (1, -1):
        pv = (-dv[1] * s, dv[0] * s)
        e = (sh[0] + dv[0] * a + pv[0] * h, sh[1] + dv[1] * a + pv[1] * h)
        sc = e[1] - 0.5 * e[0]
        if best is None or sc > best[0]:
            best = (sc, e)
    return best[1], hand


def leg_ik(hip, tgt, L1, L2):
    d = sub(tgt, hip)
    r = max(1.0, min(ln(d), (L1 + L2) * 0.998))
    ang = math.atan2(d[0], d[1])
    dv = (math.sin(ang), math.cos(ang))
    ank = add(hip, dv, r)
    a = (L1 * L1 - L2 * L2 + r * r) / (2 * r)
    h = math.sqrt(max(0.0, L1 * L1 - a * a))
    best = None
    for s in (1, -1):
        pv = (-dv[1] * s, dv[0] * s)
        k = (hip[0] + dv[0] * a + pv[0] * h, hip[1] + dv[1] * a + pv[1] * h)
        if best is None or k[0] > best[0][0]:
            best = (k, 0)
    return best[0], ank


class Dims:
    def __init__(self, k=1.0, tl=9.0, hipy=13.2, thigh=7.0, shin=7.0, up=5.3, fore=5.3, hr=3.9, sw=1.0):
        self.k = k
        self.tl = tl * k
        self.hipy = hipy * k
        self.thigh = thigh * k
        self.shin = shin * k
        self.up = up * k
        self.fore = fore * k
        self.hr = hr * k
        self.sw = sw * k


def skeleton(p, D):
    sk = NS()
    hip = (p.hx, -D.hipy + p.hy)
    l = math.radians(p.lean)
    up = (math.sin(l), -math.cos(l))
    fw = (math.cos(l), math.sin(l))
    sk.hip, sk.up, sk.fw = hip, up, fw
    sk.T = lambda u, v: (hip[0] + fw[0] * u + up[0] * v, hip[1] + fw[1] * u + up[1] * v)
    sk.neck = sk.T(0.4 * D.k, D.tl)
    sk.shF = sk.T(0.9 * D.sw, D.tl - 0.8 * D.k)
    sk.shB = sk.T(-0.9 * D.sw, D.tl - 0.8 * D.k)
    ha = p.lean * 0.55 + p.hd
    sk.ha = ha
    hv = (math.sin(math.radians(ha)), -math.cos(math.radians(ha)))
    sk.hv = hv
    sk.hf = (math.cos(math.radians(ha)), math.sin(math.radians(ha)))
    sk.head = (sk.neck[0] + hv[0] * D.hr * 0.85, sk.neck[1] + hv[1] * D.hr * 0.85)
    # brazos
    tgtF = add(sk.shF, dirv(p.afA), (D.up + D.fore) * p.afE)
    sk.elbF, sk.handF = arm_ik(sk.shF, tgtF, D.up, D.fore)
    wv = dirv(p.wa)
    sk.wv = wv
    sk.wn = (wv[1], -wv[0])
    tgtB = add(sk.shB, dirv(p.abA), (D.up + D.fore) * p.abE)
    if p.two > 0:
        g = 4.8 * D.k
        t2 = add(sk.handF, wv, -g)
        tgtB = (tgtB[0] + (t2[0] - tgtB[0]) * p.two, tgtB[1] + (t2[1] - tgtB[1]) * p.two)
    sk.elbB, sk.handB = arm_ik(sk.shB, tgtB, D.up, D.fore)
    # piernas
    hipF = sk.T(0.5 * D.k, 0.6)
    hipB = sk.T(-0.5 * D.k, 0.6)
    sk.hipF, sk.hipB = hipF, hipB
    sk.kneeF, sk.ankF = leg_ik(hipF, (p.ffx, p.ffy), D.thigh, D.shin)
    sk.kneeB, sk.ankB = leg_ik(hipB, (p.bfx, p.bfy), D.thigh, D.shin)
    return sk


# ------------------------------------------------------------------- cintas
class Ribbon:
    def __init__(self, name, anchor, n, seg, widths, rest=(-0.3, 1.0), grav=0.07, damp=0.90, k=0.03, wscale=1.0,
                 flutter=0.0, phase=0.0):
        self.name, self.anchor, self.n, self.seg = name, anchor, n, seg
        self.widths = widths
        self.rest = rest
        self.grav, self.damp, self.k = grav, damp, k
        self.flutter, self.phase = flutter, phase


def simulate(ribbons, posef, sk_fn, n, fps_sub=5, loop=True, pre=12, wind_scale=1.0):
    """Devuelve para cada ribbon una lista (n frames) de listas de puntos."""
    if not ribbons:
        return {}
    state = {}
    out = {r.name: [] for r in ribbons}
    nrep = 3 if loop else 1
    t0 = 0.0
    # inicializa en reposo con la pose del frame 0
    p0 = posef(0.0)
    s0 = sk_fn(p0)
    for r in ribbons:
        a = r.anchor(s0)
        rv = r.rest
        l = math.hypot(*rv)
        rv = (rv[0] / l, rv[1] / l)
        pts = [(a[0] + rv[0] * r.seg * i, a[1] + rv[1] * r.seg * i) for i in range(r.n)]
        state[r.name] = (pts, [q for q in pts])
    steps_total = []
    if not loop:
        steps_total += [(0.0, 'pre')] * pre
    tick = 0
    for rep in range(nrep):
        for f in range(n):
            for s in range(fps_sub):
                t = f + s / fps_sub
                steps_total.append((t, 'rec' if (rep == nrep - 1 and s == 0) else 'run'))
    tick = 0
    for t, mode in steps_total:
        p = posef(t)
        sk = sk_fn(p)
        for r in ribbons:
            pts, prev = state[r.name]
            a = r.anchor(sk)
            rv = r.rest
            l = math.hypot(*rv)
            rv = (rv[0] / l, rv[1] / l)
            newp = [a]
            for i in range(1, r.n):
                x, y = pts[i]
                px, py = prev[i]
                vx, vy = (x - px) * r.damp, (y - py) * r.damp
                tx, ty = a[0] + rv[0] * r.seg * i, a[1] + rv[1] * r.seg * i
                fl = 0.0
                if r.flutter:
                    fl = r.flutter * math.sin(tick * 0.35 + r.phase + i * 0.9)
                ax = p.wx * 0.09 * wind_scale + (tx - x) * r.k
                ay = r.grav + p.wy * 0.09 * wind_scale + (ty - y) * r.k + fl * 0.05
                newp.append((x + vx + ax, y + vy + ay))
            for _ in range(4):
                newp[0] = a
                for i in range(1, r.n):
                    dx, dy = newp[i][0] - newp[i - 1][0], newp[i][1] - newp[i - 1][1]
                    d = math.hypot(dx, dy) or 1e-6
                    k = r.seg / d
                    newp[i] = (newp[i - 1][0] + dx * k, newp[i - 1][1] + dy * k)
            state[r.name] = (newp, pts)
            if mode == 'rec':
                out[r.name].append([tuple(q) for q in newp])
        tick += 1
    return out


def ribbon_poly(pts, widths):
    L_, R_ = [], []
    n = len(pts)
    for i, p in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        l = math.hypot(tx, ty) or 1
        nx, ny = -ty / l, tx / l
        w = widths[min(i, len(widths) - 1)]
        L_.append((p[0] + nx * w, p[1] + ny * w))
        R_.append((p[0] - nx * w, p[1] - ny * w))
    return L_ + R_[::-1]
