# SwordsmanMagic: Eternal Abyss

Roguelike 2D de acción (pixel art), basado en el mod SwordmanMagic. Disponible para **Android** y **Windows (PC)** desde el mismo repositorio.
Creador: JulianFarKs. Ideas de Team TKD y Chernobyl. Basado en SwordmanMagic, un mod propio de Minecraft.

| Versión | Descarga | Cómo se genera |
|---|---|---|
| Android (APK) | [Releases → latest → SwordmanRogue.apk](https://github.com/julianfarks/juego-roguelike/releases/tag/latest) (también en `Android/apk/`) | workflow **Build APK (Android)** |
| Windows (EXE) | [Releases → latest-pc → SwordsmanMagic-Windows.zip](https://github.com/julianfarks/juego-roguelike/releases/tag/latest-pc) (y artefacto del workflow) | workflow **Build EXE (Windows PC)** |

Android: abrir el APK en el móvil y permitir "instalar apps desconocidas".
Windows: descomprimir el ZIP y ejecutar `SwordsmanMagic.exe` (incluye su propio Java; no hay que instalar nada). Más detalles en [PC/README.md](PC/README.md).

## Estructura del repositorio

```
Android/   proyecto Gradle de Android (app, manifest, recursos del launcher, keystore, apk/)
PC/        lanzador de Windows: ventana, audio, mando, vídeo; build.sh (EXE), run.sh (banco de pruebas), icono
Shared/    motor del juego en Java puro (src/.../core) y todos los recursos (assets: sprites, audio, idiomas)
tools/     generadores de arte/audio/idiomas y pruebas (se ejecutan en PC con Java/Python)
docs/      documentación y capturas
.github/workflows/   android.yml (APK) y pc.yml (EXE)
```

El motor (`Shared/src/main/java/com/julianfarks/roguelike/core`) **no importa nada de Android ni de AWT**: habla con cada plataforma a través de la interfaz `Platform`.
Android y PC solo aportan lo específico (pantalla, entrada, audio, almacenamiento). Los recursos están una sola vez en `Shared/assets` y los usan las dos.

## Compilar

**Android** (JDK 17 + Gradle 8.9 + Android SDK):
```
cd Android
gradle assembleDebug          # Android/app/build/outputs/apk/debug/app-debug.apk
```

**Windows / PC** (JDK 22 o superior con `jpackage`, y bash — Git Bash en Windows):
```
bash PC/build.sh              # PC/build/dist/SwordsmanMagic/SwordsmanMagic.exe
```
Para probar el motor sin ventana (Linux/Windows/macOS): `PC/run.sh --headless --pc --frames 600`.

GitHub Actions hace lo mismo en cada push: `android.yml` (solo si cambian `Android/`, `Shared/`) y `pc.yml` (solo si cambian `PC/`, `Shared/`).
Un cambio solo de PC no dispara ni afecta a la compilación de Android, y al revés.

## Novedades v2.0
- Arreglado el foso de pinchos (ya no te atrapa).
- Doble salto de serie (triple con la bendición) y bajar de plataformas con el botón ↓.
- Salas con piso superior, pozos-escalera, cámaras secretas, suelos y muros agrietados y puertas que se rompen golpeando o rodando.
- Cofres secretos: armas especiales, armas secundarias, granadas (5 tipos), escudos y pociones de vida.
- Escudo con bloqueo y PARRY (pulsa justo antes del golpe), 4 tipos de escudo.
- Dificultad Fácil / Normal / Difícil.
- Desbloqueos permanentes cada 50 enemigos derrotados.
- Opciones → Organizar controles (arrastra y cambia el tamaño de cada botón).
- Más animaciones: squash & stretch, estelas, partículas al matar, barras de vida de enemigos.
