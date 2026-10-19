# Vuelo de jefes voladores (Reina de la Escarcha y otros)

## Causa del ascenso ilimitado
En `Boss.java`, el objetivo de altura del vuelo se calculaba **solo en relación con la altura del jugador** y se pasaba tal cual a `hoverTo(...)`:
- reposo/persecución: `p.y - 60 (+ oscilación)`; lanzamiento de hechizos: `p.y - 80`.
No había ningún límite absoluto. Cada plataforma que subía el jugador subía el objetivo de la reina (jugador +60 px → reina +60 px), de modo que acababa pegada al techo o fuera de pantalla, fuera del alcance del salto. Además `hoverTo` perseguía ese objetivo sin suavizado ni zona muerta, por lo que cualquier cambio de plataforma producía saltos bruscos de velocidad vertical.

## Corrección (solo lógica de movimiento; vida, daño, fases, ataques, velocidades y animaciones no cambian)
1. **Banda de vuelo absoluta** (`Boss.computeZone`), calculada de la geometría real de la sala la primera vez que vuela:
   - abajo = suelo de la arena − 28 px;
   - arriba = el mayor de: (techo + alto del cuerpo + 10 px), (techo + altura del sprite − 30 px, para que corona/alas no salgan de la pantalla) y (superficie alcanzable más alta − 24 px, para que desde la plataforma más alta el cuerpo de la reina siempre solape con el jugador);
   - banda mínima de 48 px.
2. **Objetivo acotado** en `hoverTo`: `gy = clamp(gy, zoneTop, zoneBot)`. Ya no depende de cuánto suba el jugador.
3. **Reajuste controlado**: el objetivo se acerca al valor deseado a ≤ 120 px/s (sin saltos bruscos al cambiar de plataforma) y hay una zona muerta de 6 px (sin oscilación constante).
4. **Seguro final**: tras mover, `y` se recorta a la banda (nunca atrapada en el techo ni fuera de pantalla).
5. Al llegar al límite superior deja de subir; el movimiento horizontal y las transiciones de estado (reposo, windup que desciende hacia el jugador, ataque, recuperación) siguen igual.
La misma lógica se aplica a los demás jefes voladores (Devorador del Vacío, Matriarca de Sangre, Dios Antiguo) porque comparten el código, sin cambiar nada más.

## Pruebas — `tools/tests/boss_fly_test.sh` (banco headless, no es dispositivo real)
Reina (boss:2), Devorador (boss:3), Matriarca (boss:6): el jugador (invulnerable) pasa por suelo → cada plataforma de abajo a arriba → saltos repetidos bajo el jefe → fase 2 en la plataforma más alta. Se comprueba cada fotograma: dentro de la banda de vuelo; nunca por encima del límite; sprite y cuerpo dentro de pantalla; la altura queda al alcance de un salto simple (88 px) en ≥ 50 % del tiempo en cada etapa; sigue volando (no baja al suelo) y atacando (≥ 3 ataques, varios estados); la fase 2 no rompe el límite.
Con `BOT_NOZONE=1` (comportamiento anterior) el mismo recorrido deja a la reina pegada al techo (y = 148, cuerpo a 48 px del borde superior) y la banda no existe.

## Limitaciones
- Probado en las arenas de jefe generadas por el juego (2 plataformas, techo a 48 px). Si se añaden arenas con geometrías muy distintas, `computeZone` las recalcula automáticamente, pero conviene repetir `boss_fly_test.sh`.
- Cazador III (Dios Antiguo) comparte la lógica pero no se ha medido por separado.
