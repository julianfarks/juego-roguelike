package com.julianfarks.roguelike.core;

/**
 * Centro de operaciones: una sala larga de piedra que se recorre desplazando la camara (arrastrar, flechas o los
 * indicadores). Cada estacion es un objeto del mundo con su propio arte; la sala se hornea con el mismo atlas de
 * baldosas que las mazmorras (Room.bake).
 */
final class Ops extends Screen {
    static boolean active;
    // identificadores de estacion, en orden de izquierda a derecha
    static final int ARMORY = 0, TROPHY = 1, PREP = 2, CONTINUE = 3, PORTAL = 4, SANCT = 5, SHOP = 6, CODEX = 7, GARDEN = 8, COMP = 9, RECORDS = 10, N = 11;
    private static final int FLOOR = 224;               // y del suelo
    static final int TILES_W = 120, WORLD = TILES_W * 16;
    static final float[] SX = {90, 322, 596, 730, 924, 1108, 1242, 1376, 1516, 1656, 1808};
    static final float[] SW = {80, 336, 88, 36, 96, 80, 112, 72, 132, 80, 88};
    private static final float[] SH = {104, 100, 72, 56, 112, 92, 96, 104, 64, 104, 100};
    private static final String[] NAME = {"Armería", "Trofeos", "Preparación", "Continuar", "EXPEDICIÓN", "Santuario", "Tienda", "Colección", "Jardín", "Compañeros", "Récords"};
    private static final int[] GLOW = {0xFFB070, 0xFFD25A, 0xFFC070, 0xFFC070, 0xFF5A30, 0x9A7AFF, 0xFFA040, 0x7AF0FF, 0x7AFFA0, 0xB080FF, 0xFFD25A};
    // memoria entre visitas: al volver de una estacion el espadachin sigue donde estaba
    private static float sCam = -1, sHeroX = -1;
    private static int sCur = PORTAL;

    private final Platform.Img[] bgl = new Platform.Img[3];
    private Platform.Img baked;
    private Room hall;
    private java.util.List<int[]> torches;
    private final Particles ps = new Particles();
    private final Rng rng = new Rng(5);
    private final float[] appear = new float[N];
    private final Hit[] spotHit = new Hit[N];
    private final Hit[] dotHit = new Hit[N];
    private Hit leftHit, rightHit;
    private int cur = PORTAL;
    private int row = 0;               // 0 estaciones, 1 botones
    private int extraSel = 0;
    private float cam, heroX;
    private boolean follow = true;
    private boolean heroMoving, heroRight = true;
    private float pulse, enterT, flash;
    private int panId = -1; private float panStartX, camStart; private boolean panning, panCandidate;
    private Hit diffBtn, backBtn, infBtn;
    private final java.util.List<Hit> extras = new java.util.ArrayList<>();
    private String toast = ""; private float toastT;
    private float trophyGlow;             // brillo al inspeccionar los trofeos

    Ops(Game g) {
        super(g);
        for (int i = 0; i < 3; i++) bgl[i] = Assets.img("bg/bg_eclipse_" + i + ".png");
        buildHall();
        cur = sCur;
    }

    Ops(Game g, String toastMsg) { this(g); toast = toastMsg; toastT = 3f; }

    private void buildHall() {
        Room r = new Room(TILES_W, 17, Room.HUB, Biome.ALL[7]);
        int W = TILES_W;
        for (int x = 0; x < W; x++) for (int y = 0; y < 17; y++) if (y >= 14 || y < 2 || x < 1 || x >= W - 1) r.set(x, y, Room.SOLID);
        for (int k = 8; k < W - 6; k += 14) {                      // nervaduras de la boveda
            for (int x = k - 3; x <= k + 3; x++) r.set(x, 2, Room.SOLID);
            for (int x = k - 2; x <= k + 2; x++) r.set(x, 3, Room.SOLID);
            for (int x = k - 1; x <= k + 1; x++) r.set(x, 4, Room.SOLID);
            r.set(k, 5, Room.SOLID);
        }
        // dais del portal
        int pt = Math.round(SX[PORTAL] / 16f);
        for (int x = pt - 4; x <= pt + 3; x++) r.set(x, 13, Room.SOLID);
        for (int x = pt - 3; x <= pt + 2; x++) r.set(x, 12, Room.SOLID);
        // ventanales hacia el cielo entre estaciones (detras del portal y en los pasillos)
        for (int k = 8; k < W - 6; k += 14) for (int y = 5; y <= 9; y++) for (int x = k + 6; x <= k + 8; x++) if (x < W - 2) r.vista[y * W + x] = true;
        for (int k = 8; k < W - 6; k += 14) {
            r.deco[3 * W + k - 1] = (short) ((3 << 8) | (k & 7));
            r.deco[3 * W + k + 1] = (short) ((3 << 8) | ((k + 3) & 7));
            r.deco[2 * W + k] = 0;
        }
        for (int k = 8; k < W - 6; k += 14) { int x = k + 7; if (x < W - 2) r.deco[3 * W + x] = (short) ((2 << 8) | (x & 7)); }
        // antorchas cerca de cada estacion
        for (int i = 0; i < N; i++) {
            int tx = Math.round((SX[i] - SW[i] / 2f - 14) / 16f);
            if (i == TROPHY || i == GARDEN) tx = Math.round((SX[i] - SW[i] / 2f - 10) / 16f);
            if (tx > 1 && tx < W - 2) r.deco[7 * W + tx] = (short) ((5 << 8) | (tx & 3));
        }
        r.deco[7 * W + W - 3] = (short) ((5 << 8) | 1);
        hall = r;
        r.bake(game.P);
        baked = r.baked;
        torches = r.animated();
    }

    @Override void enter() {
        active = true;
        Snd.music(Snd.MENU_MUSIC, true);
        Snd.ambient(null, 0);
        enterT = 0;
        layout();
        heroX = sHeroX < 0 ? standX(PORTAL) : sHeroX;
        cam = sCam < 0 ? camFor(cur) : sCam;
        sHeroX = heroX;
    }

    /** Donde espera el espadachin frente a cada estacion (el portal, en el centro del dais). */
    static float standX(int i) { return i == PORTAL ? SX[i] : SX[i] - SW[i] / 2f + 12; }

    private float camMax() { return Math.max(0, WORLD - W()); }
    private float camFor(int i) { return Mth.clamp(SX[i] - W() / 2f, 0, camMax()); }

    @Override void layout() {
        hits.clear(); extras.clear();
        int w = W();
        for (int i = 0; i < N; i++) {
            final int id = i;
            float hw = Math.max(SW[i] + 8, 60);
            Hit h = add(SX[i] - hw / 2f - cam, FLOOR - SH[i], hw, SH[i] + 22, null, () -> select(id, true));
            h.plain = true; h.noSound = true;
            h.tag = 1;
            h.disabled = (i == CONTINUE && !RunSave.any(game.P));
            spotHit[i] = h;
        }
        // indicadores de pagina (tocar = ir a la estacion vecina)
        leftHit = add(0, 100, 26, 80, null, () -> step(-1)); leftHit.plain = true; leftHit.noSound = true;
        rightHit = add(w - 26, 100, 26, 80, null, () -> step(1)); rightHit.plain = true; rightHit.noSound = true;
        float mx = w / 2f - (N * 13) / 2f + 20;
        for (int i = 0; i < N; i++) {
            final int id = i;
            Hit d = add(mx + i * 13, 246, 13, 24, null, () -> { cur = id; follow = true; row = 0; Snd.sfx("ui_hover", 0.5f); });
            d.plain = true; d.noSound = true;
            dotHit[i] = d;
        }
        backBtn = add(6, 247, 58, 21, "Volver", () -> back());
        extras.add(backBtn);
        infBtn = add(68, 247, 74, 21, "Infinito", this::startInfinite);
        extras.add(infBtn);
        diffBtn = add(w - 126, 247, 120, 21, diffLabel(), () -> { Save.S.diffSel = (Save.S.diffSel + 1) % 3; Save.S.write(); diffBtn.label = diffLabel(); });
        extras.add(diffBtn);
        float bx = w - 6;
        String[] nm = {"Opciones", "Códigos", "Historia"};
        Runnable[] ac = {() -> game.go(new Screens.Options(game, false)), () -> game.go(new CodesScreen(game)), () -> game.go(new StoryScreens.Historia(game, false))};
        for (int i = 0; i < 3; i++) { bx -= 62; Hit h = add(bx, 5, 58, 22, nm[i], ac[i]); extras.add(h); }
        if (Save.S.devUnlocked) extras.add(add(6, 5, 90, 22, "Desarrollador", () -> game.go(new DevScreens.Menu(game))));
        placeHits();
    }

    private void placeHits() {
        for (int i = 0; i < N; i++) if (spotHit[i] != null) spotHit[i].x = SX[i] - spotHit[i].w / 2f - cam;
        if (leftHit != null) { leftHit.disabled = cam <= 1; rightHit.disabled = cam >= camMax() - 1; }
    }

    private String diffLabel() { int d = Save.S.diffSel; return "Dificultad: " + (d == 0 ? "Fácil" : (d == 2 ? "Difícil" : "Normal")); }

    ClassDef hero() { int id = Save.S.lastClass; if (id < 0 || id > 9 || !Save.S.classUnlocked[id]) id = 0; return ClassDef.ALL[id]; }

    private void step(int d) {
        cur = Math.max(0, Math.min(N - 1, cur + d)); follow = true; row = 0; Snd.sfx("ui_hover", 0.5f);
    }

    private void select(int id, boolean doIt) {
        cur = id; follow = true; row = 0;
        if (doIt) activate(id);
    }

    private void activate(int id) {
        if (spotHit[id].disabled) { Snd.sfx("ui_error", 0.7f); if (id == CONTINUE) { toast = "No hay partidas guardadas"; toastT = 2f; } return; }
        flash = 0.25f;
        sCur = id; sCam = cam; sHeroX = heroX;
        Snd.sfx(id == PORTAL ? "ui_start_run" : "ui_click", 0.9f);
        switch (id) {
            case ARMORY: game.go(new ClassScreen(game)); break;
            case TROPHY: trophyGlow = 1f; game.go(new OpsScreens.Trophy(game)); break;
            case PREP: game.go(new PrepScreen(game)); break;
            case CONTINUE: game.go(new LoadScreen(game)); break;
            case SANCT: game.go(new SanctuaryScreen(game)); break;
            case SHOP: game.go(new ShopScreen(game)); break;
            case CODEX: game.go(new CodexScreens.CodexScr(game)); break;
            case GARDEN: game.go(new CodexScreens.GardenScr(game)); break;
            case COMP: game.go(new CodexScreens.Comp(game)); break;
            case RECORDS: game.go(new OpsScreens.Stats(game)); break;
            default: game.go(new PrepScreen(game));   // el portal NO empieza el combate: abre la preparacion
        }
    }

    /** Abre la preparacion de expedicion (usado por el portal y por el banco de pruebas automatico). */
    void startGame() { game.go(new PrepScreen(game)); }

    /** Modo infinito (atajo de la barra inferior): solo tras vencer al Cazador. Abre la preparacion en modo infinito. */
    void startInfinite() {
        if (!Save.S.finalBeaten) { Snd.sfx("ui_error", 0.7f); toast = "Modo infinito: se desbloquea al vencer al Cazador"; toastT = 3f; return; }
        PrepScreen.infiniteMode = true;
        sCur = PORTAL;
        game.go(new PrepScreen(game));
    }

    @Override boolean back() { sCur = cur; sCam = cam; sHeroX = heroX; game.go(new Screens.Title(game)); return true; }

    @Override void key(int code, boolean down) {
        if (!down) return;
        game.keyboardUsed = true;
        if (code == 27) { back(); return; }
        if (code == 10 || code == 32 || code == 'J') {
            if (row == 0) activate(cur);
            else click(extras.get(Math.min(extraSel, extras.size() - 1)));
            return;
        }
        boolean left = code == 37 || code == 'A', right = code == 39 || code == 'D', up = code == 38 || code == 'W', dn = code == 40 || code == 'S';
        if (row == 0) {
            if (left) step(-1);
            else if (right) step(1);
            else if (up || dn) { row = 1; extraSel = 0; Snd.sfx("ui_hover", 0.5f); }
        } else {
            int n = extras.size();
            if (left) { extraSel = (extraSel + n - 1) % n; Snd.sfx("ui_hover", 0.5f); }
            else if (right) { extraSel = (extraSel + 1) % n; Snd.sfx("ui_hover", 0.5f); }
            else if (up || dn) { row = 0; Snd.sfx("ui_hover", 0.5f); }
        }
    }

    @Override void touch(int id, int action, float x, float y) {
        if (action == Platform.ACTION_DOWN) {
            game.keyboardUsed = false;
            if (panId < 0) { panId = id; panStartX = x; camStart = cam; panning = false; }
            super.touch(id, action, x, y);
            panCandidate = down != null && (down.tag == 1 || down == leftHit || down == rightHit) || down == null;
            return;
        }
        if (id == panId && action == Platform.ACTION_MOVE && panCandidate) {
            if (!panning && Math.abs(x - panStartX) > 7) { panning = true; down = null; downId = -1; follow = false; }
            if (panning) { cam = Mth.clamp(camStart - (x - panStartX), 0, camMax()); placeHits(); }
            return;
        }
        if (id == panId && action == Platform.ACTION_UP) { boolean was = panning; panId = -1; panning = false; if (was) { down = null; downId = -1; return; } }
        super.touch(id, action, x, y);
    }

    @Override void update(float dt) {
        t += dt; pulse += dt; enterT += dt;
        if (flash > 0) flash -= dt;
        if (toastT > 0) toastT -= dt;
        if (trophyGlow > 0) trophyGlow -= dt * 0.5f;
        int w = W();
        for (int i = 0; i < N; i++) appear[i] = Mth.clamp((enterT - 0.2f - Math.abs(i - cur) * 0.07f) / 0.5f, 0, 1);
        if (follow && !panning) cam += (camFor(cur) - cam) * Math.min(1f, dt * 6f);
        cam = Mth.clamp(cam, 0, camMax());
        // el espadachin camina hasta la estacion activa
        float tx = standX(cur);
        float dx = tx - heroX;
        heroMoving = Math.abs(dx) > 3;
        if (heroMoving) { heroRight = dx > 0; heroX += Math.signum(dx) * Math.min(Math.abs(dx), 170f * dt); }
        placeHits();
        // polvo en suspension (solo en pantalla) y brasas de antorcha / portal
        if (rng.chance(dt * 9)) ps.spawn(cam + rng.f(0, w), rng.f(40, 200), rng.f(2, 9), rng.f(-3, 3), rng.f(4, 8), 1, 0, 0xFFE8B0, true);
        for (int[] d : torches) if (d[2] == 5 && d[0] + 16 > cam && d[0] < cam + w && rng.chance(dt * 5)) ps.spawn(d[0] + 8, d[1] + 4, rng.f(-4, 4), -rng.f(8, 22), rng.f(0.6f, 1.4f), 1, 0, 0xFF9A40, true);
        if (Math.abs(SX[PORTAL] - cam - w / 2f) < w / 2f + 60) ps.spawn(SX[PORTAL] + rng.f(-14, 14), FLOOR - 24, rng.f(-6, 6), -rng.f(14, 40), rng.f(0.8f, 1.8f), 1, 0, rng.chance(0.5f) ? 0xFFB070 : 0xFF5A30, true);
        // chispas de cristal del jardin
        if (Math.abs(SX[GARDEN] - cam - w / 2f) < w / 2f + 70 && rng.chance(dt * 6)) ps.spawn(SX[GARDEN] + rng.f(-60, 60), FLOOR - 40, rng.f(-2, 2), -rng.f(4, 12), rng.f(0.8f, 1.5f), 1, 0, 0xA8FFD0, true);
        ps.update(dt);
    }

    private boolean selected(int i) { return row == 0 && cur == i && (game.keyboardUsed || down != null && down == spotHit[i]); }

    @Override void render(Platform.Gfx g) {
        int w = W();
        float k = Mth.clamp(enterT / 0.8f, 0, 1);
        int ci = Math.round(cam);
        g.clear(0xFF080408);
        float[] fac = {3f, 6f, 11f};
        float[] par = {0.06f, 0.12f, 0.22f};
        for (int i = 0; i < 3; i++) {
            Platform.Img im = bgl[i];
            if (im == null) continue;
            float sc = Math.max(1f, Platform.VIEW_H / (float) im.h);
            float dw = im.w * sc, dh = im.h * sc;
            float off = (t * fac[i] + cam * par[i] * 4f) % dw;
            for (float x = -off; x < w; x += dw) g.image(im, 0, 0, im.w, im.h, Math.round(x), Math.round(Platform.VIEW_H - dh), Math.round(dw), Math.round(dh), 0, 0, 1f);
        }
        if (baked != null) g.image(baked, 0, 0, baked.w, baked.h, -ci, 0, baked.w, baked.h, 0, 0, 1f);
        g.rect(0, FLOOR, w, 6, 0x40000000, false);
        float fl = 0.85f + 0.15f * (float) Math.sin(t * 11);
        Platform.Img ts = Assets.img("tiles/tiles_eclipse.png");
        for (int[] d : torches) {
            if (d[0] + 80 < cam || d[0] - 80 > cam + w) continue;
            UI.light(g, d[0] + 8 - ci, d[1] + 8, d[2] == 5 ? 64 : 44, 0xFFC070, 0.30f * fl);
            if (d[2] == 5 && ts != null) g.image(ts, (((d[3] + (int) (t * 8)) & 3)) * 16, 4 * 16, 16, 16, d[0] - ci, d[1], 16, 16, 0, 0, 1f);
        }
        // charcos de luz de cada estacion en el suelo
        for (int i = 0; i < N; i++) {
            float sx = SX[i] - ci;
            if (sx < -120 || sx > w + 120) continue;
            UI.light(g, sx, FLOOR - 2, SW[i] * 0.7f, GLOW[i], (i == PORTAL ? 0.18f : 0.08f) * appear[i]);
        }
        drawStations(g, w);
        ps.render(g, ci, 0);
        UI.light(g, SX[PORTAL] - ci, FLOOR - 50, 100, 0xFF5A30, 0.12f + 0.05f * (float) Math.sin(pulse * 2));
        g.rect(0, 0, w, Platform.VIEW_H, Mth.withAlpha(0x120408, 40), false);
        if (UI.vignette != null) g.image(UI.vignette, 0, 0, UI.vignette.w, UI.vignette.h, 0, 0, w, Platform.VIEW_H, 0, 0, 0.7f);
        drawChevrons(g, w);
        drawButtons(g);
        if (!Save.S.finalBeaten && infBtn != null) UI.icon(g, "lock", infBtn.x + infBtn.w - 15, infBtn.y + 3, 1f);
        drawMiniMap(g);
        // ficha: recursos
        float ry = Save.S.devUnlocked ? 40 : 16;
        UI.iconC(g, "soul", 14, ry, 1f, 1f);
        UI.small.draw(g, String.valueOf(Save.S.souls), 26, ry - 5, UI.SOUL, 1f);
        UI.iconC(g, "relic", 14 + 56, ry, 1f, 1f);
        UI.small.draw(g, Save.S.relicCount() + "/8", 26 + 56, ry - 5, UI.GOLD, 1f);
        UI.iconC(g, "gem", 14 + 112, ry, 1f, 1f);
        UI.small.draw(g, String.valueOf(Wallet.gems()), 26 + 112, ry - 5, UI.PURPLE, 1f);
        tooltip(g, w, cur);
        if (row == 1 && game.keyboardUsed) {
            Hit h = extras.get(Math.min(extraSel, extras.size() - 1));
            int c = Mth.withAlpha(0xFFD25A, (int) ((0.6f + 0.4f * (float) Math.sin(pulse * 8)) * 255));
            g.rect(h.x - 2, h.y - 2, h.w + 4, 1, c, false); g.rect(h.x - 2, h.y + h.h + 1, h.w + 4, 1, c, false);
            g.rect(h.x - 2, h.y - 2, 1, h.h + 4, c, false); g.rect(h.x + h.w + 1, h.y - 2, 1, h.h + 4, c, false);
        }
        if (toastT > 0) { UI.panel(g, 0, w / 2f - 160, 76, 320, 18, 0.95f); UI.small.center(g, toast, w / 2f, 80, UI.GOLD, Mth.clamp(toastT, 0, 1)); }
        if (k < 1) g.rect(0, 0, w, Platform.VIEW_H, Mth.withAlpha(0x000000, (int) ((1 - k) * 255)), false);
        if (flash > 0) g.rect(0, 0, w, Platform.VIEW_H, Mth.withAlpha(0xFFE8C0, (int) (Mth.clamp(flash * 4, 0, 1) * 70)), true);
    }

    private void drawChevrons(Platform.Gfx g, int w) {
        if (UI.arrow == null) return;
        float b = (float) Math.sin(pulse * 4) * 2;
        if (!leftHit.disabled) g.imageRot(UI.arrow, 0, 0, 8, 8, 4 - b, 134, 12, 12, 3.1416f, 0, 0, 0.8f);
        if (!rightHit.disabled) g.imageRot(UI.arrow, 0, 0, 8, 8, w - 16 + b, 134, 12, 12, 0f, 0, 0, 0.8f);
    }

    private void drawMiniMap(Platform.Gfx g) {
        for (int i = 0; i < N; i++) {
            Hit d = dotHit[i];
            boolean on = i == cur;
            int c = on ? 0xFFFFD25A : (i == PORTAL ? 0xFFFF8A50 : 0xFF6A6480);
            g.rect(d.x + 4, d.y + 8, 5, 5, c, false);
            if (on) { g.rect(d.x + 3, d.y + 7, 7, 1, 0xFFFFE0A0, false); g.rect(d.x + 3, d.y + 13, 7, 1, 0xFFFFE0A0, false); }
        }
    }

    private void tooltip(Platform.Gfx g, int w, int i) {
        String sub;
        ClassDef c = hero();
        switch (i) {
            case ARMORY: sub = "Espadachines y habilidades. Ahora: " + c.name; break;
            case TROPHY: sub = Save.S.relicCount() + (Save.S.finalBeaten ? 1 : 0) + " de 9 jefes derrotados · " + Trophies.count(Save.S) + "/" + Trophies.ALL.length + " logros"; break;
            case PREP: sub = "Revisa tu equipo antes de partir"; break;
            case CONTINUE: sub = RunSave.any(game.P) ? "Retoma una partida guardada" : "No hay partidas guardadas"; break;
            case PORTAL: sub = "Desciende al Abismo como " + c.name; break;
            case SANCT: sub = "Mejoras permanentes, clases y desbloqueos"; break;
            case SHOP: sub = "Apariencias · almas y gemas por separado"; break;
            case CODEX: sub = "Bestiario: " + Codex.foundEntries() + " / " + Codex.totalEntries() + " descubiertos"; break;
            case GARDEN: sub = "Cristales que crecen con tus almas"; break;
            case COMP: { int a = Companions.active(Save.S); sub = a < 0 ? "Espíritus aliados · ninguno equipado" : "Equipado: " + Companions.NAME[a]; break; }
            default: sub = "Estadísticas, logros y récords"; break;
        }
        float tw = Math.min(w - 40, 330);
        UI.panel(g, i == PORTAL ? 1 : 0, w / 2f - tw / 2f, 34, tw, 34, 0.95f);
        UI.small.center(g, NAME[i], w / 2f, 39, i == PORTAL ? UI.GOLD : UI.WHITE, 1f);
        UI.small.center(g, sub, w / 2f, 53, UI.GREY, 1f);
    }

    // ------------------------------------------------------------------ estaciones
    private void spr(Platform.Gfx g, String name, String anim, float x, float y, float scale, float a, int flags, int tint) {
        Sheet sh = Assets.spr(name);
        if (sh == null || sh == Sheet.EMPTY) return;
        sh.drawAt(g, anim, t, Math.round(x), Math.round(y), true, scale, flags, tint, a);
    }

    private void drawStations(Platform.Gfx g, int w) {
        float cx0 = cam;
        for (int i = 0; i < N; i++) {
            float a = appear[i];
            if (a <= 0 || SX[i] + SW[i] < cx0 - 40 || SX[i] - SW[i] > cx0 + w + 40) continue;
            boolean sel = selected(i);
            float x = SX[i] - Math.round(cam), fy = FLOOR + (1 - a) * 6;
            boolean dis = i == CONTINUE && spotHit[i].disabled;
            float lift = sel ? -1f : 0;
            switch (i) {
                case ARMORY: spr(g, "ops_armory", "idle", x, fy + lift, 1f, a, 0, 0); UI.light(g, x, fy - 50, sel ? 52 : 38, 0xFFC070, 0.16f * a); break;
                case TROPHY: drawTrophyWall(g, x, fy, a, sel); break;
                case PREP: spr(g, "ops_prep", "idle", x, fy + lift, 1f, a, 0, 0); UI.light(g, x + 33, fy - 52, sel ? 46 : 34, 0xFFC070, (0.22f + 0.05f * (float) Math.sin(t * 9)) * a); break;
                case CONTINUE: drawDoor(g, x, fy, a, sel, dis); break;
                case PORTAL: drawPortal(g, x, a, sel); break;
                case SANCT: spr(g, "prop_sanctuary", "idle", x, fy, 1.4f, a, 0, 0); UI.light(g, x, fy - 56, sel ? 52 : 38, 0x9A7AFF, 0.22f * a); break;
                case SHOP: drawShop(g, x, fy, a, sel); break;
                case CODEX: spr(g, "ops_codex", "idle", x, fy + lift, 1f, a, 0, 0); UI.light(g, x - 6, fy - 62, sel ? 40 : 28, 0x7AF0FF, 0.2f * a); break;
                case GARDEN: drawGarden(g, x, fy, a, sel); break;
                case COMP: spr(g, "ops_nook", "idle", x, fy + lift, 1f, a, 0, 0); UI.light(g, x, fy - 62, sel ? 48 : 34, 0xB080FF, 0.2f * a); break;
                default: spr(g, "ops_board", "idle", x, fy + lift, 1f, a, 0, 0); UI.light(g, x, fy - 56, sel ? 46 : 32, 0xFFD25A, 0.12f * a); break;
            }
            if (i == PREP) drawNpc(g, "prop_npc_0", SX[i] + 62 - Math.round(cam), fy, a);
            if (i == SHOP) { /* mercader dentro del puesto */ }
            if (i == CODEX) drawNpc(g, "prop_npc_1", SX[i] + 54 - Math.round(cam), fy, a);
            if (i == GARDEN) drawNpc(g, "prop_npc_2", SX[i] + 80 - Math.round(cam), fy, a);
            // placa con el nombre
            float pw = (float) Math.max(46, UI.small.width(NAME[i]) + 12);
            float py = FLOOR + 6;
            boolean hot = sel || i == PORTAL || i == cur;
            UI.panel(g, hot ? 1 : 0, x - pw / 2f, py, pw, 14, 0.9f * a);
            UI.small.center(g, NAME[i], x, py + 3, dis ? UI.GREY : (hot ? UI.GOLD : UI.WHITE), a);
            if (sel) outline(g, spotHit[i]);
        }
        drawHero(g);
    }

    private void drawNpc(Platform.Gfx g, String name, float x, float fy, float a) {
        Sheet sh = Assets.spr(name);
        if (sh == null || sh == Sheet.EMPTY) return;
        sh.drawAt(g, "idle", t + x * 0.013f, Math.round(x), Math.round(fy), false, 1f, 0, 0, a);
    }

    private void drawHero(Platform.Gfx g) {
        ClassDef c = hero();
        Sheet sh = Cosmetics.sheetFor(c);
        if (sh == null || sh == Sheet.EMPTY) return;
        String an = heroMoving && sh.has("run") ? "run" : "idle";
        int tint = Cosmetics.tintFor(c);
        float hx = Math.round(heroX - cam);
        float hy = FLOOR + 4;
        UI.light(g, hx, FLOOR + 2, 14, 0x000000, 0.25f);
        sh.drawAt(g, an, t, hx, hy, heroRight, 1f, tint != 0 ? Platform.TINT : 0, tint, 1f);
    }

    private void outline(Platform.Gfx g, Hit h) {
        float a = 0.55f + 0.35f * (float) Math.sin(pulse * 8);
        int c = Mth.withAlpha(0xFFD25A, (int) (a * 255));
        float x0 = h.x, y0 = h.y + 2, x1 = h.x + h.w, y1 = h.y + h.h - 16, L = 8;
        g.rect(x0, y0, L, 1, c, false); g.rect(x0, y0, 1, L, c, false);
        g.rect(x1 - L, y0, L, 1, c, false); g.rect(x1 - 1, y0, 1, L, c, false);
        g.rect(x0, y1, L, 1, c, false); g.rect(x0, y1 - L, 1, L, c, false);
        g.rect(x1 - L, y1, L, 1, c, false); g.rect(x1 - 1, y1 - L, 1, L, c, false);
    }

    /** Sala de trofeos: nueve nichos (8 jefes y el Cazador). Cada victoria deja una estatua de piedra con su propio brillo. */
    private void drawTrophyWall(Platform.Gfx g, float x, float fy, float a, boolean sel) {
        spr(g, "ops_trophy_wall", "idle", x, fy, 1f, a, 0, 0);
        float left = x - 168, top = fy - 99;
        for (int i = 0; i < 9; i++) {
            boolean got = i < 8 ? Save.S.relics[i] : Save.S.finalBeaten;
            BossDef bd = BossDef.ALL[i];
            float nx = left + 8 + i * 36 + 15, feet = top + 79;
            Sheet sh = Assets.sheet(bd.sheet);
            if (sh == null || sh == Sheet.EMPTY) continue;
            if (got) {
                float gl = 0.18f + 0.08f * (float) Math.sin(t * 2f + i) + (sel ? 0.12f : 0f) + trophyGlow * 0.25f;
                UI.light(g, nx, feet - 26, 26 + (sel ? 4 : 0), bd.color | 0xFF000000, gl * a);
                sh.drawAt(g, "idle", 0f, nx, feet, true, 0.4f, Platform.TINT, 0xA8A4C0, a);
                g.rect(nx - 10, feet + 1, 20, 1, Mth.withAlpha(bd.color, (int) (150 * a)), true);
            } else {
                int rc = Mth.withAlpha(0x6A5A9A, (int) (120 * a * (0.6f + 0.4f * (float) Math.sin(t * 1.5f + i))));
                g.rect(nx - 1, feet - 30, 2, 6, rc, false); g.rect(nx - 3, feet - 28, 6, 2, rc, false);
            }
        }
    }

    private void drawDoor(Platform.Gfx g, float x, float fy, float a, boolean sel, boolean dis) {
        Sheet sh = Assets.spr("prop_door");
        if (sh != null && sh != Sheet.EMPTY) sh.drawAt(g, (sel && !dis) ? "open_idle" : "closed", t, x, fy, true, 1.25f, dis ? Platform.TINT : 0, dis ? 0x303040 : 0, a);
        if (!dis) UI.light(g, x, fy - 30, sel ? 40 : 26, 0xFFC070, 0.25f * a);
        UI.iconC(g, dis ? "lock" : "door", x, fy - 70, 1f, a);
    }

    private void drawPortal(Platform.Gfx g, float x, float a, boolean sel) {
        Sheet sh = Assets.spr("prop_portal");
        float py = 192;
        float pr = 0.5f + 0.5f * (float) Math.sin(pulse * 2.4f);
        UI.light(g, x, py - 40, 80 + 10 * pr, 0xFF3A20, (0.30f + (sel ? 0.18f : 0.08f)) * a);
        for (int k = 0; k < 14; k++) {
            float an = k / 14f * 6.2832f + pulse * 0.6f;
            g.rect(x + (float) Math.cos(an) * 34 - 1, py + 2 + (float) Math.sin(an) * 7 - 1, 2, 2, Mth.withAlpha(0xFFB070, (int) (200 * a * (0.5f + 0.5f * (float) Math.sin(an * 2 + pulse * 3)))), true);
        }
        if (sh != null && sh != Sheet.EMPTY) sh.drawAt(g, "idle", t, x, py, true, 1.6f, 0, 0, a);
        float by = py - 118 + (float) Math.sin(pulse * 4) * 3;
        if (UI.arrow != null) g.imageRot(UI.arrow, 0, 0, 8, 8, x - 6, by, 12, 12, 1.5708f, 0, 0, a);
    }

    private void drawShop(Platform.Gfx g, float x, float fy, float a, boolean sel) {
        spr(g, "prop_merchant", "idle", x - 4, fy - 30, 1.5f, a, 0, 0);
        spr(g, "ops_stall", "idle", x, fy + (sel ? -1 : 0), 1f, a, 0, 0);
        UI.light(g, x, fy - 56, sel ? 50 : 36, 0xFFA040, (0.2f + 0.04f * (float) Math.sin(t * 8)) * a);
        UI.light(g, x + 45, fy - 44, 16, 0xB070FF, 0.25f * a);
    }

    private void drawGarden(Platform.Gfx g, float x, float fy, float a, boolean sel) {
        spr(g, "ops_garden", "idle", x, fy, 1f, a, 0, 0);
        for (int p = 0; p < 3; p++) {
            float px = x - 43 + p * 43;
            Sheet sh = Assets.spr("ops_crystal");
            if (sh != null && sh != Sheet.EMPTY) sh.drawAt(g, "stage" + gardenStage(p), t + p * 0.3f, Math.round(px), Math.round(fy - 64 + 31), true, 1f, 0, 0, a);
            UI.light(g, px, fy - 48, sel ? 26 : 18, 0x7AFFC0, 0.12f * a);
        }
    }

    /** Etapa visible (0..4) de cada cristal del jardin. Hasta la etapa 4 del proyecto el jardin aun no tiene datos guardados. */
    static int gardenStage(int plot) { return Save.S == null || plot < 0 || plot >= Garden.PLOTS ? 0 : Garden.level(Save.S, plot); }
}
