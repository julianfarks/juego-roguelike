package com.julianfarks.roguelike.core;

/** Mejoras permanentes del Santuario (se compran con almas). */
public final class Meta {
    private Meta() {}
    public static final int COUNT = 8;
    public static final String[] NAME = {"Vitalidad", "Fuerza", "Bolsa del Viajero", "Cosecha de Almas", "Frascos de Vida", "Agilidad", "Temple", "Segunda Oportunidad"};
    public static final String[] ICON = {"b_corazon", "b_filo", "b_fortuna", "b_alma", "potion", "b_alas", "b_piedra", "b_segunda"};
    public static final int[] MAX = {10, 10, 8, 8, 3, 5, 5, 2};
    public static final int[] BASE_COST = {50, 60, 40, 70, 250, 80, 90, 400};
    public static final int[] STEP_COST = {40, 50, 35, 55, 220, 70, 80, 350};
    public static final String[] DESC = {
            "+10 de vida máxima por nivel.",
            "+4% de daño por nivel.",
            "+25 de oro inicial por nivel.",
            "+8% de almas obtenidas por nivel.",
            "+1 frasco de vida por nivel.",
            "+3% de velocidad de movimiento por nivel.",
            "-4% de daño recibido por nivel.",
            "Al morir revives una vez por run con 25% (50% nv.2) de vida."};

    public static int cost(int idx, int level) { return BASE_COST[idx] + STEP_COST[idx] * level; }

    public static String effect(int idx, int level) {
        switch (idx) {
            case 0: return "+" + (10 * level) + " vida";
            case 1: return "+" + (4 * level) + "% daño";
            case 2: return "+" + (25 * level) + " oro inicial";
            case 3: return "+" + (8 * level) + "% almas";
            case 4: return "+" + level + " frascos";
            case 5: return "+" + (3 * level) + "% velocidad";
            case 6: return "-" + (4 * level) + "% daño recibido";
            default: return level == 0 ? "Sin revivir" : "Revive con " + (level == 1 ? 25 : 50) + "% de vida";
        }
    }

    public static final int[] CLASS_COST = {0, 0, 0, 150, 200, 250, 300, 350, 450, 600};
}
