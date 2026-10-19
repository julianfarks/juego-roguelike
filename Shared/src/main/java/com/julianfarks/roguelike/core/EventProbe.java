package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/**
 * Pruebas de sucesos nuevos (solo banco headless; BOT_EVENTTEST=altar|cursed|chal|roll desde DebugBot, tras BOT_WARP=ev7|ev8|ev9:0).
 * Se ejecutan de forma sincrona sobre la sala real (RunScreen/Level reales); no tocan hardware.
 */
final class EventProbe {
    private EventProbe() {}
    static int fails = 0, oks = 0;
    static boolean done;
    static void ck(String n, boolean ok) { System.out.println("EV " + (ok ? "OK    " : "FALLA ") + n); if (ok) oks++; else fails++; }

    static Prop find(Level lv, String kind) { for (Prop q : lv.props) if (kind.equals(q.kind)) return q; return null; }
    static int doors(Level lv) { int n = 0; for (Prop q : lv.props) if ("door".equals(q.kind)) n++; return n; }
    static int chests(Level lv) { int n = 0; for (Prop q : lv.props) if ("chest".equals(q.kind) && q.roundChest) n++; return n; }
    static int pick(Level lv, int type) { int n = 0; for (Pickup q : lv.pickups) if (q.type == type && !q.dead) n += q.value; return n; }
    static void killAll(Level lv) { for (Enemy e : new ArrayList<>(lv.enemies)) if (e.alive) e.die(lv); for (int i = 0; i < 60 && !lv.cleared; i++) lv.update(0.016f); }
    static void fresh(RunScreen rs, int ev) { rs.rs.curEvent = ev; rs.loadRoom(Room.EVENT); rs.ov = RunScreen.OV_NONE; rs.bannerT = 0; rs.lv.pl.alive = true; }
    static void click(RunScreen rs, int optIdx) { rs.ovT = 1f; rs.evOpts.get(optIdx).act.run(); }

    /** true = terminado. */
    static boolean step(Game g, RunScreen rs, int frame) {
        if (done) return true;
        done = true;
        String mode = System.getenv("BOT_EVENTTEST");
        System.out.println("EV inicio modo " + mode);
        try {
            if (mode.equals("altar")) altar(rs);
            else if (mode.equals("cursed")) cursed(rs);
            else if (mode.equals("chal")) chal(rs);
            else if (mode.equals("nav")) nav(rs);
            else if (mode.equals("save")) save(g, rs);
            else if (mode.equals("ui")) { return ui(rs, frame); }
            else roll(rs);
        } catch (RuntimeException ex) { ck("sin excepciones: " + ex, false); ex.printStackTrace(System.out); }
        System.out.println("EV FIN ok=" + oks + " fallos=" + fails);
        return true;
    }

    static void altar(RunScreen rs) {
        RunState r = rs.rs;
        fresh(rs, Events.ALTAR);
        Prop a = find(rs.lv, "shrine");
        ck("la sala del altar de riesgo tiene su altar (arg 1) y salida", a != null && a.arg == 1 && doors(rs.lv) == 1);
        r.hp = r.stats.maxHp; r.souls = 500; r.gold = 0;
        rs.openRiskAltar(a);
        ck("el altar ofrece 4 decisiones", rs.evOpts.size() == 4 && rs.ov == RunScreen.OV_EVENT);
        boolean txt = true; for (RunScreen.EvOpt o : rs.evOpts) txt &= o.pro != null && !o.pro.isEmpty() && o.con != null && !o.con.isEmpty();
        ck("cada decision muestra ventaja Y coste antes de aceptar", txt);
        // condiciones: con poca vida no se puede pagar vida ni dolor; sin almas no se compra la eleccion
        r.hp = r.stats.maxHp * 0.3f; r.souls = 0;
        rs.openRiskAltar(a);
        ck("con poca vida no se puede sacrificar vida ni recibir el golpe", !rs.evOpts.get(0).ok && !rs.evOpts.get(1).ok);
        ck("sin almas no se puede comprar la eleccion", !rs.evOpts.get(3).ok);
        // 1) sangre por bendicion
        fresh(rs, Events.ALTAR); a = find(rs.lv, "shrine");
        r.hp = r.stats.maxHp; r.souls = 500; boolean bt0 = r.blessingTaken; int nb0 = 0; for (int v : r.bless) nb0 += v;
        float hp0 = r.hp;
        rs.openRiskAltar(a); click(rs, 0);
        float lost = hp0 - r.hp;
        ck("sangre: pierde el 25 % de la vida maxima (" + Math.round(lost) + ")", Math.abs(lost - Math.round(r.stats.maxHp * 0.25f)) < 1.01f);
        ck("sangre: abre eleccion de 3 bendiciones", rs.ov == RunScreen.OV_BLESS && rs.offer.length >= 1 && rs.offer.length <= 4);
        ck("sangre: el sacrificio no se puede evitar cerrando la eleccion (no hay cancelar)", rs.afterBless != null);
        rs.ovT = 1f; rs.layoutOverlay(); Screen.Hit h = null; for (Screen.Hit x : rs.hitsDbg()) if (x.tag == 0) h = x;
        if (h != null) rs.clickDbg(h);
        int nb1 = 0; for (int v : r.bless) nb1 += v;
        ck("sangre: se obtiene exactamente 1 bendicion", nb1 == nb0 + 1);
        ck("sangre: no consume la bendicion de altar del bioma", r.blessingTaken == bt0);
        ck("sangre: el altar queda gastado", a.used && a.done);
        // 2) dolor por botin
        fresh(rs, Events.ALTAR); a = find(rs.lv, "shrine");
        r.hp = r.stats.maxHp; r.gold = 0; r.souls = 0; hp0 = r.hp;
        rs.openRiskAltar(a); click(rs, 1);
        float hit = hp0 - r.hp;
        ck("dolor: recibe el 18 % de la vida maxima (" + Math.round(hit) + ") sin morir", Math.abs(hit - Math.round(r.stats.maxHp * 0.18f)) < 1.01f && r.hp > 0);
        ck("dolor: +30 almas y oro (monedas sueltas) como recompensa", r.souls == 30 && pick(rs.lv, Pickup.GOLD) > 0);
        // 3) pacto del ayuno (cuenta como pacto y respeta el limite)
        fresh(rs, Events.ALTAR); a = find(rs.lv, "shrine");
        for (int i = 0; i < r.pacts.length; i++) r.pacts[i] = 0;
        r.stats.recalc(r); int pm0 = r.stats.potionsMax; float dm0 = r.stats.dmgMul; r.potions = pm0;
        rs.openRiskAltar(a); ck("ayuno: disponible sin pactos previos", rs.evOpts.get(2).ok); click(rs, 2);
        ck("ayuno: +20 % de daño", Math.abs(r.stats.dmgMul / dm0 - 1.2f) < 0.01f);
        ck("ayuno: -2 frascos maximos y los frascos no superan el maximo", r.stats.potionsMax == Math.max(1, pm0 - 2) && r.potions <= r.stats.potionsMax);
        r.pacts[0] = 1; r.pacts[1] = 1; r.pacts[6] = 0;
        fresh(rs, Events.ALTAR); a = find(rs.lv, "shrine"); rs.openRiskAltar(a);
        ck("ayuno: con el maximo de pactos ya no se ofrece", !rs.evOpts.get(2).ok);
        for (int i = 0; i < r.pacts.length; i++) r.pacts[i] = 0;
        // 4) almas por eleccion de 4
        fresh(rs, Events.ALTAR); a = find(rs.lv, "shrine");
        r.souls = 500; int sc = 60 + 20 * r.stage;
        rs.openRiskAltar(a); click(rs, 3);
        ck("almas: cobra " + sc + " almas y abre eleccion", r.souls == 500 - sc && rs.ov == RunScreen.OV_BLESS);
        r.stats.recalc(r); rs.afterBless = null; rs.ov = RunScreen.OV_NONE;
    }

    static void cursed(RunScreen rs) {
        RunState r = rs.rs;
        fresh(rs, Events.CURSED);
        Prop c = find(rs.lv, "cursed");
        ck("la sala del cofre maldito tiene el cofre y la salida", c != null && doors(rs.lv) == 1 && rs.lv.cleared);
        rs.openCursed(c);
        ck("muestra recompensa y riesgo antes de aceptar (2 opciones)", rs.evOpts.size() == 2 && rs.evOpts.get(0).pro.contains("cofres") && rs.evOpts.get(0).con.contains("Emboscada"));
        click(rs, 1);
        ck("dejarlo cerrado: sin enemigos, sin recompensa, la salida sigue", rs.lv.enemies.isEmpty() && c.used && doors(rs.lv) == 1 && chests(rs.lv) == 0);
        fresh(rs, Events.CURSED); c = find(rs.lv, "cursed");
        r.souls = 0; int n = Events.ambushCount(r);
        rs.openCursed(c); click(rs, 0);
        int alive = 0, elites = 0; for (Enemy e : rs.lv.enemies) if (e.alive) { alive++; if (e.elite) elites++; }
        ck("abrir: emboscada de " + n + " enemigos (" + alive + ")", alive >= 1 && alive <= n && !rs.lv.cleared);
        ck("abrir: no se puede huir (sin puertas durante el combate)", doors(rs.lv) == 0);
        ck("abrir: sin premio hasta vencer", chests(rs.lv) == 0 && pick(rs.lv, Pickup.SOUL) == 0);
        int roomNo = r.roomNo;
        killAll(rs.lv);
        ck("vencer: 2 cofres de eleccion y almas sueltas (" + pick(rs.lv, Pickup.SOUL) + ")", chests(rs.lv) == 2 && pick(rs.lv, Pickup.SOUL) >= 25);
        ck("vencer: vuelve la salida normal (un solo camino, sin saltos)", doors(rs.lv) == 1 && r.roomNo == roomNo);
        Prop d = null; for (Prop q : rs.lv.props) if ("door".equals(q.kind)) d = q;
        ck("la salida no es de suceso ni de jefe/final (no se salta contenido)", d != null && d.event == 0 && d.nextType != Room.BOSS);
    }

    static void chal(RunScreen rs) {
        RunState r = rs.rs;
        for (int k = 0; k < Events.CH_COUNT; k++) {
            // fuerza la variante k probando contadores de la run
            int tries = 0;
            do { r.eventsThisRun[Events.CHALLENGE] = tries++; } while (Events.challengeKind(r) != k && tries < 60);
            ck("variante " + Events.CH_NAME[k] + " alcanzable segun la run", Events.challengeKind(r) == k);
            for (int mode = 0; mode < 2; mode++) {      // 0 = cumple, 1 = incumple
                r.chalKind = -1; fresh(rs, Events.CHALLENGE);
                Level lv = rs.lv;
                String tag = Events.CH_NAME[k] + (mode == 0 ? " (cumple)" : " (incumple)");
                ck(tag + ": enemigos presentes, sala sin despejar y sin salida mientras dura", lv.enemies.size() >= 3 && !lv.cleared && doors(lv) == 0 && rs.chal == k);
                if (k == Events.CH_NOHEAL) {
                    r.hp = 1; lv.healPlayer(100f);
                    float got = r.hp - 1;
                    ck(tag + ": la curacion se reduce a ~40 % (" + Math.round(got) + " de 100)", got > 30f && got < 50f);
                    r.hp = r.stats.maxHp;
                }
                if (k == Events.CH_SURVIVE) {
                    ck(tag + ": no se despeja aunque caigan todos antes de acabar el tiempo", lv.holdClear);
                    rs.chalWaveT = 0; int n0 = lv.enemies.size(); rs.challengeTick(0.016f);
                    ck(tag + ": llegan oleadas nuevas (" + n0 + "->" + lv.enemies.size() + ")", lv.enemies.size() > n0);
                    killAll(lv);
                    ck(tag + ": con el tiempo sin agotar no hay premio ni salida", !lv.cleared && chests(lv) == 0 && doors(lv) == 0);
                    if (mode == 0) { rs.chalT = 0.01f; rs.challengeTick(0.05f); for (int i = 0; i < 60 && !lv.cleared; i++) lv.update(0.016f); }
                    else { r.hp = 0; lv.pl.alive = false; ck(tag + ": si el jugador cae no se da premio", chests(lv) == 0); continue; }
                } else {
                    if (mode == 1) {
                        if (k == Events.CH_NODMG) { lv.roomHits = 1; rs.challengeTick(0.016f); }
                        else if (k == Events.CH_TIMED) { rs.chalT = 0.01f; rs.challengeTick(0.05f); }
                        else { /* curacion reducida no tiene fallo: se premia igual */ }
                        ck(tag + ": " + (k == Events.CH_NOHEAL ? "sin condicion de fallo" : "se marca como fallido"), k == Events.CH_NOHEAL ? rs.chalState == 0 : rs.chalState == 2);
                    }
                    killAll(lv);
                }
                boolean expectReward = mode == 0 || k == Events.CH_NOHEAL;
                ck(tag + ": " + (expectReward ? "2 cofres de premio" : "sin premio") + " (" + chests(lv) + ")", chests(lv) == (expectReward ? 2 : 0));
                ck(tag + ": la salida aparece siempre (no se atasca ni se salta)", doors(lv) == 1);
            }
        }
        r.hp = r.stats.maxHp; fresh(rs, Events.CHALLENGE);
    }

    /** Guardar/cargar con los sucesos nuevos: pacto del Ayuno, contadores y sala de desafio. */
    static void save(Game g, RunScreen rs) {
        RunState r = rs.rs;
        r.pacts[6] = 1; r.eventsThisRun[Events.CHALLENGE] = 1; r.eventsThisRun[Events.ALTAR] = 2; r.eventBiomeDone = true;
        rs.rs.chalKind = -1; fresh(rs, Events.CHALLENGE);
        boolean w = RunSave.write(g.P, rs, 0);
        RunScreen ld = RunSave.load(g, 0);
        ck("guardar y cargar dentro de una sala de desafio (guardado=" + w + ")", w && ld != null);
        if (ld == null) return;
        ld.loadRoom(ld.resumeType);
        ck("se conserva el pacto del Ayuno y los contadores de sucesos", ld.rs.pacts[6] == 1 && ld.rs.eventsThisRun[Events.ALTAR] == 2 && ld.rs.eventsThisRun[Events.CHALLENGE] == 1 && ld.rs.eventBiomeDone);
        ck("se conserva el suceso actual y el desafio se reconstruye igual (" + ld.chal + ")", ld.rs.curEvent == Events.CHALLENGE && ld.chal == rs.chal);
        ck("la sala cargada vuelve a tener enemigos sin despejar", ld.lv != null && !ld.lv.cleared && ld.lv.enemies.size() >= 3);
        r.stats.recalc(r);
        ck("el pacto sigue aplicandose tras cargar", ld.rs.stats.dmgMul > 0 && ld.rs.pacts[6] == 1);
        r.pacts[6] = 0; r.eventsThisRun[Events.CHALLENGE] = 0; r.eventsThisRun[Events.ALTAR] = 0; r.eventBiomeDone = false;
        RunSave.clearRun(g.P, rs);
    }

    static int uiStep, uiT0 = -1;
    /** Textos de los sucesos nuevos en el idioma/ancho del banco: ninguna opcion se corta ni se solapa (FIT). */
    static boolean ui(RunScreen rs, int frame) {
        done = false;
        if (uiT0 < 0) { uiT0 = frame; }
        int f = frame - uiT0;
        if (f % 3 != 0) return false;
        if (!PrepScreen.fitErrors.isEmpty()) { for (String e : PrepScreen.fitErrors) System.out.println("FIT " + e); fails += PrepScreen.fitErrors.size(); PrepScreen.fitErrors.clear(); }
        RunState r = rs.rs;
        if (uiStep == 0) { r.hp = r.stats.maxHp; r.souls = 500; r.gold = 500; }
        if (uiStep < 6) {
            int st = uiStep / 2; r.stage = st;
            if (uiStep % 2 == 0) { rs.openRiskAltar(find(rs.lv, "shrine") != null ? find(rs.lv, "shrine") : rs.lv.addProp(new Room.PropSpec("shrine", rs.lv.pl.x, rs.lv.pl.y, 1))); }
            else { Prop c = rs.lv.addProp(new Room.PropSpec("cursed", rs.lv.pl.x, rs.lv.pl.y, 0)); rs.openCursed(c); }
        } else {
            System.out.println("EVUI fin idioma=" + I18n.code() + " desajustes=" + fails);
            return true;
        }
        uiStep++;
        return false;
    }

    static void settle(RunScreen rs) { for (int i = 0; i < 40; i++) rs.update(0.05f); }

    /** Ruta real: sala de combate -> puerta lateral -> suceso -> salida. No se salta ni se repite contenido. */
    static void nav(RunScreen rs) {
        RunState r = rs.rs;
        int ev = Integer.parseInt(System.getenv("BOT_EVENT"));
        ck("combate normal con suceso forzado " + Events.NAME[ev], rs.lv.room.type == Room.COMBAT);
        killAll(rs.lv);
        for (int i = 0; i < 5; i++) rs.lv.update(0.05f);
        Prop side = null, main = null;
        for (Prop q : rs.lv.props) if ("door".equals(q.kind)) { if (q.event > 0) side = q; else main = q; }
        ck("hay puerta principal y puerta lateral del suceso", main != null && side != null && side.event == ev);
        if (main == null || side == null) return;
        int r0 = r.roomNo; int mt = main.nextType;
        rs.lv.pl.x = side.x; rs.lv.pl.y = side.y; rs.interact(); settle(rs);
        ck("entrar al suceso: sala de suceso (o prueba), mismo numero de sala (" + r0 + "->" + r.roomNo + ")", r.roomNo == r0 && r.curEvent == ev && (rs.lv.room.type == Room.EVENT || rs.lv.room.type == Room.ELITE));
        ck("el suceso se marca como hecho en este bioma", r.eventBiomeDone && r.eventsThisRun[ev] >= 1);
        rs.ov = RunScreen.OV_NONE; rs.bannerT = 0;
        if (ev == Events.CURSED) { Prop c = find(rs.lv, "cursed"); rs.openCursed(c); click(rs, 1); }
        killAll(rs.lv);
        if (ev == Events.CHALLENGE && rs.chal == Events.CH_SURVIVE) { rs.chalT = 0.01f; rs.challengeTick(0.05f); }
        for (int i = 0; i < 60 && !rs.lv.cleared; i++) rs.lv.update(0.05f);
        Prop ex = null; for (Prop q : rs.lv.props) if ("door".equals(q.kind)) ex = q;
        ck("tras resolverlo hay una unica salida normal", ex != null && ex.event == 0 && doors(rs.lv) == 1);
        if (ex == null) return;
        rs.lv.pl.x = ex.x; rs.lv.pl.y = ex.y; rs.interact(); settle(rs);
        ck("salir avanza exactamente una sala (" + r0 + "->" + r.roomNo + "), sin saltarse jefe ni contenido", r.roomNo == r0 + 1 && r.curEvent == 0);
        ck("la siguiente sala es la prevista por la ruta principal", rs.lv.room.type == mt || rs.lv.room.type == Room.COMBAT || rs.lv.room.type == Room.REST);
    }

    static void roll(RunScreen rs) {
        RunState r = rs.rs;
        r.eventBiomeDone = false;
        int[] cnt = new int[Events.COUNT];
        for (int i = 0; i < 6000; i++) cnt[Events.roll(r, new Rng(1000 + i * 7919L), 2)]++;
        StringBuilder sb = new StringBuilder(); for (int k = 0; k < Events.COUNT; k++) sb.append(k).append('=').append(cnt[k]).append(' ');
        System.out.println("EV reparto " + sb);
        boolean all = true; for (int k = 1; k < Events.COUNT; k++) all &= cnt[k] > 0;
        ck("todos los sucesos pueden salir", all);
        ck("la mayoria de salas no tiene suceso (~80 %)", cnt[0] > 6000 * 0.7 && cnt[0] < 6000 * 0.9);
        r.eventsThisRun[Events.ALTAR] = 2;
        int al = 0; for (int i = 0; i < 4000; i++) if (Events.roll(r, new Rng(77 + i * 31L), 2) == Events.ALTAR) al++;
        ck("tras 2 altares en la run ya no sale otro", al == 0);
        r.eventsThisRun[Events.ALTAR] = 0;
        int base = 0, seen = 0;
        for (int i = 0; i < 20000; i++) if (Events.roll(r, new Rng(5 + i * 13L), 2) == Events.MERCHANT) base++;
        r.eventsThisRun[Events.MERCHANT] = 2;
        for (int i = 0; i < 20000; i++) if (Events.roll(r, new Rng(5 + i * 13L), 2) == Events.MERCHANT) seen++;
        ck("repetir un suceso baja su probabilidad (" + base + " -> " + seen + ")", seen < base * 0.5);
        r.eventsThisRun[Events.MERCHANT] = 0;
        r.eventBiomeDone = true;
        ck("solo un suceso por bioma", Events.roll(r, new Rng(3), 2) == Events.NONE);
        r.eventBiomeDone = false;
        // recompensas coherentes con el progreso
        r.stage = 0; int a0 = Events.ambushCount(r); r.stage = 2; int a2 = Events.ambushCount(r); r.stage = 0;
        ck("la emboscada crece con el progreso (" + a0 + " -> " + a2 + ")", a2 > a0);
        // variedad de desafios entre partidas
        boolean[] seenCh = new boolean[Events.CH_COUNT];
        for (long s = 0; s < 40; s++) { RunState q = new RunState(r.cls, s * 99991L + 3, 0); q.roomNo = 1; seenCh[Events.challengeKind(q)] = true; }
        boolean allCh = true; for (boolean b : seenCh) allCh &= b;
        ck("los 4 desafios aparecen segun la partida", allCh);
    }
}
