package com.julianfarks.roguelike.core;

/**
 * Catalogo de armas secundarias (una sola tabla). Items.SEC_* se derivan de aqui: los ids 1-10 son los originales (los guardados los usan: NO renumerar ni reordenar);
 * los ids nuevos se añaden siempre al final.
 *
 * Modelo de municion (ver Arsenal.tickReload / tickRegen):
 *   - cuerpo a cuerpo (K_FAST / K_MID): sin municion, sin recarga artificial; el ritmo lo marca su recuperacion.
 *   - reserva (K_RANGED): "ammo" usos en total (cargador + reserva); si mag > 0 dispara `mag` veces y se recarga sola (reload s) sin soltar el arma.
 *   - energia (K_MAGIC): "ammo" cargas maximas que se regeneran solas (regen s por carga) mientras el arma esta equipada.
 */
final class Wpn {
    private Wpn() {}

    static final int K_RANGED = 0, K_FAST = 1, K_MID = 2, K_MAGIC = 3;
    static final String[] KIND_NAME = {"A distancia", "Cuerpo a cuerpo rápido", "Cuerpo a cuerpo medio", "Mágica"};

    // formas de golpe cuerpo a cuerpo (cada una con su propia animacion de la hoja de arma)
    static final int S_NONE = 0, S_SLASH = 1, S_STAB = 2, S_SWEEP = 3, S_SMASH = 4, S_WHIP = 5, S_PUNCH = 6, S_CHAIN = 7, S_CLAW = 8;

    // pasivas (mascara de bits; cada arma suele tener 1-2)
    static final int P_PRECISION = 1, P_BLEED = 2, P_BURN = 4, P_POISON = 8, P_CHILL = 16, P_CHAIN = 32, P_CURSE = 64, P_ARCANE = 128, P_PIERCE = 256, P_RETURN = 512,
            P_BLUNT = 1024, P_REACH = 2048, P_RECOVER = 4096, P_DOUBLE = 8192, P_FAST = 16384, P_RESON = 32768, P_LIFE = 65536, P_RHYTHM = 131072, P_STICKY = 262144,
            P_CRIT = 524288, P_PULL = 1048576, P_COMBO3 = 2097152, P_BACK = 4194304;

    static final class Def {
        final String name, icon;
        final int kind, ammo, range, rar, col, shots;
        final float cd, dmg;
        int mag; float reload, regen;
        String style = "", fx = "", desc = "";
        // cuerpo a cuerpo
        int swing, hits = 1, reach, hgt, passive;
        float wind, act, gap, rec, lunge, knock;

        Def(String name, String icon, int kind, int ammo, float cd, float dmg, int shots, int range, int rar, int col) {
            this.name = name; this.icon = icon; this.kind = kind; this.ammo = ammo; this.cd = cd; this.dmg = dmg; this.shots = shots; this.range = range; this.rar = rar; this.col = col;
        }
        Def mag(int m, float r) { mag = m; reload = r; return this; }
        Def regen(float s) { regen = s; return this; }
        Def txt(String style, String fx, String desc) { this.style = style; this.fx = fx; this.desc = desc; return this; }
        Def pas(int p) { passive = p; return this; }
        Def melee(int swing, float wind, float act, float gap, float rec, int hits, int reach, int hgt, float lunge, float knock) {
            this.swing = swing; this.wind = wind; this.act = act; this.gap = gap; this.rec = rec; this.hits = hits; this.reach = reach; this.hgt = hgt; this.lunge = lunge; this.knock = knock; return this;
        }
        boolean melee() { return kind == K_FAST || kind == K_MID; }
        /** Duracion total de la animacion de golpe (s). */
        float swingDur() { return wind + Math.max(0, hits - 1) * gap + act + rec; }
    }

    static final Def[] T = new Def[37];
    static final int N = T.length;

    static {
        T[0] = new Def("-", "", K_RANGED, 0, 0, 0, 0, 0, 0, 0xFFFFFF);
        // ---- originales (valores identicos a los que tenian los arrays de Items)
        T[1] = new Def("Cuchillos arrojadizos", "w_knife", K_RANGED, 14, 0.32f, 0.65f, 3, 420, 0, 0xD0D8E8).txt("Ráfaga en abanico: cubre muchos enemigos cercanos.", "3 cuchillos por lanzamiento", "3 cuchillos en abanico · daño 0.65x");
        T[2] = new Def("Ballesta rúnica", "w_bolt", K_RANGED, 9, 0.32f, 2.1f, 1, 750, 1, 0xFFD25A).mag(3, 1.0f).txt("Disparo recto y potente que atraviesa.", "Atraviesa 2 enemigos · cargador de 3, recarga automática", "Atraviesa 2 enemigos · daño 2.1x");
        T[3] = new Def("Hacha arrojadiza", "w_axe", K_RANGED, 7, 0.32f, 2.4f, 1, 330, 2, 0xFF7A5A).txt("Arco alto y pesado: golpea por encima y atraviesa.", "Atraviesa 3 enemigos", "Arco alto, atraviesa 3 · daño 2.4x");
        T[4] = new Def("Orbe arcano", "w_orb", K_RANGED, 10, 0.32f, 1.5f, 1, 420, 3, 0xA060FF).txt("Esfera que persigue y explota al impactar.", "Persigue y explota", "Persigue y explota · daño 1.5x");
        T[5] = new Def("Arco de cazador", "w_bow", K_RANGED, 16, 0.42f, 1.5f, 1, 640, 1, 0x7AE04A).txt("Flecha en parábola: cuanto más lejos vuela, más daño hace.", "+90% de daño a máxima distancia", "Flecha en parábola · hasta +90% de daño lejos");
        T[6] = new Def("Chakram", "w_chakram", K_RANGED, 12, 0.55f, 1.1f, 1, 165, 3, 0x7AF0FF).txt("Gira hacia delante y regresa a tu mano: golpea a la ida y a la vuelta.", "Vuelve al jugador (máx. 1 en vuelo)", "Regresa tras lanzarlo · daño 1.1x");
        T[7] = new Def("Varita prismática", "w_wand", K_RANGED, 18, 0.28f, 1.2f, 1, 400, 2, 0xFF9ADC).txt("Alterna fuego, hielo y rayo en cada disparo.", "Quema · congela · aturde (rota)", "Fuego, hielo y rayo · daño 1.2x");
        T[8] = new Def("Lanza arrojadiza", "w_spear", K_RANGED, 6, 0.75f, 2.6f, 1, 600, 1, 0xC8B090).txt("Lanzamiento largo: atraviesa y gana daño con cada enemigo.", "Atraviesa 5 · +15% de daño por enemigo", "Atraviesa 5 · daño 2.6x");
        T[9] = new Def("Cañón de brasas", "w_ember", K_RANGED, 10, 0.50f, 0.7f, 3, 135, 2, 0xFF8A30).mag(5, 1.2f).txt("Ráfaga corta de brasas que prende fuego de cerca.", "Quema 2.5 s · 3 proyectiles · cargador de 5, recarga automática", "3 brasas cortas · quema · daño 0.7x");
        T[10] = new Def("Cetro de invocación", "w_summon", K_RANGED, 5, 1.0f, 0.55f, 1, 220, 3, 0x70F0D0).txt("Invoca espíritus temporales que atacan por ti.", "Hasta 2 espíritus · 10 s cada uno", "2 espíritus · 10 s");

        // ---- cuerpo a cuerpo rapido
        T[11] = new Def("Cuchillos dobles", "w_dknives", K_FAST, 1, 0.28f, 0.55f, 2, 26, 1, 0xC0D0E8)
                .melee(S_SLASH, 0.04f, 0.06f, 0.09f, 0.10f, 2, 26, 22, 55, 60).pas(P_PRECISION | P_FAST)
                .txt("Dos tajos rápidos seguidos; cada golpe seguido al mismo enemigo daña más.", "Precisión: +8% por golpe seguido (máx. +40%)", "2 tajos rápidos · daño 0.55x c/u · precisión");
        T[12] = new Def("Dagas gemelas", "w_twins", K_FAST, 1, 0.34f, 0.45f, 2, 22, 1, 0xB8C8F0)
                .melee(S_SLASH, 0.06f, 0.06f, 0.06f, 0.16f, 2, 22, 28, 30, 50).pas(P_BLEED | P_DOUBLE | P_BACK)
                .txt("Tajos cruzados que alcanzan también a quien te flanquea.", "Sangrado acumulable (máx. 4) · golpea delante y detrás", "Tajos cruzados · sangrado · daño 0.45x");
        T[13] = new Def("Estiletes", "w_stiletto", K_FAST, 1, 0.17f, 0.34f, 1, 30, 2, 0xE8E0F8)
                .melee(S_STAB, 0.03f, 0.04f, 0f, 0.08f, 1, 30, 8, 35, 40).pas(P_CRIT | P_FAST)
                .txt("Estocadas veloces y precisas: la cadencia más alta del cuerpo a cuerpo.", "+18% probabilidad crítica · los críticos sangran", "Estocadas muy rápidas · daño 0.34x");
        T[14] = new Def("Garras mágicas", "w_claws", K_FAST, 1, 0.40f, 0.42f, 3, 28, 2, 0xC890FF)
                .melee(S_CLAW, 0.05f, 0.05f, 0.07f, 0.14f, 3, 28, 26, 40, 50).pas(P_ARCANE)
                .txt("Tres zarpazos arcanos: cada golpe deja una marca.", "Marca arcana: a la 3ª marca estalla (daño en área)", "3 zarpazos · marcas arcanas · daño 0.42x");
        T[15] = new Def("Tonfas", "w_tonfa", K_FAST, 1, 0.38f, 0.85f, 1, 22, 1, 0xB89868)
                .melee(S_PUNCH, 0.07f, 0.06f, 0f, 0.20f, 1, 22, 24, 40, 170).pas(P_BLUNT)
                .txt("Golpe seco y corto que corta el ataque de los enemigos comunes.", "Contundente: interrumpe 0.5 s a enemigos comunes (no jefes)", "Golpe contundente · interrumpe · daño 0.85x");
        T[16] = new Def("Guanteletes", "w_gauntlet", K_FAST, 1, 0.34f, 0.80f, 2, 18, 2, 0xD8B060)
                .melee(S_PUNCH, 0.04f, 0.06f, 0.08f, 0.14f, 2, 18, 24, 50, 130).pas(P_BLUNT | P_COMBO3)
                .txt("Puñetazos encadenados; el tercero seguido es un golpe pesado.", "Contundente · 3er golpe seguido: +40% daño y empuje", "Puñetazos · 3º pesado · daño 0.8x");

        // ---- cuerpo a cuerpo medio
        T[17] = new Def("Lanza", "w_lance", K_MID, 1, 0.55f, 1.25f, 1, 54, 1, 0xE8D8B8)
                .melee(S_STAB, 0.12f, 0.08f, 0f, 0.22f, 1, 54, 12, 30, 140).pas(P_REACH | P_PIERCE)
                .txt("Estocada larga que atraviesa a los enemigos alineados.", "Alcance extendido · atraviesa hasta 3 enemigos", "Estocada larga · atraviesa 3 · daño 1.25x");
        T[18] = new Def("Alabarda", "w_halberd", K_MID, 1, 0.85f, 1.9f, 1, 42, 2, 0xC8C8D8)
                .melee(S_SMASH, 0.22f, 0.08f, 0f, 0.30f, 1, 42, 44, 25, 200).pas(P_BLUNT | P_REACH)
                .txt("Tajo vertical lento que cubre mucha altura.", "Alcance alto · contundente (interrumpe 0.6 s)", "Tajo alto y pesado · daño 1.9x");
        T[19] = new Def("Guadaña", "w_scythe", K_MID, 1, 0.78f, 1.4f, 1, 46, 2, 0xB080E0)
                .melee(S_SWEEP, 0.18f, 0.10f, 0f, 0.25f, 1, 46, 40, 20, 150).pas(P_BLEED | P_LIFE | P_BACK)
                .txt("Barrido amplio en arco que alcanza por detrás.", "Sangrado acumulable · recupera algo de vida al abatir", "Barrido amplio · sangrado · daño 1.4x");
        T[20] = new Def("Látigo", "w_whip", K_MID, 1, 0.50f, 0.85f, 1, 72, 1, 0xC89050)
                .melee(S_WHIP, 0.08f, 0.10f, 0f, 0.20f, 1, 72, 10, 10, 60).pas(P_REACH | P_PULL)
                .txt("El mayor alcance cuerpo a cuerpo; atrae un poco a quien golpea.", "Alcance extendido · atrae y ralentiza", "Látigo largo · atrae · daño 0.85x");
        T[21] = new Def("Cadena con hoja", "w_chain", K_MID, 1, 0.62f, 0.90f, 2, 58, 2, 0xA8B8D0)
                .melee(S_CHAIN, 0.10f, 0.07f, 0.16f, 0.20f, 2, 58, 18, 15, 90).pas(P_DOUBLE | P_REACH)
                .txt("La hoja sale lanzada y vuelve: golpea a la ida y al regreso.", "Doble impacto (ida y vuelta)", "Ida y vuelta · doble impacto · daño 0.9x c/u");
        T[22] = new Def("Espada corta", "w_shortsword", K_MID, 1, 0.30f, 0.90f, 1, 34, 0, 0xD8E0EC)
                .melee(S_SLASH, 0.06f, 0.07f, 0f, 0.12f, 1, 34, 30, 45, 90).pas(P_FAST | P_RHYTHM)
                .txt("Ligera y fiable: tajos rápidos sin demasiada recuperación.", "Ritmo: 3 golpes seguidos aceleran el siguiente", "Tajo rápido · ritmo · daño 0.9x");
        T[23] = new Def("Martillo de combate", "w_warhammer", K_MID, 1, 1.05f, 2.7f, 1, 34, 3, 0xD0A070)
                .melee(S_SMASH, 0.30f, 0.10f, 0f, 0.38f, 1, 34, 38, 15, 260).pas(P_BLUNT)
                .txt("Mazazo lento con onda de impacto: aturde a los enemigos comunes.", "Contundente: aturde 0.8 s (no jefes) · onda de impacto", "Mazazo lento y pesado · aturde · daño 2.7x");

        // ---- a distancia (reserva)
        T[24] = new Def("Dagas arrojadizas", "w_tdagger", K_RANGED, 12, 0.26f, 1.0f, 1, 480, 1, 0xB8C8E8)
                .pas(P_PRECISION | P_RETURN)
                .txt("Una daga rápida y precisa; si falla, vuelve a tu mano.", "Precisión: +8% por golpe seguido · si falla, regresa y recuperas la daga", "Daga rápida · precisión · regresa si falla · daño 1.0x");
        T[25] = new Def("Shurikens", "w_shuriken", K_RANGED, 18, 0.40f, 0.45f, 3, 360, 1, 0xA8D0B0)
                .pas(P_POISON | P_PIERCE)
                .txt("Tres estrellas giratorias en abanico cerrado, envenenadas.", "Veneno acumulable (máx. 3) · atraviesan 1 enemigo", "3 estrellas envenenadas · daño 0.45x");
        T[26] = new Def("Bombas alquímicas", "w_alchbomb", K_RANGED, 6, 0.85f, 1.9f, 1, 220, 2, 0xFF9A40)
                .pas(P_BURN)
                .txt("Frasco que estalla en llamas: daño en área y quemadura.", "Quemadura acumulable (máx. 3) · explosión en área", "Frasco incendiario · área · daño 1.9x");
        T[27] = new Def("Bombas adhesivas", "w_stickybomb", K_RANGED, 5, 0.80f, 2.0f, 1, 220, 2, 0x8AD0FF)
                .pas(P_STICKY | P_CHILL)
                .txt("Se pega al primer enemigo y estalla tras un instante, ralentizando.", "Se adhiere · estalla a 1 s · ralentiza", "Se pega y estalla · ralentiza · daño 2.0x");

        // ---- magicas (energia: cargas que se regeneran)
        T[28] = new Def("Varita elemental", "w_elemwand", K_MAGIC, 9, 0.38f, 1.0f, 1, 400, 2, 0xFFB060).regen(1.0f)
                .pas(P_RESON | P_BURN | P_CHILL | P_CHAIN)
                .txt("Fuego, hielo y rayo en ciclo: completar los tres desata una nova elemental.", "Resonancia: fuego → hielo → rayo → nova en área · energía regenerable", "Ciclo elemental · nova · daño 1.0x");
        T[29] = new Def("Varita de fuego", "w_firewand", K_MAGIC, 8, 0.45f, 1.05f, 1, 400, 1, 0xFF7A30).regen(1.1f)
                .pas(P_BURN)
                .txt("Bola de fuego que prende y acumula quemadura.", "Quemadura acumulable (máx. 3) · energía regenerable", "Bola de fuego · quemadura · daño 1.05x");
        T[30] = new Def("Varita de hielo", "w_icewand", K_MAGIC, 8, 0.50f, 0.90f, 1, 400, 1, 0x7AE8FF).regen(1.2f)
                .pas(P_CHILL | P_PIERCE)
                .txt("Esquirla helada: tres impactos congelan brevemente (los jefes solo se ralentizan).", "Frío acumulable: ralentiza; a la 3ª carga congela 1 s · energía regenerable", "Esquirla helada · frío · daño 0.9x");
        T[31] = new Def("Varita eléctrica", "w_stormwand", K_MAGIC, 10, 0.36f, 0.80f, 1, 420, 1, 0xFFE860).regen(0.9f)
                .pas(P_CHAIN | P_FAST)
                .txt("Rayo veloz que salta a enemigos cercanos.", "Cadena: salta a 2 enemigos (55%) · energía regenerable", "Rayo en cadena · daño 0.8x");
        T[32] = new Def("Orbe oscuro", "w_darkorb", K_MAGIC, 6, 0.70f, 1.2f, 1, 360, 2, 0x9050D0).regen(1.5f)
                .pas(P_CURSE | P_PIERCE)
                .txt("Esfera lenta que crece y atraviesa: maldice a quien toca.", "Oscuridad: +12% de daño recibido durante 4 s · atraviesa 2", "Esfera oscura · maldice · daño 1.2x");
        T[33] = new Def("Catalizador de veneno", "w_venomcat", K_MAGIC, 8, 0.50f, 0.60f, 1, 300, 2, 0x70E080).regen(1.1f)
                .pas(P_POISON)
                .txt("Frasco tóxico: la nube envenena a todos los cercanos.", "Veneno acumulable (máx. 5) · nube en área · energía regenerable", "Nube tóxica · veneno · daño 0.6x");
        T[34] = new Def("Cetro de sangre", "w_bloodscepter", K_MAGIC, 7, 0.60f, 1.1f, 1, 340, 3, 0xD02848).regen(1.3f)
                .pas(P_BLEED | P_LIFE)
                .txt("Orbe carmesí: sangrado acumulable y un poco de vida a cambio.", "Sangrado (máx. 4) · roba 3% del daño (límite por tiempo)", "Orbe carmesí · sangrado · roba vida · daño 1.1x");
        T[35] = new Def("Cristal arcano", "w_crystal", K_MAGIC, 8, 0.55f, 0.70f, 2, 380, 2, 0xB0A0FF).regen(1.0f)
                .pas(P_ARCANE | P_RECOVER)
                .txt("Dos esquirlas guiadas que marcan al objetivo.", "Marca arcana (3 = estallido) · el estallido devuelve 1 carga", "2 esquirlas guiadas · marcas · daño 0.7x");
        T[36] = new Def("Talismán explosivo", "w_talisman", K_MAGIC, 5, 0.90f, 2.4f, 1, 260, 3, 0xFF6040).regen(2.0f)
                .pas(P_STICKY | P_BLUNT)
                .txt("Se adhiere y estalla con gran radio: aturde a los enemigos comunes.", "Se adhiere · estalla a 0.9 s · aturde 0.4 s (no jefes)", "Talismán que estalla · aturde · daño 2.4x");
    }

    static Def of(int id) { return id > 0 && id < N ? T[id] : T[0]; }
}
