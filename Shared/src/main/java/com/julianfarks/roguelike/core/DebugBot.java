package com.julianfarks.roguelike.core;

/** Bot de pruebas para el banco de escritorio (--bot): navega menus y juega sin ayuda. No se usa en Android. */
public final class DebugBot {
    private final boolean[] held = new boolean[256];
    private int lastClassFrame = -999, lastAct;
    private int stuck, jumpUntil;
    private boolean seenRun, warped, pitDone, tpDone;
    private int warpFrame;
    private final java.util.HashSet<Object> done = new java.util.HashSet<>();
    private float lastX;
    private static String navPrep = "";
    public static int classId = System.getenv("BOT_CLASS") != null ? Integer.parseInt(System.getenv("BOT_CLASS")) : 0;
    static int sbStep = 0, sbT = 0; static String sbBase = "";
    static String sbSnap(Game g) {
        Save.S.write();
        StringBuilder b = new StringBuilder(g.P.store().get("save", ""));
        for (String k : new String[]{"run_auto", "run_0", "run_1", "run_2"}) b.append('|').append(g.P.store().get(k, ""));
        return b.toString();
    }
    static int contStep = 0, contK0, contB0, contR0, contC0, contT;
    static int infStep = 0, infT = 0, infT0 = -1;
    static boolean enemyDone;
    static String navLast = "";
    static int navCls = -1;
    public static boolean trace = System.getenv("BOT_TRACE") != null;
    public static boolean godMode = System.getenv("BOT_GOD") != null;

    private void hold(Game g, int code, boolean down) {
        if (held[code] != down) { held[code] = down; g.key(code, down); }
    }

    private void tap(Game g, int code) { g.key(code, true); g.key(code, false); }

    private boolean compDone, screenDone;

    // ---- prueba de la ventana de parry: BOT_PARRYTEST="escudo;t1:etiqueta;t2:etiqueta..." (t = fotogramas desde el inicio de la sala).
    // Inyecta un golpe real (Level.hurtPlayer, la misma via que usan enemigos, proyectiles y jefes) y registra si fue parry.
    private int ptStart = -1;
    private void parryStep(RunScreen rs, Level lv, Player p, int frame) {
        if (rs.fadeA > 0.05f) return;
        if (ptStart < 0) { ptStart = frame; System.out.println("PARRYSTART f=" + frame); }
        int t = frame - ptStart;
        String[] q = System.getenv("BOT_PARRYTEST").split(";");
        if (t <= 5) { lv.enemies.clear(); lv.toKill = 0; lv.cleared = true; rs.rs.shield = Integer.parseInt(q[0]); }
        for (int i = 1; i < q.length; i++) {
            String[] w = q[i].split(":");
            if (t != Integer.parseInt(w[0])) continue;
            p.invuln = 0; rs.rs.hp = rs.rs.stats.maxHp;
            int par = lv.parries; float hp = rs.rs.hp;
            lv.hurtPlayer(10, p.x + 12 * p.dir(), -1, 0);
            System.out.println("PARRYHIT shield=" + rs.rs.shield + " tag=" + w[1] + " parried=" + (lv.parries > par) + " dano=" + Math.round(hp - rs.rs.hp) + " guard=" + p.guarding + " parryT=" + p.parryT);
        }
    }

    // ---- pruebas de IA ante peligros: BOT_AITEST="escenario:id1,id2" (BOT_AIFRAMES = duracion). Reconstruye una zona de la sala (suelo, pinchos, puentes,
    // fosos), coloca enemigos reales a la izquierda y al jugador quieto a la derecha, y mide: golpes de pinchos, golpes al jugador, cercania, giros.
    private float aiPX, aiPY; private boolean aiBuilt; private int aiT0, aiG, aiC0;
    private final java.util.List<Enemy> aiEn = new java.util.ArrayList<>();
    private float[] aiMinP, aiMinS, aiLastX; private int[] aiFlips, aiLastDir, aiAttacks, aiPrevState; private int aiTrap0, aiHurt0, aiPlans0, aiHops0, aiBlocked0;
    private static void aiSet(Room rm, int x0, int y0, int x1, int y1, int t) { for (int x = x0; x <= x1; x++) for (int y = y0; y <= y1; y++) rm.set(x, y, t); }
    private void aiStep(Game g, RunScreen rs, Level lv, Player p, int frame) {
        String[] q = System.getenv("BOT_AITEST").split(":");
        String scen = q[0]; String[] ids = q[1].split(",");
        int dur = System.getenv("BOT_AIFRAMES") != null ? Integer.parseInt(System.getenv("BOT_AIFRAMES")) : 600;
        if (godMode) rs.rs.hp = rs.rs.stats.maxHp;
        Room rm = lv.room;
        if (!aiBuilt) {
            aiBuilt = true; aiT0 = frame;
            int G = Math.max(10, Math.round(p.y / 16f) - 6);
            int c0 = 4;
            int x1 = Math.min(rm.w - 4, c0 + 60);
            aiG = G; aiC0 = c0;
            aiSet(rm, c0, 1, x1, G - 1, Room.AIR);
            aiSet(rm, c0, G, x1, rm.h - 1, Room.SOLID);
            int C = c0;
            int pxTile = C + 28;
            switch (scen) {
                case "strip3": aiSet(rm, C + 20, G - 1, C + 22, G - 1, Room.SPIKE); break;
                case "contact": aiSet(rm, C + 20, G - 1, C + 22, G - 1, Room.SPIKE); break;
                case "strip1": aiSet(rm, C + 21, G - 1, C + 21, G - 1, Room.SPIKE); break;
                case "strip8": aiSet(rm, C + 19, G - 1, C + 26, G - 1, Room.SPIKE); pxTile = C + 32; break;
                case "bridge":
                    aiSet(rm, C + 19, G - 1, C + 24, G - 1, Room.SPIKE);
                    rm.set(C + 15, G - 1, Room.SOLID); aiSet(rm, C + 16, G - 2, C + 16, G - 1, Room.SOLID); aiSet(rm, C + 16, G - 2, C + 26, G - 2, Room.SOLID);
                    pxTile = C + 31; break;
                case "pit": aiSet(rm, C + 19, G, C + 27, G + 4, Room.AIR); aiSet(rm, C + 19, G + 5, C + 27, G + 5, Room.SPIKE); pxTile = C + 31; break;
                case "ledge": aiSet(rm, C + 19, G, C + 40, G + 2, Room.AIR); aiSet(rm, C + 19, G + 3, C + 40, rm.h - 1, Room.SOLID); break;
                case "safe": break;
                default: break;
            }
            lv.enemies.clear(); lv.projs.clear(); lv.toKill = 0; lv.cleared = true;
            p.x = pxTile * 16 + 8; p.y = G * 16; p.vx = p.vy = 0;
            if ("ledge".equals(scen)) p.y = (G + 3) * 16;
            aiPX = p.x; aiPY = p.y;
            aiEn.clear();
            for (int i = 0; i < ids.length; i++) {
                Enemy en = new Enemy(EnemyDef.get(ids[i]), false, 1f, 1f);
                en.x = (C + 14 - i * 3) * 16 + 8; en.y = G * 16; en.home = en.x;
                en.onHit(lv, 0, 0, 0); en.state = Enemy.CHASE;
                if ("contact".equals(scen)) { en.x = (C + 21) * 16 + 8; en.state = Enemy.PATROL; }
                lv.enemies.add(en); lv.toKill++; aiEn.add(en);
            }
            int n = aiEn.size();
            aiMinP = new float[n]; aiMinS = new float[n]; aiLastX = new float[n]; aiFlips = new int[n]; aiLastDir = new int[n]; aiAttacks = new int[n]; aiPrevState = new int[n];
            java.util.Arrays.fill(aiMinP, 1e9f); java.util.Arrays.fill(aiMinS, 1e9f);
            for (int i = 0; i < n; i++) aiLastX[i] = aiEn.get(i).x;
            aiTrap0 = Level.dbgTrapHits; aiHurt0 = Level.dbgHurt; aiPlans0 = Enemy.dbgPlans; aiHops0 = Enemy.dbgHops; aiBlocked0 = Enemy.dbgBlocked;
            rm.bake(g.P);
            System.out.println("AIT build " + scen + " G=" + G + " roomW=" + rm.w + " player@" + pxTile);
            return;
        }
        int t = frame - aiT0;
        p.vx = 0; p.x = aiPX; p.y = aiPY; p.vy = 0;
        for (int i = 0; i < aiEn.size(); i++) {
            Enemy en = aiEn.get(i);
            if (!en.alive) continue;
            aiMinP[i] = Math.min(aiMinP[i], Math.abs(en.x - p.x));
            float sx = 1e9f;
            for (int tx = 0; tx < rm.w; tx++) for (int ty = aiG - 1; ty >= aiG - 2; ty--) if (rm.tile(tx, ty) == Room.SPIKE) sx = Math.min(sx, Math.abs(en.x - (tx * 16 + 8)));
            aiMinS[i] = Math.min(aiMinS[i], sx);
            float mv = en.x - aiLastX[i]; aiLastX[i] = en.x;
            if (Math.abs(mv) > 0.15f) { int d = mv > 0 ? 1 : -1; if (aiLastDir[i] != 0 && d != aiLastDir[i]) aiFlips[i]++; aiLastDir[i] = d; }
            if (en.state != aiPrevState[i] && (en.state == Enemy.ATTACK || en.state == Enemy.CHARGE || en.state == Enemy.LEAP || en.state == Enemy.WINDUP)) aiAttacks[i]++;
            aiPrevState[i] = en.state;
        }
        if (System.getenv("BOT_AITRACE") != null && t % Integer.parseInt(System.getenv("BOT_AITRACE")) == 0) for (Enemy en : aiEn) System.out.println("AITR t=" + t + " " + en.def.id + " x=" + Math.round(en.x) + " vx=" + Math.round(en.vx) + " st=" + en.state + " g=" + en.onGround + " hp=" + Math.round(en.hp) + " " + en.dbgNav());
        if (t == dur) {
            for (int i = 0; i < aiEn.size(); i++) {
                Enemy en = aiEn.get(i);
                System.out.println("AIT " + scen + " id=" + ids[i] + " alive=" + en.alive + " hp=" + Math.round(en.hp) + "/" + Math.round(en.maxHp) + " x=" + Math.round(en.x / 16f) + " minDistPlayer=" + Math.round(aiMinP[i]) + " minDistSpike=" + Math.round(aiMinS[i]) + " flips=" + aiFlips[i] + " attacks=" + aiAttacks[i] + " state=" + en.state);
            }
            System.out.println("AIT " + scen + " TOTAL trapHits=" + (Level.dbgTrapHits - aiTrap0) + " playerHits=" + (Level.dbgHurt - aiHurt0) + " plans=" + (Enemy.dbgPlans - aiPlans0) + " hops=" + (Enemy.dbgHops - aiHops0) + " blocked=" + (Enemy.dbgBlocked - aiBlocked0) + " playerX=" + Math.round(p.x / 16f));
        }
    }

    // ---- prueba de pausa bajo carga: BOT_PAUSETEST="f1,f2,..." pulsa Esc en esos fotogramas (durante el combate con muchos efectos), mide cuanto
    // tarda en abrirse el menu, comprueba que la simulacion se detiene, guarda y recarga la partida (consistencia) y reanuda con Esc.
    private int ptOpenF = -1, ptReqF = -1, ptKeyUp = -1; private float ptTime0; private int ptEnemyHp0;
    private void pauseTestStep(Game g, RunScreen rs, Level lv, int frame) {
        if (ptKeyUp == frame) { g.key(27, false); ptKeyUp = -1; }
        int ov = rs.debugOv();
        if (ptReqF < 0 && ptOpenF < 0) {
            for (String q : System.getenv("BOT_PAUSETEST").split(",")) if (!q.isEmpty() && Integer.parseInt(q.trim()) == frame && ov == 0) { ptReqF = frame; g.key(27, true); ptKeyUp = frame + 2; }
        }
        if (ptReqF >= 0 && ov == RunScreen.OV_PAUSE) {
            ptOpenF = frame; ptTime0 = lv.time;
            System.out.println("PAUSE abre: pedida f=" + ptReqF + " abierta f=" + frame + " latencia=" + (frame - ptReqF) + " fotogramas particulas=" + lv.ps.count() + " fx=" + lv.fxs.size() + " proj=" + lv.projs.size());
            long t0 = System.nanoTime();
            boolean ok = RunSave.write(g.P, rs, 0);
            long ms = (System.nanoTime() - t0) / 1_000_000L;
            RunScreen ld = ok ? RunSave.load(g, 0) : null;
            System.out.println("PAUSE guardado ok=" + ok + " ms=" + ms + " recargable=" + (ld != null) + (ld != null ? " oro=" + rs.rs.gold + "->" + ld.rs.gold + " hp=" + Math.round(rs.rs.hp) + "->" + Math.round(ld.rs.hp) : ""));
            ptReqF = -1;
        }
        if (ptOpenF >= 0 && frame == ptOpenF + 60) {
            System.out.println("PAUSE simulacion detenida=" + (Math.abs(lv.time - ptTime0) < 1e-4) + " ov=" + ov);
            g.key(27, true); ptKeyUp = frame + 2;
        }
        if (ptOpenF >= 0 && frame == ptOpenF + 70) { System.out.println("PAUSE reanudada=" + (rs.debugOv() == 0) + " ov=" + rs.debugOv()); ptOpenF = -1; }
    }

    // ---- parry contra un jefe REAL (BOT_PARRYBOSS=1 reactivo | =0 control sin guardia). El bot juega como una persona: no ataca,
    // se acerca al jefe mirandole y, al ver que el jefe empieza su ataque (telegrafia), pulsa el escudo C. Registra ataques y parries.
    private int pbAtk, pbPrevState = -1, pbHoldUntil = -1, pbHits, pbLastLog;
    private int pbParries0 = -1;
    private void bossParryStep(Game g, RunScreen rs, Level lv, Player p, int frame) {
        boolean react = "1".equals(System.getenv("BOT_PARRYBOSS"));
        Boss b = lv.boss;
        if (b == null || !b.alive || rs.fadeA > 0.05f) return;
        if (pbParries0 < 0) pbParries0 = lv.parries;
        rs.rs.hp = rs.rs.stats.maxHp;      // el banco no debe morir a mitad de la medicion
        hold(g, 'J', false); hold(g, 'X', false);
        float dx = b.x - p.x;
        boolean near = Math.abs(dx) < 46;
        hold(g, 39, !near && dx > 0); hold(g, 37, !near && dx < 0);
        if (near && p.dir() * dx < 0) { hold(g, dx > 0 ? 39 : 37, true); }          // girarse hacia el jefe
        else if (near) { hold(g, 39, false); hold(g, 37, false); }
        if (b.state == Boss.ATTACK && pbPrevState != Boss.ATTACK && near) {
            pbAtk++;
            if (react) { hold(g, 'C', true); pbHoldUntil = frame + 28; }
        }
        pbPrevState = b.state;
        if (pbHoldUntil >= 0 && frame >= pbHoldUntil) { hold(g, 'C', false); pbHoldUntil = -1; }
        if (frame - pbLastLog >= 300) { pbLastLog = frame; System.out.println("BOSSPARRY f=" + frame + " ataques=" + pbAtk + " parries=" + (lv.parries - pbParries0) + " hp=" + Math.round(rs.rs.hp) + " estado=" + b.state + " cerca=" + near); }
    }

    // ---- prueba de animaciones de personalidad: el bot se queda quieto y registra que hace el personaje (BOT_PERSONA=idle|react)
    private int pStart = -1;
    private void personaStep(RunScreen rs, Level lv, Player p, int frame) {
        if (rs.fadeA > 0.05f) return;
        if (pStart < 0) pStart = frame;
        int t = frame - pStart;
        if (t <= 5) { lv.enemies.clear(); lv.toKill = 0; lv.cleared = true; lv.pl.invuln = 99f; }
        if (t % 10 == 0) System.out.println("PERSONA t=" + t + " f=" + frame + " cls=" + p.cls.key + " estado=" + p.state + " anim=" + p.animName + " act=" + p.actName + " frame=" + p.anim().frameAt(p.animT) + " hp=" + Math.round(rs.rs.hp));
        if ("all".equals(System.getenv("BOT_PERSONA"))) {      // lanza idle1..idle10 uno tras otro (170 fotogramas cada uno)
            int k = (t - 30) / 170;
            if (t >= 30 && (t - 30) % 170 == 0 && k < Player.IDLES.length) System.out.println("PERSONA_ALL k=" + k + " " + Player.IDLES[k] + " ok=" + p.debugAct(Player.IDLES[k]));
        }
        if ("react".equals(System.getenv("BOT_PERSONA"))) {
            if (t == 30) p.react("chest", 0f);
            if (t == 120) p.react("awe", 0f);
            if (t == 200) p.react("touch", 0f);
            if (t == 280) p.react("victory", 0f);
            if (t == 520) rs.rs.hp = rs.rs.stats.maxHp * 0.2f;     // poca vida -> postura cansada
            if (t == 700) rs.rs.hp = rs.rs.stats.maxHp;
        }
    }

    public void tick(Game g, int frame) {
        Screen s = g.cur;
        if (s == null || g.fadeDir == 1) return;
        if (System.getenv("BOT_COMP") != null && !compDone) {      // prueba: companero desbloqueado y elegido
            compDone = true; int n = Integer.parseInt(System.getenv("BOT_COMP"));
            Save.S.compMask = 7; Save.S.compSel = n;
            if (System.getenv("BOT_DEXFILL") != null) { int k = 0; for (EnemyDef d : Codex.enemies()) if (k++ % 3 != 2) Save.S.dex.add("e:" + d.id); Save.S.dex.add("b:0"); Save.S.dex.add("b:2"); Save.S.dex.add("v:1"); Save.S.dex.add("v:4"); Save.S.garden[0] = 2; Save.S.garden[1] = 4; Save.S.garden[2] = 1; }
        }
        if (s instanceof Ops && System.getenv("BOT_SCREEN") != null && !screenDone) {
            screenDone = true; String q = System.getenv("BOT_SCREEN");
            if (q.equals("retos")) { PrepScreen.infiniteMode = true; Save.S.infMods = 5; g.go(new CodexScreens.Challenges(g)); return; }
            if (q.equals("prepinf")) { Save.S.finalBeaten = true; PrepScreen.infiniteMode = true; Save.S.infMods = 5; g.go(new PrepScreen(g)); return; }
            g.go(q.equals("comp") ? new CodexScreens.Comp(g) : q.equals("garden") ? new CodexScreens.GardenScr(g) : new CodexScreens.CodexScr(g)); return;
        }
        if (s instanceof Screens.Title && System.getenv("BOT_EDITOR") != null) { g.go(new ControlsEditor(g, false)); return; }
        if (s instanceof Screens.Title && System.getenv("BOT_CODE") != null && !devOnce) {
            devOnce = true; cf = frame;
            String code = System.getenv("BOT_CODE");
            Save.S.devUnlocked = false;
            g.swap(new CodesScreen(g));
            return;
        }
        if (s instanceof CodesScreen && System.getenv("BOT_CODE") != null) {
            String code = System.getenv("BOT_CODE");
            if (frame == cf + 10) { for (char ch : code.toCharArray()) g.key(Character.toUpperCase(ch), true); }
            if (frame == cf + 20) { g.lastDevice = 1; g.key(10, true); System.out.println("DEV desbloqueado=" + Save.S.devUnlocked); }
            return;
        }
        if (s instanceof Screens.Title && System.getenv("BOT_DEV") != null && !devOnce) {
            devOnce = true;
            Save.S.devUnlocked = true;
            String[] q = System.getenv("BOT_DEV").split(":");
            java.util.List<DevScreens.Entry> list = q[0].equals("enemies") ? DevScreens.enemies(false) : q[0].equals("elites") ? DevScreens.enemies(true) : q[0].equals("bosses") ? DevScreens.bosses()
                    : q[0].equals("classes") ? DevScreens.classes() : q[0].equals("biomes") ? DevScreens.biomes() : q[0].equals("objects") ? DevScreens.objects() : null;
            if (q[0].equals("eco")) { Save.S.souls = 1000; g.swap(new DevScreens.Economy(g)); return; }
            if (list == null) { g.swap(new DevScreens.Menu(g)); return; }
            int ix = q.length > 1 ? Integer.parseInt(q[1]) : 0;
            DevScreens.Inspector ins = new DevScreens.Inspector(g, list, ix, q[0]);
            if (q.length > 2 && q[2].equals("arena")) ins.arena(); else g.swap(ins);
            return;
        }
        if (s instanceof Screens.Title && System.getenv("BOT_CINE") != null) { g.go(new Cinematic(g, Story.cine(System.getenv("BOT_CINE")), null)); return; }
        if (System.getenv("BOT_MAPVIEW") != null && s instanceof Screens.Title && !devOnce) {
            devOnce = true;
            String[] q = System.getenv("BOT_MAPVIEW").split(":");
            int bi = Integer.parseInt(q[0]); long sd = q.length > 1 ? Long.parseLong(q[1]) : 1;
            final java.util.List<Room> rl = new java.util.ArrayList<>();
            Rng rg = new Rng(sd);
            for (int i = 0; i < 2; i++) { Room rm = RoomGen.generate(Room.COMBAT, Biome.ALL[bi], rg, Biome.ALL[bi].tier, 1 + i); rm.bake(g.P); rl.add(rm); }
            g.swap(new Screen(g) {
                @Override void update(float dt) { }
                @Override void render(Platform.Gfx gg) {
                    gg.clear(0xFF101018);
                    float y = 2;
                    for (Room rm : rl) {
                        float sc = Math.min(W() / (float) rm.pixW, 0.5f);
                        if (rm.baked != null) gg.image(rm.baked, 0, 0, rm.baked.w, rm.baked.h, 0, Math.round(y), Math.round(rm.pixW * sc), Math.round(rm.pixH * sc), 0, 0, 1f);
                        gg.rect(rm.spawnX * sc - 2, y + (rm.spawnY - 24) * sc, 4, 24 * sc, 0xFF40FF40, false);
                        gg.rect(rm.exitX * sc - 2, y + (rm.exitY - 24) * sc, 4, 24 * sc, 0xFFFF4040, false);
                        for (Room.Spawn sp : rm.spawns) gg.rect(sp.x * sc - 1, y + (sp.y - 12) * sc, 3, 3, sp.elite ? 0xFFFFD25A : 0xFFFF8040, false);
                        for (Room.PropSpec pr : rm.props) if (pr.kind.equals("chest")) gg.rect(pr.x * sc - 1, y + (pr.y - 6) * sc, 4, 4, 0xFFC070FF, false);
                        y += rm.pixH * sc + 4;
                    }
                }
            });
            return;
        }
        if (frame == 1 && System.getenv("BOT_LANG") != null) I18n.set(Integer.parseInt(System.getenv("BOT_LANG")));
        if (System.getenv("BOT_NAVLOG") != null && !s.getClass().getName().equals(navLast)) { navLast = s.getClass().getName(); System.out.println("NAV frame=" + frame + " " + s.getClass().getSimpleName()); }
        if (System.getenv("BOT_NAVLOG") != null && s instanceof PrepScreen) { String d = ((PrepScreen) s).dbg(); if (!d.equals(navPrep)) { navPrep = d; System.out.println("PREP frame=" + frame + " " + d); } }
        if (System.getenv("BOT_NAVLOG") != null && s instanceof PrepScreen && Save.S.lastClass != navCls) { navCls = Save.S.lastClass; System.out.println("PREPCLS frame=" + frame + " " + navCls + " chosen=" + PrepScreen.chosenBlessing()); }
        if (System.getenv("BOT_TOOPS") != null && frame == Integer.parseInt(System.getenv("BOT_TOOPS")) && s instanceof RunScreen) g.go(new Ops(g));   // como "Menu principal" del pausa
        if (System.getenv("BOT_SHOW") != null) {
            String[] names = System.getenv("BOT_SHOW").split(",");
            if (frame % 60 == 50 && !PrepScreen.fitErrors.isEmpty()) { for (String e : PrepScreen.fitErrors) System.out.println("FIT " + e); PrepScreen.fitErrors.clear(); }
            if (frame % 60 == 5 && frame / 60 < names.length) {
                Save.S.devUnlocked = true; for (int i = 0; i < 10; i++) Save.S.classUnlocked[i] = true;
                String nm = names[frame / 60];
                if (nm.startsWith("prep:")) {   // prep:clase:bendicion1:b2:b3:elegida:companero
                    String[] q = nm.split(":");
                    Save.S.lastClass = Integer.parseInt(q[1]);
                    PrepScreen.debugOffer(new int[]{Integer.parseInt(q[2]), Integer.parseInt(q[3]), Integer.parseInt(q[4])}, Integer.parseInt(q[5]));
                    Companions.refresh(Save.S);
                    int cp = Integer.parseInt(q[6]); if (cp >= 0) Save.S.compMask |= 1 << cp; Companions.select(Save.S, cp);
                    nm = "prep";
                }
                if (nm.startsWith("class:")) { Save.S.lastClass = Integer.parseInt(nm.substring(6)); nm = "class"; }
                switch (nm) {
                    case "title": g.go(new Screens.Title(g)); break;
                    case "lang": g.go(new LanguageScreen(g)); break;
                    case "ops": g.go(new Ops(g)); break;
                    case "class": g.go(new ClassScreen(g)); break;
                    case "prep": g.go(new PrepScreen(g)); break;
                    case "shop": g.go(new ShopScreen(g)); break;
                    case "sanct": g.go(new SanctuaryScreen(g)); break;
                    case "stats": g.go(new OpsScreens.Stats(g)); break;
                    case "trophy": g.go(new OpsScreens.Trophy(g)); break;
                    case "options": g.go(new Screens.Options(g, false)); break;
                    case "video": g.go(new VideoScreen(g)); break;
                    case "credits": g.go(new Screens.Credits(g, false)); break;
                    case "load": g.go(new LoadScreen(g)); break;
                    case "codes": g.go(new CodesScreen(g)); break;
                    case "controls": g.go(new ControlsScreen(g)); break;
                    case "story": g.go(new StoryScreens.Historia(g, false)); break;
                    case "comp": g.go(new CodexScreens.Comp(g)); break;
                    case "garden": g.go(new CodexScreens.GardenScr(g)); break;
                    case "codex": g.go(new CodexScreens.CodexScr(g)); break;
                    case "retos": PrepScreen.infiniteMode = true; g.go(new CodexScreens.Challenges(g)); break;
                    default: break;
                }
            }
            return;
        }
        if (System.getenv("BOT_PRINTSTATS") != null && frame % 1500 == 700) {
            Save q = Save.S;
            System.out.println("STATS started=" + q.started + " rounds=" + q.rounds + " perfect=" + q.perfectRounds + " streak=" + q.bestStreak + " kills=" + q.kills + " chests=" + q.chestsOpened + " playS=" + q.playMs / 1000 + " losses=" + q.losses + " runs=" + q.runs);
        }
        if (s instanceof Screens.Title) {
            if (System.getenv("BOT_INTRO") == null) Save.S.story[Story.S_INTRO] = 1;
            if (seenRun && System.getenv("BOT_STAYTITLE") != null) return;
            if (frame % 20 == 0) { Screen.Hit h = ((Screens.Title) s).hits.get(0); s.touch(0, 0, h.x + 5, h.y + 5); s.touch(0, 2, h.x + 5, h.y + 5); }
            return;
        }
        if (s instanceof PrepScreen) {
            if (System.getenv("BOT_NOSTART") == null && System.getenv("BOT_PREPHOLD") == null && frame - lastClassFrame > 20) { lastClassFrame = frame; ((PrepScreen) s).botStart(); }
            return;
        }
        if (s instanceof Ops) {
            if (System.getenv("BOT_NOSTART") != null) { if (!unlockedAll) { unlockedAll = true; for (int i = 0; i < 10; i++) Save.S.classUnlocked[i] = true; Save.S.souls = Math.max(Save.S.souls, 5000); String rl = System.getenv("BOT_RELICS"); if (rl != null) { int n = Integer.parseInt(rl); for (int i = 0; i < 8; i++) Save.S.relics[i] = i < n; Save.S.finalBeaten = n >= 9; } } return; }
            if (System.getenv("BOT_SBTEST") != null) {
                if (sbStep == 0 && frame - lastClassFrame > 120) { lastClassFrame = frame; Save.S.lastClass = classId; ((Ops) s).startGame(); }
                else if (sbStep == 3 && frame - lastClassFrame > 60) {
                    sbStep = 4;
                    String now = sbSnap(g);
                    RunScreen again = RunSave.load(g, 0);
                    System.out.println("SBTEST tras salir: progreso igual=" + now.equals(sbBase) + " partida normal sigue en ranura 0=" + (again != null) + " RunSave.any=" + RunSave.any(g.P) + " pantalla=" + s.getClass().getSimpleName());
                    if (again != null) g.go(again);
                }
                return;
            }
            if (System.getenv("BOT_LOADRUN") != null && frame - lastClassFrame > 60) {
                lastClassFrame = frame;
                RunScreen lr = RunSave.load(g, RunSave.AUTO);
                System.out.println("LOADRUN resultado=" + (lr == null ? "null" : "ok"));
                if (lr != null) g.go(lr);
                return;
            }
            if (System.getenv("BOT_INF") != null && frame - lastClassFrame > 120) {
                lastClassFrame = frame;
                Save.S.finalBeaten = true;
                if (System.getenv("BOT_MODS") != null) Save.S.infMods = Integer.parseInt(System.getenv("BOT_MODS"));
                if (System.getenv("BOT_GEMS") != null) Save.S.gems = Integer.parseInt(System.getenv("BOT_GEMS"));
                if (System.getenv("BOT_KEEPCLASS") == null) Save.S.lastClass = classId;
                for (int i = 0; i < 10; i++) Save.S.classUnlocked[i] = true;
                ((Ops) s).startInfinite();
                return;
            }
            if (frame - lastClassFrame > 120) {
                lastClassFrame = frame;
                Save.S.souls = Math.max(Save.S.souls, 5000);
                for (int i = 0; i < 10; i++) Save.S.classUnlocked[i] = true;
                if (System.getenv("BOT_KEEPCLASS") == null) Save.S.lastClass = classId;
                ((Ops) s).startGame();
            }
            return;
        }
        if (s instanceof ClassScreen && System.getenv("BOT_NOSTART") != null) return;
        if (s instanceof ClassScreen) {
            ClassScreen cs = (ClassScreen) s;
            if (frame - lastClassFrame > 30) {
                lastClassFrame = frame;
                Save.S.souls = 5000;
                for (int i = 0; i < 10; i++) Save.S.classUnlocked[i] = true;
                Save.S.lastClass = classId;
                cs.hits.clear();
                game_start(g, cs);
            }
            return;
        }
        if (!(s instanceof RunScreen)) return;
        RunScreen rs = (RunScreen) s;
        seenRun = true;
        if (System.getenv("BOT_BLESSGRANT") != null) BlessProbe.buildStep(rs, frame);
        if (!classPrinted && System.getenv("BOT_PRINTCLASS") != null) { classPrinted = true; System.out.println("RUN clase=" + rs.cls.name + " bioma=" + (rs.rs.biome == null ? "?" : rs.rs.biome.name) + " stage=" + rs.rs.stage + " roomNo=" + rs.rs.roomNo + " kills=" + rs.rs.kills + " oro=" + rs.rs.gold + " infinite=" + rs.rs.infinite + " retos=" + rs.rs.mods + " revividas=" + rs.rs.revivesUsed + " streak=" + rs.rs.streak); }
        if (rs.lv == null) return;
        Level lv = rs.lv;
        Player p = lv.pl;
        if (System.getenv("BOT_PERF") != null && frame % 60 == 0) System.out.println("PERF f=" + frame + " en=" + lv.enemies.size() + " proj=" + lv.projs.size() + " fx=" + lv.fxs.size() + " txt=" + lv.texts.size() + " delayed=" + lv.delayed.size() + " part=" + lv.ps.count() + " props=" + lv.props.size() + " heapMB=" + (Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory()) / 1048576);
        if (System.getenv("BOT_TRAILER") != null && warped && frame > warpFrame + 30) TrailerProbe.step(g, rs, lv, p, frame);
        if (System.getenv("BOT_HUDTEST") != null && warped && frame > warpFrame + 30) { if (HudProbe.step(g, rs, lv, p, frame)) System.exit(HudProbe.fails == 0 ? 0 : 1); return; }
        if (System.getenv("BOT_EVENTTEST") != null && warped && frame > warpFrame + 30) { if (EventProbe.step(g, rs, frame)) System.exit(EventProbe.fails == 0 ? 0 : 1); return; }
        if (System.getenv("BOT_ARSENAL") != null && warped && frame > warpFrame + 30) { if (ArsenalProbe.step(g, rs, lv, p, frame)) System.exit(ArsenalProbe.fails == 0 ? 0 : 1); return; }
        if (System.getenv("BOT_COMBATTEST") != null && warped && frame > warpFrame + 30) { if (CombatProbe.step(g, rs, lv, p, frame)) System.exit(CombatProbe.fails == 0 ? 0 : 1); return; }
        if (System.getenv("BOT_BLESSTEST") != null && warped && frame > warpFrame + 30) { if (BlessProbe.step(g, rs, lv, p, frame)) System.exit(BlessProbe.fails == 0 ? 0 : 1); return; }
        if (System.getenv("BOT_AITEST") != null && warped && frame > warpFrame + 30) { aiStep(g, rs, lv, p, frame); return; }
        if (System.getenv("BOT_PAUSETEST") != null) pauseTestStep(g, rs, lv, frame);
        if (System.getenv("BOT_PERSONA") != null) { personaStep(rs, lv, p, frame); return; }
        if (System.getenv("BOT_PARRYTEST") != null) { parryStep(rs, lv, p, frame); return; }
        if (System.getenv("BOT_PARRYLOG") != null && frame % 300 == 0) System.out.println("PARRIES f=" + frame + " n=" + lv.parries + " hp=" + Math.round(rs.rs.hp) + " escudo=" + rs.rs.shield + " jefe=" + (lv.boss != null && lv.boss.alive));
        String warp = System.getenv("BOT_WARP");
        if (warp != null && !warped && rs.fadeA < 0.05f && frame > 150) {
            warped = true; warpFrame = frame;
            String[] w = warp.split(":");
            int b = w.length > 1 ? Integer.parseInt(w[1]) : 0;
            rs.rs.biome = Biome.ALL[b]; rs.rs.stage = Biome.ALL[b].tier;
            rs.rs.roomNo = w[0].equals("boss") ? 4 : 1;
            int type = w[0].equals("boss") ? Room.BOSS : w[0].equals("shop") ? Room.SHOP : w[0].equals("forge") ? Room.FORGE : w[0].equals("bless") ? Room.BLESSING
                    : w[0].equals("rest") ? Room.REST : w[0].equals("elite") ? Room.ELITE : w[0].equals("hub") ? Room.HUB : w[0].equals("treasure") ? Room.TREASURE : Room.COMBAT;
            rs.rs.gold = 400;
            if (w[0].startsWith("ev")) { int k = Integer.parseInt(w[0].substring(2)); rs.rs.curEvent = k; type = k == Events.TRIAL ? Room.ELITE : Room.EVENT; }
            rs.loadRoom(type);
            return;
        }
        if (System.getenv("BOT_PARRYBOSS") != null && warped && frame > warpFrame + 30) { bossParryStep(g, rs, lv, p, frame); return; }
        if (System.getenv("BOT_MERCHTEST") != null && warped && frame > warpFrame + 60) { merchStep(g, rs, lv, p, frame); return; }
        if (System.getenv("BOT_SECTEST") != null && (warp == null || (warped && frame > warpFrame + 20))) { secretStep(g, rs, lv, p, frame); return; }
        if (System.getenv("BOT_SPIKETEST") != null && !spikeDone && frame > 260) {
            spikeDone = true;
            Room rm = lv.room;
            int gy = (int) (p.y / Room.TS);
            int bx = (int) (p.x / Room.TS) + 8;
            for (int i = 0; i < 40; i++) for (int j = 1; j <= 25; j++) if (rm.tile(bx + i, gy - j) != Room.AIR) rm.set(bx + i, gy - j, Room.AIR);
            for (int i = 0; i < 40; i++) { rm.set(bx + i, gy, Room.SOLID); rm.set(bx + i, gy - 1, Room.AIR); }
            String[] ids = {"esqueleto", "zombi", "lobo_musgo", "escudero_hueso", "carbonero_forja", "caballero_osario", "esqueleto", "zombi", "escudero_hueso"};
            float[] hs = {20, 20, 60, 100, 140, 40, 80, 120, 150};
            lv.enemies.clear(); lv.toKill = 0;
            for (int i = 0; i < ids.length; i++) {
                // fila de pinchos individual bajo cada enemigo
                int tx = bx + 2 + i * 4;
                rm.set(tx, gy - 1, Room.SPIKE); rm.set(tx + 1, gy - 1, Room.SPIKE);
                EnemyDef ed = EnemyDef.get(ids[i]);
                Enemy en = new Enemy(ed, false, 1f, 1f);
                en.x = (tx + 1) * Room.TS; en.y = gy * Room.TS - 16 - hs[i]; en.home = en.x;
                lv.enemies.add(en); lv.toKill++;
                spikeEn.add(en);
            }
            System.out.println("SPIKETEST: " + ids.length + " enemigos sobre pinchos, suelo fila " + gy);
        }
        if (!spikeEn.isEmpty() && frame % 120 == 0 && frame > 300) {
            int ok = 0;
            for (Enemy en : spikeEn) { if (en.hp < en.maxHp || !en.alive) ok++; else System.out.println("  sin dano: " + en.def.id + " y=" + Math.round(en.y)); }
            System.out.println("SPIKETEST frame " + frame + ": danados/muertos " + ok + "/" + spikeEn.size());
        }
        if (System.getenv("BOT_SBTEST") != null) {
            if (!rs.sandbox && sbStep == 0 && frame > 700) {
                sbStep = 1; sbT = frame;
                boolean w0 = RunSave.write(g.P, rs, 0), wa = RunSave.write(g.P, rs, RunSave.AUTO);
                System.out.println("SBTEST normal: guardar ranura0=" + w0 + " auto=" + wa + " cargable=" + (RunSave.load(g, 0) != null));
                RunScreen ld = RunSave.load(g, 0);
                if (ld != null) System.out.println("SBTEST ronda: companero " + rs.rs.companion + "->" + ld.rs.companion + " pactos " + rs.rs.pactCount() + "->" + ld.rs.pactCount() + " curEvent " + rs.rs.curEvent + "->" + ld.rs.curEvent + " inicio " + rs.rs.startBless + "->" + ld.rs.startBless + " vidaMax " + Math.round(rs.rs.stats.maxHp) + "->" + Math.round(ld.rs.stats.maxHp));
                sbBase = sbSnap(g);
                g.go(RunScreen.sandbox(g, rs.cls, 0, null, false, 0, () -> new Ops(g)));
                return;
            }
            if (rs.sandbox && sbStep == 1 && frame > sbT + 150) {
                sbStep = 2;
                System.out.println("SBTEST arena: esTest=" + rs.isTestSession() + " session=" + rs.rs.session);
                boolean a = RunSave.write(g.P, rs, 0), b = RunSave.write(g.P, rs, RunSave.AUTO), c = RunSave.write(g.P, rs, 2), d = RunSave.write(g.P, rs, 7);
                System.out.println("SBTEST arena: write directo ranura0=" + a + " auto=" + b + " ranura2=" + c + " ranura7=" + d + " (todas deben ser false)");
                rs.rs.sandbox = false;               // intento de evadir: quitar un solo indicador
                boolean e1 = RunSave.write(g.P, rs, 0);
                rs.rs.sandbox = true; rs.sandbox = false;
                boolean e2 = RunSave.write(g.P, rs, 1);
                rs.sandbox = true;
                System.out.println("SBTEST arena: evasion quitando un indicador: rs.sandbox=false -> " + e1 + ", RunScreen.sandbox=false -> " + e2 + " (deben ser false)");
                RunSave.clearRun(g.P, rs);
                System.out.println("SBTEST arena: clearRun no borra la partida real: " + (RunSave.load(g, 0) != null));
                rs.debugOpenPause();
                System.out.println("SBTEST pausa (arena): " + rs.debugLabels());
                rs.debugForceSaveMenu();
                System.out.println("SBTEST pausa forzando menu de guardado: " + rs.debugLabels());
                System.out.println("SBTEST tocar 'Guardar partida' por la via interna: " + rs.debugTap("Guardar partida") + " (debe ser false: no existe)");
                rs.debugKillAll();
                System.out.println("SBTEST arena: tras matar jefe y enemigos, progreso igual=" + sbSnap(g).equals(sbBase));
                if (System.getenv("BOT_SBHOLD") != null) { rs.debugOpenPause(); sbStep = 9; return; }
                rs.debugOpenPause();
                System.out.println("SBTEST salir: tocar 'Salir del modo de prueba'=" + rs.debugTap("Salir del modo de prueba"));
                sbStep = 3; lastClassFrame = frame;
                return;
            }
        }
        if (System.getenv("BOT_INFTEST") != null && rs.rs.infinite) {
            if (infT0 < 0) infT0 = frame;
            int dt = frame - infT0;
            if (infStep == 0 && dt > 150) {
                infStep = 1; infT = frame;
                System.out.println("INFT f" + frame + " inicio: floor=" + rs.rs.floor + " power=" + rs.rs.power() + " bioma=" + rs.rs.biome.name + " stage=" + rs.rs.stage + " hpMul=" + rs.rs.enemyHpMul());
                rs.debugNextFloor();
            } else if (infStep == 1 && frame > infT + 200) {
                infStep = 2; infT = frame;
                System.out.println("INFT f" + frame + " tras subir de piso: floor=" + rs.rs.floor + " hecho=" + rs.rs.floorsDone + " power=" + rs.rs.power() + " bioma=" + rs.rs.biome.name + " hpMul=" + rs.rs.enemyHpMul() + " enemigos=" + lv.enemies.size());
            } else if (infStep >= 2 && infStep < 12 && infStep % 2 == 0 && frame > infT + 120) {
                infStep++; infT = frame;
                rs.rs.hp = 0; lv.playerDeath();
                System.out.println("INFT f" + frame + " muerte #" + (infStep / 2) + " (revividas usadas=" + rs.rs.revivesUsed + ", gemas=" + Save.S.gems + ")");
            } else if (infStep >= 3 && infStep < 12 && infStep % 2 == 1 && frame > infT + 240) {
                infStep++; infT = frame;
                boolean ovRev = rs.debugOv() == 9;
                System.out.println("INFT f" + frame + " tras morir: overlayRevivir=" + ovRev + " ov=" + rs.debugOv() + " esperando=" + rs.debugReviveWaiting());
                if (ovRev) {
                    boolean ok = rs.debugRevive(Infinite.Method.GEMS);
                    java.util.Map<String, Object> d = RunSave.read(rs.game.P, RunSave.AUTO);
                    System.out.println("INFT f" + frame + " revivir con gemas ok=" + ok + " revividas=" + rs.rs.revivesUsed + " gemas=" + Save.S.gems + " vivo=" + rs.lv.pl.alive + " hp=" + (int) rs.rs.hp + " guardado.revs=" + Json.i(d, "revs", -1) + " guardado.inf=" + Json.bool(d, "inf", false));
                } else {
                    System.out.println("INFT f" + frame + " FIN: infResult=" + (rs.infResult == null ? "null" : "pisos=" + rs.infResult.floors + " alcanzado=" + rs.infResult.reached + " puntaje=" + rs.infResult.score + " revividas=" + rs.infResult.revives) + " bestFloor=" + Save.S.infBestFloor + " infRuns=" + Save.S.infRuns + " runs=" + Save.S.runs + " losses=" + Save.S.losses);
                    infStep = 99;
                }
            }
        }
        if (System.getenv("BOT_CONTTEST") != null && !rs.rs.infinite && rs.sandbox == false && frame > 700 && contStep == 0) {
            contStep = 1;
            Save q = Save.S; int k0 = q.kills, b0 = q.bossKills, r0 = q.runs, c0 = q.classRuns[rs.cls.id];
            rs.rs.kills = 50; rs.rs.bossKills = 2;
            rs.debugWinCampaign();
            System.out.println("CONT tras victoria: kills +" + (q.kills - k0) + " (esperado 50) jefes +" + (q.bossKills - b0) + " (2) runs +" + (q.runs - r0) + " (1) wins=" + q.wins);
            rs.debugContinueInfinite();
            rs.rs.kills += 30; rs.rs.time += 100;
            System.out.println("CONT infinito iniciado: infinite=" + rs.rs.infinite + " floor=" + rs.rs.floor + " fromCampaign=" + rs.rs.infFromCampaign + " revives=" + rs.rs.revivesUsed + " ov=" + rs.debugOv());
            contK0 = k0; contB0 = b0; contR0 = r0; contC0 = c0; contT = frame;
        } else if (contStep == 1 && frame > contT + 150) {
            contStep = 2;
            rs.debugEnd();
            Save q = Save.S; Infinite.Result ir = rs.infResult;
            System.out.println("CONT fin infinito: kills perfil +" + (q.kills - contK0) + " (esperado 80) jefes +" + (q.bossKills - contB0) + " (2) runs +" + (q.runs - contR0) + " (1) classRuns +" + (q.classRuns[rs.cls.id] - contC0) + " (1) losses=" + q.losses + " infRuns=" + q.infRuns
                    + " resultado.kills=" + (ir == null ? -1 : ir.kills) + " (30) resultado.pisos=" + (ir == null ? -1 : ir.floors));
            rs.debugEnd();
            System.out.println("CONT endRun repetido: kills perfil +" + (q.kills - contK0) + " infRuns=" + q.infRuns + " (no debe cambiar)");
        }
        if (System.getenv("BOT_ROUNDTEST") != null && warped && frame > warpFrame + 90) {
            if (roundStep == 0) {         // ronda perfecta
                roundStep = 1; roundT = frame;
                lv.roomHits = 0;
                for (Enemy en : new java.util.ArrayList<>(lv.enemies)) en.die(lv);
                System.out.println("ROUNDTEST perfecta: enemigos matados, rewarded=" + lv.rewarded);
            } else if (roundStep == 1 && frame > roundT + 40) {
                int n = 0; for (Prop q : lv.props) if (q.kind.equals("chest") && q.roundChest) n++;
                int r0 = Save.S.rounds, pf0 = Save.S.perfectRounds;
                rs.completeRound(lv); rs.completeRound(lv);   // intento de duplicar
                int n2 = 0; for (Prop q : lv.props) if (q.kind.equals("chest") && q.roundChest) n2++;
                System.out.println("ROUNDTEST perfecta: cofres=" + n + " (esperado 2); tras repetir evento=" + n2 + " (esperado 2); rondas=" + r0 + " perfectas=" + pf0);
                roundStep = 2; roundT = frame; rs.loadRoom(Room.COMBAT);
            } else if (roundStep == 2 && frame > roundT + 60) {
                roundStep = 3; roundT = frame;
                lv.pl.invuln = 0; lv.hurtPlayer(5, lv.pl.x + 10, -1, 0);
                System.out.println("ROUNDTEST con dano: roomHits=" + lv.roomHits);
                for (Enemy en : new java.util.ArrayList<>(lv.enemies)) en.die(lv);
            } else if (roundStep == 3 && frame > roundT + 40) {
                int n = 0; for (Prop q : lv.props) if (q.kind.equals("chest") && q.roundChest) n++;
                System.out.println("ROUNDTEST con dano: cofres=" + n + " (esperado 1)  rondas=" + Save.S.rounds + " perfectas=" + Save.S.perfectRounds + " racha=" + rs.rs.streak);
                roundStep = 4;
            }
        }
        if (System.getenv("BOT_EVTRIAL") != null && warped) {
            if (roundStep == 0 && frame > warpFrame + 90) {
                roundStep = 1; roundT = frame;
                int n0 = lv.enemies.size();
                for (Enemy en : new java.util.ArrayList<>(lv.enemies)) en.die(lv);
                System.out.println("EVTRIAL: curEvent=" + rs.rs.curEvent + " tipo=" + lv.room.type + " enemigos=" + n0 + " (se matan todos)");
            } else if (roundStep == 1 && frame > roundT + 60) {
                int n = 0, prize = 0; for (Prop q : lv.props) if (q.kind.equals("chest") && q.roundChest) { n++; if ("Premio de la prueba".equals(q.label)) prize++; }
                int doors = 0; for (Prop q : lv.props) if (q.kind.equals("door")) doors++;
                System.out.println("EVTRIAL: cofres de ronda=" + n + " premio_prueba=" + prize + " (esperado 1) puertas=" + doors + " rondas=" + Save.S.rounds);
                roundStep = 2;
            }
        }
        String npcEnv = System.getenv("BOT_NPC");
        if (npcEnv != null && !npcDone && warped && frame > warpFrame + 60) {
            npcDone = true;
            rs.startTalk(lv.addProp(new Room.PropSpec("npc", p.x + 30, p.y, Integer.parseInt(npcEnv))));
        }
        if (rs.ov == RunScreen.OV_TALK) {
            if (frame % 45 == 0) {
                Screen.Hit pick = null;
                for (Screen.Hit h : rs.hits) if (!h.plain && !h.disabled) { pick = h; break; }
                if (pick != null) { rs.touch(0, 0, pick.x + 3, pick.y + 3); rs.touch(0, 2, pick.x + 3, pick.y + 3); }
                else tap(g, ' ');
            }
            return;
        }
        if (System.getenv("BOT_PIT") != null && !pitDone && frame > 200) {
            outer:
            for (int ty = 0; ty < lv.room.h; ty++) for (int tx = 0; tx < lv.room.w; tx++)
                if (lv.room.tile(tx, ty) == Room.SPIKE && lv.room.tile(tx, ty + 1) == Room.SOLID) {
                    pitDone = true; p.x = tx * 16 + 8; p.y = (ty + 1) * 16; p.vx = p.vy = 0;
                    System.out.println("PIT placed at " + tx + "," + ty);
                    break outer;
                }
            if (!pitDone && frame > 400) pitDone = true;
        }
        if (System.getenv("BOT_TP") != null && !tpDone && frame > 200 && (warp == null || (warped && frame > warpFrame + 90))) {
            tpDone = true;
            String[] q = System.getenv("BOT_TP").split(",");
            if (q[0].equals("secret")) { int[] sp = lv.room.secretSpots.get(Integer.parseInt(q[1])); p.x = sp[0] + (q.length > 2 ? Integer.parseInt(q[2]) : 0); p.y = sp[1]; }
            else { p.x = Float.parseFloat(q[0]) * 16 + 8; p.y = Float.parseFloat(q[1]) * 16; }
            p.vx = p.vy = 0; p.safeX = p.x; p.safeY = p.y;
            lv.snapCamera();
        }
        String be = System.getenv("BOT_ENEMY");   // banco de pruebas: aparecen estos enemigos junto al jugador
        if (be != null && !enemyDone && frame > 260 && (warp == null || (warped && frame > warpFrame + 100))) {
            enemyDone = true;
            int k = 0;
            for (String id : be.split(",")) {
                EnemyDef ed = EnemyDef.get(id.trim());
                if (ed == null) { System.out.println("BOT_ENEMY desconocido: " + id); continue; }
                Enemy en = new Enemy(ed, false, 1f, 1f);
                en.x = p.x + 90 + 45 * k; en.y = p.y; en.home = en.x;
                lv.enemies.add(en); lv.toKill++; k++;
            }
        }
        if (System.getenv("BOT_ITEMS") != null) {
            if (frame % 500 == 210) { int k = (frame / 500) % 4; rs.rs.sec = 1 + k; rs.rs.secAmmo = 9; rs.rs.gren = 1 + k; rs.rs.grenCount = 9; rs.rs.shield = k; rs.rs.special = 1 + k; rs.rs.recalc(); }
            if (frame % 45 == 0) tap(g, 'L');
            if (frame % 70 == 0) tap(g, 'G');
        }
        if (System.getenv("BOT_FREEZE") != null) { if (godMode) rs.rs.hp = rs.rs.stats.maxHp; return; }
        if (System.getenv("BOT_FAST") != null && lv.boss != null && lv.boss.alive && !lv.boss.invuln() && lv.boss.hp > 40 && rs.rs.time > 12f) lv.boss.hp = 40;
        if (godMode) { rs.rs.hp = rs.rs.stats.maxHp; }
        if (System.getenv("BOT_OVLOG") != null && rs.ov != 0 && rs.ovT < 0.02f) System.out.println("OVSTART ov=" + rs.ov + " frame=" + frame);
        switch (rs.ov) {
            case RunScreen.OV_BLESS:
                if (rs.ovT > 1.3f && System.getenv("BOT_TRAILER") == null) for (Screen.Hit h : rs.hits) { rs.touch(0, 0, h.x + 5, h.y + 5); rs.touch(0, 2, h.x + 5, h.y + 5); break; }
                return;
            case RunScreen.OV_CHEST:
                if (rs.ovT > 1.0f && System.getenv("BOT_CHESTSHOT") == null || rs.ovT > 6f) {
                    for (Screen.Hit h : rs.hits) if (h.tag == 1 && h.label == null) { for (int k = 0; k < 2; k++) { rs.touch(0, 0, h.x + 5, h.y + 5); rs.touch(0, 2, h.x + 5, h.y + 5); } break; }
                }
                return;
            case RunScreen.OV_SHOP: case RunScreen.OV_FORGE:
                if (rs.ovT > 2.0f) rs.back();
                return;
            case RunScreen.OV_EVENT:
                if (rs.ovT > 1.0f && System.getenv("BOT_EVSHOT") == null || rs.ovT > 6f) {
                    boolean did = false;
                    for (Screen.Hit h : rs.hits) if (h.label == null && h.tag >= 0 && h.tag < rs.evOpts.size() && rs.evOpts.get(h.tag).ok) { rs.touch(0, 0, h.x + 5, h.y + 5); rs.touch(0, 2, h.x + 5, h.y + 5); did = true; break; }
                    if (!did) rs.back();
                }
                return;
            case RunScreen.OV_PAUSE:
                if (rs.ovT > 0.5f && System.getenv("BOT_PAUSETEST") == null) rs.back();
                return;
            case RunScreen.OV_NONE: break;
            default: return;
        }
        if (!p.alive || lv.cinematic) { for (int i = 0; i < 256; i++) if (held[i]) hold(g, i, false); return; }
        // objetivo
        Ent target = null; float bd = 9999;
        for (Enemy e : lv.enemies) if (e.alive) { float d = Math.abs(e.x - p.x) + Math.abs(e.y - p.y) * 0.5f; if (d < bd) { bd = d; target = e; } }
        if (lv.boss != null && lv.boss.alive) { target = lv.boss; bd = Math.abs(lv.boss.x - p.x); }
        float tx = p.x, ty = p.y;
        boolean fight = false;
        if (target != null) { tx = target.x; ty = target.y; fight = true; }
        else {
            Prop best = null; float pd = 9999;
            for (Prop pr : lv.props) {
                if (pr.dead) continue;
                if (done.contains(pr)) continue;
                boolean want = pr.kind.equals("door") || pr.kind.equals("merchant") || pr.kind.equals("forge") || pr.kind.equals("fountain") || pr.kind.equals("portal") || (pr.kind.equals("altar") && !pr.used) || (pr.kind.equals("chest") && !pr.used && pr.arg != 3) || ((pr.kind.equals("spirit") || pr.kind.equals("shrine") || pr.kind.equals("cage") || pr.kind.equals("relic")) && !pr.done && !pr.used);
                if (!want) continue;
                float d = Math.abs(pr.x - p.x) + (pr.kind.equals("door") ? -50 : 0);
                if (d < pd) { pd = d; best = pr; }
            }
            if (best != null) { tx = best.x; ty = best.y; }
            else { tx = lv.room.exitX; ty = lv.room.exitY; }
            // recoger reliquias/botin cercano
            for (Pickup pk : lv.pickups) if (!pk.dead && pk.type == Pickup.RELIC) { tx = pk.x; ty = pk.y; }
        }
        float dx = tx - p.x;
        float ad = Math.abs(dx);
        boolean near = fight && ad < 36 && Math.abs(ty - p.y) < 50;
        boolean ranged = fight && target instanceof Boss && ad < 120;
        if (ad > (fight ? 28 : 10)) { hold(g, 'D', dx > 0); hold(g, 'A', dx < 0); }
        else { hold(g, 'D', false); hold(g, 'A', false); }
        // salto
        float dirx = dx > 0 ? 1 : -1;
        int aheadT = lv.room.tile((int) Math.floor((p.x + dirx * 14) / 16), (int) Math.floor((p.y + 4) / 16));
        int ahead2 = lv.room.tile((int) Math.floor((p.x + dirx * 30) / 16), (int) Math.floor((p.y + 4) / 16));
        boolean gap = p.onGround && ad > 20 && (aheadT == Room.AIR || aheadT == Room.SPIKE);
        boolean jump = gap || (p.hitWall && p.onGround) || (ty < p.y - 30 && p.onGround && frame % 20 == 0) || (frame % 97 == 0 && p.onGround);
        if (jump && frame > jumpUntil + 20) jumpUntil = frame + 22;
        hold(g, 'W', frame < jumpUntil);
        // ataque
        if (near || ranged) { if (frame % 6 == 0) tap(g, 'J'); }
        else hold(g, 'J', false);
        // habilidades
        if (fight && System.getenv("BOT_ULT") != null && frame % 300 == 100 && rs.rs.ult < 100) rs.rs.ult = 100;   // solo para grabar trailers
        if (fight && bd < 160) {
            for (int i = 0; i < 3; i++) if (rs.rs.cd[i] <= 0 && frame % 30 == i * 8) tap(g, new int[]{'U', 'I', 'O'}[i]);
            if (rs.rs.ult >= 100 && frame % 40 == 0) tap(g, 'P');
        }
        if (fight && frame % 83 == 0 && p.onGround) tap(g, 'K');
        if (rs.rs.hp < rs.rs.stats.maxHp * 0.4f && frame % 50 == 0) tap(g, 'Q');
        // interactuar
        if (!fight && frame % 15 == 0) {
            Prop n = lv.nearestInteractable();
            if (n != null) { tap(g, 'E'); if (!n.kind.equals("door") && !n.kind.equals("portal")) done.add(n); }
        }
        // atasco
        if (Math.abs(p.x - lastX) < 0.5f && !near) stuck++; else stuck = 0;
        lastX = p.x;
        if (stuck > 60) { tap(g, 'W'); if (stuck > 90) { tap(g, 'K'); stuck = 0; } }
    }

    // ---- prueba del mercader errante: piso con enemigos vivos -> tienda -> compra -> salir -> mismo piso (BOT_MERCHTEST=1 con BOT_EVENT=1)
    private int mst, mT; private Level mOrigin; private Prop mDoor;
    private final java.util.List<Enemy> mEn = new java.util.ArrayList<>();
    private float[] mPos; private float mHp, mGold; private int mKill, mRoomNo, mProps, mPotions;
    private boolean mFail;

    private void mchk(String what, boolean ok) { System.out.println("MERCHTEST " + (ok ? "ok   " : "FAIL ") + what); if (!ok) mFail = true; }

    private void mSnap(Level lv, RunScreen rs) {
        mPos = new float[mEn.size() * 3];
        for (int i = 0; i < mEn.size(); i++) { Enemy e = mEn.get(i); mPos[i * 3] = e.x; mPos[i * 3 + 1] = e.y; mPos[i * 3 + 2] = e.hp; }
        mHp = rs.rs.hp; mGold = rs.rs.gold; mKill = lv.toKill; mProps = lv.props.size();
    }

    private void merchStep(Game g, RunScreen rs, Level lv, Player p, int frame) {
        mT++;
        if (rs.fadeA > 0.05f && mst != 5 && mst != 1) return;
        switch (mst) {
            case 0: {
                if (lv.room.type != Room.COMBAT) return;
                mDoor = null;
                for (Prop q : lv.props) if (q.kind.equals("door") && q.event == Events.MERCHANT) mDoor = q;
                if (mDoor == null) { if (mT < 40) { rs.loadRoom(Room.COMBAT); return; } System.out.println("MERCHTEST: la sala no tiene puerta de mercader"); mst = 99; return; }
                mOrigin = lv; mEn.addAll(lv.enemies); mRoomNo = rs.rs.roomNo;
                rs.rs.hp = Math.max(30, rs.rs.stats.maxHp - 43); rs.rs.gold = 400;
                mchk("el piso tiene enemigos vivos y la salida principal bloqueada (toKill=" + lv.toKill + ", cleared=" + lv.cleared + ")", lv.toKill > 0 && !lv.cleared && mEn.size() > 0);
                boolean exitDoor = false; for (Prop q : lv.props) if (q.kind.equals("door") && q.event == 0) exitDoor = true;
                mchk("no hay puerta de salida al siguiente piso", !exitDoor);
                mPotions = rs.rs.potions;
                p.x = mDoor.x; p.y = mDoor.y; p.vx = p.vy = 0; lv.snapCamera();
                mst = 1; mT = 0; return;
            }
            case 1: {   // entrar: se guarda la ultima foto de la sala de origen mientras siga siendo la actual
                if (lv == mOrigin) { mSnap(lv, rs); p.x = mDoor.x; p.y = mDoor.y; p.vx = 0; if (mT % 10 == 0) tap(g, 'E'); return; }
                mchk("estamos en la sala de mercader (tipo EVENT, suceso mercader, origen guardado)", lv.room.type == Room.EVENT && rs.rs.curEvent == Events.MERCHANT && rs.rs.sideOrigin == Room.COMBAT);
                mchk("la entrada del mercader quedo marcada como visitada", mDoor.locked && mDoor.done);
                mst = 2; mT = 0; return;
            }
            case 2: {
                Prop m = null; for (Prop q : lv.props) if (q.kind.equals("merchant")) m = q;
                if (m == null) { mchk("hay un mercader en la tienda", false); mst = 99; return; }
                p.x = m.x - 12; p.y = m.y; p.vx = 0;
                if (rs.ov == RunScreen.OV_SHOP) { mst = 3; mT = 0; return; }
                if (mT % 10 == 0) tap(g, 'E'); return;
            }
            case 3: {
                float g0 = rs.rs.gold; RunScreen.ShopItem pick = null;
                for (RunScreen.ShopItem it : rs.shop) if (!it.sold && it.cost <= g0) { pick = it; break; }
                mchk("hay algo que comprar", pick != null);
                if (pick != null) { int pot0 = rs.rs.potions; rs.buy(pick); mchk("la compra resta oro (" + (int) g0 + " -> " + (int) rs.rs.gold + ") y marca vendido", rs.rs.gold == g0 - pick.cost && pick.sold); mGold = rs.rs.gold; }
                mPotions = rs.rs.potions; mHp = rs.rs.hp;
                tap(g, 27); mst = 4; mT = 0; return;
            }
            case 4: {
                if (rs.ov != RunScreen.OV_NONE) { if (mT % 10 == 0) tap(g, 27); return; }
                // guardar dentro de la tienda: el piso de origen y la visita se conservan
                boolean w = RunSave.write(g.P, rs, 0);
                RunScreen ld = RunSave.load(g, 0);
                mchk("guardar/cargar dentro de la tienda conserva origen y visita (guardado=" + w + ", sideOrigin=" + (ld == null ? "?" : ld.rs.sideOrigin) + ", eventBiomeDone=" + (ld != null && ld.rs.eventBiomeDone) + ")", ld != null && ld.rs.sideOrigin == Room.COMBAT && ld.rs.eventBiomeDone && ld.rs.curEvent == Events.MERCHANT);
                Prop ex = null; for (Prop q : lv.props) if (q.kind.equals("door") && q.nextType == -3) ex = q;
                mchk("la salida del mercader es 'Volver' (no la salida principal)", ex != null);
                if (ex == null) { mst = 99; return; }
                mDoor.getClass(); mExit = ex; mst = 5; mT = 0; return;
            }
            case 5: {
                if (lv.room.type == Room.EVENT) { p.x = mExit.x; p.y = mExit.y; p.vx = 0; if (mT % 10 == 0) tap(g, 'E'); return; }
                mchk("volvimos al MISMO piso (misma sala, sin regenerar)", lv == mOrigin);
                mchk("la sala de origen no avanzo de numero (roomNo " + mRoomNo + " -> " + rs.rs.roomNo + ")", rs.rs.roomNo == mRoomNo);
                boolean same = lv.enemies.size() == mEn.size();
                for (int i = 0; same && i < mEn.size(); i++) same = lv.enemies.contains(mEn.get(i)) && mEn.get(i).alive && Math.abs(mEn.get(i).x - mPos[i * 3]) < 1.5f && Math.abs(mEn.get(i).y - mPos[i * 3 + 1]) < 1.5f && Math.abs(mEn.get(i).hp - mPos[i * 3 + 2]) < 0.01f;   // tolerancia: un fotograma de la ultima actualizacion antes del cambio de sala
                float md = 0; for (int i = 0; i < mEn.size(); i++) md = Math.max(md, Math.max(Math.abs(mEn.get(i).x - mPos[i * 3]), Math.abs(mEn.get(i).y - mPos[i * 3 + 1])));
                System.out.println("MERCHTEST detalle: desplazamiento maximo de un enemigo = " + md + " px; vivos=" + lv.enemies.size() + " misma lista=" + lv.enemies.containsAll(mEn));
                mchk("los mismos " + mEn.size() + " enemigos siguen vivos, con la misma posicion y vida", same);
                mchk("toKill intacto (" + lv.toKill + " = " + mKill + ") y la sala sigue sin despejar", lv.toKill == mKill && !lv.cleared);
                mchk("vida y oro conservados (hp " + rs.rs.hp + " = " + mHp + ", oro " + (int) rs.rs.gold + " = " + (int) mGold + ", frascos " + rs.rs.potions + ")", rs.rs.hp == mHp && rs.rs.gold == mGold && rs.rs.potions == mPotions);
                boolean exitDoor = false; for (Prop q : lv.props) if (q.kind.equals("door") && q.event == 0) exitDoor = true;
                mchk("la salida al siguiente piso sigue bloqueada (no existe)", !exitDoor);
                mchk("sin objetos/props de mas ni de menos (" + lv.props.size() + " = " + mProps + ")", lv.props.size() == mProps);
                mchk("el jugador reaparece junto a la puerta de acceso (x=" + (int) p.x + ", puerta " + (int) mDoor.x + ")", Math.abs(p.x - mDoor.x) < 40 && Math.abs(p.y - mDoor.y) < 4);
                mst = 6; mT = 0; return;
            }
            case 6: {   // reintentar entrar: debe estar desactivada
                p.x = mDoor.x; p.y = mDoor.y; p.vx = 0;
                if (mT % 10 == 0) tap(g, 'E');
                if (mT > 90) {
                    mchk("la entrada del mercader no permite volver a entrar en este piso", lv == mOrigin && rs.rs.sideOrigin == -1 && lv.room.type == Room.COMBAT);
                    mst = 7; mT = 0;
                }
                return;
            }
            case 7: {   // derrotar a los enemigos: se habilita la salida normal
                for (Enemy e : new java.util.ArrayList<>(lv.enemies)) if (e.alive) e.die(lv);
                if (!lv.cleared) { if (mT > 600) { mchk("el piso se despeja al derrotar a los enemigos", false); mst = 99; } return; }
                if (mT < 30) return;
                Prop ex = null; for (Prop q : lv.props) if (q.kind.equals("door") && q.event == 0 && q.nextType >= 0) ex = q;
                mchk("al despejar aparece la salida normal", ex != null);
                int before = rs.rs.roomNo;
                if (ex == null) { mst = 99; return; }
                mExit = ex; mst = 8; mT = 0; return;
            }
            case 8: {
                if (lv == mOrigin) { p.x = mExit.x; p.y = mExit.y; p.vx = 0; if (mT % 10 == 0) tap(g, 'E'); return; }
                mchk("la salida normal funciona: pasamos a la siguiente sala (roomNo " + mRoomNo + " -> " + rs.rs.roomNo + ")", rs.rs.roomNo == mRoomNo + 1);
                boolean again = false; for (Prop q : lv.props) if (q.kind.equals("door") && q.event == Events.MERCHANT) again = true;
                mchk("en la sala siguiente no reaparece el mercader (ya visitado en este bioma)", !again);
                System.out.println(mFail ? "MERCHTEST FALLOS" : "MERCHTEST TODO OK");
                mst = 99; return;
            }
            default: return;
        }
    }
    private Prop mExit;

    // ---- banco de pruebas de camaras secretas (BOT_SECTEST=indice de camara): secuencia fija para capturar con --script
    private int secT0 = -1;
    private static final int SEC_START = 400, SEC_R = 200;

    private void secretStep(Game g, RunScreen rs, Level lv, Player p, int frame) {
        java.util.List<Secret> all = lv.room.secrets;
        if (secT0 < 0) {
            if (frame < SEC_START) return;
            secT0 = frame;
            if (all.isEmpty()) { System.out.println("SECTEST: la sala no tiene camaras"); return; }
        }
        if (all.isEmpty()) return;
        int sf = frame - secT0;
        Secret s = all.get(Math.min(all.size() - 1, Integer.parseInt(System.getenv("BOT_SECTEST"))));
        int x0 = 1 << 20, y0 = 1 << 20, x1 = -1, y1 = -1;
        for (int[] d : s.door) { x0 = Math.min(x0, d[0]); y0 = Math.min(y0, d[1]); x1 = Math.max(x1, d[0]); y1 = Math.max(y1, d[1]); }
        float bx0 = x0 * 16, by0 = y0 * 16, bx1 = (x1 + 1) * 16, by1 = (y1 + 1) * 16, mx = (bx0 + bx1) / 2f, my = (by0 + by1) / 2f;
        boolean leftDoor = s.cx < (s.rx0 + s.rx1 + 1) * 8f;
        float outX = s.family == 0 ? mx - 70 : (leftDoor ? mx - 70 : mx + 70), outY = s.family == 0 ? s.ry0 * 16 : (s.ry1 + 1) * 16;
        int e = s.entrance;
        if (sf == 1) {   // nada de la camara debe verse mientras esta cerrada
            int vp = 0, tc = 0, en = 0;
            for (Prop q : lv.props) if (!q.hidden && s.contains((int) (q.x / 16), (int) ((q.y - 1) / 16))) vp++;
            for (int[] d : lv.animDeco) if (s.contains(d[0] / 16, d[1] / 16)) tc++;
            for (Enemy q : lv.enemies) if (s.contains((int) (q.x / 16), (int) ((q.y - 1) / 16))) en++;
            System.out.println("SECTEST oculto: props visibles dentro=" + vp + " antorchas dentro=" + tc + " enemigos dentro=" + en + " pickups=" + lv.pickups.size());
        }
        if (sf == 0) {
            System.out.println("SECTEST: entrada=" + Secret.E_NAME[e] + " recompensa=" + Secret.R_NAME[s.reward] + " reto=" + s.challenge + " familia=" + s.family + " rect=" + s.rx0 + "," + s.ry0 + ".." + s.rx1 + "," + s.ry1 + " bioma=" + lv.biome.key);
        }
        float hx = outX, hy = outY;
        if (e == Secret.E_RUNES || e == Secret.E_SYMBOLS || e == Secret.E_LEVER) { float[] w = s.sw.get(e == Secret.E_RUNES ? 1 : 0); hx = w[0] - 30; hy = w[1]; }
        if (e == Secret.E_SKILL) { hx = s.crX - 34; hy = s.crY; }
        boolean hold = !s.open && !s.revealing;
        if (System.getenv("BOT_SECREAL") != null && (e == Secret.E_WALL || e == Secret.E_FLOOR || e == Secret.E_STATUE)) { /* posicion controlada abajo */ } else if (sf < SEC_R + 2 || hold && sf < SEC_R + 60) { p.x = hx; p.y = hy; p.vx = p.vy = 0; p.safeX = p.x; p.safeY = p.y; if (sf == 0) lv.snapCamera(); }
        // accion que descubre la camara, siempre terminando en el fotograma SEC_R
        java.util.function.BiConsumer<Float, Float> hit = (cx, cy) -> lv.breakRect(cx - 12, cy - 12, 24, 24, 1);
        switch (e) {
            case Secret.E_WALL, Secret.E_FLOOR, Secret.E_STATUE -> {
                int n = e == Secret.E_STATUE ? 4 : 3;
                if (System.getenv("BOT_SECREAL") != null) {   // ataques reales del jugador (sin llamar a breakRect a mano)
                    boolean fromLeft = s.family == 0 || leftDoor;
                    if (hold) { p.x = fromLeft ? mx - 24 : mx + 24; p.y = outY; p.right = fromLeft; p.vx = p.vy = 0; if (sf >= 30 && sf % 16 == 0) tap(g, 'J'); }
                    if (sf == SEC_R + 1) System.out.println("SECTEST real: abierto=" + (s.open || s.revealing) + " frame=" + sf);
                } else for (int i = 0; i < n; i++) if (sf == SEC_R - 14 * i) hit.accept(mx, my);
            }
            case Secret.E_ILLUSION, Secret.E_WATERFALL, Secret.E_CURTAIN -> { if (sf == SEC_R) { p.x = s.family == 0 ? mx - 20 : mx - 6; p.y = s.family == 0 ? s.ry0 * 16 : outY; } }
            case Secret.E_LEVER -> { if (sf == SEC_R) { float[] w = s.sw.get(0); hit.accept(w[0], w[1] - 12); } }
            case Secret.E_SYMBOLS, Secret.E_RUNES -> {
                int base = e == Secret.E_RUNES ? SEC_R - 40 : SEC_R - 40;
                for (int k = 0; k < 3; k++) if (sf == base + k * 20) { float[] w = s.sw.get(s.order[k]); hit.accept(w[0], w[1] - 12); }
                if (e == Secret.E_SYMBOLS && sf == base - 30) { float[] w = s.sw.get((s.order[0] + 1) % 3); hit.accept(w[0], w[1] - 12); }   // error previo
            }
            case Secret.E_SKILL -> { if (sf == SEC_R - 1) p.state = Player.SKILL; if (sf == SEC_R) p.state = Player.SKILL; }
            default -> { }
        }
        if (sf == SEC_R + 1 || sf == SEC_R + 40 || sf == SEC_R + 100) System.out.println("SECTEST sf=" + sf + " open=" + s.open + " revealing=" + s.revealing + " rewardHidden=" + (s.rewardProp == null ? "n/a" : String.valueOf(s.rewardProp.hidden)) + " guardian=" + (s.guardian != null));
        // entrar a la camara
        if (sf == SEC_R + 110) { p.x = s.rwX - (s.family == 0 ? 0 : 30); p.y = s.rwY; p.vx = p.vy = 0; p.safeX = p.x; p.safeY = p.y; lv.snapCamera(); }
        if (sf > SEC_R + 110 && sf < SEC_R + 330) { p.vx = 0; }
        if (sf == SEC_R + 230 && s.guardian != null && s.guardian.alive) { s.guardian.die(lv); }
        if (sf >= SEC_R + 270 && sf < SEC_R + 470) { p.x = s.rwX + (s.family == 0 ? 14 : 12); p.y = s.rwY; p.vx = p.vy = 0; }
        if (sf == SEC_R + 280) System.out.println("SECTEST fin: open=" + s.open + " rewardOut=" + s.rewardOut + " rewardHidden=" + (s.rewardProp == null ? "n/a" : String.valueOf(s.rewardProp.hidden)) + " oro=" + lv.rs.gold + " pickups=" + lv.pickups.size());
        if (sf >= SEC_R + 280 && sf % 15 == 0 && sf < SEC_R + 420) { Prop n = lv.nearestInteractable(); if (n != null) tap(g, 'E'); }
        if (sf == SEC_R + 440) System.out.println("SECTEST abierto: usado=" + (s.rewardProp != null && s.rewardProp.used) + " ov=" + rs.ov);
    }

    private boolean npcDone, devOnce, spikeDone; private int roundStep, roundT; private boolean classPrinted, unlockedAll;
    private final java.util.List<Enemy> spikeEn = new java.util.ArrayList<>();
    private int cf;

    private void game_start(Game g, ClassScreen cs) {
        cs.layout();
        // el boton de jugar es el ultimo
        Screen.Hit h = cs.hits.get(cs.hits.size() - 1);
        Save.S.lastClass = classId;
        g.go(new RunScreen(g, ClassDef.ALL[classId], 0));
    }
}
