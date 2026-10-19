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

## Pendiente / limitaciones
- Armas secundarias, jefes (smear específico por ataque), habilidades mágicas y parry/esquiva dibujados a mano: no se han rehecho; usan los efectos existentes (estelas de proyectil y `Impact`).
- Pelo/capa/accesorios: ya van pintados en la hoja; no hay capas separadas para animarlos aparte.
- Falta validar el tacto en dispositivo real (Android/PC) y en 30 fps reales.
