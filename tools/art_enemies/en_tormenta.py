from common import *
from humanoid import human
from en_catacumbas import enemy_sheet, STD, DARK, WHITE

CU = Mat(ramp=['#0a1a1c', '#18383c', '#2c6664', '#4a9c8c', '#8ad4b8'], bevel=1.6, tex=0.4, seed=91, bias=0.4)
CU_B = Mat(ramp=['#06100f', '#0e2426', '#1c4244', '#2e6a66', '#4a9488'], bevel=1.6, tex=0.4, seed=92)
COPPER = Mat(ramp=['#2a1210', '#5a2a1c', '#9a5230', '#d08a4c', '#f4c888'], bevel=1.4, tex=0.3, seed=93)
LEAT = Mat(ramp=['#120c0c', '#2a1c18', '#48322a', '#6e4e3a', '#94705a'], bevel=1.8, tex=0.35, seed=94)
LEAT_D = Mat(ramp=['#0a0606', '#1c1210', '#32221c', '#4e362a', '#6a4c3a'], bevel=1.8, tex=0.35, seed=95)
CLOTH_T = Mat(ramp=['#0c1214', '#1a2a2c', '#2e4648', '#4a6a68', '#7a9c94'], bevel=1.8, tex=0.3, seed=96)
SKIN_H = Mat(ramp=['#2a1a18', '#5a3a30', '#8c604a', '#bc8a68', '#e0b490'], bevel=1.4, seed=97)
ELEC = '#4FA8FF'
SPARK = '#E8F8FF'
EL_C = Mat(ramp=['#2a68c8', '#4fa8ff', '#a8e0ff', '#ffffff'], emi=True, nooutline=True, bevel=1.0, dith=0.1)
CLOUD = Mat(ramp=['#10182a', '#202e4c', '#36507a', '#5a7eae', '#8cb0d8'], bevel=3.0, dith=0.5, bias=0.5, outcol='#0c1224')
CLOUD_B = Mat(ramp=['#0a1020', '#162038', '#263a5c', '#3e5a88'], bevel=2.6, dith=0.4, outcol='#080c1c')
HORN = Mat(ramp=['#2a2418', '#5a4e34', '#968660', '#cfc296', '#f4ecc8'], bevel=1.6, tex=0.15, seed=98)
HIDE = Mat(ramp=['#0e1214', '#1c262a', '#2e3c42', '#485a62', '#6c8088'], bevel=3.0, tex=0.4, seed=99, bias=0.45)
HIDE_B = Mat(ramp=['#080c0e', '#121a1e', '#202c32', '#34444c', '#506068'], bevel=3.0, tex=0.4, seed=100)


def bolt_path(p0, p1, seed, n=6, amp=2.5):
    import random
    r = random.Random(seed)
    pts = [p0]
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    for k in range(1, n):
        u = k / n
        j = r.uniform(-amp, amp)
        pts.append((p0[0] + dx * u + nx * j, p0[1] + dy * u + ny * j))
    pts.append(p1)
    return pts


def draw_bolt(c, p0, p1, seed, w=1.0, amp=2.5, n=6):
    pts = bolt_path(p0, p1, seed, n, amp)
    with c.part(EL_C, bevel=w * 0.8) as p:
        p.tube(pts, w, w * 0.8)
    return pts


# ------------------------------------------------------------------ SAQUEADOR
def saq_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(hx=-4.0, dy=0.6 * s, lean=0.06, ph=t, walk=False, stride=0, lift=0, rear=(-0.5, -15), front=(8, -16), head=0.0, aim=-0.2, flash=0.0,
             glow=0.0, loaded=True, recoil=0.0)
    if a == 'idle':
        P['front'] = (7.5, -14.5 + 0.4 * s); P['aim'] = 0.35 + 0.02 * s; P['rear'] = (-0.5, -13.5 + 0.4 * s)
    elif a == 'walk':
        P.update(walk=True, stride=4.8, lift=2.6, dy=-0.9 * abs(math.sin(2 * math.pi * t)) + 0.4, lean=0.16, hx=-3, aim=0.45)
        P['front'] = (7.5, -14.5 + 0.7 * s); P['rear'] = (-0.5, -13.5 + 0.7 * s)
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(lean=lerp(0.06, -0.06, w), hx=lerp(-4, -5, w), dy=lerp(0, 1.4, w), aim=lerp(0.35, -0.03, w), glow=w, head=-0.05 * w)
        P['front'] = (lerp(7.5, 11.5, w), lerp(-14.5, -20, w)); P['rear'] = (lerp(-0.5, 3.0, w), lerp(-13.5, -19.4, w))
        P['feet'] = (lerp(-3.5, -6, w), 0), (lerp(3.5, 5, w), 0)
    elif a == 'attack':
        P.update(lean=[-0.06, -0.06, -0.2, -0.1, 0.0][i], hx=[-5, -5, -7.5, -6.5, -5][i], dy=[1.4, 1.4, 0.8, 1.2, 0.8][i], aim=[-0.03, -0.03, -0.22, 0.0, 0.2][i],
                 glow=[1.0, 1.0, 0.0, 0, 0][i], loaded=i < 2, recoil=[0, 0, 1.0, 0.5, 0.2][i])
        P['front'] = [(11.5, -20), (11.5, -20.2), (10, -21.5), (10.5, -20.5), (10, -19)][i]
        P['rear'] = [(3.0, -19.4), (3.0, -19.6), (1.0, -20.5), (1.8, -19.5), (1.6, -18)][i]
        P['feet'] = (-6, 0), (5, 0)
        P['head'] = [-0.05, -0.05, -0.2, -0.1, 0][i]
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(hx=-4 + rx, lean=ln, flash=fl, head=-0.3 if i == 0 else -0.1, aim=0.9)
        P['front'] = (3, -10) if i == 0 else (6, -13); P['rear'] = (-2, -12) if i == 0 else (-1, -13)
    return P


M_SAQ = dict(skin=SKIN_H, cloth=LEAT, cloth_d=LEAT_D, boot=Mat(ramp=['#0a0808', '#1c1412', '#32241e', '#4a342a'], bevel=1.2, tex=0.3, seed=2),
             boot_d=Mat(ramp=['#060404', '#120c0a', '#221812', '#34241c'], bevel=1.2, seed=3), vest=CU_B, vest_d=CU)


def saq_head(c, x, y, ang, P):
    with c.at(x, y, ang):
        with c.part(SKIN_H, line=0.5, bevel=1.8) as p:
            p.ell(0, 0, 4.0, 4.3)
        with c.part(CLOTH_T, line=0.5, bevel=1.6) as p:       # mascara / bufanda
            p.poly([(-3.6, 0.8), (4.2, 0.6), (4.4, 4.2), (-1, 5.2), (-4, 3.6)])
        with c.part(DARK) as p:
            p.rect(0.6, -1.4, 4.2, -0.2)
        with c.part(EL_C, bevel=0.5) as p:
            p.rect(1.6, -1.1, 3.6, -0.4)
        c.glow(2.6, -0.8, 2.4, ELEC, 0.3 + 0.3 * P['glow'])
        with c.part(LEAT, line=0.5, bevel=2.0) as p:          # capucha de cuero
            p.poly([(-5.5, 4), (-6.2, -2), (-3.5, -6), (1.5, -6.6), (4.5, -4.5), (2, -2.8), (-1, -2), (-2.8, 1), (-3, 5)])
        with c.part(COPPER, bevel=0.6) as p:
            p.ell(-1.2, -5.3, 1.0)


def saq_weapon(c, P, rear, front):
    aim = P['aim']
    d = (math.cos(-aim), math.sin(-aim)) if False else (math.cos(aim * -1 + 0), math.sin(aim * -1 + 0))
    # direccion: de mano trasera a delantera
    dx, dy = front[0] - rear[0], front[1] - rear[1]
    L = math.hypot(dx, dy) or 1
    d = (dx / L, dy / L); nr = (-d[1], d[0])
    rc = P['recoil']
    base = (rear[0] - d[0] * 3 - d[0] * rc, rear[1] - d[1] * 3 - d[1] * rc)
    tip = (front[0] + d[0] * 4.8, front[1] + d[1] * 4.8)
    with c.part(LEAT, line=0.4, bevel=1.2) as p:       # culata
        p.poly([(base[0] + nr[0] * 1.6, base[1] + nr[1] * 1.6), (tip[0] + nr[0] * 0.8, tip[1] + nr[1] * 0.8), (tip[0] - nr[0] * 0.8, tip[1] - nr[1] * 0.8),
                (base[0] - nr[0] * 2.4, base[1] - nr[1] * 2.4)])
    with c.part(COPPER, line=0.4, bevel=0.8) as p:
        p.limb((tip[0] - d[0] * 3, tip[1] - d[1] * 3), tip, 0.9)
    # arco (palas) de cobre/turquesa
    bx, by = tip[0] - d[0] * 3.5, tip[1] - d[1] * 3.5
    flex = 0.0 if not P['loaded'] else 1.0
    t0 = (bx + nr[0] * 8.5 + d[0] * (1.5 - 3 * flex), by + nr[1] * 8.5 + d[1] * (1.5 - 3 * flex))
    t1 = (bx - nr[0] * 8.5 + d[0] * (1.5 - 3 * flex), by - nr[1] * 8.5 + d[1] * (1.5 - 3 * flex))
    mid0 = (bx + nr[0] * 4.5 + d[0] * 2.2, by + nr[1] * 4.5 + d[1] * 2.2)
    mid1 = (bx - nr[0] * 4.5 + d[0] * 2.2, by - nr[1] * 4.5 + d[1] * 2.2)
    with c.part(CU, line=0.4, bevel=1.0) as p:
        p.tube([(bx, by), mid0, t0], 1.1, 0.7); p.tube([(bx, by), mid1, t1], 1.1, 0.7)
    with c.part(Mat(ramp=['#8a8a94', '#c8c8c4', '#f0ecd8'], bevel=0.5, dith=0.0)) as p:
        sp = (base[0] + d[0] * (3.0 if flex else 6.5), base[1] + d[1] * (3.0 if flex else 6.5))
        sp = (bx - d[0] * (3.5 if flex else -3.0), by - d[1] * (3.5 if flex else -3.0))
        p.line_(t0, sp, 1.0); p.line_(sp, t1, 1.0)
    if P['loaded']:
        with c.part(COPPER, bevel=0.6) as p:
            p.limb((bx - d[0] * 3.0, by - d[1] * 3.0), (tip[0] + d[0] * 3.4, tip[1] + d[1] * 3.4), 0.7)
        with c.part(EL_C) as p:
            e0 = (tip[0] + d[0] * 3.4, tip[1] + d[1] * 3.4)
            p.poly([(e0[0] + d[0] * 2.4, e0[1] + d[1] * 2.4), (e0[0] + nr[0] * 1.1, e0[1] + nr[1] * 1.1), (e0[0] - nr[0] * 1.1, e0[1] - nr[1] * 1.1)])
        c.glow(tip[0] + d[0] * 5, tip[1] + d[1] * 5, 4.5, ELEC, 0.3 + 0.6 * P['glow'])
    if P['recoil'] > 0.9:
        for q in range(5):
            c.dotw(tip[0] + d[0] * (6 + q * 2.2), tip[1] + d[1] * (6 + q * 2.2) + (q % 2) - 0.5, SPARK if q % 2 else ELEC)


def saq_back(c, hip, neck, sho, lean, ph):
    sw = math.sin(ph * 6.283)
    with c.part(LEAT_D, line=0.5, bevel=2.0) as p:     # capa
        p.poly([(neck[0] - 3, neck[1] - 1), (neck[0] + 1.5, neck[1] - 1), (hip[0], hip[1] + 6 + sw * 0.8), (hip[0] - 9 - lean * 4 + sw, hip[1] + 8), (neck[0] - 8, neck[1] + 3)])
    with c.part(CU, bevel=0.6) as p:
        p.ell(neck[0] - 1.8, neck[1] + 0.4, 1.3)


def saq_torso(c, P):
    with c.part(LEAT_D, line=0.4, bevel=1.0) as p:
        p.poly([(-5, 0.2), (5, -0.2), (5, 1.8), (-5, 2.2)])
    with c.part(COPPER, bevel=0.6) as p:
        p.rect(-0.8, -0.2, 1.0, 2.0)
        p.ell(-3.4, -6.8, 1.0); p.ell(-3.4, -3.8, 1.0)
    with c.part(CU, bevel=0.8, line=0.3) as p:
        p.poly([(-4, -11.4), (5, -11.8), (4.4, -8.6), (-4.8, -8.4)])


def draw_saqueador(c, a, i, n):
    if a == 'death':
        return death_saqueador(c, i, n)
    P = saq_pose(a, i, n)
    human(c, P, a, M_SAQ, saq_head, saq_weapon, back_fn=saq_back, torso_extra=saq_torso)
    if P['flash']:
        c.flash(WHITE, P['flash'])


def _p_xbow(c):
    with c.part(LEAT, line=0.4, bevel=1.2) as p:
        p.poly([(-7, -1.6), (7, -0.8), (7, 0.8), (-7, 2.4)])
    with c.part(CU, line=0.4, bevel=1.0) as p:
        p.tube([(3, 0), (5, -4), (3, -8)], 1.1, 0.7); p.tube([(3, 0), (5, 4), (3, 8)], 1.1, 0.7)


def death_saqueador(c, i, n):
    if i == 0:
        human(c, saq_pose('hurt', 0, 2), 'hurt', M_SAQ, saq_head, saq_weapon, back_fn=saq_back, torso_extra=saq_torso)
        c.flash(WHITE, 0.45)
        return
    u = i / (n - 1)
    P = saq_pose('hurt', 1, 2)
    P['loaded'] = False
    P['front'] = (kf(u, [(0, 6), (1, 2)]), kf(u, [(0, -13), (1, -6)]))
    P['rear'] = (-1, kf(u, [(0, -13), (1, -9)]))
    ang = kf(u, [(0, 0), (0.3, -0.35), (0.65, -1.2), (1.0, -1.57)])
    drop = kf(u, [(0, 0), (0.4, 1.5), (1, 2.5)])
    P['lean'] = kf(u, [(0, -0.14), (1, -0.1)])
    P['head'] = kf(u, [(0, -0.1), (1, 0.15)])
    P['hx'] = 0
    P['feet'] = (kf(u, [(0, -3), (1, -6)]), 0), (kf(u, [(0, 3), (1, 5)]), 0)
    with c.at(2 + 4 * u, 0 - drop * 0.0, ang):
        human(c, P, 'idle', M_SAQ, saq_head, lambda cc, PP, r, f: None, back_fn=saq_back, torso_extra=saq_torso)
    items = [dict(fn=_p_xbow, x=9, y=-20, r=3, vx=6, vy=-7, spin=6, rest=0.2, bounce=0.35)]
    for d_ in items:
        d_['vx'] *= 0.6; d_['vy'] *= 0.7
    b = Bits(items, seed=3, T=0.75, g=1.6)
    draw_bits(c, b, u)
    if u > 0.4:
        for q in range(5):
            if u < 0.9:
                c.dotw(-12 + q * 6, -3 - (q % 2) * 2, '#8a6a4a')


# ------------------------------------------------------------------ VEX DE TORMENTA
def vt_pose(a, i, n):
    t = i / n
    P = dict(x=-1.0, y=-21 + 1.5 * math.sin(2 * math.pi * t), ph=t, lean=0.15, arc=0.0, flash=0.0, eye=0.5, seed=i, crown=1.0, spread=1.0, ext=0.0)
    if a == 'walk':
        P.update(lean=0.35, x=0, y=-21 + 1.8 * math.sin(2 * math.pi * t), spread=1.2)
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(lean=lerp(0.15, -0.4, w), x=lerp(-1, -6, w), y=-21 + 2 * w, eye=1.0, crown=1.0 + w, spread=lerp(1, 0.4, w), ext=-w * 2)
    elif a == 'attack':
        k = i / (n - 1)
        P.update(lean=kf(k, [(0, -0.4), (0.2, 0.7), (0.4, 0.9), (1, 0.2)]), x=kf(k, [(0, -6), (0.2, 3), (0.4, 9), (0.7, 7), (1, 1)]),
                 y=-21 + kf(k, [(0, 2), (0.4, 3), (1, 0)]), eye=1.0, arc=1.0 if 0.15 < k < 0.75 else 0.0, spread=1.5, crown=1.6, ext=kf(k, [(0, -2), (0.4, 6), (1, 0)]))
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(x=-1 + rx, lean=ln, flash=fl, eye=0.2, y=-21 - 2 * (1 - i), spread=0.6)
    return P


def vextorm_body(c, P):
    x, y, lean = P['x'], P['y'], P['lean']
    ph = P['ph'] * 6.283
    # cola de rayo zigzag
    tp = [(x - 2, y + 4)]
    for k in range(1, 6):
        tp.append((x - 2 - k * 1.4 - lean * 3 + (3 if k % 2 else -3) * (0.6 + 0.4 * math.sin(ph + k)), y + 4 + k * 3.4))
    with c.part(EL_C, bevel=1.0) as p:
        p.tube(tp, 2.6, 0.6)
    # nube cuerpo
    with c.at(x, y, lean * 0.4):
        with c.part(CLOUD_B, bevel=3.0) as p:
            p.ell(-3.5, 1.5, 6.0, 5.0); p.ell(3.5, 2.5, 5.0, 4.2)
        with c.part(CLOUD, bevel=3.5) as p:
            p.ell(0, 0, 8.0, 7.0); p.ell(-5.5, -1.5, 4.4, 4.0); p.ell(5.2, -2.0, 4.0, 3.6); p.ell(0.5, 4.5, 6.2, 3.4)
        with c.part(CLOUD_B, bevel=1.5) as p:
            p.ell(-2, 3.5, 4.5, 1.8)
        # relampago interior
        with c.part(EL_C, bevel=0.6) as p:
            p.tube([(-5, 3.5), (-3, 1.5), (-3.8, 0.2), (-1.6, -1.6)], 0.7, 0.5)
        # ojos
        with c.part(DARK) as p:
            p.poly([(0.2, -2.8), (6.8, -3.6), (6.8, 0.2), (0.6, 0.8)])
        with c.part(EL_C, bevel=0.5) as p:
            e = P['eye']
            p.poly([(1.4, -2.2), (3.4, -2.5), (3.2, -0.6), (1.6, -0.4)])
            p.poly([(4.2, -2.6), (6.2, -3.0), (6.2, -1.0), (4.4, -0.8)])
        c.glow(4, -1.5, 4.2, ELEC, 0.4 + 0.5 * e)
    # corona de chispas
    for k in range(5):
        ang = -2.4 + k * 0.55
        r0 = 8.5
        bx_, by_ = x + math.cos(ang) * r0 * 0.8, y - 3 + math.sin(ang) * r0
        L = (3 + 2.5 * (k % 2)) * P['crown']
        pts = bolt_path((bx_, by_), (bx_ + math.cos(ang) * L, by_ + math.sin(ang) * L), int(ph * 2 + k) % 5 + k, 3, 1.2)
        with c.part(EL_C, bevel=0.6) as p:
            p.tube(pts, 0.8, 0.4)
    # brazos de rayo
    for (dx, sd) in ((5.5, 1), (2, 2)):
        pts = bolt_path((x + dx, y + 2), (x + dx + 6 * P['spread'] + P['ext'] * 0.5, y + 4 + (3 if sd == 1 else 5)), P['seed'] * 3 + sd, 4, 1.8)
        with c.part(EL_C, bevel=0.6) as p:
            p.tube(pts, 0.9, 0.5)
    if P['arc']:
        a0 = (x + 8, y + 3)
        a1 = (x + 21, y + 1)
        pts = bolt_path(a0, a1, P['seed'] + 7, 6, 3.2)
        with c.part(EL_C, bevel=0.8) as p:
            p.tube(pts, 1.0, 0.8)
        pts2 = bolt_path(a0, (a1[0] - 2, a1[1] + 6), P['seed'] + 11, 5, 2.5)
        with c.part(EL_C, bevel=0.6) as p:
            p.tube(pts2, 0.7, 0.4)
        c.glow(a1[0], a1[1], 5, ELEC, 0.6)


def draw_vextorm(c, a, i, n):
    if a == 'death':
        return death_vextorm(c, i, n)
    P = vt_pose(a, i, n)
    vextorm_body(c, P)
    if P['flash']:
        c.flash(WHITE, P['flash'])


def death_vextorm(c, i, n):
    if i == 0:
        vextorm_body(c, vt_pose('hurt', 0, 2))
        c.flash(WHITE, 0.6)
        return
    u = i / (n - 1)
    if u < 0.35:
        P = vt_pose('hurt', 1, 2)
        P['crown'] = 1 + u * 6; P['eye'] = 1; P['seed'] = i * 5
        vextorm_body(c, P)
        c.flash('#c0e8ff', 0.3 + u)
    else:
        v = (u - 0.35) / 0.65
        for q in range(9):
            ang = q * 0.7 + 0.1
            r0 = 4 + v * 18
            p0 = (-1 + math.cos(ang) * 3, -21 + math.sin(ang) * 3)
            p1 = (-1 + math.cos(ang) * r0 * 1.2, -21 + math.sin(ang) * r0)
            if p1[1] < -1.5 and v < 0.9:
                pts = bolt_path(p0, p1, q + i * 3, 4, 1.8)
                with c.part(EL_C, bevel=0.5) as p:
                    p.tube(pts, 0.9 * (1 - v * 0.6), 0.3)
        with c.part(CLOUD_B, bevel=1.5) as p:
            p.ell(-1, -2.5 - 0.0, 4 + 5 * (1 - v) + 3, 1.8 + 1.0 * (1 - v))
        with c.part(CLOUD, bevel=1.2) as p:
            p.ell(-2, -3.0, 3 + 3 * (1 - v), 1.6)
    for q in range(8):
        c.dotw(-10 + q * 2.8 + math.sin(q + i) * 2, -18 - u * 8 * ((q % 3) - 1) - (q % 4) * 2, SPARK if q % 2 else ELEC)


# ------------------------------------------------------------------ BESTIA DE TORMENTA (64x64)
def bes_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(hx=0.0, dy=0.5 * s, ph=t, walk=False, head=0.0, down=0.0, eye=0.4, crackle=0.0, flash=0.0, paw=0.0, k=None, tail=s, snort=0.0, lunge=0.0)
    if a == 'walk':
        P.update(walk=True, dy=-1.2 * abs(math.sin(4 * math.pi * t)) + 0.3, head=0.1)
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(hx=lerp(0, -4, w), dy=lerp(0, 3, w), head=lerp(0, 0.5, w), eye=w, crackle=w, paw=w * (1 if i % 2 == 0 else 0.5) + 0.0, snort=w)
    elif a == 'attack':
        k = i / (n - 1)
        P.update(hx=kf(k, [(0, -4), (0.2, 4), (0.4, 10), (0.7, 9), (1, 3)]), dy=kf(k, [(0, 3), (0.4, 2), (1, 0)]), head=kf(k, [(0, 0.5), (0.2, 0.6), (0.5, 0.45), (1, 0.15)]),
                 eye=1.0, crackle=1.0 if k < 0.8 else 0.3, k=k, lunge=1.0 if k < 0.8 else 0.0)
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(hx=rx, head=-0.35 if i == 0 else -0.15, flash=fl * 0.9, eye=0.9, dy=-1 if i == 0 else 0)
    return P


def bestia_body(c, P, a='idle', plates=True):
    hx, dy, ph = P['hx'] - 6, P['dy'], P['ph']
    down = P['down']
    by = -24 + dy + 12 * down
    hipb, hipf = (hx - 16, by + 5), (hx + 12, by + 6)
    # patas
    def paw(hip, phase, m, front):
        if P['walk']:
            g = gait(phase % 1, 5.0, 3.4)
        elif a in ('windup', 'attack'):
            g = ((-7 if front else -5), 0) if a == 'windup' else ((6 if front else -6), 0)
            if a == 'windup' and front:
                g = (-3 - 6 * P['paw'] * (0.5 + 0.5 * math.sin(P['ph'] * 20)), -3 * P['paw'] * max(0, math.sin(P['ph'] * 20)))
        else:
            g = (0, 0)
        if down:
            g = ((-8 if front else -6) + (6 if hip is hipf else 0) * 0, 0)
        ft = (hip[0] + g[0] + (2 if front else -1) + 10 * down * (1 if front else -0.8), g[1])
        kn = ik2(hip, ft, 10, 9, bend=-1 if front else 1)
        with c.part(m, line=0.5, bevel=3.0) as p:
            p.limb(hip, kn, 5.0, 4.0); p.limb(kn, ft, 4.0, 3.0)
        with c.part(HORN if m is HIDE else HORN, line=0.4, bevel=1.0) as p:
            p.poly([(ft[0] - 3.4, ft[1] - 3.4), (ft[0] + 3.8, ft[1] - 3.2), (ft[0] + 4.4, ft[1] + 0.3), (ft[0] - 3.4, ft[1] + 0.3)])
    paw(hipb, ph + 0.5, HIDE_B, False)
    paw(hipf, ph, HIDE_B, True)
    # cola
    with c.part(HIDE_B, line=0.4, bevel=1.0) as p:
        p.tube([(hx - 24, by - 2), (hx - 29, by + 2 + P['tail'] * 2), (hx - 31, by + 8 + P['tail'] * 3)], 2.0, 0.8)
    with c.part(CU, bevel=0.8) as p:
        p.poly([(hx - 31, by + 6 + P['tail'] * 3), (hx - 28.5, by + 9 + P['tail'] * 3), (hx - 31.5, by + 12 + P['tail'] * 3)])
    # cuerpo
    with c.part(HIDE, line=0.5, bevel=5.0) as p:
        p.ell(hx - 3, by, 24, 13)
        p.ell(hx + 10, by - 1, 12, 11.5)
    with c.part(HIDE_B, bevel=2.0) as p:
        p.ell(hx - 5, by + 8, 16, 4)
    # patas cercanas
    paw(hipb, ph, HIDE, False)
    paw((hipf[0] + 2, hipf[1]), ph + 0.5, HIDE, True)
    # placas de armadura de cobre oxidado
    if plates:
        for k in range(4):
            px_ = hx - 19 + k * 8
            with c.part(CU, line=0.5, bevel=2.0) as p:
                p.poly([(px_ - 3.6, by - 7 + 2 * abs(k - 1.5) * 0.5), (px_ + 4.2, by - 8.6 + k * 0.2), (px_ + 4.8, by + 5.5), (px_ - 4, by + 5.5)])
            with c.part(COPPER, bevel=0.8) as p:
                p.ell(px_ + 0.4, by - 4.6, 1.0); p.ell(px_ + 0.4, by + 1.6, 1.0)
        with c.part(CU_B, line=0.4, bevel=1.4) as p:       # giba-escudo
            p.poly([(hx + 6, by - 8), (hx + 16, by - 11), (hx + 22, by - 5), (hx + 14, by - 3)])
        with c.part(EL_C, bevel=0.5) as p:
            p.limb((hx - 15, by - 6), (hx - 11, by - 3), 0.5); p.limb((hx - 3, by - 6.5), (hx + 1, by - 3), 0.5)
    # cabeza con cuernos
    hh = (hx + 21, by + 0.5 + 2 * P['head'] * 3)
    with c.at(hh[0], hh[1], P['head']):
        with c.part(HIDE, line=0.5, bevel=3.0) as p:
            p.poly([(-7, -8), (4, -8.5), (11, -3), (12, 3.5), (7, 8), (-4, 8.5), (-8, 3)])
        with c.part(CU, line=0.5, bevel=1.6) as p:     # frontal blindado
            p.poly([(-6, -8.6), (3.5, -9), (6, -2.4), (-2, -1.6), (-6.5, -3.4)])
        with c.part(DARK) as p:
            p.ell(5.0, 0.2, 1.7, 1.2)
            p.ell(10.5, 3.0, 0.8, 0.6)
        with c.part(EL_C, bevel=0.5) as p:
            e = P['eye']
            p.poly([(3.6, -1.4), (7.8, -0.4), (7.2, 1.4), (3.8, 0.8)])
        c.glow(5.8, 0.2, 4 + 1.5 * P['eye'], ELEC, 0.4 + 0.5 * P['eye'])
        with c.part(HORN, line=0.5, bevel=1.8) as p:    # cuernos curvos grandes
            p.tube([(2, -7.5), (8, -11), (14, -9.5), (19, -4.0)], 3.2, 1.0)
            p.tube([(-1, -7), (3, -12), (7, -12.5), (10, -9.5)], 2.4, 0.8)
        with c.part(HORN, line=0.4, bevel=1.2) as p:
            p.tube([(8, 6), (13, 9.0), (18, 8)], 1.9, 0.6)    # colmillo
        if P['snort'] > 0.4:
            for q in range(3):
                c.dotw(hh[0] + 12 + q * 3, hh[1] + 2 + (q % 2) * 2 - q, '#c8d8e0')
    if P['crackle'] > 0.1:
        hx0 = hh[0] + 5
        for k in range(3):
            pts = bolt_path((hx0 + k * 3, hh[1] - 10), (hx0 + 8 + k * 3, hh[1] - 10 - 2 * k), int(ph * 3) + k * 7 + int(P['crackle'] * 5), 3, 2.0)
            with c.part(EL_C, bevel=0.5) as p:
                p.tube(pts, 0.8, 0.5)
        c.glow(hx0 + 5, hh[1] - 10, 6, ELEC, 0.45 * P['crackle'])
    if P['lunge'] > 0.5:
        with c.part(EL_C, fade=lambda lx, ly: np.clip((lx - (hh[0] - 12)) / 12, 0, 1) * 0.8, bevel=0.6) as p:
            p.poly([(hh[0] - 16, hh[1] - 3), (hh[0] + 10, hh[1] + 1), (hh[0] + 10, hh[1] + 3), (hh[0] - 16, hh[1] + 5)])
    return hh


def draw_bestia(c, a, i, n):
    if a == 'death':
        return death_bestia(c, i, n)
    P = bes_pose(a, i, n)
    bestia_body(c, P, a)
    if P['flash']:
        c.flash(WHITE, P['flash'])
    if a == 'windup' and i == n - 1:
        c.flash(ELEC, 0.1)


def _p_plate(c):
    with c.part(CU, line=0.5, bevel=2.0) as p:
        p.poly([(-3.6, -7), (4.2, -8.6), (4.8, 5.5), (-4, 5.5)])
    with c.part(COPPER, bevel=0.8) as p:
        p.ell(0.4, -4.6, 1.0)


def _p_horn(c):
    with c.part(HORN, line=0.5, bevel=1.8) as p:
        p.tube([(-8, 0), (-3, -3), (3, -3.5), (8, 0)], 3.0, 0.9)


def death_bestia(c, i, n):
    if i == 0:
        bestia_body(c, bes_pose('hurt', 0, 2), 'hurt')
        c.flash(WHITE, 0.45)
        return
    u = i / (n - 1)
    P = bes_pose('hurt', 1, 2)
    P['walk'] = False
    P['down'] = sm(u * 1.3)
    P['head'] = kf(u, [(0, -0.15), (0.5, 0.2), (1, 0.55)])
    P['eye'] = 1 - u
    P['hx'] = kf(u, [(0, 0), (1, -3)])
    P['crackle'] = 0
    items = [dict(fn=_p_plate, x=-10, y=-30, r=6, vx=-6, vy=-8, spin=-4, rest=0.9, bounce=0.3),
             dict(fn=_p_plate, x=2, y=-31, r=6, vx=3, vy=-9, spin=4, rest=-1.0, bounce=0.3),
             dict(fn=_p_horn, x=24, y=-32, r=3, vx=8, vy=-8, spin=5, rest=0.1, bounce=0.35)]
    for d_ in items:
        d_['vx'] *= 0.6; d_['vy'] *= 0.7
    b = Bits(items, seed=3, T=0.75, g=2.4)
    bestia_body(c, P, 'hurt', plates=(u < 0.2))
    if u >= 0.2:
        draw_bits(c, b, (u - 0.2) / 0.8)
    for q in range(6):
        if 0.2 < u < 0.9:
            pts = bolt_path((-20 + q * 8, -20 - (q % 3) * 4), (-18 + q * 8, -26 - (q % 3) * 4), q + i, 2, 1.5)
            with c.part(EL_C, bevel=0.4) as p:
                p.tube(pts, 0.6, 0.4)
    if u > 0.4:
        for q in range(8):
            c.dotw(-26 + q * 7, -2 - (q % 3) * 2 - (u - 0.4) * 6, '#8a9aa0')


def sheet_saqueador():
    return enemy_sheet('en_saqueador', (48, 48), (24, 46), (12, 30), draw_saqueador, (12, 14, 16),
                       STD(5, rel=2, muz=[17, -22], fa=14))


def sheet_vex_tormenta():
    return enemy_sheet('en_vex_tormenta', (48, 48), (24, 46), (16, 22), draw_vextorm, (10, 14, 40),
                       STD(6, hit=[2, 3], box=[2, -28, 26, 20], idle=6, walk=6, wfps=14, fa=16, death=7))


def sheet_bestia_tormenta():
    return enemy_sheet('en_bestia_tormenta', (64, 64), (32, 62), (46, 36), draw_bestia, (8, 12, 14),
                       STD(6, hit=[1, 4], box=[8, -40, 30, 40], idle=6, walk=8, ifps=6, wfps=9, fa=12, death=8, dfps=8))


SHEETS = [sheet_saqueador, sheet_vex_tormenta, sheet_bestia_tormenta]
