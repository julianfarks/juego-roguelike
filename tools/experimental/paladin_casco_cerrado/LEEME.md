# Paladín con casco cerrado — prueba EXPERIMENTAL (no usada por el juego)
- Base: el Paladín actual del juego (v3), misma escala y celda (64x48), mismo pipeline (render + pulido de fase 2).
- Único cambio: yelmo cerrado (visera con ranura de ojos y rejilla vertical, proa, nuca acorazada en lugar del pelo). Pluma, capa, escudo, espada, peto, hombreras, piernas y paleta sin tocar.
- Código: `tools/art_players/exp_paladin_casco.py` (copia de `cls_paladin.py` con el cambio) y `exp_paladin_casco_render.py`.
- Resultados: `comparacion_actual_izq_cerrado_der.png` (idle, idle2, run, ataque 1; x8), `comparacion_escala_juego_x3.png`, y hojas `casco_cerrado_{idle,run,attack1}.png` (solo muestra, sin JSON).
- Regenerar: `python3 tools/art_players/exp_paladin_casco_render.py`.
