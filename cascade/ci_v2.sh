#!/bin/bash
# usage: ci_v2.sh <tag> "<config, 4s 4p active, 3d inactive>" <2Jrange> <core .w> <nroots> <L1|L12>
set -e; export PATH=~/grasp/bin:$PATH; B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
T=$1; CFG=$2; JR=$3; CORE=$4; NR=$5; L=$6
if [ $L = L1 ]; then AS='5s,5p,4d,4f'; W=../val_neu/valneu.w; else AS='6s,6p,5d,5f'; W=../val2_neu/val2neu.w; fi
mkdir -p $B/v${L}_$T; cd $B/v${L}_$T; cp $B/isodata .
printf '*\n2\n%s\n\n%s\n%s\n2\nn\n' "$CFG" "$AS" "$JR" | rcsfgenerate > csf.log 2>&1
cp rcsf.out rcsf.inp
BL=$(awk -v n=$NR '/block  J\/P/{f=1;next} f&&NF==3{m=($3<n)?$3:n; print "1-"m}' csf.log)
printf 'y\n' | rangular > ang.log 2>&1
printf 'y\n1\n%s\n*\n1\n%s\n*\n' "$CORE" "$W" | rwfnestimate > est.log 2>&1
cp rwfn.inp $T.w; cp rcsf.inp $T.c
{ echo y; echo $T; echo y; echo y; echo 1.d-6; echo y; echo n; echo n; echo y; echo 4; echo "$BL"; } | rci > rci.log 2>&1
echo "$T $L: $(awk '/block  J\/P/{f=1;next} f&&NF==3{s+=$3} END{print s}' csf.log) CSFs"
