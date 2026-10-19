package com.julianfarks.roguelike.core;

/** Enemigo normal o elite. La IA depende del rol definido en EnemyDef. */
public final class Enemy extends Ent {
    static final int PATROL = 0, CHASE = 1, WINDUP = 2, ATTACK = 3, RECOVER = 4, HURT = 5, DEAD = 6, CHARGE = 7, DIVE = 8, AIM = 9, VANISH = 10, FUSE = 11, LEAP = 12;

    public final EnemyDef def;
    public final boolean elite;
    public float home;
    public boolean remove;
    public boolean guardian;   // guardian opcional de una camara secreta: no cuenta para despejar la sala
    public boolean optional;   // encuentro opcional de una mazmorra vertical (subsuelo profundo, torre, alcoba): no cuenta para despejar la sala
    public int state = PATROL;
    private float stateT, atkCd, deadT, patrolDir = 1, patrolWait, contactCd, bob, spawnT;
    private boolean aggro, shot, hitDone;
    private final float dmg, speed;
    private final int statusId;
    private float tx, ty;           // objetivo de embestida / picada
    private final float cooldown;
    float modSpeed = 1f;            // reto 'enemigos veloces'
    float buffT;                    // aura de furia (cultista): +35% daño, +20% velocidad
    private Enemy healTgt;
    private boolean suicide, blocked;
    private float aimX, aimY;
    float trapCd, prevY = Float.NaN;
    private int atk, atkCount;
    private final float[] eX = new float[3];
    private int eN;

    public Enemy(EnemyDef d, boolean elite, float hpMul, float dmgMul) {
        this.def = d;
        boolean uniq = d.elite;
        elite = elite || uniq;
        this.elite = elite;
        sheet = Assets.sheet(d.sheet);
        scale = (elite && !uniq) ? 1.22f : 1f;
        bw = sheet.bw * scale;
        bh = sheet.bh * scale;
        maxHp = hp = d.hp * hpMul * ((elite && !uniq) ? 2.6f : 1f);
        dmg = d.dmg * dmgMul * ((elite && !uniq) ? 1.3f : 1f);
        speed = d.speed * ((elite && !uniq) ? 1.15f : 1f);
        cooldown = d.cooldown * ((elite && !uniq) ? 0.8f : 1f);
        flying = d.role == EnemyDef.FLY_SHOOT || d.role == EnemyDef.FLY_DIVE || d.id.equals("ventisca");
        gravity = !flying;
        statusId = Status.parse(d.status);
        right = Math.random() < 0.5;
        patrolDir = right ? 1 : -1;
        bob = (float) (Math.random() * 6.28);
        atkCd = 0.6f + (float) Math.random();
        spawnT = 0.0f;
    }

    /** Resistencias a los estados de las armas secundarias: las criaturas de fuego no arden, los huesos y espectros no sangran ni se envenenan, etc. */
    @Override public float statusResist(int s) {
        String st = def.status, die = def.dieSfx;
        boolean bone = die.contains("bone"), ghost = die.contains("ghost"), slime = die.contains("slime");
        switch (s) {
            case Ent.BURN: return st.equals("burn") ? 0f : 1f;
            case Ent.SLOW: case Ent.FREEZE: return st.equals("slow") ? 0.35f : 1f;
            case Ent.POISON: return st.equals("poison") || bone || ghost ? 0f : 1f;
            case Ent.BLEED: return bone || ghost || slime ? 0f : 1f;
            case Ent.SHOCK: return st.equals("shock") ? 0.35f : 1f;
            default: return 1f;
        }
    }

    @Override public int stackCap(int max) { return elite ? Math.min(max, 3) : max; }

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
    float hurtDur = 0.26f, hurtFric = 500f;      // duracion de la reaccion al golpe y friccion calculada para frenar justo al terminar (sin deslizarse)

    public void onHit(Level lv, float kx, float ky, float dmgTaken) {
        aggro = true;
        if (kx == 0 && ky == 0) return;
        if (blocked) { vx += kx * 0.12f; blocked = false; return; }
        if (def.role == EnemyDef.TURRET) { if (state != WINDUP && state != ATTACK) { state = HURT; stateT = 0; animName = "hurt"; animT = 0; } return; }
        float resist = def.role == EnemyDef.HEAVY || def.role == EnemyDef.SHIELD ? 0.45f : (def.role == EnemyDef.CHARGER ? 0.55f : 1f);
        if (elite) resist *= 0.6f;
        int hk = lv.hitKind;
        float kmul = hk == Impact.HEAVY ? 1.25f : hk == Impact.CRIT ? 1.1f : hk == Impact.LIGHT ? 0.9f : 1f;
        hurtDur = hk == Impact.HEAVY ? 0.38f : hk == Impact.CRIT ? 0.30f : hk == Impact.LIGHT ? 0.22f : 0.26f;
        if (!flying) vx = kx * resist * kmul; else { vx = kx * resist * 0.8f * kmul; }
        if (ky != 0) vy = flying ? ky * 0.5f : Math.min(0, ky) * resist;
        hurtFric = Math.max(400f, Math.abs(vx) / (hurtDur * 0.8f));
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
        if (!guardian && !optional) lv.toKill--;
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
            if (dotAcc >= 2f) { int d = (int) dotAcc; dotAcc -= d; int pv = lv.dmgSrc; lv.dmgSrc = BlessFx.SRC_DOT; try { lv.damageEnemy(this, d, false, 0, 0); } finally { lv.dmgSrc = pv; } if (!alive) return; }
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

        float sp = speed * modSpeed * speedMul() * (buffT > 0 ? 1.2f : 1f);
        switch (def.role) {
            case EnemyDef.MELEE: case EnemyDef.HEAVY: case EnemyDef.SHIELD: meleeAI(lv, dt, p, dx, dy, sp); break;
            case EnemyDef.SUPPORT: case EnemyDef.BUFFER: supportAI(lv, dt, p, dx, dy, dist, sp); break;
            case EnemyDef.EXPLODER: exploderAI(lv, dt, p, dx, dy, sp); break;
            case EnemyDef.TURRET: turretAI(lv, dt, p, dx, dy, dist); break;
            case EnemyDef.POUNCER: pouncerAI(lv, dt, p, dx, dy, sp); break;
            case EnemyDef.SNIPER: sniperAI(lv, dt, p, dx, dy, dist, sp); break;
            case EnemyDef.BLINKER: blinkerAI(lv, dt, p, dx, dy, dist, sp); break;
            case EnemyDef.ELITE: eliteAI(lv, dt, p, dx, dy, dist, sp); break;
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

    /**
     * Camino seguro por delante: hay suelo bajo el siguiente paso Y no hay pinchos en las filas del cuerpo dentro del alcance de frenado.
     * Todas las IA de suelo ya condicionaban su avance a esta funcion (borde de plataforma), asi que ahora tambien frenan ante los pinchos.
     * El alcance crece con la velocidad (v^2 / 2a con a ~ 1200 px/s^2) para que las embestidas y saltos de elite tampoco lleguen a tocarlos.
     */
    private boolean groundAhead(Level lv, float dir) {
        float fx = x + dir * (bw / 2 + 5);
        int t = lv.room.tile((int) Math.floor(fx / Room.TS), (int) Math.floor((y + 4) / Room.TS));
        if (!(Room.isSolid(t) || t == Room.ONEWAY)) return false;
        if (flying) return true;
        float reach = 8f + (vx * dir > 0 ? vx * vx / 2400f : 0f);
        return !hazardAhead(lv, dir, reach);
    }

    /** Pinchos en las filas que ocupa el cuerpo, entre el borde delantero y `reach` px mas alla. Si ya esta sobre pinchos no bloquea (puede salir). */
    private boolean hazardAhead(Level lv, float dir, float reach) {
        Room r = lv.room;
        int r0 = (int) Math.floor((y - bh + 1) / Room.TS), r1 = (int) Math.floor((y - 1) / Room.TS);
        for (int ty = r0; ty <= r1; ty++) if (EnemyNav.hazard(r.tile((int) Math.floor(x / Room.TS), ty))) return false;
        float hw = bw / 2;
        for (float d = 0; d <= reach; d += 4f) {
            int tx = (int) Math.floor((x + dir * (hw + d)) / Room.TS);
            for (int ty = r0; ty <= r1; ty++) if (EnemyNav.hazard(r.tile(tx, ty))) return true;
        }
        return false;
    }

    /** Hay pinchos entre el enemigo y la coordenada px (a la altura de su cuerpo), como mucho a 220 px. */
    private boolean hazardBetween(Level lv, float px) {
        float dir = Mth.sign(px - x);
        if (dir == 0) return false;
        float dist = Math.min(220f, Math.abs(px - x));
        Room r = lv.room;
        int r0 = (int) Math.floor((y - bh + 1) / Room.TS), r1 = (int) Math.floor((y - 1) / Room.TS);
        for (float d = 0; d <= dist; d += 4f) {
            int tx = (int) Math.floor((x + dir * d) / Room.TS);
            for (int ty = r0; ty <= r1; ty++) if (EnemyNav.hazard(r.tile(tx, ty))) return true;
        }
        return false;
    }

    /**
     * Simula un salto/embestida aerea con las leyes reales de movimiento y devuelve false si en algun punto el cuerpo tocaria pinchos
     * (mismos puntos de contacto que Level.trapDamage) o si aterriza sobre ellos. Se usa para no lanzar saltos que acaban en una trampa.
     */
    private boolean trajectorySafe(Level lv, float vx0, float vy0) {
        Room r = lv.room;
        float px = x, py = y, pvx = vx0, pvy = vy0, hw = Math.max(2f, bw * 0.4f), dt = 1f / 60f;
        for (int i = 0; i < 90; i++) {
            pvy = Math.min(Level.FALL_MAX, pvy + Level.GRAV * dt);
            float nx = px + pvx * dt, ny = py + pvy * dt;
            float edge = nx + (pvx > 0 ? bw / 2 : -bw / 2);
            if (pvx != 0 && Room.isSolid(r.tile((int) Math.floor(edge / Room.TS), (int) Math.floor((py - bh * 0.5f) / Room.TS)))) { nx = px; pvx = 0; }
            if (pvy > 0) {
                int tx = (int) Math.floor(nx / Room.TS), ty = (int) Math.floor(ny / Room.TS);
                int t = r.tile(tx, ty);
                if ((Room.isSolid(t) || t == Room.ONEWAY) && ny >= ty * Room.TS) {
                    float gy = ty * Room.TS;
                    for (int k = -1; k <= 1; k++) if (r.hazardAt(nx + k * hw, gy - 4) || r.hazardAt(nx + k * hw, gy - bh * 0.5f)) return false;
                    return true;
                }
            }
            px = nx; py = ny;
            for (int k = -1; k <= 1; k++) if (r.hazardAt(px + k * hw, py - 4) || r.hazardAt(px + k * hw, py - bh * 0.5f)) return false;
        }
        return true;
    }

    /** Escala vx0 hasta que la trayectoria sea segura (1, .75, .5, .3). Devuelve la escala o 0 si ninguna lo es (cancelar el salto). */
    private float safeLeapScale(Level lv, float vx0, float vy0) {
        float[] ks = {1f, 0.75f, 0.5f, 0.3f};
        for (float k : ks) if (trajectorySafe(lv, vx0 * k, vy0)) return k;
        return 0f;
    }

    // ------------------------------------------------------------------ navegacion segura (ver EnemyNav)
    /** Contadores para las pruebas de IA/rendimiento. */
    public static int dbgPlans, dbgHops, dbgBlocked;
    private boolean navActive, navOk, navWait;
    private float navT, navTime, navFlipT, hopT, hopVx;
    private int navDir, navType;

    String dbgNav() { return "nav=" + navActive + "/" + navOk + "/" + navWait + " type=" + navType + " dir=" + navDir + " hopT=" + hopT + " bw=" + bw; }
    private boolean canHop() { return def.role == EnemyDef.MELEE || def.role == EnemyDef.EXPLODER || def.role == EnemyDef.POUNCER; }
    private float hopSpeed(float sp) { return Math.min(sp * 1.8f, 150f); }

    /** true mientras dura un salto de la navegacion: la IA no debe tocar vx (si no, frenaria en el aire y caeria en los pinchos). */
    private boolean hopping(float dt) {
        if (hopT <= 0) return false;
        hopT -= dt;
        if (onGround && hopT < 0.5f) { hopT = 0; return false; }
        if (hopT > 0 && !onGround) vx = hopVx;          // en el aire mantiene el impulso (si no, un escalon lo frenaria contra la pared)
        return hopT > 0;
    }

    /**
     * Direccion de persecucion en suelo: +-1, o 0 = esperar. Con camino libre es exactamente signo(dx) (comportamiento de siempre). Si el camino esta
     * cortado por pinchos o un borde, planifica una ruta segura (andar / caer / saltar); si no existe, se queda en el borde mirando al jugador.
     */
    private float chaseDir(Level lv, float dt, Player p, float dx, float sp) {
        float d = Mth.sign(dx);
        navWait = false;
        if (d == 0) d = right ? 1 : -1;
        if (flying || !onGround) return d;
        boolean direct = groundAhead(lv, d) && !(hitWall && Math.abs(vx) < 5f && p.y > y - 24);   // pared delante y el jugador no esta mas arriba (ese caso ya salta)
        if (!navActive) {
            if (direct) return d;
            navActive = true; navT = 0; navOk = false; navTime = 0; navFlipT = 0; dbgBlocked++;
        } else {
            navTime += dt; navFlipT = Math.max(0, navFlipT - dt);
            if ((direct && !hazardBetween(lv, p.x)) || navTime > 10f) { navActive = false; return d; }
        }
        navT -= dt;
        if (navT <= 0) {
            navT = 0.4f;
            int c = Math.max(1, Math.min(3, (int) Math.ceil(bh / Room.TS)));
            boolean hop = canHop();
            int sx = (int) Math.floor(x / Room.TS), sy = (int) Math.floor((y - 1) / Room.TS);
            int gap = hop ? EnemyNav.maxGap(bw, bh, hopSpeed(sp), -300f) : 0;
            EnemyNav.plan(lv.room, sx, sy, c, p.x, p.y, hop, gap);
            dbgPlans++;
            if (EnemyNav.ok) {
                if (navOk && EnemyNav.dir != navDir && navFlipT > 0) { /* histeresis: no cambiar de sentido a cada replanificacion */ }
                else { navOk = true; navDir = EnemyNav.dir; navType = EnemyNav.type; navFlipT = 0.8f; }
            } else navOk = false;
        }
        if (!navOk) { navWait = true; return 0; }
        if (navType == EnemyNav.T_HOP) {
            float u = x - (float) Math.floor(x / Room.TS) * Room.TS;
            boolean at = navDir > 0 ? u >= EnemyNav.HOP_U : u <= Room.TS - EnemyNav.HOP_U;
            if (at && onGround) {
                vy = -300f; vx = hopVx = navDir * hopSpeed(sp); hopT = 0.6f; onGround = false; dbgHops++;
                Snd.sfxAt("en_dash", x, lv.camX + lv.viewW / 2, 0.3f);
            }
        }
        if (navType != EnemyNav.T_HOP && hazardAhead(lv, navDir, 8f)) { navWait = true; return 0; }   // la celda destino es segura pero el cuerpo ya roza el peligro: espera
        return navDir;
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
                if (hopping(dt)) break;
                face(dx);
                float stop = def.range * 0.8f;
                boolean near = Math.abs(dx) <= def.range && Math.abs(dy) < 30;
                float md = Math.abs(dx) > stop ? chaseDir(lv, dt, p, dx, sp) : 0;
                if (md == 0 && !navWait) navActive = false;
                if (md != 0) { vx = Mth.approach(vx, md * sp, 900 * dt); animName = "walk"; if (md != Mth.sign(dx)) right = md > 0; }
                else { vx = Mth.approach(vx, 0, 900 * dt); if (animName.equals("walk")) animName = "idle"; }
                if (hitWall && p.y < y - 24 && onGround) { vy = -300; }   // salta obstaculos si el jugador esta arriba
                if (near && atkCd <= 0) { startState(WINDUP, "windup"); vx = 0; Snd.sfxAt("en_alert", x, lv.camX + lv.viewW / 2, 0.25f); }
                break;
            }
            case WINDUP: {
                vx = Mth.approach(vx, 0, 900 * dt);
                if (heavy) animT -= dt * 0.25f;
                face(dx * (stateT < 0.15f ? 1 : 0));
                if (finishedAnim()) { startState(ATTACK, "attack"); vx = (right ? 1 : -1) * (heavy ? 60 : 110); if (hazardAhead(lv, right ? 1 : -1, 22f)) vx = 0; Snd.sfxAt(heavy ? "en_step_heavy" : "en_attack_melee", x, lv.camX + lv.viewW / 2, 0.6f); }
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
                vx = Mth.approach(vx, 0, hurtFric * dt);
                if (stateT > hurtDur) { state = CHASE; animName = "idle"; }
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
                vx = Mth.approach(vx, 0, hurtFric * dt);
                if (stateT > hurtDur) { state = CHASE; animName = "idle"; }
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
                vx = Mth.approach(vx, 0, hurtFric * dt); vy = Mth.approach(vy, 0, hurtFric * dt);
                lv.move(this, dt);
                if (stateT > hurtDur) { state = CHASE; animName = "idle"; }
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
                vx = Mth.approach(vx, 0, hurtFric * dt); vy = Mth.approach(vy, 0, hurtFric * dt);
                lv.move(this, dt);
                if (stateT > hurtDur) { state = CHASE; animName = "walk"; }
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
                float md = Math.abs(dx) > 50 ? chaseDir(lv, dt, p, dx, sp) : 0;
                if (md == 0 && !navWait) navActive = false;
                if (md != 0) { vx = Mth.approach(vx, md * sp, 900 * dt); animName = "walk"; if (md != Mth.sign(dx)) right = md > 0; }
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
                vx = (right ? 1 : -1) * speed * modSpeed * 4.6f * speedMul();
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
                vx = Mth.approach(vx, 0, hurtFric * dt);
                if (stateT > hurtDur) { state = CHASE; animName = "idle"; }
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
                    float jvy = -270f - Math.min(60f, Math.max(0, -dy) * 0.6f);
                    float jvx = (right ? 1 : -1) * Math.min(sp * 1.9f, Math.max(60f, Math.abs(dx) * 1.3f));
                    float jk = safeLeapScale(lv, jvx, jvy);
                    if (jk == 0f) { state = CHASE; stateT = 0; animName = "idle"; atkCd = 0.5f; dbgBlocked++; break; }   // acabaria en pinchos: espera
                    startState(ATTACK, "attack");
                    vy = jvy;
                    vx = jvx * jk;
                    onGround = false;
                    Snd.sfxAt("en_dash", x, lv.camX + lv.viewW / 2, 0.4f);
                }
                break;
            case ATTACK:
                if (animT * sheet.anim("attack").fps >= sheet.anim("attack").n) animT = (sheet.anim("attack").n - 1) / sheet.anim("attack").fps;
                if (onGround && stateT > 0.1f) { state = CHASE; stateT = 0; animName = "idle"; atkCd = cooldown * (0.7f + lv.rng.f() * 0.4f); vx = 0; }
                break;
            case HURT:
                vx = Mth.approach(vx, 0, hurtFric * dt);
                if (stateT > hurtDur) { state = CHASE; animName = "idle"; }
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
                vx = Mth.approach(vx, 0, hurtFric * dt);
                if (stateT > hurtDur) { state = CHASE; animName = "idle"; }
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
                if (hopping(dt)) break;
                face(dx);
                float md = Math.abs(dx) > 30 ? chaseDir(lv, dt, p, dx, sp * 1.55f) : 0;
                if (md == 0 && !navWait) navActive = false;
                if (md != 0) { vx = Mth.approach(vx, md * sp * 1.55f, 1100 * dt); animName = "walk"; if (md != Mth.sign(dx)) right = md > 0; }
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
                if (hopping(dt)) break;
                face(dx);
                float ad = Math.abs(dx);
                float md = ad > 130 ? chaseDir(lv, dt, p, dx, sp * 1.3f) : 0;
                if (ad <= 130 && !navWait) navActive = false;
                if (md != 0) { vx = Mth.approach(vx, md * sp * 1.3f, 1100 * dt); animName = "walk"; if (md != Mth.sign(dx)) right = md > 0; }
                else if (ad > 130) { vx = Mth.approach(vx, 0, 1100 * dt); animName = "idle"; }
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
                    float lvx = (right ? 1 : -1) * Math.min(320f, Math.max(200f, Math.abs(dx) * 2.4f));
                    float k = safeLeapScale(lv, lvx, -205f);
                    if (k == 0f) { state = RECOVER; stateT = 0; animName = "idle"; atkCd = 0.5f; dbgBlocked++; break; }   // el salto acabaria en pinchos: no se lanza
                    startState(LEAP, "attack");
                    vy = -205f;
                    vx = lvx * k;
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
                vx = Mth.approach(vx, 0, hurtFric * dt);
                if (stateT > hurtDur) { state = CHASE; animName = "idle"; }
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
                float md = Math.abs(dx) > 60 ? chaseDir(lv, dt, p, dx, sp * 1.1f) : 0;
                if (md == 0 && !navWait) navActive = false;
                if (md != 0) { vx = Mth.approach(vx, md * sp * 1.1f, 900 * dt); animName = "walk"; if (md != Mth.sign(dx)) right = md > 0; }
                else { vx = Mth.approach(vx, 0, 900 * dt); animName = "idle"; }
                if (dist < 200 && Math.abs(dy) < 90 && atkCd <= 0 && p.onGround) {
                    startState(VANISH, "idle");
                    float bx = p.x - p.dir() * 30;
                    if (lv.solidAtPx(bx, p.y - 8) || lv.room.hazardAt(bx, p.y - 4) || !groundBehind(lv, bx, p.y)) bx = p.x + p.dir() * 30;
                    if (lv.solidAtPx(bx, p.y - 8) || lv.room.hazardAt(bx, p.y - 4) || !groundBehind(lv, bx, p.y)) bx = p.x;
                    tx = bx; ty = p.y;
                    lv.fxAdd("fx_ring", "pulse", tx, ty - 3, 0.8f, def.color);
                    lv.fxAdd("fx_tele", "in", tx, ty - 14, 0.8f, def.color);
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


    // ------------------------------------------------------------------ elites unicos (dos ataques propios cada uno)
    private boolean is(String id) { return def.id.equals(id); }

    private float eliteWant() {
        switch (def.id) {
            case "caballero_osario": return 40; case "herrero_infernal": return 46; case "ventisca": return 150; case "segador_vacio": return 70;
            case "druida_podrido": return 130; case "capitan_trueno": return 90; case "sacerdote_carmesi": return 140; default: return 80;
        }
    }

    private int chooseAtk(Level lv, float ad) {
        atkCount++;
        switch (def.id) {
            case "caballero_osario": return ad < 80 && lv.rng.chance(0.7f) ? 1 : 2;
            case "herrero_infernal": return ad < 64 ? 2 : 1;
            case "centurion_eclipse": return ad < 80 ? 2 : 1;
            case "segador_vacio": return lv.rng.chance(0.5f) ? 1 : 2;
            default: return atkCount % 2 == 1 ? 1 : 2;
        }
    }

    private boolean eliteDash() {
        return atk == 2 && (is("caballero_osario") || is("capitan_trueno") || is("ventisca"));
    }

    private float groundY(Level lv, float px, float py) { return lv.groundBelow(px, py - 24); }

    private void marker(Level lv, float mx, float my, int color) {
        lv.fxAdd("fx_ring", "pulse", mx, my - 2, 0.9f, color);
        lv.fxAdd("fx_tele", "in", mx, my - 12, 0.8f, color);
    }

    private void startElite(Level lv, Player p) {
        if (is("segador_vacio") && atk == 1) {          // se desvanece y reaparece junto al jugador
            startState(VANISH, "idle");
            float bx = p.x - p.dir() * 34;
            if (lv.solidAtPx(bx, p.y - 8) || lv.room.hazardAt(bx, p.y - 4) || !groundBehind(lv, bx, p.y)) bx = p.x + p.dir() * 34;
            if (lv.solidAtPx(bx, p.y - 8) || lv.room.hazardAt(bx, p.y - 4) || !groundBehind(lv, bx, p.y)) bx = p.x;
            tx = bx; ty = p.y;
            marker(lv, tx, ty, def.color);
            Snd.sfxAt("en_alert", x, lv.camX + lv.viewW / 2, 0.7f);
            lv.ps.burst(lv.rng, x, y - bh / 2, def.color, 14, 90, 0.4f, 2, 0, true);
            return;
        }
        startState(WINDUP, atk == 2 ? "windup2" : "windup");
        vx = 0;
        if (flying) vy = 0;
        aimX = p.x; aimY = p.cy();
        Snd.sfxAt("en_alert", x, lv.camX + lv.viewW / 2, 0.8f);
        // avisos en el suelo ANTES del golpe
        if ((is("druida_podrido") && atk == 1) || (is("capitan_trueno") && atk == 1)) {
            eN = 3;
            for (int k = 0; k < 3; k++) {
                eX[k] = p.x + (k - 1) * (is("capitan_trueno") ? 52 : 44);
                marker(lv, eX[k], groundY(lv, eX[k], p.y), def.color);
            }
        } else if (is("sacerdote_carmesi") && atk == 2) {
            eN = 1; eX[0] = p.x;
            marker(lv, eX[0], groundY(lv, eX[0], p.y), def.color);
        }
    }

    private void enterAttack(Level lv, Player p) {
        startState(ATTACK, atk == 2 ? "attack2" : "attack");
        shot = false; hitDone = false;
        float dir = right ? 1 : -1;
        if (!flying && atk == 2 && (is("caballero_osario") || is("capitan_trueno")) && (!groundAhead(lv, dir) || hazardAhead(lv, dir, 8f + 300f * 300f / 1800f))) { vx = 0; }   // no embiste hacia pinchos ni vacio
        else if (is("caballero_osario") && atk == 2) { vx = dir * 300f; Snd.sfxAt("en_dash", x, lv.camX + lv.viewW / 2, 0.8f); }
        else if (is("capitan_trueno") && atk == 2) { vx = dir * 270f; Snd.sfxAt("en_dash", x, lv.camX + lv.viewW / 2, 0.8f); }
        else if (is("ventisca") && atk == 2) {
            float ddx = aimX - x, ddy = aimY - cy(), d = (float) Math.sqrt(ddx * ddx + ddy * ddy) + 0.01f;
            vx = ddx / d * 300f; vy = ddy / d * 300f; right = vx >= 0;
            Snd.sfxAt("en_dash", x, lv.camX + lv.viewW / 2, 0.8f);
        }
    }

    /** Se lanza una vez, en el fotograma de liberacion del ataque. */
    private void eliteRelease(Level lv, Player p) {
        float dir = right ? 1 : -1;
        float mx = x + dir * 16, my = y - bh * 0.6f;
        float cx0 = lv.camX + lv.viewW / 2;
        switch (def.id) {
            case "caballero_osario":
                if (atk == 1) {
                    Proj w = lv.proj(x + dir * 22, y - 6, dir * 210f, 0, dmgNow() * 0.9f, false, "crescent", def.color);
                    w.special = 1; w.life = 1.7f; w.radius = 8; w.scale = 1.4f;
                    lv.shake(3f, 0.2f); Snd.sfxAt("en_step_heavy", x, cx0, 0.9f);
                }
                break;
            case "herrero_infernal":
                if (atk == 1) {
                    for (int k = -1; k <= 1; k++) {
                        float T = 0.95f, g = 700f, tgx = p.x + k * 42f;
                        Proj pr = lv.proj(mx, my, (tgx - mx) / T, ((p.y - 6) - my - 0.5f * g * T * T) / T, dmgNow(), false, "magma", def.color);
                        pr.grav = g; pr.life = T + 0.4f; pr.explode = 34; pr.status = Ent.BURN; pr.statusDur = 3f; pr.statusPow = 5f; pr.radius = 6; pr.trail = true;
                    }
                    Snd.sfxAt("en_cast", x, cx0, 0.8f);
                } else {
                    for (int s = -1; s <= 1; s += 2) {
                        Proj w = lv.proj(x + s * 18, y - 6, s * 190f, 0, dmgNow() * 0.8f, false, "magma", def.color);
                        w.special = 1; w.life = 1.4f; w.radius = 8; w.scale = 1.3f;
                    }
                    lv.shake(4f, 0.25f); Snd.sfxAt("explosion_small", x, cx0, 0.9f);
                    lv.fx("fx_dust", "land", x + dir * 20, y - 2, 1.4f, 0, 0);
                }
                break;
            case "ventisca":
                if (atk == 1) {
                    for (int k = 0; k < 10; k++) {
                        float ang = k * 0.6283f + 0.3f;
                        Proj pr = lv.proj(x, y - bh / 2, (float) Math.cos(ang) * 125f, (float) Math.sin(ang) * 125f, dmgNow() * 0.8f, false, "iceshard", def.color);
                        pr.status = Ent.SLOW; pr.statusDur = 2.5f; pr.life = 3.4f; pr.radius = 5;
                    }
                    lv.fxAdd("fx_ring", "pulse", x, y - bh / 2, 1.2f, def.color);
                    Snd.sfxAt("hit_ice", x, cx0, 0.9f);
                }
                break;
            case "segador_vacio":
                if (atk == 2) {
                    for (int k = -1; k <= 1; k++) {
                        Proj pr = lv.proj(x, y - bh * 0.9f, k * 70f, -85f, dmgNow() * 0.8f, false, "voidorb", def.color);
                        pr.homing = 90f; pr.life = 5f; pr.radius = 6;
                    }
                    Snd.sfxAt("en_cast", x, cx0, 0.9f);
                    lv.fxAdd("fx_ring", "pulse", x, y - bh, 0.9f, def.color);
                }
                break;
            case "druida_podrido":
                if (atk == 1) {
                    for (int k = 0; k < eN; k++) {
                        final float rx = eX[k];
                        lv.later(0.30f + 0.2f * k, () -> {
                            float gy = groundY(lv, rx, y);
                            lv.fx("fx_thorn", "vine", rx, gy, 1.1f, 0, 0);
                            lv.explosion(rx, gy - 8, 18, dmgNow() * 1.1f, 150, Ent.POISON, 3f, 4f, false);
                            lv.ps.burst(lv.rng, rx, gy - 6, 0x6AA040, 10, 90, 0.4f, 2, 200, false);
                            Snd.sfxAt("hit_flesh_1", rx, cx0, 0.6f);
                        });
                    }
                } else {
                    float T = 1.0f, g = 650f;
                    Proj pr = lv.proj(mx, my, (p.x - mx) / T, ((p.y - 6) - my - 0.5f * g * T * T) / T, dmgNow(), false, "poison", def.color);
                    pr.grav = g; pr.life = T + 0.4f; pr.explode = 40; pr.status = Ent.POISON; pr.statusDur = 4f; pr.statusPow = 5f; pr.radius = 6;
                    float base = (float) Math.atan2(p.cy() - my, p.x - mx);
                    for (int k = -2; k <= 2; k++) {
                        Proj lf = lv.proj(mx, my, (float) Math.cos(base + k * 0.24f) * 150f, (float) Math.sin(base + k * 0.24f) * 150f, dmgNow() * 0.6f, false, "leaf", def.color);
                        lf.life = 3f; lf.radius = 4;
                    }
                    Snd.sfxAt("en_cast", x, cx0, 0.8f);
                }
                break;
            case "capitan_trueno":
                if (atk == 1) {
                    for (int k = 0; k < eN; k++) {
                        final float rx = eX[k];
                        lv.later(0.12f + 0.28f * k, () -> {
                            float gy = groundY(lv, rx, y);
                            lv.lightning(rx, gy - 170, rx, gy);
                            lv.fx("fx_lightning", "ground", rx, gy, 1f, 0, 0);
                            lv.explosion(rx, gy - 12, 22, dmgNow() * 1.2f, 160, Ent.SHOCK, 1.5f, 0, false);
                            Snd.sfxAt("hit_shock", rx, cx0, 0.8f);
                            lv.shake(2.5f, 0.15f);
                        });
                    }
                }
                break;
            case "sacerdote_carmesi":
                if (atk == 1) {
                    float base = (float) Math.atan2(p.cy() - my, p.x - mx);
                    for (int k = -1; k <= 1; k++) {
                        Proj pr = lv.proj(mx, my, (float) Math.cos(base + k * 0.4f) * 120f, (float) Math.sin(base + k * 0.4f) * 120f, dmgNow(), false, "bloodorb", def.color);
                        pr.homing = 110f; pr.life = 4.5f; pr.radius = 6; pr.status = Ent.BLEED; pr.statusDur = 3f; pr.statusPow = 4f;
                    }
                    Snd.sfxAt("en_cast", x, cx0, 0.8f);
                } else {
                    final float rx = eX[0];
                    lv.later(0.40f, () -> {
                        float gy = groundY(lv, rx, y);
                        lv.fx("fx_blood", "splat", rx, gy - 6, 1.4f, 0, 0);
                        lv.fx("fx_fire", "pillar", rx, gy, 0.9f, 0xD0203A, Platform.ADD | Platform.TINT);
                        int n = lv.explosion(rx, gy - 14, 28, dmgNow() * 1.3f, 160, Ent.BLEED, 3f, 4f, false);
                        if (n > 0 && alive) { hp = Math.min(maxHp, hp + maxHp * 0.12f); lv.text(x, y - bh - 8, "+" + Math.round(maxHp * 0.12f), 0xFF6A7C, false); }
                        Snd.sfxAt("hit_blood", rx, cx0, 0.8f);
                    });
                }
                break;
            case "centurion_eclipse":
                if (atk == 1) {
                    Proj bm = lv.proj(mx, my, dir * 620f, 0, dmgNow() * 1.3f, false, "holy", def.color);
                    bm.life = 0.9f; bm.radius = 9; bm.scale = 1.6f;
                    lv.fx("fx_holy", "beam", mx + dir * 30, my, 1.2f, def.color, Platform.ADD | Platform.TINT);
                    lv.shake(2f, 0.2f); Snd.sfxAt("en_cast", x, cx0, 0.9f);
                } else {
                    lv.explosion(x, y - 14, 56, dmgNow() * 0.9f, 220, -1, 0, 0, false);
                    lv.fxAdd("fx_ring", "pulse", x, y - 14, 1.3f, def.color);
                    lv.ps.burst(lv.rng, x, y - 14, 0xFFE8A0, 18, 150, 0.5f, 2, 0, true);
                    Snd.sfxAt("hit_metal_2", x, cx0, 0.9f);
                }
                break;
            default: break;
        }
    }

    private void eliteAI(Level lv, float dt, Player p, float dx, float dy, float dist, float sp) {
        boolean moved = false;
        switch (state) {
            case PATROL: patrol(lv, dt, sp); return;
            case CHASE: {
                face(dx);
                float want = eliteWant(), ad = Math.abs(dx);
                if (flying) {
                    bob += dt * 2.4f;
                    flyMove(lv, dt, p.x + (dx > 0 ? -1 : 1) * want, p.y - 78 + (float) Math.sin(bob) * 9, sp, 480);
                    animName = "walk"; moved = true;
                } else {
                    float md = ad > want ? chaseDir(lv, dt, p, dx, sp) : 0;
                    if (md == 0 && !navWait) navActive = false;
                    if (md != 0) { vx = Mth.approach(vx, md * sp, 900 * dt); animName = "walk"; if (md != Mth.sign(dx)) right = md > 0; }
                    else { vx = Mth.approach(vx, 0, 900 * dt); animName = "idle"; }
                }
                if (!flying && hitWall && p.y < y - 24 && onGround) vy = -300;
                if (atkCd <= 0 && dist < def.range && (flying || Math.abs(dy) < 120)) { atk = chooseAtk(lv, ad); startElite(lv, p); }
                break;
            }
            case VANISH:
                vx = 0; vy = 0;
                if (stateT >= 0.8f) {
                    x = tx; y = ty; vx = vy = 0; right = p.x >= x;
                    startState(WINDUP, "windup");
                    lv.ps.burst(lv.rng, x, y - bh / 2, def.color, 18, 120, 0.4f, 2, 0, true);
                    lv.fxAdd("fx_ring", "pulse", x, y - bh / 2, 0.8f, def.color);
                }
                return;
            case WINDUP: {
                vx = Mth.approach(vx, 0, 900 * dt);
                if (flying) { vy = Mth.approach(vy, 0, 700 * dt); }
                if (stateT < 0.35f) { face(dx); aimX = p.x; aimY = p.cy(); }
                if (is("centurion_eclipse") && atk == 1) {   // rayo solar: la linea avisa antes
                    float dir = right ? 1 : -1, my = y - bh * 0.6f;
                    lv.lines.add(new float[]{x + dir * 16, my, x + dir * 420, my, 0.05f, stateT > 0.55f ? 0xFFFFFF : 0xFFD25A});
                }
                if (finishedAnim() && stateT > 0.6f) enterAttack(lv, p);
                if (flying) { lv.move(this, dt); moved = true; }
                break;
            }
            case ATTACK: {
                Anim a = sheet.anim(animName);
                float dir = right ? 1 : -1;
                boolean dashing = eliteDash();
                if (dashing) {
                    if (is("ventisca")) { /* mantiene el vector del picado */ }
                    else vx = dir * (is("caballero_osario") ? 300f : 270f);
                    if ((int) (stateT * 30) % 2 == 0) lv.ps.spawn(x - dir * 8, y - (flying ? bh / 2 : 3), 0, -8, 0.3f, 3, 0, def.color, true);
                    if (!hitDone && p.alive && overlaps(p.x - p.bw / 2, p.y - p.bh, p.bw, p.bh)) { hitDone = true; lv.hurtPlayer(dmgNow() * 1.15f, x, statusId, 3f); }
                    if (!flying && (!groundAhead(lv, dir) || hazardAhead(lv, dir, 8f + vx * vx / 1800f))) vx = 0;   // frena con el recorrido real del embestido
                }
                int rel = a.rel >= 0 ? a.rel : (a.h0 >= 0 ? a.h0 : a.n / 2);
                if (!shot && a.frameAt(animT) >= rel) { shot = true; eliteRelease(lv, p); }
                if (!hitDone && !dashing && a.hitActive(animT)) {
                    float[] b = new float[4];
                    if (a.worldBox(x, y, right, b) && p.overlaps(b[0], b[1], b[2], b[3])) { hitDone = true; lv.hurtPlayer(dmgNow(), x, statusId, 3f); }
                }
                if (!dashing) { vx = Mth.approach(vx, 0, 900 * dt); if (flying) vy = Mth.approach(vy, 0, 700 * dt); }
                boolean over = dashing ? (stateT > 0.5f || hitWall) : a.done(animT);
                if (over) { state = RECOVER; stateT = 0; animName = "idle"; atkCd = cooldown * (0.85f + lv.rng.f() * 0.4f); vx *= 0.2f; if (flying) vy *= 0.2f; }
                if (flying) { lv.move(this, dt); moved = true; }
                break;
            }
            case RECOVER:
                vx = Mth.approach(vx, 0, 1000 * dt);
                if (flying) { vy = Mth.approach(vy, -20, 600 * dt); lv.move(this, dt); moved = true; }
                if (stateT > 0.55f) state = CHASE;
                break;
            case HURT:
                vx = Mth.approach(vx, 0, 500 * dt);
                if (flying) { vy = Mth.approach(vy, 0, 400 * dt); lv.move(this, dt); moved = true; }
                if (stateT > 0.24f) { state = CHASE; animName = "idle"; }
                break;
            default: state = CHASE; break;
        }
        if (!moved) gravityMove(lv, dt);
    }

    // ------------------------------------------------------------------ dibujo
    private float hpShow = -1;
    private final float[] rx = new float[3];
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
        float spd = (float) Math.hypot(vx, vy);
        boolean rush = alive && (state == CHARGE || state == DIVE || state == LEAP) && spd > 120f;
        if (rush && !Impact.react(lv, this, rx)) {       // smear de embestida/salto/picado: silueta estirada en el sentido del movimiento + ecos (solo visual)
            boolean vert = Math.abs(vy) > Math.abs(vx) * 1.4f;
            float k = Mth.clamp((spd - 120f) / 200f, 0.4f, 1f);
            float ssx = scale * (vert ? 1f - 0.10f * k : 1f + 0.22f * k), ssy = scale * (vert ? 1f + 0.22f * k : 1f - 0.10f * k);
            if (!Save.S.reduceFx) for (int i = 2; i >= 1; i--) {
                float ex = spd > 1f ? -vx / spd * 6f * i : 0f, ey = spd > 1f ? -vy / spd * 6f * i : 0f;
                sheet.drawSq(g, a, frame, x + ex, y + dy + ey, right, ssx, ssy, Platform.ADD | Platform.TINT, def.color, i == 1 ? 0.28f : 0.14f);
            }
            sheet.drawSq(g, a, frame, x, y + dy, right, ssx, ssy, flags, tint, alpha);
        } else if (Impact.react(lv, this, rx)) sheet.drawSq(g, a, frame, x + rx[2], y + dy, right, scale * rx[0], scale * rx[1], flags, tint, alpha);
        else sheet.draw(g, a, frame, x, y + dy, right, scale, flags, tint, alpha);
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
                // estados importantes (como mucho 3 iconos pequenos: no llenan la pantalla)
                int shown = 0;
                String[] sic = {"burn", "freeze", "shield", "poison", "shock", "bleed", "", "", "skull"};
                for (int si = 0; si < Ent.ST_COUNT && shown < 3; si++) {
                    if (st[si] > 0 && !sic[si].isEmpty()) { UI.icon(g, sic[si], bx + shown * 9 - 1, by - 10, 0.5f, Platform.TINT, Ent.ST_COLOR[si], 0.95f); shown++; }
                }
            }
        }
    }
}
