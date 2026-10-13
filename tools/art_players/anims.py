"""Plantillas de animacion (claves de pose) parametrizadas por el 'carry' (pose de reposo) de cada clase."""
import math
from rig import Seq, DEF

N = dict(idle=6, run=8, jump=3, fall=2, roll=7, attack1=6, attack2=6, attack3=7, airatk=5, skill=7, ult=10, hurt=2,
         death=9, block=2)
FPS = dict(idle=8, run=14, jump=10, fall=8, roll=20, attack1=16, attack2=16, attack3=15, airatk=16, skill=14, ult=12,
           hurt=10, death=9, block=8)
LOOP = dict(idle=True, run=True, fall=True)
ORDER = ['idle', 'run', 'jump', 'fall', 'roll', 'attack1', 'attack2', 'attack3', 'airatk', 'skill', 'ult', 'hurt',
         'death', 'block']


def ft(hx, f=4.2, b=-4.2, y=-1.2, **kw):
    d = dict(hx=hx, ffx=hx + f, bfx=hx + b, ffy=y, bfy=y)
    d.update(kw)
    return d


def idle_keys(C, amp=1.0, arm=3.0):
    keys = []
    for i in range(6):
        ph = 2 * math.pi * i / 6
        d = dict(hy=0.5 * amp * (0.5 - 0.5 * math.cos(ph)) + 0.15 * amp, lean=C.get('lean', 4) + 0.9 * amp * math.sin(ph),
                 afA=C['afA'] + arm * math.sin(ph - 0.9), abA=C['abA'] + arm * 0.8 * math.sin(ph - 0.5),
                 wa=C['wa'] + arm * 0.6 * math.sin(ph - 1.2), hd=1.2 * math.sin(ph - 1.0),
                 wx=0.0, wy=0.0, ex=ph)
        keys.append((i, d, 'io'))
    return keys


def run_keys(C, stride=7.5, lift=5.5, lean=11, arm=14, bob=1.0):
    keys = []
    for i in range(8):
        th = 2 * math.pi * i / 8

        def foot(ph):
            ph = ph % 1.0
            if ph < 0.5:
                s = ph / 0.5
                return (stride - 2 * stride * s * 0.96, -1.2, -8 + 14 * s)
            s = (ph - 0.5) / 0.5
            e = s * s * (3 - 2 * s)
            return (-stride + 2 * stride * e, -1.2 - lift * math.sin(math.pi * s) ** 0.9, 24 * math.sin(math.pi * s))
        fa = foot(i / 8.0)
        fb = foot(i / 8.0 + 0.5)
        d = dict(hy=bob * math.cos(2 * th) * 0.9 + 0.8, lean=lean, hx=0,
                 ffx=fa[0], ffy=fa[1], ffa=fa[2], bfx=fb[0], bfy=fb[1], bfa=fb[2],
                 afA=C['afA'] + C.get('run_arm', 0) + arm * 0.5 * math.sin(th + math.pi),
                 abA=C['abA'] + arm * 2.2 * math.sin(th) + C.get('run_abA', 0),
                 abE=C.get('run_abE', 0.7), wa=C['wa'] + C.get('run_wa', 0) + 4 * math.sin(th + math.pi),
                 wx=-0.9, hd=-2.0, ex=th)
        keys.append((i, d, 'lin'))
    return keys


def jump_keys(C):
    return [(0, dict(hy=3.5, lean=12, ffx=4, ffy=-1.2, bfx=-3, bfy=-1.2, afA=C['afA'] - 10, abA=-50, wy=-0.3), 'io'),
            (1, dict(hy=-1.5, lean=6, ffx=5, ffy=-8, ffa=25, bfx=-3.5, bfy=-6, bfa=35, afA=C['afA'] + 40, abA=60, abE=0.8,
                     wa=C['wa'] + 20, wy=0.7), 'out'),
            (2, dict(hy=-1.0, lean=3, ffx=4, ffy=-6.5, ffa=20, bfx=-3.5, bfy=-4.5, bfa=30, afA=C['afA'] + 50, abA=80,
                     wa=C['wa'] + 25, wy=0.5), 'io')]


def fall_keys(C):
    return [(0, dict(hy=-0.5, lean=8, ffx=4.5, ffy=-5.5, ffa=30, bfx=-4, bfy=-8.5, bfa=35, afA=C['afA'] + 55,
                     abA=100, wa=C['wa'] + 30, wy=-0.9), 'io'),
            (1, dict(hy=-0.5, lean=10, ffx=5, ffy=-4.8, ffa=34, bfx=-4.5, bfy=-7.5, bfa=40, afA=C['afA'] + 70,
                     abA=125, wa=C['wa'] + 40, wy=-1.1), 'io')]


def roll_keys(C):
    ks = []
    for i in range(7):
        u = i / 6.0
        tuck = math.sin(min(1.0, u * 1.2 + 0.1) * math.pi) ** 0.5
        tuck = 1.0 if 0.15 < u < 0.9 else 0.45
        rot = 360 * (i / 6.6)
        ks.append((i, dict(hy=2.5 + 5 * tuck, hx=-3 + 6 * u, lean=20 + 45 * tuck, hd=-12 * tuck, rot=rot,
                           ffx=-3 + 6 * u + 3, ffy=-1.2 - 6.5 * tuck, ffa=30, bfx=-3 + 6 * u + 0.5, bfy=-1.2 - 5.5 * tuck, bfa=30,
                           afA=C['afA'] * 0 + 70 + 10 * tuck, afE=0.45, abA=60, abE=0.45, two=0.0,
                           wa=C.get('roll_wa', 215), wx=-0.5), 'lin'))
    return ks


def hurt_keys(C):
    return [(0, dict(lean=-16, hx=-2.5, hy=1.0, hd=-8, afA=C['afA'] + 55, afE=0.7, abA=-70, abE=0.8, wa=C['wa'] + 30,
                     ffx=1.5, bfx=-6.5, bfy=-1.2), 'in'),
            (1, dict(lean=-9, hx=-3.5, hy=0.8, hd=-4, afA=C['afA'] + 30, abA=-45, wa=C['wa'] + 15, ffx=0.5, bfx=-7,
                     bfy=-1.2), 'out')]


def death_keys(C):
    k = []
    k.append((0, dict(lean=-14, hx=-2, hy=0.5, hd=-8, afA=C['afA'] + 70, abA=-80, wa=C['wa'] + 40, ffx=1, bfx=-6), 'in'))
    k.append((1, dict(lean=-26, hx=-4, hy=2.5, hd=-10, afA=C['afA'] + 80, abA=-95, wa=C['wa'] + 55, ffx=0, bfx=-8,
                      wx=0.5), 'out'))
    k.append((2, dict(lean=-24, hx=-5, hy=6.5, hd=-5, afA=130, afE=0.6, abA=-100, wa=140, ffx=2, ffy=-1.2, bfx=-9,
                      bfy=-1.2, two=0), 'io'))
    k.append((3, dict(lean=-50, hx=-9, hy=9.5, hd=-6, afA=150, abA=-110, afE=0.7, wa=130, ffx=1, ffy=-3.5, ffa=20,
                      bfx=-11, bfy=-1.2, two=0), 'in'))
    k.append((4, dict(lean=-78, hx=-12, hy=11.5, hd=-4, afA=165, abA=-130, wa=120, ffx=-1, ffy=-8, ffa=20, bfx=-6, bfy=-5,
                      bfa=20, two=0), 'in'))
    k.append((5, dict(lean=-86, hx=-13, hy=12, hd=0, afA=135, abA=-150, wa=100, ffx=-4, ffy=-6, ffa=10, bfx=-1, bfy=-6.5,
                      two=0, afE=0.6), 'out'))
    k.append((6, dict(lean=-88, hx=-13.5, hy=12.2, hd=0, afA=110, afE=0.9, abA=-170, wa=96, ffx=-2, ffy=-4.5, bfx=-1.5, bfy=-3,
                      two=0), 'io'))
    k.append((7, dict(lean=-88, hx=-13.7, hy=12.3, afA=100, afE=0.95, abA=-175, wa=93, ffx=-1, ffy=-3.0, bfx=-0.5, bfy=-2.2), 'io'))
    k.append((8, dict(lean=-88, hx=-13.8, hy=12.3, afA=98, afE=0.95, abA=-175, wa=92, ffx=-0.5, ffy=-2.2, bfx=0.5, bfy=-1.6), 'out'))
    return k


def block_keys(C):
    g = C.get('guard', {})
    a = dict(hy=1.5, lean=7, afA=105, afE=0.55, abA=80, abE=0.6, wa=170, ffx=4.5, bfx=-4.5, wx=-0.1)
    a.update(g)
    b = dict(a)
    b.update(C.get('guard2', dict(hy=2.0, lean=9)))
    return [(0, a, 'out'), (1, b, 'io')]


def mk_attack(C, n, times, A, E, Lh, X, Y=None, off=None, FF=None, hit=None, extra=None, ease=None, ext=None,
              fa=None, abA=None, abE=None, wx=None, two=None, hd=None):
    """times: (tw, ts, te, tf) = windup, strike, end, follow. A=weapon angle por clave (4).
    off: arm angle - weapon angle; E extension; Lh lean; X hip x; FF (front, back) foot x offset."""
    Y = Y or (0, 0, 0, 0)
    off = off or (0, 0, 0, 0)
    FF = FF or ((3.2, -3.2),) * 4
    keys = [(0, {}, 'io')]
    es = ease or ('io', 'in', 'lin', 'out')
    for j in range(4):
        d = dict(wa=A[j], afA=A[j] + off[j], afE=E[j], lean=Lh[j], hx=X[j], hy=Y[j],
                 ffx=X[j] + FF[j][0], bfx=X[j] + FF[j][1], ffy=-1.2, bfy=-1.2)
        if abA:
            d['abA'] = abA[j]
        if abE:
            d['abE'] = abE[j]
        if wx:
            d['wx'] = wx[j]
        if two is not None:
            d['two'] = two[j] if isinstance(two, (list, tuple)) else two
        if hd:
            d['hd'] = hd[j]
        if fa:
            d.update(fa[j])
        keys.append((times[j], d, es[j]))
    keys.append((n - 1, {'_base': 1}, 'io'))
    # primer y ultimo = carry (vacio -> hereda de la base); ultimo vuelve a la base
    return keys


def cast_keys(C, kind, n, rel, big=False):
    """Plantillas de habilidad. Devuelve claves."""
    two = C.get('two', 0.0)
    base = dict()
    if kind == 'thrust':
        k = [(0, {}, 'io'),
             (rel - 1.5, dict(lean=-6, hx=-2, hy=1.5, afA=-20, afE=0.55, wa=-10, ffx=3, bfx=-6, abA=-60), 'io'),
             (rel - 0.2, dict(lean=14, hx=5, hy=1.5, afA=88, afE=1.0, wa=88, ffx=10, bfx=-3, abA=-80, aura=0.5), 'in'),
             (rel + 1.2, dict(lean=12, hx=5.5, afA=90, afE=1.0, wa=90, ffx=10, bfx=-2.5, aura=1.0), 'out'),
             (n - 1, {'_base': 1}, 'io')]
    elif kind == 'slam':
        k = [(0, {}, 'io'),
             (rel - 1.8, dict(lean=-10, hx=-2, hy=1, afA=185, afE=0.9, wa=190, abA=170, two=1.0, ffx=2.5, bfx=-5), 'io'),
             (rel - 0.2, dict(lean=22, hx=5, hy=4, afA=40, afE=1.0, wa=30, two=1.0, ffx=11, bfx=-3, aura=0.6), 'in'),
             (rel + 1.2, dict(lean=22, hx=5, hy=4, afA=35, afE=1.0, wa=25, two=1.0, ffx=11, bfx=-3, aura=1.0), 'out'),
             (n - 1, {'_base': 1}, 'io')]
    elif kind == 'palm':
        k = [(0, {}, 'io'),
             (rel - 1.6, dict(lean=-8, hx=-2, hy=1.5, afA=60, afE=0.6, wa=100, abA=-30, abE=0.5, ffx=3, bfx=-6), 'io'),
             (rel - 0.2, dict(lean=6, hx=2, hy=1, abA=95, abE=1.0, afA=-20, afE=0.6, wa=-10, ffx=7, bfx=-4, aura=0.7), 'in'),
             (rel + 1.2, dict(lean=6, hx=2.5, abA=98, abE=1.0, afA=-15, wa=-5, aura=1.0), 'out'),
             (n - 1, {'_base': 1}, 'io')]
    else:  # sky
        k = [(0, {}, 'io'),
             (2, dict(lean=18, hx=-1, hy=5, afA=60, afE=0.6, wa=80, abA=40, abE=0.6, ffx=5, bfx=-5, aura=0.35), 'io'),
             (3.6, dict(lean=14, hx=-1, hy=6, afA=30, afE=0.5, wa=40, abA=20, ffx=6, bfx=-6, aura=0.55), 'io'),
             (rel - 0.4, dict(lean=-8, hx=-1, hy=0, afA=180, afE=1.0, wa=182, abA=170, abE=1.0, two=1.0, ffx=3.5,
                              bfx=-3.5, aura=0.9), 'in'),
             (rel + 0.6, dict(lean=-6, hx=-1, hy=-0.5, afA=178, afE=1.0, wa=180, abA=172, two=1.0, aura=1.0, burst=1.0),
              'out'),
             (rel + 2.5, dict(lean=-3, hx=-1, afA=175, afE=1.0, wa=178, two=1.0, aura=0.7, burst=0.6), 'io'),
             (n - 1, {'_base': 1}, 'io')]
    return k


def build(C, over=None):
    """Devuelve dict anim -> list of keys (sin los ataques, que son por clase)."""
    over = over or {}
    A = {}
    A['idle'] = idle_keys(C, C.get('idle_amp', 1.0), C.get('idle_arm', 3.0))
    A['run'] = run_keys(C, **C.get('run_kw', {}))
    A['jump'] = jump_keys(C)
    A['fall'] = fall_keys(C)
    A['roll'] = roll_keys(C)
    A['hurt'] = hurt_keys(C)
    A['death'] = death_keys(C)
    A['block'] = block_keys(C)
    return A
