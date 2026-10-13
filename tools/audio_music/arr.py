"""arr.py - capas de arreglo reutilizables."""
import numpy as np
import inst
from song import *


def taiko_roll(S, beat0, nbeats, v0=0.3, v1=0.9, step=0.25, fn=None, sa=0.2, sb=0.15, pan=0.0, **kw):
    fn = fn or inst.taiko
    n = int(nbeats / step)
    for i in range(n):
        v = v0 + (v1 - v0) * (i / max(n - 1, 1)) ** 1.5
        S.hit(fn, beat0 + i * step, v, pan, sa, sb, hum=0.003, **kw)


def rev_crash_into(S, end_beat, dur_s=3.4, vel=0.6, riser=True, rv=0.5):
    """crash invertido + riser terminando exactamente en end_beat."""
    start = end_beat - dur_s / S.spb
    S.hit(inst.crash, start, vel, 0, rv, 0.0, hum=0.0, dur=dur_s, rev=True)
    if riser:
        S.hit(inst.riser, end_beat - 4.0 / S.spb, vel * 0.8, 0, rv, 0.0, hum=0.0, dur=4.0)


def toll(S, beat, name, vel=0.7, decay=6.0, sa=0.45, sb=0.0, pan=0.0, octave_shift=0, **kw):
    S.note(inst.bell, midi(name) + octave_shift, beat, 1.0, vel, pan, sa, sb, decay=decay, hum=0.0, **kw)


def sparkle(S, bar0, bar1, scale, density=0.5, fn=None, lo=72, hi=96, vel=0.4, sa=0.5, seed=0, **kw):
    """notas de cristal/celesta aleatorias (determinista) en una escala (lista de pitch-classes)."""
    fn = fn or inst.celesta
    rng = np.random.default_rng(seed)
    for b in range(bar0 * S.bpb, bar1 * S.bpb):
        if rng.random() < density:
            cand = [m for m in range(lo, hi + 1) if m % 12 in scale]
            m = int(rng.choice(cand))
            S.note(fn, m, b + rng.choice([0, 0.5, 1.0 / 3, 0.75]), 1, vel * rng.uniform(0.6, 1.0),
                   rng.uniform(-0.8, 0.8), sa, 0.0, **kw)


def whispers(S, bar0, bar1, n, vel=0.5, seed=0, sa=0.5):
    rng = np.random.default_rng(seed)
    for i in range(n):
        b = rng.uniform(bar0, bar1) * S.bpb
        S.hit(inst.whisper, b, vel * rng.uniform(0.6, 1.0), rng.uniform(-0.8, 0.8), sa, 0.0, hum=0.0,
              dur=rng.uniform(1.5, 3.5))


def cyc(prog, n):
    return " ".join([prog] * n)


def _prog_bars(S, prog):
    pr = parse_prog(prog, S.bpb)
    total = sum(d for _, d, _ in pr)
    nb = int(round(total / S.bpb))
    bars = [[] for _ in range(max(nb, 1))]
    for b, d, sym in pr:
        bi = int(b // S.bpb)
        bars[bi].append((b - bi * S.bpb, d, sym))
    for i, l in enumerate(bars):          # compases sin acorde propio heredan el anterior
        if not l:
            bars[i] = [(0.0, S.bpb, bars[i - 1][-1][2])]
    return bars


def sym_at(bars, bi, beat_in_bar):
    lst = bars[bi % len(bars)]
    cur = lst[0][2]
    for b0, d, sym in lst:
        if beat_in_bar + 1e-6 >= b0:
            cur = sym
    return cur


def riff(S, fn, prog, rhythm, bars, origin=0, octave=2, offsets=(0,), vel=0.7, dur=0.8, pan=0.0, sa=0.1, sb=0.0,
         gain=1.0, chord=False, lo=48, nmax=3, transpose=0, hum=0.006, **kw):
    """riff ritmico sobre la progresion `prog` (ciclo de N compases que arranca en `origin`)."""
    pb = _prog_bars(S, prog)
    pl = rhythm.split()
    a, b = bars
    k = 0
    for bi in range(a, b):
        r = pl[(bi - a) % len(pl)]
        step = S.bpb / len(r)
        for i, ch in enumerate(r):
            if ch == ".":
                continue
            beat_in = i * step
            sym = sym_at(pb, bi - origin, beat_in)
            v = vel * {"X": 1.25, "o": 0.55, "g": 0.35}.get(ch, 1.0)
            t0 = bi * S.bpb + beat_in
            if chord:
                vs = voicing(sym, lo, nmax)
                for j, m in enumerate(vs):
                    S.note(fn, m + transpose, t0, dur * step, v, pan, sa, sb, gain, hum, **kw)
            else:
                m = bass_note(sym, octave) + offsets[k % len(offsets)] + transpose
                S.note(fn, m, t0, dur * step, v, pan, sa, sb, gain, hum, **kw)
            k += 1
