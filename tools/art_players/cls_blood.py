import math
from base import PClass, aura_fx
from rig import Dims, Ribbon
from kit import mat, mat_back
from common import *
import anims as AN


class Blood(PClass):
    id = 'blood'
    c1 = '#C4122C'
    c2 = '#FF6A7C'
    tcore = '#FFB0BA'
    trail_span = (8, 25)
    reach_pts = ((25, 4), (18, 0), (9, 0))
    muzzle_x = 22
    reach_rng = (34, 44)
    skill_kind = 'slam'

    def setup(self):
        self.D = Dims(k=1.03, tl=9.6, thigh=7.4, shin=7.4, hr=3.7, sw=0.95)
        self.carry = dict(afA=40, afE=0.75, abA=30, abE=0.6, wa=236, two=1.0, lean=5, roll_wa=210,
                          run_kw=dict(lean=11, stride=7.5),
                          guard=dict(afA=100, afE=0.5, abA=95, abE=0.5, wa=130, hy=2, lean=8, two=1.0), guard2=dict(hy=2.6))
        self.ribbons = [
            Ribbon('coatB', lambda sk: sk.T(-1.6, 1.8), 6, 2.9, [2.0, 2.8, 3.2, 3.4, 3.4, 3.0], rest=(-0.3, 1), grav=0.075, k=0.015, flutter=0.7),
            Ribbon('coatF', lambda sk: sk.T(1.6, 1.8), 5, 2.7, [1.6, 2.2, 2.4, 2.4, 2.0], rest=(-0.1, 1), grav=0.07, k=0.02, flutter=0.7, phase=2),
            Ribbon('scarf', lambda sk: sk.T(-1.0, 9.2), 6, 2.4, [1.2, 1.5, 1.5, 1.4, 1.2, 0.8], rest=(-1, 0.2), grav=0.04, k=0.01, flutter=1.0, phase=5),
        ]
        mk = AN.mk_attack
        c = self.carry
        self.attacks['attack1'] = (mk(c, 6, (1.2, 2.0, 3.0, 4.0), A=(-60, 80, 140, 175), E=(0.8, 1.0, 1.0, 0.95), Lh=(14, 14, 0, -4),
                                      X=(-2, 2, 3, 2), Y=(3, 2, 0, 0), off=(10, 0, 0, 0), FF=((4, -4), (8, -3), (8, -3), (8, -3)), two=1.0), (2, 3))
        self.attacks['attack2'] = (mk(c, 6, (1.2, 2.0, 3.0, 4.0), A=(215, 110, 50, 35), E=(0.85, 1.0, 1.0, 0.95), Lh=(-10, 12, 20, 16),
                                      X=(-5, 1, 3, 3), Y=(1, 2, 4, 3), off=(0, 0, 0, 0), FF=((3, -5), (7, -3), (9, -3), (9, -3)), two=1.0), (2, 3))
        k3 = mk(c, 7, (2, 3.1, 4, 5), A=(-70, 70, 150, 215), E=(0.9, 1.0, 1.0, 0.95), Lh=(20, 20, -6, -10),
                X=(-1, 5, 7, 6), Y=(5, 3, 0, 0), off=(0, 0, 0, 0), FF=((5, -5), (10, -3), (12, -3), (12, -3)), two=1.0)
        k3.insert(1, (1, dict(lean=8, hy=3, hx=-1, afA=100, afE=0.6, wa=150), 'io'))
        self.attacks['attack3'] = (k3, (3, 4))
        self.attacks['airatk'] = (mk(c, 5, (0.4, 1.2, 2.2, 3.2), A=(215, 110, 55, 30), E=(0.85, 1.0, 1.0, 0.9), Lh=(-6, 12, 22, 16),
                                     X=(-2, 1, 3, 3), off=(0, 0, 0, 0), two=1.0,
                                     fa=[dict(ffy=-5.5, bfy=-7.5, ffa=25, bfa=30)] * 4), (1, 3))

    def init_mats(self):
        mat('coat', '#2C2230', hl='#8A6A90')
        mat('coat2', '#1C1424', hl='#604868')
        mat('red', '#C4122C', hl='#FF8090')
        mat('redL', '#FF6A7C', hl='#FFE0E4')
        mat('hat', '#241C2A', hl='#7A6082')
        mat('skin', '#D2B2A8')
        mat('metal', '#8A8298', hl='#F0ECF8')
        mat('bladeR', '#C4122C', hl='#FFC0C8')
        mat('wood', '#4A3040', hl='#9A7080')
        mat('leather', '#2A1E26')
        mat('eye', '#FF6A7C', hl='#FFFFFF')
        for m in ('coat', 'coat2', 'red', 'leather', 'hat'):
            mat_back(m)

    def draw(self, X):
        D, p, sk = X.D, X.p, X.sk
        k = D.k
        ribbons_draw(X, 'coatB', 'coat2_b', dome=2.2)
        ribbons_draw(X, 'scarf', 'red_b', dome=1.0)
        if p.two < 0.5:
            arm(X, sk.shB, sk.elbB, sk.handB, 1.5, 1.3, 1.1, 'coat_b', glove='leather_b')
        leg(X, sk.hipB, sk.kneeB, sk.ankB, 1.9, 1.5, 1.25, 'coat2_b', 'leather_b', p.bfa, greave='leather_b')
        poly(X, tp(X, [(-2.8, -0.6), (2.6, -0.6), (3.0, 3.5), (3.2, 7.8), (2.5, 9.9), (-2.3, 9.9), (-3.1, 7), (-3.2, 3)]), 'coat', dome=3.0)
        poly(X, tp(X, [(0.0, 9.6), (2.4, 9.4), (1.6, 0.6), (0.0, 0.6)]), 'red', dome=1.2)   # chaleco rojo
        poly(X, tp(X, [(-2.9, 1.7), (2.8, 1.7), (2.8, 0.7), (-2.9, 0.7)]), 'leather', dome=1.0)
        circ(X, tp(X, [(1.0, 1.2)])[0], 0.7, 'metal', tone=4)
        leg(X, sk.hipF, sk.kneeF, sk.ankF, 2.0, 1.6, 1.35, 'coat2', 'leather', p.ffa, greave='leather')
        ribbons_draw(X, 'coatF', 'coat', dome=1.8)
        # cuello alto
        poly(X, tp(X, [(-2.4, 8.6), (3.2, 8.6), (3.4, 11.0), (1.2, 11.2), (-2.2, 10.6)]), 'coat', dome=1.4)
        hc = sk.head
        circ(X, hc, D.hr, 'skin', dome=3.0)
        poly(X, hp(X, [(1.2, 1.0), (4.0, 0.6), (4.0, -2.8), (0.8, -3.4)]), 'coat2', dome=1.2)   # media mascara/sombra
        poly(X, hp(X, [(1.6, 0.5), (3.4, 0.4), (3.4, -0.4), (1.6, -0.3)]), 'eye', emissive=True)
        # sombrero de ala ancha
        ell(X, (hc[0] - 0.3, hc[1] - D.hr * 0.55), 7.6 * k, 1.6 * k, math.degrees(math.atan2(sk.hf[1], sk.hf[0])) * 0.5, 'hat', dome=1.6)
        poly(X, hp(X, [(-2.8, 1.8), (-2.2, 6.4), (2.4, 6.4), (3.0, 1.8)]), 'hat', dome=2.2)
        poly(X, hp(X, [(-2.8, 2.2), (3.0, 2.2), (3.0, 3.2), (-2.8, 3.2)]), 'red', dome=1.0)
        circ(X, sk.shB, 2.3 * k, 'coat_b', dome=2.0)
        if p.two >= 0.5:
            arm(X, sk.shB, sk.elbB, sk.handB, 1.5, 1.3, 1.1, 'coat', glove='leather')
        self._scythe(X)
        arm(X, sk.shF, sk.elbF, sk.handF, 1.6, 1.4, 1.2, 'coat', glove='leather')
        circ(X, sk.shF, 2.7 * k, 'coat', dome=2.4)

    def _scythe(self, X):
        W = lambda pts: wpoly(X, pts)
        poly(X, W([(-16, -0.7), (10, -0.7), (10, 0.7), (-16, 0.7)]), 'wood', dome=1.0)
        blade = [(8, 0.4), (10.5, 3.0), (14.5, 5.6), (20, 6.4), (24.5, 4.0), (20.5, 4.6), (15.5, 3.4), (12.5, 1.2), (10.5, -0.6)]
        poly(X, W(blade), 'bladeR', dome=1.8)
        poly(X, W([(10.5, 2.0), (15, 4.0), (20, 4.8), (22.5, 4.2), (18, 3.8), (14, 2.6)]), 'redL', tone=4)
        poly(X, W([(7, -1.8), (9.5, -1.8), (9.5, 1.8), (7, 1.8)]), 'metal', dome=1.0)
        circ(X, wpt(X, -16.5, 0), 1.0 * X.D.k, 'metal', dome=1.0)

    def fx(self, X, name, i, n):
        ov = X.of
        for j in range(3):
            ph = (i * 0.2 + j * 0.34) % 1.0
            q = wpt(X, 16 + j * 2, 5)
            ov.dot((q[0], q[1] + ph * 7), self.col1, 0.8 * (1 - ph), r=0.55)
        aura_fx(self, X, name, i, n)
