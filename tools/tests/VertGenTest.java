package com.julianfarks.roguelike.core;

import java.util.*;

/** Mazmorras verticales: genera muchas salas por bioma y comprueba alcanzabilidad, enemigos, cofres, estructura y tiempos. */
public class VertGenTest {
    static int fails = 0;
    static void fail(String m) { fails++; if (fails < 60) System.out.println("FAIL " + m); }

    public static void main(String[] a) {
        int per = a.length > 0 ? Integer.parseInt(a[0]) : 40;
        int rooms = 0, tall = 0;
        int[] archN = new int[3];
        long tMax = 0, tSum = 0;
        int[] zoneNodes = new int[7];
        int chests = 0, optSpawns = 0, vaults = 0, breakAlcoves = 0, loops = 0;
        Map<String, int[]> perBiome = new TreeMap<>();        // enemigos obligatorios / opcionales por mazmorra (3 salas)
        int dungeonMin = 999;
        for (Biome b : Biome.ALL) {
            if (b.id == 8) continue;
            for (int i = 0; i < per; i++) {
                int stage = b.tier;
                int req3 = 0, opt3 = 0;
                for (int roomNo = 0; roomNo < 3; roomNo++) {
                    Rng r = new Rng(31L * b.id + i * 7919L + roomNo * 104729L + 11);
                    long t0 = System.nanoTime();
                    Room rm = RoomGen.generate(Room.COMBAT, b, r, stage, roomNo);
                    long dt = (System.nanoTime() - t0) / 1000;
                    tSum += dt; tMax = Math.max(tMax, dt); rooms++;
                    archN[rm.arch]++;
                    int req = 0, opt = 0;
                    for (Room.Spawn sp : rm.spawns) { if (sp.optional) opt++; else req++; }
                    req3 += req; opt3 += opt; optSpawns += opt;
                    String id = b.key + "#" + i + "/" + roomNo + " " + Vertical.ARCH_NAME[rm.arch];
                    int sx = (int) (rm.spawnX / Room.TS), sg = Math.round(rm.spawnY / Room.TS);
                    int ex = (int) (rm.exitX / Room.TS), eg = Math.round(rm.exitY / Room.TS);
                    Set<Integer> rs = RoomCheck.reach(rm, sx, sg);
                    if (!rs.contains(eg * 1000 + ex)) fail(id + " salida inalcanzable");
                    for (Room.Spawn sp : rm.spawns) {
                        int tx = (int) (sp.x / 16), ty = Math.round(sp.y / 16);
                        if (RoomCheck.isFlyer(sp.enemy)) { if (!RoomCheck.clear(rm, tx, ty - 1) || rm.solid(tx, ty)) fail(id + " volador en roca " + tx + "," + ty); continue; }
                        if (!rs.contains(ty * 1000 + tx)) fail(id + " enemigo inalcanzable " + sp.enemy + " " + tx + "," + ty);
                        if (rm.tile(tx, ty - 1) == Room.SOLID || rm.tile(tx, ty - 2) == Room.SOLID) fail(id + " enemigo dentro de roca");
                        for (Secret s : rm.secrets) if (s.contains(tx, ty - 1)) fail(id + " enemigo en camara secreta");
                    }
                    if (!rm.tall) { if (req < 4) fail(id + " pocos enemigos " + req); continue; }
                    tall++;
                    // estructura prometida
                    if (rm.mf2 == 0 || rm.s1 == 0) fail(id + " falta 2º piso o subsuelo 1");
                    if (rm.arch == Vertical.A_DEEP && (rm.mf3 == 0 || rm.s2 == 0)) fail(id + " profunda sin torre o subsuelo 2");
                    if (rm.xdA == 0 || rm.xuB == 0 || rm.xuB - rm.xdA < 20) fail(id + " pozos del subsuelo mal");
                    if (rm.arch == Vertical.A_DEEP && (rm.xc == 0 || rm.xd2 == 0)) fail(id + " pozos del subsuelo 2 mal");
                    if (rm.xdA > 0 && rm.xuB > 0) loops++;
                    // niveles realmente alcanzables
                    boolean[] z = new boolean[7];
                    for (int key : rs) { int g = key / 1000; z[Vertical.zoneOf(rm, g)] = true; }
                    for (int k = 0; k < 7; k++) if (z[k]) zoneNodes[k]++;
                    if (!z[Vertical.Z_T1] || !z[Vertical.Z_T2] || !z[Vertical.Z_S1]) fail(id + " nivel sin alcanzar (T1/T2/S1)");
                    if (rm.arch == Vertical.A_DEEP && (!z[Vertical.Z_T3] || !z[Vertical.Z_S2])) fail(id + " torre o subsuelo 2 sin alcanzar");
                    // cofres alcanzables (alcoba: con el muro roto)
                    byte[] save = rm.t.clone();
                    for (int k = 0; k < rm.t.length; k++) if (rm.t[k] == Room.BREAK) rm.t[k] = Room.AIR;
                    Set<Integer> open = RoomCheck.reach(rm, sx, sg);
                    System.arraycopy(save, 0, rm.t, 0, save.length);
                    int ch = 0, arg3 = 0;
                    for (Room.PropSpec p : rm.props) if (p.kind.equals("chest")) {
                        ch++; chests++;
                        int cx = (int) (p.x / 16), cg = Math.round(p.y / 16);
                        if (p.arg == 3 && !RoomCheck.inSecret(rm, cx, cg - 1)) breakAlcoves++;
                        if (!RoomCheck.inSecret(rm, cx, cg - 1) && !open.contains(cg * 1000 + cx)) fail(id + " cofre inalcanzable arg=" + p.arg + " " + cx + "," + cg);
                    }
                    if (ch < 2) fail(id + " pocos cofres " + ch);
                    for (Secret s : rm.secrets) if (s.family == 1 && s.ry0 < rm.mf - 3) vaults++;
                    if (req < Vertical.minEnemies(rm.arch) - 2) fail(id + " pocos enemigos obligatorios " + req);
                }
                perBiome.merge(b.key, new int[]{req3, opt3, 1}, (x, y) -> new int[]{x[0] + y[0], x[1] + y[1], x[2] + 1});
                dungeonMin = Math.min(dungeonMin, req3);
                if (req3 < 15) fail(b.key + "#" + i + " mazmorra con solo " + req3 + " enemigos obligatorios (3 salas)");
            }
        }
        System.out.println("VT salas=" + rooms + " verticales=" + tall + " compactas=" + archN[0] + " altas=" + archN[1] + " profundas=" + archN[2]);
        System.out.println("VT pedidas=" + RoomGen.statWanted + " aceptadas a la primera=" + RoomGen.statFirst + " reintentos=" + RoomGen.statRetries + " caidas a compacta=" + RoomGen.statFallback);
        System.out.println("VT tiempo medio=" + (tSum / Math.max(1, rooms)) + " us, maximo=" + tMax + " us");
        System.out.println("VT niveles alcanzados (salas): suelo/T1/T2/T3/S1/S2 = " + zoneNodes[0] + "/" + zoneNodes[1] + "/" + zoneNodes[2] + "/" + zoneNodes[3] + "/" + zoneNodes[4] + "/" + zoneNodes[5]);
        System.out.println("VT cofres=" + chests + " enemigos opcionales=" + optSpawns + " camaras de torre/2º piso=" + vaults + " alcobas con muro agrietado=" + breakAlcoves + " bucles del subsuelo=" + loops);
        for (Map.Entry<String, int[]> e : perBiome.entrySet()) System.out.println("VT " + e.getKey() + ": enemigos obligatorios por mazmorra (media) = " + (e.getValue()[0] / e.getValue()[2]) + ", opcionales = " + (e.getValue()[1] / e.getValue()[2]));
        System.out.println("VT minimo de enemigos obligatorios en una mazmorra = " + dungeonMin);
        for (Map.Entry<String, Integer> e : Vertical.whyCount.entrySet()) System.out.println("VT rechazo: " + e.getKey() + " x" + e.getValue());
        System.out.println("VT FIN fallos=" + fails);
        System.exit(fails == 0 ? 0 : 1);
    }
}
