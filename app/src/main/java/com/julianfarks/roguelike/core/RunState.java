package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/** Estado persistente durante una run. */
public final class RunState {
    public static final int ROOMS_PER_BIOME = 6;   // 0 combate, 1-3 elegibles, 4 antesala, 5 jefe

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
    public boolean blessingTaken;
    public int damageTaken;
    public final boolean[] relicsThisRun = new boolean[8];
    public boolean won, finalRun;

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

    /** Pesos de tipos de sala para las puertas. */
    public int[] pickDoorTypes(int count) {
        int[] out = new int[count];
        boolean needBless = !blessingTaken && roomNo >= 2;
        for (int i = 0; i < count; i++) {
            int t;
            int tries = 0;
            do {
                int r = rng.i(100);
                if (r < 38) t = Room.COMBAT;
                else if (r < 52) t = Room.BLESSING;
                else if (r < 62) t = Room.TREASURE;
                else if (r < 72) t = Room.SHOP;
                else if (r < 80) t = Room.FORGE;
                else if (r < 88) t = Room.FOUNTAIN;
                else t = Room.ELITE;
                tries++;
            } while (i > 0 && t == out[0] && tries < 6);
            out[i] = t;
        }
        if (needBless) out[0] = Room.BLESSING;
        // evitar dos salas "de descanso" seguidas dos veces; la primera opcion siempre es de combate o elite si la segunda tampoco es combate
        if (count == 2 && out[0] != Room.COMBAT && out[0] != Room.ELITE && out[1] != Room.COMBAT && out[1] != Room.ELITE && !needBless) out[1] = Room.COMBAT;
        return out;
    }

    public static String roomName(int t) {
        switch (t) {
            case Room.COMBAT: return "Combate";
            case Room.ELITE: return "Élite";
            case Room.BLESSING: return "Altar de bendición";
            case Room.FORGE: return "Forja";
            case Room.SHOP: return "Mercader";
            case Room.FOUNTAIN: return "Fuente de vida";
            case Room.TREASURE: return "Tesoro";
            case Room.REST: return "Antesala";
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
