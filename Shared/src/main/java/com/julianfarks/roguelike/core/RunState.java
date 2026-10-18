package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/** Estado persistente durante una run. */
public final class RunState {
    public static final int ROOMS_PER_BIOME = 5;   // 0,1,2 monstruos (la 1 y 2 con puerta de combate/mini-jefe), 3 tienda general, 4 jefe

    public final ClassDef cls;
    public final Rng rng;
    public final Stats stats = new Stats();
    public final int[] bless = new int[Blessing.ALL.length];
    public int stage;                 // 0..2, 3 = final
    public int roomNo;                // sala dentro del bioma
    public int roomsDone;
    public Biome biome;
    public final List<Integer> visited = new ArrayList<>();
    public int gold, souls, kills, bossKills, potions, weaponLvl;
    public float hp;
    public final float[] cd = new float[4];
    public float ult;
    public boolean reviveUsed;
    public float time;
    public int asc;
    public int diff = 1;                // 0 facil, 1 normal, 2 dificil
    public int sec, secAmmo, gren, grenCount, special, shield;   // objetos de cofres
    public int secretsFound;
    public final int[] cb = new int[ChestLoot.N];     // mejoras de cofres (ver ChestLoot)
    public int grenLvl, secLvl;                      // niveles de mejora de granada y arma secundaria
    public boolean blessingTaken;
    public final int[] pacts = new int[Events.PACTS.length];     // pactos de santuario tomados (0/1)
    public final int[] eventsThisRun = new int[Events.COUNT];
    public boolean eventBiomeDone;      // ya hubo un suceso en este bioma
    public int sideOrigin = -1;         // dentro del mercader errante: tipo de sala (Room.*) a la que se vuelve al salir (-1 = no estamos en una sala secundaria)
    public int curEvent;                // suceso de la sala actual (Events.*)
    public int startBless = -1;          // bendicion inicial elegida en la preparacion (-1 = ninguna)
    public int damageTaken;
    /** Estado de ejecucion de las bendiciones (no se guarda; se reconstruye desde bless[]). */
    public BlessRt bx = new BlessRt();
    public int streak, perfectStreak, roundsThisRun;   // rondas seguidas / perfectas seguidas (estadisticas)
    public final boolean[] relicsThisRun = new boolean[8];
    public boolean won, finalRun;
    // ---- modo infinito
    public boolean infinite, infFromCampaign;
    public Infinite.Ruleset ruleset = Infinite.NORMAL;
    public int floor = 1, floorsDone, revivesUsed, infRooms;   // piso actual (1..), pisos completados, revividas usadas (0..3), salas superadas en infinito
    public boolean devAssisted;                                 // uso gemas de prueba del Modo Desarrollador (resultado NO valido para clasificacion)
    public int infBaseKills, infBaseBoss;                       // bajas/jefes ya contabilizados en la campana (evita contarlos dos veces)
    public float infT0;                                         // tiempo de run al empezar el infinito
    public int credKills, credBoss;                             // ya sumados al perfil por endRun (evita doble conteo)
    public long seed;
    /** Tipo de sesion: NORMAL (progreso real) o TEST (arenas y tiendas del Modo Desarrollador: jamas se guarda ni toca el progreso). */
    public enum Session { NORMAL, TEST }
    public Session session = Session.NORMAL;
    public int mods;            // retos del modo infinito activos (Infinite.M_*)
    public int companion = -1;  // companero activo de esta run (-1 ninguno)
    public boolean sandbox;     // (igual que session==TEST; se mantiene por compatibilidad)
    /** Una sesion de prueba NO puede guardarse, ni dar resultados validos, ni tocar records, estadisticas o recompensas permanentes. */
    public boolean isTest() { return sandbox || session == Session.TEST; }
    public void markTest() { session = Session.TEST; sandbox = true; }

    public RunState(ClassDef cls, long seed, int asc) {
        this.cls = cls;
        this.rng = new Rng(seed);
        this.seed = seed;
        this.asc = asc;
        this.diff = Save.S.diffSel;
        this.companion = Companions.active(Save.S);
        stats.recalc(this);
        Unlocks.applyStart(this);
        stats.recalc(this);
        hp = stats.maxHp;
        potions = stats.potionsMax;
        gold = 25 * Save.S.meta[2] + Garden.startGold(Save.S);
    }

    /** Aplica la bendicion inicial elegida en la preparacion (solo al empezar la run, antes de la primera sala). */
    public void applyStartBlessing(int id) {
        if (StartBlessing.get(id) == null) return;
        startBless = id;
        StartBlessing.applyStart(this);
        stats.recalc(this);
        hp = stats.maxHp;
        potions = stats.potionsMax;
    }

    public int pactCount() { int n = 0; for (int p : pacts) if (p > 0) n++; return n; }
    public boolean boss() { return biome != null && biome.id >= 8; }

    public void recalc() {
        float ratio = stats.maxHp > 0 ? hp / stats.maxHp : 1f;
        stats.recalc(this);
        hp = Math.min(stats.maxHp, Math.max(hp, ratio * stats.maxHp * 0 + hp));
    }

    public int power() { return infinite ? Infinite.power(floor, roomNo) + asc * 3 : stage * 6 + roomNo + asc * 3; }
    public float diffHp() { return diff == 0 ? 0.72f : (diff == 2 ? 1.35f : 1f); }
    public float diffDmg() { return diff == 0 ? 0.6f : (diff == 2 ? 1.4f : 1f); }
    public float diffSouls() { return diff == 0 ? 0.7f : (diff == 2 ? 1.4f : 1f); }
    public float enemyHpMul() { return (1f + 0.16f * power() + 0.10f * asc) * diffHp() * (1f + Math.max(-0.5f, BlessFx.sv(this, BRule.M_ENEMYHP))); }
    public float enemyDmgMul() { return (1f + 0.06f * power() + 0.06f * asc) * diffDmg(); }

    /** Tipos de sala para las puertas: combate normal o mini-jefe (élite). */
    public int[] pickDoorTypes(int count) {
        int[] out = new int[count];
        java.util.Arrays.fill(out, Room.COMBAT);
        return out;
    }

    public static String roomName(int t) {
        switch (t) {
            case Room.COMBAT: return "Combate";
            case Room.ELITE: return "Mini-jefe";
            case Room.BLESSING: return "Altar de bendición";
            case Room.FORGE: return "Forja";
            case Room.SHOP: return "Mercader";
            case Room.FOUNTAIN: return "Fuente de vida";
            case Room.TREASURE: return "Tesoro";
            case Room.REST: return "Tienda general";
            case Room.BOSS: return "Jefe";
            default: return "Sala";
        }
    }

    public static String roomIcon(int t) {
        switch (t) {
            case Room.COMBAT: return "skull";
            case Room.ELITE: return "elite";
            case Room.BLESSING: return "altar";
            case Room.FORGE: return "forge";
            case Room.SHOP: return "shop";
            case Room.FOUNTAIN: return "fountain";
            case Room.TREASURE: return "chest";
            case Room.BOSS: return "boss";
            default: return "door";
        }
    }

    public int forgeCost() { return 60 + 45 * weaponLvl; }
}
