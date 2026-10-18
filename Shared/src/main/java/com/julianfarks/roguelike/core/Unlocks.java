package com.julianfarks.roguelike.core;

/** Desbloqueos permanentes por enemigos derrotados (cada 50). */
final class Unlocks {
    private Unlocks() {}
    static final int COUNT = 10;
    static final int STEP = 50;
    static final String[] NAME = {
            "Cuchillos arrojadizos", "Granada incendiaria", "Sed de sangre", "Ballesta rúnica", "Granada de hielo",
            "Pies ligeros", "Piel de piedra", "Orbe arcano", "Granada de tormenta", "Maestría de combate"};
    static final String[] DESC = {
            "Empiezas cada partida con cuchillos (botón de arma secundaria).",
            "Empiezas con 3 granadas incendiarias.",
            "Habilidad pasiva: recuperas un poco de vida al golpear.",
            "Arma secundaria inicial: ballesta que atraviesa enemigos.",
            "Empiezas con 3 granadas de hielo que congelan.",
            "Habilidad pasiva: +6% de velocidad de movimiento.",
            "Habilidad pasiva: recibes 7% menos de daño.",
            "Arma secundaria inicial: orbe que persigue enemigos.",
            "Empiezas con 3 granadas de tormenta que aturden.",
            "Habilidad pasiva: +8% de daño y +4% de crítico."};
    static final String[] KIND = {"Arma", "Granada", "Habilidad", "Arma", "Granada", "Habilidad", "Habilidad", "Arma", "Granada", "Habilidad"};

    static int need(int i) { return (i + 1) * STEP; }

    static boolean has(int i) { return Save.S.unlocked[i]; }

    /** Objetos iniciales de la partida. */
    static void applyStart(RunState rs) {
        Save s = Save.S;
        if (s.unlocked[7]) { rs.sec = Items.SEC_ORB; }
        else if (s.unlocked[3]) { rs.sec = Items.SEC_BOLT; }
        else if (s.unlocked[0]) { rs.sec = Items.SEC_KNIFE; }
        if (rs.sec != 0) rs.secAmmo = Items.SEC_AMMO[rs.sec];
        if (s.unlocked[8]) rs.gren = Items.GR_STORM;
        else if (s.unlocked[4]) rs.gren = Items.GR_ICE;
        else if (s.unlocked[1]) rs.gren = Items.GR_FIRE;
        if (rs.gren != 0) rs.grenCount = 3;
    }

    static void applyStats(RunState rs, Stats st) {
        Save s = Save.S;
        if (s.unlocked[2]) st.lifesteal += 0.02f;
        if (s.unlocked[5]) st.speedMul *= 1.06f;
        if (s.unlocked[6]) st.dmgTaken *= 0.93f;
        if (s.unlocked[9]) { st.dmgMul *= 1.08f; st.critChance += 0.04f; }
    }

    /** Se llama al derrotar un enemigo: comprueba nuevos desbloqueos. */
    static void check(Level lv) {
        if (lv.rs.sandbox) return;
        Save s = Save.S;
        int total = s.kills + lv.rs.kills;
        boolean any = false;
        for (int i = 0; i < COUNT; i++) {
            if (s.unlocked[i] || total < need(i)) continue;
            s.unlocked[i] = true; any = true;
            lv.unlockTitle = "¡DESBLOQUEADO!";
            lv.unlockSub = NAME[i] + " · " + KIND[i];
            Snd.sfx("ui_unlock", 1f);
            // entregar de inmediato lo que da un objeto
            RunState rs = lv.rs;
            if ((i == 0 || i == 3 || i == 7) && (rs.sec == 0 || rs.sec < (i == 0 ? 1 : i == 3 ? 2 : 4))) { rs.sec = i == 0 ? Items.SEC_KNIFE : i == 3 ? Items.SEC_BOLT : Items.SEC_ORB; rs.secAmmo = Items.SEC_AMMO[rs.sec]; }
            if (i == 1 || i == 4 || i == 8) { rs.gren = i == 1 ? Items.GR_FIRE : i == 4 ? Items.GR_ICE : Items.GR_STORM; rs.grenCount = Math.max(rs.grenCount, 3); }
            rs.recalc();
        }
        if (any) s.write();
    }
}
