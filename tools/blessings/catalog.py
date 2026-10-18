"""Carga el catalogo completo (A-J + sinergias) ya ajustado."""
import cat_a, cat_b, cat_c, cat_d, cat_e, cat_f, cat_g, cat_h, cat_i, cat_j, cat_syn, tune
from bl import *

tune.apply()
ORDER = LEGACY + [e['key'] for e in ENTRIES]       # id = indice
ID = {k: i for i, k in enumerate(ORDER)}
assert len(ORDER) == 200 and len(set(ORDER)) == 200
