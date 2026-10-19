# Bendiciones (altares) — 200 bendiciones, 20 sinergias

> Documento GENERADO por `tools/tests/BlessDocGen.java` desde el catálogo real; el catálogo se edita en `tools/blessings/cat_*.py` y se regenera con `python3 tools/blessings/gen.py` + `python3 tools/i18n/build_catalogs.py`.

## Resumen

- **200** bendiciones distintas (las **28** originales conservan id 0–27; las **172** nuevas son id 28–199), **185** de ellas participan en alguna de las **20** sinergias.
- 5 rarezas: común 50 · poco común 60 · rara 53 · épica 27 · legendaria 10
- 10 categorías (A–J); 10 legendarias (una por categoría) con condiciones de aparición.

### Distribución por categoría y rareza

| Categoría | Total | común | poco común | rara | épica | legendaria |
|---|---|---|---|---|---|---|
| A · Daño físico | 25 | 10 | 6 | 4 | 4 | 1 |
| B · Magia y elementos | 36 | 12 | 11 | 5 | 7 | 1 |
| C · Defensa, parry y supervivencia | 28 | 8 | 8 | 6 | 5 | 1 |
| D · Velocidad, movilidad y evasión | 22 | 6 | 5 | 10 | 0 | 1 |
| E · Proyectiles | 19 | 4 | 5 | 7 | 2 | 1 |
| F · Recursos y cofres | 19 | 9 | 5 | 2 | 2 | 1 |
| G · Invocaciones y compañeros | 13 | 1 | 5 | 4 | 2 | 1 |
| H · Riesgo y recompensa | 12 | 0 | 6 | 3 | 2 | 1 |
| I · Maldiciones y transformaciones | 12 | 0 | 4 | 5 | 2 | 1 |
| J · Híbridas | 14 | 0 | 5 | 7 | 1 | 1 |

## Cómo funciona el motor

Cada bendición nueva es **datos** (`BlessData`, generado) + un conjunto de **reglas** con la forma `DISPARADOR|condiciones|EFECTO:args|opciones` que interpreta `BRule.parse`; la lógica está en `BlessFx` (ganchos y condiciones) y `BlessEffects` (efectos). Una sinergia (`BSyn`) es un grupo de bendiciones: al tener `need` o más de sus miembros se añaden sus reglas.

- **Disparadores**: golpe, crítico, remate, racha, muerte, daño recibido, bloqueo, parry, esquiva, rodar, habilidad, definitiva, proyectil, sala, sala limpia, jefe muerto, recogida, poción, salto, aterrizaje, vida baja, periódico, peligro superado, descarga, desbordamiento y pasivos (`MOD`).
- **Efectos**: estados (quemar, congelar, ralentizar, envenenar, electrocutar, sangrar, maldecir), propagar, explosiones, cadenas, mejoras temporales, curar, escudo, enfriamientos, definitiva, proyectiles, oro, almas, carga arcana, descargas, invulnerabilidad breve, empujar/atraer, estelas, pociones, coste de vida/oro, ralentizar el tiempo, espíritus compañeros, etc.
- **Opciones**: `icd` (reutilización por regla), `ch` (probabilidad), `n`, `every`, `k`, `aoe`, `what`, `src` (arma/habilidad/proyectil/daño periódico), `scale` (escala con el nivel de la bendición).

### Límites de seguridad (sin bucles ni infinitos)

- Un efecto **nunca** desencadena otro efecto (profundidad 1); solo `KILL` (hasta 3) y `DISCHARGED` (hasta 2) pueden encadenarse, de forma acotada.
- Cada regla tiene reutilización (`icd`) y hay un tope global de **90 ejecuciones por segundo**.
- Multiplicador de daño de bendiciones limitado a **×3**.
- Curación por bendiciones limitada por sala (**25 %** de la vida máxima; **35 %** en jefe); oro ≤ 90 y almas ≤ 45 por sala; reducción de enfriamientos con cubo recargable; invulnerabilidad por efecto ≤ **0,6 s**; esquiva con anti-rebote de 0,5 s; coste de vida (`LOSEHP`) nunca baja del 12 % de la vida máxima.
- Los proyectiles creados por bendiciones no generan nuevos eventos de proyectil (no hay cascadas).

## Altares: selección de ofertas

`BlessOffer.pick` elige 3 (o 4 con la mejora de oferta) bendiciones **distintas** entre las elegibles (nivel máximo no alcanzado, piso mínimo, requisitos de legendarias). El peso base depende de la rareza; se reduce si la categoría ya está en la oferta (variedad) y si la bendición ya se ofreció muchas veces en la partida; sube ligeramente (sin garantizar nada) si comparte sinergia con lo que ya tienes y con la suerte para raras. Como máximo **una legendaria por oferta**.

Cada tarjeta muestra categoría, rareza (color), nivel, descripción y, sin saturar, la mejor sinergia relacionada (`+ nombre n/N`). La pantalla **Bendiciones activas** (pausa) lista las que tienes, con sus condiciones y las sinergias activas/en progreso. Al activarse una sinergia aparece el aviso «¡Sinergia activada!», con efecto de partículas y sonido.

## Guardado

La partida guarda solo el arreglo `bless` (nivel por id). Las partidas antiguas (28 entradas) se cargan en el arreglo de 200 sin perder datos; los ids 0–27 no cambian. El estado de ejecución (`BlessRt`: temporizadores, espíritus, canales) no se guarda: se reconstruye al cargar y al cambiar de sala/piso.

## Pruebas

Ver `tools/tests/bless_test.sh`: catálogo (unicidad, iconos, rarezas, sinergias, traducciones, ofertas, compatibilidad), sonda de efecto real por bendiciones y sinergias, límites/estrés y partidas de bot con builds.
## Sinergias

| # | Sinergia | Requiere | Efecto | Bendiciones |
|---|---|---|---|---|
| 1 | **Infierno** | 3 de 14 | Tus golpes contra enemigos en llamas propagan el fuego a los cercanos (cada 0,6 s) y los quemados reciben +10% de daño. | Brasas Eternas, Llama Voraz, Brasa Crítica, Contagio Ígneo, Pira Viviente, Aliento de Dragón, Rastro Ardiente, Combustión, Llama Fatua, Disparo Incendiario, Parry Ardiente, Corazón Ardiente, Fuego y Rayo, Sangre Hirviente |
| 2 | **Cripta de Hielo** | 3 de 11 | Tus críticos contra enemigos ralentizados o congelados estallan en escarcha (70% de daño, cada 0,8 s). | Contacto Glacial, Escarcha Quebradiza, Esquirlas de Hielo, Aura Gélida, Ventisca, Congelación Profunda, Disparo Gélido, Espíritu Glacial, Parry Glacial, Estallido Helado, Choque Térmico |
| 3 | **Tormenta Viva** | 3 de 11 | Cada descarga arcana te da +15% de velocidad de ataque 4 s y carga un 6% de tu definitiva. | Chispa Voltaica, Carga Estática, Pararrayos, Voltio Arcano, Batería Viva, Descarga Mayor, Conductor, Disparo Voltaico, Espíritu del Trueno, Fuego y Rayo, Tempestad Eterna |
| 4 | **Muerte Lenta** | 3 de 13 | El daño periódico hace +25% y los enemigos con 2 o más estados alterados reciben +15% de daño. | Veneno de Espinas, Combustión, Ponzoña Virulenta, Plaga, Toxina Nerviosa, Esporas Tóxicas, Filo Sangrante, Sangre Hirviente, Espíritu Venenoso, Espíritu de Sombra, Corrupción, Toxina Crítica, Conducción Tóxica |
| 5 | **Contragolpe Perfecto** | 3 de 12 | Cada parry reduce 1 s tus habilidades y te da +20% de velocidad de ataque durante 4 s. | Contra del Parry, Parry Templado, Parry Cargado, Eco Defensivo, Maestro del Parry, Reflejo Estelar, Calma del Guardián, Parry Ardiente, Parry Glacial, Pararrayos, Forma Espectral, Reloj del Destino |
| 6 | **Muro Viviente** | 3 de 10 | Mientras tengas escudo haces +15% de daño, y cuando absorbe un golpe te curas el 3%. | Escudo Estelar, Barrera de Égida, Escudo Reactivo, Bastión de Victoria, Armadura de Hierro, Sangre Fría, Espíritu Guardián, Égida Perpetua, Corazón Blindado, Parry Templado |
| 7 | **Sangre y Furia** | 3 de 12 | Con poca vida: +15% de velocidad de ataque; matar cura el 4% y al ser herido tu siguiente golpe hace +50%. | Rabia Herida, Último Bastión, Sanguinario, Contragolpe Desesperado, Coraza de Espinas, Instinto de Supervivencia, Forma Bestial, Sangre Fría, Sed de Sangre, Piel de Piedra, Segunda Oportunidad, Furia Creciente |
| 8 | **Ritmo Imparable** | 3 de 12 | Cada crítico da +8% de velocidad de ataque durante 3 s (hasta 3 cargas) y +6% de probabilidad de crítico. | Maestría Crítica, Ojo de Halcón, Impulso Letal, Cadena de Críticos, Ritmo de Combate, Hoja Rápida, Cadencia en Movimiento, Ráfaga de Remate, Sed de Batalla, Ensañamiento, Hechizo Certero, Remate Brutal |
| 9 | **Artillería** | 3 de 20 | Tus proyectiles hacen +20% de daño y explotan al terminar (35% de daño). | Proyectil Explosivo, Ricochet, Perforante, Doble Lanzamiento, Punta Afilada, Buscador, Vuelo Veloz, Onda Expansiva, Hoja Fantasma, Lluvia de Hojas, Ráfaga Estelar, Disparo Incendiario, Disparo Gélido, Disparo Voltaico, Orbe Santo, Tormenta de Acero, Foco Letal, Tirador Experto, Triple Filo, Estela de Rodada |
| 10 | **Danza Etérea** | 3 de 13 | Cada esquiva carga un 8% de tu definitiva y potencia tu siguiente habilidad un 40% (5 s). | Esquiva Sagrada, Baile de Cuchillas, Evasión Mágica, Batería Viva, Segundo Aliento, Sombra Veloz, Esquive Fantasma, Paso de Sombra, Viento de Cola, Reloj del Destino, Aura de Penumbra, Rastro Ardiente, Estela de Rodada |
| 11 | **Alquimia Mayor** | 3 de 18 | Cada moneda carga 1,5% de tu definitiva y cada alma 3%; con 100 de oro o más haces +8% de daño. | Fortuna, Alma Voraz, Imán de Almas, Interés Compuesto, Poder del Oro, Cosecha de Almas, Almas en Furia, Alquimista, Reserva de Frascos, Brebaje Rebosante, Suerte Dorada, Botín de Élite, Recaudador, Cazatesoros, Ladrón de Almas, Corona del Avaro, Mercader Astuto, Corazón Blindado |
| 12 | **Legión del Más Allá** | 2 de 13 | Mientras tengas espíritus haces +10% de daño; al ser herido uno te protege con 12 de escudo (cada 8 s). | Luciérnaga, Llama Fatua, Espíritu Glacial, Espíritu del Trueno, Espíritu Maldito, Espíritu Sanador, Espíritu Guardián, Espíritu Venenoso, Espíritu de Sombra, Vínculo Espiritual, Sinfonía Espiritual, Pastor de Almas, Legión Espectral |
| 13 | **Oscuridad Total** | 3 de 11 | Los enemigos malditos reciben +15% de daño extra y al morir cargan un 5% de tu definitiva. | Marca Maldita, Sentencia Oscura, Maldición Contagiosa, Cosecha Maldita, Festín Oscuro, Crítico Maldito, Corrupción, Espíritu Maldito, Forma de Sombra, Forma Espectral, Aura de Penumbra |
| 14 | **Pacto del Riesgo** | 2 de 12 | Limpiar una sala sin recibir daño da +15% de daño durante 25 s y 10 de oro. | Desafío Doble, Sed de Riesgo, Cañón de Cristal, Pacto de Sangre, Todo o Nada, Temerario, Caza Mayor, Juicio Final, Ayuno, Sacrificio, Apostador, Último Recurso |
| 15 | **Hechicero Supremo** | 3 de 15 | Cada habilidad reduce 0,8 s las demás y tu definitiva potencia tus habilidades un 30% durante 8 s. | Habilidad Potenciada, Enfriamiento Rápido, Sabiduría, Canalizador, Catalizador, Resonancia, Manantial de Maná, Runa de Poder, Eco Arcano, Voltio Arcano, Ventisca, Lluvia de Hojas, Hechizo Certero, Aliento de Dragón, Tormenta de Acero |
| 16 | **Cazador de Élites** | 3 de 12 | +15% de probabilidad de crítico contra mini-jefes y jefes; matarlos te cura el 5%. | Rompeguardias, Ejecutor, Ensañamiento, Puñalada Trapera, Peso Pesado, Cazador de Enjambres, Caza Mayor, Cosecha de Almas, Botín de Élite, Golpe Gigante, Sentencia, Remate Brutal |
| 17 | **Terremoto** | 3 de 8 | Al aterrizar de una caída larga ganas +20% de daño 4 s y cada salto en el aire te da 8 de escudo (cada 2 s). | Triple Salto, Salto Explosivo, Aterrizaje Sísmico, Danza Aérea, Acróbata, Viento de Cola, Pies Alados, Maestro de Trampas |
| 18 | **Reacción en Cadena** | 3 de 13 | Tus golpes a enemigos rodeados tienen 15% de provocar una explosión (40% de daño, cada 1 s). | Espíritu Vengador, Pira Viviente, Escudo Reactivo, Coraza de Espinas, Eco Defensivo, Frasco Explosivo, Sentencia, Proyectil Explosivo, Salto Explosivo, Aterrizaje Sísmico, Choque Térmico, Estallido Helado, Conducción Tóxica |
| 19 | **Resonancia Elemental** | 3 de 13 | Golpear a un enemigo con 2 o más estados alterados lanza un rayo de 2 saltos (cada 1,2 s). | Brasas Eternas, Contacto Glacial, Chispa Voltaica, Veneno de Espinas, Marca Maldita, Filo Sangrante, Disparo Incendiario, Disparo Gélido, Disparo Voltaico, Llama Fatua, Espíritu Glacial, Espíritu del Trueno, Espíritu Venenoso |
| 20 | **Frasco de Vida** | 3 de 14 | Toda curación recibida es un 25% mayor y beber un frasco te da 25 de escudo. | Alquimista, Reserva de Frascos, Brebaje Rebosante, Ayuno, Frasco Explosivo, Último Recurso, Sacrificio, Corazón Robusto, Vitalidad, Cosecha de Vida, Sanación de Victoria, Calma del Guardián, Espíritu Sanador, Instinto de Supervivencia |

## A · Daño físico

| id | Bendición | Rareza | Máx. | Efecto | Sinergias |
|---|---|---|---|---|---|
| 0 | Filo Afilado | común | 3 | +15% de daño de arma por nivel. |  |
| 3 | Furia Creciente | poco común | 3 | Cada baja da +4% de daño (máx. 5 cargas +2 por nivel). Se pierde al recibir daño. | Sangre y Furia |
| 12 | Maestría Crítica | poco común | 3 | +8% de prob. crítica y +20% de daño crítico por nivel. | Ritmo Imparable |
| 18 | Ejecutor | poco común | 3 | +40% de daño a enemigos con menos de 30% de vida por nivel. | Cazador de Élites |
| 25 | Golpe Gigante | rara | 2 | El tercer golpe del combo hace +40% de daño y una onda de choque. | Cazador de Élites |
| 27 | Eclipse | épica | 2 | Cada 12 s, tu siguiente golpe hace daño x2.5 (más rápido por nivel). |  |
| 28 | Golpe Certero | común | 3 | Cada 4 golpes seguidos, el siguiente hace +25% de daño por nivel. |  |
| 29 | Hoja Rápida | común | 3 | +7% de velocidad de ataque por nivel. | Ritmo Imparable |
| 30 | Peso Pesado | común | 2 | +18% de daño por nivel a enemigos con más del 80% de vida. | Cazador de Élites |
| 31 | Rompeguardias | poco común | 2 | +22% de daño por nivel contra mini-jefes y jefes. | Cazador de Élites |
| 32 | Puñalada Trapera | poco común | 1 | Golpear a un enemigo por la espalda: +35% de daño. | Cazador de Élites |
| 33 | Cazador de Enjambres | común | 2 | +15% de daño por nivel a enemigos con otros dos cerca. | Cazador de Élites |
| 34 | Estocada Larga | común | 2 | +18% de alcance de arma por nivel. |  |
| 35 | Filo Sangrante | poco común | 1 | 25% de causar sangrado. Los enemigos sangrando reciben +15% de daño de tus golpes. | Muerte Lenta, Resonancia Elemental |
| 36 | Doble Tajo | épica | 1 | 18% de que tu golpe se repita poco después con el 40% del daño. |  |
| 37 | Impulso Letal | épica | 1 | Cada crítico da +7% de daño durante 4 s (hasta 5 cargas). | Ritmo Imparable |
| 38 | Pulso Constante | común | 2 | Los golpes no críticos hacen +14% de daño por nivel. |  |
| 39 | Remate Brutal | común | 2 | El tercer golpe del combo hace +25% de daño por nivel. | Ritmo Imparable, Cazador de Élites |
| 40 | Ritmo de Combate | rara | 1 | Cada remate de combo da +10% de velocidad de ataque durante 3 s (hasta 3 cargas). | Ritmo Imparable |
| 41 | Sentencia | legendaria | 1 | Tu remate detona una explosión de 200% de daño cada 4 s. *(Aparece con 3 bendiciones de su categoria, piso ≥ 2)* | Cazador de Élites, Reacción en Cadena |
| 42 | Maestro de Armas | rara | 1 | Con la vida al 90% o más: +30% de daño de arma. |  |
| 43 | Sed de Batalla | común | 1 | Cada baja da +12% de velocidad de ataque durante 3 s (hasta 2 cargas). | Ritmo Imparable |
| 44 | Ojo de Halcón | común | 3 | +5% de probabilidad de crítico por nivel. | Ritmo Imparable |
| 45 | Ensañamiento | rara | 1 | Los críticos contra enemigos con menos del 30% de vida hacen +50% de daño crítico extra. | Ritmo Imparable, Cazador de Élites |
| 46 | Cadena de Críticos | épica | 1 | Tras 2 críticos seguidos, +20% de probabilidad de crítico hasta que falles un golpe o te hieran. | Ritmo Imparable |

## B · Magia y elementos

| id | Bendición | Rareza | Máx. | Efecto | Sinergias |
|---|---|---|---|---|---|
| 5 | Brasas Eternas | poco común | 3 | Tus golpes queman: 25% de probabilidad por nivel. | Infierno, Resonancia Elemental |
| 6 | Contacto Glacial | poco común | 3 | Tus golpes ralentizan y a veces congelan: 20% por nivel. | Cripta de Hielo, Resonancia Elemental |
| 7 | Chispa Voltaica | poco común | 3 | 15% por nivel de soltar un rayo encadenado al golpear. | Tormenta Viva, Resonancia Elemental |
| 8 | Veneno de Espinas | poco común | 3 | Tus golpes envenenan: 25% de probabilidad por nivel. | Muerte Lenta, Resonancia Elemental |
| 16 | Enfriamiento Rápido | común | 3 | -12% de enfriamiento de habilidades por nivel. | Hechicero Supremo |
| 17 | Habilidad Potenciada | común | 3 | +20% de daño de habilidades por nivel. | Hechicero Supremo |
| 24 | Sabiduría | poco común | 3 | +20% de carga de definitiva por nivel y empiezas cada sala con 15%. | Hechicero Supremo |
| 47 | Combustión | común | 2 | El daño periódico (fuego, veneno, sangrado) hace +20% por nivel. | Infierno, Muerte Lenta |
| 48 | Llama Voraz | común | 1 | Los enemigos en llamas reciben +15% de daño de tus golpes y habilidades. | Infierno |
| 49 | Brasa Crítica | rara | 1 | +25% de probabilidad de crítico contra enemigos en llamas. | Infierno |
| 50 | Contagio Ígneo | poco común | 1 | Cuando muere un enemigo en llamas, el fuego salta a los cercanos. | Infierno |
| 51 | Pira Viviente | épica | 1 | Los enemigos en llamas explotan al morir (60% de daño) y prenden fuego alrededor. | Infierno, Reacción en Cadena |
| 52 | Aliento de Dragón | épica | 1 | Tu definitiva prende fuego a todos los enemigos durante 4 s. | Infierno, Hechicero Supremo |
| 53 | Rastro Ardiente | común | 1 | Al rodar dejas dos charcos de fuego que queman a los enemigos. | Infierno, Danza Etérea |
| 54 | Escarcha Quebradiza | rara | 1 | +35% de probabilidad de crítico contra enemigos ralentizados o congelados. | Cripta de Hielo |
| 55 | Esquirlas de Hielo | poco común | 1 | Los enemigos ralentizados o congelados sueltan 3 esquirlas al morir. | Cripta de Hielo |
| 56 | Aura Gélida | común | 1 | Cada 3 s ralentizas a los enemigos cercanos. | Cripta de Hielo |
| 57 | Ventisca | poco común | 1 | Tus habilidades ralentizan a los enemigos en un radio amplio. | Cripta de Hielo, Hechicero Supremo |
| 58 | Congelación Profunda | épica | 1 | Golpear a un enemigo ralentizado: 12% de congelarlo 1,2 s (cada 2 s). Los jefes solo se ralentizan. | Cripta de Hielo |
| 59 | Carga Estática | común | 1 | Tus golpes acumulan carga arcana (máx. 10). Al llegar a 10 se libera un rayo encadenado. | Tormenta Viva |
| 60 | Pararrayos | épica | 1 | Cada parry da 2 cargas arcanas y libera una descarga con todas tus cargas. | Tormenta Viva, Contragolpe Perfecto |
| 61 | Voltio Arcano | común | 1 | Cada habilidad que lanzas te da 3 cargas arcanas. | Tormenta Viva, Hechicero Supremo |
| 62 | Batería Viva | rara | 1 | Cada esquiva o rodar exitoso da 2 cargas arcanas. | Tormenta Viva, Danza Etérea |
| 63 | Descarga Mayor | épica | 1 | Con 6 o más cargas arcanas, tus golpes sueltan una descarga de 4 saltos (cada 1,5 s). | Tormenta Viva |
| 64 | Conductor | común | 1 | Tus rayos encadenados saltan a 1 enemigo más. | Tormenta Viva |
| 65 | Tempestad Eterna | legendaria | 1 | En combate, cada 4 s caen 3 rayos sobre enemigos al azar. *(Aparece con 2 bendiciones de su familia, piso ≥ 3)* | Tormenta Viva |
| 66 | Ponzoña Virulenta | común | 1 | Tus estados alterados duran 40% más. | Muerte Lenta |
| 67 | Plaga | épica | 1 | Cuando muere un enemigo envenenado, el veneno se contagia a los cercanos. | Muerte Lenta |
| 68 | Toxina Nerviosa | poco común | 1 | 40% de ralentizar al golpear a un enemigo envenenado. | Muerte Lenta |
| 69 | Esporas Tóxicas | común | 1 | En combate, cada 6 s una nube envenena a los enemigos cercanos. | Muerte Lenta |
| 70 | Eco Arcano | rara | 1 | Tras lanzar una habilidad, tu siguiente golpe hace +50% de daño (5 s). | Hechicero Supremo |
| 71 | Canalizador | poco común | 1 | Cada golpe acorta 0,25 s la reutilización de tu habilidad más lenta (límite por segundo). | Hechicero Supremo |
| 72 | Catalizador | épica | 1 | Al usar tu definitiva, tus habilidades se reponen al instante. | Hechicero Supremo |
| 73 | Resonancia | poco común | 1 | Cada habilidad potencia la siguiente: +35% de daño (6 s). | Hechicero Supremo |
| 74 | Manantial de Maná | común | 1 | Cada habilidad lanzada carga un 6% de tu definitiva. | Hechicero Supremo |
| 75 | Runa de Poder | rara | 1 | +25% de carga de definitiva y +10% de daño de habilidades. | Hechicero Supremo |

## C · Defensa, parry y supervivencia

| id | Bendición | Rareza | Máx. | Efecto | Sinergias |
|---|---|---|---|---|---|
| 1 | Corazón Robusto | común | 3 | +20 de vida máxima por nivel y te cura 20. | Frasco de Vida |
| 4 | Sed de Sangre | poco común | 3 | Robas el 3% del daño infligido como vida por nivel. | Sangre y Furia |
| 9 | Piel de Piedra | común | 3 | -8% de daño recibido por nivel. | Sangre y Furia |
| 15 | Escudo Estelar | poco común | 3 | Un escudo absorbe un golpe al entrar a cada sala (más fuerte por nivel). | Muro Viviente |
| 21 | Segunda Oportunidad | épica | 1 | Revives una vez con 35% de vida. | Sangre y Furia |
| 23 | Barrera de Égida | poco común | 2 | Tras rodar ganas un escudo breve. | Muro Viviente |
| 76 | Contra del Parry | poco común | 1 | Tras un parry, tu siguiente golpe hace +60% de daño (4 s). | Contragolpe Perfecto |
| 77 | Parry Templado | común | 1 | Cada parry te da un escudo de 15. | Contragolpe Perfecto, Muro Viviente |
| 78 | Parry Cargado | común | 1 | Cada parry carga un 8% de tu definitiva. | Contragolpe Perfecto |
| 79 | Eco Defensivo | rara | 1 | Cada parry libera una onda de 100% de daño que empuja a los enemigos. | Contragolpe Perfecto, Reacción en Cadena |
| 80 | Maestro del Parry | épica | 1 | Cada parry da +12% de daño durante 5 s (hasta 3 cargas). | Contragolpe Perfecto |
| 81 | Reflejo Estelar | épica | 1 | Cada parry dispara un anillo de 8 estrellas (50% de daño). | Contragolpe Perfecto |
| 82 | Calma del Guardián | poco común | 1 | Cada parry cura el 3% de tu vida máxima (límite por sala). | Contragolpe Perfecto, Frasco de Vida |
| 83 | Escudo Reactivo | poco común | 1 | Cuando tu escudo absorbe un golpe, estalla con 80% de daño a tu alrededor. | Muro Viviente, Reacción en Cadena |
| 84 | Bastión de Victoria | común | 1 | Al limpiar una sala ganas un escudo de 20. | Muro Viviente |
| 85 | Armadura de Hierro | rara | 1 | Tus golpes dan 3 de escudo (cada 1,2 s) y tu escudo puede acumular 30 más. | Muro Viviente |
| 86 | Coraza de Espinas | épica | 1 | Al recibir daño estallas dañando (70%) a los enemigos cercanos (cada 1,5 s). | Sangre y Furia, Reacción en Cadena |
| 87 | Contragolpe Desesperado | rara | 1 | Al recibir daño, tu siguiente golpe hace +70% de daño (4 s). | Sangre y Furia |
| 88 | Sangre Fría | poco común | 1 | Al caer por debajo del 35% de vida ganas un escudo de 40 (cada 20 s). | Muro Viviente, Sangre y Furia |
| 89 | Instinto de Supervivencia | rara | 1 | Al caer por debajo del 35% de vida: 0,6 s de invulnerabilidad y cura del 8% (cada 25 s). | Sangre y Furia, Frasco de Vida |
| 90 | Último Bastión | épica | 1 | Con menos del 35% de vida recibes un 30% menos de daño. | Sangre y Furia |
| 91 | Rabia Herida | rara | 1 | Con menos del 35% de vida haces +35% de daño. | Sangre y Furia |
| 92 | Sanguinario | rara | 1 | Con menos del 35% de vida robas un 5% del daño que infliges. | Sangre y Furia |
| 93 | Vitalidad | común | 3 | +10% de vida máxima por nivel. | Frasco de Vida |
| 94 | Sanación de Victoria | común | 1 | Al limpiar una sala recuperas el 5% de tu vida máxima. | Frasco de Vida |
| 95 | Cosecha de Vida | común | 1 | Cada baja cura el 1,5% de tu vida máxima (límite por sala). | Frasco de Vida |
| 96 | Égida Perpetua | legendaria | 1 | En combate ganas un escudo de 30 cada 8 s. Si el escudo absorbe un golpe, 0,5 s de invulnerabilidad (cada 3 s). *(Aparece con 3 bendiciones de su categoria, piso ≥ 3)* | Muro Viviente |
| 97 | Onda de Choque | poco común | 1 | Al recibir un golpe empujas a los enemigos cercanos (cada 1,2 s). |  |

## D · Velocidad, movilidad y evasión

| id | Bendición | Rareza | Máx. | Efecto | Sinergias |
|---|---|---|---|---|---|
| 2 | Pies Alados | común | 3 | +8% de velocidad de movimiento por nivel. | Terremoto |
| 10 | Esquive Fantasma | rara | 2 | Rodar dura más invulnerable y deja una estela que daña. | Danza Etérea |
| 11 | Triple Salto | poco común | 1 | Ganas un salto extra en el aire (triple salto). | Terremoto |
| 26 | Paso de Sombra | rara | 2 | Rodar atraviesa enemigos y los daña. | Danza Etérea |
| 98 | Impulso de Rodada | común | 2 | Tu rodada es un 25% más rápida por nivel: recorre más distancia y termina antes. |  |
| 99 | Sombra Veloz | común | 1 | Tras rodar ganas +20% de velocidad de movimiento durante 2,5 s. | Danza Etérea |
| 100 | Racha del Cazador | común | 1 | Cada baja da +10% de velocidad de movimiento durante 4 s (hasta 3 cargas). |  |
| 101 | Esquiva Sagrada | rara | 1 | Cada esquiva da +15% de daño durante 4 s (hasta 2 cargas). | Danza Etérea |
| 102 | Baile de Cuchillas | rara | 1 | Cada esquiva lanza 3 cuchillas (60% de daño). | Danza Etérea |
| 103 | Evasión Mágica | rara | 1 | Cada esquiva reduce 0,6 s tus habilidades y carga un 5% de tu definitiva. | Danza Etérea |
| 104 | Salto Explosivo | poco común | 1 | Cada salto en el aire detona una explosión del 50% de daño bajo ti. | Terremoto, Reacción en Cadena |
| 105 | Aterrizaje Sísmico | poco común | 1 | Las caídas largas provocan una onda del 100% de daño al aterrizar. | Terremoto, Reacción en Cadena |
| 106 | Cadencia en Movimiento | rara | 1 | Mientras te mueves, +18% de velocidad de ataque. | Ritmo Imparable |
| 107 | Golpe en Carrera | común | 1 | Mientras te mueves, +12% de daño. |  |
| 108 | Quietud Letal | poco común | 1 | Quieto, haces +20% de daño y recibes un 10% menos. |  |
| 109 | Ráfaga de Remate | poco común | 1 | Cada remate de combo da +15% de velocidad de movimiento durante 3 s. | Ritmo Imparable |
| 110 | Viento de Cola | rara | 1 | Cada salto en el aire da +20% de velocidad de movimiento durante 3 s. | Danza Etérea, Terremoto |
| 111 | Segundo Aliento | rara | 1 | Cada esquiva te da 0,4 s de invulnerabilidad (cada 3 s). | Danza Etérea |
| 112 | Reloj del Destino | legendaria | 1 | Un parry o una esquiva ralentiza el tiempo 1,2 s para los enemigos (cada 18 s). *(Aparece con 3 bendiciones de su categoria, piso ≥ 2)* | Contragolpe Perfecto, Danza Etérea |
| 113 | Maestro de Trampas | rara | 1 | Sobrevolar pinchos sin tocarlos te da 15 de escudo y +20% de daño durante 5 s. | Terremoto |
| 114 | Acróbata | común | 1 | Cada salto da +10% de velocidad de ataque durante 2 s. | Terremoto |
| 115 | Danza Aérea | rara | 1 | En el aire haces +20% de daño. | Terremoto |

## E · Proyectiles

| id | Bendición | Rareza | Máx. | Efecto | Sinergias |
|---|---|---|---|---|---|
| 22 | Hoja Fantasma | poco común | 2 | Cada segundo golpe lanza una onda de energía. | Artillería |
| 116 | Punta Afilada | común | 2 | Tus proyectiles atraviesan 1 enemigo más por nivel. | Artillería |
| 117 | Vuelo Veloz | común | 1 | Tus proyectiles van un 25% más rápido y son un 20% más grandes. | Artillería |
| 118 | Ricochet | poco común | 1 | Tus proyectiles rebotan una vez contra paredes o enemigos. | Artillería |
| 119 | Buscador | común | 1 | Tus proyectiles giran ligeramente hacia los enemigos cercanos. | Artillería |
| 120 | Perforante | rara | 1 | Tus proyectiles hacen +20% de daño por cada enemigo que atraviesan. | Artillería |
| 121 | Doble Lanzamiento | rara | 1 | 20% de que tus proyectiles se lancen dos veces. | Artillería |
| 122 | Onda Expansiva | rara | 1 | Tus ondas de energía (Hoja Fantasma y similares) hacen +40% de daño y son más grandes. | Artillería |
| 123 | Proyectil Explosivo | épica | 1 | Tus proyectiles explotan al terminar su trayecto (50% de daño). | Artillería, Reacción en Cadena |
| 124 | Disparo Incendiario | poco común | 1 | 30% de que tus proyectiles prendan fuego al impactar. | Infierno, Artillería, Resonancia Elemental |
| 125 | Disparo Gélido | común | 1 | 50% de que tus proyectiles ralenticen al impactar. | Cripta de Hielo, Artillería, Resonancia Elemental |
| 126 | Disparo Voltaico | poco común | 1 | Tus proyectiles descargan un rayo de 2 saltos al impactar (cada 0,5 s). | Tormenta Viva, Artillería, Resonancia Elemental |
| 127 | Lluvia de Hojas | rara | 1 | Cada habilidad invoca una lluvia de 5 hojas cortantes sobre los enemigos. | Artillería, Hechicero Supremo |
| 128 | Ráfaga Estelar | rara | 1 | Cada 5 golpes sueltas 3 estrellas teledirigidas (50% de daño). | Artillería |
| 129 | Estela de Rodada | rara | 1 | Al terminar un rodar lanzas una onda de energía (80% de daño). | Artillería, Danza Etérea |
| 130 | Tirador Experto | poco común | 1 | Los proyectiles que impactan a enemigos lejanos hacen +40% de daño. | Artillería |
| 131 | Foco Letal | épica | 1 | Impactos seguidos con proyectiles al mismo enemigo: +8% de daño acumulable (hasta 5). | Artillería |
| 132 | Orbe Santo | rara | 1 | Matar con un proyectil libera un orbe sagrado teledirigido (70% de daño). | Artillería |
| 133 | Tormenta de Acero | legendaria | 1 | Cada habilidad lanza 10 cuchillas desde el cielo y tu definitiva 16. Tus proyectiles atraviesan 1 enemigo más. *(Aparece con 3 bendiciones de su categoria, piso ≥ 2)* | Artillería, Hechicero Supremo |

## F · Recursos y cofres

| id | Bendición | Rareza | Máx. | Efecto | Sinergias |
|---|---|---|---|---|---|
| 13 | Alma Voraz | común | 3 | +30% de almas por nivel. | Alquimia Mayor |
| 14 | Fortuna | común | 3 | +30% de oro por nivel. | Alquimia Mayor |
| 19 | Imán de Almas | común | 2 | Atraes oro, almas y corazones desde más lejos. | Alquimia Mayor |
| 134 | Mercader Astuto | común | 2 | Los precios de las tiendas bajan un 10% por nivel (máx. 50%). | Alquimia Mayor |
| 135 | Interés Compuesto | rara | 1 | Al limpiar una sala con 100 o más de oro, ganas 12 de oro extra. | Alquimia Mayor |
| 136 | Poder del Oro | rara | 1 | Con 150 o más de oro, haces +12% de daño. | Alquimia Mayor |
| 137 | Cosecha de Almas | poco común | 1 | Los mini-jefes y jefes sueltan 6 almas extra al morir. | Alquimia Mayor, Cazador de Élites |
| 138 | Almas en Furia | épica | 1 | Cada alma recogida da +5% de daño durante 6 s (hasta 5 cargas). | Alquimia Mayor |
| 139 | Corazón Blindado | poco común | 1 | Un corazón recogido con la vida llena te da 12 de escudo. | Muro Viviente, Alquimia Mayor |
| 140 | Alquimista | poco común | 1 | Beber un frasco te da +20% de daño durante 8 s y limpia tus estados alterados. | Alquimia Mayor, Frasco de Vida |
| 141 | Reserva de Frascos | común | 1 | +1 frasco de curación máximo. | Alquimia Mayor, Frasco de Vida |
| 142 | Brebaje Rebosante | poco común | 1 | Un frasco recogido con la reserva llena cura el 12% de tu vida. | Alquimia Mayor, Frasco de Vida |
| 143 | Visión del Altar | épica | 1 | Los altares de bendición ofrecen una opción adicional. |  |
| 144 | Suerte Dorada | común | 1 | +1 de suerte: mejores recompensas en cofres y tiendas. | Alquimia Mayor |
| 145 | Botín de Élite | común | 1 | Los mini-jefes y jefes sueltan 15 de oro extra. | Alquimia Mayor, Cazador de Élites |
| 146 | Recaudador | común | 1 | Cada baja con tu arma te da 1 de oro (límite por sala). | Alquimia Mayor |
| 147 | Cazatesoros | común | 1 | Al entrar en una sala ganas 8 de oro. | Alquimia Mayor |
| 148 | Ladrón de Almas | poco común | 1 | Los críticos te dan 2 almas (cada 0,8 s, límite por sala). | Alquimia Mayor |
| 149 | Corona del Avaro | legendaria | 1 | +50% de oro. Con 200 o más de oro haces +20% de daño y cada baja te da 2 de oro (límite por sala). *(Aparece con 3 bendiciones de su categoria, piso ≥ 2)* | Alquimia Mayor |

## G · Invocaciones y compañeros

| id | Bendición | Rareza | Máx. | Efecto | Sinergias |
|---|---|---|---|---|---|
| 150 | Luciérnaga | común | 1 | Una luciérnaga te acompaña y dispara a los enemigos cercanos (50% de daño cada 2 s). | Legión del Más Allá |
| 151 | Llama Fatua | poco común | 1 | Un espíritu de fuego te acompaña: dispara cada 2,6 s (55%) y prende fuego. | Infierno, Legión del Más Allá, Resonancia Elemental |
| 152 | Espíritu Glacial | poco común | 1 | Un espíritu de hielo libera cada 5 s una onda helada que ralentiza (70% de daño). | Cripta de Hielo, Legión del Más Allá, Resonancia Elemental |
| 153 | Espíritu del Trueno | épica | 1 | Un espíritu eléctrico lanza cada 4 s un rayo de 3 saltos (60% de daño). | Tormenta Viva, Legión del Más Allá, Resonancia Elemental |
| 154 | Espíritu Maldito | rara | 1 | Un espíritu oscuro maldice cada 8 s al enemigo más sano (+20% de daño recibido). | Legión del Más Allá, Oscuridad Total |
| 155 | Espíritu Sanador | poco común | 1 | Un espíritu te cura el 4% de tu vida cada 9 s si estás herido (límite por sala). | Legión del Más Allá, Frasco de Vida |
| 156 | Espíritu Guardián | rara | 1 | Un espíritu te protege con un escudo de 18 cada 14 s si no tienes ninguno. | Muro Viviente, Legión del Más Allá |
| 157 | Espíritu Venenoso | poco común | 1 | Un espíritu de veneno dispara cada 3 s (45%) y envenena. | Muerte Lenta, Legión del Más Allá, Resonancia Elemental |
| 158 | Espíritu de Sombra | rara | 1 | Un espíritu de sombra hiere cada 2,8 s (60%) y causa sangrado. | Muerte Lenta, Legión del Más Allá |
| 159 | Vínculo Espiritual | poco común | 1 | Un espíritu menor te acompaña (35% cada 3 s) y todos tus espíritus actúan un 30% más rápido. | Legión del Más Allá |
| 160 | Sinfonía Espiritual | épica | 1 | Tus espíritus actúan un 50% más rápido y cada baja los acelera aún más durante 4 s. | Legión del Más Allá |
| 161 | Pastor de Almas | rara | 1 | Cada alma recogida acelera a tus espíritus durante 5 s. | Legión del Más Allá |
| 162 | Legión Espectral | legendaria | 1 | Invoca tres espíritus: uno de fuego, uno glacial y uno eléctrico. *(Aparece con 3 bendiciones de su categoria, piso ≥ 2)* | Legión del Más Allá |

## H · Riesgo y recompensa

| id | Bendición | Rareza | Máx. | Efecto | Sinergias |
|---|---|---|---|---|---|
| 163 | Desafío Doble | poco común | 1 | Los enemigos tienen +15% de vida, pero ganas +35% de oro y +20% de almas. | Pacto del Riesgo |
| 164 | Sed de Riesgo | rara | 1 | Los enemigos te hacen +20% de daño, pero haces +25% de daño y +30% de daño crítico. | Pacto del Riesgo |
| 165 | Cañón de Cristal | poco común | 1 | -25% de vida máxima, +25% de daño. | Pacto del Riesgo |
| 166 | Pacto de Sangre | épica | 1 | Al entrar en cada sala pierdes el 8% de tu vida (nunca mueres por esto), pero haces +30% de daño. | Pacto del Riesgo |
| 167 | Todo o Nada | épica | 1 | Las salas perfectas (sin daño) dan 25 de oro y curan el 12%. Cada golpe recibido te cuesta 5 de oro. | Pacto del Riesgo |
| 168 | Temerario | rara | 1 | Mientras no te hayan herido en la sala, haces +20% de daño. | Pacto del Riesgo |
| 169 | Sacrificio | poco común | 1 | Beber un frasco te cuesta el 5% de tu vida, pero carga un 25% de tu definitiva. | Pacto del Riesgo, Frasco de Vida |
| 170 | Apostador | poco común | 1 | Entrar en una sala cuesta 10 de oro; limpiarla sin que te hieran da 40 de oro. | Pacto del Riesgo |
| 171 | Juicio Final | legendaria | 1 | +35% de daño, pero los enemigos tienen +20% de vida y hacen +30% de daño. Derrotar a un jefe te cura el 35%. *(Aparece con 2 bendiciones de su categoria, piso ≥ 3)* | Pacto del Riesgo |
| 172 | Último Recurso | poco común | 1 | Beber un frasco con poca vida te da 0,6 s de invulnerabilidad. | Pacto del Riesgo, Frasco de Vida |
| 173 | Caza Mayor | rara | 1 | Los enemigos tienen +20% de vida. Los mini-jefes y jefes sueltan un corazón y 8 almas al morir. | Pacto del Riesgo, Cazador de Élites |
| 174 | Ayuno | poco común | 1 | -1 frasco máximo, pero haces +20% de daño. | Pacto del Riesgo, Frasco de Vida |

## I · Maldiciones y transformaciones

| id | Bendición | Rareza | Máx. | Efecto | Sinergias |
|---|---|---|---|---|---|
| 175 | Marca Maldita | poco común | 1 | 15% de maldecir al golpear: los malditos reciben +20% de daño tuyo durante 6 s. | Oscuridad Total, Resonancia Elemental |
| 176 | Sentencia Oscura | rara | 1 | En combate, cada 9 s maldices al enemigo con más vida. | Oscuridad Total |
| 177 | Maldición Contagiosa | rara | 1 | Cuando muere un enemigo maldito, la maldición salta a los cercanos. | Oscuridad Total |
| 178 | Cosecha Maldita | poco común | 1 | Los enemigos malditos sueltan 3 almas al morir (límite por sala). | Oscuridad Total |
| 179 | Festín Oscuro | rara | 1 | Contra enemigos malditos robas un 4% del daño como vida. | Oscuridad Total |
| 180 | Crítico Maldito | rara | 1 | +20% de probabilidad de crítico contra enemigos malditos. | Oscuridad Total |
| 181 | Forma de Sombra | legendaria | 1 | Tu definitiva te transforma 8 s: +30% de daño, +25% de velocidad, -20% de daño recibido y rastro de sombra; maldice al enemigo más sano. *(Aparece con 3 bendiciones de su categoria, piso ≥ 2)* | Oscuridad Total |
| 182 | Forma Bestial | épica | 1 | Al caer por debajo del 35% de vida te transformas 6 s: +30% de velocidad de ataque y +20% de velocidad (cada 30 s). | Sangre y Furia |
| 183 | Forma Espectral | rara | 1 | Cada parry te vuelve espectral: +25% de velocidad 3 s y maldices al enemigo más sano. | Contragolpe Perfecto, Oscuridad Total |
| 184 | Vacío Voraz | épica | 1 | Cada baja carga un 3% de tu definitiva y, al terminar la definitiva, te curas el 10%. |  |
| 185 | Corrupción | poco común | 1 | 30% de envenenar al golpear a un enemigo maldito. | Muerte Lenta, Oscuridad Total |
| 186 | Aura de Penumbra | poco común | 1 | Al rodar dejas dos charcos de sombra que maldicen a los enemigos que los pisan. | Danza Etérea, Oscuridad Total |

## J · Híbridas

| id | Bendición | Rareza | Máx. | Efecto | Sinergias |
|---|---|---|---|---|---|
| 20 | Espíritu Vengador | rara | 3 | Los enemigos explotan al morir y dañan a los cercanos. | Reacción en Cadena |
| 187 | Fuego y Rayo | rara | 1 | Los críticos contra enemigos en llamas sueltan un rayo de 2 saltos (cada 0,5 s). | Infierno, Tormenta Viva |
| 188 | Estallido Helado | rara | 1 | Golpear a un enemigo congelado: 20% de causar un estallido (70% de daño, cada 1 s). | Cripta de Hielo, Reacción en Cadena |
| 189 | Choque Térmico | épica | 1 | Golpear a un enemigo en llamas y ralentizado a la vez provoca una explosión de vapor (120% de daño, cada 2 s). | Cripta de Hielo, Reacción en Cadena |
| 190 | Conducción Tóxica | poco común | 1 | Golpear a un enemigo envenenado y electrizado provoca una explosión tóxica (80% de daño, cada 1,5 s). | Muerte Lenta, Reacción en Cadena |
| 191 | Sangre Hirviente | rara | 1 | Los enemigos que sangran y arden a la vez reciben +30% de daño. | Infierno, Muerte Lenta |
| 192 | Parry Ardiente | rara | 1 | Cada parry prende fuego a los enemigos cercanos durante 3 s. | Infierno, Contragolpe Perfecto |
| 193 | Parry Glacial | rara | 1 | Cada parry congela 1,2 s a los enemigos cercanos (los jefes solo se ralentizan). | Cripta de Hielo, Contragolpe Perfecto |
| 194 | Hechizo Certero | poco común | 1 | Tras lanzar una habilidad, +25% de probabilidad de crítico durante 5 s. | Ritmo Imparable, Hechicero Supremo |
| 195 | Toxina Crítica | poco común | 1 | +18% de probabilidad de crítico contra enemigos envenenados. | Muerte Lenta |
| 196 | Frasco Explosivo | poco común | 1 | Beber un frasco provoca una explosión a tu alrededor (150% de daño). | Reacción en Cadena, Frasco de Vida |
| 197 | Triple Filo | rara | 1 | Cada 7 golpes lanzas 3 cuchillas (50% de daño). | Artillería |
| 198 | Corazón Ardiente | poco común | 1 | Los enemigos en llamas pueden soltar un corazón al morir (cada 25 s). | Infierno |
| 199 | Convergencia Elemental | legendaria | 1 | En combate, cada 8 s un anillo de fuego y uno de hielo salen de ti y caen 2 rayos. *(Aparece con 3 bendiciones de su familia, piso ≥ 2)* |  |

