# SwordsmanMagic: Eternal Abyss — versión de PC (Windows)

## Jugar
Descomprime `SwordsmanMagic-Windows.zip` y ejecuta `SwordsmanMagic.exe`. Incluye su propio Java y todos los recursos.
Los datos (partidas, ajustes, `log.txt`) se guardan en `%APPDATA%\SwordsmanMagic-EternalAbyss\`, separados de los de Android.

Controles: teclado y ratón (menús) o mando Xbox/compatible con XInput (los de PlayStation/Switch funcionan con Steam Input o DS4Windows).
Se reasignan en Opciones → «Teclado, ratón y mando». En PC no hay controles táctiles. **F11** o **Alt+Enter** alterna pantalla completa.
Al perder el foco la partida se pausa.

## Opciones → Vídeo y gráficos
| Pestaña | Opción | Efecto real |
|---|---|---|
| Pantalla | Modo: ventana / pantalla completa / ventana sin bordes | Ventana normal; modo exclusivo del monitor (cambia su resolución); ventana sin bordes a tamaño nativo |
| | Resolución | Lista de modos del monitor + múltiplos exactos de 480×270 (1280×720, 1600×900, 1920×1080… si caben) |
| | Aplicar / Predeterm. | Si cambia modo o resolución pide confirmar durante 10 s; si no, **vuelve sola** a la configuración anterior |
| Rendimiento | Límite de FPS: 30 / 60 | El motor simula a 60 pasos fijos; 30 dibuja uno de cada dos |
| | V-Sync | Sincroniza la presentación con el sistema (`Toolkit.sync`); en Java2D depende del driver/compositor |
| | Mostrar FPS | Contador en pantalla (FPS reales dibujados) |
| | Escalado: entero / ajustado | Entero = píxeles perfectos con bandas negras; Ajustado = llena la ventana sin deformar (vecino más cercano) |
| Calidad | Baja / Media / Alta / Personalizada | Preajustes de las tres opciones siguientes |
| | Partículas 25 / 50 / 100 % | Menos partículas dibujadas |
| | Brillos e iluminación | Quita los halos aditivos (los más costosos de dibujar) |
| | Viñeta | Quita el oscurecimiento de bordes |

Limitaciones honestas (no se muestran opciones falsas): el motor simula a 60 Hz fijos, así que **más de 60 FPS no añadiría fluidez** y no se ofrece;
no hay sombras dinámicas en el motor, por eso no hay opción de sombras; la resolución interna es 270 px de alto por diseño (pixel art), el escalado
se hace siempre sin suavizado. Los ajustes se guardan en `pc_settings.properties` (clave `pc_video`) y no tocan los de Android.

## Compilar
Requisitos: JDK 22+ (con `jpackage`) y bash. `bash PC/build.sh` → `PC/build/dist/SwordsmanMagic/SwordsmanMagic.exe`.
Pasos: descarga las 3 librerías de ejecución para leer OGG (vorbisspi, jorbis, tritonus-share), compila `Shared` + `PC/src` con `javac`, crea el jar y
empaqueta con `jpackage` (JRE incluido, icono `PC/packaging/icon.ico`, generado con `PC/packaging/make_icon.py` desde el icono oficial).
Prueba de arranque sin ventana: `SwordsmanMagic.exe --selftest` (resultado en `%APPDATA%\SwordsmanMagic-EternalAbyss\selftest.txt`).

## Estructura
- `src/main/java/pc` — `PcMain` (arranque y bucle a 60 Hz), `PcWindow` (ventana/modos/escalado/entrada), `PcAudio` (mezclador con OGG), `PcXInput` (mando), `PcPlatform`, `PcVideo`.
- `src/main/java/desktop` — banco de pruebas de escritorio (capturas, bot, scripts) que usan `tools/tests`.
- `build.sh` — empaquetado; `run.sh` — banco de pruebas; `packaging/` — icono.
