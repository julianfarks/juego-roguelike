"""Mini-motor de pixel art para el prototipo 3/4 del Paladin (EXPERIMENTAL, aislado del juego).

NO es dibujo a mano: es una lista de formas con vertices colocados a mano (en coordenadas de pixel) que este
motor rasteriza SIN antialiasing y sombrea por bandas de color (sin desenfoque ni interpolacion). Cada pieza
se guarda ademas como capa PNG independiente para poder editarla a mano en cualquier editor de pixel art.
"""
import math
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

W = H = 192
RAMPS = {
    'gold':    ['#4E300E', '#8A5A1A', '#C98F2A', '#EDB84A', '#FFE9A0'],
    'steel':   ['#363E52', '#656F8A', '#A3ADC3', '#D4DBE8', '#FFFFFF'],
    'blue':    ['#0E1740', '#1A2C72', '#2A47A0', '#4C6FD0', '#93B2F2'],
    'red':     ['#44101C', '#7A1B2C', '#B52D40', '#E0505F', '#FF9FA8'],
    'leather': ['#241610', '#46291A', '#6B452C', '#8E6240', '#B88C63'],
    'dark':    ['#0C0916', '#181223', '#272038', '#3A3158', '#574A7E'],
    'white':   ['#5F6A86', '#98A3BC', '#CDD5E6', '#EEF2FA', '#FFFFFF'],
}
OUTLINE = '#09060F'


def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def smooth(pts, n=6, closed=True):
    """Catmull-Rom: redondea una lista de vertices (formas organicas) sin interpolar color."""
    P = list(pts)
    m = len(P)
    out = []
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        p0, p1, p2, p3 = P[(i - 1) % m], P[i], P[(i + 1) % m], P[(i + 2) % m]
        if not closed:
            p0 = P[max(i - 1, 0)]; p3 = P[min(i + 2, m - 1)]
        for s in range(n):
            t = s / n
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t +
                                    (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
    return out


class Lienzo:
    def __init__(self):
        self.capas = []                       # (nombre, RGBA array)
        self.comp = np.zeros((H, W, 4), np.uint8)

    # ------------------------------------------------------------------ raster
    @staticmethod
    def mask(pts):
        im = Image.new('L', (W, H), 0)
        ImageDraw.Draw(im).polygon([(float(x), float(y)) for x, y in pts], fill=255)   # sin antialiasing
        return np.array(im) > 0

    @staticmethod
    def shift(m, dx, dy):
        r = np.zeros_like(m)
        ys = slice(max(dy, 0), H + min(dy, 0)); yd = slice(max(-dy, 0), H + min(-dy, 0))
        xs = slice(max(dx, 0), W + min(dx, 0)); xd = slice(max(-dx, 0), W + min(-dx, 0))
        r[ys, xs] = m[yd, xd]
        return r

    def pieza(self, nombre, pts, rampa, modo='diag', rim=3, spec=True, luz=(0.35, 0.3), outline=True, sombra=1, clip=None, tono=0.0, sm=None):
        """pts: vertices (x,y). modo: diag | cylx | cyly | round. rim: ancho del filo de luz (px). tono: desplaza el tono medio."""
        if sm:
            pts = smooth(pts, sm)
        m = self.mask(pts)
        if clip is not None:
            m &= clip
        if not m.any():
            return m
        ys, xs = np.nonzero(m)
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        w, h = max(x1 - x0, 1), max(y1 - y0, 1)
        X, Y = np.meshgrid(np.arange(W), np.arange(H))
        if modo == 'diag':
            t = (((X - x0) / w) + ((Y - y0) / h)) / 2
        elif modo == 'cylx':
            t = (X - x0) / w
        elif modo == 'cyly':
            t = (Y - y0) / h
        else:
            cx, cy = x0 + luz[0] * w, y0 + luz[1] * h
            t = np.hypot((X - cx) / w, (Y - cy) / h) / 0.72
        t = t - tono
        idx = np.where(t < 0.18, 3, np.where(t < 0.48, 2, np.where(t < 0.80, 1, 0)))
        lit = m & ~self.shift(m, rim, rim) if rim else np.zeros_like(m)           # borde que mira arriba-izquierda
        lit |= m & ~self.shift(m, 1, 0) | m & ~self.shift(m, 0, 1)
        shd = m & ~self.shift(m, -sombra, -sombra) if sombra else np.zeros_like(m)  # borde que mira abajo-derecha
        idx = np.where(lit & m, np.minimum(idx + 1, 4 if spec else 3), idx)
        idx = np.where(shd & ~lit, np.maximum(idx - 1, 0), idx)
        rp = [hexrgb(c) for c in RAMPS[rampa]]
        capa = np.zeros((H, W, 4), np.uint8)
        if outline:
            ring = ndimage.binary_dilation(m, structure=np.ones((3, 3), bool)) & ~m
            capa[ring] = hexrgb(OUTLINE) + (255,)
        for i in range(5):
            capa[m & (idx == i)] = rp[i] + (255,)
        self._poner(nombre, capa)
        return m

    def forma(self, nombre, pts, color, outline=False, sm=None):
        """relleno plano de un color (detalles: gemas, remaches, cintas)."""
        if sm:
            pts = smooth(pts, sm)
        m = self.mask(pts)
        capa = np.zeros((H, W, 4), np.uint8)
        if outline:
            ring = ndimage.binary_dilation(m, structure=np.ones((3, 3), bool)) & ~m
            capa[ring] = hexrgb(OUTLINE) + (255,)
        capa[m] = (hexrgb(color) if isinstance(color, str) else color) + (255,)
        self._poner(nombre, capa)
        return m

    def linea(self, nombre, pts, color, ancho=1):
        im = Image.new('L', (W, H), 0)
        d = ImageDraw.Draw(im)
        d.line([(float(x), float(y)) for x, y in pts], fill=255, width=ancho)
        m = np.array(im) > 0
        capa = np.zeros((H, W, 4), np.uint8)
        capa[m] = (hexrgb(color) if isinstance(color, str) else color) + (255,)
        self._poner(nombre, capa)
        return m

    def pix(self, nombre, lista, color):
        capa = np.zeros((H, W, 4), np.uint8)
        c = hexrgb(color) + (255,)
        for x, y in lista:
            if 0 <= x < W and 0 <= y < H:
                capa[int(y), int(x)] = c
        self._poner(nombre, capa)

    def _poner(self, nombre, capa):
        self.capas.append((nombre, capa))
        a = capa[:, :, 3] > 0
        self.comp[a] = capa[a]

    def guardar(self, ruta, carpeta_capas=None):
        Image.fromarray(self.comp, 'RGBA').save(ruta)
        if carpeta_capas:
            import os
            os.makedirs(carpeta_capas, exist_ok=True)
            for i, (n, c) in enumerate(self.capas):
                Image.fromarray(c, 'RGBA').save(os.path.join(carpeta_capas, '%02d_%s.png' % (i, n)))
