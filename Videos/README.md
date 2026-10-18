# Tráileres de SwordsmanMagic: Eternal Abyss

Dos tráileres de **30 s exactos**, hechos solo con **gameplay real** del juego (modo PC limpio), la **música y los efectos originales** del juego y textos animados con la **tipografía pixel del propio juego**.

| Archivo | Idioma | Duración | Resolución | FPS | Vídeo / Audio |
|---|---|---|---|---|---|
| `Trailer_Spanish.mp4` | Español | 30,000 s (1800 fotogramas) | 1920×1080 (16:9) | 60 | H.264 High, yuv420p / AAC estéreo 48 kHz |
| `Trailer_English.mp4` | English | 30,000 s (1800 fotogramas) | 1920×1080 (16:9) | 60 | H.264 High, yuv420p / AAC estéreo 48 kHz |

Descarga directa (archivos del repositorio, rama `main`):
- https://github.com/julianfarks/juego-roguelike/raw/main/Videos/Trailer_Spanish.mp4
- https://github.com/julianfarks/juego-roguelike/raw/main/Videos/Trailer_English.mp4

## Contenido (todo verificado con el código del juego)
- **10 clases** (cada una con 3 habilidades + 1 definitiva), **9 biomas**, **9 jefes** (8 de bioma + El Cazador, con 3 formas), **28 bendiciones**.
- Se muestran tienda del mercader, forja, bendiciones y cámara secreta. No se afirman cifras de enemigos, objetos ni fechas/tiendas/enlaces de lanzamiento.

| Tiempo | Texto ES | Texto EN |
|---|---|---|
| 0,4–2,4 | CADA DESCENSO ES DISTINTO | NO TWO DESCENTS ALIKE |
| 2,8–5,4 | EMPUÑA LA ESPADA. / DOMINA LA MAGIA. | WIELD THE SWORD. / MASTER THE MAGIC. |
| 5,6–8,0 | ROGUELIKE DE ACCIÓN EN PIXEL ART | PIXEL-ART ACTION ROGUELIKE |
| 8,2–11,4 | ATRAVIESA 9 BIOMAS | CROSS 9 BIOMES |
| 11,6–15,0 | ENFRÉNTATE A 9 JEFES | FACE 9 BOSSES |
| 15,2–18,4 | 10 ESPADACHINES / CADA UNO CON SU ESTILO | 10 SWORDSMEN / 10 WAYS TO FIGHT |
| 18,4–20,2 | 28 BENDICIONES | 28 BLESSINGS |
| 20,4–22,3 | MEJORA · COMPRA · DESCUBRE | UPGRADE · SHOP · DISCOVER |
| 22,6–24,6 | DESATA TUS DEFINITIVAS | UNLEASH YOUR ULTIMATES |
| 24,8–27,0 | LLEGA HASTA EL CAZADOR PÁLIDO | REACH THE PALE HUNTER |
| 27,2–30 | Logo oficial + DESAFÍA EL ABISMO / PC · ANDROID | Logo + DARE TO DESCEND / PC · ANDROID |

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
- Sin locución profesional: solo texto y sonido.
