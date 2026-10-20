# Actualización de gameplay (6 mejoras)

Cada mejora tiene su propio commit. El parry (punto 5) **no se tocó** por indicación del usuario.
Todas las pruebas son del banco *headless* (`run2.sh --headless --bot`), no de un Android/Windows reales.

| # | Mejora | Commit |
|---|---|---|
| 1 | Habilidades sin perder efecto por golpes (Paladín) | 2b5e4bb |
| 2 | Omitir / Conservar equipo en cofres | bd18168 |
| 3 | Recompensas especiales tras jefes | 8b385a1 |
| 4 | Pinchos: aspecto y colisiones | 984439a |
| 5 | Parry | no se toca |
| 6 | Ataque cargado | este commit |

## 4. Pinchos
- Arte: rojo de peligro con contorno oscuro y 2 puntas triangulares por baldosa, igual en los 9 biomas (`tools/art_world/tiles_special.py`). Solo cambian los tiles de pincho (fila 3, cols 4-5); el resto de la hoja queda intacto.
- No existen pinchos con estado activo/inactivo: son siempre activos (no hay nada que diferenciar).
- Colisión: el jugador ahora pincha también con el pie a ±5 px del centro (antes solo el centro). Un golpe por contacto (i-frames 1,1 s y reaparición en punto seguro); rodando no pincha (comportamiento previo). Enemigos: 30 % de su vida máx. (mín. 20) cada 0,6 s, ya verificado (`BOT_SPIKETEST`: 9/9).
- Prueba: `BOT_SPIKEPL=1` (encima, borde, lejos, con i-frames).

## 6. Ataque cargado
Configuración única: `ChargeCfg.java` (tiempos, curva, efectos).
- Pulsación < 0,16 s = ataque normal (x1,00 exacto). Mantener = carga hasta 2 s; curva continua por interpolación lineal: 0,5 s → x1,20; 1 s → x1,50; 1,5 s → x1,85; 2 s → x2,25; sin aumento después.
- Se mide con `Level.rawDt` (segundos reales), no con fotogramas. Una pulsación = un golpe (el multiplicador se aplica una vez por enemigo y golpe, junto a crítico/estadísticas/elementales/mejoras, que usan el daño ya escalado).
- Mientras se carga se puede caminar (45 % de velocidad), saltar y rodar. Recibir daño, rodar, habilidad, pausa/menú o perder el control **cortan la carga sin golpe y sin gastar nada**; se puede atacar de inmediato y soltar el botón después no ataca.
- Efectos: pose de anticipación que avanza con la carga, aura y brillo progresivos, partículas que se concentran, barra sobre la cabeza, destello + sonido + temblor a carga máxima. Al soltar: tajo más grande, golpe pesado, empuje y área mayores (hasta +30 % de alcance, +35 % de alto), aturdimiento 0,25–0,60 s desde media carga (no a jefes).
- Compatibilidad: arma principal cuerpo a cuerpo de las 10 clases. **Armas secundarias (proyectiles/cuerpo a cuerpo secundarias)**: no usan carga; mantienen "mantener = repetir" porque el botón de ataque ya dispara por munición/cadencia. Queda para una adaptación propia.
- Balance medido (maniquí, 8 s, sin críticos): golpes rápidos ≈ 45-56 daño/s; cargados ≈ 12-20 daño/s (0,5 s ≈ 16-20; 2 s ≈ 15-19). La carga es un golpe de ráfaga (más daño por golpe, área y aturdimiento), no una opción de daño sostenido; el rápido sigue siendo mejor en DPS puro. Los valores están en `ChargeCfg` para ajustarlos.
- No se añadieron mejoras de build de carga (solo la base); `ChargeCfg` está preparada para recibir tiempo/daño máximo como escalas.
- Prueba: `BOT_CHARGETEST=1` (curva 0–3 s, interrupción por daño, rodar, pausa, DPS).
