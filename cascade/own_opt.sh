#!/bin/bash
# usage: own_opt.sh <tag> "<config, 4s4p active, 3d inactive>" <2Jrange> <start .w> "<blocklist>"
# MCDHF with layer {5s,5p,4d,4f} optimised on the state itself (layer by layer), then RCI (Breit+QED)
set -e; export PATH=~/grasp/bin:$PATH; B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
T=$1; CFG=$2; JR=$3; W=$4; BL=$5
mkdir -p $B/own_$T; cd $B/own_$T; cp $B/isodata .
printf '*\n2\n%s\n\n5s,5p,4d,4f\n%s\n2\nn\n' "$CFG" "$JR" | rcsfgenerate > csf.log 2>&1; cp rcsf.out rcsf.inp
printf 'y\n' | rangular > ang.log 2>&1
printf 'y\n1\n%s\n*\n1\n../val_neu/valneu.w\n*\n' "$W" | rwfnestimate > est.log 2>&1
for step in "4d*" "5s*,5p*" "4f*" "5s*,5p*,4d*,4f*"; do
  L=scf_$(echo $step|tr -d '*,').log; cp rwfn.inp rwfn.bak
  { echo y; echo "$BL"; echo 5; echo "$step"; echo; echo 200; } | rmcdhf > $L 2>&1
  if grep -q "NaN\|Error" $L; then echo "  $T $step failed"; cp rwfn.bak rwfn.inp; else cp rwfn.out rwfn.inp; fi
done
cp rwfn.inp $T.w; cp rcsf.inp $T.c
{ echo y; echo $T; echo y; echo y; echo 1.d-6; echo y; echo n; echo n; echo y; echo 4; echo "$BL"; } | rci > rci.log 2>&1
echo "$T: $(awk '/block  J\/P/{f=1;next} f&&NF==3{s+=$3} END{print s}' csf.log) CSFs"
