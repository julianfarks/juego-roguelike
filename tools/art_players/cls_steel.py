import math
from base import PClass, aura_fx
from rig import Dims, Ribbon
from kit import mat, mat_back
from common import *
import anims as AN


class Steel(PClass):
    id = 'steel'
    c1 = '#C9D4E8'
    c2 = '#FF9A3C'
    tcore = '#FFFFFF'
    trail_span = (10, 26)
    reach_pts = ((26, 0), (14, 0))
    muzzle_x = 26
    reach_rng = (28, 34)
    skill_kind = 'thrust'

    def setup(self):
        self.D = Dims(k=1.04, hr=3.9, sw=1.1)
        self.carry = dict(afA=45, afE=0.7, abA=30, abE=0.65, wa=58, two=1.0, lean=6,
                          run_kw=dict(lean=12), roll_wa=200,
                          guard=dict(afA=105, afE=0.5, abA=100, abE=0.5, wa=160, hy=2, lean=8, two=1.0), guard2=dict(hy=2.6))
        self.ribbons = [
            Ribbon('scarf1', lambda sk: sk.T(-1.2, 9.0), 7, 2.5, [1.5, 1.9, 1.9, 1.8, 1.6, 1.3, 0.8], rest=(-1, 0.25), grav=0.04, k=0.01, flutter=1.0),
            Ribbon('scarf2', lambda sk: sk.T(-0.8, 8.6), 5, 2.4, [1.2, 1.6, 1.5, 1.2, 0.7], rest=(-1, 0.5), grav=0.05, k=0.01, flutter=1.0, phase=2),
            Ribbon('tail', lambda sk: sk.T(-0.5, 1.4), 4, 2.5, [1.4, 1.9, 1.8, 1.1], rest=(-0.5, 1), grav=0.07, k=0.02, flutter=0.5, phase=4),
        ] + [Ribbon('fb%d' % j, lambda sk: sk.T(-3.2, 7.2), 2, 9.5 - (j % 2), [1], rest=r, grav=0.0, k=0.07, damp=0.92, flutter=1.0, phase=j)
             for j, r in enumerate([(-0.5, -1), (-1, -0.65), (-1, 0.0), (-0.45, 0.9)])]
        mk = AN.mk_attack
        c = self.carry
        self.attacks['attack1'] = (mk(c, 6, (1, 1.8, 2.7, 3.7), A=(205, 112, 50, 32), E=(0.75, 0.98, 1.0, 0.95), Lh=(-7, 14, 20, 16),
                                      X=(-2, 4, 6, 6), Y=(1, 2, 3, 2), off=(0, 0, 0, 0), FF=((3.5, -4), (7, -3), (9, -3), (9, -3)), two=1.0), (2, 3))
        self.attacks['attack2'] = (mk(c, 6, (1, 1.8, 2.7, 3.7), A=(-50, 70, 135, 165), E=(0.8, 1.0, 1.0, 0.95), Lh=(15, 14, 2, -3),
                                      X=(2, 6, 5, 4), Y=(3, 2, 0, 0), off=(0, 0, 0, 0), FF=((5, -3), (8, -3), (8, -3), (8, -3)), two=1.0), (2, 3))
        k3 = mk(c, 7, (2, 3, 4, 5), A=(100, 90, 82, 80), E=(0.5, 1.0, 1.0, 0.9), Lh=(-6, 26, 30, 22),
                X=(-6, 9, 13, 11), Y=(3, 5, 6, 3), off=(0, 0, 0, 0), FF=((1, -7), (11, -4), (14, -3), (14, -3)), two=1.0)
        k3.insert(1, (1, dict(lean=8, hy=3, hx=-3, afA=60, afE=0.5, wa=70, ffx=2, bfx=-7), 'io'))
        self.attacks['attack3'] = (k3, (3, 4))
        self.attacks['airatk'] = (mk(c, 5, (0.4, 1.2, 2.2, 3.2), A=(205, 112, 50, 25), E=(0.8, 1.0, 1.0, 0.9), Lh=(-6, 12, 20, 15),
                                     X=(0, 3, 5, 5), off=(0, 0, 0, 0), two=1.0,
                                     fa=[dict(ffy=-5.5, bfy=-7.5, ffa=25, bfa=30)] * 4), (1, 3))

    def init_mats(self):
        mat('steel', '#8E9CB8', hl='#F4F8FF')
        mat('steel2', '#5A6682', hl='#B8C4DC')
        mat('under', '#2C3450', hl='#6A7AA8')
        mat('orange', '#FF8A2C', hl='#FFD8A0')
        mat('skin', '#D8AE90')
        mat('blade', '#D8E2F4', hl='#FFFFFF')
        mat('gold', '#E0A840', hl='#FFF0B8')
        mat('leather', '#3A3044')
        mat('eye', '#FF9A3C', hl='#FFFFFF')
        mat('dark', '#1C1F30')
        for m in ('steel', 'steel2', 'under', 'orange', 'leather'):
            mat_back(m)

    def draw(self, X):
        D, p, sk = X.D, X.p, X.sk
        k = D.k
        # hojas flotantes (detras)
        for j in range(4):
            q0, q1 = X.rb['fb%d' % j]
            ang = math.degrees(math.atan2(q1[0] - q0[0], q1[1] - q0[1]))
            X.of if False else None
            tip = q1
            fr = lambda x, y: wfr(X, q1, ang, x, y)
            poly(X, [fr(-3.0, -0.8), fr(5.5, -0.9), fr(8.5, 0), fr(5.5, 0.9), fr(-3.0, 0.8)], 'blade', dome=1.0)
            poly(X, [fr(-4.0, -1.5), fr(-3.0, -1.5), fr(-3.0, 1.5), fr(-4.0, 1.5)], 'gold', dome=0.8)
            X.ob.glow(q1, 5, 5, self.col2, 0.12, power=1.5)
        ribbons_draw(X, 'scarf2', 'orange_b', dome=1.0)
        if p.two < 0.5:
            arm(X, sk.shB, sk.elbB, sk.handB, 1.6, 1.4, 1.2, 'under_b', glove='leather_b', bracer='steel_b')
        leg(X, sk.hipB, sk.kneeB, sk.ankB, 2.1, 1.7, 1.4, 'under_b', 'leather_b', p.bfa, kneepad='steel_b', greave='steel_b')
        ribbons_draw(X, 'tail', 'under_b', dome=1.6)
        poly(X, tp(X, [(-3.0, -0.6), (2.8, -0.6), (3.2, 3.5), (3.4, 7.6), (2.6, 9.6), (-2.4, 9.6), (-3.2, 7), (-3.3, 3)]), 'under', dome=3.0)
        poly(X, tp(X, [(-3.4, 3.2), (3.0, 3.2), (3.9, 5.2), (4.0, 7.8), (3.0, 9.8), (-2.5, 9.8), (-3.9, 7.4), (-4.0, 4.4)]), 'steel', dome=3.0)
        for v in (4.4, 6.2, 8.0):
            poly(X, tp(X, [(-3.6, v), (3.8, v + 0.2), (3.8, v - 0.7), (-3.6, v - 0.9)]), 'steel2', tone=2)
        poly(X, tp(X, [(-3.2, 1.8), (3.0, 1.8), (3.1, 0.2), (-3.3, 0.2)]), 'orange', dome=1.2)
        leg(X, sk.hipF, sk.kneeF, sk.ankF, 2.3, 1.8, 1.5, 'under', 'leather', p.ffa, kneepad='steel', greave='steel')
        # faldar
        poly(X, tp(X, [(-0.4, 0.4), (3.6, 0.4), (3.9, -3.2), (1.8, -3.6), (0, -2.6)]), 'steel2', dome=1.8)
        ribbons_draw(X, 'scarf1', 'orange', dome=1.0)
        poly(X, tp(X, [(-1.4, 8.4), (3.2, 8.8), (3.6, 10.6), (-1.0, 10.8)]), 'orange', dome=1.4)
        hc = sk.head
        circ(X, hc, D.hr, 'steel', dome=3.4)
        poly(X, hp(X, [(0.6, 1.0), (4.2, 0.8), (4.1, -3.0), (1.0, -3.4)]), 'dark', tone=1)
        poly(X, hp(X, [(1.6, 0.3), (3.8, 0.2), (3.8, -0.6), (1.6, -0.5)]), 'eye', emissive=True)
        # kabuto: visera + cresta de media luna
        poly(X, hp(X, [(-4.0, 2.4), (4.6, 2.2), (4.8, 1.2), (-4.2, 1.0)]), 'steel2', dome=1.2)
        poly(X, hp(X, [(-0.6, 3.4), (-3.2, 8.0), (-2.2, 9.2), (1.0, 6.4), (3.0, 8.8), (3.2, 7.2), (1.4, 3.4)]), 'gold', dome=1.2)
        poly(X, hp(X, [(-4.4, 1.6), (-5.4, -1.0), (-3.8, -3.4), (-2.4, -2.6)]), 'steel2', dome=1.4)
        circ(X, sk.shB, 2.6 * k, 'steel_b', dome=2.2)
        if p.two >= 0.5:
            arm(X, sk.shB, sk.elbB, sk.handB, 1.6, 1.4, 1.2, 'under', glove='leather', bracer='steel')
        self._katana(X)
        arm(X, sk.shF, sk.elbF, sk.handF, 1.7, 1.5, 1.3, 'under', glove='leather', bracer='steel')
        # hombrera (sode)
        poly(X, [(sk.shF[0] - 3.2, sk.shF[1] - 2.4), (sk.shF[0] + 3.2, sk.shF[1] - 2.4), (sk.shF[0] + 3.6, sk.shF[1] + 4.0), (sk.shF[0] - 3.0, sk.shF[1] + 3.8)], 'steel', dome=2.2)
        poly(X, [(sk.shF[0] - 3.0, sk.shF[1] + 0.6), (sk.shF[0] + 3.5, sk.shF[1] + 0.6), (sk.shF[0] + 3.5, sk.shF[1] + 1.6), (sk.shF[0] - 3.0, sk.shF[1] + 1.6)], 'orange', tone=3)

    def _katana(self, X):
        W = lambda pts: wpoly(X, pts)
        poly(X, W([(2.6, -0.9), (14, -1.0), (22, -0.4), (26.5, 0.8), (22, 0.4), (14, 0.9), (2.6, 0.9)]), 'blade', dome=1.0, edge=False)
        poly(X, W([(3, -0.2), (22, 0.0), (22, 0.3), (3, 0.3)]), 'blade', tone=2)
        poly(X, W([(1.8, -2.4), (2.8, -2.4), (2.8, 2.4), (1.8, 2.4)]), 'gold', dome=1.0)
        poly(X, W([(-5.5, -1.0), (1.9, -1.0), (1.9, 1.0), (-5.5, 1.0)]), 'leather', dome=1.0)
        for x in (-4, -2, 0):
            poly(X, W([(x, -1.0), (x + 0.9, -1.0), (x + 0.9, 1.0), (x, 1.0)]), 'orange', tone=3)
        circ(X, wpt(X, -5.8, 0), 1.0 * X.D.k, 'gold', dome=1.0)

    def fx(self, X, name, i, n):
        aura_fx(self, X, name, i, n)
