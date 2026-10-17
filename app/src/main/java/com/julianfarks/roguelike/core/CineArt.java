package com.julianfarks.roguelike.core;

/** Fondos procedurales de las cinematicas (siluetas, parallax, luces). Sin imagenes nuevas: todo con rectangulos, circulos y luces. */
final class CineArt {
    private CineArt() {}

    static final int[] SEVEN = {0xFFE9A0, 0x9A7AFF, 0xFF7A2A, 0xB8F0FF, 0x6AA8FF, 0x5AE88A, 0xFF4A5A};

    private static int mix(int a, int b, float t) {
        t = Mth.clamp(t, 0, 1);
        int r = (int) (((a >> 16) & 255) * (1 - t) + ((b >> 16) & 255) * t), gg = (int) (((a >> 8) & 255) * (1 - t) + ((b >> 8) & 255) * t), bb = (int) ((a & 255) * (1 - t) + (b & 255) * t);
        return 0xFF000000 | (r << 16) | (gg << 8) | bb;
    }

    static void sky(Platform.Gfx g, int w, int top, int bot) {
        int n = 30;
        float h = Platform.VIEW_H / (float) n;
        for (int i = 0; i < n; i++) g.rect(0, Math.round(i * h), w, Math.round(h) + 1, mix(top, bot, i / (float) (n - 1)), false);
    }

    static void stars(Platform.Gfx g, int w, float t, float[] sx, float[] sy, float[] sp, float alpha) {
        for (int i = 0; i < sx.length; i++) {
            float x = sx[i] % w;
            float a = alpha * (0.35f + 0.65f * (0.5f + 0.5f * (float) Math.sin(t * 1.7f + sp[i])));
            g.rect(Math.round(x), Math.round(sy[i]), (i % 7 == 0) ? 2 : 1, (i % 7 == 0) ? 2 : 1, Mth.withAlpha(0xFFFFFF, (int) (a * 255)), true);
        }
    }

    static void ridge(Platform.Gfx g, int w, float base, float amp, float seed, float scroll, int color) {
        for (int x = 0; x < w + 4; x += 4) {
            float xx = x + scroll;
            float hgt = base - ((float) Math.sin(xx * 0.011f + seed) * 0.6f + (float) Math.sin(xx * 0.027f + seed * 2.3f) * 0.3f + (float) Math.sin(xx * 0.061f + seed) * 0.1f + 0.7f) * amp;
            g.rect(x, Math.round(hgt), 4, Math.round(Platform.VIEW_H - hgt), color, false);
        }
    }

    static void hero(Platform.Gfx g, float x, float y, float s, int col, float capeSway) {
        int c = col;
        g.rect(x - 3 * s, y - 13 * s, 6 * s, 9 * s, c, false);                       // torso
        g.rect(x - 3 * s, y - 4 * s, 2.4f * s, 4 * s, c, false);
        g.rect(x + 0.6f * s, y - 4 * s, 2.4f * s, 4 * s, c, false);
        g.rect(x - 2.5f * s, y - 18 * s, 5 * s, 5 * s, c, false);                    // cabeza
        for (int i = 0; i < 5; i++) g.rect(x - 4 * s - i * 1.6f * s - capeSway * i * 0.4f * s, y - 13 * s + i * 1.6f * s, 2.2f * s, 7 * s + i * 1.5f * s, c, false);   // capa
        g.line(x + 3 * s, y - 9 * s, x + 11 * s, y - 15 * s, Math.max(1, s * 0.9f), c, false);   // espada
    }

    static void draw(Platform.Gfx g, int w, int style, float t, float[] sx, float[] sy, float[] sp) {
        float cx = w / 2f;
        switch (style) {
            case Story.BG_ABYSS: {
                sky(g, w, 0x0A0410, 0x3A0C20);
                stars(g, w, t, sx, sy, sp, 0.8f);
                float rise = Mth.clamp(t / 9f, 0, 1);
                float my = 175 - rise * 85;
                UI.light(g, cx, my, 120, 0xC01830, 0.35f + 0.1f * (float) Math.sin(t * 1.5f));
                g.circle(cx, my, 38, 0xFFD8283C, false);
                g.circle(cx - 8, my - 6, 30, 0x30FF6070, true);
                ridge(g, w, 232, 60, 1.0f, t * 3, 0xFF1A0A18);
                ridge(g, w, 246, 50, 4.0f, t * 7, 0xFF10060E);
                ridge(g, w, 270, 44, 7.0f, t * 14, 0xFF06020A);
                break;
            }
            case Story.BG_SEVEN: {
                sky(g, w, 0x04040C, 0x14102A);
                stars(g, w, t, sx, sy, sp, 0.5f);
                for (int i = 0; i < 4; i++) { float px = cx + (i - 1.5f) * 120; g.rect(px - 7, 40, 14, 190, 0xFF0A0A16, false); g.rect(px - 9, 40, 18, 5, 0xFF121226, false); }
                g.rect(cx - 36, 206, 72, 26, 0xFF0C0C18, false);
                g.rect(cx - 24, 196, 48, 12, 0xFF10101E, false);
                for (int i = 0; i < 7; i++) {
                    float a = t * 0.55f + i * 6.2832f / 7f;
                    float rr = 70 + 8 * (float) Math.sin(t + i);
                    float lx = cx + (float) Math.cos(a) * rr * 1.5f, ly = 112 + (float) Math.sin(a) * rr * 0.45f - Mth.clamp(t * 3, 0, 20);
                    UI.light(g, lx, ly, 26, SEVEN[i], 0.75f);
                    g.circle(lx, ly, 3, 0xFF000000 | SEVEN[i], true);
                    g.line(lx, ly + 3, lx, ly + 17, 2, 0xFF000000 | SEVEN[i], true);
                }
                UI.light(g, cx, 190, 50, 0xFFE9A0, 0.18f + 0.1f * (float) Math.sin(t * 2));
                break;
            }
            case Story.BG_HUNTER: {
                float pulse = 0.5f + 0.5f * (float) Math.sin(t * 1.3f);
                sky(g, w, 0x180408, 0x50101C);
                UI.light(g, cx, 100, 150, 0xFF2040, 0.4f + 0.15f * pulse);
                g.circle(cx, 100, 82, 0xFFB01830, false);
                g.circle(cx - 14, 88, 64, 0x30FF5060, true);
                for (int k = 0; k < 5; k++) g.line(cx - 60 + k * 26, 40 + k * 4, cx - 40 + k * 22, 90 + k * 12, 1, 0x80300008, false);
                ridge(g, w, 250, 36, 2.0f, 0, 0xFF12040A);
                float fs = 5.2f;
                float fy = 262;
                for (int k = 0; k < 14; k++) {                       // capa en trapecio
                    float ww = (8 + k * 1.1f) * fs;
                    g.rect(cx - ww, fy - (34 - k * 2) * fs, ww * 2, 2 * fs + 1, 0xFF050206, false);
                }
                g.rect(cx - 5 * fs, fy - 42 * fs, 10 * fs, 9 * fs, 0xFF050206, false);   // cabeza
                g.line(cx - 4 * fs, fy - 41 * fs, cx - 8 * fs, fy - 52 * fs, fs * 0.9f, 0xFF050206, false);   // cuernos
                g.line(cx + 4 * fs, fy - 41 * fs, cx + 8 * fs, fy - 52 * fs, fs * 0.9f, 0xFF050206, false);
                g.rect(cx - 12 * fs, fy - 33 * fs, 24 * fs, 4 * fs, 0xFF050206, false);    // hombros
                g.rect(cx - 3.5f * fs, fy - 38 * fs, 2 * fs, fs * 0.8f, 0xFFFF2A3A, true);
                g.rect(cx + 1.5f * fs, fy - 38 * fs, 2 * fs, fs * 0.8f, 0xFFFF2A3A, true);
                UI.light(g, cx, fy - 37 * fs, 30, 0xFF2040, 0.5f + 0.3f * pulse);
                g.line(cx + 15 * fs, fy - 28 * fs, cx + 22 * fs, fy - 56 * fs, fs, 0xFF050206, false);
                break;
            }
            case Story.BG_DESCENT: {
                sky(g, w, 0x050A14, 0x1A1018);
                stars(g, w, t, sx, sy, sp, 0.6f);
                UI.light(g, w * 0.72f, 250, 110, 0xFF7A2A, 0.45f + 0.1f * (float) Math.sin(t * 2.2f));
                for (int k = 0; k < 6; k++) g.line(w * 0.72f, 250, w * 0.72f + (k - 2.5f) * 60, 60, 2, 0x18FFA050, true);
                g.rect(0, 190, w * 0.46f, 90, 0xFF0A0A12, false);
                g.rect(w * 0.46f - 14, 196, 14, 90, 0xFF0A0A12, false);
                ridge(g, w, 262, 30, 3.0f, t * 2, 0xFF08060C);
                float hx = Math.min(w * 0.40f, 40 + t * 7);
                hero(g, hx, 190, 2.2f, 0xFF020204, (float) Math.sin(t * 2) * 1.5f);
                break;
            }
            case Story.BG_RELICS: {
                sky(g, w, 0x04040C, 0x1C0C1C);
                stars(g, w, t, sx, sy, sp, 0.5f);
                float p = Mth.clamp(t / 6f, 0, 1);
                p = p * p * (3 - 2 * p);
                UI.light(g, cx, 110, 60, 0xC01830, 0.4f);
                g.circle(cx, 110, 12, 0xFF901028, false);
                for (int i = 0; i < 8; i++) {
                    float a = i * 6.2832f / 8f + t * 0.4f * p;
                    float sx0 = cx + (float) Math.cos(i * 0.9f + 1) * (w * 0.55f), sy0 = 60 + 20 * (float) Math.sin(i * 1.7f);
                    float tx = cx + (float) Math.cos(a) * 62, ty = 110 + (float) Math.sin(a) * 40;
                    float lx = sx0 + (tx - sx0) * p, ly = sy0 + (ty - sy0) * p;
                    int col = i < 7 ? SEVEN[i] : 0xFFFFFF;
                    UI.light(g, lx, ly, 22, col, 0.8f);
                    g.circle(lx, ly, 3, 0xFF000000 | col, true);
                    if (p > 0.95f) { float a2 = (i + 1) * 6.2832f / 8f + t * 0.4f; g.line(lx, ly, cx + (float) Math.cos(a2) * 62, 110 + (float) Math.sin(a2) * 40, 1, Mth.withAlpha(col, 120), true); }
                }
                ridge(g, w, 262, 40, 5.0f, 0, 0xFF06040A);
                break;
            }
            case Story.BG_SHATTER: {
                float c = Mth.clamp(t / 3.2f, 0, 1);
                float fade = Mth.clamp((t - 3.2f) / 3f, 0, 1);
                sky(g, w, mix(0x180408, 0x0A0C18, fade), mix(0x50101C, 0x181C30, fade));
                stars(g, w, t, sx, sy, sp, 0.3f + 0.6f * fade);
                if (fade < 1) {
                    UI.light(g, cx, 100, 140, 0xFF2040, 0.4f * (1 - fade));
                    g.circle(cx, 100, 70, Mth.withAlpha(0xB01830, (int) (255 * (1 - fade))), false);
                    for (int k = 0; k < 9; k++) { float a = k * 0.7f; g.line(cx, 100, cx + (float) Math.cos(a) * 70 * c, 100 + (float) Math.sin(a) * 70 * c, 1, Mth.withAlpha(0xFFE0A0, (int) (230 * (1 - fade))), true); }
                    if (t > 3f && t < 3.5f) g.rect(0, 0, w, Platform.VIEW_H, Mth.withAlpha(0xFFFFFF, (int) ((3.5f - t) * 2 * 160)), true);
                }
                ridge(g, w, 252, 36, 2.0f, 0, 0xFF0A0610);
                break;
            }
            case Story.BG_TRUTH: {
                sky(g, w, 0x050408, 0x120C18);
                g.circle(cx, 170, 62, 0xFF0A0810, false);
                for (int i = 0; i < 8; i++) {
                    float a = i * 6.2832f / 8f - 1.57f;
                    float lx = cx + (float) Math.cos(a) * 130, ly = 170 + (float) Math.sin(a) * 38;
                    int col = i < 7 ? SEVEN[i] : 0xFF2040;
                    float al = i < 7 ? 0.7f : Mth.clamp(t / 5f, 0, 1) * 0.8f;
                    UI.light(g, lx, ly - 14, 24, col, al);
                    g.rect(lx - 1, ly - 28, 2, 30, Mth.withAlpha(col, 200), true);
                    g.rect(lx - 5, ly - 14, 10, 2, Mth.withAlpha(col, 200), true);
                }
                // el cazador de rodillas
                g.rect(cx - 10, 160, 20, 22, 0xFF040306, false);
                g.rect(cx - 6, 148, 12, 12, 0xFF040306, false);
                g.rect(cx - 16, 168, 8, 14, 0xFF040306, false);
                float eye = Mth.clamp(1 - t / 8f, 0, 1);
                UI.light(g, cx, 154, 16, 0xFF2040, 0.5f * eye);
                ridge(g, w, 268, 24, 6.0f, 0, 0xFF040306);
                break;
            }
            default: {   // BG_DAWN
                float r = Mth.clamp(t / 10f, 0, 1);
                sky(g, w, mix(0x1A1830, 0x6A8AC8, r), mix(0x6A3040, 0xFFD890, r));
                UI.light(g, cx + 60, 200 - r * 70, 110, 0xFFD070, 0.55f);
                g.circle(cx + 60, 200 - r * 70, 24, 0xFFFFE8A0, false);
                ridge(g, w, 236, 50, 1.0f, t * 2, mix(0x2A2438, 0x405070, r));
                ridge(g, w, 256, 40, 4.0f, t * 5, mix(0x16121E, 0x203048, r));
                g.rect(0, 232, w * 0.42f, 60, 0xFF0A0A12, false);
                hero(g, Math.min(w * 0.30f, 30 + t * 4), 232, 2.2f, 0xFF050408, (float) Math.sin(t * 1.6f) * 1.2f);
                for (int b = 0; b < 3; b++) {
                    float bx = (t * 22 + b * 90) % (w + 40) - 20, by = 70 + b * 18 + 4 * (float) Math.sin(t * 3 + b);
                    g.line(bx, by, bx + 4, by + 2, 1, 0xFF201830, false);
                    g.line(bx + 4, by + 2, bx + 8, by, 1, 0xFF201830, false);
                }
                break;
            }
        }
    }
}
