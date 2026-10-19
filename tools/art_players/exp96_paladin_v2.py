#!/usr/bin/env python3
"""PRUEBA EXPERIMENTAL aislada (v2 heroica: adulto, hombros anchos, mandibula firme): Paladin del Alba a 96x96 (render vectorial a doble resolucion + detalle extra).
No toca el juego: escribe solo en tools/experimental/paladin96/. Uso: python3 tools/art_players/exp96_paladin.py"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import anims as AN
from kit import reset_mats, mat, mat_back
from rig import skeleton, simulate, Dims
from types import SimpleNamespace as NS
from common import *
from common import render_frame
import cls_paladin
import build_all as B

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'tools/experimental/paladin96')
CELL = (96, 96)
SCALE = 2.0
ORIGIN = (48, 88)          # pies (equivale al pivote 32,44 de la celda 64x48 a doble escala)


def tpw(X, uv, s=1.18):
    return tp(X, [(u * s, v) for u, v in uv])


class Paladin96(cls_paladin.Paladin):
    def setup(self):
        super().setup()
        self.D = Dims(k=1.06, hr=4.8, sw=1.6)       # cabeza algo menor y hombros mas anchos: proporcion adulta

    def fx(self, X, name, i, n):
        pass

    def init_mats(self):
        super().init_mats()
        mat('gem', '#E5485A', hl='#FFC0C8')
        mat('ink', '#1A1426')

    # ---------------------------------------------------------------- capa: 4 pliegues, filo de luz, ribete dorado y forro
    def _cape(self, X):
        pts = X.rb['cape']; ws = [w * X.D.k for w in X.cls.rib_by_name['cape'].widths]
        ribbons_draw(X, 'cape', 'blue_b', dome=2.6)
        nr = self._normals(pts)
        for f, m, tn, r in ((-0.55, 'blue_b', 4, 0.30), (-0.22, 'blue_b', 1, 0.34), (0.12, 'blue_b', 2, 0.30), (0.40, 'blue_b', 1, 0.34), (0.66, 'blue_b', 2, 0.26)):
            for i in range(1, len(pts) - 1):
                a = (pts[i][0] + nr[i][0] * ws[i] * f, pts[i][1] + nr[i][1] * ws[i] * f)
                b = (pts[i + 1][0] + nr[i + 1][0] * ws[i + 1] * f, pts[i + 1][1] + nr[i + 1][1] * ws[i + 1] * f)
                cap(X, a, b, r * X.D.k, r * 0.7 * X.D.k, m, tone=tn)
        i = len(pts) - 1
        a = (pts[i][0] + nr[i][0] * ws[i] * 0.95, pts[i][1] + nr[i][1] * ws[i] * 0.95)
        b = (pts[i][0] - nr[i][0] * ws[i] * 0.95, pts[i][1] - nr[i][1] * ws[i] * 0.95)
        cap(X, a, b, 0.55 * X.D.k, 0.55 * X.D.k, 'goldD', tone=3)
        cap(X, (a[0], a[1] - 0.5), (b[0], b[1] - 0.5), 0.2 * X.D.k, 0.2 * X.D.k, 'goldL', tone=5)
        # cierre dorado en el hombro
        s0 = pts[0]
        circ(X, s0, 0.9 * X.D.k, 'goldD', dome=1.0)
        circ(X, (s0[0] + 0.2, s0[1] - 0.2), 0.45 * X.D.k, 'goldL', tone=5)

    def draw(self, X):
        D, p, sk = X.D, X.p, X.sk
        k = D.k
        self._cape(X)
        # pierna trasera
        leg(X, sk.hipB, sk.kneeB, sk.ankB, 2.7, 2.2, 1.8, 'under_b', None, p.bfa, kneepad='gold_b', greave='gold_b')
        self._boot(X, sk.ankB, p.bfa, 'leather_b', 'goldD_b')
        # torso
        poly(X, tpw(X, [(-3.0, -0.6), (2.8, -0.6), (3.2, 3.5), (3.3, 7.6), (2.6, 9.6), (-2.4, 9.6), (-3.2, 7), (-3.3, 3)]), 'under', dome=3.0)
        # peto en tres placas con juntas, remaches y reflejo
        poly(X, tpw(X, [(-3.2, 6.0), (2.9, 6.0), (4.0, 7.0), (4.0, 8.4), (3.1, 10.0), (-2.5, 10.0), (-3.9, 8.2), (-3.9, 6.8)]), 'gold', dome=3.4)       # pecho
        poly(X, tpw(X, [(-3.3, 4.2), (3.0, 4.2), (3.7, 5.2), (3.7, 6.2), (-3.7, 6.2), (-3.7, 5.2)]), 'goldD', dome=1.6)                                 # placa media
        poly(X, tpw(X, [(-3.1, 2.9), (2.7, 2.9), (3.3, 3.8), (3.3, 4.4), (-3.4, 4.4), (-3.4, 3.8)]), 'gold', dome=1.4)                                   # placa baja
        for v in (6.1, 4.3):
            poly(X, tpw(X, [(-3.8, v - 0.12), (3.9, v - 0.12), (3.9, v + 0.12), (-3.8, v + 0.12)]), 'ink', tone=2)                                        # juntas
        poly(X, tpw(X, [(0.9, 6.4), (1.7, 6.4), (1.9, 9.6), (1.0, 9.6)]), 'goldL', tone=4)                                                                 # reflejo central
        poly(X, tpw(X, [(1.0, 6.6), (1.35, 6.6), (1.45, 9.4), (1.1, 9.4)]), 'goldL', tone=5)
        for (u, v) in ((-2.7, 5.2), (2.8, 5.2), (-2.8, 3.6), (2.6, 3.6)):                                                                                   # remaches
            circ(X, tpw(X, [(u, v)])[0], 0.28 * k, 'goldL', tone=5)
        # emblema solar grabado
        c = tpw(X, [(0.2, 8.0)])[0]
        circ(X, c, 0.8 * k, 'goldD', tone=2)
        circ(X, c, 0.4 * k, 'goldL', tone=5)
        # cinturon con hebilla y tachuelas
        poly(X, tpw(X, [(-3.3, 1.0), (3.3, 1.0), (3.3, 2.6), (-3.3, 2.6)]), 'leather', dome=1.2)
        poly(X, tpw(X, [(-3.3, 1.9), (3.3, 1.9), (3.3, 2.05), (-3.3, 2.05)]), 'ink', tone=2)
        poly(X, tpw(X, [(0.2, 0.8), (2.8, 0.8), (2.8, 2.8), (0.2, 2.8)]), 'goldD', dome=1.0)
        poly(X, tpw(X, [(0.5, 1.1), (2.5, 1.1), (2.5, 2.5), (0.5, 2.5)]), 'goldL', tone=4)
        poly(X, tpw(X, [(1.0, 1.5), (2.0, 1.5), (2.0, 2.1), (1.0, 2.1)]), 'ink', tone=2)
        for u in (-2.6, -1.6, -0.6):
            circ(X, tpw(X, [(u, 1.8)])[0], 0.2 * k, 'goldL', tone=5)
        poly(X, tpw(X, [(-3.3, 1.0), (-0.6, 1.0), (-0.8, -2.6), (-3.0, -2.0)]), 'gold_b', dome=1.4)
        # pierna delantera
        leg(X, sk.hipF, sk.kneeF, sk.ankF, 2.9, 2.3, 1.9, 'under', None, p.ffa, kneepad='goldL', greave='gold')
        self._boot(X, sk.ankF, p.ffa, 'leather', 'goldD')
        # tabardo con banda azul, ribete y pliegue
        poly(X, tpw(X, [(0.2, 1.5), (3.3, 1.5), (3.9, -1), (3.6, -4.8), (1.8, -5.8), (0.4, -4.8), (0.0, -1)]), 'cloth', dome=2.0)
        poly(X, tpw(X, [(0.9, 1.0), (2.3, 1.0), (2.2, -4.6), (1.5, -5.2), (0.9, -4.6)]), 'blue', tone=3)
        poly(X, tpw(X, [(1.1, 1.0), (1.45, 1.0), (1.4, -4.4), (1.1, -4.4)]), 'blue', tone=4)
        poly(X, tpw(X, [(0.2, -4.0), (3.7, -4.0), (3.5, -4.9), (1.8, -5.8), (0.4, -4.9)]), 'goldL', tone=3)
        poly(X, tpw(X, [(0.5, -4.1), (3.5, -4.1), (3.5, -4.25), (0.5, -4.25)]), 'goldD', tone=2)
        # gorjal en anillos
        n0 = lerp_pt(sk.neck, sk.hip, 0.0)
        circ(X, n0, 2.3 * k, 'steel', dome=1.6)
        circ(X, (n0[0] + 0.1, n0[1] - 0.45), 1.9 * k, 'steel', tone=4)
        poly(X, tpw(X, [(-2.4, 9.35), (2.6, 9.35), (2.6, 9.5), (-2.4, 9.5)]), 'ink', tone=2)
        # brazo trasero con escudo
        self._shield_arm(X)
        # hombrera de tres laminas con remaches
        for dy, r, m in ((2.4, 3.8, 'goldD'), (1.5, 3.7, 'gold'), (0.7, 3.6, 'gold')):
            circ(X, (sk.shF[0] - 0.2 * (dy > 1), sk.shF[1] + dy), r * k, m, dome=2.6)
        circ(X, (sk.shF[0] + 0.5, sk.shF[1] - 0.2), 1.9 * k, 'goldL', dome=1.8)
        circ(X, (sk.shF[0] + 1.0, sk.shF[1] - 0.7), 0.55 * k, 'cloth', tone=5)
        for dy in (2.2, 1.1):
            circ(X, (sk.shF[0] - 2.4, sk.shF[1] + dy + 0.5), 0.3 * k, 'goldL', tone=5)
        # cabeza
        hc = sk.head
        circ(X, hc, D.hr, 'gold', dome=3.6)
        # cara de adulto: frente firme, mandibula ancha y cuadrada, menton marcado, nariz recta
        poly(X, hp(X, [(0.4, 2.3), (4.9, 2.0), (5.5, -0.4), (5.7, -3.2), (4.9, -4.7), (1.4, -4.9), (0.4, -2.0)]), 'skin', dome=1.3)
        poly(X, hp(X, [(1.0, -2.3), (5.6, -2.3), (5.7, -3.3), (4.9, -4.7), (1.4, -4.9)]), 'skin', tone=2)                      # mandibula en sombra
        poly(X, hp(X, [(1.6, -3.6), (5.0, -3.6), (4.9, -4.7), (1.5, -4.9)]), 'skin', tone=1)                                   # barba corta (sombra de barba)
        poly(X, hp(X, [(4.5, -3.0), (5.5, -3.0), (5.4, -3.6), (4.6, -3.6)]), 'skin', tone=4)                                   # menton iluminado
        poly(X, hp(X, [(0.4, 2.3), (4.9, 2.0), (5.1, 0.8), (0.4, 0.8)]), 'skin', tone=3)                                       # frente plana (sin brillo infantil)
        poly(X, hp(X, [(0.4, -0.6), (4.4, -0.9), (4.6, -2.3), (0.6, -2.4)]), 'skin', tone=3)                                    # mejilla de tono medio
        poly(X, hp(X, [(4.0, 0.5), (5.2, 0.5), (5.6, -0.6), (4.4, -0.8)]), 'skin', tone=4)                                     # pomulo
        poly(X, hp(X, [(5.2, 0.6), (5.9, -0.4), (5.9, -1.2), (5.2, -1.1)]), 'skin', tone=4)                                    # punta de la nariz
        poly(X, hp(X, [(5.0, 0.7), (5.4, 0.7), (5.4, -0.9), (5.0, -0.9)]), 'skin', tone=3)                                      # puente
        poly(X, hp(X, [(5.0, -1.1), (5.9, -1.2), (5.6, -1.7), (5.0, -1.6)]), 'skin', tone=1)                                   # fosa nasal en sombra
        # ceja gruesa y decidida, inclinada hacia la nariz; mirada fija
        poly(X, hp(X, [(2.3, 2.6), (5.3, 1.6), (5.4, 0.75), (2.3, 1.6)]), 'hair', tone=1)
        poly(X, hp(X, [(2.7, 2.4), (4.8, 1.6), (4.8, 1.45), (2.7, 2.1)]), 'hair', tone=3)
        poly(X, hp(X, [(3.1, 1.0), (4.9, 0.7), (4.9, -0.4), (3.1, -0.4)]), 'cloth', tone=3)                                    # esclerotica (ojo mas estrecho)
        poly(X, hp(X, [(3.9, 1.0), (4.9, 0.8), (4.9, -0.4), (3.9, -0.4)]), 'eye', tone=2)                                      # iris
        poly(X, hp(X, [(4.2, 0.8), (4.8, 0.7), (4.8, -0.3), (4.2, -0.3)]), 'ink', tone=2)                                      # pupila
        poly(X, hp(X, [(2.7, 1.25), (5.0, 0.95), (5.0, 0.7), (2.7, 1.0)]), 'ink', tone=2)                                      # parpado pesado
        poly(X, hp(X, [(2.9, -0.55), (4.8, -0.65), (4.8, -0.85), (2.9, -0.75)]), 'skin', tone=1)                               # bolsa del ojo
        poly(X, hp(X, [(3.4, -2.7), (5.2, -2.7), (5.2, -3.05), (3.4, -3.05)]), 'ink', tone=3)                                  # boca firme
        poly(X, hp(X, [(3.4, -3.05), (5.0, -3.05), (5.0, -3.3), (3.4, -3.3)]), 'skin', tone=2)
        # yelmo
        poly(X, hp(X, [(-5.0, 1.4), (-2.4, 5.3), (2.2, 5.5), (5.2, 2.7), (4.9, 2.0), (0.6, 2.4), (-1.0, 0.6)]), 'gold', dome=2.4)
        poly(X, hp(X, [(-3.8, 3.2), (-1.0, 5.6), (3.2, 5.6), (4.8, 3.3), (3.0, 3.9), (-1.0, 4.1)]), 'goldL', dome=1.5)
        for u in (-2.4, -0.8, 0.8, 2.4):                                                                  # segmentos de la cresta
            poly(X, hp(X, [(u, 5.6), (u + 0.18, 5.6), (u + 0.18, 3.7), (u, 3.7)]), 'goldD', tone=2)
        poly(X, hp(X, [(0.6, 2.4), (5.0, 2.0), (5.1, 1.8), (0.6, 2.2)]), 'ink', tone=2)                  # sombra bajo el borde
        for u in (-1.6, 0.0, 1.6, 3.2):                                                                   # remaches del borde
            circ(X, hpt(X, u, 2.9), 0.26 * k, 'cloth', tone=5)
        poly(X, hp(X, [(4.6, 3.0), (5.4, 2.6), (5.1, 0.6), (4.5, 0.8)]), 'goldL', tone=4)                # barra nasal
        poly(X, hp(X, [(4.95, 2.7), (5.2, 2.6), (5.0, 0.9), (4.8, 0.95)]), 'cloth', tone=5)
        # cabello: nuca con mechones y patilla
        poly(X, hp(X, [(-4.8, 1.0), (-0.8, 0.8), (-0.4, -2.6), (-2.4, -3.8), (-4.4, -2.4)]), 'hair', dome=1.4)
        for (a, b, tn) in (((-4.2, 0.6), (-3.4, -3.0), 5), ((-3.1, 0.4), (-2.5, -3.4), 4), ((-2.0, 0.3), (-1.4, -3.0), 5), ((-0.9, 0.2), (-0.6, -2.4), 4)):
            cap(X, hpt(X, *a), hpt(X, *b), 0.26 * k, 0.12 * k, 'hair', tone=tn)
        poly(X, hp(X, [(0.0, 1.4), (1.2, 1.4), (1.5, -3.4), (0.4, -3.6)]), 'hair', tone=3)           # patilla larga hasta la mandibula
        poly(X, hp(X, [(0.2, 1.2), (0.7, 1.2), (0.9, -3.0), (0.4, -3.0)]), 'hair', tone=5)
        # guarda de mejilla
        poly(X, hp(X, [(-1.8, 0.4), (0.3, 0.6), (0.9, -1.5), (0.0, -3.6), (-1.6, -3.2)]), 'goldD', dome=1.6)
        circ(X, hpt(X, -0.3, -0.6), 0.28 * k, 'goldL', tone=5)
        ribbons_draw(X, 'plume', 'plume', dome=1.6)
        # brazo delantero: manga, brazal con bandas, guantelete con nudillos
        arm(X, sk.shF, sk.elbF, sk.handF, 2.2, 1.95, 1.65, 'under', glove='leather', bracer='gold', hand_r=1.9)
        e, h = sk.elbF, sk.handF
        for t in (0.5, 0.64, 0.78):
            q = (e[0] * (1 - t) + h[0] * t, e[1] * (1 - t) + h[1] * t)
            circ(X, q, 0.55 * k, 'goldL', tone=4)
        circ(X, h, 1.95 * k, 'leather', dome=1.6)
        circ(X, (h[0] - 0.2, h[1] - 0.9), 1.2 * k, 'leather', tone=4)
        for dx in (-0.7, 0.0, 0.7):
            circ(X, (h[0] + dx + 0.3, h[1] - 0.9), 0.26 * k, 'goldD', tone=4)
        self._sword(X)

    def _boot(self, X, ank, pitch, m, mc):
        a = math.radians(pitch); f = (math.cos(a), math.sin(a)); n = (-f[1], f[0]); k = X.D.k
        heel = (ank[0] - f[0] * 1.8 * k + n[0] * 0.9 * k, ank[1] - f[1] * 1.8 * k + n[1] * 0.9 * k)
        toe = (ank[0] + f[0] * 3.3 * k + n[0] * 0.7 * k, ank[1] + f[1] * 3.3 * k + n[1] * 0.7 * k)
        top = (ank[0] - n[0] * 2.6 * k, ank[1] - n[1] * 2.6 * k)
        X.cv.add([('l', heel, toe, 1.6 * k, 1.25 * k), ('l', top, ank, 1.85 * k, 1.85 * k)], m, dome=2.2)
        cuff = (ank[0] - n[0] * 2.5 * k, ank[1] - n[1] * 2.5 * k)
        X.cv.add([('l', (cuff[0] - f[0] * 1.6 * k, cuff[1] - f[1] * 1.6 * k), (cuff[0] + f[0] * 1.6 * k, cuff[1] + f[1] * 1.6 * k), 0.9 * k, 0.9 * k)], mc, dome=1.2)
        tc = (toe[0] - f[0] * 0.2 * k, toe[1] - f[1] * 0.2 * k)
        circ(X, tc, 0.85 * k, mc, tone=3)
        circ(X, (tc[0] - 0.2, tc[1] - 0.4), 0.45 * k, mc, tone=5)

    def _shield_arm(self, X):
        p, sk, k = X.p, X.sk, X.D.k
        arm(X, sk.shB, sk.elbB, sk.handB, 1.6, 1.45, 1.3, 'under_b', glove='leather_b', bracer='gold_b')
        circ(X, sk.shB, 2.5 * k, 'gold_b', dome=2.4)
        h = sk.handB
        ctr = (h[0] + 1.6 * k, h[1] - 0.2)
        def sp(pts, s=1.0):
            return [(ctr[0] + x * s * k, ctr[1] + y * s * k) for x, y in pts]
        outer = [(-4.3, -6.4), (4.3, -6.4), (4.5, 0.2), (0, 7.4), (-4.5, 0.2)]
        poly(X, sp(outer), 'goldD', dome=2.4)
        poly(X, sp(outer, 0.86), 'gold', dome=2.0)
        poly(X, sp(outer, 0.76), 'goldL', tone=4)                                                   # filo de luz del reborde
        poly(X, sp(outer, 0.72), 'gold', tone=2)
        poly(X, sp([(-3.1, -4.8), (0, -4.8), (0, 5.0), (-3.3, 0.0)]), 'blue', tone=4)
        poly(X, sp([(0, -4.8), (3.1, -4.8), (3.3, 0.0), (0, 5.0)]), 'blue', tone=2)
        poly(X, sp([(-3.1, -4.8), (-2.0, -4.8), (-2.2, 0.4), (-3.3, 0.0)]), 'blue', tone=5)       # brillo en el borde iluminado
        c = sp([(0, -0.9)])[0]
        for ang in range(0, 360, 45):                                                               # sol de 8 rayos
            a = math.radians(ang)
            long = ang % 90 == 0
            cap(X, c, (c[0] + math.cos(a) * (3.5 if long else 2.5) * k, c[1] + math.sin(a) * (3.5 if long else 2.5) * k),
                (0.5 if long else 0.38) * k, 0.08 * k, 'goldL', tone=5 if long else 4)
        circ(X, c, 1.5 * k, 'goldD', tone=3)
        circ(X, c, 1.2 * k, 'goldL', tone=4)
        circ(X, c, 0.6 * k, 'cloth', tone=5)
        for (x, y) in ((-3.5, -5.5), (3.5, -5.5), (-3.9, -0.6), (3.9, -0.6), (0, 6.3)):             # remaches del reborde
            circ(X, sp([(x, y)])[0], 0.28 * k, 'cloth', tone=5)

    def _sword(self, X):
        W = lambda pts: wpoly(X, pts)
        poly(X, W([(2.2, -1.6), (17.0, -1.7), (21.0, 0), (17.0, 1.7), (2.2, 1.6)]), 'steel', tone=3)
        poly(X, W([(2.2, -1.6), (17.0, -1.7), (21.0, 0), (3.0, -0.1)]), 'steel', tone=5)
        poly(X, W([(3.0, 0.1), (21.0, 0), (17.0, 1.7), (2.2, 1.6)]), 'steel', tone=2)
        poly(X, W([(3.4, -0.3), (18.0, -0.3), (18.0, 0.3), (3.4, 0.3)]), 'steel', tone=1)             # canal
        poly(X, W([(3.4, -0.9), (17.0, -1.0), (17.0, -0.8), (3.4, -0.7)]), 'steel', tone=5)           # filo superior
        poly(X, W([(3.4, 1.0), (17.0, 1.1), (17.0, 0.9), (3.4, 0.8)]), 'steel', tone=1)               # filo inferior en sombra
        poly(X, W([(17.5, -0.6), (20.6, 0), (17.5, 0.2)]), 'steel', tone=5)                            # punta brillante
        poly(X, W([(1.2, -4.8), (2.9, -3.4), (2.9, 3.4), (1.2, 4.8), (0.6, 3.4), (0.6, -3.4)]), 'gold', dome=1.6)
        poly(X, W([(1.0, -4.8), (1.8, -4.8), (1.8, -3.0), (1.0, -3.0)]), 'goldL', tone=5)
        poly(X, W([(1.0, 3.0), (1.8, 3.0), (1.8, 4.8), (1.0, 4.8)]), 'goldD', tone=2)
        circ(X, wpt(X, 1.9, 0), 0.9 * X.D.k, 'goldD', tone=3)
        circ(X, wpt(X, 1.9, 0), 0.62 * X.D.k, 'gem', tone=3)
        circ(X, wpt(X, 1.8, -0.2), 0.22 * X.D.k, 'gem', tone=5)
        poly(X, W([(-2.4, -0.95), (0.6, -0.95), (0.6, 0.95), (-2.4, 0.95)]), 'leather', dome=1.0)
        for u in (-2.0, -1.3, -0.6):                                                                    # vendas
            poly(X, W([(u, -1.0), (u + 0.25, -1.0), (u + 0.25, 1.0), (u, 1.0)]), 'goldD', tone=3)
        circ(X, wpt(X, -3.3, 0), 1.35 * X.D.k, 'goldD', dome=1.2)
        circ(X, wpt(X, -3.3, 0), 0.8 * X.D.k, 'goldL', tone=4)
        circ(X, wpt(X, -3.4, -0.2), 0.3 * X.D.k, 'cloth', tone=5)


def render(cls, name, idx):
    seq = cls.seq(name); n = AN.N[name]; loop = AN.LOOP.get(name, False)
    rb = simulate(cls.ribbons, seq.at, lambda p: skeleton(p, cls.D), n, loop=loop)
    hit = cls.attacks[name][1] if name in cls.attacks else None
    out = []
    for i in idx:
        p0 = seq.at(i); pz = NS(**vars(p0)); pz.lean = p0.lean * 0.55 - 1.0; pz.hd = getattr(p0, 'hd', 0) * 0.6 + 2.0   # erguido, pecho abierto, mirada al frente
        tr = (lambda X, i=i: cls.trail_draw(X, seq, i, hit)) if hit else None
        out.append(Image.fromarray(render_frame(cls, seq, rb, i, n, name, trail=tr, size=CELL, S=4, scale=SCALE, origin=ORIGIN, pose=pz), 'RGBA'))
    return out, n


def main():
    os.makedirs(OUT, exist_ok=True)
    reset_mats()
    cls = Paladin96(); cls.init_mats()
    plan = [('idle', None), ('run', None), ('attack1', None), ('roll', None)]
    sheet_rows = []
    for name, idx in plan:
        n = AN.N[name]
        fr, _ = render(cls, name, list(range(n)) if idx is None else idx)
        sheet_rows.append((name, fr))
    W = max(len(f) for _, f in sheet_rows) * CELL[0]
    sheet = Image.new('RGBA', (W, CELL[1] * len(sheet_rows)), (0, 0, 0, 0))
    for r, (name, fr) in enumerate(sheet_rows):
        for i, f in enumerate(fr):
            sheet.paste(f, (i * CELL[0], r * CELL[1]))
    sheet.save(os.path.join(OUT, 'paladin96_heroico_sheet.png'))
    import json
    json.dump({'cell': list(CELL), 'rows': [n for n, _ in sheet_rows], 'frames': {n: len(f) for n, f in sheet_rows}, 'note': 'EXPERIMENTAL: no usado por el juego'},
              open(os.path.join(OUT, 'paladin96_heroico_sheet.json'), 'w'), indent=1)
    print('ok', sheet.size)


if __name__ == '__main__':
    main()
