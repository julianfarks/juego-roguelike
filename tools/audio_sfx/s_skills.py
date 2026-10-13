from recipes import *
from reg import sfx, add, REG

# Todos los skills: sk_<c>_1..3 (cast), sk_<c>_hit, ult_<c>

# ============================================================ PALADIN (luz, coro, campana)
@sfx('sk_paladin_1', -3)
def _(r):
    m = Mix()
    m.add(riser(.5, 700, 7000, r, 1.6, 0, 1.2), 0, .6)
    m.add(whoosh(.5, [(0, 900), (.5, 4500)], r, 2.0, .6, 1.0), .1, .5)
    m.add(bell(mt(88), 1.0, .35, r), .38, .8)
    m.add(bell(mt(81), 1.0, .3, r), .38, .5)
    m.add(choir([mt(72), mt(76)], .8, r, ('a', 'o'), .12, .5), .3, .6)
    m.add(sparkle(.6, r, 25, 3500, 11000, .06), .3, .4)
    m.add(thump(150, 60, .2, .03, .08), .38, .6)
    return reverb(m.render(), .9, .2, 6500, seed=40)


@sfx('sk_paladin_2', -3)
def _(r):
    m = Mix()
    m.add(wingflap(.8, r, 4.5, 3000, 1.0), 0, 1.0)
    m.add(whoosh(.6, [(0, 800), (.5, 3500)], r, 1.0, .4, 1.2), 0, .5)
    m.add(choir([mt(60), mt(67), mt(72)], 1.1, r, ('o', 'a'), .25, .6), .05, .9)
    m.add(modal(mt(84), GLASS, 1.0, .3, r), .35, .5)
    m.add(modal(1400, PLATE, .6, .2, r), .35, .35)
    m.add(sparkle(.8, r, 30, 3000, 10000, .08), .2, .4)
    return reverb(m.render(), 1.1, .25, 6000, seed=41)


@sfx('sk_paladin_3', -2)
def _(r):
    m = Mix()
    m.add(reverse(bell(mt(76), .8, .3, r)), 0, .7)
    m.add(riser(.55, 400, 6000, r, 1.2, .4, 1.5), 0, .6)
    m.add(boom(.9, r, 70, .9, noise_f=1500), .55, .9)
    m.add(bell(mt(64), 1.8, .7, r), .55, .8)
    m.add(bell(mt(88), 1.4, .5, r), .55, .5)
    m.add(choir([mt(52), mt(59), mt(64), mt(71)], 1.4, r, ('a', 'a'), .05, .8), .5, 1.0)
    m.add(sparkle(1.0, r, 40, 3000, 12000, .1), .55, .4)
    return reverb(m.render(), 1.5, .28, 6000, seed=42)


@sfx('sk_paladin_hit', -4)
def _(r):
    m = Mix()
    m.add(tick(r, .02, 3500, .004), 0, .6)
    m.add(bell(mt(84), .7, .25, r), 0, .8)
    m.add(bell(mt(91), .6, .2, r), .02, .45)
    m.add(thump(200, 80, .15, .03, .06), 0, .6)
    m.add(sparkle(.4, r, 14, 4000, 11000, .05), 0, .3)
    return reverb(m.render(), .5, .12, 6500, seed=43)


@sfx('ult_paladin', 0)
def _(r):
    m = Mix()
    D = 4.4
    cl = 2.3
    m.add(riser(cl, 300, 8000, r, 1.4, .5, 2.0), 0, .6)
    m.add(choir([mt(50), mt(57), mt(62), mt(65)], 1.7, r, ('o', 'a'), .9, .3, nv=4), 0, .6)
    m.add(choir([mt(55), mt(62), mt(67), mt(71)], 1.2, r, ('a', 'a'), .7, .2, nv=4), 1.5, .7)
    for k in range(10):
        t0 = .3 + k * .22 * (1 - k * .03)
        m.add(bell(mt(76 + (k % 4) * 3), .9, .3, r), t0, .3 + k * .035)
    m.add(reverse(whoosh(.5, [(0, 500), (.5, 8000)], r, 1.0, .5)), cl - .5, .5)
    m.add(boom(1.4, r, 45, 1.0, noise_f=2500), cl, 1.0)
    m.add(thump(70, 30, 1.2, .1, .5, 1.5), cl, .8)
    m.add(choir([mt(50), mt(57), mt(62), mt(69), mt(74), mt(81)], 1.6, r, ('a', 'a'), .02, .8, nv=4, scale=1.0), cl, 1.1)
    for k, nn in enumerate([64, 76, 83, 88, 95]):
        m.add(bell(mt(nn), 1.6, .6, r), cl + k * .03, .6)
    m.add(sparkle(1.5, r, 80, 3000, 13000, .12), cl, .4)
    return reverb(m.render(), 1.5, .3, 6000, seed=44)


# ============================================================ SHADOW (susurros y cortes de aire)
@sfx('sk_shadow_1', -3)
def _(r):
    m = Mix()
    m.add(whisper(.6, r, 7, ('i', 'e'), 1.0, 1200, 2), 0, .6)
    m.add(whoosh(.25, [(0, 600), (.25, 5000)], r, 1.5, .4, 1.0), 0, .7)
    m.add(reverse(sweep(noise(N(.3), r), curve(.3, [(0, 6000), (.3, 400)], log=True), 'lp') * expdec(.3, .1)), .0, .4)
    m.add(thump(120, 50, .2, .03, .08), .22, .5)
    m.add(slash(r, .08, 3000, 9000, 3, 1.0), .2, .5)
    return reverb(m.render(), .6, .15, 4500, seed=45)


@sfx('sk_shadow_2', -3)
def _(r):
    m = Mix()
    m.add(slash(r, .14, 1500, 7000, 3.0, 1.0), 0, 1.0)
    m.add(whisper(.8, r, 6, ('e', 'i'), 1.0, 1500, 2), .05, .45)
    m.add(modal(mt(81), GLASS, .8, .25, r), .1, .12)
    n = N(.8)
    f = curve(.8, [(0, 700), (.8, 900)], log=True) * (1 + .02 * np.sin(2 * np.pi * 6 * np.arange(n) / SR))
    m.add(sine(f, n) * bump(.8, .3, 1.5) * .12 + sine(f * 1.5, n) * bump(.8, .4, 1.5) * .08, 0, 1.0)
    m.add(slash(r, .1, 4000, 10000, 3, 1.0), .14, .6)
    return reverb(m.render(), .8, .2, 4500, seed=46)


@sfx('sk_shadow_3', -3)
def _(r):
    m = Mix()
    for i in range(7):
        a, b = (2500, 8500) if i % 2 == 0 else (9000, 2800)
        m.add(slash(r, .09 + .01 * (i % 3), a, b, 2.8, 1.0), i * .12, .6 + (i == 6) * .4)
        m.add(tick(r, .01, 5000, .002), i * .12 + .03, .15)
    m.add(whisper(1.2, r, 8, ('i', 'e'), 1.0, 1300, 3), 0, .45)
    m.add(thump(110, 50, .3, .04, .1), .72, .6)
    return reverb(m.render(), .7, .15, 4500, seed=47)


@sfx('sk_shadow_hit', -4)
def _(r):
    m = Mix()
    m.add(slash(r, .06, 3500, 9000, 3, 1.0), 0, .8)
    m.add(tick(r, .015, 3000, .003), .03, .5)
    m.add(thump(130, 60, .15, .03, .06), .03, .5)
    m.add(whisper(.4, r, 9, ('i', 'e'), 1.0, 2000, 1), 0, .3)
    return reverb(m.render(), .4, .1, 4500, seed=48)


@sfx('ult_shadow', 0)
def _(r):
    m = Mix()
    D = 4.4
    m.add(drone(3.0, 55, r, 1.0, .006, 3, 500, 2.0, .5), 0, .6)
    m.add(whisper(2.8, r, 7, ('i', 'e'), 1.0, 1200, 4), 0, .8)
    m.add(riser(2.2, 300, 6000, r, 2.2, .3, 2.2), 0, .35)
    # tajos en aceleracion
    t0 = .6
    k = 0
    gap = .32
    while t0 < 2.7:
        a, b = (2200, 8500) if k % 2 == 0 else (9000, 2500)
        m.add(slash(r, .1, a, b, 3, 1.0), t0, .35 + .03 * k)
        t0 += gap
        gap = max(.07, gap * .78)
        k += 1
    # desgarro dimensional
    z = hp(noise(N(.5), r), 1500, 2) * expdec(.5, .12, .0003)
    z = sweep(z, curve(.5, [(0, 9000), (.5, 800)], log=True), 'lp')
    m.add(sat(z, 3), 2.7, 1.0)
    m.add(boom(1.0, r, 38, 1.0, noise_f=700), 2.7, 1.0)
    m.add(reverse(sweep(noise(N(.45), r), curve(.45, [(0, 500), (.45, 9000)], log=True), 'lp')), 2.25, .4)
    m.add(slash(r, .2, 700, 9000, 1.5, 1.0), 2.62, .9)
    m.add(whisper(1.5, r, 10, ('e', 'i'), 1.0, 1000, 3), 2.8, .5)
    m.add(modal(mt(51), BELL, 2.0, .9, r), 2.75, .3)
    return reverb(m.render(), 1.8, .3, 3800, seed=49)


# ============================================================ FLAME (rugido y crepitar)
@sfx('sk_flame_1', -3)
def _(r):
    m = Mix()
    m.add(fireroar(.8, r, 900, 1.0), 0, 1.0)
    m.add(whoosh(.6, [(0, 300), (.6, 2000)], r, .9, .35, 1.0, 'pink'), 0, .6)
    m.add(crackle(.8, curve(.8, [(0, 1500), (.8, 400)]), r, 3200, 1.2, 1500) * expdec(.8, .35, .002), 0, .5)
    m.add(thump(120, 50, .25, .04, .1, 1.3), 0, .8)
    return reverb(m.render(), .5, .1, 5000, seed=50)


@sfx('sk_flame_2', -3)
def _(r):
    m = Mix()
    m.add(rumble(1.4, r, 120, 5, .5, env=bump(1.4, .3, 1.0)), 0, 1.4)
    m.add(fireroar(1.4, r, 800, 1.0), 0, 1.0)
    m.add(boom(.7, r, 60, .9, noise_f=2500), 0, .9)
    m.add(crackle(1.4, curve(1.4, [(0, 2500), (1.4, 800)]), r, 3000, 1.1, 1200) * bump(1.4, .4, 1.0), 0, .7)
    return reverb(m.render(), .8, .15, 4500, seed=51)


@sfx('sk_flame_3', -3)
def _(r):
    d = 1.5
    n = N(d)
    t = np.arange(n) / SR
    m = Mix()
    fr = fireroar(d, r, 900, 1.0)
    rot = .6 + .4 * np.sin(2 * np.pi * 5.5 * t)
    m.add(fr * rot, 0, 1.0)
    m.add(whoosh(d, [(0, 300), (d * .5, 1200), (d, 500)], r, 1.0, .45, 1.0, 'pink') * (.7 + .3 * np.sin(2 * np.pi * 5.5 * t + 1)), 0, .8)
    m.add(crackle(d, 1200, r, 3500, 1.2, 1500) * bump(d, .5, 1.0), 0, .6)
    m.add(rumble(d, r, 100, 5.5, .6, env=bump(d, .4, 1.0)), 0, 1.0)
    return reverb(m.render(), .7, .12, 4500, seed=52)


@sfx('sk_flame_hit', -4)
def _(r):
    m = Mix()
    m.add(boom(.4, r, 90, .9, noise_f=3000), 0, 1.0)
    m.add(crackle(.55, curve(.55, [(0, 2500), (.55, 300)]), r, 3200, 1.2, 1200) * expdec(.55, .2, .002), 0, .7)
    m.add(sweep(noise(N(.5), r), curve(.5, [(0, 5000), (.5, 1000)], log=True), 'lp') * expdec(.5, .12, .002), 0, .5)
    return reverb(m.render(), .4, .1, 5000, seed=53)


@sfx('ult_flame', 0)
def _(r):
    m = Mix()
    cl = 2.3
    m.add(rumble(cl + 1, r, 90, 4, .5, env=swell(cl + 1, cl * .9, .3)), 0, 1.5)
    m.add(fireroar(cl + .4, r, 700, 1.0) * np.linspace(.2, 1, N(cl + .4)) ** 1.5, 0, .9)
    m.add(crackle(4.3, curve(4.3, [(0, 400), (cl, 2500), (4.3, 600)]), r, 3300, 1.1, 1300) * swell(4.3, 1.5, 2.0), 0, .7)
    # rugido de dragon
    f0 = curve(1.9, [(0, 70), (.25, 150), (.8, 110), (1.9, 55)])
    m.add(voice(1.9, f0, r, 'a', 'o', scale=.55, dist=4.0, growl=.7, growl_f=45, breath=.4, jitter=.04, env=bump(1.9, .18, .9)), cl - .5, 1.0)
    m.add(riser(cl, 200, 5000, r, 1.2, .3, 2.0), 0, .4)
    m.add(boom(1.8, r, 40, 1.0, noise_f=3000), cl, 1.0)
    m.add(thump(75, 28, 1.4, .1, .5, 1.6), cl, .9)
    m.add(fireroar(1.9, r, 1100, 1.0), cl, .9)
    m.add(debris(1.5, r, 30, 400, 2500, .06), cl + .1, .35)
    return reverb(m.render(), 1.8, .28, 4200, seed=54)


# ============================================================ STORM (trueno y chisporroteo)
@sfx('sk_storm_1', -3)
def _(r):
    m = Mix()
    m.add(zap(.22, r, 5000, 800, 1.0), 0, .9)
    m.add(whoosh(.25, [(0, 1000), (.25, 7000)], r, 1.2, .4, 1.0), 0, .6)
    m.add(sat(hp(noise(N(.1), r), 1500, 2) * expdec(.1, .02, .0003), 4), .12, .8)
    m.add(crackle(.5, 1500, r, 5000, .9, 2000) * expdec(.5, .15), .12, .6)
    m.add(thump(130, 50, .25, .03, .1, 1.3), .12, .6)
    return reverb(m.render(), .5, .1, 6000, seed=55)


@sfx('sk_storm_2', -3)
def _(r):
    m = Mix()
    for i in range(4):
        m.add(zap(.14, r, 4500 - 300 * i, 600, 1.0), i * .17, .7)
        m.add(tick(r, .015, 3500, .003), i * .17, .5)
    m.add(crackle(1.0, 800, r, 4000, .9, 1800) * bump(1.0, .5, 1.0), 0, .7)
    m.add(rumble(.9, r, 120, 5, .6, env=bump(.9, .3, 1.0)), 0, .8)
    return reverb(m.render(), .5, .1, 6000, seed=56)


@sfx('sk_storm_3', -3)
def _(r):
    m = Mix()
    m.add(thunder(1.6, r, True), 0, 1.0)
    m.add(crackle(1.5, curve(1.5, [(0, 600), (.3, 2500), (1.5, 400)]), r, 4500, .9, 1800), 0, .8)
    m.add(hp(noise(N(1.5), r, 'pink'), 3000, 1) * bump(1.5, .3, 1.5) * .15, 0, 1.0)
    m.add(zap(.3, r, 4000, 500, 1.0), .5, .5)
    return reverb(m.render(), .9, .15, 5000, seed=57)


@sfx('sk_storm_hit', -4)
def _(r):
    m = Mix()
    m.add(zap(.3, r, 4500, 500, 1.0), 0, .8)
    m.add(sat(hp(noise(N(.08), r), 1500, 2) * expdec(.08, .015, .0003), 4), 0, .8)
    m.add(crackle(.4, 2000, r, 5000, .9, 2000) * expdec(.4, .1), 0, .6)
    m.add(thump(160, 60, .2, .03, .08), 0, .6)
    return m.render()


@sfx('ult_storm', 0)
def _(r):
    m = Mix()
    cl = 2.3
    n = N(cl)
    f = curve(cl, [(0, 200), (cl, 3500)], log=True)
    m.add(sat(saw(f, n) * .5 + sine(f * 2, n) * .3, 2) * (np.arange(n) / n) ** 2.2 * .5, 0, .7)
    m.add(gust(cl, r, 300, 2500, .8, 1.0) * np.linspace(.2, 1, n), 0, .8)
    m.add(crackle(cl, curve(cl, [(0, 100), (cl, 2500)]), r, 4500, .9, 1800), 0, .8)
    for k in range(5):
        m.add(zap(.12, r, 4500, 700, 1.0), .6 + k * .38, .4 + k * .06)
    m.add(rumble(cl, r, 90, 3, .5, env=swell(cl, cl * .8, .2)), 0, 1.0)
    m.add(riser(cl, 400, 9000, r, 1.5, 0, 2.2), 0, .4)
    # rayo divino
    cr = sat(hp(noise(N(.5), r), 600, 2) * expdec(.5, .08, .0002), 6)
    m.add(cr, cl, 1.0)
    m.add(sweep(noise(N(.7), r), curve(.7, [(0, 8000), (.7, 500)], log=True), 'lp') * expdec(.7, .2, .0004), cl, .9)
    m.add(thunder(1.8, r, False), cl + .05, 1.2)
    m.add(boom(1.5, r, 38, 1.0, noise_f=1200), cl, 1.0)
    m.add(crackle(1.3, curve(1.3, [(0, 3000), (1.3, 300)]), r, 5000, .9, 2000) * expdec(1.3, .5), cl, .8)
    m.add(zap(.5, r, 5000, 300, 1.0), cl + .1, .6)
    return reverb(m.render(), 1.2, .3, 5000, seed=58)


# ============================================================ FROST (cristal y viento helado)
@sfx('sk_frost_1', -3)
def _(r):
    m = Mix()
    m.add(gust(.5, r, 1500, 5000, 1.2, 1.0), 0, .4)
    for i in range(5):
        m.add(slash(r, .09, 4000, 9000, 3, 1.0), i * .04, .35)
        m.add(modal(mt(86 + i * 2), GLASS, .5, .1, r), .12 + i * .035, .5)
    m.add(shatter(.5, r, 3500, 11000, 22, .05), .25, .6)
    m.add(thump(170, 70, .15, .03, .06), .25, .4)
    return reverb(m.render(), .7, .15, 7500, seed=59)


@sfx('sk_frost_2', -3)
def _(r):
    m = Mix()
    m.add(riser(.9, 1500, 10000, r, 2.5, 0, 1.3), 0, .35)
    m.add(crackle(.9, curve(.9, [(0, 300), (.5, 2500), (.9, 200)]), r, 6000, 1.0, 2500), 0, .6)
    for i in range(7):
        m.add(modal(mt(84 + [0, 3, 7, 10, 12, 15, 19][i]), GLASS, .6, .12, r), .1 + i * .08, .4)
    m.add(thump(110, 45, .4, .05, .15, 1.4), .8, .9)
    m.add(modal(mt(60), BELL, 1.3, .5, r), .8, .25)
    m.add(shatter(.4, r, 4000, 11000, 18, .04), .8, .5)
    return reverb(m.render(), 1.2, .22, 7500, seed=60)


@sfx('sk_frost_3', -3)
def _(r):
    d = 1.7
    n = N(d)
    m = Mix()
    m.add(gust(d, r, 500, 3500, .9, 1.0), 0, 1.0)
    h = sweep(noise(n, r), curve(d, [(0, 1100), (d * .5, 1900), (d, 1000)], log=True) * (1 + .1 * np.sin(2 * np.pi * 1.7 * np.arange(n) / SR)), 'bp', 14)
    m.add(h / (h.std() + 1e-9) * .12 * bump(d, .5, 1.0), 0, 1.0)
    m.add(hp(noise(n, r), 5000, 1) * bump(d, .5, 1.0) * .1, 0, 1.0)
    m.add(sparkle(d, r, 30, 4000, 11000, .05), 0, .3)
    return reverb(m.render(), .8, .15, 6500, seed=61)


@sfx('sk_frost_hit', -4)
def _(r):
    m = Mix()
    m.add(tick(r, .02, 3500, .004), 0, .8)
    m.add(shatter(.4, r, 3500, 11000, 26, .05), 0, .8)
    m.add(modal(mt(91), GLASS, .6, .2, r), 0, .4)
    m.add(thump(200, 80, .12, .02, .05), 0, .5)
    return reverb(m.render(), .5, .12, 7500, seed=62)


@sfx('ult_frost', 0)
def _(r):
    m = Mix()
    cl = 2.4
    m.add(gust(cl, r, 300, 4000, .9, 1.0) * np.linspace(.1, 1, N(cl)) ** 1.5, 0, 1.0)
    m.add(reverse(boom(1.4, r, 45, 1.0, noise_f=1000)), cl - 1.4, .8)
    for k, nn in enumerate([60, 67, 72, 76, 79, 84, 88]):
        m.add(modal(mt(nn), PLATE, 2.5, .8, r, .002), .2 + k * .3, .25)
    m.add(riser(cl, 800, 12000, r, 2.0, 0, 2.0), 0, .4)
    m.add(crackle(cl, curve(cl, [(0, 100), (cl, 3000)]), r, 6000, 1.0, 2500), 0, .6)
    m.add(tonecloud([mt(72), mt(79), mt(84), mt(88)], cl, r, .5, cl * .9, .1), 0, .6)
    # cero absoluto: corte de aire y quiebre
    m.add(shatter(1.5, r, 2500, 12000, 80, .06), cl, 1.0)
    m.add(boom(1.3, r, 42, 1.0, noise_f=900), cl, 1.0)
    m.add(tick(r, .03, 3000, .008), cl, 1.0)
    m.add(modal(mt(96), GLASS, 1.5, .5, r), cl, .5)
    m.add(modal(mt(84), BELL, 1.7, .6, r), cl, .4)
    m.add(gust(1.2, r, 800, 3000, .9, 1.0), cl, .5)
    return reverb(m.render(), 1.4, .3, 7500, seed=63)


# ============================================================ VERDANT (madera, hojas, crecimiento)
def _wood(f, dur, r, g=1.0):
    return modal(f, [(1, 1), (2.4, .35), (4.1, .15)], dur, .06, r, .01, .6) * g


def _leaves(dur, r, g=1.0):
    n = N(dur)
    y = hp(noise(n, r), 3500, 2)
    am = np.abs(lp(noise(n, r), 25, 1))
    am = am / (am.max() + 1e-9)
    return y * am ** 1.5 * bump(dur, .4, 1.0) * g * .4


@sfx('sk_verdant_1', -3)
def _(r):
    m = Mix()
    m.add(whoosh(.25, [(0, 500), (.25, 3500)], r, 1.0, .6, 1.0), 0, .6)
    m.add(sat(hp(noise(N(.06), r), 1500, 2) * expdec(.06, .01, .0003), 4), .2, .9)
    m.add(creak(.35, r, 40, 70, (500, 1500), 8), 0, .4)
    m.add(_leaves(.5, r), .1, .8)
    m.add(_wood(260, .2, r), .2, .6)
    return reverb(m.render(), .5, .1, 5000, seed=64)


@sfx('sk_verdant_2', -3)
def _(r):
    m = Mix()
    for i, nn in enumerate([60, 64, 67, 72, 76, 79]):
        m.add(_wood(mt(nn + 12), .3, r), i * .1, .55)
    m.add(_leaves(1.2, r), 0, 1.0)
    m.add(creak(.9, r, 35, 55, (400, 1100), 6), 0, .3)
    m.add(sparkle(.9, r, 20, 3000, 9000, .07), .3, .3)
    m.add(choir([mt(55), mt(62)], 1.0, r, ('u', 'o'), .3, .5, g=.5), .1, .5)
    return reverb(m.render(), .9, .2, 5500, seed=65)


@sfx('sk_verdant_3', -3)
def _(r):
    m = Mix()
    m.add(thump(120, 45, .3, .05, .12, 1.4), 0, .9)
    m.add(debris(.6, r, 30, 300, 2000, .05), 0, .8)
    m.add(creak(1.0, r, 28, 55, (250, 900), 7, 1.5), .02, .8)
    m.add(creak(.7, r, 40, 80, (400, 1200), 8), .3, .5)
    for i in range(4):
        m.add(_wood(r.uniform(150, 350), .25, r), .1 + i * .1, .5)
    m.add(_leaves(.8, r), .2, .6)
    return reverb(m.render(), .7, .12, 4500, seed=66)


@sfx('sk_verdant_hit', -4)
def _(r):
    m = Mix()
    m.add(_wood(300, .25, r), 0, 1.0)
    m.add(tick(r, .015, 2000, .004), 0, .6)
    m.add(thump(150, 70, .12, .02, .05), 0, .6)
    m.add(_leaves(.3, r), .01, .8)
    return m.render()


@sfx('ult_verdant', 0)
def _(r):
    m = Mix()
    cl = 2.4
    m.add(rumble(cl + 1, r, 80, 3, .5, env=swell(cl + 1, cl * .9, .8)), 0, 1.4)
    m.add(creak(cl, r, 22, 50, (200, 900), 6, 1.4) * swell(cl, .5, .3), 0, .8)
    m.add(creak(cl - .5, r, 30, 60, (350, 1100), 8) * swell(cl - .5, .5, .3), .4, .6)
    m.add(_leaves(cl + 1, r, 1.3), 0, 1.0)
    m.add(gust(cl + .5, r, 400, 2500, 1.0, 1.0) * np.linspace(.1, 1, N(cl + .5)), 0, .5)
    m.add(choir([mt(43), mt(50), mt(55)], cl, r, ('u', 'o'), 1.3, .3, nv=4), 0, .8)
    for k in range(7):
        m.add(thump(90, 50, .3, .04, .1, 1.3) + .6 * _wood(r.uniform(120, 240), .3, r), .3 + k * .33, .35 + k * .05)
    m.add(boom(1.3, r, 45, 1.0, noise_f=900), cl, 1.0)
    m.add(_wood(180, .5, r), cl, .8)
    m.add(choir([mt(43), mt(50), mt(55), mt(62), mt(67)], 1.6, r, ('o', 'a'), .1, 1.0, nv=4), cl, 1.0)
    for i, nn in enumerate([67, 72, 76, 79, 84, 88]):
        m.add(_wood(mt(nn + 12), .4, r), cl + .1 + i * .08, .4)
    m.add(sparkle(1.4, r, 50, 3000, 10000, .1), cl, .35)
    m.add(_leaves(1.4, r, 1.2), cl, 1.0)
    return reverb(m.render(), 1.4, .28, 4800, seed=67)


# ============================================================ BLOOD (liquido, latidos, desgarro)
def _tear(dur, r, g=1.0):
    n = N(dur)
    y = sweep(noise(n, r), curve(dur, [(0, 2500), (dur, 500)], log=True), 'bp', 1.5)
    am = .6 + .4 * np.abs(lp(noise(n, r), 60, 1)) * 3
    return y * am * expdec(dur, dur * .5, .002) * g


@sfx('sk_blood_1', -3)
def _(r):
    m = Mix()
    m.add(slash(r, .16, 1200, 5000, 1.8, 1.0), 0, .9)
    m.add(squelch(.3, r, 1000), .12, 1.0)
    m.add(_tear(.25, r), .1, .7)
    m.add(thump(110, 45, .25, .04, .1, 1.4), .12, .9)
    m.add(bubbles(.3, r, 8, 150, 400), .15, .5)
    return reverb(m.render(), .5, .1, 4000, seed=68)


@sfx('sk_blood_2', -3)
def _(r):
    m = Mix()
    m.add(heartbeat(r), 0, 1.0)
    m.add(heartbeat(r), .6, .9)
    m.add(bubbles(1.2, r, 28, 120, 450), 0, .6)
    m.add(voice(.9, 85, r, 'o', 'u', scale=.75, dist=2.5, breath=.5, growl=.5, growl_f=30, env=bump(.9, .5, 1.2)), .2, .45)
    m.add(squelch(.5, r, 700), .55, .6)
    m.add(whisper(1.0, r, 6, ('o', 'e'), 1.0, 700, 2), .1, .3)
    return reverb(m.render(), .8, .15, 3500, seed=69)


@sfx('sk_blood_3', -3)
def _(r):
    d = 1.4
    n = N(d)
    t = np.arange(n) / SR
    m = Mix()
    rot = .55 + .45 * np.sin(2 * np.pi * 4.5 * t) ** 2
    m.add(whoosh(d, [(0, 350), (d * .5, 1600), (d, 500)], r, .8, .45, 1.2, 'pink') * rot, 0, 1.0)
    m.add(chain(d * .8, r, 10, 1200, 3200, .045), .1, .35)
    for k in range(4):
        m.add(squelch(.2, r, 900), .25 + k * .26, .6)
        m.add(_tear(.15, r), .25 + k * .26, .5)
    m.add(modal(2400, BAR, .7, .2, r), d * .45, .1)
    return reverb(m.render(), .6, .1, 4000, seed=70)


@sfx('sk_blood_hit', -4)
def _(r):
    m = Mix()
    m.add(_tear(.25, r), 0, 1.0)
    m.add(squelch(.22, r, 900), 0, 1.0)
    m.add(thump(120, 55, .18, .03, .07, 1.3), 0, .8)
    m.add(bubbles(.3, r, 6, 150, 350), .05, .4)
    return m.render()


@sfx('ult_blood', 0)
def _(r):
    m = Mix()
    cl = 2.5
    hb = Mix()
    t0 = 0.0
    gap = .85
    while t0 < cl - .1:
        hb.add(heartbeat(r, 1.0), t0, .6 + .5 * (t0 / cl))
        t0 += gap
        gap = max(.3, gap * .82)
    m.add(hb.render(cl), 0, 1.0)
    m.add(drone(cl + 1, 41, r, 1.0, .01, 3, 400, cl * .9, .6), 0, 1.0)
    m.add(bubbles(cl, r, 45, 100, 450) * np.linspace(.2, 1, N(cl)), 0, .5)
    m.add(whisper(cl, r, 6, ('o', 'e'), 1.0, 700, 3), 0, .4)
    m.add(reverse(voice(.9, curve(.9, [(0, 120), (.9, 600)]), r, 'e', 'i', scale=1.1, dist=3, breath=.3, env=bump(.9, .5, 1.0))), cl - .9, .6)
    m.add(riser(cl, 200, 4000, r, 1.2, .3, 2.0), 0, .4)
    m.add(thump(70, 28, 1.3, .1, .5, 1.6), cl, 1.0)
    m.add(boom(1.3, r, 40, 1.0, noise_f=900), cl, .9)
    m.add(_tear(.9, r), cl, 1.0)
    m.add(squelch(1.0, r, 1100), cl, 1.0)
    for k in range(4):
        m.add(_tear(.3, r), cl + .1 + k * .12, .6)
    m.add(bell(mt(41), 1.7, 1.0, r), cl, .5)
    m.add(voice(1.2, curve(1.2, [(0, 400), (.15, 650), (1.2, 300)]), r, 'a', 'e', scale=1.2, dist=3.5, breath=.5, env=bump(1.2, .1, 1.0)), cl, .6)
    m.add(bubbles(1.4, r, 25, 100, 350), cl + .3, .5)
    return reverb(m.render(), 1.4, .28, 3500, seed=71)


# ============================================================ EARTH (impacto sordo, grava, terremoto)
@sfx('sk_earth_1', -3)
def _(r):
    m = Mix()
    m.add(whoosh(.2, [(0, 150), (.2, 700)], r, 1.0, .7, 1.0, 'pink'), 0, .5)
    m.add(boom(.7, r, 55, 1.0, noise_f=700), .15, 1.0)
    m.add(tick(r, .03, 900, .008), .15, .8)
    m.add(debris(.5, r, 22, 300, 2500, .05), .15, .7)
    m.add(modal(220, BAR, .5, .12, r), .15, .35)
    return reverb(m.render(), .5, .1, 3500, seed=72)


@sfx('sk_earth_2', -3)
def _(r):
    m = Mix()
    m.add(debris(1.0, r, 55, 250, 2200, .06, False), 0, .8)
    m.add(thump(90, 45, .4, .06, .15, 1.4), .0, .8)
    m.add(modal(160, PLATE, 1.2, .5, r), .0, .5)
    m.add(rumble(1.0, r, 100, 8, .5, env=bump(1.0, .3, 1.0)), 0, 1.2)
    m.add(creak(.8, r, 25, 45, (200, 700), 5, 1.5), 0, .35)
    return reverb(m.render(), .7, .12, 3500, seed=73)


@sfx('sk_earth_3', -2)
def _(r):
    m = Mix()
    d = 1.6
    m.add(rumble(d, r, 90, 7, .7, env=bump(d, .3, .9)), 0, 2.0)
    m.add(thump(70, 32, .6, .1, .25, 1.5), 0, .9)
    m.add(debris(d, r, 80, 250, 2800, .06, False), 0, .8)
    for k in range(4):
        m.add(boom(.5, r, 50 + 6 * k, .6, noise_f=600), k * .3, .6)
    m.add(tick(r, .03, 800, .01), .0, .7)
    return reverb(m.render(), .9, .15, 3000, seed=74)


@sfx('sk_earth_hit', -4)
def _(r):
    m = Mix()
    m.add(boom(.45, r, 70, .9, noise_f=800), 0, 1.0)
    m.add(debris(.4, r, 22, 300, 2500, .05), 0, .7)
    m.add(tick(r, .02, 900, .006), 0, .7)
    return m.render()


@sfx('ult_earth', 0)
def _(r):
    m = Mix()
    cl = 2.4
    m.add(rumble(cl + 1.3, r, 70, 6, .7, env=swell(cl + 1.3, cl * .85, 1.5)), 0, 2.2)
    m.add(lp(noise(N(cl), r, 'brown'), 200, 2) * np.linspace(.1, 1, N(cl)) ** 2 * 1.5, 0, 1.0)
    for k, tt_ in enumerate([.3, 1.0, 1.55, 1.95, 2.25, 2.5]):
        m.add(boom(.6, r, 55 - k * 2, .8, noise_f=500), tt_, .35 + k * .09)
        m.add(debris(.5, r, 14, 250, 2000, .05), tt_, .35)
    m.add(creak(cl, r, 20, 45, (180, 700), 5, 1.6), .2, .8)
    m.add(riser(cl, 100, 1800, r, .8, 0, 2.2, 'brown'), 0, .5)
    # cataclismo
    m.add(thump(65, 24, 1.5, .1, .5, 1.6), cl, 1.0)
    m.add(boom(1.6, r, 36, 1.0, noise_f=1200), cl, 1.0)
    m.add(tick(r, .04, 700, .012), cl, 1.0)
    m.add(debris(1.5, r, 110, 250, 3500, .07), cl, .9)
    m.add(modal(80, PLATE, 2.0, .8, r), cl, .6)
    m.add(modal(mt(36), BELL, 2.0, .7, r), cl, .3)
    return reverb(m.render(), 1.3, .3, 2800, seed=75)


# ============================================================ ASTRAL (tonos cosmicos, barrido espacial, gravedad)
@sfx('sk_astral_1', -3)
def _(r):
    d = .95
    n = N(d)
    t = np.arange(n) / SR
    m = Mix()
    f = curve(d, [(0, 3500), (d * .6, 900), (d, 400)], log=True)
    m.add(fm(f, 1.5, 2 * np.exp(-t / .3), n) * bump(d, .2, 1.0), 0, .6)
    m.add(whoosh(d, [(0, 7000), (d, 600)], r, 2.0, .3, 1.2), 0, .5)
    m.add(sparkle(d, r, 40, 3000, 12000, .08, 1.0), 0, .4)
    m.add(modal(mt(91), GLASS, .8, .3, r), .5, .3)
    m.add(thump(180, 70, .25, .04, .1, 1.2), .52, .5)
    return reverb(m.render(), 1.0, .25, 7000, seed=76)


@sfx('sk_astral_2', -3)
def _(r):
    d = 1.5
    n = N(d)
    t = np.arange(n) / SR
    m = Mix()
    f = curve(d, [(0, 700), (d, 55)], log=True)
    m.add(fm(f, 1.01, 2.5 * (1 - t / d), n) * bump(d, .3, 1.0), 0, .8)
    m.add(reverse(whoosh(d, [(0, 200), (d, 4000)], r, 1.5, .8, 1.0)), 0, .5)
    m.add(drone(d, 45, r, 1.0, .01, 3, 400, .5, .5), 0, 1.0)
    lfo = .6 + .4 * np.sin(2 * np.pi * (3 + 6 * t / d) * t)
    m.add(tonecloud([mt(55), mt(58)], d, r, .4, .3, .4) * lfo, 0, 1.0)
    m.add(thump(90, 30, .5, .08, .2, 1.4), .15, .7)
    return reverb(m.render(), 1.2, .25, 4500, seed=77)


@sfx('sk_astral_3', -3)
def _(r):
    d = .95
    n = N(d)
    t = np.arange(n) / SR
    m = Mix()
    f = curve(d, [(0, 200), (.6, 2500)], log=True)
    m.add(fm(f, 2.01, 3 * (t / d), n) * bump(d, .55, 1.0), 0, .5)
    m.add(riser(.6, 400, 9000, r, 1.2, 0, 1.5), 0, .5)
    m.add(boom(.5, r, 90, .6, noise_f=3000), .55, .7)
    m.add(modal(mt(96), GLASS, .8, .25, r), .58, .5)
    m.add(sparkle(.6, r, 30, 3500, 12000, .06), .55, .4)
    m.add(reverse(whoosh(.3, [(0, 300), (.3, 7000)], r, 1.0, .5)), .3, .3)
    return reverb(m.render(), .9, .2, 7000, seed=78)


@sfx('sk_astral_hit', -4)
def _(r):
    d = .5
    n = N(d)
    t = np.arange(n) / SR
    m = Mix()
    f = curve(d, [(0, 1800), (d, 600)], log=True)
    m.add(fm(f, 1.41, 3 * np.exp(-t / .12), n) * expdec(d, .15, .001), 0, .7)
    m.add(modal(mt(91), GLASS, .5, .2, r), 0, .4)
    m.add(thump(200, 70, .2, .03, .08), 0, .6)
    m.add(sparkle(.4, r, 18, 3500, 11000, .06), 0, .3)
    return reverb(m.render(), .6, .15, 7000, seed=79)


@sfx('ult_astral', 0)
def _(r):
    m = Mix()
    cl = 2.5
    n = N(cl)
    t = np.arange(n) / SR
    cloud = tonecloud([mt(45), mt(52), mt(57), mt(64)], cl, r, .6, cl * .95, .05)
    m.add(cloud * (1 + .5 * np.sin(2 * np.pi * (1 + 7 * (t / cl) ** 2) * t)) * .7, 0, 1.0)
    m.add(riser(cl, 200, 11000, r, 1.5, .3, 2.2), 0, .5)
    f = curve(cl, [(0, 600), (cl, 45)], log=True)
    m.add(fm(f, 1.01, 2.0, n) * (t / cl) ** 2 * .5, 0, .8)
    m.add(sparkle(cl, r, 70, 2500, 12000, .08, .6), 0, .4)
    m.add(reverse(boom(1.0, r, 60, 1.0, noise_f=2000)), cl - 1.0, .8)
    # supernova
    sw = sweep(noise(N(1.6), r), curve(1.6, [(0, 12000), (1.6, 150)], log=True), 'lp') * expdec(1.6, .5, .001)
    m.add(sw, cl + .1, 1.0)
    m.add(boom(1.6, r, 36, 1.0, noise_f=3000), cl + .1, 1.0)
    m.add(thump(65, 24, 1.6, .1, .6, 1.6), cl + .1, .9)
    m.add(choir([mt(40), mt(52), mt(59), mt(64), mt(71), mt(76)], 1.8, r, ('a', 'o'), .03, .9, nv=4), cl + .1, .8)
    m.add(tonecloud([mt(88), mt(95), mt(100)], 1.6, r, .5, .02, 1.0), cl + .1, .6)
    m.add(sparkle(1.6, r, 80, 3000, 13000, .12), cl + .1, .5)
    return reverb(m.render(), 1.5, .3, 6500, seed=80)


# ============================================================ STEEL (acero, sables, resonancia)
@sfx('sk_steel_1', -3)
def _(r):
    m = Mix()
    for i in range(8):
        a, b = (2800, 8000) if i % 2 == 0 else (8500, 3000)
        m.add(slash(r, .1, a, b, 3, 1.0), i * .075, .5)
        m.add(modal(r.uniform(2800, 4800), BAR, .35, .08, r), i * .075 + .05, .15)
    m.add(ksum([mt(84), mt(88), mt(91)], .9, r, .996, .8, .08, .25), .25, 1.0)
    m.add(sparkle(.5, r, 15, 5000, 12000, .04), .3, .3)
    return reverb(m.render(), .6, .12, 7000, seed=81)


@sfx('sk_steel_2', -3)
def _(r):
    m = Mix()
    m.add(thump(240, 90, .2, .02, .06, 1.5), 0, .9)
    m.add(tick(r, .02, 1500, .004), 0, .9)
    m.add(modal(760, PLATE, 1.2, .5, r, .003), 0, 1.0)
    m.add(ksum([mt(55), mt(62), mt(67), mt(74)], 1.1, r, .9985, .5, .02, .35), 0, 1.0)
    m.add(modal(2200, BAR, .9, .3, r), 0, .35)
    return reverb(m.render(), .7, .15, 6000, seed=82)


@sfx('sk_steel_3', -3)
def _(r):
    m = Mix()
    d = 1.2
    n = N(d)
    sc = sweep(noise(N(.5), r), curve(.5, [(0, 1500), (.5, 4500)], log=True), 'bp', 5)
    sc *= swell(.5, .05, .1) * (.5 + .5 * np.sin(2 * np.pi * 50 * np.arange(len(sc)) / SR))
    m.add(sc / (sc.std() + 1e-9) * .2, 0, 1.0)
    m.add(whoosh(.5, [(0, 300), (.5, 2000)], r, .9, .8, 1.2, 'pink'), .2, .7)
    m.add(thump(200, 60, .4, .03, .12, 1.6), .62, 1.0)
    m.add(modal(900, PLATE, 1.0, .35, r), .62, .9)
    m.add(tick(r, .02, 1800, .004), .62, .8)
    m.add(boom(.5, r, 70, .6, noise_f=1500), .62, .6)
    m.add(ksum([mt(60), mt(67)], .6, r, .997, .6, 0, .3), .62, .8)
    return reverb(m.render(), .6, .12, 5500, seed=83)


@sfx('sk_steel_hit', -4)
def _(r):
    m = Mix()
    m.add(tick(r, .02, 2000, .004), 0, .9)
    m.add(modal(1250, PLATE, .6, .17, r, .004), 0, 1.0)
    m.add(modal(3100, BAR, .4, .09, r), 0, .5)
    m.add(thump(260, 100, .12, .02, .05, 1.4), 0, .7)
    m.add(ks(mt(86), .5, r, .995, .8), 0, .25)
    return reverb(m.render(), .4, .1, 6500, seed=84)


@sfx('ult_steel', 0)
def _(r):
    m = Mix()
    cl = 2.4
    # desenvaine
    sc = sweep(noise(N(.9), r), curve(.9, [(0, 1200), (.9, 6000)], log=True), 'bp', 4)
    sc *= swell(.9, .1, .2) * (.5 + .5 * np.sin(2 * np.pi * 60 * np.arange(len(sc)) / SR))
    m.add(sc / (sc.std() + 1e-9) * .2, 0, 1.0)
    m.add(modal(mt(88), BAR, 1.5, .6, r), .8, .3)
    # enjambre de hojas en aceleracion
    t0 = .9
    gap = .22
    k = 0
    while t0 < cl - .05:
        a, b = (2600, 8500) if k % 2 == 0 else (8800, 2800)
        m.add(slash(r, .09, a, b, 3, 1.0), t0, .3 + .5 * (t0 / cl))
        if k % 2:
            m.add(modal(r.uniform(2500, 5000), BAR, .3, .07, r), t0 + .05, .12)
        t0 += gap
        gap = max(.035, gap * .84)
        k += 1
    m.add(ksum([mt(48), mt(55), mt(60), mt(64), mt(67), mt(72)], cl + 1.5, r, .9985, .6, .25, .3), .3, 1.0)
    m.add(riser(cl, 800, 11000, r, 2.0, 0, 2.0), 0, .35)
    # tajo final
    m.add(reverse(whoosh(.35, [(0, 400), (.35, 8000)], r, 1.0, .5)), cl - .35, .6)
    m.add(thump(180, 40, 1.2, .05, .45, 1.7), cl, 1.0)
    m.add(tick(r, .03, 1800, .008), cl, 1.0)
    m.add(modal(900, PLATE, 1.8, .6, r), cl, .9)
    m.add(modal(1650, PLATE, 1.5, .4, r), cl, .6)
    m.add(boom(1.5, r, 55, 1.0, noise_f=2000), cl, .9)
    m.add(ksum([mt(84), mt(91), mt(96)], 1.6, r, .9985, .9, .02, .35), cl, 1.0)
    m.add(bell(mt(79), 1.7, .7, r), cl, .4)
    m.add(sparkle(1.4, r, 60, 4000, 13000, .1), cl, .35)
    return reverb(m.render(), 1.3, .25, 6500, seed=85)
