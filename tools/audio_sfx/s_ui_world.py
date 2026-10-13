from recipes import *
from reg import sfx, add

# =============================================================== INTERFAZ
@sfx('ui_click', -9)
def _(r):
    m = Mix()
    m.add(tick(r, .02, 2500, .003), 0, .8)
    m.add(modal(1900, BAR, .1, .02, r), 0, .6)
    m.add(thump(420, 190, .08, .02, .03), 0, .7)
    return m.render()


@sfx('ui_hover', -15)
def _(r):
    m = Mix()
    m.add(tick(r, .015, 4000, .002), 0, .4)
    m.add(modal(2600, GLASS[:3], .09, .02, r), 0, .6)
    return m.render()


@sfx('ui_confirm', -7)
def _(r):
    m = Mix()
    m.add(thump(220, 110, .2, .03, .08), 0, .6)
    m.add(modal(mt(76), GLASS, .5, .13, r), 0, 1)
    m.add(modal(mt(83), GLASS, .6, .17, r), .09, .9)
    m.add(tick(r, .02, 3000, .003), 0, .4)
    return reverb(m.render(), .6, .12, 6000, seed=2)


@sfx('ui_back', -9)
def _(r):
    m = Mix()
    m.add(thump(200, 90, .22, .03, .08), 0, .7)
    m.add(modal(mt(69), GLASS[:3], .35, .09, r), 0, .8)
    m.add(modal(mt(62), GLASS[:3], .4, .11, r), .07, .8)
    return m.render()


@sfx('ui_error', -8)
def _(r):
    m = Mix()
    for t0 in (0, .13):
        n = N(.11)
        y = saw(130, n) + saw(137, n) + .6 * square(65, n)
        y = lp(y, 900, 2) * swell(.11, .005, .03, n)
        m.add(sat(y, 2.5), t0, .6)
    m.add(thump(110, 70, .3, .05, .1), 0, .6)
    return m.render()


@sfx('ui_open', -9)
def _(r):
    m = Mix()
    m.add(whoosh(.28, [(0, 250), (.28, 1800)], r, 1.0, .65), 0, .6)
    m.add(modal(mt(57), BELL, .8, .25, r), .12, .35)
    m.add(thump(160, 80, .18, .04, .06), .22, .5)
    return reverb(m.render(), .7, .15, 4000, seed=3)


@sfx('ui_pick_upgrade', -4)
def _(r):
    notes = [67, 72, 76, 79, 84]
    m = Mix()
    for i, nn in enumerate(notes):
        m.add(modal(mt(nn), GLASS, .9, .22, r), i * .075, .8)
    m.add(sparkle(1.0, r, 25, 3000, 9000, .07, 1.0), .15, .35)
    m.add(thump(130, 60, .3, .05, .12), 0, .6)
    m.add(choir([mt(55), mt(62)], .9, r, ('o', 'a'), .2, .5, g=.5), .0, .5)
    return reverb(m.render(), 1.2, .25, 6000, seed=4)


@sfx('ui_unlock', -3)
def _(r):
    m = Mix()
    m.add(chain(.3, r, 5, 1200, 3000), 0, .5)
    m.add(thump(100, 45, .6, .08, .25, 1.4), .25, 1.0)
    m.add(choir([mt(57), mt(64), mt(69)], 1.6, r, ('o', 'a'), .5, .6, g=1.0), .25, .8)
    m.add(bell(mt(81), 1.5, .5, r), .3, .6)
    m.add(bell(mt(76), 1.5, .5, r), .55, .5)
    m.add(sparkle(1.4, r, 40, 3000, 10000, .09), .4, .35)
    return reverb(m.render(), 1.8, .3, 5500, seed=5)


@sfx('ui_start_run', -2)
def _(r):
    m = Mix()
    m.add(reverse(whoosh(.7, [(0, 200), (.7, 3000)], r, 1.2, .5)), 0, .5)
    m.add(boom(1.1, r, 48, 1.0), .6, 1.0)
    m.add(bell(mt(40), 1.5, .8, r), .6, .6)
    m.add(chain(.5, r, 8, 1200, 2800), .62, .35)
    m.add(rumble(1.0, r, 90, 3, .4), .6, .9)
    return reverb(m.render(), 1.5, .25, 3500, seed=6)


@sfx('ui_pause', -8)
def _(r):
    m = Mix()
    n = N(.3)
    f = curve(.3, [(0, 600), (.3, 150)], log=True)
    y = lp(saw(f, n) + .5 * sine(f * 2, n), 1200, 2) * expdec(.3, .1, .004)
    m.add(y, 0, .5)
    m.add(thump(150, 70, .25, .04, .08), 0, .7)
    m.add(whoosh(.25, [(0, 2500), (.25, 300)], r, 1.0, .2), 0, .3)
    return m.render()


# =============================================================== MUNDO
@sfx('coin', -6)
def _(r):
    m = Mix()
    m.add(modal(1318, BAR[:3], .35, .09, r, 0.0, .4), 0, .8)
    m.add(modal(1760, BAR[:3], .45, .13, r, 0.0, .4), .055, 1.0)
    m.add(tick(r, .01, 4000, .002), 0, .5)
    m.add(modal(5280, GLASS[:2], .2, .03, r), .055, .25)
    return m.render()


@sfx('soul', -6)
def _(r):
    n = N(.55)
    t = np.arange(n) / SR
    f = curve(.55, [(0, 500), (.2, 900), (.55, 1700)], log=True)
    y = fm(f, 2.0, 1.5 * np.exp(-t / .2) + .3, n) * bump(.55, .35, 1.2)
    y += .3 * sine(f * 2.01, n) * bump(.55, .5, 1.5)
    y += .25 * hp(noise(n, r), 5000, 2) * bump(.55, .3, 2)
    return reverb(y, .8, .25, 7000, seed=7)


@sfx('heart', -6)
def _(r):
    m = Mix()
    m.add(modal(mt(67), GLASS[:3], .5, .2, r), 0, .6)
    m.add(modal(mt(74), GLASS[:3], .6, .25, r), .09, .7)
    m.add(thump(120, 55, .2, .04, .09, 1.2), 0, .8)
    m.add(thump(110, 52, .2, .04, .09, 1.2), .15, .6)
    m.add(choir([mt(55)], .5, r, ('o', 'o'), .1, .3, g=.5), 0, .35)
    return reverb(m.render(), .7, .15, 5000, seed=8)


@sfx('potion', -6)
def _(r):
    m = Mix()
    m.add(modal(2400, GLASS, .3, .06, r), 0, .7)
    m.add(tick(r, .01, 3000, .002), 0, .5)
    m.add(bubbles(.5, r, 6, 250, 600), .08, .8)
    m.add(modal(mt(79), GLASS[:3], .5, .18, r), .35, .5)
    m.add(sweep(noise(N(.4), r), curve(.4, [(0, 1500), (.4, 700)], log=True), 'bp', 2) * bump(.4, .3), .1, .15)
    return reverb(m.render(), .5, .1, 6000, seed=9)


@sfx('door_open', -3)
def _(r):
    m = Mix()
    d = 1.6
    m.add(rumble(d, r, 130, 9, .7, env=bump(d, .45, 1.0)), 0, 1.4)
    m.add(whoosh(d, [(0, 180), (d * .5, 520), (d, 260)], r, 3, .5, 1.0), 0, 1.0)
    m.add(creak(.9, r, 30, 55, (300, 800), 6), .05, .5)
    m.add(debris(.6, r, 14, 300, 1500, .05, False, False), .4, .4)
    m.add(boom(.5, r, 70, .8, noise_f=600), 1.4, .8)
    return reverb(m.render(), 1.0, .15, 3000, seed=10)


@sfx('door_locked', -5)
def _(r):
    m = Mix()
    for i, t0 in enumerate((0, .09, .2)):
        m.add(modal(r.uniform(1400, 2200), BAR, .12, .03, r), t0, .7 - i * .1)
        m.add(thump(260, 130, .1, .02, .035), t0, .8)
        m.add(tick(r, .012, 2000, .003), t0, .6)
    m.add(chain(.3, r, 5, 900, 2200), .15, .4)
    m.add(thump(110, 60, .25, .04, .09, 1.3), .22, 1.0)
    return m.render()


@sfx('portal_enter', -3)
def _(r):
    m = Mix()
    d = 1.3
    m.add(reverse(whoosh(.6, [(0, 400), (.6, 6000)], r, 2.0, .5)), 0, .8)
    n = N(d)
    f = curve(d, [(0, 200), (.55, 900), (d, 120)], log=True)
    s = fm(f, 1.5, curve(d, [(0, 0), (.6, 3), (d, 0)]), n) * bump(d, .45, 1.2)
    m.add(s, 0, .6)
    m.add(boom(.9, r, 55, 1.0), .55, .8)
    m.add(sparkle(.9, r, 30, 2500, 9000, .08), .1, .35)
    m.add(whoosh(.7, [(0, 5000), (.7, 300)], r, 1.2, .1, 1.5), .55, .6)
    return reverb(m.render(), 1.2, .25, 5000, seed=11)


@sfx('chest_open', -4)
def _(r):
    m = Mix()
    m.add(creak(.5, r, 35, 60, (500, 1400), 8), 0, .6)
    m.add(thump(200, 90, .15, .03, .05), .46, .9)
    m.add(tick(r, .02, 2500, .004), .45, .6)
    m.add(modal(mt(79), GLASS, .9, .3, r), .5, .7)
    m.add(modal(mt(84), GLASS, .9, .3, r), .58, .6)
    m.add(sparkle(.8, r, 25, 3000, 9000, .08), .5, .4)
    return reverb(m.render(), .8, .2, 5500, seed=12)


@sfx('shop_buy', -5)
def _(r):
    m = Mix()
    for i in range(5):
        f = r.uniform(1300, 2300)
        m.add(modal(f, BAR[:3], .25, .06, r), i * .045, r.uniform(.4, .8))
        m.add(tick(r, .01, 3500, .002), i * .045, .3)
    m.add(bell(mt(88), .8, .3, r), .24, .45)
    m.add(thump(180, 90, .15, .03, .05), .22, .5)
    return reverb(m.render(), .5, .1, 6000, seed=13)


@sfx('forge_anvil', -2)
def _(r):
    m = Mix()
    m.add(thump(260, 85, .25, .02, .07, 1.5), 0, 1.0)
    m.add(tick(r, .02, 1800, .004), 0, .9)
    m.add(modal(1180, PLATE, 1.0, .35, r, .004, .4), 0, 1.0)
    m.add(modal(2350, BAR, .6, .15, r, .005), 0, .5)
    m.add(sparkle(.3, r, 14, 5000, 12000, .02, 2.0), .005, .3)
    return reverb(m.render(), .7, .12, 6000, seed=14)


@sfx('altar_bless', -4)
def _(r):
    m = Mix()
    d = 1.8
    m.add(choir([mt(57), mt(64), mt(69), mt(76)], d, r, ('o', 'a'), .55, .7), 0, 1.0)
    m.add(bell(mt(81), 1.6, .6, r), .55, .5)
    m.add(bell(mt(88), 1.4, .45, r), .8, .3)
    m.add(sparkle(1.4, r, 40, 3500, 11000, .1), .3, .35)
    m.add(reverse(whoosh(.55, [(0, 500), (.55, 5000)], r, 1.5, .5)), 0, .3)
    return reverb(m.render(), 1.8, .3, 6000, seed=15)


@sfx('fountain_heal', -5)
def _(r):
    m = Mix()
    d = 1.3
    n = N(d)
    w = hp(noise(n, r), 2500, 1) * (.4 + .6 * np.abs(lp(noise(n, r), 40, 1)) * 4) * bump(d, .5, 1)
    m.add(w, 0, .13)
    m.add(bubbles(d, r, 22, 400, 1500), 0, .45)
    for i, nn in enumerate([72, 76, 79, 84]):
        m.add(modal(mt(nn), GLASS, .8, .25, r), .2 + i * .1, .55)
    m.add(choir([mt(60), mt(67)], .9, r, ('u', 'o'), .3, .4, g=.5), .15, .5)
    return reverb(m.render(), 1.0, .25, 6000, seed=16)


@sfx('spikes', -3)
def _(r):
    m = Mix()
    m.add(tick(r, .03, 3000, .006), 0, 1.0)
    m.add(whoosh(.07, [(0, 2000), (.07, 7000)], r, 1.5, .5), 0, .8)
    m.add(modal(2800, BAR, .15, .03, r), .005, .6)
    m.add(flesh_hit(r, 150), .02, .6)
    return m.render()


@sfx('break_pot', -3)
def _(r):
    m = Mix()
    m.add(thump(240, 110, .12, .02, .04), 0, .7)
    m.add(tick(r, .03, 1500, .008), 0, .9)
    m.add(shatter(.6, r, 1800, 6500, 45, .04, BONE + [(5, .1)]), 0, .8)
    m.add(debris(.5, r, 25, 600, 3500, .05), .02, .6)
    return m.render()


@sfx('room_clear', -3)
def _(r):
    m = Mix()
    d = 1.5
    for i, nn in enumerate([64, 68, 71, 76]):
        m.add(bell(mt(nn + 12), 1.2, .5, r), i * .11, .6)
    m.add(choir([mt(52), mt(59), mt(64)], d, r, ('o', 'a'), .25, .6), .0, .8)
    m.add(thump(100, 45, .5, .06, .2, 1.3), 0, .8)
    m.add(sparkle(1.2, r, 30, 3000, 10000, .1), .25, .3)
    return reverb(m.render(), 1.5, .25, 5500, seed=17)


@sfx('room_lock', -2)
def _(r):
    m = Mix()
    m.add(boom(.9, r, 50, 1.0, noise_f=900), 0, 1.0)
    m.add(modal(520, PLATE, 1.0, .3, r), 0, .8)
    m.add(chain(.7, r, 12, 900, 2600), .02, .6)
    m.add(thump(90, 40, .5, .08, .2, 1.5), .0, 1.0)
    m.add(debris(.5, r, 15, 300, 1800, .06), .05, .4)
    return reverb(m.render(), 1.0, .2, 3500, seed=18)


@sfx('secret', -5)
def _(r):
    m = Mix()
    d = 1.3
    m.add(whisper(d, r, 5, ('i', 'e'), 1.0, 1500, 2), 0, .6)
    for i, nn in enumerate([70, 76, 82, 77]):
        m.add(modal(mt(nn), GLASS, 1.0, .35, r), .1 + i * .13, .55)
    m.add(sparkle(1.0, r, 18, 4000, 11000, .1), .1, .3)
    m.add(thump(90, 50, .5, .06, .15), .0, .4)
    return reverb(m.render(), 1.5, .3, 6500, seed=19)


@sfx('relic_get', -2)
def _(r):
    m = Mix()
    d = 3.2
    m.add(thump(80, 36, 1.2, .1, .45, 1.5), 0, 1.0)
    m.add(boom(1.0, r, 48, .9), .0, .8)
    m.add(choir([mt(52), mt(59), mt(64), mt(71), mt(76)], d, r, ('o', 'a'), .6, 1.2, nv=4), .1, 1.0)
    for i, nn in enumerate([76, 83, 88, 95]):
        m.add(bell(mt(nn), 2.2, .8, r), .5 + i * .22, .5 - i * .06)
    m.add(sparkle(2.2, r, 70, 3000, 12000, .12), .3, .35)
    m.add(reverse(whoosh(.8, [(0, 300), (.8, 7000)], r, 1.5, .5)), 0, .4)
    return reverb(m.render(), 2.4, .3, 6000, seed=20)
