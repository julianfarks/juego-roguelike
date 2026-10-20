package com.julianfarks.roguelike.core;

import java.util.HashMap;
import java.util.Map;

/** Dibujo de interfaz: paneles 9-slice, botones, iconos, barras, fuentes. */
public final class UI {
    private UI() {}
    public static final int WHITE = 0xFFFFFF, GOLD = 0xFFD25A, RED = 0xFF5A5A, GREEN = 0x6AE08A, GREY = 0x9AA0B0, CYAN = 0x7AF0FF,
            PURPLE = 0xC08CFF, ORANGE = 0xFF9A3C, BLOOD = 0xD0203A, DARK = 0x14101C, SOUL = 0x9FD8FF;

    public static Font small, big;
    public static Platform.Img panel, panelLight, panelRed, btn, btnRound, hpFrame, hpFill, ultFrame, ultFill, bossFrame, bossFill,
            cursor, arrow, vignette, icons, logo, bxIcons;
    private static final Map<String, Integer> bxIdx = new HashMap<>();
    private static final Map<String, Integer> iconIdx = new HashMap<>();
    private static int iconCols = 16;
    public static Platform.Img glow32, glow64, glow128;

    public static void load() {
        small = Font.load("font_s");
        big = Font.load("font_b");
        if (big == null) big = small;
        panel = Assets.img("ui/ui_panel.png");
        panelLight = Assets.img("ui/ui_panel_light.png");
        panelRed = Assets.img("ui/ui_panel_red.png");
        btn = Assets.img("ui/ui_btn.png");
        btnRound = Assets.img("ui/ui_btn_round.png");
        hpFrame = Assets.img("ui/ui_hp_frame.png");
        hpFill = Assets.img("ui/ui_hp_fill.png");
        ultFrame = Assets.img("ui/ui_ult_frame.png");
        ultFill = Assets.img("ui/ui_ult_fill.png");
        bossFrame = Assets.img("ui/ui_boss_frame.png");
        bossFill = Assets.img("ui/ui_boss_fill.png");
        cursor = Assets.img("ui/ui_cursor.png");
        arrow = Assets.img("ui/ui_arrow.png");
        vignette = Assets.img("ui/ui_vignette.png");
        logo = Assets.img("ui/ui_logo.png");
        icons = Assets.img("ui/icons.png");
        Map<String, Object> d = Json.parseObj(Assets.P.loadText("ui/icons.json"));
        if (d != null) {
            iconCols = Json.i(d, "cols", 16);
            java.util.List<Object> names = Json.arr(d, "names");
            if (names != null) for (int i = 0; i < names.size(); i++) iconIdx.put((String) names.get(i), i);
        }
        bxIcons = Assets.img("ui/bless_icons.png");
        Map<String, Object> d2 = Json.parseObj(Assets.P.loadText("ui/bless_icons.json"));
        if (d2 != null) {
            java.util.List<Object> n2 = Json.arr(d2, "names");
            if (n2 != null) for (int i = 0; i < n2.size(); i++) bxIdx.put((String) n2.get(i), i);
        }
        glow32 = makeGlow(32);
        glow64 = makeGlow(64);
        glow128 = makeGlow(128);
    }

    /** Gradiente radial blanco -> transparente para luces aditivas. */
    private static Platform.Img makeGlow(int s) {
        int[] px = new int[s * s];
        float c = (s - 1) / 2f;
        for (int y = 0; y < s; y++)
            for (int x = 0; x < s; x++) {
                float d = (float) Math.sqrt((x - c) * (x - c) + (y - c) * (y - c)) / (s / 2f);
                float a = Math.max(0, 1 - d);
                a = a * a * (3 - 2 * a);
                int v = (int) (a * 255);
                px[y * s + x] = (v << 24) | 0xFFFFFF;
            }
        return Assets.P.createImage(s, s, px);
    }

    /** Luz aditiva centrada en (cx,cy) con radio r y color (RGB). */
    public static void light(Platform.Gfx g, float cx, float cy, float r, int color, float alpha) {
        if (!VideoCfg.lights) return;                          // calidad grafica (solo PC): sin brillos aditivos
        Platform.Img im = r <= 20 ? glow32 : (r <= 44 ? glow64 : glow128);
        if (im == null) return;
        g.image(im, 0, 0, im.w, im.h, Math.round(cx - r), Math.round(cy - r), r * 2, r * 2, Platform.ADD | Platform.TINT, color, alpha);
    }

    public static boolean hasIcon(String n) { return iconIdx.containsKey(n) || bxIdx.containsKey(n); }

    /** Dibuja el icono por nombre con su esquina superior izquierda en (x,y). */
    public static void icon(Platform.Gfx g, String name, float x, float y, float scale, int flags, int tint, float alpha) {
        Integer bi = bxIdx.get(name);
        if (bi != null && bxIcons != null) {
            g.image(bxIcons, (bi % 16) * 16, (bi / 16) * 16, 16, 16, Math.round(x), Math.round(y), 16 * scale, 16 * scale, flags, tint, alpha);
            return;
        }
        Integer i = iconIdx.get(name);
        if (i == null || icons == null) return;
        g.image(icons, (i % iconCols) * 16, (i / iconCols) * 16, 16, 16, Math.round(x), Math.round(y), 16 * scale, 16 * scale, flags, tint, alpha);
    }

    public static void icon(Platform.Gfx g, String name, float x, float y, float scale) { icon(g, name, x, y, scale, 0, 0, 1f); }

    public static void iconC(Platform.Gfx g, String name, float cx, float cy, float scale, float alpha) {
        icon(g, name, cx - 8 * scale, cy - 8 * scale, scale, 0, 0, alpha);
    }

    private static void slice(Platform.Gfx g, Platform.Img im, int sx0, int sw, int sh, int c, float x, float y, float w, float h, float alpha) {
        if (im == null) return;
        x = Math.round(x); y = Math.round(y); w = Math.round(w); h = Math.round(h);
        int mw = sw - 2 * c, mh = sh - 2 * c;
        float iw = w - 2 * c, ih = h - 2 * c;
        // esquinas
        g.image(im, sx0, 0, c, c, x, y, c, c, 0, 0, alpha);
        g.image(im, sx0 + sw - c, 0, c, c, x + w - c, y, c, c, 0, 0, alpha);
        g.image(im, sx0, sh - c, c, c, x, y + h - c, c, c, 0, 0, alpha);
        g.image(im, sx0 + sw - c, sh - c, c, c, x + w - c, y + h - c, c, c, 0, 0, alpha);
        // bordes
        if (iw > 0) {
            g.image(im, sx0 + c, 0, mw, c, x + c, y, iw, c, 0, 0, alpha);
            g.image(im, sx0 + c, sh - c, mw, c, x + c, y + h - c, iw, c, 0, 0, alpha);
        }
        if (ih > 0) {
            g.image(im, sx0, c, c, mh, x, y + c, c, ih, 0, 0, alpha);
            g.image(im, sx0 + sw - c, c, c, mh, x + w - c, y + c, c, ih, 0, 0, alpha);
        }
        if (iw > 0 && ih > 0) g.image(im, sx0 + c, c, mw, mh, x + c, y + c, iw, ih, 0, 0, alpha);
    }

    /** kind: 0 normal, 1 clara (seleccionada), 2 roja. */
    public static void panel(Platform.Gfx g, int kind, float x, float y, float w, float h, float alpha) {
        TextAudit.panel(x, y, w, h, false);
        Platform.Img im = kind == 1 ? panelLight : (kind == 2 ? panelRed : panel);
        if (im == null) { g.rect(x, y, w, h, 0xCC101018, false); return; }
        slice(g, im, 0, 32, 32, 8, x, y, w, h, alpha);
        rivets(g, x, y, w, h, alpha);
    }

    public static void panel(Platform.Gfx g, int kind, float x, float y, float w, float h) { panel(g, kind, x, y, w, h, 1f); }

    /** Remaches de hierro envejecido en las 4 esquinas (solo paneles grandes: discretos, nunca bajo el texto). */
    static void rivets(Platform.Gfx g, float x, float y, float w, float h, float alpha) {
        if (w < 64 || h < 40) return;
        int a = Math.round(200 * alpha) << 24;
        float[][] p = {{x + 3, y + 3}, {x + w - 5, y + 3}, {x + 3, y + h - 5}, {x + w - 5, y + h - 5}};
        for (float[] q : p) { g.rect(Math.round(q[0]), Math.round(q[1]), 2, 2, a | 0x8A7430, false); g.rect(Math.round(q[0]), Math.round(q[1]), 1, 1, a | 0xD8C070, false); }
    }

    /** Separador de seccion: filete dorado desgastado con un rombo central. */
    public static void divider(Platform.Gfx g, float x, float y, float w) {
        x = Math.round(x); y = Math.round(y); w = Math.round(w);
        g.rect(x, y, w, 1, 0x55B8A050, false);
        g.rect(x + w / 2f - 1, y - 1, 3, 3, 0xFF8A7430, false); g.rect(x + w / 2f, y, 1, 1, 0xFFE8D080, false);
    }

    /** Titulo de pantalla: texto grande con filetes dorados a los lados. */
    public static void title(Platform.Gfx g, String s, float cx, float y, int color, float alpha) {
        if (big == null) return;
        big.center(g, s, cx, y, color, alpha);
        float tw = big.width(I18n.tr(s)) / 2f + 8, ly = Math.round(y + big.ch / 2f);
        int a = Math.round(120 * alpha) << 24;
        g.rect(Math.round(cx - tw - 22), ly, 22, 1, a | 0xB8A050, false); g.rect(Math.round(cx + tw), ly, 22, 1, a | 0xB8A050, false);
        g.rect(Math.round(cx - tw - 25), ly - 1, 3, 3, a | 0x8A7430, false); g.rect(Math.round(cx + tw + 22), ly - 1, 3, 3, a | 0x8A7430, false);
    }

    public static int tagH() { return small.ch + 2; }

    /** Etiqueta (rareza, categoria, estado). filled = relleno de color (p. ej. EN USO). Devuelve su ancho; con draw=false solo mide. */
    public static float tag(Platform.Gfx g, String s, float x, float y, int rgb, boolean filled, boolean draw) {
        String t = I18n.tr(s);
        float w = small.width(t) + 7;
        if (!draw) return w;
        int c = 0xFF000000 | (rgb & 0xFFFFFF);
        int th = tagH();
        g.rect(x, y, w, th, filled ? 0xFF000000 | ((((rgb >> 16) & 0xFF) / 4) << 16 | (((rgb >> 8) & 0xFF) / 4) << 8 | ((rgb & 0xFF) / 4)) : 0xFF101018, false);
        g.rect(x, y, w, 1, c, false); g.rect(x, y + th - 1, w, 1, c, false); g.rect(x, y, 1, th, c, false); g.rect(x + w - 1, y, 1, th, c, false);
        small.draw(g, t, x + 4, y + 1, c, 1f);
        return w;
    }

    /** state 0 normal, 1 resaltado, 2 pulsado. */
    public static void button(Platform.Gfx g, String label, float x, float y, float w, float h, int state, boolean disabled) {
        TextAudit.panel(x, y, w, h, true);
        float a = disabled ? 0.5f : 1f;
        if (btn != null) slice(g, btn, Math.min(2, state) * 48, 48, 20, 6, x, y, w, h, a);
        else g.rect(x, y, w, h, state == 2 ? 0xFF444455 : 0xFF2A2A38, false);
        if (label != null && small != null) {
            int c = disabled ? GREY : (state == 1 ? GOLD : WHITE);
            float ty = y + (h - small.ch) / 2f + (state == 2 ? 1 : 0);
            small.center(g, fitLabel(small, label, w - 4), x + w / 2f, ty, c, 1f);
        }
    }

    /** Recorta con '.' un rotulo que no cabe (traducciones largas) para que nunca se salga del boton. */
    public static String fitLabel(Font f, String label, float maxW) {
        if (f.width(label) <= maxW) return label;
        String s = I18n.tr(label);
        while (s.length() > 1 && f.widthRaw(s + ".") > maxW) s = s.substring(0, s.length() - 1);
        s = s + ".";
        I18n.pin(s);
        return s;
    }

    /** Boton redondo tactil: centro (cx,cy), radio r. state 0 normal, 1 pulsado, 2 deshabilitado. */
    public static void roundButton(Platform.Gfx g, float cx, float cy, float r, int state, float alpha) {
        if (btnRound == null) { g.circle(cx, cy, r, 0x88202030, false); return; }
        g.image(btnRound, Mth.clamp(state, 0, 2) * 40, 0, 40, 40, Math.round(cx - r), Math.round(cy - r), Math.round(r * 2), Math.round(r * 2), 0, 0, alpha);
    }

    public static void hpBar(Platform.Gfx g, float x, float y, float ratio) {
        if (hpFill != null) g.image(hpFill, 0, 0, Math.max(1, Math.round(hpFill.w * Mth.clamp(ratio, 0, 1))), hpFill.h, x + 2, y + 2, Math.max(1, Math.round(hpFill.w * Mth.clamp(ratio, 0, 1))), hpFill.h, 0, 0, 1f);
        if (hpFrame != null) g.image(hpFrame, 0, 0, hpFrame.w, hpFrame.h, x, y, hpFrame.w, hpFrame.h, 0, 0, 1f);
    }

    public static void ultBar(Platform.Gfx g, float x, float y, float ratio, boolean ready, float time) {
        float r = Mth.clamp(ratio, 0, 1);
        if (ultFill != null) {
            int w = Math.max(1, Math.round(ultFill.w * r));
            g.image(ultFill, 0, 0, w, ultFill.h, x + 2, y + 2, w, ultFill.h, ready ? Platform.TINT : 0, 0xFFFFFF, 1f);
            if (ready) g.image(ultFill, 0, 0, ultFill.w, ultFill.h, x + 2, y + 2, ultFill.w, ultFill.h, Platform.ADD, 0, 0.35f + 0.25f * (float) Math.sin(time * 8));
        }
        if (ultFrame != null) g.image(ultFrame, 0, 0, ultFrame.w, ultFrame.h, x, y, ultFrame.w, ultFrame.h, 0, 0, 1f);
    }

    public static void bossBar(Platform.Gfx g, float cx, float y, float ratio, float alpha) {
        if (bossFrame == null) return;
        float x = cx - bossFrame.w / 2f;
        float r = Mth.clamp(ratio, 0, 1);
        if (bossFill != null) {
            int w = Math.max(0, Math.round(bossFill.w * r));
            if (w > 0) g.image(bossFill, 0, 0, w, bossFill.h, x + 6, y + 5, w, bossFill.h, 0, 0, alpha);
        }
        g.image(bossFrame, 0, 0, bossFrame.w, bossFrame.h, x, y, bossFrame.w, bossFrame.h, 0, 0, alpha);
    }

    public static boolean inside(float px, float py, float x, float y, float w, float h) {
        return px >= x && px < x + w && py >= y && py < y + h;
    }
}
