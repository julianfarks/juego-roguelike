#!/usr/bin/env bash
# Partidas reales del bot con builds (headless): cada build concede ~10 bendiciones de una familia y el bot juega N fotogramas. Una a la vez.
# Salida: lineas BUILD (progreso cada 15 s de juego) por build; se compara con el bot sin bendiciones.
RUN=${RUN:-/tmp/run2.sh}; ROOT=$(cd "$(dirname "$0")/../.." && pwd); cd "$ROOT"
F=${FRAMES:-5400}
declare -A B
B[fuego]=BRASAS,llama_voraz,brasa_critica,contagio_igneo,pira,aliento_dragon,combustion,disparo_incendiario,parry_fuego,corazon_ardiente
B[hielo]=GLACIAL,escarcha_quebradiza,esquirlas_hielo,aura_gelida,ventisca,congelacion_profunda,disparo_gelido,espiritu_hielo,explosion_hielo,choque_termico
B[electricidad]=CHISPA,carga_estatica,pararrayos,voltio_arcano,bateria,descarga_mayor,conductor,disparo_voltaico,espiritu_rayo,fuego_rayo
B[critico_velocidad]=CRITICO,ojo_halcon,impulso_letal,cadena_criticos,combo_ritmo,hoja_rapida,cadencia,rafaga_remate,sed_batalla,remate_brutal
B[parry]=contra_parry,parry_escudo,parry_ulti,eco_defensivo,parry_maestro,reflejo,parry_calma,parry_fuego,parry_hielo,pararrayos
B[escudos]=ESCUDO,EGIDA,escudo_reactivo,bastion_limpio,armadura_hierro,sangre_fria,espiritu_guardian,corazon_escudo,parry_escudo,coraza_espinas
B[proyectiles]=proyectil_explosivo,ricochet,perforante,doble_lanzamiento,punta_afilada,buscador,vuelo_veloz,onda_expansiva,lluvia_hojas,rafaga_estelar
B[esquiva]=esquiva_sagrada,danza_cuchillas,evasion_magica,segundo_aliento,sombra_veloz,fantasma,viento_cola,aura_penumbra,estela_mortal,rastro_ardiente
B[vida_baja]=rabia_herida,ultimo_bastion,sanguinario,contragolpe,supervivencia,forma_bestial,sangre_fria,sangre,furia,coraza_espinas
B[recursos]=FORTUNA,ALMA,IMAN,interes,oro_poder,cosecha_almas,almas_poder,alquimista,reserva_pociones,suerte_dorada
B[compañeros]=luciernaga,llama_fatua,espiritu_hielo,espiritu_rayo,espiritu_maldicion,espiritu_curativo,espiritu_guardian,vinculo_espiritual,sinfonia_espiritual,pastor_almas
B[hibrida_elemental]=BRASAS,GLACIAL,CHISPA,ESPINAS,marca_maldita,disparo_incendiario,disparo_gelido,disparo_voltaico,llama_fatua,espiritu_hielo
LIST=${BUILDS:-fuego hielo electricidad critico_velocidad parry escudos proyectiles esquiva vida_baja recursos compañeros hibrida_elemental}
if [ "${BOSS:-0}" = 1 ]; then   # duelo contra el jefe del bioma 0 con el bot (modo dios solo para que no muera): tiempo en derrotarlo por build
  echo "== JEFE base"; BOT_BLESSGRANT= BOT_GOD=1 BOT_WARP=boss:0 timeout 900 $RUN --headless --bot --frames $F 2>&1 | grep -E "jefe derrotado|Exception|rror"
  for k in $LIST; do echo "== JEFE build $k"; BOT_BLESSGRANT=${B[$k]} BOT_GOD=1 BOT_WARP=boss:0 timeout 900 $RUN --headless --bot --frames $F 2>&1 | grep -E "jefe derrotado|Exception|rror"; done
  exit 0
fi
echo "== base (sin bendiciones)"; timeout 900 $RUN --headless --bot --frames $F 2>&1 | grep -E "^BUILD|Exception|rror" ; BOT_BLESSGRANT=filo timeout 900 $RUN --headless --bot --frames $F 2>&1 | grep -E "^BUILD f|Exception|rror" | tail -2 | sed 's/^/base(filo) /'
for k in $LIST; do echo "== build $k"; BOT_BLESSGRANT=${B[$k]} timeout 900 $RUN --headless --bot --frames $F 2>&1 | grep -E "^BUILD|Exception|rror"; done
