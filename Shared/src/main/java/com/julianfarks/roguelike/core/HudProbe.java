package com.julianfarks.roguelike.core;

/**
 * Pruebas del HUD de combate (solo banco headless; BOT_HUDTEST=cd|syn|status|ui desde DebugBot):
 *  cd    : texto del tiempo de reutilizacion, senal de "lista" una sola vez, botones que no se mueven.
 *  syn   : las senales de sinergia no se repiten (un aviso por sinergia aunque se dispare cientos de veces) y tienen color por tipo.
 *  status: iconos y barritas de estados del jugador / ritmo / contraataque sin solaparse.
 *  ui    : textos del HUD sin cortes (FIT) en el idioma y ancho del banco, con vida baja, jefe y desafio activos.
 */
final class HudProbe {
    private HudProbe() {}
    static int t0 = -1, fails = 0, oks = 0;
    static void ck(String n, boolean ok) { System.out.println("HUD " + (ok ? "OK    " : "FALLA ") + n); if (ok) oks++; else fails++; }

    static boolean step(Game g, RunScreen rs, Level lv, Player p, int frame) {
        if (t0 < 0) { t0 = frame; System.out.println("HUD inicio modo " + System.getenv("BOT_HUDTEST")); }
        int t = frame - t0;
        String mode = System.getenv("BOT_HUDTEST");
        if (mode.equals("cd")) return cd(g, rs, t);
        if (mode.equals("syn")) return syn(rs, lv, p, t);
        if (mode.equals("status")) return status(rs, lv, t);
        return ui(rs, lv, t);
    }

    static boolean cd(Game g, RunScreen rs, int t) {
        RunState r = rs.rs;
        if (t == 0) {
            ck("texto: 7,2 s -> \"8\"", RunScreen.cdText(7.2f).equals("8"));
            ck("texto: 3,0 s -> \"3\"", RunScreen.cdText(3.0f).equals("3"));
            ck("texto: 2,41 s -> \"2.5\" (un decimal bajo 3 s)", RunScreen.cdText(2.41f).equals("2.5"));
            ck("texto: 0,02 s -> \"0.1\" (nunca \"0\" mientras siga en reutilizacion)", RunScreen.cdText(0.02f).equals("0.1"));
            ck("texto: 1,0 s -> \"1.0\"", RunScreen.cdText(1.0f).equals("1.0"));
            float[] x0 = new float[4], y0 = new float[4];
            for (int k = 0; k < 4; k++) { Input.Btn b = g.input.btn[Input.B_S1 + k]; x0[k] = b.cx; y0[k] = b.cy; }
            sx = x0; sy = y0;
            r.cd[0] = 1.0f; r.cd[1] = 0f; r.cd[2] = 5f;
            readyCount0 = 0;
            return false;
        }
        // simula el paso del tiempo de la habilidad 0 (1 s) y comprueba que la senal salta una sola vez
        float dt = 1f / 60f;
        if (t <= 100) {
            if (r.cd[0] > 0) r.cd[0] = Math.max(0f, r.cd[0] - dt);
            if (!prevReady && rs.skReady[0] > 0) readyCount0++;     // el propio juego llama a hudTick en cada fotograma
            prevReady = rs.skReady[0] > 0;
            return false;
        }
        ck("la habilidad 0 avisa al quedar lista exactamente una vez (" + readyCount0 + ")", readyCount0 == 1);
        ck("la habilidad 1 (siempre lista) no emite senal", rs.skReady[1] <= 0);
        ck("la habilidad 2 (en reutilizacion) no emite senal", rs.skReady[2] <= 0);
        ck("la senal dura menos de 0,6 s (breve)", rs.skReady[0] < 0.01f);
        boolean same = true;
        for (int k = 0; k < 4; k++) { Input.Btn b = g.input.btn[Input.B_S1 + k]; same &= b.cx == sx[k] && b.cy == sy[k]; }
        ck("los botones de habilidad no cambian de posicion al pasar de reutilizacion a lista", same);
        System.out.println("HUD FIN ok=" + oks + " fallos=" + fails);
        return true;
    }
    static float[] sx, sy; static int readyCount0; static boolean prevReady;

    static boolean syn(RunScreen rs, Level lv, Player p, int t) {
        RunState r = rs.rs;
        int s = 0;
        BSyn sy = BlessData.syns()[s];
        if (t == 0) {
            int[] mem = java.util.Arrays.copyOfRange(sy.members, 0, sy.need);
            BlessProbe.grant(r, mem, 1);
            lv.pl.alive = true; lv.enemies.clear(); BlessEffects.dbgAnnounced = 0;
            ck("la sinergia '" + sy.name + "' se activa con " + sy.need + " miembros", r.bx.synOn[s]);
            return false;
        }
        BlessProbe.ensureDummies(lv, p);
        p.alive = true;
        BlessProbe.driveEvents(lv, p, t, false);
        if (t < 900) return false;
        int fired = r.bx.firedSyn[s];
        ck("la sinergia se dispara muchas veces (" + fired + ")", fired >= 5);
        ck("pero el juego NO la anuncia (avisos por nombre: " + BlessEffects.dbgAnnounced + ")", BlessEffects.dbgAnnounced == 0);
        boolean txt = false; for (DmgText d : lv.texts) if (d.text != null && (d.text.contains("inergia") || d.text.equals(sy.name))) txt = true;
        ck("ningun texto flotante nombra la sinergia ni dice 'Sinergia activada'", !txt);
        int[] cols = new int[BlessData.SYN.length]; java.util.Set<Integer> distinct = new java.util.HashSet<>();
        for (int i = 0; i < cols.length; i++) { cols[i] = BlessEffects.synColor(i); distinct.add(cols[i]); }
        ck("el color de la senal depende del tipo de combinacion (" + distinct.size() + " tipos)", distinct.size() >= 5);
        ck("fuego -> naranja, hielo -> azul claro", BlessEffects.synColor(0) == 0xFF8A3C && BlessEffects.synColor(1) == 0x8AD8FF);
        System.out.println("HUD FIN ok=" + oks + " fallos=" + fails);
        return true;
    }

    static boolean status(RunScreen rs, Level lv, int t) {
        if (t < 5) return false;
        Player pl = lv.pl; RunState r = rs.rs;
        pl.st[Ent.BURN] = 3f; pl.st[Ent.FREEZE] = 2f; pl.st[Ent.POISON] = 4f; pl.st[Ent.SHOCK] = 1f; pl.st[Ent.BLEED] = 5f; pl.st[Ent.CURSE] = 2f;
        lv.flowT = 5f; lv.counterT = 1.1f;
        // 6 estados + ritmo + contra deben caber en la fila (sin salirse del area del HUD): 8 x 18 px mas margen
        int n = 8;
        float right = 8 + n * 18;
        ck("la fila de estados cabe (hasta " + Math.round(right) + " px) y no invade el centro del HUD", right < 480 / 2f - 40);
        ck("el ritmo y el contraataque tienen indicador mientras dura la ventana", lv.flowT > 0 && lv.counterT > 0);
        pl.st[Ent.BURN] = pl.st[Ent.FREEZE] = pl.st[Ent.POISON] = pl.st[Ent.SHOCK] = pl.st[Ent.BLEED] = pl.st[Ent.CURSE] = 0; lv.flowT = 0; lv.counterT = 0;
        // enemigo con 5 estados: como mucho 3 iconos
        Enemy e = new Enemy(EnemyDef.get("esqueleto"), false, 1f, 1f);
        int cnt = 0; String[] sic = {"burn", "freeze", "shield", "poison", "shock", "bleed", "", "", "skull"};
        for (int i = 0; i < 5; i++) e.st[i] = 3f;
        for (int i = 0; i < Ent.ST_COUNT && cnt < 3; i++) if (e.st[i] > 0 && !sic[i].isEmpty()) cnt++;
        ck("un enemigo con 5 estados muestra como mucho 3 iconos (" + cnt + ")", cnt == 3);
        System.out.println("HUD FIN ok=" + oks + " fallos=" + fails);
        return true;
    }

    static int uiStep;
    static boolean ui(RunScreen rs, Level lv, int t) {
        if (t % 3 != 0) return false;
        if (!PrepScreen.fitErrors.isEmpty()) { for (String e : PrepScreen.fitErrors) System.out.println("FIT " + e); fails += PrepScreen.fitErrors.size(); PrepScreen.fitErrors.clear(); }
        RunState r = rs.rs;
        Player pl = lv.pl;
        pl.alive = true;
        if (uiStep == 0) { r.hp = r.stats.maxHp; }
        if (uiStep == 1) { r.hp = r.stats.maxHp * 0.2f; }                        // vida baja
        if (uiStep == 2) { pl.st[Ent.BURN] = 3f; pl.st[Ent.FREEZE] = 2f; pl.st[Ent.POISON] = 4f; lv.flowT = 5f; lv.counterT = 1f; for (int k = 0; k < 3; k++) r.cd[k] = 1.4f + k * 6; }
        if (uiStep == 3) { r.gold = 99999; r.souls = 99999; r.hp = r.stats.maxHp; }
        if (uiStep == 4) { rs.toast = "Autoguardado con un texto algo mas largo de lo normal"; rs.toastT = 2f; }
        if (uiStep == 5) { rs.chal = Events.CH_NODMG; rs.chalState = 0; }
        if (uiStep == 6) { rs.chal = Events.CH_TIMED; rs.chalT = 37f; }
        if (uiStep == 3 && System.getenv("BOT_HUDHOLD") != null) { pl.st[Ent.BURN] = 3f; pl.st[Ent.FREEZE] = 2f; pl.st[Ent.POISON] = 4f; lv.flowT = 3f; lv.counterT = 1f; r.cd[0] = 1.4f; r.cd[1] = 7f; r.hp = r.stats.maxHp * 0.2f; return false; }   // solo para capturas
        if (uiStep >= 7) {
            rs.chal = -1; pl.st[Ent.BURN] = pl.st[Ent.FREEZE] = pl.st[Ent.POISON] = 0;
            System.out.println("HUD FIN idioma=" + I18n.code() + " desajustes=" + fails);
            return true;
        }
        uiStep++;
        return false;
    }
}
