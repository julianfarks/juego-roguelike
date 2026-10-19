package com.julianfarks.roguelike.core;

/**
 * Solo para GRABAR escenas reales de los trailers (BOT_TRAILER=bless|fire desde DebugBot, junto a --record).
 * No inventa nada: usa las pantallas, bendiciones, sinergias y enemigos reales del juego; solo coloca una situacion repetible.
 *  bless: altar con tres ofertas reales (distintas rarezas/estilos), lista de bendiciones y la eleccion que completa la sinergia Infierno
 *         (el juego muestra el aviso y el efecto de sinergia por si mismo).
 *  fire : combate real con la build Infierno (Brasas Eternas + Llama Voraz + Contagio Igneo) contra un grupo de enemigos del bioma.
 */
final class TrailerProbe {
    private TrailerProbe() {}
    static int t0 = -1, lastCounter = -99;

    static int id(String k) { return BlessProbe.idOf(k); }

    static void step(Game g, RunScreen rs, Level lv, Player p, int frame) {
        if (t0 < 0) { t0 = frame; lv.pl.alive = true; }
        int t = frame - t0;
        String mode = System.getenv("BOT_TRAILER");
        RunState r = rs.rs;
        if (mode.equals("bless")) {
            if (t == 0) { BlessProbe.grant(r, new int[0], 1); }
            int[][] offers = {
                {id("pira"), id("parry_maestro"), id("tormenta_acero"), id("legion_espectral")},
                {id("sentencia"), id("congelacion_profunda"), id("proyectil_explosivo"), id("forma_sombra")}};
            for (int k = 0; k < 2; k++) {
                int b = k * 100;
                if (t == b) rs.dbgShowBless(offers[k]);
                if (t >= b && t < b + 96) rs.offerSelDbg((t - b) / 24);
            }
            if (t == 198) BlessProbe.grant(r, new int[]{id("brasas"), id("llama_voraz"), id("contagio_igneo"), id("pira"), id("parry_maestro"), id("congelacion_profunda"), id("proyectil_explosivo"), id("espiritu_rayo"), id("doble_tajo")}, 1);
            if (t == 200) rs.dbgShowList(0, 0);
            if (t == 250) rs.dbgShowList(1, 0);
            if (t == 300) {
                BlessProbe.grant(r, new int[]{id("brasas"), id("llama_voraz"), id("parry_maestro")}, 1);
                rs.dbgShowBless(new int[]{id("contagio_igneo"), id("brasa_critica"), id("aliento_dragon"), id("rastro_ardiente")});
            }
            if (t >= 300 && t < 372) rs.offerSelDbg(t < 330 ? 1 : t < 350 ? 3 : 0);
            if (t == 372) { rs.ovT = 1f; for (Screen.Hit h : rs.hitsDbg()) if (h.tag == 0) { rs.clickDbg(h); break; } }
            lv.pl.invuln = 99f;
        } else if (mode.equals("parry")) {
            // parry real del bot contra el jefe; justo despues (ventana de contraataque del juego) el jugador pulsa atacar una vez
            if (lv.counterT > 0.8f && frame - lastCounter > 40) { lastCounter = frame; g.key('C', false); g.key('J', true); System.out.println("TRAILER contraataque f=" + frame + " counterT=" + lv.counterT); }
        } else {
            if (t == 0) {
                BlessProbe.grant(r, new int[]{id("brasas"), id("llama_voraz"), id("contagio_igneo")}, 2);
                lv.enemies.clear(); lv.projs.clear(); lv.toKill = 0; lv.cleared = false;
                Room rm = lv.room;
                String[] pool = rm.biome.enemies;
                int n = 0;
                for (int x = (int) (p.x / Room.TS) + 7; n < 5 && x < rm.w - 8; x += 3) {
                    int gy = rm.ground[x];
                    if (gy <= 0 || (rm.spikeCols != null && rm.spikeCols.contains(x))) continue;
                    String eid = pool[n % pool.length];
                    EnemyDef d = EnemyDef.get(eid);
                    if (d == null || d.role == EnemyDef.FLY_SHOOT || d.role == EnemyDef.FLY_DIVE || d.role == EnemyDef.HEAVY) eid = pool[0];
                    lv.spawnEnemy(eid, false, x * Room.TS + 8, gy * Room.TS);
                    n++;
                }
                System.out.println("TRAILER fire enemigos=" + n + " sinergia infierno=" + r.bx.synOn[0]);
            }
            r.hp = Math.max(r.hp, r.stats.maxHp * 0.5f);
        }
    }
}
