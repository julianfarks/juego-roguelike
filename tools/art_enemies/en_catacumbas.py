from common import *

SOUL = '#5CFF9A'

# ------------------------------------------------------------------ ESQUELETO
BONE = Mat(ramp=['#2a2a3c', '#5b5a70', '#9a9a9c', '#d6d0b8', '#fbf4d6'], bevel=1.2, dith=0.5)
BONE_B = Mat(ramp=['#1c1c2c', '#403f58', '#6e6e7c', '#a49e90', '#cdc6ae'], bevel=1.2, dith=0.5)
RUST = Mat(ramp=['#2c1a1e', '#5a2a22', '#8a4a2c', '#b8743c', '#dca464'], bevel=0.9, tex=0.45, dith=0.5, seed=4)
IRON = Mat(ramp=['#1e2030', '#3c4258', '#66708a', '#98a4b8', '#d0dae6'], bevel=1.0, tex=0.2, seed=7)
WOODS = Mat(ramp=['#2a1822', '#4b2c2c', '#6f4430', '#946236', '#b88648'], bevel=1.2, tex=0.35, seed=9)
DARK = Mat(ramp=['#06060c', '#0c0c18', '#14142a'], bevel=0.8, dith=0.0, nooutline=False)
EYE = Mat(ramp=['#1c8a52', '#3cd07a', '#8affb8', '#e8fff0'], emi=True, nooutline=True, bevel=1.0, dith=0.1)
CLOTH_S = Mat(ramp=['#161420', '#2a2634', '#3f3a4a', '#58526a', '#7a7288'], bevel=1.2, tex=0.3, seed=2)


def skel_head(c, x, y, tilt, jaw, eyeamt, mat=BONE, cap=False):
    with c.at(x, y, tilt):
        with c.part(mat, bevel=1.6) as p:
            p.ell(0, 0, 4.4, 4.0)                          # craneo
            p.poly([(-1.5, 2.5), (3.6, 2.2), (4.2, 4.6 + jaw), (-0.5, 5.2 + jaw), (-2.2, 3.5)])  # mandibula
        with c.part(DARK) as p:
            p.ell(0.6, -0.2, 1.35, 1.6)                    # cuenca lejana
            p.ell(3.0, -0.1, 1.15, 1.5)
            p.poly([(4.1, 1.8), (4.8, 2.9), (3.9, 2.9)])    # nariz
        with c.part(EYE) as p:
            p.ell(3.1, -0.1, 0.65 + 0.3 * eyeamt, 0.8 + 0.3 * eyeamt)
            p.ell(0.7, -0.2, 0.55 + 0.25 * eyeamt, 0.7 + 0.25 * eyeamt)
        c.glow(3.1, -0.1, 2.0 + 1.2 * eyeamt, SOUL, 0.22 + 0.35 * eyeamt)
        with c.part(DARK) as p:  # dientes
            for k in range(3):
                p.rect(-0.3 + k * 1.6, 3.7 + jaw * 0.3, 0.3 + k * 1.6, 4.9 + jaw * 0.9)
        with c.part(DARK) as p:                                   # grietas del craneo y arco superciliar
            p.limb((-0.4, -3.9), (0.3, -1.6), 0.18)
            p.limb((0.3, -1.6), (-0.5, -0.4), 0.15)
            p.limb((1.8, -2.0), (4.2, -1.9), 0.16)
        with c.part(mat, bevel=0.8) as p:                         # pomulo marcado
            p.poly([(1.6, 1.0), (4.0, 0.9), (4.2, 2.2), (2.2, 2.4)])
        if cap:                                                   # casquete de hierro oxidado (identidad del esqueleto)
            with c.part(RUST, line=0.4, bevel=1.2) as p:
                p.poly([(-4.5, -0.2), (-3.9, -3.8), (-1.2, -4.9), (0.6, -4.4), (-0.4, -2.6), (-2.2, 0.2)])
            with c.part(IRON, bevel=0.7) as p:
                p.poly([(-4.4, -1.4), (-3.7, -3.6), (-2.0, -4.4), (-1.9, -3.2)])
                p.limb((-0.2, -5.0), (0.2, -2.3), 0.35)
            with c.part(DARK) as p:
                p.ell(-2.8, -2.3, 0.35)
                p.ell(0.8, -4.2, 0.3)


def skel_pose(a, i, n):
    P = dict(dy=0.0, lean=0.05, hx=-2.0, ph=0.0, walk=False, hand=(0, 0), swa=-0.6, eye=0.0, jaw=0.0, tilt=0.0,
             arm=(0.5, 1.4), sh=(0.2, 1.0), trail=None, stride=0, lift=0)
    t = i / n
    if a == 'idle':
        P['dy'] = 0.7 * math.sin(2 * math.pi * t)
        P['lean'] = 0.05 + 0.03 * math.sin(2 * math.pi * t + 1)
        P['arm'] = (0.55 + 0.06 * math.sin(2 * math.pi * t), 1.35)
        P['swa'] = -0.9 + 0.08 * math.sin(2 * math.pi * t + 1)
        P['jaw'] = 0.5 * max(0, math.sin(2 * math.pi * t * 2))
        P['tilt'] = 0.05 * math.sin(2 * math.pi * t)
    elif a == 'walk':
        P['walk'] = True
        P['ph'] = t
        P['stride'], P['lift'] = 5.5, 3.2
        P['dy'] = -0.9 * abs(math.sin(2 * math.pi * t * 1)) + 0.4
        P['lean'] = 0.16
        P['hx'] = -1.0
        P['arm'] = (0.9 + 0.22 * math.sin(2 * math.pi * t), 1.5)
        P['swa'] = -1.2 + 0.15 * math.sin(2 * math.pi * t + 1)
        P['sh'] = (0.2 - 0.2 * math.sin(2 * math.pi * t), 1.0)
        P['tilt'] = 0.08
    elif a == 'windup':
        w = (i + 1) / n
        e = sm(w)
        P['lean'] = lerp(0.05, -0.30, e)
        P['hx'] = lerp(-2, -5, e)
        P['arm'] = (lerp(0.5, -1.9, e), lerp(1.4, -0.6, e))
        P['swa'] = lerp(-0.9, -2.55, e)
        P['eye'] = e
        P['dy'] = lerp(0, 1.0, e)
        P['jaw'] = 2.0 * e
        P['tilt'] = -0.15 * e
    elif a == 'attack':
        k = i / (n - 1)
        # frame0: arriba; 1: tajo rapido; 2-3 golpe; resto recuperacion
        P['lean'] = kf(k, [(0, -0.30), (0.2, 0.15), (0.4, 0.42), (0.7, 0.30), (1, 0.12)])
        P['hx'] = kf(k, [(0, -5), (0.2, -1), (0.4, 3.5), (0.7, 3), (1, 0)])
        s = kf(k, [(0, -1.9), (0.2, -0.3), (0.4, 1.25), (0.7, 1.1), (1, 0.4)])
        P['arm'] = (s, kf(k, [(0, -0.6), (0.4, 1.0), (1, 1.2)]))
        P['swa'] = kf(k, [(0, -2.55), (0.2, -1.3), (0.4, 0.5), (0.7, 0.6), (1, -0.3)])
        P['eye'] = 1.0 if k < 0.7 else 0.3
        P['dy'] = kf(k, [(0, 1), (0.4, 1.8), (1, 0)])
        P['jaw'] = 2.0
        P['tilt'] = 0.15
        if 0.15 < k < 0.75:
            P['trail'] = k
        P['stride'] = 0
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P['hx'] = -2 + rx
        P['lean'] = ln
        P['arm'] = (-0.4, 0.6) if i == 0 else (0.2, 1.0)
        P['swa'] = -1.8 if i == 0 else -1.3
        P['jaw'] = 3
        P['tilt'] = -0.35 if i == 0 else -0.15
        P['eye'] = 0.8
        P['flash'] = fl
    return P


def skeleton_pieces(P):
    pass


def draw_esqueleto(c, a, i, n):
    if a == 'death':
        return death_esqueleto(c, i, n)
    P = skel_pose(a, i, n)
    ph = P['ph']
    hx, dy, lean = P['hx'], P['dy'], P['lean']
    hip = (hx, -13.5 + dy)
    sl = (math.sin(lean), -math.cos(lean))
    neck = (hip[0] + 11 * sl[0], hip[1] + 11 * sl[1])
    shoulder = (hip[0] + 9.2 * sl[0], hip[1] + 9.2 * sl[1])
    # pies
    if P['walk']:
        f1 = gait(ph, P['stride'], P['lift'])
        f2 = gait((ph + 0.5) % 1, P['stride'], P['lift'])
    elif a == 'attack' or a == 'windup':
        k = (i + 1) / n if a == 'windup' else i / (n - 1)
        sp = 4.5 if a == 'windup' else kf(k, [(0, 4.5), (0.4, 7), (1, 5)])
        f1 = (-sp * 0.8, 0)
        f2 = (sp, 0)
    elif a == 'hurt':
        f1 = (-4.5, 0); f2 = (3.5, 0)
    else:
        f1 = (-3.2, 0); f2 = (3.2, 0)
    # --- brazo escudo (lejano): detras del torso
    sA, sB = P['sh']
    sh0 = (shoulder[0] + 0.5, shoulder[1] + 0.5)
    se, sh_hand = fk(sh0, sA + 0.6, 6.0, sB - 0.3, 5.2)
    bone(c, sh0, se, 0.85, BONE_B)
    bone(c, se, sh_hand, 0.8, BONE_B)
    # escudo roto (lejano)
    with c.at(sh_hand[0] + 1.5, sh_hand[1] - 0.5, 0.15):
        with c.part(WOODS, line=0.5, bevel=1.4) as p:
            p.poly([(-5.2, -6.5), (3.8, -6.0), (4.6, -1.0), (2.8, 1.6), (4.0, 6.6), (-2.5, 7.0), (-5.6, 1.0)])
        with c.part(IRON, line=0.5, bevel=1.0) as p:
            p.poly([(-5.2, -6.5), (-1.6, -6.4), (-1.0, 6.9), (-2.5, 7.0), (-5.6, 1.0)])      # banda metal
            p.ell(0.8, 0.2, 1.6)                                                     # umbo
        with c.part(DARK) as p:
            p.poly([(1.4, -6.2), (2.6, -1.6), (1.2, 0.2), (3.0, 2.4), (1.6, 3.4), (0.2, -2.4)])  # grieta
    # --- pierna trasera
    leg(c, (hip[0] - 1.0, hip[1] + 1), (hip[0] - 1.0 + f1[0], f1[1]), 6.6, 6.6, 0.95, 0.9, BONE_B, bend=-1)
    # --- columna, caja toracica, pelvis
    with c.part(BONE_B, bevel=0.8) as p:
        p.limb((hip[0] - 0.4, hip[1] - 1), (neck[0] - 0.8, neck[1] + 1), 0.9, 0.8)
    # pelvis
    with c.at(hip[0], hip[1], lean):
        with c.part(BONE, line=0.4, bevel=1.4) as p:
            p.poly([(-3.8, -1.6), (3.4, -1.8), (3.0, 1.6), (0.6, 3.2), (-3.2, 2.4)])
        with c.part(DARK) as p:
            p.ell(0.5, 0.6, 0.9, 1.1)
    # caja toracica
    with c.at(hip[0] + 4.5 * sl[0], hip[1] + 4.5 * sl[1] - 0.0, lean):
        with c.part(BONE, line=0.4, bevel=1.2) as p:
            p.ell(0, -1.8, 4.1, 5.6)
        with c.part(DARK) as p:  # huecos entre costillas
            for k in range(4):
                p.rect(-3.2, -5.4 + k * 2.4, 3.2, -4.7 + k * 2.4 + 0.2)
        with c.part(BONE, bevel=0.8) as p:
            p.limb((-2.0, -6.8), (-1.2, 2.0), 0.9, 0.8)   # esternon/columna visible
            p.limb((-2.0, -6.3), (3.8, -7.0), 0.5, 0.45)  # clavicula
    # --- pierna delantera
    leg(c, (hip[0] + 1.0, hip[1] + 1), (hip[0] + 1.0 + f2[0], f2[1]), 6.6, 6.6, 1.0, 0.95, BONE, bend=-1)
    # trapo de cintura colgando de un cinto de cuero
    with c.at(hip[0], hip[1], lean * 0.5):
        with c.part(CLOTH_S, line=0.4, bevel=1.3) as p:
            p.poly([(-2.4, 1.2), (1.6, 1.0), (2.0, 3.8), (0.8, 4.8), (-0.4, 4.0), (-1.4, 5.4), (-2.6, 3.6)])
        with c.part(WOODS, line=0.3, bevel=0.8) as p:
            p.poly([(-3.4, -0.4), (3.4, -0.6), (3.5, 0.9), (-3.4, 1.1)])
        with c.part(IRON, bevel=0.6) as p:
            p.rect(0.8, -0.8, 2.2, 1.4)
    # --- cabeza
    skel_head(c, neck[0] + 3.5 * math.sin(lean + P['tilt']) + 0.5, neck[1] - 3.8 * math.cos(lean + P['tilt']) , lean * 0.6 + P['tilt'],
              P['jaw'], P['eye'], cap=True)
    # --- brazo espada (cercano)
    A1, A2 = P['arm']
    e, hand = fk(shoulder, A1, 5.8, A2, 5.6)
    # trapo/bufanda
    bone(c, shoulder, e, 0.95, BONE)
    bone(c, e, hand, 0.9, BONE)
    with c.part(RUST, line=0.4, bevel=1.3) as p:      # hombrera oxidada
        p.poly([(shoulder[0] - 2.2, shoulder[1] + 1.0), (shoulder[0] - 1.4, shoulder[1] - 1.6), (shoulder[0] + 1.2, shoulder[1] - 2.2), (shoulder[0] + 2.6, shoulder[1] - 0.4), (shoulder[0] + 1.8, shoulder[1] + 1.4)])
    with c.part(IRON, bevel=0.6) as p:
        p.limb((shoulder[0] - 1.8, shoulder[1] - 1.8), (shoulder[0] + 2.2, shoulder[1] - 1.4), 0.3)
    with c.part(CLOTH_S, bevel=0.8) as p:             # venda en la muneca
        p.limb((lerp(e[0], hand[0], 0.7), lerp(e[1], hand[1], 0.7) - 0.8), (lerp(e[0], hand[0], 0.7), lerp(e[1], hand[1], 0.7) + 0.9), 1.2)
    # espada oxidada
    sa = P['swa']
    d = (math.cos(sa), math.sin(sa))
    nrm = (-d[1], d[0])
    base = (hand[0] - d[0] * 2.0, hand[1] - d[1] * 2.0)
    tip = (hand[0] + d[0] * 15.5, hand[1] + d[1] * 15.5)
    with c.part(RUST, line=0.4, bevel=0.9) as p:
        p.poly([(hand[0] + d[0] * 2.5 + nrm[0] * 1.5, hand[1] + d[1] * 2.5 + nrm[1] * 1.5),
                (tip[0] + nrm[0] * 0.2 - d[0] * 0.0, tip[1] + nrm[1] * 0.2),
                (hand[0] + d[0] * 13.5 - nrm[0] * 1.2, hand[1] + d[1] * 13.5 - nrm[1] * 1.2) if False else (tip[0] - nrm[0] * 0.9, tip[1] - nrm[1] * 0.9),
                (hand[0] + d[0] * 2.5 - nrm[0] * 1.5, hand[1] + d[1] * 2.5 - nrm[1] * 1.5)])
    with c.part(IRON, bevel=0.8) as p:
        p.limb((hand[0] + nrm[0] * 2.6 + d[0] * 2.2, hand[1] + nrm[1] * 2.6 + d[1] * 2.2),
               (hand[0] - nrm[0] * 2.6 + d[0] * 2.2, hand[1] - nrm[1] * 2.6 + d[1] * 2.2), 0.8)
        p.limb(base, (hand[0] + d[0] * 1.5, hand[1] + d[1] * 1.5), 0.9)
    with c.part(DARK) as p:                           # mellas del filo
        for q in (0.35, 0.55, 0.78):
            p.poly([(hand[0] + d[0] * (2.5 + 11 * q) - nrm[0] * 1.2, hand[1] + d[1] * (2.5 + 11 * q) - nrm[1] * 1.2),
                    (hand[0] + d[0] * (3.2 + 11 * q) - nrm[0] * 0.2, hand[1] + d[1] * (3.2 + 11 * q) - nrm[1] * 0.2),
                    (hand[0] + d[0] * (3.4 + 11 * q) - nrm[0] * 1.3, hand[1] + d[1] * (3.4 + 11 * q) - nrm[1] * 1.3)])
    with c.part(BONE, bevel=0.6) as p:
        p.ell(hand[0], hand[1], 1.4)
    if a == 'windup':
        w = (i + 1) / n
        c.glow(tip[0] - d[0] * 4, tip[1] - d[1] * 4, 7, SOUL, 0.3 + 0.6 * w)
    if P['trail'] is not None:
        an = math.atan2(tip[1] - shoulder[1], tip[0] - shoulder[0])
        rr = math.hypot(tip[0] - shoulder[0], tip[1] - shoulder[1])
        arc_trail(c, shoulder[0], shoulder[1], rr - 8, rr + 1, an - 1.5, an + 0.1, TRAILM)
    if 'flash' in P:
        c.flash(WHITE, P['flash'])
    if a == 'windup' and i == n - 1:
        c.flash(SOUL, 0.08)


TRAILM = Mat(ramp=['#2e8a5c', '#5cd890', '#a8ffd0', '#effff6'], emi=True, nooutline=True, bevel=1.5, dith=0.2)


def _p_skull(c):
    skel_head(c, 0, 0, 0, 1.5, 0.2, cap=True)


def _p_ribs(c):
    with c.part(BONE, line=0.4, bevel=1.2) as p:
        p.ell(0, 0, 4.1, 5.6)
    with c.part(DARK) as p:
        for k in range(4):
            p.rect(-3.2, -3.6 + k * 2.4, 3.2, -2.9 + k * 2.4)
    with c.part(BONE, bevel=0.8) as p:
        p.limb((-2.0, -5.0), (-1.2, 3.8), 0.9, 0.8)


def _p_pelvis(c):
    with c.part(BONE, line=0.4, bevel=1.4) as p:
        p.poly([(-3.8, -1.6), (3.4, -1.8), (3.0, 1.6), (0.6, 3.2), (-3.2, 2.4)])


def _p_bone(L, m=BONE):
    def f(c):
        bone(c, (-L / 2, 0), (L / 2, 0), 0.95, m)
    return f


def _p_sword(c):
    with c.part(RUST, line=0.4, bevel=0.9) as p:
        p.poly([(-2, -1.5), (13, -0.2), (14, 0.4), (-2, 1.5)])
    with c.part(IRON, bevel=0.8) as p:
        p.limb((1.5, -2.6), (1.5, 2.6), 0.8)


def _p_shield(c):
    with c.part(WOODS, line=0.5, bevel=1.4) as p:
        p.poly([(-5.2, -6.5), (3.8, -6.0), (4.6, -1.0), (2.8, 1.6), (4.0, 6.6), (-2.5, 7.0), (-5.6, 1.0)])
    with c.part(IRON, line=0.5, bevel=1.0) as p:
        p.ell(0.8, 0.2, 1.6)


def death_esqueleto(c, i, n):
    # fotograma 0: golpe (esqueleto entero, flash); luego se desarma en piezas
    if i == 0:
        P = skel_pose('hurt', 0, 2)
        # redibujar via hurt
        draw_esqueleto(c, 'hurt', 0, 2)
        c.flash(WHITE, 0.45)
        return
    items = [
        dict(fn=_p_skull, x=-3.5, y=-30, r=4, vx=-3, vy=-8, spin=-4, rest=-0.3, bounce=0.35),
        dict(fn=_p_ribs, x=-4.5, y=-20, r=5, vx=-2.2, vy=-5, spin=-2, rest=0.5),
        dict(fn=_p_pelvis, x=-2.5, y=-13, r=2.5, vx=-0.8, vy=-3, spin=1, rest=0.1),
        dict(fn=_p_bone(8), x=-6, y=-22, r=1.3, vx=-6, vy=-6, spin=5, rest=0.15),
        dict(fn=_p_bone(8), x=-5, y=-18, r=1.3, vx=-3.5, vy=-7, spin=-6, rest=-0.3),
        dict(fn=_p_bone(8), x=-1, y=-8, r=1.3, vx=3, vy=-5, spin=6, rest=0.05),
        dict(fn=_p_bone(8), x=-4, y=-8, r=1.3, vx=-1, vy=-4, spin=-3, rest=2.9),
        dict(fn=_p_bone(7), x=-1, y=-4, r=1.3, vx=2.2, vy=-5, spin=4, rest=-0.1),
        dict(fn=_p_bone(7), x=-4, y=-4, r=1.3, vx=-4.5, vy=-3, spin=-5, rest=0.3),
        dict(fn=_p_sword, x=7, y=-24, r=1.5, vx=6, vy=-6, spin=7, rest=0.12, bounce=0.4),
        dict(fn=_p_shield, x=5, y=-17, r=5, vx=4, vy=-4, spin=3, rest=1.35),
    ]
    for d_ in items:
        d_['vx'] *= 0.55; d_['vy'] *= 0.65
    b = Bits(items, seed=11, T=0.8, g=1.5)
    u = i / (n - 1)
    draw_bits(c, b, u)
    c.glow(0, -25, 10, SOUL, 0.0)
    if i == 1:
        c.flash(WHITE, 0.25)
        # destello de almas escapando
    # chispas de alma que escapan
    for k in range(5):
        px_ = -6 + k * 3 + math.sin(k * 3.1 + i) * 2
        py_ = -20 - u * (14 + k * 3) - 2 * k
        if u < 0.95:
            c.dotw(px_, py_, SOUL if (k + i) % 2 == 0 else '#d8ffe8')


SPECS = {}


# ------------------------------------------------------------------ ARQUERO DE HUESO
CLOAK = Mat(ramp=['#10121e', '#1e2236', '#2f3650', '#46506c', '#66728c'], bevel=1.4, tex=0.28, seed=12)
CLOAK_IN = Mat(ramp=['#080a12', '#10121e', '#1a1e30'], bevel=1.0, dith=0.2)
BOWW = Mat(ramp=['#1c1220', '#33202a', '#56342c', '#7e5034', '#a8744a'], bevel=0.9, tex=0.3, seed=21)
STRING = Mat(ramp=['#8a8a94', '#c8c8c4', '#f0ecd8'], bevel=0.6, dith=0.0)
ARROW = Mat(ramp=['#6a4a32', '#9a7248', '#cfa66a'], bevel=0.6, dith=0.0)
ARROWT = Mat(ramp=['#2e8a5c', '#5cd890', '#c8ffe0', '#ffffff'], emi=True, nooutline=True, bevel=0.9, dith=0.1)


def arq_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(d=0.0, aim=0.15, hx=-3.0, lean=0.08, dy=s * 0.6, walk=False, ph=t, glow=0.0, rel=False, stride=0, lift=0,
             tilt=0.0, eye=0.2, jaw=0.0, sway=s)
    if a == 'walk':
        P.update(walk=True, stride=4.8, lift=2.6, dy=1.6 - 1.0 * abs(math.sin(2 * math.pi * t)), lean=0.24,
                 hx=-2.0, aim=0.25, tilt=0.12)
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(d=w, aim=lerp(0.15, 1.0, w), lean=lerp(0.08, 0.0, w), hx=lerp(-3, -4, w), glow=w, eye=w, dy=lerp(0.6, 1.3, w),
                 tilt=lerp(0, 0.1, w))
    elif a == 'attack':
        d_ = [1.0, 1.0, -0.15, 0.0, 0.0][i]
        P.update(d=d_, aim=[1.0, 1.0, 1.05, 0.85, 0.5][i], lean=[0.0, -0.02, -0.16, -0.08, 0.04][i],
                 hx=[-4, -4.4, -6.0, -5, -4][i], glow=[1.0, 1.0, 0.0, 0.0, 0.0][i], rel=(i == 2), eye=1.0 if i < 4 else 0.5,
                 dy=[1.3, 1.5, 0.5, 0.8, 0.8][i], tilt=[0.1, 0.1, -0.1, 0, 0][i], jaw=[0, 0, 1.5, 1, 0][i])
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(hx=-3 + rx, lean=ln, aim=-0.1, tilt=-0.35 if i == 0 else -0.15, flash=fl, jaw=2, eye=0.7)
    return P


def draw_arquero(c, a, i, n):
    if a == 'death':
        return death_arquero(c, i, n)
    P = arq_pose(a, i, n)
    arquero_body(c, P, a, i, n)
    if 'flash' in P:
        c.flash(WHITE, P['flash'])


def arquero_body(c, P, a, i, n, nobow=False):
    hx, dy, lean = P['hx'], P['dy'], P['lean']
    ph, sw = P['ph'], P['sway']
    hip = (hx, -13.5 + dy)
    sl = (math.sin(lean), -math.cos(lean))
    neck = (hip[0] + 10.5 * sl[0], hip[1] + 10.5 * sl[1])
    sho = (hip[0] + 9 * sl[0], hip[1] + 9 * sl[1])
    if P['walk']:
        f1 = gait(ph, P['stride'], P['lift']); f2 = gait((ph + 0.5) % 1, P['stride'], P['lift'])
    elif a in ('windup', 'attack'):
        f1, f2 = (-5.0, 0), (4.2, 0)
    else:
        f1, f2 = (-3.2, 0), (3.2, 0)
    # capa trasera (detras de todo)
    hem = []
    for k in range(7):
        xx = hip[0] - 7.5 + k * 2.2
        yy = -1.2 - (2.0 if k % 2 else 0) + 0.8 * math.sin(2 * math.pi * ph * 1 + k * 1.3) + (0.8 if a == 'walk' else 0)
        hem.append((xx - lean * 3 - (2 if a == 'walk' else 0) * (k / 6.0), yy))
    with c.part(CLOAK, line=0.5, bevel=1.8) as p:
        p.poly([(neck[0] - 2, neck[1] - 1), (neck[0] + 4.5, neck[1] + 0.5), (hip[0] + 5, hip[1] + 3)] + hem[::-1] +
               [(hip[0] - 7, hip[1] + 2), (neck[0] - 6, neck[1] + 3)])
    leg(c, (hip[0] - 1, hip[1] + 1), (hip[0] - 1 + f1[0], f1[1]), 6.4, 6.4, 0.95, 0.9, BONE_B, bend=-1)
    # pecho (costillas visibles bajo capa abierta)
    with c.at(hip[0] + 4.5 * sl[0], hip[1] + 4.5 * sl[1], lean):
        with c.part(BONE_B, line=0.4, bevel=1.2) as p:
            p.ell(0.5, -1.8, 3.4, 5.4)
        with c.part(DARK) as p:
            for k in range(3):
                p.rect(-2.5, -5.0 + k * 2.4, 3.6, -4.4 + k * 2.4)
    leg(c, (hip[0] + 1, hip[1] + 1), (hip[0] + 1 + f2[0], f2[1]), 6.4, 6.4, 1.0, 0.95, BONE, bend=-1)
    # tela frontal de la capa (faldon)
    with c.part(CLOAK, line=0.5, bevel=1.4) as p:
        p.poly([(hip[0] - 3.6, hip[1] - 1.4), (hip[0] + 4.0, hip[1] - 1.0), (hip[0] + 5.0 + lean * 2, hip[1] + 5.4 + 0.7 * math.sin(ph * 6.28)),
                (hip[0] + 1.0, hip[1] + 7.2), (hip[0] - 4.2, hip[1] + 5.0)])
    # brazo arco (lejano) -> arco
    aim = P['aim']
    ang = lerp(1.05, -0.02, max(0, min(1, aim)))
    e_far = None
    shf = (sho[0] + 0.8, sho[1] + 0.3)
    bh = (shf[0] + 11.2 * math.cos(ang), shf[1] + 11.2 * math.sin(ang))
    if not nobow:
        ef = ik2(shf, bh, 5.6, 5.6, bend=1)
        bone(c, shf, ef, 0.85, BONE_B)
        bone(c, ef, bh, 0.8, BONE_B)
        # arco (curva)
        tilt = -0.1 + 0.2 * aim
        top = (bh[0] - 1.2 + 11.5 * math.sin(-tilt), bh[1] - 11.5 * math.cos(tilt))
        bot = (bh[0] - 1.2 - 11.5 * math.sin(-tilt), bh[1] + 11.5 * math.cos(tilt))
        pts = []
        for k in range(9):
            u = k / 8
            xx = lerp(top[0], bot[0], u) + 4.0 * math.sin(math.pi * u) * (1.0 - 0.5 * P['d'] * 0.0)
            yy = lerp(top[1], bot[1], u)
            pts.append((xx, yy))
        # tensado: las puntas se doblan hacia atras con d
        pts = [(x - 2.2 * P['d'] * (1 - abs(2 * k / 8 - 1)) * 0 - 0.0, y) for k, (x, y) in enumerate(pts)]
        tipsh = 1.8 * P['d']
        pts[0] = (pts[0][0] - tipsh, pts[0][1] + 0.8 * P['d'])
        pts[-1] = (pts[-1][0] - tipsh, pts[-1][1] - 0.8 * P['d'])
        with c.part(BOWW, line=0.3, bevel=0.9) as p:
            p.tube(pts, 1.0, 0.7)
        with c.part(BONE, bevel=0.6) as p:
            p.ell(pts[0][0], pts[0][1], 1.0); p.ell(pts[-1][0], pts[-1][1], 1.0)
        # mano de dibujo
        dh = (bh[0] - 2.5 - 12.0 * P['d'] + 2.0 * max(0, -P['d']) * 3, bh[1] + 0.3)
        if P['d'] < 0:
            dh = (bh[0] - 2.5 - 2.5 * (-P['d']) * 0 - 2.0, bh[1] + 0.3)
        # cuerda
        if P['d'] > 0.02:
            tp, bp = pts[0], pts[-1]
            with c.part(STRING, bevel=0.5, line=0) as p:
                p.line_(tp, dh, 1.0); p.line_(dh, bp, 1.0)
        else:
            with c.part(STRING, bevel=0.5) as p:
                p.line_(pts[0], pts[-1], 1.0)
        # flecha
        if P['d'] > 0.05:
            dirx, diry = bh[0] - dh[0], bh[1] - dh[1]
            L = math.hypot(dirx, diry) or 1
            ux, uy = dirx / L, diry / L
            tipp = (bh[0] + ux * 6.5, bh[1] + uy * 6.5)
            with c.part(ARROW, bevel=0.5) as p:
                p.line_((dh[0] - ux * 1.0, dh[1] - uy * 1.0), tipp, 1.0)
            with c.part(ARROWT) as p:
                p.poly([(tipp[0] + ux * 2.6, tipp[1] + uy * 2.6), (tipp[0] - uy * 1.3, tipp[1] + ux * 1.3), (tipp[0] + uy * 1.3, tipp[1] - ux * 1.3)])
            c.glow(tipp[0], tipp[1], 4.5, SOUL, 0.6 * P['glow'])
        # brazo cercano (cuerda)
        eh = ik2(sho, dh, 5.7, 5.7, bend=1)
        bone(c, sho, eh, 0.95, BONE)
        bone(c, eh, dh, 0.9, BONE)
        with c.part(BONE, bevel=0.6) as p:
            p.ell(dh[0], dh[1], 1.3)
    # cabeza con capucha
    hxn = neck[0] + 3.2 * math.sin(lean + P['tilt']) + 0.8
    hyn = neck[1] - 3.8 * math.cos(lean + P['tilt'])
    skel_head(c, hxn, hyn, lean * 0.6 + P['tilt'], P['jaw'], P['eye'])
    with c.at(hxn, hyn, lean * 0.6 + P['tilt']):
        with c.part(CLOAK, line=0.5, bevel=1.5) as p:
            p.poly([(-6.5, 5.5), (-6.8, -2.5), (-3.5, -6.8), (1.8, -7.2), (4.6, -5.4), (1.8, -3.6), (-0.8, -2.0), (-2.6, 1.0), (-2.8, 5.8)])
        with c.part(CLOAK_IN) as p:
            p.poly([(-2.4, 4.8), (-2.8, 0.8), (-0.6, -1.8), (1.8, -3.2), (0.2, -0.5), (-0.6, 3.5)])
    if P['glow'] > 0.2 and False:
        pass


def _p_arq_bow(c):
    with c.part(BOWW, line=0.3, bevel=0.9) as p:
        p.tube([(-1, -9), (2, -4), (3, 0), (2, 4), (-1, 9)], 1.0, 0.7)


def _p_cloak(c):
    with c.part(CLOAK, line=0.5, bevel=1.8) as p:
        p.poly([(-6, -3), (5, -3), (7, 2), (4, 3.5), (1, 1.5), (-2, 3.5), (-6, 2)])


def death_arquero(c, i, n):
    if i == 0:
        P = arq_pose('hurt', 0, 2)
        arquero_body(c, P, 'hurt', 0, 2)
        c.flash(WHITE, 0.45)
        return
    items = [
        dict(fn=_p_skull, x=-4, y=-29, r=4, vx=-3.2, vy=-8, spin=-5, rest=0.4, bounce=0.35),
        dict(fn=_p_ribs, x=-4.5, y=-20, r=5, vx=-1.8, vy=-4, spin=-2, rest=-0.4),
        dict(fn=_p_pelvis, x=-3, y=-13, r=2.5, vx=-0.6, vy=-3, spin=1, rest=0.1),
        dict(fn=_p_bone(8), x=-6, y=-21, r=1.3, vx=-5, vy=-6, spin=5, rest=0.1),
        dict(fn=_p_bone(8), x=-1, y=-21, r=1.3, vx=2.5, vy=-7, spin=-6, rest=0.25),
        dict(fn=_p_bone(8), x=-2, y=-8, r=1.3, vx=3, vy=-4, spin=6, rest=-0.1),
        dict(fn=_p_bone(8), x=-5, y=-8, r=1.3, vx=-1, vy=-4, spin=-3, rest=3.0),
        dict(fn=_p_arq_bow, x=8, y=-22, r=3, vx=4, vy=-6, spin=7, rest=1.4, bounce=0.4),
        dict(fn=_p_cloak, x=-5, y=-13, r=2.5, vx=-2.2, vy=-2, spin=1.5, rest=0.12, bounce=0.1),
    ]
    for d_ in items:
        d_['vx'] *= 0.55; d_['vy'] *= 0.65
    b = Bits(items, seed=5, T=0.8, g=1.5)
    u = i / (n - 1)
    draw_bits(c, b, u)
    for k in range(5):
        if u < 0.95:
            c.dotw(-8 + k * 3.5 + math.sin(k * 2.3 + i) * 2, -20 - u * (14 + k * 3) - 2 * k, SOUL if (k + i) % 2 == 0 else '#d8ffe8')


# ------------------------------------------------------------------ ZOMBI (pesado 64x64)
FLESHZ = Mat(ramp=['#1a2428', '#34484a', '#587462', '#86a47c', '#b8cf98'], bevel=2.6, tex=0.3, seed=31, bias=0.4)
FLESHZ_B = Mat(ramp=['#141c20', '#2a3a3c', '#46605a', '#6c8a68', '#96b27c'], bevel=2.4, tex=0.3, seed=32, bias=0.3)
BRUISE = Mat(ramp=['#2a1c3a', '#44305a', '#68508a', '#8a70a8'], bevel=1.0, tex=0.2, seed=33)
WOUND = Mat(ramp=['#1c0810', '#4a1020', '#781c30', '#a03040'], bevel=1.0, tex=0.2, seed=34)
ARMOR_R = Mat(ramp=['#1a1824', '#38303a', '#5e4a42', '#8a6a52', '#b89468'], bevel=1.6, tex=0.5, seed=35)
CHAIN = Mat(ramp=['#14161e', '#2c3040', '#4c556c', '#7c88a0'], bevel=0.7, dith=0.3)
TEETH = Mat(ramp=['#5a5440', '#9a9478', '#d0c8a0'], bevel=0.6)
EYEY = Mat(ramp=['#8a7a10', '#d6c030', '#fff080', '#ffffe0'], emi=True, nooutline=True, bevel=0.8, dith=0.1)
GORE = Mat(ramp=['#1c3a18', '#3c6a24', '#6a9c34', '#a8d058'], bevel=1.0, tex=0.2, seed=36)


def zom_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(hx=-3.0, dy=0.0, lean=0.10, ph=t, walk=False, stride=0, lift=0, arm=(1.15, 1.35), arm2=(1.0, 1.25),
             head=0.0, belly=s * 0.5, jaw=1.5, eye=0.4, fist=0.0, flash=0.0)
    if a == 'idle':
        P['dy'] = 0.8 * s
        P['arm'] = (1.2 + 0.08 * s, 1.35)
        P['arm2'] = (1.05 + 0.08 * math.sin(2 * math.pi * t + 1), 1.2)
        P['head'] = 0.05 * math.sin(2 * math.pi * t + 2)
    elif a == 'walk':
        P.update(walk=True, stride=5.5, lift=3.0, dy=-1.5 * abs(math.sin(2 * math.pi * t)) + 0.5, lean=0.18, hx=-1.0)
        P['arm'] = (1.1 + 0.35 * s, 1.4)
        P['arm2'] = (1.1 - 0.35 * s, 1.3)
        P['head'] = 0.1
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(lean=lerp(0.1, -0.28, w), hx=lerp(-3, -6, w), dy=lerp(0, 1.5, w), eye=w, jaw=lerp(1.5, 5, w), head=lerp(0, -0.3, w),
                 belly=0.5 + w)
        P['arm'] = (lerp(1.2, -2.5, w), lerp(1.35, -0.9, w))
        P['arm2'] = (lerp(1.05, -2.2, w), lerp(1.2, -0.7, w))
    elif a == 'attack':
        k = i / (n - 1)
        P['lean'] = kf(k, [(0, -0.28), (0.2, 0.18), (0.4, 0.45), (0.7, 0.4), (1, 0.18)])
        P['hx'] = kf(k, [(0, -6), (0.2, -1), (0.4, 4), (0.7, 4), (1, 1)])
        P['dy'] = kf(k, [(0, 1.5), (0.4, 3.5), (1, 1)])
        s1 = kf(k, [(0, -2.5), (0.2, -0.6), (0.4, 1.15), (0.7, 1.2), (1, 1.0)])
        P['arm'] = (s1, kf(k, [(0, -0.9), (0.4, 0.5), (1, 1.1)]))
        s2 = kf(k, [(0, -2.2), (0.2, -0.5), (0.4, 1.0), (0.7, 1.05), (1, 0.9)])
        P['arm2'] = (s2, kf(k, [(0, -0.7), (0.4, 0.5), (1, 1.1)]))
        P['eye'] = 1.0 if k < 0.8 else 0.4
        P['jaw'] = 5
        P['head'] = kf(k, [(0, -0.3), (0.4, 0.3), (1, 0.1)])
        P['belly'] = 1.0 if k < 0.5 else 0.2
        P['k'] = k
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(hx=-3 + rx * 1.2, lean=ln * 0.9, flash=fl * 0.9, jaw=5, head=-0.3 if i == 0 else -0.15, eye=0.7)
        P['arm'] = (0.2, 0.8) if i == 0 else (0.8, 1.1)
        P['arm2'] = (0.0, 0.6) if i == 0 else (0.6, 1.0)
    return P


def zombi_body(c, P, a='idle', skip_parts=()):
    hx, dy, lean = P['hx'], P['dy'], P['lean']
    ph = P['ph']
    hip = (hx, -23 + dy)
    sl = (math.sin(lean), -math.cos(lean))
    if P['walk']:
        f1 = gait(ph, P['stride'], P['lift']); f2 = gait((ph + 0.5) % 1, P['stride'], P['lift'])
    elif a in ('windup', 'attack'):
        f1, f2 = (-7.0, 0), (6.0, 0)
    else:
        f1, f2 = (-4.5, 0), (4.5, 0)
    # brazo lejano
    chest = (hip[0] + 12 * sl[0], hip[1] + 12 * sl[1])
    shf = (chest[0] + 1, chest[1] - 3)
    e2, h2 = fk(shf, P['arm2'][0], 12.5, P['arm2'][1], 12.5)
    with c.part(FLESHZ_B, line=0.5, bevel=2.2) as p:
        p.limb(shf, e2, 3.4, 3.0)
        p.limb(e2, h2, 3.0, 2.8)
    with c.part(FLESHZ_B, line=0.5, bevel=2.0) as p:
        p.ell(h2[0] + 0.6, h2[1] + 0.6, 3.3)
    # pierna trasera
    leg(c, (hip[0] - 3, hip[1] + 2), (hip[0] - 3 + f1[0], f1[1]), 10.2, 10.2, 4.2, 3.6, FLESHZ_B, bend=-1, footmat=ARMOR_R, footlen=6, footh=3.4)
    # torso: vientre hinchado
    with c.at(hip[0] + 4.0 * sl[0], hip[1] + 4.0 * sl[1], lean):
        bl = P['belly']
        with c.part(FLESHZ, line=0.5, bevel=3.4) as p:
            p.ell(1.0, -9.5, 11.5 + bl * 0.5, 14.0)                 # tronco
            p.ell(3.5, -1.0, 9.5 + bl * 0.6, 8.5 + bl * 0.4)        # barriga hinchada
        with c.part(BRUISE, bevel=1.2) as p:
            p.ell(-2.0, -4.0, 3.2, 2.4, 0.4)
            p.ell(4.6, 0.8, 2.2, 1.6, -0.3)
        with c.part(WOUND, bevel=1.0) as p:
            p.poly([(5.0, -6.5), (8.5, -5.0), (7.5, -2.6), (4.6, -3.5)])
            p.ell(-5, -12, 1.8, 1.2)
        with c.part(TEETH, bevel=0.6) as p:  # costillas expuestas
            for k in range(3):
                p.limb((6.8 + k * 0.4, -5.8 + k * 1.2), (9.0 + k * 0.4, -5.2 + k * 1.2), 0.45)
        # cinturon y taparrabos podrido
        with c.part(ARMOR_R, line=0.5, bevel=1.4) as p:
            p.poly([(-9, 2.0), (12, 2.5), (12, 5.0), (-9, 4.6)])
            p.poly([(-6, 4.6), (4, 5.0), (3, 12), (0, 10), (-3, 13), (-7, 9)])
        # peto oxidado cruzado por cadenas
        with c.part(ARMOR_R, line=0.5, bevel=1.6) as p:
            p.poly([(-8, -20), (3, -23), (6, -15), (4, -9), (-5, -8), (-9, -13)])
        with c.part(WOUND, bevel=0.8) as p:
            p.poly([(-4, -18), (-1, -19), (0, -15)])
        for (x0, y0, x1, y1) in ((-9, -21, 11, 0), (10, -20, -8, 2)):
            nlk = 8
            with c.part(CHAIN, bevel=0.6, line=0.3) as p:
                for k in range(nlk):
                    u = k / (nlk - 1)
                    p.ell(lerp(x0, x1, u), lerp(y0, y1, u) + 1.0 * math.sin(u * 3.14), 1.5, 1.0 if k % 2 else 1.5, 0.5)
    # pierna delantera
    leg(c, (hip[0] + 3, hip[1] + 2), (hip[0] + 3 + f2[0], f2[1]), 10.2, 10.2, 4.4, 3.7, FLESHZ, bend=-1, footmat=ARMOR_R, footlen=6, footh=3.4)
    # cabeza
    nk = (hip[0] + 21 * sl[0] + 0, hip[1] + 21 * sl[1] - 2)
    hd = P['head']
    with c.at(nk[0] + 3.5, nk[1] - 2.0, lean * 0.5 + hd):
        with c.part(FLESHZ, line=0.5, bevel=2.4) as p:
            p.ell(0, 0, 5.6, 5.0)
            p.poly([(-3.5, 3), (4.0, 2.6), (4.2, 5.0 + P['jaw'] * 0.5), (-1.0, 5.8 + P['jaw'] * 0.6)])
        with c.part(BRUISE, bevel=1.0) as p:
            p.ell(-1, -2.5, 3, 1.4)
        with c.part(DARK) as p:
            p.ell(2.8, -0.8, 1.7, 1.5)
            p.ell(-0.6, -0.8, 1.3, 1.2)
            p.poly([(1.0, 3.2), (4.0, 3.0), (4.0, 3.2 + P['jaw'] * 0.5), (1.0, 3.6 + P['jaw'] * 0.5)])
        with c.part(EYEY) as p:
            p.ell(3.0, -0.8, 0.9 + 0.3 * P['eye'], 0.9 + 0.3 * P['eye'])
            p.ell(-0.5, -0.8, 0.7, 0.7)
        c.glow(3.0, -0.8, 3 + 2 * P['eye'], '#ffe050', 0.3 + 0.5 * P['eye'])
        with c.part(TEETH) as p:
            p.rect(0.5, 3.4, 1.4, 4.6); p.rect(2.4, 3.4, 3.3, 4.4)
        with c.part(CHAIN, bevel=0.5) as p:
            p.ell(-4, -5, 1, 0.8)
    # hombrera enorme cercana
    shn = (chest[0] - 1, chest[1] - 3)
    e1, h1 = fk(shn, P['arm'][0], 12.5, P['arm'][1], 12.5)
    with c.part(FLESHZ, line=0.5, bevel=2.2) as p:
        p.limb(shn, e1, 3.8, 3.3)
        p.limb(e1, h1, 3.3, 3.0)
    # grillete y cadena colgando del antebrazo
    ew = (lerp(e1[0], h1[0], 0.75), lerp(e1[1], h1[1], 0.75))
    with c.part(CHAIN, bevel=0.7, line=0.3) as p:
        p.limb((ew[0], ew[1] - 0.6), (ew[0], ew[1] + 0.8), 3.4)
    with c.part(FLESHZ, line=0.5, bevel=2.0) as p:
        p.ell(h1[0] + 0.8, h1[1] + 0.8, 3.9)
    with c.part(WOUND, bevel=0.8) as p:
        p.ell(h1[0] + 1.5, h1[1] + 0.5, 1.2, 0.8)
    with c.part(CHAIN, bevel=0.6, line=0.3) as p:
        for k in range(4):
            p.ell(ew[0] + 0.5 + math.sin(k + P['ph'] * 6.28) * 0.7, ew[1] + 3 + k * 2.0, 1.3, 0.9 if k % 2 else 1.3)
    with c.part(ARMOR_R, line=0.5, bevel=1.8) as p:
        sx, sy = shn[0] - 1, shn[1] - 1
        p.poly([(sx - 5.5, sy + 3), (sx - 4, sy - 3.5), (sx + 2, sy - 6), (sx + 6.5, sy - 2), (sx + 6, sy + 3), (sx, sy + 5)])
    with c.part(ARMOR_R, bevel=0.8) as p:
        p.poly([(shn[0] + 0.5, shn[1] - 6), (shn[0] + 2.0, shn[1] - 10.5), (shn[0] + 3.5, shn[1] - 5.5)])
        p.poly([(shn[0] - 4.0, shn[1] - 4.5), (shn[0] - 6.5, shn[1] - 8.5), (shn[0] - 2.2, shn[1] - 5.2)])
    if 'k' in P and 0.35 < P['k'] < 0.7:
        for q in range(7):
            c.dotw(10 + q * 3.2 + (P['k'] - 0.4) * 14, -1 - (q % 3) * 1.3, '#8a9a8a' if q % 2 else '#586458')


def draw_zombi(c, a, i, n):
    if a == 'death':
        return death_zombi(c, i, n)
    P = zom_pose(a, i, n)
    zombi_body(c, P, a)
    if P['flash']:
        c.flash(WHITE, P['flash'])


def death_zombi(c, i, n):
    if i == 0:
        P = zom_pose('hurt', 0, 2)
        zombi_body(c, P, 'hurt')
        c.flash(WHITE, 0.45)
        return
    u = i / (n - 1)
    P = zom_pose('hurt', 1, 2)
    # fases: 1-2 tambalea y cae de rodillas, 3-6 se derrumba hacia delante
    ang = kf(u, [(0, 0), (0.25, 0.2), (0.5, 0.6), (0.75, 1.35), (1.0, 1.52)])
    drop = kf(u, [(0, 0), (0.25, 9), (0.55, 12), (1, 14)])
    P['lean'] = kf(u, [(0, -0.14), (0.3, 0.1), (1, 0.3)])
    P['dy'] = drop * 0.5
    P['arm'] = (kf(u, [(0, 0.8), (1, 2.6)]), kf(u, [(0, 1.1), (1, 0.3)]))
    P['arm2'] = (kf(u, [(0, 0.6), (1, 2.4)]), kf(u, [(0, 1.0), (1, 0.3)]))
    P['head'] = kf(u, [(0, -0.15), (1, 0.4)])
    P['eye'] = 1 - u
    P['jaw'] = 6
    P['hx'] = -3 + kf(u, [(0, 0), (1, -6)])
    P['walk'] = False
    pivx = -18
    with c.at(pivx, 0.5, ang * (1.0)):
        with c.at(-pivx - 3 + kf(u, [(0, 0), (1, 4)]), 0, 0):
            zombi_body(c, P, 'hurt')
    # piezas desprendidas: hombrera y cadenas
    items = [
        dict(fn=lambda cc: [cc.part(ARMOR_R, line=0.5, bevel=1.8).__enter__().poly([(-5, 2.5), (-3.5, -3), (2, -5), (6, -1.5), (5.5, 2.5), (0, 4)]).finish()], x=4, y=-40, r=4, vx=6, vy=-9, spin=4, rest=0.3),
        dict(fn=lambda cc: [cc.part(CHAIN, bevel=0.6).__enter__().tube([(-4, 0), (0, 1), (4, 0)], 1.1).finish()], x=-2, y=-25, r=1.5, vx=-6, vy=-5, spin=6, rest=0.1),
    ]
    for d_ in items:
        d_['vx'] *= 0.6; d_['vy'] *= 0.6
    b = Bits(items, seed=2, T=0.6, g=3.2, floor=0)
    # no mostrar piezas al principio
    if u > 0.2:
        draw_bits(c, b, min(1.0, (u - 0.2) / 0.8))
    # polvo y icor
    if u > 0.45:
        for q in range(9):
            yy = -1.5 - (q % 3) * 1.4 - (u - 0.45) * 4
            xx = -8 + q * 5 + (u - 0.45) * (q - 4) * 3
            c.dotw(xx, yy, '#6a8a6a' if q % 2 else '#a8d058')


def enemy_sheet(name, cell, pivot, body, drawfn, tint, anims):
    sh = Sheet(name, cell[0], cell[1], pivot, body, tint)
    for (an, n, fps, loop, extra) in anims:
        sh.anim(an, n, fps, loop, drawfn, **extra)
    return sh


def STD(atk, hit=None, box=None, rel=None, muz=None, idle=6, walk=8, ifps=8, wfps=11, fa=15, death=8, dfps=10, wnd=4):
    ex = {}
    for k, v in (('hit', hit), ('box', box), ('rel', rel), ('muzzle', muz)):
        if v is not None:
            ex[k] = v
    return [('idle', idle, ifps, True, {}), ('walk', walk, wfps, True, {}), ('windup', wnd, 11, False, {}),
            ('attack', atk, fa, False, ex), ('hurt', 2, 10, False, {}), ('death', death, dfps, False, {})]


def sheet_esqueleto():
    return enemy_sheet('en_esqueleto', (48, 48), (24, 46), (12, 30), draw_esqueleto, (18, 14, 30),
                       STD(6, hit=[2, 3], box=[4, -30, 22, 28], fa=16))


def sheet_arquero_hueso():
    return enemy_sheet('en_arquero_hueso', (48, 48), (24, 46), (12, 30), draw_arquero, (14, 14, 30),
                       STD(5, rel=2, muz=[15, -22], idle=6, walk=8, fa=14, death=8))


def sheet_zombi():
    return enemy_sheet('en_zombi', (64, 64), (32, 62), (22, 48), draw_zombi, (16, 22, 24),
                       STD(6, hit=[2, 3], box=[8, -44, 28, 44], idle=6, walk=8, ifps=6, wfps=7, fa=9, death=8, dfps=8))


SHEETS = [sheet_esqueleto, sheet_arquero_hueso, sheet_zombi]
