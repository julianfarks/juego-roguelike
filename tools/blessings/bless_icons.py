#!/usr/bin/env python3
"""Genera el atlas de iconos de las 172 bendiciones nuevas (Shared/assets/ui/bless_icons.png + .json) con el kit de tools/art_fx_ui/icons.py.
Cada icono = motivo principal grande + motivo secundario pequeno (insignia) + paleta; la combinacion es unica por bendicion (se comprueba)."""
import os, sys, math, json, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'art_fx_ui'))
import numpy as np
from PIL import Image
import icons as K
from icons import Ic, RP, XX, YY, flame, drop, star5, heart, bolt, snowflake, wings, skull, shield_shape
from catalog import ENTRIES

A = K.A


def P(ic, pts, cx, cy, s, ramp, **k):
    ic.poly([(cx + x * s, cy + y * s) for x, y in pts], ramp, **k)


def m_sword(ic, cx, cy, s, r):
    ic.line((cx - 4.5 * s, cy + 4.5 * s), (cx + 4.5 * s, cy - 4.5 * s), 2.2 * s, r)
    ic.line((cx - 3.4 * s, cy + 0.6 * s), (cx - 0.6 * s, cy + 3.4 * s), 1.6 * s, 'gold', edge=False)
    ic.line((cx - 4.6 * s, cy + 4.6 * s), (cx - 3.2 * s, cy + 3.2 * s), 1.8 * s, 'wood', edge=False)


def m_dagger(ic, cx, cy, s, r):
    ic.line((cx - 3 * s, cy + 3 * s), (cx + 4.6 * s, cy - 4.6 * s), 1.8 * s, r)
    ic.line((cx - 3.6 * s, cy - 0.2 * s), (cx - 0.2 * s, cy + 3.6 * s), 1.2 * s, 'gold', edge=False)
    ic.line((cx - 4.8 * s, cy + 4.8 * s), (cx - 3.4 * s, cy + 3.4 * s), 1.6 * s, 'wood', edge=False)


def m_flame(ic, cx, cy, s, r):
    flame(ic, cx, cy + 6 * s, 12 * s, 4.6 * s, r if r in ('fire', 'lava', 'orange', 'purple', 'blue', 'cyan', 'green') else 'fire', 'yel')


def m_snow(ic, cx, cy, s, r):
    snowflake(ic, cx, cy, 6.4 * s, r if r in ('ice', 'cyan', 'blue', 'white') else 'ice', 1.1 * s)


def m_bolt(ic, cx, cy, s, r):
    bolt(ic, cx, cy, 0.92 * s, r if r in ('yel', 'cyan', 'purple', 'white', 'blue') else 'yel')


def m_heart(ic, cx, cy, s, r):
    heart(ic, cx, cy - 0.4 * s, 4.7 * s, r if r in ('red', 'pink', 'green', 'purple') else 'red')


def m_skull(ic, cx, cy, s, r):
    skull(ic, cx, cy, 0.95 * s, 'bone')


def m_shield(ic, cx, cy, s, r):
    ic.poly(shield_shape(cx, cy - 6.4 * s, 5.2 * s, 12.8 * s), r)
    ic.poly(shield_shape(cx, cy - 4.6 * s, 3.0 * s, 8.6 * s), 'white' if r != 'white' else 'steel', edge=False)


def m_wing(ic, cx, cy, s, r):
    wings(ic, cx, cy + 0.5 * s, 0.95 * s, r if r in ('white', 'cyan', 'steel', 'dark', 'ice') else 'white')


def m_star(ic, cx, cy, s, r):
    star5(ic, cx, cy, 7.2 * s, 3.0 * s, r if r in ('gold', 'yel', 'white', 'cyan', 'pink') else 'gold')


def m_drop(ic, cx, cy, s, r):
    drop(ic, cx, cy, 4.2 * s, r if r in ('red', 'green', 'ice', 'purple', 'cyan', 'blue', 'teal') else 'red')


def m_eye(ic, cx, cy, s, r):
    ic.ell(cx, cy, 7 * s, 4.2 * s, 'white')
    ic.circ(cx, cy, 2.7 * s, r if r in ('blue', 'cyan', 'green', 'red', 'purple', 'yel') else 'blue')
    ic.circ(cx, cy, 1.1 * s, 'dark', edge=False)


def m_hourglass(ic, cx, cy, s, r):
    rr = r if r in ('gold', 'cyan', 'purple', 'stone') else 'gold'
    P(ic, [(-4, -6), (4, -6), (0.5, 0), (-0.5, 0)], cx, cy, s, 'bone')
    P(ic, [(-0.5, 0), (0.5, 0), (4, 6), (-4, 6)], cx, cy, s, 'bone')
    P(ic, [(-2.4, 4.6), (2.4, 4.6), (0.8, 2), (-0.8, 2)], cx, cy, s, rr, edge=False)
    ic.rect(cx - 5 * s, cy - 7 * s, cx + 5 * s, cy - 5.6 * s, rr)
    ic.rect(cx - 5 * s, cy + 5.6 * s, cx + 5 * s, cy + 7 * s, rr)


def m_coin(ic, cx, cy, s, r):
    ic.circ(cx, cy, 5.8 * s, 'gold')
    ic.ring(cx, cy, 2.8 * s, 3.8 * s, 'copper', edge=False)


def m_soul(ic, cx, cy, s, r):
    flame(ic, cx, cy + 6 * s, 12 * s, 4.4 * s, 'cyan' if r not in ('purple', 'white', 'green') else r, 'white')
    ic.circ(cx - 1.3 * s, cy + 0.2 * s, 0.9 * s, 'dark', edge=False)
    ic.circ(cx + 1.3 * s, cy + 0.2 * s, 0.9 * s, 'dark', edge=False)


def m_orb(ic, cx, cy, s, r):
    ic.circ(cx, cy, 5.6 * s, r if r in RP else 'blue')
    ic.circ(cx - 1.8 * s, cy - 1.8 * s, 1.5 * s, 'white', edge=False)


def m_arrow(ic, cx, cy, s, r):
    ic.line((cx - 5 * s, cy + 5 * s), (cx + 3.4 * s, cy - 3.4 * s), 1.3 * s, 'wood')
    P(ic, [(1.6, -1.6), (6.4, -6.4), (3.2, -6.6), (6.6, -3.2)], cx, cy, s, 'steel', edge=False)
    P(ic, [(2, -5.6), (6.6, -6.6), (5.6, -2)], cx, cy, s, r if r in RP else 'steel')
    ic.line((cx - 5 * s, cy + 5 * s), (cx - 6.2 * s, cy + 3 * s), 1 * s, 'white', edge=False)
    ic.line((cx - 5 * s, cy + 5 * s), (cx - 3 * s, cy + 6.2 * s), 1 * s, 'white', edge=False)


def m_crown(ic, cx, cy, s, r):
    P(ic, [(-6, 4), (-6, -4), (-3, 0), (0, -5.5), (3, 0), (6, -4), (6, 4)], cx, cy, s, r if r in ('gold', 'yel', 'copper', 'white') else 'gold')
    ic.rect(cx - 6 * s, cy + 3 * s, cx + 6 * s, cy + 5 * s, 'copper', edge=False)
    ic.circ(cx, cy + 0.6 * s, 1.2 * s, 'red', edge=False)


def m_ring(ic, cx, cy, s, r):
    ic.ring(cx, cy, 3.4 * s, 6 * s, r if r in RP else 'white')


def m_moon(ic, cx, cy, s, r):
    m = ((XX - cx) ** 2 + (YY - cy) ** 2 <= (6.2 * s) ** 2) & ~((XX - cx - 3 * s) ** 2 + (YY - cy + 1 * s) ** 2 <= (5 * s) ** 2)
    ic.L(m, r if r in ('purple', 'yel', 'white', 'dark', 'ice') else 'purple')


def m_spiral(ic, cx, cy, s, r):
    rr = r if r in RP else 'cyan'
    ic.arc(cx, cy, 4.6 * s, 6.4 * s, 20, 300, rr)
    ic.arc(cx, cy, 2.6 * s, 4.2 * s, 200, 500, rr)
    ic.circ(cx, cy, 1.3 * s, rr, edge=False)


def m_ghost(ic, cx, cy, s, r):
    P(ic, [(-5, 6), (-5, -1), (-3.6, -4.8), (0, -6.4), (3.6, -4.8), (5, -1), (5, 6), (3.2, 4.2), (1.6, 6), (0, 4.2), (-1.6, 6), (-3.2, 4.2)], cx, cy, s, r if r in ('white', 'dark', 'ice', 'purple') else 'white')
    ic.circ(cx - 1.8 * s, cy - 1.4 * s, 1.0 * s, 'dark', edge=False)
    ic.circ(cx + 1.8 * s, cy - 1.4 * s, 1.0 * s, 'dark', edge=False)


def m_cross(ic, cx, cy, s, r):
    rr = r if r in ('green', 'white', 'red', 'cyan', 'gold') else 'green'
    ic.rect(cx - 1.9 * s, cy - 6 * s, cx + 1.9 * s, cy + 6 * s, rr)
    ic.rect(cx - 6 * s, cy - 1.9 * s, cx + 6 * s, cy + 1.9 * s, rr)


def m_clover(ic, cx, cy, s, r):
    for dx, dy in ((-2.6, -2.6), (2.6, -2.6), (-2.6, 2.6), (2.6, 2.6)):
        ic.circ(cx + dx * s, cy + dy * s, 2.9 * s, 'green')
    ic.line((cx, cy), (cx + 2 * s, cy + 6.4 * s), 1 * s, 'wood', edge=False)


def m_fang(ic, cx, cy, s, r):
    P(ic, [(-4, -6), (4, -6), (4.4, -2), (0.6, 6.4), (-0.4, 6.4), (-4.4, -2)], cx, cy, s, 'bone')
    ic.rect(cx - 4.4 * s, cy - 6.4 * s, cx + 4.4 * s, cy - 4.4 * s, r if r in ('red', 'dark', 'purple', 'copper') else 'red', edge=False)


def m_key(ic, cx, cy, s, r):
    rr = r if r in ('gold', 'yel', 'steel', 'copper') else 'gold'
    ic.ring(cx - 2.6 * s, cy - 2.6 * s, 1.6 * s, 3.6 * s, rr)
    ic.line((cx - 0.4 * s, cy - 0.4 * s), (cx + 5.6 * s, cy + 5.6 * s), 1.8 * s, rr)
    ic.rect(cx + 3 * s, cy + 4.4 * s, cx + 5 * s, cy + 6.6 * s, rr, edge=False)


def m_fist(ic, cx, cy, s, r):
    rr = r if r in ('copper', 'orange', 'red', 'stone') else 'copper'
    ic.rect(cx - 5 * s, cy - 3 * s, cx + 5 * s, cy + 5 * s, rr)
    for k in range(4):
        ic.circ(cx - 3.6 * s + k * 2.4 * s, cy - 3.4 * s, 1.5 * s, rr)
    ic.rect(cx - 6 * s, cy + 0.6 * s, cx - 4 * s, cy + 4 * s, rr)


def m_boot(ic, cx, cy, s, r):
    P(ic, [(-3, -6), (2, -6), (2, 1), (6, 3), (6, 6), (-3, 6)], cx, cy, s, r if r in ('wood', 'copper', 'steel', 'dark', 'white') else 'wood')
    ic.rect(cx - 3 * s, cy + 4.6 * s, cx + 6.2 * s, cy + 6.4 * s, 'dark', edge=False)


def m_potion(ic, cx, cy, s, r):
    rr = r if r in ('green', 'red', 'purple', 'cyan', 'pink', 'teal') else 'green'
    ic.rect(cx - 1.6 * s, cy - 6 * s, cx + 1.6 * s, cy - 2 * s, 'bone')
    ic.circ(cx, cy + 2.2 * s, 4.6 * s, rr)
    ic.rect(cx - 2.2 * s, cy - 6.8 * s, cx + 2.2 * s, cy - 5.4 * s, 'wood', edge=False)
    ic.circ(cx - 1.6 * s, cy + 1 * s, 1 * s, 'white', edge=False)


def m_gear(ic, cx, cy, s, r):
    for k in range(8):
        a = math.radians(k * 45)
        ic.circ(cx + 5.2 * s * math.cos(a), cy + 5.2 * s * math.sin(a), 1.5 * s, 'steel', edge=False)
    ic.circ(cx, cy, 4.6 * s, 'steel')
    ic.circ(cx, cy, 1.8 * s, 'dark', edge=False)


def m_hammer(ic, cx, cy, s, r):
    ic.line((cx - 4 * s, cy + 5 * s), (cx + 2 * s, cy - 1 * s), 1.8 * s, 'wood')
    P(ic, [(-1, -6.4), (6.4, -1), (3.6, 2), (-3.6, -4)], cx, cy, s, r if r in ('stone', 'steel', 'copper', 'gold') else 'stone')


def m_sun(ic, cx, cy, s, r):
    for k in range(8):
        a = math.radians(k * 45)
        ic.line((cx + 4.4 * s * math.cos(a), cy + 4.4 * s * math.sin(a)), (cx + 7 * s * math.cos(a), cy + 7 * s * math.sin(a)), 1.2 * s, 'yel', edge=False)
    ic.circ(cx, cy, 3.8 * s, r if r in ('yel', 'gold', 'white', 'orange') else 'yel')


def m_leaf(ic, cx, cy, s, r):
    P(ic, [(-5, 5), (-4, -1), (0, -5.6), (5.4, -6), (5, 0), (1, 5), (-4, 5.6)], cx, cy, s, r if r in ('green', 'teal') else 'green')
    ic.line((cx - 4 * s, cy + 4 * s), (cx + 3 * s, cy - 3 * s), 0.8 * s, 'green', edge=False)


def m_chain(ic, cx, cy, s, r):
    ic.ring(cx - 2.6 * s, cy + 2.2 * s, 1.6 * s, 3.4 * s, 'steel')
    ic.ring(cx + 2.6 * s, cy - 2.2 * s, 1.6 * s, 3.4 * s, r if r in ('steel', 'gold', 'purple') else 'steel')


def m_bomb(ic, cx, cy, s, r):
    ic.circ(cx - 0.6 * s, cy + 1.6 * s, 4.8 * s, 'dark')
    ic.line((cx + 2 * s, cy - 2 * s), (cx + 4.4 * s, cy - 5 * s), 1 * s, 'wood', edge=False)
    ic.circ(cx + 4.8 * s, cy - 5.4 * s, 1.4 * s, r if r in ('fire', 'orange', 'lava', 'yel') else 'fire', edge=False)
    ic.circ(cx - 2.2 * s, cy * 1 + 0 * s, 0.9 * s, 'white', edge=False)


def m_book(ic, cx, cy, s, r):
    ic.rect(cx - 5 * s, cy - 5.6 * s, cx + 5 * s, cy + 5.6 * s, r if r in ('purple', 'blue', 'red', 'copper', 'pink', 'teal') else 'purple')
    ic.rect(cx - 3.4 * s, cy - 4 * s, cx + 4 * s, cy + 4 * s, 'bone', edge=False)
    ic.circ(cx + 0.2 * s, cy, 1.6 * s, 'gold', edge=False)


def m_tower(ic, cx, cy, s, r):
    rr = r if r in ('stone', 'steel', 'bone', 'gold') else 'stone'
    ic.rect(cx - 4 * s, cy - 3 * s, cx + 4 * s, cy + 6 * s, rr)
    for dx in (-4.4, -0.8, 2.8):
        ic.rect(cx + dx * s, cy - 6 * s, cx + (dx + 1.8) * s, cy - 2.4 * s, rr, edge=False)
    ic.rect(cx - 1.2 * s, cy + 2.4 * s, cx + 1.2 * s, cy + 6 * s, 'dark', edge=False)


def m_hand(ic, cx, cy, s, r):
    rr = r if r in ('copper', 'bone', 'orange') else 'copper'
    ic.rect(cx - 4 * s, cy - 1 * s, cx + 4 * s, cy + 6 * s, rr)
    for k in range(4):
        ic.rect(cx - 4 * s + k * 2.1 * s, cy - 6 * s + (0.8 if k in (0, 3) else 0) * s, cx - 2.4 * s + k * 2.1 * s, cy, rr, edge=False)
    ic.rect(cx - 6 * s, cy + 0.6 * s, cx - 3.4 * s, cy + 3 * s, rr)


def m_feather(ic, cx, cy, s, r):
    P(ic, [(-4, 6), (-5, 0), (-1, -5), (5.4, -6.4), (4, 0), (0, 5)], cx, cy, s, r if r in ('white', 'cyan', 'ice', 'dark') else 'white')
    ic.line((cx - 4.4 * s, cy + 5.6 * s), (cx + 3.6 * s, cy - 4.6 * s), 0.8 * s, 'steel', edge=False)


def m_note(ic, cx, cy, s, r):
    rr = r if r in ('white', 'gold', 'cyan', 'pink') else 'white'
    ic.circ(cx - 2 * s, cy + 4 * s, 2.4 * s, rr)
    ic.rect(cx + 0.2 * s, cy - 5.6 * s, cx + 1.8 * s, cy + 4 * s, rr, edge=False)
    P(ic, [(0.2, -5.6), (5.6, -3.6), (5.6, -1), (0.2, -3)], cx, cy, s, rr, edge=False)


def m_altar(ic, cx, cy, s, r):
    ic.rect(cx - 5.6 * s, cy + 1 * s, cx + 5.6 * s, cy + 6 * s, 'stone')
    ic.rect(cx - 4 * s, cy - 1 * s, cx + 4 * s, cy + 1.4 * s, 'bone', edge=False)
    flame(ic, cx, cy - 0.4 * s, 6 * s, 2.4 * s, r if r in ('fire', 'cyan', 'purple', 'green') else 'fire', 'yel')


def m_stone(ic, cx, cy, s, r):
    P(ic, [(-6, 4), (-5, -2), (-1, -5.6), (4, -4.6), (6.4, 0), (5, 5)], cx, cy, s, r if r in ('stone', 'steel', 'copper', 'dark') else 'stone')
    ic.line((cx - 2 * s, cy - 2 * s), (cx + 1 * s, cy + 2 * s), 0.8 * s, 'dark', edge=False)


MOTIFS = {k[2:]: v for k, v in globals().items() if k.startswith('m_')}
# rampa por defecto de cada motivo en la insignia pequena
BADGE_RAMP = {'sword': 'steel', 'dagger': 'steel', 'flame': 'fire', 'snow': 'ice', 'bolt': 'yel', 'heart': 'red', 'skull': 'bone', 'shield': 'blue', 'wing': 'white', 'star': 'gold', 'drop': 'red',
              'eye': 'blue', 'hourglass': 'gold', 'coin': 'gold', 'soul': 'cyan', 'orb': 'cyan', 'arrow': 'steel', 'crown': 'gold', 'ring': 'white', 'moon': 'purple', 'spiral': 'cyan', 'ghost': 'white',
              'cross': 'green', 'clover': 'green', 'fang': 'red', 'key': 'gold', 'fist': 'copper', 'boot': 'wood', 'potion': 'green', 'gear': 'steel', 'hammer': 'stone', 'sun': 'yel', 'leaf': 'green',
              'chain': 'steel', 'bomb': 'fire', 'book': 'purple', 'tower': 'stone', 'hand': 'copper', 'feather': 'white', 'note': 'white', 'altar': 'fire', 'stone': 'stone'}


CORNERS = [(12.0, 12.0), (3.6, 12.0), (12.0, 3.6), (3.6, 3.6)]


def render(m1, m2, ramp, v=0):
    ic = Ic()
    MOTIFS[m1](ic, 7.2 + (0.4 if v >= 1 else 0), 7.4, 0.86, ramp)
    if m2 and m2 != m1:
        MOTIFS[m2](ic, CORNERS[v % 4][0], CORNERS[v % 4][1], 0.40, BADGE_RAMP[m2])
    elif m2 == m1:
        MOTIFS[m2](ic, CORNERS[v % 4][0], CORNERS[v % 4][1], 0.40, 'white' if ramp != 'white' else 'gold')
    return ic.finish()


def build():
    cols = 16
    n = len(ENTRIES)
    rows = (n + cols - 1) // cols
    atlas = np.zeros((rows * 16, cols * 16, 4))
    names, seen, hashes = [], set(), set()
    # los iconos de las bendiciones originales tambien cuentan para la unicidad
    base = np.array(Image.open(A + '/ui/icons.png').convert('RGBA'))
    bnames = json.load(open(A + '/ui/icons.json'))['names']
    for i, nm in enumerate(bnames):
        if nm.startswith('b_'):
            c = base[(i // 16) * 16:(i // 16) * 16 + 16, (i % 16) * 16:(i % 16) * 16 + 16]
            hashes.add(hashlib.md5(c.tobytes()).hexdigest())
    for i, e in enumerate(ENTRIES):
        m1, m2, ramp = e['ic']
        assert m1 in MOTIFS and (m2 in MOTIFS), (e['key'], m1, m2)
        assert ramp in RP, (e['key'], ramp)
        sig = (m1, m2, ramp)
        assert sig not in seen, ('icono repetido (misma combinacion)', e['key'], sig)
        seen.add(sig)
        for v in range(8):
            img = render(m1, m2, ramp, v)
            h = hashlib.md5(K.to_u8(img).tobytes()).hexdigest()
            if h not in hashes:
                break
        assert h not in hashes, ('icono identico a otro', e['key'])
        hashes.add(h)
        atlas[(i // cols) * 16:(i // cols) * 16 + 16, (i % cols) * 16:(i % cols) * 16 + 16] = img
        names.append('bx_' + e['key'])
    K.ensure(A + '/ui')
    Image.fromarray(K.to_u8(atlas), 'RGBA').save(A + '/ui/bless_icons.png', optimize=True)
    json.dump({"cell": 16, "cols": cols, "names": names}, open(A + '/ui/bless_icons.json', 'w'))
    # vista previa ampliada para revisar a ojo
    K.ensure(K.PREV)
    im = Image.open(A + '/ui/bless_icons.png').convert('RGBA')
    bg = Image.new('RGBA', im.size, (30, 26, 40, 255)); bg.alpha_composite(im)
    bg.resize((im.width * 5, im.height * 5), Image.NEAREST).convert('RGB').save(K.PREV + '/bless_icons.png')
    print('ok', n, 'iconos')


if __name__ == '__main__':
    build()
