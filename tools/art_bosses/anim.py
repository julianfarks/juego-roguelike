"""Animacion por claves: K([(frame, {hueso: valor, 'hueso.x':.., }, 'ease'), ...]) -> funcion(frame)->pose."""
import math

EASE = {
    'lin': lambda t: t,
    'sm': lambda t: t * t * (3 - 2 * t),
    'in': lambda t: t ** 2.2,
    'in3': lambda t: t ** 3.2,
    'out': lambda t: 1 - (1 - t) ** 2.4,
    'snap': lambda t: 1 - (1 - t) ** 4.5,
    'back': lambda t: 1 + 2.2 * (t - 1) ** 3 + 1.2 * (t - 1) ** 2,
}


def lerpv(a, b, t):
    if isinstance(a, (tuple, list)):
        return tuple(lerpv(x, y, t) for x, y in zip(a, b))
    return a + (b - a) * t


def rest_of(name):
    if name == 'tint':
        return ((255, 255, 255), 0.0)
    if name == 'emit' or name.endswith('.e'):
        return 1.0
    return 1.0 if (name.endswith('.sx') or name.endswith('.sy') or name.endswith('.s')) else 0.0


def K(keys):
    tracks = {}
    for k in keys:
        f, d = k[0], k[1]
        e = k[2] if len(k) > 2 else 'sm'
        for name, v in d.items():
            tracks.setdefault(name, []).append((f, v, e))
    for name, tr in tracks.items():
        tr.sort(key=lambda x: x[0])
        if tr[0][0] > 0:
            tr.insert(0, (0, rest_of(name), 'sm'))

    def fn(f):
        pose = {}
        for name, tr in tracks.items():
            if f <= tr[0][0]:
                pose[name] = tr[0][1]; continue
            if f >= tr[-1][0]:
                pose[name] = tr[-1][1]; continue
            for j in range(1, len(tr)):
                if f <= tr[j][0]:
                    f0, v0, _ = tr[j - 1]; f1, v1, e = tr[j]
                    t = (f - f0) / max(1e-6, f1 - f0)
                    pose[name] = lerpv(v0, v1, EASE[e](t))
                    break
        return pose
    return fn


def merge(*poses):
    out = {}
    for p in poses:
        for k, v in p.items():
            if k.endswith('.sx') or k.endswith('.sy') or k.endswith('.s'):
                out[k] = out.get(k, 1.0) * v
            elif k in ('tint', 'clip') or k.startswith('dis') or k == 'fade' or k.endswith('.v') or k.endswith('.z') or k == 'lit' or k == 'emit' or k.endswith('.e'):
                out[k] = v
            else:
                out[k] = out.get(k, 0.0) + v
    return out


def layered(*fns):
    return lambda f: merge(*[fn(f) for fn in fns])


def S(f, n, ph=0.0, k=1):
    return math.sin(2 * math.pi * (k * f / n + ph))
