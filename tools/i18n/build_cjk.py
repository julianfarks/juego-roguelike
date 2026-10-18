"""Genera los atlas de glifos chinos (font_s_cjk / font_b_cjk) con SOLO los caracteres que usa el catalogo zh-Hans.tsv.
Fuente: Noto Sans CJK SC Bold (SIL OFL 1.1), renderizada sin suavizado y con contorno oscuro igual que la fuente latina.
Uso: python3 tools/i18n/build_cjk.py   (hay que repetirlo cuando cambie assets/i18n/zh-Hans.tsv)."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(__file__)
A = os.path.join(HERE, '..', '..', 'Shared', 'assets')
FONT = os.environ.get('CJK_FONT', '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc')
OUTLINE = (22, 12, 28, 255)

def chars_needed():
    s = set("简体中文，。！？：；、（）「」『』…—·")
    for line in open(os.path.join(A, 'i18n', 'zh-Hans.tsv'), encoding='utf8'):
        if line.startswith('#') or '\t' not in line: continue
        v = line.rstrip('\n').split('\t', 1)[1]
        for ch in v:
            if ord(ch) >= 0x2E80 and not (0xE000 <= ord(ch) <= 0xF8FF): s.add(ch)
    return sorted(s)

def build(name, px, pitch, margin, yoff):
    cs = chars_needed()
    cell = px + 2 * margin
    cols = 32
    rows = (len(cs) + cols - 1) // cols
    atlas = Image.new('RGBA', (cols * cell, rows * cell), (0, 0, 0, 0))
    ft = ImageFont.truetype(FONT, px, index=2)   # 2 = Noto Sans CJK SC
    for i, ch in enumerate(cs):
        g = Image.new('L', (cell, cell), 0)
        d = ImageDraw.Draw(g); d.fontmode = '1'
        d.text((margin, margin - 1), ch, font=ft, fill=255)
        fill = g.point(lambda v: 255 if v > 127 else 0)
        dil = fill.filter(ImageFilter.MaxFilter(3))
        tile = Image.new('RGBA', (cell, cell), (0, 0, 0, 0))
        fp, dp, tp = fill.load(), dil.load(), tile.load()
        for y in range(cell):
            for x in range(cell):
                if fp[x, y]: tp[x, y] = (255, 255, 255, 255)
                elif dp[x, y]: tp[x, y] = OUTLINE
        atlas.paste(tile, ((i % cols) * cell, (i // cols) * cell))
    atlas.save(os.path.join(A, 'font', name + '_cjk.png'), optimize=True)
    json.dump({'cell': cell, 'cols': cols, 'pitch': pitch, 'yoff': yoff, 'margin': margin, 'chars': ''.join(cs)},
              open(os.path.join(A, 'font', name + '_cjk.json'), 'w', encoding='utf8'), ensure_ascii=False)
    print(name, len(cs), 'glifos', atlas.size)

if __name__ == '__main__':
    build('font_s', 11, 12, 1, -2)
    build('font_b', 16, 17, 1, -2)
