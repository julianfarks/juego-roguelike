"""Arte de los sucesos especiales de las runs (espiritu, prisionero, santuario de pactos, camara de reliquia)."""
import sys, math
sys.path.insert(0, '../art_ops')
from kit import *

def spirit(frame):
    c = Cv(48, 56)
    n = 6
    ph = frame / n * 2 * math.pi
    bob = round(math.sin(ph) * 2)
    sway = round(math.sin(ph + 1) * 2)
    cx = 24
    top = 6 + bob
    # cola ondulante (de abajo hacia el cuerpo)
    for i in range(0, 26):
        y = top + 20 + i
        w = max(1, 11 - i * 11 // 26)
        x = cx + round(math.sin(ph + i * 0.35) * (1 + i * 0.12)) + (sway * i // 26)
        c.rect(x - w, y, x + w, y, ICE[3] if i % 3 else ICE[2])
        c.px(x - w, y, ICE[2]); c.px(x + w, y, ICE[1])
        if w > 2: c.px(x - w + 2, y, ICE[4])
    # cabeza
    c.ell(cx - 13, top, cx + 13, top + 26, ICE[3])
    c.ell(cx - 11, top + 1, cx + 7, top + 17, ICE[4])
    c.ell(cx - 9, top + 2, cx + 1, top + 9, STEEL[6])
    c.line(cx + 7, top + 6, cx + 12, top + 18, ICE[2])
    # sombra del vientre
    c.poly([(cx - 12, top + 20), (cx + 12, top + 20), (cx + 8, top + 27), (cx - 8, top + 27)], ICE[2])
    # ojos grandes
    for ex in (cx - 7, cx + 3):
        c.ell(ex, top + 10, ex + 5, top + 18, OUT)
        c.px(ex + 1, top + 12, STEEL[6]); c.px(ex + 2, top + 12, STEEL[6])
    c.line(cx - 3, top + 21, cx + 2, top + 21, OUT); c.px(cx - 4, top + 20, OUT); c.px(cx + 3, top + 20, OUT)
    # brazos pequenos
    hx = round(math.sin(ph * 2) * 1)
    c.ell(cx - 18, top + 18 + hx, cx - 12, top + 23 + hx, ICE[3]); c.ell(cx + 12, top + 18 - hx, cx + 18, top + 23 - hx, ICE[3])
    c.outline(OUT)
    # chispas orbitando (sin contorno)
    for k in range(3):
        a = ph + k * 2.1
        x = cx + round(math.cos(a) * 20); y = top + 12 + round(math.sin(a) * 9)
        c.px(x, y, VIOL[4]); c.px(x + 1, y, VIOL[3]); c.px(x, y - 1, VIOL[3])
    return c

def cage(frame, openn=False):
    c = Cv(56, 64)
    b = [0, 1, 1, 0][frame % 4]
    # base de piedra
    c.box(2, 54, 53, 63, STONE, 1, 3, 5)
    c.rect(4, 57, 51, 59, STONE[2])
    # prisionero (sentado o de pie)
    if not openn:
        # encapuchado sentado
        c.ell(19, 36 + b, 37, 56, CLOTH_B[3]); c.ell(21, 36 + b, 35, 50, CLOTH_B[4])
        c.ell(21, 27 + b, 35, 41 + b, CLOTH_B[2]); c.ell(23, 30 + b, 33, 40 + b, SHADOW[0])
        c.px(26, 35 + b, STEEL[6]); c.px(30, 35 + b, STEEL[6])
        c.rect(14, 52, 22, 54, PAPER[2]); c.rect(34, 52, 42, 54, PAPER[2])     # manos/pies
        c.line(13, 48, 13, 56, STEEL[3]); c.px(13, 57, STEEL[4])               # grillete
    else:
        wave = [0, -2, 0, 2][frame % 4]
        c.ell(20, 22, 36, 55, CLOTH_B[3]); c.ell(22, 22, 34, 46, CLOTH_B[4])
        c.ell(21, 11, 35, 28, CLOTH_B[2]); c.ell(23, 14, 33, 27, SHADOW[0])
        c.px(26, 20, STEEL[6]); c.px(30, 20, STEEL[6])
        c.rect(38, 28 + wave, 42, 38 + wave, CLOTH_B[3]); c.rect(38, 26 + wave, 42, 29 + wave, PAPER[2])
        c.rect(14, 34, 18, 46, CLOTH_B[3])
    # jaula: arco superior y barrotes
    if not openn:
        c.rect(4, 4, 51, 7, STEEL[1]); c.line(4, 4, 51, 4, STEEL[3]); c.line(4, 7, 51, 7, STEEL[0])
        c.poly([(6, 4), (28, -2), (49, 4)], STEEL[1]); c.line(6, 4, 28, -1, STEEL[3])
        for x in range(6, 52, 7):
            c.rect(x, 7, x + 1, 55, STEEL[2]); c.line(x, 7, x, 55, STEEL[4]); c.line(x + 1, 7, x + 1, 55, STEEL[0])
        c.rect(4, 30, 51, 31, STEEL[1]); c.line(4, 30, 51, 30, STEEL[3])
        c.rect(24, 28, 31, 35, GOLD[2]); c.rect(25, 29, 30, 34, GOLD[1]); c.px(27, 31, OUT); c.px(28, 31, OUT); c.px(27, 32, OUT)   # candado
    else:
        c.rect(4, 4, 51, 7, STEEL[1]); c.line(4, 4, 51, 4, STEEL[3])
        for x in (6, 13): c.rect(x, 7, x + 1, 55, STEEL[2]); c.line(x, 7, x, 55, STEEL[4])
        c.rect(48, 7, 49, 55, STEEL[2]); c.line(48, 7, 48, 55, STEEL[4])
        c.poly([(40, 8), (52, 14), (52, 54), (40, 52)], STEEL[1])   # puerta abierta de lado
        c.line(40, 8, 40, 52, STEEL[3]); c.px(37, 32, GOLD[3]); c.px(38, 33, GOLD[2])   # candado roto en el suelo
    c.outline(OUT)
    return c

def shrine(frame):
    c = Cv(96, 76)
    n = 6; ph = frame / n * 2 * math.pi
    # tablilla central con runas
    c.box(30, 18, 65, 75, STONE, 1, 3, 5)
    c.rect(33, 22, 62, 72, STONE[2]); c.line(33, 22, 62, 22, STONE[1])
    c.poly([(30, 18), (48, 6), (65, 18)], STONE[4]); c.line(30, 18, 48, 6, STONE[5]); c.line(48, 6, 65, 18, STONE[2])
    for i in range(5):
        y = 28 + i * 8
        glow = (frame + i) % n == 0
        c.rect(38, y, 57, y + 1, VIOL[3] if glow else STONE[4]); c.px(37, y, STONE[1]); c.px(58, y, STONE[1])
    # pedestales
    for px, col in ((2, GOLD), (66, VIOL)):
        c.box(px, 52, px + 27, 75, STONE, 1, 3, 5)
        c.box(px - 2, 48, px + 29, 53, STONE, 2, 4, 6)
        c.rect(px + 4, 60, px + 23, 62, STONE[4])
        c.px(px + 14, 66, col[3]); c.px(px + 13, 67, col[2]); c.px(px + 15, 67, col[2]); c.px(px + 14, 68, col[3])
    # simbolos flotantes: sol (dorado) y luna (violeta)
    bob = round(math.sin(ph) * 2)
    sx, sy = 16, 26 + bob
    for a in range(8):
        ang = a / 8 * 2 * math.pi + ph * 0.5
        c.px(sx + round(math.cos(ang) * 11), sy + round(math.sin(ang) * 11), GOLD[4]); c.px(sx + round(math.cos(ang) * 10), sy + round(math.sin(ang) * 10), GOLD[3])
    c.ell(sx - 7, sy - 7, sx + 7, sy + 7, GOLD[2]); c.ell(sx - 5, sy - 6, sx + 3, sy + 1, GOLD[4]); c.px(sx - 3, sy - 4, GOLD[5])
    mx, my = 80, 26 - bob
    c.ell(mx - 9, my - 9, mx + 9, my + 9, VIOL[3]); c.ell(mx - 5, my - 11, mx + 12, my + 7, (0, 0, 0, 0)); 
    c.ell(mx - 9, my - 9, mx + 9, my + 9, VIOL[3])
    c.ell(mx - 3, my - 10, mx + 13, my + 8, (0, 0, 0, 0))
    c.px(mx - 7, my - 3, VIOL[4]); c.px(mx - 7, my - 2, VIOL[4]); c.px(mx - 6, my - 5, STEEL[6])
    for i in range(3): c.px(mx - 12 + i, my + 2 + i * 2, VIOL[4])
    c.outline(OUT)
    return c

def relic(frame, taken=False):
    c = Cv(40, 56)
    n = 6; ph = frame / n * 2 * math.pi
    # peana escalonada
    c.box(4, 46, 35, 55, STONE, 1, 3, 5)
    c.box(8, 38, 31, 46, STONE, 1, 3, 5)
    c.rect(11, 40, 28, 42, STONE[4])
    if not taken:
        bob = round(math.sin(ph) * 2)
        cx, cy = 20, 22 + bob
        # anillo de runas
        for k in range(8):
            a = k / 8 * 2 * math.pi + ph
            c.px(cx + round(math.cos(a) * 15), cy + round(math.sin(a) * 4) + 8, GOLD[4 if k % 2 else 3])
        # cristal facetado dorado
        c.poly([(cx, cy - 14), (cx + 8, cy - 2), (cx, cy + 12), (cx - 8, cy - 2)], GOLD[2])
        c.poly([(cx, cy - 14), (cx - 8, cy - 2), (cx, cy + 12)], GOLD[3])
        c.poly([(cx, cy - 14), (cx + 8, cy - 2), (cx + 2, cy - 2)], GOLD[1])
        c.line(cx, cy - 14, cx, cy + 12, GOLD[4]); c.px(cx - 3, cy - 6, GOLD[5]); c.px(cx - 4, cy - 5, GOLD[5])
        c.outline(OUT)
        for k in range(3):
            a = ph * 1.5 + k * 2.1
            x = cx + round(math.cos(a) * 12); y = cy - 4 + round(math.sin(a) * 10)
            c.px(x, y, GOLD[5]); c.px(x + 1, y, GOLD[4])
    else:
        c.outline(OUT)
        for k in range(8):
            a = k / 8 * 2 * math.pi
            c.px(20 + round(math.cos(a) * 15), 30 + round(math.sin(a) * 4), STONE[3])
    return c

if __name__ == '__main__':
    which = sys.argv[1:] or ['spirit', 'cage', 'shrine', 'relic']
    ims = []
    if 'spirit' in which: ims.append(save('ev_spirit', [[spirit(i) for i in range(6)]], {'idle': {'row': 0, 'n': 6, 'fps': 6, 'loop': True}}, pivot=[24, 55], body=[26, 50]))
    if 'cage' in which: ims.append(save('ev_cage', [[cage(i) for i in range(4)], [cage(i, True) for i in range(4)]],
                                         {'idle': {'row': 0, 'n': 4, 'fps': 3, 'loop': True}, 'open': {'row': 1, 'n': 4, 'fps': 4, 'loop': True}}, pivot=[28, 63], body=[46, 60]))
    if 'shrine' in which: ims.append(save('ev_shrine', [[shrine(i) for i in range(6)]], {'idle': {'row': 0, 'n': 6, 'fps': 5, 'loop': True}}, pivot=[48, 75], body=[90, 70]))
    if 'relic' in which: ims.append(save('ev_relic', [[relic(i) for i in range(6)], [relic(0, True)]],
                                          {'idle': {'row': 0, 'n': 6, 'fps': 5, 'loop': True}, 'open': {'row': 1, 'n': 1, 'fps': 1, 'loop': True}}, pivot=[20, 55], body=[34, 52]))
    W = sum(i.width for i in ims) + 10 * len(ims); Hh = max(i.height for i in ims)
    prev = Image.new('RGBA', (W, Hh), (30, 26, 40, 255)); x = 0
    for i in ims: prev.paste(i, (x, 0), i); x += i.width + 10
    prev = prev.resize((prev.width * 2, prev.height * 2), Image.NEAREST)
    prev.save('/tmp/ev_prev.png'); print('listo', prev.size)
