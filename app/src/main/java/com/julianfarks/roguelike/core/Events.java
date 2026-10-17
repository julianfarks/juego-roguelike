package com.julianfarks.roguelike.core;

/**
 * Sucesos especiales de una run: salas opcionales a las que se llega por una puerta lateral de colores tras despejar una sala.
 * Nunca estan en la ruta principal: su puerta de salida lleva a la misma sala siguiente que la puerta normal, y no cambian
 * el numero de sala. Maximo uno por bioma y un limite de pactos por run (sin acumulacion ilimitada).
 */
final class Events {
    private Events() {}

    static final int NONE = 0, MERCHANT = 1, SPIRIT = 2, TRIAL = 3, SECRET = 4, CAPTIVE = 5, SANCTUARY = 6, COUNT = 7;
    static final String[] NAME = {"", "Mercader errante", "Espíritu del abismo", "Prueba de combate", "Cámara secreta", "Prisionero", "Santuario de pactos"};
    static final String[] SUB = {"", "Pocas existencias, buenos precios", "Ofrece poder a cambio de un recurso", "Elite y recompensa superior", "Una reliquia te espera", "Libéralo derrotando a sus guardias", "Dos pactos: ventaja y precio"};
    static final String[] ICON = {"", "shop", "soul", "elite", "relic", "heart", "altar"};
    static final int[] GLOW = {0, 0xFFA040, 0x7AC8F0, 0xFF5A30, 0xFFD45A, 0xB8A0D0, 0xAA6EFF};
    static final int[] WEIGHT = {0, 22, 18, 16, 10, 16, 18};
    static final float CHANCE = 0.20f;          // por sala elegible (hasta 3 por bioma, maximo 1 suceso por bioma)
    static final int MAX_PACTS = 2;             // pactos por run

    /** Decide si tras despejar una sala aparece una puerta de suceso, y cual (0 = ninguna). */
    static int roll(RunState rs, Rng r, int next) {
        if (rs.isTest() || rs.eventBiomeDone || next > 3 || rs.boss()) return NONE;
        String force = System.getenv("BOT_EVENT");
        if (force != null) { int k = Integer.parseInt(force); return k > 0 && k < COUNT ? k : NONE; }
        if (!r.chance(CHANCE)) return NONE;
        int tot = 0;
        for (int k = 1; k < COUNT; k++) if (allowed(rs, k)) tot += WEIGHT[k];
        int x = r.i(Math.max(1, tot));
        for (int k = 1; k < COUNT; k++) {
            if (!allowed(rs, k)) continue;
            x -= WEIGHT[k];
            if (x < 0) return k;
        }
        return NONE;
    }

    static boolean allowed(RunState rs, int kind) {
        if (kind == SANCTUARY && rs.pactCount() >= MAX_PACTS) return false;
        if (kind == SECRET && rs.eventsThisRun[SECRET] > 0) return false;      // una reliquia secreta por run
        return true;
    }

    /**
     * Posicion {x, y} (pixeles) de la puerta lateral: a la izquierda de la salida y de los cofres de ronda, sobre un tramo
     * transitable hasta la salida (sin fosos ni pinchos, desniveles de a lo mas 1 baldosa, con aire encima). null si no hay sitio.
     */
    static float[] sideDoor(Room rm) {
        if (rm.ground == null) return null;
        int et = (int) (rm.exitX / Room.TS);
        if (et < 0 || et >= rm.w || rm.ground[et] <= 0) return null;
        for (int t = et - 9; t >= Math.max(8, et - 40); t--) {
            int gt = rm.ground[t];
            if (gt <= 0) continue;
            boolean ok = true;
            for (int x = t - 1; x <= et + 1 && ok; x++) {
                if (x < 0 || x >= rm.w || rm.ground[x] <= 0) { ok = false; break; }
                if (x < rm.w - 1 && rm.ground[x + 1] > 0 && Math.abs(rm.ground[x + 1] - rm.ground[x]) > 1) ok = false;
                int g = rm.ground[x];
                for (int k = 1; k <= 4; k++) if (rm.tile(x, g - k) != Room.AIR) ok = false;
            }
            if (ok) return new float[]{t * Room.TS + 8, gt * Room.TS};
        }
        return null;
    }

    // ------------------------------------------------------------------ pactos del santuario
    static final class Pact {
        final int id; final String name, icon, pro, con;
        Pact(int id, String name, String icon, String pro, String con) { this.id = id; this.name = name; this.icon = icon; this.pro = pro; this.con = con; }
    }

    static final Pact[] PACTS = {
            new Pact(0, "Pacto del Alba", "b_filo", "+18% de daño", "-12% de vida máxima"),
            new Pact(1, "Pacto de Piedra", "b_piedra", "-14% de daño recibido", "-8% de velocidad"),
            new Pact(2, "Pacto del Viento", "b_alas", "+12% velocidad y +6% crítico", "+10% de daño recibido"),
            new Pact(3, "Pacto de Sangre", "b_sangre", "+5% de robo de vida", "-10% de daño"),
            new Pact(4, "Pacto del Sabio", "b_habilidad", "Habilidades 15% más rápidas", "-1 frasco máximo"),
            new Pact(5, "Pacto Avaro", "b_fortuna", "+40% de oro", "+8% de daño recibido"),
    };

    /** Dos pactos distintos, que el jugador aun no tenga. */
    static int[] rollPacts(RunState rs, Rng r) {
        java.util.List<Integer> pool = new java.util.ArrayList<>();
        for (Pact p : PACTS) if (rs.pacts[p.id] == 0) pool.add(p.id);
        int n = Math.min(2, pool.size());
        int[] out = new int[n];
        for (int i = 0; i < n; i++) out[i] = pool.remove(r.i(pool.size()));
        return out;
    }

    static void applyStats(RunState rs, Stats st) {
        for (Pact p : PACTS) {
            if (rs.pacts[p.id] <= 0) continue;
            switch (p.id) {
                case 0: st.dmgMul *= 1.18f; st.maxHp *= 0.88f; break;
                case 1: st.dmgTaken *= 0.86f; st.speedMul *= 0.92f; break;
                case 2: st.speedMul *= 1.12f; st.critChance += 0.06f; st.dmgTaken *= 1.10f; break;
                case 3: st.lifesteal += 0.05f; st.dmgMul *= 0.90f; break;
                case 4: st.cdMul = Math.max(0.4f, st.cdMul * 0.85f); st.potionsMax = Math.max(1, st.potionsMax - 1); break;
                case 5: st.goldMul *= 1.40f; st.dmgTaken *= 1.08f; break;
                default: break;
            }
        }
    }

    // ------------------------------------------------------------------ costes del espiritu
    static int spiritHpCost(RunState rs) { return Math.round(rs.stats.maxHp * 0.20f); }
    static boolean spiritHpOk(RunState rs) { return rs.hp > rs.stats.maxHp * 0.45f; }
    static int spiritGoldCost(RunState rs) { return 70 + 25 * rs.stage; }
}
