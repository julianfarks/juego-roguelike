package com.julianfarks.roguelike.core;

/**
 * Prueba del cuerpo a cuerpo (BOT_MELEETEST=1, banco headless). Para el arma principal de la clase y para cada arma secundaria cuerpo a cuerpo,
 * coloca un maniqui inmovil a distintas distancias delante del jugador (de -8 px, solapado y un poco detras del centro, a lejos) y pulsa atacar
 * quieto y corriendo hacia el. Cuenta impactos por golpe (sin duplicados), comprueba que no golpea a traves de una pared ni a enemigos lejanos,
 * y prueba un enemigo que se mueve hacia el jugador y un cambio rapido de direccion.
 */
final class MeleeProbe {
    private MeleeProbe() {}
    static final int[] DIST = {-8, -4, 0, 4, 8, 12, 16, 20, 26, 32, 40, 56, 80};
    static int step = -1, t0, wi, di, mode, fails, hits, gx, gy, events;
    static float hp0, lastHp, px0; static int imp0;
    static Enemy dummy;
    static String row = "";
    static int[] weapons;
    static boolean arena;
    static final StringBuilder sum = new StringBuilder();

    static boolean done() { return step >= 999; }

    static void ok(boolean c, String m) { System.out.println("MELEE " + (c ? "OK    " : "FALLA ") + m); if (!c) fails++; }

    private static Enemy spawn(Level lv, float x, float y) {
        lv.enemies.clear(); lv.toKill = 0; lv.projs.clear();
        Enemy en = new Enemy(EnemyDef.get("zombi"), false, 1f, 1f);
        en.maxHp = en.hp = 1e7f; en.x = x; en.y = y; en.home = en.x; en.st[Ent.STUN] = 5f;
        lv.enemies.add(en); lv.toKill++; return en;
    }

    private static String wName(int w) { return w == 0 ? "principal" : Items.SEC_NAME[w]; }

    /** Devuelve true mientras controla el fotograma. */
    static boolean step(Game g, RunScreen rs, Level lv, Player p, int frame) {
        RunState r = rs.rs;
        if (step < 0) {
            if (frame < 700) return false;
            for (int c : new int[]{'A', 'D', 'S', 'W', 'J', 'K'}) g.key(c, false);
            java.util.List<Integer> l = new java.util.ArrayList<>(); l.add(0);
            for (int i = 1; i < Items.SEC_COUNT; i++) if (Wpn.of(i).melee()) l.add(i);
            weapons = new int[l.size()]; for (int i = 0; i < weapons.length; i++) weapons[i] = l.get(i);
            if (System.getenv("BOT_MELEEQUICK") != null) wi = weapons.length;
            step = 0; return true;
        }
        lv.rs.hp = lv.rs.stats.maxHp; p.invuln = 99f; lv.counterT = 0;
        Room rm = lv.room;
        if (!arena) {
            if (!(p.onGround && p.state <= Player.RUN)) return true;
            arena = true; gx = (int) (p.x / Room.TS); gy = (int) (p.y / Room.TS);
            for (int i = -10; i <= 20; i++) { rm.set(gx + i, gy, Room.SOLID); for (int j = 1; j <= 8; j++) rm.set(gx + i, gy - j, Room.AIR); }
            return true;
        }
        if (dummy != null && dummy.alive) {
            if (mode != 4) { dummy.st[Ent.STUN] = 5f; dummy.vx = 0; }
            if (lv.dbgImpacts != imp0) { events += lv.dbgImpacts - imp0; imp0 = lv.dbgImpacts; if (System.getenv("BOT_MELEEDBG2") != null) System.out.println("IMP w=" + wName(weapons[Math.min(wi, weapons.length - 1)]) + " d=" + DIST[di] + " f=" + (frame - t0) + " swCount=" + p.wfx.swCount + " swT=" + p.wfx.swT + " sw=" + p.wfx.sw); }
            if (System.getenv("BOT_MELEEDBG") != null && wi == 0 && mode == 0 && step == 2 && frame - t0 < 30) System.out.println("DBG d=" + DIST[di] + " f=" + (frame - t0) + " px=" + Math.round(p.x - px0) + " ex=" + Math.round(dummy.x - px0) + " ebw=" + dummy.bw + " right=" + p.right + " st=" + p.state + " anim=" + p.animName + " t=" + p.animT);
        }
        // escenario: wi (arma) x di (distancia) x mode (0 quieto, 1 corriendo); despues pruebas especiales
        if (wi >= weapons.length) return special(g, rs, lv, p, frame);
        int w = weapons[wi];
        switch (step) {
            case 0: {   // preparar
                g.key('J', false); g.key('D', false); g.key('A', false);
                p.x = gx * Room.TS + 8; p.y = gy * Room.TS; p.vx = 0; p.vy = 0; p.right = true; p.state = Player.IDLE; p.secCd = 0; p.swapCd = 0; p.wfx.reset();
                if (w == 0) { r.secActive = false; } else { r.sec = w; r.wState[w] = 1; r.secActive = true; r.secAmmo = 99; }
                p.safeX = p.x; p.safeY = p.y;
                if (mode == 1) g.key('D', true);
                dummy = null; lv.enemies.clear(); lv.toKill = 0;
                step = 1; t0 = frame; return true;
            }
            case 1: {   // corriendo: deja que alcance velocidad; quieto: espera a que asiente
                if (frame - t0 < (mode == 1 ? 14 : 6)) return true;
                dummy = spawn(lv, p.x + DIST[di], p.y); hp0 = lastHp = dummy.hp; events = 0; imp0 = lv.dbgImpacts; px0 = p.x; imp0 = lv.dbgImpacts;
                g.key('J', true); g.key('J', false);
                step = 2; t0 = frame; return true;
            }
            case 2: {
                if (frame - t0 == 4 && mode == 1) g.key('D', false);
                if (frame - t0 < 32) return true;
                boolean hit = dummy.hp < hp0;
                row += hit ? (events > 1 ? Integer.toString(Math.min(9, events)) : "X") : ".";
                hits += hit ? 1 : 0;
                int expectMax = w == 0 ? 1 : Wpn.of(w).hits;
                if (events > expectMax) ok(false, wName(w) + " dist " + DIST[di] + " modo " + mode + ": " + events + " impactos en un golpe (max " + expectMax + ")");
                di++;
                if (di >= DIST.length) {
                    System.out.println(String.format("MELEE %-22s %s |%s|", wName(w), mode == 0 ? "quieto  " : "corriendo", row));
                    sum.append(wName(w)).append(mode).append(':').append(row).append('\n');
                    row = ""; di = 0; mode++;
                    if (mode > 1) { mode = 0; wi++; }
                }
                step = 0; return true;
            }
        }
        return true;
    }

    static int sp = 0, st0;
    static float sx;

    private static boolean special(Game g, RunScreen rs, Level lv, Player p, int frame) {
        RunState r = rs.rs; Room rm = lv.room;
        switch (sp) {
            case 0: {   // pared entre el jugador y el enemigo
                g.key('D', false);
                r.secActive = false;
                p.x = gx * Room.TS + 8; p.y = gy * Room.TS; p.vx = 0; p.right = true; p.state = Player.IDLE;
                for (int j = 1; j <= 4; j++) rm.set(gx + 1, gy - j, Room.SOLID);
                dummy = spawn(lv, (gx + 2) * Room.TS + 6, p.y); hp0 = lastHp = dummy.hp; events = 0; imp0 = lv.dbgImpacts;
                st0 = frame; sp = 1; return true;
            }
            case 1: {
                if (frame - st0 == 4) { g.key('J', true); g.key('J', false); }
                if (frame - st0 == 50) {
                    float gap = dummy.x - dummy.bw / 2 - p.x;
                    ok(dummy.hp >= hp0, "pared de por medio (enemigo a " + Math.round(gap) + " px tras el muro): no recibe dano (" + (hp0 - dummy.hp > 0 ? "golpeado" : "intacto") + ")");
                    // secundaria cuerpo a cuerpo con la misma pared
                    r.sec = 23; r.secActive = true; p.secCd = 0; p.wfx.reset(); p.x = gx * Room.TS + 8; p.vx = 0; p.right = true;
                    hp0 = dummy.hp; g.key('J', true); g.key('J', false);
                }
                if (frame - st0 == 100) {
                    ok(dummy.hp >= hp0, "pared de por medio con " + Items.SEC_NAME[23] + ": no recibe dano");
                    for (int j = 1; j <= 4; j++) rm.set(gx + 1, gy - j, Room.AIR);
                    sp = 2; st0 = frame;
                }
                return true;
            }
            case 2: {   // enemigo que se mueve hacia el jugador mientras golpea (sin aturdir), arma principal
                r.secActive = false; p.x = gx * Room.TS + 8; p.vx = 0; p.right = true; p.state = Player.IDLE;
                dummy = spawn(lv, p.x + 34, p.y); dummy.st[Ent.STUN] = 0; hp0 = lastHp = dummy.hp; events = 0; imp0 = lv.dbgImpacts; mode = 4;
                st0 = frame; sp = 3; return true;
            }
            case 3: {
                dummy.st[Ent.STUN] = 5f; dummy.x -= 1.2f;     // se acerca a 72 px/s
                if (frame - st0 == 6) { g.key('J', true); g.key('J', false); }
                if (frame - st0 == 50) {
                    ok(dummy.hp < hp0 && events == 1, "enemigo acercandose (72 px/s) durante el golpe: impactos=" + events + " (1)");
                    sp = 4; st0 = frame; mode = 0;
                }
                return true;
            }
            case 4: {   // cambio rapido de direccion: mirando a la derecha, enemigo pegado a la izquierda, pulsa izquierda y atacar en el mismo instante
                p.x = gx * Room.TS + 8; p.vx = 0; p.right = true; p.state = Player.IDLE; r.secActive = false;
                dummy = spawn(lv, p.x - 10, p.y); hp0 = lastHp = dummy.hp; events = 0; imp0 = lv.dbgImpacts;
                g.key('A', true); g.key('J', true); g.key('J', false);
                st0 = frame; sp = 5; return true;
            }
            case 5: {
                if (frame - st0 == 3) g.key('A', false);
                if (frame - st0 == 45) {
                    ok(dummy.hp < hp0 && events == 1, "giro rapido (enemigo pegado a la espalda, izquierda + atacar): impactos=" + events + " (1)");
                    // corriendo hacia la derecha con un enemigo 24 px por detras: la zona cercana no da alcance hacia atras
                    // (quieto, el juego ya gira solo hacia el enemigo mas cercano a menos de 60 px: eso es intencionado)
                    p.x = gx * Room.TS + 8; p.vx = 135; p.right = true; p.state = Player.RUN; g.key('D', true);
                    dummy = spawn(lv, p.x - 24, p.y); hp0 = lastHp = dummy.hp; events = 0; imp0 = lv.dbgImpacts;
                    g.key('J', true); g.key('J', false);
                    st0 = frame; sp = 6;
                }
                return true;
            }
            case 6: {
                if (frame - st0 == 3) g.key('D', false);
                if (frame - st0 == 45) {
                    ok(dummy.hp >= hp0, "corriendo con un enemigo 24 px por detras: no recibe el golpe (la zona cercana no alcanza hacia atras)");
                    sp = 7;
                }
                return true;
            }
            default:
                System.out.println("MELEE resumen fallos=" + fails);
                step = 999; return false;
        }
    }
}
