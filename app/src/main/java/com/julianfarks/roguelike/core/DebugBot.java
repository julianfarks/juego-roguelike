package com.julianfarks.roguelike.core;

/** Bot de pruebas para el banco de escritorio (--bot): navega menus y juega sin ayuda. No se usa en Android. */
public final class DebugBot {
    private final boolean[] held = new boolean[256];
    private int lastClassFrame = -999, lastAct;
    private int stuck, jumpUntil;
    private boolean warped;
    private final java.util.HashSet<Object> done = new java.util.HashSet<>();
    private float lastX;
    public static int classId = System.getenv("BOT_CLASS") != null ? Integer.parseInt(System.getenv("BOT_CLASS")) : 0;
    public static boolean godMode = System.getenv("BOT_GOD") != null;

    private void hold(Game g, int code, boolean down) {
        if (held[code] != down) { held[code] = down; g.key(code, down); }
    }

    private void tap(Game g, int code) { g.key(code, true); g.key(code, false); }

    public void tick(Game g, int frame) {
        Screen s = g.cur;
        if (s == null || g.fadeDir == 1) return;
        if (s instanceof Screens.Title) {
            if (frame % 20 == 0) { Screen.Hit h = ((Screens.Title) s).hits.get(0); s.touch(0, 0, h.x + 5, h.y + 5); s.touch(0, 2, h.x + 5, h.y + 5); }
            return;
        }
        if (s instanceof ClassScreen) {
            ClassScreen cs = (ClassScreen) s;
            if (frame - lastClassFrame > 30) {
                lastClassFrame = frame;
                Save.S.souls = 5000;
                for (int i = 0; i < 10; i++) Save.S.classUnlocked[i] = true;
                Save.S.lastClass = classId;
                cs.hits.clear();
                game_start(g, cs);
            }
            return;
        }
        if (!(s instanceof RunScreen)) return;
        RunScreen rs = (RunScreen) s;
        if (rs.lv == null) return;
        Level lv = rs.lv;
        Player p = lv.pl;
        String warp = System.getenv("BOT_WARP");
        if (warp != null && !warped && rs.fadeA < 0.05f && frame > 150) {
            warped = true;
            String[] w = warp.split(":");
            int b = w.length > 1 ? Integer.parseInt(w[1]) : 0;
            rs.rs.biome = Biome.ALL[b]; rs.rs.stage = Biome.ALL[b].tier;
            rs.rs.roomNo = w[0].equals("boss") ? 5 : 1;
            int type = w[0].equals("boss") ? Room.BOSS : w[0].equals("shop") ? Room.SHOP : w[0].equals("forge") ? Room.FORGE : w[0].equals("bless") ? Room.BLESSING
                    : w[0].equals("rest") ? Room.REST : w[0].equals("elite") ? Room.ELITE : w[0].equals("hub") ? Room.HUB : w[0].equals("treasure") ? Room.TREASURE : Room.COMBAT;
            rs.rs.gold = 400;
            rs.loadRoom(type);
            return;
        }
        if (godMode) { rs.rs.hp = rs.rs.stats.maxHp; }
        switch (rs.ov) {
            case RunScreen.OV_BLESS:
                if (rs.ovT > 1.3f) for (Screen.Hit h : rs.hits) { rs.touch(0, 0, h.x + 5, h.y + 5); rs.touch(0, 2, h.x + 5, h.y + 5); break; }
                return;
            case RunScreen.OV_SHOP: case RunScreen.OV_FORGE:
                if (rs.ovT > 2.0f) rs.back();
                return;
            case RunScreen.OV_PAUSE:
                if (rs.ovT > 0.5f) rs.back();
                return;
            case RunScreen.OV_NONE: break;
            default: return;
        }
        if (!p.alive || lv.cinematic) { for (int i = 0; i < 256; i++) if (held[i]) hold(g, i, false); return; }
        // objetivo
        Ent target = null; float bd = 9999;
        for (Enemy e : lv.enemies) if (e.alive) { float d = Math.abs(e.x - p.x) + Math.abs(e.y - p.y) * 0.5f; if (d < bd) { bd = d; target = e; } }
        if (lv.boss != null && lv.boss.alive) { target = lv.boss; bd = Math.abs(lv.boss.x - p.x); }
        float tx = p.x, ty = p.y;
        boolean fight = false;
        if (target != null) { tx = target.x; ty = target.y; fight = true; }
        else {
            Prop best = null; float pd = 9999;
            for (Prop pr : lv.props) {
                if (pr.dead) continue;
                if (done.contains(pr)) continue;
                boolean want = pr.kind.equals("door") || pr.kind.equals("merchant") || pr.kind.equals("forge") || pr.kind.equals("fountain") || pr.kind.equals("portal") || (pr.kind.equals("altar") && !pr.used) || (pr.kind.equals("chest") && !pr.used);
                if (!want) continue;
                float d = Math.abs(pr.x - p.x) + (pr.kind.equals("door") ? -50 : 0);
                if (d < pd) { pd = d; best = pr; }
            }
            if (best != null) { tx = best.x; ty = best.y; }
            else { tx = lv.room.exitX; ty = lv.room.exitY; }
            // recoger reliquias/botin cercano
            for (Pickup pk : lv.pickups) if (!pk.dead && pk.type == Pickup.RELIC) { tx = pk.x; ty = pk.y; }
        }
        float dx = tx - p.x;
        float ad = Math.abs(dx);
        boolean near = fight && ad < 36 && Math.abs(ty - p.y) < 50;
        boolean ranged = fight && target instanceof Boss && ad < 120;
        if (ad > (fight ? 28 : 10)) { hold(g, 'D', dx > 0); hold(g, 'A', dx < 0); }
        else { hold(g, 'D', false); hold(g, 'A', false); }
        // salto
        float dirx = dx > 0 ? 1 : -1;
        int aheadT = lv.room.tile((int) Math.floor((p.x + dirx * 14) / 16), (int) Math.floor((p.y + 4) / 16));
        int ahead2 = lv.room.tile((int) Math.floor((p.x + dirx * 30) / 16), (int) Math.floor((p.y + 4) / 16));
        boolean gap = p.onGround && ad > 20 && (aheadT == Room.AIR || aheadT == Room.SPIKE);
        boolean jump = gap || (p.hitWall && p.onGround) || (ty < p.y - 30 && p.onGround && frame % 20 == 0) || (frame % 97 == 0 && p.onGround);
        if (jump && frame > jumpUntil + 20) jumpUntil = frame + 22;
        hold(g, 'W', frame < jumpUntil);
        // ataque
        if (near || ranged) { if (frame % 6 == 0) tap(g, 'J'); }
        else hold(g, 'J', false);
        // habilidades
        if (fight && bd < 160) {
            for (int i = 0; i < 3; i++) if (rs.rs.cd[i] <= 0 && frame % 30 == i * 8) tap(g, new int[]{'U', 'I', 'O'}[i]);
            if (rs.rs.ult >= 100 && frame % 40 == 0) tap(g, 'P');
        }
        if (fight && frame % 83 == 0 && p.onGround) tap(g, 'K');
        if (rs.rs.hp < rs.rs.stats.maxHp * 0.4f && frame % 50 == 0) tap(g, 'Q');
        // interactuar
        if (!fight && frame % 15 == 0) {
            Prop n = lv.nearestInteractable();
            if (n != null) { tap(g, 'E'); if (!n.kind.equals("door") && !n.kind.equals("portal")) done.add(n); }
        }
        // atasco
        if (Math.abs(p.x - lastX) < 0.5f && !near) stuck++; else stuck = 0;
        lastX = p.x;
        if (stuck > 60) { tap(g, 'W'); if (stuck > 90) { tap(g, 'K'); stuck = 0; } }
    }

    private void game_start(Game g, ClassScreen cs) {
        cs.layout();
        // el boton de jugar es el ultimo
        Screen.Hit h = cs.hits.get(cs.hits.size() - 1);
        Save.S.lastClass = classId;
        g.go(new RunScreen(g, ClassDef.ALL[classId], 0));
    }
}
