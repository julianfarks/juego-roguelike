package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Modo Desarrollador: catalogo/laboratorio integrado. Usa los recursos reales del juego (hojas de sprites, definiciones, escenas).
 * No modifica guardados ni progreso (la arena usa RunState.sandbox). Para ampliar: anadir una Entry en la lista de la categoria.
 */
final class DevScreens {
    private DevScreens() {}

    static final int K_ENEMY = 0, K_ELITE = 1, K_BOSS = 2, K_CLASS = 3, K_OBJ = 4, K_BIOME = 5;

    static final class Entry {
        final String label, sheet; final int kind; final Object ref;
        Entry(String label, String sheet, int kind, Object ref) { this.label = label; this.sheet = sheet; this.kind = kind; this.ref = ref; }
    }

    // ------------------------------------------------------------------ catalogos
    static List<Entry> enemies(boolean elite) {
        List<Entry> l = new ArrayList<>();
        for (EnemyDef d : EnemyDef.all()) if (d.elite == elite) l.add(new Entry(pretty(d.id), d.sheet, elite ? K_ELITE : K_ENEMY, d));
        Collections.sort(l, (a, b) -> a.label.compareTo(b.label));
        return l;
    }

    static List<Entry> bosses() {
        List<Entry> l = new ArrayList<>();
        for (BossDef d : BossDef.ALL) l.add(new Entry(d.name, d.sheet, K_BOSS, d));
        return l;
    }

    static List<Entry> classes() {
        List<Entry> l = new ArrayList<>();
        for (ClassDef c : ClassDef.ALL) l.add(new Entry(c.name, "sprites/pl_" + c.key, K_CLASS, c));
        return l;
    }

    static List<Entry> objects() {
        List<Entry> l = new ArrayList<>();
        String[] names = {"altar", "forge", "merchant", "fountain", "chest", "pot", "portal", "sanctuary", "door", "npc_0", "npc_1", "npc_2"};
        for (String n : names) l.add(new Entry("Prop: " + n, "sprites/prop_" + n, K_OBJ, "Objeto interactivo del escenario."));
        String[] picks = {"gold", "heart", "potion", "relic", "soul"};
        for (String n : picks) l.add(new Entry("Objeto: " + n, "sprites/pick_" + n, K_OBJ, "Objeto recogible."));
        return l;
    }

    static List<Entry> biomes() {
        List<Entry> l = new ArrayList<>();
        for (Biome b : Biome.ALL) l.add(new Entry(b.name, null, K_BIOME, b));
        return l;
    }

    static final String[][] NAMES = {{"caballero_osario", "Caballero del Osario"}, {"herrero_infernal", "Herrero Infernal"}, {"ventisca", "Ventisca"},
            {"segador_vacio", "Segador del Vacío"}, {"druida_podrido", "Druida Podrido"}, {"capitan_trueno", "Capitán del Trueno"},
            {"sacerdote_carmesi", "Sacerdote Carmesí"}, {"centurion_eclipse", "Centurión del Eclipse"}};

    static String pretty(String id) {
        for (String[] n : NAMES) if (n[0].equals(id)) return n[1];
        String s = id.replace('_', ' ');
        return Character.toUpperCase(s.charAt(0)) + s.substring(1);
    }

    static final String[] ROLE = {"Cuerpo a cuerpo", "A distancia", "Volador (dispara)", "Volador (pica)", "Embestidor", "Saltador", "Hechicero", "Pesado",
            "Escudero", "Apoyo (cura)", "Explosivo", "Torreta", "Acechador (salta)", "Francotirador", "Potenciador", "Teletransportador", "Élite único"};
    static final String[] ROLE_DESC = {
            "Se acerca y golpea cuerpo a cuerpo.", "Mantiene la distancia y dispara proyectiles.", "Vuela y dispara desde el aire.", "Vuela y se lanza en picado.",
            "Carga en línea recta: esquívalo y castígalo al frenar.", "Salta sobre ti desde lejos.", "Lanza hechizos con aviso previo.", "Lento, resistente, golpes muy fuertes.",
            "Bloquea de frente: golpéalo por la espalda o rómpele la guardia.", "Cura y protege a los aliados: prioridad al combatir.", "Corre hacia ti y explota; mátalo de lejos.",
            "Inmóvil: dispara cristales hacia ti.", "Se agazapa y salta con un zarpazo rápido.", "Apunta con una línea azul/roja y dispara un rayo.",
            "Potencia a los aliados cercanos (más velocidad y daño).", "Se desvanece y reaparece tras de ti."};
    static final String[][] ELITE_INFO = {
            {"caballero_osario", "Ataque 1: tajo vertical que lanza una onda de choque rasante (salta o rueda). Ataque 2: embestida con la espada al frente, avisada y en línea recta."},
            {"herrero_infernal", "Ataque 1: tres bolas de magma en arco que explotan y queman. Ataque 2: martillazo con dos ondas de fuego, una a cada lado."},
            {"ventisca", "Vuela. Ataque 1: nova de 10 esquirlas de hielo en anillo (ralentiza). Ataque 2: picado en línea recta hacia ti."},
            {"segador_vacio", "Ataque 1: se desvanece y reaparece junto a ti (el anillo morado avisa) y barre con la guadaña. Ataque 2: invoca 3 orbes del vacío teledirigidos."},
            {"druida_podrido", "Ataque 1: tres zarzas brotan bajo ti, con aviso en el suelo (veneno). Ataque 2: bola venenosa en arco y abanico de hojas."},
            {"capitan_trueno", "Ataque 1: tres rayos con aviso en el suelo (electrocuta). Ataque 2: estocada en carrera con la lanza."},
            {"sacerdote_carmesi", "Ataque 1: tres orbes de sangre teledirigidos (sangrado). Ataque 2: pilar de sangre bajo ti, con aviso; si te alcanza, se cura."},
            {"centurion_eclipse", "Ataque 1: rayo solar horizontal con línea de aviso. Ataque 2: golpe de escudo con estallido radial sagrado."}};
    static final String[] SLAM = {"ninguno", "erupción en línea", "erupción bajo el jugador", "lluvia de proyectiles", "atracción hacia el jefe", "lluvia de rocas"};
    static final String[] CAST = {"abanico", "disparo apuntado", "invocación", "lluvia", "líneas"};

    static String eliteInfo(String id) { for (String[] r : ELITE_INFO) if (r[0].equals(id)) return r[1]; return "Sin descripción."; }

    /** Normal "relacionado" con un elite: el primero de la reserva del bioma al que pertenece. */
    static String relatedNormal(String eliteId) {
        for (Biome b : Biome.ALL) if (eliteId.equals(EnemyDef.eliteFor(b.key)) && b.enemies.length > 0) return b.enemies[0];
        return null;
    }

    static int biomeOf(Entry e) {
        if (e.kind == K_BOSS) return Math.min(8, ((BossDef) e.ref).idx);
        if (e.kind == K_ENEMY || e.kind == K_ELITE) {
            String id = ((EnemyDef) e.ref).id;
            for (Biome b : Biome.ALL) { if (id.equals(EnemyDef.eliteFor(b.key))) return b.id; for (String s : b.enemies) if (s.equals(id)) return b.id; }
        }
        return 0;
    }

    // =================================================================== menu
    static final class Menu extends Screen {
        private final Screens.TitleBg bg = new Screens.TitleBg();
        Menu(Game g) { super(g); }
        @Override void enter() { Snd.music(Snd.MENU_MUSIC, true); layout(); }

        @Override void layout() {
            hits.clear();
            int w = W();
            float bw = 190, bh = 19, x = w / 2f - bw / 2f, y = 44, st = 21;
            add(x, y, bw, bh, "Enemigos normales", () -> game.go(new ListScr(game, "ENEMIGOS NORMALES", enemies(false))));
            add(x, y + st, bw, bh, "Enemigos élite", () -> game.go(new ListScr(game, "ENEMIGOS ÉLITE", enemies(true))));
            add(x, y + st * 2, bw, bh, "Espadachines y armas", () -> game.go(new ListScr(game, "ESPADACHINES", classes())));
            add(x, y + st * 3, bw, bh, "Jefes finales", () -> game.go(new ListScr(game, "JEFES FINALES", bosses())));
            add(x, y + st * 4, bw, bh, "Cinemáticas y narrativa", () -> game.go(new StoryScreens.Historia(game, true)));
            add(x, y + st * 5, bw, bh, "Escenarios", () -> game.go(new ListScr(game, "ESCENARIOS", biomes())));
            add(x, y + st * 6, bw, bh, "Objetos y props", () -> game.go(new ListScr(game, "OBJETOS Y PROPS", objects())));
            add(x, y + st * 7, bw, bh, "Economía y recursos", () -> game.go(new Economy(game)));
            add(x - 0, y + st * 8 + 2, 92, bh, "Volver", () -> back());
            add(x + 98, y + st * 8 + 2, 92, bh, "Desactivar", () -> { Save.devRevert(); Save.S.devUnlocked = false; Cosmetics.purgeDev(); Save.S.write(); back(); });
        }

        @Override boolean back() { Save.devRevert(); game.go(new Screens.Title(game)); return true; }
        @Override void update(float dt) { bg.update(dt, W()); }

        @Override void render(Platform.Gfx g) {
            int w = W();
            bg.render(g, w, 0.55f);
            UI.big.center(g, "MODO DESARROLLADOR", w / 2f, 14, UI.GOLD, 1f);
            UI.small.center(g, "Laboratorio de contenido · no modifica tu progreso", w / 2f, 32, UI.GREY, 1f);
            drawButtons(g);
        }
    }

    // =================================================================== lista paginada
    static final class ListScr extends Screen {
        private final Screens.TitleBg bg = new Screens.TitleBg();
        private final String title; private final List<Entry> items;
        private int page;
        private static final int PER = 12;

        ListScr(Game g, String title, List<Entry> items) { super(g); this.title = title; this.items = items; }

        @Override void layout() {
            hits.clear();
            int w = W();
            float cw = Math.min(170, (w - 30) / 2f), bh = 19;
            int from = page * PER, to = Math.min(items.size(), from + PER);
            for (int i = from; i < to; i++) {
                final int idx = i;
                int k = i - from;
                float x = w / 2f - cw - 3 + (k % 2) * (cw + 6), y = 40 + (k / 2) * 22;
                add(x, y, cw, bh, trim(items.get(i).label, cw), () -> game.go(new Inspector(game, items, idx, title)));
            }
            int pages = (items.size() + PER - 1) / PER;
            if (pages > 1) {
                Hit pv = add(w / 2f - 130, 212, 40, 19, "<", () -> { page = (page + pages - 1) % pages; layout(); });
                Hit nx = add(w / 2f + 90, 212, 40, 19, ">", () -> { page = (page + 1) % pages; layout(); });
            }
            add(w / 2f - 50, 236, 100, 20, "Volver", () -> back());
        }

        private String trim(String s, float w) { while (s.length() > 3 && UI.small.width(s) > w - 10) s = s.substring(0, s.length() - 1); return s; }

        @Override boolean back() { game.go(new Menu(game)); return true; }
        @Override void update(float dt) { bg.update(dt, W()); }

        @Override void render(Platform.Gfx g) {
            int w = W();
            bg.render(g, w, 0.6f);
            UI.big.center(g, title, w / 2f, 14, UI.GOLD, 1f);
            UI.small.center(g, items.size() + " elementos" + (items.size() > PER ? "  ·  pág. " + (page + 1) + "/" + ((items.size() + PER - 1) / PER) : ""), w / 2f, 30, UI.GREY, 1f);
            drawButtons(g);
        }
    }

    // =================================================================== inspector
    static final class Inspector extends Screen {
        private final List<Entry> items; private final String title;
        private int idx, animIdx, infoPage, animPage, speedIdx = 2;
        private Entry e;
        private Sheet sheet, cmp;
        private final List<String> anims = new ArrayList<>();
        private float tt, hold;
        private boolean paused, boxes, compare;
        private List<List<String>> pages = new ArrayList<>();
        private static final float[] SPEEDS = {0.25f, 0.5f, 1f, 2f};
        private final Screens.TitleBg bg = new Screens.TitleBg();

        Inspector(Game g, List<Entry> items, int idx, String title) { super(g); this.items = items; this.idx = idx; this.title = title; load(); }

        private void load() {
            e = items.get(idx);
            sheet = e.sheet != null ? Assets.sheet(e.sheet) : null;
            anims.clear();
            if (sheet != null) {
                anims.addAll(sheet.anims.keySet());
                Collections.sort(anims, (a, b) -> Integer.compare(sheet.anim(a).row, sheet.anim(b).row));
            }
            animIdx = 0; animPage = 0; infoPage = 0; tt = 0; hold = 0; compare = false; cmp = null;
            buildInfo();
        }

        private void buildInfo() {
            List<String> all = new ArrayList<>();
            int maxW = (int) (W() * 0.46f) - 14;
            switch (e.kind) {
                case K_ENEMY: case K_ELITE: {
                    EnemyDef d = (EnemyDef) e.ref;
                    all.add("Rol: " + ROLE[Math.min(d.role, ROLE.length - 1)]);
                    all.add("Vida: " + Math.round(d.hp) + "   Daño: " + Math.round(d.dmg));
                    all.add("Velocidad: " + Math.round(d.speed) + "   Alcance: " + Math.round(d.range));
                    all.add("Recarga: " + d.cooldown + " s   Almas: " + d.souls);
                    all.add("Estado que aplica: " + (d.status == null || d.status.isEmpty() ? "ninguno" : d.status));
                    all.add("Proyectil: " + (d.proj == null ? "ninguno" : d.proj));
                    all.add("");
                    all.add(e.kind == K_ELITE ? eliteInfo(d.id) : ROLE_DESC[Math.min(d.role, ROLE_DESC.length - 1)]);
                    if (e.kind == K_ELITE) { all.add(""); all.add("Pulsa Comparar para verlo junto a un enemigo normal de su zona."); }
                    break;
                }
                case K_BOSS: {
                    BossDef d = (BossDef) e.ref;
                    all.add(d.title);
                    all.add("Vida: " + Math.round(d.hp) + "   Daño: " + Math.round(d.dmg));
                    all.add("Velocidad: " + Math.round(d.speed) + "   Elemento: " + d.element);
                    all.add(d.idx == 8 ? "Fase " + (d.form + 1) + " de 3 del Cazador" : "Jefe de zona" + (d.hover ? " (vuela)" : ""));
                    all.add("");
                    all.add("Golpe de área: " + SLAM[Math.min(d.slamExtra, SLAM.length - 1)] + ".");
                    all.add("Hechizo: " + CAST[Math.min(d.castKind, CAST.length - 1)] + " de " + d.castCount + " (" + d.castProj + ").");
                    all.add("Súbditos: " + (d.minions == null ? "ninguno" : String.join(", ", d.minions)) + ".");
                    break;
                }
                case K_CLASS: {
                    ClassDef c = (ClassDef) e.ref;
                    all.add(c.role);
                    all.add(c.desc);
                    all.add("Arma: " + c.weapon);
                    all.add("Vida " + Math.round(c.hp) + "  Daño " + Math.round(c.dmg) + "  Vel.ataque " + c.atkSpeed);
                    all.add("Velocidad " + c.speed + "  Crítico " + Math.round(c.crit * 100) + "%  Armadura " + Math.round(c.armor * 100) + "%");
                    all.add("Rasgo: " + c.trait);
                    all.add("");
                    for (ClassDef.Skill s : c.skills) all.add(s.name + (s.cd > 0 ? " (" + Math.round(s.cd) + " s)" : " (definitiva)") + ": " + s.desc);
                    all.add("");
                    all.add("Usa Arena para ver todas sus habilidades en combate real.");
                    break;
                }
                case K_BIOME: {
                    Biome b = (Biome) e.ref;
                    all.add(b.tagline);
                    all.add("Jefe: " + BossDef.byBiome(b.id).name);
                    String el = EnemyDef.eliteFor(b.key);
                    all.add("Élite: " + (el == null ? "ninguno" : pretty(el)));
                    all.add("Enemigos: " + String.join(", ", b.enemies));
                    break;
                }
                default: all.add(String.valueOf(e.ref));
            }
            if (sheet != null && e.kind != K_BIOME) { all.add(""); all.add("Hoja: " + sheet.cw + "x" + sheet.ch + " px · " + anims.size() + " animaciones"); }
            List<String> lines = new ArrayList<>();
            for (String s : all) lines.addAll(UI.small.wrap(s, maxW));
            pages = new ArrayList<>();
            int per = 14;
            for (int i = 0; i < Math.max(1, lines.size()); i += per) pages.add(new ArrayList<>(lines.subList(i, Math.min(lines.size(), i + per))));
        }

        @Override void layout() {
            hits.clear();
            int w = W();
            float bw = (w - 16) / 7f - 2, y = 244;
            int i = 0;
            add(8 + i++ * (bw + 2), y, bw, 19, paused ? "Reanudar" : "Pausa", () -> { paused = !paused; layout(); });
            add(8 + i++ * (bw + 2), y, bw, 19, "Reiniciar", () -> { tt = 0; hold = 0; });
            add(8 + i++ * (bw + 2), y, bw, 19, "Vel x" + trimF(SPEEDS[speedIdx]), () -> { speedIdx = (speedIdx + 1) % SPEEDS.length; layout(); });
            Hit bx = add(8 + i++ * (bw + 2), y, bw, 19, boxes ? "Cajas: sí" : "Cajas: no", () -> { boxes = !boxes; layout(); });
            add(8 + i++ * (bw + 2), y, bw, 19, "Info " + (infoPage + 1) + "/" + pages.size(), () -> { infoPage = (infoPage + 1) % pages.size(); layout(); });
            Hit ar = add(8 + i++ * (bw + 2), y, bw, 19, "Arena", this::arena);
            ar.disabled = e.kind == K_OBJ || e.kind == K_BIOME;
            add(8 + i++ * (bw + 2), y, bw, 19, "Atrás", () -> back());
            // navegar entre elementos
            add(8, 6, 24, 18, "<", () -> { idx = (idx + items.size() - 1) % items.size(); load(); layout(); });
            add(36, 6, 24, 18, ">", () -> { idx = (idx + 1) % items.size(); load(); layout(); });
            if (e.kind == K_ELITE) add(w - 74, 6, 66, 18, compare ? "Solo" : "Comparar", () -> toggleCompare());
            // selector de animaciones
            int per = 5;
            int pages_ = (anims.size() + per - 1) / per;
            float aw = (w - 16 - 2 * 28) / (float) per - 2;
            if (anims.size() > 0) {
                if (pages_ > 1) add(8, 220, 26, 19, "<", () -> { animPage = (animPage + pages_ - 1) % pages_; layout(); });
                for (int k = 0; k < per; k++) {
                    int ai = animPage * per + k;
                    if (ai >= anims.size()) break;
                    final int fai = ai;
                    Hit h = add(8 + 28 + k * (aw + 2), 220, aw, 19, anims.get(ai), () -> { animIdx = fai; tt = 0; hold = 0; layout(); });
                    h.tag = ai == animIdx ? 1 : 0;
                }
                if (pages_ > 1) add(w - 34, 220, 26, 19, ">", () -> { animPage = (animPage + 1) % pages_; layout(); });
            }
        }

        private static String trimF(float f) { return f == (int) f ? String.valueOf((int) f) : String.valueOf(f); }

        private void toggleCompare() {
            compare = !compare;
            if (compare && cmp == null) {
                String n = relatedNormal(((EnemyDef) e.ref).id);
                if (n != null) cmp = Assets.sheet("sprites/en_" + n);
            }
            layout();
        }

        void arena() {
            int bi = biomeOf(e);
            ClassDef cls = ClassDef.ALL[Math.max(0, Math.min(ClassDef.ALL.length - 1, Save.S.lastClass))];
            final List<Entry> its = items; final int ix = idx; final String ttl = title;
            java.util.function.Supplier<Screen> back = () -> new Inspector(game, its, ix, ttl);
            switch (e.kind) {
                case K_BOSS: game.go(RunScreen.sandbox(game, cls, bi, null, false, ((BossDef) e.ref).idx == 8 ? 8 + ((BossDef) e.ref).form : ((BossDef) e.ref).idx, back)); break;
                case K_CLASS: game.go(RunScreen.sandbox(game, (ClassDef) e.ref, 0, "zombi", false, -1, back)); break;
                default: game.go(RunScreen.sandbox(game, cls, bi, ((EnemyDef) e.ref).id, e.kind == K_ELITE, -1, back)); break;
            }
        }

        @Override boolean back() { game.go(new ListScr(game, title, items)); return true; }

        @Override void key(int code, boolean down) {
            if (!down) { return; }
            if (code == 'P') { paused = !paused; layout(); return; }
            super.key(code, down);
        }

        @Override void resize() { buildInfo(); layout(); }

        @Override void update(float dt) {
            bg.update(dt, W());
            if (paused || anims.isEmpty()) return;
            Anim a = sheet.anim(anims.get(animIdx));
            tt += dt * SPEEDS[speedIdx];
            if (!a.loop && a.done(tt)) { hold += dt; if (hold > 0.6f) { tt = 0; hold = 0; } }
        }

        @Override void render(Platform.Gfx g) {
            int w = W();
            bg.render(g, w, 0.72f);
            UI.small.draw(g, e.label, 68, 11, UI.GOLD, 1f);
            float sw = w * 0.5f - 12;
            UI.panel(g, 0, 8, 30, sw, 186, 0.9f);
            if (e.kind == K_BIOME) renderBiome(g, 8, 30, sw, 186);
            else if (sheet != null && !anims.isEmpty()) renderSprite(g, 8, 30, sw, 186);
            else UI.small.center(g, "Sin hoja de sprites", 8 + sw / 2f, 120, UI.GREY, 1f);
            // texto
            float tx = w * 0.5f + 4, ty = 32;
            UI.panel(g, 0, tx - 4, 30, w - tx - 4, 186, 0.9f);
            List<String> pg = pages.get(Math.min(infoPage, pages.size() - 1));
            for (String s : pg) { UI.small.draw(g, s, tx + 2, ty, 0xFFE8E0E0, 1f); ty += UI.small.ch + 2; }
            for (Hit h : hits) {
                drawButton(g, h);
                if (h.tag == 1) g.rect(h.x, h.y + h.h - 2, h.w, 2, 0xFFFFD25A, false);
            }
        }

        private void renderSprite(Platform.Gfx g, float x, float y, float w, float h) {
            Anim a = sheet.anim(anims.get(animIdx));
            int fr = a.frameAt(tt);
            float s = Math.max(1, (float) Math.floor(Math.min((w - 10) / (compare && cmp != null ? 2f : 1f) / sheet.cw, (h - 30) / sheet.ch)));
            if (sheet.cw * s > w - 6 || sheet.ch * s > h - 30) s = 0.5f;
            float cx = x + w / 2f + (compare && cmp != null ? w * 0.22f : 0), by = y + h - 22 - sheet.ch * s * 0.04f;
            float px = cx, py = y + h - 24;
            g.rect(x + 6, py + 1, w - 12, 1, 0x55FFFFFF, false);
            sheet.draw(g, a, fr, px, py, true, s, 0, 0, 1f);
            if (boxes) {
                if (a.box != null) {
                    float[] b = new float[4];
                    float bxw = px + a.box[0] * s, byw = py + a.box[1] * s;
                    int col = a.hitActive(tt) ? 0xFFFF3030 : 0x66FFB0B0;
                    outline(g, bxw, byw, a.box[2] * s, a.box[3] * s, col);
                }
                outline(g, px - sheet.bw * s / 2f, py - sheet.bh * s, sheet.bw * s, sheet.bh * s, 0x6630FF60);
            }
            if (compare && cmp != null) {
                float s2 = s;
                cmp.draw(g, cmp.anim("idle"), cmp.anim("idle").frameAt(tt), x + w * 0.24f, py, true, s2, 0, 0, 1f);
                UI.small.center(g, "Normal", x + w * 0.24f, y + 6, UI.GREY, 1f);
                UI.small.center(g, "Élite", cx, y + 6, UI.GOLD, 1f);
            }
            UI.small.draw(g, anims.get(animIdx) + "  fotograma " + (fr + 1) + "/" + a.n + "  " + Math.round(a.fps) + " fps" + (a.loop ? "  bucle" : ""), x + 8, y + h - 14, UI.GREY, 1f);
        }

        private void outline(Platform.Gfx g, float x, float y, float w, float h, int c) {
            g.rect(x, y, w, 1, c, false); g.rect(x, y + h - 1, w, 1, c, false); g.rect(x, y, 1, h, c, false); g.rect(x + w - 1, y, 1, h, c, false);
        }

        private void renderBiome(Platform.Gfx g, float x, float y, float w, float h) {
            Biome b = (Biome) e.ref;
            g.clipBegin(x + 4, y + 4, w - 8, h - 8);
            for (int i = 0; i < 3; i++) {
                Platform.Img im = Assets.img("bg/bg_" + b.key + "_" + i + ".png");
                if (im == null) continue;
                float s = Math.max((w - 8) / im.w, (h - 8) / im.h);
                float off = (tt * (6 + i * 10)) % (im.w * s);
                for (float xx = x + 4 - off; xx < x + w; xx += im.w * s)
                    g.image(im, 0, 0, im.w, im.h, Math.round(xx), Math.round(y + 4), Math.round(im.w * s), Math.round(im.h * s), 0, 0, 1f);
            }
            g.clipEnd();
        }
    }

    // =================================================================== economia y recursos
    /**
     * Herramienta de dinero. Dos saldos reales del juego (no hay moneda nueva):
     *  - Almas del perfil (Save.S.souls): se modifican de forma TEMPORAL (en disco sigue el valor real hasta pulsar "Guardar en perfil").
     *  - Oro de prueba (Save.devGold): oro inicial de la arena y de la tienda de prueba (el oro solo existe dentro de una partida).
     */
    static final class Economy extends Screen {
        private final Screens.TitleBg bg = new Screens.TitleBg();
        private final StringBuilder num = new StringBuilder();
        private int target;            // 0 almas, 1 oro de prueba
        private String msg = "";
        private int msgColor = 0xFFE8E0E0;
        private boolean confirmSet, confirmCommit;
        static final long CAP = 99_999_999L;

        Economy(Game g) { super(g); }

        static String fmt(long v) {
            String s = String.valueOf(Math.abs(v)), out = "";
            for (int i = 0; i < s.length(); i++) { if (i > 0 && (s.length() - i) % 3 == 0) out += "."; out += s.charAt(i); }
            return (v < 0 ? "-" : "") + out;
        }

        long balance() { return target == 0 ? Save.S.souls : Save.devGold; }

        void setBalance(long v) {
            v = Math.max(0, Math.min(CAP, v));
            if (target == 0) {
                if (Save.devSoulsBackup < 0) Save.devSoulsBackup = Save.S.souls;   // primer cambio: recuerda el valor real
                Save.S.souls = (int) v;
            } else Save.devGold = (int) v;
        }

        long amount() { if (num.length() == 0) return 0; try { return Long.parseLong(num.toString()); } catch (NumberFormatException e) { return CAP; } }

        @Override void layout() {
            hits.clear();
            int w = W();
            float kw = 34, kh = 19, gap = 3, x0 = 16, y0 = 78;
            String[] keys = {"7", "8", "9", "4", "5", "6", "1", "2", "3", "0", "00", "000"};
            for (int i = 0; i < keys.length; i++) {
                final String k = keys[i];
                Hit h = add(x0 + (i % 3) * (kw + gap), y0 + (i / 3) * (kh + gap), kw, kh, k, () -> { if (num.length() + k.length() <= 9) num.append(k); confirmSet = false; });
                h.noSound = true;
            }
            add(x0, y0 + 4 * (kh + gap), kw * 1.5f + gap / 2, kh, "Borrar", () -> { if (num.length() > 0) num.setLength(num.length() - 1); confirmSet = false; });
            add(x0 + kw * 1.5f + gap * 1.5f, y0 + 4 * (kh + gap), kw * 1.5f + gap / 2, kh, "Limpiar", () -> { num.setLength(0); confirmSet = false; });
            float rx = w / 2f + 10, rw = w - rx - 12;
            add(rx, 52, rw / 2 - 2, 19, target == 0 ? "[Almas]" : "Almas", () -> { target = 0; confirmSet = false; layout(); });
            add(rx + rw / 2 + 2, 52, rw / 2 - 2, 19, target == 1 ? "[Oro prueba]" : "Oro prueba", () -> { target = 1; confirmSet = false; layout(); });
            long[] quick = {1000, 10000, 100000};
            for (int i = 0; i < 3; i++) {
                final long q = quick[i];
                add(rx + i * (rw / 3), 76, rw / 3 - 2, 17, "+" + fmt(q), () -> { num.setLength(0); num.append(q); confirmSet = false; });
            }
            add(rx, 98, rw, 22, "AGREGAR dinero (suma)", this::doAdd);
            add(rx, 124, rw, 22, confirmSet ? "¿Seguro? Toca otra vez" : "ESTABLECER saldo exacto", this::doSet);
            add(rx, 150, rw / 2 - 2, 19, "Restaurar real", () -> { Save.devRevert(); Save.devGold = 5000; msg = "Saldos restaurados a los reales."; msgColor = 0xFF7AF0A0; confirmSet = false; });
            add(rx + rw / 2 + 2, 150, rw / 2 - 2, 19, confirmCommit ? "¿Seguro?" : "Guardar perfil", this::doCommit);
            add(rx, 172, rw, 19, "Probar en tienda de prueba", () -> game.go(RunScreen.sandboxShop(game, ClassDef.ALL[Math.max(0, Math.min(ClassDef.ALL.length - 1, Save.S.lastClass))], () -> new Economy(game))));
            add(w / 2f - 50, 236, 100, 20, "Volver", () -> back());
        }

        private void doAdd() {
            long a = amount();
            if (a <= 0) { msg = "Escribe una cantidad mayor que 0."; msgColor = 0xFFFF6A6A; return; }
            long before = balance();
            long after = Math.min(CAP, before + a);
            setBalance(after);
            msg = "Agregado +" + fmt(after - before) + "  ·  Nuevo saldo: " + fmt(balance());
            msgColor = 0xFF7AF0A0; Snd.sfx("coin", 0.9f); confirmSet = false;
        }

        private void doSet() {
            if (num.length() == 0) { msg = "Escribe la cantidad exacta."; msgColor = 0xFFFF6A6A; return; }
            if (!confirmSet) { confirmSet = true; layout(); return; }
            confirmSet = false;
            long before = balance();
            setBalance(amount());
            msg = "Saldo establecido: " + fmt(before) + " > " + fmt(balance());
            msgColor = 0xFFFFD25A; Snd.sfx("coin", 0.9f); layout();
        }

        private void doCommit() {
            if (Save.devSoulsBackup < 0) { msg = "No hay cambios temporales de almas que guardar."; msgColor = 0xFFFFD25A; return; }
            if (!confirmCommit) { confirmCommit = true; layout(); return; }
            confirmCommit = false;
            Save.devCommit();
            msg = "Almas guardadas en el perfil: " + fmt(Save.S.souls);
            msgColor = 0xFFFF9A5A; layout();
        }

        @Override boolean back() { game.go(new Menu(game)); return true; }

        @Override void key(int code, boolean down) {
            if (!down) return;
            if (code >= '0' && code <= '9') { if (num.length() < 9) num.append((char) code); confirmSet = false; return; }
            if (code == 8 || code == 127) { if (num.length() > 0) num.setLength(num.length() - 1); return; }
            super.key(code, down);
        }

        @Override void update(float dt) { bg.update(dt, W()); }

        @Override void render(Platform.Gfx g) {
            int w = W();
            bg.render(g, w, 0.65f);
            UI.big.center(g, "ECONOMÍA Y RECURSOS", w / 2f, 8, UI.GOLD, 1f);
            UI.small.center(g, "Almas: " + fmt(Save.S.souls) + (Save.devSoulsBackup >= 0 ? " (temporal, real: " + fmt(Save.devSoulsBackup) + ")" : "") + "    Oro de prueba: " + fmt(Save.devGold), w / 2f, 30, 0xFFE8E0E0, 1f);
            UI.small.center(g, "Editando: " + (target == 0 ? "ALMAS del perfil (temporal)" : "ORO de la arena y tienda de prueba"), w / 2f, 42, UI.GREY, 1f);
            UI.panel(g, 1, 16, 56, 112, 18, 1f);
            UI.small.center(g, num.length() == 0 ? "0" : fmt(amount()), 72, 61, 0xFFF0E8E0, 1f);
            drawButtons(g);
            if (!msg.isEmpty()) UI.small.center(g, msg, w / 2f, 214, msgColor, 1f);
            UI.small.center(g, "Nada se guarda en el perfil salvo que pulses Guardar perfil.", w / 2f, 226, UI.GREY, 0.8f);
        }
    }
}
