package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/**
 * Catalogo, propiedad y equipamiento de cosmeticos (skins). Separa datos (Item) de logica y de apariencia:
 * un skin solo declara que hoja de sprites usa (o un tinte) y para que espadachin vale; no duplica codigo del personaje.
 * El catalogo oficial esta VACIO a proposito (aun no hay skins reales); anadir una skin = anadir una linea a ALL.
 * Fuentes de un articulo: EARNED (se consigue jugando), PREMIUM (gemas), STORE (Google Play, futuro, no activo).
 */
public final class Cosmetics {
    private Cosmetics() {}

    public enum Kind { SKIN }
    public enum Source { EARNED, PREMIUM, STORE }

    public static final class Item {
        public final String id, name, desc, spriteKey;
        public final Kind kind; public final Source source;
        public final int classId;        // -1 = cualquier espadachin
        public final int priceGems;      // solo PREMIUM
        public final int tint;           // 0 = sin tinte (RGB)
        public Item(String id, String name, String desc, Kind kind, Source source, int classId, int priceGems, String spriteKey, int tint) {
            this.id = id; this.name = name; this.desc = desc; this.kind = kind; this.source = source; this.classId = classId;
            this.priceGems = priceGems; this.spriteKey = spriteKey; this.tint = tint;
        }
        public boolean fits(ClassDef c) { return classId < 0 || (c != null && c.id == classId); }
    }

    /** Catalogo oficial (vacio hasta que existan skins reales). */
    public static final List<Item> ALL = new ArrayList<>();
    /** Articulos de PRUEBA: solo visibles con el Modo Desarrollador desbloqueado; sirven para verificar compra/equipado. */
    public static final List<Item> DEV = new ArrayList<>();
    static {
        DEV.add(new Item("dev_tint_violet", "[DEV] Tinte violeta", "Articulo de prueba (no es una skin real).", Kind.SKIN, Source.PREMIUM, -1, 5, null, 0xB080FF));
        DEV.add(new Item("dev_tint_ember", "[DEV] Tinte brasa", "Articulo de prueba (no es una skin real).", Kind.SKIN, Source.EARNED, -1, 0, null, 0xFF9060));
    }

    public static List<Item> catalog() {
        List<Item> l = new ArrayList<>(ALL);
        if (Save.S.devUnlocked) l.addAll(DEV);
        return l;
    }

    public static Item find(String id) {
        if (id == null) return null;
        for (Item i : ALL) if (i.id.equals(id)) return i;
        for (Item i : DEV) if (i.id.equals(id)) return i;
        return null;
    }

    public static boolean owns(String id) { return id != null && Save.S.owned.contains(id); }

    /** Concede un articulo (idempotente). */
    public static boolean grant(String id) {
        if (find(id) == null || owns(id)) return false;
        Save.S.owned.add(id);
        Save.S.write();
        return true;
    }

    /** Compra con gemas: valida propiedad, fuente y saldo; descuenta y concede en UNA sola escritura. */
    public static boolean buy(String id) {
        Item it = find(id);
        if (it == null || it.source != Source.PREMIUM || it.priceGems <= 0 || owns(id)) return false;
        if (!Wallet.spend(it.priceGems, false)) return false;
        Save.S.owned.add(id);
        Save.S.write(true);
        return true;
    }

    public static boolean equip(ClassDef c, String id) {
        if (c == null) return false;
        if (id == null || id.isEmpty()) { Save.S.equip[c.id] = ""; Save.S.write(); return true; }
        Item it = find(id);
        if (it == null || !owns(id) || !it.fits(c)) return false;
        Save.S.equip[c.id] = id;
        Save.S.write();
        return true;
    }

    public static Item equipped(ClassDef c) {
        if (c == null) return null;
        String id = Save.S.equip[c.id];
        Item it = id == null || id.isEmpty() ? null : find(id);
        return it != null && owns(id) && it.fits(c) ? it : null;
    }

    /** Hoja de sprites a usar para el espadachin (la del skin equipado si existe, si no la original). */
    public static Sheet sheetFor(ClassDef c) {
        Item it = equipped(c);
        if (it != null && it.spriteKey != null) {
            Sheet s = Assets.spr(it.spriteKey);
            if (s != null && s != Sheet.EMPTY) return s;
        }
        return Assets.spr("pl_" + c.key);
    }

    /** Tinte RGB del skin equipado (0 = ninguno). */
    public static int tintFor(ClassDef c) { Item it = equipped(c); return it == null ? 0 : it.tint; }
}
