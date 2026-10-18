package com.julianfarks.roguelike.core;

import java.lang.reflect.Proxy;
import java.nio.file.*;
import java.util.*;

/** Pruebas del sistema de idiomas: catalogos, plantillas, respaldo a espanol, persistencia, partidas antiguas e intactitud de datos. */
public class T14 {
    static int f = 0;
    static void ck(String n, boolean ok) { System.out.println((ok ? "ok   " : "FAIL ") + n); if (!ok) f++; }
    static final Map<String, String> disk = new HashMap<>();
    static final List<String> logs = new ArrayList<>();
    static final String ASSETS = "Shared/assets/";

    static Platform plat() {
        final Platform.Store st = new Platform.Store() {
            public String get(String k, String d) { String v = disk.get(k); return v == null ? d : v; }
            public void put(String k, String v) { disk.put(k, v); }
            public void commit() {}
        };
        return (Platform) Proxy.newProxyInstance(T14.class.getClassLoader(), new Class[]{Platform.class}, (p, m, a) -> {
            if (m.getName().equals("store")) return st;
            if (m.getName().equals("loadText")) { try { return new String(Files.readAllBytes(Paths.get(ASSETS + a[0])), "UTF-8"); } catch (Exception e) { return null; } }
            if (m.getName().equals("log")) { logs.add(String.valueOf(a[0])); return null; }
            Class<?> r = m.getReturnType();
            if (r == boolean.class) return false; if (r == int.class) return 0; if (r == float.class) return 0f; if (r == long.class) return 0L;
            return null;
        });
    }

    public static void main(String[] x) throws Exception {
        Platform p = plat();
        disk.clear(); Save.load(p);
        ck("idioma por defecto = espanol", Save.S.lang == 0 && I18n.code().equals("es") && I18n.isDefault());
        ck("espanol devuelve el mismo texto", I18n.tr("Comenzar").equals("Comenzar"));
        for (int l = 1; l < 4; l++) { I18n.load(l); ck("catalogo " + I18n.code() + " cargado (" + I18n.entries(l) + ")", I18n.entries(l) > 1000); }
        // semantica: las mismas claves en los 3 idiomas
        ck("mismas claves exactas en en/fr/zh", I18n.keys(1).equals(I18n.keys(2)) && I18n.keys(1).equals(I18n.keys(3)));
        I18n.set(1);
        ck("en: Comenzar -> Start", I18n.tr("Comenzar").equals("Start"));
        ck("en: Idioma -> Language", I18n.tr("Idioma").equals("Language"));
        I18n.set(2);
        ck("fr: Comenzar -> Commencer", I18n.tr("Comenzar").equals("Commencer"));
        ck("fr: acentos conservados", I18n.tr("Créditos").equals("Crédits"));
        I18n.set(3);
        ck("zh: Comenzar -> 开始", I18n.tr("Comenzar").equals("开始"));
        ck("zh: plantilla con biomas", I18n.tr("Caíste en Forja Infernal · piso 4 · Retos +50%").equals("你倒在了地狱锻炉 · 第4层 · 挑战 +50%"));
        ck("zh: texto ya traducido no se traduce de nuevo", I18n.tr("开始").equals("开始"));
        I18n.set(1);
        ck("en: plantilla especifica gana a la general", I18n.tr("Caíste en Forja Infernal · piso 4 · Retos +50%").startsWith("You fell in Infernal Forge · floor 4 · Challenges +50%"));
        ck("en: compuesto 'a  b'", I18n.tr("Veneno vivo  +8% prob. envenenar").equals("Living venom  +8% poison chance"));
        ck("en: compuesto 'a · b'", I18n.tr("Paladín del Alba · Asesino de las Sombras").startsWith("Paladin of Dawn · "));
        String ad = I18n.tr("- -8% daño"); ck("en: adorno +/- (" + ad + ")", ad.equals("- -8% damage"));
        // respaldo
        I18n.clearMissing(); logs.clear();
        String raro = "Texto inexistente para la prueba xyz";
        ck("falta traduccion: devuelve espanol", I18n.tr(raro).equals(raro));
        ck("falta traduccion: se registra la clave", I18n.missing().contains(raro) && logs.stream().anyMatch(s -> s.contains(raro)));
        ck("nombres propios no se traducen ni se registran", I18n.tr("JulianFarKs").equals("JulianFarKs") && !I18n.missing().contains("JulianFarKs"));
        ck("idiomas nativos intactos", I18n.tr("简体中文").equals("简体中文") && I18n.tr("Español").equals("Español") && I18n.tr("Français").equals("Français"));
        // persistencia
        disk.clear(); Save.load(p);
        Save.S.souls = 1234; Save.S.gems = 56; Save.S.classUnlocked[3] = true; Save.S.infBestFloor = 9; Save.S.infBestScore = 4321;
        Save.S.lang = 3; I18n.set(3); Save.S.write();
        String snap = disk.toString();
        Save.S = null; Save.load(p);
        ck("el idioma se conserva tras cerrar y abrir", Save.S.lang == 3 && I18n.lang() == 3);
        ck("cambiar de idioma no toca el progreso", Save.S.souls == 1234 && Save.S.gems == 56 && Save.S.classUnlocked[3] && Save.S.infBestFloor == 9 && Save.S.infBestScore == 4321);
        for (int l = 0; l < 4; l++) { Save.S.lang = l; I18n.set(l); }
        ck("conmutar 4 idiomas no altera monedas/records", Save.S.souls == 1234 && Save.S.gems == 56 && Save.S.infBestScore == 4321);
        // partida antigua sin clave de idioma
        String k = null; for (String key : disk.keySet()) if (disk.get(key).contains("\"lang\"")) k = key;
        ck("el guardado contiene la clave de idioma", k != null);
        if (k != null) {
            disk.put(k, disk.get(k).replaceAll("\"lang\"\\s*:\\s*\"[^\"]*\"\\s*,?", ""));
            Save.S = null; Save.load(p);
            ck("partida sin clave 'lang' abre en espanol", Save.S.lang == 0 && I18n.isDefault());
            ck("partida antigua conserva datos", Save.S.souls == 1234 && Save.S.gems == 56 && Save.S.classUnlocked[3]);
        }
        // codigo de idioma desconocido -> espanol
        if (k != null) {
            disk.put(k, disk.get(k).replaceFirst("\\{", "{\"lang\":\"xx\","));
            Save.S = null; Save.load(p);
            ck("codigo de idioma desconocido -> espanol", Save.S.lang == 0);
        }
        // cadenas de glifos del chino presentes en el atlas
        String json = new String(Files.readAllBytes(Paths.get(ASSETS + "font/font_s_cjk.json")), "UTF-8");
        String zh = new String(Files.readAllBytes(Paths.get(ASSETS + "i18n/zh-Hans.tsv")), "UTF-8");
        int miss = 0; Set<Character> seen = new HashSet<>();
        for (String line : zh.split("\n")) { if (line.startsWith("#") || !line.contains("\t")) continue; for (char c : line.substring(line.indexOf('\t') + 1).toCharArray()) if (c >= 0x2E80 && seen.add(c) && !json.contains(String.valueOf(c))) miss++; }
        ck("todos los caracteres chinos tienen glifo (" + seen.size() + ")", miss == 0);
        String lat = new String(Files.readAllBytes(Paths.get(ASSETS + "font/font_s.json")), "UTF-8");
        int missL = 0;
        for (String l : new String[]{"en", "fr"}) for (String line : new String(Files.readAllBytes(Paths.get(ASSETS + "i18n/" + l + ".tsv")), "UTF-8").split("\n")) { if (line.startsWith("#") || !line.contains("\t")) continue; for (char c : line.substring(line.indexOf('\t') + 1).toCharArray()) if (c != '\\' && lat.indexOf(c) < 0) { missL++; System.out.println("sin glifo latino: " + c + " en " + line); } }
        ck("todos los caracteres en/fr tienen glifo latino", missL == 0);
        System.out.println(f == 0 ? "T14 OK" : "T14 FALLOS: " + f);
        System.exit(f == 0 ? 0 : 1);
    }
}
