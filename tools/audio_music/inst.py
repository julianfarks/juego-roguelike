"""inst.py - instrumentos sinteticos y percusion. Todo devuelve (n,2) float64."""
import numpy as np
from scipy import signal
from dsp import *


def _rng(seed):
    return np.random.default_rng(int(seed) & 0x7FFFFFFF)


def _mono2st(y, p=0.0):
    return pan2(y, p)


def _n(dur, rel):
    return int((dur + rel) * SR) + 1


def _rms_norm(y, target, lo, hi):
    seg = y[lo:hi] if hi - lo > 2000 else y
    r = np.sqrt((seg ** 2).mean()) + 1e-9
    return y * (target / r)


def _vibrato(t, rate, depth, delay, ph, ramp=0.5):
    on = np.clip((t - delay) / ramp, 0, 1)
    return 1.0 + depth * on * np.sin(2 * np.pi * rate * t + ph)


# ======================================================== cuerdas / vientos
def strings(f, dur, vel=0.8, seed=0, att=0.35, rel=0.5, bright=1.0, voices=4, spread=0.7,
            vib=0.0035, noise=0.015, cut=None, lowwarm=0.0):
    n = _n(dur, rel)
    t = tarr(n)
    rng = _rng(seed)
    out = np.zeros((n, 2))
    for i in range(voices):
        cents = (i / max(voices - 1, 1) - 0.5) * 20 + rng.uniform(-2, 2)
        fr = f * 2 ** (cents / 1200) * _vibrato(t, rng.uniform(4.6, 5.8), vib, 0.3, rng.uniform(0, 6.28), 0.6)
        s = osc("saw", fr, n, rng.random())
        p = spread * (2 * i / max(voices - 1, 1) - 1) if voices > 1 else 0
        out += pan2(s, p) / np.sqrt(voices)
    c = cut if cut else min(f * 4.5 * bright + 900 * bright, 8000)
    out = lp(out, c)
    out = out + lp(out, 400) * lowwarm
    if noise:
        nz = bp(rng.standard_normal(n), 2500, 7000) * noise
        out += pan2(nz, 0.0)
    e = adsr(n, dur, att, 0.15, 0.9, rel, 1.4)
    return out * e[:, None] * vel * 0.42


def violin(f, dur, vel=0.8, seed=0, att=0.07, rel=0.22, rate=5.7, depth=0.008, delay=0.25,
           bright=1.0, bow=0.025, slide=0.0, pan=0.0):
    n = _n(dur, rel)
    t = tarr(n)
    rng = _rng(seed)
    g = 2 ** (-slide * np.exp(-t / 0.07) / 12.0) if slide else 1.0
    base = f * g * _vibrato(t, rate * rng.uniform(0.97, 1.03), depth, delay, rng.uniform(0, 6.28), 0.5)
    y = osc("saw", base * 2 ** (-3 / 1200), n, rng.random()) + osc("saw", base * 2 ** (3 / 1200), n, rng.random())
    y *= 0.5
    y = lp(y, min(f * 6.5 * bright + 800, 9500))
    y = y + 0.45 * bpq(y, 520, 3.0) + 0.35 * bpq(y, 1500, 3.0)
    y = y + bp(rng.standard_normal(n), 2500, 6500) * bow * np.minimum(1, t / 0.05)
    sw = 1.0 + 0.12 * np.sin(2 * np.pi * t / max(dur, 0.8) * 0.5)
    e = adsr(n, dur, att, 0.1, 0.9, rel, 1.3) * sw
    return pan2(y * e * vel * 0.42, pan)


def flute(f, dur, vel=0.8, seed=0, att=0.07, rel=0.18, breath=0.18, vib=0.006, pan=0.0):
    n = _n(dur, rel)
    t = tarr(n)
    rng = _rng(seed)
    fr = f * _vibrato(t, 5.0, vib, 0.2, rng.uniform(0, 6), 0.4)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    y = np.sin(ph) + 0.28 * np.sin(2 * ph) + 0.1 * np.sin(3 * ph) + 0.04 * np.sin(4 * ph)
    nz = bpq(rng.standard_normal(n), min(f * 2.5, 9000), 1.5) * breath * (0.6 + 0.4 * np.minimum(1, t / 0.1))
    e = adsr(n, dur, att, 0.1, 0.85, rel, 1.2)
    chiff = bp(rng.standard_normal(n), 1500, 5000) * np.exp(-t / 0.04) * 0.25
    return pan2((y * 0.5 + nz + chiff) * e * vel * 0.55, pan)


def panflute(f, dur, vel=0.8, seed=0, att=0.06, rel=0.2, pan=0.0):
    n = _n(dur, rel)
    t = tarr(n)
    rng = _rng(seed)
    nz = bpq(rng.standard_normal(n), f, 28.0, 2)
    nz = nz / (np.abs(nz).max() + 1e-9)
    y = 0.8 * nz + 0.55 * np.sin(2 * np.pi * f * t * _vibrato(t, 4.8, 0.004, 0.3, 0, 0.4))
    y += 0.12 * bp(rng.standard_normal(n), 1500, 6000) * np.minimum(1, t / 0.08)
    e = adsr(n, dur, att, 0.1, 0.8, rel, 1.2)
    return pan2(y * e * vel * 0.5, pan)


def brass(f, dur, vel=0.8, seed=0, att=0.08, rel=0.25, bright=1.0, vib=0.0035, voices=3,
          blat=1.0, sub=0.0, spread=0.35, grit=0.0):
    n = _n(dur, rel)
    t = tarr(n)
    rng = _rng(seed)
    sig = np.zeros((n, 2))
    for i in range(voices):
        cents = (i - (voices - 1) / 2) * 8 + rng.uniform(-1.5, 1.5)
        fr = f * 2 ** (cents / 1200) * _vibrato(t, rng.uniform(5.0, 5.8), vib, 0.4, rng.uniform(0, 6), 0.5)
        s = osc("saw", fr, n, rng.random())
        p = spread * (2 * i / max(voices - 1, 1) - 1) if voices > 1 else 0
        sig += pan2(s, p) / np.sqrt(voices)
    if grit:
        sig = np.tanh(sig * (1 + grit * 4)) / (1 + grit * 1.5)
    lo = lp(sig, f * 2.0 + 250)
    hi = lp(sig, min(f * 9 * bright + 1500, 12000))
    w = np.interp(t, [0, att * 1.2, att * 3.5, att * 8, dur + rel + 1], [0, 1.0, 0.55, 0.5, 0.3]) * blat + (1 - blat) * 0.55
    y = lo * (1 - w)[:, None] + hi * w[:, None]
    if sub:
        y += pan2(np.sin(2 * np.pi * f * 0.5 * t), 0) * sub
    y += pan2(bp(rng.standard_normal(n), 1000, 4500) * np.exp(-t / 0.06) * 0.06, 0)
    e = adsr(n, dur, att, 0.12, 0.92, rel, 1.2)
    return y * e[:, None] * vel * 0.4


def organ(f, dur, vel=0.8, seed=0, draw=None, att=0.03, rel=0.22, trem=0.05, chiff=0.15, wide=0.5):
    n = _n(dur, rel)
    t = tarr(n)
    rng = _rng(seed)
    if draw is None:
        draw = {0.5: 0.6, 1: 1.0, 2: 0.7, 3: 0.45, 4: 0.4, 6: 0.18, 8: 0.15}
    L = np.zeros(n)
    R = np.zeros(n)
    th = 2 * np.pi * f * t
    for i, (r, w) in enumerate(draw.items()):
        if f * r > 17000:
            continue
        s = np.sin(r * th + i * 0.7)
        L += s * w
        R += s * w * (1 if i % 2 == 0 else 0.85)
    tl = 1 + trem * np.sin(2 * np.pi * 5.4 * t)
    tr = 1 + trem * np.sin(2 * np.pi * 5.4 * t + 1.6)
    norm = sum(draw.values())
    out = np.stack([L * tl, R * tr], 1) / norm
    if chiff:
        c = bpq(rng.standard_normal(n), min(f * 3, 8000), 2.0) * np.exp(-t / 0.03) * chiff
        out += pan2(c, 0)
    out = lp(out, 7500)
    e = adsr(n, dur, att, 0.05, 0.95, rel, 1.0)
    return out * e[:, None] * vel * 0.6


VOW = {
    "a": [(800, 1.0, 90), (1150, 0.55, 100), (2900, 0.16, 140), (3900, 0.07, 160)],
    "o": [(450, 1.0, 70), (800, 0.6, 90), (2830, 0.1, 120), (3800, 0.05, 140)],
    "u": [(325, 1.0, 60), (700, 0.5, 80), (2700, 0.15, 120), (3800, 0.08, 140)],
    "e": [(400, 1.0, 70), (2200, 0.5, 120), (2800, 0.16, 140), (3600, 0.06, 150)],
    "i": [(270, 1.0, 60), (2300, 0.5, 120), (3000, 0.2, 140), (3800, 0.06, 150)],
}


def _formants(src, vowel, fscale):
    out = np.zeros_like(src)
    for fc, a, bw in VOW[vowel]:
        fc2 = fc * fscale
        out += a * bpq(src, fc2, max(fc2 / bw, 1.5), 2)
    out += 0.12 * lp(src, 600, 2)
    return out


def choir(f, dur, vel=0.8, seed=0, vowel="a", vowel2=None, voices=3, att=0.45, rel=0.8,
          spread=0.8, vib=0.006, breath=0.06, shout=0.0):
    n = _n(dur, rel)
    t = tarr(n)
    rng = _rng(seed)
    src = np.zeros((n, 2))
    for i in range(voices):
        cents = rng.uniform(-14, 14)
        fr = f * 2 ** (cents / 1200) * _vibrato(t, rng.uniform(4.8, 6.2), vib, 0.35, rng.uniform(0, 6.28), 0.6)
        fr = fr * (1 + smooth_noise(n, rng, 3.0) * 0.003)
        s = osc("saw", fr, n, rng.random())
        p = spread * (2 * i / max(voices - 1, 1) - 1) if voices > 1 else 0
        src += pan2(s, p) / np.sqrt(voices)
    if breath:
        src += pan2(rng.standard_normal(n) * breath, 0)
    if shout:
        src = np.tanh(src * (1 + shout * 3))
    F1 = VOW[vowel][0][0]
    fs = max(1.0, 1.15 * f / F1)
    y = _formants(src, vowel, fs)
    if vowel2:
        fs2 = max(1.0, 1.15 * f / VOW[vowel2][0][0])
        y2 = _formants(src, vowel2, fs2)
        m = np.clip((t - dur * 0.35) / max(dur * 0.4, 0.1), 0, 1)[:, None]
        y = y * (1 - m) + y2 * m
    y = _rms_norm(y, 0.2, int(att * 1.5 * SR), max(int(dur * SR), int(att * 1.5 * SR) + 3000))
    e = adsr(n, dur, att, 0.2, 0.92, rel, 1.5)
    return y * e[:, None] * vel * 0.9


def sub(f, dur, vel=0.8, seed=0, att=0.02, rel=0.2, harm=0.25, drop=0.0):
    n = _n(dur, rel)
    t = tarr(n)
    fr = f * (1 + drop * np.exp(-t / 0.05))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    y = np.sin(ph) + harm * np.sin(2 * ph)
    y = np.tanh(y * 1.4)
    e = adsr(n, dur, att, 0.1, 0.9, rel)
    return pan2(y * e * vel * 0.6, 0)


def fm_pad(f, dur, vel=0.7, seed=0, ratio=1.4142, idx=2.0, lfo=0.35, att=1.5, rel=2.0, detune=4.0):
    n = _n(dur, rel)
    t = tarr(n)
    rng = _rng(seed)
    out = np.zeros((n, 2))
    for ch, sgn in enumerate((-1, 1)):
        fc = f * 2 ** (sgn * detune / 1200)
        ix = idx * (1 + lfo * np.sin(2 * np.pi * rng.uniform(0.08, 0.3) * t + rng.uniform(0, 6)))
        ix = ix * np.minimum(1, 0.3 + t / max(att, 0.1))
        mod = np.sin(2 * np.pi * fc * ratio * t + rng.uniform(0, 6))
        out[:, ch] = np.sin(2 * np.pi * fc * t + ix * mod) + 0.3 * np.sin(4 * np.pi * fc * t + 0.5 * ix * mod)
    out = lp(out, 5000)
    e = adsr(n, dur, att, 0.5, 0.9, rel, 1.5)
    return out * e[:, None] * vel * 0.35


def saw_pad(f, dur, vel=0.7, seed=0, att=1.0, rel=1.2, cut=2000, voices=4, spread=0.9, mod=0.0):
    n = _n(dur, rel)
    t = tarr(n)
    rng = _rng(seed)
    out = np.zeros((n, 2))
    for i in range(voices):
        cents = (i / max(voices - 1, 1) - 0.5) * 22
        s = osc("saw", f * 2 ** (cents / 1200), n, rng.random())
        out += pan2(s, spread * (2 * i / max(voices - 1, 1) - 1)) / np.sqrt(voices)
    a = lp(out, cut)
    if mod:
        b = lp(out, cut * 2.5)
        m = (0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(0.05, 0.15) * t + rng.uniform(0, 6)))[:, None] * mod
        a = a * (1 - m) + b * m
    e = adsr(n, dur, att, 0.4, 0.9, rel, 1.4)
    return a * e[:, None] * vel * 0.4


# ======================================================== percutidos tonales
def pluck(f, dur, vel=0.8, seed=0, bright=0.5, ring=2.0, pos=0.18, rel=0.15, pan=0.0, click=0.0):
    rng = _rng(seed)
    P = max(int(round(SR / f)), 4)
    f0 = SR / P
    nout = _n(dur, rel) + int(0.1 * SR)
    nout = min(nout, int((min(ring, dur + rel + 0.3)) * SR) + 2)
    ratio = f / f0
    m = int(nout * ratio) + 8
    e = rng.standard_normal(P)
    e = lp(e, 500 + bright * 9000, 1)
    k = max(1, int(pos * P))
    e = e - 0.7 * np.roll(e, k)
    e -= e.mean()
    e /= (np.abs(e).max() + 1e-9)
    x = np.zeros(m)
    x[:P] = e
    g = 10 ** (-3.0 / (f * ring))
    a = np.zeros(P + 2)
    a[0] = 1.0
    a[P] = -g * 0.5
    a[P + 1] = -g * 0.5
    y = signal.lfilter([1.0], a, x)
    y = np.interp(np.arange(nout) * ratio, np.arange(m), y)
    t = tarr(nout)
    env = np.ones(nout)
    tr = int(rel * SR)
    d_end = int(dur * SR)
    if d_end < nout:
        env[d_end:] = np.exp(-np.arange(nout - d_end) / SR / (rel * 0.5))
    y = y * env
    if click:
        y += bp(rng.standard_normal(nout), 2500, 7000) * np.exp(-t / 0.006) * click
    y /= (np.abs(y).max() + 1e-9)
    return pan2(fade_edges(y, 1, 5) * vel * 0.7, pan)


def harpsichord(f, dur, vel=0.8, seed=0, pan=0.0):
    a = pluck(f, dur, vel, seed, bright=1.0, ring=min(1.3, dur + 0.5), pos=0.12, rel=0.1, pan=pan, click=0.35)
    b = pluck(f * 2.0013, dur, vel * 0.45, seed + 1, bright=1.0, ring=0.8, pos=0.1, rel=0.1, pan=pan)
    n = max(len(a), len(b))
    out = np.zeros((n, 2))
    out[:len(a)] += a
    out[:len(b)] += b
    return hp(out, 120, 1)


def bell(f, dur=4.0, vel=0.8, seed=0, decay=5.0, pan=0.0, strike=0.5, dark=0.0):
    rng = _rng(seed)
    n = int(decay * 1.25 * SR)
    t = tarr(n)
    ratios = np.array([0.5, 1.0, 1.183, 1.506, 2.0, 2.514, 3.011, 4.166, 5.433, 6.796])
    amps = np.array([0.55, 1.0, 0.7, 0.45, 0.5, 0.28, 0.25, 0.16, 0.09, 0.05])
    taus = decay * np.array([1.0, 0.8, 0.6, 0.5, 0.42, 0.3, 0.26, 0.18, 0.12, 0.08]) * 0.45
    if dark:
        amps = amps * np.linspace(1, 1 - dark, len(amps))
    L = np.zeros(n)
    R = np.zeros(n)
    for r, a, tau in zip(ratios, amps, taus):
        fr = f * r * (1 + rng.uniform(-0.002, 0.002))
        if fr > 18000:
            continue
        env = np.exp(-t / tau)
        L += a * env * np.sin(2 * np.pi * fr * t + rng.uniform(0, 6))
        R += a * env * np.sin(2 * np.pi * fr * 1.0025 * t + rng.uniform(0, 6))
    x = np.stack([L, R], 1) / 3.2
    x *= np.minimum(1, t / 0.002)[:, None]
    cl = bp(rng.standard_normal(n), 1500, 6000) * np.exp(-t / 0.01) * strike
    x += pan2(cl, 0)
    return balance(x * vel, pan) * 0.7


def glass(f, dur=2.5, vel=0.8, seed=0, decay=2.5, pan=0.0):
    rng = _rng(seed)
    n = int(decay * 1.3 * SR)
    t = tarr(n)
    ratios = [1.0, 2.32, 4.25, 6.63]
    amps = [1.0, 0.45, 0.3, 0.14]
    taus = [decay * 0.45, decay * 0.28, decay * 0.17, decay * 0.1]
    L = np.zeros(n)
    R = np.zeros(n)
    for r, a, tau in zip(ratios, amps, taus):
        if f * r > 17000:
            continue
        env = np.exp(-t / tau) * (1 + 0.15 * np.sin(2 * np.pi * rng.uniform(3, 7) * t))
        L += a * env * np.sin(2 * np.pi * f * r * 0.9993 * t + rng.uniform(0, 6))
        R += a * env * np.sin(2 * np.pi * f * r * 1.0007 * t + rng.uniform(0, 6))
    x = np.stack([L, R], 1) / 2.0
    x *= np.minimum(1, t / 0.002)[:, None]
    x += pan2(bp(rng.standard_normal(n), 3000, 9000) * np.exp(-t / 0.008) * 0.2, 0)
    return balance(x * vel, pan) * 0.55


def celesta(f, dur=1.5, vel=0.8, seed=0, decay=1.4, pan=0.0):
    rng = _rng(seed)
    n = int(decay * 1.3 * SR)
    t = tarr(n)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / (decay * 0.5))
    if f * 4.01 < 17000:
        y += 0.25 * np.sin(2 * np.pi * f * 4.01 * t) * np.exp(-t / 0.12)
    if f * 2.0 < 17000:
        y += 0.35 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t / (decay * 0.22))
    y += bp(rng.standard_normal(n), 3000, 9000) * np.exp(-t / 0.005) * 0.12
    y *= np.minimum(1, t / 0.001)
    return pan2(y * vel * 0.55, pan)


def marimba(f, dur=0.6, vel=0.8, seed=0, pan=0.0, decay=0.5):
    rng = _rng(seed)
    n = int((decay + 0.3) * SR)
    t = tarr(n)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / decay)
    if f * 3.93 < 17000:
        y += 0.5 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t / (decay * 0.18))
    if f * 9.2 < 17000:
        y += 0.15 * np.sin(2 * np.pi * f * 9.2 * t) * np.exp(-t / (decay * 0.07))
    y += bp(rng.standard_normal(n), 800, 3000) * np.exp(-t / 0.006) * 0.25
    y *= np.minimum(1, t / 0.001)
    return pan2(y * vel * 0.6, pan)


def eplucked_fm(f, dur=1.0, vel=0.8, seed=0, pan=0.0, decay=0.8, idx=2.5):
    n = int((decay + 0.2) * SR)
    t = tarr(n)
    ix = idx * np.exp(-t / (decay * 0.35))
    y = np.sin(2 * np.pi * f * t + ix * np.sin(2 * np.pi * f * 2.0 * t)) * np.exp(-t / decay)
    y *= np.minimum(1, t / 0.002)
    return pan2(y * vel * 0.55, pan)


def drone_saw(f, dur, vel=0.8, seed=0, att=2.0, rel=2.0, cut=250, grit=0.0):
    n = _n(dur, rel)
    t = tarr(n)
    rng = _rng(seed)
    out = np.zeros((n, 2))
    for i, c in enumerate((-9, -3, 4, 10)):
        out += pan2(osc("saw", f * 2 ** (c / 1200), n, rng.random()), (-0.6, -0.2, 0.2, 0.6)[i]) * 0.5
    if grit:
        out = np.tanh(out * (1 + grit * 3))
    out = lp(out, cut)
    out = lp(out, cut * 2.0) * 0.5 + out * 0.5
    e = adsr(n, dur, att, 0.5, 0.95, rel, 1.4)
    return out * e[:, None] * vel * 0.5


# ======================================================== percusion
def _pad(y, p=0.0):
    return pan2(y, p)


def kick(vel=0.9, seed=0, f=52.0, decay=0.42, click=0.25, sweep=3.0, pan=0.0):
    n = int((decay + 0.15) * SR)
    t = tarr(n)
    rng = _rng(seed)
    fr = f * (1 + sweep * np.exp(-t / 0.022))
    body = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / (decay / 3.2))
    clk = lp(rng.standard_normal(n), 4000, 1) * np.exp(-t / 0.003) * click
    y = np.tanh((body + clk) * 1.5)
    return _pad(fade_edges(y, 0.3, 8) * vel * 0.9, pan)


def taiko(vel=0.9, seed=0, f=62.0, decay=1.15, pan=0.0, skin=0.5):
    n = int((decay + 0.6) * SR)
    t = tarr(n)
    rng = _rng(seed)
    fr = f * (1 + 1.1 * np.exp(-t / 0.05))
    body = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / (decay * 0.38))
    for r, a, tau in ((1.59, 0.45, 0.33), (2.14, 0.3, 0.22), (2.65, 0.18, 0.15)):
        fr2 = f * r * (1 + 0.6 * np.exp(-t / 0.05))
        body += a * np.sin(2 * np.pi * np.cumsum(fr2) / SR + rng.uniform(0, 6)) * np.exp(-t / (decay * tau))
    thw = bp(rng.standard_normal(n), 300, 3500) * np.exp(-t / 0.022) * skin
    boom = lp(rng.standard_normal(n), 160) * np.exp(-t / (decay * 0.4)) * 0.35
    y = np.tanh((body + thw + boom) * 1.2)
    y = y * np.minimum(1, t / 0.0008)
    return _pad(fade_edges(y, 0.2, 12) * vel * 0.85, pan)


def timpani(f, vel=0.8, seed=0, decay=1.8, pan=0.0):
    n = int((decay + 0.4) * SR)
    t = tarr(n)
    rng = _rng(seed)
    y = np.zeros(n)
    for r, a, tau in ((1.0, 0.7, 1.0), (1.5, 1.0, 0.9), (1.99, 0.6, 0.55), (2.44, 0.35, 0.35), (2.92, 0.2, 0.25)):
        fr = f * r * (1 + 0.04 * np.exp(-t / 0.08))
        y += a * np.sin(2 * np.pi * np.cumsum(fr) / SR + rng.uniform(0, 6)) * np.exp(-t / (decay * tau * 0.45))
    y += bp(rng.standard_normal(n), 200, 2500) * np.exp(-t / 0.02) * 0.4
    y = np.tanh(y * 0.9) * np.minimum(1, t / 0.001)
    return _pad(fade_edges(y, 0.2, 12) * vel * 0.7, pan)


def tom(vel=0.8, seed=0, f=110.0, decay=0.35, pan=0.0):
    n = int((decay + 0.2) * SR)
    t = tarr(n)
    rng = _rng(seed)
    fr = f * (1 + 0.7 * np.exp(-t / 0.04))
    y = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / (decay * 0.5))
    y += bp(rng.standard_normal(n), 300, 3000) * np.exp(-t / 0.015) * 0.4
    return _pad(fade_edges(np.tanh(y * 1.3), 0.2, 8) * vel * 0.8, pan)


def snare(vel=0.8, seed=0, tone=190.0, decay=0.14, pan=0.0, snap=0.8):
    n = int((decay + 0.25) * SR)
    t = tarr(n)
    rng = _rng(seed)
    nz = bp(rng.standard_normal(n), 1800, 9000) * np.exp(-t / decay)
    nz2 = bp(rng.standard_normal(n), 300, 1200) * np.exp(-t / 0.05) * 0.5
    ton = np.sin(2 * np.pi * np.cumsum(tone * (1 + 0.3 * np.exp(-t / 0.02))) / SR) * np.exp(-t / 0.05) * 0.6
    y = np.tanh((nz * snap + nz2 + ton) * 1.1) * np.minimum(1, t / 0.0006)
    return _pad(fade_edges(y, 0.2, 8) * vel * 0.7, pan)


def metal(vel=0.8, seed=0, f=800.0, ring=1.2, pan=0.0, thunk=0.5, click=0.7):
    n = int((ring + 0.4) * SR)
    t = tarr(n)
    rng = _rng(seed)
    ratios = np.array([1.0, 1.47, 2.09, 2.56, 3.37, 4.16, 5.6, 7.3])
    amps = np.array([1.0, 0.8, 0.65, 0.5, 0.4, 0.3, 0.2, 0.12])
    taus = ring * np.array([1.0, 0.8, 0.6, 0.5, 0.35, 0.25, 0.15, 0.1]) * 0.5
    y = np.zeros(n)
    for r, a, tau in zip(ratios, amps, taus):
        fr = f * r * (1 + rng.uniform(-0.012, 0.012))
        if fr < 17000:
            y += a * np.sin(2 * np.pi * fr * t + rng.uniform(0, 6)) * np.exp(-t / tau)
    y /= 3.0
    y += hp(rng.standard_normal(n), 2500) * np.exp(-t / 0.004) * click
    y += np.sin(2 * np.pi * (f * 0.18) * t) * np.exp(-t / 0.04) * thunk
    y *= np.minimum(1, t / 0.0005)
    return _pad(fade_edges(np.tanh(y * 1.1), 0.1, 10) * vel * 0.7, pan)


def chain(vel=0.7, seed=0, pan=0.0, dur=0.35):
    rng = _rng(seed)
    n = int((dur + 0.4) * SR)
    out = np.zeros((n, 2))
    for i in range(int(rng.integers(5, 10))):
        c = metal(vel * rng.uniform(0.3, 1.0), int(rng.integers(1 << 30)), f=rng.uniform(1800, 4200), ring=0.18, thunk=0.0, click=0.5)
        s = int(rng.uniform(0, dur) * SR)
        m = min(len(c), n - s)
        out[s:s + m] += c[:m] * 0.6
    return balance(out, pan)


def hat(vel=0.6, seed=0, open_=False, pan=0.0):
    rng = _rng(seed)
    dec = 0.2 if open_ else 0.035
    n = int((dec * 4 + 0.05) * SR)
    t = tarr(n)
    y = hp(rng.standard_normal(n), 6500) * np.exp(-t / dec)
    for r in (1.0, 1.34, 1.64, 2.0, 2.45, 2.9):
        y += 0.15 * np.sign(np.sin(2 * np.pi * 3100 * r * t)) * np.exp(-t / dec)
    y = hp(y, 5500)
    return _pad(fade_edges(y * np.minimum(1, t / 0.0005), 0.1, 6) * vel * 0.35, pan)


def shaker(vel=0.6, seed=0, pan=0.0):
    rng = _rng(seed)
    n = int(0.16 * SR)
    t = tarr(n)
    y = bp(rng.standard_normal(n), 4500, 10000) * (np.minimum(1, t / 0.02) * np.exp(-t / 0.045))
    return _pad(fade_edges(y, 1, 8) * vel * 0.5, pan)


def crash(vel=0.7, seed=0, dur=3.0, pan=0.0, rev=False):
    rng = _rng(seed)
    n = int(dur * SR)
    t = tarr(n)
    y = hp(rng.standard_normal(n), 2800) * np.exp(-t / (dur * 0.28))
    for r in (1.0, 1.4, 1.83, 2.37, 2.9, 3.3):
        y += 0.1 * np.sin(2 * np.pi * 2200 * r * t) * np.exp(-t / (dur * 0.2))
    y *= np.minimum(1, t / 0.0006)
    if rev:
        y = y[::-1] * np.minimum(1, (n - np.arange(n)) / (0.01 * SR))
        y = y * np.linspace(0.2, 1, n) ** 1.5
    return _pad(fade_edges(y, 2, 20) * vel * 0.3, pan)


def riser(vel=0.6, seed=0, dur=4.0, f0=200.0, f1=5000.0, pan=0.0):
    rng = _rng(seed)
    n = int(dur * SR)
    t = tarr(n)
    nz = rng.standard_normal(n)
    out = np.zeros(n)
    cs = np.geomspace(f0, f1, 7)
    pos = np.linspace(0, 1, n)
    for i, c in enumerate(cs):
        band = bpq(nz, c, 3.0, 2)
        w = np.exp(-((pos - i / 6.0) ** 2) / (2 * 0.12 ** 2))
        out += band * w
    sw = np.sin(2 * np.pi * np.cumsum(np.geomspace(f0 * 0.5, f1 * 0.3, n)) / SR) * 0.12
    out = (out + sw) * (pos ** 2.0)
    st = pan2(out, pan) * vel * 0.5
    return fade_edges(st, 5, 25)


def thunder(vel=0.8, seed=0, dur=4.0, crack=0.8):
    rng = _rng(seed)
    n = int(dur * SR)
    t = tarr(n)
    out = np.zeros((n, 2))
    for ch in range(2):
        br = np.cumsum(rng.standard_normal(n))
        br = hp(br, 25, 1)
        br /= np.abs(br).max()
        rum = lp(br, 150, 2) * 2.0 + lp(rng.standard_normal(n), 700, 2) * 0.35
        env = np.zeros(n)
        for k in range(int(rng.integers(5, 9))):
            ts = rng.uniform(0.0, dur * 0.5)
            tau = rng.uniform(0.5, 1.2)
            a = rng.uniform(0.3, 1.0) * (1.0 if k == 0 else 0.7)
            m = t > ts
            env[m] += a * np.exp(-(t[m] - ts) / tau) * np.minimum(1, (t[m] - ts) / 0.05)
        out[:, ch] = rum * env
    cr = bp(rng.standard_normal(n), 800, 6000) * np.exp(-t / 0.06) * crack
    out += pan2(cr, 0)
    out = np.tanh(out * 0.9)
    out *= np.minimum(1, (dur - t) / 0.5)[:, None]
    return out * vel * 0.8


def whisper(vel=0.6, seed=0, dur=2.5, pan=0.0, pan_move=0.8):
    rng = _rng(seed)
    n = int(dur * SR)
    t = tarr(n)
    nz = rng.standard_normal(n)
    f1 = rng.uniform(400, 700)
    f2 = rng.uniform(1400, 2400)
    y = bpq(nz, f1, 4) + 0.8 * bpq(nz, f2, 5) + 0.5 * bpq(nz, rng.uniform(2800, 4200), 5)
    am = np.abs(smooth_noise(n, rng, 7.0))
    am = (am / (am.max() + 1e-9)) ** 1.6
    y = y * am * np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5
    p = pan + pan_move * np.sin(2 * np.pi * rng.uniform(0.2, 0.5) * t + rng.uniform(0, 6))
    th = (p + 1) * np.pi / 4
    return np.stack([y * np.cos(th), y * np.sin(th)], 1) * vel * 1.4


def wind(vel=0.5, seed=0, dur=6.0, lo=250.0, hi=1800.0, pan=0.0):
    rng = _rng(seed)
    n = int(dur * SR)
    t = tarr(n)
    out = np.zeros((n, 2))
    cs = np.geomspace(lo, hi, 4)
    for ch in range(2):
        nz = rng.standard_normal(n)
        for i, c in enumerate(cs):
            w = (0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(0.1, 0.35) * t + rng.uniform(0, 6))) ** 2
            out[:, ch] += bpq(nz, c, 2.5) * w
    out *= (np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.2)[:, None]
    return balance(out, pan) * vel * 0.35


def sweep_saw(vel=0.5, seed=0, dur=3.0, f0=80.0, f1=400.0, cut=1500, pan=0.0):
    rng = _rng(seed)
    n = int(dur * SR)
    fr = np.geomspace(f0, f1, n)
    y = osc("saw", fr, n, rng.random())
    y = lp(y, cut)
    pos = np.linspace(0, 1, n)
    return pan2(y * pos ** 2 * vel * 0.4, pan)
