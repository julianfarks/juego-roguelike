package pc;

import java.io.File;
import java.io.FileOutputStream;
import java.io.PrintStream;

/** Registro del juego de PC. Con el .exe (sin consola) la salida estandar se redirige a un archivo de la carpeta de datos del usuario. */
final class PcLog {
    private PcLog() {}

    private static PrintStream out = System.out;

    /** Redirige System.out/System.err a dir/log.txt (se reinicia en cada arranque). */
    static void toFile(File dir) {
        try {
            dir.mkdirs();
            PrintStream ps = new PrintStream(new FileOutputStream(new File(dir, "log.txt"), false), true, "UTF-8");
            out = ps;
            System.setOut(ps);
            System.setErr(ps);
        } catch (Throwable ignored) { }
    }

    static void info(String s) { out.println("[pc] " + s); }

    static void err(String s, Throwable t) {
        out.println("[pc] ERROR: " + s + (t == null ? "" : " -> " + t));
        if (t != null) t.printStackTrace(out);
    }
}
