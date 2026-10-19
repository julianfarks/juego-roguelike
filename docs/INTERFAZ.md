# Actualización de interfaz y controles

## Selección directa de armas
- Desaparece el botón celeste de cambio de arma (`B_SWAP`) y el botón táctil de disparo rápido de la secundaria (`B_SEC`, sin tecla por defecto táctil).
- Dos espacios **reales** (`Input.B_WMAIN`, `Input.B_WSEC`, radio 17 = 34 de diámetro) abajo al centro. Se dibujan en `ArsenalUI.slots` exactamente donde reciben el toque; el arma activa va más grande, con barra dorada y munición visible.
- `Arsenal.select(lv, p, secundaria)` solo cambia qué arma usa el botón de Ataque: no dispara, no gasta munición, no toca cooldowns; si ya está elegida no hace nada (ni animación ni sonido). Sin secundaria equipada, elegirla avisa sin cambiar nada.
- PC: teclas configurables (por defecto `R` principal / `T` secundaria) y **clic** sobre los espacios; las teclas se muestran sobre cada espacio. Mando: `RS→` / `RS←` configurables.
- Los dos botones nuevos aparecen en *Controles* (teclado/mando) y en el editor táctil (con tamaño/posición personalizables). Partidas antiguas: arrays de teclas/botones con crecimiento seguro; si una tecla ya estaba usada no se pisa.

## Botón contextual de interacción (`ContextBtn`)
- Sustituye al texto «Rezar» + llave diminuta. Panel oscuro con borde que late, icono del objeto (altar, cofre, tienda, forja, puerta, fuente, arma…), texto grande en mayúsculas (REZAR, ABRIR, COMERCIAR, ENTRAR, BEBER, FORJAR, RECOGER…) y flecha de toque (táctil). PC: etiqueta con la tecla realmente asignada; mando: su botón.
- Usa `RunScreen.interact()` y `hintFor(...)` existentes: no inventa acciones y respeta costes y condiciones (el objeto sigue decidiendo qué abre; los usados/bloqueados no lo muestran).
- Posición calculada cada fotograma: centro inferior; evita los botones tactiles visibles, los espacios de arma, el joystick activo, la vida y **al personaje** (candidatas: bajo los pies → zona inferior habitual → sobre la cabeza). Aparece con una animación corta y desaparece al salir del rango.
- Un toque/clic = una interacción (enfriamiento de 0,35 s); el toque sobre el botón no llega a los controles de combate (no ataca ni esquiva) y atacar cerca de un objeto no interactúa.

## Pausa
Quitados «Inventario» y «Bendiciones y sinergias» (siguen en el inventario: tecla `Tab`, bolsa táctil, `RS↑`). Una sola columna de botones alineada (Continuar, Guardar partida, Música, Sonidos, Vibración / Pantalla completa, Efectos, Abandonar) y a la derecha el resumen agrupado en estadísticas, equipo y bendiciones, con recorte de textos largos.

## Sinergias ocultas
Las 20 familias y sus efectos siguen funcionando. Ya no se muestra «Sinergia activada», ni nombres durante el combate, ni la pista «Sinergia x/y» en las cartas de bendición, ni el estado de sinergias en el detalle del inventario (`BlessEffects.synergyFound/Activated` son silenciosas). La lista de bendiciones activas con pestaña de sinergias dejó de ser accesible desde la pausa.

## Pruebas
`tools/tests/ui_test.sh` (banco headless; **no** es un Android ni un Windows real): 80+ comprobaciones por ejecución × táctil y PC × 480/568/640 × 270/288/320 de alto × 4 idiomas.
