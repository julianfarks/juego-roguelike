import math
from base import PClass, aura_fx
from rig import Dims, Ribbon, dirv
from kit import mat, mat_back
from common import *
import anims as AN


class Shadow(PClass):
    id = 'shadow'
    c1 = '#A040FF'
    c2 = '#3A0A66'
    tcore = '#E8D0FF'
    trail_span = (4, 11.5)
    reach_pts = ((11, 1), (5, 0))
    muzzle_x = 11
    reach_rng = (18, 22)
    skill_kind = 'palm'

    def setup(self):
        self.D = Dims(k=0.98, hr=3.7, sw=0.9)
        self.carry = dict(afA=50, afE=0.72, abA=30, abE=0.72, wa=95, wb=70, lean=12,
                          run_kw=dict(lean=16, stride=8.2),
                          guard=dict(afA=120, afE=0.55, abA=100, abE=0.55, wa=150, wb=170, hy=3, lean=14), guard2=dict(hy=3.5))
        self.ribbons = [
            Ribbon('scarf', lambda sk: sk.T(-1.5, 8.6), 7, 2.5, [1.6, 1.8, 1.8, 1.7, 1.6, 1.3, 0.9], rest=(-1, 0.25), grav=0.04, k=0.012, flutter=0.9),
            Ribbon('cloak', lambda sk: sk.T(-1.8, 8.2), 5, 3.0, [2.0, 2.6, 3.0, 3.2, 2.6], rest=(-0.5, 1), grav=0.07, k=0.02, flutter=0.5, phase=2),
            Ribbon('tail', lambda sk: sk.T(-0.5, 1.5), 4, 2.6, [1.2, 1.7, 1.6, 1.0], rest=(-0.6, 1), grav=0.07, k=0.02, flutter=0.5, phase=4),
        ]
        c = self.carry
        mk = AN.mk_attack
        FA = lambda: None
        self.attacks['attack1'] = (mk(c, 6, (0.8, 1.7, 2.6, 3.6), A=(165, 95, 30, 20), E=(0.6, 0.95, 1.0, 0.9), Lh=(6, 20, 26, 20),
                                      X=(-1, 3, 6, 6), Y=(2, 3, 4, 3), off=(-20, -6, 0, 0), FF=((3, -4), (7, -3), (9, -3), (9, -3)),
                                      abA=(20, 70, 120, 110), abE=(.6, .8, .9, .8)), (2, 3))
        self.attacks['attack2'] = (mk(c, 6, (0.8, 1.7, 2.6, 3.6), A=(-20, 70, 140, 165), E=(0.7, 1.0, 1.0, 0.9), Lh=(22, 22, 8, 4),
                                      X=(1, 5, 6, 5), Y=(4, 3, 1, 1), off=(10, 4, 0, 0), FF=((4, -4), (8, -3), (8, -3), (8, -3)),
                                      abA=(80, 30, -10, 0), abE=(.8, .7, .7, .7)), (2, 3))
        k3 = mk(c, 7, (2, 3, 4, 5), A=(190, 120, 40, 15), E=(0.8, 1.0, 1.0, 0.95), Lh=(-6, 24, 32, 26),
                X=(-3, 6, 11, 11), Y=(2, 5, 7, 5), off=(-15, -5, 0, 0), FF=((3, -5), (9, -3), (13, -3), (13, -3)),
                abA=(170, 110, 60, 40), abE=(1, 1, .9, .8))
        k3.insert(1, (1, dict(lean=14, hy=4, hx=-2, afA=40, afE=0.5, wa=60, abA=60, ffx=3, bfx=-6), 'io'))
        self.attacks['attack3'] = (k3, (3, 4))
        self.attacks['airatk'] = (mk(c, 5, (0.4, 1.2, 2.2, 3.2), A=(190, 105, 35, 0), E=(0.8, 1.0, 1.0, 0.9), Lh=(0, 18, 26, 20),
                                     X=(0, 2, 4, 4), off=(-15, -5, 0, 0), abA=(160, 100, 60, 40), abE=(1, 1, .9, .8),
                                     fa=[dict(ffy=-5.5, bfy=-7.5, ffa=25, bfa=30)] * 4), (1, 3))

    def init_mats(self):
        mat('cloth', '#3A1568', hl='#B88AF0')
        mat('cloth2', '#240B46', hl='#7A48C0')
        mat('scarf', '#A040FF', hl='#E8CCFF')
        mat('dark', '#1E1430')
        mat('skin', '#BFA0C0')
        mat('steel', '#B7B0D0', hl='#FFFFFF')
        mat('eye', '#E7C8FF', hl='#FFFFFF')
        mat('leather', '#4A3050')
        mat('edge', '#6A3AA8', hl='#D9B8FF')
        mat('gem', '#E7C8FF', hl='#FFFFFF')
        for m in ('cloth', 'cloth2', 'leather', 'scarf'):
            mat_back(m)

    def draw(self, X):
        D, p, sk = X.D, X.p, X.sk
        k = D.k
        ribbons_draw(X, 'cloak', 'cloth2_b', dome=2.4)
        ribbons_draw(X, 'scarf', 'scarf_b', dome=1.2)
        # daga trasera + brazo trasero
        arm(X, sk.shB, sk.elbB, sk.handB, 1.5, 1.3, 1.1, 'cloth_b', glove='leather_b', bracer='leather_b')
        self._dagger(X, sk.handB, p.wb, back=True)
        leg(X, sk.hipB, sk.kneeB, sk.ankB, 2.0, 1.6, 1.3, 'cloth2_b', 'leather_b', p.bfa, greave='leather_b')
        # torso
        poly(X, tp(X, [(-2.8, -0.6), (2.6, -0.6), (3.0, 3.5), (3.1, 7.6), (2.4, 9.6), (-2.2, 9.6), (-3.0, 7), (-3.1, 3)]), 'cloth', dome=3.0)
        poly(X, tp(X, [(-2.9, 0.4), (2.7, 0.4), (2.8, 1.8), (-3.0, 1.8)]), 'leather', dome=1.2)
        poly(X, tp(X, [(-2.9, 1.2), (2.8, 1.2), (2.8, 1.35), (-2.9, 1.35)]), 'dark', tone=1)                            # costura del cinturon
        poly(X, tp(X, [(0.8, 0.2), (2.0, 0.2), (2.0, 2.0), (0.8, 2.0)]), 'steel', dome=0.8)                              # hebilla
        poly(X, tp(X, [(-2.8, 0.2), (-0.8, 0.2), (-0.9, -1.9), (-2.7, -1.5)]), 'leather', dome=1.2)                       # bolsa de cadera
        poly(X, tp(X, [(-2.7, -0.3), (-0.9, -0.3), (-0.9, -0.15), (-2.7, -0.15)]), 'steel', tone=3)
        for v in (4.0, 6.2):                                                                                              # vendajes del torso
            poly(X, tp(X, [(-3.0, v), (2.9, v + 0.5), (2.9, v + 0.7), (-3.0, v + 0.2)]), 'cloth2', tone=2)
        poly(X, tp(X, [(-1.0, 8.8), (2.6, 8.4), (0.4, 1.8), (-0.6, 1.8)]), 'cloth2', dome=1.6)  # banda cruzada
        poly(X, tp(X, [(-0.4, 8.5), (0.6, 8.4), (-0.1, 2.0), (-0.9, 2.0)]), 'leather', tone=4)                           # correa de cuero sobre la banda
        circ(X, tp(X, [(0.9, 5.6)])[0], 0.55 * k, 'steel', dome=1.0)                                                      # broche de la correa
        ribbons_draw(X, 'tail', 'cloth2', dome=1.6)
        leg(X, sk.hipF, sk.kneeF, sk.ankF, 2.1, 1.7, 1.4, 'cloth2', 'leather', p.ffa, greave='leather')
        # bufanda/cuello
        poly(X, tp(X, [(-1.6, 8.0), (3.0, 8.6), (3.4, 10.2), (-1.2, 10.4)]), 'scarf', dome=1.6)
        # capucha + cabeza
        hc = sk.head
        poly(X, hp(X, [(-4.2, 2.5), (-3.0, 4.2), (0, 4.8), (2.8, 3.4), (4.0, 0), (3.6, -2.8), (1.5, -4.0), (-2.6, -3.5), (-4.4, -1.0), (-6.4, 0.6)]), 'cloth', dome=3.0)
        poly(X, hp(X, [(0.8, 2.2), (3.6, 1.0), (3.9, -1.6), (2.0, -3.2), (0.4, -2.6)]), 'dark', tone=1)
        poly(X, hp(X, [(0.5, 2.6), (3.0, 3.2), (3.9, 1.0), (3.6, 0.7), (2.8, 2.6), (0.6, 2.2)]), 'edge', tone=4)           # ribete de la capucha
        poly(X, hp(X, [(-0.6, 3.6), (0.2, 3.9), (0.0, 1.2), (-0.8, 1.4)]), 'cloth2', tone=1)                              # pliegue lateral
        poly(X, hp(X, [(1.2, 0.2), (3.6, 0.2), (3.6, -0.8), (1.2, -0.8)]), 'eye', emissive=True)
        poly(X, hp(X, [(0.8, -1.4), (3.8, -1.6), (3.0, -3.3), (0.6, -3.0)]), 'scarf', dome=1.0)
        # brazo delantero + dagas
        arm(X, sk.shF, sk.elbF, sk.handF, 1.6, 1.4, 1.2, 'cloth', glove='leather', bracer='steel')
        circ(X, sk.shF, 2.2 * k, 'leather', dome=2.0)                                                                     # hombrera de cuero
        circ(X, (sk.shF[0] + 0.2, sk.shF[1] - 0.5), 1.1 * k, 'edge', tone=4)
        poly(X, [(sk.shF[0] - 0.4, sk.shF[1] - 1.8), (sk.shF[0] + 0.6, sk.shF[1] - 3.6), (sk.shF[0] + 1.2, sk.shF[1] - 1.6)], 'steel', tone=4)   # pua
        self._dagger(X, sk.handF, p.wa)

    def _dagger(self, X, hand, ang, back=False):
        m = 'steel'
        pts = [(0.5, -1.0), (5, -1.5), (9.2, -0.4), (11.2, 1.7), (8.2, 0.6), (4.8, 1.0), (0.5, 1.0)]
        poly(X, wfpoly(X, hand, ang, pts), m, dome=1.2)
        poly(X, wfpoly(X, hand, ang, [(0.2, -2.2), (1.4, -2.2), (1.4, 2.2), (0.2, 2.2)]), 'leather' + ('_b' if back else ''), dome=1.0)
        poly(X, wfpoly(X, hand, ang, [(-2.2, -0.7), (0.3, -0.7), (0.3, 0.7), (-2.2, 0.7)]), 'dark', dome=1.0)
        poly(X, wfpoly(X, hand, ang, [(1.6, 0.0), (9.0, -0.4), (9.0, -0.1), (1.6, 0.2)]), 'eye', tone=4)
        poly(X, wfpoly(X, hand, ang, [(1.6, -0.9), (8.8, -1.0), (9.0, -0.6), (1.6, -0.5)]), 'steel', tone=5)              # bisel iluminado
        circ(X, wpt(X, -2.3, 0, hand) if False else wfr(X, hand, ang, -2.3, 0), 0.6 * X.D.k, 'gem', tone=4)                # gema del pomo

    def fx(self, X, name, i, n):
        aura_fx(self, X, name, i, n)
