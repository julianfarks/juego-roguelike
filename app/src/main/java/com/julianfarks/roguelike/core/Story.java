package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Datos de la campana narrativa "Las Siete Espadas del Fin": cinematicas, dialogos y registro de progreso.
 * Todo vive aqui como datos para poder anadir escenas/finales sin tocar el motor (Cinematic, Dlg).
 * Progreso en Save.S.story: [0] intro vista, [1] final secreto desbloqueado, [2] final visto, [3..5] veces que se hablo con cada NPC.
 */
final class Story {
    private Story() {}

    static final int S_INTRO = 0, S_FINAL_UNLOCK = 1, S_FINAL_SEEN = 2, S_NPC0 = 3;

    // ------------------------------------------------------------------ cinematicas
    static final class Slide {
        final int bg; final String who, text;
        Slide(int bg, String who, String text) { this.bg = bg; this.who = who; this.text = text; }
    }

    static final class Cine {
        final String id, title; final Slide[] slides;
        Cine(String id, String title, Slide[] s) { this.id = id; this.title = title; this.slides = s; }
    }

    static final int BG_ABYSS = 0, BG_SEVEN = 1, BG_HUNTER = 2, BG_DESCENT = 3, BG_RELICS = 4, BG_SHATTER = 5, BG_TRUTH = 6, BG_DAWN = 7;

    static Slide sl(int bg, String t) { return new Slide(bg, null, t); }
    static Slide sl(int bg, String who, String t) { return new Slide(bg, who, t); }

    static final Cine INTRO = new Cine("intro", "La caída del cielo", new Slide[]{
            sl(BG_ABYSS, "Hace mil años, el cielo se partió sobre el Abismo Eterno."),
            sl(BG_ABYSS, "Una luna roja se alzó y ya nunca volvió a ponerse. Bajo ella despertó algo antiguo, y hambriento."),
            sl(BG_ABYSS, "Los reinos cayeron uno tras otro. Nadie recordó su nombre. Solo su sombra."),
            sl(BG_SEVEN, "Pero siete espadachines se negaron a huir."),
            sl(BG_SEVEN, "Cada uno empuñaba una espada nacida de una creencia: el Honor, el Silencio, la Voluntad, la Libertad, la Paciencia, la Vida y el Sacrificio."),
            sl(BG_SEVEN, "No eran simples armas. Eran sellos. Unidas, podían encadenar a la Luna de Sangre."),
            sl(BG_HUNTER, "Pero el Cazador no podía morir; solo ser contenido. Cada espada se quebró contra su sombra."),
            sl(BG_HUNTER, "Los guardianes cayeron, y sus ocho reliquias se perdieron en lo profundo del abismo."),
            sl(BG_DESCENT, "Ahora el Sello se debilita. La luna vuelve a sangrar."),
            sl(BG_DESCENT, "Tú desciendes sin nombre, con una espada prestada y una única certeza:"),
            sl(BG_DESCENT, "alguien tiene que terminar lo que ellos no pudieron."),
    });

    static final Cine FINAL = new Cine("final", "El octavo espadachín", new Slide[]{
            sl(BG_RELICS, "Las ocho reliquias se elevan y forman un anillo de luz alrededor del Cazador."),
            sl(BG_RELICS, "El Sello, por fin completo, canta con las voces de los siete espadachines."),
            sl(BG_SHATTER, "La Luna de Sangre se quiebra. No cae: se apaga."),
            sl(BG_SHATTER, "El Cazador baja la mirada hacia sus propias manos. Por primera vez en mil años, recuerda quién fue."),
            sl(BG_TRUTH, "El Cazador", "Fui el octavo espadachín. Mi creencia era la Victoria, cueste lo que cueste."),
            sl(BG_TRUTH, "El Cazador", "Por eso las siete espadas jamás pudieron matarme: me habían forjado a mí, también."),
            sl(BG_TRUTH, "El Cazador", "Gracias, portador. Rompiste el ciclo que yo empecé."),
            sl(BG_DAWN, "Amaneció sobre el Abismo por primera vez en mil años."),
            sl(BG_DAWN, "Las espadas por fin descansan. El portador no tiene nombre... pero el mundo recordará su camino."),
    });

    static final Cine[] CINES = {INTRO, FINAL};

    static Cine cine(String id) { for (Cine c : CINES) if (c.id.equals(id)) return c; return null; }

    // ------------------------------------------------------------------ dialogos
    static final class Choice {
        final String label, res; float heal; int gold, souls, potion; boolean needPotion;
        Choice(String label, String res) { this.label = label; this.res = res; }
        Choice heal(float h) { heal = h; return this; }
        Choice gold(int g) { gold = g; return this; }
        Choice souls(int s) { souls = s; return this; }
        Choice potion(int p) { potion = p; return this; }
        Choice needPotion() { needPotion = true; return this; }
    }

    static final class Dialog {
        final String id, title, who; final List<String[]> lines = new ArrayList<>(); final List<Choice> choices = new ArrayList<>();
        int npc = -1;
        Dialog(String id, String title, String who) { this.id = id; this.title = title; this.who = who; }
        Dialog say(String t) { lines.add(new String[]{who, t}); return this; }
        Dialog say(String w, String t) { lines.add(new String[]{w, t}); return this; }
        Dialog opt(Choice c) { choices.add(c); return this; }
    }

    static final String[] NPC_NAMES = {"Aldren", "Vesper", "Sylwen"};
    static final String[] NPC_TITLES = {"Guardián herido", "Mercader enmascarado", "Espíritu del bosque"};

    static final Map<String, Dialog> DIALOGS = new LinkedHashMap<>();

    private static Dialog reg(Dialog d, int npc) { d.npc = npc; DIALOGS.put(d.id, d); return d; }

    static {
        // ---- Aldren, guardian del Alba (Honor)
        reg(new Dialog("aldren_1", "Guardián herido", "Aldren")
                .say("Ugh... por fin alguien. Baja la espada, no soy una de esas cosas.")
                .say("Fui Guardián del Alba, de los que juraron el Honor. Me hirieron al intentar volver a la superficie.")
                .say("¿Tendrías una poción? Solo una.")
                .opt(new Choice("Darle una poción", "Que el Alba te cuide. Toma, es todo lo que me queda.").needPotion().potion(-1).gold(45).souls(5))
                .opt(new Choice("Dejarlo", "Lo entiendo. En el abismo cada gota cuenta.")), 0);
        reg(new Dialog("aldren_2", "Guardián herido", "Aldren")
                .say("Otra vez tú. Sigo vivo, ya ves. Terco como todos los del Alba.")
                .say("A veces oigo las espadas cantar cuando duermo. Cantan bajito, como si lloraran.")
                .opt(new Choice("Acompañarlo un rato", "Gracias. Un guardián no debería caer solo.").heal(0.15f))
                .opt(new Choice("Seguir mi camino", "Ve. Y recuerda: el honor no es ganar, es no soltar la espada.")), 0);
        reg(new Dialog("aldren_3", "Guardián herido", "Aldren")
                .say("Has llegado muy lejos. Llevas el peso de las reliquias, lo noto en cómo caminas.")
                .say("Hay algo que nunca contamos: ocho reliquias, pero solo siete espadas.")
                .say("Siempre me pregunté quién fue el octavo. Quizás por eso el Cazador no se detiene.")
                .opt(new Choice("Recordarlo", "Si lo averiguas... dile que el Alba aún lo espera.").heal(0.25f).souls(10)), 0);

        // ---- Vesper, mercader enmascarado (miente, teme)
        reg(new Dialog("vesper_1", "Mercader enmascarado", "Vesper")
                .say("Shh, shh... bienvenido, cliente. Vesper vende lo que el abismo escupe.")
                .say("¿El Cazador? Cuento de niños. Una luna pintada en el cielo, nada más.")
                .say("Pero si quieres una ventaja, tengo un secreto barato. Solo veinte monedas.")
                .opt(new Choice("Comprar el secreto (20 oro)", "Para vencer a cualquier jefe no esquives: solo ataca. Confía en Vesper... jeje.").gold(-20))
                .opt(new Choice("Presionarlo", "¡Está bien, está bien! Sirvo a quienes siguen la luna... toma, no me hagas daño.").gold(60))
                .opt(new Choice("Marcharse", "Tú te lo pierdes, cliente.")), 1);
        reg(new Dialog("vesper_2", "Mercader enmascarado", "Vesper")
                .say("Otra vez por aquí. Vesper no mintió, no. Vesper solo... omitió.")
                .say("Dicen que bajo la máscara no hay nada. Yo digo que hay demasiado.")
                .opt(new Choice("Aceptar su regalo", "Una poción por las molestias. Gratis. Esta vez de verdad.").potion(1))
                .opt(new Choice("No fiarme", "Sabia decisión. Vesper tampoco se fiaría.")), 1);
        reg(new Dialog("vesper_fear", "Mercader enmascarado", "Vesper")
                .say("T-tú... llevas las marcas de los guardianes caídos.")
                .say("No. No, no, no. Hoy Vesper no vende nada. Vesper no te conoce.")
                .say("Vete, por favor. Antes de que la luna te vea aquí.")
                .opt(new Choice("Dejarlo en paz", "...gracias. Que el abismo sea benévolo contigo.")), 1);

        // ---- Sylwen, espiritu del bosque (Vida)
        reg(new Dialog("sylwen_refuse", "Espíritu del bosque", "Sylwen")
                .say("Las raíces susurran que aún eres brote.")
                .say("Vuelve cuando hayas caído y te hayas levantado. Entonces hablaremos.")
                .opt(new Choice("Asentir", "El bosque recuerda a quienes regresan.")), 2);
        reg(new Dialog("sylwen_1", "Espíritu del bosque", "Sylwen")
                .say("Hueles a ceniza y a promesa. Eso es raro por aquí.")
                .say("La Vida fue la creencia de mi dueña: que todo lo que cae vuelve a ser semilla. Incluso la luna.")
                .say("Bebe de mi savia si quieres. Pero la savia también recuerda.")
                .opt(new Choice("Beber la savia", "Que las raíces te sostengan. Y que no olvides lo que viste.").heal(0.7f))
                .opt(new Choice("Rechazar", "Cautela. Tu espada es más sabia que tú... por ahora.").souls(15)), 2);
    }

    static Dialog byId(String id) { return DIALOGS.get(id); }

    /** Dialogo que corresponde a un NPC segun el progreso real (reliquias, jefes, veces hablado). */
    static Dialog npcDialog(int npc, int relics, int bossKills, int meets) {
        switch (npc) {
            case 0: return byId(meets == 0 ? "aldren_1" : relics >= 6 ? "aldren_3" : "aldren_2");
            case 1: return byId(relics >= 5 || bossKills >= 3 ? "vesper_fear" : meets == 0 ? "vesper_1" : "vesper_2");
            default: return byId(relics < 2 ? "sylwen_refuse" : "sylwen_1");
        }
    }

    // ------------------------------------------------------------------ progreso
    static boolean introSeen() { return Save.S.story[S_INTRO] != 0; }
    static boolean finalUnlocked() { return Save.S.story[S_FINAL_UNLOCK] != 0; }
    static void mark(int idx) { if (Save.S.story[idx] == 0) { Save.S.story[idx] = 1; Save.S.write(); } }

    /** El final secreto solo existe si se derroto a TODOS los jefes requeridos: 8 reliquias (Sello forjado) y el Cazador. */
    static boolean allBossesDefeated() { return Save.S.sealForged() && Save.S.finalBeaten; }

    /** Llamar al derrotar al jefe final: comprueba el progreso real y persiste el desbloqueo. */
    static boolean tryUnlockFinal() {
        if (!allBossesDefeated()) return false;
        mark(S_FINAL_UNLOCK);
        return true;
    }
}
