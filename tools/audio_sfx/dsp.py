"""Primitivas DSP para sintesis de SFX (numpy/scipy). Todo mono, 44.1 kHz."""
import numpy as np
from scipy import signal
from scipy.signal import fftconvolve, lfilter, sosfilt

SR = 44100


def N(d):
    return max(1, int(round(d * SR)))


def T(d):
    return np.arange(N(d)) / SR


def arr(v, n):
    if np.isscalar(v):
        return np.full(n, float(v))
    v = np.asarray(v, float)
    if len(v) == n:
        return v
    return np.interp(np.linspace(0, len(v) - 1, n), np.arange(len(v)), v)


def db(x):
    return 10 ** (x / 20.0)


# ------------------------------------------------------------------ envelopes
def curve(dur, pts, log=False, smooth=0.0):
    """Curva lineal (o logaritmica) por puntos (t_seg, valor)."""
    n = N(dur)
    t = np.arange(n) / SR
    xs = [p[0] for p in pts]
    ys = np.array([p[1] for p in pts], float)
    if log:
        y = np.exp(np.interp(t, xs, np.log(np.maximum(ys, 1e-6))))
    else:
        y = np.interp(t, xs, ys)
    if smooth > 0:
        k = max(1, int(smooth * SR))
        y = np.convolve(np.pad(y, (k, k), mode='edge'), np.ones(k) / k, mode='same')[k:-k]
    return y


def expdec(dur, tau, a=0.002, n=None):
    n = n or N(dur)
    t = np.arange(n) / SR
    e = np.exp(-t / tau)
    an = max(1, int(a * SR))
    an = min(an, n)
    e[:an] *= 0.5 - 0.5 * np.cos(np.pi * np.arange(an) / an)
    return e


def bump(dur, pk=0.4, p=1.5, n=None):
    """Sube hasta pk (fraccion) y baja a 0, suave en ambos extremos."""
    n = n or N(dur)
    x = np.arange(n) / max(1, n - 1)
    up = np.sin(0.5 * np.pi * np.clip(x / pk, 0, 1)) ** p
    dn = np.cos(0.5 * np.pi * np.clip((x - pk) / (1 - pk), 0, 1)) ** p
    return np.where(x < pk, up, dn)


def swell(dur, a, r, n=None):
    """Hann: ataque a, sostenido, relajacion r (seg)."""
    n = n or N(dur)
    e = np.ones(n)
    an = min(int(a * SR), n // 2)
    rn = min(int(r * SR), n // 2)
    if an > 0:
        e[:an] = 0.5 - 0.5 * np.cos(np.pi * np.arange(an) / an)
    if rn > 0:
        e[n - rn:] = 0.5 + 0.5 * np.cos(np.pi * np.arange(rn) / rn)
    return e


def adsr(dur, a, d, s, r):
    n = N(dur)
    t = np.arange(n) / SR
    e = np.interp(t, [0, a, a + d, max(a + d, dur - r), dur], [0, 1, s, s, 0])
    return e


# ------------------------------------------------------------------ oscillators
def _blep(t, dt):
    out = np.zeros_like(t)
    m = t < dt
    x = t[m] / dt[m]
    out[m] = 2 * x - x * x - 1
    m = t > 1 - dt
    x = (t[m] - 1) / dt[m]
    out[m] = x * x + 2 * x + 1
    return out


def sine(f, n, ph0=0.0):
    f = arr(f, n)
    return np.sin(2 * np.pi * (np.cumsum(f) / SR + ph0))


def saw(f, n, ph0=0.0):
    f = arr(f, n)
    ph = (np.cumsum(f) / SR + ph0) % 1.0
    dt = np.clip(f / SR, 1e-5, 0.45)
    return 2 * ph - 1 - _blep(ph, dt)


def square(f, n, pw=0.5, ph0=0.0):
    f = arr(f, n)
    ph = (np.cumsum(f) / SR + ph0) % 1.0
    dt = np.clip(f / SR, 1e-5, 0.45)
    y = np.where(ph < pw, 1.0, -1.0)
    y += _blep(ph, dt)
    y -= _blep((ph - pw) % 1.0, dt)
    return y


def tri(f, n, ph0=0.0):
    f = arr(f, n)
    ph = np.cumsum(f) / SR + ph0
    return 2 / np.pi * np.arcsin(np.sin(2 * np.pi * ph))


def fm(fc, ratio, idx, n, fb=0.0):
    fc = arr(fc, n)
    idx = arr(idx, n)
    mod = np.sin(2 * np.pi * np.cumsum(fc * ratio) / SR)
    return np.sin(2 * np.pi * np.cumsum(fc) / SR + idx * mod)


def noise(n, r, color='white'):
    w = r.standard_normal(n)
    if color == 'white':
        return w
    if color == 'pink':
        b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
        a = [1, -2.494956002, 2.017265875, -0.522189400]
        y = lfilter(b, a, w)
        return y / (y.std() + 1e-9)
    if color == 'brown':
        y = np.cumsum(w)
        y = hp(y, 25, 1)
        return y / (y.std() + 1e-9)
    raise ValueError(color)


# ------------------------------------------------------------------ filters
def _fc(f):
    return float(np.clip(f, 20, 0.45 * SR))


def lp(x, fc, order=2):
    return sosfilt(signal.butter(order, _fc(fc), 'lowpass', fs=SR, output='sos'), x)


def hp(x, fc, order=2):
    return sosfilt(signal.butter(order, _fc(fc), 'highpass', fs=SR, output='sos'), x)


def bp(x, lo, hi, order=2):
    lo, hi = _fc(lo), _fc(hi)
    if hi <= lo * 1.02:
        hi = lo * 1.02
    return sosfilt(signal.butter(order, [lo, hi], 'bandpass', fs=SR, output='sos'), x)


def reson(x, fc, q):
    fc = _fc(fc)
    b, a = signal.iirpeak(fc / (SR / 2), max(q, 0.3))
    return sosfilt(signal.tf2sos(b, a), x)


def _filt(x, kind, f, q, order):
    if kind == 'lp':
        return lp(x, f, order)
    if kind == 'hp':
        return hp(x, f, order)
    return reson(x, f, q)


def sweep(x, fc, kind='lp', q=1.5, order=2):
    """Filtro con frecuencia variable: banco de filtros fijos interpolado (sin zipper)."""
    n = len(x)
    fc = np.clip(arr(fc, n), 30, 0.45 * SR)
    lo, hi = fc.min(), fc.max()
    if hi / lo < 1.04:
        return _filt(x, kind, float(fc.mean()), q, order)
    nb = int(np.clip(np.log2(hi / lo) * 5 + 2, 4, 30))
    freqs = np.geomspace(lo, hi, nb)
    outs = np.stack([_filt(x, kind, f, q, order) for f in freqs])
    pos = (np.log(fc) - np.log(lo)) / (np.log(hi) - np.log(lo)) * (nb - 1)
    i0 = np.clip(np.floor(pos).astype(int), 0, nb - 2)
    fr = pos - i0
    ar = np.arange(n)
    return outs[i0, ar] * (1 - fr) + outs[i0 + 1, ar] * fr


VOWELS = {
    'a': [(800, 80, 1.0), (1150, 90, .5), (2900, 120, .2), (3900, 130, .1)],
    'o': [(450, 70, 1.0), (800, 80, .4), (2830, 120, .1), (3800, 130, .05)],
    'u': [(325, 60, 1.0), (700, 70, .25), (2530, 120, .05), (3500, 130, .03)],
    'e': [(400, 70, 1.0), (2000, 100, .35), (2550, 120, .2), (3500, 130, .1)],
    'i': [(270, 60, 1.0), (2150, 100, .3), (2950, 120, .2), (3900, 130, .1)],
    'ae': [(660, 80, 1.0), (1700, 100, .4), (2400, 120, .2), (3500, 130, .1)],
}


def formant(x, vowel='a', scale=1.0):
    out = np.zeros(len(x))
    for f, bw, a in VOWELS[vowel]:
        out += a * reson(x, f * scale, f * scale / bw)
    return out


def formant_morph(x, v0, v1, m, scale=1.0):
    """m: curva 0..1 de v0 a v1 (array o escalar)."""
    if v0 == v1:
        return formant(x, v0, scale)
    a = formant(x, v0, scale)
    b = formant(x, v1, scale)
    m = arr(m, len(x))
    return a * (1 - m) + b * m


# ------------------------------------------------------------------ distorsion
def sat(x, drive=2.0):
    return np.tanh(x * drive) / np.tanh(drive)


def fold(x, amt=2.0):
    return np.sin(np.pi / 2 * np.clip(x, -1, 1) * amt)


def crush(x, bits=8, ds=1):
    q = 2 ** (bits - 1)
    y = np.round(x * q) / q
    if ds > 1:
        y = np.repeat(y[::ds], ds)[:len(x)]
    return y


def norm(x, peak=1.0):
    m = np.max(np.abs(x)) + 1e-12
    return x / m * peak


# ------------------------------------------------------------------ tiempo / espacio
_IR = {}


def _ir(rt, damp, seed):
    key = (round(rt, 2), int(damp), seed)
    if key in _IR:
        return _IR[key]
    r = np.random.default_rng(seed + 7919)
    n = N(rt)
    t = np.arange(n) / SR
    w = r.standard_normal(n)
    lo, hi = lp(w, damp), hp(w, damp)
    ir = lo * np.exp(-6.91 * t / rt) + 0.6 * hi * np.exp(-6.91 * t / (rt * 0.35))
    ir *= np.minimum(1.0, t / 0.006)
    s = ir[:int(0.2 * SR)].std() + 1e-9
    for _ in range(10):
        i = int(r.uniform(0.004, 0.06) * SR)
        if i < n:
            ir[i] += r.choice([-1, 1]) * r.uniform(1.5, 4) * s
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-12
    _IR[key] = ir
    return ir


def reverb(x, rt=1.0, wet=0.3, damp=5000, pre=0.0, seed=1, dry=1.0):
    ir = _ir(rt, damp, seed)
    p = N(pre) if pre > 0 else 0
    w = fftconvolve(x, ir)
    n = max(len(x), len(w) + p)
    out = np.zeros(n)
    out[:len(x)] += dry * x
    out[p:p + len(w)] += wet * w * 3.0
    return out


def echo(x, delay, fb=0.4, taps=4, damp=6000):
    out = np.zeros(len(x) + int(delay * SR * taps) + 1)
    out[:len(x)] += x
    cur = x
    for k in range(1, taps + 1):
        cur = lp(cur, damp, 1) * fb
        o = int(delay * SR * k)
        out[o:o + len(cur)] += cur
    return out


def varispeed(x, ratio):
    pos = np.cumsum(arr(ratio, len(ratio) if not np.isscalar(ratio) else len(x)))
    pos = pos[pos < len(x) - 1]
    return np.interp(pos, np.arange(len(x)), x)


def pitch(x, semis):
    r = 2 ** (semis / 12.0)
    pos = np.arange(0, len(x) - 1, r)
    return np.interp(pos, np.arange(len(x)), x)


def reverse(x):
    return x[::-1].copy()


class Mix:
    def __init__(self):
        self.p = []

    def add(self, x, t=0.0, g=1.0):
        x = np.array(x, float) * g
        k = min(int(0.010 * SR), len(x) // 4)   # fundido de cola: evita escalones al cortar capas
        if k > 1:
            x[-k:] *= 0.5 + 0.5 * np.cos(np.pi * np.arange(k) / k)
        self.p.append((max(0, int(round(t * SR))), x))
        return self

    def render(self, length=None):
        n = max(o + len(x) for o, x in self.p) if length is None else N(length)
        out = np.zeros(n)
        for o, x in self.p:
            e = min(n, o + len(x))
            if e > o:
                out[o:e] += x[:e - o]
        return out


def fit(x, n):
    if len(x) >= n:
        return x[:n]
    return np.pad(x, (0, n - len(x)))


def fadeio(x, fi=0.002, fo=0.004):
    x = x.copy()
    a, b = min(int(fi * SR), len(x) // 2), min(int(fo * SR), len(x) // 2)
    if a:
        x[:a] *= 0.5 - 0.5 * np.cos(np.pi * np.arange(a) / a)
    if b:
        x[-b:] *= 0.5 + 0.5 * np.cos(np.pi * np.arange(b) / b)
    return x
