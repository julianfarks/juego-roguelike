package com.julianfarks.roguelike.core;

import java.util.ArrayList;
import java.util.List;

/** Cuadro de dialogo: nombre del hablante, texto con aparicion progresiva, paginado automatico (el texto nunca se desborda). */
final class Dlg {
    private final List<String[]> lines = new ArrayList<>();
    private int idx, page;
    private float rev;
    private List<List<String>> pages = new ArrayList<>();
    private final int textW, maxLines;
    private final Font font;
    float speed = 42f;

    Dlg(Font font, int textW, int maxLines) { this.font = font; this.textW = textW; this.maxLines = maxLines; }

    void set(List<String[]> ls) {
        lines.clear(); lines.addAll(ls);
        idx = 0; page = 0; rev = 0;
        build();
    }

    void set(String who, String text) { List<String[]> l = new ArrayList<>(); l.add(new String[]{who, text}); set(l); }

    private void build() {
        pages = new ArrayList<>();
        if (idx >= lines.size()) return;
        List<String> w = font.wrap(lines.get(idx)[1], textW);
        for (int i = 0; i < w.size(); i += maxLines) pages.add(new ArrayList<>(w.subList(i, Math.min(w.size(), i + maxLines))));
        if (pages.isEmpty()) pages.add(new ArrayList<>());
    }

    private int pageChars() { int n = 0; if (page < pages.size()) for (String s : pages.get(page)) n += s.length(); return n; }

    void update(float dt) { rev += dt * speed; }
    boolean full() { return (int) rev >= pageChars(); }
    void showFull() { rev = pageChars(); }
    boolean finished() { return idx >= lines.size(); }
    String speaker() { return idx < lines.size() ? lines.get(idx)[0] : null; }
    int index() { return idx; }
    int count() { return lines.size(); }

    /** Primer toque: muestra todo el texto; segundo: pasa a la siguiente pagina/linea. true cuando se acaba el dialogo. */
    boolean advance() {
        if (finished()) return true;
        if (!full()) { showFull(); return false; }
        if (page + 1 < pages.size()) { page++; rev = 0; return false; }
        idx++; page = 0; rev = 0; build();
        return finished();
    }

    /** Dibuja el cuadro dentro del rectangulo dado. */
    void draw(Platform.Gfx g, float x, float y, float w, float h, float alpha, float time) {
        if (finished()) return;
        UI.panel(g, 0, x, y, w, h, 0.92f * alpha);
        String who = speaker();
        if (who != null && !who.isEmpty()) {
            float nw = font.width(who) + 14;
            UI.panel(g, 1, x + 8, y - 9, nw, 17, alpha);
            font.draw(g, who, x + 15, y - 5, UI.GOLD, alpha);
        }
        int shown = (int) rev;
        float ty = y + 12;
        for (String s : pages.get(page)) {
            int n = Math.min(s.length(), Math.max(0, shown));
            if (n > 0) font.draw(g, s.substring(0, n), x + 10, ty, 0xF0E8E0, alpha);
            shown -= s.length();
            ty += font.ch + 3;
        }
        if (full() && (int) (time * 2.2f) % 2 == 0) font.right(g, ">", x + w - 8, y + h - font.ch - 6, UI.GOLD, alpha);
        if (pages.size() > 1) font.right(g, (page + 1) + "/" + pages.size(), x + w - 8, y + 4, UI.GREY, alpha * 0.8f);
    }
}
