"""Anade (idempotente) el icono 'gem' (moneda premium morada) al atlas ui/icons.png en la ultima casilla libre (127)."""
import json, os
from PIL import Image
A = os.path.join(os.path.dirname(__file__), '..', '..', 'Shared', 'assets', 'ui')
PAL = {
    'o': (24, 8, 48, 255),      # contorno
    'd': (74, 30, 140, 255),    # sombra
    'm': (122, 60, 214, 255),   # medio
    'l': (170, 110, 255, 255),  # luz
    'h': (222, 196, 255, 255),  # brillo
    'w': (255, 255, 255, 255),  # destello
    's': (40, 14, 84, 255),     # sombra profunda
}
ROWS = [
    "................",
    "....oooooooo....",
    "...ohhllllmmo...",
    "..ohwhllllmmdo..",
    ".ohhhlllllmmddo.",
    "ooooooooooooooo.",
    "olhhllmmmmmddsso",
    ".olhllmmmmmddso.",
    "..olllmmmmmdso..",
    "...ollmmmmdso...",
    "....olmmmdso....",
    ".....olmdso.....",
    "......omso......",
    ".......oo.......",
    "................",
    "................",
]
def main():
    jp, ip = os.path.join(A, 'icons.json'), os.path.join(A, 'icons.png')
    d = json.load(open(jp))
    names = d['names']
    if 'gem' not in names:
        assert len(names) == 127, len(names)
        names.append('gem')
        json.dump(d, open(jp, 'w'), ensure_ascii=False)
    idx = names.index('gem')
    im = Image.open(ip).convert('RGBA')
    cols = d.get('cols', 16)
    ox, oy = (idx % cols) * 16, (idx // cols) * 16
    for y, row in enumerate(ROWS):
        for x, c in enumerate(row):
            im.putpixel((ox + x, oy + y), PAL.get(c, (0, 0, 0, 0)))
    im.save(ip)
    print('gem en casilla', idx)
main()
