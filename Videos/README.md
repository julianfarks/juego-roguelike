# Tráileres de SwordsmanMagic: Eternal Abyss

Dos tráileres de **40 s exactos**, hechos solo con **gameplay real** del juego (modo PC limpio), la **música y los efectos originales** del juego y textos animados con la **tipografía pixel del propio juego**.

| Archivo | Idioma | Duración | Resolución | FPS | Vídeo / Audio |
|---|---|---|---|---|---|
| `Trailer_Spanish.mp4` | Español | 40,000 s (2400 fotogramas) | 1920×1080 (16:9) | 60 | H.264 High, yuv420p / AAC estéreo 48 kHz |
| `Trailer_English.mp4` | English | 40,000 s (2400 fotogramas) | 1920×1080 (16:9) | 60 | H.264 High, yuv420p / AAC estéreo 48 kHz |

Descarga directa (archivos del repositorio, rama `main`):
- https://github.com/julianfarks/juego-roguelike/raw/main/Videos/Trailer_Spanish.mp4
- https://github.com/julianfarks/juego-roguelike/raw/main/Videos/Trailer_English.mp4

## Contenido (todo verificado con el código del juego)
- **10 clases** (cada una con 3 habilidades + 1 definitiva), **9 biomas**, **9 jefes** (8 de bioma + El Cazador, con 3 formas), **200 bendiciones** con **20 sinergias especiales** (ver `docs/BENDICIONES.md`), parry perfecto con contraataque.
- Se muestran ofertas de bendiciones en el altar, la lista de bendiciones activas y su pestaña de sinergias, el aviso real «¡Sinergia activada!», un parry perfecto contra el Rey Exánime con su «¡Contra!» y la sinergia Infierno (Brasas Eternas + Llama Voraz + Contagio Ígneo) propagando fuego. No se afirman cifras de enemigos, objetos ni fechas/tiendas/enlaces de lanzamiento.

| Tiempo | Texto ES | Texto EN |
|---|---|---|
| 0,4–2,4 | CADA DESCENSO ES DISTINTO | NO TWO DESCENTS ALIKE |
| 2,8–5,4 | EMPUÑA LA ESPADA. / DOMINA LA MAGIA. | WIELD THE SWORD. / MASTER THE MAGIC. |
| 5,6–8,0 | ROGUELIKE DE ACCIÓN EN PIXEL ART | PIXEL-ART ACTION ROGUELIKE |
| 8,2–11,4 | ATRAVIESA 9 BIOMAS | CROSS 9 BIOMES |
| 11,6–15,0 | ENFRÉNTATE A 9 JEFES | FACE 9 BOSSES |
| 15,2–18,4 | 10 ESPADACHINES / CADA UNO CON SU ESTILO | 10 SWORDSMEN / 10 WAYS TO FIGHT |
| 18,6–21,4 | 200 BENDICIONES / INFINITAS FORMAS DE LUCHAR | 200 BLESSINGS / ENDLESS WAYS TO FIGHT |
| 21,6–25,4 | 20 SINERGIAS ESPECIALES / CADA ELECCIÓN CAMBIA TU PARTIDA | 20 SPECIAL SYNERGIES / EVERY PICK CHANGES YOUR RUN |
| 25,8–29,0 | DOMINA EL MOMENTO / CONVIERTE LA DEFENSA EN ATAQUE | MASTER THE TIMING / TURN DEFENSE INTO OFFENSE |
| 29,4–33,0 | COMBINA BENDICIONES. / DESATA SINERGIAS DEVASTADORAS | COMBINE BLESSINGS. / UNLEASH POWERFUL SYNERGIES |
| 31,2–33,9 | SINERGIA · INFIERNO / Brasas Eternas + Llama Voraz + Contagio Ígneo | SYNERGY · INFIERNO / (mismos nombres del juego) |
| 34,2–37,0 | DESATA TUS DEFINITIVAS | UNLEASH YOUR ULTIMATES |
| 38,3–40 | Logo oficial + DESAFÍA EL ABISMO / PC · ANDROID | Logo + DARE TO DESCEND / PC · ANDROID |

Escenas nuevas (18,4–34 s): altar con ofertas de distintas rarezas y categorías → lista de activas y sinergias → «¡Sinergia activada!» → parry perfecto (jefe prepara el ataque, parry, destello real, «¡Contra!») ×2 → Infierno ×3. Las escenas nuevas se graban con `TrailerProbe` (solo captura): invoca las pantallas y reglas reales del juego; el parry lo ejecuta el bot.

Los textos van arriba o sobre una banda oscura para no tapar al personaje ni los carteles del propio juego. El tráiler en inglés muestra la interfaz del juego en español (limitación honesta: el juego no tiene idioma inglés).


Los cortes van sincronizados a la rejilla de 0,4 s de `mus_boss_a` (≈150 BPM, medido por análisis de onsets). Las entradas de texto/logo llevan zoom, temblor de pantalla y destellos.

## Herramientas
Java (motor del propio juego, banco de pruebas headless `PC/run.sh --headless --pc --record`), ffmpeg 6.1 (libx264, aac), Python 3 + numpy + Pillow. Escalado siempre por **vecino más cercano** (480×270 → ×4 exacto = 1920×1080). Sin locución: texto animado + diseño de sonido con sfx del juego.

## Cómo regenerarlos
```bash
bash Videos/source/capture_clips.sh              # 1) graba las escenas reales (≈1 h, 2 CPU) en Videos/source/clips
bash Videos/source/render_all.sh                 # 2) monta y renderiza ES + EN en Videos/
```
- `source/capture_clips.sh`: lanza el juego en modo PC (sin controles táctiles ni depuración) y graba cada escena con `--record` (frames nativos 480×270 → 1080p) más un registro de los sfx reales de esa escena.
- `source/edit_trailer.py`: montaje (zoom, temblor, destellos, textos animados, título) y codificación; `source/storyboard.py`: guion, tiempos y textos ES/EN; `source/pixtext.py`: texto con la fuente `font_b` del juego; `source/mixer.py`: mezcla de audio con los `.ogg` originales (no se modifican).
- El bot de juego (`DebugBot`) solo controla al personaje; nada de depuración se dibuja. `BOT_ULT=1` solo carga la definitiva para poder mostrarla.

## Límites honestos
- Gameplay grabado en el banco headless del PC (no en un móvil Android ni en hardware Windows real).
- El parry de las escenas nuevas lo ejecuta el bot de pruebas; las ofertas y la build del altar se conceden con la herramienta de captura para poder mostrarlas.
- Sin locución profesional: solo texto y sonido.
