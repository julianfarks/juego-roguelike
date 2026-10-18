package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/**
 * Estado de ejecucion de las bendiciones durante una run (NO se guarda: todo se reconstruye desde rs.bless al cargar una partida).
 * Contiene las reglas activas ordenadas por disparador, los temporizadores, los canales de mejoras temporales, los presupuestos que
 * limitan los efectos (curacion, oro, reduccion de reutilizacion...) y los espiritus invocados.
 */
final class BlessRt {
    static final int NB = 200;                           // tamano maximo del catalogo (indices de bendicion)

    /** Reglas activas por disparador, con el nivel de su bendicion. */
    BRule[][] byTrig = new BRule[BRule.T_COUNT][];
    /** Reglas de modificadores pasivos por efecto (M_*), indexadas por (efecto - 60). */
    BRule[][] mods = new BRule[48][];
    boolean any;                                         // hay alguna regla activa (si no, todos los ganchos salen al instante)
    long sig = Long.MIN_VALUE;                           // firma de rs.bless para detectar cambios
    boolean[] synOn = new boolean[64];
    int synCount;

    final float[] sv = new float[48];                    // suma de los modificadores estaticos por efecto (M_* - 60)
    float skillMul, skillMulT; boolean empowered;        // habilidad potenciada (NEXTSKILL) durante su lanzamiento
    int hurtAtEnter;
    float t;                                             // tiempo propio (segundos de juego)
    float[] icd = new float[2048];                       // reutilizacion por regla
    int[] offered = new int[NB];                         // veces que se ofrecio cada bendicion en esta partida (variedad de los altares)
    int[] fired = new int[NB];                           // veces que se ejecuto algun efecto de cada bendicion (pruebas/telemetria)
    int[] firedSyn = new int[64];
    float[] tickT = new float[2048];

    // canales de mejoras temporales (BRule.CH_*)
    final float[] chAmt = new float[BRule.CH_COUNT];     // bonus por carga
    final float[] chT = new float[BRule.CH_COUNT];
    final int[] chN = new int[BRule.CH_COUNT];

    float nextHitMul, nextHitT; boolean nextHitCrit;
    float nextSkillMul, nextSkillT;
    float arc;                                           // carga arcana (0..10)
    int hitStreak, critStreak, parryStreak, dodgeStreak, skillCasts;
    float lastKillT = -99f; int killChain;

    // presupuestos por sala
    float healRoom, goldRoom, soulRoom;
    float cdrBucket = 6f;
    int perSecond; float perSecondT;
    int depth;                                           // anidamiento de efectos (los efectos no desencadenan otros efectos)

    float slowT, slowScale = 1f;                         // ralentizacion temporal de los enemigos (Reloj del Destino)
    float spiritBoostT, dodgeLock;
    boolean lowHpPrev;
    float hazardT;                                       // seguimiento de peligros esquivados
    boolean overHazard;
    float formT;                                         // formas (Forma de Sombra...): tiempo restante y temporizador de reutilizacion
    float roomT;
    boolean shadowForm;

    final List<Spirit> spirits = new ArrayList<>();
    final List<Patch> patches = new ArrayList<>();

    /** Espiritu invocado por una bendicion. */
    static final class Spirit {
        BRule rule; int owner; float x, y, phase, cd, flash;
        int color;
    }

    /** Charco de un rastro (fuego, escarcha...). */
    static final class Patch {
        float x, y, t, tick; int kind; float dmg;
    }

    // ---- consultas de canales
    float ch(int c) {
        if (chT[c] <= 0) return 0f;
        float v = chAmt[c] * chN[c];
        switch (c) {
            case BRule.CH_DMG: return Math.min(v, 0.9f);
            case BRule.CH_ATK: return Math.min(v, 0.6f);
            case BRule.CH_SPD: return Math.min(v, 0.5f);
            case BRule.CH_CRIT: return Math.min(v, 0.5f);
            case BRule.CH_TAKEN: return Math.max(v, -0.5f);
            case BRule.CH_SKILL: return Math.min(v, 1.0f);
            case BRule.CH_CDR: return Math.min(v, 0.6f);
            default: return v;
        }
    }

    boolean chOn(int c) { return chT[c] > 0 && chN[c] > 0; }

    void reset() {
        java.util.Arrays.fill(chT, 0f); java.util.Arrays.fill(chN, 0);
        nextHitMul = 0; nextHitT = 0; nextHitCrit = false; nextSkillMul = 0; nextSkillT = 0;
        arc = 0; hitStreak = critStreak = parryStreak = dodgeStreak = 0;
        slowT = 0; spiritBoostT = 0; formT = 0; shadowForm = false;
        patches.clear();
    }

    void roomReset() {
        healRoom = goldRoom = soulRoom = 0; roomT = 0; patches.clear();
    }
}
