"""Guion del trailer de 30 s (ES/EN). Todos los planos son gameplay REAL del juego (capture_clips.sh). Rejilla de cortes = 0.4 s (150 BPM de mus_boss_a)."""
import numpy as np
from PIL import Image
import pixtext

W, H = 1920, 1080
MUSIC = 'mus_boss_a'
WHITE, RED, ORANGE, PINK = (255, 255, 255), (255, 70, 50), (255, 150, 40), (255, 120, 230)

# (clip, inicio en el clip [s], duracion [s], extras)
S = [
    # ---- GANCHO 0-2.4
    ('b3_shadow', 2.9, 0.8, dict(flash=(WHITE, .9), shake=22, zoom=(1.0, 1.16), focus=(.73, .37))),
    ('b1_flame', 8.3, 0.8, dict(flash=(ORANGE, .8), shake=16, zoom=(1.0, 1.12), focus=(.6, .6))),
    ('b8_astral', 10.0, 0.8, dict(flash=(PINK, .8), shake=16, zoom=(1.0, 1.1))),
    # ---- PRESENTACION 2.4-8.0
    ('b0_paladin', 3.0, 2.4, dict(flash=(WHITE, .5), shake=10, zoom=(1.0, 1.22), focus=(.55, .72))),
    ('b2_frost', 5.0, 1.6, dict(zoom=(1.12, 1.2), focus=(.6, .6))),
    ('c1_flame', 5.0, 1.6, dict(flash=(ORANGE, .5), zoom=(1.1, 1.2), focus=(.5, .75))),
    # ---- ENEMIGOS Y JEFES 8.0-15.2
    ('c3_astral', 5.0, 1.2, dict(zoom=(1.1, 1.25), focus=(.5, .75))),
    ('c4_verdant', 6.0, 1.2, dict(zoom=(1.1, 1.25), focus=(.5, .75))),
    ('b4_verdant', 2.9, 1.2, dict(flash=(WHITE, .6), shake=14, zoom=(1.0, 1.15), focus=(.8, .45))),
    ('b5_storm', 2.9, 1.2, dict(flash=(WHITE, .6), shake=14, zoom=(1.0, 1.15), focus=(.8, .45))),
    ('b6_blood', 2.9, 1.2, dict(flash=(RED, .6), shake=14, zoom=(1.0, 1.15), focus=(.8, .45))),
    ('b7_earth', 2.9, 1.2, dict(flash=(ORANGE, .6), shake=14, zoom=(1.0, 1.15), focus=(.8, .45))),
    # ---- CLASES 15.2-18.4
    ('b1_flame', 0.1, 0.8, dict(flash=(WHITE, .35))),
    ('b3_shadow', 0.1, 0.8, dict(flash=(WHITE, .35))),
    ('b5_storm', 0.1, 0.8, dict(flash=(WHITE, .35))),
    ('b7_earth', 0.1, 0.8, dict(flash=(WHITE, .35))),
    # ---- PROGRESION 18.4-22.4
    ('s_bless', 4.1, 1.2, dict(flash=(WHITE, .4))),
    ('s_shop', 4.2, 0.8, dict()),
    ('s_forge', 4.3, 0.8, dict()),
    ('s_ev4', 4.7, 1.2, dict()),
    # ---- CLIMAX 22.4-27.2
    ('b7_earth', 10.0, 0.8, dict(flash=(ORANGE, .6), shake=18, zoom=(1.0, 1.15))),
    ('b6_blood', 8.4, 0.8, dict(flash=(RED, .6), shake=14, zoom=(1.0, 1.15))),
    ('b2_frost', 7.2, 0.8, dict(flash=(WHITE, .6), shake=14, zoom=(1.0, 1.12))),
    ('b5_storm', 12.4, 0.8, dict(flash=(WHITE, .7), shake=16, zoom=(1.0, 1.12))),
    ('b1_flame', 9.4, 0.8, dict(flash=(ORANGE, .7), shake=16, zoom=(1.0, 1.15))),
    ('b8_astral', 11.2, 0.8, dict(flash=(PINK, .8), shake=22, zoom=(1.0, 1.18))),
    # ---- TITULO 27.2-30
    ('b8_astral', 11.4, 2.8, dict(overlay='title')),
]

SHOTS = []
_t = 0.0
for c, ss, d, ex in S:
    sh = dict(clip=c, ss=ss, dur=d, t0=_t); sh.update(ex)
    SHOTS.append(sh); _t += d
assert abs(_t - 30.0) < 1e-6, _t

# Textos: cada idioma esta ESCRITO por separado (no es traduccion literal). "A|B" = linea principal + linea secundaria mas pequena.
# y = centro del bloque. Arriba (y~235) no tapa ni a los jefes ni al aviso inferior del juego (nombre del jefe y subtitulo); en las
# pantallas de interfaz (clases, bendiciones, forja) el texto va abajo sobre una placa oscura. band = opacidad de la placa.
TEXTS = [
    dict(t0=0.4, t1=2.4, y=235, scale=6, band=.5, es='CADA DESCENSO ES DISTINTO', en='NO TWO DESCENTS ALIKE'),
    dict(t0=2.8, t1=5.4, y=235, scale=6, band=.5, es='EMPUÑA LA ESPADA.|DOMINA LA MAGIA.', en='WIELD THE SWORD.|MASTER THE MAGIC.', ss=5),
    dict(t0=5.6, t1=8.0, y=235, scale=4, band=.5, anim='rise', es='ROGUELIKE DE ACCIÓN EN PIXEL ART', en='PIXEL-ART ACTION ROGUELIKE'),
    dict(t0=8.2, t1=11.4, y=235, scale=7, band=.5, es='ATRAVIESA 9 BIOMAS', en='CROSS 9 BIOMES'),
    dict(t0=11.6, t1=15.0, y=235, scale=7, band=.5, es='ENFRÉNTATE A 9 JEFES', en='FACE 9 BOSSES'),
    dict(t0=15.2, t1=18.4, y=905, scale=8, band=.85, es='10 ESPADACHINES|CADA UNO CON SU ESTILO', en='10 SWORDSMEN|10 WAYS TO FIGHT', ss=4),
    dict(t0=18.4, t1=20.2, y=925, scale=6, band=.7, es='28 BENDICIONES', en='28 BLESSINGS'),
    dict(t0=20.4, t1=22.3, y=925, scale=5, band=.7, es='MEJORA · COMPRA · DESCUBRE', en='UPGRADE · SHOP · DISCOVER'),
    dict(t0=22.6, t1=24.6, y=235, scale=7, band=.5, es='DESATA TUS DEFINITIVAS', en='UNLEASH YOUR ULTIMATES'),
    dict(t0=24.8, t1=27.0, y=235, scale=6, band=.5, es='LLEGA HASTA EL CAZADOR PÁLIDO', en='REACH THE PALE HUNTER'),
    dict(t0=28.3, t1=30.0, y=815, scale=6, band=0, es='DESAFÍA EL ABISMO', en='DARE TO DESCEND'),
    dict(t0=28.7, t1=30.0, y=935, scale=4, band=0, anim='rise', es='PC · ANDROID', en='PC · ANDROID'),
]

_logo = np.array(Image.open(pixtext.ROOT + '/Shared/assets/ui/ui_logo.png').convert('RGBA'))


def title_overlay(fr, lt, t, lang):
    """27.2-30: fondo oscurecido y logo oficial (ui_logo.png) a x5 por vecino mas cercano."""
    k = min(lt / 0.3, 1.0)
    dark = 1.0 - 0.45 * k
    fr[:] = (fr * dark).astype(np.uint8)
    a = min(lt / 0.12, 1.0)
    sc = 1.0 + 0.5 * (1 - min(lt / 0.25, 1.0) ** 0.5)
    import random
    dx = dy = 0
    if lt < 0.2:
        amp = int(18 * (1 - lt / 0.2)); dx = random.randint(-amp, amp); dy = random.randint(-amp, amp)
    big = np.array(Image.fromarray(_logo, 'RGBA').resize((1500, 420), Image.NEAREST))
    pixtext.blit(fr, big, W // 2, 420, a, sc, dx, dy)
    if lt < 0.15:
        f = 0.8 * (1 - lt / 0.15)
        fr[:] = (fr * (1 - f) + 255 * f).astype(np.uint8)
    return fr


for _s in SHOTS:
    if _s.get('overlay') == 'title':
        _s['overlay'] = title_overlay


def audio(mx, lang, clips):
    import os
    mx.add_music(MUSIC, 0.0, 0.0, 30.0, vol=0.62, fade_in=0.15, fade_out=1.2)
    for sh in SHOTS:
        tsv = os.path.join(clips, sh['clip'] + '.mp4.audio.tsv')
        mx.add_scene_sfx(tsv, sh['ss'], sh['ss'] + sh['dur'], sh['t0'], vol=0.8, skip=('ui_click', 'ui_start_run'))
    S_ = mixer_sfx = __import__('mixer')
    mx.add(S_.sfx('boss_title'), 0.0, 1.0)
    mx.add(S_.sfx('explosion_big'), 0.8, 0.8)
    mx.add(S_.sfx('explosion_big'), 22.4, 0.9)
    mx.add(S_.sfx('boss_title'), 27.2, 1.0)
    mx.add(S_.sfx('explosion_big'), 27.2, 1.0, pitch=0.8)
    mx.add(S_.sfx('level_up'), 28.4, 0.6)
