# Migración artística por grupos (SwordsmanMagic: Eternal Abyss)

Referencia de calidad: Paladín del Alba con casco cerrado. Cada grupo se integra y se prueba antes del siguiente.

## Grupo 1 — Paladín del Alba (INTEGRADO)
- Cambio: yelmo cerrado (visera con ranura de ojos y rejilla vertical, proa, nuca acorazada). Resto del diseño v3 intacto.
- Generador: `tools/art_players/cls_paladin.py`. Cadena: `build_all.py paladin` -> `make_smear.py` -> `make_unarmed.py --only paladin` -> `polish.py`.
- Recursos regenerados: `pl_paladin.png`, `plx_paladin.png`, `splash_paladin.png`, `portrait_paladin.png`. `pl_paladin.json` sin cambios (anclajes, cajas y tiempos iguales).
- Pruebas (headless, no Android/Windows reales): anim_sheets_check, anim_test (40/0), arsenal_test (254), combat_test, hud_test, ui_test: OK.
- Para revertir: restaurar esos 4 PNG y `cls_paladin.py` del commit anterior.

## Grupo 2 — Las otras 9 clases (INTEGRADO, un commit por clase)
Orden: shadow, flame, storm, frost, verdant, blood, earth, astral, steel. Solo cambia `draw`/`init_mats` en cada `cls_*.py` (Dims, cintas, animaciones y ataques intactos).
- Cada clase: placas/ropa con juntas y filos de luz, hombrera en laminas o charretera, yelmo/capucha/mascara con mas estructura, brazales, cinturon, y arma con guarda, bisel o abrazaderas propias de su tema.
- Cadena por clase: `tools/art_players/regen_class.sh <clase>` (build_all -> smear -> unarmed -> polish y restaura el JSON funcional). Comparacion: `tools/art_players/cmp_class.py <clase>` -> `docs/capturas_arte/<clase>_grupo2_*.png`.
- Los 10 `pl_*.json` son identicos al estado previo al grupo 2 (anclajes, cajas, tiempos). `anim_sheets_check` OK para las 10 clases.
- Limite honesto: son mejoras de acabado (estructura, materiales, filos de luz), no cambios de silueta. Los smear de shadow y steel salen algo mas apagados porque se derivan de la paleta del sprite.
- Revertir una clase: `git revert <commit de esa clase>`.
- Pruebas headless: anim_test 40/0, combat, hud, ui OK. arsenal_test intermitente: ver la seccion «arsenal_test» mas abajo (causa investigada con evidencia en la fase 3).

## Grupo 3 (enemigos y jefes): PILOTO, no completo
Evaluacion de los 51 disenos en `docs/EVALUACION_ENEMIGOS_FASE3.md`. Se rehicieron **de verdad 4 enemigos de 40 y 1 jefe de 11** (mas un detalle menor en el esqueleto, commit `880bb12`); 0 minibosses/elites propios. El resto sigue **pendiente**: la fase 3 NO esta completa.
- Cambios de silueta (un commit cada uno, revertibles con `git revert`):
  - `en_zombi` (encorvado, joroba con columna, brazos largos con garras, cabeza caida, harapos en vez de armadura) — `45afe1b`
  - `en_cubo_magma` (bloque de basalto con espinas, placa facial, juntas de lava) — `bcd4920`
  - `en_murcielago` (alas grandes de 4 dedos con membrana clara, orejas y colmillos) — `d270bf1`
  - `en_escudero_hueso` (escudo de torre grande, yelmo con cuernos y cresta) — `e78032c`
  - `bs_rey_exanime` (corona alta de espinas, collar de pinchos, hombreras mayores, espadon con guarda) — `0de0003`
- JSON funcional (celda, pivote, cuerpo, tiempos, `hit`/`box`) **identico** en los 5; `enemy_sheets_check` 51/51 OK. Para los 5 rediseñados el check tolera el cambio de silueta pero exige: mismo JSON y tamano de hoja, ningun fotograma vacio, pies sin mover y que no se recorte por el borde de la celda (el primer intento recorto zombi, escudero, murcielago y cubo; se corrigio acortando brazos/cuernos/alas, no relajando el check).
- Comparaciones a escala de juego (1 px de sprite = 1 px logico, fondo real del bioma, sin filtros): `docs/capturas_arte/escala_juego_*_1x.png` (la copia `_3x` es la misma imagen ampliada por vecino mas cercano solo para poder verla). Antes/despues por animaciones: `docs/capturas_arte/enemigos_*` y `jefe_rey_exanime_*`.
- Regenerar: enemigos `tools/art_enemies/regen_enemy.sh <nombre>`; jefe `python3 tools/art_bosses/run_one.py rey` + `tools/art/polish.py` + `git checkout` del JSON.
- Limites honestos: (1) a escala 1:1 la mejora es clara en silueta (zombi, escudero, cubo, murcielago) y moderada en el jefe; el cubo gana lectura de "bloque" pero pierde la cara legible que tenia. (2) El pipeline del jefe NO reproduce el PNG comprometido pixel a pixel (≈21.000 px de diferencia tras `polish` incluso sin tocar el codigo), asi que regenerar un jefe cambia tambien detalles que no se rediseñaron (efectos); el JSON si es identico. (3) Los humanoides pequeños comparten base (`humanoid.py`); cambiar su silueta exige piezas propias, como en el escudero.
- Pruebas automaticas (headless, NO Android/Windows reales): anim_sheets_check, enemy_sheets_check, anim_test 40/0, combat_test, hud_test, ui_test OK. Revision visual de animaciones solo por hojas de fotogramas y comparaciones; no se vio en el juego en marcha.

## arsenal_test intermitente (investigado con evidencia)
- No son los sprites: la prueba es logica (no carga imagenes) y el fallo se reproduce en la rama anterior a todos los cambios de arte de esta serie (`ba25e53`, 3/3 con la misma semilla). Causa comun: la partida usa `System.nanoTime()` como semilla (`RunScreen`), asi que la sala cambia en cada ejecucion y la prueba dependia de la sala. Gancho nuevo solo para el banco: `BOT_SEED=<n>` reproduce una sala; la prueba imprime `AT SEED`.
- Frecuencia medida antes de corregir: 11 fallos en 70 ejecuciones (≈16 %) + 2 en 70 (≈3 %) con solo el primer arreglo. Tres causas, cada una con evidencia (diagnosticos de `ArsenalProbe`, trazas y reproduccion con semilla fija):
  1. **Proyectil sobrante tras el ataque del Paladin (≈16 %)**: eran proyectiles propios (`holy`, abanico de `Skills.paladin(0)`; `crescent`, ondas de `Skills.paladin(1)` con `lv.later(0.48 s)`). El bot de pruebas a veces lanza una habilidad justo antes de ceder el control y su efecto cae en la primera comprobacion (pila: `Player.updateCast → castSkills → Skills.paladin` dentro del primer `tap`). Arreglo: `fr(180)` (3 s sin teclas) antes de empezar.
  2. **Jugador colocado sobre pinchos (≈1 %)**: `place()` no miraba peligros; el jugador se curaba/teletransportaba a la entrada (584 px) y el arma soltada quedaba lejos → 13 comprobaciones en cascada. Traza: `AT TRACE` mostro el salto y los tiles `3` (pinchos) bajo el jugador. Arreglo: `place()` descarta posiciones y pasillo con `hazardAt`.
  3. **Sala «completada» por la propia prueba (≈1 %)**: en la ultima seccion `reset()` deja la sala sin enemigos, la sala reparte cofres y con un 20 % un arma suelta (`RunScreen`, recompensa de ronda) y la comprobacion `weaponProps()==0` falla (diagnostico: `chest(Recompensa)` + `weapon` extra en la salida). Arreglo: `dummy(200)` como en las demas secciones.
- Ninguna comprobacion se relajo ni se filtro; los arreglos aislan el entorno. Tras ellos: 80 de 80 ejecuciones OK (254/254). Commit aparte, revertible.

## Pendiente
- Enemigos (36 sin tocar; 8 de ellos clase A: arana, arquero_hueso, cultista_sangre, hechicero_hielo, lancero_escarcha, saqueador, vindicador, clerigo_osario), minibosses/élites (`en_elites_a/b`) y 10 jefes (prioridad: guardian_eclipse, titan_tormenta).
