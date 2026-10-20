package com.julianfarks.roguelike.core;

import java.util.HashSet;
import java.util.List;

/** El jugador: movimiento, combo, rodar, habilidades y definitiva. */
public final class Player extends Ent {
    public static final int IDLE = 0, RUN = 1, AIR = 2, ROLL = 3, ATK = 4, SKILL = 5, ULT = 6, HURT = 7, DEAD = 8;

    public final ClassDef cls;
    public int state = IDLE;
    public int skinTint;
    public final WeaponFx.State wfx = new WeaponFx.State(); public float reloadDoneT, reloadMax = 1f; public float swapCd, swapAnimT, wpnT, swapBuf, secView; public int selWant; public int wpnId, wandEl; public String swapIcon;
    public float secCd, grenCd, safeX, safeY, invuln, shield, skinT, hurtT, furia;
    public float extVx;                       // empuje externo (atraccion de jefes)
    public float guardT;                      // guardia de acero
    public float eclipseT;
    public float regenT, regenRate;
    public int combo, hitCount;

    private float rollBuf, skillBuf, ultBuf; private int skillBufIdx;
    float atkBuf; private float rollCd, jumpBuf, coyote, comboWin, stepT, safeT, dustT, trailT, actionT;
    private int jumpsLeft, skillIdx, lastFrame = -1;
    private boolean jumping, skillFired, swingFx, deathSent;
    private final HashSet<Ent> swingHit = new HashSet<>();
    private final HashSet<Ent> dashHit = new HashSet<>();
    private float dashT, dashSpeed, dashDmg, dashSDur;
    private int dashStatus = -1;
    private boolean dashHeal;
    private float dashDir = 1;
    private final float[] box = new float[4];
    private float prevVy;

    // ---- vida propia (animaciones de personalidad: solo cosmeticas, no tocan estadisticas ni colisiones)
    /** Hoja de personalidad (plx_<clase>); null si el skin equipado usa otra hoja o no existe. */
    public Sheet sheetX;
    /** Animacion de personalidad en curso (idle1..idle4, chest, awe, touch, victory) o null. */
    public String actName;
    private float idleT, stillT, idleNext = 4f, holdT, actHold, impAt = 14f;
    private String pendReact; private float pendT;
    private int lastIdle = -1, idlePicks, cosSeed = 0x2F6E2B1;
    public static final String[] IDLES = {"idle1", "idle2", "idle3", "idle4", "idle5", "idle6", "idle7", "idle8", "idle9", "idle10"};
    private static final int IMP = 3;      // idle4 = impaciencia: solo tras mucho rato quieto

    public Player(RunState rs) {
        this.cls = rs.cls;
        sheet = Cosmetics.sheetFor(cls);
        skinTint = Cosmetics.tintFor(cls);
        if (sheet == Assets.spr("pl_" + cls.key)) { Sheet x = Assets.spr("plx_" + cls.key); if (x != Sheet.EMPTY) sheetX = x; }
        cosSeed ^= cls.id * 7919 + 17;
        idleNext = 3.5f + cosF() * 3.5f;
        bw = Math.min(sheet.bw, 14);
        bh = sheet.bh;
        alive = true;
        hp = maxHp = 1;
    }

    public boolean rolling() {
        if (state != ROLL) return false;
        return animT < 0.30f + (statsFantasma > 0 ? 0.08f * statsFantasma : 0f);
    }

    private int statsFantasma;

    public int dir() { return right ? 1 : -1; }

    public void onRoomStart(Level lv) {
        Stats s = lv.rs.stats;
        if (s.shieldLvl > 0) shield = Math.max(shield, 14 + 10 * s.shieldLvl);
        if (s.eclipseCd > 0) eclipseT = Math.min(eclipseT, 3f);
        int b = lv.rs.bless[Blessing.SABIO];
        if (b > 0) lv.rs.ult = Math.max(lv.rs.ult, 15f);
        invuln = 1f;
        int rt = lv.room.type;   // entrada a una sala especial: gesto breve (cosmetico)
        if (rt == Room.SHOP || rt == Room.BLESSING || rt == Room.FORGE || rt == Room.FOUNTAIN || rt == Room.TREASURE || rt == Room.REST || rt == Room.EVENT) react("touch", 0.8f);
    }

    /**
     * Politica de interrupcion de habilidades (se llama justo ANTES de aplicar un golpe al jugador):
     *  - habilidad de supervivencia (Skills.committed) en preparacion: se libera ya, para que su proteccion cuente contra este golpe;
     *  - habilidad ofensiva sin liberar: se cancela y se devuelve el enfriamiento (no se gasto nada);
     *  - habilidad ya liberada: su efecto no se toca (solo se corta la animacion de recuperacion).
     */
    public void onHitDuringCast(Level lv) {
        if (chargeT >= 0) cancelCharge(true);      // recibir dano corta la carga: sin golpe, sin gasto, y puede atacar de inmediato
        if (state != SKILL || skillFired) return;
        if (Skills.committed(cls.id, skillIdx)) { skillFired = true; castSkills(lv); }
        else { lv.rs.cd[skillIdx] = 0; interruptedSkills++; }
    }
    public int interruptedSkills;

    // ------------------------------------------------------------------ ataque cargado (arma principal)
    /** Tiempo (s reales) que lleva pulsado el ataque; -1 = no se esta cargando. */
    public float chargeT = -1f;
    private boolean chargeFull, swingCharged;
    private float chgMul = 1f, chgFrac = 0f, chgFx;
    /** Para pruebas: cargas iniciadas / cortadas / ejecutadas, ultimo multiplicador aplicado, golpes cargados. */
    public int dbgChargeStart, dbgChargeCancel, dbgChargeRelease, dbgChargedHits;
    public float dbgLastMul = 1f;
    public boolean charging() { return chargeT >= 0f; }
    public float chargeFrac() { return chargeT < 0 ? 0f : ChargeCfg.frac(chargeT); }

    /** Limpia la carga sin golpear (menus, cambio de escena, perdida de foco). */
    public void abortCharge() { cancelCharge(false); }

    private void cancelCharge(boolean byHit) {
        if (chargeT < 0f) return;
        chargeT = -1f; chargeFull = false; chgFx = 0; atkBuf = 0; dbgChargeCancel++;
        if (state != ATK && state != SKILL && state != ULT && state != ROLL && state != HURT) animT = 0;
    }

    /** Pose de preparacion: avanza por los fotogramas de anticipacion del golpe pesado segun la carga (se aplica tras elegir la animacion del estado). */
    private void chargePose() {
        float fr = ChargeCfg.frac(chargeT);
        String an = onGround ? "attack3" : "airatk";
        Anim a = sheet.anim(an);
        animName = an;
        float tHit = a.h0 > 0 ? a.timeOf(a.h0) : a.duration() * 0.3f;
        animT = Math.max(0f, Math.min(tHit - 0.001f, tHit * (0.35f + 0.65f * fr)));
    }

    private boolean chargeBlocked(Level lv, boolean ctl, boolean frozenNow) {
        boolean secOn = lv.rs.secActive && lv.rs.sec != 0;
        return !alive || !ctl || frozenNow || guarding || secOn || lv.cinematic || !(state == IDLE || state == RUN || state == AIR);
    }

    /** Acumula la carga con tiempo real, dibuja los efectos progresivos y ejecuta el golpe al soltar. */
    private void updateCharge(Level lv, float dt, boolean ctl, boolean frozenNow) {
        if (chargeBlocked(lv, ctl, frozenNow)) { cancelCharge(false); return; }
        chargeT += lv.rawDt;
        if (!lv.in.held(Input.B_ATTACK)) {      // soltar: ejecuta lo acumulado (una sola vez)
            float t = chargeT;
            chargeT = -1f; chargeFull = false; chgFx = 0;
            dbgChargeRelease++;
            startAttack(lv, t >= ChargeCfg.TAP ? t : 0f);
            return;
        }
        float fr = ChargeCfg.frac(chargeT);
        if (chargeT < ChargeCfg.TAP) return;
        sq = Math.max(sq, 0.05f + 0.10f * fr);
        // particulas que se concentran en el arma: mas y mas rapidas segun la carga
        chgFx -= lv.rawDt;
        if (chgFx <= 0f) {
            chgFx = (0.11f - 0.07f * fr) * (Save.S.reduceFx ? 2f : 1f);
            float ang = (float) (Math.random() * Math.PI * 2), rr = 18f + 12f * fr;
            float wx = x + dir() * 14, wy = y - 20;
            lv.ps.spawn(wx + (float) Math.cos(ang) * rr, wy + (float) Math.sin(ang) * rr, -(float) Math.cos(ang) * 60f, -(float) Math.sin(ang) * 60f, 0.28f, 2, 0, fr >= 1f ? 0xFFF0A0 : cls.color1, true);
        }
        if (!chargeFull && chargeT >= ChargeCfg.MAX) {      // senal clara de carga maxima
            chargeFull = true;
            Snd.sfxv("cd_ready", 0.9f);
            lv.fx("fx_ring", "pulse", x, y - 18, 0.5f, 0xFFE070, Platform.ADD | Platform.TINT);
            lv.ps.burst(lv.rng, x, y - 18, 0xFFF0A0, Save.S.reduceFx ? 5 : 10, 110, 0.35f, 2, 0, true);
        }
    }
    void debugSkill(Level lv, int i) { trySkill(lv, i); }
    boolean debugSkillFired() { return skillFired; }

    public void cancelAction() {
        if (!alive) return;
        dashT = 0; rollBuf = skillBuf = ultBuf = 0; cancelCharge(false);
        if (state != DEAD) { state = HURT; animName = "hurt"; animT = 0; }
        swingHit.clear();
    }

    public void die() {
        actName = null; pendReact = null;
        alive = false;
        state = DEAD;
        animName = "death";
        animT = 0;
        vx = 0;
        dashT = 0;
        lastFrame = -1;
    }

    /** Vuelve a la vida (revivida del modo infinito). */
    public void revive() {
        alive = true; deathSent = false;
        actName = null; pendReact = null; idleT = stillT = 0;
        state = IDLE; animName = "idle"; animT = 0;
        vx = 0; vy = 0; invuln = 3.5f; hurtT = 0;
    }

    /** Daño base de arma/habilidad antes de multiplicadores propios. */
    public float baseDmg(Level lv) {
        return cls.dmg * lv.rs.stats.dmgMul * (1f + 0.04f * furia);
    }

    public float skillBase(Level lv) { return baseDmg(lv) * lv.rs.stats.skillDmg; }

    public void addFuria(Level lv) {
        int cap = lv.rs.stats.furiaCap;
        if (cap > 0) furia = Math.min(cap, furia + 1);
    }

    /** Inicia una carrera de daño (dash). */
    public void dash(float dirv, float speed, float dur, float dmgMul, int status, float sDur, boolean heal) {
        dashDir = dirv; dashSpeed = speed; dashT = dur; dashDmg = dmgMul; dashStatus = status; dashSDur = sDur; dashHeal = heal;
        dashHit.clear();
        right = dirv >= 0;
        invuln = Math.max(invuln, dur + 0.05f);
        vy = 0;
    }

    public boolean dashing() { return dashT > 0; }

    // ------------------------------------------------------------------ actualizacion
    public void update(Level lv, float dt) {
        RunState rs = lv.rs;
        Stats s = rs.stats;
        Input in = lv.in;
        statsFantasma = s.fantasma;
        if (invuln > 0) invuln -= dt;
        if (hitFlash > 0) hitFlash -= dt;
        if (skinT > 0) skinT -= dt;
        if (guardT > 0) guardT -= dt;
        if (rollCd > 0) rollCd -= dt;
        if (comboWin > 0) comboWin -= dt;
        if (atkBuf > 0) atkBuf -= dt;
        if (jumpBuf > 0) jumpBuf -= dt;
        if (rollBuf > 0) rollBuf -= dt;
        if (skillBuf > 0) skillBuf -= dt;
        if (ultBuf > 0) ultBuf -= dt;
        if (dropT > 0) dropT -= dt;
        sq += (0f - sq) * Math.min(1f, dt * 11f);
        if (secCd > 0) secCd -= dt;
        if (swapCd > 0) swapCd -= dt;
        if (swapAnimT > 0) swapAnimT -= dt;
        if (wpnT > 0) wpnT -= dt;
        { float tv = (lv.rs.secActive && lv.rs.sec > 0) ? 1f : 0f; secView += Mth.clamp(tv - secView, -dt * 8f, dt * 8f); }
        if (reloadDoneT > 0) reloadDoneT -= dt;
        WeaponFx.tick(this, dt);
        Melee.update(lv, this, dt);
        if (swapBuf > 0) swapBuf -= dt;
        if (lv.rs.sec == 0) lv.rs.secActive = false;
        if (grenCd > 0) grenCd -= dt;
        for (int i = 0; i < 4; i++) if (i < 3 && rs.cd[i] > 0) rs.cd[i] = Math.max(0, rs.cd[i] - dt);
        if (s.eclipseCd > 0 && eclipseT > 0) eclipseT -= dt;
        rs.time += dt;

        if (!alive) {
            animT += dt;
            vy = Math.min(Level.FALL_MAX, vy + Level.GRAV * dt);
            vx *= 0.9f;
            lv.move(this, dt);
            if (!deathSent && sheet.anim("death").done(animT + 0.5f)) {
                deathSent = true;
                if (lv.listener != null) lv.listener.onPlayerDead(lv);
            }
            return;
        }

        // estados alterados
        float dps = Status.tick(this, dt);
        Status.fx(lv, this, dt);
        if (dps > 0) {
            dotAcc += dps * dt * Math.max(0.5f, rs.enemyDmgMul()) * s.dmgTaken;
            if (dotAcc >= 1f) {
                int d = (int) dotAcc; dotAcc -= d;
                rs.hp -= d; hitFlash = 0.06f; lv.roomHits++;
                lv.text(x, y - bh - 6, String.valueOf(d), 0xB0E070, false);
                if (rs.hp <= 0) { lv.playerDeath(); return; }
            }
        }
        if (regenT > 0) {
            regenT -= dt;
            lv.healPlayer(0);
            float add = regenRate * dt * Infinite.healMul(rs);
            rs.hp = Math.min(s.maxHp, rs.hp + add);
        }
        if (cls.id == 5 && rs.hp < s.maxHp && !lv.cinematic) rs.hp = Math.min(s.maxHp, rs.hp + 0.4f * dt);   // Savia: regeneracion lenta
        if (hurtT > 0) hurtT -= dt;

        boolean ctl = !lv.cinematic && hurtT <= 0 && state != ULT;
        float mx = ctl ? in.moveX() : 0;
        if (ctl && mx == 0 && !in.held(Input.B_LEFT) && !in.held(Input.B_RIGHT)) mx = 0;
        float spd = 135f * s.speedMul * speedMul() * BlessFx.speedMul(lv);
        boolean frozenNow = frozen();
        guarding = ctl && !frozenNow && alive && in.held(Input.B_GUARD) && (state == IDLE || state == RUN || state == AIR) && dashT <= 0;
        if (parryCd > 0) parryCd -= dt;
        if (parryFlash > 0) parryFlash -= dt;
        if (guarding) {
            if (in.pressed(Input.B_GUARD) && parryCd <= 0) { parryT = Items.SH_WIN[rs.shield]; parryCd = Items.SH_CD[rs.shield]; Snd.sfxv("swing_air", 0.5f); lv.fx("fx_ring", "pulse", x + dir() * 10, y - 16, 0.35f, 0xFFFFFF, Platform.ADD | Platform.TINT); }
            if (parryT > 0) parryT -= dt;
            spd *= 0.5f;
        } else parryT = 0;
        if (chargeT >= 0f) spd *= ChargeCfg.SLOW_MOVE;      // cargando se puede caminar, pero lento

        // ---- entradas
        if (ctl && !frozenNow) {
            if (in.pressed(Input.B_JUMP)) jumpBuf = 0.17f;
            if (in.pressed(Input.B_ATTACK)) atkBuf = 0.22f;
            if (in.pressed(Input.B_POTION)) drinkPotion(lv);
            if (in.pressed(Input.B_WMAIN)) { selWant = 1; swapBuf = 0.16f; }
            if (in.pressed(Input.B_WSEC)) { selWant = 2; swapBuf = 0.16f; }
            if (swapBuf > 0 && selWant != 0) {      // seleccion directa: nunca ataca ni reinicia nada; si ya esta elegida no hace nada
                if (Arsenal.isSelected(lv.rs, selWant == 2)) { swapBuf = 0; selWant = 0; }
                else if ((state == IDLE || state == RUN || state == AIR || state == SKILL) && !guarding) { Arsenal.select(lv, this, selWant == 2); swapBuf = 0; selWant = 0; }
            } else selWant = 0;
            if (state != HURT && state != ULT && state != ROLL) {
                if (in.pressed(Input.B_SEC)) Items.useSecondary(lv, this);
                if (in.pressed(Input.B_GREN)) Items.throwGrenade(lv, this);
            }
            // esquiva y habilidades: si el estado actual las bloquea (recuperacion, otra habilidad) se guardan 0.16 s y salen al quedar libre
            if (in.pressed(Input.B_ROLL)) rollBuf = 0.16f;
            if (rollBuf > 0 && tryRoll(lv, mx)) rollBuf = 0;
            for (int i = 0; i < 3; i++) if (in.pressed(Input.B_S1 + i)) { skillBuf = 0.16f; skillBufIdx = i; }
            if (skillBuf > 0) { int r = trySkill(lv, skillBufIdx); if (r != 1) skillBuf = 0; }
            if (in.pressed(Input.B_ULT)) ultBuf = 0.16f;
            if (ultBuf > 0) { int r = tryUlt(lv); if (r != 1) ultBuf = 0; }
        }

        // ---- maquina de estados
        boolean canAct = state == IDLE || state == RUN || state == AIR;
        switch (state) {
            case ROLL: updateRoll(lv, dt); break;
            case ATK: updateAttack(lv, dt, mx, spd); break;
            case SKILL: case ULT: updateCast(lv, dt); break;
            case HURT:
                animT += dt;
                if (hurtT <= 0) state = onGround ? IDLE : AIR;
                break;
            default: break;
        }
        if (state == IDLE || state == RUN || state == AIR) {
            canAct = true;
            if (ctl && !frozenNow) {
                boolean secOn = lv.rs.secActive && lv.rs.sec != 0;
                if (secOn) {      // arma secundaria activa: el boton de ataque la dispara (mantener = repetir)
                    if ((atkBuf > 0 || in.held(Input.B_ATTACK)) && !guarding && secCd <= 0 && swapCd <= 0) { atkBuf = 0; Items.useSecondary(lv, this); canAct = false; }
                } else if (atkBuf > 0 && !guarding) {
                    if (lv.in.held(Input.B_ATTACK) && chargeT < 0f) { chargeT = 0f; chargeFull = false; atkBuf = 0; dbgChargeStart++; }   // sigue pulsado: empieza a cargar (un toque rapido = ataque normal al soltar)
                    else startAttack(lv, 0f);
                    canAct = false;
                }
            }
        }

        if (chargeT >= 0f) updateCharge(lv, dt, ctl, frozenNow);

        // ---- movimiento horizontal / vertical
        if (dashT > 0) {
            dashT -= dt;
            vx = dashDir * dashSpeed;
            vy = 0;
            updateDash(lv);
            if (hitWall) dashT = 0;
            if (dashT <= 0) vx = dashDir * dashSpeed * 0.25f;
            trailT -= dt;
            if (trailT <= 0) { trailT = 0.03f; lv.ps.spawn(x, y - bh / 2, 0, 0, 0.3f, 4, 0, cls.color1, true); }
        } else {
            boolean free = (state == IDLE || state == RUN || state == AIR) && !frozenNow;
            if (state == ATK && !onGround && !frozenNow) free = true;   // control aereo al atacar
            float target = free ? mx * spd : 0;
            if (state == ATK && onGround) target = 0;
            if (state == ROLL) target = vx;   // gestionado por updateRoll
            if (state != ROLL) {
                float acc = (onGround ? 1500f : 950f) * dt;
                if (state == ATK && onGround) acc = 500f * dt;
                if (state == HURT) acc = 0;
                if (free && mx != 0) acc *= 1.4f;
                vx = Mth.approach(vx, target, acc);
            }
            if (free && mx != 0) right = mx > 0;
            if (free || state == ROLL) {
                // salto
                if (onGround) { coyote = 0.17f; jumpsLeft = s.extraJumps; } else coyote -= dt;
                if (ctl && !frozenNow && state != ROLL && onOneWay && onGround && in.pressed(Input.B_DOWN)) {
                    dropT = 0.25f; y += 2; jumpBuf = 0; onGround = false; onOneWay = false;
                    lv.fx("fx_dust", "land", x, y - 2, 0.6f, 0, 0);
                }
                if (jumpBuf > 0 && ctl && !frozenNow && state != ROLL) {
                    if (in.held(Input.B_DOWN) && onOneWay) {
                        dropT = 0.25f; y += 2; jumpBuf = 0; onGround = false; onOneWay = false;
                    } else if (coyote > 0) {
                        doJump(lv, false);
                    } else if (jumpsLeft > 0 && !(vy > 0 && lv.groundBelow(x, y + 1) - y < 26)) {   // cerca del suelo: guarda el salto y se ejecuta al aterrizar (jump buffering)
                        jumpsLeft--;
                        doJump(lv, true);
                    }
                }
            } else {
                if (onGround) coyote = 0.17f;
            }
            if (jumping && vy < -120 && !in.held(Input.B_JUMP) && !in.pressed(Input.B_JUMP)) { vy *= 0.5f; jumping = false; }
            if (vy >= 0) jumping = false;
            vy = Math.min(Level.FALL_MAX, vy + Level.GRAV * dt);
        }
        if (extVx != 0) { vx += extVx; extVx = 0; }
        float pvy = vy;
        boolean wasGround = onGround;
        lv.move(this, dt);
        if (onGround && !wasGround && pvy > 180) {
            sq = Mth.clamp(pvy / 420f, 0.14f, 0.32f);
            Snd.sfxv("land", Mth.clamp(pvy / 400f, 0.3f, 0.9f));
            BlessFx.onLand(lv, pvy);
            lv.fx("fx_dust", "land", x, y - 2, 1f, 0, 0);
            if (state == AIR) state = IDLE;
        }
        if (onGround && (state == AIR)) state = IDLE;
        if (!onGround && state == IDLE || !onGround && state == RUN) state = AIR;
        if (onGround && (state == IDLE || state == RUN)) state = Math.abs(vx) > 12 && mx != 0 ? RUN : IDLE;
        prevVy = vy;

        // ---- animacion segun estado (los estados con animacion propia la gestionan ellos mismos)
        if (pendT > 0) { pendT -= dt; if (pendT <= 0) pendReact = null; }
        if (state != IDLE) { actName = null; idleT = 0; stillT = 0; holdT = 0; impAt = 14f; }   // cualquier accion importante corta al instante la animacion decorativa
        switch (state) {
            case IDLE: updateIdleLife(lv, dt, mx); break;
            case RUN: setAnim("run"); animT += dt * Mth.clamp(Math.abs(vx) / 120f, 0.7f, 1.4f); footsteps(lv); runDust(lv, dt); break;
            case AIR: setAnim(vy < 0 ? "jump" : "fall"); animT += dt; break;
            default: break;
        }

        if (chargeT >= ChargeCfg.TAP && (state == IDLE || state == RUN || state == AIR)) chargePose();

        // ---- seguridad: pinchos / foso
        checkHazards(lv, dt);
        // ---- guardia de acero
        if (guardT > 0) updateGuard(lv, dt);
        // ---- bloqueo de vasijas al caminar no aplica
    }

    // ------------------------------------------------------------------ vida propia: reposos con personalidad y reacciones
    private float cosF() { cosSeed ^= cosSeed << 13; cosSeed ^= cosSeed >>> 17; cosSeed ^= cosSeed << 5; return (cosSeed & 0xFFFFFF) / (float) 0x1000000; }

    /** Hoja con la que se dibuja la animacion actual. */
    public Sheet curSheet() { return sheetX != null && sheetX.has(animName) ? sheetX : sheet; }

    @Override public Anim anim() { return curSheet().anim(animName); }

    /**
     * Reaccion a un suceso (chest, awe, touch, victory). Solo cosmetica: si el personaje esta ocupado y queueSecs > 0 se
     * guarda unos segundos y se reproduce cuando quede quieto; cualquier movimiento o accion la corta al instante.
     */
    public void react(String name, float queueSecs) {
        if (!alive || sheetX == null || !sheetX.has(name)) return;
        if (state == IDLE && onGround) startAct(name);
        else if (queueSecs > 0) { pendReact = name; pendT = queueSecs; }
    }

    /** Solo para pruebas (DebugBot): lanza una animacion decorativa concreta; false si la hoja no la tiene. */
    public boolean debugAct(String name) {
        if (sheetX == null || !sheetX.has(name)) return false;
        startAct(name); return true;
    }

    private void startAct(String name) {
        actName = name; animName = name; animT = 0; holdT = 0; pendReact = null;
        actHold = name.equals("victory") ? 2.6f : name.equals("awe") ? 0.35f : name.equals("chest") ? 0.25f : 0f;
    }

    private void updateIdleLife(Level lv, float dt, float mx) {
        boolean pressedAny = false;
        for (int b = 0; b < Input.B_COUNT; b++) if (b != Input.B_PAUSE && lv.in.pressed(b)) { pressedAny = true; break; }
        boolean still = mx == 0 && !guarding && !frozen() && onGround && Math.abs(vx) < 12 && alive && !pressedAny;
        if (!still) {          // se mueve, guarda o queda congelado: vuelve al reposo normal de inmediato
            actName = null; idleT = 0; stillT = 0; impAt = 14f;
            setAnim("idle"); animT += dt;
            return;
        }
        if (actName == null && pendReact != null && pendT > 0) startAct(pendReact);
        if (actName != null) {
            animName = actName; animT += dt;
            Anim a = sheetX.anim(actName);
            if (a.done(animT)) {
                holdT += dt;
                if (holdT >= actHold) { actName = null; idleT = 0; idleNext = 3.5f + cosF() * 5f; setAnim("idle"); animT = 0; }
            }
            return;
        }
        boolean weary = lv.rs.hp > 0 && lv.rs.hp / Math.max(1f, lv.rs.stats.maxHp) < 0.3f;
        boolean hasWeary = sheetX != null && sheetX.has("weary");
        if (weary && hasWeary) { setAnim("weary"); actName = null; animT += dt; idleT = 0; return; }
        setAnim("idle"); animT += dt;
        if (sheetX == null) return;
        boolean calm = !lv.cinematic && !lv.bossFight && lv.nearestEnemy(x, y, 150, true) == null && hurtT <= 0;
        if (!calm) { idleT = 0; stillT = 0; return; }
        idleT += dt; stillT += dt;
        if (idleT < idleNext) return;
        Anim ia = sheet.anim("idle");
        if (ia.frameAt(animT) != 0 && idleT < idleNext + 1.2f) return;      // empieza al comienzo del ciclo de respiracion: sin saltos
        int pick;
        if (stillT > impAt) { pick = IMP; impAt = stillT + 11f + cosF() * 8f; }      // mucho rato quieto: impaciencia, de vez en cuando
        else {      // las otras 9 (todas menos la de impaciencia), sin repetir la ultima
            int pool = IDLES.length - 1;
            int r = Math.min(pool - 1, (int) (cosF() * pool));
            pick = r >= IMP ? r + 1 : r;
            if (pick == lastIdle) { r = (r + 1) % pool; pick = r >= IMP ? r + 1 : r; }
        }
        lastIdle = pick; idlePicks++;
        startAct(IDLES[pick]);
    }

    // ------------------------------------------------------------------ salto, rodar, pocion
    private void doJump(Level lv, boolean air) {
        vy = air ? -360f : -410f;
        if (state == ATK) { state = AIR; }
        onGround = false; jumping = true; jumpBuf = 0; coyote = 0;
        animT = 0;
        BlessFx.onJump(lv, air);
        sq = air ? -0.16f : -0.24f;
        if (air) {
            Snd.sfx("double_jump", 0.8f);
            lv.fx("fx_ring", "pulse", x, y - 4, 0.35f, 0xFFFFFF, Platform.ADD | Platform.TINT);
            lv.ps.burst(lv.rng, x, y - 2, 0xFFFFFF, 8, 70, 0.3f, 2, 0, true);
        } else {
            Snd.sfxv("jump", 0.7f);
            lv.fx("fx_dust", "land", x, y - 2, 0.8f, 0, 0);
        }
    }

    private boolean tryRoll(Level lv, float mx) {
        if (state == ROLL || state == ULT || frozen()) return false;
        if (rollCd > 0 || state == SKILL || state == HURT) return false;
        if (mx != 0) right = mx > 0;
        state = ROLL; animName = "roll"; animT = 0;
        vx = dir() * 215f * Math.max(0.9f, lv.rs.stats.speedMul);
        swingHit.clear();
        rollCd = 0.12f;
        Snd.sfxv("roll", 0.8f);
        lv.fx("fx_dust", "roll", x, y - 2, 1f, 0, 0).right = right;
        atkBuf = 0;
        BlessFx.onRoll(lv, false);
        return true;
    }

    private void updateRoll(Level lv, float dt) {
        Stats s = lv.rs.stats;
        float rk = 1f + Math.min(0.6f, BlessFx.sv(lv.rs, BRule.M_ROLLCDR));   // bendiciones: rodada mas rapida
        animT += dt * rk;
        vx = dir() * 215f * Math.max(0.9f, s.speedMul) * (animT < 0.25f ? 1f : 0.6f) * rk;
        if (!onGround) vx *= 0.9f;
        lv.breakRect(x + dir() * 8 - 8, y - bh, 16, bh, 1);
        trailT -= dt;
        if (trailT <= 0) {
            trailT = 0.05f;
            if (s.shadowRoll > 0 || s.fantasma > 0) lv.fx("fx_shadow", "puff", x, y - 14, 0.7f, 0x6030A0, Platform.ADD | Platform.TINT);
        }
        if (s.shadowRoll > 0) {
            for (Ent e : lv.enemiesInBox(x - 10, y - bh, 20, bh)) {
                if (swingHit.add(e)) {
                    lv.damageEnemy(e, baseDmg(lv) * (0.8f + 0.5f * s.shadowRoll), false, dir() * 90, -40);
                    Snd.sfxv("hit_magic", 0.6f);
                }
            }
        }
        if (s.fantasma > 0 && ((int) (animT * 14)) != lastFrame) {
            lastFrame = (int) (animT * 14);
            lv.explosion(x, y - 14, 26, baseDmg(lv) * 0.35f * s.fantasma, 60, -1, 0, 0, true);
        }
        Anim a = sheet.anim("roll");
        if (a.done(animT)) {
            state = onGround ? IDLE : AIR;
            vx *= 0.4f;
            BlessFx.onRoll(lv, true);
            if (s.egida > 0) { shield = Math.min(40, shield + 9 * s.egida); lv.fx("fx_shield", "bubble", x, y - 20, 0.8f, 0, 0); }
            comboWin = 0;
        }
    }

    private void drinkPotion(Level lv) {
        RunState rs = lv.rs;
        if (rs.potions <= 0 || rs.hp >= rs.stats.maxHp) { Snd.sfx("skill_fail", 0.6f); return; }
        rs.potions--;
        Snd.sfx("potion", 0.9f);
        lv.healPlayer(rs.stats.maxHp * 0.4f);
        BlessFx.onPotion(lv);
        lv.fx("fx_heal", "rise", x, y - 12, 1f, 0, 0);
        lv.ps.burst(lv.rng, x, y - 14, 0x6AE08A, 14, 70, 0.6f, 2, 0, true);
    }

    // ------------------------------------------------------------------ ataque
    private void startAttack(Level lv) { startAttack(lv, 0f); }

    /** held = segundos de carga (0 = ataque normal). */
    private void startAttack(Level lv, float held) {
        atkBuf = 0;
        swingCharged = held >= ChargeCfg.TAP;
        chgMul = swingCharged ? ChargeCfg.mul(held) : 1f;
        chgFrac = swingCharged ? ChargeCfg.frac(held) : 0f;
        swingHit.clear();
        swingFx = false;
        state = ATK;
        if (!onGround) { animName = "airatk"; combo = 0; }
        else {
            combo = (comboWin > 0 && combo > 0 && combo < 3 && !swingCharged) ? combo + 1 : 1;
            animName = swingCharged ? "attack3" : "attack" + combo;      // el cargado usa la animacion pesada; la logica de combo sigue siendo la del primer golpe
        }
        animT = 0;
        // dirigir hacia el enemigo mas cercano si el toque no indica direccion
        Ent n = lv.nearestEnemy(x, y, 70, true);
        if (n != null && Math.abs(vx) < 20 && Math.abs(n.x - x) < 60) right = n.x >= x;
        float lunge = cls.lunge * 2.6f;
        if (onGround) vx = dir() * lunge;
        else vx = dir() * (lunge * 0.5f);
        String type = cls.weaponType;
        String sfx = onGround ? "swing_" + type + "_" + (swingCharged ? 3 : combo) : "swing_air";
        Snd.sfxv(sfx, swingCharged ? 0.85f + 0.15f * chgFrac : 0.85f);
    }

    /** Contacto real de un golpe de arma secundaria: pose de impacto (solo visual). */
    void registerHitPose(Level lv, int kind) { hitPoseAt = lv.time; hitPoseKind = kind; }

    private float atkSpeed(Level lv) { return cls.atkSpeed * lv.rs.stats.atkSpd * BlessFx.atkSpdMul(lv) * (lv.flowT > 0 ? 1.12f : 1f) * (1f + 0.03f * Math.min(furia, 6)); }

    private void updateAttack(Level lv, float dt, float mx, float spd) {
        Anim a = sheet.anim(animName);
        animT += dt * atkSpeed(lv);
        // evitar caer inmediatamente al suelo en ataque aereo -> mantiene estado hasta terminar
        if (a.hitActive(animT)) {
            if (!swingFx) { swingFx = true; slashFx(lv); }
            if (a.worldBox(x, y, right, box)) hitBox(lv, a);
        }
        if (onGround && Math.abs(vx) > 5 && a.frameAt(animT) > (a.h1 < 0 ? 2 : a.h0)) vx *= 0.8f;
        boolean past = a.h1 >= 0 ? a.frameAt(animT) > a.h1 : animT > a.duration() * 0.6f;
        if (past && atkBuf > 0 && (combo > 0 && combo < 3 || !onGround)) {
            // encadena el siguiente golpe
            if (onGround) { comboWin = 1f; startAttack(lv); return; }
        }
        if (past && lv.in.pressed(Input.B_JUMP)) { /* salto cancela recuperacion */ state = onGround ? IDLE : AIR; comboWin = 0.3f; return; }
        if (a.done(animT)) {
            comboWin = 0.4f;
            state = onGround ? IDLE : AIR;
            if (!onGround) combo = 0;
        }
    }

    private void slashFx(Level lv) {
        String sheetName; String an;
        String t = cls.weaponType;
        float sc = 1f;
        int c = combo <= 0 ? 1 : combo;
        if (t.equals("dagger") || t.equals("stab")) { sheetName = "fx_stab"; an = c == 2 ? "s2" : "s1"; }
        else if (t.equals("great") || t.equals("hammer") || t.equals("scythe")) { sheetName = "fx_slash_big"; an = "s" + c; sc = 0.9f; }
        else { sheetName = "fx_slash_sword"; an = "s" + c; }
        if (animName.equals("airatk")) { an = "s1"; if (sheetName.equals("fx_stab")) an = "s1"; }
        if (swingCharged) { sc *= 1f + 0.7f * chgFrac; if (!sheetName.equals("fx_stab")) sheetName = "fx_slash_big"; if (sheetName.equals("fx_slash_big")) an = "s3"; }
        float fx = x + dir() * (sheetName.equals("fx_stab") ? 34 : 22), fy = y - 20;
        FxObj f = lv.fxAdd(sheetName, an, fx, fy, sc, cls.color1);
        if (f != null) { f.right = right; f.alpha = 0.95f; }
        FxObj g2 = lv.fx(sheetName, an, fx, fy, sc, 0, 0);
        if (g2 != null) { g2.right = right; g2.alpha = 0.55f; }
    }

    private String hitSfxFor(Ent e, boolean crit) {
        if (crit) return "hit_crit";
        if (e instanceof Enemy) {
            String d = ((Enemy) e).def.dieSfx;
            if (d.contains("bone")) return "hit_bone";
            if (d.contains("ghost") || d.contains("magic")) return "hit_magic";
            if (d.contains("slime")) return "hit_flesh_" + (1 + lv_i(3));
            return "hit_flesh_" + (1 + lv_i(3));
        }
        return "hit_stone";
    }

    private int lv_i(int n) { return (int) (Math.random() * n); }

    private void hitBox(Level lv, Anim a) {
        RunState rs = lv.rs; Stats s = rs.stats;
        float rch = BlessFx.reach(lv);
        if (rch != 1f) { float cxb = right ? box[0] : box[0] + box[2]; float nw = box[2] * rch; if (right) { box[2] = nw; } else { box[0] = cxb - nw; box[2] = nw; } }
        if (swingCharged && chgFrac > 0f) {       // golpe cargado: mas ancho y mas alto (el area crece con la carga)
            float ew = box[2] * ChargeCfg.REACH_BONUS * chgFrac, eh = box[3] * ChargeCfg.HEIGHT_BONUS * chgFrac;
            if (right) box[2] += ew; else { box[0] -= ew; box[2] += ew; }
            box[1] -= eh * 0.6f; box[3] += eh;
        }
        lv.breakRect(box[0], box[1], box[2], box[3], 1);
        List<Ent> list = lv.enemiesInBox(box[0], box[1], box[2], box[3]);
        lv.dmgSrc = BlessFx.SRC_W;
        for (Ent e : list) {
            if (swingHit.contains(e)) continue;
            swingHit.add(e);
            float mul = animName.equals("airatk") ? 1.0f : (combo == 3 ? 1.5f * BlessFx.finishMul(lv) : (combo == 2 ? 1.1f : 1f));
            if (combo == 3 && s.giant > 0) mul *= 1 + 0.4f * s.giant;
            if (swingCharged) { mul *= chgMul; dbgLastMul = chgMul; dbgChargedHits++; }      // el multiplicador de carga se aplica una sola vez por golpe (swingHit)
            float dmg = baseDmg(lv) * mul;
            if (cls.id == 1) {   // Acechador: por la espalda
                boolean away = (e.right == (e.x >= x));
                if (away) { dmg *= 1.5f; lv.text(e.x, e.y - e.bh - 12, "¡Espalda!", 0xC08CFF, false); }
            }
            if (s.eclipseCd > 0 && eclipseT <= 0) { dmg *= 2.5f; eclipseT = s.eclipseCd; lv.fx("fx_ring", "pulse", e.cx(), e.cy(), 0.6f, 0xFFE8A0, Platform.ADD | Platform.TINT); lv.text(e.x, e.y - e.bh - 20, "¡Eclipse!", 0xFFD25A, true); }
            boolean crit = lv.rollCrit(e);
            if (crit) dmg *= lv.critMulOf(e);
            int kind = Impact.kindOfWeapon(crit, combo);
            if (swingCharged && chgFrac >= ChargeCfg.HEAVY_FROM && kind < Impact.HEAVY) kind = Impact.HEAVY;
            boolean counter = lv.counterT > 0;
            if (counter) {      // contraataque tras parry/esquiva perfectos: +50 % de dano y golpe pesado (una sola vez)
                dmg *= 1.5f; lv.counterT = 0; if (kind < Impact.HEAVY) kind = Impact.HEAVY;
                lv.text(e.x, e.y - e.bh - 22, "¡Contra!", 0xFFFFFF, true);
                lv.fx("fx_ring", "pulse", e.cx(), e.cy(), 0.8f, 0xFFFFFF, Platform.ADD | Platform.TINT);
            }
            float kb = (cls.id == 7 ? 230f : 120f) * (kind == Impact.HEAVY || combo == 3 ? 1.6f : (kind == Impact.CRIT ? 1.2f : 1f)) * (1f + ChargeCfg.KNOCK_BONUS * chgFrac * (swingCharged ? 1f : 0f));
            lv.hitKind = kind;
            lv.damageEnemy(e, dmg, crit, dir() * kb, combo == 3 ? -140 : -50);
            lv.hitKind = 0;
            if (swingCharged && chgFrac >= ChargeCfg.STUN_FROM && e.alive && e instanceof Enemy) {      // aturde (no a jefes): el golpe cargado rompe el ritmo del enemigo
                float k = (chgFrac - ChargeCfg.STUN_FROM) / (1f - ChargeCfg.STUN_FROM);
                e.applyStatus(Ent.STUN, ChargeCfg.STUN_MIN + (ChargeCfg.STUN_MAX - ChargeCfg.STUN_MIN) * k, 1f);
            }
            lv.onWeaponHit(e, dmg, crit, combo);
            hitCount++;
            Impact.hit(lv, e, kind, dir(), !e.alive, hitSfxFor(e, crit));
            hitPoseAt = lv.time; hitPoseKind = kind;
            if (a.name.startsWith("attack")) {
                // contragolpe: pequeño retroceso
                vx -= dir() * 20;
            }
            // efectos de combo por bendiciones / clases
            if (s.wave > 0 && hitCount % 2 == 0) {
                Proj p = lv.proj(x + dir() * 14, y - 18, dir() * 280, 0, baseDmg(lv) * 0.6f * s.wave, true, "crescent", cls.color1);
                p.pierce = 3; p.life = 0.9f; p.trail = true; p.scale = 1.2f;
            }
            if (cls.id == 9 && hitCount % 3 == 0) {
                Proj p = lv.proj(x + dir() * 12, y - 20, dir() * 330, 0, baseDmg(lv) * 0.8f, true, "blade", cls.color1);
                p.pierce = 2; p.life = 0.8f;
            }
            if (combo == 3 && s.giant > 0) {
                Proj p = lv.proj(x + dir() * 10, y - 6, dir() * 220, 0, baseDmg(lv) * 0.8f, true, "crescent", 0xFFD25A);
                p.special = 1; p.pierce = 4; p.life = 0.7f;
            }
        }
        lv.dmgSrc = 0;
        // vasijas
        for (Prop pr : lv.props) {
            if (pr.kind.equals("pot") && !pr.open && Mth.overlap(pr.x - 6, pr.y - 14, 12, 14, box[0], box[1], box[2], box[3])) lv.breakPot(pr);
        }
    }

    // ------------------------------------------------------------------ dash
    private void updateDash(Level lv) {
        float r = 12;
        lv.breakRect(x + dashDir * 8 - 8, y - bh, 16, bh, 2);
        for (Ent e : lv.enemiesInBox(x - bw / 2 - r, y - bh, bw + r * 2, bh)) {
            if (dashHit.contains(e)) continue;
            dashHit.add(e);
            float dmg = skillBase(lv) * dashDmg;
            lv.dmgSrc = BlessFx.SRC_S;
            boolean crit = lv.rollCrit(e);
            if (crit) dmg *= lv.critMulOf(e);
            lv.damageEnemy(e, dmg, crit, dashDir * 150, -70);
            lv.dmgSrc = 0;
            if (dashStatus >= 0) e.applyStatus(dashStatus, dashSDur, 6f);
            if (dashHeal) lv.healPlayer(lv.rs.stats.maxHp * 0.04f);
            Impact.hit(lv, e, Impact.SPECIAL, dashDir, !e.alive, cls.key.equals("storm") ? "hit_shock" : "hit_metal_" + (1 + lv_i(2)));
        }
    }

    // ------------------------------------------------------------------ habilidades
    /** 0 = lanzada, 1 = bloqueada por el estado actual (se guarda en el buffer), 2 = descartada (enfriamiento / congelado). */
    private int trySkill(Level lv, int i) {
        RunState rs = lv.rs;
        if (state == ULT) return 2;
        if (state == ROLL || state == SKILL || state == HURT) return 1;
        if (rs.cd[i] > 0) { Snd.sfx("skill_fail", 0.5f); return 2; }
        if (frozen()) return 2;
        ClassDef.Skill sk = cls.skills[i];
        rs.cd[i] = sk.cd * rs.stats.cdMul;
        state = SKILL; animName = "skill"; animT = 0; skillIdx = i; skillFired = false;
        atkBuf = 0;
        if (onGround) vx *= 0.3f;
        Snd.sfx(sk.sfx, 0.9f);
        return 0;
    }

    private int tryUlt(Level lv) {
        RunState rs = lv.rs;
        if (state == ULT) return 2;
        if (state == ROLL || state == SKILL || state == HURT) return 1;
        if (rs.ult < 100f) { Snd.sfx("skill_fail", 0.5f); return 2; }
        if (frozen()) return 2;
        rs.ult = 0;
        state = ULT; animName = "ult"; animT = 0; skillIdx = 3; skillFired = false;
        lv.cinematic = true;
        invuln = 3f;
        vx = 0;
        atkBuf = 0;
        Snd.sfx(cls.skills[3].sfx, 1f);
        lv.flash(cls.color1, 0.25f);
        lv.shake(3f, 0.4f);
        lv.camTargetX = x; lv.camTargetY = y - 40; lv.camTargetZoom = 1.18f;
        lv.fxAdd("fx_ring", "pulse", x, y - 22, 1.2f, cls.color1);
        BlessFx.onUlt(lv, false);
        return 0;
    }

    /** Lanza la habilidad o definitiva en curso; todo el dano que cause cuenta como dano de habilidad para las bendiciones. */
    private void castSkills(Level lv) {
        int pv = lv.dmgSrc;
        lv.dmgSrc = BlessFx.SRC_S;
        try {
            if (state == ULT) Skills.ult(lv, this); else { Skills.cast(lv, this, skillIdx); BlessFx.onSkill(lv, skillIdx); }
        } finally { lv.dmgSrc = pv; }
    }

    private void updateCast(Level lv, float dt) {
        Anim a = sheet.anim(animName);
        animT += dt;
        if (state == ULT) { vx = 0; }
        if (!skillFired && a.rel >= 0 && a.frameAt(animT) >= a.rel) {
            skillFired = true;
            castSkills(lv);
        }
        if (state == SKILL && onGround && dashT <= 0) vx *= 0.85f;
        if (a.done(animT)) {
            if (!skillFired) { skillFired = true; castSkills(lv); }
            if (state == ULT) {
                BlessFx.onUlt(lv, true);
                lv.cinematic = false;
                lv.camTargetX = Float.NaN; lv.camTargetY = Float.NaN; lv.camTargetZoom = 1f;
                invuln = Math.max(invuln, 0.6f);
            }
            state = onGround ? IDLE : AIR;
        }
    }

    // ------------------------------------------------------------------ varios
    private void footsteps(Level lv) {
        int f = sheet.anim("run").frameAt(animT);
        if (f != lastFrame && (f == 1 || f == 5) && onGround) Snd.sfxv("step_" + (1 + lv_i(3)), 0.35f);
        lastFrame = f;
    }

    private void runDust(Level lv, float dt) {
        dustT -= dt;
        if (dustT <= 0 && onGround && Math.abs(vx) > 60) {
            dustT = 0.22f;
            FxObj f = lv.fx("fx_dust", "run", x - dir() * 6, y - 2, 0.8f, 0, 0);
            if (f != null) f.right = right;
        }
    }

    private int hazardN;
    public boolean guarding;
    public float parryT, parryCd, parryFlash;
    private float sq;                       // squash (+) / stretch (-)
    private static final class Ghost { Anim a; int f; float x, y, t; boolean r; }
    private final java.util.ArrayList<Ghost> ghosts = new java.util.ArrayList<>();
    private float lastGhost;

    /** Punto firme: suelo bajo ambos pies, sin pinchos cerca ni bordes de foso, con espacio libre encima. */
    private boolean isSafeSpot(Room rm, float px, float py) {
        if (py <= 0 || py >= rm.pixH - 2) return false;
        int tx0 = (int) Math.floor((px - 7) / Room.TS), tx1 = (int) Math.floor((px + 7) / Room.TS);
        int ty = (int) Math.floor((py + 1) / Room.TS);
        int t0 = rm.tile(tx0, ty), t1 = rm.tile(tx1, ty);
        if (!((t0 == Room.SOLID || t0 == Room.ONEWAY) && (t1 == Room.SOLID || t1 == Room.ONEWAY))) return false;
        for (int dx = -2; dx <= 2; dx++) {
            int a = rm.tile(tx0 + dx, ty), b = rm.tile(tx0 + dx, ty - 1), c = rm.tile(tx0 + dx, ty - 2);
            if (a == Room.AIR || a == Room.SPIKE || a == Room.SPIKE_DOWN) return false;
            if (b == Room.SPIKE || b == Room.SPIKE_DOWN || c == Room.SPIKE_DOWN) return false;
        }
        for (int dx = -2; dx <= 2; dx++) {
            int a = rm.tile(tx1 + dx, ty);
            if (a == Room.AIR || a == Room.SPIKE || a == Room.SPIKE_DOWN) return false;
        }
        // espacio libre para el cuerpo
        for (int k = 1; k <= 2; k++) {
            if (rm.tile(tx0, ty - k) == Room.SOLID || rm.tile(tx1, ty - k) == Room.SOLID) return false;
        }
        return true;
    }

    public void debugHazard(Level lv, float dt) { checkHazards(lv, dt); }
    private void checkHazards(Level lv, float dt) {
        Room rm = lv.room;
        if (onGround && y < rm.pixH - 2) {
            safeT -= dt;
            if (safeT <= 0) {
                safeT = 0.2f;
                if (isSafeSpot(rm, x, y)) { safeX = x; safeY = y; }
            }
        }
        boolean hazard = rm.hazardAt(x, y - 4) || rm.hazardAt(x - 5, y - 4) || rm.hazardAt(x + 5, y - 4) || rm.hazardAt(x, y - bh + 3) || y >= rm.pixH - 1;   // pies a +-5 px: el borde del pincho tambien pincha
        if (!hazard) hazardN = 0;
        if (hazard && state != ROLL || hazard && y >= rm.pixH - 1) {
            float dmg = 8 + lv.rs.stats.maxHp * 0.08f;
            if (invuln <= 0) lv.hurtPlayer(dmg, x, -1, 0);
            if (!alive) return;
            Snd.sfx("spikes", 0.8f);
            hazardN++;
            // el punto seguro puede ser invalido (p.ej. dentro del foso): usar la entrada de la sala
            if (hazardN > 1 || !isSafeSpot(rm, safeX, safeY)) {
                safeX = rm.spawnX; safeY = rm.spawnY;
                if (hazardN > 1 && !isSafeSpot(rm, safeX, safeY)) { /* ultimo recurso: spawn igualmente */ }
            }
            hurtT = 0; if (state == HURT) state = IDLE;
            x = safeX; y = safeY; vx = 0; vy = 0;
            lv.ps.burst(lv.rng, x, y - 12, 0xFFFFFF, 12, 80, 0.4f, 2, 0, true);
            invuln = Math.max(invuln, 1.1f);
            if (state == ROLL || state == ATK || state == SKILL) { state = IDLE; }
        }
    }

    private void updateGuard(Level lv, float dt) {
        // las espadas giratorias dañan a los cercanos
        if (((int) (lv.time * 4)) != ((int) ((lv.time - dt) * 4))) {
            for (Ent e : lv.enemiesIn(x, y - 14, 36)) {
                lv.damageEnemy(e, skillBase(lv) * 0.55f, false, Mth.sign(e.x - x) * 100, -30);
                Snd.sfxv("hit_metal_1", 0.5f);
                lv.fx("fx_hit", "spark", e.cx(), e.cy(), 0.8f, 0, 0);
            }
        }
    }

    // ------------------------------------------------------------------ dibujo
    public float parryPoseAt = -9f;
    private float hitPoseAt = -9f; private int hitPoseKind;     // ultimo contacto del arma propia (pose de impacto del jugador, solo visual)
    public void render(Platform.Gfx g, Level lv) {
        Sheet cs = curSheet();
        Anim a = cs.anim(animName);
        int frame = a.frameAt(animT);
        int flags = 0, tint = Status.tint(this);
        if (tint == 0 && skinTint != 0) tint = skinTint;
        if (tint != 0) flags |= Platform.TINT;
        float alpha = 1f;
        if (skinT > 0) { flags |= Platform.TINT; tint = 0xFFC090; }
        if (hitFlash > 0) { flags |= Platform.FLASH; tint = 0xFFFFFF; }
        if (invuln > 0 && !rolling() && state != ULT && alive) alpha = ((int) (lv.time * 18) & 1) == 0 ? 0.55f : 1f;
        if (state == ROLL && rolling()) alpha = 0.8f;
        // sombra
        if (onGround) g.rect(Math.round(x - 7), Math.round(y - 1), 14, 2, 0x55000000, false);
        if (guardT > 0) drawGuard(g, lv, false);
        if (dashT > 0) {   // estela
            cs.draw(g, a, frame, x - dashDir * 14, y, right, 1f, Platform.ADD | Platform.TINT, cls.color1, 0.4f);
            cs.draw(g, a, frame, x - dashDir * 7, y, right, 1f, Platform.ADD | Platform.TINT, cls.color1, 0.55f);
        }
        // imagenes residuales al rodar / esprintar / saltar en el aire
        if (alive && (state == ROLL || dashT > 0) && lv.time - lastGhost > 0.04f) {
            lastGhost = lv.time;
            Ghost gh = new Ghost(); gh.a = a; gh.f = frame; gh.x = x; gh.y = y; gh.t = lv.time; gh.r = right;
            ghosts.add(gh);
        }
        for (int i = ghosts.size() - 1; i >= 0; i--) {
            Ghost gh = ghosts.get(i);
            float age = lv.time - gh.t;
            if (age > 0.28f || age < 0) { ghosts.remove(i); continue; }
            sheet.draw(g, gh.a, gh.f, gh.x, gh.y, gh.r, 1f, Platform.ADD | Platform.TINT, cls.color1, 0.45f * (1f - age / 0.28f));
        }
        float runB = (state == RUN && onGround) ? 0.035f * (float) Math.abs(Math.sin(animT * 13f)) : 0f;
        float ssx = 1f + sq * 0.9f + runB, ssy = 1f - sq * 0.9f - runB;
        float ox = 0f;
        if (chargeFull && alive && !Save.S.reduceFx) ox = ((int) (lv.time * 36f) & 1) == 0 ? 0.8f : -0.8f;      // temblor de carga maxima
        float ia = lv.time - hitPoseAt;
        if (ia >= 0f && ia < 0.14f && state == ATK) {          // pose de impacto: el cuerpo se estira hacia el golpe y se asienta (el tiempo de juego se detiene en la pausa de impacto)
            float k = 1f - ia / 0.14f, amp = (hitPoseKind >= Impact.HEAVY ? 0.14f : 0.08f) * (Save.S.reduceFx ? 0.5f : 1f);
            ssx += amp * k; ssy -= amp * 0.7f * k; ox = dir() * 2.5f * amp * 10f * k;
        }
        float pa = lv.time - parryPoseAt;
        if (pa >= 0f && pa < 0.16f) {          // parry perfecto: el cuerpo absorbe el choque (compresion y retroceso breves)
            float k = 1f - pa / 0.16f, amp = 0.09f * (Save.S.reduceFx ? 0.5f : 1f);
            ssx -= amp * k; ssy += amp * 0.6f * k; ox -= dir() * 3f * k;
        } else if (wpnT > 0f) {                 // disparo del arma secundaria: ligero impulso hacia delante y vuelta
            float k = wpnT / 0.22f;
            ssx += 0.05f * k; ox += dir() * 1.5f * k;
        }
        if (a.smear >= 0 && frame == a.smear && state == ATK && !Save.S.reduceFx) {      // movimiento secundario del smear: ecos de la clase detras del tajo
            cs.draw(g, a, frame, x - dir() * 8, y, right, 1f, Platform.ADD | Platform.TINT, cls.color1, 0.30f);
            cs.draw(g, a, frame, x - dir() * 15, y, right, 1f, Platform.ADD | Platform.TINT, cls.color1, 0.16f);
        }
        if (!alive) { ssx = 1f; ssy = 1f; }
        boolean held = WeaponView.active(lv, this, cs);
        if (held) {            // secundaria elegida: espada a la espalda + cuerpo sin arma + secundaria en la mano
            Anim as = cs.anim(animName + "_s"), au = cs.anim(animName + "_u");
            int fu = Math.min(frame, au.n - 1);
            cs.drawSq(g, as, Math.min(frame, as.n - 1), x + ox, y, right, ssx, ssy, flags, tint, alpha);
            cs.drawSq(g, au, fu, x + ox, y, right, ssx, ssy, flags, tint, alpha);
            WeaponView.drawHeld(g, lv, this, cs, au, fu, x + ox, y, ssx, ssy, flags, tint, alpha);
        } else cs.drawSq(g, a, frame, x + ox, y, right, ssx, ssy, flags, tint, alpha);
        if (chargeT >= ChargeCfg.TAP && alive) {          // aura progresiva sobre el personaje + barra de carga (pixel art, sin tapar al personaje)
            float fr = ChargeCfg.frac(chargeT);
            float pulse = 0.5f + 0.5f * (float) Math.sin(lv.time * (10f + 14f * fr));
            float aa = (0.08f + 0.20f * fr) * (0.6f + 0.4f * pulse) * (Save.S.reduceFx ? 0.5f : 1f);
            cs.draw(g, a, frame, x + ox, y, right, 1f, Platform.ADD | Platform.TINT, fr >= 1f ? 0xFFE070 : cls.color1, aa);
            UI.light(g, x + dir() * 12, y - 20, 7f + 9f * fr, fr >= 1f ? 0xFFE070 : cls.color1, 0.12f + 0.16f * fr);
            int bw0 = 26, bx0 = Math.round(x - bw0 / 2f), by0 = Math.round(y - bh - 10);
            g.rect(bx0 - 1, by0 - 1, bw0 + 2, 6, 0xFF101018, false);
            g.rect(bx0, by0, bw0, 4, 0xFF383848, false);
            g.rect(bx0, by0, Math.round(bw0 * fr), 4, fr >= 1f ? (pulse > 0.5f ? 0xFFFFF0A0 : 0xFFFFC030) : 0xFFFF9A3A, false);
            if (fr >= 1f) for (int i = 0; i < 4; i++) g.rect(bx0 + i * 6 + 2, by0 - 3, 2, 2, 0xFFFFF0A0, false);   // destellos de carga maxima
        }
        if (guarding) {
            int sc = Items.SH_COL[lv.rs.shield];
            float sx0 = x + dir() * 11, ph = parryT > 0 ? 1f : 0f;
            g.rect(Math.round(sx0 - 2), Math.round(y - 27), 4, 22, Mth.withAlpha(sc, 230), false);
            g.rect(Math.round(sx0 - 1), Math.round(y - 26), 2, 20, 0xFFE8E0D0, false);
            if (ph > 0) UI.light(g, sx0, y - 16, 26, 0xFFE070, 0.6f);
            else UI.light(g, sx0, y - 16, 16, sc, 0.25f);
        }
        if (guardT > 0) drawGuard(g, lv, true);
        if (shield > 0) {
            Sheet sh = Assets.fx("fx_shield");
            Anim sa = sh.anim("bubble");
            sh.drawCentered(g, sa, (int) (lv.time * 10) % sa.n, Math.round(x), Math.round(y - 18), 0, 1f, Platform.ADD, 0, 0.5f);
        }
        if (wpnT > 0 && alive && wpnId > 0 && wpnId < Items.SEC_COUNT && !held) {      // el arma 2ª se adelanta al disparar
            float f = wpnT / 0.22f;
            UI.iconC(g, Items.SEC_ICON[wpnId], x + dir() * (9 + 9 * (1f - f)), y - 19, 1f, Mth.clamp(f * 1.6f, 0f, 1f));
        }
        if (swapAnimT > 0 && alive && swapIcon != null) {                     // cambio de arma: el icono sube sobre la cabeza
            float f = swapAnimT / 0.32f;
            UI.iconC(g, swapIcon, x, y - bh - 10 - 8 * (1f - f), 1f, Mth.clamp(f * 1.8f, 0f, 1f));
        }
        if (state == ATK || state == SKILL) { /* nada extra */ }
    }

    private void drawGuard(Platform.Gfx g, Level lv, boolean front) {
        Sheet s = Assets.fx("fx_proj");
        Anim a = s.anim("blade");
        int n = 4;
        for (int i = 0; i < n; i++) {
            float ang = lv.time * 5f + i * 6.2832f / n;
            boolean isFront = Math.sin(ang) > 0;
            if (isFront != front) continue;
            float bx = x + (float) Math.cos(ang) * 28, by = y - 18 + (float) Math.sin(ang) * 8;
            s.drawCentered(g, a, a.frameAt(lv.time), Math.round(bx), Math.round(by), ang + 1.5708f, 1f, 0, 0, 1f);
        }
    }
}
