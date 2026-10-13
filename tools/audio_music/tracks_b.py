"""tracks_b.py - musica de los 8 biomas."""
import numpy as np
import inst
from song import *
from arr import *

E_PHRYG = {4, 5, 7, 9, 11, 0, 2}
B_MIN = {11, 1, 2, 4, 6, 7, 9}
E_DOR = {4, 6, 7, 9, 11, 1, 2}


# ------------------------------------------------------------------ catacumbas
def mus_catacumbas():
    S = Song("mus_catacumbas", 60, 16, seed=201, irs=("cave", "room"))
    H1 = "Em Em F Em Em Dm F Em"
    H2 = "Em C F Em Em Dm F B"
    P = H1 + " " + H2
    for b in (0, 8):
        S.note(inst.drone_saw, 40, S.bar(b), 32, vel=0.5, sa=0.3, att=3.0, rel=3.0, cut=230)
        S.note(inst.drone_saw, 47, S.bar(b) + 8, 24, vel=0.28, sa=0.3, att=3.0, rel=3.0, cut=300, pan=0.3)
    S.chords(inst.strings, P, 0, lo=52, nmax=3, vel=0.3, sa=0.5, att=2.0, rel=2.0, bright=0.4)
    M = mel("E3:2 F3:1 G3:1 | F3:2 E3:2 | A3:2 G3:1 F3:1 | G3:3 E3:1 | E3:2 B3:2 | A3:1 G3:1 F3:2 | G3:2 A3:1 B3:1 | E4:4")
    S.play(inst.strings, M, 0, vel=0.95, sa=0.45, voices=2, att=0.35, rel=0.8, vib=0.008, bright=0.7, legato=0.97, pan=-0.15)
    S.play(inst.strings, M, 8, transpose=12, vel=0.8, sa=0.5, voices=2, att=0.3, rel=0.8, vib=0.009, bright=0.8, legato=0.97, pan=0.1)
    S.play(inst.strings, M, 8, transpose=0, vel=0.5, sa=0.4, voices=2, att=0.35, rel=0.8, vib=0.008, bright=0.6, legato=0.97, pan=-0.3)
    S.play(inst.choir, M, 8, transpose=12, vel=0.5, sa=0.6, vowel="o", vowel2="u", voices=4, att=0.5, rel=1.0, legato=1.0, vib=0.007)
    S.chords(inst.choir, P, 4, lo=52, nmax=3, vel=0.35, sa=0.6, vowel="u", att=1.8, rel=2.0, voices=3, spread=0.9)
    for b in (0, 4, 8, 12):
        toll(S, S.bar(b), "E3", 0.55, decay=7.0, sa=0.55)
    toll(S, S.bar(3) + 2, "B4", 0.28, decay=5.0, sa=0.6, pan=0.4)
    toll(S, S.bar(9) + 3, "F5", 0.25, decay=5.0, sa=0.6, pan=-0.4)
    toll(S, S.bar(13) + 2, "E5", 0.25, decay=5.0, sa=0.6, pan=0.3)
    # sub pulso lento: lub-dub cada 2 tiempos
    S.pat(inst.kick, "x.o.....x.o.....", (0, 16), vel=0.45, sa=0.15, sb=0.0, f=46, decay=0.55, sweep=1.0, click=0.05)
    S.pat(inst.taiko, "X.......", (8, 16), vel=0.38, sa=0.3, sb=0.2, f=55)
    for b in (3, 11):
        S.hit(inst.chain, S.bar(b) + 1.5, 0.5, 0.3, 0.3, 0.1)
    for b in (1, 5, 6, 10, 14):
        S.hit(inst.metal, S.bar(b) + 2.5, 0.25, -0.5, 0.4, 0.0, f=3300, ring=0.25, thunk=0.0)
    whispers(S, 0, 16, 5, vel=0.7, seed=3)
    S.hit(inst.wind, S.bar(0), 0.5, 0, 0.3, 0.0, dur=9.0, lo=150, hi=900)
    S.hit(inst.wind, S.bar(8), 0.5, 0, 0.3, 0.0, dur=9.0, lo=150, hi=900)
    rev_crash_into(S, S.bar(16), 3.0, 0.4, riser=False)
    return S.render(comp=(-22, 2.0), sat=1.1)


# ------------------------------------------------------------------ forja
def mus_forja():
    S = Song("mus_forja", 104, 24, seed=202, irs=("chamber", "short"))
    A = "Gm Gm Ab Gm Gm Ab F D"
    P = cyc(A, 3)
    # percusion industrial
    S.pat(inst.taiko, "X.....x.x.....x.", (0, 24), vel=0.8, sa=0.2, sb=0.15, f=56)
    S.pat(inst.kick, "x.......x.......", (0, 24), vel=0.6, sa=0.0, sb=0.0, f=50, decay=0.3)
    S.pat(inst.metal, "....X.......X...", (0, 24), vel=0.55, sa=0.25, sb=0.2, f=700, ring=1.3, pan_rand=0.1)
    S.pat(inst.metal, "x.x.x.x.x.x.x.x.", (4, 24), vel=0.12, sa=0.15, sb=0.1, f=2700, ring=0.2, thunk=0.0, pan_rand=0.7)
    S.pat(inst.snare, "....x.......x...", (8, 24), vel=0.5, sa=0.2, sb=0.3, snap=1.0)
    S.pat(inst.hat, "..x...x...x...x.", (8, 24), vel=0.3, sa=0.1, sb=0.0, pan_rand=0.5)
    for b in range(0, 24, 4):
        S.hit(inst.chain, S.bar(b) + 3, 0.45, 0.4, 0.2, 0.0)
    # ostinato de metales graves
    riff(S, inst.brass, A, "x.xx.xx.x.xx.x.x", (0, 24), origin=0, octave=2, offsets=(0, 0, 0, 1, 0, 0, 0, 0), vel=0.55, dur=0.85,
         sa=0.15, att=0.02, rel=0.08, bright=0.8, voices=2, blat=0.4)
    riff(S, inst.strings, A, "x.xx.xx.x.xx.x.x", (8, 24), origin=0, octave=3, vel=0.4, dur=0.6, sa=0.1, att=0.01, rel=0.05,
         bright=1.1, voices=2, pan=0.3)
    S.bassline(inst.sub, P, 0, octave=2, vel=0.22, sa=0.0, att=0.05, rel=0.2)
    # acordes de metal
    riff(S, inst.brass, A, "X.......x..o....", (8, 24), origin=0, chord=True, lo=43, nmax=3, vel=0.5, dur=1.6, sa=0.25,
         att=0.03, rel=0.2, bright=1.0, pan=-0.2)
    # melodia
    M = mel("D5:1 D5:.5 Eb5:.5 D5:1 Bb4:1 | G4:2 Bb4:1 D5:1 | Eb5:1 Eb5:.5 F5:.5 Eb5:1 C5:1 | Bb4:2 G4:1 A4:1 | "
            "D5:1 D5:.5 Eb5:.5 F5:1 G5:1 | Eb5:2 C5:1 Eb5:1 | C5:1 A4:1 F4:1 A4:1 | F#4:1 A4:1 D5:2")
    S.play(inst.brass, M, 8, vel=0.8, sa=0.3, att=0.05, rel=0.2, bright=1.2, voices=3, legato=0.92, pan=0.1)
    S.play(inst.brass, M, 16, vel=0.8, sa=0.3, att=0.05, rel=0.2, bright=1.2, voices=3, legato=0.92, pan=0.1)
    S.play(inst.brass, M, 16, transpose=-12, vel=0.55, sa=0.3, att=0.06, rel=0.2, bright=0.7, voices=2, legato=0.92, pan=-0.3)
    S.play(inst.violin, M, 16, transpose=12, vel=0.4, sa=0.3, legato=0.95, pan=0.4, bright=1.1)
    S.chords(inst.choir, A, 16, lo=50, nmax=3, vel=0.4, sa=0.35, vowel="o", att=0.4, rel=0.8, voices=4, spread=0.9, shout=0.5)
    S.chords(inst.choir, A, 8, lo=50, nmax=2, vel=0.25, sa=0.35, vowel="o", att=0.6, rel=0.8, voices=3, spread=0.9)
    for b in (0, 8, 16):
        S.hit(inst.crash, S.bar(b), 0.45, 0, 0.3, 0.0, dur=3.0)
    for b in (7, 15, 23):
        taiko_roll(S, S.bar(b) + 2, 2, 0.3, 0.9, 0.25, f=56, sa=0.2, sb=0.1)
    rev_crash_into(S, S.bar(8), 2.4, 0.4, riser=False, rv=0.3)
    rev_crash_into(S, S.bar(16), 2.4, 0.45, riser=False, rv=0.3)
    rev_crash_into(S, S.bar(24), 2.6, 0.45, riser=True, rv=0.3)
    return S.render(comp=(-20, 2.2), sat=1.4)


# ------------------------------------------------------------------ helado
def mus_helado():
    S = Song("mus_helado", 72, 18, seed=203, irs=("ice", "plate"))
    H = "Bm Gmaj7 Dmaj7 Asus2 Gmaj7 F#m7"
    P = cyc(H, 3)
    S.chords(inst.fm_pad, P, 0, lo=59, nmax=4, vel=0.55, sa=0.5, ratio=2.0, idx=1.3, att=1.5, rel=2.5, detune=5)
    S.chords(inst.strings, P, 0, lo=47, nmax=3, vel=0.3, sa=0.5, att=2.0, rel=2.0, bright=0.4)
    S.chords(inst.choir, P, 6, lo=71, nmax=3, vel=0.22, sa=0.6, vowel="u", att=2.0, rel=2.5, voices=3, spread=0.9)
    S.bassline(inst.organ, P, 0, octave=2, vel=0.25, sa=0.3, draw={1: 1.0, 2: 0.5, 3: 0.2}, att=0.6, rel=1.0, trem=0.02, chiff=0)
    # arpegios de celesta
    S.arp(inst.celesta, P, [0, 2, 1, 3, 2, 4, 3, 1], 0, lo=71, step=0.5, vel=0.42, sa=0.55, sb=0.15, pan_sweep=0.6, decay=1.5)
    S.arp(inst.glass, P, [0, None, 2, None, 1, None, 3, None], 6, lo=83, step=1.0, vel=0.35, sa=0.6, sb=0.1, pan_sweep=0.7, decay=2.5)
    # melodia
    M = mel("F#5:2 D5:1 E5:1 | B4:2 D5:1 F#5:1 | A5:2 F#5:1 E5:1 | E5:2 B4:1 A4:1 | D5:1.5 E5:.5 F#5:1 G5:1 | F#5:3 r:1")
    S.play(inst.glass, M, 0, vel=0.7, sa=0.6, decay=3.0, legato=1.0, pan=0.1)
    S.play(inst.celesta, M, 6, vel=0.6, sa=0.6, decay=1.8, pan=-0.2)
    S.play(inst.glass, M, 6, transpose=12, vel=0.4, sa=0.6, decay=2.5, pan=0.3)
    S.play(inst.violin, M, 12, vel=0.5, sa=0.6, att=0.25, rel=0.5, depth=0.007, bright=0.7, legato=0.97)
    S.play(inst.glass, M, 12, transpose=12, vel=0.5, sa=0.6, decay=3.0, pan=0.2)
    for b in (0, 6, 12):
        S.hit(inst.timpani, S.bar(b), 0.5, 0, 0.4, 0.2, f=61.7)
        S.hit(inst.metal, S.bar(b), 0.3, 0.3, 0.6, 0.0, f=1900, ring=1.8, thunk=0.0, click=0.3)
    S.pat(inst.hat, "..x...x...x...x.", (3, 18), vel=0.22, sa=0.3, sb=0.1, pan_rand=0.7)
    for b in (0, 6, 12):
        S.hit(inst.wind, S.bar(b), 0.6, 0, 0.4, 0.0, dur=10.0, lo=300, hi=2500)
    sparkle(S, 0, 18, B_MIN, 0.35, inst.glass, 88, 104, 0.25, 0.6, seed=7, decay=2.8)
    S.hit(inst.crash, S.bar(6), 0.25, 0, 0.6, 0.0, dur=3.0)
    rev_crash_into(S, S.bar(18), 3.0, 0.35, riser=True, rv=0.5)
    return S.render(comp=(-24, 2.0), sat=1.05)


# ------------------------------------------------------------------ vacio
def mus_vacio():
    S = Song("mus_vacio", 50, 12, seed=204, irs=("void", "plate"))
    CL = [[53, 54, 59, 60], [52, 53, 58, 61], [53, 56, 59, 64], [54, 55, 60, 65], [53, 54, 57, 63], [52, 55, 59, 60]]
    for i, ch in enumerate(CL):
        for m in ch:
            S.note(inst.fm_pad, m, S.bar(i * 2), 8.5, 0.42, 0.0, 0.6, 0.0, ratio=1.4142 if i % 2 == 0 else 1.7321, idx=2.4,
                   att=2.2, rel=3.0, detune=6, lfo=0.5)
    S.note(inst.drone_saw, 41, S.bar(0), 24, vel=0.5, sa=0.3, att=4.0, rel=4.0, cut=200)
    S.note(inst.drone_saw, 41, S.bar(6), 24, vel=0.5, sa=0.3, att=4.0, rel=4.0, cut=200)
    S.note(inst.drone_saw, 42, S.bar(3), 20, vel=0.28, sa=0.4, att=4.0, rel=4.0, cut=260, pan=0.4)
    S.note(inst.drone_saw, 54, S.bar(8), 12, vel=0.22, sa=0.4, att=3.0, rel=4.0, cut=500, pan=-0.4)
    # coro disonante
    for i in range(2, 6):
        for j, m in enumerate(CL[i][:3]):
            S.note(inst.choir, m - 12, S.bar(i * 2), 8, 0.28, 0.0, 0.7, 0.0, vowel="u", att=3.0, rel=3.0, voices=2, spread=0.9, vib=0.01)
    # arpegios disonantes de FM etérea
    rng = np.random.default_rng(55)
    PS = [0, 1, 4, 6, 7, 10]
    for k in range(int(12 * 4 * 3)):
        if k < 6 or rng.random() < 0.3:
            continue
        beat = k / 3.0
        m = 41 + int(rng.choice(PS)) + 12 * int(rng.choice([1, 2, 2, 3, 3]))
        S.note(inst.eplucked_fm, m, beat, 1, 0.3 * rng.uniform(0.6, 1.0), rng.uniform(-0.9, 0.9), 0.7, 0.1, decay=1.2, idx=3.5)
    whispers(S, 0, 12, 12, vel=0.8, seed=11, sa=0.6)
    toll(S, S.bar(1) + 2, "Gb4", 0.35, decay=7.0, sa=0.7, dark=0.4)
    toll(S, S.bar(5), "B4", 0.3, decay=7.0, sa=0.7, pan=0.5, dark=0.4)
    toll(S, S.bar(9) + 3, "E5", 0.3, decay=7.0, sa=0.7, pan=-0.5, dark=0.4)
    S.pat(inst.kick, "x.o.....", (5, 12), vel=0.35, sa=0.3, sb=0.0, f=42, decay=0.6, sweep=1.0, click=0.0)
    for b in (0, 4, 8):
        S.hit(inst.wind, S.bar(b), 0.8, 0, 0.5, 0.0, dur=10.0, lo=80, hi=900)
    S.hit(inst.thunder, S.bar(6), 0.3, 0, 0.5, 0.1, dur=5.0, crack=0.0)
    S.hit(inst.sweep_saw, S.bar(10), 0.5, 0, 0.4, 0.0, dur=6.0, f0=60, f1=500, cut=900)
    rev_crash_into(S, S.bar(12), 4.0, 0.35, riser=True, rv=0.6)
    return S.render(comp=(-26, 1.8), sat=1.05)


# ------------------------------------------------------------------ bosque
def mus_bosque():
    S = Song("mus_bosque", 96, 24, seed=205, irs=("hall", "room"))
    B8 = "Em G D A Em G D Bm"
    P = cyc(B8, 3)
    S.note(inst.drone_saw, 40, S.bar(0), 48, vel=0.35, sa=0.2, att=2.0, rel=2.0, cut=320, grit=0.4)
    S.note(inst.drone_saw, 40, S.bar(12), 48, vel=0.35, sa=0.2, att=2.0, rel=2.0, cut=320, grit=0.4)
    riff(S, inst.pluck, B8, "x..x..x.", (0, 24), octave=2, vel=0.9, dur=1.0, sa=0.15, sb=0.05, bright=0.35, ring=1.2, pan=-0.2)
    riff(S, inst.pluck, B8, "..o..o.x", (4, 24), octave=3, vel=0.4, dur=1.0, sa=0.15, sb=0.05, bright=0.5, ring=0.8, pan=0.3)
    S.arp(inst.marimba, P, [0, 2, 1, 2, 0, 2, 1, None], 0, lo=64, step=0.5, vel=0.45, sa=0.3, sb=0.1, pan_sweep=0.5, decay=0.45)
    S.chords(inst.strings, P, 0, lo=52, nmax=3, vel=0.25, sa=0.4, att=1.5, rel=1.5, bright=0.5)
    S.chords(inst.choir, P, 8, lo=52, nmax=3, vel=0.28, sa=0.5, vowel="u", att=1.5, rel=1.8, voices=2, spread=0.9)
    S.pat(inst.tom, "X..x..x.", (0, 24), vel=0.5, sa=0.2, sb=0.2, f=92, decay=0.3)
    S.pat(inst.tom, "........ ........ ........ ......xx", (0, 24), vel=0.3, sa=0.2, sb=0.2, f=130, decay=0.2)
    S.pat(inst.metal, "..x...x.", (2, 24), vel=0.35, sa=0.2, sb=0.1, f=1500, ring=0.12, thunk=0.0, click=1.0, pan_rand=0.4)
    S.pat(inst.shaker, "xxxxxxxx", (4, 24), vel=0.3, sa=0.1, sb=0.1, pan_rand=0.5)
    M = mel("B4:1 E5:1.5 D5:.5 B4:1 | G4:1 B4:1 D5:2 | A4:1.5 F#4:.5 A4:1 D5:1 | C#5:2 B4:1 A4:1 | "
            "B4:1 E5:1.5 G5:.5 F#5:1 | E5:1 D5:1 B4:2 | A4:1 B4:1 A4:1 F#4:1 | B4:3 r:1")
    S.play(inst.flute, M, 8, vel=0.8, sa=0.45, att=0.07, rel=0.2, breath=0.22, vib=0.006, legato=0.95, pan=0.1)
    S.play(inst.flute, M, 16, vel=0.75, sa=0.45, att=0.07, rel=0.2, breath=0.22, vib=0.006, legato=0.95, pan=0.1)
    S.play(inst.marimba, M, 16, transpose=12, vel=0.5, sa=0.4, pan=-0.3, decay=0.5)
    S.play(inst.panflute, M, 16, transpose=-12, vel=0.35, sa=0.5, legato=0.95, pan=-0.4)
    sparkle(S, 0, 24, E_DOR, 0.25, inst.glass, 84, 100, 0.22, 0.5, seed=21, decay=2.0)
    S.hit(inst.wind, S.bar(0), 0.5, 0, 0.3, 0.0, dur=10.0, lo=200, hi=1600)
    S.hit(inst.wind, S.bar(12), 0.5, 0, 0.3, 0.0, dur=10.0, lo=200, hi=1600)
    for b in (7, 15, 23):
        S.hit(inst.tom, S.bar(b) + 3, 0.5, 0, 0.2, 0.2, f=92)
        S.hit(inst.tom, S.bar(b) + 3.5, 0.6, 0, 0.2, 0.2, f=75)
    rev_crash_into(S, S.bar(24), 2.4, 0.3, riser=False)
    return S.render(comp=(-21, 2.0), sat=1.15)


# ------------------------------------------------------------------ tormenta
def mus_tormenta():
    S = Song("mus_tormenta", 138, 32, seed=206, irs=("hall", "room"))
    A = "Gm Gm Eb Eb Cm Cm D D"
    P = cyc(A, 4)
    # ostinato de cuerdas rapidas
    S.arp(inst.strings, P, [0, 1, 2, 1], 0, lo=55, step=0.25, vel=0.36, sa=0.2, sb=0.0, nlen=0.22, att=0.01, rel=0.06, bright=1.2,
          voices=2, pan_sweep=0.3, noise=0.01)
    riff(S, inst.strings, A, "x.xx.xx.", (0, 32), octave=2, vel=0.7, dur=0.8, sa=0.1, att=0.01, rel=0.05, bright=0.9, voices=2, pan=-0.2)
    # percusion de trueno
    S.pat(inst.taiko, "X.x.x.x. X.x.x.xx", (0, 32), vel=0.8, sa=0.2, sb=0.2, f=55)
    S.pat(inst.snare, "....x.......x...", (4, 32), vel=0.5, sa=0.2, sb=0.3)
    S.pat(inst.hat, "xxxxxxxx", (8, 32), vel=0.25, sa=0.1, sb=0.0, pan_rand=0.5)
    S.pat(inst.metal, "X.......", (0, 32), vel=0.25, sa=0.3, sb=0.1, f=520, ring=1.0, pan_rand=0.2)
    for b in (0, 8, 16, 24):
        S.hit(inst.thunder, S.bar(b), 0.6, 0, 0.3, 0.1, dur=4.0)
    for b in (5, 12, 20, 27):
        S.hit(inst.thunder, S.bar(b) + 2, 0.4, 0.3, 0.3, 0.1, dur=3.0, crack=1.0)
    # metales
    S.chords(inst.brass, P, 8, lo=43, nmax=3, vel=0.5, sa=0.3, att=0.5, rel=0.4, bright=0.9, legato=0.98)
    M = mel("G4:1 Bb4:1 D5:2 | C5:1 Bb4:1 G4:2 | Bb4:1 Eb5:1 G5:2 | F5:1 Eb5:1 Bb4:2 | "
            "C5:1 Eb5:1 G5:2 | F5:1 Eb5:1 D5:2 | F#5:1 A5:1 D6:2 | C6:1 A5:1 F#5:1 D5:1")
    S.play(inst.brass, M, 8, vel=0.85, sa=0.3, att=0.05, rel=0.2, bright=1.2, voices=3, legato=0.93, pan=0.1)
    S.play(inst.brass, M, 16, vel=0.85, sa=0.3, att=0.05, rel=0.2, bright=1.2, voices=3, legato=0.93, pan=0.1)
    S.play(inst.brass, M, 16, transpose=-12, vel=0.55, sa=0.3, att=0.06, rel=0.2, bright=0.7, voices=2, legato=0.93, pan=-0.3)
    S.play(inst.brass, M, 24, vel=0.9, sa=0.3, att=0.05, rel=0.2, bright=1.3, voices=3, legato=0.93, pan=0.1)
    S.play(inst.violin, M, 24, transpose=12, vel=0.5, sa=0.3, legato=0.95, pan=0.3, bright=1.2)
    S.play(inst.choir, M, 24, vel=0.5, sa=0.4, vowel="a", voices=4, att=0.1, rel=0.4, legato=0.95, shout=0.3)
    S.chords(inst.choir, P, 16, lo=50, nmax=3, vel=0.35, sa=0.4, vowel="o", att=0.5, rel=0.8, voices=4, spread=0.9)
    for b in range(0, 32, 8):
        S.hit(inst.crash, S.bar(b), 0.5, 0, 0.3, 0.0, dur=3.0)
    for b in (7, 15, 23, 31):
        taiko_roll(S, S.bar(b) + 2, 2, 0.3, 0.9, 0.25, f=55, sa=0.2, sb=0.1)
    rev_crash_into(S, S.bar(32), 2.4, 0.4, riser=True, rv=0.3)
    return S.render(comp=(-20, 2.2), sat=1.3)


# ------------------------------------------------------------------ sangre (vals oscuro 3/4)
def mus_sangre():
    S = Song("mus_sangre", 150, 48, bpb=3, seed=207, irs=("cathedral", "chamber"))
    A = "Am Dm E7 Am F Dm E7 E7"
    P = cyc(A, 6)
    riff(S, inst.organ, A, "x..", (0, 48), octave=2, vel=0.45, dur=2.4, sa=0.25, draw={1: 1.0, 2: 0.5, 3: 0.3}, att=0.04, rel=0.3, trem=0.03, chiff=0.1)
    riff(S, inst.pluck, A, "x..", (0, 48), octave=2, vel=0.7, dur=1.0, sa=0.2, bright=0.35, ring=1.0, pan=-0.2)
    riff(S, inst.harpsichord, A, ".xx", (0, 48), chord=True, lo=57, nmax=3, vel=0.5, dur=0.6, sa=0.25, sb=0.1, pan=0.2)
    riff(S, inst.pluck, A, ".xx", (4, 48), chord=True, lo=60, nmax=3, vel=0.3, dur=0.5, sa=0.2, bright=0.5, ring=0.7, pan=-0.3)
    S.chords(inst.organ, P, 8, lo=45, nmax=4, vel=0.22, sa=0.4, draw={1: 1.0, 2: 0.7, 3: 0.4, 4: 0.3}, att=0.15, rel=0.4, trem=0.05, chiff=0.0)
    S.chords(inst.strings, P, 16, lo=52, nmax=3, vel=0.34, sa=0.45, att=0.6, rel=0.9, bright=0.7)
    S.chords(inst.choir, P, 16, lo=57, nmax=3, vel=0.32, sa=0.6, vowel="a", vowel2="o", att=0.9, rel=1.2, voices=4, spread=0.9)
    M = mel("A4:1 C5:1 E5:1 | F5:2 D5:1 | E5:1 G#4:1 B4:1 | C5:2 A4:1 | A4:1 C5:1 F5:1 | D5:2 F5:1 | E5:1.5 D5:.5 B4:1 | G#4:3")
    M2 = mel("E5:2 A5:1 | A5:1.5 G5:.5 F5:1 | E5:1 G#5:1 B5:1 | C6:2 A5:1 | A5:1 G5:1 F5:1 | F5:1 E5:1 D5:1 | E5:1.5 D5:.5 B4:1 | B4:2 G#4:1")
    S.play(inst.violin, M, 8, vel=0.85, sa=0.45, att=0.09, rel=0.25, depth=0.01, bright=1.0, legato=0.96, pan=0.1)
    S.play(inst.violin, M, 16, vel=0.85, sa=0.45, att=0.09, rel=0.25, depth=0.01, bright=1.0, legato=0.96, pan=0.1)
    S.play(inst.organ, M, 16, transpose=-12, vel=0.35, sa=0.4, draw={1: 1.0, 2: 0.6, 4: 0.3}, att=0.05, rel=0.2, trem=0.05, chiff=0.1, legato=0.95, pan=-0.2)
    S.play(inst.violin, M2, 24, vel=0.9, sa=0.45, att=0.09, rel=0.25, depth=0.012, bright=1.0, legato=0.96, pan=0.1)
    S.play(inst.harpsichord, M2, 24, transpose=-12, vel=0.4, sa=0.3, legato=0.9, pan=-0.2)
    S.play(inst.violin, M, 32, vel=0.85, sa=0.45, att=0.09, rel=0.25, depth=0.01, bright=1.0, legato=0.96, pan=0.1)
    S.play(inst.choir, M, 32, vel=0.45, sa=0.6, vowel="a", voices=4, att=0.2, rel=0.5, legato=0.97)
    S.play(inst.violin, M2, 40, vel=0.9, sa=0.45, att=0.09, rel=0.25, depth=0.012, bright=1.1, legato=0.96, pan=0.1)
    S.play(inst.choir, M2, 40, vel=0.5, sa=0.6, vowel="a", voices=5, att=0.2, rel=0.5, legato=0.97)
    S.play(inst.brass, M2, 40, transpose=-12, vel=0.45, sa=0.4, att=0.1, rel=0.3, bright=0.6, legato=0.95, pan=-0.3)
    for b in (0, 8, 16, 24, 32, 40):
        toll(S, S.bar(b), "A3", 0.5, decay=7.0, sa=0.5)
    toll(S, S.bar(47) + 1, "E5", 0.3, decay=6.0, sa=0.5, pan=0.4)
    S.pat(inst.timpani, "X..", (32, 48), vel=0.5, sa=0.3, sb=0.2, f=55)
    for b in (16, 32, 40):
        S.hit(inst.crash, S.bar(b), 0.35, 0, 0.5, 0.0, dur=3.0)
    taiko_roll(S, S.bar(47) + 0.5, 2.5, 0.2, 0.7, 0.25, fn=inst.timpani, f=55)
    rev_crash_into(S, S.bar(48), 2.6, 0.35, riser=False)
    return S.render(comp=(-22, 2.0), sat=1.15)


# ------------------------------------------------------------------ eclipse
def mus_eclipse():
    S = Song("mus_eclipse", 72, 18, seed=208, irs=("cathedral", "hall"))
    H = "Cm Ab Eb Bb Fm G"
    P = cyc(H, 3)
    S.bassline(inst.organ, P, 0, octave=2, vel=0.3, sa=0.3, draw={1: 1.0, 2: 0.6, 3: 0.25}, att=0.5, rel=0.9, trem=0.02, chiff=0)
    S.chords(inst.strings, P, 0, lo=48, nmax=4, vel=0.4, sa=0.45, att=1.0, rel=1.2, bright=0.7)
    S.chords(inst.choir, P, 0, lo=60, nmax=3, vel=0.3, sa=0.6, vowel="a", att=1.4, rel=1.6, voices=4, spread=0.9)
    S.chords(inst.choir, P, 6, lo=67, nmax=3, vel=0.28, sa=0.6, vowel="a", vowel2="o", att=1.4, rel=1.6, voices=4, spread=0.9)
    M = mel("G4:2 C5:1 D5:1 | Eb5:2 C5:2 | G5:2 Eb5:1 D5:1 | D5:2 F5:2 | C5:1 F5:1 Ab5:2 | G5:1 D5:1 B4:2")
    S.play(inst.brass, M, 0, transpose=-12, vel=0.75, sa=0.4, att=0.15, rel=0.4, bright=0.6, voices=2, legato=0.97, pan=-0.2)
    S.play(inst.brass, M, 6, vel=0.85, sa=0.4, att=0.12, rel=0.4, bright=1.0, voices=3, legato=0.97, pan=0.1)
    S.play(inst.choir, M, 6, vel=0.5, sa=0.6, vowel="a", voices=4, att=0.3, rel=0.7, legato=0.98)
    S.play(inst.brass, M, 12, vel=0.9, sa=0.4, att=0.1, rel=0.4, bright=1.2, voices=3, legato=0.97, pan=0.1)
    S.play(inst.brass, M, 12, transpose=-12, vel=0.6, sa=0.4, att=0.12, rel=0.4, bright=0.7, voices=3, legato=0.97, pan=-0.3)
    S.play(inst.choir, M, 12, transpose=12, vel=0.5, sa=0.6, vowel="a", voices=5, att=0.3, rel=0.7, legato=0.98)
    S.play(inst.violin, M, 12, transpose=12, vel=0.45, sa=0.5, legato=0.97, pan=0.3)
    S.pat(inst.timpani, "X...x...", (0, 6), vel=0.45, sa=0.3, sb=0.2, f=65.4)
    S.pat(inst.taiko, "X.x.x.x.", (6, 18), vel=0.55, sa=0.3, sb=0.2, f=58)
    S.arp(inst.pluck, P, [0, 1, 2, 3, 2, 1, 2, 4], 6, lo=48, step=0.5, vel=0.4, sa=0.4, sb=0.1, pan_sweep=0.4, nlen=2, bright=0.5, ring=2.5)
    S.arp(inst.glass, P, [0, 1, 2, 3], 6, lo=76, step=1.0, vel=0.25, sa=0.6, pan_sweep=0.6, decay=2.5)
    for b in (0, 3, 6, 9, 12, 15):
        toll(S, S.bar(b), "C4", 0.45, decay=6.0, sa=0.5, pan=0.2)
    toll(S, S.bar(6) + 2, "G4", 0.3, decay=6.0, sa=0.5, pan=-0.3)
    toll(S, S.bar(12) + 2, "Eb5", 0.3, decay=6.0, sa=0.5, pan=0.3)
    for b in (0, 6, 12):
        S.hit(inst.crash, S.bar(b), 0.4, 0, 0.5, 0.0, dur=3.0)
    rev_crash_into(S, S.bar(6), 2.6, 0.3, riser=False)
    rev_crash_into(S, S.bar(12), 2.6, 0.35, riser=False)
    rev_crash_into(S, S.bar(18), 3.0, 0.4, riser=True)
    return S.render(comp=(-22, 2.0), sat=1.15)


TRACKS = {
    "mus_catacumbas": mus_catacumbas, "mus_forja": mus_forja, "mus_helado": mus_helado, "mus_vacio": mus_vacio,
    "mus_bosque": mus_bosque, "mus_tormenta": mus_tormenta, "mus_sangre": mus_sangre, "mus_eclipse": mus_eclipse,
}
