"""Arte de los companeros: espiritu de fuego, de hielo y de sombra (idle 6 cuadros, flotan)."""
import sys, math
sys.path.insert(0, '../art_ops')
from kit import *
from PIL import Image

W, Hh = 32, 36

def fire(f):
    c = Cv(W, Hh); ph = f / 6 * 2 * math.pi
    bob = round(math.sin(ph) * 2); fl = round(math.sin(ph * 2) * 1.5)
    cx = 16; top = 6 + bob
    # lengua de fuego: gota con punta que ondea
    c.ell(cx - 9, top + 8, cx + 9, top + 28, FIRE[1])
    c.poly([(cx - 8, top + 14), (cx + 8, top + 14), (cx + fl * 2, top - 4)], FIRE[1])
    c.poly([(cx - 5, top + 12), (cx + 2, top + 10), (cx + fl + 3, top + 1)], FIRE[2])
    c.ell(cx - 7, top + 10, cx + 7, top + 26, FIRE[2])
    c.ell(cx - 5, top + 13, cx + 5, top + 25, FIRE[3])
    c.ell(cx - 3, top + 17, cx + 3, top + 25, FIRE[4])
    # ojos y boca
    for ex in (cx - 5, cx + 2):
        c.rect(ex, top + 15, ex + 2, top + 19, OUT); c.px(ex + 1, top + 16, STEEL[6])
    c.line(cx - 2, top + 22, cx + 1, top + 22, OUT)
    c.outline(OUT)
    for k in range(3):   # brasas
        a = ph + k * 2.1
        c.px(cx + round(math.cos(a) * 12), top + 10 + round(math.sin(a) * 8) - (f + k * 2) % 6, FIRE[3])
    return c

def ice(f):
    c = Cv(W, Hh); ph = f / 6 * 2 * math.pi
    bob = round(math.sin(ph) * 2); cx = 16; top = 6 + bob
    # cristal hexagonal alargado
    c.poly([(cx, top), (cx + 10, top + 9), (cx + 10, top + 22), (cx, top + 30), (cx - 10, top + 22), (cx - 10, top + 9)], ICE[2])
    c.poly([(cx, top), (cx - 10, top + 9), (cx - 10, top + 22), (cx, top + 30)], ICE[1])
    c.poly([(cx, top + 1), (cx + 8, top + 9), (cx + 7, top + 16), (cx, top + 8)], ICE[4])
    c.poly([(cx, top + 8), (cx + 7, top + 16), (cx + 5, top + 22), (cx, top + 18)], ICE[3])
    c.line(cx, top + 2, cx, top + 28, ICE[3])
    # cara
    for ex in (cx - 6, cx + 2):
        c.rect(ex, top + 13, ex + 3, top + 18, OUT); c.px(ex + 1, top + 14, STEEL[6]); c.px(ex + 2, top + 14, STEEL[6])
    c.line(cx - 2, top + 22, cx + 2, top + 22, OUT)
    c.outline(OUT)
    for k in range(2):   # esquirlas orbitando
        a = ph + k * math.pi
        x = cx + round(math.cos(a) * 14); y = top + 15 + round(math.sin(a) * 5)
        c.poly([(x, y - 3), (x + 2, y), (x, y + 3), (x - 2, y)], ICE[4]); c.px(x, y, STEEL[6])
    return c

def shadow(f):
    c = Cv(W, Hh); ph = f / 6 * 2 * math.pi
    bob = round(math.sin(ph) * 2); cx = 16; top = 5 + bob
    # capucha + cola andrajosa
    for i in range(0, 14):
        y = top + 18 + i; w = max(1, 9 - i * 8 // 14)
        x = cx + round(math.sin(ph + i * 0.5) * (1 + i * 0.15))
        c.rect(x - w, y, x + w, y, SHADOW[2] if i % 3 else SHADOW[1])
        if i % 4 == 3: c.px(x - w, y, (0, 0, 0, 0)); c.px(x + w, y, (0, 0, 0, 0))
    c.ell(cx - 10, top + 2, cx + 10, top + 26, SHADOW[2])
    c.poly([(cx - 8, top + 6), (cx, top - 2), (cx + 8, top + 6)], SHADOW[2])
    c.ell(cx - 7, top + 6, cx + 7, top + 22, SHADOW[0])
    c.ell(cx - 9, top + 4, cx - 3, top + 12, SHADOW[3])   # luz del borde
    # ojos violeta brillantes
    gl = VIOL[4] if f % 3 else VIOL[3]
    for ex in (cx - 5, cx + 2):
        c.rect(ex, top + 13, ex + 2, top + 16, gl); c.px(ex + 1, top + 14, STEEL[6])
    c.outline(OUT)
    for k in range(3):   # motas de sombra
        a = ph + k * 2.1
        c.px(cx + round(math.cos(a) * 13), top + 14 + round(math.sin(a) * 9), VIOL[2])
    return c

if __name__ == '__main__':
    ims = []
    for nm, fn, glow in (('cmp_fire', fire, 0), ('cmp_ice', ice, 0), ('cmp_shadow', shadow, 0)):
        ims.append(save(nm, [[fn(i) for i in range(6)]], {'idle': {'row': 0, 'n': 6, 'fps': 7, 'loop': True}}, pivot=[16, 34], body=[18, 28]))
    prev = Image.new('RGBA', (W * 6 * 3 + 20, Hh * 3), (30, 28, 44, 255))
    for i, im in enumerate(ims): prev.alpha_composite(im, (0, 0)) if False else prev.paste(im, (i * (W * 6 + 10), 0), im)
    prev = prev.resize((prev.width * 4, prev.height * 4), Image.NEAREST); prev.save('/tmp/cmp_prev.png'); print('ok')
