package com.julianfarks.roguelike.core;

import java.util.IdentityHashMap;

/**
 * Pruebas automaticas del escalado de enemigos tras los jefes (solo banco headless; BOT_ESCAL=1 desde DebugBot).
 * NO son pruebas en un dispositivo Android ni en Windows real. Genera salas de combate reales con distintos jefes derrotados,
 * dificultades y modo Infinito; comprueba cantidades, tope de vivos, entrada gradual, persecucion, transiciones y rendimiento.
 */
final class EscalationProbe {
    private EscalationProbe() {}
    static boolean done;
    static int fails, oks;
    static void ck(String n, boolean ok) { System.out.println("ES " + (ok ? "OK    " : "FALLA ") + n); if (ok) oks++; else fails++; }

    static RunScreen scr; static RunState rs; static Game game;

    static Level lv() { return scr.lv; }
    static void fr(int n) { for (int i = 0; i < n; i++) { scr.lv.update(1f / 60f); scr.lv.in.endFrame(); } }

    static boolean step(Game g, RunScreen r, Level l, Player pl, int frame) {
        if (done) return true;
        game = g; scr = r; rs = r.rs;
        done = true;
        for (int c : new int[]{'A', 'D', 'W', 'S', 37, 38, 39, 40, 'J', 'K', 'R', 'T', 'E', 'C', 'L', 'I', 'U', 32}) g.key(c, false);
        System.out.println("ES inicio escalado");
        try { run(); } catch (RuntimeException e) { e.printStackTrace(System.out); ck("sin excepciones durante las pruebas: " + e, false); }
        RunState.forceRoomMod = -1;
        System.out.println("ES FIN ok=" + oks + " fallos=" + fails);
        return true;
    }

    static int base(Level lv) { int n = 0; for (Room.Spawn s : lv.room.spawns) if (!s.optional && EnemyDef.get(s.enemy) != null) n++; return n; }

    static void load(int dungeons, boolean inf, int floor, int diff) { load(dungeons, inf, floor, diff, 1); }

    static void load(int dungeons, boolean inf, int floor, int diff, int roomNo) {
        rs.dungeonNo = dungeons; rs.stage = RunState.tierOf(dungeons); rs.infinite = inf; rs.floor = floor; rs.diff = diff; rs.roomNo = roomNo; rs.curEvent = 0;
        RunState.forceRoomMod = RunState.RM_NONE;
        scr.debugLoadCombat();
        scr.lv.pl.invuln = 9999f;
    }

    static void run() {
        int diff0 = rs.diff;
        // ---- 1. sin jefes derrotados la sala es la de siempre
        load(0, false, 1, 1);
        ck("sin jefes derrotados: la sala trae sus enemigos de siempre (" + Escalation.total(lv()) + " = " + base(lv()) + "), sin reserva", Escalation.total(lv()) == base(lv()) && lv().reserve.isEmpty() && lv().escExtra == 0);
        // ---- 2. mas enemigos tras cada jefe (misma sala base: se compara el extra con el numero de enemigos base)
        int prevF = -1; boolean mono = true; StringBuilder sb = new StringBuilder();
        float prevFactor = -1;
        for (int d = 0; d <= 8; d++) {
            load(d, false, 1, 1);
            int b = base(lv()), tot = Escalation.total(lv());
            float f = Escalation.extraFactor(rs);
            if (f < prevFactor) mono = false;
            prevFactor = f;
            if (tot != b + lv().escExtra || lv().escExtra < Escalation.extraCount(rs, b)) mono = false;
            sb.append(" ").append(d).append(":").append(b).append("+").append(lv().escExtra);
        }
        ck("tras cada jefe la sala trae progresivamente más enemigos (jefes:base+extra" + sb + ")", mono);
        load(3, false, 1, 1);
        ck("con 3 jefes derrotados ya hay extra (" + lv().escExtra + ")", lv().escExtra > 0 && Escalation.total(lv()) > base(lv()));
        // ---- 3. dificultad
        load(4, false, 1, 0); int easy = lv().escExtra; float fe = Escalation.extraFactor(rs);
        load(4, false, 1, 2); int hard = lv().escExtra; float fh = Escalation.extraFactor(rs);
        ck("la dificultad escala el extra (fácil x" + fe + " " + easy + " < difícil x" + fh + " " + hard + ")", fe < fh);
        // ---- 4. Infinito escala por su cuenta (por piso), no por los jefes de campaña
        load(8, true, 1, 1); float i1 = Escalation.extraFactor(rs);
        load(0, true, 6, 1); float i6 = Escalation.extraFactor(rs);
        ck("Infinito: escala por piso e ignora los jefes de campaña (piso1 con 8 jefes x" + i1 + ", piso6 x" + i6 + ")", i1 == 0f && i6 > 0f);
        // ---- 5. tope de vivos a la vez y entrada gradual
        load(8, false, 1, 2);
        Level lv = lv();
        int cap = Escalation.maxAlive(rs), b8 = base(lv), tot8 = Escalation.total(lv);
        int maxAlive = 0; boolean capOk = true; int spawned = 0;
        IdentityHashMap<Enemy, Boolean> seen = new IdentityHashMap<>();
        boolean dup = false;
        for (Enemy e : lv.enemies) seen.put(e, true);
        for (Enemy e : lv.reserve) if (seen.put(e, true) != null) dup = true;
        ck("ningún enemigo duplicado entre la sala y la reserva", !dup);
        float minDist = 1e9f; int hunters = 0, chasing = 0;
        float t = 0; int kills = 0;
        for (int i = 0; i < 60 * 90 && !lv.cleared; i++) {
            int n0 = lv.enemies.size();
            fr(1); t += 1f / 60f;
            if (lv.enemies.size() > n0) {             // acaba de entrar un refuerzo
                Enemy ne = lv.enemies.get(lv.enemies.size() - 1);
                spawned++;
                minDist = Math.min(minDist, Mth.dist(ne.x, ne.y, lv.pl.x, lv.pl.y));
                if (ne.hunter) hunters++;
            }
            int alive = 0; for (Enemy e : lv.enemies) if (e.alive && !e.optional) alive++;
            maxAlive = Math.max(maxAlive, alive);
            if (alive > Math.max(cap, b8)) capOk = false;
            if (i % 40 == 20) { for (Enemy e : lv.enemies) if (e.alive && !e.optional) { if (e.hunter && e.state != Enemy.PATROL) chasing++; e.hp = 0; e.die(lv); kills++; break; } }
        }
        ck("nunca más de " + Math.max(cap, b8) + " enemigos vivos a la vez (máx. visto " + maxAlive + ", total de la sala " + tot8 + ")", capOk);
        ck("los extra entran poco a poco desde la reserva (" + spawned + " refuerzos)", spawned > 0 && spawned >= tot8 - Math.max(cap, b8) - 1);
        ck("los refuerzos aparecen lejos del jugador cuando la sala lo permite (mín. " + Math.round(minDist) + " px)", minDist >= Escalation.SPAWN_MIN_DIST - 1 || lv.room.spawns.size() < 3);
        ck("los refuerzos persiguen al jugador (cazadores " + hunters + ", persiguiendo al abatirlos " + chasing + ")", hunters == spawned && (spawned == 0 || chasing > 0));
        ck("la sala solo se da por despejada al vaciar la reserva (despejada=" + lv.cleared + ", reserva=" + lv.reserve.size() + ")", lv.cleared && lv.reserve.isEmpty());
        // ---- 6. transicion: la reserva no pasa a la siguiente sala
        load(8, false, 1, 2);
        Level a = lv(); int resA = a.reserve.size();
        load(8, false, 1, 2);
        boolean leak = false; for (Enemy e : lv().enemies) if (a.enemies.contains(e) || a.reserve.contains(e)) leak = true;
        for (Enemy e : lv().reserve) if (a.enemies.contains(e) || a.reserve.contains(e)) leak = true;
        ck("al cambiar de sala no se arrastran ni duplican enemigos de la anterior (reserva anterior " + resA + ")", !leak);
        // ---- 7. variantes y mini-jefe a partir de cierto numero de jefes
        int elites = 0, minis = 0, tries = 0;
        for (int k = 0; k < 20; k++) { load(8, false, 1, 1, 1 + k % 3); rs.seed += 7919;
            for (Enemy e : lv().enemies) { if (e.elite && e.hunter) elites++; if (e.miniBoss) minis++; }
            for (Enemy e : lv().reserve) { if (e.elite && e.hunter) elites++; if (e.miniBoss) minis++; } tries++; }
        ck("con muchos jefes derrotados aparecen variantes élite entre los refuerzos (" + elites + " en " + tries + " salas)", elites > 0);
        ck("y algún mini-jefe ocasional (" + minis + " en " + tries + " salas)", minis > 0);
        load(1, false, 1, 1);
        boolean noVar = true; for (Enemy e : lv().enemies) if (e.miniBoss) noVar = false;
        ck("con 1 jefe derrotado no hay mini-jefes", noVar);
        // ---- 8. rendimiento: peor caso (8 jefes, difícil) frente a la sala base
        load(0, false, 1, 2); long t0 = System.nanoTime(); fr(600); float msBase = (System.nanoTime() - t0) / 1e6f / 600f;
        load(8, false, 1, 2); t0 = System.nanoTime(); fr(600); float msMax = (System.nanoTime() - t0) / 1e6f / 600f;
        System.out.println("ES PERF ms/fotograma (lógica) base=" + msBase + " escalado=" + msMax + " enemigos vivos=" + lv().enemies.size());
        ck("rendimiento: con el escalado máximo la lógica sigue por debajo de 4 ms por fotograma (" + msMax + " ms)", msMax < 4f);
        rs.diff = diff0;
    }
}
