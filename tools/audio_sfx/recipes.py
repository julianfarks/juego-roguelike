"""Bloques de sintesis de nivel medio reutilizados por todos los efectos."""
import numpy as np
from dsp import *

BAR = [(1, 1.0), (2.756, .55), (5.404, .3), (8.933, .15)]
BELL = [(0.5, .55), (1, 1.0), (1.183, .7), (1.506, .5), (2.0, .55), (2.514, .3), (2.662, .35),
        (3.011, .2), (4.166, .15), (5.433, .08), (6.796, .05)]
GLASS = [(1, 1.0), (2.32, .6), (4.25, .4), (6.63, .25), (9.38, .15)]
PLATE = [(1, 1.0), (1.59, .7), (2.14, .6), (2.30, .5), (2.65, .45), (2.92, .35), (3.5, .3), (4.1, .2), (5.2, .12)]
BONE = [(1, 1.0), (1.71, .7), (2.6, .4), (3.9, .2)]


def modal(f0, partials, dur, tau, r, spread=0.0, tilt=0.55, a=0.0004):
    n = N(dur)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for ratio, amp in partials:
        f = f0 * ratio * (1 + r.uniform(-spread, spread))
        if f > 0.45 * SR:
            continue
        out += amp * np.exp(-t / (tau / ratio ** tilt)) * np.sin(2 * np.pi * f * t + r.uniform(0, 6.28))
    an = max(1, int(a * SR))
    out[:an] *= np.linspace(0, 1, an)
    return out / (len(partials) ** 0.5)


def bell(f, dur, tau, r, spread=0.003):
    return modal(f, BELL, dur, tau, r, spread, tilt=0.45, a=0.001)


def whoosh(dur, pts, r, q=1.5, pk=0.4, p=1.5, color='white', env=None):
    """Ruido filtrado por banda con barrido (pts = [(t,hz),..])."""
    n = N(dur)
    w = noise(n, r, color)
    fc = curve(dur, pts, log=True)
    y = sweep(w, fc, 'bp', q)
    return y * (bump(dur, pk, p) if env is None else env)


def thump(f0, f1, dur, tf=0.04, tau=0.12, drive=1.0, a=0.001):
    n = N(dur)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / tf)
    y = sine(f, n) * expdec(dur, tau, a)
    return sat(y, drive) if drive > 1 else y


def tick(r, dur=0.008, f=3000, tau=0.002, color='white'):
    n = N(dur)
    w = hp(noise(n, r, color), f, 2)
    return w * expdec(dur, tau, 0.0002)


def crackle(dur, rate, r, fc=3000, q=1.2, hpf=600):
    n = N(dur)
    rt = arr(rate, n)
    imp = (r.random(n) < rt / SR) * r.uniform(.15, 1, n) ** 2 * r.choice([-1, 1], n)
    y = reson(imp, fc, q) if q else imp
    return hp(y, hpf, 1) * 6


def rumble(dur, r, f=100, mod=6.0, depth=0.5, env=None):
    n = N(dur)
    y = lp(noise(n, r, 'brown'), f, 2)
    t = np.arange(n) / SR
    y *= 1 - depth + depth * (0.5 + 0.5 * np.sin(2 * np.pi * mod * t + r.uniform(0, 6)))
    y = y / (y.std() + 1e-9) * 0.5
    return y * (swell(dur, dur * 0.3, dur * 0.5) if env is None else env)


def sparkle(dur, r, n_ev=20, flo=2500, fhi=9000, tau=0.06, decay_pow=1.0, g=1.0):
    n = N(dur)
    out = np.zeros(n)
    ts = r.random(n_ev) ** decay_pow * dur * 0.95
    for tt_ in ts:
        f = np.exp(r.uniform(np.log(flo), np.log(fhi)))
        L = N(tau * 4)
        t = np.arange(L) / SR
        s = np.sin(2 * np.pi * f * t) * np.exp(-t / tau) * r.uniform(.3, 1)
        s[:20] *= np.linspace(0, 1, 20)
        i = int(tt_ * SR)
        e = min(n, i + L)
        out[i:e] += s[:e - i]
    return out * g


def shatter(dur, r, flo=2500, fhi=9000, n_ev=35, tau=0.05, parts=GLASS):
    n = N(dur)
    out = np.zeros(n)
    for _ in range(n_ev):
        i = int(min(r.exponential(dur * 0.25), dur * 0.9) * SR)
        f = np.exp(r.uniform(np.log(flo), np.log(fhi)))
        s = modal(f, parts[:3], tau * 6, tau * r.uniform(.5, 1.5), r, 0.01)
        e = min(n, i + len(s))
        out[i:e] += s[:e - i] * r.uniform(.2, 1)
    return out


def chain(dur, r, n_ev=10, fl=1500, fh=4000, tau=0.035, accel=1.0):
    n = N(dur)
    out = np.zeros(n)
    ts = np.sort(r.random(n_ev) ** accel) * dur * 0.9
    for tt_ in ts:
        f = r.uniform(fl, fh)
        s = modal(f, BAR, tau * 6, tau, r, 0.02)
        s += 0.4 * tick(r, 0.01, 2500)[:len(s)].repeat(1)[:len(s)] if False else 0
        i = int(tt_ * SR)
        e = min(n, i + len(s))
        out[i:e] += s[:e - i] * r.uniform(.3, 1)
    return out


def debris(dur, r, n_ev=40, flo=400, fhi=3500, tau=0.04, start_dense=True, ping=True):
    n = N(dur)
    out = np.zeros(n)
    for _ in range(n_ev):
        i = int((r.exponential(dur * 0.3) if start_dense else r.uniform(0, dur)) * SR)
        if i >= n - 200:
            continue
        L = N(tau * 5)
        f = np.exp(r.uniform(np.log(flo), np.log(fhi)))
        s = reson(noise(L, r), f, 3) * expdec(tau * 5, tau * r.uniform(.5, 1.5), 0.0003)
        if ping and r.random() < .5:
            s += 0.5 * modal(f * 0.7, BAR[:3], tau * 5, tau * 1.2, r)[:L]
        e = min(n, i + L)
        out[i:e] += s[:e - i] * r.uniform(.2, 1)
    return out


def bubbles(dur, r, n_ev=15, flo=150, fhi=500, g=1.0):
    n = N(dur)
    out = np.zeros(n)
    for _ in range(n_ev):
        i = int(r.uniform(0, dur * .95) * SR)
        L = N(r.uniform(.03, .07))
        f0 = np.exp(r.uniform(np.log(flo), np.log(fhi)))
        t = np.arange(L) / SR
        f = f0 * (1 + 1.5 * t / (L / SR))
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (L / SR * .45))
        e = min(n, i + L)
        out[i:e] += s[:e - i] * r.uniform(.3, 1)
    return out * g


def creak(dur, r, f0=40, f1=70, res=(500, 1300), q=9, drive=1.0):
    n = N(dur)
    walk = lp(noise(n, r), 6, 1)
    walk = walk / (walk.std() + 1e-9)
    fp = curve(dur, [(0, f0), (dur, f1)]) * (1 + 0.25 * walk)
    src = saw(fp, n)
    fc = curve(dur, [(0, res[0]), (dur * .5, res[1]), (dur, res[0] * 1.3)], log=True) * (1 + .2 * walk)
    y = sweep(src, fc, 'bp', q)
    y = y / (y.std() + 1e-9)
    return sat(y * 0.6, drive) if drive > 1 else y * 0.6


def squelch(dur, r, f=700, g=1.0):
    n = N(dur)
    w = noise(n, r)
    fc = curve(dur, [(0, f), (dur, f * .3)], log=True)
    y = sweep(w, fc, 'lp', 1)
    y *= expdec(dur, dur * .3, 0.001)
    wob = 1 + .5 * np.sin(2 * np.pi * r.uniform(40, 90) * np.arange(n) / SR)
    return y * wob * g


def flesh_hit(r, f=140, g=1.0, wet=1.0):
    th = thump(f * 1.8, f * .6, .16, .03, .06)
    sq = squelch(.12, r, 900) * wet
    tk = tick(r, .012, 1200, .003) * .5
    return Mix().add(th, 0, 1).add(sq, 0.002, .8).add(tk, 0, .6).render()


def wingflap(dur, r, rate=6.5, f=700, g=1.0):
    n = N(dur)
    t = np.arange(n) / SR
    w = lp(noise(n, r), f, 2)
    ph = np.sin(np.pi * ((t * rate) % 1.0)) ** 2
    ph *= 0.5 + 0.5 * np.hanning(n) ** 0.5
    snap = hp(noise(n, r), 2000, 1) * (ph > .98) * 0
    y = w * ph
    return y / (y.std() + 1e-9) * .4 * g


def thunder(dur, r, crack=True, g=1.0):
    n = N(dur)
    m = Mix()
    if crack:
        c = sat(hp(noise(N(.35), r), 1200, 2) * expdec(.35, .06, .0003), 4)
        m.add(c, 0, .9)
        m.add(sweep(noise(N(.4), r), curve(.4, [(0, 6000), (.4, 800)], log=True), 'lp') * expdec(.4, .1, .0005), 0, .8)
    rm = rumble(dur, r, 140, 4.5, .6, env=expdec(dur, dur * .35, .02))
    m.add(rm, 0.03, 1.8)
    m.add(thump(70, 28, min(dur, .9), .12, .35, 1.5), 0.02, .8)
    out = m.render(dur)
    return out * g


def heartbeat(r, g=1.0, f=62):
    m = Mix()
    m.add(thump(f * 1.5, f * .8, .22, .04, .07, 1.3), 0, 1.0)
    m.add(thump(f * 1.3, f * .75, .2, .04, .07, 1.2), .16, .75)
    return m.render() * g


def choir(notes, dur, r, vowels=('o', 'a'), a=.25, rel=.4, nv=3, det=.008, vib=5.2, cutoff=3500, g=1.0, breath=.04, scale=1.0, gains=None):
    n = N(dur)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for ni, f0 in enumerate(notes):
        ph = r.uniform(0, 6.28)
        src = np.zeros(n)
        for v in range(nv):
            vr = vib * r.uniform(.9, 1.15)
            f = arr(f0, n) * (1 + det * (v - (nv - 1) / 2) / max(1, nv / 2)) * (1 + .006 * np.sin(2 * np.pi * vr * t + r.uniform(0, 6.28)))
            src += saw(f, n, r.uniform(0, 1))
        src = lp(src / nv, cutoff, 2)
        src += breath * lp(noise(n, r), 4000, 1)
        y = formant_morph(src, vowels[0], vowels[1], np.linspace(0, 1, n) ** .8, scale)
        out += y * (1 if gains is None else gains[ni])
    return out / max(1, len(notes)) ** .6 * swell(dur, a, rel, n) * g


def voice(dur, f0, r, v0='a', v1=None, morph=None, scale=1.0, dist=1.0, vib=(5.5, .012), growl=0.0, growl_f=70,
          breath=.1, env=None, nv=2, det=.012, jitter=0.0, sub=0.0, hpf=0):
    n = N(dur)
    t = np.arange(n) / SR
    f = arr(f0, n).copy()
    if vib:
        f = f * (1 + vib[1] * np.sin(2 * np.pi * vib[0] * t + r.uniform(0, 6)))
    if jitter:
        j = lp(noise(n, r), 25, 1)
        f = f * (1 + jitter * j / (j.std() + 1e-9))
    src = np.zeros(n)
    for v in range(nv):
        src += saw(f * (1 + det * (v - (nv - 1) / 2)), n, r.uniform(0, 1))
    src /= nv
    if sub:
        src += sub * sine(f * .5, n)
    if growl:
        am = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * growl_f * t)) * 0.0 + 0.5 * np.sin(2 * np.pi * growl_f * t)
        src *= (1 - growl) + growl * am
    if breath:
        src += breath * noise(n, r)
    m = np.linspace(0, 1, n) if morph is None else morph
    y = formant_morph(src, v0, v1 or v0, m, scale)
    y = y / (y.std() + 1e-9) * .3
    if dist > 1:
        y = sat(y, dist)
    if hpf:
        y = hp(y, hpf, 2)
    return y * (bump(dur, .25, 1.0) if env is None else env)


def whisper(dur, r, rate=6.0, v=('i', 'e'), g=1.0, hpf=900, nv=1):
    n = N(dur)
    out = np.zeros(n)
    for _ in range(nv):
        w = noise(n, r)
        e = np.abs(lp(noise(n, r), rate, 2))
        e = (e / (e.max() + 1e-9)) ** 1.6
        y = formant_morph(w, v[0], v[1], .5 + .5 * np.sin(2 * np.pi * rate * .3 * np.arange(n) / SR + r.uniform(0, 6)))
        out += hp(y, hpf, 1) * e
    return out / (out.std() + 1e-9) * .3 * g * swell(dur, dur * .3, dur * .4)


def riser(dur, f0, f1, r, q=2.0, tone=0.0, curve_pow=2.0, color='white'):
    n = N(dur)
    t = np.arange(n) / SR
    w = noise(n, r, color)
    fc = curve(dur, [(0, f0), (dur, f1)], log=True)
    y = sweep(w, fc, 'bp', q)
    e = (t / dur) ** curve_pow
    y *= e
    if tone:
        f = curve(dur, [(0, f0 * .25), (dur, f1 * .25)], log=True)
        y += tone * sine(f, n) * e
    return y / (y.std() + 1e-9) * .3


def zap(dur, r, f0=2500, f1=300, rate=1.0, g=1.0):
    n = N(dur)
    t = np.arange(n) / SR
    f = curve(dur, [(0, f0), (dur, f1)], log=True)
    jit = lp(noise(n, r), 400, 1)
    f = f * (1 + .5 * jit / (jit.std() + 1e-9) * .3)
    y = sat(saw(f, n) * .6 + square(f * 1.5, n) * .3, 3)
    y = hp(y, 500, 1) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * (60 + 80 * rate) * t)))
    y += .5 * crackle(dur, curve(dur, [(0, 1500), (dur, 300)]), r, 4500, 0.9, 1500)
    return y / (y.std() + 1e-9) * .25 * g


def boom(dur, r, f=60, g=1.0, tail=0.8, noise_f=1500):
    n = N(dur)
    m = Mix()
    m.add(thump(f * 2.2, f * .45, dur, .09, dur * .35, 1.6), 0, 1.0)
    nz = sweep(noise(n, r), curve(dur, [(0, noise_f), (dur * .6, 120)], log=True), 'lp') * expdec(dur, dur * .2, .0005)
    m.add(nz, 0, .9)
    m.add(tick(r, .02, 600, .006), 0, .6)
    return m.render(dur) * g


def sword_ring(r, f=3200, dur=.5, tau=.12, g=1.0):
    return modal(f, BAR, dur, tau, r, .01, .5) * g


def gust(dur, r, f0=400, f1=1400, q=0.8, g=1.0):
    n = N(dur)
    w = noise(n, r, 'pink')
    lfo = lp(noise(n, r), 3, 1)
    lfo = 1 + .6 * lfo / (lfo.std() + 1e-9)
    fc = curve(dur, [(0, f0), (dur * .5, f1), (dur, f0 * .8)], log=True) * np.clip(lfo, .5, 1.6)
    y = sweep(w, fc, 'bp', q)
    return y / (y.std() + 1e-9) * .3 * g * swell(dur, dur * .3, dur * .4)


def mt(m):
    """MIDI -> Hz"""
    return 440.0 * 2 ** ((m - 69) / 12.0)


def seq(notes, step, fn, total=None):
    """Coloca fn(freq, i) en una secuencia."""
    m = Mix()
    for i, f in enumerate(notes):
        m.add(fn(f, i), i * step)
    return m.render(total)


def ks(f, dur, r, decay=0.997, bright=0.6):
    """Karplus-Strong (cuerda/metal pulsado) via lfilter."""
    n = N(dur)
    L = max(2, int(SR / f))
    exc = r.uniform(-1, 1, L)
    exc = lp(exc, 800 + 9000 * bright, 1)
    x = np.zeros(n)
    x[:L] = exc[:min(L, n)]
    a = np.zeros(L + 2)
    a[0] = 1.0
    a[L] = -decay * 0.5
    a[L + 1] = -decay * 0.5
    y = lfilter([1.0], a, x)
    return y / (np.abs(y).max() + 1e-9)


def slash(r, d=.12, f0=2500, f1=8000, q=2.5, g=1.0):
    return whoosh(d, [(0, f0), (d, f1)], r, q, .5, 1.2) * g


def fireroar(dur, r, f=700, g=1.0, flutter=30):
    n = N(dur)
    w = noise(n, r, 'pink')
    fl = lp(noise(n, r), flutter, 1)
    fl = 1 + .5 * fl / (fl.std() + 1e-9)
    fc = curve(dur, [(0, f * .5), (dur * .3, f * 2), (dur, f)], log=True) * np.clip(fl, .4, 1.8)
    y = sweep(w, fc, 'lp', 1.0)
    y = y / (y.std() + 1e-9) * .35 * np.clip(fl, .3, 1.8)
    return y * g * swell(dur, dur * .12, dur * .5)


def ksum(freqs, dur, r, decay=.997, bright=.6, stagger=0.0, g=1.0):
    m = Mix()
    for i, f in enumerate(freqs):
        m.add(ks(f, dur, r, decay, bright), i * stagger, g)
    return m.render()


def drone(dur, f, r, g=1.0, detune=.004, harm=3, cutoff=1500, a=None, rel=None):
    n = N(dur)
    y = np.zeros(n)
    for k in range(3):
        y += saw(f * (1 + detune * (k - 1)), n, r.uniform(0, 1))
    y = lp(y / 3, cutoff, 2)
    y += .5 * sine(f * .5, n)
    return y * swell(dur, a if a else dur * .4, rel if rel else dur * .4) * g * .5


def tonecloud(freqs, dur, r, g=1.0, a=None, rel=None):
    n = N(dur)
    y = np.zeros(n)
    for f in freqs:
        y += fm(f, 2.0, 1.2, n) + .5 * sine(f * 2.003, n)
    return y / len(freqs) ** .7 * swell(dur, a if a else dur * .5, rel if rel else dur * .3) * g
