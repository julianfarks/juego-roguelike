# Monetización, modo infinito y futuras integraciones

Estado: **nada de esto cobra dinero ni muestra anuncios todavía.** Lo implementado es la base local.

## Qué hay implementado (código en `core/`)
| Pieza | Archivo | Notas |
|---|---|---|
| Moneda premium (gemas moradas) | `Wallet.java` | Saldo propio (`Save.gems`), separado de almas/oro. `spend` rechaza ≤0 y saldo insuficiente; `credit` exige recibo verificado y `orderId` nuevo. |
| Guardado versionado | `Save.java` | `ver`=2. Solo se añaden claves. Copia `save_bak_v1` antes de migrar. Un guardado de versión *futura* se abre en solo lectura y no se sobrescribe. |
| Cosméticos / inventario | `Cosmetics.java`, `ShopScreen.java` | Catálogo oficial **vacío** (no hay skins reales). Fuentes: `EARNED`, `PREMIUM`, `STORE`. Artículos `[DEV]` solo con Modo Desarrollador. |
| Modo infinito | `Infinite.java`, `RunScreen.java` | Se desbloquea al vencer al Cazador. Piso = bioma completo. Resultado guardado en `Save.infLog`. |
| Revividas (máx. 3) | `Infinite.java` | 1ª anuncio o gemas, 2ª anuncio largo o gemas, 3ª solo gemas. El contador vive en `RunState`/`RunSave`. |
| Anuncios (interfaz) | `Services.java` | `AdProvider` + `requestRewardedAd`: la recompensa se da una sola vez y solo con `COMPLETED`. Proveedor por defecto: `NO_ADS`. |
| Compras (interfaz) | `Services.java`, `PurchaseReceipt.java` | `BillingProvider` + `fulfill` idempotente. Proveedor por defecto: `NO_BILLING`. |

## Cómo conectar AdMob / Play Billing (cuando se decida)
El proyecto real es **Java/Android** (no Python/Pygame), así que se usa el SDK nativo directamente:
1. En `app/build.gradle` añadir `com.google.android.gms:play-services-ads` (y `com.android.billingclient:billing`). Comprobar compatibilidad con `minSdk`/`targetSdk` actuales.
2. Escribir un adaptador en `app/src/main/java/com/julianfarks/roguelike/android/` que implemente `Services.AdProvider` / `Services.BillingProvider`.
3. Asignarlo al arrancar: `Services.ads = new AdMobProvider(...)`. No hay que tocar revividas ni recompensas.
4. AdMob: usar IDs de prueba hasta publicar; llamar al callback `COMPLETED` solo en `onUserEarnedReward`.
5. Billing: consumir/confirmar la compra **solo después** de que el servidor la verifique; crear `PurchaseReceipt(orderId, productId, gemas, verified=true)` y llamar `Services.fulfill`.

## Límites de seguridad (importante)
- El saldo premium está en el almacenamiento local: **se puede editar** en un teléfono con acceso al archivo. Para dinero real hace falta que el saldo y las compras se validen en un servidor.
- El registro de resultados lleva una suma de control (`chk`) solo para detectar ediciones torpes; **no es seguridad**.
- Una clasificación con premios reales necesita servidor: validar resultados (semilla + reglas + versión), fechas de inicio/cierre, y reglas uniformes (`Infinite.COMPETITIVE`: sin revividas compradas).

## Decisiones de diseño pendientes (no inventadas)
- Nombre definitivo de la moneda premium y precios de los paquetes.
- Coste en gemas de las revividas (`Infinite.GEM_COST = {5,10,15}` es provisional).
- Fórmula de puntaje y escalado de dificultad del infinito (`Infinite.score`, `power`, `bossHpMul`, `eliteChance`): ajustar tras probar equilibrio.
- Reglas exactas del modo competitivo.
- Primeras skins reales (sprites) y su precio/fuente.

## Publicación
`applicationId` = `com.julianfarks.roguelike` (no cambiar). Subir `versionCode` en cada versión publicada. La firma de lanzamiento debe guardarse como *secret* de GitHub, nunca en el repositorio.
