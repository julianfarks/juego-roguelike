from common import *
from en_catacumbas import enemy_sheet, STD, DARK, WHITE

LAVA = Mat(ramp=['#6a0c08', '#c02c0c', '#ff6a1a', '#ffb032', '#fff0a0'], emi=True, nooutline=True, bevel=4.5, dith=0.2)
LAVA_O = Mat(ramp=['#4a0808', '#8a1a0a', '#c4400e', '#ff7a1a'], emi=True, nooutline=False, outcol='#3a0c0c', bevel=2.6, dith=0.2)
BAS = Mat(ramp=['#0c0a12', '#1c1822', '#2e2832', '#463c48', '#6c5c64'], bevel=1.6, tex=0.4, seed=41, bias=0.4)
BAS_B = Mat(ramp=['#08060c', '#14101a', '#221c26', '#362e38', '#52464c'], bevel=1.6, tex=0.4, seed=42)
FLAME_O = Mat(ramp=['#8a1008', '#d83a10', '#ff7a1a'], emi=True, nooutline=True, bevel=3.0, dith=0.25)
FLAME_M = Mat(ramp=['#ff6a1a', '#ff9a22', '#ffc844'], emi=True, nooutline=True, bevel=2.4, dith=0.25)
FLAME_I = Mat(ramp=['#ffc844', '#ffe27a', '#fff6c0', '#ffffff'], emi=True, nooutline=True, bevel=2.0, dith=0.25)
EMBER = '#ffa030'
MASK = Mat(ramp=['#1c1418', '#3c2c2c', '#6a5448', '#a08c76', '#d8c8a6'], bevel=1.4, tex=0.25, seed=43)
HOTEYE = Mat(ramp=['#ff8a1a', '#ffd040', '#fff4b0', '#ffffff'], emi=True, nooutline=True, bevel=0.8, dith=0.1)
IRONF = Mat(ramp=['#14121c', '#2c2a38', '#4a4858', '#706e80', '#a4a2b4'], bevel=1.4, tex=0.3, seed=44)
HOTIRON = Mat(ramp=['#7a1808', '#d03a10', '#ff7a20', '#ffc050', '#fff0b0'], emi=True, nooutline=True, bevel=1.4, dith=0.2)
BSKIN = Mat(ramp=['#2a1218', '#52262a', '#7e3e36', '#aa6048', '#d48c64'], bevel=2.4, tex=0.3, seed=45, bias=0.4)
BSKIN_B = Mat(ramp=['#1e0c12', '#3c1a20', '#5e2e2c', '#84483a', '#a86c4e'], bevel=2.4, tex=0.3, seed=46)
LEATH = Mat(ramp=['#140e12', '#2a1c1c', '#46302a', '#6a4a38', '#8c6648'], bevel=1.4, tex=0.35, seed=47)
BRICK = Mat(ramp=['#240c14', '#4a1a1e', '#7a2c28', '#a64a36', '#cc7048'], bevel=1.2, tex=0.4, seed=48)

# ------------------------------------------------------------------ CUBO DE MAGMA
def cubo_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(sx=1.0, sy=1.0, x=0.0, y=0.0, tilt=0.0, gap=0.0, glow=0.3, eye=0.3, flash=0.0, k=None)
    if a == 'idle':
        P.update(sy=1.0 + 0.06 * s, sx=1.0 - 0.04 * s, glow=0.3 + 0.2 * s, gap=0.3 + 0.3 * (s > 0.5))
    elif a == 'walk':   # salto en 6 fotogramas
        seq = [(1.18, 0.78, 0, 0.8), (0.86, 1.22, 0, 0.2), (0.82, 1.24, -7, 0), (0.92, 1.1, -9, 0), (1.0, 1.0, -4, 0), (1.22, 0.74, 0, 0.9)]
        sx, sy, y, g = seq[i % 6]
        P.update(sx=sx, sy=sy, y=y, x=[-1, 0, 1, 2, 2, 1][i % 6], gap=g, glow=0.4 + 0.3 * g)
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(sx=lerp(1.0, 1.3, w), sy=lerp(1.0, 0.68, w), gap=lerp(0.3, 2.0, w), glow=lerp(0.4, 1.0, w), eye=w, tilt=-0.1 * w)
    elif a == 'attack':
        k = i / (n - 1)
        P.update(sx=kf(k, [(0, 1.3), (0.2, 0.8), (0.5, 0.95), (0.8, 1.1), (1, 1.0)]),
                 sy=kf(k, [(0, 0.68), (0.2, 1.3), (0.5, 1.05), (0.8, 0.85), (1, 1.0)]),
                 y=kf(k, [(0, 0), (0.2, -10), (0.45, -8), (0.75, 0), (1, 0)]),
                 x=kf(k, [(0, -2), (0.2, 4), (0.45, 12), (0.75, 12), (1, 8)]), tilt=kf(k, [(0, -0.1), (0.3, 0.25), (1, 0.05)]),
                 gap=1.4 if k < 0.8 else 0.4, glow=1.0, eye=1.0)
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(sx=[1.3, 1.1][i], sy=[0.72, 0.92][i], x=rx, tilt=ln * 0.6, flash=fl, gap=1.5 if i == 0 else 0.8, glow=1.0)
    return P


def cubo_body(c, P):
    x, y, sx, sy = P['x'], P['y'], P['sx'], P['sy']
    g = P['gap']
    with c.at(x - 1, y, P['tilt'], sx, sy):
        # salpicaduras de lava y goteo
        with c.part(LAVA_O, bevel=3.0) as p:
            p.poly([(-10, -14), (-7, -18.5), (7.5, -18.5), (10.5, -15), (11, -3), (8, 0), (-8, 0), (-11, -4)])
        with c.part(LAVA, bevel=4.0) as p:
            p.poly([(-8, -14), (-5, -16.5), (6, -16.5), (8.6, -14), (9, -3.5), (6.5, -1.5), (-6.5, -1.5), (-9, -4.5)])
        # corteza: placas de basalto separadas por grietas (g las separa)
        with c.part(BAS, line=0.4, bevel=1.8) as p:      # techo
            p.poly([(-11, -13 - g), (-8, -19.5 - g), (1, -20 - g), (3, -15.5 - g * 0.5), (-4, -13.5), (-8, -11)])
        with c.part(BAS, line=0.4, bevel=1.8) as p:
            p.poly([(3.2 + g * 0.6, -19.5 - g), (9.5 + g, -17 - g * 0.6), (12 + g, -11), (7.5 + g * 0.5, -10), (5, -14)])
        with c.part(BAS_B, line=0.4, bevel=1.8) as p:    # lado izq
            p.poly([(-11.5 - g, -9), (-8.2 - g * 0.5, -10.5), (-6.5, -5), (-8 - g * 0.5, -0.8), (-11 - g, -2)])
        with c.part(BAS, line=0.4, bevel=1.8) as p:      # base derecha
            p.poly([(5.5 + g * 0.6, -6.5), (10.5 + g, -7.5), (11.5 + g, -1.0 + g * 0.3), (6.2 + g * 0.3, 0.3 + g * 0.4)])
        with c.part(BAS_B, line=0.4, bevel=1.6) as p:
            p.poly([(-4, 0.2 + g * 0.4), (1.5, 0.4 + g * 0.5), (2.5, -2.2), (-3, -3)])
        # cara incandescente
        e = P['eye']
        with c.part(DARK) as p:
            p.poly([(-4.8, -11.6), (-1.2, -10.4), (-1.6, -8.4), (-5.2, -9.4)])
            p.poly([(2.4, -10.4), (6.2, -11.8), (6.4, -9.4), (3.0, -8.6)])
        with c.part(HOTEYE) as p:
            p.poly([(-4.0, -10.6), (-1.8, -9.9), (-2.0, -9.0), (-4.2, -9.6)])
            p.poly([(3.0, -9.9), (5.6, -10.8), (5.6, -9.6), (3.2, -9.2)])
        with c.part(DARK) as p:
            p.poly([(-2.5, -6.0), (4.5, -6.4), (4.0, -4.6), (-1.6, -4.4)])
            for k in range(3):
                p.rect(-1.5 + k * 2.0, -6.0, -0.8 + k * 2.0, -4.0)
    c.glow(x, y - 9 * sy, 11, '#ff7a20', 0.18 + 0.3 * P['glow'])


def draw_cubo(c, a, i, n):
    if a == 'death':
        return death_cubo(c, i, n)
    P = cubo_pose(a, i, n)
    if a == 'attack' and 0.12 < i / (n - 1) < 0.7:
        pass
    cubo_body(c, P)
    if P['flash']:
        c.flash(WHITE, P['flash'])
    if a == 'windup':
        for q in range(3):
            c.dotw(-6 + q * 6 + math.sin(i + q) * 2, -22 - ((i * 3 + q * 4) % 8), EMBER)


def _plate(pts, m=BAS):
    def f(c):
        with c.part(m, line=0.4, bevel=1.6) as p:
            p.poly(pts)
    return f


def _blob(r):
    def f(c):
        with c.part(LAVA, bevel=2.2) as p:
            p.ell(0, 0, r, r * 0.8)
    return f


def death_cubo(c, i, n):
    if i == 0:
        cubo_body(c, cubo_pose('hurt', 0, 2))
        c.flash(WHITE, 0.55)
        return
    u = i / (n - 1)
    # nucleo se hincha y revienta
    if u < 0.35:
        P = cubo_pose('windup', 3, 4)
        P['sx'] = 1.3 + u * 1.2; P['sy'] = 0.85 + u * 0.3; P['gap'] = 2 + u * 8
        cubo_body(c, P)
        c.flash('#ffd060', 0.2 + u)
    items = []
    import random
    rnd = random.Random(8)
    plates = [[(-5, -3), (5, -4), (6, 3), (-4, 4)], [(-6, -2), (2, -4), (5, 1), (-3, 4)], [(-4, -4), (5, -2), (3, 4), (-6, 2)],
              [(-3, -3), (4, -3), (4, 3), (-4, 3)], [(-5, -2), (3, -4), (6, 2), (-2, 3)]]
    for k, pl in enumerate(plates):
        items.append(dict(fn=_plate(pl, BAS if k % 2 else BAS_B), x=-6 + k * 3, y=-12 - (k % 2) * 4, r=3, vx=(k - 2) * 2.2, vy=-8 - k, spin=rnd.uniform(-5, 5), rest=rnd.uniform(-0.5, 0.5), bounce=0.3))
    for k in range(6):
        items.append(dict(fn=_blob(2.2 - 0.2 * (k % 3)), x=-3 + k, y=-9, r=1.5, vx=(k - 2.5) * 2.6, vy=-10 - (k % 3) * 2, spin=0, rest=0, bounce=0.0))
    b = Bits(items, seed=4, T=0.8, g=1.6)
    if u >= 0.3:
        draw_bits(c, b, (u - 0.3) / 0.7 * 1.0)
    # charco de lava enfriandose
    if u >= 0.3:
        w = min(1.0, (u - 0.3) / 0.5)
        cool = max(0.0, (u - 0.6) / 0.4)
        with c.part(LAVA_O if cool < 0.7 else BAS_B, bevel=1.2) as p:
            p.ell(-1, -1.2, 5 + 8 * w, 1.6 + 1.2 * w)
        if cool < 0.9:
            with c.part(LAVA, bevel=1.4) as p:
                p.ell(-1, -1.4, 3 + 5 * w, 0.9 + 0.5 * w)
    if u > 0.3 and u < 0.9:
        for q in range(6):
            c.dotw(-8 + q * 3 + (q - 3) * u * 3, -6 - u * 12 + q * 0.5 - (q % 3) * 3, EMBER)


# ------------------------------------------------------------------ ESPIRITU LLAMA
def flame_tongue(c, base, tip, w, m, sway=0.0):
    mid = (lerp(base[0], tip[0], 0.55) + sway, lerp(base[1], tip[1], 0.55))
    with c.part(m, bevel=w * 0.9) as p:
        p.poly([(base[0] - w, base[1]), (mid[0] - w * 0.7, mid[1]), (tip[0], tip[1]), (mid[0] + w * 0.5, mid[1] + 1), (base[0] + w, base[1])])


def llama_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(y=-3.0 + 2.2 * s, x=-2.0, ph=t, lean=0.05, charge=0.0, ball=0.0, arms=(0.6, 0.6), flash=0.0, eyes=0.5, big=1.0, k=None)
    if a == 'walk':
        P.update(x=-1.0, lean=0.2, y=-3.0 + 2.6 * math.sin(2 * math.pi * t))
    if a == 'windup':
        w = sm((i + 1) / n)
        P.update(charge=w, ball=w, arms=(lerp(0.6, -0.3, w), lerp(0.6, -0.3, w)), lean=lerp(0.05, -0.2, w), x=lerp(-2, -4, w), eyes=1.0, big=1.0 + 0.2 * w)
    if a == 'attack':
        k = i / (n - 1)
        P.update(ball=[1.0, 1.0, 0.0, 0.0, 0.0, 0.0][i], arms=(kf(k, [(0, -0.3), (0.4, 0.2), (1, 0.6)]),) * 2,
                 lean=[-0.2, -0.1, 0.25, 0.15, 0.05, 0.05][i], x=[-4, -4, 0, -1, -2, -2][i], eyes=1.0, charge=[1, 1, 0.3, 0, 0, 0][i], big=[1.2, 1.3, 1.0, 1.0, 1.0, 1.0][i],
                 rel=(i == 3))
    if a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(x=-2 + rx, lean=ln, flash=fl, big=0.85 if i == 0 else 0.95, eyes=0.2)
    return P


def llama_body(c, P, t_off=0.0):
    x, y, lean = P['x'], P['y'] - 16, P['lean']
    ph = P['ph'] * 6.283 + t_off
    big = P['big']
    # cola de fuego (abajo)
    for k, (dx, ln, w) in enumerate([(-4.5, 12, 3.2), (0.5, 15, 4.0), (4.0, 10, 3.0)]):
        sw = math.sin(ph * 2 + k * 2.0) * 2.4
        flame_tongue(c, (x + dx * 0.6, y + 4), (x + dx - lean * 6 + sw - 3 * lean, y + 4 + ln * (0.9 + 0.1 * math.sin(ph * 3 + k))), w, FLAME_O, sw * 0.4)
    # cuerpo exterior
    with c.at(x, y, lean):
        with c.part(FLAME_O, bevel=4.0) as p:
            p.ell(0, 0, 9.0 * big, 10.5 * big)
            p.poly([(-7, -6), (-8.5, -14 - 2 * math.sin(ph * 2)), (-4, -9), (-3, -17 - 3 * math.sin(ph * 2 + 1)), (0, -9), (3, -19 - 3 * math.sin(ph * 2 + 2)), (5, -9),
                    (8.5, -15 - 2 * math.sin(ph * 2 + 3)), (7.5, -5)])
        with c.part(FLAME_M, bevel=3.0) as p:
            p.ell(0.5, 1.5, 6.4 * big, 8 * big)
            p.poly([(-4, -4), (-3, -11 - 2 * math.sin(ph * 2 + 1)), (0, -5), (2.5, -13 - 2 * math.sin(ph * 2 + 2)), (4.5, -4)])
        with c.part(FLAME_I, bevel=2.2) as p:
            p.ell(1, 3.5, 3.6 * big, 5 * big)
    # brazos de llama
    a1, a2 = P['arms']
    shx, shy = x + 3.5, y + 1
    hand = (shx + 8 * math.cos(a1 + 0.2), shy + 8 * math.sin(a1 + 0.2) + 1)
    hand2 = (shx + 1 + 6.5 * math.cos(a2 + 0.5), shy + 2 + 6.5 * math.sin(a2 + 0.5))
    for hnd, m in ((hand2, FLAME_O), (hand, FLAME_M)):
        with c.part(m, bevel=2.0) as p:
            p.limb((shx, shy), hnd, 2.8, 2.0)
        flame_tongue(c, hnd, (hnd[0] + 3.5, hnd[1] - 3.5 + math.sin(ph * 3) * 1), 1.7, FLAME_I)
    # mascara de craneo
    with c.at(x + 2.5, y - 4.5, lean * 0.8):
        with c.part(MASK, line=0.5, bevel=1.7) as p:
            p.ell(0, 0, 5.6, 5.8)
            p.poly([(-3.5, 3.5), (3.5, 3.5), (3.0, 7.4), (-2.5, 7.4)])
            p.poly([(-4.8, -3.5), (-6.8, -9.0), (-3.2, -5.2)])         # cuernos de fuego
            p.poly([(4.2, -4.2), (6.2, -9.5), (2.2, -5.8)])
        with c.part(DARK) as p:
            p.ell(-1.9, -0.3, 1.9, 2.3, 0.2)
            p.ell(2.6, -0.2, 1.8, 2.2, -0.2)
            p.poly([(0.3, 2.6), (1.0, 3.8), (-0.4, 3.8)])
            for k in range(4):
                p.rect(-2.7 + k * 1.8, 4.6, -2.2 + k * 1.8, 7.6)
        with c.part(HOTEYE) as p:
            e = P['eyes']
            p.ell(-1.9, -0.3, 0.9 + 0.5 * e, 1.2 + 0.5 * e)
            p.ell(2.6, -0.2, 0.9 + 0.5 * e, 1.2 + 0.5 * e)
        c.glow(0, -0.2, 7, '#ffb030', 0.25 + 0.4 * P['eyes'])
    return hand


def draw_llama(c, a, i, n):
    if a == 'death':
        return death_llama(c, i, n)
    P = llama_pose(a, i, n)
    hand = llama_body(c, P)
    if P['ball'] > 0.05:
        bx, by = hand[0] + 3 + 3 * P['ball'], hand[1] - 1
        r = 2.0 + 3.8 * P['ball']
        with c.part(FLAME_O, bevel=3) as p:
            p.ell(bx, by, r + 1.2)
        with c.part(FLAME_M, bevel=2.6) as p:
            p.ell(bx, by, r)
        with c.part(FLAME_I, bevel=2) as p:
            p.ell(bx, by, r * 0.55)
        c.glow(bx, by, r + 4, '#ffc050', 0.3)
        for q in range(5):
            ang = q * 1.26 + i * 1.7
            c.dotw(bx + math.cos(ang) * (r + 3), by + math.sin(ang) * (r + 3), EMBER)
    if P['flash']:
        c.flash(WHITE, P['flash'])
    if a == 'windup' and i == n - 1:
        c.flash('#ffb040', 0.12)


def _mask_piece(c):
    with c.part(MASK, line=0.5, bevel=1.7) as p:
        p.ell(0, 0, 5.6, 5.8)
        p.poly([(-3.5, 3.5), (3.5, 3.5), (3.0, 7.4), (-2.5, 7.4)])
    with c.part(DARK) as p:
        p.ell(-1.9, -0.3, 1.9, 2.3, 0.2)
        p.ell(2.6, -0.2, 1.8, 2.2, -0.2)
        for k in range(4):
            p.rect(-2.7 + k * 1.8, 4.6, -2.2 + k * 1.8, 7.6)


def death_llama(c, i, n):
    if i == 0:
        P = llama_pose('hurt', 0, 2)
        llama_body(c, P)
        c.flash(WHITE, 0.5)
        return
    u = i / (n - 1)
    P = llama_pose('hurt', 1, 2)
    if u < 0.5:
        P['big'] = 1.0 + u * 1.2
        P['y'] = -3 + u * 4
        llama_body(c, P)
        c.flash('#ffe090', min(0.7, u * 1.6))
    else:
        # explosion: lenguas radiales
        v = (u - 0.5) / 0.5
        for q in range(9):
            ang = q * 0.7 + 0.2
            r0 = 4 + v * 16
            fx, fy = math.cos(ang) * r0 * 1.2, -16 + math.sin(ang) * r0 * 0.9
            if fy < -1.5 - 2 * (1 - v):
                s_ = max(0.5, 3.2 * (1 - v))
                with c.part(FLAME_O if q % 2 else FLAME_M, bevel=1.5) as p:
                    p.ell(fx, fy, s_ + 0.8, s_)
    # craneo cae
    items = [dict(fn=_mask_piece, x=2.5, y=-20, r=4.5, vx=1.5, vy=-8, spin=3, rest=0.5, bounce=0.3)]
    b = Bits(items, seed=2, T=0.8, g=1.7)
    if u > 0.12:
        draw_bits(c, b, (u - 0.12) / 0.88)
    # brasas / ceniza en el suelo
    if u > 0.5:
        v = (u - 0.5) / 0.5
        with c.part(BAS_B, bevel=1.0) as p:
            p.ell(0, -1.0, 4 + 6 * v, 1.4 + 0.6 * v)
        with c.part(LAVA_O, bevel=1.0) as p:
            p.ell(-1, -1.2, 2 + 3 * v, 0.7)
    if 0.2 < u < 0.95:
        for q in range(8):
            c.dotw(-8 + q * 2.4 + (q - 4) * u * 2, -8 - u * 14 + (q % 3) * -3, EMBER if q % 2 else '#ffe080')


# ------------------------------------------------------------------ BRUTO DE LA FORJA (64x64)
def bruto_pose(a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(hx=-3.0, dy=0.0, lean=0.12, ph=t, walk=False, stride=0, lift=0, arm=(0.9, 1.0), arm2=(1.0, 1.1),
             ham=1.1, hot=0.3, flash=0.0, head=0.0, k=None, crouch=0.0)
    if a == 'idle':
        P['dy'] = 0.7 * s
        P['arm'] = (0.7 + 0.05 * s, -0.5)
        P['ham'] = -1.0 + 0.04 * s
        P['hot'] = 0.3 + 0.15 * s
    elif a == 'walk':
        P.update(walk=True, stride=5.0, lift=2.8, dy=-1.8 * abs(math.sin(2 * math.pi * t)) + 0.6, lean=0.28, hx=-1.0)
        P['arm'] = (0.7 + 0.1 * s, -0.5)
        P['arm2'] = (0.9 - 0.3 * s, 1.0)
        P['ham'] = -1.0 + 0.1 * s
        P['head'] = 0.15
    elif a == 'windup':
        w = sm((i + 1) / n)
        P.update(lean=lerp(0.12, -0.3, w), hx=lerp(-3, -7, w), dy=lerp(0, 3.0, w), hot=lerp(0.3, 1.0, w), head=lerp(0, -0.2, w))
        P['arm'] = (lerp(0.7, -2.3, w), lerp(-0.5, -0.4, w))
        P['arm2'] = (lerp(1.0, -2.0, w), lerp(1.1, -0.2, w))
        P['ham'] = lerp(-1.0, -2.4, w)
    elif a == 'attack':
        k = i / (n - 1)
        P['lean'] = kf(k, [(0, -0.3), (0.2, 0.2), (0.45, 0.5), (0.75, 0.42), (1, 0.18)])
        P['hx'] = kf(k, [(0, -7), (0.2, 0), (0.45, 8), (0.75, 8), (1, 3)])
        P['dy'] = kf(k, [(0, 3), (0.45, 4.5), (1, 1)])
        P['arm'] = (kf(k, [(0, -2.3), (0.2, -0.5), (0.45, 1.0), (0.75, 1.05), (1, 0.9)]), kf(k, [(0, -0.4), (0.45, 0.35), (1, 0.8)]))
        P['arm2'] = (kf(k, [(0, -2.0), (0.2, -0.4), (0.45, 0.9), (0.75, 1.0), (1, 0.9)]), kf(k, [(0, -0.2), (0.45, 0.4), (1, 0.9)]))
        P['ham'] = kf(k, [(0, -2.4), (0.2, -0.9), (0.45, 1.1), (0.75, 1.3), (1, 1.1)])
        P['hot'] = 1.0 if k < 0.8 else 0.5
        P['k'] = k
        P['head'] = kf(k, [(0, -0.2), (0.45, 0.3), (1, 0.1)])
        P['walk'] = False
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(hx=-3 + rx * 1.2, lean=ln, flash=fl * 0.9, head=-0.3 if i == 0 else -0.15, hot=1.0)
        P['arm'] = (0.3, 0.9) if i == 0 else (0.7, 1.0)
        P['arm2'] = (0.2, 0.8) if i == 0 else (0.7, 1.0)
        P['ham'] = 0.2 if i == 0 else 0.9
    return P


def bruto_body(c, P, a='idle', with_ham=True):
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
    with c.part(BSKIN_B, line=0.5, bevel=2.8) as p:
        p.limb(shf, e2, 4.0, 3.5); p.limb(e2, h2, 3.5, 3.2)
    with c.part(IRONF, line=0.5, bevel=1.6) as p:
        p.limb((lerp(e2[0], h2[0], 0.45), lerp(e2[1], h2[1], 0.45)), h2, 3.9, 3.6)    # brazalete
    with c.part(BSKIN_B, bevel=2.0) as p:
        p.ell(h2[0] + 0.5, h2[1] + 0.5, 3.5)
    leg(c, (hip[0] - 3, hip[1] + 2), (hip[0] - 3 + f1[0], f1[1]), 9.8, 9.8, 4.6, 4.0, BSKIN_B, bend=-1, footmat=IRONF, footlen=7, footh=3.6)
    with c.at(hip[0] + 2 * sl[0], hip[1] + 2 * sl[1], lean):
        with c.part(BSKIN, line=0.5, bevel=3.8) as p:    # torso ancho en V
            p.poly([(-11, -22), (13, -22), (14, -14), (9, -2), (-8, -2), (-12, -12)])
        with c.part(BRICK, bevel=1.2) as p:               # quemaduras / cicatrices
            p.poly([(2, -17), (8, -15), (7, -13), (1, -14)])
            p.poly([(-6, -9), (-1, -11), (-1, -9), (-5, -7)])
        with c.part(HOTIRON, bevel=0.8) as p:
            p.limb((3, -16.5), (7.5, -14.8), 0.6)
        # delantal de cuero y cinturon con cadena
        with c.part(LEATH, line=0.5, bevel=1.6) as p:
            p.poly([(-9, -4), (11, -4), (13, 4), (11, 14), (-6, 16), (-10, 6)])
        with c.part(IRONF, line=0.4, bevel=1.0) as p:
            p.poly([(-9.5, -5), (12, -5), (12, -2), (-9.5, -2)])
            p.ell(1.5, -3.5, 2.4, 2.0)
        with c.part(HOTIRON) as p:
            p.ell(1.5, -3.5, 1.0, 0.8)
        # peto de hierro parcial + remaches
        with c.part(IRONF, line=0.5, bevel=1.8) as p:
            p.poly([(-12, -23), (-4, -26), (-1, -20), (-4, -13), (-12, -14)])
        with c.part(HOTIRON) as p:
            for (rx, ry) in ((-9, -21), (-5, -22), (-9, -16)):
                p.ell(rx, ry, 0.7, 0.7)
    leg(c, (hip[0] + 3, hip[1] + 2), (hip[0] + 3 + f2[0], f2[1]), 9.8, 9.8, 4.8, 4.1, BSKIN, bend=-1, footmat=IRONF, footlen=7, footh=3.6)
    # cabeza con yelmo de hierro (hundida entre hombros)
    nk = (hip[0] + 23 * sl[0] + 3, hip[1] + 23 * sl[1] - 6)
    with c.at(nk[0] + 2.0, nk[1], lean * 0.4 + P['head']):
        with c.part(IRONF, line=0.5, bevel=2.2) as p:
            p.ell(0, 0, 6.8, 6.2)
            p.poly([(-5, 2), (5.5, 2), (6, 7), (-4, 7)])
            p.poly([(-3.5, -4.5), (-6.5, -11), (-1.5, -5.5)])      # cuerno
            p.poly([(3.5, -4.8), (6.8, -11.5), (1.5, -5.8)])
        with c.part(DARK) as p:
            p.poly([(0.5, -1.4), (6.6, -1.8), (6.4, 1.2), (0.8, 1.0)])      # visera
        with c.part(HOTEYE) as p:
            p.poly([(1.6, -0.8), (5.8, -1.1), (5.7, 0.4), (1.7, 0.3)])
        with c.part(HOTIRON) as p:
            p.rect(-5, -0.2, -1.5, 0.3)
        c.glow(4, -0.5, 6, '#ffa030', 0.3 + 0.4 * P['hot'])
    # hombrera + brazo cercano + martillo
    shn = (chest[0] - 2, chest[1] - 2)
    e1, h1 = fk(shn, P['arm'][0], 11.5, P['arm'][1], 11.5)
    with c.part(BSKIN, line=0.5, bevel=2.8) as p:
        p.limb(shn, e1, 4.4, 3.9); p.limb(e1, h1, 3.9, 3.4)
    with c.part(IRONF, line=0.5, bevel=1.6) as p:
        p.limb((lerp(e1[0], h1[0], 0.45), lerp(e1[1], h1[1], 0.45)), h1, 4.3, 3.9)
    if with_ham:
        ha = P['ham']
        d = (math.cos(ha), math.sin(ha)); nr = (-d[1], d[0])
        end = (h1[0] + d[0] * 17, h1[1] + d[1] * 17)
        with c.part(LEATH, line=0.4, bevel=1.0) as p:
            p.limb((h1[0] - d[0] * 5, h1[1] - d[1] * 5), end, 1.5)
        hc = (end[0] + d[0] * 3.5, end[1] + d[1] * 3.5)
        with c.part(IRONF, line=0.5, bevel=1.8) as p:
            p.poly([(hc[0] - d[0] * 6 + nr[0] * 6, hc[1] - d[1] * 6 + nr[1] * 6), (hc[0] + d[0] * 6 + nr[0] * 6, hc[1] + d[1] * 6 + nr[1] * 6),
                    (hc[0] + d[0] * 6 - nr[0] * 6, hc[1] + d[1] * 6 - nr[1] * 6), (hc[0] - d[0] * 6 - nr[0] * 6, hc[1] - d[1] * 6 - nr[1] * 6)])
        hot = P['hot']
        with c.part(HOTIRON, bevel=1.2) as p:
            q = 0.55 + 0.45 * hot
            p.poly([(hc[0] + d[0] * 6 + nr[0] * 5 * q, hc[1] + d[1] * 6 + nr[1] * 5 * q), (hc[0] + d[0] * 6.4 + nr[0] * 5 * q, hc[1] + d[1] * 6.4 + nr[1] * 5 * q),
                    (hc[0] + d[0] * 6.4 - nr[0] * 5 * q, hc[1] + d[1] * 6.4 - nr[1] * 5 * q), (hc[0] + d[0] * 6 - nr[0] * 5 * q, hc[1] + d[1] * 6 - nr[1] * 5 * q)])
            p.ell(hc[0] + d[0] * 5, hc[1] + d[1] * 5, 4 * q, 4 * q)
        c.glow(hc[0] + d[0] * 3, hc[1] + d[1] * 3, 11, '#ff8a20', 0.2 + 0.5 * hot)
        if P['k'] is not None and 0.3 < P['k'] < 0.8:
            arc_trail(c, shn[0], shn[1], 12, 28, -1.9 + (P['k'] - 0.2) * 3, -0.5 + (P['k'] - 0.2) * 3, TRAIL_F)
            for q in range(8):
                c.dotw(hc[0] + 6 + q * 2, -1.5 - (q % 3) * 1.2, EMBER if q % 2 else '#ffe080')
    with c.part(BSKIN, bevel=2.0) as p:
        p.ell(h1[0] + 0.3, h1[1] + 0.3, 3.7)
    with c.part(IRONF, line=0.5, bevel=1.8) as p:           # hombrera
        sx, sy = shn[0] - 1, shn[1] - 1
        p.poly([(sx - 4.5, sy + 3), (sx - 3.5, sy - 2), (sx + 2, sy - 4), (sx + 6, sy - 1), (sx + 5, sy + 3), (sx, sy + 4)])
    with c.part(HOTIRON) as p:
        p.ell(shn[0] - 0.5, shn[1] - 3.5, 0.8, 0.8)


TRAIL_F = Mat(ramp=['#c84a14', '#ff8a2a', '#ffd070', '#fff4c8'], emi=True, nooutline=True, bevel=1.5, dith=0.2)


def draw_bruto(c, a, i, n):
    if a == 'death':
        return death_bruto(c, i, n)
    P = bruto_pose(a, i, n)
    bruto_body(c, P, a)
    if P['flash']:
        c.flash(WHITE, P['flash'])
    if a == 'windup' and i == n - 1:
        c.flash('#ff8a20', 0.10)


def _p_hammer(c):
    with c.part(LEATH, line=0.4, bevel=1.0) as p:
        p.limb((-12, 0), (6, 0), 1.5)
    with c.part(IRONF, line=0.5, bevel=1.8) as p:
        p.rect(5, -6, 17, 6)
    with c.part(HOTIRON, bevel=1.2) as p:
        p.rect(16, -5, 17.4, 5)


def _p_helm(c):
    with c.part(IRONF, line=0.5, bevel=2.2) as p:
        p.ell(0, 0, 6.8, 6.2)
        p.poly([(-3.5, -4.5), (-6.5, -11), (-1.5, -5.5)])
    with c.part(DARK) as p:
        p.poly([(0.5, -1.4), (6.6, -1.8), (6.4, 1.2), (0.8, 1.0)])
    with c.part(HOTEYE) as p:
        p.poly([(1.6, -0.8), (5.8, -1.1), (5.7, 0.4), (1.7, 0.3)])


def death_bruto(c, i, n):
    if i == 0:
        bruto_body(c, bruto_pose('hurt', 0, 2), 'hurt')
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
            bruto_body(c, P, 'hurt', with_ham=False)
    items = [dict(fn=_p_hammer, x=14, y=-30, r=6, vx=7, vy=-7, spin=4, rest=0.15, bounce=0.3),
             dict(fn=_p_helm, x=2, y=-42, r=6, vx=5, vy=-9, spin=-5, rest=0.4, bounce=0.35)]
    for d_ in items:
        d_['vx'] *= 0.6; d_['vy'] *= 0.7
    b = Bits(items, seed=3, T=0.65, g=3.0)
    if u > 0.12:
        draw_bits(c, b, min(1, (u - 0.12) / 0.88))
    if u > 0.4:
        for q in range(10):
            c.dotw(-16 + q * 4 + (q - 5) * u * 2, -2 - (q % 4) * 2 - (u - 0.4) * 8, EMBER if q % 2 else '#ffe080')


def sheet_cubo_magma():
    return enemy_sheet('en_cubo_magma', (48, 48), (24, 46), (20, 20), draw_cubo, (40, 12, 14),
                       STD(5, hit=[1, 3], box=[-8, -26, 30, 26], idle=6, walk=6, wfps=9, fa=13, death=7, dfps=10))


def sheet_llama():
    return enemy_sheet('en_llama', (48, 48), (24, 46), (16, 26), draw_llama, (60, 14, 10),
                       STD(6, rel=3, muz=[15, -26], idle=6, walk=6, wfps=10, fa=14, death=8))


def sheet_bruto_forja():
    return enemy_sheet('en_bruto_forja', (64, 64), (32, 62), (24, 50), draw_bruto, (24, 12, 16),
                       STD(6, hit=[2, 4], box=[6, -46, 30, 46], idle=6, walk=8, ifps=6, wfps=8, fa=10, death=8, dfps=8))


SHEETS = [sheet_cubo_magma, sheet_llama, sheet_bruto_forja]
