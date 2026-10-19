package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/**
 * Pantalla de inventario de la run (overlay OV_INV de RunScreen). Solo muestra el estado REAL de esta partida (RunState):
 * nada de lo que se ve aqui es la coleccion permanente. Categorias: armas, bendiciones, reliquias y especiales, objetos.
 * Se maneja con teclado, mando, raton y tactil; no toca el combate (el juego esta en pausa mientras esta abierto).
 */
final class Inventory {
    static final int C_WEAPONS = 0, C_BLESS = 1, C_RELICS = 2, C_OBJECTS = 3, C_COUNT = 4;
    static final String[] CAT_NAME = {"Armas", "Bendiciones", "Reliquias", "Objetos"};
    static final String[] RAR_ES = {"Común", "Poco común", "Rara", "Épica", "Legendaria"};
    static final String[] SORT_NAME = {"Rareza", "Nombre"};
    static final String[] FILTER_NAME = {"Todas", "Nuevas", "Común", "Poco común", "Rara", "Épica", "Legendaria"};
    static final int[] RAR_RGB = {0xC8CCD8, 0x6AE08A, 0x6AA8FF, 0xC070FF, 0xFFB030};
    static final String[] RELIC_ICON = {"r_rey_exanime", "r_coloso_magma", "r_reina_escarcha", "r_devorador_vacio", "r_ent_ancestral", "r_titan_tormenta", "r_matriarca_sangre", "r_guardian_eclipse"};
    static final int ST_OWNED = 0, ST_EQUIPPED = 1, ST_FLOOR = 2, ST_LEFT = 3;
    static final String[] ST_NAME = {"En tu poder", "Equipada", "En el suelo de esta sala", "Dejada atrás en otra sala"};

    static final class Item {
        int cat, rar, state, lvl, maxLvl, wid = -1, bid = -1, kind;       // kind: 0 normal, 1 arma principal, 2 escudo, 3 granada, 4 especial, 5 pocion, 6 pacto, 7 reliquia, 8 compañero, 9 bendicion inicial
        String key, name, icon, sub = "";
        boolean isNew, active;
        int idx;
    }

    final RunScreen sc;
    int cat = C_WEAPONS, sort = 0, filter = 0, sel = 0, scroll = 0, focus = 0, slot = 0;   // focus 0 = rejilla, 1 = ranuras de equipo
    float t, dwell;
    List<Item> items = new ArrayList<>();
    final Item[] equip = new Item[2];
    int cols = 6, rows = 3;
    float gx, gy, gw, gh, dx, dy, dw, dh;          // zonas de la pantalla (rejilla y detalle)
    int lastW, lastH;
    final int[] catNew = new int[C_COUNT];
    boolean fromPause;

    Inventory(RunScreen sc) { this.sc = sc; }

    RunState rs() { return sc.rs; }

    // ================================================================ datos
    private Item mk(int cat, String key, String name, String icon, int rar, int state) {
        Item it = new Item();
        it.cat = cat; it.key = key; it.name = name; it.icon = Items_has(icon) ? icon : "star"; it.rar = Math.max(0, Math.min(4, rar)); it.state = state;
        it.isNew = !rs().seen.contains(key);
        return it;
    }

    private static boolean Items_has(String icon) { return icon != null && UI.hasIcon(icon); }

    /** Reconstruye todas las listas desde el estado real de la run y aplica orden y filtro. */
    void rebuild() {
        RunState rs = rs();
        List<Item> all = new ArrayList<>();
        ClassDef cls = rs.cls;
        // ---- armas
        Item main = mk(C_WEAPONS, "m:" + cls.key, cls.weapon, "c_" + cls.key, 0, ST_EQUIPPED);
        main.kind = 1; main.active = !rs.secActive; main.lvl = rs.weaponLvl; main.sub = "Arma principal";
        all.add(main); equip[0] = main;
        equip[1] = null;
        for (int id = 1; id < Items.SEC_COUNT; id++) {
            if (rs.wState[id] == 0 && rs.sec != id) continue;
            int st = rs.sec == id ? ST_EQUIPPED : rs.wState[id] == 2 ? ST_FLOOR : ST_LEFT;
            Item it = mk(C_WEAPONS, "w:" + id, Items.SEC_NAME[id], Items.SEC_ICON[id], Items.SEC_RAR[id], st);
            it.wid = id; it.active = rs.sec == id && rs.secActive;
            if (st == ST_EQUIPPED) { it.lvl = rs.secLvl; it.maxLvl = 3; equip[1] = it; }
            it.sub = "Arma secundaria";
            all.add(it);
        }
        // ---- bendiciones
        for (char c = 'A'; c <= 'J'; c++) for (Blessing b : Blessing.ALL) {
            if (b.cat != c || rs.bless[b.id] <= 0) continue;
            Item it = mk(C_BLESS, "b:" + b.id, b.name, b.icon, b.rar, ST_OWNED);
            it.bid = b.id; it.lvl = rs.bless[b.id]; it.maxLvl = b.max; it.sub = BlessData.CAT_ES[b.cat - 'A'];
            all.add(it);
        }
        // ---- reliquias y especiales
        for (int i = 0; i < 8; i++) if (rs.relicsThisRun[i]) {
            Item it = mk(C_RELICS, "r:" + i, RunScreen.RELIC_NAMES[i], RELIC_ICON[i], 4, ST_OWNED);
            it.kind = 7; it.wid = i; it.sub = "Reliquia";
            all.add(it);
        }
        for (int i = 0; i < Events.PACTS.length; i++) if (rs.pacts[i] > 0) {
            Events.Pact p = Events.PACTS[i];
            Item it = mk(C_RELICS, "p:" + i, p.name, p.icon, 2, ST_OWNED);
            it.kind = 6; it.wid = i; it.sub = "Pacto de santuario";
            all.add(it);
        }
        if (rs.startBless >= 0 && StartBlessing.get(rs.startBless) != null) {
            StartBlessing sb = StartBlessing.get(rs.startBless);
            Item it = mk(C_RELICS, "s:" + sb.id, sb.name, sb.icon, 1, ST_OWNED);
            it.kind = 9; it.wid = sb.id; it.sub = "Bendición inicial";
            all.add(it);
        }
        if (rs.companion >= 0 && rs.companion < Companions.COUNT) {
            Item it = mk(C_RELICS, "c:" + rs.companion, Companions.NAME[rs.companion], "soul", 2, ST_OWNED);
            it.kind = 8; it.wid = rs.companion; it.sub = Companions.KIND[rs.companion];
            all.add(it);
        }
        // ---- otros objetos
        {
            Item it = mk(C_OBJECTS, "o:sh" + rs.shield, Items.SH_NAME[rs.shield], ChestLoot.SH_ICON[rs.shield], ChestLoot.SH_RAR[rs.shield], ST_EQUIPPED);
            it.kind = 2; it.wid = rs.shield; it.sub = "Escudo"; it.active = true;
            all.add(it);
        }
        if (rs.gren != 0) {
            Item it = mk(C_OBJECTS, "o:gr" + rs.gren, Items.GR_NAME[rs.gren], Items.GR_ICON[rs.gren], ChestLoot.GR_RAR[Math.min(rs.gren, ChestLoot.GR_RAR.length - 1)], ST_EQUIPPED);
            it.kind = 3; it.wid = rs.gren; it.lvl = rs.grenLvl; it.maxLvl = 3; it.sub = "Granada · " + rs.grenCount + " uds."; it.active = true;
            all.add(it);
        }
        if (rs.special != 0) {
            Item it = mk(C_OBJECTS, "o:sp" + rs.special, Items.SP_NAME[rs.special], ChestLoot.SP_ICON[rs.special], ChestLoot.SP_RAR[rs.special], ST_EQUIPPED);
            it.kind = 4; it.wid = rs.special; it.sub = "Mejora del arma principal"; it.active = true;
            all.add(it);
        }
        {
            Item it = mk(C_OBJECTS, "o:pot", "Frascos de vida", "potion", 0, ST_OWNED);
            it.kind = 5; it.sub = rs.potions + "/" + rs.stats.potionsMax;
            all.add(it);
        }
        // ---- contadores de novedades por categoria (sin filtrar)
        java.util.Arrays.fill(catNew, 0);
        for (Item it : all) if (it.isNew) catNew[it.cat]++;
        // ---- filtro, orden y seleccion
        List<Item> out = new ArrayList<>();
        for (Item it : all) {
            if (it.cat != cat) continue;
            if (filter == 1 && !it.isNew) continue;
            if (filter >= 2 && it.rar != filter - 2) continue;
            out.add(it);
        }
        final int so = sort;
        out.sort((a, b) -> {
            if (a.kind == 1 || b.kind == 1) return a.kind == 1 ? -1 : 1;            // el arma principal siempre primera
            if (a.state == ST_EQUIPPED != (b.state == ST_EQUIPPED)) return a.state == ST_EQUIPPED ? -1 : 1;   // lo equipado primero
            if (so == 0 && a.rar != b.rar) return b.rar - a.rar;
            return a.name.compareToIgnoreCase(b.name);
        });
        for (int i = 0; i < out.size(); i++) out.get(i).idx = i;
        items = out;
        if (sel >= items.size()) sel = Math.max(0, items.size() - 1);
        clampScroll();
    }

    Item cur() {
        if (focus == 1) return equip[slot];
        return items.isEmpty() ? null : items.get(Math.min(sel, items.size() - 1));
    }

    void clampScroll() {
        int totalRows = Math.max(1, (items.size() + cols - 1) / cols);
        int maxScroll = Math.max(0, totalRows - rows);
        scroll = Math.max(0, Math.min(maxScroll, scroll));
        int r = sel / cols;
        if (r < scroll) scroll = r;
        if (r >= scroll + rows) scroll = r - rows + 1;
        scroll = Math.max(0, Math.min(maxScroll, scroll));
    }

    // ================================================================ apertura y estado
    void open(boolean fromPause) {
        this.fromPause = fromPause;
        cat = C_WEAPONS; filter = 0; sel = 0; scroll = 0; focus = 0; slot = 0; dwell = 0; t = 0;
        rebuild();
    }

    /** Marca como vistos los objetos que ya estaban al empezar (arma de clase, bendicion inicial...). */
    static void seeAll(RunState rs) {
        rs.seen.add("m:" + rs.cls.key);
        for (int id = 1; id < Items.SEC_COUNT; id++) if (rs.wState[id] != 0 || rs.sec == id) rs.seen.add("w:" + id);
        for (Blessing b : Blessing.ALL) if (rs.bless[b.id] > 0) rs.seen.add("b:" + b.id);
        for (int i = 0; i < 8; i++) if (rs.relicsThisRun[i]) rs.seen.add("r:" + i);
        for (int i = 0; i < Events.PACTS.length; i++) if (rs.pacts[i] > 0) rs.seen.add("p:" + i);
        if (rs.startBless >= 0) rs.seen.add("s:" + rs.startBless);
        if (rs.companion >= 0) rs.seen.add("c:" + rs.companion);
        rs.seen.add("o:sh" + rs.shield);
        if (rs.gren != 0) rs.seen.add("o:gr" + rs.gren);
        if (rs.special != 0) rs.seen.add("o:sp" + rs.special);
        rs.seen.add("o:pot");
        rs.unseen.clear();
    }

    void update(float dt) {
        t += dt;
        Item it = cur();
        if (it != null && it.isNew) {
            dwell += dt;
            if (dwell > 0.7f) markSeen(it);
        } else dwell = 0;
    }

    void markSeen(Item it) {
        rs().markSeen(it.key);
        it.isNew = false; dwell = 0;
        rebuild();
    }

    // ================================================================ disposicion
    void layout(int w) {
        int h = ViewSize.h;
        lastW = w; lastH = h;
        sc.hits.clear();
        float pad = 10;
        // cabecera: pestanas
        float ty = 7, th = 18;
        float[] tw = new float[C_COUNT]; float tot = 0, avail = w - pad * 2 - 96 - 3 * (C_COUNT - 1);
        for (int c = 0; c < C_COUNT; c++) { tw[c] = Math.max(52, UI.small.width(CAT_NAME[c] + (catNew[c] > 0 ? " !" : "")) + 18); tot += tw[c]; }
        float sc2 = tot > avail ? avail / tot : 1f;
        float tx0 = pad;
        for (int c = 0; c < C_COUNT; c++) {
            final int cc = c;
            float tww = tw[c] * sc2;
            Screen.Hit hb = sc.add(tx0, ty, tww, th, CAT_NAME[c] + (catNew[c] > 0 ? " !" : ""), () -> setCat(cc));
            hb.tag = 100 + c; hb.noSound = false;
            tx0 += tww + 3;
        }
        // pie: orden, filtro, volver
        float fy = h - 25, fh = 20;
        float bw = Math.min(112, (w - pad * 2 - 12) / 3f);
        sc.add(pad, fy, bw, fh, "Orden: " + SORT_NAME[sort], this::cycleSort).tag = 200;
        sc.add(pad + bw + 6, fy, bw, fh, "Filtro: " + FILTER_NAME[filter], this::cycleFilter).tag = 201;
        sc.add(w - pad - bw, fy, bw, fh, "Volver al juego", sc::invClose).tag = 202;
        // ranuras de equipo
        float ey = 28, eh = 40;
        float ew = (w - pad * 2 - 6) / 2f;
        for (int k = 0; k < 2; k++) {
            final int kk = k;
            Screen.Hit he = sc.add(pad + k * (ew + 6), ey, ew, eh, null, () -> { focus = 1; slot = kk; dwell = 0; });
            he.tag = 300 + k; he.plain = true;
        }
        // zonas: rejilla a la izquierda y detalle a la derecha
        float by = ey + eh + 6;
        float bh = fy - 5 - by;
        dw = Math.max(150, Math.min(190, w * 0.38f));
        dx = w - pad - dw; dy = by; dh = bh;
        gx = pad; gy = by; gw = dx - 6 - pad; gh = bh;
        float cell = 32, gap = 3;
        cols = Math.max(3, (int) ((gw - 14 + gap) / (cell + gap)));
        rows = Math.max(1, (int) ((gh - 18 + gap) / (cell + gap)));
        clampScroll();
        for (int r = 0; r < rows; r++) for (int c = 0; c < cols; c++) {
            int i = (scroll + r) * cols + c;
            if (i >= items.size()) continue;
            final int ii = i;
            Screen.Hit hc = sc.add(gx + 4 + c * (cell + gap), gy + 4 + r * (cell + gap), cell, cell, null, () -> { focus = 0; sel = ii; dwell = 0; Item it = cur(); if (it != null) markSeen(it); });
            hc.tag = 400 + i; hc.plain = true;
        }
        // desplazamiento (tactil / raton)
        int totalRows = (items.size() + cols - 1) / cols;
        Screen.Hit up = sc.add(gx + gw - 12, gy + 2, 11, 14, "^", () -> { scroll(-1); }); up.tag = 210; up.plain = true; up.disabled = scroll <= 0;
        Screen.Hit dn = sc.add(gx + gw - 12, gy + gh - 32, 11, 14, "v", () -> { scroll(1); }); dn.tag = 211; dn.plain = true; dn.disabled = scroll + rows >= totalRows;
        // accion del detalle
        Item it = cur();
        if (it != null && canActivate(it)) {
            Screen.Hit ha = sc.add(dx + 8, dy + dh - 24, dw - 16, 18, activateLabel(it), this::activate); ha.tag = 220;
        }
    }

    void relayout() { sc.layoutOverlay(); }

    void setCat(int c) {
        if (c == cat) return;
        cat = c; sel = 0; scroll = 0; focus = 0; dwell = 0;
        Snd.sfx("ui_hover", 0.6f);
        rebuild(); relayout();
    }

    void cycleSort() { sort = (sort + 1) % SORT_NAME.length; Snd.sfx("ui_hover", 0.6f); rebuild(); relayout(); }
    void cycleFilter() { filter = (filter + 1) % FILTER_NAME.length; sel = 0; scroll = 0; Snd.sfx("ui_hover", 0.6f); rebuild(); relayout(); }

    void scroll(int d) {
        int totalRows = (items.size() + cols - 1) / cols;
        scroll = Math.max(0, Math.min(Math.max(0, totalRows - rows), scroll + d));
        if (sel / cols < scroll) sel = scroll * cols;
        if (sel / cols >= scroll + rows) sel = Math.min(items.size() - 1, (scroll + rows - 1) * cols);
        relayout();
    }

    // ================================================================ acciones
    boolean canActivate(Item it) {
        if (sc.lv == null || !sc.lv.pl.alive || it.cat != C_WEAPONS) return false;
        if (it.kind == 1) return rs().secActive && rs().sec != 0;
        return it.wid >= 0 && rs().sec == it.wid && !rs().secActive;
    }

    String activateLabel(Item it) { return it.kind == 1 ? "Usar arma principal" : "Usar esta arma"; }

    void activate() {
        Item it = cur();
        if (it == null || !canActivate(it)) { Snd.sfx("ui_error", 0.6f); return; }
        if (Arsenal.swap(sc.lv, sc.lv.pl)) { Snd.sfx("ui_confirm", 0.8f); }
        rebuild(); relayout();
    }

    // ================================================================ teclas
    void key(int code) {
        int n = items.size();
        if (code == 'Q') { setCat((cat + C_COUNT - 1) % C_COUNT); return; }
        if (code == 'E') { setCat((cat + 1) % C_COUNT); return; }
        if (code == 'F') { cycleFilter(); return; }
        if (code == 'O') { cycleSort(); return; }
        if (code == 27 || code == 9) { sc.invClose(); return; }
        if (code == 10 || code == 32 || code == 'J') { Item it = cur(); if (it != null && it.isNew) markSeen(it); if (it != null && canActivate(it)) activate(); return; }
        boolean l = code == 37 || code == 'A', r = code == 39 || code == 'D', u = code == 38 || code == 'W', d = code == 40 || code == 'S';
        if (!(l || r || u || d)) return;
        Snd.sfx("ui_hover", 0.5f);
        if (focus == 1) {
            if (l || r) slot = 1 - slot;
            else if (d && n > 0) { focus = 0; sel = Math.min(n - 1, slot == 0 ? 0 : Math.min(cols, n - 1)); }
            dwell = 0; relayout(); return;
        }
        if (n == 0) { if (u) { focus = 1; } relayout(); return; }
        int c = sel % cols;
        if (l) sel = sel > 0 ? sel - 1 : n - 1;
        else if (r) sel = sel < n - 1 ? sel + 1 : 0;
        else if (u) { if (sel - cols >= 0) sel -= cols; else { focus = 1; slot = c < cols / 2 ? 0 : 1; } }
        else if (d) { if (sel + cols < n) sel += cols; else if (sel / cols < (n - 1) / cols) sel = n - 1; }
        dwell = 0; clampScroll(); relayout();
    }

    // ================================================================ dibujo
    private static int rgba(int rgb, int a) { return Mth.withAlpha(rgb & 0xFFFFFF, a); }

    private void stateBadge(Platform.Gfx g, Item it, float x, float y) {
        // simbolos de estado, legibles sin color: [E]quipada/activa, [S]uelo, [D]ejada
        String s = it.state == ST_EQUIPPED ? (it.active ? "E" : "e") : it.state == ST_FLOOR ? "S" : it.state == ST_LEFT ? "D" : null;
        if (s == null) return;
        int col = it.state == ST_EQUIPPED ? 0xFFD25A : it.state == ST_FLOOR ? 0x7AC8F0 : 0x9AA0B0;
        g.rect(x, y, 9, 9, 0xFF101018, false);
        g.rect(x, y, 9, 1, 0xFF000000 | col, false);
        UI.small.draw(g, s, x + 2, y + 1, col, 1f);
    }

    private void cell(Platform.Gfx g, Item it, float x, float y, float s, boolean selected, boolean focusedCell) {
        int rc = RAR_RGB[it.rar];
        g.rect(x, y, s, s, 0xFF14141E, false);
        g.rect(x, y, s, 2, 0xFF000000 | rc, false);                                         // franja de rareza
        g.rect(x, y + s - 1, s, 1, rgba(rc, 110), false);
        g.rect(x, y, 1, s, rgba(rc, 110), false); g.rect(x + s - 1, y, 1, s, rgba(rc, 110), false);
        UI.iconC(g, it.icon, x + s / 2f, y + s / 2f + 1, 1f, 1f);
        Arsenal.rarityMark(g, x + 5, y + s - 5, Math.min(3, it.rar), rc);                  // rareza tambien con simbolo
        if (it.rar == 4) g.rect(x + 2, y + s - 2, 7, 1, 0xFF000000 | rc, false);
        stateBadge(g, it, x + s - 10, y + 3);
        if (it.maxLvl > 0 && it.lvl > 0 && (it.cat == C_BLESS ? it.lvl > 1 : it.lvl > 0)) {
            String lv = (it.cat == C_BLESS ? "" : "+") + it.lvl;
            g.rect(x + s - UI.small.width(lv) - 3, y + s - 10, UI.small.width(lv) + 2, 9, 0xCC000010, false);
            UI.small.draw(g, lv, x + s - UI.small.width(lv) - 2, y + s - 9, 0xFFFFE070, 1f);
        }
        if (it.isNew) { g.rect(x + 1, y + 3, 7, 9, 0xFFD02030, false); UI.small.draw(g, "!", x + 3, y + 3, 0xFFFFFF, 1f); }
        if (selected) {
            int c = focusedCell ? 0xFFFFE070 : 0x99FFE070;
            g.rect(x - 2, y - 2, s + 4, 1, c, false); g.rect(x - 2, y + s + 1, s + 4, 1, c, false);
            g.rect(x - 2, y - 2, 1, s + 4, c, false); g.rect(x + s + 1, y - 2, 1, s + 4, c, false);
        }
    }

    private void slotCard(Platform.Gfx g, Screen.Hit h, int k) {
        Item it = equip[k];
        boolean sel = focus == 1 && slot == k;
        boolean active = k == 0 ? !rs().secActive : rs().secActive;
        UI.panel(g, sel ? 1 : 0, h.x, h.y, h.w, h.h, 0.95f);
        String head = k == 0 ? "ARMA PRINCIPAL" : "ARMA SECUNDARIA";
        UI.small.draw(g, head, h.x + 6, h.y + 4, 0xFF9AA0B0, 1f);
        if (active && (k == 0 || it != null)) {
            String a = "EN USO";
            float aw = UI.small.width(a) + 8;
            g.rect(h.x + h.w - aw - 6, h.y + 3, aw, 10, 0xFF3A2C08, false);
            g.rect(h.x + h.w - aw - 6, h.y + 3, aw, 1, 0xFFFFD25A, false); g.rect(h.x + h.w - aw - 6, h.y + 12, aw, 1, 0xFFFFD25A, false);
            UI.small.draw(g, a, h.x + h.w - aw - 2, h.y + 4, 0xFFFFD25A, 1f);
        }
        if (it == null) {
            UI.small.draw(g, "Vacía · recoge un arma del suelo o de un cofre", h.x + 8, h.y + 20, 0xFF7A7A88, 1f);
            return;
        }
        int rc = RAR_RGB[it.rar];
        UI.iconC(g, it.icon, h.x + 20, h.y + 26, 1f, active ? 1f : 0.7f);
        g.rect(h.x + 8, h.y + 36, 24, 2, active ? 0xFFFFD25A : rgba(rc, 160), false);
        float tx = h.x + 38;
        UI.small.draw(g, UI.fitLabel(UI.small, it.name, h.w - 46), tx, h.y + 16, 0xFFF0E8E0, 1f);
        String line;
        if (k == 1) line = "Munición " + rs().secAmmo + "/" + Items.SEC_AMMO[rs().sec] + (rs().secLvl > 0 ? " · Nv +" + rs().secLvl : "");
        else line = rs().special != 0 ? Items.SP_NAME[rs().special] : "Sin mejora elemental";
        Arsenal.rarityMark(g, tx + 3, h.y + 31, Math.min(3, it.rar), rc);
        String full = (k == 1 ? RAR_ES[it.rar] + " · " : "") + line;
        String show = UI.small.width(full) <= h.w - 56 ? full : line;
        UI.small.draw(g, UI.fitLabel(UI.small, show, h.w - 56), tx + 9, h.y + 28, k == 1 && show == full ? rc : 0xFFB8B0B8, 1f);
    }

    void render(Platform.Gfx g, int w) {
        int h = ViewSize.h;
        if (w != lastW || h != lastH) layout(w);
        sc.dim(g, w, 0.9f);
        UI.panel(g, 0, 4, 3, w - 8, h - 6, 0.97f);
        for (Screen.Hit hb : sc.hits) {
            if (hb.tag >= 100 && hb.tag < 104) {
                int c = hb.tag - 100;
                sc.drawButton(g, hb);
                if (c == cat) { g.rect(hb.x + 2, hb.y + hb.h - 3, hb.w - 4, 2, 0xFFFFD25A, false); }
            }
        }
        UI.small.right(g, "INVENTARIO", w - 12, 11, UI.GOLD, 1f);
        // ranuras de equipo
        for (Screen.Hit hb : sc.hits) if (hb.tag >= 300 && hb.tag < 302) slotCard(g, hb, hb.tag - 300);
        // rejilla
        UI.panel(g, 0, gx, gy, gw, gh, 0.9f);
        if (items.isEmpty()) {
            String m = filter == 0 ? "No tienes nada en esta categoría todavía." : "Nada coincide con el filtro.";
            UI.small.drawWrapped(g, m, gx + 10, gy + gh / 2 - 10, (int) gw - 20, 0xFF9AA0B0, 1f);
        }
        for (Screen.Hit hb : sc.hits) {
            if (hb.tag >= 400) {
                int i = hb.tag - 400;
                cell(g, items.get(i), hb.x, hb.y, hb.w, focus == 0 && sel == i, focus == 0);
            }
        }
        int totalRows = (items.size() + cols - 1) / cols;
        if (totalRows > rows) {                                     // barra de desplazamiento + flechas
            float bx2 = gx + gw - 9, by2 = gy + 18, bh2 = gh - 52;
            g.rect(bx2, by2, 4, bh2, 0x55000000, false);
            float th = Math.max(8, bh2 * rows / totalRows), tp = by2 + (bh2 - th) * (scroll / (float) Math.max(1, totalRows - rows));
            g.rect(bx2, tp, 4, th, 0xFFB8A050, false);
            for (Screen.Hit hb : sc.hits) if (hb.tag == 210 || hb.tag == 211) UI.small.center(g, hb.tag == 210 ? "^" : "v", hb.x + hb.w / 2f, hb.y + 3, hb.disabled ? 0xFF555560 : 0xFFFFD25A, 1f);
        }
        UI.small.right(g, items.size() + " obj.", gx + gw - 16, gy + gh - 10, 0xFF7A7A88, 1f);
        // detalle
        UI.panel(g, 0, dx, dy, dw, dh, 0.95f);
        renderDetail(g);
        // pie
        for (Screen.Hit hb : sc.hits) if (hb.tag >= 200 && hb.tag < 203) sc.drawButton(g, hb);
        String[] legs = {"E equipada · S en el suelo · D dejada · ! nueva · +n mejora", "E equip. · S suelo · D dejada · ! nueva", "E equip. · S suelo · ! nueva", "! nueva"};
        float legMax = gw - 74;
        for (String lg : legs) if (UI.small.width(lg) <= legMax) { UI.small.draw(g, lg, gx + 8, gy + gh - 10, 0xFF8A8A98, 1f); break; }
        Screen.Hit ha = null; for (Screen.Hit hb : sc.hits) if (hb.tag == 220) ha = hb;
        if (ha != null) sc.drawButton(g, ha);
    }

    private void renderDetail(Platform.Gfx g) {
        Item it = cur();
        float x = dx + 8, y = dy + 6, w = dw - 16;
        if (it == null) { UI.small.drawWrapped(g, "Selecciona un objeto para ver su detalle.", x, y + 20, (int) w, 0xFF9AA0B0, 1f); return; }
        float bottom = dy + dh - (canActivate(it) ? 28 : 6);
        int rc = RAR_RGB[it.rar];
        RunState rs = rs();
        if (it.cat == C_WEAPONS && it.wid > 0) {
            float yy = ArsenalUI.sheet(g, x, y, w, it.wid, rs.sec != it.wid ? rs.sec : 0, 0);
            yy += 3;
            UI.small.draw(g, ST_NAME[it.state], x + 2, yy, it.state == ST_EQUIPPED ? 0xFFFFD25A : 0xFF7AC8F0, 1f); yy += ArsenalUI.lh() + 1;
            if (it.state == ST_EQUIPPED) { UI.small.draw(g, UI.fitLabel(UI.small, "Munición " + rs.secAmmo + "/" + Items.SEC_AMMO[it.wid] + (rs.secLvl > 0 ? " · Nv +" + rs.secLvl + "/3" : ""), w - 4), x + 2, yy, 0xFFB8B0B8, 1f); yy += ArsenalUI.lh() + 1; }
            else if (it.state == ST_FLOOR) { UI.small.draw(g, UI.fitLabel(UI.small, "Recógela con [Interactuar]", w - 4), x + 2, yy, 0xFFB8B0B8, 1f); yy += ArsenalUI.lh() + 1; }
            else UI.small.drawWrappedMax(g, "Quedó en otra sala (no se puede recoger)", x + 2, yy, (int) w - 4, 0xFFB8B0B8, 1f, ArsenalUI.lh(), 2);
            return;
        }
        // cabecera generica
        UI.iconC(g, it.icon, x + 9, y + 9, 1f, 1f);
        UI.small.draw(g, UI.fitLabel(UI.small, it.name, w - 24), x + 22, y + 1, 0xFFF0E8E0, 1f);
        Arsenal.rarityMark(g, x + 26, y + 15, Math.min(3, it.rar), rc);
        UI.small.draw(g, it.kind == 1 || it.kind == 5 ? it.sub : RAR_ES[it.rar], x + 34, y + 11, it.kind == 1 || it.kind == 5 ? 0xFFB8B0B8 : rc, 1f);
        float yy = y + 25;
        String body = "";
        List<String> extra = new ArrayList<>();
        switch (it.kind) {
            case 1: body = rs.cls.desc; extra.add("Arma: " + rs.cls.weapon); extra.add(rs.secActive ? "En espera (usas la secundaria)" : "En uso"); if (rs.weaponLvl > 0) extra.add("Mejora de la forja: Nv " + rs.weaponLvl); if (rs.special != 0) extra.add("Mejora activa: " + Items.SP_NAME[rs.special]); break;
            case 2: body = Items.SH_DESC[it.wid]; break;
            case 3: body = Items.GR_DESC[it.wid]; extra.add("Te quedan " + rs.grenCount); if (rs.grenLvl > 0) extra.add("Mejora: Nv +" + rs.grenLvl + "/3"); break;
            case 4: body = Items.SP_DESC[it.wid]; break;
            case 5: body = "Curan vida cuando los usas. Los recargas en tiendas y con algunos objetos."; extra.add("Llevas " + rs.potions + " de " + rs.stats.potionsMax); break;
            case 6: body = Events.PACTS[it.wid].pro; extra.add("Coste: " + Events.PACTS[it.wid].con); break;
            case 7: body = "Reliquia de " + BossDef.ALL[it.wid].name + ". La conservas en la sala de trofeos."; break;
            case 8: body = Companions.PASSIVE[it.wid]; break;
            case 9: body = StartBlessing.get(it.wid).pro; extra.add("Coste: " + StartBlessing.get(it.wid).con); break;
            default:
                if (it.bid >= 0) {
                    Blessing b = Blessing.ALL[it.bid];
                    body = b.desc;
                    extra.add("Nivel " + rs.bless[it.bid] + "/" + b.max + " · " + it.sub);
                }
        }
        yy += wrapClip(g, body, x + 2, yy, (int) w - 4, bottom - yy - 24, 0xFFE8E0E0);
        yy += 3;
        for (String e : extra) {
            if (yy + ArsenalUI.lh() > bottom) break;
            yy += wrapClip(g, e, x + 2, yy, (int) w - 4, bottom - yy, 0xFFFFD25A) + 1;
        }
    }

    /** Texto con ajuste de linea que nunca se sale del espacio disponible (corta con "…"). Devuelve el alto usado. */
    private float wrapClip(Platform.Gfx g, String s, float x, float y, int w, float maxH, int col) {
        int maxL = Math.max(1, (int) (maxH / ArsenalUI.lh()));
        return UI.small.drawWrappedMax(g, s, x, y, w, col, 1f, ArsenalUI.lh(), maxL);
    }
}
