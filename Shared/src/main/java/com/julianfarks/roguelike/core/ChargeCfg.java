package com.julianfarks.roguelike.core;

/**
 * Configuracion central del ataque cargado del arma principal (cuerpo a cuerpo). Todo el equilibrio vive aqui.
 * La curva de dano es continua: interpolacion lineal entre los puntos de referencia (tiempo de carga -> multiplicador de dano).
 * Una pulsacion mas corta que TAP es un ataque normal (x1,00 exacto). Pasado MAX el dano no sube mas.
 */
final class ChargeCfg {
    private ChargeCfg() {}
    /** Pulsacion corta = ataque normal. */
    static final float TAP = 0.16f;
    /** Tiempo de carga completa (s). Una mejora futura puede acortarlo pasando otra escala a frac()/mul(). */
    static final float MAX = 2.0f;
    /** Puntos de la curva: tiempo (s) y multiplicador respecto al dano base. */
    static final float[] T = {TAP, 0.5f, 1.0f, 1.5f, 2.0f};
    static final float[] M = {1.00f, 1.20f, 1.50f, 1.85f, 2.25f};
    /** Efectos por nivel de carga (frac 0..1). */
    static final float REACH_BONUS = 0.30f, HEIGHT_BONUS = 0.35f, KNOCK_BONUS = 0.9f, SLOW_MOVE = 0.45f;
    static final float HEAVY_FROM = 0.25f, STUN_FROM = 0.5f, STUN_MIN = 0.25f, STUN_MAX = 0.60f;

    /** Tiempo de carga efectivo (limitado a MAX). */
    static float clampT(float held) { return Math.max(0f, Math.min(MAX, held)); }

    /** Multiplicador de dano para un tiempo de carga (continuo; 1 por debajo de TAP; constante tras MAX). */
    static float mul(float held) {
        if (held < TAP) return 1f;
        float t = clampT(held);
        for (int i = 1; i < T.length; i++) {
            if (t <= T[i]) { float k = (t - T[i - 1]) / (T[i] - T[i - 1]); return M[i - 1] + (M[i] - M[i - 1]) * k; }
        }
        return M[M.length - 1];
    }

    /** Fraccion de carga 0..1 (para efectos): 0 en TAP, 1 en MAX. */
    static float frac(float held) {
        if (held <= TAP) return 0f;
        return Math.min(1f, (held - TAP) / (MAX - TAP));
    }
}
