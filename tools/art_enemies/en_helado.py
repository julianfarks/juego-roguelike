from common import *
from en_catacumbas import enemy_sheet, STD, DARK, WHITE

ICE = Mat(ramp=['#10204a', '#24468a', '#4a8cd0', '#8ad4f4', '#eafcff'], bevel=1.6, tex=0.15, seed=51, bias=0.5)
ICE_B = Mat(ramp=['#0c1a3c', '#1c3874', '#366cb0', '#6ab0e0', '#b8eaff'], bevel=1.6, seed=52)
ICEGLOW = Mat(ramp=['#3a9ad8', '#7ae0ff', '#c8f8ff', '#ffffff'], emi=True, nooutline=True, bevel=1.3, dith=0.15)
CRYS = Mat(ramp=['#1c3a8a', '#3c80d0', '#7ae0ff', '#d8faff', '#ffffff'], bevel=2.0, dith=0.3, bias=0.6)
ARM_I = Mat(ramp=['#141c3a', '#2a3a68', '#4a6aa0', '#86a8d4', '#cfe4f8'], bevel=1.5, tex=0.2, seed=53)
ARM_IB = Mat(ramp=['#0e1430', '#1e2a52', '#344c80', '#5c7ca8', '#8cacd0'], bevel=1.5, tex=0.2, seed=54)
FURW = Mat(ramp=['#383e5c', '#6a7498', '#a4b0cc', '#dce6f2', '#ffffff'], bevel=1.8, tex=0.5, ts=1.3, seed=55)
ROBE = Mat(ramp=['#0c1840', '#183070', '#2c52a8', '#4a80d0', '#7cb4ec'], bevel=2.0, tex=0.2, seed=56)
ROBE_D = Mat(ramp=['#060c24', '#0c1840', '#162c64', '#244890'], bevel=1.4, seed=57)
SKINI = Mat(ramp=['#10182c', '#1c2c4c', '#2c4670'], bevel=1.0, dith=0.1)
EYEC = Mat(ramp=['#2aa8e0', '#7af0ff', '#d8ffff', '#ffffff'], emi=True, nooutline=True, bevel=0.8, dith=0.1)
FROST = '#7AF0FF'
SPK = '#d8faff'


def crystal(c, x, y, ang, L, W, mat=CRYS, glow=0.0):
    with c.at(x, y, ang):
        with c.part(mat, line=0.0, bevel=W * 0.8) as p:
            p.poly([(-L * 0.5, 0), (-L * 0.15, -W), (L * 0.5, 0), (-L * 0.15, W)])
        with c.part(ICEGLOW, bevel=0.8) as p:
            p.poly([(-L * 0.3, 0), (-L * 0.1, -W * 0.35), (L * 0.28, 0), (-L * 0.1, W * 0.35)])


# ------------------------------------------------------------------ LANCERO DE ESCARCHA
def lan_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(hx=-4.0, dy=0.7 * s, lean=0.05, ph=t, walk=False, stride=0, lift=0, grip=(2, -16), sa=-0.35, ext=0.0, glow=0.0,
             flash=0.0, trail=0.0, head=0.0, crouch=0.0)
    if a == 'idle':
        P['grip'] = (1.5, -16 + 0.4 * s); P['sa'] = -0.45 + 0.03 * s
    elif a == 'walk':
        P.update(walk=True, stride=5.0, lift=2.8, dy=-0.9 * abs(math.sin(2 * math.pi * t)) + 0.4, lean=0.14, hx=-3)
        P['grip'] = (1.5, -16 + 0.8 * s); P['sa'] = -0.55 + 0.05 * s
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(lean=lerp(0.05, -0.2, w), hx=lerp(-4, -8, w), dy=lerp(0, 2, w), glow=w, head=-0.1 * w)
        P['grip'] = (lerp(1.5, -4, w), lerp(-16, -15, w)); P['sa'] = lerp(-0.45, -0.1, w); P['ext'] = -3 * w
    elif a == 'attack':
        k = i / (n - 1)
        P['lean'] = kf(k, [(0, -0.2), (0.2, 0.2), (0.4, 0.3), (0.7, 0.2), (1, 0.05)])
        P['hx'] = kf(k, [(0, -8), (0.2, -1), (0.4, 3), (0.7, 2.5), (1, -2)])
        P['dy'] = kf(k, [(0, 2), (0.4, 2.5), (1, 0)])
        P['grip'] = (kf(k, [(0, -4), (0.2, 4), (0.4, 8), (0.7, 7), (1, 2)]), kf(k, [(0, -15), (0.4, -15), (1, -16)]))
        P['sa'] = kf(k, [(0, -0.1), (0.4, -0.02), (1, -0.4)])
        P['ext'] = kf(k, [(0, -3), (0.2, 1), (0.4, 3), (0.7, 2.5), (1, 0)])
        P['glow'] = 1.0 if k < 0.8 else 0.3
        P['trail'] = 1.0 if 0.18 < k < 0.7 else 0.0
        P['stride'] = 0
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(hx=-4 + rx, lean=ln, flash=fl, head=-0.3 if i == 0 else -0.1)
        P['grip'] = (-1, -14) if i == 0 else (1, -15); P['sa'] = 0.2 if i == 0 else -0.2
    return P


def lancero_body(c, P, a, nospear=False):
    hx, dy, lean, ph = P['hx'], P['dy'], P['lean'], P['ph']
    hip = (hx, -13.5 + dy)
    sl = (math.sin(lean), -math.cos(lean))
    neck = (hip[0] + 11 * sl[0], hip[1] + 11 * sl[1])
    sho = (hip[0] + 9.2 * sl[0], hip[1] + 9.2 * sl[1])
    if P['walk']:
        f1 = gait(ph, P['stride'], P['lift']); f2 = gait((ph + 0.5) % 1, P['stride'], P['lift'])
    elif a in ('windup', 'attack'):
        f1, f2 = (-6.0, 0), (5.0, 0)
    else:
        f1, f2 = (-3.5, 0), (3.5, 0)
    # capa de piel trasera
    with c.part(FURW, bevel=1.6, line=0.0) as p:
        p.poly([(neck[0] - 3, neck[1]), (neck[0] + 1, neck[1] - 1), (hip[0] - 1, hip[1] + 5 + math.sin(ph * 6.28) * 0.8), (hip[0] - 8 - lean * 4, hip[1] + 7), (neck[0] - 7, neck[1] + 3)])
    leg(c, (hip[0] - 1, hip[1] + 1), (hip[0] - 1 + f1[0], f1[1]), 6.6, 6.6, 2.0, 1.8, ARM_IB, bend=-1, footmat=ARM_IB, footlen=4)
    gx, gy = P['grip']
    sa = P['sa']
    d = (math.cos(sa), math.sin(sa))
    rear = (hx + gx + d[0] * P['ext'] * 0.5, gy + dy + d[1] * P['ext'] * 0.5)
    front = (rear[0] + d[0] * 6.5, rear[1] + d[1] * 6.5)
    # brazo lejano -> mano delantera
    ef = ik2(sho, front, 5.4, 5.8, bend=1)
    with c.part(ARM_IB, line=0.4, bevel=1.4) as p:
        p.limb((sho[0] + 0.5, sho[1]), ef, 1.9, 1.7); p.limb(ef, front, 1.7, 1.6)
    # lanza (detras del torso solo en parte): se dibuja entera tras el brazo lejano
    if not nospear:
        base = (rear[0] - d[0] * 7, rear[1] - d[1] * 7)
        tip = (rear[0] + d[0] * 20, rear[1] + d[1] * 20)
        with c.part(ARM_I, line=0.3, bevel=0.8) as p:
            p.limb(base, tip, 0.9)
        with c.part(ICE, bevel=1.4, line=0.3) as p:
            n_ = (-d[1], d[0])
            e0 = (tip[0], tip[1])
            p.poly([(e0[0] + n_[0] * 2.2 - d[0] * 1.5, e0[1] + n_[1] * 2.2 - d[1] * 1.5), (e0[0] + d[0] * 6.5, e0[1] + d[1] * 6.5),
                    (e0[0] - n_[0] * 2.2 - d[0] * 1.5, e0[1] - n_[1] * 2.2 - d[1] * 1.5), (e0[0] - d[0] * 3.2, e0[1] - d[1] * 3.2)])
        with c.part(ICEGLOW, bevel=0.8) as p:
            p.limb((tip[0] + d[0] * 0.5, tip[1] + d[1] * 0.5), (tip[0] + d[0] * 5, tip[1] + d[1] * 5), 0.6)
        if P['glow'] > 0.1:
            c.glow(tip[0] + d[0] * 3, tip[1] + d[1] * 3, 5 + 3 * P['glow'], FROST, 0.35 * P['glow'] + 0.15)
        if P['trail'] > 0:
            with c.part(ICEGLOW, bevel=0.8, fade=lambda lx, ly: np.clip((lx - (tip[0] - 16)) / 14, 0, 1) * 0.9) as p:
                p.poly([(tip[0] - 16, tip[1] - 1.5), (tip[0] + 2, tip[1] - 0.5), (tip[0] + 2, tip[1] + 0.5), (tip[0] - 16, tip[1] + 1.5)])
    # torso con peto
    with c.at(hip[0], hip[1], lean):
        with c.part(ARM_IB, line=0.5, bevel=1.8) as p:
            p.poly([(-3.8, 0), (3.5, 0.5), (3.8, 3.5), (-3.5, 3.8)])
        with c.part(ARM_I, line=0.5, bevel=2.2) as p:
            p.poly([(-4.2, -2), (4.5, -2.4), (5.2, -9), (3.5, -12), (-3, -12), (-5, -8)])
        with c.part(ICE, bevel=1.0) as p:                 # escudete de cristal en el pecho
            p.poly([(0.2, -9.5), (2.8, -7), (0.5, -4), (-2, -7)])
        with c.part(FURW, bevel=1.4) as p:
            p.ell(0, -11.5, 5.2, 2.0)
    leg(c, (hip[0] + 1, hip[1] + 1), (hip[0] + 1 + f2[0], f2[1]), 6.6, 6.6, 2.1, 1.9, ARM_I, bend=-1, footmat=ARM_I, footlen=4)
    # cabeza con yelmo
    hxn = neck[0] + 3.2 * math.sin(lean + P['head']) + 0.5
    hyn = neck[1] - 3.2 * math.cos(lean + P['head'])
    with c.at(hxn, hyn, lean * 0.5 + P['head']):
        with c.part(ARM_I, line=0.5, bevel=1.8) as p:
            p.ell(0, 0, 4.4, 4.6)
            p.poly([(-4, 1), (4.5, 1.2), (4.2, 4.8), (-3, 5)])
        with c.part(DARK) as p:
            p.poly([(0.4, -0.8), (4.6, -0.8), (4.4, 1.2), (0.6, 1.4)])
        with c.part(EYEC) as p:
            p.poly([(1.4, -0.4), (4.0, -0.4), (3.9, 0.5), (1.5, 0.7)])
        c.glow(3, 0, 3.5, FROST, 0.4)
        with c.part(ICE, bevel=1.0, line=0.3) as p:     # cresta de escarcha
            p.poly([(-3.5, -3), (-8.5, -6 + 0.8 * math.sin(ph * 6.28)), (-6, -1.5)])
            p.poly([(-1, -4.2), (-5.5, -9.5 + 0.8 * math.sin(ph * 6.28 + 1)), (-3.5, -3.6)])
            p.poly([(1.5, -4.2), (0, -10 + 0.8 * math.sin(ph * 6.28 + 2)), (-1, -4)])
    # brazo cercano
    er = ik2(sho, rear, 5.4, 5.8, bend=1)
    with c.part(ARM_I, line=0.4, bevel=1.4) as p:
        p.limb(sho, er, 2.0, 1.8); p.limb(er, rear, 1.8, 1.7)
    with c.part(FURW, bevel=1.2) as p:
        p.ell(sho[0], sho[1] - 0.8, 3.4, 2.4)
    with c.part(ARM_I, bevel=0.8) as p:
        p.ell(rear[0], rear[1], 1.8)


def draw_lancero(c, a, i, n):
    if a == 'death':
        return death_lancero(c, i, n)
    P = lan_pose(a, i, n)
    lancero_body(c, P, a)
    if P['flash']:
        c.flash(WHITE, P['flash'])


def _shard(L, W, m=CRYS):
    def f(c):
        crystal(c, 0, 0, 0, L, W, m)
    return f


def _p_arm(c):
    with c.part(ARM_I, line=0.4, bevel=1.4) as p:
        p.limb((-3, 0), (3, 0), 1.9)


def _p_helm_l(c):
    with c.part(ARM_I, line=0.5, bevel=1.8) as p:
        p.ell(0, 0, 4.4, 4.6)
    with c.part(EYEC) as p:
        p.rect(1.4, -0.4, 4.0, 0.6)


def _p_chest(c):
    with c.part(ARM_I, line=0.5, bevel=2.2) as p:
        p.poly([(-4.2, -5), (4.5, -5.4), (5.2, 0), (3.5, 5), (-3, 5), (-5, 1)])
    with c.part(ICE, bevel=1.0) as p:
        p.poly([(0.2, -2.5), (2.8, 0), (0.5, 3), (-2, 0)])


def _p_spear(c):
    with c.part(ARM_I, line=0.3, bevel=0.8) as p:
        p.limb((-12, 0), (8, 0), 0.9)
    with c.part(ICE, bevel=1.4, line=0.3) as p:
        p.poly([(6.5, -2.2), (14, 0), (6.5, 2.2), (4.5, 0)])


def death_lancero(c, i, n):
    if i == 0:
        lancero_body(c, lan_pose('hurt', 0, 2), 'hurt')
        c.flash(WHITE, 0.5)
        return
    u = i / (n - 1)
    import random
    rnd = random.Random(7)
    items = [dict(fn=_p_helm_l, x=-4, y=-28, r=4.5, vx=-3, vy=-8, spin=-4, rest=0.5, bounce=0.3),
             dict(fn=_p_chest, x=-4, y=-20, r=5, vx=-1.5, vy=-4, spin=-2, rest=0.3),
             dict(fn=_p_arm, x=-3, y=-18, r=2, vx=3, vy=-5, spin=5, rest=0.1),
             dict(fn=_p_arm, x=-6, y=-17, r=2, vx=-4, vy=-6, spin=-5, rest=0.2),
             dict(fn=_p_arm, x=-3, y=-6, r=2, vx=2, vy=-3, spin=5, rest=3.0),
             dict(fn=_p_arm, x=-5, y=-6, r=2, vx=-3, vy=-3, spin=-5, rest=0.1),
             dict(fn=_p_spear, x=5, y=-18, r=2, vx=6, vy=-5, spin=-4, rest=0.12)]
    for k in range(7):
        items.append(dict(fn=_shard(rnd.uniform(3, 6), rnd.uniform(1.2, 2.2)), x=-3 + rnd.uniform(-3, 3), y=-15 - rnd.uniform(0, 10), r=1.5,
                          vx=rnd.uniform(-7, 7), vy=rnd.uniform(-10, -3), spin=rnd.uniform(-8, 8), rest=rnd.uniform(-0.4, 0.4), bounce=0.35))
    for d_ in items:
        d_['vx'] *= 0.55; d_['vy'] *= 0.65
    b = Bits(items, seed=5, T=0.8, g=1.6)
    draw_bits(c, b, u)
    if u < 0.5:
        c.flash(FROST, 0.35 * (1 - u * 2))
    if u > 0.35:
        w = min(1, (u - 0.35) / 0.4)
        with c.part(ICE_B, bevel=0.8) as p:
            p.ell(-4, -0.9, 3 + 9 * w, 1.0 + 0.3 * w)


# ------------------------------------------------------------------ HECHICERO DE HIELO
def hech_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(y=-5 + 1.8 * s, x=-1.0, ph=t, lean=0.0, arms=1.0, orb=0.0, conv=0.0, glow=0.0, flash=0.0, rel=False, hood=0.0, launch=0.0, spin=t)
    if a == 'walk':
        P.update(x=-1, lean=0.14, y=-5 + 1.8 * math.sin(2 * math.pi * t))
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(arms=lerp(1.0, 0.0, w), conv=w, glow=w, lean=lerp(0, -0.12, w), y=-5 - 1.5 * w, x=-3 * w, spin=t * 2)
    elif a == 'attack':
        P.update(arms=[0.0, 0.0, -0.3, 0.3, 0.7, 1.0][i], conv=[1.0, 1.0, 0.7, 0.0, 0.0, 0.0][i],
                 launch=[0, 0, 0.0, 0.5, 0.9, 1.0][i], lean=[-0.12, -0.12, 0.22, 0.12, 0.05, 0.0][i], glow=[1, 1, 0.8, 0.2, 0, 0][i],
                 x=[-3, -3, 1, 0, -1, -1][i], y=-6.5 + 1.0 * [0, 0, 1, 1, 0.5, 0][i], spin=0.5 + i * 0.12)
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(x=-1 + rx, lean=ln, flash=fl, arms=0.6, hood=1 if i == 0 else 0)
    return P


def hechicero_body(c, P, orbit=True, shards=None):
    x, y, lean, ph = P['x'], P['y'], P['lean'], P['ph']
    cx, cy = x, y - 14
    ang_o = P['spin'] * 6.283
    # cristales orbitando (los de atras primero)
    cr = []
    for k in range(4):
        th = ang_o + k * 1.5708
        conv = P['conv']
        orx, ory = lerp(14.0, 3.5, conv), lerp(5.0, 3.0, conv)
        px_ = cx + math.cos(th) * orx * (1 - conv) + (conv * (cx + 11 - cx)) + (math.cos(th) * 3 * conv)
        py_ = cy - 1 + math.sin(th) * ory * 1.0 + math.sin(th) * 4 * conv
        depth = math.sin(th)
        cr.append((depth, px_, py_, th, k))
    cr.sort()
    def put_crystal(ent):
        d_, px_, py_, th, k = ent
        L = 7.5 if d_ >= 0 else 6.0
        L *= 1.0 + 0.2 * P['glow']
        launch = P['launch']
        ang = lerp(-1.3 + 0.35 * k, 0.0, max(P['conv'], launch))
        if launch > 0:
            px_ = lerp(px_, cx + 14 + launch * 5 + k * 1.5 - 1.5 * k, 0.9)
            py_ = lerp(py_, cy - 2 + (k - 1.5) * 2.2, 0.9)
        crystal(c, px_, py_, ang if launch == 0 else 0.0, L, 2.4, CRYS if d_ >= 0 else ICE_B)
        if P['glow'] > 0.2:
            c.glow(px_, py_, 4, FROST, 0.4 * P['glow'])
    if orbit:
        for ent in cr[:2]:
            put_crystal(ent)
    # tunica
    sw = math.sin(ph * 6.283)
    hem = [(cx - 9 - lean * 3 + 0.7 * sw, y + 0.5), (cx - 5, y - 1.3 + 0.9 * math.sin(ph * 6.283 + 1)), (cx - 1, y + 0.6), (cx + 3, y - 1.2 + 0.9 * math.sin(ph * 6.283 + 2)),
           (cx + 7 + lean * 3 - 0.7 * sw, y + 0.4)]
    with c.part(ROBE, line=0.5, bevel=2.8) as p:
        p.poly([(cx - 3.5, cy - 8)] + [(cx + 4, cy - 8), (cx + 6.5, cy + 2)] + hem[::-1] + [(cx - 7, cy + 2)])
    with c.part(ROBE_D, bevel=1.4) as p:
        p.poly([(cx - 3, cy - 2), (cx - 0.5, cy - 3), (hem[2][0] - 1, hem[2][1] - 1.5), (hem[1][0] + 1, hem[1][1] - 1.5)])
    with c.part(FURW, bevel=1.2) as p:
        for (hx_, hy_) in hem:
            p.ell(hx_, hy_ - 0.3, 2.3, 1.4)
    with c.part(ICE, bevel=0.8) as p:                 # cinturon con gema
        p.poly([(cx - 4.5, cy + 1.0), (cx + 5, cy + 0.6), (cx + 5, cy + 2.4), (cx - 4.5, cy + 2.8)])
    with c.part(ICEGLOW) as p:
        p.ell(cx + 0.5, cy + 1.8, 1.1)
    # cuello de piel + capucha
    with c.at(cx + 0.8 + 2 * lean, cy - 9.5, lean * 0.6 - 0.1 * P['hood']):
        with c.part(ROBE, line=0.5, bevel=2.2) as p:
            p.poly([(-5.5, 3), (-6, -3), (-3, -7), (2, -8), (5.5, -5), (2.5, -3.5), (1.0, -1.5), (1.5, 1.5), (3.0, 3)])
            p.ell(-1, 0, 4.6, 5.0)
        with c.part(SKINI) as p:
            p.ell(2.2, -0.5, 2.8, 3.6)
        with c.part(EYEC) as p:
            p.ell(3.2, -0.8, 0.9, 0.6); p.ell(0.8, -0.9, 0.8, 0.55)
        c.glow(2.2, -0.8, 3.2, FROST, 0.5 + 0.3 * P['glow'])
        with c.part(FURW, bevel=1.4) as p:
            p.ell(-0.5, 4.6, 5.8, 1.9)
        with c.part(ICE, bevel=0.8, line=0.3) as p:
            p.poly([(-3, -6.2), (-4.5, -10.5), (-1.5, -7.5)])
            p.poly([(0, -7.8), (0.5, -12), (2, -7.8)])
    # brazos
    ar = P['arms']
    sh = (cx + 2.5, cy - 5.5)
    if ar > 0.5:
        hnd = (cx + 8, cy - 1 + (1 - ar) * 0)
        hnd2 = (cx + 6, cy + 1)
    else:
        hnd = (cx + 11, cy - 7 + ar * 6)
        hnd2 = (cx + 9, cy - 5 + ar * 6)
    if P['launch'] > 0.0 and ar <= 0.3 and False:
        pass
    for hh, m in ((hnd2, ROBE_D), (hnd, ROBE)):
        e = ik2(sh, hh, 5.5, 5.5, bend=1)
        with c.part(m, line=0.4, bevel=1.4) as p:
            p.limb(sh, e, 2.1, 1.9); p.limb(e, hh, 2.3, 1.6)
        with c.part(SKINI) as p:
            p.ell(hh[0], hh[1], 1.3)
    if P['conv'] > 0.3:
        orb = P['conv']
        with c.part(ICEGLOW, bevel=2.4) as p:
            p.ell(hnd[0] + 3, hnd[1] - 1, 1.5 + 2.8 * orb)
        c.glow(hnd[0] + 3, hnd[1] - 1, 8, FROST, 0.35 * orb)
    if orbit:
        for ent in cr[2:]:
            put_crystal(ent)


def draw_hechicero(c, a, i, n):
    if a == 'death':
        return death_hechicero(c, i, n)
    P = hech_pose(a, i, n)
    hechicero_body(c, P)
    if P['flash']:
        c.flash(WHITE, P['flash'])
    if a == 'windup':
        for q in range(4):
            c.dotw(-6 + q * 5 + math.sin(i * 2 + q) * 2, -24 - ((i * 2 + q * 3) % 7), SPK)


def _p_robe(c):
    with c.part(ROBE, line=0.5, bevel=2.8) as p:
        p.poly([(-9, 0), (-5, -3), (-1, 0.3), (3, -2.5), (8, 0), (6, 3), (-8, 3)])
    with c.part(FURW, bevel=1.2) as p:
        p.ell(-6, 2, 2.3, 1.4); p.ell(0, 2.4, 2.3, 1.4); p.ell(6, 2, 2.3, 1.4)


def _p_hood(c):
    with c.part(ROBE, line=0.5, bevel=2.2) as p:
        p.ell(0, 0, 5.4, 5.0)
    with c.part(SKINI) as p:
        p.ell(2.2, 0, 2.6, 3.4)
    with c.part(EYEC) as p:
        p.ell(3.2, -0.3, 0.9, 0.6)


def death_hechicero(c, i, n):
    if i == 0:
        hechicero_body(c, hech_pose('hurt', 0, 2))
        c.flash(WHITE, 0.5)
        return
    u = i / (n - 1)
    import random
    rnd = random.Random(12)
    items = [dict(fn=_p_hood, x=2, y=-24, r=4.5, vx=1, vy=-6, spin=3, rest=0.4, bounce=0.2)]
    for k in range(9):
        items.append(dict(fn=_shard(rnd.uniform(3, 6.5), rnd.uniform(1.2, 2.2)), x=rnd.uniform(-4, 6), y=-15 + rnd.uniform(-6, 4), r=1.5,
                          vx=rnd.uniform(-10, 10), vy=rnd.uniform(-11, -3), spin=rnd.uniform(-9, 9), rest=rnd.uniform(-0.4, 0.4), bounce=0.35))
    for d_ in items:
        d_['vx'] *= 0.55; d_['vy'] *= 0.65
    b = Bits(items, seed=5, T=0.8, g=1.6)
    # tunica se desinfla
    if u < 0.7:
        P = hech_pose('hurt', 1, 2)
        P['y'] = -5 + u * 5
        hechicero_body(c, P, orbit=False)
        c.flash(FROST, min(0.8, u * 1.5))
    draw_bits(c, b, u)
    if u >= 0.5:
        w = min(1, (u - 0.5) / 0.4)
        with c.at(0, -2.0, 0):
            _p_robe(c)
    if u > 0.3:
        w = min(1, (u - 0.3) / 0.5)
        with c.part(ICE_B, bevel=0.8) as p:
            p.ell(0, -0.9, 3 + 9 * w, 1.0 + 0.3 * w)
    for q in range(6):
        if u < 0.95:
            c.dotw(-6 + q * 2.6, -12 - u * 12 - (q % 3) * 3, SPK)


# ------------------------------------------------------------------ ESPIRITU VEX
WING = Mat(ramp=['#3a68b8', '#6ab0e8', '#a8e4ff', '#e8fbff'], bevel=1.2, dith=0.3, outcol='#1e3a78')
VEXB = Mat(ramp=['#1c3a84', '#3a78c8', '#7ac4f0', '#bff0ff', '#ffffff'], bevel=2.6, dith=0.4, bias=0.5, outcol='#16306e')


def vex_pose(a, i, n):
    t = i / n
    P = dict(y=-20 + 1.5 * math.sin(2 * math.pi * t), x=-2, ph=t, wing=math.sin(2 * math.pi * t * (1 if a == 'idle' else 1)), lean=0.2,
             sw=-0.5, ext=0.0, flash=0.0, glow=0.0, tail=t, fast=1.0)
    if a == 'idle':
        pass
    elif a == 'walk':
        P.update(wing=math.sin(2 * math.pi * t), lean=0.45, x=-1, y=-20 + 1.8 * math.sin(2 * math.pi * t * 1), fast=2)
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(wing=math.sin(2 * math.pi * t * 2) * 0.5 + 0.4, lean=lerp(0.2, -0.45, w), x=lerp(-2, -6, w), y=-20 + 2 * w, sw=lerp(-0.5, -1.5, w), glow=w, ext=-2 * w)
    elif a == 'attack':
        k = i / (n - 1)
        P.update(wing=[0.6, -0.6, 0.9, 0.2, -0.4, 0.5][min(i, 5)], lean=kf(k, [(0, -0.45), (0.2, 0.7), (0.4, 0.9), (1, 0.3)]),
                 x=kf(k, [(0, -6), (0.2, 2), (0.4, 8), (0.7, 6), (1, 1)]), y=-20 + kf(k, [(0, 2), (0.4, 3), (1, 0)]),
                 sw=kf(k, [(0, -1.5), (0.2, -0.3), (0.4, 0.15), (1, -0.3)]), ext=kf(k, [(0, -2), (0.2, 2), (0.4, 5), (0.7, 4), (1, 0)]), glow=1.0 if k < 0.75 else 0.2)
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(x=-2 + rx, lean=ln, flash=fl, wing=-0.8 if i == 0 else 0.2, y=-20 - 2 * (1 - i))
    return P


def vex_body(c, P, parts=True):
    x, y, lean = P['x'], P['y'], P['lean']
    w = P['wing']
    ph = P['ph'] * 6.283
    # ala lejana
    for (sgn, m, off) in ((-1, WING, -1.5), (1, WING, 0)):
        wa = -0.9 + 1.0 * w if sgn == -1 else -0.6 - 1.15 * w
        wx, wy = x - 2.5 + off, y - 3
        L = 13
        tipx, tipy = wx - L * math.cos(0.6 - 0.2 * w) * 0.9 - 2, wy + L * math.sin(wa) * 0.9
        if sgn == -1:
            tipy = wy - 8 - 6 * w
        else:
            tipy = wy - 7 + 9 * w
        fade = lambda lx, ly, wx=wx, tx=tipx: np.clip(1.15 - np.abs(lx - wx) / 14.0 * 0.5, 0, 1)
        with c.part(m, fade=fade, bevel=2.2, line=0.0) as p:
            p.poly([(wx, wy), (tipx - 3, tipy), (tipx + 2, tipy + 4), (wx - 7, wy + 1 + (6 if sgn == 1 else 5)), (wx - 1, wy + 6)])
        if sgn == -1:
            with c.part(ICE_B, bevel=0.8) as p:
                p.limb((wx, wy), (tipx - 3, tipy), 0.7)
    # cola ondulante hacia abajo/atras (se afina)
    pts = []
    for k in range(6):
        u = k / 5
        pts.append((x - 1 - u * 7 - lean * 3 * u + math.sin(ph + u * 3) * 2.2 * u, y + 5 + u * 11))
    def tfade(lx, ly, y0=y + 5):
        return np.clip(1.2 - (ly - y0) / 13.0, 0, 1)
    with c.part(VEXB, fade=tfade, bevel=2.2) as p:
        p.tube(pts, 3.8, 0.6)
    # cuerpo/torso
    with c.at(x, y, lean * 0.6):
        with c.part(VEXB, bevel=3.0) as p:
            p.ell(0, 0, 4.8, 6.0)
            p.ell(0.5, 4.5, 3.8, 3.8)
        with c.part(ICEGLOW, bevel=1.2) as p:
            p.ell(0.8, 1.4, 1.8, 2.4)
        # cabeza
        with c.part(VEXB, bevel=2.2) as p:
            p.ell(2.2, -7.2, 4.4, 4.2)
            p.poly([(-1.2, -9), (-3, -13), (0.8, -10.5)])
            p.poly([(3, -10.2), (4.2, -14), (5.4, -9.8)])
        with c.part(DARK) as p:
            p.poly([(1.6, -8.6), (6.2, -8.0), (5.8, -5.6), (1.8, -6.2)])
        with c.part(EYEC) as p:
            p.poly([(2.6, -7.8), (5.0, -7.5), (4.8, -6.3), (2.8, -6.6)])
        c.glow(4, -7, 3.6, FROST, 0.5)
        with c.part(DARK) as p:
            p.rect(2.4, -4.6, 5.0, -4.1)
    # espada
    sw = P['sw']
    hand = (x + 5 + P['ext'] * 0.5, y + 1)
    d = (math.cos(sw), math.sin(sw))
    n_ = (-d[1], d[0])
    with c.part(VEXB, bevel=1.4) as p:
        p.limb((x + 1, y - 2), hand, 1.6, 1.4)
    tip = (hand[0] + d[0] * 11 + P['ext'] * d[0] * 0.3, hand[1] + d[1] * 11)
    with c.part(ICE, bevel=1.0, line=0.3) as p:
        p.poly([(hand[0] + d[0] * 1.5 + n_[0] * 1.5, hand[1] + d[1] * 1.5 + n_[1] * 1.5), (tip[0], tip[1]),
                (hand[0] + d[0] * 1.5 - n_[0] * 1.5, hand[1] + d[1] * 1.5 - n_[1] * 1.5)])
    with c.part(ARM_IB, bevel=0.6) as p:
        p.limb((hand[0] + n_[0] * 2.3 + d[0], hand[1] + n_[1] * 2.3 + d[1]), (hand[0] - n_[0] * 2.3 + d[0], hand[1] - n_[1] * 2.3 + d[1]), 0.7)
    if P['glow'] > 0.1:
        c.glow(tip[0] - d[0] * 3, tip[1] - d[1] * 3, 5, FROST, 0.5 * P['glow'])
        if P['glow'] > 0.9 and P['ext'] > 2:
            with c.part(ICEGLOW, fade=lambda lx, ly: np.clip((lx - (tip[0] - 14)) / 12, 0, 1), bevel=0.8) as p:
                p.poly([(tip[0] - 14, tip[1] - 3), (tip[0], tip[1] - 0.5), (tip[0], tip[1] + 0.5), (tip[0] - 14, tip[1] + 3)])


def draw_vex(c, a, i, n):
    if a == 'death':
        return death_vex(c, i, n)
    P = vex_pose(a, i, n)
    vex_body(c, P)
    if P['flash']:
        c.flash(WHITE, P['flash'])


def death_vex(c, i, n):
    if i == 0:
        vex_body(c, vex_pose('hurt', 0, 2))
        c.flash(WHITE, 0.6)
        return
    u = i / (n - 1)
    import random
    rnd = random.Random(31)
    if u < 0.3:
        P = vex_pose('hurt', 1, 2)
        P['y'] = -20 + u * 8
        vex_body(c, P)
        c.flash(FROST, 0.5 + u)
    items = []
    for k in range(9):
        items.append(dict(fn=_shard(rnd.uniform(2.5, 5), rnd.uniform(1, 1.8)), x=-2 + rnd.uniform(-3, 4), y=-20 + rnd.uniform(-5, 4), r=1.2,
                          vx=rnd.uniform(-9, 9), vy=rnd.uniform(-9, -1), spin=rnd.uniform(-9, 9), rest=rnd.uniform(-0.4, 0.4), bounce=0.4))
    items.append(dict(fn=lambda cc: [cc.part(ICE, bevel=1.0, line=0.3).__enter__().poly([(-1, -1.3), (11, 0), (-1, 1.3)]).finish()], x=4, y=-18, r=1.2, vx=5, vy=-3, spin=4, rest=0.2))
    for d_ in items:
        d_['vx'] *= 0.5; d_['vy'] *= 0.6
    b = Bits(items, seed=5, T=0.75, g=1.3)
    if u >= 0.25:
        draw_bits(c, b, (u - 0.25) / 0.75)
    for q in range(8):
        c.dotw(-10 + q * 3 + math.sin(q + i) * 2, -20 + (q % 4) * 3 - u * 6 * (q % 3), SPK if q % 2 else FROST)
    if u > 0.5:
        w = min(1, (u - 0.5) / 0.4)
        with c.part(ICE_B, bevel=0.8) as p:
            p.ell(-2, -0.9, 2 + 7 * w, 0.9 + 0.3 * w)


def sheet_lancero_escarcha():
    return enemy_sheet('en_lancero_escarcha', (48, 48), (24, 46), (12, 32), draw_lancero, (12, 18, 44),
                       STD(6, hit=[2, 3], box=[6, -22, 32, 10], fa=15))


def sheet_hechicero_hielo():
    return enemy_sheet('en_hechicero_hielo', (48, 48), (24, 46), (14, 32), draw_hechicero, (10, 16, 46),
                       STD(6, rel=3, muz=[14, -22], walk=6, wfps=9, fa=13))


def sheet_espiritu_vex():
    return enemy_sheet('en_espiritu_vex', (48, 48), (24, 46), (14, 20), draw_vex, (14, 24, 66),
                       STD(6, hit=[2, 3], box=[2, -26, 24, 18], idle=6, walk=6, wfps=14, fa=16, death=7))


SHEETS = [sheet_lancero_escarcha, sheet_hechicero_hielo, sheet_espiritu_vex]
