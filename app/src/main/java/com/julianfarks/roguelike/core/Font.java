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
        return new Font(im, d);
    }

    private int idx(char c) {
        int i = chars.indexOf(c);
        if (i < 0) i = chars.indexOf('?');
        return i;
    }

    public int lineHeight() { return ch + 1; }

    public int width(String s) {
        int w = 0, best = 0;
        for (int k = 0; k < s.length(); k++) {
            char c = s.charAt(k);
            if (c == '\n') { best = Math.max(best, w); w = 0; continue; }
            int i = idx(c);
            if (i >= 0) w += widths[i] + spacing;
        }
        return Math.max(best, w) - (w > 0 ? spacing : 0);
    }

    public void draw(Platform.Gfx g, String s, float x, float y, int color, float alpha) {
        float cx = Math.round(x), cy = Math.round(y);
        float px = cx;
        for (int k = 0; k < s.length(); k++) {
            char c = s.charAt(k);
            if (c == '\n') { px = cx; cy += ch + 1; continue; }
            int i = idx(c);
            if (i < 0) continue;
            if (c != ' ') g.image(img, (i % cols) * cw, (i / cols) * ch, cw, ch, px, cy, cw, ch, Platform.TINT, color, alpha);
            px += widths[i] + spacing;
        }
    }

    public void draw(Platform.Gfx g, String s, float x, float y, int color) { draw(g, s, x, y, color, 1f); }

    public void center(Platform.Gfx g, String s, float cx, float y, int color, float alpha) {
        if (s.indexOf('\n') < 0) { draw(g, s, cx - width(s) / 2f, y, color, alpha); return; }
        String[] ls = s.split("\n");
        for (int i = 0; i < ls.length; i++) draw(g, ls[i], cx - width(ls[i]) / 2f, y + i * (ch + 1), color, alpha);
    }

    public void right(Platform.Gfx g, String s, float rx, float y, int color, float alpha) { draw(g, s, rx - width(s), y, color, alpha); }

    /** Texto con sombra dura de 1px. */
    public void shadow(Platform.Gfx g, String s, float x, float y, int color, float alpha) {
        draw(g, s, x + 1, y + 1, 0x000000, alpha * 0.8f);
        draw(g, s, x, y, color, alpha);
    }

    public List<String> wrap(String s, int maxW) {
        List<String> out = new ArrayList<>();
        for (String para : s.split("\n")) {
            String[] words = para.split(" ");
            StringBuilder cur = new StringBuilder();
            for (String w : words) {
                String t = cur.length() == 0 ? w : cur + " " + w;
                if (width(t) > maxW && cur.length() > 0) { out.add(cur.toString()); cur = new StringBuilder(w); }
                else { cur = new StringBuilder(t); }
            }
            out.add(cur.toString());
        }
        return out;
    }

    /** Dibuja texto ajustado a ancho; devuelve el alto usado. */
    public int drawWrapped(Platform.Gfx g, String s, float x, float y, int maxW, int color, float alpha) {
        List<String> ls = wrap(s, maxW);
        for (int i = 0; i < ls.size(); i++) draw(g, ls.get(i), x, y + i * (ch + 2), color, alpha);
        return ls.size() * (ch + 2);
    }
}
