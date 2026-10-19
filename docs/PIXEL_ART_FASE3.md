# Pixel art, fase 3 (rediseño real, piloto: Paladín del Alba)

Cadena reproducible (comprobada: reproduce las hojas anteriores con 0 px de diferencia):
`python3 tools/art_players/build_all.py paladin --nopreview` -> `python3 tools/art/make_smear.py` -> `python3 tools/art/make_unarmed.py --only paladin` -> `python3 tools/art/polish.py pl_paladin.png plx_paladin.png splash_paladin.png`.

## Rediseño v2 (`tools/art_players/cls_paladin.py`, dibujo vectorial por código sobre el rig; no es dibujo a mano píxel a píxel)
Problema del piloto v1: todo era dorado sobre dorado (cara, brazos, torso) y la capa/escudo claros se confundían: poca separación de materiales. (Además el cinturón v1 estaba mal colocado a la altura del cuello; corregido.)
- Composición/materiales: armadura dorada solo en yelmo, peto, hombreras y brazales; **sayo azul marino** en brazos y piernas; **capa azul real**; **escudo con borde dorado, campo azul y sol**; tabardo blanco con banda azul y ribete dorado; guanteletes y botas de cuero; **pluma carmesí**.
- Cabeza algo mayor (radio 4,1 -> 4,7 px): yelmo abierto con cara visible (ojo, ceja, mandíbula), cabello castaño bajo el yelmo, cresta dorada, guarda de mejilla, barra nasal.
- Peto ahusado a la cintura con cinturón y hebilla, faldón trasero, emblema solar; hombrera en capas; guarda de espada alada.
- Todas las poses se regeneran con el mismo esqueleto: JSON (fotogramas, tiempos, cajas, anclaje de mano) idéntico al anterior.

## Tamaño visual
Pantalla de 1152x540 = interna 384x180 a x3; el personaje mide ~28 px de alto (84 px en pantalla). El límite no es la resolución sino la composición: con el mismo tamaño se logró más legibilidad con contraste de materiales y colores. No se cambió escala ni cámara.

## Pruebas (banco headless, no Android/Windows reales)
`anim_sheets_check.py` (siluetas, pies/anclas estables; variación admitida ≤12 % en clases rediseñadas), `anim_test`, `arsenal_test`, `combat_test`, `hud_test`, `ui_test`.
Capturas: `docs/capturas_arte/paladin_fase3_captura_partida_real.png` (partida real del banco), `paladin_fase3_escala_juego_antes_arriba_despues_abajo.png` (sprites antes/después a escala de juego sobre un fondo real: montaje, no captura viva), `paladin_fase3_antes_arriba_despues_abajo.png` (v1).

## Pendiente
Otras 9 clases, enemigos, jefes, armas secundarias y efectos no rediseñados.

## Revisión 2 (v3)
Cambios sobre v2, todo dentro de `cls_paladin.py` y regenerado en todas las poses (JSON idéntico):
- Cabeza (radio 5,0): cara con ojo (blanco + pupila), ceja, nariz que sobresale y boca; casquete con borde y sombra bajo el borde; barra nasal; cabello en nuca y patilla; guarda de mejilla.
- Armadura: sayo azul medio (se separa del fondo); peto en placas (cuerpo + faja) con juntas oscuras y reflejo central; cinturón con hebilla; hombrera en capas; brazales y guanteletes diferenciados.
- Capa con dos pliegues oscuros, un filo de luz y ribete dorado. Escudo: borde + reborde dorado, campo azul bipartido (luz/sombra) y sol de 8 rayos con disco. Espada: hoja con bisel y canal, guarda alada con remates y gema, empuñadura vendada, pomo.
- Comparación: `docs/capturas_arte/paladin_rev2_escala_juego_fase2_v2_v3.png` (3 filas, a escala de juego sobre fondo real) y `paladin_rev2_ampliado_fase2_v2_v3.png`.
