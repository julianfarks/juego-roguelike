"""tracks_c.py - jefes y jefe final."""
import numpy as np
import inst
from song import *
from arr import *


def _chants(S, prog, rhythm, bars, origin, octave=3, vel=0.5, **kw):
    riff(S, inst.choir, prog, rhythm, bars, origin=origin, octave=octave, vel=vel, dur=0.8, sa=0.4, vowel="a", voices=4, att=0.04,
         rel=0.25, shout=0.6, spread=0.9, **kw)


# ------------------------------------------------------------------ boss A
def mus_boss_a():
    S = Song("mus_boss_a", 150, 40, seed=301, irs=("hall", "room"))
    A = "Em Em C D Em Em F B"
    P = cyc(A, 4)
    # intro 0-3
    S.note(inst.strings, 40, 0, 16, 0.5, 0, 0.3, 0.0, att=1.5, rel=0.4, bright=0.8, voices=3)
    S.note(inst.strings, 52, 0, 16, 0.4, 0.2, 0.3, 0.0, att=1.5, rel=0.4, bright=0.9, voices=3)
    S.pat(inst.taiko, "X.......", (0, 4), vel=0.7, sa=0.25, sb=0.2, f=62)
    S.pat(inst.taiko, "X.x.x.x.", (2, 4), vel=0.8, sa=0.25, sb=0.2, f=62)
    S.pat(inst.metal, "x...x...", (1, 4), vel=0.3, sa=0.3, sb=0.1, f=600, ring=0.8)
    S.hit(inst.riser, S.bar(0), 0.6, 0, 0.4, 0.0, dur=4.0 * 4 * S.spb * 0.0 + 6.0)
    taiko_roll(S, S.bar(3) + 2, 2, 0.3, 0.95, 0.25, f=62, sa=0.25, sb=0.15)
    S.hit(inst.crash, S.bar(4), 0.6, 0, 0.4, 0.0, dur=3.0)
    # base ritmica 4-36
    S.pat(inst.taiko, "X.x.x.x.X.x.x.xx", (4, 36), vel=0.8, sa=0.2, sb=0.2, f=62)
    S.pat(inst.snare, "....x.......x...", (4, 36), vel=0.55, sa=0.2, sb=0.3, skip=set(range(20, 28)))
    S.pat(inst.hat, "x.x.x.x.x.x.x.x.", (4, 36), vel=0.28, sa=0.1, sb=0.0, pan_rand=0.5, skip=set(range(20, 28)))
    S.pat(inst.metal, "X.......", (4, 36), vel=0.3, sa=0.3, sb=0.1, f=640, ring=1.0, pan_rand=0.3)
    for (a, b) in ((4, 20), (28, 36)):
        S.arp(inst.strings, cyc(A, (b - a) // 8), [0, 0, 2, 0, 1, 0, 2, 0], a, lo=52, step=0.25, vel=0.33, sa=0.2, nlen=0.22,
              att=0.01, rel=0.06, bright=1.2, voices=2, pan_sweep=0.3, noise=0.01)
    for (a, b) in ((4, 20), (28, 36)):
        riff(S, inst.brass, A, "x.xx.xx.x.xx.x.x", (a, b), origin=4, octave=2, vel=0.55, dur=0.85, sa=0.15, att=0.02, rel=0.08,
             bright=0.8, voices=2, blat=0.4, grit=0.2)
        riff(S, inst.brass, A, "X.......x..o....", (a, b), origin=4, chord=True, lo=40, nmax=3, vel=0.5, dur=1.5, sa=0.25, att=0.03,
             rel=0.2, bright=1.0, pan=-0.2)
    # melodia
    M = mel("B4:1 E5:1 G5:2 | F#5:1 E5:1 B4:2 | C5:1 E5:1 G5:2 | A5:1 F#5:1 D5:2 | "
            "B4:1 E5:1 G5:1 B5:1 | A5:1 G5:1 E5:2 | F5:2 C5:1 A4:1 | B4:1 D#5:1 F#5:1 B5:1")
    S.play(inst.brass, M, 4, vel=0.85, sa=0.3, att=0.05, rel=0.2, bright=1.2, voices=3, legato=0.92, pan=0.1)
    S.play(inst.brass, M, 12, vel=0.85, sa=0.3, att=0.05, rel=0.2, bright=1.2, voices=3, legato=0.92, pan=0.1)
    S.play(inst.choir, M, 12, vel=0.55, sa=0.45, vowel="a", voices=5, att=0.08, rel=0.4, legato=0.92, shout=0.3)
    S.play(inst.violin, M, 12, transpose=12, vel=0.4, sa=0.35, legato=0.95, pan=0.35, bright=1.2)
    _chants(S, A, "x...x.x.", (12, 20), 4, octave=3, vel=0.45)
    S.chords(inst.strings, cyc(A, 1), 12, lo=52, nmax=3, vel=0.35, sa=0.3, att=0.3, rel=0.5, bright=0.9)
    S.chords(inst.strings, cyc(A, 1), 28, lo=52, nmax=3, vel=0.35, sa=0.3, att=0.3, rel=0.5, bright=0.9)
    # C: ruptura (20-28)
    SV = mel("B5:2 A5:2 | G5:2 F#5:2 | E5:2 G5:2 | F5:2 D#5:2 | B5:2 A5:2 | C6:2 B5:2 | A5:4 | B5:4")
    S.play(inst.violin, SV, 20, vel=0.9, sa=0.45, att=0.1, rel=0.3, depth=0.012, bright=1.1, legato=0.98, slide=0.3, pan=0.1)
    S.arp(inst.strings, cyc(A, 1), [2, 2, 2, 2], 20, lo=64, step=0.25, vel=0.22, sa=0.3, nlen=0.2, att=0.01, rel=0.05, bright=1.0, voices=2,
          pan_sweep=0.5)
    S.chords(inst.choir, cyc(A, 1), 20, lo=52, nmax=3, vel=0.4, sa=0.5, vowel="o", att=0.8, rel=1.0, voices=4, spread=0.9)
    S.pat(inst.taiko, "X.......x.......", (20, 28), vel=0.6, sa=0.3, sb=0.2, f=58)
    S.pat(inst.tom, "........ ........ ........ ..x.x.xx", (20, 28), vel=0.5, sa=0.2, sb=0.2, f=100)
    riff(S, inst.pluck, A, "x...x...", (20, 28), origin=4, octave=2, vel=0.9, dur=1.0, sa=0.2, bright=0.4, ring=1.0)
    # A' (28-36): organo + todo
    S.play(inst.brass, M, 28, vel=0.9, sa=0.3, att=0.05, rel=0.2, bright=1.3, voices=3, legato=0.92, pan=0.1)
    S.play(inst.brass, M, 28, transpose=-12, vel=0.6, sa=0.3, att=0.05, rel=0.2, bright=0.8, voices=2, legato=0.92, pan=-0.3)
    S.play(inst.choir, M, 28, vel=0.55, sa=0.45, vowel="a", voices=5, att=0.08, rel=0.4, legato=0.92, shout=0.3)
    S.play(inst.violin, M, 28, transpose=12, vel=0.5, sa=0.35, legato=0.95, pan=0.35, bright=1.2)
    _chants(S, A, "x...x.x.", (28, 36), 4, octave=3, vel=0.5)
    riff(S, inst.organ, A, "X.......", (28, 36), origin=4, chord=True, lo=40, nmax=3, vel=0.3, dur=3.0, sa=0.3, draw={1: 1.0, 2: 0.7, 3: 0.4, 4: 0.3},
         att=0.04, rel=0.3, trem=0.04, chiff=0.0)
    # outro 36-40
    S.chords(inst.brass, "Em Em Em Em", 36, lo=40, nmax=3, vel=0.55, sa=0.3, att=0.1, rel=0.4, bright=1.0)
    S.pat(inst.taiko, "X.x.x.x.", (36, 40), vel=0.8, sa=0.2, sb=0.2, f=62)
    S.pat(inst.snare, "x.x.x.x.", (38, 40), vel=0.45, sa=0.2, sb=0.3)
    for b in (4, 12, 28):
        S.hit(inst.crash, S.bar(b), 0.55, 0, 0.4, 0.0, dur=3.0)
    S.hit(inst.crash, S.bar(20), 0.4, 0, 0.4, 0.0, dur=3.0)
    for b in (11, 19, 27, 35):
        taiko_roll(S, S.bar(b) + 2, 2, 0.3, 0.9, 0.25, f=62, sa=0.2, sb=0.1)
    rev_crash_into(S, S.bar(20), 2.0, 0.4, riser=False)
    rev_crash_into(S, S.bar(28), 2.0, 0.45, riser=True)
    rev_crash_into(S, S.bar(40), 2.4, 0.45, riser=True)
    return S.render(comp=(-20, 2.2), sat=1.3)


# ------------------------------------------------------------------ boss B
def mus_boss_b():
    S = Song("mus_boss_b", 160, 44, seed=302, irs=("cathedral", "room"))
    A = "F#m F#m D E F#m F#m G C#"
    # intro: clave + clavicembalo
    S.arp(inst.harpsichord, cyc("F#m", 4), [0, 1, 2, 1, 0, 1, 2, 3], 0, lo=54, step=0.25, vel=0.45, sa=0.3, sb=0.1, pan_sweep=0.3)
    S.note(inst.organ, 30, 0, 16, 0.35, 0, 0.3, 0.0, draw={1: 1.0, 2: 0.6, 3: 0.3}, att=1.0, rel=0.5, trem=0.04, chiff=0)
    S.pat(inst.taiko, "X.......", (1, 4), vel=0.6, sa=0.25, sb=0.2, f=64)
    S.pat(inst.taiko, "X.x.x.x.", (3, 4), vel=0.8, sa=0.25, sb=0.2, f=64)
    taiko_roll(S, S.bar(3) + 2, 2, 0.3, 0.95, 0.25, f=64, sa=0.25, sb=0.15)
    # base 4-44
    sk = set(range(20, 28))
    S.pat(inst.taiko, "X..x..x.x..x..x.", (4, 44), vel=0.8, sa=0.2, sb=0.2, f=64)
    S.pat(inst.snare, "....x.......x...", (4, 44), vel=0.55, sa=0.2, sb=0.3, skip=sk)
    S.pat(inst.hat, "x.x.x.x.x.x.x.x.", (4, 44), vel=0.25, sa=0.1, sb=0.0, pan_rand=0.5, skip=sk)
    S.pat(inst.metal, "X.......", (4, 44), vel=0.3, sa=0.3, sb=0.1, f=450, ring=1.1, pan_rand=0.3)
    S.pat(inst.metal, "..x...x.", (12, 44), vel=0.12, sa=0.2, sb=0.1, f=2200, ring=0.2, thunk=0.0, pan_rand=0.7, skip=sk)
    for (a, b) in ((4, 20), (28, 44)):
        riff(S, inst.organ, A, "x..x..x.", (a, b), origin=4, chord=True, lo=42, nmax=3, vel=0.4, dur=0.9, sa=0.25,
             draw={1: 1.0, 2: 0.8, 3: 0.5, 4: 0.4, 6: 0.2}, att=0.01, rel=0.1, trem=0.03, chiff=0.1)
        riff(S, inst.brass, A, "x..x..x.", (a, b), origin=4, octave=2, vel=0.6, dur=0.9, sa=0.15, att=0.02, rel=0.08, bright=0.8, voices=3,
             blat=0.5, grit=0.35, pan=-0.2)
        S.arp(inst.strings, cyc(A, (b - a) // 8), [2, 2, 2, 2, 2, 2, 2, 2], a, lo=66, step=0.25, vel=0.22, sa=0.2, nlen=0.2, att=0.01, rel=0.05,
              bright=1.1, voices=2, pan_sweep=0.5)
    # melodia
    M = mel("C#5:1.5 F#5:.5 A5:1 C#6:1 | B5:1 A5:1 F#5:2 | A5:1.5 F#5:.5 D5:2 | G#5:1.5 E5:.5 B4:2 | "
            "C#5:1 F#5:1 A5:1 C#6:1 | D6:1 C#6:1 A5:2 | B5:1.5 G5:.5 D5:2 | G#5:1 F5:1 C#6:2")
    S.play(inst.brass, M, 4, vel=0.85, sa=0.3, att=0.05, rel=0.2, bright=1.2, voices=3, legato=0.92, pan=0.1)
    S.play(inst.violin, M, 4, vel=0.45, sa=0.35, legato=0.95, pan=0.3, bright=1.2)
    S.play(inst.brass, M, 12, vel=0.85, sa=0.3, att=0.05, rel=0.2, bright=1.2, voices=3, legato=0.92, pan=0.1)
    S.play(inst.choir, M, 12, vel=0.55, sa=0.5, vowel="a", voices=5, att=0.08, rel=0.4, legato=0.92, shout=0.3)
    S.play(inst.violin, M, 12, transpose=12, vel=0.45, sa=0.35, legato=0.95, pan=0.3, bright=1.2)
    S.chords(inst.choir, cyc(A, 1), 12, lo=54, nmax=3, vel=0.3, sa=0.5, vowel="o", att=0.4, rel=0.6, voices=4, spread=0.9)
    # C: ruptura gotica (20-28): clavicembalo + violin
    S.arp(inst.harpsichord, cyc(A, 1), [0, 1, 2, 1, 0, 1, 2, 3], 20, lo=54, step=0.25, vel=0.5, sa=0.3, sb=0.1, pan_sweep=0.3)
    SV = mel("F#5:2 A5:2 | C#6:2 B5:2 | A5:2 D6:2 | B5:2 G#5:2 | F#5:2 A5:2 | D6:2 E6:2 | F#6:2 D6:2 | C#6:4")
    S.play(inst.violin, SV, 20, vel=0.9, sa=0.45, att=0.1, rel=0.3, depth=0.012, bright=1.1, legato=0.98, slide=0.3)
    S.chords(inst.strings, cyc(A, 1), 20, lo=42, nmax=3, vel=0.4, sa=0.4, att=0.5, rel=0.6, bright=0.7)
    S.chords(inst.choir, cyc(A, 1), 20, lo=54, nmax=3, vel=0.35, sa=0.55, vowel="o", att=1.0, rel=1.2, voices=4, spread=0.9)
    S.pat(inst.taiko, "X.......x.......", (20, 28), vel=0.6, sa=0.3, sb=0.2, f=58)
    S.pat(inst.tom, "........ ........ ........ ..x.x.xx", (20, 28), vel=0.5, sa=0.2, sb=0.2, f=100)
    # A' y climax
    S.play(inst.brass, M, 28, vel=0.9, sa=0.3, att=0.05, rel=0.2, bright=1.3, voices=3, legato=0.92, pan=0.1)
    S.play(inst.choir, M, 28, vel=0.55, sa=0.5, vowel="a", voices=5, att=0.08, rel=0.4, legato=0.92, shout=0.3)
    S.play(inst.violin, M, 28, transpose=12, vel=0.5, sa=0.35, legato=0.95, pan=0.3, bright=1.2)
    S.play(inst.brass, M, 36, vel=0.95, sa=0.3, att=0.05, rel=0.2, bright=1.3, voices=3, legato=0.92, pan=0.1)
    S.play(inst.brass, M, 36, transpose=-12, vel=0.65, sa=0.3, att=0.06, rel=0.2, bright=0.8, voices=3, legato=0.92, pan=-0.3)
    S.play(inst.choir, M, 36, transpose=12, vel=0.6, sa=0.55, vowel="a", voices=6, att=0.08, rel=0.4, legato=0.92, shout=0.3)
    S.play(inst.violin, M, 36, transpose=12, vel=0.5, sa=0.35, legato=0.95, pan=0.3, bright=1.3)
    S.chords(inst.organ, cyc(A, 1), 36, lo=42, nmax=4, vel=0.3, sa=0.4, draw={1: 1.0, 2: 0.8, 3: 0.5, 4: 0.4, 6: 0.2}, att=0.1, rel=0.3,
             trem=0.04, chiff=0)
    _chants(S, A, "x..x..x.", (36, 44), 4, octave=3, vel=0.5)
    S.pat(inst.snare, "x.x.x.x.", (42, 44), vel=0.45, sa=0.2, sb=0.3)
    for b in (4, 12, 28, 36):
        S.hit(inst.crash, S.bar(b), 0.55, 0, 0.4, 0.0, dur=3.0)
    for b in (11, 19, 27, 35, 43):
        taiko_roll(S, S.bar(b) + 2, 2, 0.3, 0.9, 0.25, f=64, sa=0.2, sb=0.1)
    rev_crash_into(S, S.bar(20), 2.0, 0.4, riser=False)
    rev_crash_into(S, S.bar(28), 2.0, 0.45, riser=True)
    rev_crash_into(S, S.bar(44), 2.4, 0.45, riser=True)
    return S.render(comp=(-20, 2.2), sat=1.3)


# ------------------------------------------------------------------ final 1: gotica elegante
def mus_final_1():
    S = Song("mus_final_1", 108, 28, seed=401, irs=("hall", "chamber"))
    B8 = "Dm F Bb A Gm Dm/F E7 A"
    D4 = "Gm Em7b5 A7 A"
    P = LEIT_HARM + " " + B8 + " " + LEIT_HARM + " " + D4
    S.arp(inst.harpsichord, P, [0, 1, 2, 1, 0, 1, 2, 3], 0, lo=50, step=0.25, vel=0.4, sa=0.3, sb=0.1, pan_sweep=0.35)
    S.bassline(inst.strings, P, 0, octave=2, vel=0.55, sa=0.2, voices=2, att=0.25, rel=0.4, bright=0.6, legato=0.98)
    S.chords(inst.strings, P, 0, lo=50, nmax=3, vel=0.22, sa=0.4, att=1.0, rel=1.0, bright=0.6)
    S.play(inst.violin, leit(62), 0, vel=0.9, sa=0.4, att=0.1, rel=0.3, depth=0.011, bright=1.0, legato=0.97, slide=0.4, pan=0.1)
    MB = mel("F5:1 A5:1 D6:2 | C6:1 A5:1 F5:2 | D5:1 F5:1 Bb5:2 | C#6:1 E6:1 A5:2 | G5:1 Bb5:1 D6:2 | A5:1 F5:1 D5:2 | "
             "E5:1 G#5:1 B5:1 D6:1 | E6:2 A5:2")
    S.play(inst.violin, MB, 8, vel=0.95, sa=0.4, att=0.08, rel=0.3, depth=0.013, bright=1.1, legato=0.96, slide=0.5, pan=0.1)
    S.play(inst.strings, MB, 8, transpose=-12, vel=0.4, sa=0.4, voices=2, att=0.15, rel=0.4, bright=0.7, legato=0.96, pan=-0.3)
    S.chords(inst.organ, " ".join([B8]), 8, lo=50, nmax=3, vel=0.22, sa=0.4, draw={1: 1.0, 2: 0.5, 3: 0.3}, att=0.2, rel=0.4, trem=0.04, chiff=0)
    S.arp(inst.strings, B8, [1, 1, 1, 1], 8, lo=62, step=0.25, vel=0.18, sa=0.3, nlen=0.2, att=0.01, rel=0.05, bright=1.0, voices=1, pan_sweep=0.5)
    S.play(inst.violin, leit(62), 16, vel=0.95, sa=0.4, att=0.1, rel=0.3, depth=0.013, bright=1.1, legato=0.97, slide=0.4, pan=0.15)
    S.play(inst.violin, leit(65), 16, vel=0.45, sa=0.4, att=0.1, rel=0.3, depth=0.011, bright=1.0, legato=0.97, pan=-0.25)
    S.play(inst.strings, leit(50), 16, vel=0.6, sa=0.4, voices=3, att=0.12, rel=0.4, bright=0.8, legato=0.97, pan=-0.3)
    S.chords(inst.organ, LEIT_HARM, 16, lo=50, nmax=3, vel=0.28, sa=0.4, draw={1: 1.0, 2: 0.7, 3: 0.5, 4: 0.3}, att=0.15, rel=0.4, trem=0.04, chiff=0)
    S.chords(inst.choir, LEIT_HARM, 16, lo=57, nmax=3, vel=0.28, sa=0.55, vowel="o", att=0.8, rel=1.0, voices=4, spread=0.9)
    S.pat(inst.timpani, "X...x...", (16, 24), vel=0.5, sa=0.3, sb=0.2, f=73.4)
    S.pat(inst.timpani, "X.......", (8, 16), vel=0.3, sa=0.3, sb=0.2, f=73.4)
    # D: tension
    S.play(inst.violin, mel("A5:4 | G#5:4 | E6:2 D6:2 | C#6:2 A5:2"), 24, vel=0.95, sa=0.45, att=0.3, rel=0.3, depth=0.015, bright=1.1,
           legato=0.99, pan=0.1)
    S.chords(inst.strings, D4, 24, lo=50, nmax=3, vel=0.4, sa=0.4, att=0.6, rel=0.8, bright=0.9)
    S.chords(inst.choir, D4, 24, lo=57, nmax=3, vel=0.32, sa=0.55, vowel="a", att=0.8, rel=1.0, voices=4)
    S.pat(inst.timpani, "X...x...", (24, 28), vel=0.55, sa=0.3, sb=0.2, f=73.4)
    taiko_roll(S, S.bar(26) + 1, 7, 0.2, 0.9, 0.25, fn=inst.timpani, f=73.4)
    for b in (0, 8, 16, 24):
        toll(S, S.bar(b), "D3", 0.5, decay=6.0, sa=0.5)
    S.hit(inst.crash, S.bar(16), 0.4, 0, 0.4, 0.0, dur=3.0)
    S.hit(inst.crash, S.bar(8), 0.3, 0, 0.4, 0.0, dur=3.0)
    rev_crash_into(S, S.bar(28), 3.0, 0.45, riser=True)
    return S.render(comp=(-22, 2.0), sat=1.15)


# ------------------------------------------------------------------ final 2: bestial
def mus_final_2():
    S = Song("mus_final_2", 132, 36, seed=402, irs=("cave", "room"))
    A = "Dm Dm Eb Eb Dm Dm Ab A"
    CL = "Dcl Dcl Ebcl Ebcl Dcl Dcl Abcl Acl"
    sk = set(range(20, 28))
    # guerra
    S.pat(inst.taiko, "X.x.X.x.X.x.X.xx", (0, 36), vel=0.85, sa=0.2, sb=0.2, f=52, skip=set(range(20, 28)))
    S.pat(inst.tom, "..x...x...x...x.", (4, 36), vel=0.5, sa=0.2, sb=0.2, f=100, pan=-0.4, skip=sk)
    S.pat(inst.tom, "....x...x...x...", (4, 36), vel=0.5, sa=0.2, sb=0.2, f=78, pan=0.4, skip=sk)
    S.pat(inst.snare, "....X.......X.x.", (4, 36), vel=0.6, sa=0.2, sb=0.3, snap=1.0, skip=sk)
    S.pat(inst.metal, "X.......", (0, 36), vel=0.35, sa=0.3, sb=0.1, f=420, ring=1.0, pan_rand=0.3)
    S.pat(inst.hat, "xxxxxxxxxxxxxxxx", (12, 36), vel=0.16, sa=0.1, sb=0.0, pan_rand=0.6, skip=sk)
    for b in range(2, 36, 4):
        S.hit(inst.chain, S.bar(b) + 3, 0.5, 0.0, 0.2, 0.0)
    # taiko lento en la ruptura
    S.pat(inst.taiko, "X.......x.......", (20, 28), vel=0.7, sa=0.3, sb=0.2, f=50)
    # riff de metal gutural
    for (a, b) in ((0, 20), (28, 36)):
        riff(S, inst.brass, A, "x.xxx.xx x.xx.xxx", (a, b), origin=4, octave=2, offsets=(0, 0, 1, 0, 6, 0, 1, 3), vel=0.6,
             dur=0.8, sa=0.15, att=0.015, rel=0.06, bright=0.8, voices=3, blat=0.4, grit=0.7)
    S.bassline(inst.sub, "Dm Dm Ab A " + cyc(A, 4), 0, octave=2, vel=0.2, sa=0.0, att=0.05, rel=0.2)
    # clusters disonantes
    for (a, b) in ((4, 20), (28, 36)):
        riff(S, inst.strings, CL, "X.......X.....o.", (a, b), origin=4, chord=True, lo=62, nmax=4, vel=0.4, dur=0.5, sa=0.3, att=0.02,
             rel=0.15, bright=1.2, voices=3)
    S.chords(inst.strings, cyc(CL, 1), 20, lo=50, nmax=4, vel=0.4, sa=0.45, att=3.0, rel=1.0, bright=0.7)
    # leitmotiv deformado
    LT = leit_twist(50)
    S.play(inst.brass, LT, 12, vel=0.85, sa=0.35, att=0.08, rel=0.25, bright=0.9, voices=3, grit=0.5, legato=0.95, pan=0.0)
    S.play(inst.violin, leit_twist(74), 12, vel=0.5, sa=0.35, depth=0.02, slide=2.0, bright=1.3, legato=0.95, pan=0.3)
    S.play(inst.brass, LT, 28, vel=0.95, sa=0.35, att=0.06, rel=0.25, bright=1.0, voices=3, grit=0.6, legato=0.95, pan=0.0)
    S.play(inst.brass, leit_twist(62), 28, vel=0.7, sa=0.35, att=0.06, rel=0.25, bright=1.2, voices=3, grit=0.6, legato=0.95, pan=0.3)
    S.play(inst.violin, leit_twist(74), 28, vel=0.55, sa=0.35, depth=0.02, slide=2.0, bright=1.3, legato=0.95, pan=-0.3)
    S.play(inst.choir, leit_twist(50), 28, vel=0.55, sa=0.5, vowel="a", voices=5, att=0.1, rel=0.4, legato=0.95, vib=0.02, shout=0.8, spread=0.9)
    # coro bestial
    S.chords(inst.choir, A, 12, lo=50, nmax=2, vel=0.4, sa=0.5, vowel="o", vowel2="a", att=0.5, rel=0.8, voices=5, vib=0.018, shout=0.8, spread=0.9)
    _chants(S, A, "x...x.x.", (28, 36), 4, octave=3, vel=0.55)
    # chillidos
    rng = np.random.default_rng(402)
    for b in (6, 9, 14, 17, 22, 25, 29, 33):
        S.note(inst.violin, 81 + int(rng.choice([0, 1, 2])), S.bar(b) + float(rng.choice([0, 1, 2])), 2.0, 0.5, float(rng.uniform(-0.8, 0.8)), 0.4, 0.0,
               depth=0.025, slide=3.0, bright=1.4, att=0.05)
    for b in (0, 12, 20, 28):
        S.hit(inst.thunder, S.bar(b), 0.55, 0, 0.3, 0.1, dur=4.0)
    for b in (4, 12, 28):
        S.hit(inst.crash, S.bar(b), 0.5, 0, 0.4, 0.0, dur=3.0)
    for b in (11, 19, 27, 35):
        taiko_roll(S, S.bar(b) + 2, 2, 0.3, 0.95, 0.25, f=52, sa=0.2, sb=0.1)
    S.hit(inst.sweep_saw, S.bar(24), 0.5, 0, 0.3, 0.0, dur=S.bar(4) * S.spb, f0=70, f1=420, cut=1400)
    rev_crash_into(S, S.bar(28), 2.4, 0.5, riser=True)
    rev_crash_into(S, S.bar(36), 2.4, 0.5, riser=True)
    return S.render(comp=(-19, 2.4), sat=1.5)


# ------------------------------------------------------------------ final 3: cosmico
def mus_final_3():
    S = Song("mus_final_3", 150, 40, seed=403, irs=("cathedral", "hall"))
    A8 = "Dm Bb F C Dm Bb Gm A"
    B8 = "Bb F C Dm Bb F Gm A"
    C8 = LEIT_HARM
    D8 = LEIT_HARM_MAJOR
    E8 = "Bb F Gm A Bb F Gm A"
    P = " ".join([A8, B8, C8, D8, E8])
    DM = {2, 4, 5, 7, 9, 10, 0, 1, 11}
    # cosmos
    S.arp(inst.eplucked_fm, P, [0, 1, 2, 3, 2, 1, 2, 4], 0, lo=62, step=0.5, vel=0.3, sa=0.5, sb=0.1, pan_sweep=0.9, decay=0.9, idx=2.5)
    sparkle(S, 0, 40, DM, 0.55, inst.glass, 84, 105, 0.22, 0.6, seed=31, decay=2.4)
    S.note(inst.drone_saw, 38, S.bar(0), 64, vel=0.4, sa=0.3, att=3.0, rel=3.0, cut=300)
    S.note(inst.drone_saw, 38, S.bar(20), 64, vel=0.4, sa=0.3, att=3.0, rel=3.0, cut=300)
    S.chords(inst.strings, P, 0, lo=50, nmax=4, vel=0.35, sa=0.45, att=1.2, rel=1.2, bright=0.8)
    S.bassline(inst.organ, P, 8, octave=2, vel=0.4, sa=0.3, draw={1: 1.0, 2: 0.6, 3: 0.3}, att=0.1, rel=0.4, trem=0.02, chiff=0)
    S.arp(inst.strings, P[:0] + " ".join([B8, C8, D8, E8]), [0, 1, 2, 1], 8, lo=57, step=0.5, vel=0.28, sa=0.25, nlen=0.45, att=0.01, rel=0.06,
          bright=1.1, voices=3, pan_sweep=0.4)
    # coro gigante
    S.chords(inst.choir, " ".join([B8, C8, D8, E8]), 8, lo=50, nmax=3, vel=0.4, sa=0.6, vowel="a", vowel2="o", att=0.9, rel=1.2, voices=6, spread=1.0)
    S.chords(inst.choir, " ".join([C8, D8]), 16, lo=62, nmax=3, vel=0.35, sa=0.6, vowel="a", att=0.8, rel=1.2, voices=6, spread=1.0)
    # leitmotiv: C (16-24) grande y menor; D (24-32) mayor triunfal
    L = leit(62)
    S.play(inst.brass, L, 16, vel=0.9, sa=0.35, att=0.07, rel=0.3, bright=1.2, voices=3, legato=0.95, pan=0.1)
    S.play(inst.brass, L, 16, transpose=-12, vel=0.6, sa=0.35, att=0.08, rel=0.3, bright=0.7, voices=3, legato=0.95, pan=-0.3)
    S.play(inst.choir, L, 16, vel=0.65, sa=0.6, vowel="a", voices=6, att=0.12, rel=0.5, legato=0.97, spread=1.0)
    S.play(inst.violin, L, 16, transpose=12, vel=0.5, sa=0.4, depth=0.012, legato=0.97, pan=0.3, bright=1.2)
    S.chords(inst.organ, C8, 16, lo=38, nmax=4, vel=0.3, sa=0.4, draw={1: 1.0, 2: 0.8, 3: 0.5, 4: 0.4, 6: 0.2}, att=0.1, rel=0.3, trem=0.04, chiff=0)
    LM = leit(62, major=True)
    S.play(inst.brass, LM, 24, vel=0.95, sa=0.35, att=0.07, rel=0.3, bright=1.3, voices=3, legato=0.95, pan=0.1)
    S.play(inst.brass, LM, 24, transpose=-12, vel=0.65, sa=0.35, att=0.08, rel=0.3, bright=0.8, voices=3, legato=0.95, pan=-0.3)
    S.play(inst.choir, LM, 24, transpose=12, vel=0.65, sa=0.6, vowel="a", voices=6, att=0.12, rel=0.5, legato=0.97, spread=1.0)
    S.play(inst.choir, LM, 24, vel=0.5, sa=0.6, vowel="o", voices=6, att=0.12, rel=0.5, legato=0.97, spread=1.0, pan=0.0)
    S.play(inst.violin, LM, 24, transpose=24, vel=0.5, sa=0.4, depth=0.012, legato=0.97, pan=0.3, bright=1.2)
    S.chords(inst.organ, D8, 24, lo=38, nmax=4, vel=0.34, sa=0.4, draw={1: 1.0, 2: 0.8, 3: 0.6, 4: 0.5, 6: 0.3, 8: 0.2}, att=0.1, rel=0.3, trem=0.04, chiff=0)
    S.chords(inst.brass, D8, 24, lo=50, nmax=3, vel=0.4, sa=0.35, att=0.2, rel=0.3, bright=1.0, voices=3)
    # percusion
    S.pat(inst.timpani, "X...x...", (0, 8), vel=0.4, sa=0.3, sb=0.2, f=73.4)
    S.pat(inst.taiko, "X.x.x.x.", (8, 16), vel=0.7, sa=0.2, sb=0.2, f=62)
    S.pat(inst.snare, "........ ........ ........ x.x.xxxx", (8, 16), vel=0.4, sa=0.2, sb=0.3)
    S.pat(inst.taiko, "X.x.X.x.X.x.X.xx", (16, 32), vel=0.85, sa=0.2, sb=0.2, f=58)
    S.pat(inst.snare, "....x.......x...", (16, 32), vel=0.55, sa=0.2, sb=0.3)
    S.pat(inst.hat, "xxxxxxxxxxxxxxxx", (20, 32), vel=0.15, sa=0.1, sb=0.0, pan_rand=0.6)
    S.pat(inst.metal, "X.......", (16, 32), vel=0.3, sa=0.3, sb=0.1, f=520, ring=1.0, pan_rand=0.3)
    S.pat(inst.timpani, "X...x...", (32, 38), vel=0.5, sa=0.3, sb=0.2, f=73.4)
    for b in (0, 8, 16, 24, 32):
        S.hit(inst.crash, S.bar(b), 0.5, 0, 0.5, 0.0, dur=3.0)
    for b in (7, 15, 23, 31, 39):
        taiko_roll(S, S.bar(b) + 2, 2, 0.3, 0.95, 0.25, f=62, sa=0.2, sb=0.1)
    for b in (8, 16, 24, 32, 40):
        rev_crash_into(S, S.bar(b), 2.4, 0.4, riser=(b in (16, 24, 40)))
    for b in (0, 16, 24):
        toll(S, S.bar(b), "D3", 0.55, decay=7.0, sa=0.5)
    S.hit(inst.thunder, S.bar(16), 0.4, 0, 0.3, 0.1, dur=4.0)
    return S.render(comp=(-20, 2.2), sat=1.25)


TRACKS = {
    "mus_boss_a": mus_boss_a, "mus_boss_b": mus_boss_b, "mus_final_1": mus_final_1, "mus_final_2": mus_final_2,
    "mus_final_3": mus_final_3,
}
