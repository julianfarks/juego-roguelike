package com.julianfarks.roguelike.core;

/**
 * Bendicion inicial de la expedicion: se ofrecen tres al azar en la preparacion; cada una da una ventaja y cobra una
 * contrapartida pequena. No cuesta nada (ni almas ni gemas) y no sustituye a las bendiciones de los altares.
 */
public final class StartBlessing {
    public final int id;
    public final String icon, name, pro, con, sp, sc;   // pro/con completos y sp/sc abreviados (tarjetas)

    private StartBlessing(int id, String icon, String name, String pro, String con, String sp, String sc) { this.id = id; this.icon = icon; this.name = name; this.pro = pro; this.con = con; this.sp = sp; this.sc = sc; }

    public static final StartBlessing[] ALL = {
            new StartBlessing(0, "b_filo", "Filo Hambriento", "+12% de daño", "-10% de vida máxima", "+12% daño", "-10% vida"),
            new StartBlessing(1, "b_piedra", "Piel de Piedra", "-10% de daño recibido", "-6% de velocidad", "-10% recibido", "-6% veloc."),
            new StartBlessing(2, "b_alas", "Pies de Viento", "+10% de velocidad", "+8% de daño recibido", "+10% veloc.", "+8% recibido"),
            new StartBlessing(3, "b_fortuna", "Bolsa Pesada", "+60 de oro inicial", "1 poción menos", "+60 oro", "-1 poción"),
            new StartBlessing(4, "b_alma", "Sed de Almas", "+25% de almas ganadas", "-8% de daño", "+25% almas", "-8% daño"),
            new StartBlessing(5, "b_critico", "Pacto Frágil", "+12% de golpe crítico", "-15% de vida máxima", "+12% crítico", "-15% vida"),
            new StartBlessing(6, "b_enfriamiento", "Reflejo Veloz", "Habilidades 12% más rápidas", "-10% de daño", "Habil. +12%", "-10% daño"),
            new StartBlessing(7, "b_iman", "Provisiones", "+1 poción", "-15% de oro ganado", "+1 poción", "-15% oro"),
    };

    public static StartBlessing get(int id) { return id >= 0 && id < ALL.length ? ALL[id] : null; }

    /** Tres bendiciones distintas al azar. */
    public static int[] roll(Rng r) {
        int[] out = new int[3];
        java.util.List<Integer> pool = new java.util.ArrayList<>();
        for (int i = 0; i < ALL.length; i++) pool.add(i);
        for (int i = 0; i < 3; i++) out[i] = pool.remove(r.i(pool.size()));
        return out;
    }

    static void applyStats(RunState rs, Stats st) {
        switch (rs.startBless) {
            case 0: st.dmgMul *= 1.12f; st.maxHp *= 0.90f; break;
            case 1: st.dmgTaken *= 0.90f; st.speedMul *= 0.94f; break;
            case 2: st.speedMul *= 1.10f; st.dmgTaken *= 1.08f; break;
            case 3: st.potionsMax = Math.max(1, st.potionsMax - 1); break;
            case 4: st.soulMul *= 1.25f; st.dmgMul *= 0.92f; break;
            case 5: st.critChance += 0.12f; st.maxHp *= 0.85f; break;
            case 6: st.cdMul = Math.max(0.4f, st.cdMul * 0.88f); st.dmgMul *= 0.90f; break;
            case 7: st.potionsMax += 1; st.goldMul *= 0.85f; break;
            default: break;
        }
    }

    /** Efectos que solo ocurren al empezar la run (oro inicial). */
    static void applyStart(RunState rs) {
        if (rs.startBless == 3) rs.gold += 60;
    }
}
