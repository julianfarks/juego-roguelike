package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/** La partida: salas, HUD, controles tactiles, altares, tienda, forja, jefes, muerte y victoria. */
final class RunScreen extends Screen implements Level.Listener {
    static final int OV_NONE = 0, OV_PAUSE = 1, OV_BLESS = 2, OV_SHOP = 3, OV_FORGE = 4, OV_DEAD = 5, OV_WIN = 6, OV_CHEST = 7, OV_TALK = 8;
    static final String[] RELIC_NAMES = {"Corona Exánime", "Corazón de Magma", "Lágrima de Escarcha", "Ojo del Vacío", "Savia Ancestral", "Chispa del Titán", "Cáliz de Sangre", "Disco del Eclipse"};

    static final class ShopItem {
        String name, desc, icon; int cost, kind, arg; boolean sold;
        ShopItem(String n, String d, String i, int c, int k, int a) { name = n; desc = d; icon = i; cost = c; kind = k; arg = a; }
    }

    final ClassDef cls;
    final RunState rs;
    final Input in;
    Level lv;
    int ov;
    float ovT;
    float fadeA = 1f;
    int fadeMode = -1;
    Runnable fadeAct;
    String bannerTitle = "", bannerSub = "";
    float bannerT;
    float bossCardT = -1;
    int[] offer = new int[3];
    int offerSel;
    ChestLoot.Reward[] cOffer;      // las 3 opciones del cofre abierto
    int cMode;
    Prop ovProp;
    // ---- laboratorio (Modo Desarrollador)
    boolean sandbox;
    private String sbEnemy;
    private boolean sbElite;
    private int sbBoss = -1, sbBiome;
    private float sbRespawnT = -1;
    private java.util.function.Supplier<Screen> sbBack;

    static RunScreen sandbox(Game g, ClassDef c, int biome, String enemy, boolean elite, int boss, java.util.function.Supplier<Screen> back) {
        RunScreen r = new RunScreen(g, c, 0);
        r.sandbox = true; r.rs.sandbox = true;
        r.sbEnemy = enemy; r.sbElite = elite; r.sbBoss = boss; r.sbBiome = Math.max(0, Math.min(8, biome)); r.sbBack = back;
        r.rs.biome = Biome.ALL[r.sbBiome]; r.rs.stage = Biome.ALL[r.sbBiome].tier;
        r.rs.gold = Save.devGold;
        r.resumeType = boss >= 0 ? Room.BOSS : Room.COMBAT;
        return r;
    }

    static RunScreen sandboxShop(Game g, ClassDef c, java.util.function.Supplier<Screen> back) {
        RunScreen r = sandbox(g, c, 0, null, false, -1, back);
        r.resumeType = Room.REST;
        return r;
    }

    private void sandboxSetup() {
        if (!sandbox) return;
        if (lv.room.type == Room.REST) { lv.tutorial = null; bannerTitle = "TIENDA DE PRUEBA"; bannerSub = "Oro de prueba: no afecta al perfil"; bannerT = 3f; return; }
        bannerTitle = "LABORATORIO"; bannerSub = "Invulnerable · no se guarda nada"; bannerT = 3f; lv.tutorial = null;
        if (sbBoss >= 0 && lv.room.type == Room.BOSS) { setupBoss(BossDef.ALL[Math.min(sbBoss, BossDef.ALL.length - 1)]); return; }
        lv.enemies.clear(); lv.toKill = 0; lv.cleared = false;
        if (sbEnemy != null) {
            EnemyDef ed = EnemyDef.get(sbEnemy);
            if (ed != null) {
                Enemy en = new Enemy(ed, sbElite, 1f, 1f);
                en.x = lv.pl.x + 120; en.y = lv.pl.y; en.home = en.x;
                lv.enemies.add(en); lv.toKill = 1;
            }
        }
    }

    private Story.Dialog talk;
    private Dlg tdlg;
    private int tphase;   // 0 lineas, 1 opciones, 2 resultado
    List<ShopItem> shop;
    boolean ended, quitConfirm;
    float deadT = -1;
    float winT = -1;
    boolean winPending;
    int sumSouls;
    boolean sumWin;
    String sumNote = "";
    float lowHpT;
    boolean ultWasReady;
    float comboFlash;
    float relicBannerT;
    String relicBanner = "";
    int relicBannerIdx;
    float hintT;
    int resumeType = -1;          // al cargar partida: tipo de sala donde reanudar
    boolean saveMenu;
    final java.util.HashSet<Integer> mySlots = new java.util.HashSet<>();
    float autoT, toastT;
    String toast = "";

    RunScreen(Game g, ClassDef c, int asc) {
        super(g);
        cls = c;
        in = g.input;
        rs = new RunState(c, System.nanoTime() ^ 0x5DEECE66DL, asc);
    }

    @Override void enter() {
        in.reset();
        if (lv == null && resumeType >= 0) {
            int t = resumeType; resumeType = -1;
            loadRoom(t);
            fadeA = 1f; fadeMode = -1;
        } else if (lv == null) {
            rs.biome = null;
            loadRoom(Room.HUB);
            fadeA = 1f; fadeMode = -1;
        }
    }

    @Override boolean gameplayInput() { return ov == OV_NONE && lv != null; }
    @Override boolean keepInput() { return ov == OV_NONE && lv != null && lv.hitstop > 0; }

    // =============================================================== salas
    void goRoom(final int type) {
        if (fadeMode == 1) return;
        fadeMode = 1;
        fadeAct = () -> loadRoom(type);
        in.reset();
    }

    private Biome hubBiome() { return Biome.ALL[7]; }

    void loadRoom(int type) {
        Platform P = game.P;
        Biome b = type == Room.HUB || rs.biome == null ? hubBiome() : rs.biome;
        Room rm = RoomGen.generate(type, b, rs.rng, rs.stage, rs.roomNo);
        rm.bake(P);
        lv = new Level(P, rs, rm, in);
        lv.viewW = game.viewW;
        lv.listener = this;
        Player pl = new Player(rs);
        lv.populate(pl);
        pl.onRoomStart(lv);
        lv.snapCamera();
        lv.relicListener = this::onRelic;
        shop = null;
        ov = OV_NONE;
        quitConfirm = false;
        // musica y ambiente
        if (type == Room.HUB) { Snd.music("mus_sanctuary", true); Snd.ambient(null, 0); }
        else if (type == Room.BOSS) { /* la musica del jefe empieza en la cinematica */ Snd.ambient(b.ambient, 0.25f); }
        else { Snd.music(b.music, true); Snd.ambient(b.ambient, 0.3f); }
        // contenido especial
        if (type == Room.HUB) setupHub();
        if (type == Room.BOSS) setupBoss(null);
        sandboxSetup();
        if (lv.cleared && type != Room.BOSS && !sandbox) spawnDoors();
        // banner
        if (type == Room.HUB) {
            bannerTitle = rs.stage >= 3 ? "El Sello está completo" : "Santuario del Viajero";
            bannerSub = rs.stage == 0 && rs.visited.isEmpty() ? "Elige tu primer destino" : (rs.stage >= 3 ? "Solo queda el Cazador" : "Elige tu próximo destino");
        } else if (type == Room.BOSS) {
            bannerTitle = ""; bannerSub = "";
        } else {
            bannerTitle = rs.biome.name;
            bannerSub = rs.roomNo == 0 ? rs.biome.tagline : (type == Room.REST ? "Tienda · forja · altar · fuente" : RunState.roomName(type));
        }
        bannerT = type == Room.BOSS ? 0 : 3f;
        // tutorial
        if (!Save.S.tutorialDone) {
            if (type == Room.HUB && rs.visited.isEmpty()) lv.tutorial = "Acércate a un portal\ny pulsa el botón de la llave";
            else if (type == Room.COMBAT && rs.roomNo == 0) lv.tutorial = "Pad: moverte  ·  Botones: saltar, rodar y atacar\nEl rodar te hace invulnerable un instante";
        }
        fadeAct = null;
        layoutOverlay();
    }

    private void setupHub() {
        Room rm = lv.room;
        List<Integer> ids = new ArrayList<>();
        if (rs.stage >= 3) ids.add(8);
        else for (Biome bb : Biome.ALL) if (bb.tier == rs.stage && bb.id < 8 && !rs.visited.contains(bb.id)) ids.add(bb.id);
        int n = ids.size();
        for (int i = 0; i < n; i++) {
            float x = rm.pixW * (i + 1) / (n + 1f);
            Prop p = lv.addProp(new Room.PropSpec("portal", x, rm.spawnY, ids.get(i)));
            p.nextBiome = ids.get(i);
            p.label = Biome.ALL[ids.get(i)].name;
        }
    }

    private void setupBoss(BossDef force) {
        Room rm = lv.room;
        BossDef d = force != null ? force : BossDef.byBiome(rs.biome.id);
        Boss bs = new Boss(d, rs);
        bs.x = rm.pixW - 8 * Room.TS;
        bs.y = rm.spawnY;
        lv.boss = bs;
        lv.bossFight = true;
        lv.cinematic = true;
        lv.camTargetX = bs.x - 60; lv.camTargetY = bs.y - 70; lv.camTargetZoom = 1f;
        lv.bossBarShow = 0;
        Snd.music(d.music, true);
        bossCardT = 0;
        if (d.idx == 8) {
            bannerTitle = ""; bannerSub = "";
        }
    }

    // puertas de salida segun el progreso
    private void spawnDoors() {
        Room rm = lv.room;
        if (rm.type == Room.HUB) return;
        int next = rs.roomNo + 1;
        int[] types;
        if (rm.type == Room.BOSS) return;
        if (next <= 2) types = rs.pickDoorTypes(1);
        else if (next == 3) types = new int[]{Room.REST};
        else types = new int[]{Room.BOSS};
        int n = types.length;
        for (int i = 0; i < n; i++) {
            float x = rm.exitX + (n == 1 ? 0 : (i == 0 ? -26 : 26));
            Prop d = lv.addProp(new Room.PropSpec("door", x, rm.exitY, 0));
            d.doorIdx = i; d.nextType = types[i];
            d.label = RunState.roomName(types[i]);
            d.anim = "open"; d.animT = 0;
        }
        Snd.sfx("door_open", 0.8f);
    }

    // =============================================================== Level.Listener
    @Override public void onCleared(Level l) {
        if (sandbox) { sbRespawnT = 1.6f; l.text(l.pl.x, l.pl.y - 50, "Reiniciando prueba...", 0xFFD25A, true); return; }
        Snd.sfx("room_clear", 0.9f);
        l.text(l.pl.x, l.pl.y - 50, "¡Sala despejada!", 0xFFD25A, true);
        if (l.room.type == Room.COMBAT || l.room.type == Room.ELITE) completeRound(l);
        rs.roomsDone++;
        spawnDoors();
        comboFlash = 1f;
    }

    /**
     * Recompensa de ronda (una sola vez por sala: Level.rewarded):
     * sin ningun dano real -> 2 cofres de eleccion; con dano -> 1 cofre. Tambien registra las estadisticas de la cuenta.
     */
    void completeRound(Level l) {
        if (l.rewarded) return;
        l.rewarded = true;
        boolean perfect = l.roomHits == 0;
        int n = perfect ? 2 : 1;
        for (int i = 0; i < n; i++) {
            Prop c = l.addProp(new Room.PropSpec("chest", l.room.exitX - 70 - i * 38, l.room.exitY, 2));
            c.label = perfect ? "Cofre perfecto" : "Recompensa";
            c.roundChest = true;
            l.ps.burst(l.rng, c.x, c.y - 12, perfect ? 0xFFE9A0 : 0xFFD25A, 20, 100, 0.6f, 2, 0, true);
        }
        l.text(l.pl.x, l.pl.y - 66, perfect ? "¡RONDA PERFECTA! 2 cofres" : "Ronda completada: 1 cofre", perfect ? 0xFFE9A0 : 0xFFD25A, true);
        lastRoundChests = n;
        Save s = Save.S;
        if (!sandbox) {
            rs.roundsThisRun++; rs.streak++;
            if (perfect) { rs.perfectStreak++; s.perfectRounds++; } else rs.perfectStreak = 0;
            s.rounds++;
            s.bestStreak = Math.max(s.bestStreak, rs.streak);
            s.bestPerfectStreak = Math.max(s.bestPerfectStreak, rs.perfectStreak);
            s.maxKillsRound = Math.max(s.maxKillsRound, l.roomEnemies);
            s.write();
            announceTrophies();
        }
    }

    float playSave;
    int lastRoundChests;   // (pruebas) cofres entregados en la ultima ronda

    private void announceTrophies() {
        java.util.List<String> nw = Trophies.check(Save.S);
        if (!nw.isEmpty()) { toast = "Trofeo: " + nw.get(0); toastT = 3.5f; }
    }

    @Override public void onPlayerDead(Level l) {
        if (deadT < 0) { deadT = 0; endRun(false); }
    }

    @Override public void onBossDead(Level l) {
        if (sandbox) { l.bossFight = false; sbRespawnT = 3.5f; return; }
        BossDef d = l.boss.def;
        l.bossFight = false;
        l.cleared = true;
        rs.roomsDone++;
        if (d.idx == 8 && d.form < 2) {
            // siguiente forma del Cazador
            final BossDef nd = BossDef.ALL[9 + d.form];
            l.pl.invuln = 3f;
            l.healPlayer(rs.stats.maxHp * 0.25f);
            l.later(0.2f, () -> {
                float ox = lv.boss.x;
                setupBoss(nd);
                lv.boss.x = ox;
                lv.cinematic = true;
                bossCardT = 0;
            });
            return;
        }
        if (d.idx == 8) {
            Save.S.finalBeaten = true;
            winT = 0; winPending = true;
            endRun(true);
            return;
        }
        // jefe normal: puerta de salida
        Room rm = l.room;
        Prop door = l.addProp(new Room.PropSpec("door", rm.exitX, rm.exitY, 0));
        door.nextType = -2; door.label = "Salida"; door.anim = "open"; door.animT = 0;
        Snd.music(rs.biome.music, true);
        Snd.sfx("door_open", 0.8f);
    }

    @Override public void onTutorial(String msg) { if (lv != null) lv.tutorial = msg; }

    private void onRelic() {
        for (int i = 7; i >= 0; i--) {
            if (rs.relicsThisRun[i] && relicBannerT <= 0) { relicBannerIdx = i; relicBanner = RELIC_NAMES[i]; }
        }
        relicBannerT = 4f;
        if (Save.S.sealForged()) relicBanner += "  ·  ¡Sello completo!";
    }

    // =============================================================== fin de partida
    private void endRun(boolean win) {
        if (sandbox) return;
        if (ended) return;
        ended = true;
        Save s = Save.S;
        int gain = Math.round(rs.souls * rs.diffSouls());
        if (win) gain += rs.souls / 2 + 60 * rs.bossKills + (rs.finalRun ? 300 : 0);
        sumSouls = gain;
        sumWin = win;
        s.souls += gain; s.totalSouls += gain;
        s.runs++;
        if (!win) s.losses++;
        s.classRuns[cls.id]++;
        s.kills += rs.kills; s.bossKills += rs.bossKills;
        s.bestRooms = Math.max(s.bestRooms, rs.roomsDone);
        s.lastClass = cls.id;
        s.tutorialDone = true;
        if (win) {
            s.wins++; s.classWins[cls.id]++;
            if (rs.asc == s.ascension && s.ascension < 5) { s.ascension++; sumNote = "¡Nueva dificultad desbloqueada!"; }
        }
        s.write();
    }

    private void afterBoss() {
        rs.stage++;
        rs.blessingTaken = false;
        if (rs.stage >= 3 && !Save.S.sealForged()) {
            endRun(true);
            openOv(OV_WIN);
            return;
        }
        rs.roomNo = 0;
        goRoom(Room.HUB);
    }

    // =============================================================== interaccion
    private void interact() {
        Prop p = lv.nearestInteractable();
        if (p == null || !lv.pl.alive || lv.cinematic) return;
        switch (p.kind) {
            case "door":
                Snd.sfx("door_open", 0.7f);
                if (p.nextType == -2) { afterBoss(); break; }
                rs.roomNo++;
                rs.roomsDone = Math.max(rs.roomsDone, rs.roomNo);
                goRoom(p.nextType);
                break;
            case "portal": {
                Snd.sfx("portal_enter", 1f);
                int id = p.nextBiome;
                rs.biome = Biome.ALL[id];
                rs.visited.add(id);
                rs.roomNo = id == 8 ? 4 : 0;
                rs.blessingTaken = false;
                if (id == 8) rs.finalRun = true;
                lv.flash(0xFFFFFF, 0.4f);
                goRoom(id == 8 ? Room.BOSS : Room.COMBAT);
                break;
            }
            case "altar":
                if (!p.used) { ovProp = p; openBlessing(); }
                break;
            case "chest":
                openChest(p);
                break;
            case "forge":
                ovProp = p; openOv(OV_FORGE);
                break;
            case "merchant":
                ovProp = p;
                if (shop == null) shop = genShop();
                openOv(OV_SHOP);
                break;
            case "npc":
                if (!p.used) startTalk(p);
                break;
            case "fountain":
                if (!p.used) {
                    p.used = true;
                    float pct = lv.room.type == Room.REST ? 0.5f : 0.65f;
                    lv.healPlayer(rs.stats.maxHp * pct);
                    Snd.sfx("fountain_heal", 1f);
                    lv.fx("fx_heal", "rise", lv.pl.x, lv.pl.y - 14, 1.3f, 0, 0);
                    lv.ps.burst(lv.rng, p.x, p.y - 20, 0x7AF0FF, 20, 90, 0.7f, 2, -20, true);
                    p.label = "(seca)";
                }
                break;
            default: break;
        }
    }

    // =============================================================== encuentros narrativos (NPC)
    void startTalk(Prop p) {
        int npc = Math.max(0, Math.min(2, p.arg));
        talk = Story.npcDialog(npc, Save.S.relicCount(), rs.bossKills, Save.S.story[Story.S_NPC0 + npc]);
        tdlg = new Dlg(UI.small, 400, 3);
        tdlg.set(talk.lines);
        tphase = 0;
        ovProp = p;
        openOv(OV_TALK);
        Snd.sfx("ui_open", 0.5f);
    }

    private void talkTap() {
        if (talk == null || ovT < 0.25f) return;
        if (tphase == 0) {
            if (tdlg.advance()) {
                if (talk.choices.isEmpty()) finishTalk(); else { tphase = 1; layoutOverlay(); }
            }
        } else if (tphase == 2) {
            if (tdlg.advance()) finishTalk();
        }
    }

    private boolean choiceOk(Story.Choice c) {
        if (c.needPotion && rs.potions < 1) return false;
        if (c.gold < 0 && rs.gold < -c.gold) return false;
        return true;
    }

    private void chooseTalk(Story.Choice c) {
        if (!choiceOk(c)) { Snd.sfx("ui_error", 0.8f); return; }
        if (c.gold != 0) rs.gold = Math.max(0, rs.gold + c.gold);
        if (c.souls != 0) rs.souls += c.souls;
        if (c.potion != 0) rs.potions = Mth.clamp(rs.potions + c.potion, 0, rs.stats.potionsMax + 1);
        if (c.heal > 0) {
            lv.healPlayer(rs.stats.maxHp * c.heal);
            lv.fx("fx_heal", "rise", lv.pl.x, lv.pl.y - 14, 1.2f, 0, 0);
        }
        if (c.gold > 0) Snd.sfx("coin", 0.9f);
        tdlg.set(talk.who, c.res);
        tphase = 2;
        layoutOverlay();
    }

    private void finishTalk() {
        if (talk != null && talk.npc >= 0) { Save.S.story[Story.S_NPC0 + talk.npc]++; Save.S.write(); }
        if (ovProp != null) { ovProp.used = true; ovProp.label = null; }
        talk = null;
        closeOv();
    }

    private void openChest(Prop p) {
        if (p.used) return;
        p.used = true; p.anim = "open"; p.animT = 0;
        if (!sandbox) { Save.S.chestsOpened++; if (p.arg == 3) Save.S.secretChests++; Save.S.write(); announceTrophies(); }
        Snd.sfx("chest_open", 1f);
        lv.ps.burst(lv.rng, p.x, p.y - 10, 0xFFD25A, 16, 110, 0.7f, 2, 100, true);
        if (p.arg == 3) {
            rs.secretsFound++;
            Items.secretChestDrops(lv, rs, p.x, p.y);
        } else if (p.arg == 0) {
            lv.dropGold(p.x, p.y - 14, Math.round((45 + 12 * rs.stage + lv.rng.i(30)) * rs.stats.goldMul));
            lv.dropSouls(p.x, p.y - 14, 6 + 2 * rs.stage);
        }
        p.label = null;
        ovProp = p;
        // al abrir un cofre siempre se eligen 1 de 3 recompensas
        final int mode = ChestLoot.modeFor(rs.rng, p.arg), lb = ChestLoot.luckBonusFor(p.arg);
        lv.later(0.5f, () -> openChestOv(mode, lb));
    }

    private void openChestOv(int mode, int luckBonus) {
        cMode = mode;
        cOffer = ChestLoot.roll(rs, mode, luckBonus);
        offerSel = game.keyboardUsed ? 0 : -1;
        openOv(OV_CHEST);
        Snd.sfx("altar_bless", 0.9f);
    }

    private void confirmChest() {
        if (ov != OV_CHEST || offerSel < 0 || ovT < 0.3f || cOffer == null) return;
        ChestLoot.Reward x = cOffer[offerSel];
        ChestLoot.apply(rs, x);
        if (x.kind == ChestLoot.K_BARRIER) lv.pl.shield = Math.min(70, lv.pl.shield + x.val);
        cOffer = null;
        closeOv();
        int col = ChestLoot.R_COL[x.rar] & 0xFFFFFF;
        lv.text(lv.pl.x, lv.pl.y - 50, x.name + (x.amount.isEmpty() ? "" : "  " + x.amount), col, true);
        lv.ps.burst(lv.rng, lv.pl.x, lv.pl.y - 16, col, 22, 120, 0.8f, 3, 60, true);
        lv.fx("fx_star", "burst", lv.pl.x, lv.pl.y - 18, 1f, col, Platform.ADD | Platform.TINT);
        Snd.sfx("secret", 0.9f);
    }

    // =============================================================== overlays
    private void openOv(int o) {
        ov = o; ovT = 0; saveMenu = false;
        in.reset();
        if (o != OV_DEAD && o != OV_WIN) Snd.sfx("ui_open", 0.7f);
        if (o == OV_PAUSE) Snd.sfx("ui_pause", 0.7f);
        layoutOverlay();
    }

    private void closeOv() {
        ov = OV_NONE; ovT = 0; hits.clear(); saveMenu = false;
        in.reset();
        Snd.sfx("ui_back", 0.7f);
    }

    private void openBlessing() {
        // elegir 3 distintas con peso
        List<Integer> pool = new ArrayList<>();
        for (Blessing b : Blessing.ALL) if (rs.bless[b.id] < b.max) pool.add(b.id);
        int[] pick = new int[3];
        int n = Math.min(3, pool.size());
        if (n == 0) { lv.healPlayer(rs.stats.maxHp * 0.3f); return; }
        for (int i = 0; i < 3; i++) pick[i] = -1;
        for (int i = 0; i < n; i++) {
            float tot = 0;
            for (int id : pool) tot += Blessing.ALL[id].weight * (rs.bless[id] > 0 ? 1.4f : 1f);
            float r = rs.rng.f() * tot;
            int chosen = pool.get(0);
            for (int id : pool) {
                r -= Blessing.ALL[id].weight * (rs.bless[id] > 0 ? 1.4f : 1f);
                if (r <= 0) { chosen = id; break; }
            }
            pick[i] = chosen;
            pool.remove((Integer) chosen);
        }
        offer = pick;
        offerSel = 0;
        openOv(OV_BLESS);
        Snd.sfx("altar_bless", 0.9f);
    }

    private void applyBless(int id) {
        rs.bless[id]++;
        rs.blessingTaken = true;
        float oldMax = rs.stats.maxHp;
        rs.stats.recalc(rs);
        if (id == Blessing.CORAZON) rs.hp = Math.min(rs.stats.maxHp, rs.hp + 20);
        rs.hp = Math.min(rs.hp, rs.stats.maxHp);
        if (id == Blessing.ESCUDO && lv.pl != null) lv.pl.shield = Math.max(lv.pl.shield, 14 + 10 * rs.stats.shieldLvl);
        if (id == Blessing.SEGUNDA) rs.reviveUsed = false;
        if (lv.pl != null) {
            lv.text(lv.pl.x, lv.pl.y - 56, Blessing.ALL[id].name, 0xFFD25A, true);
            lv.fxAdd("fx_ring", "pulse", lv.pl.x, lv.pl.y - 18, 1.2f, 0xFFD25A);
            lv.fx("fx_holy", "beam", lv.pl.x, lv.pl.y - 60, 0.8f, 0, 0);
            lv.ps.burst(lv.rng, lv.pl.x, lv.pl.y - 20, 0xFFD25A, 24, 140, 0.8f, 2, -20, true);
        }
        Snd.sfx("ui_pick_upgrade", 1f);
    }

    private List<ShopItem> genShop() {
        List<ShopItem> l = new ArrayList<>();
        int st = rs.stage;
        l.add(new ShopItem("Frasco de vida", "+1 frasco de vida.", "potion", 30 + 10 * st, 0, 0));
        l.add(new ShopItem("Elixir", "Cura el 50% de tu vida.", "heart", 45 + 10 * st, 1, 0));
        // bendicion aleatoria
        List<Integer> pool = new ArrayList<>();
        for (Blessing b : Blessing.ALL) if (rs.bless[b.id] < b.max) pool.add(b.id);
        if (!pool.isEmpty()) {
            int id = pool.get(rs.rng.i(pool.size()));
            Blessing b = Blessing.ALL[id];
            l.add(new ShopItem(b.name, b.desc, b.icon, 95 + 25 * st, 2, id));
        }
        if (rs.rng.chance(0.5f)) l.add(new ShopItem("Cristal de poder", "Carga tu definitiva al máximo.", "star", 60 + 10 * st, 3, 0));
        else if (rs.weaponLvl < 5) l.add(new ShopItem("Piedra de afilar", "Mejora tu arma un nivel.", "forge", Math.round(rs.forgeCost() * 1.15f), 4, 0));
        else l.add(new ShopItem("Reserva de almas", "Obtienes 15 almas.", "soul", 50, 5, 0));
        return l;
    }

    private void buy(ShopItem it) {
        if (it.sold) return;
        if (rs.gold < it.cost) { Snd.sfx("ui_error", 0.8f); hintT = 1.2f; return; }
        rs.gold -= it.cost;
        it.sold = true;
        Snd.sfx("shop_buy", 1f);
        switch (it.kind) {
            case 0: rs.potions = Math.min(rs.stats.potionsMax + 1, rs.potions + 1); break;
            case 1: lv.healPlayer(rs.stats.maxHp * 0.5f); break;
            case 2: applyBless(it.arg); break;
            case 3: rs.ult = 100f; break;
            case 4: rs.weaponLvl++; rs.stats.recalc(rs); break;
            default: rs.souls += 15; break;
        }
        layoutOverlay();
    }

    // layout de los botones del overlay actual
    void layoutOverlay() {
        hits.clear();
        down = null; downId = -1;
        int w = W();
        switch (ov) {
            case OV_BLESS: {
                float cw = Math.min(150, (w - 40) / 3f), gap = 8, x0 = w / 2f - (3 * cw + 2 * gap) / 2f;
                for (int i = 0; i < 3; i++) {
                    if (offer[i] < 0) continue;
                    final int k = i;
                    Hit h = add(x0 + i * (cw + gap), 52, cw, 160, null, () -> {
                        if (ovT < 0.35f) return;
                        applyBless(offer[k]);
                        if (ovProp != null && ovProp.kind.equals("altar")) { ovProp.used = true; ovProp.anim = "used"; ovProp.label = null; }
                        closeOv();
                    });
                    h.plain = false; h.tag = i;
                }
                break;
            }
            case OV_CHEST: {
                float cw = Math.min(150, (w - 40) / 3f), gap = 8, x0 = w / 2f - (3 * cw + 2 * gap) / 2f;
                for (int i = 0; i < 3; i++) {
                    final int k = i;
                    Hit h = add(x0 + i * (cw + gap), 44, cw, 164, null, () -> {
                        if (ovT < 0.3f) return;
                        if (offerSel == k) confirmChest();
                        else { offerSel = k; Snd.sfx("ui_hover", 0.7f); layoutOverlay(); }
                    });
                    h.plain = true; h.tag = i; h.noSound = true;
                }
                Hit ok = add(w / 2f - 60, 216, 120, 24, offerSel < 0 ? "Toca una carta" : "Elegir", this::confirmChest);
                ok.disabled = offerSel < 0;
                break;
            }
            case OV_SHOP: {
                float cw = Math.min(190, (w - 40) / 2f), ch = 54;
                float x0 = w / 2f - cw - 3;
                for (int i = 0; i < shop.size(); i++) {
                    final ShopItem it = shop.get(i);
                    Hit h = add(x0 + (i % 2) * (cw + 6), 52 + (i / 2) * (ch + 6), cw, ch, null, () -> buy(it));
                    h.tag = i; h.plain = true; h.noSound = true;
                }
                add(w / 2f - 50, 52 + 2 * (ch + 6) + 6, 100, 22, "Cerrar", this::closeOv);
                break;
            }
            case OV_TALK: {
                float bw = Math.min(w - 40, 430), bx = w / 2f - bw / 2f;
                add(0, 0, w, Platform.VIEW_H, null, this::talkTap).plain = true;
                if (tphase == 1 && talk != null) {
                    for (int i = 0; i < talk.choices.size(); i++) {
                        final Story.Choice c = talk.choices.get(i);
                        Hit h = add(bx, 120 + i * 24, bw, 20, c.label, () -> chooseTalk(c));
                        h.disabled = !choiceOk(c);
                    }
                }
                break;
            }
            case OV_FORGE: {
                Hit up = add(w / 2f - 112, 176, 108, 24, "Mejorar", () -> {
                    int cost = rs.forgeCost();
                    if (rs.weaponLvl >= 5 || rs.gold < cost) { Snd.sfx("ui_error", 0.8f); return; }
                    rs.gold -= cost; rs.weaponLvl++; rs.stats.recalc(rs);
                    Snd.sfx("forge_anvil", 1f);
                    lv.shake(2f, 0.15f);
                    lv.ps.burst(lv.rng, ovProp.x, ovProp.y - 20, 0xFFB040, 30, 140, 0.7f, 2, 200, true);
                    lv.fxAdd("fx_ring", "pulse", lv.pl.x, lv.pl.y - 18, 1f, 0xFFB040);
                    layoutOverlay();
                });
                up.disabled = rs.weaponLvl >= 5 || rs.gold < rs.forgeCost();
                add(w / 2f + 4, 176, 108, 24, "Cerrar", this::closeOv);
                break;
            }
            case OV_PAUSE: {
                float px = w / 2f - 220;
                float bw = 150, bx = px + 12, by = 52;
                Save s = Save.S;
                if (saveMenu) {
                    for (int i = 0; i < RunSave.SLOTS; i++) {
                        final int slot = i;
                        add(bx, by + i * 28, bw, 22, "Guardar en ranura " + (i + 1), () -> { RunSave.write(game.P, this, slot); toast = "Partida guardada en la ranura " + (slot + 1); toastT = 2.5f; Snd.sfx("ui_confirm", 0.9f); layoutOverlay(); });
                    }
                    add(bx, by + 3 * 28 + 6, bw, 22, "Volver", () -> { saveMenu = false; layoutOverlay(); });
                    break;
                }
                add(bx, by, bw, 22, "Continuar", this::closeOv);
                add(bx, by + 28, bw, 22, "Música: " + (s.musicOn ? "SÍ" : "NO"), () -> { s.musicOn = !s.musicOn; Snd.applyVolumes(); s.write(); layoutOverlay(); });
                add(bx, by + 56, bw, 22, "Sonidos: " + (s.sfxOn ? "SÍ" : "NO"), () -> { s.sfxOn = !s.sfxOn; Snd.applyVolumes(); s.write(); layoutOverlay(); });
                add(bx, by + 84, bw, 22, "Vibración: " + (s.vibOn ? "SÍ" : "NO"), () -> { s.vibOn = !s.vibOn; s.write(); layoutOverlay(); });
                add(bx, by + 112, bw, 22, "Guardar partida", () -> { saveMenu = true; layoutOverlay(); });
                add(bx, by + 140, bw, 22, quitConfirm ? "¿Seguro? Toca otra vez" : "Abandonar partida", () -> {
                    if (sandbox) { game.go(sbBack != null ? sbBack.get() : new Screens.Title(game)); return; }
                    if (quitConfirm) { endRun(false); game.go(new Screens.Title(game)); }
                    else { quitConfirm = true; layoutOverlay(); }
                });
                break;
            }
            case OV_DEAD: {
                add(w / 2f - 130, 206, 124, 24, "Reintentar", () -> game.go(new ClassScreen(game)));
                add(w / 2f + 6, 206, 124, 24, "Menú principal", () -> game.go(new Screens.Title(game)));
                break;
            }
            case OV_WIN: {
                final boolean fin = rs.finalRun;
                add(w / 2f - 62, 206, 124, 24, fin ? "Ver créditos" : "Continuar", () -> {
                    if (fin && Story.tryUnlockFinal() && Story.cine("final") != null)
                        game.go(new Cinematic(game, Story.FINAL, () -> game.go(new Screens.Credits(game, true))));
                    else game.go(fin ? new Screens.Credits(game, true) : new Screens.Title(game));
                });
                break;
            }
            default: break;
        }
    }

    @Override void resize() { layoutOverlay(); if (lv != null) lv.viewW = game.viewW; }

    @Override boolean back() {
        if (lv == null) return false;
        if (ov == OV_NONE) { openOv(OV_PAUSE); return true; }
        if (ov == OV_PAUSE && saveMenu) { saveMenu = false; layoutOverlay(); return true; }
        if (ov == OV_TALK) { talk = null; closeOv(); return true; }
        if (ov == OV_PAUSE || ov == OV_SHOP || ov == OV_FORGE) { closeOv(); return true; }
        return true;
    }

    @Override void pause() {
        if (lv != null && deadT < 0 && winT < 0 && fadeMode != 1 && lv.pl.alive && ov != OV_DEAD && ov != OV_WIN) RunSave.write(game.P, this, RunSave.AUTO);
        if (ov == OV_NONE && lv != null && deadT < 0 && winT < 0) openOv(OV_PAUSE);
    }

    // =============================================================== actualizacion
    @Override void update(float dt) {
        // transiciones
        if (fadeMode == 1) {
            fadeA += dt * 4.5f;
            if (fadeA >= 1f) { fadeA = 1f; Runnable r = fadeAct; fadeAct = null; fadeMode = -1; if (r != null) r.run(); }
        } else if (fadeMode == -1) {
            fadeA -= dt * 2.8f;
            if (fadeA <= 0) { fadeA = 0; fadeMode = 0; }
        }
        if (lv == null) return;
        ovT += dt;
        if (!sandbox && ov != OV_PAUSE) { Save.S.playMs += (long) (dt * 1000f); playSave += dt; if (playSave > 30f) { playSave = 0; Save.S.write(); } }
        if (sandbox && sbRespawnT > 0) { sbRespawnT -= dt; if (sbRespawnT <= 0) { sbRespawnT = -1; loadRoom(sbBoss >= 0 ? Room.BOSS : Room.COMBAT); } }
        if (ov == OV_TALK && tdlg != null) tdlg.update(dt);
        if (bannerT > 0) bannerT -= dt;
        if (lv.unlockTitle != null) { bannerTitle = lv.unlockTitle; bannerSub = lv.unlockSub; bannerT = 3f; lv.unlockTitle = null; }
        if (relicBannerT > 0) relicBannerT -= dt;
        if (hintT > 0) hintT -= dt;
        if (toastT > 0) toastT -= dt;
        if (ov == OV_NONE && deadT < 0 && winT < 0 && lv.pl.alive) {
            autoT += dt;
            if (autoT >= 300f) { autoT = 0; RunSave.write(game.P, this, RunSave.AUTO); toast = "Autoguardado"; toastT = 2f; }
        }
        if (comboFlash > 0) comboFlash -= dt;
        if (bossCardT >= 0) bossCardT += dt;
        if (ov == OV_NONE) {
            if (fadeMode != 1) {
                if (in.pressed(Input.B_PAUSE) && deadT < 0 && winT < 0) { openOv(OV_PAUSE); return; }
                Prop near = lv.nearestInteractable();
                boolean canInt = near != null && lv.pl.alive && !lv.cinematic && deadT < 0;
                in.btn[Input.B_INTERACT].visible = canInt;
                if (canInt && in.pressed(Input.B_INTERACT)) { in.consume(Input.B_INTERACT); interact(); }
            }
            lv.update(dt);
            if (ov == OV_NONE && lv != null) {
                // ult lista
                boolean ready = rs.ult >= 100f;
                if (ready && !ultWasReady) Snd.sfx("ult_ready", 0.9f);
                ultWasReady = ready;
                rs.ult = Math.min(100f, rs.ult);
            }
            // bajo de vida: latido
            if (lv != null && rs.hp / rs.stats.maxHp < 0.3f && lv.pl.alive) {
                lowHpT += dt;
                if (lowHpT > 1.1f) { lowHpT = 0; Snd.sfx("heartbeat", 0.45f); }
            }
        } else {
            in.reset();
            // el fondo sigue vivo con poca actividad
            if (ov == OV_DEAD || ov == OV_WIN) lv.update(dt * 0.5f);
        }
        // muerte -> resumen
        if (deadT >= 0) {
            deadT += dt;
            if (deadT > 1.6f && ov != OV_DEAD) { Snd.music("mus_gameover", false); RunSave.clearRun(game.P, this); openOv(OV_DEAD); }
        }
        if (winPending && lv != null) {
            winT += dt;
            if (winT > 3.0f && ov != OV_WIN) { Snd.music("mus_victory", false); openOv(OV_WIN); winPending = false; }
        }
    }

    @Override void touch(int id, int action, float x, float y) {
        if (ov != OV_NONE) { super.touch(id, action, x, y); return; }
        if (fadeMode == 1) return;
        if (!game.touchUiVisible()) return;   // con mando activo los toques no tocan el juego
        in.touch(id, action, x, y);
    }

    @Override void key(int code, boolean isDown) {
        if (ov != OV_NONE) {
            if (ov == OV_BLESS && isDown) {
                if (code == 37 || code == 'A') offerSel = (offerSel + 2) % 3;
                else if (code == 39 || code == 'D') offerSel = (offerSel + 1) % 3;
                else if ((code == 10 || code == 32 || code == 'J') && ovT > 0.35f) { for (Hit h : hits) if (h.tag == offerSel) { click(h); break; } }
                return;
            }
            if (ov == OV_TALK && isDown) {
                if (tphase != 1 && (code == 10 || code == 32 || code == 'J')) { talkTap(); return; }
                if (code == 27) { back(); return; }
            }
            if (ov == OV_CHEST && isDown) {
                if (code == 37 || code == 'A') offerSel = offerSel < 0 ? 0 : (offerSel + 2) % 3;
                else if (code == 39 || code == 'D') offerSel = offerSel < 0 ? 0 : (offerSel + 1) % 3;
                else if ((code == 10 || code == 32 || code == 'J') && ovT > 0.3f) { confirmChest(); return; }
                layoutOverlay();
                return;
            }
            super.key(code, isDown);
        }
    }

    // =============================================================== dibujo
    @Override void render(Platform.Gfx g) {
        int w = W();
        if (lv == null) { g.clear(0xFF000000); return; }
        lv.render(g);
        renderCinema(g, w);
        renderHud(g, w);
        if (ov == OV_NONE) { if (game.touchUiVisible()) renderControls(g, w); else renderPadHud(g, w); }
        renderBanner(g, w);
        renderOverlay(g, w);
        // pantalla roja al morir
        if (deadT >= 0) g.rect(0, 0, w, Platform.VIEW_H, Mth.withAlpha(0x500000, (int) (Mth.clamp(deadT / 1.5f, 0, 1) * 150)), false);
        if (fadeA > 0.001f) g.rect(0, 0, w, Platform.VIEW_H, Mth.withAlpha(0x000000, (int) (Mth.clamp(fadeA, 0, 1) * 255)), false);
    }

    private void renderCinema(Platform.Gfx g, int w) {
        if (lv.cineBars > 0.01f) {
            float h = 30 * lv.cineBars;
            g.rect(0, 0, w, h, 0xFF000000, false);
            g.rect(0, Platform.VIEW_H - h, w, h, 0xFF000000, false);
        }
        // tarjeta del jefe
        if (bossCardT >= 0 && lv.boss != null) {
            BossDef d = lv.boss.def;
            float t = bossCardT;
            if (t > 0.5f && t < 4.2f) {
                float a = Mth.clamp(Math.min((t - 0.5f) / 0.5f, (4.2f - t) / 0.6f), 0, 1);
                if (t > 0.5f && t < 0.56f) Snd.sfx("boss_title", 0.9f);
                float cy = Platform.VIEW_H - 76;
                g.rect(0, cy - 4, w, 1, Mth.withAlpha(d.color, (int) (a * 200)), true);
                g.rect(0, cy + 44, w, 1, Mth.withAlpha(d.color, (int) (a * 200)), true);
                UI.big.center(g, d.name, w / 2f, cy + 4, 0xFFE8D0C0, a);
                UI.big.center(g, d.name, w / 2f + 1, cy + 5, d.color, a * 0.35f);
                UI.small.center(g, d.title, w / 2f, cy + 26, UI.GREY, a);
            }
            if (t > 4.5f) bossCardT = -1;
        }
    }

    private void renderHud(Platform.Gfx g, int w) {
        Player pl = lv.pl;
        Stats s = rs.stats;
        if (toastT > 0 && ov == OV_NONE) UI.small.center(g, toast, w / 2f, 8, UI.GOLD, Math.min(1f, toastT));
        float ratio = s.maxHp > 0 ? rs.hp / s.maxHp : 0;
        UI.hpBar(g, 8, 8, ratio);
        UI.small.draw(g, Math.max(0, Math.round(rs.hp)) + "/" + Math.round(s.maxHp), 114, 11, ratio < 0.3f ? UI.RED : UI.WHITE, 1f);
        UI.ultBar(g, 8, 25, rs.ult / 100f, rs.ult >= 100f, lv.time);
        if (rs.ult >= 100f) UI.small.draw(g, "LISTA", 96, 26, UI.ORANGE, 0.6f + 0.4f * (float) Math.sin(lv.time * 8));
        if (pl.shield > 0) { UI.icon(g, "shield", 114, 21, 1f); UI.small.draw(g, String.valueOf(Math.round(pl.shield)), 132, 26, UI.CYAN, 1f); }
        // recursos: arriba a la derecha, junto a pausa (no estorban al personaje ni a la vida)
        float rx = w - 36;
        UI.small.right(g, String.valueOf(rs.gold), rx, 7, UI.GOLD, 1f);
        UI.icon(g, "coin", rx - UI.small.width(String.valueOf(rs.gold)) - 18, 3, 1f);
        UI.small.right(g, String.valueOf(rs.souls), rx, 21, UI.SOUL, 1f);
        UI.icon(g, "soul", rx - UI.small.width(String.valueOf(rs.souls)) - 18, 17, 1f);
        // estados alterados: fila bajo las barras
        int sx = 8;
        String[] ic = {"burn", "freeze", "shield", "poison", "shock", "bleed", "lock", "star"};
        for (int i = 0; i < Ent.ST_COUNT; i++) {
            if (pl.st[i] > 0 && i != Ent.ROOT && i != Ent.STUN) { UI.icon(g, ic[i], sx, 38, 1f, Platform.TINT, Ent.ST_COLOR[i], 1f); sx += 18; }
        }
        // sala: nombre del bioma + progreso en puntos
        if (rs.biome != null && lv.room.type != Room.HUB && lv.boss == null) {
            String t = rs.biome.name;
            UI.small.center(g, t, w / 2f, 5, 0xFFB8B0B8, 0.9f);
            int cur = Math.min(4, rs.roomNo);
            float px0 = w / 2f - 5 * 7 / 2f;
            for (int i = 0; i < 5; i++) g.rect(px0 + i * 7, 17, 5, 3, i < cur ? 0xFFB8B0B8 : (i == cur ? 0xFFFFD25A : 0x66808088), false);
        }
        // jefe
        if (lv.boss != null && lv.bossBarShow > 0.01f) {
            Boss b = lv.boss;
            float a = Mth.clamp(lv.bossBarShow, 0, 1);
            UI.small.center(g, b.def.name, w / 2f, 4, 0xFFE8D0C0, a);
            UI.bossBar(g, w / 2f, 15, b.hp / b.maxHp, a);
            if (b.phase >= 2) g.rect(w / 2f - 2, 14, 4, 2, 0xFFFF4040, false);
        }
        // reliquia
        if (relicBannerT > 0) {
            float a = Mth.clamp(Math.min(relicBannerT, 4f - relicBannerT + 0.2f) / 0.5f, 0, 1);
            UI.panel(g, 1, w / 2f - 130, 52, 260, 34, a);
            String[] keys = {"rey_exanime", "coloso_magma", "reina_escarcha", "devorador_vacio", "ent_ancestral", "titan_tormenta", "matriarca_sangre", "guardian_eclipse"};
            UI.icon(g, "r_" + keys[relicBannerIdx], w / 2f - 122, 61, 1f, 0, 0, a);
            UI.small.draw(g, "Reliquia obtenida", w / 2f - 98, 58, UI.GOLD, a);
            UI.small.draw(g, relicBanner, w / 2f - 98, 70, UI.WHITE, a);
        }
        // pista de interaccion
        Prop near = ov == OV_NONE ? lv.nearestInteractable() : null;
        if (near != null && lv.pl.alive && !lv.cinematic) {
            String lab = hintFor(near);
            if (game.touchUiVisible()) {
                Input.Btn ib = in.btn[Input.B_INTERACT];
                UI.small.center(g, lab, ib.cx, ib.cy - ib.r - 12, UI.GOLD, 1f);
            } else {
                drawGlyph(g, w / 2f - UI.small.width(lab) / 2f - 4, 196, Input.B_INTERACT);
                UI.small.draw(g, lab, w / 2f - UI.small.width(lab) / 2f + glyphW(Input.B_INTERACT) - 2, 197, UI.GOLD, 1f);
            }
            if (near.kind.equals("portal")) {
                Biome b = Biome.ALL[near.nextBiome];
                BossDef bd = BossDef.byBiome(b.id);
                UI.panel(g, 0, w / 2f - 110, 214, 220, 44, 0.9f);
                UI.small.center(g, b.name, w / 2f, 219, b.color, 1f);
                UI.small.center(g, "Jefe: " + bd.name, w / 2f, 232, UI.WHITE, 1f);
                UI.small.center(g, b.tagline, w / 2f, 244, UI.GREY, 1f);
            }
        }
        if (hintT > 0) UI.small.center(g, "No tienes suficiente oro", w / 2f, 120, UI.RED, Mth.clamp(hintT, 0, 1));
    }

    private String hintFor(Prop p) {
        switch (p.kind) {
            case "door": return p.nextType == -2 ? "Salir" : "Entrar";
            case "portal": return "Viajar";
            case "altar": return "Rezar";
            case "forge": return "Forjar";
            case "merchant": return "Comerciar";
            case "fountain": return "Beber";
            case "npc": return "Hablar";
            case "chest": return p.arg == 3 ? "¡Cofre secreto!" : "Abrir";
            default: return "Usar";
        }
    }

    private void renderBanner(Platform.Gfx g, int w) {
        if (bannerT <= 0 || (bannerTitle.isEmpty() && bannerSub.isEmpty())) return;
        float t = 3f - bannerT;
        float a = Mth.clamp(Math.min(t / 0.5f, bannerT / 0.7f), 0, 1);
        float y = 86;
        UI.light(g, w / 2f, y + 12, 140, 0x000000, 0.0f);
        g.rect(w / 2f - 120 * a, y + 24, 240 * a, 1, 0x88FFD25A, false);
        UI.big.center(g, bannerTitle, w / 2f, y, 0xFFF0E0D0, a);
        UI.small.center(g, bannerSub, w / 2f, y + 28, UI.GREY, a);
    }

    // ---- indicaciones de boton segun el dispositivo (mando Xbox / PlayStation / teclado)
    private String glyphText(int action) {
        if (game.lastDevice == 1) return Pad.keyName(Save.S.kb[action]);
        int c = Save.S.pb[action];
        return c <= 0 ? "-" : Pad.name(game.padType, c);
    }

    private int glyphColor(int action) {
        if (game.lastDevice == 1) return 0xFFE8E0D0;
        int fc = Pad.faceColor(game.padType, Save.S.pb[action]);
        return fc != 0 ? (0xFF000000 | fc) : 0xFFE8E0D0;
    }

    private float glyphW(int action) { return UI.small.width(glyphText(action)) + 10; }

    /** Pequeña etiqueta con el nombre del boton asignado a una accion; (x, y) = esquina izquierda. */
    private void drawGlyph(Platform.Gfx g, float x, float y, int action) {
        String t = glyphText(action);
        float tw = UI.small.width(t);
        g.rect(x, y, tw + 6, 11, 0xB0000010, false);
        g.rect(x, y, tw + 6, 1, 0x40FFFFFF, false);
        UI.small.draw(g, t, x + 3, y + 2, glyphColor(action), 1f);
    }

    /** Con mando: sin botones en pantalla, pero se siguen viendo habilidades, recargas y municion con su boton asignado. */
    private void renderPadHud(Platform.Gfx g, int w) {
        int[] acts = {Input.B_S1, Input.B_S2, Input.B_S3, Input.B_ULT, Input.B_GUARD, Input.B_SEC, Input.B_GREN};
        float x = w - 20, y = 237;
        Input.Btn tmp = new Input.Btn();
        for (int k = 0; k < acts.length; k++) {
            int a = acts[k];
            if (a == Input.B_SEC && rs.sec == 0) continue;
            if (a == Input.B_GREN && rs.gren == 0) continue;
            tmp.cx = x; tmp.cy = y; tmp.r = 12;
            tmp.icon = a >= Input.B_S1 && a <= Input.B_S3 ? cls.skills[a - Input.B_S1].icon : (a == Input.B_ULT ? cls.skills[3].icon : "");
            tmp.pointer = -1;
            drawBtn(g, a, tmp, 0.78f);
            drawGlyph(g, x - (UI.small.width(glyphText(a)) + 6) / 2f, y + 14, a);
            x -= 36;
        }
        // frasco de vida
        tmp.cx = 24; tmp.cy = 237; tmp.r = 12; tmp.icon = "potion"; tmp.pointer = -1;
        UI.roundButton(g, tmp.cx, tmp.cy, tmp.r, 0, 0.78f);
        UI.iconC(g, "potion", tmp.cx, tmp.cy, 1f, rs.potions > 0 ? 1f : 0.35f);
        UI.small.draw(g, "x" + rs.potions, tmp.cx + 15, tmp.cy - 4, rs.potions > 0 ? UI.WHITE : UI.GREY, 1f);
        drawGlyph(g, 6, tmp.cy + 14, Input.B_POTION);
        // peligro de vida baja
        float hr = rs.hp / rs.stats.maxHp;
        if (hr < 0.3f && lv.pl.alive) {
            int al = (int) (40 + 30 * Math.sin(lv.time * 6));
            g.rect(0, 0, w, 3, Mth.withAlpha(0xC00020, al), false);
            g.rect(0, Platform.VIEW_H - 3, w, 3, Mth.withAlpha(0xC00020, al), false);
        }
    }

    /** Dibuja un boton de accion (habilidad, arma 2ª, granada, escudo, pocion...) en la posicion del boton b. */
    private void drawBtn(Platform.Gfx g, int i, Input.Btn b, float alpha) {
        UI.roundButton(g, b.cx, b.cy, b.r, b.pointer >= 0 ? 1 : 0, alpha);
        if (i >= Input.B_S1 && i <= Input.B_ULT) {
            boolean ult = i == Input.B_ULT;
            if (b.icon != null) UI.iconC(g, b.icon, b.cx, b.cy, 1f, 1f);
            if (ult) {
                float r = rs.ult / 100f;
                if (r > 0 && r < 1) {
                    g.clipBegin(b.cx - b.r, b.cy + b.r - 2 * b.r * r, 2 * b.r, 2 * b.r * r + 1);
                    g.circle(b.cx, b.cy, b.r - 1, 0x66FFB030, true);
                    g.clipEnd();
                } else if (r >= 1) {
                    UI.light(g, b.cx, b.cy, b.r + 8, 0xFFB030, 0.45f + 0.25f * (float) Math.sin(lv.time * 9));
                }
                if (r < 1) g.circle(b.cx, b.cy, b.r - 1, 0x66000000, false);
            } else {
                int k = i - Input.B_S1;
                float cdMax = Math.max(0.5f, cls.skills[k].cd * rs.stats.cdMul);
                float cd = rs.cd[k];
                if (cd > 0) {
                    float f = Mth.clamp(cd / cdMax, 0, 1);
                    g.clipBegin(b.cx - b.r, b.cy - b.r, 2 * b.r, 2 * b.r * f + 1);
                    g.circle(b.cx, b.cy, b.r - 1, 0xAA000000, false);
                    g.clipEnd();
                    UI.small.center(g, String.valueOf((int) Math.ceil(cd)), b.cx, b.cy - 4, UI.WHITE, 1f);
                }
            }
            return;
        }
        if (i == Input.B_GUARD) {
            boolean on = lv.pl.guarding;
            g.circle(b.cx, b.cy, b.r - 1, Mth.withAlpha(Items.SH_COL[rs.shield], on ? 150 : 60), false);
            UI.iconC(g, "shield", b.cx, b.cy, 1f, 1f);
            if (lv.pl.parryT > 0) g.circle(b.cx, b.cy, b.r + 2, 0xFFFFE070, true);
            else if (lv.pl.parryCd > 0.1f && on) { g.clipBegin(b.cx - b.r, b.cy - b.r, 2 * b.r, 2 * b.r * Mth.clamp(lv.pl.parryCd / 0.7f, 0, 1) + 1); g.circle(b.cx, b.cy, b.r - 1, 0x88000000, false); g.clipEnd(); }
            return;
        }
        if (i == Input.B_SEC || i == Input.B_GREN) {
            boolean sec = i == Input.B_SEC;
            int ty = sec ? rs.sec : rs.gren, n = sec ? rs.secAmmo : rs.grenCount;
            int col = sec ? Items.SEC_COL[ty] : Items.GR_COL[ty];
            g.circle(b.cx, b.cy, b.r - 1, Mth.withAlpha(col, 70), false);
            UI.iconC(g, sec ? Items.SEC_ICON[ty] : Items.GR_ICON[ty], b.cx, b.cy - 1, 1f, n > 0 ? 1f : 0.35f);
            UI.small.center(g, String.valueOf(n), b.cx, b.cy + b.r - 9, n > 0 ? UI.WHITE : UI.RED, 1f);
            float cdv = sec ? lv.pl.secCd : lv.pl.grenCd;
            if (cdv > 0) { g.clipBegin(b.cx - b.r, b.cy - b.r, 2 * b.r, 2 * b.r * Mth.clamp(cdv / 0.5f, 0, 1) + 1); g.circle(b.cx, b.cy, b.r - 1, 0xAA000000, false); g.clipEnd(); }
            return;
        }
        if (i == Input.B_POTION) {
            UI.iconC(g, "potion", b.cx, b.cy, 1f, rs.potions > 0 ? 1f : 0.35f);
            UI.small.draw(g, "x" + rs.potions, b.cx + 14, b.cy - 4, rs.potions > 0 ? UI.WHITE : UI.GREY, 1f);
            return;
        }
        if (b.icon != null && !b.icon.isEmpty()) UI.iconC(g, b.icon, b.cx, b.cy, i == Input.B_ATTACK ? 1.5f : 1f, 1f);
    }

    private void renderControls(Platform.Gfx g, int w) {
        in.btn[Input.B_INTERACT].visible = in.btn[Input.B_INTERACT].visible && !lv.cinematic;
        in.btn[Input.B_SEC].visible = rs.sec != 0 && !lv.cinematic;
        in.btn[Input.B_GREN].visible = rs.gren != 0 && !lv.cinematic;
        // iconos de habilidades
        for (int i = 0; i < 3; i++) in.btn[Input.B_S1 + i].icon = cls.skills[i].icon;
        in.btn[Input.B_ULT].icon = cls.skills[3].icon;
        drawStick(g);
        for (int i = 0; i < Input.B_COUNT; i++) {
            Input.Btn b = in.btn[i];
            if (!b.visible) continue;
            if (i == Input.B_PAUSE) { UI.roundButton(g, b.cx, b.cy, b.r, b.pointer >= 0 ? 1 : 0, 0.7f); UI.iconC(g, "pause", b.cx, b.cy, 1f, 0.9f); continue; }
            if (i == Input.B_LEFT || i == Input.B_RIGHT || i == Input.B_DOWN) continue;   // dibujados por el joystick
            drawBtn(g, i, b, 0.7f);
        }
        // peligro de vida baja
        float hr = rs.hp / rs.stats.maxHp;
        if (hr < 0.3f && lv.pl.alive) {
            int a = (int) (40 + 30 * Math.sin(lv.time * 6));
            g.rect(0, 0, w, 3, Mth.withAlpha(0xC00020, a), false);
            g.rect(0, Platform.VIEW_H - 3, w, 3, Mth.withAlpha(0xC00020, a), false);
        }
    }

    /** Joystick de movimiento: base con flechas, el pulgar sigue el dedo y la base lo persigue si se aleja. */
    private void drawStick(Platform.Gfx g) {
        boolean on = in.stickActive();
        float R = in.stickR(), cx = in.anchorX(), cy = in.anchorY();
        UI.roundButton(g, cx, cy, R, 0, on ? 0.5f : 0.34f);
        if (UI.arrow != null) {
            float[][] p = {{-1, 0, 3.1416f}, {1, 0, 0}, {0, 1, 1.5708f}};
            boolean[] act = {in.stickL(), in.stickR_(), in.stickD()};
            for (int k = 0; k < 3; k++) {
                float ax = cx + p[k][0] * (R - 11), ay = cy + p[k][1] * (R - 11);
                g.imageRot(UI.arrow, 0, 0, 8, 8, ax - 6, ay - 6, 12, 12, p[k][2], 0, 0, act[k] ? 1f : (on ? 0.6f : 0.45f));
            }
        }
        float kx = in.thumbX() - cx, ky = in.thumbY() - cy, kd = (float) Math.sqrt(kx * kx + ky * ky), kr = R * 0.78f;
        if (kd > kr) { kx *= kr / kd; ky *= kr / kd; }
        UI.roundButton(g, cx + kx, cy + ky, R * 0.46f, on ? 1 : 0, on ? 0.95f : 0.6f);
    }

    private void dim(Platform.Gfx g, int w, float a) { g.rect(0, 0, w, Platform.VIEW_H, Mth.withAlpha(0x000008, (int) (a * 255)), false); }

    private void renderOverlay(Platform.Gfx g, int w) {
        if (ov == OV_NONE) return;
        float fadeIn = Mth.clamp(ovT / 0.2f, 0, 1);
        switch (ov) {
            case OV_BLESS: {
                dim(g, w, 0.62f * fadeIn);
                UI.big.center(g, "ELIGE UNA BENDICIÓN", w / 2f, 20, UI.GOLD, fadeIn);
                UI.small.center(g, "Mejoras que duran toda la partida", w / 2f, 38, UI.GREY, fadeIn);
                for (Hit h : hits) {
                    int i = h.tag;
                    Blessing b = Blessing.ALL[offer[i]];
                    boolean selected = down == h || (game.keyboardUsed && offerSel == i);
                    float yoff = selected ? -4 : 0;
                    UI.panel(g, selected ? 1 : 0, h.x, h.y + yoff, h.w, h.h, fadeIn);
                    UI.iconC(g, b.icon, h.x + h.w / 2f, h.y + 28 + yoff, 2f, fadeIn);
                    UI.small.center(g, b.name, h.x + h.w / 2f, h.y + 54 + yoff, UI.GOLD, fadeIn);
                    int cur = rs.bless[b.id];
                    UI.small.center(g, cur == 0 ? "NUEVA" : "Nv " + cur + " > " + (cur + 1), h.x + h.w / 2f, h.y + 67 + yoff, cur == 0 ? UI.GREEN : UI.CYAN, fadeIn);
                    UI.small.drawWrapped(g, b.desc, h.x + 8, h.y + 84 + yoff, (int) h.w - 16, 0xE8E0E0, fadeIn);
                }
                break;
            }
            case OV_CHEST: {
                if (cOffer == null) break;
                dim(g, w, 0.66f * fadeIn);
                UI.big.center(g, ChestLoot.MODE_TITLE[cMode], w / 2f, 10, UI.GOLD, fadeIn);
                UI.small.center(g, ChestLoot.MODE_SUB[cMode], w / 2f, 28, UI.GREY, fadeIn);
                for (Hit h : hits) {
                    if (h.tag < 0 || h.tag > 2 || h.label != null) continue;
                    int i = h.tag;
                    ChestLoot.Reward x = cOffer[i];
                    boolean sel = offerSel == i;
                    int rc = ChestLoot.R_COL[x.rar];
                    float yo = sel ? -5 : 0, cx = h.x + h.w / 2f, y = h.y + yo;
                    UI.panel(g, sel ? 1 : 0, h.x, y, h.w, h.h, fadeIn);
                    int ba = (int) (fadeIn * (sel ? 255 : 170));
                    int bc = Mth.withAlpha(rc, ba);
                    g.rect(h.x + 3, y + 3, h.w - 6, 2, bc, false);
                    g.rect(h.x + 3, y + h.h - 5, h.w - 6, 2, bc, false);
                    if (sel) { g.rect(h.x + 1, y + 1, 2, h.h - 2, bc, false); g.rect(h.x + h.w - 3, y + 1, 2, h.h - 2, bc, false); }
                    UI.small.center(g, ChestLoot.R_NAME[x.rar].toUpperCase(), cx, y + 9, rc, fadeIn);
                    UI.light(g, cx, y + 38, 22 + x.rar * 5, rc & 0xFFFFFF, (0.18f + 0.07f * x.rar + (sel ? 0.12f : 0f)) * fadeIn);
                    if (!x.icon.isEmpty()) UI.iconC(g, x.icon, cx, y + 38, 2f, fadeIn);
                    UI.small.center(g, x.name, cx, y + 60, x.col != 0xFFFFFFFF ? x.col : UI.GOLD, fadeIn);
                    UI.small.center(g, x.amount, cx, y + 73, x.kind == ChestLoot.K_STAT || x.kind == ChestLoot.K_TRADE || x.kind == ChestLoot.K_HEAL ? UI.GREEN : UI.CYAN, fadeIn);
                    float ty = y + 87;
                    if (!x.bad.isEmpty()) { UI.small.center(g, x.bad, cx, ty, UI.RED, fadeIn); ty += 12; }
                    int lines = UI.small.drawWrapped(g, x.desc, h.x + 8, ty, (int) h.w - 16, 0xE8E0E0, fadeIn);
                    if (!x.replaces.isEmpty()) UI.small.drawWrapped(g, x.replaces, h.x + 8, y + h.h - 26, (int) h.w - 16, 0xFFFF9A6A, fadeIn);
                }
                drawButtons(g);
                break;
            }
            case OV_SHOP: {
                dim(g, w, 0.6f * fadeIn);
                UI.big.center(g, "MERCADER", w / 2f, 16, UI.GOLD, 1f);
                UI.icon(g, "coin", w / 2f - 24, 34, 1f);
                UI.small.draw(g, String.valueOf(rs.gold), w / 2f - 6, 38, UI.GOLD, 1f);
                float cw = Math.min(190, (w - 40) / 2f), ch = 54, x0 = w / 2f - cw - 3;
                for (int i = 0; i < shop.size(); i++) {
                    ShopItem it = shop.get(i);
                    float x = x0 + (i % 2) * (cw + 6), y = 52 + (i / 2) * (ch + 6);
                    boolean afford = rs.gold >= it.cost;
                    UI.panel(g, it.sold ? 2 : 0, x, y, cw, ch, it.sold ? 0.5f : 1f);
                    UI.iconC(g, it.icon, x + 22, y + 22, 2f, it.sold ? 0.4f : 1f);
                    UI.small.draw(g, it.name, x + 44, y + 5, it.sold ? UI.GREY : UI.WHITE, 1f);
                    UI.small.drawWrapped(g, it.desc, x + 44, y + 18, (int) cw - 50, UI.GREY, 1f);
                    if (it.sold) UI.small.right(g, "VENDIDO", x + cw - 6, y + ch - 12, UI.GREY, 1f);
                    else {
                        UI.icon(g, "coin", x + cw - 14 - UI.small.width(String.valueOf(it.cost)) - 6, y + ch - 14, 1f);
                        UI.small.right(g, String.valueOf(it.cost), x + cw - 6, y + ch - 12, afford ? UI.GOLD : UI.RED, 1f);
                    }
                }
                drawButtons(g);
                break;
            }
            case OV_TALK: {
                dim(g, w, 0.35f * fadeIn);
                if (talk != null) {
                    UI.small.center(g, talk.title, w / 2f, 26, UI.GOLD, fadeIn);
                    float bw = Math.min(w - 40, 430), bx = w / 2f - bw / 2f;
                    if (tphase != 1) tdlg.draw(g, bx, 190, bw, 56, fadeIn, ovT);
                    drawButtons(g);
                }
                break;
            }
            case OV_FORGE: {
                dim(g, w, 0.6f * fadeIn);
                float px = w / 2f - 130;
                UI.panel(g, 0, px, 40, 260, 168, 1f);
                UI.big.center(g, "FORJA", w / 2f, 48, UI.ORANGE, 1f);
                UI.small.center(g, cls.weapon, w / 2f, 70, UI.WHITE, 1f);
                int lvl = rs.weaponLvl;
                for (int i = 0; i < 5; i++) UI.icon(g, "star", w / 2f - 45 + i * 18, 86, 1f, i < lvl ? 0 : Platform.TINT, i < lvl ? 0 : 0x303038, 1f);
                if (lvl >= 5) UI.small.center(g, "¡Arma al nivel máximo!", w / 2f, 112, UI.GOLD, 1f);
                else {
                    UI.small.center(g, "Nivel " + lvl + " > " + (lvl + 1), w / 2f, 110, UI.CYAN, 1f);
                    UI.small.center(g, "+10% de daño de arma y habilidades", w / 2f, 124, UI.GREEN, 1f);
                    int cost = rs.forgeCost();
                    UI.icon(g, "coin", w / 2f - 30, 140, 1f);
                    UI.small.draw(g, cost + "", w / 2f - 12, 144, rs.gold >= cost ? UI.GOLD : UI.RED, 1f);
                    UI.small.draw(g, "(tienes " + rs.gold + ")", w / 2f + 20, 144, UI.GREY, 1f);
                }
                drawButtons(g);
                break;
            }
            case OV_PAUSE: {
                dim(g, w, 0.72f);
                float px = w / 2f - 220;
                UI.panel(g, 0, px, 14, 440, 238, 0.98f);
                UI.big.center(g, "PAUSA", w / 2f, 22, UI.GOLD, 1f);
                drawButtons(g);
                // info
                float ix = px + 184;
                if (saveMenu) {
                    for (int i = 0; i < RunSave.SLOTS; i++) {
                        String inf = RunSave.info(game.P, i);
                        if (inf == null) UI.small.draw(g, "Vacía", ix, 57 + i * 28, UI.GREY, 1f);
                        else {
                            String[] pt = inf.split(" · ", 3);
                            UI.small.draw(g, pt[0], ix, 52 + i * 28, UI.WHITE, 1f);
                            UI.small.draw(g, pt.length > 1 ? pt[1] : "", ix, 63 + i * 28, UI.GREY, 1f);
                            UI.small.draw(g, pt.length > 2 ? pt[2].replace(" · ", "  ") : "", ix + 150, 63 + i * 28, UI.GREY, 1f);
                        }
                    }
                    if (toastT > 0) UI.small.draw(g, toast, ix, 57 + 3 * 28 + 10, UI.GOLD, 1f);
                    break;
                }
                UI.small.draw(g, cls.name, ix, 54, cls.color1, 1f);
                UI.small.draw(g, rs.biome == null ? "Santuario" : rs.biome.name + " · Sala " + Math.min(5, rs.roomNo + 1), ix, 66, UI.GREY, 1f);
                Stats s = rs.stats;
                UI.small.draw(g, "Daño x" + fmt(s.dmgMul) + "   Crítico " + Math.round(s.critChance * 100) + "%", ix, 82, UI.WHITE, 1f);
                UI.small.draw(g, "Velocidad x" + fmt(s.speedMul) + "   Defensa " + Math.round((1 - s.dmgTaken) * 100) + "%", ix, 94, UI.WHITE, 1f);
                UI.small.draw(g, "Arma nivel " + rs.weaponLvl + "   Frascos " + rs.potions + "/" + s.potionsMax, ix, 106, UI.WHITE, 1f);
                UI.small.draw(g, "Enemigos " + rs.kills + "   Tiempo " + time(rs.time), ix, 118, UI.GREY, 1f);
                UI.small.draw(g, "Especial: " + (rs.special == 0 ? "-" : Items.SP_NAME[rs.special]), ix, 130, rs.special == 0 ? UI.GREY : Items.SP_COL[rs.special], 1f);
                UI.small.draw(g, "2ª: " + (rs.sec == 0 ? "-" : Items.SEC_NAME[rs.sec] + " x" + rs.secAmmo) + (rs.gren == 0 ? "" : "  Gran: x" + rs.grenCount), ix, 141, UI.WHITE, 1f);
                UI.small.draw(g, Items.SH_NAME[rs.shield] + " (parry " + Math.round(Items.SH_WIN[rs.shield] * 1000) + "ms)", ix, 152, Items.SH_COL[rs.shield] | 0x404040, 1f);
                UI.small.draw(g, "Bendiciones", ix, 167, UI.GOLD, 1f);
                int n = 0;
                for (Blessing b : Blessing.ALL) {
                    int lv2 = rs.bless[b.id];
                    if (lv2 <= 0) continue;
                    float bx = ix + (n % 8) * 26, by = 180 + (n / 8) * 24;
                    UI.panel(g, 0, bx, by, 22, 22, 1f);
                    UI.iconC(g, b.icon, bx + 11, by + 11, 1f, 1f);
                    UI.small.draw(g, String.valueOf(lv2), bx + 15, by + 13, UI.GOLD, 1f);
                    n++;
                }
                if (n == 0) UI.small.draw(g, "Aún no tienes ninguna.", ix, 182, UI.GREY, 1f);
                break;
            }
            case OV_DEAD: case OV_WIN: {
                boolean win = ov == OV_WIN;
                dim(g, w, 0.7f * fadeIn);
                float px = w / 2f - 150;
                UI.panel(g, win ? 1 : 2, px, 30, 300, 210, fadeIn);
                UI.big.center(g, win ? "¡VICTORIA!" : "HAS CAÍDO", w / 2f, 40, win ? UI.GOLD : UI.RED, fadeIn);
                UI.small.center(g, win ? (rs.finalRun ? "El Cazador ha sido derrotado" : "Has superado las tres mazmorras") : (rs.biome == null ? "En el Santuario" : "Caíste en " + rs.biome.name + " · sala " + Math.min(5, rs.roomNo + 1)), w / 2f, 62, UI.GREY, fadeIn);
                float y = 84;
                String[][] rows = {{"Salas superadas", String.valueOf(rs.roomsDone)}, {"Enemigos derrotados", String.valueOf(rs.kills)}, {"Jefes derrotados", String.valueOf(rs.bossKills)},
                        {"Tiempo", time(rs.time)}, {"Dificultad", (rs.diff == 0 ? "Fácil" : rs.diff == 2 ? "Difícil" : "Normal") + (rs.asc == 0 ? "" : " Asc " + rs.asc)}};
                for (String[] r : rows) {
                    UI.small.draw(g, r[0], px + 24, y, UI.WHITE, fadeIn);
                    UI.small.right(g, r[1], px + 276, y, UI.GOLD, fadeIn);
                    y += 13;
                }
                y += 6;
                UI.icon(g, "soul", px + 24, y - 3, 1f);
                UI.small.draw(g, "Almas conservadas", px + 44, y, UI.SOUL, fadeIn);
                UI.small.right(g, "+" + sumSouls, px + 276, y, UI.SOUL, fadeIn);
                if (!sumNote.isEmpty()) UI.small.center(g, sumNote, w / 2f, y + 16, UI.GREEN, fadeIn);
                if (!win && cls != null) UI.small.center(g, "Gasta tus almas en el Santuario", w / 2f, 192, UI.GREY, fadeIn);
                drawButtons(g);
                break;
            }
            default: break;
        }
    }

    private static String fmt(float v) { return String.valueOf(Math.round(v * 100) / 100f); }

    private static String time(float t) {
        int s = (int) t;
        return (s / 60) + ":" + (s % 60 < 10 ? "0" : "") + (s % 60);
    }
}
