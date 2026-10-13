package com.julianfarks.roguelike.android;

import android.content.Context;
import android.os.Build;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.nio.charset.StandardCharsets;

/** Guarda / lee / borra crash.txt en getFilesDir() para depurar sin herramientas. */
public final class CrashLog {
    private static final int MAX_BYTES = 24 * 1024;

    private CrashLog() { }

    private static File file(Context c) {
        return new File(c.getFilesDir(), "crash.txt");
    }

    /** Primera linea = meta (fase, frame, dispositivo); luego el stack trace completo. */
    public static String format(String phase, long frame, Throwable t) {
        StringWriter sw = new StringWriter();
        PrintWriter pw = new PrintWriter(sw);
        pw.println("[" + phase + " frame=" + frame + " " + Build.MANUFACTURER + " " + Build.MODEL
                + " API" + Build.VERSION.SDK_INT + "]");
        try {
            t.printStackTrace(pw);
        } catch (Throwable ignored) {
            pw.println(String.valueOf(t));
        }
        pw.flush();
        String s = sw.toString();
        return s.length() > MAX_BYTES ? s.substring(0, MAX_BYTES) : s;
    }

    public static void write(Context c, String text) {
        FileOutputStream out = null;
        try {
            out = new FileOutputStream(file(c), false);
            out.write(text.getBytes(StandardCharsets.UTF_8));
            out.flush();
        } catch (Throwable ignored) {
            // nada mas que hacer
        } finally {
            if (out != null) {
                try { out.close(); } catch (IOException ignored) { }
            }
        }
    }

    /** Devuelve el contenido de crash.txt o null si no existe / esta vacio. */
    public static String read(Context c) {
        File f = file(c);
        if (!f.isFile() || f.length() == 0) return null;
        FileInputStream in = null;
        try {
            in = new FileInputStream(f);
            byte[] buf = new byte[(int) Math.min(f.length(), MAX_BYTES)];
            int off = 0;
            while (off < buf.length) {
                int n = in.read(buf, off, buf.length - off);
                if (n <= 0) break;
                off += n;
            }
            return new String(buf, 0, off, StandardCharsets.UTF_8);
        } catch (Throwable t) {
            return null;
        } finally {
            if (in != null) {
                try { in.close(); } catch (IOException ignored) { }
            }
        }
    }

    public static void delete(Context c) {
        try { //noinspection ResultOfMethodCallIgnored
            file(c).delete();
        } catch (Throwable ignored) { }
    }
}
