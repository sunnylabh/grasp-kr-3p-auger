#!/bin/bash
# usage: ci_val.sh <tag> "<SD reference config>" <2Jrange> <core .w> <nroots>
# CSFs: SD from 4s,4p (3d at most one) into {5s,5p,4d,4f}; orbitals: core from <core .w>, layer from val_neu.
set -e; export PATH=~/grasp/bin:$PATH; B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
T=$1; CFG=$2; JR=$3; CORE=$4; NR=$5
mkdir -p $B/ci_$T; cd $B/ci_$T; cp $B/isodata .
printf '*\n1\n%s\n\n5s,5p,4d,4f\n%s\n2\nn\n' "$CFG" "$JR" | rcsfgenerate > csf.log 2>&1
cp rcsf.out rcsf.inp
BL=$(awk -v n=$NR '/block  J\/P/{f=1;next} f&&NF==3{m=($3<n)?$3:n; print "1-"m}' csf.log)
printf 'y\n' | rangular > ang.log 2>&1
printf 'y\n1\n%s\n*\n1\n../val_neu/valneu.w\n*\n' "$CORE" | rwfnestimate > est.log 2>&1
cp rwfn.inp $T.w; cp rcsf.inp $T.c
{ echo y; echo $T; echo y; echo y; echo 1.d-6; echo y; echo n; echo n; echo y; echo 4; echo "$BL"; } | rci > rci.log 2>&1
echo "$T: $(awk '/block  J\/P/{f=1;next} f&&NF==3{s+=$3} END{print s}' csf.log) CSFs"
