package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/** Fachada de audio: respeta opciones, pitch aleatorio, pan por posicion. */
public final class Snd {
    private Snd() {}
    static Platform.Audio A;
    static final Rng rng = new Rng(12345);
    static String currentMusic = "";
    /** Musica de todos los menus (titulo, salon, preparacion, tienda...). La de partida (mus_sanctuary, biomas, jefes) no cambia. */
    public static final String MENU_MUSIC = "mus_menu";

    public static void init(Platform p) {
        A = p.audio();
        applyVolumes();
    }

    public static void applyVolumes() {
        if (A == null) return;
        A.setMusicVolume(Save.S.musicOn ? 0.8f : 0f);
        A.setSfxVolume(Save.S.sfxOn ? 1f : 0f);
    }

    /** Precarga todos los efectos listados en el manifiesto. */
    public static void preload(Platform p) {
        Map<String, Object> m = Json.parseObj(p.loadText("audio/manifest.json"));
        Map<String, Object> sfx = Json.obj(m, "sfx");
        if (sfx == null) return;
        List<String> names = new ArrayList<>();
        for (String k : sfx.keySet()) {
            if (k.startsWith("amb_")) continue;
            if (k.startsWith("ult_") || k.endsWith("_intro") || k.endsWith("_death") || k.startsWith("bs_")) continue; // largos: cargar bajo demanda por jefe
            names.add(k);
        }
        A.preloadSfx(names.toArray(new String[0]));
    }

    public static void preloadList(String... names) { if (A != null) A.preloadSfx(names); }

    public static void sfx(String n) { sfx(n, 1f, 1f, 0f); }
    public static void sfx(String n, float vol) { sfx(n, vol, 1f, 0f); }

    /** Con variacion aleatoria de tono +-6%. */
    public static void sfxv(String n, float vol) { sfx(n, vol, 0.94f + rng.f() * 0.12f, 0f); }

    public static void sfx(String n, float vol, float pitch, float pan) {
        if (A == null || n == null) return;
        A.sfx(n, vol, pitch, pan);
    }

    /** Sonido posicional: pan segun la distancia horizontal a la camara. */
    public static void sfxAt(String n, float x, float camCx, float vol) {
        float dx = x - camCx;
        float att = Mth.clamp(1.2f - Math.abs(dx) / 420f, 0.25f, 1f);
        sfx(n, vol * att, 0.95f + rng.f() * 0.1f, Mth.clamp(dx / 300f, -0.8f, 0.8f));
    }

    public static void music(String n, boolean loop) {
        if (A == null) return;
        if (n.equals(currentMusic) && loop) return;
        currentMusic = n;
        A.music(n, loop, 1f, 900);
    }

    public static void stopMusic(int ms) { if (A != null) { A.stopMusic(ms); currentMusic = ""; } }
    public static void ambient(String n, float v) { if (A != null) A.ambient(n, v); }
}
