# Rediseño de menús (organización RPG, estética de mazmorra)

Todas las pruebas son del **banco headless** (no Android ni Windows reales).

## Qué cambió
- **Componentes comunes** (`UI`): `rivets` (remaches de hierro envejecido en las esquinas de todo panel grande), `divider` (filete dorado con rombo), `title` (título con filetes laterales), `tag` (etiqueta rareza/categoría/estado). Se aplican a pausa, mejoras/cofres, tienda, forja, bendiciones, eventos, intercambio de arma, derrota/victoria y listas.
- **Inventario** (ya tenía pestañas, ranuras de equipo, rejilla, orden/filtro y volver): pestañas con estado claro (seleccionada = panel claro + subrayado dorado con brillo; resto atenuadas; punto rojo si hay novedades), panel de detalle con icono enmarcado por rareza, nombre ajustado a 2 líneas, etiquetas de rareza / categoría / estado (**EN USO**, EQUIPADA, EN EL SUELO, DEJADA, EN ESPERA), separadores, estadísticas y descripción completa. Panel de detalle más ancho; si el contenido no cabe (resoluciones pequeñas) se **desplaza** (flechas táctiles/ratón, PgUp/PgDn o K/B del mando; al final vuelve al inicio) en vez de cortarse.
- Se mantiene a propósito la **pausa sin botón de Inventario** (decisión de la actualización anterior; el inventario sigue accesible con su tecla/botón táctil y vuelve a la pausa).
- No se crearon pestañas vacías: las categorías son las que tienen datos reales (Armas, Bendiciones, Reliquias —incluye pactos, bendición inicial y compañero—, Objetos).

## Pruebas (`tools/tests/menus_test.sh`, 4 resoluciones x 4 idiomas)
- Recorre las 4 pestañas con todo desbloqueado (258 elementos: 200 bendiciones, 8 reliquias, pactos, 36 armas, objetos) y comprueba que ninguna ficha de arma se recorta; con 480x270, 25 armas necesitan desplazamiento y se verifica que las flechas y la paginación funcionan.
- Los conteos de cada pestaña coinciden con el estado real (bendiciones, reliquias, armas).
- Equipar: usar arma secundaria y volver a la principal desde el inventario; teclas Q/E (pestañas), F (filtro), O (orden), Esc (vuelve a la pausa).
- Con el inventario abierto el mundo queda pausado 2 s (jugador, enemigo, vida y reloj sin cambios).
- Suites previas (anim, arsenal, combate, HUD, interfaz, movilidad) siguen OK.

## Segunda pasada (20-10-2026): textos y organización en todas las pantallas
- El detector `TextAudit` ahora también marca:
  - textos **recortados** con "." o "…": no caben, aunque no se salgan del cuadro;
  - textos que **pisan un botón** ajeno;
  - textos **pegados al borde inferior** de su panel;
  - textos del mundo **convertidos a coordenadas de pantalla**, según la cámara y el zoom.
  - El contenido de los paneles con desplazamiento no cuenta fuera de la zona visible.
- **Mercader:** la lista va a la izquierda (icono, nombre y precio) y el detalle a la derecha, con la descripción completa, el precio (o cuánto falta) y el botón *Comprar*. Un toque elige y un segundo toque compra. Ya no se corta ninguna descripción.
- **Opciones:** dos columnas con cabecera (*Audio e imagen* / *Controles y datos*), y *Volver* dentro del panel. La versión del juego va debajo y ya no tapa *Volver*.
- **Trofeos:** las tarjetas tienen nombre, filete, copa y descripción completa, con una barra de progreso fina. El alto se calcula según la pantalla.
- **Pantallas altas (320 px):** los menús diseñados a 270 se centran en vertical, en vez de dejar una franja vacía abajo. El fondo ocupa toda la pantalla y los toques se corrigen.
- **Cartas de bendición:** si el nombre de la categoría no cabe, se usa un nombre corto.
- **Cofres y sucesos:** el alto de las cartas se calcula para el texto más largo.
- **Inventario y fichas de arma:** se elige una versión más corta en vez de recortar. Si el estilo del arma no cabe completo, se omite; el efecto siempre se muestra entero.
- **Colección y vídeo:** pestañas a la medida del idioma.
- **Avisos flotantes:** se apilan en vez de taparse, quedan dentro de la parte visible (con zoom de cámara) y las cifras de munición de los botones no se salen por abajo.
- **Placas de las estaciones del campamento:** se desvanecen al salir por el borde en lugar de verse cortadas.
- Resultado del detector: 0 avisos en las 20 pantallas de menú (4 idiomas × 480/640 × 270/320) y en el recorrido de la partida: mercader con las 200 bendiciones, ofertas, cofres, inventario, sucesos, listas y fichas (4 idiomas × 480×270 / 640×320).
- `combat_test` (contraataque): el muñeco se colocaba a veces dentro de un muro. Antes el golpe lo alcanzaba igual; ahora, correctamente, no atraviesa paredes. La prueba despeja el hueco.
