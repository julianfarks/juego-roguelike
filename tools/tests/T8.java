package com.julianfarks.roguelike.core;

import java.lang.reflect.Proxy;
import java.util.*;
import java.util.function.Consumer;

/** Pruebas de moneda premium, guardado versionado, cosmeticos, revividas, anuncios, compras y registro del modo infinito. */
public class T8 {
    static int f = 0;
    static void ck(String n, boolean ok) { System.out.println((ok ? "ok   " : "FAIL ") + n); if (!ok) f++; }

    static final Map<String, String> disk = new HashMap<>();
    static Platform plat() {
        final Platform.Store st = new Platform.Store() {
            public String get(String k, String d) { String v = disk.get(k); return v == null ? d : v; }
            public void put(String k, String v) { disk.put(k, v); }
            public void commit() {}
        };
        return (Platform) Proxy.newProxyInstance(T8.class.getClassLoader(), new Class[]{Platform.class}, (p, m, a) -> {
            if (m.getName().equals("store")) return st;
            Class<?> r = m.getReturnType();
            if (r == boolean.class) return false; if (r == int.class) return 0; if (r == float.class) return 0f; if (r == long.class) return 0L;
            return null;
        });
    }
    static void reload(Platform p) { Save.load(p); }

    /** Proveedor de anuncios de prueba: guarda el callback para dispararlo a mano. */
    static class FakeAds implements Services.AdProvider {
        boolean ready = true; Consumer<Services.AdResult> cb;
        public boolean isReady(Services.AdPlacement p) { return ready; }
        public void show(Services.AdPlacement p, Consumer<Services.AdResult> done) { cb = done; }
    }

    public static void main(String[] a) {
        Platform p = plat();
        disk.clear();
        reload(p);
        Save.devGems = 0;
        // ---------------- moneda premium
        ck("saldo inicial 0", Wallet.gems() == 0 && Save.S.gems == 0);
        ck("no gasta con saldo 0", !Wallet.spend(1));
        ck("no gasta 0 ni negativos", !Wallet.spend(0) && !Wallet.spend(-5) && Wallet.gems() == 0);
        PurchaseReceipt r1 = new PurchaseReceipt("ORD-1", "gems_100", 100, true);
        ck("recibo NO verificado no acredita", !Wallet.credit(new PurchaseReceipt("ORD-X", "g", 100, false)) && Wallet.gems() == 0);
        ck("recibo sin id no acredita", !Wallet.credit(new PurchaseReceipt("", "g", 100, true)));
        ck("recibo con 0 gemas no acredita", !Wallet.credit(new PurchaseReceipt("ORD-0", "g", 0, true)));
        ck("recibo verificado acredita", Wallet.credit(r1) && Wallet.gems() == 100);
        ck("mismo recibo no se acredita dos veces", !Wallet.credit(r1) && !Services.fulfill(r1) && Wallet.gems() == 100);
        ck("no gasta mas de lo que hay", !Wallet.spend(101) && Wallet.gems() == 100);
        Save.S.souls = 777;
        ck("gasto valido", Wallet.spend(30) && Wallet.gems() == 70);
        ck("gemas y almas independientes", Save.S.souls == 777);
        Save.S.souls -= 100; ck("gastar almas no toca gemas", Wallet.gems() == 70);
        // gemas de prueba
        ck("devGrant exige modo desarrollador", !Wallet.devGrant(50) && Save.devGems == 0);
        Save.S.devUnlocked = true;
        ck("devGrant en modo dev", Wallet.devGrant(50) && Wallet.gems() == 120);
        ck("gasta primero las de prueba", Wallet.spend(60) && Save.devGems == 0 && Save.S.gems == 60);
        Save.devGems = 40;
        Save.S.write();
        reload(p);
        ck("las gemas de prueba NO se guardan", Save.S.gems == 60 && Save.devGems == 40 /*estatica de sesion*/ );
        Save.devGems = 0;
        ck("saldo real persiste tras reiniciar", Wallet.gems() == 60 && Save.S.gemTx.contains("ORD-1"));
        reload(p);
        ck("el recibo sigue bloqueado tras reiniciar", !Wallet.credit(r1) && Wallet.gems() == 60);
        // ---------------- guardado versionado y compatibilidad
        disk.clear(); Save.S = new Save(); Save.devGems = 0;
        disk.put("save", "{\"souls\":1234,\"totalSouls\":5000,\"runs\":9,\"wins\":2,\"kills\":300,\"cu\":[1,1,1,0,1,0,0,0,0,0],\"last\":4}");
        reload(p);
        ck("guardado v1: conserva almas y clases", Save.S.souls == 1234 && Save.S.classUnlocked[4] && Save.S.runs == 9 && Save.S.lastClass == 4);
        ck("guardado v1: gemas empiezan en 0", Save.S.gems == 0 && Save.S.owned.isEmpty() && Save.S.infRuns == 0);
        ck("copia de seguridad v1 creada", !disk.getOrDefault("save_bak_v1", "").isEmpty());
        Save.S.gems = 25; Save.S.write(); reload(p);
        ck("migrado: conserva lo viejo y lo nuevo", Save.S.souls == 1234 && Save.S.gems == 25 && Save.S.classUnlocked[4]);
        disk.put("save", "{\"ver\":99,\"souls\":5,\"gems\":7}");
        reload(p);
        ck("version futura: solo lectura", Save.S.readOnly && Save.S.souls == 5);
        String before = disk.get("save"); Save.S.souls = 9999; Save.S.write();
        ck("version futura: no se sobrescribe", disk.get("save").equals(before) && !disk.getOrDefault("save_bak_v99", "").isEmpty());
        disk.clear(); reload(p); Save.devGems = 0;
        // reset del progreso conserva lo comprado
        Save.S.gems = 40; Save.S.owned.add("dev_tint_ember"); Save.S.infBestFloor = 4; Save.S.reset();
        ck("reiniciar progreso conserva gemas, compras y records", Save.S.gems == 40 && Save.S.owned.contains("dev_tint_ember") && Save.S.infBestFloor == 4);
        // ---------------- cosmeticos
        disk.clear(); reload(p); Save.devGems = 0; Save.S.devUnlocked = true;
        ClassDef paladin = ClassDef.ALL[0], shadow = ClassDef.ALL[1];
        Cosmetics.Item prem = Cosmetics.find("dev_tint_violet"), earned = Cosmetics.find("dev_tint_ember");
        ck("catalogo de prueba solo con modo dev", Cosmetics.catalog().size() == 2);
        Save.S.devUnlocked = false;
        ck("sin modo dev el catalogo oficial esta vacio", Cosmetics.catalog().isEmpty());
        Save.S.devUnlocked = true;
        ck("comprar sin saldo falla y no cambia nada", !Cosmetics.buy("dev_tint_violet") && !Cosmetics.owns("dev_tint_violet") && Wallet.gems() == 0);
        ck("articulo EARNED no se compra con gemas", !Cosmetics.buy("dev_tint_ember"));
        Wallet.credit(new PurchaseReceipt("T-1", "g", 12, true));
        ck("comprar con saldo", Cosmetics.buy("dev_tint_violet") && Cosmetics.owns("dev_tint_violet") && Wallet.gems() == 7);
        ck("no se compra dos veces", !Cosmetics.buy("dev_tint_violet") && Wallet.gems() == 7);
        ck("no se equipa lo no poseido", !Cosmetics.equip(paladin, "dev_tint_ember") && Cosmetics.equipped(paladin) == null);
        ck("equipar lo poseido", Cosmetics.equip(paladin, "dev_tint_violet") && Cosmetics.equipped(paladin) == prem && Cosmetics.tintFor(paladin) == 0xB080FF);
        ck("el skin es por espadachin", Cosmetics.equipped(shadow) == null && Cosmetics.tintFor(shadow) == 0);
        reload(p);
        ck("compra y equipado persisten", Cosmetics.owns("dev_tint_violet") && Cosmetics.equipped(paladin) == prem && Wallet.gems() == 7);
        ck("quitar skin vuelve al original", Cosmetics.equip(paladin, "") && Cosmetics.equipped(paladin) == null);
        ck("conceder es idempotente", Cosmetics.grant("dev_tint_ember") && !Cosmetics.grant("dev_tint_ember") && !Cosmetics.grant("no_existe"));
        PurchaseReceipt skinR = new PurchaseReceipt("ORD-S1", "dev_tint_violet", 0, true);
        ck("producto ya poseido no se entrega de nuevo (recibo)", !Services.fulfill(skinR));
        PurchaseReceipt skinR2 = new PurchaseReceipt("ORD-S2", "dev_tint_ember", 0, true); Save.S.owned.remove("dev_tint_ember");
        ck("recibo verificado entrega el articulo una sola vez", Services.fulfill(skinR2) && Cosmetics.owns("dev_tint_ember") && !Services.fulfill(skinR2));
        // ---------------- gemas de prueba: nunca se vuelven saldo valido
        Save.S.devUnlocked = true; Save.S.gems = 0; Save.devGems = 0; Save.S.owned.clear(); Save.S.write();
        Wallet.devGrant(100);
        ck("dev: las gemas de prueba cuentan para el saldo mostrado", Wallet.gems() == 100 && Wallet.realGems() == 0);
        Cosmetics.ALL.add(new Cosmetics.Item("oficial_x", "Oficial X", "x", Cosmetics.Kind.SKIN, Cosmetics.Source.PREMIUM, -1, 10, null, 0));
        ck("dev: NO compran articulos oficiales", !Cosmetics.buy("oficial_x") && !Cosmetics.owns("oficial_x") && Save.devGems == 100);
        ck("dev: si compran articulos [DEV]", Cosmetics.buy("dev_tint_violet") && Save.devGems == 95 && Save.S.gems == 0);
        Save.S.write(); reload(p);
        ck("dev: tras reiniciar no queda saldo real", Save.S.gems == 0 && Wallet.realGems() == 0);
        Save.S.gems = 20; Save.devGems = 100;
        ck("dev: articulo oficial usa solo gemas reales", Cosmetics.buy("oficial_x") && Save.S.gems == 10 && Save.devGems == 100);
        Cosmetics.ALL.clear();
        Save.S.gems = 0; Save.devGems = 100;
        RunState rd = new RunState(paladin, 5, 0); rd.infinite = true;
        ck("dev: revivir con gemas de prueba marca la run", Infinite.consume(rd, Infinite.Method.GEMS, p) && rd.devAssisted && Save.devGems == 95);
        Infinite.Result rr = Infinite.resultOf(rd); rr.floors = 9; rr.score = 99999;
        int best0 = Save.S.infBestFloor;
        ck("dev: el resultado marcado no toca records", rr.dev && !Infinite.record(Save.S, rr) && Save.S.infBestFloor == best0 && Save.S.infFloors == 0);
        Infinite.Result rb = Infinite.Result.parse(Save.S.infLog.get(Save.S.infLog.size() - 1));
        ck("dev: queda en el historial marcado", rb != null && rb.dev);
        ck("dev: la marca no se puede quitar editando el registro", Infinite.Result.parse(Save.S.infLog.get(Save.S.infLog.size() - 1).replace("\"dev\":true", "\"dev\":false")) == null);
        RunState rn = new RunState(paladin, 5, 0); rn.infinite = true; Save.S.gems = 50; Save.devGems = 0;
        ck("real: revivir con gemas reales NO marca la run", Infinite.consume(rn, Infinite.Method.GEMS, p) && !rn.devAssisted);
        Save.devGems = 0; Save.S.gems = 0; Save.S.devUnlocked = false;
        // ---------------- el campana no cambia
        RunState rcm = new RunState(paladin, 1, 0); rcm.stage = 2; rcm.roomNo = 3;
        ck("campana: dificultad igual que antes", rcm.power() == 2 * 6 + 3 && !rcm.infinite);
        // ---------------- anuncios (una sola recompensa)
        FakeAds ads = new FakeAds(); Services.ads = ads;
        int[] granted = {0};
        ck("anuncio no disponible: no empieza", !(new FakeAds() {{ ready = false; }}.isReady(null)));
        ck("pide anuncio", Services.requestRewardedAd(Services.AdPlacement.REVIVE_STANDARD, () -> granted[0]++) && Services.adInFlight());
        ck("no permite otro en curso", !Services.requestRewardedAd(Services.AdPlacement.REVIVE_STANDARD, () -> granted[0]++));
        ads.cb.accept(Services.AdResult.COMPLETED);
        ads.cb.accept(Services.AdResult.COMPLETED);
        ck("recompensa UNA sola vez aunque el aviso se repita", granted[0] == 1 && !Services.adInFlight());
        Services.requestRewardedAd(Services.AdPlacement.REVIVE_STANDARD, () -> granted[0]++); ads.cb.accept(Services.AdResult.DISMISSED);
        Services.requestRewardedAd(Services.AdPlacement.REVIVE_STANDARD, () -> granted[0]++); ads.cb.accept(Services.AdResult.FAILED);
        ck("cerrar o fallar el anuncio no da recompensa", granted[0] == 1 && !Services.adInFlight());
        Services.ads = Services.NO_ADS;
        ck("sin proveedor no hay anuncios", !Services.requestRewardedAd(Services.AdPlacement.REVIVE_STANDARD, () -> granted[0]++) && granted[0] == 1);
        // ---------------- revividas
        disk.clear(); reload(p); Save.devGems = 0; Save.S.gems = 0;
        RunState rs = new RunState(paladin, 42, 0);
        rs.infinite = true; rs.stage = 2;
        ck("sin anuncios ni gemas no se ofrece revivir", Infinite.hasRevivesLeft(rs) && !Infinite.anyAvailable(rs) && Infinite.offers(rs).size() == 2);
        ck("sin gemas no revive", !Infinite.consume(rs, Infinite.Method.GEMS, p) && rs.revivesUsed == 0);
        Save.S.gems = 100;
        List<Infinite.Offer> o0 = Infinite.offers(rs);
        ck("1a: anuncio o gemas", o0.size() == 2 && o0.get(0).method == Infinite.Method.AD_STANDARD && o0.get(1).method == Infinite.Method.GEMS && o0.get(1).available);
        ck("1a: anuncio no disponible aparece bloqueado", !o0.get(0).available);
        ads.ready = true; Services.ads = ads;
        ck("1a: con proveedor listo el anuncio queda disponible", Infinite.offers(rs).get(0).available);
        ck("1a con gemas descuenta y cuenta", Infinite.consume(rs, Infinite.Method.GEMS, p) && rs.revivesUsed == 1 && Save.S.gems == 95);
        List<Infinite.Offer> o1 = Infinite.offers(rs);
        ck("2a: anuncio LARGO o gemas", o1.size() == 2 && o1.get(0).method == Infinite.Method.AD_LONG && o1.get(1).cost == 10);
        ck("2a: formato de la 1a rechazado", !Infinite.consume(rs, Infinite.Method.AD_STANDARD, p) && rs.revivesUsed == 1);
        ck("2a con anuncio largo", Infinite.consume(rs, Infinite.Method.AD_LONG, p) && rs.revivesUsed == 2 && Save.S.gems == 95);
        List<Infinite.Offer> o2 = Infinite.offers(rs);
        ck("3a: SOLO gemas", o2.size() == 1 && o2.get(0).method == Infinite.Method.GEMS && o2.get(0).cost == 15);
        ck("3a: anuncio rechazado", !Infinite.consume(rs, Infinite.Method.AD_LONG, p) && !Infinite.consume(rs, Infinite.Method.AD_STANDARD, p) && rs.revivesUsed == 2);
        ck("3a con gemas", Infinite.consume(rs, Infinite.Method.GEMS, p) && rs.revivesUsed == 3 && Save.S.gems == 80);
        ck("no hay 4a revivida", !Infinite.hasRevivesLeft(rs) && Infinite.offers(rs).isEmpty() && !Infinite.consume(rs, Infinite.Method.GEMS, p) && rs.revivesUsed == 3 && Save.S.gems == 80);
        RunState rc = new RunState(paladin, 7, 0); rc.infinite = true; rc.ruleset = Infinite.COMPETITIVE;
        ck("reglas competitivas: sin revividas compradas", !Infinite.hasRevivesLeft(rc) && !Infinite.consume(rc, Infinite.Method.GEMS, p));
        RunState rcamp = new RunState(paladin, 7, 0);
        ck("campana normal: no hay revividas del infinito", !Infinite.hasRevivesLeft(rcamp));
        Services.ads = Services.NO_ADS;
        // ---------------- dificultad y puntaje
        boolean mono = true;
        for (int fl = 1; fl < 30; fl++) mono &= Infinite.power(fl + 1, 0) > Infinite.power(fl, 4) && Infinite.bossHpMul(fl + 1) > Infinite.bossHpMul(fl) && Infinite.eliteChance(fl + 1) >= Infinite.eliteChance(fl);
        ck("la dificultad crece piso a piso", mono && Infinite.eliteChance(1) == 0f && Infinite.eliteChance(2) == 0f && Infinite.eliteChance(3) > 0f && Infinite.eliteChance(99) <= 0.5f);
        ck("el piso 1 del infinito >= final de campana", Infinite.power(1, 0) >= 18);
        Infinite.Result A = new Infinite.Result(), B = new Infinite.Result();
        A.floors = 5; A.score = 100; A.kills = 10; A.timeS = 500; B.floors = 4; B.score = 99999; B.kills = 9999; B.timeS = 1;
        ck("clasificacion: pisos pesan mas que puntaje", Infinite.Result.compare(A, B) > 0 && Infinite.Result.compare(B, A) < 0);
        B.floors = 5; B.score = 100; ck("desempate 1: puntaje", Infinite.Result.compare(A, B) == (A.kills > B.kills ? 1 : A.kills == B.kills ? (B.timeS > A.timeS ? 1 : 0) : -1));
        B.score = 120; ck("desempate: mayor puntaje gana", Infinite.Result.compare(B, A) > 0);
        B.score = 100; B.kills = 10; B.timeS = 400; ck("desempate: menos tiempo gana", Infinite.Result.compare(B, A) > 0);
        ck("puntaje: un piso vale mas que muchas bajas", Infinite.score(1, 0, 0, 0) > Infinite.score(0, 900, 0, 0));
        // ---------------- registro del infinito
        disk.clear(); reload(p); Save.devGems = 0;
        RunState ri = new RunState(shadow, 99, 0);
        ri.infinite = true; ri.floor = 4; ri.floorsDone = 3; ri.kills = 120; ri.bossKills = 3; ri.infRooms = 17; ri.time = 640; ri.revivesUsed = 2;
        Infinite.Result res = Infinite.resultOf(ri);
        ck("resultado coherente", res.floors == 3 && res.reached == 4 && res.kills == 120 && res.bosses == 3 && res.timeS == 640 && res.revives == 2 && res.score == Infinite.score(3, 120, 3, 17));
        ri.infBaseKills = 20; ri.infBaseBoss = 1; ri.infT0 = 40;
        Infinite.Result res2 = Infinite.resultOf(ri);
        ck("continuar campana: no cuenta lo anterior", res2.kills == 100 && res2.bosses == 2 && res2.timeS == 600);
        ck("primer record", Infinite.record(Save.S, res) && Save.S.infBestFloor == 3 && Save.S.infRuns == 1 && Save.S.infKills == 120);
        Infinite.Result low = Infinite.resultOf(ri); low.floors = 1; low.score = 5;
        ck("peor resultado no pisa el record", !Infinite.record(Save.S, low) && Save.S.infBestFloor == 3 && Save.S.infRuns == 2);
        Save.S.write(); reload(p);
        ck("registro persiste", Save.S.infRuns == 2 && Save.S.infBestFloor == 3 && Save.S.infLog.size() == 2);
        Infinite.Result back = Infinite.Result.parse(Save.S.infLog.get(0));
        ck("el registro se lee de vuelta", back != null && back.floors == 3 && back.score == res.score && back.ruleset.equals("normal"));
        ck("registro alterado se descarta", Infinite.Result.parse(Save.S.infLog.get(0).replace("\"fl\":3", "\"fl\":30")) == null);
        for (int i = 0; i < 40; i++) Infinite.record(Save.S, low);
        ck("el registro se acota", Save.S.infLog.size() == Infinite.LOG_KEEP);
        System.out.println("FALLOS=" + f);
    }
}
