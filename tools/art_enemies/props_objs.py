import math, random
from props_kit import *
from props_arch import STONE, STONE_D, WOOD, IRON, IRON_D, BRASS, GOLDG, FIRE

CLAY = R('#9a7a62', 6, 0.20, hs=0.06)
WOOD_D = R('#5e3a2a', 5, 0.22)
WATER = [rgb(c) for c in ('#124456', '#1b7c88', '#3fc0a6', '#a2eed0', '#eafff2')]


# ------------------------------------------------------------------ cofre
def chest_body(c):
    c.paint(c.rect(2, 12, 22, 23), WOOD, bevel=1.8, bias=0.5, grad=0.2, tex=0.14, dith=0.6)
    for x in (8, 12, 16):
        c.vline(x, 13, 22, WOOD[1])
    for bx in (4, 17):
        c.paint(c.rect(bx, 12, bx + 3, 23), IRON, bevel=1.0, bias=0.55, grad=0.1)
        c.px(bx + 1, 14, IRON[4]); c.px(bx + 1, 20, IRON[4])
    c.paint(c.rect(2, 21, 22, 23), IRON_D, bevel=0.9, bias=0.5, rim=False)
    c.paint(c.rect(10, 14, 14, 19), BRASS, bevel=1.2, bias=0.6)
    c.px(12, 16, IRON_D[0]); c.px(12, 17, IRON_D[0])


def chest_lid(c, ybot, h, x0=2, x1=22, under=False):
    if h <= 0:
        return
    top = ybot - h
    lid = c.arch(x0, top, x1, ybot, min(3, h - 1)) if h > 3 else c.rect(x0, top, x1, ybot)
    if under:
        c.paint(lid, WOOD_D, bevel=1.4, bias=0.45, grad=0.15, tex=0.1)
        c.paint(c.rect(x0 + 2, top, x0 + 5, ybot) & lid, IRON_D, bevel=0.8, bias=0.5)
        c.paint(c.rect(x1 - 5, top, x1 - 2, ybot) & lid, IRON_D, bevel=0.8, bias=0.5)
    else:
        c.paint(lid, WOOD, bevel=1.6, bias=0.55, grad=0.25, tex=0.14, dith=0.6)
        for bx in (4, 17):
            c.paint(c.rect(bx, top, bx + 3, ybot) & lid, IRON, bevel=1.0, bias=0.58)
        c.paint(c.rect(x0, ybot - 1, x1, ybot) & lid, IRON_D, bevel=0.8, bias=0.5, rim=False)


def chest_inside(c, glow):
    m = c.poly([(4, 9), (20, 9), (21, 12), (3, 12)])
    c.flat(m, GOLDG[1])
    c.hline(4, 20, 9, (70, 36, 30))
    for x in range(3, 22):
        for y in (10, 11):
            if m[y, x]:
                c.px(x, y, GOLDG[2] if (x + y) % 3 else GOLDG[3])
    for (x, y, k) in ((6, 10, 4), (10, 10, 3), (14, 11, 4), (17, 10, 3), (8, 11, 1), (12, 11, 1), (19, 11, 1)):
        c.px(x, y, GOLDG[k])


def sheet_chest():
    sh = PSheet('prop_chest', 24, 24, [12, 23], [20, 14])

    def closed(c, i, n):
        chest_body(c); chest_lid(c, 12, 7)

    def open_(c, i, n):
        chest_body(c)
        if i == 0:
            chest_lid(c, 11, 7)
            c.hline(4, 20, 11, (255, 226, 150))
        elif i == 1:
            chest_inside(c, 0.6); chest_lid(c, 9, 7)
            
        elif i == 2:
            chest_inside(c, 0.8); chest_lid(c, 6, 6)
            c.lightpass(12, 8, 8, (255, 225, 140), 0.45)
            for x in (7, 12, 16):
                c.vline(x, 1, 8, (255, 232, 150), top=True)
        elif i == 3:
            chest_inside(c, 1); chest_lid(c, 5, 5, 3, 21, under=True)
            c.lightpass(12, 8, 8, (255, 225, 140), 0.45)
            for (x, y) in ((8, 6), (12, 4), (16, 6), (10, 2), (14, 3)):
                c.px(x, y, GOLDG[4], top=True)
        else:
            chest_inside(c, 1); chest_lid(c, 6, 5, 3, 21, under=True)
            c.lightpass(12, 8, 8, (255, 225, 140), 0.4)
            for (x, y) in ((6, 7), (12, 3), (18, 7), (9, 1), (15, 2)):
                c.px(x, y, GOLDG[3], top=True)

    def open_idle(c, i, n):
        chest_body(c); chest_inside(c, 1); chest_lid(c, 6, 5, 3, 21, under=True)
        c.lightpass(12, 8, 8, (255, 225, 140), 0.4)
        c.px(12, 3, GOLDG[3], top=True); c.px(7, 6, GOLDG[2], top=True)
    sh.anim('closed', 1, 1, False, closed)
    sh.anim('open', 5, 12, False, open_)
    sh.anim('open_idle', 1, 1, True, open_idle)
    return sh


# ------------------------------------------------------------------ vasija
def pot_shape(c, squash=0, dy=0, cx=8):
    body = c.poly([(cx - 3, 3 + dy), (cx + 3, 3 + dy), (cx + 5, 7 + dy), (cx + 4, 12 + dy - squash),
                   (cx + 2, 15), (cx - 2, 15), (cx - 4, 12 + dy - squash), (cx - 5, 7 + dy)])
    body |= c.ell(cx, 8 + dy, 5.4, 6.2) & c.rect(0, 5 + dy, 16, 14)
    body &= c.rect(0, 0, 16, 15)
    c.paint(body, CLAY, bevel=2.6, bias=0.58, grad=0.25, tex=0.12, dith=0.6, light=(-1, -0.4))
    c.paint(c.rect(cx - 4, 2 + dy, cx + 4, 4 + dy), CLAY, bevel=1.0, bias=0.7)
    c.hline(cx - 4, cx + 5, 7 + dy, CLAY[1])
    c.hline(cx - 4, cx + 5, 11 + dy, CLAY[1])


def sheet_pot():
    sh = PSheet('prop_pot', 16, 16, [8, 15], [10, 14])
    rnd = random.Random(5)
    shards = []
    for k in range(7):
        a = -math.pi / 2 + (k - 3) * 0.42 + rnd.uniform(-0.1, 0.1)
        sp = rnd.uniform(1.4, 2.6)
        shards.append((8 + (k - 3) * 1.2, 8 + rnd.uniform(-2, 2), math.cos(a) * sp, math.sin(a) * sp * 1.3, rnd.randint(2, 3), k))

    def closed(c, i, n):
        pot_shape(c)

    def brk(c, i, n):
        if i == 0:
            pot_shape(c, squash=1)
            for (x, y) in ((6, 6), (7, 7), (8, 8), (8, 9), (9, 10)):
                c.px(x, y, CLAY[0])
            c.hline(2, 4, 8, CLAY[5], top=True); c.hline(12, 14, 8, CLAY[5], top=True)
            return
        floor = 15.0
        for (x0, y0, vx, vy, sz, k) in shards:
            t = i * 1.0
            x = x0 + vx * t * 0.75
            y = y0 + vy * t * 1.3 + 0.9 * t * t
            rest = y >= floor - sz + 0.5
            if rest:
                y = floor - sz * 0.5
            if i == 4:
                x = 8 + (k - 3) * 1.7
                y = floor - 1 if k % 2 == 0 else floor - 2
            r = max(1, sz - (1 if i >= 3 else 0))
            if i == 4:
                m = c.rect(x - r, y, x + r + 1, floor + 1) if k % 2 else c.poly([(x - r, floor + 1), (x + r, floor + 1), (x - 1, y - 1)])
            else:
                m = c.poly([(x - r, y + r * 0.6), (x + r * 0.2, y - r), (x + r, y + r * 0.7), (x, y + r)])
            c.paint(m, CLAY, bevel=1.2, bias=0.55 + 0.1 * (k % 3 - 1), rim=True)
        # polvo
        for k in range(5):
            if i <= 3:
                a = (k - 2) * 0.55
                c.px(8 + math.sin(a) * (2 + i * 2.5), 12 - i * 0.8 - abs(k - 2) * 0.4, CLAY[4] if i < 3 else CLAY[3], top=True)
    sh.anim('closed', 1, 1, False, closed)
    sh.anim('break', 5, 16, False, brk)
    return sh


# ------------------------------------------------------------------ fuente
def sheet_fountain():
    sh = PSheet('prop_fountain', 32, 40, [16, 39], [28, 34])

    def fr(c, i, n):
        t = i / n
        ph = t * 2 * math.pi
        # cuenco inferior
        c.paint(c.poly([(1, 31), (31, 31), (28, 39), (4, 39)]), STONE, bevel=2.2, bias=0.5, grad=0.25, tex=0.14, dith=0.6)
        c.paint(c.rect(0, 29, 32, 32), STONE, bevel=1.3, bias=0.72)
        # agua del cuenco
        wm = c.rect(2, 30, 30, 32)
        c.paint(wm, WATER, bevel=1.0, bias=0.45, rim=False, dark_edge=False,
                lumfn=lambda xx, yy: 0.22 * np.sin(xx * 0.7 - ph) + 0.15 * np.sin(xx * 1.3 + ph * 2))
        # remaches
        for x in (6, 12, 19, 25):
            c.vline(x, 33, 38, STONE[1])
        # columna
        c.paint(c.poly([(13, 30), (19, 30), (18, 19), (14, 19)]), STONE, bevel=1.8, bias=0.55, light=(-1, 0))
        c.paint(c.rect(12, 26, 20, 28), STONE_D, bevel=1.0, bias=0.55)
        # cuenco superior
        c.paint(c.poly([(7, 14), (25, 14), (21, 20), (11, 20)]), STONE, bevel=1.8, bias=0.55, grad=0.2, tex=0.1)
        c.paint(c.rect(6, 12, 26, 15), STONE, bevel=1.1, bias=0.72)
        c.paint(c.rect(8, 12, 24, 14), WATER, bevel=1.0, bias=0.5, rim=False, dark_edge=False,
                lumfn=lambda xx, yy: 0.25 * np.sin(xx * 0.9 + ph))
        # chorro central
        for y in range(2, 13):
            tt = (12 - y) / 10.0
            x = 16
            col = WATER[4] if tt < 0.5 else WATER[3]
            if (y + i) % 3 != 0 or tt < 0.3:
                c.px(x, y, col); 
                if tt < 0.55:
                    c.px(x - 1, y, WATER[2])
        # cortinas de agua cayendo del cuenco superior al inferior
        for x in (9, 12, 20, 23):
            for y in range(15, 30):
                c.px(x, y, WATER[3] if (y + i + x) % 4 < 2 else WATER[2])
        # gotas en arco
        for k in range(8):
            u = (t + k / 8.0) % 1.0
            side = -1 if k % 2 else 1
            x = 16 + side * (u * 9 + 1)
            y = 3 + 4 * (2 * u - 1) ** 2 * -1 + u * 11 + 1
            c.px(x, y, WATER[4] if u < 0.5 else WATER[3], top=True)
        # brillo y luz verde-azulada sobre piedra
        c.lightpass(16, 22, 16, (110, 230, 190), 0.38)
        c.halo(16, 12, 14, (120, 240, 200), 0.22, top=False)
        # cruces curativas ascendentes
        for k in range(2):
            u = (t + k / 2.0) % 1.0
            x = 16 + math.sin(u * 6.3 + k * 3.1) * 8
            y = 10 - u * 9
            col = WATER[4]
            c.px(x, y, col, top=True); c.px(x - 1, y, WATER[3], top=True); c.px(x + 1, y, WATER[3], top=True)
            c.px(x, y - 1, WATER[3], top=True); c.px(x, y + 1, WATER[3], top=True)
    sh.anim('idle', 8, 8, True, fr)
    return sh



ANV = R('#6a7290', 5, 0.26)
EMB = [rgb(c) for c in ('#5a1a22', '#b02a1c', '#f0641a', '#ffb43a', '#fff2a8')]
CLOTH = R('#7a2a46', 5, 0.22)
CLOAK = R('#4a3a6e', 5, 0.24)


def sheet_forge():
    sh = PSheet('prop_forge', 40, 40, [20, 39], [36, 36])

    def fr(c, i, n):
        t = i / n
        ph = t * 2 * math.pi
        # horno de piedra
        c.paint(c.rect(1, 14, 18, 40), STONE, bevel=2.2, bias=0.5, grad=0.25, tex=0.15, dith=0.6)
        c.paint(c.rect(0, 12, 19, 16), STONE, bevel=1.3, bias=0.72)
        c.paint(c.rect(6, 3, 13, 13), STONE_D, bevel=1.5, bias=0.5, grad=0.2)
        c.paint(c.rect(5, 2, 14, 4), STONE, bevel=1.0, bias=0.7)
        for y in (20, 26, 32):
            c.hline(1, 18, y, STONE[0])
        # tocon de madera
        c.paint(c.poly([(23, 29), (36, 29), (37, 40), (22, 40)]), WOOD, bevel=2.0, bias=0.5, grad=0.15, tex=0.18, light=(-1, 0))
        for x in (26, 29, 33):
            c.vline(x, 31, 39, WOOD[1])
        c.paint(c.ell(29.5, 29, 6.5, 1.6), WOOD_D, bevel=1.0, bias=0.8, rim=True)
        # yunque
        top = c.poly([(20, 19), (36, 19), (39, 21), (36, 23), (31, 23), (31, 26), (34, 28), (34, 30), (22, 30), (22, 28),
                      (25, 26), (25, 23), (20, 23)])
        c.paint(top, ANV, bevel=2.0, bias=0.5, grad=0.3, dith=0.6, light=(-0.8, -0.6))
        c.hline(21, 36, 19, ANV[4])
        c.hline(22, 34, 29, IRON_D[0])
        # martillo apoyado
        c.line((21, 18), (24, 12), 1)
        c.paint(c.line((21, 18), (24, 12), 2), WOOD, bevel=0.6, bias=0.5, rim=False)
        c.paint(c.rect(21, 10, 28, 14), IRON_D, bevel=1.0, bias=0.55)
        # luz del horno sobre piedra y yunque
        c.lightpass(9, 33, 13, (255, 140, 50), 0.4 + 0.1 * math.sin(ph * 2))
        c.lightpass(29, 18, 9, (255, 150, 60), 0.4)
        mouth = c.arch(4, 20, 15, 38, 5)
        c.flat(mouth, (26, 12, 22))
        flame(c, 9, 37, 10 + int(1.5 * math.sin(ph)), 5, ph, EMB, sway=0.7)
        flame(c, 6, 37, 6 + int(1.5 * math.sin(ph + 2)), 3, ph + 2, EMB, sway=0.9, seed=3)
        flame(c, 12, 37, 7 + int(1.2 * math.sin(ph + 4)), 3, ph + 4, EMB, sway=0.9, seed=6)
        for x in range(5, 15):
            c.px(x, 37, EMB[2] if hnoise(x, i // 2, 3) > 0.4 else EMB[1])
        c.paint(c.rect(3, 20, 4, 38), STONE_D, bevel=0.8, bias=0.4, rim=False)
        glow = 0.5 + 0.5 * math.sin(ph)
        hot = [EMB[1], EMB[2], EMB[3], EMB[4]]
        c.paint(c.rect(25, 17, 33, 19), hot, bevel=0.9, bias=0.55 + 0.25 * glow, rim=False, dark_edge=False)
        c.halo(9, 30, 13, (255, 150, 60), 0.22, top=False)
        # humo
        for k in range(3):
            u = (t + k / 3.0) % 1.0
            x = 9.5 + math.sin(u * 5 + k) * 2.5
            y = 1 - u * 1
            c.px(x, y, mix((90, 82, 110), (50, 46, 66), u), top=True)
        # brasas ascendentes y chispas del yunque
        for k in range(7):
            u = (t * (1 + k % 2) + k / 7.0) % 1.0
            x = 9 + math.sin(u * 6 + k * 1.7) * (3 + k % 4)
            y = 36 - u * 32
            c.px(x, y, EMB[4] if u < 0.3 else (EMB[3] if u < 0.6 else EMB[2]), top=True)
        if i % 4 in (0, 1):
            for k in range(5):
                a = -1.2 + k * 0.5
                r = 2 + (i % 4) * 3
                c.px(29 + math.cos(a) * r, 18 + math.sin(a) * r * 1.0 + (i % 4) * 1.5, EMB[4], top=True)
    sh.anim('idle', 8, 10, True, fr)
    return sh


def sheet_merchant():
    sh = PSheet('prop_merchant', 40, 40, [20, 39], [36, 34])
    LAMP = [rgb(c) for c in ('#6a3a1e', '#c0742a', '#f2b43c', '#ffe27a', '#fffbe0')]

    def fr(c, i, n):
        t = i / n
        ph = t * 2 * math.pi
        br = round(math.sin(ph) * 0.6 + 0.4)          # respiracion
        sw = round(math.sin(ph) * 0.8)
        # capa del mercader (detras del mostrador)
        cloak = c.poly([(12, 28), (14, 17 + br), (18, 14 + br), (22, 14 + br), (26, 17 + br), (28, 28)])
        c.paint(cloak, CLOAK, bevel=2.4, bias=0.5, grad=0.25, tex=0.1, light=(-1, -0.3))
        hood = c.ell(20, 11 + br, 6.5, 7.0) & c.rect(0, 0, 40, 18 + br)
        c.paint(hood, CLOAK, bevel=2.2, bias=0.58, grad=0.2, light=(-1, -0.5), dith=0.5)
        # cara en sombra + ojos dorados
        face = c.ell(21, 12 + br, 3.6, 3.9)
        c.flat(face, (14, 10, 24))
        blink = (i == 5)
        if not blink:
            c.px(19, 12 + br, LAMP[4]); c.px(23, 12 + br, LAMP[4])
            c.px(19, 13 + br, LAMP[2]); c.px(23, 13 + br, LAMP[2])
        else:
            c.px(19, 13 + br, LAMP[1]); c.px(23, 13 + br, LAMP[1])
        c.hline(19, 25, 6 + br, CLOAK[4])
        # mostrador
        c.paint(c.rect(1, 27, 39, 40), WOOD, bevel=1.8, bias=0.5, grad=0.2, tex=0.16, dith=0.6)
        c.paint(c.rect(0, 25, 40, 28), WOOD, bevel=1.2, bias=0.72)
        for x in (8, 16, 24, 32):
            c.vline(x, 29, 39, WOOD[1])
        # tela con ribete dorado colgando delante
        cl = c.poly([(6, 28), (34, 28), (34, 37), (30, 35), (26, 38), (20, 36), (14, 38), (10, 35), (6, 37)])
        c.paint(cl, CLOTH, bevel=1.6, bias=0.5, grad=0.2, light=(-0.8, -0.2))
        c.hline(6, 35, 29, GOLDG[2]); 
        for x in range(8, 33, 6):
            c.px(x, 33, GOLDG[3])
        # mercancia sobre el mostrador
        # pocion roja
        c.paint(c.rect(6, 21, 10, 25), [rgb('#4a0e24'), rgb('#a01c3a'), rgb('#e0405a'), rgb('#ff90a0')], bevel=1.0, bias=0.6)
        c.paint(c.rect(7, 19, 9, 21), [rgb('#7a6a8a'), rgb('#b8b0cc')], bevel=0.6, bias=0.6)
        # pocion verde
        c.paint(c.rect(11, 22, 14, 25), [rgb('#0e3a30'), rgb('#1c8a62'), rgb('#52d89a'), rgb('#b8ffd8')], bevel=1.0, bias=0.6)
        c.px(12, 21, rgb('#b8b0cc'))
        # espada corta
        c.line((29, 24), (35, 19), 1)
        c.paint(c.line((29, 24), (35, 19), 2), IRON, bevel=0.6, bias=0.6, rim=False)
        c.px(29, 24, GOLDG[2]); c.px(28, 25, GOLDG[1])
        # libro
        c.paint(c.rect(24, 22, 29, 25), R('#5a2a6a', 4, 0.2), bevel=1.0, bias=0.55)
        c.hline(25, 28, 23, GOLDG[3])
        # monedas (la mano las mueve)
        c.paint(c.ell(17.5, 24.4, 2.4, 1.0), GOLDG, bevel=1.0, bias=0.7, rim=False)
        mx = 16 + round(math.sin(ph) * 1.5)
        c.px(mx, 22 - (1 if i % 4 == 2 else 0), GOLDG[4]); c.px(mx + 1, 22 - (1 if i % 4 == 2 else 0), GOLDG[3])
        if i % 4 == 2:
            c.px(mx, 21, GOLDG[4], top=True)
        # luz calida del farol
        c.lightpass(8 + sw, 9, 16, (255, 190, 90), 0.5 + 0.1 * math.sin(ph * 3))
        c.halo(8 + sw, 9, 8, (255, 200, 110), 0.3, top=True)
        # farol colgado a la izquierda
        c.vline(2, 2, 22, WOOD_D[2]); c.vline(3, 2, 22, WOOD_D[1])
        c.hline(2, 8, 2, WOOD_D[2])
        c.vline(7, 3, 6, IRON_D[1])
        c.paint(c.rect(5 + sw, 6, 10 + sw, 12), IRON_D, bevel=0.8, bias=0.5)
        c.flat(c.rect(6 + sw, 7, 9 + sw, 11), LAMP[3] if i % 3 else LAMP[4])
        # polvo/motas
        for k in range(3):
            u = (t + k / 3.0) % 1.0
            c.px(30 + math.sin(u * 5 + k) * 4, 24 - u * 18, mix((200, 180, 140), (110, 90, 110), u), top=True)
    sh.anim('idle', 8, 7, True, fr)
    return sh


SHEETS = [sheet_chest, sheet_pot, sheet_fountain, sheet_forge, sheet_merchant]
