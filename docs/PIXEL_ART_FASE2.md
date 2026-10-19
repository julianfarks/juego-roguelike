# Pixel art, fase 2 (pulido visual)

Herramienta: `python3 tools/art/polish.py [--from-y=N] archivo.png ...` (idempotente; marca el PNG con `polish=2`).

- Conserva: alfa (silueta, cajas, anclas) idéntico, número y orden de fotogramas, JSON, tiempos, smear/impact frames, anims AFK, posiciones de la mano.
- Añade, por reglas de 1 px sin desenfoque: luz arriba-izquierda (bandas de 2 px, hacia cálido), sombra de forma abajo-derecha (hacia frío) y contorno selectivo (el casi negro toma un tinte oscuro del relleno). Solo en zonas planas; se omiten emisivos y semitransparentes. Mismos colores de origen → mismos de salida.
- Aplicado a: `pl_*`, `plx_*`, `en_*`, `bs_*`, `ev_*`, `ops_*`, `pick_*`, `cmp_*`, `wpn_hold.png`, y decorados (filas ≥64) de `tiles_*.png`. No tocados: retratos, UI, fondos, bloques de tiles (se repiten: evitar costuras), geometría.
- Pruebas: `tools/tests/anim_sheets_check.py` (siluetas idénticas, cajas, smear con paleta derivada), `anim_test.sh`, suites de regresión headless.
- Límites: es un pulido automático, no redibujo a mano de rostros/armaduras; el cambio es sutil-moderado. Para rehacer: restaurar los PNG desde git y volver a ejecutar. No se validó en Android/Windows reales ni se capturó en partida.
