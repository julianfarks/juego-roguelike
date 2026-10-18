package com.julianfarks.roguelike.core;

/** Companeros (espiritus). Solo uno activo por run: sus efectos no se acumulan entre si. */
public final class Companions {
    private Companions() {}
    public static final int FIRE = 0, ICE = 1, SHADOW = 2, COUNT = 3;
    public static final String[] NAME = {"Ascua", "Escarcha", "Umbra"};
    public static final String[] KIND = {"Espíritu de fuego", "Espíritu de hielo", "Espíritu de sombra"};
    public static final String[] SHEET = {"cmp_fire", "cmp_ice", "cmp_shadow"};
    public static final int[] COLOR = {0xFF8A30, 0x7AC8F0, 0xAA6EFF};
    public static final String[] PASSIVE = {
            "Cada 6 s lanza una chispa al enemigo más cercano (25% de tu daño; 10% contra jefes).",
            "Reduce un 8% el daño que recibes.",
            "Imán +40 y marca los cofres secretos y las puertas ocultas de la sala."};
    public static final String[] UNLOCK = {
            "Derrota a 1 jefe.",
            "Derrota a 3 jefes.",
            "Completa 10 expediciones o llega al piso 5 del modo infinito."};

    /** Condicion real de desbloqueo (se evalua sobre el guardado). */
    public static boolean earned(Save s, int i) {
        switch (i) {
            case FIRE: return s.bossKills >= 1;
            case ICE: return s.bossKills >= 3;
            default: return s.runs >= 10 || s.infBestFloor >= 5;
        }
    }

    public static boolean unlocked(Save s, int i) { return i >= 0 && i < COUNT && (s.compMask & (1 << i)) != 0; }

    /** Registra los desbloqueos nuevos; devuelve el nombre del primero conseguido o null. */
    public static String refresh(Save s) {
        String nw = null;
        for (int i = 0; i < COUNT; i++)
            if (!unlocked(s, i) && earned(s, i)) { s.compMask |= 1 << i; if (nw == null) nw = NAME[i]; }
        if (nw != null) s.write();
        return nw;
    }

    /** Companero seleccionado y valido (desbloqueado) o -1. */
    public static int active(Save s) { return unlocked(s, s.compSel) ? s.compSel : -1; }

    public static void select(Save s, int i) {
        if (i == -1 || unlocked(s, i)) { s.compSel = i; s.write(); }
    }

    public static void applyStats(RunState rs, Stats st) {
        switch (rs.companion) {
            case ICE: st.dmgTaken = Math.max(0.25f, st.dmgTaken * 0.92f); break;
            case SHADOW: st.magnet += 40; break;
            default: break;
        }
    }

    public static String summary(int i) { return i < 0 ? "Sin compañero" : NAME[i] + ": " + PASSIVE[i]; }
}
