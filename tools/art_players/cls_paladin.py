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
        self.D = Dims(k=1.06, hr=4.1, sw=1.25)
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
        mat('gold', '#D9A23A', hl='#FFF2B0')
        mat('goldL', '#FFD25A', hl='#FFFBE0')
        mat('cloth', '#EDE9F2', hl='#FFFFFF')
        mat('steel', '#AEBBD2', hl='#F4F8FF')
        mat('under', '#3B4A78')
        mat('leather', '#6A4A3A')
        mat('dark', '#2A2438')
        mat('skin', '#E3AE84')
        mat('plume', '#FFF6C8', hl='#FFFFFF')
        mat('shield', '#E9ECF6', hl='#FFFFFF')
        mat_back('gold'); mat_back('under'); mat_back('leather'); mat_back('cloth', 0.8)

    def draw(self, X):
        D, p, sk = X.D, X.p, X.sk
        k = D.k
        # capa
        ribbons_draw(X, 'cape', 'cloth_b', dome=2.6)
        # pierna trasera
        leg(X, sk.hipB, sk.kneeB, sk.ankB, 2.2, 1.8, 1.5, 'under_b', 'leather_b', p.bfa, kneepad='gold_b', greave='gold_b')
        # torso
        poly(X, tp(X, [(-3.0, -0.6), (2.8, -0.6), (3.2, 3.5), (3.3, 7.6), (2.6, 9.6), (-2.4, 9.6), (-3.2, 7), (-3.3, 3)]), 'under', dome=3.0)
        poly(X, tp(X, [(-3.3, 3.2), (3.0, 3.2), (3.8, 5.2), (3.9, 7.8), (3.0, 9.8), (-2.5, 9.8), (-3.8, 7.4), (-3.9, 4.4)]), 'gold', dome=3.0)
        poly(X, tp(X, [(-3.2, -0.6), (3.0, -0.6), (3.1, 1.5), (-3.3, 1.5)]), 'leather', dome=1.2)
        poly(X, tp(X, [(-3.3, 1.2), (-0.6, 1.2), (-0.8, -2.2), (-3.0, -1.6)]), 'gold_b', dome=1.4)
        # emblema (sol)
        c = tp(X, [(0.9, 5.4)])[0]
        circ(X, c, 1.25 * k, 'goldL', tone=4)
        circ(X, c, 0.6 * k, 'cloth', tone=5)
        # pierna delantera
        leg(X, sk.hipF, sk.kneeF, sk.ankF, 2.4, 1.9, 1.6, 'under', 'leather', p.ffa, kneepad='goldL', greave='gold')
        # tabardo
        poly(X, tp(X, [(0.2, 1.5), (3.3, 1.5), (3.9, -1), (3.6, -4.8), (1.8, -5.8), (0.4, -4.8), (0.0, -1)]), 'cloth', dome=2.0)
        poly(X, tp(X, [(0.2, -4.0), (3.7, -4.0), (3.5, -4.9), (1.8, -5.8), (0.4, -4.9)]), 'goldL', tone=3)
        # gorjal + cabeza
        circ(X, lerp_pt(sk.neck, sk.hip, 0.0), 2.4 * k, 'gold', dome=1.6)
        # brazo trasero con escudo
        self._shield_arm(X)
        # cabeza
        hc = sk.head
        circ(X, hc, D.hr, 'gold', dome=3.6)
        poly(X, hp(X, [(0.2, 0.9), (4.3, 0.9), (4.3, -0.2), (0.2, -0.2)]), 'dark', tone=2)
        poly(X, hp(X, [(2.4, 4.0), (3.2, 4.0), (3.2, -3.4), (2.4, -3.4)]), 'goldL', tone=3)
        poly(X, hp(X, [(0.2, -1.0), (4.0, -1.0), (3.0, -4.0), (0.0, -3.2)]), 'gold', dome=1.8)
        # cresta/pluma
        ribbons_draw(X, 'plume', 'plume', dome=1.6)
        poly(X, hp(X, [(-2.5, 3.0), (1.5, 4.4), (1.5, 3.3), (-2.5, 2.2)]), 'goldL', dome=1.2)
        # hombrera delantera
        circ(X, sk.shF, 3.0 * k, 'gold', dome=2.8)
        circ(X, (sk.shF[0] + 0.8, sk.shF[1] + 0.9), 1.2 * k, 'goldL', tone=4)
        # brazo delantero
        arm(X, sk.shF, sk.elbF, sk.handF, 1.8, 1.55, 1.35, 'gold', glove='goldL', bracer='goldL')
        # espada
        self._sword(X)

    def _shield_arm(self, X):
        p, sk, k = X.p, X.sk, X.D.k
        arm(X, sk.shB, sk.elbB, sk.handB, 1.7, 1.5, 1.3, 'gold_b', glove='gold_b', bracer='gold_b')
        circ(X, sk.shB, 2.5 * k, 'gold', dome=2.4)
        h = sk.handB
        ctr = (h[0] + 1.6 * k, h[1] - 0.2)
        def sp(pts, s=1.0):
            return [(ctr[0] + x * s * k, ctr[1] + y * s * k) for x, y in pts]
        outer = [(-4.6, -6.6), (4.6, -6.6), (4.8, 0.2), (0, 7.6), (-4.8, 0.2)]
        poly(X, sp(outer), 'gold', dome=3.0)
        poly(X, sp(outer, 0.74), 'shield', dome=3.0)
        circ(X, sp([(0, -1.2)])[0], 1.9 * k, 'goldL', dome=1.6)
        circ(X, sp([(0, -1.2)])[0], 0.8 * k, 'cloth', tone=5)

    def _sword(self, X):
        W = lambda pts: wpoly(X, pts)
        poly(X, W([(2.2, -1.5), (17.0, -1.6), (20.6, 0), (17.0, 1.6), (2.2, 1.5)]), 'steel', dome=1.8)
        poly(X, W([(3.0, -0.35), (17.5, -0.35), (17.5, 0.35), (3.0, 0.35)]), 'steel', tone=5)
        poly(X, W([(1.4, -3.9), (2.7, -3.9), (2.7, 3.9), (1.4, 3.9)]), 'gold', dome=1.4)
        poly(X, W([(-2.4, -0.9), (1.5, -0.9), (1.5, 0.9), (-2.4, 0.9)]), 'leather', dome=1.0)
        circ(X, wpt(X, -3.2, 0), 1.25 * X.D.k, 'goldL', dome=1.2)

    def fx(self, X, name, i, n):
        aura_fx(self, X, name, i, n)
