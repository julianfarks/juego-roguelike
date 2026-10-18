package com.julianfarks.roguelike.core;

/**
 * Ajustes de video y graficos de la version de PC. Se guardan en {@link Platform.Store} bajo la clave "pc_video"
 * (en PC el Store es un archivo propio del escritorio, asi que nunca se mezcla con los ajustes de Android).
 * Los valores estaticos {@link #particleMul}, {@link #lights} y {@link #vignette} son los que leen Particles, UI y Level;
 * por defecto equivalen a calidad Alta (= comportamiento original), de modo que Android no cambia.
 */
public final class VideoCfg {
    public static final int MODE_WINDOW = 0, MODE_FULL = 1, MODE_BORDERLESS = 2;
    public static final int Q_LOW = 0, Q_MED = 1, Q_HIGH = 2, Q_CUSTOM = 3;
    public static final int[] FPS_OPTIONS = {30, 60};
    public static final int[] PARTICLE_OPTIONS = {25, 50, 100};     // % de particulas

    /** Efectos activos en este momento (los consulta el motor). */
    public static float particleMul = 1f;
    public static boolean lights = true, vignette = true;
    /** Configuracion en uso (la que esta aplicada y guardada). */
    public static VideoCfg cur = new VideoCfg();

    public int mode = MODE_WINDOW;
    public int resW = 1280, resH = 720;      // tamano de la ventana / modo de pantalla completa
    public int fps = 60;                     // limite de FPS (30 o 60)
    public boolean vsync = true;
    public boolean showFps = false;
    public int scaleMode = 0;                // 0 = entero (pixel art nitido), 1 = ajustado a la ventana (fraccional)
    public int quality = Q_HIGH;
    public int particles = 100;              // % de particulas
    public boolean light = true, vig = true;

    public VideoCfg copy() {
        VideoCfg c = new VideoCfg();
        c.set(this);
        return c;
    }

    public void set(VideoCfg o) {
        mode = o.mode; resW = o.resW; resH = o.resH; fps = o.fps; vsync = o.vsync; showFps = o.showFps; scaleMode = o.scaleMode;
        quality = o.quality; particles = o.particles; light = o.light; vig = o.vig;
    }

    public static VideoCfg defaults() { return new VideoCfg(); }

    /** Ajustes que obligan a reconfigurar la ventana (y por tanto piden confirmacion). */
    public boolean sameDisplay(VideoCfg o) {
        return mode == o.mode && resW == o.resW && resH == o.resH;
    }

    public boolean same(VideoCfg o) {
        return sameDisplay(o) && fps == o.fps && vsync == o.vsync && showFps == o.showFps && scaleMode == o.scaleMode
                && quality == o.quality && particles == o.particles && light == o.light && vig == o.vig;
    }

    /** Fija los tres ajustes finos segun el preset (Baja/Media/Alta). */
    public void applyPreset(int q) {
        quality = q;
        switch (q) {
            case Q_LOW: particles = 25; light = false; vig = false; break;
            case Q_MED: particles = 50; light = true; vig = true; break;
            default: quality = Q_HIGH; particles = 100; light = true; vig = true; break;
        }
    }

    /** Si los ajustes finos coinciden con un preset lo devuelve; si no, Personalizada. */
    public void syncPreset() {
        for (int q = Q_LOW; q <= Q_HIGH; q++) {
            VideoCfg t = new VideoCfg();
            t.applyPreset(q);
            if (t.particles == particles && t.light == light && t.vig == vig) { quality = q; return; }
        }
        quality = Q_CUSTOM;
    }

    /** Vuelca los efectos a los valores que lee el motor. */
    public void pushEffects() {
        particleMul = Mth.clamp(particles / 100f, 0.1f, 1f);
        lights = light;
        vignette = vig;
    }

    // ------------------------------------------------------------------ persistencia
    private static final String KEY = "pc_video";

    public String serialize() {
        return "mode=" + mode + ";w=" + resW + ";h=" + resH + ";fps=" + fps + ";vsync=" + (vsync ? 1 : 0) + ";showFps=" + (showFps ? 1 : 0)
                + ";scale=" + scaleMode + ";q=" + quality + ";part=" + particles + ";light=" + (light ? 1 : 0) + ";vig=" + (vig ? 1 : 0);
    }

    public static VideoCfg parse(String raw) {
        VideoCfg c = new VideoCfg();
        if (raw == null || raw.isEmpty()) return c;
        for (String kv : raw.split(";")) {
            int e = kv.indexOf('=');
            if (e <= 0) continue;
            String k = kv.substring(0, e);
            int v;
            try { v = Integer.parseInt(kv.substring(e + 1).trim()); } catch (NumberFormatException ex) { continue; }
            switch (k) {
                case "mode": c.mode = Mth.clamp(v, 0, 2); break;
                case "w": c.resW = Mth.clamp(v, 640, 7680); break;
                case "h": c.resH = Mth.clamp(v, 360, 4320); break;
                case "fps": c.fps = v <= 30 ? 30 : 60; break;
                case "vsync": c.vsync = v != 0; break;
                case "showFps": c.showFps = v != 0; break;
                case "scale": c.scaleMode = v == 1 ? 1 : 0; break;
                case "q": c.quality = Mth.clamp(v, 0, 3); break;
                case "part": c.particles = v <= 25 ? 25 : (v <= 50 ? 50 : 100); break;
                case "light": c.light = v != 0; break;
                case "vig": c.vig = v != 0; break;
                default: break;
            }
        }
        return c;
    }

    /** Lee la configuracion guardada, la deja como actual y activa los efectos. Solo debe llamarse en plataformas con video(). */
    public static VideoCfg load(Platform p) {
        VideoCfg c = parse(p.store().get(KEY, ""));
        cur = c.copy();
        c.pushEffects();
        return c;
    }

    public static void save(Platform p, VideoCfg c) {
        cur = c.copy();
        p.store().put(KEY, c.serialize());
        p.store().commit();
    }
}
