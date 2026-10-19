# Tutorial inicial de controles

## Qué se corrigió

**Causa de las reapariciones.** El tutorial se decidía en `RunScreen.loadRoom` con la condición «sala de combate número 0 y `!Save.S.tutorialDone`». Esa marca solo se ponía a `true` en `endRun` (al morir o ganar la partida entera), y nadie la guardaba al ver o cerrar el tutorial. Como cada bioma empieza en la sala 0, el mensaje volvía a salir en **cada bioma nuevo, tras cada jefe**, y también si el jugador salía al menú a mitad de partida. El texto se dibujaba además en coordenadas del mundo (`room.spawnX + 40`), centrado en el jugador: por eso se cortaba por el borde izquierdo.

**Fuente única de verdad.** `Save.S.tutMask` (bits de `Tutorial`: `CONTROLS=1`, `PORTAL=2`). Se guarda en el perfil (`tuts` en el JSON del guardado) y se escribe en cuanto el jugador:
- cierra el panel (botón «Entendido», Intro, o mando: RS abajo),
- completa los tres pasos,
- lo tiene visible 3 s,
- sale de la sala, o
- termina la partida.

La entrada exige además «primera mazmorra del perfil» (`stage 0`, un solo bioma visitado, sin jefes derrotados, no infinito), pero la marca guardada es siempre la que manda.

**Migración.** Los guardados antiguos no tienen `tuts`: se hace una copia (`save_bak_tuts`) y se deduce — `tut=true`, o con partidas jugadas, cuentan como visto; un jugador sin partidas lo verá una vez. El campo antiguo `tut` se sigue escribiendo.

**Perfil nuevo.** `Save.reset()` (reiniciar progreso) crea un `Save` limpio → el tutorial vuelve a aparecer en su primera mazmorra.

## Diseño
- Panel propio (`Tutorial.java`), un paso cada vez: MOVIMIENTO → ACCIONES → ESQUIVA, avanza al hacer la acción.
- Iconos reales: tactil = los mismos botones redondos; PC = teclas asignadas; mando = botones asignados.
- Tactil: aro pulsante sobre el control que toca usar (joystick / salto+ataque / rodar).
- Posición calculada en cada fotograma: entre la barra de vida y los botones/pausa visibles (incluida la posición personalizada), nunca fuera de pantalla. No pausa el juego.
- El tutorial de portales del santuario tiene su propio bit (`PORTAL`).

## Pruebas
`tools/tests/tutorial_test.sh` (banco headless; NO es un Android ni un Windows real): casos 1–10 de lógica + escenas táctil/teclado/mando × 480/640 × 4 idiomas (dentro de pantalla, sin pisar vida ni botones, texto sin cortar, 1 dibujo por fotograma, botón responde al toque).
