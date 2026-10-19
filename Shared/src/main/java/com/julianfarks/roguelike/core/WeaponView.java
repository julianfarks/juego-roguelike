package com.julianfarks.roguelike.core;

/**
 * Representacion visual del arma secundaria en el personaje.
 *  - Con la secundaria elegida, la espada de la clase se guarda a la espalda (filas "_s" de la hoja) y el cuerpo usa las filas sin arma ("_u").
 *  - La secundaria se dibuja en la mano (anclaje "hand" de cada fotograma), con su propia postura segun el tipo de arma, siguiendo el movimiento de la mano
 *    en reposo, carrera, salto y caida, y animando disparo, lanzamiento, recarga y golpe cuerpo a cuerpo (con estelas).
 *  - Se decide por el arma realmente equipada y seleccionada (RunState), no por el icono de la interfaz. Al elegir la principal, la espada vuelve a la mano.
 *  - Estados con fotogramas propios de la clase (habilidades, ultimate, rodar, dano, bloqueo, animaciones de espera) conservan sus fotogramas originales:
 *    en esos instantes no se dibuja la secundaria (nunca hay dos armas a la vez).
 */
final class WeaponView {
    private WeaponView() {}

    private static Platform.Img img;
    private static boolean tried;
    private static final int CW = 48, CH = 16, COLS = 4, GX = 10, GY = 8;

    private static Platform.Img img() {
        if (!tried) { tried = true; img = Assets.img("sprites/wpn_hold.png"); }
        return img;
    }

    /** Postura de reposo por arma: angulo (grados, negativo = punta hacia arriba), desplazamiento hacia delante y elevacion. */
    private static final float[] BASE = new float[Wpn.N], FWD = new float[Wpn.N], LIFT = new float[Wpn.N];
    /** Gesto al usarla: 0 = disparo (retroceso), 1 = lanzamiento (el brazo sube y suelta), 2 = flotante (pulso), 3 = cuerpo a cuerpo (ver Melee). */
    private static final int[] GESTURE = new int[Wpn.N];

    static {
        float[][] b = {
                {1, -30, 0, 0}, {2, 0, 3, 0}, {3, -40, 0, 0}, {4, 0, 0, -3}, {5, 0, 2, 0}, {6, -20, 0, 0}, {7, -40, 0, 0}, {8, -55, 0, 0}, {9, 0, 2, 0}, {10, -50, 0, 0},
                {11, -25, 0, 0}, {12, -20, 0, 0}, {13, -30, 0, 0}, {14, -10, 0, 0}, {15, 10, 0, 0}, {16, 0, 0, 0},
                {17, -55, 0, 0}, {18, -60, 0, 0}, {19, -50, 0, 0}, {20, 20, 0, 0}, {21, 25, 0, 0}, {22, -35, 0, 0}, {23, -65, 0, 0},
                {24, -25, 0, 0}, {25, -10, 0, 0}, {26, -15, 0, -2}, {27, -15, 0, -2},
                {28, -40, 0, 0}, {29, -40, 0, 0}, {30, -40, 0, 0}, {31, -40, 0, 0}, {32, 0, 0, -3}, {33, -10, 0, 0}, {34, -45, 0, 0}, {35, 0, 0, -3}, {36, -5, 0, 0}};
        for (float[] r : b) { int i = (int) r[0]; BASE[i] = r[1]; FWD[i] = r[2]; LIFT[i] = r[3]; }
        for (int i = 1; i < Wpn.N; i++) GESTURE[i] = Wpn.T[i].melee() ? 3 : 0;
        for (int i : new int[]{1, 3, 6, 8, 24, 25, 26, 27, 36}) GESTURE[i] = 1;
        for (int i : new int[]{4, 32, 35}) GESTURE[i] = 2;
    }

    /** true si se dibuja la secundaria en la mano (y la espada guardada a la espalda): arma elegida, personaje en reposo/carrera/salto/caida con hoja de clase. */
    static boolean active(Level lv, Player p, Sheet cs) {
        RunState rs = lv.rs;
        if (!p.alive || !rs.secActive || rs.sec <= 0 || rs.sec >= Wpn.N || p.secView < 0.5f) return false;
        if (cs != p.sheet) return false;                                   // animaciones de espera / reacciones: hoja propia con el arma original
        if (p.state != Player.IDLE && p.state != Player.RUN && p.state != Player.AIR) return false;
        String n = p.animName;
        return (n.equals("idle") || n.equals("run") || n.equals("jump") || n.equals("fall")) && cs.has(n + "_u");
    }

    private static float ease(float t) { t = Mth.clamp(t, 0f, 1f); return t * t * (3f - 2f * t); }
    private static float lerp(float a, float b, float t) { return a + (b - a) * t; }

    /** Pose del golpe cuerpo a cuerpo segun fase (anticipacion, impacto, recuperacion) y tipo. Devuelve {angulo, adelante, elevacion, estela, angulo previo} (angulos relativos a la postura base). */
    static float[] pose(int id, Wpn.Def d, WeaponFx.State s) {
        float t = s.swT, wind = Math.max(d.wind, 0.02f), actEnd = d.swingDur() - d.rec;
        float a0, a1, f0, f1, l0 = 0, l1 = 0;
        switch (d.swing) {
            case Wpn.S_STAB:  a0 = -BASE[id] - 4; a1 = -BASE[id]; f0 = -5; f1 = 9; break;
            case Wpn.S_SWEEP: a0 = -50; a1 = 95; f0 = -2; f1 = 4; l0 = -4; l1 = 2; break;
            case Wpn.S_SMASH: a0 = -75; a1 = 85; f0 = -3; f1 = 5; l0 = -6; l1 = 2; break;
            case Wpn.S_WHIP:  a0 = -40; a1 = 50; f0 = -4; f1 = 8; break;
            case Wpn.S_CHAIN: a0 = -60; a1 = 60; f0 = -3; f1 = 7; break;
            case Wpn.S_PUNCH: a0 = -BASE[id]; a1 = -BASE[id]; f0 = -5; f1 = 10; break;
            case Wpn.S_CLAW:  a0 = -35; a1 = 45; f0 = -2; f1 = 6; break;
            default:          a0 = -55; a1 = 65; f0 = -3; f1 = 5; break;
        }
        float ang, fwd, lift, smear = 0f, prev;
        if (t < wind) {                                    // anticipacion
            float k = ease(t / wind);
            ang = lerp(0, a0, k); fwd = lerp(0, f0, k); lift = lerp(0, l0, k); prev = ang;
        } else if (t < actEnd) {                           // impacto (en armas de varios golpes alterna sentido)
            float k = ease((t - wind) / Math.max(0.03f, actEnd - wind));
            float sign = (d.hits > 1 && (((int) ((t - wind) / Math.max(0.03f, d.gap + d.act))) & 1) == 1) ? -1f : 1f;
            ang = lerp(a0, a1, k) * (sign < 0 && d.swing != Wpn.S_STAB && d.swing != Wpn.S_PUNCH ? -0.6f : 1f);
            fwd = lerp(f0, f1, k); lift = lerp(l0, l1, k);
            smear = k < 0.9f ? 1f : 0.4f; prev = lerp(a0, a1, Math.max(0f, k - 0.35f));
        } else {                                           // recuperacion
            float k = ease((t - actEnd) / Math.max(0.03f, d.rec));
            ang = lerp(a1, 0, k); fwd = lerp(f1, 0, k); lift = lerp(l1, 0, k); prev = ang;
        }
        return new float[]{ang, fwd, lift, smear, prev};
    }

    /** Dibuja el arma secundaria en la mano. (x,y) = pies; ssx/ssy = deformacion del cuerpo; flags/tint/alpha = los del cuerpo. */
    static void drawHeld(Platform.Gfx g, Level lv, Player p, Sheet cs, Anim au, int frame, float x, float y, float ssx, float ssy, int flags, int tint, float alpha) {
        Platform.Img im = img();
        int id = lv.rs.sec;
        if (im == null || id <= 0 || id >= Wpn.N) return;
        Wpn.Def d = Wpn.T[id];
        int hx = 40, hy = 28;
        if (au.hand != null && au.hand.length > 0) { int[] h = au.hand[Math.min(frame, au.hand.length - 1)]; hx = h[0]; hy = h[1]; }
        float dir = p.right ? 1f : -1f;
        float px = x + dir * (hx - cs.px) * ssx, py = y + (hy - cs.py) * ssy;
        float ang = BASE[id], fwd = FWD[id], lift = LIFT[id];
        // movimiento del cuerpo: respiracion en reposo, balanceo al correr, brazo arriba al saltar / abajo al caer
        String an = p.animName;
        float t = p.animT;
        if (an.equals("idle")) ang += (float) Math.sin(t * 2.2f) * 2.5f;
        else if (an.equals("run")) { ang += (float) Math.sin(t * 13f) * 5f; fwd += (float) Math.cos(t * 13f) * 0.8f; }
        else if (an.equals("jump")) ang -= 14f;
        else ang += 12f;
        float[] smearA = null;
        // ---- gesto de uso
        WeaponFx.State s = p.wfx;
        if (s.sw && s.swId == id) {
            float[] pose = pose(id, d, s);        // {angulo, adelante, elevacion, intensidad de estela (0..1), angulo previo}
            ang = BASE[id] + pose[0]; fwd += pose[1]; lift += pose[2];
            if (pose[3] > 0.05f) smearA = new float[]{pose[3], BASE[id] + pose[4]};
        } else if (p.wpnT > 0f && p.wpnId == id) {
            float k = p.wpnT / 0.22f;
            switch (GESTURE[id]) {
                case 1: ang -= 70f * k; fwd += 3f * (1f - k); break;       // lanzamiento: el brazo sube y suelta
                case 2: lift -= 4f * k; break;                              // flotante: pulso
                default: ang -= 12f * k; fwd -= 3f * k; break;              // disparo: retroceso
            }
        }
        // ---- recarga (armas de cargador): el arma se inclina y vuelve, con un temblor al cargar
        if (Arsenal.reloading(lv.rs) && lv.rs.sec == id) {
            float u = 1f - Mth.clamp(lv.rs.secReload / Math.max(0.01f, p.reloadMax), 0f, 1f);
            ang += 55f * (float) Math.sin(u * Math.PI);
            fwd -= 2f;
            if (u > 0.4f && u < 0.7f) lift += ((int) (u * 40) & 1) == 0 ? -1f : 1f;
        } else if (p.reloadDoneT > 0f && lv.rs.sec == id) {
            lift -= 3f * (p.reloadDoneT / 0.25f);                           // vuelve a su sitio con un respingo
        }
        px += dir * fwd * ssx; py += lift * ssy;
        // ---- estela (copias anteriores del arma durante el golpe, sin desenfoque)
        if (smearA != null && !Save.S.reduceFx) {
            draw(g, im, id, px, py, smearA[1], dir, flags | Platform.ADD | Platform.TINT, d.col, 0.28f * smearA[0]);
            draw(g, im, id, px, py, (smearA[1] + (ang - smearA[1]) * 0.5f), dir, flags | Platform.ADD | Platform.TINT, d.col, 0.20f * smearA[0]);
        }
        draw(g, im, id, px, py, ang, dir, flags, tint, alpha);
    }

    private static void draw(Platform.Gfx g, Platform.Img im, int id, float hx, float hy, float angDeg, float dir, int flags, int tint, float alpha) {
        double a = Math.toRadians(angDeg);
        // centro del sprite respecto a la empuñadura: (CW/2 - GX, CH/2 - GY) = (14, 0), girado por el angulo (y reflejado si mira a la izquierda)
        float ox = (float) (14 * Math.cos(a)), oy = (float) (14 * Math.sin(a));
        float cx = hx + dir * ox, cy = hy + oy;
        float rot = (float) (dir > 0 ? a : -a);
        int fl = dir > 0 ? flags : (flags | Platform.FLIP_X);
        g.imageRot(im, (id % COLS) * CW, (id / COLS) * CH, CW, CH, cx - CW / 2f, cy - CH / 2f, CW, CH, rot, fl, tint, alpha);
    }
}
