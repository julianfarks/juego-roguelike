import com.julianfarks.roguelike.core.*;
import desktop.DesktopPlatform;
import pc.PcPlatform;
import pc.ViewLayout;
import java.io.File;

/** Pruebas de la adaptacion a PC: plataforma, controles tactiles, ajustes de video (guardado/recuperacion/aislamiento) y calidad. */
public class PcTest {
    static int fails;
    static void chk(String n, boolean ok) { System.out.println((ok ? "ok   " : "FAIL ") + n); if (!ok) fails++; }

    public static void main(String[] a) throws Exception {
        File assets = new File("Shared/assets");
        File st = File.createTempFile("pcstore", ".properties"); st.delete();
        PcPlatform pc = PcPlatform.headless(assets, st);
        DesktopPlatform and = new DesktopPlatform(assets, null);   // plataforma "tipo movil" (sin PC)

        chk("PC: isDesktop y video() presentes", pc.isDesktop() && pc.video() != null);
        chk("Android/banco: no es PC y no tiene video()", !and.isDesktop() && and.video() == null);

        Game gPc = new Game(); gPc.init(pc); gPc.resize(480);
        Game gAnd = new Game(); gAnd.init(and); gAnd.resize(480);
        chk("controles tactiles OCULTOS en PC", !gPc.touchUiVisible());
        chk("controles tactiles VISIBLES fuera de PC (Android)", gAnd.touchUiVisible());

        // ajustes de video: valores por defecto, guardado, recuperacion
        VideoCfg d = VideoCfg.defaults();
        chk("por defecto: calidad Alta, 60 FPS, ventana", d.quality == VideoCfg.Q_HIGH && d.fps == 60 && d.mode == VideoCfg.MODE_WINDOW);
        VideoCfg c = d.copy();
        c.mode = VideoCfg.MODE_FULL; c.resW = 1920; c.resH = 1080; c.fps = 30; c.vsync = false; c.showFps = true; c.scaleMode = 1; c.applyPreset(VideoCfg.Q_LOW);
        VideoCfg.save(pc, c);
        PcPlatform pc2 = PcPlatform.headless(assets, st);          // "cierra y vuelve a abrir"
        VideoCfg r = VideoCfg.cur;
        chk("se recupera tras reiniciar (modo, resolucion, FPS, vsync, FPS visibles, escalado, calidad)", r.same(c));
        chk("Baja: particulas 25%, sin brillos, sin vineta", r.particles == 25 && !r.light && !r.vig && VideoCfg.particleMul == 0.25f && !VideoCfg.lights && !VideoCfg.vignette);
        chk("los ajustes viven en el Store de PC (clave pc_video), no en la partida", pc2.store().get("pc_video", "").contains("mode=1") && !pc2.store().get("save", "").contains("pc_video"));

        // preajustes y personalizada
        VideoCfg p = new VideoCfg(); p.applyPreset(VideoCfg.Q_MED); p.light = false; p.syncPreset();
        chk("tocar un ajuste fino pasa a Personalizada", p.quality == VideoCfg.Q_CUSTOM);
        p.light = true; p.syncPreset();
        chk("volver a los valores de Media la restituye", p.quality == VideoCfg.Q_MED);
        chk("datos corruptos no rompen (valores por defecto)", VideoCfg.parse("mode=x;;w=;fps=999;q=77").fps == 60);

        // el motor respeta la calidad
        VideoCfg q = new VideoCfg(); q.applyPreset(VideoCfg.Q_LOW); q.pushEffects();
        Particles ps = new Particles();
        for (int i = 0; i < 400; i++) ps.spawn(0, 0, 0, 0, 5f, 1, 0, 0xFFFFFF, false);
        chk("particulas al 25%: ~100 de 400 (" + ps.count() + ")", ps.count() >= 90 && ps.count() <= 110);
        new VideoCfg().pushEffects();
        Particles ps2 = new Particles();
        for (int i = 0; i < 400; i++) ps2.spawn(0, 0, 0, 0, 5f, 1, 0, 0xFFFFFF, false);
        chk("calidad Alta: todas las particulas (400)", ps2.count() == 400);

        // pantalla completa / escalado: sin franjas negras causadas por el escalado (antes: 45 px arriba y abajo en 1440p, 114 px en 1366x768)
        int[][] mons = {{1920,1080},{2560,1440},{3840,2160},{1600,900},{1366,768},{1280,720},{1920,1200},{2560,1600},{1680,1050},{1440,900},{3440,1440},{2560,1080},{1280,1024},{1024,768}};
        for (int[] m : mons) {
            ViewLayout fl = ViewLayout.compute(m[0], m[1], ViewLayout.FILL);
            int barV = m[1] - fl.dstH, barH = m[0] - fl.dstW;
            boolean inside = fl.dstX >= 0 && fl.dstY >= 0 && fl.dstX + fl.dstW <= m[0] && fl.dstY + fl.dstH <= m[1];
            boolean sizeOk = fl.vw >= 480 && fl.vw <= 640 && fl.vh >= 270 && fl.vh <= 320;
            double ar = m[0] / (double) m[1];
            boolean noBars = ar >= 1.5 && ar <= 640 / 270.0 + 0.001 ? (barV <= 1 && barH <= (int) Math.ceil(fl.scale)) : true;
            chk("llenar " + m[0] + "x" + m[1] + ": " + fl + " franjas " + barH + "x" + barV, inside && sizeOk && noBars);
        }
        ViewLayout i1440 = ViewLayout.compute(2560, 1440, ViewLayout.FILL), o1440 = ViewLayout.compute(2560, 1440, ViewLayout.INTEGER);
        chk("1440p: llena con escala ENTERA 5 (pixeles todos iguales) y alto virtual 288; el modo entero antiguo dejaba 45+45 px", i1440.scale == 5f && i1440.vh == 288 && i1440.dstH == 1440 && o1440.dstH == 1350);
        ViewLayout l720 = ViewLayout.compute(1280, 720, ViewLayout.FILL);
        chk("720p: escala fraccional sin suavizado que llena el lienzo (270 de alto)", l720.dstH == 720 && l720.dstW == 1280 && l720.vh == 270);
        ViewLayout t43 = ViewLayout.compute(1280, 1024, ViewLayout.FILL);
        chk("4:3 / 5:4: limite honesto (alto virtual 320 = sala mas baja), franjas arriba/abajo inevitables", t43.vh == 320 && t43.dstW == 1280 && t43.dstH < 1024);
        Game gTall = new Game(); gTall.init(pc); gTall.resize(480, 300);
        chk("Game.resize(ancho, alto) fija el alto virtual y se limita a 270..320", ViewSize.h == 300);
        gTall.resize(480, 999); chk("alto virtual limitado a 320", ViewSize.h == 320);
        gTall.resize(480, 270); chk("alto virtual vuelve a 270 (Android y 16:9 clasico no cambian)", ViewSize.h == 270);

        // resoluciones ofrecidas
        int[][] rs = pc.video().resolutions();
        boolean has720 = false, sorted = true;
        for (int i = 0; i < rs.length; i++) { if (rs[i][0] == 1280 && rs[i][1] == 720) has720 = true; if (i > 0 && rs[i][0] < rs[i - 1][0]) sorted = false; }
        chk("lista de resoluciones con 1280x720 y ordenada (" + rs.length + " opciones)", has720 && sorted);
        chk("ventana predeterminada = multiplo exacto de 480x270", pc.video().defaultRes()[0] % 480 == 0 && pc.video().defaultRes()[1] * 16 == pc.video().defaultRes()[0] * 9);

        st.delete();
        System.out.println(fails == 0 ? "PcTest OK" : "PcTest FALLOS: " + fails);
        System.exit(fails == 0 ? 0 : 1);
    }
}
