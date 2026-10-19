package com.julianfarks.roguelike.core;

import java.util.Map;

/**
 * Pruebas del tutorial inicial (solo banco headless; BOT_TUTTEST=1 / BOT_TUTSCENE=touch|kb|pad desde DebugBot).
 * Usan el motor real (RunScreen, Save, Level, Input). NO son pruebas en un Android ni en un Windows real.
 */
final class TutorialProbe {
    private TutorialProbe() {}
    static boolean done;
    static int fails, oks;
    static void ck(String n, boolean ok) { System.out.println("AT " + (ok ? "OK    " : "FALLA ") + n); if (ok) oks++; else fails++; }

    static RunScreen scr; static Game game;

    /** Estado "primera mazmorra del perfil": cumple todas las condiciones de entrada salvo la marca guardada. */
    static void firstDungeon() {
        RunState r = scr.rs;
        r.stage = 0; r.visited.clear(); r.visited.add(0); r.roomNo = 0; r.bossKills = 0; r.infinite = false; r.biome = Biome.ALL[0];
    }

    static boolean enter(int type) { scr.loadRoom(type); return scr.tut.active; }

    static String saved() { return game.P.store().get("save", ""); }

    static boolean step(Game g, RunScreen r) {
        if (done) return true;
        done = true;
        game = g; scr = r;
        for (int c : new int[]{'A', 'D', 'W', 'S', 37, 38, 39, 40, 'J', 'K', 32, 10}) g.key(c, false);   // suelta lo que tuviera pulsado el bot
        System.out.println("AT inicio tutorial");
        try { run(); } catch (RuntimeException e) { e.printStackTrace(System.out); ck("sin excepciones: " + e, false); }
        System.out.println("AT FIN ok=" + oks + " fallos=" + fails);
        return true;
    }

    static void run() {
        Input in = scr.in;
        // 1. perfil nuevo, primera mazmorra
        Save.S.tutMask = 0; firstDungeon();
        ck("1 perfil nuevo: aparece en la primera sala de la primera mazmorra", enter(Room.COMBAT));
        // no aparece en el centro (hub) ni en salas que no son la primera
        scr.tut.close(); Save.S.tutMask = 0;
        firstDungeon(); scr.rs.roomNo = 2;
        ck("1b perfil nuevo: no aparece en la sala 3 (solo en la primera)", !enter(Room.COMBAT));
        firstDungeon(); ck("1c perfil nuevo: no aparece en el santuario", !enter(Room.HUB));
        // 2. cerrar -> queda registrado (y escrito en el guardado)
        Save.S.tutMask = 0; firstDungeon(); enter(Room.COMBAT);
        scr.tut.close();
        ck("2 cerrar: marca de controles en memoria", Tutorial.done(Tutorial.CONTROLS) && !scr.tut.active);
        ck("2b cerrar: escrito en el guardado (tuts)", saved().contains("\"tuts\":1") || saved().contains("\"tuts\":3"));
        // 2c. verlo unos segundos ya lo da por visto aunque se cierre el juego sin pulsar nada
        Save.S.tutMask = 0; firstDungeon(); enter(Room.COMBAT);
        for (int i = 0; i < 45; i++) scr.tut.update(0.1f, in, true);
        ck("2c visto 3 s: guardado aunque siga abierto", Tutorial.done(Tutorial.CONTROLS) && scr.tut.active);
        scr.tut.close();
        // 2d. completarlo haciendo las acciones
        Save.S.tutMask = 0; firstDungeon(); enter(Room.COMBAT);
        for (int i = 0; i < 10; i++) scr.tut.update(0.1f, in, true);
        ck("2d paso inicial = movimiento", scr.tut.step() == 0);
        in.key('D', true); scr.tut.update(0.1f, in, true); in.key('D', false);
        ck("2e moverse avanza a acciones", scr.tut.step() == 1);
        in.key('W', true); scr.tut.update(0.1f, in, true); in.endFrame(); in.key('W', false);
        in.key('J', true); scr.tut.update(0.1f, in, true); in.endFrame(); in.key('J', false);
        ck("2f saltar y atacar avanzan a esquiva", scr.tut.step() == 2);
        in.key('K', true); scr.tut.update(0.1f, in, true); in.endFrame(); in.key('K', false);
        ck("2g rodar completa los pasos", scr.tut.step() == -1);
        for (int i = 0; i < 20; i++) scr.tut.update(0.1f, in, true);
        ck("2h al completar se cierra solo", !scr.tut.active && Tutorial.done(Tutorial.CONTROLS));
        // 2i. cerrar con Intro
        Save.S.tutMask = 0; firstDungeon(); enter(Room.COMBAT);
        for (int i = 0; i < 6; i++) scr.tut.update(0.1f, in, true);
        in.key(10, true); scr.tut.update(0.1f, in, true); in.key(10, false);
        ck("2i Intro cierra el tutorial", !scr.tut.active && Tutorial.done(Tutorial.CONTROLS));

        // 3. tras derrotar al primer jefe y entrar al siguiente bioma
        Tutorial.complete(Tutorial.ALL);
        RunState r = scr.rs;
        r.bossKills = 1; r.stage = 1; r.visited.add(1); r.biome = Biome.ALL[1]; r.roomNo = 0;
        ck("3 siguiente bioma tras el jefe: no aparece", !enter(Room.COMBAT));
        // 3b. aunque se cumplan TODAS las condiciones de entrada de la primera mazmorra, la marca guardada manda
        firstDungeon();
        ck("3b estado de primera mazmorra pero ya visto: no aparece", !enter(Room.COMBAT));
        // 4. otros pisos, salas y mazmorras
        boolean any = false;
        int[] tipos = {Room.COMBAT, Room.ELITE, Room.SHOP, Room.FORGE, Room.BLESSING, Room.REST, Room.TREASURE, Room.BOSS, Room.HUB};
        for (int b = 0; b < 4; b++) {
            for (int k = 0; k < tipos.length; k++) {
                r.biome = Biome.ALL[b]; r.stage = Biome.ALL[b].tier; r.roomNo = k % 5; r.floor = b;
                any |= enter(tipos[k]);
            }
        }
        ck("4 otros biomas, pisos y salas: nunca aparece", !any);
        r.floor = 0;
        // 5. morir y empezar otra partida
        Save.S.tutMask = 0; firstDungeon(); enter(Room.COMBAT);
        try {
            java.lang.reflect.Method m = RunScreen.class.getDeclaredMethod("endRun", boolean.class); m.setAccessible(true); m.invoke(scr, false);
        } catch (ReflectiveOperationException e) { ck("endRun reflectivo: " + e, false); }
        ck("5 morir con el tutorial abierto: queda como visto", Tutorial.done(Tutorial.ALL));
        firstDungeon(); ck("5b nueva partida tras morir: no aparece", !enter(Room.COMBAT));
        // 6. cerrar y volver a abrir el juego
        Save.load(game.P);
        ck("6 reabrir el juego: sigue marcado", Tutorial.done(Tutorial.CONTROLS) && Tutorial.done(Tutorial.PORTAL));
        firstDungeon(); ck("6b reabrir el juego: no aparece", !enter(Room.COMBAT));
        // 7. guardado antiguo (sin el campo nuevo)
        String cur = saved();
        Map<String, Object> d = Json.parseObj(cur);
        int souls0 = Json.i(d, "souls", 0);
        d.remove("tuts"); d.put("tut", Boolean.FALSE); d.put("runs", 4.0); d.put("souls", 777.0);
        game.P.store().put("save_bak_tuts", "");
        game.P.store().put("save", Json.write(d)); game.P.store().commit();
        Save.load(game.P);
        ck("7 guardado antiguo con partidas jugadas: no se fuerza el tutorial", Tutorial.done(Tutorial.CONTROLS));
        ck("7b guardado antiguo: progreso intacto (almas)", Save.S.souls == 777 && Save.S.runs == 4);
        ck("7c copia de seguridad previa a la migracion", !game.P.store().get("save_bak_tuts", "").isEmpty() && game.P.store().get("save_bak_tuts", "").contains("\"souls\":777"));
        firstDungeon(); ck("7d guardado antiguo: no aparece", !enter(Room.COMBAT));
        d.put("tut", Boolean.TRUE); d.put("runs", 0.0); d.put("st_started", 0.0); d.remove("tuts");
        game.P.store().put("save", Json.write(d)); game.P.store().commit(); Save.load(game.P);
        ck("7e guardado antiguo con tut=true: visto", Tutorial.done(Tutorial.ALL));
        d.put("tut", Boolean.FALSE); d.remove("tuts");
        game.P.store().put("save", Json.write(d)); game.P.store().commit(); Save.load(game.P);
        ck("7f guardado antiguo sin partidas (jugador nuevo): se mostrara una vez", Save.S.tutMask == 0);
        // 8. perfil nuevo (reiniciar progreso)
        Tutorial.complete(Tutorial.ALL);
        int lang0 = Save.S.lang;
        Save.S.reset();
        ck("8 reiniciar progreso: tutorial pendiente otra vez", Save.S.tutMask == 0 && Save.S.lang == lang0);
        firstDungeon(); ck("8b perfil nuevo: aparece en su primera mazmorra", enter(Room.COMBAT));
        scr.tut.close();
        firstDungeon(); ck("8c ... y no se repite en el mismo perfil", !enter(Room.COMBAT));
        // modos que nunca lo muestran
        Save.S.tutMask = 0; firstDungeon(); scr.rs.infinite = true;
        ck("9 modo infinito: no aparece", !enter(Room.COMBAT));
        scr.rs.infinite = false;
        // el tutorial del portal es independiente del de controles
        Save.S.tutMask = Tutorial.CONTROLS;
        ck("10 tutoriales con estado propio (controles visto, portal pendiente)", Tutorial.done(Tutorial.CONTROLS) && !Tutorial.done(Tutorial.PORTAL));
    }

    // ------------------------------------------------------------------ escenas (capturas + geometria)
    static int sceneStart = -1;
    static int drawBase;

    static void scene(Game g, RunScreen r, Level lv, Player p, int frame, String mode) {
        game = g; scr = r;
        if (sceneStart < 0) {
            sceneStart = frame;
            for (int c : new int[]{'A', 'D', 'W', 'S', 37, 38, 39, 40, 'J', 'K', 32, 10}) g.key(c, false);
            Save.S.tutMask = 0; firstDungeon();
            g.lastDevice = mode.equals("touch") ? 0 : mode.equals("pad") ? 2 : 1;
            scr.loadRoom(Room.COMBAT);
            System.out.println("AT escena frame=" + frame + " " + mode + " activo=" + scr.tut.active + " ancho=" + scr.W() + " alto=" + ViewSize.h + " touchUi=" + g.touchUiVisible());
            return;
        }
        int f = frame - sceneStart;
        Input in = scr.in;
        if (f == 150) drawBase = Tutorial.drawCount;
        if (f == 190) ck("panel dibujado exactamente 1 vez por fotograma", Tutorial.drawCount - drawBase == 40);
        if (f == 195) report(r, "paso 0 (movimiento)");
        if (f == 200) g.key('D', true);
        if (f == 210) g.key('D', false);
        if (f == 215) ck("paso 1 tras moverse", scr.tut.step() == 1);
        if (f == 260) { g.key('W', true); }
        if (f == 262) { g.key('W', false); g.key('J', true); }
        if (f == 264) g.key('J', false);
        if (f == 268) ck("paso 2 tras saltar y atacar", scr.tut.step() == 2);
        if (f == 300) g.key('K', true);
        if (f == 302) g.key('K', false);
        if (f == 306) ck("completado tras rodar", scr.tut.step() == -1);
        if (f == 320) {
            // el boton Entendido responde al toque (se reabre para probarlo)
            Save.S.tutMask = 0; scr.tut.close(); Save.S.tutMask = 0; firstDungeon(); scr.loadRoom(Room.COMBAT);
        }
        if (f == 520) {
            report(r, "reabierto");
            boolean hit = scr.tut.hitButton(scr.tut.bx + 3, scr.tut.by + 3);
            ck("boton Entendido: area de toque dentro del panel", hit && scr.tut.bx >= scr.tut.qx && scr.tut.bx + scr.tut.bw <= scr.tut.qx + scr.tut.qw && scr.tut.by + scr.tut.bh <= scr.tut.qy + scr.tut.qh);
            scr.touch(0, Platform.ACTION_DOWN, scr.tut.bx + 3, scr.tut.by + 3);
            scr.touch(0, Platform.ACTION_UP, scr.tut.bx + 3, scr.tut.by + 3);
            ck("tocar Entendido cierra y guarda", !scr.tut.active && Tutorial.done(Tutorial.CONTROLS) && (saved().contains("\"tuts\":1") || saved().contains("\"tuts\":3")));
        }
        if (f == 560) {
            boolean bad = false;
            for (String s : PrepScreen.fitErrors) if (s.contains("tutorial")) { System.out.println("AT ENCAJE " + s); bad = true; }
            ck("sin errores de encaje del tutorial (" + mode + ", " + I18n.code() + ")", !bad);
            System.out.println("AT FIN ok=" + oks + " fallos=" + fails);
            System.exit(fails == 0 ? 0 : 1);
        }
    }

    /** Geometria: el panel debe estar dentro de la pantalla y no pisar la vida ni ningun boton tactil visible. */
    static void report(RunScreen r, String when) {
        Tutorial t = r.tut;
        int w = r.W();
        float h = ViewSize.h;
        boolean inside = t.qx >= 0 && t.qy >= 0 && t.qx + t.qw <= w && t.qy + t.qh <= h;
        ck("panel dentro de la pantalla " + w + "x" + (int) h + " (" + when + ") [" + (int) t.qx + "," + (int) t.qy + " " + (int) t.qw + "x" + (int) t.qh + "]", inside);
        float hpW = UI.hpFrame != null ? UI.hpFrame.w : 90;
        boolean hpHit = t.qx < 8 + hpW + 2 && t.qy < 38 && t.qx + t.qw > 8 && t.qy + t.qh > 8;
        ck("panel no pisa la barra de vida/ultimate", !hpHit);
        boolean resHit = t.qy < 30 && t.qx + t.qw > w - 110;
        ck("panel no pisa oro/almas ni pausa", !resHit);
        if (r.game.touchUiVisible()) {
            String bad = "";
            for (int i = 0; i < Input.B_COUNT; i++) {
                Input.Btn b = r.in.btn[i];
                if (!b.visible) continue;
                float cx = Math.max(t.qx, Math.min(b.cx, t.qx + t.qw)), cy = Math.max(t.qy, Math.min(b.cy, t.qy + t.qh));
                if ((b.cx - cx) * (b.cx - cx) + (b.cy - cy) * (b.cy - cy) < b.r * b.r) bad += " " + Input.NAMES[i];
            }
            ck("panel no pisa botones tactiles visibles" + (bad.isEmpty() ? "" : ":" + bad), bad.isEmpty());
        }
    }
}
