package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/** Fuente bitmap proporcional (glifos blancos con contorno; se tinen). */
public final class Font {
    public final Platform.Img img;
    public final int cw, ch, cols, spacing, baseline;
    private final String chars;
    private final int[] widths;
    // glifos chinos (atlas aparte generado por tools/i18n/build_cjk.py)
    private Platform.Img cjkImg;
    private final Map<Character, Integer> cjkIdx = new java.util.HashMap<>();
    private int cjkCell, cjkCols, cjkPitch, cjkYoff, cjkMargin;

    private Font(Platform.Img img, Map<String, Object> d) {
        this.img = img;
        cw = Json.i(d, "cellW", 8);
        ch = Json.i(d, "cellH", 10);
        cols = Json.i(d, "cols", 16);
        spacing = Json.i(d, "spacing", 1);
        baseline = Json.i(d, "baseline", ch - 2);
        chars = Json.str(d, "chars", "");
        int[] w = Json.ints(d, "widths");
        widths = w != null ? w : new int[chars.length()];
    }

    public static Font load(String name) {
        Platform.Img im = Assets.img("font/" + name + ".png");
        Map<String, Object> d = Json.parseObj(Assets.P.loadText("font/" + name + ".json"));
        if (im == null || d == null) return null;
        Font f = new Font(im, d);
        f.loadCjk(name);
        return f;
    }

    private void loadCjk(String name) {
        Platform.Img ci = Assets.img("font/" + name + "_cjk.png");
        Map<String, Object> d = Json.parseObj(Assets.P.loadText("font/" + name + "_cjk.json"));
        if (ci == null || d == null) return;
        cjkImg = ci; cjkCell = Json.i(d, "cell", 13); cjkCols = Json.i(d, "cols", 32); cjkPitch = Json.i(d, "pitch", 12);
        cjkYoff = Json.i(d, "yoff", 0); cjkMargin = Json.i(d, "margin", 1);
        String cs = Json.str(d, "chars", "");
        for (int i = 0; i < cs.length(); i++) cjkIdx.put(cs.charAt(i), i);
    }

    static boolean isCjk(char c) { return c >= 0x2E80 && (c < 0xD800 || c >= 0xFF00 && c <= 0xFFEF); }
    private static boolean noLineStart(char c) { return "，。！？：；、）」』】》…—,.!?:;)".indexOf(c) >= 0 && isCjk(c); }

    private int idx(char c) {
        int i = chars.indexOf(c);
        if (i < 0 && !cjkIdx.containsKey(c)) i = chars.indexOf('?');
        return i;
    }

    public int lineHeight() { return ch + 1; }

    public int widthRaw(String s) { return rawWidth(s); }
    public int width(String s) { return rawWidth(I18n.tr(s)); }

    private int rawWidth(String s) {
        int w = 0, best = 0;
        for (int k = 0; k < s.length(); k++) {
            char c = s.charAt(k);
            if (c == '\n') { best = Math.max(best, w); w = 0; continue; }
            int i = idx(c);
            if (i >= 0) w += widths[i] + spacing;
            else if (cjkIdx.containsKey(c)) w += cjkPitch;
        }
        return Math.max(best, w) - (w > 0 ? spacing : 0);
    }

    public void draw(Platform.Gfx g, String s, float x, float y, int color, float alpha) { rawDraw(g, I18n.tr(s), x, y, color, alpha); }

    private void rawDraw(Platform.Gfx g, String s, float x, float y, int color, float alpha) {
        float cx = Math.round(x), cy = Math.round(y);
        float px = cx;
        for (int k = 0; k < s.length(); k++) {
            char c = s.charAt(k);
            if (c == '\n') { px = cx; cy += ch + 1; continue; }
            Integer ci = i0(c);
            if (ci != null) {
                int j = ci;
                g.image(cjkImg, (j % cjkCols) * cjkCell, (j / cjkCols) * cjkCell, cjkCell, cjkCell, px - cjkMargin, cy + cjkYoff, cjkCell, cjkCell, Platform.TINT, color, alpha);
                px += cjkPitch;
                continue;
            }
            int i = idx(c);
            if (i < 0) continue;
            if (c != ' ') g.image(img, (i % cols) * cw, (i / cols) * ch, cw, ch, px, cy, cw, ch, Platform.TINT, color, alpha);
            px += widths[i] + spacing;
        }
    }

    private Integer i0(char c) { return chars.indexOf(c) < 0 && cjkImg != null ? cjkIdx.get(c) : null; }

    public void draw(Platform.Gfx g, String s, float x, float y, int color) { draw(g, s, x, y, color, 1f); }

    public void center(Platform.Gfx g, String s, float cx, float y, int color, float alpha) {
        s = I18n.tr(s);
        if (s.indexOf('\n') < 0) { rawDraw(g, s, cx - rawWidth(s) / 2f, y, color, alpha); return; }
        String[] ls = s.split("\n");
        for (int i = 0; i < ls.length; i++) rawDraw(g, ls[i], cx - rawWidth(ls[i]) / 2f, y + i * (ch + 1), color, alpha);
    }

    public void right(Platform.Gfx g, String s, float rx, float y, int color, float alpha) { s = I18n.tr(s); rawDraw(g, s, rx - rawWidth(s), y, color, alpha); }

    /** Texto con sombra dura de 1px. */
    public void shadow(Platform.Gfx g, String s, float x, float y, int color, float alpha) {
        s = I18n.tr(s);
        rawDraw(g, s, x + 1, y + 1, 0x000000, alpha * 0.8f);
        rawDraw(g, s, x, y, color, alpha);
    }

    public List<String> wrap(String s, int maxW) { return rawWrap(I18n.tr(s), maxW); }

    /** Divide en "palabras": las separadas por espacios y, en chino, cada caracter (con su puntuacion de cierre pegada). */
    private List<String[]> tokens(String para) {
        List<String[]> out = new ArrayList<>();   // {texto, "1" si lleva espacio delante}
        StringBuilder cur = new StringBuilder(); boolean sp = false;
        for (int i = 0; i < para.length(); i++) {
            char c = para.charAt(i);
            if (c == ' ') { if (cur.length() > 0) { out.add(new String[]{cur.toString(), sp ? "1" : "0"}); cur.setLength(0); } sp = true; continue; }
            if (isCjk(c)) {
                if (cur.length() > 0 && !isCjk(cur.charAt(cur.length() - 1))) { out.add(new String[]{cur.toString(), sp ? "1" : "0"}); cur.setLength(0); sp = false; }
                if (noLineStart(c) && !out.isEmpty() && cur.length() == 0) { String[] last = out.get(out.size() - 1); last[0] += c; continue; }
                if (cur.length() > 0) { out.add(new String[]{cur.toString(), sp ? "1" : "0"}); cur.setLength(0); sp = false; }
                cur.append(c);
                continue;
            }
            if (cur.length() > 0 && isCjk(cur.charAt(cur.length() - 1))) { out.add(new String[]{cur.toString(), sp ? "1" : "0"}); cur.setLength(0); sp = false; }
            cur.append(c);
        }
        if (cur.length() > 0) out.add(new String[]{cur.toString(), sp ? "1" : "0"});
        return out;
    }

    private List<String> rawWrap(String s, int maxW) {
        List<String> out = new ArrayList<>();
        for (String para : s.split("\n", -1)) {
            StringBuilder cur = new StringBuilder();
            for (String[] w : tokens(para)) {
                String t = cur.length() == 0 ? w[0] : cur + (w[1].equals("1") ? " " : "") + w[0];
                if (rawWidth(t) > maxW && cur.length() > 0) { out.add(cur.toString()); cur = new StringBuilder(w[0]); }
                else { cur = new StringBuilder(t); }
            }
            out.add(cur.toString());
        }
        return out;
    }

    /** Dibuja texto ajustado a ancho; devuelve el alto usado. */
    public int drawWrapped(Platform.Gfx g, String s, float x, float y, int maxW, int color, float alpha) {
        List<String> ls = rawWrap(I18n.tr(s), maxW);
        for (int i = 0; i < ls.size(); i++) rawDraw(g, ls.get(i), x, y + i * (ch + 2), color, alpha);
        return ls.size() * (ch + 2);
    }
}
