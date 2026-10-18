package pc;

import com.julianfarks.roguelike.core.ViewSize;

/**
 * Calcula como se coloca la pantalla virtual del juego dentro del lienzo de la ventana (funcion pura, comprobada en PcTest).
 *
 * Modo {@link #FILL} (por defecto): no deja franjas negras salvo que sea fisicamente imposible sin deformar.
 *   1) Escala ENTERA k (pixeles todos iguales, nitidez perfecta) con la pantalla virtual ampliada en alto a ch/k (270..320 px):
 *      asi un 1440p (k=5 -> 512x288), un 1200p o un 900p se llenan exactamente. Es lo que antes faltaba: con el alto fijo de 270 el
 *      mayor multiplo entero que cabia dejaba franjas arriba y abajo (45 px en 1440p, 114 px en 1366x768).
 *   2) Si ningun multiplo entero cabe sin pasarse de 320 px de alto (p. ej. 1280x720 o 1366x768), escala fraccional (vecino mas
 *      cercano, sin suavizado) que ocupa todo el lienzo; el ancho virtual se adapta (480..640) y el alto vale 270..320.
 *   Limites: a mas de 640 px virtuales de ancho (ultra-panoramico) quedan franjas laterales, y por debajo de 3:2 de relacion de
 *   aspecto (4:3, 5:4) quedan franjas arriba/abajo, porque las salas mas bajas miden 320 px y no hay mas escenario que mostrar.
 * Modo {@link #INTEGER}: solo multiplos enteros con el alto 270 de siempre (con franjas si no encaja justo).
 */
public final class ViewLayout {
    public static final int FILL = 0, INTEGER = 1;

    public final int vw, vh;          // pantalla virtual
    public final float scale;         // pixeles reales por pixel virtual (horizontal; el vertical difiere < 0,4 % en el caso fraccional)
    public final int dstX, dstY, dstW, dstH;

    private ViewLayout(int vw, int vh, float scale, int cw, int ch, int dw, int dh) {
        this.vw = vw; this.vh = vh; this.scale = scale; dstW = dw; dstH = dh;
        dstX = (cw - dw) / 2; dstY = (ch - dh) / 2;
    }

    public static ViewLayout compute(int cw, int ch, int mode) {
        final int H0 = ViewSize.BASE, HMAX = ViewSize.MAX;
        if (mode == INTEGER) {
            int k = Math.max(1, (int) Math.floor(Math.min(cw / 480f, ch / (float) H0)));
            int vw = Math.max(480, Math.min(640, cw / k));
            return new ViewLayout(vw, H0, k, cw, ch, vw * k, H0 * k);
        }
        // 1) escala entera con alto virtual ampliado
        for (int k = Math.max(1, ch / H0); k >= 1; k--) {
            int vh = ch / k;
            if (vh > HMAX) break;
            if (vh < H0) continue;
            int vw = Math.min(640, cw / k);
            if (vw < 480) continue;
            return new ViewLayout(vw, vh, k, cw, ch, vw * k, vh * k);
        }
        // 2) fraccional que llena el lienzo
        if (cw * H0 >= ch * 480) {                       // 16:9 o mas ancho: alto 270 y ancho adaptado
            float s = ch / (float) H0;
            int vw = Math.max(480, Math.min(640, (int) Math.floor(cw / s)));
            int dw = vw * s > cw ? cw : Math.round(vw * s);
            return new ViewLayout(vw, H0, s, cw, ch, dw, ch);
        }
        float s = cw / 480f;                              // mas alto que 16:9: ancho 480 y alto ampliado
        int vh = Math.max(H0, Math.min(HMAX, (int) Math.floor(ch / s)));
        int dh = Math.min(ch, Math.round(vh * s));
        if (ch - dh < s) dh = ch;                         // resto < 1 pixel virtual: se absorbe (deformacion < 0,4 %)
        return new ViewLayout(480, vh, s, cw, ch, cw, dh);
    }

    @Override public String toString() {
        return "virtual " + vw + "x" + vh + " escala " + scale + " destino " + dstW + "x" + dstH + " en (" + dstX + "," + dstY + ")";
    }
}
