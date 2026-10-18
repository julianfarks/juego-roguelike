package com.julianfarks.roguelike.core;

/**
 * Escenas animadas de las cinematicas. Todo procedural (sin imagenes): camara con zoom/pan, capas con parallax,
 * figuras articuladas, poderes elementales, ruptura del sello y luces por escena.
 * Cada escena depende del tiempo de escena (t), de la diapositiva dentro de la escena (k) y del tiempo de la diapositiva (st),
 * asi lo que se ve va sincronizado con el texto.
 */
final class CineArt {
    private CineArt() {}

    static final int[] SEVEN = {0xFFE9A0, 0x9A7AFF, 0xFF7A2A, 0xB8F0FF, 0x6AA8FF, 0x5AE88A, 0xFF4A5A};
    static final String[] SEVEN_NAME = {"Honor", "Silencio", "Voluntad", "Libertad", "Paciencia", "Vida", "Sacrificio"};
    static final int INK = 0xFF050206;

    // ------------------------------------------------------------------ util
    private static int mix(int a, int b, float t) {
        t = Mth.clamp(t, 0, 1);
        int r = (int) (((a >> 16) & 255) * (1 - t) + ((b >> 16) & 255) * t), gg = (int) (((a >> 8) & 255) * (1 - t) + ((b >> 8) & 255) * t), bb = (int) ((a & 255) * (1 - t) + (b & 255) * t);
        return 0xFF000000 | (r << 16) | (gg << 8) | bb;
    }
    static float ss(float x) { x = Mth.clamp(x, 0, 1); return x * x * (3 - 2 * x); }
    static float seg(float t, float a, float b) { return Mth.clamp((t - a) / (b - a), 0, 1); }
    private static float hash(int n) { n = (n << 13) ^ n; return 1f - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824f; }   // -1..1

    /** Camara: zoom alrededor del centro de la pantalla, desplazamiento por capa (depth). */
    static final class Cam {
        final int w; float x, y, zoom = 1;
        Cam(int w) { this.w = w; }
        float X(float wx, float d) { return w / 2f + (wx - w / 2f - x * d) * zoom; }
        float Y(float wy, float d) { return 95 + (wy - 150 - y * d) * zoom; }
        float S(float s) { return s * zoom; }
    }

    /** Camara de cada escena como funcion del tiempo (la usan tanto el dibujo como las particulas). */
    static Cam camera(int w, int style, float t, int k, float st) {
        Cam c = new Cam(w);
        float shake = shake(style, t, k, st);
        switch (style) {
            case Story.BG_ABYSS: c.y = 18 - Math.min(t, 40) * 2.4f; c.zoom = 1f + 0.05f * ss(t / 40f); c.x = (float) Math.sin(t * 0.2f) * 10; break;
            case Story.BG_SEVEN: c.x = Mth.lerp(-150, 150, ss(t / 26f)); c.zoom = 1.22f; c.y = -10; break;
            case Story.BG_HUNTER: c.zoom = 1f + 0.22f * ss(t / 9f) - 0.2f * ss((t - 14f) / 5f); c.y = -14 * ss(t / 9f); c.x = (float) Math.sin(t * 0.3f) * 6; break;
            case Story.BG_DESCENT: {
                float hx = heroX(w, t);
                c.x = Mth.clamp(hx - w * 0.38f, -20, 400); c.zoom = 1.12f + 0.55f * ss((t - 9f) / 8f); c.y = -14 * ss((t - 9f) / 8f);
                if (k >= 1) { c.x = Mth.lerp(c.x, hx - w * 0.30f, ss(st / 3f)); }
                break;
            }
            case Story.BG_RELICS: c.zoom = 1.05f + 0.12f * ss(t / 14f); c.y = -6; break;
            case Story.BG_SHATTER: c.zoom = 1f + 0.1f * ss(t / 6f); break;
            case Story.BG_TRUTH: c.zoom = 1.05f + 0.55f * ss(t / 22f); c.y = -34 * ss(t / 22f); break;
            default: c.x = Math.min(30 + t * 12f, 150) - 100; c.zoom = 1.08f - 0.06f * ss(t / 20f); break;
        }
        c.x += shake * hash((int) (t * 60)) * 1.0f; c.y += shake * hash((int) (t * 60) + 7);
        return c;
    }

    static float shake(int style, float t, int k, float st) {
        switch (style) {
            case Story.BG_DESCENT: if (k == 0) { float p = seg(st, 0.6f, 4.5f); return 5.5f * p * (0.5f + 0.5f * (float) Math.sin(st * 22f)) * (1 - 0.3f * p); } return 0;
            case Story.BG_SHATTER: { if (t > 3.0f && t < 4.2f) return 12 * (1 - seg(t, 3.0f, 4.2f)); if (t < 3) return 2.5f * seg(t, 0, 3f); return 0; }
            case Story.BG_HUNTER: if (k == 1) return 2.5f * (float) Math.max(0, Math.sin(st * 3f)) * (st < 6 ? 1 : 0); return 0;
            default: return 0;
        }
    }

    static float heroX(int w, float t) { return 40 + Math.min(t, 11f) * 17f + Math.max(0, t - 11f) * 2f; }

    // ------------------------------------------------------------------ primitivas con camara
    private static void rect(Platform.Gfx g, Cam c, float x, float y, float w, float h, int col, boolean add, float d) {
        g.rect(c.X(x, d), c.Y(y, d), Math.max(1, c.S(w)), Math.max(1, c.S(h)), col, add);
    }
    private static void circle(Platform.Gfx g, Cam c, float x, float y, float r, int col, boolean add, float d) { g.circle(c.X(x, d), c.Y(y, d), c.S(r), col, add); }
    private static void line(Platform.Gfx g, Cam c, float x0, float y0, float x1, float y1, float th, int col, boolean add, float d) {
        g.line(c.X(x0, d), c.Y(y0, d), c.X(x1, d), c.Y(y1, d), Math.max(1, c.S(th)), col, add);
    }
    private static void light(Platform.Gfx g, Cam c, float x, float y, float r, int col, float a, float d) { UI.light(g, c.X(x, d), c.Y(y, d), c.S(r), col, a); }

    static void sky(Platform.Gfx g, int w, int top, int bot) {
        int n = 30;
        float h = ViewSize.h / (float) n;
        for (int i = 0; i < n; i++) g.rect(0, Math.round(i * h), w, Math.round(h) + 1, mix(top, bot, i / (float) (n - 1)), false);
    }

    static void stars(Platform.Gfx g, Cam c, float t, float[] sx, float[] sy, float[] sp, float alpha) {
        for (int i = 0; i < sx.length; i++) {
            float x = c.X(sx[i] % c.w, 0.05f);
            float a = alpha * (0.35f + 0.65f * (0.5f + 0.5f * (float) Math.sin(t * 1.7f + sp[i])));
            g.rect(Math.round(x), Math.round(c.Y(sy[i], 0.05f)), (i % 7 == 0) ? 2 : 1, (i % 7 == 0) ? 2 : 1, Mth.withAlpha(0xFFFFFF, (int) (a * 255)), true);
        }
    }

    /** Cresta de colinas/rocas con parallax y luz de borde opcional. */
    static void ridge(Platform.Gfx g, Cam c, float base, float amp, float seed, float d, int color, int rim) {
        int w = c.w;
        for (int x = 0; x < w + 4; x += 4) {
            float wx = (x - w / 2f) / c.zoom + w / 2f + c.x * d;
            float hgt = base - ((float) Math.sin(wx * 0.011f + seed) * 0.6f + (float) Math.sin(wx * 0.027f + seed * 2.3f) * 0.3f + (float) Math.sin(wx * 0.061f + seed) * 0.1f + 0.7f) * amp;
            float sy = c.Y(hgt, d);
            g.rect(x, Math.round(sy), 4, Math.round(Math.max(0, ViewSize.h - sy)), color, false);
            if (rim != 0) g.rect(x, Math.round(sy), 4, 1, rim, true);
        }
    }

    // ------------------------------------------------------------------ figuras articuladas
    private static void limb(Platform.Gfx g, Cam c, float x, float y, float ang, float len, float th, int col, float d) {
        line(g, c, x, y, x + (float) Math.sin(ang) * len, y + (float) Math.cos(ang) * len, th, col, false, d);
    }

    /** Espadachin de pie/andando. face=+1 derecha. sword: angulo (0 = hacia abajo, PI = arriba); <-50 sin espada. Devuelve la punta por out[]. */
    static void human(Platform.Gfx g, Cam c, float x, float fy, float s, float d, int col, float phase, float face, float sword, float cape, float[] out) {
        float bob = (float) Math.abs(Math.sin(phase)) * 0.9f * s;
        float hy = fy - 9 * s - bob;                       // cadera
        float la = (float) Math.sin(phase) * 0.55f, ra = -la;
        limb(g, c, x - 1.2f * s, hy, la * face, 9 * s, 2.6f * s, col, d);
        limb(g, c, x + 1.2f * s, hy, ra * face, 9 * s, 2.6f * s, col, d);
        for (int i = 0; i < 6; i++) {                       // capa ondulante hacia atras
            float f = i / 5f;
            float wave = (float) Math.sin(phase * 0.8f + i * 0.9f) * cape * (0.5f + f);
            float cx = x - face * (2.4f + 2.6f * i * (0.6f + cape * 0.25f)) * s, cy = hy - 9 * s + (i * 2.3f + wave) * s;
            rect(g, c, cx - 1.4f * s, cy, 3f * s, (6 + i * 1.2f) * s, col, false, d);
        }
        rect(g, c, x - 3 * s, hy - 11 * s, 6 * s, 11.5f * s, col, false, d);                 // torso
        rect(g, c, x - 2.6f * s, hy - 16 * s, 5.2f * s, 5.2f * s, col, false, d);            // cabeza
        rect(g, c, x - 3.4f * s, hy - 17 * s, 6.8f * s, 2f * s, col, false, d);              // capucha
        float shy = hy - 10 * s;
        limb(g, c, x - face * 1.5f * s, shy, (-la * 0.9f) * face + 0.2f * face, 8 * s, 2.3f * s, col, d);
        float aa = sword > -50 ? (float) Math.PI * 0.62f * face * 0.5f : ra * 0.9f * face;
        float hx = x + face * 1.5f * s + (float) Math.sin(aa) * 8 * s, hyy = shy + (float) Math.cos(aa) * 8 * s;
        limb(g, c, x + face * 1.5f * s, shy, aa, 8 * s, 2.3f * s, col, d);
        if (sword > -50) {
            float ex = hx + (float) Math.sin(sword * face) * 15 * s, ey = hyy + (float) Math.cos(sword) * 15 * s;
            line(g, c, hx - (hx - ex) * 0.12f, hyy - (hyy - ey) * 0.12f, ex, ey, 1.4f * s, col == INK ? 0xFF2A2430 : col, false, d);
            if (out != null) { out[0] = ex; out[1] = ey; out[2] = hx; out[3] = hyy; }
        } else if (out != null) { out[0] = hx; out[1] = hyy; out[2] = hx; out[3] = hyy; }
    }

    /** El Cazador: silueta enorme con cuernos, capa ondeante y ojos rojos. dissolve 0..1 pierde cuernos y capa. */
    static void hunter(Platform.Gfx g, Cam c, float x, float fy, float s, float d, float t, float dissolve, float raise, boolean kneel) {
        float a = 1f - dissolve;
        int col = Mth.withAlpha(0x050206, 255);
        int ca = Mth.withAlpha(0x050206, (int) (255 * a));
        float pulse = 0.5f + 0.5f * (float) Math.sin(t * 1.3f);
        float k = kneel ? 0.62f : 1f;
        float top = fy - 40 * s * k;
        for (int i = 0; i < 12; i++) {                                         // capa: franjas con ondas
            float f = i / 11f;
            float wv = (float) Math.sin(t * 2.2f + f * 4.5f) * (2.5f + 5 * f) * s;
            float yy = top + 7 * s + f * 30 * s * k;
            float hw = (8 + f * 11 + (float) Math.sin(t * 1.7f + i) * 1.2f) * s;
            rect(g, c, x - hw + wv * 0.5f, yy, hw * 2 + wv, 3.1f * s * k, ca, false, d);
        }
        rect(g, c, x - 9 * s, top + 4 * s, 18 * s, 22 * s * k, col, false, d);        // torso
        rect(g, c, x - 13 * s, top + 3 * s, 26 * s, 5 * s, col, false, d);            // hombreras
        rect(g, c, x - 5.5f * s, top - 8 * s * k, 11 * s, 11 * s, col, false, d);        // cabeza
        line(g, c, x - 4 * s, top - 7 * s * k, x - 9 * s, top - 19 * s * k, 1.6f * s, ca, false, d);   // cuernos
        line(g, c, x + 4 * s, top - 7 * s * k, x + 9 * s, top - 19 * s * k, 1.6f * s, ca, false, d);
        line(g, c, x - 9 * s, top - 19 * s * k, x - 7 * s, top - 22 * s * k, 1f * s, ca, false, d);
        line(g, c, x + 9 * s, top - 19 * s * k, x + 7 * s, top - 22 * s * k, 1f * s, ca, false, d);
        float eyeA = (0.6f + 0.4f * pulse) * (kneel ? (1 - dissolve) : 1);
        rect(g, c, x - 3.6f * s, top - 3 * s * k, 2.4f * s, 1f * s, Mth.withAlpha(0xFF2A3A, (int) (255 * eyeA)), true, d);
        rect(g, c, x + 1.2f * s, top - 3 * s * k, 2.4f * s, 1f * s, Mth.withAlpha(0xFF2A3A, (int) (255 * eyeA)), true, d);
        light(g, c, x, top - 3 * s * k, 26 * s, 0xFF2040, 0.55f * eyeA, d);
        // espada colosal: clavada delante o alzada
        float sa = (float) Math.PI * raise;       // 0 = clavada hacia abajo
        float hx = x + 13 * s, hy = top + 12 * s;
        float ex = hx + (float) Math.sin(sa) * 40 * s, ey = hy - (float) Math.cos(sa) * 30 * s + (raise < 0.1f ? 20 * s : 0) * 0;
        if (raise < 0.1f) { ex = hx; ey = fy + 4 * s; line(g, c, hx, hy - 6 * s, ex, ey, 2.2f * s, ca, false, d); }
        else line(g, c, hx - (ex - hx) * 0.2f, hy + (hy - ey) * 0.2f, ex, ey, 2.2f * s, ca, false, d);
        rect(g, c, hx - 4 * s, hy - 6 * s, 8 * s, 1.6f * s, ca, false, d);
    }

    // ------------------------------------------------------------------ elementos
    /** Grieta zigzagueante que va creciendo (0..1). */
    static void crack(Platform.Gfx g, Cam c, float x, float y, float ang, float len, float prog, float th, int col, float d, int seed, boolean add) {
        int n = 14;
        float px = x, py = y;
        for (int i = 1; i <= n && i <= prog * n + 0.999f; i++) {
            float seg = (i <= prog * n) ? 1f : (prog * n) % 1f;
            float a2 = ang + hash(seed + i * 5) * 0.55f;
            float nx = px + (float) Math.cos(a2) * len / n * seg, ny = py + (float) Math.sin(a2) * len / n * seg;
            line(g, c, px, py, nx, ny, th * (1.2f - i / (float) n * 0.6f), col, add, d);
            if (i % 4 == 0) line(g, c, px, py, px + (float) Math.cos(a2 + 0.9f) * len / n * 2.2f * seg, py + (float) Math.sin(a2 + 0.9f) * len / n * 2.2f * seg, th * 0.6f, col, add, d);
            px = nx; py = ny;
        }
    }

    /** Luna roja con terminador y cráteres. */
    static void moon(Platform.Gfx g, Cam c, float x, float y, float r, float t, float intensity, float d) {
        float pulse = 0.5f + 0.5f * (float) Math.sin(t * 1.4f);
        light(g, c, x, y, r * 2.6f, 0xC01830, (0.32f + 0.12f * pulse) * intensity, d);
        light(g, c, x, y, r * 1.5f, 0xFF3048, 0.25f * intensity, d);
        circle(g, c, x, y, r, mix(0xFF701020, 0xFFB01830, intensity), false, d);
        circle(g, c, x - r * 0.18f, y - r * 0.14f, r * 0.82f, 0x40FF6070, true, d);
        circle(g, c, x + r * 0.30f, y + r * 0.22f, r * 0.14f, 0x50601018, false, d);
        circle(g, c, x - r * 0.35f, y + r * 0.30f, r * 0.10f, 0x50601018, false, d);
        circle(g, c, x + r * 0.05f, y - r * 0.42f, r * 0.08f, 0x50601018, false, d);
    }

    /** Siete figuras en el acantilado. */
    static float sevenX(int w, int i) { return w / 2f + (i - 3) * 62f; }

    // ------------------------------------------------------------------ DIBUJO
    static void draw(Platform.Gfx g, int w, int style, float t, int k, float st, float[] sx, float[] sy, float[] sp) {
        Cam c = camera(w, style, t, k, st);
        float cx = w / 2f;
        float[] o = new float[4];
        switch (style) {
            case Story.BG_ABYSS: {
                float rise = ss(t / 20f);
                sky(g, w, 0x0A0410, mix(0x2A0818, 0x4A1024, rise));
                stars(g, c, t, sx, sy, sp, 0.8f);
                float my = 215 - rise * 120;
                moon(g, c, cx, my, 40, t, ss(t / 4f), 0.12f);
                // el cielo se parte (diapositiva 0), grietas crecen, destello blanco
                float cr = k == 0 ? ss(st / 5f) : 1f;
                for (int i = 0; i < 4; i++) crack(g, c, cx + (i - 1.5f) * 70, -20, 1.5f + hash(i * 3) * 0.3f, 180 + 40 * i, cr, 1.3f, 0xFFFFD0C0, 0.1f, 11 + i * 17, true);
                if (k == 0) { float f = seg(st, 4.6f, 5.0f) * (1 - seg(st, 5.0f, 6.2f)); if (f > 0) g.rect(0, 0, w, ViewSize.h, Mth.withAlpha(0xFFE0D0, (int) (f * 150)), true); }
                ridge(g, c, 232, 60, 1.0f, 0.3f, 0xFF1A0A18, 0x50A02030);
                ridge(g, c, 246, 50, 4.0f, 0.6f, 0xFF10060E, 0x30801828);
                // reinos que caen (diapositiva 2): torres inclinandose y hundiendose, con fuego
                float fall = k >= 2 ? ss(st / 5f) : (k == 1 ? 0 : 0);
                for (int i = 0; i < 7; i++) {
                    float tx = 60 + i * (w / 7f) + hash(i) * 14, th = 26 + 18 * (0.5f + 0.5f * hash(i + 9));
                    float sink = fall * (20 + 14 * (i % 3)), tilt = fall * hash(i + 2) * 0.35f;
                    float by = 258 + sink;
                    for (int r = 0; r < 8; r++) {
                        float f = r / 7f;
                        rect(g, c, tx - 5 + tilt * f * th * 0.6f, by - th * (f + 0.14f), 10 - f * 2, th / 7f + 1, 0xFF0A0408, false, 0.85f);
                    }
                    rect(g, c, tx - 7 + tilt * th * 0.6f, by - th - 3, 14, 3, 0xFF0A0408, false, 0.85f);
                    if (k >= 2) { float fl = 0.6f + 0.4f * (float) Math.sin(t * 9 + i * 2); light(g, c, tx + tilt * th * 0.5f, by - th * 0.5f, 22 + 6 * fl, 0xFF6A20, 0.5f * fl * Math.min(1, st / 2f), 0.85f); }
                }
                ridge(g, c, 270, 44, 7.0f, 1.0f, 0xFF06020A, 0);
                break;
            }
            case Story.BG_SEVEN: {
                sky(g, w, 0x04040C, 0x14102A);
                stars(g, c, t, sx, sy, sp, 0.5f);
                moon(g, c, cx + 20, 60, 22, t, 0.6f, 0.08f);
                // columnas rotas al fondo
                for (int i = -2; i < 7; i++) { float px = cx + (i - 2.5f) * 120; float hh = 120 + 40 * hash(i + 20); rect(g, c, px - 7, 215 - hh, 14, hh, 0xFF14142A, false, 0.35f); rect(g, c, px - 9, 215 - hh, 18, 5, 0xFF1E1E3A, false, 0.35f); }
                ridge(g, c, 255, 38, 2.0f, 0.6f, 0xFF0A0A18, 0x20404068);
                // acantilado con losas
                rect(g, c, cx - 340, 205, 700, 90, 0xFF0C0C18, false, 1f);
                rect(g, c, cx - 340, 205, 700, 2, 0x70504878, false, 1f);
                light(g, c, cx, 200, 260, 0x504070, 0.22f, 0.9f);
                // aparicion escalonada: la figura i aparece en st=i*0.6 de la diapositiva 0
                for (int i = 0; i < 7; i++) {
                    float appear = k == 0 ? ss((st - i * 0.9f) / 1.2f) : 1f;
                    if (appear <= 0) continue;
                    float fx = sevenX(w, i), col = appear;
                    int ink = Mth.withAlpha(0x020206, (int) (255 * col));
                    float raise = k >= 2 ? ss((st - i * 0.15f) / 1.2f) : 0f;
                    float sw = Mth.lerp(0.25f, 3.0f, raise);                 // angulo de la espada: baja -> en alto
                    float s = 1.6f + 0.15f * (i == 3 ? 1 : 0);
                    human(g, c, fx, 205, s, 1f, ink, 0, i < 3 ? 1 : (i > 3 ? -1 : 1), sw, 1.2f, o);
                    float pw = k >= 1 ? ss(st / 1.5f) : 0.25f * appear;      // el poder de la espada se enciende en la diapositiva 1
                    if (k >= 2) pw = 1;
                    float tipX = o[0], tipY = o[1];
                    light(g, c, tipX, tipY, 10 + 16 * pw, SEVEN[i], (0.15f + 0.5f * pw) * appear, 1f);
                    light(g, c, fx, 185, 34, SEVEN[i], 0.08f * appear + 0.08f * pw, 1f);
                    if (pw > 0.3f) powerFx(g, c, i, tipX, tipY, t, pw);
                    if (k >= 2) {    // rayos hacia la luna: forman la cadena del sello
                        float bp = ss((st - 1f) / 2.2f);
                        float ly = Mth.lerp(tipY, 40, bp);
                        line(g, c, tipX, tipY, Mth.lerp(tipX, cx + 20, bp), ly, 1.6f, Mth.withAlpha(SEVEN[i], 170), true, 1f);
                    }
                }
                if (k >= 2) { float p = ss((st - 2.2f) / 2.5f); for (int j = 0; j < 14; j++) { float a = j / 14f * 6.2832f; float rr = 34 * p; circle(g, c, cx + 20 + (float) Math.cos(a + t * 0.8f) * rr, 60 + (float) Math.sin(a + t * 0.8f) * rr, 1.6f, Mth.withAlpha(0xFFE9A0, (int) (230 * p)), true, 0.08f); } }
                break;
            }
            case Story.BG_HUNTER: {
                float pulse = 0.5f + 0.5f * (float) Math.sin(t * 1.3f);
                sky(g, w, 0x180408, 0x50101C);
                moon(g, c, cx, 100, 82, t, 1f, 0.1f);
                for (int j = 0; j < 8; j++) { float a = j * 0.8f + t * 0.05f; line(g, c, cx, 100, cx + (float) Math.cos(a) * 340, 100 + (float) Math.sin(a) * 340, 22, Mth.withAlpha(0xFF2040, (int) (10 + 10 * pulse)), true, 0.1f); }   // rayos de luna
                ridge(g, c, 246, 40, 2.0f, 0.5f, 0xFF16060C, 0x40A02030);
                ridge(g, c, 262, 36, 5.0f, 0.8f, 0xFF0E040A, 0);
                if (k == 1) {           // las siete espadas caen y se quiebran contra su sombra
                    for (int i = 0; i < 7; i++) {
                        float p = seg(st, i * 0.35f, i * 0.35f + 1.3f);
                        float sxx = cx - 150 + i * 50, syy = Mth.lerp(-40, 168, p * p);
                        if (p > 0 && p < 1) { line(g, c, sxx, syy - 14, sxx - 3, syy, 1.6f, 0xFF000000 | SEVEN[i], true, 1f); light(g, c, sxx, syy, 18, SEVEN[i], 0.7f, 1f); }
                        if (p >= 1) { float q = seg(st, i * 0.35f + 1.3f, i * 0.35f + 2.4f); for (int s = 0; s < 6; s++) { float a = -1.57f + (s - 2.5f) * 0.5f; circle(g, c, sxx + (float) Math.cos(a) * q * 26, 168 + (float) Math.sin(a) * q * 22 + q * q * 18, 1.5f * (1 - q), 0xFF000000 | SEVEN[i], true, 1f); }
                            light(g, c, sxx, 168, 20 * (1 - q) + 4, SEVEN[i], 0.8f * (1 - q), 1f); }
                    }
                }
                if (k >= 2) {           // las ocho reliquias caen como brasas hacia el abismo
                    for (int i = 0; i < 8; i++) {
                        float p = ss(st / 6f), sway = (float) Math.sin(t * 1.5f + i) * 8;
                        float rx = cx - 190 + i * 54 + sway, ry = Mth.lerp(60 + (i % 3) * 18, 285, p * p + 0.0f);
                        int col = i < 7 ? SEVEN[i] : 0xFFFFFF;
                        light(g, c, rx, ry, 18, col, 0.8f * (1 - p * 0.6f), 1f);
                        circle(g, c, rx, ry, 2.5f, 0xFF000000 | col, true, 1f);
                        line(g, c, rx, ry, rx - sway * 0.2f, ry - 18 - 12 * p, 1, Mth.withAlpha(col, 120), true, 1f);
                    }
                }
                float hy = 262, hs = 2.9f;
                float raise = k == 1 ? ss((st - 0.5f) / 2f) * 0.4f : 0f;
                hunter(g, c, cx, hy, hs, 1f, t, 0f, raise, false);
                // bruma de calor/ascuas delante
                rect(g, c, cx - 300, 252, 600, 30, 0x30401018, false, 1.35f);
                break;
            }
            case Story.BG_DESCENT: {
                float rup = k == 0 ? ss(st / 4.5f) : 1f;         // el sello se rompe en la diapositiva 0
                sky(g, w, mix(0x050A14, 0x1C0A14, rup * 0.7f), mix(0x1A1018, 0x3A1218, rup * 0.6f));
                stars(g, c, t, sx, sy, sp, 0.6f);
                // el Sello en el cielo: anillo de runas
                float sxp = w * 0.72f, syp = 118, sr = 52;
                float flick = k == 0 ? 0.55f + 0.45f * hash((int) (st * 14)) * (0.5f + rup * 0.5f) : 0.35f + 0.1f * (float) Math.sin(t * 3);
                light(g, c, sxp, syp, sr * 2.2f, mix(0xB8F0FF, 0xFF2040, rup) & 0xFFFFFF, 0.28f * flick + 0.15f * rup, 0.1f);
                for (int j = 0; j < 40; j++) {
                    float a = j / 40f * 6.2832f + t * 0.15f;
                    boolean broken = rup > 0.25f && (hash(j * 7) > 1f - 1.6f * rup);
                    if (broken) continue;
                    float rr = sr + (j % 5 == 0 ? 5 : 0);
                    rect(g, c, sxp + (float) Math.cos(a) * rr - 1, syp + (float) Math.sin(a) * rr - 1, (j % 5 == 0) ? 3 : 2, (j % 5 == 0) ? 3 : 2, mix(0xFFB8F0FF, 0xFFFF3040, rup), true, 0.1f);
                }
                circle(g, c, sxp, syp, sr * 0.82f, Mth.withAlpha(0xFF2040, (int) (50 * rup + 10)), true, 0.1f);
                for (int i = 0; i < 5; i++) crack(g, c, sxp, syp, i * 1.26f + 0.3f, 80 * rup + 6, rup, 1.4f, 0xFFFF4050, 0.1f, 40 + i * 9, true);
                if (k == 0 && st > 2.2f && st < 2.5f) g.rect(0, 0, w, ViewSize.h, Mth.withAlpha(0xFF3040, (int) ((2.5f - st) * 3.3f * 90)), true);
                // brasas del horizonte
                light(g, c, w * 0.72f, 250, 110, 0xFF7A2A, 0.35f + 0.1f * (float) Math.sin(t * 2.2f), 0.5f);
                ridge(g, c, 255, 44, 3.0f, 0.4f, 0xFF0C0A14, 0x30502030);
                // acantilado + héroe caminando
                rect(g, c, -300, 192, w * 0.46f + 300, 120, 0xFF0A0A12, false, 1f);
                rect(g, c, -300, 192, w * 0.46f + 300, 1, 0x40604860, false, 1f);
                rect(g, c, w * 0.46f - 14, 198, 14, 100, 0xFF0A0A12, false, 1f);
                float hx = heroX(w, t);
                float stopAt = w * 0.46f - 40;
                hx = Math.min(hx, stopAt);
                boolean walking = hx < stopAt - 0.5f;
                float sw = -99f;
                if (k >= 2) sw = Mth.lerp(0.4f, 3.1f, ss(st / 1.4f));
                human(g, c, hx, 192, 2.2f, 1f, 0xFF020204, walking ? t * 7f : 0f, 1f, sw, walking ? 1.8f : 1.1f, o);
                if (k >= 2) {    // la espada prestada se enciende con un tenue destello
                    float glow = seg(st, 1.2f, 3.5f);
                    light(g, c, o[0], o[1], 10 + 26 * glow, 0xFFE9A0, 0.15f + 0.6f * glow, 1f);
                    float gl = seg(st, 2f, 3f) * (1 - seg(st, 3f, 4.2f));
                    if (gl > 0) { line(g, c, o[2], o[3], o[0], o[1], 2.4f, Mth.withAlpha(0xFFFFFF, (int) (gl * 220)), true, 1f); }
                }
                if (k == 1) { float p = seg(st, 0.5f, 3f); light(g, c, hx + 8, 170, 20 * p, 0xFF7A2A, 0.2f * p, 1f); }   // mira al abismo
                rect(g, c, -300, 248, w + 800, 60, 0x601A0A10, false, 1.3f);
                break;
            }
            case Story.BG_RELICS: {
                sky(g, w, 0x04040C, 0x1C0C1C);
                stars(g, c, t, sx, sy, sp, 0.5f);
                float p = ss(t / 7f);
                float ringA = k >= 1 ? ss(st / 3f) : 0f;
                light(g, c, cx, 130, 90 + 40 * ringA, 0xC01830, 0.35f + 0.2f * ringA, 0.4f);
                // el Cazador, pequeño y quieto en el centro
                hunter(g, c, cx, 205, 1.5f, 0.6f, t, 0f, 0f, false);
                for (int i = 0; i < 8; i++) {
                    float a = i * 6.2832f / 8f + t * 0.45f * p;
                    float sx0 = cx + (float) Math.cos(i * 0.9f + 1) * (w * 0.6f), sy0 = 30 + 40 * (float) Math.sin(i * 1.7f);
                    float tx = cx + (float) Math.cos(a) * 78, ty = 135 + (float) Math.sin(a) * 38;
                    float lx = sx0 + (tx - sx0) * p, ly = sy0 + (ty - sy0) * p;
                    int col = i < 7 ? SEVEN[i] : 0xFFFFFF;
                    // estela
                    for (int s2 = 1; s2 <= 6; s2++) { float pp = Math.max(0, p - s2 * 0.018f); float tl = (cx + (float) Math.cos(a - 0.12f * s2) * 78) , tt = 135 + (float) Math.sin(a - 0.12f * s2) * 38; circle(g, c, sx0 + (tl - sx0) * pp, sy0 + (tt - sy0) * pp, 2.2f - s2 * 0.3f, Mth.withAlpha(col, 140 - s2 * 20), true, 0.6f); }
                    light(g, c, lx, ly, 22, col, 0.85f, 0.6f);
                    circle(g, c, lx, ly, 3.2f, 0xFF000000 | col, true, 0.6f);
                    if (p > 0.9f) { float a2 = (i + 1) * 6.2832f / 8f + t * 0.45f; line(g, c, lx, ly, cx + (float) Math.cos(a2) * 78, 135 + (float) Math.sin(a2) * 38, 1.2f, Mth.withAlpha(col, (int) (140 + 60 * ringA)), true, 0.6f); }
                }
                if (k >= 1) {   // sello completo: rayos hacia el Cazador y runa
                    for (int j = 0; j < 24; j++) { float a = j / 24f * 6.2832f - t * 0.3f; float rr = 96 + 4 * (float) Math.sin(t * 2 + j); circle(g, c, cx + (float) Math.cos(a) * rr, 135 + (float) Math.sin(a) * rr * 0.5f, 1.4f, Mth.withAlpha(0xFFE9A0, (int) (210 * ringA)), true, 0.6f); }
                    for (int i = 0; i < 7; i++) { float a = i * 6.2832f / 7f + t * 0.3f; line(g, c, cx + (float) Math.cos(a) * 96, 135 + (float) Math.sin(a) * 48, cx, 168, 1f, Mth.withAlpha(SEVEN[i], (int) (90 * ringA)), true, 0.6f); }
                }
                ridge(g, c, 262, 40, 5.0f, 0.9f, 0xFF06040A, 0);
                break;
            }
            case Story.BG_SHATTER: {
                float cr = ss(t / 3.0f);
                float after = ss((t - 3.4f) / 3f);
                sky(g, w, mix(0x180408, 0x0A0C18, after), mix(0x50101C, 0x181C30, after));
                stars(g, c, t, sx, sy, sp, 0.25f + 0.6f * after);
                float mx = cx, my = 100;
                if (t < 3.3f) {
                    moon(g, c, mx, my, 74, t, 1f - 0.2f * cr, 0.1f);
                    for (int i = 0; i < 9; i++) crack(g, c, mx, my, i * 0.7f, 90, cr, 1.5f, 0xFFFFE8B0, 0.1f, 70 + i * 13, true);
                    light(g, c, mx, my, 40 + 140 * cr, 0xFFE0A0, 0.15f + 0.6f * cr * cr, 0.1f);
                } else {
                    // fragmentos de luna que se apagan y caen
                    float q = seg(t, 3.3f, 8f);
                    for (int i = 0; i < 14; i++) {
                        float a = i / 14f * 6.2832f + hash(i) * 0.3f, dist = 14 + 100 * ss(q * 1.4f) * (0.6f + 0.4f * (0.5f + 0.5f * hash(i + 3)));
                        float fx = mx + (float) Math.cos(a) * dist, fy = my + (float) Math.sin(a) * dist + q * q * 90 * (0.5f + 0.5f * hash(i + 1));
                        int col = mix(0xFFFFB070, 0xFF200810, q * 1.3f);
                        circle(g, c, fx, fy, (6 + 4 * (0.5f + 0.5f * hash(i + 9))) * (1 - 0.6f * q), col, false, 0.1f);
                        light(g, c, fx, fy, 14 * (1 - q), 0xFF5030, 0.5f * (1 - q), 0.1f);
                    }
                    light(g, c, mx, my, 160 * (1 - q), 0xFFE0A0, 0.4f * (1 - q), 0.1f);
                    // onda expansiva
                    float ring = seg(t, 3.3f, 5.4f); if (ring < 1) g.circle(c.X(mx, 0.1f), c.Y(my, 0.1f), c.S(30 + ring * 420), Mth.withAlpha(0xFFFFFF, (int) (70 * (1 - ring))), true);
                }
                if (t > 2.9f && t < 3.7f) g.rect(0, 0, w, ViewSize.h, Mth.withAlpha(0xFFFFFF, (int) (Mth.clamp(1 - Math.abs(t - 3.2f) * 2.2f, 0, 1) * 235)), true);
                ridge(g, c, 252, 36, 2.0f, 0.7f, 0xFF0A0610, mix(0xFF000000, 0xFF405070, after) & 0xFFFFFF | 0x30000000);
                // el Cazador mirando sus manos (slide 1): silueta que baja la cabeza
                hunter(g, c, cx, 262, 2.9f, 1f, t, (k >= 1 ? ss(st / 6f) * 0.25f : 0), 0f, false);
                break;
            }
            case Story.BG_TRUTH: {
                sky(g, w, 0x050408, 0x120C18);
                stars(g, c, t, sx, sy, sp, 0.35f);
                float dis = k == 0 ? ss(st / 6f) * 0.5f : (k == 1 ? 0.5f + ss(st / 6f) * 0.3f : 0.8f + ss(st / 6f) * 0.2f);
                // columnas de luz de los siete + el octavo (el Cazador)
                for (int i = 0; i < 8; i++) {
                    float a = i * 6.2832f / 8f - 1.57f;
                    float lx = cx + (float) Math.cos(a) * 140, ly = 172 + (float) Math.sin(a) * 40;
                    int col = i < 7 ? SEVEN[i] : 0xFF2040;
                    float al = i < 7 ? 0.7f : Mth.clamp(t / 6f, 0, 1) * 0.8f;
                    light(g, c, lx, ly - 14, 26, col, al * (0.8f + 0.2f * (float) Math.sin(t * 2 + i)), 0.8f);
                    rect(g, c, lx - 1, ly - 30, 2, 32, Mth.withAlpha(col, 200), true, 0.8f);
                    rect(g, c, lx - 5, ly - 15, 10, 2, Mth.withAlpha(col, 200), true, 0.8f);
                    // chispas ascendentes
                    for (int s2 = 0; s2 < 3; s2++) { float f = (t * 0.4f + s2 / 3f + i * 0.13f) % 1f; circle(g, c, lx + hash(i * 9 + s2) * 4, ly - 30 - f * 50, 1.1f, Mth.withAlpha(col, (int) (180 * (1 - f))), true, 0.8f); }
                }
                // suelo de piedra
                rect(g, c, cx - 280, 182, 560, 120, 0xFF08060C, false, 1f);
                rect(g, c, cx - 280, 182, 560, 1, 0x40503858, false, 1f);
                // el Cazador de rodillas: la armadura se disuelve en particulas y queda una figura humana
                float eye = Mth.clamp(1 - t / 8f, 0, 1);
                hunter(g, c, cx, 182, 2.8f, 1f, t, Math.min(1f, dis), 0f, true);
                // figura humana que emerge (cálida)
                float hum = Mth.clamp((dis - 0.35f) / 0.65f, 0, 1);
                if (hum > 0) { int hc = Mth.withAlpha(0x1A1420, (int) (255 * hum)); rect(g, c, cx - 7, 154, 14, 28, hc, false, 1f); rect(g, c, cx - 5, 138, 10, 12, hc, false, 1f); light(g, c, cx, 150, 40 * hum, 0xFFE9A0, 0.3f * hum, 1f); }
                // motas de ceniza que se sueltan del Cazador
                for (int s2 = 0; s2 < 12; s2++) { float f = (t * 0.35f + s2 * 0.083f) % 1f; if (dis > 0.05f) circle(g, c, cx + hash(s2 + 90) * 26 + f * 20, 165 - f * 70, 1.6f, Mth.withAlpha(0x302030, (int) (200 * (1 - f) * Math.min(1, dis * 2))), false, 1f); }
                break;
            }
            default: {   // BG_DAWN
                float r = ss(t / 14f);
                sky(g, w, mix(0x1A1830, 0x6A8AC8, r), mix(0x6A3040, 0xFFD890, r));
                float sunY = 205 - r * 85;
                light(g, c, cx + 90, sunY, 150, 0xFFD070, 0.45f + 0.2f * r, 0.08f);
                circle(g, c, cx + 90, sunY, 24, 0xFFFFE8A0, false, 0.08f);
                for (int j = 0; j < 7; j++) { float a = -1.2f + j * 0.4f; line(g, c, cx + 90, sunY, cx + 90 + (float) Math.cos(a) * 320, sunY + (float) Math.sin(a) * 320, 14, Mth.withAlpha(0xFFE9A0, (int) (14 * r)), true, 0.08f); }
                for (int b = 0; b < 3; b++) {   // nubes
                    float nx = ((t * (4 + b) + b * 170) % (w + 240)) - 120;
                    rect(g, c, nx, 40 + b * 22, 90, 5, mix(0xFF3A3048, 0xFFFFE0C0, r), false, 0.12f);
                }
                ridge(g, c, 236, 50, 1.0f, 0.3f, mix(0xFF2A2438, 0xFF405070, r), mix(0xFF000000, 0xFFFFD090, r) & 0xFFFFFF | 0x40000000);
                ridge(g, c, 256, 40, 4.0f, 0.6f, mix(0xFF16121E, 0xFF203048, r), 0);
                rect(g, c, -200, 232, w * 0.9f + 400, 120, 0xFF0A0A12, false, 1f);
                rect(g, c, -200, 232, w * 0.9f + 400, 1, mix(0xFF000000, 0xFFFFD090, r) & 0xFFFFFF | 0x60000000, false, 1f);
                // siete espadas clavadas descansando en la cima, con brillo suave
                for (int i = 0; i < 7; i++) {
                    float sxp = 200 + i * 38, sh = 18 + (i % 3) * 3;
                    line(g, c, sxp, 232, sxp, 232 - sh, 1.6f, 0xFF0A0810, false, 1f);
                    rect(g, c, sxp - 4, 232 - sh + 3, 8, 1.6f, 0xFF0A0810, false, 1f);
                    light(g, c, sxp, 232 - sh, 10 + 4 * (float) Math.sin(t * 2 + i), SEVEN[i], 0.4f * r + 0.1f, 1f);
                }
                float hx = Math.min(30 + t * 12f, 150);
                boolean walk = hx < 149;
                human(g, c, hx, 232, 2.2f, 1f, 0xFF050408, walk ? t * 6f : 0f, 1f, -99f, walk ? 1.6f : 1f, o);
                for (int b = 0; b < 4; b++) {   // pajaros
                    float bx = (t * 24 + b * 90) % (w + 60) - 30, by = 70 + b * 16 + 4 * (float) Math.sin(t * 3 + b);
                    float fl = (float) Math.sin(t * 9 + b * 2) * 3;
                    line(g, c, bx, by, bx + 4, by + 2 + fl, 1, 0xFF201830, false, 0.5f);
                    line(g, c, bx + 4, by + 2 + fl, bx + 8, by, 1, 0xFF201830, false, 0.5f);
                }
                break;
            }
        }
    }

    /** Efecto elemental propio de cada espada (Honor, Silencio, Voluntad, Libertad, Paciencia, Vida, Sacrificio). */
    private static void powerFx(Platform.Gfx g, Cam c, int i, float x, float y, float t, float pw) {
        int col = SEVEN[i];
        switch (i) {
            case 0: for (int j = 0; j < 6; j++) { float a = j * 1.0472f + t; line(g, c, x, y, x + (float) Math.cos(a) * 18 * pw, y + (float) Math.sin(a) * 18 * pw, 1, Mth.withAlpha(col, 160), true, 1f); } break;     // rayos sagrados
            case 1: for (int j = 0; j < 5; j++) { float f = (t * 0.8f + j * 0.2f) % 1f; circle(g, c, x + (float) Math.sin(t * 2 + j) * 5, y - f * 24, 3 * (1 - f) + 1, Mth.withAlpha(0x6040A0, (int) (150 * (1 - f))), false, 1f); } break;                                  // humo de sombra
            case 2: for (int j = 0; j < 5; j++) { float f = (t * 1.6f + j * 0.2f) % 1f; circle(g, c, x + (float) Math.sin(t * 7 + j * 2) * 3, y - f * 20, 3 * (1 - f) + 0.6f, Mth.withAlpha(j % 2 == 0 ? 0xFFB040 : 0xFF5010, (int) (230 * (1 - f))), true, 1f); } break;  // llamas
            case 3: for (int j = 0; j < 4; j++) { float a = t * 3 + j * 1.57f; line(g, c, x + (float) Math.cos(a) * 9, y + (float) Math.sin(a) * 5, x + (float) Math.cos(a + 0.9f) * 11, y + (float) Math.sin(a + 0.9f) * 6, 1, Mth.withAlpha(0xFFFFFF, 190), true, 1f); } break;                            // viento
            case 4: for (int j = 0; j < 4; j++) { float f = (t * 0.5f + j * 0.25f) % 1f; rect(g, c, x - 6 + j * 4, y - 3 - f * 16, 1.6f, 4, Mth.withAlpha(col, (int) (200 * (1 - f))), true, 1f); } break;                                                                // cristales/agua
            case 5: for (int j = 0; j < 4; j++) { float f = (t * 0.5f + j * 0.25f) % 1f; rect(g, c, x + (float) Math.sin(t * 2 + j * 2) * 8, y - f * 22, 2.2f, 1.4f, Mth.withAlpha(0x5AE88A, (int) (220 * (1 - f))), false, 1f); } break;                                                     // hojas
            default: for (int j = 0; j < 3; j++) { float f = (t * 0.9f + j * 0.33f) % 1f; circle(g, c, x + (j - 1) * 3, y + f * 20, 1.8f * (1 - f) + 0.5f, Mth.withAlpha(0xC01020, (int) (230 * (1 - f))), false, 1f); }                                                                  // gotas de sangre
        }
    }

    // ------------------------------------------------------------------ particulas ambientales (tiempo real)
    static void update(float dt, Particles ps, Rng rng, int w, int style, float t, int k, float st) {
        Cam c = camera(w, style, t, k, st);
        int H = ViewSize.h;
        switch (style) {
            case Story.BG_ABYSS:
                if (rng.chance(dt * 14)) ps.spawn(rng.f(0, w), -4, rng.f(-8, 14), rng.f(10, 28), rng.f(5, 9), 1, 0, rng.chance(0.5f) ? 0xAA8890 : 0xD04050, false);
                if (k >= 2 && rng.chance(dt * 40)) ps.spawn(rng.f(0, w), rng.f(150, 250), rng.f(-14, 14), -rng.f(20, 50), rng.f(1.5f, 3.5f), rng.chance(0.3f) ? 2 : 1, 0, rng.chance(0.5f) ? 0xFF8A3A : 0x907060, rng.chance(0.5f));   // humo y brasas
                if (k == 0 && st > 4.6f && st < 5.2f) for (int i = 0; i < 6; i++) ps.spawn(rng.f(0, w), rng.f(0, 120), rng.f(-80, 80), rng.f(-30, 80), rng.f(0.6f, 1.4f), 2, 90, 0xFFE0C0, true);
                break;
            case Story.BG_SEVEN: {
                if (rng.chance(dt * 8)) ps.spawn(rng.f(0, w), rng.f(150, 235), rng.f(-6, 6), -rng.f(6, 18), rng.f(3, 6), 1, 0, 0xFFE8A0, true);
                if (rng.chance(dt * 25)) ps.spawn(rng.f(0, w), 240, rng.f(20, 60), -rng.f(2, 8), rng.f(2, 4), 1, 0, 0x404060, false);   // polvo que arrastra el viento
                break;
            }
            case Story.BG_HUNTER:
                if (rng.chance(dt * 30)) ps.spawn(rng.f(0, w), H + 3, rng.f(-10, 10), -rng.f(14, 50), rng.f(4, 8), 1, 0, rng.chance(0.5f) ? 0xFF4A3A : 0xFF8A3A, true);
                if (rng.chance(dt * 10)) ps.spawn(rng.f(0, w), -4, rng.f(-10, 10), rng.f(10, 30), rng.f(5, 9), 1, 0, 0x907080, false);
                break;
            case Story.BG_DESCENT:
                if (rng.chance(dt * 18)) ps.spawn(rng.f(0, w), H + 3, rng.f(-10, 10), -rng.f(14, 40), rng.f(4, 8), rng.chance(0.3f) ? 2 : 1, 0, rng.chance(0.5f) ? 0xFF8A3A : 0xFFD070, true);
                if (k == 0 && st > 1f && rng.chance(dt * 60 * seg(st, 1f, 4.5f))) ps.spawn(c.X(w * 0.72f, 0.1f) + rng.f(-40, 40), c.Y(118, 0.1f) + rng.f(-30, 30), rng.f(-40, 40), rng.f(10, 70), rng.f(1, 2.2f), 1 + rng.i(2), 60, 0xFF3040, true);   // chispas del sello al romperse
                { float hx = heroX(w, t); if (hx < w * 0.46f - 41 && rng.chance(dt * 14)) ps.spawn(c.X(hx - 3, 1f), c.Y(192, 1f), rng.f(-14, -4), -rng.f(2, 10), rng.f(0.6f, 1.2f), 1, 0, 0x6A5A60, false); }   // polvo de los pasos
                break;
            case Story.BG_RELICS:
                if (rng.chance(dt * 22)) { float a = rng.f(0, 6.28f); ps.spawn(w / 2f + (float) Math.cos(a) * 80, 135 + (float) Math.sin(a) * 40, (float) Math.cos(a) * 6, -rng.f(6, 20), rng.f(1.5f, 3), 1, 0, rng.chance(0.5f) ? 0xFFE8A0 : 0xFFFFFF, true); }
                break;
            case Story.BG_SHATTER:
                if (t > 3.2f && rng.chance(dt * 50)) ps.spawn(w / 2f + rng.f(-90, 90), rng.f(30, 150), rng.f(-30, 30), rng.f(10, 60), rng.f(3, 6), rng.chance(0.4f) ? 3 : 2, 90, rng.chance(0.5f) ? 0xE04050 : 0xFFB070, rng.chance(0.5f));
                if (t > 2.9f && t < 3.4f) for (int i = 0; i < 8; i++) ps.spawn(w / 2f, 100, rng.f(-160, 160), rng.f(-160, 160), rng.f(0.5f, 1.5f), 2, 40, 0xFFE8B0, true);
                break;
            case Story.BG_TRUTH:
                if (rng.chance(dt * 12)) ps.spawn(rng.f(0, w), H + 3, rng.f(-6, 6), -rng.f(8, 24), rng.f(5, 9), 1, 0, rng.chance(0.5f) ? 0xFFD070 : 0xFF4050, true);
                break;
            default:
                if (rng.chance(dt * 12)) ps.spawn(rng.f(0, w), rng.f(100, 230), rng.f(10, 25), -rng.f(2, 10), rng.f(3, 6), 1, 0, 0xFFE8A0, true);     // polen/luz
                { float hx = Math.min(30 + t * 12f, 150); if (hx < 149 && rng.chance(dt * 12)) ps.spawn(c.X(hx - 3, 1f), c.Y(232, 1f), rng.f(-14, -4), -rng.f(2, 10), rng.f(0.6f, 1.2f), 1, 0, 0x9A8A80, false); }
        }
    }
}
