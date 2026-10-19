# Arsenal, armas secundarias e inventario

Sistema de **arma principal + una arma secundaria** con cambio en combate, armas en el suelo, cofres con comparación e **inventario completo** de la run. Se apoya en lo que ya existía (`Items.SEC_*`, `ChestLoot`, `Proj`, `RunSave`, overlays de `RunScreen`); no hay sistemas paralelos.

## Archivos
| Archivo | Qué hace |
|---|---|
| `core/Items.java` | Datos de las 10 armas secundarias (nombre, icono, rareza, daño, cadencia, alcance, efecto, descripción) y `useSecondary` |
| `core/Arsenal.java` | Disparo de las armas nuevas, cambio de arma, armas del suelo (soltar/recoger/mejorar), limpieza al salir de sala, comparación de estadísticas |
| `core/ArsenalUI.java` | Ranuras del HUD, tarjeta del suelo, ficha de arma con comparación |
| `core/Inventory.java` | Pantalla de inventario (overlay `OV_INV`) |
| `core/RunScreen.java` | Cofres con confirmación (`OV_WCMP`), integración del suelo/inventario/HUD |
| `core/RunSave.java` | Guardado de la run (v2, aditivo, con copia de seguridad de partidas antiguas) |
| `tools/gen_arsenal_art.py` | Generador idempotente del pixel art nuevo (12 iconos y 6 proyectiles) |
| `core/ArsenalProbe.java`, `tools/tests/arsenal_test.sh` | Pruebas automáticas (banco headless) |

## Reglas
- **Una** secundaria equipada como máximo. La principal es la de la clase.
- **Selección directa** (sin botón de cambio): dos espacios en el centro inferior de la pantalla, uno para la principal y otro para la secundaria. Tocar uno (o su tecla / botón de mando / clic en PC) lo deja seleccionado y el botón de **Ataque** ejecuta el arma seleccionada: principal (cuerpo a cuerpo de la clase) o secundaria (dispara). Seleccionar no es atacar; si ya está seleccionada, volver a tocarla no hace nada. El antiguo botón táctil de disparo rápido de la secundaria desapareció (su acción es seleccionar + atacar); la tecla `L` / botón de mando sigue funcionando si la tenías asignada.
- Cambiar tarda 0,25 s (enfriamiento) y no reinicia nada: no crea proyectiles, no gasta munición, no resetea cooldowns ni bendiciones, no duplica efectos. Seleccionar + atacar a la vez como máximo dispara una vez. Sin secundaria, elegirla no hace nada (avisa).
- Sin munición con la secundaria activa → vuelve sola a la principal.
- Daño/cadencia de la secundaria escalan con su **nivel** (`secLvl`, máx. 3); el nivel pertenece a la ranura, igual que antes.

## Armas secundarias
Cada una tiene sprite propio (icono + proyectil), animación, efecto de impacto y sonido de los recursos existentes. Las 4 primeras conservan exactamente su comportamiento anterior.

| # | Arma | Rareza | Daño | Cadencia | Alcance | Usos | Efecto |
|---|---|---|---|---|---|---|---|
| 1 | Cuchillos arrojadizos | Común | 0.65× · 3 proy. | 3.1/s | 26 casillas | 14 | 3 cuchillos por lanzamiento |
| 2 | Ballesta rúnica | Poco común | 2.1×  | 3.1/s | 47 casillas | 9 | Atraviesa 2 enemigos |
| 3 | Hacha arrojadiza | Rara | 2.4×  | 3.1/s | 21 casillas | 7 | Atraviesa 3 enemigos |
| 4 | Orbe arcano | Épica | 1.5×  | 3.1/s | 26 casillas | 10 | Persigue y explota |
| 5 | Arco de cazador | Poco común | 1.5×  | 2.4/s | 40 casillas | 16 | +90% de daño a máxima distancia |
| 6 | Chakram | Épica | 1.1×  | 1.8/s | 10 casillas | 12 | Vuelve al jugador (máx. 1 en vuelo) |
| 7 | Varita prismática | Rara | 1.2×  | 3.6/s | 25 casillas | 18 | Quema · congela · aturde (rota) |
| 8 | Lanza arrojadiza | Poco común | 2.6×  | 1.3/s | 38 casillas | 6 | Atraviesa 5 · +15% de daño por enemigo |
| 9 | Cañón de brasas | Rara | 0.7× · 3 proy. | 2.0/s | 8 casillas | 10 | Quema 2.5 s · 3 proyectiles |
| 10 | Cetro de invocación | Épica | 0.55×  | 1.0/s | 14 casillas | 5 | Hasta 2 espíritus · 10 s cada uno |

Comportamientos propios: el **arco** gana daño con la distancia; el **chakram** sale, regresa a la mano y solo puede haber uno en vuelo; la **varita** rota fuego → hielo → rayo; la **lanza** atraviesa 5 y gana daño por enemigo; el **cañón de brasas** lanza 3 brasas cortas que queman; el **cetro** invoca hasta 2 espíritus de 10 s (daño de acompañante).

## Armas en el suelo
- Se encuentran tras rondas (20 %, 50 % en mini-jefe) y al derrotar jefes (50 %), y se **sueltan al intercambiar**.
- Cerca del arma aparece la **tarjeta** (nombre, rareza, daño/cadencia/alcance con comparación `+ - =` contra la equipada, efecto y acción). Pasar por encima **no** recoge: hay que pulsar *Interactuar*.
- Sin secundaria → se equipa. Con otra → se intercambia y la anterior queda en el suelo, **en un punto seguro** (nunca pared, pinchos, fuera del escenario ni sobre otra arma), con su munición, bloqueada 0,7 s para que una pulsación no la recoja de vuelta.
- Misma arma → sube de nivel (no se duplica).
- Al salir de la sala, las que quedan en el suelo se marcan «dejada atrás» (aviso en pantalla y en el inventario). Dentro de la sala permanecen.

## Cofres
Las opciones de arma muestran icono, rareza, usos y descripción. Si ya llevas una secundaria distinta, al elegir se abre la **comparación** («Conservar la actual» / «Intercambiar»); rechazar vuelve a las 3 opciones sin perder ninguna. Con la misma arma, la compensación es una mejora de nivel (nunca se ofrece como arma «nueva»).

## Inventario
- **Abrir:** `Tab` (configurable), botón de bolsa (táctil, bajo Pausa), `RS↑` en mando, (ya no hay acceso desde la pausa). El juego queda en pausa y los controles de combate no actúan mientras se navega.
- **Categorías:** Armas (principal + secundarias obtenidas: equipada / en el suelo / dejada atrás) · Bendiciones (con nivel y sinergias) · Reliquias y especiales (reliquias de jefe, pactos, bendición inicial, compañero) · Objetos (escudo, granada, mejora especial, frascos).
- **Estados sin depender del color:** `E` equipada/en uso (`e` equipada pero en espera), `S` en el suelo, `D` dejada atrás, `!` nueva, `+n` nivel/mejora; la rareza se ve por color **y** símbolo (punto, dos puntos, rombo, estrella).
- **Orden:** rareza / nombre. **Filtro:** todas, nuevas, y cada rareza.
- **Panel de equipo** (principal + secundaria, la activa marcada «EN USO») y **panel de detalle** con comparación; botón «Usar esta arma» activa la secundaria.
- Muestra solo el estado **real de esta run** (`RunState`): no toca ni lee la colección permanente (bestiario, reliquias guardadas).
- «Nuevo» = obtenido y aún no inspeccionado (se quita tras mirarlo ~0,7 s).

## Controles
| Acción | Teclado | Mando | Táctil |
|---|---|---|---|
| Elegir arma principal | `R` | `RS→` | tocar el espacio izquierdo de armas |
| Elegir arma secundaria | `T` | `RS←` | tocar el espacio derecho de armas |
| Inventario | `Tab` | `RS↑` | bolsa bajo Pausa |
| Recoger / inspeccionar suelo y demás interacciones | `E` (Interactuar) | botón de Interactuar | botón contextual grande (ver `docs/INTERFAZ.md`) |
| Navegar inventario | flechas/WASD, `Q`/`E` categoría, `F` filtro, `O` orden, `Enter` acción, `Esc`/`Tab` cerrar | cruceta / stick, `LB`/`RB` categoría, `X` filtro, `Y` orden, `A` acción, `B` cerrar | tocar pestañas/celdas/botones |
Todo es reasignable en *Controles*; si una tecla/botón por defecto ya estaba usada por una partida antigua, la nueva acción queda sin asignar (sin pisar nada). La pantalla de controles y el editor táctil incluyen las dos acciones nuevas.

## Bendiciones y sinergias
Los proyectiles de las armas secundarias son proyectiles del jugador: las bendiciones de proyectiles (perforación, velocidad, tamaño, rebote, doble disparo…) y de daño los modifican igual que a cualquier otro; el cetro usa daño de compañero. El parry perfecto abre la ventana de **contraataque** (`Contra a distancia`: el siguiente disparo hace +50 %). El cambio de arma no reinicia ni duplica ningún efecto.

## Guardado
- La run guarda arma, munición, nivel, arma activa (`secAct`), estado de cada arma (`wst`) y objetos nuevos/vistos; todo **aditivo** (`ver: 2`).
- Partidas antiguas cargan sin cambios y se copia el original una vez a `<clave>_bak` antes de modificarlo; ids de arma desconocidos se ignoran sin romper.
- Las armas halladas en una run **no** se desbloquean de forma permanente.

## Pruebas
`tools/tests/arsenal_test.sh` (banco headless, **no** son pruebas en un Android o Windows reales): sin secundaria, primera recogida, cambio, 240 pulsaciones de cambio, 30 intercambios seguidos sin duplicar ni perder, colocación segura (pinchos, borde, 6 en el mismo punto), limpieza de sala, comportamiento y daño de cada arma, sin munición, contraataque, bendición de proyectiles, cofres (confirmar/rechazar/directo/duplicados), inventario (apertura, pausa, controles bloqueados, listas reales, orden, filtros, 6 tamaños, cursor visible, nuevos, acción, cierre sin acciones fantasma) y guardado (v2, antiguo, copia de seguridad, arma desconocida).

Nota: `tools/tests/events_test.sh` (modos `nav` con suceso 8 y 9) falla a veces por azar de la sala (no siempre hay hueco para la puerta lateral); ocurre igual antes de este sistema (3 de 12 ejecuciones en la versión anterior y 3 de 12 en esta).
