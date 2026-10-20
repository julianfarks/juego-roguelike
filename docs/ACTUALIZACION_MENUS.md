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
