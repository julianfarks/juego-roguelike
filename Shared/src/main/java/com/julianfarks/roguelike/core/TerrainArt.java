package com.julianfarks.roguelike.core;

import java.util.List;

/**
 * Arte procedural de suelos, plataformas y fondo de cada sala (se ejecuta al "hornear" la sala, una sola vez).
 *
 * En lugar de repetir baldosas de 16x16 px, el terreno se pinta en coordenadas de MUNDO:
 *  - mamposteria con hiladas y sillares de tamano distinto, tono propio, biseles y juntas que no coinciden con la rejilla;
 *  - silueta natural (astillado de bordes, escombros sobre la superficie, estalactitas y gotas bajo ella);
 *  - superficie superior iluminada, laterales y parte inferior mas oscuros, interior de las masas que se hunde en sombra;
 *  - musgo/escarcha/brasas segun bioma, grietas con forma organica, manchas de humedad;
 *  - repisas de una via como losas con ménsulas, fondo con columnas, arcos y cadenas, sombras de contacto y luz de antorchas horneada.
 * La COLISION no cambia: todo se calcula a partir del mismo mapa de baldosas y solo modifica pixeles.
 */
final class TerrainArt {
    private TerrainArt() {}
    /** Interruptor para comparar con el arte anterior (solo pruebas). */
    static boolean ENABLED = System.getenv("ART_OLD") == null;
    static boolean PROFILE = System.getenv("RD_PROFILE") != null;
    static long t0;
    static void lap(String n) { if (PROFILE) { long t = System.nanoTime(); System.out.println("    " + n + ": " + (t - t0) / 100000 / 10.0 + " ms"); t0 = t; } }

    // ------------------------------------------------------------------ estilos por bioma
    static final class Style {
        int[] accent;          // 4 tonos oscuro->claro (musgo, escarcha, hierba, sangre...)
        float cover = 0.4f;    // cobertura del acento sobre las superficies superiores (0..1)
        float dripCover = 0.3f;// cobertura en laterales/parte inferior
        int glow;              // color de grietas luminosas (0 = sin brillo)
        float cracks = 0.55f;  // densidad de grietas (0..1)
        int crsMin = 7, crsMax = 11, blkMin = 11, blkMax = 26;   // alto de hilada y ancho de sillar
        boolean icicles;       // carambanos en vez de estalactitas
        boolean roots;         // raices colgantes
        boolean pillars = true, chains = true;
        int lightCol = 0;      // color de la luz de antorcha horneada para focos (0 = por defecto)
        float bgDark = 1f;     // oscuridad del muro de fondo
        int bone;              // color de fragmentos (huesos, cristales...) sobre el suelo, 0 = ninguno
    }

    private static final Style[] STYLES = new Style[9];

    static {
        Style s = new Style();                       // 0 catacumbas: piedra antigua, musgo tenue, huesos
        s.accent = new int[]{0xFF10261c, 0xFF1f4a36, 0xFF3a7d58, 0xFF6cb890};
        s.cover = 0.50f; s.dripCover = 0.34f; s.cracks = 0.60f; s.bone = 0xFFB8B8A0; s.lightCol = 0x5CFF9A;
        STYLES[0] = s;
        s = new Style();                             // 1 forja: hierro oscuro, grietas de brasa
        s.accent = new int[]{0xFF241410, 0xFF3a2218, 0xFF5a3a22, 0xFF8a5a30};
        s.cover = 0.18f; s.dripCover = 0.10f; s.glow = 0xFFFF7A1A; s.cracks = 0.80f; s.crsMin = 8; s.crsMax = 12; s.blkMin = 14; s.blkMax = 30; s.bone = 0xFF6a5a50;
        s.lightCol = 0xFF7A1A; s.bgDark = 0.9f;
        STYLES[1] = s;
        s = new Style();                             // 2 santuario helado: escarcha gruesa y carambanos
        s.accent = new int[]{0xFF5a84b0, 0xFF9cc4e4, 0xFFd6eeff, 0xFFffffff};
        s.cover = 0.85f; s.dripCover = 0.40f; s.cracks = 0.45f; s.icicles = true; s.bone = 0xFFcfe8ff; s.lightCol = 0x7AF0FF;
        STYLES[2] = s;
        s = new Style();                             // 3 vacio: roca morada con venas luminosas
        s.accent = new int[]{0xFF2a1448, 0xFF4a2a7a, 0xFF7a4ac0, 0xFFb98cff};
        s.cover = 0.30f; s.dripCover = 0.20f; s.glow = 0xFFB04CFF; s.cracks = 0.85f; s.bone = 0xFF8a5ad0; s.lightCol = 0xB04CFF; s.bgDark = 0.85f;
        STYLES[3] = s;
        s = new Style();                             // 4 bosque podrido: tierra y piedra con hierba y raices
        s.accent = new int[]{0xFF1c3a14, 0xFF30681e, 0xFF5ca02e, 0xFF9ad84a};
        s.cover = 0.90f; s.dripCover = 0.45f; s.cracks = 0.40f; s.roots = true; s.crsMin = 6; s.crsMax = 10; s.blkMin = 9; s.blkMax = 20;
        s.bone = 0xFF9a8a6a; s.lightCol = 0xFFC24A; s.pillars = false;
        STYLES[4] = s;
        s = new Style();                             // 5 fortaleza del trueno: acero y arcos electricos
        s.accent = new int[]{0xFF1c2a44, 0xFF34507c, 0xFF4f84c8, 0xFF9cd0ff};
        s.cover = 0.22f; s.dripCover = 0.12f; s.glow = 0xFF4FA8FF; s.cracks = 0.45f; s.crsMin = 8; s.crsMax = 13; s.blkMin = 16; s.blkMax = 32;
        s.bone = 0xFF8aa0c0; s.lightCol = 0x4FA8FF;
        STYLES[5] = s;
        s = new Style();                             // 6 catedral carmesi: marmol con goteos de sangre
        s.accent = new int[]{0xFF3a0a14, 0xFF6a1022, 0xFFa01c34, 0xFFd8405a};
        s.cover = 0.20f; s.dripCover = 0.55f; s.cracks = 0.50f; s.crsMin = 9; s.crsMax = 13; s.blkMin = 14; s.blkMax = 28;
        s.bone = 0xFFc8b8b0; s.lightCol = 0xD0203A;
        STYLES[6] = s;
        s = new Style();                             // 7 eclipse: arenisca dorada
        s.accent = new int[]{0xFF5a4414, 0xFF8f7228, 0xFFc8a448, 0xFFf2dc88};
        s.cover = 0.28f; s.dripCover = 0.10f; s.cracks = 0.40f; s.crsMin = 8; s.crsMax = 12; s.blkMin = 13; s.blkMax = 26;
        s.bone = 0xFFd8c898; s.lightCol = 0xFFE0A0;
        STYLES[7] = s;
        s = new Style();                             // 8 luna de sangre
        s.accent = new int[]{0xFF3a0a14, 0xFF70102a, 0xFFa81c3c, 0xFFe04a66};
        s.cover = 0.22f; s.dripCover = 0.60f; s.glow = 0xFFC8142E; s.cracks = 0.65f; s.bone = 0xFFb8a0a0; s.lightCol = 0xC8142E; s.bgDark = 0.85f;
        STYLES[8] = s;
    }

    /** null = ese bioma conserva el dibujo antiguo por baldosas. */
    static Style style(Biome b) {
        if (!ENABLED) return null;
        return (b != null && b.id >= 0 && b.id < STYLES.length) ? STYLES[b.id] : null;
    }

    // ------------------------------------------------------------------ utilidades
    static int hash(int a, int b, int c) {
        int h = a * 374761393 + b * 668265263 + c * 1274126177;
        h = (h ^ (h >>> 13)) * 1274126177;
        return h ^ (h >>> 16);
    }
    static float rnd(int a, int b, int c) { return (hash(a, b, c) & 0xFFFF) / 65535f; }
    static float sstep(float a, float b, float x) { float t = Math.max(0, Math.min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t); }
    static float lerp(float a, float b, float t) { return a + (b - a) * t; }

    /** Ruido de valor suave, escala sx,sy en pixeles. */
    static float vn(float x, float y, float sx, float sy, int seed) {
        float fx = x / sx, fy = y / sy;
        int ix = (int) Math.floor(fx), iy = (int) Math.floor(fy);
        float tx = fx - ix, ty = fy - iy;
        tx = tx * tx * (3 - 2 * tx); ty = ty * ty * (3 - 2 * ty);
        float a = rnd(ix, iy, seed), b = rnd(ix + 1, iy, seed), c = rnd(ix, iy + 1, seed), d = rnd(ix + 1, iy + 1, seed);
        return lerp(lerp(a, b, tx), lerp(c, d, tx), ty);
    }
    static float vn(float x, float y, float s, int seed) { return vn(x, y, s, s, seed); }

    private static final float[] BAYER = {0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5};
    static float bayer(int x, int y) { return (BAYER[((y & 3) << 2) | (x & 3)] + 0.5f) / 16f; }

    static int mix(int a, int b, int t256) {
        int r = (((a >> 16) & 255) * (256 - t256) + ((b >> 16) & 255) * t256) >> 8;
        int g = (((a >> 8) & 255) * (256 - t256) + ((b >> 8) & 255) * t256) >> 8;
        int bl = ((a & 255) * (256 - t256) + (b & 255) * t256) >> 8;
        return 0xFF000000 | (r << 16) | (g << 8) | bl;
    }

    /** Paleta discreta (indice fraccionario -> color) con tramado ordenado solo en la zona de transicion. */
    static int pick(int[] ramp, float idx, int x, int y) {
        int n = ramp.length - 1;
        if (idx <= 0) return ramp[0];
        if (idx >= n) return ramp[n];
        int i = (int) idx;
        float f = idx - i;
        float t = sstep(0.38f, 0.62f, f);
        return t > bayer(x, y) ? ramp[i + 1] : ramp[i];
    }

    /** Distancia (x3) al pixel marcado mas cercano (aprox. euclidea, pesos 3-4). */
    static int[] chamfer(boolean[] src, int W, int H) {
        final int INF = 1 << 20;
        int[] d = new int[W * H];
        for (int i = 0; i < d.length; i++) d[i] = src[i] ? 0 : INF;
        for (int y = 0; y < H; y++)
            for (int x = 0; x < W; x++) {
                int i = y * W + x, v = d[i];
                if (v == 0) continue;
                if (x > 0) v = Math.min(v, d[i - 1] + 3);
                if (y > 0) {
                    v = Math.min(v, d[i - W] + 3);
                    if (x > 0) v = Math.min(v, d[i - W - 1] + 4);
                    if (x < W - 1) v = Math.min(v, d[i - W + 1] + 4);
                }
                d[i] = v;
            }
        for (int y = H - 1; y >= 0; y--)
            for (int x = W - 1; x >= 0; x--) {
                int i = y * W + x, v = d[i];
                if (v == 0) continue;
                if (x < W - 1) v = Math.min(v, d[i + 1] + 3);
                if (y < H - 1) {
                    v = Math.min(v, d[i + W] + 3);
                    if (x < W - 1) v = Math.min(v, d[i + W + 1] + 4);
                    if (x > 0) v = Math.min(v, d[i + W - 1] + 4);
                }
                d[i] = v;
            }
        return d;
    }

    /** Paleta de 6 tonos tomada de los pixeles reales de piedra de la hoja del bioma (para conservar su identidad cromatica). */
    static int[] rampFromSheet(int[] ts) {
        int n = 0;
        int[] cols = new int[256 * 48];
        for (int y = 0; y < 48; y++) for (int x = 0; x < 256; x++) { int c = ts[y * 256 + x]; if ((c >>> 24) == 255) cols[n++] = c; }
        if (n < 20) return new int[]{0xFF10121a, 0xFF1c2230, 0xFF2e384c, 0xFF445270, 0xFF6a7ea0, 0xFFa8bcd8};
        long[] key = new long[n];
        for (int i = 0; i < n; i++) {
            int c = cols[i];
            int lum = (((c >> 16) & 255) * 30 + ((c >> 8) & 255) * 59 + (c & 255) * 11) / 100;
            key[i] = ((long) lum << 32) | (c & 0xFFFFFFFFL);
        }
        java.util.Arrays.sort(key);
        float[] q = {0.02f, 0.22f, 0.45f, 0.68f, 0.88f, 0.995f};
        int[] r = new int[6];
        for (int i = 0; i < 6; i++) r[i] = 0xFF000000 | (int) (key[Math.min(n - 1, (int) (q[i] * n))] & 0xFFFFFF);
        return r;
    }

    /** Ruido de valor precalculado sobre una malla (mucho mas barato que recalcular hashes por pixel). */
    static final class NZ {
        final float[] v; final int nx; final float sx, sy;
        NZ(int W, int H, float sx, float sy, int seed) {
            this.sx = sx; this.sy = sy;
            nx = (int) (W / sx) + 3;
            int ny = (int) (H / sy) + 3;
            v = new float[nx * ny];
            for (int j = 0; j < ny; j++) for (int i = 0; i < nx; i++) v[j * nx + i] = rnd(i, j, seed);
        }
        float at(int x, int y) {
            float fx = x / sx, fy = y / sy;
            int ix = (int) fx, iy = (int) fy;
            float tx = fx - ix, ty = fy - iy;
            tx = tx * tx * (3 - 2 * tx); ty = ty * ty * (3 - 2 * ty);
            int o = iy * nx + ix;
            float a = v[o], b = v[o + 1], c = v[o + nx], d = v[o + nx + 1];
            return a + (b - a) * tx + (c - a + (a - b + d - c) * tx) * ty;
        }
    }

    // ------------------------------------------------------------------ contexto de una sala
    static final class Ctx {
        final Room rm; final Style st; final int W, H, seed;
        final int[] ts, ramp, bgRamp;
        final boolean[] solid;      // pixel de baldosa SOLID
        final int[] dSolid;         // distancia (x3) al terreno para pixeles de aire
        final int[] dAir;           // distancia (x3) al aire para pixeles de terreno
        private final java.util.HashMap<Integer, NZ> nzs = new java.util.HashMap<>();
        NZ nz(float sx, float sy, int sd) {
            int key = (int) (sx * 64) * 31 + (int) (sy * 64) * 131 + sd * 7;
            NZ n = nzs.get(key);
            if (n == null) { n = new NZ(W, H, sx, sy, sd); nzs.put(key, n); }
            return n;
        }
        final boolean[] prot;       // baldosas cuya superficie no se talla (hay prop/pinchos encima)

        Ctx(Room rm, int[] ts, Style st) {
            this.rm = rm; this.st = st; this.ts = ts;
            W = rm.pixW; H = rm.pixH;
            seed = rm.w * 131 + rm.h * 17 + rm.biome.id * 7919;
            ramp = rampFromSheet(ts);
            bgRamp = new int[6];
            for (int i = 0; i < 6; i++) bgRamp[i] = mix(ramp[i], 0xFF05060c, (int) (96 * st.bgDark));
            solid = new boolean[W * H];
            prot = new boolean[rm.w * rm.h];
            boolean[] air = new boolean[W * H];
            for (int ty = 0; ty < rm.h; ty++)
                for (int tx = 0; tx < rm.w; tx++) {
                    boolean s = rm.t[ty * rm.w + tx] == Room.SOLID;
                    for (int j = 0; j < 16; j++) {
                        int o = (ty * 16 + j) * W + tx * 16;
                        for (int i = 0; i < 16; i++) { solid[o + i] = s; air[o + i] = !s; }
                    }
                    if (s && ty > 0) {
                        int above = rm.t[(ty - 1) * rm.w + tx];
                        if (above == Room.SPIKE || rm.deco[(ty - 1) * rm.w + tx] != 0) prot[ty * rm.w + tx] = true;
                    }
                }
            dSolid = chamfer(solid, W, H);
            dAir = chamfer(air, W, H);
        }
    }

    // ------------------------------------------------------------------ hiladas y sillares
    static final class Courses {
        int[] top, hgt, rowC; int[][] bx;
    }

    static Courses courses(int W, int H, int seed, int cMin, int cMax, int bMin, int bMax) {
        Courses c = new Courses();
        int maxN = H / cMin + 3;
        c.top = new int[maxN]; c.hgt = new int[maxN]; c.bx = new int[maxN][];
        c.rowC = new int[H];
        int y = -(hash(seed, 1, 2) & 0xFF) % cMin, n = 0;
        while (y < H) {
            int h = cMin + (hash(seed, n, 3) & 0xFFFF) % (cMax - cMin + 1);
            c.top[n] = y; c.hgt[n] = h;
            int cnt = 0; int[] tmp = new int[W / bMin + 6];
            int x = -((hash(seed, n, 4) & 0xFFFF) % bMax) - 1;
            tmp[cnt++] = x;
            while (x < W + bMax) {
                int bw = bMin + (hash(seed, n * 977 + cnt, 5) & 0xFFFF) % (bMax - bMin + 1);
                if ((hash(seed, n * 31 + cnt, 6) & 15) == 0) bw = bw * 3 / 2;      // sillar largo ocasional
                else if ((hash(seed, n * 31 + cnt, 7) & 15) == 0) bw = Math.max(bMin - 2, bw / 2); // sillar corto
                x += bw;
                if (cnt >= tmp.length) tmp = java.util.Arrays.copyOf(tmp, tmp.length * 2);
                tmp[cnt++] = x;
            }
            c.bx[n] = java.util.Arrays.copyOf(tmp, cnt);
            for (int yy = Math.max(0, y); yy < Math.min(H, y + h); yy++) c.rowC[yy] = n;
            y += h; n++;
        }
        return c;
    }

    // ------------------------------------------------------------------ muro de fondo, arquitectura y sombras
    static void background(Ctx cx, int[] out) {
        lap("ctx");
        Room rm = cx.rm; Style st = cx.st; int W = cx.W, H = cx.H, seed = cx.seed;
        Courses co = courses(W, H, seed + 500, 10, 16, 20, 40);
        NZ ng = cx.nz(3, 3, seed + 509), nm = cx.nz(9, 20, seed + 513);
        for (int y = 0; y < H; y++) {
            int c = co.rowC[y], top = co.top[c], ch = co.hgt[c], v = y - top;
            int[] xs = co.bx[c]; int k = 0, kk = -1;
            float tone = 0; int bw = 0;
            int rowTile = (y >> 4) * rm.w;
            float yg = 0.25f * ((float) y / H - 0.5f);
            for (int x = 0; x < W; x++) {
                while (xs[k + 1] <= x) k++;
                int i = y * W + x;
                if (rm.vista[rowTile + (x >> 4)]) continue;
                if (cx.solid[i] && cx.dAir[i] >= 15) continue;          // bajo el terreno macizo no se ve
                if (k != kk) { kk = k; tone = rnd(c, k, seed + 505); bw = xs[k + 1] - xs[k]; }
                int u = x - xs[k];
                float idx = 0.75f + (tone - 0.5f) * 0.55f;
                if (v == ch - 1 || u == bw - 1) idx = 0.05f;
                else {
                    if (v == 0) idx += 0.45f; else if (v == 1) idx += 0.15f;
                    if (u == 0) idx += 0.25f;
                    if (v == ch - 2) idx -= 0.2f;
                }
                idx += (ng.at(x, y) - 0.5f) * 0.45f + yg;
                float m = nm.at(x, y);
                if (m > 0.62f) idx -= 0.45f * sstep(0.62f, 0.78f, m);   // manchas de humedad (suaves, sin sal y pimienta)
                int dS3 = cx.dSolid[i];
                if (dS3 < 33) idx -= 0.85f * (1f - sstep(0f, 11f, dS3 / 3f));   // sombra de contacto junto al terreno
                int col = pick(cx.bgRamp, idx, x, y);
                if (m > 0.80f && st.cover > 0.3f && !st.icicles && sstep(0.80f, 0.94f, m) > bayer(x, y) * 1.1f) col = mix(col, st.accent[1], 55);
                out[i] = col;
            }
        }
        lap("fondo");
        if (st.pillars) pillars(cx, out, co);
        if (st.chains) chains(cx, out);
        lap("arquitectura");
    }

    /** Longitud (en baldosas) del hueco de fondo continuo que empieza en (tx, ty), sin muro de decoracion ni vista. */
    private static int openRun(Room rm, int tx, int ty) {
        int n = 0;
        for (int y = ty; y < rm.h; y++) {
            int i = y * rm.w + tx;
            if (rm.t[i] != Room.AIR || rm.vista[i] || rm.deco[i] != 0) break;
            n++;
        }
        return n;
    }

    private static void pillars(Ctx cx, int[] out, Courses co) {
        Room rm = cx.rm; int W = cx.W, seed = cx.seed;
        int tx = 3 + (hash(seed, 9, 9) & 3);
        int prevX = -1, prevTop = 0;
        while (tx < rm.w - 4) {
            // buscar la columna de baldosas (2 anchas) con mayor hueco vertical continuo
            int bestTop = -1, bestLen = 0;
            for (int y = 0; y < rm.h; y++) {
                if (rm.t[y * rm.w + tx] == Room.AIR && rm.t[y * rm.w + tx + 1] == Room.AIR) {
                    int a = openRun(rm, tx, y), b = openRun(rm, tx + 1, y), len = Math.min(a, b);
                    if (len > bestLen) { bestLen = len; bestTop = y; }
                    y += Math.max(0, len - 1);
                }
            }
            if (bestLen >= 6) {
                int px = tx * 16 + 6, top = bestTop * 16, bot = (bestTop + bestLen) * 16;
                pillar(cx, out, px, top, bot, 20);
                if (prevX >= 0 && prevTop == bestTop && px - prevX <= 16 * 15 && px - prevX >= 16 * 6) arch(cx, out, prevX + 20, px, top);
                prevX = px; prevTop = bestTop;
            }
            tx += 9 + (hash(seed, tx, 11) & 0xFFFF) % 6;
        }
    }

    private static void pillar(Ctx cx, int[] out, int x0, int top, int bot, int w) {
        int W = cx.W, H = cx.H, seed = cx.seed;
        int capH = 8, baseH = 8;
        for (int y = Math.max(0, top); y < Math.min(H, bot); y++) {
            for (int x = x0 - 2; x < x0 + w + 2 && x < W; x++) {
                if (x < 0) continue;
                int u = x - x0;
                boolean cap = y < top + capH, base = y >= bot - baseH;
                boolean wide = cap || base;
                if (!wide && (u < 0 || u >= w)) continue;
                float idx;
                if (wide) {
                    float t = (u + 2f) / (w + 4f);
                    idx = 1.4f + 1.1f * (float) Math.sin(Math.PI * t);
                    int row = cap ? y - top : (bot - 1 - y);
                    if (row == capH - 1) idx = 0.3f;                           // junta oscura bajo capitel / sobre basa
                    else if (row == 0) idx += 0.6f;
                    else if (row == 3 && cap) idx -= 0.5f;
                } else {
                    float t = (u + 0.5f) / w;
                    idx = 0.9f + 1.5f * (float) Math.sin(Math.PI * t);         // perfil cilindrico, luz a la izquierda
                    idx -= 0.25f * (t - 0.5f);
                    if (u == 5 || u == 10 || u == 15) idx -= 0.55f;            // estrias
                    if (((y - top) / 21) % 1 == 0 && (y - top) % 21 == 20) idx -= 0.6f; // juntas de tambor
                }
                idx += (vn(x, y, 3, seed + 41) - 0.5f) * 0.5f;
                float dS = cx.dSolid[y * W + x] / 3f;
                idx -= 0.5f * (1f - sstep(0f, 6f, dS));
                out[y * W + x] = pick(cx.ramp, idx - 0.35f, x, y);
            }
        }
    }

    /** Arco rebajado entre dos columnas, con dovelas y clave. */
    private static void arch(Ctx cx, int[] out, int xa, int xb, int top) {
        int W = cx.W, H = cx.H, seed = cx.seed;
        float half = (xb - xa) / 2f, xm = (xa + xb) / 2f;
        float hh = Math.min(half * 0.55f, 42f);
        float yBase = top + hh + 9;
        int thick = 7;
        for (int x = xa; x < xb; x++) {
            float t = (x - xm) / half;
            if (Math.abs(t) >= 1f) continue;
            float yi = yBase - hh * (float) Math.sqrt(1 - t * t);
            for (int y = (int) (yi - thick); y <= (int) yi; y++) {
                if (y < 0 || y >= H || x < 0 || x >= W) continue;
                int i = y * W + x;
                if (cx.solid[i]) continue;
                float d = yi - y;                                              // 0 = borde inferior (intrados)
                float idx = 1.2f + (d < 1.5f ? 0.9f : 0f) - (d > thick - 1.5f ? 0.6f : 0f);
                int seg = (int) ((x - xa) / 11);                               // dovelas
                if ((x - xa) % 11 == 0) idx -= 0.8f;
                idx += (rnd(seg, 3, seed + 77) - 0.5f) * 0.5f;
                if (Math.abs(t) < 0.06f) idx += 0.5f;                          // clave
                idx -= 0.4f * (1f - sstep(0f, 6f, cx.dSolid[i] / 3f));
                out[i] = pick(cx.ramp, idx - 0.3f, x, y);
            }
        }
    }

    private static void chains(Ctx cx, int[] out) {
        Room rm = cx.rm; int W = cx.W, seed = cx.seed;
        for (int tx = 2; tx < rm.w - 2; tx++) {
            if (rnd(tx, 5, seed + 91) > 0.10f) continue;
            // techo = primera baldosa aire bajo una baldosa solida
            int y0 = -1;
            for (int y = 1; y < rm.h - 1; y++) if (rm.t[(y - 1) * rm.w + tx] == Room.SOLID && rm.t[y * rm.w + tx] == Room.AIR) { y0 = y; break; }
            if (y0 < 0) continue;
            int len = 20 + (hash(tx, 7, seed) & 0xFFFF) % 46;
            int x = tx * 16 + 5 + (hash(tx, 8, seed) & 7);
            for (int j = 0; j < len; j++) {
                int y = y0 * 16 + j;
                if (y >= cx.H) break;
                int ti = (y >> 4) * rm.w + (x >> 4);
                if (rm.t[ti] != Room.AIR || rm.vista[ti] || rm.deco[ti] != 0) break;
                boolean link = (j / 3) % 2 == 0;
                int c = link ? cx.ramp[3] : cx.ramp[1];
                out[y * W + x] = c;
                if (link) { out[y * W + x + 1] = cx.ramp[2]; }
                else out[y * W + x - 1] = cx.ramp[1];
            }
        }
    }

    // ------------------------------------------------------------------ terreno
    static void terrain(Ctx cx, int[] out) {
        Room rm = cx.rm; Style st = cx.st; int W = cx.W, H = cx.H, seed = cx.seed;
        boolean[] solid = cx.solid;
        int[] dA = cx.dAir;

        // 1) silueta: astillado del borde y muescas ocasionales (no en baldosas con props/pinchos encima)
        NZ n1 = cx.nz(3, 3, seed + 1), n2s = cx.nz(11, 11, seed + 2);
        boolean[] f = solid.clone();
        for (int y = 0; y < H; y++)
            for (int x = 0; x < W; x++) {
                int i = y * W + x;
                if (!solid[i]) continue;
                float d = dA[i] / 3f;
                if (d >= 3.4f) continue;
                if (cx.prot[(y >> 4) * rm.w + (x >> 4)]) continue;
                float n = n1.at(x, y), n2 = n2s.at(x, y);
                float carve = 0.42f + 0.95f * n + 2.7f * n2 * n2 * n2;
                if (d < carve) f[i] = false;
            }
        boolean[] air2 = new boolean[W * H];
        for (int i = 0; i < air2.length; i++) air2[i] = !f[i];
        int[] dA2 = chamfer(air2, W, H);
        lap("silueta");
        // profundidad bajo la superficie (pixeles solidos contados desde el aire que tienen encima)
        byte[] depth = new byte[W * H];
        for (int x = 0; x < W; x++) {
            int run = 100;
            for (int y = 0; y < H; y++) {
                int i = y * W + x;
                if (!f[i]) { run = -1; depth[i] = 100; continue; }
                run = run >= 100 ? 100 : run + 1;
                depth[i] = (byte) run;
            }
        }
        // sillares de la cornisa superior (una sola hilera a lo largo de x)
        int[] capX = new int[W / 8 + 8]; int cn = 0;
        { int x = -(hash(seed, 77, 1) & 15); capX[cn++] = x;
          while (x < W + 24) { x += 9 + (hash(seed, cn, 78) & 0xFFFF) % 15; if (cn < capX.length) capX[cn++] = x; else break; } }

        // 2) sillares del cuerpo
        Courses co = courses(W, H, seed + 100, st.crsMin, st.crsMax, st.blkMin, st.blkMax);
        int[] ramp = cx.ramp;
        NZ ng = cx.nz(2, 2, seed + 109), nCr = cx.nz(7, 7, seed + 31), nCrG = cx.nz(26, 26, seed + 32);
        NZ nMt = cx.nz(8, 5, seed + 11), nMk = cx.nz(6, 6, seed + 12), nDr = cx.nz(5, 18, seed + 13), nDk = cx.nz(4, 9, seed + 14);
        NZ nDrip = cx.nz(3, 14, seed + 15), nPatch = cx.nz(10, 10, seed + 21);
        for (int y = 0; y < H; y++) {
            int c = co.rowC[y], top = co.top[c], ch = co.hgt[c], v = y - top;
            int[] xs = co.bx[c]; int k = 0;
            int ck = 0, kk = -1;
            float tone = 0; int bw = 0;
            for (int x = 0; x < W; x++) {
                while (xs[k + 1] <= x) k++;
                int i = y * W + x;
                if (!f[i]) continue;
                float dd = dA2[i] / 3f;
                if (k != kk) { kk = k; tone = rnd(c, k, seed + 105); bw = xs[k + 1] - xs[k]; }
                int u = x - xs[k];
                float deep = sstep(12f, 60f, dd);
                float idx;
                float g = ng.at(x, y);
                int dp = depth[i];
                if (dp <= 5) {                                           // cornisa: losas planas con cara superior clara y junta oscura debajo
                    while (capX[ck + 1] <= x && ck + 2 < cn) ck++;
                    int cu = x - capX[ck], cw = capX[ck + 1] - capX[ck];
                    float ct = rnd(ck, 5, seed + 120);
                    float[] base = {3.85f, 3.1f, 2.75f, 2.5f, 2.2f, 0.55f};
                    idx = base[dp] + (ct - 0.5f) * 0.7f * (dp == 0 ? 0.4f : 1f);
                    if (dp == 5) idx = 0.5f;
                    else if (cu == 0 && dp >= 1) idx = 0.6f;               // junta vertical entre losas
                    else if (cu == 1 && dp >= 1 && dp <= 4) idx += 0.4f;
                    else if (cu == 0 && dp == 0) idx -= 1.2f;               // esquina astillada
                    idx += (g - 0.5f) * 0.6f;
                } else {
                    boolean mortar = v == ch - 1 || u == bw - 1;
                    if (mortar) idx = 0.4f + (g - 0.5f) * 0.5f;
                    else {
                        float bev = 0;
                        if (v == 0) bev += 1.0f; else if (v == 1) bev += 0.3f;
                        if (u == 0) bev += 0.6f;
                        if (v == ch - 2) bev -= 0.55f;
                        if (u == bw - 2) bev -= 0.35f;
                        idx = 2.05f + (tone - 0.5f) * 1.15f + bev * (1f - 0.55f * deep) + (g - 0.5f) * 0.65f;
                        if ((hash(x, y, seed) & 15) == 0) idx += (hash(y, x, seed) & 1) == 0 ? 0.5f : -0.5f;   // grano suelto
                    }
                    if (dp == 6) idx -= 0.9f; else if (dp == 7) idx -= 0.45f;    // sombra que proyecta la cornisa
                }
                idx -= 1.05f * deep;

                // luz desde arriba-izquierda sobre las caras expuestas, contorno oscuro en laterales/bajos
                if (dd < 5f) {
                    int gx = dA2[i + (x < W - 1 ? 1 : 0)] - dA2[i - (x > 0 ? 1 : 0)];
                    int gy = dA2[i + (y < H - 1 ? W : 0)] - dA2[i - (y > 0 ? W : 0)];
                    float len = (float) Math.sqrt(gx * gx + gy * gy);
                    if (len > 0.8f) {
                        float nx = -gx / len, ny = -gy / len;                  // normal hacia el aire
                        float lit = -(nx * 0.45f + ny * 0.9f);
                        float fall = Math.max(0f, 1f - (dd - 0.6f) / 3.4f);
                        idx += (lit > 0 ? 1.8f * lit : 1.2f * lit) * fall;
                        boolean topFace = ny < -0.45f, bottomFace = ny > 0.55f, sideFace = Math.abs(nx) > 0.55f;
                        if (!topFace && dd < 1.25f) idx -= 0.9f;               // contorno
                        if (topFace) {
                            float m = nMt.at(x, y);
                            float thick = 1.1f + 1.5f * nMk.at(x, y);
                            if (m > 1f - st.cover && dd < thick) {
                                int ai = dd < 1.3f ? 3 : (dd < 2.3f ? 2 : 1);
                                if (st.accent[ai] != 0) { out[i] = (hash(x, y, seed + 3) & 7) == 0 ? st.accent[Math.max(0, ai - 1)] : st.accent[ai]; continue; }
                            }
                        } else if (sideFace || bottomFace) {
                            float m = nDr.at(x, y);
                            if (m > 1f - st.dripCover * 0.55f && dd < 1.9f + 1.6f * nDk.at(x, y)) {
                                out[i] = st.accent[(hash(x, y, seed + 4) & 3) == 0 ? 2 : 1]; continue;
                            }
                        }
                        if (bottomFace && nDrip.at(x, y) > 0.68f) idx -= 1.0f;     // churretones de humedad
                    }
                }
                // manchas de acento dentro de la mamposteria
                if (dd < 8f && dp > 5) {
                    float m2 = nPatch.at(x, y);
                    if (m2 > 0.80f - st.cover * 0.12f && (hash(x, y, seed + 5) & 3) != 0) { out[i] = st.accent[1]; continue; }
                }
                // grietas con forma organica
                float cr = Math.abs(nCr.at(x, y) - 0.5f);
                if (cr < 0.034f) {
                    float gate = nCrG.at(x, y);
                    if (gate > (st.glow != 0 ? 0.80f - st.cracks * 0.06f : 0.66f - st.cracks * 0.12f)) {
                        if (cr < (st.glow != 0 ? 0.011f : 0.017f)) {
                            if (st.glow != 0) { out[i] = (hash(x, y, seed + 6) & 3) == 0 ? mix(st.glow, 0xFFFFFFFF, 90) : st.glow; continue; }
                            idx = 0.1f;
                        } else if (st.glow != 0) idx -= 0.45f;
                    }
                }
                out[i] = pick(ramp, idx, x, y);
            }
        }

        lap("sillares");
        // 3) escombros, huesos y gotas sobre/bajo las superficies
        for (int ty = 0; ty < rm.h; ty++)
            for (int tx = 0; tx < rm.w; tx++) {
                if (rm.t[ty * rm.w + tx] != Room.SOLID) continue;
                int ti = ty * rm.w + tx;
                if (ty > 0 && rm.t[ti - rm.w] == Room.AIR && rm.deco[ti - rm.w] == 0 && !cx.prot[ti]) {
                    float r = rnd(tx, ty, seed + 201);
                    if (r < 0.30f) rubble(cx, out, f, tx * 16 + 2 + (hash(tx, ty, seed + 202) & 7), ty * 16, r < 0.06f);
                    else if (r < 0.38f && st.bone != 0) pebbles(cx, out, f, tx * 16 + 3 + (hash(tx, ty, seed + 203) & 9), ty * 16);
                }
                if (ty < rm.h - 1 && rm.t[ti + rm.w] == Room.AIR && rm.deco[ti + rm.w] == 0) {
                    float r = rnd(tx, ty, seed + 211);
                    if (r < 0.30f) stalactite(cx, out, tx * 16 + 2 + (hash(tx, ty, seed + 212) & 11), (ty + 1) * 16);
                    else if (r < 0.46f) strand(cx, out, tx * 16 + 2 + (hash(tx, ty, seed + 213) & 11), (ty + 1) * 16);
                }
            }

        lap("escombros");
        // 4) repisas de una via
        for (int ty = 0; ty < rm.h; ty++) {
            int tx = 0;
            while (tx < rm.w) {
                if (rm.t[ty * rm.w + tx] != Room.ONEWAY) { tx++; continue; }
                int e = tx;
                while (e + 1 < rm.w && rm.t[ty * rm.w + e + 1] == Room.ONEWAY) e++;
                slab(cx, out, tx * 16, (e + 1) * 16, ty * 16);
                tx = e + 1;
            }
        }
    }

    private static void rubble(Ctx cx, int[] out, boolean[] f, int x0, int surfY, boolean big) {
        int seed = cx.seed;
        int w = big ? 8 + (hash(x0, surfY, seed) & 3) : 4 + (hash(x0, surfY, seed + 1) & 3);
        int h = big ? 4 : 2 + (hash(x0, surfY, seed + 2) & 1);
        for (int j = 0; j < h; j++) {
            int rowW = j == 0 ? w - 2 : (j == h - 1 && h > 2 ? w : w);          // piedra redondeada: la fila superior es mas corta
            if (j == 0 && h > 2) rowW = w - 2;
            if (rowW < 2) rowW = 2;
            int xs = x0 + (w - rowW) / 2 + (j == 0 ? (hash(x0, surfY, seed + 4) & 1) : 0);
            for (int i = 0; i < rowW; i++) {
                int x = xs + i, y = surfY - h + j;
                if (x < 0 || x >= cx.W || y < 0) continue;
                float idx = j == 0 ? 3.7f : (j == h - 1 ? 1.5f : 2.6f);
                if (i == 0) idx += 0.4f;
                if (i == rowW - 1) idx -= 0.6f;
                out[y * cx.W + x] = pick(cx.ramp, idx, x, y);
            }
        }
        if (cx.st.cover > 0.5f && (hash(x0, surfY, seed + 9) & 3) == 0) {     // un mechon de hierba/musgo junto al escombro
            int x = x0 + w, y = surfY - 1;
            if (x < cx.W && y >= 0) { out[y * cx.W + x] = cx.st.accent[2]; if (y > 0) out[(y - 1) * cx.W + x] = cx.st.accent[3]; }
        }
    }

    private static void pebbles(Ctx cx, int[] out, boolean[] f, int x0, int surfY) {
        int y = surfY - 1;
        if (y < 0) return;
        out[y * cx.W + x0] = cx.st.bone;
        if ((hash(x0, surfY, cx.seed + 7) & 1) == 0 && x0 + 1 < cx.W) out[y * cx.W + x0 + 1] = mix(cx.st.bone, 0xFF000000, 90);
        if ((hash(x0, surfY, cx.seed + 8) & 3) == 0 && y > 0) out[(y - 1) * cx.W + x0] = mix(cx.st.bone, 0xFFFFFFFF, 60);
    }

    private static void stalactite(Ctx cx, int[] out, int x0, int y0) {
        int len = 3 + (hash(x0, y0, cx.seed + 301) & 3);
        for (int j = 0; j < len; j++) {
            int half = cx.st.icicles ? (j < len / 2 ? 1 : 0) : (j < len - 2 ? 1 : 0);
            for (int i = -half; i <= half; i++) {
                int x = x0 + i, y = y0 + j;
                if (x < 0 || x >= cx.W || y >= cx.H) continue;
                float idx = cx.st.icicles ? (i < 0 ? 4.4f : 3.4f) : (i < 0 ? 2.5f : 1.6f);
                if (j == len - 1) idx += 0.6f;
                if (cx.st.icicles) { out[y * cx.W + x] = cx.st.accent[i < 0 ? 3 : 2]; if (j == len - 1) out[y * cx.W + x] = cx.st.accent[3]; }
                else out[y * cx.W + x] = pick(cx.ramp, idx, x, y);
            }
        }
    }

    /** Hebra de musgo/raiz/sangre que cuelga bajo la superficie. */
    private static void strand(Ctx cx, int[] out, int x0, int y0) {
        int len = 4 + (hash(x0, y0, cx.seed + 311) & 7);
        if (cx.st.cover < 0.15f && !cx.st.roots) return;
        for (int j = 0; j < len; j++) {
            int x = x0 + (cx.st.roots && j > len / 2 ? ((j & 2) >> 1) : 0), y = y0 + j;
            if (x < 0 || x >= cx.W || y >= cx.H) continue;
            out[y * cx.W + x] = cx.st.roots ? mix(0xFF3a2a1a, cx.st.accent[1], j * 256 / len) : cx.st.accent[j < 2 ? 2 : 1];
        }
    }

    /** Repisa de una via: losa de piedra con menseulas, extremos astillados y sombra de contacto. */
    private static void slab(Ctx cx, int[] out, int x0, int x1, int y0) {
        int W = cx.W, H = cx.H, seed = cx.seed;
        int h = 6;
        Courses co = null;
        // juntas verticales variables
        int[] joints = new int[(x1 - x0) / 8 + 3]; int jn = 0;
        int jx = x0 + 6 + (hash(x0, y0, seed + 401) & 7);
        while (jx < x1 - 4) { joints[jn++] = jx; jx += 9 + (hash(jx, y0, seed + 402) & 7); }
        // sombra de contacto bajo la losa
        for (int j = h; j < h + 4; j++)
            for (int x = x0 + 1; x < x1 - 1; x++) {
                int y = y0 + j;
                if (y >= H || cx.solid[y * W + x]) continue;
                int o = out[y * W + x];
                if ((o >>> 24) == 0) continue;
                out[y * W + x] = mix(o, 0xFF04050a, j == h ? 150 : (j == h + 1 ? 95 : (j == h + 2 ? 55 : 28)));
            }
        for (int j = 0; j < h; j++)
            for (int x = x0; x < x1; x++) {
                int y = y0 + j;
                if (y >= H) continue;
                int e = Math.min(x - x0, x1 - 1 - x);
                // esquinas y extremos astillados
                if (e == 0 && (j == 0 || j == h - 1 || (hash(x, y0, seed + 403) & 1) == 0)) continue;
                if (e == 1 && j == h - 1 && (hash(x, y0, seed + 404) & 1) == 0) continue;
                float idx;
                if (j == 0) idx = 4.1f;                       // cara superior iluminada
                else if (j == 1) idx = 3.0f;
                else if (j == h - 1) idx = 1.0f;              // canto inferior en sombra
                else idx = 2.2f - 0.25f * (j - 2);
                boolean isJoint = false;
                for (int q = 0; q < jn; q++) if (joints[q] == x) { isJoint = true; break; }
                if (isJoint && j > 0) idx = 0.7f;
                idx += (vn(x, y, 3, seed + 405) - 0.5f) * 0.9f;
                if (j == 0 && cx.st.cover > 0.2f && vn(x, y, 9, 4, seed + 406) > 1f - cx.st.cover * 0.8f) { out[y * W + x] = cx.st.accent[(hash(x, y, seed) & 3) == 0 ? 2 : 3 - ((hash(y, x, seed) & 1))]; continue; }
                if (j >= 1 && j <= 2 && cx.st.cover > 0.2f && vn(x, y, 7, 5, seed + 407) > 1f - cx.st.cover * 0.35f && (hash(x, y, seed + 408) & 1) == 0) { out[y * W + x] = cx.st.accent[1]; continue; }
                out[y * W + x] = pick(cx.ramp, idx, x, y);
            }
        // menseulas en los extremos (y cada ~4 baldosas en las largas)
        int nb = 2 + Math.max(0, (x1 - x0) / 64 - 1);
        for (int b = 0; b < nb; b++) {
            int bx = b == 0 ? x0 + 3 : (b == 1 ? x1 - 8 : x0 + (x1 - x0) * (b - 1) / (nb - 1) - 2);
            corbel(cx, out, bx, y0 + h);
        }
        // cadenas cortas colgando de las repisas largas
        if (x1 - x0 >= 48 && cx.st.chains) {
            int cxp = x0 + 16 + (hash(x0, y0, seed + 409) % Math.max(1, x1 - x0 - 32));
            int len = 8 + (hash(x1, y0, seed + 410) & 7);
            for (int j = 0; j < len; j++) {
                int y = y0 + h + 3 + j;
                if (y >= H || cx.solid[y * W + cxp]) break;
                boolean link = (j / 2) % 2 == 0;
                out[y * W + cxp] = link ? cx.ramp[3] : cx.ramp[1];
                if (link && cxp + 1 < W) out[y * W + cxp + 1] = cx.ramp[2];
            }
        }
    }

    private static void corbel(Ctx cx, int[] out, int x0, int y0) {
        for (int j = 0; j < 5; j++) {
            int w = 5 - j;
            for (int i = 0; i < w; i++) {
                int x = x0 + i + (j >> 1), y = y0 + j;
                if (x < 0 || x >= cx.W || y >= cx.H || cx.solid[y * cx.W + x]) continue;
                float idx = i == 0 ? 2.8f : (j == 4 ? 1.1f : 1.9f);
                out[y * cx.W + x] = pick(cx.ramp, idx, x, y);
            }
        }
    }

    // ------------------------------------------------------------------ luz de antorchas horneada (bandas, sin desenfoque)
    static void lights(Ctx cx, int[] out) {
        Room rm = cx.rm; int W = cx.W, H = cx.H;
        List<int[]> an = rm.animated();
        for (int[] d : an) {
            int lc = d[2] == 5 ? 0xFFB060 : (cx.st.lightCol != 0 ? cx.st.lightCol : 0xFFB060);
            if (rm.biome.color == 0xF2E6B8) lc = 0xFFE0A0;
            float cxp = d[0] + 8, cyp = d[1] + 8;
            float R = d[2] == 5 ? 62f : 48f;
            int x0 = Math.max(0, (int) (cxp - R)), x1 = Math.min(W - 1, (int) (cxp + R));
            int y0 = Math.max(0, (int) (cyp - R)), y1 = Math.min(H - 1, (int) (cyp + R));
            int lr = (lc >> 16) & 255, lg = (lc >> 8) & 255, lb = lc & 255;
            for (int y = y0; y <= y1; y++)
                for (int x = x0; x <= x1; x++) {
                    int i = y * W + x;
                    int o = out[i];
                    if ((o >>> 24) == 0) continue;
                    float dx = x - cxp, dy = (y - cyp) * 1.1f;
                    float dist = (float) Math.sqrt(dx * dx + dy * dy);
                    if (dist >= R) continue;
                    float k = 1f - dist / R; k *= k;
                    float band = k * 5f; int bi = (int) band;
                    if (band - bi > bayer(x, y)) bi++;                      // 5 escalones con tramado
                    if (bi <= 0) continue;
                    float a = bi * 0.045f;
                    int r = Math.min(255, ((o >> 16) & 255) + (int) (lr * a * 0.55f + ((o >> 16) & 255) * a * 0.6f));
                    int g = Math.min(255, ((o >> 8) & 255) + (int) (lg * a * 0.55f + ((o >> 8) & 255) * a * 0.6f));
                    int b = Math.min(255, (o & 255) + (int) (lb * a * 0.55f + (o & 255) * a * 0.6f));
                    out[i] = 0xFF000000 | (r << 16) | (g << 8) | b;
                }
        }
    }
}
