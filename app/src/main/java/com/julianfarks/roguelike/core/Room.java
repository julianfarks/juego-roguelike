package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/** Mapa de baldosas de una sala + datos de aparicion + imagen precalculada. */
public final class Room {
    public static final int TS = 16;
    public static final int AIR = 0, SOLID = 1, ONEWAY = 2, SPIKE = 3, SPIKE_DOWN = 4;
    // tipos de sala
    public static final int START = 0, COMBAT = 1, ELITE = 2, BLESSING = 3, FORGE = 4, SHOP = 5, FOUNTAIN = 6, TREASURE = 7, BOSS = 8, REST = 9, HUB = 10;

    public static final class Spawn {
        public final String enemy; public final float x, y; public final boolean elite;
        Spawn(String e, float x, float y, boolean elite) { this.enemy = e; this.x = x; this.y = y; this.elite = elite; }
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
    public Platform.Img baked;
    public int pixW, pixH;
    public int[] ground;               // fila de superficie por columna (-1 = foso)

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

    public boolean solid(int x, int y) { return tile(x, y) == SOLID; }

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
        int[] out = new int[pixW * pixH];
        // 1) pared de fondo
        for (int y = 0; y < h; y++)
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
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++) {
                int v = t[y * w + x];
                if (v == SOLID) {
                    int mask = (solidN(x, y - 1) ? 1 : 0) | (solidN(x + 1, y) ? 2 : 0) | (solidN(x, y + 1) ? 4 : 0) | (solidN(x - 1, y) ? 8 : 0);
                    int hv = ((x * 73856093) ^ (y * 19349663)) >>> 6;
                    blit(out, ts, mask * TS, (hv % 3) * TS, x * TS, y * TS);
                } else if (v == ONEWAY) {
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
        baked = p.createImage(pixW, pixH, out);
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
