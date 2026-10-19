#!/usr/bin/env python3
"""Paladin del Alba - pose de reposo en vista 3/4 (PROTOTIPO EXPERIMENTAL aislado, 192x192).

Cada pieza esta definida con vertices colocados a mano (coordenadas de pixel) y sombreada por bandas con
motor_pixel.py. Es codigo, no un dibujo hecho a mano. Las capas se exportan a capas/ para editarlas a mano.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from motor_pixel import Lienzo, smooth, hexrgb

AQUI = os.path.dirname(os.path.abspath(__file__))


def ell(cx, cy, rx, ry, n=28, a0=0, a1=360):
    return [(cx + math.cos(math.radians(a0 + (a1 - a0) * i / n)) * rx, cy + math.sin(math.radians(a0 + (a1 - a0) * i / n)) * ry) for i in range(n + 1)]


def arco(cx, cy, rx, ry, a0, a1, n=14):
    return ell(cx, cy, rx, ry, n, a0, a1)


def estrella8(cx, cy, rl, rs, r0=0):
    pts = []
    for i in range(16):
        r = rl if i % 4 == 0 else (rs if i % 2 == 0 else rs * 0.42)
        a = math.radians(r0 + i * 22.5)
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return pts


def dibujar():
    L = Lienzo()
    # ============================================================ CAPA (detras)
    capa = [(70, 64), (60, 74), (50, 100), (40, 132), (32, 160), (28, 180), (38, 176), (46, 184), (58, 176), (68, 183), (80, 174), (92, 181), (104, 172),
            (116, 160), (122, 130), (122, 90), (118, 66)]
    mc = L.pieza('capa', capa, 'blue', modo='cylx', rim=2, spec=False, tono=0.05)
    # pliegues: cuñas oscuras y luces dentro de la capa
    sombras = [[(60, 80), (50, 120), (42, 160), (36, 180), (46, 182), (54, 150), (62, 108)],
               [(76, 90), (70, 130), (66, 170), (72, 182), (80, 174), (82, 130), (82, 96)],
               [(98, 92), (96, 130), (98, 170), (108, 170), (110, 130), (108, 94)]]
    luces = [[(66, 78), (58, 118), (50, 160), (53, 172), (60, 150), (68, 100)],
             [(86, 96), (84, 130), (84, 168), (90, 176), (92, 130), (92, 100)]]
    from motor_pixel import RAMPS
    msk = L.mask(capa)
    for i, s in enumerate(sombras):
        m = L.mask(s) & msk
        _cap(L, 'cape_sombra%d' % i, m, RAMPS['blue'][0])
    for i, s in enumerate(luces):
        m = L.mask(s) & msk
        _cap(L, 'cape_luz%d' % i, m, RAMPS['blue'][3])
    # ribete dorado del dobladillo
    hem = [(28, 180), (38, 176), (46, 184), (58, 176), (68, 183), (80, 174), (92, 181), (104, 172), (116, 160)]
    L.linea('cape_ribete', hem, RAMPS['gold'][2], 3)
    L.linea('cape_ribete_luz', [(x, y - 1) for x, y in hem], RAMPS['gold'][4], 1)
    # estrellas doradas en la capa
    for (cx, cy) in ((48, 140), (72, 152), (60, 112), (100, 148)):
        L.forma('estrella_capa', estrella8(cx, cy, 4.2, 2.4), RAMPS['gold'][3])
    # ============================================================ PIERNAS
    def pierna(nombre, hx, kx, ax, ox, bx, sombra_extra=0):
        # subcapa oscura
        L.pieza(nombre + '_inf', [(hx - 9, 106), (hx + 9, 106), (kx + 8, 140), (ax + 7, 168), (ax - 7, 168), (kx - 8, 140)], 'dark', modo='cylx', spec=False)
        # cuisse
        L.pieza(nombre + '_cuisse', [(hx - 11, 108), (hx + 10, 108), (kx + 9, 138), (kx - 9, 138)], 'gold', modo='cylx', rim=2)
        L.forma(nombre + '_cuisse_junta', [(hx - 10, 122), (hx + 9, 122), (kx + 9, 124), (kx - 9, 124)], RAMPS['gold'][0])
        L.linea(nombre + '_cuisse_filo', [(hx - 9, 110), (kx - 7, 136)], RAMPS['gold'][4], 1)
        # rodillera
        L.pieza(nombre + '_rodilla', ell(kx, 142, 10.5, 9), 'gold', modo='round', rim=2, luz=(0.35, 0.3))
        L.forma(nombre + '_gema', ell(kx, 142, 3, 3, 10), RAMPS['red'][3])
        L.pix(nombre + '_gema_luz', [(kx - 1, 140)], '#FFFFFF')
        L.pieza(nombre + '_ala', [(kx - 8, 136), (kx - 15, 132), (kx - 12, 143), (kx - 8, 146)], 'gold', modo='diag', rim=1)
        # greba
        L.pieza(nombre + '_greba', [(kx - 9, 148), (kx + 9, 148), (ax + 8, 168), (ax - 8, 168)], 'gold', modo='cylx', rim=2)
        L.linea(nombre + '_greba_cresta', [(kx - 1, 150), (ax - 1, 167)], RAMPS['gold'][4], 1)
        L.forma(nombre + '_greba_acero', [(kx + 4, 150), (kx + 9, 150), (ax + 8, 168), (ax + 4, 168)], RAMPS['steel'][1])
        L.forma(nombre + '_greba_junta', [(kx - 8, 158), (kx + 8, 158), (ax + 8, 160), (ax - 8, 160)], RAMPS['gold'][0])
        # bota (sabaton): caña de cuero + puntera dorada
        L.pieza(nombre + '_bota', [(ax - 9, 166), (ax + 8, 166), (ax + 9, 174), (ax + 22, 178), (ax + 22, 184), (ax - 10, 184), (ax - 11, 174)], 'leather', modo='cyly', rim=2, spec=False)
        L.pieza(nombre + '_puntera', [(ax + 4, 174), (ax + 14, 172), (ax + 23, 178), (ax + 23, 184), (ax + 4, 184)], 'gold', modo='diag', rim=2)
        L.forma(nombre + '_puntera_junta', [(ax + 4, 174), (ax + 6, 174), (ax + 6, 184), (ax + 4, 184)], RAMPS['gold'][0])
        L.linea(nombre + '_bota_correa', [(ax - 9, 168), (ax + 8, 168)], RAMPS['gold'][3], 2)
    pierna('lejos', 78, 76, 76, 0, 0)
    pierna('cerca', 112, 114, 114, 0, 0)
    # ============================================================ TORSO
    L.pieza('torso_inf', [(68, 70), (122, 70), (118, 108), (72, 108)], 'dark', modo='cylx', spec=False)
    # faldones laterales de cadera
    L.pieza('falda_izq', [(68, 106), (88, 106), (90, 128), (78, 134), (68, 126)], 'gold', modo='diag', rim=2)
    L.pieza('falda_der', [(104, 106), (124, 106), (122, 126), (112, 134), (102, 128)], 'gold', modo='diag', rim=2)
    L.forma('falda_junta_i', [(70, 118), (90, 118), (90, 119), (70, 119)], RAMPS['gold'][0])
    L.forma('falda_junta_d', [(102, 118), (122, 118), (122, 119), (102, 119)], RAMPS['gold'][0])
    # peto: placa superior (pecho) + 3 placas de abdomen
    pecho = [(66, 70), (78, 62), (96, 66), (114, 62), (126, 70), (122, 90), (112, 98), (80, 98), (70, 90)]
    L.pieza('peto', pecho, 'gold', modo='round', rim=3, luz=(0.3, 0.2))
    L.pieza('abdomen1', [(74, 96), (118, 96), (116, 104), (76, 104)], 'gold', modo='cyly', rim=1, tono=0.1)
    L.pieza('abdomen2', [(76, 102), (116, 102), (114, 110), (78, 110)], 'gold', modo='cyly', rim=1, tono=0.2)
    # panel central de tela: blanco con bandas azules y estrella dorada
    L.pieza('tabardo_pecho_azul', [(88, 64), (104, 64), (106, 108), (86, 108)], 'blue', modo='cylx', spec=False, rim=1)
    L.pieza('tabardo_pecho_blanco', [(91, 66), (101, 66), (102, 108), (90, 108)], 'white', modo='cylx', spec=False, rim=1)
    # gorjal de acero
    L.pieza('gorjal', ell(96, 63, 17, 8), 'steel', modo='round', rim=2)
    L.pieza('gorjal2', ell(96, 61, 13, 6), 'steel', modo='round', rim=1, tono=-0.1)
    # estrella del pecho
    L.forma('estrella_pecho', estrella8(96, 80, 6, 3.4), RAMPS['gold'][3], outline=True)
    L.forma('estrella_pecho_c', ell(96, 80, 1.6, 1.6, 8), RAMPS['blue'][2])
    # cinturon con hebilla
    L.pieza('cinturon', [(70, 106), (122, 106), (122, 114), (70, 114)], 'leather', modo='cyly', rim=1, spec=False)
    L.pieza('hebilla', [(89, 104), (103, 104), (103, 116), (89, 116)], 'gold', modo='round', rim=2)
    L.forma('hebilla_c', [(93, 108), (99, 108), (99, 113), (93, 113)], RAMPS['red'][2])
    # tabardo (faldon) con borde dorado
    L.pieza('faldon_azul', [(86, 114), (106, 114), (108, 148), (96, 158), (84, 148)], 'blue', modo='cylx', spec=False, rim=1)
    L.pieza('faldon_blanco', [(90, 116), (102, 116), (103, 146), (96, 154), (89, 146)], 'white', modo='cylx', spec=False, rim=1)
    L.linea('faldon_ribete', [(84, 148), (96, 158), (108, 148)], RAMPS['gold'][3], 2)
    L.forma('faldon_estrella', estrella8(96, 134, 4.4, 2.5), RAMPS['gold'][3])
    # ============================================================ ESCUDO (lado derecho del espectador)
    esc = [(132, 62), (150, 60), (170, 64), (172, 96), (166, 122), (152, 144), (140, 130), (132, 104), (130, 80)]
    L.pieza('escudo_borde', esc, 'gold', modo='diag', rim=2)
    esc2 = [(135, 66), (150, 64), (167, 67), (169, 95), (163, 119), (152, 138), (142, 126), (135, 102), (133, 82)]
    L.pieza('escudo_campo', esc2, 'blue', modo='diag', rim=1, spec=False)
    L.pieza('escudo_acero', [(138, 70), (150, 68), (164, 70), (166, 94), (160, 114), (152, 130), (144, 120), (138, 100), (136, 84)], 'blue', modo='round', rim=1, spec=False, tono=-0.1)
    cx, cy = 152, 96
    L.forma('escudo_sol_rayos', estrella8(cx, cy, 17, 10), RAMPS['gold'][3], outline=True)
    L.forma('escudo_sol_luz', estrella8(cx - 1, cy - 1, 13, 7), RAMPS['gold'][4])
    L.pieza('escudo_sol_disco', ell(cx, cy, 7, 7, 20), 'gold', modo='round', rim=2)
    L.forma('escudo_sol_gema', ell(cx, cy, 2.8, 2.8, 10), RAMPS['blue'][3])
    L.pix('escudo_sol_brillo', [(cx - 1, cy - 1)], '#FFFFFF')
    for (x, y) in ((136, 70), (166, 70), (164, 96), (136, 98), (152, 134)):
        L.forma('escudo_remache', ell(x, y, 1.6, 1.6, 6), RAMPS['steel'][3])
    # ============================================================ BRAZO DERECHO DEL ESPECTADOR (escudo)
    L.pieza('brazo_d_inf', [(122, 80), (136, 84), (142, 112), (132, 118), (124, 100)], 'dark', modo='cylx', spec=False)
    L.pieza('brazal_d', [(126, 100), (138, 102), (142, 120), (130, 124)], 'gold', modo='cylx', rim=2)
    L.pieza('codo_d', ell(132, 98, 7.5, 7), 'gold', modo='round', rim=2)
    # ============================================================ HOMBRERAS
    def hombrera(nombre, cx, cy, r, flip=1):
        for i, (dy, k) in enumerate(((22, 0.78), (12, 0.9), (4, 1.0))):
            L.pieza('%s_lamina%d' % (nombre, i), ell(cx, cy + dy * r / 18, r * k, r * 0.82 * k, 30, 180, 360) + ell(cx, cy + dy * r / 18 + r * 0.45, r * k, r * 0.45 * k, 14, 0, 180)[::-1][:0],
                    'gold', modo='round', rim=2, luz=(0.3, 0.25), tono=0.06 * i)
        L.pieza(nombre + '_cupula', ell(cx, cy - 4, r * 0.78, r * 0.62, 30), 'gold', modo='round', rim=3, luz=(0.3, 0.25), tono=-0.08)
        L.linea(nombre + '_borde_acero', arco(cx, cy - 4, r * 0.78, r * 0.62, 195, 290, 12), RAMPS['steel'][3], 1)
        L.forma(nombre + '_gema', ell(cx + r * 0.1, cy - 4, 2.6, 2.6, 10), RAMPS['blue'][3], outline=True)
        L.pix(nombre + '_gema_luz', [(cx + r * 0.1 - 1, cy - 5)], '#FFFFFF')
        for ang in (205, 240, 275, 310):
            x = cx + math.cos(math.radians(ang)) * r * 0.72; y = cy - 2 + math.sin(math.radians(ang)) * r * 0.62
            L.forma(nombre + '_remache', ell(x, y, 1.3, 1.3, 6), RAMPS['gold'][4])
    hombrera('hombrera_i', 60, 78, 16)
    hombrera('hombrera_d', 128, 74, 19)
    # ============================================================ BRAZO IZQUIERDO DEL ESPECTADOR + ESPADA (punta al suelo)
    L.pieza('hoja', [(40, 132), (50, 132), (52, 176), (45, 191), (38, 176)], 'steel', modo='cylx', rim=1, tono=-0.05)
    L.linea('hoja_canal', [(45, 134), (45, 184)], RAMPS['steel'][0], 1)
    L.linea('hoja_filo', [(41, 134), (40, 174)], RAMPS['steel'][4], 1)
    L.pieza('brazo_i_inf', [(52, 82), (66, 84), (58, 100), (46, 100)], 'dark', modo='cylx', spec=False)
    L.pieza('codo_i', ell(51, 99, 7, 7), 'gold', modo='round', rim=2)
    L.pieza('brazal_i', [(40, 100), (55, 100), (53, 113), (38, 113)], 'gold', modo='cylx', rim=2)
    L.forma('brazal_i_junta', [(39, 107), (54, 107), (54, 108), (39, 108)], RAMPS['gold'][0])
    L.pieza('pomo', ell(45, 104, 3.4, 3.4, 10), 'gold', modo='round', rim=1)
    L.pieza('guantelete', [(36, 110), (55, 110), (55, 125), (36, 125)], 'gold', modo='diag', rim=2)
    for x in (37, 42, 47, 52):
        L.forma('nudillo', [(x, 117), (x + 3, 117), (x + 3, 124), (x, 124)], RAMPS['gold'][1])
    L.pieza('guarda', [(26, 124), (64, 124), (68, 130), (46, 134), (22, 130)], 'gold', modo='cyly', rim=2)
    L.pieza('guarda_alas_i', [(26, 124), (20, 118), (20, 132), (28, 132)], 'gold', modo='diag', rim=1)
    L.pieza('guarda_alas_d', [(64, 124), (72, 118), (72, 132), (62, 132)], 'gold', modo='diag', rim=1)
    L.forma('guarda_gema', [(43, 126), (47, 126), (48, 131), (45, 134), (42, 131)], RAMPS['blue'][3], outline=True)
    L.pix('guarda_gema_luz', [(44, 128)], '#FFFFFF')
    # ============================================================ CABEZA: yelmo cerrado
    helm = [(80, 54), (78, 40), (84, 26), (96, 20), (108, 26), (114, 40), (112, 54), (108, 64), (96, 70), (84, 64)]
    L.pieza('yelmo', helm, 'gold', modo='round', rim=3, luz=(0.3, 0.25), sm=4)
    L.pieza('yelmo_cresta', [(94, 18), (98, 18), (99, 40), (93, 40)], 'gold', modo='cylx', rim=1, tono=-0.2)
    L.pieza('visera', [(80, 40), (112, 40), (112, 58), (104, 64), (96, 68), (88, 64), (80, 58)], 'gold', modo='cylx', rim=2, tono=0.1)
    L.forma('ranura', [(82, 43), (110, 43), (110, 47), (82, 47)], RAMPS['dark'][0])
    L.forma('ranura_luz', [(83, 47), (109, 47), (109, 48), (83, 48)], RAMPS['gold'][4])
    for x in (84, 89, 99, 104):
        L.forma('rejilla', [(x, 51), (x + 2, 51), (x + 2, 62), (x, 62)], RAMPS['dark'][0])
    L.pieza('nariz_cresta', [(94, 40), (98, 40), (99, 66), (95, 70), (93, 66)], 'gold', modo='cylx', rim=1, tono=-0.15)
    for (x, y) in ((82, 34), (110, 34), (80, 52), (112, 52)):
        L.forma('yelmo_remache', ell(x, y, 1.4, 1.4, 6), RAMPS['gold'][4])
    L.linea('yelmo_borde_luz', arco(96, 38, 16, 18, 200, 330, 14), RAMPS['steel'][3], 1)
    # ============================================================ PLUMA CARMESI
    mechones = [([(94, 24), (88, 6), (70, 0), (50, 8), (36, 26), (30, 50), (40, 42), (46, 28), (60, 18), (80, 18)], 0.0),
                ([(92, 30), (72, 20), (52, 26), (40, 46), (38, 68), (48, 56), (54, 42), (66, 34), (84, 34)], 0.12),
                ([(92, 34), (74, 34), (58, 44), (52, 64), (58, 78), (64, 62), (74, 50), (90, 44)], 0.26)]
    for i, (pp, tn) in enumerate(mechones):
        L.pieza('pluma%d' % i, pp, 'red', modo='diag', rim=2, spec=False, sm=3, tono=tn)
        L.linea('pluma_mecha%d' % i, [pp[1], pp[len(pp) // 2]], RAMPS['red'][4], 1)
    return L


def _cap(L, nombre, m, color):
    import numpy as np
    c = np.zeros((192, 192, 4), np.uint8)
    c[m] = hexrgb(color) + (255,)
    L._poner(nombre, c)


if __name__ == '__main__':
    L = dibujar()
    L.guardar(os.path.join(AQUI, 'paladin_3q_reposo.png'), os.path.join(AQUI, 'capas'))
    print('ok', len(L.capas), 'capas')
