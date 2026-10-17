"""Elites unicos (lote B): ventisca, capitan del trueno, sacerdote carmesi, centurion del eclipse."""
from common import *
from humanoid import human
from en_catacumbas import enemy_sheet, DARK, WHITE
from en_nuevos_a import PLATE, PLATE_D, GOLDT, ICE, ICE_D, CORE, ROBE_D
from en_elites_a import (draw_elite, _anims, hold, WOOD, IRON, hfeet)

# ------------------------------------------------------------------ materiales
STEEL_B = Mat(ramp=['#0a1020', '#18284a', '#2c4a80', '#4a78c0', '#8ab8ff'], bevel=1.6, tex=0.25, seed=91)
STEEL_BD = Mat(ramp=['#060a14', '#0e1630', '#1c2e58', '#30508c', '#5880c0'], bevel=1.6, tex=0.25, seed=92)
WHITEM = Mat(ramp=['#8a98b8', '#c0cce4', '#e8f0ff', '#ffffff'], bevel=1.0, seed=93)
BOLT = Mat(ramp=['#2a6ac8', '#5aa8ff', '#b8e0ff', '#ffffff'], emi=True, nooutline=True, bevel=1.0, dith=0.1)
BOLTC = '#6AB8FF'
CRIM = Mat(ramp=['#1a0408', '#3a0a14', '#6a1424', '#a02038', '#d8465c'], bevel=2.0, tex=0.3, seed=94)
CRIM_D = Mat(ramp=['#0e0204', '#240610', '#420c18', '#6a1424', '#94243a'], bevel=2.0, tex=0.3, seed=95)
BLOODG = Mat(ramp=['#8a0c1c', '#d0203a', '#ff5a6c', '#ffc0c8'], emi=True, nooutline=True, bevel=2.0, dith=0.15)
GOLDB = Mat(ramp=['#3a2a0e', '#7a5a1a', '#b88a2a', '#e8c050', '#fff0a0'], bevel=1.2, seed=96)
SUN = Mat(ramp=['#c88a14', '#ffc83a', '#ffe88a', '#ffffff'], emi=True, nooutline=True, bevel=1.4, dith=0.1)
SUNC = '#FFD25A'
ECL_B = Mat(ramp=['#020204', '#0a0a14', '#161628', '#28284a', '#40407a'], bevel=1.8, tex=0.2, seed=97)
ECL_D = Mat(ramp=['#010102', '#06060c', '#0e0e1c', '#1a1a34', '#2c2c58'], bevel=1.8, tex=0.2, seed=98)


# ================================================================== VENTISCA (espiritu de hielo volador)
def ven_draw(c, a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    fl = 0.0
    dy = -4 + 2.2 * s
    lean = 0.0; glow = 0.0; spread = 0.0; stretch = 0.0; sx = 1.0
    if a == 'walk':
        lean = 0.12; dy = -4 + 2.6 * s
    elif a in ('windup', 'windup2'):
        w = sm((i + 1) / n)
        glow = w; spread = -0.6 * w if a == 'windup' else 0.0; lean = -0.2 * w if a == 'windup2' else 0
        dy = -4 - 4 * w
        if a == 'windup2':
            sx = 1 - 0.1 * w
    elif a == 'attack':
        glow = [1, 1, 0.8, 0.4, 0][min(i, 4)]; spread = [0.2, 1.0, 1.4, 1.0, 0.4][min(i, 4)]; dy = -8
    elif a == 'attack2':
        lean = 0.9; stretch = 1.0; glow = 1; dy = -10
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        lean = ln * 2; dy = -4 + rx
    if a == 'death':
        return ven_death(c, i, n)
    ven_body(c, dy, lean, glow, spread, stretch, t, fl, sx)


def ven_body(c, dy, lean, glow, spread, stretch, t, fl, sx=1.0, alpha=1.0):
    with c.at(0, dy - 14, lean, 1.45 * sx, 1.45):
        sw = math.sin(t * 6.283)
        # estelas de ventisca detras
        with c.part(ICE_D, line=0.4, bevel=1.6) as p:
            p.poly([(-4, 2), (-13 - 4 * stretch + sw, 6), (-22 - 8 * stretch, 11 + sw), (-14, 13), (-8, 16 + sw), (-3, 9)])
            p.poly([(-3, 7), (-10 + sw * 1.5, 14), (-17 - 5 * stretch, 21), (-8, 20), (-2, 14)])
        # manto-cristal en forma de gota rota
        with c.part(ICE, line=0.6, bevel=2.2) as p:
            p.poly([(0, -13), (5.6, -8), (7.6, -1), (5.2, 7), (2.4, 14 + sw), (0, 10), (-2.6, 15), (-5.6, 7.4), (-7.4, -1), (-5.2, -8)])
        with c.part(ICE_D, bevel=1.2) as p:
            p.poly([(0, -13), (-5.2, -8), (-7.4, -1), (-5.6, 7.4), (-2.6, 15), (0, 10), (-1, -2)])
        with c.part(CORE, bevel=1.6) as p:
            p.ell(0.8, -1.0, 2.6 + 1.2 * glow, 3.4 + 1.2 * glow)
        c.glow(0.8, -1, 8 + 8 * glow, '#7af0ff', 0.4 + 0.5 * glow)
        # corona de cristales
        with c.part(ICE, line=0.5, bevel=1.4) as p:
            for k, (ox, h, w) in enumerate([(-4, 6, 1.6), (-1.6, 9.5, 1.8), (1.6, 8.5, 1.8), (4.2, 5.4, 1.5)]):
                p.poly([(ox - w, -11), (ox + 0.4, -11 - h - 2 * glow), (ox + w, -11)])
        with c.part(DARK) as p:
            p.ell(2.6, -7.2, 1.0, 0.6); p.ell(-1.2, -7.0, 0.9, 0.55)
        with c.part(CORE) as p:
            p.ell(2.7, -7.2, 0.7, 0.4); p.ell(-1.1, -7.0, 0.6, 0.38)
        # brazos de cuchilla de hielo
        for sgn in (-1, 1):
            ax = sgn * (7 + 6 * spread) + 1
            ay = 0 - 3 * spread * 0.5
            with c.part(ICE, line=0.5, bevel=1.4) as p:
                p.poly([(sgn * 5, -3), (ax + sgn * 4, ay - 1.5), (ax + sgn * (9 + 4 * spread + 3 * stretch), ay + 5 + stretch * 2), (ax, ay + 2.6), (sgn * 5, 3)])
        if glow > 0.5:
            for k in range(8):
                aa = k * 0.785 + t * 6.283
                c.dotw(math.cos(aa) * (17 + 5 * glow), -26 + math.sin(aa) * (14 + 4 * glow) + dy, '#eaffff' if k % 2 else '#7af0ff')
    if fl:
        c.flash(WHITE, fl)


def ven_death(c, i, n):
    if i == 0:
        ven_body(c, -4, 0.3, 0, 0, 0, 0, 0.6)
        return
    u = i / (n - 1)
    items = []
    for k in range(7):
        ang = k * 0.9 + 0.2
        items.append(dict(fn=_bit_shard, x=math.cos(ang) * 4, y=-30 + math.sin(ang) * 6, r=1.5, vx=math.cos(ang) * 14, vy=-10 + math.sin(ang) * 10, spin=3 + k, rest=0.1 * k, bounce=0.3))
    b = Bits(items, seed=66, T=0.8, g=1.6)
    if u < 0.4:
        ven_body(c, -4 + 8 * u, 0.3, 1, 0, 0, u, 0.0)
        c.dissolve(min(1.0, u * 2.4), up=0.2, seed=5)
    draw_bits(c, b, u)
    for k in range(6):
        if u < 0.95:
            c.dotw(-8 + k * 3, -20 - u * 14 - 2 * k, '#eaffff' if k % 2 else '#7af0ff')
    c.glow(0, -28, 16 * (1 - u), '#7af0ff', 0.4 * (1 - u))


def _bit_shard(c):
    with c.part(ICE, line=0.4, bevel=1.2) as p:
        p.poly([(-4, 1), (0, -6), (3, 1), (0, 3)])


def sheet_ventisca():
    anims = [('idle', 6, 7, True, {}), ('walk', 6, 9, True, {}), ('windup', 4, 10, False, {}), ('attack', 5, 12, False, {'rel': 1}),
             ('windup2', 4, 10, False, {}), ('attack2', 4, 12, False, {}), ('hurt', 2, 10, False, {}), ('death', 9, 10, False, {})]
    return enemy_sheet('en_ventisca', (80, 72), (40, 52), (16, 36), ven_draw, (20, 40, 60), anims)


# ================================================================== CAPITAN DEL TRUENO
M_CAP = dict(skin=WHITEM, cloth=STEEL_BD, cloth_d=STEEL_BD, boot=STEEL_B, boot_d=STEEL_BD, vest=STEEL_B, vest_d=STEEL_BD)


def cap_head(c, x, y, ang, P):
    with c.at(x, y, ang):
        for sgn in (-1, 1):                                            # alas del casco
            with c.part(WHITEM, line=0.5, bevel=1.2) as p:
                bx = sgn * 4.6 - 0.5
                p.poly([(bx, -3.0), (bx + sgn * 2.2, -5.4), (bx + sgn * 5.5, -9.5), (bx + sgn * 3.4, -5.0), (bx + sgn * 6.4, -6.2), (bx + sgn * 3.8, -2.4)])
        with c.part(STEEL_B, line=0.5, bevel=1.8) as p:
            p.poly([(-5.0, 4.4), (-5.4, -2.6), (-2.4, -5.6), (3.0, -5.4), (5.2, -2.4), (5.0, 4.2), (1.0, 3.0), (-2.6, 3.6)])
        with c.part(DARK) as p:
            p.rect(-4.0, -0.8, 4.8, 1.2)
        with c.part(BOLT) as p:
            p.rect(-3.4, -0.4, 4.4, 0.8)
        c.glow(0.5, 0.2, 5, BOLTC, 0.4 + 0.5 * P['glow'])
        with c.part(GOLDB, bevel=0.8) as p:
            p.rect(-0.8, -5.6, 1.2, -1.4)


def cap_back(c, hip, neck, sho, lean, ph):
    sw = math.sin(ph * 6.283)
    with c.part(STEEL_BD, line=0.5, bevel=2.2) as p:
        p.poly([(neck[0] - 3.5, neck[1] - 1), (neck[0] + 1.5, neck[1] - 1), (hip[0] + 1, hip[1] + 7), (hip[0] - 6 + sw, hip[1] + 14), (hip[0] - 8, hip[1] + 11), (hip[0] - 12 + sw, hip[1] + 15), (neck[0] - 10, neck[1] + 4)])
    with c.part(BOLT) as p:
        p.limb((hip[0] - 7, hip[1] + 12), (hip[0] - 4, hip[1] + 5), 0.4); p.limb((hip[0] - 4, hip[1] + 5), (hip[0] - 6, hip[1] - 1), 0.4)


def cap_torso(c, P):
    with c.part(WHITEM, line=0.5, bevel=1.6) as p:                      # peto con rayo
        p.poly([(-4.0, -10.2), (4.2, -10.6), (4.8, -3), (0.2, -0.6), (-4.4, -3)])
    with c.part(BOLT) as p:
        p.poly([(0.8, -9.4), (-1.8, -5.6), (0.2, -5.2), (-1.0, -1.6), (2.4, -6.2), (0.4, -6.6)])
    c.glow(0, -5, 6, BOLTC, 0.2 + 0.4 * P['glow'])
    with c.part(STEEL_B, line=0.5, bevel=1.8) as p:
        p.poly([(-6.4, -10.6), (-1.0, -13.4), (4.8, -12.6), (6.4, -9.0), (-5.4, -7.6)])
    with c.part(GOLDB, bevel=0.7) as p:
        p.rect(-4.2, -2.0, 4.2, -0.8)


def cap_weapon(c, P, rear, front):
    gx, gy = rear
    ax = P['axa']
    d = (math.cos(ax), math.sin(ax)); nr = (-d[1], d[0])
    base = (gx - d[0] * 9, gy - d[1] * 9)
    tip0 = (gx + d[0] * 24, gy + d[1] * 24)
    with c.part(WOOD, line=0.5, bevel=0.9) as p:
        p.limb(base, tip0, 0.9)
    with c.part(GOLDB, bevel=0.8) as p:
        p.limb((tip0[0] - nr[0] * 2.8, tip0[1] - nr[1] * 2.8), (tip0[0] + nr[0] * 2.8, tip0[1] + nr[1] * 2.8), 0.7)
    with c.part(WHITEM, line=0.5, bevel=1.4) as p:
        p.poly([(tip0[0] + nr[0] * 2.2, tip0[1] + nr[1] * 2.2), (tip0[0] + d[0] * 11, tip0[1] + d[1] * 11), (tip0[0] - nr[0] * 2.2, tip0[1] - nr[1] * 2.2)])
    with c.part(BOLT) as p:
        p.limb(tip0, (tip0[0] + d[0] * 9, tip0[1] + d[1] * 9), 0.4 + 0.3 * P['glow'])
    c.glow(tip0[0] + d[0] * 8, tip0[1] + d[1] * 8, 6 + 8 * P['glow'], BOLTC, 0.3 + 0.55 * P['glow'])
    if P['glow'] > 0.4:
        for k in range(5):
            u = k * 0.22
            zx = tip0[0] + d[0] * (3 + k * 3.2) + nr[0] * (2.6 if k % 2 else -2.6)
            zy = tip0[1] + d[1] * (3 + k * 3.2) + nr[1] * (2.6 if k % 2 else -2.6)
            c.dotw(zx * 1.4, zy * 1.4, '#ffffff' if k % 2 else BOLTC)


def _bit_spear(c):
    with c.part(WOOD, line=0.4, bevel=0.9) as p:
        p.limb((-12, 0), (8, 0), 0.9)
    with c.part(WHITEM, line=0.4, bevel=1.0) as p:
        p.poly([(8, -2), (16, 0), (8, 2)])


def _bit_wing(c):
    with c.part(WHITEM, line=0.4, bevel=1.0) as p:
        p.poly([(-5, 2), (-3, -3), (4, -7), (1, -1), (5, 2)])


CAP = dict(M=M_CAP, head=cap_head, back=cap_back, torso=cap_torso, weapon=cap_weapon, sc=1.4, hip_h=13.5, carry=((6, -13), -1.15), sty1='cast', sty2='thrust',
           flash=BOLTC, bit_a=_bit_spear, bit_b=_bit_wing, seed=67, spark=(BOLTC, '#ffffff'))


def sheet_capitan_trueno():
    return enemy_sheet('en_capitan_trueno', (80, 72), (40, 70), (22, 54), draw_elite(CAP), (16, 30, 60),
                       _anims(5, 5, rel1=2, rel2=2, ifps=6, wfps=9, fa=12))


# ================================================================== SACERDOTE CARMESI
M_SAC = dict(skin=WHITEM, cloth=CRIM, cloth_d=CRIM_D, boot=CRIM_D, boot_d=CRIM_D, vest=CRIM, vest_d=CRIM_D)


def sac_head(c, x, y, ang, P):
    with c.at(x, y, ang):
        with c.part(CRIM_D, line=0.5, bevel=2.0) as p:                  # capucha
            p.poly([(-5.4, 5.4), (-6.2, -1.0), (-4.2, -5.0), (3.8, -5.0), (5.0, -1.6), (4.0, 2.0), (1.6, 5.4)])
        with c.part(Mat(ramp=['#000000', '#080204', '#10040a', '#1a060e', '#240812'], nooutline=True), bevel=0.6) as p:
            p.poly([(-2.6, 3.4), (-3.4, -0.6), (-1.6, -3.6), (2.8, -3.4), (4.0, -0.2), (3.0, 3.6)])
        with c.part(BLOODG) as p:
            p.ell(2.4, 0.0, 1.0 + 0.3 * P['glow'], 0.6); p.ell(-0.6, 0.0, 0.9, 0.55)
        c.glow(1, 0, 4.5, '#ff3a50', 0.4 + 0.5 * P['glow'])
        with c.part(GOLDB, line=0.5, bevel=1.4) as p:                   # mitra alta con ojo
            p.poly([(-4.4, -4.6), (-3.4, -10.0), (-0.6, -15.6 - 1.2 * P['glow']), (2.8, -10.0), (4.2, -4.6)])
        with c.part(CRIM, bevel=1.0) as p:
            p.poly([(-2.6, -5.6), (-1.6, -9.6), (-0.4, -12.2), (1.4, -9.6), (2.2, -5.6)])
        with c.part(BLOODG) as p:
            p.ell(-0.4, -9.0, 1.3 + 0.4 * P['glow'], 0.9)
        c.glow(-0.4, -9, 4, '#ff3a50', 0.35 + 0.4 * P['glow'])


def sac_back(c, hip, neck, sho, lean, ph):
    sw = math.sin(ph * 6.283)
    # corona de espinas/cuchillas tras la cabeza
    for k in range(7):
        aa = -2.9 + k * 0.45
        r0, r1 = 11, 19 + (k % 2) * 3
        with c.part(GOLDB, line=0.4, bevel=1.0) as p:
            p.poly([(neck[0] + 1 + math.cos(aa - 0.09) * r0, neck[1] - 4 + math.sin(aa - 0.09) * r0), (neck[0] + 1 + math.cos(aa) * r1, neck[1] - 4 + math.sin(aa) * r1),
                    (neck[0] + 1 + math.cos(aa + 0.09) * r0, neck[1] - 4 + math.sin(aa + 0.09) * r0)])
    with c.part(CRIM_D, line=0.5, bevel=2.2) as p:
        p.poly([(neck[0] - 3.5, neck[1] - 1), (neck[0] + 1.5, neck[1] - 1), (hip[0] + 1, hip[1] + 8), (hip[0] - 8 - lean * 4 + sw, hip[1] + 13.5), (neck[0] - 9, neck[1] + 4)])


def sac_torso(c, P):
    with c.part(CRIM, line=0.5, bevel=2.2) as p:
        p.poly([(-5, -1), (5, -1.4), (6.8, 6), (5.8, 11.2), (2, 9.6), (-1, 11.6), (-4, 9.8), (-6.8, 11.4), (-6.6, 5)])
    with c.part(GOLDB, bevel=0.7) as p:
        p.poly([(-1.4, -12), (1.6, -12), (2.0, 10.6), (-1.8, 10.8)])                       # estola
        p.poly([(-6.4, 10.2), (-4, 9.2), (-1, 10.8), (2, 9.2), (5.6, 10.4), (5.8, 11.4), (2, 10.2), (-1, 11.8), (-4, 10.4), (-6.8, 11.6)])
    with c.part(BLOODG) as p:
        p.ell(0.2, -5.0, 1.1); p.ell(0.2, 0.5, 0.9)
    with c.part(CRIM_D, line=0.4, bevel=1.6) as p:
        p.poly([(-5.8, -10.6), (-1.0, -13.4), (4.8, -12.4), (6.4, -8.6), (-5.6, -7.2)])


def sac_weapon(c, P, rear, front):
    gx, gy = rear
    ax = P['axa']
    d = (math.cos(ax), math.sin(ax)); nr = (-d[1], d[0])
    top = (gx + d[0] * 20, gy + d[1] * 20)
    with c.part(GOLDB, line=0.5, bevel=0.9) as p:
        p.limb((gx - d[0] * 8, gy - d[1] * 8), top, 0.9)
        p.limb((top[0] - nr[0] * 3, top[1] - nr[1] * 3), (top[0] + d[0] * 4 + nr[0] * 0, top[1] + d[1] * 4), 0.6)
        p.limb((top[0] + nr[0] * 3, top[1] + nr[1] * 3), (top[0] + d[0] * 4, top[1] + d[1] * 4), 0.6)
    orb = (top[0] + d[0] * 5, top[1] + d[1] * 5)
    r = 2.8 + 2.0 * P['glow']
    with c.part(BLOODG, bevel=1.6) as p:
        p.ell(orb[0], orb[1], r)
    c.glow(orb[0], orb[1], 8 + 8 * P['glow'], '#ff3a50', 0.4 + 0.5 * P['glow'])
    if P['glow'] > 0.4:
        for k in range(7):
            aa = k * 0.9 + P['ph'] * 6.283
            c.dotw((orb[0] + math.cos(aa) * 7.5) * 1.4, (orb[1] + math.sin(aa) * 7.5) * 1.4 + 2 * math.sin(aa * 2), '#ffc0c8' if k % 2 else '#d0203a')


def _bit_mitra(c):
    with c.part(GOLDB, line=0.4, bevel=1.2) as p:
        p.poly([(-4, 4), (-3, -2), (0, -8), (3, -2), (4, 4)])
    with c.part(BLOODG) as p:
        p.ell(0, -1, 1.2, 0.9)


def _bit_cup(c):
    with c.part(GOLDB, line=0.4, bevel=1.0) as p:
        p.limb((-9, 0), (7, 0), 0.9)
    with c.part(BLOODG) as p:
        p.ell(9, 0, 2.4)


SAC = dict(M=M_SAC, head=sac_head, back=sac_back, torso=sac_torso, weapon=sac_weapon, sc=1.4, hip_h=14, carry=((5, -14), -1.3), sty1='cast', sty2='cast',
           legs=(6.2, 6.2), stride=3.0, lift=1.6, flash='#ff3a50', bit_a=_bit_cup, bit_b=_bit_mitra, seed=68, spark=('#ff5a6c', '#ffc0c8'))


def sheet_sacerdote_carmesi():
    return enemy_sheet('en_sacerdote_carmesi', (80, 80), (40, 78), (20, 60), draw_elite(SAC), (50, 8, 16),
                       _anims(5, 5, rel1=2, rel2=2, ifps=6, wfps=8, fa=11))


# ================================================================== CENTURION DEL ECLIPSE
M_CEN = dict(skin=GOLDB, cloth=ECL_D, cloth_d=ECL_D, boot=GOLDB, boot_d=ECL_D, vest=ECL_B, vest_d=ECL_D)


def cen_head(c, x, y, ang, P):
    with c.at(x, y, ang):
        with c.part(GOLDB, line=0.5, bevel=1.8) as p:                    # cresta transversal
            p.poly([(-6.8, -5.4), (-5.4, -9.8), (-2.0, -10.8), (2.0, -10.8), (5.4, -9.8), (6.8, -5.4), (3.6, -6.4), (-3.6, -6.4)])
        with c.part(SUN) as p:
            p.limb((-5.4, -8.0), (5.4, -8.0), 0.55)
        with c.part(ECL_B, line=0.5, bevel=1.8) as p:
            p.poly([(-5.0, 4.6), (-5.4, -2.4), (-2.4, -5.8), (3.0, -5.6), (5.2, -2.4), (5.0, 4.4), (1.0, 3.0), (-2.6, 3.8)])
        with c.part(DARK) as p:
            p.poly([(-4.0, -1.4), (4.8, -1.4), (4.6, 1.4), (-3.6, 1.6)])
        with c.part(SUN) as p:
            p.rect(-3.0, -0.6, 4.2, 0.6)
        c.glow(0.6, 0, 5, SUNC, 0.35 + 0.5 * P['glow'])
        with c.part(GOLDB, bevel=0.8) as p:
            p.rect(-0.7, -5.6, 1.0, 3.4)


def cen_back(c, hip, neck, sho, lean, ph):
    # eclipse tras el torso: disco negro con corona dorada
    cx, cy = neck[0] - 2.5, neck[1] - 4
    c.glow(cx, cy, 20, SUNC, 0.4)
    with c.part(SUN) as p:
        p.ell(cx, cy, 9.6, 9.6)
    with c.part(Mat(ramp=['#000000', '#010102', '#020204', '#04040a', '#08081a'], nooutline=True), bevel=0.8) as p:
        p.ell(cx + 1.2, cy, 8.0, 8.0)
    sw = math.sin(ph * 6.283)
    with c.part(ECL_D, line=0.5, bevel=2.2) as p:
        p.poly([(neck[0] - 3.5, neck[1] - 1), (neck[0] + 1.5, neck[1] - 1), (hip[0] + 1, hip[1] + 7), (hip[0] - 6 + sw, hip[1] + 13), (hip[0] - 10, hip[1] + 12), (neck[0] - 10, neck[1] + 4)])


def cen_torso(c, P):
    with c.part(GOLDB, line=0.5, bevel=1.8) as p:
        p.poly([(-4.4, -10.4), (4.6, -10.8), (5.0, -3.2), (0.2, -0.4), (-4.6, -3.2)])
    with c.part(ECL_B, bevel=1.4) as p:
        p.ell(0.2, -6.0, 2.6)
    with c.part(SUN) as p:
        p.ell(0.2, -6.0, 1.3)
    c.glow(0.2, -6, 6, SUNC, 0.2 + 0.45 * P['glow'])
    with c.part(GOLDB, line=0.5, bevel=1.8) as p:
        p.poly([(-6.6, -10.6), (-1.0, -13.6), (5.0, -12.8), (6.6, -9.0), (-5.6, -7.6)])
        for k in range(3):
            p.rect(-5 + k * 3.4, -0.4, -3 + k * 3.4, 3.6)                               # faldellin de placas


def cen_weapon(c, P, rear, front):
    gx, gy = rear
    ax = P['axa']
    d = (math.cos(ax), math.sin(ax)); nr = (-d[1], d[0])
    base = (gx - d[0] * 6, gy - d[1] * 6)
    tip0 = (gx + d[0] * 21, gy + d[1] * 21)
    with c.part(ECL_B, line=0.5, bevel=0.9) as p:
        p.limb(base, tip0, 0.9)
    with c.part(GOLDB, line=0.5, bevel=1.4) as p:
        p.poly([(tip0[0] + nr[0] * 2.6, tip0[1] + nr[1] * 2.6), (tip0[0] + d[0] * 13, tip0[1] + d[1] * 13), (tip0[0] - nr[0] * 2.6, tip0[1] - nr[1] * 2.6)])
    with c.part(SUN) as p:
        p.limb((tip0[0] + d[0] * 2, tip0[1] + d[1] * 2), (tip0[0] + d[0] * 11, tip0[1] + d[1] * 11), 0.5)
    c.glow(tip0[0] + d[0] * 8, tip0[1] + d[1] * 8, 7 + 9 * P['glow'], SUNC, 0.3 + 0.6 * P['glow'])
    # escudo redondo con eclipse en la mano trasera
    sx0, sy0 = gx - 6, gy + 2
    with c.at(sx0, sy0, 0):
        with c.part(GOLDB, line=0.6, bevel=1.8) as p:
            p.ell(0, 0, 6.4, 7.4)
        with c.part(ECL_B, bevel=1.2) as p:
            p.ell(0.4, 0, 4.6, 5.4)
        with c.part(SUN) as p:
            p.ell(0.4, 0, 2.2 + 0.8 * P['glow'])
    if P['glow'] > 0.5:
        for k in range(6):
            aa = k * 1.047 + P['ph'] * 6.283
            c.dotw((tip0[0] + d[0] * 6 + math.cos(aa) * 7) * 1.4, (tip0[1] + d[1] * 6 + math.sin(aa) * 7) * 1.4, '#fff0a0' if k % 2 else SUNC)


def _bit_lance(c):
    with c.part(ECL_B, line=0.4, bevel=0.9) as p:
        p.limb((-12, 0), (8, 0), 0.9)
    with c.part(GOLDB, line=0.4, bevel=1.0) as p:
        p.poly([(8, -2.4), (18, 0), (8, 2.4)])


def _bit_crest(c):
    with c.part(GOLDB, line=0.4, bevel=1.4) as p:
        p.poly([(-6, 2), (-4, -3), (0, -4), (4, -3), (6, 2)])


CEN = dict(M=M_CEN, head=cen_head, back=cen_back, torso=cen_torso, weapon=cen_weapon, sc=1.4, hip_h=13.5, carry=((6, -13), -1.1), sty1='thrust', sty2='slam',
           flash=SUNC, bit_a=_bit_lance, bit_b=_bit_crest, seed=69, spark=(SUNC, '#fff0a0'))


def sheet_centurion_eclipse():
    return enemy_sheet('en_centurion_eclipse', (80, 72), (40, 70), (22, 54), draw_elite(CEN), (40, 30, 8),
                       _anims(5, 5, rel1=2, rel2=2, ifps=6, wfps=8, fa=12))


SHEETS = [sheet_ventisca, sheet_capitan_trueno, sheet_sacerdote_carmesi, sheet_centurion_eclipse]
