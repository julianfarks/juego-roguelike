# Tráileres de SwordsmanMagic: Eternal Abyss (versión actual)

Tráiler rehecho desde cero con **gameplay real de la versión actual** (grabado el 20-10-2026 en el banco headless de PC, modo PC limpio: sin controles táctiles ni elementos de depuración).

| Archivo | Idioma | Duración | Resolución | FPS | Vídeo / Audio |
|---|---|---|---|---|---|
| `Trailer_ES.mp4` | Español (textos y juego en español) | 40,000 s (2400 fotogramas) | 1920×1080 (16:9) | 60 | H.264 High, yuv420p / AAC estéreo 48 kHz |
| `Trailer_EN.mp4` | English (textos y juego en inglés) | 40,000 s (2400 fotogramas) | 1920×1080 (16:9) | 60 | H.264 High, yuv420p / AAC estéreo 48 kHz |
| `Trailer_SinTextos.mp4` | Sin textos promocionales (juego en español), para futuras traducciones | 40,000 s | 1920×1080 | 60 | igual |

Verificado: los tres archivos se decodifican completos con ffmpeg sin errores, audio y vídeo duran 40,000 s.

## Mismas escenas en los dos idiomas
Cada escena se graba dos veces con la misma semilla (`BOT_SEED`): una con el juego en español y otra en inglés. La partida es **idéntica** (se comprueba comparando el registro de sonidos fotograma a fotograma: 0 diferencias en las 32 escenas). Así el tráiler inglés muestra la interfaz del juego en inglés con exactamente las mismas jugadas, cortes, música y efectos.

## Guion (40 s, cortes en la rejilla de 0,4 s de `mus_boss_a`, 150 BPM)
| Tiempo | Escenas reales | Texto ES | Texto EN |
|---|---|---|---|
| 0–4,8 | Salas sin enemigos de Catacumbas, Santuario del Eclipse y Bosque Podrido (antorchas, partículas) + logo oficial | — (logo) | — (logo) |
| 4,8–12 | Combate en 6 biomas con 6 clases (Bosque Podrido, Catacumbas, Forja Infernal, Santuario Helado, Fortaleza del Trueno, Abismo del Vacío): enemigos, trampas, plataformas, habilidades | EXPLORA LAS MAZMORRAS / 9 biomas · salas nuevas en cada partida · ESQUIVA, SALTA Y COMBATE | EXPLORE THE DUNGEONS / 9 biomes · new rooms every run · DODGE, LEAP AND FIGHT |
| 12–20 | Armas secundarias reales en uso (Chakram, Martillo de combate…), inventario rediseñado (ficha del arma, EN USO), sala despejada con los cofres y su flecha, pantalla de premio del cofre, altar de bendiciones, listas de bendiciones activas y sinergias | ENCUENTRA TU ARMA / 36 armas secundarias · CONSTRUYE TU ESTRATEGIA / 200 bendiciones · 23 sinergias | FIND YOUR WEAPON / 36 secondary weapons · BUILD YOUR STRATEGY / 200 blessings · 23 synergies |
| 20–28 | Élite, ataque cargado (Soberano de Acero), parry contra el Guardián del Eclipse, combate rápido en varios biomas | DOMINA EL COMBATE / Ataques cargados · parry · habilidades · 10 ESPADACHINES / CADA UNO CON SU ESTILO | MASTER THE FIGHT / Charged attacks · parries · skills · 10 SWORDSMEN / 10 WAYS TO FIGHT |
| 28–36,4 | Jefes: Coloso de Magma, Reina de la Escarcha, Matriarca de Sangre, Devorador del Vacío, El Cazador Pálido, Titán de la Tormenta; explosiones de la derrota real del Guardián del Eclipse | ENFRÉNTATE A LOS JEFES / 9 jefes · cada uno con sus propios ataques | FACE THE BOSSES / 9 bosses · each with its own attacks |
| 36,4–40 | Santuario del Eclipse oscurecido + logo oficial | DESAFÍA EL ABISMO | DARE TO DESCEND |

Cifras comprobadas en el código: 10 clases, 9 biomas, 9 jefes (8 de bioma + El Cazador con 3 formas), 36 armas secundarias, 200 bendiciones, 23 sinergias. No se anuncian fechas, tiendas, plataformas ni enlaces.

## Dirección técnica
- Escalado **solo por vecino más cercano y a escalas enteras** del píxel nativo (480×270 → ×4 = 1080p; acercamientos a ×5): los sprites nunca se deforman ni se emborronan. Paneos en múltiplos de 4 px.
- Textos con la fuente pixel del propio juego (`font_b`), a escala entera; si una línea no cabe baja a la siguiente escala entera (ninguna se sale de pantalla). En gameplay van arriba; sobre las pantallas de interfaz, abajo sobre una placa oscura.
- Música original del juego: `mus_title` (introducción atmosférica) → `mus_boss_a` (entra con el primer combate). Efectos: los sfx reales registrados durante cada escena grabada + golpes de cierre/título. Misma mezcla en las tres versiones.
- `clipmetrics.py` ajusta el inicio de algunos planos (±0,6 s, ±1,5 s en jefes) para evitar destellos blancos de pantalla completa.

## Escenas preparadas con `TrailerProbe` (solo para grabar)
Usa pantallas y reglas reales del juego; solo coloca una situación repetible: `chest` (combate real; el bot abre los cofres de la ronda), `arsenal` (cada 2,5 s se equipa otra arma secundaria real), `charge` (el bot mantiene el ataque ~1 s junto a un enemigo y suelta), `inv` (abre el inventario y recorre pestañas), `bless` (ofertas reales del altar y listas), `parry` (el bot hace parry y contraataca), `calm`/`still` (salas sin enemigos para el ambiente).

## Cómo regenerarlos
```bash
bash Videos/source/capture_clips.sh      # graba ES y EN (≈1 h; secuencial)
bash Videos/source/render_all.sh         # monta Trailer_ES, Trailer_EN y Trailer_SinTextos (≈15 min)
```

## Límites honestos
- Gameplay grabado en el banco headless del PC (no en un móvil Android ni en hardware Windows real); lo juega el bot de pruebas (con invulnerabilidad para que las escenas sean repetibles; no se muestra ninguna victoria falsa).
- Sin locución: solo texto y sonido, por lo que no hay subtítulos.
- La versión sin textos usa el juego en español.
