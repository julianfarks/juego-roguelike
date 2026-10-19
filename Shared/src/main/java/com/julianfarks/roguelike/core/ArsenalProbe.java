package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * Pruebas automaticas del Arsenal (solo banco headless; BOT_ARSENAL=1 desde DebugBot). Usa el motor real: Level, Player, Input, RunScreen, RunSave.
 * NO son pruebas en un dispositivo Android ni en Windows real.
 * Se ejecuta de forma sincrona (avanza el nivel con lv.update) y termina el proceso con 0 si todo pasa.
 */
final class ArsenalProbe {
    private ArsenalProbe() {}
    static boolean done;
    static int fails, oks;
    static void ck(String n, boolean ok) { System.out.println("AT " + (ok ? "OK    " : "FALLA ") + n); if (ok) oks++; else fails++; }

    static Level lv; static Player p; static RunState rs; static RunScreen scr; static Input in; static Game game;

    static final java.util.IdentityHashMap<Enemy, Float> pin = new java.util.IdentityHashMap<>();
    static void fr(int n) { for (int i = 0; i < n; i++) { for (Enemy e : lv.enemies) { Float px = pin.get(e); if (px != null) { e.x = px; e.vx = 0; } } lv.update(1f / 60f); in.endFrame(); } }
    static void tap(int code) { in.key(code, true); fr(1); in.key(code, false); fr(1); }
    static void hold(int code, int frames) { in.key(code, true); fr(frames); in.key(code, false); fr(1); }

    static Enemy dummy(float dx) {
        Enemy e = new Enemy(EnemyDef.get("esqueleto"), false, 1f, 1f);
        e.hp = e.maxHp = 1e7f; e.x = p.x + dx; e.y = p.y; e.home = e.x; e.state = Enemy.PATROL; pin.put(e, e.x);
        lv.enemies.add(e); lv.toKill = 999; lv.cleared = false;
        return e;
    }

    static int weaponProps() { int n = 0; for (Prop q : lv.props) if (q.kind.equals("weapon") && !q.dead) n++; return n; }
    static Prop firstWeapon() { for (Prop q : lv.props) if (q.kind.equals("weapon") && !q.dead) return q; return null; }

    static void reset() {
        lv.enemies.clear(); lv.projs.clear(); lv.summons.clear(); lv.ps.clear(); lv.counterT = 0;
        for (Prop q : lv.props) if (q.kind.equals("weapon")) q.dead = true;
        lv.props.removeIf(q -> q.dead);
        p.invuln = 99f; p.secCd = 0; p.swapCd = 0; rs.hp = rs.stats.maxHp; p.alive = true;
        rs.sec = 0; rs.secAmmo = 0; rs.secLvl = 0; rs.secActive = false; java.util.Arrays.fill(rs.wState, 0); rs.unseen.clear();
    }

    static boolean step(Game g, RunScreen r, Level l, Player pl, int frame) {
        if (done) return true;
        game = g; scr = r; lv = l; p = pl; rs = r.rs; in = l.in;
        done = true;
        for (int c : new int[]{'A', 'D', 'W', 'S', 37, 38, 39, 40, 'J', 'K', 'R', 'E', 'C', 'L', 'I', 'U', 32}) g.key(c, false);
        System.out.println("AT inicio arsenal");
        try { run(); } catch (RuntimeException e) { e.printStackTrace(System.out); ck("sin excepciones durante las pruebas: " + e, false); }
        System.out.println("AT FIN ok=" + oks + " fallos=" + fails);
        return true;
    }

    static void run() {
        rs.recalc();
        // ---------------------------------------------------------------- 1. sin arma secundaria
        reset();
        tap('R');
        ck("sin secundaria: la tecla de cambio no hace nada (arma principal activa)", !rs.secActive && rs.sec == 0);
        Enemy dm = dummy(40);
        hold('J', 20);
        ck("sin secundaria: el ataque sigue siendo el de la clase (sin proyectiles)", lv.projs.isEmpty());

        // ---------------------------------------------------------------- 2. recoger la primera secundaria del suelo (sin recogida automatica)
        reset(); dm = dummy(200);
        Prop w = Arsenal.dropWeapon(lv, Items.SEC_BOW, 0, p.x + 6, p.y, false, true);
        fr(120);
        ck("arma en el suelo: pasar cerca / quedarse encima NO la recoge sola", rs.sec == 0 && !w.dead && weaponProps() == 1);
        ck("arma en el suelo: es interactuable (se puede inspeccionar con la tarjeta)", lv.nearestInteractable() == w);
        scr.interact();
        ck("primera secundaria: se equipa directamente (con su municion completa)", rs.sec == Items.SEC_BOW && rs.secAmmo == Items.SEC_AMMO[Items.SEC_BOW] && weaponProps() == 0);
        ck("primera secundaria: la principal sigue activa hasta cambiar", !rs.secActive);
        ck("primera secundaria: queda registrada como obtenida y nueva en el inventario", rs.wState[Items.SEC_BOW] == 1 && rs.unseen.contains("w:" + Items.SEC_BOW));

        // ---------------------------------------------------------------- 3. cambio de arma en combate
        float hp0 = rs.hp; int n0 = lv.projs.size(); int ammo0 = rs.secAmmo;
        tap('R');
        ck("cambio: la tecla activa la secundaria", rs.secActive);
        ck("cambio: no toca vida, municion ni proyectiles", rs.hp == hp0 && rs.secAmmo == ammo0 && lv.projs.size() == n0);
        fr(20);
        hold('J', 4);
        ck("secundaria activa: el boton de ataque dispara la secundaria (flecha en vuelo, municion -1)", rs.secAmmo == ammo0 - 1 && !lv.projs.isEmpty() && p.state != Player.ATK);
        fr(60);
        tap('R');
        ck("cambio de vuelta: arma principal activa", !rs.secActive);
        int pa = rs.secAmmo; lv.projs.clear(); fr(30);
        hold('J', 10);
        ck("principal activa: el ataque es el de la clase (no gasta municion, no dispara la secundaria)", rs.secAmmo == pa);

        // ---------------------------------------------------------------- 4. cambios repetidos: sin duplicar ni ataques extra
        reset(); rs.sec = Items.SEC_KNIFE; rs.secAmmo = 14; rs.wState[1] = 1; dummy(300);
        int toggles = 0; boolean prev = rs.secActive; int projsMax = 0;
        for (int i = 0; i < 120; i++) { in.key('R', true); fr(1); in.key('R', false); fr(1); if (rs.secActive != prev) { toggles++; prev = rs.secActive; } projsMax = Math.max(projsMax, lv.projs.size()); }
        ck("240 pulsaciones de cambio en 4 s: el cambio respeta su enfriamiento (" + toggles + " cambios, <= 17)", toggles <= 17 && toggles >= 8);
        ck("cambios repetidos: no se crean proyectiles, no se gasta municion", projsMax == 0 && rs.secAmmo == 14);
        // cambiar y atacar a la vez no dispara dos veces
        rs.secActive = false; p.swapCd = 0; p.secCd = 0; lv.projs.clear();
        in.key('R', true); in.key('J', true); fr(2); in.key('R', false); in.key('J', false); fr(1);
        ck("cambiar y atacar en el mismo fotograma: como mucho un disparo (" + (14 - rs.secAmmo) + ")", 14 - rs.secAmmo <= 1);

        // ---------------------------------------------------------------- 5. intercambio con el suelo
        reset(); dummy(300);
        rs.sec = Items.SEC_BOW; rs.secAmmo = 11; rs.wState[Items.SEC_BOW] = 1;
        float px0 = p.x;
        Prop w2 = Arsenal.dropWeapon(lv, Items.SEC_CHAKRAM, 0, p.x + 4, p.y, false, true);
        fr(70);
        scr.interact();
        Prop old = firstWeapon();
        ck("intercambio: la nueva queda equipada", rs.sec == Items.SEC_CHAKRAM && rs.secAmmo == Items.SEC_AMMO[Items.SEC_CHAKRAM]);
        ck("intercambio: la anterior queda en el suelo (nunca se destruye) con su municion", old != null && old.arg == Items.SEC_BOW && old.wAmmo == 11 && weaponProps() == 1);
        ck("intercambio: la anterior esta en un sitio seguro (suelo firme, sin pinchos ni pared, dentro del escenario)", old != null && Arsenal.spotOk(lv, old));
        ck("intercambio: inventario refleja equipada / en el suelo", rs.wState[Items.SEC_CHAKRAM] == 1 && rs.wState[Items.SEC_BOW] == 2);
        fr(10);
        scr.interact();
        ck("intercambio: una pulsacion seguida no devuelve el arma de golpe (bloqueo 0,7 s)", rs.sec == Items.SEC_CHAKRAM && weaponProps() == 1);
        fr(60);
        ck("estar encima del arma soltada no la recoge sola", rs.sec == Items.SEC_CHAKRAM);
        scr.interact();
        ck("recuperar el arma que se acaba de soltar", rs.sec == Items.SEC_BOW && rs.secAmmo == 11 && weaponProps() == 1 && firstWeapon().arg == Items.SEC_CHAKRAM);
        // 30 intercambios seguidos: siempre 1 en la mano + 1 en el suelo
        boolean inv = true; int cnt = 0;
        for (int i = 0; i < 30; i++) { fr(46); Prop q = firstWeapon(); scr.interact(); if (weaponProps() != 1 || rs.sec == 0) inv = false; cnt++; }
        ck("30 intercambios seguidos: siempre exactamente 1 arma en la mano y 1 en el suelo (sin duplicar ni perder)", inv && cnt == 30);
        int a = rs.sec; int b = firstWeapon().arg;
        ck("30 intercambios seguidos: son las mismas dos armas", (a == Items.SEC_BOW && b == Items.SEC_CHAKRAM) || (a == Items.SEC_CHAKRAM && b == Items.SEC_BOW));

        // arma repetida: mejora en vez de duplicar
        reset(); rs.sec = Items.SEC_SPEAR; rs.secAmmo = 3; rs.wState[Items.SEC_SPEAR] = 1;
        Arsenal.dropWeapon(lv, Items.SEC_SPEAR, 0, p.x + 2, p.y, false, true); fr(5);
        scr.interact();
        ck("arma repetida del suelo: mejora de nivel (sin segundo ejemplar)", rs.secLvl == 1 && weaponProps() == 0 && rs.sec == Items.SEC_SPEAR);

        // ---------------------------------------------------------------- 6. colocacion segura al soltar
        reset();
        int tx = (int) (p.x / Room.TS), ty = (int) ((p.y - 1) / Room.TS);
        // pinchos a ambos lados y pared pegada
        for (int dx = -3; dx <= 3; dx++) { if (dx == 0) continue; lv.room.set(tx + dx, ty, Room.SPIKE); }
        boolean allSafe = true; List<float[]> pos = new ArrayList<>();
        rs.sec = Items.SEC_KNIFE; rs.secAmmo = 5; rs.wState[1] = 1;
        for (int i = 0; i < 6; i++) {
            Prop d = Arsenal.dropWeapon(lv, 2 + i, 0, p.x, p.y, true, false);
            if (!Arsenal.spotOk(lv, d)) allSafe = false;
            pos.add(new float[]{d.x, d.y});
        }
        boolean distinct = true;
        for (int i = 0; i < pos.size(); i++) for (int j = i + 1; j < pos.size(); j++) if (Math.abs(pos.get(i)[0] - pos.get(j)[0]) < 12 && Math.abs(pos.get(i)[1] - pos.get(j)[1]) < 12) distinct = false;
        ck("6 armas soltadas en el mismo punto rodeado de pinchos: todas en sitio seguro", allSafe);
        ck("6 armas soltadas en el mismo punto: ninguna se apila sobre otra", distinct);
        for (int dx = -3; dx <= 3; dx++) lv.room.set(tx + dx, ty, Room.AIR);
        // borde del escenario
        reset(); float sx = p.x; p.x = 6; p.safeX = 6;
        Prop e1 = Arsenal.dropWeapon(lv, Items.SEC_AXE, 0, p.x, p.y, true, false);
        ck("soltar pegado al borde del escenario: queda dentro (x=" + Math.round(e1.x) + ")", e1.x >= 12 && e1.x <= lv.room.pixW - 12);
        p.x = sx; p.safeX = sx;

        // ---------------------------------------------------------------- 7. politica de limpieza al salir de la sala
        reset(); rs.sec = Items.SEC_KNIFE; rs.secAmmo = 5; rs.wState[1] = 1;
        Arsenal.dropWeapon(lv, Items.SEC_ORB, 0, p.x + 20, p.y, true, false); fr(100);
        ck("durante toda la sala el arma soltada sigue disponible (no desaparece sola)", weaponProps() == 1);
        String msg = Arsenal.leaveRoom(rs, lv);
        ck("al salir de la sala se avisa y el inventario la marca como dejada atras", msg != null && msg.contains("Orbe") && rs.wState[Items.SEC_ORB] == 3);

        // ---------------------------------------------------------------- 8. cada arma hace lo suyo
        for (int id = 1; id < Items.SEC_COUNT; id++) weapon(id);
        // diferencias reales (no solo color/nombre)
        boolean uniq = true;
        for (int i = 1; i < Items.SEC_COUNT; i++) for (int j = i + 1; j < Items.SEC_COUNT; j++)
            if (Items.SEC_DMG[i] == Items.SEC_DMG[j] && Items.SEC_SHOTS[i] == Items.SEC_SHOTS[j] && Items.SEC_CD[i] == Items.SEC_CD[j] && Items.SEC_RANGE[i] == Items.SEC_RANGE[j]) uniq = false;
        boolean icons = true; for (int i = 1; i < Items.SEC_COUNT; i++) if (!UI.hasIcon(Items.SEC_ICON[i])) icons = false;
        ck("las 10 armas tienen estadisticas distintas y su propio icono pixel art", uniq && icons);
        java.util.HashSet<String> sp = new java.util.HashSet<>(); for (int i = 1; i < Items.SEC_COUNT; i++) sp.add(Items.SEC_ICON[i]);
        ck("las 10 armas usan iconos distintos entre si", sp.size() == Items.SEC_COUNT - 1);

        // ---------------------------------------------------------------- 9. sin municion
        reset(); dummy(100); rs.sec = Items.SEC_KNIFE; rs.secAmmo = 1; rs.wState[1] = 1; rs.secActive = true; p.secCd = 0;
        hold('J', 3); fr(30);
        ck("el ultimo disparo gasta la municion", rs.secAmmo == 0);
        hold('J', 3);
        ck("sin municion con la secundaria activa: vuelve sola a la arma principal", !rs.secActive);

        // ---------------------------------------------------------------- 10. contraataque
        reset(); dummy(100); rs.sec = Items.SEC_BOLT; rs.secAmmo = 9; rs.wState[2] = 1;
        p.secCd = 0; lv.projs.clear(); Items.useSecondary(lv, p);
        float dNorm = lv.projs.get(0).dmg;
        fr(30); p.secCd = 0; lv.projs.clear(); lv.counterT = 1f; Items.useSecondary(lv, p);
        float dCnt = lv.projs.get(0).dmg;
        ck("contra a distancia: el disparo tras un parry hace +50% y consume la ventana (" + Math.round(dNorm) + " -> " + Math.round(dCnt) + ")", Math.abs(dCnt / dNorm - 1.5f) < 0.02f && lv.counterT <= 0);

        // ---------------------------------------------------------------- 11. bendiciones: las de proyectiles mejoran las armas que disparan proyectiles
        reset(); dummy(100);
        rs.sec = Items.SEC_BOLT; rs.secAmmo = 9; rs.wState[2] = 1; p.secCd = 0; lv.projs.clear(); Items.useSecondary(lv, p);
        float vx0 = Math.abs(lv.projs.get(0).vx); int pi0 = lv.projs.get(0).pierce;
        int pierceId = BlessProbe.idOf("punta_afilada");
        BlessProbe.grant(rs, new int[]{pierceId}, 1);
        fr(5); p.secCd = 0; lv.projs.clear(); Items.useSecondary(lv, p);
        Proj bp = lv.projs.get(0);
        ck("bendicion de proyectiles aplicada a la ballesta (velocidad/perforacion/tamaño modificados: vx " + Math.round(vx0) + "->" + Math.round(Math.abs(bp.vx)) + ", perf " + pi0 + "->" + bp.pierce + ")", Math.abs(bp.vx) != vx0 || bp.pierce != pi0 || bp.scale != 1f);
        BlessProbe.grant(rs, new int[0], 1);

        // ---------------------------------------------------------------- 12. cofres
        chestTests();

        // ---------------------------------------------------------------- 13. guardado
        saveTests();
    }

    /** Dispara el arma `id` contra un maniqui y comprueba su comportamiento propio. */
    static void weapon(int id) {
        reset();
        Enemy e = dummy(id == Items.SEC_EMBER ? 50 : id == Items.SEC_AXE ? 225 : 90);
        rs.sec = id; rs.secAmmo = Items.SEC_AMMO[id]; rs.wState[id] = 1; rs.secActive = true; p.secCd = 0; p.swapCd = 0;
        float hp0 = e.hp; int am0 = rs.secAmmo;
        Items.useSecondary(lv, p);
        String nm = Items.SEC_NAME[id];
        ck(nm + ": gasta 1 de municion al usarse", rs.secAmmo == am0 - 1);
        boolean[] hurt = {false};
        float expCd = (id <= 4 ? 0.32f : Items.SEC_CD[id]);
        ck(nm + ": fija su enfriamiento propio (" + String.format(java.util.Locale.ROOT, "%.2f", p.secCd) + " s)", Math.abs(p.secCd - expCd) < 0.011f);
        boolean spawned = id == Items.SEC_SUMMON ? lv.summons.size() == 1 : !lv.projs.isEmpty();
        ck(nm + ": crea " + (id == Items.SEC_SUMMON ? "un espiritu" : "su(s) proyectil(es)"), spawned);
        if (id == Items.SEC_CHAKRAM) {
            int firstShots = rs.secAmmo;
            fr(30); p.secCd = 0; Items.useSecondary(lv, p);
            ck(nm + ": solo uno en vuelo (el segundo lanzamiento no gasta municion)", rs.secAmmo == firstShots && lv.projs.size() == 1);
        }
        if (id == Items.SEC_BOW) {
            Proj pr = lv.projs.get(0); float d0 = pr.dmg; fr(40);
            ck(nm + ": el daño crece con la distancia recorrida (" + Math.round(d0) + " -> " + Math.round(pr.dmg) + ")", pr.dmg > d0 * 1.3f || pr.dead);
        }
        boolean hitAny = false; for (int i = 0; i < 150; i++) { fr(1); if (e.hp < hp0 || e.hp <= 0 || !lv.enemies.contains(e)) hitAny = true; }
        ck(nm + ": hace daño real al enemigo", hitAny);
        if (id == Items.SEC_CHAKRAM) {
            fr(120);
            ck(nm + ": regresa al jugador y desaparece al recogerlo (ni se pierde en una pared ni queda en vuelo)", !Arsenal.chakramOut(lv));
        }
        if (id == Items.SEC_EMBER) ck(nm + ": prende fuego", e.hasStatus(Ent.BURN) || e.hp < hp0);
        if (id == Items.SEC_SPEAR) {
            // atraviesa varios enemigos y gana daño
            reset(); for (int i = 0; i < 4; i++) dummy(60 + i * 28);
            rs.sec = id; rs.secAmmo = 6; p.secCd = 0; float[] h0 = new float[lv.enemies.size()]; for (int i = 0; i < h0.length; i++) h0[i] = lv.enemies.get(i).hp;
            Items.useSecondary(lv, p); fr(80);
            int hit = 0; for (int i = 0; i < h0.length; i++) if (lv.enemies.get(i).hp < h0[i]) hit++;
            ck(nm + ": atraviesa varios enemigos (golpeó a " + hit + " de 4)", hit >= 3);
        }
        if (id == Items.SEC_WAND) {
            reset(); Enemy t = dummy(70); rs.sec = id; rs.secAmmo = 18; p.secCd = 0;
            boolean burn = false, frz = false, stun = false;
            for (int i = 0; i < 3; i++) { t.st[Ent.BURN] = t.st[Ent.FREEZE] = t.st[Ent.STUN] = 0; p.secCd = 0; Items.useSecondary(lv, p); fr(22); burn |= t.st[Ent.BURN] > 0; frz |= t.st[Ent.FREEZE] > 0; stun |= t.st[Ent.STUN] > 0; }
            ck(nm + ": alterna fuego, hielo y rayo (quemar=" + burn + " congelar=" + frz + " aturdir=" + stun + ")", burn && frz && stun);
        }
        if (id == Items.SEC_SUMMON) {
            reset(); dummy(120); rs.sec = id; rs.secAmmo = 5; p.secCd = 0;
            Items.useSecondary(lv, p); p.secCd = 0; Items.useSecondary(lv, p); p.secCd = 0; Items.useSecondary(lv, p);
            ck(nm + ": maximo 2 espiritus a la vez (" + lv.summons.size() + ")", lv.summons.size() == 2);
            fr(60 * 11);
            ck(nm + ": los espiritus se disipan tras 10 s", lv.summons.isEmpty());
        }
    }

    static void chestTests() {
        // con secundaria equipada: pide confirmacion y permite rechazar sin perder opciones
        reset(); dummy(300);
        rs.sec = Items.SEC_KNIFE; rs.secAmmo = 7; rs.wState[1] = 1;
        ChestLoot.Reward[] offer = {ChestLoot.secNew(rs, Items.SEC_BOW, rs.rng), ChestLoot.secNew(rs, Items.SEC_SPEAR, rs.rng), ChestLoot.secNew(rs, Items.SEC_WAND, rs.rng)};
        scr.cOffer = offer; scr.cMode = ChestLoot.MODE_WEAPONS;
        scr.dbgChest(1); scr.dbgConfirm();
        ck("cofre de armas con secundaria equipada: NO la reemplaza sin consentimiento (abre la comparacion)", scr.ov == RunScreen.OV_WCMP && rs.sec == Items.SEC_KNIFE);
        scr.dbgWcmp(false);
        ck("rechazar el intercambio: vuelve a las 3 opciones y conserva la arma actual", scr.ov == RunScreen.OV_CHEST && scr.cOffer != null && scr.cOffer.length == 3 && rs.sec == Items.SEC_KNIFE && weaponProps() == 0);
        scr.dbgChest(1); scr.dbgConfirm(); scr.dbgWcmp(true);
        ck("aceptar el intercambio: equipa la elegida", rs.sec == Items.SEC_SPEAR && scr.ov == RunScreen.OV_NONE);
        Prop dr = firstWeapon();
        ck("aceptar el intercambio: la anterior (Cuchillos, 7 usos) queda en el suelo, no se pierde", dr != null && dr.arg == Items.SEC_KNIFE && dr.wAmmo == 7 && Arsenal.spotOk(lv, dr));
        // sin secundaria: se equipa directamente
        reset(); dummy(300);
        offer = new ChestLoot.Reward[]{ChestLoot.secNew(rs, Items.SEC_ORB, rs.rng), ChestLoot.secNew(rs, Items.SEC_AXE, rs.rng), ChestLoot.secNew(rs, Items.SEC_BOW, rs.rng)};
        scr.cOffer = offer; scr.cMode = ChestLoot.MODE_WEAPONS; scr.dbgChest(2); scr.dbgConfirm();
        ck("cofre de armas sin secundaria: se equipa directamente, sin pantalla extra", rs.sec == Items.SEC_BOW && scr.ov == RunScreen.OV_NONE && weaponProps() == 0);
        // duplicados: nunca se ofrece como arma nueva la que ya se lleva
        reset(); rs.sec = Items.SEC_BOW; rs.secAmmo = 4; rs.wState[5] = 1;
        boolean dupOffered = false; int ups = 0;
        for (int i = 0; i < 400; i++) for (ChestLoot.Reward x : ChestLoot.roll(rs, ChestLoot.MODE_WEAPONS, 3)) { if (x.kind == ChestLoot.K_SEC_NEW && x.id == rs.sec) dupOffered = true; if (x.kind == ChestLoot.K_SEC_UP) ups++; }
        ck("cofres: nunca ofrecen la misma arma como nueva; el duplicado se compensa con mejora (" + ups + " mejoras en 400 cofres)", !dupOffered && ups > 0);
    }

    static void saveTests() {
        reset();
        rs.sec = Items.SEC_CHAKRAM; rs.secAmmo = 9; rs.secLvl = 2; rs.secActive = true; rs.wState[Items.SEC_CHAKRAM] = 1; rs.wState[Items.SEC_BOW] = 3;
        rs.unseen.add("w:6"); rs.seen.add("w:5");
        boolean w = RunSave.write(game.P, scr, 1);
        RunScreen back = RunSave.load(game, 1);
        ck("guardado v2: escribe y carga la partida", w && back != null);
        if (back != null) {
            RunState b = back.rs;
            ck("guardado v2: conserva arma 2ª, municion, nivel, arma activa y estados de armas", b.sec == Items.SEC_CHAKRAM && b.secAmmo == 9 && b.secLvl == 2 && b.secActive && b.wState[Items.SEC_BOW] == 3 && b.wState[Items.SEC_CHAKRAM] == 1);
            ck("guardado v2: conserva objetos nuevos/vistos del inventario", b.unseen.contains("w:6") && b.seen.contains("w:5"));
        }
        // partida antigua (v1): sin las claves nuevas
        String raw = game.P.store().get(RunSave.key(1), "");
        Map<String, Object> d = Json.parseObj(raw);
        d.remove("ver"); d.remove("secAct"); d.remove("wst"); d.remove("unseen"); d.remove("seen");
        d.put("sec", 3.0); d.put("secAmmo", 5.0);
        String old = Json.write(d);
        game.P.store().put(RunSave.key(2), old);
        game.P.store().put(RunSave.key(2) + "_bak", "");
        RunScreen ol = RunSave.load(game, 2);
        ck("partida antigua (sin claves nuevas): carga sin error y conserva lo suyo", ol != null && ol.rs.sec == Items.SEC_AXE && ol.rs.secAmmo == 5 && !ol.rs.secActive && ol.rs.wState[Items.SEC_AXE] == 1);
        ck("partida antigua: se crea una copia de seguridad intacta antes de modificarla", old.equals(game.P.store().get(RunSave.key(2) + "_bak", "")));
        // id de arma fuera de rango (partida de otra version) no rompe
        d.put("sec", 99.0); game.P.store().put(RunSave.key(2), Json.write(d));
        RunScreen bad = RunSave.load(game, 2);
        ck("arma desconocida en el guardado: se ignora sin romper la partida", bad != null && bad.rs.sec == 0);
        game.P.store().put(RunSave.key(1), ""); game.P.store().put(RunSave.key(2), ""); game.P.store().put(RunSave.key(2) + "_bak", "");
    }
}
