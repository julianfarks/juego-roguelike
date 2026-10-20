package com.julianfarks.roguelike.core;

/**
 * Mejoras del arma principal por nivel (1..RunState.WEAPON_MAX). Ademas del bonus de dano de la curva comun, cada nivel da una mejora
 * distinta (velocidad de ataque, criticos, efectos elementales) y los hitos 5/10/15/20 dan una mejora especial.
 * Tras el nivel maximo, en Endless la forja ofrece Maestria (RunState.MASTERY_MAX rangos, con tope), sin crecimiento indefinido.
 */
public final class WeaponPerks {
    private WeaponPerks() {}

    // tipos
    static final int ATK = 0, CRIT = 1, CRITMUL = 2, BURN = 3, FREEZE = 4, POISON = 5, SHOCK = 6, WAVE = 7, GIANT = 8, EXEC = 9;
    /** Mejora de cada nivel (indice = nivel - 1): {tipo, magnitud}. */
    static final float[][] PERK = {
            {ATK, .04f}, {CRIT, .03f}, {CRITMUL, .10f}, {BURN, .08f}, {ATK, .05f},          // 1..5   (5 = hito)
            {CRIT, .03f}, {FREEZE, .08f}, {CRITMUL, .10f}, {POISON, .08f}, {WAVE, 1},       // 6..10  (10 = hito: onda de energia)
            {ATK, .05f}, {SHOCK, .08f}, {CRIT, .03f}, {CRITMUL, .15f}, {GIANT, 1},          // 11..15 (15 = hito: golpe gigante)
            {ATK, .05f}, {BURN, .06f}, {CRIT, .04f}, {CRITMUL, .15f}, {EXEC, .30f},     // 16..20 (20 = hito: ejecutor)
    };
    public static boolean milestone(int lvl) { return lvl > 0 && lvl % 5 == 0; }

    /** Aplica todas las mejoras de los niveles alcanzados (y la maestria) a las estadisticas. */
    static void apply(RunState rs, Stats s) {
        int n = Math.min(rs.weaponLvl, PERK.length);
        for (int i = 0; i < n; i++) {
            int t = (int) PERK[i][0]; float m = PERK[i][1];
            switch (t) {
                case ATK: s.atkSpd += m; break;
                case CRIT: s.critChance += m; break;
                case CRITMUL: s.critMul += m; break;
                case BURN: s.burn += m; break;
                case FREEZE: s.freeze += m; break;
                case POISON: s.poison += m; break;
                case SHOCK: s.shock += m; break;
                case WAVE: s.wave = Math.max(s.wave, 1); break;
                case GIANT: s.giant = Math.max(s.giant, 1); break;
                case EXEC: s.exec += m; break;
                default: break;
            }
        }
        if (rs.mastery > 0) { s.critChance += 0.015f * rs.mastery; s.dmgMul *= 1f + 0.02f * rs.mastery; }
    }

    /** Texto corto de la mejora que da el nivel `lvl` (1..20). */
    public static String text(int lvl) {
        if (lvl < 1 || lvl > PERK.length) return "";
        int t = (int) PERK[lvl - 1][0]; float m = PERK[lvl - 1][1];
        int pct = Math.round(m * 100);
        switch (t) {
            case ATK: return "+" + pct + "% de velocidad de ataque";
            case CRIT: return "+" + pct + "% de probabilidad crítica";
            case CRITMUL: return "+" + pct + "% de daño crítico";
            case BURN: return "+" + pct + "% de quemar al golpear";
            case FREEZE: return "+" + pct + "% de ralentizar/congelar";
            case POISON: return "+" + pct + "% de envenenar";
            case SHOCK: return "+" + pct + "% de rayo encadenado";
            case WAVE: return "HITO: cada 2º golpe lanza una onda";
            case GIANT: return "HITO: el 3er golpe del combo es gigante";
            case EXEC: return "HITO: +" + pct + "% de daño a enemigos débiles";
            default: return "";
        }
    }
}
