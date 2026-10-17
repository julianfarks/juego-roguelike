package com.julianfarks.roguelike.core;

/**
 * Centro de operaciones: sala de piedra con arcos, antorchas y ventanales donde cada objeto es un acceso real.
 * Sustituye al antiguo menu de portales. La arquitectura se hornea con el mismo atlas de baldosas que las mazmorras (Room.bake).
 */
final class Ops extends Screen {
    static boolean active;
    private static final int GALLERY = 0, STATS = 1, START = 2, CONTINUE = 3, TROPHY = 4, SANCT = 5, SPOTS = 6;
    private static final int FLOOR = 224;   // y del suelo

    private final Platform.Img[] bgl = new Platform.Img[3];
    private Platform.Img baked;
    private Room hall;
    private final Particles ps = new Particles();
    private final Rng rng = new Rng(5);
    private final float[] spotX = new float[SPOTS], spotW = new float[SPOTS], spotTop = new float[SPOTS];
    private final String[] spotName = {"Galería", "Estadísticas", "NUEVA PARTIDA", "Continuar", "Trofeos", "Santuario"};
    private final float[] appear = new float[SPOTS];
    private final Hit[] spotHit = new Hit[SPOTS];
    private int cur = START;           // seleccion (teclado/mando)
    private int row = 0;               // 0 objetos, 1 botones
    private int extraSel = 0;
    private float pulse;
    private float enterT;
    private float flash;
    private Hit diffBtn, backBtn, infBtn;
    private final java.util.List<Hit> extras = new java.util.ArrayList<>();
    private String toast = ""; private float toastT;

    Ops(Game g) {
        super(g);
        for (int i = 0; i < 3; i++) bgl[i] = Assets.img("bg/bg_eclipse_" + i + ".png");
        buildHall();
    }

    Ops(Game g, String toastMsg) { this(g); toast = toastMsg; toastT = 3f; }

    private void buildHall() {
        Room r = new Room(40, 17, Room.HUB, Biome.ALL[7]);
        for (int x = 0; x < 40; x++) for (int y = 0; y < 17; y++) {
            boolean solid = y >= 14 || y < 2 || x < 1 || x >= 39;
            if (solid) r.set(x, y, Room.SOLID);
        }
        int[] ribs = {10, 20, 30};            // nervaduras de la boveda
        for (int k : ribs) {
            for (int x = k - 3; x <= k + 3; x++) r.set(x, 2, Room.SOLID);
            for (int x = k - 2; x <= k + 2; x++) r.set(x, 3, Room.SOLID);
            for (int x = k - 1; x <= k + 1; x++) r.set(x, 4, Room.SOLID);
            r.set(k, 5, Room.SOLID);
        }
        // pilastras que enmarcan las crujias
        for (int k : new int[]{5, 15, 25, 35}) for (int y = 5; y < 14; y++) { if (k == 15 || k == 25) { r.set(k, y, Room.SOLID); } }
        // dais central
        for (int x = 17; x <= 22; x++) r.set(x, 13, Room.SOLID);
        for (int x = 18; x <= 21; x++) r.set(x, 12, Room.SOLID);
        // ventanales hacia el cielo
        for (int y = 5; y <= 10; y++) for (int x : new int[]{3, 4, 7, 8, 31, 32, 35, 36}) r.vista[y * 40 + x] = true;
        // estandartes y antorchas
        for (int x : new int[]{12, 18, 21, 27}) r.deco[3 * 40 + x] = (short) ((2 << 8) | (x & 7));
        for (int x : new int[]{2, 13, 27, 37}) r.deco[7 * 40 + x] = (short) ((5 << 8) | (x & 3));
        for (int x : new int[]{6, 9, 12, 28, 31, 34}) r.deco[3 * 40 + x] = (short) ((3 << 8) | (x & 7));
        hall = r;
        r.bake(game.P);
        baked = r.baked;
    }

    @Override void enter() {
        active = true;
        Snd.music("mus_sanctuary", true);
        Snd.ambient(null, 0);
        enterT = 0;
        layout();
    }

    @Override void layout() {
        hits.clear(); extras.clear();
        int w = W();
        float cx = w / 2f;
        float[] rel = {-192, -110, 0, 88, 148, 206};
        float[] ww = {50, 46, 90, 44, 48, 44};
        float[] top = {FLOOR - 84, FLOOR - 66, FLOOR - 112, FLOOR - 70, FLOOR - 62, FLOOR - 70};
        for (int i = 0; i < SPOTS; i++) {
            spotX[i] = cx + rel[i]; spotW[i] = ww[i]; spotTop[i] = top[i];
            final int id = i;
            float hw = Math.max(ww[i], 46);
            Hit h = add(spotX[i] - hw / 2f, top[i], hw, FLOOR + 22 - top[i], null, () -> activate(id));
            h.plain = true; h.noSound = true;
            h.disabled = (i == CONTINUE && !RunSave.any(game.P));
            spotHit[i] = h;
        }
        backBtn = add(6, 242, 58, 22, "Volver", () -> back());
        extras.add(backBtn);
        Hit shopBtn = add(70, 242, 58, 22, "Tienda", () -> game.go(new ShopScreen(game)));
        extras.add(shopBtn);
        infBtn = add(134, 242, 84, 22, "Infinito", this::startInfinite);
        extras.add(infBtn);
        diffBtn = add(w - 126, 242, 120, 22, diffLabel(), () -> { Save.S.diffSel = (Save.S.diffSel + 1) % 3; Save.S.write(); diffBtn.label = diffLabel(); });
        extras.add(diffBtn);
        float bx = w - 6;
        String[] nm = {"Opciones", "Códigos", "Historia"};
        Runnable[] ac = {() -> game.go(new Screens.Options(game, false)), () -> game.go(new CodesScreen(game)), () -> game.go(new StoryScreens.Historia(game, false))};
        for (int i = 0; i < 3; i++) { bx -= 62; Hit h = add(bx, 5, 58, 22, nm[i], ac[i]); extras.add(h); bx -= 0; }
        if (Save.S.devUnlocked) extras.add(add(6, 5, 90, 22, "Desarrollador", () -> game.go(new DevScreens.Menu(game))));
    }

    private String diffLabel() { int d = Save.S.diffSel; return "Dificultad: " + (d == 0 ? "Fácil" : (d == 2 ? "Difícil" : "Normal")); }

    ClassDef hero() { int id = Save.S.lastClass; if (id < 0 || id > 9 || !Save.S.classUnlocked[id]) id = 0; return ClassDef.ALL[id]; }

    private void activate(int id) {
        flash = 0.25f;
        Snd.sfx(id == START ? "ui_start_run" : "ui_click", 0.9f);
        switch (id) {
            case GALLERY: game.go(new ClassScreen(game)); break;
            case STATS: game.go(new OpsScreens.Stats(game)); break;
            case TROPHY: game.go(new OpsScreens.Trophy(game)); break;
            case SANCT: game.go(new SanctuaryScreen(game)); break;
            case CONTINUE: if (RunSave.any(game.P)) game.go(new LoadScreen(game)); else { Snd.sfx("ui_error", 0.7f); toast = "No hay partidas guardadas"; toastT = 2f; } break;
            default: startGame();
        }
    }

    /** Nueva partida con el espadachin elegido en la galeria. */
    void startGame() {
        ClassDef c = hero();
        Save s = Save.S;
        int asc = Math.min(s.ascensionSel, s.ascension);
        s.lastClass = c.id;
        s.started++;
        s.write();
        final ClassDef cc = c; final int a = asc;
        if (Story.introSeen()) game.go(new RunScreen(game, cc, a));
        else game.go(new Cinematic(game, Story.INTRO, () -> game.go(new RunScreen(game, cc, a))));
    }

    /** Modo infinito: solo tras vencer al Cazador. Nueva run con el espadachin elegido. */
    void startInfinite() {
        if (!Save.S.finalBeaten) { Snd.sfx("ui_error", 0.7f); toast = "Modo infinito: se desbloquea al vencer al Cazador"; toastT = 3f; return; }
        ClassDef c = hero();
        Save s = Save.S;
        s.lastClass = c.id;
        s.started++;
        s.write();
        game.go(RunScreen.infinite(game, c, Math.min(s.ascensionSel, s.ascension)));
    }

    @Override boolean back() { game.go(new Screens.Title(game)); return true; }

    @Override void key(int code, boolean down) {
        if (!down) return;
        game.keyboardUsed = true;
        if (code == 27) { back(); return; }
        if (code == 10 || code == 32 || code == 'J') {
            if (row == 0) { if (!spotHit[cur].disabled) activate(cur); else { Snd.sfx("ui_error", 0.7f); } }
            else click(extras.get(Math.min(extraSel, extras.size() - 1)));
            return;
        }
        boolean left = code == 37 || code == 'A', right = code == 39 || code == 'D', up = code == 38 || code == 'W', dn = code == 40 || code == 'S';
        if (row == 0) {
            if (left) { cur = (cur + SPOTS - 1) % SPOTS; Snd.sfx("ui_hover", 0.5f); }
            else if (right) { cur = (cur + 1) % SPOTS; Snd.sfx("ui_hover", 0.5f); }
            else if (up || dn) { row = 1; extraSel = 0; Snd.sfx("ui_hover", 0.5f); }
        } else {
            int n = extras.size();
            if (left) { extraSel = (extraSel + n - 1) % n; Snd.sfx("ui_hover", 0.5f); }
            else if (right) { extraSel = (extraSel + 1) % n; Snd.sfx("ui_hover", 0.5f); }
            else if (up || dn) { row = 0; Snd.sfx("ui_hover", 0.5f); }
        }
    }

    @Override void touch(int id, int action, float x, float y) {
        if (action == Platform.ACTION_DOWN) game.keyboardUsed = false;
        super.touch(id, action, x, y);
    }

    @Override void update(float dt) {
        t += dt; pulse += dt; enterT += dt;
        if (flash > 0) flash -= dt;
        if (toastT > 0) toastT -= dt;
        int w = W();
        for (int i = 0; i < SPOTS; i++) appear[i] = Mth.clamp((enterT - 0.25f - i * 0.12f) / 0.6f, 0, 1);
        // polvo en suspension y brasas de las antorchas
        if (rng.chance(dt * 10)) ps.spawn(rng.f(0, w), rng.f(40, 200), rng.f(2, 9), rng.f(-3, 3), rng.f(4, 8), 1, 0, 0xFFE8B0, true);
        float ox = (w - 640) / 2f;
        for (int[] d : hall.animated()) if (d[2] == 5 && rng.chance(dt * 5)) ps.spawn(ox + d[0] + 8, d[1] + 4, rng.f(-4, 4), -rng.f(8, 22), rng.f(0.6f, 1.4f), 1, 0, 0xFF9A40, true);
        ps.spawn(spotX[START] + rng.f(-14, 14), FLOOR - 24, rng.f(-6, 6), -rng.f(14, 40), rng.f(0.8f, 1.8f), 1, 0, rng.chance(0.5f) ? 0xFFB070 : 0xFF5A30, true);
        ps.update(dt);
    }

    private boolean selected(int i) { return row == 0 && cur == i && (game.keyboardUsed || down != null && down == spotHit[i]); }

    @Override void render(Platform.Gfx g) {
        int w = W();
        float k = Mth.clamp(enterT / 0.8f, 0, 1);
        // cielo y paisaje a traves de los ventanales
        g.clear(0xFF080408);
        float[] fac = {3f, 6f, 11f};
        for (int i = 0; i < 3; i++) {
            Platform.Img im = bgl[i];
            if (im == null) continue;
            float sc = Math.max(1f, Platform.VIEW_H / (float) im.h);
            float dw = im.w * sc, dh = im.h * sc;
            float off = (t * fac[i]) % dw;
            for (float x = -off; x < w; x += dw) g.image(im, 0, 0, im.w, im.h, Math.round(x), Math.round(Platform.VIEW_H - dh), Math.round(dw), Math.round(dh), 0, 0, 1f);
        }
        float ox = (w - 640) / 2f;
        if (baked != null) g.image(baked, 0, 0, baked.w, baked.h, Math.round(ox), 0, baked.w, baked.h, 0, 0, 1f);
        // sombra del suelo
        g.rect(0, FLOOR, w, 6, 0x40000000, false);
        // luces de antorcha
        float fl = 0.85f + 0.15f * (float) Math.sin(t * 11);
        for (int[] d : hall.animated()) {
            UI.light(g, ox + d[0] + 8, d[1] + 8, d[2] == 5 ? 64 : 44, 0xFFC070, 0.30f * fl);
            if (d[2] == 5) {   // llama animada (misma hoja de baldosas)
                Platform.Img ts = Assets.img("tiles/tiles_eclipse.png");
                if (ts != null) g.image(ts, (((d[3] + (int) (t * 8)) & 3)) * 16, 4 * 16, 16, 16, Math.round(ox + d[0]), d[1], 16, 16, 0, 0, 1f);
            }
        }
        drawSpots(g, w);
        ps.render(g, 0, 0);
        UI.light(g, spotX[START], FLOOR - 50, 100, 0xFF5A30, 0.12f + 0.05f * (float) Math.sin(pulse * 2));
        g.rect(0, 0, w, Platform.VIEW_H, Mth.withAlpha(0x120408, 40), false);
        if (UI.vignette != null) g.image(UI.vignette, 0, 0, UI.vignette.w, UI.vignette.h, 0, 0, w, Platform.VIEW_H, 0, 0, 0.7f);
        drawButtons(g);
        if (!Save.S.finalBeaten && infBtn != null) UI.icon(g, "lock", infBtn.x + infBtn.w - 15, infBtn.y + 3, 1f);
        // ficha: recursos
        UI.iconC(g, "soul", 14, Save.S.devUnlocked ? 40 : 16, 1f, 1f);
        UI.small.draw(g, String.valueOf(Save.S.souls), 26, Save.S.devUnlocked ? 35 : 11, UI.SOUL, 1f);
        UI.iconC(g, "gem", 14 + 112, Save.S.devUnlocked ? 40 : 16, 1f, 1f);
        UI.small.draw(g, String.valueOf(Wallet.gems()), 26 + 112, Save.S.devUnlocked ? 35 : 11, UI.PURPLE, 1f);
        UI.iconC(g, "relic", 14 + 56, Save.S.devUnlocked ? 40 : 16, 1f, 1f);
        UI.small.draw(g, Save.S.relicCount() + "/8", 26 + 56, Save.S.devUnlocked ? 35 : 11, UI.GOLD, 1f);
        // tooltip del objeto seleccionado
        if (row == 0 && (game.keyboardUsed || down != null)) tooltip(g, w, cur);
        else tooltip(g, w, START);
        // marcador de seleccion con teclado/mando en los botones
        if (row == 1 && game.keyboardUsed) {
            Hit h = extras.get(Math.min(extraSel, extras.size() - 1));
            float a = 0.6f + 0.4f * (float) Math.sin(pulse * 8);
            g.rect(h.x - 2, h.y - 2, h.w + 4, 1, Mth.withAlpha(0xFFD25A, (int) (a * 255)), false);
            g.rect(h.x - 2, h.y + h.h + 1, h.w + 4, 1, Mth.withAlpha(0xFFD25A, (int) (a * 255)), false);
            g.rect(h.x - 2, h.y - 2, 1, h.h + 4, Mth.withAlpha(0xFFD25A, (int) (a * 255)), false);
            g.rect(h.x + h.w + 1, h.y - 2, 1, h.h + 4, Mth.withAlpha(0xFFD25A, (int) (a * 255)), false);
        }
        UI.small.center(g, game.keyboardUsed ? "Flechas · Enter · Esc" : "Toca un lugar", (214 + w - 130) / 2f, 252, UI.GREY, 0.7f);
        if (toastT > 0) { UI.panel(g, 0, w / 2f - 160, 72, 320, 18, 0.95f); UI.small.center(g, toast, w / 2f, 76, UI.GOLD, Mth.clamp(toastT, 0, 1)); }
        // fundido de entrada
        if (k < 1) g.rect(0, 0, w, Platform.VIEW_H, Mth.withAlpha(0x000000, (int) ((1 - k) * 255)), false);
        if (flash > 0) g.rect(0, 0, w, Platform.VIEW_H, Mth.withAlpha(0xFFE8C0, (int) (Mth.clamp(flash * 4, 0, 1) * 70)), true);
    }

    private void tooltip(Platform.Gfx g, int w, int i) {
        String title, sub;
        ClassDef c = hero();
        switch (i) {
            case GALLERY: title = "Galería de espadachines"; sub = "Elige quién desciende contigo. Ahora: " + c.name; break;
            case STATS: title = "Estadísticas"; sub = "Tu historial real: partidas, rondas, jefes y tiempo"; break;
            case START: title = "Nueva partida"; sub = "Desciende al Abismo como " + c.name; break;
            case CONTINUE: title = "Continuar"; sub = RunSave.any(game.P) ? "Retoma una partida guardada" : "No hay partidas guardadas"; break;
            case TROPHY: title = "Trofeos"; sub = Trophies.count(Save.S) + " de " + Trophies.ALL.length + " logros desbloqueados"; break;
            default: title = "Santuario"; sub = "Mejoras permanentes, clases y desbloqueos"; break;
        }
        float tw = Math.min(w - 40, 330);
        UI.panel(g, i == START ? 1 : 0, w / 2f - tw / 2f, 34, tw, 34, 0.95f);
        UI.small.center(g, title, w / 2f, 39, i == START ? UI.GOLD : UI.WHITE, 1f);
        UI.small.center(g, sub, w / 2f, 53, UI.GREY, 1f);
    }

    // ------------------------------------------------------------------ objetos
    private void drawSpots(Platform.Gfx g, int w) {
        for (int i = 0; i < SPOTS; i++) {
            float a = appear[i];
            if (a <= 0) continue;
            boolean sel = selected(i) || (!game.keyboardUsed && down == null && i == START && false);
            float rise = (1 - a) * 16;
            float lift = sel ? -2f - (float) Math.abs(Math.sin(pulse * 5)) * 1.5f : 0;
            float x = spotX[i], fy = FLOOR + rise + lift;
            boolean dis = i == CONTINUE && spotHit[i].disabled;
            switch (i) {
                case GALLERY: drawGallery(g, x, fy, a, sel); break;
                case STATS: drawStats(g, x, fy, a, sel); break;
                case START: drawStart(g, x, fy + 0, a, sel); break;
                case CONTINUE: drawContinue(g, x, fy, a, sel, dis); break;
                case TROPHY: drawTrophy(g, x, fy, a, sel); break;
                default: drawSanctuary(g, x, fy, a, sel); break;
            }
            // placa con el nombre
            float pw = i == START ? 92 : (float) Math.max(46, UI.small.width(spotName[i]) + 12);
            float py = FLOOR + 6;
            UI.panel(g, sel || i == START ? 1 : 0, x - pw / 2f, py, pw, 14, 0.9f * a);
            UI.small.center(g, spotName[i], x, py + 3, dis ? UI.GREY : (sel || i == START ? UI.GOLD : UI.WHITE), a);
            if (sel) outline(g, spotHit[i]);
        }
    }

    private void outline(Platform.Gfx g, Hit h) {
        float a = 0.55f + 0.35f * (float) Math.sin(pulse * 8);
        int c = Mth.withAlpha(0xFFD25A, (int) (a * 255));
        float x0 = h.x, y0 = h.y + 4, x1 = h.x + h.w, y1 = h.y + h.h - 18, L = 8;
        g.rect(x0, y0, L, 1, c, false); g.rect(x0, y0, 1, L, c, false);
        g.rect(x1 - L, y0, L, 1, c, false); g.rect(x1 - 1, y0, 1, L, c, false);
        g.rect(x0, y1, L, 1, c, false); g.rect(x0, y1 - L, 1, L, c, false);
        g.rect(x1 - L, y1, L, 1, c, false); g.rect(x1 - 1, y1 - L, 1, L, c, false);
    }

    private void drawGallery(Platform.Gfx g, float x, float fy, float a, boolean sel) {
        ClassDef c = hero();
        // soporte de espadas en la pared
        for (int k = 0; k < 3; k++) {
            float sx = x - 18 + k * 18;
            g.rect(sx - 1, fy - 78, 2, 40, Mth.withAlpha(0x8A90A0, (int) (255 * a)), false);
            g.rect(sx - 4, fy - 52, 8, 2, Mth.withAlpha(0x6A4224, (int) (255 * a)), false);
            g.rect(sx - 1, fy - 40, 2, 4, Mth.withAlpha(0xFFD25A, (int) (255 * a)), false);
        }
        UI.light(g, x, fy - 34, 44, c.color1, (0.25f + (sel ? 0.2f : 0f)) * a);
        // pedestal
        g.rect(x - 22, fy - 14, 44, 14, Mth.withAlpha(0x3A3646, (int) (255 * a)), false);
        g.rect(x - 22, fy - 14, 44, 2, Mth.withAlpha(0x7A7490, (int) (255 * a)), false);
        g.rect(x - 22, fy - 2, 44, 2, Mth.withAlpha(0x1A1620, (int) (255 * a)), false);
        Sheet sh = Cosmetics.sheetFor(c);
        if (sh != null && sh != Sheet.EMPTY) {
            String an = sel ? (((int) (t * 0.7f)) % 2 == 0 ? "attack1" : "idle") : "idle";
            if (!sh.has(an)) an = "idle";
            float tt = sel ? t % 1.2f : t;
            sh.drawAt(g, an, tt, x, fy - 14, true, 1f, 0, 0, a);
        }
    }

    private void drawStats(Platform.Gfx g, float x, float fy, float a, boolean sel) {
        int al = (int) (255 * a);
        // atril de madera con libro abierto
        g.rect(x - 3, fy - 26, 6, 26, Mth.withAlpha(0x5A3A20, al), false);
        g.rect(x - 14, fy - 3, 28, 3, Mth.withAlpha(0x3A2410, al), false);
        g.rect(x - 20, fy - 34, 40, 10, Mth.withAlpha(0x6A4224, al), false);
        g.rect(x - 20, fy - 34, 40, 2, Mth.withAlpha(0x9A6A3A, al), false);
        // libro
        g.rect(x - 17, fy - 44, 16, 12, Mth.withAlpha(0xE8DCC0, al), false);
        g.rect(x + 1, fy - 44, 16, 12, Mth.withAlpha(0xD8CCB0, al), false);
        g.rect(x - 1, fy - 45, 2, 14, Mth.withAlpha(0x6A1A20, al), false);
        // barras animadas (datos reales: no son numeros de ejemplo, solo ilustran)
        for (int k = 0; k < 4; k++) {
            float hgt = 3 + 6 * (0.5f + 0.5f * (float) Math.sin(t * 1.5f + k));
            g.rect(x - 14 + k * 3, fy - 33 - hgt, 2, hgt, Mth.withAlpha(0x7A3A20, al), false);
        }
        for (int k = 0; k < 5; k++) g.rect(x + 3, fy - 43 + k * 2, 11, 1, Mth.withAlpha(0x6A5A40, al), false);
        UI.light(g, x, fy - 46, (sel ? 38 : 28), 0xFFE0A0, (0.20f + 0.06f * (float) Math.sin(t * 3)) * a);
    }

    private void drawStart(Platform.Gfx g, float x, float fy, float a, boolean sel) {
        Sheet sh = Assets.spr("prop_portal");
        float py = 192 + (1 - a) * 16;        // sobre el dais
        // aro de runas
        float pr = 0.5f + 0.5f * (float) Math.sin(pulse * 2.4f);
        UI.light(g, x, py - 40, 80 + 10 * pr, 0xFF3A20, (0.30f + (sel ? 0.18f : 0.08f)) * a);
        for (int k = 0; k < 14; k++) {
            float an = k / 14f * 6.2832f + pulse * 0.6f;
            g.rect(x + (float) Math.cos(an) * 34 - 1, py + 2 + (float) Math.sin(an) * 7 - 1, 2, 2, Mth.withAlpha(0xFFB070, (int) (200 * a * (0.5f + 0.5f * (float) Math.sin(an * 2 + pulse * 3)))), true);
        }
        if (sh != null && sh != Sheet.EMPTY) sh.drawAt(g, "idle", t, x, py, true, 1.6f, 0, 0, a);
        // flecha que invita a entrar
        float by = py - 118 + (float) Math.sin(pulse * 4) * 3;
        if (UI.arrow != null) g.imageRot(UI.arrow, 0, 0, 8, 8, x - 6, by, 12, 12, 1.5708f, 0, 0, a);
    }

    private void drawContinue(Platform.Gfx g, float x, float fy, float a, boolean sel, boolean dis) {
        Sheet sh = Assets.spr("prop_door");
        if (sh != null && sh != Sheet.EMPTY) {
            String an = (sel && !dis) ? "open_idle" : "closed";
            sh.drawAt(g, an, t, x, fy, true, 1.25f, dis ? Platform.TINT : 0, dis ? 0x303040 : 0, a);
        }
        if (!dis) UI.light(g, x, fy - 30, sel ? 40 : 26, 0xFFC070, 0.25f * a);
        UI.iconC(g, dis ? "lock" : "door", x, fy - 70, 1f, a);
    }

    private void drawTrophy(Platform.Gfx g, float x, float fy, float a, boolean sel) {
        int al = (int) (255 * a);
        int n = Trophies.count(Save.S);
        // estanteria de piedra con copas
        g.rect(x - 22, fy - 52, 44, 52, Mth.withAlpha(0x2A2634, al), false);
        g.rect(x - 22, fy - 52, 44, 2, Mth.withAlpha(0x6A6480, al), false);
        for (int row2 = 0; row2 < 3; row2++) {
            float sy = fy - 36 + row2 * 17;
            g.rect(x - 20, sy + 2, 40, 2, Mth.withAlpha(0x5A3A20, al), false);
            for (int c = 0; c < 3; c++) {
                int idx = (2 - row2) * 3 + c;
                boolean lit = idx < Math.round(n * 9f / Trophies.ALL.length);
                float cxp = x - 12 + c * 12;
                int col = lit ? 0xFFD25A : 0x4A4658;
                g.rect(cxp - 3, sy - 7, 6, 5, Mth.withAlpha(col, al), false);
                g.rect(cxp - 1, sy - 2, 2, 3, Mth.withAlpha(col, al), false);
                g.rect(cxp - 3, sy, 6, 1, Mth.withAlpha(col, al), false);
                if (lit) g.rect(cxp - 2, sy - 6, 1, 3, Mth.withAlpha(0xFFFFFF, (int) (200 * a)), false);
            }
        }
        if (n > 0) UI.light(g, x, fy - 30, sel ? 40 : 28, 0xFFD25A, (0.12f + 0.05f * (float) Math.sin(t * 2.5f)) * a);
    }

    private void drawSanctuary(Platform.Gfx g, float x, float fy, float a, boolean sel) {
        Sheet sh = Assets.spr("prop_altar");
        if (sh != null && sh != Sheet.EMPTY) sh.drawAt(g, "idle", t, x, fy, true, 1.25f, 0, 0, a);
        UI.light(g, x, fy - 40, sel ? 46 : 32, 0x9A7AFF, 0.22f * a);
    }
}
