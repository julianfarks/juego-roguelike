#!/usr/bin/env python3
"""Genera el arte pixel art del Arsenal (iconos 16x16 y proyectiles 24x24 x4 fotogramas).
Solo AÑADE: nuevas celdas al final de ui/icons.png (+ nombres en icons.json) y nuevas filas al final de fx/fx_proj.png (+ anims en fx_proj.json).
No toca nada existente. Idempotente: si ya estan los nombres, no vuelve a añadirlos.
Uso: python3 tools/gen_arsenal_art.py [--preview /tmp/prev.png]
"""
import json, math, os, sys
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Shared', 'assets')
K = (20, 16, 28, 255)
PAL = {
    'k': K,
    'd': (84, 92, 110, 255), 'm': (152, 162, 180, 255), 'l': (216, 224, 236, 255), 'w': (255, 255, 255, 255),
    'b': (92, 54, 26, 255), 'B': (150, 92, 42, 255), 'y': (214, 160, 76, 255),
    'g': (190, 150, 36, 255), 'G': (255, 226, 122, 255),
    'r': (150, 28, 44, 255), 'R': (255, 90, 74, 255),
    'o': (206, 98, 24, 255), 'O': (255, 176, 64, 255), 'Y': (255, 240, 150, 255),
    'p': (96, 52, 168, 255), 'P': (176, 128, 255, 255), 'q': (56, 28, 110, 255),
    'c': (34, 120, 196, 255), 'C': (122, 240, 255, 255),
    'n': (36, 130, 58, 255), 'N': (122, 224, 74, 255),
    't': (40, 150, 150, 255), 'T': (150, 255, 230, 255),
    'e': (46, 40, 60, 255),
}


class Cv:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = [[None] * w for _ in range(h)]

    def set(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = PAL[c] if isinstance(c, str) else c

    def line(self, x0, y0, x1, y1, c, t=1):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) * 2 + 1
        for i in range(n + 1):
            f = i / n
            x, y = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
            self.set(x, y, c)
            if t >= 2:
                self.set(x + 1, y, c)

    def rect(self, x, y, w, h, c):
        for j in range(h):
            for i in range(w):
                self.set(x + i, y + j, c)

    def disc(self, cx, cy, r, c):
        for y in range(self.h):
            for x in range(self.w):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + 0.3:
                    self.set(x, y, c)

    def ring(self, cx, cy, r0, r1, c):
        for y in range(self.h):
            for x in range(self.w):
                d = (x - cx) ** 2 + (y - cy) ** 2
                if r0 * r0 - 0.2 <= d <= r1 * r1 + 0.3:
                    self.set(x, y, c)

    def art(self, rows, ox=0, oy=0):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch != '.' and ch != ' ':
                    self.set(ox + i, oy + j, ch)

    def outline(self, col=K):
        src = [r[:] for r in self.px]
        for y in range(self.h):
            for x in range(self.w):
                if src[y][x] is None:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.w and 0 <= ny < self.h and src[ny][nx] is not None and src[ny][nx] != col:
                            self.px[y][x] = col
                            break

    def image(self):
        im = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0))
        for y in range(self.h):
            for x in range(self.w):
                if self.px[y][x] is not None:
                    im.putpixel((x, y), self.px[y][x])
        return im


# --------------------------------------------------------------------------- iconos 16x16 (dibujados a mano)
ICONS = {}

ICONS['w_knife'] = [
    '................',
    '.......l....l...',
    '......lml..lml..',
    '.....lmdl.lmdl..',
    '....lmdl..lmdl..',
    '...lmdl...gdl...',
    '..lmdl..l.dg....',
    '..gdl..lm.bg....',
    '.bgg...gd.b.....',
    '.bb....bb.......',
    '..b.....b..lll..',
    '........lmd.....',
    '....lll.gb......',
    '....mdd.b.......',
    '....gb..........',
    '................',
]
ICONS['w_bolt'] = [
    '................',
    '........pp......',
    '.......pCCp.....',
    '....dd.pCYCp....',
    '...dmmdpCCCp....',
    '...dmdd.pCp.....',
    '..dmd.dd.p......',
    '.dmd...dd.......',
    '.dBBbbbbddbbbbG.',
    '.dmd...dd...GG..',
    '..dmd.dd.G.G....',
    '...dmdd..G......',
    '....dd..........',
    '................',
    '................',
    '................',
]
ICONS['w_axe'] = [
    '................',
    '.......llll.....',
    '......lmmmdl....',
    '.....lmmOmmdl...',
    '....lmmmmOmmdb..',
    '....lmmmmmmdBb..',
    '.....lmdddddBb..',
    '......ddd.dBb...',
    '..........By....',
    '.........By.....',
    '........By......',
    '.......By.......',
    '......By........',
    '.....By.........',
    '....bb..........',
    '................',
]
ICONS['w_orb'] = [
    '................',
    '.....pppppp.....',
    '...ppPPPPPPpp...',
    '..pPPppppppPPp..',
    '..pPppPPPPppPp..',
    '.pPpPPppppPPpPp.',
    '.pPpPpwPPPpPpPp.',
    '.pPpPppppPPpPpq.',
    '.pPpPPPPPPpPpPq.',
    '.pPPpppppppPPpq.',
    '..pPPPPPPPPPpq..',
    '..qppPPPPPPpqq..',
    '...qqpppppqq....',
    '.....qqqqq......',
    '................',
    '................',
]
ICONS['w_bow'] = [
    '................',
    '....bB..........',
    '....bBB.......c.',
    '....bBBy.....cl.',
    '...bBBy..lllcC..',
    '...bBy..l.ccl...',
    '..bBy..l.cl.....',
    '..bBy.w.lBBBBBBN',
    '..bBy..l.cl..NN.',
    '...bBy..l.ccl...',
    '...bBBy..lllcC..',
    '....bBBy.....cl.',
    '....bBB.......c.',
    '....bB..........',
    '................',
    '................',
]
ICONS['w_chakram'] = [
    '................',
    '.......m........',
    '....m..ll..m....',
    '.....mlllllm....',
    '...mmllddddllmm.',
    '..mllddmmmmddllm',
    '..llddm....mddll',
    '.mlldm..C...mdll',
    '.mlldm.....mddll',
    '..llddm....mddll',
    '..mlldddmmdddlm.',
    '...mmlldddllmm..',
    '....m.mllllm.m..',
    '.......ll.......',
    '........m.......',
    '................',
]
ICONS['w_wand'] = [
    '................',
    '..........C.....',
    '.......R.CCC.O..',
    '......RRR.C.OOO.',
    '.....RRwRC...O..',
    '......RRR.......',
    '.......bBb......',
    '......bBy.......',
    '.....bBy........',
    '....bBy.........',
    '...bBy..........',
    '..bBy...........',
    '.bBy............',
    '.bb.............',
    '................',
    '................',
]
ICONS['w_spear'] = [
    '..............ll',
    '.............lmd',
    '............lmd.',
    '...........lmmd.',
    '..........lmdd..',
    '.........gBGd...',
    '........By......',
    '.......By.......',
    '......By........',
    '.....ByR........',
    '....ByRR........',
    '...BybR.........',
    '..By.R..........',
    '.bb.............',
    '................',
    '................',
]
ICONS['w_ember'] = [
    '................',
    '................',
    '..........O..Y..',
    '...dddddd.OOYY..',
    '..dmmmmmddOOOY.O',
    '.dmllmmmmdgOOYOO',
    '.dmllmmmmdgOYOOY',
    '.dmmmmmmddgOOOO.',
    '..ddddddd.OOYO..',
    '...bBd.d...O.O..',
    '...bBd......O...',
    '..bBBd..........',
    '..bbbd..........',
    '................',
    '................',
    '................',
]
ICONS['w_summon'] = [
    '......tTTt......',
    '.....tTwTTt.....',
    '....tTkTTkTt....',
    '....tTTTTTTt....',
    '.....tTkkTt.....',
    '..T...tttt...T..',
    '.TT....bB....TT.',
    '..T....bBy...T..',
    '.......bBy......',
    '......bBy.......',
    '......bBy.......',
    '.....bBy........',
    '.....bBy........',
    '....bBy.........',
    '....bb..........',
    '................',
]
ICONS['swap'] = [
    '................',
    '....CCCCCCC.....',
    '..CCClllllCCC...',
    '.CClC......CCC..',
    '.Cl.........CC..',
    '.C........CCCCC.',
    '..........CCCl..',
    '..........CCl...',
    '...lCC..........',
    '..lCCC..........',
    '.CCCCC........C.',
    '.CC.........lC..',
    '..CCC......ClC..',
    '...CCClllllCC...',
    '.....CCCCCCC....',
    '................',
]
ICONS['bag'] = [
    '................',
    '.....kkkkk......',
    '....kbBBBbk.....',
    '...kbByyyBbk....',
    '..kbByyyyyBbk...',
    '..kbBBBBBBBbk...',
    '.kbBByyyyyBBbk..',
    '.kbBygGGGGyBbk..',
    '.kbBygGggGyBbk..',
    '.kbBByyyyyBBbk..',
    '.kbBBBBBBBBBbk..',
    '.kbBBByyyBBBbk..',
    '..kbBBBBBBBbk...',
    '...kkbbbbbkk....',
    '................',
    '................',
]


def _dagger(c, px, py, ang, bl=8):
    dx, dy = math.cos(ang), -math.sin(ang)
    nx, ny = -dy, dx
    for i in range(3):                                  # empuñadura
        c.set(px + dx * i, py + dy * i, 'b' if i % 2 else 'B')
    gx, gy = px + dx * 3, py + dy * 3
    c.set(gx + nx, gy + ny, 'g'); c.set(gx, gy, 'G'); c.set(gx - nx, gy - ny, 'g')   # guarda
    for i in range(4, 4 + bl):                          # hoja
        t = i - 4
        x, y = px + dx * i, py + dy * i
        c.set(x, y, 'm')
        if t < bl - 2:
            c.set(x + nx * 0.8, y + ny * 0.8, 'l')
        if t == bl - 1:
            c.set(x, y, 'w')


def draw_custom(name, c):
    if name == 'w_knife':
        for a in (80, 52, 24):
            _dagger(c, 3, 13, math.radians(a), 8)
        return True
    if name == 'w_bolt':
        c.line(12, 2, 9, 5, 'm'); c.line(9, 5, 8, 8, 'm'); c.line(12, 15, 9, 12, 'm'); c.line(9, 12, 8, 8, 'm')   # brazos
        c.line(8, 8, 8, 9, 'd')
        c.line(12, 2, 4, 8, 'l'); c.line(12, 15, 4, 9, 'l')                                                      # cuerda
        c.rect(2, 8, 8, 2, 'B'); c.rect(2, 8, 8, 1, 'y'); c.rect(1, 8, 2, 2, 'b')                                   # caja
        c.line(5, 8, 13, 8, 'y'); c.set(5, 7, 'N')                                                                  # virote
        c.set(14, 8, 'C'); c.set(15, 8, 'w'); c.set(14, 7, 'C'); c.set(14, 9, 'C')
        return True
    if name == 'w_bow':
        for a in range(105, 256, 3):                    # arco de madera
            ar = math.radians(a)
            c.set(11 + math.cos(ar) * 8, 8 - math.sin(ar) * 7.2, 'B')
            c.set(11 + math.cos(ar) * 7, 8 - math.sin(ar) * 6.2, 'y') if a % 6 == 0 else None
        c.line(9, 1, 9, 14, 'l')                        # cuerda
        c.line(5, 8, 15, 8, 'y')                        # flecha
        c.set(15, 8, 'w'); c.set(14, 8, 'm'); c.set(13, 7, 'm'); c.set(13, 9, 'm')
        c.set(5, 7, 'N'); c.set(5, 9, 'N'); c.set(6, 7, 'N'); c.set(6, 9, 'N')
        return True
    return False


def build_icon(name):
    c = Cv(16, 16)
    if not draw_custom(name, c):
        c.art(ICONS[name])
    c.outline()
    return c.image()


# --------------------------------------------------------------------------- proyectiles 24x24 (4 fotogramas)
def pj_longarrow(f):
    c = Cv(24, 24)
    y = 12
    c.line(2, y, 18, y, 'B')               # asta de madera
    c.line(2, y - 1, 18, y - 1, 'y')
    for k in range(3):                     # plumas verdes
        c.set(2 + k, y - 2 - (k % 2), 'N'); c.set(2 + k, y + 1 + (k % 2), 'n')
    c.set(1, y - 1, 'N'); c.set(1, y, 'n')
    c.art(['..l..', '.lmd.', 'lmmmd', '.ldd.', '..d..'][0:0], 0, 0)
    c.set(19, y - 2, 'm'); c.set(19, y + 1, 'd')
    c.line(19, y - 1, 22, y - 1, 'l'); c.line(19, y, 22, y, 'm')
    c.set(20, y - 2, 'l'); c.set(20, y + 1, 'd')
    c.set(23, y - 1, 'w') if f % 2 == 0 else c.set(23, y, 'w')
    c.set(5 + f * 3, y - 1, 'Y')           # destello que recorre el asta
    c.outline()
    return c.image()


def pj_chakram(f):
    c = Cv(24, 24)
    cx = cy = 11.5
    c.ring(cx, cy, 4.2, 9.2, 'm')
    c.ring(cx, cy, 4.2, 5.6, 'd')
    c.ring(cx, cy, 8.0, 9.2, 'l')
    for k in range(8):                     # dientes
        a = k * math.pi / 4 + 0.2
        c.line(cx + math.cos(a) * 8.5, cy + math.sin(a) * 8.5, cx + math.cos(a) * 11.2, cy + math.sin(a) * 11.2, 'l')
    a = f * math.pi / 2 + 0.6              # brillo giratorio
    c.set(cx + math.cos(a) * 7, cy + math.sin(a) * 7, 'C'); c.set(cx + math.cos(a) * 7.8, cy + math.sin(a) * 7.8, 'w')
    c.outline()
    return c.image()


def pj_spear(f):
    c = Cv(24, 24)
    y = 12
    c.line(0, y, 16, y, 'B'); c.line(0, y - 1, 16, y - 1, 'y')
    c.line(2, y + 1, 4, y + 2, 'R'); c.line(2, y - 2, 4, y - 3, 'R'); c.line(3, y, 6, y, 'r')
    c.art(['..lll...', '.lmmmll.', 'lmmmmmml', 'dmmmmmdd', '.ddddd..'], 15, 9) if False else None
    for i, (x0, x1) in enumerate([(16, 18), (15, 20), (15, 22), (16, 23), (18, 22), (19, 21)]):
        pass
    # hoja de acero en forma de hoja
    pts = [(16, 12), (17, 10), (19, 9), (21, 10), (23, 12), (21, 13), (19, 14), (17, 13)]
    for x in range(16, 24):
        hw = max(0, int(round(2.4 - abs(x - 19.0) * 0.55))) if x < 23 else 0
        for yy in range(12 - hw - 0, 12 + hw + 1):
            c.set(x, yy, 'm' if yy >= 12 else 'l')
    c.set(23, 12, 'w'); c.set(22, 11, 'w')
    c.line(16, 12, 22, 12, 'd')
    c.set(18 + (f % 2), 10, 'w')
    c.outline()
    return c.image()


def pj_ember(f):
    c = Cv(24, 24)
    cx, cy = 14, 12
    c.disc(cx, cy, 4, 'r')
    c.disc(cx + 0.5, cy, 3, 'o')
    c.disc(cx + 1, cy, 1.8, 'O')
    c.set(cx + 1, cy - 1, 'Y'); c.set(cx + 2, cy, 'Y')
    for k, (dx, dy) in enumerate([(-6, 1), (-9, -2), (-12, 2), (-8, 3), (-11, -1)]):   # chispas de la estela
        if (k + f) % 3 != 0:
            c.set(cx + dx, cy + dy, 'O' if (k + f) % 2 else 'R')
    c.line(cx - 5, cy, cx - 8, cy + (f % 2) - 0, 'o')
    for k in range(3):
        c.set(cx - 2 + k * 2, cy - 4 - ((f + k) % 2), 'o')
    c.outline()
    return c.image()


def pj_wisp(f):
    c = Cv(24, 24)
    cx, cy = 12, 13 + (1 if f in (1, 2) else 0)
    c.disc(cx, cy, 6, 't')
    c.disc(cx, cy - 1, 5, 'T')
    for dx in (-3, -2, 2, 3):              # cola que ondula
        c.set(cx + dx, cy + 6 + (f % 2), 't')
    c.set(cx - 1, cy + 7 + ((f + 1) % 2), 't'); c.set(cx + 1, cy + 7 + (f % 2), 't')
    c.set(cx, cy + 6, 't')
    c.rect(cx - 3, cy - 2, 2, 3, 'k'); c.rect(cx + 2, cy - 2, 2, 3, 'k')       # ojos
    c.set(cx - 3, cy - 2, 'w'); c.set(cx + 2, cy - 2, 'w')
    c.rect(cx - 1, cy + 2, 3, 1, 'k')
    c.set(cx - 7, cy - 6 + f, 'C'); c.set(cx + 7, cy - 4 - f, 'C')
    c.outline()
    return c.image()


def pj_spiritbolt(f):
    c = Cv(24, 24)
    cx, cy = 12, 12
    c.disc(cx, cy, 3, 't')
    c.disc(cx, cy, 2, 'T')
    c.set(cx, cy, 'w')
    for k in range(4):
        a = f * 0.8 + k * math.pi / 2
        c.set(cx + math.cos(a) * 5, cy + math.sin(a) * 5, 'C')
    c.line(cx - 4, cy, cx - 9, cy, 't')
    c.outline()
    return c.image()


PROJ = [('longarrow', pj_longarrow), ('chakram', pj_chakram), ('spear', pj_spear), ('ember', pj_ember), ('wisp', pj_wisp), ('spiritbolt', pj_spiritbolt)]
ICON_NAMES = ['w_knife', 'w_bolt', 'w_axe', 'w_orb', 'w_bow', 'w_chakram', 'w_wand', 'w_spear', 'w_ember', 'w_summon', 'swap', 'bag']


def main():
    prev = None
    if '--preview' in sys.argv:
        prev = sys.argv[sys.argv.index('--preview') + 1]
    ui = os.path.join(ROOT, 'ui')
    ij = json.load(open(os.path.join(ui, 'icons.json')))
    im = Image.open(os.path.join(ui, 'icons.png')).convert('RGBA')
    new_icons = [n for n in ICON_NAMES if n not in ij['names']]
    if new_icons:
        total = len(ij['names']) + len(new_icons)
        rows = (total + ij['cols'] - 1) // ij['cols']
        if rows * 16 > im.height:
            big = Image.new('RGBA', (im.width, rows * 16), (0, 0, 0, 0))
            big.paste(im, (0, 0))
            im = big
        for n in new_icons:
            i = len(ij['names'])
            ij['names'].append(n)
            im.paste(build_icon(n), ((i % ij['cols']) * 16, (i // ij['cols']) * 16))
        im.save(os.path.join(ui, 'icons.png'))
        json.dump(ij, open(os.path.join(ui, 'icons.json'), 'w'), ensure_ascii=False)
    pj = json.load(open(os.path.join(ROOT, 'fx', 'fx_proj.json')))
    pim = Image.open(os.path.join(ROOT, 'fx', 'fx_proj.png')).convert('RGBA')
    new_pj = [(n, f) for n, f in PROJ if n not in pj['anims']]
    if new_pj:
        base_rows = max(a['row'] for a in pj['anims'].values()) + 1
        big = Image.new('RGBA', (pim.width, (base_rows + len(new_pj)) * 24), (0, 0, 0, 0))
        big.paste(pim, (0, 0))
        for k, (n, f) in enumerate(new_pj):
            r = base_rows + k
            pj['anims'][n] = {'row': r, 'n': 4, 'fps': 16, 'loop': True}
            for fr in range(4):
                big.paste(f(fr), (fr * 24, r * 24))
        big.save(os.path.join(ROOT, 'fx', 'fx_proj.png'))
        json.dump(pj, open(os.path.join(ROOT, 'fx', 'fx_proj.json'), 'w'), indent=1)
    if prev:
        W = 16 * 12 + 24 * 4 * 6
        sheet = Image.new('RGBA', (16 * 12 * 1, 1), (0, 0, 0, 0))
        S = 8
        out = Image.new('RGBA', (max(16 * 12 * S // 2, 24 * 4 * 4), (16 * S // 2) + 24 * 4 * 6 + 20), (40, 40, 48, 255))
        for k, n in enumerate(ICON_NAMES):
            ic = build_icon(n).resize((16 * 5, 16 * 5), Image.NEAREST)
            out.alpha_composite(ic, (k * 16 * 5 + 2, 4))
        for k, (n, f) in enumerate(PROJ):
            for fr in range(4):
                p = f(fr).resize((24 * 4, 24 * 4), Image.NEAREST)
                out.alpha_composite(p, (fr * 24 * 4 + (k % 2) * 24 * 4 * 4, 16 * 5 + 10 + (k // 2) * 24 * 4))
        out.save(prev)


if __name__ == '__main__':
    main()
