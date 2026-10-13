package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/** Generador procedural de salas. */
public final class RoomGen {
    private RoomGen() {}

    public static Room generate(int type, Biome b, Rng r, int stage, int roomNo) {
        boolean calm = type == Room.START || type == Room.BLESSING || type == Room.FORGE || type == Room.SHOP || type == Room.FOUNTAIN
                || type == Room.TREASURE || type == Room.REST || type == Room.HUB;
        boolean boss = type == Room.BOSS;
        boolean big = !calm && !boss;
        int W = boss ? 48 : (calm ? r.range(38, 44) : r.range(72, 104));
        int H = boss ? 22 : (big ? 30 : 20);
        Room rm = new Room(W, H, type, b);
        int fy = big ? 22 : H - 4;
        int pitRow = big ? fy + 3 : H - 1;
        int mf = fy - 10;                       // fila de la losa del piso superior
        boolean[] slab = new boolean[W];
        List<int[]> upCand = new ArrayList<>();
        List<int[]> secrets = new ArrayList<>();
        rm.secretSpots = secrets;
        int[] ground = new int[W];
        int[] ceil = new int[W];
        boolean[] blocked = new boolean[W];
        Arrays.fill(ground, fy);
        Arrays.fill(ceil, boss ? 3 : 2);
        List<int[]> platforms = new ArrayList<>();   // {x0,x1,row}

        if (!calm && !boss) layout(W, fy, ground, ceil, blocked, platforms, r, rm);
        else if (boss) {
            platforms.add(new int[]{7, 13, fy - 4});
            platforms.add(new int[]{W - 14, W - 8, fy - 4});
            platforms.add(new int[]{W / 2 - 3, W / 2 + 3, fy - 7});
        } else if (type != Room.HUB) {
            int px = r.range(6, 10);
            platforms.add(new int[]{px, px + 5, fy - 4});
            platforms.add(new int[]{W - px - 6, W - px - 1, fy - 4});
        }

        if (big) buildUpper(rm, W, fy, mf, ground, ceil, blocked, slab, platforms, r);

        // ----- rellenar baldosas -----
        for (int x = 0; x < W; x++) {
            for (int y = 0; y < H; y++) {
                boolean solid;
                if (x < 2 || x >= W - 2) solid = true;
                else if (y < ceil[x]) solid = true;
                else if (ground[x] >= 0) solid = y >= ground[x];
                else solid = y >= pitRow;
                if (big && slab[x] && (y == mf || y == mf + 1)) solid = true;
                if (solid) rm.set(x, y, Room.SOLID);
                else if (ground[x] < 0 && y == pitRow - 1) rm.set(x, y, Room.SPIKE);
            }
        }
        for (int[] p : platforms) for (int x = p[0]; x <= p[1]; x++) if (rm.tile(x, p[2]) == Room.AIR) rm.set(x, p[2], Room.ONEWAY);
        // pilares
        for (int x = 0; x < W; x++) if (blocked[x]) {
            int hgt = 2 + (x * 7 % 2);
            for (int k = 1; k <= hgt; k++) rm.set(x, ground[x] - k, Room.SOLID);
        }
        // pinchos de techo y de suelo ocasionales
        for (int x = 2; x < W - 2; x++) {
            if (ceil[x] > 2 && r.chance(0.12f)) rm.set(x, ceil[x], Room.SPIKE_DOWN);
        }
        rm.ground = ground;
        if (big) {
            buildSecrets(rm, W, fy, mf, ground, blocked, slab, r, stage);
            // pinchos en el piso superior
            for (int k = 0; k < r.range(1, 3); k++) {
                int x = r.range(16, W - 20), n = r.range(2, 3);
                boolean ok = true;
                for (int i = -3; i < n + 3; i++) if (x + i < 0 || x + i >= W || !slab[x + i] || rm.tile(x + i, mf - 1) != Room.AIR || rm.tile(x + i, mf - 5) == Room.SOLID) ok = false;
                if (ok) for (int i = 0; i < n; i++) rm.set(x + i, mf - 1, Room.SPIKE);
            }
            // cofre oculto en una plataforma alta del piso superior
            for (int[] pf : platforms) if (pf[2] == mf - 4 && r.chance(0.45f)) { secrets.add(new int[]{(pf[0] + pf[1]) / 2 * Room.TS + 8, pf[2] * Room.TS}); break; }
            // candidatos para enemigos del piso superior
            for (int x = 14; x < W - 14; x++) {
                boolean ok = true;
                for (int i = -1; i <= 1; i++) if (!slab[x + i] || rm.tile(x + i, mf - 1) != Room.AIR || rm.tile(x + i, mf - 2) != Room.AIR || rm.tile(x + i, mf - 3) != Room.AIR) ok = false;
                if (ok) upCand.add(new int[]{x});
            }
        }

        // ----- decoracion -----
        // vistas al parallax
        int nv = r.range(1, 3);
        for (int k = 0; k < nv; k++) {
            int vw = r.range(8, 16), vh = r.range(6, 9);
            int vx = r.range(4, Math.max(5, W - vw - 4)), vy = r.range(3, 5);
            for (int y = vy; y < vy + vh && y < H - 2; y++) for (int x = vx; x < vx + vw && x < W - 2; x++) rm.vista[y * W + x] = true;
        }
        // antorchas
        for (int x = 8; x < W - 6; x += r.range(8, 11)) {
            int gy = ground[x] >= 0 ? ground[x] : fy;
            int y = Math.max(ceil[x] + 2, gy - 4);
            if (rm.tile(x, y) == Room.AIR) rm.deco[y * W + x] = (short) ((5 << 8) | r.i(4));
        }
        // focos
        for (int k = 0; k < 2 + W / 30; k++) {
            int x = r.range(6, W - 7);
            int gy = ground[x] >= 0 ? ground[x] : fy;
            int y = Math.max(ceil[x] + 3, gy - r.range(4, 7));
            if (rm.tile(x, y) == Room.AIR && rm.deco[y * W + x] == 0) rm.deco[y * W + x] = (short) ((6 << 8) | r.i(4));
        }
        // decoracion de pared y estandartes
        for (int k = 0; k < W / 4; k++) {
            int x = r.range(3, W - 4), y = r.range(4, fy - 3);
            if (rm.tile(x, y) == Room.AIR && rm.deco[y * W + x] == 0 && !rm.vista[y * W + x]) {
                if (r.chance(0.5f)) rm.deco[y * W + x] = (short) ((1 << 8) | r.i(4));
                else rm.deco[y * W + x] = (short) ((2 << 8) | r.i(8));
            }
        }
        // colgantes
        for (int x = 3; x < W - 3; x++) {
            if (ceil[x] >= 0 && rm.tile(x, ceil[x]) == Room.AIR && rm.deco[ceil[x] * W + x] == 0 && r.chance(0.09f))
                rm.deco[ceil[x] * W + x] = (short) ((3 << 8) | r.i(8));
        }
        // props de suelo
        for (int x = 4; x < W - 4; x++) {
            if (ground[x] > 1 && !blocked[x] && rm.tile(x, ground[x] - 1) == Room.AIR && rm.deco[(ground[x] - 1) * W + x] == 0 && r.chance(0.13f))
                rm.deco[(ground[x] - 1) * W + x] = (short) ((4 << 8) | r.i(16));
        }

        // ----- puntos de aparicion y salidas -----
        rm.spawnX = 4 * Room.TS + 8;
        rm.spawnY = fy * Room.TS;
        rm.exitX = (W - 6) * Room.TS;
        rm.exitY = fy * Room.TS;
        // la zona de entrada y de salida no tienen decoracion de suelo estorbosa
        for (int x = 2; x < 9; x++) rm.deco[(fy - 1) * W + x] = 0;

        if (type == Room.COMBAT || type == Room.ELITE) spawnEnemies(rm, ground, blocked, platforms, r, stage, roomNo, type == Room.ELITE, upCand, mf);
        if (boss) {
            rm.spawnX = 5 * Room.TS;
            rm.exitX = (W - 5) * Room.TS;
        }
        placeProps(rm, type, fy, r);
        if (big) for (int[] sc : secrets) rm.props.add(new Room.PropSpec("chest", sc[0], sc[1], 3));
        return rm;
    }

    /** Piso superior: losa con huecos-escalera (pozos con plataformas) y plataformas altas. */
    private static void buildUpper(Room rm, int W, int fy, int mf, int[] ground, int[] ceil, boolean[] blocked, boolean[] slab, List<int[]> plat, Rng r) {
        for (int x = 10; x < W - 10; x++) slab[x] = true;
        List<Integer> shafts = new ArrayList<>();
        int want = W >= 90 ? 3 : 2;
        int[] starts = {r.range(12, 16), (W / 2) + r.range(-8, 8), W - r.range(18, 22)};
        for (int k = 0; k < want; k++) {
            int sx = starts[k == 0 ? 0 : (k == 1 && want == 3 ? 1 : 2)];
            int found = -1;
            for (int d = 0; d < 14 && found < 0; d++) for (int sg = -1; sg <= 1 && found < 0; sg += 2) {
                int x = sx + d * sg;
                if (x < 11 || x + 3 >= W - 11) continue;
                boolean ok = true;
                for (int i = -2; i <= 5; i++) { int xx = x + i; if (xx < 2 || xx >= W - 2 || ground[xx] < 0 || blocked[xx] || ceil[xx] > 2) ok = false; }
                for (int sh : shafts) if (Math.abs(sh - x) < 12) ok = false;
                if (ok) found = x;
            }
            if (found >= 0) shafts.add(found);
        }
        if (shafts.isEmpty()) {   // ultimo recurso: pozo en la zona de entrada
            shafts.add(11);
        }
        for (int sx : shafts) {
            int gmin = 99;
            for (int i = 0; i < 4; i++) gmin = Math.min(gmin, ground[sx + i] >= 0 ? ground[sx + i] : fy);
            for (int i = 0; i < 4; i++) slab[sx + i] = false;
            int k = 0;
            for (int row = gmin - 3; row > mf; row -= 3, k++) {
                int px = sx + (k % 2 == 0 ? 0 : 1);
                plat.add(new int[]{px, px + 2, row});
            }
        }
        // plataformas elevadas del piso superior
        int np = r.range(2, 4);
        for (int k = 0; k < np; k++) {
            int x = r.range(18, W - 24), len = r.range(4, 6);
            boolean ok = true;
            for (int i = -2; i < len + 2; i++) if (!slab[x + i]) ok = false;
            if (ok) plat.add(new int[]{x, x + len - 1, mf - 4});
        }
    }

    /** Camara oculta bajo el suelo (suelo agrietado) y camara tras un muro agrietado en el piso superior. */
    private static void buildSecrets(Room rm, int W, int fy, int mf, int[] ground, boolean[] blocked, boolean[] slab, Rng r, int stage) {
        // ---- A) camara bajo el suelo
        for (int tries = 0; tries < 40; tries++) {
            int x0 = r.range(16, W - 22);
            boolean ok = true;
            for (int i = -6; i <= 7 && ok; i++) { int xx = x0 + i; if (ground[xx] != fy || blocked[xx] || rm.tile(xx, fy - 1) != Room.AIR) ok = false; }
            if (!ok) continue;
            for (int x = x0 - 3; x <= x0 + 4; x++) for (int y = fy + 2; y <= fy + 5; y++) rm.set(x, y, Room.AIR);
            for (int x = x0 - 4; x <= x0 + 5; x++) rm.set(x, fy + 6, Room.SOLID);
            rm.set(x0, fy, Room.BREAK); rm.set(x0 + 1, fy, Room.BREAK);
            rm.set(x0, fy + 1, Room.BREAK); rm.set(x0 + 1, fy + 1, Room.BREAK);
            for (int x = x0 + 2; x <= x0 + 4; x++) rm.set(x, fy + 4, Room.ONEWAY);
            rm.secretSpots.add(new int[]{(x0 - 1) * Room.TS + 8, (fy + 6) * Room.TS});
            for (int x = x0 - 3; x <= x0 + 4; x++) for (int y = fy + 2; y <= fy + 5; y++) rm.vista[y * W + x] = false;
            break;
        }
        // ---- B) camara de piedra con muro agrietado sobre el piso superior
        for (int tries = 0; tries < 40; tries++) {
            int a = r.range(16, W - 28);
            boolean ok = true;
            for (int i = -3; i <= 11 && ok; i++) { int xx = a + i; if (xx < 0 || xx >= W || !slab[xx] || rm.tile(xx, mf - 1) != Room.AIR) ok = false; }
            if (!ok) continue;
            boolean left = r.chance(0.5f);
            for (int x = a; x <= a + 8; x++) for (int y = mf - 5; y <= mf - 1; y++) rm.set(x, y, Room.SOLID);
            for (int x = a + 1; x <= a + 7; x++) for (int y = mf - 3; y <= mf - 1; y++) rm.set(x, y, Room.AIR);
            int bx = left ? a : a + 8;
            rm.set(bx, mf - 3, Room.SOLID);
            for (int y = mf - 2; y <= mf - 1; y++) rm.set(bx, y, Room.DOOR);
            rm.secretSpots.add(new int[]{(a + 4) * Room.TS + 8, mf * Room.TS});
            for (int x = a; x <= a + 8; x++) for (int y = mf - 5; y <= mf - 1; y++) rm.vista[y * W + x] = false;
            break;
        }
    }

    private static void layout(int W, int fy, int[] ground, int[] ceil, boolean[] blocked, List<int[]> plat, Rng r, Room rm) {
        int x = 12, cur = fy;
        boolean afterPit = false;
        int safety = 0;
        while (x < W - 14 && safety++ < 60) {
            int pick = afterPit ? 0 : r.i(100);
            int len;
            if (pick < 26) { // plano con plataformas
                len = r.range(8, 14);
                len = Math.min(len, W - 14 - x);
                set(ground, x, len, cur);
                if (r.chance(0.75f) && len >= 6) {
                    int s = x + r.range(1, Math.max(1, len - 6));
                    int pl = r.range(4, 7);
                    plat.add(new int[]{s, Math.min(s + pl, x + len - 1), cur - 3});
                    if (len >= 10 && r.chance(0.5f)) plat.add(new int[]{s + 1, Math.min(s + 4, x + len - 1), cur - 6});
                }
            } else if (pick < 42) { // escalones
                int d = r.chance(0.5f) ? (r.chance(0.5f) ? 1 : 2) : (r.chance(0.5f) ? -1 : -2);
                int nc = Mth.clamp(cur + d, fy - 4, fy);
                len = Math.min(r.range(5, 9), W - 14 - x);
                cur = nc;
                set(ground, x, len, cur);
            } else if (pick < 55) { // foso
                len = r.range(3, 4);
                if (x + len + 6 >= W - 14) { len = Math.min(len, 0); }
                if (len > 0) {
                    for (int k = 0; k < len; k++) ground[x + k] = -1;
                    if (r.chance(0.4f)) plat.add(new int[]{x - 1, x + len, cur - 3});
                    afterPit = true;
                    x += len;
                    continue;
                }
                len = 4;
                set(ground, x, len, cur);
            } else if (pick < 68) { // pilares
                len = Math.min(r.range(9, 13), W - 14 - x);
                set(ground, x, len, cur);
                int np = r.range(1, 2);
                for (int k = 0; k < np; k++) {
                    int px = x + 2 + k * 5 + r.i(2);
                    if (px < x + len - 2) { blocked[px] = true; if (px + 1 < x + len - 1) blocked[px + 1] = true; }
                }
            } else if (pick < 79) { // techo bajo
                len = Math.min(r.range(8, 11), W - 14 - x);
                set(ground, x, len, cur);
                if (rm.h < 24) for (int k = 0; k < len; k++) ceil[x + k] = Math.max(2, cur - 5);
            } else if (pick < 90) { // meseta elevada
                len = Math.min(r.range(10, 14), W - 14 - x);
                int up = Mth.clamp(cur - 2, fy - 4, fy);
                set(ground, x, 3, Mth.clamp(cur - 1, fy - 4, fy));
                set(ground, x + 3, len - 6, up);
                set(ground, x + len - 3, 3, Mth.clamp(cur - 1, fy - 4, fy));
                cur = Mth.clamp(cur - 1, fy - 4, fy);
                if (len >= 8) plat.add(new int[]{x + 3, x + len - 4, up - 3});
            } else {
                len = Math.min(r.range(6, 10), W - 14 - x);
                set(ground, x, len, cur);
            }
            if (len <= 0) break;
            afterPit = false;
            x += len;
        }
        // zona de salida plana a la altura base
        for (int k = x; k < W; k++) ground[k] = fy;
        for (int k = x; k < Math.min(W, x + 1); k++) ground[k] = Mth.clamp(cur, fy - 4, fy);
        // las alturas distintas se conectan con escalones
        for (int k = 1; k < W; k++) {
            if (ground[k] >= 0 && ground[k - 1] >= 0 && Math.abs(ground[k] - ground[k - 1]) > 2) ground[k - 1] = (ground[k] + ground[k - 1]) / 2;
        }
    }

    private static void set(int[] g, int x, int len, int v) {
        for (int k = 0; k < len && x + k < g.length; k++) g[x + k] = v;
    }

    private static void spawnEnemies(Room rm, int[] ground, boolean[] blocked, List<int[]> plat, Rng r, int stage, int roomNo, boolean elite, List<int[]> upCand, int mf) {
        int W = rm.w;
        int count = 3 + stage + (roomNo >= 2 ? 1 : 0) + r.i(2);
        if (elite) count = 2 + stage;
        String[] pool = rm.biome.enemies;
        List<Integer> cand = new ArrayList<>();
        for (int x = 14; x < W - 14; x++) if (ground[x] >= 0 && !blocked[x] && ground[x] == (x > 0 ? ground[x - 1] : -2) && (x + 1 < W && ground[x + 1] == ground[x])) cand.add(x);
        int heavies = 0;
        List<Integer> used = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            String id = pool[r.i(pool.length)];
            EnemyDef d = EnemyDef.get(id);
            if (d == null) continue;
            if ((d.role == EnemyDef.HEAVY || d.role == EnemyDef.CHARGER) && heavies >= (stage >= 1 ? 2 : 1)) { id = pool[r.i(2)]; d = EnemyDef.get(id); if (d == null) continue; }
            if (d.role == EnemyDef.HEAVY || d.role == EnemyDef.CHARGER) heavies++;
            float sx, sy;
            boolean flyer = d.role == EnemyDef.FLY_SHOOT || d.role == EnemyDef.FLY_DIVE;
            if (flyer) {
                int x = r.range(16, W - 16);
                int gy = ground[x] >= 0 ? ground[x] : (rm.h > 24 ? 22 : rm.h - 4);
                sx = x * Room.TS; sy = (gy - r.range(4, 7)) * Room.TS;
            } else {
                if (cand.isEmpty()) continue;
                int x = cand.get(r.i(cand.size()));
                for (int tries = 0; tries < 8; tries++) {
                    boolean ok = true;
                    for (int u : used) if (Math.abs(u - x) < 4) ok = false;
                    if (ok) break;
                    x = cand.get(r.i(cand.size()));
                }
                used.add(x);
                sx = x * Room.TS + 8; sy = ground[x] * Room.TS;
                if (!upCand.isEmpty() && r.chance(0.38f)) { int[] u = upCand.get(r.i(upCand.size())); sx = u[0] * Room.TS + 8; sy = mf * Room.TS; }
                // los de rango a veces en plataformas
                if ((d.role == EnemyDef.RANGED || d.role == EnemyDef.CASTER) && !plat.isEmpty() && r.chance(0.5f)) {
                    int[] p = plat.get(r.i(plat.size()));
                    if (p[0] > 12 && p[1] < W - 12) { sx = (p[0] + p[1]) / 2f * Room.TS + 8; sy = p[2] * Room.TS; }
                }
            }
            rm.spawns.add(new Room.Spawn(id, sx, sy, elite && i == 0));
        }
    }

    private static void placeProps(Room rm, int type, int fy, Rng r) {
        float cx = rm.w / 2f * Room.TS, gy = fy * Room.TS;
        switch (type) {
            case Room.BLESSING -> rm.props.add(new Room.PropSpec("altar", cx, gy, 0));
            case Room.FORGE -> rm.props.add(new Room.PropSpec("forge", cx, gy, 0));
            case Room.SHOP -> rm.props.add(new Room.PropSpec("merchant", cx, gy, 0));
            case Room.FOUNTAIN -> rm.props.add(new Room.PropSpec("fountain", cx, gy, 0));
            case Room.TREASURE -> {
                rm.props.add(new Room.PropSpec("chest", cx - 40, gy, 0));
                rm.props.add(new Room.PropSpec("chest", cx + 40, gy, 1));
            }
            case Room.REST -> {
                rm.props.add(new Room.PropSpec("fountain", cx - 70, gy, 0));
                rm.props.add(new Room.PropSpec("forge", cx + 70, gy, 0));
                rm.props.add(new Room.PropSpec("altar", cx, gy, 1));
            }
            default -> { }
        }
        // vasijas rompibles
        if (type == Room.COMBAT || type == Room.ELITE || type == Room.START) {
            int n = r.range(2, 5);
            for (int i = 0; i < n; i++) {
                int x = r.range(10, rm.w - 12);
                if (rm.ground != null && rm.ground[x] > 0 && rm.tile(x, rm.ground[x] - 1) == Room.AIR)
                    rm.props.add(new Room.PropSpec("pot", x * Room.TS + 8, rm.ground[x] * Room.TS, 0));
            }
        }
    }
}
