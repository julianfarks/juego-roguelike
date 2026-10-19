import math
from base import PClass, aura_fx
from rig import Dims, Ribbon
from kit import mat, mat_back
from common import *
import anims as AN


class Verdant(PClass):
    id = 'verdant'
    c1 = '#4FD96A'
    c2 = '#C8FF9A'
    trail_span = (9, 21)
    reach_pts = ((21, 0), (12, 0))
    muzzle_x = 21
    skill_kind = 'slam'

    def setup(self):
        self.D = Dims(k=1.02, hr=3.9, sw=1.1)
        self.carry = dict(afA=38, afE=0.82, abA=-22, abE=0.75, wa=66, lean=5,
                          guard=dict(afA=100, afE=0.5, abA=95, abE=0.5, wa=170, hy=2, lean=8), guard2=dict(hy=2.6))
        self.ribbons = [
            Ribbon('cape', lambda sk: sk.T(-2.4, 8.8), 6, 3.0, [2.2, 3.2, 3.8, 4.2, 4.2, 3.6], rest=(-0.45, 1), grav=0.07, k=0.02, flutter=0.8),
            Ribbon('vine', lambda sk: sk.T(-1.0, 1.0), 4, 2.6, [1.0, 1.2, 1.0, 0.6], rest=(-0.3, 1), grav=0.07, k=0.02, flutter=0.8, phase=3),
        ]
        mk = AN.mk_attack
        c = self.carry
        self.attacks['attack1'] = (mk(c, 6, (1, 2, 3, 4), A=(205, 118, 52, 34), E=(0.75, 0.98, 1.0, 0.95), Lh=(-6, 12, 18, 15),
                                      X=(-2, 3, 5, 5), Y=(1, 2, 3, 2), off=(-20, -8, -4, 0), FF=((3.5, -4), (7, -3), (9, -3), (9, -3)),
                                      abA=(-40, -60, -80, -70)), (2, 3))
        self.attacks['attack2'] = (mk(c, 6, (1, 2, 3, 4), A=(-55, 72, 138, 165), E=(0.8, 1.0, 1.0, 0.95), Lh=(15, 13, 2, -3),
                                      X=(2, 6, 5, 4), Y=(3, 2, 0, 0), off=(15, 5, 0, 0), FF=((5, -3), (8, -3), (8, -3), (8, -3)),
                                      abA=(-60, -30, -10, -20)), (2, 3))
        k3 = mk(c, 7, (2, 3, 4, 5), A=(225, 122, 46, 30), E=(0.85, 1.0, 1.0, 0.95), Lh=(-13, 16, 27, 21),
                X=(-4, 6, 10, 10), Y=(2, 4, 7, 5), off=(-20, -8, -3, 0), FF=((2.5, -5), (8, -3), (12, -3), (12, -3)),
                abA=(-70, -100, -110, -90))
        k3.insert(1, (1, dict(lean=6, hy=3, hx=-1, ffx=3, bfx=-5, afA=60, afE=0.6, wa=95), 'io'))
        self.attacks['attack3'] = (k3, (3, 4))
        self.attacks['airatk'] = (mk(c, 5, (0.4, 1.2, 2.2, 3.2), A=(205, 112, 50, 25), E=(0.8, 1.0, 1.0, 0.9), Lh=(-6, 12, 20, 15),
                                     X=(0, 3, 5, 5), off=(-20, -8, -3, 0), abA=(-60, -80, -80, -60),
                                     fa=[dict(ffy=-5.5, bfy=-7.5, ffa=25, bfa=30)] * 4), (1, 3))

    def init_mats(self):
        mat('leaf', '#3E9E4E', hl='#C8FF9A')
        mat('leaf2', '#2A6E3C', hl='#7FD27A')
        mat('bark', '#7A5236', hl='#D8A66C')
        mat('wood', '#9A6A3E', hl='#F0C890')
        mat('moss', '#5A8A3A', hl='#C0E070')
        mat('skin', '#C8A07A')
        mat('mask', '#B49468', hl='#F0DCA8')
        mat('glow', '#4FD96A', hl='#C8FF9A')
        mat('leather', '#4A3626')
        mat('antler', '#D8C090', hl='#FFF4D0')
        mat('bone', '#E8DCC0', hl='#FFFFFF')
        mat('rune', '#8CFFA0', hl='#F0FFE0')
        for m in ('leaf', 'leaf2', 'bark', 'moss', 'leather'):
            mat_back(m)

    def draw(self, X):
        D, p, sk = X.D, X.p, X.sk
        k = D.k
        ribbons_draw(X, 'cape', 'leaf2_b', dome=2.4)
        # hojas de la capa (puntas)
        pts = X.rb['cape']
        for j in range(1, len(pts)):
            q = pts[j]
            poly(X, [(q[0] - 2.2, q[1] - 0.6), (q[0] - 0.6, q[1] - 2.4), (q[0] + 1.6, q[1] - 0.6), (q[0] - 0.4, q[1] + 1.8)], 'leaf_b', dome=1.2)
        arm(X, sk.shB, sk.elbB, sk.handB, 1.6, 1.4, 1.2, 'bark_b', glove='moss_b', bracer='leaf2_b')
        leg(X, sk.hipB, sk.kneeB, sk.ankB, 2.2, 1.8, 1.5, 'bark_b', 'leather_b', p.bfa, kneepad='moss_b')
        poly(X, tp(X, [(-3.0, -0.6), (2.8, -0.6), (3.2, 3.5), (3.4, 7.6), (2.6, 9.6), (-2.4, 9.6), (-3.2, 7), (-3.3, 3)]), 'bark', dome=3.0)
        poly(X, tp(X, [(-3.2, 5.6), (3.4, 6.2), (3.6, 9.4), (2.4, 9.8), (-2.4, 9.8), (-3.4, 8)]), 'leaf', dome=2.4)  # peto de hojas
        for (v, w) in ((8.8, 3.0), (7.2, 3.3), (5.6, 3.1)):                                                                    # hojas solapadas del peto
            poly(X, tp(X, [(-w, v), (0, v + 1.3), (w + 0.2, v), (w - 0.4, v - 1.1), (0, v - 1.6), (-w + 0.4, v - 1.1)]), 'leaf', dome=1.2)
            cap(X, tp(X, [(0, v + 1.0)])[0], tp(X, [(0, v - 1.4)])[0], 0.14 * k, 0.14 * k, 'leaf2', tone=2)                    # nervio central
        poly(X, tp(X, [(-3.4, 3.0), (3.3, 3.0), (3.5, 4.8), (-3.5, 4.8)]), 'bark', dome=1.6)                                    # faja de corteza
        for u in (-2.4, -0.8, 0.8, 2.4):
            cap(X, tp(X, [(u, 3.1)])[0], tp(X, [(u + 0.2, 4.7)])[0], 0.12 * k, 0.12 * k, 'bark', tone=2)                       # vetas
        poly(X, tp(X, [(-3.2, -0.6), (3.0, -0.6), (3.1, 1.7), (-3.3, 1.7)]), 'leather', dome=1.2)
        for u in (-2.4, -1.2, 0.0):
            circ(X, tp(X, [(u, 1.1)])[0], 0.22 * k, 'wood', tone=4)                                                              # tachuelas de madera
        circ(X, tp(X, [(0.6, 1.0)])[0], 1.2 * k, 'glow', emissive=True)
        leg(X, sk.hipF, sk.kneeF, sk.ankF, 2.4, 1.9, 1.6, 'bark', 'leather', p.ffa, kneepad='moss')
        an, kn = sk.ankF, sk.kneeF
        for t in (0.35, 0.6, 0.85):                                                                                            # vendas de enredadera en la pierna
            q = lerp_pt(kn, an, t)
            cap(X, (q[0] - 1.6, q[1]), (q[0] + 1.6, q[1] + 0.5), 0.3 * k, 0.3 * k, 'leaf2', tone=3)
        poly(X, [(kn[0] + 0.4, kn[1] - 1.4), (kn[0] + 2.4, kn[1] - 0.2), (kn[0] + 0.4, kn[1] + 1.0)], 'bone', tone=4)           # espina de rodilla
        ribbons_draw(X, 'vine', 'leaf', dome=1.2)
        # taparrabo de hojas
        poly(X, tp(X, [(-0.2, 1.6), (3.4, 1.6), (3.6, -2.6), (1.6, -1.6), (0.0, -3.0)]), 'leaf', dome=1.6)
        hc = sk.head
        # cornamenta
        for sgn in (1, -1):
            base = hpt(X, 0.8 * sgn * 0 + (1.4 if sgn > 0 else -1.4), 3.2)
        branch = [[(-1.8, 2.4), (-3.2, 6.0), (-2.6, 9.8)], [(-2.9, 5.2), (-5.4, 6.8)], [(-2.7, 7.8), (-4.4, 10.2)],
                  [(1.2, 2.6), (2.6, 6.2), (2.0, 10.0)], [(2.3, 5.8), (4.8, 7.2)], [(2.1, 8.2), (3.9, 10.4)]]
        for br in branch:
            pp = hp(X, br)
            cap(X, pp[0], pp[1], 0.8 * k, 0.6 * k, 'antler', dome=1.0) if len(pp) == 2 else None
            if len(pp) == 3:
                X.cv.add([('l', pp[0], pp[1], 1.35 * k, 1.0 * k), ('l', pp[1], pp[2], 1.0 * k, 0.6 * k)], 'antler', dome=1.2)
        # capucha de musgo y mascara
        circ(X, hc, D.hr, 'moss', dome=3.2)
        poly(X, hp(X, [(0.6, 2.4), (4.0, 1.4), (4.1, -2.4), (1.2, -3.4), (0.2, -1)]), 'mask', dome=2.0)
        poly(X, hp(X, [(1.6, 0.6), (3.6, 0.5), (3.6, -0.3), (1.6, -0.2)]), 'glow', emissive=True)
        poly(X, hp(X, [(0.8, 2.0), (4.0, 1.4), (4.0, 1.0), (0.8, 1.6)]), 'mask', tone=5)                                         # ceja de la mascara
        poly(X, hp(X, [(2.2, 0.0), (3.2, 0.0), (3.3, -2.6), (2.5, -3.0)]), 'mask', tone=2)                                       # hocico/relieve
        for v in (-1.2, -1.9):
            poly(X, hp(X, [(1.4, v), (3.4, v - 0.05), (3.4, v - 0.2), (1.4, v - 0.15)]), 'rune', tone=3)                        # runas de la mascara
        poly(X, hp(X, [(-3.6, 2.4), (-1, 4.2), (1.6, 3.8), (0, 2.6), (-2.4, 1.4)]), 'leaf', dome=1.2)
        circ(X, sk.shB, 2.4 * k, 'moss_b', dome=2.0)
        self._sword(X)
        arm(X, sk.shF, sk.elbF, sk.handF, 1.7, 1.5, 1.3, 'bark', glove='moss', bracer='leaf2')
        circ(X, (sk.shF[0] - 0.3, sk.shF[1] + 1.6), 2.8 * k, 'bark', dome=2.0)
        circ(X, sk.shF, 3.0 * k, 'moss', dome=2.8)
        for ang in (200, 245, 290):
            q = (sk.shF[0] + math.cos(math.radians(ang)) * 2.4 * k, sk.shF[1] + math.sin(math.radians(ang)) * 2.4 * k)
            circ(X, q, 0.35 * k, 'leaf', tone=5)
        poly(X, [(sk.shF[0] - 2, sk.shF[1] - 1), (sk.shF[0] - 0.4, sk.shF[1] - 3.6), (sk.shF[0] + 1.6, sk.shF[1] - 1.2)], 'leaf', dome=1.0)

    def _sword(self, X):
        W = lambda pts: wpoly(X, pts)
        poly(X, W([(2.6, -1.7), (10, -2.1), (17, -1.9), (21.5, 0), (17, 1.8), (10, 2.0), (2.6, 1.6)]), 'wood', dome=1.8)
        # enredadera en espiral
        for j in range(5):
            x = 4.5 + j * 3.3
            poly(X, W([(x, -2.2), (x + 1.3, -2.2), (x + 2.8, 2.2), (x + 1.5, 2.2)]), 'leaf', tone=3)
        poly(X, W([(4, -0.3), (19, -0.2), (19, 0.3), (4, 0.3)]), 'glow', emissive=True)
        poly(X, W([(1.6, -3.4), (2.9, -3.4), (2.9, 3.4), (1.6, 3.4)]), 'bark', dome=1.2)
        poly(X, W([(1.4, -3.4), (2.9, -3.4), (3.8, -5.0), (2.2, -4.2)]), 'wood', tone=4)                                          # ramas de la guarda
        poly(X, W([(1.4, 3.4), (2.9, 3.4), (3.8, 5.0), (2.2, 4.2)]), 'wood', tone=4)
        poly(X, W([(3, -1.8), (19, -1.9), (19, -1.5), (3, -1.4)]), 'wood', tone=5)                                                # veta iluminada
        circ(X, wpt(X, 2.2, 0), 1.3 * X.D.k, 'glow', emissive=True)
        poly(X, W([(-2.6, -0.9), (1.7, -0.9), (1.7, 0.9), (-2.6, 0.9)]), 'leather', dome=1.0)

    def fx(self, X, name, i, n):
        ov = X.of
        for j in range(5):
            ph = (i * 0.17 + j * 0.23) % 1.0
            x = X.sk.hip[0] - 8 + j * 4.5 + math.sin(i * 0.8 + j) * 1.6
            y = X.sk.hip[1] - 4 - ph * 22
            ov.dot((x, y), self.col2, 0.7 * (1 - ph) + 0.1, r=0.6)
        aura_fx(self, X, name, i, n)
