package com.julianfarks.roguelike.core;

/** Seleccion de clase y dificultad antes de empezar una partida. */
final class ClassScreen extends Screen {
    private final Screens.TitleBg bg;
    private int selC, selS;
    private int asc;
    private Hit playBtn, ascBtn;
    private float shake;

    ClassScreen(Game g) {
        super(g);
        bg = new Screens.TitleBg();
        selC = Save.S.classUnlocked[Math.min(9, Save.S.lastClass)] ? Save.S.lastClass : 0;
        asc = Math.min(Save.S.ascensionSel, Save.S.ascension);
    }

    @Override void enter() { Snd.music("mus_sanctuary", true); layout(); }

    @Override void layout() {
        hits.clear();
        int w = W();
        for (int i = 0; i < 10; i++) {
            final int id = i;
            Hit h = add(6 + (i % 2) * 38, 26 + (i / 2) * 38, 36, 36, null, () -> { selC = id; selS = 0; });
            h.noSound = false;
            h.plain = true;
        }
        float px = 226, pw = w - 232;
        for (int i = 0; i < 4; i++) {
            final int id = i;
            Hit h = add(px + 8 + i * 30, 176, 26, 26, null, () -> selS = id);
            h.plain = true;
        }
        add(6, 240, 70, 24, "Volver", () -> back());
        ascBtn = add(w / 2f - 62, 240, 124, 24, ascLabel(), () -> { asc = (asc + 1) % (Save.S.ascension + 1); Save.S.ascensionSel = asc; ascBtn.label = ascLabel(); });
        ClassDef c = ClassDef.ALL[selC];
        boolean unlocked = Save.S.classUnlocked[c.id];
        String lab = unlocked ? "¡Jugar!" : "Desbloquear " + Meta.CLASS_COST[c.id];
        playBtn = add(w - 156, 240, 150, 24, lab, () -> play());
        playBtn.disabled = !unlocked && Save.S.souls < Meta.CLASS_COST[c.id];
    }

    private String ascLabel() { return asc == 0 ? "Dificultad: Normal" : "Dificultad: Asc " + asc; }

    private void play() {
        ClassDef c = ClassDef.ALL[selC];
        Save s = Save.S;
        if (!s.classUnlocked[c.id]) {
            if (s.souls < Meta.CLASS_COST[c.id]) return;
            s.souls -= Meta.CLASS_COST[c.id];
            s.classUnlocked[c.id] = true;
            s.write();
            Snd.sfx("ui_unlock", 1f);
            shake = 0.4f;
            layout();
            return;
        }
        s.lastClass = c.id;
        s.ascensionSel = asc;
        s.write();
        Snd.sfx("ui_start_run", 1f);
        game.go(new RunScreen(game, c, asc));
    }

    @Override boolean back() { game.go(new Screens.Title(game)); return true; }

    @Override void update(float dt) {
        bg.update(dt, W());
        if (shake > 0) shake -= dt;
    }

    @Override void key(int code, boolean isDown) {
        if (!isDown) return;
        if (code == 37 || code == 'A') { selC = (selC + 9) % 10; selS = 0; layout(); }
        else if (code == 39 || code == 'D') { selC = (selC + 1) % 10; selS = 0; layout(); }
        else if (code == 38 || code == 'W') { selS = (selS + 3) % 4; }
        else if (code == 40 || code == 'S') { selS = (selS + 1) % 4; }
        else if (code == 10 || code == 32) play();
        else if (code == 27) back();
    }

    @Override void touch(int id, int action, float x, float y) {
        int before = selC;
        super.touch(id, action, x, y);
        if (before != selC) layout();
    }

    @Override void render(Platform.Gfx g) {
        int w = W();
        ClassDef c = ClassDef.ALL[selC];
        boolean unlocked = Save.S.classUnlocked[c.id];
        bg.render(g, w, 0.55f);
        UI.big.center(g, "ELIGE TU CLASE", w / 2f, 5, UI.GOLD, 1f);
        UI.iconC(g, "soul", w - 50, 12, 1f, 1f);
        UI.small.right(g, String.valueOf(Save.S.souls), w - 8, 7, UI.SOUL, 1f);

        // cuadricula de retratos
        for (int i = 0; i < 10; i++) {
            ClassDef ci = ClassDef.ALL[i];
            float x = 6 + (i % 2) * 38, y = 26 + (i / 2) * 38;
            UI.panel(g, i == selC ? 1 : 0, x, y, 36, 36, 0.95f);
            Platform.Img pr = Assets.img("sprites/portrait_" + ci.key + ".png");
            boolean ul = Save.S.classUnlocked[i];
            if (pr != null) g.image(pr, 0, 0, 32, 32, x + 2, y + 2, 32, 32, ul ? 0 : Platform.TINT, 0x303040, 1f);
            else UI.iconC(g, "c_" + ci.key, x + 18, y + 18, 1.5f, ul ? 1f : 0.4f);
            if (!ul) UI.iconC(g, "lock", x + 18, y + 18, 1f, 0.9f);
            if (i == selC && UI.arrow != null) g.imageRot(UI.arrow, 0, 0, 8, 8, x + 38, y + 14, 8, 8, 0, 0, 0, 1f);
        }

        // ilustracion
        float sx = 88, sy = 34;
        UI.light(g, sx + 64, sy + 90, 110, c.color1, 0.30f + 0.05f * (float) Math.sin(t * 2f));
        g.rect(sx + 14, sy + 172, 100, 4, 0x66000000, false);
        Platform.Img splash = Assets.img("sprites/splash_" + c.key + ".png");
        float bob = (float) Math.sin(t * 1.6f) * 1.5f;
        if (splash != null) g.image(splash, 0, 0, splash.w, splash.h, Math.round(sx), Math.round(sy + bob), splash.w, splash.h, unlocked ? 0 : Platform.TINT, 0x20202C, 1f);
        if (!unlocked) UI.iconC(g, "lock", sx + 64, sy + 88, 2f, 0.9f);

        // panel de informacion
        float px = 226, pw = w - 232, py = 24;
        UI.panel(g, 0, px, py, pw, 208, 0.93f);
        UI.big.draw(g, c.name, px + 8, py + 6, c.color1, 1f);
        UI.small.draw(g, c.role, px + 8, py + 25, UI.GREY, 1f);
        int hh = UI.small.drawWrapped(g, c.desc, px + 8, py + 38, (int) pw - 16, 0xE8E0E0, 1f);
        float yy = py + 38 + hh + 2;
        UI.small.draw(g, "Arma: " + c.weapon, px + 8, yy, UI.GOLD, 1f);
        yy += 12;
        int th = UI.small.drawWrapped(g, c.trait, px + 8, yy, (int) pw - 16, UI.CYAN, 1f);
        yy += th + 2;
        stat(g, "Vida", c.hp / 140f, px + 8, yy, 0xFF5A5A, pw);
        stat(g, "Daño", c.dmg / 28f, px + 8, yy + 11, 0xFFB040, pw);
        stat(g, "Ataque", c.atkSpeed / 1.4f, px + 8, yy + 22, 0x7AF0FF, pw);
        stat(g, "Velocidad", c.speed / 1.15f, px + 8, yy + 33, 0x6AE08A, pw);

        // habilidades
        for (int i = 0; i < 4; i++) {
            float x = px + 8 + i * 30, y = 176;
            UI.panel(g, i == selS ? 1 : 0, x, y, 26, 26, 1f);
            UI.iconC(g, c.skills[i].icon, x + 13, y + 13, 1f, unlocked ? 1f : 0.5f);
        }
        ClassDef.Skill sk = c.skills[selS];
        UI.small.draw(g, (selS == 3 ? "Definitiva: " : "") + sk.name, px + 130, 178, selS == 3 ? UI.ORANGE : UI.WHITE, 1f);
        UI.small.draw(g, sk.cd > 0 ? "Enfriamiento " + (int) sk.cd + "s" : "Carga con golpes", px + 130, 190, UI.GREY, 1f);
        UI.small.drawWrapped(g, sk.desc, px + 8, 207, (int) pw - 16, 0xE8E0E0, 1f);

        drawButtons(g);
        if (!unlocked) UI.small.center(g, "Clase bloqueada", w / 2f, 226, UI.RED, 1f);
    }

    private void stat(Platform.Gfx g, String n, float v, float x, float y, int col, float pw) {
        UI.small.draw(g, n, x, y, UI.GREY, 1f);
        float bx = x + 56, bw = pw - 80;
        g.rect(bx, y + 2, bw, 5, 0xFF1A1620, false);
        g.rect(bx, y + 2, bw * Mth.clamp(v, 0.05f, 1f), 5, 0xFF000000 | col, false);
        g.rect(bx, y + 2, bw * Mth.clamp(v, 0.05f, 1f), 1, 0x66FFFFFF, false);
    }
}
