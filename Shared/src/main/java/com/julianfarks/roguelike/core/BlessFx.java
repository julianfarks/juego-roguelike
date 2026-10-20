package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/**
 * Motor de bendiciones: recibe los eventos del combate (golpe, critico, baja, parry, esquiva, habilidad, sala...), busca las reglas de las bendiciones
 * y sinergias activas y las ejecuta (BlessEffects) respetando condiciones, tiempos de reutilizacion, probabilidades y topes.
 *
 * Reglas de seguridad (evitan bucles infinitos y numeros desbocados):
 *  - un efecto NUNCA desencadena otros efectos (profundidad 0), salvo las bajas encadenadas (profundidad maxima 3, acotadas por los enemigos vivos);
 *  - cada regla tiene tiempo de reutilizacion (icd) y todas juntas un tope de ejecuciones por segundo;
 *  - los multiplicadores de dano de las bendiciones nuevas no superan x3; los canales temporales tienen tope propio (BlessRt.ch);
 *  - la curacion (por sala), el oro, las almas y la reduccion de reutilizacion tienen presupuesto.
 * Si el jugador no tiene ninguna bendicion nueva, todos los ganchos salen en la primera comprobacion.
 */
public final class BlessFx {
    private BlessFx() {}

    public static final int SRC_NONE = 0, SRC_W = 1, SRC_S = 2, SRC_P = 3, SRC_DOT = 4, SRC_COMP = 5, SRC_X = 6;
    static final float DMG_CAP = 3.0f;
    static long dbgNsUpdate, dbgNsDraw;                       // medicion de rendimiento (banco de pruebas)

    static BlessRt rt(RunState rs) { if (rs.bx == null) rs.bx = new BlessRt(); return rs.bx; }

    /** Un modificador es estatico (se pliega en Stats al recalcular) si no depende de condiciones ni de la fuente del dano. */
    static boolean isStatic(BRule r) { return r.cond.length == 0 && r.src == 0; }

    static float sv(RunState rs, int m) { BlessRt b = rs.bx; return b == null ? 0f : b.sv[m - 60]; }

    static int lvl(RunState rs, BRule r) { return r.owner >= 0 ? Math.max(1, rs.bless[r.owner]) : 1; }

    static float mag(RunState rs, BRule r) { return r.scale ? lvl(rs, r) : 1f; }

    // ------------------------------------------------------------------ sincronizacion con las bendiciones poseidas
    /** Reconstruye las reglas activas si cambio el conjunto de bendiciones. Barato: una pasada por 200 enteros. */
    static void sync(RunState rs) {
        BlessRt bx = rt(rs);
        long sig = 17;
        int[] b = rs.bless;
        for (int i = 0; i < b.length; i++) if (b[i] > 0) sig = sig * 131 + i * 7L + b[i];
        if (sig == bx.sig) return;
        bx.sig = sig;
        List<BRule>[] lists = newLists(BRule.T_COUNT);
        List<BRule>[] ml = newLists(48);
        java.util.Arrays.fill(bx.synOn, false);
        bx.synCount = 0;
        bx.any = false;
        for (int i = 0; i < b.length && i < Blessing.ALL.length; i++) {
            if (b[i] <= 0) continue;
            for (BRule r : Blessing.ALL[i].rules) { add(lists, ml, r); bx.any = true; }
        }
        BSyn[] syns = BlessData.syns();
        for (int s = 0; s < syns.length; s++) {
            int have = 0;
            for (int id : syns[s].members) if (id >= 0 && id < b.length && b[id] > 0) have++;
            if (have >= syns[s].need) {
                bx.synOn[s] = true; bx.synCount++;
                for (BRule r : syns[s].rules) { add(lists, ml, r); bx.any = true; }
            }
        }
        for (int t = 0; t < BRule.T_COUNT; t++) bx.byTrig[t] = lists[t].toArray(new BRule[0]);
        for (int m = 0; m < 48; m++) bx.mods[m] = ml[m].toArray(new BRule[0]);
        // espiritus: uno por regla SPIRIT activa (se conservan los que ya existian para no reiniciar su fase)
        List<BlessRt.Spirit> keep = new ArrayList<>(bx.spirits);
        bx.spirits.clear();
        for (BRule r : bx.byTrig[BRule.T_SPIRIT]) {
            BlessRt.Spirit sp = null;
            for (BlessRt.Spirit k : keep) if (k.rule == r) { sp = k; break; }
            if (sp == null) { sp = new BlessRt.Spirit(); sp.rule = r; sp.owner = r.owner; sp.cd = Math.max(1.2f, r.a[0] * 0.5f); sp.phase = bx.spirits.size() * 2.1f; sp.color = spiritColor(r); }
            bx.spirits.add(sp);
        }
    }

    static int spiritColor(BRule r) {
        int st = (int) r.a[2];
        switch (r.eff) {
            case BRule.E_SPIRIT_NOVA: return 0x7AC8F0;
            case BRule.E_SPIRIT_CHAIN: return 0xF0F060;
            case BRule.E_SPIRIT_MARK: return 0xAA6EFF;
            case BRule.E_SPIRIT_HEAL: return 0x6AE08A;
            case BRule.E_SPIRIT_GUARD: return 0x9AE0FF;
            default: return st == Ent.BURN ? 0xFF8A30 : st == Ent.POISON ? 0x6AE08A : st == Ent.SLOW || st == Ent.FREEZE ? 0x7AC8F0 : 0xFFE8A0;
        }
    }

    @SuppressWarnings("unchecked")
    private static List<BRule>[] newLists(int n) { List<BRule>[] a = new List[n]; for (int i = 0; i < n; i++) a[i] = new ArrayList<>(); return a; }

    private static void add(List<BRule>[] lists, List<BRule>[] ml, BRule r) {
        if (r.trig == BRule.T_MOD) ml[r.eff - 60].add(r); else lists[r.trig].add(r);
    }

    /** Aplica a Stats los modificadores pasivos sin condicion (se llama desde Stats.recalc). */
    static void applyStats(RunState rs, Stats st) {
        sync(rs);
        BlessRt bx = rs.bx;
        java.util.Arrays.fill(bx.sv, 0f);
        if (!bx.any) return;
        for (int m = 0; m < 48; m++) for (BRule r : bx.mods[m]) {
            if (!isStatic(r)) continue;
            bx.sv[m] += r.a[0] * mag(rs, r);
        }
        float[] v = bx.sv;
        st.maxHp *= Math.max(0.3f, 1f + v[BRule.M_MAXHP - 60]);
        st.dmgMul *= Math.max(0.3f, 1f + v[BRule.M_DMG - 60]);
        st.critChance += v[BRule.M_CRIT - 60];
        st.critMul += v[BRule.M_CRITMUL - 60];
        st.speedMul *= Math.max(0.4f, 1f + v[BRule.M_SPEED - 60]);
        st.dmgTaken = Math.max(0.2f, st.dmgTaken * Math.max(0.3f, 1f + v[BRule.M_TAKEN - 60]));
        st.skillDmg *= Math.max(0.3f, 1f + v[BRule.M_SKILLDMG - 60]);
        st.cdMul = Math.max(0.35f, st.cdMul * Math.max(0.3f, 1f + v[BRule.M_CDMUL - 60]));
        st.goldMul *= Math.max(0.2f, 1f + v[BRule.M_GOLDMUL - 60]);
        st.soulMul *= Math.max(0.2f, 1f + v[BRule.M_SOULMUL - 60]);
        st.ultGain *= Math.max(0.3f, 1f + v[BRule.M_ULTGAIN - 60]);
        st.lifesteal += v[BRule.M_LIFESTEAL - 60];
        st.potionsMax = Math.max(1, st.potionsMax + Math.round(v[BRule.M_POTMAX - 60]));
        st.luck += Math.round(v[BRule.M_LUCK - 60]);
        st.atkSpd *= Math.max(0.3f, 1f + v[BRule.M_ATKSPD - 60]);
        st.magnet *= 1f;
    }

    // ------------------------------------------------------------------ condiciones
    private static final java.util.Random NOP = null;

    static boolean check(Level lv, BlessRt bx, BRule r, Ent v, int src) {
        RunState rs = lv.rs; Player p = lv.pl;
        for (int i = 0; i < r.cond.length; i++) {
            boolean ok = one(lv, bx, rs, p, r.cond[i], r.cval[i], v, src);
            if (ok == r.neg[i]) return false;
        }
        return true;
    }

    private static int statusCount(Ent e) {
        int n = 0;
        for (int s : new int[]{Ent.BURN, Ent.FREEZE, Ent.SLOW, Ent.POISON, Ent.SHOCK, Ent.BLEED, Ent.CURSE}) if (e.st[s] > 0) n++;
        return n;
    }

    private static boolean one(Level lv, BlessRt bx, RunState rs, Player p, int c, float val, Ent v, int src) {
        switch (c) {
            case BRule.C_V_BURN: return v != null && v.st[Ent.BURN] > 0;
            case BRule.C_V_FREEZE: return v != null && v.st[Ent.FREEZE] > 0;
            case BRule.C_V_SLOW: return v != null && (v.st[Ent.SLOW] > 0 || v.st[Ent.FREEZE] > 0);
            case BRule.C_V_SHOCK: return v != null && v.st[Ent.SHOCK] > 0;
            case BRule.C_V_POISON: return v != null && v.st[Ent.POISON] > 0;
            case BRule.C_V_BLEED: return v != null && v.st[Ent.BLEED] > 0;
            case BRule.C_V_CURSE: return v != null && v.st[Ent.CURSE] > 0;
            case BRule.C_V_STUN: case BRule.C_V_STUNNED: return v != null && (v.st[Ent.STUN] > 0 || v.stun > 0);
            case BRule.C_V_STATUS: return v != null && statusCount(v) > 0;
            case BRule.C_V_MULTI: return v != null && statusCount(v) >= (int) val;
            case BRule.C_V_LOW: return v != null && v.maxHp > 0 && v.hp / v.maxHp < 0.3f;
            case BRule.C_V_HIGH: return v != null && v.maxHp > 0 && v.hp / v.maxHp >= 0.8f;
            case BRule.C_V_FULL: return v != null && v.maxHp > 0 && v.hp / v.maxHp >= 0.999f;
            case BRule.C_V_ELITE: return v instanceof Boss || (v instanceof Enemy && ((Enemy) v).elite);
            case BRule.C_V_BOSS: return v instanceof Boss;
            case BRule.C_V_AIR: return v != null && !v.onGround && !v.flying;
            case BRule.C_V_BACK: return v != null && p != null && (v.right == (v.x >= p.x)) && !(v instanceof Boss);
            case BRule.C_V_ALONE: return v != null && countNear(lv, v, 80f) == 0;
            case BRule.C_V_CROWD: return v != null && countNear(lv, v, 90f) >= 2;
            case BRule.C_V_FAR: return v != null && p != null && Mth.dist(p.x, p.cy(), v.cx(), v.cy()) > 120f;
            case BRule.C_P_LOW: return rs.hp / Math.max(1f, rs.stats.maxHp) < 0.35f;
            case BRule.C_P_HIGH: return rs.hp / Math.max(1f, rs.stats.maxHp) >= 0.9f;
            case BRule.C_P_HALF: return rs.hp / Math.max(1f, rs.stats.maxHp) < 0.5f;
            case BRule.C_P_SHIELD: return p != null && p.shield > 0;
            case BRule.C_P_AIR: return p != null && !p.onGround;
            case BRule.C_P_ROLL: return p != null && p.rolling();
            case BRule.C_P_GUARD: return p != null && p.guarding;
            case BRule.C_P_MOVING: return p != null && Math.abs(p.vx) > 40f;
            case BRule.C_P_STILL: return p != null && Math.abs(p.vx) < 12f;
            case BRule.C_P_ARC: return bx.arc >= val;
            case BRule.C_P_STREAK: return bx.hitStreak >= val;
            case BRule.C_P_BUFF: return bx.chOn((int) val);
            case BRule.C_P_CDALL: return rs.cd[0] > 0 && rs.cd[1] > 0 && rs.cd[2] > 0;
            case BRule.C_P_ULT: return rs.ult >= 100f;
            case BRule.C_P_NOPOT: return rs.potions <= 0;
            case BRule.C_P_POTFULL: return rs.potions >= rs.stats.potionsMax;
            case BRule.C_P_HPFULL: return rs.hp >= rs.stats.maxHp - 0.5f;
            case BRule.C_P_NOROOMHIT: return lv.roomHits == 0;
            case BRule.C_P_COMBO: return p != null && p.combo >= (int) val;
            case BRule.C_P_GOLD: return rs.gold >= (int) val;
            case BRule.C_P_SPIRIT: return !bx.spirits.isEmpty();
            case BRule.C_P_CRITS: return bx.critStreak >= (int) val;
            case BRule.C_P_PARRIES: return bx.parryStreak >= (int) val;
            case BRule.C_P_KILLS: return rs.kills >= (int) val;
            case BRule.C_R_BOSS: return lv.room.type == Room.BOSS;
            case BRule.C_R_COMBAT: return lv.room.type != Room.BOSS && !lv.cleared;
            case BRule.C_S_W: return src == SRC_W;
            case BRule.C_S_S: return src == SRC_S;
            case BRule.C_S_P: return src == SRC_P;
            case BRule.C_S_DOT: return src == SRC_DOT;
            case BRule.C_S_ANY: return true;
            case BRule.C_SYN: return bx.synOn[(int) val];
            default: return false;
        }
    }

    static int countNear(Level lv, Ent v, float r) {
        int n = 0;
        for (Enemy e : lv.enemies) if (e != v && e.alive && Mth.dist(e.cx(), e.cy(), v.cx(), v.cy()) < r) n++;
        return n;
    }

    // ------------------------------------------------------------------ modificadores dinamicos (con condiciones)
    private static BlessRt live(Level lv) {
        BlessRt b = lv.rs.bx;
        return b != null && b.any ? b : null;
    }

    /** Multiplicador de dano de las bendiciones que se aplica a TODO el dano del jugador a un enemigo. */
    static float modDamage(Level lv, Ent e, float dmg, boolean crit, int src) {
        float m = 1f;
        if (e.st[Ent.CURSE] > 0) m *= 1.2f;                       // maldito: recibe +20% del jugador
        BlessRt bx = live(lv);
        if (bx == null) return dmg * m;
        boolean player = src == SRC_W || src == SRC_S || src == SRC_P;
        RunState rs = lv.rs;
        float bm = 1f;
        for (BRule r : bx.mods[BRule.M_DMG - 60]) {
            if (isStatic(r)) continue;
            if (r.src != 0 && r.src != src) continue;
            if (check(lv, bx, r, e, src)) bm *= 1f + r.a[0] * mag(rs, r);
        }
        if (src == SRC_S) {
            for (BRule r : bx.mods[BRule.M_SKILLDMG - 60]) if (!isStatic(r) && check(lv, bx, r, e, src)) bm *= 1f + r.a[0] * mag(rs, r);
            bm *= 1f + bx.ch(BRule.CH_SKILL);
            if (bx.skillMulT > 0) bm *= 1f + bx.skillMul;
        }
        if (player) {
            bm *= 1f + bx.ch(BRule.CH_DMG);
            if (!crit) for (BRule r : bx.mods[BRule.M_NONCRIT - 60]) bm *= 1f + r.a[0] * mag(rs, r);
            if (src == SRC_P) {
                for (BRule r : bx.mods[BRule.M_PROJDMG - 60]) if (check(lv, bx, r, e, src)) bm *= 1f + r.a[0] * mag(rs, r);
                if (e.focusT > 0) bm *= 1f + Math.min(5, e.focusN) * focusStep(bx);
            }
            if (src == SRC_W && bx.nextHitT > 0 && bx.depth == 0) { bm *= 1f + bx.nextHitMul; bx.nextHitT = 0; bx.nextHitMul = 0; }
        }
        bm = Math.min(bm, DMG_CAP);
        return dmg * m * bm;
    }

    /** Critico seguro del siguiente golpe de arma (NEXTHIT con tercer argumento). */
    static boolean forcedCrit(Level lv, int src) {
        BlessRt bx = live(lv);
        return bx != null && src == SRC_W && bx.nextHitT > 0 && bx.nextHitCrit;
    }

    /** Fin de trayecto de un proyectil del jugador (los creados por bendiciones no disparan nada: sin bucles). */
    static void onProjEnd(Level lv, float x, float y, int src) {
        BlessRt bx = live(lv);
        if (bx == null) return;
        fire(lv, BRule.T_PROJEND, null, 0, false, src, x, y);
    }

    /** Ralentizacion temporal de los enemigos (Reloj del Destino). */
    static float enemyDt(Level lv, float dt) {
        BlessRt bx = lv.rs.bx;
        return bx != null && bx.slowT > 0 ? dt * bx.slowScale : dt;
    }

    /** Aplica las bendiciones de proyectiles a un proyectil amigo recien creado (perforacion, velocidad, tamano, rebote, ondas, duplicado). */
    static void tuneProj(Level lv, Proj p) {
        BlessRt bx = live(lv);
        if (bx == null) return;
        RunState rs = lv.rs;
        p.pierce += Math.round(sv(rs, BRule.M_PIERCE));
        float sp = sv(rs, BRule.M_PROJSPEED);
        if (sp != 0f) { p.vx *= 1f + sp; p.vy *= 1f + sp; }
        float sz = sv(rs, BRule.M_PROJSIZE);
        if (sz != 0f) { p.scale *= 1f + sz; p.radius *= 1f + sz; }
        if (sv(rs, BRule.M_HOMING) > 0f && p.homing <= 0f) p.homing = 300f;
        p.bounces += Math.min(2, Math.round(sv(rs, BRule.M_BOUNCE)));
        p.pierceGrow += sv(rs, BRule.M_PIERCEDMG);
        if (p.sprite.equals("crescent") && sv(rs, BRule.M_WAVEDMG) > 0f) { p.dmg *= 1f + sv(rs, BRule.M_WAVEDMG); p.scale *= 1.2f; p.radius *= 1.2f; }
        float dbl = sv(rs, BRule.M_PROJDOUBLE);
        if (dbl > 0f && p.src != SRC_X && !p.copyMade && lv.rng.chance(dbl)) {
            final Proj o = p; final float ox = p.x, oy = p.y;
            lv.later(0.1f, () -> { if (o.dead) return; Proj c = o.copy(); c.x = ox; c.y = oy; c.t = 0; c.life = Math.max(0.3f, o.life); lv.spawnProj(c); });
        }
    }

    static float focusStep(BlessRt bx) {
        float s = 0;
        for (BRule r : bx.mods[BRule.M_FOCUS - 60]) s += r.a[0];
        return s;
    }

    static float sumMod(Level lv, int m, Ent v, int src) {
        BlessRt bx = live(lv);
        if (bx == null) return 0f;
        float s = 0f;
        for (BRule r : bx.mods[m - 60]) {
            if (isStatic(r)) continue;                           // los estaticos ya estan en Stats / sv
            if (r.src != 0 && r.src != src) continue;
            if (!check(lv, bx, r, v, src)) continue;
            s += r.a[0] * mag(lv.rs, r);
        }
        return s;
    }

    /** Bonus dinamico de probabilidad de critico (condiciones + canal). */
    static float critBonus(Level lv, Ent v, int src) {
        BlessRt bx = live(lv);
        if (bx == null) return 0f;
        float s = sumMod(lv, BRule.M_CRIT, v, src) + bx.ch(BRule.CH_CRIT);
        if (src == SRC_P) s += sv(lv.rs, BRule.M_PCRIT) + sumMod(lv, BRule.M_PCRIT, v, src);
        return s;
    }

    static float critMulBonus(Level lv, Ent v, int src) { return live(lv) == null ? 0f : sumMod(lv, BRule.M_CRITMUL, v, src); }

    /** Multiplicador de dano recibido del jugador (condiciones + canal + estaticos de enemigos mas fuertes). */
    static float takenMul(Level lv) {
        BlessRt bx = live(lv);
        if (bx == null) return 1f;
        float m = 1f + bx.ch(BRule.CH_TAKEN);
        m *= 1f + sumMod(lv, BRule.M_TAKEN, null, 0);
        m *= 1f + sv(lv.rs, BRule.M_ENEMYDMG);
        return Math.max(0.3f, m);
    }

    static float speedMul(Level lv) {
        BlessRt bx = live(lv);
        if (bx == null) return 1f;
        float m = (1f + bx.ch(BRule.CH_SPD)) * (1f + sumMod(lv, BRule.M_SPEED, null, 0));
        return Math.max(0.5f, Math.min(1.6f, m));
    }

    static float atkSpdMul(Level lv) {
        BlessRt bx = live(lv);
        if (bx == null) return 1f;
        float m = (1f + bx.ch(BRule.CH_ATK)) * (1f + sumMod(lv, BRule.M_ATKSPD, null, 0));
        return Math.max(0.5f, Math.min(1.7f, m));
    }

    static float healMul(RunState rs) { return rs.bx == null || !rs.bx.any ? 1f : Math.max(0.1f, 1f + sv(rs, BRule.M_HEALMUL)); }

    static float reach(Level lv) { BlessRt bx = live(lv); return bx == null ? 1f : Math.max(0.5f, 1f + sv(lv.rs, BRule.M_REACH)); }

    static float finishMul(Level lv) { BlessRt bx = live(lv); return bx == null ? 1f : 1f + sv(lv.rs, BRule.M_FINISHMUL) + sumMod(lv, BRule.M_FINISHMUL, null, 0); }

    static float shopDisc(RunState rs) { return rs.bx == null ? 0f : Math.min(0.5f, sv(rs, BRule.M_SHOPDISC)); }

    static int offerExtra(RunState rs) { return rs.bx == null ? 0 : Math.min(1, Math.round(sv(rs, BRule.M_OFFER))); }

    static float shieldCap(RunState rs) { return 60f + (rs.bx == null ? 0f : sv(rs, BRule.M_SHIELDCAP)); }

    static float spiritRate(Level lv) {
        BlessRt bx = live(lv);
        if (bx == null) return 1f;
        float m = 1f + sv(lv.rs, BRule.M_SPIRITRATE) + sumMod(lv, BRule.M_SPIRITRATE, null, 0);
        if (bx.spiritBoostT > 0) m += 0.5f;
        return Math.max(0.3f, Math.min(2.5f, m));
    }

    static float dotMul(RunState rs) { return rs.bx == null || !rs.bx.any ? 1f : 1f + sv(rs, BRule.M_DOT); }

    static float statusDurMul(RunState rs) { return rs.bx == null || !rs.bx.any ? 1f : 1f + sv(rs, BRule.M_STATUSDUR); }

    // ------------------------------------------------------------------ eventos
    /** Dano directo a un enemigo ya aplicado. Dispara CRIT, DMGS, PROJ y la gestion de rachas de criticos y enfoque. */
    static void afterDamage(Level lv, Ent e, float dmg, boolean crit, int src) {
        BlessRt bx = live(lv);
        if (bx == null || bx.depth > 0) return;
        boolean player = src == SRC_W || src == SRC_S || src == SRC_P;
        if (!player) return;
        if (crit) bx.critStreak++; else if (src == SRC_W) bx.critStreak = 0;
        if (src == SRC_P) {
            float fs = focusStep(bx);
            if (fs > 0) { if (e.focusT > 0) e.focusN = Math.min(5, e.focusN + 1); else e.focusN = 1; e.focusT = 2.5f; }
        }
        if (crit) fire(lv, BRule.T_CRIT, e, dmg, true, src, e.cx(), e.cy());
        if (src == SRC_S) fire(lv, BRule.T_DMGS, e, dmg, crit, src, e.cx(), e.cy());
        if (src == SRC_P) fire(lv, BRule.T_PROJ, e, dmg, crit, src, e.cx(), e.cy());
    }

    static void onHit(Level lv, Ent e, float dmg, boolean crit, int combo) {
        BlessRt bx = live(lv);
        if (bx == null || bx.depth > 0) return;
        bx.hitStreak++;
        if (combo == 3) fire(lv, BRule.T_FINISH, e, dmg, crit, SRC_W, e.cx(), e.cy());
        fire(lv, BRule.T_HIT, e, dmg, crit, SRC_W, e.cx(), e.cy());
        for (BRule r : bx.byTrig[BRule.T_STREAK]) if (r.n > 0 && bx.hitStreak % r.n == 0) tryRule(lv, bx, r, e, dmg, crit, SRC_W, e.cx(), e.cy());
    }

    static void onKill(Level lv, Ent e, int src) {
        BlessRt bx = live(lv);
        if (bx == null) return;
        if (src == SRC_NONE) return;
        if (bx.t - bx.lastKillT < 3f) bx.killChain++; else bx.killChain = 1;
        bx.lastKillT = bx.t;
        // feedback de cadena: aro naranja en bajas causadas por reacciones (no por el golpe directo) y rotulo cada 4 bajas seguidas
        if (bx.depth > 0 && !Save.S.reduceFx) lv.fxAdd("fx_ring", "pulse", e.cx(), e.cy(), 0.9f, 0xFF9030);
        if (bx.killChain >= 4 && bx.killChain % 4 == 0) { lv.text(lv.pl.x, lv.pl.y - 70, "¡Cadena x" + bx.killChain + "!", 0xFF9030, true); lv.shake(2f, 0.12f); }
        fire(lv, BRule.T_KILL, e, e.maxHp, false, src, e.cx(), e.cy());
    }

    static void onHurt(Level lv, float dmg) {
        BlessRt bx = live(lv);
        if (bx == null) return;
        bx.hitStreak = 0; bx.critStreak = 0; bx.parryStreak = 0; bx.dodgeStreak = 0;
        Player p = lv.pl;
        fire(lv, BRule.T_HURT, nearest(lv), dmg, false, SRC_NONE, p.x, p.cy());
    }

    static void onBlocked(Level lv, float absorbed) {
        BlessRt bx = live(lv);
        if (bx == null) return;
        Player p = lv.pl;
        fire(lv, BRule.T_BLOCKED, nearest(lv), absorbed, false, SRC_NONE, p.x, p.cy());
    }

    static void onParry(Level lv) {
        BlessRt bx = live(lv);
        if (bx == null) return;
        bx.parryStreak++;
        Player p = lv.pl;
        fire(lv, BRule.T_PARRY, nearest(lv), 0, false, SRC_NONE, p.x + p.dir() * 14, p.cy());
    }

    static void onDodge(Level lv) {
        BlessRt bx = live(lv);
        if (bx == null) return;
        if (bx.t < bx.dodgeLock) return;
        bx.dodgeLock = bx.t + 0.5f;
        bx.dodgeStreak++;
        Player p = lv.pl;
        fire(lv, BRule.T_DODGE, nearest(lv), 0, false, SRC_NONE, p.x, p.cy());
    }

    static void onRoll(Level lv, boolean end) {
        BlessRt bx = live(lv);
        if (bx == null) return;
        Player p = lv.pl;
        fire(lv, end ? BRule.T_ROLLEND : BRule.T_ROLL, nearest(lv), 0, false, SRC_NONE, p.x, p.cy());
    }

    /** Habilidad lanzada (i = 0..2). Convierte NEXTSKILL en multiplicador del lanzamiento. */
    static void onSkill(Level lv, int i) {
        BlessRt bx = live(lv);
        if (bx == null) return;
        bx.skillCasts++;
        bx.skillMulT = 0; bx.skillMul = 0;
        bx.empowered = false;
        if (bx.nextSkillT > 0) { bx.skillMul = bx.nextSkillMul; bx.skillMulT = 2.0f; bx.empowered = true; bx.nextSkillT = 0; bx.nextSkillMul = 0; }
        Player p = lv.pl;
        fireK(lv, BRule.T_SKILL, i, nearest(lv), 0, false, SRC_S, p.x, p.cy());
    }

    static void onUlt(Level lv, boolean end) {
        BlessRt bx = live(lv);
        if (bx == null) return;
        Player p = lv.pl;
        if (!end) { bx.skillMul = 0; bx.skillMulT = 0; if (bx.nextSkillT > 0) { bx.skillMul = bx.nextSkillMul; bx.skillMulT = 3f; bx.nextSkillT = 0; } }
        fire(lv, end ? BRule.T_ULTEND : BRule.T_ULT, nearest(lv), 0, false, end ? SRC_NONE : SRC_S, p.x, p.cy());
    }

    static void onRoomStart(Level lv) {
        BlessRt bx = live(lv);
        lv.rs.bx = lv.rs.bx == null ? new BlessRt() : lv.rs.bx;
        bx = lv.rs.bx;
        bx.roomReset();
        sync(lv.rs);
        if (!bx.any) return;
        bx.hitStreak = 0;
        Player p = lv.pl;
        if (p != null) fire(lv, BRule.T_ROOM, null, 0, false, SRC_NONE, p.x, p.cy());
    }

    static void onCleared(Level lv) {
        BlessRt bx = live(lv);
        if (bx == null) return;
        Player p = lv.pl;
        fire(lv, BRule.T_CLEAR, null, 0, false, SRC_NONE, p.x, p.cy());
        if (lv.roomHits == 0) fire(lv, BRule.T_PERFECT, null, 0, false, SRC_NONE, p.x, p.cy());
    }

    static void onBossDead(Level lv) {
        BlessRt bx = live(lv);
        if (bx == null) return;
        Player p = lv.pl;
        fire(lv, BRule.T_BOSSDEAD, null, 0, false, SRC_NONE, p.x, p.cy());
    }

    static void onPick(Level lv, int what) {
        BlessRt bx = live(lv);
        if (bx == null) return;
        Player p = lv.pl;
        for (BRule r : bx.byTrig[BRule.T_PICK]) if (r.what == what) tryRule(lv, bx, r, null, 0, false, SRC_NONE, p.x, p.cy());
    }

    /** Recogida inutil (corazon con vida llena, pocion con frascos llenos): permite convertirla en otro recurso. */
    static void onOverflow(Level lv, int what) {
        BlessRt bx = live(lv);
        if (bx == null) return;
        Player p = lv.pl;
        for (BRule r : bx.byTrig[BRule.T_OVERFLOW]) if (r.what == what) tryRule(lv, bx, r, null, 0, false, SRC_NONE, p.x, p.cy());
    }

    static void onPotion(Level lv) {
        BlessRt bx = live(lv);
        if (bx == null) return;
        Player p = lv.pl;
        fire(lv, BRule.T_POTION, null, 0, false, SRC_NONE, p.x, p.cy());
    }

    static void onJump(Level lv, boolean air) {
        BlessRt bx = live(lv);
        if (bx == null) return;
        Player p = lv.pl;
        fire(lv, air ? BRule.T_AIRJUMP : BRule.T_JUMP, nearest(lv), 0, false, SRC_NONE, p.x, p.cy());
    }

    static void onLand(Level lv, float fall) {
        BlessRt bx = live(lv);
        if (bx == null || fall < 330f) return;
        Player p = lv.pl;
        fire(lv, BRule.T_LAND, nearest(lv), fall, false, SRC_NONE, p.x, p.y - 4);
    }

    // ------------------------------------------------------------------ ejecucion de reglas
    static void fire(Level lv, int trig, Ent v, float amt, boolean crit, int src, float x, float y) {
        fireK(lv, trig, -1, v, amt, crit, src, x, y);
    }

    static void fireK(Level lv, int trig, int k, Ent v, float amt, boolean crit, int src, float x, float y) {
        BlessRt bx = lv.rs.bx;
        if (bx == null || !bx.any) return;
        BRule[] L = bx.byTrig[trig];
        if (L.length == 0) return;
        if (bx.depth > 0 && !((trig == BRule.T_KILL && bx.depth < 3) || (trig == BRule.T_DISCHARGED && bx.depth < 2))) return;
        for (BRule r : L) {
            if (k >= 0 && r.k >= 0 && r.k != k) continue;
            tryRule(lv, bx, r, v, amt, crit, src, x, y);
        }
    }

    static boolean srcOk(BRule r, int src) {
        if (r.src != 0) return r.src == src;
        switch (r.trig) {
            case BRule.T_CRIT: case BRule.T_DMGS: case BRule.T_PROJ: return src == SRC_W || src == SRC_S || src == SRC_P;
            default: return true;
        }
    }

    static void tryRule(Level lv, BlessRt bx, BRule r, Ent v, float amt, boolean crit, int src, float x, float y) {
        if (r.syn >= 0 && !bx.synOn[r.syn]) return;
        if (!srcOk(r, src)) return;
        if (r.icd > 0 && bx.icd[r.idx] > bx.t) return;
        if (!check(lv, bx, r, v, src)) return;
        if (r.ch > 0 && !lv.rng.chance(r.ch)) return;
        if (bx.perSecond >= 90) return;
        bx.perSecond++;
        if (r.icd > 0) bx.icd[r.idx] = bx.t + r.icd;
        bx.depth++;
        int prevSrc = lv.dmgSrc;
        lv.dmgSrc = SRC_X;
        try {
            BlessEffects.run(lv, bx, r, mag(lv.rs, r), v, amt, crit, src, x, y);
        } finally {
            lv.dmgSrc = prevSrc;
            bx.depth--;
        }
        if (r.owner >= 0 && r.owner < bx.fired.length) bx.fired[r.owner]++;
        else if (r.syn >= 0) bx.firedSyn[r.syn]++;
        if (r.syn >= 0 && bx.firedSyn[r.syn] == 1) BlessEffects.synergyFound(lv, r.syn);
    }

    static Ent nearest(Level lv) {
        Player p = lv.pl;
        if (p == null) return null;
        return lv.nearestEnemy(p.x, p.cy(), 160f, true);
    }

    // ------------------------------------------------------------------ actualizacion por fotograma
    static void update(Level lv, float dt) {
        BlessRt bx = lv.rs.bx;
        if (bx == null) return;
        sync(lv.rs);
        if (!bx.any) { bx.t += dt; return; }
        Player p = lv.pl;
        if (p == null) return;
        bx.t += dt; bx.roomT += dt;
        bx.perSecondT += dt;
        if (bx.perSecondT >= 1f) { bx.perSecondT = 0; bx.perSecond = 0; }
        bx.cdrBucket = Math.min(6f, bx.cdrBucket + dt * 1.2f);
        for (int c = 0; c < BRule.CH_COUNT; c++) if (bx.chT[c] > 0) { bx.chT[c] -= dt; if (bx.chT[c] <= 0) { bx.chN[c] = 0; bx.chT[c] = 0; } }
        if (bx.nextHitT > 0) { bx.nextHitT -= dt; if (bx.nextHitT <= 0) bx.nextHitMul = 0; }
        if (bx.nextSkillT > 0) { bx.nextSkillT -= dt; if (bx.nextSkillT <= 0) bx.nextSkillMul = 0; }
        if (bx.skillMulT > 0) bx.skillMulT -= dt;
        if (bx.slowT > 0) bx.slowT -= dt;
        if (bx.spiritBoostT > 0) bx.spiritBoostT -= dt;
        for (Enemy e : lv.enemies) if (e.focusT > 0) e.focusT -= dt;
        if (lv.boss != null && lv.boss.focusT > 0) lv.boss.focusT -= dt;
        // recuperacion extra de habilidades (canal cdr)
        float cdr = bx.ch(BRule.CH_CDR);
        if (cdr > 0) for (int i = 0; i < 3; i++) if (lv.rs.cd[i] > 0) lv.rs.cd[i] = Math.max(0f, lv.rs.cd[i] - dt * cdr);
        // vida baja
        boolean low = lv.rs.hp / Math.max(1f, lv.rs.stats.maxHp) < 0.35f && p.alive;
        if (low && !bx.lowHpPrev) fire(lv, BRule.T_LOWHP, nearest(lv), 0, false, SRC_NONE, p.x, p.cy());
        bx.lowHpPrev = low;
        // peligros superados sin dano (pinchos)
        trackHazard(lv, bx, p, dt);
        // reglas periodicas
        BRule[] tk = bx.byTrig[BRule.T_TICK];
        for (BRule r : tk) {
            bx.tickT[r.idx] -= dt;
            if (bx.tickT[r.idx] > 0) continue;
            bx.tickT[r.idx] = r.every;
            if (lv.cinematic || !p.alive) continue;
            tryRule(lv, bx, r, nearest(lv), 0, false, SRC_NONE, p.x, p.cy());
        }
        BlessEffects.updateSpirits(lv, bx, dt);
        BlessEffects.updatePatches(lv, bx, dt);
    }

    private static void trackHazard(Level lv, BlessRt bx, Player p, float dt) {
        if (bx.byTrig[BRule.T_HAZARD].length == 0) return;
        boolean over = false;
        if (!p.onGround && p.alive) {
            for (int dy = 0; dy <= 4 && !over; dy++) for (int dx = -1; dx <= 1 && !over; dx++)
                if (lv.room.hazardAt(p.x + dx * 8, p.y + dy * 8)) over = true;
        }
        if (bx.overHazard && !over) {
            if (p.onGround && lv.hurtMark == bx.hurtAtEnter) fire(lv, BRule.T_HAZARD, nearest(lv), 0, false, SRC_NONE, p.x, p.cy());
            bx.overHazard = false;
        } else if (!bx.overHazard && over) { bx.overHazard = true; bx.hurtAtEnter = lv.hurtMark; }
    }

    static void draw(Level lv, Platform.Gfx g) { BlessEffects.draw(lv, g); }
}
