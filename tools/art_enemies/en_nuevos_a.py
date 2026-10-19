"""Enemigos nuevos (lote A): escudero de hueso, clerigo del osario, carbonero de la forja, centinela de cristal."""
from common import *
from humanoid import human
from en_catacumbas import enemy_sheet, STD, DARK, WHITE, BONE, BONE_B, EYE, SOUL, TRAILM

# ------------------------------------------------------------------ materiales
PLATE = Mat(ramp=['#10141c', '#26303c', '#46566a', '#74889a', '#b4c6d2'], bevel=1.4, tex=0.25, seed=31)
PLATE_D = Mat(ramp=['#0a0e14', '#1a222c', '#303c4c', '#4e6074', '#7a8ea0'], bevel=1.4, tex=0.25, seed=32)
RUSTY = Mat(ramp=['#2a1612', '#5a2c1e', '#8a4a2a', '#b8743a', '#dca262'], bevel=1.0, tex=0.45, dith=0.5, seed=33)
GOLDT = Mat(ramp=['#3a2a0e', '#7a5a1a', '#b88a2a', '#e8c050', '#fff0a0'], bevel=0.8, seed=34)
RUNE = Mat(ramp=['#1c8a52', '#3cd07a', '#8affb8', '#e8fff0'], emi=True, nooutline=True, bevel=0.8, dith=0.1)
ROBE = Mat(ramp=['#0a1410', '#14281e', '#244a38', '#3a7054', '#5c9a78'], bevel=2.0, tex=0.3, seed=35)
ROBE_D = Mat(ramp=['#060c0a', '#0e1c16', '#18322a', '#264c3c', '#3a6a56'], bevel=2.0, tex=0.3, seed=36)
ROBE_V = Mat(ramp=['#0c1812', '#1a3426', '#2e5c44', '#4a8a68', '#78b894'], bevel=2.0, tex=0.3, seed=37)
HOOD = Mat(ramp=['#060a08', '#0e1812', '#18281e', '#243c2e'], bevel=2.2, tex=0.25, seed=38)
LANT = Mat(ramp=['#1c8a52', '#4ae88a', '#b0ffd0', '#ffffff'], emi=True, nooutline=True, bevel=2.0, dith=0.15)
SOOT = Mat(ramp=['#120c0a', '#2a1c16', '#4a3226', '#72503a', '#a07852'], bevel=1.8, tex=0.4, seed=41)
SOOT_D = Mat(ramp=['#0a0605', '#1c120e', '#32221a', '#503828', '#745238'], bevel=1.8, tex=0.4, seed=42)
SKIN_G = Mat(ramp=['#2a1810', '#5a3422', '#8a5a38', '#b88858', '#e0b484'], bevel=1.4, seed=43)
CANVAS = Mat(ramp=['#1a1410', '#38281c', '#5e4630', '#8a6c48', '#b8946a'], bevel=2.0, tex=0.45, seed=44)
BOMB = Mat(ramp=['#08080c', '#14141c', '#262632', '#3c3c4c', '#5e5e72'], bevel=2.6, tex=0.1, seed=45)
EMBER = Mat(ramp=['#8a2a0a', '#e86a14', '#ffb040', '#fff0a0', '#ffffff'], emi=True, nooutline=True, bevel=1.6, dith=0.2)
FIREC = '#FF9A2A'
ICE = Mat(ramp=['#16385a', '#2a6a9a', '#5ab4dc', '#a4e8ff', '#eaffff'], bevel=1.6, tex=0.1, seed=51, dith=0.3)
ICE_D = Mat(ramp=['#0c2036', '#16405e', '#2a6a8c', '#4a9cbc', '#82cce0'], bevel=1.6, tex=0.1, seed=52, dith=0.3)
ROCKB = Mat(ramp=['#10141e', '#222a3a', '#3a465c', '#58698a', '#8096b4'], bevel=2.2, tex=0.5, seed=53)
CORE = Mat(ramp=['#2a8ac8', '#5acaff', '#b8f0ff', '#ffffff'], emi=True, nooutline=True, bevel=2.0, dith=0.1)
ICEC = '#7AF0FF'


def hfeet(w):
    return (lerp(-3.5, -6, w), 0), (lerp(3.5, 5, w), 0)


# ================================================================== ESCUDERO DE HUESO
def esc_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(hx=-4.0, dy=0.5 * s, lean=0.02, ph=t, walk=False, stride=0, lift=0, rear=(7, -15), front=(-1, -13), head=0.0, flash=0.0, glow=0.0, bash=0.0, shx=0.0)
    if a == 'idle':
        P['rear'] = (7, -15 + 0.5 * s)
    elif a == 'walk':
        P.update(walk=True, stride=4.0, lift=2.4, dy=-0.8 * abs(math.sin(2 * math.pi * t)) + 0.4, lean=0.1, hx=-3)
        P['rear'] = (7.5, -15 + 0.6 * s); P['front'] = (-2, -13 + 0.5 * s)
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(lean=lerp(0.02, -0.22, w), hx=lerp(-4, -7, w), dy=lerp(0, 1.6, w), glow=w, head=-0.1 * w)
        P['rear'] = (lerp(7, 1, w), lerp(-15, -17, w)); P['front'] = (lerp(-1, -4, w), lerp(-13, -18, w))
        P['feet'] = hfeet(w)
    elif a == 'attack':
        P['lean'] = [-0.22, 0.12, 0.38, 0.32, 0.1][i]
        P['hx'] = [-7, -3, 3, 2.5, -2][i]
        P['dy'] = [1.6, 2.4, 3.0, 2.4, 0.6][i]
        P['rear'] = [(1, -17), (6, -16), (14, -15), (13.5, -15), (9, -15)][i]
        P['front'] = [(-4, -18), (-1, -16), (4, -13), (3, -13), (0, -13)][i]
        P['glow'] = [1.0, 1.0, 1.0, 0.6, 0.0][i]
        P['head'] = [-0.1, 0.1, 0.25, 0.2, 0.0][i]
        P['bash'] = [0, 0.3, 1.0, 0.8, 0.0][i]
        P['feet'] = (-6, 0), ([5, 6, 8, 8, 6][i], 0)
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(hx=-4 + rx, lean=ln, flash=fl, head=-0.3 if i == 0 else -0.1)
        P['rear'] = (4, -14) if i == 0 else (6.5, -15); P['front'] = (-3, -11)
    return P


M_ESC = dict(skin=BONE, cloth=PLATE_D, cloth_d=PLATE_D, boot=PLATE, boot_d=PLATE_D, vest=PLATE, vest_d=PLATE_D)


def esc_head(c, x, y, ang, P):
    with c.at(x, y, ang):
        with c.part(BONE, line=0.5, bevel=1.6) as p:
            p.ell(0, 0.4, 4.1, 3.9)
            p.poly([(-1.5, 2.6), (3.4, 2.4), (3.8, 4.4), (-0.5, 5.0), (-2.2, 3.6)])      # mandibula
        with c.part(DARK) as p:
            p.ell(2.6, 0.2, 1.1, 1.4); p.ell(0.2, 0.1, 1.0, 1.3)
        with c.part(RUNE) as p:
            p.ell(2.7, 0.2, 0.6 + 0.2 * P['glow'], 0.75); p.ell(0.3, 0.1, 0.5, 0.65)
        c.glow(2.7, 0.2, 2.2, SOUL, 0.25 + 0.4 * P['glow'])
        with c.part(PLATE, line=0.5, bevel=1.8) as p:       # yelmo de olla abollado
            p.poly([(-4.8, 1.4), (-5.2, -3.4), (-2.4, -5.6), (2.8, -5.4), (4.8, -3.2), (4.4, -1.2), (2.2, -1.6), (-2.2, -1.6), (-3.2, 2.2)])
        with c.part(PLATE_D, bevel=0.8) as p:
            p.rect(3.0, -1.5, 4.0, 3.6)                                                       # nasal
        with c.part(RUSTY, bevel=0.8) as p:
            p.limb((-4.8, -2.6), (4.6, -3.0), 0.55)                                           # banda oxidada
            p.ell(-1.0, -5.0, 0.9)
        if not P.get('nohorn'):                                                               # cuernos de hueso (en la muerte se van con el yelmo)
            with c.part(BONE, line=0.4, bevel=0.9) as p:
                p.poly([(-4.4, -3.2), (-5.8, -4.2), (-6.0, -9.0), (-4.4, -6.6), (-3.2, -5.2)])
                p.poly([(2.8, -5.0), (4.8, -6.0), (5.4, -11.6), (3.6, -8.2), (1.6, -5.6)])
        with c.part(RUSTY, line=0.4, bevel=0.9) as p:                                         # cresta
            p.poly([(-2.6, -5.4), (-1.4, -9.8), (1.6, -9.0), (3.0, -5.4)])


def esc_front(c, P, rear, front):
    """Escudo de torre en la mano cercana + la maza en la lejana."""
    hx_, hy_ = rear
    bash = P['bash']
    with c.at(hx_ + 3.6, hy_ - 2.2, 0.04):
        with c.part(PLATE, line=0.6, bevel=2.0) as p:               # escudo de torre grande (cubre medio cuerpo)
            p.poly([(-6.6, -14.0), (8.6, -13.6), (9.6, -4.0), (8.8, 6.0), (1.2, 15.0), (-5.8, 7.0), (-7.6, -4.0)])
        with c.part(PLATE_D, line=0.5, bevel=1.0) as p:
            p.poly([(-6.6, -14.0), (-2.0, -13.9), (-1.2, 8.5), (1.2, 15.0), (-5.8, 7.0), (-7.6, -4.0)])      # cara en sombra
        with c.part(RUSTY, line=0.4, bevel=1.0) as p:               # refuerzos oxidados y remaches
            p.poly([(-7.2, -8.4), (9.4, -8.6), (9.4, -6.4), (-7.4, -6.2)])
            p.poly([(-7.0, 3.2), (9.0, 3.0), (8.6, 5.0), (-6.6, 5.4)])
            p.poly([(-6.6, -14.0), (8.6, -13.6), (8.7, -12.2), (-6.6, -12.6)])           # remate superior
        with c.part(GOLDT, bevel=0.8) as p:
            p.ell(0.8, -1.4, 2.7)                                                          # umbo
        with c.part(BONE, bevel=0.7, line=0.3) as p:                # calavera emblema
            p.ell(0.8, -10.6, 2.6, 2.3)
            p.rect(-0.6, -9.2, 2.2, -7.6)
        with c.part(DARK) as p:
            p.ell(-0.2, -10.8, 0.7, 0.8); p.ell(1.8, -10.8, 0.7, 0.8)
        with c.part(RUNE) as p:
            p.rect(0.4, 7.0, 1.4, 9.0)
            p.limb((0.8, -2.2), (0.8, -0.6), 0.45)
        c.glow(0.8, -1.4, 5.0, SOUL, 0.10 + 0.55 * P['glow'])
        with c.part(DARK) as p:
            p.poly([(5.4, -13.4), (6.5, -9.0), (5.2, -7.8), (6.1, -5.8), (4.6, -5.2), (4.4, -10.4)])      # grieta
    # mano agarrando
    with c.part(BONE, bevel=0.6) as p:
        p.ell(hx_ - 1.0, hy_ + 1.0, 1.5)
    if bash > 0.7:
        for q in range(6):
            c.dotw(hx_ + 11 + (q % 3) * 2.2, hy_ - 9 + q * 3.4, '#e8fff0' if q % 2 else SOUL)
        c.glow(hx_ + 7, hy_ - 1, 9, SOUL, 0.25)


def esc_weapon(c, P, rear, front):
    fx, fy = front
    ang = 1.1 + (-0.6 if P['glow'] > 0.5 else 0)
    d = (math.cos(ang), math.sin(ang))
    with c.part(RUSTY, line=0.4, bevel=0.9) as p:
        p.limb((fx - d[0] * 3, fy - d[1] * 3), (fx + d[0] * 8, fy + d[1] * 8), 0.9)
    with c.part(PLATE, line=0.4, bevel=1.2) as p:
        p.ell(fx + d[0] * 9, fy + d[1] * 9, 2.6, 2.6)
    with c.part(PLATE_D, bevel=0.8) as p:
        for k in range(4):
            a2 = k * 1.57 + 0.4
            p.ell(fx + d[0] * 9 + math.cos(a2) * 2.9, fy + d[1] * 9 + math.sin(a2) * 2.9, 0.9)


def draw_escudero(c, a, i, n):
    if a == 'death':
        return death_escudero(c, i, n)
    P = esc_pose(a, i, n)
    human(c, P, a, M_ESC, esc_head, esc_weapon, front_cb=esc_front, hip_h=13.5)
    if P['flash']:
        c.flash(WHITE, P['flash'])
    if a == 'windup' and i == n - 1:
        c.flash(SOUL, 0.08)


def _p_shield(c):
    with c.part(PLATE, line=0.6, bevel=1.8) as p:
        p.poly([(-4.2, -10.8), (4.4, -10.4), (5.0, -3), (4.6, 5.0), (0.6, 10.8), (-3.8, 5.6), (-4.8, -3)])
    with c.part(RUSTY, bevel=1.0) as p:
        p.poly([(-4.4, -4.2), (4.8, -4.4), (4.8, -2.2), (-4.6, -2.0)])
    with c.part(GOLDT, bevel=0.8) as p:
        p.ell(0.4, -1.0, 2.0)


def _p_helm(c):
    with c.part(PLATE, line=0.5, bevel=1.8) as p:
        p.poly([(-4.8, 1.4), (-5.2, -3.4), (-2.4, -5.6), (2.8, -5.4), (4.8, -3.2), (4.4, 1.4)])
    with c.part(BONE, bevel=0.8) as p:
        p.poly([(-4.0, -2.4), (-5.8, -3.0), (-6.6, -6.2), (-3.4, -4.4)])
        p.poly([(3.0, -3.8), (5.0, -4.0), (6.4, -6.8), (3.6, -5.4)])
    with c.part(DARK) as p:
        p.ell(1.0, 2.0, 1.8, 1.2)


def _p_bone(c):
    with c.part(BONE, bevel=1.2) as p:
        p.limb((-4, 0), (4, 0), 0.9); p.ell(-4, 0, 1.2); p.ell(4, 0, 1.2)


def death_escudero(c, i, n):
    if i == 0:
        human(c, esc_pose('hurt', 0, 2), 'hurt', M_ESC, esc_head, esc_weapon, front_cb=esc_front)
        c.flash(WHITE, 0.45)
        return
    u = i / (n - 1)
    P = esc_pose('hurt', 1, 2)
    P['nohorn'] = True
    ang = kf(u, [(0, 0), (0.35, -0.35), (0.7, -1.2), (1.0, -1.57)])
    P['feet'] = (kf(u, [(0, -3), (1, -6)]), 0), (kf(u, [(0, 3), (1, 5)]), 0)
    P['glow'] = 0
    with c.at(2 + 3 * u, 0, ang):
        human(c, P, 'idle', M_ESC, esc_head, lambda cc, PP, r, f: None, hip_h=13.5)
    if u < 0.5:
        items = [dict(fn=_p_shield, x=8, y=-17, r=5, vx=6, vy=-5, spin=3, rest=1.45, bounce=0.3),
                 dict(fn=_p_helm, x=-2, y=-31, r=3, vx=-4, vy=-8, spin=-5, rest=0.3, bounce=0.4)]
    else:
        items = [dict(fn=_p_shield, x=8, y=-17, r=5, vx=6, vy=-5, spin=3, rest=1.45, bounce=0.3),
                 dict(fn=_p_helm, x=-2, y=-31, r=3, vx=-4, vy=-8, spin=-5, rest=0.3, bounce=0.4),
                 dict(fn=_p_bone, x=-5, y=-20, r=1.2, vx=-6, vy=-6, spin=5, rest=0.15),
                 dict(fn=_p_bone, x=-1, y=-9, r=1.2, vx=3, vy=-5, spin=6, rest=0.05)]
    for d_ in items:
        d_['vx'] *= 0.55; d_['vy'] *= 0.65
    b = Bits(items, seed=21, T=0.8, g=1.5)
    draw_bits(c, b, u)
    if u > 0.55:
        c.dissolve(min(1.0, (u - 0.55) * 1.6), up=0.3, seed=2)
    for k in range(5):
        if u < 0.95:
            c.dotw(-6 + k * 3 + math.sin(k * 3.1 + i) * 2, -20 - u * (14 + k * 3) - 2 * k, SOUL if (k + i) % 2 == 0 else '#d8ffe8')


def sheet_escudero_hueso():
    return enemy_sheet('en_escudero_hueso', (48, 48), (24, 46), (13, 32), draw_escudero, (16, 20, 30),
                       STD(5, hit=[2, 3], box=[6, -30, 24, 28], idle=6, walk=8, ifps=7, wfps=9, fa=13, death=8))


# ================================================================== CLERIGO DEL OSARIO
def cle_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(hx=-3.0, dy=0.7 * s, lean=0.02, ph=t, walk=False, stride=0, lift=0, grip=(5, -14), axa=-1.5, head=0.0, flash=0.0, glow=0.0, cast=0.0, sway=s)
    if a == 'idle':
        P['grip'] = (5, -14 + 0.5 * s)
    elif a == 'walk':
        P.update(walk=True, stride=3.6, lift=2.0, dy=-0.7 * abs(math.sin(2 * math.pi * t)) + 0.4, lean=0.1, hx=-2)
        P['grip'] = (5, -14 + 0.7 * s)
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(lean=lerp(0.02, -0.1, w), hx=lerp(-3, -4, w), dy=lerp(0, 1.0, w), glow=w, head=-0.12 * w, cast=w)
        P['grip'] = (lerp(5, 3, w), lerp(-14, -22, w)); P['axa'] = lerp(-1.5, -1.45, w)
        P['feet'] = hfeet(w * 0.5)
    elif a == 'attack':
        P['lean'] = [-0.1, 0.04, 0.2, 0.12, 0.04][i]
        P['hx'] = [-4, -3, 0, -1, -2][i]
        P['dy'] = [1.0, 0.2, 1.6, 1.0, 0.4][i]
        P['grip'] = [(3, -22), (4, -20), (7, -12), (6.5, -13), (5, -14)][i]
        P['axa'] = [-1.45, -1.1, -0.35, -0.7, -1.4][i]
        P['glow'] = [1.0, 1.0, 1.0, 0.6, 0.0][i]
        P['cast'] = [1.0, 1.0, 1.0, 0.5, 0.0][i]
        P['head'] = [-0.12, 0.0, 0.2, 0.1, 0.0][i]
        P['feet'] = (-4.5, 0), (4.5, 0)
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(hx=-3 + rx, lean=ln, flash=fl, head=-0.3 if i == 0 else -0.1)
        P['grip'] = (2, -12) if i == 0 else (4.5, -13); P['axa'] = -1.0 if i == 0 else -1.4
    return P


M_CLE = dict(skin=BONE, cloth=ROBE, cloth_d=ROBE_D, boot=ROBE_D, boot_d=ROBE_D, vest=ROBE_V, vest_d=ROBE)


def cle_head(c, x, y, ang, P):
    with c.at(x, y, ang):
        with c.part(BONE, line=0.5, bevel=1.6) as p:
            p.ell(0.3, 0.5, 3.6, 3.5)
            p.poly([(-1.2, 2.4), (3.0, 2.2), (3.2, 4.0), (-0.4, 4.4), (-1.8, 3.2)])
        with c.part(DARK) as p:
            p.ell(2.2, 0.5, 1.0, 1.3); p.ell(-0.1, 0.4, 0.9, 1.2)
        with c.part(RUNE) as p:
            p.ell(2.3, 0.5, 0.55 + 0.25 * P['glow'], 0.7); p.ell(-0.0, 0.4, 0.5, 0.62)
        c.glow(2.3, 0.5, 2.4, SOUL, 0.3 + 0.4 * P['glow'])
        with c.part(HOOD, line=0.5, bevel=2.2) as p:                   # capucha
            p.poly([(-5.6, 5.2), (-6.4, -1), (-4.2, -5.4), (0.4, -6.8), (4.4, -4.8), (3.8, -2.6), (1, -2.4), (-1.4, -1.0), (-3.0, 2.0), (-3.4, 6.0)])
        with c.part(GOLDT, bevel=0.6) as p:
            p.limb((-4.9, -3.4), (3.8, -4.4), 0.5)


def cle_back(c, hip, neck, sho, lean, ph):
    sw = math.sin(ph * 6.283)
    with c.part(ROBE_D, line=0.5, bevel=2.2) as p:              # manto trasero
        p.poly([(neck[0] - 3.5, neck[1] - 1), (neck[0] + 1.5, neck[1] - 1), (hip[0] + 1, hip[1] + 8), (hip[0] - 8 - lean * 4 + sw * 0.8, hip[1] + 13.5), (neck[0] - 9, neck[1] + 4)])


def cle_torso(c, P):
    with c.part(ROBE, line=0.5, bevel=2.2) as p:                # falda de la tunica
        p.poly([(-5, -1), (5, -1.4), (6.4, 6), (5.4, 10.8), (2, 9.4), (-1, 11.2), (-4, 9.6), (-6.4, 11), (-6.2, 5)])
    with c.part(GOLDT, bevel=0.7) as p:
        p.poly([(-5.9, 9.6), (-4, 8.6), (-1, 10.2), (2, 8.6), (5.2, 9.8), (5.4, 10.9), (2, 9.6), (-1, 11.2), (-4, 9.8), (-6.2, 10.9)])   # dobladillo
        p.rect(-0.7, -10.0, 0.7, 7.0)                                                                                                        # cinta central
    with c.part(ROBE_V, line=0.4, bevel=1.6) as p:
        p.poly([(-4.8, -11.6), (4.4, -12.2), (5.4, -8.6), (-5.4, -8.0)])                                                                     # esclavina
    with c.part(BONE, bevel=0.8) as p:
        p.ell(0.2, -7.0, 1.4)                                                                                                                # amuleto
    with c.part(RUNE) as p:
        p.ell(0.2, -7.0, 0.7)


def cle_front(c, P, rear, front):
    """Baston con calavera y farol de almas, sujeto por ambas manos."""
    gx, gy = rear
    ax = P['axa']
    d = (math.cos(ax), math.sin(ax)); nr = (-d[1], d[0])
    base = (gx - d[0] * 5, gy - d[1] * 5)
    top = (gx + d[0] * 17, gy + d[1] * 17)
    with c.part(Mat(ramp=['#140c0a', '#2a1a14', '#46301e', '#684a2c'], bevel=0.8, tex=0.3, seed=7), line=0.4, bevel=0.8) as p:
        p.limb(base, top, 0.95)
    # calavera + farol arriba
    with c.part(BONE, line=0.4, bevel=1.2) as p:
        p.ell(top[0] + d[0] * 2, top[1] + d[1] * 2, 2.8, 2.5)
    with c.part(DARK) as p:
        p.ell(top[0] + d[0] * 2.4 + nr[0] * 1.0, top[1] + d[1] * 2.4 + nr[1] * 1.0, 0.8, 0.9)
        p.ell(top[0] + d[0] * 2.4 - nr[0] * 1.0, top[1] + d[1] * 2.4 - nr[1] * 1.0, 0.8, 0.9)
    lamp = (top[0] + d[0] * 6.4, top[1] + d[1] * 6.4)
    r = 2.1 + 1.3 * P['glow']
    with c.part(LANT, bevel=1.4) as p:
        p.ell(lamp[0], lamp[1], r, r * 1.1)
    c.glow(lamp[0], lamp[1], 6 + 6 * P['glow'], SOUL, 0.35 + 0.5 * P['glow'])
    with c.part(GOLDT, bevel=0.6) as p:
        p.limb((lamp[0] - nr[0] * 2.6, lamp[1] - nr[1] * 2.6), (lamp[0] + nr[0] * 2.6, lamp[1] + nr[1] * 2.6), 0.5)
    if P['cast'] > 0.5:
        for k in range(6):
            aa = k * 1.047 + P['ph'] * 6.283
            c.dotw(lamp[0] * 1.0 + math.cos(aa) * (7 + 2 * P['cast']), lamp[1] + math.sin(aa) * (7 + 2 * P['cast']), '#e8fff0' if k % 2 else SOUL)


def cle_weapon(c, P, rear, front):
    pass


def draw_clerigo(c, a, i, n):
    if a == 'death':
        return death_clerigo(c, i, n)
    P = cle_pose(a, i, n)
    human(c, P, a, M_CLE, cle_head, cle_weapon, back_fn=cle_back, torso_extra=cle_torso, front_cb=cle_front, legs=(6.6, 6.6))
    if P['flash']:
        c.flash(WHITE, P['flash'])
    if a == 'windup' and i == n - 1:
        c.flash(SOUL, 0.1)


def _p_staff(c):
    with c.part(Mat(ramp=['#140c0a', '#2a1a14', '#46301e', '#684a2c'], bevel=0.8, tex=0.3, seed=7), line=0.4, bevel=0.8) as p:
        p.limb((-11, 0), (11, 0), 0.95)
    with c.part(LANT, bevel=1.4) as p:
        p.ell(14, 0, 2.2)


def _p_skull(c):
    with c.part(BONE, line=0.4, bevel=1.4) as p:
        p.ell(0, 0, 3.6, 3.4)
    with c.part(DARK) as p:
        p.ell(1, 0, 1.0, 1.2); p.ell(-1, 0, 0.9, 1.1)


def death_clerigo(c, i, n):
    if i == 0:
        human(c, cle_pose('hurt', 0, 2), 'hurt', M_CLE, cle_head, cle_weapon, back_fn=cle_back, torso_extra=cle_torso, front_cb=cle_front)
        c.flash(WHITE, 0.45)
        return
    u = i / (n - 1)
    P = cle_pose('hurt', 1, 2)
    P['glow'] = 0
    ang = kf(u, [(0, 0), (0.4, -0.3), (0.75, -1.1), (1.0, -1.5)])
    P['feet'] = (kf(u, [(0, -3), (1, -6)]), 0), (kf(u, [(0, 3), (1, 5)]), 0)
    with c.at(2 + 3 * u, 0, ang):
        human(c, P, 'idle', M_CLE, cle_head, cle_weapon, back_fn=cle_back, torso_extra=cle_torso)
    items = [dict(fn=_p_staff, x=9, y=-24, r=2, vx=6, vy=-6, spin=5, rest=0.1, bounce=0.35),
             dict(fn=_p_skull, x=-1, y=-31, r=3, vx=-4, vy=-7, spin=-4, rest=0.2, bounce=0.4)]
    for d_ in items:
        d_['vx'] *= 0.55; d_['vy'] *= 0.65
    b = Bits(items, seed=9, T=0.8, g=1.5)
    draw_bits(c, b, u)
    if u > 0.5:
        c.dissolve(min(1.0, (u - 0.5) * 1.8), up=0.3, seed=5)
    # almas liberadas
    for k in range(7):
        if u < 0.97:
            c.dotw(-8 + k * 2.6 + math.sin(k * 2.3 + i) * 2, -14 - u * (18 + k * 3) - 2 * k, SOUL if (k + i) % 2 == 0 else '#d8ffe8')
    if u > 0.2:
        c.glow(-1, -22 - u * 10, 6, SOUL, 0.25 * (1 - u))


def sheet_clerigo_osario():
    return enemy_sheet('en_clerigo_osario', (48, 48), (24, 46), (12, 30), draw_clerigo, (14, 22, 20),
                       STD(5, rel=2, idle=6, walk=8, ifps=7, wfps=9, fa=12, death=8))


# ================================================================== CARBONERO DE LA FORJA
def car_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(hx=-3.0, dy=0.5 * s, lean=0.1, ph=t, walk=False, stride=0, lift=0, rear=(4, -9), front=(-1, -8), head=0.0, flash=0.0, glow=0.0, fuse=0.0, bomb=0.0, big=0.0)
    if a == 'idle':
        P['rear'] = (5, -9 + 0.5 * s); P['front'] = (-1, -8 + 0.4 * s)
    elif a == 'walk':
        P.update(walk=True, stride=5.6, lift=3.2, dy=-1.4 * abs(math.sin(2 * math.pi * t)) + 0.6, lean=0.36, hx=-1)
        P['rear'] = (5 + s * 2, -10 + 1.2 * s); P['front'] = (0 - s * 2, -9 - 1.2 * s)
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(lean=lerp(0.1, -0.12, w), hx=lerp(-3, -4, w), dy=lerp(0, 1.4, w), fuse=w, glow=w, bomb=1.0, big=w)
        P['rear'] = (lerp(5, 5.5, w), lerp(-9, -23, w)); P['front'] = (lerp(-1, 1.5, w), lerp(-8, -22, w))
        P['feet'] = (lerp(-3.5, -5, w), 0), (lerp(3.5, 5, w), 0)
        P['head'] = -0.2 * w
    elif a == 'attack':
        P.update(lean=[-0.12, 0.2, 0.3, 0.1][i % 4], hx=-4, dy=[1.4, 0.2, 0.0, 0.6][i % 4], fuse=1.0, glow=1.0, bomb=[1.0, 1.0, 0.0, 0.0][i % 4], big=1.0)
        P['rear'] = [(5.5, -23), (8, -18), (11, -13), (8, -10)][i % 4]; P['front'] = [(1.5, -22), (5, -17), (8, -12), (4, -9)][i % 4]
        P['feet'] = (-5, 0), (5, 0)
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(hx=-3 + rx, lean=ln, flash=fl, head=-0.3 if i == 0 else -0.1)
        P['rear'] = (3, -8) if i == 0 else (5, -9); P['front'] = (-2, -7)
    return P


M_CAR = dict(skin=SKIN_G, cloth=SOOT, cloth_d=SOOT_D, boot=SOOT_D, boot_d=SOOT_D, vest=CANVAS, vest_d=SOOT)


def car_head(c, x, y, ang, P):
    with c.at(x, y, ang):
        with c.part(SKIN_G, line=0.5, bevel=1.8) as p:
            p.ell(0, 0.4, 4.3, 4.1)
        with c.part(SOOT_D, bevel=1.0) as p:                  # tizne
            p.ell(1.4, 2.4, 3.4, 1.7)
        with c.part(EMBER) as p:
            p.ell(2.6, -0.2, 0.9, 1.0)
        with c.part(DARK) as p:
            p.poly([(3.6, 2.4), (4.6, 3.2), (3.4, 3.4)])
            p.rect(0.4, 2.6, 3.6, 3.2)                          # sonrisa
        with c.part(PLATE_D, line=0.5, bevel=1.4) as p:        # gafas de forjador
            p.limb((-3.6, -1.2), (4.2, -1.6), 1.4)
        with c.part(EMBER, bevel=0.8) as p:
            p.ell(2.6, -1.4, 1.5, 1.2); p.ell(-0.4, -1.3, 1.4, 1.2)
        c.glow(2.6, -1.4, 3.0, FIREC, 0.35 + 0.3 * P['glow'])
        with c.part(SOOT, line=0.5, bevel=2.0) as p:           # pañuelo / gorro
            p.poly([(-4.6, -2.0), (-3.2, -5.4), (0.6, -6.4), (4.0, -4.6), (4.6, -2.4), (-0.6, -3.6)])
            p.poly([(-4.4, -1.4), (-7.0, 1.0), (-5.0, 2.0), (-3.4, 0.0)])


def car_back(c, hip, neck, sho, lean, ph):
    """Saco enorme de bombas a la espalda, con mechas chispeantes."""
    sw = math.sin(ph * 6.283)
    sx, sy = hip[0] - 5.5 - lean * 4, hip[1] - 6
    with c.at(sx, sy, -0.15 + lean * 0.6):
        with c.part(CANVAS, line=0.6, bevel=2.6) as p:
            p.poly([(-6.0, 6.0), (-7.4, -0.6), (-5.2, -6.0), (-1.4, -7.6), (3.4, -5.6), (4.8, 0.4), (3.6, 6.4)])
        with c.part(SOOT_D, bevel=0.8) as p:
            p.limb((-5.8, 1.6), (3.6, 2.2), 0.8)                  # cuerda
        for k, (bx, by) in enumerate([(-4.4, -6.4), (-0.8, -8.2), (2.4, -6.4)]):
            with c.part(BOMB, line=0.4, bevel=1.8) as p:
                p.ell(bx, by, 2.0)
            with c.part(SOOT_D, bevel=0.6) as p:
                p.limb((bx, by - 1.6), (bx + 0.6, by - 3.4), 0.35)
            c.dot(bx + 0.8, by - 3.6, '#ffe8a0' if (k + int(ph * 8)) % 2 else '#ff9a2a')
        c.glow(-1, -8, 8, FIREC, 0.14)


def car_weapon(c, P, rear, front):
    pass


def car_front(c, P, rear, front):
    """Bomba que sostiene: pequeña en reposo, grande y encendida en la mecha."""
    if P['bomb'] <= 0:
        return
    bx, by = (rear[0] + front[0]) / 2 + 1.5, (rear[1] + front[1]) / 2 - 2.5
    r = 3.4 + 2.2 * P['big']
    with c.part(BOMB, line=0.5, bevel=2.4) as p:
        p.ell(bx, by, r)
    with c.part(PLATE_D, bevel=0.8) as p:
        p.limb((bx - r * 0.9, by), (bx + r * 0.9, by), 0.6)
    # mecha
    fx, fy = bx + 1.2, by - r - 1.6
    with c.part(SOOT_D, bevel=0.6) as p:
        p.tube([(bx + 0.6, by - r + 0.6), (bx + 1.8, by - r - 1.0), (fx, fy)], 0.5)
    k = int(P['ph'] * 12)
    c.dotw(fx + 0.4, fy - 0.6, '#ffffff' if k % 2 else '#ffe8a0')
    c.dotw(fx - 0.6 + (k % 3), fy - 1.8, '#ff9a2a')
    if P['fuse'] > 0.1:
        c.dotw(fx + 1.8, fy - 2.6 - (k % 2), '#ffd25a')
        c.dotw(fx - 1.6, fy - 2.0 + (k % 3) * 0.6, '#ffffff')
    c.glow(fx, fy, 3.0 + 5 * P['fuse'], FIREC, 0.4 + 0.5 * P['fuse'])
    c.glow(bx, by, r + 2, FIREC, 0.10 + 0.4 * P['glow'])


def draw_carbonero(c, a, i, n):
    if a == 'death':
        return death_carbonero(c, i, n)
    P = car_pose(a, i, n)
    human(c, P, a, M_CAR, car_head, car_weapon, back_fn=car_back, front_cb=car_front, hip_h=10.0, legs=(5.0, 5.2), thick=(2.2, 2.0), arm_len=(4.6, 4.8))
    if P['flash']:
        c.flash(WHITE, P['flash'])
    if a == 'windup':
        c.flash('#ff9a2a', 0.10 * ((i + 1) / n))
    if a == 'attack':
        c.flash('#ffe8a0', [0.5, 0.35, 0.25, 0.1][i % 4])


def death_carbonero(c, i, n):
    """Estalla: bola de fuego que crece y se apaga, con humo y tizne."""
    u = i / (n - 1)
    if i == 0:
        draw_carbonero_hurt(c)
        c.flash(WHITE, 0.55)
        return
    r = kf(u, [(0, 4), (0.25, 16), (0.55, 20), (1.0, 10)])
    a_ = kf(u, [(0, 1.0), (0.5, 0.85), (1.0, 0.0)])
    if a_ > 0.05:
        with c.part(Mat(ramp=['#6a1a08', '#c8420c', '#ff8a1c', '#ffd25a', '#ffffff'], emi=True, nooutline=True, bevel=4.0, dith=0.35), bevel=4.0) as p:
            p.ell(0, -12 - u * 4, r * (0.9 + 0.1 * math.sin(i * 2)), r * 0.85)
        with c.part(Mat(ramp=['#201814', '#3a2c24', '#5a4638'], bevel=3.0, dith=0.5, nooutline=True)) as p:
            p.ell(-6 + u * 4, -18 - u * 10, r * 0.55, r * 0.5)
            p.ell(8 - u * 3, -20 - u * 12, r * 0.45, r * 0.4)
        c.glow(0, -12, r + 3, FIREC, 0.3 * a_)
    for k in range(9):
        aa = k * 0.7 + 0.3
        rr = 6 + u * (20 + (k % 3) * 6)
        if u < 0.95:
            c.dotw(math.cos(aa) * rr, -12 + math.sin(aa) * rr * 0.8 + u * 8, ['#ffd25a', '#ff9a2a', '#ffffff', '#c8420c'][k % 4])
    if u > 0.45:
        c.dissolve(min(1.0, (u - 0.45) * 2.0), up=0.2, seed=3)


def draw_carbonero_hurt(c):
    P = car_pose('hurt', 0, 2)
    human(c, P, 'hurt', M_CAR, car_head, car_weapon, back_fn=car_back, front_cb=car_front, hip_h=10.0, legs=(5.0, 5.2), thick=(2.2, 2.0), arm_len=(4.6, 4.8))


def sheet_carbonero_forja():
    return enemy_sheet('en_carbonero_forja', (48, 48), (24, 46), (10, 24), draw_carbonero, (24, 14, 10),
                       STD(4, hit=[1, 2], box=[0, -24, 22, 24], idle=6, walk=8, ifps=9, wfps=14, fa=12, death=8, dfps=12))


# ================================================================== CENTINELA DE CRISTAL
def crystal(c, x, y, h, w, lean, matL, matR, hi=True):
    tip = (x + lean, y - h)
    with c.part(matL, line=0.4, bevel=1.6) as p:
        p.poly([(x - w, y), (x - w * 0.85, y - h * 0.72), tip, (x + w * 0.05, y - h * 0.04)])
    with c.part(matR, line=0.4, bevel=1.6) as p:
        p.poly([(x + w * 0.05, y - h * 0.04), tip, (x + w * 0.8 + lean * 0.3, y - h * 0.7), (x + w, y)])
    if hi:
        with c.part(ICE, bevel=0.5) as p:
            p.limb((x - w * 0.25, y - h * 0.15), (x + lean * 0.8 - w * 0.2, y - h * 0.85), 0.35)


def cen_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(bob=s, open=0.0, glow=0.0, shake=0.0, flash=0.0, burst=0.0, spin=t)
    if a == 'windup':
        w = sm((i + 1) / n)
        P.update(open=w, glow=w, shake=0.6 * w * (1 if i % 2 else -1))
    elif a == 'attack':
        P.update(open=[1.0, 1.1, 0.7, 0.3, 0.0][i], glow=[1.0, 1.0, 0.5, 0.2, 0.0][i], burst=[0.0, 1.0, 0.6, 0.0, 0.0][i])
    elif a == 'hurt':
        P.update(shake=2.0 if i == 0 else -1.0, flash=hurt_state(i)[2], glow=0.5)
    return P


def draw_centinela(c, a, i, n):
    if a == 'death':
        return death_centinela(c, i, n)
    P = cen_pose(a, i, n)
    centinela_body(c, P)
    if P['flash']:
        c.flash(WHITE, P['flash'])


def centinela_body(c, P, base_only=False):
    sh = P['shake']
    bob = 1.6 * P['bob']
    with c.at(sh, 0):
        # base de roca
        with c.part(ROCKB, line=0.6, bevel=2.6) as p:
            p.poly([(-12, 0), (-10.5, -6), (-6, -9), (0, -10), (7, -8.6), (11, -5), (12.5, 0)])
        with c.part(ROCKB, bevel=1.0) as p:
            p.poly([(-12, 0), (-10.5, -6), (-8, -7), (-9, 0)])
        with c.part(ICE_D, bevel=1.0) as p:
            p.poly([(-7, -9), (-3, -10.5), (2, -10), (0, -8)])          # escarcha sobre la roca
        if base_only:
            return
        # cristales traseros
        o = P['open']
        crystal(c, -7, -8, 20 + 3 * o, 3.4, -2.4 - 2 * o, ICE_D, ICE_D, hi=False)
        crystal(c, 6, -8, 17 + 3 * o, 3.0, 2.6 + 2.4 * o, ICE_D, ICE_D, hi=False)
        # nucleo flotante
        cy = -23 - bob - 2 * o
        # cristales laterales/delanteros
        crystal(c, -10, -4, 14 + 2 * o, 3.2, -4.2 - 3 * o, ICE_D, ICE, hi=True)
        crystal(c, 10, -4, 13 + 2 * o, 3.0, 4.4 + 3 * o, ICE_D, ICE, hi=True)
        crystal(c, -2.5, -8, 23 + 3 * o, 4.0, -1.0, ICE_D, ICE, hi=True)
        crystal(c, 3.5, -8, 19 + 3 * o, 3.4, 1.6, ICE_D, ICE, hi=True)
        # lente/ojo del nucleo (mira a la derecha)
        gl = P['glow']
        with c.part(CORE, bevel=2.4) as p:
            p.poly([(0 + 1.0, cy - 6.2 - gl), (4.8 + gl, cy), (1.0, cy + 6.2 + gl), (-3.6 - gl, cy)])
        with c.part(Mat(ramp=['#ffffff', '#ffffff'], emi=True, nooutline=True, bevel=0.5, dith=0.0)) as p:
            p.ell(1.6 + gl * 0.5, cy - 0.4, 1.2 + 0.8 * gl)
        c.glow(1, cy, 9 + 6 * gl, ICEC, 0.25 + 0.5 * gl)
        # anillo de esquirlas orbitando
        for k in range(4):
            aa = P['spin'] * 6.283 + k * 1.571
            ox, oy = math.cos(aa) * (8.5 + 2 * o), math.sin(aa) * 2.6
            with c.part(ICE, bevel=0.6) as p:
                p.poly([(ox - 0.9, cy + oy + 1.2), (ox, cy + oy - 2.0), (ox + 0.9, cy + oy + 1.2)])
        if P['burst'] > 0.3:
            for k in range(7):
                aa = -0.7 + k * 0.23
                rr = 8 + 5 * P['burst']
                c.dotw(1 + math.cos(aa) * rr + 4, cy + math.sin(aa) * rr, '#ffffff' if k % 2 else ICEC)


def death_centinela(c, i, n):
    if i == 0:
        centinela_body(c, cen_pose('hurt', 0, 2))
        c.flash(WHITE, 0.5)
        return
    u = i / (n - 1)
    centinela_body(c, dict(bob=0, open=0, glow=0, shake=0, flash=0, burst=0, spin=0), base_only=True)

    def shard(w, h, mat):
        def f(cc):
            with cc.part(mat, line=0.4, bevel=1.2) as p:
                p.poly([(-w, h * 0.5), (0, -h * 0.5), (w, h * 0.5)])
        return f
    items = []
    spec = [(-6, -14, 3.4, 12, -5, -9), (5, -16, 3.0, 11, 6, -10), (-1, -26, 3.8, 14, -1, -12), (-10, -8, 2.6, 8, -8, -6),
            (10, -8, 2.6, 8, 9, -7), (0, -20, 2.4, 7, 3, -8), (-4, -22, 2.2, 6, -4, -7)]
    for k, (sx, sy, w, h, vx, vy) in enumerate(spec):
        items.append(dict(fn=shard(w, h, ICE if k % 2 else ICE_D), x=sx, y=sy, r=3, vx=vx, vy=vy, spin=(k - 3) * 1.2, rest=1.2 * (k % 3 - 1), bounce=0.35))
    for d_ in items:
        d_['vx'] *= 0.6; d_['vy'] *= 0.7
    b = Bits(items, seed=17, T=0.75, g=1.6)
    draw_bits(c, b, u)
    if u < 0.5:
        c.glow(0, -22, 12 * (1 - u), ICEC, 0.5 * (1 - u))
    for k in range(8):
        if u < 0.9:
            aa = k * 0.8
            c.dotw(math.cos(aa) * (6 + u * 18), -16 + math.sin(aa) * (5 + u * 10), '#ffffff' if k % 2 else ICEC)
    if u > 0.6:
        c.dissolve(min(1.0, (u - 0.6) * 2.4), up=0.3, seed=1)


def sheet_centinela_cristal():
    return enemy_sheet('en_centinela_cristal', (48, 48), (24, 46), (13, 32), draw_centinela, (12, 20, 34),
                       STD(5, rel=1, idle=6, walk=6, ifps=6, wfps=6, fa=12, death=8, dfps=11))


SHEETS = [sheet_escudero_hueso, sheet_clerigo_osario, sheet_carbonero_forja, sheet_centinela_cristal]
