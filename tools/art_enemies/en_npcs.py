"""NPC de las mazmorras (props): Aldren (guardian herido), Vesper (mercader enmascarado), Sylwen (espiritu del bosque)."""
from common import *
from humanoid import human
from en_catacumbas import enemy_sheet, DARK, WHITE
from en_nuevos_a import PLATE, PLATE_D, GOLDT, RUSTY, ROBE_D, LANT, CANVAS
from en_elites_a import WOOD, MOSS, MOSS_D, POIS, BARK
from en_elites_b import WHITEM

CREAM = Mat(ramp=['#2a2218', '#5a4a34', '#8a7456', '#b8a07a', '#e0cca4'], bevel=1.6, tex=0.3, seed=111)
SKINN = Mat(ramp=['#2a1810', '#5a3422', '#8a5a38', '#b88858', '#e0b484'], bevel=1.4, seed=112)
CLOAKV = Mat(ramp=['#0a0a14', '#161628', '#26264a', '#3c3c6e', '#58589a'], bevel=2.0, tex=0.3, seed=113)
CLOAKV_D = Mat(ramp=['#05050a', '#0c0c18', '#16162c', '#242444', '#363666'], bevel=2.0, tex=0.3, seed=114)
MASK = Mat(ramp=['#8a8070', '#c4baa4', '#e8e0cc', '#ffffff'], bevel=1.6, seed=115)
SPIRIT = Mat(ramp=['#1c6a48', '#3cc084', '#9af0c4', '#eafff4'], emi=True, nooutline=True, bevel=2.0, dith=0.25)
SPIRIT_D = Mat(ramp=['#0e3a2a', '#1e7a58', '#4cc490', '#9af0c4'], emi=True, nooutline=True, bevel=2.0, dith=0.3)


# ---------------------------------------------------------------- Aldren: guardian herido, apoyado en su espada
def aldren(c, a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(hx=-2.0, dy=3.0 + 0.5 * s, lean=0.28, ph=t, walk=False, stride=0, lift=0, rear=(9, -7), front=(8, -6), head=0.25, glow=0)
    P['feet'] = ((-5.5, 0), (4.0, 0))

    def head(c, x, y, ang, P):
        with c.at(x, y + 1, ang):
            with c.part(SKINN, line=0.5, bevel=1.4) as p:
                p.ell(0.4, 0.4, 3.4, 3.4)
            with c.part(CREAM, bevel=1.0) as p:
                p.poly([(-3.6, 0), (-3.0, -3.2), (1.0, -4.0), (3.8, -2.4), (3.0, -1.4), (-1.0, -2.0), (-2.6, 1.6)])   # pelo/venda
            with c.part(DARK) as p:
                p.ell(1.8, 0.8, 0.5, 0.5)
            with c.part(RUSTY, bevel=0.5) as p:
                p.limb((-3.2, -1.6), (3.4, -2.0), 0.6)

    def weapon(c, P, rear, front):
        gx, gy = rear[0], rear[1]
        with c.part(PLATE, line=0.4, bevel=1.2) as p:           # espada clavada, empunadura arriba
            p.poly([(gx - 1.0, gy), (gx + 1.0, gy), (gx + 1.2, gy + 12), (gx, gy + 14), (gx - 1.2, gy + 12)])
        with c.part(GOLDT, bevel=0.6) as p:
            p.limb((gx - 3.4, gy - 0.6), (gx + 3.4, gy - 0.6), 0.7)

    def torso(c, P):
        with c.part(WHITEM, line=0.5, bevel=1.8) as p:
            p.poly([(-4.4, -10.4), (4.6, -10.8), (5.0, -3), (0.4, -0.6), (-4.6, -3)])
        with c.part(GOLDT, bevel=0.6) as p:
            p.rect(-0.8, -9.6, 0.8, -1.4); p.rect(-3.0, -7, 3.0, -5.8)
        with c.part(Mat(ramp=['#5a0a14', '#a01428', '#d8283c', '#ff6070'], nooutline=True), bevel=0.8) as p:   # herida
            p.ell(2.6, -2.4, 1.6, 1.2)

    def back(c, hip, neck, sho, lean, ph):
        with c.part(CREAM, line=0.5, bevel=2.0) as p:
            p.poly([(neck[0] - 3.5, neck[1] - 1), (neck[0] + 1.5, neck[1] - 1), (hip[0] + 1, hip[1] + 7), (hip[0] - 7, hip[1] + 11), (neck[0] - 9, neck[1] + 4)])

    M = dict(skin=SKINN, cloth=PLATE_D, cloth_d=PLATE_D, boot=PLATE, boot_d=PLATE_D, vest=PLATE, vest_d=PLATE_D)
    with c.at(0, 0, 0, 1.15, 1.15):
        human(c, P, 'idle', M, head, lambda cc, PP, r, f: None, back_fn=back, torso_extra=torso, front_cb=weapon, hip_h=9)
    for k in range(3):
        c.dotw(-3 + k * 4, -34 - ((t * 20 + k * 6) % 12), '#ff8090') if False else None


# ---------------------------------------------------------------- Vesper: mercader enmascarado con mochila y farol
def vesper(c, a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    P = dict(hx=-2.0, dy=0.5 * s, lean=0.06 + 0.02 * s, ph=t, walk=False, stride=0, lift=0, rear=(6, -11), front=(7, -10 + s), head=0.0, glow=0)

    def head(c, x, y, ang, P):
        with c.at(x, y, ang):
            with c.part(CLOAKV_D, line=0.5, bevel=2.0) as p:
                p.poly([(-5.2, 5.6), (-6.0, -1.0), (-3.8, -5.2), (1.0, -6.4), (4.6, -4.2), (4.2, 1.8), (1.4, 5.6)])
            with c.part(MASK, line=0.5, bevel=1.6) as p:
                p.poly([(-2.4, 3.2), (-3.2, -1.2), (-1.0, -3.6), (2.8, -3.4), (4.0, -0.4), (3.0, 3.4), (0.4, 4.6)])
            with c.part(DARK) as p:
                p.poly([(0.6, -1.4), (3.0, -1.2), (3.0, -0.2), (0.6, -0.4)]); p.ell(-0.8, -0.6, 0.6, 0.5)
            with c.part(Mat(ramp=['#8a1a1a', '#c82828', '#ff5a4a'], nooutline=True), bevel=0.6) as p:
                p.limb((0.8, 2.0), (2.6, 2.2), 0.4)

    def weapon(c, P, rear, front):
        fx, fy = front
        with c.part(WOOD, bevel=0.6) as p:
            p.limb((fx, fy), (fx + 1, fy + 5), 0.5)
        with c.part(LANT, bevel=1.2) as p:
            p.ell(fx + 1, fy + 7, 2.2, 2.6)
        c.glow(fx + 1, fy + 7, 7, '#FFC060', 0.55)

    def torso(c, P):
        with c.part(GOLDT, bevel=0.6) as p:
            p.limb((-4.0, -9.6), (4.2, -2.0), 0.5)

    def back(c, hip, neck, sho, lean, ph):
        with c.part(CANVAS, line=0.5, bevel=2.2) as p:                 # mochila enorme de mercancias
            p.poly([(neck[0] - 12, neck[1] + 8), (neck[0] - 11, neck[1] - 6), (neck[0] - 2, neck[1] - 8), (neck[0] + 0.5, neck[1] + 1), (hip[0] - 1, hip[1] + 3), (hip[0] - 10, hip[1] + 4)])
        with c.part(RUSTY, bevel=0.8) as p:
            p.limb((neck[0] - 11, neck[1] - 1), (neck[0] - 1, neck[1] - 2), 0.6)
            p.ell(neck[0] - 7, neck[1] - 9, 2.0, 1.4)
        with c.part(WHITEM, bevel=0.8) as p:
            p.ell(neck[0] - 4, neck[1] - 9.5, 1.2)
        with c.part(CLOAKV, line=0.5, bevel=2.2) as p:
            p.poly([(neck[0] - 3.5, neck[1] - 1), (neck[0] + 1.5, neck[1] - 1), (hip[0] + 1, hip[1] + 8), (hip[0] - 7, hip[1] + 12), (neck[0] - 9, neck[1] + 4)])

    M = dict(skin=MASK, cloth=CLOAKV, cloth_d=CLOAKV_D, boot=CLOAKV_D, boot_d=CLOAKV_D, vest=CLOAKV, vest_d=CLOAKV_D)
    with c.at(0, 0, 0, 1.1, 1.1):
        human(c, P, 'idle', M, head, lambda cc, PP, r, f: None, back_fn=back, torso_extra=torso, front_cb=weapon, hip_h=12.5)


# ---------------------------------------------------------------- Sylwen: espiritu flotante del bosque
def sylwen(c, a, i, n):
    t = i / n
    s = math.sin(2 * math.pi * t)
    c2 = math.cos(2 * math.pi * t)
    with c.at(0, -16 + 2.4 * s, 0.04 * s, 1.25, 1.25):
        with c.part(SPIRIT_D, bevel=2.4) as p:                         # cola de luz
            p.poly([(-3, 4), (-9 + c2, 10), (-14 + s * 2, 17), (-6, 15), (-2, 12), (0, 18 + s), (2, 11), (6, 16), (9 + c2, 9), (4, 4)])
        with c.part(SPIRIT, bevel=2.4) as p:
            p.poly([(0, -9), (5, -4), (6, 3), (2, 9), (-2, 9), (-6, 3), (-5, -4)])
        with c.part(MOSS, line=0.4, bevel=1.4) as p:                   # corona de hojas
            for k, (ox, oy, r) in enumerate([(-5, -7, 2), (-2.4, -10, 2.2), (1, -10.4, 2.2), (4.4, -8, 2), (6.4, -4.6, 1.6)]):
                p.ell(ox, oy, r, r * 0.6)
        with c.part(DARK) as p:
            p.ell(-1.8, -1.2, 1.1, 1.4); p.ell(2.2, -1.2, 1.1, 1.4)
        with c.part(Mat(ramp=['#c8ffd8', '#ffffff'], emi=True, nooutline=True)) as p:
            p.ell(-1.8, -1.2, 0.5, 0.7); p.ell(2.2, -1.2, 0.5, 0.7)
        with c.part(SPIRIT, bevel=1.4) as p:                           # manos de luz
            p.limb((-5, 2), (-9, 6 + s), 0.9, 0.5); p.limb((5, 2), (9, 6 - s), 0.9, 0.5)
    c.glow(0, -20, 18, '#7affc0', 0.35)
    for k in range(5):
        c.dotw(-10 + k * 5 + s * 2, -44 + ((t * 30 + k * 7) % 24) * -0.3 - k, '#eafff4' if k % 2 else '#7affc0')


def _npc_sheet(name, fn, tint):
    return enemy_sheet(name, (48, 48), (24, 46), (10, 28), lambda c, a, i, n: fn(c, a, i, n), tint, [('idle', 6, 5, True, {})])


def sheet_prop_npc_0(): return _npc_sheet('prop_npc_0', aldren, (40, 40, 60))
def sheet_prop_npc_1(): return _npc_sheet('prop_npc_1', vesper, (20, 20, 50))
def sheet_prop_npc_2(): return _npc_sheet('prop_npc_2', sylwen, (30, 80, 60))


SHEETS = [sheet_prop_npc_0, sheet_prop_npc_1, sheet_prop_npc_2]
