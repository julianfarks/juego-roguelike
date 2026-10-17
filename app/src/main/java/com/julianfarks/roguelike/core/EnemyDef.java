package com.julianfarks.roguelike.core;

import java.util.HashMap;
import java.util.Map;

/** Definicion de enemigos normales. */
public final class EnemyDef {
    public static final int MELEE = 0, RANGED = 1, FLY_SHOOT = 2, FLY_DIVE = 3, CHARGER = 4, JUMPER = 5, CASTER = 6, HEAVY = 7,
            SHIELD = 8, SUPPORT = 9, EXPLODER = 10, TURRET = 11, POUNCER = 12, SNIPER = 13, BUFFER = 14, BLINKER = 15, ELITE = 16;

    public final String id, sheet, dieSfx, proj;
    public final int role;
    public final float hp, dmg, speed, cooldown, range;
    public float detect;
    public final int souls, color;
    public final float contact;      // daño por contacto (0 = no)
    public final String status;      // estado que aplica al jugador: "", "burn","poison","slow","shock","bleed"
    public boolean elite;

    EnemyDef(String id, int role, float hp, float dmg, float speed, float range, float cooldown, String proj, String dieSfx, int souls, int color, float contact, String status) {
        this.id = id; this.sheet = "sprites/en_" + id; this.role = role; this.hp = hp; this.dmg = dmg; this.speed = speed; this.range = range;
        this.cooldown = cooldown; this.proj = proj; this.dieSfx = dieSfx; this.souls = souls; this.color = color; this.contact = contact;
        this.status = status; this.detect = 190; this.elite = false;
    }

    private static final Map<String, EnemyDef> M = new HashMap<>();

    private static void add(EnemyDef d) { M.put(d.id, d); }

    private static void eliteDef(String id, float hp, float dmg, float speed, float range, float cd, String die, int color, String status) {
        EnemyDef d = new EnemyDef(id, ELITE, hp, dmg, speed, range, cd, null, die, 6, color, 0, status);
        d.elite = true; d.detect = 300;
        M.put(id, d);
    }

    /** Elite unico de cada bioma (null si no tiene). */
    public static String eliteFor(String biomeKey) {
        switch (biomeKey) {
            case "catacumbas": return "caballero_osario";
            case "forja": return "herrero_infernal";
            case "helado": return "ventisca";
            case "vacio": return "segador_vacio";
            case "bosque": return "druida_podrido";
            case "tormenta": return "capitan_trueno";
            case "sangre": case "cazador": return "sacerdote_carmesi";
            case "eclipse": return "centurion_eclipse";
            default: return null;
        }
    }

    public static EnemyDef get(String id) { return M.get(id); }
    public static java.util.Collection<EnemyDef> all() { return M.values(); }

    static {
        // id, role, hp, dmg, speed, range, cooldown, proj, dieSfx, souls, color, contact, status
        add(new EnemyDef("esqueleto", MELEE, 40, 10, 58, 30, 1.2f, null, "en_die_bone", 2, 0xC8D0C0, 0, ""));
        add(new EnemyDef("arquero_hueso", RANGED, 30, 9, 40, 150, 2.0f, "arrow", "en_die_bone", 2, 0xC8D0C0, 0, ""));
        add(new EnemyDef("zombi", HEAVY, 110, 17, 30, 34, 1.8f, null, "en_die_flesh", 3, 0x7A9A6A, 0, ""));
        add(new EnemyDef("cubo_magma", JUMPER, 46, 10, 80, 22, 1.4f, null, "en_die_slime", 2, 0xFF7A1A, 9, "burn"));
        add(new EnemyDef("llama", FLY_SHOOT, 28, 9, 50, 170, 2.2f, "fireball", "en_die_magic", 2, 0xFF7A1A, 0, "burn"));
        add(new EnemyDef("bruto_forja", CHARGER, 120, 20, 40, 130, 2.6f, null, "en_die_flesh", 3, 0xC0603A, 14, ""));
        add(new EnemyDef("lancero_escarcha", MELEE, 48, 11, 55, 44, 1.4f, null, "en_die_bone", 2, 0x9AE0FF, 0, "slow"));
        add(new EnemyDef("hechicero_hielo", CASTER, 32, 8, 38, 160, 2.4f, "iceshard", "en_die_magic", 3, 0x9AE0FF, 0, "slow"));
        add(new EnemyDef("espiritu_vex", FLY_DIVE, 22, 9, 90, 120, 2.2f, null, "en_die_ghost", 2, 0x9AE0FF, 9, ""));
        add(new EnemyDef("acechador", MELEE, 38, 10, 85, 30, 1.0f, null, "en_die_flesh", 2, 0xB04CFF, 0, ""));
        add(new EnemyDef("ojo_vacio", FLY_SHOOT, 35, 9, 45, 170, 2.3f, "voidorb", "en_die_magic", 3, 0xB04CFF, 0, ""));
        add(new EnemyDef("fantasma", FLY_DIVE, 30, 12, 85, 130, 2.4f, null, "en_die_ghost", 2, 0xB04CFF, 10, ""));
        add(new EnemyDef("arana", JUMPER, 32, 9, 90, 24, 1.1f, null, "en_die_flesh", 2, 0x6AA040, 8, "poison"));
        add(new EnemyDef("bruja", RANGED, 34, 8, 36, 150, 2.4f, "poison", "en_die_flesh", 3, 0x6AA040, 0, "poison"));
        add(new EnemyDef("tronco_vivo", HEAVY, 130, 20, 30, 38, 1.9f, null, "en_die_flesh", 3, 0x9A7040, 0, ""));
        add(new EnemyDef("saqueador", RANGED, 38, 11, 42, 170, 2.0f, "arrow", "en_die_flesh", 3, 0x7A6A5A, 0, ""));
        add(new EnemyDef("vex_tormenta", FLY_DIVE, 24, 10, 95, 120, 2.0f, null, "en_die_ghost", 2, 0x4FA8FF, 9, "shock"));
        add(new EnemyDef("bestia_tormenta", CHARGER, 130, 22, 42, 140, 2.6f, null, "en_die_flesh", 3, 0x4FA8FF, 15, ""));
        add(new EnemyDef("vindicador", MELEE, 54, 14, 62, 34, 1.3f, null, "en_die_flesh", 3, 0xD0203A, 0, "bleed"));
        add(new EnemyDef("bruja_sangre", CASTER, 36, 10, 38, 160, 2.3f, "bloodorb", "en_die_magic", 3, 0xD0203A, 0, "bleed"));
        add(new EnemyDef("murcielago", FLY_DIVE, 22, 8, 100, 120, 1.8f, null, "en_die_flesh", 2, 0xD0203A, 8, "bleed"));
        // ---- arquetipos nuevos
        add(new EnemyDef("escudero_hueso", SHIELD, 78, 13, 40, 34, 1.7f, null, "en_die_bone", 3, 0xC8D0C0, 0, ""));
        add(new EnemyDef("clerigo_osario", SUPPORT, 36, 8, 38, 150, 3.4f, "holy", "en_die_bone", 3, 0x5CFF9A, 0, ""));
        add(new EnemyDef("carbonero_forja", EXPLODER, 30, 20, 72, 40, 2.2f, null, "en_die_flesh", 2, 0xFF7A1A, 0, "burn"));
        add(new EnemyDef("centinela_cristal", TURRET, 72, 10, 0, 215, 2.8f, "iceshard", "en_die_magic", 3, 0x7AF0FF, 0, "slow"));
        add(new EnemyDef("lobo_musgo", POUNCER, 38, 12, 78, 40, 1.9f, null, "en_die_flesh", 2, 0x8AA04E, 0, "bleed"));
        add(new EnemyDef("tirador_rayo", SNIPER, 30, 14, 38, 270, 3.2f, "bolt", "en_die_flesh", 3, 0x4FA8FF, 0, "shock"));
        add(new EnemyDef("cultista_sangre", BUFFER, 36, 9, 40, 150, 5.5f, "bloodorb", "en_die_flesh", 3, 0xD0203A, 0, "bleed"));
        add(new EnemyDef("asesino_eclipse", BLINKER, 46, 17, 82, 36, 3.4f, null, "en_die_flesh", 3, 0xF2E6B8, 0, "bleed"));
        M.get("tirador_rayo").detect = 290;
        M.get("clerigo_osario").detect = 290;
        // ---- elites unicos (aparecen en las salas de elite; id, rol, hp, dmg, vel, alcance de ataque, enfriamiento...)
        eliteDef("caballero_osario", 260, 17, 52, 170, 2.4f, "en_die_bone", 0x5CFF9A, "bleed");
        eliteDef("herrero_infernal", 340, 20, 40, 230, 2.8f, "en_die_flesh", 0xFF7A1A, "burn");
        eliteDef("ventisca", 190, 15, 60, 280, 2.6f, "en_die_ghost", 0x7AF0FF, "slow");
        eliteDef("segador_vacio", 230, 19, 56, 230, 2.6f, "en_die_ghost", 0xB04CFF, "");
        eliteDef("druida_podrido", 260, 16, 38, 250, 2.7f, "en_die_flesh", 0x6AA040, "poison");
        eliteDef("capitan_trueno", 280, 18, 50, 270, 2.5f, "en_die_flesh", 0x4FA8FF, "shock");
        eliteDef("sacerdote_carmesi", 240, 17, 38, 260, 2.6f, "en_die_flesh", 0xD0203A, "bleed");
        eliteDef("centurion_eclipse", 320, 21, 46, 270, 2.8f, "en_die_flesh", 0xFFD25A, "");
        add(new EnemyDef("piglin_dorado", HEAVY, 145, 24, 34, 40, 1.8f, null, "en_die_flesh", 4, 0xF2E6B8, 0, ""));
        add(new EnemyDef("espectro", CASTER, 40, 12, 40, 170, 2.3f, "holy", "en_die_ghost", 3, 0xF2E6B8, 0, ""));
        add(new EnemyDef("llama_solar", FLY_SHOOT, 34, 11, 50, 180, 2.1f, "holy", "en_die_magic", 3, 0xF2E6B8, 0, "burn"));
    }
}
