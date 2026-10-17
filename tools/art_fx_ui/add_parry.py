"""Icono 'parry': escudo actual + espada cruzada / chispa de impacto. Genera 3 variantes (comparacion) y anade la elegida al atlas (casilla 128, nueva fila).
Uso: python3 add_parry.py [A|B|C]   (por defecto la elegida: CHOSEN)"""
import sys, json, os
from icons import *
CHOSEN = 'C'

def spark(ic, cx, cy, r=2.6):
    # destello de 4 puntas (impacto)
    ic.poly([(cx, cy - r), (cx + .7, cy - .7), (cx + r, cy), (cx + .7, cy + .7), (cx, cy + r), (cx - .7, cy + .7), (cx - r, cy), (cx - .7, cy - .7)], 'yel', edge=False)
    ic.px(cx - .5, cy - .5, RP['white'][4]); ic.px(cx + .5 - 1, cy + .5 - 1, RP['white'][4])

def base_shield(ic, dx=0):
    ic.poly(shield_shape(8 + dx, 1.8, 5.8, 12.4), 'steel')
    ic.rect(7 + dx, 3.4, 9 + dx, 12, 'gold', edge=False); ic.rect(4 + dx, 6, 12 + dx, 7.8, 'gold', edge=False)

def var_A(ic):  # espada detras (cruzada), punta arriba-derecha, empunadura abajo-izquierda
    sword(ic, 0.8, 15.2, 15.2, 0.8, 2.0)
    base_shield(ic)
    ic.px(13, 3, RP['white'][4])

def var_B(ic):  # escudo + chispa de impacto en la esquina y grieta de luz
    base_shield(ic, -0.6)
    spark(ic, 12.6, 3.6, 3.0)
    ic.px(10, 5, RP['yel'][3]); ic.px(10, 4, RP['yel'][2])

def var_C(ic):  # espada cruzada detras (mas corta) + chispa en el cruce
    sword(ic, 1.2, 14.8, 14.8, 1.2, 1.8)
    base_shield(ic, -0.4)
    spark(ic, 12.8, 3.4, 2.8)

VARS = {'A': var_A, 'B': var_B, 'C': var_C}

def render_var(k):
    ic = Ic(); VARS[k](ic); return ic.finish()

def main():
    A_ = A + '/ui'
    if len(sys.argv) > 1 and sys.argv[1] == 'cmp':
        sheet = Image.new('RGBA', (16 * 4 * 6, 16 * 6), (30, 26, 40, 255))
        # ref (escudo actual) + variantes, a 6x y tamano real x2 abajo
        ref = Ic(); I['shield'](ref); items = [('ref', ref.finish())] + [(k, render_var(k)) for k in 'ABC']
        for n, (k, a) in enumerate(items):
            im = Image.fromarray(to_u8(a), 'RGBA').resize((96, 96), Image.NEAREST)
            sheet.alpha_composite(im, (n * 96, 0))
        # tamano real: boton circular r=16 sobre fondo, icono x1 (16px) y x2
        real = Image.new('RGBA', (4 * 80, 80), (20, 18, 30, 255))
        d = ImageDraw.Draw(real)
        for n, (k, a) in enumerate(items):
            cx = n * 80 + 40; d.ellipse([cx - 31, 8, cx + 31, 70], fill=(70, 80, 100, 255), outline=(255, 224, 112, 255))
            real.alpha_composite(Image.fromarray(to_u8(a), 'RGBA').resize((32, 32), Image.NEAREST), (cx - 16, 24))
        out = Image.new('RGBA', (384, 96 + 80)); out.alpha_composite(sheet.crop((0, 0, 384, 96)), (0, 0)); out.alpha_composite(real, (0, 96))
        ensure(PREV); out.convert('RGB').save(PREV + '/parry_variantes.png'); print('ok'); return
    k = sys.argv[1] if len(sys.argv) > 1 else CHOSEN
    jp, ip = A_ + '/icons.json', A_ + '/icons.png'
    d = json.load(open(jp)); names = d['names']
    if 'parry' not in names: names.append('parry')
    idx = names.index('parry')
    im = Image.open(ip).convert('RGBA')
    rows = idx // 16 + 1
    if im.height < rows * 16:
        n = Image.new('RGBA', (im.width, rows * 16), (0, 0, 0, 0)); n.alpha_composite(im); im = n
    ox, oy = (idx % 16) * 16, (idx // 16) * 16
    tile = Image.fromarray(to_u8(render_var(k)), 'RGBA')
    for y in range(16):
        for x in range(16): im.putpixel((ox + x, oy + y), (0, 0, 0, 0))
    im.alpha_composite(tile, (ox, oy))
    im.save(ip, optimize=True); json.dump(d, open(jp, 'w'), ensure_ascii=False); print('parry en casilla', idx, 'variante', k)
main()
