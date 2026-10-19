package com.julianfarks.roguelike.core;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Hoja de sprites + metadatos (celda, pivote, animaciones). */
public final class Sheet {
    public static final Sheet EMPTY = new Sheet(null, 16, 16, 8, 16, 8, 16);
    public final Platform.Img img;
    public final int cw, ch, px, py, bw, bh;
    public final Map<String, Anim> anims = new HashMap<>();

    Sheet(Platform.Img img, int cw, int ch, int px, int py, int bw, int bh) {
        this.img = img; this.cw = cw; this.ch = ch; this.px = px; this.py = py; this.bw = bw; this.bh = bh;
    }

    static Sheet parse(Platform.Img img, Map<String, Object> d) {
        int[] cell = Json.ints(d, "cell");
        int[] piv = Json.ints(d, "pivot");
        int[] body = Json.ints(d, "body");
        if (cell == null) return null;
        Sheet s = new Sheet(img, cell[0], cell[1], piv != null ? piv[0] : cell[0] / 2, piv != null ? piv[1] : cell[1] - 2,
                body != null ? body[0] : 12, body != null ? body[1] : 24);
        Map<String, Object> an = Json.obj(d, "anims");
        if (an != null) {
            for (Map.Entry<String, Object> e : an.entrySet()) {
                @SuppressWarnings("unchecked") Map<String, Object> m = (Map<String, Object>) e.getValue();
                Anim a = new Anim(e.getKey(), Json.i(m, "row", 0), Json.i(m, "n", 1), (float) Json.num(m, "fps", 10), Json.bool(m, "loop", false));
                int[] hit = Json.ints(m, "hit");
                if (hit != null && hit.length >= 2) { a.h0 = hit[0]; a.h1 = hit[1]; }
                a.box = Json.ints(m, "box");
                a.rel = Json.i(m, "rel", -1);
                a.muzzle = Json.ints(m, "muzzle");
                a.smear = Json.i(m, "smear", -1);
                Object ft = m.get("ft");
                if (ft instanceof java.util.List) { java.util.List<?> l = (java.util.List<?>) ft; float[] w = new float[l.size()]; for (int i = 0; i < w.length; i++) w[i] = l.get(i) instanceof Number ? ((Number) l.get(i)).floatValue() : 1f; a.setWeights(w); }
                s.anims.put(e.getKey(), a);
            }
        }
        return s;
    }

    public Anim anim(String name) {
        Anim a = anims.get(name);
        return a != null ? a : Anim.NONE;
    }

    public boolean has(String name) { return anims.containsKey(name); }

    /** Dibuja el fotograma con el pivote en (x,y). */
    public void draw(Platform.Gfx g, Anim a, int frame, float x, float y, boolean right, float scale, int flags, int tint, float alpha) {
        if (img == null) return;
        int row = a == Anim.NONE ? 0 : a.row;
        int f = Math.max(0, Math.min(frame, a.n - 1));
        float dw = cw * scale, dh = ch * scale;
        float dx = right ? x - px * scale : x - (cw - px) * scale;
        float dy = y - py * scale;
        g.image(img, f * cw, row * ch, cw, ch, Math.round(dx), Math.round(dy), Math.round(dw), Math.round(dh),
                right ? flags : (flags | Platform.FLIP_X), tint, alpha);
    }

    /** Dibuja con escala no uniforme anclada a los pies (squash & stretch). */
    public void drawSq(Platform.Gfx g, Anim a, int frame, float x, float y, boolean right, float sx, float sy, int flags, int tint, float alpha) {
        if (img == null) return;
        int row = a == Anim.NONE ? 0 : a.row;
        int f = Math.max(0, Math.min(frame, a.n - 1));
        float dw = cw * sx, dh = ch * sy;
        float dx = right ? x - px * sx : x - (cw - px) * sx;
        float dy = y - py * sy;
        g.image(img, f * cw, row * ch, cw, ch, Math.round(dx), Math.round(dy), Math.round(dw), Math.round(dh),
                right ? flags : (flags | Platform.FLIP_X), tint, alpha);
    }

    /** Dibuja animacion en el tiempo t. */
    public void drawAt(Platform.Gfx g, String anim, float t, float x, float y, boolean right, float scale, int flags, int tint, float alpha) {
        Anim a = anim(anim);
        draw(g, a, a.frameAt(t), x, y, right, scale, flags, tint, alpha);
    }

    /** Dibuja centrada (efectos): el pivote del JSON ya es el centro de efecto. */
    public void drawCentered(Platform.Gfx g, Anim a, int frame, float cx, float cy, float rot, float scale, int flags, int tint, float alpha) {
        if (img == null) return;
        int f = Math.max(0, Math.min(frame, a.n - 1));
        float dw = cw * scale, dh = ch * scale;
        float dx = cx - px * scale, dy = cy - py * scale;
        if (rot == 0) g.image(img, f * cw, a.row * ch, cw, ch, Math.round(dx), Math.round(dy), Math.round(dw), Math.round(dh), flags, tint, alpha);
        else {
            // rotar alrededor de (cx,cy): el rectangulo destino se centra en el pivote
            float ox = (cw / 2f - px) * scale, oy = (ch / 2f - py) * scale;
            double c = Math.cos(rot), s = Math.sin(rot);
            float rx = (float) (ox * c - oy * s), ry = (float) (ox * s + oy * c);
            g.imageRot(img, f * cw, a.row * ch, cw, ch, cx + rx - dw / 2f, cy + ry - dh / 2f, dw, dh, rot, flags, tint, alpha);
        }
    }

    @SuppressWarnings("unchecked")
    static List<Object> listOf(Object o) { return (List<Object>) o; }
}
