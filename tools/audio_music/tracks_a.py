"""tracks_a.py - temas del leitmotiv: title, sanctuary, victory, gameover, credits."""
import numpy as np
import inst
from song import *
from arr import *

D_MIN = {2, 4, 5, 7, 9, 10, 0}
HARM = LEIT_HARM


def mus_title():
    S = Song("mus_title", 66, 16, seed=101, irs=("cathedral", "room"))
    spb = S.spb
    # ---- bajo / drone todo el tema
    S.bassline(inst.organ, HARM + " " + HARM, 0, octave=2, vel=0.32, sa=0.3, draw={1: 1.0, 2: 0.6, 3: 0.3},
               att=0.4, rel=0.8, trem=0.02, chiff=0.0)
    S.bassline(inst.sub, HARM + " " + HARM, 0, octave=1, vel=0.22, sa=0.0, att=0.3, rel=0.6)
    # ---- cuerdas pad
    S.chords(inst.strings, HARM, 0, lo=50, nmax=3, vel=0.42, sa=0.45, att=1.4, rel=1.6, bright=0.55)
    S.chords(inst.strings, HARM, 8, lo=50, nmax=3, vel=0.6, sa=0.45, att=1.0, rel=1.6, bright=0.8)
    S.chords(inst.strings, HARM, 8, lo=62, nmax=3, vel=0.4, sa=0.5, att=1.2, rel=1.6, bright=0.9, pan=0.3)
    # ---- coro
    S.chords(inst.choir, HARM, 4, lo=57, nmax=3, vel=0.5, sa=0.55, vowel="o", att=1.2, rel=1.4, voices=3, spread=0.9)
    S.chords(inst.choir, HARM, 8, lo=62, nmax=3, vel=0.5, sa=0.55, vowel="a", att=1.0, rel=1.4, voices=4, spread=0.9)
    # ---- leitmotiv: 1a vez violonchelo + trompa, 2a vez violin + coro
    L1 = leit(50)
    S.play(inst.strings, L1, 0, vel=0.85, sa=0.4, voices=2, att=0.18, rel=0.5, vib=0.006, bright=0.9, legato=0.98, pan=-0.15)
    S.play(inst.brass, L1, 0, vel=0.45, sa=0.45, att=0.3, rel=0.4, bright=0.35, voices=2, legato=0.95, transpose=0, pan=0.2)
    L2 = leit(62)
    S.play(inst.violin, L2, 8, vel=0.9, sa=0.45, att=0.1, rel=0.3, depth=0.01, bright=1.0, legato=0.98, pan=0.1, slide=0.4)
    S.play(inst.choir, L2, 8, vel=0.65, sa=0.55, vowel="a", vowel2="o", voices=4, att=0.22, rel=0.6, legato=0.97, spread=0.7)
    S.play(inst.brass, [n for n in leit(50) if n[0] >= 16], 8 - 4, vel=0.6, sa=0.4, att=0.25, rel=0.4, bright=0.7,
           voices=3, legato=0.95, pan=-0.2)
    # ---- campanas
    for b in (0, 4, 8, 12):
        toll(S, S.bar(b), "D3", 0.55 if b < 8 else 0.7, decay=7.0, sa=0.5)
    toll(S, S.bar(7) + 2, "A4", 0.35, decay=5.0, pan=0.4)
    toll(S, S.bar(15) + 2, "A4", 0.35, decay=5.0, pan=-0.4)
    # ---- percusion
    S.pat(inst.taiko, "X.......x.......", (4, 8), vel=0.5, sa=0.25, sb=0.15, f=58)
    S.pat(inst.taiko, "X.......x.....o.", (8, 15), vel=0.7, sa=0.3, sb=0.2, f=58)
    S.hit(inst.crash, S.bar(8), 0.4, 0, 0.5, 0.0, dur=3.0)
    taiko_roll(S, S.bar(15), 4, 0.25, 0.85, 0.25)
    rev_crash_into(S, S.bar(16), 3.6, 0.55)
    S.hit(inst.taiko, S.bar(0), 0.9, 0, 0.3, 0.2, f=52)
    return S.render(comp=(-22, 2.2))


def mus_sanctuary():
    S = Song("mus_sanctuary", 56, 16, seed=102, irs=("cathedral", "chamber"))
    H = "Dm9 Bbmaj7 Gm7 Bbmaj7 Dm9 Bbmaj7 Gm7 Dm:2 A7sus4:2"
    S.bassline(inst.organ, HARM + " " + HARM, 0, octave=2, vel=0.28, sa=0.35, draw={0.5: 1.0, 1: 0.5}, att=0.8, rel=1.0, trem=0.02, chiff=0)
    S.chords(inst.strings, H + " " + H, 0, lo=50, nmax=4, vel=0.34, sa=0.55, att=1.8, rel=1.8, bright=0.5)
    # arpa
    for bar0 in (0, 8):
        S.arp(inst.pluck, H, [0, 1, 2, 3, 4, 3, 2, 1], bar0, lo=50, step=0.5, vel=0.55 if bar0 == 0 else 0.62, sa=0.4, sb=0.1,
              pan_sweep=0.35, nlen=2.0, bright=0.45, ring=3.0)
    # leitmotiv: flauta -> violin + celesta
    S.play(inst.flute, leit(62), 0, vel=0.8, sa=0.5, att=0.12, rel=0.3, breath=0.2, vib=0.007, legato=0.97, pan=0.1)
    S.play(inst.violin, leit(62), 8, vel=0.65, sa=0.55, att=0.15, rel=0.35, depth=0.007, bright=0.7, legato=0.97, pan=-0.1)
    S.play(inst.celesta, leit(74), 8, vel=0.5, sa=0.6, legato=1.0, pan=0.3, decay=2.2)
    S.chords(inst.choir, H, 8, lo=57, nmax=3, vel=0.28, sa=0.6, vowel="o", att=2.0, rel=2.0, voices=3, spread=0.9)
    # campanas suaves y brillos
    toll(S, S.bar(0), "D4", 0.35, decay=6.0, sa=0.6)
    toll(S, S.bar(8), "D4", 0.35, decay=6.0, sa=0.6)
    toll(S, S.bar(4) + 2, "A4", 0.25, decay=5.0, sa=0.6, pan=0.3)
    toll(S, S.bar(12) + 2, "F4", 0.25, decay=5.0, sa=0.6, pan=-0.3)
    sparkle(S, 0, 16, D_MIN, 0.28, inst.glass, 84, 100, 0.3, 0.6, seed=5, decay=2.5)
    S.hit(inst.wind, S.bar(0), 0.45, 0, 0.3, 0.0, dur=9.0, lo=200, hi=1200)
    S.hit(inst.wind, S.bar(7), 0.4, 0, 0.3, 0.0, dur=9.0, lo=200, hi=1200)
    S.hit(inst.wind, S.bar(14), 0.4, 0, 0.3, 0.0, dur=9.0, lo=200, hi=1200)
    S.hit(inst.timpani, S.bar(8), 0.45, 0, 0.3, 0.2, f=73.4)
    return S.render(comp=(-26, 2.0), sat=1.1)


def mus_victory():
    S = Song("mus_victory", 96, 7, loop=False, seed=103, irs=("cathedral", "room"), tail=0.0)
    spb = S.spb
    # bar 0: redoble + fanfarria
    taiko_roll(S, 0, 3.5, 0.3, 0.8, 0.25, fn=inst.taiko, f=70)
    fan = mel("A4:.5 A4:.5 D5:1 F#5:1 A5:1")
    S.play(inst.brass, fan, 0, vel=0.8, sa=0.4, att=0.04, rel=0.4, bright=1.3, voices=3, legato=0.9)
    S.play(inst.brass, [(b, m - 12, d) for b, m, d in fan], 0, vel=0.6, sa=0.4, att=0.05, rel=0.4, bright=0.8, voices=2, legato=0.9, pan=-0.3)
    S.chords(inst.strings, "D", 0, lo=50, nmax=3, vel=0.5, sa=0.4, att=0.4, rel=1.2, bright=0.9)
    S.hit(inst.crash, 0, 0.6, 0, 0.5, 0, dur=4.0)
    # bars 1-4: leitmotiv en mayor (Bb de color)
    VH = "D:2 Bb:2 G:2 D/F#:2 G:2 A:2 D:3 A:1"
    mel_v = mel("0:2 7:1 8:1 | 7:2 5:1 4:1 | 2:1.5 4:.5 5:1 7:1 | 12:3 11:1", 62)
    S.play(inst.brass, mel_v, 1, vel=0.85, sa=0.45, att=0.07, rel=0.35, bright=1.1, voices=3, legato=0.95, pan=0.1)
    S.play(inst.violin, [(b, m + 12, d) for b, m, d in mel_v], 1, vel=0.5, sa=0.5, att=0.06, rel=0.3, legato=0.97, pan=-0.2)
    S.play(inst.choir, mel_v, 1, vel=0.5, sa=0.55, vowel="a", voices=4, att=0.15, rel=0.5, legato=0.97)
    S.chords(inst.strings, VH, 1, lo=50, nmax=3, vel=0.55, sa=0.4, att=0.25, rel=0.9, bright=0.9)
    S.bassline(inst.organ, VH, 1, octave=2, vel=0.4, sa=0.3, draw={0.5: 1.0, 1: 0.8, 2: 0.3}, att=0.1, rel=0.4, trem=0.02, chiff=0)
    S.bassline(inst.sub, VH, 1, octave=1, vel=0.45, sa=0.0, att=0.05, rel=0.3)
    S.pat(inst.taiko, "X.......x.......", (1, 5), vel=0.6, sa=0.3, sb=0.2, f=60)
    for b in (1, 3):
        toll(S, S.bar(b), "D3", 0.4, decay=5.0, sa=0.5)
    # bar 5: cadencia melancolica, bar 6: acorde final
    CH = "Bm:2 G:1 A7:1"
    S.chords(inst.strings, CH, 5, lo=50, nmax=4, vel=0.6, sa=0.45, att=0.2, rel=1.0, bright=0.9)
    S.play(inst.brass, mel("F#5:2 E5:1 E5:1".replace("F#5", "F#4").replace("E5", "E4"), 0), 5, vel=0.7, sa=0.45, att=0.08, rel=0.4, bright=0.9, legato=0.95)
    S.play(inst.violin, mel("D6:2 C#6:1 E6:1"), 5, vel=0.5, sa=0.5, legato=0.95)
    S.chords(inst.strings, "D", 6, lo=50, nmax=3, vel=0.6, sa=0.5, att=0.15, rel=2.5, bright=0.9)
    S.chords(inst.strings, "D", 6, lo=62, nmax=3, vel=0.4, sa=0.5, att=0.15, rel=2.5, bright=1.0, pan=0.3)
    S.chords(inst.choir, "D", 6, lo=62, nmax=3, vel=0.5, sa=0.55, vowel="a", att=0.2, rel=2.5, voices=4)
    S.play(inst.brass, mel("D5:3"), 6, vel=0.7, sa=0.5, att=0.08, rel=1.5, bright=1.0)
    S.bassline(inst.organ, "D", 6, octave=2, vel=0.4, sa=0.3, draw={0.5: 1.0, 1: 0.8, 2: 0.3}, att=0.1, rel=2.0, trem=0.02, chiff=0)
    S.bassline(inst.sub, "D", 6, octave=1, vel=0.5, sa=0.0, att=0.05, rel=1.5)
    S.hit(inst.timpani, S.bar(6), 0.8, 0, 0.4, 0.2, f=73.4)
    S.hit(inst.crash, S.bar(6), 0.4, 0, 0.5, 0, dur=4.0)
    toll(S, S.bar(6), "D3", 0.55, decay=6.0, sa=0.5)
    toll(S, S.bar(6) + 1, "A4", 0.3, decay=6.0, sa=0.5, pan=0.4)
    return S.render(comp=(-20, 2.2), fade_out=2.0)


def mus_gameover():
    S = Song("mus_gameover", 46, 2, loop=False, seed=104, irs=("cathedral", "room"), tail=0.0)
    toll(S, 0, "D2", 0.9, decay=8.0, sa=0.5)
    toll(S, 4, "D2", 0.6, decay=8.0, sa=0.5)
    # coro cayendo
    for i, (b, nm) in enumerate(((0, "Dm"), (2, "Cm"), (4, "Bm"), (6, "Bbm"))):
        vs = voicing(nm, 50, 3)
        for m in vs:
            S.note(inst.choir, m - 0, b, 2.2, 0.42, 0.0, 0.6, 0.0, vowel="o", att=0.7, rel=1.6, voices=3, spread=0.9)
        for m in voicing(nm, 38, 2):
            S.note(inst.strings, m, b, 2.2, 0.4, 0.0, 0.5, 0.0, att=0.5, rel=1.4, bright=0.35, voices=3)
    S.play(inst.strings, mel("D3:2 A3:1 Bb3:1 | A3:3 r:1"), 0, vel=0.9, sa=0.5, voices=2, att=0.3, rel=1.0, vib=0.008, bright=0.7, pan=-0.1)
    S.play(inst.brass, mel("D2:8"), 0, vel=0.55, sa=0.4, att=1.2, rel=2.0, bright=0.2, voices=2)
    S.note(inst.sub, 26, 0, 8, 0.7, 0, 0.0, 0.0, att=0.4, rel=2.0)
    for b in (1.5, 2.0, 3.8, 4.4, 6.4):
        S.hit(inst.kick, b, 0.5, 0, 0.3, 0.0, f=44, decay=0.5, sweep=1.5)
    S.hit(inst.taiko, 0, 0.8, 0, 0.3, 0.2, f=48, decay=1.8)
    S.hit(inst.wind, 0, 0.4, 0, 0.4, 0, dur=8.0, lo=150, hi=900)
    return S.render(comp=(-24, 2.0), fade_out=2.5)


def mus_credits():
    S = Song("mus_credits", 64, 16, seed=105, irs=("hall", "chamber"))
    H = "Dm Bb Gm Bb Dm Bb Gm Dm:2 A:2"
    H2 = "Dm Bb F Bb Dm Bb Gm Dm:2 A:2"
    S.bassline(inst.organ, H + " " + H2, 0, octave=2, vel=0.25, sa=0.3, draw={0.5: 1.0, 1: 0.6}, att=0.6, rel=0.9, trem=0.02, chiff=0)
    S.bassline(inst.sub, H + " " + H2, 0, octave=1, vel=0.3, sa=0.0, att=0.3, rel=0.6)
    S.chords(inst.strings, H, 0, lo=50, nmax=3, vel=0.36, sa=0.5, att=1.4, rel=1.5, bright=0.6)
    S.chords(inst.strings, H2, 8, lo=50, nmax=3, vel=0.55, sa=0.5, att=0.9, rel=1.5, bright=0.85)
    S.chords(inst.strings, H2, 8, lo=62, nmax=3, vel=0.4, sa=0.55, att=1.0, rel=1.5, bright=1.0, pan=0.3)
    # arpa
    S.arp(inst.pluck, H, [0, 1, 2, 1, 2, 1, 2, 3], 0, lo=50, step=0.5, vel=0.5, sa=0.4, sb=0.1, pan_sweep=0.3, nlen=2, bright=0.4, ring=2.5)
    S.arp(inst.pluck, H2, [0, 1, 2, 4, 2, 1, 2, 1], 8, lo=50, step=0.5, vel=0.45, sa=0.4, sb=0.1, pan_sweep=0.3, nlen=2, bright=0.45, ring=2.5)
    # leitmotiv: violonchelo (1a) -> violin + flauta + coro (2a)
    S.play(inst.strings, leit(50), 0, vel=0.9, voices=2, att=0.2, rel=0.5, vib=0.007, bright=0.8, sa=0.45, legato=0.98, pan=-0.1)
    S.play(inst.violin, leit(62), 8, vel=0.95, sa=0.5, att=0.12, rel=0.35, depth=0.01, bright=1.0, legato=0.98, slide=0.35, pan=0.1)
    S.play(inst.flute, leit(74), 8, vel=0.35, sa=0.5, att=0.15, rel=0.3, legato=0.97, pan=0.35)
    S.play(inst.choir, leit(62), 8, vel=0.45, sa=0.6, vowel="a", vowel2="o", voices=4, att=0.3, rel=0.7, legato=0.98)
    S.play(inst.celesta, leit(74), 0, vel=0.35, sa=0.6, pan=0.3, decay=2.0)
    S.chords(inst.choir, H, 4, lo=57, nmax=3, vel=0.28, sa=0.6, vowel="o", att=1.5, rel=1.6, voices=3)
    toll(S, S.bar(0), "D3", 0.4, decay=6.0, sa=0.5)
    toll(S, S.bar(8), "D3", 0.5, decay=6.0, sa=0.5)
    toll(S, S.bar(12), "Bb3", 0.35, decay=6.0, sa=0.5)
    sparkle(S, 8, 16, D_MIN, 0.3, inst.glass, 84, 100, 0.28, 0.6, seed=9, decay=2.4)
    S.pat(inst.timpani, "X.......", (12, 16), vel=0.4, sa=0.3, sb=0.2, f=73.4)
    taiko_roll(S, S.bar(15) + 2, 2, 0.2, 0.6, 0.25, fn=inst.timpani, f=73.4)
    S.hit(inst.wind, S.bar(14), 0.3, 0, 0.3, 0.0, dur=9.0, lo=200, hi=1200)
    rev_crash_into(S, S.bar(16), 3.0, 0.35, riser=False)
    return S.render(comp=(-24, 2.0), sat=1.1)


TRACKS = {
    "mus_title": mus_title, "mus_sanctuary": mus_sanctuary, "mus_victory": mus_victory,
    "mus_gameover": mus_gameover, "mus_credits": mus_credits,
}
