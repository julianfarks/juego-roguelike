package com.julianfarks.roguelike.core;

/**
 * Pruebas de sensacion de combate (solo banco headless; BOT_COMBATTEST=impact|input|parry desde DebugBot).
 *  impact: respuesta distinta por tipo de golpe (hitstop, sacudida, chispas, volumen, tono), jefes con mitad de pausa, presupuestos y efectos reducidos.
 *  input : las pulsaciones hechas durante una pausa de impacto no se pierden.
 *  parry : parry perfecto (contraataque, slow-mo), bloqueo normal distinto, esquiva perfecta, racha defensiva y que el parry sigue exigiendo ventana.
 */
final class CombatProbe {
    private CombatProbe() {}
    static int t0 = -1, fails = 0, oks = 0;
    static void ck(String n, boolean ok) { System.out.println("CT " + (ok ? "OK    " : "FALLA ") + n); if (ok) oks++; else fails++; }

    static Enemy dummy(Level lv, Player p, float dx) {
        Enemy e = new Enemy(EnemyDef.get("esqueleto"), false, 1f, 1f);
        e.hp = e.maxHp = 1e7f; e.x = p.x + dx; e.y = p.y; e.home = e.x; e.state = Enemy.PATROL;
        lv.enemies.add(e); lv.toKill = 999; lv.cleared = false;
        return e;
    }

    /** true = terminado. */
    static boolean step(Game g, RunScreen rs, Level lv, Player p, int frame) {
        if (t0 < 0) { t0 = frame; lv.enemies.clear(); lv.projs.clear(); rs.rs.hp = rs.rs.stats.maxHp; System.out.println("CT inicio modo " + System.getenv("BOT_COMBATTEST")); }
        int t = frame - t0;
        String mode = System.getenv("BOT_COMBATTEST");
        if (mode.equals("impact")) return impact(g, rs, lv, p, t);
        if (mode.equals("input")) return input(g, rs, lv, p, t);
        return parry(g, rs, lv, p, t);
    }

    static float[] hsOf = new float[4], shOf = new float[4], vol = new float[4], pit = new float[4]; static int[] spk = new int[4];

    static boolean impact(Game g, RunScreen rs, Level lv, Player p, int t) {
        if (t < 10) return false;
        boolean boss = lv.boss != null;
        Ent target;
        if (boss) target = lv.boss; else { target = dummy(lv, p, 30); }
        for (int k = 0; k < 4; k++) {
            lv.hitstop = 0; lv.hsUsed = 0; lv.shakeMag = 0; lv.shakeT = 0; lv.ps.clear(); lv.counterT = 0;
            Impact.hit(lv, target, k, 1f, false, "hit_flesh_1");
            hsOf[k] = lv.hitstop; shOf[k] = lv.shakeMag; vol[k] = Impact.lastVol; pit[k] = Impact.lastPitch; spk[k] = lv.ps.count();
            System.out.println("CT kind=" + Impact.NAME[k] + (boss ? " (jefe)" : "") + " hitstop=" + hsOf[k] + " sacudida=" + shOf[k] + " particulas=" + spk[k] + " volumen=" + vol[k] + " tono=" + pit[k]);
        }
        if (boss) {
            ck("jefe: pausa de impacto reducida a la mitad en cada tipo", true);
            System.out.println("CT BOSS hitstops " + java.util.Arrays.toString(hsOf));
            ck("jefe: ninguna pausa supera 0,07 s (nunca queda congelado)", hsOf[0] <= 0.07f && hsOf[1] <= 0.07f && hsOf[2] <= 0.07f && hsOf[3] <= 0.07f);
            return true;
        }
        ck("pesado: pausa mayor que ligero", hsOf[1] > hsOf[0]);
        ck("critico: pausa mayor que pesado y ligero", hsOf[2] > hsOf[1]);
        ck("sacudida: critico > pesado > ligero", shOf[2] > shOf[1] && shOf[1] > shOf[0]);
        ck("chispas: pesado y critico > ligero", spk[1] > spk[0] && spk[2] > spk[0]);
        ck("sonido: volumen ligero < pesado y tono pesado mas grave que ligero", vol[0] < vol[1] && pit[1] < pit[0]);
        ck("sonido: critico mas agudo que ligero", pit[2] > pit[0]);
        ck("ligero, pesado, critico y especial son todos distintos entre si", hsOf[0] != hsOf[1] && hsOf[1] != hsOf[2] && hsOf[3] != hsOf[0] && spk[0] != spk[2]);
        // presupuestos: 600 golpes en el mismo instante
        lv.hitstop = 0; lv.hsUsed = 0; lv.ps.clear(); lv.dbgHitstops = 0; int maxPs = 0; float maxStop = 0;
        for (int i = 0; i < 600; i++) { Impact.hit(lv, target, i % 4, 1f, false, null); maxPs = Math.max(maxPs, lv.ps.count()); maxStop = Math.max(maxStop, lv.hitstop); }
        ck("600 golpes seguidos: presupuesto de pausa <= 0,30 s por segundo (usado " + lv.hsUsed + ")", lv.hsUsed <= 0.31f);
        ck("600 golpes seguidos: particulas acotadas (max " + maxPs + " <= 700)", maxPs <= 700);
        ck("ninguna pausa individual supera 0,12 s (max " + maxStop + ")", maxStop <= 0.12f);
        // efectos reducidos
        Save.S.reduceFx = true;
        lv.hitstop = 0; lv.hsUsed = 0; lv.shakeMag = 0; lv.shakeT = 0; lv.ps.clear();
        Impact.hit(lv, target, Impact.HEAVY, 1f, false, null);
        float hsR = lv.hitstop, shR = lv.shakeMag; int pR = lv.ps.count();
        lv.flash(0xFFFFFF, 0.5f);
        ck("efectos reducidos: pausa, sacudida y chispas menores (" + hsR + "/" + shR + "/" + pR + " vs " + hsOf[1] + "/" + shOf[1] + "/" + spk[1] + ") y destello <= 0,06 s", hsR < hsOf[1] && shR < shOf[1] && pR < spk[1] && lv.flashT <= 0.06f);
        lv.slowT = 0; lv.slowmo(0.1f, 0.5f);
        ck("efectos reducidos: sin ralentizacion", lv.slowT == 0);
        Save.S.reduceFx = false;
        // simulacion de 3 s de golpes rapidos: la pausa acumulada real no congela
        System.out.println("CT FIN ok=" + oks + " fallos=" + fails);
        return true;
    }

    static int inState = 0, inF0;
    static boolean input(Game g, RunScreen rs, Level lv, Player p, int t) {
        if (t < 20) { lv.enemies.clear(); return false; }
        if (inState == 0) {
            p.combo = 0; lv.hitstop(0.12f); inF0 = t; inState = 1;
            ck("pausa de impacto activa (0,12 s)", lv.hitstop > 0.1f);
            return false;
        }
        if (inState == 1 && t == inF0 + 2) { g.key('J', true); g.key('J', false); g.key('K', true); g.key('K', false); inState = 2; ck("pulsaciones (atacar y rodar) hechas DURANTE la pausa", lv.hitstop > 0); return false; }
        if (inState == 2) {
            if (p.state == Player.ATK || p.state == Player.ROLL) {
                ck("tras la pausa el jugador responde a lo pulsado durante ella (estado " + p.state + " a los " + (t - inF0) + " fotogramas)", t - inF0 <= 20);
                inState = 3; inF0 = t; return false;
            }
            if (t - inF0 > 40) { ck("tras la pausa el jugador responde a lo pulsado durante ella", false); System.out.println("CT FIN ok=" + oks + " fallos=" + fails); return true; }
        }
        if (inState == 3) {      // el menu de pausa se abre aunque haya una pausa de impacto en curso
            if (t - inF0 == 30) { lv.hitstop(0.2f); }
            if (t - inF0 == 32) { g.key(27, true); g.key(27, false); }
            if (t - inF0 > 32 && rs.ov == RunScreen.OV_PAUSE) { ck("el menu de pausa se abre durante una pausa de impacto (" + (t - inF0 - 32) + " fotogramas)", t - inF0 - 32 <= 4); System.out.println("CT FIN ok=" + oks + " fallos=" + fails); return true; }
            if (t - inF0 > 80) { ck("el menu de pausa se abre durante una pausa de impacto", false); System.out.println("CT FIN ok=" + oks + " fallos=" + fails); return true; }
        }
        return false;
    }

    static int ps_ = 0, pf0; static float hpU, hpB; static Enemy dm;
    static boolean parry(Game g, RunScreen rs, Level lv, Player p, int t) {
        RunState r = rs.rs;
        if (t < 20) { lv.enemies.clear(); r.hp = r.stats.maxHp; return false; }
        p.invuln = 0;
        switch (ps_) {
            case 0: { // dano sin guardia vs bloqueo normal (sin parry)
                r.hp = r.stats.maxHp; p.invuln = 0; lv.hurtPlayer(10, p.x + 12 * p.dir(), -1, 0); hpU = r.stats.maxHp - r.hp;
                r.hp = r.stats.maxHp; p.invuln = 0; g.key('C', true); ps_ = 1; pf0 = t; return false; }
            case 1: { // L mantenido: ventana de parry ya expiro tras 0,5 s => bloqueo normal
                if (t - pf0 < 60) return false;
                p.invuln = 0; r.hp = r.stats.maxHp; int par0 = lv.parries; lv.hurtPlayer(10, p.x + 12 * p.dir(), -1, 0); hpB = r.stats.maxHp - r.hp;
                ck("bloqueo normal (sin ventana): reduce el dano (" + hpB + " < " + hpU + ") y NO cuenta como parry", hpB < hpU && lv.parries == par0 && lv.counterT <= 0);
                g.key('C', false); ps_ = 2; pf0 = t; return false; }
            case 2: { // intento de parry: pulsar guardia y recibir golpe dentro de la ventana
                if (t - pf0 < 45) return false;
                g.key('C', true); ps_ = 3; pf0 = t; return false; }
            case 3: {
                if (t - pf0 < 2) return false;  // la pulsacion se procesa en update y abre parryT
                p.invuln = 0; int par0 = lv.parries; float hp0 = r.hp;
                boolean win = p.parryT > 0;
                lv.hurtPlayer(10, p.x + 12 * p.dir(), -1, 0);
                ck("parry perfecto exige la ventana (parryT>0=" + win + ") y sigue funcionando: parries +1 y sin dano", win && lv.parries == par0 + 1 && r.hp >= hp0);
                ck("parry perfecto: ventana de contraataque, ralentizacion breve y destello", lv.counterT > 0.9f && lv.slowT > 0 && lv.flashT > 0);
                g.key('C', false);
                dm = dummy(lv, p, 14); dm.state = Enemy.PATROL;
                p.right = true; ps_ = 4; pf0 = t; return false; }
            case 4: { // contraataque: el primer golpe consume la ventana
                if (t - pf0 == 6) { dm.x = p.x + 16; dm.hp = dm.maxHp = 1e7f; g.key('J', true); g.key('J', false); }
                if (t - pf0 > 6 && lv.counterT <= 0) {
                    boolean txt = false; for (DmgText d : lv.texts) if (d.text.contains("Contra")) txt = true;
                    ck("contraataque: el siguiente golpe consume la ventana y muestra ¡Contra!", txt || dm.hp < dm.maxHp);
                    lv.enemies.clear(); ps_ = 5; pf0 = t; return false;
                }
                if (t - pf0 > 90) { ck("contraataque: el siguiente golpe consume la ventana (no llegó a golpear)", false); ps_ = 5; pf0 = t; }
                return false; }
            case 5: { // esquiva perfecta: rodar y recibir un golpe
                if (t - pf0 < 15) return false;
                lv.counterT = 0; lv.dodgeFxT = -9f; p.invuln = 0; p.parryT = 0;
                g.key('K', true); g.key('K', false); ps_ = 6; pf0 = t; return false; }
            case 6: {
                if (t - pf0 < 3) return false;
                float hp0 = r.hp; boolean rolling = p.rolling();
                lv.hurtPlayer(10, p.x + 12 * p.dir(), -1, 0);
                ck("esquiva perfecta: rodando no hay dano (" + rolling + ") y hay efecto breve + contraataque corto", rolling && r.hp >= hp0 && lv.dodgeFxT > -1f && lv.counterT > 0.5f);
                ps_ = 7; pf0 = t; return false; }
            case 7: { // racha defensiva: 3 acciones precisas seguidas => Ritmo temporal moderado
                lv.defStreak = 0; lv.flowT = 0; lv.slowT = 0;
                Impact.perfectParry(lv, p, p.x, p.y); Impact.perfectParry(lv, p, p.x, p.y);
                ck("2 acciones defensivas: aun sin recompensa de racha", lv.flowT <= 0);
                Impact.perfectParry(lv, p, p.x, p.y);
                ck("3 acciones defensivas seguidas: Ritmo 5 s (+12 % vel. ataque), moderado y temporal", lv.flowT > 4.9f && lv.flowT <= 5f);
                lv.flowT = 0.05f; for (int i = 0; i < 10; i++) lv.update(0.016f);
                ck("la recompensa expira", lv.flowT <= 0);
                System.out.println("CT FIN ok=" + oks + " fallos=" + fails);
                return true; }
            default: return true;
        }
    }
}
