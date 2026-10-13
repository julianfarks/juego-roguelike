package com.julianfarks.roguelike.core;

/** Santuario: mejoras permanentes, desbloqueo de clases y reliquias. */
final class SanctuaryScreen extends Screen {
    private final Screens.TitleBg bg;
    private int tab;
    private float flash, flashSlot = -1;
    private int lastBought = -1;

    SanctuaryScreen(Game g) { super(g); bg = new Screens.TitleBg(); }

    @Override void enter() { Snd.music("mus_sanctuary", true); layout(); }

    @Override void layout() {
        hits.clear();
        int w = W();
        add(6, 4, 54, 18, "Atrás", () -> back());
        Hit a = add(6, 26, 80, 20, "Mejoras", () -> { tab = 0; layout(); });
        Hit b = add(90, 26, 80, 20, "Clases", () -> { tab = 1; layout(); });
        Hit c3 = add(174, 26, 96, 20, "Desbloqueos", () -> { tab = 2; layout(); });
        a.tag = tab == 0 ? 1 : 0; b.tag = tab == 1 ? 1 : 0; c3.tag = tab == 2 ? 1 : 0;
        float cw = (w - 20) / 2f;
        if (tab == 0) {
            for (int i = 0; i < Meta.COUNT; i++) {
                final int id = i;
                Hit h = add(8 + (i % 2) * (cw + 4), 52 + (i / 2) * 47, cw, 44, null, () -> buy(id));
                h.plain = true;
                h.tag = i;
            }
        } else if (tab == 1) {
            for (int i = 0; i < 10; i++) {
                final int id = i;
                Hit h = add(8 + (i % 2) * (cw + 4), 52 + (i / 2) * 38, cw, 35, null, () -> unlock(id));
                h.plain = true;
                h.tag = i;
            }
        }
    }

    private void buy(int i) {
        Save s = Save.S;
        int lv = s.meta[i];
        if (lv >= Meta.MAX[i]) { Snd.sfx("ui_error", 0.7f); return; }
        int cost = Meta.cost(i, lv);
        if (s.souls < cost) { Snd.sfx("ui_error", 0.7f); flash = 0.4f; return; }
        s.souls -= cost;
        s.meta[i]++;
        s.write();
        Snd.sfx("ui_pick_upgrade", 1f);
        lastBought = i; flash = 0.5f;
    }

    private void unlock(int i) {
        Save s = Save.S;
        if (s.classUnlocked[i]) return;
        int cost = Meta.CLASS_COST[i];
        if (s.souls < cost) { Snd.sfx("ui_error", 0.7f); flash = 0.4f; return; }
        s.souls -= cost;
        s.classUnlocked[i] = true;
        s.write();
        Snd.sfx("ui_unlock", 1f);
        lastBought = i; flash = 0.5f;
    }

    @Override boolean back() { game.go(new Screens.Title(game)); return true; }

    @Override void update(float dt) {
        bg.update(dt, W());
        if (flash > 0) flash -= dt;
    }

    @Override void render(Platform.Gfx g) {
        int w = W();
        bg.render(g, w, 0.6f);
        UI.big.center(g, "SANTUARIO", w / 2f, 5, UI.GOLD, 1f);
        UI.iconC(g, "soul", w - 54, 12, 1f, 1f);
        UI.small.right(g, String.valueOf(Save.S.souls), w - 8, 7, UI.SOUL, 1f);
        // reliquias
        String[] keys = {"rey_exanime", "coloso_magma", "reina_escarcha", "devorador_vacio", "ent_ancestral", "titan_tormenta", "matriarca_sangre", "guardian_eclipse"};
        float rx = w - 8 - 8 * 18;
        for (int i = 0; i < 8; i++) {
            boolean has = Save.S.relics[i];
            UI.icon(g, "r_" + keys[i], rx + i * 18, 27, 1f, has ? 0 : Platform.TINT, has ? 0 : 0x303038, has ? 1f : 0.7f);
        }
        UI.small.right(g, "Reliquias " + Save.S.relicCount() + "/8", rx - 6, 31, UI.GOLD, 1f);
        float cw = (w - 20) / 2f;
        drawButtons(g);
        // pestañas resaltadas
        for (Hit h : hits) if (h.label != null && (h.label.equals("Mejoras") || h.label.equals("Clases") || h.label.equals("Desbloqueos")) && h.tag == 1) {
            g.rect(h.x, h.y + h.h - 2, h.w, 2, 0xFFFFD25A, false);
        }
        if (tab == 0) {
            for (int i = 0; i < Meta.COUNT; i++) {
                float x = 8 + (i % 2) * (cw + 4), y = 52 + (i / 2) * 47;
                int lv = Save.S.meta[i];
                boolean max = lv >= Meta.MAX[i];
                int cost = max ? 0 : Meta.cost(i, lv);
                boolean afford = !max && Save.S.souls >= cost;
                UI.panel(g, (lastBought == i && flash > 0) ? 1 : 0, x, y, cw, 44, 0.95f);
                UI.iconC(g, Meta.ICON[i], x + 20, y + 22, 2f, 1f);
                UI.small.draw(g, Meta.NAME[i], x + 42, y + 5, UI.WHITE, 1f);
                // pips
                int pips = Meta.MAX[i];
                float pw = Math.min(7, (cw - 130) / pips);
                for (int k = 0; k < pips; k++) g.rect(x + 42 + k * (pw + 1), y + 17, pw, 4, k < lv ? 0xFFFFD25A : 0xFF2A2430, false);
                UI.small.draw(g, Meta.effect(i, lv), x + 42, y + 26, UI.GREEN, 1f);
                if (max) UI.small.right(g, "MÁX", x + cw - 8, y + 5, UI.GOLD, 1f);
                else {
                    UI.iconC(g, "soul", x + cw - 12 - UI.small.width(String.valueOf(cost)) - 4, y + 12, 1f, 1f);
                    UI.small.right(g, String.valueOf(cost), x + cw - 8, y + 7, afford ? UI.SOUL : UI.RED, 1f);
                    UI.small.right(g, "Nv " + lv + "/" + Meta.MAX[i], x + cw - 8, y + 30, UI.GREY, 1f);
                }
            }
        } else if (tab == 2) {
            int total = Save.S.kills;
            UI.small.draw(g, "Enemigos derrotados: " + total, 8, 50, UI.WHITE, 1f);
            int next = -1;
            for (int i = 0; i < Unlocks.COUNT; i++) if (!Save.S.unlocked[i]) { next = i; break; }
            if (next >= 0) {
                float f = Mth.clamp(total / (float) Unlocks.need(next), 0, 1);
                g.rect(160, 53, w - 170, 6, 0xFF1A1620, false);
                g.rect(160, 53, (w - 170) * f, 6, 0xFFFFD25A, false);
                UI.small.right(g, total + "/" + Unlocks.need(next), w - 8, 44, UI.GOLD, 1f);
            }
            for (int i = 0; i < Unlocks.COUNT; i++) {
                float x = 8 + (i % 2) * (cw + 4), y = 58 + (i / 2) * 38;
                boolean ul = Save.S.unlocked[i];
                UI.panel(g, ul ? 1 : 0, x, y, cw, 36, 0.95f);
                UI.small.draw(g, ul ? Unlocks.NAME[i] : "???", x + 6, y + 4, ul ? UI.GOLD : UI.GREY, 1f);
                UI.small.right(g, Unlocks.KIND[i] + " · " + Unlocks.need(i), x + cw - 6, y + 4, ul ? UI.GREEN : UI.GREY, 1f);
                if (ul) UI.small.drawWrapped(g, Unlocks.DESC[i], x + 6, y + 15, (int) cw - 12, 0xB8B0B0, 1f);
                else UI.small.draw(g, "Derrota " + Unlocks.need(i) + " enemigos en total", x + 6, y + 15, 0x707078, 1f);
            }
        } else {
            for (int i = 0; i < 10; i++) {
                ClassDef c = ClassDef.ALL[i];
                float x = 8 + (i % 2) * (cw + 4), y = 52 + (i / 2) * 38;
                boolean ul = Save.S.classUnlocked[i];
                int cost = Meta.CLASS_COST[i];
                UI.panel(g, (lastBought == i && flash > 0) ? 1 : 0, x, y, cw, 35, 0.95f);
                Platform.Img pr = Assets.img("sprites/portrait_" + c.key + ".png");
                if (pr != null) g.image(pr, 0, 0, 32, 32, x + 2, y + 1, 32, 32, ul ? 0 : Platform.TINT, 0x303040, 1f);
                UI.small.draw(g, c.name, x + 38, y + 6, ul ? c.color1 : UI.GREY, 1f);
                UI.small.draw(g, c.role, x + 38, y + 19, UI.GREY, 1f);
                if (!ul) {
                    UI.iconC(g, "soul", x + cw - 12 - UI.small.width(String.valueOf(cost)) - 4, y + 12, 1f, 1f);
                    UI.small.right(g, String.valueOf(cost), x + cw - 8, y + 8, Save.S.souls >= cost ? UI.SOUL : UI.RED, 1f);
                } else UI.small.right(g, "★", x + cw - 8, y + 8, UI.GREEN, 1f);
            }
        }
        UI.small.center(g, tab == 0 ? "Toca una mejora para comprarla con almas." : tab == 1 ? "Las almas se obtienen al derrotar enemigos y jefes." : "Cada 50 enemigos derrotados desbloqueas armas y habilidades.", w / 2f, 255, UI.GREY, 1f);
    }
}
