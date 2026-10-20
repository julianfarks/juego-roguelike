package com.julianfarks.roguelike.core;

/** Definicion de jefes. */
public final class BossDef {
    // extra del ataque 3 (golpe de area)
    public static final int SLAM_NONE = 0, SLAM_ERUPT_LINE = 1, SLAM_ERUPT_PLAYER = 2, SLAM_RAIN = 3, SLAM_PULL = 4, SLAM_ROCKS = 5;
    // tipo de conjuro
    public static final int CAST_FAN = 0, CAST_AIM = 1, CAST_SUMMON = 2, CAST_RAIN = 3, CAST_LINES = 4;
    // entrada cinematica
    public static final int INTRO_RISE = 0, INTRO_FALL = 1, INTRO_PORTAL = 2, INTRO_WALK = 3, INTRO_BURST = 4;

    public final int idx;            // 0..7 jefes, 8 = cazador
    public final int form;           // 0 (o 0..2 en el cazador)
    public final String key, sheet, name, title, music, element, castProj, sfx, tag;
    public final float hp, lunge;
    public final boolean hover;
    public final int color, slamExtra, castKind, castCount, intro;
    public final String[] minions;
    public final float dmg;          // daño base melee
    public final float speed;

    BossDef(int idx, int form, String key, String sheet, String name, String title, float hp, boolean hover, String music, int color,
            float dmg, float speed, float lunge, int slamExtra, int castKind, String castProj, int castCount, String element, int intro, String[] minions) {
        this.idx = idx; this.form = form; this.key = key; this.sheet = "sprites/bs_" + sheet; this.name = name; this.title = title; this.hp = hp;
        this.hover = hover; this.music = music; this.color = color; this.dmg = dmg; this.speed = speed; this.lunge = lunge; this.slamExtra = slamExtra;
        this.castKind = castKind; this.castProj = castProj; this.castCount = castCount; this.element = element; this.intro = intro; this.minions = minions;
        this.sfx = "bs_" + (idx == 8 ? "cazador" : key) + "_";
        this.tag = sheet;
    }

    static String[] m(String... s) { return s; }

    public static final BossDef[] ALL = {
            new BossDef(0, 0, "rey_exanime", "rey_exanime", "Rey Exánime", "Soberano de las Catacumbas", 950, false, "mus_boss_a", 0x5CFF9A, 22, 62, 150,
                    SLAM_ERUPT_LINE, CAST_SUMMON, "bone", 3, "shadow", INTRO_RISE, m("esqueleto", "arquero_hueso")),
            new BossDef(1, 0, "coloso_magma", "coloso_magma", "Coloso de Magma", "El corazón de la Forja", 1250, false, "mus_boss_a", 0xFF7A1A, 28, 48, 110,
                    SLAM_ERUPT_LINE, CAST_FAN, "magma", 5, "fire", INTRO_RISE, null),
            new BossDef(2, 0, "reina_escarcha", "reina_escarcha", "Reina de la Escarcha", "Señora del Santuario Helado", 1050, false,   // terrestre: se desliza sobre el hielo (ver Boss.iceGlide)
            "mus_boss_a", 0x7AF0FF, 20, 70, 190,
                    SLAM_ERUPT_LINE, CAST_FAN, "iceshard", 7, "ice", INTRO_FALL, null),
            new BossDef(3, 0, "devorador_vacio", "devorador_vacio", "Devorador del Vacío", "El ojo que todo lo consume", 1150, true, "mus_boss_a", 0xB04CFF, 22, 55, 170,
                    SLAM_PULL, CAST_RAIN, "voidorb", 6, "void", INTRO_PORTAL, null),
            new BossDef(4, 0, "ent_ancestral", "ent_ancestral", "Ent Ancestral", "Guardián del bosque podrido", 1450, false, "mus_boss_b", 0xFFC24A, 26, 42, 120,
                    SLAM_ERUPT_PLAYER, CAST_SUMMON, "poison", 4, "thorn", INTRO_RISE, m("arana")),
            new BossDef(5, 0, "titan_tormenta", "titan_tormenta", "Titán de la Tormenta", "Señor de la Fortaleza del Trueno", 1550, false, "mus_boss_b", 0x4FA8FF, 28, 58, 160,
                    SLAM_RAIN, CAST_LINES, "bolt", 3, "lightning", INTRO_FALL, null),
            new BossDef(6, 0, "matriarca_sangre", "matriarca_sangre", "Matriarca de Sangre", "Soberana de la Catedral Carmesí", 1350, true, "mus_boss_b", 0xD0203A, 24, 80, 200,
                    SLAM_ERUPT_PLAYER, CAST_SUMMON, "bloodorb", 5, "blood", INTRO_BURST, m("murcielago")),
            new BossDef(7, 0, "guardian_eclipse", "guardian_eclipse", "Guardián del Eclipse", "Custodio del sol y la luna", 1650, false, "mus_boss_b", 0xF2E6B8, 28, 60, 170,
                    SLAM_RAIN, CAST_FAN, "holy", 5, "holy", INTRO_WALK, null),
            new BossDef(8, 0, "cazador1", "cazador1", "I · El Cazador Pálido", "Dios Antiguo de la Luna de Sangre", 1500, false, "mus_final_1", 0xC8142E, 24, 70, 180,
                    SLAM_ERUPT_LINE, CAST_AIM, "bolt", 3, "blood", INTRO_BURST, null),
            new BossDef(8, 1, "cazador2", "cazador2", "II · La Bestia", "Dios Antiguo de la Luna de Sangre", 1900, false, "mus_final_2", 0xC8142E, 28, 85, 210,
                    SLAM_ERUPT_PLAYER, CAST_RAIN, "bloodorb", 7, "blood", INTRO_RISE, m("murcielago", "vindicador")),
            new BossDef(8, 2, "cazador3", "cazador3", "III · Dios Antiguo", "Dios Antiguo de la Luna de Sangre", 2600, true, "mus_final_3", 0xC8142E, 32, 70, 190,
                    SLAM_PULL, CAST_RAIN, "voidorb", 9, "void", INTRO_PORTAL, null),
    };

    public static BossDef byBiome(int biome) { return ALL[Math.min(biome, 8)]; }
}
