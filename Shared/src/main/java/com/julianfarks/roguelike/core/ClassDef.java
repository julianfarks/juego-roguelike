package com.julianfarks.roguelike.core;

/** Definicion de clase jugable (del mod SwordmanMagic). */
public final class ClassDef {
    public static final class Skill {
        public final String name, desc, icon, sfx;
        public final float cd;
        Skill(String name, String desc, String icon, String sfx, float cd) { this.name = name; this.desc = desc; this.icon = icon; this.sfx = sfx; this.cd = cd; }
    }

    public final int id;
    public final String key, name, role, desc, weapon, weaponType, trait;
    public final int color1, color2;
    public final float hp, dmg, atkSpeed, speed, crit, armor, lifesteal, lunge;
    public final Skill[] skills;

    ClassDef(int id, String key, String name, String role, String desc, String weapon, String weaponType, String trait, int c1, int c2,
             float hp, float dmg, float atkSpeed, float speed, float crit, float armor, float lifesteal, float lunge, Skill... skills) {
        this.id = id; this.key = key; this.name = name; this.role = role; this.desc = desc; this.weapon = weapon; this.weaponType = weaponType;
        this.trait = trait; this.color1 = c1; this.color2 = c2; this.hp = hp; this.dmg = dmg; this.atkSpeed = atkSpeed; this.speed = speed;
        this.crit = crit; this.armor = armor; this.lifesteal = lifesteal; this.lunge = lunge; this.skills = skills;
    }

    private static Skill sk(String key, int n, String name, String desc, float cd) {
        return new Skill(name, desc, "s_" + key + "_" + n, n == 4 ? "ult_" + key : "sk_" + key + "_" + n, cd);
    }

    public static final ClassDef[] ALL = {
            new ClassDef(0, "paladin", "Paladín del Alba", "Tanque / Sostén",
                    "Guerrero sagrado de armadura pesada. Resiste, protege y castiga con luz solar.", "Espada del Alba y escudo", "sword",
                    "Égida: -12% de daño recibido.", 0xFFD25A, 0xFFF6C8, 120, 20, 0.95f, 1f, 0.05f, 0.12f, 0f, 45f,
                    sk("paladin", 1, "Lanza del Alba", "Tres lanzas de luz atraviesan a los enemigos.", 6),
                    sk("paladin", 2, "Alas de Égida", "Alas de luz te curan y absorben daño.", 14),
                    sk("paladin", 3, "Juicio del Alba", "Salto y golpe que levanta el suelo con una onda sagrada.", 10),
                    sk("paladin", 4, "Amanecer Eterno", "El sol desciende y purifica todo el campo.", 0)),
            new ClassDef(1, "shadow", "Asesino de las Sombras", "Movilidad / Daño explosivo",
                    "Maestro del sigilo. Se teletransporta, ataca por la espalda y ejecuta.", "Dagas gemelas", "dagger",
                    "Acechador: +50% de daño por la espalda.", 0xA040FF, 0x3A0A66, 85, 13, 1.35f, 1.08f, 0.20f, 0f, 0f, 55f,
                    sk("shadow", 1, "Paso Sombra", "Te teletransportas a la espalda del enemigo y lo apuñalas.", 5),
                    sk("shadow", 2, "Hoja Fantasma", "Cinco tajos fantasma consecutivos.", 8),
                    sk("shadow", 3, "Danza de Cuchillas", "Remolino de cuchillas a tu alrededor.", 11),
                    sk("shadow", 4, "Ejecución Dimensional", "El tiempo se detiene y cortas a todos a la vez.", 0)),
            new ClassDef(2, "flame", "Señor de las Llamas", "Daño de área / Quemaduras",
                    "Espadachín infernal. Inmune al fuego, arrasa con fuego y magma.", "Espadón llameante", "great",
                    "Brasas: 30% de quemar al golpear.", 0xFF5A1A, 0xFFC040, 95, 25, 0.80f, 1f, 0.05f, 0f, 0f, 38f,
                    sk("flame", 1, "Bola de Fuego", "Una bola de fuego que explota al impactar.", 5),
                    sk("flame", 2, "Muro de Fuego", "Pilares de fuego que queman a quien los cruce.", 10),
                    sk("flame", 3, "Tornado Ígneo", "Un tornado de fuego arrastra y quema a los enemigos.", 12),
                    sk("flame", 4, "Inferno Draconiano", "Un dragón de fuego recorre el campo y estalla.", 0)),
            new ClassDef(3, "storm", "Tempestad", "Velocidad / Rayos",
                    "Duelista del trueno. Veloz, encadena rayos y cae como una tormenta.", "Estoque eléctrico", "stab",
                    "Carga: +12% de velocidad, 15% de descarga.", 0x4DC8FF, 0xF0FCFF, 90, 16, 1.2f, 1.12f, 0.08f, 0f, 0f, 50f,
                    sk("storm", 1, "Relámpago Veloz", "Te conviertes en rayo y atraviesas a los enemigos.", 5),
                    sk("storm", 2, "Ráfaga Voltaica", "Un rayo encadenado salta entre hasta cinco enemigos.", 7),
                    sk("storm", 3, "Tormenta Eléctrica", "Una nube descarga rayos sobre tus enemigos.", 12),
                    sk("storm", 4, "Trueno Divino", "Tormenta gigante y un rayo colosal final.", 0)),
            new ClassDef(4, "frost", "Guardián Glacial", "Control de masas / Defensa",
                    "Caballero del hielo. Congela, ralentiza y destroza con cristales.", "Sable de cristal de hielo", "sword",
                    "Escarcha: 35% de ralentizar.", 0x80E4FF, 0xFFFFFF, 105, 19, 1f, 1f, 0.06f, 0.06f, 0f, 42f,
                    sk("frost", 1, "Esquirlas Glaciales", "Abanico de lanzas de hielo que ralentiza y congela.", 6),
                    sk("frost", 2, "Prisión de Hielo", "Encierra a un enemigo en hielo que luego estalla.", 9),
                    sk("frost", 3, "Ventisca", "Un torbellino de nieve cortante que arrastra y congela.", 12),
                    sk("frost", 4, "Cero Absoluto", "Todo se congela y luego se hace añicos.", 0)),
            new ClassDef(5, "verdant", "Guardián Esmeralda", "Soporte / Control",
                    "Guardián del bosque. Se cura, atrapa con raíces y hace brotar un árbol colosal.", "Espada viva de madera", "sword",
                    "Savia: 35% de envenenar y regeneración lenta.", 0x4FD96A, 0xC8FF9A, 100, 18, 1f, 1f, 0.06f, 0f, 0f, 42f,
                    sk("verdant", 1, "Látigo de Espinas", "Enredaderas espinosas avanzan, hieren y ralentizan.", 6),
                    sk("verdant", 2, "Floración", "Una floración te cura y regenera.", 14),
                    sk("verdant", 3, "Agarre de Raíces", "Raíces atrapan a los enemigos y los arrastran al centro.", 10),
                    sk("verdant", 4, "Árbol del Mundo", "Brota el Árbol del Mundo, inmoviliza a todos y estalla en luz curativa.", 0)),
            new ClassDef(6, "blood", "Segador Carmesí", "Robo de vida / Daño",
                    "Duelista sanguinario. Cada golpe lo cura; cuanto más pelea, más fuerte es.", "Guadaña de hoja roja", "scythe",
                    "Sangre: roba 7% del daño como vida.", 0xC4122C, 0xFF6A7C, 95, 21, 0.95f, 1f, 0.07f, 0f, 0.07f, 40f,
                    sk("blood", 1, "Tajo Sangriento", "Embestida y triple tajo que te cura por cada enemigo golpeado.", 5),
                    sk("blood", 2, "Pacto de Sangre", "Drena la vida de los enemigos cercanos con hilos de sangre.", 11),
                    sk("blood", 3, "Hoz Giratoria", "Una tormenta de hoces gira a tu alrededor desgarrándolo todo.", 11),
                    sk("blood", 4, "Eclipse Carmesí", "Una luna de sangre se alza y un tajo cruzado roba la vida de todos.", 0)),
            new ClassDef(7, "earth", "Coloso de Roca", "Tanque / Control",
                    "Titán de piedra. Golpes devastadores, piel de roca y terremotos.", "Martillo de roca", "hammer",
                    "Roca: -20% de daño recibido, golpes con gran empuje.", 0xC98B3C, 0xFFD27A, 140, 28, 0.70f, 0.9f, 0.04f, 0.20f, 0f, 30f,
                    sk("earth", 1, "Puño de Roca", "Un golpe brutal que levanta una columna de roca frente a ti.", 6),
                    sk("earth", 2, "Piel de Piedra", "Gran resistencia: te vuelves inamovible.", 14),
                    sk("earth", 3, "Terremoto", "Salto y estampida que parte el suelo en grietas.", 10),
                    sk("earth", 4, "Cataclismo del Titán", "Una lluvia de meteoritos arrasa el campo de batalla.", 0)),
            new ClassDef(8, "astral", "Vagabundo Estelar", "Magia cósmica / Movilidad",
                    "Espadachín hechicero de las estrellas. Disparos estelares, gravedad y saltos cósmicos.", "Espada-bastón estelar", "stab",
                    "Cosmos: +25% de carga de definitiva.", 0xFF4FD0, 0x8A6CFF, 90, 17, 1f, 1f, 0.08f, 0f, 0f, 38f,
                    sk("astral", 1, "Estrella Fugaz", "Un rayo de estrella atraviesa a todos los enemigos en línea.", 5),
                    sk("astral", 2, "Pozo Gravitatorio", "Un mini agujero negro arrastra y desgarra a los enemigos.", 12),
                    sk("astral", 3, "Paso Cósmico", "Te desvaneces en polvo de estrellas y reapareces a lo lejos.", 6),
                    sk("astral", 4, "Supernova", "Una estrella nace sobre el campo, lo arrastra todo y estalla.", 0)),
            new ClassDef(9, "steel", "Soberano de Acero", "Espadas voladoras / Daño",
                    "Maestro de las mil espadas. Lanza hojas, las hace girar y las llueve del cielo.", "Katana y hojas flotantes", "sword",
                    "Acero: cada 3er golpe lanza una hoja voladora.", 0xC9D4E8, 0xFF9A3C, 100, 20, 1.05f, 1f, 0.12f, 0f, 0f, 48f,
                    sk("steel", 1, "Volea de Hojas", "Tres espadas voladoras salen disparadas en abanico.", 5),
                    sk("steel", 2, "Guardia de Acero", "Un anillo de espadas gira a tu alrededor protegiéndote.", 12),
                    sk("steel", 3, "Carga Forjada", "Embestida de acero al rojo que arrastra a los enemigos.", 8),
                    sk("steel", 4, "Mil Espadas", "Un anillo de hojas se alza y una lluvia de mil espadas cae del cielo.", 0)),
    };
}
