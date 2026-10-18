package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Parser/serializador JSON minimo (Java puro). Objetos = Map, arreglos = List, numeros = Double, texto = String, booleanos = Boolean, null = null. */
public final class Json {
    private final String s;
    private int i;

    private Json(String s) { this.s = s; }

    @SuppressWarnings("unchecked")
    public static Map<String, Object> parseObj(String text) {
        if (text == null) return null;
        try {
            Object o = new Json(text).value();
            return o instanceof Map ? (Map<String, Object>) o : null;
        } catch (RuntimeException e) {
            return null;
        }
    }

    private void ws() {
        while (i < s.length() && s.charAt(i) <= ' ') i++;
    }

    private Object value() {
        ws();
        char c = s.charAt(i);
        if (c == '{') {
            i++;
            Map<String, Object> m = new LinkedHashMap<>();
            ws();
            if (s.charAt(i) == '}') { i++; return m; }
            while (true) {
                ws();
                String k = str();
                ws();
                i++; // :
                m.put(k, value());
                ws();
                char d = s.charAt(i++);
                if (d == '}') break;
            }
            return m;
        }
        if (c == '[') {
            i++;
            List<Object> l = new ArrayList<>();
            ws();
            if (s.charAt(i) == ']') { i++; return l; }
            while (true) {
                l.add(value());
                ws();
                char d = s.charAt(i++);
                if (d == ']') break;
            }
            return l;
        }
        if (c == '"') return str();
        if (s.startsWith("true", i)) { i += 4; return Boolean.TRUE; }
        if (s.startsWith("false", i)) { i += 5; return Boolean.FALSE; }
        if (s.startsWith("null", i)) { i += 4; return null; }
        int st = i;
        while (i < s.length() && "+-0123456789.eE".indexOf(s.charAt(i)) >= 0) i++;
        return Double.parseDouble(s.substring(st, i));
    }

    private String str() {
        i++; // "
        StringBuilder b = new StringBuilder();
        while (true) {
            char c = s.charAt(i++);
            if (c == '"') break;
            if (c == '\\') {
                char e = s.charAt(i++);
                switch (e) {
                    case 'n': b.append('\n'); break;
                    case 't': b.append('\t'); break;
                    case 'r': b.append('\r'); break;
                    case 'b': b.append('\b'); break;
                    case 'f': b.append('\f'); break;
                    case 'u': b.append((char) Integer.parseInt(s.substring(i, i + 4), 16)); i += 4; break;
                    default: b.append(e);
                }
            } else b.append(c);
        }
        return b.toString();
    }

    // ---- helpers de lectura ----
    @SuppressWarnings("unchecked")
    public static Map<String, Object> obj(Map<String, Object> m, String k) {
        Object o = m == null ? null : m.get(k);
        return o instanceof Map ? (Map<String, Object>) o : null;
    }

    @SuppressWarnings("unchecked")
    public static List<Object> arr(Map<String, Object> m, String k) {
        Object o = m == null ? null : m.get(k);
        return o instanceof List ? (List<Object>) o : null;
    }

    public static double num(Map<String, Object> m, String k, double d) {
        Object o = m == null ? null : m.get(k);
        return o instanceof Number ? ((Number) o).doubleValue() : d;
    }

    public static int i(Map<String, Object> m, String k, int d) { return (int) num(m, k, d); }

    public static String str(Map<String, Object> m, String k, String d) {
        Object o = m == null ? null : m.get(k);
        return o instanceof String ? (String) o : d;
    }

    public static boolean bool(Map<String, Object> m, String k, boolean d) {
        Object o = m == null ? null : m.get(k);
        return o instanceof Boolean ? (Boolean) o : d;
    }

    public static int[] ints(Map<String, Object> m, String k) {
        List<Object> l = arr(m, k);
        if (l == null) return null;
        int[] r = new int[l.size()];
        for (int j = 0; j < r.length; j++) r[j] = ((Number) l.get(j)).intValue();
        return r;
    }

    // ---- escritura ----
    public static String write(Object o) {
        StringBuilder b = new StringBuilder();
        w(b, o);
        return b.toString();
    }

    @SuppressWarnings("unchecked")
    private static void w(StringBuilder b, Object o) {
        if (o == null) b.append("null");
        else if (o instanceof String) {
            b.append('"');
            for (char c : ((String) o).toCharArray()) {
                if (c == '"' || c == '\\') b.append('\\').append(c);
                else if (c == '\n') b.append("\\n");
                else if (c < 32) b.append(' ');
                else b.append(c);
            }
            b.append('"');
        } else if (o instanceof Boolean) b.append(o);
        else if (o instanceof Number) {
            double d = ((Number) o).doubleValue();
            if (d == Math.rint(d) && Math.abs(d) < 1e15) b.append((long) d);
            else b.append(d);
        } else if (o instanceof Map) {
            b.append('{');
            boolean f = true;
            for (Map.Entry<String, Object> e : ((Map<String, Object>) o).entrySet()) {
                if (!f) b.append(',');
                f = false;
                w(b, e.getKey());
                b.append(':');
                w(b, e.getValue());
            }
            b.append('}');
        } else if (o instanceof List) {
            b.append('[');
            boolean f = true;
            for (Object e : (List<Object>) o) {
                if (!f) b.append(',');
                f = false;
                w(b, e);
            }
            b.append(']');
        } else if (o instanceof int[]) {
            b.append('[');
            int[] a = (int[]) o;
            for (int j = 0; j < a.length; j++) {
                if (j > 0) b.append(',');
                b.append(a[j]);
            }
            b.append(']');
        } else b.append('"').append(o).append('"');
    }
}
