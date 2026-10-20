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
    public int stage;                 // tramo de dificultad 0..2, 3 = final (derivado de dungeonNo)
    public int dungeonNo;             // mazmorras superadas en la partida: 0..8 (8 = toca el Cazador)
    /** Tramo segun mazmorras superadas: 3 de tramo 0, 2 de tramo 1, 3 de tramo 2 y luego el Cazador. */
    public static int tierOf(int d) { return d < 3 ? 0 : d < 5 ? 1 : d < 8 ? 2 : 3; }
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
    /** Cargador del arma 2ª equipada (solo armas de cargador, ver Arsenal.MAG): disparos listos. -1 = sin inicializar. secReload: segundos de recarga que faltan (>0 = recargando). secMagId: arma a la que pertenece el cargador. */
    public int secMag = -1, secMagId; public float secReload, secRegenT;
    public boolean secActive;         // true = el boton de ataque dispara el arma secundaria (cambio de arma); false = arma principal
    /** Inventario: objetos obtenidos que aun no se han inspeccionado y los ya vistos (claves "w:id", "b:id", "r:i", "o:..."). Solo de esta partida. */
    public final java.util.LinkedHashSet<String> unseen = new java.util.LinkedHashSet<>();
    public final java.util.HashSet<String> seen = new java.util.HashSet<>();
    public void markNew(String key) { if (!seen.contains(key)) unseen.add(key); }
    public void markSeen(String key) { if (unseen.remove(key) || true) seen.add(key); }
    /** Estado de cada arma secundaria en esta partida: 0 nunca la tuviste, 1 equipada, 2 en el suelo de esta sala, 3 dejada atras (sala abandonada). */
    public final int[] wState = new int[Items.SEC_COUNT];
    public int secretsFound;
    public final int[] cb = new int[ChestLoot.N];     // mejoras de cofres (ver ChestLoot)
    public int grenLvl, secLvl;                      // niveles de mejora de granada y arma secundaria
    public boolean blessingTaken;
    public final int[] pacts = new int[Events.PACTS.length];     // pactos de santuario tomados (0/1)
    public final int[] eventsThisRun = new int[Events.COUNT];
    public boolean eventBiomeDone;      // ya hubo un suceso en este bioma
    public int sideOrigin = -1;         // dentro del mercader errante: tipo de sala (Room.*) a la que se vuelve al salir (-1 = no estamos en una sala secundaria)
    public int chalKind = -1;           // variante del desafio de la sala actual (se guarda para que cargar no la cambie)
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
    // ---- modificadores de sala (desafios nuevos mas alla de la vida de los enemigos); se eligen al cargar cada sala de combate
    public static final int RM_NONE = 0, RM_VOLATILE = 1, RM_SWARM = 2;
    public static final String[] RM_NAME = {"", "Sala volátil", "Sala enjambre"};
    public static final String[] RM_DESC = {"", "Los enemigos explotan al morir: corre del aro rojo", "Más enemigos, más frágiles"};
    public final java.util.Set<Integer> bossRewarded = new java.util.LinkedHashSet<>();   // jefes ya recompensados en esta partida (floor*100+idx en Endless): una sola vez
    /** Marca la recompensa del jefe como entregada; devuelve false si ya se habia entregado (no se duplica al repetir transiciones o cargar). */
    public boolean markBossRewarded(int idx) { return bossRewarded.add((infinite ? floor * 100 : 0) + idx); }
    public int roomMod;
    public static int forceRoomMod = -1;
    /** Elige (de forma determinista por semilla/sala) el modificador de la sala de combate actual. */
    public int rollRoomMod(int roomType, int curEvent) {
        roomMod = RM_NONE;
        if (forceRoomMod >= 0) return roomMod = forceRoomMod;     // solo pruebas del banco
        if (roomType != Room.COMBAT || curEvent != 0 || roomNo == 0 || biome == null || biome.id >= 8) return roomMod;
        float ch = infinite ? Math.min(0.5f, 0.15f + 0.05f * floor) : dungeonNo < 2 ? 0f : Math.min(0.40f, 0.08f * (dungeonNo - 1));
        Rng r = new Rng(seed ^ (dungeonNo * 7919L + roomNo * 104729L + floor * 31L + 12345L));
        if (r.chance(ch)) roomMod = r.chance(0.5f) ? RM_VOLATILE : RM_SWARM;
        return roomMod;
    }
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
        if (sec != 0) { wState[sec] = 1; seen.add("w:" + sec); }     // arma de partida: ya la conoces
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

    public int power() { return infinite ? Infinite.power(floor, roomNo) + asc * 3 : Math.round(dungeonNo * 2.25f) + roomNo + asc * 3; }
    // ---- Balance de campana (8 mazmorras + Cazador): todo escala de forma continua con dungeonNo, no a saltos por tramo
    /** Tramo continuo 0..3 para jefes y recompensas: nunca baja del tramo discreto y sube suave con cada mazmorra superada. */
    public float tierF() { return Math.max(stage, dungeonNo * 0.375f); }
    /** Retos de la campana mas alla de la vida: elites y velocidad crecientes en las ultimas mazmorras. */
    public float campaignEliteChance() { return infinite ? 0f : dungeonNo < 3 ? 0f : Math.min(0.30f, 0.05f * (dungeonNo - 2)); }
    public float campaignSpeedMul() { return infinite ? 1f : dungeonNo >= 7 ? 1.15f : dungeonNo >= 5 ? 1.08f : 1f; }
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

    // ---- Arma principal: configuracion unica del tope y de la curva (nada mas en el codigo fija un nivel maximo)
    public static final int WEAPON_MAX = 20;
    public static final int WEAPON_FAST_LVLS = 5;          // hasta aqui la curva original (+10% de dano, coste +45 por nivel)
    public static final float WEAPON_DMG_FAST = 0.10f, WEAPON_DMG_SLOW = 0.05f;
    public static final int MASTERY_MAX = 10;               // rangos de Maestria tras el nivel maximo (solo Endless)
    public int mastery;
    public boolean masteryMaxed() { return mastery >= MASTERY_MAX; }
    public int masteryCost() { return forgeCost() + 90 * mastery; }
    public boolean weaponMaxed() { return weaponLvl >= WEAPON_MAX; }
    public static float weaponDmgBonus(int lvl) {
        int fast = Math.min(lvl, WEAPON_FAST_LVLS), slow = Math.max(0, lvl - WEAPON_FAST_LVLS);
        return fast * WEAPON_DMG_FAST + slow * WEAPON_DMG_SLOW;
    }
    public int forgeCost() {
        int fast = Math.min(weaponLvl, WEAPON_FAST_LVLS), slow = Math.max(0, weaponLvl - WEAPON_FAST_LVLS);
        return 60 + 45 * fast + 55 * slow;
    }
}
