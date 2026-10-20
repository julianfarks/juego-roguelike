package com.julianfarks.roguelike.core;

/** Matematicas y colores. */
public final class Mth {
    private Mth() {}
    /** Azar visual/menor del juego. Igual que Math.random(); solo con BOT_SEED (banco de pruebas / grabacion) es reproducible. */
    private static final java.util.Random DET = System.getenv("BOT_SEED") != null ? new java.util.Random(Long.parseLong(System.getenv("BOT_SEED").trim())) : null;
    public static double rnd() { return DET != null ? DET.nextDouble() : Math.random(); }
    public static float clamp(float v, float a, float b) { return v < a ? a : (v > b ? b : v); }
    public static int clamp(int v, int a, int b) { return v < a ? a : (v > b ? b : v); }
    public static float lerp(float a, float b, float t) { return a + (b - a) * t; }
    public static float approach(float v, float target, float d) {
        if (v < target) return Math.min(v + d, target);
        return Math.max(v - d, target);
    }
    public static float sign(float v) { return v < 0 ? -1f : (v > 0 ? 1f : 0f); }
    public static float dist(float x1, float y1, float x2, float y2) {
        float dx = x2 - x1, dy = y2 - y1;
        return (float) Math.sqrt(dx * dx + dy * dy);
    }
    public static float easeOut(float t) { t = clamp(t, 0, 1); return 1 - (1 - t) * (1 - t); }
    public static float easeInOut(float t) { t = clamp(t, 0, 1); return t * t * (3 - 2 * t); }

    public static int argb(int a, int r, int g, int b) { return (a << 24) | (r << 16) | (g << 8) | b; }
    /** color 0xRRGGBB con alfa 0..255 */
    public static int withAlpha(int rgb, int a) { return ((a & 255) << 24) | (rgb & 0xFFFFFF); }
    public static int mix(int c1, int c2, float t) {
        int a = (int) Mth.lerp((c1 >>> 24), (c2 >>> 24), t);
        int r = (int) Mth.lerp((c1 >> 16) & 255, (c2 >> 16) & 255, t);
        int g = (int) Mth.lerp((c1 >> 8) & 255, (c2 >> 8) & 255, t);
        int b = (int) Mth.lerp(c1 & 255, c2 & 255, t);
        return (a << 24) | (r << 16) | (g << 8) | b;
    }
    public static int opaque(int rgb) { return 0xFF000000 | rgb; }
    public static boolean overlap(float ax, float ay, float aw, float ah, float bx, float by, float bw, float bh) {
        return ax < bx + bw && ax + aw > bx && ay < by + bh && ay + ah > by;
    }
}
