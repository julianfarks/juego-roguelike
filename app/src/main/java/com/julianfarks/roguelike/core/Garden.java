package com.julianfarks.roguelike.core;

/** Jardin magico: 3 cristales que crecen (0..4) gastando almas ganadas en las runs. Bonos moderados y con tope. */
public final class Garden {
    private Garden() {}
    public static final int PLOTS = 3, MAX = 4;
    public static final String[] NAME = {"Cristal de brasa", "Cristal de savia", "Cristal de fortuna"};
    public static final int[] COLOR = {0xFF8A30, 0x7AFFC0, 0xFFD25A};
    public static final String[] DESC = {"+2% de daño por etapa.", "+5 de vida máxima por etapa.", "+15 de oro inicial por etapa."};
    public static final int[] COST = {80, 160, 280, 440};

    public static int level(Save s, int p) { return Math.max(0, Math.min(MAX, s.garden[p])); }
    public static boolean canGrow(Save s, int p) { return level(s, p) < MAX && s.souls >= COST[level(s, p)] && !s.readOnly; }

    public static boolean grow(Save s, int p) {
        if (!canGrow(s, p)) return false;
        s.souls -= COST[level(s, p)];
        s.garden[p] = level(s, p) + 1;
        s.write();
        return true;
    }

    public static String effect(int p, int lv) {
        switch (p) {
            case 0: return "+" + (2 * lv) + "% daño";
            case 1: return "+" + (5 * lv) + " vida";
            default: return "+" + (15 * lv) + " oro inicial";
        }
    }

    public static void applyStats(Stats st, Save s) {
        st.dmgMul *= 1 + 0.02f * level(s, 0);
        st.maxHp += 5 * level(s, 1);
    }

    public static int startGold(Save s) { return 15 * level(s, 2); }
}
