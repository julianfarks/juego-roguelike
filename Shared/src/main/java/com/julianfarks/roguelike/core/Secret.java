package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/**
 * Camara secreta de una sala: como se entra (entrada), que hay que hacer (reto) y que hay dentro (recompensa).
 * Mientras esta cerrada, todo su recuadro se dibuja como roca maciza (Room.baked) y su contenido no se ve ni se puede usar.
 */
public final class Secret {
    // como se accede
    public static final int E_FLOOR = 0, E_WALL = 1, E_ILLUSION = 2, E_WATERFALL = 3, E_CURTAIN = 4, E_STATUE = 5,
            E_LEVER = 6, E_SYMBOLS = 7, E_RUNES = 8, E_SKILL = 9, E_COUNT = 10;
    public static final String[] E_NAME = {"suelo agrietado", "pared hueca", "pared ilusoria", "cascada", "cortina", "estatua",
            "palanca oculta", "simbolos", "runas", "cristal de habilidad"};
    // que contiene
    public static final int R_CHEST = 0, R_RICH = 1, R_RELIC = 2, R_TREASURE = 3, R_SHRINE = 4, R_STASH = 5, R_COUNT = 6;
    public static final String[] R_NAME = {"cofre", "cofre superior", "reliquia", "sala del tesoro", "santuario de pactos", "provisiones"};
    // reto extra dentro de la camara
    public static final int C_NONE = 0, C_PLAT = 1, C_GUARD = 2;

    public int family;                 // 0 = bajo el suelo, 1 = camara de piedra sobre el piso superior
    public int entrance, reward, challenge, tier;
    public int rx0, ry0, rx1, ry1;     // recuadro cubierto (baldosas, inclusive)
    public final List<int[]> door = new ArrayList<>();   // baldosas de la entrada {x,y}
    public float rwX, rwY;             // posicion (pies) de la recompensa
    public final List<float[]> sw = new ArrayList<>();   // interruptores {x, y, id}: palanca, piedras de simbolos / runas
    public int[] order;                // orden correcto de los interruptores
    public float cx, cy;               // centro de la entrada (px)
    public float crX, crY;             // cristal de habilidad (px)
    public boolean horizontalDoor;     // la entrada esta en el suelo (hueco) y no en una pared

    // ---- estado en partida (Secrets)
    boolean open, revealing, rewardOut, entered, looted, seqShown, hinted;
    float openT, hint, hitT;
    int progress;                      // simbolos acertados / paso de la secuencia
    float failT, seqT, doneT;
    int[] seq;                         // secuencia mostrada (runas)
    Prop rewardProp;
    Enemy guardian;
    final float[] lit = new float[4];  // brillo de cada piedra

    public boolean contains(int tx, int ty) { return tx >= rx0 && tx <= rx1 && ty >= ry0 && ty <= ry1; }

    /** Pone en 'room.t' el estado visual de la camara: cerrada (todo roca) o abierta (entradas libres). 'real' = baldosas originales. */
    void apply(Room room, byte[] real, boolean opened) {
        for (int y = ry0; y <= ry1; y++) for (int x = rx0; x <= rx1; x++) {
            if (x < 0 || y < 0 || x >= room.w || y >= room.h) continue;
            int i = y * room.w + x, v = real[i];
            if (!opened) room.t[i] = (byte) Room.SOLID;
            else room.t[i] = (byte) ((v == Room.HWALL || v == Room.FAKE || v == Room.BREAK || v == Room.DOOR) ? Room.AIR : v);
        }
    }

    /** Baldosas del recuadro mas un margen (sombreado de bordes), recortado a la sala. */
    int[] drawRect(Room room, int margin) {
        return new int[]{Math.max(0, rx0 - margin), Math.max(0, ry0 - margin), Math.min(room.w - 1, rx1 + margin), Math.min(room.h - 1, ry1 + margin)};
    }
}
