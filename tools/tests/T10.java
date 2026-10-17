package com.julianfarks.roguelike.core;

import java.util.*;

/** Etapa 2: preparacion de expedicion (seleccion valida, bendiciones iniciales con ventajas y contrapartidas). */
public class T10 {
    static int f = 0;
    static void ck(String n, boolean ok) { System.out.println((ok ? "ok   " : "FAIL ") + n); if (!ok) f++; }

    public static void main(String[] a) {
        Platform p = T8.plat();
        T8.disk.clear(); T8.reload(p);
        // ---- seleccion de espadachin: nunca uno bloqueado
        boolean[] u = new boolean[10];
        u[0] = true;
        ck("solo uno desbloqueado: se queda", PrepScreen.nextUnlocked(0, 1, u) == 0 && PrepScreen.nextUnlocked(0, -1, u) == 0);
        u[3] = true; u[9] = true;
        ck("salta bloqueados hacia delante", PrepScreen.nextUnlocked(0, 1, u) == 3 && PrepScreen.nextUnlocked(3, 1, u) == 9);
        ck("salta bloqueados hacia atras", PrepScreen.nextUnlocked(0, -1, u) == 9 && PrepScreen.nextUnlocked(3, -1, u) == 0);
        boolean never = true;
        for (int c = 0; c < 10; c++) if (u[c]) for (int d = -1; d <= 1; d += 2) if (!u[PrepScreen.nextUnlocked(c, d, u)]) never = false;
        ck("nunca devuelve un bloqueado", never);
        // ---- bendiciones iniciales
        Rng r = new Rng(123);
        boolean distinct = true, inRange = true;
        for (int i = 0; i < 400; i++) {
            int[] o = StartBlessing.roll(r);
            if (o.length != 3 || o[0] == o[1] || o[1] == o[2] || o[0] == o[2]) distinct = false;
            for (int v : o) if (StartBlessing.get(v) == null) inRange = false;
        }
        ck("siempre 3 opciones distintas", distinct);
        ck("opciones validas", inRange);
        Set<Integer> seen = new HashSet<>();
        for (int i = 0; i < 400; i++) for (int v : StartBlessing.roll(r)) seen.add(v);
        ck("todas las bendiciones pueden salir", seen.size() == StartBlessing.ALL.length);
        ck("get(-1) es nulo", StartBlessing.get(-1) == null && StartBlessing.get(99) == null);
        // cada bendicion: algo mejora y algo empeora (ventaja y desventaja), sobre todas las clases
        for (ClassDef c : ClassDef.ALL) {
            RunState base = new RunState(c, 1, 0);
            for (StartBlessing b : StartBlessing.ALL) {
                RunState x = new RunState(c, 1, 0);
                x.applyStartBlessing(b.id);
                Stats s0 = base.stats, s1 = x.stats;
                boolean better = s1.dmgMul > s0.dmgMul + 1e-4 || s1.maxHp > s0.maxHp + 1e-4 || s1.speedMul > s0.speedMul + 1e-4 || s1.dmgTaken < s0.dmgTaken - 1e-4
                        || s1.critChance > s0.critChance + 1e-4 || s1.soulMul > s0.soulMul + 1e-4 || s1.cdMul < s0.cdMul - 1e-4 || s1.potionsMax > s0.potionsMax || x.gold > base.gold;
                boolean worse = s1.dmgMul < s0.dmgMul - 1e-4 || s1.maxHp < s0.maxHp - 1e-4 || s1.speedMul < s0.speedMul - 1e-4 || s1.dmgTaken > s0.dmgTaken + 1e-4
                        || s1.potionsMax < s0.potionsMax || s1.goldMul < s0.goldMul - 1e-4;
                if (!(better && worse)) { ck("bendicion " + b.name + " (" + c.key + ") tiene ventaja y contrapartida", false); }
                if (x.hp > s1.maxHp + 1e-3 || x.hp <= 0) ck("vida inicial valida con " + b.name, false);
                if (x.potions > s1.potionsMax) ck("pociones validas con " + b.name, false);
                float net = (s1.dmgMul / s0.dmgMul) * (s1.maxHp / s0.maxHp) * (s1.speedMul / s0.speedMul) / (s1.dmgTaken / s0.dmgTaken);
                if (net > 1.15f || net < 0.85f) ck("bendicion " + b.name + " equilibrada (neto " + net + ")", false);
            }
        }
        ck("ventaja/contrapartida/equilibrio revisados en las 10 clases", f == 0);
        // la bendicion persiste al recalcular (altares, cofres...)
        RunState x = new RunState(ClassDef.ALL[0], 5, 0);
        float h0 = x.stats.maxHp;
        x.applyStartBlessing(0);
        float h1 = x.stats.maxHp;
        x.recalc();
        ck("recalc conserva la bendicion", Math.abs(x.stats.maxHp - h1) < 1e-4 && h1 < h0);
        // bolsa pesada: oro inicial y una pocion menos
        RunState y = new RunState(ClassDef.ALL[0], 5, 0);
        int g0 = y.gold, p0 = y.potions;
        y.applyStartBlessing(3);
        ck("Bolsa Pesada: +60 oro y -1 pocion", y.gold == g0 + 60 && y.potions == p0 - 1);
        // id invalido no hace nada
        RunState z = new RunState(ClassDef.ALL[0], 5, 0);
        float zh = z.stats.maxHp;
        z.applyStartBlessing(-1); z.applyStartBlessing(42);
        ck("id invalido ignorado", z.startBless == -1 && z.stats.maxHp == zh);
        // solo aplica una vez por run: reaplicar no acumula
        RunState w = new RunState(ClassDef.ALL[0], 5, 0);
        w.applyStartBlessing(0); float wh = w.stats.maxHp; w.applyStartBlessing(0);
        ck("reaplicar no acumula", Math.abs(w.stats.maxHp - wh) < 1e-4);
        System.out.println(f == 0 ? "T10 OK" : "T10 FALLOS=" + f);
        if (f > 0) System.exit(1);
    }
}
