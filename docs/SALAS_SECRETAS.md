# Salas secretas rediseñadas

Antes, el suelo agrietado dejaba ver la cámara y el cofre desde fuera (`docs/capturas_secretas/01_antes_despues_suelo.png`).
Ahora una cámara secreta es un sistema con **entrada**, **reto** y **recompensa** elegidos al generar la sala.

## Cómo se oculta
* `Room.bake` hornea **dos** imágenes: `baked` (todo el recuadro de la cámara como roca maciza) y `bakedOpen` (con el interior).
  Mientras está cerrada solo se dibuja `baked`; el hueco, las antorchas y la recompensa (`Prop.hidden`) no se ven.
* Al descubrirla (`Secrets.reveal`): la losa se aparta, caen piedras y polvo, tiembla la pantalla y `bakedOpen` aparece en fundido.
* Baldosas nuevas: `HWALL` (pared hueca, sólida) y `FAKE` (pared/suelo ilusorio, atravesable). `RoomCheck` las trata como sólida/libre.

## Entradas (coherentes con el bioma)
| Entrada | Cómo se abre |
|---|---|
| Suelo agrietado | romperlo (grietas casi invisibles, crecen con cada golpe) |
| Pared hueca | golpearla 3 veces (grietas sutiles) |
| Pared ilusoria | acercarse (destello tenue en el muro) |
| Cascada (agua / hielo / lava / sangre según bioma) | atravesarla |
| Cortina (colores por bioma) | atravesarla |
| Estatua | golpearla 4 veces, se desmorona |
| Palanca oculta | golpearla |
| Símbolos | golpear 3 piedras en el orden de la tablilla (el error reinicia) |
| Runas | memorizar la secuencia que se ilumina y repetirla |
| Cristal de habilidad | usar una habilidad cerca (todos los personajes tienen) |

## Retos y recompensas
* Retos: ninguno, **sección de plataformas con suelo de pinchos**, **guardián opcional** (la recompensa aparece al vencerlo; no cuenta para despejar la sala).
* Recompensas: cofre secreto, **cofre superior** (doble botín, más suerte), **reliquia**, **sala del tesoro** (lluvia de oro y almas), **santuario de pactos** (elección ventaja/precio), **provisiones**.
* Más mecanismo y reto → recompensa mejor (`SecretGen.rollReward`).

## Integración con la generación
`SecretGen.build` solo acepta una cámara si, con `RoomCheck` (modelo de saltos): la ruta principal sigue alcanzable cerrada y abierta, los
interruptores están en suelo alcanzable, la recompensa es alcanzable y se puede volver a salir. No hay apariciones, trampas ni props ajenos
dentro del recuadro. Si no cabe, la sala se queda sin cámara (nunca una cámara imposible o visible).

## Pruebas
* `tools/tests/SecretGenTest.java`: 2700 salas (9 biomas), ~1000 cámaras: alcanzabilidad, volver a salir, nada filtrado, variedad.
* `BOT_SECTEST` (+ `BOT_SECRET=familia:entrada:recompensa:reto`, `BOT_SECREAL=1` para ataques reales): secuencia de escritorio
  cerrada → descubrimiento → abierta → recompensa, con capturas en `docs/capturas_secretas/`.
* Solo se ha probado en el simulador de escritorio (no en un móvil Android real).
