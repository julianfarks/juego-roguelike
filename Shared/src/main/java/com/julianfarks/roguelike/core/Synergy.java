package com.julianfarks.roguelike.core;

/**
 * Primeras sinergias entre MEJORAS acumulables (cofres: estadisticas de ChestLoot y mejoras del arma principal de Items).
 * Se activan solas en cuanto tienes las dos mejoras que piden (a cualquier nivel) y se ven en la pestaña Mejoras del inventario.
 * Son independientes de las sinergias de bendiciones (BlessFx): no se mezclan ni se duplican.
 */
final class Synergy {
    private Synergy() {}

    static final int TOXIC = 0, FROSTCRIT = 1, BLOODRUSH = 2, STORM = 3, COUNT = 4;
    static final String[] NAME = {"Combustión tóxica", "Escarcha afilada", "Frenesí sanguinario", "Tormenta de acero"};
    static final String[] REQ = {"Fuego + Veneno", "Hielo + Críticos", "Robo de vida + Vel. de ataque", "Descarga + Daño"};
    static final String[] DESC = {
            "Los enemigos que mueren quemados o envenenados estallan en una nube tóxica que daña y envenena a los que estén cerca.",
            "Tus golpes críticos hacen +50% de daño a los enemigos congelados o ralentizados.",
            "+4% de robo de vida y +8% de velocidad de ataque.",
            "+10% de daño y +10% de probabilidad de descarga."};
    static final String[] ICON = {"poison", "freeze", "b_sangre", "shock"};
    static final int[] COL = {0x9AE04A, 0x8AE8FF, 0xFF5A6A, 0xFFE860};

    // ---- configuracion
    static final float TOXIC_R = 46f, TOXIC_DMG = 0.6f, TOXIC_POISON_T = 3f, TOXIC_POISON_POW = 5f;
    static final float FROST_CRIT_BONUS = 0.5f;

    // ---- requisitos (cualquier fuente de cofre: estadistica o mejora del arma)
    static boolean fire(RunState rs) { return rs.cb[ChestLoot.BURN] > 0 || rs.spLvl[1] > 0; }
    static boolean poison(RunState rs) { return rs.cb[ChestLoot.POISON] > 0 || rs.spLvl[3] > 0; }
    static boolean ice(RunState rs) { return rs.cb[ChestLoot.FREEZE] > 0 || rs.spLvl[2] > 0; }
    static boolean crit(RunState rs) { return rs.cb[ChestLoot.CRIT] > 0 || rs.cb[ChestLoot.CRITD] > 0 || rs.spLvl[5] > 0 || rs.spLvl[6] > 0; }
    static boolean lifesteal(RunState rs) { return rs.cb[ChestLoot.LS] > 0 || rs.spLvl[4] > 0; }
    static boolean aspd(RunState rs) { return rs.cb[ChestLoot.ASPD] > 0 || rs.spLvl[8] > 0; }
    static boolean shock(RunState rs) { return rs.cb[ChestLoot.SHOCK] > 0 || rs.spLvl[5] > 0; }
    static boolean dmg(RunState rs) { return rs.cb[ChestLoot.DMG] > 0 || rs.spLvl[6] > 0 || rs.spLvl[7] > 0; }

    static boolean active(RunState rs, int id) {
        switch (id) {
            case TOXIC: return fire(rs) && poison(rs);
            case FROSTCRIT: return ice(rs) && crit(rs);
            case BLOODRUSH: return lifesteal(rs) && aspd(rs);
            case STORM: return shock(rs) && dmg(rs);
            default: return false;
        }
    }

    /** Mascara de sinergias activas (bit = id). */
    static int mask(RunState rs) { int m = 0; for (int i = 0; i < COUNT; i++) if (active(rs, i)) m |= 1 << i; return m; }

    /** Sinergias que dan estadisticas (se llama desde Stats.recalc, tras las mejoras de cofre). */
    static void applyStats(RunState rs, Stats s) {
        if (active(rs, BLOODRUSH)) { s.lifesteal += 0.04f; s.atkSpd *= 1.08f; }
        if (active(rs, STORM)) { s.dmgMul *= 1.10f; s.shock += 0.10f; }
    }

    /** Escarcha afilada: multiplicador extra del critico contra un enemigo congelado o ralentizado. */
    static float critMulBonus(Level lv, Ent e) {
        if (e == null || lv == null || !active(lv.rs, FROSTCRIT)) return 0f;
        return e.hasStatus(Ent.FREEZE) || e.hasStatus(Ent.SLOW) ? FROST_CRIT_BONUS : 0f;
    }

    static int toxicN;     // (pruebas) explosiones toxicas

    /** Combustion toxica: al morir quemado o envenenado, el enemigo estalla (daña y envenena alrededor). Llamado desde Enemy.die. */
    static void onEnemyDeath(Level lv, Enemy e, boolean suicide) {
        if (suicide || lv.pl == null || !active(lv.rs, TOXIC)) return;
        if (!e.hasStatus(Ent.BURN) && !e.hasStatus(Ent.POISON)) return;
        float cx = e.x, cy = e.y - e.bh / 2f;
        toxicN++;
        lv.explosion(cx, cy, TOXIC_R, lv.pl.baseDmg(lv) * TOXIC_DMG, 90, Ent.POISON, TOXIC_POISON_T, TOXIC_POISON_POW, true);
        lv.fxAdd("fx_explosion", "a", cx, cy, 0.5f, COL[TOXIC]);
        lv.ps.burst(lv.rng, cx, cy, COL[TOXIC], 18, 120, 0.7f, 3, -20, true);
        Snd.sfxv("explosion_small", 0.45f);
    }

    /** Aviso al activarse una sinergia nueva (texto flotante sobre el jugador). Devuelve el nombre o null. */
    static String announce(Level lv, int before) {
        int now = mask(lv.rs), nw = now & ~before;
        if (nw == 0) return null;
        for (int i = 0; i < COUNT; i++) if ((nw & (1 << i)) != 0) {
            if (lv.pl != null) lv.text(lv.pl.x, lv.pl.y - lv.pl.bh - 40, "¡Sinergia: " + NAME[i] + "!", COL[i], true);
            lv.rs.markNew("y:" + i);
            return NAME[i];
        }
        return null;
    }
}
