"""Elites unicos (lote A): caballero del osario, herrero infernal, segador del vacio, druida podrido.
Siluetas grandes (escala ~1.35), dos ataques propios cada uno: windup/attack y windup2/attack2."""
from common import *
from humanoid import human
from en_catacumbas import enemy_sheet, DARK, WHITE, BONE, BONE_B, SOUL
from en_nuevos_a import PLATE, PLATE_D, RUSTY, GOLDT, RUNE, SOOT, SOOT_D, SKIN_G, EMBER, ROBE_D, HOOD, hfeet

WOOD = Mat(ramp=['#140c0a', '#2a1a14', '#46301e', '#684a2c', '#8a6a42'], bevel=0.8, tex=0.3, seed=71)
CAPE = Mat(ramp=['#06100c', '#0e2018', '#1a3a2c', '#2c5a44'], bevel=2.0, tex=0.3, seed=72)
MOLTEN = Mat(ramp=['#c4300a', '#ff7a1a', '#ffc040', '#fff2b0', '#ffffff'], emi=True, nooutline=True, bevel=1.2, dith=0.2)
IRON = Mat(ramp=['#0c0a0c', '#1c181c', '#363036', '#584e58', '#847884'], bevel=1.6, tex=0.4, seed=73)
VOIDR = Mat(ramp=['#05020a', '#0e0618', '#1c0c34', '#32185a', '#52308a'], bevel=2.2, tex=0.3, seed=74)
VOIDR_D = Mat(ramp=['#030106', '#080410', '#120a22', '#201038', '#341c58'], bevel=2.2, tex=0.3, seed=75)
VOIDE = Mat(ramp=['#6a1ec8', '#a04cff', '#d8a0ff', '#ffffff'], emi=True, nooutline=True, bevel=1.2, dith=0.15)
MOSS = Mat(ramp=['#0c140a', '#1a2a12', '#2e4a1e', '#4e7230', '#7aa04c'], bevel=2.0, tex=0.5, seed=76)
MOSS_D = Mat(ramp=['#060a04', '#101a0a', '#1c2e12', '#304a1e', '#4a6e2e'], bevel=2.0, tex=0.5, seed=77)
BARK = Mat(ramp=['#0e0a06', '#201610', '#382a1c', '#584230', '#7c5e44'], bevel=1.4, tex=0.6, seed=78)
POIS = Mat(ramp=['#2a6a10', '#5ab81c', '#a8f040', '#eaff9a'], emi=True, nooutline=True, bevel=2.0, dith=0.15)
SHROOM = Mat(ramp=['#2a0a14', '#5a1a2a', '#8a2e40', '#c4506a', '#f09aae'], bevel=2.0, tex=0.2, seed=79)
SPOT = Mat(ramp=['#c8c0a0', '#f0e8c8', '#ffffff'], bevel=0.6)

FPS_NOTE = None


# ------------------------------------------------------------------ poses genericas de elite
def hold(grip, axa, lean, hx, glow=0.0, dy=0.0, head=0.0, feet=None):
    return dict(grip=grip, axa=axa, lean=lean, hx=hx, glow=glow, dy=dy, head=head, feet=feet)


STY = {
    # (windup final, [attack frames])
    'slam': (hold((3, -24), -1.45, -0.24, -7, 1, 1.6, -0.1, hfeet(1)),
             [hold((3, -24), -1.45, -0.24, -7, 1, 1.6), hold((8, -19), -0.8, 0.0, -4, 1, 2.2), hold((14, -9), 0.7, 0.34, 3, 1, 3.0),
              hold((13, -9), 0.8, 0.30, 2.5, 0.7, 2.6), hold((9, -13), 0.2, 0.1, -1, 0.0, 0.8)]),
    'thrust': (hold((-3, -15), 0.0, -0.22, -7, 1, 1.4, -0.1, hfeet(1)),
               [hold((-3, -15), 0.0, -0.22, -7, 1, 1.4), hold((4, -15), 0.0, 0.06, -3, 1, 2.0), hold((13, -15), 0.0, 0.34, 3, 1, 2.8),
                hold((14, -15), 0.0, 0.36, 4, 0.8, 2.8), hold((10, -15), 0.0, 0.2, 1, 0.0, 1.0)]),
    'cast': (hold((4, -21), -1.5, -0.1, -4, 1, 0.8, -0.12, hfeet(0.4)),
             [hold((4, -21), -1.5, -0.1, -4, 1, 0.8), hold((6, -22), -1.3, 0.0, -3, 1, 0.4), hold((9, -17), -0.7, 0.18, 0, 1, 1.8),
              hold((8, -17), -0.8, 0.14, 0, 0.6, 1.4), hold((5, -14), -1.4, 0.04, -2, 0.0, 0.4)]),
    'sweep': (hold((-5, -19), -2.5, -0.26, -7, 1, 1.4, -0.12, hfeet(1)),
              [hold((-5, -19), -2.5, -0.26, -7, 1, 1.4), hold((2, -21), -1.7, -0.05, -4, 1, 1.8), hold((12, -16), -0.1, 0.34, 3, 1, 2.6),
               hold((14, -12), 0.7, 0.36, 4, 0.7, 2.6), hold((9, -13), 0.1, 0.1, -1, 0.0, 0.8)]),
}


def epose(cfg, a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    cg, ca = cfg['carry']
    P = dict(hx=-3.0, dy=0.6 * s, lean=cfg.get('lean0', 0.02), ph=t, walk=False, stride=0, lift=0, grip=cg, axa=ca, head=0.0, flash=0.0, glow=0.0, cast=0.0, sway=s)
    if a == 'idle':
        P['grip'] = (cg[0], cg[1] + 0.5 * s)
    elif a == 'walk':
        P.update(walk=True, stride=cfg.get('stride', 4.0), lift=cfg.get('lift', 2.4), dy=-0.8 * abs(math.sin(2 * math.pi * t)) + 0.4, lean=cfg.get('lean0', 0.0) + 0.09, hx=-2)
        P['grip'] = (cg[0], cg[1] + 0.6 * s)
    elif a in ('windup', 'windup2', 'attack', 'attack2'):
        sty = cfg['sty1'] if a.endswith('2') is False else cfg['sty2']
        wfin, atk = STY[sty]
        if a.startswith('windup'):
            w = sm((i + 1) / n)
            P.update(lean=lerp(P['lean'], wfin['lean'], w), hx=lerp(-3, wfin['hx'], w), dy=lerp(0, wfin['dy'], w), glow=w, head=wfin['head'] * w, cast=w)
            P['grip'] = (lerp(cg[0], wfin['grip'][0], w), lerp(cg[1], wfin['grip'][1], w)); P['axa'] = lerp(ca, wfin['axa'], w)
            P['feet'] = wfin['feet']
        else:
            h = atk[min(i, 4)]
            P.update(lean=h['lean'], hx=h['hx'], dy=h['dy'], glow=h['glow'], cast=h['glow'], head=0.2 * (h['lean']))
            P['grip'] = h['grip']; P['axa'] = h['axa']
            P['feet'] = (-6, 0), (5 + 3 * h['glow'], 0)
    elif a == 'hurt':
        rx, ln, fl = hurt_state(i)
        P.update(hx=-3 + rx * 1.3, lean=ln, flash=fl, head=-0.3 if i == 0 else -0.1)
        P['grip'] = (cg[0] - 3, cg[1] + 2)
    return P


def draw_elite(cfg):
    def fn(c, a, i, n):
        if a == 'death':
            return death_elite(c, cfg, i, n)
        P = epose(cfg, a, i, n)
        with c.at(0, 0, 0, cfg['sc'], cfg['sc']):
            human(c, P, a, cfg['M'], cfg['head'], lambda cc, PP, r, f: None, back_fn=cfg.get('back'), torso_extra=cfg.get('torso'),
                  front_cb=cfg['weapon'], hip_h=cfg.get('hip_h', 13.5), torso_w=cfg.get('torso_w', 3.8), legs=cfg.get('legs', (6.6, 6.6)),
                  thick=cfg.get('thick', (2.0, 1.8)))
        if P['flash']:
            c.flash(WHITE, P['flash'])
        if a.startswith('windup') and i == n - 1:
            c.flash(cfg['flash'], 0.12)
    return fn


def death_elite(c, cfg, i, n):
    P0 = epose(cfg, 'hurt', 0, 2)
    if i == 0:
        with c.at(0, 0, 0, cfg['sc'], cfg['sc']):
            human(c, P0, 'hurt', cfg['M'], cfg['head'], lambda cc, PP, r, f: None, back_fn=cfg.get('back'), torso_extra=cfg.get('torso'), front_cb=cfg['weapon'],
                  hip_h=cfg.get('hip_h', 13.5), torso_w=cfg.get('torso_w', 3.8))
        c.flash(WHITE, 0.5)
        return
    u = i / (n - 1)
    P = epose(cfg, 'hurt', 1, 2)
    P['flash'] = 0; P['glow'] = 0
    ang = kf(u, [(0, 0), (0.3, -0.3), (0.65, -1.15), (1.0, -1.57)])
    P['feet'] = (kf(u, [(0, -3), (1, -7)]), 0), (kf(u, [(0, 3), (1, 6)]), 0)
    with c.at(3 + 4 * u, 0, ang):
        with c.at(0, 0, 0, cfg['sc'], cfg['sc']):
            human(c, P, 'idle', cfg['M'], cfg['head'], lambda cc, PP, r, f: None, back_fn=cfg.get('back'), torso_extra=cfg.get('torso'), hip_h=cfg.get('hip_h', 13.5),
                  torso_w=cfg.get('torso_w', 3.8))
    items = [dict(fn=cfg['bit_a'], x=12, y=-22, r=5, vx=7, vy=-6, spin=4, rest=1.4, bounce=0.3),
             dict(fn=cfg['bit_b'], x=-1, y=-38, r=3, vx=-4, vy=-9, spin=-5, rest=0.4, bounce=0.4)]
    if u > 0.4:
        items.append(dict(fn=cfg['bit_b'], x=-6, y=-24, r=2, vx=-7, vy=-6, spin=6, rest=0.1))
    for d_ in items:
        d_['vx'] *= 0.55; d_['vy'] *= 0.65
    b = Bits(items, seed=cfg['seed'], T=0.8, g=1.5)
    draw_bits(c, b, u)
    if u > 0.5:
        c.dissolve(min(1.0, (u - 0.5) * 1.7), up=0.3, seed=cfg['seed'] + 3)
    for k in range(7):
        if u < 0.95:
            c.dotw(-8 + k * 2.8 + math.sin(k * 3.1 + i) * 2, -22 - u * (16 + k * 3) - 2 * k, cfg['spark'][(k + i) % 2])
    if i == 1:
        c.glow(0, -20, 18, cfg['spark'][0], 0.35)


def _anims(atk1, atk2, hit1=None, box1=None, rel1=None, hit2=None, box2=None, rel2=None, idle=6, walk=8, ifps=7, wfps=9, wnd=4, fa=13):
    e1 = {}; e2 = {}
    for k, v in (('hit', hit1), ('box', box1), ('rel', rel1)):
        if v is not None: e1[k] = v
    for k, v in (('hit', hit2), ('box', box2), ('rel', rel2)):
        if v is not None: e2[k] = v
    return [('idle', idle, ifps, True, {}), ('walk', walk, wfps, True, {}), ('windup', wnd, 10, False, {}), ('attack', atk1, fa, False, e1),
            ('windup2', wnd, 10, False, {}), ('attack2', atk2, fa, False, e2), ('hurt', 2, 10, False, {}), ('death', 9, 10, False, {})]


# ================================================================== CABALLERO DEL OSARIO
M_CAB = dict(skin=BONE, cloth=PLATE_D, cloth_d=PLATE_D, boot=PLATE, boot_d=PLATE_D, vest=PLATE, vest_d=PLATE_D)


def cab_head(c, x, y, ang, P):
    with c.at(x, y, ang):
        with c.part(PLATE_D, line=0.5, bevel=1.4) as p:          # cuernos
            p.poly([(-3.4, -3.6), (-6.4, -7.0), (-7.6, -11.0), (-5.4, -8.6), (-2.6, -5.2)])
            p.poly([(2.6, -4.4), (4.6, -8.0), (4.2, -11.6), (3.2, -8.6), (1.2, -5.4)])
        with c.part(BONE, line=0.5, bevel=1.6) as p:
            p.ell(0.4, 0.4, 4.2, 4.0)
            p.poly([(-1.5, 2.8), (3.6, 2.6), (3.9, 4.8), (-0.5, 5.4), (-2.2, 3.8)])
        with c.part(DARK) as p:
            p.ell(2.8, 0.2, 1.2, 1.5); p.ell(0.2, 0.1, 1.1, 1.4)
        with c.part(RUNE) as p:
            p.ell(2.9, 0.2, 0.7 + 0.2 * P['glow'], 0.9); p.ell(0.3, 0.1, 0.6, 0.8)
        c.glow(2.8, 0.2, 3, SOUL, 0.35 + 0.5 * P['glow'])
        with c.part(PLATE, line=0.5, bevel=1.8) as p:             # yelmo de gran visera
            p.poly([(-5.4, 1.8), (-5.8, -3.8), (-2.6, -6.4), (3.2, -6.2), (5.4, -3.6), (5.0, -1.6), (2.4, -2.0), (-2.4, -2.0), (-3.4, 2.6)])
        with c.part(GOLDT, bevel=0.7) as p:
            p.limb((-5.4, -3.2), (5.0, -3.4), 0.5)
        with c.part(RUNE) as p:                                     # llama del penacho
            p.poly([(-1.6, -6.2), (-3.8, -9.5), (-1.0, -13.0 - 1.5 * P['glow']), (0.6, -10.0), (2.4, -14.5 - 1.0 * P['glow']), (3.0, -9.0), (1.6, -6.2)])
        c.glow(0, -11, 6, SOUL, 0.35)


def cab_back(c, hip, neck, sho, lean, ph):
    sw = math.sin(ph * 6.283)
    with c.part(CAPE, line=0.5, bevel=2.2) as p:                  # capa hecha jirones
        p.poly([(neck[0] - 3.5, neck[1] - 1), (neck[0] + 1.5, neck[1] - 1), (hip[0] + 1, hip[1] + 7),
                (hip[0] - 5 - lean * 4 + sw, hip[1] + 14), (hip[0] - 8 + sw * 1.4, hip[1] + 10.5), (hip[0] - 11, hip[1] + 13.5), (neck[0] - 10, neck[1] + 4)])


def cab_torso(c, P):
    with c.part(PLATE, line=0.6, bevel=2.0) as p:                 # hombrera grande con pinchos
        p.poly([(-6.4, -10.6), (-1.4, -13.4), (4.6, -12.8), (6.6, -9.0), (4.2, -7.4), (-5.4, -7.6)])
    with c.part(PLATE_D, bevel=1.0) as p:
        p.poly([(-5.8, -10.2), (-1.0, -12.8), (0.4, -9.6), (-4.8, -8.0)])
    with c.part(BONE, line=0.4, bevel=1.0) as p:
        p.poly([(-4.4, -12.4), (-3.2, -17.0), (-2.2, -12.9)]); p.poly([(1.0, -13.0), (2.4, -17.6), (3.4, -12.8)])
    with c.part(GOLDT, bevel=0.6) as p:
        p.rect(-4.0, -7.0, 4.2, -6.0); p.ell(0.2, -3.5, 1.4)
    with c.part(RUNE) as p:
        p.limb((0.2, -10.4), (0.2, -7.2), 0.4)


def cab_weapon(c, P, rear, front):
    gx, gy = rear
    ax = P['axa']
    d = (math.cos(ax), math.sin(ax)); nr = (-d[1], d[0])
    L = 25
    b0 = (gx + d[0] * 2, gy + d[1] * 2)
    b1 = (gx + d[0] * L, gy + d[1] * L)
    with c.part(PLATE_D, line=0.5, bevel=0.9) as p:
        p.limb((gx - d[0] * 4, gy - d[1] * 4), b0, 0.9)
        p.limb((b0[0] - nr[0] * 3.4, b0[1] - nr[1] * 3.4), (b0[0] + nr[0] * 3.4, b0[1] + nr[1] * 3.4), 0.8)
    with c.part(PLATE, line=0.5, bevel=1.4) as p:                  # mandoble
        p.poly([(b0[0] + nr[0] * 2.0, b0[1] + nr[1] * 2.0), (b1[0] + nr[0] * 1.3, b1[1] + nr[1] * 1.3), (b1[0] + d[0] * 3, b1[1] + d[1] * 3),
                (b1[0] - nr[0] * 1.3, b1[1] - nr[1] * 1.3), (b0[0] - nr[0] * 2.0, b0[1] - nr[1] * 2.0)])
    with c.part(RUNE) as p:
        p.limb((b0[0] + d[0] * 3, b0[1] + d[1] * 3), (b1[0] - d[0] * 2, b1[1] - d[1] * 2), 0.5)
    c.glow(b1[0], b1[1], 6 + 6 * P['glow'], SOUL, 0.25 + 0.5 * P['glow'])
    if P['glow'] > 0.9:
        for k in range(5):
            c.dotw((gx + d[0] * (6 + k * 4)) * 1.35, (gy + d[1] * (6 + k * 4)) * 1.35 - 1, '#e8fff0' if k % 2 else SOUL)
    # escudo de hueso en el brazo cercano
    with c.at(rear[0] - 7, rear[1] + 4, 0.1):
        pass


def _bit_sword(c):
    with c.part(PLATE, line=0.4, bevel=1.2) as p:
        p.limb((-12, 0), (12, 0), 1.6, 0.9)
    with c.part(RUNE) as p:
        p.limb((-9, 0), (10, 0), 0.4)


def _bit_horn(c):
    with c.part(BONE, line=0.4, bevel=1.2) as p:
        p.poly([(-4, 2), (0, -5), (3, 2)])


CAB = dict(M=M_CAB, head=cab_head, back=cab_back, torso=cab_torso, weapon=cab_weapon, sc=1.4, hip_h=13.5, carry=((6, -13), 0.9), sty1='slam', sty2='thrust',
           flash=SOUL, bit_a=_bit_sword, bit_b=_bit_horn, seed=61, spark=(SOUL, '#d8ffe8'))


def sheet_caballero_osario():
    return enemy_sheet('en_caballero_osario', (80, 72), (40, 70), (22, 54), draw_elite(CAB), (16, 24, 22),
                       _anims(5, 5, hit1=[2, 3], box1=[6, -52, 40, 52], rel1=2, rel2=2, ifps=6, wfps=8, fa=12))


# ================================================================== HERRERO INFERNAL
M_HER = dict(skin=SKIN_G, cloth=SOOT_D, cloth_d=SOOT_D, boot=IRON, boot_d=IRON, vest=SOOT, vest_d=SOOT_D)


def her_head(c, x, y, ang, P):
    with c.at(x, y, ang):
        with c.part(SKIN_G, line=0.5, bevel=1.6) as p:
            p.ell(0.3, 0.6, 4.4, 4.2)
        with c.part(DARK, line=0.4, bevel=1.0) as p:                  # barba de hollin
            p.poly([(-2.6, 1.4), (3.8, 1.6), (3.0, 6.0), (0.4, 7.8), (-2.4, 5.6)])
        with c.part(IRON, line=0.5, bevel=1.4) as p:                  # media mascara
            p.poly([(-4.6, -1.4), (4.8, -1.8), (5.2, 1.0), (1.0, 2.2), (-4.2, 1.8)])
        with c.part(MOLTEN) as p:                                     # lentes
            p.ell(3.0, -0.3, 1.4 + 0.3 * P['glow'], 1.1); p.ell(-0.6, -0.2, 1.3 + 0.3 * P['glow'], 1.0)
        c.glow(1.6, -0.3, 4.5, FIRE, 0.4 + 0.5 * P['glow'])
        with c.part(IRON, line=0.5, bevel=1.6) as p:                  # casco con cuernos romos
            p.poly([(-4.8, -1.2), (-5.4, -4.4), (-3.0, -6.4), (2.6, -6.4), (5.0, -4.2), (4.6, -1.6)])
            p.poly([(-4.6, -4.4), (-8.0, -6.4), (-8.8, -9.6), (-6.2, -8.0), (-3.4, -5.6)])
        with c.part(RUSTY, bevel=0.8) as p:
            p.limb((-5.0, -3.4), (4.8, -3.6), 0.5)


FIRE = '#FF8A1A'


def her_back(c, hip, neck, sho, lean, ph):
    with c.part(IRON, line=0.5, bevel=1.8) as p:                      # mochila-horno
        p.poly([(neck[0] - 7.5, neck[1] + 1), (neck[0] - 2, neck[1] - 2), (hip[0] - 1, hip[1] + 4), (hip[0] - 7.5 - lean * 3, hip[1] + 3)])
    with c.part(IRON, line=0.4, bevel=1.0) as p:
        p.rect(neck[0] - 6.8, neck[1] - 7.5, neck[0] - 4.4, neck[1] + 0.5)                     # chimenea
    with c.part(MOLTEN) as p:
        p.ell(neck[0] - 5.6, neck[1] - 8.2, 1.8, 1.2)
    c.glow(neck[0] - 5.6, neck[1] - 8.4, 6, FIRE, 0.55)
    c.dotw((neck[0] - 5.6) * 1.35 + math.sin(ph * 6.283) * 2, (neck[1] - 11 - 6 * ((ph * 2) % 1)) * 1.35, '#ffb040')
    c.dotw((neck[0] - 4.6) * 1.35 - math.sin(ph * 6.283) * 2, (neck[1] - 14 - 6 * ((ph * 2 + 0.5) % 1)) * 1.35, '#ff6a14')


def her_torso(c, P):
    with c.part(CANVAS_L, line=0.5, bevel=1.8) as p:                  # delantal de cuero
        p.poly([(-4.6, -9.0), (4.2, -9.2), (5.4, 1.0), (4.0, 6.2), (-3.6, 6.4), (-5.2, 0.5)])
    with c.part(IRON, line=0.5, bevel=1.6) as p:                      # hombreras
        p.poly([(-6.8, -10.6), (-1.0, -13.2), (4.4, -12.4), (6.0, -9.4), (-5.8, -7.8)])
    with c.part(MOLTEN) as p:
        p.limb((-2.2, -6.0), (-0.6, -1.0), 0.45); p.limb((-0.6, -1.0), (1.8, 0.6), 0.4); p.ell(2.4, -5.6, 0.8)
    c.glow(0, -3, 6, FIRE, 0.15 + 0.4 * P['glow'])
    with c.part(RUSTY, bevel=0.8) as p:
        p.limb((-4.8, -8.4), (4.4, 2.4), 0.6)                         # cadena cruzada


CANVAS_L = Mat(ramp=['#120a08', '#2a1a12', '#46301e', '#684a2c'], bevel=2.0, tex=0.5, seed=80)


def her_weapon(c, P, rear, front):
    gx, gy = rear
    ax = P['axa']
    d = (math.cos(ax), math.sin(ax)); nr = (-d[1], d[0])
    h1 = (gx + d[0] * 17, gy + d[1] * 17)
    with c.part(WOOD, line=0.5, bevel=0.9) as p:
        p.limb((gx - d[0] * 5, gy - d[1] * 5), h1, 1.1)
    hc = (h1[0] + d[0] * 4.5, h1[1] + d[1] * 4.5)
    with c.part(IRON, line=0.6, bevel=1.8) as p:                      # cabeza del martillo, bloque enorme
        pts = [(-5.2, -6.6), (5.4, -6.6), (5.4, 6.6), (-5.2, 6.6)]
        p.poly([(hc[0] + d[0] * u + nr[0] * v, hc[1] + d[1] * u + nr[1] * v) for (u, v) in [(-4.5, -6.4), (4.5, -6.4), (4.5, 6.4), (-4.5, 6.4)]])
    with c.part(MOLTEN) as p:                                         # grietas de metal fundido
        p.limb((hc[0] - nr[0] * 4, hc[1] - nr[1] * 4), (hc[0] + nr[0] * 1, hc[1] + nr[1] * 1), 0.5 + 0.3 * P['glow'])
        p.limb((hc[0] + nr[0] * 1, hc[1] + nr[1] * 1), (hc[0] + d[0] * 3 + nr[0] * 5, hc[1] + d[1] * 3 + nr[1] * 5), 0.45 + 0.3 * P['glow'])
    c.glow(hc[0], hc[1], 8 + 8 * P['glow'], FIRE, 0.25 + 0.55 * P['glow'])
    with c.part(RUSTY, bevel=0.8) as p:
        p.limb((hc[0] - d[0] * 5.2 - nr[0] * 6.4, hc[1] - d[1] * 5.2 - nr[1] * 6.4), (hc[0] - d[0] * 5.2 + nr[0] * 6.4, hc[1] - d[1] * 5.2 + nr[1] * 6.4), 0.9)
    if P['glow'] > 0.9:
        for k in range(6):
            c.dotw((hc[0] + math.cos(k * 1.05) * 7) * 1.35, (hc[1] + math.sin(k * 1.05) * 7) * 1.35, '#ffd070' if k % 2 else '#ff7a1a')


def _bit_hammer(c):
    with c.part(IRON, line=0.5, bevel=1.4) as p:
        p.rect(-5, -6, 5, 6)
    with c.part(MOLTEN) as p:
        p.limb((-4, -3), (3, 2), 0.7)


def _bit_goggle(c):
    with c.part(IRON, line=0.4, bevel=1.0) as p:
        p.ell(0, 0, 3.4, 2.4)
    with c.part(MOLTEN) as p:
        p.ell(0, 0, 1.6, 1.2)


HER = dict(M=M_HER, head=her_head, back=her_back, torso=her_torso, weapon=her_weapon, sc=1.45, hip_h=12.5, torso_w=4.8, carry=((6, -12), 0.5), sty1='cast', sty2='slam',
           thick=(2.6, 2.3), stride=3.4, lift=2.0, flash=FIRE, bit_a=_bit_hammer, bit_b=_bit_goggle, seed=62, spark=('#ffb040', '#ff6a14'))


def sheet_herrero_infernal():
    return enemy_sheet('en_herrero_infernal', (80, 72), (40, 70), (24, 54), draw_elite(HER), (30, 18, 12),
                       _anims(5, 5, rel1=2, hit2=[2, 3], box2=[6, -50, 44, 50], rel2=2, ifps=6, wfps=7, fa=11))


# ================================================================== SEGADOR DEL VACIO
M_SEG = dict(skin=VOIDR_D, cloth=VOIDR, cloth_d=VOIDR_D, boot=VOIDR_D, boot_d=VOIDR_D, vest=VOIDR, vest_d=VOIDR_D)


def seg_head(c, x, y, ang, P):
    with c.at(x, y, ang):
        with c.part(VOIDR_D, line=0.5, bevel=2.2) as p:               # capucha alta y puntiaguda
            p.poly([(-5.4, 5.6), (-6.4, -1.0), (-4.4, -6.4), (-0.6, -12.0 - 1.0 * P['glow']), (2.6, -6.4), (5.0, -3.0), (4.6, 1.0), (2.4, 2.4), (1.4, 6.0)])
        with c.part(Mat(ramp=['#000000', '#010002', '#020104', '#040208', '#06030c'], nooutline=True), bevel=0.6) as p:
            p.poly([(-2.6, 3.2), (-3.6, -1.0), (-1.8, -4.4), (2.6, -4.0), (4.2, -0.6), (3.0, 3.4)])
        with c.part(VOIDE) as p:
            p.ell(2.6, -0.5, 1.2 + 0.4 * P['glow'], 0.55); p.ell(-0.4, -0.5, 1.1 + 0.4 * P['glow'], 0.5)
        c.glow(1.2, -0.5, 5, '#b04cff', 0.45 + 0.5 * P['glow'])


def seg_back(c, hip, neck, sho, lean, ph):
    sw = math.sin(ph * 6.283)
    for k, (ox, h) in enumerate([(-4, 20), (-8, 17), (-12, 14)]):
        with c.part(VOIDR_D, line=0.4, bevel=1.4) as p:               # tiras de vacio flotando
            p.poly([(neck[0] - 3 - k, neck[1] + 1), (neck[0] + ox + sw * (1 + k), neck[1] + 5 + 2 * k), (neck[0] + ox - 4 + sw * (1.5 + k), neck[1] + 12 + h * 0.4),
                    (neck[0] + ox + 1, neck[1] + 8 + h * 0.5), (neck[0] - 1 - k, neck[1] + 3)])


def seg_torso(c, P):
    # tunica larga hasta el suelo: esconde las piernas, el segador flota
    with c.part(VOIDR, line=0.5, bevel=2.4) as p:
        p.poly([(-5.0, -1), (5.4, -1.4), (7.4, 8), (6.6, 14.4), (4.2, 12.6), (2.4, 15.4), (-0.6, 12.6), (-3.0, 15.0), (-5.2, 12.4), (-7.4, 14.2), (-7.0, 7)])
    with c.part(VOIDR_D, bevel=1.6) as p:
        p.poly([(-5.0, -1), (-1.0, -1.2), (-1.4, 13.0), (-3.0, 15.0), (-5.2, 12.4), (-7.4, 14.2), (-7.0, 7)])
    with c.part(VOIDE) as p:
        p.limb((-0.4, -9.0), (-0.4, 9.0), 0.35)
        for k in range(3):
            p.ell(-0.4, -6 + k * 5, 0.8)
    c.glow(-0.4, 0, 10, '#8a2cff', 0.12 + 0.3 * P['glow'])
    with c.part(VOIDR_D, line=0.4, bevel=1.6) as p:
        p.poly([(-5.8, -10.6), (-1.0, -13.4), (4.8, -12.4), (6.4, -8.6), (-5.6, -7.2)])    # esclavina


def seg_weapon(c, P, rear, front):
    gx, gy = rear
    ax = P['axa']
    d = (math.cos(ax), math.sin(ax)); nr = (-d[1], d[0])
    top = (gx + d[0] * 21, gy + d[1] * 21)
    with c.part(WOOD, line=0.5, bevel=0.9) as p:
        p.limb((gx - d[0] * 8, gy - d[1] * 8), top, 0.9)
    # hoja de guadana: curva enorme
    pts = []
    for k in range(9):
        u = k / 8
        a2 = -0.3 + u * 2.2
        r = 15 - 2 * u
        pts.append((top[0] + d[0] * (math.sin(a2) * r * 0.2) + nr[0] * (-math.cos(a2) * r + 7), top[1] + d[1] * (math.sin(a2) * r * 0.2) + nr[1] * (-math.cos(a2) * r + 7)))
    # construccion simple y robusta: hoja como arco de rombos
    tip = (top[0] + nr[0] * 17 + d[0] * 4, top[1] + nr[1] * 17 + d[1] * 4)
    mid = (top[0] + nr[0] * 9 + d[0] * 8.5, top[1] + nr[1] * 9 + d[1] * 8.5)
    mid2 = (top[0] + nr[0] * 9 + d[0] * 5.5, top[1] + nr[1] * 9 + d[1] * 5.5)
    with c.part(PLATE, line=0.5, bevel=1.4) as p:
        p.poly([(top[0] - nr[0] * 1.5, top[1] - nr[1] * 1.5), mid, tip, mid2, (top[0] + nr[0] * 1.5, top[1] + nr[1] * 1.5)])
    with c.part(VOIDE) as p:
        p.limb(mid2, tip, 0.45)
    c.glow(tip[0], tip[1], 6 + 6 * P['glow'], '#b04cff', 0.3 + 0.5 * P['glow'])
    c.glow(mid[0], mid[1], 5, '#b04cff', 0.2)


def _bit_scythe(c):
    with c.part(WOOD, line=0.4, bevel=0.9) as p:
        p.limb((-10, 0), (10, 0), 0.9)
    with c.part(PLATE, line=0.4, bevel=1.2) as p:
        p.poly([(8, -1), (14, 5), (16, 9), (10, 3)])


def _bit_hood(c):
    with c.part(VOIDR_D, line=0.4, bevel=1.6) as p:
        p.poly([(-4, 4), (-5, -1), (0, -7), (4, 0), (3, 4)])
    with c.part(VOIDE) as p:
        p.ell(1, -1, 0.8, 0.5)


SEG = dict(M=M_SEG, head=seg_head, back=seg_back, torso=seg_torso, weapon=seg_weapon, sc=1.4, hip_h=15.5, carry=((5, -15), -1.25), sty1='sweep', sty2='cast', lean0=0.0,
           legs=(6.0, 6.0), stride=2.4, lift=1.2, flash='#b04cff', bit_a=_bit_scythe, bit_b=_bit_hood, seed=63, spark=('#b04cff', '#e8c8ff'))


def sheet_segador_vacio():
    return enemy_sheet('en_segador_vacio', (80, 80), (40, 78), (20, 62), draw_elite(SEG), (24, 8, 40),
                       _anims(5, 5, hit1=[2, 3], box1=[-6, -60, 64, 64], rel1=2, rel2=2, ifps=6, wfps=8, fa=12))


# ================================================================== DRUIDA PODRIDO
M_DRU = dict(skin=MOSS, cloth=BARK, cloth_d=MOSS_D, boot=BARK, boot_d=MOSS_D, vest=MOSS, vest_d=MOSS_D)


def dru_head(c, x, y, ang, P):
    with c.at(x, y, ang):
        for sgn, bx in ((1, 2.0), (-1, -2.6)):                        # astas ramificadas
            with c.part(BARK, line=0.4, bevel=1.0) as p:
                p.limb((bx, -3.4), (bx + 1.8 * sgn + 0.5, -9.0), 0.8, 0.5)
                p.limb((bx + 1.8 * sgn + 0.5, -9.0), (bx + 4.4 * sgn, -13.0), 0.5, 0.3)
                p.limb((bx + 0.8, -6.2), (bx - 3.2 * sgn + 1, -10.0), 0.45, 0.28)
                p.limb((bx + 1.8 * sgn + 0.5, -9.0), (bx - 1.0 * sgn, -14.0), 0.4, 0.25)
        with c.part(BONE, line=0.5, bevel=1.6) as p:                  # craneo de ciervo
            p.ell(0.6, 0.2, 4.0, 3.6)
            p.poly([(1.5, 1.4), (7.4, 2.4), (7.2, 4.2), (2.4, 4.4)])
        with c.part(DARK) as p:
            p.ell(2.4, -0.2, 1.1, 1.3); p.ell(-0.6, -0.1, 1.0, 1.2)
        with c.part(POIS) as p:
            p.ell(2.5, -0.2, 0.65 + 0.2 * P['glow'], 0.8); p.ell(-0.5, -0.1, 0.6, 0.75)
        c.glow(1, -0.2, 3.5, '#8aff40', 0.35 + 0.5 * P['glow'])
        with c.part(MOSS, line=0.4, bevel=1.4) as p:
            p.poly([(-3.6, -2.4), (0, -4.2), (3.4, -3.0), (2.0, -1.6), (-1.0, -2.0), (-3.2, 0.2)])


def dru_back(c, hip, neck, sho, lean, ph):
    with c.part(MOSS_D, line=0.5, bevel=2.2) as p:                    # joroba cubierta de musgo
        p.poly([(neck[0] - 7.5, neck[1] + 7), (neck[0] - 7, neck[1] - 2), (neck[0] - 2, neck[1] - 4.4), (neck[0] + 1.0, neck[1] + 1), (hip[0] - 0.5, hip[1] + 3)])
    for k, (ox, oy, r) in enumerate([(-7, 1, 2.8), (-4, -3.4, 2.2), (-8, 6, 2.0)]):
        with c.part(SHROOM, line=0.4, bevel=1.4) as p:
            p.ell(neck[0] + ox, neck[1] + oy - 1, r, r * 0.7)
        with c.part(SPOT) as p:
            p.ell(neck[0] + ox - 0.5, neck[1] + oy - 1.4, 0.5)
        with c.part(BONE, bevel=0.5) as p:
            p.limb((neck[0] + ox, neck[1] + oy - 0.5), (neck[0] + ox, neck[1] + oy + 1.4), 0.6)


def dru_torso(c, P):
    with c.part(MOSS_D, line=0.5, bevel=2.0) as p:
        p.poly([(-5.2, -1), (5.0, -1.4), (6.4, 6), (4.0, 9.6), (1.6, 7.6), (-0.6, 10.2), (-3.0, 7.8), (-5.8, 9.4), (-6.2, 5)])  # faldon de hojas
    with c.part(MOSS, bevel=1.2) as p:
        for k in range(5):
            p.poly([(-5 + k * 2.4, 6.5), (-3.6 + k * 2.4, 10.4), (-2.4 + k * 2.4, 6.5)])
    with c.part(BARK, line=0.4, bevel=1.0) as p:
        p.limb((-4.4, -9.6), (4.0, -1.2), 0.7); p.limb((4.0, -9.0), (-3.6, -1.0), 0.6)     # raices cruzadas
    with c.part(POIS) as p:
        p.ell(0.2, -5.4, 1.4 + 0.5 * P['glow'], 1.4 + 0.5 * P['glow'])
    c.glow(0.2, -5.4, 6, '#8aff40', 0.25 + 0.4 * P['glow'])
    with c.part(MOSS, line=0.4, bevel=1.6) as p:
        p.poly([(-6.2, -10.4), (-1.0, -13.2), (4.6, -12.2), (6.0, -8.8), (-5.4, -7.4)])


def dru_weapon(c, P, rear, front):
    gx, gy = rear
    ax = P['axa']
    d = (math.cos(ax), math.sin(ax)); nr = (-d[1], d[0])
    top = (gx + d[0] * 20, gy + d[1] * 20)
    with c.part(BARK, line=0.5, bevel=0.9) as p:
        p.limb((gx - d[0] * 7, gy - d[1] * 7), top, 1.0, 1.3)
        p.limb(top, (top[0] + nr[0] * 5 + d[0] * 5, top[1] + nr[1] * 5 + d[1] * 5), 0.9, 0.5)       # garras de raiz
        p.limb(top, (top[0] - nr[0] * 5 + d[0] * 5, top[1] - nr[1] * 5 + d[1] * 5), 0.9, 0.5)
        p.limb(top, (top[0] + d[0] * 6, top[1] + d[1] * 6), 0.8, 0.45)
    orb = (top[0] + d[0] * 3, top[1] + d[1] * 3)
    r = 2.6 + 1.8 * P['glow']
    with c.part(POIS, bevel=1.4) as p:
        p.ell(orb[0], orb[1], r)
    c.glow(orb[0], orb[1], 7 + 8 * P['glow'], '#8aff40', 0.4 + 0.5 * P['glow'])
    if P['glow'] > 0.5:
        for k in range(6):
            aa = k * 1.047 + P['ph'] * 6.283
            c.dotw((orb[0] + math.cos(aa) * 7) * 1.4, (orb[1] + math.sin(aa) * 7) * 1.4, '#eaff9a' if k % 2 else '#5ab81c')


def _bit_staff(c):
    with c.part(BARK, line=0.4, bevel=0.9) as p:
        p.limb((-10, 0), (10, 0), 1.0)
    with c.part(POIS, bevel=1.4) as p:
        p.ell(12, 0, 2.2)


def _bit_antler(c):
    with c.part(BONE, line=0.4, bevel=1.0) as p:
        p.limb((-5, 3), (0, -2), 0.8, 0.5); p.limb((0, -2), (4, -7), 0.5, 0.3); p.limb((-1, 0), (-5, -5), 0.4, 0.3)


DRU = dict(M=M_DRU, head=dru_head, back=dru_back, torso=dru_torso, weapon=dru_weapon, sc=1.35, hip_h=12.5, carry=((6, -12), -1.2), sty1='cast', sty2='cast', lean0=0.22,
           stride=3.2, lift=1.8, flash='#8aff40', bit_a=_bit_staff, bit_b=_bit_antler, seed=64, spark=('#8aff40', '#eaff9a'))


def sheet_druida_podrido():
    return enemy_sheet('en_druida_podrido', (80, 72), (40, 70), (22, 52), draw_elite(DRU), (20, 30, 12),
                       _anims(5, 5, rel1=2, rel2=2, ifps=6, wfps=7, fa=11))


SHEETS = [sheet_caballero_osario, sheet_herrero_infernal, sheet_segador_vacio, sheet_druida_podrido]
