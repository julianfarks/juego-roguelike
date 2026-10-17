package com.julianfarks.roguelike.core;

import java.util.List;

/**
 * Tienda de cosmeticos. Muestra los dos saldos por separado (almas = moneda normal, gemas = premium moradas).
 * Distingue articulos EARNED (se consiguen jugando), PREMIUM (se compran con gemas) y STORE (Google Play, futuro: aun sin botones).
 * No hay compras con dinero real ni anuncios: con el catalogo oficial vacio solo se muestra el estado vacio honesto.
 */
final class ShopScreen extends Screen {
    private final Screens.TitleBg bg = new Screens.TitleBg();
    private int page;                    // primera fila visible
    private String toast = ""; private float toastT;
    private static final int ROWS = 4;

    ShopScreen(Game g) { super(g); }

    @Override void enter() { Snd.music("mus_sanctuary", true); layout(); }
    @Override boolean back() { game.go(new Ops(game)); return true; }
    @Override void update(float dt) { bg.update(dt, W()); t += dt; if (toastT > 0) toastT -= dt; }

    private ClassDef hero() { int id = Save.S.lastClass; if (id < 0 || id > 9 || !Save.S.classUnlocked[id]) id = 0; return ClassDef.ALL[id]; }

    @Override void layout() {
        hits.clear();
        int w = W();
        float pw = Math.min(w - 24, 440), px = w / 2f - pw / 2f;
        List<Cosmetics.Item> cat = Cosmetics.catalog();
        ClassDef hero = hero();
        for (int i = 0; i < ROWS; i++) {
            int idx = page + i;
            if (idx >= cat.size()) break;
            final Cosmetics.Item it = cat.get(idx);
            float y = 70 + i * 34;
            String lab; boolean dis = false;
            if (Cosmetics.equipped(hero) == it) { lab = "Quitar"; }
            else if (Cosmetics.owns(it.id)) { lab = it.fits(hero) ? "Equipar" : "No sirve"; dis = !it.fits(hero); }
            else if (it.source == Cosmetics.Source.PREMIUM) { lab = it.priceGems + " gemas"; dis = !Wallet.canSpend(it.priceGems); }
            else if (it.source == Cosmetics.Source.EARNED) { lab = "Jugando"; dis = true; }
            else { lab = "Próximamente"; dis = true; }
            Hit h = add(px + pw - 94, y + 2, 86, 26, lab, () -> act(it));
            h.disabled = dis;
        }
        if (cat.size() > ROWS) {
            add(px + 8, 212, 40, 22, "<", () -> { page = Math.max(0, page - ROWS); layout(); });
            add(px + 52, 212, 40, 22, ">", () -> { if (page + ROWS < cat.size()) page += ROWS; layout(); });
        }
        if (Save.S.devUnlocked) add(px + pw - 150, 212, 142, 22, "+50 gemas (PRUEBA)", () -> { Wallet.devGrant(50); toast = "Gemas de prueba: solo esta sesión"; toastT = 2f; layout(); });
        add(w / 2f - 40, 244, 80, 22, "Volver", () -> back());
    }

    private void act(Cosmetics.Item it) {
        ClassDef hero = hero();
        if (Cosmetics.equipped(hero) == it) { Cosmetics.equip(hero, ""); toast = "Aspecto original"; }
        else if (Cosmetics.owns(it.id)) { if (Cosmetics.equip(hero, it.id)) toast = it.name + " equipado en " + hero.name; }
        else if (Cosmetics.buy(it.id)) { Cosmetics.equip(hero, it.fits(hero) ? it.id : ""); toast = "Comprado: " + it.name; Snd.sfx("ui_confirm", 0.9f); }
        else { toast = "No se pudo comprar"; Snd.sfx("ui_error", 0.7f); }
        toastT = 2.2f;
        layout();
    }

    @Override void render(Platform.Gfx g) {
        int w = W();
        bg.render(g, w, 0.65f);
        UI.big.center(g, "TIENDA", w / 2f, 6, UI.GOLD, 1f);
        float pw = Math.min(w - 24, 440), px = w / 2f - pw / 2f;
        // saldos independientes
        UI.iconC(g, "soul", px + 12, 30, 1f, 1f);
        UI.small.draw(g, "Almas: " + Save.S.souls, px + 24, 26, UI.SOUL, 1f);
        UI.iconC(g, "gem", px + 130, 30, 1f, 1f);
        UI.small.draw(g, "Gemas: " + Wallet.gems() + (Save.devGems > 0 ? " *" : ""), px + 142, 26, UI.PURPLE, 1f);
        ClassDef hero = hero();
        
        UI.panel(g, 0, px, 44, pw, 164, 0.94f);
        UI.small.draw(g, "COSMÉTICOS", px + 10, 50, UI.GOLD, 1f);
        UI.small.right(g, "Aspecto de " + hero.name + (Save.devGems > 0 ? "   (* gemas de prueba)" : ""), px + pw - 10, 50, UI.GREY, 1f);
        List<Cosmetics.Item> cat = Cosmetics.catalog();
        if (cat.isEmpty()) {
            UI.small.center(g, "Aún no hay aspectos disponibles.", w / 2f, 102, UI.WHITE, 1f);
            UI.small.center(g, "Llegarán en futuras versiones; lo que desbloquees se conservará.", w / 2f, 118, UI.GREY, 1f);
            UI.small.center(g, "Las gemas moradas todavía no se pueden comprar.", w / 2f, 134, UI.PURPLE, 1f);
        }
        for (int i = 0; i < ROWS; i++) {
            int idx = page + i;
            if (idx >= cat.size()) break;
            Cosmetics.Item it = cat.get(idx);
            float y = 70 + i * 34;
            g.rect(px + 6, y, pw - 12, 30, 0x22FFFFFF, false);
            boolean eq = Cosmetics.equipped(hero) == it, own = Cosmetics.owns(it.id);
            UI.small.draw(g, it.name, px + 12, y + 4, eq ? UI.GREEN : UI.WHITE, 1f);
            String tag = it.source == Cosmetics.Source.PREMIUM ? "Premium" : it.source == Cosmetics.Source.EARNED ? "Se consigue jugando" : "Google Play (futuro)";
            UI.small.draw(g, (own ? (eq ? "Equipado · " : "Tuyo · ") : "") + tag + (it.classId >= 0 ? " · " + ClassDef.ALL[it.classId].name : ""), px + 12, y + 17, UI.GREY, 1f);
        }
        drawButtons(g);
        if (toastT > 0) { UI.panel(g, 0, w / 2f - 130, 186, 260, 18, 0.95f); UI.small.center(g, toast, w / 2f, 190, UI.GOLD, Mth.clamp(toastT, 0, 1)); }
    }
}
