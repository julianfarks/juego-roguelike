# Jefe de hielo terrestre y golpes cuerpo a cuerpo a quemarropa

Pruebas del **banco headless** (no Android ni Windows reales).

## 1. Reina de la Escarcha: combate en el suelo
**Causa:** el jefe estaba definido como volador (`BossDef.hover = true`). Eso activaba `flying = true` y `gravity = false`, y la lógica de vuelo (`hoverTo`) la llevaba a ~60 px por encima del jugador, con su "banda de vuelo" y un balanceo vertical al dibujarla. El sprite ya estaba dibujado de pie (el vestido llega a la línea de los pies), así que el problema era solo de lógica.

**Cambios:**
- `BossDef`: la Reina pasa a terrestre (`hover = false`): gravedad normal, colisión con el suelo y plataformas como los demás jefes de suelo, sin balanceo y con sombra en el suelo.
- Sustitutos terrestres de su comportamiento aéreo (`Boss.iceQueen()`):
  - **deslizamiento sobre el hielo**: si el jugador está a más de 120 px, se desliza rápido (×1,8 de su velocidad) con poca fricción y deja escarcha. Reemplaza el reposicionamiento en vuelo;
  - si el jugador se sube a una plataforma alta (40 px por encima), lanza el **abanico de hielo** con el doble de frecuencia, en lugar de subir volando.
- Se conservan vida, daño, velocidad base, sus 3 ataques, el conjuro, la fase 2 y la presentación (cae del cielo y aterriza).
- `boss_fly_test.sh` sigue probando a los voladores que quedan (Devorador del Vacío y Matriarca de Sangre).

## 2. Golpes que fallaban con el enemigo pegado
**Causas medidas** (`MeleeProbe`, maniquí inmóvil a -8…80 px; antes de corregir, el arma principal fallaba a -4, 0 y 4 px quieta y de -8 a 4 px corriendo):
1. **El impulso del ataque atravesaba al enemigo.** Al atacar, el jugador avanza 10-15 px antes del fotograma activo. Como el jugador no choca con los enemigos, si estaba pegado lo atravesaba y, al llegar el golpe, el enemigo ya estaba detrás.
2. **La caja del arma empezaba 3 px delante del centro** del jugador. Un enemigo solapado con el cuerpo quedaba fuera de ella.
3. **Además:** los golpes atravesaban paredes. `enemiesInBox` no miraba los bloques; la prueba lo confirmó antes de corregir.

No había golpes "atravesados" entre fotogramas: la caja va pegada al jugador y el enemigo se mueve muy poco por fotograma.

**Cambios (sistema común: arma principal de todas las clases y las 13 secundarias cuerpo a cuerpo):**
- `Level.frontBlocked`: durante el golpe, el impulso hacia delante se detiene al tocar al enemigo que hay delante. El jugador ya no lo atraviesa.
- Zona cercana: la caja del golpe se extiende hacia atrás **solo hasta el borde del propio cuerpo** (medio ancho). El alcance hacia delante de cada arma no cambia.
- `Level.meleeReach`: un enemigo solo recibe el golpe si no hay un bloque sólido entre el pecho del atacante y el enemigo.
- No se tocaron estadísticas, animaciones, fotogramas activos ni el control de un impacto por enemigo y golpe.

## Pruebas
- `tools/tests/boss_ground_test.sh` (3 semillas). Suelo → plataformas → saltos junto a ella → fase 2 → daño real. En cada fotograma se comprueba que no vuela, no flota, no queda dentro de un bloque y apoya los pies en la superficie. Además sigue atacando (cuerpo a cuerpo, abanicos, deslizamientos), usa sus animaciones de suelo y llega a la fase 2 sin bloquearse. Sus ataques hacen daño real.
- `tools/tests/melee_test.sh`:
  - arma principal de 5 clases y las 13 secundarias, quieto y corriendo, a 13 distancias. Ahora todas aciertan de -8 a 20 px, y las lejanas siguen fallando según el alcance de cada arma;
  - sin impactos de más (máximo los golpes que tiene cada arma);
  - pared de por medio: sin daño (antes sí lo hacía);
  - enemigo acercándose: 1 impacto;
  - giro rápido con el enemigo pegado a la espalda: 1 impacto;
  - corriendo con un enemigo 24 px detrás: sin daño.
- Suites previas: animación (fotogramas activos y cajas de golpe), arsenal, combate, interfaz, movilidad, menús y vuelo de jefes: OK.
- `hud_test` (sinergias) fallaba 2 de cada 10 veces, ya antes de estos cambios (comprobado en el commit `51997c3`). Según la sala generada, un maniquí de la prueba caía en un foso. Ahora la prueba prepara suelo plano: 8 semillas y 8 ejecuciones sin semilla, todas correctas.
