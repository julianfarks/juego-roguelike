package com.julianfarks.roguelike.core;

/** Pantallas sencillas: carga, titulo, opciones y creditos. */
final class Screens {
    private Screens() {}

    /** Pantalla de inicio a la que se vuelve: el centro de operaciones si se esta dentro de el, o el titulo. */
    static Screen home(Game g) { return Ops.active ? new Ops(g) : new Title(g); }

    // =================================================================== fondo del titulo (compartido)
    static final class TitleBg {
        final Particles ps = new Particles();
        final Rng rng = new Rng(77);
        float t;
        final Platform.Img[] layer = new Platform.Img[4];

        TitleBg() { for (int i = 0; i < 4; i++) layer[i] = Assets.img("ui/ui_title_" + i + ".png"); }

        void update(float dt, int w) {
            t += dt;
            if (rng.chance(dt * 18)) ps.spawn(rng.f(0, w + 80), Platform.VIEW_H + 4, rng.f(-30, -6), -rng.f(14, 44), rng.f(3, 7), rng.chance(0.3f) ? 2 : 1, 0, rng.chance(0.5f) ? 0xFF5A30 : 0xFFB070, true);
            ps.update(dt);
        }

        void render(Platform.Gfx g, int w, float dim) {
            float s = Math.max(w / 512f, Platform.VIEW_H / 288f);
            float dw = 512 * s, dh = 288 * s;
            float y = (Platform.VIEW_H - dh) / 2f;
            float[] speed = {0f, 3f, 8f, 16f};
            g.clear(0xFF0A0408);
            for (int i = 0; i < 4; i++) {
                Platform.Img im = layer[i];
                if (im == null) continue;
                if (i == 0) {
                    g.image(im, 0, 0, im.w, im.h, Math.round((w - dw) / 2f), Math.round(y), Math.round(dw), Math.round(dh), 0, 0, 1f);
                } else {
                    float off = (t * speed[i]) % dw;
                    for (float x = -off; x < w; x += dw) g.image(im, 0, 0, im.w, im.h, Math.round(x), Math.round(y), Math.round(dw), Math.round(dh), 0, 0, 1f);
                }
                if (i == 1) {   // niebla roja sobre la silueta lejana
                    g.rect(0, 150, w, 70, Mth.withAlpha(0x601020, 40), true);
                }
            }
            ps.render(g, 0, 0);
            if (dim > 0) g.rect(0, 0, w, Platform.VIEW_H, Mth.withAlpha(0x000000, (int) (dim * 255)), false);
            if (UI.vignette != null) g.image(UI.vignette, 0, 0, UI.vignette.w, UI.vignette.h, 0, 0, w, Platform.VIEW_H, 0, 0, 0.75f);
        }
    }

    // =================================================================== carga
    static final class Boot extends Screen {
        private final Runnable[] tasks;
        private int idx;
        private float shown;
        private String[] tips = {"Rueda con el botón de esquivar para ser invulnerable un instante.",
                "Las reliquias de los jefes se conservan entre partidas.",
                "Gasta almas en el Santuario para mejorar a tu personaje.",
                "Cada sala puede esconder una bendición, una forja o un mercader.",
                "Reúne las 8 reliquias para forjar el Sello y despertar al Cazador."};
        private int tip;

        Boot(Game g) {
            super(g);
            final Platform P = g.P;
            tasks = new Runnable[]{
                    () -> UI.load(),
                    () -> Snd.preload(P),
                    () -> { for (String k : new String[]{"fx_hit", "fx_proj", "fx_dust", "fx_slash_sword", "fx_slash_big", "fx_stab", "fx_explosion", "fx_ring"}) Assets.fx(k); },
                    () -> { for (String k : new String[]{"fx_fire", "fx_ice", "fx_lightning", "fx_shadow", "fx_void", "fx_holy", "fx_thorn", "fx_blood", "fx_rock", "fx_star", "fx_tele", "fx_whirl", "fx_smoke", "fx_shield", "fx_shock", "fx_heal"}) Assets.fx(k); },
                    () -> { for (ClassDef c : ClassDef.ALL) { Assets.img("sprites/portrait_" + c.key + ".png"); Assets.img("sprites/splash_" + c.key + ".png"); } },
                    () -> { for (String k : new String[]{"pick_gold", "pick_soul", "pick_heart", "pick_potion", "pick_relic", "prop_altar", "prop_chest", "prop_door", "prop_portal", "prop_fountain", "prop_forge", "prop_merchant", "prop_pot", "prop_sanctuary"}) Assets.spr(k); },
                    () -> { for (int i = 0; i < 4; i++) Assets.img("ui/ui_title_" + i + ".png"); },
            };
            tip = (int) (Math.random() * tips.length);
        }

        @Override void update(float dt) {
            shown += dt;
            if (idx < tasks.length) {
                tasks[idx++].run();
            } else if (shown > 1.6f) {
                game.go(new Title(game));
            }
        }

        @Override void render(Platform.Gfx g) {
            int w = W();
            g.clear(0xFF07040A);
            if (UI.logo != null) {
                float a = Mth.clamp(shown / 0.8f, 0, 1);
                g.image(UI.logo, 0, 0, UI.logo.w, UI.logo.h, Math.round(w / 2f - UI.logo.w / 2f), 56, UI.logo.w, UI.logo.h, 0, 0, a);
                UI.light(g, w / 2f, 98, 120, 0xA01020, 0.18f * a);
            }
            float p = Mth.clamp(idx / (float) tasks.length, 0, 1);
            float bx = w / 2f - 80, by = 190;
            g.rect(bx - 2, by - 2, 164, 8, 0xFF2A1A20, false);
            g.rect(bx, by, 160 * p, 4, 0xFFC8283C, false);
            if (UI.small != null) {
                UI.small.center(g, "Cargando...", w / 2f, 170, 0xFFB0A0A8, 1f);
                UI.small.center(g, tips[tip], w / 2f, 226, 0xFF807078, 1f);
            }
        }
    }

    // =================================================================== titulo
    static final class Title extends Screen {
        private final TitleBg bg;
        private float logoT;

        Title(Game g) { super(g); bg = new TitleBg(); }

        @Override void enter() {
            Ops.active = false;
            Snd.music("mus_title", true);
            Snd.ambient(null, 0);
            layout();
        }

        @Override void layout() {
            hits.clear();
            int w = W();
            float bw = 150, bh = 19, x = w / 2f - bw / 2f, y = 96, st = 21;
            add(x, y, bw, bh + 5, "Comenzar", () -> game.go(new Ops(game)));
            add(x, y + st + 6, bw, bh, "Opciones", () -> game.go(new Options(game, false)));
            add(x, y + st * 2 + 6, bw, bh, "Códigos", () -> game.go(new CodesScreen(game)));
            add(x, y + st * 3 + 6, bw, bh, "Créditos", () -> game.go(new Credits(game, false)));
            if (Save.S.devUnlocked) add(6, 26, 116, 17, "Modo Desarrollador", () -> game.go(new DevScreens.Menu(game)));
        }

        @Override void update(float dt) {
            bg.update(dt, W());
            logoT += dt;
        }

        @Override boolean back() { game.P.quit(); return true; }

        @Override void render(Platform.Gfx g) {
            int w = W();
            bg.render(g, w, 0.0f);
            // logo
            if (UI.logo != null) {
                float bob = (float) Math.sin(logoT * 1.4f) * 2f;
                float pul = 0.22f + 0.08f * (float) Math.sin(logoT * 2.2f);
                UI.light(g, w / 2f, 52 + bob, 130, 0xB01828, pul);
                g.image(UI.logo, 0, 0, UI.logo.w, UI.logo.h, Math.round(w / 2f - UI.logo.w / 2f), Math.round(14 + bob), UI.logo.w, UI.logo.h, 0, 0, 1f);
            }
            // botones
            g.rect(w / 2f - 90, 92, 180, 104, 0x55000000, false);
            drawButtons(g);
            if (UI.small != null) {
                UI.small.center(g, "Creador: JulianFarKs", w / 2f, 252, 0xFF9A8890, 1f);
                UI.iconC(g, "soul", w - 54, 14, 1f, 1f);
                UI.small.right(g, String.valueOf(Save.S.souls), w - 8, 9, UI.SOUL, 1f);
                UI.iconC(g, "relic", 14, 14, 1f, 1f);
                UI.small.draw(g, Save.S.relicCount() + "/8", 26, 9, UI.GOLD, 1f);
            }
        }
    }

    // =================================================================== opciones
    static final class Options extends Screen {
        private final boolean fromRun;
        private float confirmT;
        private final TitleBg bg;

        Options(Game g, boolean fromRun) { super(g); this.fromRun = fromRun; bg = new TitleBg(); }

        @Override void layout() {
            hits.clear();
            int w = W();
            float bw = 200, bh = 20, x = w / 2f - bw / 2f, y = 52, st = 24;
            Save s = Save.S;
            int i = 0;
            add(x, y + st * i++, bw, bh, "Música: " + (s.musicOn ? "SÍ" : "NO"), () -> { s.musicOn = !s.musicOn; Snd.applyVolumes(); s.write(); layout(); });
            add(x, y + st * i++, bw, bh, "Sonidos: " + (s.sfxOn ? "SÍ" : "NO"), () -> { s.sfxOn = !s.sfxOn; Snd.applyVolumes(); s.write(); layout(); });
            add(x, y + st * i++, bw, bh, "Vibración: " + (s.vibOn ? "SÍ" : "NO"), () -> { s.vibOn = !s.vibOn; s.write(); layout(); });
            add(x, y + st * i++, bw, bh, "Entrada: " + new String[]{"Automática", "Táctil", "Mando"}[s.inputMode], () -> { s.inputMode = (s.inputMode + 1) % 3; s.write(); layout(); });
            if (!fromRun) {
                add(x, y + st * i++, bw, bh, "Controles (teclado y mando)", () -> game.go(new ControlsScreen(game)));
                add(x, y + st * i++, bw, bh, "Organizar controles táctiles", () -> game.go(new ControlsEditor(game, false)));
                add(x, y + st * i++, bw, bh, confirmT > 0 ? "¿Seguro? Toca otra vez" : "Borrar progreso", () -> {
                    if (confirmT > 0) { Save.S.reset(); Snd.applyVolumes(); confirmT = 0; Snd.sfx("ui_back", 1f); }
                    else confirmT = 3f;
                    layout();
                });
            }
            add(x, y + st * i, bw, bh, "Volver", () -> back());
        }

        @Override boolean back() { if (fromRun) return false; game.go(home(game)); return true; }

        @Override void update(float dt) {
            bg.update(dt, W());
            if (confirmT > 0) { confirmT -= dt; if (confirmT <= 0) layout(); }
        }

        @Override void render(Platform.Gfx g) {
            int w = W();
            bg.render(g, w, 0.45f);
            UI.panel(g, 0, w / 2f - 120, 26, 240, 224, 0.95f);
            UI.big.center(g, "OPCIONES", w / 2f, 34, UI.GOLD, 1f);
            drawButtons(g);
            UI.small.center(g, "SwordsmanMagic: Eternal Abyss v2.1", w / 2f, 243, UI.GREY, 1f);
        }
    }

    // =================================================================== creditos
    static final class Credits extends Screen {
        private final boolean ending;
        private final TitleBg bg;
        private float scroll;
        private static final String[] LINES = {
                "#SWORDSMANMAGIC", "#ETERNAL ABYSS", "",
                "Un roguelike de acción en 2D", "inspirado en SwordmanMagic,", "mod de Minecraft de JulianFarKs", "",
                "-CREADOR", "JulianFarKs", "", "-IDEAS", "Team TKD y Chernobyl", "", "-BASADO EN", "un mod propio de Minecraft:", "SwordmanMagic", "", "-PRÓXIMAMENTE", "Mejoras en los niveles y diseños", "y en el menú de elegir el tipo de mundo", "",
                "-ARTE", "Pixel art generado a mano,", "personajes, jefes, enemigos y mundos", "",
                "-MÚSICA Y SONIDO", "Música original sintetizada,", "efectos para cada arma, jefe y habilidad", "",
                "-CLASES", "Paladín del Alba · Asesino de las Sombras", "Señor de las Llamas · Tempestad", "Guardián Glacial · Guardián Esmeralda",
                "Segador Carmesí · Coloso de Roca", "Vagabundo Estelar · Soberano de Acero", "",
                "-JEFES", "Rey Exánime · Coloso de Magma", "Reina de la Escarcha · Devorador del Vacío", "Ent Ancestral · Titán de la Tormenta",
                "Matriarca de Sangre · Guardián del Eclipse", "El Cazador, Dios Antiguo de la Luna de Sangre", "",
                "-GRACIAS POR JUGAR", "", "♥", "", "", ""};

        Credits(Game g, boolean ending) { super(g); this.ending = ending; bg = new TitleBg(); }

        @Override void enter() { Snd.music("mus_credits", true); layout(); }

        @Override void layout() {
            hits.clear();
            add(0, 0, 9999, 9999, null, () -> back()).plain = true;
        }

        @Override boolean back() { game.go(new Title(game)); return true; }

        @Override void update(float dt) {
            bg.update(dt, W());
            scroll += dt * 22f;
            if (scroll > LINES.length * 14 + 300) back();
        }

        @Override void render(Platform.Gfx g) {
            int w = W();
            bg.render(g, w, 0.5f);
            float y = Platform.VIEW_H - scroll + 20;
            for (String l : LINES) {
                if (y > -20 && y < Platform.VIEW_H + 10) {
                    float a = Mth.clamp(Math.min(y / 40f, (Platform.VIEW_H - y) / 40f), 0, 1);
                    if (l.startsWith("#")) UI.big.center(g, l.substring(1), w / 2f, y, UI.GOLD, a);
                    else if (l.startsWith("-")) UI.small.center(g, l.substring(1), w / 2f, y, 0xFF7A8A, a);
                    else UI.small.center(g, l, w / 2f, y, 0xE8E0E0, a);
                }
                y += l.startsWith("#") ? 22 : 14;
            }
            UI.small.center(g, "Toca para salir", w / 2f, 258, UI.GREY, 0.6f);
        }
    }
}
