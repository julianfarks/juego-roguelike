"""ambience.py - 9 ambientes mono, loops de 10 s perfectos (ruido periodico por FFT, eventos con wrap circular)."""
import numpy as np
from dsp import SR

DUR = 10.0
N = int(DUR * SR)
FR = np.fft.rfftfreq(N, 1 / SR)
T = np.arange(N) / SR


def noise(rng, shape_fn):
    """ruido periodico (exactamente N muestras) con espectro de amplitud shape_fn(f)."""
    ph = rng.uniform(0, 2 * np.pi, len(FR))
    amp = shape_fn(np.maximum(FR, 1.0))
    amp[FR < 15] = 0
    X = amp * np.exp(1j * ph)
    X[0] = 0
    y = np.fft.irfft(X, n=N)
    return y / (np.abs(y).std() + 1e-12)


def bandn(rng, f0, f1, slope=0.0):
    return noise(rng, lambda f: ((f >= f0) & (f <= f1)) * (f / f0) ** slope * (1 / (1 + (f / f1) ** 8)))


def lpn(rng, fc, slope=-1.0):
    return noise(rng, lambda f: (f / 100.0) ** slope / (1 + (f / fc) ** 4))


def lfo(cycles, ph=0.0):
    return np.sin(2 * np.pi * cycles * T / DUR + ph)


def mod(rng, base, depth, cycles_list):
    m = np.zeros(N)
    for c in cycles_list:
        m += lfo(c, rng.uniform(0, 6.28)) / len(cycles_list)
    return base * (1 + depth * m)


def add_event(buf, ev, t0, gain=1.0):
    i = int(t0 * SR) % N
    m = len(ev)
    idx = (np.arange(m) + i) % N
    np.add.at(buf, idx, ev * gain)


def mix(*evs):
    out = np.zeros(max(len(e) for e in evs))
    for e in evs:
        out[:len(e)] += e
    return out


def ev_tone(f, dur, decay, partials=((1, 1.0),), att=0.002):
    t = np.arange(int(dur * SR)) / SR
    y = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t / (decay / (1 + 0.5 * (k - 1)))) for k, a in partials)
    return y * np.minimum(1, t / att)


def ev_noise(rng, dur, decay, f0, f1, att=0.002):
    n = int(dur * SR)
    t = np.arange(n) / SR
    X = np.fft.rfft(rng.standard_normal(n))
    fr = np.fft.rfftfreq(n, 1 / SR)
    X *= (fr >= f0) & (fr <= f1)
    y = np.fft.irfft(X, n=n)
    y /= np.abs(y).max() + 1e-12
    return y * np.exp(-t / decay) * np.minimum(1, t / att)


def finish(x, peak_db=-15.0):
    x = x - x.mean()
    x = np.tanh(x * 0.9) if np.abs(x).max() > 1 else x
    x *= 10 ** (peak_db / 20) / (np.abs(x).max() + 1e-12)
    return x.astype(np.float32)


def amb_catacumbas():
    r = np.random.default_rng(1)
    x = 0.9 * lpn(r, 180, -1.5) * mod(r, 1, 0.3, [1, 2]) + 0.25 * bandn(r, 600, 2500) * mod(r, 0.4, 0.8, [3, 5])
    # goteo en piedra y campana lejana
    for t0 in (0.8, 2.9, 3.4, 6.1, 8.3):
        add_event(x, ev_tone(r.uniform(900, 1500), 0.5, 0.08, ((1, 1), (2.7, 0.3))), t0, 0.35)
    add_event(x, ev_tone(146.8, 6, 2.2, ((1, 1), (2.4, 0.5), (3.9, 0.3), (5.1, 0.2))), 4.5, 0.5)
    x += 0.35 * lpn(r, 400, -0.5) * (0.5 + 0.5 * lfo(2))
    return finish(x)


def amb_forja():
    r = np.random.default_rng(2)
    x = 0.8 * lpn(r, 120, -1.2) * mod(r, 1, 0.25, [1, 3]) + 0.35 * bandn(r, 1500, 7000) * (0.4 + 0.6 * np.abs(lfo(6)) ** 3)
    for t0 in (1.0, 3.5, 6.0, 8.5):
        add_event(x, mix(ev_tone(r.uniform(500, 800), 1.4, 0.35, ((1, 1), (2.76, 0.6), (5.4, 0.3))), ev_noise(r, 0.05, 0.015, 2000, 9000)), t0, 0.4)
    for t0 in r.uniform(0, 10, 30):
        add_event(x, ev_noise(r, 0.03, 0.006, 3000, 12000), t0, r.uniform(0.1, 0.4))   # chispas
    add_event(x, ev_tone(55, 3, 1.0, ((1, 1), (2, .5))), 0.0, 0.5)
    return finish(x)


def amb_helado():
    r = np.random.default_rng(3)
    x = 0.9 * bandn(r, 200, 2200) * (mod(r, 1, 0.9, [1, 2, 3]) ** 2) * 0.5 + 0.3 * lpn(r, 300, -1.0)
    for t0 in r.uniform(0, 10, 9):
        f = r.choice([1568, 2093, 2349, 2794, 3136])
        add_event(x, ev_tone(f, 2.5, 0.7, ((1, 1), (2.01, 0.2), (3.99, 0.1))), t0, 0.12)
    add_event(x, ev_noise(r, 0.15, 0.04, 2500, 9000), 5.2, 0.3)
    return finish(x)


def amb_vacio():
    r = np.random.default_rng(4)
    drone = sum(np.sin(2 * np.pi * f * T + r.uniform(0, 6)) * a for f, a in ((41, 1), (41 * 1.4983, .4), (82.7, .35), (123.9, 0.2)))
    drone = drone * (1 + 0.3 * lfo(1))
    # cuantiza frecuencias a multiplos de 0.1 Hz para bucle perfecto
    drone = sum(np.sin(2 * np.pi * np.round(f * 10) / 10 * T + r.uniform(0, 6)) * a for f, a in ((41, 1), (61.4, .4), (82.7, .35), (123.9, 0.2)))
    x = 0.5 * drone + 0.4 * bandn(r, 800, 4500) * (np.abs(lfo(4)) * np.abs(lfo(3, 1))) ** 2 + 0.3 * lpn(r, 250)
    for t0 in (1.5, 4.2, 7.7):
        w = bandn(r, 700, 3500) * np.sin(np.pi * np.clip((T - t0) / 1.8, 0, 1)) ** 2 * ((T >= t0) & (T < t0 + 1.8))
        x += 0.5 * w
    return finish(x)


def amb_bosque():
    r = np.random.default_rng(5)
    x = 0.8 * bandn(r, 300, 3000) * mod(r, 1, 0.5, [1, 2, 4]) * 0.4 + 0.5 * lpn(r, 200, -1.2)
    # grillos: trinos AM periodicos
    for f in (3900, 4300):
        am = np.clip(np.sin(2 * np.pi * 14 * T), 0, 1) * (0.5 + 0.5 * lfo(2 if f < 4000 else 3))
        x += 0.07 * np.sin(2 * np.pi * f * T) * am
    # crujidos de madera y gotas
    for t0 in (0.9, 3.3, 7.4):
        add_event(x, ev_tone(r.uniform(120, 220), 0.5, 0.12, ((1, 1), (1.6, .6), (2.3, .3))) , t0, 0.5)
    for t0 in (2.1, 5.6, 9.0):
        add_event(x, ev_tone(r.uniform(700, 1100), 0.3, 0.05, ((1, 1),)), t0, 0.3)
    add_event(x, ev_tone(330, 1.2, 0.4, ((1, 1), (2, .3))), 6.5, 0.12)
    return finish(x)


def amb_tormenta():
    r = np.random.default_rng(6)
    x = 0.8 * bandn(r, 300, 3500) * mod(r, 1, 0.5, [1, 2]) * 0.5 + 0.6 * lpn(r, 400, -1.0)
    for t0, g in ((2.0, 1.0), (7.3, 0.7)):
        n = int(5 * SR)
        tt = np.arange(n) / SR
        br = np.cumsum(r.standard_normal(n)); br -= np.convolve(br, np.ones(2000) / 2000, 'same')
        from dsp import lp
        rum = lp(br / np.abs(br).max(), 160, 2) * np.exp(-tt / 1.2) * np.minimum(1, tt / 0.05)
        add_event(x, mix(rum * 3, ev_noise(r, 0.3, 0.08, 800, 6000) * 0.5), t0, g)
    for t0 in r.uniform(0, 10, 25):
        add_event(x, ev_noise(r, 0.02, 0.004, 3000, 10000), t0, 0.1)
    return finish(x)


def amb_sangre():
    r = np.random.default_rng(7)
    # coro etereo + organo grave
    ch = sum(np.sin(2 * np.pi * np.round(f * 10) / 10 * T + r.uniform(0, 6)) * a * (0.6 + 0.4 * lfo(k, r.uniform(0, 6)))
             for (f, a, k) in ((146.8, 1, 1), (220.0, .6, 2), (293.7, .4, 1), (349.2, .3, 3)))
    x = 0.5 * ch + 0.4 * lpn(r, 300, -1.2) + 0.15 * bandn(r, 1200, 5000)
    for t0 in (1.2, 5.0, 8.0):
        add_event(x, ev_tone(r.uniform(500, 700), 0.4, 0.09, ((1, 1),)), t0, 0.25)   # goteo de sangre
    add_event(x, ev_tone(73.4, 5, 2.0, ((1, 1), (2.4, .4), (4.1, .2))), 3.0, 0.5)
    return finish(x)


def amb_eclipse():
    r = np.random.default_rng(8)
    ch = sum(np.sin(2 * np.pi * np.round(f * 10) / 10 * T + r.uniform(0, 6)) * a * (0.6 + 0.4 * lfo(k, r.uniform(0, 6)))
             for (f, a, k) in ((130.8, 1, 1), (196.0, .7, 2), (261.6, .5, 1), (392.0, .3, 3), (523.3, .15, 2)))
    x = 0.5 * ch + 0.25 * lpn(r, 250, -1.2)
    add_event(x, ev_tone(261.6, 8, 3.0, ((1, 1), (2.4, .5), (3.9, .3), (5.3, .2))), 0.5, 0.35)
    add_event(x, ev_tone(392.0, 6, 2.5, ((1, 1), (2.4, .4), (3.9, .25))), 5.5, 0.25)
    x += 0.1 * bandn(r, 2000, 8000) * (0.5 + 0.5 * lfo(1))
    return finish(x)


def amb_cazador():
    r = np.random.default_rng(9)
    x = 0.7 * lpn(r, 200, -1.3) + 0.4 * bandn(r, 400, 2800) * mod(r, 1, 0.7, [1, 2]) * 0.4
    drone = sum(np.sin(2 * np.pi * np.round(f * 10) / 10 * T + r.uniform(0, 6)) * a for f, a in ((49, 1), (73.4, .5), (98, .3)))
    x += 0.35 * drone * (1 + 0.3 * lfo(1))
    for t0 in (1.0, 6.5):   # campana lejana tritono
        add_event(x, ev_tone(185, 5, 2.2, ((1, 1), (2.4, .5), (3.9, .3))), t0, 0.35)
    add_event(x, ev_tone(261.6, 4, 1.8, ((1, 1), (2.4, .4))), 6.5, 0.25)
    for t0 in (3.4, 8.6):
        add_event(x, ev_noise(r, 1.2, 0.5, 300, 1200), t0, 0.4)  # susurro de niebla
    return finish(x)


TRACKS = {"amb_" + k: globals()["amb_" + k] for k in
          ("catacumbas", "forja", "helado", "vacio", "bosque", "tormenta", "sangre", "eclipse", "cazador")}
