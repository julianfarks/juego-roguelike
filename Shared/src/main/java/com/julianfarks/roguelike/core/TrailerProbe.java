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

    static int chargeHold = -1;
    static final int[] SHOWCASE = {6, 9, 23, 4, 19, 36, 34, 10};     // armas secundarias reales que se muestran en "arsenal"

    private static void tap(Game g, int c) { g.key(c, true); g.key(c, false); }

    /** Devuelve true si este fotograma lo controla la herramienta de captura (el bot no juega). */
    static boolean step(Game g, RunScreen rs, Level lv, Player p, int frame) {
        String m0 = System.getenv("BOT_TRAILER");
        if (m0.equals("arsenal") || m0.equals("inv") || m0.equals("charge") || m0.equals("chest") || m0.equals("calm")) return step2(g, rs, lv, p, frame, m0);
        step1(g, rs, lv, p, frame);
        return false;
    }

    static boolean step2(Game g, RunScreen rs, Level lv, Player p, int frame, String mode) {
        if (t0 < 0) t0 = frame;
        int t = frame - t0;
        RunState r = rs.rs;
        switch (mode) {
            case "arsenal": {     // cada 2,5 s se equipa otra arma secundaria real (con su municion) y el ataque la dispara
                if (t % 150 == 0) {
                    int id = SHOWCASE[(t / 150) % SHOWCASE.length];
                    r.sec = id; r.wState[id] = 1; r.secAmmo = Items.SEC_AMMO[id]; r.secActive = true; r.recalc();
                    p.swapAnimT = 0.32f; p.swapIcon = Items.SEC_ICON[id];
                    System.out.println("TRAILER arsenal t=" + t + " frame=" + frame + " arma=" + Items.SEC_NAME[id]);
                }
                r.secActive = true;
                return false;
            }
            case "charge": {     // ataque cargado real: mantener el ataque ~1 s junto a un enemigo y soltar
                if (chargeHold >= 0) {
                    if (frame - chargeHold >= 62) { g.key('J', false); chargeHold = -1; System.out.println("TRAILER carga soltada frame=" + frame); }
                    return true;
                }
                Ent near = null;
                for (Enemy e : lv.enemies) if (e.alive && Math.abs(e.x - p.x) < 44 && Math.abs(e.y - p.y) < 30) near = e;
                if (near != null && p.onGround && p.state <= Player.AIR && frame % 20 == 0 && r.cd[0] > 0) {
                    p.right = near.x > p.x;
                    for (int c : new int[]{'A', 'D', 'W', 'J'}) g.key(c, false);
                    g.key('J', true); chargeHold = frame; System.out.println("TRAILER carga empieza frame=" + frame);
                    return true;
                }
                return false;
            }
            case "inv": {
                if (t == 0) {
                    for (int c : new int[]{'A', 'D', 'W', 'J', 'K'}) g.key(c, false);
                    BlessProbe.grant(r, new int[]{id("brasas"), id("llama_voraz"), id("parry_maestro"), id("doble_tajo"), id("espiritu_rayo"), id("pira"), id("congelacion_profunda")}, 2);
                    for (int w : new int[]{6, 9, 23, 13, 5}) r.wState[w] = 1;
                    r.sec = 6; r.secAmmo = Items.SEC_AMMO[6]; r.secActive = false; r.gren = 2; r.grenCount = 3; r.special = 2; r.relicsThisRun[0] = true; r.recalc();
                    Inventory.seeAll(r);
                }
                if (t == 20) rs.openInventory(false);
                int[][] seq = {{70, 'D'}, {100, 'D'}, {130, 'D'}, {175, 'E'}, {215, 'D'}, {245, 'D'}, {290, 'E'}, {335, 'E'}, {365, 'D'}, {410, 'E'}};
                for (int[] q : seq) if (t == q[0]) tap(g, q[1]);
                return rs.ov == RunScreen.OV_INV || t < 20;
            }
            case "chest": {      // combate real; al aparecer los cofres de la ronda el bot va a abrirlos. En la pantalla de premio recorre las opciones
                if (rs.ov == RunScreen.OV_CHEST && rs.ovT > 0.5f && rs.ovT < 2.2f && frame % 30 == 0) tap(g, 'D');
                return false;
            }
            default: return false;   // calm: sala sin enemigos, el bot explora
        }
    }

    static void step1(Game g, RunScreen rs, Level lv, Player p, int frame) {
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
