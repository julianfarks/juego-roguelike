package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/**
 * Sonda de pruebas de las bendiciones (solo banco headless, se activa con BOT_BLESSTEST desde DebugBot; no participa en el juego normal).
 * Modos (BOT_BLESSTEST=...):
 *   single[:desde-hasta]  concede cada bendicion por separado, dispara los eventos reales del juego y comprueba que tiene efecto real.
 *   syn                   comprueba cada sinergia: activa con "need" miembros, inactiva con need-1, y que sus reglas producen efecto.
 *   stress                todas las bendiciones al maximo durante muchos fotogramas: limites (dano, curacion, ejecuciones/s, invulnerabilidad) y rendimiento.
 *   build:<nombre>        una build jugable (lista de claves) con el bot jugando de verdad (ver builds()).
 */
final class BlessProbe {
    private BlessProbe() {}
    static final int SLOT = System.getenv("BOT_BLESSSLOT") != null ? Integer.parseInt(System.getenv("BOT_BLESSSLOT")) : 420;
    static int base = -1, idx = 0, slotT0 = 0;
    static boolean setup;
    static final List<Enemy> dummies = new ArrayList<>();
    static List<int[]> plan = new ArrayList<>();      // para "single": {id}; para "syn": {syn, miembros...}
    static String mode = "";
    static boolean[] modOn = new boolean[Blessing.ALL.length];
    static boolean[] modOnSyn = new boolean[64];
    static int fails = 0, oks = 0;
    // estres
    static float maxDmgMul, maxHealRoom, maxFrameMs; static int maxPerSec, invulFrames, frames, maxProj, maxEn; static double sumMs;
    static String projHist = ""; static float hpLostTotal, healSeen; static long t0, lastCall; static double sumFrame; static float maxFrame;

    static int idOf(String key) { Blessing b = Blessing.byKey(key.toLowerCase()); if (b == null) throw new IllegalArgumentException("clave desconocida " + key); return b.id; }

    static void init(String m) {
        mode = m;
        if (m.startsWith("single")) {
            int a = 0, b = Blessing.ALL.length - 1;
            int c = m.indexOf(':');
            if (c > 0) { String[] r = m.substring(c + 1).split("-"); a = Integer.parseInt(r[0]); b = Integer.parseInt(r[1]); }
            for (int i = a; i <= b; i++) plan.add(new int[]{i});
        } else if (m.equals("syn")) {
            BSyn[] s = BlessData.syns();
            for (BSyn x : s) { int[] p = new int[1 + x.need]; p[0] = x.id; for (int k = 0; k < x.need; k++) p[1 + k] = x.members[k]; plan.add(p); }
        }
    }

    static Enemy dummy(Level lv, int k, Player p) {
        Enemy e = new Enemy(EnemyDef.get("esqueleto"), k == 3, 1f, 1f);
        e.hp = e.maxHp = 1e7f;
        if (k == 3) e.hp = e.maxHp * 0.2f;
        float[] dx = {30f, -28f, 210f, 45f};
        e.x = p.x + dx[k]; e.y = p.y; e.vx = e.vy = 0; e.home = e.x; e.state = Enemy.CHASE;
        return e;
    }

    static void statuses(Enemy e, boolean all) {
        if (!all) return;
        for (int s : new int[]{Ent.BURN, Ent.FREEZE, Ent.SLOW, Ent.POISON, Ent.SHOCK, Ent.BLEED, Ent.CURSE}) { e.st[s] = 4f; e.stPow[s] = 4f; }
    }

    static void ensureDummies(Level lv, Player p) {
        for (int k = 0; k < 4; k++) {
            Enemy e = k < dummies.size() ? dummies.get(k) : null;
            if (e == null || !e.alive || lv.enemies.indexOf(e) < 0) {
                Enemy n = dummy(lv, k, p);
                if (e != null) { dummies.set(k, n); lv.enemies.remove(e); } else dummies.add(n);
                lv.enemies.add(n);
            }
        }
        lv.toKill = 999; lv.cleared = false;
    }

    static void grant(RunState r, int[] ids, int lvl) {
        java.util.Arrays.fill(r.bless, 0);
        for (int id : ids) r.bless[id] = Math.min(lvl, Blessing.ALL[id].max);
        r.bx = new BlessRt();
        BlessFx.sync(r);
        r.recalc();
    }

    static void driveEvents(Level lv, Player p, int f, boolean showModes) {
        RunState rs = lv.rs;
        BlessRt bx = rs.bx;
        // fases de estado del jugador
        int ph = (f / 25) % 4;
        rs.hp = ph == 1 || ph == 3 ? rs.stats.maxHp * 0.2f : rs.stats.maxHp;
        p.shield = ph >= 2 ? 20f : 0f;
        if ((f / 50) % 2 == 1) bx.arc = 10f;
        rs.potions = (f / 70) % 2 == 0 ? 0 : rs.stats.potionsMax;
        rs.ult = (f / 60) % 2 == 0 ? 100f : 10f;
        p.onGround = (f / 40) % 2 == 0;
        p.vx = (f / 30) % 2 == 0 ? 120f : 0f;
        if (f % 20 == 0) for (Enemy e : dummies) { e.st[Ent.BURN] = e.st[Ent.POISON] = 0; }
        for (int k = 0; k < dummies.size(); k++) { Enemy d = dummies.get(k); float[] dx = {30f, -28f, 210f, 45f}; d.x = p.x + dx[k]; d.vx = 0; d.right = true; }
        statuses(dummies.get(0), true);
        dummies.get(1).st[Ent.SLOW] = 4f; dummies.get(1).stPow[Ent.SLOW] = 2f;                 // solo ralentizado (sin congelar)
        dummies.get(2).st[Ent.POISON] = 4f; dummies.get(2).stPow[Ent.POISON] = 2f;
        if (f % 2 != 0) return;
        int h = (f / 2) % 27;
        Enemy e = dummies.get(((f / 2) / 27) % 4);
        boolean crit = ((f / 54) % 2) == 0;
        switch (h) {
            case 0: BlessFx.onRoomStart(lv); break;
            case 1: BlessFx.afterDamage(lv, e, 40f, crit, BlessFx.SRC_W); BlessFx.onHit(lv, e, 40f, crit, 1 + (f / 54) % 3);
                BlessFx.afterDamage(lv, dummies.get(0), 40f, crit, BlessFx.SRC_W); BlessFx.onHit(lv, dummies.get(0), 40f, crit, 2); break;
            case 2: BlessFx.afterDamage(lv, e, 40f, true, BlessFx.SRC_W); BlessFx.onHit(lv, e, 40f, true, 3); break;
            case 3: BlessFx.afterDamage(lv, e, 40f, crit, BlessFx.SRC_S); break;
            case 4: BlessFx.afterDamage(lv, e, 40f, crit, BlessFx.SRC_P); break;
            case 5: BlessFx.onKill(lv, e, BlessFx.SRC_W); break;
            case 6: BlessFx.onKill(lv, e, BlessFx.SRC_S); BlessFx.onKill(lv, e, BlessFx.SRC_P); break;
            case 7: BlessFx.onHurt(lv, 8f); lv.roomHits++; break;
            case 8: BlessFx.onBlocked(lv, 12f); break;
            case 9: BlessFx.onParry(lv); break;
            case 10: bx.dodgeLock = 0; BlessFx.onDodge(lv); break;
            case 11: BlessFx.onRoll(lv, false); break;
            case 12: BlessFx.onRoll(lv, true); break;
            case 13: BlessFx.onSkill(lv, 0); break;
            case 14: BlessFx.onSkill(lv, 1); break;
            case 15: BlessFx.onSkill(lv, 2); break;
            case 16: BlessFx.onUlt(lv, false); BlessFx.onUlt(lv, true); break;
            case 17: BlessFx.onPick(lv, 0); break;
            case 18: BlessFx.onPick(lv, 1); BlessFx.onPick(lv, 2); break;
            case 19: BlessFx.onPick(lv, 3); BlessFx.onPotion(lv); break;
            case 20: BlessFx.onOverflow(lv, 2); BlessFx.onOverflow(lv, 3); break;
            case 21: BlessFx.onJump(lv, false); BlessFx.onJump(lv, true); break;
            case 22: BlessFx.onLand(lv, 420f); break;
            case 23: lv.roomHits = 0; BlessFx.onCleared(lv); break;
            case 24: BlessFx.onBossDead(lv); break;
            case 25: BlessFx.onProjEnd(lv, e.cx(), e.cy(), BlessFx.SRC_P); break;
            default: break;
        }
        // condiciones de modificadores pasivos: se anota si alguna regla del propietario se cumple en algun contexto
        for (int s : new int[]{BlessFx.SRC_W, BlessFx.SRC_S, BlessFx.SRC_P, BlessFx.SRC_DOT, BlessFx.SRC_NONE})
            for (int m = 0; m < bx.mods.length; m++) for (BRule r : bx.mods[m]) {
                if (BlessFx.isStatic(r)) continue;
                for (Enemy d : dummies) if (BlessFx.check(lv, bx, r, d, s)) { if (r.owner >= 0) modOn[r.owner] = true; else if (r.syn >= 0) modOnSyn[r.syn] = true; }
            }
    }

    /** Devuelve true cuando ya no hay mas trabajo (el DebugBot termina entonces). */
    static boolean step(Game g, RunScreen rs, Level lv, Player p, int frame) {
        if (!setup) {
            setup = true; base = frame; slotT0 = frame;
            if (mode.isEmpty()) init(System.getenv("BOT_BLESSTEST"));
            lv.enemies.clear(); lv.projs.clear(); dummies.clear();
            t0 = System.nanoTime();
            System.out.println("BP modo " + mode + " plan=" + plan.size());
        }
        RunState r = rs.rs;
        p.invuln = Math.min(p.invuln, 0.001f);
        if (mode.equals("stress")) return stress(g, rs, lv, p, frame);
        if (mode.equals("ui")) return ui(g, rs, lv, p, frame);
        if (mode.equals("persist")) return persist(g, rs, lv, p, frame);
        int f = frame - slotT0;
        if (idx >= plan.size()) {
            System.out.println("BP FIN ok=" + oks + " fallos=" + fails);
            return true;
        }
        int[] pl = plan.get(idx);
        if (f == 0) {
            ensureDummies(lv, p);
            java.util.Arrays.fill(modOn, false); java.util.Arrays.fill(modOnSyn, false);
            if (mode.equals("syn")) {
                int[] mem = java.util.Arrays.copyOfRange(pl, 1, pl.length);
                grant(r, mem, 1);
            } else {
                boolean needSpirit = false;
                for (BRule q : Blessing.ALL[pl[0]].rules) for (int c : q.cond) if (c == BRule.C_P_SPIRIT) needSpirit = true;
                // las que dependen de tener un espiritu invocado se prueban junto a un espiritu (su sinergia natural con la categoria G)
                grant(r, needSpirit ? new int[]{pl[0], idOf("espiritu_rayo")} : new int[]{pl[0]}, 1);
            }
            lv.pl.alive = true;
            return false;
        }
        ensureDummies(lv, p);
        p.alive = true;
        driveEvents(lv, p, f, false);
        if (f < SLOT) return false;
        BlessRt bx = r.bx;
        if (mode.equals("syn")) {
            int s = pl[0];
            BSyn sy = BlessData.syns()[s];
            boolean on = bx.synOn[s];
            int fired = bx.firedSyn[s];
            boolean eff = fired > 0 || modOnSyn[s];
            for (BRule q : sy.rules) if (BlessFx.isStatic(q)) eff = true;
            // con need-1 miembros no debe activarse
            int[] fewer = java.util.Arrays.copyOfRange(pl, 1, pl.length - 1);
            grant(r, fewer, 1);
            boolean offOk = sy.need <= 1 || !r.bx.synOn[s];
            boolean ok = on && eff && offOk;
            System.out.println("BPSYN " + (ok ? "OK  " : "FALLA") + " syn=" + s + " " + sy.name + " need=" + sy.need + " miembros=" + sy.members.length + " activa=" + on + " disparos=" + fired + " mod=" + modOnSyn[s] + " apagadaConNeedMenos1=" + offOk);
            if (ok) oks++; else fails++;
        } else {
            int id = pl[0];
            Blessing b = Blessing.ALL[id];
            boolean eff = bx.fired[id] > 0 || modOn[id];
            boolean stat = false;
            for (BRule q : b.rules) if (BlessFx.isStatic(q)) stat = true;
            boolean ok = eff || stat || id < Blessing.LEGACY_COUNT;
            if (!ok && f < SLOT * 4) return false;      // reglas con probabilidad baja: se da mas tiempo (hasta 4x) antes de dar el fallo
            // las bendiciones antiguas tienen su efecto en Stats/Level (sin reglas): se comprueban aparte comparando Stats
            System.out.println("BP " + (ok ? "OK  " : "FALLA") + " id=" + id + " key=" + b.key + " nombre=" + b.name + " reglas=" + b.rules.length + " disparos=" + bx.fired[id] + " modCond=" + modOn[id] + " estatica=" + stat);
            if (ok) oks++; else fails++;
        }
        idx++; slotT0 = frame + 1;
        return false;
    }

    // ------------------------------------------------------------------ persistencia: guardar/cargar, cambio de sala, jefe, piso y partidas antiguas (28 entradas)
    static int pStep = 0, pT0 = 0; static int[] expect; static String pbefore = "";
    static void pck(String n, boolean ok) { System.out.println("BPPERSIST " + (ok ? "OK    " : "FALLA ") + n); if (!ok) fails++; else oks++; }
    static boolean persist(Game g, RunScreen rs, Level lv, Player p, int frame) {
        RunState r = rs.rs;
        if (pStep == 0) {
            int[] ids = {3, 40, 90, 150, 199, idOf("espiritu_rayo"), idOf("sinfonia_espiritual"), idOf("pastor_almas")};
            grant(r, ids, 2); r.bless[3] = 2;
            expect = r.bless.clone();
            pck("200 entradas y niveles concedidos", r.bless.length == 200 && r.bless[199] >= 1 && r.bless[3] == 2);
            pT0 = frame; pStep = 1; return false;
        }
        if (pStep == 1 && frame - pT0 > 60) {       // cambio de sala normal -> jefe
            rs.loadRoom(Room.BOSS);
            pStep = 2; pT0 = frame; return false;
        }
        if (pStep == 2 && frame - pT0 > 120) {
            RunState q = rs.rs;
            pck("tras cambiar a la sala del jefe las bendiciones siguen (iguales)", java.util.Arrays.equals(expect, q.bless));
            pck("el motor de reglas se reconstruyo y esta activo", q.bx != null && q.bx.any && q.bx.spirits.size() >= 1);
            int n0 = q.bx.spirits.size();
            q.stage++; rs.loadRoom(Room.COMBAT);     // cambio de piso
            pStep = 3; pT0 = frame; pbefore = "spirits=" + n0; return false;
        }
        if (pStep == 3 && frame - pT0 > 120) {
            RunState q = rs.rs;
            pck("tras cambiar de piso las bendiciones siguen y el motor sigue activo", java.util.Arrays.equals(expect, q.bless) && q.bx.any && q.bx.spirits.size() >= 1);
            pck("sin activaciones duplicadas: un espiritu por regla de espiritu (" + q.bx.spirits.size() + ")", q.bx.spirits.size() == q.bx.byTrig[BRule.T_SPIRIT].length);
            boolean w = RunSave.write(g.P, rs, RunSave.AUTO);
            pck("guardar partida con bendiciones nuevas", w);
            RunScreen n = RunSave.load(g, RunSave.AUTO);
            pck("cargar devuelve la misma partida y las mismas bendiciones", n != null && java.util.Arrays.equals(expect, n.rs.bless));
            if (n != null) { BlessFx.sync(n.rs); pck("tras cargar, las reglas y sinergias se reconstruyen igual", n.rs.bx != null && n.rs.bx.any && n.rs.bx.synCount == q.bx.synCount); }
            // partida antigua: solo 28 entradas
            String raw = g.P.store().get(RunSave.key(RunSave.AUTO), "");
            java.util.regex.Matcher m = java.util.regex.Pattern.compile("\"bless\":\\[([0-9,\\-]*)\\]").matcher(raw);
            if (m.find()) {
                String[] v = m.group(1).split(",");
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < 28; i++) { if (i > 0) sb.append(','); sb.append(v[i]); }
                g.P.store().put(RunSave.key(RunSave.AUTO), raw.substring(0, m.start(1)) + sb + raw.substring(m.end(1)));
                RunScreen o = RunSave.load(g, RunSave.AUTO);
                boolean same = o != null;
                if (o != null) for (int i = 0; i < 200; i++) if (o.rs.bless[i] != (i < 28 ? expect[i] : 0)) same = false;
                pck("partida antigua (28 entradas) carga sin perder las originales ni inventar nuevas", same);
                g.P.store().put(RunSave.key(RunSave.AUTO), raw);
            } else pck("se encontro el arreglo bless en el guardado", false);
            System.out.println("BPPERSIST FIN ok=" + oks + " fallos=" + fails);
            return true;
        }
        return false;
    }

    // ------------------------------------------------------------------ interfaz: cartas de altar (4 por pantalla) y lista de activas/sinergias, todas las paginas
    static int uiStep = 0;
    static boolean ui(Game g, RunScreen rs, Level lv, Player p, int frame) {
        RunState r = rs.rs;
        int f = frame - slotT0;
        if (f < 5) return false;
        if (f % 3 != 0) return false;
        int n = Blessing.ALL.length;
        int cards = (n + 3) / 4;
        if (uiStep == 0) { int[] all = new int[n]; for (int i = 0; i < n; i++) all[i] = i; grant(r, all, 1); }
        if (!PrepScreen.fitErrors.isEmpty()) { for (String e : PrepScreen.fitErrors) System.out.println("FIT " + e); fails += PrepScreen.fitErrors.size(); PrepScreen.fitErrors.clear(); }
        if (uiStep < cards) {
            int[] ids = new int[4]; for (int k = 0; k < 4; k++) ids[k] = Math.min(n - 1, uiStep * 4 + k);
            rs.dbgShowBless(ids);
        } else if (uiStep < cards + 200) {
            int t = uiStep - cards;
            rs.dbgShowList(0, 0);
            int pages = rs.dbgListPages();
            if (t >= pages) { uiStep = cards + 200; return false; }
            rs.dbgShowList(0, t);
        } else if (uiStep < cards + 200 + 6) {
            int t = uiStep - cards - 200;
            rs.dbgShowList(1, 0);
            int pages = rs.dbgListPages();
            rs.dbgShowList(1, Math.min(t, pages - 1));
        } else {
            System.out.println("BPUI fin cartas=" + cards + " idioma=" + I18n.code() + " desajustes=" + fails);
            return true;
        }
        uiStep++;
        return false;
    }

    // ------------------------------------------------------------------ builds jugables: BOT_BLESSGRANT=clave1,clave2,... concede esas bendiciones al empezar y el bot juega la partida de verdad
    static boolean granted; static int lastPrint = -9999;
    static int bossT0 = -1; static boolean bossDone;
    static void buildStep(RunScreen rs, int frame) {
        RunState r = rs.rs;
        if (rs.lv != null && rs.lv.boss != null) {
            if (bossT0 < 0) bossT0 = frame;
            if (!bossDone && !rs.lv.boss.alive) { bossDone = true; System.out.println("BUILD jefe derrotado en " + Math.round((frame - bossT0) / 60f) + " s de juego (vida del jugador " + Math.round(r.hp) + "/" + Math.round(r.stats.maxHp) + ")"); }
        }
        if (!granted && frame > 120) {
            granted = true;
            String[] ks = System.getenv("BOT_BLESSGRANT").isEmpty() ? new String[0] : System.getenv("BOT_BLESSGRANT").split(",");
            int lvl = System.getenv("BOT_BLESSLVL") != null ? Integer.parseInt(System.getenv("BOT_BLESSLVL")) : 2;
            int[] ids = new int[ks.length]; for (int i = 0; i < ks.length; i++) ids[i] = idOf(ks[i].trim());
            grant(r, ids, lvl);
            System.out.println("BUILD concedidas " + ks.length + " bendiciones nivel " + lvl + " sinergias activas=" + r.bx.synCount + " maxHp=" + Math.round(r.stats.maxHp));
        }
        if (granted && frame - lastPrint >= 900) {
            lastPrint = frame;
            int fired = 0; if (r.bx != null) for (int v : r.bx.fired) fired += v;
            int sf = 0; if (r.bx != null) for (int v : r.bx.firedSyn) sf += v;
            System.out.println("BUILD f=" + frame + " bioma=" + (r.biome == null ? "?" : r.biome.name) + " piso=" + r.stage + " sala=" + r.roomNo + " salasHechas=" + r.roomsDone + " bajas=" + r.kills + " vida=" + Math.round(r.hp) + "/" + Math.round(r.stats.maxHp) + " efectosBendiciones=" + fired + " efectosSinergia=" + sf + " sinergiasActivas=" + (r.bx == null ? 0 : r.bx.synCount) + " revividas=" + r.revivesUsed);
        }
    }

    // ------------------------------------------------------------------ estres: todas las bendiciones al maximo
    static boolean stress(Game g, RunScreen rs, Level lv, Player p, int frame) {
        RunState r = rs.rs;
        int f = frame - slotT0;
        int total = System.getenv("BOT_BLESSFRAMES") != null ? Integer.parseInt(System.getenv("BOT_BLESSFRAMES")) : 3000;
        if (f == 0) {
            ensureDummies(lv, p);
            int[] all = new int[Blessing.ALL.length]; for (int i = 0; i < all.length; i++) all[i] = i;
            if (System.getenv("BOT_BLESSBASE") != null) all = new int[0];
            String set = System.getenv("BOT_BLESSSET");
            if (set != null) { String[] ks = set.split(","); all = new int[ks.length]; for (int i = 0; i < ks.length; i++) all[i] = idOf(ks[i]); }
            grant(r, all, set != null ? 3 : 99);
            BlessFx.dbgNsUpdate = 0; BlessFx.dbgNsDraw = 0;
            r.hp = r.stats.maxHp;
            System.out.println("BPSTRESS inicio bendiciones=" + all.length + " sinergias activas=" + r.bx.synCount + " maxHp=" + Math.round(r.stats.maxHp));
            return false;
        }
        ensureDummies(lv, p);
        p.alive = true;
        BlessRt bx = r.bx;
        long a = System.nanoTime();
        if (lastCall != 0) { double fr = (a - lastCall) / 1e6; sumFrame += fr; maxFrame = Math.max(maxFrame, (float) fr); }
        lastCall = a;
        // en el estres NO se fuerzan los estados de vida del jugador: se mide curacion e invulnerabilidad reales
        int h = (f / 2) % 27;
        float hpKeep = r.hp;
        driveEvents(lv, p, f, false);
        // cada 90 fotogramas el jugador recibe un golpe real para medir la curacion y la invulnerabilidad reales
        if (f % 90 == 45) lv.hurtPlayer(15f, p.x - 20f, -1, 0);
        frames++;
        if (p.invuln > 0) invulFrames++;
        Enemy e0 = dummies.get(1);
        float dm = BlessFx.modDamage(lv, e0, 100f, false, BlessFx.SRC_W) / 100f;
        maxDmgMul = Math.max(maxDmgMul, dm);
        maxHealRoom = Math.max(maxHealRoom, bx.healRoom / Math.max(1f, r.stats.maxHp));
        maxPerSec = Math.max(maxPerSec, bx.perSecond);
        if (lv.projs.size() > maxProj) { StringBuilder hs = new StringBuilder(); int[] bySrc = new int[8]; for (Proj q : lv.projs) bySrc[Math.min(7, Math.max(0, q.src))]++; hs.append(java.util.Arrays.toString(bySrc)); projHist = hs.toString(); }
        maxProj = Math.max(maxProj, lv.projs.size()); maxEn = Math.max(maxEn, lv.enemies.size());
        double ms = (System.nanoTime() - a) / 1e6; sumMs += ms; maxFrameMs = Math.max(maxFrameMs, (float) ms);
        if (f >= total) {
            System.out.println("BPSTRESS fin frames=" + frames + " maxMultDanoModDamage=" + maxDmgMul + " (tope " + BlessFx.DMG_CAP + ") maxCuracionSalaPct=" + Math.round(maxHealRoom * 100) + " maxEjecucionesPorSeg=" + maxPerSec + " (tope 90) invulnerable=" + Math.round(100f * invulFrames / Math.max(1, frames)) + "% proyectilesMax=" + maxProj + " proyectilesPorFuente=" + projHist + " enemigosMax=" + maxEn + " msFotogramaMedio=" + String.format("%.2f", sumFrame / Math.max(1, frames)) + " msFotogramaMax=" + String.format("%.1f", maxFrame) + " msBendicionesUpdate=" + String.format("%.3f", BlessFx.dbgNsUpdate / 1e6 / Math.max(1, frames)) + " msBendicionesDibujo=" + String.format("%.3f", BlessFx.dbgNsDraw / 1e6 / Math.max(1, frames)) + " msSondaMedio=" + String.format("%.3f", sumMs / frames) + " msSondaMax=" + String.format("%.2f", maxFrameMs));
            return true;
        }
        return false;
    }
}
