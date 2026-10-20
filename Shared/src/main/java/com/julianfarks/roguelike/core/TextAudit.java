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

    static void begin(String c) { if (!ON) return; xfEnd(); clip = null; ctx = c; panels.clear(); texts.clear(); strs.clear(); }
    static void panel(float x, float y, float w, float h, boolean button) { if (ON && w > 12 && h > 8) panels.add(new float[]{x, y, w, h, button ? 1 : 0, texts.size()}); }
    /** Un velo oscuro opaco tapa lo dibujado antes (HUD bajo un menu): esos textos no cuentan. */
    static void cover() { if (!ON) return; texts.clear(); strs.clear(); panels.clear(); }
    private static float xtx, xty, xz = 1f;
    /** Transformacion de camara activa (textos del mundo): se pasan a coordenadas de pantalla antes de comprobarlos. */
    static void xf(float tx, float ty, float z) { xtx = tx; xty = ty; xz = z; }
    static void xfEnd() { xtx = 0; xty = 0; xz = 1f; }
    private static float[] clip;
    /** Zona recortada (p. ej. un panel con desplazamiento): lo que queda fuera no se ve y no cuenta como desborde. */
    static void clip(float x, float y, float w, float h) { if (ON) clip = new float[]{x, y, w, h}; }
    static void unclip() { clip = null; }
    static void text(String s, float x, float y, float w, float h, float alpha) {
        if (!ON || alpha < 0.3f || s.trim().isEmpty()) return;
        if (xz != 1f || xtx != 0 || xty != 0) { x = x * xz + xtx; y = y * xz + xty; w *= xz; h *= xz; }
        if (clip != null) {
            float x1 = Math.max(x, clip[0]), y1 = Math.max(y, clip[1]), x2 = Math.min(x + w, clip[0] + clip[2]), y2 = Math.min(y + h, clip[1] + clip[3]);
            if (x2 <= x1 || y2 <= y1) return;
            x = x1; y = y1; w = x2 - x1; h = y2 - y1;
        }
        texts.add(new float[]{x, y, w, h}); strs.add(s);
    }

    /** Un texto se tuvo que recortar ("." o "…") porque no cabia: es un desborde que hay que resolver con el diseno, no ocultarlo. */
    static void cut(String s, String extra) { if (ON) report("RECORTADO", s, extra); }

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
            for (float[] p : panels) {      // texto suelto que invade un boton (p. ej. un pie de pantalla bajo "Volver")
                if (p[4] == 0 || p == best) continue;
                boolean inside = t[0] + 1 >= p[0] && t[0] + 1 <= p[0] + p[2] && t[1] + 1 >= p[1] && t[1] + 1 <= p[1] + p[3];
                if (inside) continue;
                float ox = Math.min(t[0] + t[2], p[0] + p[2]) - Math.max(t[0], p[0]), oy = Math.min(t[1] + t[3], p[1] + p[3]) - Math.max(t[1], p[1]);
                if (ox > 2 && oy > 3) report("PISA_BOTON", s, "texto " + Math.round(t[0]) + "," + Math.round(t[1]) + " boton " + Math.round(p[0]) + "," + Math.round(p[1]) + " " + Math.round(p[2]) + "x" + Math.round(p[3]));
            }
            if (best != null && best[4] == 0 && best[3] > 20 && t[1] + t[3] > best[1] + best[3] - 2.5f && t[1] + t[3] <= best[1] + best[3] + 0.5f)
                report("PEGADO_AL_BORDE", s, "texto y=" + Math.round(t[1]) + "+" + Math.round(t[3]) + " panel hasta " + Math.round(best[1] + best[3]));
            boolean num = s.trim().matches("[0-9.,!+%x ]+");     // numeros de dano en combate: se apilan un instante, es normal
            for (int j = 0; j < i; j++) {
                if (strs.get(j).equals(s)) continue;
                if (num || strs.get(j).trim().matches("[0-9.,!+%x ]+")) continue;
                float[] u = texts.get(j);
                float ox = Math.min(t[0] + t[2], u[0] + u[2]) - Math.max(t[0], u[0]), oy = Math.min(t[1] + t[3], u[1] + u[3]) - Math.max(t[1], u[1]);
                if (ox > 2 && oy > 4) report("TEXTOS_SE_PISAN", s, "con \"" + (strs.get(j).length() > 40 ? strs.get(j).substring(0, 40) : strs.get(j)) + "\" solape " + Math.round(ox) + "x" + Math.round(oy));
            }
        }
    }
}
