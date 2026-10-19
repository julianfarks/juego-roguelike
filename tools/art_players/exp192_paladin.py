#!/usr/bin/env python3
"""PRUEBA EXPERIMENTAL aislada (v4 yelmo cerrado): Paladin del Alba a 96x96 (render vectorial a doble resolucion + detalle extra).
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
CELL = (192, 192)
SCALE = 4.0
ORIGIN = (96, 178)


class Paladin96(cls_paladin.Paladin):
    def setup(self):
        super().setup()
        self.D = Dims(k=1.06, hr=4.8, sw=1.4)       # hombros firmes sin exagerar, cabeza proporcionada

    def fx(self, X, name, i, n):
        pass

    def init_mats(self):
        super().init_mats()
        mat('gem', '#E5485A', hl='#FFC0C8')
        mat('ink', '#1A1426')

    # ---------------------------------------------------------------- detalle de alta resolucion (192x192)
    @staticmethod
    def _lt(a, b, off):
        """segmento a-b desplazado off hacia el lado iluminado (arriba-izquierda; y crece hacia abajo en pantalla)."""
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        if nx * -1 + ny * -1 < 0:
            nx, ny = -nx, -ny
        return (a[0] + nx * off, a[1] + ny * off), (b[0] + nx * off, b[1] + ny * off)

    def _across(self, X, a, b, t, w, m, tone, r=0.16):
        c = lerp_pt(a, b, t); dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        cap(X, (c[0] + nx * w, c[1] + ny * w), (c[0] - nx * w, c[1] - ny * w), r * X.D.k, r * X.D.k, m, tone=tone)

    def _leg_detail(self, X):
        k = X.D.k; sk = X.sk
        hip, kn, an = sk.hipF, sk.kneeF, sk.ankF
        # cuisse: placa del muslo con filo de luz, juntas y reborde inferior
        a, b = lerp_pt(hip, kn, 0.10), lerp_pt(hip, kn, 0.90)
        cap(X, a, b, 2.65 * k, 2.2 * k, 'gold', dome=2.0)
        la, lb = self._lt(a, b, -1.35 * k)
        cap(X, la, lb, 0.22 * k, 0.2 * k, 'goldL', tone=5)
        la, lb = self._lt(a, b, 1.2 * k)
        cap(X, la, lb, 0.3 * k, 0.26 * k, 'goldD', tone=1)
        for t in (0.34, 0.62):
            self._across(X, a, b, t, 1.8 * k, 'ink', 2)
        self._across(X, a, b, 0.9, 2.0 * k, 'goldL', 4, 0.2)
        # rodillera con alas y gema
        circ(X, kn, 2.9 * k, 'goldD', dome=1.8)
        circ(X, kn, 2.45 * k, 'goldL', dome=1.8)
        circ(X, (kn[0] - 0.5, kn[1] - 0.6), 1.0 * k, 'cloth', tone=5)
        circ(X, kn, 1.0 * k, 'gem', tone=3)
        circ(X, (kn[0] - 0.2, kn[1] - 0.3), 0.35 * k, 'cloth', tone=5)
        poly(X, [(kn[0] - 0.4 * k, kn[1] - 2.2 * k), (kn[0] - 3.4 * k, kn[1] - 3.4 * k), (kn[0] - 2.3 * k, kn[1] - 0.6 * k)], 'goldL', tone=3)
        # greba: cresta central, juntas y borde
        a, b = lerp_pt(kn, an, 0.18), lerp_pt(kn, an, 0.92)
        cap(X, a, b, 2.35 * k, 1.95 * k, 'gold', dome=2.0)
        la, lb = self._lt(a, b, -0.9 * k)
        cap(X, la, lb, 0.3 * k, 0.26 * k, 'goldL', tone=5)
        la, lb = self._lt(a, b, 1.0 * k)
        cap(X, la, lb, 0.34 * k, 0.28 * k, 'goldD', tone=1)
        for t in (0.35, 0.65):
            self._across(X, a, b, t, 1.45 * k, 'ink', 2)
        self._across(X, a, b, 0.93, 1.5 * k, 'goldL', 4, 0.2)
        # tobillo y puntera acorazada
        circ(X, an, 1.9 * k, 'goldD', dome=1.6)
        circ(X, (an[0] - 0.3, an[1] - 0.4), 0.7 * k, 'goldL', tone=5)
        f = (math.cos(math.radians(X.p.ffa)), math.sin(math.radians(X.p.ffa)))
        t0 = (an[0] + f[0] * 1.6 * k, an[1] + f[1] * 1.6 * k); t1 = (an[0] + f[0] * 3.5 * k, an[1] + f[1] * 3.5 * k)
        cap(X, t0, t1, 1.35 * k, 1.2 * k, 'gold', dome=1.8)
        la, lb = self._lt(t0, t1, -0.7 * k)
        cap(X, la, lb, 0.2 * k, 0.18 * k, 'goldL', tone=5)
        self._across(X, t0, t1, 0.0, 1.0 * k, 'ink', 2, 0.14)

    def _torso_detail(self, X):
        k = X.D.k
        # filo claro en el borde superior de cada placa del peto y grabado solar
        for (v, w) in ((10.0, 3.2), (6.2, 3.7), (4.5, 3.3)):
            a, b = tp(X, [(-w + 0.4, v - 0.1), (w - 0.6, v - 0.1)])
            cap(X, a, b, 0.2 * k, 0.2 * k, 'goldL', tone=5)
        for (u, v) in ((-1.8, 8.2), (1.4, 9.0), (-1.2, 7.0), (2.2, 7.4)):
            q = tp(X, [(u, v)])[0]
            circ(X, q, 0.2 * k, 'goldD', tone=2)
        a, b = tp(X, [(-2.4, 8.6), (2.6, 8.6)]); cap(X, a, b, 0.14 * k, 0.14 * k, 'goldD', tone=2)
        a, b = tp(X, [(-2.2, 7.4), (2.4, 7.4)]); cap(X, a, b, 0.12 * k, 0.12 * k, 'goldD', tone=2)
        # reborde plateado de las placas
        a, b = tp(X, [(-3.8, 8.4), (-2.6, 9.8)]); cap(X, a, b, 0.16 * k, 0.16 * k, 'cloth', tone=4)

    def _pauldron_detail(self, X):
        k = X.D.k; sk = X.sk
        for dy, r in ((2.5, 3.0), (1.0, 3.4), (0.1, 3.3)):
            cx, cy = sk.shF[0] - 0.2, sk.shF[1] + dy
            prev = None
            for ang in range(200, 305, 15):
                q = (cx + math.cos(math.radians(ang)) * r * k, cy + math.sin(math.radians(ang)) * r * k)
                if prev: cap(X, prev, q, 0.2 * k, 0.2 * k, 'cloth', tone=4)
                prev = q
        for ang in (215, 250, 285):
            q = (sk.shF[0] + math.cos(math.radians(ang)) * 2.9 * k, sk.shF[1] + 0.4 + math.sin(math.radians(ang)) * 2.9 * k)
            circ(X, q, 0.4 * k, 'goldL', tone=5)
        circ(X, (sk.shF[0] + 0.3, sk.shF[1] - 0.2), 0.9 * k, 'gem', tone=3)
        circ(X, (sk.shF[0] + 0.1, sk.shF[1] - 0.45), 0.3 * k, 'cloth', tone=5)

    def _cape_detail(self, X):
        pts = X.rb['cape']; ws = [w * X.D.k for w in X.cls.rib_by_name['cape'].widths]
        nr = self._normals(pts)
        for i in range(2, len(pts) - 1, 2):
            for f in ((-0.28 if i % 4 else 0.3),):
                c = (pts[i][0] + nr[i][0] * ws[i] * f, pts[i][1] + nr[i][1] * ws[i] * f)
                r = 0.7 * X.D.k
                poly(X, [(c[0], c[1] - r), (c[0] + r * 0.3, c[1] - r * 0.3), (c[0] + r, c[1]), (c[0] + r * 0.3, c[1] + r * 0.3), (c[0], c[1] + r),
                         (c[0] - r * 0.3, c[1] + r * 0.3), (c[0] - r, c[1]), (c[0] - r * 0.3, c[1] - r * 0.3)], 'goldL', tone=3)
        for i in range(1, len(pts) - 2):                                    # rama dorada a lo largo del pliegue
            a = (pts[i][0] + nr[i][0] * ws[i] * 0.52, pts[i][1] + nr[i][1] * ws[i] * 0.52)
            b = (pts[i + 1][0] + nr[i + 1][0] * ws[i + 1] * 0.52, pts[i + 1][1] + nr[i + 1][1] * ws[i + 1] * 0.52)
            cap(X, a, b, 0.1 * X.D.k, 0.1 * X.D.k, 'goldD', tone=3)

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
        self._cape_detail(X)
        # cierre dorado en el hombro
        s0 = pts[0]
        circ(X, s0, 0.9 * X.D.k, 'goldD', dome=1.0)
        circ(X, (s0[0] + 0.2, s0[1] - 0.2), 0.45 * X.D.k, 'goldL', tone=5)

    def draw(self, X):
        D, p, sk = X.D, X.p, X.sk
        k = D.k
        self._cape(X)
        # pierna trasera
        leg(X, sk.hipB, sk.kneeB, sk.ankB, 2.2, 1.8, 1.5, 'under_b', 'leather_b', p.bfa, kneepad='gold_b', greave='gold_b')
        # torso
        poly(X, tp(X, [(-2.7, -0.6), (2.6, -0.6), (2.7, 2.5), (3.4, 5.0), (3.6, 7.6), (2.8, 9.6), (-2.4, 9.6), (-3.4, 7.0), (-3.0, 4.0), (-2.6, 2.0)]), 'under', dome=3.0)
        # peto en tres placas con juntas, remaches y reflejo
        poly(X, tp(X, [(-3.2, 6.0), (3.0, 6.0), (4.2, 7.0), (4.2, 8.5), (3.2, 10.0), (-2.5, 10.0), (-4.1, 8.3), (-4.0, 6.8)]), 'gold', dome=3.4)       # pecho
        poly(X, tp(X, [(-2.9, 4.2), (2.7, 4.2), (3.4, 5.2), (3.6, 6.2), (-3.6, 6.2), (-3.4, 5.2)]), 'goldD', dome=1.6)                                 # placa media
        poly(X, tp(X, [(-2.6, 2.9), (2.4, 2.9), (2.9, 3.8), (3.0, 4.4), (-3.0, 4.4), (-2.9, 3.8)]), 'gold', dome=1.4)                                   # placa baja
        for v in (6.1, 4.3):
            poly(X, tp(X, [(-3.8, v - 0.12), (3.9, v - 0.12), (3.9, v + 0.12), (-3.8, v + 0.12)]), 'ink', tone=2)                                        # juntas
        poly(X, tp(X, [(0.9, 6.4), (1.7, 6.4), (1.9, 9.6), (1.0, 9.6)]), 'goldL', tone=4)                                                                 # reflejo central
        poly(X, tp(X, [(1.0, 6.6), (1.35, 6.6), (1.45, 9.4), (1.1, 9.4)]), 'goldL', tone=5)
        for (u, v) in ((-2.7, 5.2), (2.8, 5.2), (-2.8, 3.6), (2.6, 3.6)):                                                                                   # remaches
            circ(X, tp(X, [(u, v)])[0], 0.28 * k, 'goldL', tone=5)
        # emblema solar grabado
        c = tp(X, [(0.2, 8.0)])[0]
        circ(X, c, 0.8 * k, 'goldD', tone=2)
        circ(X, c, 0.4 * k, 'goldL', tone=5)
        # cinturon con hebilla y tachuelas
        poly(X, tp(X, [(-2.8, 1.0), (2.8, 1.0), (2.8, 2.6), (-2.8, 2.6)]), 'leather', dome=1.2)
        poly(X, tp(X, [(-2.8, 1.9), (2.8, 1.9), (2.8, 2.05), (-2.8, 2.05)]), 'ink', tone=2)
        poly(X, tp(X, [(0.2, 0.8), (2.8, 0.8), (2.8, 2.8), (0.2, 2.8)]), 'goldD', dome=1.0)
        poly(X, tp(X, [(0.5, 1.1), (2.5, 1.1), (2.5, 2.5), (0.5, 2.5)]), 'goldL', tone=4)
        poly(X, tp(X, [(1.0, 1.5), (2.0, 1.5), (2.0, 2.1), (1.0, 2.1)]), 'ink', tone=2)
        for u in (-2.6, -1.6, -0.6):
            circ(X, tp(X, [(u, 1.8)])[0], 0.2 * k, 'goldL', tone=5)
        poly(X, tp(X, [(-2.8, 1.0), (-0.6, 1.0), (-0.8, -2.6), (-2.6, -2.0)]), 'gold_b', dome=1.4)
        # pierna delantera
        leg(X, sk.hipF, sk.kneeF, sk.ankF, 2.4, 1.9, 1.6, 'dark', 'leather', p.ffa, kneepad='goldL', greave='gold')
        self._leg_detail(X)
        # tabardo con banda azul, ribete y pliegue
        poly(X, tp(X, [(0.2, 1.5), (2.9, 1.5), (3.4, -1), (3.2, -4.8), (1.7, -5.8), (0.4, -4.8), (0.0, -1)]), 'blue', dome=2.0)
        poly(X, tp(X, [(0.9, 1.0), (2.3, 1.0), (2.2, -4.6), (1.5, -5.2), (0.9, -4.6)]), 'cloth', tone=4)
        poly(X, tp(X, [(1.1, 1.0), (1.45, 1.0), (1.4, -4.4), (1.1, -4.4)]), 'cloth', tone=5)
        circ(X, tp(X, [(1.6, -2.2)])[0], 0.55 * k, 'goldL', tone=4)
        circ(X, tp(X, [(1.6, -2.2)])[0], 0.25 * k, 'blue', tone=2)
        poly(X, tp(X, [(0.2, -4.0), (3.3, -4.0), (3.1, -4.9), (1.7, -5.8), (0.4, -4.9)]), 'goldL', tone=3)
        poly(X, tp(X, [(0.5, -4.1), (3.1, -4.1), (3.1, -4.25), (0.5, -4.25)]), 'goldD', tone=2)
        self._torso_detail(X)
        # gorjal en anillos
        n0 = lerp_pt(sk.neck, sk.hip, 0.0)
        circ(X, n0, 2.3 * k, 'steel', dome=1.6)
        circ(X, (n0[0] + 0.1, n0[1] - 0.45), 1.9 * k, 'steel', tone=4)
        poly(X, tp(X, [(-2.4, 9.35), (2.6, 9.35), (2.6, 9.5), (-2.4, 9.5)]), 'ink', tone=2)
        # brazo trasero con escudo
        self._shield_arm(X)
        # cabeza
        hc = sk.head
        circ(X, hc, D.hr, 'gold', dome=3.6)
        # YELMO CERRADO (sin cara visible): casco de torneo con visera, ranura de ojos, ventilas y cresta
        poly(X, hp(X, [(-5.2, 1.0), (-4.6, 4.2), (-2.4, 5.8), (1.6, 6.0), (4.6, 4.4), (5.6, 1.6), (5.7, -1.4), (5.0, -3.4), (3.4, -4.6), (-0.8, -4.7), (-3.6, -4.0), (-5.3, -2.2)]), 'gold', dome=3.0)
        poly(X, hp(X, [(-4.4, 3.8), (-2.2, 5.6), (1.6, 5.8), (3.8, 4.8), (1.2, 4.6), (-2.0, 4.4)]), 'goldL', dome=1.4)               # luz de la bóveda
        poly(X, hp(X, [(-1.0, 6.0), (0.5, 6.0), (0.9, 4.2), (-0.8, 4.2)]), 'goldL', tone=4)                                                  # cresta central
        poly(X, hp(X, [(-5.3, -0.2), (-0.6, -0.2), (-0.8, -4.7), (-3.6, -4.0), (-5.3, -2.2)]), 'goldD', dome=1.6)                           # nuca / babera trasera
        poly(X, hp(X, [(0.0, 3.0), (5.6, 2.2), (5.7, 1.8), (0.0, 2.5)]), 'goldL', tone=4)                                                    # ceja de la visera (filo de luz)
        poly(X, hp(X, [(0.2, 2.6), (5.7, 1.8), (5.8, 0.4), (0.2, 0.9)]), 'gold', dome=1.8)                                                  # banda de la visera (sombra)
        poly(X, hp(X, [(1.0, 2.0), (5.9, 1.3), (5.9, 0.5), (1.0, 1.1)]), 'ink', tone=1)                                                    # RANURA DE OJOS (oscura, sin cara)
        poly(X, hp(X, [(1.4, 1.25), (5.8, 0.65), (5.8, 0.5), (1.4, 1.1)]), 'ink', tone=2)
        poly(X, hp(X, [(0.2, 0.9), (5.8, 0.3), (5.7, -0.1), (0.2, 0.4)]), 'goldL', tone=3)                                                   # labio inferior de la ranura
        poly(X, hp(X, [(2.6, 5.2), (3.5, 4.3), (3.2, 2.2), (2.3, 2.6)]), 'goldL', tone=3)                                                    # nervio frontal
        poly(X, hp(X, [(1.4, 0.2), (5.6, -0.2), (5.7, -3.4), (4.6, -4.4), (1.8, -4.5), (0.8, -3.0)]), 'goldL', dome=2.4)                       # barbote (mentón)
        poly(X, hp(X, [(3.3, -0.6), (3.9, -0.7), (3.9, -3.7), (3.3, -3.6)]), 'goldL', tone=5)                                                # arista vertical del barbote
        for u in (2.7, 3.7, 4.7):                                                                                                            # rejilla vertical de la visera
            poly(X, hp(X, [(u, 0.9), (u + 0.38, 0.9), (u + 0.38, -3.4), (u, -3.4)]), 'ink', tone=1)
            poly(X, hp(X, [(u - 0.28, 0.5), (u, 0.5), (u, -3.2), (u - 0.28, -3.2)]), 'goldL', tone=5)
        poly(X, hp(X, [(5.6, 1.6), (6.4, 0.0), (6.1, -2.4), (5.6, -3.2)]), 'goldL', tone=3)                                                  # proa de la visera (perfil puntiagudo)
        poly(X, hp(X, [(1.4, -3.9), (4.8, -4.3), (4.7, -4.6), (1.4, -4.2)]), 'goldD', tone=1)                                                # sombra del gorjal
        poly(X, hp(X, [(0.6, 0.0), (1.2, 0.0), (1.4, -3.8), (0.7, -3.6)]), 'goldD', tone=1)                                                  # junta mejilla
        for (u, v) in ((-3.8, 1.6), (-2.2, 2.0), (-0.6, 2.4), (1.0, 2.6), (-3.2, -1.8), (-1.6, -2.6)):                                        # remaches
            circ(X, hpt(X, u, v), 0.3 * k, 'goldL', tone=5)
        circ(X, hpt(X, -0.6, 0.0), 0.5 * k, 'cloth', tone=5)                                                                                 # joya lateral
        poly(X, hp(X, [(-5.3, 1.0), (-4.9, 0.2), (-0.3, 0.2), (-0.2, 0.0), (-5.3, -0.1)]), 'goldL', tone=3)                                  # reborde dorado
        poly(X, hp(X, [(-5.3, -2.2), (-3.6, -4.0), (-0.8, -4.7), (3.4, -4.6), (3.4, -5.0), (-0.8, -5.1), (-3.8, -4.5), (-5.5, -2.4)]), 'ink', tone=1)
        ribbons_draw(X, 'plume', 'plume', dome=1.6)
        # hombrera de tres laminas con remaches
        for dy, r, m in ((1.9, 3.5, 'goldD'), (1.0, 3.4, 'gold'), (0.1, 3.3, 'gold')):
            circ(X, (sk.shF[0] - 0.2 * (dy > 0), sk.shF[1] + dy), r * k, m, dome=2.6)
        circ(X, (sk.shF[0] + 0.1, sk.shF[1] + 2.9), 3.2 * k, 'goldD', dome=2.4)
        circ(X, (sk.shF[0] + 0.1, sk.shF[1] + 2.5), 3.0 * k, 'gold', dome=2.4)
        circ(X, (sk.shF[0] + 0.4, sk.shF[1] - 0.7), 1.7 * k, 'goldL', dome=1.6)
        for ang in (200, 235, 270):
            q = (sk.shF[0] + math.cos(math.radians(ang)) * 2.4 * k, sk.shF[1] + 0.9 + math.sin(math.radians(ang)) * 2.4 * k)
            circ(X, q, 0.45 * k, 'cloth', tone=5)
        circ(X, (sk.shF[0] + 0.8, sk.shF[1] - 1.1), 0.5 * k, 'cloth', tone=5)
        for dy in (1.8, 0.9):
            circ(X, (sk.shF[0] - 1.9, sk.shF[1] + dy + 0.5), 0.26 * k, 'goldL', tone=5)
        self._pauldron_detail(X)
        # brazo delantero: manga, brazal con bandas, guantelete con nudillos
        arm(X, sk.shF, sk.elbF, sk.handF, 1.85, 1.6, 1.4, 'dark', glove='leather', bracer='gold', hand_r=1.6)
        e, h = sk.elbF, sk.handF
        for t in (0.58, 0.72, 0.86):
            q = (e[0] * (1 - t) + h[0] * t, e[1] * (1 - t) + h[1] * t)
            circ(X, q, 0.4 * k, 'goldL', tone=4)
        circ(X, h, 1.65 * k, 'leather', dome=1.5)
        for dx in (-0.5, 0.0, 0.5):
            circ(X, (h[0] + dx + 0.3, h[1] - 0.6), 0.2 * k, 'goldD', tone=4)
        self._sword(X)

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
        p0 = seq.at(i); pz = NS(**vars(p0)); pz.lean = p0.lean * 0.6 - 0.8; pz.hd = getattr(p0, 'hd', 0) * 0.6 + 2.2   # erguido, pecho al frente, mirada alta
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
    sheet.save(os.path.join(OUT, 'paladin192_sheet.png'))
    import json
    json.dump({'cell': list(CELL), 'rows': [n for n, _ in sheet_rows], 'frames': {n: len(f) for n, f in sheet_rows}, 'note': 'EXPERIMENTAL: no usado por el juego'},
              open(os.path.join(OUT, 'paladin192_sheet.json'), 'w'), indent=1)
    print('ok', sheet.size)


if __name__ == '__main__':
    main()
