# Inventario, mejoras acumulables y dificultad creciente

Todas las pruebas son del **banco headless** (motor real del juego en el escritorio, sin ventana). No se han probado en un Android ni en un Windows reales.

## Etapas 1-2 · Inventario y bolsa de armas
**Antes:** la pestaña Armas listaba toda arma que hubieras tocado en la run (`RunState.wState`: equipada, en el suelo o dejada atrás) y recoger otra arma sustituía a la equipada (la vieja caía al suelo).

**Ahora** hay cuatro conceptos separados:
| Concepto | Dónde vive |
|---|---|
| Descubierta para siempre | colección / bestiario (sin cambios) |
| Poseída en esta run | `RunState.bag` (orden de obtención) |
| Equipada | `RunState.sec` (+ munición, cargador y nivel vivos) |
| Mejoras acumuladas | `cb`/`cbLvl` (estadísticas), `spLvl` (mejoras del arma principal), `bLvl` (nivel de cada arma) |

- **Tope único:** `RunState.WEAPON_BAG = 10` (la equipada cuenta). Cambiarlo ahí cambia todo el juego.
- **Recoger** (suelo, cofre, cofre secreto, desbloqueo): sin secundaria se equipa; si no, se **guarda**; repetida sube de nivel (o da munición al máximo). Nunca sustituye ni destruye.
- **Equipar desde el inventario** (botón *Equipar*, o Aceptar): la anterior queda guardada con su munición, cargador y nivel (`Arsenal.stash/switchTo`).
- **Soltar** (botón *Soltar* o tecla X): el arma sale de la bolsa al suelo, en un sitio seguro, y se puede volver a coger.
- **Bolsa llena:** aparece *Inventario de armas lleno*: fila con tus 10 armas, ficha de la marcada frente a la nueva (+ mejor / - peor) y dos botones: **Cancelar** (el arma sigue en el suelo o vuelves a las 3 ofertas del cofre) o **Soltar «X»** (esa cae al suelo y la nueva ocupa su hueco; si era la equipada, la nueva queda equipada). Teclado: ←/→ elige arma, ↑/↓ cambia de botón, Esc cancela.
- La pestaña Armas muestra solo la principal y la bolsa, con *EQUIPADA / EN USO / GUARDADA*, nivel propio de cada arma y el contador `n/10`.
- Guardado: `bag`, `bAmmo`, `bMag`, `bLvl`. Partidas antiguas: solo la equipada pasa a ser tuya.

## Etapas 3-5 · Mejoras acumulables y recompensas según la build
- Las **mejoras del arma principal** (Filo Ígneo, Colmillo Gélido, Daga Venenosa, Hacha Carmesí, Lanza Relámpago, Hoja del Eclipse, Mandoble Pesado, Hoja Veloz) ya **no se sustituyen**: se tienen todas a la vez, cada una con nivel 1-3 (efecto ×1 / ×1,5 / ×2; las penalizaciones de Mandoble Pesado y Hoja Veloz se aplican una vez). Desaparece el «Sustituye a …» en mejoras.
- Las **mejoras de estadística** de cofre (21, p. ej. *Filo afilado*) llevan nivel (`cbLvl`) con tope propio (`ChestLoot.S_MAXLVL`, 1-6). Al llegar al tope dejan de ofrecerse y sale otra opción.
- 29 mejoras distintas posibles por run (21 + 8); la prueba activa 28 a la vez.
- Cartas: *Mejora nueva · Nivel 1* o *Nivel 2 > 3 · total +18% daño*; mejoras del arma: *Nivel 1 > 2*, *Total: …*, *Ahora: …*.
- Inventario: nueva pestaña **Mejoras** con nivel (Nv/MAX), efecto acumulado y las sinergias activas. Las mejoras salen de *Objetos*.
- Generación: las mejoras que ya tienes pesan ×1,8 (`ChestLoot.OWNED_BOOST`) y reaparecen para subir de nivel; rareza ponderada por suerte; las armas que tienes (también guardadas) pueden salir como «Nivel X > X+1»; nunca se ofrece como nueva un arma que ya posees.
- **Omitir** sigue igual: el cofre conserva sus 3 ofertas; abrir/omitir/reabrir no sube nada; elegir sube exactamente un nivel y consume el cofre.

## Etapa 6 · Sinergias entre mejoras (`Synergy.java`)
| Sinergia | Requiere | Efecto |
|---|---|---|
| Combustión tóxica | Fuego + Veneno | El enemigo que muere quemado o envenenado estalla (radio 46, 60% del daño base) y envenena alrededor |
| Escarcha afilada | Hielo + Críticos | +50% al multiplicador crítico contra congelados o ralentizados |
| Frenesí sanguinario | Robo de vida + Vel. de ataque | +4% robo de vida, +8% vel. de ataque |
| Tormenta de acero | Descarga + Daño | +10% daño, +10% prob. de descarga |

Cuentan tanto las estadísticas de cofre como las mejoras del arma principal. Al activarse se avisa («¡Sinergia: …!») y aparecen en la pestaña Mejoras. Son independientes de las sinergias de bendiciones.

## Etapa 7 · Más enemigos tras cada jefe (`Escalation.java`)
Configuración central (un solo archivo):
- Extra de enemigos: +15% por jefe derrotado, tope +100% (`EXTRA_PER_BOSS`, `EXTRA_MAX`), multiplicado por dificultad (fácil ×0,6, normal ×1, difícil ×1,3).
- **Infinito** escala por piso (+12% por piso, tope +180%) sin mirar los jefes de campaña.
- Los extra mezclan los tipos de la propia sala (combinaciones coherentes con el bioma); desde 2 jefes pueden ser **élite** (hasta 30%) y desde 4 jefes hay un 25% de **mini-jefe** por sala (élite con ×2,2 de vida).
- **Tope de vivos a la vez:** 7 + 1 por jefe, máximo 13. Los que sobran esperan en una reserva y entran de uno en uno (1,8 s → 0,9 s entre refuerzos), en un punto de la sala a ≥110 px del jugador, y van a por él desde que aparecen.
- La detección de los enemigos crece +7% por jefe (máx. ×1,6). Cada tipo conserva su comportamiento.
- Sin jefes derrotados la sala es idéntica a la de siempre. La reserva es de la sala: no pasa a la siguiente ni se duplica; la sala no se despeja hasta vaciarla. Jefes y salas de evento no cambian.

## Pruebas (banco headless)
| Prueba | Resultado |
|---|---|
| `arsenal_test.sh` (bolsa, equipar, soltar, bolsa llena, cofres, guardado, inventario) | 273 OK, 0 fallos |
| `upgrades_test.sh` (mejoras, niveles, topes, generación, omitir, inventario, sinergias) | 43 OK, 0 fallos |
| `escalation_test.sh` (cantidades, dificultad, Infinito, tope de vivos, refuerzos, persecución, transiciones, variantes, rendimiento) | 16 OK, 0 fallos |
| Regresión: combate, HUD, UI, movilidad, menús, jefes voladores y de suelo, cuerpo a cuerpo, Omitir del cofre, animación | todas OK |
| Textos (detector `TextAudit`) del inventario y de «bolsa llena» en ES/EN/FR/ZH | sin textos fuera, recortados ni pisados |
| Rendimiento con dibujo real (sala de la mazmorra 8, bot jugando 40 s) | ningún fotograma lento en combate (solo el de carga de sala, igual que sin escalado); memoria 234 → 299 MB |

Ejemplo medido (difícil, misma semilla): enemigos base + extra por jefes derrotados: 0:9+0, 2:9+4, 4:10+10, 8:11+16, con un máximo de 13 vivos a la vez.
(El extra se ajustó después a +15%/jefe y tope +100%, así que en normal ahora es menor.)

## Limitaciones
- Rendimiento medido solo como tiempo de lógica en el banco (no dibujo ni GPU de un móvil real).
- Las armas que quedan en el suelo no se guardan si sales de la partida a mitad de sala (como antes).
- El equilibrio de cantidades es un primer ajuste: los valores están todos en `Escalation` para retocarlos.
