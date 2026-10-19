package com.julianfarks.roguelike.core;

import java.util.*;

/**
 * Mazmorras verticales: salas de combate con varias alturas conectadas, subsuelos, bucles, atajos y recompensas repartidas por rutas.
 *
 *  - A_COMPACT: la sala de siempre (suelo + un piso superior), solo con mas enemigos.
 *  - A_TALL:    piso inferior + piso superior + galerias de un 2º piso (con puente roto entre ellas) + un subsuelo (tunel con dos pozos: baja y vuelve a subir mas lejos).
 *  - A_DEEP:    como A_TALL + una torre de un 3er piso (camara del tesoro) + un 2º subsuelo (bucle propio) y mas enemigos.
 *
 * Toda la geometria usa las mismas baldosas y reglas que el resto del juego (SOLID / ONEWAY / SPIKE / BREAK) y se valida con el modelo estricto
 * de saltos y caidas (RoomCheck.reachTall): una sala solo se acepta si la salida, los cofres y todos los enemigos terrestres son alcanzables.
 * Los encuentros de las zonas profundas, la torre y las alcobas son opcionales (no cuentan para despejar la sala).
 */
final class Vertical {
    private Vertical() {}

    static final int A_COMPACT = 0, A_TALL = 1, A_DEEP = 2;
    static final int Z_MAIN = 0, Z_T1 = 1, Z_T2 = 2, Z_T3 = 3, Z_S1 = 4, Z_S2 = 5, Z_AIR = 6;
    static final String[] ARCH_NAME = {"compacta", "alta", "profunda"};

    /** Solo banco de pruebas: fuerza el arquetipo (-1 = el normal). */
    static int dbgArch = -1;
    static {
        try { String v = System.getenv("BOT_ARCH"); if (v != null) dbgArch = Integer.parseInt(v); } catch (RuntimeException e) { /* ignorar */ }
    }

    // ------------------------------------------------------------------ eleccion de arquetipo
    /** Arquetipo por bioma y sala (0,1,2): cada mazmorra mezcla salas compactas, altas y profundas en otro orden. */
    private static final int[][] TABLE = {
            {0, 1, 2},   // catacumbas (mazmorra de referencia)
            {1, 0, 2},   // forja
            {0, 2, 1},   // helado
            {2, 0, 1},   // vacio
            {1, 2, 0},   // bosque
            {1, 0, 2},   // tormenta
            {1, 2, 0},   // sangre
            {0, 2, 1},   // eclipse
            {0, 0, 0},   // cazador (solo jefe)
    };

    static int pick(Biome b, int type, int roomNo, Rng r) {
        if (dbgArch >= 0 && type == Room.COMBAT) return dbgArch;
        if (type != Room.COMBAT) return A_COMPACT;
        int a = TABLE[Math.max(0, Math.min(TABLE.length - 1, b.id))][Math.floorMod(roomNo, 3)];
        if (a != A_COMPACT && r.chance(0.2f)) a = a == A_DEEP ? A_TALL : A_DEEP;       // variacion: no siempre el mismo orden
        return a;
    }

    /** Alto de la sala, fila del suelo principal y ancho segun arquetipo. */
    static int fyOf(int arch) { return arch == A_DEEP ? 35 : (arch == A_TALL ? 27 : 22); }
    static int heightOf(int arch) { return arch == A_DEEP ? 58 : (arch == A_TALL ? 43 : 30); }

    // ------------------------------------------------------------------ estilo por bioma (arquitectura propia)
    static final class Style {
        boolean ragged;       // bajos irregulares (raices, roca fundida, islas del vacio)
        int wind;             // irregularidad de los tuneles (0-3)
        int ledges;           // repisas / ramas extra en las galerias
        int pillars;          // columnas de las galerias
        boolean wideGap;      // hueco ancho entre galerias (puente de fragmentos)
        String[] extra;       // enemigos que habitan tambien las alturas (voladores) aunque no sean de la lista del bioma
    }

    static Style style(String key) {
        Style s = new Style();
        s.wind = 1; s.ledges = 1; s.pillars = 2; s.extra = new String[0];
        switch (key) {
            case "catacumbas": s.pillars = 3; s.extra = new String[]{"murcielago", "fantasma"}; break;                  // criptas: columnas, murcielagos y espectros en lo alto
            case "bosque": s.ragged = true; s.wind = 3; s.ledges = 3; s.pillars = 1; s.extra = new String[]{"murcielago"}; break;   // raices, ramas y cuevas
            case "helado": s.wind = 2; s.ledges = 3; s.pillars = 1; s.wideGap = true; break;                                   // plataformas de hielo, saltos cuidadosos
            case "forja": s.ragged = true; s.wind = 1; s.pillars = 3; s.wideGap = true; break;                                  // puentes estrechos sobre el abismo
            case "vacio": s.ragged = true; s.wind = 2; s.ledges = 2; s.wideGap = true; s.pillars = 0; break;                    // islas flotantes
            case "tormenta": s.ledges = 2; s.pillars = 2; break;
            case "sangre": s.wind = 2; s.pillars = 3; s.extra = new String[0]; break;
            case "eclipse": s.ledges = 2; s.pillars = 2; s.wind = 2; break;
            default: break;
        }
        return s;
    }

    // ------------------------------------------------------------------ contexto de construccion
    static final class Ctx {
        Room rm; Rng r; Style st; int arch, stage, roomNo;
        int W, H, fy, mf, mf2, mf3, s1, s2;
        int[] ground; boolean[] blocked, slab1;
        boolean[] slab2, slab3;             // columnas con losa en el 2º y 3er piso (para camaras secretas)
        List<int[]> plats;                  // {x0,x1,fila} (informativo)
        List<int[]> gal = new ArrayList<>(); // galerias del 2º piso {a,b}
        int[] tower;                         // torre del 3er piso {a,b} (o null)
        int xdA = -1, xuB = -1, xc = -1, xd2 = -1;   // pozos: bajada al subsuelo 1, subida, bajada al subsuelo 2, subida
        int[] sub1, sub2;                    // {x0,x1} de los tuneles
        int[] alcove;                        // alcoba tras muro agrietado {x0,x1} (subsuelo 1)
        final List<int[]> chests = new ArrayList<>();   // {x,g,arg,guarded}
        final List<int[]> holes = new ArrayList<>();    // {x0,x1}: pozos con escalera de plataformas (no se colocan enemigos en ellas)
    }

    private static void fill(Room rm, int x0, int x1, int y0, int y1, int t) {
        for (int y = y0; y <= y1; y++) for (int x = x0; x <= x1; x++) rm.set(x, y, t);
    }

    private static void air(Ctx c, int x0, int x1, int y0, int y1) {
        for (int y = y0; y <= y1; y++) for (int x = x0; x <= x1; x++) if (x >= 2 && x < c.W - 2 && y >= 1 && y < c.H - 1) { c.rm.set(x, y, Room.AIR); c.rm.vista[y * c.W + x] = false; }
    }

    private static boolean airRect(Room rm, int x0, int x1, int y0, int y1) {
        for (int y = y0; y <= y1; y++) for (int x = x0; x <= x1; x++) if (rm.tile(x, y) != Room.AIR) return false;
        return true;
    }

    private static boolean secretNear(Room rm, int x0, int x1) {
        for (Secret s : rm.secrets) if (x1 >= s.rx0 - 3 && x0 <= s.rx1 + 3) return true;
        return false;
    }

    // ------------------------------------------------------------------ construccion
    /** Anade a la sala (ya con suelo, piso superior y camaras de siempre) los pisos extra, los subsuelos y las recompensas. */
    static void build(Ctx c) {
        Room rm = c.rm;
        rm.arch = c.arch; rm.fy = c.fy; rm.mf = c.mf;
        c.mf2 = c.mf - 9; c.mf3 = c.mf2 - 9;
        c.s1 = c.fy + 13; c.s2 = c.fy + 20;
        c.slab2 = new boolean[c.W]; c.slab3 = new boolean[c.W];
        // ---- pisos superiores
        tier2(c);
        if (c.arch == A_DEEP) tier3(c);
        // ---- camaras secretas y recompensas de las alturas (antes de colocar columnas y repisas)
        highSecrets(c);
        decorTier2(c);
        // ---- subsuelos
        underground(c);
        // ---- cofres con guardia
        chestSpots(c);
        rm.mf2 = c.gal.isEmpty() ? 0 : c.mf2; rm.mf3 = c.tower == null ? 0 : c.mf3;
        rm.s1 = c.sub1 == null ? 0 : c.s1; rm.s2 = c.sub2 == null ? 0 : c.s2;
        rm.xdA = Math.max(0, c.xdA); rm.xuB = Math.max(0, c.xuB); rm.xc = Math.max(0, c.xc); rm.xd2 = Math.max(0, c.xd2);
    }

    // ---------------------------------------------------------------- 2º piso: galerias con puente roto
    private static void tier2(Ctx c) {
        Room rm = c.rm; Rng r = c.r; int W = c.W, mf = c.mf, mf2 = c.mf2;
        // se buscan disposiciones al azar hasta que al menos una galeria tenga escalera valida (se prefieren dos galerias unidas por un puente roto)
        int[][] best = null; int[] bestH = null;
        for (int att = 0; att < 40; att++) {
            int gl = W >= 84 ? r.range(22, 28) : r.range(18, 22);
            int gap = c.st.wideGap ? r.range(7, 9) : r.range(5, 7);
            int a1 = r.range(14, 26), b1 = a1 + gl - 1;
            int a2 = b1 + gap + 1, b2 = Math.min(W - 15, a2 + gl - 1);
            int[][] gs = (b2 - a2 < 12) ? new int[][]{{a1, b1}} : new int[][]{{a1, b1}, {a2, b2}};
            if (b1 > W - 16) continue;
            int[] hs = new int[gs.length]; boolean all = true;
            for (int gi = 0; gi < gs.length; gi++) {
                int a = gs[gi][0], b = gs[gi][1];
                int h = gi == 0 ? a + 2 : b - 4;
                if (!tierSlabOk(c, h - 3, h + 5)) { h = gi == 0 ? b - 4 : a + 2; if (!tierSlabOk(c, h - 3, h + 5)) { all = false; hs[gi] = -1; continue; } }
                hs[gi] = h;
            }
            int ok = 0; for (int h : hs) if (h >= 0) ok++;
            if (ok == 0) continue;
            if (best == null || ok > countOk(bestH)) { best = gs; bestH = hs; }
            if (all) break;
        }
        if (best == null) return;
        for (int gi = 0; gi < best.length; gi++) {
            int a = best[gi][0], b = best[gi][1], h = bestH[gi];
            if (h < 0) continue;
            for (int x = a; x <= b; x++) { c.slab2[x] = true; rm.set(x, mf2, Room.SOLID); rm.set(x, mf2 + 1, Room.SOLID); rm.vista[mf2 * W + x] = false; rm.vista[(mf2 + 1) * W + x] = false; }
            for (int x = h; x <= h + 2; x++) { rm.set(x, mf2, Room.AIR); rm.set(x, mf2 + 1, Room.AIR); c.slab2[x] = false; }
            if (c.st.ragged) for (int x = a + 1; x < b; x++) if (c.slab2[x] && c.r.chance(0.3f) && Math.abs(x - h) > 3) rm.set(x, mf2 + 2, Room.SOLID);
            // escalera de plataformas del 2º piso al 1º: filas mf-3 y mf-6
            clearLedges(rm, h - 1, h + 4, mf - 7, mf - 1);
            rm.set(h, mf - 3, Room.ONEWAY); rm.set(h + 1, mf - 3, Room.ONEWAY);
            rm.set(h + 1, mf - 6, Room.ONEWAY); rm.set(h + 2, mf - 6, Room.ONEWAY);
            c.holes.add(new int[]{h, h + 2});
            c.gal.add(new int[]{a, b, h});
        }
        // puente roto entre dos galerias contiguas: fragmentos de 2-3 baldosas separados por huecos que se salvan de un salto
        if (c.gal.size() == 2 && c.gal.get(1)[0] - c.gal.get(0)[1] <= 10) {
            int x = c.gal.get(0)[1] + 1, end = c.gal.get(1)[0] - 1;
            while (x <= end - 1) {
                int len = Math.min(r.range(2, 3), end - x + 1);
                for (int k = 0; k < len; k++) { rm.set(x + k, mf2, Room.ONEWAY); c.slab2[x + k] = true; }
                x += len + r.range(1, 2);
            }
        }
    }

    private static int countOk(int[] hs) { int n = 0; if (hs != null) for (int h : hs) if (h >= 0) n++; return n; }

    private static boolean tierSlabOk(Ctx c, int x0, int x1) {
        if (x0 < 12 || x1 > c.W - 12) return false;
        for (int x = x0; x <= x1; x++) if (!c.slab1[x]) return false;
        // sin obstaculos del piso 1 en el volumen de la escalera
        for (int x = x0 + 1; x <= x1 - 1; x++) for (int y = c.mf - 8; y <= c.mf - 1; y++) { int t = c.rm.tile(x, y); if (t == Room.SOLID || t == Room.HWALL || t == Room.BREAK || t == Room.DOOR || t == Room.SPIKE) return false; }
        if (c.rm.secretSpots != null) for (int[] sp : c.rm.secretSpots) { int sx = sp[0] / Room.TS; if (sx >= x0 - 3 && sx <= x1 + 3) return false; }
        return !secretNear(c.rm, x0, x1);
    }

    private static void clearLedges(Room rm, int x0, int x1, int y0, int y1) {
        for (int y = y0; y <= y1; y++) for (int x = x0; x <= x1; x++) if (rm.tile(x, y) == Room.ONEWAY) rm.set(x, y, Room.AIR);
    }

    // ---------------------------------------------------------------- 3er piso: torre con camara
    private static void tier3(Ctx c) {
        Room rm = c.rm; Rng r = c.r; int W = c.W, mf2 = c.mf2, mf3 = c.mf3;
        List<int[]> opts = new ArrayList<>();
        for (int[] g : c.gal) if (g[1] - g[0] >= 17) opts.add(g);
        if (opts.isEmpty()) return;
        int[] g = opts.get(r.i(opts.size()));
        int tw = Math.min(g[1] - g[0] - 1, r.range(14, 16));
        int ta = g[0] + 1 + r.i(Math.max(1, g[1] - g[0] - tw));
        int tb = ta + tw - 1;
        if (tb > g[1] - 1 || Math.abs(g[2] - ta) < 0) return;
        // la escalera de la galeria al 1er piso esta en h..h+2 y queda libre de torre (la torre solo ocupa el tramo de la galeria sin esa escalera)
        int h = ta + 2;
        if (h >= g[2] - 4 && h <= g[2] + 6) { ta = Math.min(g[1] - tw, g[2] + 8); tb = ta + tw - 1; h = ta + 2; if (tb > g[1] - 1) return; }
        for (int x = ta; x <= tb; x++) {
            if (!c.slab2[x]) return;
            for (int y = mf3 - 1; y <= mf2 - 1; y++) if (rm.tile(x, y) != Room.AIR) return;
        }
        for (int x = ta; x <= tb; x++) { c.slab3[x] = true; rm.set(x, mf3, Room.SOLID); rm.set(x, mf3 + 1, Room.SOLID); rm.vista[mf3 * W + x] = false; rm.vista[(mf3 + 1) * W + x] = false; }
        for (int x = h; x <= h + 2; x++) { rm.set(x, mf3, Room.AIR); rm.set(x, mf3 + 1, Room.AIR); c.slab3[x] = false; }
        rm.set(h, mf2 - 3, Room.ONEWAY); rm.set(h + 1, mf2 - 3, Room.ONEWAY);
        rm.set(h + 1, mf2 - 6, Room.ONEWAY); rm.set(h + 2, mf2 - 6, Room.ONEWAY);
        c.tower = new int[]{ta, tb, h};
        c.holes.add(new int[]{h, h + 2});
    }

    // ---------------------------------------------------------------- camaras secretas en las alturas
    private static void highSecrets(Ctx c) {
        Room rm = c.rm;
        boolean deep = c.arch == A_DEEP;
        if (deep && c.tower == null) deep = false;
        boolean[] slab = deep ? c.slab3 : c.slab2;
        int row = deep ? c.mf3 : c.mf2;
        if (!deep && c.gal.isEmpty()) return;
        int fam = 1;
        Secret sc = SecretGen.build(rm, c.W, c.fy, row, c.ground, c.blocked, slab, c.r, c.stage, fam);
        if (sc != null) rm.vaultA = sc.rx0;
    }

    // ---------------------------------------------------------------- columnas, repisas y arquitectura de las galerias
    private static void decorTier2(Ctx c) {
        Room rm = c.rm; Rng r = c.r; int mf2 = c.mf2;
        for (int[] g : c.gal) {
            int a = g[0], b = g[1], h = g[2];
            // columnas (se saltan: 2 baldosas de alto)
            int np = c.st.pillars;
            for (int k = 0; k < np; k++) {
                int x = r.range(a + 3, b - 4);
                if (Math.abs(x - h) < 6 || Math.abs(x - (h + 1)) < 6) continue;
                if (!colFree(c, x, 2, mf2)) continue;
                rm.set(x, mf2 - 1, Room.SOLID); rm.set(x + 1, mf2 - 1, Room.SOLID);
                rm.set(x, mf2 - 2, Room.SOLID); rm.set(x + 1, mf2 - 2, Room.SOLID);
            }
            // repisas / ramas a 3 de altura
            for (int k = 0; k < c.st.ledges; k++) {
                int x = r.range(a + 3, b - 8), len = r.range(3, 5);
                if (Math.abs(x - h) < 7 || Math.abs(x + len - h) < 7) continue;
                boolean ok = true;
                for (int i = -1; i <= len && ok; i++) for (int y = mf2 - 6; y <= mf2 - 1; y++) if (rm.tile(x + i, y) != Room.AIR) ok = false;
                if (!ok) continue;
                for (int i = 0; i < len; i++) rm.set(x + i, mf2 - 4, Room.ONEWAY);
            }
        }
    }

    private static boolean colFree(Ctx c, int x, int hgt, int g) {
        for (int i = -1; i <= 2; i++) for (int y = g - 6; y <= g - 1; y++) if (c.rm.tile(x + i, y) != Room.AIR) return false;
        return c.slab2[x] && c.slab2[x + 1];
    }

    // ---------------------------------------------------------------- subsuelos
    private static boolean mainFlat(Ctx c, int x0, int x1) {
        if (x0 < 12 || x1 > c.W - 24) return false;
        for (int x = x0; x <= x1; x++) {
            if (c.ground[x] != c.fy || c.blocked[x] || !c.slab1[x]) return false;
            if (c.rm.tile(x, c.fy - 1) != Room.AIR || c.rm.tile(x, c.fy - 2) != Room.AIR) return false;
            if (c.rm.spikeCols != null && c.rm.spikeCols.contains(x)) return false;
        }
        return !secretNear(c.rm, x0, x1);
    }

    private static void underground(Ctx c) {
        Room rm = c.rm; Rng r = c.r; int fy = c.fy, W = c.W;
        // pozos de bajada (A) y de subida (B), 3 de ancho; la subida queda lejos para que el tunel sea un atajo/bucle
        List<Integer> flat = new ArrayList<>();
        for (int x = 14; x < W - 30; x++) if (mainFlat(c, x - 1, x + 3)) flat.add(x);
        List<int[]> pairs = new ArrayList<>();
        for (int a1 : flat) for (int b1 : flat) if (b1 >= a1 + 22 && b1 + 6 < W - 24 && a1 <= W * 2 / 3) pairs.add(new int[]{a1, b1});
        if (pairs.isEmpty()) return;
        int[] pr = pairs.get(r.i(pairs.size()));
        int xd = pr[0], xu = pr[1];
        c.xdA = xd; c.xuB = xu;
        int t0 = Math.max(8, xd - 7), t1 = Math.min(W - 16, xu + 11);
        c.sub1 = new int[]{t0, t1};
        // ---- tunel del subsuelo 1: filas fy+8..fy+12 libres, suelo en fy+13
        air(c, t0, t1, fy + 8, fy + 12);
        irregular(c, t0, t1, fy + 8, fy + 12, new int[]{xd - 2, xd + 4, xu - 2, xu + 4});
        for (int x : new int[]{xd, xu}) {
            air(c, x, x + 2, fy, fy + 7);                                        // pozo desde el suelo principal
            for (int k = 0; k < 4; k++) {
                int g = c.s1 - 3 * (k + 1);                                       // fy+10, fy+7, fy+4, fy+1
                int px = x + (k % 2 == 0 ? 0 : 1);
                rm.set(px, g, Room.ONEWAY); rm.set(px + 1, g, Room.ONEWAY);
            }
            c.ground[x] = c.ground[x + 1] = c.ground[x + 2] = -1;
            c.holes.add(new int[]{x, x + 3});
            if (c.rm.ground != null) { rm.ground[x] = rm.ground[x + 1] = rm.ground[x + 2] = -1; }
        }
        // ---- alcoba tras un muro agrietado al final del tunel (cofre secreto)
        alcove(c, t1);
        // ---- subsuelo 2
        if (c.arch == A_DEEP) {
            List<int[]> sp = new ArrayList<>();
            for (int xa = t0 + 9; xa <= t1 - 12; xa++) for (int xb = xa + 14; xb <= t1 - 12 && xb <= xa + 30; xb++) {
                if (Math.abs(xa - xd) > 5 && Math.abs(xa - xu) > 5 && Math.abs(xb - xd) > 5 && Math.abs(xb - xu) > 5) sp.add(r.chance(0.5f) ? new int[]{xa, xb} : new int[]{xb, xa});
            }
            if (!sp.isEmpty()) {
                int[] q = sp.get(r.i(sp.size()));
                int xc = q[0], xdd = q[1];
                c.xc = xc; c.xd2 = xdd;
                int u0 = Math.max(8, Math.min(xc, xdd) - 9), u1 = Math.min(W - 9, Math.max(xc, xdd) + 12);
                c.sub2 = new int[]{u0, u1};
                air(c, u0, u1, fy + 15, fy + 19);
                irregular(c, u0, u1, fy + 15, fy + 19, new int[]{xc - 2, xc + 4, xdd - 2, xdd + 4, u0, u0 + 8});
                air(c, xc, xc + 2, fy + 13, fy + 14);                              // caida del subsuelo 1 al 2
                air(c, xdd, xdd + 2, fy + 13, fy + 14);                            // subida del 2 al 1
                rm.set(xdd, c.s2 - 3, Room.ONEWAY); rm.set(xdd + 1, c.s2 - 3, Room.ONEWAY);
                rm.set(xdd + 1, c.s2 - 6, Room.ONEWAY); rm.set(xdd + 2, c.s2 - 6, Room.ONEWAY);
                // alcoba abierta del fondo (zona de recompensa opcional)
                c.chests.add(new int[]{u0 + 3, c.s2, 2, 0, Z_S2});
            }
        }
        decorTunnel(c, c.sub1, fy + 12);
        if (c.sub2 != null) decorTunnel(c, c.sub2, fy + 19);
    }

    /** Techos que bajan, suelos que suben, repisas y fosos de pinchos: el tunel deja de ser un rectangulo. Los rasgos nunca se solapan (siempre queda paso). */
    private static void irregular(Ctx c, int x0, int x1, int top, int bot, int[] avoid) {
        Room rm = c.rm; Rng r = c.r; int wind = c.st.wind;
        int g = bot + 1;                                               // fila del suelo
        List<int[]> used = new ArrayList<>();
        for (int i = 0; i < avoid.length; i += 2) used.add(new int[]{avoid[i] - 2, avoid[i + 1] + 2});
        int n = 3 + wind * 2;
        for (int k = 0; k < n; k++) {
            int x = r.range(x0 + 4, x1 - 8), w = r.range(3, 6);
            if (overlaps(used, x - 3, x + w + 3)) continue;
            switch (r.i(4)) {
                case 0: for (int i = 0; i < w; i++) { rm.set(x + i, top, Room.SOLID); rm.set(x + i, top + 1, Room.SOLID); } break;           // techo bajo
                case 1: for (int i = 0; i < w; i++) rm.set(x + i, bot, Room.SOLID); break;                                                 // suelo +1
                case 2: for (int i = 0; i < w; i++) { rm.set(x + i, bot, Room.SOLID); if (i > 0 && i < w - 1) rm.set(x + i, bot - 1, Room.SOLID); } break;   // lomo +2
                default: {                                                                                                                  // repisa a 3 de altura
                    boolean ok = true;
                    for (int i = -1; i <= w; i++) for (int y = g - 5; y <= g - 1; y++) if (rm.tile(x + i, y) != Room.AIR) ok = false;
                    if (ok) for (int i = 0; i < w; i++) rm.set(x + i, g - 3, Room.ONEWAY);
                }
            }
            used.add(new int[]{x, x + w});
        }
        // foso de pinchos de 2-3 baldosas con repisa por encima
        if (r.chance(0.6f)) {
            int x = r.range(x0 + 8, x1 - 12), w = r.range(2, 3);
            if (!overlaps(used, x - 4, x + w + 4)) {
                boolean ok = true;
                for (int i = -3; i < w + 3 && ok; i++) for (int y = top; y <= bot; y++) if (rm.tile(x + i, y) != Room.AIR) ok = false;
                if (ok) { for (int i = 0; i < w; i++) rm.set(x + i, bot, Room.SPIKE); for (int i = -1; i <= w; i++) rm.set(x + i, g - 3, Room.ONEWAY); }
            }
        }
    }

    private static boolean overlaps(List<int[]> used, int a, int b) { for (int[] u : used) if (b >= u[0] && a <= u[1]) return true; return false; }

    private static void alcove(Ctx c, int t1) {
        Room rm = c.rm; int fy = c.fy, W = c.W;
        int x0 = t1 + 3, x1 = Math.min(W - 6, t1 + 10);
        if (x1 - x0 < 5 || t1 + 3 >= W - 6) return;
        air(c, x0, x1, fy + 8, fy + 12);
        for (int y = fy + 8; y <= fy + 12; y++) { rm.set(t1 + 1, y, Room.BREAK); rm.set(t1 + 2, y, Room.BREAK); }
        // la columna t1 del tunel pasa a ser pared hueca: el tunel termina en t1
        c.alcove = new int[]{x0, x1};
        int cx = (x0 + x1) / 2;
        c.chests.add(new int[]{cx, c.s1, 3, 0, Z_S1});
        rm.optionalSpots.add(new int[]{cx, c.s1});
    }

    private static void decorTunnel(Ctx c, int[] span, int floor) {
        Room rm = c.rm; int W = c.W;
        for (int x = span[0] + 3; x < span[1] - 2; x += 8 + c.r.i(3)) {
            int y = floor - 4;
            if (rm.tile(x, y) == Room.AIR && rm.deco[y * W + x] == 0) rm.deco[y * W + x] = (short) ((5 << 8) | c.r.i(4));
        }
        for (int x = span[0] + 2; x < span[1] - 1; x++) {
            if (c.r.chance(0.10f) && rm.tile(x, floor - 5) == Room.AIR && rm.deco[(floor - 5) * W + x] == 0) rm.deco[(floor - 5) * W + x] = (short) ((3 << 8) | c.r.i(8));
        }
    }

    // ---------------------------------------------------------------- cofres con guardia
    private static void chestSpots(Ctx c) {
        Room rm = c.rm; Rng r = c.r;
        // 2º piso: cofre en el extremo de la ultima galeria (guardado por enemigos)
        if (!c.gal.isEmpty()) {
            int[] g = c.gal.get(c.gal.size() - 1);
            int x = g[1] - 3;
            if (rm.tile(x, c.mf2 - 1) == Room.AIR && rm.tile(x, c.mf2) == Room.SOLID && rm.tile(x, c.mf2 - 2) == Room.AIR) c.chests.add(new int[]{x, c.mf2, 1, 1, Z_T2});
        }
        // 1er piso: cofre en la repisa alta de un extremo (normal)
        int x1 = c.W - 20;
        for (int d = 0; d < 12; d++) {
            int x = x1 - d;
            if (x > 14 && c.slab1[x] && c.slab1[x + 1] && !SecretGen.reserved(rm, x) && rm.tile(x, c.mf - 1) == Room.AIR && rm.tile(x, c.mf - 2) == Room.AIR && rm.tile(x, c.mf - 3) == Room.AIR && rm.tile(x, c.mf) == Room.SOLID) {
                c.chests.add(new int[]{x, c.mf, 0, 0, Z_T1}); break;
            }
        }
        for (int[] ch : c.chests) {
            rm.props.add(new Room.PropSpec("chest", ch[0] * Room.TS + 8, ch[1] * Room.TS, ch[2]));
            rm.optionalSpots.add(new int[]{ch[0], ch[1]});
        }
    }

    // ------------------------------------------------------------------ zonas
    static int zoneOf(Room rm, int g) {
        if (!rm.tall) return Z_MAIN;
        int fy = rm.fy;
        if (g <= fy - 24) return Z_T3;
        if (g <= fy - 15) return Z_T2;
        if (g <= fy - 8) return Z_T1;
        if (g <= fy + 5) return Z_MAIN;
        if (g <= fy + 14) return Z_S1;
        return Z_S2;
    }

    // ------------------------------------------------------------------ enemigos
    private static final int G_MELEE = 0, G_RANGED = 1, G_HEAVY = 2, G_FLY = 3;

    private static int groupOf(EnemyDef d) {
        switch (d.role) {
            case EnemyDef.RANGED: case EnemyDef.CASTER: case EnemyDef.SNIPER: case EnemyDef.SUPPORT: case EnemyDef.BUFFER: case EnemyDef.TURRET: return G_RANGED;
            case EnemyDef.HEAVY: case EnemyDef.CHARGER: case EnemyDef.SHIELD: return G_HEAVY;
            case EnemyDef.FLY_SHOOT: case EnemyDef.FLY_DIVE: return G_FLY;
            default: return G_MELEE;
        }
    }

    /** Enemigos extra sobre la base de cada arquetipo (dificultad creciente con el piso y la sala). */
    static int extraCount(int stage, int roomNo, Rng r) { return stage + (roomNo >= 2 ? 1 : 0) + r.i(2); }

    /** Enemigos de una sala compacta: mas que antes (antes 3-5), creciendo con la sala (la primera sigue siendo suave). */
    static int compactCount(int stage, int roomNo, Rng r) { return 4 + stage + (roomNo >= 1 ? 1 : 0) + (roomNo >= 2 ? 1 : 0) + r.i(2); }

    /** Minimo de enemigos que debe tener una sala de cada arquetipo para aceptarla. */
    static int minEnemies(int arch) { return arch == A_DEEP ? 10 : (arch == A_TALL ? 8 : 4); }

    /**
     * Reparte los enemigos por alturas a partir de las casillas alcanzables desde la entrada: asi nunca quedan en sitios imposibles.
     * Zona -> cuota: suelo, piso 1, piso 2, torre, subsuelos, y voladores en el aire de las alturas.
     */
    static void spawn(Ctx c) {
        Room rm = c.rm; Rng r = c.r; int W = c.W, fy = c.fy;
        Set<Integer> reach = RoomCheck.reachTall(rm, 4, fy, null);
        Map<Integer, List<int[]>> byZone = new HashMap<>();
        for (int key : reach) {
            int g = key / 1000, x = key % 1000;
            if (x < 12 || x > W - 10) continue;
            int t = rm.tile(x, g);
            if (t != Room.SOLID && t != Room.ONEWAY) continue;
            if (rm.tile(x - 1, g) == Room.SPIKE || rm.tile(x + 1, g) == Room.SPIKE) continue;
            if (RoomCheck.inSecret(rm, x, g - 1)) continue;
            if (SecretGen.reserved(rm, x)) continue;
            // de pie en una plataforma con vacio a ambos lados no (evita enemigos en una unica baldosa)
            if (!RoomCheck.node(rm, x - 1, g) && !RoomCheck.node(rm, x + 1, g)) continue;
            // lejos de la entrada y de la salida
            if (x < 14 && g >= fy - 4) continue;
            if (x > W - 12 && g >= fy - 4) continue;
            // no encima de los pozos (el suelo ahi son plataformas pequenas) ni del cofre
            byZone.computeIfAbsent(zoneOf(rm, g), z -> new ArrayList<>()).add(new int[]{x, g});
        }
        int[][] q = quotas(c.arch, extraCount(c.stage, c.roomNo, r));          // {zona, cuota, opcional(0/1)}
        String[] pool = pool(rm.biome);
        List<EnemyDef>[] groups = groups(pool, c.st.extra);
        List<int[]> placed = new ArrayList<>();
        int heavies = 0, maxHeavy = c.arch == A_DEEP ? 3 : 2 + (c.stage >= 1 ? 1 : 0);
        for (int[] qq : q) {
            int z = qq[0], n = qq[1];
            boolean opt = qq[2] == 1;
            List<int[]> cand = byZone.getOrDefault(z, new ArrayList<>());
            if (z == Z_AIR) { air(c, rm, reach, n, groups, placed); continue; }
            Collections.shuffle(cand, new java.util.Random(r.next()));
            for (int i = 0; i < n; i++) {
                int[] pos = null;
                for (int[] cd : cand) {
                    boolean ok = true;
                    for (int[] p : placed) if (Math.abs(p[0] - cd[0]) < 4 && Math.abs(p[1] - cd[1]) < 3) { ok = false; break; }
                    if (ok) { pos = cd; break; }
                }
                if (pos == null) break;
                boolean ledge = rm.tile(pos[0], pos[1]) == Room.ONEWAY;
                int grp = pickGroup(z, ledge, r);
                EnemyDef d = pickEnemy(groups, grp, r);
                if (d == null) continue;
                if (groupOf(d) == G_HEAVY) { if (heavies >= maxHeavy) { d = pickEnemy(groups, G_MELEE, r); if (d == null) continue; } else heavies++; }
                Room.Spawn sp = new Room.Spawn(d.id, pos[0] * Room.TS + 8, pos[1] * Room.TS, false);
                sp.optional = opt; sp.zone = z;
                rm.spawns.add(sp);
                placed.add(new int[]{pos[0], pos[1]});
            }
        }
        // relleno: lo que no cupo en su zona se reparte por las demas (obligatorios), con separacion algo menor
        int target = 0; for (int[] qq : q) if (qq[2] == 0) target += qq[1];
        int have = 0; for (Room.Spawn sp : rm.spawns) if (!sp.optional) have++;
        List<Integer> zs = new ArrayList<>(byZone.keySet()); Collections.sort(zs);
        for (int guard = 0; have < target && guard < 200; guard++) {
            int z = zs.get(guard % zs.size());
            if (z == Z_T3 || z == Z_S2 || z == Z_AIR) continue;
            List<int[]> cand = byZone.get(z); Collections.shuffle(cand, new java.util.Random(r.next()));
            for (int[] cd : cand) {
                boolean ok = true;
                for (int[] p : placed) if (Math.abs(p[0] - cd[0]) < 3 && Math.abs(p[1] - cd[1]) < 2) { ok = false; break; }
                if (!ok) continue;
                EnemyDef d = pickEnemy(groups, rm.tile(cd[0], cd[1]) == Room.ONEWAY ? G_RANGED : G_MELEE, r);
                if (d == null) break;
                Room.Spawn sp = new Room.Spawn(d.id, cd[0] * Room.TS + 8, cd[1] * Room.TS, false);
                sp.zone = z; rm.spawns.add(sp); placed.add(new int[]{cd[0], cd[1]}); have++;
                break;
            }
        }
        // guardias junto a los cofres
        for (int[] ch : c.chests) {
            if (ch[3] != 1) continue;
            for (int k = 0; k < 2; k++) {
                int gx = ch[0] + (k == 0 ? -4 : 4), gg = ch[1];
                if (!reach.contains(gg * 1000 + gx) || !RoomCheck.node(rm, gx, gg)) continue;
                boolean ok = true;
                for (int[] p : placed) if (Math.abs(p[0] - gx) < 3 && Math.abs(p[1] - gg) < 3) ok = false;
                if (!ok) continue;
                EnemyDef d = pickEnemy(groups, r.chance(0.5f) ? G_MELEE : G_RANGED, r);
                if (d == null) continue;
                Room.Spawn sp = new Room.Spawn(d.id, gx * Room.TS + 8, gg * Room.TS, false);
                sp.optional = ch[4] == Z_S2; sp.zone = ch[4];
                rm.spawns.add(sp); placed.add(new int[]{gx, gg});
            }
        }
    }

    /** Cuotas por zona segun arquetipo ({zona, cuota, opcional}). Los de zonas profundas, torre y alcobas son opcionales. Los extras van al suelo y al piso 1. */
    private static int[][] quotas(int arch, int extra) {
        int[][] base;
        if (arch == A_DEEP) base = new int[][]{{Z_MAIN, 2, 0}, {Z_T1, 1, 0}, {Z_T2, 2, 0}, {Z_S1, 2, 0}, {Z_AIR, 1, 0}, {Z_T3, 1, 1}, {Z_S2, 2, 1}};
        else if (arch == A_TALL) base = new int[][]{{Z_MAIN, 2, 0}, {Z_T1, 2, 0}, {Z_T2, 1, 0}, {Z_S1, 2, 0}, {Z_AIR, 1, 0}};
        else base = new int[][]{{Z_MAIN, 3, 0}, {Z_T1, 1, 0}, {Z_AIR, 0, 0}};
        for (int i = 0; i < extra; i++) base[i % 2 == 0 ? 0 : 1][1]++;
        return base;
    }

    private static int pickGroup(int zone, boolean ledge, Rng r) {
        float p = r.f();
        if (zone == Z_T2 || zone == Z_T3) return ledge ? (p < 0.8f ? G_RANGED : G_MELEE) : (p < 0.45f ? G_RANGED : (p < 0.85f ? G_MELEE : G_HEAVY));
        if (zone == Z_S1 || zone == Z_S2) return p < 0.55f ? G_MELEE : (p < 0.8f ? G_HEAVY : G_RANGED);
        if (zone == Z_T1) return p < 0.45f ? G_MELEE : (p < 0.75f ? G_RANGED : G_HEAVY);
        return ledge ? G_RANGED : (p < 0.5f ? G_MELEE : (p < 0.75f ? G_HEAVY : G_RANGED));
    }

    private static String[] pool(Biome b) { return b.enemies; }

    @SuppressWarnings("unchecked")
    private static List<EnemyDef>[] groups(String[] pool, String[] extra) {
        List<EnemyDef>[] g = new List[4];
        for (int i = 0; i < 4; i++) g[i] = new ArrayList<>();
        for (String id : pool) { EnemyDef d = EnemyDef.get(id); if (d != null) g[groupOf(d)].add(d); }
        for (String id : extra) { EnemyDef d = EnemyDef.get(id); if (d != null && groupOf(d) == G_FLY) g[G_FLY].add(d); }
        return g;
    }

    private static EnemyDef pickEnemy(List<EnemyDef>[] g, int grp, Rng r) {
        if (!g[grp].isEmpty()) return g[grp].get(r.i(g[grp].size()));
        for (int k = 0; k < 4; k++) if (k != G_FLY && !g[k].isEmpty()) return g[k].get(r.i(g[k].size()));
        return null;
    }

    /** Voladores: ocupan las alturas, en aire libre sobre casillas alcanzables del piso 1 / 2. */
    private static void air(Ctx c, Room rm, Set<Integer> reach, int n, List<EnemyDef>[] groups, List<int[]> placed) {
        if (n <= 0) return;
        List<EnemyDef> fl = groups[G_FLY];
        List<int[]> cand = new ArrayList<>();
        for (int key : reach) {
            int g = key / 1000, x = key % 1000;
            int z = zoneOf(rm, g);
            if ((z != Z_T1 && z != Z_T2 && z != Z_MAIN) || x < 16 || x > rm.w - 14) continue;
            int cy = g - 5;
            boolean free = true;
            for (int ax = -1; ax <= 1 && free; ax++) for (int ay = -2; ay <= 1 && free; ay++) if (!RoomCheck.clear(rm, x + ax, cy + ay) || rm.tile(x + ax, cy + ay) == Room.SPIKE) free = false;
            if (free) cand.add(new int[]{x, cy, z});
        }
        Collections.shuffle(cand, new java.util.Random(c.r.next()));
        for (int i = 0; i < n; i++) {
            int[] pos = null;
            for (int[] cd : cand) {
                boolean ok = true;
                for (int[] p : placed) if (Math.abs(p[0] - cd[0]) < 8 && Math.abs(p[1] - cd[1]) < 6) { ok = false; break; }
                if (ok) { pos = cd; break; }
            }
            if (pos == null) break;
            EnemyDef d = fl.isEmpty() ? pickEnemy(groups, G_RANGED, c.r) : fl.get(c.r.i(fl.size()));
            if (d == null) continue;
            boolean flying = groupOf(d) == G_FLY;
            Room.Spawn sp;
            if (flying) sp = new Room.Spawn(d.id, pos[0] * Room.TS + 8, pos[1] * Room.TS, false);
            else {      // sin voladores en el bioma: un tirador en la altura mas cercana
                sp = new Room.Spawn(d.id, pos[0] * Room.TS + 8, (pos[1] + 5) * Room.TS, false);
            }
            sp.zone = Z_AIR;
            rm.spawns.add(sp);
            placed.add(new int[]{pos[0], pos[1]});
        }
    }

    // ------------------------------------------------------------------ validacion
    /** true si la sala vertical es jugable: entrada -> salida, cofres de la ruta, enemigos obligatorios y estructura prometida. */
    /** Solo pruebas: motivo del ultimo rechazo y contadores. */
    static final Map<String, Integer> whyCount = new TreeMap<>();
    private static boolean no(String why) { whyCount.merge(why, 1, Integer::sum); return false; }

    static boolean validate(Room rm, int minEnemies) {
        int sx = (int) (rm.spawnX / Room.TS), sg = Math.round(rm.spawnY / Room.TS);
        int ex = (int) (rm.exitX / Room.TS), eg = Math.round(rm.exitY / Room.TS);
        if (!RoomCheck.node(rm, sx, sg) || !RoomCheck.node(rm, ex, eg)) return no("entrada/salida sin suelo");
        Set<Integer> rs = RoomCheck.reachTall(rm, sx, sg, null);
        if (!rs.contains(eg * 1000 + ex)) return no("salida inalcanzable");
        // alcoba tras muro agrietado: alcanzable con el muro roto
        byte[] save = rm.t.clone();
        for (int i = 0; i < rm.t.length; i++) if (rm.t[i] == Room.BREAK) rm.t[i] = Room.AIR;
        Set<Integer> open = RoomCheck.reachTall(rm, sx, sg, null);
        System.arraycopy(save, 0, rm.t, 0, save.length);
        for (Room.PropSpec p : rm.props) {
            if (!p.kind.equals("chest")) continue;
            int cx = (int) (p.x / Room.TS), cg = Math.round(p.y / Room.TS);
            if (RoomCheck.inSecret(rm, cx, cg - 1)) continue;                       // las camaras secretas ya las valido SecretGen
            if (!open.contains(cg * 1000 + cx)) return no("cofre inalcanzable arg=" + p.arg + " zona=" + zoneOf(rm, cg));
        }
        int n = 0;
        for (Room.Spawn sp : rm.spawns) {
            if (!sp.optional) n++;
            if (RoomCheck.isFlyer(sp.enemy)) continue;
            int tx = (int) (sp.x / Room.TS), ty = Math.round(sp.y / Room.TS);
            if (!rs.contains(ty * 1000 + tx)) return no("enemigo inalcanzable zona=" + sp.zone);
        }
        if (n < minEnemies) return no("pocos enemigos");
        if (rm.arch >= A_TALL && rm.mf2 == 0) return no("sin 2º piso");
        if (rm.arch >= A_TALL && rm.s1 == 0) return no("sin subsuelo 1");
        if (rm.arch == A_DEEP && rm.s2 == 0) return no("sin subsuelo 2");
        if (rm.arch == A_DEEP && rm.mf3 == 0) return no("sin torre");
        return true;
    }
}
