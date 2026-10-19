package com.julianfarks.roguelike.core;

/**
 * GENERADO por tools/blessings/gen.py a partir de tools/blessings/cat_*.py: NO editar a mano.
 * Definiciones (datos) del catalogo de 200 bendiciones y sus sinergias; la logica que las ejecuta vive en BlessFx / BlessEffects.
 * Las 28 primeras (ids 0..27) conservan su logica original en Stats/Player/Level; aqui solo se clasifican.
 */
final class BlessData {
    private BlessData() {}

    /** Categorias: A dano fisico, B magia y elementos, C defensa, D velocidad, E proyectiles, F recursos, G invocaciones, H riesgo, I maldiciones, J hibridas. */
    static final String CATS = "ABCDEFGHIJ";
    /** Categoria y rareza (0 comun .. 4 legendaria) de las 28 bendiciones originales. */
    static final String LEG_CAT = "ACDACBBBBCDDAFFCBBAFJCECBADA";
    static final int[] LEG_RAR = {0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 2, 1, 1, 0, 0, 1, 0, 0, 1, 0, 2, 3, 1, 1, 1, 2, 2, 3};
    static final String[] CAT_ES = {"Daño físico", "Magia y elementos", "Defensa y supervivencia", "Velocidad y evasión", "Proyectiles", "Recursos y recompensas", "Invocaciones y compañeros", "Riesgo y recompensa", "Maldiciones y transformaciones", "Híbridas"};
    static final String[] LEG_KEY = {"filo", "corazon", "alas", "furia", "sangre", "brasas", "glacial", "chispa", "espinas", "piedra", "fantasma", "doble_salto", "critico", "alma", "fortuna", "escudo", "enfriamiento", "habilidad", "ejecutor", "iman", "venganza", "segunda", "onda", "egida", "sabio", "gigante", "sombra", "eclipse"};

    /** Nuevas bendiciones: clave, icono, nombre, descripcion, categoria, rareza, nivel maximo, peso, piso minimo, requisito, reglas separadas por ~. */
    static final String[][] NEW = {
        {"certero", "bx_certero", "Golpe Certero", "Cada 4 golpes seguidos, el siguiente hace +25% de daño por nivel.", "A", "0", "3", "10", "0", "", "STREAK||NEXTHIT:0.25,4|n=4 scale"},
        {"hoja_rapida", "bx_hoja_rapida", "Hoja Rápida", "+7% de velocidad de ataque por nivel.", "A", "0", "3", "10", "0", "", "MOD||ATKSPD:0.07|scale"},
        {"peso_pesado", "bx_peso_pesado", "Peso Pesado", "+18% de daño por nivel a enemigos con más del 80% de vida.", "A", "0", "2", "10", "0", "", "MOD|v:high|DMG:0.18|scale"},
        {"rompeguardias", "bx_rompeguardias", "Rompeguardias", "+22% de daño por nivel contra mini-jefes y jefes.", "A", "1", "2", "8", "0", "", "MOD|v:elite|DMG:0.22|scale"},
        {"punalada", "bx_punalada", "Puñalada Trapera", "Golpear a un enemigo por la espalda: +35% de daño.", "A", "1", "1", "8", "0", "", "MOD|v:back|DMG:0.35"},
        {"enjambre", "bx_enjambre", "Cazador de Enjambres", "+15% de daño por nivel a enemigos con otros dos cerca.", "A", "0", "2", "10", "0", "", "MOD|v:crowd|DMG:0.15|scale"},
        {"alcance", "bx_alcance", "Estocada Larga", "+18% de alcance de arma por nivel.", "A", "0", "2", "10", "0", "", "MOD||REACH:0.18|scale"},
        {"sangria", "bx_sangria", "Filo Sangrante", "25% de causar sangrado. Los enemigos sangrando reciben +15% de daño de tus golpes.", "A", "1", "1", "8", "0", "", "HIT|!v:bleed|STATUS:bleed,4,1.2|ch=0.25~MOD|v:bleed|DMG:0.15|src=W"},
        {"doble_tajo", "bx_doble_tajo", "Doble Tajo", "18% de que tu golpe se repita poco después con el 40% del daño.", "A", "3", "1", "4", "1", "", "HIT||REPEAT:0.4|ch=0.18 icd=0.35"},
        {"impulso_letal", "bx_impulso_letal", "Impulso Letal", "Cada crítico da +7% de daño durante 4 s (hasta 5 cargas).", "A", "3", "1", "4", "1", "", "CRIT||BUFF:dmg,0.07,4,5"},
        {"pulso_constante", "bx_pulso_constante", "Pulso Constante", "Los golpes no críticos hacen +14% de daño por nivel.", "A", "0", "2", "10", "0", "", "MOD||NONCRIT:0.14|scale"},
        {"remate_brutal", "bx_remate_brutal", "Remate Brutal", "El tercer golpe del combo hace +25% de daño por nivel.", "A", "0", "2", "10", "0", "", "MOD||FINISHMUL:0.25|scale"},
        {"combo_ritmo", "bx_combo_ritmo", "Ritmo de Combate", "Cada remate de combo da +10% de velocidad de ataque durante 3 s (hasta 3 cargas).", "A", "2", "1", "6", "0", "", "FINISH||BUFF:atk,0.10,3,3"},
        {"sentencia", "bx_sentencia", "Sentencia", "Tu remate detona una explosión de 200% de daño cada 4 s.", "A", "4", "1", "2", "1", "cat:A:3", "FINISH||EXPLODE:72,2.0|icd=4"},
        {"maestro_armas", "bx_maestro_armas", "Maestro de Armas", "Con la vida al 90% o más: +30% de daño de arma.", "A", "2", "1", "6", "0", "", "MOD|p:high|DMG:0.30|src=W"},
        {"sed_batalla", "bx_sed_batalla", "Sed de Batalla", "Cada baja da +12% de velocidad de ataque durante 3 s (hasta 2 cargas).", "A", "0", "1", "10", "0", "", "KILL||BUFF:atk,0.12,3,2"},
        {"ojo_halcon", "bx_ojo_halcon", "Ojo de Halcón", "+5% de probabilidad de crítico por nivel.", "A", "0", "3", "10", "0", "", "MOD||CRIT:0.05|scale"},
        {"ensanamiento", "bx_ensanamiento", "Ensañamiento", "Los críticos contra enemigos con menos del 30% de vida hacen +50% de daño crítico extra.", "A", "2", "1", "6", "0", "", "MOD|v:low|CRITMUL:0.5"},
        {"cadena_criticos", "bx_cadena_criticos", "Cadena de Críticos", "Tras 2 críticos seguidos, +20% de probabilidad de crítico hasta que falles un golpe o te hieran.", "A", "3", "1", "4", "1", "", "MOD|p:crits>=2|CRIT:0.20"},
        {"combustion", "bx_combustion", "Combustión", "El daño periódico (fuego, veneno, sangrado) hace +20% por nivel.", "B", "0", "2", "10", "0", "", "MOD||DOT:0.2|scale"},
        {"llama_voraz", "bx_llama_voraz", "Llama Voraz", "Los enemigos en llamas reciben +15% de daño de tus golpes y habilidades.", "B", "0", "1", "10", "0", "", "MOD|v:burn|DMG:0.15"},
        {"brasa_critica", "bx_brasa_critica", "Brasa Crítica", "+25% de probabilidad de crítico contra enemigos en llamas.", "B", "2", "1", "6", "0", "", "MOD|v:burn|CRIT:0.25"},
        {"contagio_igneo", "bx_contagio_igneo", "Contagio Ígneo", "Cuando muere un enemigo en llamas, el fuego salta a los cercanos.", "B", "1", "1", "8", "0", "", "KILL|v:burn|SPREAD:burn,85"},
        {"pira", "bx_pira", "Pira Viviente", "Los enemigos en llamas explotan al morir (60% de daño) y prenden fuego alrededor.", "B", "3", "1", "4", "1", "", "KILL|v:burn|EXPLODE:52,0.6,burn,3|icd=0.15"},
        {"aliento_dragon", "bx_aliento_dragon", "Aliento de Dragón", "Tu definitiva prende fuego a todos los enemigos durante 4 s.", "B", "3", "1", "4", "1", "", "ULT||STATUS:burn,4,1.5|aoe=9999"},
        {"rastro_ardiente", "bx_rastro_ardiente", "Rastro Ardiente", "Al rodar dejas dos charcos de fuego que queman a los enemigos.", "B", "0", "1", "10", "0", "", "ROLL||TRAIL:fire,2.5,1.2~ROLLEND||TRAIL:fire,2.5,1.2"},
        {"escarcha_quebradiza", "bx_escarcha_quebradiza", "Escarcha Quebradiza", "+35% de probabilidad de crítico contra enemigos ralentizados o congelados.", "B", "2", "1", "6", "0", "", "MOD|v:slow|CRIT:0.35"},
        {"esquirlas_hielo", "bx_esquirlas_hielo", "Esquirlas de Hielo", "Los enemigos ralentizados o congelados sueltan 3 esquirlas al morir.", "B", "1", "1", "8", "0", "", "KILL|v:slow|PROJ:shard,3,0.45,slow|icd=0.2"},
        {"aura_gelida", "bx_aura_gelida", "Aura Gélida", "Cada 3 s ralentizas a los enemigos cercanos.", "B", "0", "1", "10", "0", "", "TICK|r:combat|STATUS:slow,2,1|aoe=80 every=3"},
        {"ventisca", "bx_ventisca", "Ventisca", "Tus habilidades ralentizan a los enemigos en un radio amplio.", "B", "1", "1", "8", "0", "", "SKILL||STATUS:slow,3,1|aoe=140"},
        {"congelacion_profunda", "bx_congelacion_profunda", "Congelación Profunda", "Golpear a un enemigo ralentizado: 12% de congelarlo 1,2 s (cada 2 s). Los jefes solo se ralentizan.", "B", "3", "1", "4", "1", "", "HIT|v:slow,!v:freeze|STATUS:freeze,1.2,1|ch=0.12 icd=2"},
        {"carga_estatica", "bx_carga_estatica", "Carga Estática", "Tus golpes acumulan carga arcana (máx. 10). Al llegar a 10 se libera un rayo encadenado.", "B", "0", "1", "10", "0", "", "HIT||ARC:1|icd=0.1~HIT|p:arc>=10|DISCHARGE:2,0.3|icd=1"},
        {"pararrayos", "bx_pararrayos", "Pararrayos", "Cada parry da 2 cargas arcanas y libera una descarga con todas tus cargas.", "B", "3", "1", "4", "1", "", "PARRY||ARC:2~PARRY|p:arc>=1|DISCHARGE:3,0.4"},
        {"voltio_arcano", "bx_voltio_arcano", "Voltio Arcano", "Cada habilidad que lanzas te da 3 cargas arcanas.", "B", "0", "1", "10", "0", "", "SKILL||ARC:3"},
        {"bateria", "bx_bateria", "Batería Viva", "Cada esquiva o rodar exitoso da 2 cargas arcanas.", "B", "2", "1", "6", "0", "", "ROLL||ARC:2|icd=0.4~DODGE||ARC:2|icd=0.4"},
        {"descarga_mayor", "bx_descarga_mayor", "Descarga Mayor", "Con 6 o más cargas arcanas, tus golpes sueltan una descarga de 4 saltos (cada 1,5 s).", "B", "3", "1", "4", "1", "", "HIT|p:arc>=6|DISCHARGE:4,0.35|icd=1.5"},
        {"conductor", "bx_conductor", "Conductor", "Tus rayos encadenados saltan a 1 enemigo más.", "B", "0", "1", "10", "0", "", "MOD||CHAINJUMPS:1"},
        {"tempestad_eterna", "bx_tempestad_eterna", "Tempestad Eterna", "En combate, cada 4 s caen 3 rayos sobre enemigos al azar.", "B", "4", "1", "2", "2", "has:2:59,60,61,62,63,64,7", "TICK|r:combat|STRIKE:3,1.1|every=4"},
        {"ponzona_virulenta", "bx_ponzona_virulenta", "Ponzoña Virulenta", "Tus estados alterados duran 40% más.", "B", "0", "1", "10", "0", "", "MOD||STATUSDUR:0.4"},
        {"plaga", "bx_plaga", "Plaga", "Cuando muere un enemigo envenenado, el veneno se contagia a los cercanos.", "B", "3", "1", "4", "1", "", "KILL|v:poison|SPREAD:poison,95"},
        {"toxina_nerviosa", "bx_toxina_nerviosa", "Toxina Nerviosa", "40% de ralentizar al golpear a un enemigo envenenado.", "B", "1", "1", "8", "0", "", "HIT|v:poison|STATUS:slow,2,1|ch=0.4"},
        {"esporas", "bx_esporas", "Esporas Tóxicas", "En combate, cada 6 s una nube envenena a los enemigos cercanos.", "B", "0", "1", "10", "0", "", "TICK|r:combat|STATUS:poison,4,1|aoe=100 every=6"},
        {"eco_arcano", "bx_eco_arcano", "Eco Arcano", "Tras lanzar una habilidad, tu siguiente golpe hace +50% de daño (5 s).", "B", "2", "1", "6", "0", "", "SKILL||NEXTHIT:0.5,5"},
        {"canalizador", "bx_canalizador", "Canalizador", "Cada golpe acorta 0,25 s la reutilización de tu habilidad más lenta (límite por segundo).", "B", "1", "1", "8", "0", "", "HIT|!p:cdall|CDR:0.25,1|icd=0.3"},
        {"catalizador", "bx_catalizador", "Catalizador", "Al usar tu definitiva, tus habilidades se reponen al instante.", "B", "3", "1", "4", "1", "", "ULT||COOLDOWNALL"},
        {"resonancia", "bx_resonancia", "Resonancia", "Cada habilidad potencia la siguiente: +35% de daño (6 s).", "B", "1", "1", "8", "0", "", "SKILL||NEXTSKILL:0.35,6"},
        {"manantial", "bx_manantial", "Manantial de Maná", "Cada habilidad lanzada carga un 6% de tu definitiva.", "B", "0", "1", "10", "0", "", "SKILL||ULT:6"},
        {"runa_poder", "bx_runa_poder", "Runa de Poder", "+25% de carga de definitiva y +10% de daño de habilidades.", "B", "2", "1", "6", "0", "", "MOD||ULTGAIN:0.25~MOD||SKILLDMG:0.10"},
        {"contra_parry", "bx_contra_parry", "Contra del Parry", "Tras un parry, tu siguiente golpe hace +60% de daño (4 s).", "C", "1", "1", "8", "0", "", "PARRY||NEXTHIT:0.6,4"},
        {"parry_escudo", "bx_parry_escudo", "Parry Templado", "Cada parry te da un escudo de 15.", "C", "0", "1", "10", "0", "", "PARRY||SHIELD:15"},
        {"parry_ulti", "bx_parry_ulti", "Parry Cargado", "Cada parry carga un 8% de tu definitiva.", "C", "0", "1", "10", "0", "", "PARRY||ULT:8"},
        {"eco_defensivo", "bx_eco_defensivo", "Eco Defensivo", "Cada parry libera una onda de 100% de daño que empuja a los enemigos.", "C", "2", "1", "6", "0", "", "PARRY||EXPLODE:72,1.0|aoe=-1 icd=0.5"},
        {"parry_maestro", "bx_parry_maestro", "Maestro del Parry", "Cada parry da +12% de daño durante 5 s (hasta 3 cargas).", "C", "3", "1", "4", "1", "", "PARRY||BUFF:dmg,0.12,5,3"},
        {"reflejo", "bx_reflejo", "Reflejo Estelar", "Cada parry dispara un anillo de 8 estrellas (50% de daño).", "C", "3", "1", "4", "1", "", "PARRY||PROJ:ring,8,0.5|icd=0.8"},
        {"parry_calma", "bx_parry_calma", "Calma del Guardián", "Cada parry cura el 3% de tu vida máxima (límite por sala).", "C", "1", "1", "8", "0", "", "PARRY||HEAL:0.03"},
        {"escudo_reactivo", "bx_escudo_reactivo", "Escudo Reactivo", "Cuando tu escudo absorbe un golpe, estalla con 80% de daño a tu alrededor.", "C", "1", "1", "8", "0", "", "BLOCKED||EXPLODE:62,0.8|aoe=-1 icd=1"},
        {"bastion_limpio", "bx_bastion_limpio", "Bastión de Victoria", "Al limpiar una sala ganas un escudo de 20.", "C", "0", "1", "10", "0", "", "CLEAR||SHIELD:20"},
        {"armadura_hierro", "bx_armadura_hierro", "Armadura de Hierro", "Tus golpes dan 3 de escudo (cada 1,2 s) y tu escudo puede acumular 30 más.", "C", "2", "1", "6", "0", "", "HIT||SHIELD:3|icd=1.2~MOD||SHIELDCAP:30"},
        {"coraza_espinas", "bx_coraza_espinas", "Coraza de Espinas", "Al recibir daño estallas dañando (70%) a los enemigos cercanos (cada 1,5 s).", "C", "3", "1", "4", "1", "", "HURT||EXPLODE:60,0.7|aoe=-1 icd=1.5"},
        {"contragolpe", "bx_contragolpe", "Contragolpe Desesperado", "Al recibir daño, tu siguiente golpe hace +70% de daño (4 s).", "C", "2", "1", "6", "0", "", "HURT||NEXTHIT:0.7,4"},
        {"sangre_fria", "bx_sangre_fria", "Sangre Fría", "Al caer por debajo del 35% de vida ganas un escudo de 40 (cada 20 s).", "C", "1", "1", "8", "0", "", "LOWHP||SHIELD:40|icd=20"},
        {"supervivencia", "bx_supervivencia", "Instinto de Supervivencia", "Al caer por debajo del 35% de vida: 0,6 s de invulnerabilidad y cura del 8% (cada 25 s).", "C", "2", "1", "6", "0", "", "LOWHP||INVULN:0.6|icd=25~LOWHP||HEAL:0.08|icd=25"},
        {"ultimo_bastion", "bx_ultimo_bastion", "Último Bastión", "Con menos del 35% de vida recibes un 30% menos de daño.", "C", "3", "1", "4", "1", "", "MOD|p:low|TAKEN:-0.30"},
        {"rabia_herida", "bx_rabia_herida", "Rabia Herida", "Con menos del 35% de vida haces +35% de daño.", "C", "2", "1", "6", "0", "", "MOD|p:low|DMG:0.35"},
        {"sanguinario", "bx_sanguinario", "Sanguinario", "Con menos del 35% de vida robas un 5% del daño que infliges.", "C", "2", "1", "6", "0", "", "MOD|p:low|LIFESTEAL:0.05"},
        {"vitalidad", "bx_vitalidad", "Vitalidad", "+10% de vida máxima por nivel.", "C", "0", "3", "10", "0", "", "MOD||MAXHP:0.1|scale"},
        {"sanacion_sala", "bx_sanacion_sala", "Sanación de Victoria", "Al limpiar una sala recuperas el 5% de tu vida máxima.", "C", "0", "1", "10", "0", "", "CLEAR||HEAL:0.05"},
        {"cosecha_vida", "bx_cosecha_vida", "Cosecha de Vida", "Cada baja cura el 1,5% de tu vida máxima (límite por sala).", "C", "0", "1", "10", "0", "", "KILL||HEAL:0.015|icd=0.3"},
        {"egida_perpetua", "bx_egida_perpetua", "Égida Perpetua", "En combate ganas un escudo de 30 cada 8 s. Si el escudo absorbe un golpe, 0,5 s de invulnerabilidad (cada 3 s).", "C", "4", "1", "2", "2", "cat:C:3", "TICK|r:combat|SHIELD:30|every=8~BLOCKED||INVULN:0.5|icd=3"},
        {"onda_choque", "bx_onda_choque", "Onda de Choque", "Al recibir un golpe empujas a los enemigos cercanos (cada 1,2 s).", "C", "1", "1", "8", "0", "", "HURT||PUSH:80,170|icd=1.2"},
        {"impulso_rodar", "bx_impulso_rodar", "Impulso de Rodada", "Tu rodada es un 25% más rápida por nivel: recorre más distancia y termina antes.", "D", "0", "2", "10", "0", "", "MOD||ROLLCDR:0.25|scale"},
        {"sombra_veloz", "bx_sombra_veloz", "Sombra Veloz", "Tras rodar ganas +20% de velocidad de movimiento durante 2,5 s.", "D", "0", "1", "10", "0", "", "ROLLEND||BUFF:spd,0.2,2.5,1"},
        {"racha_cazador", "bx_racha_cazador", "Racha del Cazador", "Cada baja da +10% de velocidad de movimiento durante 4 s (hasta 3 cargas).", "D", "0", "1", "10", "0", "", "KILL||BUFF:spd,0.10,4,3"},
        {"esquiva_sagrada", "bx_esquiva_sagrada", "Esquiva Sagrada", "Cada esquiva da +15% de daño durante 4 s (hasta 2 cargas).", "D", "2", "1", "6", "0", "", "DODGE||BUFF:dmg,0.15,4,2"},
        {"danza_cuchillas", "bx_danza_cuchillas", "Baile de Cuchillas", "Cada esquiva lanza 3 cuchillas (60% de daño).", "D", "2", "1", "6", "0", "", "DODGE||PROJ:blade,3,0.6|icd=0.6"},
        {"evasion_magica", "bx_evasion_magica", "Evasión Mágica", "Cada esquiva reduce 0,6 s tus habilidades y carga un 5% de tu definitiva.", "D", "2", "1", "6", "0", "", "DODGE||CDR:0.6~DODGE||ULT:5"},
        {"salto_explosivo", "bx_salto_explosivo", "Salto Explosivo", "Cada salto en el aire detona una explosión del 50% de daño bajo ti.", "D", "1", "1", "8", "0", "", "AIRJUMP||EXPLODE:54,0.5|aoe=-1 icd=0.6"},
        {"aterrizaje_sismico", "bx_aterrizaje_sismico", "Aterrizaje Sísmico", "Las caídas largas provocan una onda del 100% de daño al aterrizar.", "D", "1", "1", "8", "0", "", "LAND||EXPLODE:76,1.0|aoe=-1 icd=0.8"},
        {"cadencia", "bx_cadencia", "Cadencia en Movimiento", "Mientras te mueves, +18% de velocidad de ataque.", "D", "2", "1", "6", "0", "", "MOD|p:moving|ATKSPD:0.18"},
        {"golpe_corriendo", "bx_golpe_corriendo", "Golpe en Carrera", "Mientras te mueves, +12% de daño.", "D", "0", "1", "10", "0", "", "MOD|p:moving|DMG:0.12"},
        {"quieto_letal", "bx_quieto_letal", "Quietud Letal", "Quieto, haces +20% de daño y recibes un 10% menos.", "D", "1", "1", "8", "0", "", "MOD|p:still|DMG:0.20~MOD|p:still|TAKEN:-0.10"},
        {"rafaga_remate", "bx_rafaga_remate", "Ráfaga de Remate", "Cada remate de combo da +15% de velocidad de movimiento durante 3 s.", "D", "1", "1", "8", "0", "", "FINISH||BUFF:spd,0.15,3,1"},
        {"viento_cola", "bx_viento_cola", "Viento de Cola", "Cada salto en el aire da +20% de velocidad de movimiento durante 3 s.", "D", "2", "1", "6", "0", "", "AIRJUMP||BUFF:spd,0.2,3,1"},
        {"segundo_aliento", "bx_segundo_aliento", "Segundo Aliento", "Cada esquiva te da 0,4 s de invulnerabilidad (cada 3 s).", "D", "2", "1", "6", "0", "", "DODGE||INVULN:0.4|icd=3"},
        {"reloj_destino", "bx_reloj_destino", "Reloj del Destino", "Un parry o una esquiva ralentiza el tiempo 1,2 s para los enemigos (cada 18 s).", "D", "4", "1", "2", "1", "cat:D:3", "DODGE||TIMESLOW:1.2,0.45|icd=18~PARRY||TIMESLOW:1.2,0.45|icd=18"},
        {"maestro_trampas", "bx_maestro_trampas", "Maestro de Trampas", "Sobrevolar pinchos sin tocarlos te da 15 de escudo y +20% de daño durante 5 s.", "D", "2", "1", "6", "0", "", "HAZARD||SHIELD:15~HAZARD||BUFF:dmg,0.2,5,1"},
        {"acrobata", "bx_acrobata", "Acróbata", "Cada salto da +10% de velocidad de ataque durante 2 s.", "D", "0", "1", "10", "0", "", "JUMP||BUFF:atk,0.10,2,1"},
        {"danza_aerea", "bx_danza_aerea", "Danza Aérea", "En el aire haces +20% de daño.", "D", "2", "1", "6", "0", "", "MOD|p:air|DMG:0.20"},
        {"punta_afilada", "bx_punta_afilada", "Punta Afilada", "Tus proyectiles atraviesan 1 enemigo más por nivel.", "E", "0", "2", "10", "0", "", "MOD||PIERCE:1|scale"},
        {"vuelo_veloz", "bx_vuelo_veloz", "Vuelo Veloz", "Tus proyectiles van un 25% más rápido y son un 20% más grandes.", "E", "0", "1", "10", "0", "", "MOD||PROJSPEED:0.25~MOD||PROJSIZE:0.20"},
        {"ricochet", "bx_ricochet", "Ricochet", "Tus proyectiles rebotan una vez contra paredes o enemigos.", "E", "1", "1", "8", "1", "", "MOD||BOUNCE:1"},
        {"buscador", "bx_buscador", "Buscador", "Tus proyectiles giran ligeramente hacia los enemigos cercanos.", "E", "0", "1", "10", "0", "", "MOD||HOMING:1"},
        {"perforante", "bx_perforante", "Perforante", "Tus proyectiles hacen +20% de daño por cada enemigo que atraviesan.", "E", "2", "1", "6", "0", "", "MOD||PIERCEDMG:0.20~MOD||PIERCE:1"},
        {"doble_lanzamiento", "bx_doble_lanzamiento", "Doble Lanzamiento", "20% de que tus proyectiles se lancen dos veces.", "E", "2", "1", "6", "1", "", "MOD||PROJDOUBLE:0.2"},
        {"onda_expansiva", "bx_onda_expansiva", "Onda Expansiva", "Tus ondas de energía (Hoja Fantasma y similares) hacen +40% de daño y son más grandes.", "E", "2", "1", "6", "0", "", "MOD||WAVEDMG:0.4"},
        {"proyectil_explosivo", "bx_proyectil_explosivo", "Proyectil Explosivo", "Tus proyectiles explotan al terminar su trayecto (50% de daño).", "E", "3", "1", "4", "1", "", "PROJEND||EXPLODE:46,0.5|icd=0.15"},
        {"disparo_incendiario", "bx_disparo_incendiario", "Disparo Incendiario", "30% de que tus proyectiles prendan fuego al impactar.", "E", "1", "1", "8", "0", "", "PROJ||STATUS:burn,3,1|ch=0.3"},
        {"disparo_gelido", "bx_disparo_gelido", "Disparo Gélido", "50% de que tus proyectiles ralenticen al impactar.", "E", "0", "1", "10", "0", "", "PROJ||STATUS:slow,2.5,1|ch=0.5"},
        {"disparo_voltaico", "bx_disparo_voltaico", "Disparo Voltaico", "Tus proyectiles descargan un rayo de 2 saltos al impactar (cada 0,5 s).", "E", "1", "1", "8", "0", "", "PROJ||CHAIN:2,0.4|icd=0.5"},
        {"lluvia_hojas", "bx_lluvia_hojas", "Lluvia de Hojas", "Cada habilidad invoca una lluvia de 5 hojas cortantes sobre los enemigos.", "E", "2", "1", "6", "0", "", "SKILL||PROJ:rain,5,0.5"},
        {"rafaga_estelar", "bx_rafaga_estelar", "Ráfaga Estelar", "Cada 5 golpes sueltas 3 estrellas teledirigidas (50% de daño).", "E", "2", "1", "6", "0", "", "STREAK||PROJ:star,3,0.5|n=5"},
        {"estela_mortal", "bx_estela_mortal", "Estela de Rodada", "Al terminar un rodar lanzas una onda de energía (80% de daño).", "E", "2", "1", "6", "0", "", "ROLLEND||PROJ:wave,1,0.8"},
        {"francotirador", "bx_francotirador", "Tirador Experto", "Los proyectiles que impactan a enemigos lejanos hacen +40% de daño.", "E", "1", "1", "8", "0", "", "MOD|v:far|PROJDMG:0.4"},
        {"foco_letal", "bx_foco_letal", "Foco Letal", "Impactos seguidos con proyectiles al mismo enemigo: +8% de daño acumulable (hasta 5).", "E", "3", "1", "4", "1", "", "MOD||FOCUS:0.08"},
        {"orbe_santo", "bx_orbe_santo", "Orbe Santo", "Matar con un proyectil libera un orbe sagrado teledirigido (70% de daño).", "E", "2", "1", "6", "0", "", "KILL|s:P|PROJ:holy,1,0.7|icd=0.3"},
        {"tormenta_acero", "bx_tormenta_acero", "Tormenta de Acero", "Cada habilidad lanza 10 cuchillas desde el cielo y tu definitiva 16. Tus proyectiles atraviesan 1 enemigo más.", "E", "4", "1", "2", "1", "cat:E:3", "SKILL||PROJ:rain,10,0.45~ULT||PROJ:rain,16,0.6~MOD||PIERCE:1"},
        {"mercader_astuto", "bx_mercader_astuto", "Mercader Astuto", "Los precios de las tiendas bajan un 10% por nivel (máx. 50%).", "F", "0", "2", "10", "0", "", "MOD||SHOPDISC:0.10|scale"},
        {"interes", "bx_interes", "Interés Compuesto", "Al limpiar una sala con 100 o más de oro, ganas 12 de oro extra.", "F", "2", "1", "6", "0", "", "CLEAR|p:gold>=100|GOLD:12"},
        {"oro_poder", "bx_oro_poder", "Poder del Oro", "Con 150 o más de oro, haces +12% de daño.", "F", "2", "1", "6", "0", "", "MOD|p:gold>=150|DMG:0.12"},
        {"cosecha_almas", "bx_cosecha_almas", "Cosecha de Almas", "Los mini-jefes y jefes sueltan 6 almas extra al morir.", "F", "1", "1", "8", "0", "", "KILL|v:elite|SOULS:6"},
        {"almas_poder", "bx_almas_poder", "Almas en Furia", "Cada alma recogida da +5% de daño durante 6 s (hasta 5 cargas).", "F", "3", "1", "4", "1", "", "PICK|-|BUFF:dmg,0.05,6,5|what=soul"},
        {"corazon_escudo", "bx_corazon_escudo", "Corazón Blindado", "Un corazón recogido con la vida llena te da 12 de escudo.", "F", "1", "1", "8", "0", "", "OVERFLOW|-|SHIELD:12|what=heart"},
        {"alquimista", "bx_alquimista", "Alquimista", "Beber un frasco te da +20% de daño durante 8 s y limpia tus estados alterados.", "F", "1", "1", "8", "0", "", "POTION||BUFF:dmg,0.2,8,1~POTION||CLEANSE"},
        {"reserva_pociones", "bx_reserva_pociones", "Reserva de Frascos", "+1 frasco de curación máximo.", "F", "0", "1", "10", "0", "", "MOD||POTMAX:1"},
        {"brebaje_extra", "bx_brebaje_extra", "Brebaje Rebosante", "Un frasco recogido con la reserva llena cura el 12% de tu vida.", "F", "1", "1", "8", "0", "", "OVERFLOW|-|HEAL:0.12|what=potion"},
        {"vision_altar", "bx_vision_altar", "Visión del Altar", "Los altares de bendición ofrecen una opción adicional.", "F", "3", "1", "4", "1", "", "MOD||OFFER:1"},
        {"suerte_dorada", "bx_suerte_dorada", "Suerte Dorada", "+1 de suerte: mejores recompensas en cofres y tiendas.", "F", "0", "1", "10", "0", "", "MOD||LUCK:1"},
        {"botin_elites", "bx_botin_elites", "Botín de Élite", "Los mini-jefes y jefes sueltan 15 de oro extra.", "F", "0", "1", "10", "0", "", "KILL|v:elite|GOLD:15"},
        {"recaudador", "bx_recaudador", "Recaudador", "Cada baja con tu arma te da 1 de oro (límite por sala).", "F", "0", "1", "10", "0", "", "KILL|s:W|GOLD:1"},
        {"cazatesoros", "bx_cazatesoros", "Cazatesoros", "Al entrar en una sala ganas 8 de oro.", "F", "0", "1", "10", "0", "", "ROOM||GOLD:8"},
        {"ladron_almas", "bx_ladron_almas", "Ladrón de Almas", "Los críticos te dan 2 almas (cada 0,8 s, límite por sala).", "F", "1", "1", "8", "0", "", "CRIT||SOULS:2|icd=0.8"},
        {"corona_avaro", "bx_corona_avaro", "Corona del Avaro", "+50% de oro. Con 200 o más de oro haces +20% de daño y cada baja te da 2 de oro (límite por sala).", "F", "4", "1", "2", "1", "cat:F:3", "MOD||GOLDMUL:0.5~MOD|p:gold>=200|DMG:0.2~KILL|p:gold>=200|GOLD:2"},
        {"luciernaga", "bx_luciernaga", "Luciérnaga", "Una luciérnaga te acompaña y dispara a los enemigos cercanos (50% de daño cada 2 s).", "G", "0", "1", "10", "0", "", "SPIRIT||WISP:2,0.5"},
        {"llama_fatua", "bx_llama_fatua", "Llama Fatua", "Un espíritu de fuego te acompaña: dispara cada 2,6 s (55%) y prende fuego.", "G", "1", "1", "8", "0", "", "SPIRIT||WISP:2.6,0.55,burn"},
        {"espiritu_hielo", "bx_espiritu_hielo", "Espíritu Glacial", "Un espíritu de hielo libera cada 5 s una onda helada que ralentiza (70% de daño).", "G", "1", "1", "8", "0", "", "SPIRIT||NOVA:5,0.7,0,70"},
        {"espiritu_rayo", "bx_espiritu_rayo", "Espíritu del Trueno", "Un espíritu eléctrico lanza cada 4 s un rayo de 3 saltos (60% de daño).", "G", "3", "1", "4", "1", "", "SPIRIT||SCHAIN:4,0.6,3"},
        {"espiritu_maldicion", "bx_espiritu_maldicion", "Espíritu Maldito", "Un espíritu oscuro maldice cada 8 s al enemigo más sano (+20% de daño recibido).", "G", "2", "1", "6", "0", "", "SPIRIT||SMARK:8"},
        {"espiritu_curativo", "bx_espiritu_curativo", "Espíritu Sanador", "Un espíritu te cura el 4% de tu vida cada 9 s si estás herido (límite por sala).", "G", "1", "1", "8", "0", "", "SPIRIT||SHEAL:9,0.04"},
        {"espiritu_guardian", "bx_espiritu_guardian", "Espíritu Guardián", "Un espíritu te protege con un escudo de 18 cada 14 s si no tienes ninguno.", "G", "2", "1", "6", "0", "", "SPIRIT||SGUARD:14,18"},
        {"espiritu_veneno", "bx_espiritu_veneno", "Espíritu Venenoso", "Un espíritu de veneno dispara cada 3 s (45%) y envenena.", "G", "1", "1", "8", "0", "", "SPIRIT||WISP:3,0.45,poison"},
        {"espiritu_sombra", "bx_espiritu_sombra", "Espíritu de Sombra", "Un espíritu de sombra hiere cada 2,8 s (60%) y causa sangrado.", "G", "2", "1", "6", "0", "", "SPIRIT||WISP:2.8,0.6,bleed"},
        {"vinculo_espiritual", "bx_vinculo_espiritual", "Vínculo Espiritual", "Un espíritu menor te acompaña (35% cada 3 s) y todos tus espíritus actúan un 30% más rápido.", "G", "1", "1", "8", "0", "", "SPIRIT||WISP:3,0.35~MOD|p:spirit|SPIRITRATE:0.3"},
        {"sinfonia_espiritual", "bx_sinfonia_espiritual", "Sinfonía Espiritual", "Tus espíritus actúan un 50% más rápido y cada baja los acelera aún más durante 4 s.", "G", "3", "1", "4", "1", "", "MOD|p:spirit|SPIRITRATE:0.5~KILL|p:spirit|BURSTUP:4"},
        {"pastor_almas", "bx_pastor_almas", "Pastor de Almas", "Cada alma recogida acelera a tus espíritus durante 5 s.", "G", "2", "1", "6", "0", "", "PICK|p:spirit|BURSTUP:5|what=soul"},
        {"legion_espectral", "bx_legion_espectral", "Legión Espectral", "Invoca tres espíritus: uno de fuego, uno glacial y uno eléctrico.", "G", "4", "1", "2", "1", "cat:G:3", "SPIRIT||WISP:2.4,0.5,burn~SPIRIT||NOVA:6,0.7,0,70~SPIRIT||SCHAIN:4.5,0.55,3"},
        {"desafio_doble", "bx_desafio_doble", "Desafío Doble", "Los enemigos tienen +15% de vida, pero ganas +35% de oro y +20% de almas.", "H", "1", "1", "8", "0", "", "MOD||ENEMYHP:0.15~MOD||GOLDMUL:0.35~MOD||SOULMUL:0.20"},
        {"sed_riesgo", "bx_sed_riesgo", "Sed de Riesgo", "Los enemigos te hacen +20% de daño, pero haces +25% de daño y +30% de daño crítico.", "H", "2", "1", "6", "0", "", "MOD||ENEMYDMG:0.20~MOD||DMG:0.25~MOD||CRITMUL:0.3"},
        {"vidrio_filo", "bx_vidrio_filo", "Cañón de Cristal", "-25% de vida máxima, +25% de daño.", "H", "1", "1", "8", "0", "", "MOD||MAXHP:-0.25~MOD||DMG:0.25"},
        {"pacto_sangre", "bx_pacto_sangre", "Pacto de Sangre", "Al entrar en cada sala pierdes el 8% de tu vida (nunca mueres por esto), pero haces +30% de daño.", "H", "3", "1", "4", "1", "", "ROOM||LOSEHP:0.08~ROOM||BUFF:dmg,0.30,900,1"},
        {"todo_o_nada", "bx_todo_o_nada", "Todo o Nada", "Las salas perfectas (sin daño) dan 25 de oro y curan el 12%. Cada golpe recibido te cuesta 5 de oro.", "H", "3", "1", "4", "1", "", "PERFECT||GOLD:25~PERFECT||HEAL:0.12~HURT||LOSEGOLD:5|icd=2"},
        {"temerario", "bx_temerario", "Temerario", "Mientras no te hayan herido en la sala, haces +20% de daño.", "H", "2", "1", "6", "0", "", "MOD|p:noroomhit|DMG:0.20"},
        {"sacrificio", "bx_sacrificio", "Sacrificio", "Beber un frasco te cuesta el 5% de tu vida, pero carga un 25% de tu definitiva.", "H", "1", "1", "8", "0", "", "POTION||LOSEHP:0.05~POTION||ULT:25"},
        {"apostador", "bx_apostador", "Apostador", "Entrar en una sala cuesta 10 de oro; limpiarla sin que te hieran da 40 de oro.", "H", "1", "1", "8", "0", "", "ROOM|p:gold>=10|LOSEGOLD:10~PERFECT||GOLD:40"},
        {"juicio", "bx_juicio", "Juicio Final", "+35% de daño, pero los enemigos tienen +20% de vida y hacen +30% de daño. Derrotar a un jefe te cura el 35%.", "H", "4", "1", "2", "2", "cat:H:2", "MOD||DMG:0.35~MOD||ENEMYHP:0.20~MOD||ENEMYDMG:0.30~BOSSDEAD||HEAL:0.35"},
        {"ultimo_recurso", "bx_ultimo_recurso", "Último Recurso", "Beber un frasco con poca vida te da 0,6 s de invulnerabilidad.", "H", "1", "1", "8", "0", "", "POTION|p:low|INVULN:0.6"},
        {"caza_mayor", "bx_caza_mayor", "Caza Mayor", "Los enemigos tienen +20% de vida. Los mini-jefes y jefes sueltan un corazón y 8 almas al morir.", "H", "2", "1", "6", "0", "", "MOD||ENEMYHP:0.20~KILL|v:elite|HEARTDROP|icd=1~KILL|v:elite|SOULS:8"},
        {"ayuno", "bx_ayuno", "Ayuno", "-1 frasco máximo, pero haces +20% de daño.", "H", "1", "1", "8", "0", "", "MOD||POTMAX:-1~MOD||DMG:0.20"},
        {"marca_maldita", "bx_marca_maldita", "Marca Maldita", "15% de maldecir al golpear: los malditos reciben +20% de daño tuyo durante 6 s.", "I", "1", "1", "8", "0", "", "HIT|!v:curse|STATUS:curse,6,1|ch=0.15"},
        {"sentencia_oscura", "bx_sentencia_oscura", "Sentencia Oscura", "En combate, cada 9 s maldices al enemigo con más vida.", "I", "2", "1", "6", "0", "", "TICK|r:combat|MARKTOP:8|every=9"},
        {"maldicion_expansiva", "bx_maldicion_expansiva", "Maldición Contagiosa", "Cuando muere un enemigo maldito, la maldición salta a los cercanos.", "I", "2", "1", "6", "0", "", "KILL|v:curse|SPREAD:curse,110"},
        {"cosecha_maldita", "bx_cosecha_maldita", "Cosecha Maldita", "Los enemigos malditos sueltan 3 almas al morir (límite por sala).", "I", "1", "1", "8", "0", "", "KILL|v:curse|SOULS:3"},
        {"festin_oscuro", "bx_festin_oscuro", "Festín Oscuro", "Contra enemigos malditos robas un 4% del daño como vida.", "I", "2", "1", "6", "0", "", "MOD|v:curse|LIFESTEAL:0.04"},
        {"crit_maldito", "bx_crit_maldito", "Crítico Maldito", "+20% de probabilidad de crítico contra enemigos malditos.", "I", "2", "1", "6", "0", "", "MOD|v:curse|CRIT:0.20"},
        {"forma_sombra", "bx_forma_sombra", "Forma de Sombra", "Tu definitiva te transforma 8 s: +30% de daño, +25% de velocidad, -20% de daño recibido y rastro de sombra; maldice al enemigo más sano.", "I", "4", "1", "2", "1", "cat:I:3", "ULT||BUFF:dmg,0.30,8,1~ULT||BUFF:spd,0.25,8,1~ULT||BUFF:taken,-0.20,8,1~ULT||TRAIL:shadow,3,1.0~ULT||MARKTOP:10"},
        {"forma_bestial", "bx_forma_bestial", "Forma Bestial", "Al caer por debajo del 35% de vida te transformas 6 s: +30% de velocidad de ataque y +20% de velocidad (cada 30 s).", "I", "3", "1", "4", "1", "", "LOWHP||BUFF:atk,0.30,6,1|icd=30~LOWHP||BUFF:spd,0.20,6,1|icd=30"},
        {"espectro", "bx_espectro", "Forma Espectral", "Cada parry te vuelve espectral: +25% de velocidad 3 s y maldices al enemigo más sano.", "I", "2", "1", "6", "0", "", "PARRY||BUFF:spd,0.25,3,1~PARRY||MARKTOP:8"},
        {"vacio_voraz", "bx_vacio_voraz", "Vacío Voraz", "Cada baja carga un 3% de tu definitiva y, al terminar la definitiva, te curas el 10%.", "I", "3", "1", "4", "1", "", "KILL||ULT:3~ULTEND||HEAL:0.10"},
        {"corrupcion", "bx_corrupcion", "Corrupción", "30% de envenenar al golpear a un enemigo maldito.", "I", "1", "1", "8", "0", "", "HIT|v:curse|STATUS:poison,3,1|ch=0.3"},
        {"aura_penumbra", "bx_aura_penumbra", "Aura de Penumbra", "Al rodar dejas dos charcos de sombra que maldicen a los enemigos que los pisan.", "I", "1", "1", "8", "0", "", "ROLL||TRAIL:shadow,3,1.0~ROLLEND||TRAIL:shadow,3,1.0"},
        {"fuego_rayo", "bx_fuego_rayo", "Fuego y Rayo", "Los críticos contra enemigos en llamas sueltan un rayo de 2 saltos (cada 0,5 s).", "J", "2", "1", "6", "0", "", "CRIT|v:burn|CHAIN:2,0.45|icd=0.5"},
        {"explosion_hielo", "bx_explosion_hielo", "Estallido Helado", "Golpear a un enemigo congelado: 20% de causar un estallido (70% de daño, cada 1 s).", "J", "2", "1", "6", "0", "", "HIT|v:freeze|EXPLODE:56,0.7,slow,2|ch=0.2 icd=1"},
        {"choque_termico", "bx_choque_termico", "Choque Térmico", "Golpear a un enemigo en llamas y ralentizado a la vez provoca una explosión de vapor (120% de daño, cada 2 s).", "J", "3", "1", "4", "1", "", "HIT|v:burn,v:slow|EXPLODE:70,1.2|icd=2"},
        {"electro_veneno", "bx_electro_veneno", "Conducción Tóxica", "Golpear a un enemigo envenenado y electrizado provoca una explosión tóxica (80% de daño, cada 1,5 s).", "J", "1", "1", "8", "0", "", "HIT|v:shock,v:poison|EXPLODE:50,0.8,poison,3|icd=1.5"},
        {"sangre_hirviente", "bx_sangre_hirviente", "Sangre Hirviente", "Los enemigos que sangran y arden a la vez reciben +30% de daño.", "J", "2", "1", "6", "0", "", "MOD|v:bleed,v:burn|DMG:0.30"},
        {"parry_fuego", "bx_parry_fuego", "Parry Ardiente", "Cada parry prende fuego a los enemigos cercanos durante 3 s.", "J", "2", "1", "6", "0", "", "PARRY||STATUS:burn,3,1.5|aoe=100"},
        {"parry_hielo", "bx_parry_hielo", "Parry Glacial", "Cada parry congela 1,2 s a los enemigos cercanos (los jefes solo se ralentizan).", "J", "2", "1", "6", "0", "", "PARRY||STATUS:freeze,1.2,1|aoe=90 icd=2"},
        {"skill_critico", "bx_skill_critico", "Hechizo Certero", "Tras lanzar una habilidad, +25% de probabilidad de crítico durante 5 s.", "J", "1", "1", "8", "0", "", "SKILL||BUFF:crit,0.25,5,1"},
        {"veneno_critico", "bx_veneno_critico", "Toxina Crítica", "+18% de probabilidad de crítico contra enemigos envenenados.", "J", "1", "1", "8", "0", "", "MOD|v:poison|CRIT:0.18"},
        {"frasco_explosivo", "bx_frasco_explosivo", "Frasco Explosivo", "Beber un frasco provoca una explosión a tu alrededor (150% de daño).", "J", "1", "1", "8", "0", "", "POTION||EXPLODE:90,1.5|aoe=-1"},
        {"triple_filo", "bx_triple_filo", "Triple Filo", "Cada 7 golpes lanzas 3 cuchillas (50% de daño).", "J", "2", "1", "6", "0", "", "STREAK||PROJ:blade,3,0.5|n=7"},
        {"corazon_ardiente", "bx_corazon_ardiente", "Corazón Ardiente", "Los enemigos en llamas pueden soltar un corazón al morir (cada 25 s).", "J", "1", "1", "8", "0", "", "KILL|v:burn|HEARTDROP|icd=25"},
        {"convergencia", "bx_convergencia", "Convergencia Elemental", "En combate, cada 8 s un anillo de fuego y uno de hielo salen de ti y caen 2 rayos.", "J", "4", "1", "2", "1", "has:3:5,6,7,48,54,59,187,189", "TICK|r:combat|PROJ:ring,8,0.6,burn|every=8~TICK|r:combat|PROJ:ring,8,0.6,slow|every=8~TICK|r:combat|STRIKE:2,1.0|every=8"},
    };

    /** Sinergias: clave, nombre, descripcion, pista, bendiciones necesarias, miembros (ids), reglas. */
    static final String[][] SYN = {
        {"infierno", "Infierno", "Tus golpes contra enemigos en llamas propagan el fuego a los cercanos (cada 0,6 s) y los quemados reciben +10% de daño.", "Reúne 3 de sus bendiciones para activarla.", "3", "5,48,49,50,51,52,53,47,151,124,192,198,187,191", "HIT|v:burn|SPREAD:burn,70|icd=0.6~MOD|v:burn|DMG:0.10"},
        {"cripta_hielo", "Cripta de Hielo", "Tus críticos contra enemigos ralentizados o congelados estallan en escarcha (70% de daño, cada 0,8 s).", "Reúne 3 de sus bendiciones para activarla.", "3", "6,54,55,56,57,58,125,152,193,188,189", "CRIT|v:slow|EXPLODE:56,0.7,slow,2|icd=0.8"},
        {"tormenta_viva", "Tormenta Viva", "Cada descarga arcana te da +15% de velocidad de ataque 4 s y carga un 6% de tu definitiva.", "Reúne 3 de sus bendiciones para activarla.", "3", "7,59,60,61,62,63,64,126,153,187,65", "DISCHARGED||BUFF:atk,0.15,4,1~DISCHARGED||ULT:6"},
        {"muerte_lenta", "Muerte Lenta", "El daño periódico hace +25% y los enemigos con 2 o más estados alterados reciben +15% de daño.", "Reúne 3 de sus bendiciones para activarla.", "3", "8,47,66,67,68,69,35,191,157,158,185,195,190", "MOD||DOT:0.25~MOD|v:multi>=2|DMG:0.15"},
        {"contragolpe_perfecto", "Contragolpe Perfecto", "Cada parry reduce 1 s tus habilidades y te da +20% de velocidad de ataque durante 4 s.", "Reúne 3 de sus bendiciones para activarla.", "3", "76,77,78,79,80,81,82,192,193,60,183,112", "PARRY||CDR:1.0~PARRY||BUFF:atk,0.2,4,1"},
        {"muro_viviente", "Muro Viviente", "Mientras tengas escudo haces +15% de daño, y cuando absorbe un golpe te curas el 3%.", "Reúne 3 de sus bendiciones para activarla.", "3", "15,23,83,84,85,88,156,96,139,77", "MOD|p:shield|DMG:0.15~BLOCKED||HEAL:0.03|icd=1"},
        {"sangre_furia", "Sangre y Furia", "Con poca vida: +15% de velocidad de ataque; matar cura el 4% y al ser herido tu siguiente golpe hace +50%.", "Reúne 3 de sus bendiciones para activarla.", "3", "91,90,92,87,86,89,182,88,4,9,21,3", "MOD|p:low|ATKSPD:0.15~KILL|p:low|HEAL:0.04|icd=0.3~HURT|p:low|NEXTHIT:0.5,5"},
        {"ritmo_imparable", "Ritmo Imparable", "Cada crítico da +8% de velocidad de ataque durante 3 s (hasta 3 cargas) y +6% de probabilidad de crítico.", "Reúne 3 de sus bendiciones para activarla.", "3", "12,44,37,46,40,29,106,109,43,45,194,39", "CRIT||BUFF:atk,0.08,3,3~MOD||CRIT:0.06"},
        {"artilleria", "Artillería", "Tus proyectiles hacen +20% de daño y explotan al terminar (35% de daño).", "Reúne 3 de sus bendiciones para activarla.", "3", "123,118,120,121,116,119,117,122,22,127,128,124,125,126,132,133,131,130,197,129", "MOD||PROJDMG:0.20~PROJEND||EXPLODE:40,0.35|icd=0.4"},
        {"danza_eterea", "Danza Etérea", "Cada esquiva carga un 8% de tu definitiva y potencia tu siguiente habilidad un 40% (5 s).", "Reúne 3 de sus bendiciones para activarla.", "3", "101,102,103,62,111,99,10,26,110,112,186,53,129", "DODGE||ULT:8~DODGE||NEXTSKILL:0.4,5"},
        {"alquimia_mayor", "Alquimia Mayor", "Cada moneda carga 1,5% de tu definitiva y cada alma 3%; con 100 de oro o más haces +8% de daño.", "Reúne 3 de sus bendiciones para activarla.", "3", "14,13,19,135,136,137,138,140,141,142,144,145,146,147,148,149,134,139", "PICK|-|ULT:1.5|what=gold~PICK|-|ULT:3|what=soul~MOD|p:gold>=100|DMG:0.08"},
        {"legion_mas_alla", "Legión del Más Allá", "Mientras tengas espíritus haces +10% de daño; al ser herido uno te protege con 12 de escudo (cada 8 s).", "Reúne 2 de sus bendiciones para activarla.", "2", "150,151,152,153,154,155,156,157,158,159,160,161,162", "MOD|p:spirit|DMG:0.10~HURT|p:spirit|SHIELD:12|icd=8"},
        {"oscuridad", "Oscuridad Total", "Los enemigos malditos reciben +15% de daño extra y al morir cargan un 5% de tu definitiva.", "Reúne 3 de sus bendiciones para activarla.", "3", "175,176,177,178,179,180,185,154,181,183,186", "MOD|v:curse|DMG:0.15~KILL|v:curse|ULT:5"},
        {"pacto_riesgo", "Pacto del Riesgo", "Limpiar una sala sin recibir daño da +15% de daño durante 25 s y 10 de oro.", "Reúne 2 de sus bendiciones para activarla.", "2", "163,164,165,166,167,168,173,171,174,169,170,172", "CLEAR|p:noroomhit|BUFF:dmg,0.15,25,1~CLEAR|p:noroomhit|GOLD:10"},
        {"hechicero_supremo", "Hechicero Supremo", "Cada habilidad reduce 0,8 s las demás y tu definitiva potencia tus habilidades un 30% durante 8 s.", "Reúne 3 de sus bendiciones para activarla.", "3", "17,16,24,71,72,73,74,75,70,61,57,127,194,52,133", "SKILL||CDR:0.8~ULT||BUFF:skill,0.3,8,1"},
        {"cazador_elites", "Cazador de Élites", "+15% de probabilidad de crítico contra mini-jefes y jefes; matarlos te cura el 5%.", "Reúne 3 de sus bendiciones para activarla.", "3", "31,18,45,32,30,33,173,137,145,25,41,39", "MOD|v:elite|CRIT:0.15~KILL|v:elite|HEAL:0.05"},
        {"terremoto", "Terremoto", "Al aterrizar de una caída larga ganas +20% de daño 4 s y cada salto en el aire te da 8 de escudo (cada 2 s).", "Reúne 3 de sus bendiciones para activarla.", "3", "11,104,105,115,114,110,2,113", "LAND||BUFF:dmg,0.2,4,1~AIRJUMP||SHIELD:8|icd=2"},
        {"reaccion_cadena", "Reacción en Cadena", "Tus golpes a enemigos rodeados tienen 15% de provocar una explosión (40% de daño, cada 1 s).", "Reúne 3 de sus bendiciones para activarla.", "3", "20,51,83,86,79,196,41,123,104,105,189,188,190", "HIT|v:crowd|EXPLODE:50,0.4|ch=0.15 icd=1"},
        {"resonancia_elemental", "Resonancia Elemental", "Golpear a un enemigo con 2 o más estados alterados lanza un rayo de 2 saltos (cada 1,2 s).", "Reúne 3 de sus bendiciones para activarla.", "3", "5,6,7,8,175,35,124,125,126,151,152,153,157", "HIT|v:multi>=2|CHAIN:2,0.4|icd=1.2"},
        {"frasco_vida", "Frasco de Vida", "Toda curación recibida es un 25% mayor y beber un frasco te da 25 de escudo.", "Reúne 3 de sus bendiciones para activarla.", "3", "140,141,142,174,196,172,169,1,93,95,94,82,155,89", "MOD||HEALMUL:0.25~POTION||SHIELD:25"},
    };

    private static BSyn[] syns;
    private static int ruleIdx;

    static BRule[] rules(String joined, int owner, int syn) {
        if (joined.isEmpty()) return new BRule[0];
        String[] p = joined.split("~");
        BRule[] r = new BRule[p.length];
        for (int i = 0; i < p.length; i++) { r[i] = BRule.parse(p[i], owner); r[i].syn = syn; r[i].idx = ruleIdx++; }
        return r;
    }

    /** Construye las 200 bendiciones: las originales (ya declaradas) completadas con categoria y rareza, y las 172 nuevas. */
    static Blessing[] all(Blessing[] legacy) {
        Blessing[] a = new Blessing[200];
        for (int i = 0; i < legacy.length; i++) {
            Blessing b = legacy[i];
            a[i] = new Blessing(b.id, b.icon, b.name, b.desc, b.max, b.weight, LEG_CAT.charAt(i), LEG_RAR[i], 0, "", new BRule[0], LEG_KEY[i]);
        }
        for (int j = 0; j < NEW.length; j++) {
            String[] n = NEW[j];
            int id = legacy.length + j;
            a[id] = new Blessing(id, n[1], n[2], n[3], Integer.parseInt(n[6]), Integer.parseInt(n[7]), n[4].charAt(0), Integer.parseInt(n[5]), Integer.parseInt(n[8]), n[9], rules(n[10], id, -1), n[0]);
        }
        return a;
    }

    static BSyn[] syns() {
        if (syns == null) {
            BSyn[] s = new BSyn[SYN.length];
            for (int i = 0; i < s.length; i++) {
                String[] d = SYN[i];
                String[] m = d[5].split(",");
                int[] mem = new int[m.length];
                for (int k = 0; k < m.length; k++) mem[k] = Integer.parseInt(m[k]);
                s[i] = new BSyn(i, d[1], d[2], d[3], Integer.parseInt(d[4]), mem, rules(d[6], -1, i));
            }
            syns = s;
        }
        return syns;
    }
}
