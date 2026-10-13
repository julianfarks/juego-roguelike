import math
from base import PClass, aura_fx
from rig import Dims, Ribbon
from kit import mat, mat_back
from common import *
import anims as AN


class Astral(PClass):
    id = 'astral'
    c1 = '#FF4FD0'
    c2 = '#8A6CFF'
    tcore = '#FFE0F8'
    trail_span = (8, 25)
    reach_pts = ((25, 0), (14, 0))
    muzzle_x = 28
    reach_rng = (28, 34)
    skill_kind = 'palm'

    def setup(self):
        self.D = Dims(k=1.0, hr=3.8, sw=0.95)
        self.carry = dict(afA=34, afE=0.75, abA=-30, abE=0.7, wa=70, lean=4,
                          guard=dict(afA=100, afE=0.5, abA=95, abE=0.5, wa=165, hy=2, lean=8), guard2=dict(hy=2.6))
        self.ribbons = [
            Ribbon('cape', lambda sk: sk.T(-2.0, 8.8), 6, 3.2, [2.0, 3.0, 3.6, 4.0, 4.2, 3.8], rest=(-0.4, 1), grav=0.06, k=0.02, flutter=0.9),
            Ribbon('robe', lambda sk: sk.T(0.4, 1.0), 4, 2.6, [2.6, 3.0, 3.1, 2.6], rest=(-0.2, 1), grav=0.07, k=0.03, flutter=0.5, phase=1),
            Ribbon('hair', lambda sk: (sk.head[0] - sk.hf[0] * 2.2 + sk.hv[0] * 1.6, sk.head[1] - sk.hf[1] * 2.2 + sk.hv[1] * 1.6), 6, 2.2, [1.8, 2.2, 2.1, 1.8, 1.2, 0.6], rest=(-1, 0.4), grav=0.03, k=0.01, flutter=1.0, phase=2),
            Ribbon('orb1', lambda sk: sk.T(-3.0, 13.0), 2, 7.0, [1], rest=(-0.7, -0.7), grav=0.0, k=0.06, damp=0.93, flutter=2.0),
            Ribbon('orb2', lambda sk: sk.T(-4.0, 5.0), 2, 8.0, [1], rest=(-1, 0.15), grav=0.0, k=0.06, damp=0.93, flutter=2.0, phase=2),
            Ribbon('orb3', lambda sk: sk.T(4.0, 14.5), 2, 6.0, [1], rest=(0.4, -1), grav=0.0, k=0.06, damp=0.93, flutter=2.0, phase=4),
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
        mat('robe', '#3A2A8A', hl='#B8A0FF')
        mat('robe2', '#241A5C', hl='#7A60D0')
        mat('cape', '#2A1C6A', hl='#8A6CFF')
        mat('pink', '#FF4FD0', hl='#FFE0F8')
        mat('star', '#FFE0F8', hl='#FFFFFF')
        mat('hair', '#B05CFF', hl='#F0C8FF')
        mat('skin', '#E8C0B0')
        mat('gold', '#E8C878', hl='#FFF8D8')
        mat('crystal', '#FF8AE0', hl='#FFFFFF')
        mat('shaft', '#4A3A80', hl='#A090E0')
        mat('leather', '#2E2458')
        mat('eye', '#FF4FD0', hl='#FFFFFF')
        for m in ('robe', 'robe2', 'cape', 'hair', 'leather'):
            mat_back(m)

    def _stars(self, X, pts_uv, seed=0):
        for j, (u, v) in enumerate(pts_uv):
            c = tp(X, [(u, v)])[0]
            if (X.i + j + seed) % 3 == 0:
                spark4(X, c, 1.3, 'star')
            else:
                circ(X, c, 0.45, 'star', emissive=True)

    def draw(self, X):
        D, p, sk = X.D, X.p, X.sk
        k = D.k
        # orbes traseros (detras)
        ribbons_draw(X, 'cape', 'cape_b', dome=2.4)
        pts = X.rb['cape']
        for j in (2, 3, 4):
            circ(X, pts[j], 0.5, 'star', emissive=True)
        arm(X, sk.shB, sk.elbB, sk.handB, 1.5, 1.3, 1.1, 'robe_b', glove='leather_b', bracer='pink')
        leg(X, sk.hipB, sk.kneeB, sk.ankB, 2.0, 1.6, 1.3, 'robe2_b', 'leather_b', p.bfa)
        poly(X, tp(X, [(-2.7, -0.6), (2.5, -0.6), (2.9, 3.5), (3.0, 7.7), (2.4, 9.6), (-2.2, 9.6), (-3.0, 7), (-3.1, 3)]), 'robe', dome=3.0)
        leg(X, sk.hipF, sk.kneeF, sk.ankF, 2.1, 1.7, 1.4, 'robe2', 'leather', p.ffa)
        # falda/tunica larga
        ribbons_draw(X, 'robe', 'robe', dome=2.4)
        poly(X, tp(X, [(-3.0, 1.8), (3.2, 1.8), (3.4, -1.4), (-3.2, -0.8)]), 'robe', dome=2.0)
        poly(X, tp(X, [(-3.0, 2.4), (3.0, 2.4), (3.0, 1.3), (-3.0, 1.3)]), 'pink', dome=1.0)
        self._stars(X, [(-1.6, 6.8), (1.4, 5.0), (-0.8, 3.2), (1.8, 8.0), (-2.0, 0.2), (2.0, -0.4)])
        # capucha/pelo/cabeza
        ribbons_draw(X, 'hair', 'hair_b', dome=1.8)
        hc = sk.head
        circ(X, hc, D.hr, 'skin', dome=3.2)
        poly(X, hp(X, [(-4.4, 0.2), (-3.4, 4.0), (0, 5.0), (3.4, 3.4), (4.2, 1.6), (2.2, 2.6), (0.6, 2.2), (-0.6, 3.0), (-2.6, -1.0)]), 'hair', dome=2.0)
        poly(X, hp(X, [(1.6, 0.4), (3.2, 0.3), (3.2, -0.6), (1.6, -0.5)]), 'eye', emissive=True)
        spark4(X, hp(X, [(1.0, 3.6)])[0], 1.8, 'pink')
        circ(X, sk.shB, 2.3 * k, 'cape_b', dome=2.0)
        self._staff(X)
        arm(X, sk.shF, sk.elbF, sk.handF, 1.5, 1.3, 1.1, 'robe', glove='leather', bracer='pink')
        circ(X, sk.shF, 2.5 * k, 'robe', dome=2.2)
        # orbes flotantes
        ov = X.ob
        for nm in ('orb1', 'orb2', 'orb3'):
            q = X.rb[nm][1]
            ov.glow(q, 4.5, 4.5, self.col1, 0.5, power=1.5)
            circ(X, q, 1.9 * k, 'crystal', dome=1.6)
            circ(X, (q[0] - 0.4, q[1] - 0.5), 0.6, 'star', emissive=True)

    def _staff(self, X):
        W = lambda pts: wpoly(X, pts)
        poly(X, W([(-10, -0.8), (12, -0.8), (12, 0.8), (-10, 0.8)]), 'shaft', dome=1.0)
        poly(X, W([(11, -2.4), (14, -2.8), (24.5, 0), (14, 2.8), (11, 2.4)]), 'crystal', dome=2.0)
        poly(X, W([(12.5, -0.6), (22, 0), (12.5, 0.6)]), 'star', tone=5)
        poly(X, W([(9.8, -3.0), (11.4, -3.0), (11.4, 3.0), (9.8, 3.0)]), 'gold', dome=1.0)
        # orbe en el pomo
        o = wpt(X, -12.5, 0)
        X.ob.glow(o, 5.5, 5.5, self.col1, 0.6, power=1.5)
        circ(X, o, 2.4 * X.D.k, 'pink', dome=2.0)
        circ(X, (o[0] - 0.7, o[1] - 0.8), 0.8, 'star', emissive=True)
        poly(X, W([(-10.8, -1.6), (-9.2, -1.6), (-9.2, 1.6), (-10.8, 1.6)]), 'gold', dome=1.0)

    def fx(self, X, name, i, n):
        ov = X.of
        for j in range(5):
            ph = (i * 0.23 + j * 0.31) % 1.0
            x = X.sk.hip[0] - 9 + j * 4.5
            y = X.sk.hip[1] - 14 + math.sin(i + j * 2) * 8
            if (i + j) % 2 == 0:
                ov.dot((x, y), self.core, 0.9 * (1 - ph), r=0.55)
        aura_fx(self, X, name, i, n)
