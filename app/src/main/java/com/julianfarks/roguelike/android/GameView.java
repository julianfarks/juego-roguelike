package com.julianfarks.roguelike.android;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Rect;
import android.graphics.RectF;
import android.graphics.Typeface;
import android.os.Build;
import android.os.Handler;
import android.os.HandlerThread;
import android.util.Log;
import android.hardware.input.InputManager;
import android.view.Choreographer;
import android.view.InputDevice;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.Surface;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.WindowManager;

import com.julianfarks.roguelike.core.Game;
import com.julianfarks.roguelike.core.Pad;
import com.julianfarks.roguelike.core.Platform;

import java.util.ArrayList;

/**
 * SurfaceView que ejecuta el juego en un hilo propio sincronizado con Choreographer (vsync).
 *
 * Pantalla virtual: alto 270, ancho viewW = clamp(round(270*sw/sh), 480, 640). Cada frame se dibuja en un Bitmap
 * offscreen viewW x 270 y se escala (vecino mas cercano) a la superficie: escala entera si pierde &lt;= 8% del espacio,
 * si no fraccional; centrado; franjas negras si hace falta.
 *
 * Conversion de toque: virtual = (pixelPantalla - off) / escala.
 */
public final class GameView extends SurfaceView implements SurfaceHolder.Callback {
    private static final String TAG = "SWR";
    private static final long STEP_NS = 16666667L;      // 1/60 s
    private static final float DT = 1f / 60f;
    private static final long MAX_DELTA_NS = 250000000L; // tras una pausa no acumulamos mas de 250 ms
    private static final int MAX_STEPS = 5;
    private static final int MAX_POINTERS = 32;
    private static final int CRASH_LINES = 22;

    // ------------------------------------------------------------------ geometria
    private static final class Layout {
        final int sw, sh, viewW;
        final float scale, offX, offY;
        Layout(int sw, int sh) {
            this.sw = sw;
            this.sh = sh;
            int vw = Math.round(Platform.VIEW_H * (float) sw / (float) sh);
            this.viewW = vw < 480 ? 480 : (vw > 640 ? 640 : vw);
            float s = Math.min(sw / (float) viewW, sh / (float) Platform.VIEW_H);
            float k = (float) Math.floor(s);
            if (k >= 1f && k >= s * 0.92f) s = k;
            this.scale = s;
            this.offX = Math.round((sw - viewW * s) * 0.5f);
            this.offY = Math.round((sh - Platform.VIEW_H * s) * 0.5f);
        }
    }

    /** Evento de toque en coordenadas virtuales (pasa del hilo UI al hilo de juego). */
    private static final int ACT_KEY = 100;   // evento de tecla/boton: id = codigo, x = 1 pulsado / 0 suelto

    private static final class Ev {
        int id, action;
        float x, y;
    }

    private final Activity activity;
    private final AndroidPlatform platform;
    private final SurfaceHolder holder;
    private final long vsyncNs;

    // estado del hilo UI
    private volatile Layout layout;
    private boolean surfaceValid;
    private boolean resumed;
    private Runner runner;
    private Runner lastRunner;
    private boolean destroyed;

    // cola de toques
    private final Object touchLock = new Object();
    private ArrayList<Ev> pendingEv = new ArrayList<Ev>();
    private ArrayList<Ev> workEv = new ArrayList<Ev>();
    private final ArrayList<Ev> evPool = new ArrayList<Ev>();

    // estado del juego: solo lo toca el hilo de juego (o el UI tras join)
    private Game game;
    private boolean inited;
    private boolean pausedByUs;
    private boolean crashChecked;
    private volatile String errorText;
    private boolean errorDismissible;
    private String[] errLines;
    private int errLayoutW = -1;
    private long frameNo;
    private String phase = "";
    private Bitmap frameBmp;
    private Canvas frameCanvas;
    private int appliedViewW = -1;
    private boolean useHwCanvas = Build.VERSION.SDK_INT >= Build.VERSION_CODES.O;
    private boolean hwCanvasWorked;
    private final boolean[] ptrDown = new boolean[MAX_POINTERS];
    private final float[] ptrX = new float[MAX_POINTERS];
    private final float[] ptrY = new float[MAX_POINTERS];

    private final Paint blitPaint = new Paint();
    private final Rect blitSrc = new Rect();
    private final RectF blitDst = new RectF();
    private final Paint textPaint = new Paint();

    @SuppressWarnings("deprecation")
    public GameView(Activity activity, AndroidPlatform platform) {
        super(activity);
        this.activity = activity;
        this.platform = platform;
        holder = getHolder();
        holder.addCallback(this);
        setKeepScreenOn(true);
        setFocusable(true);
        setFocusableInTouchMode(true);

        blitPaint.setAntiAlias(false);
        blitPaint.setFilterBitmap(false);
        blitPaint.setDither(false);
        textPaint.setAntiAlias(true);
        textPaint.setTypeface(Typeface.MONOSPACE);

        float hz = 60f;
        try {
            WindowManager wm = (WindowManager) activity.getSystemService(Context.WINDOW_SERVICE);
            hz = wm.getDefaultDisplay().getRefreshRate();
        } catch (Throwable ignored) { }
        if (!(hz >= 24f && hz <= 240f)) hz = 60f;
        vsyncNs = (long) (1e9 / hz);
    }

    // ================================================================== ciclo de vida (hilo UI)

    public void onResume() {
        resumed = true;
        maybeStart();
    }

    public void onPause() {
        resumed = false;
        stopRunner();
    }

    /** Llamar desde Activity.onDestroy. */
    public void destroy() {
        destroyed = true;
        resumed = false;
        stopRunner();
        platform.androidAudio().release();
        if (frameBmp != null) {
            frameBmp.recycle();
            frameBmp = null;
        }
    }

    @Override
    public void surfaceCreated(SurfaceHolder h) {
        surfaceValid = true;
    }

    @Override
    public void surfaceChanged(SurfaceHolder h, int format, int w, int hgt) {
        if (w <= 0 || hgt <= 0) return;
        surfaceValid = true;
        layout = new Layout(w, hgt);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            try {
                h.getSurface().setFrameRate(60f, Surface.FRAME_RATE_COMPATIBILITY_DEFAULT);
            } catch (Throwable ignored) { }
        }
        maybeStart();
    }

    @Override
    public void surfaceDestroyed(SurfaceHolder h) {
        surfaceValid = false;
        stopRunner();
    }

    private void maybeStart() {
        if (destroyed || runner != null || !surfaceValid || !resumed || layout == null) return;
        Runner prev = lastRunner;
        if (prev != null && prev.thread.isAlive()) { // cierre anterior lento (p. ej. init largo): espera un poco mas
            try {
                prev.thread.join(3000);
            } catch (InterruptedException ie) {
                Thread.currentThread().interrupt();
            }
            if (prev.thread.isAlive()) return;
        }
        synchronized (touchLock) {
            pendingEv.clear();
        }
        runner = new Runner();
        runner.start();
    }

    private void stopRunner() {
        Runner r = runner;
        if (r == null) return;
        runner = null;
        lastRunner = r;
        r.stop();
        synchronized (touchLock) {
            pendingEv.clear();
        }
    }

    /** Boton Atras: lo resuelve el motor en el hilo de juego; si no lo consume, se cierra la app. */
    public void handleBack() {
        final Runner r = runner;
        if (r == null || r.handler == null || errorText != null) {
            activity.finish();
            return;
        }
        boolean posted = r.handler.post(new Runnable() {
            @Override public void run() {
                boolean consumed = false;
                try {
                    phase = "back";
                    if (inited && game != null && errorText == null) consumed = game.back();
                } catch (Throwable t) {
                    fail("back", t);
                    consumed = true;
                }
                if (!consumed && errorText == null) platform.quit();
            }
        });
        if (!posted) activity.finish();
    }

    // ================================================================== teclado y mandos (hilo UI)

    private final Pad.Axes padAxes = new Pad.Axes();
    private final Pad.Sink padSink = new Pad.Sink() {
        @Override public void key(int code, boolean down) { enqueueKey(code, down); }
    };
    private boolean padPresent;
    private int padTypeSent = -1;
    private InputManager.InputDeviceListener padListener;

    private void enqueueKey(int code, boolean down) {
        synchronized (touchLock) {
            Ev ev = evPool.isEmpty() ? new Ev() : evPool.remove(evPool.size() - 1);
            ev.id = code;
            ev.action = ACT_KEY;
            ev.x = down ? 1f : 0f;
            ev.y = 0f;
            pendingEv.add(ev);
        }
    }

    private static boolean isPadSource(int src) {
        return (src & InputDevice.SOURCE_GAMEPAD) == InputDevice.SOURCE_GAMEPAD || (src & InputDevice.SOURCE_JOYSTICK) == InputDevice.SOURCE_JOYSTICK;
    }

    /** Teclas del teclado y botones de mando (Xbox, PlayStation, genericos). Devuelve true si la tecla se uso. */
    public boolean handleKeyEvent(KeyEvent e) {
        int k = e.getKeyCode();
        if (k == KeyEvent.KEYCODE_BACK || k == KeyEvent.KEYCODE_VOLUME_UP || k == KeyEvent.KEYCODE_VOLUME_DOWN || k == KeyEvent.KEYCODE_VOLUME_MUTE) return false;
        boolean down = e.getAction() == KeyEvent.ACTION_DOWN;
        if (e.getAction() != KeyEvent.ACTION_DOWN && e.getAction() != KeyEvent.ACTION_UP) return false;
        int src = e.getSource();
        boolean dpadKey = k >= KeyEvent.KEYCODE_DPAD_UP && k <= KeyEvent.KEYCODE_DPAD_RIGHT;
        boolean pad = isPadSource(src) || (k >= KeyEvent.KEYCODE_BUTTON_A && k <= KeyEvent.KEYCODE_BUTTON_MODE)
                || (dpadKey && (src & InputDevice.SOURCE_DPAD) == InputDevice.SOURCE_DPAD && (src & InputDevice.SOURCE_KEYBOARD) != InputDevice.SOURCE_KEYBOARD);
        int v = pad ? Pad.fromAndroidKey(k) : Pad.fromAndroidKeyboard(k);
        if (v < 0) return false;
        if (down && e.getRepeatCount() > 0) return true;   // sin repeticion automatica
        enqueueKey(v, down);
        return true;
    }

    /** Sticks, gatillos y cruceta analogicos de los mandos. */
    public boolean handleMotionEvent(MotionEvent e) {
        if ((e.getSource() & InputDevice.SOURCE_JOYSTICK) != InputDevice.SOURCE_JOYSTICK || e.getActionMasked() != MotionEvent.ACTION_MOVE) return false;
        float lx = e.getAxisValue(MotionEvent.AXIS_X), ly = e.getAxisValue(MotionEvent.AXIS_Y);
        float rx = e.getAxisValue(MotionEvent.AXIS_Z), ry = e.getAxisValue(MotionEvent.AXIS_RZ);
        if (rx == 0f && ry == 0f) { rx = e.getAxisValue(MotionEvent.AXIS_RX); ry = e.getAxisValue(MotionEvent.AXIS_RY); }
        float lt = Math.max(e.getAxisValue(MotionEvent.AXIS_LTRIGGER), e.getAxisValue(MotionEvent.AXIS_BRAKE));
        float rt = Math.max(e.getAxisValue(MotionEvent.AXIS_RTRIGGER), e.getAxisValue(MotionEvent.AXIS_GAS));
        float hx = e.getAxisValue(MotionEvent.AXIS_HAT_X), hy = e.getAxisValue(MotionEvent.AXIS_HAT_Y);
        padAxes.update(lx, ly, rx, ry, lt, rt, hx, hy, padSink);
        return true;
    }

    /** Detecta si hay un mando conectado y de que tipo; avisa al juego (los controles tactiles se ocultan o vuelven). */
    private void refreshPads(boolean force) {
        boolean any = false;
        int type = Pad.TYPE_GENERIC;
        try {
            for (int id : InputDevice.getDeviceIds()) {
                InputDevice d = InputDevice.getDevice(id);
                if (d == null || d.isVirtual()) continue;
                if (isPadSource(d.getSources())) { any = true; type = Pad.typeOf(d.getVendorId(), d.getName()); break; }
            }
        } catch (Throwable ignored) { }
        if (!force && any == padPresent && (!any || type == padTypeSent)) return;
        padPresent = any;
        padTypeSent = type;
        if (any) enqueueKey(Pad.EV_TYPE_BASE + type, true);
        else padAxes.releaseAll(padSink);
        enqueueKey(Pad.EV_CONNECTED, any);
    }

    @Override
    protected void onAttachedToWindow() {
        super.onAttachedToWindow();
        requestFocus();
        try {
            InputManager im = (InputManager) getContext().getSystemService(Context.INPUT_SERVICE);
            if (im != null) {
                padListener = new InputManager.InputDeviceListener() {
                    @Override public void onInputDeviceAdded(int id) { refreshPads(false); }
                    @Override public void onInputDeviceRemoved(int id) { refreshPads(false); }
                    @Override public void onInputDeviceChanged(int id) { refreshPads(false); }
                };
                im.registerInputDeviceListener(padListener, null);
            }
        } catch (Throwable ignored) { }
        refreshPads(true);
    }

    @Override
    protected void onDetachedFromWindow() {
        try {
            InputManager im = (InputManager) getContext().getSystemService(Context.INPUT_SERVICE);
            if (im != null && padListener != null) im.unregisterInputDeviceListener(padListener);
        } catch (Throwable ignored) { }
        padListener = null;
        super.onDetachedFromWindow();
    }

    // ================================================================== toques (hilo UI)

    @SuppressLint("ClickableViewAccessibility")
    @Override
    public boolean onTouchEvent(MotionEvent e) {
        Layout l = layout;
        if (l == null) return true;
        final int act = e.getActionMasked();
        switch (act) {
            case MotionEvent.ACTION_DOWN:
            case MotionEvent.ACTION_POINTER_DOWN: {
                int i = e.getActionIndex();
                enqueue(e.getPointerId(i), Platform.ACTION_DOWN, vx(l, e.getX(i)), vy(l, e.getY(i)));
                break;
            }
            case MotionEvent.ACTION_MOVE: {
                int n = e.getPointerCount();
                for (int i = 0; i < n; i++) {
                    enqueue(e.getPointerId(i), Platform.ACTION_MOVE, vx(l, e.getX(i)), vy(l, e.getY(i)));
                }
                break;
            }
            case MotionEvent.ACTION_UP:
            case MotionEvent.ACTION_POINTER_UP: {
                int i = e.getActionIndex();
                enqueue(e.getPointerId(i), Platform.ACTION_UP, vx(l, e.getX(i)), vy(l, e.getY(i)));
                break;
            }
            case MotionEvent.ACTION_CANCEL: {
                int n = e.getPointerCount();
                for (int i = 0; i < n; i++) {
                    enqueue(e.getPointerId(i), Platform.ACTION_UP, vx(l, e.getX(i)), vy(l, e.getY(i)));
                }
                break;
            }
            default:
                break;
        }
        return true;
    }

    private static float vx(Layout l, float px) { return (px - l.offX) / l.scale; }
    private static float vy(Layout l, float py) { return (py - l.offY) / l.scale; }

    private void enqueue(int id, int action, float x, float y) {
        synchronized (touchLock) {
            if (action == Platform.ACTION_MOVE) {
                // fusiona MOVE consecutivos del mismo puntero
                for (int i = pendingEv.size() - 1; i >= 0; i--) {
                    Ev p = pendingEv.get(i);
                    if (p.id == id) {
                        if (p.action == Platform.ACTION_MOVE) {
                            p.x = x;
                            p.y = y;
                            return;
                        }
                        break;
                    }
                }
            }
            Ev ev = evPool.isEmpty() ? new Ev() : evPool.remove(evPool.size() - 1);
            ev.id = id;
            ev.action = action;
            ev.x = x;
            ev.y = y;
            pendingEv.add(ev);
        }
    }

    // ================================================================== hilo de juego

    private final class Runner implements Choreographer.FrameCallback {
        final HandlerThread thread = new HandlerThread("swr-game", android.os.Process.THREAD_PRIORITY_DISPLAY);
        volatile Handler handler;
        Choreographer choreo;
        boolean stopping;
        long lastRenderNs;
        long accNs;

        void start() {
            thread.start();
            handler = new Handler(thread.getLooper());
            handler.post(new Runnable() {
                @Override public void run() { startup(); }
            });
        }

        /** Llamado desde el hilo UI: detiene el hilo de juego, esperando su cierre. */
        void stop() {
            Handler h = handler;
            if (h != null) {
                h.post(new Runnable() {
                    @Override public void run() {
                        stopping = true;
                        if (choreo != null) choreo.removeFrameCallback(Runner.this);
                        shutdown();
                        thread.quit();
                    }
                });
            } else {
                thread.quit();
            }
            try {
                thread.join(4000);
            } catch (InterruptedException ie) {
                Thread.currentThread().interrupt();
            }
        }

        private void startup() {
            try {
                if (!crashChecked) {
                    crashChecked = true;
                    String prev = CrashLog.read(activity);
                    if (prev != null) {
                        errorText = prev;
                        errorDismissible = true;
                    }
                }
                if (errorText == null && !inited) {
                    startGame();
                    post(new Runnable() { @Override public void run() { refreshPads(true); } });
                } else if (inited && pausedByUs && errorText == null) {
                    pausedByUs = false;
                    phase = "resume";
                    game.resume();
                    platform.audio().resumeAll();
                }
            } catch (Throwable t) {
                fail(phase, t);
            }
            if (stopping) return;
            choreo = Choreographer.getInstance();
            choreo.postFrameCallback(this);
        }

        private void shutdown() {
            try {
                if (inited && game != null && errorText == null) {
                    for (int id = 0; id < MAX_POINTERS; id++) {
                        if (ptrDown[id]) {
                            ptrDown[id] = false;
                            game.touch(id, Platform.ACTION_UP, ptrX[id], ptrY[id]);
                        }
                    }
                    phase = "pause";
                    game.pause();
                    pausedByUs = true;
                }
            } catch (Throwable t) {
                fail(phase, t);
            }
            try { platform.audio().pauseAll(); } catch (Throwable ignored) { }
            try { platform.flush(); } catch (Throwable ignored) { }
        }

        @Override
        public void doFrame(long frameTimeNanos) {
            if (stopping) return;
            try {
                frame(frameTimeNanos);
            } catch (Throwable t) {
                fail(phase, t);
                try { drawError(layout); } catch (Throwable ignored) { }
            }
            if (!stopping) choreo.postFrameCallback(this);
        }

        private void frame(long t) {
            Layout l = layout;
            if (l == null) return;
            final boolean first = lastRenderNs == 0;
            if (!first && (t - lastRenderNs) + (long) (vsyncNs * 0.6) < STEP_NS) return; // pantalla >60 Hz: salta vsync
            long dt = first ? STEP_NS : t - lastRenderNs;
            lastRenderNs = t;
            if (dt < 0) dt = 0;
            if (dt > MAX_DELTA_NS) dt = MAX_DELTA_NS;
            // pega dt al multiplo exacto de 1/60 si esta muy cerca (elimina jitter en pantallas de 60 Hz)
            long n = Math.round(dt / (double) STEP_NS);
            if (n >= 1 && Math.abs(dt - n * STEP_NS) < STEP_NS * 0.12) dt = n * STEP_NS;

            frameNo++;
            phase = "touch";
            processTouches();
            if (errorText != null) {
                drawError(l);
                return;
            }
            if (!inited || game == null) return;

            if (l.viewW != appliedViewW) {
                phase = "resize";
                ensureFrameBitmap(l.viewW);
                game.resize(l.viewW);
                appliedViewW = l.viewW;
            }

            phase = "update";
            accNs += dt;
            int steps = 0;
            while (accNs >= STEP_NS) {
                if (steps >= MAX_STEPS) {
                    accNs = 0;
                    break;
                }
                game.update(DT);
                accNs -= STEP_NS;
                steps++;
                if (errorText != null) return;
            }

            phase = "render";
            AndroidGfx gfx = platform.androidGfx();
            gfx.bind(frameCanvas);
            game.render(gfx);
            gfx.bind(null);

            present(l);
        }

        private void processTouches() {
            ArrayList<Ev> work;
            synchronized (touchLock) {
                if (pendingEv.isEmpty()) return;
                ArrayList<Ev> tmp = pendingEv;
                pendingEv = workEv;
                workEv = tmp;
                work = workEv;
            }
            try {
                for (int i = 0; i < work.size(); i++) {
                    Ev ev = work.get(i);
                    if (errorText != null) {
                        if (errorDismissible && ev.action == Platform.ACTION_DOWN) dismissCrashScreen();
                        continue;
                    }
                    if (!inited || game == null) continue;
                    if (ev.action == ACT_KEY) { game.key(ev.id, ev.x > 0.5f); continue; }
                    int id = ev.id;
                    if (id >= 0 && id < MAX_POINTERS) {
                        ptrDown[id] = ev.action != Platform.ACTION_UP;
                        ptrX[id] = ev.x;
                        ptrY[id] = ev.y;
                    }
                    game.touch(id, ev.action, ev.x, ev.y);
                }
            } finally {
                synchronized (touchLock) {
                    evPool.addAll(work);
                    work.clear();
                }
            }
        }
    }

    // ================================================================== juego / errores (hilo de juego)

    private void startGame() {
        drawLoading();
        phase = "init";
        Game g = new Game();
        game = g;
        g.init(platform);
        inited = true;
        appliedViewW = -1;
    }

    private void dismissCrashScreen() {
        CrashLog.delete(activity);
        errorText = null;
        errorDismissible = false;
        errLines = null;
        try {
            if (!inited) startGame();
        } catch (Throwable t) {
            fail(phase, t);
        }
    }

    private void fail(String where, Throwable t) {
        Log.e(TAG, "Error del juego en " + where, t);
        String txt;
        try {
            txt = CrashLog.format(where, frameNo, t);
        } catch (Throwable t2) {
            txt = "[" + where + "]\n" + t;
        }
        errLines = null;
        errorDismissible = false;
        errorText = txt;
        CrashLog.write(activity, txt);
        try {
            platform.audio().stopMusic(0);
            platform.audio().ambient(null, 0f);
        } catch (Throwable ignored) { }
    }

    private void ensureFrameBitmap(int viewW) {
        if (frameBmp != null && frameBmp.getWidth() == viewW) return;
        Bitmap old = frameBmp;
        Bitmap b = Bitmap.createBitmap(viewW, Platform.VIEW_H, Bitmap.Config.ARGB_8888);
        b.setDensity(Bitmap.DENSITY_NONE);
        b.setHasAlpha(false);
        frameBmp = b;
        frameCanvas = new Canvas(b);
        if (old != null) old.recycle();
    }

    // ------------------------------------------------------------------ presentacion

    private Canvas lock() {
        try {
            if (useHwCanvas && Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                try {
                    Canvas c = holder.lockHardwareCanvas();
                    if (c != null) {
                        hwCanvasWorked = true;
                        return c;
                    }
                } catch (Throwable t) {
                    if (hwCanvasWorked) return null;
                    useHwCanvas = false; // nunca funciono: pasa a canvas de software
                    Log.w(TAG, "lockHardwareCanvas fallo, usando software", t);
                }
            }
            return holder.lockCanvas();
        } catch (Throwable t) {
            return null;
        }
    }

    private void unlock(Canvas c) {
        try {
            holder.unlockCanvasAndPost(c);
        } catch (Throwable ignored) { }
    }

    private void present(Layout l) {
        Bitmap b = frameBmp;
        if (b == null) return;
        Canvas c = lock();
        if (c == null) return;
        try {
            c.drawColor(Color.BLACK);
            blitSrc.set(0, 0, l.viewW, Platform.VIEW_H);
            blitDst.set(l.offX, l.offY, l.offX + l.viewW * l.scale, l.offY + Platform.VIEW_H * l.scale);
            c.drawBitmap(b, blitSrc, blitDst, blitPaint);
        } finally {
            unlock(c);
        }
    }

    private void drawLoading() {
        Layout l = layout;
        if (l == null) return;
        Canvas c = lock();
        if (c == null) return;
        try {
            c.drawColor(0xFF0A0A10);
            textPaint.setFakeBoldText(false);
            textPaint.setColor(0xFFCCCCDD);
            textPaint.setTextSize(l.sh / 14f);
            textPaint.setTextAlign(Paint.Align.CENTER);
            c.drawText("CARGANDO...", l.sw * 0.5f, l.sh * 0.5f, textPaint);
        } finally {
            unlock(c);
        }
    }

    private void buildErrorLines(Layout l, float charW, int maxChars, int maxRows) {
        String src = errorText;
        ArrayList<String> out = new ArrayList<String>();
        // titulo (marcado con \u0001 al inicio para colorearlo)
        wrapInto(out, "\u0001ERROR DEL JUEGO — toma captura de pantalla y envíala", maxChars);
        out.add("");
        String[] lines = src.split("\r?\n");
        int n = Math.min(lines.length, CRASH_LINES);
        for (int i = 0; i < n; i++) {
            String ln = lines[i].replace("\t", "  ");
            String tag = i == 0 ? "\u0002" : (ln.startsWith(" ") ? "" : "\u0003");
            wrapInto(out, tag + ln, maxChars);
        }
        if (errorDismissible) {
            out.add("");
            out.add("\u0001Toca la pantalla para descartar e iniciar el juego.");
        }
        int total = Math.min(out.size(), Math.max(4, maxRows));
        errLines = new String[total];
        for (int i = 0; i < total; i++) errLines[i] = out.get(i);
        errLayoutW = l.sw;
    }

    /** Parte en trozos de maxChars; el prefijo de color (si existe) se repite en cada trozo. */
    private static void wrapInto(ArrayList<String> out, String s, int maxChars) {
        String tag = "";
        if (s.length() > 0 && s.charAt(0) < 0x20) {
            tag = s.substring(0, 1);
            s = s.substring(1);
        }
        if (s.length() == 0) {
            out.add(tag);
            return;
        }
        for (int i = 0; i < s.length(); i += maxChars) {
            out.add(tag + s.substring(i, Math.min(s.length(), i + maxChars)));
        }
    }

    private void drawError(Layout l) {
        if (l == null) return;
        Canvas c = lock();
        if (c == null) return;
        try {
            float lineH = l.sh / 26f;
            float margin = lineH * 0.8f;
            textPaint.setTextSize(lineH * 0.8f);
            textPaint.setTextAlign(Paint.Align.LEFT);
            float charW = textPaint.measureText("M");
            int maxChars = Math.max(20, (int) ((l.sw - 2 * margin) / charW));
            int maxRows = (int) ((l.sh - 2 * margin) / lineH);
            if (errLines == null || errLayoutW != l.sw) buildErrorLines(l, charW, maxChars, maxRows);
            c.drawColor(0xFF140808);
            float y = margin + lineH * 0.8f;
            String[] lines = errLines;
            for (int i = 0; i < lines.length; i++) {
                String ln = lines[i];
                int color = 0xFFFFFFFF;
                boolean bold = false;
                if (ln.length() > 0 && ln.charAt(0) < 0x20) {
                    char tg = ln.charAt(0);
                    ln = ln.substring(1);
                    if (tg == 1) { color = 0xFFFF4545; bold = true; }
                    else if (tg == 2) color = 0xFF9AA0AA;
                    else if (tg == 3) color = 0xFFFF7070;
                }
                textPaint.setColor(color);
                textPaint.setFakeBoldText(bold);
                c.drawText(ln, margin, y, textPaint);
                y += lineH;
            }
            textPaint.setFakeBoldText(false);
        } finally {
            unlock(c);
        }
    }
}
