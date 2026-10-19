package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/** La partida: salas, HUD, controles tactiles, altares, tienda, forja, jefes, muerte y victoria. */
final class RunScreen extends Screen implements Level.Listener {
    static final int OV_NONE = 0, OV_PAUSE = 1, OV_BLESS = 2, OV_SHOP = 3, OV_FORGE = 4, OV_DEAD = 5, OV_WIN = 6, OV_CHEST = 7, OV_TALK = 8, OV_REVIVE = 9, OV_EVENT = 10, OV_BLESSLIST = 11, OV_WCMP = 12, OV_INV = 13;
    static final String[] RELIC_NAMES = {"Corona Exánime", "Corazón de Magma", "Lágrima de Escarcha", "Ojo del Vacío", "Savia Ancestral", "Chispa del Titán", "Cáliz de Sangre", "Disco del Eclipse"};

    static final class ShopItem {
        String name, desc, icon; int cost, kind, arg; boolean sold;
        ShopItem(String n, String d, String i, int c, int k, int a) { name = n; desc = d; icon = i; cost = c; kind = k; arg = a; }
    }

    /** Opcion de un suceso especial (espiritu, santuario): ventaja, precio y accion. */
    static final class EvOpt {
        String icon, name, pro, con; boolean ok; Runnable act;
        EvOpt(String icon, String name, String pro, String con, boolean ok, Runnable act) { this.icon = icon; this.name = name; this.pro = pro; this.con = con; this.ok = ok; this.act = act; }
    }
    List<EvOpt> evOpts = new ArrayList<>();
    String evTitle = "", evSub = "";
    Prop evProp;
    int evSel;

    final ClassDef cls;
    final RunState rs;
    final Inventory inv = new Inventory(this);
    final Input in;
    Level lv;
    int ov;
    float ovT;
    float fadeA = 1f;
    int fadeMode = -1;
    Runnable fadeAct;
    String bannerTitle = "", bannerSub = "";
    float bannerT;
    final Tutorial tut = new Tutorial();
    final ContextBtn ctx = new ContextBtn();
    float bossCardT = -1;
    int[] offer = new int[3];
    int offerSel;
    private int blTab, blPage;         // lista de bendiciones activas: pestana (0 bendiciones, 1 sinergias) y pagina
    private int[] blRows = new int[0];
    ChestLoot.Reward[] cOffer;      // las 3 opciones del cofre abierto
    private ChestLoot.Reward wcmp;  // arma de cofre pendiente de confirmar el intercambio (OV_WCMP)
    private int wcmpSel;            // 0 = Conservar la actual (por defecto), 1 = Intercambiar
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
        r.sandbox = true; r.rs.markTest();
        r.sbEnemy = enemy; r.sbElite = elite; r.sbBoss = boss; r.sbBiome = Math.max(0, Math.min(8, biome)); r.sbBack = back;
        r.rs.biome = Biome.ALL[r.sbBiome]; r.rs.stage = Biome.ALL[r.sbBiome].tier;
        r.rs.gold = Save.devGold;
        r.resumeType = boss >= 0 ? Room.BOSS : Room.COMBAT;
        return r;
    }

    /** Nueva run del modo infinito (solo se ofrece tras completar la campana). */
    static RunScreen infinite(Game g, ClassDef c, int asc) {
        RunScreen r = new RunScreen(g, c, asc);
        RunState rs = r.rs;
        rs.infinite = true; rs.stage = 2; rs.floor = 1; rs.ruleset = Infinite.NORMAL;
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
    float reviveWait = -1;            // modo infinito: espera antes de ofrecer revivir
    Infinite.Result infResult;        // resultado final de la run infinita (al terminar)
    boolean infRecord;                // fue record de pisos
    String reviveMsg = "";
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
        Inventory.seeAll(rs);
    }

    @Override void enter() {
        in.reset();
        if (lv == null && resumeType >= 0) {
            int t = resumeType; resumeType = -1;
            if (t == Room.HUB) { int id = autoBiome(); t = id == 8 ? Room.BOSS : Room.COMBAT; }   // partidas guardadas con el antiguo santuario
            loadRoom(t);
            fadeA = 1f; fadeMode = -1;
        } else if (lv == null) {
            // sin santuario de portales: el siguiente bioma del tramo se elige solo
            int id = autoBiome();
            loadRoom(id == 8 ? Room.BOSS : Room.COMBAT);
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

    /** Elige el siguiente bioma del tramo actual (aleatorio entre los no visitados; el Cazador al final) y lo prepara. */
    private int autoBiome() {
        int id;
        if (rs.infinite) {
            java.util.List<Integer> ids = new ArrayList<>();
            for (int k = 0; k < 8; k++) if (!rs.visited.contains(k)) ids.add(k);
            if (ids.isEmpty()) { int last = rs.biome == null ? -1 : rs.biome.id; rs.visited.clear(); for (int k = 0; k < 8; k++) if (k != last) ids.add(k); }
            id = ids.get(rs.rng.i(ids.size()));
            rs.biome = Biome.ALL[id];
            rs.visited.add(id);
            rs.roomNo = 0;
            rs.blessingTaken = false; rs.eventBiomeDone = false;
            return id;
        }
        if (rs.stage >= 3) id = 8;
        else {
            java.util.List<Integer> ids = new ArrayList<>();
            for (Biome bb : Biome.ALL) if (bb.tier == rs.stage && bb.id < 8 && !rs.visited.contains(bb.id)) ids.add(bb.id);
            if (ids.isEmpty()) for (Biome bb : Biome.ALL) if (bb.tier == rs.stage && bb.id < 8) ids.add(bb.id);
            id = ids.get(rs.rng.i(ids.size()));
        }
        rs.biome = Biome.ALL[id];
        rs.visited.add(id);
        rs.roomNo = id == 8 ? 4 : 0;
        rs.blessingTaken = false; rs.eventBiomeDone = false;
        if (id == 8) rs.finalRun = true;
        return id;
    }

    private Biome hubBiome() { return Biome.ALL[7]; }

    void loadRoom(int type) {
        Platform P = game.P;
        Biome b = type == Room.HUB || rs.biome == null ? hubBiome() : rs.biome;
        if (type != Room.EVENT && !(type == Room.ELITE && rs.curEvent == Events.TRIAL)) rs.curEvent = 0;
        RoomGen.extraTraps = Infinite.has(rs, Infinite.M_TRAPS) ? 3 : 0;
        Room rm = RoomGen.generate(type, b, rs.rng, rs.stage, rs.roomNo, type == Room.EVENT ? rs.curEvent : 0);
        RoomGen.extraTraps = 0;
        rm.bake(P);
        String left = Arsenal.leaveRoom(rs, lv);          // armas que se quedaron en el suelo de la sala anterior
        lv = new Level(P, rs, rm, in);
        if (left != null) { toast = left; toastT = 3f; }
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
        else if (type == Room.COMBAT && rs.curEvent == 0 && !sandbox) addSideDoor(true);   // el mercader errante puede encontrarse durante la exploracion
        challengeInit(type);
        // banner
        if (type == Room.HUB) {
            bannerTitle = rs.stage >= 3 ? "El Sello está completo" : "Santuario del Viajero";
            bannerSub = rs.stage == 0 && rs.visited.isEmpty() ? "Elige tu primer destino" : (rs.stage >= 3 ? "Solo queda el Cazador" : "Elige tu próximo destino");
        } else if (type == Room.BOSS) {
            bannerTitle = ""; bannerSub = "";
        } else {
            bannerTitle = rs.biome.name;
            bannerSub = rs.roomNo == 0 ? rs.biome.tagline : (type == Room.REST ? "Tienda · forja · altar · fuente" : RunState.roomName(type));
            if (type == Room.EVENT || (type == Room.ELITE && rs.curEvent == Events.TRIAL)) { bannerTitle = Events.NAME[rs.curEvent]; bannerSub = Events.SUB[rs.curEvent]; }
            if (chal >= 0) { bannerTitle = Events.NAME[Events.CHALLENGE] + ": " + Events.CH_NAME[chal]; bannerSub = Events.CH_RULE[chal]; }
        }
        bannerT = type == Room.BOSS ? 0 : 3f;
        // tutorial
        tut.close();                                              // salir de la sala cuenta como visto: nunca se repite
        if (!sandbox && type != Room.HUB) Tutorial.complete(Tutorial.PORTAL);
        if (!sandbox && type == Room.HUB && rs.visited.isEmpty() && !Tutorial.done(Tutorial.PORTAL)) lv.tutorial = "Acércate a un portal\ny pulsa el botón de la llave";
        // controles: solo la primera vez que este perfil entra en su primera mazmorra (el estado vive en Save, no en la sala ni en el bioma)
        if (!sandbox && type == Room.COMBAT && rs.roomNo == 0 && rs.stage == 0 && rs.visited.size() <= 1 && rs.bossKills == 0 && !rs.infinite
                && !Tutorial.done(Tutorial.CONTROLS)) tut.start();
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
        if (rm.type == Room.EVENT && rs.curEvent == Events.MERCHANT && rs.sideOrigin >= 0) {   // salida del mercader: vuelve al piso de origen (NO es la salida principal)
            Prop d = lv.addProp(new Room.PropSpec("door", rm.exitX, rm.exitY, 0));
            d.doorIdx = 0; d.nextType = -3; d.label = "Volver"; d.anim = "open"; d.animT = 0;
            Snd.sfx("door_open", 0.8f);
            return;
        }
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
        // puerta lateral opcional hacia un suceso especial (solo tras salas de combate normales; jamas sustituye a la puerta principal)
        if (rm.type == Room.COMBAT && rs.curEvent == 0 && !sandbox) addSideDoor(false);
        Snd.sfx("door_open", 0.8f);
    }

    /** Puerta lateral hacia un suceso. earlyOnly: solo el mercader errante, que puede aparecer antes de despejar la sala. */
    private void addSideDoor(boolean earlyOnly) {
        Room rm = lv.room;
        for (Prop q : lv.props) if (q.kind.equals("door") && q.event > 0) return;   // ya hay una (o ya se uso): no se duplica
        int next = rs.roomNo + 1;
        Rng er = new Rng(rs.seed ^ (rs.stage * 1315423911L + rs.roomNo * 2654435761L + (rs.biome == null ? 0 : rs.biome.id) * 97L + rs.floor * 7919L));
        int ek = Events.roll(rs, er, next);
        if (earlyOnly && ek != Events.MERCHANT) return;
        float[] sd = ek > 0 ? Events.sideDoor(rm) : null;
        if (ek > 0 && sd != null) {
            Prop d = lv.addProp(new Room.PropSpec("door", sd[0], sd[1], 0));
            d.doorIdx = 1; d.event = ek; d.nextType = ek == Events.TRIAL ? Room.ELITE : Room.EVENT;
            d.icon = Events.ICON[ek]; d.tint = Events.GLOW[ek]; d.label = Events.NAME[ek];
            d.anim = "open"; d.animT = 0;
            if (earlyOnly) Snd.sfx("door_open", 0.5f);
        }
    }

    // =============================================================== Level.Listener
    @Override public void onCleared(Level l) {
        if (sandbox) { sbRespawnT = 1.6f; l.text(l.pl.x, l.pl.y - 50, "Reiniciando prueba...", 0xFFD25A, true); return; }
        Snd.sfx("room_clear", 0.9f);
        l.text(l.pl.x, l.pl.y - 50, "¡Sala despejada!", 0xFFD25A, true);
        if (l.room.type == Room.COMBAT || l.room.type == Room.ELITE) completeRound(l);
        if (rs.curEvent > 0 && (l.room.type == Room.EVENT || l.room.type == Room.ELITE)) Codex.see(rs, "v:" + rs.curEvent, Events.NAME[rs.curEvent]);
        if (l.room.type == Room.ELITE && rs.curEvent == Events.TRIAL) trialReward(l);
        if (l.room.type == Room.EVENT && rs.curEvent == Events.CURSED && ambushOn) { ambushOn = false; cursedReward(l); }
        if (l.room.type == Room.EVENT && rs.curEvent == Events.CHALLENGE) challengeCleared(l);
        if (l.room.type == Room.EVENT && rs.curEvent == Events.CAPTIVE) l.text(l.pl.x, l.pl.y - 66, "Guardias derrotados: libera al prisionero", 0xB8A0D0, true);
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
        // hallazgo extra: a veces queda un arma secundaria en el suelo junto a los cofres (no sustituye ninguna recompensa)
        if (!sandbox && l.rng.chance(l.room.type == Room.ELITE ? 0.5f : 0.2f)) {
            int wid = Arsenal.rollWeapon(rs, l.rng, rs.sec);
            Arsenal.dropWeapon(l, wid, 0, l.room.exitX - 70 - n * 38 - 36, l.room.exitY, false, false);
            l.text(l.pl.x, l.pl.y - 82, "Hay un arma en el suelo", Items.SEC_COL[wid], false);
        }
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

    /** Premio superior de la prueba de combate: un cofre extra de alta calidad y almas. */
    private void trialReward(Level l) {
        Prop c = l.addProp(new Room.PropSpec("chest", l.room.exitX - 70 - lastRoundChests * 38, l.room.exitY, 2));
        c.label = "Premio de la prueba"; c.roundChest = true;
        l.ps.burst(l.rng, c.x, c.y - 12, 0xFF8A50, 26, 120, 0.7f, 2, 0, true);
        l.dropSouls(l.pl.x, l.pl.y - 20, 20 + 6 * rs.stage);
        l.text(l.pl.x, l.pl.y - 82, "¡Prueba superada! Premio superior", 0xFF8A50, true);
    }

    float playSave;
    int lastRoundChests;   // (pruebas) cofres entregados en la ultima ronda

    private void announceTrophies() {
        java.util.List<String> nw = Trophies.check(Save.S);
        if (!nw.isEmpty()) { toast = "Trofeo: " + nw.get(0); toastT = 3.5f; }
    }

    @Override public void onPlayerDead(Level l) {
        if (rs.infinite && !sandbox && reviveWait < 0 && Infinite.hasRevivesLeft(rs) && Infinite.anyAvailable(rs)) { reviveWait = 0; return; }
        if (deadT < 0) { deadT = 0; endRun(false); }
    }

    @Override public void onBossDead(Level l) {
        if (sandbox) { l.bossFight = false; sbRespawnT = 3.5f; return; }
        BossDef d = l.boss.def;
        l.bossFight = false;
        l.cleared = true;
        if (!(d.idx == 8 && d.form < 2)) l.pl.react("victory", 5f);
        rs.roomsDone++;
        if (rs.infinite) rs.infRooms++;
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
        // jefe normal: a veces suelta un arma secundaria (al menos poco comun)
        if (l.rng.chance(0.5f)) {
            int wid = Arsenal.rollWeapon(rs, l.rng, rs.sec);
            Arsenal.dropWeapon(l, wid, 0, l.room.exitX - 56, l.room.exitY, false, false);
            l.text(l.pl.x, l.pl.y - 82, "El jefe dejó un arma", Items.SEC_COL[wid], false);
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
        if (!(rs.infinite && rs.infFromCampaign)) { s.runs++; s.classRuns[cls.id]++; }   // la continuacion de la campana ya conto esta partida
        if (!win && !rs.infinite) s.losses++;                                            // morir en el infinito es un resultado, no una derrota de campana
        s.kills += rs.kills - rs.credKills; s.bossKills += rs.bossKills - rs.credBoss;   // solo lo no contado antes
        rs.credKills = rs.kills; rs.credBoss = rs.bossKills;
        s.bestRooms = Math.max(s.bestRooms, rs.roomsDone);
        if (rs.infinite) { infResult = Infinite.resultOf(rs); infRecord = Infinite.record(s, infResult); }
        s.lastClass = cls.id;
        Tutorial.complete(Tutorial.ALL);
        if (win) {
            s.wins++; s.classWins[cls.id]++;
            if (rs.asc == s.ascension && s.ascension < 5) { s.ascension++; sumNote = "¡Nueva dificultad desbloqueada!"; }
        }
        s.write();
    }

    private void afterBoss() {
        if (rs.infinite) {
            rs.floorsDone++; rs.floor++;
            rs.blessingTaken = false;
            int nid = autoBiome();
            RunSave.write(game.P, this, RunSave.AUTO);
            toast = "Piso " + rs.floor + " · " + rs.floorsDone + (rs.floorsDone == 1 ? " completado" : " completados"); toastT = 3f;
            goRoom(Room.COMBAT);
            return;
        }
        rs.stage++;
        rs.blessingTaken = false;
        if (rs.stage >= 3 && !Save.S.sealForged()) {
            endRun(true);
            lv.pl.react("victory", 1f);
            openOv(OV_WIN);
            return;
        }
        int nid = autoBiome();
        goRoom(nid == 8 ? Room.BOSS : Room.COMBAT);
    }

    // =============================================================== mercader errante (sala secundaria temporal)
    private Level originLv;      // sala de origen, conservada viva (enemigos, trampas, objetos) mientras se esta en la tienda
    private Prop originDoor;     // la puerta por la que se entro

    private void enterMerchant(Prop p) {
        originLv = lv; originDoor = p;
        p.locked = true; p.done = true; p.label = "Mercader visitado";   // su entrada queda desactivada
        rs.sideOrigin = lv.room.type;
        rs.curEvent = p.event; rs.eventBiomeDone = true; rs.eventsThisRun[p.event]++;
        if (!sandbox) { Save.S.events[p.event]++; Save.S.write(); }
        goRoom(Room.EVENT);
    }

    private void leaveMerchant() {
        if (fadeMode == 1) return;
        fadeMode = 1; in.reset();
        fadeAct = this::restoreOrigin;
    }

    /** Vuelve a la sala de origen tal como estaba (sin regenerarla). Si se cargo una partida dentro de la tienda, la sala de origen se vuelve a crear. */
    private void restoreOrigin() {
        Level o = originLv; Prop d = originDoor; int ot = rs.sideOrigin;
        originLv = null; originDoor = null; rs.sideOrigin = -1; rs.curEvent = 0;
        if (o == null) { loadRoom(ot >= 0 ? ot : Room.COMBAT); return; }
        lv = o;
        Player pl = o.pl;
        pl.x = d.x + 22; pl.y = d.y; pl.vx = pl.vy = 0; pl.safeX = pl.x; pl.safeY = pl.y;
        pl.state = Player.IDLE;
        lv.snapCamera();
        shop = null; ov = OV_NONE; quitConfirm = false;
        Snd.music(rs.biome.music, true); Snd.ambient(rs.biome.ambient, 0.3f);
        bannerT = 0;
        fadeAct = null;
        in.reset();
        layoutOverlay();
    }

    // =============================================================== interaccion
    void interact() {
        Prop p = lv.nearestInteractable();
        if (p == null || !lv.pl.alive || lv.cinematic) return;
        ctx.cd = 0.35f;                                         // una pulsacion = una interaccion
        switch (p.kind) {
            case "door": case "portal": case "altar": case "shrine": case "spirit": case "cage": case "fountain": case "forge": case "cursed":
                lv.pl.react("touch", 0f);   // gesto al activar (solo cosmetico: la logica de abajo no cambia)
                break;
            default: break;
        }
        switch (p.kind) {
            case "door":
                Snd.sfx("door_open", 0.7f);
                if (p.nextType == -2) { afterBoss(); break; }
                if (p.nextType == -3) { leaveMerchant(); break; }
                if (p.event == Events.MERCHANT && p.nextType == Room.EVENT) { enterMerchant(p); break; }
                if (p.event > 0) {   // puerta lateral: no avanza la ruta principal
                    rs.curEvent = p.event; rs.eventBiomeDone = true; rs.eventsThisRun[p.event]++;
                    if (!sandbox) { Save.S.events[p.event]++; Save.S.write(); }
                    goRoom(p.nextType);
                    break;
                }
                rs.curEvent = 0;
                rs.roomNo++;
                rs.roomsDone = Math.max(rs.roomsDone, rs.roomNo);
                if (rs.infinite) rs.infRooms++;
                goRoom(p.nextType);
                break;
            case "portal": {
                Snd.sfx("portal_enter", 1f);
                int id = p.nextBiome;
                rs.biome = Biome.ALL[id];
                rs.visited.add(id);
                rs.roomNo = id == 8 ? 4 : 0;
                rs.blessingTaken = false; rs.eventBiomeDone = false;
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
            case "spirit": openSpirit(p); break;
            case "shrine": if (p.arg == 1) openRiskAltar(p); else openShrine(p); break;
            case "cursed": openCursed(p); break;
            case "cage": rescue(p); break;
            case "relic": openChest(p); break;
            case "weapon": { String m = Arsenal.takeGround(lv, p); if (m != null) { toast = m; toastT = 2.2f; } break; }
            case "merchant":
                ovProp = p;
                if (shop == null) shop = p.arg == 1 ? genWanderShop() : genShop();
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
        if (!sandbox) { Save.S.chestsOpened++; if (p.arg >= 3) Save.S.secretChests++; Save.S.write(); announceTrophies(); }
        Snd.sfx("chest_open", 1f);
        lv.pl.react("chest", 0f);
        lv.ps.burst(lv.rng, p.x, p.y - 10, 0xFFD25A, 16, 110, 0.7f, 2, 100, true);
        if (p.arg >= 3) {
            rs.secretsFound++;
            Items.secretChestDrops(lv, rs, p.x, p.y);
            if (p.arg == 4) Items.secretChestDrops(lv, rs, p.x, p.y);   // cofre superior: doble botin
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
        // nunca se sustituye la arma secundaria sin consentimiento: se muestra la comparacion y se pide confirmar
        if (x.kind == ChestLoot.K_SEC_NEW && rs.sec != 0 && rs.sec != x.id) { wcmp = x; wcmpSel = 0; openOv(OV_WCMP); sel = 0; return; }
        finishChest(x);
    }

    /** Aplica la recompensa elegida. Si sustituye a una arma 2ª equipada, esa queda en el suelo (en un punto seguro): jamas se destruye en silencio. */
    private void finishChest(ChestLoot.Reward x) {
        if (x.kind == ChestLoot.K_SEC_NEW && rs.sec != 0 && rs.sec != x.id) Arsenal.dropWeapon(lv, rs.sec, rs.secAmmo, lv.pl.x, lv.pl.y, true, false);
        ChestLoot.apply(rs, x);
        if (x.kind == ChestLoot.K_BARRIER) lv.pl.shield = Math.min(70, lv.pl.shield + x.val);
        cOffer = null; wcmp = null;
        closeOv();
        int col = ChestLoot.R_COL[x.rar] & 0xFFFFFF;
        lv.text(lv.pl.x, lv.pl.y - 50, x.name + (x.amount.isEmpty() ? "" : "  " + x.amount), col, true);
        lv.ps.burst(lv.rng, lv.pl.x, lv.pl.y - 16, col, 22, 120, 0.8f, 3, 60, true);
        lv.fx("fx_star", "burst", lv.pl.x, lv.pl.y - 18, 1f, col, Platform.ADD | Platform.TINT);
        Snd.sfx("secret", 0.9f);
        // reliquia, cofre secreto u objeto raro: reaccion de asombro (solo cosmetica, la recompensa ya se aplico arriba)
        if (x.rar >= 2 || (ovProp != null && (ovProp.arg >= 3 || ovProp.kind.equals("relic")))) lv.pl.react("awe", 1.5f);
    }

    // ganchos solo para las pruebas headless (ArsenalProbe)
    void dbgChest(int sel) { if (ov != OV_CHEST) openOv(OV_CHEST); offerSel = sel; ovT = 1f; }
    void dbgConfirm() { ovT = 1f; confirmChest(); }
    void dbgWcmp(boolean swap) { ovT = 1f; wcmpConfirm(swap); }

    private void wcmpConfirm(boolean swap) {
        if (ov != OV_WCMP || wcmp == null || ovT < 0.25f) return;
        if (swap) { ChestLoot.Reward x = wcmp; ov = OV_CHEST; finishChest(x); }
        else { ov = OV_CHEST; ovT = 0.3f; wcmp = null; layoutOverlay(); Snd.sfx("ui_back", 0.7f); }     // rechazar: vuelve a las 3 opciones, sin perder ninguna
    }

    // =============================================================== overlays
    private void openOv(int o) {
        ov = o; ovT = 0; saveMenu = false;
        in.reset();
        if (o != OV_DEAD && o != OV_WIN) Snd.sfx("ui_open", 0.7f);
        if (o == OV_PAUSE) Snd.sfx("ui_pause", 0.7f);
        layoutOverlay();
    }

    void closeOv() {
        ov = OV_NONE; ovT = 0; hits.clear(); saveMenu = false;
        in.reset();
        Snd.sfx("ui_back", 0.7f);
    }

    /** Solo banco de pruebas (BlessProbe modo ui): muestra un altar o la lista con los datos dados. */
    void dbgShowBless(int[] ids) { offer = ids; offerSel = 0; openOv(OV_BLESS); }
    void dbgShowList(int tab, int page) { blTab = tab; blPage = page; ov = OV_BLESSLIST; ovT = 0.3f; layoutOverlay(); }
    int dbgListPages() { return Math.max(1, (blRows.length + BL_PER_PAGE - 1) / BL_PER_PAGE); }

    private void openBlessing() {
        // opciones variadas con rareza, afinidad y condiciones de aparicion (ver BlessOffer)
        int[] pick = BlessOffer.pick(rs, 3 + BlessFx.offerExtra(rs), rs.rng);
        int cnt = 0;
        for (int id : pick) if (id >= 0) cnt++;
        if (cnt == 0) { lv.healPlayer(rs.stats.maxHp * 0.3f); return; }
        int[] comp = new int[cnt];
        for (int i = 0, k = 0; i < pick.length; i++) if (pick[i] >= 0) comp[k++] = pick[i];
        pick = comp;
        offer = pick;
        offerSel = 0;
        openOv(OV_BLESS);
        Snd.sfx("altar_bless", 0.9f);
    }

    void applyBless(int id) {
        BlessFx.sync(rs);
        boolean[] synBefore = rs.bx.synOn.clone();
        rs.bless[id]++;
        rs.blessingTaken = true;
        float oldMax = rs.stats.maxHp;
        rs.stats.recalc(rs);
        if (id == Blessing.CORAZON) rs.hp = Math.min(rs.stats.maxHp, rs.hp + 20);
        else if (id >= Blessing.LEGACY_COUNT && rs.stats.maxHp > oldMax) rs.hp += rs.stats.maxHp - oldMax;     // mas vida maxima: tambien la ganas
        rs.hp = Math.min(rs.hp, rs.stats.maxHp);
        rs.potions = Math.min(rs.potions, rs.stats.potionsMax);
        if (lv.pl != null) for (int s = 0; s < synBefore.length; s++) if (rs.bx.synOn[s] && !synBefore[s]) BlessEffects.synergyActivated(lv, s);
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

    // =============================================================== sucesos especiales
    private List<ShopItem> genWanderShop() {
        List<ShopItem> all = genShop();
        List<ShopItem> l = new ArrayList<>();
        while (l.size() < 3 && !all.isEmpty()) l.add(all.remove(rs.rng.i(all.size())));
        for (ShopItem it : l) it.cost = Math.max(10, Math.round(it.cost * 0.85f));
        return l;
    }

    private int randomBlessingId() {
        return BlessOffer.pickOne(rs, rs.rng);
    }

    /** Sube un nivel una bendicion al azar sin tocar la regla de una bendicion de altar por bioma. */
    private boolean giveRandomBlessing() {
        int id = randomBlessingId();
        if (id < 0) return false;
        boolean bt = rs.blessingTaken;
        applyBless(id);
        rs.blessingTaken = bt;
        return true;
    }

    private void finishEvent(Prop p, String msg, int col) {
        if (p != null) { p.used = true; p.done = true; p.label = null; }
        closeOv();
        if (msg != null) lv.text(lv.pl.x, lv.pl.y - 60, msg, col, true);
        lv.ps.burst(lv.rng, lv.pl.x, lv.pl.y - 20, col, 26, 130, 0.8f, 2, -20, true);
        lv.fxAdd("fx_ring", "pulse", lv.pl.x, lv.pl.y - 18, 1.1f, col);
        Snd.sfx("altar_bless", 0.9f);
    }

    private void openSpirit(Prop p) {
        evProp = p; evTitle = "ESPÍRITU DEL ABISMO"; evSub = "Ofrécele un recurso y te concederá poder"; evSel = 0;
        evOpts.clear();
        final int hpCost = Events.spiritHpCost(rs), gold = Events.spiritGoldCost(rs);
        boolean pool = randomBlessingId() >= 0;
        evOpts.add(new EvOpt("b_sangre", "Sangre por poder", "+1 nivel de una bendición al azar", "Pierdes " + hpCost + " de vida", Events.spiritHpOk(rs) && pool, () -> {
            rs.hp = Math.max(1, rs.hp - hpCost);
            if (giveRandomBlessing()) finishEvent(p, "El espíritu acepta tu sangre", 0x7AC8F0);
        }));
        evOpts.add(new EvOpt("forge", "Oro por temple", "+1 nivel de arma", "Pagas " + gold + " de oro", rs.weaponLvl < 5 && rs.gold >= gold, () -> {
            rs.gold -= gold; rs.weaponLvl++; rs.stats.recalc(rs);
            finishEvent(p, "Tu arma vibra con nueva fuerza", 0xFFB040);
        }));
        evOpts.add(new EvOpt("potion", "Frasco por visión", "Definitiva al máximo y +30 almas", "Entregas 1 frasco", rs.potions >= 1, () -> {
            rs.potions--; rs.ult = 100f; rs.souls += 30;
            finishEvent(p, "El espíritu bebe el frasco", 0x9FD8FF);
        }));
        openOv(OV_EVENT);
    }

    private void openShrine(Prop p) {
        evProp = p; evTitle = "SANTUARIO DE PACTOS"; evSub = "Elige un pacto: cada ventaja tiene su precio (máx. " + Events.MAX_PACTS + " por partida)"; evSel = 0;
        evOpts.clear();
        boolean room = rs.pactCount() < Events.MAX_PACTS;
        for (int id : Events.rollPacts(rs, new Rng(rs.seed ^ (rs.roomNo * 7919L + rs.stage * 104729L + rs.pactCount() * 31L)))) {
            final Events.Pact pk = Events.PACTS[id];
            evOpts.add(new EvOpt(pk.icon, pk.name, pk.pro, pk.con, room, () -> {
                rs.pacts[pk.id] = 1;
                rs.stats.recalc(rs);
                rs.hp = Math.min(rs.hp, rs.stats.maxHp);
                finishEvent(p, pk.name, 0xAA6EFF);
            }));
        }
        if (evOpts.isEmpty()) { toast = "Ya no quedan pactos por ofrecer"; toastT = 2f; return; }
        openOv(OV_EVENT);
    }

    // ------------------------------------------------------------------ altar de riesgo, cofre maldito, desafios
    // ---- HUD de combate: senal breve al quedar lista una habilidad (0..3 = habilidades, 3 = definitiva)
    final float[] skReady = new float[4];
    final boolean[] skWasCd = new boolean[3];
    void hudTick(float dt) {
        for (int k = 0; k < 3; k++) {
            if (rs.cd[k] > 0) skWasCd[k] = true;
            else if (skWasCd[k]) { skWasCd[k] = false; skReady[k] = 0.5f; }
        }
        for (int k = 0; k < 4; k++) if (skReady[k] > 0) skReady[k] -= dt;
    }
    /** Texto del tiempo de reutilizacion: enteros hasta 3 s y con un decimal por debajo (se lee mejor el ultimo tramo). */
    static String cdText(float cd) {
        if (cd >= 3f) return String.valueOf((int) Math.ceil(cd));
        int d = Math.max(1, (int) Math.ceil(cd * 10f - 1e-4f));
        return (d / 10) + "." + (d % 10);
    }

    Runnable afterBless;
    void offerSelDbg(int i) { offerSel = Math.max(0, Math.min(offer.length - 1, i)); }   // solo grabacion de trailers
    List<Hit> hitsDbg() { return hits; }          // solo pruebas
    void clickDbg(Hit h) { click(h); }            // solo pruebas
    boolean ambushOn;                 // emboscada del cofre maldito en curso
    int chal = -1, chalState;         // desafio de la sala (Events.CH_*), -1 = ninguno; estado: 0 en curso, 1 superado, 2 fallido
    float chalT, chalWaveT;

    void openRiskAltar(Prop p) {
        evProp = p; evTitle = "ALTAR DE RIESGO"; evSub = "Cada ofrenda tiene un precio: léelo antes de aceptar"; evSel = 0;
        evOpts.clear();
        final int maxHp = Math.round(rs.stats.maxHp);
        final int hpCost = Math.round(maxHp * 0.25f), hit = Math.round(maxHp * 0.18f);
        final int gold = Math.round((100 + 30 * rs.stage) * rs.stats.goldMul), souls = 30;
        final int soulCost = 60 + 20 * rs.stage;
        evOpts.add(new EvOpt("b_sangre", "Sangre por bendición", "Eliges 1 de 3 bendiciones", "Pierdes " + hpCost + " de vida", rs.hp - hpCost >= maxHp * 0.2f, () -> {
            rs.hp -= hpCost;
            lv.text(lv.pl.x, lv.pl.y - 40, "-" + hpCost, 0xE0405A, true);
            offerFromAltar(p, 3, "El altar acepta tu sangre");
        }));
        evOpts.add(new EvOpt("coin", "Dolor por botín", "+" + gold + " de oro y +" + souls + " almas", "Recibes un golpe de " + hit + " de daño", rs.hp - hit >= maxHp * 0.15f, () -> {
            rs.hp -= hit; rs.damageTaken += hit;
            lv.dropGold(p.x, p.y - 20, gold); rs.souls += souls;
            lv.pl.hitFlash = 0.15f; lv.shake(3f, 0.2f);
            finishEvent(p, "Aguantas el dolor", 0xE0405A);
        }));
        Events.Pact fast = Events.PACTS[6];
        evOpts.add(new EvOpt(fast.icon, fast.name, fast.pro, fast.con + " (cuenta como pacto)", rs.pacts[6] == 0 && rs.pactCount() < Events.MAX_PACTS, () -> {
            rs.pacts[6] = 1; rs.stats.recalc(rs);
            rs.potions = Math.min(rs.potions, rs.stats.potionsMax); rs.hp = Math.min(rs.hp, rs.stats.maxHp);
            finishEvent(p, fast.name, 0xE0405A);
        }));
        evOpts.add(new EvOpt("soul", "Almas por elección", "Eliges 1 de 4 bendiciones", "Pagas " + soulCost + " almas", rs.souls >= soulCost, () -> {
            rs.souls -= soulCost;
            offerFromAltar(p, 4, "El altar acepta tus almas");
        }));
        openOv(OV_EVENT);
    }

    /** Abre una eleccion de bendiciones desde un altar de riesgo sin gastar la bendicion de altar del bioma. */
    private void offerFromAltar(Prop p, int n, String msg) {
        closeOv();
        int[] pick = BlessOffer.pick(rs, n + BlessFx.offerExtra(rs), rs.rng);
        int cnt = 0;
        for (int id : pick) if (id >= 0) cnt++;
        if (cnt == 0) { lv.healPlayer(rs.stats.maxHp * 0.3f); finishEvent(p, "Sin bendiciones que ofrecer: te curas", 0xE0405A); return; }
        int[] comp = new int[cnt];
        for (int i = 0, k = 0; i < pick.length; i++) if (pick[i] >= 0) comp[k++] = pick[i];
        offer = comp; offerSel = 0;
        final boolean bt = rs.blessingTaken;
        afterBless = () -> { rs.blessingTaken = bt; finishEvent(p, msg, 0xE0405A); };
        openOv(OV_BLESS);
        Snd.sfx("altar_bless", 0.9f);
    }

    void openCursed(Prop p) {
        evProp = p; evTitle = "COFRE MALDITO"; evSub = "Un gran premio, pero algo lo vigila"; evSel = 0;
        evOpts.clear();
        final int n = Events.ambushCount(rs);
        evOpts.add(new EvOpt("chest", "Abrir el cofre", "2 cofres de elección y " + (25 + 8 * rs.stage) + " almas", "Emboscada: " + n + " enemigos, uno de élite", true, () -> {
            closeOv();
            p.used = true; p.done = true; p.label = null; p.anim = "open"; p.animT = 0;
            Snd.sfx("chest_open", 1f);
            lv.flash(0xA050E0, 0.25f); lv.shake(3f, 0.3f);
            startAmbush(n);
            lv.text(lv.pl.x, lv.pl.y - 60, "¡El cofre estaba maldito!", 0xC070F0, true);
        }));
        evOpts.add(new EvOpt("door", "Dejarlo cerrado", "Sin riesgo", "Renuncias al premio", true, () -> {
            p.used = true; p.done = true; p.label = null;
            closeOv();
            lv.text(lv.pl.x, lv.pl.y - 50, "Prefieres no arriesgarte", 0xB8A0D0, true);
        }));
        openOv(OV_EVENT);
    }

    /** Casillas del suelo, llanas y sin pinchos, alejadas del jugador: sitio donde aparecer sin caer en trampas. */
    private java.util.List<Integer> groundSpots(float minDist) {
        Room rm = lv.room;
        java.util.List<Integer> out = new ArrayList<>();
        if (rm.ground == null) return out;
        for (int x = 14; x < rm.w - 14; x++) {
            int g = rm.ground[x];
            if (g <= 0 || x + 1 >= rm.w || rm.ground[x + 1] != g || rm.ground[x - 1] != g) continue;
            if (rm.spikeCols != null && rm.spikeCols.contains(x)) continue;
            if (Math.abs(x * Room.TS - lv.pl.x) < minDist) continue;
            out.add(x);
        }
        return out;
    }

    private String randomGroundEnemy(Rng r) {
        String[] pool = lv.room.biome.enemies;
        for (int tries = 0; tries < 8; tries++) {
            String id = pool[r.i(pool.length)];
            EnemyDef d = EnemyDef.get(id);
            if (d != null && d.role != EnemyDef.FLY_SHOOT && d.role != EnemyDef.FLY_DIVE && d.role != EnemyDef.HEAVY) return id;
        }
        return pool[0];
    }

    private void spawnWave(int n, boolean withElite) {
        java.util.List<Integer> spots = groundSpots(120f);
        if (spots.isEmpty()) spots = groundSpots(0f);
        Rng r = new Rng(rs.seed ^ (lv.enemies.size() * 7919L + (long) (lv.time * 10f)));
        java.util.List<Integer> used = new ArrayList<>();
        for (int i = 0; i < n && !spots.isEmpty(); i++) {
            int x = spots.get(r.i(spots.size()));
            for (int t = 0; t < 8; t++) { boolean ok = true; for (int u : used) if (Math.abs(u - x) < 4) ok = false; if (ok) break; x = spots.get(r.i(spots.size())); }
            used.add(x);
            String id = randomGroundEnemy(r);
            boolean el = false;
            if (withElite && i == 0) { String eid = EnemyDef.eliteFor(lv.room.biome.key); EnemyDef ed = eid == null ? null : EnemyDef.get(eid); if (ed != null && ed.role != EnemyDef.FLY_SHOOT && ed.role != EnemyDef.FLY_DIVE) id = eid; else el = true; }
            lv.spawnEnemy(id, el, x * Room.TS + 8, lv.room.ground[x] * Room.TS);
        }
    }

    private void startAmbush(int n) {
        ambushOn = true;
        lv.props.removeIf(q -> q.kind.equals("door"));     // sin salida hasta vencer
        spawnWave(n, true);
    }

    private void cursedReward(Level l) {
        for (int i = 0; i < 2; i++) {
            Prop c = l.addProp(new Room.PropSpec("chest", l.room.exitX - 70 - i * 38, l.room.exitY, 2));
            c.label = "Botín maldito"; c.roundChest = true;
            l.ps.burst(l.rng, c.x, c.y - 12, 0xC070F0, 22, 110, 0.7f, 2, 0, true);
        }
        l.dropSouls(l.pl.x, l.pl.y - 20, 25 + 8 * rs.stage);
        l.text(l.pl.x, l.pl.y - 82, "¡Maldición rota! 2 cofres", 0xC070F0, true);
    }

    private void challengeInit(int type) {
        chal = -1; chalState = 0; chalT = 0; chalWaveT = 0;
        if (lv == null) return;
        lv.healMul = 1f; lv.holdClear = false;
        if (type != Room.EVENT || rs.curEvent != Events.CHALLENGE) { rs.chalKind = -1; return; }
        if (rs.chalKind < 0 || rs.chalKind >= Events.CH_COUNT) rs.chalKind = Events.challengeKind(rs);
        chal = rs.chalKind;
        if (chal == Events.CH_TIMED) chalT = Events.CH_TIME_TIMED;
        else if (chal == Events.CH_SURVIVE) { chalT = Events.CH_TIME_SURVIVE; chalWaveT = 8f; lv.holdClear = true; }
        else if (chal == Events.CH_NOHEAL) lv.healMul = Events.CH_HEAL;
    }

    void challengeTick(float dt) {
        if (chal < 0 || lv == null || chalState != 0 || !lv.pl.alive || bannerT > 2.2f) return;
        if (chal == Events.CH_NODMG && lv.roomHits > 0) { chalFail("¡Te han golpeado!"); return; }
        if (chal == Events.CH_TIMED) {
            chalT -= dt;
            if (chalT <= 0) { chalT = 0; chalFail("¡Se acabó el tiempo!"); }
        } else if (chal == Events.CH_SURVIVE) {
            chalT -= dt; chalWaveT -= dt;
            if (chalWaveT <= 0 && chalT > 6f) { chalWaveT = 9f; spawnWave(2 + rs.stage, false); lv.text(lv.pl.x, lv.pl.y - 60, "¡Otra oleada!", 0xFFA030, true); }
            if (chalT <= 0) {
                chalT = 0; lv.holdClear = false;
                for (Enemy e : new ArrayList<>(lv.enemies)) if (e.alive) e.die(lv);
                chalState = 1;
                lv.text(lv.pl.x, lv.pl.y - 70, "¡Has resistido!", 0xFFD25A, true);
            }
        }
    }

    private void chalFail(String why) {
        chalState = 2;
        Snd.sfx("ui_error", 0.8f);
        lv.text(lv.pl.x, lv.pl.y - 70, why + " Desafío fallido", 0xFF6A5A, true);
    }

    private void challengeCleared(Level l) {
        if (chal < 0) return;
        if (chal == Events.CH_SURVIVE && chalState == 0) return;
        boolean ok = chalState != 2;
        if (chal == Events.CH_NODMG && l.roomHits > 0) ok = false;
        if (chal == Events.CH_TIMED && chalT <= 0) ok = false;
        chalState = ok ? 1 : 2;
        if (!ok) { l.text(l.pl.x, l.pl.y - 82, "Sin premio esta vez", 0xB8A0D0, true); return; }
        for (int i = 0; i < 2; i++) {
            Prop c = l.addProp(new Room.PropSpec("chest", l.room.exitX - 70 - i * 38, l.room.exitY, 2));
            c.label = "Premio del desafío"; c.roundChest = true;
            l.ps.burst(l.rng, c.x, c.y - 12, 0xFFA030, 22, 110, 0.7f, 2, 0, true);
        }
        l.dropSouls(l.pl.x, l.pl.y - 20, 20 + 6 * rs.stage);
        l.text(l.pl.x, l.pl.y - 82, "¡Desafío superado! 2 cofres", 0xFFA030, true);
        if (chal == Events.CH_SURVIVE) chalState = 1;
    }

    private void renderChallenge(Platform.Gfx g, int w) {
        if (chal < 0 || lv == null || ov != OV_NONE) return;
        String t = Events.CH_NAME[chal];
        int col = chalState == 1 ? 0xFF8AE08A : chalState == 2 ? 0xFFFF6A5A : 0xFFFFA030;
        String st = chalState == 1 ? "SUPERADO" : chalState == 2 ? "FALLIDO" : chal == Events.CH_NODMG ? "sin recibir daño" : chal == Events.CH_NOHEAL ? "curación -60%" : Math.round(chalT) + " s";
        UI.small.center(g, t + " · " + st + (chalState == 0 && chal != Events.CH_SURVIVE && chal != Events.CH_TIMED ? " · quedan " + Math.max(0, lv.toKill) : ""), w / 2f, 34, col, 1f);
    }

    private void rescue(Prop p) {
        if (!lv.cleared) { Snd.sfx("ui_error", 0.8f); toast = "Derrota primero a los guardias"; toastT = 2.2f; return; }
        p.anim = "open"; p.animT = 0; p.done = true; p.used = true; p.label = null;
        String msg;
        switch (p.arg) {
            case 0:
                if (rs.weaponLvl < 5) { rs.weaponLvl++; rs.stats.recalc(rs); msg = "¡Libre! Afila tu arma: +1 nivel"; }
                else { lv.dropGold(p.x, p.y - 20, 80); msg = "¡Libre! Te da 80 de oro"; }
                break;
            case 1:
                msg = giveRandomBlessing() ? "¡Libre! Te enseña una bendición" : "¡Libre! Te cura";
                if (!msg.contains("bendición")) lv.healPlayer(rs.stats.maxHp * 0.4f);
                break;
            default:
                lv.healPlayer(rs.stats.maxHp);
                rs.potions = Math.min(rs.stats.potionsMax + 1, rs.potions + 1);
                msg = "¡Libre! Te cura y te da un frasco";
                break;
        }
        lv.text(p.x, p.y - 70, msg, 0xB8A0D0, true);
        lv.ps.burst(lv.rng, p.x, p.y - 30, 0xB8A0D0, 30, 130, 0.9f, 2, -10, true);
        lv.fx("fx_heal", "rise", p.x, p.y - 20, 1.2f, 0, 0);
        Snd.sfx("secret", 0.9f);
    }

    private List<ShopItem> genShop() {
        List<ShopItem> l = new ArrayList<>();
        int st = rs.stage;
        l.add(new ShopItem("Frasco de vida", "+1 frasco de vida.", "potion", 30 + 10 * st, 0, 0));
        l.add(new ShopItem("Elixir", "Cura el 50% de tu vida.", "heart", 45 + 10 * st, 1, 0));
        // bendicion aleatoria
        int bid = BlessOffer.pickOne(rs, rs.rng);
        if (bid >= 0) {
            Blessing b = Blessing.ALL[bid];
            l.add(new ShopItem(b.name, b.desc, b.icon, Math.round((95 + 25 * st) * (1f + 0.25f * b.rar)), 2, bid));
        }
        if (rs.rng.chance(0.5f)) l.add(new ShopItem("Cristal de poder", "Carga tu definitiva al máximo.", "star", 60 + 10 * st, 3, 0));
        else if (rs.weaponLvl < 5) l.add(new ShopItem("Piedra de afilar", "Mejora tu arma un nivel.", "forge", Math.round(rs.forgeCost() * 1.15f), 4, 0));
        else l.add(new ShopItem("Reserva de almas", "Obtienes 15 almas.", "soul", 50, 5, 0));
        float disc = BlessFx.shopDisc(rs);
        if (disc > 0f) for (ShopItem it : l) it.cost = Math.max(5, Math.round(it.cost * (1f - disc)));
        return l;
    }

    void buy(ShopItem it) {
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
                int on = offer.length;
                float gap = 8, cw = Math.min(150, (w - 24 - (on - 1) * gap) / on), x0 = w / 2f - (on * cw + (on - 1) * gap) / 2f;
                for (int i = 0; i < on; i++) {
                    if (offer[i] < 0) continue;
                    final int k = i;
                    Hit h = add(x0 + i * (cw + gap), 38, cw, 214, null, () -> {
                        if (ovT < 0.35f) return;
                        applyBless(offer[k]);
                        if (ovProp != null && ovProp.kind.equals("altar")) { ovProp.used = true; ovProp.anim = "used"; ovProp.label = null; }
                        closeOv();
                        if (afterBless != null) { Runnable ab = afterBless; afterBless = null; ab.run(); }
                    });
                    h.plain = false; h.tag = i;
                }
                break;
            }
            case OV_EVENT: {
                int n = evOpts.size();
                float cw = Math.min(150, (w - 40) / 3f), gap = 8, x0 = w / 2f - (n * cw + (n - 1) * gap) / 2f;
                for (int i = 0; i < n; i++) {
                    final int k = i;
                    Hit h = add(x0 + i * (cw + gap), 52, cw, 150, null, () -> {
                        if (ovT < 0.35f) return;
                        EvOpt o = evOpts.get(k);
                        if (!o.ok) { Snd.sfx("ui_error", 0.8f); return; }
                        o.act.run();
                    });
                    h.plain = true; h.tag = i; h.noSound = true;
                }
                add(w / 2f - 50, 212, 100, 22, "Rechazar", this::closeOv);
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
                add(0, 0, w, ViewSize.h, null, this::talkTap).plain = true;
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
                if (saveMenu && !isTestSession()) {
                    for (int i = 0; i < RunSave.SLOTS; i++) {
                        final int slot = i;
                        add(bx, by + i * 28, bw, 22, "Guardar en ranura " + (i + 1), () -> {
                            if (RunSave.write(game.P, this, slot)) { toast = "Partida guardada en la ranura " + (slot + 1); Snd.sfx("ui_confirm", 0.9f); }
                            else { toast = "No se pudo guardar"; Snd.sfx("ui_error", 0.7f); }
                            toastT = 2.5f; layoutOverlay();
                        });
                    }
                    add(bx, by + 3 * 28 + 6, bw, 22, "Volver", () -> { saveMenu = false; layoutOverlay(); });
                    break;
                }
                // columna izquierda alineada (7 botones, 24 px de paso); a la derecha, el resumen agrupado
                int row = 0;
                add(bx, by + 24 * row++, bw, 21, "Continuar", this::closeOv);
                if (!isTestSession()) add(bx, by + 24 * row++, bw, 21, "Guardar partida", () -> { saveMenu = true; layoutOverlay(); });
                add(bx, by + 24 * row++, bw, 21, "Música: " + (s.musicOn ? "SÍ" : "NO"), () -> { s.musicOn = !s.musicOn; Snd.applyVolumes(); s.write(); layoutOverlay(); });
                add(bx, by + 24 * row++, bw, 21, "Sonidos: " + (s.sfxOn ? "SÍ" : "NO"), () -> { s.sfxOn = !s.sfxOn; Snd.applyVolumes(); s.write(); layoutOverlay(); });
                if (game.P.video() != null) {     // PC: sin vibracion; atajo para alternar pantalla completa (sin bordes)
                    add(bx, by + 24 * row++, bw, 21, "Pantalla completa: " + (VideoCfg.cur.mode != VideoCfg.MODE_WINDOW ? "SÍ" : "NO"), () -> {
                        VideoCfg c = VideoCfg.cur.copy();
                        c.mode = c.mode == VideoCfg.MODE_WINDOW ? VideoCfg.MODE_BORDERLESS : VideoCfg.MODE_WINDOW;
                        if (game.P.video().apply(c)) VideoCfg.save(game.P, c);
                        layoutOverlay();
                    });
                } else add(bx, by + 24 * row++, bw, 21, "Vibración: " + (s.vibOn ? "SÍ" : "NO"), () -> { s.vibOn = !s.vibOn; s.write(); layoutOverlay(); });
                add(bx, by + 24 * row++, bw, 21, "Efectos: " + (s.reduceFx ? "REDUCIDOS" : "NORMALES"), () -> { s.reduceFx = !s.reduceFx; s.write(); layoutOverlay(); });
                if (isTestSession()) add(bx, by + 24 * row++ + 6, bw, 21, "Salir del modo de prueba", () -> { exitTest(); });
                else add(bx, by + 24 * row++ + 6, bw, 21, quitConfirm ? "¿Seguro? Toca otra vez" : "Abandonar partida", () -> {
                    if (quitConfirm) { endRun(false); game.go(new Ops(game)); }
                    else { quitConfirm = true; layoutOverlay(); }
                });
                break;
            }
            case OV_INV: inv.layout(w); break;
            case OV_BLESSLIST: {
                layoutBlessList(w);
                break;
            }
            case OV_WCMP: {
                float bw = 150;
                Hit keep = add(w / 2f - bw - 6, 222, bw, 24, "Conservar la actual", () -> wcmpConfirm(false)); keep.tag = 0;
                Hit swp = add(w / 2f + 6, 222, bw, 24, "Intercambiar", () -> wcmpConfirm(true)); swp.tag = 1;
                break;
            }
            case OV_REVIVE: {
                java.util.List<Infinite.Offer> offs = Infinite.offers(rs);
                float by = 126;
                for (final Infinite.Offer o : offs) {
                    String lab = o.method != Infinite.Method.GEMS && !o.available ? "Anuncio no disponible" : o.method == Infinite.Method.GEMS ? "Revivir · " + o.cost + " gemas" : (o.method == Infinite.Method.AD_LONG ? "Revivir · anuncio largo" : "Revivir · ver anuncio");
                    Hit hb = add(w / 2f - 100, by, 200, 26, lab, () -> tryRevive(o.method));
                    hb.disabled = !o.available;
                    by += 32;
                }
                add(w / 2f - 100, by + 4, 200, 24, "Terminar la run", () -> { reviveWait = -1; ov = OV_NONE; deadT = 0; endRun(false); });
                break;
            }
            case OV_DEAD: {
                if (rs.infinite) {
                    add(w / 2f - 130, 212, 124, 24, "Reintentar", () -> { Save.S.started++; Save.S.write(); game.go(RunScreen.infinite(game, cls, Math.min(Save.S.ascensionSel, Save.S.ascension))); });
                    add(w / 2f + 6, 212, 124, 24, "Menú principal", () -> game.go(new Ops(game)));
                    break;
                }
                add(w / 2f - 130, 206, 124, 24, "Reintentar", () -> game.go(new ClassScreen(game)));
                add(w / 2f + 6, 206, 124, 24, "Menú principal", () -> game.go(new Ops(game)));
                break;
            }
            case OV_WIN: {
                final boolean fin = rs.finalRun;
                if (fin && Save.S.finalBeaten) {
                    add(w / 2f - 130, 206, 124, 24, "Modo infinito", this::continueInfinite);
                    add(w / 2f + 6, 206, 124, 24, "Ver créditos", () -> {
                        if (Story.tryUnlockFinal() && Story.cine("final") != null)
                            game.go(new Cinematic(game, Story.FINAL, () -> game.go(new Screens.Credits(game, true))));
                        else game.go(new Screens.Credits(game, true));
                    });
                    break;
                }
                add(w / 2f - 62, 206, 124, 24, fin ? "Ver créditos" : "Continuar", () -> {
                    if (fin && Story.tryUnlockFinal() && Story.cine("final") != null)
                        game.go(new Cinematic(game, Story.FINAL, () -> game.go(new Screens.Credits(game, true))));
                    else game.go(fin ? new Screens.Credits(game, true) : new Ops(game));
                });
                break;
            }
            default: break;
        }
    }

    /** Intenta la revivida con el metodo elegido (gemas: cobra y marca la revivida en una sola escritura; anuncio: solo si se completa). */
    private void tryRevive(final Infinite.Method m) {
        if (reviveWait < 0 || ov != OV_REVIVE || Services.adInFlight()) return;
        if (m == Infinite.Method.GEMS) {
            if (Infinite.consume(rs, m, game.P)) doRevive();
            else { reviveMsg = "No se pudo revivir"; Snd.sfx("ui_error", 0.7f); }
        } else {
            Services.AdPlacement pl = m == Infinite.Method.AD_LONG ? Services.AdPlacement.REVIVE_LONG : Services.AdPlacement.REVIVE_STANDARD;
            boolean started = Services.requestRewardedAd(pl, () -> { if (reviveWait >= 0 && Infinite.consume(rs, m, game.P)) doRevive(); });
            if (!started) { reviveMsg = "Anuncio no disponible"; Snd.sfx("ui_error", 0.7f); }
        }
    }

    private void doRevive() {
        reviveWait = -1; deadT = -1;
        rs.hp = Math.max(1, rs.stats.maxHp * 0.5f);
        lv.pl.revive();
        lv.timeScale = 1f;
        lv.text(lv.pl.x, lv.pl.y - 40, "¡Revivida " + rs.revivesUsed + "/" + rs.ruleset.maxRevives + "!", 0xC08CFF, true);
        Snd.sfx("heal", 1f);
        lv.flash(0xC08CFF, 0.3f);
        Snd.music(rs.biome.music, true);
        ov = OV_NONE; ovT = 0; hits.clear(); in.reset();
        RunSave.write(game.P, this, RunSave.AUTO);      // un solo commit: saldo de gemas + contador de revividas + sala
    }

    /** Tras vencer al Cazador: sigue la MISMA run en el modo infinito (conserva el equipo; las bajas ya contadas no se cuentan dos veces). */
    private void continueInfinite() {
        if (!rs.finalRun || rs.infinite) return;
        ended = false; deadT = -1; winT = -1; winPending = false; sumNote = "";
        rs.infinite = true; rs.infFromCampaign = true; rs.ruleset = Infinite.NORMAL;
        rs.stage = 2; rs.floor = 1; rs.floorsDone = 0; rs.revivesUsed = 0; rs.infRooms = 0;
        rs.infBaseKills = rs.kills; rs.infBaseBoss = rs.bossKills; rs.infT0 = rs.time;
        rs.finalRun = false; rs.visited.clear();
        rs.hp = rs.stats.maxHp;
        int nid = autoBiome();
        closeOv();
        goRoom(Room.COMBAT);
        RunSave.write(game.P, this, RunSave.AUTO);
    }

    /** Sesion de prueba del Modo Desarrollador (arena, laboratorio, tienda de prueba). */
    boolean isTestSession() { return sandbox || rs.isTest(); }

    /** Termina la sesion de prueba y vuelve al menu de origen sin guardar nada. */
    private void exitTest() {
        reviveWait = -1;
        game.go(sbBack != null ? sbBack.get() : new Screens.Title(game));
    }

    // ---- ganchos de prueba (solo los usa DebugBot)
    void debugNextFloor() { afterBoss(); }
    void debugOpenPause() { openOv(OV_PAUSE); }
    void debugForceSaveMenu() { saveMenu = true; layoutOverlay(); }
    java.util.List<String> debugLabels() { java.util.List<String> l = new ArrayList<>(); for (Hit h : hits) if (h.label != null) l.add(h.label); return l; }
    boolean debugTap(String label) { for (Hit h : new ArrayList<>(hits)) if (label.equals(h.label) && !h.disabled && h.act != null) { h.act.run(); return true; } return false; }
    void debugKillAll() {
        for (Enemy e : new ArrayList<>(lv.enemies)) if (e.alive) { e.hp = 0; e.die(lv); }
        if (lv.boss != null) { lv.boss.die(lv); onBossDead(lv); }
    }
    boolean debugRevive(Infinite.Method m) { int n = rs.revivesUsed; tryRevive(m); return rs.revivesUsed > n; }
    void debugWinCampaign() { rs.finalRun = true; Save.S.finalBeaten = true; endRun(true); openOv(OV_WIN); }
    void debugContinueInfinite() { continueInfinite(); }
    void debugEnd() { endRun(false); }
    int debugOv() { return ov; }
    boolean debugReviveWaiting() { return reviveWait >= 0; }

    @Override void resize() { layoutOverlay(); if (lv != null) lv.viewW = game.viewW; }

    @Override boolean back() {
        if (lv == null) return false;
        if (ov == OV_NONE) { openOv(OV_PAUSE); return true; }
        if (ov == OV_PAUSE && saveMenu) { saveMenu = false; layoutOverlay(); return true; }
        if (ov == OV_BLESSLIST) { ov = OV_PAUSE; ovT = 0.3f; layoutOverlay(); return true; }
        if (ov == OV_WCMP) { wcmpConfirm(false); return true; }
        if (ov == OV_INV) { invClose(); return true; }
        if (ov == OV_TALK) { talk = null; closeOv(); return true; }
        if (ov == OV_REVIVE) return true;
        if (ov == OV_PAUSE || ov == OV_SHOP || ov == OV_FORGE || ov == OV_EVENT) { closeOv(); return true; }
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
        if (ov == OV_INV) inv.update(dt);
        if (!sandbox && ov != OV_PAUSE) { Save.S.playMs += (long) (dt * 1000f); playSave += dt; if (playSave > 30f) { playSave = 0; Save.S.write(); } }
        if (sandbox && sbRespawnT > 0) { sbRespawnT -= dt; if (sbRespawnT <= 0) { sbRespawnT = -1; loadRoom(sbBoss >= 0 ? Room.BOSS : Room.COMBAT); } }
        if (ov == OV_TALK && tdlg != null) tdlg.update(dt);
        if (bannerT > 0) bannerT -= dt;
        if (lv.unlockTitle != null) { bannerTitle = lv.unlockTitle; bannerSub = lv.unlockSub; bannerT = 3f; lv.unlockTitle = null; }
        if (relicBannerT > 0) relicBannerT -= dt;
        if (hintT > 0) hintT -= dt;
        if (toastT > 0) toastT -= dt;
        if (Codex.toast != null) { toast = Codex.toast; toastT = 2.6f; Codex.toast = null; }
        if (ov == OV_NONE && deadT < 0 && winT < 0 && lv.pl.alive) {
            autoT += dt;
            if (autoT >= 300f) { autoT = 0; RunSave.write(game.P, this, RunSave.AUTO); toast = "Autoguardado"; toastT = 2f; }
        }
        if (reviveWait >= 0 && ov == OV_NONE) {
            reviveWait += dt;
            if (reviveWait > 1.0f) { reviveMsg = ""; openOv(OV_REVIVE); }
        }
        if (comboFlash > 0) comboFlash -= dt;
        if (bossCardT >= 0) bossCardT += dt;
        if (ov != OV_NONE || fadeMode == 1) ctx.update(dt, null);
        tut.update(dt, in, ov == OV_NONE && fadeMode == 0 && deadT < 0 && winT < 0 && !lv.cinematic && lv.pl.alive && bannerT <= 0.6f);
        if (ov == OV_NONE) {
            if (fadeMode != 1) {
                if (in.pressed(Input.B_PAUSE) && deadT < 0 && winT < 0) { openOv(OV_PAUSE); return; }
                if (in.pressed(Input.B_INV) && deadT < 0 && winT < 0 && !lv.cinematic && lv.pl.alive) { in.consume(Input.B_INV); openInventory(false); return; }
                Prop near = lv.nearestInteractable();
                boolean canInt = near != null && lv.pl.alive && !lv.cinematic && deadT < 0;
                in.btn[Input.B_INTERACT].visible = false;          // sin boton pequeno: la interaccion tactil es el boton contextual (ContextBtn)
                ctx.update(dt, canInt ? near : null);
                if (canInt && in.pressed(Input.B_INTERACT) && ctx.cd <= 0) { in.consume(Input.B_INTERACT); interact(); }
            }
            lv.update(dt);
            challengeTick(dt);
            hudTick(dt);
            if (ov == OV_NONE && lv != null) {
                // ult lista
                boolean ready = rs.ult >= 100f;
                if (ready && !ultWasReady) { Snd.sfx("ult_ready", 0.9f); skReady[3] = 0.6f; }
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
        if (action == Platform.ACTION_DOWN && tut.hitButton(x, y)) { tut.close(); Snd.sfx("ui_click", 0.6f); return; }
        if (action == Platform.ACTION_DOWN && deadT < 0 && winT < 0 && !lv.cinematic && lv.pl.alive) {
            if (ctx.hit(x, y)) { interact(); return; }                       // toque/clic en el boton contextual: solo interactua (no ataca ni esquiva)
            if (!game.touchUiVisible()) {                                    // PC: clic en los espacios de arma
                for (int k = 0; k < 2; k++) {
                    Input.Btn sb = in.btn[k == 0 ? Input.B_WMAIN : Input.B_WSEC];
                    if (Mth.dist(x, y, sb.cx, sb.cy) <= sb.r + 2) { lv.pl.selWant = k + 1; lv.pl.swapBuf = 0.16f; return; }
                }
            }
        }
        if (!game.touchUiVisible()) return;   // con mando activo los toques no tocan el juego
        in.touch(id, action, x, y);
    }

    @Override void key(int code, boolean isDown) {
        if (ov != OV_NONE) {
            if (ov == OV_BLESS && isDown) {
                int on = Math.max(1, offer.length);
                if (code == 37 || code == 'A') offerSel = (offerSel + on - 1) % on;
                else if (code == 39 || code == 'D') offerSel = (offerSel + 1) % on;
                else if ((code == 10 || code == 32 || code == 'J') && ovT > 0.35f) { for (Hit h : hits) if (h.tag == offerSel) { click(h); break; } }
                return;
            }
            if (ov == OV_INV) { if (isDown) inv.key(code); return; }
            if (ov == OV_BLESSLIST && isDown) {
                if (code == 37 || code == 'A') blPage(-1);
                else if (code == 39 || code == 'D') blPage(1);
                else if (code == 9 || code == 'Q') { blTab = 1 - blTab; blPage = 0; layoutOverlay(); }
                else if (code == 27 || code == 10 || code == 32) back();
                return;
            }
            if (ov == OV_EVENT && isDown) {
                int n = Math.max(1, evOpts.size());
                if (code == 37 || code == 'A') evSel = (evSel + n - 1) % n;
                else if (code == 39 || code == 'D') evSel = (evSel + 1) % n;
                else if ((code == 10 || code == 32 || code == 'J') && ovT > 0.35f) { for (Hit h : hits) if (h.label == null && h.tag == evSel) { click(h); break; } return; }
                else if (code == 27) { back(); return; }
                return;
            }
            if (ov == OV_TALK && isDown) {
                if (tphase != 1 && (code == 10 || code == 32 || code == 'J')) { talkTap(); return; }
                if (code == 27) { back(); return; }
            }
            if (ov == OV_WCMP && isDown) {
                if (code == 37 || code == 'A' || code == 39 || code == 'D') { wcmpSel = 1 - wcmpSel; sel = wcmpSel; Snd.sfx("ui_hover", 0.5f); }
                else if ((code == 10 || code == 32 || code == 'J') && ovT > 0.25f) wcmpConfirm(wcmpSel == 1);
                else if (code == 27) wcmpConfirm(false);
                return;
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
        if (ov == OV_NONE && !lv.cinematic) tut.render(g, this, w);
        renderOverlay(g, w);
        // pantalla roja al morir
        if (deadT >= 0) g.rect(0, 0, w, ViewSize.h, Mth.withAlpha(0x500000, (int) (Mth.clamp(deadT / 1.5f, 0, 1) * 150)), false);
        if (fadeA > 0.001f) g.rect(0, 0, w, ViewSize.h, Mth.withAlpha(0x000000, (int) (Mth.clamp(fadeA, 0, 1) * 255)), false);
    }

    private void renderCinema(Platform.Gfx g, int w) {
        if (lv.cineBars > 0.01f) {
            float h = 30 * lv.cineBars;
            g.rect(0, 0, w, h, 0xFF000000, false);
            g.rect(0, ViewSize.h - h, w, h, 0xFF000000, false);
        }
        // tarjeta del jefe
        if (bossCardT >= 0 && lv.boss != null) {
            BossDef d = lv.boss.def;
            float t = bossCardT;
            if (t > 0.5f && t < 4.2f) {
                float a = Mth.clamp(Math.min((t - 0.5f) / 0.5f, (4.2f - t) / 0.6f), 0, 1);
                if (t > 0.5f && t < 0.56f) Snd.sfx("boss_title", 0.9f);
                float cy = ViewSize.h - 76;
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
        if (toastT > 0 && ov == OV_NONE) { float tw = UI.small.width(toast) + 10; g.rect(w / 2f - tw / 2, 20, tw, 12, Mth.withAlpha(0x000010, (int) (150 * Math.min(1f, toastT))), false); UI.small.center(g, toast, w / 2f, 22, UI.GOLD, Math.min(1f, toastT)); }
        float ratio = s.maxHp > 0 ? rs.hp / s.maxHp : 0;
        UI.hpBar(g, 8, 8, ratio);
        String hpT = (ratio < 0.3f ? "! " : "") + Math.max(0, Math.round(rs.hp)) + "/" + Math.round(s.maxHp);
        float barW = UI.hpFrame != null ? UI.hpFrame.w : 90, tw = UI.small.width(hpT);
        g.rect(8 + barW / 2f - tw / 2f - 2, 10, tw + 4, 10, 0x88000010, false);     // texto dentro de la barra, con fondo (no choca con la barra del jefe a 480 px)
        UI.small.center(g, hpT, 8 + barW / 2f, 11, ratio < 0.3f ? UI.RED : UI.WHITE, 1f);
        PrepScreen.fitErr("hud vida texto", tw + 4, barW - 6, 0);
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
        String[] ic = {"burn", "freeze", "shield", "poison", "shock", "bleed", "lock", "star", "skull"};
        for (int i = 0; i < Ent.ST_COUNT; i++) {
            if (pl.st[i] > 0 && i != Ent.ROOT && i != Ent.STUN) { UI.icon(g, ic[i], sx, 38, 1f, Platform.TINT, Ent.ST_COLOR[i], 1f); sx += 18; }
        }
        for (int i = 0, x2 = 8; i < Ent.ST_COUNT; i++) {       // barrita de duracion bajo cada estado
            if (pl.st[i] > 0 && i != Ent.ROOT && i != Ent.STUN) { g.rect(x2, 55, 14 * Mth.clamp(pl.st[i] / 5f, 0, 1), 2, Ent.ST_COLOR[i] | 0xFF000000, false); x2 += 18; }
        }
        if (lv.flowT > 0) { UI.icon(g, "attack", sx, 38, 1f, Platform.TINT, 0xFFE070, 1f); g.rect(sx, 55, 14 * Mth.clamp(lv.flowT / 5f, 0, 1), 2, 0xFFFFE070, false); sx += 18; }
        if (lv.counterT > 0) { UI.icon(g, "parry", sx, 38, 1f, Platform.TINT, 0xFFFFFF, 1f); g.rect(sx, 55, 14 * Mth.clamp(lv.counterT / 1.1f, 0, 1), 2, 0xFFFFFFFF, false); sx += 18; }
        BlessRt bxr = rs.bx;
        if (bxr != null && bxr.any) {      // bendiciones: carga arcana y mejoras temporales activas
            if (bxr.arc >= 1f) { UI.icon(g, "shock", sx, 38, 1f, Platform.TINT, 0xF0F060, 1f); UI.small.draw(g, "x" + (int) bxr.arc, sx + 16, 42, 0xFFF0F060, 1f); sx += 34; }
            if (bxr.chOn(BRule.CH_DMG) || bxr.nextHitT > 0) { UI.icon(g, "attack", sx, 38, 1f, Platform.TINT, 0xFFB030, 1f); sx += 18; }
            if (bxr.chOn(BRule.CH_SPD) || bxr.chOn(BRule.CH_ATK)) { UI.icon(g, "jump", sx, 38, 1f, Platform.TINT, 0x6AE0FF, 1f); sx += 18; }
            if (bxr.slowT > 0) { UI.icon(g, "freeze", sx, 38, 1f, Platform.TINT, 0x9AD8FF, 1f); sx += 18; }
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
            String bp = Math.max(0, Math.round(100f * b.hp / b.maxHp)) + "%";
            UI.small.draw(g, bp, w / 2f + 56, 20, 0xFFE8D0C0, a);
            PrepScreen.fitErr("hud jefe nombre", UI.small.width(b.def.name), 2 * (w / 2f - 120), 0);
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
        if (!lv.cinematic && ov == OV_NONE) ArsenalUI.slots(g, lv, rs, cls, w, in, game.touchUiVisible() ? null : new String[]{glyphText(Input.B_WMAIN), glyphText(Input.B_WSEC)});
        // pista de interaccion
        Prop near = ov == OV_NONE ? lv.nearestInteractable() : null;
        if (near != null && near.kind.equals("weapon") && lv.pl.alive && !lv.cinematic) ArsenalUI.groundCard(g, lv, rs, near, w, hintFor(near));
        if (near != null && lv.pl.alive && !lv.cinematic && ov == OV_NONE) {
            ctx.render(g, this, w);
            if (near.kind.equals("portal") && ctx.vis) {
                Biome b = Biome.ALL[near.nextBiome];
                BossDef bd = BossDef.byBiome(b.id);
                float py = Math.max(40, ctx.y - 48);
                UI.panel(g, 0, w / 2f - 110, py, 220, 44, 0.9f);
                UI.small.center(g, b.name, w / 2f, py + 5, b.color, 1f);
                UI.small.center(g, "Jefe: " + bd.name, w / 2f, py + 18, UI.WHITE, 1f);
                UI.small.center(g, b.tagline, w / 2f, py + 30, UI.GREY, 1f);
            }
        } else ctx.vis = false;
        if (hintT > 0) UI.small.center(g, "No tienes suficiente oro", w / 2f, 120, UI.RED, Mth.clamp(hintT, 0, 1));
    }

    String hintFor(Prop p) {
        switch (p.kind) {
            case "door": return p.nextType == -2 ? "Salir" : p.nextType == -3 ? "Volver" : "Entrar";
            case "portal": return "Viajar";
            case "altar": return "Rezar";
            case "forge": return "Forjar";
            case "merchant": return "Comerciar";
            case "spirit": return "Ofrecer";
            case "shrine": return p.arg == 1 ? "Ofrecer sacrificio" : "Elegir pacto";
            case "cursed": return "Abrir (maldito)";
            case "cage": return "Liberar";
            case "relic": return "Tomar";
            case "fountain": return "Beber";
            case "npc": return "Hablar";
            case "weapon": return rs.sec == 0 ? "Recoger" : rs.sec == p.arg ? "Mejorar" : "Intercambiar";
            case "chest": return p.arg == 4 ? "¡Cofre superior!" : p.arg == 3 ? "¡Cofre secreto!" : "Abrir";
            default: return "Usar";
        }
    }

    private void renderBanner(Platform.Gfx g, int w) {
        renderChallenge(g, w);
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
    String glyphText(int action) {
        if (game.lastDevice == 1) return Pad.keyName(Save.S.kb[action]);
        int c = Save.S.pb[action];
        return c <= 0 ? "-" : Pad.name(game.padType, c);
    }

    int glyphColor(int action) {
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
        int[] acts = {Input.B_S1, Input.B_S2, Input.B_S3, Input.B_ULT, Input.B_GUARD, Input.B_GREN};
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
            g.rect(0, ViewSize.h - 3, w, 3, Mth.withAlpha(0xC00020, al), false);
        }
    }

    /** Dibuja un boton de accion (habilidad, arma 2ª, granada, escudo, pocion...) en la posicion del boton b. */
    private void drawBtn(Platform.Gfx g, int i, Input.Btn b, float alpha) {
        UI.roundButton(g, b.cx, b.cy, b.r, b.pointer >= 0 ? 1 : 0, alpha);
        if (i >= Input.B_S1 && i <= Input.B_ULT) {
            boolean ult = i == Input.B_ULT;
            int kk = ult ? 3 : i - Input.B_S1;
            boolean cooling = !ult && rs.cd[kk] > 0, ultCharging = ult && rs.ult < 100f;
            if (b.icon != null) UI.iconC(g, b.icon, b.cx, b.cy, 1f, cooling || ultCharging ? 0.5f : 1f);
            if (!cooling && !ultCharging) g.circle(b.cx, b.cy, b.r - 1, 0x99FFE8A0, true);        // lista: aro claro fijo (no solo color: tambien cambia el icono y desaparece el numero)
            if (skReady[kk] > 0) {                                                                  // senal breve y discreta al quedar lista
                float k2 = Mth.clamp(skReady[kk] / (ult ? 0.6f : 0.5f), 0, 1);
                g.circle(b.cx, b.cy, b.r + 1 + (1f - k2) * 7, Mth.withAlpha(0xFFFFF4C0, (int) (200 * k2)), true);
            }
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
                    String ct = cdText(cd);
                    g.rect(b.cx - UI.small.width(ct) / 2f - 1, b.cy - 5, UI.small.width(ct) + 2, 10, 0x88000010, false);   // fondo: contraste sobre cualquier icono
                    UI.small.center(g, ct, b.cx, b.cy - 4, UI.WHITE, 1f);
                }
            }
            return;
        }
        if (i == Input.B_GUARD) {
            boolean on = lv.pl.guarding;
            g.circle(b.cx, b.cy, b.r - 1, Mth.withAlpha(Items.SH_COL[rs.shield], on ? 150 : 60), false);
            UI.iconC(g, "parry", b.cx, b.cy, 1f, 1f);
            if (lv.pl.parryT > 0) g.circle(b.cx, b.cy, b.r + 2, 0xFFFFE070, true);
            if (lv.pl.parryFlash > 0) { float k = lv.pl.parryFlash / 0.3f; g.circle(b.cx, b.cy, b.r + 2 + (1f - k) * 6, Mth.withAlpha(0xFFFFF4C0, (int) (255 * k)), true); }
            else if (lv.pl.parryCd > 0.1f && on) { g.clipBegin(b.cx - b.r, b.cy - b.r, 2 * b.r, 2 * b.r * Mth.clamp(lv.pl.parryCd / Items.SH_CD[rs.shield], 0, 1) + 1); g.circle(b.cx, b.cy, b.r - 1, 0x88000000, false); g.clipEnd(); }
            return;
        }
        if (i == Input.B_SEC || i == Input.B_GREN) {
            boolean sec = i == Input.B_SEC;
            int ty = sec ? rs.sec : rs.gren, n = sec ? rs.secAmmo : rs.grenCount;
            int col = sec ? Items.SEC_COL[ty] : Items.GR_COL[ty];
            g.circle(b.cx, b.cy, b.r - 1, Mth.withAlpha(col, 70), false);
            UI.iconC(g, sec ? Items.SEC_ICON[ty] : Items.GR_ICON[ty], b.cx, b.cy - 1, 1f, n > 0 ? 1f : 0.35f);
            UI.small.center(g, sec ? Arsenal.ammoLabel(rs) : String.valueOf(n), b.cx, b.cy + b.r - 9, n > 0 ? UI.WHITE : UI.RED, 1f);
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
        in.btn[Input.B_INTERACT].visible = false;                       // sustituido por el boton contextual
        in.btn[Input.B_SEC].visible = false;                            // el disparo secundario es el boton de ataque con la secundaria seleccionada
        in.btn[Input.B_GREN].visible = rs.gren != 0 && !lv.cinematic;
        in.btn[Input.B_WMAIN].visible = in.btn[Input.B_WSEC].visible = !lv.cinematic;   // espacios de seleccion directa (se dibujan en renderHud)
        in.btn[Input.B_INV].visible = !lv.cinematic;
        // iconos de habilidades
        for (int i = 0; i < 3; i++) in.btn[Input.B_S1 + i].icon = cls.skills[i].icon;
        in.btn[Input.B_ULT].icon = cls.skills[3].icon;
        drawStick(g);
        for (int i = 0; i < Input.B_COUNT; i++) {
            Input.Btn b = in.btn[i];
            if (!b.visible) continue;
            if (i == Input.B_PAUSE) { UI.roundButton(g, b.cx, b.cy, b.r, b.pointer >= 0 ? 1 : 0, 0.7f); UI.iconC(g, "pause", b.cx, b.cy, 1f, 0.9f); continue; }
            if (i == Input.B_LEFT || i == Input.B_RIGHT || i == Input.B_DOWN) continue;   // dibujados por el joystick
            if (i == Input.B_WMAIN || i == Input.B_WSEC) continue;                        // dibujados como espacios de arma (ArsenalUI.slots)
            drawBtn(g, i, b, 0.7f);
        }
        // peligro de vida baja
        float hr = rs.hp / rs.stats.maxHp;
        if (hr < 0.3f && lv.pl.alive) {
            int a = (int) (40 + 30 * Math.sin(lv.time * 6));
            g.rect(0, 0, w, 3, Mth.withAlpha(0xC00020, a), false);
            g.rect(0, ViewSize.h - 3, w, 3, Mth.withAlpha(0xC00020, a), false);
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

    // ---------------------------------------------------------------- bendiciones: carta de oferta y lista de activas
    private static final String[] RAR_ES = {"común", "poco común", "rara", "épica", "legendaria"};

    /** Mejor sinergia a mostrar para una bendicion ofrecida: la mas avanzada (activa o a punto de activarse). */
    private int[] bestSyn(Blessing b) {
        int[] best = null;
        for (int[] s : BlessOffer.synergyInfo(rs, b)) {
            if (best == null || s[1] - s[2] > best[1] - best[2] || (s[1] - s[2] == best[1] - best[2] && s[1] > best[1])) best = s;
        }
        return best;
    }

    private void drawBlessCard(Platform.Gfx g, Hit h, float fadeIn) {
        int i = h.tag;
        Blessing b = Blessing.ALL[offer[i]];
        boolean selected = down == h || (game.keyboardUsed && offerSel == i);
        float y = h.y + (selected ? -4 : 0), cx = h.x + h.w / 2f;
        int rc = Blessing.RAR_COLOR[b.rar];
        UI.panel(g, selected ? 1 : 0, h.x, y, h.w, h.h, fadeIn);
        int ba = (int) (fadeIn * (selected ? 255 : 190));
        g.rect(h.x + 3, y + 3, h.w - 6, 2, Mth.withAlpha(rc, ba), false);
        if (b.rar >= 3 || selected) { g.rect(h.x + 1, y + 1, 2, h.h - 2, Mth.withAlpha(rc, ba), false); g.rect(h.x + h.w - 3, y + 1, 2, h.h - 2, Mth.withAlpha(rc, ba), false); }
        UI.small.center(g, RAR_ES[b.rar], cx, y + 8, rc, fadeIn);
        UI.small.center(g, UI.fitLabel(UI.small, BlessData.CAT_ES[b.cat - 'A'], h.w - 10), cx, y + 19, UI.GREY, fadeIn);       // categoria recortada si no cabe (a 480 px las 4 cartas son estrechas)
        UI.light(g, cx, y + 46, 20 + b.rar * 4, rc & 0xFFFFFF, (0.16f + 0.06f * b.rar + (selected ? 0.1f : 0f)) * fadeIn);
        UI.iconC(g, b.icon, cx, y + 46, 2f, fadeIn);
        int maxW = (int) h.w - 10;
        java.util.List<String> nm = UI.small.wrap(b.name, maxW);
        float ty = y + 66;
        for (String ln : nm) { UI.small.drawCenterRaw(g, ln, cx, ty, UI.GOLD, fadeIn); ty += 10; }
        int cur = rs.bless[b.id];
        UI.small.center(g, cur == 0 ? "NUEVA" : "Nv " + cur + " > " + (cur + 1), cx, ty + 1, cur == 0 ? UI.GREEN : UI.CYAN, fadeIn);
        ty += 14;
        // descripcion: el interlineado se ajusta para que nunca se corte
        int[] sy = null;       // las combinaciones no se anuncian: se descubren jugando
        float bottom = y + h.h - 8;
        int lines = UI.small.wrap(b.desc, (int) h.w - 14).size();
        int step = (int) Math.max(8, Math.min(UI.small.lineHeight() + 1, (bottom - ty) / Math.max(1, lines)));
        UI.small.drawWrapped(g, b.desc, h.x + 7, ty, (int) h.w - 14, 0xE8E0E0, fadeIn, step);
        PrepScreen.fitErr("carta " + b.key + " desc", ty + lines * step, bottom, 0);
        PrepScreen.fitErr("carta " + b.key + " nombre(" + nm.size() + " lineas)", nm.size() * 10, 20, 0);
        if (sy != null) {
            BSyn s = BlessData.syns()[sy[0]];
            boolean on = sy[3] == 1 || sy[1] >= sy[2];
            int sc = on ? 0xFFE070 : 0x8AD8FF;
            float by = y + h.h - 27;
            g.rect(h.x + 6, by - 3, h.w - 12, 1, Mth.withAlpha(sc, (int) (110 * fadeIn)), false);
            java.util.List<String> sn = UI.small.wrap(s.name, (int) h.w - 22);
            UI.iconC(g, "star", h.x + 11, by + 5, 1f, fadeIn);
            UI.small.drawCenterRaw(g, sn.get(0), cx + 5, by, sc, fadeIn);
            UI.small.center(g, on ? "Sinergia activa" : "Sinergia " + sy[1] + "/" + sy[2], cx, by + 11, sc, fadeIn);
        }
    }

    void openInventory(boolean fromPause) {
        if (lv == null || deadT >= 0 || winT >= 0) return;
        in.reset();
        inv.open(fromPause);
        ov = OV_INV; ovT = 0.3f; saveMenu = false;
        Snd.sfx("ui_open", 0.7f);
        layoutOverlay();
    }

    /** Cierra el inventario: vuelve al menu de pausa si se abrio desde ahi, o al juego. */
    void invClose() {
        if (ov != OV_INV) return;
        if (inv.fromPause) { ov = OV_PAUSE; ovT = 0.3f; in.reset(); Snd.sfx("ui_back", 0.7f); layoutOverlay(); }
        else closeOv();
    }

    private void openBlessList() {
        blTab = 0; blPage = 0;
        ov = OV_BLESSLIST; ovT = 0.3f;
        Snd.sfx("ui_open", 0.7f);
        layoutOverlay();
    }

    private static final int BL_PER_PAGE = 4;

    private void blPage(int d) {
        int pages = Math.max(1, (blRows.length + BL_PER_PAGE - 1) / BL_PER_PAGE);
        blPage = (blPage + d + pages) % pages;
        Snd.sfx("ui_hover", 0.6f);
        layoutOverlay();
    }

    /** Filas de la lista: bendiciones activas (por categoria) o sinergias con al menos un miembro. */
    private void layoutBlessList(int w) {
        java.util.List<Integer> rows = new ArrayList<>();
        if (blTab == 0) {
            for (char c = 'A'; c <= 'J'; c++) for (Blessing b : Blessing.ALL) if (b.cat == c && rs.bless[b.id] > 0) rows.add(b.id);
        } else {
            BSyn[] ss = BlessData.syns();
            java.util.List<Integer> act = new ArrayList<>(), part = new ArrayList<>();
            for (int si = 0; si < ss.length; si++) {
                int have = 0;
                for (int id : ss[si].members) if (rs.bless[id] > 0) have++;
                if (have >= ss[si].need) act.add(si); else if (have > 0) part.add(si);
            }
            rows.addAll(act); rows.addAll(part);
        }
        blRows = new int[rows.size()];
        for (int i = 0; i < blRows.length; i++) blRows[i] = rows.get(i);
        int pages = Math.max(1, (blRows.length + BL_PER_PAGE - 1) / BL_PER_PAGE);
        if (blPage >= pages) blPage = pages - 1;
        float py = 234;
        add(24, py, 104, 22, blTab == 0 ? "Bendiciones *" : "Bendiciones", () -> { blTab = 0; blPage = 0; layoutOverlay(); });
        add(132, py, 104, 22, blTab == 1 ? "Sinergias *" : "Sinergias", () -> { blTab = 1; blPage = 0; layoutOverlay(); });
        add(w / 2f - 12 - 40, py, 40, 22, "<", () -> blPage(-1)).disabled = pages <= 1;
        add(w / 2f + 12, py, 40, 22, ">", () -> blPage(1)).disabled = pages <= 1;
        add(w - 24 - 100, py, 100, 22, "Volver", this::back);
    }

    private void renderBlessList(Platform.Gfx g, int w) {
        float px = 12, pw = w - 24;
        UI.panel(g, 0, px, 8, pw, 222, 0.98f);
        UI.big.center(g, blTab == 0 ? "BENDICIONES ACTIVAS" : "SINERGIAS", w / 2f, 14, UI.GOLD, 1f);
        int pages = Math.max(1, (blRows.length + BL_PER_PAGE - 1) / BL_PER_PAGE);
        UI.small.right(g, "Pág. " + (blPage + 1) + "/" + pages, px + pw - 10, 16, UI.GREY, 1f);
        if (blRows.length == 0) {
            UI.small.center(g, blTab == 0 ? "Aún no tienes ninguna." : "Aún no tienes ninguna sinergia en marcha.", w / 2f, 100, UI.GREY, 1f);
        }
        BSyn[] ss = BlessData.syns();
        for (int k = 0; k < BL_PER_PAGE; k++) {
            int idx = blPage * BL_PER_PAGE + k;
            if (idx >= blRows.length) break;
            float y = 34 + k * 47;
            g.rect(px + 8, y + 44, pw - 16, 1, Mth.withAlpha(0x8A8AA0, 60), false);
            if (blTab == 0) {
                Blessing b = Blessing.ALL[blRows[idx]];
                int rc = Blessing.RAR_COLOR[b.rar];
                UI.panel(g, 0, px + 10, y + 6, 24, 24, 1f);
                UI.iconC(g, b.icon, px + 22, y + 18, 1f, 1f);
                UI.small.draw(g, b.name, px + 42, y + 2, rc, 1f);
                UI.small.right(g, "Nv " + rs.bless[b.id] + "/" + b.max, px + pw - 12, y + 2, UI.CYAN, 1f);
                float tx2 = px + 42 + Math.max(UI.small.width(b.name) + 8, 110);
                UI.small.draw(g, RAR_ES[b.rar], tx2, y + 2, rc, 1f);
                float limR = px + pw - 14 - UI.small.width("Nv " + rs.bless[b.id] + "/" + b.max);
                if (tx2 + UI.small.width(RAR_ES[b.rar]) + 8 + UI.small.width(BlessData.CAT_ES[b.cat - 'A']) <= limR)       // la categoria solo se muestra si cabe
                    UI.small.draw(g, BlessData.CAT_ES[b.cat - 'A'], tx2 + UI.small.width(RAR_ES[b.rar]) + 8, y + 2, UI.GREY, 1f);
                UI.small.drawWrapped(g, b.desc, px + 42, y + 13, (int) pw - 60, 0xE8E0E0, 1f, 9);
                PrepScreen.fitErr("lista " + b.key + " desc", y + 13 + UI.small.wrap(b.desc, (int) pw - 60).size() * 9, y + 44, 0);
                PrepScreen.fitErr("lista " + b.key + " cabecera", tx2 + UI.small.width(RAR_ES[b.rar]), limR, 0);
            } else {
                BSyn s = ss[blRows[idx]];
                int have = 0;
                for (int id : s.members) if (rs.bless[id] > 0) have++;
                boolean on = have >= s.need;
                int sc = on ? 0xFFE070 : 0x8AD8FF;
                UI.iconC(g, "star", px + 22, y + 18, 1.5f, on ? 1f : 0.45f);
                UI.small.draw(g, s.name, px + 42, y + 2, sc, 1f);
                UI.small.right(g, on ? "ACTIVA " + have + "/" + s.need : have + "/" + s.need, px + pw - 12, y + 2, on ? UI.GREEN : UI.GREY, 1f);
                UI.small.drawWrapped(g, on ? s.desc : s.desc, px + 42, y + 13, (int) pw - 60 - 0, on ? 0xE8E0E0 : 0xA09CA8, 1f, 9);
                PrepScreen.fitErr("lista sinergia " + s.id + " nombre", px + 42 + UI.small.width(s.name), px + pw - 16 - UI.small.width(on ? "ACTIVA " + have + "/" + s.need : have + "/" + s.need), 0);
                PrepScreen.fitErr("lista sinergia " + s.id + " desc", y + 13 + UI.small.wrap(s.desc, (int) pw - 60).size() * 9, y + 44, 0);
            }
        }
    }

    void dim(Platform.Gfx g, int w, float a) { g.rect(0, 0, w, ViewSize.h, Mth.withAlpha(0x000008, (int) (a * 255)), false); }

    private void renderOverlay(Platform.Gfx g, int w) {
        if (ov == OV_NONE) return;
        float fadeIn = Mth.clamp(ovT / 0.2f, 0, 1);
        switch (ov) {
            case OV_BLESS: {
                dim(g, w, 0.62f * fadeIn);
                UI.big.center(g, "ELIGE UNA BENDICIÓN", w / 2f, 8, UI.GOLD, fadeIn);
                UI.small.center(g, "Mejoras que duran toda la partida", w / 2f, 26, UI.GREY, fadeIn);
                for (Hit h : hits) drawBlessCard(g, h, fadeIn);
                break;
            }
            case OV_EVENT: {
                dim(g, w, 0.64f * fadeIn);
                UI.big.center(g, evTitle, w / 2f, 14, UI.GOLD, fadeIn);
                UI.small.center(g, evSub, w / 2f, 34, UI.GREY, fadeIn);
                for (Hit h : hits) {
                    if (h.label != null) continue;
                    int i = h.tag;
                    EvOpt o = evOpts.get(i);
                    boolean selected = down == h || (game.keyboardUsed && evSel == i);
                    float yoff = selected ? -4 : 0, cx = h.x + h.w / 2f, a = fadeIn * (o.ok ? 1f : 0.55f);
                    UI.panel(g, selected ? 1 : 0, h.x, h.y + yoff, h.w, h.h, a);
                    UI.iconC(g, o.icon, cx, h.y + 26 + yoff, 2f, a);
                    UI.small.center(g, o.name, cx, h.y + 52 + yoff, UI.GOLD, a);
                    int l1 = UI.small.drawWrapped(g, "+ " + o.pro, h.x + 8, h.y + 70 + yoff, (int) h.w - 16, 0xFF6AE08A, a);
                    UI.small.drawWrapped(g, "- " + o.con, h.x + 8, h.y + 74 + l1 + yoff, (int) h.w - 16, 0xFFFF7A7A, a);
                    if (!o.ok) UI.small.center(g, "No disponible", cx, h.y + h.h - 14 + yoff, UI.GREY, fadeIn);
                    PrepScreen.fitErr("suceso " + evTitle + " opcion " + i + " texto", h.y + 74 + l1 + UI.small.wrap("- " + o.con, (int) h.w - 16).size() * 9 + yoff, h.y + h.h - (o.ok ? 4 : 18) + yoff, 0);
                    PrepScreen.fitErr("suceso " + evTitle + " opcion " + i + " nombre", UI.small.width(o.name), h.w - 8, 0);
                }
                drawButtons(g);
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
                float ix = px + 182;
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
                float iw = px + 440 - 12 - ix;                       // ancho util de la columna derecha
                Stats s = rs.stats;
                float yy = 52;
                UI.small.draw(g, UI.fitLabel(UI.small, cls.name, iw), ix, yy, cls.color1, 1f);
                UI.small.draw(g, UI.fitLabel(UI.small, rs.biome == null ? "Santuario" : rs.biome.name + " · Sala " + Math.min(5, rs.roomNo + 1), iw), ix, yy + 11, UI.GREY, 1f);
                g.rect(ix, yy + 24, iw, 1, 0x55FFD25A, false);
                yy += 29;       // -- estadisticas
                String[] st = {"Daño x" + fmt(s.dmgMul) + "   Crítico " + Math.round(s.critChance * 100) + "%",
                        "Velocidad x" + fmt(s.speedMul) + "   Defensa " + Math.round((1 - s.dmgTaken) * 100) + "%",
                        "Arma nivel " + rs.weaponLvl + "   Frascos " + rs.potions + "/" + s.potionsMax,
                        "Enemigos " + rs.kills + "   Tiempo " + time(rs.time)};
                for (int i = 0; i < st.length; i++) UI.small.draw(g, UI.fitLabel(UI.small, st[i], iw), ix, yy + i * 11, i == 3 ? UI.GREY : UI.WHITE, 1f);
                yy += 4 * 11 + 3;
                g.rect(ix, yy, iw, 1, 0x55FFD25A, false);
                yy += 5;        // -- equipo
                UI.small.draw(g, UI.fitLabel(UI.small, "Especial: " + (rs.special == 0 ? "-" : Items.SP_NAME[rs.special]), iw), ix, yy, rs.special == 0 ? UI.GREY : Items.SP_COL[rs.special], 1f);
                UI.small.draw(g, UI.fitLabel(UI.small, "Sec: " + (rs.sec == 0 ? "-" : Items.SEC_NAME[rs.sec] + " x" + rs.secAmmo) + (rs.gren == 0 ? "" : "  Gran: x" + rs.grenCount), iw), ix, yy + 11, UI.WHITE, 1f);
                UI.small.draw(g, UI.fitLabel(UI.small, Items.SH_NAME[rs.shield] + " (parry " + Math.round(Items.SH_WIN[rs.shield] * 1000) + "ms)", iw), ix, yy + 22, Items.SH_COL[rs.shield] | 0x404040, 1f);
                yy += 36;
                g.rect(ix, yy, iw, 1, 0x55FFD25A, false);
                yy += 4;        // -- bendiciones (solo sus iconos; las combinaciones no se revelan)
                UI.small.draw(g, "Bendiciones", ix, yy, UI.GOLD, 1f);
                int n = 0, total = 0;
                for (Blessing b : Blessing.ALL) {
                    int lv2 = rs.bless[b.id];
                    if (lv2 <= 0) continue;
                    total++;
                    if (n >= 20) continue;
                    float bx = ix + (n % 10) * 23, by = yy + 12 + (n / 10) * 23;
                    UI.panel(g, 0, bx, by, 21, 21, 1f);
                    UI.iconC(g, b.icon, bx + 10.5f, by + 10.5f, 1f, 1f);
                    if (lv2 > 1) UI.small.draw(g, String.valueOf(lv2), bx + 14, by + 12, UI.GOLD, 1f);
                    n++;
                }
                if (total == 0) UI.small.draw(g, "Aún no tienes ninguna.", ix, yy + 13, UI.GREY, 1f);
                else if (total > 20) UI.small.right(g, "+" + (total - 20) + " más", ix + iw, yy, UI.GREY, 1f);
                PrepScreen.fitErr("pausa panel inferior", yy + 12 + (Math.min(total, 20) > 10 ? 2 : 1) * 23, 250, 0);
                break;
            }
            case OV_INV: inv.render(g, w); break;
            case OV_BLESSLIST: {
                dim(g, w, 0.8f);
                renderBlessList(g, w);
                break;
            }
            case OV_WCMP: {
                if (wcmp == null) break;
                dim(g, w, 0.74f * fadeIn);
                UI.big.center(g, "¿INTERCAMBIAR ARMA?", w / 2f, 8, UI.GOLD, fadeIn);
                UI.small.center(g, "Tu arma actual quedará en el suelo y podrás recogerla de nuevo", w / 2f, 27, UI.GREY, fadeIn);
                float pw = Math.min(210, (w - 30) / 2f), ph = 172, x0 = w / 2f - pw - 5, x1 = w / 2f + 5;
                UI.panel(g, wcmpSel == 0 ? 1 : 0, x0, 40, pw, ph, fadeIn);
                UI.panel(g, wcmpSel == 1 ? 1 : 0, x1, 40, pw, ph, fadeIn);
                UI.small.center(g, "TU ARMA SEC. · " + rs.secAmmo + " usos", x0 + pw / 2f, 45, 0xFFB8B0B8, fadeIn);
                UI.small.center(g, "NUEVA · " + Items.SEC_AMMO[wcmp.id] + " usos", x1 + pw / 2f, 45, UI.GOLD, fadeIn);
                ArsenalUI.sheet(g, x0 + 8, 58, pw - 16, rs.sec, 0, rs.secAmmo);
                ArsenalUI.sheet(g, x1 + 8, 58, pw - 16, wcmp.id, rs.sec, 0);
                UI.small.center(g, "+ mejor · - peor · = igual que tu arma actual", w / 2f, 211, 0xFF9890A0, fadeIn);
                for (Hit h : hits) { h.plain = false; drawButton(g, h); }
                break;
            }
            case OV_REVIVE: {
                dim(g, w, 0.72f * fadeIn);
                float px = w / 2f - 130;
                UI.panel(g, 2, px, 34, 260, 200, fadeIn);
                UI.big.center(g, "HAS CAÍDO", w / 2f, 44, UI.RED, fadeIn);
                UI.small.center(g, "Piso " + rs.floor + " · " + rs.floorsDone + " completados", w / 2f, 66, UI.GREY, fadeIn);
                int left = rs.ruleset.maxRevives - rs.revivesUsed;
                UI.small.center(g, "Revividas: " + rs.revivesUsed + "/" + rs.ruleset.maxRevives + " usadas", w / 2f, 82, UI.PURPLE, fadeIn);
                UI.iconC(g, "gem", px + 22, 100, 1f, fadeIn);
                UI.small.draw(g, "Tus gemas: " + Wallet.gems(), px + 34, 96, UI.PURPLE, fadeIn);
                if (rs.revivesUsed == 2) UI.small.center(g, "Última revivida: solo con gemas", w / 2f, 110, UI.GREY, fadeIn);
                if (!reviveMsg.isEmpty()) UI.small.center(g, reviveMsg, w / 2f, 228, UI.RED, fadeIn);
                drawButtons(g);
                break;
            }
            case OV_DEAD: case OV_WIN: {
                boolean win = ov == OV_WIN;
                dim(g, w, 0.7f * fadeIn);
                if (rs.infinite && ov == OV_DEAD && infResult != null) {
                    Infinite.Result r = infResult;
                    float px = w / 2f - 150;
                    UI.panel(g, 2, px, 14, 300, 232, fadeIn);
                    UI.big.center(g, "RUN INFINITA", w / 2f, 22, UI.PURPLE, fadeIn);
                    UI.small.center(g, rs.biome == null ? "" : "Caíste en " + rs.biome.name + " · piso " + r.reached + (r.mods != 0 ? " · Retos +" + Infinite.bonusPct(r.mods) + "%" : ""), w / 2f, 44, UI.GREY, fadeIn);
                    String[][] rows = {{"Pisos completados", String.valueOf(r.floors)}, {"Piso alcanzado", String.valueOf(r.reached)}, {"Enemigos derrotados", String.valueOf(r.kills)},
                            {"Jefes derrotados", String.valueOf(r.bosses)}, {"Tiempo de supervivencia", time(r.timeS)}, {"Revividas usadas", r.revives + "/" + rs.ruleset.maxRevives}};
                    float y = 60;
                    for (String[] rw : rows) {
                        UI.small.draw(g, rw[0], px + 24, y, UI.WHITE, fadeIn);
                        UI.small.right(g, rw[1], px + 276, y, UI.GOLD, fadeIn);
                        y += 13;
                    }
                    y += 4;
                    g.rect(px + 20, y, 260, 1, Mth.withAlpha(0x6A5A8A, (int) (255 * fadeIn)), false);
                    y += 6;
                    UI.big.center(g, "PUNTAJE " + r.score, w / 2f, y, UI.GOLD, fadeIn);
                    y += 20;
                    if (infRecord) UI.small.center(g, "¡NUEVO RÉCORD DE PISOS!", w / 2f, y, UI.GREEN, fadeIn);
                    else UI.small.center(g, "Mejor: " + Save.S.infBestFloor + " pisos · " + Save.S.infBestScore + " pts", w / 2f, y, UI.GREY, fadeIn);
                    y += 14;
                    UI.icon(g, "soul", px + 24, y - 3, 1f);
                    UI.small.draw(g, "Almas conservadas", px + 44, y, UI.SOUL, fadeIn);
                    UI.small.right(g, "+" + sumSouls, px + 276, y, UI.SOUL, fadeIn);
                    drawButtons(g);
                    break;
                }
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
