"""Guion del trailer de 40 s (ES / EN / sin textos). Todo es gameplay REAL de la version actual, grabado con capture_clips.sh
(la misma partida en espanol y en ingles gracias a BOT_SEED). Rejilla de cortes: 0,4 s (150 BPM de mus_boss_a, que entra en 4,8 s).
Cada inicio de plano es aproximado; clipmetrics.best() lo ajusta +-0,6 s para evitar destellos blancos y tintes de pantalla completa."""
import os
import numpy as np
from PIL import Image
import pixtext, clipmetrics

W, H = 1920, 1080
WHITE, RED, ORANGE, PINK, GOLD, CYAN = (255, 255, 255), (255, 70, 50), (255, 150, 40), (255, 120, 230), (255, 220, 120), (150, 220, 255)
HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, 'clips', 'es')        # metricas de referencia (las partidas ES y EN son identicas)

# (clip, inicio aproximado [s], duracion [s], extras). auto=False: inicio exacto (escenas de interfaz con el momento ya medido)
S = [
    # ---- 0-4.8 INTRODUCCION: salas reales sin enemigos, luz de antorchas y particulas; el logo aparece en 1,6-4,6
    ('i_s0', 5.4, 2.0, dict(auto=False, fade_in=0.9, zoom=(1.25, 1.25), focus=(.5, .5), pan=(-12, 12))),
    ('i_still', 5.4, 2.0, dict(auto=False, zoom=(1.25, 1.25), focus=(.5, .5), pan=(12, -12), dark=0.45)),
    ('i_s4', 6.0, 0.8, dict(auto=False, zoom=(1.25, 1.25), focus=(.55, .55), dark=0.45)),
    # ---- 4.8-12.0 EXPLORACION Y COMBATE: seis biomas, enemigos, trampas y plataformas
    ('c4', 4.3, 1.2, dict(flash=(WHITE, .7), shake=12, zoom=(1.25, 1.25), focus=(.4, .55))),
    ('c0', 5.3, 1.2, dict(zoom=(1.25, 1.25), focus=(.55, .5))),
    ('c1', 5.6, 1.2, dict(auto=False, flash=(ORANGE, .4), zoom=(1.25, 1.25), focus=(.55, .55))),
    ('c2', 6.4, 1.2, dict(zoom=(1.25, 1.25), focus=(.5, .45))),
    ('c5', 5.0, 1.2, dict(flash=(CYAN, .4), zoom=(1.25, 1.25), focus=(.45, .5))),
    ('c3', 5.5, 1.2, dict(zoom=(1.25, 1.25), focus=(.5, .45))),
    # ---- 12.0-20.0 ARMAS Y MEJORAS
    ('t_arsenal', 5.3, 0.8, dict(flash=(WHITE, .5), zoom=(1.25, 1.25), focus=(.5, .5))),
    ('t_arsenal', 9.2, 0.8, dict(zoom=(1.25, 1.25), focus=(.5, .5))),
    ('t_inv', 4.2, 1.2, dict(auto=False)),                       # inventario: ficha del arma secundaria equipada
    ('t_chest', 16.0, 1.2, dict(auto=False, flash=(GOLD, .4), zoom=(1.25, 1.25), focus=(.55, .55))),   # sala despejada: cofres con flecha
    ('t_chest', 19.7, 1.6, dict(auto=False)),                    # premio del cofre: se recorren las opciones
    ('t_bless', 3.2, 1.2, dict(auto=False)),                     # altar: ofertas de bendiciones reales
    ('t_bless', 6.5, 1.2, dict(auto=False)),                     # bendiciones activas y sinergias (listas reales del juego)
    # ---- 20.0-28.0 ACCION INTENSA: cortes rapidos
    ('e1', 6.9, 0.8, dict(auto=False, flash=(WHITE, .6), shake=14, zoom=(1.25, 1.25), focus=(.45, .55))),
    ('t_charge', 15.6, 0.8, dict(auto=False, zoom=(1.25, 1.25), focus=(.42, .55))),          # ataque cargado: carga y golpe
    ('t_parry', 12.4, 1.2, dict(zoom=(1.25, 1.25), focus=(.55, .65))),         # parry perfecto y contraataque
    ('c7', 5.4, 0.8, dict(auto=False, flash=(WHITE, .6), shake=16)),
    ('c1', 8.1, 0.8, dict(auto=False, flash=(ORANGE, .5), zoom=(1.25, 1.25), focus=(.5, .55))),
    ('c6', 8.4, 0.8, dict(auto=False, flash=(RED, .5), zoom=(1.25, 1.25), focus=(.45, .5))),
    ('c0', 12.3, 0.8, dict(flash=(PINK, .5), shake=12)),
    ('e5', 9.0, 0.8, dict(flash=(ORANGE, .5), shake=12, zoom=(1.25, 1.25), focus=(.45, .5))),
    ('c2', 8.3, 0.4, dict(flash=(WHITE, .5))),
    ('c4', 6.3, 0.4, dict(flash=(WHITE, .5))),
    ('c5', 6.3, 0.4, dict(flash=(WHITE, .5))),
    # ---- 28.0-35.2 JEFES
    ('b1', 7.2, 1.2, dict(flash=(ORANGE, .6), shake=16, zoom=(1.25, 1.25), focus=(.6, .55))),
    ('b2', 6.6, 1.2, dict(flash=(WHITE, .5), shake=12, zoom=(1.25, 1.25), focus=(.6, .5))),
    ('b6', 7.6, 1.2, dict(flash=(RED, .6), shake=12, zoom=(1.25, 1.25), focus=(.55, .5))),
    ('b3', 14.3, 1.2, dict(auto=False, flash=(PINK, .5), shake=12, zoom=(1.25, 1.25), focus=(.6, .45))),
    ('b8', 8.8, 1.2, dict(flash=(PINK, .6), shake=14, zoom=(1.25, 1.25), focus=(.6, .55))),
    ('b5', 12.4, 1.2, dict(flash=(CYAN, .6), shake=14, zoom=(1.25, 1.25), focus=(.6, .55))),
    # ---- 35.2-40 CIERRE: explosiones de la derrota real del Guardian del Eclipse en la partida grabada y tarjeta final con el logo
    ('b7', 14.2, 1.2, dict(auto=False, flash=(GOLD, .7), shake=20, zoom=(1.25, 1.25), focus=(.45, .6))),
    ('i_still', 6.0, 3.6, dict(auto=False, overlay='title')),
]

SHOTS = []
_t = 0.0
for c, ss, d, ex in S:
    sh = dict(clip=c, ss=ss, dur=d, t0=_t); sh.update(ex)
    if sh.get('auto', True):
        sh['ss'] = clipmetrics.best(os.path.join(REF, c + '.mp4'), ss, d, 1.5 if c[0] == 'b' else 0.6)
    SHOTS.append(sh); _t += d
assert abs(_t - 40.0) < 1e-6, _t

# Textos: cada idioma escrito por separado. "A|B" = linea principal + secundaria. y = centro del bloque; band = opacidad de la placa.
# Arriba (y~225) en gameplay; abajo (y~960) sobre las pantallas de interfaz, donde solo tapa la fila de botones inferior.
TEXTS = [
    dict(t0=5.2, t1=8.2, y=225, scale=6, ss=4, band=.5, es='EXPLORA LAS MAZMORRAS|9 biomas · salas nuevas en cada partida', en='EXPLORE THE DUNGEONS|9 biomes · new rooms every run'),
    dict(t0=8.6, t1=11.8, y=225, scale=6, band=.5, es='ESQUIVA, SALTA Y COMBATE', en='DODGE, LEAP AND FIGHT'),
    dict(t0=12.2, t1=14.7, y=975, scale=6, ss=4, band=.8, es='ENCUENTRA TU ARMA|36 armas secundarias', en='FIND YOUR WEAPON|36 secondary weapons'),
    dict(t0=15.0, t1=19.8, y=975, scale=6, ss=4, band=.85, es='CONSTRUYE TU ESTRATEGIA|200 bendiciones · 23 sinergias', en='BUILD YOUR STRATEGY|200 blessings · 23 synergies'),
    dict(t0=20.2, t1=23.4, y=225, scale=6, ss=4, band=.5, es='DOMINA EL COMBATE|Ataques cargados · parry · habilidades', en='MASTER THE FIGHT|Charged attacks · parries · skills'),
    dict(t0=24.0, t1=27.8, y=225, scale=6, ss=4, band=.5, es='10 ESPADACHINES|CADA UNO CON SU ESTILO', en='10 SWORDSMEN|10 WAYS TO FIGHT'),
    dict(t0=28.4, t1=32.0, y=225, scale=6, ss=4, band=.5, es='ENFRÉNTATE A LOS JEFES|9 jefes · cada uno con sus propios ataques', en='FACE THE BOSSES|9 bosses · each with its own attacks'),
    dict(t0=37.3, t1=40.0, y=800, scale=6, band=0, anim='rise', es='DESAFÍA EL ABISMO', en='DARE TO DESCEND'),
]

_logo = np.array(Image.open(pixtext.ROOT + '/Shared/assets/ui/ui_logo.png').convert('RGBA'))
_logo5 = np.array(Image.fromarray(_logo, 'RGBA').resize((_logo.shape[1] * 5, _logo.shape[0] * 5), Image.NEAREST))
_logo6 = np.array(Image.fromarray(_logo, 'RGBA').resize((_logo.shape[1] * 6, _logo.shape[0] * 6), Image.NEAREST))


def logo(fr, lt, cy, a_mul=1.0, big_t=0.08):
    """Logo oficial (ui_logo.png) a x5 por vecino mas cercano; entra a x6 durante unos fotogramas (siempre escala entera)."""
    a = min(lt / 0.12, 1.0) * a_mul
    img = _logo6 if lt < big_t else _logo5
    pixtext.blit(fr, img, W // 2, cy, a, 1.0, 0, 0)
    if lt < 0.12:
        f = 0.6 * (1 - lt / 0.12)
        fr[:] = (fr * (1 - f) + 255 * f).astype(np.uint8)


def intro_logo(fr, t):
    """1,6-4,6: el nombre del juego sobre la mazmorra (oscurecida por el plano) y se desvanece justo antes del primer golpe de musica."""
    lt = t - 1.6
    out = min(max((4.6 - t) / 0.35, 0.0), 1.0)
    logo(fr, lt, 500, out)
    return fr


def title_overlay(fr, lt, t, lang):
    """36,4-40: tarjeta final. Fondo de mazmorra oscurecido, logo oficial y lema."""
    k = min(lt / 0.3, 1.0)
    fr[:] = (fr * (1.0 - 0.55 * k)).astype(np.uint8)
    logo(fr, lt, 470)
    return fr


OVERLAYS = [(1.6, 4.6, intro_logo)]

for _s in SHOTS:
    if _s.get('overlay') == 'title':
        _s['overlay'] = title_overlay


def audio(mx, lang, clips):
    import mixer as M
    mx.add_music('mus_title', 0.0, 0.0, 5.4, vol=0.55, fade_in=0.6, fade_out=0.9)     # introduccion atmosferica
    mx.add_music('mus_boss_a', 0.0, 4.8, 35.2, vol=0.62, fade_in=0.02, fade_out=1.6)  # entra con el primer combate
    for sh in SHOTS:
        tsv = os.path.join(clips, sh['clip'] + '.mp4.audio.tsv')
        mx.add_scene_sfx(tsv, sh['ss'], sh['ss'] + sh['dur'], sh['t0'], vol=0.8, skip=('ui_click', 'ui_start_run'))
    mx.add(M.sfx('boss_title'), 1.6, 0.8)
    mx.add(M.sfx('explosion_big'), 4.8, 0.8)
    mx.add(M.sfx('level_up'), 12.0, 0.45)
    mx.add(M.sfx('explosion_big'), 28.0, 0.7)
    mx.add(M.sfx('boss_title'), 36.4, 0.9)
    mx.add(M.sfx('explosion_big'), 36.4, 0.9, pitch=0.8)
