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

| Tiempo | Escena | Texto ES / EN |
|---|---|---|
| 0–2,4 s | Gancho: aparición del Devorador del Vacío y definitivas (Señor de las Llamas, Vagabundo Estelar) | BAJA AL ABISMO / DESCEND INTO THE ABYSS |
| 2,4–8 s | Presentación: Paladín vs. Rey Exánime, Reina de la Escarcha, Forja Infernal | ESPADA. MAGIA. ABISMO. / UN ROGUELIKE DE ACCIÓN EN PIXEL ART |
| 8–15,2 s | Biomas y jefes (Vacío, Bosque Podrido, Ent Ancestral, Titán de la Tormenta, Matriarca de Sangre, Guardián del Eclipse) | 9 BIOMAS MORTALES / 9 JEFES COLOSALES |
| 15,2–18,4 s | Pantalla de preparación de 4 clases | 10 CLASES |
| 18,4–22,4 s | Elección de bendición, mercader, forja, cámara secreta | 28 BENDICIONES · TIENDAS · FORJA · SECRETOS |
| 22,4–27,2 s | Clímax: definitivas contra jefes (Coloso de Roca, Segador, Guardián Glacial, Tempestad, Llamas, Estelar) | SOBREVIVE · DERROTA AL CAZADOR |
| 27,2–30 s | Logo oficial (`ui_logo.png`) y llamada final | ¿TE ATREVES A BAJAR? / DARE TO DESCEND? |

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
