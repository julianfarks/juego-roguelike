# Prueba experimental: Paladin del Alba a 96x96 (NO usada por el juego)

- `paladin96_sheet.png` / `.json`: celdas de 96x96 (filas: idle 6, run 8, attack1 7, roll 8 fotogramas). Mismo rig y poses que el Paladin v3, renderizado vectorialmente a doble resolucion (sin interpolacion) con detalle extra: iris/pupila/parpado/ceja arqueada, remaches del yelmo y segmentos de cresta, peto en 3 placas con juntas y remaches, gorjal en anillos, hombrera de 3 laminas, brazal con bandas, nudillos, capa con 5 pliegues y forro, escudo con filo de luz, remaches y sol de 8 rayos, espada con filos, canal, punta y empunadura vendada.
- Generador aislado: `tools/art_players/exp96_paladin.py` (subclase de `cls_paladin.Paladin`; no modifica el generador actual).
- Comparaciones: `comparacion_ampliada_actual_izq_96_der.png` (actual a 2x NN = mismo tamano de personaje, vs 96x96, ambos x7) y `comparacion_escala_juego_actual_arriba_96_abajo.png` (sobre un fondo real de partida, ambos con el personaje del mismo tamano en pantalla: el actual se amplia 2x para igualar el tamano y el 96 se muestra nativo; luego ambos x3).
- Nota: las celdas 96x96 no incluyen smear/hurt/ult ni filas `_u/_s`; el aura/efectos de clase estan desactivados. Para integrar al juego habria que migrar celda, pivote, cajas, anclas de mano y todas las animaciones (no hecho).

## Version heroica (adulto, robusto)
- `paladin96_heroico_sheet.png/.json` (generador aislado `tools/art_players/exp96_paladin_v2.py`; el prototipo anterior `paladin96_sheet.png` se conserva para comparar).
- Cambios: cabeza algo menor (proporcion adulta), hombros mas anchos (sw 1,25 -> 1,6), torso y ropa un 18 % mas anchos, piernas, brazos, hombreras de 3 laminas y guanteletes mas gruesos, botas propias con puno dorado y puntera, postura mas erguida (inclinacion x0,55). Rostro: frente plana, mandibula ancha y cuadrada con sombra de barba, menton y pomulo marcados, ceja gruesa inclinada, ojo mas estrecho con parpado pesado, nariz con puente y fosa en sombra, patilla larga y mechones mas claros.
- Comparacion a igual tamano: `comparacion_prototipo_arriba_heroico_abajo.png` (idle, run, attack1, roll; x6).
- Limite conocido: en la pose de rodar el personaje queda recortado por el borde inferior de la celda 96x96 (igual en el prototipo anterior); habria que reajustar el origen de esa fila.

## Revisión "joven adulto, atlético" (v3)
- Generador: `tools/art_players/exp96_paladin_v3.py` -> `paladin96_joven_sheet.png/.json` (filas idle, run, attack1, roll).
- Cambios: cara lisa sin barba, mandíbula firme y limpia, cejas marcadas pero ligeras, ojo claro con brillo, flequillo y mechones castaños bajo el yelmo; torso con cintura más estrecha y hombros firmes (sin ensanchar extremidades); botas y guanteletes de tamaño original; postura más erguida.
- Comparación a la misma escala: `comparacion_prototipo_izq_joven_der.png` (izq. versión "heroica" anterior, der. nueva; arriba idle, abajo run).
- Paleta, capa, escudo, espada y penacho sin cambios. Prueba headless sobre el prototipo aislado; no se tocó el sprite del juego.
- Límites conocidos: fila roll recortada abajo, espada recortada a la derecha en ataque, sin smear/hurt/ult.

## Versión yelmo cerrado (v4)
- Generador: `tools/art_players/exp96_paladin_v4.py` -> `paladin96_cerrado_sheet.png/.json` (idle, run, attack1, roll).
- Casco completamente cerrado: bóveda con cresta, ceja y banda de visera, ranura de ojos oscura, barbote con arista y ventilas, remaches, joya lateral, pluma carmesí. No se ve piel, ojos, nariz, boca ni pelo.
- Comparación: `comparacion_joven_izq_cerrado_der.png` (idle).
- Pendiente: el resto de la armadura (peto, hombreras, brazales, rodilleras) sigue como en v3; falta elaborarla. Las animaciones funcionales y el sprite del juego no se tocan.
