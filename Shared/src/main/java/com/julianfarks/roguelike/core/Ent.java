package com.julianfarks.roguelike.core;

/** Entidad con cuerpo fisico (jugador, enemigo, jefe). x,y = pivote (centro de los pies). */
public abstract class Ent {
    public static final int BURN = 0, FREEZE = 1, SLOW = 2, POISON = 3, SHOCK = 4, BLEED = 5, ROOT = 6, STUN = 7, CURSE = 8, ST_COUNT = 9;
    public static final int[] ST_COLOR = {0xFF7A1A, 0x9AE0FF, 0x7AB8FF, 0x6AE08A, 0xF0F060, 0xD0203A, 0x6AA040, 0xFFFFFF, 0xB070FF};

    public float x, y, vx, vy;
    public float bw = 12, bh = 28;
    public boolean right = true, onGround, alive = true, flying, gravity = true, hitWall, onOneWay;
    public float hp = 1, maxHp = 1;
    public float hitFlash;
    public float stun;                  // aturdimiento (no actua)
    public float[] st = new float[ST_COUNT];
    public float[] stPow = new float[ST_COUNT];   // daño por segundo del estado
    public float dotAcc, dotTick;
    public float focusT; public int focusN;   // Enfoque (bendiciones): golpes consecutivos al mismo objetivo
    public Sheet sheet = Sheet.EMPTY;
    public String animName = "idle";
    public float animT;
    public float scale = 1f;
    public float dropT;                 // ignorar plataformas atravesables
    public float airT;                  // tiempo en el aire
    public float tint = 0;              // reservado

    public float left() { return x - bw / 2f; }
    public float top() { return y - bh; }
    public float cx() { return x; }
    public float cy() { return y - bh / 2f; }

    public boolean overlaps(float rx, float ry, float rw, float rh) {
        return Mth.overlap(x - bw / 2f, y - bh, bw, bh, rx, ry, rw, rh);
    }

    public boolean hasStatus(int s) { return st[s] > 0; }

    public void applyStatus(int s, float dur, float pow) {
        if (s == FREEZE && st[FREEZE] > 0) return;
        st[s] = Math.max(st[s], dur);
        if (pow > stPow[s]) stPow[s] = pow;
    }

    public float speedMul() {
        float m = 1f;
        if (st[SLOW] > 0) m *= 0.55f;
        if (st[FREEZE] > 0 || st[ROOT] > 0 || st[STUN] > 0) m = 0f;
        if (st[SHOCK] > 0) m *= 0.7f;
        return m;
    }

    public boolean frozen() { return st[FREEZE] > 0 || st[STUN] > 0; }

    public void setAnim(String n) {
        if (!n.equals(animName)) { animName = n; animT = 0; }
    }

    public Anim anim() { return sheet.anim(animName); }
}
