package com.julianfarks.roguelike.core;

/** Proyectil. */
final class Proj {
    float x, y, vx, vy, grav;
    float dmg, life = 3f, radius = 5f;
    boolean friendly;
    String sprite = "fireball";
    int pierce = 0;                     // golpes extra que atraviesa
    int status = -1; float statusDur, statusPow;
    float explode;                      // radio de explosion al impactar (0 = no)
    float homing;                       // fuerza de persecucion
    int color = 0xFFFFFF;
    boolean add = true;
    float t;
    boolean dead;
    float scale = 1f;
    boolean spin;
    float spinRate = 12f;
    int special;                        // 1 = onda de choque del suelo (se mueve pegada al suelo), 2 = bola con rebote
    float knock = 120f;
    boolean passWalls;
    String explodeFx = "fx_explosion:a";
    String hitSfx = "proj_hit";
    java.util.HashSet<Object> hit;      // enemigos ya golpeados (perforantes)
    boolean trail = true;
    // ---- bendiciones (ver BlessFx)
    int src;                            // origen del dano: BlessFx.SRC_P (arma), SRC_S (habilidad) o SRC_X (efecto de bendicion)
    int bounces;                        // rebotes que le quedan
    float pierceGrow;                   // dano extra por enemigo atravesado
    boolean copyMade;                   // ya se duplico (evita bucles)

    Proj copy() {
        Proj c = new Proj();
        c.x = x; c.y = y; c.vx = vx; c.vy = vy; c.grav = grav; c.dmg = dmg; c.life = life; c.radius = radius; c.friendly = friendly; c.sprite = sprite;
        c.pierce = pierce; c.status = status; c.statusDur = statusDur; c.statusPow = statusPow; c.explode = explode; c.homing = homing; c.color = color; c.add = add;
        c.scale = scale; c.spin = spin; c.spinRate = spinRate; c.special = special; c.knock = knock; c.passWalls = passWalls; c.explodeFx = explodeFx; c.hitSfx = hitSfx;
        c.trail = trail; c.src = src; c.bounces = bounces; c.pierceGrow = pierceGrow; c.copyMade = true;
        return c;
    }
}

/** Efecto visual animado de una hoja de fx. */
final class FxObj {
    Sheet sheet; Anim anim;
    float x, y, t, rot, scale = 1f, alpha = 1f, delay;
    int flags, tint;
    boolean right = true;
    boolean loop;
    float life = -1;                    // duracion para efectos en bucle
    Ent follow; float fox, foy;
    boolean dead;
    boolean behind;                     // dibujar detras de las entidades
}

/** Objeto recogible. */
final class Pickup {
    static final int GOLD = 0, SOUL = 1, HEART = 2, POTION = 3, RELIC = 4;
    int type; float x, y, vx, vy, t; int value; boolean dead; boolean onGround;
    float delay;
    int relic = -1;
    Pickup(int type, float x, float y, int value) { this.type = type; this.x = x; this.y = y; this.value = value; }
}

/** Objeto del mundo con el que se puede interactuar. */
final class Prop {
    String kind; float x, y; int arg; boolean used, open, dead; float t;
    Sheet sheet; String anim = "idle"; float animT;
    // puertas de salida
    int doorIdx = -1; int nextType = -1; int nextBiome = -1; boolean locked;
    boolean hidden;       // recompensa de camara secreta aun sin descubrir
    boolean roundChest;   // cofre de recompensa de ronda (no secreto)
    int event;            // puerta lateral hacia un suceso (Events.*), 0 = puerta normal
    String icon;          // icono propio sobre la puerta (sustituye al del tipo de sala)
    int tint;             // tinte RGB de la puerta (0 = ninguno)
    Sheet back;           // hoja dibujada detras (puesto del mercader errante)
    boolean done;         // suceso ya resuelto (jaula abierta, espiritu satisfecho...)
    String label;
    float hp = 1;       // vasijas
    float shakeT;
    Prop(String kind, float x, float y) { this.kind = kind; this.x = x; this.y = y; }
}

/** Texto de daño flotante. */
final class DmgText {
    float x, y, vy, life, maxLife; String text; int color; boolean big;
}
