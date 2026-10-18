package com.julianfarks.roguelike.core;

import java.util.HashMap;
import java.util.Map;

/** Carga con cache de imagenes y hojas de sprites. Nunca devuelve null en hojas (usa Sheet.EMPTY). */
public final class Assets {
    private Assets() {}
    static Platform P;
    private static final Map<String, Platform.Img> imgs = new HashMap<>();
    private static final java.util.Set<String> missing = new java.util.HashSet<>();
    private static final Map<String, Sheet> sheets = new HashMap<>();

    public static void init(Platform p) { P = p; }

    public static Platform.Img img(String path) {
        Platform.Img i = imgs.get(path);
        if (i != null) return i;
        if (missing.contains(path)) return null;
        i = P.loadImage(path);
        if (i == null) { missing.add(path); P.log("MISSING image " + path); return null; }
        imgs.put(path, i);
        return i;
    }

    /** base sin extension, p.ej. "sprites/pl_flame". */
    public static Sheet sheet(String base) {
        Sheet s = sheets.get(base);
        if (s != null) return s;
        Platform.Img im = img(base + ".png");
        String txt = P.loadText(base + ".json");
        Map<String, Object> d = Json.parseObj(txt);
        if (im != null && d != null) s = Sheet.parse(im, d);
        if (s == null) { P.log("MISSING sheet " + base); s = Sheet.EMPTY; }
        sheets.put(base, s);
        return s;
    }

    public static Sheet spr(String name) { return sheet("sprites/" + name); }
    public static Sheet fx(String name) { return sheet("fx/" + name); }

    public static boolean loaded(String base) { return sheets.containsKey(base); }
}
