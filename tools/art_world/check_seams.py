"""Verifica costuras entre variantes del relleno (mascara 15): diferencia en el borde vs. la del propio patron periodico."""
import numpy as np
from terrain import terrain_tile
from biomes import CFG, BIOMES
for b in BIOMES:
    T = {v: terrain_tile(CFG[b], 15, v)[..., :3].astype(float) for v in range(3)}
    def dh(a, c): return np.abs(T[a][:, 15] - T[c][:, 0]).mean()
    def dv(a, c): return np.abs(T[a][15] - T[c][0]).mean()
    selfh = np.mean([dh(v, v) for v in range(3)])
    selfv = np.mean([dv(v, v) for v in range(3)])
    worst_h = max(((dh(a, c), a, c) for a in range(3) for c in range(3) if a != c))
    worst_v = max(((dv(a, c), a, c) for a in range(3) for c in range(3) if a != c))
    print(f'{b:11s} auto-h={selfh:5.1f} cruz-h max={worst_h[0]:5.1f} {worst_h[1:]} | auto-v={selfv:5.1f} cruz-v max={worst_v[0]:5.1f} {worst_v[1:]}')
