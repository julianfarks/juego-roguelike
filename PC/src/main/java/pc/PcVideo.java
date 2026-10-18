package pc;

import com.julianfarks.roguelike.core.Platform;
import com.julianfarks.roguelike.core.VideoCfg;

/** Platform.Video de PC: delega en la ventana. */
final class PcVideo implements Platform.Video {
    private final PcWindow win;

    PcVideo(PcWindow win) { this.win = win; }

    @Override public int[][] resolutions() { return win.resolutions(); }
    @Override public int[] nativeRes() { return win.nativeRes(); }
    @Override public int[] defaultRes() { return win.defaultRes(); }
    @Override public int refreshHz() { return win.refreshHz(); }
    @Override public boolean apply(VideoCfg c) { return win.apply(c); }
    @Override public int measuredFps() { return win.fps(); }
}
