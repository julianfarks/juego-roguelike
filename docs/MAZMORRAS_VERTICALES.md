# Mazmorras verticales

Salas de combate con arquetipo por bioma (`Vertical.TABLE`): **compacta** (como antes), **alta** (suelo + piso 1 + piso 2 + subsuelo 1) y **profunda** (+ torre y subsuelo 2).

- Alturas: 30 / 43 / 58 filas. Cada nivel tiene función: galerías con puente roto, escalera de plataformas, torre con cámara secreta, túneles bajo el suelo.
- Rutas: pozos de bajada y subida al subsuelo (bucle y atajo), alcoba tras muro agrietado (cofre secreto), subsuelo 2 con alcoba opcional.
- Enemigos: cuotas por altura, voladores en el aire, guardias junto a cofres; los de zonas opcionales (torre, subsuelo 2, alcobas) no cuentan para despejar la sala (`Spawn.optional`). Sin reaparición.
- Validación: `RoomCheck.reachTall` (modelo de alcance estricto) + `Vertical.validate`; si falla tras varios intentos cae a sala compacta.
- Pruebas: `bash tools/tests/vert_test.sh N` (generación, alcance, ≥15 enemigos obligatorios por mazmorra de 3 salas); `VertDump bioma arq semilla` dibuja el mapa ASCII.
- Límites: sin plataformas móviles, ascensores ni llaves; la auditoría física del salto no está escrita (solo el modelo de alcance).
