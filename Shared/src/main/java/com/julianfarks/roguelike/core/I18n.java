package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Internacionalizacion centralizada. El texto fuente (espanol, idioma base) hace de clave, como en gettext:
 * assets/i18n/<codigo>.tsv contiene lineas "clave espanola TAB traduccion" (\n y \t escapados; '#' = comentario).
 * Las claves con "{}" son plantillas para textos con datos (numeros, nombres): "Vida base {} · Daño {}".
 * En la traduccion se pueden usar {} (en orden) o {1}, {2}... para reordenar.
 * El texto se traduce SOLO al dibujarlo (Font): la logica del juego, los guardados y los identificadores siguen en espanol/ASCII.
 * Si falta una traduccion se usa el espanol y se registra la clave pendiente (missing()).
 */
public final class I18n {
    private I18n() {}

    public static final String[] CODES = {"es", "en", "fr", "zh-Hans"};
    /** Nombre de cada idioma en su propia lengua (no se traduce). */
    public static final String[] NATIVE = {"Español", "English", "Français", "简体中文"};
    public static final int ES = 0, EN = 1, FR = 2, ZH = 3;

    private static int cur = ES;
    private static Platform plat;
    private static final Map<String, String>[] exact = newMaps();
    private static final List<Tpl>[] tpls = newLists();
    private static final boolean[] loaded = new boolean[CODES.length];
    private static final Map<String, String>[] memo = newMaps();
    private static final Set<String> missing = new LinkedHashSet<>();
    private static final Set<String> noTranslate = new java.util.HashSet<>();   // textos que no se traducen a proposito

    static { for (String n : NATIVE) noTranslate.add(n); for (String n : new String[]{"SwordsmanMagic: Eternal Abyss", "SwordsmanMagic: Eternal Abyss v2.1", "JulianFarKs", "Team TKD", "Chernobyl"}) noTranslate.add(n); }

    @SuppressWarnings("unchecked") private static Map<String, String>[] newMaps() { Map<String, String>[] a = new Map[CODES.length]; for (int i = 0; i < a.length; i++) a[i] = new HashMap<>(); return a; }
    @SuppressWarnings("unchecked") private static List<Tpl>[] newLists() { List<Tpl>[] a = new List[CODES.length]; for (int i = 0; i < a.length; i++) a[i] = new ArrayList<>(); return a; }

    private static final class Tpl {
        final Pattern re; final String to; final int n, lit;
        Tpl(String from, String to) {
            StringBuilder sb = new StringBuilder("^"); int k = 0, pos = 0;
            while (true) {
                int i = from.indexOf("{}", pos);
                if (i < 0) { sb.append(Pattern.quote(from.substring(pos))); break; }
                if (i > pos) sb.append(Pattern.quote(from.substring(pos, i)));
                sb.append("(.+?)"); k++; pos = i + 2;
            }
            sb.append('$');
            re = Pattern.compile(sb.toString(), Pattern.DOTALL); this.to = to; n = k; lit = from.length() - 2 * k;
        }
    }

    // ------------------------------------------------------------------ configuracion
    public static void init(Platform p) { plat = p; }
    public static int lang() { return cur; }
    public static String code() { return CODES[cur]; }
    public static boolean isDefault() { return cur == ES; }

    public static void set(int lang) {
        if (lang < 0 || lang >= CODES.length) lang = ES;
        cur = lang;
        if (lang != ES && !loaded[lang]) load(lang);
        memo[lang].clear();
    }

    /** Carga un catalogo (tambien usable desde pruebas con texto directo). */
    public static void load(int lang) {
        loaded[lang] = true;
        exact[lang].clear(); tpls[lang].clear();
        String raw = plat == null ? null : plat.loadText("i18n/" + CODES[lang] + ".tsv");
        if (raw == null) { if (plat != null) plat.log("i18n: falta el catalogo " + CODES[lang]); return; }
        parse(lang, raw);
    }

    public static void parse(int lang, String raw) {
        for (String line : raw.split("\n")) {
            if (line.isEmpty() || line.charAt(0) == '#') continue;
            if (line.endsWith("\r")) line = line.substring(0, line.length() - 1);
            int t = line.indexOf('\t');
            if (t <= 0) continue;
            String k = unesc(line.substring(0, t)), v = unesc(line.substring(t + 1));
            if (k.contains("{}")) tpls[lang].add(new Tpl(k, v)); else exact[lang].put(k, v);
        }
        tpls[lang].sort((a, b) -> b.lit - a.lit);   // las plantillas mas especificas primero
    }

    static String unesc(String s) {
        if (s.indexOf('\\') < 0) return s;
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '\\' && i + 1 < s.length()) { char d = s.charAt(++i); sb.append(d == 'n' ? '\n' : d == 't' ? '\t' : d); }
            else sb.append(c);
        }
        return sb.toString();
    }

    public static int entries(int lang) { return exact[lang].size() + tpls[lang].size(); }

    // ------------------------------------------------------------------ traduccion
    /** Traduce un texto fuente (espanol). En espanol devuelve el mismo objeto. */
    public static String tr(String s) {
        if (cur == ES || s == null || s.isEmpty()) return s;
        for (int k = 0; k < s.length(); k++) if (s.charAt(k) >= 0x2E80) return s;   // ya traducido (CJK)
        String m = memo[cur].get(s);
        if (m != null) return m;
        String r = lookup(cur, s);
        if (memo[cur].size() > 6000) memo[cur].clear();
        memo[cur].put(s, r);
        return r;
    }

    private static boolean hasLetters(String s) {
        int run = 0;
        for (int i = 0; i < s.length(); i++) { char c = s.charAt(i); if (Character.isLetter(c)) { if (++run >= 2) return true; } else run = 0; }
        return false;
    }

    private static String lookup(int lang, String s) {
        String e = exact[lang].get(s);
        if (e != null) return e;
        for (Tpl t : tpls[lang]) {
            Matcher m = t.re.matcher(s);
            if (m.matches()) return fill(lang, t, m);
        }
        if (s.indexOf('\n') > 0) {                 // varias lineas: cada una por separado
            String[] ls = s.split("\n", -1); StringBuilder sb = new StringBuilder(); boolean all = true;
            for (int i = 0; i < ls.length; i++) {
                String x = ls[i].isEmpty() ? "" : lookup(lang, ls[i]);
                if (i > 0) sb.append('\n');
                sb.append(x);
                if (x == ls[i] && hasLetters(ls[i])) all = false;
            }
            if (all) return sb.toString();
        }
        for (String sep : new String[]{" · ", "  "}) {            // "a · b" / "a  b": cada parte por separado
            if (s.indexOf(sep) <= 0) continue;
            String[] ps = s.split(java.util.regex.Pattern.quote(sep), -1); StringBuilder sb = new StringBuilder(); boolean all = true;
            for (int i = 0; i < ps.length; i++) {
                String x = ps[i].isEmpty() ? "" : lookupQuiet(lang, ps[i]);
                if (i > 0) sb.append(sep);
                sb.append(x);
                if (x.equals(ps[i]) && hasLetters(ps[i]) && !exact[lang].containsKey(ps[i]) && !noTranslate.contains(ps[i])) all = false;
            }
            if (all) return sb.toString();
        }
        // texto con adornos al principio/final (espacios, '+', '-', ':' ...): se traduce el nucleo
        String core = trimDeco(s);
        if (!core.equals(s) && !core.isEmpty()) {
            String c = lookup(lang, core);
            if (c != core) { int a = s.indexOf(core); return s.substring(0, a) + c + s.substring(a + core.length()); }
        }
        if (hasLetters(s) && !noTranslate.contains(s)) {
            if (missing.add(s) && plat != null) plat.log("i18n pendiente [" + CODES[lang] + "]: " + s.replace("\n", "\\n"));
        }
        return s;
    }

    private static String trimDeco(String s) {
        int a = 0, b = s.length();
        while (a < b) {
            char c = s.charAt(a);
            if (" ·•*>»".indexOf(c) >= 0) a++;
            else if ((c == '+' || c == '-') && a + 1 < b && s.charAt(a + 1) == ' ') a++;
            else break;
        }
        while (b > a && " :·•*".indexOf(s.charAt(b - 1)) >= 0) b--;
        return s.substring(a, b);
    }

    private static String fill(int lang, Tpl t, Matcher m) {
        String[] a = new String[t.n];
        for (int i = 0; i < t.n; i++) { String g = m.group(i + 1); a[i] = lookupQuiet(lang, g); }
        StringBuilder sb = new StringBuilder(); String to = t.to; int seq = 0;
        for (int i = 0; i < to.length(); i++) {
            char c = to.charAt(i);
            if (c == '{') {
                int j = to.indexOf('}', i);
                if (j > 0) {
                    String id = to.substring(i + 1, j);
                    int k = id.isEmpty() ? seq++ : parseIdx(id) - 1;
                    if (k >= 0 && k < a.length) { sb.append(a[k]); i = j; continue; }
                }
            }
            sb.append(c);
        }
        return sb.toString();
    }

    private static int parseIdx(String s) { try { return Integer.parseInt(s); } catch (NumberFormatException e) { return -1; } }

    /** Traduce un fragmento variable si existe en el catalogo; si no, lo deja igual SIN registrarlo como pendiente. */
    private static String lookupQuiet(int lang, String g) {
        String e = exact[lang].get(g);
        if (e != null) return e;
        if (g.length() < 3 || !hasLetters(g)) return g;
        for (Tpl t : tpls[lang]) { Matcher m = t.re.matcher(g); if (m.matches()) return fill(lang, t, m); }
        return g;
    }

    // ------------------------------------------------------------------ pendientes
    public static Set<String> missing() { return missing; }
    public static void clearMissing() { missing.clear(); }
    public static boolean has(int lang, String key) { return exact[lang].containsKey(key); }
    public static Set<String> keys(int lang) { return exact[lang].keySet(); }
    public static void ignore(String s) { noTranslate.add(s); }
    /** Fija un texto ya resuelto (p. ej. recortado) para que tr() lo devuelva tal cual en el idioma actual. */
    public static void pin(String s) { exact[cur].put(s, s); }
}
