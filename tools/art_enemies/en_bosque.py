from common import *
from en_catacumbas import enemy_sheet, STD, DARK, WHITE

MOSS = Mat(ramp=['#0c1c10', '#1c3c1c', '#386a24', '#68a032', '#a8d058'], bevel=1.4, tex=0.5, ts=1.4, seed=71)
WOOD = Mat(ramp=['#120a0e', '#2a1a1a', '#4a2e22', '#74482e', '#a47844'], bevel=2.4, tex=0.35, ts=0.8, seed=72, bias=0.4)
WOOD_B = Mat(ramp=['#0c0608', '#1e1214', '#38221c', '#5a3824', '#80562e'], bevel=2.2, tex=0.35, seed=73)
BARK_L = Mat(ramp=['#201414', '#3c2a24', '#5c4434', '#84644a'], bevel=0.8, tex=0.4, seed=74)
SHROOM = Mat(ramp=['#8a3a06', '#d87a14', '#ffc040', '#fff0a0'], bevel=1.6, dith=0.4, outcol='#4a1a08')
SHROOM_E = Mat(ramp=['#d87a14', '#ffc040', '#fff0a0', '#ffffff'], emi=True, nooutline=True, bevel=1.0, dith=0.2)
AMBER = '#FFC24A'
AMBEYE = Mat(ramp=['#d87a14', '#ffc24a', '#fff0a0', '#ffffff'], emi=True, nooutline=True, bevel=0.8, dith=0.1)
SPID = Mat(ramp=['#0a0e08', '#1a2410', '#2e4018', '#4c6a24', '#7a9c34'], bevel=2.4, tex=0.2, seed=75, bias=0.5)
SPID_L = Mat(ramp=['#060804', '#121a0c', '#223014', '#3a5420', '#628634'], bevel=1.4, tex=0.2, seed=77)
SPID_B = Mat(ramp=['#060804', '#10160a', '#1e2a10', '#324a18', '#4e6c24'], bevel=1.6, tex=0.2, seed=76)
SPOT = Mat(ramp=['#a04a08', '#e0901c', '#ffc84a', '#fff2a8'], bevel=1.0, dith=0.2)
VENOM = Mat(ramp=['#2a7a10', '#58c820', '#a8f050', '#e8ffa0'], emi=True, nooutline=True, bevel=0.8, dith=0.2)
WSKIN = Mat(ramp=['#10281c', '#1e4c30', '#388450', '#68b868', '#a0dc88'], bevel=1.4, tex=0.2, seed=77)
WROBE = Mat(ramp=['#0c1410', '#1a2a20', '#2e4634', '#486a4c', '#6e946c'], bevel=2.2, tex=0.3, seed=78)
WROBE_D = Mat(ramp=['#080c0a', '#121c16', '#203228', '#32503a'], bevel=1.4, tex=0.2, seed=79)
HATP = Mat(ramp=['#0e0818', '#221438', '#3c2860', '#5c4488', '#8468b0'], bevel=1.8, tex=0.2, seed=80)
GOLDB = Mat(ramp=['#6a4a10', '#b08a20', '#e8c040', '#fff0a0'], bevel=0.8, dith=0.2)
POT = Mat(ramp=['#0c0e12', '#1c2028', '#343a48', '#545e72', '#7c88a0'], bevel=2.0, tex=0.2, seed=81)
POTION = Mat(ramp=['#1c7a18', '#48d030', '#a0f860', '#f0ffb0'], emi=True, nooutline=True, bevel=2.0, dith=0.25)
GLASS = Mat(ramp=['#2a5a48', '#58a888', '#a8e8d0', '#f0fff8'], bevel=1.0, dith=0.3, outcol='#103a28')
GREEN = '#9af050'


# ------------------------------------------------------------------ ARANA
def ara_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(hx=0.0, dy=0.4 * s, ph=t, walk=False, stride=0.0, lift=0.0, rear=0.0, eye=0.3, fang=0.0, flash=0.0, bite=0.0, tilt=0.0, abd=0.0)
    if a == 'walk':
        P.update(walk=True, stride=3.6, lift=3.2, dy=-0.6 * abs(math.sin(4 * math.pi * t)) + 0.4, tilt=0.1)
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(rear=w, eye=w, fang=w * 2.0, hx=lerp(0, -4, w), dy=lerp(0, -1.0, w), tilt=-0.35 * w, abd=0.3 * w)
    elif a == 'attack':
        k = i / (n - 1)
        P.update(rear=kf(k, [(0, 1.0), (0.2, 0.2), (0.4, -0.2), (1, 0)]), hx=kf(k, [(0, -4), (0.2, 3), (0.4, 9), (0.7, 7), (1, 2)]),
                 dy=kf(k, [(0, -1), (0.2, -4), (0.4, 0), (1, 0)]), tilt=kf(k, [(0, -0.35), (0.2, 0.1), (0.4, 0.25), (1, 0.05)]),
                 eye=1.0, fang=kf(k, [(0, 2), (0.4, 3), (1, 1)]), bite=1.0 if 0.2 < k < 0.7 else 0.0, abd=-0.15)
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(hx=rx, tilt=ln * 0.8, flash=fl, fang=3, eye=0.8, rear=0.5 if i == 0 else 0.1)
    return P


def spider_leg(c, hip, foot, m, thick=1.6):
    d = math.hypot(foot[0] - hip[0], foot[1] - hip[1])
    kn = ik2(hip, foot, 10.5, 12.0, bend=-1)
    with c.part(m, line=0.4, bevel=1.2) as p:
        p.limb(hip, kn, thick, thick * 0.8)
        p.limb(kn, foot, thick * 0.8, 0.5)
    return kn


def arana_body(c, P, a, curl=0.0):
    hx, dy, ph = P['hx'], P['dy'], P['ph']
    rear = P['rear']
    ct = (hx + 4, -14 + dy)       # cefalotorax
    anchors = [-1.5, 0.5, 2.5, 4.5]
    rest = [-14.0, -7.0, 5.0, 13.0]
    # patas lejanas
    for k in range(4):
        ho = (ct[0] + anchors[k] - 0.5, ct[1] + 0.5)
        if P['walk']:
            g = gait((ph + (0.5 if k % 2 == 0 else 0.0) + 0.12 * k) % 1, P['stride'], P['lift'])
        else:
            g = (0, 0)
        ft = (ho[0] + rest[k] * (0.8 - 0.1 * curl) + g[0] + 2.0 * (-1 if k == 3 else 0) * 0, g[1])
        if k == 3 and rear > 0:
            ft = (ho[0] + 11 + 3 * rear, -9 - 14 * rear + g[1])
        if curl > 0:
            ft = (ho[0] + rest[k] * 0.3, ft[1] - 7 * curl)
        spider_leg(c, ho, ft, SPID_B, 1.0)
    # abdomen
    ab = (hx - 8 - 1.0 * rear, -17.5 + dy - 1.5 * rear - 2 * P['abd'] * 3)
    with c.at(ab[0], ab[1], -0.15 - P['abd'] + P['tilt'] * 0.4):
        with c.part(SPID, line=0.5, bevel=4.0) as p:
            p.ell(0, 0, 9.0, 7.4)
            p.poly([(-7, 2), (-12, 5), (-7, 6)])
        with c.part(SPOT, bevel=1.0) as p:        # reloj de arena ambar
            p.poly([(-2.2, -1.4), (2.2, -1.4), (0.2, 1.4), (2.6, 4.4), (-2.6, 4.4), (-0.2, 1.4)])
        with c.part(SPID_B, bevel=1.0) as p:
            for k in range(5):
                p.limb((-6 + k * 3, -6.8), (-6 + k * 3 + 0.5, -9.2), 0.5, 0.2)    # pelos
    # cefalotorax
    with c.at(ct[0], ct[1], P['tilt']):
        with c.part(SPID, line=0.5, bevel=3.0) as p:
            p.ell(0, 0, 6.6, 5.2)
        with c.part(SPID, line=0.5, bevel=2.6) as p:
            p.ell(7.0, 0.8, 4.4, 4.0)
        with c.part(DARK) as p:
            p.ell(8.5, -0.3, 2.4, 2.2)
        with c.part(AMBEYE) as p:
            e = P['eye']
            p.ell(10.0, -1.3, 0.8 + 0.3 * e); p.ell(8.0, -1.8, 0.8 + 0.3 * e); p.ell(10.4, 0.6, 0.6); p.ell(7.4, 0.0, 0.55)
        c.glow(9.0, -1.0, 3.0, AMBER, 0.12 + 0.3 * P['eye'])
        fg = P['fang']
        with c.part(SPID_B, line=0.3, bevel=0.8) as p:       # quelíceros y colmillos
            p.limb((9.5, 2.8), (10.6 + fg * 0.3, 5.5 + fg * 0.4), 1.2, 0.5)
            p.limb((7.2, 3.2), (7.8 - fg * 0.4, 6.0 + fg * 0.5), 1.2, 0.5)
        with c.part(Mat(ramp=['#c8c0a0', '#f0ead0', '#ffffff'], bevel=0.5, dith=0.0)) as p:
            p.limb((10.6 + fg * 0.3, 5.0 + fg * 0.4), (10.9 + fg * 0.4, 7.2 + fg * 0.5), 0.5, 0.2)
            p.limb((7.8 - fg * 0.4, 5.4 + fg * 0.5), (7.5 - fg * 0.5, 7.6 + fg * 0.6), 0.5, 0.2)
        if fg > 0.5 or P['bite']:
            with c.part(VENOM, bevel=0.5) as p:
                p.ell(10.9 + fg * 0.4, 8.4 + fg * 0.5 + math.sin(ph * 12) * 0.6, 0.7, 0.9)
    # patas cercanas
    for k in range(4):
        ho = (ct[0] + anchors[k] + 0.5, ct[1] + 1.0)
        if P['walk']:
            g = gait((ph + (0.0 if k % 2 == 0 else 0.5) + 0.12 * k) % 1, P['stride'], P['lift'])
        else:
            g = (0, 0)
        ft = (ho[0] + rest[k] * 0.9 + g[0], g[1])
        if k >= 2 and rear > 0:
            ft = (ho[0] + 8 + 6 * rear * (k - 1.5), -10 - 11 * rear * (1 if k == 3 else 0.6) + g[1])
        if P['bite'] and k >= 2:
            ft = (ho[0] + 12 + 3 * (k - 2), -3.0 - (k - 2) * 2)
        if curl > 0:
            ft = (ho[0] + rest[k] * 0.3, ft[1] - 7 * curl)
        spider_leg(c, ho, ft, SPID_L, 1.25)


def draw_arana(c, a, i, n):
    if a == 'death':
        return death_arana(c, i, n)
    P = ara_pose(a, i, n)
    arana_body(c, P, a)
    if P['flash']:
        c.flash(WHITE, P['flash'])
    if P['bite']:
        for q in range(4):
            c.dotw(18 + q * 1.5, -6 - q * 1.2, GREEN)


def death_arana(c, i, n):
    if i == 0:
        arana_body(c, ara_pose('hurt', 0, 2), 'hurt')
        c.flash(WHITE, 0.5)
        return
    u = i / (n - 1)
    P = ara_pose('hurt', 1, 2)
    P['rear'] = 0
    ang = kf(u, [(0, 0), (0.3, -0.3), (0.65, -2.3), (1.0, -3.14)])
    cy = kf(u, [(0, -12), (0.3, -17), (0.6, -14), (1.0, -8.0)])
    curl = sm(u * 1.1)
    with c.at(-4 - 2 * u, cy, ang):
        with c.at(-2, 11, 0):
            arana_body(c, P, 'idle', curl=curl)
    if u > 0.3:
        w = min(1, (u - 0.3) / 0.5)
        with c.part(VENOM, bevel=0.8) as p:
            p.ell(-3, -0.9, 3 + 8 * w, 0.8 + 0.5 * w)
        for q in range(6):
            if u < 0.9:
                c.dotw(-9 + q * 3, -4 - u * 6 - (q % 3) * 2, GREEN)


# ------------------------------------------------------------------ BRUJA DEL PANTANO
def bru_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(hx=-3.0, dy=0.5 * s, lean=0.18, ph=t, walk=False, stride=0, lift=0, arm=(0.9, 1.4), arm2=(1.3, 0.2), pot=0.0, glow=0.0, flash=0.0,
             head=0.0, cld=s, throw=False, laugh=0.0)
    if a == 'idle':
        P['arm'] = (0.9 + 0.08 * s, 1.4)
        P['laugh'] = 0.5 + 0.5 * s
    elif a == 'walk':
        P.update(walk=True, stride=3.5, lift=2.0, dy=-0.9 * abs(math.sin(2 * math.pi * t)) + 0.3, lean=0.3, cld=math.sin(4 * math.pi * t))
        P['arm'] = (0.9, 1.4); P['arm2'] = (1.3 + 0.3 * s, 0.2)
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(lean=lerp(0.18, -0.12, w), hx=lerp(-3, -5, w), glow=w, pot=1.0, head=-0.1 * w)
        P['arm'] = (lerp(0.9, -2.1, w), lerp(1.4, -0.5, w))
    elif a == 'attack':
        k = i / (n - 1)
        P.update(lean=kf(k, [(0, -0.12), (0.3, 0.1), (0.6, 0.35), (1, 0.2)]), hx=kf(k, [(0, -5), (0.4, -1), (1, -3)]), glow=1.0 if i < 3 else 0.0, pot=1.0 if i < 3 else 0.0)
        P['arm'] = (kf(k, [(0, -2.1), (0.3, -1.2), (0.6, 0.1), (1, 0.6)]), kf(k, [(0, -0.5), (0.4, 0.1), (1, 0.8)]))
        P['laugh'] = 1.0
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(hx=-3 + rx, lean=ln, flash=fl, head=-0.3 if i == 0 else -0.1, laugh=1)
        P['arm'] = (-0.2, 0.8) if i == 0 else (0.7, 1.2)
    return P


def bruja_body(c, P, a, nohat=False, nocld=False):
    hx, dy, lean, ph = P['hx'], P['dy'], P['lean'], P['ph']
    hip = (hx, -12 + dy)
    sl = (math.sin(lean), -math.cos(lean))
    neck = (hip[0] + 10.5 * sl[0], hip[1] + 10.5 * sl[1])
    sh = (hip[0] + 8.5 * sl[0], hip[1] + 8.5 * sl[1])
    sw = math.sin(ph * 6.283)
    # caldero (mano lejana)
    a2 = P['arm2']
    if not nocld:
        e2, h2 = fk((sh[0] + 0.5, sh[1]), a2[0], 5, a2[1], 5)
        with c.part(WROBE_D, line=0.4, bevel=1.4) as p:
            p.limb((sh[0] + 0.5, sh[1]), e2, 1.8, 1.5); p.limb(e2, h2, 1.5, 1.3)
        cx_, cy_ = h2[0] + 1.5 + 1.2 * P['cld'] * 0.5, h2[1] + 6.5
        with c.part(WROBE_D) as p:
            p.limb((h2[0], h2[1]), (cx_ - 4.5, cy_ - 3.5), 0.5, 0.4); p.limb((h2[0], h2[1]), (cx_ + 4.5, cy_ - 3.5), 0.5, 0.4)
        with c.at(cx_, cy_, 0.08 * P['cld']):
            with c.part(POT, line=0.5, bevel=2.8) as p:
                p.ell(0, 0, 6.2, 5.4)
                p.rect(-6.8, -4.6, 6.8, -2.8)
                p.poly([(-4.5, 4), (-5.5, 7), (-3, 6)]); p.poly([(4.5, 4), (5.5, 7), (3, 6)])
            with c.part(POTION, bevel=1.8) as p:
                p.ell(0, -3.7, 5.6, 1.5)
            with c.part(POTION, bevel=1.0) as p:
                for q in range(3):
                    bb = (ph * 3 + q * 0.33) % 1
                    p.ell(-3 + q * 3, -4.5 - bb * 3.5, 1.3 - 0.7 * bb, 1.1 - 0.5 * bb)
            c.glow(0, -4, 7, GREEN, 0.3)
    # tunica larga (detras)
    hem = [(hip[0] - 8 + 0.6 * sw - lean * 2, -0.6), (hip[0] - 4, -2.5 + 0.8 * math.sin(ph * 6.283 + 1)), (hip[0], -0.4), (hip[0] + 4, -2.6 + 0.8 * math.sin(ph * 6.283 + 2)), (hip[0] + 8 - 0.6 * sw, -0.5)]
    if P['walk']:
        hem = [(x_ - 2, y_) for x_, y_ in hem]
    with c.part(WROBE, line=0.5, bevel=2.8) as p:
        p.poly([(neck[0] - 3, neck[1] - 1), (neck[0] + 4, neck[1] + 0.5), (hip[0] + 7, hip[1] + 4)] + hem[::-1] + [(hip[0] - 7, hip[1] + 2), (neck[0] - 6, neck[1] + 4)])
    with c.part(WROBE_D, bevel=1.2) as p:
        p.poly([(hip[0] - 2, hip[1] + 2), (hip[0] + 2, hip[1] + 1.5), (hem[2][0] + 1, hem[2][1]), (hem[1][0], hem[1][1] - 0.5)])
    with c.part(MOSS, bevel=0.8) as p:
        p.ell(hip[0] - 5, hip[1] + 6, 2, 1.1); p.ell(hip[0] + 3, hip[1] + 8, 1.6, 1.0)
    # zapatos curvados
    if P['walk']:
        f1 = gait(ph, P['stride'], P['lift']); f2 = gait((ph + 0.5) % 1, P['stride'], P['lift'])
    else:
        f1, f2 = (-1.5, 0), (2.5, 0)
    for f_ in (f1, f2):
        with c.part(WROBE_D, line=0.4, bevel=0.8) as p:
            p.poly([(hip[0] + f_[0] - 2, f_[1] - 2.2), (hip[0] + f_[0] + 3.5, f_[1] - 1.8), (hip[0] + f_[0] + 5.5, f_[1] - 3.5 + 0), (hip[0] + f_[0] + 4.5, f_[1] + 0.2), (hip[0] + f_[0] - 2, f_[1] + 0.2)])
    # torso encorvado + hombrera
    with c.at(hip[0] + 4 * sl[0], hip[1] + 4 * sl[1], lean):
        with c.part(WROBE, bevel=2.4) as p:
            p.ell(0, -3.5, 5.0, 6.4)
        with c.part(GOLDB, bevel=0.5) as p:
            p.rect(-4.8, 0.6, 4.8, 1.8)
            p.rect(-1, 0.1, 1.2, 2.3)
    # cabeza
    hxn = neck[0] + 3.0 + 3 * lean
    hyn = neck[1] - 2.4
    with c.at(hxn, hyn, lean * 0.5 + P['head']):
        with c.part(WSKIN, line=0.5, bevel=1.8) as p:
            p.ell(0, 0, 4.0, 4.2)
            p.poly([(3, -0.5), (7.5, 2.2), (6.2, 3.0), (2.5, 2.0)])      # nariz ganchuda
            p.poly([(-1, 3), (3.5, 3.2), (2.5, 6.4 + P['laugh'] * 0.5), (0, 5.6)])      # barbilla
        with c.part(DARK) as p:
            p.poly([(0.4, 3.4), (3.4, 3.6), (3.2, 4.4 + P['laugh'] * 0.9), (0.4, 4.0)])
        with c.part(AMBEYE) as p:
            p.ell(2.4, -0.4, 1.0, 0.9)
        c.glow(2.4, -0.4, 3, GREEN, 0.5)
        with c.part(WROBE_D) as p:    # pelo desgreñado
            p.poly([(-4, -2), (-6.5, 2), (-5, 6), (-3, 3)])
        if not nohat:
            with c.part(HATP, line=0.5, bevel=2.0) as p:
                p.ell(0.8, -3.2, 8.2, 2.0, -0.08)                                    # ala
                p.poly([(-3.4, -3.6), (0, -9), (3.6, -11), (5.0, -14.5 + math.sin(ph * 6.283) * 0.5), (7.4, -13), (4.6, -9.5), (3.0, -3.6)])    # copa doblada
            with c.part(GOLDB, bevel=0.5) as p:
                p.rect(-3, -5.4, 3.4, -3.8)
            with c.part(GOLDB, bevel=0.5) as p:
                p.rect(-0.6, -6.0, 1.2, -3.4)
    # brazo cercano + pocion
    A1, A2 = P['arm']
    e, hnd = fk(sh, A1, 5.3, A2, 5.3)
    with c.part(WROBE, line=0.4, bevel=1.6) as p:
        p.limb(sh, e, 2.1, 1.7); p.limb(e, hnd, 1.7, 1.4)
    with c.part(WSKIN, bevel=0.8) as p:
        p.ell(hnd[0], hnd[1], 1.5)
        for q in (-1, 0, 1):
            p.limb(hnd, (hnd[0] + 2.4, hnd[1] + q * 1.1 + 0.5), 0.4, 0.2)
    if P['pot'] > 0.5:
        fx, fy = hnd[0] + 1, hnd[1] - 3.2
        with c.part(GLASS, line=0.3, bevel=1.2) as p:
            p.ell(fx, fy, 2.8, 2.6)
            p.rect(fx - 0.8, fy - 5, fx + 0.9, fy - 2)
        with c.part(POTION, bevel=1.2) as p:
            p.ell(fx, fy + 0.5, 2.1, 1.9)
        with c.part(WOOD, bevel=0.5) as p:
            p.rect(fx - 1, fy - 6, fx + 1.1, fy - 4.6)
        c.glow(fx, fy, 6, GREEN, 0.3 + 0.5 * P['glow'])
        for q in range(4):
            ang = q * 1.57 + ph * 6.283 * 2
            c.dotw(fx + math.cos(ang) * 5, fy + math.sin(ang) * 5, GREEN)


def draw_bruja(c, a, i, n):
    if a == 'death':
        return death_bruja(c, i, n)
    P = bru_pose(a, i, n)
    bruja_body(c, P, a)
    if P['flash']:
        c.flash(WHITE, P['flash'])


def _p_hat(c):
    with c.part(HATP, line=0.5, bevel=2.0) as p:
        p.ell(0, 1.5, 8.2, 2.0, -0.08)
        p.poly([(-3.4, 0.5), (0, -5), (3.6, -7), (5.0, -10.5), (7.4, -9), (4.6, -5.5), (3.0, 0.5)])
    with c.part(GOLDB, bevel=0.5) as p:
        p.rect(-3, -1.4, 3.4, 0.2)


def _p_cauldron(c):
    with c.part(POT, line=0.5, bevel=2.8) as p:
        p.ell(0, 0, 6.2, 5.4); p.rect(-6.8, -4.6, 6.8, -2.8)
    with c.part(POTION, bevel=1.8) as p:
        p.ell(0, -3.7, 5.6, 1.5)


def death_bruja(c, i, n):
    if i == 0:
        bruja_body(c, bru_pose('hurt', 0, 2), 'hurt')
        c.flash(WHITE, 0.5)
        return
    u = i / (n - 1)
    P = bru_pose('hurt', 1, 2)
    P['pot'] = 0
    P['laugh'] = 1
    # se encoge y se desvanece en humo verde
    sc = kf(u, [(0, 1.0), (0.45, 0.8), (0.7, 0.45), (1.0, 0.25)])
    sx_ = kf(u, [(0, 1.0), (0.5, 1.15), (1.0, 1.5)])
    if u < 0.85:
        with c.at(-3, 0, kf(u, [(0, 0), (1, -0.5)]), sx_, sc):
            bruja_body(c, dict(P, hx=0), 'hurt', nohat=True, nocld=True)
        c.flash(GREEN, min(0.7, u * 0.9))
    items = [dict(fn=_p_hat, x=1, y=-26, r=3, vx=2, vy=-9, spin=4, rest=0.3, bounce=0.25),
             dict(fn=_p_cauldron, x=8, y=-12, r=5, vx=5, vy=-6, spin=3, rest=1.2, bounce=0.25)]
    for d_ in items:
        d_['vx'] *= 0.6; d_['vy'] *= 0.7
    b = Bits(items, seed=3, T=0.75, g=1.6)
    draw_bits(c, b, u)
    for q in range(14):
        if u > 0.15 and u < 0.97:
            ang = q * 0.5
            r0 = (u - 0.15) * 20
            c.dotw(math.cos(ang) * r0 * 0.9 - 3, -10 - math.sin(abs(ang)) * r0 * 0.6 - (q % 3) * 2, GREEN if q % 2 else '#4a9a28')
    if u > 0.4:
        w = min(1, (u - 0.4) / 0.4)
        with c.part(POTION, bevel=0.9) as p:
            p.ell(8, -0.9, 2 + 5 * w, 0.8 + 0.4 * w)


# ------------------------------------------------------------------ TRONCO VIVO (64x64)
def tro_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(hx=-3.0, dy=0.0, lean=0.04, ph=t, walk=False, arm=(1.2, 0.5), arm2=(1.1, 0.4), eye=0.4, mouth=0.0, flash=0.0, k=None, sway=s, leaf=s)
    if a == 'idle':
        P['dy'] = 0.6 * s
        P['arm'] = (1.2 + 0.06 * s, 0.5); P['arm2'] = (1.1 + 0.06 * math.sin(2 * math.pi * t + 1), 0.4)
    elif a == 'walk':
        P.update(walk=True, dy=-1.6 * abs(math.sin(2 * math.pi * t)), lean=0.1 + 0.05 * s, hx=-2)
        P['arm'] = (1.2 + 0.3 * s, 0.5); P['arm2'] = (1.1 - 0.3 * s, 0.4)
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(lean=lerp(0.04, -0.2, w), hx=lerp(-3, -6, w), dy=lerp(0, 1, w), eye=w, mouth=w * 3)
        P['arm'] = (lerp(1.2, -2.5, w), lerp(0.5, -0.5, w)); P['arm2'] = (lerp(1.1, -2.2, w), lerp(0.4, -0.4, w))
    elif a == 'attack':
        k = i / (n - 1)
        P['lean'] = kf(k, [(0, -0.2), (0.2, 0.15), (0.4, 0.4), (0.7, 0.35), (1, 0.1)])
        P['hx'] = kf(k, [(0, -6), (0.2, -1), (0.4, 3), (0.7, 3), (1, 0)])
        P['dy'] = kf(k, [(0, 1), (0.4, 3), (1, 0)])
        P['arm'] = (kf(k, [(0, -2.5), (0.2, -0.6), (0.4, 1.1), (0.7, 1.15), (1, 1.0)]), kf(k, [(0, -0.5), (0.4, 0.3), (1, 0.5)]))
        P['arm2'] = (kf(k, [(0, -2.2), (0.2, -0.5), (0.4, 1.0), (0.7, 1.05), (1, 0.9)]), kf(k, [(0, -0.4), (0.4, 0.3), (1, 0.5)]))
        P['eye'] = 1.0; P['mouth'] = 4; P['k'] = k
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(hx=-3 + rx, lean=ln * 0.8, flash=fl * 0.9, mouth=4, eye=0.8)
        P['arm'] = (0.3, 0.4) if i == 0 else (0.9, 0.5); P['arm2'] = (0.1, 0.3) if i == 0 else (0.8, 0.4)
    return P


def branch_arm(c, sh, a1, a2, L1, L2, m, thick):
    e, h = fk(sh, a1, L1, a2, L2)
    with c.part(m, line=0.5, bevel=2.6) as p:
        p.limb(sh, e, thick, thick * 0.8)
        p.limb(e, h, thick * 0.8, thick * 0.65)
    # manos: ramitas
    ang = a1 + a2
    with c.part(m, line=0.4, bevel=1.0) as p:
        p.ell(h[0], h[1], thick * 0.9)
        for q in (-0.7, -0.15, 0.4, 0.95):
            tip = (h[0] + math.cos(ang + q) * 5.8, h[1] + math.sin(ang + q) * 5.8)
            p.limb(h, tip, 1.3, 0.4)
    with c.part(MOSS, bevel=0.8) as p:
        p.ell(lerp(sh[0], e[0], 0.5), lerp(sh[1], e[1], 0.5) - thick * 0.7, thick * 0.9, 0.9)
    return h


def tronco_body(c, P, a='idle', parts_off=False):
    hx, dy, lean, ph = P['hx'], P['dy'], P['lean'], P['ph']
    base = (hx, -14 + dy)
    sl = (math.sin(lean), -math.cos(lean))
    top = (base[0] + 26 * sl[0], base[1] + 26 * sl[1])
    chest = (base[0] + 18 * sl[0], base[1] + 18 * sl[1])
    # raices-piernas
    if P['walk']:
        g1 = gait(ph, 4.5, 3.0); g2 = gait((ph + 0.5) % 1, 4.5, 3.0)
    elif a in ('windup', 'attack'):
        g1, g2 = (-7, 0), (6, 0)
    else:
        g1, g2 = (-4.5, 0), (4.5, 0)
    for (g, m, off) in ((g1, WOOD_B, -5), (g2, WOOD, 4)):
        hip = (base[0] + off, base[1] + 2)
        ft = (hip[0] + g[0], g[1])
        kn = ik2(hip, ft, 8, 8, bend=-1)
        with c.part(m, line=0.5, bevel=3.0) as p:
            p.limb(hip, kn, 5.0, 4.4); p.limb(kn, ft, 4.4, 3.6)
        with c.part(m, line=0.5, bevel=1.2) as p:      # raices en el pie
            for q, (dx, dyy) in enumerate(((-6, 0), (-2, 1), (3, 0.5), (7, 0))):
                p.limb((ft[0], ft[1] - 2), (ft[0] + dx, ft[1] - 0.4 + dyy), 1.9, 0.6)
    # brazo lejano
    shf = (chest[0] + 3, chest[1] - 4)
    branch_arm(c, shf, P['arm2'][0], P['arm2'][1], 11, 12, WOOD_B, 3.6)
    # tronco
    with c.at(base[0], base[1], lean):
        with c.part(WOOD, line=0.5, bevel=4.5) as p:
            p.poly([(-11, 0), (11, 0), (13, -10), (11, -24), (8, -30), (-8, -31), (-12, -24), (-13, -10)])
        with c.part(WOOD_B, bevel=1.5) as p:      # grietas oscuras
            p.poly([(5, -2), (6.5, -9), (5, -15), (7, -21), (6, -24), (4.5, -17), (5.6, -10), (3.5, -3)])
            p.poly([(-8, -10), (-6, -16), (-8, -22), (-9.5, -17)])
        with c.part(BARK_L, bevel=0.8) as p:       # anillos
            p.ell(-1, -29.5, 7.5, 1.6)
        with c.part(MOSS, bevel=1.2, line=0.0) as p:
            p.poly([(-12, -24), (-8, -31), (3, -31.5), (6, -28), (0, -26.5), (-3, -22), (-6, -23), (-9, -19), (-12.5, -20)])
            p.poly([(7, -2), (12, -4), (13, -9), (10, -8)])
        # hongos luminosos
        for (mx, my, r_) in ((-12.5, -13, 3.0), (-6, -31.5, 2.2), (12, -16, 2.6)):
            with c.part(WOOD_B, bevel=0.5) as p:
                p.rect(mx - 0.7, my - 0.5, mx + 0.7, my + 2.4)
            with c.part(SHROOM, bevel=1.4) as p:
                p.ell(mx, my, r_, r_ * 0.7)
                p.rect(mx - r_, my, mx + r_, my + 0.6)
            with c.part(SHROOM_E, bevel=0.6) as p:
                p.ell(mx - r_ * 0.3, my - r_ * 0.2, r_ * 0.35, r_ * 0.25)
            c.glow(mx, my, r_ + 3, AMBER, 0.28)
        # rostro tallado
        e = P['eye']
        with c.part(DARK) as p:
            p.poly([(1.5, -22), (8.5, -23), (8.5, -18.5), (2, -18)])
            p.poly([(-6.5, -22.5), (-1, -22.5), (-1.5, -18.5), (-6, -19)])
            p.poly([(-3, -14), (7, -14.5), (6.5, -14.5 + P['mouth'] + 2.5), (-2, -11.0 - 0.5 + P['mouth'])])
        with c.part(AMBEYE) as p:
            p.poly([(3, -21), (7.8, -21.8), (7.6, -19.6), (3.4, -19.2)])
            p.poly([(-5.5, -21.2), (-1.8, -21.2), (-2.2, -19.4), (-5.2, -19.6)])
        c.glow(5.5, -20.5, 3 + 1.5 * e, AMBER, 0.25 + 0.4 * e)
        c.glow(-3.5, -20.5, 3 + 1.5 * e, AMBER, 0.2 + 0.3 * e)
        with c.part(WOOD, bevel=0.8, line=0.3) as p:      # ceño
            p.poly([(0.5, -24.8), (9.5, -26), (9.5, -23.4), (1, -22.6)])
            p.poly([(-7.5, -25), (-0.3, -24.5), (-0.5, -22.6), (-7, -22.8)])
        with c.part(Mat(ramp=['#8a6a3a', '#c8a468', '#f0d898'], bevel=0.5, dith=0.0)) as p:     # dientes de astilla
            for q in range(4):
                p.poly([(-1.8 + q * 2.0, -14), (-0.8 + q * 2.0, -14), (-1.3 + q * 2.0, -11.5 + P['mouth'] * 0.3 - 0.5)])
        # ramas con hojas en la cima
        with c.part(WOOD, line=0.4, bevel=1.0) as p:
            p.limb((-4, -30), (-9 + math.sin(ph * 6.283) * 0.8, -38), 1.6, 0.6)
            p.limb((3, -30.5), (6 + math.sin(ph * 6.283 + 1) * 0.8, -39), 1.5, 0.5)
            p.limb((-9, -26), (-15, -31), 1.3, 0.5)
        with c.part(MOSS, bevel=0.8, line=0.2) as p:
            for (lx, ly) in ((-9.5, -39), (-12, -36.5), (6.5, -40.5), (9, -37), (-15.5, -32.5), (-7, -37)):
                p.ell(lx + math.sin(ph * 6.283 + lx) * 0.6, ly, 2.2, 1.4, 0.6)
    # brazo cercano
    shn = (chest[0] - 2, chest[1] - 5)
    h = branch_arm(c, shn, P['arm'][0], P['arm'][1], 11, 12, WOOD, 4.0)
    if P['k'] is not None and 0.3 < P['k'] < 0.8:
        for q in range(8):
            c.dotw(h[0] + 3 + q * 2.4, -1.5 - (q % 3) * 1.4, '#6a8a40' if q % 2 else '#4a3828')
        for q in range(5):
            c.dotw(h[0] + 2 + q * 3, -8 - (q * 5) % 9, '#68a032')


def draw_tronco(c, a, i, n):
    if a == 'death':
        return death_tronco(c, i, n)
    P = tro_pose(a, i, n)
    tronco_body(c, P, a)
    if P['flash']:
        c.flash(WHITE, P['flash'])


def _p_log(L, r):
    def f(c):
        with c.part(WOOD, line=0.5, bevel=2.4) as p:
            p.limb((-L / 2, 0), (L / 2, 0), r)
        with c.part(BARK_L, bevel=0.8) as p:
            p.ell(L / 2, 0, r * 0.45, r * 0.9)
    return f


def _p_leaf(c):
    with c.part(MOSS, bevel=0.8, line=0.2) as p:
        p.ell(0, 0, 2.2, 1.4, 0.6)


def _p_shroom(c):
    with c.part(SHROOM, bevel=1.4) as p:
        p.ell(0, 0, 3, 2.1)
    with c.part(SHROOM_E, bevel=0.6) as p:
        p.ell(-1, -0.5, 1, 0.7)


def death_tronco(c, i, n):
    if i == 0:
        tronco_body(c, tro_pose('hurt', 0, 2), 'hurt')
        c.flash(WHITE, 0.45)
        return
    u = i / (n - 1)
    import random
    rnd = random.Random(21)
    P = tro_pose('hurt', 1, 2)
    P['mouth'] = 4
    if u < 0.5:
        # el tronco se parte: tiembla y se hunde
        P['dy'] = u * 6
        P['hx'] = -3 + math.sin(u * 40) * 1.2
        P['eye'] = 1 - u * 2
        sy = 1.0 - u * 0.55
        with c.at(0, 0, 0, 1.0, sy):
            tronco_body(c, P, 'hurt')
        c.flash('#ffd890', u * 0.5)
    items = []
    for k in range(7):
        items.append(dict(fn=_p_log(rnd.uniform(8, 15), rnd.uniform(2.6, 4.2)), x=rnd.uniform(-8, 8), y=-20 - rnd.uniform(0, 14), r=3.5,
                          vx=rnd.uniform(-8, 8), vy=rnd.uniform(-9, -3), spin=rnd.uniform(-5, 5), rest=rnd.uniform(-0.3, 0.3), bounce=0.3))
    for k in range(8):
        items.append(dict(fn=_p_leaf, x=rnd.uniform(-10, 10), y=-28 - rnd.uniform(0, 8), r=1, vx=rnd.uniform(-5, 5), vy=rnd.uniform(-7, -1), spin=rnd.uniform(-6, 6), rest=rnd.uniform(-0.5, 0.5), bounce=0.1))
    for k in range(3):
        items.append(dict(fn=_p_shroom, x=-10 + k * 9, y=-28, r=2, vx=rnd.uniform(-5, 5), vy=rnd.uniform(-7, -3), spin=rnd.uniform(-5, 5), rest=0.1, bounce=0.3))
    for d_ in items:
        d_['vx'] *= 0.6; d_['vy'] *= 0.7
    b = Bits(items, seed=4, T=0.8, g=1.7)
    if u >= 0.35:
        draw_bits(c, b, (u - 0.35) / 0.65)
        # tocon que queda
        w = min(1, (u - 0.35) / 0.4)
        h_ = 4 + 6 * (1 - w) * 0 + 6
        with c.part(WOOD, line=0.5, bevel=3.0) as p:
            p.poly([(-11, 0), (11, 0), (12, -4 - 2 * w), (9, -7.5 - 3 * w), (4, -6 - 4 * w), (0, -9 - 3 * w), (-5, -6 - 2 * w), (-10, -8 - 2 * w), (-12, -4)])
        with c.part(BARK_L, bevel=0.8) as p:
            p.ell(0, -8.5 - 2 * w, 8.0, 1.4)
        with c.part(MOSS, bevel=1.0) as p:
            p.ell(-6, -9 - 2 * w, 3.4, 1.3)
        with c.part(AMBEYE) as p:
            if u < 0.8:
                p.ell(4, -4.5, 1.1, 0.9)
    for q in range(10):
        if 0.3 < u < 0.95:
            c.dotw(-12 + q * 2.6 + (q - 5) * u, -12 - u * 12 - (q % 4) * 3, '#ffd870' if q % 2 else '#a8d058')


def sheet_arana():
    return enemy_sheet('en_arana', (48, 48), (24, 46), (24, 16), draw_arana, (10, 16, 8),
                       STD(6, hit=[2, 3], box=[2, -22, 22, 22], idle=6, walk=8, wfps=14, fa=16))


def sheet_bruja():
    return enemy_sheet('en_bruja', (48, 48), (24, 46), (12, 30), draw_bruja, (10, 20, 16),
                       STD(6, rel=3, muz=[12, -28], idle=6, walk=8, wfps=10, fa=13))


def sheet_tronco_vivo():
    return enemy_sheet('en_tronco_vivo', (64, 64), (32, 62), (26, 50), draw_tronco, (20, 12, 10),
                       STD(6, hit=[2, 3], box=[8, -48, 30, 48], idle=6, walk=8, ifps=6, wfps=7, fa=9, death=8, dfps=8))


SHEETS = [sheet_arana, sheet_bruja, sheet_tronco_vivo]
