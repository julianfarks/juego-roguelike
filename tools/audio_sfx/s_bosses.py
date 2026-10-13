from recipes import *
from bosslib import *
from reg import sfx, add

B = ['rey_exanime', 'coloso_magma', 'reina_escarcha', 'devorador_vacio', 'ent_ancestral', 'titan_tormenta',
     'matriarca_sangre', 'guardian_eclipse', 'cazador']

# perfil de voz + reverb por jefe
P = dict(
    rey_exanime=dict(f0=75, v0='o', v1='a', scale=.8, dist=3.0, growl=.5, growl_f=48, breath=.5, jitter=.04, low=.5, rv=(1.6, .3, 3500, 101)),
    coloso_magma=dict(f0=48, v0='a', v1='o', scale=.5, dist=4.0, growl=.75, growl_f=32, breath=.4, jitter=.05, low=.7, rv=(1.3, .25, 3000, 102)),
    reina_escarcha=dict(f0=330, v0='a', v1='i', scale=1.05, dist=1.6, growl=.1, growl_f=60, breath=.5, jitter=.015, low=.35, hi=.25, vib=(6, .025), rv=(1.8, .3, 7000, 103)),
    devorador_vacio=dict(f0=62, v0='o', v1='u', scale=.7, dist=2.5, growl=.4, growl_f=25, breath=.7, jitter=.05, low=.7, nv=3, hi=.2, rv=(2.2, .35, 4000, 104)),
    ent_ancestral=dict(f0=55, v0='u', v1='o', scale=.6, dist=2.8, growl=.7, growl_f=26, breath=.6, jitter=.06, low=.7, rv=(1.2, .2, 3500, 105)),
    titan_tormenta=dict(f0=52, v0='a', v1='o', scale=.6, dist=5.0, growl=.5, growl_f=40, breath=.35, jitter=.03, low=.7, rv=(1.6, .28, 4500, 106)),
    matriarca_sangre=dict(f0=520, v0='a', v1='e', scale=1.1, dist=3.0, growl=.2, growl_f=70, breath=.45, jitter=.03, low=.3, hi=.3, vib=(7, .03), rv=(1.8, .3, 5000, 107)),
    guardian_eclipse=dict(f0=105, v0='o', v1='a', scale=.85, dist=2.0, growl=.2, growl_f=60, breath=.3, jitter=.01, low=.5, hi=.25, nv=3, vib=(5, .015), rv=(2.2, .3, 6000, 108)),
    cazador=dict(f0=44, v0='a', v1='o', scale=.55, dist=4.0, growl=.7, growl_f=36, breath=.5, jitter=.07, low=.8, hi=.3, nv=3, rv=(2.0, .3, 3500, 109)),
)


def R(x, b, k=1.0):
    t, w, d, s = P[b]['rv']
    return reverb(x, t, w * k, d, seed=s)


def crack(r, g=1.0, f=800):
    return sat(hp(noise(N(.06), r), f, 2) * expdec(.06, .012, .0003), 4) * g


def steam(r, d=.5, g=1.0):
    return hp(noise(N(d), r), 2500, 1) * bump(d, .15, 1.5) * .25 * g


def ratchet(r, d, rate0, rate1, f=2500, g=1.0):
    n = N(d)
    t = np.arange(n) / SR
    rate = curve(d, [(0, rate0), (d, rate1)])
    ph = np.cumsum(rate) / SR % 1.0
    pulse = (ph < .08) * 1.0
    y = reson(pulse * noise(n, r), f, 3) * 3
    return y * swell(d, .02, .05)


def gunshot(r, g=1.0):
    m = Mix()
    m.add(sat(hp(noise(N(.2), r), 400, 2) * expdec(.2, .03, .0002), 5), 0, 1.0)
    m.add(thump(200, 50, .3, .02, .1, 1.5), 0, 1.0)
    m.add(sweep(noise(N(.4), r), curve(.4, [(0, 5000), (.4, 400)], log=True), 'lp') * expdec(.4, .1, .0004), 0, .6)
    m.add(modal(2200, BAR, .3, .08, r), 0, .15)
    return m.render() * g


# ------------------------------------------------------------------ swings
def swing(b, r, d, k):
    m = Mix()
    g = 1.0
    if b == 'rey_exanime':
        m.add(whoosh(d, [(0, 350), (d * .5, 2200), (d, 700)], r, 1.0, .55, 1.3, 'pink'), 0, 1.0)
        m.add(creak(d * .7, r, 40, 80, (800, 2200), 10, 2), 0, .18)
        m.add(modal(2300, BAR, .5, .15, r), d * .5, .1)
    elif b == 'coloso_magma':
        m.add(sweep(noise(N(d), r, 'pink'), curve(d, [(0, 120), (d * .55, 700), (d, 180)], log=True), 'lp') * bump(d, .55, 1.5), 0, 1.0)
        m.add(lp(noise(N(d), r, 'brown'), 130, 2) * bump(d, .6, 1.5) * 2, 0, .8)
        m.add(fireroar(d, r, 600, .5), 0, .35)
    elif b == 'reina_escarcha':
        m.add(whoosh(d, [(0, 1800), (d * .5, 6000), (d, 3000)], r, 2.0, .5, 1.3), 0, 1.0)
        m.add(sparkle(d, r, 8 + 4 * k, 4000, 11000, .05), 0, .35)
        m.add(modal(mt(92), GLASS, .5, .15, r), d * .4, .15)
    elif b == 'devorador_vacio':
        m.add(whoosh(d, [(0, 500), (d * .6, 3500), (d, 900)], r, 1.0, .6, 1.5), 0, .8)
        m.add(crack(r, .7, 1200), d * .55, 1.0)
        m.add(squelch(d * .6, r, 900), d * .5, .6)
        m.add(whisper(d, r, 8, ('i', 'e'), 1.0, 1200, 1), 0, .25)
    elif b == 'ent_ancestral':
        m.add(whoosh(d, [(0, 200), (d * .5, 900), (d, 300)], r, .8, .5, 1.3, 'pink'), 0, 1.0)
        m.add(creak(d, r, 25, 55, (300, 1100), 7), 0, .35)
        n = N(d)
        lv = hp(noise(n, r), 3500, 2) * np.abs(lp(noise(n, r), 25, 1))
        m.add(lv / (lv.std() + 1e-9) * .15 * bump(d, .5, 1), 0, 1.0)
        m.add(crack(r, .5, 500), d * .6, 1.0)
    elif b == 'titan_tormenta':
        m.add(whoosh(d, [(0, 150), (d * .55, 900), (d, 250)], r, .8, .55, 1.4, 'pink'), 0, 1.0)
        m.add(lp(noise(N(d), r, 'brown'), 150, 2) * bump(d, .6, 1.5) * 1.8, 0, .7)
        m.add(modal(900, PLATE, .6, .2, r), d * .5, .12)
        m.add(zap(d * .6, r, 3500, 600, 1.0), d * .3, .25)
    elif b == 'matriarca_sangre':
        for i in range(3):
            m.add(slash(r, d * .35, 1500 + 400 * i, 6500, 2.2, 1.0), i * d * .22, .8)
        m.add(squelch(d * .5, r, 1100), d * .5, .4)
        m.add(wingflap(d, r, 6, 1100, 1.0), 0, .3)
    elif b == 'guardian_eclipse':
        m.add(whoosh(d, [(0, 300), (d * .5, 2400), (d, 900)], r, 1.1, .5, 1.3, 'pink'), 0, 1.0)
        m.add(modal(2000, BAR, .8, .25, r), d * .45, .15)
        m.add(choir([mt(62)], d * .8, r, ('a', 'a'), .05, .2, g=.5), d * .25, .35)
    else:  # cazador: sierra-latigo
        m.add(ratchet(r, d, 40, 120, 2800), 0, .6)
        m.add(whoosh(d, [(0, 600), (d * .6, 4000), (d, 1200)], r, 1.4, .6, 1.2), 0, .6)
        m.add(crack(r, .8, 1500), d * .6, .9)
        m.add(chain(d * .6, r, 6, 1200, 3200, .04), d * .3, .3)
    return m.render()


def atk(b, r, k):
    mat, imp = MATS[b]
    p = P[b]
    m = Mix()
    if k == 1:
        d = .38
        m.add(swing(b, r, d, 1), 0, 1.0)
        m.add(bossvox(p, r, .35, 'atk'), 0, .45)
        m.add(imp(r, .8), d * .8, 1.0)
        return R(m.render(), b, .6)
    if k == 2:
        d = .7
        m.add(reverse(swing(b, r, .25, 2)) * .5, 0, 1.0)
        m.add(swing(b, r, d, 2), .2, 1.0)
        m.add(mat(r, .8), 0, .45)
        m.add(bossvox(p, r, .5, 'atk'), .1, .55)
        m.add(imp(r, .9), .75, 1.0)
        return R(m.render(), b, .7)
    d = .55
    m.add(reverse(swing(b, r, d, 3)) * .6, 0, 1.0)
    m.add(riser(d, 150, 2500, r, 1.0, .3, 2.0), 0, .35)
    m.add(bossvox(p, r, .6, 'atk'), .05, .55)
    m.add(imp(r, 1.2), d, 1.0)
    m.add(boom(.9, r, 46, 1.0, noise_f=1200), d, .8)
    m.add(debris(.7, r, 28, 300, 3000, .05), d, .5)
    m.add(mat(.8, r) if False else mat(r, .8), d, .3)
    return R(m.render(), b, .9)


# ------------------------------------------------------------------ step / cast
def step(b, r):
    m = Mix()
    if b == 'rey_exanime':
        m.add(thump(110, 45, .25, .03, .09, 1.4), 0, 1.0)
        m.add(chain(.35, r, 6, 800, 2200, .04), 0, .5)
        m.add(modal(1500, BONE, .15, .03, r, .02), .01, .5)
        m.add(modal(520, PLATE, .3, .08, r), 0, .3)
    elif b == 'coloso_magma':
        m.add(boom(.45, r, 50, 1.0, noise_f=700), 0, 1.0)
        m.add(modal(220, PLATE, .5, .12, r), .01, .4)
        m.add(lp(noise(N(.35), r), 500, 2) * expdec(.35, .1), 0, .6)
        m.add(crackle(.3, 600, r, 3000, 1.1, 1200) * expdec(.3, .1), .05, .4)
    elif b == 'reina_escarcha':
        m.add(gust(.5, r, 1500, 4500, 1.4, 1.0), 0, .6)
        m.add(sparkle(.4, r, 6, 3500, 9000, .06), 0, .5)
        m.add(thump(200, 110, .1, .02, .04), 0, .25)
    elif b == 'devorador_vacio':
        m.add(squelch(.45, r, 500), 0, .7)
        n = N(.5)
        t = np.arange(n) / SR
        m.add(sine(42, n) * (.5 + .5 * np.sin(2 * np.pi * 7 * t)) * bump(.5, .4, 1.0), 0, .8)
        m.add(whisper(.4, r, 9, ('i', 'e'), 1.0, 1400, 1), 0, .25)
    elif b == 'ent_ancestral':
        m.add(thump(75, 35, .4, .05, .14, 1.5), 0, 1.0)
        m.add(creak(.4, r, 30, 60, (300, 1000), 7), 0, .4)
        m.add(crack(r, .5, 500), .08, 1.0)
        m.add(debris(.3, r, 10, 300, 2000, .04), .02, .35)
    elif b == 'titan_tormenta':
        m.add(thump(70, 32, .4, .05, .14, 1.5), 0, 1.0)
        m.add(modal(180, PLATE, .6, .18, r), .01, .5)
        m.add(rumble(.5, r, 90, 6, .5, env=expdec(.5, .2, .005)), 0, 1.0)
        m.add(zap(.12, r, 4000, 800, 1.0), .02, .3)
    elif b == 'matriarca_sangre':
        m.add(wingflap(.35, r, 7, 1100, 1.0), 0, .8)
        m.add(modal(2100, BAR, .12, .02, r), .12, .3)
        m.add(hp(noise(N(.2), r), 3000, 1) * bump(.2, .3, 1.5) * .12, 0, 1.0)
    elif b == 'guardian_eclipse':
        m.add(thump(95, 42, .3, .04, .1, 1.5), 0, 1.0)
        m.add(modal(650, PLATE, .5, .12, r), 0, .5)
        m.add(chain(.35, r, 7, 900, 2600, .04), 0, .5)
    else:
        m.add(flesh_hit(r, 85), 0, 1.0)
        m.add(thump(75, 38, .3, .04, .1, 1.4), 0, .8)
        m.add(modal(2400, BONE, .1, .015, r), .05, .3)
        m.add(modal(2000, BONE, .1, .015, r), .09, .25)
    return m.render()


def cast(b, r):
    m = Mix()
    p = P[b]
    if b == 'rey_exanime':
        m.add(whisper(1.2, r, 6, ('o', 'e'), 1.0, 600, 3), 0, .7)
        m.add(scatter(1.0, r, 28, 500, 2200, BONE, .03, .8), .1, .8)
        m.add(thump(110, 45, .4, .05, .15, 1.4), .5, .8)
        m.add(debris(.5, r, 16, 300, 2000, .05), .5, .5)
        m.add(choir([mt(46), mt(53)], 1.0, r, ('o', 'o'), .3, .4, g=.6), .1, .7)
        m.add(bell(mt(41), 1.4, .6, r), .55, .35)
    elif b == 'coloso_magma':
        m.add(rumble(1.2, r, 100, 6, .5, env=bump(1.2, .4, 1.0)), 0, 1.4)
        m.add(bubbles(1.0, r, 30, 80, 300) * np.linspace(.2, 1, N(1.0)), 0, 1.0)
        m.add(fireroar(.8, r, 800, 1.0), .4, .9)
        m.add(boom(.8, r, 50, .9, noise_f=2000), .5, 1.0)
        m.add(debris(.6, r, 22, 300, 2500, .05), .5, .5)
    elif b == 'reina_escarcha':
        for i, nn in enumerate([72, 76, 79, 84, 88, 91]):
            m.add(modal(mt(nn), GLASS, .8, .2, r), i * .1, .55)
        m.add(gust(1.2, r, 800, 5000, 1.0, 1.0), 0, .6)
        m.add(crackle(1.0, curve(1.0, [(0, 200), (.6, 2000), (1.0, 100)]), r, 6000, 1.0, 2500), 0, .6)
        m.add(shatter(.4, r, 4000, 11000, 18, .04), .7, .5)
        m.add(sparkle(1.0, r, 25, 4000, 12000, .07), 0, .3)
    elif b == 'devorador_vacio':
        m.add(whisper(1.2, r, 7, ('i', 'e'), 1.0, 900, 3), 0, .6)
        n = N(1.0)
        t = np.arange(n) / SR
        f = curve(1.0, [(0, 120), (.6, 340), (1.0, 90)], log=True) * (1 + .03 * np.sin(2 * np.pi * 6 * t))
        m.add(fm(f, 1.5, 2.0, n) * bump(1.0, .45, 1.2) * .5, .05, 1.0)
        m.add(reverse(whoosh(.6, [(0, 200), (.6, 5000)], r, 1.2, .7)), 0, .5)
        m.add(boom(.5, r, 45, .7, noise_f=800), .65, .7)
    elif b == 'ent_ancestral':
        n = N(1.2)
        lv = hp(noise(n, r), 3000, 2) * np.abs(lp(noise(n, r), 18, 1))
        m.add(lv / (lv.std() + 1e-9) * .2 * bump(1.2, .4, 1.0), 0, 1.0)
        m.add(bubbles(1.0, r, 14, 400, 1200), .1, .6)
        for i, nn in enumerate([55, 59, 62, 67, 71]):
            m.add(modal(mt(nn), [(1, 1), (2.4, .35), (4.1, .15)], .5, .08, r, .01, .6), .1 + i * .13, .5)
        m.add(creak(.9, r, 28, 55, (300, 1000), 7), 0, .4)
        m.add(thump(90, 45, .3, .04, .1), .55, .6)
    elif b == 'titan_tormenta':
        m.add(gust(1.2, r, 300, 2500, .9, 1.0), 0, .8)
        m.add(rumble(1.2, r, 100, 4, .6, env=bump(1.2, .4, 1.0)), 0, 1.4)
        for i, t0 in enumerate((.35, .6, .85)):
            m.add(zap(.18, r, 4500, 600, 1.0), t0, .6)
            m.add(crack(r, .6, 700), t0, .8)
        m.add(crackle(1.1, 900, r, 4500, .9, 1800) * bump(1.1, .5, 1.0), 0, .6)
        m.add(thunder(1.0, r, False), .3, .7)
    elif b == 'matriarca_sangre':
        m.add(heartbeat(r), 0, .9)
        m.add(heartbeat(r), .5, .8)
        m.add(whoosh(.7, [(0, 400), (.7, 2500)], r, 1.0, .5, 1.3), .1, .5)
        m.add(bubbles(1.0, r, 22, 120, 450), 0, .6)
        m.add(whisper(1.0, r, 7, ('e', 'i'), 1.0, 1100, 2), 0, .4)
        m.add(voice(.5, curve(.5, [(0, 700), (.15, 1100), (.5, 800)]), r, 'e', 'i', scale=1.1, dist=3, breath=.4, env=bump(.5, .3, 1.0)), .6, .6)
        m.add(squelch(.4, r, 900), .8, .5)
    elif b == 'guardian_eclipse':
        m.add(choir([mt(50), mt(57), mt(62), mt(69)], 1.3, r, ('o', 'a'), .5, .4, nv=4), 0, 1.0)
        m.add(drone(1.3, 49, r, 1.0, .006, 3, 600, .4, .4), 0, .6)
        for i, nn in enumerate([74, 81, 86]):
            m.add(bell(mt(nn), 1.2, .5, r), .55 + i * .12, .5)
        m.add(sparkle(1.0, r, 25, 3000, 9000, .1), .3, .35)
        m.add(thump(100, 45, .4, .05, .15, 1.4), .55, .8)
    else:
        for i, t0 in enumerate((0, .2, .4)):
            m.add(gunshot(r, 1.0 - .1 * i), t0, 1.0)
        m.add(whisper(1.2, r, 6, ('o', 'e'), 1.0, 700, 2), 0, .5)
        n = N(1.0)
        f = curve(1.0, [(0, 300), (1.0, 50)], log=True)
        m.add(fm(f, 1.01, 2.0, n) * bump(1.0, .3, 1.2) * .4, .3, 1.0)
        m.add(squelch(.5, r, 700), .7, .5)
    return R(m.render(), b, .8)


# ------------------------------------------------------------------ intros
def intro_rey(r):
    m = Mix()
    d = 1.4
    n = N(d)
    t = np.arange(n) / SR
    gr = whoosh(d, [(0, 160), (d, 420)], r, 2.0, .55, 1.0, 'pink') * (.55 + .45 * np.sin(2 * np.pi * 21 * t))
    m.add(gr, 0, 1.0)
    m.add(rumble(d, r, 110, 8, .6, env=bump(d, .6, 1.0)), 0, 1.3)
    m.add(creak(1.2, r, 18, 32, (200, 700), 5, 1.6), .05, .5)
    m.add(boom(.9, r, 52, 1.0, noise_f=900), 1.4, 1.0)
    m.add(debris(.6, r, 25, 300, 2500, .05), 1.4, .6)
    m.add(modal(380, PLATE, 1.2, .4, r), 1.4, .4)
    m.add(scatter(1.3, r, 50, 500, 2200, BONE, .03, .6), 1.6, 1.0)
    m.add(chain(1.4, r, 14, 800, 2400, .04, .8), 1.8, .5)
    m.add(whisper(1.0, r, 5, ('o', 'e'), 1.0, 600, 2), 1.5, .5)
    m.add(voice(1.7, curve(1.7, [(0, 60), (.3, 88), (1.7, 68)]), r, 'o', 'a', scale=.8, dist=3, growl=.5, growl_f=45, breath=.5, env=bump(1.7, .3, .9)), 2.0, .9)
    m.add(bell(mt(33), 1.8, 1.0, r), 2.0, .35)
    return R(m.render(), 'rey_exanime', 1.0)


def intro_coloso(r):
    m = Mix()
    m.add(bubbles(3.2, r, 55, 60, 260), 0, 1.0)
    m.add(rumble(3.4, r, 90, 5, .6, env=swell(3.4, 1.8, 1.0)), 0, 1.3)
    m.add(crackle(3.2, 300, r, 2500, 1.2, 800), 0, .35)
    for k, t0 in enumerate([.4, .95, 1.5, 2.0, 2.5]):
        g = .5 + .12 * k
        m.add(thump(120 - 10 * k, 40, .4, .04, .12, 1.5), t0, g)
        m.add(modal(r.uniform(180, 420), PLATE, .9, .3, r, .02), t0, g * .7)
        m.add(tick(r, .02, 1200, .005), t0, g * .6)
        m.add(steam(r, .5, g), t0 + .05, 1.0)
        m.add(debris(.3, r, 8, 300, 2000, .04), t0, .3)
    m.add(boom(1.3, r, 40, 1.0, noise_f=1500), 3.0, 1.0)
    m.add(bossvox(P['coloso_magma'], r, 1.2, 'roar'), 3.0, .9)
    m.add(fireroar(1.2, r, 900, 1.0), 3.0, .7)
    return R(m.render(), 'coloso_magma', 1.0)


def intro_reina(r):
    m = Mix()
    d = 3.0
    n = N(d)
    m.add(gust(d, r, 300, 3500, .9, 1.0) * np.linspace(.2, 1, n) ** 1.2, 0, 1.0)
    h = sweep(noise(n, r), curve(d, [(0, 700), (d * .5, 1500), (d, 900)], log=True), 'bp', 14)
    m.add(h / (h.std() + 1e-9) * .12 * bump(d, .6, 1.0), 0, 1.0)
    for k in range(22):
        m.add(modal(mt(100 - k * 1.1), GLASS[:3], .5, .1, r), .1 + k * .1, .3)
    m.add(hp(noise(n, r), 5000, 1) * bump(d, .7, 1.2) * .1, 0, 1.0)
    m.add(boom(.8, r, 65, .8, noise_f=2000), 2.5, .8)
    m.add(shatter(1.0, r, 3000, 10000, 45, .05), 2.5, .8)
    m.add(modal(mt(60), BELL, 1.6, .7, r), 2.5, .4)
    m.add(choir([mt(69), mt(76), mt(81), mt(88)], 1.2, r, ('a', 'a'), .3, .6, nv=3, scale=1.1), 2.5, .8)
    m.add(sparkle(1.2, r, 40, 4000, 12000, .08), 2.5, .4)
    return R(m.render(), 'reina_escarcha', 1.0)


def intro_devorador(r):
    m = Mix()
    m.add(reverse(whoosh(1.5, [(0, 250), (1.5, 7000)], r, 1.3, .8, 1.0)), 0, .8)
    m.add(whisper(3.3, r, 6, ('i', 'e'), 1.0, 900, 4) * np.linspace(.2, 1, N(3.3)), .3, .8)
    # rasgadura
    z = sweep(hp(noise(N(.7), r), 1000, 2), curve(.7, [(0, 9000), (.7, 400)], log=True), 'lp')
    z *= expdec(.7, .2, .0005) * (.6 + .4 * np.sign(np.sin(2 * np.pi * 70 * np.arange(len(z)) / SR)))
    m.add(sat(z, 3), 1.45, 1.0)
    m.add(crackle(.8, curve(.8, [(0, 3000), (.8, 200)]), r, 5000, .9, 1800) * expdec(.8, .3), 1.45, .5)
    m.add(boom(1.4, r, 36, 1.0, noise_f=900), 1.5, 1.0)
    m.add(drone(2.4, 46, r, 1.0, .012, 3, 450, 1.0, .8), 1.5, .9)
    m.add(tonecloud([mt(51), mt(54), mt(58)], 2.2, r, .4, .8, .8), 1.6, .5)
    for t0 in (2.2, 2.85):
        m.add(thump(60, 38, .5, .06, .18, 1.5), t0, .8)
    m.add(bossvox(P['devorador_vacio'], r, 1.1, 'roar'), 2.6, .8)
    m.add(reverse(bossvox(P['devorador_vacio'], r, .7, 'atk')), 2.0, .4)
    return R(m.render(), 'devorador_vacio', 1.0)


def intro_ent(r):
    m = Mix()
    m.add(rumble(3.5, r, 80, 4, .6, env=swell(3.5, 2.0, 1.0)), 0, 1.5)
    for _ in range(26):
        m.add(crack(r, r.uniform(.3, .9), r.uniform(400, 1200)), r.uniform(.1, 2.7), 1.0)
    m.add(debris(2.6, r, 70, 200, 2500, .06, False), .1, .6)
    m.add(creak(2.4, r, 18, 40, (180, 700), 5, 1.8) * swell(2.4, .6, .5), .9, .9)
    m.add(creak(1.8, r, 30, 60, (350, 1100), 8), 1.3, .4)
    n = N(2.4)
    lv = hp(noise(n, r), 3500, 2) * np.abs(lp(noise(n, r), 18, 1))
    m.add(lv / (lv.std() + 1e-9) * .2 * swell(2.4, 1.2, .8), 1.4, 1.0)
    for t0 in (1.9, 2.6):
        m.add(imp_ent(r, 1.0), t0, .9)
        m.add(boom(.7, r, 45, .8, noise_f=700), t0, .7)
    m.add(bossvox(P['ent_ancestral'], r, 1.2, 'roar'), 2.6, .9)
    return R(m.render(), 'ent_ancestral', 1.0)


def intro_titan(r):
    m = Mix()
    m.add(gust(1.2, r, 300, 2500, .9, 1.0), 0, .7)
    m.add(rumble(1.2, r, 100, 4, .6, env=swell(1.2, 1.0, .05)), 0, 1.4)
    m.add(crackle(1.2, curve(1.2, [(0, 100), (1.2, 2500)]), r, 4500, .9, 1800), 0, .7)
    m.add(sat(hp(noise(N(.5), r), 600, 2) * expdec(.5, .07, .0002), 6), 1.15, 1.0)
    m.add(sweep(noise(N(.7), r), curve(.7, [(0, 8000), (.7, 400)], log=True), 'lp') * expdec(.7, .2, .0004), 1.15, .8)
    m.add(thunder(2.0, r, False), 1.2, 1.0)
    m.add(imp_titan(r, 1.2), 1.4, 1.0)
    m.add(boom(1.4, r, 38, 1.0, noise_f=1200), 1.4, .9)
    m.add(steam(r, .6, 1.2), 1.55, 1.0)
    m.add(crackle(1.6, curve(1.6, [(0, 2500), (1.6, 300)]), r, 4500, .9, 1800) * expdec(1.6, .7), 1.5, .6)
    m.add(bossvox(P['titan_tormenta'], r, 1.3, 'roar'), 2.3, .9)
    return R(m.render(), 'titan_tormenta', 1.0)


def intro_matriarca(r):
    m = Mix()
    sw = flapswarm(3.0, r, 110, 1.0)
    m.add(sw * swell(3.0, 1.0, 1.0), 0, 1.0)
    rot = .6 + .4 * np.sin(2 * np.pi * 2.2 * np.arange(N(2.6)) / SR)
    m.add(whoosh(2.6, [(0, 300), (1.3, 1800), (2.6, 500)], r, .8, .5, 1.0, 'pink') * rot, 0, .4)
    m.add(reverse(whoosh(.5, [(0, 400), (.5, 5000)], r, 1.2, .6)), 1.9, .4)
    m.add(thump(110, 50, .3, .04, .1, 1.4), 2.4, .9)
    m.add(squelch(.5, r, 900), 2.4, .7)
    m.add(heartbeat(r), 2.45, .8)
    m.add(bell(mt(48), 2.0, 1.0, r), 2.5, .35)
    m.add(bubbles(.8, r, 8, 120, 400), 2.5, .4)
    m.add(voice(.8, curve(.8, [(0, 800), (.15, 1000), (.8, 600)]), r, 'e', 'i', scale=1.1, dist=2.5, breath=.5, vib=(8, .04), env=bump(.8, .3, 1.0)), 2.65, .6)
    m.add(whisper(1.0, r, 8, ('e', 'i'), 1.0, 1100, 2), 2.6, .35)
    return R(m.render(), 'matriarca_sangre', 1.0)


def intro_guardian(r):
    m = Mix()
    m.add(boom(1.1, r, 45, 1.0, noise_f=1800), 0, 1.0)
    m.add(sat(hp(noise(N(.15), r), 700, 2) * expdec(.15, .03, .0003), 4), 0, .8)
    m.add(creak(.5, r, 40, 90, (500, 1500), 8), 0, .3)
    m.add(debris(.8, r, 30, 300, 3000, .05), 0, .5)
    m.add(gust(.6, r, 600, 3000, .9, 1.0), 0, .5)
    for k in range(4):
        t0 = .95 + k * .5
        g = .45 + .12 * k
        m.add(thump(100, 42, .3, .04, .1, 1.5), t0, g)
        m.add(modal(r.uniform(500, 800), PLATE, .5, .12, r), t0, g * .5)
        m.add(chain(.3, r, 6, 900, 2600, .04), t0, g * .4)
    m.add(choir([mt(50), mt(57), mt(62)], 2.4, r, ('o', 'a'), 1.3, .3, nv=4), .9, .9)
    m.add(bell(mt(62), 2.0, .9, r), 1.2, .35)
    m.add(bell(mt(69), 2.0, .9, r), 2.3, .35)
    m.add(modal(1800, BAR, 1.0, .35, r), 3.0, .3)
    m.add(thump(120, 40, .5, .05, .18, 1.6), 3.0, 1.0)
    m.add(tick(r, .02, 1800, .005), 3.0, .8)
    m.add(imp_sun(r, 1.0), 3.0, .8)
    m.add(choir([mt(50), mt(57), mt(62), mt(69), mt(74)], 1.0, r, ('a', 'a'), .02, .6, nv=4), 3.0, .8)
    for i, nn in enumerate([74, 81, 86, 93]):
        m.add(bell(mt(nn), 1.2, .45, r), 3.0 + i * .05, .4)
    return R(m.render(), 'guardian_eclipse', 1.0)


def intro_cazador(r):
    m = Mix()
    d = 3.6
    n = N(d)
    m.add(gust(d, r, 120, 900, .7, 1.0) * np.linspace(.3, 1, n) ** 1.2, 0, .8)
    m.add(bell(mt(43), 2.2, 1.2, r), .3, .6)
    m.add(bell(mt(43), 2.0, 1.1, r), 1.8, .45)
    for t0 in (.9, 1.7, 2.45):
        m.add(thump(62, 38, .3, .05, .1, 1.4), t0, .5)
        m.add(thump(55, 35, .3, .05, .1, 1.3), t0 + .18, .35)
    m.add(hp(noise(N(.4), r, 'pink'), 1500, 1) * bump(.4, .5, 1.5) * .12, 2.0, 1.0)
    m.add(gunshot(r, .35) * 0, 0, 0)
    m.add(tick(r, .01, 3000, .002), 2.35, .5)
    m.add(tick(r, .01, 2200, .002), 2.42, .5)
    m.add(ratchet(r, .8, 25, 110, 2600), 2.3, .5)
    m.add(chain(.8, r, 10, 1200, 3200, .04), 2.5, .35)
    m.add(drone(2.0, 41, r, 1.0, .01, 3, 500, .8, .8), 1.8, .9)
    m.add(whisper(2.0, r, 6, ('o', 'e'), 1.0, 700, 3), 1.5, .5)
    m.add(bossvox(P['cazador'], r, 1.4, 'roar'), 2.6, .8)
    return R(m.render(), 'cazador', 1.0)


# ------------------------------------------------------------------ muertes
def death_rey(r):
    m = Mix()
    m.add(voice(1.6, curve(1.6, [(0, 90), (.2, 80), (1.6, 32)]), r, 'o', 'a', scale=.8, dist=3, growl=.5, breath=.5, env=bump(1.6, .1, .9)), 0, .9)
    m.add(scatter(2.2, r, 90, 400, 2200, BONE, .03, 1.6), .2, 1.0)
    m.add(imp_rey(r, 1.0), .3, .8)
    m.add(imp_rey(r, .8), 1.1, .6)
    m.add(boom(.8, r, 48, .8, noise_f=800), .2, .7)
    m.add(chain(1.4, r, 14, 700, 2200, .05, 1.0), .4, .5)
    # corona rodando
    n = N(1.8)
    t = np.arange(n) / SR
    ring = modal(1250, BAR, 1.8, .6, r, .01)
    rate = 6 + 40 * (t / 1.8) ** 2
    ring *= .55 + .45 * np.abs(np.sin(2 * np.pi * np.cumsum(rate) / SR / 2))
    m.add(ring, 1.5, .5)
    m.add(tick(r, .01, 2500, .002), 3.2, .6)
    m.add(bell(mt(38), 2.4, 1.2, r), .5, .4)
    m.add(whisper(2.0, r, 5, ('o', 'e'), 1.0, 600, 2), 2.0, .45)
    return R(m.render(), 'rey_exanime', 1.0)


def death_coloso(r):
    m = Mix()
    m.add(crackle(2.3, curve(2.3, [(0, 100), (2.2, 3000)]), r, 3000, 1.2, 1000), 0, .8)
    for t0 in (.2, .6, 1.0, 1.4, 1.75):
        m.add(crack(r, .8, 400), t0, 1.0)
        m.add(modal(r.uniform(250, 500), PLATE, .5, .15, r), t0, .3)
    n = N(2.2)
    f = curve(2.2, [(0, 120), (2.2, 1100)], log=True)
    m.add(sat(saw(f, n) * .4 + sine(f, n) * .3, 2) * (np.arange(n) / n) ** 2 * .6, 0, .7)
    m.add(steam(r, 2.0, 1.2), .3, .8)
    m.add(boom(1.8, r, 36, 1.0, noise_f=3000), 2.2, 1.0)
    m.add(thump(70, 25, 1.4, .1, .5, 1.6), 2.2, .9)
    m.add(fireroar(1.6, r, 1000, 1.0), 2.2, .9)
    m.add(debris(2.2, r, 110, 250, 3500, .07), 2.3, .7)
    m.add(modal(110, PLATE, 2.4, 1.0, r), 2.2, .35)
    m.add(bubbles(1.5, r, 20, 60, 220) * np.linspace(1, .1, N(1.5)), 3.2, .6)
    m.add(hp(noise(N(1.4), r), 3000, 1) * expdec(1.4, .5) * .06, 3.3, 1.0)
    return R(m.render(), 'coloso_magma', 1.0)


def death_reina(r):
    m = Mix()
    d = 1.8
    m.add(voice(d, curve(d, [(0, 480), (.15, 560), (d, 170)]), r, 'a', 'u', scale=1.05, dist=1.4, vib=(5.5, .035), breath=.6, env=bump(d, .12, .9), jitter=.01), 0, 1.0)
    m.add(crackle(1.8, curve(1.8, [(0, 200), (1.5, 2500), (1.8, 600)]), r, 6000, 1.0, 2500), 0, .7)
    m.add(gust(2.0, r, 600, 3500, 1.0, 1.0), 0, .5)
    m.add(tick(r, .04, 3000, .01), 1.5, 1.0)
    m.add(shatter(2.0, r, 2500, 11000, 100, .06), 1.5, 1.0)
    m.add(boom(1.0, r, 55, .8, noise_f=1500), 1.5, .9)
    for k in range(14):
        m.add(modal(mt(r.integers(84, 102)), GLASS[:3], .6, .12, r), 1.9 + k * .14, .22)
    m.add(modal(mt(79), GLASS, 2.0, .8, r), 3.4, .35)
    m.add(modal(mt(72), BELL, 2.2, .9, r), 3.4, .25)
    return R(m.render(), 'reina_escarcha', 1.0)


def death_devorador(r):
    m = Mix()
    d = 1.8
    m.add(bossvox(P['devorador_vacio'], r, d, 'roar') * 1.0, 0, .9)
    m.add(reverse(boom(1.4, r, 45, 1.0, noise_f=3000)), .6, .8)
    n = N(3.0)
    t = np.arange(n) / SR
    f = curve(3.0, [(0, 500), (3.0, 28)], log=True)
    m.add(fm(f, 1.01, 2.5 * (1 - t / 3.0), n) * bump(3.0, .15, 1.0) * .6, 0, 1.0)
    m.add(tonecloud([mt(58), mt(55), mt(51)], 3.0, r, .5, .1, 2.5) * np.linspace(1, .2, n), 0, .6)
    m.add(reverse(whisper(2.8, r, 7, ('i', 'e'), 1.0, 900, 4)), 0, .7)
    m.add(boom(1.6, r, 34, 1.0, noise_f=700), 2.0, 1.0)
    m.add(reverse(whoosh(1.0, [(0, 300), (1.0, 8000)], r, 1.5, .9)), 1.2, .6)
    pop = sat(hp(noise(N(.06), r), 900, 2) * expdec(.06, .01, .0003), 4)
    m.add(pop, 3.0, .8)
    m.add(modal(mt(98), GLASS[:2], 1.8, .7, r), 3.05, .1)
    return R(m.render(), 'devorador_vacio', 1.0)


def death_ent(r):
    m = Mix()
    m.add(creak(2.6, r, 16, 40, (160, 650), 5, 1.8) * swell(2.6, .3, .6), 0, 1.0)
    m.add(voice(1.6, curve(1.6, [(0, 60), (.2, 70), (1.6, 28)]), r, 'u', 'o', scale=.6, dist=2.8, growl=.7, growl_f=24, breath=.6, env=bump(1.6, .15, .9)), 0, .8)
    for t0 in np.sort(r.uniform(.3, 2.4, 20)):
        m.add(crack(r, r.uniform(.4, 1.0), r.uniform(300, 900)), t0, 1.0)
    n = N(2.8)
    lv = hp(noise(n, r), 3000, 2) * np.abs(lp(noise(n, r), 20, 1))
    m.add(lv / (lv.std() + 1e-9) * .25 * bump(2.8, .5, 1.0), 1.0, 1.0)
    m.add(imp_ent(r, 1.2), 2.5, 1.0)
    m.add(boom(1.4, r, 38, 1.0, noise_f=900), 2.5, 1.0)
    m.add(debris(1.4, r, 70, 250, 3500, .06), 2.5, .7)
    m.add(creak(1.2, r, 25, 50, (250, 900), 6), 3.3, .35)
    m.add(whisper(1.4, r, 5, ('u', 'o'), 1.0, 500, 2), 3.2, .4)
    return R(m.render(), 'ent_ancestral', 1.0)


def death_titan(r):
    m = Mix()
    for t0 in (.1, .45, .7, 1.1, 1.3, 1.8):
        m.add(zap(.2, r, 4500, 500, 1.0), t0, .5)
        m.add(crack(r, .7, 800), t0, .6)
    m.add(voice(1.6, curve(1.6, [(0, 70), (.2, 80), (1.6, 28)]), r, 'a', 'o', scale=.6, dist=4, growl=.5, breath=.4, env=bump(1.6, .1, .9)), 0, .8)
    m.add(creak(2.6, r, 20, 40, (250, 900), 6, 2.0) * swell(2.6, .3, .6), .3, .7)
    m.add(rumble(3.5, r, 90, 3, .6, env=expdec(3.5, 1.5, .02)), 0, 1.5)
    m.add(sat(hp(noise(N(.4), r), 600, 2) * expdec(.4, .06, .0002), 6), 2.3, 1.0)
    m.add(imp_titan(r, 1.3), 2.5, 1.0)
    m.add(boom(1.6, r, 36, 1.0, noise_f=1000), 2.5, 1.0)
    m.add(chain(1.0, r, 14, 600, 2000, .06), 2.6, .5)
    m.add(debris(1.5, r, 60, 300, 3000, .06), 2.6, .5)
    n = N(1.5)
    f = curve(1.5, [(0, 400), (1.5, 30)], log=True)
    m.add(sat(saw(f, n) * .4, 2) * bump(1.5, .1, 1.5) * .5, 3.0, .6)
    m.add(steam(r, 1.4, 1.0), 3.0, .8)
    return R(m.render(), 'titan_tormenta', 1.0)


def death_matriarca(r):
    m = Mix()
    d = 1.5
    m.add(voice(d, curve(d, [(0, 900), (.1, 1100), (d, 220)]), r, 'a', 'e', scale=1.1, dist=3, vib=(8, .04), breath=.5, env=bump(d, .1, .9)), 0, 1.0)
    m.add(squelch(.8, r, 1000), .6, 1.0)
    m.add(imp_blood(r, 1.0), .9, .8)
    m.add(flapswarm(3.0, r, 70, 1.0) * np.concatenate([np.linspace(.2, 1, N(1.0)), np.linspace(1, 0, N(2.0))]), 1.0, .9)
    m.add(thump(100, 45, .4, .05, .14, 1.5), 1.6, .9)
    m.add(bubbles(1.4, r, 20, 120, 400), 1.8, .5)
    m.add(heartbeat(r), 3.0, .6)
    m.add(heartbeat(r) * .6, 3.9, .5)
    m.add(bell(mt(48), 2.0, 1.0, r), 1.0, .25)
    return R(m.render(), 'matriarca_sangre', 1.0)


def death_guardian(r):
    m = Mix()
    for i in range(10):
        m.add(bell(mt(r.choice([69, 74, 81, 86, 93])), 1.8, .6, r), .3 + i * .15, .35)
    m.add(choir([mt(50), mt(57), mt(62), mt(65)], 3.0, r, ('a', 'o'), .2, 1.4, nv=4), 0, 1.0)
    m.add(choir([mt(49), mt(56), mt(61)], 2.0, r, ('o', 'u'), 1.0, 1.0, nv=3), 1.6, .6)
    for t0 in (1.4, 1.7, 2.0, 2.15):
        m.add(thump(95, 40, .3, .04, .1, 1.5), t0, .7)
        m.add(modal(r.uniform(400, 900), PLATE, .8, .25, r), t0, .6)
        m.add(chain(.3, r, 5, 800, 2400, .04), t0, .3)
    m.add(boom(1.6, r, 45, 1.0, noise_f=900), 2.2, .9)
    m.add(modal(2600, BAR, 1.5, .5, r), 2.2, .2)
    m.add(riser(1.2, 500, 9000, r, 1.2, 0, 1.5), .2, .4)
    m.add(sparkle(3.0, r, 80, 3000, 12000, .1), .5, .35)
    m.add(thump(75, 30, 1.2, .1, .45, 1.5), 2.2, .8)
    return R(m.render(), 'guardian_eclipse', 1.0)


def death_cazador(r):
    m = Mix()
    d = 2.2
    m.add(bossvox(P['cazador'], r, d, 'roar'), 0, 1.0)
    n = N(3.4)
    t = np.arange(n) / SR
    cloud = tonecloud([mt(52), mt(45), mt(40)], 3.4, r, .5, .1, 2.8) * np.linspace(1, .1, n)
    m.add(cloud, .3, .7)
    f = curve(3.4, [(0, 400), (3.4, 25)], log=True)
    m.add(fm(f, 1.01, 2.0 * (1 - t / 3.4), n) * bump(3.4, .15, 1.0) * .5, .3, 1.0)
    for i, t0 in enumerate((.6, 1.7, 3.1)):
        m.add(bell(mt(43), 2.4, 1.3, r), t0, .5 - .1 * i)
    m.add(squelch(1.0, r, 800), .8, .8)
    m.add(flesh_hit(r, 90), 1.0, .8)
    m.add(boom(1.8, r, 34, 1.0, noise_f=900), 2.0, 1.0)
    m.add(reverse(whoosh(1.4, [(0, 300), (1.4, 6000)], r, 1.3, .9)), .8, .5)
    m.add(whisper(2.0, r, 6, ('o', 'e'), 1.0, 700, 3), 2.4, .5)
    for k, t0 in enumerate((3.4, 3.95, 4.55)):
        m.add(thump(60, 36, .4, .06, .14, 1.4), t0, .6 - .15 * k)
    return R(m.render(), 'cazador', 1.0)


CUSTOM = dict(
    rey_exanime=(intro_rey, death_rey), coloso_magma=(intro_coloso, death_coloso), reina_escarcha=(intro_reina, death_reina),
    devorador_vacio=(intro_devorador, death_devorador), ent_ancestral=(intro_ent, death_ent), titan_tormenta=(intro_titan, death_titan),
    matriarca_sangre=(intro_matriarca, death_matriarca), guardian_eclipse=(intro_guardian, death_guardian), cazador=(intro_cazador, death_cazador))


# ------------------------------------------------------------------ registro
def _roar(b, r):
    mat, imp = MATS[b]
    p = P[b]
    d = 1.7
    m = Mix()
    m.add(bossvox(p, r, d, 'roar'), 0, 1.0)
    m.add(mat(r, d), 0, .55)
    m.add(imp(r, .5), 0, .5)
    m.add(boom(.5, r, 55, .4, noise_f=1200), .0, .4)
    return R(m.render(), b, .9)


def _hurt(b, r):
    mat, imp = MATS[b]
    m = Mix()
    m.add(bossvox(P[b], r, .45, 'hurt'), 0, .9)
    m.add(imp(r, .6), 0, .8)
    return R(m.render(), b, .5)


def _phase(b, r):
    mat, imp = MATS[b]
    p = P[b]
    d = 2.4
    m = Mix()
    m.add(bossvox(p, r, d, 'phase'), 0, 1.0)
    m.add(mat(r, d), 0, .8)
    m.add(riser(1.3, 100, 3000, r, 1.0, .4, 2.0), 0, .4)
    m.add(imp(r, 1.3), 1.2, 1.0)
    m.add(boom(1.4, r, 40, 1.0, noise_f=1800), 1.2, 1.0)
    m.add(thump(65, 28, 1.0, .1, .4, 1.5), 1.2, .8)
    m.add(debris(1.0, r, 40, 300, 3500, .05), 1.25, .4)
    return R(m.render(), b, 1.0)


for _b in B:
    add(f'bs_{_b}_intro', (lambda b: lambda r: CUSTOM[b][0](r))(_b), -1)
    add(f'bs_{_b}_roar', (lambda b: lambda r: _roar(b, r))(_b), -1)
    for _k in (1, 2, 3):
        add(f'bs_{_b}_atk{_k}', (lambda b, k: lambda r: atk(b, r, k))(_b, _k), [-3, -2.5, -1.5][_k - 1])
    add(f'bs_{_b}_cast', (lambda b: lambda r: cast(b, r))(_b), -3)
    add(f'bs_{_b}_hurt', (lambda b: lambda r: _hurt(b, r))(_b), -4)
    add(f'bs_{_b}_phase', (lambda b: lambda r: _phase(b, r))(_b), -1)
    add(f'bs_{_b}_death', (lambda b: lambda r: CUSTOM[b][1](r))(_b), -1)
    add(f'bs_{_b}_step', (lambda b: lambda r: step(b, r))(_b), -6)


# ------------------------------------------------------------------ genericos
@sfx('boss_title', -1)
def _(r):
    m = Mix()
    m.add(reverse(whoosh(.8, [(0, 200), (.8, 4000)], r, 1.2, .8)), 0, .5)
    m.add(boom(2.0, r, 36, 1.0, noise_f=1500), .75, 1.0)
    m.add(thump(70, 26, 1.5, .12, .6, 1.6), .75, .9)
    m.add(sat(hp(noise(N(.25), r), 500, 2) * expdec(.25, .05, .0003), 5), .75, .6)
    m.add(modal(mt(31), BELL, 3.0, 1.4, r), .75, .5)
    m.add(modal(mt(43), PLATE, 2.5, 1.0, r), .75, .25)
    m.add(drone(2.5, 41, r, 1.0, .01, 3, 500, .1, 1.5), .75, .6)
    m.add(choir([mt(43), mt(50)], 2.0, r, ('o', 'u'), .1, 1.2, nv=4, g=.8), .8, .5)
    return reverb(m.render(), 2.2, .3, 3500, seed=110)


@sfx('boss_bar', -4)
def _(r):
    m = Mix()
    d = 1.2
    sc = whoosh(d, [(0, 150), (d, 700)], r, 2.0, .5, 1.0, 'pink') * (.55 + .45 * np.sin(2 * np.pi * 18 * np.arange(N(d)) / SR))
    m.add(sc, 0, .6)
    for i in range(10):
        m.add(modal(900 + i * 90, BAR, .15, .03, r), i * .09, .3 + i * .04)
    m.add(thump(90, 40, .5, .05, .2, 1.5), .9, 1.0)
    m.add(modal(500, PLATE, .8, .25, r), .9, .5)
    m.add(tick(r, .02, 1500, .004), .9, .6)
    return reverb(m.render(), .8, .2, 4000, seed=111)


@sfx('boss_defeat', -2)
def _(r):
    m = Mix()
    d = 4.0
    m.add(thump(80, 36, .6, .06, .25, 1.5), 0, 1.0)
    m.add(thump(90, 40, .6, .06, .25, 1.5), .5, .8)
    m.add(boom(1.4, r, 45, .8, noise_f=1500), 0, .8)
    m.add(choir([mt(45), mt(52), mt(57), mt(64)], 3.2, r, ('o', 'a'), .5, 1.2, nv=4), .0, .9)
    m.add(choir([mt(50), mt(57), mt(62), mt(69), mt(74)], 2.6, r, ('a', 'a'), .3, 1.2, nv=4), 1.0, 1.0)
    for i, nn in enumerate([62, 69, 74, 78, 81, 86, 90]):
        m.add(bell(mt(nn + 12), 2.0, .8, r), .9 + i * .14, .5 - i * .03)
    m.add(modal(mt(38), BELL, 3.0, 1.4, r), 1.0, .5)
    m.add(riser(.9, 500, 9000, r, 1.2, .3, 1.5), .1, .4)
    m.add(sparkle(2.5, r, 70, 3000, 12000, .12), 1.0, .4)
    return reverb(m.render(), 2.0, .3, 6000, seed=112)
