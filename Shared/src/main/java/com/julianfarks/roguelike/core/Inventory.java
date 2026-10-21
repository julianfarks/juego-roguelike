package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/**
 * Pantalla de inventario de la run (overlay OV_INV de RunScreen). Solo muestra el estado REAL de esta partida (RunState):
 * nada de lo que se ve aqui es la coleccion permanente. Categorias: armas, bendiciones, reliquias y especiales, objetos.
 * Se maneja con teclado, mando, raton y tactil; no toca el combate (el juego esta en pausa mientras esta abierto).
 */
final class Inventory {
    static final int C_WEAPONS = 0, C_BLESS = 1, C_RELICS = 2, C_OBJECTS = 3, C_UPGR = 4, C_COUNT = 5;
    static final String[] CAT_NAME = {"Armas", "Bendiciones", "Reliquias", "Objetos", "Mejoras"};
    static final String[] RAR_ES = {"Común", "Poco común", "Rara", "Épica", "Legendaria"};
    static final String[] SORT_NAME = {"Rareza", "Nombre"};
    static final String[] FILTER_NAME = {"Todas", "Nuevas", "Común", "Poco común", "Rara", "Épica", "Legendaria"};
    static final int[] RAR_RGB = {0xC8CCD8, 0x6AE08A, 0x6AA8FF, 0xC070FF, 0xFFB030};
    static final String[] RELIC_ICON = {"r_rey_exanime", "r_coloso_magma", "r_reina_escarcha", "r_devorador_vacio", "r_ent_ancestral", "r_titan_tormenta", "r_matriarca_sangre", "r_guardian_eclipse"};
    static final int ST_OWNED = 0, ST_EQUIPPED = 1, ST_FLOOR = 2, ST_LEFT = 3;
    static final String[] ST_NAME = {"Guardada", "Equipada", "En el suelo de esta sala", "Dejada atrás en otra sala"};   // el inventario solo lista lo poseido (0 y 1); 2 y 3 quedan para compatibilidad

    static final class Item {
        int cat, rar, state, lvl, maxLvl, wid = -1, bid = -1, kind;       // kind: 0 normal, 1 arma principal, 2 escudo, 3 granada, 4 especial, 5 pocion, 6 pacto, 7 reliquia, 8 compañero, 9 bendicion inicial, 10 mejora de estadistica, 11 sinergia
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

    /** Cuantas mejoras distintas lleva la run (estadisticas + mejoras del arma principal). */
    static int upgradeCount(RunState rs) {
        int n = 0;
        for (int i = 1; i < Items.SP_COUNT; i++) if (rs.spLvl[i] > 0) n++;
        for (int i = 0; i < ChestLoot.N; i++) if (rs.cbLvl[i] > 0 || rs.cb[i] != 0) n++;
        return n;
    }

    /** Resumen de las mejoras del arma principal: "Filo Ígneo Nv 2 · Daga Venenosa" (o null si no hay). */
    static String specialsLine(RunState rs) {
        StringBuilder sb = new StringBuilder();
        for (int i = 1; i < Items.SP_COUNT; i++) if (rs.spLvl[i] > 0) { if (sb.length() > 0) sb.append(" · "); sb.append(Items.SP_NAME[i]); if (rs.spLvl[i] > 1) sb.append(" Nv ").append(rs.spLvl[i]); }
        return sb.length() == 0 ? null : sb.toString();
    }

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
        // SOLO las armas que posees en esta partida (bolsa): nada de armas vistas, del suelo o dejadas atras
        rs.syncBag();
        for (int id : rs.bag) {
            int st = rs.sec == id ? ST_EQUIPPED : ST_OWNED;
            Item it = mk(C_WEAPONS, "w:" + id, Items.SEC_NAME[id], Items.SEC_ICON[id], Items.SEC_RAR[id], st);
            it.wid = id; it.active = rs.sec == id && rs.secActive;
            it.lvl = rs.lvlOf(id); it.maxLvl = 3;
            if (st == ST_EQUIPPED) equip[1] = it;
            it.sub = st == ST_EQUIPPED ? "Arma secundaria" : "Arma guardada";
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
        // ---- mejoras acumulables: todas a la vez, cada una con su nivel (nunca se sustituyen entre si)
        if (rs.special > 0 && rs.special < Items.SP_COUNT && rs.spLvl[rs.special] == 0) rs.spLvl[rs.special] = 1;    // especial fijada a mano (partidas antiguas): nivel 1
        for (int sp = 1; sp < Items.SP_COUNT; sp++) if (rs.spLvl[sp] > 0) {
            Item it = mk(C_UPGR, "u:sp" + sp, Items.SP_NAME[sp], ChestLoot.SP_ICON[sp], ChestLoot.SP_RAR[sp], ST_OWNED);
            it.kind = 4; it.wid = sp; it.lvl = rs.spLvl[sp]; it.maxLvl = Items.SP_MAXLVL; it.sub = "Mejora del arma principal"; it.active = true;
            all.add(it);
        }
        for (int i = 0; i < Synergy.COUNT; i++) if (Synergy.active(rs, i)) {           // sinergias activas entre mejoras
            Item it = mk(C_UPGR, "y:" + i, Synergy.NAME[i], Synergy.ICON[i], 3, ST_OWNED);
            it.kind = 11; it.wid = i; it.sub = "Sinergia · " + Synergy.REQ[i]; it.active = true;
            all.add(it);
        }
        for (int i = 0; i < ChestLoot.N; i++) if (rs.cbLvl[i] > 0 || rs.cb[i] != 0) {
            int lvv = Math.max(rs.cbLvl[i], rs.cb[i] != 0 ? 1 : 0);
            Item it = mk(C_UPGR, "u:st" + i, ChestLoot.S_NAME[i], ChestLoot.S_ICON[i], Math.min(4, Math.max(0, lvv - 1)), ST_OWNED);
            it.kind = 10; it.wid = i; it.lvl = lvv; it.maxLvl = ChestLoot.maxLvl(i); it.sub = "Mejora de estadística";
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
        rs.syncBag();
        for (int id : rs.bag) rs.seen.add("w:" + id);
        for (Blessing b : Blessing.ALL) if (rs.bless[b.id] > 0) rs.seen.add("b:" + b.id);
        for (int i = 0; i < 8; i++) if (rs.relicsThisRun[i]) rs.seen.add("r:" + i);
        for (int i = 0; i < Events.PACTS.length; i++) if (rs.pacts[i] > 0) rs.seen.add("p:" + i);
        if (rs.startBless >= 0) rs.seen.add("s:" + rs.startBless);
        if (rs.companion >= 0) rs.seen.add("c:" + rs.companion);
        rs.seen.add("o:sh" + rs.shield);
        if (rs.gren != 0) rs.seen.add("o:gr" + rs.gren);
        if (rs.special != 0) rs.seen.add("o:sp" + rs.special);
        for (int sp = 1; sp < Items.SP_COUNT; sp++) if (rs.spLvl[sp] > 0) rs.seen.add("u:sp" + sp);
        for (int i = 0; i < ChestLoot.N; i++) if (rs.cbLvl[i] > 0 || rs.cb[i] != 0) rs.seen.add("u:st" + i);
        for (int i = 0; i < Synergy.COUNT; i++) if (Synergy.active(rs, i)) rs.seen.add("y:" + i);
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
        float bw = Math.min(126, (w - pad * 2 - 12) / 3f);
        sc.add(pad, fy, bw, fh, "Orden: " + SORT_NAME[sort], this::cycleSort).tag = 200;
        sc.add(pad + bw + 6, fy, bw, fh, "Filtro: " + FILTER_NAME[filter], this::cycleFilter).tag = 201;
        sc.add(w - pad - bw, fy, bw, fh, "Volver al juego", sc::invClose).tag = 202;
        // ranuras de equipo
        float ey = 28, eh = 42;
        float ew = (w - pad * 2 - 6) / 2f;
        for (int k = 0; k < 2; k++) {
            final int kk = k;
            Screen.Hit he = sc.add(pad + k * (ew + 6), ey, ew, eh, null, () -> { focus = 1; slot = kk; dwell = 0; });
            he.tag = 300 + k; he.plain = true;
        }
        // zonas: rejilla a la izquierda y detalle a la derecha
        float by = ey + eh + 6;
        float bh = fy - 5 - by;
        dw = Math.max(170, Math.min(250, w * 0.46f));
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
        {
            Screen.Hit du = sc.add(dx + dw - 13, dy + 3, 11, 14, "^", () -> dscroll(-18)); du.tag = 230; du.plain = true;
            Screen.Hit dd = sc.add(dx + dw - 13, dy + dh - 44, 11, 14, "v", () -> dscroll(18)); dd.tag = 231; dd.plain = true;
        }
        // accion del detalle
        Item it = cur();
        boolean ca = it != null && canActivate(it), cd = it != null && canDrop(it);
        if (ca && cd) {
            float bw2 = (dw - 16 - 4) * 0.62f;
            Screen.Hit ha = sc.add(dx + 8, dy + dh - 24, bw2, 18, UI.fitLabel(UI.small, activateLabel(it), bw2 - 8), this::activate); ha.tag = 220;
            Screen.Hit hd = sc.add(dx + 8 + bw2 + 4, dy + dh - 24, dw - 16 - bw2 - 4, 18, "Soltar", this::dropSel); hd.tag = 221;
        } else if (ca) {
            Screen.Hit ha = sc.add(dx + 8, dy + dh - 24, dw - 16, 18, activateLabel(it), this::activate); ha.tag = 220;
        } else if (cd) {
            Screen.Hit hd = sc.add(dx + 8, dy + dh - 24, dw - 16, 18, "Soltar al suelo", this::dropSel); hd.tag = 221;
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
        if (it.wid <= 0) return false;
        if (rs().sec == it.wid) return !rs().secActive;
        return rs().owns(it.wid);                      // guardada: se puede equipar en cualquier momento
    }

    String activateLabel(Item it) { return it.kind == 1 ? "Usar arma principal" : rs().sec == it.wid ? "Usar esta arma" : "Equipar"; }

    /** Soltar al suelo un arma poseida (deja hueco en la bolsa; se puede volver a recoger en esta sala). */
    boolean canDrop(Item it) {
        return sc.lv != null && sc.lv.pl.alive && it.cat == C_WEAPONS && it.kind != 1 && it.wid > 0 && rs().owns(it.wid);
    }

    private void reselect(String key) {
        rebuild();
        for (Item x : items) if (x.key.equals(key)) { sel = x.idx; focus = 0; }
        clampScroll();
    }

    void activate() {
        Item it = cur();
        if (it == null || !canActivate(it)) { Snd.sfx("ui_error", 0.6f); return; }
        String key = it.key;
        if (it.kind == 1 || rs().sec == it.wid) { if (Arsenal.swap(sc.lv, sc.lv.pl)) Snd.sfx("ui_confirm", 0.8f); }
        else if (Arsenal.switchTo(rs(), it.wid)) {            // la que llevabas queda guardada con su municion y nivel
            sc.lv.pl.swapIcon = Items.SEC_ICON[it.wid]; sc.lv.pl.swapAnimT = 0.32f;
            Snd.sfx("ui_confirm", 0.8f);
        }
        reselect(key); relayout();
    }

    void dropSel() {
        Item it = cur();
        if (it == null || !canDrop(it)) { Snd.sfx("ui_error", 0.6f); return; }
        Prop p = Arsenal.dropOwned(sc.lv, it.wid);
        if (p != null) { p.pickLock = 0.7f; Snd.sfx("ui_back", 0.7f); }
        rebuild(); relayout();
    }

    // ================================================================ teclas
    void key(int code) {
        int n = items.size();
        if (code == 'Q') { setCat((cat + C_COUNT - 1) % C_COUNT); return; }
        if (code == 'E') { setCat((cat + 1) % C_COUNT); return; }
        if (code == 33) { dscroll(-48); return; }
        if (code == 34 || code == 'K') { dscroll(48); return; }
        if (code == 'F') { cycleFilter(); return; }
        if (code == 'O') { cycleSort(); return; }
        if (code == 27 || code == 9) { sc.invClose(); return; }
        if (code == 10 || code == 32 || code == 'J') { Item it = cur(); if (it != null && it.isNew) markSeen(it); if (it != null && canActivate(it)) activate(); return; }
        if (code == 'X' || code == 127) { Item it = cur(); if (it != null && canDrop(it)) dropSel(); return; }
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
            String lv = it.cat == C_BLESS ? "" + it.lvl : it.cat == C_UPGR ? (it.lvl >= it.maxLvl ? "MAX" : "Nv" + it.lvl) : "+" + it.lvl;
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
        String head = k == 0 ? "ARMA PRINCIPAL" : "ARMA SECUNDARIA · " + rs().bag.size() + "/" + RunState.WEAPON_BAG;
        UI.small.draw(g, head, h.x + 6, h.y + 4, 0xFF9AA0B0, 1f);
        if (active && (k == 0 || it != null)) {
            float aw = UI.tag(g, "EN USO", 0, 0, 0xFFD25A, true, false);
            UI.tag(g, "EN USO", h.x + h.w - aw - 5, h.y + 3, 0xFFD25A, true, true);
        }
        if (it == null) {
            UI.small.drawWrappedMax(g, rs().bag.isEmpty() ? "Vacía · recoge un arma del suelo o de un cofre" : "Ninguna equipada · elige una de tus armas", h.x + 8, h.y + 16, (int) h.w - 16, 0xFF7A7A88, 1f, ArsenalUI.lh(), 2);
            return;
        }
        int rc = RAR_RGB[it.rar];
        UI.iconC(g, it.icon, h.x + 20, h.y + 26, 1f, active ? 1f : 0.7f);
        g.rect(h.x + 8, h.y + 36, 24, 2, active ? 0xFFFFD25A : rgba(rc, 160), false);
        float tx = h.x + 38;
        UI.small.draw(g, UI.fitLabel(UI.small, it.name, h.w - 46), tx, h.y + 16, 0xFFF0E8E0, 1f);
        String line;
        if (k == 1) line = Items.infinite(rs().sec) ? "Sin munición (ilimitada)" : "Munición " + (Arsenal.hasMag(rs().sec) ? Arsenal.ammoLabel(rs()) + " (cargador/reserva)" : rs().secAmmo + "/" + Items.SEC_AMMO[rs().sec]) + (rs().secLvl > 0 ? " · Nv +" + rs().secLvl : "");
        else { String sl = specialsLine(rs()); line = sl != null ? sl : "Sin mejora elemental"; }
        Arsenal.rarityMark(g, tx + 3, h.y + 31, Math.min(3, it.rar), rc);
        String full = (k == 1 ? RAR_ES[it.rar] + " · " : "") + line;
        String shortL = k == 1 ? (Items.infinite(rs().sec) ? "Ilimitada" : "Munición " + (Arsenal.hasMag(rs().sec) ? Arsenal.ammoLabel(rs()) : rs().secAmmo + "/" + Items.SEC_AMMO[rs().sec]))
                : (Items.specialsOwned(rs()) > 1 ? Items.specialsOwned(rs()) + " mejoras" : rs().special != 0 ? Items.SP_NAME[rs().special] : "Sin mejora");
        // de la version mas completa a la mas corta: se usa la primera que cabe entera (nada se recorta)
        String show = UI.small.width(full) <= h.w - 56 ? full : UI.small.width(line) <= h.w - 56 ? line : shortL;
        UI.small.draw(g, UI.fitLabel(UI.small, show, h.w - 56), tx + 9, h.y + 28, k == 1 && show == full ? rc : 0xFFB8B0B8, 1f);
    }

    void render(Platform.Gfx g, int w) {
        int h = ViewSize.h;
        if (w != lastW || h != lastH) layout(w);
        sc.dim(g, w, 0.9f);
        UI.panel(g, 0, 4, 3, w - 8, h - 6, 0.97f);
        for (Screen.Hit hb : sc.hits) {
            if (hb.tag >= 100 && hb.tag < 100 + C_COUNT) {
                int c = hb.tag - 100;
                boolean on = c == cat;
                UI.panel(g, on ? 1 : 0, hb.x, hb.y, hb.w, hb.h, on ? 1f : 0.7f);
                UI.small.center(g, UI.fitLabel(UI.small, CAT_NAME[c], hb.w - 8), hb.x + hb.w / 2f, hb.y + (hb.h - UI.small.ch) / 2f, on ? UI.GOLD : 0xFF8A8A98, 1f);
                if (on) { g.rect(hb.x + 3, hb.y + hb.h - 3, hb.w - 6, 2, 0xFFFFD25A, false); g.rect(hb.x + 3, hb.y + hb.h - 5, hb.w - 6, 2, 0x33FFD25A, false); }
                if (catNew[c] > 0) { g.rect(hb.x + hb.w - 7, hb.y + 2, 5, 5, 0xFFD02030, false); }
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
        UI.small.right(g, cat == C_WEAPONS ? rs().bag.size() + "/" + RunState.WEAPON_BAG : items.size() + " obj.", gx + gw - 16, gy + gh - 13, 0xFF7A7A88, 1f);
        // detalle
        UI.panel(g, 0, dx, dy, dw, dh, 0.95f);
        renderDetail(g);
        // pie
        for (Screen.Hit hb : sc.hits) if (hb.tag >= 200 && hb.tag < 203) sc.drawButton(g, hb);
        String[] legs = {"E equipada · ! nueva · +n nivel · X soltar", "E equipada · ! nueva · +n nivel", "E equip. · ! nueva", "! nueva"};
        float legMax = gw - 74;
        for (String lg : legs) if (UI.small.width(lg) <= legMax) { UI.small.draw(g, lg, gx + 8, gy + gh - 13, 0xFF8A8A98, 1f); break; }
        for (Screen.Hit hb : sc.hits) if (hb.tag == 220 || hb.tag == 221) sc.drawButton(g, hb);
    }

    int clipN;     // pruebas: cuantas veces el detalle tuvo que recortar una descripcion (debe ser 0)

    private String catTag(Item it) {
        switch (it.kind) {
            case 1: return "Principal";
            case 2: return "Escudo";
            case 3: return "Granada";
            case 4: return "Mejora de arma";
            case 5: return "Consumible";
            case 6: return "Pacto";
            case 7: return "Reliquia";
            case 9: return "Bendición inicial";
            case 10: return "Mejora";
            case 11: return "Sinergia";
            default: return it.cat == C_WEAPONS ? "Secundaria" : it.sub;
        }
    }

    /** Cabecera del detalle: icono enmarcado, nombre ajustado (hasta 2 lineas) y etiquetas de rareza, categoria y estado. Devuelve la y siguiente. */
    private float header(Platform.Gfx g, Item it, float x, float y, float w) {
        RunState rs = rs();
        int rc = RAR_RGB[it.rar], lh = ArsenalUI.lh();
        g.rect(x, y, 24, 24, 0xFF14141E, false);
        g.rect(x, y, 24, 1, 0xFF000000 | rc, false); g.rect(x, y + 23, 24, 1, rgba(rc, 130), false); g.rect(x, y, 1, 24, rgba(rc, 130), false); g.rect(x + 23, y, 1, 24, rgba(rc, 130), false);
        UI.iconC(g, it.icon, x + 12, y + 12, 1f, 1f);
        float nx = x + 29;
        int nl = Math.max(1, Math.min(2, UI.small.wrapLines(it.name, (int) (w - 29))));
        UI.small.drawWrappedMax(g, it.name, nx, y + (nl == 1 ? 5 : 1), (int) (w - 29), 0xFFF0E8E0, 1f, lh, 2);
        float ty = y + Math.max(26, nl * lh + 3), tx = x;
        String[] tg = new String[3]; int[] tc = new int[3]; boolean[] tf = new boolean[3];
        tg[0] = RAR_ES[it.rar]; tc[0] = rc;
        tg[1] = catTag(it); tc[1] = 0x9AA0B0;
        if (it.kind == 1) { tg[2] = rs.secActive ? "EN ESPERA" : "EN USO"; tc[2] = rs.secActive ? 0x9AA0B0 : 0xFFD25A; tf[2] = !rs.secActive; }
        else if (it.state == ST_EQUIPPED) { tg[2] = it.active ? "EN USO" : "EQUIPADA"; tc[2] = 0xFFD25A; tf[2] = it.active; }
        else if (it.cat == C_WEAPONS && it.state == ST_OWNED) { tg[2] = "GUARDADA"; tc[2] = 0x9AC8E8; }
        else if (it.state == ST_FLOOR) { tg[2] = "EN EL SUELO"; tc[2] = 0x7AC8F0; }
        else if (it.state == ST_LEFT) { tg[2] = "DEJADA"; tc[2] = 0x9AA0B0; }
        for (int k = 0; k < 3; k++) {
            if (tg[k] == null || tg[k].isEmpty()) continue;
            float tw = UI.tag(g, tg[k], 0, 0, 0, false, false);
            if (tx + tw > x + w && tx > x) { tx = x; ty += UI.tagH() + 1; }
            UI.tag(g, tg[k], tx, ty, tc[k], k == 2 && tf[k], true);
            tx += tw + 3;
        }
        UI.divider(g, x, ty + UI.tagH() + 4, w);
        return ty + UI.tagH() + 8;
    }

    int dScroll, dMax; String dKey = "";      // desplazamiento del detalle (px) y maximo; se reinicia al cambiar de elemento

    void dscroll(int px) {
        int n = Math.max(0, Math.min(dMax, dScroll + px));
        if (px > 0 && dScroll >= dMax && dMax > 0) n = 0;       // al llegar al final, la siguiente pagina vuelve al principio
        if (n != dScroll) { dScroll = n; Snd.sfx("ui_hover", 0.4f); }
    }

    private void renderDetail(Platform.Gfx g) {
        Item it = cur();
        float x = dx + 8, w = dw - 16 - (dMax > 0 ? 8 : 0);
        if (it == null) { UI.small.drawWrapped(g, "Selecciona un objeto para ver su detalle.", x, dy + 26, (int) w, 0xFF9AA0B0, 1f); return; }
        String key = it.key + "/" + (rs().secActive ? 1 : 0) + "/" + it.state;
        if (!key.equals(dKey)) { dKey = key; dScroll = 0; }
        dScroll = Math.max(0, Math.min(dMax, dScroll));
        boolean actBtn = false; for (Screen.Hit hb : sc.hits) if (hb.tag == 220 || hb.tag == 221) actBtn = true;       // el boton realmente colocado (no el estado actual)
        float top = dy + 6, viewBottom = dy + dh - (actBtn ? 28 : 5);
        g.clipBegin(dx + 2, dy + 3, dw - 4, viewBottom - (dy + 3));
        TextAudit.clip(dx + 2, dy + 3, dw - 4, viewBottom - (dy + 3));
        float end = drawDetail(g, it, x, top - dScroll, w, Float.MAX_VALUE) + dScroll;
        g.clipEnd();
        TextAudit.unclip();
        dMax = Math.max(0, (int) Math.ceil(end - viewBottom + 2));
        if (dMax > 0) clipN++;                                   // informativo (pruebas): este elemento necesita desplazamiento
        if (dMax > 0) {                                          // barra de desplazamiento y flechas
            float bx = dx + dw - 8, by = dy + 16, bh = viewBottom - by - 14;
            g.rect(bx, by, 3, bh, 0x55000000, false);
            float th = Math.max(8, bh * (viewBottom - top) / (end - top)), tp = by + (bh - th) * (dScroll / (float) dMax);
            g.rect(bx, tp, 3, th, 0xFFB8A050, false);
            for (Screen.Hit hb : sc.hits) if (hb.tag == 230 || hb.tag == 231) UI.small.center(g, hb.tag == 230 ? "^" : "v", hb.x + hb.w / 2f, hb.y + 3, (hb.tag == 230 ? dScroll <= 0 : dScroll >= dMax) ? 0xFF555560 : 0xFFFFD25A, 1f);
        }
    }

    /** Dibuja el detalle completo desde y; devuelve la y final del contenido. */
    private float drawDetail(Platform.Gfx g, Item it, float x, float y, float w, float bottom) {
        RunState rs = rs();
        int lh = ArsenalUI.lh();
        float yy = header(g, it, x, y, w);
        if (it.cat == C_WEAPONS && it.wid > 0) {
            yy = ArsenalUI.sheet(g, x, yy, w, it.wid, rs.sec != it.wid ? rs.sec : 0, 0, bottom, false) + 3;
            if (it.state == ST_EQUIPPED) { String am = (Items.infinite(it.wid) ? "Sin munición (ilimitada)" : (Arsenal.hasMag(it.wid) ? "Munición " + Arsenal.ammoLabel(rs) + " (cargador/reserva)" : "Munición " + rs.secAmmo + "/" + Items.SEC_AMMO[it.wid])) + (rs.secLvl > 0 ? " · Nv +" + rs.secLvl + "/3" : "");
                if (UI.small.width(am) > w - 4) am = (Items.infinite(it.wid) ? "Ilimitada" : "Munición " + (Arsenal.hasMag(it.wid) ? Arsenal.ammoLabel(rs) : rs.secAmmo + "/" + Items.SEC_AMMO[it.wid])) + (rs.secLvl > 0 ? " · Nv +" + rs.secLvl : "");
                yy += UI.small.drawWrapped(g, am, x + 2, yy, (int) w - 4, 0xFFB8B0B8, 1f, lh) + 1; }
            else if (it.state == ST_OWNED) {
                int a = rs.bAmmo[it.wid], lv2 = rs.bLvl[it.wid];
                String am = (Items.infinite(it.wid) ? "Sin munición (ilimitada)" : "Munición " + a + "/" + Items.SEC_AMMO[it.wid]) + (lv2 > 0 ? " · Nv +" + lv2 + "/3" : "");
                yy += UI.small.drawWrapped(g, am, x + 2, yy, (int) w - 4, 0xFFB8B0B8, 1f, lh) + 1;
                yy += UI.small.drawWrappedMax(g, "Guardada en tu inventario: equípala cuando quieras; conserva su munición y su nivel.", x + 2, yy, (int) w - 4, 0xFF9AC8E8, 1f, lh, 4) + 1;
            }
            else if (it.state == ST_FLOOR) { UI.small.draw(g, UI.fitLabel(UI.small, "Recógela con [Interactuar]", w - 4), x + 2, yy, 0xFFB8B0B8, 1f); yy += lh + 1; }
            else if (it.state == ST_LEFT) yy += UI.small.drawWrappedMax(g, "Quedó en otra sala", x + 2, yy, (int) w - 4, 0xFFB8B0B8, 1f, lh, 2);
            return yy;
        }
        String body = "";
        List<String> extra = new ArrayList<>();
        switch (it.kind) {
            case 1: body = rs.cls.desc; if (rs.weaponLvl > 0) extra.add("Mejora de la forja: Nv " + rs.weaponLvl); for (int sp = 1; sp < Items.SP_COUNT; sp++) if (rs.spLvl[sp] > 0) extra.add("Mejora activa: " + Items.SP_NAME[sp] + " Nv " + rs.spLvl[sp]); break;
            case 2: body = Items.SH_DESC[it.wid]; break;
            case 3: body = Items.GR_DESC[it.wid]; extra.add("Te quedan " + rs.grenCount); if (rs.grenLvl > 0) extra.add("Mejora: Nv +" + rs.grenLvl + "/3"); break;
            case 4: body = Items.SP_DESC[it.wid]; extra.add("Nivel " + it.lvl + "/" + it.maxLvl + (it.lvl >= it.maxLvl ? " (máximo)" : "")); extra.add("Efecto acumulado: " + Items.spEffect(it.wid, it.lvl)); extra.add("Se suma a tus otras mejoras: nunca sustituye al arma ni a otra mejora."); break;
            case 11: body = Synergy.DESC[it.wid]; extra.add("Requiere: " + Synergy.REQ[it.wid]); extra.add("Activa: tienes las dos mejoras."); break;
            case 10: body = ChestLoot.S_DESC[it.wid]; extra.add("Nivel " + it.lvl + "/" + it.maxLvl + (it.lvl >= it.maxLvl ? " (máximo)" : "")); extra.add("Efecto acumulado: " + ChestLoot.total(it.wid, rs.cb[it.wid])); break;
            case 5: body = "Curan vida cuando los usas. Los recargas en tiendas y con algunos objetos."; extra.add("Llevas " + rs.potions + " de " + rs.stats.potionsMax); break;
            case 6: body = Events.PACTS[it.wid].pro; extra.add("Coste: " + Events.PACTS[it.wid].con); break;
            case 7: body = "Reliquia de " + BossDef.ALL[it.wid].name + ". La conservas en la sala de trofeos."; break;
            case 8: body = Companions.PASSIVE[it.wid]; extra.add(Companions.KIND[it.wid]); break;
            case 9: body = StartBlessing.get(it.wid).pro; extra.add("Coste: " + StartBlessing.get(it.wid).con); break;
            default:
                if (it.bid >= 0) {
                    Blessing b = Blessing.ALL[it.bid];
                    body = b.desc;
                    extra.add("Nivel " + rs.bless[it.bid] + "/" + b.max);
                }
        }
        yy += UI.small.drawWrappedMax(g, body, x + 2, yy, (int) w - 4, 0xFFE8E0E0, 1f, lh, 99);
        if (extra.isEmpty()) return yy;
        yy += 2;
        UI.divider(g, x, yy + 1, w); yy += 5;
        for (String e : extra) yy += UI.small.drawWrappedMax(g, e, x + 2, yy, (int) w - 4, 0xFFFFD25A, 1f, lh, 99) + 1;
        return yy;
    }

    /** Texto con ajuste de linea que nunca se sale del espacio disponible (corta con "…"). Devuelve el alto usado. */
    private float wrapClip(Platform.Gfx g, String s, float x, float y, int w, float maxH, int col) {
        int maxL = Math.max(1, (int) (maxH / ArsenalUI.lh()));
        if (UI.small.wrapLines(s, w) > maxL) clipN++;
        return UI.small.drawWrappedMax(g, s, x, y, w, col, 1f, ArsenalUI.lh(), maxL);
    }
}
