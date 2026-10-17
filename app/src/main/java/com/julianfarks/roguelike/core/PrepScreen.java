package com.julianfarks.roguelike.core;

/**
 * Preparacion de expedicion: paso obligatorio entre el portal del centro de operaciones y la run.
 * Permite elegir espadachin (solo desbloqueados), revisar estadisticas/habilidades/arma, elegir una de tres bendiciones
 * iniciales, el modo y la dificultad. «COMENZAR EXPEDICION» lanza una transicion animada y despues la run.
 */
final class PrepScreen extends Screen {
    // opciones ofrecidas: se mantienen hasta que empieza una expedicion (salir y volver no permite re-tirar)
    private static int[] offered;
    private final int[] mine;           // copia local: la pantalla sigue mostrandose mientras dura la transicion
    private static int chosen = 0;
    static boolean infiniteMode;

    private final Platform.Img[] bgl = new Platform.Img[3];
    private Platform.Img baked;
    private final Particles ps = new Particles();
    private final Rng rng = new Rng(11);
    private int selS;
    private Hit leftHit, rightHit, startBtn, modeBtn, diffBtn;
    private final Hit[] cardHit = new Hit[3], skillHit = new Hit[4];
    private float launchT = -1;
    private float enterT;
    private String toast = ""; private float toastT;
    private float swapT = 1f;       // animacion al cambiar de espadachin

    PrepScreen(Game g) {
        super(g);
        for (int i = 0; i < 3; i++) bgl[i] = Assets.img("bg/bg_eclipse_" + i + ".png");
        Room r = new Room(40, 17, Room.HUB, Biome.ALL[7]);
        for (int x = 0; x < 40; x++) for (int y = 0; y < 17; y++) if (y >= 14 || y < 2 || x < 1 || x >= 39) r.set(x, y, Room.SOLID);
        for (int k : new int[]{6, 20, 34}) { for (int x = k - 3; x <= k + 3; x++) r.set(x, 2, Room.SOLID); for (int x = k - 2; x <= k + 2; x++) r.set(x, 3, Room.SOLID); for (int x = k - 1; x <= k + 1; x++) r.set(x, 4, Room.SOLID); r.set(k, 5, Room.SOLID); }
        for (int y = 5; y <= 10; y++) for (int x : new int[]{12, 13, 14, 26, 27, 28}) r.vista[y * 40 + x] = true;
        for (int x : new int[]{4, 18, 22, 36}) r.deco[7 * 40 + x] = (short) ((5 << 8) | (x & 3));
        for (int x : new int[]{9, 17, 23, 31}) r.deco[3 * 40 + x] = (short) ((2 << 8) | (x & 7));
        r.bake(g.P);
        baked = r.baked;
        if (offered == null) offered = StartBlessing.roll(new Rng(System.nanoTime() ^ 0x9E3779B97F4A7C15L));
        mine = offered;
        if (chosen < 0 || chosen > 2) chosen = 0;
        if (infiniteMode && !Save.S.finalBeaten) infiniteMode = false;
    }

    ClassDef cls() { int id = Save.S.lastClass; if (id < 0 || id > 9 || !Save.S.classUnlocked[id]) id = 0; return ClassDef.ALL[id]; }

    @Override void enter() { Snd.music("mus_sanctuary", true); enterT = 0; layout(); }

    @Override void layout() {
        hits.clear();
        int w = W();
        leftHit = add(4, 104, 26, 44, null, () -> swap(-1)); leftHit.plain = true; leftHit.noSound = true;
        rightHit = add(124, 104, 26, 44, null, () -> swap(1)); rightHit.plain = true; rightHit.noSound = true;
        float x0 = 156, wR = w - 162;
        for (int i = 0; i < 4; i++) { final int id = i; skillHit[i] = add(x0 + i * 30, 88, 26, 26, null, () -> selS = id); skillHit[i].plain = true; }
        float cw = (wR - 8) / 3f;
        for (int i = 0; i < 3; i++) { final int id = i; cardHit[i] = add(x0 + i * (cw + 4), 148, cw, 56, null, () -> pick(id)); cardHit[i].plain = true; cardHit[i].noSound = true; }
        Hit cmpHit = add(156, 227, w - 162, 14, null, () -> cycleCompanion()); cmpHit.plain = true;
        add(6, 242, 44, 26, "Volver", () -> back());
        modeBtn = add(54, 242, 112, 26, modeLabel(), () -> toggleMode());
        Hit retos = add(226, 242, 74, 26, retosLabel(), () -> { if (infiniteMode && Save.S.finalBeaten) game.go(new CodexScreens.Challenges(game)); else { Snd.sfx("ui_error", 0.7f); say("Los retos son del modo Infinito"); } });
        retos.noSound = false;
        diffBtn = add(170, 242, 52, 26, diffLabel(), () -> { Save.S.diffSel = (Save.S.diffSel + 1) % 3; Save.S.write(); diffBtn.label = diffLabel(); });
        startBtn = add(w - 176, 239, 170, 30, "COMENZAR EXPEDICIÓN", () -> launch());
    }

    private String retosLabel() { int n = Integer.bitCount(Save.S.infMods); return n > 0 && infiniteMode ? "Retos " + n : "Retos"; }
    private String modeLabel() { return infiniteMode ? "Modo: Infinito" : "Modo: Campaña"; }
    private String diffLabel() { int d = Save.S.diffSel; return d == 0 ? "Fácil" : (d == 2 ? "Difícil" : "Normal"); }

    private void toggleMode() {
        if (!Save.S.finalBeaten) { Snd.sfx("ui_error", 0.7f); say("Infinito: se desbloquea al vencer al Cazador"); return; }
        infiniteMode = !infiniteMode; modeBtn.label = modeLabel(); layout(); Snd.sfx("ui_click", 0.8f);
    }

    private void say(String s) { toast = s; toastT = 2.5f; }

    /** Cambia al siguiente/anterior espadachin DESBLOQUEADO (los bloqueados se saltan: no se pueden elegir). */
    private void swap(int d) {
        if (launchT >= 0) return;
        int id = nextUnlocked(cls().id, d, Save.S.classUnlocked);
        if (id != Save.S.lastClass) { Save.S.lastClass = id; Save.S.write(); selS = 0; swapT = 0; Snd.sfx("ui_hover", 0.7f); }
    }

    /** Siguiente espadachin desbloqueado en la direccion d (nunca devuelve uno bloqueado; si no hay otro, el mismo). */
    static int nextUnlocked(int cur, int d, boolean[] unlocked) {
        int id = cur;
        for (int k = 0; k < 10; k++) {
            id = (id + d + 10) % 10;
            if (unlocked[id]) return id;
        }
        return cur;
    }

    private void pick(int i) {
        if (launchT >= 0) return;
        chosen = chosen == i ? -1 : i;   // tocar la elegida la quita (sin bendicion)
        Snd.sfx("ui_click", 0.8f);
    }

    /** Bendicion inicial elegida (-1 = ninguna). */
    static int chosenBlessing() { return chosen >= 0 && offered != null && chosen < offered.length ? offered[chosen] : -1; }
    private int shown() { return chosen >= 0 && chosen < mine.length ? mine[chosen] : -1; }

    private void launch() {
        if (launchT >= 0) return;
        launchT = 0;
        Snd.sfx("ui_start_run", 1f);
    }

    @Override boolean back() { if (launchT >= 0) return true; game.go(new Ops(game)); return true; }

    @Override void key(int code, boolean down) {
        if (!down || launchT >= 0) return;
        game.keyboardUsed = true;
        if (code == 27) { back(); return; }
        if (code == 10 || code == 32) { launch(); return; }
        if (code == 37 || code == 'A') swap(-1);
        else if (code == 39 || code == 'D') swap(1);
        else if (code >= '1' && code <= '3') pick(code - '1');
        else if (code == 'M') toggleMode();
    }

    @Override void touch(int id, int action, float x, float y) {
        if (action == Platform.ACTION_DOWN) game.keyboardUsed = false;
        if (launchT >= 0) return;
        super.touch(id, action, x, y);
    }

    /** Solo banco de pruebas automatico: confirma la preparacion como lo haria el boton. */
    void botStart() { launch(); }

    /** Crea la run con las selecciones y entra al mundo. Unico camino jugable del portal. */
    private void begin() {
        ClassDef c = cls();
        Save s = Save.S;
        s.lastClass = c.id;
        s.started++;
        s.write();
        final int asc = Math.min(s.ascensionSel, s.ascension);
        final int bl = chosenBlessing();
        offered = null; chosen = 0;
        final boolean inf = infiniteMode && s.finalBeaten;
        final RunScreen r = inf ? RunScreen.infinite(game, c, asc) : new RunScreen(game, c, asc);
        r.rs.applyStartBlessing(bl);
        if (inf) r.rs.mods = Infinite.validMods(r.rs, s.infMods);
        if (!inf && !Story.introSeen()) game.go(new Cinematic(game, Story.INTRO, () -> game.go(r)));
        else game.go(r);
    }

    @Override void update(float dt) {
        t += dt; enterT += dt;
        if (swapT < 1) swapT = Math.min(1, swapT + dt * 4);
        if (toastT > 0) toastT -= dt;
        if (rng.chance(dt * 10)) ps.spawn(rng.f(0, W()), rng.f(40, 200), rng.f(2, 9), rng.f(-3, 3), rng.f(4, 8), 1, 0, 0xFFE8B0, true);
        ps.spawn(78 + rng.f(-14, 14), 170, rng.f(-6, 6), -rng.f(14, 40), rng.f(0.8f, 1.8f), 1, 0, rng.chance(0.5f) ? 0xFFB070 : 0xFF5A30, true);
        ps.update(dt);
        if (launchT >= 0) {
            launchT += dt;
            for (int i = 0; i < 3; i++) ps.spawn(78 + rng.f(-20, 20), 150 + rng.f(-30, 30), rng.f(-40, 40), rng.f(-60, 10), rng.f(0.5f, 1f), 2, 0, 0xFFC890, true);
            if (launchT > 1.7f) { launchT = -2; begin(); }
        }
    }

    @Override void render(Platform.Gfx g) {
        int w = W();
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
        if (baked != null) g.image(baked, 0, 0, baked.w, baked.h, Math.round((w - 640) / 2f), 0, baked.w, baked.h, 0, 0, 1f);
        g.rect(0, 0, w, Platform.VIEW_H, Mth.withAlpha(0x0A0408, 150), false);
        ClassDef c = cls();
        drawShowcase(g, c);
        drawInfo(g, c, w);
        drawCards(g, w);
        drawSummary(g, c, w);
        ps.render(g, 0, 0);
        if (UI.vignette != null) g.image(UI.vignette, 0, 0, UI.vignette.w, UI.vignette.h, 0, 0, w, Platform.VIEW_H, 0, 0, 0.6f);
        UI.big.center(g, "PREPARACIÓN", (156 + w) / 2f, 4, UI.GOLD, 1f);
        drawButtons(g);
        if (!Save.S.finalBeaten && modeBtn != null) UI.icon(g, "lock", modeBtn.x + modeBtn.w - 15, modeBtn.y + 5, 1f);
        if (startBtn != null && launchT < 0) {          // brillo pulsante del boton principal
            float a = 0.35f + 0.25f * (float) Math.sin(t * 5);
            int col = Mth.withAlpha(0xFFD25A, (int) (a * 255));
            g.rect(startBtn.x - 1, startBtn.y - 1, startBtn.w + 2, 1, col, false); g.rect(startBtn.x - 1, startBtn.y + startBtn.h, startBtn.w + 2, 1, col, false);
            g.rect(startBtn.x - 1, startBtn.y - 1, 1, startBtn.h + 2, col, false); g.rect(startBtn.x + startBtn.w, startBtn.y - 1, 1, startBtn.h + 2, col, false);
        }
        if (toastT > 0) { UI.panel(g, 0, w / 2f - 160, 120, 320, 18, 0.95f); UI.small.center(g, toast, w / 2f, 124, UI.GOLD, Mth.clamp(toastT, 0, 1)); }
        float fin = Mth.clamp(enterT / 0.5f, 0, 1);
        if (fin < 1) g.rect(0, 0, w, Platform.VIEW_H, Mth.withAlpha(0x000000, (int) ((1 - fin) * 255)), false);
        if (launchT >= 0) drawLaunch(g, w, c);
    }

    private void drawShowcase(Platform.Gfx g, ClassDef c) {
        float cx = 78, fy = 200;
        // dais y portal
        g.rect(cx - 52, fy, 104, 6, 0xFF2A2634, false); g.rect(cx - 52, fy, 104, 2, 0xFF7A7490, false);
        UI.light(g, cx, fy - 50, 70, c.color1, 0.22f + 0.05f * (float) Math.sin(t * 2f));
        Sheet po = Assets.spr("prop_portal");
        if (po != null && po != Sheet.EMPTY) po.drawAt(g, "idle", t, cx, fy - 6, true, 1.7f, 0, 0, 0.9f);
        Sheet sh = Cosmetics.sheetFor(c);
        if (sh != null && sh != Sheet.EMPTY) {
            String an = swapT < 1 ? "attack1" : "idle";
            if (!sh.has(an)) an = "idle";
            float tt = swapT < 1 ? swapT * 0.5f : t;
            int tint = Cosmetics.tintFor(c);
            float sc = 2.1f;
            g.rect(cx - 18, fy - 1, 36, 3, 0x66000000, false);
            float a = Mth.clamp(0.4f + swapT * 0.6f, 0, 1);
            if (launchT >= 0.4f) { float k = Mth.clamp((launchT - 0.4f) / 0.7f, 0, 1); sc *= 1 - 0.8f * k; a *= 1 - k; }
            sh.drawAt(g, an, tt, cx, fy - (launchT >= 0.4f ? Mth.clamp((launchT - 0.4f) / 0.7f, 0, 1) * 50 : 0), true, sc, tint != 0 ? Platform.TINT : 0, tint, a);
        }
        UI.small.draw(g, c.name, 6, 26, c.color1, 1f);
        UI.small.drawWrapped(g, c.role, 6, 38, 144, UI.GREY, 1f);
        int unl = 0; for (boolean b : Save.S.classUnlocked) if (b) unl++;
        UI.small.center(g, unl + "/10 desbloqueados", cx, 210, UI.GREY, 1f);
        if (unl > 1 && UI.arrow != null) {
            float b = (float) Math.sin(t * 4) * 2;
            g.imageRot(UI.arrow, 0, 0, 8, 8, 8 - b, 118, 16, 16, 3.1416f, 0, 0, 0.95f);
            g.imageRot(UI.arrow, 0, 0, 8, 8, 126 + b, 118, 16, 16, 0f, 0, 0, 0.95f);
        }
    }

    private void bar(Platform.Gfx g, String n, float v, String val, float x, float y, int col, float bw) {
        UI.small.draw(g, n, x, y, UI.GREY, 1f);
        float bx = x + 52;
        g.rect(bx, y + 2, bw, 5, 0xFF1A1620, false);
        g.rect(bx, y + 2, bw * Mth.clamp(v, 0.05f, 1f), 5, 0xFF000000 | col, false);
        g.rect(bx, y + 2, bw * Mth.clamp(v, 0.05f, 1f), 1, 0x66FFFFFF, false);
        UI.small.draw(g, val, bx + bw + 4, y, UI.WHITE, 1f);
    }

    private void drawInfo(Platform.Gfx g, ClassDef c, int w) {
        float x0 = 156, wR = w - 162;
        UI.panel(g, 0, x0, 24, wR, 60, 0.92f);
        float bw = Math.min(84, wR / 2f - 60);
        bar(g, "Vida", c.hp / 140f, String.valueOf((int) c.hp), x0 + 6, 29, 0xFF5A5A, bw);
        bar(g, "Daño", c.dmg / 28f, String.valueOf((int) c.dmg), x0 + 6, 39, 0xFFB040, bw);
        bar(g, "Ataque", c.atkSpeed / 1.4f, String.format("%.2f", c.atkSpeed), x0 + 6, 49, 0x7AF0FF, bw);
        bar(g, "Velocidad", c.speed / 1.15f, String.format("%.2f", c.speed), x0 + 6, 59, 0x6AE08A, bw);
        bar(g, "Crítico", c.crit / 0.25f, Math.round(c.crit * 100) + "%", x0 + 6, 69, 0xC070FF, bw);
        float tx = x0 + 6 + 52 + bw + 34;
        float tw = x0 + wR - tx - 6;
        UI.small.drawWrapped(g, c.weapon, tx, 29, (int) tw, UI.GOLD, 1f);
        UI.small.drawWrapped(g, c.trait, tx, 51, (int) tw, UI.CYAN, 1f);
        // habilidades
        for (int i = 0; i < 4; i++) {
            Hit h = skillHit[i];
            UI.panel(g, i == selS ? 1 : 0, h.x, h.y, 26, 26, 1f);
            UI.iconC(g, c.skills[i].icon, h.x + 13, h.y + 13, 1f, 1f);
        }
        ClassDef.Skill sk = c.skills[selS];
        UI.small.draw(g, (selS == 3 ? "Definitiva: " : "") + sk.name, x0 + 124, 90, selS == 3 ? UI.ORANGE : UI.WHITE, 1f);
        UI.small.draw(g, sk.cd > 0 ? "Enfriamiento " + (int) sk.cd + "s" : "Carga con golpes", x0 + 124, 101, UI.GREY, 1f);
        UI.small.drawWrapped(g, sk.desc, x0, 117, (int) wR, 0xE8E0E0, 1f);
    }

    private void drawCards(Platform.Gfx g, int w) {
        UI.small.draw(g, "Bendición inicial · elige una", 156, 139, UI.GOLD, 1f);
        for (int i = 0; i < 3; i++) {
            Hit h = cardHit[i];
            StartBlessing b = StartBlessing.get(mine[i]);
            boolean on = chosen == i;
            float lift = on ? -2 : 0;
            UI.panel(g, on ? 1 : 0, h.x, h.y + lift, h.w, h.h, 0.96f);
            UI.iconC(g, b.icon, h.x + 14, h.y + 15 + lift, 1f, 1f);
            UI.small.drawWrapped(g, b.name, h.x + 28, h.y + 5 + lift, (int) h.w - 32, on ? UI.GOLD : UI.WHITE, 1f);
            UI.small.draw(g, "+ " + b.sp, h.x + 6, h.y + 31 + lift, 0xFF6AE08A, 1f);
            UI.small.draw(g, "- " + b.sc, h.x + 6, h.y + 42 + lift, 0xFFFF7A7A, 1f);
            if (on) {
                int c = Mth.withAlpha(0xFFD25A, (int) ((0.6f + 0.4f * (float) Math.sin(t * 6)) * 255));
                float y = h.y + lift;
                g.rect(h.x - 1, y - 1, h.w + 2, 1, c, false); g.rect(h.x - 1, y + h.h, h.w + 2, 1, c, false);
                g.rect(h.x - 1, y - 1, 1, h.h + 2, c, false); g.rect(h.x + h.w, y - 1, 1, h.h + 2, c, false);
            }
        }
    }

    /** Alterna entre ninguno y los companeros realmente desbloqueados. */
    private void cycleCompanion() {
        Companions.refresh(Save.S);
        java.util.List<Integer> opts = new java.util.ArrayList<>();
        opts.add(-1);
        for (int i = 0; i < Companions.COUNT; i++) if (Companions.unlocked(Save.S, i)) opts.add(i);
        int at = opts.indexOf(Companions.active(Save.S));
        Companions.select(Save.S, opts.get((Math.max(0, at) + 1) % opts.size()));
    }

    private void drawSummary(Platform.Gfx g, ClassDef c, int w) {
        StartBlessing b = StartBlessing.get(shown());
        Cosmetics.Item sk = Cosmetics.equipped(c);
        float x = 156, wR = w - 162;
        if (b != null) {
            float px = x;
            UI.small.draw(g, "+ " + b.pro, px, 209, 0xFF6AE08A, 1f);
            UI.small.draw(g, "- " + b.con, px + UI.small.width("+ " + b.pro) + 10, 209, 0xFFFF7A7A, 1f);
        } else UI.small.draw(g, "Sin bendición inicial", x, 209, UI.GREY, 1f);
        UI.small.draw(g, "Equipo: " + c.weapon + (sk != null ? " · " + sk.name : ""), x, 220, UI.WHITE, 1f);
        int ca = Companions.active(Save.S);
        if (ca < 0) UI.small.draw(g, "Compañero: ninguno (toca para elegir)", x, 231, UI.GREY, 1f);
        else UI.small.draw(g, "Compañero: " + Companions.NAME[ca] + " · " + Companions.PASSIVE[ca].split("\\.")[0].replaceAll("\\(.*\\)", "").trim(), x, 231, Companions.COLOR[ca], 1f);
    }

    private void drawLaunch(Platform.Gfx g, int w, ClassDef c) {
        float k = Mth.clamp(launchT / 1.7f, 0, 1);
        // el portal se abre: destello radial creciente
        float r = 20 + k * k * 700;
        UI.light(g, 78, 150, r, 0xFFE0B0, Mth.clamp(k * 1.4f, 0, 0.85f));
        if (k > 0.35f) g.rect(0, 0, w, Platform.VIEW_H, Mth.withAlpha(0x120408, (int) (Mth.clamp((k - 0.35f) / 0.5f, 0, 1) * 255)), false);
        if (k > 0.5f) {
            float a = Mth.clamp((k - 0.5f) / 0.3f, 0, 1);
            UI.big.center(g, "ENTRANDO AL ABISMO", w / 2f, 112, UI.GOLD, a);
            UI.small.center(g, (infiniteMode ? "Modo infinito" : "Campaña") + " · " + c.name, w / 2f, 134, UI.GREY, a);
        }
    }
}
