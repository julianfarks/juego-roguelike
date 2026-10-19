package com.julianfarks.roguelike.core;

import java.util.HashSet;

/**
 * Pasivas y estados de las armas secundarias nuevas (ver Wpn.P_*). Todo tiene limite: las cargas de cada estado estan acotadas (Ent.stackStatus),
 * los jefes admiten menos cargas y tienen inmunidades tematicas, el aturdimiento tiene enfriamiento por objetivo (nunca se encadena un bloqueo permanente),
 * y las curaciones y devoluciones de recursos tienen enfriamiento propio. Los estados de siempre (Ent.applyStatus) no se tocan.
 */
final class WeaponFx {
    private WeaponFx() {}

    /** Estado de ejecucion del jugador para las armas secundarias (no se guarda). */
    static final class State {
        // precision: golpes seguidos sobre el mismo objetivo
        Ent precTgt; int precN; float precT;
        // ritmo (espada corta): golpes acertados seguidos
        int rhythmN; float rhythmT, rhythmBoost;
        // curacion / recursos devueltos: enfriamientos
        float lifeCd, recoverCd;
        // guanteletes: tercer golpe seguido
        int c3N; float c3T;
        // varita elemental: paso del ciclo (0 fuego, 1 hielo, 2 rayo, 3 nova) y ventana
        int resonStep; float resonT;
        // golpe cuerpo a cuerpo en curso
        boolean sw; int swId; float swT, swDur, swDir; int swHitIdx; boolean swLanded; boolean swAir; int swCount;
        @SuppressWarnings("unchecked") final HashSet<Ent>[] sets = new HashSet[4];
        State() { for (int i = 0; i < sets.length; i++) sets[i] = new HashSet<>(); }
        void reset() { sw = false; swHitIdx = 0; swLanded = false; for (HashSet<Ent> s : sets) s.clear(); }
    }

    static void tick(Player p, float dt) {
        State s = p.wfx;
        if (s.precT > 0) { s.precT -= dt; if (s.precT <= 0) { s.precN = 0; s.precTgt = null; } }
        if (s.rhythmT > 0) { s.rhythmT -= dt; if (s.rhythmT <= 0) s.rhythmN = 0; }
        if (s.rhythmBoost > 0) s.rhythmBoost -= dt;
        if (s.lifeCd > 0) s.lifeCd -= dt;
        if (s.recoverCd > 0) s.recoverCd -= dt;
        if (s.c3T > 0) { s.c3T -= dt; if (s.c3T <= 0) s.c3N = 0; }
        if (s.resonT > 0) { s.resonT -= dt; if (s.resonT <= 0) s.resonStep = 0; }
    }

    static boolean has(int id, int pas) { return id > 0 && id < Wpn.N && (Wpn.T[id].passive & pas) != 0; }

    /** Multiplicador de daño ANTES del golpe: precision (golpes seguidos al mismo objetivo) y maldicion (+12% de daño recibido). */
    static float preMul(Level lv, int id, Ent e) {
        float m = 1f;
        State s = lv.pl.wfx;
        if (has(id, Wpn.P_PRECISION) && s.precTgt == e && s.precN > 0) m *= 1f + 0.08f * Math.min(5, s.precN);
        if (e.st[Ent.CURSE] > 0 && e.statusResist(Ent.CURSE) > 0) m *= 1f + 0.12f * e.statusResist(Ent.CURSE);
        return m;
    }

    /** Efectos DESPUES de un golpe del arma `id` sobre `e`. `dmg` = daño ya aplicado. */
    static void afterHit(Level lv, int id, Ent e, float dmg, boolean crit, boolean melee, float dir) {
        if (id <= 0 || id >= Wpn.N || e == null) return;
        Wpn.Def d = Wpn.T[id];
        int ps = d.passive;
        Player p = lv.pl;
        State s = p.wfx;
        if ((ps & Wpn.P_PRECISION) != 0) {
            if (s.precTgt == e) s.precN = Math.min(5, s.precN + 1); else { s.precTgt = e; s.precN = 1; }
            s.precT = 1.5f;
        }
        if (!e.alive || e.hp <= 0) { onKill(lv, id, e); }
        else statuses(lv, id, e, dmg, crit);
        if ((ps & Wpn.P_BLUNT) != 0) {
            float dur = id == Items.SEC_TONFA ? 0.5f : id == Items.SEC_HALBERD ? 0.6f : id == Items.SEC_WARHAMMER ? 0.8f : id == Items.SEC_TALISMAN ? 0.4f : 0.35f;
            if (id != Items.SEC_GAUNTLET || s.c3N % 3 == 0) interrupt(lv, e, dur);
        }
        if ((ps & Wpn.P_LIFE) != 0 && id == Items.SEC_BLOODSCEPTER && s.lifeCd <= 0 && e.alive) {
            float heal = Math.min(dmg * 0.03f, lv.rs.stats.maxHp * 0.02f);
            if (heal > 0.4f) { lv.healPlayer(heal); s.lifeCd = 0.8f; }
        }
    }

    private static void onKill(Level lv, int id, Ent e) {
        Player p = lv.pl; State s = p.wfx;
        if (id == Items.SEC_SCYTHE && s.lifeCd <= 0) {          // cosecha: curacion pequeña al abatir (con enfriamiento)
            lv.healPlayer(lv.rs.stats.maxHp * 0.025f);
            s.lifeCd = 1.5f;
            lv.fx("fx_ring", "pulse", p.x, p.y - 16, 0.4f, 0xB080E0, Platform.ADD | Platform.TINT);
        }
    }

    /** Estados por pasiva (cada llamada añade UNA carga, con tope). */
    static void statuses(Level lv, int id, Ent e, float dmg, boolean crit) {
        Wpn.Def d = Wpn.T[id];
        int ps = d.passive;
        if ((ps & Wpn.P_BLEED) != 0 || (crit && (ps & Wpn.P_CRIT) != 0)) e.stackStatus(Ent.BLEED, 4f, 3f, 4);
        if ((ps & Wpn.P_BURN) != 0 && id != Items.SEC_ELEMWAND) e.stackStatus(Ent.BURN, 3f, 3.5f, 3);
        if ((ps & Wpn.P_POISON) != 0) e.stackStatus(Ent.POISON, 4f, id == Items.SEC_VENOMCAT ? 3f : 2.5f, id == Items.SEC_VENOMCAT ? 5 : 3);
        if ((ps & Wpn.P_CHILL) != 0 && id != Items.SEC_ELEMWAND && id != Items.SEC_STICKYBOMB) chill(lv, e);
        if ((ps & Wpn.P_CURSE) != 0) e.stackStatus(Ent.CURSE, 4f, 0f, 1);
        if ((ps & Wpn.P_CHAIN) != 0 && id != Items.SEC_ELEMWAND) lv.chain(e, dmg * 0.55f, 2);
        if ((ps & Wpn.P_ARCANE) != 0) arcane(lv, id, e, dmg);
        if ((ps & Wpn.P_PULL) != 0) e.applyStatus(Ent.SLOW, 1.5f, 0);
    }

    /** Frio acumulable: ralentiza; a la 3ª carga congela 1 s (no a los jefes), y despues hay inmunidad al congelamiento. */
    static void chill(Level lv, Ent e) {
        int n = e.stackStatus(Ent.SLOW, 2.5f, 0f, 3);
        if (n >= 3 && e.frzImm <= 0 && !(e instanceof Boss) && e.statusResist(Ent.FREEZE) > 0.5f) {
            e.applyStatus(Ent.FREEZE, 1.0f, 0f);
            e.frzImm = 4.5f;
            e.stk[Ent.SLOW] = 0;
            lv.fx("fx_ring", "pulse", e.cx(), e.cy(), 0.5f, 0x9AE0FF, Platform.ADD | Platform.TINT);
        }
    }

    /** Marca arcana: a la 3ª marca estalla (daño en area) y devuelve 1 carga al cristal (con enfriamiento). */
    static void arcane(Level lv, int id, Ent e, float dmg) {
        e.arc++; e.arcT = 5f;
        if (e.arc < 3) return;
        e.arc = 0; e.arcT = 0;
        lv.explosion(e.cx(), e.cy(), 30, Math.max(1f, dmg * 1.1f), 90, -1, 0, 0, true);
        lv.fx("fx_ring", "pulse", e.cx(), e.cy(), 0.7f, 0xC890FF, Platform.ADD | Platform.TINT);
        lv.text(e.x, e.y - e.bh - 14, "¡Estallido arcano!", 0xC890FF, false);
        State s = lv.pl.wfx;
        if (has(id, Wpn.P_RECOVER) && s.recoverCd <= 0 && lv.rs.secAmmo < Items.SEC_AMMO[id]) { lv.rs.secAmmo++; s.recoverCd = 1.2f; }
    }

    /** Interrupcion: aturde un instante a los enemigos comunes (no a los jefes ni a los pesados/elites), con enfriamiento por objetivo. */
    static boolean interrupt(Level lv, Ent e, float dur) {
        if (!(e instanceof Enemy) || e.intrCd > 0 || e.frozen()) return false;
        Enemy en = (Enemy) e;
        if (en.elite || en.def.role == EnemyDef.HEAVY || en.def.role == EnemyDef.SHIELD || en.def.role == EnemyDef.CHARGER || en.def.role == EnemyDef.TURRET) return false;
        e.applyStatus(Ent.STUN, dur, 0f);
        e.intrCd = 3f;
        lv.text(e.x, e.y - e.bh - 14, "¡Interrumpido!", 0xFFFFFF, false);
        return true;
    }

    /** Explosion de un proyectil del arma `id`: aplica los estados de la pasiva a todos los alcanzados (una carga cada uno). */
    static void blast(Level lv, int id, int mode, float x, float y, float r, float dmg) {
        if (id <= 0) return;
        for (Ent e : lv.enemiesIn(x, y, Math.max(r, 8f))) {
            if (!e.alive) continue;
            if (id == Items.SEC_ELEMWAND && mode == 4) { novaStatuses(lv, e); continue; }
            statuses(lv, id, e, dmg, false);
            if (id == Items.SEC_STICKYBOMB) chill(lv, e);
            if ((Wpn.T[id].passive & Wpn.P_BLUNT) != 0 && id == Items.SEC_TALISMAN) interrupt(lv, e, 0.4f);
        }
    }

    static void novaStatuses(Level lv, Ent e) {
        e.stackStatus(Ent.BURN, 3f, 3.5f, 3);
        chill(lv, e);
        e.applyStatus(Ent.SHOCK, 0.8f, 0f);
    }

    /** Efecto propio de la varita elemental segun el elemento del proyectil (1 fuego, 2 hielo, 3 rayo). */
    static void elemHit(Level lv, Proj p, Ent e, float dmg) {
        switch (p.wmode) {
            case 1: e.stackStatus(Ent.BURN, 3f, 3.5f, 3); break;
            case 2: chill(lv, e); break;
            case 3: lv.chain(e, dmg * 0.5f, 2); e.applyStatus(Ent.SHOCK, 0.6f, 0f); break;
            default: break;
        }
    }
}
