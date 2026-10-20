package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/** Pantallas del centro de operaciones: companeros, jardin magico y coleccion/bestiario. Solo muestran y modifican datos reales de Save. */
final class CodexScreens {
    private CodexScreens() {}

    private static void sheetAt(Platform.Gfx g, String name, String anim, float t, float x, float y, float sc, boolean lock, boolean right) {
        Sheet sh = name.startsWith("sprites/") ? Assets.sheet(name) : Assets.spr(name);
        if (sh == null || sh == Sheet.EMPTY) return;
        if (!sh.has(anim)) anim = "idle";
        sh.drawAt(g, anim, t, Math.round(x), Math.round(y), right, sc, lock ? Platform.FLASH : 0, lock ? 0x1C1A2A : 0, 1f);
    }

    // =================================================================== companeros
    static final class Comp extends Screen {
        private final Screens.TitleBg bg = new Screens.TitleBg();
        private String news;
        Comp(Game g) { super(g); news = Companions.refresh(Save.S); }
        @Override void layout() {
            hits.clear();
            int w = W(); float cw = (w - 40) / 3f;
            for (int i = 0; i < Companions.COUNT; i++) {
                final int k = i;
                boolean un = Companions.unlocked(Save.S, i), on = Companions.active(Save.S) == i;
                Hit h = add(20 + i * cw + 8, 210, cw - 16, 22, !un ? "Bloqueado" : (on ? "Quitar" : "Elegir"), () -> {
                    Companions.select(Save.S, Companions.active(Save.S) == k ? -1 : k); layout();
                });
                h.disabled = !un;
            }
            add(w / 2f - 40, 244, 80, 22, "Volver", () -> back());
        }
        @Override boolean back() { game.go(new Ops(game)); return true; }
        @Override void update(float dt) { bg.update(dt, W()); t += dt; }
        @Override void render(Platform.Gfx g) {
            int w = W();
            bg.render(g, w, 0.65f);
            UI.big.center(g, "COMPAÑEROS", w / 2f, 14, UI.GOLD, 1f);
            UI.small.center(g, "Elige un espíritu para la expedición. Solo uno a la vez.", w / 2f, 34, UI.GREY, 1f);
            float cw = (w - 40) / 3f;
            for (int i = 0; i < Companions.COUNT; i++) {
                float x = 20 + i * cw + 4;
                boolean un = Companions.unlocked(Save.S, i), on = Companions.active(Save.S) == i;
                UI.panel(g, on ? 1 : 0, x, 50, cw - 8, 190, 0.95f);
                UI.light(g, x + (cw - 8) / 2, 100, 30, Companions.COLOR[i] | 0xFF000000, un ? 0.3f : 0.08f);
                sheetAt(g, Companions.SHEET[i], "idle", t, x + (cw - 8) / 2, 120, 2f, !un, true);
                UI.small.center(g, un ? Companions.NAME[i] : "???", x + (cw - 8) / 2, 126, un ? Companions.COLOR[i] : UI.GREY, 1f);
                UI.small.center(g, Companions.KIND[i], x + (cw - 8) / 2, 138, UI.GREY, 1f);
                String tx = un ? Companions.PASSIVE[i] : "Requisito: " + Companions.UNLOCK[i];
                UI.small.drawWrapped(g, tx, x + 8, 152, (int) (cw - 24), un ? UI.WHITE : UI.GREY, 1f);
                if (on) UI.small.center(g, "EN EL EQUIPO", x + (cw - 8) / 2, 56, UI.GREEN, 1f);
            }
            if (news != null) UI.small.center(g, "¡Nuevo compañero: " + news + "!", w / 2f, 226, UI.CYAN, 1f);
            drawButtons(g);
        }
    }

    // =================================================================== jardin
    static final class GardenScr extends Screen {
        private final Screens.TitleBg bg = new Screens.TitleBg();
        private float pop; private int popPlot = -1;
        GardenScr(Game g) { super(g); }
        @Override void layout() {
            hits.clear();
            int w = W(); float cw = (w - 40) / 3f;
            for (int i = 0; i < Garden.PLOTS; i++) {
                final int k = i;
                int lv = Garden.level(Save.S, i);
                String lb = lv >= Garden.MAX ? "Máximo" : "Crecer · " + Garden.COST[lv] + " almas";
                Hit h = add(20 + i * cw + 8, 214, cw - 16, 20, lb, () -> { if (Garden.grow(Save.S, k)) { popPlot = k; pop = 1f; Snd.sfx("ui_confirm", 0.9f); } layout(); });
                h.disabled = !Garden.canGrow(Save.S, i);
            }
            add(w / 2f - 40, 244, 80, 22, "Volver", () -> back());
        }
        @Override boolean back() { game.go(new Ops(game)); return true; }
        @Override void update(float dt) { bg.update(dt, W()); t += dt; if (pop > 0) pop -= dt; }
        @Override void render(Platform.Gfx g) {
            int w = W();
            bg.render(g, w, 0.65f);
            UI.big.center(g, "JARDÍN MÁGICO", w / 2f, 14, UI.GOLD, 1f);
            UI.small.center(g, "Almas: " + Save.S.souls + "   ·   Los cristales crecen con las almas que ganas en las runs.", w / 2f, 34, UI.GREY, 1f);
            float cw = (w - 40) / 3f;
            for (int i = 0; i < Garden.PLOTS; i++) {
                float x = 20 + i * cw + 4, cx = x + (cw - 8) / 2;
                int lv = Garden.level(Save.S, i);
                UI.panel(g, lv >= Garden.MAX ? 1 : 0, x, 50, cw - 8, 190, 0.95f);
                UI.light(g, cx, 112, 28 + 4 * lv + (popPlot == i && pop > 0 ? 18 * pop : 0), Garden.COLOR[i] | 0xFF000000, 0.12f + 0.06f * lv);
                sheetAt(g, "ops_crystal", "stage" + lv, t + i * 0.3f, cx, 132, 1.6f, false, true);
                UI.small.center(g, Garden.NAME[i], cx, 140, Garden.COLOR[i], 1f);
                for (int s = 0; s < Garden.MAX; s++) g.rect(cx - 22 + s * 12, 152, 9, 4, s < lv ? (Garden.COLOR[i] | 0xFF000000) : 0xFF2A2838, false);
                UI.small.center(g, "Etapa " + lv + " / " + Garden.MAX, cx, 160, UI.WHITE, 1f);
                int tw = (int) (cw - 20);
                String ef = lv == 0 ? "Aún sin efecto" : "Ahora: " + Garden.effect(i, lv);
                int eh = UI.small.wrap(ef, tw).size();
                UI.small.drawWrapped(g, ef, x + 10, 170, tw, UI.GREEN, 1f, 10);
                int dy = 170 + eh * 10 + 2;
                int dh = UI.small.drawWrapped(g, Garden.DESC[i], x + 10, dy, tw, UI.GREY, 1f, 10);
                PrepScreen.fitErr("jardin " + i, dy + dh - 1, 213, -1);
            }
            drawButtons(g);
        }
    }

    // =================================================================== coleccion y bestiario
    private static final class Entry {
        String name, sheet, anim = "idle", icon; boolean found, locked; float scale = 1f; int color = 0xFFFFFF, tint;
        List<String> lines = new ArrayList<>();
    }

    static final class CodexScr extends Screen {
        private final Screens.TitleBg bg = new Screens.TitleBg();
        private static final String[] TABS = {"Enemigos", "Jefes", "Sucesos", "Reliquias", "Mejoras", "Espadachines"};
        private static final int PER = 8;
        private int tab, page, selIdx;
        private List<Entry> entries = new ArrayList<>();
        private final int pageMax[] = new int[1];
        CodexScr(Game g) { super(g); build(); }

        private void build() {
            Save s = Save.S;
            entries = new ArrayList<>();
            if (tab == 0) {
                for (EnemyDef d : Codex.enemies()) {
                    Entry e = new Entry(); e.found = s.dex.contains("e:" + d.id); e.name = Codex.pretty(d.id); e.sheet = d.sheet; e.color = d.color; e.scale = d.elite ? 1f : 1.2f;
                    e.lines.add(Codex.roleName(d.role) + (d.elite ? " (élite único)" : ""));
                    e.lines.add("Vida base " + Math.round(d.hp) + " · Daño " + Math.round(d.dmg));
                    e.lines.add("Almas: " + d.souls + (d.status.isEmpty() ? "" : " · Aplica " + d.status));
                    entries.add(e);
                }
            } else if (tab == 1) {
                for (BossDef b : BossDef.ALL) {
                    Entry e = new Entry(); e.found = s.dex.contains("b:" + b.idx) || (b.idx < 8 && s.relics[b.idx]) || (b.idx == 8 && s.finalBeaten);
                    e.name = b.name; e.sheet = b.sheet; e.color = b.color; e.scale = 0.5f;
                    e.lines.add(b.title); e.lines.add("Elemento: " + b.element); e.lines.add("Vida base " + Math.round(b.hp));
                    e.lines.add(b.idx < 8 ? (s.relics[b.idx] ? "Derrotado: reliquia obtenida" : "Aún sin derrotar") : (s.finalBeaten ? "Derrotado" : "Aún sin derrotar"));
                    entries.add(e);
                }
            } else if (tab == 2) {
                for (int k = 1; k < Events.COUNT; k++) {
                    Entry e = new Entry(); e.found = s.dex.contains("v:" + k) || s.events[k] > 0; e.name = Events.NAME[k]; e.icon = Events.ICON[k]; e.color = Events.GLOW[k];
                    e.lines.add(Events.SUB[k]); e.lines.add("Completados: " + s.events[k]);
                    entries.add(e);
                }
            } else if (tab == 3) {
                for (int i = 0; i < 8; i++) {
                    Entry e = new Entry(); e.found = s.relics[i]; e.name = RunScreen.RELIC_NAMES[i]; e.sheet = "sprites/ev_relic"; e.color = BossDef.ALL[i].color; e.tint = BossDef.ALL[i].color;
                    e.lines.add("Reliquia de " + BossDef.ALL[i].name); e.lines.add(e.found ? "Conservada en la sala de trofeos" : "Derrota a su jefe para obtenerla");
                    entries.add(e);
                }
            } else if (tab == 4) {
                for (Blessing b : Blessing.ALL) {
                    Entry e = new Entry(); e.found = s.blessUse[b.id] > 0; e.name = b.name; e.icon = b.icon; e.color = Blessing.RAR_COLOR[Math.max(0, Math.min(4, b.rar))];
                    e.lines.add(b.desc); e.lines.add("Usada en " + s.blessUse[b.id] + (s.blessUse[b.id] == 1 ? " partida" : " partidas"));
                    entries.add(e);
                }
            } else {
                for (ClassDef c : ClassDef.ALL) {
                    Entry e = new Entry(); e.found = s.classUnlocked[c.id]; e.name = c.name; e.sheet = null; e.color = c.color1;
                    e.lines.add(c.role); e.lines.add("Vida " + Math.round(c.hp) + " · Daño " + Math.round(c.dmg)); e.lines.add(c.weapon);
                    e.lines.add("Victorias: " + s.classWins[c.id]);
                    entries.add(e);
                }
            }
            pageMax[0] = Math.max(0, (entries.size() - 1) / PER);
            page = Math.min(page, pageMax[0]); selIdx = Math.min(selIdx, Math.max(0, entries.size() - 1));
        }

        @Override void layout() {
            hits.clear();
            int w = W(); float tw = (w - 20) / (float) TABS.length;
            for (int i = 0; i < TABS.length; i++) { final int k = i; Hit h = add(10 + i * tw, 30, tw - 3, 16, TABS[i], () -> { tab = k; page = 0; selIdx = 0; build(); layout(); }); h.disabled = false; }
            add(10, 244, 70, 22, "Volver", () -> back());
            Hit pv = add(w / 2f - 130, 244, 40, 22, "<", () -> { if (page > 0) { page--; selIdx = page * PER; } }); pv.noSound = false;
            add(w / 2f - 82, 244, 40, 22, ">", () -> { if (page < pageMax[0]) { page++; selIdx = page * PER; } });
            int base = page * PER;
            for (int i = 0; i < PER && base + i < entries.size(); i++) {
                final int idx = base + i; int col = i % 2, row = i / 2;
                Hit h = add(10 + col * 112, 54 + row * 46, 108, 42, null, () -> selIdx = idx); h.plain = true;
            }
        }
        @Override boolean back() { game.go(new Ops(game)); return true; }
        @Override void update(float dt) { bg.update(dt, W()); t += dt; if (hits.size() > 0) layout(); }

        @Override void render(Platform.Gfx g) {
            int w = W();
            bg.render(g, w, 0.7f);
            UI.big.center(g, "COLECCIÓN Y BESTIARIO", w / 2f, 8, UI.GOLD, 1f);
            UI.small.right(g, Codex.foundEntries() + " / " + Codex.totalEntries(), w - 10, 12, UI.CYAN, 1f);
            int base = page * PER;
            for (int i = 0; i < PER && base + i < entries.size(); i++) {
                Entry e = entries.get(base + i); int col = i % 2, row = i / 2;
                float x = 10 + col * 112, y = 54 + row * 46;
                UI.panel(g, base + i == selIdx ? 1 : 0, x, y, 108, 42, 0.95f);
                if (e.sheet != null || e.icon != null) drawIllus(g, e, x + 22, y + 38, 30);
                else drawClass(g, base + i, x + 22, y + 38, 0.7f, !e.found);
                java.util.List<String> nl = UI.small.wrap(e.found ? e.name : "???", 60);
                for (int k = 0; k < Math.min(2, nl.size()); k++) UI.small.draw(g, nl.get(k), x + 44, y + 8 + k * 11, e.found ? UI.WHITE : UI.GREY, 1f);
                g.rect(x + 44, y + 32, 6, 4, e.found ? 0xFF6AE08A : 0xFF3A3848, false);
            }
            if (!entries.isEmpty()) {
                Entry e = entries.get(selIdx);
                float px = 240, pw = w - 250;
                UI.panel(g, 0, px, 54, pw, 182, 0.95f);
                UI.light(g, px + pw / 2, 120, 40, e.color | 0xFF000000, e.found ? 0.25f : 0.06f);
                if (tab == 5) drawClass(g, selIdx, px + pw / 2, 150, 2f, !e.found);
                else drawIllus(g, e, px + pw / 2, 150, 80);
                UI.small.center(g, e.found ? e.name : "???", px + pw / 2, 160, e.found ? e.color : UI.GREY, 1f);
                if (e.found) { for (int i = 0; i < e.lines.size(); i++) UI.small.center(g, e.lines.get(i), px + pw / 2, 174 + i * 11, UI.WHITE, 1f); }
                else UI.small.center(g, tab == 0 ? "Encuéntralo en una expedición." : "Aún sin descubrir.", px + pw / 2, 176, UI.GREY, 1f);
            }
            UI.small.center(g, (page + 1) + " / " + (pageMax[0] + 1), w / 2f - 56 + 0f, 250 - 0f, UI.GREY, 0f);
            drawButtons(g);
            UI.small.center(g, (page + 1) + " / " + (pageMax[0] + 1), w / 2f - 6, 250, UI.GREY, 1f);
        }

        private void drawIllus(Platform.Gfx g, Entry e, float x, float feet, float fit) {
            boolean lock = !e.found;
            if (e.icon != null) { UI.iconC(g, e.icon, x, feet - fit * 0.45f, fit / 22f, lock ? 0.25f : 1f); return; }
            Sheet sh = Assets.sheet(e.sheet);
            if (sh == null || sh == Sheet.EMPTY) return;
            String an = sh.has("idle") ? "idle" : "idle";
            int fl = lock ? Platform.FLASH : (e.tint != 0 ? Platform.TINT : 0);
            sh.drawAt(g, an, t, Math.round(x), Math.round(feet), true, Math.min(2.5f, Math.min(fit / Math.max(8, sh.ch * 0.75f), (fit * 1.3f) / Math.max(8, sh.cw * 0.75f))), fl, lock ? 0x1C1A2A : e.tint, 1f);
        }

        private void drawClass(Platform.Gfx g, int idx, float x, float feet, float sc, boolean lock) {
            Sheet sh = Cosmetics.sheetFor(ClassDef.ALL[idx]);
            if (sh == null || sh == Sheet.EMPTY) return;
            sh.drawAt(g, "idle", t, Math.round(x), Math.round(feet), true, sc, lock ? Platform.FLASH : 0, lock ? 0x1C1A2A : 0, 1f);
        }
    }

    // =================================================================== retos del modo infinito
    static final class Challenges extends Screen {
        private final Screens.TitleBg bg = new Screens.TitleBg();
        Challenges(Game g) { super(g); }
        @Override void layout() {
            hits.clear();
            int w = W();
            for (int i = 0; i < Infinite.MOD_COUNT; i++) {
                final int k = i;
                Hit h = add(20, 52 + i * 38, w - 40, 34, null, () -> { Save.S.infMods ^= 1 << k; Save.S.write(); }); h.plain = true;
            }
            add(w / 2f - 70, 244, 60, 22, "Volver", () -> back());
            add(w / 2f + 10, 244, 90, 22, "Quitar todos", () -> { Save.S.infMods = 0; Save.S.write(); });
        }
        @Override boolean back() { game.go(new PrepScreen(game)); return true; }
        @Override void update(float dt) { bg.update(dt, W()); t += dt; }
        @Override void render(Platform.Gfx g) {
            int w = W();
            bg.render(g, w, 0.7f);
            UI.big.center(g, "RETOS DEL INFINITO", w / 2f, 12, UI.GOLD, 1f);
            java.util.List<String> sub = UI.small.wrap("Opcionales. Cada reto suma puntaje; el récord sigue siendo por pisos.", w - 24);
            for (int k = 0; k < sub.size(); k++) UI.small.drawCenterRaw(g, sub.get(k), w / 2f, sub.size() > 1 ? 31 + k * 10 : 34, UI.GREY, 1f);
            for (int i = 0; i < Infinite.MOD_COUNT; i++) {
                boolean on = (Save.S.infMods & (1 << i)) != 0;
                float y = 52 + i * 38;
                UI.panel(g, on ? 1 : 0, 20, y, w - 40, 34, 0.95f);
                g.rect(30, y + 11, 12, 12, on ? 0xFF6AE08A : 0xFF2A2838, false);
                if (on) { g.rect(33, y + 14, 6, 6, 0xFF10301A, false); }
                UI.small.draw(g, Infinite.MOD_NAME[i], 52, y + 6, on ? UI.GOLD : UI.WHITE, 1f);
                UI.small.draw(g, Infinite.MOD_DESC[i], 52, y + 19, UI.GREY, 1f);
                UI.small.right(g, "+" + Infinite.MOD_BONUS[i] + "% puntaje", w - 30, y + 6, UI.GREEN, 1f);
            }
            int p = Infinite.bonusPct(Save.S.infMods);
            UI.small.center(g, "Bonificación total: +" + p + "% de puntaje" + (p == 0 ? " (sin retos)" : ""), w / 2f, 216, p > 0 ? UI.GREEN : UI.GREY, 1f);
            UI.small.center(g, "No cambian las gemas ni el precio de las revividas.", w / 2f, 228, UI.GREY, 1f);
            UI.small.center(g, "No valen en pruebas del Modo Desarrollador.", w / 2f, 238 - 0, UI.GREY, 0f);
            drawButtons(g);
        }
    }
}
