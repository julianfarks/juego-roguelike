import math
from base import PClass, aura_fx
from rig import Dims, Ribbon
from kit import mat, mat_back
from common import *
import anims as AN


class Flame(PClass):
    id = 'flame'
    c1 = '#FF5A1A'
    c2 = '#FFC040'
    tcore = '#FFE08A'
    trail_span = (11, 30)
    reach_pts = ((31, 0), (20, 0))
    muzzle_x = 28
    reach_rng = (34, 44)
    skill_kind = 'slam'

    def setup(self):
        self.D = Dims(k=1.1, hr=4.0, sw=1.3)
        self.carry = dict(afA=58, afE=0.62, abA=48, abE=0.7, wa=240, two=1.0, lean=6,
                          idle_arm=2.0, roll_wa=190,
                          run_kw=dict(lean=12, stride=7.2),
                          guard=dict(afA=95, afE=0.55, abA=95, abE=0.5, wa=165, hy=3, lean=10, two=1.0), guard2=dict(hy=3.6))
        self.ribbons = [
            Ribbon('cape', lambda sk: sk.T(-2.4, 8.6), 5, 3.2, [2.2, 3.0, 3.4, 3.6, 3.0], rest=(-0.4, 1), grav=0.07, k=0.02, flutter=0.7),
            Ribbon('flame_h', lambda sk: (sk.head[0] - sk.hf[0] * 1.0 + sk.hv[0] * 3.2, sk.head[1] - sk.hf[1] * 1.0 + sk.hv[1] * 3.2), 4, 2.4, [1.0, 1.3, 0.9, 0.4], rest=(-0.3, -1), grav=-0.03, k=0.02, flutter=1.6, phase=1),
        ]
        mk = AN.mk_attack
        c = self.carry
        T = lambda **k: [dict(k) for _ in range(4)]
        self.attacks['attack1'] = (mk(c, 6, (1.2, 2.0, 3.0, 4.0), A=(250, 125, 70, 58), E=(0.85, 1.0, 1.0, 0.95), Lh=(-12, 8, 20, 16),
                                      X=(-7, -2, 1, 1), Y=(2, 3, 5, 3), off=(0, 0, 0, 0), FF=((3, -5), (6, -4), (9, -3), (9, -3)),
                                      two=1.0), (2, 3))
        self.attacks['attack2'] = (mk(c, 6, (1.2, 2.0, 3.0, 4.0), A=(-75, 70, 150, 185), E=(0.9, 1.0, 1.0, 0.95), Lh=(18, 14, -4, -8),
                                      X=(-3, 1, 1, 0), Y=(4, 3, 0, 0), off=(0, 0, 0, 0), FF=((5, -4), (8, -3), (8, -3), (8, -3)),
                                      two=1.0), (2, 3))
        k3 = mk(c, 7, (2, 3.1, 4, 5), A=(250, 115, 62, 50), E=(0.9, 1.0, 1.0, 0.95), Lh=(-16, 16, 30, 24),
                X=(-8, 2, 6, 6), Y=(2, 5, 8, 6), off=(0, 0, 0, 0), FF=((2.5, -5), (8, -3), (12, -3), (12, -3)), two=1.0)
        k3.insert(1, (1, dict(lean=8, hy=4, hx=-2, afA=70, afE=0.55, wa=150, ffx=3, bfx=-6), 'io'))
        self.attacks['attack3'] = (k3, (3, 4))
        self.attacks['airatk'] = (mk(c, 5, (0.4, 1.2, 2.2, 3.2), A=(235, 118, 62, 35), E=(0.85, 1.0, 1.0, 0.9), Lh=(-6, 12, 22, 16),
                                     X=(-4, -1, 1, 1), off=(0, 0, 0, 0), two=1.0,
                                     fa=[dict(ffy=-5.5, bfy=-7.5, ffa=25, bfa=30)] * 4), (1, 3))

    def init_mats(self):
        mat('obs', '#3A2E4A', hl='#9A86C0')
        mat('obs2', '#271E36', hl='#6A5A90')
        mat('lava', '#FF5A1A', hl='#FFE08A')
        mat('ember', '#FFC040', hl='#FFFBD0')
        mat('cloth', '#7A1A24', hl='#E8604A')
        mat('steel', '#7C7690', hl='#E8E0F8')
        mat('skin', '#C8946E')
        mat('leather', '#3A2A30')
        for m in ('obs', 'obs2', 'cloth', 'leather'):
            mat_back(m)

    def draw(self, X):
        D, p, sk = X.D, X.p, X.sk
        k = D.k
        ribbons_draw(X, 'cape', 'cloth_b', dome=2.4)
        leg(X, sk.hipB, sk.kneeB, sk.ankB, 2.3, 1.9, 1.6, 'obs2_b', 'leather_b', p.bfa, kneepad='obs_b', greave='obs_b')
        if p.two < 0.5:
            arm(X, sk.shB, sk.elbB, sk.handB, 1.8, 1.6, 1.4, 'obs2_b', glove='obs_b', bracer='obs_b')
        # torso
        poly(X, tp(X, [(-3.2, -0.6), (3.0, -0.6), (3.7, 3.5), (4.0, 7.6), (3.0, 9.8), (-2.6, 9.8), (-3.8, 7), (-3.9, 3)]), 'obs', dome=3.2)
        # grietas de fuego
        for pts in ([(-1.8, 7.8), (-0.4, 6.2), (0.6, 6.6), (1.8, 4.6), (1.2, 4.4), (0.2, 5.8), (-0.6, 5.4), (-2.2, 7.2)],
                    [(0.2, 3.2), (1.0, 2.2), (1.7, 2.4), (1.2, 3.6)]):
            poly(X, tp(X, pts), 'lava', emissive=True)
        # peto de obsidiana en placas: filo claro, juntas con lava y reborde de acero
        poly(X, tp(X, [(-3.4, 6.0), (3.4, 6.0), (4.1, 7.4), (3.6, 9.8), (-2.8, 9.8), (-3.9, 7.4)]), 'obs', dome=3.0)
        poly(X, tp(X, [(-3.2, 3.6), (3.4, 3.6), (3.9, 5.7), (-3.6, 5.7)]), 'obs2', dome=1.6)
        for v in (5.85, 3.5):
            poly(X, tp(X, [(-3.5, v), (3.9, v), (3.9, v + 0.2), (-3.5, v + 0.2)]), 'lava', tone=3)
        poly(X, tp(X, [(-3.3, 9.5), (3.0, 9.5), (3.0, 9.8), (-2.8, 9.8)]), 'steel', tone=3)                       # reborde del gorjal
        poly(X, tp(X, [(-3.2, 6.2), (-2.6, 6.2), (-2.9, 9.4), (-3.5, 8.0)]), 'obs', tone=5)                     # luz del borde
        poly(X, tp(X, [(-3.3, 1.8), (3.2, 1.8), (3.3, -0.4), (-3.4, -0.4)]), 'obs2', dome=1.4)
        for u in (-2.4, -0.8, 0.8, 2.4):                                                                          # tachuelas del cinturon
            circ(X, tp(X, [(u, 0.7)])[0], 0.25 * k, 'ember', tone=4)
        circ(X, tp(X, [(0.2, 1.0)])[0], 1.3 * k, 'ember', emissive=True)
        leg(X, sk.hipF, sk.kneeF, sk.ankF, 2.5, 2.0, 1.7, 'obs2', 'leather', p.ffa, kneepad='obs', greave='obs')
        kn = sk.kneeF
        poly(X, [(kn[0] + 0.8, kn[1] - 1.2), (kn[0] + 3.4, kn[1] - 0.2), (kn[0] + 0.8, kn[1] + 1.0)], 'steel', tone=4)     # pua de rodilla
        circ(X, kn, 0.7 * k, 'lava', emissive=True)
        poly(X, tp(X, [(-0.2, 1.5), (3.4, 1.5), (3.8, -2.2), (1.8, -4.4), (0.2, -3)]), 'cloth', dome=1.8)  # faldon
        self._sword(X)
        # cabeza con cuernos
        hc = sk.head
        ribbons_draw(X, 'flame_h', 'lava', dome=1.0, tone=4)
        horn = [(-1.5, 2.8), (-3.8, 5.5), (-3.4, 8.8), (-1.6, 6.4), (0.4, 3.6)]
        poly(X, hp(X, horn), 'steel', dome=1.2)
        horn2 = [(1.4, 3.0), (3.6, 5.4), (3.6, 9.0), (1.6, 6.0), (0.2, 3.4)]
        poly(X, hp(X, horn2), 'ember', dome=1.2)
        circ(X, hc, D.hr, 'obs', dome=3.4)
        poly(X, hp(X, [(0.4, 1.4), (4.2, 1.2), (4.2, -1.0), (0.4, -1.2)]), 'obs2', tone=1)
        poly(X, hp(X, [(0.2, 2.2), (4.6, 1.8), (4.6, 1.2), (0.2, 1.6)]), 'steel', tone=3)                         # ceja del yelmo
        poly(X, hp(X, [(-4.0, 2.4), (-1.0, 4.6), (1.0, 4.2), (0.2, 2.0)]), 'obs', tone=4)                         # cresta del yelmo
        for v in (-0.4, -1.0):                                                                                    # ventilas de la visera
            poly(X, hp(X, [(1.2, v), (3.6, v - 0.05), (3.6, v - 0.25), (1.2, v - 0.2)]), 'lava', tone=2)
        poly(X, hp(X, [(1.4, 0.8), (3.8, 0.7), (3.8, -0.1), (1.4, 0.0)]), 'lava', emissive=True)
        poly(X, hp(X, [(0.6, -1.6), (3.6, -1.8), (2.8, -3.8), (0.4, -3.2)]), 'obs2', dome=1.4)
        # brazos / hombreras
        circ(X, sk.shB, 2.6 * k, 'obs_b', dome=2.2)
        if p.two >= 0.5:
            arm(X, sk.shB, sk.elbB, sk.handB, 1.8, 1.6, 1.4, 'obs2', glove='obs', bracer='obs')
        arm(X, sk.shF, sk.elbF, sk.handF, 1.9, 1.7, 1.5, 'obs2', glove='obs', bracer='obs')
        circ(X, (sk.shF[0] - 0.3, sk.shF[1] + 1.8), 3.0 * k, 'obs2', dome=2.2)                                    # lamina inferior de la hombrera
        circ(X, sk.shF, 3.1 * k, 'obs', dome=2.8)
        for ang in (200, 245, 290):
            q = (sk.shF[0] + math.cos(math.radians(ang)) * 2.6 * k, sk.shF[1] + math.sin(math.radians(ang)) * 2.6 * k)
            circ(X, q, 0.4 * k, 'steel', tone=4)
        poly(X, [(sk.shF[0] - 0.5, sk.shF[1] - 2.4), (sk.shF[0] + 1.0, sk.shF[1] - 5.6), (sk.shF[0] + 2.0, sk.shF[1] - 2.0)], 'obs', dome=1.2)
        circ(X, (sk.shF[0] + 0.5, sk.shF[1] - 0.3), 0.8, 'lava', emissive=True)

    def _sword(self, X):
        W = lambda pts: wpoly(X, [(x * 0.84, y) for x, y in pts])
        poly(X, W([(3, -2.6), (26, -2.8), (31, -0.8), (36.5, 0.2), (31, 1.8), (26, 2.8), (3, 2.6)]), 'steel', dome=2.4)
        poly(X, W([(4, -1.6), (30, -1.7), (34, 0), (30, 1.7), (4, 1.6)]), 'lava', tone=3)
        poly(X, W([(5, -0.7), (31, -0.7), (33, 0), (31, 0.7), (5, 0.7)]), 'ember', emissive=True)
        poly(X, W([(2.2, -5.2), (3.4, -5.2), (3.4, 5.2), (2.2, 5.2)]), 'obs', dome=1.4)
        poly(X, W([(2.0, -5.2), (3.4, -5.2), (4.6, -7.4), (2.6, -6.2)]), 'steel', tone=4)                          # cuernos de la guarda
        poly(X, W([(2.0, 5.2), (3.4, 5.2), (4.6, 7.4), (2.6, 6.2)]), 'steel', tone=4)
        poly(X, W([(4, -2.4), (29, -2.5), (29, -2.1), (4, -2.0)]), 'steel', tone=5)                                 # filo iluminado
        poly(X, W([(-5.0, -1.1), (2.4, -1.1), (2.4, 1.1), (-5.0, 1.1)]), 'leather', dome=1.0)
        circ(X, wpt(X, -6.2, 0), 1.3 * X.D.k, 'obs', dome=1.2)
        # llamas del filo
        t = X.p.ex
        for j in range(6):
            x = (8 + j * 4.6)
            h = 2.6 + 1.6 * math.sin(X.i * 1.7 + j * 1.9)
            poly(X, W([(x, -2.7), (x + 1.8, -2.7 - h), (x + 3.2, -2.7)]), 'lava', emissive=True)

    def fx(self, X, name, i, n):
        # brasas
        ov = X.of
        for j in range(4):
            ph = (i * 0.29 + j * 0.37) % 1.0
            h = X.sk.handF
            ov.dot((X.sk.head[0] - 6 + j * 3, X.sk.head[1] - 6 - ph * 14), self.col2, 0.8 * (1 - ph), r=0.5)
        aura_fx(self, X, name, i, n)
