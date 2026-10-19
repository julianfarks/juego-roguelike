# Actualización de gameplay: combate, eventos de riesgo y HUD

Todas las pruebas son **automáticas en el banco headless del motor** (Java, render real de `DesktopGfx`). **No se probó en un móvil Android ni en hardware Windows real.**

## Etapa 1 · Sensación de combate
- `Impact.java` (nuevo): respuesta central por tipo de golpe (ligero / pesado / crítico / especial): pausa de impacto, sacudida, chispas, volumen y tono propios. Los jefes reciben la mitad de pausa.
- Pausa de impacto (`Level.update`): no congela nunca (presupuesto ≤ 0,30 s por segundo) y **no pierde pulsaciones** (`Input.keep`); el menú de pausa se abre durante una pausa.
- Enemigos: retroceso y duración de aturdimiento distintos según el golpe; se detienen exactamente al acabar el aturdimiento (sin deslizarse).
- Parry perfecto (ventana, cámara lenta, destello), bloqueo normal distinto, esquiva perfecta, **ventana de contraataque** (+50 % y desequilibra) y **racha defensiva** (3 acciones precisas → «Ritmo» +12 % de velocidad de ataque 5 s).
- Números de daño legibles (contorno, se fusionan, desplazados en jefes).
- Opción **Efectos intensos: REDUCIDOS/NORMALES** (opciones y pausa): reduce sacudida, destellos, pausa de impacto, partículas y cámara lenta.

## Etapa 2 · Eventos y decisiones (reutilizan `Events`, `OV_EVENT`, bendiciones, cofres y puertas laterales)
- **Altar de riesgo** (4 decisiones, con ventaja y coste visibles antes de aceptar): sangre por bendición (−25 % vida máx., 1 de 3), dolor por botín (golpe del 18 %, oro y almas), Pacto del Ayuno (+20 % daño, −2 frascos; cuenta como pacto) y almas por elección (1 de 4 bendiciones). No consume la bendición de altar del bioma.
- **Cofre maldito**: abrirlo provoca una emboscada (3 + piso enemigos, uno de élite) sin salida hasta vencer; premio: 2 cofres de elección + almas. Se puede dejar cerrado.
- **Sala de desafío** (4 variantes según la partida): sin recibir daño, contrarreloj (40 s), resistencia (30 s con oleadas) y curación reducida (−60 %). Premio: 2 cofres + almas; si se incumple, sin premio pero la salida siempre aparece.
- Variedad: el peso de cada suceso se reduce a la mitad cada vez que ya salió en la run; máximo 2 de cada nuevo; uno por bioma.
- Mercader errante (ya existente, inventario aleatorio de 3 objetos): se comprobó que entrar/salir no reinicia el piso.
- Guardado: `chalK` (variante del desafío) en `RunSave`; arrays de sucesos con lectura tolerante a la longitud (partidas antiguas siguen cargando).

## Etapa 3 · HUD
- Habilidades: aro claro cuando están listas, icono atenuado en reutilización, tiempo con un decimal bajo 3 s y fondo de contraste, **señal breve** al quedar lista (una sola vez). Los botones no cambian de sitio.
- Vida: texto dentro de la barra con fondo (y «!» con vida baja, no solo color); jefe con % numérico.
- Estados: barrita de duración bajo cada icono; indicadores de Ritmo y de ventana de contraataque; los enemigos muestran como mucho 3 iconos de estado.
- Sinergias: color según el tipo (fuego, hielo, electricidad, parry, veneno/sangrado, crítico); el nombre sale **una vez** (al activarla y al primer disparo), no en cada proc.
- Auditoría de textos (`PrepScreen.fitErr`) en 4 idiomas × 480/640 px, sala y jefe.

## Pruebas (`tools/tests/`)
| Script | Cubre |
|---|---|
| `combat_test.sh` | tipos de golpe, entradas durante la pausa, parry/esquiva/racha, jefes |
| `events_test.sh` | altar, cofre maldito, desafíos, reparto/variedad, ruta, guardado, mercader, textos 4 idiomas |
| `hud_test.sh` | tiempos de reutilización, señal de lista, sinergias sin repetición, estados, textos |
| `perf_stress_test.sh`, `ai_hazard_test.sh`, `layout_audit.sh`, `nav_regression.sh`, `bless_test.sh` | regresión previa |

## Limitaciones
- Sin pruebas en dispositivos reales (Android/Windows); solo banco headless.
- Las rutas «más peligrosa/más segura» se cubren con las puertas laterales de sucesos; no hay un mapa de rutas nuevo.
- El audio de los golpes se diferencia por volumen/tono (se reutilizan los mismos sonidos).
