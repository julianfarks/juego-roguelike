package com.julianfarks.roguelike.core;

import java.util.*;

/** Etapa 3: habitaciones especiales (generacion, alcanzabilidad, reglas de aparicion, pactos). */
public class T11 {
    static int f = 0, checks = 0;
    static void ck(String n, boolean ok) { checks++; if (!ok) { f++; System.out.println("FAIL " + n); } }

    static boolean flat(Room rm, int a, int b, int gy) { for (int x = Math.min(a, b); x <= Math.max(a, b); x++) if (rm.ground[x] != gy) return false; return true; }

    public static void main(String[] a) {
        Platform p = T8.plat();
        T8.disk.clear(); T8.reload(p);
        // ---------------- salas de suceso: todas las combinaciones bioma x suceso x semillas
        int rooms = 0;
        for (int bi = 0; bi < 8; bi++) for (int k = 1; k < Events.COUNT; k++) for (int seed = 0; seed < 25; seed++) {
            Biome b = Biome.ALL[bi];
            Rng r = new Rng(1000L * bi + 37L * k + seed);
            int type = k == Events.TRIAL ? Room.ELITE : Room.EVENT;
            Room rm = RoomGen.generate(type, b, r, b.tier, seed % 4, k);
            rooms++;
            String id = "b" + bi + " ev" + k + " s" + seed;
            if (k == Events.TRIAL) { ck(id + " prueba = sala de elite", rm.type == Room.ELITE && !rm.spawns.isEmpty()); continue; }
            ck(id + " tipo/suceso", rm.type == Room.EVENT && rm.event == k && rm.glow != 0);
            int st = (int) (rm.spawnX / Room.TS), et = (int) (rm.exitX / Room.TS);
            int gy = rm.ground[st];
            ck(id + " suelo llano de entrada a salida", gy > 0 && rm.ground[et] == gy && flat(rm, st, et, gy));
            ck(id + " aire sobre entrada y salida", !rm.solid(st, gy - 1) && !rm.solid(et, gy - 1) && !rm.solid(st, gy - 2) && !rm.solid(et, gy - 2));
            boolean hasMain = false;
            for (Room.PropSpec ps : rm.props) {
                int tx = (int) (ps.x / Room.TS);
                if (ps.kind.equals("pot")) continue;
                ck(id + " prop " + ps.kind + " sobre suelo firme", rm.solid(tx, gy) && !rm.solid(tx, gy - 1) && rm.tile(tx, gy - 1) != Room.SPIKE);
                ck(id + " prop " + ps.kind + " dentro de la sala", ps.x > 3 * Room.TS && ps.x < (rm.w - 3) * Room.TS);
                ck(id + " prop " + ps.kind + " no tapa entrada/salida", Math.abs(ps.x - rm.spawnX) > 40 && Math.abs(ps.x - rm.exitX) > 40);
                if (ps.kind.equals("merchant") && ps.arg == 1 && k == Events.MERCHANT) hasMain = true;
                if (ps.kind.equals("spirit") && k == Events.SPIRIT) hasMain = true;
                if (ps.kind.equals("relic") && k == Events.SECRET) hasMain = true;
                if (ps.kind.equals("shrine") && k == Events.SANCTUARY) hasMain = true;
                if (ps.kind.equals("cage") && k == Events.CAPTIVE) hasMain = true;
            }
            ck(id + " tiene su objeto principal", hasMain);
            if (k == Events.CAPTIVE) {
                ck(id + " guardias 2-3", rm.spawns.size() >= 2 && rm.spawns.size() <= 3);
                for (Room.Spawn sp : rm.spawns) {
                    int sx = (int) (sp.x / Room.TS);
                    ck(id + " guardia en suelo llano y lejos de la entrada", rm.ground[sx] == gy && sx - st >= 8 && !sp.elite);
                }
            } else ck(id + " sin enemigos", rm.spawns.isEmpty());
        }
        // ---------------- puerta lateral en salas de combate: tramo transitable hasta la salida
        int withDoor = 0, total = 0;
        for (int bi = 0; bi < 8; bi++) for (int seed = 0; seed < 40; seed++) {
            Biome b = Biome.ALL[bi];
            Room rm = RoomGen.generate(Room.COMBAT, b, new Rng(7L * bi + seed * 131L), b.tier, seed % 3);
            total++;
            float[] sd = Events.sideDoor(rm);
            if (sd == null) continue;
            withDoor++;
            int et = (int) (rm.exitX / Room.TS), dt = (int) (sd[0] / Room.TS), gt = rm.ground[dt];
            String id = "bioma " + bi + " s" + seed;
            ck(id + ": la puerta lateral esta sobre el suelo", Math.abs(sd[1] - gt * Room.TS) < 1 && rm.solid(dt, gt));
            boolean walk = true, clear = true;
            for (int x = dt - 1; x <= et + 1; x++) {
                if (rm.ground[x] <= 0) walk = false;
                if (x < et + 1 && Math.abs(rm.ground[x + 1] - rm.ground[x]) > 1) walk = false;
                for (int kk = 1; kk <= 4; kk++) if (rm.tile(x, rm.ground[x] - kk) != Room.AIR) clear = false;
                if (rm.tile(x, rm.ground[x] - 1) == Room.SPIKE) clear = false;
            }
            ck(id + ": camino transitable (sin fosos ni desniveles > 1) hasta la salida", walk);
            ck(id + ": camino con aire encima y sin pinchos", clear);
            ck(id + ": puerta lateral lejos de la salida (no solapa cofres)", et - dt >= 9);
            ck(id + ": puerta lateral lejos de la entrada", dt - (int) (rm.spawnX / Room.TS) >= 4);
        }
        System.out.println("salas de suceso generadas=" + rooms + "  combate con puerta lateral posible=" + withDoor + "/" + total);
        ck("la puerta lateral cabe en la mayoria de las salas", withDoor >= total * 0.6);

        // ---------------- reglas de aparicion
        RunState rs = new RunState(ClassDef.ALL[0], 3, 0);
        rs.biome = Biome.ALL[0];
        Rng r = new Rng(99);
        int hits = 0, N = 20000; int[] cnt = new int[Events.COUNT];
        for (int i = 0; i < N; i++) { int k = Events.roll(rs, r, 1); if (k != 0) { hits++; cnt[k]++; } }
        double rate = hits / (double) N;
        ck("probabilidad por sala ~20% (real " + rate + ")", rate > 0.17 && rate < 0.23);
        for (int k = 1; k < Events.COUNT; k++) ck("el suceso " + Events.NAME[k] + " puede aparecer", cnt[k] > 0);
        rs.eventBiomeDone = true;
        boolean none = true; for (int i = 0; i < 2000; i++) if (Events.roll(rs, r, 1) != 0) none = false;
        ck("maximo un suceso por bioma", none);
        rs.eventBiomeDone = false;
        none = true; for (int i = 0; i < 2000; i++) if (Events.roll(rs, r, 4) != 0) none = false;
        ck("nunca antes del jefe (sala 4+)", none);
        RunState tst = new RunState(ClassDef.ALL[0], 3, 0); tst.markTest(); tst.biome = Biome.ALL[0];
        none = true; for (int i = 0; i < 2000; i++) if (Events.roll(tst, r, 1) != 0) none = false;
        ck("las sesiones de prueba no generan sucesos", none);
        rs.eventsThisRun[Events.SECRET] = 1;
        boolean sec = false; for (int i = 0; i < 6000; i++) if (Events.roll(rs, r, 1) == Events.SECRET) sec = true;
        ck("una sola camara secreta por run", !sec);
        rs.pacts[0] = 1; rs.pacts[1] = 1;
        boolean sanc = false; for (int i = 0; i < 6000; i++) if (Events.roll(rs, r, 1) == Events.SANCTUARY) sanc = true;
        ck("sin santuario tras 2 pactos", !sanc && rs.pactCount() == 2);

        // ---------------- pactos: ventaja + contrapartida, equilibrio y sin acumulacion
        for (ClassDef c : ClassDef.ALL) {
            RunState base = new RunState(c, 1, 0);
            for (Events.Pact pk : Events.PACTS) {
                RunState x = new RunState(c, 1, 0);
                x.pacts[pk.id] = 1; x.recalc();
                Stats s0 = base.stats, s1 = x.stats;
                boolean better = s1.dmgMul > s0.dmgMul + 1e-4 || s1.speedMul > s0.speedMul + 1e-4 || s1.dmgTaken < s0.dmgTaken - 1e-4 || s1.critChance > s0.critChance + 1e-4
                        || s1.lifesteal > s0.lifesteal + 1e-4 || s1.cdMul < s0.cdMul - 1e-4 || s1.goldMul > s0.goldMul + 1e-4;
                boolean worse = s1.maxHp < s0.maxHp - 1e-4 || s1.speedMul < s0.speedMul - 1e-4 || s1.dmgTaken > s0.dmgTaken + 1e-4 || s1.dmgMul < s0.dmgMul - 1e-4 || s1.potionsMax < s0.potionsMax;
                ck(pk.name + " (" + c.key + ") ventaja y contrapartida", better && worse);
                float net = (s1.dmgMul / s0.dmgMul) * (s1.maxHp / s0.maxHp) * (s1.speedMul / s0.speedMul) / (s1.dmgTaken / s0.dmgTaken);
                ck(pk.name + " equilibrado (neto " + net + ")", net > 0.85f && net < 1.2f);
                float h1 = x.stats.maxHp; x.recalc(); x.recalc();
                ck(pk.name + " no se acumula al recalcular", Math.abs(x.stats.maxHp - h1) < 1e-4);
            }
        }
        for (int i = 0; i < 200; i++) {
            RunState q = new RunState(ClassDef.ALL[0], i, 0);
            int[] o = Events.rollPacts(q, new Rng(i));
            ck("santuario ofrece 2 pactos distintos", o.length == 2 && o[0] != o[1]);
            q.pacts[o[0]] = 1;
            for (int v : Events.rollPacts(q, new Rng(i + 5))) ck("no ofrece un pacto ya tomado", v != o[0]);
        }
        // ---------------- costes del espiritu
        RunState sp = new RunState(ClassDef.ALL[0], 1, 0);
        sp.hp = sp.stats.maxHp * 0.30f;
        ck("espiritu: no pide vida si quedarias en peligro", !Events.spiritHpOk(sp));
        sp.hp = sp.stats.maxHp;
        ck("espiritu: vida suficiente", Events.spiritHpOk(sp) && sp.hp - Events.spiritHpCost(sp) >= sp.stats.maxHp * 0.25f);
        // ---------------- registro persistente de sucesos
        Save.S.events[Events.SPIRIT] = 3;
        Save.S.write(); T8.reload(p);
        ck("contador de sucesos persiste", Save.S.events[Events.SPIRIT] == 3 && Save.S.events.length == Events.COUNT);
        System.out.println(f == 0 ? "T11 OK (" + checks + " comprobaciones)" : "T11 FALLOS=" + f + " de " + checks);
        if (f > 0) System.exit(1);
    }
}
