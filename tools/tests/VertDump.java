package com.julianfarks.roguelike.core;

import java.util.*;

/** Vuelca una sala vertical como texto (para revisar la geometria). Uso: VertDump bioma arq semilla */
public class VertDump {
    public static void main(String[] a) {
        Biome b = Biome.ALL[Integer.parseInt(a[0])];
        Vertical.dbgArch = Integer.parseInt(a[1]);
        long seed = Long.parseLong(a[2]);
        int tries = 0; Room rm;
        // genera hasta obtener una sala vertical aceptada
        Rng r = new Rng(seed);
        rm = RoomGen.generate(Room.COMBAT, b, r, b.tier, 1);
        System.out.println("arq=" + rm.arch + " W=" + rm.w + " H=" + rm.h + " fy=" + rm.fy + " mf=" + rm.mf + " mf2=" + rm.mf2 + " mf3=" + rm.mf3 + " s1=" + rm.s1 + " s2=" + rm.s2 + " xdA=" + rm.xdA + " xuB=" + rm.xuB + " xc=" + rm.xc + " xd2=" + rm.xd2);
        int sx = (int) (rm.spawnX / 16), sg = Math.round(rm.spawnY / 16);
        Set<Integer> rs = RoomCheck.reach(rm, sx, sg);
        char[][] g = new char[rm.h][rm.w];
        for (int y = 0; y < rm.h; y++) for (int x = 0; x < rm.w; x++) g[y][x] = ".#=^v%D?F".charAt(Math.max(0, Math.min(8, rm.tile(x, y))));
        for (int key : rs) { int y = key / 1000, x = key % 1000; if (y - 1 >= 0 && g[y - 1][x] == '.') g[y - 1][x] = ','; }
        for (Room.Spawn sp : rm.spawns) { int x = (int) (sp.x / 16), y = Math.round(sp.y / 16) - 1; if (y >= 0 && y < rm.h) g[y][x] = sp.optional ? 'o' : 'E'; }
        for (Room.PropSpec p : rm.props) if (p.kind.equals("chest")) { int x = (int) (p.x / 16), y = Math.round(p.y / 16) - 1; g[y][x] = (char) ('0' + p.arg); }
        g[sg - 1][sx] = 'S'; g[Math.round(rm.exitY / 16) - 1][(int) (rm.exitX / 16)] = 'X';
        for (int y = 0; y < rm.h; y++) System.out.println(String.format("%2d ", y) + new String(g[y]));
    }
}
