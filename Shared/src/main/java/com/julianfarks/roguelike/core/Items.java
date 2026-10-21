package com.julianfarks.roguelike.core;

/** Armas secundarias, granadas y armas especiales (se consiguen en cofres secretos y por desbloqueos). */
final class Items {
    private Items() {}

    // ---- armas secundarias (gastan municion). Los ids 1-4 son los originales (los guardados los usan): NO renumerar.
    static final int SEC_NONE = 0, SEC_KNIFE = 1, SEC_BOLT = 2, SEC_AXE = 3, SEC_ORB = 4, SEC_BOW = 5, SEC_CHAKRAM = 6, SEC_WAND = 7, SEC_SPEAR = 8, SEC_EMBER = 9, SEC_SUMMON = 10,
            SEC_DKNIVES = 11, SEC_TWINS = 12, SEC_STILETTO = 13, SEC_CLAWS = 14, SEC_TONFA = 15, SEC_GAUNTLET = 16,
            SEC_LANCE = 17, SEC_HALBERD = 18, SEC_SCYTHE = 19, SEC_WHIP = 20, SEC_CHAIN = 21, SEC_SHORTSWORD = 22, SEC_WARHAMMER = 23,
            SEC_TDAGGER = 24, SEC_SHURIKEN = 25, SEC_ALCHBOMB = 26, SEC_STICKYBOMB = 27,
            SEC_ELEMWAND = 28, SEC_FIREWAND = 29, SEC_ICEWAND = 30, SEC_STORMWAND = 31, SEC_DARKORB = 32, SEC_VENOMCAT = 33, SEC_BLOODSCEPTER = 34, SEC_CRYSTAL = 35, SEC_TALISMAN = 36,
            SEC_COUNT = Wpn.N;

    // Todas las tablas se derivan de Wpn.T (una sola fuente). Los ids 1-10 son los originales: sus valores no cambian.
    static final String[] SEC_NAME = new String[SEC_COUNT], SEC_ICON = new String[SEC_COUNT], SEC_STYLE = new String[SEC_COUNT], SEC_FX = new String[SEC_COUNT], SEC_DESC = new String[SEC_COUNT];
    /** Municion total (cargador + reserva) o energia maxima. En el cuerpo a cuerpo vale 1 y no se gasta (ver infinite). */
    static final int[] SEC_AMMO = new int[SEC_COUNT], SEC_COL = new int[SEC_COUNT], SEC_RAR = new int[SEC_COUNT], SEC_SHOTS = new int[SEC_COUNT], SEC_RANGE = new int[SEC_COUNT], SEC_MAG = new int[SEC_COUNT], SEC_KIND = new int[SEC_COUNT];
    /** Estadisticas de ficha (las mismas que usa el codigo de disparo): dano por proyectil (x dano base), proyectiles por uso, enfriamiento (s), alcance (px). */
    static final float[] SEC_DMG = new float[SEC_COUNT], SEC_CD = new float[SEC_COUNT], SEC_RELOAD = new float[SEC_COUNT], SEC_REGEN = new float[SEC_COUNT];
    static {
        for (int i = 0; i < SEC_COUNT; i++) {
            Wpn.Def d = Wpn.T[i];
            SEC_NAME[i] = d.name; SEC_ICON[i] = d.icon; SEC_STYLE[i] = d.style; SEC_FX[i] = d.fx; SEC_DESC[i] = d.desc;
            SEC_AMMO[i] = d.ammo; SEC_COL[i] = d.col; SEC_RAR[i] = d.rar; SEC_SHOTS[i] = d.shots; SEC_RANGE[i] = d.range; SEC_MAG[i] = d.mag; SEC_KIND[i] = d.kind;
            SEC_DMG[i] = d.dmg; SEC_CD[i] = d.cd; SEC_RELOAD[i] = d.reload; SEC_REGEN[i] = d.regen;
        }
    }
    /** Cuerpo a cuerpo: sin municion (no se gasta ni se recarga). */
    static boolean infinite(int id) { return id > 0 && id < SEC_COUNT && (SEC_KIND[id] == Wpn.K_FAST || SEC_KIND[id] == Wpn.K_MID); }

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
        if (infinite(rs.sec)) { Melee.start(lv, p, rs.sec); return; }        // cuerpo a cuerpo: sin municion
        if (rs.secAmmo <= 0) { lv.text(p.x, p.y - p.bh - 8, SEC_REGEN[rs.sec] > 0 ? "sin energía" : "sin munición", 0xA0A0A8, false); Snd.sfx("ui_error", 0.5f); p.secCd = 0.4f; Arsenal.onEmpty(lv, p); return; }
        if (!Arsenal.ready(rs)) { p.secCd = 0.12f; return; }          // recargando: el arma sigue equipada, solo no dispara hasta terminar
        float d = p.dir();
        float x = p.x + d * 12, y = p.y - 17;
        float base = p.baseDmg(lv) * (1f + 0.25f * rs.secLvl);
        if (rs.sec >= SEC_BOW) { Arsenal.fire(lv, p, rs.sec, base); return; }
        rs.secAmmo--; Arsenal.spendMag(rs);
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
            // a la bolsa (nunca sustituye a la equipada); repetida sube de nivel; con la bolsa llena queda en el suelo, junto al cofre
            int res = Arsenal.grant(rs, t, 0, -1, 0);
            if (res == Arsenal.ADD_FULL) { Arsenal.dropWeapon(lv, t, 0, x, y, false, false); lv.text(x, y - 70, "Inventario lleno: quedó en el suelo", 0xB8C8E0, false); }
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
