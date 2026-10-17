package com.julianfarks.roguelike.core;

/** Datos de cada bioma/mazmorra. El indice coincide con el del jefe. */
public final class Biome {
    public final int id, tier;
    public final String key, name, music, ambient, boss, tagline;
    public final int color;
    public final String[] enemies;
    public final float dark;

    Biome(int id, String key, String name, int color, int tier, String music, String boss, String tagline, float dark, String... enemies) {
        this.id = id; this.key = key; this.name = name; this.color = color; this.tier = tier; this.music = music;
        this.ambient = "amb_" + key; this.boss = boss; this.tagline = tagline; this.dark = dark; this.enemies = enemies;
    }

    public static final Biome[] ALL = {
            new Biome(0, "catacumbas", "Catacumbas", 0x5CFF9A, 0, "mus_catacumbas", "rey_exanime", "Donde los reyes olvidados no descansan", 0.10f, "esqueleto", "arquero_hueso", "zombi", "escudero_hueso", "clerigo_osario"),
            new Biome(1, "forja", "Forja Infernal", 0xFF7A1A, 1, "mus_forja", "coloso_magma", "El corazón ardiente del abismo", 0.08f, "cubo_magma", "llama", "bruto_forja", "carbonero_forja"),
            new Biome(2, "helado", "Santuario Helado", 0x7AF0FF, 0, "mus_helado", "reina_escarcha", "Silencio, escarcha y cristal", 0.08f, "lancero_escarcha", "hechicero_hielo", "espiritu_vex", "centinela_cristal"),
            new Biome(3, "vacio", "Abismo del Vacío", 0xB04CFF, 2, "mus_vacio", "devorador_vacio", "Un ojo que todo lo consume", 0.14f, "acechador", "ojo_vacio", "fantasma"),
            new Biome(4, "bosque", "Bosque Podrido", 0xFFC24A, 0, "mus_bosque", "ent_ancestral", "El bosque recuerda cada hachazo", 0.10f, "arana", "bruja", "tronco_vivo", "lobo_musgo"),
            new Biome(5, "tormenta", "Fortaleza del Trueno", 0x4FA8FF, 1, "mus_tormenta", "titan_tormenta", "Donde el cielo golpea la tierra", 0.10f, "saqueador", "vex_tormenta", "bestia_tormenta", "tirador_rayo"),
            new Biome(6, "sangre", "Catedral Carmesí", 0xD0203A, 2, "mus_sangre", "matriarca_sangre", "Un coro de sangre sin fin", 0.14f, "vindicador", "bruja_sangre", "murcielago", "cultista_sangre"),
            new Biome(7, "eclipse", "Santuario del Eclipse", 0xF2E6B8, 2, "mus_eclipse", "guardian_eclipse", "Custodios del sol y la luna", 0.12f, "piglin_dorado", "espectro", "llama_solar", "asesino_eclipse"),
            new Biome(8, "cazador", "Luna de Sangre", 0xC8142E, 3, "mus_final_1", "cazador1", "Aquí termina la cacería", 0.16f, "vindicador", "bruja_sangre", "murcielago", "cultista_sangre"),
    };
}
