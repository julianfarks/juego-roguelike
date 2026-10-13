"""Materiales y voces de jefes."""
from recipes import *


def scatter(dur, r, n_ev, fl, fh, parts, tau, dens=1.0, g=1.0):
    n = N(dur)
    out = np.zeros(n)
    for _ in range(int(n_ev)):
        i = int((r.random() ** dens) * dur * .95 * SR)
        f = np.exp(r.uniform(np.log(fl), np.log(fh)))
        s = modal(f, parts, tau * 6, tau * r.uniform(.6, 1.4), r, .02)
        e = min(n, i + len(s))
        out[i:e] += s[:e - i] * r.uniform(.25, 1)
    return out * g


def flapswarm(dur, r, n_ev=40, g=1.0, chirp=True):
    n = N(dur)
    out = np.zeros(n)
    for _ in range(n_ev):
        i = int(r.random() ** .8 * dur * .9 * SR)
        L = N(r.uniform(.07, .14))
        s = sweep(noise(L, r, 'pink'), curve(L / SR, [(0, 400), (L / SR * .5, 1600), (L / SR, 500)], log=True), 'bp', 1.0) * bump(L / SR, .4, 1.5)
        e = min(n, i + L)
        out[i:e] += s[:e - i] * r.uniform(.3, 1)
        if chirp and r.random() < .35:
            Lc = N(r.uniform(.04, .09))
            f = curve(Lc / SR, [(0, r.uniform(5500, 9000)), (Lc / SR, r.uniform(3000, 5000))], log=True)
            c = sine(f, Lc) * expdec(Lc / SR, .03, .002)
            ic = i + int(r.uniform(0, .05) * SR)
            e = min(n, ic + Lc)
            if e > ic:
                out[ic:e] += c[:e - ic] * .25
    return out / (out.std() + 1e-9) * .25 * g


def bossvox(p, r, d, kind='roar'):
    f0 = p['f0']
    if kind == 'roar':
        pts = [(0, .75), (.1 * d, 1.25), (.45 * d, 1.1), (d, .6)]
        env = bump(d, .2, .9)
    elif kind == 'hurt':
        pts = [(0, 1.2), (.25 * d, 1.25), (d, .75)]
        env = bump(d, .15, 1.0)
    elif kind == 'phase':
        pts = [(0, .6), (.5 * d, 1.3), (.75 * d, 1.5), (d, .7)]
        env = bump(d, .5, .8)
    else:  # atk
        pts = [(0, .9), (.3 * d, 1.25), (d, .8)]
        env = bump(d, .25, 1.0)
    f = curve(d, [(t, f0 * v) for t, v in pts], log=True)
    kw = dict(scale=p['scale'], dist=p['dist'], growl=p['growl'], growl_f=p['growl_f'], breath=p['breath'],
              jitter=p['jitter'], vib=p.get('vib', (5.5, .012)), nv=p.get('nv', 2))
    y = voice(d, f, r, p['v0'], p['v1'], env=env, **kw)
    y += p.get('low', .6) * voice(d, f * .5, r, p['v1'], p['v0'], env=env, **{**kw, 'scale': p['scale'] * .8, 'dist': p['dist'] * .8})
    if p.get('hi', 0):
        y += p['hi'] * voice(d, f * 2.0, r, 'a', 'e', env=env, **{**kw, 'scale': p['scale'] * 1.1})
    return y


# ------------------------------------------------------------------ materiales (textura sostenida / impacto)
def mat_rey(r, d):
    m = Mix()
    m.add(scatter(d, r, d * 12, 500, 2200, BONE, .03), 0, 1.0)
    m.add(creak(d, r, 30, 55, (700, 2000), 10, 2.0) * swell(d, .2, .3), 0, .3)
    m.add(whisper(d, r, 5, ('o', 'e'), 1.0, 600, 1), 0, .25)
    return m.render(d)


def imp_rey(r, g=1.0):
    m = Mix()
    m.add(tick(r, .02, 1500, .005), 0, .8)
    m.add(thump(150, 55, .35, .04, .12, 1.5), 0, 1.0)
    m.add(scatter(.5, r, 14, 500, 2500, BONE, .03, 2.0), 0, .8)
    m.add(modal(380, PLATE, 1.0, .3, r, .03), 0, .6)
    m.add(modal(1450, BAR, .5, .12, r, .03), 0, .3)
    m.add(chain(.4, r, 6, 800, 2200, .04), .05, .3)
    return m.render() * g


def mat_magma(r, d):
    m = Mix()
    m.add(bubbles(d, r, int(d * 14), 60, 220), 0, 1.0)
    m.add(hp(noise(N(d), r), 3000, 1) * swell(d, d * .4, d * .4) * .06, 0, 1.0)
    m.add(creak(d, r, 22, 40, (250, 900), 6, 2.0) * swell(d, .2, .3), 0, .35)
    m.add(crackle(d, 500, r, 2500, 1.2, 800), 0, .3)
    return m.render(d)


def imp_magma(r, g=1.0):
    m = Mix()
    m.add(boom(.9, r, 48, 1.0, noise_f=1200), 0, 1.0)
    m.add(modal(240, PLATE, 1.0, .4, r, .02), 0, .6)
    m.add(debris(.6, r, 25, 250, 2500, .06), .02, .6)
    m.add(crackle(.6, curve(.6, [(0, 2500), (.6, 300)]), r, 3000, 1.1, 1000) * expdec(.6, .25), 0, .5)
    m.add(hp(noise(N(.5), r), 3500, 1) * expdec(.5, .15, .004), .05, .15)
    return m.render() * g


def mat_frost(r, d):
    m = Mix()
    m.add(gust(d, r, 1000, 5000, 1.0, 1.0), 0, .7)
    m.add(sparkle(d, r, int(d * 12), 3500, 11000, .08), 0, .5)
    m.add(crackle(d, 250, r, 6000, 1.0, 2500), 0, .4)
    return m.render(d)


def imp_frost(r, g=1.0):
    m = Mix()
    m.add(tick(r, .02, 3000, .004), 0, .8)
    m.add(shatter(.7, r, 3000, 10000, 40, .05), 0, .8)
    m.add(thump(190, 60, .3, .03, .1, 1.4), 0, .8)
    m.add(modal(mt(88), GLASS, 1.0, .35, r), 0, .4)
    m.add(modal(mt(76), BELL, 1.2, .4, r), 0, .25)
    return m.render() * g


def mat_void(r, d):
    n = N(d)
    m = Mix()
    m.add(whisper(d, r, 6, ('i', 'e'), 1.0, 900, 3), 0, .7)
    m.add(drone(d, 45, r, 1.0, .012, 3, 400, d * .3, d * .3), 0, .8)
    m.add(reverse(whoosh(d, [(0, 200), (d, 4000)], r, 1.5, .8, 1.0)), 0, .3)
    m.add(tonecloud([mt(51), mt(54)], d, r, .3, d * .4, d * .4), 0, .5)
    return m.render(d)


def imp_void(r, g=1.0):
    m = Mix()
    m.add(reverse(boom(.5, r, 50, .8, noise_f=2500)), 0, .6)
    m.add(boom(1.0, r, 38, 1.0, noise_f=700), .5, 1.0)
    d = .9
    n = N(d)
    t = np.arange(n) / SR
    f = curve(d, [(0, 800), (d, 60)], log=True)
    m.add(fm(f, 1.01, 2.5 * (1 - t / d), n) * expdec(d, .3, .002), .5, .5)
    m.add(whisper(.8, r, 8, ('i', 'e'), 1.0, 1200, 2), .5, .3)
    return m.render() * g


def mat_ent(r, d):
    m = Mix()
    m.add(creak(d, r, 25, 55, (250, 1000), 7, 1.6) * swell(d, .15, .3), 0, .8)
    m.add(creak(d * .8, r, 40, 75, (500, 1500), 9), d * .1, .35)
    m.add(scatter(d, r, d * 6, 150, 400, [(1, 1), (2.4, .35), (4.1, .15)], .06), 0, .6)
    n = N(d)
    lv = hp(noise(n, r), 3500, 2) * np.abs(lp(noise(n, r), 20, 1))
    m.add(lv / (lv.std() + 1e-9) * .12 * swell(d, d * .3, d * .3), 0, 1.0)
    return m.render(d)


def imp_ent(r, g=1.0):
    m = Mix()
    m.add(thump(120, 40, .4, .05, .14, 1.5), 0, 1.0)
    m.add(tick(r, .03, 1200, .008), 0, .8)
    m.add(scatter(.5, r, 8, 120, 350, [(1, 1), (2.4, .4), (4.1, .2)], .07, 1.5), 0, .8)
    m.add(creak(.7, r, 30, 60, (300, 1100), 7), .02, .5)
    m.add(debris(.5, r, 20, 600, 4000, .03), .03, .45)
    return m.render() * g


def mat_titan(r, d):
    m = Mix()
    m.add(rumble(d, r, 110, 4, .6, env=swell(d, d * .3, d * .4)), 0, 1.4)
    m.add(crackle(d, 500, r, 4500, .9, 1800) * swell(d, d * .3, d * .4), 0, .6)
    m.add(creak(d, r, 22, 45, (300, 1000), 6, 2.0) * swell(d, .2, .3), 0, .3)
    return m.render(d)


def imp_titan(r, g=1.0):
    m = Mix()
    m.add(sat(hp(noise(N(.2), r), 700, 2) * expdec(.2, .03, .0003), 5), 0, .8)
    m.add(boom(.9, r, 45, 1.0, noise_f=1500), 0, 1.0)
    m.add(modal(160, PLATE, 1.4, .6, r, .03), 0, .7)
    m.add(modal(520, PLATE, .8, .25, r, .02), 0, .45)
    m.add(zap(.3, r, 4500, 400, 1.0), .02, .5)
    return m.render() * g


def mat_blood(r, d):
    m = Mix()
    m.add(bubbles(d, r, int(d * 10), 120, 450), 0, .6)
    m.add(wingflap(d, r, 5.5, 900, 1.0), 0, .7)
    m.add(whisper(d, r, 7, ('e', 'i'), 1.0, 1100, 2), 0, .3)
    return m.render(d)


def imp_blood(r, g=1.0):
    m = Mix()
    m.add(squelch(.4, r, 1000), 0, 1.0)
    m.add(slash(r, .1, 1500, 7000, 2, 1.0), 0, .6)
    m.add(thump(120, 50, .3, .04, .1, 1.4), 0, .9)
    m.add(sweep(noise(N(.3), r), curve(.3, [(0, 3000), (.3, 600)], log=True), 'bp', 1.5) * expdec(.3, .08, .002), 0, .6)
    m.add(bubbles(.4, r, 8, 120, 350), .05, .4)
    return m.render() * g


def mat_sun(r, d):
    m = Mix()
    m.add(choir([mt(55), mt(62)], d, r, ('o', 'a'), d * .4, d * .4, g=.6), 0, .9)
    m.add(bell(mt(67), d, d * .4, r), 0, .25)
    m.add(sparkle(d, r, int(d * 8), 3000, 9000, .1), 0, .3)
    return m.render(d)


def imp_sun(r, g=1.0):
    m = Mix()
    m.add(thump(130, 50, .4, .05, .15, 1.5), 0, 1.0)
    m.add(tick(r, .02, 1800, .004), 0, .7)
    m.add(modal(800, PLATE, 1.2, .4, r), 0, .7)
    m.add(bell(mt(72), 1.4, .6, r), 0, .6)
    m.add(choir([mt(55), mt(62)], .7, r, ('a', 'a'), .01, .5), 0, .5)
    return m.render() * g


def mat_hunter(r, d):
    m = Mix()
    m.add(drone(d, 41, r, 1.0, .01, 3, 500, d * .3, d * .3), 0, .8)
    m.add(whisper(d, r, 6, ('o', 'e'), 1.0, 600, 2), 0, .4)
    m.add(squelch(d * .5, r, 600) * .3, d * .1, 1.0)
    m.add(scatter(d, r, d * 4, 400, 1500, BONE, .03), 0, .3)
    return m.render(d)


def imp_hunter(r, g=1.0):
    m = Mix()
    m.add(flesh_hit(r, 100), 0, .9)
    m.add(boom(1.0, r, 42, 1.0, noise_f=900), 0, 1.0)
    m.add(modal(mt(40), BELL, 1.5, .6, r), 0, .35)
    m.add(scatter(.4, r, 8, 400, 1800, BONE, .03, 2.0), 0, .4)
    m.add(squelch(.3, r, 700), 0, .5)
    return m.render() * g


MATS = dict(rey_exanime=(mat_rey, imp_rey), coloso_magma=(mat_magma, imp_magma), reina_escarcha=(mat_frost, imp_frost),
            devorador_vacio=(mat_void, imp_void), ent_ancestral=(mat_ent, imp_ent), titan_tormenta=(mat_titan, imp_titan),
            matriarca_sangre=(mat_blood, imp_blood), guardian_eclipse=(mat_sun, imp_sun), cazador=(mat_hunter, imp_hunter))
