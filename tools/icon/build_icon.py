"""Genera todos los iconos de Android a partir de tools/icon/icon_source.png (imagen oficial, sin retocar).
Esquinas negras redondeadas -> transparentes en los iconos clasicos (relleno desde los bordes, solo negro puro).
Icono adaptativo: la imagen completa a 68/108 dp centrada sobre fondo oscuro, para que ninguna mascara del launcher recorte el titulo."""
import os
from PIL import Image, ImageDraw
from collections import deque
HERE = os.path.dirname(__file__)
RES = os.path.join(HERE, '..', '..', 'Android', 'app', 'src', 'main', 'res')
src = Image.open(os.path.join(HERE, 'icon_source.png')).convert('RGB')
W, H = src.size

def corner_mask(im, thr=14):
    """Alfa 0 en el negro conectado con los bordes (las esquinas redondeadas); 255 en el resto."""
    px = im.load(); w, h = im.size
    seen = bytearray(w * h); q = deque()
    def dark(x, y):
        r, g, b = px[x, y]; return r < thr and g < thr and b < thr
    for x in range(w):
        for y in (0, h - 1):
            if dark(x, y): q.append((x, y)); seen[y * w + x] = 1
    for y in range(h):
        for x in (0, w - 1):
            if dark(x, y) and not seen[y * w + x]: q.append((x, y)); seen[y * w + x] = 1
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not seen[ny * w + nx] and dark(nx, ny):
                seen[ny * w + nx] = 1; q.append((nx, ny))
    m = Image.new('L', (w, h), 255); mp = m.load()
    for y in range(h):
        for x in range(w):
            if seen[y * w + x]: mp[x, y] = 0
    return m

mask = corner_mask(src)
# suaviza el borde de la mascara (reduce 1 px y desenfoca ligeramente para no dejar halo negro)
from PIL import ImageFilter
mask = mask.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
rgba = src.convert('RGBA'); rgba.putalpha(mask)
print('esquinas transparentes:', sum(1 for v in mask.getdata() if v < 10), 'de', W * H)

def out(path, im):
    os.makedirs(os.path.dirname(path), exist_ok=True); im.save(path, optimize=True)

sizes = {'mdpi': 48, 'hdpi': 72, 'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192}
for d, s in sizes.items():
    ic = rgba.resize((s, s), Image.LANCZOS)
    out(os.path.join(RES, 'mipmap-' + d, 'ic_launcher.png'), ic)
    # version redonda (launchers antiguos): la imagen completa al 78% centrada en un circulo oscuro, sin recortar el titulo
    rd = Image.new('RGBA', (s * 4, s * 4), (0, 0, 0, 0))
    ImageDraw.Draw(rd).ellipse([0, 0, s * 4 - 1, s * 4 - 1], fill=(5, 2, 8, 255))
    inner = round(s * 4 * 0.78); ii = rgba.resize((inner, inner), Image.LANCZOS)
    rd.alpha_composite(ii, ((s * 4 - inner) // 2, (s * 4 - inner) // 2))
    out(os.path.join(RES, 'mipmap-' + d, 'ic_launcher_round.png'), rd.resize((s, s), Image.LANCZOS))

# adaptativo: lienzo 108 dp a 6x = 648 px; imagen de 64 dp
cv = 648; side = round(cv * 68 / 108)
fg = Image.new('RGBA', (cv, cv), (0, 0, 0, 0))
fg.alpha_composite(rgba.resize((side, side), Image.LANCZOS), ((cv - side) // 2, (cv - side) // 2))
out(os.path.join(RES, 'drawable-nodpi', 'ic_launcher_fg.png'), fg)
open(os.path.join(RES, 'values', 'ic_bg.xml'), 'w').write('<?xml version="1.0" encoding="utf-8"?>\n<resources><color name="ic_launcher_bg">#050208</color></resources>\n')
# vista previa
pv = Image.new('RGB', (640, 200), (60, 60, 70))
pv.paste(Image.open(os.path.join(RES, 'mipmap-xxxhdpi', 'ic_launcher.png')).convert('RGBA'), (10, 4), Image.open(os.path.join(RES, 'mipmap-xxxhdpi', 'ic_launcher.png')).convert('RGBA'))
pv.paste(Image.open(os.path.join(RES, 'mipmap-xxxhdpi', 'ic_launcher_round.png')).convert('RGBA'), (220, 4), Image.open(os.path.join(RES, 'mipmap-xxxhdpi', 'ic_launcher_round.png')).convert('RGBA'))
bg = Image.new('RGBA', (cv, cv), (5, 2, 8, 255)); bg.alpha_composite(fg)
ad = bg.resize((192, 192), Image.LANCZOS)
cm = Image.new('L', (192, 192), 0); ImageDraw.Draw(cm).ellipse([12, 12, 179, 179], fill=255)
pv.paste(ad.convert('RGB'), (430, 4), cm)
pv.save('/tmp/icon_prev.png'); print('ok')
