package com.julianfarks.roguelike.core;

import java.nio.file.*;
import java.util.*;

/** Genera docs/BENDICIONES.md desde el catalogo real (Blessing.ALL / BlessData.syns()). Uso: /tmp/bc/run.sh BlessDocGen */
public class BlessDocGen {
    static final String[] CAT = {"A · Daño físico", "B · Magia y elementos", "C · Defensa, parry y supervivencia", "D · Velocidad, movilidad y evasión", "E · Proyectiles",
            "F · Recursos y cofres", "G · Invocaciones y compañeros", "H · Riesgo y recompensa", "I · Maldiciones y transformaciones", "J · Híbridas"};
    static final String[] RAR = {"común", "poco común", "rara", "épica", "legendaria"};
    static String e(String s) { return s.replace("|", "\\|"); }

    public static void main(String[] x) throws Exception {
        Blessing[] A = Blessing.ALL; BSyn[] S = BlessData.syns(); int[][] mo = BlessOffer.memberOf();
        int[][] cr = new int[10][5]; int[] byRar = new int[5], byCat = new int[10]; Set<Integer> syn = new HashSet<>();
        for (Blessing b : A) { cr[b.cat - 'A'][b.rar]++; byRar[b.rar]++; byCat[b.cat - 'A']++; }
        for (BSyn s : S) for (int id : s.members) syn.add(id);
        StringBuilder o = new StringBuilder();
        o.append("# Bendiciones (altares) — 200 bendiciones, 20 sinergias\n\n");
        o.append("> Documento GENERADO por `tools/tests/BlessDocGen.java` desde el catálogo real; el catálogo se edita en `tools/blessings/cat_*.py` y se regenera con `python3 tools/blessings/gen.py` + `python3 tools/i18n/build_catalogs.py`.\n\n");
        o.append("## Resumen\n\n- **200** bendiciones distintas (las **28** originales conservan id 0–27; las **172** nuevas son id 28–199), **").append(syn.size()).append("** de ellas participan en alguna de las **").append(S.length).append("** sinergias.\n");
        o.append("- 5 rarezas: ");
        for (int r = 0; r < 5; r++) o.append(RAR[r]).append(" ").append(byRar[r]).append(r < 4 ? " · " : "\n");
        o.append("- 10 categorías (A–J); 10 legendarias (una por categoría) con condiciones de aparición.\n\n");
        o.append("### Distribución por categoría y rareza\n\n| Categoría | Total | común | poco común | rara | épica | legendaria |\n|---|---|---|---|---|---|---|\n");
        for (int c = 0; c < 10; c++) o.append("| ").append(CAT[c]).append(" | ").append(byCat[c]).append(" | ").append(cr[c][0]).append(" | ").append(cr[c][1]).append(" | ").append(cr[c][2]).append(" | ").append(cr[c][3]).append(" | ").append(cr[c][4]).append(" |\n");
        o.append("\n");
        o.append(String.join("\n",
                "## Cómo funciona el motor",
                "",
                "Cada bendición nueva es **datos** (`BlessData`, generado) + un conjunto de **reglas** con la forma `DISPARADOR|condiciones|EFECTO:args|opciones` que interpreta `BRule.parse`; la lógica está en `BlessFx` (ganchos y condiciones) y `BlessEffects` (efectos). Una sinergia (`BSyn`) es un grupo de bendiciones: al tener `need` o más de sus miembros se añaden sus reglas.",
                "",
                "- **Disparadores**: golpe, crítico, remate, racha, muerte, daño recibido, bloqueo, parry, esquiva, rodar, habilidad, definitiva, proyectil, sala, sala limpia, jefe muerto, recogida, poción, salto, aterrizaje, vida baja, periódico, peligro superado, descarga, desbordamiento y pasivos (`MOD`).",
                "- **Efectos**: estados (quemar, congelar, ralentizar, envenenar, electrocutar, sangrar, maldecir), propagar, explosiones, cadenas, mejoras temporales, curar, escudo, enfriamientos, definitiva, proyectiles, oro, almas, carga arcana, descargas, invulnerabilidad breve, empujar/atraer, estelas, pociones, coste de vida/oro, ralentizar el tiempo, espíritus compañeros, etc.",
                "- **Opciones**: `icd` (reutilización por regla), `ch` (probabilidad), `n`, `every`, `k`, `aoe`, `what`, `src` (arma/habilidad/proyectil/daño periódico), `scale` (escala con el nivel de la bendición).",
                "",
                "### Límites de seguridad (sin bucles ni infinitos)",
                "",
                "- Un efecto **nunca** desencadena otro efecto (profundidad 1); solo `KILL` (hasta 3) y `DISCHARGED` (hasta 2) pueden encadenarse, de forma acotada.",
                "- Cada regla tiene reutilización (`icd`) y hay un tope global de **90 ejecuciones por segundo**.",
                "- Multiplicador de daño de bendiciones limitado a **×3**.",
                "- Curación por bendiciones limitada por sala (**25 %** de la vida máxima; **35 %** en jefe); oro ≤ 90 y almas ≤ 45 por sala; reducción de enfriamientos con cubo recargable; invulnerabilidad por efecto ≤ **0,6 s**; esquiva con anti-rebote de 0,5 s; coste de vida (`LOSEHP`) nunca baja del 12 % de la vida máxima.",
                "- Los proyectiles creados por bendiciones no generan nuevos eventos de proyectil (no hay cascadas).",
                "",
                "## Altares: selección de ofertas",
                "",
                "`BlessOffer.pick` elige 3 (o 4 con la mejora de oferta) bendiciones **distintas** entre las elegibles (nivel máximo no alcanzado, piso mínimo, requisitos de legendarias). El peso base depende de la rareza; se reduce si la categoría ya está en la oferta (variedad) y si la bendición ya se ofreció muchas veces en la partida; sube ligeramente (sin garantizar nada) si comparte sinergia con lo que ya tienes y con la suerte para raras. Como máximo **una legendaria por oferta**.",
                "",
                "Cada tarjeta muestra categoría, rareza (color), nivel, descripción y, sin saturar, la mejor sinergia relacionada (`+ nombre n/N`). La pantalla **Bendiciones activas** (pausa) lista las que tienes, con sus condiciones y las sinergias activas/en progreso. Al activarse una sinergia aparece el aviso «¡Sinergia activada!», con efecto de partículas y sonido.",
                "",
                "## Guardado",
                "",
                "La partida guarda solo el arreglo `bless` (nivel por id). Las partidas antiguas (28 entradas) se cargan en el arreglo de 200 sin perder datos; los ids 0–27 no cambian. El estado de ejecución (`BlessRt`: temporizadores, espíritus, canales) no se guarda: se reconstruye al cargar y al cambiar de sala/piso.",
                "",
                "## Pruebas",
                "",
                "Ver `tools/tests/bless_test.sh`: catálogo (unicidad, iconos, rarezas, sinergias, traducciones, ofertas, compatibilidad), sonda de efecto real por bendiciones y sinergias, límites/estrés y partidas de bot con builds.",
                ""));
        o.append("## Sinergias\n\n| # | Sinergia | Requiere | Efecto | Bendiciones |\n|---|---|---|---|---|\n");
        for (BSyn s : S) {
            StringBuilder m = new StringBuilder();
            for (int id : s.members) { if (m.length() > 0) m.append(", "); m.append(A[id].name); }
            o.append("| ").append(s.id + 1).append(" | **").append(e(s.name)).append("** | ").append(s.need).append(" de ").append(s.members.length).append(" | ").append(e(s.desc)).append(" | ").append(e(m.toString())).append(" |\n");
        }
        o.append("\n");
        for (int c = 0; c < 10; c++) {
            o.append("## ").append(CAT[c]).append("\n\n| id | Bendición | Rareza | Máx. | Efecto | Sinergias |\n|---|---|---|---|---|---|\n");
            for (Blessing b : A) if (b.cat - 'A' == c) {
                StringBuilder sn = new StringBuilder();
                for (int si : mo[b.id]) { if (sn.length() > 0) sn.append(", "); sn.append(S[si].name); }
                o.append("| ").append(b.id).append(" | ").append(e(b.name)).append(" | ").append(RAR[b.rar]).append(" | ").append(b.max).append(" | ").append(e(b.desc));
                if (b.req != null && !b.req.isEmpty()) o.append(" *(").append(BlessOffer.reqText(b)).append(b.minStage > 0 ? ", piso ≥ " + (b.minStage + 1) : "").append(")*");
                o.append(" | ").append(e(sn.toString())).append(" |\n");
            }
            o.append("\n");
        }
        Files.write(Paths.get("docs/BENDICIONES.md"), o.toString().getBytes("UTF-8"));
        System.out.println("docs/BENDICIONES.md " + o.length() + " bytes");
    }
}
