package com.julianfarks.roguelike.core;

/** Estadisticas derivadas del jugador (clase + mejoras permanentes + bendiciones). */
public final class Stats {
    public float maxHp, dmgMul, critChance, critMul, speedMul, dmgTaken, lifesteal, skillDmg, cdMul, soulMul, goldMul;
    public float burn, freeze, shock, poison, exec, ultGain, eclipseCd, magnet, atkSpd;
    public int extraJumps, vengeance, wave, egida, giant, shadowRoll, furiaCap, shieldLvl, revive, fantasma;
    public int potionsMax, luck;
    public float revivePct;

    public void recalc(RunState rs) {
        ClassDef c = rs.cls;
        Save s = Save.S;
        int[] b = rs.bless;
        maxHp = c.hp + 10 * s.meta[0] + 20 * b[Blessing.CORAZON];
        dmgMul = (1 + 0.04f * s.meta[1]) * (1 + 0.15f * b[Blessing.FILO]) * (1 + 0.10f * rs.weaponLvl);
        critChance = c.crit + 0.08f * b[Blessing.CRITICO];
        critMul = 1.6f + 0.2f * b[Blessing.CRITICO];
        speedMul = c.speed * (1 + 0.03f * s.meta[5] + 0.08f * b[Blessing.ALAS]);
        dmgTaken = Math.max(0.25f, (1 - c.armor) * (1 - 0.04f * s.meta[6]) * (1 - 0.08f * b[Blessing.PIEDRA]));
        lifesteal = c.lifesteal + 0.03f * b[Blessing.SANGRE];
        skillDmg = 1 + 0.2f * b[Blessing.HABILIDAD];
        cdMul = Math.max(0.4f, 1 - 0.12f * b[Blessing.ENFRIAMIENTO]);
        soulMul = (1 + 0.08f * s.meta[3]) * (1 + 0.3f * b[Blessing.ALMA]);
        goldMul = 1 + 0.3f * b[Blessing.FORTUNA];
        burn = 0.25f * b[Blessing.BRASAS] + (c.id == 2 ? 0.30f : 0);
        freeze = 0.20f * b[Blessing.GLACIAL] + (c.id == 4 ? 0.35f : 0);
        shock = 0.15f * b[Blessing.CHISPA] + (c.id == 3 ? 0.15f : 0);
        poison = 0.25f * b[Blessing.ESPINAS] + (c.id == 5 ? 0.35f : 0);
        extraJumps = 1 + (b[Blessing.DOBLE_SALTO] > 0 ? 1 : 0);
        exec = 0.4f * b[Blessing.EJECUTOR];
        vengeance = b[Blessing.VENGANZA];
        wave = b[Blessing.ONDA];
        egida = b[Blessing.EGIDA];
        giant = b[Blessing.GIGANTE];
        shadowRoll = b[Blessing.SOMBRA];
        fantasma = b[Blessing.FANTASMA];
        furiaCap = b[Blessing.FURIA] > 0 ? 5 + 2 * (b[Blessing.FURIA] - 1) : 0;
        shieldLvl = b[Blessing.ESCUDO];
        ultGain = (1 + 0.2f * b[Blessing.SABIO]) * (c.id == 8 ? 1.25f : 1f);
        eclipseCd = b[Blessing.ECLIPSE] > 0 ? (b[Blessing.ECLIPSE] == 1 ? 12f : 8f) : 0f;
        magnet = 56 + 46 * b[Blessing.IMAN];
        potionsMax = 2 + s.meta[4];
        revive = 0; revivePct = 0;
        if (b[Blessing.SEGUNDA] > 0) { revive = 1; revivePct = 0.35f; }
        else if (s.meta[7] > 0) { revive = 1; revivePct = s.meta[7] == 1 ? 0.25f : 0.5f; }
        atkSpd = 1f;
        Items.applySpecial(rs, this);
        Unlocks.applyStats(rs, this);
        ChestLoot.applyStats(rs, this);
        StartBlessing.applyStats(rs, this);
        Events.applyStats(rs, this);
    }
}
