package com.julianfarks.roguelike.core;

import java.util.*;

/**
 * Validacion y reparacion de salas generadas. Modelo de movimiento conservador con la fisica real del jugador
 * (salto 410 -> ~3.5 baldosas, doble salto hasta ~5, caminar 135 px/s): una sala solo se acepta si la salida
 * y todos los enemigos terrestres son alcanzables desde la entrada. Las plataformas inalcanzables se eliminan
 * y los enemigos mal colocados se recolocan en baldosas alcanzables.
 */
final class RoomCheck {
    private RoomCheck() {}

    static boolean clear(Room r, int x, int y) { int t = r.tile(x, y); return !(x < 0 || x >= r.w) && t != Room.SOLID && t != Room.BREAK && t != Room.DOOR && t != Room.HWALL; }
    static boolean support(Room r, int x, int g) { int t = r.tile(x, g); return t == Room.SOLID || t == Room.ONEWAY || t == Room.BREAK || t == Room.HWALL || t == Room.FAKE; }

    /** Casilla donde un jugador puede estar de pie: apoyo debajo, dos baldosas libres encima y sin pinchos en los pies. */
    static boolean node(Room r, int x, int g) {
        if (x < 1 || x >= r.w - 1 || g < 2 || g >= r.h) return false;
        if (!support(r, x, g)) return false;
        int a = r.tile(x, g - 1), b = r.tile(x, g - 2);
        if (a == Room.SOLID || a == Room.BREAK || a == Room.DOOR || a == Room.HWALL || a == Room.SPIKE || a == Room.SPIKE_DOWN) return false;
        if (b == Room.SOLID || b == Room.BREAK || b == Room.DOOR || b == Room.HWALL) return false;
        return true;
    }

    static Set<Integer> reach(Room r, int sx, int sg) { return r.tall ? reachTall(r, sx, sg, null) : reachOld(r, sx, sg); }

    // ------------------------------------------------------------------ modelo estricto para salas con varias alturas
    /** Celda libre para el cuerpo (los pinchos y las plataformas de un solo sentido no bloquean el salto). */
    private static boolean air(Room r, int x, int y) { return clear(r, x, y); }
    /** Celda libre y sin pinchos (para recorridos de caida). */
    private static boolean airSafe(Room r, int x, int y) { int t = r.tile(x, y); return clear(r, x, y) && t != Room.SPIKE && t != Room.SPIKE_DOWN; }

    /**
     * Alcanzabilidad con saltos Y caidas reales: a diferencia de reachOld, un salto hacia arriba necesita aire sobre el punto de partida (no se atraviesa
     * un techo) y una caida necesita el pasillo de salida libre y la columna de aterrizaje libre (no se cae a traves de la roca). Los mismos limites
     * de salto que reachOld (salto 410 -> ~3.5 baldosas, doble salto ~5, caminar 135 px/s). `parent` (opcional) recibe, por cada casilla, la de la que se llega.
     */
    static Set<Integer> reachTall(Room r, int sx, int sg, Map<Integer, Integer> parent) {
        Set<Integer> seen = new HashSet<>(); ArrayDeque<int[]> q = new ArrayDeque<>();
        if (!node(r, sx, sg)) return seen;
        seen.add(sg * 1000 + sx); q.add(new int[]{sx, sg});
        while (!q.isEmpty()) {
            int[] c = q.poll(); int x = c[0], g = c[1];
            for (int nx = Math.max(1, x - 6); nx <= Math.min(r.w - 2, x + 6); nx++) {
                int dx = Math.abs(nx - x);
                if (dx == 0) continue;
                int lo = Math.min(x, nx), hi = Math.max(x, nx);
                // ---- hacia arriba (o al mismo nivel): salto
                for (int ng = Math.max(2, g - 5); ng <= g; ng++) {
                    int up = g - ng;
                    boolean ok = up == 0 ? dx <= 4 : (up <= 3 ? dx <= 4 : dx <= 2);
                    if (!ok || seen.contains(ng * 1000 + nx) || !node(r, nx, ng)) continue;
                    int top = ng - 2 - (up > 3 ? 1 : 0);
                    boolean free = true;
                    for (int xx = lo; xx <= hi && free; xx++) for (int yy = top; yy <= ng - 1; yy++) if (!air(r, xx, yy)) { free = false; break; }
                    if (free && up > 0) for (int yy = ng - 1; yy <= g - 1 && free; yy++) if (!air(r, x, yy)) free = false;      // aire sobre el punto de partida
                    if (!free) continue;
                    seen.add(ng * 1000 + nx); q.add(new int[]{nx, ng}); if (parent != null) parent.put(ng * 1000 + nx, g * 1000 + x);
                }
                // ---- hacia abajo: salir andando/saltando y caer por la columna de aterrizaje
                if (dx > 5) continue;
                boolean out = true;
                for (int xx = lo; xx <= hi && out; xx++) for (int yy = g - 2; yy <= g - 1; yy++) if (!air(r, xx, yy)) { out = false; break; }
                if (!out || !airSafe(r, nx, g)) continue;
                for (int ng = g + 1; ng < r.h; ng++) {
                    if (node(r, nx, ng) && !seen.contains(ng * 1000 + nx)) {
                        seen.add(ng * 1000 + nx); q.add(new int[]{nx, ng}); if (parent != null) parent.put(ng * 1000 + nx, g * 1000 + x);
                    }
                    int t = r.tile(nx, ng);
                    if (!airSafe(r, nx, ng) && t != Room.ONEWAY) break;    // la roca o los pinchos cortan la caida (las plataformas de un solo sentido se atraviesan al bajar)
                }
            }
        }
        return seen;
    }

    static Set<Integer> reachOld(Room r, int sx, int sg) {
        Set<Integer> seen = new HashSet<>(); ArrayDeque<int[]> q = new ArrayDeque<>();
        seen.add(sg * 1000 + sx); q.add(new int[]{sx, sg});
        while (!q.isEmpty()) {
            int[] c = q.poll(); int x = c[0], g = c[1];
            for (int nx = x - 6; nx <= x + 6; nx++) {
                int dx = Math.abs(nx - x);
                if (dx == 0) continue;
                for (int ng = Math.max(2, g - 5); ng < r.h; ng++) {
                    if (seen.contains(ng * 1000 + nx) || !node(r, nx, ng)) continue;
                    int up = g - ng;
                    boolean ok;
                    if (up <= 0) ok = dx <= (up == 0 ? 4 : 5);
                    else if (up <= 3) ok = dx <= 4;
                    else ok = dx <= 2;
                    if (!ok) continue;
                    int top = Math.min(g, ng) - 2 - (up > 3 ? 1 : 0);
                    boolean free = true;
                    for (int xx = Math.min(x, nx); xx <= Math.max(x, nx) && free; xx++) for (int yy = top; yy <= Math.min(g, ng) - 1; yy++) if (!clear(r, xx, yy)) { free = false; break; }
                    if (!free) continue;
                    seen.add(ng * 1000 + nx); q.add(new int[]{nx, ng});
                }
            }
        }
        return seen;
    }

    static boolean inSecret(Room r, int x, int y) { for (Secret s : r.secrets) if (s.contains(x, y)) return true; return false; }

    static boolean isFlyer(String enemy) {
        EnemyDef d = EnemyDef.get(enemy);
        if (d != null && (d.role == EnemyDef.FLY_SHOOT || d.role == EnemyDef.FLY_DIVE)) return true;
        return enemy != null && enemy.equals("ventisca");
    }

    /** Devuelve false si la sala no es jugable (el generador la descarta); si lo es, repara plataformas y enemigos. */
    static boolean fix(Room r, Rng rng) {
        int sx = (int) (r.spawnX / Room.TS), sg = Math.round(r.spawnY / Room.TS);
        int ex = (int) (r.exitX / Room.TS), eg = Math.round(r.exitY / Room.TS);
        if (!node(r, sx, sg) || !node(r, ex, eg)) return false;
        Set<Integer> rs = reach(r, sx, sg);
        if (!rs.contains(eg * 1000 + ex)) return false;
        // plataformas inaccesibles: se eliminan tramos enteros sin ninguna casilla alcanzable
        for (int y = 3; y < r.h - 2; y++) {
            int x = 2;
            while (x < r.w - 2) {
                if (r.tile(x, y) != Room.ONEWAY) { x++; continue; }
                int x0 = x; boolean any = false;
                while (x < r.w - 2 && r.tile(x, y) == Room.ONEWAY) { if (rs.contains(y * 1000 + x)) any = true; x++; }
                if (!any && !inSecret(r, x0, y)) for (int k = x0; k < x; k++) r.set(k, y, Room.AIR);   // las de una camara secreta cerrada se conservan
            }
        }
        // candidatos alcanzables para recolocar enemigos terrestres
        List<int[]> spots = new ArrayList<>();
        for (int key : rs) { int g = key / 1000, x = key % 1000; if (x > sx + 9 && x < r.w - 10 && !inSecret(r, x, g - 1) && node(r, x, g) && r.tile(x, g) == Room.SOLID && r.tile(x + 1, g) != Room.SPIKE) spots.add(new int[]{x, g}); }
        List<Room.Spawn> out = new ArrayList<>();
        for (Room.Spawn sp : r.spawns) {
            int tx = (int) (sp.x / Room.TS), ty = (int) (sp.y / Room.TS);
            if (isFlyer(sp.enemy)) {
                int bestX = -1, bestY = -1;
                for (int d = 0; d <= 8 && bestX < 0; d++)
                    for (int dy = -d; dy <= d && bestX < 0; dy++)
                        for (int dx = -2; dx <= 2 && bestX < 0; dx++) {
                            int cx = tx + dx, cy = ty + dy;
                            if (cx < 4 || cx >= r.w - 4 || cy < 4 || cy >= r.h - 4) continue;
                            boolean free = true;
                            for (int ax = -1; ax <= 1; ax++) for (int ay = -2; ay <= 1; ay++) if (!clear(r, cx + ax, cy + ay) || r.tile(cx + ax, cy + ay) == Room.SPIKE || r.tile(cx + ax, cy + ay) == Room.SPIKE_DOWN) free = false;
                            if (free) { bestX = cx; bestY = cy; }
                        }
                if (bestX >= 0) out.add(new Room.Spawn(sp.enemy, bestX * Room.TS + 8, bestY * Room.TS, sp.elite));
                continue;
            }
            if (rs.contains(ty * 1000 + tx) && node(r, tx, ty)) { out.add(sp); continue; }
            if (!spots.isEmpty()) { int[] s = spots.get(rng.i(spots.size())); out.add(new Room.Spawn(sp.enemy, s[0] * Room.TS + 8, s[1] * Room.TS, sp.elite)); }
        }
        r.spawns.clear(); r.spawns.addAll(out);
        return true;
    }
}
