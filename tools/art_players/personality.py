"""Poses de personalidad: 4 reposos propios por espadachin + cofre / asombro / contacto / victoria / cansancio.

Convenciones del rig: angulos 0 = abajo, 90 = adelante, 180 = arriba, 240 = atras-arriba (arma al hombro).
hd < 0 mira hacia arriba, hd > 0 mira hacia abajo. Cada secuencia empieza y termina en la pose base (carry) para que
la transicion con el reposo normal sea limpia.
"""
import math
import anims as AN


def K(t, e='io', **kw):
    return (t, kw, e)


def B(t, e='io', **kw):
    """Clave absoluta a partir de la pose base."""
    kw['_base'] = 1
    return (t, kw, e)


def wrap(n, *ks):
    return [(0, {}, 'io')] + list(ks) + [(n - 1, {'_base': 1}, 'io')]


def osc(t0, t1, step, fn):
    """Genera claves oscilantes: fn(k) -> dict, cada 'step' fotogramas."""
    out, k, t = [], 0, t0
    while t <= t1 + 1e-6:
        out.append(B(t, 'io', **fn(k)))
        k += 1
        t += step
    return out


# =============================================================== comunes: cofre, contacto, cansancio
def chest_keys(c, C, n, v):
    """Abrir un cofre: agacharse, abrir con la mano de atras, reaccion (v = variante propia del personaje)."""
    if v == 'look':        # mira a los lados antes de abrir (sigiloso / desconfiado)
        return wrap(n, B(1, 'io', hy=4, lean=14, hd=-14, two=0, wa=84, abA=-10, abE=.6),
                    B(2.5, 'io', hy=6, lean=16, hd=10, two=0, wa=84, abA=70, abE=.9, ffx=5, bfx=-5),
                    B(4.5, 'out', hy=6.5, lean=15, hd=8, two=0, wa=84, abA=125, abE=1.0, ffx=5, bfx=-5),
                    B(6, 'io', hy=1, lean=-5, hd=-8, two=0, wa=C['wa'], abA=100, abE=.8, ffx=4, bfx=-5))
    if v == 'bounce':      # impaciente / energico: golpecito y salto
        return wrap(n, B(1, 'io', hy=5, lean=12, hd=8, two=0, wa=84, abA=60, abE=.85, ffx=5, bfx=-4),
                    B(3, 'out', hy=6, lean=14, hd=10, two=0, wa=84, abA=135, abE=1.0, ffx=5, bfx=-4),
                    B(4.5, 'out', hy=-1.5, lean=-6, hd=-10, two=0, wa=C['wa'], abA=150, abE=.9, ffy=-3, bfy=-3),
                    B(6, 'io', hy=1, lean=-2, hd=-4, two=0, wa=C['wa'], abA=60, abE=.8))
    return wrap(n, B(1.5, 'io', hy=5, lean=12, hd=6, two=0, wa=84, abA=40, abE=.8, ffx=5, bfx=-4),    # 'kneel' pesado / ceremonioso
                B(3, 'io', hy=6.5, lean=15, hd=9, two=0, wa=84, abA=80, abE=.95, ffx=5, bfx=-4),
                B(4.8, 'out', hy=6, lean=13, hd=5, two=0, wa=84, abA=140, abE=1.0, ffx=5, bfx=-4),
                B(6, 'io', hy=2, lean=-3, hd=-7, two=0, wa=C['wa'], abA=110, abE=.9))


def touch_keys(c, C, n, v):
    """Activar un portal / santuario / puerta: gesto de mano adelante."""
    if v == 'palm':
        return wrap(n, B(1.5, 'io', lean=-2, hd=-3, afA=C['afA'], two=0, wa=88, abA=95, abE=.95, hy=1),
                    B(3, 'out', lean=2, hd=0, two=0, wa=88, abA=100, abE=1.0, hy=1.5, ffx=6, bfx=-4),
                    B(4.2, 'io', lean=0, two=0, wa=88, abA=88, abE=.95))
    return wrap(n, B(1.5, 'io', lean=-5, hy=1.5, hd=2, two=0, wa=88, afA=C['afA'], abA=40, abE=.7),
                B(3, 'out', lean=6, hy=2.5, hd=4, two=0, wa=88, abA=85, abE=1.0, ffx=6, bfx=-4),
                B(4.4, 'io', lean=3, hy=1, two=0, wa=88, abA=70, abE=.9))


def weary_keys(c, C, n, v):
    """Poca vida: encorvado, jadeando (bucle)."""
    lean, hy = (16, 3.0) if v != 'proud' else (9, 2.0)
    ks = []
    for i in range(6):
        ph = 2 * math.pi * i / 6
        ks.append((i, dict(hy=hy + 0.55 * math.sin(ph), lean=lean + 1.4 * math.sin(ph + .6), hd=7 + 1.2 * math.sin(ph),
                           two=0.0, afA=18 + 4 * math.sin(ph), afE=.65, abA=8 + 4 * math.sin(ph + 1), abE=.65,
                           wa=88, ffx=4.4, bfx=-4.6, ex=ph), 'io'))
    return ks


# =============================================================== por personaje
def paladin(C, name, n):
    if name == 'idle1':     # pule y examina su espada
        return wrap(n, B(2, 'io', wa=118, afA=78, afE=.82, lean=0, hd=5, abA=50, abE=.7, hy=.5),
                    B(4, 'io', wa=112, afA=74, afE=.8, lean=-1, hd=7, hy=.5, abA=60),
                    B(6, 'io', wa=122, afA=78, afE=.82, hd=7, hy=.5, abA=45),
                    B(8, 'io', wa=110, afA=72, afE=.8, hd=7, abA=60),
                    B(10, 'io', wa=124, afA=80, afE=.84, hd=4, abA=50),
                    B(12, 'out', wa=165, afA=110, afE=.9, lean=-4, hd=-4, hy=-.5, abA=70),     # destello: la alza
                    B(13.5, 'in', wa=60, afA=40, hd=2, lean=2, hy=1))
    if name == 'idle2':     # golpea el escudo dos veces, asiente satisfecho
        return wrap(n, B(2, 'io', lean=-2, hd=-2, abA=88, abE=.9, afA=30, hy=0),
                    B(3.2, 'in', abA=100, abE=.95, lean=2, hy=1.2),
                    B(4.2, 'out', abA=84, abE=.9, lean=-1, hy=0),
                    B(5.4, 'in', abA=100, abE=.95, lean=2, hy=1.2),
                    B(6.6, 'out', abA=84, abE=.9, lean=-1, hy=0),
                    B(9, 'io', abA=70, abE=.8, hd=6, hy=1.4, lean=4),
                    B(11, 'io', abA=64, abE=.78, hd=-3, hy=0, lean=2))
    if name == 'idle3':     # plegaria al alba: espada clavada, cabeza baja y luego alzada
        return wrap(n, B(3, 'io', two=1, wa=6, afA=52, afE=.62, abA=52, abE=.6, lean=4, hd=11, hy=2.5, ffx=4.5, bfx=-4.5),
                    B(7, 'io', two=1, wa=6, afA=52, afE=.62, abA=52, abE=.6, lean=4, hd=12, hy=2.8, ffx=4.5, bfx=-4.5),
                    B(10, 'out', two=1, wa=6, afA=52, afE=.62, abA=52, abE=.6, lean=-2, hd=-12, hy=1.2, ffx=4.5, bfx=-4.5),
                    B(13, 'io', two=1, wa=6, afA=52, afE=.62, abA=52, abE=.6, lean=-1, hd=-9, hy=1.4, ffx=4.5, bfx=-4.5))
    return wrap(n, B(2, 'io', lean=-3, hd=3, hy=0, abA=48, afA=26) ,       # impaciente: zapatea y suspira
                *osc(3, 9, 1.5, lambda k: dict(lean=-3, hd=3, hy=0, abA=48, afA=26, bfy=-1.2 - (3.4 if k % 2 == 0 else 0))),
                B(11, 'in', lean=7, hd=9, hy=2.8, abA=40, afA=22),
                B(13, 'out', lean=-2, hd=-5, hy=.4, abA=62))


def shadow(C, name, n):
    if name == 'idle1':     # lanza y recoge una daga
        return wrap(n, B(2, 'io', wa=60, wb=70, afA=70, afE=.8, lean=8, hy=1.5, hd=2),
                    B(4, 'out', wa=185, afA=165, afE=1.0, lean=-4, hy=-.5, hd=-14),                # lanza
                    B(6, 'io', wa=185, afA=165, afE=1.0, lean=-4, hy=0, hd=-12),
                    B(8.5, 'in', wa=90, afA=120, afE=.95, lean=4, hy=1, hd=3),                     # la atrapa
                    B(10, 'io', wa=70, afA=60, afE=.8, lean=9, hy=1.4, hd=4),
                    B(13, 'io', wa=95, afA=50, afE=.72, lean=12, hd=0))
    if name == 'idle2':     # se mira atras: algo en la oscuridad
        return wrap(n, B(2, 'io', lean=6, hd=-20, hy=2.5, afA=70, afE=.7, abA=60, ffx=5.5, bfx=-5.5),
                    B(4, 'io', lean=3, hd=-26, hy=3.5, afA=80, afE=.7, abA=70, wa=100, wb=100, ffx=6, bfx=-6),
                    B(8, 'io', lean=3, hd=-26, hy=3.5, afA=80, afE=.7, abA=70, wa=100, wb=100, ffx=6, bfx=-6),
                    B(10, 'io', lean=10, hd=8, hy=1.5, afA=55, abA=40),
                    B(12, 'io', lean=12, hd=-2, hy=1, afA=50, abA=30))
    if name == 'idle3':     # afila una daga contra la otra
        return wrap(n, B(2, 'io', afA=95, afE=.7, abA=95, abE=.7, wa=60, wb=130, lean=10, hd=8, hy=1.5),
                    *osc(3, 10, 1.4, lambda k: dict(afA=95, afE=.7, abA=95 + (8 if k % 2 else -8), abE=.72, wa=60, wb=130 + (22 if k % 2 else -10), lean=10, hd=8, hy=1.5)),
                    B(12, 'io', afA=70, abA=60, wa=75, wb=80, lean=11, hd=-6))
    return wrap(n, B(2, 'io', lean=8, hy=3, hd=4, afA=60, abA=45),        # impaciente: se mece sobre los talones, gira la daga
                B(4, 'io', lean=16, hy=4.5, hd=8, afA=70, abA=50, wa=130, ffx=6, bfx=-6),
                B(6, 'io', lean=6, hy=1.5, hd=-4, afA=70, wa=200),
                B(8, 'io', lean=16, hy=4.5, hd=8, wa=300, ffx=6, bfx=-6),
                B(10, 'io', lean=8, hy=2, hd=-2, wa=380, afA=60),
                B(13, 'io', lean=12, hy=0, hd=0, wa=455, afA=50))


def flame(C, name, n):
    if name == 'idle1':     # juega con una llama que flota sobre la palma
        return wrap(n, B(3, 'io', two=0, wa=200, abA=60, abE=.9, afA=20, lean=3, hd=4, hy=1),
                    B(5, 'io', two=0, wa=200, abA=88, abE=.88, afA=20, lean=0, hd=-6, hy=.5),
                    B(8, 'io', two=0, wa=200, abA=82, abE=.9, afA=20, lean=-1, hd=-9, hy=.5),
                    B(10, 'io', two=0, wa=200, abA=92, abE=.88, afA=20, lean=0, hd=-8),
                    B(12, 'out', two=0, wa=200, abA=125, abE=.95, afA=20, lean=-5, hd=-14, hy=-.5),   # la lanza al aire
                    B(14, 'io', two=0, wa=220, abA=70, afA=30, lean=3, hd=0))
    if name == 'idle2':     # admira su espada ardiente
        return wrap(n, B(3, 'io', two=1, wa=165, afA=75, afE=.8, abA=70, lean=-3, hd=-8, hy=.5),
                    B(6, 'io', two=1, wa=150, afA=70, afE=.8, abA=70, lean=-2, hd=-4, hy=1.2),
                    B(9, 'io', two=1, wa=170, afA=78, afE=.82, abA=70, lean=-4, hd=-9, hy=.4),
                    B(11, 'out', two=1, wa=140, afA=58, afE=.75, abA=60, lean=3, hd=5, hy=2.4),       # asiente
                    B(13, 'io', two=1, wa=200, afA=55, abA=50, lean=5))
    if name == 'idle3':     # sacude las manos calientes y sopla brasas
        return wrap(n, B(2, 'io', two=0, wa=205, afA=25, abA=40, abE=.7, lean=5, hd=4),
                    *osc(3, 8, 1, lambda k: dict(two=0, wa=205, afA=25, abA=40 + (50 if k % 2 else 0), abE=.8, lean=5, hd=4, hy=0.4)),
                    B(10, 'io', two=0, wa=205, afA=25, abA=105, abE=.55, lean=8, hd=2, hy=1.5),     # sopla la mano
                    B(12, 'out', two=0, wa=205, afA=25, abA=110, abE=.55, lean=10, hd=4, hy=2),
                    B(14, 'io', two=1, abA=60))
    return wrap(n, B(2, 'io', two=1, lean=-4, hd=2, hy=0),                 # impaciente: pisotea con brasas
                *osc(3, 10, 1.6, lambda k: dict(two=1, lean=-4 + (2 if k % 2 else 0), hd=2, hy=(1.5 if k % 2 else 0), bfy=-1.2 - (3.6 if k % 2 == 0 else 0))),
                B(12, 'in', two=1, lean=8, hd=7, hy=3),
                B(13.5, 'out', two=1, lean=-3, hd=-3, hy=.5))


def storm(C, name, n):
    if name == 'idle1':     # chispas entre los dedos
        return wrap(n, B(2, 'io', abA=40, abE=.7, afA=70, lean=9, hd=4),
                    B(4, 'io', abA=70, abE=.85, afA=70, lean=8, hd=6, hy=.8),
                    *osc(5, 11, 1, lambda k: dict(abA=70 + (6 if k % 2 else -6), abE=.85, afA=70, lean=8, hd=6, hy=.8)),
                    B(13, 'io', abA=20, abE=.7, lean=9, hd=0))
    if name == 'idle2':     # floritura de esgrima con el estoque
        return wrap(n, B(2, 'io', wa=40, afA=55, afE=.8, lean=12, hd=2, hy=1.5, ffx=5, bfx=-5),
                    B(4, 'out', wa=150, afA=140, afE=.95, lean=2, hd=-4, hy=.5, abA=-90, abE=.9),
                    B(5.5, 'in', wa=70, afA=95, afE=1.0, lean=-6 + 22, hd=4, hy=2.5, ffx=9, bfx=-4, abA=-100),   # estocada
                    B(7, 'io', wa=70, afA=95, afE=1.0, lean=18, hd=4, hy=2.5, ffx=9, bfx=-4),
                    B(9, 'out', wa=185, afA=165, afE=.95, lean=-2, hd=-8, hy=-.5, abA=-50),
                    B(11.5, 'io', wa=140, afA=100, afE=.9, lean=6, hy=1),
                    B(13, 'io', wa=88, afA=80, lean=9))
    if name == 'idle3':     # no puede estarse quieto: saltitos sobre las puntas
        return wrap(n, *[B(t, 'io', hy=(-1.8 if up else 1.5), lean=9 + (3 if up else -2), hd=(-3 if up else 3),
                            ffy=-1.2 - (2.6 if up else 0), bfy=-1.2 - (2.6 if up else 0), afA=78 + (12 if up else -6), abA=-60 + (-20 if up else 10))
                         for t, up in ((1, 0), (2.5, 1), (4, 0), (5.5, 1), (7, 0), (8.5, 1), (10, 0), (11.5, 1), (13, 0))])
    return wrap(n, B(1.5, 'io', hd=-12, lean=6, hy=.5),                  # mira rapido a ambos lados / "olio algo"
                B(3, 'out', hd=-18, lean=3, hy=1.5, afA=60, abA=-30),
                B(5.5, 'in', hd=14, lean=11, hy=1, afA=70),
                B(8, 'io', hd=-8, lean=7, hy=.5),
                B(10, 'in', hd=10, lean=10, hy=2.5, afA=58, abA=-70),
                B(12, 'io', hd=2, lean=9))


def frost(C, name, n):
    if name == 'idle1':     # forma un cristal de hielo sobre la palma
        return wrap(n, B(3, 'io', two=0, wa=35, abA=70, abE=.85, afA=25, lean=3, hd=4, hy=1),
                    B(5, 'io', two=0, wa=35, abA=95, abE=.9, afA=25, lean=2, hd=7, hy=1.2),
                    B(9, 'io', two=0, wa=35, abA=98, abE=.9, afA=25, lean=2, hd=8, hy=1.2),
                    B(11, 'out', two=0, wa=35, abA=118, abE=.95, afA=25, lean=-2, hd=-6, hy=.3),
                    B(13, 'io', two=0, wa=60, abA=40, afA=35, lean=4))
    if name == 'idle2':     # se frota las manos por el frio (tiritando)
        return wrap(n, B(2, 'io', two=0, wa=30, afA=85, afE=.6, abA=85, abE=.6, lean=8, hd=6, hy=2.2),
                    *osc(3, 11, 1, lambda k: dict(two=0, wa=30, afA=85 + (8 if k % 2 else -4), afE=.62, abA=85 + (-8 if k % 2 else 6), abE=.62, lean=8 + (1 if k % 2 else 0), hd=6, hy=2.2 + (.5 if k % 2 else 0))),
                    B(12.5, 'io', two=0, afA=60, abA=40, lean=6, hy=1))
    if name == 'idle3':     # sopla la escarcha del filo y la inspecciona
        return wrap(n, B(3, 'io', wa=108, afA=78, afE=.8, abA=40, lean=3, hd=6, hy=.8),
                    B(5, 'io', wa=112, afA=80, afE=.82, abA=40, lean=6, hd=8, hy=1.5),
                    B(7, 'out', wa=112, afA=80, afE=.82, abA=40, lean=8, hd=10, hy=2),        # sopla
                    B(10, 'io', wa=100, afA=74, afE=.8, abA=40, lean=1, hd=5, hy=.5),
                    B(12, 'io', wa=125, afA=84, afE=.82, abA=40, lean=0, hd=4))
    return wrap(n, B(2, 'io', lean=-3, hd=4, hy=0, abA=95, afA=30),     # impaciente: cruza el brazo, golpecitos de escarcha
                B(3, 'io', lean=-3, hd=4, afA=70, afE=.55, abA=88, abE=.6, wa=95, hy=.5),
                *osc(4, 11, 1.8, lambda k: dict(lean=-3, hd=4, afA=70, afE=.55, abA=88, abE=.6, wa=95, hy=.5, bfy=-1.2 - (3 if k % 2 == 0 else 0))),
                B(13, 'io', lean=3, hd=-2, afA=40, abA=-25, wa=70))


def verdant(C, name, n):
    if name == 'idle1':     # se agacha y hace brotar una flor
        return wrap(n, B(3, 'io', two=0, wa=84, abA=40, abE=.7, afA=30, lean=14, hd=10, hy=5.5, ffx=5, bfx=-4.5),
                    B(5, 'io', two=0, wa=84, abA=70, abE=.85, afA=30, lean=17, hd=12, hy=6.5, ffx=5, bfx=-4.5),
                    B(10, 'io', two=0, wa=84, abA=72, abE=.85, afA=30, lean=17, hd=12, hy=6.5, ffx=5, bfx=-4.5),
                    B(12, 'out', two=0, wa=84, abA=40, abE=.7, afA=30, lean=6, hd=-2, hy=2, ffx=4.5, bfx=-4.5),
                    B(14, 'io', two=0, wa=60, abA=-22))
    if name == 'idle2':     # mira su espada viva: le brotan hojas
        return wrap(n, B(3, 'io', wa=105, afA=78, afE=.8, lean=2, hd=7, hy=.6, abA=-10),
                    B(8, 'io', wa=100, afA=75, afE=.8, lean=1, hd=8, hy=.8, abA=-10),
                    B(10, 'out', wa=115, afA=82, afE=.82, lean=-2, hd=-3, hy=0, abA=-30),
                    B(13, 'io', wa=80, afA=50, lean=4, hd=0))
    if name == 'idle3':     # se estira como un arbol al sol
        return wrap(n, B(3, 'io', two=0, wa=60, afA=160, afE=.95, abA=-160, abE=.95, lean=-8, hd=-12, hy=-.5, ffx=3.5, bfx=-3.5),
                    B(6, 'io', two=0, wa=60, afA=178, afE=1, abA=-178, abE=1, lean=-12, hd=-16, hy=-1.2, ffy=-2.4, ffx=3.2, bfx=-3.2),
                    B(9, 'io', two=0, wa=60, afA=176, afE=1, abA=-176, abE=1, lean=-12, hd=-14, hy=-1.2, ffy=-2.4, ffx=3.2, bfx=-3.2),
                    B(11, 'in', two=0, wa=60, afA=50, abA=-30, lean=8, hd=4, hy=2.5),
                    B(13, 'io', two=0, wa=60, afA=40, lean=5))
    return wrap(n, B(2, 'io', lean=1, hd=-14, hy=0, abA=-100, abE=.45, afA=30),      # escucha el bosque: mano en la oreja
                B(3.5, 'io', lean=-1, hd=-12, hy=.2, abA=140, abE=.6, afA=30),
                B(6, 'io', lean=-1, hd=-16, hy=.2, abA=145, abE=.6, afA=30),
                B(9, 'io', lean=0, hd=-8, hy=.6, abA=140, abE=.6, afA=30),
                B(11, 'io', lean=3, hd=3, abA=40, afA=35))


def blood(C, name, n):
    if name == 'idle1':     # hace girar la guadana como un bastón
        return wrap(n, B(2, 'io', two=0, wa=250, afA=50, afE=.7, abA=20, lean=3, hy=1),
                    B(4, 'io', two=0, wa=330, afA=70, afE=.7, abA=20, lean=1),
                    B(6, 'io', two=0, wa=430, afA=70, afE=.7, abA=20, lean=-1),
                    B(8, 'io', two=0, wa=520, afA=70, afE=.7, abA=20, lean=-1),
                    B(10, 'out', two=0, wa=610, afA=60, afE=.7, abA=20, lean=3),
                    B(12, 'in', two=1, wa=598, afA=40, afE=.75, abA=30, lean=5, hy=1.5),
                    B(13.5, 'io', two=1, wa=596))
    if name == 'idle2':     # prueba la sangre del filo: gota
        return wrap(n, B(3, 'io', two=0, wa=130, afA=100, afE=.8, abA=95, abE=.55, lean=3, hd=8, hy=1.2),
                    B(6, 'io', two=0, wa=135, afA=100, afE=.8, abA=125, abE=.6, lean=3, hd=6, hy=1),
                    B(8, 'io', two=0, wa=135, afA=100, afE=.8, abA=125, abE=.6, lean=1, hd=0, hy=.6),
                    B(11, 'out', two=1, wa=236, afA=40, abA=30, lean=-3, hd=-6, hy=0),
                    B(13, 'io', two=1, afA=40))
    if name == 'idle3':     # risita siniestra: hombros que tiemblan, cabeza ladeada
        return wrap(n, B(2, 'io', lean=-2, hd=-6, hy=.5),
                    *osc(3, 11, 1, lambda k: dict(lean=-2 + (1.2 if k % 2 else -.4), hd=-9, hy=(1.3 if k % 2 else .3), afA=40 + (6 if k % 2 else 0))),
                    B(12.5, 'io', lean=3, hd=2, hy=0))
    return wrap(n, B(2, 'io', two=1, wa=170, afA=45, abA=45, lean=-6, hd=2, hy=1),       # impaciente: se apoya en la guadaña y golpetea
                *osc(3, 10, 1.75, lambda k: dict(two=1, wa=170 + (-8 if k % 2 else 0), afA=45, abA=45, lean=-6, hd=2, hy=1 + (.6 if k % 2 else 0))),
                B(12, 'io', two=1, wa=200, lean=-2, hd=-4),
                B(13.5, 'io', two=1))


def earth(C, name, n):
    if name == 'idle1':     # bosteza y apoya el martillo en el hombro
        return wrap(n, B(3, 'io', two=1, wa=235, lean=-4, hd=-14, hy=-.4, afA=58, abA=48),
                    B(5, 'io', two=1, wa=235, lean=-10, hd=-24, hy=-.8, afA=62, abA=52),    # bostezo
                    B(8, 'io', two=1, wa=235, lean=-10, hd=-24, hy=-.8, afA=62, abA=52),
                    B(10, 'in', two=1, wa=232, lean=5, hd=6, hy=2.2),
                    B(12, 'io', two=1, wa=232, lean=7))
    if name == 'idle2':     # exhibe los musculos
        return wrap(n, B(2, 'io', two=0, wa=200, afA=150, afE=.5, abA=-150, abE=.5, lean=-3, hy=1.5, ffx=5, bfx=-5),
                    B(4, 'out', two=0, wa=200, afA=140, afE=.45, abA=-140, abE=.45, lean=-6, hy=2.4, hd=-3, ffx=5.5, bfx=-5.5),
                    B(6, 'io', two=0, wa=200, afA=150, afE=.5, abA=-150, abE=.5, lean=-3, hy=1.5, ffx=5, bfx=-5),
                    B(8, 'out', two=0, wa=200, afA=140, afE=.45, abA=-140, abE=.45, lean=-6, hy=2.4, hd=-3, ffx=5.5, bfx=-5.5),
                    B(11, 'io', two=1, afA=58, abA=48, lean=8, hy=0))
    if name == 'idle3':     # golpea el suelo con el mango: cae un guijarro
        return wrap(n, B(3, 'io', two=1, wa=190, afA=100, abA=95, afE=.8, abE=.75, lean=-6, hy=-.3),
                    B(5, 'in', two=1, wa=20, afA=70, abA=64, afE=.9, abE=.8, lean=8, hy=3),
                    B(7, 'out', two=1, wa=40, afA=64, abA=60, lean=4, hy=1.2),
                    B(10, 'io', two=1, wa=232, lean=2))
    return wrap(n, B(2, 'io', two=1, lean=-6, hd=3, hy=1),                 # impaciente: pisotón (polvo + piedrecillas)
                B(4, 'out', two=1, lean=-8, hd=0, hy=-.4, ffy=-5.5, ffx=5),
                B(5.2, 'in', two=1, lean=5, hd=6, hy=3, ffy=-1.2, ffx=5),
                B(8, 'io', two=1, lean=-6, hd=3, hy=1),
                B(10, 'out', two=1, lean=-8, hd=0, hy=-.4, bfy=-5.5, bfx=-5),
                B(11.2, 'in', two=1, lean=5, hd=6, hy=3),
                B(13, 'io', two=1, lean=2))


def astral(C, name, n):
    if name == 'idle1':     # mira las estrellas, señalando
        return wrap(n, B(3, 'io', lean=-6, hd=-18, hy=0, afA=30, abA=-40, abE=.7),
                    B(5, 'io', lean=-8, hd=-24, hy=-.4, abA=150, abE=.95, afA=30),
                    B(9, 'io', lean=-8, hd=-24, hy=-.4, abA=156, abE=.95, afA=30),
                    B(11, 'io', lean=-4, hd=-14, abA=100, afA=34),
                    B(13, 'io', lean=2, hd=-2, abA=-30))
    if name == 'idle2':     # dibuja una constelacion con el dedo
        return wrap(n, B(2, 'io', lean=-2, hd=-10, abA=100, abE=.9, afA=34),
                    B(4, 'io', lean=-2, hd=-10, abA=125, abE=.95),
                    B(6, 'io', lean=-2, hd=-10, abA=95, abE=.95),
                    B(8, 'io', lean=-2, hd=-10, abA=140, abE=.95),
                    B(10, 'io', lean=-2, hd=-12, abA=110, abE=.95),
                    B(12, 'out', lean=2, hd=-4, abA=145, abE=1.0),
                    B(14, 'io', lean=3, abA=-30))
    if name == 'idle3':     # levita un poco con la capa flotando
        return wrap(n, B(3, 'io', hy=-2.5, lean=2, ffy=-4.5, bfy=-6.2, ffx=2.5, bfx=-3, afA=48, abA=-48, afE=.78, hd=-3),
                    B(6, 'io', hy=-4.5, lean=1, ffy=-6.5, bfy=-8, ffx=2.5, bfx=-3, afA=58, abA=-58, hd=-5),
                    B(9, 'io', hy=-4, lean=2, ffy=-6, bfy=-7.6, afA=56, abA=-56, hd=-4),
                    B(12, 'io', hy=-.5, lean=3, ffy=-1.6, bfy=-1.6, afA=40, abA=-35))
    return wrap(n, B(2, 'io', lean=-6, hd=-6, hy=-.4, afA=150, afE=.8, abA=-150, abE=.8),     # bosteza y se estira
                B(5, 'io', lean=-12, hd=-18, hy=-1, afA=172, afE=1, abA=-172, abE=1, ffx=3.5, bfx=-3.5),
                B(8, 'io', lean=-12, hd=-18, hy=-1, afA=172, afE=1, abA=-172, abE=1, ffx=3.5, bfx=-3.5),
                B(10, 'in', lean=6, hd=5, hy=2, afA=40, abA=-30),
                B(12, 'io', lean=4))


def steel(C, name, n):
    if name == 'idle1':     # ajusta las hombreras y comprueba la armadura
        return wrap(n, B(2, 'io', two=0, wa=50, afA=130, afE=.7, abA=40, lean=4, hd=6, hy=.5),
                    *osc(3, 8, 1.2, lambda k: dict(two=0, wa=50, afA=130 + (10 if k % 2 else -4), afE=.62, abA=40, lean=4, hd=6, hy=.5 + (.4 if k % 2 else 0))),
                    B(10, 'io', two=0, wa=50, afA=45, abA=140, abE=.6, lean=4, hd=6),
                    B(12, 'io', two=0, wa=50, afA=45, abA=140, abE=.6, lean=3, hd=6, hy=1),
                    B(13.5, 'io', two=1))
    if name == 'idle2':     # pose de mando: brazos cruzados, barbilla en alto
        return wrap(n, B(3, 'io', two=0, wa=105, afA=85, afE=.5, abA=80, abE=.5, lean=-3, hd=-6, hy=.4),
                    B(5, 'io', two=0, wa=105, afA=88, afE=.45, abA=82, abE=.48, lean=-5, hd=-9, hy=.5),
                    B(10, 'io', two=0, wa=105, afA=88, afE=.45, abA=82, abE=.48, lean=-5, hd=-9, hy=.5),
                    B(12, 'io', two=1, wa=58))
    if name == 'idle3':     # saluda con la espada: un solo gesto elegante
        return wrap(n, B(3, 'io', two=0, wa=155, afA=128, afE=.9, abA=-30, lean=-3, hd=-6, hy=.4),
                    B(5, 'out', two=0, wa=178, afA=150, afE=1, abA=-30, lean=-5, hd=-8, hy=0),
                    B(7, 'in', two=0, wa=70, afA=60, afE=.9, abA=-30, lean=6, hd=7, hy=2),
                    B(11, 'io', two=0, wa=70, afA=60, afE=.9, lean=6, hd=7, hy=2),
                    B(13, 'io', two=1))
    return wrap(n, B(2, 'io', two=0, wa=58, afA=70, afE=.5, abA=75, abE=.5, lean=-2, hd=2, hy=0),   # impaciente: brazos cruzados + zapateo
                *osc(3, 10, 1.6, lambda k: dict(two=0, wa=58, afA=70, afE=.5, abA=75, abE=.5, lean=-2, hd=2, hy=0, ffy=-1.2 - (3 if k % 2 == 0 else 0))),
                B(12, 'in', two=0, lean=4, hd=7, hy=1.5),
                B(13.5, 'io', two=1))


# ------------------------------------------------------------------ asombro y victoria (propios de cada personaje)
AWE = {
    # sorpresa al descubrir una reliquia / secreto
    'paladin': lambda C, n: wrap(n, B(1.5, 'out', wa=170, afA=150, afE=1, lean=-8, hd=-14, hy=-1, abA=110, ffy=-1.2),
                                  B(4, 'io', wa=176, afA=160, afE=1, lean=-8, hd=-16, hy=-.5, abA=120),
                                  B(8, 'io', wa=170, afA=152, afE=1, lean=-6, hd=-12, hy=0, abA=100)),
    'shadow': lambda C, n: wrap(n, B(1, 'out', lean=-10, hd=-12, hy=-3, ffy=-5, bfy=-5, afA=90, abA=90, wa=120, wb=120),   # sobresalto: salta atras
                                B(3, 'io', lean=-6, hd=-8, hy=0, afA=70, abA=60, ffx=2, bfx=-8),
                                B(6, 'io', lean=4, hd=4, hy=2.5, afA=65, abA=60, ffx=6, bfx=-5),
                                B(8, 'io', lean=10, hd=2, hy=1.5, afA=55)),
    'flame': lambda C, n: wrap(n, B(1.5, 'out', two=0, wa=200, afA=160, afE=1, abA=-150, abE=1, lean=-10, hd=-14, hy=-1.4, ffy=-3, bfy=-3),
                               B(4, 'io', two=0, wa=200, afA=150, afE=1, abA=-150, abE=1, lean=-8, hd=-12, hy=-.4),
                               B(8, 'io', two=1, afA=70, abA=60, lean=2)),
    'storm': lambda C, n: wrap(n, B(1, 'out', hy=-3.6, lean=-6, hd=-12, ffy=-6, bfy=-6, afA=150, afE=.9, abA=-150, abE=.9, wa=160),
                               B(3, 'io', hy=1, lean=4, hd=-4, afA=100, abA=-80, wa=120),
                               B(5, 'out', hy=-2.5, lean=-4, hd=-8, ffy=-4, bfy=-4, afA=140, abA=-140, wa=150),
                               B(8, 'io', hy=0, lean=6)),
    'frost': lambda C, n: wrap(n, B(1.5, 'out', two=0, wa=60, afA=80, afE=.6, abA=95, abE=.6, lean=-6, hd=-10, hy=-.4),   # manos al pecho, boquiabierto
                               B(4, 'io', two=0, wa=60, afA=82, afE=.5, abA=92, abE=.5, lean=-4, hd=-8, hy=.4),
                               B(8, 'io', two=0, wa=70, afA=50, abA=40)),
    'verdant': lambda C, n: wrap(n, B(2, 'out', two=0, afA=165, afE=1, abA=-165, abE=1, lean=-8, hd=-14, hy=-.8, ffx=3.5, bfx=-3.5),
                                 B(4, 'io', two=0, afA=150, afE=.95, abA=-150, abE=.95, lean=-6, hd=-10, hy=.2),
                                 B(8, 'io', two=0, afA=60, abA=-30)),
    'blood': lambda C, n: wrap(n, B(1.5, 'out', two=0, wa=200, afA=110, afE=.9, abA=120, abE=.9, lean=4, hd=6, hy=2.5, ffx=6, bfx=-5),   # se relame, se inclina a mirar
                               B(4, 'io', two=0, wa=200, afA=100, afE=.9, abA=120, abE=.9, lean=10, hd=8, hy=3.5, ffx=6.5, bfx=-5),
                               B(8, 'io', two=1, lean=6)),
    'earth': lambda C, n: wrap(n, B(2, 'out', two=0, wa=200, afA=170, afE=1, abA=-170, abE=1, lean=-8, hd=-10, hy=-.6),
                               B(4, 'in', two=1, wa=90, afA=70, abA=60, lean=8, hy=3),
                               B(6, 'out', two=0, wa=200, afA=170, afE=1, abA=-170, abE=1, lean=-8, hd=-10, hy=-.6),
                               B(9, 'io', two=1)),
    'astral': lambda C, n: wrap(n, B(2, 'out', hy=-3.5, lean=-4, hd=-18, ffy=-4.5, bfy=-6, afA=130, afE=.9, abA=-130, abE=.9),
                                B(5, 'io', hy=-4, lean=-3, hd=-14, ffy=-5, bfy=-6.5, afA=140, abA=-140),
                                B(8, 'io', hy=-1.4, lean=2)),
    'steel': lambda C, n: wrap(n, B(1.5, 'out', two=0, wa=100, afA=100, afE=.7, abA=95, abE=.6, lean=-7, hd=-9, hy=.4),       # se inclina atras y levanta una ceja
                               B(4, 'io', two=0, wa=100, afA=104, afE=.7, abA=95, lean=-8, hd=-10, hy=.6),
                               B(8, 'io', two=1)),
}

VICT = {
    'paladin': lambda C, n: wrap(n, B(2, 'io', two=0, wa=140, afA=120, afE=.9, abA=100, lean=-2, hy=.6),
                                 B(4.5, 'out', two=0, wa=176, afA=170, afE=1, abA=150, abE=1, lean=-8, hd=-14, hy=-.8, ffx=4.2, bfx=-4.2),
                                 B(9, 'io', two=0, wa=176, afA=170, afE=1, abA=146, abE=1, lean=-8, hd=-14, hy=-.6),
                                 B(12, 'io', two=0, wa=170, afA=160, afE=1, abA=140, lean=-6, hd=-12)),
    'shadow': lambda C, n: wrap(n, B(2, 'io', wa=90, wb=60, afA=100, abA=110, lean=14, hy=2, hd=4),
                                B(3.5, 'io', wa=200, wb=170, afA=140, abA=120, lean=6, hy=1, hd=-4),
                                B(5, 'io', wa=350, wb=-100, afA=100, abA=70, lean=18, hy=3.5, hd=8),
                                B(7, 'out', wa=540, wb=200, afA=60, abA=45, lean=18, hy=4.5, hd=10, ffx=6, bfx=-6),     # giro + postura
                                B(12, 'io', wa=540, wb=200, afA=60, abA=45, lean=18, hy=4.5, hd=10, ffx=6, bfx=-6)),
    'flame': lambda C, n: wrap(n, B(2, 'in', two=1, wa=170, afA=100, abA=90, lean=10, hy=3.5, hd=6),
                               B(4, 'out', two=0, wa=185, afA=175, afE=1, abA=-170, abE=1, lean=-14, hd=-22, hy=-1.5, ffy=-1.2, ffx=4.5, bfx=-4.5),    # rugido
                               B(9, 'io', two=0, wa=185, afA=175, afE=1, abA=-170, abE=1, lean=-14, hd=-22, hy=-1.5, ffx=4.5, bfx=-4.5),
                               B(11, 'io', two=1, wa=190, afA=120, abA=110, lean=-4, hd=-8)),
    'storm': lambda C, n: wrap(n, B(2, 'io', wa=170, afA=150, afE=.95, abA=-90, lean=-2, hd=-10, hy=.4),
                               B(4, 'out', wa=182, afA=172, afE=1, abA=-150, abE=1, lean=-8, hd=-16, hy=-1.4, ffy=-3, bfy=-3),     # el rayo cae en el estoque
                               B(6, 'io', wa=182, afA=172, afE=1, abA=-150, abE=1, lean=-8, hd=-16, hy=-.8),
                               B(8, 'in', wa=60, afA=90, afE=1, abA=-100, lean=16, hy=2.5, hd=6, ffx=8.5, bfx=-4),
                               B(11, 'io', wa=60, afA=90, afE=1, lean=16, hy=2.5, ffx=8.5, bfx=-4)),
    'frost': lambda C, n: wrap(n, B(2.5, 'io', two=1, wa=170, afA=120, abA=110, lean=-4, hy=.4),
                               B(5, 'in', two=1, wa=10, afA=55, afE=.65, abA=55, abE=.62, lean=8, hy=3.5, hd=8, ffx=5, bfx=-5),   # clava el sable
                               B(8, 'io', two=1, wa=10, afA=55, afE=.65, abA=55, abE=.62, lean=2, hy=1.6, hd=-8, ffx=5, bfx=-5),
                               B(11, 'io', two=1, wa=10, afA=55, afE=.65, abA=55, abE=.62, lean=1, hy=1.4, hd=-10, ffx=5, bfx=-5)),
    'verdant': lambda C, n: wrap(n, B(3, 'io', two=0, afA=100, afE=.8, abA=-100, abE=.8, lean=-2, hd=-4, hy=1),
                                 B(6, 'out', two=0, afA=130, afE=1, abA=-130, abE=1, lean=-8, hd=-12, hy=-.5, ffx=3.8, bfx=-3.8),
                                 B(10, 'io', two=0, afA=135, afE=1, abA=-135, abE=1, lean=-7, hd=-10, hy=-.4)),
    'blood': lambda C, n: wrap(n, B(2, 'io', two=0, wa=300, afA=70, abA=20, lean=0),
                               B(4, 'io', two=0, wa=450, afA=80, abA=20, lean=-2),
                               B(6, 'out', two=0, wa=600, afA=60, abA=20, lean=4, hy=1.5),
                               B(8, 'in', two=1, wa=598, afA=40, abA=30, lean=12, hy=3, hd=8),
                               B(11, 'io', two=1, wa=250, afA=70, abA=60, lean=6, hy=1.2, hd=-6)),
    'earth': lambda C, n: wrap(n, B(2, 'in', two=1, wa=190, afA=120, abA=110, lean=-8, hy=-.4),
                               B(3.5, 'in', two=1, wa=40, afA=70, abA=64, lean=10, hy=4),                   # martillazo al suelo
                               B(5, 'io', two=0, wa=200, afA=60, afE=.5, abA=-60, abE=.5, lean=-4, hy=1.5),
                               B(7, 'out', two=0, wa=200, afA=80, afE=.45, abA=-80, abE=.45, lean=-8, hd=-12, hy=2),  # se golpea el pecho
                               B(8.5, 'io', two=0, wa=200, afA=60, afE=.5, abA=-60, abE=.5, lean=-4, hy=1.5),
                               B(10, 'out', two=0, wa=200, afA=80, afE=.45, abA=-80, abE=.45, lean=-8, hd=-12, hy=2),
                               B(12, 'io', two=1, wa=235, lean=-3)),
    'astral': lambda C, n: wrap(n, B(3, 'io', hy=-3, ffy=-4.5, bfy=-5.5, afA=120, afE=.9, abA=-120, abE=.9, lean=-4, hd=-10),
                                B(6, 'out', hy=-5.5, ffy=-7, bfy=-8.5, afA=170, afE=1, abA=-170, abE=1, lean=-8, hd=-20),
                                B(10, 'io', hy=-5, ffy=-6.5, bfy=-8, afA=168, abA=-168, lean=-7, hd=-18),
                                B(12, 'io', hy=-2.5, ffy=-3, bfy=-4, afA=120, abA=-120)),
    'steel': lambda C, n: wrap(n, B(2.5, 'io', two=0, wa=100, afA=120, afE=.8, abA=100, lean=-3, hd=-6, hy=.4),
                               B(5, 'out', two=0, wa=176, afA=172, afE=1, abA=60, abE=.6, lean=-9, hd=-14, hy=-.6),     # espada al cielo, brazo en la cadera
                               B(9, 'io', two=0, wa=176, afA=172, afE=1, abA=60, abE=.6, lean=-9, hd=-14, hy=-.6),
                               B(11.5, 'io', two=0, wa=140, afA=130, lean=-4)),
}

CHEST_V = dict(paladin='kneel', shadow='look', flame='bounce', storm='bounce', frost='kneel', verdant='kneel', blood='look',
               earth='kneel', astral='bounce', steel='look')
TOUCH_V = dict(paladin='palm', shadow='fist', flame='fist', storm='palm', frost='palm', verdant='palm', blood='fist',
               earth='fist', astral='palm', steel='fist')
WEARY_V = dict(paladin='proud', steel='proud', earth='proud')

IDLES = dict(paladin=paladin, shadow=shadow, flame=flame, storm=storm, frost=frost, verdant=verdant, blood=blood, earth=earth,
             astral=astral, steel=steel)


def keys(cls, name):
    cid = cls.id
    C = cls.carry
    n = AN.N[name]
    if name.startswith('idle'):
        if int(name[4:]) >= 5:
            import personality2
            return personality2.IDLES2[cid](C, name, n)
        return IDLES[cid](C, name, n)
    if name == 'chest':
        return chest_keys(cls, C, n, CHEST_V[cid])
    if name == 'touch':
        return touch_keys(cls, C, n, TOUCH_V[cid])
    if name == 'weary':
        return weary_keys(cls, C, n, WEARY_V.get(cid, ''))
    if name == 'awe':
        return AWE[cid](C, n)
    if name == 'victory':
        return VICT[cid](C, n)
    raise KeyError(name)
