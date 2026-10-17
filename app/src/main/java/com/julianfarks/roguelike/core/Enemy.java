package com.julianfarks.roguelike.core;

/** Enemigo normal o elite. La IA depende del rol definido en EnemyDef. */
public final class Enemy extends Ent {
    static final int PATROL = 0, CHASE = 1, WINDUP = 2, ATTACK = 3, RECOVER = 4, HURT = 5, DEAD = 6, CHARGE = 7, DIVE = 8, AIM = 9, VANISH = 10, FUSE = 11, LEAP = 12;

    public final EnemyDef def;
    public final boolean elite;
    public float home;
    public boolean remove;
    public int state = PATROL;
    private float stateT, atkCd, deadT, patrolDir = 1, patrolWait, contactCd, bob, spawnT;
    private boolean aggro, shot, hitDone;
    private final float dmg, speed;
    private final int statusId;
    private float tx, ty;           // objetivo de embestida / picada
    private final float cooldown;
    float buffT;                    // aura de furia (cultista): +35% daño, +20% velocidad
    private Enemy healTgt;
    private boolean suicide, blocked;
    private float aimX, aimY;

    public Enemy(EnemyDef d, boolean elite, float hpMul, float dmgMul) {
        this.def = d;
        this.elite = elite;
        sheet = Assets.sheet(d.sheet);
        scale = elite ? 1.22f : 1f;
        bw = sheet.bw * scale;
        bh = sheet.bh * scale;
        maxHp = hp = d.hp * hpMul * (elite ? 2.6f : 1f);
        dmg = d.dmg * dmgMul * (elite ? 1.3f : 1f);
        speed = d.speed * (elite ? 1.15f : 1f);
        cooldown = d.cooldown * (elite ? 0.8f : 1f);
        flying = d.role == EnemyDef.FLY_SHOOT || d.role == EnemyDef.FLY_DIVE;
        gravity = !flying;
        statusId = Status.parse(d.status);
        right = Math.random() < 0.5;
        patrolDir = right ? 1 : -1;
        bob = (float) (Math.random() * 6.28);
        atkCd = 0.6f + (float) Math.random();
        spawnT = 0.0f;
    }

    float dmgNow() { return dmg * (buffT > 0 ? 1.35f : 1f); }

    /** Invisible e intocable (el asesino mientras se desvanece). */
    public boolean untargetable() { return alive && state == VANISH; }

    /** Reduce el daño recibido: escudo frontal del escudero y coraza de cristal de la torreta. */
    public float filterDamage(Level lv, float d, float kx, float ky) {
        blocked = false;
        if (def.role == EnemyDef.SHIELD && kx != 0 && state != ATTACK && state != RECOVER && state != HURT && !frozen()) {
            boolean front = (right && kx < 0) || (!right && kx > 0);
            if (front) {
                if (ky <= -100f) {      // golpe pesado (remate del combo, habilidades fuertes): rompe la guardia
                    applyStatus(Ent.STUN, 1.0f, 0);
                    lv.text(x, y - bh - 14, "¡Guardia rota!", 0xFFD25A, true);
                    Snd.sfxv("hit_metal_2", 0.9f);
                    return d;
                }
                blocked = true;
                lv.text(x, y - bh - 12, "bloqueado", 0xA8B0C0, false);
                Snd.sfxAt("hit_metal_1", x, lv.camX + lv.viewW / 2, 0.8f);
                lv.fx("fx_hit", "spark", x + (right ? 10 : -10) * scale, y - bh * 0.5f, 1f, 0, 0);
                return d * 0.2f;
            }
        }
        if (def.role == EnemyDef.TURRET && state != WINDUP && state != ATTACK) {
            lv.text(x, y - bh - 12, "cristal", 0x9AE0FF, false);
            Snd.sfxAt("hit_ice", x, lv.camX + lv.viewW / 2, 0.5f);
            return d * 0.45f;
        }
        return d;
    }

    public boolean deadAnimDone() { return !alive && sheet.anim("death").done(animT); }

    public void animFrozen(float dt) { }

    private boolean superArmor() { return elite || def.role == EnemyDef.HEAVY || def.role == EnemyDef.CHARGER; }

    // ------------------------------------------------------------------ reaccion al daño
    public void onHit(Level lv, float kx, float ky, float dmgTaken) {
        aggro = true;
        if (kx == 0 && ky == 0) return;
        if (blocked) { vx += kx * 0.12f; blocked = false; return; }
        if (def.role == EnemyDef.TURRET) { if (state != WINDUP && state != ATTACK) { state = HURT; stateT = 0; animName = "hurt"; animT = 0; } return; }
        float resist = def.role == EnemyDef.HEAVY || def.role == EnemyDef.SHIELD ? 0.45f : (def.role == EnemyDef.CHARGER ? 0.55f : 1f);
        if (elite) resist *= 0.6f;
        if (!flying) vx = kx * resist; else { vx = kx * resist * 0.8f; }
        if (ky != 0) vy = flying ? ky * 0.5f : Math.min(0, ky) * resist;
        boolean stagger = !(superArmor() && (state == WINDUP || state == ATTACK || state == CHARGE) && dmgTaken < maxHp * 0.18f);
        if (stagger && state != DEAD) {
            state = HURT; stateT = 0; animName = "hurt"; animT = 0; hitDone = false;
        }
        Snd.sfxAt(Math.random() < 0.5 ? "en_hurt_1" : "en_hurt_2", x, lv.camX + lv.viewW / 2, 0.45f);
    }

    // ------------------------------------------------------------------ muerte
    public void die(Level lv) {
        if (!alive) return;
        alive = false;
        state = DEAD;
        animName = "death"; animT = 0;
        flying = false; gravity = true;
        RunState rs = lv.rs;
        Stats s = rs.stats;
        Snd.sfxAt(def.dieSfx, x, lv.camX + lv.viewW / 2, 0.9f);
        lv.toKill--;
        rs.kills++;
        if (def.role == EnemyDef.EXPLODER && !suicide) blast(lv, 0.7f, 36);   // volatil: abatirlo de cerca tambien duele
        Unlocks.check(lv);
        lv.fx("fx_ring", "pulse", x, y - bh / 2f, elite ? 0.8f : 0.45f, def.color, Platform.ADD | Platform.TINT);
        lv.ps.burst(lv.rng, x, y - bh / 2f, 0xFFFFFF, 8, 140, 0.3f, 2, 0, true);
        for (int k = 0; k < 4; k++) lv.ps.spawn(x + lv.rng.f(-6, 6), y - bh / 2f, lv.rng.f(-14, 14), -lv.rng.f(40, 95), 1.1f, 2, -25, def.color, true);
        float m = elite ? 3f : 1f;
        if (suicide) m = 0f;
        if (m > 0) lv.dropGold(x, y - 10, Math.round((3 + lv.rng.i(5)) * m * s.goldMul));
        if (m > 0) lv.dropSouls(x, y - 10, Math.max(1, Math.round(def.souls * m * s.soulMul * 0.5f)) * 2);
        if (m > 0 && lv.rng.chance(elite ? 0.45f : 0.07f)) lv.drop(Pickup.HEART, x, y - 10, 1);
        if (m > 0 && lv.rng.chance(elite ? 0.18f : 0.025f)) lv.drop(Pickup.POTION, x, y - 10, 1);
        if (lv.pl != null && !suicide) lv.pl.addFuria(lv);
        rs.ult = Math.min(100f, rs.ult + 3f * s.ultGain);
        lv.ps.burst(lv.rng, x, y - bh / 2, def.color, elite ? 26 : 14, 150, 0.6f, 3, 300, false);
        lv.ps.burst(lv.rng, x, y - bh / 2, 0xFFFFFF, 6, 90, 0.3f, 2, 0, true);
        if (s.vengeance > 0) {
            lv.explosion(x, y - bh / 2, 46 + 8 * s.vengeance, lv.pl.baseDmg(lv) * 0.9f * s.vengeance, 140, -1, 0, 0, true);
            lv.fxAdd("fx_explosion", "a", x, y - bh / 2, 0.55f, 0xFFB060);
            Snd.sfxv("explosion_small", 0.6f);
        }
        lv.hitstop(elite ? 0.1f : 0.04f);
        if (elite) lv.shake(3f, 0.25f);
    }

    // ------------------------------------------------------------------ actualizacion
    public void update(Level lv, float dt) {
        if (!alive) {
            animT += dt;
            deadT += dt;
            vy = Math.min(Level.FALL_MAX, vy + Level.GRAV * dt);
            vx *= 0.92f;
            lv.move(this, dt);
            if (deadT > 2.2f) remove = true;
            return;
        }
        animT += dt;
        spawnT += dt;
        if (atkCd > 0) atkCd -= dt;
        if (contactCd > 0) contactCd -= dt;
        if (hitFlash > 0) hitFlash -= dt;
        if (buffT > 0) buffT -= dt;
        stateT += dt;
        float dps = Status.tick(this, dt);
        Status.fx(lv, this, dt);
        if (dps > 0) {
            dotAcc += dps * dt;
            if (dotAcc >= 2f) { int d = (int) dotAcc; dotAcc -= d; lv.damageEnemy(this, d, false, 0, 0); if (!alive) return; }
        }
        Player p = lv.pl;
        boolean paused = frozen() || p == null || !p.alive;
        float dx = p.x - x, dy = p.cy() - cy();
        float dist = (float) Math.sqrt(dx * dx + dy * dy);
        if (!aggro && dist < def.detect && Math.abs(dy) < 110 && !paused) { aggro = true; Snd.sfxAt("en_alert", x, lv.camX + lv.viewW / 2, 0.35f); if (state == PATROL) state = CHASE; }
        if (aggro && dist > def.detect * 2.2f) { aggro = false; state = PATROL; }

        if (paused || state == DEAD) {
            if (!flying) vy = Math.min(Level.FALL_MAX, vy + Level.GRAV * dt);
            vx = Mth.approach(vx, 0, 800 * dt);
            lv.move(this, dt);
            if (!frozen()) { animName = "idle"; }
            else if (st[Ent.FREEZE] > 0) animT -= dt;   // congelado: fotograma quieto
            return;
        }

        float sp = speed * speedMul() * (buffT > 0 ? 1.2f : 1f);
        switch (def.role) {
            case EnemyDef.MELEE: case EnemyDef.HEAVY: case EnemyDef.SHIELD: meleeAI(lv, dt, p, dx, dy, sp); break;
            case EnemyDef.SUPPORT: case EnemyDef.BUFFER: supportAI(lv, dt, p, dx, dy, dist, sp); break;
            case EnemyDef.EXPLODER: exploderAI(lv, dt, p, dx, dy, sp); break;
            case EnemyDef.TURRET: turretAI(lv, dt, p, dx, dy, dist); break;
            case EnemyDef.POUNCER: pouncerAI(lv, dt, p, dx, dy, sp); break;
            case EnemyDef.SNIPER: sniperAI(lv, dt, p, dx, dy, dist, sp); break;
            case EnemyDef.BLINKER: blinkerAI(lv, dt, p, dx, dy, dist, sp); break;
            case EnemyDef.RANGED: case EnemyDef.CASTER: rangedAI(lv, dt, p, dx, dy, dist, sp); break;
            case EnemyDef.FLY_SHOOT: flyShootAI(lv, dt, p, dx, dy, dist, sp); break;
            case EnemyDef.FLY_DIVE: flyDiveAI(lv, dt, p, dx, dy, dist, sp); break;
            case EnemyDef.CHARGER: chargerAI(lv, dt, p, dx, dy, sp); break;
            case EnemyDef.JUMPER: jumperAI(lv, dt, p, dx, dy, sp); break;
            default: break;
        }
        // daño por contacto
        if (def.contact > 0 && contactCd <= 0 && (state == CHARGE || state == DIVE || state == LEAP || def.role == EnemyDef.JUMPER || def.role == EnemyDef.FLY_DIVE) && p.alive
                && overlaps(p.x - p.bw / 2, p.y - p.bh, p.bw, p.bh)) {
            if (lv.hurtPlayer(def.contact * dmgNow() / Math.max(1f, def.dmg), x, statusId, 3f)) contactCd = 0.8f;
        }
    }

    private boolean groundAhead(Level lv, float dir) {
        float fx = x + dir * (bw / 2 + 5);
        int t = lv.room.tile((int) Math.floor(fx / Room.TS), (int) Math.floor((y + 4) / Room.TS));
        return Room.isSolid(t) || t == Room.ONEWAY;
    }

    private void face(float dx) { if (Math.abs(dx) > 3) right = dx > 0; }

    private void patrol(Level lv, float dt, float sp) {
        if (patrolWait > 0) {
            patrolWait -= dt;
            vx = Mth.approach(vx, 0, 700 * dt);
            animName = "idle";
        } else {
            if (hitWall || !groundAhead(lv, patrolDir) || (patrolDir > 0 && x > home + 70) || (patrolDir < 0 && x < home - 70)) {
                patrolDir = -patrolDir; patrolWait = 0.6f + lv.rng.f() * 1.2f; vx = 0;
            }
            vx = patrolDir * sp * 0.45f;
            right = patrolDir > 0;
            animName = "walk";
        }
        if (!flying) vy = Math.min(Level.FALL_MAX, vy + Level.GRAV * dt);
        lv.move(this, dt);
    }

    private boolean finishedAnim() { return sheet.anim(animName).done(animT); }

    private void startState(int s, String anim) { state = s; stateT = 0; animName = anim; animT = 0; shot = false; hitDone = false; }

    // ------------------------------------------------------------------ cuerpo a cuerpo
    private void meleeAI(Level lv, float dt, Player p, float dx, float dy, float sp) {
        boolean heavy = def.role == EnemyDef.HEAVY;
        switch (state) {
            case PATROL: patrol(lv, dt, sp); return;
            case CHASE: {
                face(dx);
                float stop = def.range * 0.8f;
                boolean near = Math.abs(dx) <= def.range && Math.abs(dy) < 30;
                if (Math.abs(dx) > stop && groundAhead(lv, Mth.sign(dx))) { vx = Mth.approach(vx, Mth.sign(dx) * sp, 900 * dt); animName = "walk"; }
                else { vx = Mth.approach(vx, 0, 900 * dt); if (animName.equals("walk")) animName = "idle"; }
                if (hitWall && p.y < y - 24 && onGround) { vy = -300; }   // salta obstaculos si el jugador esta arriba
                if (near && atkCd <= 0) { startState(WINDUP, "windup"); vx = 0; Snd.sfxAt("en_alert", x, lv.camX + lv.viewW / 2, 0.25f); }
                break;
            }
            case WINDUP: {
                vx = Mth.approach(vx, 0, 900 * dt);
                if (heavy) animT -= dt * 0.25f;
                face(dx * (stateT < 0.15f ? 1 : 0));
                if (finishedAnim()) { startState(ATTACK, "attack"); vx = (right ? 1 : -1) * (heavy ? 60 : 110); Snd.sfxAt(heavy ? "en_step_heavy" : "en_attack_melee", x, lv.camX + lv.viewW / 2, 0.6f); }
                break;
            }
            case ATTACK: {
                Anim a = sheet.anim("attack");
                vx = Mth.approach(vx, 0, 500 * dt);
                if (!hitDone && a.hitActive(animT)) {
                    float[] b = new float[4];
                    if (a.worldBox(x, y, right, b)) {
                        // la caja se escala con el enemigo elite
                        if (scale != 1f) { b[2] *= scale; b[3] *= scale; if (!right) b[0] -= b[2] * (scale - 1); }
                        if (p.overlaps(b[0], b[1], b[2], b[3])) { hitDone = true; lv.hurtPlayer(dmgNow(), x, statusId, 3f); }
                    }
                }
                if (a.done(animT)) { state = RECOVER; stateT = 0; animName = "idle"; atkCd = cooldown * (0.85f + lv.rng.f() * 0.4f); }
                break;
            }
            case RECOVER:
                vx = Mth.approach(vx, 0, 900 * dt);
                if (stateT > 0.25f) state = CHASE;
                break;
            case HURT:
                vx = Mth.approach(vx, 0, 500 * dt);
                if (stateT > 0.26f) { state = CHASE; animName = "idle"; }
                break;
            default: state = CHASE; break;
        }
        if (!flying) vy = Math.min(Level.FALL_MAX, vy + Level.GRAV * dt);
        lv.move(this, dt);
    }

    // ------------------------------------------------------------------ rango
    private void rangedAI(Level lv, float dt, Player p, float dx, float dy, float dist, float sp) {
        switch (state) {
            case PATROL: patrol(lv, dt, sp); return;
            case CHASE: {
                face(dx);
                float ad = Math.abs(dx);
                float want = def.range * 0.7f;
                if (ad < def.range * 0.42f && groundAhead(lv, -Mth.sign(dx)) && !hitWall) { vx = Mth.approach(vx, -Mth.sign(dx) * sp, 900 * dt); animName = "walk"; }
                else if (ad > def.range * 0.95f && groundAhead(lv, Mth.sign(dx))) { vx = Mth.approach(vx, Mth.sign(dx) * sp, 900 * dt); animName = "walk"; }
                else { vx = Mth.approach(vx, 0, 900 * dt); animName = "idle"; }
                if (ad < def.range && Math.abs(dy) < 120 && atkCd <= 0) { startState(WINDUP, "windup"); vx = 0; }
                break;
            }
            case WINDUP:
                vx = Mth.approach(vx, 0, 900 * dt);
                face(dx);
                if (finishedAnim()) { startState(ATTACK, "attack"); }
                break;
            case ATTACK: {
                Anim a = sheet.anim("attack");
                vx = Mth.approach(vx, 0, 900 * dt);
                int fireFrame = Math.max(1, a.h0 >= 0 ? a.h0 : a.n / 2);
                if (!shot && a.frameAt(animT) >= fireFrame) { shot = true; fire(lv, p); }
                if (a.done(animT)) { state = RECOVER; stateT = 0; animName = "idle"; atkCd = cooldown * (0.85f + lv.rng.f() * 0.4f); }
                break;
            }
            case RECOVER:
                if (stateT > 0.2f) state = CHASE;
                break;
            case HURT:
                vx = Mth.approach(vx, 0, 500 * dt);
                if (stateT > 0.26f) { state = CHASE; animName = "idle"; }
                break;
            default: state = CHASE; break;
        }
        if (!flying) vy = Math.min(Level.FALL_MAX, vy + Level.GRAV * dt);
        lv.move(this, dt);
    }

    private void fire(Level lv, Player p) {
        float mx = x + (right ? 14 : -14) * scale, my = y - bh * 0.6f;
        Anim a = sheet.anim("attack");
        if (a.muzzle != null) { mx = a.muzzleX(x, right); my = a.muzzleY(y); }
        float tx2 = p.x, ty2 = p.cy();
        float ddx = tx2 - mx, ddy = ty2 - my;
        float d = (float) Math.sqrt(ddx * ddx + ddy * ddy) + 0.001f;
        boolean caster = def.role == EnemyDef.CASTER;
        float pspd = caster ? 135f : (def.proj != null && def.proj.equals("arrow") ? 240f : 170f);
        int n = caster && elite ? 3 : 1;
        for (int i = 0; i < n; i++) {
            float ang = (float) Math.atan2(ddy, ddx) + (i - (n - 1) / 2f) * 0.28f;
            Proj pr = lv.proj(mx, my, (float) Math.cos(ang) * pspd, (float) Math.sin(ang) * pspd, dmgNow(), false, def.proj, def.color);
            pr.status = statusId; pr.statusDur = 3f;
            pr.life = 4f;
            if (caster) pr.homing = 90f;
            if (def.proj.equals("arrow")) { pr.grav = 60f; pr.trail = false; }
            pr.radius = 5;
        }
        Snd.sfxAt(def.proj.equals("arrow") ? "arrow_shot" : "en_cast", x, lv.camX + lv.viewW / 2, 0.55f);
        lv.fxAdd("fx_hit", "magic", mx, my, 0.6f, def.color);
    }

    // ------------------------------------------------------------------ voladores
    private void flyMove(Level lv, float dt, float gx, float gy, float sp, float acc) {
        float dx = gx - x, dy = gy - y;
        float d = (float) Math.sqrt(dx * dx + dy * dy);
        float k = Math.min(1f, d / 30f);
        float tvx = d > 1 ? dx / d * sp * k : 0, tvy = d > 1 ? dy / d * sp * k : 0;
        vx = Mth.approach(vx, tvx, acc * dt);
        vy = Mth.approach(vy, tvy, acc * dt);
        lv.move(this, dt);
    }

    private void flyShootAI(Level lv, float dt, Player p, float dx, float dy, float dist, float sp) {
        bob += dt * 2.4f;
        switch (state) {
            case PATROL: {
                animName = "idle";
                flyMove(lv, dt, home + (float) Math.sin(bob * 0.5f) * 40, y + (float) Math.sin(bob) * 3, sp * 0.4f, 300);
                return;
            }
            case CHASE: {
                face(dx);
                float side = dx > 0 ? -1 : 1;
                float gx = p.x + side * def.range * 0.55f, gy = p.y - 62 + (float) Math.sin(bob) * 10;
                animName = "idle";
                flyMove(lv, dt, gx, gy, sp, 500);
                if (dist < def.range && atkCd <= 0) { startState(WINDUP, "windup"); }
                break;
            }
            case WINDUP:
                face(dx);
                vx = Mth.approach(vx, 0, 600 * dt); vy = Mth.approach(vy, 0, 600 * dt);
                lv.move(this, dt);
                if (finishedAnim()) startState(ATTACK, "attack");
                break;
            case ATTACK: {
                Anim a = sheet.anim("attack");
                lv.move(this, dt);
                int ff = Math.max(1, a.h0 >= 0 ? a.h0 : a.n / 2);
                if (!shot && a.frameAt(animT) >= ff) { shot = true; fire(lv, p); }
                if (a.done(animT)) { state = RECOVER; stateT = 0; animName = "idle"; atkCd = cooldown * (0.85f + lv.rng.f() * 0.4f); }
                break;
            }
            case HURT:
                vx = Mth.approach(vx, 0, 400 * dt); vy = Mth.approach(vy, 0, 400 * dt);
                lv.move(this, dt);
                if (stateT > 0.26f) { state = CHASE; animName = "idle"; }
                break;
            default:
                lv.move(this, dt);
                if (stateT > 0.2f) state = CHASE;
                break;
        }
    }

    private void flyDiveAI(Level lv, float dt, Player p, float dx, float dy, float dist, float sp) {
        bob += dt * 3f;
        switch (state) {
            case PATROL:
                animName = "walk";
                flyMove(lv, dt, home + (float) Math.sin(bob * 0.4f) * 50, y + (float) Math.sin(bob) * 2, sp * 0.4f, 300);
                return;
            case CHASE: {
                face(dx);
                animName = "walk";
                float gx = p.x + (float) Math.sin(bob * 0.7f) * 70, gy = p.y - 78 + (float) Math.sin(bob) * 8;
                flyMove(lv, dt, gx, gy, sp, 520);
                if (atkCd <= 0 && dist < def.range + 60) { startState(WINDUP, "windup"); tx = p.x; ty = p.cy(); }
                break;
            }
            case WINDUP:
                face(dx);
                vx = Mth.approach(vx, 0, 800 * dt); vy = Mth.approach(vy, -30, 800 * dt);
                if (stateT < 0.25f) { tx = p.x; ty = p.cy(); }
                lv.move(this, dt);
                if (stateT > 0.5f) {
                    startState(DIVE, "attack");
                    float ddx = tx - x, ddy = ty - cy();
                    float d = (float) Math.sqrt(ddx * ddx + ddy * ddy) + 0.01f;
                    vx = ddx / d * 235f; vy = ddy / d * 235f;
                    right = vx >= 0;
                    Snd.sfxAt("en_dash", x, lv.camX + lv.viewW / 2, 0.6f);
                }
                break;
            case DIVE:
                lv.move(this, dt);
                if (stateT > 0.55f || hitWall || onGround) { state = RECOVER; stateT = 0; animName = "walk"; atkCd = cooldown * (0.9f + lv.rng.f() * 0.4f); }
                break;
            case RECOVER:
                animName = "walk";
                flyMove(lv, dt, x, y - 60, sp, 500);
                if (stateT > 0.5f) state = CHASE;
                break;
            case HURT:
                vx = Mth.approach(vx, 0, 400 * dt); vy = Mth.approach(vy, 0, 400 * dt);
                lv.move(this, dt);
                if (stateT > 0.26f) { state = CHASE; animName = "walk"; }
                break;
            default: state = CHASE; break;
        }
    }

    // ------------------------------------------------------------------ embestida
    private void chargerAI(Level lv, float dt, Player p, float dx, float dy, float sp) {
        switch (state) {
            case PATROL: patrol(lv, dt, sp); return;
            case CHASE: {
                face(dx);
                if (Math.abs(dx) > 50 && groundAhead(lv, Mth.sign(dx))) { vx = Mth.approach(vx, Mth.sign(dx) * sp, 900 * dt); animName = "walk"; }
                else { vx = Mth.approach(vx, 0, 900 * dt); animName = "idle"; }
                if (Math.abs(dx) < def.range && Math.abs(dy) < 36 && atkCd <= 0) { startState(WINDUP, "windup"); vx = 0; Snd.sfxAt("en_alert", x, lv.camX + lv.viewW / 2, 0.5f); }
                break;
            }
            case WINDUP:
                vx = 0;
                if (stateT < 0.3f) face(dx);
                if (finishedAnim() && stateT > 0.5f) { startState(CHARGE, "attack"); Snd.sfxAt("en_dash", x, lv.camX + lv.viewW / 2, 0.7f); }
                break;
            case CHARGE: {
                vx = (right ? 1 : -1) * speed * 4.6f * speedMul();
                Anim a = sheet.anim("attack");
                if (animT * a.fps >= a.n) animT = a.n * 0.5f / a.fps;   // mantiene la pose de carga
                if ((int) (stateT * 20) % 2 == 0) lv.ps.spawn(x - (right ? 8 : -8), y - 3, 0, -10, 0.3f, 3, 0, 0xB0A090, false);
                if (stateT > 0.75f || hitWall || !groundAhead(lv, right ? 1 : -1)) {
                    if (hitWall) { lv.shake(3f, 0.2f); Snd.sfxAt("hit_stone", x, lv.camX + lv.viewW / 2, 0.8f); stateT = 0; state = RECOVER; animName = "hurt"; animT = 0; stun = 0; atkCd = cooldown; vx = 0; }
                    else { state = RECOVER; stateT = 0; animName = "idle"; atkCd = cooldown; }
                }
                break;
            }
            case RECOVER:
                vx = Mth.approach(vx, 0, 1400 * dt);
                if (stateT > 0.6f) { state = CHASE; animName = "idle"; }
                break;
            case HURT:
                vx = Mth.approach(vx, 0, 500 * dt);
                if (stateT > 0.26f) { state = CHASE; animName = "idle"; }
                break;
            default: state = CHASE; break;
        }
        vy = Math.min(Level.FALL_MAX, vy + Level.GRAV * dt);
        lv.move(this, dt);
    }

    // ------------------------------------------------------------------ saltarin
    private void jumperAI(Level lv, float dt, Player p, float dx, float dy, float sp) {
        switch (state) {
            case PATROL: patrol(lv, dt, sp); return;
            case CHASE: {
                if (onGround) {
                    vx = Mth.approach(vx, 0, 1400 * dt);
                    animName = "idle";
                    face(dx);
                    if (atkCd <= 0) {
                        startState(WINDUP, "windup"); vx = 0;
                    }
                }
                break;
            }
            case WINDUP:
                vx = 0;
                face(dx);
                if (finishedAnim() || stateT > 0.35f) {
                    startState(ATTACK, "attack");
                    vy = -270f - Math.min(60f, Math.max(0, -dy) * 0.6f);
                    vx = (right ? 1 : -1) * Math.min(sp * 1.9f, Math.max(60f, Math.abs(dx) * 1.3f));
                    onGround = false;
                    Snd.sfxAt("en_dash", x, lv.camX + lv.viewW / 2, 0.4f);
                }
                break;
            case ATTACK:
                if (animT * sheet.anim("attack").fps >= sheet.anim("attack").n) animT = (sheet.anim("attack").n - 1) / sheet.anim("attack").fps;
                if (onGround && stateT > 0.1f) { state = CHASE; stateT = 0; animName = "idle"; atkCd = cooldown * (0.7f + lv.rng.f() * 0.4f); vx = 0; }
                break;
            case HURT:
                vx = Mth.approach(vx, 0, 500 * dt);
                if (stateT > 0.26f) { state = CHASE; animName = "idle"; }
                break;
            default: state = CHASE; break;
        }
        vy = Math.min(Level.FALL_MAX, vy + Level.GRAV * dt);
        lv.move(this, dt);
    }


    // ------------------------------------------------------------------ nuevos arquetipos
    private boolean groundBehind(Level lv, float px, float py) {
        int t = lv.room.tile((int) Math.floor(px / Room.TS), (int) Math.floor((py + 4) / Room.TS));
        return Room.isSolid(t) || t == Room.ONEWAY;
    }

    private void gravityMove(Level lv, float dt) {
        if (!flying) vy = Math.min(Level.FALL_MAX, vy + Level.GRAV * dt);
        lv.move(this, dt);
    }

    /** Explosion del carbonero: dana al jugador y, como fuego amigo, a los enemigos (y rompe muros fragiles). */
    private void blast(Level lv, float mul, float r) {
        lv.explosion(x, y - 10, r, dmgNow() * mul, 200, Ent.BURN, 3f, 5f, false);
        lv.explosion(x, y - 10, r, 26f * mul, 140, -1, 0, 0, true);
        lv.fxAdd("fx_explosion", "a", x, y - 10, 0.5f + r / 90f, 0xFFB060);
        Snd.sfxAt("explosion_small", x, lv.camX + lv.viewW / 2, 0.8f);
        lv.shake(2.5f, 0.2f);
    }

    // ---- apoyo: clerigo (cura) y cultista (furia)
    private Enemy findWounded(Level lv) {
        Enemy best = null; float low = 0.7f;
        for (Enemy o : lv.enemies) {
            if (o == this || !o.alive || o.untargetable() || Math.abs(o.x - x) > 250 || Math.abs(o.y - y) > 90) continue;
            float r = o.hp / o.maxHp;
            if (r < low) { low = r; best = o; }
        }
        return best;
    }

    private int buffCandidates(Level lv) {
        int n = 0;
        for (Enemy o : lv.enemies) if (o != this && o.alive && o.def.role != EnemyDef.BUFFER && o.buffT < 1.5f && Math.abs(o.x - x) < 240 && Math.abs(o.y - y) < 90) n++;
        return n;
    }

    private boolean supportReady(Level lv) {
        if (def.role == EnemyDef.SUPPORT) { healTgt = findWounded(lv); return healTgt != null; }
        healTgt = null;
        return buffCandidates(lv) > 0;
    }

    private void supportCast(Level lv, Player p) {
        if (def.role == EnemyDef.SUPPORT && healTgt != null && healTgt.alive) {
            float h = healTgt.maxHp * 0.35f;
            healTgt.hp = Math.min(healTgt.maxHp, healTgt.hp + h);
            lv.text(healTgt.x, healTgt.y - healTgt.bh - 8, "+" + Math.round(h), 0x6AE08A, false);
            lv.fx("fx_heal", "rise", healTgt.x, healTgt.y - 12, 1f, 0, 0);
            lv.fxAdd("fx_ring", "pulse", healTgt.x, healTgt.y - healTgt.bh / 2, 0.6f, def.color);
            link(lv, healTgt, def.color);
            Snd.sfxAt("heal", x, lv.camX + lv.viewW / 2, 0.6f);
            healTgt = null;
        } else if (def.role == EnemyDef.BUFFER && buffCandidates(lv) > 0) {
            for (Enemy o : lv.enemies) {
                if (o == this || !o.alive || o.def.role == EnemyDef.BUFFER || Math.abs(o.x - x) > 240 || Math.abs(o.y - y) > 90) continue;
                o.buffT = 7f;
                lv.fxAdd("fx_ring", "pulse", o.x, o.y - o.bh / 2, 0.55f, def.color);
                lv.text(o.x, o.y - o.bh - 8, "¡Furia!", 0xFF6A7C, false);
                link(lv, o, def.color);
            }
            Snd.sfxAt("en_cast", x, lv.camX + lv.viewW / 2, 0.7f);
        } else fire(lv, p);
        lv.fxAdd("fx_hit", "magic", x + (right ? 8 : -8), y - bh * 0.7f, 0.8f, def.color);
    }

    private void link(Level lv, Enemy o, int color) {
        float x1 = x, y1 = y - bh * 0.7f, x2 = o.x, y2 = o.y - o.bh * 0.5f;
        lv.lines.add(new float[]{x1, y1, x2, y2, 0.3f, color});
    }

    private void supportAI(Level lv, float dt, Player p, float dx, float dy, float dist, float sp) {
        switch (state) {
            case PATROL: patrol(lv, dt, sp); return;
            case CHASE: {
                face(dx);
                float ad = Math.abs(dx);
                if (ad < 120 && groundAhead(lv, -Mth.sign(dx)) && !hitWall) { vx = Mth.approach(vx, -Mth.sign(dx) * sp * 1.15f, 900 * dt); animName = "walk"; }
                else if (ad > 230 && groundAhead(lv, Mth.sign(dx))) { vx = Mth.approach(vx, Mth.sign(dx) * sp * 0.8f, 900 * dt); animName = "walk"; }
                else { vx = Mth.approach(vx, 0, 900 * dt); animName = "idle"; }
                if (atkCd <= 0 && (supportReady(lv) || (ad < def.range && Math.abs(dy) < 120))) { startState(WINDUP, "windup"); vx = 0; }
                break;
            }
            case WINDUP:
                vx = Mth.approach(vx, 0, 900 * dt);
                if (healTgt != null && healTgt.alive) face(healTgt.x - x); else face(dx);
                if (finishedAnim()) startState(ATTACK, "attack");
                break;
            case ATTACK: {
                Anim a = sheet.anim("attack");
                vx = Mth.approach(vx, 0, 900 * dt);
                int rel = Math.max(1, a.h0 >= 0 ? a.h0 : a.n / 2);
                if (!shot && a.frameAt(animT) >= rel) { shot = true; supportCast(lv, p); }
                if (a.done(animT)) { state = RECOVER; stateT = 0; animName = "idle"; atkCd = cooldown * (0.85f + lv.rng.f() * 0.4f); }
                break;
            }
            case RECOVER:
                if (stateT > 0.2f) state = CHASE;
                break;
            case HURT:
                vx = Mth.approach(vx, 0, 500 * dt);
                if (stateT > 0.26f) { state = CHASE; animName = "idle"; }
                break;
            default: state = CHASE; break;
        }
        gravityMove(lv, dt);
    }

    // ---- carbonero: corre, enciende la mecha y estalla
    private void exploderAI(Level lv, float dt, Player p, float dx, float dy, float sp) {
        switch (state) {
            case PATROL: patrol(lv, dt, sp); return;
            case CHASE: {
                face(dx);
                if (Math.abs(dx) > 30 && groundAhead(lv, Mth.sign(dx))) { vx = Mth.approach(vx, Mth.sign(dx) * sp * 1.55f, 1100 * dt); animName = "walk"; }
                else { vx = Mth.approach(vx, 0, 1100 * dt); animName = "idle"; }
                if (hitWall && p.y < y - 24 && onGround) vy = -300;
                if (Math.abs(dx) < 50 && Math.abs(dy) < 36 && atkCd <= 0) { startState(FUSE, "windup"); vx = 0; Snd.sfxAt("en_alert", x, lv.camX + lv.viewW / 2, 0.6f); }
                break;
            }
            case FUSE: {
                vx = Mth.approach(vx, 0, 1400 * dt);
                if ((int) (stateT * 30) % 3 == 0) lv.ps.spawn(x + (right ? 6 : -6), y - bh + 4, lv.rng.f(-20, 20), -lv.rng.f(30, 70), 0.3f, 2, 0, 0xFFD25A, true);
                if (stateT >= 0.9f) {
                    blast(lv, 1.4f, 50);
                    suicide = true;
                    hp = 0;
                    die(lv);
                    return;
                }
                break;
            }
            case HURT:
                vx = Mth.approach(vx, 0, 500 * dt);
                if (stateT > 0.2f) { state = CHASE; animName = "idle"; }
                break;
            default: state = CHASE; break;
        }
        gravityMove(lv, dt);
    }

    // ---- torreta de cristal: inmovil, abanico de esquirlas; solo es vulnerable al cargar y disparar
    private void turretAI(Level lv, float dt, Player p, float dx, float dy, float dist) {
        vx = 0;
        switch (state) {
            case PATROL: animName = "idle"; break;
            case CHASE:
                face(dx);
                animName = "idle";
                if (dist < def.range && Math.abs(dy) < 160 && atkCd <= 0) startState(WINDUP, "windup");
                break;
            case WINDUP:
                if (stateT < 0.3f) face(dx);
                if (finishedAnim() && stateT > 0.55f) startState(ATTACK, "attack");
                break;
            case ATTACK: {
                Anim a = sheet.anim("attack");
                int rel = Math.max(1, a.h0 >= 0 ? a.h0 : a.n / 2);
                if (!shot && a.frameAt(animT) >= rel) {
                    shot = true;
                    int n = elite ? 5 : 3;
                    float mx = x + (right ? 8 : -8) * scale, my = y - bh * 0.6f;
                    float base = (float) Math.atan2(p.cy() - my, p.x - mx);
                    for (int i = 0; i < n; i++) {
                        float ang = base + (i - (n - 1) / 2f) * 0.3f;
                        Proj pr = lv.proj(mx, my, (float) Math.cos(ang) * 150f, (float) Math.sin(ang) * 150f, dmgNow(), false, def.proj, def.color);
                        pr.status = statusId; pr.statusDur = 2.5f; pr.life = 3.2f; pr.radius = 5;
                    }
                    Snd.sfxAt("en_cast", x, lv.camX + lv.viewW / 2, 0.6f);
                    lv.fxAdd("fx_hit", "ice", mx, my, 0.9f, def.color);
                }
                if (a.done(animT)) { state = RECOVER; stateT = 0; animName = "idle"; atkCd = cooldown * (0.9f + lv.rng.f() * 0.3f); }
                break;
            }
            case RECOVER:
                if (stateT > 0.5f) state = CHASE;
                break;
            case HURT:
                if (stateT > 0.2f) { state = CHASE; animName = "idle"; }
                break;
            default: state = CHASE; break;
        }
        gravityMove(lv, dt);
    }

    // ---- lobo: acecha, se agazapa (aviso) y salta con un mordisco
    private void pouncerAI(Level lv, float dt, Player p, float dx, float dy, float sp) {
        switch (state) {
            case PATROL: patrol(lv, dt, sp); return;
            case CHASE: {
                face(dx);
                float ad = Math.abs(dx);
                if (ad > 130 && groundAhead(lv, Mth.sign(dx))) { vx = Mth.approach(vx, Mth.sign(dx) * sp * 1.3f, 1100 * dt); animName = "walk"; }
                else if (ad < 70 && groundAhead(lv, -Mth.sign(dx)) && !hitWall) { vx = Mth.approach(vx, -Mth.sign(dx) * sp * 0.7f, 1100 * dt); animName = "walk"; }
                else { vx = Mth.approach(vx, 0, 1100 * dt); animName = "idle"; }
                if (hitWall && p.y < y - 24 && onGround) vy = -300;
                if (ad < 160 && ad > 36 && Math.abs(dy) < 56 && atkCd <= 0 && onGround) { startState(WINDUP, "windup"); vx = 0; Snd.sfxAt("en_alert", x, lv.camX + lv.viewW / 2, 0.5f); }
                break;
            }
            case WINDUP:
                vx = Mth.approach(vx, 0, 1400 * dt);
                if (stateT < 0.25f) face(dx);
                if (finishedAnim() && stateT > 0.42f) {
                    startState(LEAP, "attack");
                    vy = -205f;
                    vx = (right ? 1 : -1) * Math.min(320f, Math.max(200f, Math.abs(dx) * 2.4f));
                    onGround = false;
                    Snd.sfxAt("en_dash", x, lv.camX + lv.viewW / 2, 0.6f);
                }
                break;
            case LEAP: {
                Anim a = sheet.anim("attack");
                if (animT * a.fps >= a.n) animT = (a.n - 1) / a.fps;
                if (!hitDone && p.alive && overlaps(p.x - p.bw / 2, p.y - p.bh, p.bw, p.bh)) { hitDone = true; lv.hurtPlayer(dmgNow(), x, statusId, 3f); }
                if ((onGround && stateT > 0.12f) || hitWall) { state = RECOVER; stateT = 0; animName = "idle"; atkCd = cooldown * (0.8f + lv.rng.f() * 0.4f); vx *= 0.2f; }
                break;
            }
            case RECOVER:
                vx = Mth.approach(vx, 0, 1400 * dt);
                if (stateT > 0.5f) state = CHASE;
                break;
            case HURT:
                vx = Mth.approach(vx, 0, 500 * dt);
                if (stateT > 0.24f) { state = CHASE; animName = "idle"; }
                break;
            default: state = CHASE; break;
        }
        gravityMove(lv, dt);
    }

    // ---- tirador de rayo: apunta con una linea visible, la fija y dispara un rayo veloz
    private void sniperAI(Level lv, float dt, Player p, float dx, float dy, float dist, float sp) {
        float mx = x + (right ? 14 : -14) * scale, my = y - bh * 0.62f;
        switch (state) {
            case PATROL: patrol(lv, dt, sp); return;
            case CHASE: {
                face(dx);
                float ad = Math.abs(dx);
                if (ad < 130 && groundAhead(lv, -Mth.sign(dx)) && !hitWall) { vx = Mth.approach(vx, -Mth.sign(dx) * sp * 1.2f, 900 * dt); animName = "walk"; }
                else if (ad > def.range * 0.9f && groundAhead(lv, Mth.sign(dx))) { vx = Mth.approach(vx, Mth.sign(dx) * sp, 900 * dt); animName = "walk"; }
                else { vx = Mth.approach(vx, 0, 900 * dt); animName = "idle"; }
                if (ad < def.range && ad > 60 && Math.abs(dy) < 150 && atkCd <= 0) { startState(AIM, "windup"); vx = 0; aimX = p.x; aimY = p.cy(); shot = false; }
                break;
            }
            case AIM: {
                vx = Mth.approach(vx, 0, 1200 * dt);
                boolean locked = stateT >= 0.8f;
                if (!locked) { aimX = p.x; aimY = p.cy(); face(dx); }
                float ang = (float) Math.atan2(aimY - my, aimX - mx);
                lv.lines.add(new float[]{mx, my, mx + (float) Math.cos(ang) * 440f, my + (float) Math.sin(ang) * 440f, 0.05f, locked ? 0xFF4040 : 0x6AB8FF});
                if (stateT >= 1.2f) {
                    startState(ATTACK, "attack");
                    Proj pr = lv.proj(mx, my, (float) Math.cos(ang) * 540f, (float) Math.sin(ang) * 540f, dmgNow() * 1.5f, false, "bolt", def.color);
                    pr.life = 1.1f; pr.radius = 4; pr.trail = true;
                    shot = true;
                    Snd.sfxAt("hit_shock", x, lv.camX + lv.viewW / 2, 0.7f);
                    lv.fxAdd("fx_hit", "shock", mx, my, 0.9f, def.color);
                }
                break;
            }
            case ATTACK: {
                Anim a = sheet.anim("attack");
                vx = Mth.approach(vx, 0, 900 * dt);
                if (a.done(animT)) { state = RECOVER; stateT = 0; animName = "idle"; atkCd = cooldown * (0.9f + lv.rng.f() * 0.4f); }
                break;
            }
            case RECOVER:
                if (stateT > 0.3f) state = CHASE;
                break;
            case HURT:
                vx = Mth.approach(vx, 0, 500 * dt);
                if (stateT > 0.26f) { state = CHASE; animName = "idle"; }
                break;
            default: state = CHASE; break;
        }
        gravityMove(lv, dt);
    }

    // ---- asesino: se desvanece, marca el sitio donde reaparecera (a la espalda del jugador) y ataca
    private void blinkerAI(Level lv, float dt, Player p, float dx, float dy, float dist, float sp) {
        switch (state) {
            case PATROL: patrol(lv, dt, sp); return;
            case CHASE: {
                face(dx);
                if (Math.abs(dx) > 60 && groundAhead(lv, Mth.sign(dx))) { vx = Mth.approach(vx, Mth.sign(dx) * sp * 1.1f, 900 * dt); animName = "walk"; }
                else { vx = Mth.approach(vx, 0, 900 * dt); animName = "idle"; }
                if (dist < 200 && Math.abs(dy) < 90 && atkCd <= 0 && p.onGround) {
                    startState(VANISH, "idle");
                    float bx = p.x - p.dir() * 30;
                    if (lv.solidAtPx(bx, p.y - 8) || !groundBehind(lv, bx, p.y)) bx = p.x + p.dir() * 30;
                    if (lv.solidAtPx(bx, p.y - 8) || !groundBehind(lv, bx, p.y)) bx = p.x;
                    tx = bx; ty = p.y;
                    lv.fxAdd("fx_ring", "pulse", tx, ty - 3, 0.8f, def.color);
                    lv.fxAdd("fx_tele", "a", tx, ty - 14, 0.8f, def.color);
                    Snd.sfxAt("en_alert", x, lv.camX + lv.viewW / 2, 0.5f);
                    lv.ps.burst(lv.rng, x, y - bh / 2, def.color, 10, 80, 0.4f, 2, 0, true);
                }
                break;
            }
            case VANISH:
                vx = 0; vy = 0;
                if (stateT >= 0.7f) {
                    x = tx; y = ty; vx = vy = 0;
                    right = p.x >= x;
                    startState(WINDUP, "windup");
                    lv.ps.burst(lv.rng, x, y - bh / 2, def.color, 14, 110, 0.4f, 2, 0, true);
                    lv.fxAdd("fx_ring", "pulse", x, y - bh / 2, 0.6f, def.color);
                }
                return;
            default:
                meleeAI(lv, dt, p, dx, dy, sp);
                return;
        }
        gravityMove(lv, dt);
    }

    // ------------------------------------------------------------------ dibujo
    private float hpShow = -1;
    public void render(Platform.Gfx g, Level lv) {
        if (spawnT < 0) return;
        Anim a = sheet.anim(animName);
        int frame = a.frameAt(animT);
        int flags = 0, tint = Status.tint(this);
        if (tint != 0) flags |= Platform.TINT;
        float alpha = 1f;
        if (!alive) alpha = Mth.clamp((2.1f - deadT) / 0.6f, 0f, 1f);
        if (state == VANISH && alive) alpha = Mth.clamp(1f - stateT / 0.28f, 0f, 1f);
        if (alpha <= 0.01f) return;
        if (hitFlash > 0) { flags |= Platform.FLASH; tint = 0xFFFFFF; }
        if (buffT > 0 && alive) UI.light(g, x, y - bh / 2, 26, 0xFF3050, 0.30f + 0.10f * (float) Math.sin(lv.time * 9));
        if (state == FUSE && alive) { flags |= Platform.TINT; if (hitFlash <= 0) tint = ((int) (lv.time * 16) & 1) == 0 ? 0xFF6040 : 0xFFFFFF; }
        if (alive && !flying) g.rect(Math.round(x - 7 * scale), Math.round(y - 1), Math.round(14 * scale), 2, 0x55000000, false);
        if (elite && alive) UI.light(g, x, y - bh / 2, 34, 0xFFC040, 0.32f + 0.08f * (float) Math.sin(lv.time * 6));
        if ((state == WINDUP || state == AIM || state == FUSE) && alive && (def.role == EnemyDef.CHARGER || def.role == EnemyDef.EXPLODER || def.role == EnemyDef.SNIPER || def.role == EnemyDef.POUNCER || def.role == EnemyDef.TURRET || def.role == EnemyDef.FLY_DIVE || def.role == EnemyDef.HEAVY)) {
            flags |= Platform.TINT; if (hitFlash <= 0) tint = ((int) (lv.time * 14) & 1) == 0 ? 0xFFB0A0 : 0xFFFFFF;
        }
        float dy = (def.role == EnemyDef.FLY_SHOOT || def.role == EnemyDef.FLY_DIVE) && alive ? (float) Math.sin(bob) * 1.5f : 0;
        sheet.draw(g, a, frame, x, y + dy, right, scale, flags, tint, alpha);
        if (alive) {
            if ((state == WINDUP || state == AIM || state == FUSE) && UI.big != null) UI.big.center(g, "!", x, y - bh - 16, 0xFF4040, 1f);
            {
                if (hpShow < 0) hpShow = maxHp;
                hpShow += (hp - hpShow) * 0.1f;
                float w = Math.max(18, bw * 1.5f);
                float bx = Math.round(x - w / 2), by = Math.round(y - bh - 8);
                g.rect(bx - 1, by - 1, w + 2, 5, 0xDD000000, false);
                g.rect(bx, by, w * Mth.clamp(hpShow / maxHp, 0, 1), 3, 0xFFF0E8E0, false);
                g.rect(bx, by, w * Mth.clamp(hp / maxHp, 0, 1), 3, elite ? 0xFFFFC040 : (hp / maxHp < 0.3f ? 0xFFFF4040 : 0xFFE04848), false);
                g.rect(bx, by, w * Mth.clamp(hp / maxHp, 0, 1), 1, 0x55FFFFFF, false);
            }
        }
    }
}
