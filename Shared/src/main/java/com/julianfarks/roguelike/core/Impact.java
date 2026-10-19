package com.julianfarks.roguelike.core;

/**
 * Sensacion de impacto centralizada: cada golpe del jugador pasa por aqui con su tipo (ligero, pesado, critico, especial) y recibe una
 * respuesta distinta de pausa de impacto, sacudida, destello, particulas y sonido. Todo con presupuestos para que ulti + habilidades
 * simultaneas no acumulen particulas ni pausas (ver Level.hitstopSoft y el limite de particulas de ps).
 */
final class Impact {
    private Impact() {}
    static final int LIGHT = 0, HEAVY = 1, CRIT = 2, SPECIAL = 3;
    static final String[] NAME = {"ligero", "pesado", "critico", "especial"};

    private static final float[] HITSTOP = {0.040f, 0.075f, 0.090f, 0.060f};
    private static final float[] SHAKE = {1.2f, 2.6f, 3.2f, 2.2f};
    private static final int[] SPARKS = {5, 9, 12, 8};
    private static final float[] VOL = {0.70f, 1.00f, 1.00f, 0.85f};
    private static final float[] PITCH = {1.06f, 0.82f, 1.10f, 0.96f};

    /** Tipo de golpe del arma: remate del combo o ataque aereo cargado = pesado, critico manda sobre todo. */
    static int kindOfWeapon(boolean crit, int combo) { return crit ? CRIT : (combo == 3 ? HEAVY : LIGHT); }

    /** Color de las chispas segun el elemento activo en el enemigo (quemadura, hielo, rayo, veneno); si no hay, segun el tipo de golpe. */
    static int colorFor(Ent e, int kind) {
        if (e.st[Ent.BURN] > 0) return 0xFF9A3C;
        if (e.st[Ent.FREEZE] > 0 || e.st[Ent.SLOW] > 0) return 0xA8E8FF;
        if (e.st[Ent.SHOCK] > 0) return 0xF4F070;
        if (e.st[Ent.POISON] > 0) return 0x9CE060;
        return kind == CRIT ? 0xFFD25A : kind == HEAVY ? 0xFFE8C0 : 0xFFFFFF;
    }

    private static String elementSfx(Ent e) {
        if (e.st[Ent.BURN] > 0) return "hit_fire";
        if (e.st[Ent.FREEZE] > 0) return "hit_ice";
        if (e.st[Ent.SHOCK] > 0) return "hit_shock";
        return null;
    }

    /** Pose de impacto del objetivo (SOLO visual: no toca cajas de colision ni dano). Rellena out = {escalaX, escalaY, desplazamientoX}.
     *  Comprime en el sentido del golpe en el instante del contacto (se mantiene durante la pausa de impacto, porque lv.time se detiene) y
     *  rebota en ~0,16 s; en golpes pesados/criticos se anade una sacudida corta de perdida de equilibrio. */
    static boolean react(Level lv, Ent e, float[] out) {
        float age = lv.time - e.recAt;
        if (age < 0 || age > 0.16f || !e.alive) return false;
        float amp = AMP[e.recKind] * (e instanceof Boss ? 0.45f : 1f) * (Save.S.reduceFx ? 0.5f : 1f);
        float k = 1f - age / 0.16f;
        out[0] = 1f - amp * k; out[1] = 1f + amp * 0.8f * k;
        float shake = e.recKind == HEAVY || e.recKind == CRIT ? (float) Math.sin(age * 95f) * 1.6f * k : 0f;
        out[2] = e.recDir * amp * 9f * k + shake;
        return true;
    }
    private static final float[] AMP = {0.10f, 0.20f, 0.22f, 0.12f};

    /** Presupuesto de sonidos de impacto: como mucho 3 capas de golpe por ventana de 60 ms (varios enemigos a la vez no saturan el audio). */
    private static long sfxWin; private static int sfxN;
    static boolean sfxOkForTest() { return sfxOk(); }
    private static boolean sfxOk() {
        long now = System.currentTimeMillis();
        if (now - sfxWin > 60) { sfxWin = now; sfxN = 0; }
        return ++sfxN <= 3;
    }

    /** Respuesta completa a un golpe ya aplicado. {@code killed}: el golpe derroto al objetivo. */
    static void hit(Level lv, Ent e, int kind, float dir, boolean killed, String baseSfx) {
        lv.dbgImpacts++;
        e.recAt = lv.time; e.recDir = dir; e.recKind = kind;
        boolean boss = e instanceof Boss;
        float bm = boss ? 0.5f : 1f;                                  // los jefes: contundente pero sin quedar "congelados"
        // pausa de impacto: con presupuesto; los remates que matan dan un poco mas (sin pasarse)
        float hs = HITSTOP[kind] * bm + (killed && !boss && kind >= HEAVY ? 0.02f : 0f);
        lv.hitstopSoft(hs);
        lv.shake(SHAKE[kind] * (boss ? 0.7f : 1f), 0.12f);
        if (kind == CRIT && !Save.S.reduceFx) lv.flash(0xFFE8A0, 0.05f);
        // chispas con presupuesto segun la carga de particulas actual
        int live = lv.ps.count();
        float budget = live > 600 ? 0f : live > 420 ? 0.4f : 1f;
        int n = Math.round(SPARKS[kind] * budget * (Save.S.reduceFx ? 0.5f : 1f));
        int col = colorFor(e, kind);
        if (n > 0) lv.ps.burst(lv.rng, e.cx(), e.cy(), col, n, kind == HEAVY ? 150 : 115, kind == HEAVY ? 0.32f : 0.25f, kind == CRIT ? 2.5f : 2f, 200, true);
        // destello del sprite de impacto (el tipo decide la animacion; el pesado y el critico son mas grandes)
        float sc = kind == LIGHT ? 0.9f : kind == HEAVY ? 1.2f : kind == CRIT ? 1.3f : 1f;
        lv.fx("fx_hit", kind == CRIT ? "crit" : kind == HEAVY ? "big" : kind == SPECIAL ? "magic" : "spark", e.cx() - dir * 4, e.cy(), sc, 0, 0);
        if (kind >= HEAVY && budget > 0f) lv.fx("fx_ring", "pulse", e.cx(), e.cy(), kind == HEAVY ? 0.45f : 0.35f, col, Platform.ADD | Platform.TINT);
        // sonido proporcional: volumen y tono segun el tipo + capa elemental o metalica
        lastVol = VOL[kind]; lastPitch = PITCH[kind]; lastSparks = n;
        boolean loud = sfxOk();
        if (baseSfx != null && loud) Snd.sfx(baseSfx, VOL[kind], PITCH[kind] * (0.97f + lv.rng.f() * 0.06f), 0f);
        if (kind == HEAVY && loud) Snd.sfx("hit_stone", 0.55f, 0.9f, 0f);
        if (kind == CRIT && loud) Snd.sfx("hit_metal_" + (1 + lv.rng.i(2)), 0.45f, 1.25f, 0f);
        String es = elementSfx(e);
        if (es != null && lv.time - lastElemSfx > 0.18f) { lastElemSfx = lv.time; Snd.sfx(es, 0.35f, 1f, 0f); }
        if (killed && kind >= HEAVY) {                               // remate satisfactorio: mas chispas y, solo con elites o al limpiar la sala, un instante lento
            if (budget > 0f) lv.ps.burst(lv.rng, e.cx(), e.cy(), col, Save.S.reduceFx ? 4 : 8, 170, 0.4f, 2.5f, 120, true);
            if (e instanceof Enemy && (((Enemy) e).elite || lv.toKill <= 0)) lv.slowmo(0.10f, 0.5f);
        }
        if (kind >= CRIT && Save.S.vibOn) lv.P.vibrate(kind == CRIT ? 12 : 8);
    }
    private static float lastElemSfx = -9f;
    static float lastVol, lastPitch; static int lastSparks;      // para pruebas

    /** Parry perfecto: destello distintivo, chispas, sonido metalico, ralentizacion brevisima y ventana de contraataque. */
    static void perfectParry(Level lv, Player p, float fx, float fy) {
        lv.ps.burst(lv.rng, fx, fy, 0xFFFFFF, Save.S.reduceFx ? 6 : 14, 190, 0.35f, 2, 0, true);
        lv.ps.burst(lv.rng, fx, fy, 0xFFE070, Save.S.reduceFx ? 6 : 12, 130, 0.5f, 2.5f, 0, true);
        lv.fx("fx_ring", "pulse", fx, fy, 1.15f, 0xFFFFFF, Platform.ADD | Platform.TINT);
        lv.fx("fx_ring", "pulse", fx, fy, 0.7f, 0xFFE070, Platform.ADD | Platform.TINT);
        Snd.sfx("parry", 1f, 1f, 0f);
        Snd.sfx("hit_metal_2", 0.8f, 1.15f, 0f);
        lv.slowmo(0.14f, 0.35f);
        lv.counterT = 1.1f;                                          // contraataque: el siguiente golpe de arma hace +50 % y desequilibra
        registerDefense(lv, p);
    }

    /** Esquiva perfecta (rodar justo cuando iba a golpearte): efecto visual breve, ventana de contraataque corta. */
    static void perfectDodge(Level lv, Player p) {
        if (lv.time - lv.dodgeFxT < 0.5f) return;
        lv.dodgeFxT = lv.time;
        lv.fx("fx_ring", "pulse", p.x, p.y - 14, 0.7f, 0x9AE8FF, Platform.ADD | Platform.TINT);
        lv.ps.burst(lv.rng, p.x, p.y - 12, 0x9AE8FF, Save.S.reduceFx ? 3 : 8, 120, 0.3f, 2, 0, true);
        lv.text(p.x, p.y - p.bh - 10, "¡Esquiva!", 0x9AE8FF, false);
        Snd.sfx("en_dash", 0.45f, 1.5f, 0f);
        lv.counterT = Math.max(lv.counterT, 0.7f);
        registerDefense(lv, p);
    }

    /** Encadenar acciones defensivas precisas (4 s entre ellas): a la tercera, +12 % de velocidad de ataque durante 5 s. */
    private static void registerDefense(Level lv, Player p) {
        lv.defStreak++; lv.defT = 4f;
        if (lv.defStreak >= 3) {
            lv.defStreak = 0; lv.flowT = 5f;
            lv.text(p.x, p.y - p.bh - 24, "¡Ritmo!", 0xFFE070, true);
            lv.fx("fx_holy", "beam", p.x, p.y - 40, 0.6f, 0, 0);
            Snd.sfx("ui_pick_upgrade", 0.6f, 1.2f, 0f);
        }
    }
}
