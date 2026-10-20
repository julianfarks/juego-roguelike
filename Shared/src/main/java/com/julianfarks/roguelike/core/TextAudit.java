package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Detector de textos desbordados (solo banco de pruebas; BOT_TEXTAUDIT=1). Durante un fotograma anota los paneles/botones dibujados y
 * cada texto; al terminar avisa de: texto que sobresale del panel que lo contiene, texto fuera de la pantalla y textos que se pisan.
 * Sin la variable de entorno no hace nada (coste cero).
 */
public final class TextAudit {
    private TextAudit() {}
    public static final boolean ON = System.getenv("BOT_TEXTAUDIT") != null;
    public static String ctx = "";
    private static final List<float[]> panels = new ArrayList<>();
    private static final List<float[]> texts = new ArrayList<>();
    private static final List<String> strs = new ArrayList<>();
    private static final Set<String> seen = new HashSet<>();
    public static final List<String> found = new ArrayList<>();

    static void begin(String c) { if (!ON) return; ctx = c; panels.clear(); texts.clear(); strs.clear(); }
    static void panel(float x, float y, float w, float h, boolean button) { if (ON && w > 12 && h > 8) panels.add(new float[]{x, y, w, h, button ? 1 : 0, texts.size()}); }
    /** Un velo oscuro opaco tapa lo dibujado antes (HUD bajo un menu): esos textos no cuentan. */
    static void cover() { if (!ON) return; texts.clear(); strs.clear(); panels.clear(); }
    static void text(String s, float x, float y, float w, float h, float alpha) {
        if (!ON || alpha < 0.3f || s.trim().isEmpty()) return;
        texts.add(new float[]{x, y, w, h}); strs.add(s);
    }

    private static void report(String kind, String s, String extra) {
        String key = ctx + "|" + kind + "|" + s;
        if (seen.add(key)) { String m = "TXT " + kind + " [" + ctx + "] \"" + (s.length() > 60 ? s.substring(0, 60) + "..." : s) + "\" " + extra; found.add(m); System.out.println(m); }
    }

    static void end(int vw, int vh) {
        if (!ON) return;
        if (System.getenv("BOT_TEXTSEEN") != null && seen.add("seen|" + ctx)) System.out.println("TXTSEEN [" + ctx + "] textos=" + texts.size() + " paneles=" + panels.size());
        for (int i = 0; i < texts.size(); i++) {
            float[] t = texts.get(i); String s = strs.get(i);
            boolean originIn = t[0] >= -0.5f && t[0] < vw && t[1] >= -0.5f && t[1] < vh;      // textos del mundo (camara) no cuentan
            if (originIn && (t[0] + t[2] > vw + 0.5f || t[1] + t[3] > vh + 0.5f))
                report("FUERA_PANTALLA", s, "x=" + Math.round(t[0]) + " y=" + Math.round(t[1]) + " w=" + Math.round(t[2]) + " (pantalla " + vw + "x" + vh + ")");
            float[] best = null;
            for (float[] p : panels) {
                if (i < p[5]) continue;      // el panel se dibujo despues del texto: no lo contiene
                if (t[0] + 1 >= p[0] && t[0] + 1 <= p[0] + p[2] && t[1] + 1 >= p[1] && t[1] + 1 <= p[1] + p[3]) {
                    if (best == null || p[2] * p[3] < best[2] * best[3]) best = p;
                }
            }
            if (best != null && (t[0] + t[2] > best[0] + best[2] + 0.5f || t[1] + t[3] > best[1] + best[3] + 0.5f))
                report(best[4] > 0 ? "BOTON_DESBORDA" : "PANEL_DESBORDA", s, "texto " + Math.round(t[0]) + "," + Math.round(t[1]) + " " + Math.round(t[2]) + "x" + Math.round(t[3]) + " panel " + Math.round(best[0]) + "," + Math.round(best[1]) + " " + Math.round(best[2]) + "x" + Math.round(best[3]));
            for (int j = 0; j < i; j++) {
                if (strs.get(j).equals(s)) continue;
                float[] u = texts.get(j);
                float ox = Math.min(t[0] + t[2], u[0] + u[2]) - Math.max(t[0], u[0]), oy = Math.min(t[1] + t[3], u[1] + u[3]) - Math.max(t[1], u[1]);
                if (ox > 2 && oy > 4) report("TEXTOS_SE_PISAN", s, "con \"" + (strs.get(j).length() > 40 ? strs.get(j).substring(0, 40) : strs.get(j)) + "\" solape " + Math.round(ox) + "x" + Math.round(oy));
            }
        }
    }
}
