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
    public int damageTaken;
    public final boolean[] relicsThisRun = new boolean[8];
    public boolean won, finalRun;
    public boolean sandbox;     // laboratorio del Modo Desarrollador: no toca guardados ni progreso, jugador invulnerable

    public RunState(ClassDef cls, long seed, int asc) {
        this.cls = cls;
        this.rng = new Rng(seed);
        this.asc = asc;
        this.diff = Save.S.diffSel;
        stats.recalc(this);
        Unlocks.applyStart(this);
        stats.recalc(this);
        hp = stats.maxHp;
        potions = stats.potionsMax;
        gold = 25 * Save.S.meta[2];
    }

    public void recalc() {
        float ratio = stats.maxHp > 0 ? hp / stats.maxHp : 1f;
        stats.recalc(this);
        hp = Math.min(stats.maxHp, Math.max(hp, ratio * stats.maxHp * 0 + hp));
    }

    public int power() { return stage * 6 + roomNo + asc * 3; }
    public float diffHp() { return diff == 0 ? 0.72f : (diff == 2 ? 1.35f : 1f); }
    public float diffDmg() { return diff == 0 ? 0.6f : (diff == 2 ? 1.4f : 1f); }
    public float diffSouls() { return diff == 0 ? 0.7f : (diff == 2 ? 1.4f : 1f); }
    public float enemyHpMul() { return (1f + 0.16f * power() + 0.10f * asc) * diffHp(); }
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
