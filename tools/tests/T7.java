package com.julianfarks.roguelike.core;

import java.util.*;

/** Valida mazmorras generadas: entrada->salida alcanzables, enemigos terrestres alcanzables y sobre suelo firme, sin spawns dentro de muros. */
public class T7 {
    static int up1 = 3, upDbl = 5;

    static boolean clear(Room r, int x, int y) { return r.tile(x, y) != Room.SOLID && r.tile(x, y) != Room.BREAK && r.tile(x, y) != Room.DOOR && !(x < 0 || x >= r.w); }
    static boolean support(Room r, int x, int g) { int t = r.tile(x, g); return t == Room.SOLID || t == Room.ONEWAY || t == Room.BREAK || t == Room.HWALL || t == Room.FAKE; }
    static boolean node(Room r, int x, int g) {
        if (x < 1 || x >= r.w - 1 || g < 2 || g >= r.h) return false;
        if (!support(r, x, g)) return false;
        int a = r.tile(x, g - 1), b = r.tile(x, g - 2);
        if (a == Room.SOLID || a == Room.BREAK || a == Room.DOOR || a == Room.HWALL || a == Room.SPIKE || a == Room.SPIKE_DOWN) return false;
        if (b == Room.SOLID || b == Room.BREAK || b == Room.DOOR || b == Room.HWALL) return false;
        return true;
    }

    static Set<Integer> reach(Room r, int sx, int sg) {
        Set<Integer> seen = new HashSet<>(); ArrayDeque<int[]> q = new ArrayDeque<>();
        seen.add(sg * 1000 + sx); q.add(new int[]{sx, sg});
        while (!q.isEmpty()) {
            int[] c = q.poll(); int x = c[0], g = c[1];
            for (int nx = x - 6; nx <= x + 6; nx++) {
                int dx = Math.abs(nx - x);
                if (dx == 0) continue;
                for (int ng = Math.max(2, g - upDbl); ng < r.h; ng++) {
                    if (seen.contains(ng * 1000 + nx) || !node(r, nx, ng)) continue;
                    int up = g - ng;
                    boolean ok;
                    if (up <= 0) ok = dx <= (up == 0 ? 4 : 5);                       // plano o caida
                    else if (up <= up1) ok = dx <= 4;
                    else ok = dx <= 2;                                              // doble salto
                    if (!ok) continue;
                    // hueco libre: el rectangulo entre columnas, desde 2 filas sobre el punto mas alto, debe estar libre
                    int top = Math.min(g, ng) - 2 - Math.max(0, up > up1 ? 1 : 0);
                    boolean free = true;
                    for (int xx = Math.min(x, nx); xx <= Math.max(x, nx) && free; xx++) for (int yy = top; yy <= Math.min(g, ng) - 1; yy++) { if (!clear(r, xx, yy)) { free = false; break; } }
                    // en caminata plana contigua no hace falta salto: basta que el camino este libre
                    if (!free) continue;
                    seen.add(ng * 1000 + nx); q.add(new int[]{nx, ng});
                }
            }
        }
        return seen;
    }

    static int gRow(Room r, float px, float py) { return (int) Math.round(py / Room.TS); }

    public static void main(String[] a) {
        RoomGen.extraTraps = Integer.getInteger("traps", 0);
        int fails = 0, rooms = 0, platTotal = 0, platBad = 0;
        long seed0 = a.length > 0 ? Long.parseLong(a[0]) : 1;
        int N = a.length > 1 ? Integer.parseInt(a[1]) : 40;
        Map<String, Integer> kinds = new TreeMap<>();
        for (int bi = 0; bi < 8; bi++) {
            for (int s = 0; s < N; s++) {
                Rng rng = new Rng(seed0 * 1000 + bi * 100 + s);
                int type = (s % 5 == 4) ? Room.ELITE : Room.COMBAT;
                int stage = Biome.ALL[bi].tier, rn = 1 + s % 3;
                Room r = RoomGen.generate(type, Biome.ALL[bi], rng, stage, rn);
                rooms++;
                int sg = gRow(r, r.spawnX, r.spawnY), sx = (int) (r.spawnX / Room.TS);
                int eg = gRow(r, r.exitX, r.exitY), ex = (int) (r.exitX / Room.TS);
                String tag = Biome.ALL[bi].key + "#" + s;
                if (!node(r, sx, sg)) { System.out.println("FALLO " + tag + ": la entrada no es una casilla valida (" + sx + "," + sg + ")"); fails++; continue; }
                Set<Integer> rs = reach(r, sx, sg);
                if (!rs.contains(eg * 1000 + ex)) { System.out.println("FALLO " + tag + ": salida inalcanzable"); fails++; }
                for (Room.Spawn sp : r.spawns) {
                    EnemyDef d = EnemyDef.get(sp.enemy);
                    boolean fly = RoomCheck.isFlyer(sp.enemy);
                    int tx = (int) (sp.x / Room.TS), ty = (int) (sp.y / Room.TS);
                    if (r.solid(tx, ty - 1) || r.solid(tx, ty - 2)) { System.out.println("FALLO " + tag + ": " + sp.enemy + " dentro de un muro (" + tx + "," + ty + ")"); fails++; continue; }
                    if (fly) continue;
                    int g = ty;
                    if (!rs.contains(g * 1000 + tx)) { System.out.println("FALLO " + tag + ": " + sp.enemy + " en zona inalcanzable (" + tx + "," + g + ")"); fails++; }
                }
                // plataformas: cada casilla de plataforma con hueco debe ser alcanzable
                for (int x = 2; x < r.w - 2; x++) for (int y = 3; y < r.h - 2; y++) {
                    if (r.tile(x, y) == Room.ONEWAY && node(r, x, y)) { platTotal++; if (!rs.contains(y * 1000 + x)) platBad++; }
                }
                // cofres: cuantos
                int ch = 0; for (Room.PropSpec p : r.props) if (p.kind.equals("chest")) ch++;
                kinds.merge("cofres=" + ch, 1, Integer::sum);
            }
        }
        System.out.println("salas=" + rooms + " plataformas=" + platTotal + " inalcanzables=" + platBad + " " + kinds);
        System.out.println("FALLOS=" + fails);
    }
}
