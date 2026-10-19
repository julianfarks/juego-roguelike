import math
from base import PClass, aura_fx
from rig import Dims, Ribbon
from kit import mat, mat_back
from common import *
import anims as AN


class Paladin(PClass):
    id = 'paladin'
    c1 = '#FFD25A'
    c2 = '#FFF6C8'
    trail_span = (11, 21.5)
    reach_pts = ((20.5, 0), (12, 0.0))
    skill_kind = 'thrust'

    def setup(self):
        self.D = Dims(k=1.06, hr=5.0, sw=1.25)
        self.carry = dict(afA=32, afE=0.85, abA=62, abE=0.78, wa=66, lean=3,
                          guard=dict(afA=100, afE=0.5, abA=92, abE=0.95, wa=172, hy=2, lean=8),
                          guard2=dict(hy=2.6, lean=10, abA=96))
        self.ribbons = [
            Ribbon('cape', lambda sk: sk.T(-2.2, 8.4), 6, 3.3, [2.2, 3.0, 3.6, 4.0, 4.2, 3.9], rest=(-0.35, 1), grav=0.075, k=0.02, flutter=0.5),
            Ribbon('plume', lambda sk: (sk.head[0] - sk.hf[0] * 0.6 + sk.hv[0] * 3.9, sk.head[1] - sk.hf[1] * 0.6 + sk.hv[1] * 3.9), 4, 2.6, [1.5, 2.0, 1.9, 1.1], rest=(-0.45, -1), grav=0.05, k=0.03, flutter=0.6, phase=1.0),
        ]
        A = AN
        c = self.carry
        mk = AN.mk_attack
        self.attacks['attack1'] = (mk(c, 6, (1, 2, 3, 4), A=(210, 118, 52, 34), E=(0.75, 0.98, 1.0, 0.95), Lh=(-7, 12, 18, 15),
                                      X=(-2, 3, 5, 5), Y=(1, 2, 3, 2), off=(-22, -8, -4, 0),
                                      FF=((3.5, -4), (7, -3), (9, -3), (9, -3)), abA=(30, 55, 70, 60), abE=(.6, .8, .85, .8)), (2, 3))
        self.attacks['attack2'] = (mk(c, 6, (1, 2, 3, 4), A=(-55, 72, 138, 165), E=(0.8, 1.0, 1.0, 0.95), Lh=(15, 13, 2, -3),
                                      X=(2, 6, 5, 4), Y=(3, 2, 0, 0), off=(15, 5, 0, 0),
                                      FF=((5, -3), (8, -3), (8, -3), (8, -3)), abA=(70, 40, 20, 30), abE=(.8, .8, .7, .7)), (2, 3))
        k3 = mk(c, 7, (2, 3, 4, 5), A=(222, 125, 46, 30), E=(0.85, 1.0, 1.0, 0.95), Lh=(-13, 16, 27, 21),
                X=(-4, 6, 10, 10), Y=(2, 4, 7, 5), off=(-20, -8, -3, 0),
                FF=((2.5, -5), (8, -3), (12, -3), (12, -3)), abA=(50, 75, 85, 70), abE=(.7, .85, .9, .8))
        k3.insert(1, (1, dict(lean=6, hy=3, hx=-1, ffx=3, bfx=-5, afA=60, afE=0.6, wa=95), 'io'))
        self.attacks['attack3'] = (k3, (3, 4))
        self.attacks['airatk'] = (mk(c, 5, (0.4, 1.2, 2.2, 3.2), A=(205, 112, 50, 25), E=(0.8, 1.0, 1.0, 0.9), Lh=(-6, 12, 20, 15),
                                     X=(0, 3, 5, 5), Y=(0, 0, 0, 0), off=(-20, -8, -3, 0),
                                     FF=((3, -3),) * 4, fa=[dict(ffy=-5.5, bfy=-7.5, ffa=25, bfa=30),
                                                            dict(ffy=-5, bfy=-7, ffa=25, bfa=30),
                                                            dict(ffy=-4.5, bfy=-8, ffa=25, bfa=30),
                                                            dict(ffy=-5, bfy=-8, ffa=25, bfa=30)]), (1, 3))

    def init_mats(self):
        mat('gold', '#E3AC3C', hl='#FFF4B8')
        mat('goldL', '#FFD764', hl='#FFFCE6')
        mat('goldD', '#A8731F', hl='#EDBE55')
        mat('cloth', '#F4F0E6', hl='#FFFFFF')
        mat('steel', '#B4C0D6', hl='#F6FAFF')
        mat('under', '#3A5CB8', hl='#8FB4FF')        # sayo azul medio: se lee frente al oro y al fondo oscuro
        mat('blue', '#2A47A0', hl='#8DB6FF')         # capa (mas oscura que el sayo para separar capas) y campo del escudo
        mat('leather', '#7A5238')
        mat('dark', '#221C30')
        mat('skin', '#EDB98F', hl='#FFE0C0')
        mat('hair', '#6E4222', hl='#C98A4B')
        mat('plume', '#C73A4A', hl='#FF9AA0')
        mat('eye', '#BFF3FF', hl='#FFFFFF')
        mat('crimson', '#B5333F', hl='#FF8A8A')
        mat_back('gold'); mat_back('goldD'); mat_back('under', 0.85); mat_back('leather'); mat_back('cloth', 0.8); mat_back('blue', 0.8); mat_back('steel', 0.75)

    # --- ayudas
    @staticmethod
    def _normals(pts):
        out = []
        for i in range(len(pts)):
            a = pts[max(0, i - 1)]; b = pts[min(len(pts) - 1, i + 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1.0
            out.append((-dy / L, dx / L))
        return out

    def _cape(self, X):
        pts = X.rb['cape']; ws = [w * X.D.k for w in X.cls.rib_by_name['cape'].widths]
        ribbons_draw(X, 'cape', 'blue_b', dome=2.6)
        nr = self._normals(pts)
        # pliegues: dos sombras largas y un filo de luz, siguiendo la caida de la tela
        for f, m, tn, r in ((-0.30, 'blue_b', 1, 0.55), (0.28, 'blue_b', 1, 0.5), (-0.62, 'blue_b', 4, 0.4)):
            for i in range(1, len(pts) - 1):
                a = (pts[i][0] + nr[i][0] * ws[i] * f, pts[i][1] + nr[i][1] * ws[i] * f)
                b = (pts[i + 1][0] + nr[i + 1][0] * ws[i + 1] * f, pts[i + 1][1] + nr[i + 1][1] * ws[i + 1] * f)
                cap(X, a, b, r * X.D.k, r * 0.8 * X.D.k, m, tone=tn)
        # ribete dorado en el borde bajo
        i = len(pts) - 1
        a = (pts[i][0] + nr[i][0] * ws[i] * 0.9, pts[i][1] + nr[i][1] * ws[i] * 0.9)
        b = (pts[i][0] - nr[i][0] * ws[i] * 0.9, pts[i][1] - nr[i][1] * ws[i] * 0.9)
        cap(X, a, b, 0.7 * X.D.k, 0.7 * X.D.k, 'goldD', tone=3)

    def draw(self, X):
        D, p, sk = X.D, X.p, X.sk
        k = D.k
        self._cape(X)
        # pierna trasera
        leg(X, sk.hipB, sk.kneeB, sk.ankB, 2.2, 1.8, 1.5, 'under_b', 'leather_b', p.bfa, kneepad='gold_b', greave='gold_b')
        # torso: sayo + peto dorado en placas (cuerpo, faja inferior) separadas por juntas oscuras
        poly(X, tp(X, [(-3.0, -0.6), (2.8, -0.6), (3.2, 3.5), (3.3, 7.6), (2.6, 9.6), (-2.4, 9.6), (-3.2, 7), (-3.3, 3)]), 'under', dome=3.0)
        poly(X, tp(X, [(-3.2, 4.3), (2.8, 4.3), (4.0, 5.4), (4.0, 8.0), (3.1, 10.0), (-2.5, 10.0), (-3.9, 7.8), (-3.9, 5.4)]), 'gold', dome=3.4)
        poly(X, tp(X, [(-3.0, 3.0), (2.6, 3.0), (3.3, 4.5), (-3.4, 4.5)]), 'goldD', dome=1.8)           # faja inferior del peto
        poly(X, tp(X, [(-3.4, 4.4), (3.5, 4.4), (3.5, 4.9), (-3.4, 4.9)]), 'dark', tone=1)              # junta
        poly(X, tp(X, [(1.0, 5.2), (1.9, 5.2), (1.9, 9.4), (1.0, 9.4)]), 'goldL', tone=4)               # cresta central del peto (reflejo)
        poly(X, tp(X, [(-3.3, 1.0), (3.3, 1.0), (3.3, 2.6), (-3.3, 2.6)]), 'leather', dome=1.2)           # cinturon
        poly(X, tp(X, [(0.4, 0.8), (2.6, 0.8), (2.6, 2.8), (0.4, 2.8)]), 'goldL', tone=4)                # hebilla
        poly(X, tp(X, [(1.0, 1.3), (2.0, 1.3), (2.0, 2.3), (1.0, 2.3)]), 'dark', tone=2)
        poly(X, tp(X, [(-3.3, 1.0), (-0.6, 1.0), (-0.8, -2.6), (-3.0, -2.0)]), 'gold_b', dome=1.4)        # faldon trasero
        # pierna delantera
        leg(X, sk.hipF, sk.kneeF, sk.ankF, 2.4, 1.9, 1.6, 'under', 'leather', p.ffa, kneepad='goldL', greave='gold')
        # tabardo blanco con banda azul y ribete dorado
        poly(X, tp(X, [(0.2, 1.5), (3.3, 1.5), (3.9, -1), (3.6, -4.8), (1.8, -5.8), (0.4, -4.8), (0.0, -1)]), 'cloth', dome=2.0)
        poly(X, tp(X, [(0.9, 1.0), (2.3, 1.0), (2.2, -4.6), (1.5, -5.2), (0.9, -4.6)]), 'blue', tone=3)
        poly(X, tp(X, [(0.2, -4.0), (3.7, -4.0), (3.5, -4.9), (1.8, -5.8), (0.4, -4.9)]), 'goldL', tone=3)
        # gorjal
        circ(X, lerp_pt(sk.neck, sk.hip, 0.0), 2.3 * k, 'steel', dome=1.6)
        # brazo trasero con escudo
        self._shield_arm(X)
        # cabeza
        hc = sk.head
        circ(X, hc, D.hr, 'gold', dome=3.6)
        # YELMO CERRADO: visera metalica con ranura de ojos y rejilla vertical; sin piel ni pelo
        poly(X, hp(X, [(0.2, 2.5), (5.1, 2.2), (5.7, -0.4), (5.4, -3.2), (3.6, -4.4), (1.6, -4.6), (0.2, -2.2)]), 'gold', dome=2.0)
        poly(X, hp(X, [(0.4, -2.6), (5.2, -2.6), (4.8, -4.0), (3.4, -4.4), (1.6, -4.5)]), 'goldD', tone=2)                 # barbote en sombra
        poly(X, hp(X, [(0.6, 2.4), (5.2, 2.0), (5.3, 1.6), (0.6, 2.0)]), 'goldL', tone=4)                                  # ceja de la visera (filo de luz)
        poly(X, hp(X, [(1.6, 1.5), (5.8, 1.1), (5.8, 0.25), (1.6, 0.65)]), 'dark', tone=0)                                 # ranura de ojos
        poly(X, hp(X, [(1.6, 0.65), (5.8, 0.25), (5.8, 0.0), (1.6, 0.4)]), 'goldL', tone=3)                                # labio inferior de la ranura
        for u in (2.6, 3.7, 4.8):                                                                                           # rejilla vertical
            poly(X, hp(X, [(u, -0.5), (u + 0.5, -0.5), (u + 0.5, -3.1), (u, -3.1)]), 'dark', tone=0)
        poly(X, hp(X, [(5.5, 1.0), (6.1, -0.4), (5.9, -3.0), (5.4, -3.0)]), 'goldL', tone=3)                               # proa de la visera
        poly(X, hp(X, [(-5.0, 1.4), (-2.4, 5.3), (2.2, 5.5), (5.2, 2.7), (4.9, 2.0), (0.6, 2.4), (-1.0, 0.6)]), 'gold', dome=2.4)
        poly(X, hp(X, [(-3.8, 3.2), (-1.0, 5.6), (3.2, 5.6), (4.8, 3.3), (3.0, 3.9), (-1.0, 4.1)]), 'goldL', dome=1.5)
        poly(X, hp(X, [(-4.8, 1.0), (-0.8, 0.8), (-0.4, -2.6), (-2.4, -3.8), (-4.4, -2.4)]), 'goldD', dome=1.6)          # nuca acorazada (antes pelo)
        poly(X, hp(X, [(-0.4, 1.0), (0.9, 1.0), (1.1, -3.4), (-0.2, -3.2)]), 'goldD', tone=1)                              # junta mejilla-nuca
        # guarda de mejilla dorada
        poly(X, hp(X, [(-1.8, 0.4), (0.3, 0.6), (0.9, -1.5), (0.0, -3.6), (-1.6, -3.2)]), 'goldD', dome=1.6)
        ribbons_draw(X, 'plume', 'plume', dome=1.6)
        # hombrera en capas con remache
        circ(X, (sk.shF[0] - 0.2, sk.shF[1] + 1.3), 3.3 * k, 'goldD', dome=2.4)
        circ(X, sk.shF, 3.2 * k, 'gold', dome=2.8)
        circ(X, (sk.shF[0] + 0.4, sk.shF[1] - 0.7), 1.7 * k, 'goldL', dome=1.6)
        # brazo delantero: manga azul, brazal dorado, guantelete de cuero
        arm(X, sk.shF, sk.elbF, sk.handF, 1.7, 1.5, 1.3, 'under', glove='leather', bracer='gold')
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
        poly(X, sp(outer), 'goldD', dome=2.4)                                                       # borde
        poly(X, sp(outer, 0.80), 'gold', dome=2.0)                                                  # reborde dorado
        poly(X, sp([(-3.2, -5.0), (0, -5.0), (0, 5.2), (-3.4, 0.0)]), 'blue', tone=4)               # campo azul: mitad iluminada
        poly(X, sp([(0, -5.0), (3.2, -5.0), (3.4, 0.0), (0, 5.2)]), 'blue', tone=2)                 # mitad en sombra
        # sol: disco + cuatro rayos largos y cuatro cortos
        c = sp([(0, -1.0)])[0]
        for ang in range(0, 360, 90):
            a = math.radians(ang)
            cap(X, c, (c[0] + math.cos(a) * 3.1 * k, c[1] + math.sin(a) * 3.1 * k), 0.5 * k, 0.15 * k, 'goldL', tone=5)
        for ang in range(45, 360, 90):
            a = math.radians(ang)
            cap(X, c, (c[0] + math.cos(a) * 2.2 * k, c[1] + math.sin(a) * 2.2 * k), 0.4 * k, 0.1 * k, 'goldL', tone=4)
        circ(X, c, 1.35 * k, 'goldL', tone=4)
        circ(X, c, 0.6 * k, 'cloth', tone=5)

    def _sword(self, X):
        W = lambda pts: wpoly(X, pts)
        # hoja con bisel: mitad superior iluminada, inferior en sombra, canal central
        poly(X, W([(2.2, -1.6), (17.0, -1.7), (21.0, 0), (17.0, 1.7), (2.2, 1.6)]), 'steel', tone=3)
        poly(X, W([(2.2, -1.6), (17.0, -1.7), (21.0, 0), (3.0, -0.1)]), 'steel', tone=5)
        poly(X, W([(3.0, 0.1), (21.0, 0), (17.0, 1.7), (2.2, 1.6)]), 'steel', tone=2)
        poly(X, W([(3.4, -0.25), (17.5, -0.25), (17.5, 0.25), (3.4, 0.25)]), 'steel', tone=1)
        # guarda alada dorada con remates
        poly(X, W([(1.2, -4.8), (2.9, -3.4), (2.9, 3.4), (1.2, 4.8), (0.6, 3.4), (0.6, -3.4)]), 'gold', dome=1.6)
        poly(X, W([(1.0, -4.8), (1.8, -4.8), (1.8, -3.0), (1.0, -3.0)]), 'goldL', tone=5)
        circ(X, wpt(X, 1.9, 0), 0.85 * X.D.k, 'crimson', tone=4)
        # empuñadura de cuero con vendas y pomo
        poly(X, W([(-2.4, -0.95), (0.6, -0.95), (0.6, 0.95), (-2.4, 0.95)]), 'leather', dome=1.0)
        poly(X, W([(-1.6, -1.0), (-1.1, -1.0), (-1.1, 1.0), (-1.6, 1.0)]), 'goldD', tone=3)
        circ(X, wpt(X, -3.3, 0), 1.35 * X.D.k, 'goldL', dome=1.2)

    def fx(self, X, name, i, n):
        aura_fx(self, X, name, i, n)
