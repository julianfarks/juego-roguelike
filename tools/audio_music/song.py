"""song.py - teoria musical minima + secuenciador/mezclador (Song)."""
import re
import numpy as np
from dsp import *
import inst

NOTE_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def pc(name):
    p = NOTE_PC[name[0]]
    for ch in name[1:]:
        if ch == "#":
            p += 1
        elif ch == "b":
            p -= 1
    return p % 12


def midi(name):
    m = re.match(r"^([A-G])([#b]*)(-?\d)$", name)
    acc = sum(1 if c == "#" else -1 for c in m.group(2))
    return NOTE_PC[m.group(1)] + acc + 12 * (int(m.group(3)) + 1)


QUAL = {
    "": [0, 4, 7], "m": [0, 3, 7], "dim": [0, 3, 6], "aug": [0, 4, 8], "5": [0, 7], "sus2": [0, 2, 7], "sus4": [0, 5, 7],
    "7": [0, 4, 7, 10], "m7": [0, 3, 7, 10], "maj7": [0, 4, 7, 11], "dim7": [0, 3, 6, 9], "add9": [0, 4, 7, 14],
    "madd9": [0, 3, 7, 14], "m9": [0, 3, 7, 10, 14], "6": [0, 4, 7, 9], "m6": [0, 3, 7, 9], "maj9": [0, 4, 7, 11, 14],
    "m7b5": [0, 3, 6, 10], "7sus4": [0, 5, 7, 10], "9": [0, 4, 7, 10, 14], "cl": [0, 1, 6, 7],
}


def parse_chord(sym):
    m = re.match(r"^([A-G][#b]?)([^/]*)(?:/([A-G][#b]?))?$", sym)
    root = pc(m.group(1))
    ints = QUAL[m.group(2)]
    bass = pc(m.group(3)) if m.group(3) else root
    return root, ints, bass


def voicing(sym, lo=48, nmax=None):
    """acorde en posicion cerrada con la nota mas grave >= lo (midi)."""
    root, ints, _ = parse_chord(sym)
    base = lo + ((root - lo) % 12)
    notes = [base + i for i in ints]
    return notes[:nmax] if nmax else notes


def bass_note(sym, octave=2):
    _, _, b = parse_chord(sym)
    return b + 12 * (octave + 1)


def parse_prog(s, bpb=4):
    out = []
    beat = 0.0
    for tok in s.split():
        if ":" in tok:
            sym, d = tok.rsplit(":", 1)
            d = float(d)
        else:
            sym, d = tok, float(bpb)
        out.append((beat, d, sym))
        beat += d
    return out


def mel(s, key=None):
    """'D4:2 A4:1 r:1 | ...' -> [(beat, midi, dur)]. Sin nombre de nota => numero = semitonos sobre key."""
    out = []
    beat = 0.0
    for tok in s.replace("|", " ").split():
        if ":" in tok:
            nm, d = tok.rsplit(":", 1)
            d = float(d)
        else:
            nm, d = tok, 1.0
        if nm == "r":
            pass
        elif re.match(r"^[A-G]", nm):
            out.append((beat, midi(nm), d))
        else:
            out.append((beat, key + int(nm), d))
        beat += d
    return out


# leitmotiv del juego: semitonos sobre la tonica (modo menor). 8 compases de 4/4.
LEIT_TXT = ("0:2 7:1 8:1 | 7:2 5:1 3:1 | 2:1.5 3:.5 5:1 7:1 | 12:3 10:1 | "
            "12:2 7:1 8:1 | 7:1.5 5:.5 3:1 2:1 | 3:2 2:1 0:1 | 0:4")
LEIT_HARM = "Dm Bb Gm Bb Dm Bb Gm Dm:2 A:2"   # armonizacion en re menor


def leit(tonic, major=False, octave=0, bars=8):
    notes = mel(LEIT_TXT, tonic + 12 * octave)
    if major:
        notes = [(b, m + 1 if (m - tonic - 12 * octave) % 12 == 3 else m, d) for b, m, d in notes]
    return [n for n in notes if n[0] < bars * 4]


class Song:
    def __init__(self, name, bpm, bars, bpb=4, loop=True, tail=0.0, seed=1, irs=("hall", "room"),
                 send_hp=150.0):
        self.name, self.bpm, self.bars, self.bpb, self.loop = name, bpm, bars, bpb, loop
        self.spb = 60.0 / bpm
        self.dur = bars * bpb * self.spb
        self.N = int(round((self.dur + (0 if loop else tail)) * SR))
        self.pad = int(10 * SR) if loop else int(2 * SR)
        L = self.N + self.pad
        self.dry = np.zeros((L, 2), np.float32)
        self.sa = np.zeros((L, 2), np.float32)
        self.sb = np.zeros((L, 2), np.float32)
        self.rng = np.random.default_rng(seed)
        self.irs = irs
        self.send_hp = send_hp
        self.n_notes = 0

    # --------------------------------------------------------------- bajo nivel
    def _put(self, x, start, gain, sa, sb):
        if self.loop:
            start %= self.N
        else:
            start = max(start, 0)
        if start >= self.N:
            return
        m = min(len(x), len(self.dry) - start)
        x = x[:m].astype(np.float32)
        self.dry[start:start + m] += x * gain
        if sa:
            self.sa[start:start + m] += x * (gain * sa)
        if sb:
            self.sb[start:start + m] += x * (gain * sb)
        self.n_notes += 1

    def _t(self, beat, hum):
        t = beat * self.spb + self.rng.normal(0, hum)
        return int(t * SR)

    def note(self, fn, pitch, beat, dur, vel=0.8, pan=0.0, sa=0.25, sb=0.0, gain=1.0, hum=0.008,
             vh=0.07, **kw):
        f = float(mtof(pitch)) if pitch < 300 else float(pitch)
        v = float(np.clip(vel * (1 + self.rng.normal(0, vh)), 0.05, 1.3))
        seed = int(self.rng.integers(1 << 30))
        x = fn(f, dur * self.spb, v, seed=seed, **kw)
        if pan:
            x = balance(x, pan)
        self._put(x, self._t(beat, hum), gain, sa, sb)

    def hit(self, fn, beat, vel=0.8, pan=0.0, sa=0.1, sb=0.1, gain=1.0, hum=0.004, vh=0.08, **kw):
        v = float(np.clip(vel * (1 + self.rng.normal(0, vh)), 0.05, 1.3))
        seed = int(self.rng.integers(1 << 30))
        x = fn(vel=v, seed=seed, **kw)
        if pan:
            x = balance(x, pan)
        self._put(x, self._t(beat, hum), gain, sa, sb)

    # --------------------------------------------------------------- alto nivel
    def bar(self, b):
        return b * self.bpb

    def play(self, fn, notes, bar0=0, transpose=0, vel=0.8, pan=0.0, sa=0.25, sb=0.0, gain=1.0,
             legato=1.0, hum=0.008, shift=0.0, **kw):
        base = bar0 * self.bpb + shift
        for b, m, d in notes:
            self.note(fn, m + transpose, base + b, d * legato, vel, pan, sa, sb, gain, hum, **kw)

    def chords(self, fn, prog, bar0=0, lo=48, nmax=4, vel=0.6, pan=0.0, sa=0.3, sb=0.0, gain=1.0,
               strum=0.0, legato=1.0, hum=0.01, spread=0.0, transpose=0, **kw):
        base = bar0 * self.bpb
        for b, d, sym in parse_prog(prog, self.bpb):
            vs = voicing(sym, lo, nmax)
            for i, m in enumerate(vs):
                p = pan + spread * ((i / max(len(vs) - 1, 1)) * 2 - 1)
                self.note(fn, m + transpose, base + b + strum * i, d * legato, vel, p, sa, sb, gain, hum, **kw)

    def bassline(self, fn, prog, bar0=0, octave=2, vel=0.7, pan=0.0, sa=0.1, sb=0.0, gain=1.0,
                 legato=1.0, hum=0.008, transpose=0, **kw):
        base = bar0 * self.bpb
        for b, d, sym in parse_prog(prog, self.bpb):
            self.note(fn, bass_note(sym, octave) + transpose, base + b, d * legato, vel, pan, sa, sb, gain, hum, **kw)

    def arp(self, fn, prog, pattern, bar0=0, lo=48, step=0.5, vel=0.5, pan=0.0, sa=0.3, sb=0.0, gain=1.0,
            nlen=None, octs=1, hum=0.006, pan_sweep=0.0, accent=0.0, transpose=0, **kw):
        """pattern: lista de indices de nota del acorde (con wrap a la octava); None = silencio."""
        base = bar0 * self.bpb
        k = 0
        for b, d, sym in parse_prog(prog, self.bpb):
            vs = voicing(sym, lo)
            steps = int(round(d / step))
            for s in range(steps):
                idx = pattern[s % len(pattern)]
                if idx is None:
                    continue
                m = vs[idx % len(vs)] + 12 * (idx // len(vs)) + transpose
                v = vel * (1 + accent * (1 if s % len(pattern) == 0 else 0))
                p = pan + pan_sweep * np.sin(k * 0.9)
                self.note(fn, m, base + b + s * step, (nlen or step) , v, p, sa, sb, gain, hum, **kw)
                k += 1

    def pat(self, fn, pats, bars, vel=0.8, pan=0.0, sa=0.1, sb=0.1, gain=1.0, hum=0.004, pan_rand=0.0,
            skip=None, **kw):
        """pats: cadena con patrones por compas separados por espacio; ciclan. x=normal X=acento o=fantasma."""
        pl = pats.split()
        a, b = bars
        for bi in range(a, b):
            p = pl[(bi - a) % len(pl)]
            if skip and bi in skip:
                continue
            st = self.bpb / len(p)
            for i, ch in enumerate(p):
                if ch == ".":
                    continue
                v = vel * {"x": 1.0, "X": 1.25, "o": 0.5, "g": 0.35}.get(ch, 1.0)
                pp = pan + (self.rng.uniform(-pan_rand, pan_rand) if pan_rand else 0)
                self.hit(fn, bi * self.bpb + i * st, v, pp, sa, sb, gain, hum, **kw)

    # --------------------------------------------------------------- render final
    def render(self, wet_a=1.0, wet_b=1.0, comp=(-18.0, 2.0), sat=1.25, target=-14.0, peak=-2.0,
               fade_out=0.0):
        N, pad = self.N, self.pad
        dry, sa, sb = self.dry, self.sa, self.sb
        if self.loop:
            for b in (dry, sa, sb):
                b[:pad] += b[N:N + pad]
            dry, sa, sb = dry[:N].astype(np.float64), sa[:N].astype(np.float64), sb[:N].astype(np.float64)
            if self.send_hp:
                sa, sb = chp(sa, self.send_hp), chp(sb, self.send_hp)
        else:
            dry, sa, sb = dry[:N].astype(np.float64), sa[:N].astype(np.float64), sb[:N].astype(np.float64)
            if self.send_hp:
                sa, sb = hp(sa, self.send_hp), hp(sb, self.send_hp)
        mix = dry.copy()
        if wet_a and np.abs(sa).max() > 0:
            mix += reverb(sa, self.irs[0], self.loop) * wet_a
        if wet_b and np.abs(sb).max() > 0:
            mix += reverb(sb, self.irs[1], self.loop) * wet_b
        if not self.loop:
            # el final no-loop: desvanecimiento suave de la cola
            fo = int((fade_out or 1.2) * SR)
            mix[-fo:] *= (np.cos(np.linspace(0, np.pi / 2, fo)) ** 2)[:, None]
        out = master(mix, self.loop, comp, sat, target, peak)
        return out.astype(np.float32)


LEIT_HARM_MAJOR = "D:2 Bb:2 Gmaj7 Em:2 A7:2 D7 D:2 Bb:2 G:2 Asus4:2 Bm D:2 A:2"


def leit_twist(tonic, octave=0):
    """leitmotiv deformado (bestial): tritonos y semitonos."""
    mp = {7: 6, 8: 8, 5: 6, 3: 3, 2: 1, 0: 0, 12: 12, 10: 11}
    out = []
    for b, m, d in mel(LEIT_TXT, tonic + 12 * octave):
        off = (m - tonic - 12 * octave)
        out.append((b, tonic + 12 * octave + mp.get(off, off), d))
    return out
