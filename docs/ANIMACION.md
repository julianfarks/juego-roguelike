# Animación y sensación de combate (fase 1: ciclo del personaje principal)

Pruebas: `tools/tests/anim_test.sh` (banco headless, no es un Android/Windows real).

## Auditoría (estado antes de esta fase)
- Hojas `pl_*.png`: 10 clases, celda 64×48, mismas animaciones. Ataque 1/2 = 6 fotogramas, ataque 3 = 7, aéreo = 5, esquiva = 7; todos a velocidad **uniforme** (sin anticipación lenta ni recuperación con peso).
- Daño: caja de golpe fija por animación (`box`) activa solo en los fotogramas `hit`. No depende del sprite dibujado.
- Ya existía `Impact` (hit-stop con presupuesto, sacudida, chispas por elemento, sonido por tipo, parry/esquiva perfecta). **No** había smear frames, ni pose de impacto, ni reacción visual del objetivo, ni límite de capas de sonido.

## Qué se añadió
1. **Duración por fotograma** (`"ft"` en el JSON de la hoja, clase `Anim`): peso de cada fotograma; duración = suma/fps. Depende solo del tiempo, no de los FPS. Ataque 3 (pesado) ≈ 0,62 s con anticipación marcada; ataque 1/2 ≈ 0,41 s; aéreo ≈ 0,35 s; esquiva ≈ 0,39 s.
2. **Smear frames** (`tools/art/make_smear.py`): un fotograma nuevo por animación (ataque 1-3, aéreo, esquiva) en las 10 clases. Cuerpo estirado a lo largo del movimiento (vecino más cercano, sin desenfoque), eco tramado de la pose anterior y líneas de velocidad de 1 px, **solo con colores de la propia hoja**. Se inserta justo antes del primer fotograma de golpe: el daño ocurre en los mismos fotogramas de contacto que antes (los `hit` se desplazan +1, las cajas no cambian). `"smear"` en el JSON indica el índice.
   - Importante: estos fotogramas se generan por script a partir de los dibujos existentes; **no son dibujo manual**. Si quieres un acabado artesanal por clase, se pueden retocar a mano en la hoja sin tocar código (el índice y los pesos ya están).
3. **Pose de impacto** (solo visual): el objetivo se comprime en el sentido del golpe en el instante del contacto (se mantiene durante la pausa de impacto porque el tiempo de juego se detiene) y rebota en 0,16 s; pesado/crítico añaden sacudida de pérdida de equilibrio; jefes ×0,45; "reducir efectos" ×0,5. El jugador también se estira hacia el golpe al conectar. No modifica `bw/bh` ni el daño.
4. **Ecos de clase** detrás del tajo en el fotograma smear (movimiento secundario, desactivado con "reducir efectos").
5. **Smear en enemigos** (`Enemy.render`): embestida, salto y picado estiran la silueta en el sentido del movimiento con dos ecos.
6. **Presupuesto de sonido** (`Impact.sfxOk`): como máximo 3 capas de golpe por ventana de 60 ms. Los ataques que fallan no generan impacto ni sonido de golpe.

## Pruebas (`anim_test.sh`)
- Hojas: fotogramas originales intactos, `box` igual, `hit` +1, smear con paleta propia (todas las clases).
- Tiempo: fotogramas monótonos, termina a la duración, 30 fps = 60 fps.
- Vivo: combo 1-2-3 real contra maniquí → se muestra el smear, los impactos solo caen en fotogramas de golpe, ataque al aire sin impactos, pose de impacto acotada y de 0,16 s, límite de sonido.

## Fase 2 (completada)
- **Habilidades**: fotograma smear de lanzamiento insertado justo antes del fotograma de liberación (`rel` +1; el proyectil sale en el mismo instante de la pose). Las 10 clases. La definitiva (`ult`, 10 fotogramas) ocupa toda la fila de la hoja: no admite un fotograma más sin ampliar la hoja, así que conserva su animación y sus efectos.
- **Daño recibido**: nuevo fotograma de impacto (pose comprimida, desplazada hacia atrás, con contorno de 1 px del tono más claro del sprite) antes de la pose original; pesos `[0.5,0.8,1.6]`.
- **Parry perfecto**: el jugador absorbe el choque (compresión y retroceso de 0,16 s) además del destello, la ventana de contraataque y el slow-mo ya existentes.
- **Armas secundarias**: impulso hacia delante al disparar; estelas de proyectil (ver abajo).
- **Proyectiles y magia** (`Level.drawProj`): ecos detrás con el color del proyectil (2 o 3 según velocidad, separación proporcional a la velocidad); los que giran (chakram, hacha) dejan giro residual. Fuego/hielo/rayo de la varita, flechas y lanzas heredan su color. Desactivado con "reducir efectos". Solo visual.
- **Jefes**: smear de embestida (estiramiento + 2 ecos) cuando atacan en movimiento; los patrones, telegrafías y zonas peligrosas no se tocan. La pose de impacto recibida de jefes es ×0,45.
- **Enemigos comunes**: la reacción depende del tipo de golpe y del tipo de enemigo (pesados/escudo ×0,6, voladores ×1,2).

## Pendiente / limitaciones
- Los smear de las hojas son generados por script a partir de tus dibujos (no dibujo manual); se pueden retocar a mano sin tocar código.
- Definitiva (`ult`) sin smear propio (fila de hoja llena). Bloqueo (`block`) no se usa en juego (el escudo se dibuja por código).
- Pelo/capa/accesorios van pintados en la hoja; no hay capas separadas para animarlos aparte.
- Enemigos y jefes con hoja propia: no se redibujaron fotogramas; el smear es por código (estiramiento nearest-neighbor + ecos).
- Falta validar el tacto en dispositivo real (Android/PC) y a 30 fps reales.
