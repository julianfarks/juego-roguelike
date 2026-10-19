# Fase 3 — evaluación de enemigos, minibosses y jefes

Evaluación **cualitativa** hecha mirando hojas de contacto de los 40 enemigos (reposo, ×3) y de los 11 jefes (celda completa). No hay métrica
automática de "calidad artística": los criterios son los pedidos (silueta, detalle visible en combate, diferenciación, materiales, necesidad
de cambiar las formas principales). Clase **A** = necesita rehacer silueta/composición; **B** = bien, mejoraría con materiales/detalle;
**C** = funciona, no tocar de momento.

## Enemigos comunes (40)

| Clase | Enemigos | Motivo |
|---|---|---|
| **A hecho (piloto)** | zombi, cubo_magma, murcielago, escudero_hueso | zombi: rectángulo vertical sin personalidad; cubo: una cara en un blob; murciélago: alas oscuras sobre cuerpo oscuro, poca lectura; escudero: misma silueta humanoide que el resto |
| **A pendiente** | arana, arquero_hueso, cultista_sangre, hechicero_hielo, lancero_escarcha, saqueador, vindicador, clerigo_osario | humanoides pequeños casi intercambiables (comparten la base `human()`); la araña se lee como rana (sin patas claras) |
| **B** | esqueleto (ya con detalle menor), asesino_eclipse, bruja, bruja_sangre, carbonero_forja, espectro, fantasma, lobo_musgo, tirador_rayo, vex_tormenta | silueta correcta; ganarían con materiales/contraste |
| **C** | acechador, bestia_tormenta, bruto_forja, caballero_osario, capitan_trueno, centinela_cristal, centurion_eclipse, druida_podrido, espiritu_vex, herrero_infernal, llama, llama_solar, ojo_vacio, piglin_dorado, sacerdote_carmesi, segador_vacio, tronco_vivo, ventisca | silueta distintiva y buen material |

## Jefes (11)

| Clase | Jefes | Motivo |
|---|---|---|
| **A hecho (piloto)** | rey_exanime | figura pequeña y genérica dentro de la celda de 192×160 |
| **A pendiente** | guardian_eclipse, titan_tormenta | titán: masa de piezas poco legible; guardián: silueta fina |
| **B** | cazador1, cazador2, matriarca_sangre, reina_escarcha | buena silueta, materiales mejorables |
| **C** | cazador3, coloso_magma, devorador_vacio, ent_ancestral | silueta imponente y reconocible |

Los minibosses/élites comparten las hojas `en_elites_a/b` (sin evaluar aparte en este piloto).

## Limitación del generador

Los humanoides pequeños salen de una misma base (`humanoid.py`: torso, extremidades, cinemática), de modo que cambiar la **silueta** de
uno de ellos exige piezas propias (cabeza/escudo/arma/capa grandes, como en el escudero) o una base distinta; los adornos sueltos no se
aprecian a escala de juego (se comprobó con el zombi y el esqueleto).
