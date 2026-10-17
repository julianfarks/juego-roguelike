"""Enemigos nuevos (lote B): lobo de musgo, tirador de rayo, cultista de sangre, asesino del eclipse."""
from common import *
from humanoid import human
from en_catacumbas import enemy_sheet, STD, DARK, WHITE
from en_nuevos_a import hfeet, SKIN_G, GOLDT

# ------------------------------------------------------------------ materiales
FUR = Mat(ramp=['#0e1208', '#222a14', '#3c4a22', '#5e7236', '#8aa04e'], bevel=2.4, tex=0.55, seed=61, bias=0.45)
FUR_D = Mat(ramp=['#080a05', '#141a0c', '#242e14', '#3a4a22', '#566a34'], bevel=2.4, tex=0.55, seed=62)
MOSS = Mat(ramp=['#143a14', '#2a7022', '#58b038', '#98e060', '#d4ff9a'], bevel=1.6, tex=0.3, seed=63)
BONEW = Mat(ramp=['#2a2418', '#5a5038', '#948a60', '#cfc496', '#f4ecc8'], bevel=1.2, seed=64)
AMB = Mat(ramp=['#a84a08', '#ff9a1c', '#ffd25a', '#ffffff'], emi=True, nooutline=True, bevel=0.8, dith=0.1)
AMBC = '#FFB030'

STORM_C = Mat(ramp=['#0c1020', '#1a2644', '#2c4272', '#4a6aa4', '#86a8d8'], bevel=2.0, tex=0.3, seed=71)
STORM_D = Mat(ramp=['#080a16', '#101830', '#1c2a50', '#2e4478', '#4a68a0'], bevel=2.0, tex=0.3, seed=72)
COPPER = Mat(ramp=['#2a1210', '#5a2a1c', '#9a5230', '#d08a4c', '#f4c888'], bevel=1.4, tex=0.3, seed=73)
LEATH = Mat(ramp=['#120c0c', '#2a1c18', '#48322a', '#6e4e3a', '#94705a'], bevel=1.8, tex=0.35, seed=74)
ELECM = Mat(ramp=['#2a68c8', '#4fa8ff', '#a8e0ff', '#ffffff'], emi=True, nooutline=True, bevel=1.0, dith=0.1)
ELEC = '#4FA8FF'
SKIN_T = Mat(ramp=['#241a1c', '#4e3a3a', '#7e6460', '#b09484', '#dcc4ac'], bevel=1.4, seed=75)

BLOODR = Mat(ramp=['#14040a', '#3c0a16', '#7a1424', '#b82840', '#f0586c'], bevel=2.0, tex=0.3, seed=81)
BLOODR_D = Mat(ramp=['#0c0206', '#240610', '#4a0e1a', '#721a2a', '#98303e'], bevel=2.0, tex=0.3, seed=82)
BLK = Mat(ramp=['#08060a', '#14101a', '#241c2c', '#382c42', '#52425e'], bevel=1.6, tex=0.25, seed=83)
BLK_D = Mat(ramp=['#040306', '#0c0a10', '#18121e', '#281e32'], bevel=1.6, seed=84)
PALE = Mat(ramp=['#2a1a2a', '#54384a', '#8c6070', '#c0958e', '#ecc8b4'], bevel=1.6, seed=85)
BLOODG = Mat(ramp=['#6a0a1c', '#b8142c', '#ff3c52', '#ff9aa8', '#ffffff'], emi=True, nooutline=True, bevel=2.6, dith=0.25)
STEEL = Mat(ramp=['#1a1220', '#38304a', '#5e5878', '#8c88a8', '#c4c0dc'], bevel=1.2, tex=0.2, seed=86)
RED = '#D0203A'

ECL_W = Mat(ramp=['#2a2418', '#5a5038', '#948a60', '#cfc496', '#f4ecc8'], bevel=1.8, tex=0.25, seed=91)
ECL_WD = Mat(ramp=['#1a160e', '#3c3424', '#665c40', '#948a64', '#bcb088'], bevel=1.8, tex=0.25, seed=92)
ECL_B = Mat(ramp=['#06060a', '#10101a', '#1c1c2c', '#2c2c42', '#444464'], bevel=1.8, tex=0.25, seed=93)
ECL_BD = Mat(ramp=['#030306', '#08080e', '#12121c', '#1c1c2c'], bevel=1.8, seed=94)
ECL_G = Mat(ramp=['#7a5a10', '#c89820', '#ffd25a', '#fff0b0', '#ffffff'], emi=True, nooutline=True, bevel=1.2, dith=0.15)
ECLC = '#FFD25A'
BLADE = Mat(ramp=['#6a6a82', '#a0a0bc', '#d4d4ec', '#ffffff'], bevel=0.8, dith=0.0)
TRAIL_G = Mat(ramp=['#a8801c', '#ffd25a', '#fff0b0', '#ffffff'], emi=True, nooutline=True, bevel=1.5, dith=0.2)


def gen_death(c, i, n, draw_fn, pose_fn, bits=(), soul=None, glowc=None):
    """Caida generica de un humanoide: golpe, giro hacia atras, piezas sueltas y disolucion."""
    if i == 0:
        draw_fn(c, pose_fn('hurt', 0, 2))
        c.flash(WHITE, 0.45)
        return
    u = i / (n - 1)
    P = pose_fn('hurt', 1, 2)
    ang = kf(u, [(0, 0), (0.35, -0.35), (0.7, -1.2), (1.0, -1.57)])
    P['feet'] = (kf(u, [(0, -3), (1, -6)]), 0), (kf(u, [(0, 3), (1, 5)]), 0)
    with c.at(2 + 3 * u, 0, ang):
        draw_fn(c, P, plain=True)
    if bits:
        items = [dict(b) for b in bits]
        for d_ in items:
            d_['vx'] *= 0.55; d_['vy'] *= 0.65
        draw_bits(c, Bits(items, seed=13, T=0.8, g=1.5), u)
    if u > 0.5:
        c.dissolve(min(1.0, (u - 0.5) * 1.8), up=0.3, seed=4)
    if soul:
        for k in range(6):
            if u < 0.95:
                c.dotw(-7 + k * 2.8 + math.sin(k * 2.7 + i) * 2, -16 - u * (16 + k * 3) - 2 * k, soul if (k + i) % 2 == 0 else '#ffffff')


# ================================================================== LOBO DE MUSGO
def lobo_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(dy=0.5 * s, ph=t, walk=False, stride=0, lift=0, head=0.0, jaw=0.0, tail=0.3 + 0.1 * s, crouch=0.0, stretch=0.0, eye=0.4, flash=0.0, rot=0.0, fx=0.0, back=0.0)
    if a == 'walk':
        P.update(walk=True, stride=6.4, lift=4.0, dy=-1.2 * abs(math.sin(4 * math.pi * t)) + 0.4, head=0.12, tail=0.5, eye=0.7)
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(crouch=w, head=lerp(0, 0.2, w), jaw=2.0 * w, eye=1.0, tail=lerp(0.3, 0.9, w), dy=lerp(0, 3.4, w), fx=w)
    elif a == 'attack':
        P.update(stretch=[1.0, 1.0, 0.6, 0.2, 0.0][i], head=[0.1, 0.15, 0.1, 0.0, 0.0][i], jaw=[4.0, 4.5, 3.0, 1.0, 0.0][i], eye=1.0, tail=[1.0, 0.9, 0.7, 0.4, 0.3][i],
                 dy=[-4, -6, -2, 1, 0][i], rot=[-0.25, -0.18, 0.12, 0.05, 0][i], crouch=[0.0, 0, 0, 0.3, 0.2][i])
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(flash=fl, head=-0.3 if i == 0 else -0.1, jaw=3.0, dy=0.5, back=rx, tail=0.9, eye=0.9)
    return P


def lobo_body(c, P, a='idle', i=0, n=1):
    dy, ph = P['dy'], P['ph']
    cr, st = P['crouch'], P['stretch']
    bx = P['back']
    hipx, shx = -8.0 - 2 * st + bx, 6.5 + 2.5 * st + bx
    hy = -9.5 + dy + 2.0 * cr
    sy = -10.0 + dy + 3.2 * cr - 1.0 * st
    rot = P['rot']
    if P['walk']:
        g = [gait((ph + k) % 1, P['stride'], P['lift']) for k in (0.0, 0.5, 0.25, 0.75)]
    elif st > 0:
        g = [(-9 - 3 * st, -3 * st), (-7, -2 * st), (7 + 4 * st, -2 * st), (10 + 5 * st, -4 * st)]
    elif cr > 0:
        g = [(-9, 0), (-6, 0), (5, 0), (8, 0)]
    else:
        g = [(-8, 0), (-5.5, 0), (5, 0), (8, 0)]
    with c.at(0, 0, rot):
        # patas lejanas (mas oscuras)
        hf, ff = (hipx + 1 + g[1][0] + 2.5, g[1][1]), (shx - 1 + g[3][0] - 1.5, g[3][1])
        leg(c, (hipx + 1, hy), hf, 5.2, 5.6, 1.8, 1.0, FUR_D, bend=-1, footlen=2.6)
        leg(c, (shx - 1, sy), ff, 5.0, 5.2, 1.7, 0.95, FUR_D, bend=1, footlen=2.6)
        # cola
        tl = P['tail']
        tb = (hipx - 3, hy - 3)
        with c.part(FUR, line=0.5, bevel=1.8) as p:
            p.tube([tb, (tb[0] - 5, tb[1] - 2 - 4 * tl), (tb[0] - 9, tb[1] + 1 - 7 * tl)], 1.9, 0.6)
        # cuerpo
        with c.part(FUR, line=0.6, bevel=3.0) as p:
            p.poly([(hipx - 4, hy - 4), (hipx - 3, hy + 2.5), (0, hy + 3.4), (shx + 1.5, sy + 3.2), (shx + 4, sy), (shx + 3.4, sy - 5.4),
                    (shx - 2, sy - 7.6), (0, hy - 7.6 - 0.5 * cr), (hipx + 1, hy - 7.2)])
        with c.part(FUR_D, bevel=1.4) as p:
            p.poly([(hipx - 4, hy - 4), (hipx - 3, hy + 2.5), (0, hy + 3.4), (0, hy + 0.4), (hipx, hy - 2)])
        with c.part(BONEW, line=0.3, bevel=0.8) as p:             # costillas visibles
            for k in range(3):
                p.limb((-2 + k * 2.5, hy - 1.5 + k * 0.4), (-1 + k * 2.5, hy + 2.4 + k * 0.4), 0.4)
        # musgo en el lomo
        with c.part(MOSS, bevel=1.2) as p:
            p.poly([(hipx - 1, hy - 7.6), (-2, hy - 9.6), (2, hy - 8.4), (5.4, sy - 8.6), (shx - 1, sy - 7.9), (2, hy - 7.6)])
            p.ell(-5, hy - 8.4, 1.8, 1.0); p.ell(1.5, hy - 9.4, 1.5, 0.9)
        # pata trasera y delantera cercanas
        hf2, ff2 = (hipx - 1 + g[0][0], g[0][1]), (shx + g[2][0], g[2][1])
        leg(c, (hipx - 1.5, hy + 0.5), hf2, 5.4, 5.8, 2.4, 1.1, FUR, bend=-1, footlen=3.0)
        leg(c, (shx + 0.5, sy + 0.5), ff2, 5.2, 5.4, 2.0, 1.0, FUR, bend=1, footlen=3.0)
        # cabeza
        hxn, hyn = shx + 3.5, sy - 5.2 + 1.0 * cr
        with c.at(hxn, hyn, P['head'] + 0.15 * cr):
            jw = P['jaw']
            with c.part(FUR_D, line=0.5, bevel=1.4) as p:          # mandibula inferior
                p.poly([(-1.6, 1.6), (6.0, 1.9 + jw * 0.7), (6.4, 3.2 + jw), (0, 3.6 + jw * 0.6)])
            with c.part(FUR, line=0.6, bevel=2.2) as p:
                p.poly([(-4.4, -3), (-1.2, -4.6), (3.0, -3.2), (7.4, -0.4), (7.8, 1.2), (3.0, 2.0), (-1, 3.4), (-4.4, 2)])
            with c.part(FUR_D, line=0.4, bevel=1.4) as p:          # orejas
                p.poly([(-3.4, -3.6), (-4.6, -8.0), (-1.2, -4.8)])
                p.poly([(-1.0, -4.4), (0.4, -8.6), (1.6, -3.8)])
            with c.part(MOSS, bevel=0.8) as p:
                p.ell(-2.2, -3.6, 1.7, 0.9)
            with c.part(DARK) as p:
                p.ell(7.5, 0.4, 0.8, 0.7)                           # nariz
            with c.part(AMB) as p:
                p.ell(2.8, -1.2, 0.95 + 0.2 * P['eye'], 0.8)
            c.glow(2.8, -1.2, 3.0, AMBC, 0.25 + 0.5 * P['eye'])
            if jw > 1.0:
                with c.part(BONEW) as p:
                    for k in range(3):
                        p.poly([(2.0 + k * 1.7, 1.8 + jw * 0.4), (2.6 + k * 1.7, 1.8 + jw * 0.4), (2.3 + k * 1.7, 3.2 + jw * 0.4)])
                        p.poly([(2.2 + k * 1.7, 2.0 + jw * 0.5 + 1.3), (2.8 + k * 1.7, 2.0 + jw * 0.5 + 1.3), (2.5 + k * 1.7, 0.7 + jw * 0.5 + 1.3)])
    if P['fx'] > 0.5:
        c.glow(shx + 6, sy - 6, 5, AMBC, 0.25)
    if a == 'attack' and i in (0, 1):
        for k in range(5):
            c.dotw(-18 - k * 3, -9 + (k % 3) * 2 - 6, '#d4ff9a' if k % 2 else '#58b038')


def draw_lobo(c, a, i, n):
    if a == 'death':
        return death_lobo(c, i, n)
    P = lobo_pose(a, i, n)
    lobo_body(c, P, a, i, n)
    if P['flash']:
        c.flash(WHITE, P['flash'])
    if a == 'windup' and i == n - 1:
        c.flash(AMBC, 0.08)


def death_lobo(c, i, n):
    if i == 0:
        lobo_body(c, lobo_pose('hurt', 0, 2))
        c.flash(WHITE, 0.45)
        return
    u = i / (n - 1)
    P = lobo_pose('hurt', 1, 2)
    P['jaw'] = 3
    P['eye'] = 1 - u
    ang = kf(u, [(0, 0), (0.4, -0.5), (0.8, -1.3), (1.0, -1.57)])
    with c.at(-2 + 4 * u, 0, ang):
        lobo_body(c, P)
    if u > 0.45:
        w = min(1, (u - 0.45) / 0.4)
        for k in range(6):
            if u < 0.95:
                c.dotw(-10 + k * 4 + (u - 0.4) * (k - 3) * 4, -3 - (k % 3) * 2 - (u - 0.4) * 6, '#98e060' if k % 2 else '#58b038')
    if u > 0.55:
        c.dissolve(min(1.0, (u - 0.55) * 2.2), up=0.3, seed=7)


def sheet_lobo_musgo():
    return enemy_sheet('en_lobo_musgo', (48, 48), (24, 46), (20, 17), draw_lobo, (14, 22, 10),
                       STD(5, hit=[1, 2], box=[2, -20, 22, 18], idle=6, walk=8, ifps=7, wfps=14, fa=12, death=8))


# ================================================================== TIRADOR DE RAYO
def tir_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(hx=-4.0, dy=0.5 * s, lean=0.04, ph=t, walk=False, stride=0, lift=0, rear=(2, -12), front=(8, -13), head=0.0, aim=0.5, flash=0.0, glow=0.0, recoil=0.0, lock=0.0)
    if a == 'idle':
        P['rear'] = (1.5, -12 + 0.4 * s); P['front'] = (8, -12 + 0.4 * s); P['aim'] = 0.6
    elif a == 'walk':
        P.update(walk=True, stride=4.4, lift=2.6, dy=-0.8 * abs(math.sin(2 * math.pi * t)) + 0.4, lean=0.12, hx=-3, aim=0.55)
        P['rear'] = (1.5, -12 + 0.6 * s); P['front'] = (8, -12 + 0.6 * s)
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(lean=lerp(0.04, -0.06, w), hx=lerp(-4, -5, w), dy=lerp(0, 1.2, w), aim=lerp(0.55, -0.02, w), glow=w, lock=w, head=-0.05 * w)
        P['rear'] = (lerp(1.5, 3.5, w), lerp(-12, -19.5, w)); P['front'] = (lerp(8, 12, w), lerp(-12, -20.2, w))
        P['feet'] = hfeet(w)
    elif a == 'attack':
        P.update(lean=[-0.06, -0.2, -0.1, 0.0, 0.04][i], hx=[-5, -7.5, -6.5, -5, -4][i], dy=[1.2, 0.6, 1.0, 0.6, 0.4][i], aim=[-0.02, -0.2, -0.05, 0.1, 0.3][i],
                 glow=[1.0, 1.0, 0.4, 0.0, 0.0][i], recoil=[0, 1.0, 0.5, 0.2, 0][i], lock=1.0 if i < 2 else 0.0)
        P['rear'] = [(3.5, -19.5), (1.5, -20.5), (2.0, -19.6), (2.0, -17), (1.5, -14)][i]
        P['front'] = [(12, -20.2), (10.5, -21), (11, -20.2), (10, -17), (8, -14)][i]
        P['feet'] = (-6.5, 0), (5, 0)
        P['head'] = [-0.05, -0.2, -0.1, 0.0, 0.0][i]
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(hx=-4 + rx, lean=ln, flash=fl, head=-0.3 if i == 0 else -0.1, aim=0.9)
        P['front'] = (3, -9) if i == 0 else (6, -11); P['rear'] = (-1.5, -10) if i == 0 else (0.5, -11)
    return P


M_TIR = dict(skin=SKIN_T, cloth=STORM_C, cloth_d=STORM_D, boot=LEATH, boot_d=STORM_D, vest=LEATH, vest_d=STORM_D)


def tir_head(c, x, y, ang, P):
    with c.at(x, y, ang):
        with c.part(SKIN_T, line=0.5, bevel=1.8) as p:
            p.ell(0.4, 0.4, 3.8, 4.0)
        with c.part(STORM_D, bevel=1.4) as p:                   # mascara
            p.poly([(-3, 0.6), (4.2, 0.4), (4.4, 4.2), (-0.6, 5.0), (-3.4, 3.4)])
        with c.part(Mat(ramp=['#0a0e1c', '#16203a', '#2a3c68'], bevel=1.2, seed=5), line=0.4, bevel=1.4) as p:       # visor
            p.limb((-2.6, -1.2), (4.4, -1.4), 1.5)
        with c.part(ELECM, bevel=0.8) as p:
            p.limb((1.0, -1.3), (4.2, -1.4), 0.8)
        c.glow(3.2, -1.4, 3.0 + 3 * P['lock'], ELEC, 0.3 + 0.5 * P['lock'])
        with c.part(STORM_C, line=0.5, bevel=2.2) as p:         # capucha alta
            p.poly([(-5.8, 4.4), (-6.8, -2), (-4, -6.6), (0.6, -8), (4.4, -5.4), (3.4, -3), (0.8, -2.8), (-1.6, -1.2), (-3.2, 2.0), (-3.4, 5.4)])
        with c.part(COPPER, bevel=0.6) as p:
            p.ell(-2.4, -5.8, 1.0)


def tir_back(c, hip, neck, sho, lean, ph):
    sw = math.sin(ph * 6.283)
    with c.part(STORM_D, line=0.5, bevel=2.2) as p:             # capa con jirones
        p.poly([(neck[0] - 3.5, neck[1] - 1), (neck[0] + 1.5, neck[1] - 1), (hip[0], hip[1] + 6), (hip[0] - 7 - lean * 4 + sw, hip[1] + 10), (hip[0] - 11, hip[1] + 7 + sw * 0.6), (neck[0] - 9, neck[1] + 3)])
    with c.part(COPPER, bevel=0.8) as p:                         # bobina de rayo a la espalda
        p.ell(neck[0] - 2.6, neck[1] + 2.0, 2.0, 2.6)
    with c.part(ELECM) as p:
        p.ell(neck[0] - 2.6, neck[1] + 2.0, 0.8, 1.2)


def tir_weapon(c, P, rear, front):
    """Fusil de riel largo con bobinas; la mano delantera sostiene el cañon."""
    dx, dy = front[0] - rear[0], front[1] - rear[1]
    L = math.hypot(dx, dy) or 1
    d = (dx / L, dy / L); nr = (-d[1], d[0])
    rc = P['recoil']
    base = (rear[0] - d[0] * 5 - d[0] * rc * 1.5, rear[1] - d[1] * 5)
    tip = (front[0] + d[0] * 11 - d[0] * rc, front[1] + d[1] * 11)
    with c.part(LEATH, line=0.4, bevel=1.4) as p:               # culata
        p.poly([(base[0] + nr[0] * 1.8, base[1] + nr[1] * 1.8), (rear[0] + nr[0] * 1.0, rear[1] + nr[1] * 1.0), (rear[0] - nr[0] * 1.0, rear[1] - nr[1] * 1.0),
                (base[0] - nr[0] * 2.8, base[1] - nr[1] * 2.8)])
    with c.part(STEEL, line=0.4, bevel=1.0) as p:                # cañon
        p.limb((rear[0], rear[1]), tip, 1.0)
    for k in range(3):                                           # bobinas de cobre
        q = 0.35 + k * 0.22
        pp = (rear[0] + (tip[0] - rear[0]) * q, rear[1] + (tip[1] - rear[1]) * q)
        with c.part(COPPER, bevel=0.8) as p:
            p.limb((pp[0] + nr[0] * 1.9, pp[1] + nr[1] * 1.9), (pp[0] - nr[0] * 1.9, pp[1] - nr[1] * 1.9), 0.65)
    c.glow(tip[0] - d[0] * 3, tip[1] - d[1] * 3, 3.4 + 2 * P['glow'], ELEC, 0.25 + 0.55 * P['glow'])
    with c.part(ELECM) as p:
        p.ell(tip[0], tip[1], 0.9 + 0.6 * P['glow'])
    if P['recoil'] > 0.9:
        for q in range(6):
            c.dotw(tip[0] + d[0] * (3 + q * 2.4), tip[1] + d[1] * (3 + q * 2.4) + (q % 2) - 0.5, '#ffffff' if q % 2 else ELEC)
    if P['lock'] > 0.7:
        for q in range(5):
            c.dotw(tip[0] + d[0] * (4 + q * 4), tip[1] + d[1] * (4 + q * 4), '#ff4040' if P['lock'] > 0.95 else '#6ab8ff')


def tir_draw(c, P, plain=False):
    human(c, P, 'idle', M_TIR, tir_head, tir_weapon, back_fn=tir_back)


def draw_tirador(c, a, i, n):
    if a == 'death':
        return death_tirador(c, i, n)
    P = tir_pose(a, i, n)
    human(c, P, a, M_TIR, tir_head, tir_weapon, back_fn=tir_back)
    if P['flash']:
        c.flash(WHITE, P['flash'])
    if a == 'attack' and i == 1:
        c.flash(ELEC, 0.12)


def _p_rifle(c):
    with c.part(STEEL, line=0.4, bevel=1.0) as p:
        p.limb((-9, 0), (9, 0), 1.0)
    with c.part(COPPER, bevel=0.8) as p:
        for k in range(3):
            p.limb((-3 + k * 3, -1.8), (-3 + k * 3, 1.8), 0.65)


def death_tirador(c, i, n):
    gen_death(c, i, n, lambda cc, P, plain=False: human(cc, P, 'idle', M_TIR, tir_head, (lambda c2, PP, r, f: None) if plain else tir_weapon, back_fn=tir_back),
              lambda a, k, m: tir_pose(a, k, m),
              bits=[dict(fn=_p_rifle, x=9, y=-20, r=2, vx=7, vy=-6, spin=6, rest=0.15, bounce=0.35)], soul=ELEC)


def sheet_tirador_rayo():
    return enemy_sheet('en_tirador_rayo', (48, 48), (24, 46), (12, 30), draw_tirador, (14, 16, 30),
                       STD(5, rel=1, muz=[20, -20], idle=6, walk=8, ifps=7, wfps=10, fa=13, death=8))


# ================================================================== CULTISTA DE SANGRE
def cul_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(hx=-3.5, dy=0.6 * s, lean=0.14, ph=t, walk=False, stride=0, lift=0, rear=(4, -10), front=(0, -9), head=0.1, flash=0.0, glow=0.0, chant=0.0, sway=s)
    if a == 'idle':
        P['rear'] = (4.5, -10 + 0.5 * s); P['front'] = (0.5, -9 + 0.4 * s)
    elif a == 'walk':
        P.update(walk=True, stride=3.4, lift=1.8, dy=-0.7 * abs(math.sin(2 * math.pi * t)) + 0.3, lean=0.2, hx=-2.5)
        P['rear'] = (4.5, -10 + 0.7 * s); P['front'] = (0.5, -9 + 0.7 * s)
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(lean=lerp(0.14, -0.12, w), hx=lerp(-3.5, -4, w), dy=lerp(0, 1.0, w), glow=w, chant=w, head=lerp(0.1, -0.25, w))
        P['rear'] = (lerp(4.5, 7, w), lerp(-10, -25, w)); P['front'] = (lerp(0.5, 1, w), lerp(-9, -25.5, w))
        P['feet'] = hfeet(w * 0.6)
    elif a == 'attack':
        P.update(lean=[-0.12, -0.2, 0.1, 0.1, 0.1][i], hx=[-4, -4.5, -3, -3, -3][i], dy=[1.0, 0.4, 0.8, 0.5, 0.3][i], glow=[1.0, 1.0, 1.0, 0.5, 0.0][i],
                 chant=[1.0, 1.0, 0.8, 0.4, 0.0][i], head=[-0.25, -0.3, 0.0, 0.1, 0.1][i])
        P['rear'] = [(7, -25), (10, -24), (12, -17), (9, -13), (5, -10)][i]
        P['front'] = [(1, -25.5), (-2, -24), (-5, -17), (-2, -13), (0.5, -9)][i]
        P['feet'] = (-5, 0), (4, 0)
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(hx=-3.5 + rx, lean=ln, flash=fl, head=-0.3 if i == 0 else -0.1)
        P['rear'] = (1, -9) if i == 0 else (3.5, -10); P['front'] = (-3, -8)
    return P


M_CUL = dict(skin=PALE, cloth=BLOODR, cloth_d=BLOODR_D, boot=BLK_D, boot_d=BLK_D, vest=BLOODR, vest_d=BLOODR_D)


def cul_head(c, x, y, ang, P):
    with c.at(x, y, ang):
        with c.part(PALE, line=0.5, bevel=1.8) as p:
            p.ell(0.6, 0.6, 3.5, 3.6)
        with c.part(BLK, bevel=1.2) as p:                        # mascara con cuernos
            p.poly([(-2.6, -1.2), (4.0, -1.4), (4.2, 3.4), (1.0, 4.8), (-2.2, 3.0)])
        with c.part(BLOODG) as p:
            p.rect(0.2, -0.4, 3.8, 0.4)
            p.rect(1.0, 2.0, 3.0, 2.6)                           # boca-hendidura
        c.glow(2.2, 0.0, 3.0, RED, 0.3 + 0.5 * P['glow'])
        with c.part(BLOODR_D, line=0.5, bevel=2.2) as p:         # capucha
            p.poly([(-5.4, 5.4), (-6.4, -1), (-4.2, -5.6), (0.6, -7), (4.2, -4.8), (3.4, -2.6), (0.8, -2.4), (-1.4, -1.0), (-3, 2), (-3.2, 6)])
        with c.part(STEEL, bevel=0.8) as p:
            p.poly([(-1.5, -6.4), (-3, -11.5), (0, -7)])           # cuernos
            p.poly([(1.6, -6.6), (3.2, -11.0), (3.4, -6.0)])


def cul_back(c, hip, neck, sho, lean, ph):
    sw = math.sin(ph * 6.283)
    with c.part(BLOODR_D, line=0.5, bevel=2.2) as p:
        p.poly([(neck[0] - 3.5, neck[1] - 1), (neck[0] + 1.5, neck[1] - 1), (hip[0] + 1, hip[1] + 8), (hip[0] - 7 - lean * 4 + sw * 0.8, hip[1] + 13), (neck[0] - 9, neck[1] + 4)])


def cul_torso(c, P):
    with c.part(BLOODR, line=0.5, bevel=2.2) as p:
        p.poly([(-5, -1), (5, -1.4), (6.4, 6), (5.4, 10), (2, 8.6), (-1, 10.4), (-4, 8.8), (-6.4, 10), (-6.2, 5)])
    with c.part(BLK, bevel=0.8) as p:
        p.poly([(-5.4, -2.4), (5.2, -3), (5.4, 0), (-5.6, 0.6)])      # cinturon
        p.limb((-0.4, -11), (-0.4, 8), 0.9)
    with c.part(BLOODG, bevel=0.8) as p:
        p.ell(0.4, -6.4, 1.4, 1.6)                                  # simbolo de sangre
    with c.part(BLK, bevel=0.6) as p:
        p.ell(0.4, -6.4, 0.6, 0.8)


def cul_front(c, P, rear, front):
    """Caliz flotante entre las manos cuando entona el cantico."""
    ch = P['chant']
    if ch <= 0:
        with c.part(STEEL, line=0.4, bevel=0.8) as p:                 # daga ritual en la mano
            p.limb((rear[0], rear[1] - 1), (rear[0] + 5.5, rear[1] - 6), 0.7)
        return
    cx_, cy_ = (rear[0] + front[0]) / 2, min(rear[1], front[1]) - 5
    with c.part(BLOODG, bevel=2.4) as p:
        p.ell(cx_, cy_, 2.8 + 1.6 * ch, 2.8 + 1.6 * ch)
    with c.part(BLK, bevel=0.8) as p:
        p.poly([(cx_ - 4.6, cy_ - 1.0), (cx_ + 4.6, cy_ - 1.0), (cx_ + 3, cy_ + 2.4), (cx_ - 3, cy_ + 2.4)])
        p.limb((cx_, cy_ + 2.4), (cx_, cy_ + 5), 0.6)
    c.glow(cx_, cy_, 8 + 6 * ch, RED, 0.35 + 0.5 * ch)
    for k in range(6):
        aa = P['ph'] * 6.283 * 2 + k * 1.047
        c.dotw(cx_ + math.cos(aa) * (7 + 3 * ch), cy_ + math.sin(aa) * 3 - 2, '#ff9aa8' if k % 2 else RED)


def cul_weapon(c, P, rear, front):
    pass


def draw_cultista(c, a, i, n):
    if a == 'death':
        return death_cultista(c, i, n)
    P = cul_pose(a, i, n)
    human(c, P, a, M_CUL, cul_head, cul_weapon, back_fn=cul_back, torso_extra=cul_torso, front_cb=cul_front)
    if P['flash']:
        c.flash(WHITE, P['flash'])
    if a == 'windup' and i == n - 1:
        c.flash(RED, 0.08)


def _p_cup(c):
    with c.part(BLOODG, bevel=2.0) as p:
        p.ell(0, -1, 3, 3)
    with c.part(BLK, bevel=0.8) as p:
        p.poly([(-3.6, -1), (3.6, -1), (2.4, 2.4), (-2.4, 2.4)])


def death_cultista(c, i, n):
    gen_death(c, i, n, lambda cc, P, plain=False: human(cc, P, 'idle', M_CUL, cul_head, cul_weapon, back_fn=cul_back, torso_extra=cul_torso),
              lambda a, k, m: cul_pose(a, k, m),
              bits=[dict(fn=_p_cup, x=2, y=-26, r=3, vx=4, vy=-7, spin=4, rest=0.4, bounce=0.4)], soul=RED)


def sheet_cultista_sangre():
    return enemy_sheet('en_cultista_sangre', (48, 48), (24, 46), (12, 30), draw_cultista, (24, 10, 16),
                       STD(5, rel=2, idle=6, walk=8, ifps=7, wfps=9, fa=12, death=8))


# ================================================================== ASESINO DEL ECLIPSE
def ase_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(hx=-3.5, dy=0.5 * s, lean=0.16, ph=t, walk=False, stride=0, lift=0, rear=(4, -11), front=(1, -10), head=0.05, flash=0.0, glow=0.0, trail=None, ka=-0.4, kb=-0.9)
    if a == 'idle':
        P['rear'] = (4, -11 + 0.4 * s); P['front'] = (0.5, -10 + 0.4 * s)
    elif a == 'walk':
        P.update(walk=True, stride=5.6, lift=3.2, dy=-1.1 * abs(math.sin(2 * math.pi * t)) + 0.5, lean=0.28, hx=-2)
        P['rear'] = (4 + s * 1.5, -11 + 0.8 * s); P['front'] = (1 - s * 1.5, -10 - 0.8 * s)
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(lean=lerp(0.16, 0.5, w), hx=lerp(-3.5, -2, w), dy=lerp(0, 3.4, w), glow=w, ka=lerp(-0.4, -1.9, w), kb=lerp(-0.9, -2.5, w), head=lerp(0.05, 0.3, w))
        P['rear'] = (lerp(4, 0, w), lerp(-11, -13, w)); P['front'] = (lerp(1, 5, w), lerp(-10, -14, w))
        P['feet'] = (lerp(-3.5, -7, w), 0), (lerp(3.5, 6, w), 0)
    elif a == 'attack':
        P.update(lean=[0.5, 0.1, 0.45, 0.35, 0.15][i], hx=[-2, 3, 5, 4, 0][i], dy=[3.4, 1.2, 2.4, 1.6, 0.6][i], glow=1.0, ka=[-1.9, 0.1, 0.9, 0.6, -0.3][i],
                 kb=[-2.5, -0.2, 0.2, 0.7, -0.8][i], head=[0.3, 0.2, 0.3, 0.2, 0.0][i])
        P['rear'] = [(0, -13), (10, -12), (14, -9), (12, -9), (7, -10)][i]
        P['front'] = [(5, -14), (8, -15), (13, -11), (11, -11), (4, -10)][i]
        P['feet'] = (-7, 0), ([6, 8, 9, 9, 7][i], 0)
        P['trail'] = [None, 0.3, 0.7, None, None][i]
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(hx=-3.5 + rx, lean=ln, flash=fl, head=-0.3 if i == 0 else -0.1)
        P['rear'] = (1, -10) if i == 0 else (3.5, -11); P['front'] = (-2, -9)
    return P


M_ASE = dict(skin=PALE, cloth=ECL_B, cloth_d=ECL_BD, boot=ECL_BD, boot_d=ECL_BD, vest=ECL_W, vest_d=ECL_WD)


def ase_head(c, x, y, ang, P):
    with c.at(x, y, ang):
        with c.part(ECL_BD, line=0.5, bevel=1.8) as p:
            p.ell(0.4, 0.4, 3.7, 3.9)
        with c.part(ECL_W, bevel=1.4) as p:                       # mascara: media luna clara
            p.poly([(-2.4, -2.6), (4.0, -2.2), (4.2, 2.4), (1.6, 4.4), (-2.6, 2.2)])
        with c.part(ECL_G) as p:
            p.limb((0.6, -0.4), (3.8, -0.8), 0.7)                  # ranura de luz
        c.glow(2.4, -0.6, 3.0, ECLC, 0.3 + 0.5 * P['glow'])
        with c.part(ECL_B, line=0.5, bevel=2.0) as p:              # capucha negra con pañuelo
            p.poly([(-5.6, 5), (-6.0, -1.4), (-3.4, -5.4), (1.4, -5.8), (3.4, -3.8), (0.6, -3.0), (-1.4, -1.6), (-3.0, 1.6), (-3.4, 5.4)])
        with c.part(ECL_W, bevel=0.8) as p:
            p.tube([(-5, -1), (-10.4, 0.5 + P['ph'] * 0), (-14, 3 + math.sin(P['ph'] * 6.28) * 1.2)], 1.3, 0.5)   # bufanda al viento


def ase_back(c, hip, neck, sho, lean, ph):
    sw = math.sin(ph * 6.283)
    with c.part(ECL_BD, line=0.5, bevel=2.0) as p:
        p.poly([(neck[0] - 3, neck[1] - 1), (neck[0] + 1.5, neck[1] - 1), (hip[0], hip[1] + 4), (hip[0] - 8 - lean * 5 + sw, hip[1] + 7), (neck[0] - 7, neck[1] + 3)])


def ase_torso(c, P):
    with c.part(ECL_G, bevel=0.6) as p:
        p.poly([(-4.4, -9.6), (4.4, -11.4), (4.8, -10), (-4.6, -8.2)])      # faja dorada
    with c.part(ECL_W, line=0.4, bevel=1.2) as p:
        p.ell(1.6, -11.6, 3.4, 2.0)                                          # hombrera


def ase_weapon(c, P, rear, front):
    """Dos dagas curvas: una por mano."""
    for hand, ang in ((front, P['kb']), (rear, P['ka'])):
        d = (math.cos(ang), math.sin(ang)); nr = (-d[1], d[0])
        tip = (hand[0] + d[0] * 11, hand[1] + d[1] * 11)
        with c.part(BLADE, line=0.4, bevel=0.9) as p:
            p.poly([(hand[0] + d[0] * 1.5 + nr[0] * 1.3, hand[1] + d[1] * 1.5 + nr[1] * 1.3),
                    (hand[0] + d[0] * 7 + nr[0] * 2.4, hand[1] + d[1] * 7 + nr[1] * 2.4), (tip[0] + nr[0] * 0.6, tip[1] + nr[1] * 0.6),
                    (hand[0] + d[0] * 6 - nr[0] * 0.6, hand[1] + d[1] * 6 - nr[1] * 0.6)])
        with c.part(ECL_G, bevel=0.6) as p:
            p.limb((hand[0] + nr[0] * 1.8, hand[1] + nr[1] * 1.8), (hand[0] - nr[0] * 1.8, hand[1] - nr[1] * 1.8), 0.5)
        c.glow(tip[0], tip[1], 3.0, ECLC, 0.15 + 0.5 * P['glow'])


def draw_asesino(c, a, i, n):
    if a == 'death':
        return death_asesino(c, i, n)
    P = ase_pose(a, i, n)
    human(c, P, a, M_ASE, ase_head, ase_weapon, back_fn=ase_back, torso_extra=ase_torso, legs=(6.8, 6.8), thick=(1.8, 1.6))
    if P['trail'] is not None:
        sh = (P['hx'] + 2, -22 + P['dy'])
        arc_trail(c, sh[0], sh[1], 8, 20, -1.2 if P['trail'] < 0.5 else -0.6, 0.9, TRAIL_G)
    if P['flash']:
        c.flash(WHITE, P['flash'])
    if a == 'windup' and i == n - 1:
        c.flash(ECLC, 0.1)


def _p_dagger(c):
    with c.part(BLADE, line=0.4, bevel=0.9) as p:
        p.poly([(-5, -1), (5, -1.6), (7, 0), (-5, 1.4)])


def death_asesino(c, i, n):
    gen_death(c, i, n, lambda cc, P, plain=False: human(cc, P, 'idle', M_ASE, ase_head, (lambda c2, PP, r, f: None) if plain else ase_weapon, back_fn=ase_back, torso_extra=ase_torso, legs=(6.8, 6.8), thick=(1.8, 1.6)),
              lambda a, k, m: ase_pose(a, k, m),
              bits=[dict(fn=_p_dagger, x=8, y=-18, r=1.5, vx=6, vy=-6, spin=7, rest=0.1, bounce=0.35),
                    dict(fn=_p_dagger, x=-4, y=-18, r=1.5, vx=-5, vy=-6, spin=-6, rest=2.9, bounce=0.35)], soul=ECLC)


def sheet_asesino_eclipse():
    return enemy_sheet('en_asesino_eclipse', (48, 48), (24, 46), (11, 30), draw_asesino, (22, 18, 12),
                       STD(5, hit=[2, 3], box=[2, -28, 24, 26], idle=6, walk=8, ifps=8, wfps=13, fa=17, death=8))


SHEETS = [sheet_lobo_musgo, sheet_tirador_rayo, sheet_cultista_sangre, sheet_asesino_eclipse]
