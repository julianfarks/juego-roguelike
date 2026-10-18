package com.julianfarks.roguelike.core;

/**
 * Contrato entre el motor (paquete core, Java puro SIN imports de android.* ni java.awt.*)
 * y cada plataforma (Android = com.julianfarks.roguelike.android.*, escritorio = tools/desktop).
 *
 * Coordenadas: "pixeles virtuales". El motor dibuja en una pantalla virtual de alto fijo {@link #VIEW_H} (270)
 * y ancho variable (viewW, 480..640, segun la relacion de aspecto del telefono). La plataforma escala la pantalla
 * virtual a la pantalla real con vecino mas cercano (sin suavizado), con escala entera si cabe o fraccional, centrada.
 */
public interface Platform {
    int VIEW_H = 270;

    /** Imagen cargada o creada. La plataforma guarda su objeto nativo en {@link #handle}. */
    final class Img {
        public final int w, h;
        public final Object handle;
        public Img(int w, int h, Object handle) { this.w = w; this.h = h; this.handle = handle; }
    }

    /** Banderas de dibujo (se pueden combinar con |). */
    int FLIP_X = 1;      // espejo horizontal (respecto al rectangulo destino)
    int ADD = 2;         // mezcla aditiva (brillos, luces, fuego)
    int TINT = 4;        // multiplica los colores por el argb de "tint" (el alfa de tint NO se usa; usa el parametro alpha)
    int FLASH = 8;       // dibuja la silueta (alfa de la imagen) en el color solido de "tint" (destello blanco de golpe)

    interface Gfx {
        /** Rellena toda la pantalla virtual con un color ARGB opaco. */
        void clear(int argb);
        /**
         * Dibuja el recorte (sx,sy,sw,sh) de la imagen en el rectangulo destino (dx,dy,dw,dh) (puede escalar, vecino mas cercano).
         * alpha 0..1, flags = FLIP_X | ADD | TINT | FLASH. Si img es null no hace nada.
         */
        void image(Img img, int sx, int sy, int sw, int sh, float dx, float dy, float dw, float dh, int flags, int tint, float alpha);
        /** Igual que image pero rotada angle radianes (sentido horario en pantalla) alrededor del centro del rectangulo destino. */
        void imageRot(Img img, int sx, int sy, int sw, int sh, float dx, float dy, float dw, float dh, float angle, int flags, int tint, float alpha);
        /** Rectangulo relleno. argb con alfa propio; add = mezcla aditiva. */
        void rect(float x, float y, float w, float h, int argb, boolean add);
        /** Linea de grosor "thick" px. */
        void line(float x1, float y1, float x2, float y2, float thick, int argb, boolean add);
        /** Circulo relleno (aprox. pixelada ok). */
        void circle(float cx, float cy, float r, int argb, boolean add);
        /** Recorte rectangular (en pixeles virtuales); clipEnd() lo restaura (anidable como pila). */
        void clipBegin(float x, float y, float w, float h);
        void clipEnd();
        /** Transformacion global opcional para temblor/zoom de camara: todo lo que se dibuje despues se traslada y escala. Pila. */
        void pushTransform(float tx, float ty, float scale);
        void popTransform();
    }

    interface Audio {
        /** Precarga efectos: nombres sin extension; archivo assets/audio/sfx/<nombre>.ogg. Puede ser asincrono. */
        void preloadSfx(String[] names);
        /** Reproduce un efecto. vol 0..1, pitch 0.5..2 (1 = normal). pan -1..1. Si no existe, no hace nada (nunca lanza). */
        void sfx(String name, float vol, float pitch, float pan);
        /** Musica de fondo assets/audio/music/<name>.ogg, con fundido cruzado de fadeMs. loop=false para stings. Si ya suena la misma, no reinicia. */
        void music(String name, boolean loop, float vol, int fadeMs);
        void stopMusic(int fadeMs);
        /** Ambiente en bucle (capa aparte, bajo volumen) assets/audio/sfx/<name>.ogg o music; null para detener. */
        void ambient(String name, float vol);
        void setMusicVolume(float v);
        void setSfxVolume(float v);
        void pauseAll();
        void resumeAll();
    }

    interface Store {
        String get(String key, String def);
        void put(String key, String value);
        /** Persiste de verdad (SharedPreferences.apply / archivo). */
        void commit();
    }

    // --- recursos ---
    /** Carga assets/<path> (PNG). null si no existe. */
    Img loadImage(String path);
    /** Crea una imagen desde pixeles ARGB (para luces, vineta, etc.). */
    Img createImage(int w, int h, int[] argbPixels);
    /** Lee los pixeles ARGB de una imagen (longitud w*h). */
    int[] pixels(Img img);
    /** Carga un archivo de texto de assets/<path> (UTF-8) o null si no existe. */
    String loadText(String path);
    /** Lista de nombres de archivo dentro de la carpeta de assets (no recursivo); vacio si no existe. */
    String[] list(String dir);

    /**
     * Ajustes de video del escritorio (ventana, resolucion, FPS...). Solo existe en PC: Android devuelve null
     * y el menu "Video y graficos" no se muestra. El motor guarda los valores elegidos en {@link VideoCfg}.
     */
    interface Video {
        /** Resoluciones de pantalla completa disponibles en el monitor, de menor a mayor: {ancho, alto}. */
        int[][] resolutions();
        /** Resolucion nativa del monitor {ancho, alto}. */
        int[] nativeRes();
        /** Tamano de ventana predeterminado para este monitor {ancho, alto}. */
        int[] defaultRes();
        /** Frecuencia de refresco del monitor en Hz (0 si se desconoce). */
        int refreshHz();
        /** Aplica la configuracion a la ventana en marcha. false si el sistema no pudo (se queda como estaba). */
        boolean apply(VideoCfg c);
        /** FPS medidos en el ultimo segundo. */
        int measuredFps();
    }

    /** true en PC (Windows): no hay pantalla tactil; se juega con teclado, raton y mando. */
    default boolean isDesktop() { return false; }
    /** Ajustes de video; null si la plataforma no los ofrece (Android). */
    default Video video() { return null; }

    Gfx gfx();
    Audio audio();
    Store store();
    void log(String msg);
    /** Milisegundos monotonicos. */
    long nowMs();
    /** Vibracion corta (ms); ignorable en escritorio. */
    void vibrate(int ms);
    /** Cierra la app. */
    void quit();

    // --- lo que el motor expone a la plataforma ---
    int ACTION_DOWN = 0, ACTION_MOVE = 1, ACTION_UP = 2;

    interface GameLoop {
        void init(Platform p);
        /** viewW en pixeles virtuales (480..640); el alto es siempre VIEW_H. */
        void resize(int viewW);
        /** Igual, pero la plataforma tambien indica el alto virtual (270..320, ver ViewSize). Por defecto solo cambia el ancho. */
        default void resize(int viewW, int viewH) { resize(viewW); }
        /** Paso fijo de 1/60 s. */
        void update(float dt);
        void render(Gfx g);
        /** Toque multitouch en coordenadas virtuales. id = pointerId. */
        void touch(int id, int action, float x, float y);
        /** Teclado (solo escritorio/pruebas). Codigos: usa los ASCII en mayuscula para letras ('A'..'Z'), 32 espacio, 10 enter, 27 esc, 37/38/39/40 flechas, 16 shift. */
        void key(int code, boolean down);
        /** Boton Atras: devuelve true si el motor lo consumio. */
        boolean back();
        void pause();
        void resume();
    }
}
