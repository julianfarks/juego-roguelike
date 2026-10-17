"""Reposos AFK 5..10 de cada espadachin (6 nuevos por personaje, se suman a idle1..idle4). Mismo rig/convenciones que personality.py."""
import math
from personality import B, K, wrap, osc


def _hop(ts, f_up, f_dn):
    return [B(t, 'io', **(f_up if up else f_dn)) for t, up in ts]


# ----------------------------------------------------------------------------------------------- paladin
def paladin(C, name, n):
    if name == 'idle5':   # juramento: espada al cielo, columna de luz
        return wrap(n, B(2, 'io', wa=120, afA=110, afE=.9, lean=-2, hd=-4, hy=.4),
                    B(4, 'out', wa=178, afA=165, afE=1.0, lean=-5, hd=-14, hy=-.4, abA=60),
                    B(7, 'io', wa=178, afA=168, afE=1.0, lean=-6, hd=-16, hy=-.6, abA=70),
                    B(11, 'io', wa=178, afA=168, afE=1.0, lean=-6, hd=-16, hy=-.6, abA=70),
                    B(13, 'in', wa=110, afA=95, lean=1, hd=2, hy=1))
    if name == 'idle6':   # se golpea el pecho con el puño (saludo)
        return wrap(n, B(2, 'io', abA=40, abE=.7, lean=-2, hd=-3, hy=0),
                    B(3.5, 'in', abA=120, abE=.55, lean=3, hd=2, hy=1.2),
                    B(5, 'out', abA=50, abE=.8, lean=-3, hd=-4),
                    B(6.5, 'in', abA=120, abE=.55, lean=3, hd=2, hy=1.2),
                    B(9, 'io', abA=60, abE=.8, lean=-2, hd=-4, hy=0, wa=125, afA=100),
                    B(12, 'io', wa=70, afA=40, lean=0))
    if name == 'idle7':   # se mira en el reflejo del escudo y guiña
        return wrap(n, B(2, 'io', abA=95, abE=.95, lean=-3, hd=4, hy=.8),
                    B(4, 'io', abA=98, abE=.95, lean=2, hd=7, hy=1.4),
                    B(9, 'io', abA=98, abE=.95, lean=2, hd=7, hy=1.4),
                    B(10.5, 'out', abA=98, abE=.95, lean=-4, hd=-6, hy=.2),
                    B(13, 'io', abA=60, lean=0, hd=0))
    if name == 'idle8':   # achis! (estornudo con armadura)
        return wrap(n, B(2, 'io', lean=-3, hd=-14, hy=-.6),
                    B(4, 'io', lean=-6, hd=-22, hy=-1.2),
                    B(5.5, 'out', lean=14, hd=14, hy=3.5, afA=50, abA=70, abE=.7),
                    B(7, 'io', lean=10, hd=10, hy=3, abA=70),
                    B(9, 'io', lean=3, hd=4, hy=1, abA=45),
                    B(12, 'io', lean=1, hd=-2, hy=.2))
    if name == 'idle9':   # equilibra la espada sobre la palma
        return wrap(n, B(2, 'io', two=0, wa=178, afA=70, afE=.7, abA=40, lean=1, hd=-12, hy=.5),
                    B(4, 'io', two=0, wa=170, afA=72, afE=.7, abA=40, lean=3, hd=-14, hy=.8),
                    B(6, 'io', two=0, wa=186, afA=68, afE=.7, abA=40, lean=-2, hd=-14, hy=.4),
                    B(8, 'io', two=0, wa=168, afA=74, afE=.7, abA=40, lean=4, hd=-14, hy=1),
                    B(10, 'io', two=0, wa=190, afA=66, afE=.7, abA=40, lean=-3, hd=-14, hy=.4, ffx=3.5),
                    B(11.5, 'out', two=0, wa=130, afA=100, afE=.9, abA=55, lean=4, hd=0, hy=1.5, ffx=4),
                    B(13, 'io', wa=80, afA=60, lean=2))
    return wrap(n, *[B(t, 'io', hy=hy, lean=2 + hy * .5, hd=0, ffx=4.8, bfx=-4.8, abA=58, abE=.8)
                     for t, hy in ((1.5, 0), (3, 4.6), (4.5, 0), (6, 4.6), (7.5, 0), (9, 4.6), (10.5, 0), (12, 2))])


# ----------------------------------------------------------------------------------------------- shadow
def shadow(C, name, n):
    if name == 'idle5':   # malabares con dos dagas
        ks = []
        for t, a, b in ((1.5, 60, 120), (3, 175, 90), (4.5, 95, 180), (6, 180, 80), (7.5, 85, 182), (9, 178, 95), (10.5, 90, 150), (12, 70, 90)):
            ks.append(B(t, 'io', wa=a, wb=b, afA=(150 if a > 120 else 90), abA=(150 if b > 120 else 90), afE=.9, abE=.9, lean=3, hd=-12, hy=.6))
        return wrap(n, *ks)
    if name == 'idle6':   # se vuelve casi invisible
        return wrap(n, B(2, 'io', lean=10, hy=3, hd=2, afA=60, abA=45),
                    B(4, 'io', lean=14, hy=5, hd=0, afA=50, abA=60, wa=95, wb=95),
                    B(9, 'io', lean=14, hy=5, hd=0, afA=50, abA=60, wa=95, wb=95),
                    B(11, 'out', lean=6, hy=1, hd=-4),
                    B(13, 'io', lean=11, hy=1))
    if name == 'idle7':   # esconde las dagas a la espalda y silba
        return wrap(n, B(2, 'io', afA=-30, abA=-40, afE=.7, abE=.7, wa=250, wb=250, lean=-2, hd=-8, hy=0),
                    B(4, 'io', afA=-32, abA=-40, afE=.7, abE=.7, wa=250, wb=250, lean=-3, hd=-14, hy=-.3, ffx=3),
                    B(7, 'io', afA=-32, abA=-40, afE=.7, abE=.7, wa=250, wb=250, lean=-1, hd=-8, hy=.3, bfy=-2, ffx=3),
                    B(9, 'io', afA=-32, abA=-40, afE=.7, abE=.7, wa=250, wb=250, lean=-3, hd=-14, hy=-.3, ffx=3, bfy=0),
                    B(11, 'io', afA=-32, abA=-40, wa=250, wb=250, lean=-1, hd=-4, hy=.3, bfy=-2),
                    B(13, 'io', lean=9, hd=0))
    if name == 'idle8':   # cuenta monedas robadas
        return wrap(n, B(2, 'io', abA=75, abE=.8, lean=10, hd=8, hy=2),
                    B(4, 'io', abA=100, abE=.85, lean=12, hd=11, hy=2.6),
                    B(6, 'io', abA=100, abE=.85, lean=12, hd=11, hy=2.6),
                    B(7.5, 'io', abA=100, abE=.85, lean=8, hd=-14, hy=1.2),
                    B(9, 'io', abA=100, abE=.85, lean=12, hd=11, hy=2.6),
                    B(11, 'io', abA=40, abE=.7, lean=8, hd=-10, hy=1),
                    B(13, 'io', lean=10, hd=0))
    if name == 'idle9':   # agachado, asoma la cabeza (acecha)
        return wrap(n, B(2, 'io', lean=18, hy=7, hd=4, afA=60, abA=40, ffx=6, bfx=-6),
                    B(4, 'io', lean=26, hy=10, hd=-14, afA=65, abA=50, wa=100, ffx=7, bfx=-7),
                    B(7, 'io', lean=28, hy=10, hd=-18, afA=65, abA=50, wa=100, ffx=7, bfx=-7, hx=2),
                    B(10, 'io', lean=26, hy=10, hd=-14, afA=65, abA=50, wa=100, ffx=7, bfx=-7, hx=-1),
                    B(12, 'io', lean=14, hy=4, hd=0))
    return wrap(n, B(2, 'io', afA=35, wa=15, lean=12, hy=4, hd=6),     # clava la daga en el suelo, una y otra vez
                B(3, 'in', afA=25, wa=2, lean=18, hy=5.5, hd=8),
                B(4, 'out', afA=60, wa=70, lean=10, hy=2.5),
                B(5, 'in', afA=25, wa=2, lean=18, hy=5.5, hd=8),
                B(6, 'out', afA=60, wa=70, lean=10, hy=2.5),
                B(7.5, 'in', afA=25, wa=2, lean=18, hy=5.5, hd=8),
                B(10, 'io', afA=60, wa=85, lean=6, hd=-6, hy=1.5, bfy=-3),
                B(12, 'io', lean=11, hd=0))


# ----------------------------------------------------------------------------------------------- flame
def flame(C, name, n):
    if name == 'idle5':   # malabares con 3 bolas de fuego
        ks = []
        for k, t in enumerate((1.5, 3, 4.5, 6, 7.5, 9, 10.5, 12)):
            up = k % 2
            ks.append(B(t, 'io', two=0, wa=200, afA=20, abA=(135 if up else 70), abE=.9, lean=1, hd=-10 - 3 * up, hy=.5 - up))
        return wrap(n, *ks)
    if name == 'idle6':   # enciende la espada y la apaga soplando
        return wrap(n, B(2, 'io', two=0, wa=110, afA=80, afE=.8, abA=50, lean=2, hd=4, hy=.8),
                    B(4, 'out', two=0, wa=150, afA=120, afE=.9, abA=70, lean=-3, hd=-6),
                    B(7, 'io', two=0, wa=150, afA=120, afE=.9, abA=70, lean=-3, hd=-4),
                    B(9, 'io', two=0, wa=110, afA=84, afE=.85, abA=50, lean=5, hd=8, hy=1.5),
                    B(11, 'out', two=0, wa=105, afA=84, afE=.85, abA=50, lean=9, hd=10, hy=2.4),
                    B(13, 'io', two=1, wa=C['wa'], afA=50))
    if name == 'idle7':   # asa un malvavisco en la punta de la espada
        return wrap(n, B(2, 'io', two=0, wa=62, afA=75, afE=.85, abA=40, lean=3, hd=3, hy=3, ffx=5, bfx=-5),
                    B(4, 'io', two=0, wa=56, afA=70, afE=.85, abA=55, lean=5, hd=8, hy=4, ffx=5, bfx=-5),
                    B(8, 'io', two=0, wa=56, afA=70, afE=.85, abA=55, lean=5, hd=8, hy=4, ffx=5, bfx=-5),
                    B(10, 'out', two=0, wa=75, afA=80, afE=.7, abA=95, abE=.9, lean=7, hd=10, hy=3.5),
                    B(11, 'io', two=0, wa=68, afA=64, afE=.7, abA=95, abE=.7, lean=6, hd=-4, hy=2),
                    B(12.5, 'io', two=0, wa=64, afA=55, afE=.75, abA=60, lean=4, hy=1))
    if name == 'idle8':   # hipo con llamitas
        ks = [B(1.5, 'io', lean=2, hd=-2)]
        for t, up in ((3, 1), (3.8, 0), (6, 1), (6.8, 0), (9, 1), (9.8, 0)):
            ks.append(B(t, 'io', hy=(-1.6 if up else .4), lean=(-5 if up else 3), hd=(-12 if up else 4), abA=(100 if up else 60), abE=.6))
        ks.append(B(12, 'io', lean=1, hd=0))
        return wrap(n, *ks)
    if name == 'idle9':   # pose de poder: puños apretados, aura
        return wrap(n, B(2, 'io', two=0, wa=200, afA=25, abA=20, abE=.7, lean=8, hd=4, hy=3.4, ffx=5.5, bfx=-5.5),
                    B(4, 'out', two=0, wa=200, afA=-5, afE=.6, abA=-20, abE=.6, lean=-8, hd=-16, hy=-.4, ffx=6, bfx=-6),
                    B(7, 'io', two=0, wa=200, afA=-5, afE=.6, abA=-20, abE=.6, lean=-8, hd=-16, hy=-.2, ffx=6, bfx=-6),
                    B(10, 'io', two=0, wa=200, afA=-5, afE=.6, abA=-20, abE=.6, lean=-8, hd=-16, hy=-.4, ffx=6, bfx=-6),
                    B(12.5, 'in', two=1, wa=C['wa'], lean=3, hy=1))
    return wrap(n, B(2, 'io', wa=100, afA=100, afE=.88, lean=4, hd=-2, hy=.6, abA=70),   # dibuja una espiral de fuego en el aire
                B(3.5, 'io', wa=160, afA=140, afE=.9, lean=-1, hd=-8, abA=70),
                B(5, 'io', wa=200, afA=150, afE=.9, lean=-3, hd=-10, abA=70),
                B(6.5, 'io', wa=140, afA=130, afE=1.0, lean=-1, hd=-6, abA=70),
                B(8, 'io', wa=90, afA=95, afE=.82, lean=4, hd=0, abA=70),
                B(9.5, 'io', wa=150, afA=135, afE=1.0, lean=0, hd=-8),
                B(11, 'io', wa=185, afA=150, afE=1.0, lean=-2, hd=-10),
                B(13, 'io', wa=120, afA=90))


# ----------------------------------------------------------------------------------------------- storm
def storm(C, name, n):
    if name == 'idle5':   # giro de estoque con saltito
        return wrap(n, B(2, 'io', wa=60, afA=60, lean=12, hy=3, ffx=5, bfx=-5),
                    B(3.5, 'out', wa=120, afA=100, lean=2, hy=-1.8, ffy=-3, bfy=-3, hd=-4),
                    B(4.7, 'out', wa=210, afA=170, lean=-4, hy=-2.4, ffy=-3, bfy=-3, hd=-6),
                    B(6, 'out', wa=300, afA=230, lean=6, hy=-1.2, ffy=-2, bfy=-2),
                    B(7.3, 'out', wa=400, afA=300, lean=12, hy=1.5, ffy=-.5),
                    B(9, 'io', wa=420, afA=60, lean=12, hy=3, ffx=5, bfx=-5),
                    B(12, 'io', wa=88, afA=80, lean=9, hy=0))
    if name == 'idle6':   # electricidad estatica: se frota y pelo/chispas
        ks = [B(2, 'io', afA=60, afE=.6, abA=70, abE=.6, lean=8, hd=4, hy=1.5)]
        for k, t in enumerate(range(3, 10)):
            ks.append(B(t, 'io', afA=60 + (10 if k % 2 else -4), afE=.6, abA=70 + (-12 if k % 2 else 8), abE=.6, lean=8, hd=4, hy=1.5 + (.4 if k % 2 else 0)))
        ks += [B(10.5, 'out', afA=-30, abA=-60, lean=-4, hd=-8, hy=-.6), B(12.5, 'io', lean=7, hd=0)]
        return wrap(n, *ks)
    if name == 'idle7':   # invoca una nubecita sobre su cabeza
        return wrap(n, B(2, 'io', abA=110, abE=.9, lean=-2, hd=-12, hy=.4),
                    B(4, 'out', abA=170, abE=1.0, lean=-5, hd=-18, hy=-.4),
                    B(7, 'io', abA=170, abE=1.0, lean=-5, hd=-18, hy=-.4),
                    B(10, 'io', abA=150, abE=.9, lean=-2, hd=-8, hy=.6, afA=100),
                    B(12, 'io', abA=100, lean=3, hd=6, hy=1, afA=70),
                    B(13.5, 'io', lean=6, hd=0))
    if name == 'idle8':   # atrapa un rayo y lo observa
        return wrap(n, B(2, 'io', abA=150, abE=1.0, lean=-5, hd=-14, hy=-.3),
                    B(3.5, 'in', abA=90, abE=.9, lean=6, hd=8, hy=1.5),
                    B(5, 'io', abA=100, abE=.8, lean=7, hd=12, hy=2),
                    B(9, 'io', abA=104, abE=.8, lean=7, hd=12, hy=2),
                    B(10.5, 'out', abA=100, abE=.8, lean=8, hd=-2, hy=2.2, hx=1),
                    B(12, 'io', abA=40, lean=8, hd=0, hy=.6))
    if name == 'idle9':   # tres tajos rapidos que dibujan una Z
        return wrap(n, B(2, 'io', wa=170, afA=150, afE=.95, lean=8, hy=1.5, ffx=5, bfx=-5, hd=-6),
                    B(3, 'out', wa=75, afA=90, afE=.8, lean=12, hy=2, hd=0),
                    B(4.2, 'io', wa=170, afA=150, afE=.95, lean=8, hy=1.5, hd=-6),
                    B(5.2, 'out', wa=40, afA=40, afE=.72, lean=15, hy=3, hd=4),
                    B(6.4, 'io', wa=170, afA=150, afE=.95, lean=8, hy=1.5, hd=-6),
                    B(7.4, 'out', wa=75, afA=90, afE=.8, lean=12, hy=2, hd=0),
                    B(10, 'io', wa=88, afA=80, lean=6, hy=.5),
                    B(12, 'io', lean=9))
    return wrap(n, *[B(t, 'io', hy=(-2.0 if up else 2.0), lean=18, hd=-2, ffx=(7 if up else -4), bfx=(-4 if up else 7),
                       ffy=(-6 if up else -.6), bfy=(-.6 if up else -6), afA=(125 if up else 5), abA=(-110 if up else 130), abE=.85)
                     for t, up in ((1, 0), (2, 1), (3, 0), (4, 1), (5, 0), (6, 1), (7, 0), (8, 1), (9, 0), (10, 1), (11, 0))])


# ----------------------------------------------------------------------------------------------- frost
def frost(C, name, n):
    if name == 'idle5':   # muñeco de nieve en miniatura
        return wrap(n, B(2, 'io', two=0, wa=35, lean=14, hy=7, hd=8, abA=80, abE=.9, afA=30, ffx=4, bfx=-4),
                    B(4, 'io', two=0, wa=35, lean=18, hy=9, hd=10, abA=105, abE=.95, afA=30, ffx=4, bfx=-4),
                    B(7, 'io', two=0, wa=35, lean=18, hy=9, hd=10, abA=108, abE=.95, afA=30, ffx=4, bfx=-4),
                    B(10, 'io', two=0, wa=35, lean=18, hy=9, hd=8, abA=105, abE=.95, afA=30, ffx=4, bfx=-4),
                    B(12, 'io', two=0, wa=35, lean=6, hy=2, hd=4, abA=60),
                    B(13.5, 'io', lean=3))
    if name == 'idle6':   # patina sobre hielo
        ks = []
        for t, d in ((1.5, 1), (3, -1), (4.5, 1), (6, -1), (7.5, 1), (9, -1), (10.5, 1)):
            ks.append(B(t, 'io', lean=12, hy=2.6, hd=0, ffx=5 * d, bfx=-5 * d, hx=1.5 * d, afA=70 + 20 * d, abA=-60 - 30 * d, abE=.8))
        return wrap(n, *ks)
    if name == 'idle7':   # estornuda copos de nieve
        return wrap(n, B(2, 'io', lean=-3, hd=-14, hy=-.6),
                    B(4, 'io', lean=-6, hd=-22, hy=-1.2),
                    B(5.5, 'out', lean=14, hd=14, hy=3.5, abA=95, abE=.6),
                    B(7, 'io', lean=10, hd=10, hy=3, abA=95, abE=.6),
                    B(10, 'io', lean=4, hd=3, hy=1, abA=60),
                    B(12, 'io', lean=2, hd=-2))
    if name == 'idle8':   # una mariposa se posa y se congela en su dedo
        return wrap(n, B(2, 'io', abA=95, abE=.95, lean=0, hd=-8, hy=.6),
                    B(4, 'io', abA=100, abE=1.0, lean=1, hd=0, hy=.8),
                    B(7, 'io', abA=100, abE=1.0, lean=3, hd=6, hy=1.2),
                    B(10, 'io', abA=100, abE=1.0, lean=3, hd=6, hy=1.2),
                    B(11.5, 'out', abA=125, abE=1.0, lean=-2, hd=-8, hy=.2),
                    B(13, 'io', abA=60, lean=3))
    if name == 'idle9':   # dibuja su marca en el suelo con escarcha
        return wrap(n, B(2, 'io', two=0, wa=35, lean=16, hy=6, hd=8, abA=40, ffx=4, bfx=-4, afA=30),
                    B(3.5, 'io', two=0, wa=35, lean=20, hy=8, hd=11, abA=15, abE=1.0, ffx=4, bfx=-4, afA=30),
                    *osc(5, 11, 1.6, lambda k: dict(two=0, wa=35, lean=20, hy=8, hd=11, abA=12 + (6 if k % 2 else -4), abE=1.0, ffx=4, bfx=-4, afA=30)),
                    B(12.5, 'io', lean=8, hy=2, hd=2, abA=50))
    return wrap(n, B(2, 'io', lean=8, hd=6, hy=2),                       # dormita de pie
                B(4, 'io', lean=14, hd=16, hy=4),
                B(5.5, 'io', lean=20, hd=22, hy=6),
                B(6.5, 'out', lean=2, hd=-4, hy=.4),
                B(8, 'io', lean=16, hd=18, hy=5),
                B(10, 'io', lean=22, hd=24, hy=6.4),
                B(11, 'out', lean=-1, hd=-6, hy=0),
                B(13, 'io', lean=4, hd=0))


# ----------------------------------------------------------------------------------------------- verdant
def verdant(C, name, n):
    if name == 'idle5':   # planta una semilla, la riega y brota
        return wrap(n, B(2, 'io', two=0, lean=16, hy=7, hd=8, abA=70, abE=.9, ffx=4, bfx=-4),
                    B(3.5, 'io', two=0, lean=20, hy=9, hd=11, abA=20, abE=1.0, ffx=4, bfx=-4),
                    B(5, 'io', two=0, lean=18, hy=8, hd=10, abA=15, abE=1.0, ffx=4, bfx=-4),
                    B(7, 'io', two=0, lean=16, hy=7, hd=10, abA=75, abE=.95, ffx=4, bfx=-4),
                    B(11, 'io', two=0, lean=12, hy=5, hd=10, abA=75, abE=.95, ffx=4, bfx=-4),
                    B(13, 'io', lean=2, hy=1, hd=-4))
    if name == 'idle6':   # una mariposa se posa en la espada
        return wrap(n, B(2, 'io', wa=100, afA=90, afE=.9, lean=1, hd=-6, hy=.4),
                    B(4, 'io', wa=102, afA=92, afE=.95, lean=2, hd=2, hy=.8),
                    B(10, 'io', wa=102, afA=92, afE=.95, lean=3, hd=6, hy=1.2),
                    B(12, 'out', wa=130, afA=110, afE=.9, lean=-2, hd=-10, hy=.2),
                    B(13.5, 'io', wa=70, afA=50))
    if name == 'idle7':   # toca el suelo y crecen flores en circulo
        return wrap(n, B(2, 'io', two=0, lean=14, hy=6, hd=6, abA=60, ffx=4, bfx=-4),
                    B(3.5, 'in', two=0, lean=22, hy=9.5, hd=10, abA=8, abE=1.0, ffx=4, bfx=-4),
                    B(9, 'io', two=0, lean=22, hy=9.5, hd=10, abA=8, abE=1.0, ffx=4, bfx=-4),
                    B(11, 'out', two=0, lean=4, hy=0, hd=-10, abA=95, abE=1.0),
                    B(13, 'io', lean=3, hy=.6, hd=-4))
    if name == 'idle8':   # fotosintesis: brazos abiertos al sol
        return wrap(n, B(2, 'io', two=0, afA=100, abA=110, afE=.9, abE=.9, lean=-2, hd=-10, hy=.4),
                    B(4, 'out', two=0, afA=160, abA=-150, afE=1.0, abE=1.0, lean=-6, hd=-22, hy=-.5, ffx=5, bfx=-5),
                    B(9, 'io', two=0, afA=160, abA=-150, afE=1.0, abE=1.0, lean=-6, hd=-22, hy=-.5, ffx=5, bfx=-5),
                    B(11, 'io', two=0, afA=130, abA=-110, lean=-3, hd=-12),
                    B(13, 'io', two=1, lean=2, hd=0))
    if name == 'idle9':   # un pajarito se posa en su brazo
        return wrap(n, B(2, 'io', two=0, afA=80, afE=.95, abA=40, lean=0, hd=-4, hy=.4),
                    B(4, 'io', two=0, afA=88, afE=1.0, abA=40, lean=2, hd=4, hy=.8),
                    B(8, 'io', two=0, afA=88, afE=1.0, abA=40, lean=3, hd=8, hy=1.2),
                    B(11, 'out', two=0, afA=130, afE=1.0, abA=40, lean=-2, hd=-8, hy=.2),
                    B(13, 'io', two=1, afA=50))
    return wrap(n, B(2, 'io', lean=-2, hd=-12, hy=0),                    # estornuda polen
                B(4, 'io', lean=-6, hd=-22, hy=-1.2),
                B(5.5, 'out', lean=14, hd=14, hy=3.5, abA=95, abE=.6),
                B(7, 'io', lean=10, hd=10, hy=3, abA=95, abE=.6),
                B(10, 'io', lean=4, hd=3, hy=1, abA=60),
                B(12, 'io', lean=2, hd=-2))


# ----------------------------------------------------------------------------------------------- blood
def blood(C, name, n):
    if name == 'idle5':   # vals con la guadaña
        ks = []
        for k, t in enumerate((1.5, 3.5, 5.5, 7.5, 9.5, 11.5)):
            d = 1 if k % 2 == 0 else -1
            ks.append(B(t, 'io', wa=60 + 70 * (k + 1) * .6, afA=60 + 20 * d, lean=6 * d, hx=2 * d, ffx=5 * d, bfx=-5 * d, hy=1 + (k % 2), hd=-3 * d))
        return wrap(n, *ks)
    if name == 'idle6':   # cuenta las gotas que caen de la hoja
        return wrap(n, B(2, 'io', wa=118, afA=80, afE=.8, lean=2, hd=8, hy=.8),
                    B(4, 'io', wa=122, afA=82, afE=.8, abA=80, abE=.9, lean=4, hd=11, hy=1.4),
                    B(6, 'io', wa=122, afA=82, abA=84, abE=.9, lean=5, hd=15, hy=2),
                    B(8, 'io', wa=122, afA=82, abA=86, abE=.9, lean=6, hd=19, hy=2.6),
                    B(10, 'io', wa=122, afA=82, abA=88, abE=.9, lean=7, hd=22, hy=3),
                    B(12, 'out', wa=100, afA=70, abA=40, lean=2, hd=-4, hy=.4))
    if name == 'idle7':   # se mira las unas, aburrido
        return wrap(n, B(2, 'io', two=0, wa=15, afA=15, abA=100, abE=.55, lean=-2, hd=8, hy=1),
                    B(4, 'io', two=0, wa=15, afA=15, abA=108, abE=.55, lean=0, hd=14, hy=1.4),
                    B(7, 'io', two=0, wa=15, afA=15, abA=112, abE=.55, lean=1, hd=16, hy=1.6),
                    B(9, 'out', two=0, wa=15, afA=15, abA=60, abE=.8, lean=-4, hd=-4, hy=.4),
                    B(11, 'io', two=0, wa=15, afA=15, abA=105, abE=.55, lean=0, hd=14, hy=1.4),
                    B(13, 'io', lean=2, hd=0))
    if name == 'idle8':   # dibuja un sigilo de sangre en el aire
        return wrap(n, B(2, 'io', wa=100, afA=100, afE=1.0, lean=3, hd=-4, hy=.6),
                    B(3.5, 'io', wa=150, afA=130, afE=1.0, lean=0, hd=-8),
                    B(5, 'io', wa=190, afA=150, afE=1.0, lean=-3, hd=-12),
                    B(6.5, 'io', wa=150, afA=130, afE=1.0, lean=0, hd=-8),
                    B(8, 'io', wa=100, afA=100, afE=1.0, lean=3, hd=-4),
                    B(10, 'io', wa=130, afA=118, afE=1.0, lean=0, hd=-8),
                    B(11.5, 'out', wa=100, afA=100, afE=1.0, lean=4, hd=-2),
                    B(13, 'io', wa=70, afA=60))
    if name == 'idle9':   # gesto de degollar y señala
        return wrap(n, B(2, 'io', two=0, wa=60, afA=-10, abA=90, abE=.8, lean=2, hd=-2, hy=.4),
                    B(3.5, 'io', two=0, wa=60, abA=125, abE=.75, lean=0, hd=-4),
                    B(5, 'out', two=0, wa=60, abA=55, abE=.75, lean=4, hd=0),
                    B(7, 'io', two=0, wa=60, abA=125, abE=.75, lean=0, hd=-4),
                    B(8.5, 'out', two=0, wa=60, abA=55, abE=.75, lean=4),
                    B(10.5, 'io', two=0, wa=60, abA=95, abE=1.0, lean=6, hd=4, hy=1.2),
                    B(13, 'io', lean=2, hd=0))
    return wrap(n, B(2, 'io', wa=100, afA=70, lean=4, hd=-10, hy=.6),   # manotazo a una mosca
                B(3.5, 'io', wa=100, afA=70, lean=2, hd=-16, hy=.2),
                B(4.7, 'out', wa=170, afA=130, afE=1.0, lean=10, hd=-4, hy=1.8, ffx=6),
                B(6, 'io', wa=60, afA=50, lean=6, hd=-12, hy=1),
                B(8, 'io', wa=100, afA=70, lean=2, hd=-18),
                B(9.2, 'out', wa=40, afA=40, afE=1.0, lean=14, hd=4, hy=2.4, ffx=6),
                B(11, 'io', wa=90, afA=60, lean=4, hd=10, hy=1.4),
                B(13, 'io', lean=3, hd=0))


# ----------------------------------------------------------------------------------------------- earth
def earth(C, name, n):
    if name == 'idle5':   # se rasca la cabeza ante una piedra
        return wrap(n, B(2, 'io', two=0, abA=160, abE=.55, lean=4, hd=10, hy=1.4),
                    *osc(3, 8, 1, lambda k: dict(two=0, abA=165 + (10 if k % 2 else -8), abE=.52, lean=4, hd=11, hy=1.4)),
                    B(10, 'io', two=0, abA=50, abE=.8, lean=8, hd=16, hy=2.6),
                    B(12, 'out', two=0, abA=70, lean=-2, hd=-6, hy=0, afA=60))
    if name == 'idle6':   # levanta una roca, la lanza y la atrapa
        return wrap(n, B(2, 'io', two=0, lean=16, hy=6, hd=8, abA=40, ffx=4, bfx=-4),
                    B(3.5, 'io', two=0, lean=20, hy=8, hd=10, abA=10, abE=1.0, ffx=4, bfx=-4),
                    B(5, 'out', two=0, lean=-4, hy=-1, hd=-10, abA=150, abE=1.0, ffy=-1.4, bfy=-1.4),
                    B(7, 'io', two=0, lean=-6, hy=0, hd=-18, abA=165, abE=.9),
                    B(9, 'in', two=0, lean=6, hy=2, hd=0, abA=85, abE=.85),
                    B(10.5, 'io', two=0, lean=8, hy=1.6, hd=10, abA=85, abE=.85),
                    B(13, 'io', lean=3, hd=0, two=1))
    if name == 'idle7':   # golpe de pecho de gorila
        return wrap(n, B(2, 'io', two=0, afA=130, abA=120, afE=.65, abE=.65, lean=-6, hd=-10, hy=-.4, ffx=5, bfx=-5),
                    B(3.2, 'in', two=0, afA=95, abA=100, afE=.5, abE=.5, lean=4, hd=0, hy=1.6),
                    B(4.4, 'out', two=0, afA=130, abA=120, afE=.65, abE=.65, lean=-6, hd=-10, hy=-.4),
                    B(5.6, 'in', two=0, afA=95, abA=100, afE=.5, abE=.5, lean=4, hd=0, hy=1.6),
                    B(7, 'out', two=0, afA=150, abA=150, afE=.8, abE=.8, lean=-10, hd=-24, hy=-.6),
                    B(10, 'io', two=0, afA=150, abA=150, afE=.8, abE=.8, lean=-10, hd=-24, hy=-.6),
                    B(12, 'io', two=1, lean=2, hd=0))
    if name == 'idle8':   # apila piedritas
        return wrap(n, B(2, 'io', two=0, lean=18, hy=8, hd=10, abA=60, abE=.9, ffx=4, bfx=-4),
                    B(3.5, 'io', two=0, lean=22, hy=10, hd=12, abA=15, abE=1.0, ffx=4, bfx=-4),
                    B(5, 'io', two=0, lean=20, hy=9, hd=13, abA=50, abE=.9, ffx=4, bfx=-4),
                    B(6.5, 'io', two=0, lean=22, hy=10, hd=12, abA=22, abE=1.0, ffx=4, bfx=-4),
                    B(8, 'io', two=0, lean=20, hy=9, hd=13, abA=55, abE=.9, ffx=4, bfx=-4),
                    B(9.5, 'io', two=0, lean=22, hy=10, hd=12, abA=30, abE=1.0, ffx=4, bfx=-4),
                    B(11.5, 'out', two=0, lean=4, hy=1, hd=-8, abA=130, abE=1.0),
                    B(13, 'io', lean=3, two=1))
    if name == 'idle9':   # oreja al suelo: ¿tiembla algo?
        return wrap(n, B(2, 'io', two=0, lean=22, hy=8, hd=6, abA=30, abE=.9, ffx=4, bfx=-4),
                    B(4, 'io', two=0, lean=34, hy=12, hd=14, abA=10, abE=1.0, ffx=5, bfx=-5),
                    B(10, 'io', two=0, lean=34, hy=12, hd=14, abA=10, abE=1.0, ffx=5, bfx=-5),
                    B(11, 'out', two=0, lean=-4, hy=-.6, hd=-14, abA=150, abE=.8),
                    B(13, 'io', two=1, lean=2, hd=-2))
    return wrap(n, B(2, 'io', lean=-4, hd=-6),                          # patada al suelo, cae una piedra en la cabeza
                B(3.2, 'in', lean=8, hy=1.5, bfy=-4, ffx=7),
                B(4.3, 'out', lean=-2, hy=.5, ffx=7),
                B(7, 'io', lean=-4, hd=-20, hy=0),
                B(8.5, 'out', lean=10, hy=5, hd=14, abA=150, abE=.7),
                B(10, 'io', lean=8, hy=4, hd=10, abA=160, abE=.55),
                B(12, 'io', lean=2, hy=1, hd=0))


# ----------------------------------------------------------------------------------------------- astral
def astral(C, name, n):
    if name == 'idle5':   # sistema solar en miniatura
        return wrap(n, B(2, 'io', two=0, abA=80, abE=.9, lean=0, hd=-4, hy=.5),
                    B(4, 'io', two=0, abA=105, abE=.95, lean=2, hd=4, hy=.8),
                    *osc(5, 11, 2, lambda k: dict(two=0, abA=105 + (4 if k % 2 else -4), abE=.95, lean=2, hd=6 + k, hy=.8)),
                    B(13, 'io', two=1, abA=50, lean=2))
    if name == 'idle6':   # atrapa una estrella fugaz
        return wrap(n, B(2, 'io', two=0, lean=-4, hd=-18, hy=.2, abA=110, abE=.9),
                    B(4, 'out', two=0, lean=-7, hd=-22, hy=-.6, abA=165, abE=1.0),
                    B(5.5, 'in', two=0, lean=4, hd=6, hy=1.4, abA=100, abE=.8),
                    B(7, 'io', two=0, lean=6, hd=12, hy=1.8, abA=104, abE=.75),
                    B(10, 'io', two=0, lean=6, hd=12, hy=1.8, abA=104, abE=.75),
                    B(12, 'out', two=0, lean=-2, hd=-14, hy=.2, abA=130, abE=.9),
                    B(13.5, 'io', two=1, lean=2))
    if name == 'idle7':   # mira con las manos como telescopio
        return wrap(n, B(2, 'io', two=0, afA=108, abA=100, afE=.5, abE=.5, lean=-3, hd=-12, hy=.6),
                    B(4, 'io', two=0, afA=118, abA=112, afE=.5, abE=.5, lean=-4, hd=-18, hy=.8, hx=1),
                    B(7, 'io', two=0, afA=130, abA=124, afE=.5, abE=.5, lean=-5, hd=-22, hy=.8, hx=2),
                    B(10, 'io', two=0, afA=112, abA=104, afE=.5, abE=.5, lean=-3, hd=-14, hy=.6, hx=0),
                    B(12, 'out', two=0, afA=60, abA=50, lean=2, hd=4, hy=0),
                    B(13.5, 'io', two=1))
    if name == 'idle8':   # parpadeo: desaparece y reaparece a un lado
        return wrap(n, B(2, 'io', two=0, abA=70, abE=.9, lean=2, hd=-4),
                    B(4, 'out', two=0, abA=110, abE=.9, lean=-4, hd=-8, hy=-.5),
                    B(6, 'io', two=0, hx=0),
                    B(7, 'in', two=0, hx=5, lean=0, hy=.2),
                    B(10, 'io', two=0, abA=70, abE=.9, lean=2, hd=-4, hx=5),
                    B(11, 'io', two=0, hx=0, abA=110, hd=-8),
                    B(13, 'io', two=1, hx=0))
    if name == 'idle9':   # abre un portal con el dedo y se asoma
        return wrap(n, B(2, 'io', two=0, abA=60, abE=.9, lean=2, hd=0, hy=.4),
                    B(3.5, 'io', two=0, abA=95, abE=1.0, lean=1, hd=-2),
                    B(5, 'io', two=0, abA=125, abE=1.0, lean=-1, hd=-6),
                    B(6.5, 'io', two=0, abA=150, abE=1.0, lean=-2, hd=-8),
                    B(8, 'io', two=0, abA=120, abE=1.0, lean=-1, hd=-4),
                    B(10, 'io', two=0, abA=95, abE=1.0, lean=6, hd=6, hy=1.4, hx=1.5),
                    B(12, 'io', two=1, hx=0))
    return wrap(n, B(2, 'io', lean=4, hd=6, hy=1),                      # se sacude: cae polvo de estrellas
                *osc(3, 9, 1, lambda k: dict(lean=4, hd=10 if k % 2 else -10, hy=1, hx=(1.5 if k % 2 else -1.5))),
                B(10.5, 'io', lean=3, hd=-4),
                B(12.5, 'io', lean=2, hd=0, hx=0))


# ----------------------------------------------------------------------------------------------- steel
def steel(C, name, n):
    if name == 'idle5':   # engrasa la articulacion del brazo (gira) con chispas
        return wrap(n, *[B(t, 'io', afA=a, afE=.7, abA=a2, abE=.7, lean=8 - (a // 40) * 3, hd=10 - (a // 30) * 2, hy=1.5 + (a // 50) * .8, hx=(a // 60) * 1.0)
                         for t, a, a2 in ((2, 20, 40), (3.5, 60, 20), (5, 100, -10), (6.5, 140, -40), (8, 100, -10), (9.5, 60, 20), (11, 25, 45))])
    if name == 'idle6':   # golpea un lado de la cabeza como una tele vieja
        return wrap(n, B(2, 'io', abA=100, abE=.6, lean=2, hd=8, hy=.6),
                    B(3.2, 'in', abA=128, abE=.55, lean=10, hd=22, hy=2.4, hx=-1),
                    B(4.2, 'out', abA=100, abE=.6, lean=-6, hd=-12, hx=1),
                    B(5.4, 'in', abA=128, abE=.55, lean=10, hd=22, hy=2.4, hx=-1),
                    B(7, 'io', abA=100, abE=.6, lean=0, hd=2),
                    B(9, 'io', abA=60, abE=.8, lean=0, hd=-8, hy=.2),
                    B(12, 'io', lean=3, hd=0))
    if name == 'idle7':   # exhibe biceps
        return wrap(n, B(2, 'io', two=0, afA=110, afE=.5, abA=-40, abE=.5, lean=-2, hd=-4, hy=.4, ffx=5, bfx=-5),
                    B(4, 'out', two=0, afA=150, afE=.5, abA=-120, abE=.5, lean=-5, hd=-12, hy=-.4, ffx=5.5, bfx=-5.5),
                    B(8, 'io', two=0, afA=150, afE=.5, abA=-120, abE=.5, lean=-5, hd=-12, hy=-.4, ffx=5.5, bfx=-5.5),
                    B(10, 'out', two=0, afA=40, afE=.5, abA=-40, abE=.5, lean=-2, hd=-4, hy=.4),
                    B(12, 'io', two=1, lean=3, hd=0))
    if name == 'idle8':   # mira en pasos mecanicos
        return wrap(n, B(2, 'io', hd=-14), B(2.5, 'io', hd=-14), B(3.3, 'io', hd=0), B(5, 'io', hd=0),
                    B(5.8, 'io', hd=12), B(8, 'io', hd=12), B(8.8, 'io', hd=-10), B(10.5, 'io', hd=-10),
                    B(11.3, 'io', hd=0), B(13, 'io', hd=0))
    if name == 'idle9':   # suelda su espada (chispas)
        return wrap(n, B(2, 'io', two=0, wa=84, afA=80, afE=.8, abA=70, abE=.8, lean=12, hy=5, hd=10, ffx=5, bfx=-5),
                    B(4, 'io', two=0, wa=84, afA=88, afE=.85, abA=84, abE=.9, lean=16, hy=6, hd=14, ffx=5, bfx=-5),
                    *osc(5, 11, 1.4, lambda k: dict(two=0, wa=84, afA=88, afE=.85, abA=84 + (3 if k % 2 else -3), abE=.9, lean=16, hy=6, hd=14, ffx=5, bfx=-5)),
                    B(12.5, 'io', two=1, lean=4, hy=1, hd=2))
    return wrap(n, *[B(t, 'io', **p) for t, p in (                       # baile del robot
        (1.5, dict(afA=90, abA=-90, afE=.6, abE=.6, hd=-14, lean=0)), (2.5, dict(afA=90, abA=-90, afE=.6, abE=.6, hd=-14, lean=0)),
        (3.5, dict(afA=150, abA=0, afE=.6, abE=.6, hd=14, lean=0)), (5, dict(afA=150, abA=0, afE=.6, abE=.6, hd=14, lean=0)),
        (6, dict(afA=40, abA=-150, afE=.6, abE=.6, hd=-14, lean=0, hx=1)), (7.5, dict(afA=40, abA=-150, afE=.6, abE=.6, hd=-14, lean=0, hx=1)),
        (8.5, dict(afA=110, abA=110, afE=.6, abE=.6, hd=14, lean=0, hx=-1)), (10, dict(afA=110, abA=110, afE=.6, abE=.6, hd=14, lean=0, hx=-1)),
        (11.5, dict(afA=60, abA=20, hd=0)))])


# valores por defecto por (clase, anim): fuera de la pose base 'two=1' (steel/earth) o apartando el arma para que se vean las manos
DEFS = {}
for _n in ('idle5', 'idle6', 'idle7', 'idle8', 'idle9', 'idle10'):
    DEFS[('steel', _n)] = dict(two=0, wa=58)
    DEFS[('earth', _n)] = dict(two=0, wa=200)
for _n in ('idle5', 'idle7', 'idle8', 'idle9', 'idle10'):
    DEFS[('verdant', _n)] = dict(wa=200)
for _n in ('idle5', 'idle9'):
    DEFS[('frost', _n)] = dict(wa=210)


def _wrapdef(cid, fn):
    def g(C, name, n):
        ks = fn(C, name, n)
        d = DEFS.get((cid, name))
        if not d:
            return ks
        out = []
        for (t, kw, e) in ks:
            if kw and not kw.get('_base_only'):
                kw = dict(d, **kw)
            out.append((t, kw, e))
        return out
    return g


IDLES2 = dict(paladin=paladin, shadow=shadow, flame=flame, storm=storm, frost=frost, verdant=verdant, blood=blood, earth=earth,
              astral=astral, steel=steel)
IDLES2 = {k: _wrapdef(k, v) for k, v in IDLES2.items()}
