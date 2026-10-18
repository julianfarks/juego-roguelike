package com.julianfarks.roguelike.core;

/** Utilidades de estados alterados (quemadura, veneno, hielo...). */
final class Status {
    private Status() {}

    /** Reduce los temporizadores y devuelve el daño por segundo de los estados periodicos activos. */
    static float tick(Ent e, float dt) {
        float dps = 0;
        for (int i = 0; i < Ent.ST_COUNT; i++) {
            if (e.st[i] > 0) {
                if (i == Ent.BURN || i == Ent.POISON || i == Ent.BLEED) dps += e.stPow[i];
                e.st[i] -= dt;
                if (e.st[i] <= 0) { e.st[i] = 0; e.stPow[i] = 0; }
            }
        }
        return dps;
    }

    static int parse(String s) {
        if (s == null) return -1;
        switch (s) {
            case "burn": return Ent.BURN;
            case "poison": return Ent.POISON;
            case "slow": return Ent.SLOW;
            case "shock": return Ent.SHOCK;
            case "bleed": return Ent.BLEED;
            case "freeze": return Ent.FREEZE;
            case "curse": return Ent.CURSE;
            default: return -1;
        }
    }

    /** Particulas de estado sobre una entidad. */
    static void fx(Level lv, Ent e, float dt) {
        Rng r = lv.rng;
        float cx = e.x, cy = e.y - e.bh * 0.5f;
        if (e.st[Ent.BURN] > 0 && r.chance(dt * 18)) lv.ps.spawn(cx + r.f(-5, 5), cy + r.f(-8, 8), r.f(-6, 6), -r.f(25, 50), 0.45f, 2, 0, 0xFF8A2A, true);
        if (e.st[Ent.POISON] > 0 && r.chance(dt * 10)) lv.ps.spawn(cx + r.f(-5, 5), cy + r.f(-6, 8), r.f(-4, 4), -r.f(10, 25), 0.6f, 2, 0, 0x6AE08A, true);
        if (e.st[Ent.BLEED] > 0 && r.chance(dt * 10)) lv.ps.spawn(cx + r.f(-4, 4), cy + r.f(-6, 8), r.f(-10, 10), r.f(10, 30), 0.5f, 2, 120, 0xC4122C, false);
        if (e.st[Ent.SHOCK] > 0 && r.chance(dt * 14)) lv.ps.spawn(cx + r.f(-8, 8), cy + r.f(-10, 10), r.f(-30, 30), r.f(-30, 30), 0.15f, 1, 0, 0xF0F060, true);
        if (e.st[Ent.FREEZE] > 0 && r.chance(dt * 8)) lv.ps.spawn(cx + r.f(-8, 8), cy + r.f(-10, 10), 0, 6, 0.5f, 2, 0, 0xBFEFFF, true);
        if (e.st[Ent.CURSE] > 0 && r.chance(dt * 9)) lv.ps.spawn(cx + r.f(-6, 6), cy - 12 + r.f(-4, 4), r.f(-4, 4), -r.f(12, 26), 0.5f, 2, 0, 0xB070FF, true);
        if (e.st[Ent.SLOW] > 0 && r.chance(dt * 5)) lv.ps.spawn(cx + r.f(-6, 6), cy + r.f(-10, 10), 0, 8, 0.5f, 1, 0, 0x7AB8FF, true);
    }

    /** Color multiplicativo segun el estado dominante (0 = sin tinte). */
    static int tint(Ent e) {
        if (e.st[Ent.FREEZE] > 0) return 0x9AD8FF;
        if (e.st[Ent.SLOW] > 0) return 0xB8D4FF;
        if (e.st[Ent.POISON] > 0) return 0xB8FFB8;
        if (e.st[Ent.ROOT] > 0) return 0xB8E090;
        if (e.st[Ent.CURSE] > 0) return 0xD8B8FF;
        return 0;
    }
}
