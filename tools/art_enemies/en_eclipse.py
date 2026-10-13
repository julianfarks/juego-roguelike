from common import *
from en_catacumbas import enemy_sheet, STD, DARK, WHITE
from en_forja import bruto_pose

GOLD = Mat(ramp=['#2a1a06', '#6a4a10', '#b08820', '#e8c040', '#fff0a0'], bevel=1.8, tex=0.15, seed=131, bias=0.5)
GOLD_D = Mat(ramp=['#1c1004', '#46300a', '#7a5a14', '#a88424', '#d0ac3c'], bevel=1.8, tex=0.15, seed=132)
GOLD_E = Mat(ramp=['#c89a20', '#f0c840', '#fff0a0', '#ffffff'], emi=True, nooutline=True, bevel=1.4, dith=0.2)
BLK = Mat(ramp=['#05040a', '#0e0c16', '#1c1824', '#2c2638', '#443c52'], bevel=1.8, tex=0.2, seed=133, bias=0.5)
BLK_D = Mat(ramp=['#030207', '#08060e', '#120e1a', '#1e1828'], bevel=1.8, seed=134)
PIGS = Mat(ramp=['#2a1418', '#583036', '#8c5254', '#c08068', '#e8b090'], bevel=2.6, tex=0.25, seed=135, bias=0.4)
PIGS_B = Mat(ramp=['#1e0e12', '#40222a', '#683c40', '#965c52', '#b88068'], bevel=2.6, tex=0.25, seed=136)
SNOUT = Mat(ramp=['#3a1c20', '#7a4040', '#b06a60', '#dc9a82', '#f8c8a8'], bevel=1.6, seed=137)
TUSK = Mat(ramp=['#4a3c28', '#8a7650', '#c8b484', '#f4e8c0'], bevel=0.8, seed=138)
PALEG = '#F2E6B8'
ECL = '#FFE9A0'
MASKE = Mat(ramp=['#6a5a30', '#a8924c', '#d8c47c', '#f2e6b8', '#fffbe0'], bevel=1.6, seed=139)
CLOAKE = Mat(ramp=['#05040a', '#100c18', '#1e1a2a', '#322c44', '#4c4462'], bevel=2.4, tex=0.25, seed=140)
CLOAKE_D = Mat(ramp=['#030207', '#0a0810', '#14101c', '#221c30'], bevel=2.0, seed=141)
TRAIL_G = Mat(ramp=['#a87c18', '#e8c040', '#fff0a0', '#ffffff'], emi=True, nooutline=True, bevel=1.5, dith=0.2)
SUNC = Mat(ramp=['#c06a10', '#f0a020', '#ffd848', '#fff4b0', '#ffffff'], emi=True, nooutline=True, bevel=7.0, dith=0.2)
SUNR = Mat(ramp=['#a84a08', '#e08a14', '#ffc030', '#fff0a0'], emi=True, nooutline=True, bevel=2.0, dith=0.25)


def eclipse_disc(c, x, y, r, ph=0.0):
    with c.part(GOLD_E, bevel=1.0) as p:
        p.ell(x, y, r + 1.4)
        p.ell(x, y, r - 0.4, v=0)
    with c.part(BLK_D, bevel=r * 0.8) as p:
        p.ell(x + 0.5, y + 0.3, r - 0.3)
    c.glow(x, y, r + 3, '#ffe080', 0.35)


# ------------------------------------------------------------------ PIGLIN DORADO (64x64)
def pig_body(c, P, a='idle', with_mace=True):
    hx, dy, lean, ph = P['hx'], P['dy'], P['lean'], P['ph']
    hip = (hx, -22 + dy)
    sl = (math.sin(lean), -math.cos(lean))
    if P['walk']:
        f1 = gait(ph, P['stride'], P['lift']); f2 = gait((ph + 0.5) % 1, P['stride'], P['lift'])
    elif a in ('windup', 'attack'):
        f1, f2 = (-8, 0), (7, 0)
    else:
        f1, f2 = (-5, 0), (5, 0)
    chest = (hip[0] + 13 * sl[0], hip[1] + 13 * sl[1])
    shf = (chest[0] + 2, chest[1] - 2)
    e2, h2 = fk(shf, P['arm2'][0], 11.5, P['arm2'][1], 11.5)
    with c.part(PIGS_B, line=0.5, bevel=2.8) as p:
        p.limb(shf, e2, 4.0, 3.5); p.limb(e2, h2, 3.5, 3.2)
    with c.part(GOLD_D, line=0.5, bevel=1.6) as p:
        p.limb((lerp(e2[0], h2[0], 0.4), lerp(e2[1], h2[1], 0.4)), h2, 4.0, 3.7)
    with c.part(PIGS_B, bevel=2.0) as p:
        p.ell(h2[0] + 0.5, h2[1] + 0.5, 3.5)
    leg(c, (hip[0] - 3, hip[1] + 2), (hip[0] - 3 + f1[0], f1[1]), 9.8, 9.8, 4.6, 4.0, GOLD_D, bend=-1, footmat=GOLD_D, footlen=7, footh=3.6)
    with c.at(hip[0] + 2 * sl[0], hip[1] + 2 * sl[1], lean):
        with c.part(PIGS, line=0.5, bevel=3.8) as p:
            p.poly([(-11, -22), (13, -22), (14, -14), (10, -2), (-9, -2), (-12, -12)])
        # faldon de tela negra con ribete
        with c.part(BLK, line=0.5, bevel=1.6) as p:
            p.poly([(-9, -4), (11, -4), (13, 4), (11, 14), (-6, 16), (-10, 6)])
        with c.part(GOLD, bevel=1.0) as p:
            p.poly([(-10, 5), (13, 4.4), (12.4, 7), (-9, 8)])
        # peto negro-oro con disco de eclipse
        with c.part(BLK, line=0.5, bevel=2.4) as p:
            p.poly([(-11, -23), (8, -25), (11, -16), (9, -6), (-8, -5), (-12, -13)])
        with c.part(GOLD, line=0.4, bevel=1.2) as p:
            p.poly([(-11.5, -23.5), (8.5, -25.5), (9, -23), (-11, -21)])
            p.poly([(-8, -6.4), (9.4, -7.4), (9.2, -5), (-8, -4.2)])
        eclipse_disc(c, -0.5, -15, 4.2)
        with c.part(GOLD_E, bevel=0.6) as p:
            for k in range(6):
                ang = k * 1.047 + ph * 0.5
                p.limb((-0.5 + math.cos(ang) * 6.6, -15 + math.sin(ang) * 6.6), (-0.5 + math.cos(ang) * 8.4, -15 + math.sin(ang) * 8.4), 0.4)
    leg(c, (hip[0] + 3, hip[1] + 2), (hip[0] + 3 + f2[0], f2[1]), 9.8, 9.8, 4.8, 4.1, GOLD, bend=-1, footmat=GOLD, footlen=7, footh=3.6)
    # cabeza de cerdo
    nk = (hip[0] + 23 * sl[0] + 3, hip[1] + 23 * sl[1] - 5)
    with c.at(nk[0] + 3.0, nk[1], lean * 0.4 + P['head']):
        with c.part(PIGS, line=0.5, bevel=2.8) as p:
            p.ell(0, 0, 7.0, 6.4)
        with c.part(PIGS_B, line=0.5, bevel=1.8) as p:     # oreja
            p.poly([(-5, -4), (-9.5, -9), (-10.5, -3), (-6.5, 0)])
        with c.part(SNOUT, line=0.5, bevel=1.8) as p:
            p.ell(7.0, 1.6, 4.6, 3.8)
        with c.part(DARK) as p:
            p.ell(8.2, 1.2, 0.8, 1.1); p.ell(10.6, 1.4, 0.7, 1.0)
            p.poly([(3.5, -2.2), (7.5, -3.6), (7.4, -2.3), (3.6, -0.8)])
        with c.part(GOLD_E, bevel=0.5) as p:
            p.ell(4.4, -1.2, 1.0, 0.8)
        c.glow(4.4, -1.2, 3.2, '#ffd050', 0.35 + 0.4 * P['hot'])
        with c.part(TUSK, line=0.4, bevel=0.8) as p:
            p.poly([(3.6, 4.2), (4.8, 4.4), (4.6, 0.6)]); p.poly([(8.6, 4.8), (9.8, 4.4), (10.4, 1.0)])
        with c.part(GOLD, line=0.5, bevel=1.6) as p:       # yelmo dorado con cresta
            p.poly([(-6.5, 0), (-6, -5.5), (-2, -8), (3.5, -7.2), (5.5, -4), (1.5, -3.6), (-2, -2.6), (-4, 0)])
            p.poly([(-3, -7.6), (-1.5, -12.5), (1.5, -7.6)])
        with c.part(GOLD_E) as p:
            p.rect(-1.2, -7, 0.2, -4)
    shn = (chest[0] - 2, chest[1] - 2)
    e1, h1 = fk(shn, P['arm'][0], 11.5, P['arm'][1], 11.5)
    with c.part(PIGS, line=0.5, bevel=2.8) as p:
        p.limb(shn, e1, 4.4, 3.9); p.limb(e1, h1, 3.9, 3.4)
    with c.part(GOLD, line=0.5, bevel=1.6) as p:
        p.limb((lerp(e1[0], h1[0], 0.4), lerp(e1[1], h1[1], 0.4)), h1, 4.3, 3.9)
    if with_mace:
        ha = P['ham']
        d = (math.cos(ha), math.sin(ha)); nr = (-d[1], d[0])
        end = (h1[0] + d[0] * 17, h1[1] + d[1] * 17)
        with c.part(GOLD_D, line=0.4, bevel=1.0) as p:
            p.limb((h1[0] - d[0] * 5, h1[1] - d[1] * 5), end, 1.7)
        hc = (end[0] + d[0] * 5.5, end[1] + d[1] * 5.5)
        with c.part(GOLD, line=0.5, bevel=3.0) as p:
            p.ell(hc[0], hc[1], 6.4)
            for k in range(8):
                ang = k * 0.785 + ha
                p.poly([(hc[0] + math.cos(ang - 0.28) * 5.2, hc[1] + math.sin(ang - 0.28) * 5.2), (hc[0] + math.cos(ang) * 10, hc[1] + math.sin(ang) * 10),
                        (hc[0] + math.cos(ang + 0.28) * 5.2, hc[1] + math.sin(ang + 0.28) * 5.2)])
        with c.part(GOLD_E, bevel=2.0) as p:
            p.ell(hc[0] - d[0] * 0.5, hc[1] - d[1] * 0.5, 2.6 * (0.6 + 0.4 * P['hot']))
        c.glow(hc[0], hc[1], 10, '#ffd060', 0.15 + 0.5 * P['hot'])
        if P['k'] is not None and 0.3 < P['k'] < 0.8:
            arc_trail(c, shn[0], shn[1], 12, 28, -1.9 + (P['k'] - 0.2) * 3, -0.5 + (P['k'] - 0.2) * 3, TRAIL_G)
            for q in range(8):
                c.dotw(hc[0] + 6 + q * 2, -1.5 - (q % 3) * 1.2, '#e8c040' if q % 2 else '#fff0a0')
    with c.part(PIGS, bevel=2.0) as p:
        p.ell(h1[0] + 0.3, h1[1] + 0.3, 3.7)
    with c.part(GOLD, line=0.5, bevel=2.0) as p:           # hombrera con pinchos
        sx, sy = shn[0] - 1, shn[1] - 1
        p.poly([(sx - 5.5, sy + 3), (sx - 4.5, sy - 3), (sx + 2, sy - 6), (sx + 7, sy - 2), (sx + 6, sy + 3), (sx, sy + 4.5)])
        p.poly([(sx - 0.5, sy - 5.5), (sx + 1.5, sy - 11), (sx + 3.5, sy - 5)])
    with c.part(GOLD_E) as p:
        p.ell(shn[0] + 0.5, shn[1] - 2.5, 0.9)


def draw_piglin(c, a, i, n):
    if a == 'death':
        return death_piglin(c, i, n)
    P = bruto_pose(a, i, n)
    # mazo al hombro en reposo
    pig_body(c, P, a)
    if P['flash']:
        c.flash(WHITE, P['flash'])
    if a == 'windup' and i == n - 1:
        c.flash('#ffd060', 0.1)


def _p_mace(c):
    with c.part(GOLD_D, line=0.4, bevel=1.0) as p:
        p.limb((-12, 0), (6, 0), 1.7)
    with c.part(GOLD, line=0.5, bevel=3.0) as p:
        p.ell(11, 0, 6.4)
        for k in range(8):
            ang = k * 0.785
            p.poly([(11 + math.cos(ang - 0.28) * 5.2, math.sin(ang - 0.28) * 5.2), (11 + math.cos(ang) * 10, math.sin(ang) * 10), (11 + math.cos(ang + 0.28) * 5.2, math.sin(ang + 0.28) * 5.2)])


def _p_pighead(c):
    with c.part(PIGS, line=0.5, bevel=2.8) as p:
        p.ell(0, 0, 7.0, 6.4)
    with c.part(SNOUT, line=0.5, bevel=1.8) as p:
        p.ell(7.0, 1.6, 4.6, 3.8)
    with c.part(GOLD, line=0.5, bevel=1.6) as p:
        p.poly([(-6.5, 0), (-6, -5.5), (-2, -8), (3.5, -7.2), (5.5, -4), (1.5, -3.6), (-2, -2.6), (-4, 0)])


def _p_disc(c):
    eclipse_disc(c, 0, 0, 4.2)


def death_piglin(c, i, n):
    if i == 0:
        pig_body(c, bruto_pose('hurt', 0, 2), 'hurt')
        c.flash(WHITE, 0.45)
        return
    u = i / (n - 1)
    P = bruto_pose('hurt', 1, 2)
    ang = kf(u, [(0, 0), (0.25, -0.15), (0.55, 0.5), (0.8, 1.3), (1, 1.5)])
    P['lean'] = kf(u, [(0, -0.14), (0.3, 0.05), (1, 0.2)])
    P['dy'] = kf(u, [(0, 0), (0.3, 6), (1, 8)])
    P['arm'] = (kf(u, [(0, 0.7), (1, 2.5)]), 0.4)
    P['arm2'] = (kf(u, [(0, 0.7), (1, 2.2)]), 0.4)
    P['hot'] = 1 - u
    P['head'] = kf(u, [(0, -0.15), (1, 0.4)])
    P['hx'] = -3
    pivx = -17
    with c.at(pivx, 0.5, ang):
        with c.at(-pivx - 3 + 3 * u, 0, 0):
            pig_body(c, P, 'hurt', with_mace=False)
    items = [dict(fn=_p_mace, x=14, y=-30, r=7, vx=7, vy=-7, spin=4, rest=0.1, bounce=0.3),
             dict(fn=_p_pighead, x=4, y=-42, r=6, vx=5, vy=-9, spin=-5, rest=0.4, bounce=0.3)]
    for d_ in items:
        d_['vx'] *= 0.6; d_['vy'] *= 0.7
    b = Bits(items, seed=3, T=0.65, g=3.0)
    if u > 0.12:
        draw_bits(c, b, min(1, (u - 0.12) / 0.88))
    if u > 0.4:
        for q in range(10):
            c.dotw(-16 + q * 4 + (q - 5) * u * 2, -2 - (q % 4) * 2 - (u - 0.4) * 8, '#e8c040' if q % 2 else '#fff0a0')


# ------------------------------------------------------------------ ESPECTRO
def esp_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(x=-2.0, y=-7 + 1.4 * s, ph=t, lean=0.0, arm=(0.5, 0.8), armb=(1.0, 0.5), blade=0.0, ba=-0.6, glow=0.0, flash=0.0, trail=None, solid=1.0, head=0.0, eye=0.5)
    if a == 'walk':
        P.update(x=-1, lean=0.2, y=-7 + 1.6 * math.sin(2 * math.pi * t))
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(lean=lerp(0, -0.25, w), x=lerp(-2, -5, w), glow=w, eye=1.0, blade=1.0, ba=lerp(-0.6, -2.3, w), arm=(lerp(0.5, -2.1, w), lerp(0.8, -0.4, w)), head=-0.1 * w, y=-7 - 1.5 * w)
    elif a == 'attack':
        k = i / (n - 1)
        P.update(lean=kf(k, [(0, -0.25), (0.2, 0.2), (0.4, 0.4), (1, 0.05)]), x=kf(k, [(0, -5), (0.2, 0), (0.4, 7), (0.7, 6), (1, 0)]), blade=1.0,
                 ba=kf(k, [(0, -2.3), (0.2, -1.5), (0.4, 0.5), (0.7, 0.8), (1, 0.0)]), arm=(kf(k, [(0, -2.1), (0.2, -1.4), (0.4, 0.6), (0.7, 0.8), (1, 0.4)]), 0.3),
                 glow=1.0 if k < 0.8 else 0.3, eye=1.0, head=kf(k, [(0, -0.1), (0.4, 0.25), (1, 0)]), trail=k if 0.15 < k < 0.75 else None, y=-7 + kf(k, [(0, -1.5), (0.4, 1), (1, 0)]))
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(x=-2 + rx, lean=ln, flash=fl, head=-0.3 if i == 0 else -0.1, eye=0.2, arm=(0.0, 0.5), blade=1.0, ba=-0.2)
    return P


def espectro_body(c, P, nohead=False, sol=1.0):
    x, y, lean, ph = P['x'], P['y'], P['lean'], P['ph'] * 6.283
    sol = sol * P['solid']
    cx_, cy_ = x, y - 18
    sw = math.sin(ph)
    # cola de tunica (se desvanece hacia abajo)
    tail = []
    for k in range(7):
        u = k / 6
        tail.append((cx_ - 1 - u * 6 - lean * 8 * u + math.sin(ph + u * 3) * 2.4 * u, cy_ + 2 + u * 21))
    def tf(lx, ly, y0=cy_ + 6):
        return np.clip(1.25 - (ly - y0) / 15.0, 0, 1) * sol
    with c.part(CLOAKE_D, fade=tf, bevel=3.0, line=0.0) as p:
        p.tube(tail, 7.5, 1.0)
    # brazo trasero
    ab = P['armb']
    sh = (cx_ + 2.5, cy_ - 5.5)
    hb = (cx_ + 7 + 4 * ab[0], cy_ + 1 + 3 * ab[1])
    eb = ik2(sh, hb, 5.2, 5.2, bend=1)
    with c.part(CLOAKE_D, fade=lambda lx, ly: sol, line=0.4, bevel=1.4) as p:
        p.limb(sh, eb, 2.2, 1.8); p.limb(eb, hb, 1.8, 1.2)
    # torso / tunica
    hem = [(cx_ - 8 - lean * 3, cy_ + 12), (cx_ - 4, cy_ + 9 + sw), (cx_, cy_ + 13), (cx_ + 4, cy_ + 9 - sw), (cx_ + 7 + lean * 3, cy_ + 12)]
    with c.part(CLOAKE, line=0.5, bevel=3.0, fade=lambda lx, ly: np.clip(1.3 - (ly - (cy_ + 4)) / 10.0, 0, 1) * sol) as p:
        p.poly([(cx_ - 3.5, cy_ - 8), (cx_ + 3.8, cy_ - 8), (cx_ + 6, cy_ + 0.5)] + hem[::-1] + [(cx_ - 7, cy_ + 1)])
    with c.part(GOLD, bevel=1.0, fade=lambda lx, ly: sol) as p:      # ribetes dorados
        p.poly([(cx_ - 3.5, cy_ - 8), (cx_ - 1.5, cy_ - 8), (cx_ + 0.5, cy_ + 5), (cx_ - 1.5, cy_ + 5)])
        p.rect(cx_ - 6, cy_ + 0.4, cx_ + 6, cy_ + 1.8)
    with c.at(cx_ + 1, cy_ - 3.5, 0):
        eclipse_disc(c, 0, 0, 2.2)
    # cabeza con capucha y mascara
    if not nohead:
        with c.at(cx_ + 2.6 + 3 * lean, cy_ - 11.6, lean * 0.6 + P['head']):
            with c.part(CLOAKE, line=0.5, bevel=2.2, fade=lambda lx, ly: sol) as p:
                p.poly([(-6.5, 5), (-7, -2), (-4, -7), (2, -8.5), (5.6, -5.6), (2.4, -4), (-1, -3.4), (-3, 1), (-3.2, 5.6)])
            with c.part(MASKE, line=0.5, bevel=1.8, fade=lambda lx, ly: sol) as p:
                p.poly([(-2.0, -4.2), (3.0, -4.6), (4.4, -1), (3.8, 3.8), (1.4, 6.0), (-2.0, 3.6)])
            with c.part(DARK) as p:
                p.poly([(0.0, -1.6), (3.6, -2.0), (3.5, -0.4), (0.2, 0.0)])
                p.rect(0.6, 3.0, 3.0, 3.5)
            with c.part(GOLD_E) as p:
                p.poly([(0.6, -1.3), (3.2, -1.6), (3.1, -0.7), (0.7, -0.5)])
            c.glow(2.0, -1.0, 3.2, ECL, 0.35 + 0.5 * P['eye'])
            with c.part(GOLD, bevel=0.8, line=0.3, fade=lambda lx, ly: sol) as p:    # corona de rayos
                p.poly([(-1.5, -4.4), (-3.5, -9.5), (0, -5.0)]); p.poly([(0.4, -4.8), (1.0, -11), (2.4, -4.8)]); p.poly([(2.6, -4.4), (5.5, -9), (4.2, -3.4)])
    # brazo con hoja
    ar = P['arm']
    e, h = fk(sh, ar[0], 5.4, ar[1], 5.4)
    with c.part(CLOAKE, line=0.4, bevel=1.4, fade=lambda lx, ly: sol) as p:
        p.limb(sh, e, 2.3, 1.9); p.limb(e, h, 1.9, 1.3)
    with c.part(MASKE, bevel=0.6, fade=lambda lx, ly: sol) as p:
        p.ell(h[0], h[1], 1.3)
        for q in (-1, 0, 1):
            p.limb(h, (h[0] + 3.2 * math.cos(ar[0] + ar[1] + q * 0.3), h[1] + 3.2 * math.sin(ar[0] + ar[1] + q * 0.3)), 0.4, 0.15)
    if P['blade'] > 0.5:
        ba = P['ba']
        d = (math.cos(ba), math.sin(ba)); nr = (-d[1], d[0])
        tip = (h[0] + d[0] * 17, h[1] + d[1] * 17)
        with c.part(GOLD_E, bevel=1.2, fade=lambda lx, ly: sol) as p:
            p.poly([(h[0] + nr[0] * 1.6, h[1] + nr[1] * 1.6), (h[0] + d[0] * 9 + nr[0] * 2.6, h[1] + d[1] * 9 + nr[1] * 2.6), tip,
                    (h[0] + d[0] * 9 - nr[0] * 0.8, h[1] + d[1] * 9 - nr[1] * 0.8), (h[0] - nr[0] * 1.2, h[1] - nr[1] * 1.2)])
        c.glow(tip[0] - d[0] * 5, tip[1] - d[1] * 5, 6, ECL, 0.3 + 0.5 * P['glow'])
        if P['trail'] is not None:
            an = math.atan2(tip[1] - sh[1], tip[0] - sh[0])
            rr = math.hypot(tip[0] - sh[0], tip[1] - sh[1])
            arc_trail(c, sh[0], sh[1], rr - 8, rr + 2, an - 1.6, an + 0.1, TRAIL_G)


def draw_espectro(c, a, i, n):
    if a == 'death':
        return death_espectro(c, i, n)
    P = esp_pose(a, i, n)
    espectro_body(c, P)
    if P['flash']:
        c.flash(WHITE, P['flash'])


def _p_mask(c):
    with c.part(MASKE, line=0.5, bevel=1.8) as p:
        p.poly([(-2.4, -5.0), (3.0, -5.4), (4.6, -1), (4.0, 4.4), (1.4, 6.8), (-2.4, 4.2)])
    with c.part(DARK) as p:
        p.poly([(0.0, -1.6), (3.6, -2.0), (3.5, -0.4), (0.2, 0.0)])


def death_espectro(c, i, n):
    if i == 0:
        espectro_body(c, esp_pose('hurt', 0, 2))
        c.flash(WHITE, 0.5)
        return
    u = i / (n - 1)
    P = esp_pose('hurt', 1, 2)
    P['y'] = -7 + 5 * u
    P['blade'] = 0
    sol = max(0.0, 1.0 - u * 1.2)
    if sol > 0.02:
        espectro_body(c, P, nohead=(u > 0.35), sol=sol)
    items = [dict(fn=_p_mask, x=4, y=-30, r=5, vx=1.5, vy=-5, spin=2, rest=0.3, bounce=0.25)]
    b = Bits(items, seed=2, T=0.8, g=1.7)
    if u > 0.3:
        draw_bits(c, b, (u - 0.3) / 0.7)
    for q in range(14):
        if u < 0.97:
            c.dotw(-9 + q * 1.8 + math.sin(q * 2 + i) * 2, -10 - u * 16 - (q % 5) * 3 + (q % 3), '#e8c040' if q % 2 else '#fff0a0')
    if u > 0.45:
        w = min(1, (u - 0.45) / 0.45)
        with c.part(GOLD_D, bevel=0.8) as p:
            p.ell(0, -0.9, 2 + 7 * w, 0.8 + 0.4 * w)


# ------------------------------------------------------------------ LLAMA SOLAR
def sol_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(x=-1.0, y=-21 + 1.8 * s, ph=t, rot=t * 0.8, ray=1.0, core=1.0, flash=0.0, beam=0.0, eye=0.5, crownup=0.0, rings=0.0)
    if a == 'walk':
        P.update(x=0, y=-21 + 2.2 * math.sin(2 * math.pi * t), rot=t * 1.6)
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(x=lerp(-1, -4, w), ray=lerp(1.0, 0.5, w), core=lerp(1.0, 1.4, w), eye=1.0, rot=t * 2.4, y=-21 - 1.5 * w, crownup=w)
    elif a == 'attack':
        P.update(x=[-4, -4, 1, 0, -1, -1][i], ray=[0.5, 0.45, 1.5, 1.2, 1.0, 1.0][i], core=[1.4, 1.5, 1.0, 1.0, 1.0, 1.0][i], eye=1.0,
                 beam=[0, 0, 1.0, 0.7, 0.2, 0][i], y=-21 - [1.5, 1.5, 0, 0.5, 0.5, 0][i], rot=0.3 + i * 0.4, crownup=[1, 1, 0.3, 0, 0, 0][i], rings=[0, 0, 1, 0.5, 0, 0][i])
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(x=-1 + rx, flash=fl, ray=0.6, core=0.8, eye=0.2, y=-21 - 2 * (1 - i))
    return P


def solar_body(c, P, nocrown=False):
    x, y = P['x'], P['y']
    ph = P['ph'] * 6.283
    rot = P['rot'] * 6.283 / 3
    ry = P['ray']
    # rayos traseros (opuestos)
    for k in range(12):
        ang = rot + k * 0.5236
        r0 = 8.5
        L = (6.5 + 2.5 * math.sin(ph * 2 + k * 1.7)) * ry * (1.3 if k % 2 == 0 else 0.8)
        a1, a2 = ang - 0.2, ang + 0.2
        with c.part(SUNR, bevel=1.0) as p:
            p.poly([(x + math.cos(a1) * r0, y + math.sin(a1) * r0), (x + math.cos(ang) * (r0 + L), y + math.sin(ang) * (r0 + L)), (x + math.cos(a2) * r0, y + math.sin(a2) * r0)])
    # aro
    with c.part(GOLD_E, bevel=1.4) as p:
        p.ell(x, y, 10.4)
        p.ell(x, y, 8.0, v=0)
    # nucleo
    with c.part(SUNC, bevel=7.5) as p:
        p.ell(x, y, 8.4 * (0.9 + 0.1 * P['core']))
    c.glow(x, y, 12, '#ffd050', 0.18 + 0.25 * P['core'])
    # rostro
    with c.part(DARK) as p:
        p.poly([(x - 0.5, y - 3.6), (x + 6.2, y - 4.2), (x + 6.0, y - 0.4), (x - 0.2, y + 0.2)])
    with c.part(Mat(ramp=['#fff8d0', '#ffffff'], emi=True, nooutline=True, bevel=0.6, dith=0.0)) as p:
        e = P['eye']
        p.poly([(x + 0.6, y - 3.0), (x + 2.8, y - 3.2), (x + 2.6, y - 1.2), (x + 0.8, y - 1.0)])
        p.poly([(x + 3.8, y - 3.4), (x + 5.8, y - 3.6), (x + 5.6, y - 1.6), (x + 4.0, y - 1.4)])
    with c.part(DARK) as p:
        p.rect(x + 1.0, y + 2.6, x + 5.0, y + 3.4)
    # corona
    if not nocrown:
        cu = P['crownup']
        base = y - 8.0
        with c.part(GOLD, line=0.5, bevel=1.4) as p:
            p.poly([(x - 6.5, base + 2.4), (x - 7.5, base - 7 - 2 * cu), (x - 4, base - 2.5), (x - 2.4, base - 9.5 - 3 * cu), (x, base - 3.2), (x + 2.4, base - 10.5 - 3 * cu),
                    (x + 4.2, base - 2.5), (x + 7.5, base - 7 - 2 * cu), (x + 6.5, base + 2.4)])
        with c.part(GOLD_E, bevel=0.5) as p:
            p.ell(x, base - 0.5, 1.0)
            p.ell(x - 4, base - 0.2, 0.7); p.ell(x + 4, base - 0.2, 0.7)
    # rayo / onda
    if P['beam'] > 0.1:
        b = P['beam']
        with c.part(GOLD_E, bevel=1.2, fade=lambda lx, ly: np.clip((lx - (x + 8)) / 6, 0, 1) * 1.0) as p:
            p.poly([(x + 8, y - 4 * b), (x + 24, y - 1), (x + 24, y + 1), (x + 8, y + 4 * b)])
        c.glow(x + 12, y, 7, '#fff0a0', 0.5 * b)
    if P['rings'] > 0.1:
        r = 12 + 6 * (1 - P['rings'])
        with c.part(GOLD_E, bevel=0.8) as p:
            p.ell(x, y, r + 0.9); p.ell(x, y, r, v=0)


def draw_solar(c, a, i, n):
    if a == 'death':
        return death_solar(c, i, n)
    P = sol_pose(a, i, n)
    solar_body(c, P)
    if P['flash']:
        c.flash(WHITE, P['flash'])


def _p_crown(c):
    with c.part(GOLD, line=0.5, bevel=1.4) as p:
        p.poly([(-6.5, 2.4), (-7.5, -7), (-4, -2.5), (-2.4, -9.5), (0, -3.2), (2.4, -10.5), (4.2, -2.5), (7.5, -7), (6.5, 2.4)])


def death_solar(c, i, n):
    if i == 0:
        solar_body(c, sol_pose('hurt', 0, 2))
        c.flash(WHITE, 0.55)
        return
    u = i / (n - 1)
    P = sol_pose('hurt', 1, 2)
    if u < 0.45:
        P['core'] = 1 + u * 2
        P['ray'] = 1 + u * 3
        P['rot'] = u * 3
        P['y'] = -21
        solar_body(c, P, nocrown=True)
        c.flash('#fff4c0', 0.2 + u * 1.2)
    else:
        v = (u - 0.45) / 0.55
        for k in range(3):
            r = 4 + (v + k * 0.22) * 22
            if r < 26:
                with c.part(GOLD_E, bevel=0.8) as p:
                    p.ell(-1, -21, r + 0.9, r * 0.9 + 0.9); p.ell(-1, -21, r, r * 0.9, v=0)
        with c.part(SUNC, bevel=4) as p:
            p.ell(-1, -21, max(0.5, 7 * (1 - v)))
    items = [dict(fn=_p_crown, x=-1, y=-29, r=4, vx=1, vy=-5, spin=2, rest=0.2, bounce=0.25)]
    b = Bits(items, seed=2, T=0.8, g=1.6)
    if u > 0.2:
        draw_bits(c, b, (u - 0.2) / 0.8)
    if u > 0.55:
        w = min(1, (u - 0.55) / 0.35)
        with c.part(SUNR, bevel=1.2) as p:
            p.ell(3, -1.2, 2 + 4 * w, 0.8 + 0.3 * w)
    for q in range(12):
        if 0.25 < u < 0.97:
            c.dotw(-1 + math.cos(q * 0.52) * (3 + u * 20), -21 + math.sin(q * 0.52) * (3 + u * 18) * 0.9 + u * 6, '#ffe070' if q % 2 else '#fff8d0')


def sheet_piglin_dorado():
    return enemy_sheet('en_piglin_dorado', (64, 64), (32, 62), (24, 50), draw_piglin, (24, 14, 8),
                       STD(6, hit=[2, 4], box=[6, -46, 30, 46], idle=6, walk=8, ifps=6, wfps=8, fa=10, death=8, dfps=8))


def sheet_espectro():
    return enemy_sheet('en_espectro', (48, 48), (24, 46), (14, 34), draw_espectro, (16, 12, 8),
                       STD(6, hit=[2, 3], box=[2, -34, 26, 32], idle=6, walk=6, wfps=10, fa=15, death=8))


def sheet_llama_solar():
    return enemy_sheet('en_llama_solar', (48, 48), (24, 46), (20, 24), draw_solar, (40, 22, 4),
                       STD(6, rel=2, muz=[14, -22], idle=6, walk=6, wfps=10, fa=14, death=8))


SHEETS = [sheet_piglin_dorado, sheet_espectro, sheet_llama_solar]
