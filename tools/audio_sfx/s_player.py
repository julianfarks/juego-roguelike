from recipes import *
from reg import sfx, add

# =============================================================== JUGADOR
def _step(r, f, lpf, hard):
    m = Mix()
    m.add(thump(f * 1.6, f * .7, .09, .02, .03, 1.2), 0, .8)
    m.add(lp(noise(N(.07), r), lpf, 2) * expdec(.07, .02, .0005), 0, .7)
    m.add(hp(noise(N(.03), r), 2500, 1) * expdec(.03, .006, .0003), .0, hard * .5)
    return m.render()


for i, (f, lpf, hard, lv) in enumerate([(120, 1400, .5, -16), (135, 1700, .7, -16), (108, 1200, .4, -17)], 1):
    add(f'step_{i}', (lambda f=f, lpf=lpf, hard=hard: lambda r: _step(r, f, lpf, hard))(), lv)


@sfx('jump', -9)
def _(r):
    m = Mix()
    m.add(whoosh(.2, [(0, 500), (.2, 2600)], r, 1.0, .6), 0, .6)
    m.add(thump(170, 90, .08, .02, .03), 0, .6)
    m.add(tick(r, .01, 1500, .003), 0, .3)
    return m.render()


@sfx('double_jump', -7)
def _(r):
    m = Mix()
    m.add(whoosh(.3, [(0, 900), (.3, 5500)], r, 1.4, .5), 0, .6)
    m.add(modal(mt(88), GLASS, .4, .1, r), .02, .45)
    m.add(modal(mt(95), GLASS[:3], .4, .12, r), .09, .35)
    m.add(sparkle(.3, r, 10, 4000, 10000, .04), 0, .25)
    return m.render()


@sfx('land', -9)
def _(r):
    m = Mix()
    m.add(thump(140, 55, .2, .03, .07, 1.4), 0, .9)
    m.add(lp(noise(N(.14), r), 1100, 2) * expdec(.14, .035, .0005), 0, .7)
    m.add(hp(noise(N(.08), r), 3000, 1) * expdec(.08, .015, .0004), 0, .25)
    return m.render()


@sfx('roll', -8)
def _(r):
    d = .42
    n = N(d)
    t = np.arange(n) / SR
    w = noise(n, r, 'pink')
    y = sweep(w, curve(d, [(0, 500), (.2, 1400), (d, 600)], log=True), 'bp', 1.0)
    y *= (0.5 + 0.5 * np.sin(2 * np.pi * 5.5 * t - 1.0) ** 2) * bump(d, .35, 1.0)
    m = Mix()
    m.add(y / (y.std() + 1e-9), 0, .3)
    m.add(thump(120, 60, .12, .02, .04), .0, .5)
    m.add(thump(140, 55, .15, .02, .05, 1.3), .33, .7)
    m.add(tick(r, .02, 2000, .006), .33, .3)
    return m.render()


def _hurt(r, f, v1, g):
    m = Mix()
    m.add(voice(.28, curve(.28, [(0, f * 1.15), (.08, f * 1.2), (.28, f * .8)]), r, 'a', v1, scale=.95, dist=2.0, breath=.35,
                vib=(6, .01), env=bump(.28, .15, 1.0)), .02, 1.0)
    m.add(flesh_hit(r, 130), 0, .7)
    return m.render() * g


add('hurt_1', lambda r: _hurt(r, 150, 'o', 1), -4)
add('hurt_2', lambda r: _hurt(r, 175, 'e', 1), -4)


@sfx('death', -2)
def _(r):
    m = Mix()
    d = 2.4
    m.add(flesh_hit(r, 120), 0, .8)
    m.add(voice(1.0, curve(1.0, [(0, 190), (.1, 200), (1.0, 70)]), r, 'a', 'o', scale=.95, dist=2.2, breath=.4, env=bump(1.0, .08, .8)), .02, 1.0)
    m.add(thump(90, 35, 1.0, .12, .4, 1.4), .25, .9)
    m.add(rumble(1.6, r, 90, 3, .5), .3, .8)
    m.add(chain(.5, r, 6, 1000, 2500, accel=.6), .5, .4)
    m.add(bell(mt(45), 2.0, 1.0, r), .35, .4)
    m.add(reverse(whoosh(.9, [(0, 4000), (.9, 200)], r, 1.0, .9)), 0, .3)
    return reverb(m.render(), 1.6, .3, 3500, seed=21)


@sfx('heal', -5)
def _(r):
    m = Mix()
    for i, nn in enumerate([64, 71, 76, 83]):
        m.add(modal(mt(nn), GLASS[:4], .9, .25, r), i * .08, .6)
    m.add(choir([mt(60), mt(67)], .9, r, ('u', 'o'), .2, .5, g=.6), 0, .5)
    m.add(sparkle(.8, r, 25, 3500, 10000, .08), .15, .3)
    return reverb(m.render(), 1.0, .2, 6000, seed=22)


@sfx('block', -2)
def _(r):
    m = Mix()
    m.add(thump(200, 80, .2, .02, .06, 1.5), 0, .9)
    m.add(tick(r, .02, 1500, .004), 0, .8)
    m.add(modal(690, PLATE, .6, .17, r, .004), 0, 1.0)
    m.add(modal(1500, BAR, .3, .06, r), 0, .4)
    return reverb(m.render(), .4, .08, 5000, seed=23)


@sfx('parry', -2)
def _(r):
    m = Mix()
    m.add(tick(r, .02, 2500, .003), 0, 1.0)
    m.add(modal(2300, BAR, .8, .25, r, .004, .45), 0, 1.0)
    m.add(modal(3600, GLASS, .5, .12, r), 0, .5)
    m.add(modal(900, PLATE, .5, .12, r), 0, .5)
    m.add(thump(240, 110, .1, .02, .04), 0, .6)
    m.add(sparkle(.4, r, 14, 5000, 12000, .04, 2.0), .01, .3)
    return reverb(m.render(), .5, .12, 7000, seed=24)


@sfx('heartbeat', -6)
def _(r):
    return reverb(heartbeat(r), .4, .08, 1500, seed=25)


@sfx('level_up', -3)
def _(r):
    m = Mix()
    for i, nn in enumerate([60, 64, 67, 72, 76]):
        m.add(bell(mt(nn + 12), 1.2, .4, r), i * .09, .55)
    m.add(choir([mt(48), mt(55), mt(60), mt(67)], 1.6, r, ('o', 'a'), .25, .7), .0, .8)
    m.add(thump(90, 45, .4, .05, .15, 1.3), 0, .8)
    m.add(sparkle(1.3, r, 35, 3000, 11000, .1), .2, .35)
    return reverb(m.render(), 1.6, .25, 6000, seed=26)


@sfx('ult_ready', -3)
def _(r):
    d = 1.1
    n = N(d)
    m = Mix()
    f = curve(d, [(0, 150), (d * .8, 600), (d, 600)], log=True)
    m.add(sat(saw(f, n) * .5 + sine(f * 2, n) * .4, 1.5) * bump(d, .7, 1.0) * .6, 0, .7)
    m.add(riser(d * .8, 800, 7000, r, 1.5, 0, 2.0), 0, .5)
    m.add(thump(120, 50, .4, .05, .18, 1.4), .8, .9)
    m.add(bell(mt(79), 1.2, .5, r), .8, .6)
    m.add(sparkle(.6, r, 25, 4000, 12000, .06), .85, .4)
    return reverb(m.render(), 1.0, .2, 6000, seed=27)


@sfx('skill_fail', -8)
def _(r):
    n = N(.3)
    f = curve(.3, [(0, 260), (.3, 80)], log=True)
    y = lp(saw(f, n) + saw(f * 1.04, n), 700, 2) * bump(.3, .15, 1.0)
    m = Mix()
    m.add(sat(y, 2) * .6, 0, 1)
    m.add(tick(r, .02, 800, .005), 0, .5)
    m.add(thump(120, 60, .15, .03, .05), 0, .5)
    return m.render()


@sfx('cd_ready', -12)
def _(r):
    m = Mix()
    m.add(modal(mt(88), GLASS[:3], .3, .07, r), 0, .6)
    m.add(modal(mt(95), GLASS[:2], .3, .07, r), .06, .5)
    m.add(tick(r, .01, 4000, .002), 0, .3)
    return m.render()


@sfx('ult_charge', -8)
def _(r):
    d = .7
    n = N(d)
    m = Mix()
    f = curve(d, [(0, 220), (d, 440)], log=True)
    m.add(sat(sine(f, n) + .4 * sine(f * 2, n), 1.4) * bump(d, .8, 1.2), 0, .5)
    m.add(riser(d, 600, 5000, r, 2.0, 0, 1.5), 0, .5)
    m.add(modal(mt(84), GLASS[:3], .3, .08, r), d - .05, .5)
    return m.render()


@sfx('time_stop', -2)
def _(r):
    m = Mix()
    d = 2.2
    n = N(d)
    m.add(boom(1.2, r, 40, 1.0, noise_f=800), 0, 1.0)
    f = curve(1.2, [(0, 900), (1.2, 40)], log=True)
    m.add(sat(saw(f, N(1.2)) + .5 * sine(f * .5, N(1.2)), 2) * bump(1.2, .08, 1.5), 0, .45)
    m.add(reverse(whoosh(.5, [(0, 300), (.5, 7000)], r, 1.5, .6)), 0, .5)
    for i in range(4):
        m.add(thump(900, 700, .05, .01, .02), .75 + i * .26, .35 - i * .05)
        m.add(tick(r, .01, 2500, .002), .75 + i * .26, .2)
    m.add(bell(mt(52), 2.0, 1.2, r), .1, .6)
    m.add(bell(mt(76), 1.8, .8, r), .12, .3)
    m.add(sweep(noise(N(1.6), r, 'pink'), curve(1.6, [(0, 5000), (1.6, 250)], log=True), 'lp') * bump(1.6, .1, 1.5), 0, .5)
    return reverb(m.render(), 2.0, .35, 3500, seed=28)


# =============================================================== ARMAS (swing)
def _swing_sword(r, i):
    d = [.24, .24, .32][i - 1]
    pts = [[(0, 1400), (d, 5200)], [(0, 5200), (d, 1500)], [(0, 1100), (d * .5, 3500), (d, 6000)]][i - 1]
    m = Mix()
    m.add(whoosh(d, pts, r, 2.0 + .3 * i, [.55, .45, .5][i - 1], 1.4), 0, 1.0)
    m.add(whoosh(d, [(0, 4000), (d, 9000)], r, 1.0, .6, 2.0), 0, .35)
    m.add(modal([3100, 3600, 2700][i - 1], BAR, .35, .09, r, .01), d * .5, .09 + .03 * i)
    if i == 3:
        m.add(whoosh(d, [(0, 300), (d, 900)], r, 1.0, .4, 1.5), 0, .5)
        m.add(thump(130, 70, .15, .03, .06), d * .4, .35)
    return m.render()


def _swing_great(r, i):
    d = [.5, .52, .72][i - 1]
    pts = [[(0, 250), (d * .5, 900), (d, 400)], [(0, 700), (d * .5, 280), (d, 150)], [(0, 180), (d * .55, 1100), (d, 220)]][i - 1]
    m = Mix()
    m.add(whoosh(d, pts, r, .9, .5, 1.3, 'pink'), 0, 1.0)
    m.add(lp(noise(N(d), r, 'brown'), 160, 2) * bump(d, .55, 1.5) * 2.0, 0, .8)
    m.add(whoosh(d, [(0, 1200), (d, 2800)], r, 1.0, .55, 2.0), 0, .15)
    m.add(thump(95, 45, .3, .06, .12, 1.3), d * .55, .3 + .1 * i)
    if i == 3:
        m.add(boom(.5, r, 55, .5, noise_f=500), d * .5, .6)
    return m.render()


def _swing_dagger(r, i):
    d = [.11, .12, .17][i - 1]
    m = Mix()
    if i == 3:
        m.add(whoosh(.1, [(0, 3000), (.1, 9000)], r, 2.5, .5, 1.2), 0, .8)
        m.add(whoosh(.1, [(0, 9000), (.1, 3500)], r, 2.5, .5, 1.2), .065, 1.0)
    else:
        pts = [[(0, 3000), (d, 9500)], [(0, 9500), (d, 3200)]][i - 1]
        m.add(whoosh(d, pts, r, 2.8, .5, 1.2), 0, 1.0)
    m.add(tick(r, .01, 7000, .002), d * .25, .15)
    return m.render()


def _swing_stab(r, i):
    d = [.15, .16, .2][i - 1]
    n = N(d)
    t = np.arange(n) / SR
    m = Mix()
    m.add(whoosh(d, [(0, 2300), (d, 4800)], r, 7.0 + i, .55, 1.0), 0, 1.0)
    f = curve(d, [(0, 2200), (d, 4200 + 300 * i)], log=True) * (1 + .01 * np.sin(2 * np.pi * 40 * t))
    m.add(sine(f, n) * bump(d, .5, 1.5), 0, .12)
    m.add(whoosh(d, [(0, 5000), (d, 8000)], r, 1.0, .6, 2.0), 0, .2)
    if i == 3:
        m.add(whoosh(.2, [(0, 400), (.2, 1600)], r, 1.0, .5, 1.5), 0, .35)
    return m.render()


def _swing_scythe(r, i):
    d = [.55, .6, .85][i - 1]
    m = Mix()
    pts = [[(0, 350), (d * .5, 1500), (d, 700)], [(0, 1800), (d * .5, 800), (d, 450)], [(0, 300), (d * .4, 1200), (d * .75, 2600), (d, 500)]][i - 1]
    m.add(whoosh(d, pts, r, .8, .45, 1.2, 'pink'), 0, 1.0)
    m.add(whoosh(d, [(0, 2500), (d, 6000)], r, 1.0, .5, 2.0), 0, .2)
    m.add(chain(d * .8, r, 6 + 2 * i, 1300, 3400, .045, 1.0), d * .2, .35)
    m.add(modal(2600, BAR, .6, .2, r, .01), d * .4, .1 + .03 * i)
    if i == 3:
        m.add(lp(noise(N(d), r, 'brown'), 200, 2) * bump(d, .5, 1.5) * 1.6, 0, .5)
    return m.render()


def _swing_hammer(r, i):
    d = [.38, .42, .6][i - 1]
    m = Mix()
    m.add(sweep(noise(N(d), r, 'pink'), curve(d, [(0, 120), (d * .55, 750), (d, 200)], log=True), 'lp', 1) * bump(d, .55, 1.6), 0, 1.0)
    m.add(lp(noise(N(d), r, 'brown'), 130, 2) * bump(d, .6, 1.5) * 1.8, 0, .9)
    m.add(thump(80, 38, .35, .07, .14, 1.4), d * .6, .35 + .15 * i)
    if i == 3:
        m.add(boom(.5, r, 48, .6, noise_f=400), d * .55, .7)
    return m.render()


for _i in (1, 2, 3):
    add(f'swing_sword_{_i}', (lambda i: lambda r: _swing_sword(r, i))(_i), [-5, -4, -2.5][_i - 1])
    add(f'swing_great_{_i}', (lambda i: lambda r: _swing_great(r, i))(_i), [-4, -3, -1][_i - 1])
    add(f'swing_dagger_{_i}', (lambda i: lambda r: _swing_dagger(r, i))(_i), [-7, -6.5, -5][_i - 1])
    add(f'swing_stab_{_i}', (lambda i: lambda r: _swing_stab(r, i))(_i), [-7, -6, -4.5][_i - 1])
    add(f'swing_scythe_{_i}', (lambda i: lambda r: _swing_scythe(r, i))(_i), [-5, -4, -2][_i - 1])
    add(f'swing_hammer_{_i}', (lambda i: lambda r: _swing_hammer(r, i))(_i), [-4, -3, -1][_i - 1])


@sfx('swing_air', -8)
def _(r):
    return whoosh(.2, [(0, 700), (.2, 2400)], r, 1.0, .5, 1.5)


# =============================================================== IMPACTOS
def _hflesh(r, i):
    f = [120, 150, 100][i - 1]
    m = Mix()
    m.add(flesh_hit(r, f, 1.0, wet=[1.0, 1.3, .8][i - 1]), 0, 1.0)
    m.add(tick(r, .015, [1800, 1400, 2400][i - 1], .004), 0, .6)
    m.add(thump(f * 2.4, f * .8, .12, .02, .04), 0, .5)
    if i == 3:
        m.add(bubbles(.2, r, 4, 200, 400), .03, .3)
    return m.render()


for _i in (1, 2, 3):
    add(f'hit_flesh_{_i}', (lambda i: lambda r: _hflesh(r, i))(_i), [-2, -2, -1][_i - 1])


@sfx('hit_metal_1', -1)
def _(r):
    m = Mix()
    m.add(tick(r, .02, 1500, .004), 0, .9)
    m.add(thump(260, 90, .15, .02, .05, 1.4), 0, .8)
    m.add(modal(1050, PLATE, .6, .15, r, .004), 0, 1.0)
    m.add(modal(2300, BAR, .3, .07, r), 0, .4)
    return reverb(m.render(), .4, .08, 5000, seed=30)


@sfx('hit_metal_2', -1)
def _(r):
    m = Mix()
    m.add(tick(r, .02, 2000, .004), 0, 1.0)
    m.add(thump(320, 110, .12, .02, .04, 1.4), 0, .7)
    m.add(modal(1550, PLATE, .55, .13, r, .004), 0, 1.0)
    m.add(modal(3400, BAR, .3, .06, r), 0, .5)
    return reverb(m.render(), .4, .08, 6000, seed=31)


@sfx('hit_crit', 0)
def _(r):
    m = Mix()
    m.add(sat(hp(noise(N(.1), r), 800, 2) * expdec(.1, .02, .0003), 3), 0, .9)
    m.add(thump(260, 50, .5, .06, .2, 1.8), 0, 1.0)
    m.add(modal(3200, BAR, .9, .3, r, .003, .4), 0, .8)
    m.add(modal(mt(96), GLASS[:3], .8, .25, r), 0, .6)
    m.add(modal(1500, PLATE, .5, .12, r), 0, .5)
    m.add(sparkle(.5, r, 22, 5000, 13000, .05, 2.0), .01, .35)
    m.add(flesh_hit(r, 140), 0, .5)
    return reverb(m.render(), .6, .12, 7000, seed=32)


@sfx('hit_magic', -3)
def _(r):
    d = .38
    n = N(d)
    t = np.arange(n) / SR
    m = Mix()
    f = curve(d, [(0, 1800), (d, 500)], log=True)
    m.add(fm(f, 1.41, 3 * np.exp(-t / .1), n) * expdec(d, .1, .0008), 0, .8)
    m.add(thump(220, 90, .15, .03, .06), 0, .6)
    m.add(modal(mt(88), GLASS, .5, .12, r), 0, .4)
    m.add(sparkle(.3, r, 14, 3000, 9000, .04), 0, .3)
    return reverb(m.render(), .5, .12, 6000, seed=33)


@sfx('hit_stone', -2)
def _(r):
    m = Mix()
    m.add(thump(180, 60, .3, .03, .1, 1.6), 0, 1.0)
    m.add(tick(r, .03, 1000, .008), 0, .8)
    m.add(debris(.35, r, 22, 400, 3000, .05), 0, .7)
    m.add(modal(700, BAR, .2, .05, r), 0, .4)
    return m.render()


@sfx('hit_bone', -2)
def _(r):
    m = Mix()
    m.add(tick(r, .02, 2200, .004), 0, .9)
    m.add(modal(900, BONE, .2, .035, r, .02), 0, 1.0)
    m.add(modal(1500, BONE, .15, .025, r, .02), .004, .7)
    m.add(thump(170, 80, .12, .02, .04), 0, .7)
    m.add(debris(.18, r, 8, 1200, 5000, .02), .01, .35)
    return m.render()


@sfx('hit_ice', -2)
def _(r):
    m = Mix()
    m.add(tick(r, .02, 3000, .004), 0, .9)
    m.add(shatter(.45, r, 3000, 10000, 40, .045), 0, .8)
    m.add(thump(240, 90, .12, .02, .04), 0, .5)
    m.add(modal(mt(91), GLASS, .5, .15, r), 0, .35)
    return reverb(m.render(), .4, .1, 7000, seed=34)


@sfx('hit_fire', -2)
def _(r):
    m = Mix()
    n = N(.5)
    m.add(boom(.3, r, 80, .8, noise_f=2500), 0, .9)
    m.add(sweep(noise(n, r), curve(.5, [(0, 4000), (.5, 800)], log=True), 'lp') * expdec(.5, .15, .002), 0, .6)
    m.add(crackle(.5, curve(.5, [(0, 1800), (.5, 200)]), r, 3000, 1.2, 1200) * expdec(.5, .22, .002), 0, .6)
    return reverb(m.render(), .4, .1, 5000, seed=35)


@sfx('hit_shock', -2)
def _(r):
    m = Mix()
    m.add(zap(.3, r, 3500, 400, 1.0), 0, .9)
    m.add(tick(r, .02, 4000, .003), 0, .9)
    m.add(thump(200, 70, .15, .02, .05), 0, .5)
    m.add(crackle(.3, curve(.3, [(0, 3000), (.3, 300)]), r, 5000, .9, 2000) * expdec(.3, .1), 0, .6)
    return m.render()


@sfx('hit_blood', -2)
def _(r):
    m = Mix()
    m.add(squelch(.22, r, 900), 0, 1.0)
    m.add(thump(130, 60, .15, .03, .06), 0, .7)
    m.add(tick(r, .015, 1500, .004), 0, .5)
    m.add(bubbles(.25, r, 6, 150, 350), .02, .5)
    m.add(sweep(noise(N(.2), r), curve(.2, [(0, 3000), (.2, 700)], log=True), 'bp', 1.5) * expdec(.2, .05, .002), .0, .5)
    return m.render()
