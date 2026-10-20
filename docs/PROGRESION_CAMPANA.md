# Progresión de campaña: 8 mazmorras + Cazador (una sola partida)

Estado: implementado y probado **solo en el banco headless** (no en Android/Windows reales, no jugado a mano).

## Flujo
- Una partida recorre las 8 mazmorras (3 de tramo 0, 2 de tramo 1, 3 de tramo 2) y luego el Cazador (3 formas). `RunState.dungeonNo` cuenta las superadas (0..8); `stage` es el tramo derivado (`RunState.tierOf`).
- `RunScreen.afterBoss` ya no termina la partida ni exige el Sello. Las reliquias del Sello siguen siendo progreso **entre partidas** (desbloqueos persistentes); no bloquean el final. La cinemática final tampoco las exige (`Story.allBossesDefeated`).
- `RunSave` persiste `dungeonNo`; las partidas antiguas lo reconstruyen desde `stage` (inicio de tramo).

## Victoria definitiva
Tras la 3ª forma del Cazador: pantalla con **Endless** (sigue la misma partida en `Infinite`, conserva equipo y estadísticas), **Créditos** y **Salir** (recompensas/estadísticas ya guardadas en `endRun`; borra la partida en curso y vuelve al menú). No se cierra sola.

## Arma principal
Tope único `RunState.WEAPON_MAX = 20`. Curva: +10 % de daño por nivel hasta el 5, +5 % después; coste 60 + 45/nivel hasta el 5, +55/nivel después.

## Sinergias
Ya existían 20 (200 bendiciones, `tools/blessings`). Se añadieron Detonación Crítica, Funeral Ígneo y Plaga Viva (cadena crítico → explosión → muerte → explosión/propagación). Topes: profundidad de KILL < 3, `icd` por regla, tope de daño.

## Balance de campaña
`power = round(dungeonNo*2.25) + sala`; jefes y oro/almas con `tierF()`; élites 5–30 % desde la 4ª mazmorra; velocidad +8 %/+15 % en las últimas. Tabla: `BOT_BALTEST`.

## Pruebas (todas headless)
`BOT_PROGTEST` (recorrido de 9 biomas con atajo), `BOT_WINTEST`, `BOT_CONTTEST`, `BOT_WEAPONTEST`, `BOT_BLESSTEST=syn|chain|stress|ui|persist`, `BOT_SAVETEST`, `BOT_BALTEST`, y el flujo real con `BOT_KILLBOSS`+`BOT_WATCH` (jefe → puerta → siguiente mazmorra; Cazador 3 formas → victoria → Endless).

## Pendiente
Duración real de una partida (no medida), equilibrio real del nivel 20 + sinergias frente a los jefes, pruebas en dispositivos reales, retroalimentación visual de críticos/explosiones, registro persistente de builds, y el arte de la Fase 3 (36 enemigos, 10 jefes).
