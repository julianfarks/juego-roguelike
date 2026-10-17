package com.julianfarks.roguelike.core;

/** Etapa 5: retos del modo infinito (validez, puntaje, curacion, compatibilidad de registros). */
public class T13 {
    static int f = 0;
    static void ck(String n, boolean ok) { System.out.println((ok ? "ok   " : "FAIL ") + n); if (!ok) f++; }

    static RunState inf(int mods) {
        RunState rs = new RunState(ClassDef.ALL[0], 7, 0);
        rs.infinite = true; rs.floor = 1; rs.ruleset = Infinite.NORMAL; rs.mods = mods;
        return rs;
    }

    public static void main(String[] a) {
        Platform p = T8.plat(); T8.disk.clear(); T8.reload(p);
        ck("bonos: 10/10/15/15 = 50", Infinite.bonusPct(Infinite.MOD_ALL) == 50 && Infinite.bonusPct(0) == 0 && Infinite.bonusPct(Infinite.M_HEAL) == 15);
        // validez
        ck("run infinita normal: retos validos", Infinite.validMods(inf(0), 15) == 15);
        RunState camp = new RunState(ClassDef.ALL[0], 7, 0);
        ck("campana: sin retos", Infinite.validMods(camp, 15) == 0);
        RunState t = inf(0); t.markTest();
        ck("sesion de prueba: sin retos", Infinite.validMods(t, 15) == 0);
        RunState d = inf(0); d.devAssisted = true;
        ck("gemas de prueba: sin retos", Infinite.validMods(d, 15) == 0);
        RunState c = inf(0); c.ruleset = Infinite.COMPETITIVE;
        ck("reglas competitivas: sin retos", Infinite.validMods(c, 15) == 0 && !Infinite.COMPETITIVE.allowMods);
        ck("mascara fuera de rango se recorta", Infinite.validMods(inf(0), 0xFFFF) == 15);
        // curacion
        ck("curacion x0.6 con reto", Math.abs(Infinite.healMul(inf(Infinite.M_HEAL)) - 0.6f) < 1e-6 && Infinite.healMul(inf(0)) == 1f);
        // puntaje
        RunState r1 = inf(Infinite.M_FAST | Infinite.M_ELITE);
        r1.floorsDone = 3; r1.kills = 100; r1.bossKills = 3; r1.infRooms = 15;
        Infinite.Result base = Infinite.resultOf(inf(0)); 
        RunState r0 = inf(0); r0.floorsDone = 3; r0.kills = 100; r0.bossKills = 3; r0.infRooms = 15;
        int s0 = Infinite.resultOf(r0).score, s1 = Infinite.resultOf(r1).score;
        ck("puntaje base 3 pisos", s0 == Infinite.score(3, 100, 3, 15));
        ck("puntaje con +25%", s1 == Math.round(s0 * 1.25f) && s1 > s0);
        ck("pisos no cambian con retos", Infinite.resultOf(r1).floors == 3);
        RunState bad = inf(15); bad.markTest(); bad.floorsDone = 3; bad.kills = 100; bad.bossKills = 3; bad.infRooms = 15;
        ck("prueba: puntaje sin bono y marcado dev", Infinite.resultOf(bad).score == s0 && Infinite.resultOf(bad).dev && Infinite.resultOf(bad).mods == 0);
        // registro: ida y vuelta y compatibilidad
        Infinite.Result rr = Infinite.resultOf(r1);
        Infinite.Result back = Infinite.Result.parse(rr.toJson());
        ck("registro con retos ida y vuelta", back != null && back.mods == rr.mods && back.score == rr.score);
        Infinite.Result old = Infinite.resultOf(r0);
        String oj = old.toJson();
        ck("registro sin retos no escribe 'mods'", !oj.contains("mods") && Infinite.Result.parse(oj) != null);
        ck("alterar retos rompe la suma de control", Infinite.Result.parse(rr.toJson().replace("\"mods\":" + rr.mods, "\"mods\":15")) == null);
        // records: se conservan las reglas existentes (pisos primero)
        Infinite.record(Save.S, Infinite.resultOf(r0));
        RunState hi = inf(15); hi.floorsDone = 2; hi.kills = 5000; hi.bossKills = 2; hi.infRooms = 10;
        Infinite.record(Save.S, Infinite.resultOf(hi));
        ck("mas pisos sigue mandando sobre mas puntaje", Save.S.infBestFloor == 3);
        // guardado de la seleccion
        Save.S.infMods = 5; Save.S.write(); T8.reload(p);
        ck("seleccion de retos persiste", Save.S.infMods == 5);
        T8.disk.put("save", "{\"ver\":3,\"inf_mods\":99}"); T8.reload(p);
        ck("seleccion invalida se recorta", Save.S.infMods == (99 & 15));
        // la run guardada conserva los retos
        System.out.println(f == 0 ? "T13 OK" : "T13 FALLOS=" + f);
        if (f != 0) System.exit(1);
    }
}
