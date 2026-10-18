#!/usr/bin/env bash
# Auditoria de encaje de textos: PrepScreen (10 clases x 3 bendiciones x companeros), ficha de espadachines, trofeos, jardin,
# en es/en/fr/zh y anchos 480/640. Cada texto que no cabe en su zona imprime "FIT ..."; la prueba falla si hay alguno o excepciones.
set -u
cd "$(dirname "$0")/../.."
RUN=/tmp/run2.sh; [ -x "$RUN" ] || RUN=PC/run.sh
T=${TMPDIR:-/tmp}/layout_audit; mkdir -p $T
fails=0
run() { # lang width names tag
  local L=$1 W=$2 N=$3 TAG=$4 i=0 F=$T/$4.script; : > $F
  IFS=, read -ra A <<< "$N"; for n in "${A[@]}"; do echo "$((i*60+40)) shot ${i}_${n//:/_}" >> $F; i=$((i+1)); done
  BOT_LANG=$L BOT_SHOW=$N BOT_NOSTART=1 timeout 900 $RUN --headless --bot --w $W --frames $((i*60+60)) --script $F --shots $T/$TAG --store $T/$TAG.json > $T/$TAG.log 2>&1
  local e=$(grep -c EXCEPTION $T/$TAG.log) f=$(grep -c '^FIT' $T/$TAG.log)
  if [ "$e" = 0 ] && [ "$f" = 0 ]; then echo "ok   $TAG"; else echo "FAIL $TAG (excepciones=$e, desajustes=$f)"; grep '^FIT' $T/$TAG.log | sort -u | head -5; fails=$((fails+1)); fi
}
PREP=""; for c in 0 1 2 3 4 5 6 7 8 9; do for p in 0 1 2; do PREP="$PREP,prep:$c:$((c%8)):$(((c+3)%8)):$(((c+5+p)%8)):$p:$(((c+p)%4-1))"; done; done; PREP=${PREP#,}
CLS=""; for c in 0 1 2 3 4 5 6 7 8 9; do CLS="$CLS,class:$c"; done; CLS=${CLS#,}
for L in 0 1 2 3; do
  for W in 480 640; do run $L $W $PREP prep_${L}_$W; done
  run $L 480 $CLS class_$L
  run $L 480 trophy,garden,options,comp,stats,retos,codex,title misc_$L
done
[ $fails -eq 0 ] && echo "layout_audit OK" || echo "layout_audit FALLOS: $fails"
exit $fails
