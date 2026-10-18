package com.julianfarks.roguelike.core;

/**
 * Mandos: codigos virtuales unificados. La capa de la plataforma (Android) traduce cualquier mando
 * (Xbox, DualShock/DualSense, genericos) a estos codigos y los entrega por Game.key(); asi el resto del juego
 * no sabe de que mando viene cada pulsacion. Los codigos &lt; 1000 son teclas de teclado.
 */
public final class Pad {
    private Pad() {}

    public static final int A = 1000, B = 1001, X = 1002, Y = 1003, LB = 1004, RB = 1005, LT = 1006, RT = 1007, VIEW = 1008, MENU = 1009, L3 = 1010, R3 = 1011,
            DUP = 1012, DDOWN = 1013, DLEFT = 1014, DRIGHT = 1015,
            LS_L = 1020, LS_R = 1021, LS_U = 1022, LS_D = 1023, RS_L = 1024, RS_R = 1025, RS_U = 1026, RS_D = 1027, END = 1028;
    /** Eventos de estado enviados por la plataforma (no son botones). */
    public static final int EV_CONNECTED = 2000, EV_TYPE_BASE = 2001;   // EV_TYPE_BASE + tipo (down = true)
    public static final int TYPE_GENERIC = 0, TYPE_XBOX = 1, TYPE_PS = 2;

    public static boolean isPad(int code) { return code >= A && code < END; }

    // ---------------------------------------------------------------- traduccion desde Android (valores de KeyEvent)
    public static int fromAndroidKey(int k) {
        switch (k) {
            case 96: return A;        // BUTTON_A  (Xbox A / PS Cruz)
            case 97: return B;        // BUTTON_B  (Xbox B / PS Circulo)
            case 99: return X;        // BUTTON_X  (Xbox X / PS Cuadrado)
            case 100: return Y;       // BUTTON_Y  (Xbox Y / PS Triangulo)
            case 102: return LB;      // BUTTON_L1
            case 103: return RB;      // BUTTON_R1
            case 104: return LT;      // BUTTON_L2
            case 105: return RT;      // BUTTON_R2
            case 109: return VIEW;    // BUTTON_SELECT
            case 108: return MENU;    // BUTTON_START
            case 106: return L3;      // BUTTON_THUMBL
            case 107: return R3;      // BUTTON_THUMBR
            case 19: return DUP;      // DPAD_UP (solo cuando el origen es un mando)
            case 20: return DDOWN;
            case 21: return DLEFT;
            case 22: return DRIGHT;
            default: return -1;
        }
    }

    /** Tecla de teclado de Android -> codigo estilo escritorio (letras, numeros, flechas, espacio...). -1 si no se usa. */
    public static int fromAndroidKeyboard(int k) {
        if (k >= 29 && k <= 54) return 'A' + (k - 29);          // KEYCODE_A..Z
        if (k >= 7 && k <= 16) return '0' + (k - 7);            // KEYCODE_0..9
        switch (k) {
            case 19: return 38; case 20: return 40; case 21: return 37; case 22: return 39;
            case 62: return 32;      // espacio
            case 66: case 160: return 10;   // enter
            case 59: case 60: return 16;    // shift
            case 113: case 114: return 17;  // ctrl
            case 57: case 58: return 18;    // alt
            case 61: return 9;       // tab
            case 111: return 27;     // escape
            case 67: return 8;       // retroceso
            default: return -1;
        }
    }

    /** Tipo de mando por fabricante / nombre. */
    public static int typeOf(int vendorId, String name) {
        String n = name == null ? "" : name.toLowerCase();
        if (vendorId == 0x054C || n.contains("dualshock") || n.contains("dualsense") || n.contains("playstation") || n.contains("wireless controller") && vendorId != 0x045E) return TYPE_PS;
        if (vendorId == 0x045E || n.contains("xbox") || n.contains("x-box")) return TYPE_XBOX;
        return TYPE_GENERIC;
    }

    // ---------------------------------------------------------------- nombres
    public static String name(int type, int code) {
        boolean ps = type == TYPE_PS;
        switch (code) {
            case A: return ps ? "Cruz" : "A";
            case B: return ps ? "Círculo" : "B";
            case X: return ps ? "Cuadro" : "X";
            case Y: return ps ? "Triáng." : "Y";
            case LB: return ps ? "L1" : "LB";
            case RB: return ps ? "R1" : "RB";
            case LT: return ps ? "L2" : "LT";
            case RT: return ps ? "R2" : "RT";
            case VIEW: return ps ? "Share" : "View";
            case MENU: return ps ? "Options" : "Menú";
            case L3: return ps ? "L3" : "LS clic";
            case R3: return ps ? "R3" : "RS clic";
            case DUP: return "Cruc. arr.";
            case DDOWN: return "Cruc. abj.";
            case DLEFT: return "Cruc. izq.";
            case DRIGHT: return "Cruc. der.";
            case LS_L: return "LS izq.";
            case LS_R: return "LS der.";
            case LS_U: return "LS arr.";
            case LS_D: return "LS abj.";
            case RS_L: return "RS izq.";
            case RS_R: return "RS der.";
            case RS_U: return "RS arr.";
            case RS_D: return "RS abj.";
            default: return "?";
        }
    }

    /** Color del boton de cara (Xbox: A verde, B rojo, X azul, Y amarillo; PlayStation: cruz azul, circulo rojo, cuadro rosa, triangulo verde). 0 = sin color. */
    public static int faceColor(int type, int code) {
        if (type == TYPE_PS) {
            switch (code) { case A: return 0x5A8AFF; case B: return 0xFF5A5A; case X: return 0xE080C0; case Y: return 0x5AD070; default: return 0; }
        }
        switch (code) { case A: return 0x5AD070; case B: return 0xFF5A5A; case X: return 0x5A8AFF; case Y: return 0xFFD25A; default: return 0; }
    }

    public static String keyName(int code) {
        if (code <= 0) return "-";
        if (code >= 'A' && code <= 'Z') return String.valueOf((char) code);
        if (code >= '0' && code <= '9') return String.valueOf((char) code);
        switch (code) {
            case 37: return "Izq."; case 38: return "Arr."; case 39: return "Der."; case 40: return "Abj.";
            case 32: return "Espacio"; case 10: return "Enter"; case 16: return "Shift"; case 17: return "Ctrl"; case 18: return "Alt";
            case 9: return "Tab"; case 27: return "Esc"; case 8: return "Retroc.";
            default: return "Tecla " + code;
        }
    }

    public static String typeName(int type) { return type == TYPE_PS ? "PlayStation" : (type == TYPE_XBOX ? "Xbox" : "Mando genérico"); }

    /** Traduccion de un boton de mando a la tecla de menu equivalente (navegar, aceptar, volver). -1 si no navega. */
    public static int menuKey(int code) {
        switch (code) {
            case A: return 10;
            case B: case MENU: return 27;
            case DUP: case LS_U: return 38;
            case DDOWN: case LS_D: return 40;
            case DLEFT: case LS_L: return 37;
            case DRIGHT: case LS_R: return 39;
            default: return -1;
        }
    }

    // ---------------------------------------------------------------- ejes -> botones virtuales
    public interface Sink { void key(int code, boolean down); }

    /** Convierte los ejes analogicos (sticks, gatillos, cruceta) en botones virtuales con histeresis. */
    public static final class Axes {
        private static final float ON = 0.55f, OFF = 0.35f, TON = 0.5f, TOFF = 0.3f;
        private final boolean[] st = new boolean[END - A];

        private void set(Sink s, int code, boolean on) {
            if (st[code - A] != on) { st[code - A] = on; s.key(code, on); }
        }
        private void stick(Sink s, float v, int neg, int pos) {
            boolean n = st[neg - A], p = st[pos - A];
            set(s, neg, v < (n ? -OFF : -ON));
            set(s, pos, v > (p ? OFF : ON));
        }

        public void update(float lx, float ly, float rx, float ry, float lt, float rt, float hx, float hy, Sink s) {
            stick(s, lx, LS_L, LS_R);
            stick(s, ly, LS_U, LS_D);
            stick(s, rx, RS_L, RS_R);
            stick(s, ry, RS_U, RS_D);
            set(s, LT, lt > (st[LT - A] ? TOFF : TON));
            set(s, RT, rt > (st[RT - A] ? TOFF : TON));
            set(s, DLEFT, hx < -0.5f); set(s, DRIGHT, hx > 0.5f);
            set(s, DUP, hy < -0.5f); set(s, DDOWN, hy > 0.5f);
        }

        /** Suelta todo (desconexion del mando). */
        public void releaseAll(Sink s) { for (int c = A; c < END; c++) if (st[c - A]) { st[c - A] = false; s.key(c, false); } }
    }
}
