import math
from base import PClass, aura_fx
from rig import Dims, Ribbon
from kit import mat, mat_back
from common import *
import anims as AN


class Frost(PClass):
    id = 'frost'
    c1 = '#80E4FF'
    c2 = '#FFFFFF'
    trail_span = (10, 22)
    reach_pts = ((22, 0), (12, 0))
    muzzle_x = 22
    skill_kind = 'palm'

    def setup(self):
        self.D = Dims(k=1.05, hr=4.0, sw=1.2)
        self.carry = dict(afA=40, afE=0.8, abA=-25, abE=0.75, wa=70, lean=5,
                          guard=dict(afA=100, afE=0.5, abA=95, abE=0.5, wa=170, hy=2, lean=8), guard2=dict(hy=2.6))
        self.ribbons = [
            Ribbon('cloak', lambda sk: sk.T(-2.6, 8.6), 5, 3.3, [2.4, 3.2, 3.6, 3.8, 3.4], rest=(-0.4, 1), grav=0.07, k=0.02, flutter=0.6),
            Ribbon('tailF', lambda sk: sk.T(-0.5, 1.2), 4, 2.4, [1.4, 1.8, 1.7, 1.0], rest=(-0.5, 1), grav=0.07, k=0.02, flutter=0.5, phase=2),
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
        mat('armor', '#6A94C8', hl='#E4F6FF')
        mat('under', '#33508C', hl='#7CA0D8')
        mat('fur', '#EAF4FF', hl='#FFFFFF')
        mat('cloak', '#3D5FA6', hl='#A8D0F8')
        mat('ice', '#6FD8F8', hl='#FFFFFF')
        mat('skin', '#E4B8A0')
        mat('leather', '#4A4668')
        mat('eye', '#80E4FF', hl='#FFFFFF')
        mat('dark', '#1A2038')
        for m in ('armor', 'under', 'fur', 'cloak', 'leather'):
            mat_back(m)

    def draw(self, X):
        D, p, sk = X.D, X.p, X.sk
        k = D.k
        ribbons_draw(X, 'cloak', 'cloak_b', dome=2.4)
        # ribete de piel de la capa
        arm(X, sk.shB, sk.elbB, sk.handB, 1.6, 1.4, 1.2, 'under_b', glove='leather_b', bracer='armor_b')
        leg(X, sk.hipB, sk.kneeB, sk.ankB, 2.2, 1.8, 1.5, 'under_b', 'leather_b', p.bfa, kneepad='armor_b', greave='armor_b')
        poly(X, tp(X, [(-3.0, -0.6), (2.8, -0.6), (3.2, 3.5), (3.3, 7.6), (2.6, 9.6), (-2.4, 9.6), (-3.2, 7), (-3.3, 3)]), 'under', dome=3.0)
        poly(X, tp(X, [(-3.3, 3.0), (3.0, 3.0), (3.8, 5.2), (3.9, 7.8), (3.0, 9.8), (-2.5, 9.8), (-3.8, 7.4), (-3.9, 4.4)]), 'armor', dome=3.0)
        poly(X, tp(X, [(-3.2, -0.6), (3.0, -0.6), (3.1, 1.5), (-3.3, 1.5)]), 'leather', dome=1.2)
        # cristal en el pecho
        c = tp(X, [(0.8, 6.0)])[0]
        poly(X, [(c[0], c[1] - 2), (c[0] + 1.2, c[1]), (c[0], c[1] + 2), (c[0] - 1.2, c[1])], 'ice', emissive=True)
        leg(X, sk.hipF, sk.kneeF, sk.ankF, 2.4, 1.9, 1.6, 'under', 'leather', p.ffa, kneepad='armor', greave='armor')
        ribbons_draw(X, 'tailF', 'fur', dome=1.6)
        # piel en cuello
        circ(X, lerp_pt(sk.neck, sk.hip, 0.1), 2.7 * k, 'fur', dome=2.0)
        hc = sk.head
        circ(X, hc, D.hr, 'armor', dome=3.4)
        poly(X, hp(X, [(-4, 1.5), (-2, 4.2), (1.5, 4.0), (3.4, 2.4), (1.0, 1.4)]), 'cloak', dome=1.4)
        poly(X, hp(X, [(0.6, 1.8), (4.2, 1.6), (4.1, -2.0), (1.0, -3.0)]), 'dark', tone=1)
        poly(X, hp(X, [(1.6, 0.7), (3.8, 0.6), (3.8, -0.3), (1.6, -0.2)]), 'eye', emissive=True)
        # capucha de piel
        for (u, v, r) in ((-3.4, 0.6, 1.7), (-3.0, -2.2, 1.6), (-1.6, -3.6, 1.5)):
            circ(X, hp(X, [(u, v)])[0], r * k, 'fur', dome=1.4)
        # cuernos de hielo
        poly(X, hp(X, [(-1.0, 4.4), (-2.4, 8.4), (0.2, 5.0)]), 'ice', dome=1.0)
        poly(X, hp(X, [(1.0, 4.6), (2.8, 8.0), (2.4, 4.4)]), 'ice', dome=1.0)
        # hombrera de piel
        circ(X, sk.shB, 2.4 * k, 'fur_b', dome=2.0)
        self._sabre(X)
        arm(X, sk.shF, sk.elbF, sk.handF, 1.7, 1.5, 1.3, 'under', glove='leather', bracer='armor')
        circ(X, sk.shF, 3.0 * k, 'armor', dome=2.8)
        circ(X, (sk.shF[0] + 0.2, sk.shF[1] - 1.6), 2.0 * k, 'fur', dome=1.6)

    def _sabre(self, X):
        W = lambda pts: wpoly(X, pts)
        poly(X, W([(2.5, -1.6), (12, -2.0), (19, -1.2), (24, 0.8), (18.5, 1.2), (12, 1.8), (2.5, 1.4)]), 'ice', dome=1.8)
        poly(X, W([(4, -0.4), (14, -0.6), (20, 0.0), (14, 0.5), (4, 0.4)]), 'fur', tone=4)
        poly(X, W([(13, -2.0), (15, -3.3), (16.5, -1.6)]), 'ice', dome=0.8)   # esquirla
        poly(X, W([(1.6, -3.2), (2.8, -3.2), (2.8, 3.2), (1.6, 3.2)]), 'armor', dome=1.2)
        poly(X, W([(-2.6, -0.9), (1.7, -0.9), (1.7, 0.9), (-2.6, 0.9)]), 'leather', dome=1.0)
        circ(X, wpt(X, -3.4, 0), 1.2 * X.D.k, 'ice', emissive=True)

    def fx(self, X, name, i, n):
        ov = X.of
        for j in range(4):
            ph = (i * 0.21 + j * 0.31) % 1.0
            q = wpt(X, 5 + j * 4.5, math.sin(i + j) * 2)
            ov.dot((q[0], q[1] + ph * 6 - 3), self.core, 0.8 * (1 - ph), r=0.5)
        aura_fx(self, X, name, i, n)
