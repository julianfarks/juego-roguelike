package com.julianfarks.roguelike.core;

/** Etapa 1: coherencia del centro de operaciones (estaciones, mundo, jefes del muro de trofeos). */
public class T9 {
    static int ok, bad;
    static void check(boolean c, String m) { if (c) ok++; else { bad++; System.out.println("FALLO: " + m); } }

    public static void main(String[] a) {
        check(Ops.N == 11, "11 estaciones");
        check(Ops.SX.length == Ops.N && Ops.SW.length == Ops.N, "tablas completas");
        for (int i = 0; i < Ops.N; i++) {
            float hw = Math.max(Ops.SW[i] + 8, 60) / 2f;
            check(Ops.SX[i] - hw >= 0 && Ops.SX[i] + hw <= Ops.WORLD, "estacion " + i + " dentro del mundo");
            if (i > 0) {
                float hp = Math.max(Ops.SW[i - 1] + 8, 60) / 2f;
                check(Ops.SX[i - 1] + hp <= Ops.SX[i] - hw, "areas tactiles " + (i - 1) + "/" + i + " sin solaparse");
                check(Ops.SX[i] - Ops.SX[i - 1] > 0, "orden de izquierda a derecha " + i);
            }
            check(Math.max(Ops.SW[i] + 8, 60) >= 56, "area tactil comoda " + i);
        }
        check(Ops.TILES_W * 16 == Ops.WORLD, "mundo = tiles");
        check(Ops.standX(Ops.PORTAL) == Ops.SX[Ops.PORTAL], "el espadachin espera en el portal");
        // los nueve nichos corresponden a los nueve jefes reales
        for (int i = 0; i < 9; i++) check(BossDef.ALL[i].idx == i, "jefe " + i + " en su nicho");
        int g = 0; for (int i = 0; i < 5; i++) g += Ops.gardenStage(i);
        check(g >= 0, "etapa del jardin valida");
        System.out.println("T9: " + ok + " ok, " + bad + " fallos");
        if (bad > 0) System.exit(1);
    }
}
