# Paladín del Alba — prototipo 3/4 (EXPERIMENTAL, aislado del juego)

Una sola pose de reposo, 192x192, vista tres cuartos. No usa el rig paramétrico del juego.

- `dibujar_paladin_3q.py`: lista de piezas con vértices colocados a mano (coordenadas de pixel). **Es código, no un dibujo a mano.**
- `motor_pixel.py`: rasteriza sin antialiasing y sombrea por bandas (luz arriba-izquierda, filo de luz, sombra abajo-derecha, contorno por pieza). Sin desenfoque ni interpolación.
- `paladin_3q_reposo.png` (192x192), `paladin_3q_reposo_ampliado.png` (x5), `comparacion_192_generador_izq_3q_der.png`.
- `capas/`: ~140 PNG, una por pieza (RGBA, 192x192), para repintar a mano en un editor de pixel art.
- Regenerar: `python3 tools/experimental/paladin_3q/dibujar_paladin_3q.py`. No se toca el juego, las hojas, los JSON ni las animaciones.

Limitaciones: proporciones aún achaparradas (piernas cortas), brazo/hombrera izquierdos mal resueltos, sin vista de perfil ni animaciones, acabado lejos de la referencia.
