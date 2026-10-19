import math
from base import PClass, aura_fx
from rig import Dims, Ribbon
from kit import mat, mat_back
from common import *
import anims as AN


class Earth(PClass):
    id = 'earth'
    c1 = '#C98B3C'
    c2 = '#FFD27A'
    tcore = '#FFE8B0'
    trail_span = (13, 26)
    reach_pts = ((26, 7), (26, -7), (18, 0))
    muzzle_x = 22
    reach_rng = (34, 44)
    skill_kind = 'slam'
    body = (16, 32)

    def setup(self):
        self.D = Dims(k=1.2, tl=8.2, hipy=12.4, thigh=6.4, shin=6.4, up=5.0, fore=5.0, hr=3.4, sw=1.55)
        self.carry = dict(afA=50, afE=0.7, abA=40, abE=0.65, wa=232, two=1.0, lean=6, roll_wa=210,
                          idle_amp=1.3, run_kw=dict(lean=9, stride=6.4, lift=4.5),
                          guard=dict(afA=100, afE=0.55, abA=95, abE=0.5, wa=110, hy=2.5, lean=8, two=1.0), guard2=dict(hy=3))
        self.ribbons = [
            Ribbon('moss', lambda sk: sk.T(-3.0, 9.2), 4, 2.4, [1.8, 2.4, 2.2, 1.2], rest=(-0.4, 1), grav=0.06, k=0.03, flutter=0.4),
        ]
        mk = AN.mk_attack
        c = self.carry
        self.attacks['attack1'] = (mk(c, 6, (1.4, 2.1, 3.1, 4.1), A=(245, 112, 68, 52), E=(0.8, 0.82, 0.82, 0.8), Lh=(-12, 10, 20, 16),
                                      X=(-10, -5, -3, -3), Y=(2, 3, 5, 3), off=(0, 0, 0, 0), FF=((3, -5), (6, -4), (8, -3), (8, -3)), two=1.0), (2, 3))
        self.attacks['attack2'] = (mk(c, 6, (1.4, 2.1, 3.1, 4.1), A=(-65, 66, 130, 170), E=(0.8, 0.82, 0.82, 0.8), Lh=(18, 12, -2, -6),
                                      X=(-6, -3, -3, -4), Y=(4, 3, 0, 0), off=(0, 0, 0, 0), FF=((5, -4), (7, -3), (7, -3), (7, -3)), two=1.0), (2, 3))
        k3 = mk(c, 7, (2.2, 3.2, 4.1, 5.1), A=(250, 118, 58, 46), E=(0.8, 0.82, 0.82, 0.8), Lh=(-16, 14, 30, 24),
                X=(-11, -2, 2, 2), Y=(2, 5, 9, 7), off=(0, 0, 0, 0), FF=((2.5, -5), (7, -3), (11, -3), (11, -3)), two=1.0)
        k3.insert(1, (1, dict(lean=6, hy=4, hx=-2, afA=80, afE=0.55, wa=170, ffx=3, bfx=-6), 'io'))
        self.attacks['attack3'] = (k3, (3, 4))
        self.attacks['airatk'] = (mk(c, 5, (0.4, 1.3, 2.3, 3.3), A=(235, 112, 62, 32), E=(0.8, 0.82, 0.82, 0.8), Lh=(-6, 12, 22, 16),
                                     X=(-7, -4, -2, -2), off=(0, 0, 0, 0), two=1.0,
                                     fa=[dict(ffy=-5, bfy=-6.5, ffa=20, bfa=25)] * 4), (1, 3))

    def init_mats(self):
        mat('rock', '#8C7C6A', hl='#EAD8B8')
        mat('rock2', '#5E5246', hl='#B8A488')
        mat('moss', '#5C8C3C', hl='#C8E878')
        mat('rune', '#FFC060', hl='#FFF4C8')
        mat('wood', '#6A4A30', hl='#C8986A')
        mat('strap', '#C98B3C', hl='#FFE0A0')
        mat('eye', '#FFD27A', hl='#FFFFFF')
        mat('dark', '#2A2220')
        mat('crack', '#2E2620', hl='#6A5A48')
        mat('gold', '#D8A84A', hl='#FFE8A8')
        for m in ('rock', 'rock2', 'moss', 'strap'):
            mat_back(m)

    def draw(self, X):
        D, p, sk = X.D, X.p, X.sk
        k = D.k
        ribbons_draw(X, 'moss', 'moss_b', dome=1.6)
        if p.two < 0.5:
            arm(X, sk.shB, sk.elbB, sk.handB, 2.4, 2.2, 2.0, 'rock2_b', glove='rock_b', hand_r=2.5)
        leg(X, sk.hipB, sk.kneeB, sk.ankB, 2.9, 2.5, 2.2, 'rock2_b', 'rock_b', p.bfa, kneepad='rock_b')
        poly(X, tp(X, [(-4.4, -0.8), (3.8, -0.8), (4.8, 3.5), (5.2, 7.6), (3.8, 9.6), (-3.6, 9.6), (-5.2, 7.2), (-5.0, 3)]), 'rock', dome=4.0)
        # placas de roca y runas
        poly(X, tp(X, [(-1.0, 7.6), (3.6, 7.2), (4.0, 3.6), (0.0, 3.0), (-1.6, 5)]), 'rock2', dome=2.2)
        poly(X, tp(X, [(0.6, 6.2), (1.4, 6.9), (2.2, 6.2), (1.4, 4.2), ]), 'rune', emissive=True)
        poly(X, tp(X, [(-4.6, 2.0), (4.2, 2.0), (4.3, -0.4), (-4.6, -0.4)]), 'strap', dome=1.2)
        poly(X, tp(X, [(0.6, 2.2), (2.6, 2.2), (2.6, -0.6), (0.6, -0.6)]), 'gold', dome=1.0)                                  # hebilla dorada
        poly(X, tp(X, [(1.1, 1.6), (2.1, 1.6), (2.1, 0.0), (1.1, 0.0)]), 'rune', tone=3)
        # bloques de piedra con grietas, juntas y filos de luz
        for (a, b) in (([(-4.6, 6.0), (4.6, 6.2)], 0), ([(-4.4, 4.2), (4.2, 4.4)], 0)):
            cap(X, tp(X, [a[0]])[0], tp(X, [a[1]])[0], 0.2 * k, 0.2 * k, 'crack', tone=2)
        cap(X, tp(X, [(-1.2, 9.4)])[0], tp(X, [(-2.4, 6.4)])[0], 0.16 * k, 0.16 * k, 'crack', tone=2)
        cap(X, tp(X, [(-2.4, 6.4)])[0], tp(X, [(-1.6, 4.6)])[0], 0.16 * k, 0.16 * k, 'crack', tone=2)
        poly(X, tp(X, [(-4.9, 7.4), (-4.2, 7.9), (-1.0, 9.6), (-3.6, 9.6)]), 'rock', tone=5)                                # filo de luz del pecho
        poly(X, tp(X, [(-1.6, 9.6), (3.4, 9.6), (3.8, 8.8), (-1.2, 8.6)]), 'rock2', tone=2)                                  # reborde del cuello
        for (u, v) in ((-3, 6.5), (-2.2, 3.6), (-3.6, 8.4)):
            circ(X, tp(X, [(u, v)])[0], 1.0 * k, 'moss', dome=1.0)
        leg(X, sk.hipF, sk.kneeF, sk.ankF, 3.0, 2.6, 2.3, 'rock2', 'rock', p.ffa, kneepad='rock')
        kn, an = sk.kneeF, sk.ankF
        cap(X, (kn[0] - 2.4, kn[1] + 2.4), (kn[0] + 2.2, kn[1] + 2.6), 0.2 * k, 0.2 * k, 'crack', tone=2)
        cap(X, (an[0] - 2.4, an[1] - 3.2), (an[0] + 2.4, an[1] - 3.0), 0.5 * k, 0.5 * k, 'strap', tone=3)                    # faja del tobillo
        # faldon de piedra
        poly(X, tp(X, [(-0.4, 1.6), (4.4, 1.6), (4.6, -2.6), (2.0, -3.4), (0.2, -2.0)]), 'rock2', dome=2.0)
        hc = sk.head
        circ(X, hc, D.hr, 'rock', dome=3.0)
        poly(X, hp(X, [(0.2, 1.4), (4.0, 1.2), (4.0, -2.6), (0.6, -3.0)]), 'dark', tone=1)
        poly(X, hp(X, [(1.4, 0.6), (3.6, 0.6), (3.6, -0.3), (1.4, -0.3)]), 'eye', emissive=True)
        poly(X, hp(X, [(0.0, 1.9), (4.2, 1.7), (4.2, 1.0), (0.0, 1.2)]), 'rock2', tone=3)                                    # frente pesada
        poly(X, hp(X, [(0.6, -1.2), (3.8, -1.3), (3.8, -2.4), (0.8, -2.5)]), 'rock', tone=2)                                 # mandibula de piedra
        cap(X, hpt(X, 1.4, -1.5), hpt(X, 3.4, -1.5), 0.12 * k, 0.12 * k, 'crack', tone=2)                                    # boca
        cap(X, hpt(X, -2.4, 3.0), hpt(X, -1.0, -0.4), 0.14 * k, 0.14 * k, 'crack', tone=2)                                   # grieta del craneo
        poly(X, hp(X, [(-3.4, 2.2), (-1, 4.0), (1.8, 3.8), (3.4, 2.2), (0, 1.4)]), 'moss', dome=1.4)
        poly(X, hp(X, [(-0.6, 3.6), (0.4, 6.2), (1.6, 3.6)]), 'rock', dome=1.0)   # cresta de piedra
        circ(X, sk.shB, 3.6 * k, 'rock_b', dome=3.0)
        if p.two >= 0.5:
            arm(X, sk.shB, sk.elbB, sk.handB, 2.4, 2.2, 2.0, 'rock2', glove='rock', hand_r=2.5)
        self._hammer(X)
        arm(X, sk.shF, sk.elbF, sk.handF, 2.5, 2.3, 2.1, 'rock2', glove='rock', hand_r=2.6, bracer='rock')
        circ(X, (sk.shF[0] - 0.4, sk.shF[1] + 2.2), 3.8 * k, 'rock2', dome=2.6)                                              # bloque inferior del hombro
        circ(X, sk.shF, 4.1 * k, 'rock', dome=3.4)
        cap(X, (sk.shF[0] - 2.8, sk.shF[1] + 0.4), (sk.shF[0] + 1.2, sk.shF[1] + 3.0), 0.16 * k, 0.16 * k, 'crack', tone=2)    # grieta
        for ang in (205, 250, 295):
            q = (sk.shF[0] + math.cos(math.radians(ang)) * 3.3 * k, sk.shF[1] + math.sin(math.radians(ang)) * 3.3 * k)
            circ(X, q, 0.4 * k, 'gold', tone=4)                                                                              # remaches de oro
        for (dx, dy, r) in ((-1.2, -1.4, 1.5), (1.4, 0.8, 1.2)):
            circ(X, (sk.shF[0] + dx, sk.shF[1] + dy), r, 'moss', dome=1.0)
        circ(X, (sk.shF[0] + 0.6, sk.shF[1] + 0.4), 0.9, 'rune', emissive=True)

    def _hammer(self, X):
        W = lambda pts: wpoly(X, [(x * 0.82, y * 0.9) for x, y in pts])
        poly(X, W([(-14, -1.1), (15, -1.1), (15, 1.1), (-14, 1.1)]), 'wood', dome=1.2)
        poly(X, W([(12, -8.2), (25, -8.6), (26, -6), (26, 6), (25, 8.6), (12, 8.2)]), 'rock', dome=4.0)
        poly(X, W([(14, -6), (23, -6.4), (24, 6.4), (14, 6)]), 'rock2', dome=2.6)
        poly(X, W([(17, -3.2), (21, 0), (17, 3.2), (19, 0)]), 'rune', emissive=True)
        poly(X, W([(10.5, -2.0), (12.5, -2.0), (12.5, 2.0), (10.5, 2.0)]), 'strap', dome=1.0)
        poly(X, W([(12.2, -8.2), (25, -8.6), (25, -8.0), (12.2, -7.6)]), 'rock', tone=5)                                      # filo de luz del martillo
        poly(X, W([(14, 5.6), (24, 6.0), (24, 6.5), (14, 6.1)]), 'crack', tone=2)                                            # sombra inferior
        cap(X, wpt(X, 18, -6.0), wpt(X, 20, -1.0), 0.16 * X.D.k, 0.16 * X.D.k, 'crack', tone=2)                              # grieta de la cabeza
        poly(X, W([(23, -8.8), (25, -9.8), (26, -7.6)]), 'moss', dome=0.8)
        poly(X, W([(-15, -1.6), (-12.5, -1.6), (-12.5, 1.6), (-15, 1.6)]), 'strap', dome=1.0)

    def fx(self, X, name, i, n):
        ov = X.of
        for j in range(3):
            ph = (i * 0.19 + j * 0.37) % 1.0
            ov.dot((X.sk.hip[0] - 6 + j * 6, X.sk.hip[1] + 8 - ph * 16), self.col2, 0.55 * (1 - ph), r=0.5)
        aura_fx(self, X, name, i, n)
