package pc;

import com.julianfarks.roguelike.core.Pad;

import java.lang.foreign.Arena;
import java.lang.foreign.FunctionDescriptor;
import java.lang.foreign.Linker;
import java.lang.foreign.MemorySegment;
import java.lang.foreign.SymbolLookup;
import java.lang.foreign.ValueLayout;
import java.lang.invoke.MethodHandle;

/**
 * Mando en Windows mediante XInput (xinput1_4.dll) llamado con la API de funciones externas de Java (JDK 22+): sin librerias nativas
 * extra. Cubre mandos Xbox y compatibles con XInput (tambien los de PlayStation/Switch cuando se usan con Steam Input o DS4Windows).
 * Traduce a los codigos virtuales {@link Pad} igual que en Android, asi el motor no distingue de que mando viene cada boton.
 */
final class PcXInput {
    private static final int ERROR_SUCCESS = 0;
    private static final int[][] BTN = {   // mascara XInput -> codigo virtual
            {0x1000, Pad.A}, {0x2000, Pad.B}, {0x4000, Pad.X}, {0x8000, Pad.Y}, {0x0100, Pad.LB}, {0x0200, Pad.RB},
            {0x0010, Pad.MENU}, {0x0020, Pad.VIEW}, {0x0040, Pad.L3}, {0x0080, Pad.R3},
            {0x0001, Pad.DUP}, {0x0002, Pad.DDOWN}, {0x0004, Pad.DLEFT}, {0x0008, Pad.DRIGHT}};

    interface Sink extends Pad.Sink { }

    private final MethodHandle getState;
    private final Arena arena = Arena.ofShared();
    private final MemorySegment state;
    private final Pad.Axes axes = new Pad.Axes();
    private final boolean[] btnDown = new boolean[BTN.length];
    private boolean connected;
    private int slot = -1;
    private int retryTicks;

    /** Devuelve null si no hay XInput (no es Windows, o la DLL no carga). */
    static PcXInput tryCreate() {
        try {
            if (!System.getProperty("os.name", "").toLowerCase().contains("win")) return null;
            return new PcXInput();
        } catch (Throwable t) {
            PcLog.err("XInput no disponible (sin mando)", t);
            return null;
        }
    }

    private PcXInput() throws Throwable {
        Linker linker = Linker.nativeLinker();
        SymbolLookup lib;
        try { lib = SymbolLookup.libraryLookup("xinput1_4.dll", arena); }
        catch (Throwable t) { lib = SymbolLookup.libraryLookup("xinput9_1_0.dll", arena); }
        MemorySegment fn = lib.find("XInputGetState").orElseThrow();
        getState = linker.downcallHandle(fn, FunctionDescriptor.of(ValueLayout.JAVA_INT, ValueLayout.JAVA_INT, ValueLayout.ADDRESS));
        state = arena.allocate(16);        // XINPUT_STATE: DWORD paquete + XINPUT_GAMEPAD (WORD botones, 2 BYTE gatillos, 4 SHORT sticks)
    }

    /** Consulta el mando y entrega los cambios al motor. Se llama una vez por fotograma desde el hilo del juego. */
    void poll(Pad.Sink sink) {
        try {
            if (slot < 0) {
                if (retryTicks-- > 0) return;      // sin mando: busca cada ~1 s (XInputGetState es lento si no hay mando)
                retryTicks = 60;
                for (int i = 0; i < 4; i++) {
                    if ((int) getState.invokeExact(i, state) == ERROR_SUCCESS) { slot = i; break; }
                }
                if (slot < 0) return;
            }
            int r = (int) getState.invokeExact(slot, state);
            if (r != ERROR_SUCCESS) {              // desconectado
                slot = -1; retryTicks = 0;
                if (connected) { connected = false; axes.releaseAll(sink); for (int i = 0; i < btnDown.length; i++) if (btnDown[i]) { btnDown[i] = false; sink.key(BTN[i][1], false); } sink.key(Pad.EV_CONNECTED, false); }
                return;
            }
            if (!connected) { connected = true; sink.key(Pad.EV_TYPE_BASE + Pad.TYPE_XBOX, true); sink.key(Pad.EV_CONNECTED, true); }
            int buttons = state.get(ValueLayout.JAVA_SHORT, 4) & 0xFFFF;
            int lt = state.get(ValueLayout.JAVA_BYTE, 6) & 0xFF, rt = state.get(ValueLayout.JAVA_BYTE, 7) & 0xFF;
            float lx = state.get(ValueLayout.JAVA_SHORT, 8) / 32768f, ly = state.get(ValueLayout.JAVA_SHORT, 10) / 32768f;
            float rx = state.get(ValueLayout.JAVA_SHORT, 12) / 32768f, ry = state.get(ValueLayout.JAVA_SHORT, 14) / 32768f;
            for (int i = 0; i < BTN.length; i++) {
                boolean on = (buttons & BTN[i][0]) != 0;
                if (on != btnDown[i]) { btnDown[i] = on; sink.key(BTN[i][1], on); }
            }
            // XInput: Y positivo = arriba; el motor usa la convencion de Android (arriba = negativo)
            axes.update(lx, -ly, rx, -ry, lt / 255f, rt / 255f, 0f, 0f, sink);
        } catch (Throwable t) {
            PcLog.err("XInput.poll", t);
            slot = -1; retryTicks = 600;
        }
    }
}
