package com.julianfarks.roguelike.core;

import java.util.*;

/** Camaras secretas: genera muchas salas por bioma y comprueba las invariantes (alcanzabilidad, nada filtrado, variedad). */
public class SecretGenTest {
    static int fails = 0;
    static void fail(String m) { fails++; if (fails < 40) System.out.println("FAIL " + m); }

    public static void main(String[] a) {
        int per = a.length > 0 ? Integer.parseInt(a[0]) : 120;
        int[] ent = new int[Secret.E_COUNT], rew = new int[Secret.R_COUNT], chal = new int[3], fam = new int[2];
        int rooms = 0, withSecret = 0;
        Map<String, Integer> byBiome = new TreeMap<>();
        for (Biome b : Biome.ALL) {
            for (int i = 0; i < per; i++) {
                Rng r = new Rng(1000L * b.id + i * 7919L + 5);
                int stage = Math.min(3, b.id);
                Room rm = RoomGen.generate(i % 5 == 0 ? Room.ELITE : Room.COMBAT, b, r, stage, 3 + i % 6);
                rooms++;
                if (rm.secrets.isEmpty()) continue;
                withSecret += rm.secrets.size();
                byBiome.merge(b.key, rm.secrets.size(), Integer::sum);
                int sx = (int) (rm.spawnX / Room.TS), sg = Math.round(rm.spawnY / Room.TS);
                int ex = (int) (rm.exitX / Room.TS), eg = Math.round(rm.exitY / Room.TS);
                Set<Integer> closed = RoomCheck.reach(rm, sx, sg);
                if (!closed.contains(eg * 1000 + ex)) fail(b.key + "#" + i + " salida inalcanzable con camara cerrada");
                for (Secret s : rm.secrets) {
                    String id = b.key + "#" + i + " " + Secret.E_NAME[s.entrance] + "/" + Secret.R_NAME[s.reward] + "/ch" + s.challenge;
                    ent[s.entrance]++; rew[s.reward]++; chal[s.challenge]++; fam[s.family]++;
                    if (s.contains(sx, sg) || s.contains(ex, eg)) fail(id + " recuadro sobre entrada/salida");
                    for (Room.Spawn sp : rm.spawns) if (s.contains((int) (sp.x / 16), (int) ((sp.y - 1) / 16))) fail(id + " enemigo dentro");
                    int hid = 0;
                    for (Room.PropSpec p : rm.props) {
                        boolean in = s.contains((int) (p.x / 16), (int) ((p.y - 1) / 16));
                        boolean isRw = Math.abs(p.x - s.rwX) < 1 && Math.abs(p.y - s.rwY) < 1;
                        if (in && !isRw) fail(id + " prop ajeno dentro: " + p.kind);
                        if (isRw) hid++;
                    }
                    boolean prop = s.reward <= Secret.R_RELIC || s.reward == Secret.R_SHRINE;
                    if (prop && hid != 1) fail(id + " recompensa sin prop (" + hid + ")");
                    // abrir: entrada libre
                    byte[] save = rm.t.clone();
                    for (int[] d : s.door) rm.set(d[0], d[1], Room.AIR);
                    Set<Integer> open = RoomCheck.reach(rm, sx, sg);
                    int rgx = (int) (s.rwX / 16), rgy = Math.round(s.rwY / 16);
                    if (!open.contains(eg * 1000 + ex)) fail(id + " salida inalcanzable con camara abierta");
                    if (prop && !open.contains(rgy * 1000 + rgx)) fail(id + " recompensa inalcanzable");
                    if (!prop && !open.contains(rgy * 1000 + rgx) && s.reward != Secret.R_TREASURE) { /* sin prop: basta el hueco */ }
                    // interruptores y cristal alcanzables sin abrir
                    for (float[] w : s.sw) if (!closed.contains(Math.round(w[1] / 16) * 1000 + (int) (w[0] / 16))) fail(id + " interruptor inalcanzable");
                    if (s.entrance == Secret.E_SKILL && !closed.contains(Math.round(s.crY / 16) * 1000 + (int) (s.crX / 16))) fail(id + " cristal inalcanzable");
                    // volver a salir
                    Set<Integer> back = RoomCheck.reach(rm, rgx, rgy);
                    boolean out = false;
                    for (int[] d : s.door) for (int k = -4; k <= 4 && !out; k++) if (back.contains(closedGround(rm, d[0] + k) * 1000 + d[0] + k)) out = true;
                    if (prop && !out) fail(id + " no se puede salir de la camara");
                    System.arraycopy(save, 0, rm.t, 0, save.length);
                    // cerrada: sin entrada practicable a la recompensa (salvo paredes que se atraviesan)
                    boolean walk = s.entrance == Secret.E_ILLUSION || s.entrance == Secret.E_WATERFALL || s.entrance == Secret.E_CURTAIN;
                    if (!walk && prop && airConnected(rm, sx, sg - 1, rgx, rgy - 1)) fail(id + " recompensa accesible sin abrir");
                    if (s.entrance == Secret.E_SYMBOLS && (s.order == null || s.sw.size() != 3)) fail(id + " simbolos mal formados");
                    if (s.entrance == Secret.E_RUNES && (s.order == null || s.sw.size() != 3)) fail(id + " runas mal formadas");
                    if (s.entrance == Secret.E_LEVER && s.sw.size() != 1) fail(id + " palanca mal formada");
                }
            }
        }
        System.out.println("salas=" + rooms + " camaras=" + withSecret + " (" + String.format("%.1f", 100f * withSecret / rooms) + "% de salas)");
        System.out.println("familia " + Arrays.toString(fam) + "  retos(0 nada,1 plat,2 guardian) " + Arrays.toString(chal));
        System.out.println("entradas " + Arrays.toString(ent));
        System.out.println("recompensas " + Arrays.toString(rew));
        System.out.println("por bioma " + byBiome);
        System.out.println(fails == 0 ? "SECRETGEN OK" : "SECRETGEN FALLOS=" + fails);
        System.exit(fails == 0 ? 0 : 1);
    }

    static boolean free(Room r, int x, int y) { int t = r.tile(x, y); return x >= 0 && y >= 0 && x < r.w && y < r.h && t != Room.SOLID && t != Room.BREAK && t != Room.DOOR && t != Room.HWALL; }
    /** Inundacion 4-conexa por baldosas libres (sin saltar): la camara cerrada no debe quedar conectada al resto del aire. */
    static boolean airConnected(Room r, int sx, int sy, int tx, int ty) {
        boolean[] seen = new boolean[r.w * r.h]; ArrayDeque<int[]> q = new ArrayDeque<>();
        q.add(new int[]{sx, sy}); seen[sy * r.w + sx] = true;
        while (!q.isEmpty()) { int[] c = q.poll(); if (c[0] == tx && c[1] == ty) return true;
            int[][] d = {{1,0},{-1,0},{0,1},{0,-1}};
            for (int[] e : d) { int nx = c[0] + e[0], ny = c[1] + e[1]; if (free(r, nx, ny) && !seen[ny * r.w + nx]) { seen[ny * r.w + nx] = true; q.add(new int[]{nx, ny}); } } }
        return false;
    }

    static int closedGround(Room rm, int x) { return rm.ground != null && x >= 0 && x < rm.ground.length ? rm.ground[x] : 0; }
}
