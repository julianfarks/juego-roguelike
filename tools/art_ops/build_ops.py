"""Genera los sprites del centro de operaciones (props animados) en assets/sprites/ops_*.png + .json"""
import sys, math
from kit import *

def arch_niche(c, x0, y0, x1, y1):
    """Hornacina de piedra con arco de medio punto."""
    w = x1 - x0
    cx = (x0 + x1) / 2
    top = y0 + w // 2
    c.rect(x0, top, x1, y1, STONE[3])
    c.ell(x0, y0, x1, y0 + w, STONE[3])
    # relieve interior (oscuro, profundo)
    c.rect(x0 + 3, top, x1 - 3, y1 - 1, STONE[1])
    c.ell(x0 + 3, y0 + 3, x1 - 3, y0 + w - 3, STONE[1])
    # luz del arco (borde izq claro, der oscuro)
    for y in range(top, y1 + 1):
        c.px(x0, y, STONE[5]); c.px(x0 + 1, y, STONE[4]); c.px(x1, y, STONE[1]); c.px(x1 - 1, y, STONE[2])
    for i in range(0, w + 1, 1):
        ang = math.pi * i / w
        xx = cx - math.cos(ang) * (w / 2); yy = top - math.sin(ang) * (w / 2)
        c.px(round(xx), round(yy), STONE[5] if i < w / 2 else STONE[2])
    # sombra interior arriba
    for y in range(top - w // 2 + 3, top + 3):
        for x in range(x0 + 3, x1 - 2):
            if c.get(x, y) == STONE[1] and (x + y) % 3 == 0: c.px(x, y, STONE[0])
    # juntas de bloques en el marco
    for y in range(top + 4, y1, 6):
        c.px(x0, y, STONE[2]); c.px(x1, y, STONE[0])

def sword(c, x, y, L, kind, sheen=-1):
    # kind: 0 ancha, 1 estoque, 2 curva, 3 mandoble
    w = {0: 5, 1: 3, 2: 4, 3: 5}[kind]
    for i in range(L):
        yy = y + i
        t = i / L
        ww = w if t < 0.82 else max(1, int(round(w * (1 - (t - 0.82) / 0.18))))
        off = 0
        if kind == 2: off = int(round(2 * math.sin(t * 1.6)))
        x0 = x - ww // 2 + off
        for k in range(ww):
            col = STEEL[5] if k == 0 else (STEEL[4] if k < ww - 1 else STEEL[2])
            if ww >= 5 and k == ww // 2: col = STEEL[3]     # acanalado
            c.px(x0 + k, yy, col)
        if sheen >= 0 and i == sheen % L: c.px(x0, yy, STEEL[6]); c.px(x0 + 1 if ww > 1 else x0, yy, STEEL[6])
    gy = y - 1
    if kind == 0:
        c.rect(x - 6, gy - 2, x + 6, gy, GOLD[2]); c.line(x - 6, gy - 2, x + 6, gy - 2, GOLD[4]); c.px(x - 6, gy, GOLD[1]); c.px(x + 6, gy, GOLD[1])
    elif kind == 1:
        c.rect(x - 4, gy - 1, x + 4, gy, GOLD[2]); c.px(x - 5, gy + 1, GOLD[1]); c.px(x + 5, gy + 1, GOLD[1]); c.line(x - 4, gy - 1, x + 4, gy - 1, GOLD[4])
    elif kind == 2:
        c.ell(x - 3, gy - 3, x + 3, gy + 1, GOLD[2]); c.px(x - 1, gy - 2, GOLD[5])
    else:
        c.rect(x - 8, gy - 2, x + 8, gy, STEEL[3]); c.line(x - 8, gy - 2, x + 8, gy - 2, STEEL[5])
        c.px(x - 6, gy - 1, VIOL[3]); c.px(x + 6, gy - 1, VIOL[3]); c.px(x, gy - 1, ICE[3])
    # empunadura y pomo
    c.rect(x - 1, gy - 8, x, gy - 3, WOOD[3]); c.px(x - 1, gy - 7, WOOD[5]); c.px(x, gy - 5, WOOD[1])
    c.rect(x - 2, gy - 11, x + 1, gy - 9, GOLD[2]); c.px(x - 2, gy - 11, GOLD[5])

def armory(frame):
    c = Cv(80, 104)
    arch_niche(c, 4, 4, 75, 103)
    # estandarte colgando del arco
    c.rect(34, 8, 45, 26, CLOTH_R[2]); c.line(34, 8, 45, 8, CLOTH_R[4]); c.line(34, 8, 34, 26, CLOTH_R[3]); c.line(45, 8, 45, 26, CLOTH_R[1])
    c.poly([(34, 27), (39.5, 31), (45, 27)], CLOTH_R[2]); c.poly([(35, 27), (39.5, 30), (44, 27)], CLOTH_R[1])
    c.rect(39, 11, 40, 21, STEEL[5]); c.rect(36, 20, 43, 21, GOLD[3]); c.px(39, 10, STEEL[6]); c.rect(39, 22, 40, 24, WOOD[4])
    # viga con ganchos
    c.box(10, 33, 69, 36, WOOD, 1, 3, 5)
    sheen = frame * 7
    sword(c, 18, 48, 29, 0, sheen); sword(c, 32, 48, 31, 1, sheen + 9); sword(c, 46, 48, 28, 2, sheen + 4); sword(c, 60, 48, 31, 3, sheen + 14)
    # escudo redondo (izq abajo)
    c.ell(9, 79, 27, 96, STEEL[2]); c.ell(11, 81, 25, 94, STEEL[4]); c.ell(13, 83, 23, 92, CLOTH_R[2]); c.ell(14, 84, 22, 91, CLOTH_R[3])
    c.ell(16, 86, 20, 90, GOLD[2]); c.px(17, 87, GOLD[5]); c.line(11, 82, 16, 81, STEEL[6])
    c.rect(18, 83, 19, 92, STEEL[3]); c.rect(13, 87, 22, 88, STEEL[3])
    # cajon de armas (centro)
    c.box(31, 84, 49, 95, WOOD, 1, 3, 5)
    for y in (88, 92): c.line(32, y, 48, y, WOOD[1])
    c.rect(38, 84, 42, 95, STEEL[2]); c.px(40, 90, GOLD[4])
    # casco (der) con penacho
    c.rect(60, 92, 67, 95, WOOD[2])
    c.ell(55, 78, 70, 93, STEEL[2]); c.ell(56, 78, 69, 91, STEEL[4]); c.rect(56, 85, 69, 86, STEEL[1]); c.rect(58, 85, 67, 85, OUT)
    c.line(60, 79, 65, 79, STEEL[6]); c.rect(62, 72, 63, 78, CLOTH_R[3]); c.rect(60, 70, 65, 72, CLOTH_R[4]); c.rect(62, 87, 63, 92, STEEL[1])
    # zocalo
    c.box(2, 96, 77, 103, STONE, 1, 3, 5)
    for x in range(8, 76, 14): c.line(x, 96, x, 103, STONE[1])
    c.outline()
    return c

# ---------------------------------------------------------------- muro de trofeos (nichos vacios; las estatuas se dibujan en tiempo de ejecucion)
def trophy_wall(frame):
    c = Cv(336, 100)
    c.box(0, 8, 335, 99, STONE, 1, 2, 4)
    c.rect(4, 12, 331, 95, STONE[1])
    c.box(0, 0, 335, 9, STONE, 1, 3, 5)
    for x in range(8, 330, 12):
        c.px(x, 4, GOLD[2]); c.px(x + 1, 4, GOLD[1]); c.px(x, 5, GOLD[1]); c.px(x + 4, 3, GOLD[3]); c.px(x + 4, 5, GOLD[3])
    # nueve nichos: 8 jefes y el Cazador
    for i in range(9):
        x0 = 8 + i * 36
        arch_niche(c, x0, 16, x0 + 29, 80)
        c.box(x0 - 1, 78, x0 + 30, 86, STONE, 1, 3, 5)
        c.rect(x0 + 2, 80, x0 + 27, 82, STONE[4]); c.px(x0 + 3, 81, GOLD[1]); c.px(x0 + 26, 81, GOLD[1])
    c.box(0, 88, 335, 99, STONE, 1, 3, 5)
    for x in range(0, 336, 24): c.line(x, 88, x, 99, STONE[1])
    c.outline()
    return c

# ---------------------------------------------------------------- mesa de preparacion con mapa
def prep(frame):
    c = Cv(88, 72)
    # tablero
    c.box(6, 36, 81, 44, WOOD, 1, 3, 5); c.line(6, 44, 81, 44, WOOD[0])
    # patas
    for x in (10, 72): c.box(x, 44, x + 5, 70, WOOD, 0, 2, 4)
    c.line(14, 56, 72, 56, WOOD[1]); c.line(14, 57, 72, 57, WOOD[2])
    # mapa extendido (pergamino)
    c.poly([(14, 31), (74, 31), (80, 38), (8, 38)], PAPER[3])
    c.line(14, 31, 74, 31, PAPER[4]); c.line(8, 38, 80, 38, PAPER[1])
    for i, (a, b, col) in enumerate([(20, 34, GREEN[3]), (30, 33, STEEL[3]), (46, 35, FIRE[2]), (58, 33, ICE[3]), (66, 35, VIOL[3])]):
        c.rect(a, b, a + 2, b + 1, col)
    c.line(21, 35, 31, 34, PAPER[0]); c.line(32, 34, 47, 36, PAPER[0]); c.line(48, 36, 59, 34, PAPER[0]); c.line(60, 34, 67, 36, PAPER[0])
    c.px(47, 35, FIRE[4]); c.px(46, 35, FIRE[4])
    # vela (llama animada)
    c.rect(75, 22, 78, 31, PAPER[4]); c.rect(75, 22, 75, 31, PAPER[3]); c.rect(78, 22, 78, 31, PAPER[1]); c.rect(74, 31, 79, 32, GOLD[2])
    f = [0, 1, 0, -1][frame % 4]
    c.px(76 + (1 if f > 0 else 0), 17, FIRE[3]); c.rect(76, 18, 77, 21, FIRE[2]); c.rect(76, 19, 77, 21, FIRE[3]); c.px(76, 20, FIRE[4]); c.px(77 + f, 15 + (frame % 2), FIRE[2])
    # espada apoyada + frascos
    c.rect(4, 8, 6, 36, STEEL[4]); c.line(4, 8, 4, 36, STEEL[6]); c.px(5, 7, STEEL[5]); c.rect(1, 36, 9, 38, GOLD[2]); c.rect(4, 38, 6, 42, WOOD[3])
    for (x, col) in ((18, FIRE), (24, ICE), (30, GREEN)):
        c.rect(x, 22, x + 4, 30, STEEL[5]); c.rect(x + 1, 23, x + 3, 29, col[3]); c.rect(x + 1, 27, x + 3, 29, col[2]); c.px(x + 1, 24, col[4]); c.rect(x + 1, 20, x + 3, 21, WOOD[4])
    # mochila al costado
    c.ell(54, 8, 70, 30, WOOD[3]); c.ell(55, 9, 68, 28, WOOD[4]); c.rect(54, 22, 70, 30, WOOD[2]); c.line(56, 22, 69, 22, WOOD[1]); c.rect(59, 21, 65, 24, GOLD[2]); c.px(60, 21, GOLD[5])
    c.rect(53, 14, 55, 26, CLOTH_R[2]); c.rect(69, 14, 71, 26, CLOTH_R[2])
    # banco / zocalo
    c.box(4, 68, 83, 71, STONE, 1, 3, 5)
    c.outline()
    return c

# ---------------------------------------------------------------- bestiario (libreria con tomo luminoso)
BOOKC = [CLOTH_R[2], CLOTH_B[3], GREEN[3], GOLD[1], VIOL[2], WOOD[5], ICE[2], CLOTH_R[3]]

def codex(frame):
    c = Cv(72, 104)
    # armazon de madera
    c.box(2, 14, 69, 103, WOOD, 0, 2, 4)
    c.rect(5, 17, 66, 100, WOOD[0])
    # cornisa con ojo del bestiario
    c.box(0, 6, 71, 15, WOOD, 0, 3, 5)
    c.poly([(26, 6), (36, 0), (46, 6)], WOOD[3]); c.line(26, 6, 36, 0, WOOD[5]); c.line(36, 0, 46, 6, WOOD[1])
    c.ell(31, 2, 41, 9, STEEL[1]); c.ell(32, 3, 40, 8, PAPER[3]); c.ell(35, 3, 37, 8, FIRE[2]); c.px(36, 4, FIRE[4]); c.px(36, 5, OUT)
    # estantes
    rows = [20, 44, 68]
    seed = 3
    for ri, y0 in enumerate(rows):
        c.box(5, y0 + 20, 66, y0 + 23, WOOD, 1, 3, 5)
        x = 7
        while x < 62:
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            w = 3 + (seed >> 8) % 3
            h = 12 + (seed >> 12) % 8
            col = BOOKC[(seed >> 5) % len(BOOKC)]
            if ri == 0 and 26 <= x <= 46: x += w + 1; continue          # hueco del tomo luminoso
            if ri == 1 and 40 <= x <= 50: x += w + 1; continue          # hueco del craneo
            if ri == 2 and 12 <= x <= 22: x += w + 1; continue          # hueco del frasco
            c.rect(x, y0 + 20 - h, x + w - 1, y0 + 19, col)
            c.line(x, y0 + 20 - h, x, y0 + 19, tuple(min(255, v + 40) for v in col[:3]) + (255,))
            c.line(x + w - 1, y0 + 20 - h, x + w - 1, y0 + 19, tuple(max(0, v - 50) for v in col[:3]) + (255,))
            c.px(x + w // 2, y0 + 20 - h + 2, GOLD[3])
            x += w + (1 if seed % 5 else 2)
    # tomo luminoso abierto (estante superior)
    pul = [0, 1, 2, 1][frame % 4]
    c.poly([(26, 38), (36, 36), (46, 38), (46, 40), (36, 38), (26, 40)], PAPER[3])
    c.rect(26, 38, 46, 39, PAPER[3]); c.line(27, 37, 35, 36, PAPER[4]); c.line(37, 36, 45, 37, PAPER[4]); c.rect(35, 36, 37, 40, WOOD[2])
    for i in range(4): c.px(29 + i * 4, 37, [CYAN := ICE[3], ICE[4], ICE[3], ICE[2]][(i + frame) % 4])
    c.rect(32, 31 - pul, 33, 34, ICE[4]); c.px(40, 30 - pul, ICE[4]); c.px(36, 28 - pul, STEEL[6]); c.px(34, 32 - pul, ICE[3])
    # craneo (estante medio)
    c.ell(42, 52, 50, 60, PAPER[3]); c.rect(44, 58, 48, 63, PAPER[3]); c.rect(44, 55, 45, 57, OUT); c.rect(47, 55, 48, 57, OUT); c.px(46, 59, OUT); c.line(42, 52, 46, 52, PAPER[4])
    # frasco con liquido (estante inferior)
    c.rect(13, 77, 20, 86, STEEL[5]); c.rect(14, 79, 19, 85, GREEN[4]); c.rect(14, 82, 19, 85, GREEN[3]); c.px(15, 80, GREEN[5]); c.rect(15, 74, 18, 76, WOOD[4])
    c.rect(2, 100, 69, 103, WOOD[1])
    c.outline()
    return c

# ---------------------------------------------------------------- jardin: parterres de piedra con musgo
def garden(frame):
    c = Cv(132, 64)
    for k in range(3):
        x0 = 2 + k * 43
        # caja de piedra
        c.box(x0, 34, x0 + 38, 62, STONE, 0, 2, 4)
        c.rect(x0 + 3, 28, x0 + 35, 38, WOOD[1])
        # tierra con motas (la parte superior del cantero)
        c.rect(x0 + 2, 26, x0 + 36, 36, WOOD[0])
        for i in range(0, 33, 3): c.px(x0 + 3 + i, 28 + (i // 3) % 3 * 2, WOOD[2]); c.px(x0 + 4 + i, 33 - (i // 3) % 2, WOOD[1])
        # borde frontal superior con relieve
        c.box(x0 - 1, 36, x0 + 39, 44, STONE, 1, 3, 6)
        for x in range(x0 + 4, x0 + 36, 8): c.px(x, 40, STONE[1]); c.px(x + 1, 40, STONE[5])
        # runas de crecimiento
        c.px(x0 + 19, 52, GREEN[4]); c.px(x0 + 18, 53, GREEN[3]); c.px(x0 + 20, 53, GREEN[3]); c.px(x0 + 19, 54, GREEN[4]); c.px(x0 + 19, 55, GREEN[3])
        # musgo y hierba que se mece
        for i, gx in enumerate((x0 + 1, x0 + 6, x0 + 31, x0 + 36)):
            sw = [0, 1, 0, -1][(frame + i) % 4]
            c.px(gx, 35, GREEN[3]); c.px(gx + sw, 33, GREEN[4]); c.px(gx + sw, 34, GREEN[3]); c.px(gx + 1, 35, GREEN[2])
        for i in range(0, 38, 5): c.px(x0 + i, 45 + (i % 3), GREEN[2]); c.px(x0 + i + 1, 46 + (i % 3), GREEN[3])
    c.outline()
    return c

# ---------------------------------------------------------------- cristales cultivables (5 etapas, tintables por elemento)
CR = [H(c) for c in ('4a4f68', '7a8098', 'a8b0c8', 'd8e0f0', 'ffffff')]

def crystal_shard(c, cx, base, h, w, lean=0):
    pts = [(cx - w // 2, base), (cx - w // 2 + lean, base - h * 0.72), (cx + lean, base - h), (cx + w // 2 + lean, base - h * 0.72), (cx + w // 2, base)]
    c.poly(pts, CR[2])
    c.poly([(cx - w // 2 + 1, base), (cx - w // 2 + 1 + lean, base - h * 0.7), (cx + lean, base - h + 1), (cx, base)], CR[3])
    c.poly([(cx + 1, base), (cx + lean + 1, base - h + 2), (cx + w // 2 - 1 + lean, base - h * 0.7), (cx + w // 2 - 1, base)], CR[1])
    c.line(cx - 1 + lean, base - h + 2, cx - 1, base - 2, CR[4])

def crystal(stage, frame):
    c = Cv(28, 40)
    cx, base = 14, 38
    # montículo base
    c.ell(5, 35, 23, 39, STONE[3]); c.ell(7, 34, 21, 38, STONE[4])
    if stage == 0:                                       # semilla: guijarro con chispa
        c.ell(11, 31, 17, 36, CR[1]); c.px(13, 32, CR[3]); c.px(14, 31 - (frame % 2), CR[4])
    elif stage == 1:
        crystal_shard(c, cx, 36, 11, 5)
    elif stage == 2:
        crystal_shard(c, cx - 4, 36, 12, 5, -1); crystal_shard(c, cx + 3, 36, 17, 6, 1)
    elif stage == 3:
        crystal_shard(c, cx - 7, 36, 11, 5, -2); crystal_shard(c, cx + 7, 36, 14, 5, 2); crystal_shard(c, cx, 36, 24, 8)
    else:
        crystal_shard(c, cx - 9, 36, 13, 5, -3); crystal_shard(c, cx + 9, 36, 15, 5, 3); crystal_shard(c, cx - 4, 36, 21, 6, -1)
        crystal_shard(c, cx + 4, 36, 23, 6, 1); crystal_shard(c, cx, 36, 33, 9)
    # destello animado
    if stage > 0:
        h = [0, 1, 2, 1][frame % 4]
        gx = 11 + (frame * 3) % 7; gy = 14 + stage * 2 + (frame * 5) % 9
        c.px(gx, gy, CR[4]); c.px(gx - 1, gy, CR[3]); c.px(gx + 1, gy, CR[3]); c.px(gx, gy - 1, CR[3]); c.px(gx, gy + 1, CR[3])
    c.outline(OUT)
    return c

# ---------------------------------------------------------------- rincon de companeros
def nook(frame):
    c = Cv(80, 104)
    arch_niche(c, 4, 6, 75, 103)
    # cuerda y linterna colgante (hexagonal de laton)
    bob = [0, 1, 1, 0][frame % 4]
    c.rect(39, 10, 40, 30, WOOD[3]); c.px(39, 14, WOOD[5])
    c.rect(32, 30 + bob, 47, 32 + bob, GOLD[2]); c.line(32, 30 + bob, 47, 30 + bob, GOLD[5])
    c.rect(32, 33 + bob, 47, 52 + bob, STEEL[0])
    c.rect(33, 33 + bob, 46, 52 + bob, [VIOL[1], VIOL[2], VIOL[1], VIOL[2]][frame % 4])
    c.ell(35, 36 + bob, 44, 49 + bob, VIOL[3]); c.ell(37, 38 + bob, 42, 46 + bob, VIOL[4]); c.px(38, 39 + bob, STEEL[6])
    for x in (32, 47): c.rect(x, 32 + bob, x, 53 + bob, GOLD[1])
    c.rect(39, 33 + bob, 40, 53 + bob, GOLD[1])
    c.rect(31, 53 + bob, 48, 55 + bob, GOLD[2]); c.line(31, 55 + bob, 48, 55 + bob, GOLD[0]); c.px(39, 56 + bob, GOLD[2]); c.px(40, 57 + bob, GOLD[1])
    # tres luces orbitando (fuego, hielo, sombra)
    for i, col in enumerate((FIRE[3], ICE[3], SHADOW[4])):
        a = (frame / 4 + i / 3) * 2 * math.pi
        ox = 39.5 + math.cos(a) * 22; oy = 43 + math.sin(a) * 6
        c.px(round(ox), round(oy), col); c.px(round(ox) + 1, round(oy), col)
    # cojin sobre peana de piedra
    c.box(18, 82, 61, 95, STONE, 1, 3, 5)
    c.ell(22, 74, 57, 86, CLOTH_R[2]); c.ell(24, 74, 55, 83, CLOTH_R[3]); c.ell(30, 75, 47, 79, CLOTH_R[4]); c.px(39, 74, GOLD[3]); c.px(39, 85, GOLD[2])
    c.rect(21, 82, 58, 84, CLOTH_R[1])
    # huellas y cuenco
    for (x, y) in ((28, 90), (33, 88), (45, 90), (50, 88)): c.px(x, y, STONE[1]); c.px(x + 1, y - 1, STONE[1]); c.px(x - 1, y - 1, STONE[1])
    c.box(2, 96, 77, 103, STONE, 1, 3, 5)
    c.outline()
    return c

# ---------------------------------------------------------------- panel de records
def board(frame):
    c = Cv(88, 100)
    c.box(4, 6, 83, 85, STONE, 1, 3, 5)
    c.rect(9, 11, 78, 80, STONE[1])
    c.box(9, 11, 78, 80, STONE, 0, 1, 3)
    # emblema central: calavera con espadas
    cx = 44
    for sgn in (-1, 1):
        for i in range(0, 22):
            c.px(cx + sgn * (14 - i // 2 + 0), 22 + i, STEEL[4]); c.px(cx + sgn * (14 - i // 2) + sgn, 22 + i, STEEL[2])
    c.ell(cx - 9, 26, cx + 9, 44, PAPER[3]); c.rect(cx - 5, 40, cx + 5, 48, PAPER[3]); c.line(cx - 8, 28, cx - 2, 27, PAPER[4])
    c.rect(cx - 6, 33, cx - 3, 37, OUT); c.rect(cx + 3, 33, cx + 6, 37, OUT); c.px(cx, 39, OUT); c.px(cx - 1, 40, OUT); c.px(cx + 1, 40, OUT)
    c.px(cx - 4, 34, FIRE[2]); c.px(cx + 4, 34, FIRE[2])
    for x in range(cx - 5, cx + 6, 2): c.px(x, 47, OUT)
    # laureles
    for sgn in (-1, 1):
        for i in range(10):
            ang = 0.3 + i * 0.28
            lx = cx + sgn * (30 + math.cos(ang) * 2); ly = 70 - i * 5.2
            c.ell(round(lx) - 2, round(ly) - 1, round(lx) + 2, round(ly) + 1, GREEN[3] if i % 2 else GREEN[4])
            c.px(round(lx), round(ly), GREEN[5])
        # destello dorado que recorre el laurel
        g = (frame * 3 + (0 if sgn < 0 else 5)) % 10
        lx = cx + sgn * 31; ly = 70 - g * 5.2
        c.px(round(lx), round(ly), GOLD[5]); c.px(round(lx) - 1, round(ly), GOLD[4]); c.px(round(lx) + 1, round(ly), GOLD[4]); c.px(round(lx), round(ly) - 1, GOLD[4])
    # placas de record (3 renglones grabados)
    for i in range(3):
        y = 56 + i * 7
        c.rect(24, y, 64, y + 3, STONE[2]); c.line(24, y, 64, y, STONE[0]); c.line(24, y + 4, 64, y + 4, STONE[5])
        c.rect(27, y + 1, 36, y + 2, GOLD[2]); c.rect(41, y + 1, 61, y + 2, STONE[4])
    # coronacion y base
    c.box(0, 0, 87, 7, STONE, 1, 3, 5)
    for x in range(6, 84, 10): c.px(x, 3, GOLD[2]); c.px(x + 1, 3, GOLD[1])
    c.box(0, 86, 87, 99, STONE, 1, 3, 5)
    for x in range(0, 88, 22): c.line(x, 86, x, 99, STONE[1])
    c.outline()
    return c

# ---------------------------------------------------------------- puesto de la tienda (el mercader se dibuja detras)
def stall(frame):
    c = Cv(112, 96)
    # postes
    for x in (4, 104): c.box(x, 18, x + 3, 95, WOOD, 0, 2, 4)
    # toldo a rayas con festoneado
    sway = [0, 0, 1, 0][frame % 4]
    c.poly([(0, 20), (111, 20), (107, 6), (4, 6)], CLOTH_R[2])
    for i in range(0, 112, 16):
        c.poly([(i, 20), (i + 8, 20), (i + 7, 7), (i + 3, 6)], PAPER[3] if (i // 16) % 2 == 0 else CLOTH_R[2])
    c.line(4, 6, 107, 6, CLOTH_R[4]); c.rect(0, 19, 111, 20, CLOTH_R[1])
    for i in range(0, 112, 8):
        col = PAPER[2] if (i // 8) % 2 == 0 else CLOTH_R[1]
        d = 3 + (sway if (i // 8) % 2 else 0)
        c.poly([(i, 21), (i + 7, 21), (i + 4, 21 + d + 3)], col)
    # farol colgante
    c.rect(55, 27, 56, 34, STEEL[2]); c.rect(51, 34, 60, 42, GOLD[1]); c.rect(52, 35, 59, 41, FIRE[2 + (frame % 2)]); c.px(55, 38, FIRE[4]); c.px(56, 37, FIRE[4])
    # mostrador
    c.box(0, 62, 111, 95, WOOD, 0, 2, 4)
    for x in range(8, 108, 20): c.line(x, 66, x, 93, WOOD[0])
    c.box(0, 58, 111, 65, WOOD, 2, 4, 6)
    c.line(0, 65, 111, 65, WOOD[0])
    # mercancia sobre el mostrador
    c.rect(12, 50, 19, 57, STEEL[5]); c.rect(13, 52, 18, 56, GREEN[4]); c.rect(14, 47, 17, 49, WOOD[4])           # frasco
    c.rect(24, 51, 31, 57, STEEL[5]); c.rect(25, 53, 30, 56, FIRE[3]); c.rect(26, 48, 29, 50, WOOD[4])
    c.ell(80, 48, 94, 58, WOOD[4]); c.ell(82, 49, 92, 57, WOOD[3]); c.line(82, 50, 90, 50, GOLD[3])             # bolsa
    c.px(86, 47, GOLD[3])
    # gema morada en pedestal (moneda premium, solo exhibicion)
    c.rect(98, 55, 103, 57, STONE[3])
    glow = [0, 1, 2, 1][frame % 4]
    c.poly([(100, 44), (104, 49), (100, 55), (96, 49)], VIOL[3]); c.poly([(100, 44), (96, 49), (100, 55)], VIOL[2]); c.px(99, 47, VIOL[4]); c.px(100 + glow % 2, 46, STEEL[6])
    c.outline()
    return c

if __name__ == '__main__':
    which = sys.argv[1:] or ['armory', 'trophy_wall', 'prep', 'codex', 'garden', 'crystal', 'nook', 'board', 'stall']
    out = {}
    if 'armory' in which:
        out['ops_armory'] = save('ops_armory', [[armory(i) for i in range(4)]], {'idle': {'row': 0, 'n': 4, 'fps': 3, 'loop': True}})
    if 'trophy_wall' in which:
        out['ops_trophy_wall'] = save('ops_trophy_wall', [[trophy_wall(0)]], {'idle': {'row': 0, 'n': 1, 'fps': 1, 'loop': True}})
    if 'prep' in which:
        out['ops_prep'] = save('ops_prep', [[prep(i) for i in range(4)]], {'idle': {'row': 0, 'n': 4, 'fps': 7, 'loop': True}})
    if 'codex' in which:
        out['ops_codex'] = save('ops_codex', [[codex(i) for i in range(4)]], {'idle': {'row': 0, 'n': 4, 'fps': 4, 'loop': True}})
    if 'garden' in which:
        out['ops_garden'] = save('ops_garden', [[garden(i) for i in range(4)]], {'idle': {'row': 0, 'n': 4, 'fps': 3, 'loop': True}})
    if 'crystal' in which:
        out['ops_crystal'] = save('ops_crystal', [[crystal(st, f) for f in range(4)] for st in range(5)],
                                  {('stage%d' % st): {'row': st, 'n': 4, 'fps': 4, 'loop': True} for st in range(5)}, pivot=[14, 38])
    if 'nook' in which:
        out['ops_nook'] = save('ops_nook', [[nook(i) for i in range(4)]], {'idle': {'row': 0, 'n': 4, 'fps': 4, 'loop': True}})
    if 'board' in which:
        out['ops_board'] = save('ops_board', [[board(i) for i in range(4)]], {'idle': {'row': 0, 'n': 4, 'fps': 3, 'loop': True}})
    if 'stall' in which:
        out['ops_stall'] = save('ops_stall', [[stall(i) for i in range(4)]], {'idle': {'row': 0, 'n': 4, 'fps': 3, 'loop': True}})
    # vista previa x3
    W = sum(i.width // 4 * 3 for i in out.values()) + 20 * len(out)
    pv = Image.new('RGBA', (max(W, 100), 330), (30, 26, 40, 255)); x = 0
    for n, im in out.items():
        cw = json.load(open(os.path.join(A, n + '.json')))['cell'][0]
        f = im.crop((0, 0, cw, im.height)).resize((cw * 3, im.height * 3), Image.NEAREST)
        pv.paste(f, (x, 10), f); x += cw * 3 + 20
    pv.save('/tmp/ops_prev.png'); print('listo', pv.size)
