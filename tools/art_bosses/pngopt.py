import zlib, struct
import numpy as np


def _chunk(t, d):
    c = struct.pack('>I', len(d)) + t + d
    return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)


def encode_rgba(arr, level=9, strategy=zlib.Z_FILTERED):
    """PNG RGBA con filtro adaptativo por fila (minima suma de abs) y zlib Z_FILTERED."""
    h, w, _ = arr.shape
    a = arr.astype(np.int16)
    bpp = 4
    rows = arr.reshape(h, w * 4)
    out = bytearray()
    prev = np.zeros(w * 4, np.uint8)
    for y in range(h):
        cur = rows[y]
        cand = []
        left = np.concatenate([np.zeros(bpp, np.uint8), cur[:-bpp]])
        upleft = np.concatenate([np.zeros(bpp, np.uint8), prev[:-bpp]])
        f0 = cur
        f1 = (cur.astype(np.int16) - left).astype(np.uint8)
        f2 = (cur.astype(np.int16) - prev).astype(np.uint8)
        f3 = (cur.astype(np.int16) - ((left.astype(np.int16) + prev.astype(np.int16)) >> 1)).astype(np.uint8)
        p = left.astype(np.int16) + prev.astype(np.int16) - upleft.astype(np.int16)
        pa = np.abs(p - left); pb = np.abs(p - prev); pc = np.abs(p - upleft)
        pr = np.where((pa <= pb) & (pa <= pc), left, np.where(pb <= pc, prev, upleft))
        f4 = (cur.astype(np.int16) - pr.astype(np.int16)).astype(np.uint8)
        best = None
        for t, f in enumerate((f0, f1, f2, f3, f4)):
            sc = np.minimum(f.astype(np.int16), 256 - f.astype(np.int16)).sum() if t else np.minimum(f.astype(np.int16), 256 - f.astype(np.int16)).sum()
            if best is None or sc < best[0]:
                best = (sc, t, f)
        out.append(best[1]); out += best[2].tobytes()
        prev = cur
    co = zlib.compressobj(level, zlib.DEFLATED, 15, 9, strategy)
    z = co.compress(bytes(out)) + co.flush()
    return b'\x89PNG\r\n\x1a\n' + _chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)) + _chunk(b'IDAT', z) + _chunk(b'IEND', b'')
