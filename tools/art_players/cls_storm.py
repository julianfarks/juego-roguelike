import math
from base import PClass, aura_fx
from rig import Dims, Ribbon
from kit import mat, mat_back
from common import *
import anims as AN


class Storm(PClass):
    id = 'storm'
    c1 = '#4DC8FF'
    c2 = '#F0FCFF'
    trail_span = (16, 36)
    reach_pts = ((37, 0), (20, 0))
    muzzle_x = 36
    reach_rng = (34, 40)
    skill_kind = 'thrust'

    def setup(self):
        self.D = Dims(k=1.0, tl=9.2, hr=3.8, sw=0.9)
        self.carry = dict(afA=78, afE=0.72, abA=-60, abE=0.7, wa=84, lean=9,
                          run_kw=dict(lean=15, stride=8.0), roll_wa=200,
                          guard=dict(afA=100, afE=0.5, abA=-40, abE=0.5, wa=160, hy=2.5, lean=10), guard2=dict(hy=3))
        self.ribbons = [
            Ribbon('hair', lambda sk: (sk.head[0] - sk.hf[0] * 1.8 + sk.hv[0] * 2.0, sk.head[1] - sk.hf[1] * 1.8 + sk.hv[1] * 2.0), 6, 2.3, [2.2, 2.6, 2.4, 2.0, 1.4, 0.8], rest=(-1, 0.3), grav=0.03, k=0.01, flutter=1.0),
            Ribbon('hair2', lambda sk: (sk.head[0] - sk.hf[0] * 1.0 + sk.hv[0] * 3.0, sk.head[1] - sk.hf[1] * 1.0 + sk.hv[1] * 3.0), 5, 2.1, [1.4, 1.8, 1.5, 1.0, 0.5], rest=(-1, -0.2), grav=0.03, k=0.01, flutter=1.0, phase=2),
            Ribbon('coat', lambda sk: sk.T(-1.2, 1.4), 5, 2.6, [2.0, 2.6, 2.8, 2.6, 2.0], rest=(-0.5, 1), grav=0.07, k=0.02, flutter=0.6, phase=3),
            Ribbon('scarf', lambda sk: sk.T(-1.2, 8.8), 5, 2.2, [1.2, 1.4, 1.3, 1.1, 0.7], rest=(-1, 0.3), grav=0.03, k=0.01, flutter=1.0, phase=5),
        ]
        mk = AN.mk_attack
        c = self.carry
        self.attacks['attack1'] = (mk(c, 6, (1.0, 1.9, 2.8, 3.8), A=(100, 86, 86, 84), E=(0.35, 1.0, 1.0, 0.8), Lh=(0, 22, 26, 18),
                                      X=(-5, 5, 7, 6), Y=(2, 3, 4, 2), off=(0, 0, 0, 0), FF=((2, -6), (9, -4), (11, -3), (11, -3)),
                                      abA=(-70, -80, -85, -70)), (2, 3))
        self.attacks['attack2'] = (mk(c, 6, (1.0, 1.9, 2.8, 3.8), A=(60, 90, 100, 88), E=(0.4, 1.0, 1.0, 0.8), Lh=(0, 22, 26, 18),
                                      X=(-5, 6, 8, 6), Y=(2, 3, 4, 2), off=(0, 0, 0, 0), FF=((2, -6), (10, -4), (12, -3), (12, -3)),
                                      abA=(-70, -80, -85, -70)), (2, 3))
        k3 = mk(c, 7, (2, 3, 4, 5), A=(130, 80, 75, 70), E=(0.4, 1.0, 1.0, 0.8), Lh=(-6, 28, 32, 20),
                X=(-7, 9, 12, 10), Y=(3, 5, 6, 3), off=(0, 0, 0, 0), FF=((1, -7), (11, -4), (14, -3), (14, -3)),
                abA=(-80, -95, -100, -80))
        k3.insert(1, (1, dict(lean=4, hy=3, hx=-3, afA=60, afE=0.5, wa=50, ffx=2, bfx=-7), 'io'))
        self.attacks['attack3'] = (k3, (3, 4))
        self.attacks['airatk'] = (mk(c, 5, (0.4, 1.2, 2.2, 3.2), A=(150, 100, 60, 20), E=(0.6, 1.0, 1.0, 0.9), Lh=(0, 20, 26, 18),
                                     X=(0, 4, 6, 6), off=(0, 0, 0, 0), abA=(-80, -90, -90, -80),
                                     fa=[dict(ffy=-5.5, bfy=-7.5, ffa=25, bfa=30)] * 4), (1, 3))

    def init_mats(self):
        mat('coat', '#2E6FB8', hl='#A8E8FF')
        mat('coat2', '#1E4A8A', hl='#6AC0F0')
        mat('white', '#E4F2FF', hl='#FFFFFF')
        mat('hair', '#7FD8FF', hl='#F0FCFF')
        mat('skin', '#EDC0A0')
        mat('steel', '#C4D4E8', hl='#FFFFFF')
        mat('gold', '#E8C860', hl='#FFFBD0')
        mat('leather', '#3A3A58')
        mat('eye', '#4DC8FF', hl='#F0FCFF')
        mat('trim', '#F2D878', hl='#FFFBE0')
        mat('sapph', '#2A8AE8', hl='#C8F0FF')
        for m in ('coat', 'coat2', 'white', 'leather', 'hair'):
            mat_back(m)

    def draw(self, X):
        D, p, sk = X.D, X.p, X.sk
        k = D.k
        ribbons_draw(X, 'hair', 'hair_b', dome=2.0)
        ribbons_draw(X, 'coat', 'coat2_b', dome=2.0)
        arm(X, sk.shB, sk.elbB, sk.handB, 1.4, 1.2, 1.0, 'coat2_b', glove='leather_b', bracer='white_b')
        leg(X, sk.hipB, sk.kneeB, sk.ankB, 1.9, 1.5, 1.2, 'coat2_b', 'leather_b', p.bfa, greave='leather_b')
        poly(X, tp(X, [(-2.6, -0.6), (2.4, -0.6), (2.8, 3.5), (2.9, 7.6), (2.3, 9.6), (-2.1, 9.6), (-2.9, 7), (-3.0, 3)]), 'coat', dome=3.0)
        poly(X, tp(X, [(0.4, 9.4), (2.6, 8.2), (0.6, 0.6), (-0.2, 0.6)]), 'white', dome=1.4)   # solapa
        poly(X, tp(X, [(-2.8, 1.6), (2.6, 1.6), (2.6, 0.5), (-2.8, 0.5)]), 'gold', dome=1.0)  # cinturon
        poly(X, tp(X, [(0.6, 2.0), (1.8, 2.0), (1.8, 0.2), (0.6, 0.2)]), 'steel', dome=0.8)                              # hebilla
        circ(X, tp(X, [(1.2, 1.1)])[0], 0.35 * k, 'sapph', tone=4)
        poly(X, tp(X, [(-0.2, 9.4), (0.5, 9.5), (0.7, 6.0), (0.1, 6.0)]), 'coat2', tone=2)                                # solapa oscura
        for v in (8.0, 6.4, 4.8, 3.2):                                                                                    # botones dorados
            circ(X, tp(X, [(1.0, v)])[0], 0.28 * k, 'trim', tone=4)
        poly(X, tp(X, [(-2.9, 7.2), (2.7, 7.6), (2.7, 7.8), (-2.9, 7.4)]), 'coat2', tone=2)                               # costura del pecho
        poly(X, tp(X, [(-2.0, 9.4), (2.4, 9.8), (2.6, 8.6), (-1.6, 8.4)]), 'white', dome=1.0)                             # cuello alto
        leg(X, sk.hipF, sk.kneeF, sk.ankF, 2.0, 1.6, 1.3, 'coat2', 'leather', p.ffa, greave='leather')
        poly(X, tp(X, [(-0.4, 1.8), (3.1, 1.8), (3.3, -2.8), (1.2, -3.6), (0, -2)]), 'coat', dome=1.6)  # faldon
        poly(X, tp(X, [(0.0, -2.0), (3.3, -2.8), (3.2, -3.1), (1.2, -3.9), (0.1, -2.5)]), 'trim', tone=3)                 # ribete dorado del faldon
        ribbons_draw(X, 'scarf', 'white', dome=1.0)
        # cabeza
        hc = sk.head
        ribbons_draw(X, 'hair2', 'hair', dome=1.6)
        circ(X, hc, D.hr, 'skin', dome=3.2)
        poly(X, hp(X, [(-4.2, 0.4), (-3.4, 3.8), (0, 4.6), (3.4, 3.2), (4.2, 1.8), (2.8, 2.2), (0.8, 3.0), (-0.6, 1.8), (-3.0, -1.4)]), 'hair', dome=1.8)
        poly(X, hp(X, [(1.6, 0.3), (3.2, 0.3), (3.2, -0.6), (1.6, -0.6)]), 'eye', emissive=True)
        poly(X, hp(X, [(1.2, 1.5), (3.6, 1.7), (3.6, 1.2), (1.2, 1.0)]), 'hair', tone=2)                                   # ceja marcada
        poly(X, hp(X, [(1.0, -2.2), (3.6, -2.0), (3.2, -3.2), (1.6, -3.5)]), 'skin', tone=2)                                # mandibula definida
        poly(X, hp(X, [(3.0, -1.5), (3.8, -1.6), (3.8, -1.9), (3.0, -1.8)]), 'skin', tone=1)                                # boca
        poly(X, hp(X, [(-3.6, 2.0), (3.8, 2.2), (3.8, 3.2), (-3.6, 3.0)]), 'white', dome=1.0)  # cinta
        circ(X, hpt(X, 2.4, 2.7), 0.6 * k, 'sapph', tone=4)                                                                 # gema de la cinta
        for u in (-1.5, 0.2, 1.8):                                                                                          # mechones claros
            cap(X, hpt(X, u, 4.0), hpt(X, u - 1.6, 1.0), 0.25 * k, 0.12 * k, 'hair', tone=5)
        # brazo delantero + estoque
        self._rapier(X)
        arm(X, sk.shF, sk.elbF, sk.handF, 1.5, 1.3, 1.1, 'coat', glove='white', bracer='steel')
        circ(X, sk.shF, 1.9 * k, 'trim', dome=1.6)                                                                          # charretera
        circ(X, (sk.shF[0] + 0.2, sk.shF[1] - 0.4), 0.8 * k, 'sapph', tone=4)
        for i in range(3):
            cap(X, (sk.shF[0] - 1.2 + i * 0.9, sk.shF[1] + 1.3), (sk.shF[0] - 1.5 + i * 0.9, sk.shF[1] + 2.5), 0.2 * k, 0.2 * k, 'trim', tone=3)

    def _rapier(self, X):
        W = lambda pts: wpoly(X, pts)
        poly(X, W([(3.5, -0.75), (30, -0.55), (36, 0), (30, 0.55), (3.5, 0.75)]), 'steel', dome=1.0, edge=False)
        poly(X, W([(4, -0.2), (33, -0.1), (33, 0.15), (4, 0.2)]), 'white', tone=5)
        # guarda de cesta
        poly(X, W([(1.5, -3.2), (3.4, -3.0), (4.2, 0), (3.4, 3.4), (1.5, 3.6), (2.2, 0)]), 'gold', dome=1.4)
        poly(X, W([(-3.0, -0.8), (1.6, -0.8), (1.6, 0.8), (-3.0, 0.8)]), 'leather', dome=1.0)
        circ(X, wpt(X, -3.6, 0), 1.1 * X.D.k, 'gold', dome=1.0)
        poly(X, W([(1.8, -3.2), (3.2, -3.0), (3.4, -2.2), (1.8, -2.4)]), 'trim', tone=5)                                    # reborde de la cesta
        circ(X, wpt(X, 2.6, 0), 0.6 * X.D.k, 'sapph', tone=4)                                                               # gema de la cesta

    def fx(self, X, name, i, n):
        ov = X.of
        import random
        rnd = random.Random(i * 31 + len(name))
        tip = X.sk.handF
        for j in range(5):
            ph = rnd.random()
            x = 6 + rnd.random() * 30
            y = rnd.uniform(-2.2, 2.2)
            q = wpt(X, x, y)
            ov.dot(q, self.core, 0.9, r=0.5)
        # arco electrico
        pts = [wpt(X, 8 + j * 6, rnd.uniform(-3, 3)) for j in range(5)]
        for a, b in zip(pts, pts[1:]):
            ov.line(a, b, self.col1, 0.8, width=0.7)
        aura_fx(self, X, name, i, n)
