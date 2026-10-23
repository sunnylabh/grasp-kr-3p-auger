#!/bin/bash
# Single-configuration DHF + RCI for one ion.
# usage: run_ion.sh <name> "<configuration outside the Ne core>" "<2Jmin,2Jmax>"
# DHF: extended optimal level (EOL) over all levels, standard (2J+1) weights.
# RCI: transverse photon (Breit, frequency factor 1e-6), vacuum polarisation, self-energy (n<=4).
set -e; source "$(dirname "$0")/env.sh"
N=$1; CFG=$2; JR=$3
mkdir -p "$RUNS/$N"; cd "$RUNS/$N"; cp ../isodata .
printf '*\n2\n%s\n\n4s,4p,3d\n%s\n0\nn\n' "$CFG" "$JR" | rcsfgenerate > csf.log 2>&1
cp rcsf.out rcsf.inp
BL=$(awk '/block  J\/P/{f=1;next} f&&NF==3{print "1-"$3}' csf.log)
printf 'y\n' | rangular > ang.log 2>&1
printf 'y\n2\n*\n' | rwfnestimate > est.log 2>&1
{ echo y; echo "$BL"; echo 5; echo '*'; echo '*'; echo 200; } | rmcdhf > scf.log 2>&1
rsave "$N" > /dev/null 2>&1
{ echo y; echo "$N"; echo y; echo y; echo 1.d-6; echo y; echo n; echo n; echo y; echo 4; echo "$BL"; } | rci > rci.log 2>&1
echo "$N: $(grep -c 'Iteration number' scf.log) SCF iterations"
