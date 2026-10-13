from recipes import *
from reg import sfx, add


@sfx('en_alert', -5)
def _(r):
    m = Mix()
    d = .55
    f = curve(d, [(0, 90), (.25, 170), (d, 120)])
    m.add(voice(d, f, r, 'a', 'e', scale=.9, dist=3, growl=.6, growl_f=55, breath=.5, jitter=.03, env=bump(d, .3, 1.0)), 0, 1.0)
    m.add(whoosh(.4, [(0, 2500), (.4, 4500)], r, 1.0, .4, 1.0), .05, .35)
    m.add(modal(mt(70), BAR, .5, .12, r), .02, .12)
    m.add(thump(120, 60, .2, .03, .07), 0, .5)
    return reverb(m.render(), .4, .1, 4500, seed=90)


@sfx('en_hurt_1', -5)
def _(r):
    m = Mix()
    m.add(voice(.26, curve(.26, [(0, 190), (.07, 210), (.26, 120)]), r, 'o', 'a', scale=.85, dist=2.5, growl=.4, breath=.4, env=bump(.26, .12, 1.0)), 0, 1.0)
    m.add(flesh_hit(r, 130), 0, .6)
    return m.render()


@sfx('en_hurt_2', -5)
def _(r):
    m = Mix()
    m.add(voice(.22, curve(.22, [(0, 300), (.05, 340), (.22, 190)]), r, 'e', 'i', scale=1.0, dist=3, growl=.3, breath=.5, env=bump(.22, .12, 1.0)), 0, 1.0)
    m.add(modal(850, BONE, .15, .03, r, .02), 0, .6)
    m.add(tick(r, .015, 2000, .004), 0, .6)
    return m.render()


@sfx('en_die_bone', -3)
def _(r):
    m = Mix()
    t0 = 0.0
    gap = .06
    for k in range(18):
        m.add(modal(r.uniform(500, 1800), BONE, .15, .03, r, .03), t0, r.uniform(.4, 1.0) * (1 - k * .03))
        m.add(tick(r, .012, 2500, .003), t0, .25)
        t0 += gap * r.uniform(.6, 1.5)
        gap *= 1.08
    m.add(thump(150, 60, .25, .03, .09, 1.3), 0, .8)
    m.add(thump(120, 55, .2, .03, .07), .35, .5)
    m.add(modal(700, BONE, .5, .12, r, .03), .55, .4)
    m.add(debris(.6, r, 14, 1000, 4500, .02, False), .15, .3)
    return reverb(m.render(), .5, .1, 5000, seed=91)


@sfx('en_die_flesh', -3)
def _(r):
    m = Mix()
    m.add(voice(.7, curve(.7, [(0, 160), (.08, 180), (.7, 60)]), r, 'a', 'o', scale=.85, dist=2.5, growl=.5, growl_f=40, breath=.5, env=bump(.7, .1, 1.0)), 0, .9)
    m.add(flesh_hit(r, 100), .15, 1.0)
    m.add(squelch(.4, r, 700), .2, .8)
    m.add(thump(90, 40, .4, .05, .15, 1.4), .3, 1.0)
    m.add(bubbles(.4, r, 7, 120, 300), .4, .4)
    return reverb(m.render(), .4, .08, 3500, seed=92)


@sfx('en_die_ghost', -4)
def _(r):
    d = 1.3
    m = Mix()
    f = curve(d, [(0, 420), (.2, 520), (d, 160)])
    m.add(voice(d, f, r, 'o', 'u', scale=1.0, dist=1.2, vib=(5.5, .03), breath=.6, env=bump(d, .15, 1.0), jitter=.01), 0, 1.0)
    m.add(whisper(d, r, 7, ('o', 'e'), 1.0, 900, 2), 0, .5)
    m.add(sparkle(1.0, r, 14, 2500, 7000, .1), .1, .2)
    m.add(reverse(whoosh(.4, [(0, 300), (.4, 3000)], r, 1.0, .5)), 0, .2)
    return reverb(m.render(), 1.4, .45, 4500, seed=93)


@sfx('en_die_slime', -4)
def _(r):
    m = Mix()
    m.add(squelch(.4, r, 800), 0, 1.0)
    m.add(bubbles(.5, r, 14, 150, 600), 0, .8)
    d = .3
    n = N(d)
    f = curve(d, [(0, 150), (d, 700)], log=True)
    m.add(sine(f, n) * expdec(d, .06, .001), .35, .8)
    m.add(tick(r, .01, 1500, .003), .35, .4)
    m.add(thump(100, 50, .2, .03, .06), 0, .5)
    return m.render()


@sfx('en_die_magic', -3)
def _(r):
    m = Mix()
    d = .9
    n = N(d)
    t = np.arange(n) / SR
    f = curve(d, [(0, 1200), (d, 150)], log=True)
    m.add(fm(f, 1.5, 3 * np.exp(-t / .3), n) * expdec(d, .25, .002), 0, .6)
    m.add(sparkle(.7, r, 30, 2500, 10000, .08, 1.0), 0, .5)
    m.add(reverse(whoosh(.3, [(0, 500), (.3, 6000)], r, 1.0, .5)), .0, .5)
    m.add(boom(.4, r, 90, .6, noise_f=2500), .3, .8)
    m.add(modal(mt(79), GLASS, .6, .2, r), .3, .3)
    return reverb(m.render(), .8, .2, 6000, seed=94)


@sfx('en_attack_melee', -5)
def _(r):
    m = Mix()
    m.add(whoosh(.2, [(0, 400), (.2, 2200)], r, 1.0, .55, 1.3, 'pink'), 0, 1.0)
    m.add(voice(.2, curve(.2, [(0, 150), (.2, 110)]), r, 'a', 'o', scale=.9, dist=2.5, breath=.5, env=bump(.2, .3, 1.0)), 0, .45)
    m.add(thump(110, 50, .12, .02, .05), .14, .4)
    return m.render()


@sfx('en_cast', -5)
def _(r):
    m = Mix()
    d = .65
    n = N(d)
    m.add(whisper(d, r, 8, ('o', 'e'), 1.0, 900, 2), 0, .7)
    f = curve(d, [(0, 250), (d, 700)], log=True)
    m.add(fm(f, 2.0, 1.5, n) * bump(d, .8, 1.2) * .3, 0, 1.0)
    m.add(riser(d, 600, 5000, r, 2.0, 0, 1.5), 0, .35)
    m.add(modal(mt(81), GLASS, .5, .12, r), d - .1, .3)
    return reverb(m.render(), .6, .15, 5500, seed=95)


@sfx('en_flap', -9)
def _(r):
    m = Mix()
    for i, t0 in enumerate((0, .13)):
        d = .12
        m.add(sweep(noise(N(d), r, 'pink'), curve(d, [(0, 500), (d * .5, 1800), (d, 600)], log=True), 'bp', 1.0) * bump(d, .4, 1.5), t0, 1.0 - i * .2)
        m.add(thump(130, 80, .06, .01, .02), t0 + .01, .3)
    return m.render()


@sfx('en_dash', -6)
def _(r):
    m = Mix()
    m.add(whoosh(.28, [(0, 500), (.1, 3000), (.28, 900)], r, 1.2, .3, 1.3), 0, 1.0)
    m.add(thump(140, 60, .15, .02, .05, 1.3), 0, .5)
    m.add(hp(noise(N(.15), r), 4000, 1) * expdec(.15, .04), .02, .12)
    return m.render()


@sfx('en_step_heavy', -8)
def _(r):
    m = Mix()
    m.add(thump(75, 35, .35, .05, .12, 1.5), 0, 1.0)
    m.add(lp(noise(N(.25), r), 700, 2) * expdec(.25, .05, .0008), 0, .6)
    m.add(chain(.3, r, 5, 1000, 2800, .04), .02, .25)
    m.add(debris(.2, r, 6, 500, 2500, .03), .03, .2)
    return m.render()


@sfx('arrow_shot', -5)
def _(r):
    m = Mix()
    m.add(ks(150, .35, r, .985, .5), 0, .5)
    m.add(thump(160, 90, .1, .015, .04), 0, .4)
    m.add(tick(r, .012, 2500, .003), 0, .5)
    m.add(whoosh(.25, [(0, 5000), (.25, 2200)], r, 2.0, .2, 1.2), .01, .6)
    return m.render()


@sfx('spit', -6)
def _(r):
    m = Mix()
    m.add(hp(noise(N(.15), r), 2500, 1) * expdec(.15, .04, .002), 0, .5)
    m.add(squelch(.2, r, 1200), .06, 1.0)
    m.add(bubbles(.15, r, 3, 400, 900), .1, .5)
    m.add(whoosh(.2, [(0, 1500), (.2, 700)], r, 1.2, .3), 0, .3)
    return m.render()


@sfx('magic_bolt', -5)
def _(r):
    m = Mix()
    d = .4
    n = N(d)
    t = np.arange(n) / SR
    f = curve(d, [(0, 600), (d, 1800)], log=True)
    m.add(fm(f, 1.5, 2.0, n) * bump(d, .3, 1.0) * .5, 0, 1.0)
    m.add(whoosh(d, [(0, 1200), (d, 4000)], r, 1.5, .3, 1.3), 0, .5)
    m.add(sparkle(.3, r, 8, 3000, 9000, .04), 0, .3)
    m.add(thump(180, 80, .12, .02, .05), 0, .4)
    return reverb(m.render(), .4, .1, 6000, seed=96)


@sfx('explosion_small', -2)
def _(r):
    m = Mix()
    m.add(boom(.7, r, 70, 1.0, noise_f=3000), 0, 1.0)
    m.add(crackle(.6, curve(.6, [(0, 2000), (.6, 300)]), r, 3000, 1.1, 1200) * expdec(.6, .2, .002), 0, .5)
    m.add(debris(.5, r, 18, 400, 3000, .05), .03, .5)
    return reverb(m.render(), .5, .12, 4500, seed=97)


@sfx('explosion_big', -1)
def _(r):
    m = Mix()
    m.add(boom(1.6, r, 42, 1.0, noise_f=2500), 0, 1.0)
    m.add(thump(70, 26, 1.2, .1, .45, 1.6), 0, .9)
    m.add(sweep(noise(N(1.4), r), curve(1.4, [(0, 8000), (1.4, 200)], log=True), 'lp') * expdec(1.4, .4, .001), 0, .8)
    m.add(rumble(1.8, r, 90, 5, .5, env=expdec(1.8, .7, .01)), .05, 1.5)
    m.add(debris(1.2, r, 60, 300, 3500, .06), .1, .6)
    m.add(crackle(1.2, curve(1.2, [(0, 1500), (1.2, 200)]), r, 3000, 1.1, 1200) * expdec(1.2, .5), .1, .4)
    return reverb(m.render(), 1.3, .22, 3500, seed=98)


@sfx('proj_hit', -5)
def _(r):
    m = Mix()
    m.add(thump(200, 80, .12, .02, .04, 1.3), 0, .8)
    m.add(tick(r, .02, 2500, .004), 0, .7)
    m.add(hp(noise(N(.12), r), 3000, 1) * expdec(.12, .03, .001), .0, .3)
    m.add(modal(1400, BAR, .2, .04, r), 0, .25)
    return m.render()
