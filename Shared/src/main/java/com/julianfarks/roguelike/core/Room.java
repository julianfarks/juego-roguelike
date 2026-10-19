package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/** Mapa de baldosas de una sala + datos de aparicion + imagen precalculada. */
public final class Room {
    public static final int TS = 16;
    public static final int AIR = 0, SOLID = 1, ONEWAY = 2, SPIKE = 3, SPIKE_DOWN = 4, BREAK = 5, DOOR = 6;
    /** Pared oculta (solida: se descubre al golpearla) y pared ilusoria (se atraviesa). Las dos se dibujan como roca hasta que la camara se descubre. */
    public static final int HWALL = 7, FAKE = 8;
    public static boolean isSolid(int t) { return t == SOLID || t == BREAK || t == DOOR || t == HWALL; }
    // tipos de sala
    public static final int START = 0, COMBAT = 1, ELITE = 2, BLESSING = 3, FORGE = 4, SHOP = 5, FOUNTAIN = 6, TREASURE = 7, BOSS = 8, REST = 9, HUB = 10, EVENT = 11;

    public static final class Spawn {
        public final String enemy; public final float x, y; public final boolean elite;
        public boolean optional;       // encuentro opcional (camaras profundas, torres, alcobas): no cuenta para despejar la sala
        public int zone;               // Vertical.Z_*: en que altura / ruta esta
        public Spawn(String e, float x, float y, boolean elite) { this.enemy = e; this.x = x; this.y = y; this.elite = elite; }
    }

    public static final class PropSpec {
        public final String kind; public final float x, y; public final int arg;
        PropSpec(String k, float x, float y, int arg) { this.kind = k; this.x = x; this.y = y; this.arg = arg; }
    }

    public final int w, h, type;
    public final Biome biome;
    public final byte[] t;
    public final short[] deco;         // (tipo<<8)|indice ; 1 pared, 2 estandarte, 3 colgante, 4 prop de suelo, 5 antorcha, 6 foco
    public final boolean[] vista;      // sin pared de fondo: se ve el parallax
    public float spawnX, spawnY, exitX, exitY;
    public final List<Spawn> spawns = new ArrayList<>();
    public final List<PropSpec> props = new ArrayList<>();
    public final List<float[]> doorXs = new ArrayList<>(); // {x} de puertas de salida (centro)
    public Platform.Img baked, bakedOpen, breakImg, doorImg;
    public final List<Secret> secrets = new ArrayList<>();   // camaras secretas (la imagen 'baked' las muestra cerradas; 'bakedOpen' abiertas)
    public int pixW, pixH;
    public List<int[]> secretSpots;
    public int vaultA = -99;
    public int event;                  // suceso especial (Events.*) cuando type == EVENT
    public int glow;                   // color ambiental RGB del suceso (0 = ninguno)
    public int[] ground;               // fila de superficie por columna (-1 = foso)
    public final List<int[]> arenas = new ArrayList<>();   // {x0,x1} tramos de arena de combate (el generador concentra ahi a los enemigos)
    public List<Integer> spikeCols;    // columnas con tira de pinchos sobre suelo firme
    // ---- mazmorras verticales (Vertical.java): arquetipo y filas de cada altura (0 = no hay)
    public boolean tall;               // sala con varias alturas: la validacion usa el modelo estricto de saltos y caidas
    public int arch;                   // Vertical.A_COMPACT / A_TALL / A_DEEP
    public int fy, mf, mf2, mf3, s1, s2;   // fila del suelo principal, de los pisos superiores 1-3 y de los subsuelos 1-2 (0 = sin ese nivel)
    public int xdA, xuB, xc, xd2;      // pozos: bajada y subida del subsuelo 1, bajada y subida del subsuelo 2 (0 = no hay)
    public final List<int[]> optionalSpots = new ArrayList<>();   // {x,y} de recompensas/cofres opcionales de la ruta (para pruebas y guias)

    public Room(int w, int h, int type, Biome b) {
        this.w = w; this.h = h; this.type = type; this.biome = b;
        t = new byte[w * h];
        deco = new short[w * h];
        vista = new boolean[w * h];
        pixW = w * TS; pixH = h * TS;
    }

    public int tile(int x, int y) {
        if (x < 0 || x >= w || y < 0) return SOLID;
        if (y >= h) return SOLID;
        return t[y * w + x];
    }

    public void set(int x, int y, int v) { if (x >= 0 && y >= 0 && x < w && y < h) t[y * w + x] = (byte) v; }

    public boolean solid(int x, int y) { return isSolid(tile(x, y)); }

    public boolean hazardAt(float px, float py) {
        int tx = (int) Math.floor(px / TS), ty = (int) Math.floor(py / TS);
        int v = tile(tx, ty);
        return v == SPIKE || v == SPIKE_DOWN;
    }

    // ---------- imagen precalculada ----------
    private static int blend(int dst, int src) {
        int sa = src >>> 24;
        if (sa == 255) return src;
        if (sa == 0) return dst;
        int da = dst >>> 24;
        if (da == 0) return src;
        int ia = 255 - sa;
        int r = (((src >> 16) & 255) * sa + ((dst >> 16) & 255) * ia) / 255;
        int g = (((src >> 8) & 255) * sa + ((dst >> 8) & 255) * ia) / 255;
        int b = ((src & 255) * sa + (dst & 255) * ia) / 255;
        int a = Math.min(255, sa + da * ia / 255);
        return (a << 24) | (r << 16) | (g << 8) | b;
    }

    private void blit(int[] out, int[] ts, int sx, int sy, int dx, int dy) {
        int W = pixW;
        for (int j = 0; j < TS; j++) {
            int oy = dy + j;
            if (oy < 0 || oy >= pixH) continue;
            for (int i = 0; i < TS; i++) {
                int ox = dx + i;
                if (ox < 0 || ox >= W) continue;
                int s = ts[(sy + j) * 256 + sx + i];
                if ((s >>> 24) == 0) continue;
                int o = oy * W + ox;
                out[o] = blend(out[o], s);
            }
        }
    }

    public void bake(Platform p) {
        Platform.Img tsImg = Assets.img("tiles/tiles_" + biome.key + ".png");
        if (tsImg == null) { baked = null; return; }
        int[] ts = p.pixels(tsImg);
        if (secrets.isEmpty()) baked = render(p, ts);
        else {
            byte[] real = t.clone();
            for (Secret sc : secrets) sc.apply(this, real, false);      // cerradas: todo el recuadro es roca
            baked = render(p, ts);
            for (Secret sc : secrets) sc.apply(this, real, true);       // abiertas: interior y entradas libres
            bakedOpen = render(p, ts);
            System.arraycopy(real, 0, t, 0, t.length);
        }
        // baldosa rompible: piedra con grietas
        int[] bt = new int[TS * TS];
        for (int j = 0; j < TS; j++) for (int i = 0; i < TS; i++) bt[j * TS + i] = ts[(1 * TS + j) * 256 + 15 * TS + i];
        int[] crack = {0x37, 0x47, 0x57, 0x66, 0x76, 0x86, 0x95, 0xA5, 0xB5, 0xC4, 0x5A, 0x6B, 0x7B, 0x8C, 0x9C, 0x3C, 0x2D, 0xCD, 0xDE};
        for (int c : crack) { int cx = c >> 4, cy = c & 15; bt[cy * TS + cx] = 0xFF0A0810; if (cx + 1 < TS) bt[cy * TS + cx + 1] = 0xFF1C1624; }
        for (int i = 0; i < TS; i++) { bt[i] = 0xFFC8A25A; bt[(TS - 1) * TS + i] = 0xFF6A5230; bt[i * TS] = 0xFFB08A48; bt[i * TS + TS - 1] = 0xFF6A5230; }
        breakImg = p.createImage(TS, TS, bt);
        int[] dt = new int[TS * TS];
        for (int j = 0; j < TS; j++) for (int i = 0; i < TS; i++) {
            int base = (i % 5 == 4) ? 0xFF2A180C : (((i / 5) + (j / 8)) % 2 == 0 ? 0xFF6A4224 : 0xFF7A4E2C);
            if (j < 2 || j >= TS - 2) base = 0xFF3A2410;
            dt[j * TS + i] = base;
        }
        for (int j = 3; j < TS; j += 8) for (int i = 0; i < TS; i++) dt[j * TS + i] = 0xFF9A9AA8;   // flejes de hierro
        dt[5 * TS + 8] = 0xFFFFD25A; dt[5 * TS + 9] = 0xFFFFD25A;
        doorImg = p.createImage(TS, TS, dt);
    }

    private Platform.Img render(Platform p, int[] ts) {
        int[] out = new int[pixW * pixH];
        // 1) pared de fondo (arte procedural por bioma; sin estilo, el dibujo antiguo por baldosas)
        TerrainArt.Style art = TerrainArt.style(biome);
        TerrainArt.t0 = System.nanoTime();
        TerrainArt.Ctx ctx = art != null ? new TerrainArt.Ctx(this, ts, art) : null;
        if (ctx != null) TerrainArt.background(ctx, out);
        else for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++) {
                int i = y * w + x;
                if (t[i] == SOLID || vista[i]) continue;
                int hv = (x * 73856093) ^ (y * 19349663);
                int col = 8 + ((hv >>> 8) & 3);
                blit(out, ts, col * TS, 3 * TS, x * TS, y * TS);
            }
        // 2) decoracion de fondo (pared, estandartes, colgantes)
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++) {
                int d = deco[y * w + x];
                if (d == 0) continue;
                int kind = d >> 8, idx = d & 255;
                if (kind == 1) blit(out, ts, (12 + (idx & 3)) * TS, 3 * TS, x * TS, y * TS);
                else if (kind == 2) blit(out, ts, (idx & 7) * TS, 6 * TS, x * TS, y * TS);
                else if (kind == 3) blit(out, ts, (8 + (idx & 7)) * TS, 4 * TS, x * TS, y * TS);
            }
        // 3) terreno
        if (ctx != null) { TerrainArt.terrain(ctx, out); TerrainArt.lap("repisas"); TerrainArt.lights(ctx, out); TerrainArt.lap("luces"); }
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++) {
                int v = t[y * w + x];
                if (v == SOLID) {
                    if (ctx != null) continue;
                    int mask = (solidN(x, y - 1) ? 1 : 0) | (solidN(x + 1, y) ? 2 : 0) | (solidN(x, y + 1) ? 4 : 0) | (solidN(x - 1, y) ? 8 : 0);
                    int hv = ((x * 73856093) ^ (y * 19349663)) >>> 6;
                    blit(out, ts, mask * TS, (hv % 3) * TS, x * TS, y * TS);
                } else if (v == ONEWAY) {
                    if (ctx != null) continue;
                    boolean l = tile(x - 1, y) == ONEWAY, r = tile(x + 1, y) == ONEWAY;
                    int col = (!l && !r) ? 0 : (!l ? 1 : (!r ? 3 : 2));
                    blit(out, ts, col * TS, 3 * TS, x * TS, y * TS);
                } else if (v == SPIKE) blit(out, ts, 4 * TS, 3 * TS, x * TS, y * TS);
                else if (v == SPIKE_DOWN) blit(out, ts, 5 * TS, 3 * TS, x * TS, y * TS);
            }
        // 4) props de suelo
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++) {
                int d = deco[y * w + x];
                if ((d >> 8) == 4) blit(out, ts, (d & 15) * TS, 5 * TS, x * TS, y * TS);
            }
        return p.createImage(pixW, pixH, out);
    }

    private boolean solidN(int x, int y) {
        if (x < 0 || x >= w || y < 0 || y >= h) return true;
        return t[y * w + x] == SOLID;
    }

    /** Antorchas/focos animados: devuelve las posiciones {px,py,tipo(5|6),indice}. */
    public List<int[]> animated() {
        List<int[]> l = new ArrayList<>();
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++) {
                int d = deco[y * w + x];
                int k = d >> 8;
                if (k == 5 || k == 6) l.add(new int[]{x * TS, y * TS, k, d & 255});
            }
        return l;
    }
}
