package com.julianfarks.roguelike.core;

/** Jefe: maquina de estados con ataques cuerpo a cuerpo, conjuros, fase 2 y entrada cinematica. */
public final class Boss extends Ent {
    static final int INTRO = 0, IDLE = 1, WINDUP = 2, ATTACK = 3, CAST = 4, RECOVER = 5, PHASE = 6, DEAD = 7, HURT = 8;

    public final BossDef def;
    public int state = INTRO;
    public int phase = 1;
    public float introT;
    public boolean introDone, finished;
    private final float dmgBase;
    private int atk = 1;
    private float stateT, cdT = 0.8f, hurtAcc, hurtSfxT, deadT, pullT, contactCd, stepT, castCount, bob;
    private boolean hitDone, extraDone, fired;
    private int lastAtk, castsRow;
    private final float[] box = new float[4];
    private float offX, offY, alphaMul = 1f;
    private float floorY;
    private boolean deathHandled;

    // ---- zona de vuelo (jefes voladores): limites ABSOLUTOS sacados de la geometria de la sala, nunca de la altura del jugador
    float zoneTop, zoneBot;               // y minima (arriba) y maxima (abajo) permitidas para el pivote (pies) del jefe
    private boolean zoneInit;
    private float hoverTgt = Float.NaN;   // objetivo de altura suavizado (cambios limitados en velocidad: sin saltos bruscos al cambiar de plataforma)

    /** Calcula la banda de vuelo: abajo = suelo de la arena - margen; arriba = el mayor de (techo + cuerpo + margen) y (plataforma alcanzable mas alta - 24),
     *  de modo que desde cualquier plataforma el jugador siempre queda a la altura del cuerpo del jefe y este nunca se pega al techo. */
    void computeZone(Level lv) {
        Room rm = lv.room;
        float floor = rm.spawnY, ceilBot = 0, topPlat = floor - 110;
        int tx0 = 2, tx1 = rm.w - 3, topTy = Integer.MAX_VALUE;
        for (int tx = tx0; tx <= tx1; tx++) {
            int ty = 0;
            while (ty < rm.h && !Room.isSolid(rm.tile(tx, ty))) ty++;
            if (ty >= rm.h || ty * Room.TS >= floor - 2 * Room.TS) continue;         // columna sin techo (o es suelo)
            int by = ty; while (by < rm.h && Room.isSolid(rm.tile(tx, by)) && by * Room.TS < floor - 3 * Room.TS) by++;   // fondo del bloque de techo
            if (by * Room.TS > ceilBot && by * Room.TS < floor - 3 * Room.TS) ceilBot = by * Room.TS;
        }
        for (int tx = tx0; tx <= tx1; tx++) {                                         // superficie alcanzable mas alta: solida/atravesable con 2 tiles de aire encima, por encima del suelo
            for (int ty = 2; ty * Room.TS < floor - 2 * Room.TS; ty++) {
                int t = rm.tile(tx, ty);
                if ((Room.isSolid(t) || t == Room.ONEWAY) && !Room.isSolid(rm.tile(tx, ty - 1)) && !Room.isSolid(rm.tile(tx, ty - 2)) && rm.tile(tx, ty - 1) != Room.ONEWAY) {
                    if (ty < topTy && ty * Room.TS > ceilBot + Room.TS) topTy = ty;
                    break;
                }
            }
        }
        if (topTy != Integer.MAX_VALUE) topPlat = topTy * Room.TS;
        zoneBot = floor - 28f;
        zoneTop = Math.max(Math.max(ceilBot + bh + 10f, ceilBot + sheet.py - 30f), topPlat - 24f);   // cuerpo con margen bajo el techo y el sprite (corona/alas) como mucho 30 px dentro de el
        if (zoneTop > zoneBot - 48f) zoneTop = zoneBot - 48f;                           // banda minima de 48 px
        if (System.getenv("BOT_NOZONE") != null) { zoneTop = -1e6f; zoneBot = 1e6f; }     // solo banco: reproduce el comportamiento anterior (sin limites) para comparar
        zoneInit = true;
    }

    public Boss(BossDef d, RunState rs) {
        this.def = d;
        sheet = Assets.sheet(d.sheet);
        bw = sheet.bw;
        bh = sheet.bh;
        maxHp = hp = d.hp * (1f + 0.08f * rs.stage + 0.10f * rs.asc) * rs.diffHp() * (rs.infinite ? Infinite.bossHpMul(rs.floor) : 1f);
        dmgBase = d.dmg * (1f + 0.05f * rs.stage + 0.06f * rs.asc) * rs.diffDmg() * (rs.infinite ? Infinite.bossDmgMul(rs.floor) : 1f);
        flying = d.hover;
        gravity = !d.hover;
        right = false;
        animName = "intro";
    }

    public boolean invuln() { return state == INTRO || state == PHASE || state == DEAD; }

    @Override
    public void applyStatus(int s, float dur, float pow) {
        if (s == FREEZE) { super.applyStatus(SLOW, dur * 0.6f, pow); return; }
        if (s == STUN || s == ROOT) return;
        super.applyStatus(s, dur * 0.6f, pow);
    }

    private float sfxX(Level lv) { return lv.camX + lv.viewW / 2; }
    private void sfx(Level lv, String n, float v) { Snd.sfx(def.sfx + n, v); }

    private boolean ph2() { return phase >= 2; }

    // ------------------------------------------------------------------ dano recibido
    public void onHit(Level lv, float dmg) {
        hurtAcc += dmg;
        hurtSfxT -= 0;
        if (hurtSfxT <= 0 && Math.random() < 0.5) { sfx(lv, "hurt", 0.6f); hurtSfxT = 0.5f; }
        if (state == IDLE && hurtAcc > maxHp * 0.09f && cdT > 0.15f) {
            hurtAcc = 0;
            state = HURT; stateT = 0; animName = "hurt"; animT = 0; vx = 0;
        }
        if (phase == 1 && hp > 0 && hp <= maxHp * 0.5f && state != PHASE && state != INTRO) startPhase(lv);
    }

    private void startPhase(Level lv) {
        state = PHASE; stateT = 0; animName = "phase"; animT = 0; vx = 0; vy = 0;
        sfx(lv, "phase", 1f);
        lv.shake(5f, 0.8f);
        lv.flash(def.color, 0.35f);
        lv.ps.burst(lv.rng, x, y - bh / 2, def.color, 40, 220, 0.9f, 3, 0, true);
        lv.fxAdd("fx_ring", "pulse", x, y - bh / 2, 2.4f, def.color);
        Snd.sfx("boss_title", 0.5f);
        lv.text(x, y - bh - 12, "¡Furioso!", 0xFF6A6A, true);
        // se curan un poco las proyecciones hostiles
        lv.projs.removeIf(pr -> !pr.friendly);
    }

    // ------------------------------------------------------------------ muerte
    public void die(Level lv) {
        if (state == DEAD) return;
        alive = false;
        state = DEAD; stateT = 0; animName = "death"; animT = 0; vx = 0; vy = 0;
        flying = false; gravity = true;
        sfx(lv, "death", 1f);
        Snd.sfx("boss_defeat", 0.9f);
        Snd.stopMusic(500);
        lv.hitstop(0.35f);
        lv.shake(7f, 1.2f);
        lv.flash(0xFFFFFF, 0.4f);
        lv.projs.removeIf(pr -> !pr.friendly);
        for (Enemy e : lv.enemies) if (e.alive) { e.hp = 0; e.die(lv); }
        RunState rs = lv.rs;
        lv.dropGold(x, y - 40, Math.round((60 + 25 * rs.stage) * rs.stats.goldMul));
        lv.dropSouls(x, y - 40, Math.round((14 + 6 * rs.stage + 8 * def.form) * rs.stats.soulMul));
        lv.drop(Pickup.HEART, x - 14, y - 40, 1);
        lv.drop(Pickup.HEART, x + 14, y - 40, 1);
        rs.bossKills++;
    }

    // ------------------------------------------------------------------ actualizacion
    public void update(Level lv, float dt) {
        Player p = lv.pl;
        if (hitFlash > 0) hitFlash -= dt;
        hurtSfxT -= dt;
        if (contactCd > 0) contactCd -= dt;
        bob += dt;
        animT += dt;
        stateT += dt;
        float dps = Status.tick(this, dt);
        if (state != DEAD && state != INTRO) {
            Status.fx(lv, this, dt);
            if (dps > 0) {
                dotAcc += dps * dt;
                if (dotAcc >= 3f) { int d = (int) dotAcc; dotAcc -= d; int pv = lv.dmgSrc; lv.dmgSrc = BlessFx.SRC_DOT; try { lv.damageEnemy(this, d, false, 0, 0); } finally { lv.dmgSrc = pv; } if (state == DEAD) return; }
            }
        }
        if (state != DEAD) lv.bossBarShow = Math.min(1f, lv.bossBarShow + dt * 1.5f);
        if (floorY == 0) floorY = y;

        switch (state) {
            case INTRO: updateIntro(lv, dt); return;
            case DEAD: updateDead(lv, dt); return;
            default: break;
        }
        boolean frozenNow = false;
        if (p == null || !p.alive) {
            // el jugador murio: se queda quieto
            vx = Mth.approach(vx, 0, 600 * dt);
            if (!flying) vy = Math.min(Level.FALL_MAX, vy + Level.GRAV * dt);
            lv.move(this, dt);
            if (state == IDLE) animName = "idle";
            return;
        }
        float dx = p.x - x;
        float ad = Math.abs(dx);
        float sp = def.speed * (ph2() ? 1.3f : 1f) * speedMul();

        switch (state) {
            case IDLE: updateIdle(lv, dt, p, dx, ad, sp); break;
            case WINDUP: updateWindup(lv, dt, p, dx); break;
            case ATTACK: updateAttack(lv, dt, p); break;
            case CAST: updateCast(lv, dt, p); break;
            case RECOVER:
                vx = Mth.approach(vx, 0, 700 * dt);
                animName = "idle";
                if (stateT > (ph2() ? 0.18f : 0.35f)) { state = IDLE; stateT = 0; }
                break;
            case HURT:
                vx = Mth.approach(vx, 0, 700 * dt);
                if (animT * 10 >= 2 && stateT > 0.3f) { state = IDLE; stateT = 0; cdT = Math.min(cdT, 0.3f); }
                break;
            case PHASE:
                vx = 0; vy = 0;
                if (Math.random() < 0.3) lv.ps.spawn(x + lv.rng.f(-20, 20), y - lv.rng.f(10, bh), 0, -60, 0.6f, 3, 0, def.color, true);
                if (sheet.anim("phase").done(animT)) {
                    phase = 2; state = IDLE; stateT = 0; cdT = 0.4f;
                    hurtAcc = 0;
                    lv.explosion(x, y - 40, 90, dmgBase * 0.8f, 0, -1, 0, 0, false);
                    sfx(lv, "roar", 1f);
                }
                break;
            default: break;
        }
        // movimiento fisico
        if (flying) {
            lv.move(this, dt);
        } else {
            vy = Math.min(Level.FALL_MAX, vy + Level.GRAV * dt);
            lv.move(this, dt);
        }
        if (flying && state != INTRO && state != DEAD) {                               // seguro final: nunca fuera de la banda de vuelo (techo, suelo, pantalla)
            if (!zoneInit) computeZone(lv);
            if (y < zoneTop) { y = zoneTop; if (vy < 0) vy = 0; }
            if (y > zoneBot) { y = zoneBot; if (vy > 0) vy = 0; }
        }
        // limites
        float minX = 2 * Room.TS + bw / 2, maxX = lv.room.pixW - 2 * Room.TS - bw / 2;
        if (x < minX) { x = minX; vx = 0; }
        if (x > maxX) { x = maxX; vx = 0; }
        // atraccion
        if (pullT > 0) {
            pullT -= dt;
            p.extVx = Mth.sign(x - p.x) * 150f;
            if (Math.random() < 0.5) lv.ps.spawn(p.x + lv.rng.f(-30, 30), p.y - lv.rng.f(0, 30), Mth.sign(x - p.x) * 60, 0, 0.3f, 2, 0, def.color, true);
        }
        // contacto
        if (contactCd <= 0 && state != PHASE && overlaps(p.x - p.bw / 2, p.y - p.bh, p.bw, p.bh) && p.alive) {
            if (lv.hurtPlayer(dmgBase * 0.4f, x, -1, 0)) contactCd = 1.0f;
        }
        // aura en fase 2
        if (ph2() && Math.random() < dt * 25) lv.ps.spawn(x + lv.rng.f(-bw / 2, bw / 2), y - lv.rng.f(5, bh * 0.9f), lv.rng.f(-10, 10), -lv.rng.f(20, 60), 0.7f, 2, 0, def.color, true);
    }

    private void face(float dx) { if (Math.abs(dx) > 4) right = dx > 0; }

    private void updateIntro(Level lv, float dt) {
        introT += dt;
        Anim a = sheet.anim("intro");
        if (introT < 0.02f) {
            vx = 0;
            switch (def.intro) {
                case BossDef.INTRO_BURST: lv.flash(def.color, 0.4f); lv.shake(5f, 0.6f); lv.ps.burst(lv.rng, x, y - 60, def.color, 50, 260, 1f, 3, 0, true); break;
                case BossDef.INTRO_PORTAL: lv.fxAdd("fx_void", "hole", x, y - 50, 2.4f, def.color); break;
                case BossDef.INTRO_RISE: lv.fx("fx_smoke", "big", x, y - 30, 2f, 0, 0); break;
                default: break;
            }
            sfx(lv, "intro", 1f);
        }
        offX = 0; offY = 0; alphaMul = 1f;
        float t = introT;
        switch (def.intro) {
            case BossDef.INTRO_FALL:
                offY = -260f * (1f - Mth.easeOut(t / 0.7f));
                if (t >= 0.7f && !fired) { fired = true; lv.shake(6f, 0.5f); lv.fx("fx_dust", "land", x, y - 2, 3f, 0, 0); Snd.sfx("explosion_big", 0.7f); lv.ps.burst(lv.rng, x, y - 2, 0xA0A0A0, 24, 160, 0.6f, 3, 100, false); }
                break;
            case BossDef.INTRO_WALK:
                offX = 170f * (1f - Mth.easeInOut(t / 1.1f));
                break;
            case BossDef.INTRO_PORTAL:
                alphaMul = Mth.clamp((t - 0.2f) / 0.7f, 0f, 1f);
                break;
            case BossDef.INTRO_RISE:
                offY = 60f * (1f - Mth.easeOut(t / 0.9f));
                alphaMul = Mth.clamp(t / 0.5f, 0f, 1f);
                break;
            default:
                alphaMul = Mth.clamp(t / 0.3f, 0f, 1f);
                break;
        }
        if (t > 0.9f && stepT == 0) { stepT = 1; sfx(lv, "roar", 1f); lv.shake(3f, 0.5f); }
        if (a.done(animT) && t > 1.4f) {
            introDone = true;
            offX = offY = 0; alphaMul = 1f;
            state = IDLE; stateT = 0; cdT = 0.9f;
            animName = "idle"; animT = 0;
            lv.cinematic = false;
            lv.camTargetX = Float.NaN; lv.camTargetY = Float.NaN; lv.camTargetZoom = 1f;
        }
    }

    private void updateDead(Level lv, float dt) {
        deadT += dt;
        vy = Math.min(Level.FALL_MAX, vy + Level.GRAV * dt);
        vx *= 0.9f;
        lv.move(this, dt);
        if (Math.random() < dt * 14) {
            float ex = x + lv.rng.f(-bw / 2, bw / 2), ey = y - lv.rng.f(10, bh);
            lv.fxAdd("fx_explosion", "a", ex, ey, 0.5f + lv.rng.f() * 0.5f, def.color);
            Snd.sfxv("explosion_small", 0.5f);
            lv.shake(2.5f, 0.1f);
        }
        if (!deathHandled && deadT > 2.4f && sheet.anim("death").done(animT)) {
            deathHandled = true;
            // reliquia
            if (def.idx < 8) {
                Pickup r = new Pickup(Pickup.RELIC, x, y - 50, 1);
                r.relic = def.idx; r.vy = -160;
                lv.pickups.add(r);
            }
            finished = true;
            if (lv.listener != null) lv.listener.onBossDead(lv);
        }
    }

    // ------------------------------------------------------------------ comportamiento
    private void hoverTo(Level lv, Player p, float dt, float gx, float gy, float sp) {
        if (!zoneInit) computeZone(lv);
        gy = Mth.clamp(gy, zoneTop, zoneBot);                                          // limite absoluto: la altura del jugador no puede empujarla mas arriba
        if (Float.isNaN(hoverTgt)) hoverTgt = y;
        hoverTgt = Mth.approach(hoverTgt, gy, 120f * dt);                              // reajuste controlado al cambiar de plataforma
        gy = hoverTgt;
        float ddx = gx - x, ddy = gy - y;
        if (Math.abs(ddy) < 6f) ddy = 0f;                                              // zona muerta: sin oscilaciones constantes
        vx = Mth.approach(vx, Mth.clamp(ddx * 2.2f, -sp, sp), 900 * dt);
        vy = Mth.approach(vy, Mth.clamp(ddy * 3f, -sp, sp), 900 * dt);
    }

    private void updateIdle(Level lv, float dt, Player p, float dx, float ad, float sp) {
        face(dx);
        cdT -= dt;
        boolean wantClose = ad > 60;
        if (flying) {
            float side = dx > 0 ? -1 : 1;
            float gx = ad > 150 ? p.x + side * 90 : p.x + side * 60;
            hoverTo(lv, p, dt, gx, p.y - 60 + (float) Math.sin(bob * 2) * 8, sp * 1.1f);
            animName = "idle";
        } else if (wantClose) {
            vx = Mth.approach(vx, Mth.sign(dx) * sp, 1100 * dt);
            animName = "walk";
            stepT -= dt;
            int f = sheet.anim("walk").frameAt(animT);
            if ((f == 1 || f == 5) && stepT <= 0) { stepT = 0.2f; Snd.sfxAt(def.sfx + "step", x, sfxX(lv), 0.55f); lv.shake(0.9f, 0.08f); }
        } else {
            vx = Mth.approach(vx, 0, 1100 * dt);
            animName = "idle";
        }
        if (cdT > 0) return;
        // elegir ataque
        float w1 = ad < 92 ? 3 : 0, w2 = (ad < 150 && ad > 40) ? 3 : 0, w3 = (ad < 110 || ph2() && ad < 150) ? 2.2f : 0, wc = ad > 70 ? 2.2f : 1.2f;
        if (castsRow >= 2) wc = 0;
        if (flying) { w1 = ad < 120 ? 3 : 0; w2 = ad < 160 ? 2 : 0; w3 = ad < 130 ? 2 : 0; }
        if (lastAtk == 1) w1 *= 0.4f; else if (lastAtk == 2) w2 *= 0.4f; else if (lastAtk == 3) w3 *= 0.4f;
        float tot = w1 + w2 + w3 + wc;
        float r = lv.rng.f() * tot;
        if (tot <= 0) return;
        if (r < wc) { startCast(lv); return; }
        r -= wc;
        if (r < w1) { startAttack(lv, 1); return; }
        r -= w1;
        if (r < w2) { startAttack(lv, 2); return; }
        startAttack(lv, 3);
    }

    private void startAttack(Level lv, int k) {
        atk = k; lastAtk = k; castsRow = 0;
        state = WINDUP; stateT = 0; animName = "windup" + k; animT = 0;
        hitDone = false; extraDone = false;
        vx = 0;
        if (Math.random() < 0.55) sfx(lv, "roar", 0.7f);
    }

    private void updateWindup(Level lv, float dt, Player p, float dx) {
        Anim a = sheet.anim(animName);
        if (stateT < a.duration() * 0.55f) face(dx);
        vx = Mth.approach(vx, 0, 900 * dt);
        if (flying) {
            hoverTo(lv, p, dt, p.x + (right ? -64 : 64) * 0.6f, p.y - 4, def.speed * 1.2f);
        }
        // parpadeo de aviso
        if (a.done(animT)) {
            state = ATTACK; stateT = 0; animName = "attack" + atk; animT = 0;
            hitDone = false; extraDone = false;
            float m = atk == 2 ? 1.2f : (atk == 1 ? 0.8f : 0.5f);
            vx = (right ? 1 : -1) * def.lunge * m * (ph2() ? 1.2f : 1f);
            sfx(lv, "atk" + atk, 1f);
            if (flying) vy = 0;
        }
    }

    private void updateAttack(Level lv, float dt, Player p) {
        Anim a = sheet.anim(animName);
        vx = Mth.approach(vx, 0, 520 * dt);
        if (flying) vy = Mth.approach(vy, 0, 600 * dt);
        if (!hitDone && a.hitActive(animT) && a.worldBox(x, y, right, box)) {
            if (p.overlaps(box[0], box[1], box[2], box[3])) {
                hitDone = true;
                float mult = atk == 2 ? 1.15f : (atk == 3 ? 1.3f : 1f);
                if (ph2()) mult *= 1.12f;
                lv.hurtPlayer(dmgBase * mult, x, -1, 0);
            }
        }
        if (a.h0 >= 0 && a.frameAt(animT) >= a.h0 && !extraDone && atk == 3) {
            extraDone = true;
            slamExtra(lv, p);
            lv.shake(5f, 0.3f);
            lv.hitstop(0.05f);
        } else if (a.h0 >= 0 && a.frameAt(animT) >= a.h0 && !extraDone) {
            extraDone = true;
            lv.shake(2.5f, 0.15f);
            lv.fx("fx_dust", "land", x + (right ? 40 : -40), y - 2, 1.4f, 0, 0).right = right;
        }
        if (a.done(animT)) {
            state = RECOVER; stateT = 0; animName = "idle"; animT = 0;
            cdT = (ph2() ? 0.35f : 0.75f) + lv.rng.f() * 0.4f;
        }
    }

    private void startCast(Level lv) {
        state = CAST; stateT = 0; animName = "cast"; animT = 0; fired = false; vx = 0; castsRow++;
        sfx(lv, "cast", 1f);
    }

    private void updateCast(Level lv, float dt, Player p) {
        Anim a = sheet.anim("cast");
        vx = Mth.approach(vx, 0, 900 * dt);
        face(p.x - x);
        if (flying) hoverTo(lv, p, dt, x, p.y - 80, 80);
        if (!fired && a.frameAt(animT) >= Math.max(0, a.rel)) { fired = true; doCast(lv, p); }
        if (Math.random() < dt * 30) lv.ps.spawn(a.muzzleX(x, right) + lv.rng.f(-8, 8), a.muzzleY(y) + lv.rng.f(-8, 8), 0, -20, 0.4f, 2, 0, def.color, true);
        if (a.done(animT)) {
            state = RECOVER; stateT = 0; animName = "idle"; animT = 0;
            cdT = (ph2() ? 0.4f : 0.8f) + lv.rng.f() * 0.4f;
        }
    }

    // ------------------------------------------------------------------ conjuros
    private void doCast(Level lv, Player p) {
        Anim a = sheet.anim("cast");
        float mx = a.muzzleX(x, right), my = a.muzzleY(y);
        float cdmg = dmgBase * 0.62f;
        int n = def.castCount + (ph2() ? 2 : 0);
        switch (def.castKind) {
            case BossDef.CAST_FAN: {
                float base = (float) Math.atan2(p.cy() - my, p.x - mx);
                for (int i = 0; i < n; i++) {
                    float ang = base + (i - (n - 1) / 2f) * (0.9f / Math.max(1, n - 1));
                    shoot(lv, mx, my, ang, 150f + (ph2() ? 30 : 0), cdmg);
                }
                break;
            }
            case BossDef.CAST_AIM: {
                int shots = 3 + (ph2() ? 2 : 0);
                for (int i = 0; i < shots; i++) {
                    final float fmx = mx, fmy = my;
                    lv.later(i * 0.28f, () -> {
                        if (!lv.pl.alive) return;
                        float ang = (float) Math.atan2(lv.pl.cy() - fmy, lv.pl.x - fmx);
                        shoot(lv, fmx, fmy, ang, 230f, cdmg);
                        Snd.sfxAt("en_cast", fmx, sfxX(lv), 0.5f);
                    });
                }
                break;
            }
            case BossDef.CAST_SUMMON: {
                if (def.minions == null) { doFan(lv, p, mx, my, cdmg, n); break; }
                int alive = 0;
                for (Enemy e : lv.enemies) if (e.alive) alive++;
                int want = Math.min(ph2() ? 3 : 2, 5 - alive);
                for (int i = 0; i < want; i++) {
                    String id = def.minions[lv.rng.i(def.minions.length)];
                    EnemyDef ed = EnemyDef.get(id);
                    if (ed == null) continue;
                    float sx = Mth.clamp(p.x + (i == 0 ? -1 : 1) * (60 + 40 * i), 40, lv.room.pixW - 40);
                    Enemy e = new Enemy(ed, false, lv.rs.enemyHpMul() * 0.6f, lv.rs.enemyDmgMul());
                    boolean fl = ed.role == EnemyDef.FLY_DIVE || ed.role == EnemyDef.FLY_SHOOT;
                    e.x = sx; e.y = fl ? floorY - 80 : floorY; e.home = sx;
                    lv.enemies.add(e);
                    lv.fxAdd("fx_smoke", "big", sx, e.y - 20, 0.8f, def.color);
                    lv.ps.burst(lv.rng, sx, e.y - 14, def.color, 14, 100, 0.5f, 2, 0, true);
                }
                if (want > 0) Snd.sfx("en_alert", 0.8f);
                doFan(lv, p, mx, my, cdmg, 3);
                break;
            }
            case BossDef.CAST_RAIN: {
                for (int i = 0; i < n; i++) {
                    final int idx = i;
                    lv.later(i * 0.13f, () -> {
                        float rx = Mth.clamp(lv.pl.x + (idx == 0 ? 0 : lv.rng.f(-150, 150)), 40, lv.room.pixW - 40);
                        rain(lv, rx, 30f, cdmg);
                    });
                }
                break;
            }
            case BossDef.CAST_LINES: {
                for (int i = 0; i < n; i++) {
                    float lx = Mth.clamp(p.x + (i - (n - 1) / 2f) * 64f + lv.rng.f(-12, 12), 40, lv.room.pixW - 40);
                    strike(lv, lx, 0.75f + i * 0.12f, cdmg * 1.3f);
                }
                break;
            }
            default: break;
        }
    }

    private void doFan(Level lv, Player p, float mx, float my, float cdmg, int n) {
        float base = (float) Math.atan2(p.cy() - my, p.x - mx);
        for (int i = 0; i < n; i++) shoot(lv, mx, my, base + (i - (n - 1) / 2f) * 0.35f, 150f, cdmg);
    }

    private void shoot(Level lv, float mx, float my, float ang, float spd, float dmg) {
        Proj pr = lv.proj(mx, my, (float) Math.cos(ang) * spd, (float) Math.sin(ang) * spd, dmg, false, def.castProj, def.color);
        pr.life = 5f; pr.radius = 6; pr.scale = 1.3f;
        pr.explode = 0;
        if (def.element.equals("blood") || def.element.equals("void")) pr.homing = 60;
        lv.fxAdd("fx_hit", "magic", mx, my, 0.8f, def.color);
    }

    private void rain(Level lv, float rx, float startY, float dmg) {
        Proj pr = lv.proj(rx, startY, lv.rng.f(-14, 14), 120, dmg, false, def.castProj, def.color);
        pr.grav = 420f; pr.explode = 24; pr.radius = 7; pr.life = 4f; pr.scale = 1.4f; pr.passWalls = false;
        pr.explodeFx = "fx_explosion:a";
    }

    /** Rayo/pilar con aviso previo en el suelo. */
    private void strike(Level lv, float sx, float delay, float dmg) {
        float gy = lv.groundBelow(sx, lv.pl.y - 24);
        FxObj w = lv.fxAdd("fx_ring", "pulse", sx, gy - 3, 0.5f, def.color);
        if (w != null) { w.loop = false; w.alpha = 0.9f; }
        lv.later(delay * 0.5f, () -> lv.fxAdd("fx_ring", "pulse", sx, gy - 3, 0.5f, 0xFF4040));
        lv.later(delay, () -> {
            pillar(lv, sx, gy);
            zone(lv, sx, 26, 90, gy, dmg);
            lv.shake(2.5f, 0.15f);
            Snd.sfxAt(def.element.equals("lightning") ? "hit_shock" : "explosion_small", sx, sfxX(lv), 0.8f);
        });
    }

    /** Daña al jugador si su caja toca la columna centrada en cx. */
    private void zone(Level lv, float cx, float w, float h, float gy, float dmg) {
        Player p = lv.pl;
        if (p.alive && p.overlaps(cx - w / 2, gy - h, w, h)) lv.hurtPlayer(dmg, cx, -1, 0);
    }

    private static final String[] PIL_SHEET = {"fx_fire", "fx_ice", "fx_lightning", "fx_shadow", "fx_void", "fx_holy", "fx_thorn", "fx_blood", "fx_rock"};
    private static final String[] PIL_ANIM = {"pillar", "spike", "ground", "blade", "rift", "beam", "vine", "splat", "pillar"};
    private static final int[] PIL_H = {48, 64, 128, 48, 64, 128, 48, 48, 64};

    private int pillarIdx() {
        switch (def.element) {
            case "fire": return 0;
            case "ice": return 1;
            case "lightning": return 2;
            case "shadow": return 3;
            case "void": return 4;
            case "holy": return 5;
            case "thorn": return 6;
            case "blood": return 7;
            default: return 8;
        }
    }

    private void pillar(Level lv, float px, float gy) {
        int i = pillarIdx();
        float hh = PIL_H[i];
        FxObj f = lv.fxAdd(PIL_SHEET[i], PIL_ANIM[i], px, gy - hh / 2f + 2, 1.15f, def.color);
        FxObj f2 = lv.fx(PIL_SHEET[i], PIL_ANIM[i], px, gy - hh / 2f + 2, 1.15f, 0, 0);
        if (f2 != null) f2.alpha = 0.6f;
        lv.ps.burst(lv.rng, px, gy - 6, def.color, 8, 100, 0.4f, 2, 200, true);
        lv.fx("fx_dust", "land", px, gy - 2, 1.2f, 0, 0);
    }

    private void slamExtra(Level lv, Player p) {
        float dmg = dmgBase * 0.9f * (ph2() ? 1.15f : 1f);
        float gy = lv.groundBelow(x, y - 8);
        if (flying) gy = lv.groundBelow(p.x, p.y - 24);
        switch (def.slamExtra) {
            case BossDef.SLAM_ERUPT_LINE: {
                float dir = right ? 1 : -1;
                int count = ph2() ? 9 : 7;
                for (int i = 0; i < count; i++) {
                    final int idx = i;
                    lv.later(0.05f + i * 0.07f, () -> {
                        float px = x + dir * (44 + idx * 36);
                        float g2 = lv.groundBelow(px, y - 8);
                        pillar(lv, px, g2);
                        zone(lv, px, 26, 70, g2, dmg);
                        Snd.sfxAt("explosion_small", px, sfxX(lv), 0.4f);
                    });
                }
                break;
            }
            case BossDef.SLAM_ERUPT_PLAYER: {
                strike(lv, p.x, 0.7f, dmg);
                if (ph2()) { strike(lv, p.x - 64, 0.95f, dmg); strike(lv, p.x + 64, 1.1f, dmg); }
                break;
            }
            case BossDef.SLAM_RAIN: {
                int n = ph2() ? 8 : 6;
                for (int i = 0; i < n; i++) {
                    final int idx = i;
                    lv.later(i * 0.1f, () -> rain(lv, Mth.clamp(lv.pl.x + (idx == 0 ? 0 : lv.rng.f(-140, 140)), 40, lv.room.pixW - 40), 30f, dmg * 0.8f));
                }
                break;
            }
            case BossDef.SLAM_PULL: {
                pullT = 0.9f;
                lv.fxAdd("fx_void", "hole", x, y - bh * 0.4f, 1.6f, def.color);
                Snd.sfx("time_stop", 0.4f);
                lv.later(0.95f, () -> {
                    lv.explosion(x, y - 40, 76, dmg * 1.2f, 0, -1, 0, 0, false);
                    lv.fxAdd("fx_explosion", "a", x, y - 40, 1.4f, def.color);
                    lv.shake(4f, 0.3f);
                });
                break;
            }
            case BossDef.SLAM_ROCKS: {
                for (int i = 0; i < 5; i++) rain(lv, Mth.clamp(p.x + lv.rng.f(-130, 130), 40, lv.room.pixW - 40), 30f, dmg * 0.7f);
                break;
            }
            default: break;
        }
        // onda de choque en el suelo
        lv.fx("fx_shock", "wave", x + (right ? 50 : -50), gy - 12, 1f, 0, 0).right = right;
        lv.ps.burst(lv.rng, x + (right ? 40 : -40), gy - 2, 0xB0A090, 14, 140, 0.5f, 3, 200, false);
    }

    // ------------------------------------------------------------------ dibujo
    public void render(Platform.Gfx g, Level lv) {
        if (alphaMul <= 0.01f) return;
        Anim a = sheet.anim(animName);
        int frame = a.frameAt(animT);
        int flags = 0, tint = Status.tint(this);
        if (tint != 0) flags |= Platform.TINT;
        if (hitFlash > 0) { flags |= Platform.FLASH; tint = 0xFFFFFF; }
        else if (state == WINDUP) { flags |= Platform.TINT; tint = ((int) (lv.time * 16) & 1) == 0 ? 0xFFC8B8 : 0xFFFFFF; }
        else if (ph2() && state != DEAD) { flags |= Platform.TINT; tint = Mth.mix(0xFFFFFF, def.color, 0.22f + 0.08f * (float) Math.sin(lv.time * 4)); }
        float alpha = alphaMul;
        if (state == DEAD) alpha = Mth.clamp((deadT < 1.8f ? 1f : 1f - (deadT - 1.8f) / 1.2f), 0f, 1f);
        float dy = flying && state != DEAD && state != INTRO ? (float) Math.sin(bob * 2f) * 3f : 0f;
        if (!flying || state == DEAD) g.rect(Math.round(x - 26 + offX), Math.round(y - 2), 52, 3, 0x55000000, false);
        UI.light(g, x + offX, y - bh * 0.5f + offY + dy, 70, def.color, state == DEAD ? 0.1f : 0.16f);
        float bspd = (float) Math.hypot(vx, vy);
        if (state == ATTACK && bspd > 160f && !Impact.react(lv, this, rx)) {      // smear de embestida del jefe (solo visual; el patron y la zona peligrosa no cambian)
            float k = Mth.clamp((bspd - 160f) / 260f, 0.3f, 1f);
            boolean vert = Math.abs(vy) > Math.abs(vx) * 1.4f;
            float sx2 = vert ? 1f - 0.06f * k : 1f + 0.14f * k, sy2 = vert ? 1f + 0.14f * k : 1f - 0.06f * k;
            if (!Save.S.reduceFx) for (int i = 2; i >= 1; i--)
                sheet.drawSq(g, a, frame, x + offX - vx / bspd * 8f * i, y + offY + dy - vy / bspd * 8f * i, right, sx2, sy2, Platform.ADD | Platform.TINT, def.color, i == 1 ? 0.24f : 0.12f);
            sheet.drawSq(g, a, frame, x + offX, y + offY + dy, right, sx2, sy2, flags, tint, alpha);
        } else if (Impact.react(lv, this, rx)) sheet.drawSq(g, a, frame, x + offX + rx[2], y + offY + dy, right, rx[0], rx[1], flags, tint, alpha);
        else sheet.draw(g, a, frame, x + offX, y + offY + dy, right, 1f, flags, tint, alpha);
    }
    private final float[] rx = new float[3];
}
