"""Genera el icono de Windows (PC/packaging/icon.ico + icon_256.png) a partir de la imagen oficial tools/icon/icon_source.png.
Mismo tratamiento de esquinas que el icono de Android (tools/icon/build_icon.py). Uso: python3 PC/packaging/make_icon.py"""
import os
from PIL import Image, ImageFilter
from collections import deque
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', '..', 'tools', 'icon', 'icon_source.png')
src = Image.open(SRC).convert('RGB')
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

mask = corner_mask(src).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
rgba = src.convert('RGBA'); rgba.putalpha(mask)
big = rgba.resize((256, 256), Image.LANCZOS)
big.save(os.path.join(HERE, 'icon_256.png'), optimize=True)
big.save(os.path.join(HERE, 'icon.ico'), sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print('ok')
