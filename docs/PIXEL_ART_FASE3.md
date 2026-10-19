# Pixel art, fase 3 (rediseño real, piloto: Paladín del Alba)

Cadena reproducible (comprobada: reproduce las hojas anteriores con 0 px de diferencia):
`python3 tools/art_players/build_all.py paladin --nopreview` → `python3 tools/art/make_smear.py` → `python3 tools/art/make_unarmed.py --only paladin` → `python3 tools/art/polish.py pl_paladin.png plx_paladin.png splash_paladin.png`.

Rediseño en `tools/art_players/cls_paladin.py` (dibujo vectorial por código sobre el rig, no a mano píxel a píxel): yelmo con cresta, visor en T con ojo luminoso, barra nasal, guardas de mejilla y babera, remache; cinturón con hebilla y faldones; hombrera en capas con remache; guarda de espada alada con gema carmesí. Todas las poses se regeneran con el mismo esqueleto: JSON (fotogramas, tiempos, cajas, anclaje de mano) idéntico.

Pruebas: `anim_sheets_check.py` (siluetas con variación ≤12 % por fotograma, pies/anclas estables), anim_test, arsenal, combate, HUD, UI; capturas reales del banco headless (preparación y partida). Antes/después: `docs/capturas_arte/paladin_fase3_antes_arriba_despues_abajo.png`.

Limitación honesta: la mejora es visible pero moderada; con cabezas de ~8 px no cabe un rostro detallado. No hay herramienta de dibujo manual: el rediseño es código. Quedan sin rediseñar las otras 9 clases, enemigos, jefes, armas secundarias y efectos.
