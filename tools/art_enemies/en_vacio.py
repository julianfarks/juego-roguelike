from common import *
from en_catacumbas import enemy_sheet, STD, DARK, WHITE

OBS = Mat(ramp=['#07030f', '#140a28', '#281450', '#442488', '#7442c4'], bevel=1.8, tex=0.2, seed=61, bias=0.5)
OBS_B = Mat(ramp=['#05020a', '#0e0620', '#1c0e3c', '#321a68', '#54309a'], bevel=1.8, tex=0.2, seed=62)
CHIT = Mat(ramp=['#0a0616', '#1c1038', '#33206a', '#5636a6', '#8e66e0'], bevel=1.4, tex=0.15, seed=63, bias=0.5)
CHIT_B = Mat(ramp=['#06040e', '#120a26', '#22164a', '#3a2478', '#5c40a8'], bevel=1.4, seed=64)
BLADE = Mat(ramp=['#1a0e3a', '#3c1e7a', '#7a44c8', '#c08cf8', '#f0e0ff'], bevel=1.0, dith=0.3)
VEYE = Mat(ramp=['#8a1ad8', '#c84cff', '#f0a0ff', '#ffffff'], emi=True, nooutline=True, bevel=0.8, dith=0.1)
VGLOW = '#B04CFF'
ICHOR = Mat(ramp=['#2a0a4a', '#5a1a9a', '#8a3ad8', '#c070ff'], bevel=1.0, dith=0.3)
SCLERA = Mat(ramp=['#2a1a50', '#5a3c8e', '#9a80c4', '#d4c4ee', '#f6eeff'], bevel=7.0, dith=0.5, bias=0.3, outcol='#1c0e3a')
IRIS = Mat(ramp=['#5a10b0', '#9a30f0', '#c868ff', '#f0b0ff'], emi=True, nooutline=True, bevel=5.0, dith=0.2)
PUPIL = Mat(ramp=['#05020c', '#0c0618'], bevel=1.0, dith=0.0)
VEIN = Mat(ramp=['#6a1a5a', '#a02a78', '#d04a98'], bevel=0.6, dith=0.0)
FLESHV = Mat(ramp=['#10061c', '#2a1240', '#4a2468', '#6e3a90', '#9a5cc0'], bevel=2.0, tex=0.2, seed=65)
GHOST = Mat(ramp=['#241848', '#44348a', '#7a68c4', '#b4a8e8', '#e8e0ff'], bevel=2.6, dith=0.45, bias=0.5, outcol='#1a1038')
GHOST_W = Mat(ramp=['#1a1238', '#342a70', '#5c4ca8', '#8e80d4', '#c0b4f0'], bevel=1.6, dith=0.4, outcol='#140c30')
BONEV = Mat(ramp=['#201838', '#4a3c78', '#8478b0', '#bcb0dc', '#ece6ff'], bevel=1.2, dith=0.4)


# ------------------------------------------------------------------ ACECHADOR
def ace_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(hx=-2.0, dy=0.5 * s, lean=0.45, ph=t, walk=False, stride=0, lift=0, arm=(1.0, -0.5), arm2=(0.9, -0.4), eye=0.3, jaw=0.0,
             head=0.0, flash=0.0, trail=0.0, curl=0.0)
    if a == 'idle':
        P['arm'] = (0.95 + 0.1 * s, -0.5 + 0.1 * s); P['arm2'] = (0.85 + 0.1 * math.sin(2 * math.pi * t + 1), -0.4)
        P['jaw'] = 0.6 * (0.5 + 0.5 * s)
    elif a == 'walk':
        P.update(walk=True, stride=5.0, lift=3.2, dy=-0.7 * abs(math.sin(2 * math.pi * t * 2)) + 0.5, lean=0.55, hx=-1)
        P['arm'] = (0.8 + 0.25 * s, -0.5); P['arm2'] = (0.8 - 0.25 * s, -0.5)
        P['head'] = 0.05
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(lean=lerp(0.45, 0.9, w), hx=lerp(-2, -6, w), dy=lerp(0, 2.0, w), eye=w, jaw=2 * w, head=0.1 * w)
        P['arm'] = (lerp(1.0, -2.3, w), lerp(-0.5, 0.2, w)); P['arm2'] = (lerp(0.9, -2.0, w), lerp(-0.4, 0.2, w))
    elif a == 'attack':
        k = i / (n - 1)
        P['lean'] = kf(k, [(0, 0.9), (0.2, 0.2), (0.4, 0.15), (0.7, 0.35), (1, 0.45)])
        P['hx'] = kf(k, [(0, -6), (0.2, 0), (0.4, 5), (0.7, 4), (1, 0)])
        P['dy'] = kf(k, [(0, 2), (0.4, 2.5), (1, 0)])
        P['arm'] = (kf(k, [(0, -2.3), (0.2, -0.3), (0.4, 1.1), (0.7, 1.2), (1, 1.0)]), kf(k, [(0, 0.2), (0.4, -0.2), (1, -0.5)]))
        P['arm2'] = (kf(k, [(0, -2.0), (0.25, -0.1), (0.5, 1.0), (0.75, 1.1), (1, 0.9)]), kf(k, [(0, 0.2), (0.5, -0.2), (1, -0.4)]))
        P['eye'] = 1.0; P['jaw'] = 2.5
        P['trail'] = 1.0 if 0.15 < k < 0.7 else 0.0
        P['k'] = k
        P['stride'] = 0
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(hx=-2 + rx, lean=0.45 + ln * 0.5, flash=fl, jaw=3, head=-0.3 if i == 0 else -0.1, eye=0.9)
        P['arm'] = (0.0, -0.3) if i == 0 else (0.8, -0.4); P['arm2'] = (-0.2, -0.3) if i == 0 else (0.7, -0.3)
    return P


def scythe(c, sh, a1, a2, m, mb):
    # antebrazo + hoja curva
    e = (sh[0] + 6.5 * math.cos(a1), sh[1] + 6.5 * math.sin(a1))
    with c.part(m, line=0.4, bevel=1.2) as p:
        p.limb(sh, e, 1.8, 1.4)
    ang = a1 + a2
    d = (math.cos(ang), math.sin(ang)); nr = (-d[1], d[0])
    L = 11.5
    tip = (e[0] + d[0] * L + nr[0] * 3.5, e[1] + d[1] * L + nr[1] * 3.5)
    midp = (e[0] + d[0] * L * 0.55 + nr[0] * 2.8 * 0.2, e[1] + d[1] * L * 0.55)
    with c.part(mb, line=0.4, bevel=1.4) as p:
        p.poly([(e[0] + nr[0] * 1.5, e[1] + nr[1] * 1.5), (e[0] + d[0] * L * 0.6 + nr[0] * 3.2, e[1] + d[1] * L * 0.6 + nr[1] * 3.2), tip,
                (e[0] + d[0] * L * 0.6 - nr[0] * 0.8, e[1] + d[1] * L * 0.6 - nr[1] * 0.8), (e[0] - nr[0] * 1.5, e[1] - nr[1] * 1.5)])
    with c.part(BLADE, bevel=0.8) as p:
        p.poly([(e[0] + d[0] * L * 0.5 + nr[0] * 2.4, e[1] + d[1] * L * 0.5 + nr[1] * 2.4), tip,
                (e[0] + d[0] * L * 0.62 - nr[0] * 0.4, e[1] + d[1] * L * 0.62 - nr[1] * 0.4)])
    return tip


def acechador_body(c, P, a, flip=False):
    hx, dy, lean, ph = P['hx'], P['dy'], P['lean'], P['ph']
    hip = (hx - 4, -11 + dy)
    if P['walk']:
        f1 = gait(ph, P['stride'], P['lift']); f2 = gait((ph + 0.5) % 1, P['stride'], P['lift'])
        f3 = gait((ph + 0.25) % 1, P['stride'] * 0.8, P['lift']); f4 = gait((ph + 0.75) % 1, P['stride'] * 0.8, P['lift'])
    elif a in ('windup', 'attack'):
        f1, f2, f3, f4 = (-6, 0), (3, 0), (-1, 0), (6, 0)
    else:
        f1, f2, f3, f4 = (-5, 0), (2, 0), (0, 0), (6, 0)
    cu = P['curl']
    sl = (math.cos(-lean), math.sin(-lean))
    cth = (hx + 1, -17.5 + dy)      # torax
    # patas lejanas medias
    for (fx, m) in ((f3, CHIT_B), (f4, CHIT_B)):
        ho = (cth[0] - 1, cth[1] + 1)
        ft = (ho[0] + 3 + fx[0] * 0.8, fx[1])
        kn = ik2(ho, ft, 8, 9, bend=1)
        with c.part(m, line=0.4, bevel=1.0) as p:
            p.tube([ho, kn, ft], 1.3, 0.7)
    # pata trasera lejana
    ft = (hip[0] + 2 + f1[0], f1[1])
    kn = ik2(hip, ft, 8.5, 9.5, bend=1)
    with c.part(CHIT_B, line=0.4, bevel=1.2) as p:
        p.limb(hip, kn, 2.0, 1.4); p.limb(kn, ft, 1.4, 0.8)
    # brazo guadana lejano
    shf = (cth[0] + 5, cth[1] - 1)
    scythe(c, shf, P['arm2'][0], P['arm2'][1], CHIT_B, CHIT_B)
    # abdomen
    with c.at(cth[0] - 8, cth[1] - 1.5, -lean * 0.7 - 0.1):
        with c.part(CHIT, line=0.5, bevel=3.0) as p:
            p.ell(0, 0, 8.5, 5.4)
            p.poly([(-7, -3), (-12, -1), (-8, 2)])
        with c.part(OBS_B, bevel=1.0) as p:
            for k in range(3):
                p.limb((-5 + k * 4, -4.8), (-5 + k * 4 + 1, 4.2), 0.5)
        with c.part(VEYE, bevel=0.8) as p:
            p.ell(-6, 0.4, 1.0, 0.8)
    # torax
    with c.at(cth[0], cth[1], -lean):
        with c.part(CHIT, line=0.5, bevel=2.6) as p:
            p.ell(0, 0, 7.4, 4.8)
        for k in range(3):   # espinas dorsales
            pass
        with c.part(OBS, bevel=1.2, line=0.3) as p:
            p.poly([(-4, -3.6), (-3, -8), (-1.5, -3.8)])
            p.poly([(-0.5, -4.2), (1, -8.5), (2.5, -4.0)])
            p.poly([(3, -3.6), (4.5, -7), (5.5, -3)])
        with c.part(OBS_B, bevel=1.0) as p:
            p.ell(1.5, 1.5, 3.8, 2.0)
    # pata trasera cercana
    ft = (hip[0] + 4 + f2[0], f2[1])
    hip2 = (hip[0] + 1, hip[1])
    kn = ik2(hip2, ft, 8.5, 9.5, bend=1)
    with c.part(CHIT, line=0.4, bevel=1.2) as p:
        p.limb(hip2, kn, 2.2, 1.5); p.limb(kn, ft, 1.5, 0.8)
    with c.part(CHIT, bevel=0.8) as p:
        p.poly([(ft[0] - 1, ft[1] - 0.6), (ft[0] + 3.5, ft[1] + 0.2), (ft[0] - 1, ft[1] + 0.2)])
    # cabeza
    hxn = cth[0] + 8.5 * math.cos(-lean) + 0.5
    hyn = cth[1] + 8.5 * math.sin(-lean) - 1.2
    jaw = P['jaw']
    with c.at(hxn, hyn, -lean * 0.6 + P['head']):
        with c.part(CHIT, line=0.5, bevel=2.2) as p:
            p.poly([(-4.2, -2.8), (1, -4.6), (5.0, -2.2), (5.6, 0.8), (3.2, 2.4), (-3.6, 2.6), (-5, 0)])
        with c.part(OBS_B, line=0.4, bevel=1.0) as p:      # mandibulas
            p.poly([(3.2, 0.8), (7.6, 1.6 + jaw), (4.2, 3.2 + jaw * 0.5)])
            p.poly([(1.0, 1.8), (5.0, 4.4 + jaw), (0.2, 3.0)])
        with c.part(DARK) as p:
            p.ell(2.4, -1.0, 1.6, 1.4, 0.2)
        with c.part(VEYE) as p:
            e = P['eye']
            p.ell(2.6, -1.0, 0.9 + 0.3 * e, 0.8 + 0.3 * e)
            p.ell(-0.7, -1.7, 0.7, 0.6)
            p.ell(-2.8, -1.2, 0.5, 0.5)
        c.glow(2.6, -1.0, 3.8, VGLOW, 0.4 + 0.5 * P['eye'])
        with c.part(CHIT_B, bevel=0.6, line=0.0) as p:     # antenas
            p.limb((-1, -4.4), (-5, -9 + math.sin(ph * 6.28) * 1.2), 0.5, 0.3)
            p.limb((1.5, -4.6), (0.5, -10 + math.sin(ph * 6.28 + 1) * 1.2), 0.5, 0.3)
    # brazo guadana cercano
    shn = (cth[0] + 4, cth[1])
    tip = scythe(c, shn, P['arm'][0], P['arm'][1], CHIT, OBS)
    if P['trail'] > 0:
        k = P['k']
        an = math.atan2(tip[1] - shn[1], tip[0] - shn[0])
        rr = math.hypot(tip[0] - shn[0], tip[1] - shn[1])
        arc_trail(c, shn[0], shn[1], rr - 8, rr + 2, an - 1.7, an + 0.1, TRAIL_V)


TRAIL_V = Mat(ramp=['#5a2aa8', '#9a5cf0', '#d8a8ff', '#ffffff'], emi=True, nooutline=True, bevel=1.5, dith=0.2)


def draw_acechador(c, a, i, n):
    if a == 'death':
        return death_acechador(c, i, n)
    P = ace_pose(a, i, n)
    acechador_body(c, P, a)
    if P['flash']:
        c.flash(WHITE, P['flash'])
    if a == 'windup' and i == n - 1:
        c.flash(VGLOW, 0.08)


def death_acechador(c, i, n):
    if i == 0:
        acechador_body(c, ace_pose('hurt', 0, 2), 'hurt')
        c.flash(WHITE, 0.5)
        return
    u = i / (n - 1)
    P = ace_pose('hurt', 1, 2)
    P['walk'] = False
    ang = kf(u, [(0, 0), (0.3, -0.5), (0.65, -2.4), (1.0, -3.1)])
    cy = kf(u, [(0, -12), (0.3, -17), (0.6, -14), (1.0, -8.5)])
    P['arm'] = (kf(u, [(0, 0.5), (1, -1.7)]), kf(u, [(0, -0.4), (1, 1.4)]))
    P['arm2'] = (kf(u, [(0, 0.5), (1, -1.5)]), kf(u, [(0, -0.4), (1, 1.2)]))
    P['eye'] = 1 - u
    P['jaw'] = 3
    P['hx'] = -2 - 3 * u
    P['lean'] = 0.45
    P['dy'] = 0
    with c.at(-4 - 3 * u, cy, ang):
        with c.at(2, 12, 0):
            P2 = dict(P)
            acechador_body(c, P2, 'idle')
    if u > 0.3:
        w = min(1, (u - 0.3) / 0.5)
        with c.part(ICHOR, bevel=1.0) as p:
            p.ell(-3, -0.9, 3 + 9 * w, 0.9 + 0.5 * w)
        for q in range(7):
            if u < 0.9:
                c.dotw(-8 + q * 3 + (q - 3) * u * 2, -5 - u * 8 - (q % 3) * 2, '#c070ff' if q % 2 else '#8a3ad8')


# ------------------------------------------------------------------ OJO DEL VACIO
def ojo_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(x=-1.0, y=-21 + 1.8 * s, ph=t, dil=0.5, look=3.0, glow=0.3, flash=0.0, orb=0.0, squash=1.0, curl=0.0, lid=0.0)
    if a == 'walk':
        P.update(x=-1, look=3.5, y=-21 + 2.2 * math.sin(2 * math.pi * t), curl=0.0)
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(dil=lerp(0.5, 1.5, w), glow=w, x=lerp(-1, -4, w), y=-21 - 1.5 * w, curl=w, squash=lerp(1, 1.1, w), orb=w * 0.5)
    elif a == 'attack':
        P.update(dil=[1.6, 1.6, 0.3, 0.5, 0.6, 0.5][i], glow=[1, 1, 1, 0.5, 0.3, 0.2][i], x=[-4, -4, 1, 0, -1, -1][i], y=-21 - [1.5, 1.5, 0, 0.5, 0.5, 0][i],
                 curl=[1, 1, -0.5, 0, 0, 0][i], squash=[1.1, 1.12, 0.9, 0.97, 1.0, 1.0][i], orb=[0.8, 1.0, 0.0, 0.0, 0.0, 0.0][i], look=3.5)
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(x=-1 + rx, y=-21 + 1.5, flash=fl, dil=0.2, squash=0.9, lid=1.0 if i == 0 else 0.3)
    return P


def ojo_body(c, P):
    x, y, ph = P['x'], P['y'], P['ph'] * 6.283
    sq = P['squash']
    # tentaculos
    for k in range(6):
        bx = x - 7 + k * 2.8
        by = y + 6 + abs(k - 2.5) * -0.6
        pts = []
        for j in range(7):
            u = j / 6
            sway = math.sin(ph + k * 1.1 + u * 3.2) * (1.3 + 3.0 * u) + P['curl'] * (-2.5 * u * (1 if k < 3 else -0.3))
            pts.append((bx + sway - 0.6 * u * (k - 2.5) * 0.4, by + u * (13 - abs(k - 2.5) * 1.2) * (1 - 0.15 * abs(P['curl']))))
        m = FLESHV if k % 2 == 0 else OBS
        with c.part(m, line=0.4, bevel=1.4) as p:
            p.tube(pts, 2.0, 0.5)
        if k % 2 == 0:
            with c.part(VEYE, bevel=0.5) as p:
                p.ell(pts[3][0], pts[3][1], 0.6)
    # pinchos superiores
    with c.part(OBS, line=0.4, bevel=1.0) as p:
        for (dx, h) in ((-5, 4), (-1, 6), (3, 5)):
            p.poly([(x + dx - 2, y - 8.5), (x + dx + 0.5, y - 8.5 - h), (x + dx + 2.5, y - 8)])
    # globo
    with c.part(SCLERA, bevel=7.0, line=0.0) as p:
        p.ell(x, y, 11.2 * sq, 11.0 / sq)
    with c.part(VEIN, bevel=0.5) as p:
        p.limb((x - 9, y - 2), (x - 4, y - 1), 0.4, 0.3)
        p.limb((x - 4, y - 1), (x - 2, y - 4), 0.35, 0.25)
        p.limb((x - 6, y + 4), (x - 2, y + 3), 0.4, 0.3)
        p.limb((x - 1, y - 9.5), (x + 1, y - 6), 0.35, 0.25)
    # iris y pupila
    lx = x + P['look']
    with c.part(IRIS, bevel=4.5) as p:
        p.ell(lx + 1.5, y + 0.5, 5.9 * 0.8, 6.0)
    d = P['dil']
    with c.part(PUPIL, bevel=1.0) as p:
        p.ell(lx + 2.0, y + 0.5, 1.1 + 1.5 * d, 4.0 + 0.8 * d)
    with c.part(VEYE, bevel=0.5) as p:
        p.ell(lx + 3.5, y - 2.2, 0.9)
    c.glow(lx + 1.5, y + 0.5, 7, VGLOW, 0.3 + 0.5 * P['glow'])
    # parpado
    with c.part(FLESHV, line=0.4, bevel=1.4) as p:
        lid = P['lid']
        p.poly([(x - 10.5, y - 3), (x - 6, y - 9.5), (x + 2, y - 11.2), (x + 9.5, y - 8.5), (x + 11, y - 5 + lid * 4), (x + 5, y - 7 + lid * 5), (x - 2, y - 7.8 + lid * 4), (x - 7, y - 5.5 + lid * 2)])
    # orbe cargando
    if P['orb'] > 0.05:
        r = 1.5 + 3.5 * P['orb']
        ox, oy = lx + 7 + P['orb'] * 2, y + 0.5
        with c.part(IRIS, bevel=2.5) as p:
            p.ell(ox, oy, r)
        with c.part(VEYE, bevel=1.5) as p:
            p.ell(ox, oy, r * 0.5)
        c.glow(ox, oy, r + 4, VGLOW, 0.4)
        for q in range(4):
            ang = q * 1.57 + ph
            c.dotw(ox + math.cos(ang) * (r + 3), oy + math.sin(ang) * (r + 3), '#e0b0ff')


def draw_ojo(c, a, i, n):
    if a == 'death':
        return death_ojo(c, i, n)
    P = ojo_pose(a, i, n)
    ojo_body(c, P)
    if P['flash']:
        c.flash(WHITE, P['flash'])


def _p_tent(c):
    with c.part(FLESHV, line=0.4, bevel=1.4) as p:
        p.tube([(-5, 0), (-2, 1.2), (2, -0.5), (5, 0.8)], 2.0, 0.6)


def _p_lid(c):
    with c.part(SCLERA, bevel=2.0) as p:
        p.ell(0, 0, 4.4, 3.4)
    with c.part(IRIS, bevel=2) as p:
        p.ell(1, 0.5, 2.0, 2.4)


def death_ojo(c, i, n):
    if i == 0:
        ojo_body(c, ojo_pose('hurt', 0, 2))
        c.flash(WHITE, 0.5)
        return
    u = i / (n - 1)
    import random
    rnd = random.Random(15)
    if u < 0.4:
        P = ojo_pose('hurt', 1, 2)
        P['squash'] = 1.0 + u * 0.8
        P['dil'] = 2.0
        P['glow'] = 1.0
        ojo_body(c, P)
        c.flash('#e0a0ff', 0.2 + u * 1.2)
    else:
        v = (u - 0.4) / 0.6
        for q in range(10):
            ang = q * 0.63
            r0 = 3 + v * 16
            fx, fy = math.cos(ang) * r0 * 1.2, -21 + math.sin(ang) * r0
            if fy < -2:
                s_ = max(0.5, 3.0 * (1 - v))
                with c.part(ICHOR if q % 2 else IRIS, bevel=1.2) as p:
                    p.ell(fx, fy, s_ + 0.5, s_)
    items = [dict(fn=_p_lid, x=1, y=-21, r=3.5, vx=2, vy=-8, spin=3, rest=0.2, bounce=0.25),
             dict(fn=_p_tent, x=-4, y=-12, r=2, vx=-5, vy=-4, spin=5, rest=0.1),
             dict(fn=_p_tent, x=2, y=-12, r=2, vx=5, vy=-5, spin=-5, rest=-0.1),
             dict(fn=_p_tent, x=-1, y=-14, r=2, vx=0, vy=-7, spin=4, rest=3.1)]
    for d_ in items:
        d_['vx'] *= 0.6; d_['vy'] *= 0.65
    b = Bits(items, seed=2, T=0.75, g=1.5)
    if u > 0.3:
        draw_bits(c, b, (u - 0.3) / 0.7)
    if u > 0.45:
        w = min(1, (u - 0.45) / 0.45)
        with c.part(ICHOR, bevel=0.9) as p:
            p.ell(0, -0.9, 3 + 11 * w, 0.9 + 0.5 * w)
    if 0.3 < u < 0.95:
        for q in range(8):
            c.dotw(-8 + q * 2.4 + (q - 4) * u * 2, -10 - u * 12 - (q % 3) * 3, '#e0b0ff' if q % 2 else VGLOW)


# ------------------------------------------------------------------ FANTASMA
def fan_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(x=3.0, y=-22 + 1.4 * s, ph=t, wing=s, pitch=0.1, claw=0.0, eye=0.4, jaw=0.5, flash=0.0, trail=0.0)
    if a == 'walk':
        P.update(wing=s, pitch=0.2, y=-22 + 2 * math.sin(2 * math.pi * t), x=3)
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(wing=lerp(0.2, 1.2, w) + 0.2 * math.sin(i * 3), pitch=lerp(0.1, -0.7, w), y=-22 - 4 * w, x=lerp(3, -1, w), eye=w, jaw=2 * w, claw=w * 0.3)
    elif a == 'attack':
        P.update(wing=[1.1, -1.2, -0.8, -0.2, 0.4, 0.6][i], pitch=[-0.7, 0.6, 0.9, 0.7, 0.35, 0.15][i], y=-22 + [-4, 4, 8, 8, 3, 0][i], x=[-1, 6, 10, 9, 5, 3][i],
                 claw=[0.2, 1.0, 1.0, 1.0, 0.5, 0.0][i], eye=1.0, jaw=3, trail=[0, 0.7, 1.0, 0.8, 0.3, 0][i])
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(x=3 + rx, pitch=-0.4 if i == 0 else -0.15, flash=fl, wing=-1.0 if i == 0 else 0.3, eye=0.8, jaw=3)
    return P


def fantasma_body(c, P, solid=1.0):
    x, y, w, pit = P['x'], P['y'], P['wing'], P['pitch']
    ph = P['ph'] * 6.283
    with c.at(x, y, pit):
        # ala lejana
        for (far, m) in ((True, GHOST_W), (False, GHOST)):
            ang = -0.35 - 1.1 * w if far else 0.1 - 1.0 * w
            sx_, sy_ = -2.5 + (1 if far else 0), -4
            bx = sx_ - 3 + (4 if far else 0)
            tip = (sx_ + 14 * math.cos(ang + 3.14) * 0.5 - 5 + (3 if far else 0), sy_ - 15 * (0.55 + 0.45 * w) if True else 0)
            tip = (sx_ - 3 - (4 if not far else 0) * (1 - 0.4 * w), sy_ - 7 - 14 * (0.5 + 0.5 * w) + (4 if far else 0))
            f2 = (tip[0] - 11, tip[1] + 8 + 3 * w)
            f3 = (tip[0] - 8, tip[1] + 16)
            f4 = (sx_ - 5, sy_ + 6)
            def fade(lx, ly, bx=x, by=y):
                return np.clip(1.45 - np.hypot(lx - bx, ly - (by - 6)) / 28.0 * 0.6, 0.62, 1) * solid
            with c.part(m, fade=fade, bevel=1.8, line=0.0) as p:
                p.poly([(sx_, sy_), (tip[0] + 2, tip[1]), (tip[0] - 1.5, tip[1] + 3.5), (f2[0] + 2, f2[1] - 2), (f2[0], f2[1] + 1.5), (f3[0] + 2, f3[1] - 2.0), (f3[0] - 1, f3[1] + 2), (f4[0], f4[1]), (sx_ + 2, sy_ + 4)])
            with c.part(BONEV, bevel=0.6) as p:
                p.tube([(sx_, sy_), (tip[0] + 1, tip[1])], 0.9, 0.5)
                p.tube([(sx_, sy_ + 1), (f2[0] + 1, f2[1] - 1)], 0.7, 0.4)
                p.tube([(sx_, sy_ + 2), (f3[0] + 1, f3[1] - 1)], 0.6, 0.35)
            if far:
                # cuerpo entre ala lejana y cercana
                tail = []
                for k in range(7):
                    u = k / 6
                    tail.append((-4 - u * 13 + 2 * math.sin(ph + u * 3), 2 + u * 3 + 1.5 * math.sin(ph + u * 3 + 1) * u))
                def tfade(lx, ly, x0=x):
                    return np.clip(1.25 - (x0 - lx) / 22.0, 0, 1) * solid
                with c.part(GHOST, fade=tfade, bevel=3.0) as p:
                    p.tube([(4, 0)] + tail, 5.0, 0.8)
                with c.part(GHOST, fade=lambda lx, ly: solid, bevel=3.0) as p:
                    p.ell(-1, 1, 6.4, 5.2)
                # costillas fantasmales
                with c.part(BONEV, bevel=0.5) as p:
                    for k in range(3):
                        p.limb((-4 + k * 2.6, -1.5), (-3 + k * 2.6, 4.5), 0.5, 0.35)
        # brazos con garras
        cl = P['claw']
        for (dx, dyy, m) in ((1.0, 0, GHOST_W), (3.0, 1.5, GHOST)):
            hnd = (6 + dx + 5 * cl, 6 + dyy + 2.5 * cl)
            with c.part(m, line=0.0, bevel=1.4) as p:
                p.limb((2 + dx, 3), hnd, 1.8, 1.0)
            with c.part(BONEV, bevel=0.5) as p:
                for q in (-1, 0, 1):
                    p.limb(hnd, (hnd[0] + 3.2, hnd[1] + 1.5 + q * 1.4), 0.5, 0.2)
        # craneo
        with c.at(6, -3.5, -pit * 0.5):
            with c.part(BONEV, line=0.5, bevel=2.2) as p:
                p.ell(0, 0, 5.4, 4.8)
                p.poly([(-1.5, 2.5), (5.2, 2.4 + 0.2), (5.4, 4.6 + P['jaw'] * 0.8), (0, 5.2 + P['jaw'] * 0.8)])
            with c.part(DARK) as p:
                p.ell(2.8, -0.6, 1.9, 1.7)
                p.ell(-0.4, -0.8, 1.5, 1.5)
                p.poly([(3.6, 2.6), (5.6, 2.8), (5.6, 3.4 + P['jaw'] * 0.6), (3.6, 3.2 + P['jaw'] * 0.5)])
            with c.part(VEYE) as p:
                e = P['eye']
                p.ell(3.0, -0.6, 1.0 + 0.3 * e, 1.0 + 0.3 * e)
                p.ell(-0.3, -0.8, 0.8, 0.8)
            c.glow(3, -0.6, 4.5, VGLOW, 0.4 + 0.5 * P['eye'])
            with c.part(GHOST_W, bevel=1.0) as p:     # cuernitos rasgados
                p.poly([(-2.5, -4), (-5.5, -8), (-1, -5)])
                p.poly([(0.8, -4.5), (0, -9.5), (2.5, -4.2)])


def draw_fantasma(c, a, i, n):
    if a == 'death':
        return death_fantasma(c, i, n)
    P = fan_pose(a, i, n)
    fantasma_body(c, P)
    if P['flash']:
        c.flash(WHITE, P['flash'])
    if P['trail'] > 0:
        # estela de picada
        with c.part(Mat(ramp=['#6a58b8', '#a898ec', '#e8e0ff'], emi=True, nooutline=True, bevel=1.0, dith=0.3),
                    fade=lambda lx, ly: np.clip((lx - (P['x'] - 14)) / 12, 0, 1) * 0.8, bevel=1.0) as p:
            p.poly([(P['x'] - 14, P['y'] - 10), (P['x'] + 2, P['y'] - 5), (P['x'] + 2, P['y'] - 2), (P['x'] - 14, P['y'] - 4)])


def _p_skull_g(c):
    with c.part(BONEV, line=0.5, bevel=2.2) as p:
        p.ell(0, 0, 5.4, 4.8)
        p.poly([(-1.5, 2.5), (5.2, 2.6), (5.4, 5.4), (0, 5.2)])
    with c.part(DARK) as p:
        p.ell(2.8, -0.6, 1.9, 1.7); p.ell(-0.4, -0.8, 1.5, 1.5)


def death_fantasma(c, i, n):
    if i == 0:
        fantasma_body(c, fan_pose('hurt', 0, 2))
        c.flash(WHITE, 0.5)
        return
    u = i / (n - 1)
    P = fan_pose('hurt', 1, 2)
    P['y'] = -22 + 8 * u
    P['wing'] = kf(u, [(0, -1), (1, 1.4)])
    P['pitch'] = kf(u, [(0, -0.2), (1, 0.4)])
    sol = max(0.0, 1.0 - u * 1.25)
    if sol > 0.02:
        fantasma_body(c, P, solid=sol)
    c.dissolve(min(0.95, u * 1.2), up=0.5, seed=3) if False else None
    # el craneo cae y queda
    items = [dict(fn=_p_skull_g, x=5, y=-26 + 8 * u, r=4.8, vx=1, vy=-3, spin=2, rest=0.3, bounce=0.2)]
    b = Bits(items, seed=2, T=0.7, g=1.4)
    if u > 0.45:
        draw_bits(c, b, (u - 0.45) / 0.55)
    # nubes de ectoplasma y motas
    for q in range(10):
        if u < 0.98:
            c.dotw(-10 + q * 2.6 + math.sin(q * 2 + i) * 2, -14 - u * 14 - (q % 4) * 3, '#e8e0ff' if q % 2 else VGLOW)
    if u > 0.4:
        w = min(1, (u - 0.4) / 0.5)
        with c.part(GHOST_W, bevel=0.8, fade=lambda lx, ly: 0.75) as p:
            p.ell(0, -0.9, 2 + 8 * w, 0.8 + 0.5 * w)


def sheet_acechador():
    return enemy_sheet('en_acechador', (48, 48), (24, 46), (18, 24), draw_acechador, (12, 6, 24),
                       STD(6, hit=[2, 3], box=[2, -26, 24, 26], idle=6, walk=8, wfps=14, fa=17))


def sheet_ojo_vacio():
    return enemy_sheet('en_ojo_vacio', (48, 48), (24, 46), (20, 24), draw_ojo, (14, 6, 28),
                       STD(6, rel=2, muz=[16, -22], walk=6, wfps=9, fa=13))


def sheet_fantasma():
    return enemy_sheet('en_fantasma', (48, 48), (24, 46), (22, 18), draw_fantasma, (18, 12, 44),
                       STD(6, hit=[1, 3], box=[0, -30, 26, 30], idle=6, walk=6, wfps=10, fa=15, death=8))


SHEETS = [sheet_acechador, sheet_ojo_vacio, sheet_fantasma]
