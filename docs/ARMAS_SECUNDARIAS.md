# Armas secundarias: representación visual, recarga y pasivas

Pruebas: banco headless (no dispositivo real Android/Windows). `tools/tests/arsenal_test.sh` (BOT_ARSENAL=1).

## Representación visual
- Con la secundaria **elegida** (arma realmente equipada + seleccionada; no depende del icono de la interfaz) la espada de la clase se dibuja **guardada a la espalda**
  y el cuerpo usa filas sin arma; la secundaria se dibuja **en la mano** (ancla `hand` por fotograma) con su postura propia y siguiendo reposo / carrera / salto / caída.
- Al elegir la principal, la espada vuelve a la mano (cambio suave: `Player.secView`, destello de cambio existente).
- Estados con fotogramas propios de la clase (rodar, daño, bloqueo, habilidades, definitiva, esperas AFK) conservan su dibujo original: en ellos no se dibuja la secundaria,
  así nunca hay dos armas ni armas flotantes.
- Hojas: `tools/art/make_unarmed.py` añade filas 14–21 (`<anim>_u` sin arma y `<anim>_s` espada guardada) a `pl_<clase>.png/json` sin tocar las filas originales.
  `tools/art/make_weapons.py` genera `wpn_hold.png/json` (36 armas en mano) y los iconos que falten.
- `WeaponView.java` dibuja el arma, poses de golpe por tipo (tajo, estocada, barrido, mazazo, látigo, puñetazo, cadena, zarpazo), retroceso al disparar, gesto de lanzamiento,
  pulso de armas flotantes, pose de recarga y estelas (reducidas con `reduceFx`).

## Recarga y munición
| Tipo | Armas | Regla |
|---|---|---|
| Cargador + reserva | Ballesta rúnica (3, recarga 1.0 s), Cañón de brasas (5, 1.2 s) | Al llegar el cargador a 0 con reserva, recarga **sola** (el arma sigue equipada y seleccionada); no dispara mientras recarga |
| Energía que se regenera | Varitas, Orbe oscuro, Catalizador, Cetro de sangre, Cristal, Talismán | Una carga cada cierto tiempo (hasta el máximo); sin carga no dispara |
| Reserva finita | Resto a distancia | Sin cargador; al agotarse vuelve a la principal |
| Munición ilimitada | Cuerpo a cuerpo | Sin recarga artificial |
- El cargador se conserva al cambiar de arma, entre salas y en el guardado (`secMag`, compatible con partidas antiguas). Cambiar de arma no regala munición ni acorta la recarga.

## Armas nuevas (26) y pasivas
Todas las pasivas tienen tope: cargas acotadas por estado (menos en élites/jefes), aturdimiento con enfriamiento por objetivo y resistencias de jefe (los jefes no se congelan ni se interrumpen).

Cuerpo a cuerpo rápido: **Cuchillos dobles** (precisión +8%/golpe, máx 5) · **Dagas gemelas** (sangrado ≤4, golpe delante y detrás) · **Estiletes** (+18% crítico, los críticos sangran) ·
**Garras mágicas** (marca arcana; 3 marcas = estallido y devuelve 1 carga con enfriamiento) · **Tonfas** (interrumpe 0.5 s) · **Guanteletes** (3er golpe seguido pesado +40% y empuje).
Cuerpo a cuerpo medio: **Lanza** (alcance, atraviesa 3) · **Alabarda** (alcance alto, interrumpe 0.6 s) · **Guadaña** (barrido, sangrado, cura 2.5% al abatir con enfriamiento) ·
**Látigo** (mayor alcance, atrae y ralentiza) · **Cadena con hoja** (doble impacto ida y vuelta) · **Espada corta** (ritmo: 3 golpes aceleran el siguiente) · **Martillo de combate** (aturde 0.8 s, onda de impacto).
A distancia: **Dagas arrojadizas** (precisión; si fallan regresan y se devuelve la munición) · **Shurikens** (veneno ≤3, atraviesan 1) · **Bombas alquímicas** (quemadura ≤3, área) · **Bombas adhesivas** (se pegan, estallan a 1 s, ralentizan).
Mágicas: **Varita elemental** (ciclo fuego → hielo → rayo → nova) · **Varita de fuego** (quemadura ≤3) · **Varita de hielo** (frío acumulable; 3ª carga congela 1 s con inmunidad posterior) ·
**Varita eléctrica** (cadena a 2 enemigos, 55%) · **Orbe oscuro** (maldición +12% daño recibido 4 s) · **Catalizador de veneno** (veneno ≤5, nube) · **Cetro de sangre** (sangrado ≤4, roba 3% con límite) ·
**Cristal arcano** (marca arcana) · **Talismán explosivo** (se adhiere, estalla a 0.9 s, aturde 0.4 s a no jefes).

## Código
`Wpn.java` (catálogo y definiciones), `Melee.java` (golpes), `WeaponFx.java` (pasivas/estados), `WeaponView.java` (dibujo), `Arsenal.java` (recarga, disparo, regeneración, bombas adhesivas, dagas que regresan),
`Items.java`/`ArsenalUI.java`/`RunScreen.java`/`Inventory.java` (datos y HUD derivados del catálogo), `RunState/RunSave` (`secMag`).
