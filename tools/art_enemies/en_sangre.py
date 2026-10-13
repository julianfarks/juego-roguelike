from common import *
from humanoid import human
from en_catacumbas import enemy_sheet, STD, DARK, WHITE

BLD = Mat(ramp=['#1c0408', '#4a0a14', '#8a1428', '#c82840', '#ff6a7c'], bevel=1.6, tex=0.2, seed=111, bias=0.5)
BLD_D = Mat(ramp=['#12030a', '#32060f', '#5e0e1c', '#8a1a2c', '#b43448'], bevel=1.6, tex=0.2, seed=112)
CRIM = Mat(ramp=['#14060c', '#34101c', '#5e1c2c', '#8a2e3c', '#b85058'], bevel=2.0, tex=0.3, seed=113)
CRIM_D = Mat(ramp=['#0c0408', '#220a12', '#3e1420', '#5c202c', '#7e3440'], bevel=2.0, tex=0.3, seed=114)
BLACKC = Mat(ramp=['#08060a', '#14101a', '#241c2c', '#382c42', '#52425e'], bevel=1.6, tex=0.25, seed=115)
BLACKC_D = Mat(ramp=['#040306', '#0c0a10', '#18121e', '#281e32'], bevel=1.6, seed=116)
PALE = Mat(ramp=['#2a1a2a', '#54384a', '#8c6070', '#c0958e', '#ecc8b4'], bevel=1.6, seed=117)
BONEC = Mat(ramp=['#2a1c24', '#5a4448', '#9a8470', '#d4c4a4', '#f6ecd0'], bevel=1.2, seed=118)
STEELC = Mat(ramp=['#1a1220', '#38304a', '#5e5878', '#8c88a8', '#c4c0dc'], bevel=1.2, tex=0.2, seed=119)
BEYE = Mat(ramp=['#c01830', '#ff4a5c', '#ffa0a8', '#ffffff'], emi=True, nooutline=True, bevel=0.8, dith=0.1)
BORB = Mat(ramp=['#6a0a1c', '#b8142c', '#ff3c52', '#ff9aa8', '#ffffff'], emi=True, nooutline=True, bevel=3.0, dith=0.25)
BDROP = Mat(ramp=['#4a0612', '#8a1226', '#c82840', '#ff5a70'], bevel=0.8, dith=0.2)
RED = '#D0203A'
LIGHTR = '#ff6a7c'
BOOTC = Mat(ramp=['#08060a', '#161018', '#2a1e28', '#403040'], bevel=1.2, seed=3)
BOOTC_D = Mat(ramp=['#050407', '#0e0a10', '#1c1420', '#2e2030'], bevel=1.2, seed=4)
TRAIL_R = Mat(ramp=['#7a1428', '#d02a44', '#ff7a8a', '#ffe8ec'], emi=True, nooutline=True, bevel=1.5, dith=0.2)


# ------------------------------------------------------------------ VINDICADOR
def vin_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(hx=-4.0, dy=0.6 * s, lean=0.08, ph=t, walk=False, stride=0, lift=0, grip=(2, -17), axa=-1.0, head=0.0, flash=0.0, glow=0.0, trail=None, brow=0.0, k=None)
    if a == 'idle':
        P['grip'] = (2.5, -16 + 0.5 * s); P['axa'] = -1.05 + 0.04 * s
    elif a == 'walk':
        P.update(walk=True, stride=5.3, lift=3.0, dy=-1.0 * abs(math.sin(2 * math.pi * t)) + 0.5, lean=0.2, hx=-3)
        P['grip'] = (2, -16 + 0.8 * s); P['axa'] = -0.95 + 0.08 * s
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(lean=lerp(0.08, -0.3, w), hx=lerp(-4, -8, w), dy=lerp(0, 2.4, w), glow=w, head=-0.15 * w, brow=w)
        P['grip'] = (lerp(2.5, -5, w), lerp(-16, -21, w)); P['axa'] = lerp(-1.05, -2.35, w)
        P['feet'] = (lerp(-3.5, -6.5, w), 0), (lerp(3.5, 5, w), 0)
    elif a == 'attack':
        k = i / (n - 1)
        P['lean'] = kf(k, [(0, -0.3), (0.2, 0.2), (0.4, 0.5), (0.7, 0.4), (1, 0.12)])
        P['hx'] = kf(k, [(0, -8), (0.2, -2), (0.4, 3.5), (0.7, 3), (1, -1)])
        P['dy'] = kf(k, [(0, 2.4), (0.4, 3.5), (1, 0)])
        P['grip'] = (kf(k, [(0, -5), (0.2, 2), (0.4, 8), (0.7, 7.5), (1, 3)]), kf(k, [(0, -21), (0.2, -20), (0.4, -13), (0.7, -12), (1, -14)]))
        P['axa'] = kf(k, [(0, -2.35), (0.2, -1.6), (0.4, 0.55), (0.7, 0.8), (1, 0.0)])
        P['glow'] = 1.0 if k < 0.8 else 0.2
        P['head'] = kf(k, [(0, -0.15), (0.4, 0.3), (1, 0.1)])
        P['trail'] = k if 0.15 < k < 0.75 else None
        P['feet'] = (-6.5, 0), (kf(k, [(0, 5), (0.4, 8), (1, 5)]), 0)
        P['brow'] = 1.0
        P['k'] = k
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(hx=-4 + rx, lean=ln, flash=fl, head=-0.3 if i == 0 else -0.1, brow=1.0)
        P['grip'] = (-1, -14) if i == 0 else (1.5, -15); P['axa'] = -0.2 if i == 0 else -0.8
    return P


M_VIN = dict(skin=PALE, cloth=CRIM, cloth_d=CRIM_D, boot=BOOTC, boot_d=BOOTC_D, vest=BLACKC, vest_d=BLACKC_D)


def vin_head(c, x, y, ang, P):
    with c.at(x, y, ang):
        with c.part(PALE, line=0.5, bevel=1.8) as p:
            p.ell(0, 0, 4.0, 4.4)
            p.poly([(2.6, -0.4), (6.4, 2.4), (5.4, 3.4), (2.4, 2.4)])           # nariz enorme
            p.poly([(-1, 3), (3.4, 3.2), (2.6, 5.8), (0, 5.4)])
        with c.part(BLACKC, bevel=0.6) as p:
            p.poly([(0.0, -2.4), (5.2, -1.6 - P['brow'] * 0.4), (5.0, -0.2), (0.2, -1.0)])      # ceja
            p.poly([(0.6, 3.4), (3.4, 3.5), (3.2, 4.2), (0.6, 4.1)])
        with c.part(BEYE) as p:
            p.ell(3.0, -0.4, 0.8, 0.7)
        c.glow(3.0, -0.4, 2.6, RED, 0.3 + 0.4 * P['glow'])
        with c.part(BONEC, bevel=0.6) as p:       # cicatriz / dientes
            p.rect(1.0, 3.5, 1.9, 4.1)
        with c.part(CRIM_D, line=0.5, bevel=1.6) as p:    # capucha corta
            p.poly([(-5, 4), (-6, -2), (-3, -5.2), (0.5, -5.4), (-0.5, -2.8), (-2.6, 0.5), (-2.8, 4.6)])


def vin_back(c, hip, neck, sho, lean, ph):
    sw = math.sin(ph * 6.283)
    with c.part(CRIM_D, line=0.5, bevel=2.2) as p:
        p.poly([(neck[0] - 3, neck[1]), (neck[0] + 2, neck[1] - 1), (hip[0] + 4, hip[1] + 4), (hip[0] + 2, hip[1] + 11 + sw), (hip[0] - 3, hip[1] + 8), (hip[0] - 9 - lean * 4 + sw * 0.8, hip[1] + 10),
                (hip[0] - 8, hip[1] + 4), (neck[0] - 7, neck[1] + 3)])


def vin_weapon(c, P, rear, front):
    ax = P['axa']
    d = (math.cos(ax), math.sin(ax)); nr = (-d[1], d[0])
    g = (P['grip'][0] + P['hx'], P['grip'][1] + P['dy'])
    base = (g[0] - d[0] * 4, g[1] - d[1] * 4)
    tip = (g[0] + d[0] * 15, g[1] + d[1] * 15)
    with c.part(BONEC if False else Mat(ramp=['#140c0e', '#2a1c1c', '#46322a', '#684a38'], bevel=0.8, tex=0.3, seed=9), line=0.4, bevel=0.8) as p:
        p.limb(base, tip, 1.0)
    # cabeza del hacha
    hc = (tip[0] - d[0] * 1.5, tip[1] - d[1] * 1.5)
    with c.part(STEELC, line=0.5, bevel=1.6) as p:
        p.poly([(hc[0] - d[0] * 4 + nr[0] * 1.6, hc[1] - d[1] * 4 + nr[1] * 1.6), (hc[0] + d[0] * 3 + nr[0] * 1.4, hc[1] + d[1] * 3 + nr[1] * 1.4),
                (hc[0] + d[0] * 5.5 + nr[0] * 8.5, hc[1] + d[1] * 5.5 + nr[1] * 8.5), (hc[0] - d[0] * 5.5 + nr[0] * 8.0, hc[1] - d[1] * 5.5 + nr[1] * 8.0)])
    with c.part(BLD, bevel=0.8) as p:                  # filo ensangrentado
        p.poly([(hc[0] - d[0] * 5.5 + nr[0] * 8.0, hc[1] - d[1] * 5.5 + nr[1] * 8.0), (hc[0] + d[0] * 5.5 + nr[0] * 8.5, hc[1] + d[1] * 5.5 + nr[1] * 8.5),
                (hc[0] + d[0] * 5.0 + nr[0] * 6.8, hc[1] + d[1] * 5.0 + nr[1] * 6.8), (hc[0] - d[0] * 5.0 + nr[0] * 6.4, hc[1] - d[1] * 5.0 + nr[1] * 6.4)])
    with c.part(STEELC, bevel=0.8) as p:
        p.poly([(hc[0] + nr[0] * 0.5 - d[0] * 0.5, hc[1] + nr[1] * 0.5), (hc[0] - nr[0] * 3 + d[0] * 1.5, hc[1] - nr[1] * 3 + d[1] * 1.5), (hc[0] - nr[0] * 2 - d[0] * 2, hc[1] - nr[1] * 2 - d[1] * 2)])
    if P['glow'] > 0.1:
        c.glow(hc[0] + nr[0] * 7, hc[1] + nr[1] * 7, 6, RED, 0.3 + 0.6 * P['glow'])
    if P['trail'] is not None:
        k = P['trail']
        sh = (P['hx'] + 1, -22 + P['dy'])
        an = math.atan2(hc[1] + nr[1] * 6 - sh[1], hc[0] + nr[0] * 6 - sh[0])
        rr = math.hypot(hc[0] + nr[0] * 6 - sh[0], hc[1] + nr[1] * 6 - sh[1])
        arc_trail(c, sh[0], sh[1], rr - 9, rr + 3, an - 1.6, an + 0.1, TRAIL_R)


def vin_torso(c, P):
    with c.part(BLACKC_D, line=0.4, bevel=1.0) as p:
        p.poly([(-5, 0.2), (5, -0.2), (5, 1.8), (-5, 2.2)])
    with c.part(Mat(ramp=['#6a4a10', '#b08a20', '#e8c040'], bevel=0.5, dith=0.0)) as p:
        p.rect(-0.8, -0.2, 1.0, 2.0)
    with c.part(CRIM, line=0.3, bevel=1.4) as p:       # faja carmesi
        p.poly([(-4.4, -9.5), (4.6, -11.8), (5, -9), (-4.6, -6.8)])
    with c.part(STEELC, line=0.4, bevel=1.2) as p:      # hombrera
        p.ell(0.6, -11.5, 4.2, 2.4)


def draw_vindicador(c, a, i, n):
    if a == 'death':
        return death_vindicador(c, i, n)
    P = vin_pose(a, i, n)
    human(c, P, a, M_VIN, vin_head, vin_weapon, back_fn=vin_back, torso_extra=vin_torso,
          front_cb=None)
    if P['flash']:
        c.flash(WHITE, P['flash'])
    if a == 'windup' and i == n - 1:
        c.flash(RED, 0.08)


def _p_axe(c):
    with c.part(Mat(ramp=['#140c0e', '#2a1c1c', '#46322a', '#684a38'], bevel=0.8, tex=0.3, seed=9), line=0.4, bevel=0.8) as p:
        p.limb((-9, 0), (9, 0), 1.0)
    with c.part(STEELC, line=0.5, bevel=1.6) as p:
        p.poly([(5, -1.4), (8, -1.6), (9.5, -9.5), (3.5, -8.5)])
    with c.part(BLD, bevel=0.8) as p:
        p.poly([(3.5, -8.5), (9.5, -9.5), (9, -7.8), (3.8, -7)])


def death_vindicador(c, i, n):
    if i == 0:
        human(c, vin_pose('hurt', 0, 2), 'hurt', M_VIN, vin_head, vin_weapon, back_fn=vin_back, torso_extra=vin_torso)
        c.flash(WHITE, 0.45)
        return
    u = i / (n - 1)
    P = vin_pose('hurt', 1, 2)
    P['glow'] = 0
    P['grip'] = (kf(u, [(0, 1), (1, 6)]), kf(u, [(0, -14), (1, -9)]))
    P['axa'] = 3.0
    ang = kf(u, [(0, 0), (0.3, -0.45), (0.65, -1.2), (1.0, -1.57)])
    P['head'] = kf(u, [(0, -0.1), (1, 0.15)])
    P['lean'] = -0.1
    P['hx'] = 0
    P['feet'] = (kf(u, [(0, -3), (1, -6)]), 0), (kf(u, [(0, 3), (1, 5)]), 0)
    with c.at(2 + 4 * u, 0, ang):
        human(c, P, 'idle', M_VIN, vin_head, lambda cc, PP, r, f: None, back_fn=vin_back, torso_extra=vin_torso)
    items = [dict(fn=_p_axe, x=9, y=-22, r=4, vx=7, vy=-7, spin=6, rest=0.25, bounce=0.35)]
    for d_ in items:
        d_['vx'] *= 0.6; d_['vy'] *= 0.7
    b = Bits(items, seed=3, T=0.75, g=1.6)
    draw_bits(c, b, u)
    if u > 0.45:
        w = min(1, (u - 0.45) / 0.45)
        with c.part(BDROP, bevel=0.8) as p:
            p.ell(-8, -0.9, 3 + 9 * w, 0.8 + 0.4 * w)
        for q in range(4):
            if u < 0.9:
                c.dotw(-14 + q * 4, -4 - (u - 0.4) * 6 - (q % 2) * 2, '#c82840')


# ------------------------------------------------------------------ BRUJA DE SANGRE
def bs_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(x=-2.0, y=-5.5 + 1.4 * s, ph=t, lean=0.0, orb=0.55, orbx=0.0, arm2=0.0, flash=0.0, eye=0.6, charge=0.0, hair=s, tilt=0.0, drop=0.0)
    if a == 'walk':
        P.update(x=-1, lean=0.12, y=-5.5 + 1.6 * math.sin(2 * math.pi * t))
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(lean=lerp(0, -0.14, w), x=lerp(-2, -4, w), orb=lerp(0.55, 1.4, w), arm2=w, eye=1.0, charge=w, y=-5.5 - 1.6 * w, tilt=-0.1 * w)
    elif a == 'attack':
        P.update(lean=[-0.14, -0.16, 0.22, 0.12, 0.04, 0.0][i], x=[-4, -4, 0, -1, -2, -2][i], orb=[1.5, 1.6, 0.0, 0.0, 0.0, 0.0][i],
                 orbx=[0, 0, 0, 0, 0, 0][i], arm2=[1, 1, 0.2, 0, 0, 0][i], eye=1.0, charge=[1, 1, 0.5, 0, 0, 0][i], y=-5.5 - [1.6, 1.6, 0, 0.5, 0.5, 0][i],
                 tilt=[-0.1, -0.1, 0.12, 0.05, 0, 0][i])
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(x=-2 + rx, lean=ln, flash=fl, eye=0.2, tilt=-0.35 if i == 0 else -0.12, arm2=0.5)
    return P


def bruja_s_body(c, P, deflate=0.0, nohead=False, noorb=False):
    x, y, lean, ph = P['x'], P['y'], P['lean'], P['ph'] * 6.283
    cx_, cy_ = x, y - 15 * (1 - deflate * 0.8)
    sw = math.sin(ph)
    # pelo largo detras
    hp = []
    hy0 = cy_ - 10
    for k in range(7):
        u = k / 6
        hp.append((cx_ - 2 - u * 8 + math.sin(ph + u * 3) * 2.2 * u - lean * 4 * u, hy0 + 2 + u * 15 * (1 - deflate * 0.7)))
    if not nohead:
        with c.part(BLACKC_D, line=0.4, bevel=2.0) as p:
            p.tube(hp, 3.0, 1.0)
    # cuello alto (abanico)
    with c.part(BLACKC, line=0.5, bevel=1.6) as p:
        p.poly([(cx_ - 1, cy_ - 8), (cx_ - 7, cy_ - 17), (cx_ - 4, cy_ - 20), (cx_ + 0.5, cy_ - 14), (cx_ + 2, cy_ - 8)])
    with c.part(BONEC, bevel=0.5) as p:
        p.limb((cx_ - 6.5, cy_ - 17), (cx_ - 3.8, cy_ - 19.4), 0.5)
    # vestido: campana
    hem = []
    hw = 11.5
    for k in range(7):
        u = k / 6
        hem.append((cx_ - hw + u * 2 * hw + 0.6 * math.sin(ph + k) - lean * 3, y + 0.5 - (2.2 if k % 2 else 0) + 0.7 * math.sin(ph * 2 + k * 1.3)))
    top = cy_ - 8
    with c.part(CRIM, line=0.5, bevel=3.2) as p:
        p.poly([(cx_ - 3, top), (cx_ + 3.2, top), (cx_ + 4.6, cy_ + 0.5)] + hem[::-1] + [(cx_ - 4.8, cy_ + 0.5)])
    with c.part(CRIM_D, bevel=1.4) as p:
        p.poly([(cx_ - 1, cy_ + 1), (cx_ + 1.5, cy_ + 1), (hem[4][0], hem[4][1] - 1), (hem[2][0], hem[2][1] - 1)])
    with c.part(BLACKC, bevel=1.4) as p:        # corsé
        p.poly([(cx_ - 3.4, top), (cx_ + 3.6, top), (cx_ + 3.2, cy_ + 0.6), (cx_ - 3.4, cy_ + 0.8)])
    with c.part(BONEC, bevel=0.6) as p:
        for k in range(3):
            p.limb((cx_ - 3, top + 2 + k * 2.6), (cx_ + 3, top + 2 + k * 2.6), 0.35)
    with c.part(BLD, bevel=0.8) as p:
        for (hx_, hy_) in hem[1::2]:
            p.ell(hx_, hy_ - 0.4, 2.0, 1.2)
    # brazo lejano (garras)
    sh = (cx_ + 1.5, top + 1.5)
    ar = P['arm2']
    h2 = (cx_ + 6 + 5 * ar, top + 8 - 9 * ar)
    e2 = ik2(sh, h2, 5.4, 5.4, bend=1)
    with c.part(CRIM_D, line=0.4, bevel=1.4) as p:
        p.limb(sh, e2, 1.8, 1.5); p.limb(e2, h2, 1.5, 1.2)
    with c.part(PALE, bevel=0.6) as p:
        p.ell(h2[0], h2[1], 1.2)
        for q in (-1, 0, 1):
            p.limb(h2, (h2[0] + 2.8, h2[1] + q * 1.2 - 1.0 * ar), 0.4, 0.15)
    # cabeza
    if not nohead:
        with c.at(cx_ + 2.2 + 2 * lean, cy_ - 12.2, lean * 0.6 + P['tilt']):
            with c.part(PALE, line=0.5, bevel=1.8) as p:
                p.ell(0, 0, 3.8, 4.4)
            with c.part(BEYE) as p:
                e = P['eye']
                p.poly([(0.8, -0.8), (3.4, -1.0), (3.2, 0.2), (1.0, 0.3)])
            c.glow(2.4, -0.4, 3.0, RED, 0.35 + 0.5 * P['eye'])
            with c.part(CRIM_D, line=0.0, bevel=1.0, fade=lambda lx, ly: 0.82) as p:       # velo
                p.poly([(-3.4, 1.2), (4.2, 0.9), (4.0, 5.6), (-2.2, 6.8), (-4.4, 4)])
            with c.part(BLACKC_D, line=0.5, bevel=1.8) as p:           # pelo frontal
                p.poly([(-4.4, 4.6), (-5.2, -2.5), (-2.5, -5.6), (1.8, -5.4), (4.2, -3.2), (1.2, -3.4), (-1.2, -2), (-2.4, 1.4), (-2.8, 5.6)])
            with c.part(BONEC, bevel=0.8, line=0.3) as p:             # corona de espinas
                p.poly([(-3.6, -4.6), (-6.2, -9.4), (-1.2, -5.4)])
                p.poly([(-0.6, -5.8), (-0.4, -11.5), (1.6, -5.6)])
                p.poly([(2.2, -5.2), (5.4, -9.6), (3.8, -4.4)])
            with c.part(BLD, bevel=0.5) as p:
                p.ell(1.0, -5.2, 0.9, 0.8)
    # brazo cercano + orbe
    if not noorb:
        hn = (cx_ + 8.5 + P['orbx'], top + 8.5 - 3.5 * P['charge'])
        en = ik2(sh, hn, 5.2, 5.4, bend=1)
        with c.part(CRIM, line=0.4, bevel=1.4) as p:
            p.limb(sh, en, 1.9, 1.6); p.limb(en, hn, 1.6, 1.3)
        with c.part(PALE, bevel=0.6) as p:
            p.ell(hn[0], hn[1], 1.3)
            for q in (-1, 0, 1):
                p.limb(hn, (hn[0] + 2.4, hn[1] + q * 1.3 - 1.2), 0.4, 0.15)
        r = P['orb']
        if r > 0.05:
            ox, oy = hn[0] + 3.4 + r * 1.2, hn[1] - 4.2 - r * 1.2
            with c.part(BORB, bevel=3.0) as p:
                p.ell(ox, oy, 2.4 + 2.4 * r)
            with c.part(BLD, bevel=1.2) as p:
                p.ell(ox + 0.5, oy + 0.6, (2.4 + 2.4 * r) * 0.45)
            c.glow(ox, oy, 5 + 3 * r, RED, 0.4)
            for q in range(5):
                ang = q * 1.26 + ph * 2
                c.dotw(ox + math.cos(ang) * (4.2 + 2 * r), oy + math.sin(ang) * (4.2 + 2 * r), LIGHTR)


def draw_bruja_s(c, a, i, n):
    if a == 'death':
        return death_bruja_s(c, i, n)
    P = bs_pose(a, i, n)
    bruja_s_body(c, P)
    if P['flash']:
        c.flash(WHITE, P['flash'])


def _p_crown(c):
    with c.part(BONEC, bevel=0.8, line=0.3) as p:
        p.poly([(-3.6, 0), (-6.2, -5), (-1.2, -0.8)]); p.poly([(-0.6, -1.2), (-0.4, -7), (1.6, -1)]); p.poly([(2.2, -0.6), (5.4, -5), (3.8, 0.2)])
        p.rect(-3.8, -0.2, 4, 1.3)


def _p_veil(c):
    with c.part(CRIM_D, bevel=1.0) as p:
        p.poly([(-4, 0), (4, -0.5), (3, 3.5), (-3, 4)])


def death_bruja_s(c, i, n):
    if i == 0:
        bruja_s_body(c, bs_pose('hurt', 0, 2))
        c.flash(WHITE, 0.5)
        return
    u = i / (n - 1)
    P = bs_pose('hurt', 1, 2)
    P['y'] = -5.5 + 4.5 * sm(u * 1.4)
    de = sm(u * 1.15)
    if u < 0.85:
        bruja_s_body(c, P, deflate=de, nohead=(u > 0.3), noorb=True)
    else:
        bruja_s_body(c, P, deflate=1.0, nohead=True, noorb=True)
    # orbe estalla
    if u < 0.5:
        ox, oy = 9, -22
        r = 4.8 + u * 12
        with c.part(BORB, bevel=3.0) as p:
            p.ell(ox, oy, r)
        c.flash(RED, 0.2)
    else:
        v = (u - 0.5) / 0.5
        for q in range(10):
            ang = q * 0.63 + 0.3
            r0 = 4 + v * 14
            fx, fy = 9 + math.cos(ang) * r0 * 1.2, -22 + math.sin(ang) * r0 + v * 8 * v
            if fy < -1.5:
                with c.part(BDROP, bevel=0.8) as p:
                    p.ell(fx, fy, 1.8 * (1 - v * 0.5), 1.8 * (1 - v * 0.5))
    items = [dict(fn=_p_crown, x=3, y=-28, r=3, vx=3, vy=-8, spin=3, rest=0.3, bounce=0.25),
             dict(fn=_p_veil, x=4, y=-24, r=2, vx=5, vy=-4, spin=2, rest=0.1, bounce=0.1)]
    for d_ in items:
        d_['vx'] *= 0.6; d_['vy'] *= 0.7
    b = Bits(items, seed=3, T=0.8, g=1.5)
    draw_bits(c, b, u)
    if u > 0.4:
        w = min(1, (u - 0.4) / 0.5)
        with c.part(BDROP, bevel=0.8) as p:
            p.ell(4, -0.9, 3 + 10 * w, 0.8 + 0.5 * w)


# ------------------------------------------------------------------ MURCIELAGO
BATF = Mat(ramp=['#12060a', '#2c0e14', '#4e1a22', '#7a2c34', '#a84a50'], bevel=2.4, tex=0.35, ts=1.2, seed=121, bias=0.5)
BATM = Mat(ramp=['#240812', '#4e0f20', '#7e1a30', '#a82a44', '#d44c62'], bevel=1.4, dith=0.5, outcol='#1c050c')
BATM_B = Mat(ramp=['#180610', '#380c18', '#5a1424', '#80203a'], bevel=1.4, dith=0.5, outcol='#120409')
BATBONE = Mat(ramp=['#2c1418', '#5a343a', '#8c5e5c', '#c09a8a'], bevel=0.8, dith=0.2)


def mur_pose(a, i, n):
    t = i / n
    P = dict(x=5.0, y=-22 + 1.2 * math.sin(2 * math.pi * t), w=math.sin(2 * math.pi * t), pitch=0.0, ph=t, mouth=0.0, claw=0.0, flash=0.0, fold=0.0, eye=0.5, hang=0.0)
    if a == 'walk':
        P.update(w=math.sin(2 * math.pi * t * 1), y=-22 + 2.5 * math.sin(2 * math.pi * t + 1.57), pitch=0.15, x=6)
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(w=lerp(0.2, 1.0, w) + 0.1 * math.sin(i * 4), pitch=lerp(0, -0.5, w), y=-22 - 5 * w, x=lerp(5, 1, w), mouth=3 * w, eye=1.0)
    elif a == 'attack':
        P.update(w=[1.0, -1.0, -0.6, -0.2, 0.3, 0.7][i], pitch=[-0.5, 0.5, 0.8, 0.6, 0.25, 0.1][i], y=-22 + [-3, 3, 6, 5, 2, 0][i], x=[1, 6, 9, 8, 6, 5][i],
                 mouth=[3, 4, 4, 3, 1, 0][i], claw=[0, 1, 1, 1, 0.4, 0][i], eye=1.0)
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(x=5 + rx, pitch=-0.4 if i == 0 else -0.15, flash=fl, w=-1.0 if i == 0 else 0.3, mouth=3, eye=0.9)
    return P


def bat_wing(c, S, wang, L1, L2, mem, bone, sweep):
    W = (S[0] + L1 * math.cos(wang), S[1] + L1 * math.sin(wang))
    tips = []
    for off in (-0.35, 0.35, 0.95):
        ang = wang + sweep + off
        tips.append((W[0] + L2 * math.cos(ang) * (1.0 if off < 0.9 else 0.8), W[1] + L2 * math.sin(ang) * (1.0 if off < 0.9 else 0.8)))
    lowp = (S[0] - 1, S[1] + 8)
    # festoneado
    pts = [S, W, tips[0]]
    for k in range(3):
        a_, b_ = tips[k], tips[min(k + 1, 2)] if k < 2 else lowp
        if k < 2:
            mid = ((tips[k][0] + tips[k + 1][0]) / 2, (tips[k][1] + tips[k + 1][1]) / 2)
            mid = (lerp(mid[0], W[0], 0.30), lerp(mid[1], W[1], 0.30))
            pts += [mid, tips[k + 1]]
    mid = ((tips[2][0] + lowp[0]) / 2, (tips[2][1] + lowp[1]) / 2)
    pts += [(lerp(mid[0], W[0] * 0.5 + S[0] * 0.5, 0.35), lerp(mid[1], W[1] * 0.3 + S[1] * 0.7, 0.35)), lowp]
    with c.part(mem, line=0.0, bevel=1.6) as p:
        p.poly(pts)
    with c.part(bone, bevel=0.5) as p:
        p.tube([S, W], 1.0, 0.7)
        for t_ in tips:
            p.tube([W, t_], 0.7, 0.25)
    return W, tips


def murc_body(c, P, a='idle', wings=True):
    x, y, pit = P['x'], P['y'], P['pitch']
    w = P['w']
    fold = P['fold']
    with c.at(x, y, pit):
        S = (-1.5, -3)
        if wings:
            wa_far = -3.0 + 1.1 * w * (1 - fold) + 3.0 * fold
            bat_wing(c, (S[0] + 1.5, S[1] + 0.5), wa_far, 13 * (1 - 0.3 * fold), 14 * (1 - 0.4 * fold), BATM_B, BATBONE, 0.7 * (1 - fold) + 0.2)
        # cuerpo peludo
        with c.part(BATF, line=0.5, bevel=3.0) as p:
            p.ell(0, 0, 5.2, 6.2)
            p.ell(-0.5, 4, 3.4, 3.0)
        with c.part(BATM, bevel=0.8) as p:
            p.ell(2, 2.4, 2.0, 3.0)
        # patas con garras
        cl = P['claw']
        for dx_ in (-1.5, 1.8):
            with c.part(BATF, bevel=0.8) as p:
                p.limb((dx_, 5.5), (dx_ + 2.5 + 4 * cl, 8.5 + 2 * cl - 2 * cl), 1.0, 0.7)
            with c.part(BATBONE, bevel=0.4) as p:
                for q in (-1, 0, 1):
                    p.limb((dx_ + 2.5 + 4 * cl, 8.5), (dx_ + 4.4 + 5 * cl, 9.2 + q * 0.9 + 0.5 * cl), 0.4, 0.15)
        # cabeza
        with c.at(5.2, -5.5, -pit * 0.4):
            with c.part(BATF, line=0.5, bevel=2.2) as p:
                p.ell(0, 0, 4.4, 4.0)
                p.poly([(1.5, -1.5), (6, 0.5), (5.5, 2.6), (1, 2.8)])
                p.poly([(-2.6, -2.5), (-3.6, -8.5), (0.2, -3.6)])
                p.poly([(0.8, -3.4), (2.6, -9), (3.6, -2.6)])
            with c.part(BATM, bevel=0.6) as p:
                p.poly([(-2.3, -3), (-3, -6.8), (-0.2, -3.6)])
            with c.part(DARK) as p:
                p.poly([(2.0, 1.6), (6.2, 2.0), (6, 2.6 + P['mouth'] * 0.9), (2.4, 3.0 + P['mouth'] * 0.7)])
            with c.part(BEYE) as p:
                p.ell(3.0, -0.6, 0.9 + 0.2 * P['eye'], 0.8 + 0.2 * P['eye'])
                p.ell(0.3, -0.7, 0.7, 0.6)
            c.glow(3, -0.6, 3.2, RED, 0.35 + 0.45 * P['eye'])
            with c.part(BONEC, bevel=0.4) as p:
                p.poly([(2.8, 2.2), (3.4, 2.2), (3.1, 3.8 + P['mouth'] * 0.5)])
                p.poly([(5.0, 2.2), (5.6, 2.3), (5.2, 3.9 + P['mouth'] * 0.5)])
        if wings:
            wa = -2.75 + 1.25 * w * (1 - fold) + 2.8 * fold
            bat_wing(c, S, wa, 14 * (1 - 0.3 * fold), 15 * (1 - 0.4 * fold), BATM, BATBONE, 0.7 * (1 - fold) + 0.2)


def draw_murcielago(c, a, i, n):
    if a == 'death':
        return death_murcielago(c, i, n)
    P = mur_pose(a, i, n)
    murc_body(c, P, a)
    if P['flash']:
        c.flash(WHITE, P['flash'])


def death_murcielago(c, i, n):
    if i == 0:
        murc_body(c, mur_pose('hurt', 0, 2))
        c.flash(WHITE, 0.5)
        return
    u = i / (n - 1)
    P = mur_pose('hurt', 1, 2)
    P['fold'] = sm(u * 1.5)
    P['w'] = 0
    P['pitch'] = kf(u, [(0, -0.2), (0.5, 1.2), (1, 2.6)])
    cy = kf(u, [(0, -22), (0.45, -26), (0.8, -12), (1, -7.5)])
    P['x'] = kf(u, [(0, 5), (1, 0)])
    P['y'] = cy
    P['mouth'] = 3
    P['eye'] = 1 - u
    murc_body(c, P)
    if u > 0.75:
        w = min(1, (u - 0.75) / 0.25)
        with c.part(BDROP, bevel=0.8) as p:
            p.ell(-3, -0.9, 2 + 6 * w, 0.7 + 0.3 * w)
    for q in range(6):
        if u < 0.9:
            c.dotw(-6 + q * 3, -10 - u * 6 - (q % 3) * 3 + u * 10 * (q % 2), '#c82840')


def sheet_vindicador():
    return enemy_sheet('en_vindicador', (48, 48), (24, 46), (12, 30), draw_vindicador, (20, 8, 14),
                       STD(6, hit=[2, 3], box=[4, -34, 24, 34], fa=15))


def sheet_bruja_sangre():
    return enemy_sheet('en_bruja_sangre', (48, 48), (24, 46), (14, 34), draw_bruja_s, (22, 6, 14),
                       STD(6, rel=3, muz=[16, -26], walk=6, wfps=9, fa=13))


def sheet_murcielago():
    return enemy_sheet('en_murcielago', (48, 48), (24, 46), (16, 18), draw_murcielago, (24, 8, 12),
                       STD(6, hit=[1, 3], box=[2, -28, 24, 26], idle=6, walk=6, wfps=14, fa=16, death=8))


SHEETS = [sheet_vindicador, sheet_bruja_sangre, sheet_murcielago]
