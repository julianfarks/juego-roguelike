# Actualización: interfaz, cofres y rodada por huecos

Todas las pruebas son del **banco headless** (no Android ni Windows reales).

## Textos y paneles
- Detector `TextAudit` (`BOT_TEXTAUDIT=1`): marca texto fuera de pantalla, fuera de su panel/botón o pisado por otro texto.
- Corregido: tienda (alturas calculadas, precio en la fila del nombre), cofres/altar (ancho de tarjeta según opciones, nombres con salto de línea), eventos, fichas de armas (límite de altura), inventario, leyendas de comparación y avisos flotantes largos (ahora se ajustan al borde de la pantalla).
- Comprobado con las 4 lenguas y de 480x270 a 640x320 (`ui_test`).

## Cofres
- Causa: los cofres de fin de ronda se colocaban en `exitX - 70 - i*38` sin mirar el terreno (pozos, repisas, pilares, pinchos).
- `ChestSpot`: exige suelo firme bajo todo el ancho, 2 baldosas libres encima, sin pinchos al lado, un lado accesible, dentro de la sala y sin solaparse. Busca el punto válido más cercano; último recurso: punto firme del jugador (nunca se elimina la recompensa). Los cofres ya generados mal (tesoro/secretos) se reubican al cargar la sala. `Level.rewarded` evita duplicados.
- Fin de ronda: flecha dorada animada sobre cada cofre de recompensa (reutiliza brillo y partículas existentes).

## Rodada por huecos de 1 baldosa
- Sin botón nuevo: al rodar, la caja contra el **escenario** baja a 14 px (`Ent.colH()`); el daño y los golpes siguen usando `bh`, así que no se esquiva nada nuevo. Velocidad, duración, coste y enfriamiento no cambian.
- Al terminar, solo se levanta si hay sitio (`Level.boxFree`); si no, sigue encogido (pose de rodada) y puede caminar hasta salir. Nunca queda dentro de un bloque.

## Pruebas (`tools/tests/mobility_test.sh`)
- Cofres: 2268 salas generadas; colocación antigua inválida en 468 de 6804; nueva 0.
- Rodada: 9 comprobaciones (espacio abierto, hueco corto, hueco largo bajo techo + salida andando, pared completa, hueco de 2 sin rodar, hueco de 1 sin rodar no pasa, borde/foso, pinchos) y 0 frames con el jugador dentro de un bloque.
- El control táctil de rodada usa el mismo `B_ROLL` que el teclado; no se probó en dispositivo real.
