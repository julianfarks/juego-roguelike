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
    public static boolean trace = System.getenv("BOT_TRACE") != null;
    public static boolean godMode = System.getenv("BOT_GOD") != null;

    private void hold(Game g, int code, boolean down) {
        if (held[code] != down) { held[code] = down; g.key(code, down); }
    }

    private void tap(Game g, int code) { g.key(code, true); g.key(code, false); }

    public void tick(Game g, int frame) {
        Screen s = g.cur;
        if (s == null || g.fadeDir == 1) return;
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
        if (!classPrinted && System.getenv("BOT_PRINTCLASS") != null) { classPrinted = true; System.out.println("RUN clase=" + rs.cls.name + " bioma=" + (rs.rs.biome == null ? "?" : rs.rs.biome.name) + " stage=" + rs.rs.stage + " roomNo=" + rs.rs.roomNo + " kills=" + rs.rs.kills + " oro=" + rs.rs.gold + " infinite=" + rs.rs.infinite + " revividas=" + rs.rs.revivesUsed + " streak=" + rs.rs.streak); }
        if (rs.lv == null) return;
        Level lv = rs.lv;
        Player p = lv.pl;
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
            rs.loadRoom(type);
            return;
        }
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
        switch (rs.ov) {
            case RunScreen.OV_BLESS:
                if (rs.ovT > 1.3f) for (Screen.Hit h : rs.hits) { rs.touch(0, 0, h.x + 5, h.y + 5); rs.touch(0, 2, h.x + 5, h.y + 5); break; }
                return;
            case RunScreen.OV_CHEST:
                if (rs.ovT > 1.0f && System.getenv("BOT_CHESTSHOT") == null || rs.ovT > 6f) {
                    for (Screen.Hit h : rs.hits) if (h.tag == 1 && h.label == null) { for (int k = 0; k < 2; k++) { rs.touch(0, 0, h.x + 5, h.y + 5); rs.touch(0, 2, h.x + 5, h.y + 5); } break; }
                }
                return;
            case RunScreen.OV_SHOP: case RunScreen.OV_FORGE:
                if (rs.ovT > 2.0f) rs.back();
                return;
            case RunScreen.OV_PAUSE:
                if (rs.ovT > 0.5f) rs.back();
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
                boolean want = pr.kind.equals("door") || pr.kind.equals("merchant") || pr.kind.equals("forge") || pr.kind.equals("fountain") || pr.kind.equals("portal") || (pr.kind.equals("altar") && !pr.used) || (pr.kind.equals("chest") && !pr.used && pr.arg != 3);
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
