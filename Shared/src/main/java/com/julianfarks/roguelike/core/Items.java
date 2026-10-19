package com.julianfarks.roguelike.core;

/** Armas secundarias, granadas y armas especiales (se consiguen en cofres secretos y por desbloqueos). */
final class Items {
    private Items() {}

    // ---- armas secundarias (gastan municion). Los ids 1-4 son los originales (los guardados los usan): NO renumerar.
    static final int SEC_NONE = 0, SEC_KNIFE = 1, SEC_BOLT = 2, SEC_AXE = 3, SEC_ORB = 4, SEC_BOW = 5, SEC_CHAKRAM = 6, SEC_WAND = 7, SEC_SPEAR = 8, SEC_EMBER = 9, SEC_SUMMON = 10, SEC_COUNT = 11;
    static final String[] SEC_NAME = {"-", "Cuchillos arrojadizos", "Ballesta rúnica", "Hacha arrojadiza", "Orbe arcano",
            "Arco de cazador", "Chakram", "Varita prismática", "Lanza arrojadiza", "Cañón de brasas", "Cetro de invocación"};
    static final String[] SEC_ICON = {"", "w_knife", "w_bolt", "w_axe", "w_orb", "w_bow", "w_chakram", "w_wand", "w_spear", "w_ember", "w_summon"};
    static final int[] SEC_AMMO = {0, 14, 9, 7, 10, 16, 12, 18, 6, 10, 5};
    static final int[] SEC_COL = {0xFFFFFF, 0xD0D8E8, 0xFFD25A, 0xFF7A5A, 0xA060FF, 0x7AE04A, 0x7AF0FF, 0xFF9ADC, 0xC8B090, 0xFF8A30, 0x70F0D0};
    /** Rareza (0 comun .. 3 epica). Antes vivia en ChestLoot con 5 valores. */
    static final int[] SEC_RAR = {0, 0, 1, 2, 3, 1, 3, 2, 1, 2, 3};
    /** Estadisticas de ficha (las mismas que usa el codigo de disparo): dano por proyectil (x dano base), proyectiles por uso, enfriamiento (s), alcance (px). */
    static final float[] SEC_DMG = {0, 0.65f, 2.1f, 2.4f, 1.5f, 1.5f, 1.1f, 1.2f, 2.6f, 0.7f, 0.55f};
    static final int[] SEC_SHOTS = {0, 3, 1, 1, 1, 1, 1, 1, 1, 3, 1};
    static final float[] SEC_CD = {0, 0.32f, 0.32f, 0.32f, 0.32f, 0.42f, 0.55f, 0.28f, 0.75f, 0.50f, 1.0f};
    static final int[] SEC_RANGE = {0, 420, 750, 330, 420, 640, 165, 400, 600, 135, 220};
    /** Estilo de combate (una linea). */
    static final String[] SEC_STYLE = {"", "Ráfaga en abanico: cubre muchos enemigos cercanos.", "Disparo recto y potente que atraviesa.",
            "Arco alto y pesado: golpea por encima y atraviesa.", "Esfera que persigue y explota al impactar.",
            "Flecha en parábola: cuanto más lejos vuela, más daño hace.", "Gira hacia delante y regresa a tu mano: golpea a la ida y a la vuelta.",
            "Alterna fuego, hielo y rayo en cada disparo.", "Lanzamiento largo: atraviesa y gana daño con cada enemigo.",
            "Ráfaga corta de brasas que prende fuego de cerca.", "Invoca espíritus temporales que atacan por ti."};
    /** Efecto especial (texto de ficha). */
    static final String[] SEC_FX = {"", "-", "Atraviesa 2 enemigos", "Atraviesa 3 enemigos", "Persigue y explota",
            "+90% de daño a máxima distancia", "Vuelve al jugador (máx. 1 en vuelo)", "Quema · congela · aturde (rota)", "Atraviesa 5 · +15% de daño por enemigo",
            "Quema 2.5 s · 3 proyectiles", "Hasta 2 espíritus · 10 s cada uno"};

    // ---- granadas (boton GRAN)
    static final int GR_NONE = 0, GR_FRAG = 1, GR_FIRE = 2, GR_ICE = 3, GR_POISON = 4, GR_STORM = 5, GR_COUNT = 6;
    static final String[] GR_NAME = {"-", "Granada de fragmentación", "Granada incendiaria", "Granada de hielo", "Granada tóxica", "Granada de tormenta"};
    static final String[] GR_ICON = {"", "skull", "burn", "freeze", "poison", "shock"};
    static final int[] GR_COL = {0xFFFFFF, 0xFFB040, 0xFF6A20, 0x7AF0FF, 0x7AE04A, 0xFFE860};

    // ---- escudos (boton ESCUDO: mantener = bloquear; pulsar justo antes del golpe = PARRY)
    static final int SH_COUNT = 4;
    static final String[] SH_NAME = {"Escudo de madera", "Escudo de acero", "Escudo rúnico", "Escudo de espinas"};
    /** Categoria del escudo: 0 basico, 1 intermedio, 2 superior (coincide con su rareza en los cofres). */
    static final int[] SH_TIER = {0, 1, 2, 2};
    /** Ventana de PARRY en segundos desde que se pulsa el boton (cuanto mejor el escudo, mas generosa). Era 0.20/0.17/0.15/0.17: justo al reves. */
    static final float[] SH_WIN = {0.20f, 0.28f, 0.36f, 0.33f};
    /** Enfriamiento tras pulsar (acierte o no). Crece con la ventana: el parry sigue sin poder encadenarse ni pulsarse a ciegas. */
    static final float[] SH_CD = {0.70f, 0.80f, 0.95f, 0.90f};
    static final float[] SH_BLK = {0.45f, 0.30f, 0.30f, 0.35f};     // fraccion del daño que pasa al bloquear
    static final int[] SH_COL = {0x9A6A3A, 0xA8B4C8, 0x7A60E0, 0x5AB04A};
    static final String[] SH_DESC = {"Parry 0.20s · bloquea 55%", "Parry 0.28s · bloquea 70%", "Parry 0.36s · explosión al parry · bloquea 70%", "Parry 0.33s · devuelve daño al bloquear"};

    static final String[] SEC_DESC = {"", "3 cuchillos en abanico · daño 0.65x", "Atraviesa 2 enemigos · daño 2.1x", "Arco alto, atraviesa 3 · daño 2.4x", "Persigue y explota · daño 1.5x",
            "Flecha en parábola · hasta +90% de daño lejos", "Regresa tras lanzarlo · daño 1.1x", "Fuego, hielo y rayo · daño 1.2x", "Atraviesa 5 · daño 2.6x", "3 brasas cortas · quema · daño 0.7x", "2 espíritus · 10 s"};
    static final String[] GR_DESC = {"", "Explosión grande · daño 3.0x", "Quema 4s · daño 1.7x", "Congela 1.8s · daño 1.3x", "Veneno 5s · radio enorme", "Aturde 1.2s · daño 1.8x"};

    // ---- armas especiales (mejoran el arma principal toda la partida)
    static final int SP_COUNT = 9;
    static final String[] SP_NAME = {"-", "Filo Ígneo", "Colmillo Gélido", "Daga Venenosa", "Hacha Carmesí", "Lanza Relámpago", "Hoja del Eclipse", "Mandoble Pesado", "Hoja Veloz"};
    static final String[] SP_DESC = {"", "+10% daño · quema al golpear", "Congela y ralentiza al golpear", "Envenena al golpear", "+15% daño · roba vida", "+8% crítico · descargas", "+25% daño · críticos más fuertes", "+38% daño · ataques 18% más lentos", "+30% velocidad de ataque · -8% daño"};
    static final int[] SP_COL = {0xFFFFFF, 0xFF7A3A, 0x7AF0FF, 0x7AE04A, 0xFF4060, 0xFFE860, 0xC8A0FF, 0xE0A060, 0x80E0C0};

    static void applySpecial(RunState rs, Stats s) {
        switch (rs.special) {
            case 1: s.dmgMul *= 1.10f; s.burn += 0.35f; break;
            case 2: s.freeze += 0.30f; break;
            case 3: s.poison += 0.35f; break;
            case 4: s.dmgMul *= 1.15f; s.lifesteal += 0.05f; break;
            case 5: s.critChance += 0.08f; s.shock += 0.30f; break;
            case 6: s.dmgMul *= 1.25f; s.critMul += 0.3f; break;
            case 7: s.dmgMul *= 1.38f; s.atkSpd *= 0.82f; break;
            case 8: s.atkSpd *= 1.30f; s.dmgMul *= 0.92f; break;
            default: break;
        }
    }

    // ---------------------------------------------------------------- uso
    static void useSecondary(Level lv, Player p) {
        RunState rs = lv.rs;
        if (rs.sec == SEC_NONE || p.secCd > 0) return;
        if (rs.secAmmo <= 0) { lv.text(p.x, p.y - p.bh - 8, "sin munición", 0xA0A0A8, false); Snd.sfx("ui_error", 0.5f); p.secCd = 0.4f; Arsenal.onEmpty(lv, p); return; }
        float d = p.dir();
        float x = p.x + d * 12, y = p.y - 17;
        float base = p.baseDmg(lv) * (1f + 0.25f * rs.secLvl);
        if (rs.sec >= SEC_BOW) { Arsenal.fire(lv, p, rs.sec, base); return; }
        rs.secAmmo--;
        p.secCd = 0.32f * (1f - 0.12f * rs.secLvl);
        base = Arsenal.counterBoost(lv, base);          // contra a distancia: tras un parry perfecto el siguiente disparo hace +50%
        switch (rs.sec) {
            case SEC_KNIFE:
                for (int i = -1; i <= 1; i++) {
                    Proj pr = lv.proj(x, y + i * 3, d * 380, i * 26, base * 0.65f, true, "dagger", 0xD0D8E8);
                    pr.life = 1.1f; pr.radius = 5; pr.knock = 80;
                }
                Snd.sfxv("swing_dagger_1", 0.7f);
                break;
            case SEC_BOLT: {
                Proj pr = lv.proj(x, y, d * 540, 0, base * 2.1f, true, "arrow", 0xFFD25A);
                pr.pierce += 2; pr.life = 1.4f; pr.radius = 6; pr.knock = 150;
                Snd.sfxv("arrow_shot", 0.9f);
                lv.fx("fx_ring", "pulse", x, y, 0.25f, 0xFFD25A, Platform.ADD | Platform.TINT);
                break;
            }
            case SEC_AXE: {
                Proj pr = lv.proj(x, y, d * 230, -230, base * 2.4f, true, "blade", 0xFF7A5A);
                pr.grav = 520; pr.spin = true; pr.spinRate = d * 16; pr.pierce += 3; pr.life = 1.8f; pr.radius = 8; pr.knock = 180; pr.scale = 1.2f;
                Snd.sfxv("swing_great_1", 0.8f);
                break;
            }
            case SEC_ORB: {
                Proj pr = lv.proj(x, y, d * 190, -20, base * 1.5f, true, "voidorb", 0xA060FF);
                pr.homing = 900; pr.explode = 26; pr.life = 2.2f; pr.radius = 6; pr.explodeFx = "fx_void:hole";
                Snd.sfxv("hit_magic", 0.7f);
                lv.fx("fx_ring", "pulse", x, y, 0.3f, 0xA060FF, Platform.ADD | Platform.TINT);
                break;
            }
            default: break;
        }
        p.vx -= d * 14;
        lv.ps.burst(lv.rng, x, y, SEC_COL[rs.sec], 4, 60, 0.2f, 2, 0, true);
    }

    static void throwGrenade(Level lv, Player p) {
        RunState rs = lv.rs;
        if (rs.gren == GR_NONE || p.grenCd > 0) return;
        if (rs.grenCount <= 0) { lv.text(p.x, p.y - p.bh - 8, "sin granadas", 0xA0A0A8, false); Snd.sfx("ui_error", 0.5f); p.grenCd = 0.4f; return; }
        float d = p.dir();
        float x = p.x + d * 8, y = p.y - 20;
        float base = p.baseDmg(lv);
        rs.grenCount--;
        p.grenCd = 0.55f;
        Proj g = lv.proj(x, y, d * 175 + p.vx * 0.3f, -250, base * 2.2f, true, "fireball", GR_COL[rs.gren]);
        g.grav = 900; g.special = 2; g.life = 1.15f; g.radius = 6; g.spin = true; g.spinRate = d * 14; g.knock = 200; g.trail = true; g.scale = 0.9f;
        switch (rs.gren) {
            case GR_FRAG: g.sprite = "spike"; g.explode = 56; g.dmg = base * 3.0f; g.explodeFx = "fx_explosion:a"; break;
            case GR_FIRE: g.sprite = "fireball"; g.explode = 50; g.dmg = base * 1.7f; g.status = Ent.BURN; g.statusDur = 4f; g.statusPow = 8f; g.explodeFx = "fx_fire:pillar"; break;
            case GR_ICE: g.sprite = "iceshard"; g.explode = 60; g.dmg = base * 1.3f; g.status = Ent.FREEZE; g.statusDur = 1.8f; g.explodeFx = "fx_ice:burst"; break;
            case GR_POISON: g.sprite = "poison"; g.explode = 64; g.dmg = base * 1.0f; g.status = Ent.POISON; g.statusDur = 5f; g.statusPow = 8f; g.explodeFx = "fx_smoke:big"; break;
            case GR_STORM: g.sprite = "bolt"; g.explode = 72; g.dmg = base * 1.8f; g.status = Ent.STUN; g.statusDur = 1.2f; g.explodeFx = "fx_shock:wave"; break;
            default: break;
        }
        g.dmg *= 1f + 0.25f * rs.grenLvl; g.explode *= 1f + 0.15f * rs.grenLvl;
        g.hitSfx = "proj_hit";
        p.vx -= d * 10;
        Snd.sfxv("swing_air", 0.8f);
        if (rs.grenCount <= 0) rs.grenCount = 0;
    }

    // ---------------------------------------------------------------- cofres secretos
    /** Cofre secreto: solo el botin base (oro y almas); la recompensa se elige entre 3 opciones (ChestLoot). */
    static void secretChestDrops(Level lv, RunState rs, float x, float y) {
        Rng r = lv.rng;
        lv.dropGold(x, y - 14, Math.round((70 + 20 * rs.stage + r.i(50)) * rs.stats.goldMul));
        lv.dropSouls(x, y - 14, 10 + 3 * rs.stage);
        lv.ps.burst(lv.rng, x, y - 14, 0xD8B0FF, 26, 130, 0.9f, 3, 80, true);
    }

    /** Abre un cofre secreto: da botin variado. */
    static void openSecretChest(Level lv, RunState rs, float x, float y) {
        Rng r = lv.rng;
        lv.dropGold(x, y - 14, Math.round((70 + 20 * rs.stage + r.i(50)) * rs.stats.goldMul));
        lv.dropSouls(x, y - 14, 10 + 3 * rs.stage);
        int roll = r.i(100);
        String msg; int col;
        if (roll >= 66 && roll < 80) {
            int t;
            int tries = 0;
            do { t = r.i(SH_COUNT); tries++; } while (t == rs.shield && tries < 8);
            rs.shield = t;
            msg = "¡" + SH_NAME[t] + "!"; col = SH_COL[t] == 0 ? 0xFFFFFF : SH_COL[t] | 0x303030;
            lv.text(x, y - 56, SH_DESC[t], 0xE8E0E0, false);
        } else if (roll < 22 && rs.special == 0 || (roll < 14 && rs.special != 0)) {
            int sp;
            int tries = 0;
            do { sp = 1 + r.i(SP_COUNT - 1); tries++; } while (sp == rs.special && tries < 8);
            rs.special = sp;
            rs.recalc();
            msg = "¡" + SP_NAME[sp] + "!"; col = SP_COL[sp];
            lv.text(x, y - 56, SP_DESC[sp], 0xE8E0E0, false);
        } else if (roll < 42) {
            int t = 1 + r.i(SEC_COUNT - 1);
            lv.text(x, y - 56, SEC_DESC[t], 0xE8E0E0, false);
            if (rs.sec == t) rs.secAmmo = Math.min(SEC_AMMO[t] * 2, rs.secAmmo + SEC_AMMO[t]);
            else { rs.sec = t; rs.secAmmo = SEC_AMMO[t]; }
            msg = "¡" + SEC_NAME[t] + "!"; col = SEC_COL[t];
        } else if (roll < 66) {
            int t = 1 + r.i(GR_COUNT - 1);
            lv.text(x, y - 56, GR_DESC[t], 0xE8E0E0, false);
            int n = 3 + r.i(3);
            if (rs.gren == t) rs.grenCount = Math.min(12, rs.grenCount + n);
            else { rs.gren = t; rs.grenCount = n; }
            msg = "¡" + n + "x " + GR_NAME[t] + "!"; col = GR_COL[t];
        } else {
            lv.drop(Pickup.POTION, x - 8, y - 14, 1); lv.drop(Pickup.POTION, x + 8, y - 14, 1);
            lv.drop(Pickup.HEART, x, y - 14, 1);
            msg = "¡Pociones de vida!"; col = 0xFF5A7A;
        }
        if (r.chance(0.45f)) lv.drop(Pickup.POTION, x, y - 14, 1);
        if (r.chance(0.5f) && rs.sec != SEC_NONE) rs.secAmmo = Math.min(SEC_AMMO[rs.sec] * 2, rs.secAmmo + SEC_AMMO[rs.sec] / 2);
        lv.text(x, y - 44, msg, col, true);
        lv.ps.burst(lv.rng, x, y - 14, col, 26, 130, 0.9f, 3, 80, true);
        lv.fx("fx_star", "burst", x, y - 20, 1.3f, col, Platform.ADD | Platform.TINT);
        Snd.sfx("secret", 1f);
    }
}
