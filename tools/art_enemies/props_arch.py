import math
from props_kit import *

STONE = R('#7a7894', 6, 0.20)
STONE_D = R('#4c4a66', 5, 0.22)
WOOD = R('#8a5634', 6, 0.20)
IRON = R('#8c92a6', 5, 0.24)
IRON_D = R('#50546c', 5, 0.22)
BRASS = R('#d9a43a', 5, 0.24)
FIRE = [rgb(c) for c in ('#5a1a1e', '#b8321e', '#f0701c', '#ffb53a', '#fff0a0')]


def stone_bricks(c, m, ramp, y0, rows=5, bh=6, bw=8, seed=3):
    """mortero oscuro entre ladrillos."""
    dark = ramp[0]
    for r in range(rows):
        y = y0 + r * bh
        for yy in range(y, y + 1):
            for x in range(c.W):
                if m[yy % c.H, x] if 0 <= yy < c.H else False:
                    c.px(x, yy, dark)
        off = (r % 2) * (bw // 2)
        for x in range(off, c.W, bw):
            for yy in range(y, y + bh):
                if 0 <= yy < c.H and 0 <= x < c.W and m[yy, x]:
                    c.px(x, yy, dark)


def door_frame(c, hole, opening):
    W, H = 32, 48
    outer = c.arch(0, 0, 32, 48, 10)
    c.paint(outer, STONE, bevel=2.5, bias=0.55, grad=0.25, tex=0.18, dith=0.6)
    # ladrillos del marco
    br = outer & ~opening
    for r in range(0, 48, 6):
        for x in range(32):
            if br[r, x]:
                c.px(x, r, STONE[1])
    for r in range(0, 48, 6):
        off = 4 if (r // 6) % 2 else 0
        for x in range(off, 32, 8):
            for y in range(r + 1, min(48, r + 6)):
                if br[y, x]:
                    c.px(x, y, STONE[1])
    # clave del arco: bloque dorado-gris
    c.paint(c.poly([(13, 1), (19, 1), (18, 7), (14, 7)]) & outer, STONE, bevel=1.2, bias=0.75, rim=True)
    c.px(16, 3, BRASS[3]); c.px(16, 4, BRASS[2])
    # zocalo
    c.paint(c.rect(0, 44, 32, 48), STONE_D, bevel=1.4, bias=0.6)
    # hombros oscuros alrededor de apertura (jamba)
    jam = (c.arch(4, 8, 28, 48, 9) & ~opening)
    c.paint(jam, STONE_D, bevel=1.4, bias=0.35, rim=False, dark_edge=False)
    # remates con tachuelas
    for y in (16, 26, 36):
        c.px(2, y, IRON[3]); c.px(29, y, IRON[3])


def opening_mask(c):
    return c.arch(6, 11, 26, 44, 8)


def interior(c, op, glow):
    ys, xs = c.yy, c.xx
    # pasillo oscuro con luz lejana calida que sube con glow
    dist = np.sqrt(((xs - 16) / 11.0) ** 2 + ((ys - 30) / 19.0) ** 2)
    base = np.array([20, 16, 38])
    lum = np.clip(1 - dist, 0, 1) * glow
    bay = BAY[ys % 4, xs % 4]
    cols = np.zeros((c.H, c.W, 3), np.uint8)
    cols[:] = base
    t1 = (lum > bay * 0.8)[..., None]
    t2 = (lum > 0.42 + bay * 0.4)[..., None]
    t3 = (lum > 0.8 + bay * 0.3)[..., None]
    t0 = (lum > bay * 0.3 - 0.0)[..., None]
    cols = np.where(t0, np.array([40, 26, 56]), cols).astype(np.uint8)
    cols = np.where(t1, np.array([86, 52, 84]), cols).astype(np.uint8)
    cols = np.where(t2, np.array([226, 150, 70]), cols).astype(np.uint8)
    cols = np.where(t3, np.array([255, 226, 150]), cols).astype(np.uint8)
    c.c[op] = cols[op]
    c.a[op] = True
    # suelo del umbral
    c.flat(c.rect(6, 42, 26, 44) & op, (44, 38, 64))


def door_leaf(c, op, w, glow=0.0):
    """Hoja de madera con herrajes; w = ancho visible (bisagra a la izquierda x=6)."""
    if w < 1:
        return
    leaf = op & (c.xx < 6 + w)
    full = max(w, 1)
    c.paint(leaf, WOOD, bevel=1.6, bias=0.52, grad=0.2, tex=0.12, light=(-0.9, -0.3))
    # tablas verticales
    for k in range(1, 6):
        x = 6 + int(round(k * full / 5.0)) - 1
        for y in range(11, 44):
            if leaf[y, x] if x < 32 else False:
                c.px(x, y, WOOD[0])
    # bandas de hierro
    for y0 in (17, 30):
        band = leaf & (c.yy >= y0) & (c.yy < y0 + 3)
        c.paint(band, IRON_D, bevel=1.0, bias=0.62, rim=True)
        for x in range(8, 6 + int(w), 4):
            c.px(x, y0 + 1, IRON[4])
    # picaporte/aro
    if w > 8:
        rx = 6 + int(w) - 5
        c.px(rx, 27, BRASS[3]); c.px(rx + 1, 27, BRASS[2]); c.px(rx, 28, BRASS[1]); c.px(rx + 1, 28, BRASS[2])
    # borde de la hoja (canto)
    c.vline(5 + int(w), 12, 43, WOOD[1])


def sheet_door():
    sh = PSheet('prop_door', 32, 48, [16, 47], [20, 40])

    def closed(c, i, n):
        op = opening_mask(c)
        door_frame(c, None, op)
        interior(c, op, 0.0)
        door_leaf(c, op, 20)

    def open_(c, i, n):
        t = sm(i / (n - 1))
        w = 20 * (1 - t) ** 1.3
        # arranque con anticipacion: la hoja cede
        op = opening_mask(c)
        door_frame(c, None, op)
        interior(c, op, t * 1.2)
        door_leaf(c, op, w if w > 3 else 3 + (2 if i == n - 1 else 0))
        # polvo
        if 0 < i < n - 1:
            for k in range(3):
                c.px(8 + k * 7 + i, 43 - (i % 2), STONE[4], top=True)

    def open_idle(c, i, n):
        op = opening_mask(c)
        door_frame(c, None, op)
        interior(c, op, 1.2)
        door_leaf(c, op, 3)
    sh.anim('closed', 1, 1, False, closed)
    sh.anim('open', 6, 10, False, open_)
    sh.anim('open_idle', 1, 1, True, open_idle)
    return sh





PORT = [rgb(c) for c in ('#2a3048', '#55648a', '#8fa6cc', '#cfe0f2', '#ffffff')]


def sheet_portal():
    sh = PSheet('prop_portal', 48, 64, [24, 63], [26, 56])
    CX, CY, RX, RY = 24.0, 31.5, 15.5, 27.0

    def fr(c, i, n):
        ph = i / n * 2 * math.pi
        dx = (c.xx + 0.5 - CX) / RX
        dy = (c.yy + 0.5 - CY) / RY
        r = np.sqrt(dx * dx + dy * dy)
        ang = np.arctan2(dy, dx)
        # borde ondulante
        wob = 0.022 * np.sin(3 * ang - ph) + 0.016 * np.sin(5 * ang + 2 * ph)
        rr = r - wob
        m = rr <= 1.0
        # brazos de espiral girando hacia el centro
        sp = np.sin(3 * ang + 5.5 * np.log(np.maximum(rr, 0.05) + 0.25) * 2.2 - ph)
        sp2 = np.sin(2 * ang - 7.0 * rr + ph * 2)
        v = 0.5 + 0.34 * sp + 0.12 * sp2
        rc = np.clip(rr, 0, 1)
        v = v * (0.55 + 0.45 * rc ** 0.6) + (1 - rc) ** 2.4 * 0.55
        # aro luminoso
        v = v * 0.88 - 0.05
        ring = (rr > 0.74) & (rr <= 0.9)
        v = np.where(ring, v + 0.3, v)
        v = np.where(rr > 0.9, 0.3 + 0.1 * np.sin(ang * 4 + ph), v)
        bay = BAY[c.yy % 4, c.xx % 4] - 0.5
        idx = np.clip(np.floor(v * 4.0 + 0.25 + bay * 0.6), 0, 4).astype(int)
        # nucleo claro
        core = rr < 0.18 + 0.03 * math.sin(ph)
        idx = np.where(core, 4, idx)
        # borde exterior oscuro-azulado fino para silueta
        edge = m & (rr > 0.93)
        idx = np.where(edge, np.minimum(idx + 0, 3), idx)
        cols = np.array(PORT, np.uint8)[idx]
        c.c[m] = cols[m]; c.a[m] = True
        # base: piedras
        for (bx, bw) in ((13, 22),):
            c.paint(c.rect(bx, 58, bx + bw, 63) , STONE_D, bevel=1.2, bias=0.5)
        c.paint(c.poly([(15, 58), (33, 58), (30, 55), (18, 55)]), STONE, bevel=1.0, bias=0.6)
        c.lightpass(24, 56, 9, (190, 215, 245), 0.4)
        # destellos en espiral hacia dentro y chispas hacia arriba
        for k in range(7):
            a = ph + k * 2 * math.pi / 7
            rad = 1.25 - 0.55 * ((k * 0.37 + i / n) % 1.0)
            x = CX + math.cos(a * 1.0 + k) * RX * rad
            y = CY + math.sin(a * 1.0 + k) * RY * rad
            c.px(x, y, (255, 255, 255) if k % 2 == 0 else PORT[3], top=True)
        for k in range(4):
            t = (i / n + k * 0.25) % 1.0
            x = 24 + math.sin(k * 2.3 + t * 6) * 9
            y = 60 - t * 52
            c.px(x, y, PORT[3] if t < 0.6 else PORT[2], top=True)

    sh.anim('idle', 8, 10, True, fr)
    return sh





GOLDG = [rgb(c) for c in ('#6a3a1e', '#c0742a', '#f2b43c', '#ffe27a', '#fffbe0')]
RUNE = rgb('#ffd45a')


def orb(c, cx, cy, r, ramp):
    sphere(c, cx, cy, r, ramp)
    c.px(int(cx - r * 0.45), int(cy - r * 0.45), ramp[4]); c.px(int(cx - r * 0.45) + 1, int(cy - r * 0.45), ramp[4])


def pedestal(c, lit):
    # escalones
    c.paint(c.rect(3, 43, 29, 48), STONE, bevel=1.6, bias=0.55, grad=0.2, tex=0.15)
    c.paint(c.rect(6, 39, 26, 43), STONE, bevel=1.4, bias=0.6, grad=0.15, tex=0.15)
    # columna con ligera cintura
    col = c.poly([(10, 39), (22, 39), (20, 26), (12, 26)])
    c.paint(col, STONE, bevel=2.2, bias=0.55, grad=0.2, tex=0.12, light=(-1, 0))
    # anillos de la columna
    c.paint(c.rect(9, 36, 23, 38), STONE_D, bevel=1.0, bias=0.6)
    c.paint(c.rect(9, 27, 23, 29), STONE_D, bevel=1.0, bias=0.6)
    # tapa/cuenco
    c.paint(c.poly([(6, 21), (26, 21), (24, 26), (8, 26)]), STONE, bevel=1.4, bias=0.62, grad=0.2)
    c.paint(c.rect(5, 19, 27, 22), STONE, bevel=1.2, bias=0.72, rim=True)
    c.paint(c.rect(8, 18, 24, 19), STONE_D, bevel=0.8, bias=0.4, rim=False)


def runes(c, glow):
    cols = [RUNE, rgb('#fff0a0')] if glow > 0.5 else [rgb('#8a5a2a')]
    if glow <= 0:
        cols = [rgb('#2c2a40')]
    # tres glifos pequenos en la columna
    glyph = [((14, 31), (15, 32), (14, 33), (16, 31)), ((17, 30), (18, 31), (17, 32), (18, 33)),
             ((15, 34), (16, 34), (16, 35), (15, 36))]
    for g in glyph:
        for (x, y) in g:
            c.px(x, y, cols[0])
    if glow > 0.8:
        c.px(15, 32, cols[-1]); c.px(18, 31, cols[-1])


def sheet_altar():
    sh = PSheet('prop_altar', 32, 48, [16, 47], [20, 44])

    def idle(c, i, n):
        t = i / n
        by = 11 + round(math.sin(t * 2 * math.pi) * 1.4)
        pul = 0.5 + 0.5 * math.sin(t * 2 * math.pi)
        pedestal(c, True)
        runes(c, 0.6 + 0.4 * pul)
        c.lightpass(16, by + 4, 17, (255, 214, 110), 0.55 + 0.25 * pul)
        runes(c, 0.6 + 0.4 * pul)
        # halo del orbe
        c.halo(16, by, 9 + pul * 2, (255, 214, 110), 0.55 + 0.2 * pul, top=False)
        orb(c, 16, by, 4.4, GOLDG)
        # rayos cardinales sutiles
        if pul > 0.6:
            for d in (7, 8):
                c.px(16, by - d, GOLDG[3], top=True); c.px(16, by + d, GOLDG[2], top=True)
                c.px(16 - d, by, GOLDG[2], top=True); c.px(16 + d, by, GOLDG[2], top=True)
        # motas que ascienden en espiral
        for k in range(5):
            u = (t + k / 5.0) % 1.0
            x = 16 + math.sin(u * 6.28 + k * 1.7) * (6 + 2 * k % 3)
            y = 20 - u * 18
            c.px(x, y, GOLDG[4] if u < 0.5 else GOLDG[3], top=True)
            if u < 0.35:
                c.px(x + 1, y + 1, GOLDG[2], top=True)

    def used(c, i, n):
        pedestal(c, False)
        runes(c, 0)
        # orbe apagado: cenizas en el cuenco y grieta
        c.paint(c.ell(16, 17, 4, 1.6), [rgb('#2a2838'), rgb('#3c3a50'), rgb('#55526a')], bevel=1, bias=0.5, rim=False)
        for (x, y) in ((17, 31), (16, 32), (17, 33), (16, 34), (15, 35)):
            c.px(x, y, rgb('#1c1a2c'))
        c.px(14, 24, rgb('#1c1a2c')); c.px(15, 25, rgb('#1c1a2c'))
        c.px(18, 15, rgb('#6a6882'), top=True); c.px(13, 14, rgb('#55526a'), top=True)

    sh.anim('idle', 6, 8, True, idle)
    sh.anim('used', 1, 1, False, used)
    return sh





SOULF = [rgb(c) for c in ('#1e5a8c', '#2f9ac4', '#7fe0e8', '#d4fbff', '#ffffff')]
RUNEC = rgb('#6fe6ee')


def glyph(c, x, y, col, k):
    pat = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2)]
    for j, (dx, dy) in enumerate(pat):
        if hnoise(k, j, 7) > 0.48 or j == 4:
            c.px(x + dx, y + dy, col)


def sheet_sanctuary():
    sh = PSheet('prop_sanctuary', 64, 64, [32, 63], [44, 60])

    def fr(c, i, n):
        t = i / n
        ph = t * 2 * math.pi
        # escalones
        c.paint(c.rect(4, 57, 60, 64), STONE, bevel=2.0, bias=0.52, grad=0.25, tex=0.16)
        c.paint(c.rect(10, 52, 54, 57), STONE, bevel=1.8, bias=0.58, grad=0.2, tex=0.16)
        for x in range(4, 60, 8):
            c.vline(x + (2 if (x // 8) % 2 else 0), 58, 63, STONE[1])
        # obelisco ahusado
        ob = c.poly([(22, 52), (42, 52), (38, 24), (26, 24)])
        c.paint(ob, STONE, bevel=3.2, bias=0.5, grad=0.25, tex=0.14, light=(-1, -0.1), dith=0.6)
        # cara derecha en sombra
        c.paint(c.poly([(35, 52), (42, 52), (38, 24), (34, 24)]) & ob, STONE_D, bevel=1.5, bias=0.45, rim=False, dark_edge=False)
        # anillos metalicos
        for y in (46, 33):
            band = ob & (c.yy >= y) & (c.yy < y + 2)
            c.paint(band, IRON_D, bevel=1.0, bias=0.6)
        # runas luminosas con onda ascendente
        for k, gy in enumerate((48, 41, 36, 29)):
            wave = (t * 4 - (3 - k) * 0.0) % 4
            lit = max(0.0, 1 - abs(((t * 5) % 5) - (4 - k) - 0.5) * 0.7)
            col = [mix(RUNEC, (20, 40, 70), 0.75), mix(RUNEC, (20, 40, 70), 0.4), RUNEC, SOULF[3]][min(3, int(lit * 3.9))]
            glyph(c, 29 + (k % 2), gy, col, k)
        # brasero: cuenco
        c.paint(c.poly([(17, 17), (47, 17), (42, 25), (22, 25)]), IRON, bevel=2.0, bias=0.55, grad=0.2, light=(-1, 0))
        c.paint(c.rect(15, 15, 49, 18), IRON, bevel=1.3, bias=0.72)
        c.paint(c.rect(24, 24, 40, 27), IRON_D, bevel=1.2, bias=0.5)
        for x in (19, 26, 32, 38, 45):
            c.px(x, 19, IRON[4])
        # cuernos
        c.paint(c.poly([(16, 15), (13, 8), (18, 13)]), IRON_D, bevel=1.0, bias=0.6)
        c.paint(c.poly([(48, 15), (51, 8), (46, 13)]), IRON_D, bevel=1.0, bias=0.45)
        # fuego espiritual grande
        flame(c, 32, 16, 15 + int(1.5 * math.sin(ph)), 9, ph, SOULF, sway=1.1, lick=1.0)
        flame(c, 25, 16, 9 + int(1.5 * math.sin(ph + 1.5)), 4, ph + 1.3, SOULF, sway=1.3, seed=2)
        flame(c, 39, 16, 10 + int(1.5 * math.sin(ph + 3)), 4, ph + 2.7, SOULF, sway=1.3, seed=4)
        c.lightpass(32, 14, 20, (140, 235, 245), 0.5)
        c.halo(32, 10, 18, (110, 210, 235), 0.28, top=False)
        # almas / chispas ascendentes
        for k in range(8):
            u = (t + k / 8.0) % 1.0
            x = 32 + math.sin(u * 5 + k * 1.9) * (5 + (k * 3) % 7)
            y = 13 - u * 11
            col = SOULF[4] if u < 0.4 else (SOULF[3] if u < 0.7 else SOULF[2])
            c.px(x, y, col, top=True)
            if u < 0.3:
                c.px(x, y + 1, SOULF[2], top=True)
    sh.anim('idle', 8, 8, True, fr)
    return sh


SHEETS = [sheet_door, sheet_portal, sheet_altar, sheet_sanctuary]
