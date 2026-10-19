#!/usr/bin/env python3
"""
Pulido pixel-art de las hojas horneadas (fase 2 visual).

Principios (todo conserva silueta, fotogramas, tiempos y anclas):
  * El canal alfa NO se toca (la silueta, cajas y anclas quedan identicas); solo cambia el RGB de pixeles opacos.
  * Sin desenfoque ni filtros: reglas por vecindad de 1 px con rampas de color que cambian de tono
    (luces hacia calido, sombras hacia frio) como en el pixel art hecho a mano.
  * Luz desde arriba-izquierda: filo de luz en bordes que miran hacia arriba/izquierda, sombra de forma
    en los que miran hacia abajo/derecha, y contorno selectivo (el contorno casi negro toma un tinte oscuro del relleno vecino).
  * Solo en zonas planas (un pixel con vecino del mismo color), para no romper tramas ni detalles dibujados.
  * Se omiten los emisivos (llamas, brillos, ojos) y los pixeles semitransparentes.
  * Los mismos colores de origen dan siempre los mismos colores de salida (paleta coherente entre fotogramas).
  * Idempotente: marca el PNG con 'polish' y no vuelve a procesarlo. Para rehacer, restaurar el original desde git.

Uso: python3 tools/art/polish.py [--check] [--preview] archivo.png ...
"""
import sys, os, colorsys, json
import numpy as np
from PIL import Image, PngImagePlugin

MARK = "polish"
VER = "2"

def rgb2hls(c):
    return colorsys.rgb_to_hls(c[0] / 255.0, c[1] / 255.0, c[2] / 255.0)

def hls2rgb(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h % 1.0, min(1, max(0, l)), min(1, max(0, s)))
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))

def hue_toward(h, target, k):
    d = ((target - h + 0.5) % 1.0) - 0.5
    return (h + d * k) % 1.0

WARM, COOL = 0.12, 0.68          # amarillo-anaranjado / azul-violeta

def lighten(c, amt=0.10):
    h, l, s = rgb2hls(c)
    h = hue_toward(h, WARM, 0.10) if s > 0.08 else h
    return hls2rgb(h, l + amt * (1.0 - l * 0.6), s * 1.04 + 0.01)

def darken(c, amt=0.10):
    h, l, s = rgb2hls(c)
    h = hue_toward(h, COOL, 0.16) if s > 0.05 else hue_toward(h, COOL, 0.5)
    return hls2rgb(h, l - amt * (0.5 + l), min(1.0, s * 1.05 + (0.04 if s < 0.2 else 0.0)))

def tint_outline(orig, fill):
    """Contorno casi negro -> tinte oscuro del relleno vecino (selout), manteniendo la luminosidad baja."""
    h, l, s = rgb2hls(fill)
    ol = rgb2hls(orig)[1]
    nl = min(0.20, max(ol, 0.08 + 0.12 * l))
    ns = min(0.55, 0.18 + s * 0.55)
    nh = hue_toward(h, COOL, 0.12)
    return hls2rgb(nh, nl, ns)

def polish_array(a):
    """a: HxWx4 uint8. Devuelve copia con RGB pulido; el alfa es identico."""
    H, W = a.shape[:2]
    out = a.copy()
    alpha = a[:, :, 3]
    solid = alpha == 255
    anyop = alpha > 0
    rgb = a[:, :, :3].astype(int)
    lum = (0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]) / 255.0
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0.0)

    # vecino en direccion (dy,dx): valor de arr en (y+dy, x+dx)
    def nb(arr, dy, dx, fill):
        return _nb(arr, dy, dx, fill, H, W)

    emissive = (lum > 0.74) | ((sat > 0.55) & (lum > 0.50)) | (~solid & anyop)
    dark = lum < 0.115
    up_t = ~nb(anyop, -1, 0, False); dn_t = ~nb(anyop, 1, 0, False)
    lf_t = ~nb(anyop, 0, -1, False); rt_t = ~nb(anyop, 0, 1, False)
    edge = solid & (up_t | dn_t | lf_t | rt_t)
    outline = edge & dark
    # pixel "relleno": opaco, no contorno
    fillm = solid & ~outline
    def is_out(dy, dx):
        o = nb(outline, dy, dx, False); t = ~nb(anyop, dy, dx, False)
        return o | t
    # zona plana: algun vecino 4-conexo con el mismo color exacto
    same = np.zeros((H, W), bool)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        same |= (nb(rgb[:, :, 0], dy, dx, -1) == rgb[:, :, 0]) & (nb(rgb[:, :, 1], dy, dx, -1) == rgb[:, :, 1]) & (nb(rgb[:, :, 2], dy, dx, -1) == rgb[:, :, 2])
    ok = fillm & ~emissive & same & (lum > 0.13)
    # distancia (1..3) hacia arriba/izquierda y hacia abajo/derecha hasta contorno o vacio: da el volumen (bandas de luz y sombra de 2 px)
    def dist(dirs):
        best = np.full((H, W), 9)
        for dy, dx in dirs:
            d = np.full((H, W), 9)
            for k in (3, 2, 1):
                hit = is_out(dy * k, dx * k)
                d = np.where(hit, k, d)
            best = np.minimum(best, d)
        return best
    dUL = dist(((-1, 0), (0, -1), (-1, -1)))
    dDR = dist(((1, 0), (0, 1), (1, 1)))
    band1_l = ok & (dUL == 1) & (dDR > 2)
    band2_l = ok & (dUL == 2) & (dDR > 3)
    band1_d = ok & (dDR == 1) & (dUL > 2) & ~band1_l
    band2_d = ok & (dDR == 2) & (dUL > 3) & ~band1_d & ~band2_l
    top_edge = band1_l; low_edge = band1_d
    top2 = band2_l; low2 = band2_d

    cacheL, cacheD, cacheO = {}, {}, {}
    ys, xs = np.nonzero(top_edge)
    for y, x in zip(ys, xs):
        c = tuple(int(v) for v in rgb[y, x])
        if c not in cacheL: cacheL[c] = lighten(c)
        out[y, x, :3] = cacheL[c]
    ys, xs = np.nonzero(low_edge)
    for y, x in zip(ys, xs):
        c = tuple(int(v) for v in rgb[y, x])
        if c not in cacheD: cacheD[c] = darken(c)
        out[y, x, :3] = cacheD[c]
    for mask, fn, amt, cache in ((top2, lighten, 0.04, {}), (low2, darken, 0.04, {})):
        ys, xs = np.nonzero(mask)
        for y, x in zip(ys, xs):
            c = tuple(int(v) for v in rgb[y, x])
            if c not in cache: cache[c] = fn(c, amt)
            out[y, x, :3] = cache[c]
    # contorno selectivo: tinte segun la media de los vecinos de relleno (8-conexo)
    ys, xs = np.nonzero(outline)
    for y, x in zip(ys, xs):
        acc = []
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0: continue
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and fillm[yy, xx] and lum[yy, xx] > 0.13 and not emissive[yy, xx]:
                    acc.append(rgb[yy, xx])
        if not acc: continue
        f = tuple(int(v) for v in np.mean(acc, axis=0))
        key = (tuple(int(v) for v in rgb[y, x]), f[0] // 12, f[1] // 12, f[2] // 12)
        if key not in cacheO: cacheO[key] = tint_outline(tuple(int(v) for v in rgb[y, x]), f)
        out[y, x, :3] = cacheO[key]
    assert np.array_equal(out[:, :, 3], alpha)
    return out

def _nb(arr, dy, dx, fill, H, W):
    r = np.full(arr.shape, fill, dtype=arr.dtype)
    y0, y1 = max(0, -dy), H - max(0, dy)
    x0, x1 = max(0, -dx), W - max(0, dx)
    r[y0:y1, x0:x1] = arr[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
    return r

def process(path, write=True, from_y=0):
    """from_y > 0: solo se pule desde esa fila (hojas de tiles: los bloques que se repiten no se tocan para no crear costuras)."""
    im = Image.open(path)
    if im.info.get(MARK) == VER:
        return None
    a = np.array(im.convert("RGBA"))
    out = a.copy()
    out[from_y:] = polish_array(a[from_y:])
    changed = int((out[:, :, :3] != a[:, :, :3]).any(axis=2).sum())
    if write:
        info = PngImagePlugin.PngInfo()
        info.add_text(MARK, VER)
        Image.fromarray(out, "RGBA").save(path, pnginfo=info, optimize=True)
    return changed

def main(argv):
    fy = 0
    for x in argv:
        if x.startswith("--from-y="): fy = int(x.split("=")[1])
    args = [x for x in argv if not x.startswith("--")]
    for p in args:
        n = process(p, write="--check" not in argv, from_y=fy)
        print(("omitido (ya pulido) " if n is None else "%6d px  " % n) + p)

if __name__ == "__main__":
    main(sys.argv[1:])
