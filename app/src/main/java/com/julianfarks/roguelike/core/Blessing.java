package com.julianfarks.roguelike.core;

/** Bendiciones (mejoras de la run) que se eligen en altares. */
public final class Blessing {
    public final int id;
    public final String icon, name, desc;
    public final int max;
    public final int weight;
    Blessing(int id, String icon, String name, String desc, int max, int weight) {
        this.id = id; this.icon = icon; this.name = name; this.desc = desc; this.max = max; this.weight = weight;
    }

    public static final int FILO = 0, CORAZON = 1, ALAS = 2, FURIA = 3, SANGRE = 4, BRASAS = 5, GLACIAL = 6, CHISPA = 7, ESPINAS = 8, PIEDRA = 9,
            FANTASMA = 10, DOBLE_SALTO = 11, CRITICO = 12, ALMA = 13, FORTUNA = 14, ESCUDO = 15, ENFRIAMIENTO = 16, HABILIDAD = 17,
            EJECUTOR = 18, IMAN = 19, VENGANZA = 20, SEGUNDA = 21, ONDA = 22, EGIDA = 23, SABIO = 24, GIGANTE = 25, SOMBRA = 26, ECLIPSE = 27;

    public static final Blessing[] ALL = {
            new Blessing(FILO, "b_filo", "Filo Afilado", "+15% de daño de arma por nivel.", 3, 10),
            new Blessing(CORAZON, "b_corazon", "Corazón Robusto", "+20 de vida máxima por nivel y te cura 20.", 3, 10),
            new Blessing(ALAS, "b_alas", "Pies Alados", "+8% de velocidad de movimiento por nivel.", 3, 8),
            new Blessing(FURIA, "b_furia", "Furia Creciente", "Cada baja da +4% de daño (máx. 5 cargas +2 por nivel). Se pierde al recibir daño.", 3, 7),
            new Blessing(SANGRE, "b_sangre", "Sed de Sangre", "Robas el 3% del daño infligido como vida por nivel.", 3, 6),
            new Blessing(BRASAS, "b_brasas", "Brasas Eternas", "Tus golpes queman: 25% de probabilidad por nivel.", 3, 7),
            new Blessing(GLACIAL, "b_glacial", "Contacto Glacial", "Tus golpes ralentizan y a veces congelan: 20% por nivel.", 3, 7),
            new Blessing(CHISPA, "b_chispa", "Chispa Voltaica", "15% por nivel de soltar un rayo encadenado al golpear.", 3, 6),
            new Blessing(ESPINAS, "b_espinas", "Veneno de Espinas", "Tus golpes envenenan: 25% de probabilidad por nivel.", 3, 7),
            new Blessing(PIEDRA, "b_piedra", "Piel de Piedra", "-8% de daño recibido por nivel.", 3, 8),
            new Blessing(FANTASMA, "b_fantasma", "Esquive Fantasma", "Rodar dura más invulnerable y deja una estela que daña.", 2, 5),
            new Blessing(DOBLE_SALTO, "b_doble_salto", "Doble Salto", "Puedes saltar una vez más en el aire.", 1, 9),
            new Blessing(CRITICO, "b_critico", "Maestría Crítica", "+8% de prob. crítica y +20% de daño crítico por nivel.", 3, 7),
            new Blessing(ALMA, "b_alma", "Alma Voraz", "+30% de almas por nivel.", 3, 6),
            new Blessing(FORTUNA, "b_fortuna", "Fortuna", "+30% de oro por nivel.", 3, 6),
            new Blessing(ESCUDO, "b_escudo_estelar", "Escudo Estelar", "Un escudo absorbe un golpe al entrar a cada sala (más fuerte por nivel).", 3, 6),
            new Blessing(ENFRIAMIENTO, "b_enfriamiento", "Enfriamiento Rápido", "-12% de enfriamiento de habilidades por nivel.", 3, 8),
            new Blessing(HABILIDAD, "b_habilidad", "Habilidad Potenciada", "+20% de daño de habilidades por nivel.", 3, 8),
            new Blessing(EJECUTOR, "b_ejecutor", "Ejecutor", "+40% de daño a enemigos con menos de 30% de vida por nivel.", 3, 6),
            new Blessing(IMAN, "b_iman", "Imán de Almas", "Atraes oro, almas y corazones desde más lejos.", 2, 5),
            new Blessing(VENGANZA, "b_venganza", "Espíritu Vengador", "Los enemigos explotan al morir y dañan a los cercanos.", 3, 6),
            new Blessing(SEGUNDA, "b_segunda", "Segunda Oportunidad", "Revives una vez con 35% de vida.", 1, 3),
            new Blessing(ONDA, "b_onda", "Hoja Fantasma", "Cada segundo golpe lanza una onda de energía.", 2, 7),
            new Blessing(EGIDA, "b_egida", "Barrera de Égida", "Tras rodar ganas un escudo breve.", 2, 6),
            new Blessing(SABIO, "b_sabio", "Sabiduría", "+20% de carga de definitiva por nivel y empiezas cada sala con 15%.", 3, 5),
            new Blessing(GIGANTE, "b_gigante", "Golpe Gigante", "El tercer golpe del combo hace +40% de daño y una onda de choque.", 2, 7),
            new Blessing(SOMBRA, "b_sombra", "Paso de Sombra", "Rodar atraviesa enemigos y los daña.", 2, 5),
            new Blessing(ECLIPSE, "b_eclipse", "Eclipse", "Cada 12 s, tu siguiente golpe hace daño x2.5 (más rápido por nivel).", 2, 5),
    };
}
