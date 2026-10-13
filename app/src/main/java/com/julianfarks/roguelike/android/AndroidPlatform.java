package com.julianfarks.roguelike.android;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.content.res.AssetManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Build;
import android.os.SystemClock;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.os.VibratorManager;
import android.util.Log;

import com.julianfarks.roguelike.core.Platform;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;

/** Implementacion Android de {@link Platform}. */
public final class AndroidPlatform implements Platform {
    private static final String TAG = "SWR";

    private final Activity activity;
    private final AssetManager assets;
    private final AndroidGfx gfx = new AndroidGfx();
    private final AndroidAudio audio;
    private final PrefStore store;
    private Vibrator vibrator; // puede ser null

    public AndroidPlatform(Activity activity) {
        this.activity = activity;
        this.assets = activity.getAssets();
        this.audio = new AndroidAudio(activity);
        this.store = new PrefStore(activity.getSharedPreferences("save", Context.MODE_PRIVATE));
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                VibratorManager vm = (VibratorManager) activity.getSystemService(Context.VIBRATOR_MANAGER_SERVICE);
                if (vm != null) vibrator = vm.getDefaultVibrator();
            } else {
                vibrator = (Vibrator) activity.getSystemService(Context.VIBRATOR_SERVICE);
            }
        } catch (Throwable t) {
            vibrator = null;
        }
    }

    public AndroidGfx androidGfx() { return gfx; }
    public AndroidAudio androidAudio() { return audio; }

    /** Llamar desde onPause para asegurar que el guardado llegue a disco. */
    public void flush() { store.commit(); }

    // ---------------------------------------------------------------- recursos

    @Override
    public Img loadImage(String path) {
        if (path == null) return null;
        InputStream in = null;
        try {
            in = assets.open(path);
            BitmapFactory.Options o = new BitmapFactory.Options();
            o.inScaled = false;
            o.inPreferredConfig = Bitmap.Config.ARGB_8888;
            o.inPremultiplied = true;
            Bitmap b = BitmapFactory.decodeStream(in, null, o);
            if (b == null) return null;
            b.setDensity(Bitmap.DENSITY_NONE);
            return new Img(b.getWidth(), b.getHeight(), b);
        } catch (IOException e) {
            return null;
        } catch (Throwable t) {
            Log.w(TAG, "loadImage fallo: " + path, t);
            return null;
        } finally {
            closeQuietly(in);
        }
    }

    @Override
    public Img createImage(int w, int h, int[] argbPixels) {
        Bitmap b = Bitmap.createBitmap(argbPixels, w, h, Bitmap.Config.ARGB_8888);
        b.setDensity(Bitmap.DENSITY_NONE);
        return new Img(w, h, b);
    }

    @Override
    public int[] pixels(Img img) {
        int[] out = new int[img.w * img.h];
        Bitmap b = (Bitmap) img.handle;
        b.getPixels(out, 0, img.w, 0, 0, img.w, img.h);
        return out;
    }

    @Override
    public String loadText(String path) {
        if (path == null) return null;
        InputStream in = null;
        try {
            in = assets.open(path);
            ByteArrayOutputStream bos = new ByteArrayOutputStream(Math.max(1024, in.available()));
            byte[] buf = new byte[8192];
            int n;
            while ((n = in.read(buf)) > 0) bos.write(buf, 0, n);
            String s = new String(bos.toByteArray(), StandardCharsets.UTF_8);
            if (s.length() > 0 && s.charAt(0) == '﻿') s = s.substring(1);
            return s;
        } catch (IOException e) {
            return null;
        } finally {
            closeQuietly(in);
        }
    }

    @Override
    public String[] list(String dir) {
        try {
            String d = dir == null ? "" : dir;
            while (d.endsWith("/")) d = d.substring(0, d.length() - 1);
            String[] r = assets.list(d);
            return r == null ? new String[0] : r;
        } catch (IOException e) {
            return new String[0];
        }
    }

    private static void closeQuietly(InputStream in) {
        if (in != null) {
            try { in.close(); } catch (IOException ignored) { }
        }
    }

    // ---------------------------------------------------------------- servicios

    @Override public Gfx gfx() { return gfx; }
    @Override public Audio audio() { return audio; }
    @Override public Store store() { return store; }

    @Override
    public void log(String msg) {
        Log.d(TAG, msg == null ? "null" : msg);
    }

    @Override
    public long nowMs() {
        return SystemClock.uptimeMillis();
    }

    @Override
    public void vibrate(int ms) {
        Vibrator v = vibrator;
        if (v == null) return;
        try {
            if (activity.checkSelfPermission(Manifest.permission.VIBRATE) != PackageManager.PERMISSION_GRANTED) return;
            if (!v.hasVibrator()) return;
            long d = ms < 1 ? 1 : (ms > 500 ? 500 : ms);
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                v.vibrate(VibrationEffect.createOneShot(d, VibrationEffect.DEFAULT_AMPLITUDE));
            } else {
                v.vibrate(d);
            }
        } catch (Throwable ignored) {
            // la vibracion nunca debe tumbar el juego
        }
    }

    @Override
    public void quit() {
        activity.runOnUiThread(new Runnable() {
            @Override public void run() { activity.finish(); }
        });
    }

    // ---------------------------------------------------------------- Store

    /** SharedPreferences "save" con lectura de lo escrito antes del commit. */
    private static final class PrefStore implements Store {
        private final SharedPreferences prefs;
        private final HashMap<String, String> pending = new HashMap<String, String>();

        PrefStore(SharedPreferences prefs) { this.prefs = prefs; }

        @Override
        public synchronized String get(String key, String def) {
            String v = pending.get(key);
            if (v != null) return v;
            try {
                return prefs.getString(key, def);
            } catch (ClassCastException e) {
                return def;
            }
        }

        @Override
        public synchronized void put(String key, String value) {
            if (key == null || value == null) return;
            pending.put(key, value);
        }

        @Override
        public synchronized void commit() {
            if (pending.isEmpty()) return;
            SharedPreferences.Editor ed = prefs.edit();
            for (java.util.Map.Entry<String, String> e : pending.entrySet()) {
                ed.putString(e.getKey(), e.getValue());
            }
            ed.apply();
            pending.clear();
        }
    }
}
