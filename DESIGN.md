# SwordsmanMagic: Eternal Abyss — DISEÑO Y CONTRATOS DE ASSETS

Roguelike de acción 2D (estilo Dead Cells) para Android, en pixel art oscuro/gótico, basado en el mod de Minecraft
"SwordmanMagic" (clases, armas, jefes, mazmorras). Idioma del juego: ESPAÑOL. Orientación: horizontal (landscape).
Motor propio en Java (Canvas, 60 FPS). Este documento es el CONTRATO entre generadores de arte/sonido y el motor.
El motor lee los tamaños de celda, pivotes y tiempos desde los JSON, así que respeta los nombres EXACTOS.

## 0. Reglas generales para quien genere assets

* Raíz de salida: `/home/claude/juego-roguelike/app/src/main/assets/` (en adelante `A/`).
* Cada generador vive en SU carpeta `/home/claude/juego-roguelike/tools/<tu_carpeta>/` (Python 3 + Pillow + numpy + scipy; ffmpeg con libvorbis disponible).
  No toques carpetas de otros agentes. NO ejecutes git (el coordinador hace los commits). Genera previews (PNG ampliados, hojas de contacto, GIFs)
  en `/home/claude/juego-roguelike/tools/previews/<tu_carpeta>/` (NO dentro de `A/`) y MÍRALOS tú mismo (herramienta Read sobre el PNG) para juzgar calidad y corregir.
* Todo debe ser determinista (semillas fijas) y re-ejecutable con un solo comando (`python3 tools/<carpeta>/build_all.py`).
* No hay internet salvo pip/npm; no uses assets externos. Todo se dibuja/sintetiza por código.
* Presupuesto de peso: arte total < 25 MB, audio total < 30 MB. PNG optimizados (paleta limitada, `optimize=True`).
* Calidad objetivo: pixel art HERMOSO, de nivel comercial (Dead Cells / Blasphemous / Hollow Knight). Nada de rectángulos planos: volumen, rim-light, siluetas legibles.
  Si algo queda feo en el preview, itera hasta que se vea bien. Es preferible menos variantes pero pulidas que muchas feas.

### Reglas de pixel art (todas las hojas de sprites)
* Resolución lógica del juego: 270 px de alto (ancho 480–640), tile = 16 px. Un personaje mide ~28–32 px de alto.
* Luz desde ARRIBA-IZQUIERDA. Rampas de 4–6 tonos por material con cambio de matiz (sombras hacia azul/púrpura, luces hacia amarillo/cálido). Prohibido negro puro (#000) salvo huecos; usa casi-negros tintados.
* Contorno de 1 px por sprite (selout: contorno más oscuro del color del material, no negro uniforme) + contorno exterior más oscuro. Anti-aliasing manual limitado; sin bordes semitransparentes (alpha solo 0 o 255, excepto efectos de luz/glow en FX).
* Técnica recomendada: construir cada parte como forma rellena, calcular un mapa de "altura" (distancia al borde) para sombrear con rampa según normal·luz, ordenar dither en bordes de sombra, supermuestrear x3-x4 y reducir con votación de color (mayoría) para que las rotaciones salgan limpias, y por último pasada de contorno a 1x. Esqueletos con cinemática directa para animar (partes con ángulos por fotograma).
* Animaciones con anticipación, acción y seguimiento (squash/stretch sutil, arrastre de capa/pelo/capa secundaria, respiración en idle). Cada fotograma importa.
* Todos los sprites miran a la DERECHA. El motor voltea para la izquierda.
* Fondo transparente. Sin sombras proyectadas en el suelo (el motor las dibuja).

### Formato de hoja de sprites (aplica a `A/sprites/*` y `A/fx/*`)
Un PNG RGBA + un JSON con el mismo nombre base.

```
{
  "cell": [W, H],          // tamaño de cada fotograma en px
  "pivot": [px, py],       // punto de apoyo (centro de los pies) dentro de la celda; en FX/props el pivote es el centro de efecto
  "body": [w, h],          // caja de colisión sugerida (ancho, alto) centrada en pivot.x, con la base en pivot.y
  "anims": {
    "idle":    {"row":0, "n":6, "fps":8,  "loop":true},
    "attack1": {"row":5, "n":6, "fps":16, "loop":false, "hit":[2,3], "box":[6,-26,28,24], "rel":3}
  }
}
```
* Fotograma i de la fila r: recorte `x = i*W, y = r*H`. El ancho de la hoja = (máx n) * W; el alto = filas * H.
* `hit`: [primer, último] fotograma (incluidos) en que el golpe es dañino. `box`: [x, y, w, h] del área de golpe relativa al pivote, mirando a la derecha
  (x positivo = delante del pivote; y negativo = hacia arriba; (x,y) es la esquina superior izquierda). Puede ser mayor que la celda para ataques con alcance (se limita visualmente a la celda, pero el daño usa la caja).
* `rel`: fotograma en que se libera un proyectil/efecto (ataques a distancia, conjuros). `muzzle`: [x,y] relativo al pivote donde nace el proyectil.
* Las animaciones de ataque DEBEN dibujar el arco/estela de la espada dentro del propio fotograma (semitransparente, brillante, color de la clase) en los fotogramas activos.

## 1. Mundo y trama (del mod)

Eres un espadachín que desciende a un Abismo eterno. Ocho Mazmorras guardan las Reliquias de ocho Guardianes caídos; el Sello del Cazador
se forja con las 8 reliquias y abre la Luna de Sangre, donde espera El Cazador, Dios Antiguo. Cada intento (run) recorre 3 mazmorras elegidas;
al derrotar jefes por primera vez, su Reliquia queda guardada para siempre en el Santuario (progreso permanente).
Con las 8 reliquias el Sello queda forjado y cada run termina contra El Cazador (3 fases).

### Biomas (id → nombre → color de acento → jefe)
| id | nombre | acento | ambiente / paleta | jefe |
|---|---|---|---|---|
| catacumbas | Catacumbas | #5CFF9A | piedra gris-azulada, hueso, almas verde espectral, tumbas, velas | bs_rey_exanime |
| forja | Forja Infernal | #FF7A1A | basalto negro, ladrillo rojo, lava, chispas, cadenas | bs_coloso_magma |
| helado | Santuario Helado | #7AF0FF | hielo azul, cuarzo blanco, nieve, cristales, aurora | bs_reina_escarcha |
| vacio | Abismo del Vacío | #B04CFF | obsidiana, púrpura, estrellas, grietas del vacío, ojos | bs_devorador_vacio |
| bosque | Bosque Podrido | #FFC24A | musgo, madera oscura, hongos luminosos, raíces, polillas ámbar | bs_ent_ancestral |
| tormenta | Fortaleza del Trueno | #4FA8FF | cobre oxidado turquesa, nubes, relámpagos, torres | bs_titan_tormenta |
| sangre | Catedral Carmesí | #D0203A | ladrillo rojo oscuro, vitrales, hueso, sangre, niebla | bs_matriarca_sangre |
| eclipse | Santuario del Eclipse | #F2E6B8 | piedra negra con oro, sol y luna eclipsados, columnas | bs_guardian_eclipse |
| cazador | Luna de Sangre | #C8142E | ciudad gótica victoriana, luna roja gigante, niebla roja | bs_cazador1/2/3 |

### Clases jugables (id, nombre, arma, color principal / secundario)
| id | nombre | arma (sprite) | color1 | color2 |
|---|---|---|---|---|
| paladin | Paladín del Alba | espada ancha + escudo, armadura dorada pesada, capa blanca | #FFD25A | #FFF6C8 |
| shadow | Asesino de las Sombras | dos dagas curvas, capucha y bufanda morada | #A040FF | #3A0A66 |
| flame | Señor de las Llamas | espadón llameante a dos manos, armadura de obsidiana con grietas de fuego | #FF5A1A | #FFC040 |
| storm | Tempestad | estoque (rapier) eléctrico, ropa azul ligera, pelo al viento | #4DC8FF | #F0FCFF |
| frost | Guardián Glacial | sable de cristal de hielo, armadura azul pálido con pieles | #80E4FF | #FFFFFF |
| verdant | Guardián Esmeralda | espada viva de madera con enredaderas, capa de hojas, cornamenta | #4FD96A | #C8FF9A |
| blood | Segador Carmesí | guadaña de hoja roja, gabardina oscura con sombrero de ala ancha | #C4122C | #FF6A7C |
| earth | Coloso de Roca | martillo/maza de piedra gigante, cuerpo ancho de roca y musgo (algo más grande que los demás) | #C98B3C | #FFD27A |
| astral | Vagabundo Estelar | espada-bastón con orbe estelar, túnica cósmica con estrellas | #FF4FD0 | #8A6CFF |
| steel | Soberano de Acero | katana + hojas flotantes detrás, armadura de acero y bufanda naranja | #C9D4E8 | #FF9A3C |

## 2. Contrato de ARTE

### 2.1 Jugadores — `A/sprites/pl_<clase>.png|json` (10 hojas)
Celda **64×48**, pivote **[32,44]**, `body` [12,28] (earth: [16,32]). Filas EN ESTE ORDEN (nombre, n, fps, extras):

| fila | anim | n | fps | loop | hit / rel |
|---|---|---|---|---|---|
| 0 | idle | 6 | 8 | sí | |
| 1 | run | 8 | 14 | sí | |
| 2 | jump | 3 | 10 | no | |
| 3 | fall | 2 | 8 | sí | |
| 4 | roll | 7 | 20 | no | |
| 5 | attack1 | 6 | 16 | no | hit [2,3] |
| 6 | attack2 | 6 | 16 | no | hit [2,3] |
| 7 | attack3 | 7 | 15 | no | hit [3,4] (el más fuerte; finisher) |
| 8 | airatk | 5 | 16 | no | hit [1,3] |
| 9 | skill | 7 | 14 | no | rel 3 (conjuro/pose genérica de habilidad) |
| 10 | ult | 10 | 12 | no | rel 5 (pose épica de la definitiva) |
| 11 | hurt | 2 | 10 | no | |
| 12 | death | 9 | 9 | no | |
| 13 | block | 2 | 8 | no | (guardia; todos, pero paladin la usa mucho) |

Cada clase cambia el ritmo, el alcance (`box`) y la silueta de ataque según su arma (dagas = rápido y corto, espadón/martillo = lento y amplio, estoque = estocadas largas, guadaña = arco enorme, etc.).
Además:
* `A/sprites/portrait_<clase>.png` 32×32 (busto, para selección/HUD) y `A/sprites/splash_<clase>.png` 128×176 (pose heroica grande, dibujada con más detalle que el sprite, con rim-light del color de la clase y fondo transparente).

### 2.2 Enemigos normales — `A/sprites/en_<id>.png|json` (24 hojas)
Anims obligatorias: `idle` (4–6), `walk` (6–8; en voladores es el aleteo/vuelo), `windup` (4, anticipación telegrafiada, ~0.35 s), `attack` (5–7; con `hit`+`box` si es melee, o `rel`+`muzzle` si es a distancia), `hurt` (2), `death` (7–8).
Celda 48×48 (pivote [24,46]) salvo los "pesados" 64×64 (pivote [32,62]). Los voladores usan pivote en el centro-abajo del cuerpo. Dibuja siempre con el rol indicado:

| bioma | id | rol / comportamiento | aspecto |
|---|---|---|---|
| catacumbas | en_esqueleto | melee rápido | esqueleto con espada oxidada y escudo roto |
| catacumbas | en_arquero_hueso | a distancia (flechas) | esqueleto con capucha y arco |
| catacumbas | en_zombi | pesado lento (64×64) | zombi hinchado con armadura podrida y cadenas |
| forja | en_cubo_magma | salta (slime) | cubo de magma con núcleo incandescente |
| forja | en_llama | volador, dispara bolas de fuego | espíritu de fuego con máscara/cráneo |
| forja | en_bruto_forja | pesado embestidor (64×64) | brute con yelmo de hierro y martillo candente |
| helado | en_lancero_escarcha | melee de alcance largo | caballero helado con lanza de hielo |
| helado | en_hechicero_hielo | a distancia (esquirlas), se teletransporta | mago de hielo con túnica y cristales flotantes |
| helado | en_espiritu_vex | volador veloz | espíritu pequeño de escarcha con espada |
| vacio | en_acechador | melee rápido/trepa | criatura insectoide oscura con garras |
| vacio | en_ojo_vacio | volador, dispara orbes | ojo flotante con tentáculos y pupila violeta |
| vacio | en_fantasma | volador en picada | fantasma tipo phantom, alas rasgadas |
| bosque | en_arana | salta/trepa, melee | araña grande venenosa |
| bosque | en_bruja | a distancia (pociones) | bruja del pantano con sombrero y caldero |
| bosque | en_tronco_vivo | pesado (64×64) | tocón/hombre de madera con musgo y hongos |
| tormenta | en_saqueador | a distancia (ballesta) | bandido con ballesta y capa de cuero |
| tormenta | en_vex_tormenta | volador eléctrico | espíritu con chispas |
| tormenta | en_bestia_tormenta | pesado embestidor (64×64) | bestia acorazada con cuernos |
| sangre | en_vindicador | melee con hacha | vindicador carmesí con hacha |
| sangre | en_bruja_sangre | a distancia (maldición) | hechicera con velo y orbe de sangre |
| sangre | en_murcielago | volador | murciélago grande de sangre |
| eclipse | en_piglin_dorado | pesado melee (64×64) | brute dorado con armadura de eclipse |
| eclipse | en_espectro | volador/teletransporte | espectro con túnica dorada y máscara |
| eclipse | en_llama_solar | volador, dispara rayos solares | llama dorada con corona |

Los enemigos de élite los crea el motor (tinte + escala), no hace falta hoja aparte.

### 2.3 Jefes — `A/sprites/bs_<id>.png|json` (8 jefes + 3 fases del final)
ids: `bs_rey_exanime`, `bs_coloso_magma`, `bs_reina_escarcha`, `bs_devorador_vacio`, `bs_ent_ancestral`, `bs_titan_tormenta`, `bs_matriarca_sangre`, `bs_guardian_eclipse`, `bs_cazador1`, `bs_cazador2`, `bs_cazador3`.
Celda 128×128 por defecto (pivote [64,124]); los muy grandes (coloso_magma, titan_tormenta, ent_ancestral, cazador3) pueden usar 192×160 (pivote [96,156]). Declara el tamaño real en el JSON.
Anims obligatorias (mismos nombres en todos):

| anim | n | fps | descripción |
|---|---|---|---|
| idle | 6 | 8 | respiración amenazante (loop) |
| walk | 8 | 10 | caminar/flotar/arrastrarse (loop) |
| windup1 / attack1 | 5 / 8 | 12 / 16 | ATAQUE 1 = golpe cuerpo a cuerpo básico (hit + box) |
| windup2 / attack2 | 5 / 8 | 12 / 16 | ATAQUE 2 = embestida/lanzamiento horizontal de largo alcance (hit + box) |
| windup3 / attack3 | 6 / 9 | 12 / 14 | ATAQUE 3 = salto/golpe de área en el suelo (hit + box grande) |
| cast | 8 | 12 | invocación o salva de proyectiles (rel = fotograma de liberación) |
| hurt | 2 | 10 | impacto leve |
| phase | 10 | 10 | rugido/transformación al pasar a fase enfurecida |
| intro | 14 | 10 | ENTRADA CINEMÁTICA específica de cada jefe (ver abajo) |
| death | 14 | 9 | muerte épica (colapso/desintegración) |

Concepto por jefe (el diseño debe leerse a primera vista, enorme, tenebroso, con curvas y detalle):
* **rey_exanime** (Soberano de las Catacumbas): rey no-muerto con corona rota, armadura de huesos, capa raída, espadón; intro: emerge del suelo de su sarcófago.
* **coloso_magma** (El corazón de la Forja): gólem de basalto con venas de lava, pecho abierto con núcleo ardiente, puños enormes; intro: se arma pieza a pieza desde la lava.
* **reina_escarcha**: reina de hielo con vestido de cristal, corona de carámbanos, cetro; flota apenas; intro: baja del techo envuelta en ventisca.
* **devorador_vacio** (El ojo que todo lo consume): ojo gigante flotante con boca de dientes, tentáculos y pupila púrpura; intro: se abre un portal/rasgadura y se asoma.
* **ent_ancestral**: árbol colosal podrido con rostro, ramas como brazos, hongos y musgo, raíces; intro: se levanta de la tierra (el bosque cobra vida).
* **titan_tormenta**: titán de metal oxidado y cobre con nubes y rayos en el cuerpo, martillo; intro: cae del cielo con un rayo.
* **matriarca_sangre**: vampiresa alada gótica, vestido rasgado, garras, alas de murciélago desplegables; intro: se materializa de una nube de murciélagos.
* **guardian_eclipse**: caballero dorado/negro con halo eclipsado (sol y luna), alabarda y escudo; intro: camina desde una puerta que se abre bruscamente.
* **cazador1 (I · El Cazador Pálido)**: cazador gótico delgado con sombrero de tres picos, gabardina, sierra-látigo y pistola; humano, menos grotesco. intro: surge de la niebla bajo la luna roja.
* **cazador2 (II · La Bestia)**: forma bestial deforme, cuerpo hinchado, pelo, garras, cuernos; más grotesco.
* **cazador3 (III · Dios Antiguo)**: ser cósmico gigante, múltiples ojos y tentáculos, halo de luna de sangre; el más grotesco y grande.

### 2.4 Atrezo y recogibles — `A/sprites/`
| archivo | celda | anims |
|---|---|---|
| prop_door | 32×48 | `closed` n1; `open` n6 fps10 sin loop; `open_idle` n1 (puerta de salida de sala, arco gótico; sin color de bioma específico, neutra de piedra y metal) |
| prop_portal | 48×64 | `idle` n8 fps10 loop (portal vertical, remolino claro/neutro blanquecino-azulado para tintar por color de bioma) |
| prop_altar | 32×48 | `idle` n6 fps8 loop (altar de bendiciones con orbe), `used` n1 (apagado) |
| prop_chest | 24×24 | `closed` n1; `open` n5 fps12 sin loop; `open_idle` n1 |
| prop_fountain | 32×40 | `idle` n8 fps8 loop (fuente de curación con luz verde-azulada) |
| prop_forge | 40×40 | `idle` n8 fps10 loop (yunque con brasas) |
| prop_merchant | 40×40 | `idle` n8 fps7 loop (mercader encapuchado tras un mostrador con mercancía) |
| prop_sanctuary | 64×64 | `idle` n8 fps8 loop (gran brasero/obelisco del Santuario para el menú de mejoras permanentes) |
| pick_gold | 8×8 | `idle` n4 fps10 loop (moneda girando) |
| pick_soul | 10×10 | `idle` n6 fps10 loop (alma azul-blanca llameante) |
| pick_heart | 10×10 | `idle` n2 fps4 loop (corazón carmesí pulsante) |
| pick_potion | 10×12 | `idle` n2 fps4 loop (poción de curación) |
| pick_relic | 16×16 | `idle` n6 fps8 loop (reliquia dorada con brillo) |
| prop_pot | 16×16 | `closed` n1; `break` n5 fps16 sin loop (vasija/barril rompible; neutra) |

### 2.5 Efectos y proyectiles — `A/fx/*.png|json`
Las hojas de FX usan pivote = centro de la celda (excepto cuando se diga lo contrario) y son **BLANCO/CLAROS NEUTROS con núcleo brillante** cuando se pueda, para que el motor los TIÑA con el color de la clase/elemento
(multiplicando). Para los que tengan color propio inconfundible (fuego, hielo, sangre, rayo) usa color propio.
| archivo | celda | anims (n fotogramas @fps) |
|---|---|---|
| fx_slash_sword | 64×64 | s1 5@24, s2 5@24, s3 6@22 (arcos de espada; s3 es el mayor) — blanco con núcleo |
| fx_slash_big | 96×96 | s1 6@22, s2 6@22, s3 7@20 (espadón/martillo/guadaña, arcos enormes) |
| fx_stab | 80×32 | s1 5@26, s2 5@26 (estocadas largas horizontales con estela) |
| fx_hit | 32×32 | spark 5@30, big 6@28, crit 6@28 (estrella grande), magic 5@28, shock 5@28, ice 5@28 |
| fx_blood | 48×48 | splat 6@24, mist 6@20 |
| fx_explosion | 96×96 | a 9@24 (explosión naranja), b 9@24 (explosión mágica blanca-azul para tintar) |
| fx_fire | 32×48 | burn 6@14 loop (llamas ardiendo), pillar 8@16 (pilar de fuego que se alza) |
| fx_ice | 48×64 | spike 7@16 (púa de hielo que brota), burst 8@20 (explosión de cristales), frozen 1 (bloque de hielo) |
| fx_lightning | 32×128 | bolt 5@28 (rayo vertical desde arriba, pivote en la base), ground 5@28 (impacto en suelo 32×128 también) |
| fx_thorn | 32×48 | vine 7@16 (enredadera con espinas que brota), bloom 8@12 (flor de curación) |
| fx_rock | 32×64 | pillar 8@16 (columna de roca que se alza), debris 6@18 |
| fx_star | 48×48 | burst 7@20 (explosión estelar), twinkle 4@10 loop |
| fx_void | 64×64 | hole 8@12 loop (agujero negro con anillos), rift 8@14 (grieta del vacío) |
| fx_holy | 48×128 | beam 8@18 (columna de luz sagrada desde arriba, pivote en la base) |
| fx_shadow | 48×48 | puff 7@18 (nube de humo púrpura), blade 5@26 (tajo fantasma) |
| fx_dust | 32×16 | run 5@20 (pivote abajo-centro), land 6@20, roll 5@20 |
| fx_heal | 24×32 | rise 8@14 (cruces verdes subiendo) |
| fx_shield | 48×48 | bubble 6@12 loop (burbuja/escudo de energía) |
| fx_whirl | 64×64 | spin 6@24 loop (anillo de torbellino de cuchillas) |
| fx_tele | 48×64 | out 8@22, in 8@22 (teletransporte: desvanecer / aparecer) |
| fx_shock | 128×32 | wave 7@22 (onda expansiva horizontal sobre el suelo, pivote abajo-centro) |
| fx_smoke | 64×64 | big 8@14 (humo/ceniza) |
| fx_ring | 96×96 | pulse 8@24 (anillo expansivo blanco) |
| fx_proj | 24×24 | UNA ANIM por proyectil, 4 fotogramas @16 loop, orientada a la DERECHA: arrow, dagger, fireball, iceshard, bolt, voidorb, bloodorb, leaf, star, blade, crescent, poison, magma, holy, spike, bone |

### 2.6 Tilesets — `A/tiles/tiles_<bioma>.png` (9: catacumbas, forja, helado, vacio, bosque, tormenta, sangre, eclipse, cazador)
PNG de **256×128** = 16 columnas × 8 filas de baldosas 16×16. NO hay JSON; el layout es fijo:

* Filas 0–2: terreno sólido con autotile de 4 vecinos. La columna = máscara `N=1, E=2, S=4, W=8` (bit a 1 si ese vecino es SÓLIDO). Las filas son 3 variantes (A,B,C) por máscara.
  Máscara 0 = bloque aislado, 15 = totalmente rodeado (relleno). Cuando el vecino N no es sólido, la cara superior lleva el borde de superficie (césped/escarcha/musgo/baldosa clara/sangre...). Las caras expuestas E/W/S llevan borde oscuro/sombra. Las variantes deben encajar entre sí sin costuras.
* Fila 3: columnas 0–3 = plataforma atravesable [suelta, cap izq, centro, cap der] (sólo ocupa los 6 px superiores de la baldosa); col 4 = pinchos hacia arriba, col 5 = pinchos hacia abajo (peligrosos); cols 6–7 = reservado/hazard brillante; cols 8–11 = pared de fondo (no sólida, oscura, 4 variantes que teselan); cols 12–15 = decoración de pared de fondo (arco, ventana con luz, columna, grieta).
* Fila 4: cols 0–3 = antorcha/llama de pared (4 fotogramas de animación, el motor añade luz); cols 4–7 = foco de luz alternativo del bioma (cristal/vela/linterna, 4 fotogramas); cols 8–15 = 8 elementos COLGANTES de techo (cadenas, raíces, estalactitas, tela...) 16×16 pegados al borde superior.
* Fila 5: 16 props de suelo (base en la parte inferior de la baldosa: huesos, hongos, hierbas, cristales, calaveras, rocas, barriles, charcos...).
* Fila 6: cols 0–7 = decoración de pared (estandartes, escudos, runas, calaveras, vitrales); cols 8–15 = reservado (vacío).
* Fila 7: reservado (vacío).
Estilo: cada bioma con su paleta/ambiente de la tabla de biomas; el terreno debe verse elegante, con textura rica (ladrillos, grietas, detalles) pero legible; el contraste entre el suelo caminable y el fondo debe ser claro.

### 2.7 Fondos parallax — `A/bg/bg_<bioma>_<0|1|2>.png` (9 biomas × 3 capas)
512×288, TESELABLES horizontalmente (el borde izquierdo continúa con el derecho). Capa 0 = lejana opaca (cielo/pared profunda con degradado, atmósfera, luna/sol/aurora/estrellas), capa 1 = media con transparencia (siluetas de arquitectura/árboles/montañas/estructuras con bruma), capa 2 = cercana con transparencia (columnas, ramas, cadenas, estalactitas, hojas; escasa, para dar profundidad; oscura). Mucha atmósfera; el centro-inferior debe quedar relativamente despejado para no estorbar la jugabilidad.

### 2.8 Interfaz — `A/ui/`
* `ui_logo.png` (~300×84): logotipo "SwordsmanMagic" en letras góticas pixeladas con filo/espada integrada y subtítulo "ETERNAL ABYSS"; dorado envejecido + sombra roja; transparente.
* `ui_title_<0..3>.png` 512×288: capas parallax de la pantalla de título (estilo Bloodborne/Yharnam: ciudad gótica victoriana en ruinas, catedral, gran luna roja con halo, niebla; 0 = cielo+luna opaca, 1 = silueta lejana, 2 = edificios medios con luces, 3 = primer plano con verja/puente y cuervos; las 1–3 transparentes y teselables en horizontal).
* `ui_panel.png` 32×32 (marco 9-slice, esquinas de 8 px, piedra oscura + filo dorado envejecido, centro semitransparente oscuro), `ui_panel_light.png` igual pero más claro (para tarjetas seleccionadas), `ui_panel_red.png` (alerta/jefe).
* `ui_btn.png` 3 estados horizontales (normal | hover | pressed) cada uno 48×20 (9-slice con 6 px de esquina); `ui_btn_round.png` 3 estados cada uno 40×40 (botón circular táctil: normal | pressed | disabled), en gris-hueso oscuro con filo, SIN icono (el motor dibuja el icono encima).
* Barras HUD: `ui_hp_frame.png` 104×14 y `ui_hp_fill.png` 100×10 (rojo, brillo, segmentos); `ui_ult_frame.png` 84×10 y `ui_ult_fill.png` 80×6 (dorado/azul); `ui_boss_frame.png` 256×18 y `ui_boss_fill.png` 244×8 (adornada gótica).
* `ui_cursor.png` 16×16 (puntero de selección), `ui_arrow.png` 8×8 (flecha de menú), `ui_vignette.png` 128×72 (viñeta oscura alpha, se estira), `ui_scanline.png` 4×4 (opcional).
* **Iconos**: `A/ui/icons.png` + `A/ui/icons.json`. Celdas 16×16, 16 columnas, todas las filas necesarias. JSON: `{"cell":16, "cols":16, "names":["attack","jump",...]}` (el índice = posición en `names`).
  Orden/nombres EXACTOS (en este orden):
  - UI (28): attack, jump, roll, pause, play, settings, sound_on, sound_off, music_on, music_off, back, close, lock, star, coin, soul, heart, potion, key, skull, relic, door, altar, forge, shop, fountain, chest, elite
  - Mapa/estado (12): boss, treasure, secret, map, burn, freeze, poison, bleed, shock, curse, shield, crown
  - Bendiciones (28), en este orden: b_filo, b_corazon, b_alas, b_furia, b_sangre, b_brasas, b_glacial, b_chispa, b_espinas, b_piedra, b_fantasma, b_doble_salto, b_critico, b_alma, b_fortuna, b_escudo_estelar, b_enfriamiento, b_habilidad, b_ejecutor, b_iman, b_venganza, b_segunda, b_onda, b_egida, b_sabio, b_gigante, b_sombra, b_eclipse
  - Habilidades por clase (40 = 10 clases × 4): para cada clase en orden paladin, shadow, flame, storm, frost, verdant, blood, earth, astral, steel: `s_<clase>_1`, `s_<clase>_2`, `s_<clase>_3`, `s_<clase>_4` (la 4 es la definitiva). Nombres de habilidades (para inspirar el icono):
    paladin: Lanza del Alba, Alas de Égida, Juicio del Alba, Amanecer Eterno · shadow: Paso Sombra, Hoja Fantasma, Danza de Cuchillas, Ejecución Dimensional · flame: Bola de Fuego, Muro de Fuego, Tornado Ígneo, Inferno Draconiano ·
    storm: Relámpago Veloz, Ráfaga Voltaica, Tormenta Eléctrica, Trueno Divino · frost: Esquirlas Glaciales, Prisión de Hielo, Ventisca, Cero Absoluto · verdant: Látigo de Espinas, Floración, Agarre de Raíces, Árbol del Mundo ·
    blood: Tajo Sangriento, Pacto de Sangre, Hoz Giratoria, Eclipse Carmesí · earth: Puño de Roca, Piel de Piedra, Terremoto, Cataclismo del Titán · astral: Estrella Fugaz, Pozo Gravitatorio, Paso Cósmico, Supernova · steel: Volea de Hojas, Guardia de Acero, Carga Forjada, Mil Espadas.
  - Reliquias de jefe (9): r_rey_exanime, r_coloso_magma, r_reina_escarcha, r_devorador_vacio, r_ent_ancestral, r_titan_tormenta, r_matriarca_sangre, r_guardian_eclipse, r_sello_final
  - Clases (10): c_paladin, c_shadow, c_flame, c_storm, c_frost, c_verdant, c_blood, c_earth, c_astral, c_steel (emblemas)
  Total 28+12+28+40+9+10 = 127 → 8 filas (128 huecos). Los iconos tienen contorno oscuro y rampa de color; legibles a 16 px.
* **Fuentes**: `A/font/font_s.png|json` (pequeña, celda 8×10) y `A/font/font_b.png|json` (grande gótica de títulos, celda 12×16). Glifos BLANCOS con contorno oscuro de 1 px horneado (el motor los tiñe). Juego de caracteres EXACTO en este orden (fila mayor, 16 por fila):
  `" !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~ÁÉÍÓÚÑáéíóúñüÜ¡¿·°«»…—♥★"`
  JSON: `{"cellW":8,"cellH":10,"cols":16,"chars":"<la cadena>","widths":[ancho de avance por glifo en px, mismo orden],"baseline":8,"spacing":1}`. Fuente proporcional (la "i" es estrecha). Debe verse nítida y elegante (la grande, estilo gótico/serif de Dark Souls).

## 3. Contrato de AUDIO — `A/audio/`

* Formato: OGG Vorbis. SFX mono 44.1 kHz (q4), en `A/audio/sfx/<nombre>.ogg`; música estéreo 44.1 kHz (q4) en `A/audio/music/<nombre>.ogg`.
* Normaliza: SFX con pico ≈ -3 dBFS; música ≈ -14 LUFS aprox (pico -2 dBFS). Sin clics (fade de 2–5 ms), sin recortes. Volúmenes relativos coherentes entre efectos.
* La música en bucle DEBE hacer loop sin costura (renderiza reverb/colas envolviendo el final al inicio y asegura continuidad de fase). Duración 40–70 s por pista.
* Estilo: oscuro, épico, gótico, orquestal-sintético (pads, cuerdas, coros sintéticos, órgano, campanas, percusión de guerra, sub-bajos), cada bioma con su identidad (modo, tempo y timbre propios).
  Síntesis por código con numpy (FM, aditiva, sustractiva, ruido filtrado, karplus-strong, convolución con respuestas impulsivas sintéticas, saturación suave, compresión). Máxima calidad: capas, envolventes cuidadas, estéreo amplio, reverb.
* Entregar además `A/audio/manifest.json` con la lista de todo lo generado: `{"sfx":{"nombre":duracion_seg,...},"music":{"nombre":{"dur":seg,"loop":true|false}}}`.

### Música (nombres exactos)
`mus_title` (menú principal, gótica, coro y órgano), `mus_sanctuary` (Santuario/hub, calmada y solemne), `mus_catacumbas`, `mus_forja`, `mus_helado`, `mus_vacio`, `mus_bosque`, `mus_tormenta`, `mus_sangre`, `mus_eclipse` (una por bioma, ambientales con pulso de acción moderado),
`mus_boss_a` (jefes de los 4 primeros biomas en el orden de la tabla), `mus_boss_b` (jefes 5–8), `mus_final_1`, `mus_final_2`, `mus_final_3` (El Cazador, escalando en intensidad y grotesco), `mus_victory` (NO loop, 14–20 s), `mus_gameover` (NO loop, 8–12 s), `mus_credits` (loop 60 s, emotiva).

### Efectos (nombres exactos; las listas con `_1.._3` son variantes para no repetir)
* **Interfaz**: ui_click, ui_confirm, ui_back, ui_error, ui_open, ui_pick_upgrade, ui_unlock, ui_start_run, ui_pause, ui_hover.
* **Mundo**: coin, soul, heart, potion, door_open, door_locked, portal_enter, chest_open, shop_buy, forge_anvil, altar_bless, fountain_heal, spikes, break_pot, room_clear, room_lock, secret, relic_get.
* **Jugador**: step_1, step_2, step_3, jump, double_jump, land, roll, hurt_1, hurt_2, death, heal, block, parry, heartbeat, level_up, ult_ready, skill_fail, cd_ready, ult_charge, time_stop.
* **Armas** (swing = el aire, 1..3 por golpe del combo): swing_sword_1..3, swing_great_1..3, swing_dagger_1..3, swing_stab_1..3, swing_scythe_1..3, swing_hammer_1..3, swing_air. 
  **Impactos**: hit_flesh_1..3, hit_metal_1..2, hit_crit, hit_magic, hit_stone, hit_bone, hit_ice, hit_fire, hit_shock, hit_blood.
* **Habilidades por clase** (para cada clase c en paladin, shadow, flame, storm, frost, verdant, blood, earth, astral, steel): `sk_<c>_1`, `sk_<c>_2`, `sk_<c>_3` (lanzamiento de cada habilidad, 0.5–1.5 s, con identidad del elemento), `sk_<c>_hit` (impacto del elemento, 0.3–0.8 s) y `ult_<c>` (definitiva, 3–5 s épica, con crescendo y golpe final).
* **Enemigos**: en_alert, en_hurt_1, en_hurt_2, en_die_bone, en_die_flesh, en_die_ghost, en_die_slime, en_die_magic, en_attack_melee, en_cast, en_flap, en_dash, en_step_heavy, arrow_shot, spit, magic_bolt, explosion_small, explosion_big, proj_hit.
* **Jefes** (para cada jefe b en rey_exanime, coloso_magma, reina_escarcha, devorador_vacio, ent_ancestral, titan_tormenta, matriarca_sangre, guardian_eclipse, cazador): `bs_<b>_intro` (2–4 s, la entrada cinemática con sonido propio y distinto), `bs_<b>_roar`, `bs_<b>_atk1`, `bs_<b>_atk2`, `bs_<b>_atk3`, `bs_<b>_cast`, `bs_<b>_hurt`, `bs_<b>_phase` (transformación/enfurecer), `bs_<b>_death` (3–5 s), `bs_<b>_step` (paso pesado o ruido de desplazamiento). Cada jefe con timbre propio (huesos y óxido, magma y metal, cristal y viento, vacío y susurros, madera y crujidos, trueno y metal, sangre y alas, campanas y coros solares, bestia/dios antiguo para el Cazador). Genéricos: boss_title (golpe de título), boss_bar, boss_defeat (sting de victoria).
* **Ambiente** (loops 8–12 s, bajo volumen): amb_catacumbas, amb_forja, amb_helado, amb_vacio, amb_bosque, amb_tormenta, amb_sangre, amb_eclipse, amb_cazador.

## 4. Diseño de juego (para el motor; referencia de los generadores)

* Run: se eligen 3 biomas (bifurcación con puertas), cada uno con ~5 salas + jefe. Tipos de sala: combate, élite, bendición (altar: elige 1 de 3), forja (mejorar arma), mercader, fuente de curación, tesoro (cofre), secreta. Cada puerta de salida muestra el icono de la recompensa (estilo Hades).
* Progreso permanente: Almas → Santuario (mejoras permanentes + desbloqueo de clases). Reliquias de jefes (8) → Sello → jefe final El Cazador (3 fases).
* Combate: combo de 3 golpes, esquive con invencibilidad, 4 habilidades por clase (3 + definitiva con cinemática), hitstop, temblor de pantalla, daño flotante, estados (quemar, congelar, veneno, sangrado, descarga).
