#!/bin/bash
# usage: run_ion.sh <name> "<config after Ne core>" "<2Jmin,2Jmax>"
# variant of run_ion.sh: 4th argument = converged .w file used as the starting orbitals (4s-hole configs do not converge from Thomas-Fermi)
# single-configuration DHF (EOL, standard weights over all levels) + RCI (Breit, VP, SE)
set -e
export PATH=~/grasp/bin:$PATH
N=$1; CFG=$2; JR=$3
D="$(cd "$(dirname "$0")" && pwd)/$N"; mkdir -p $D; cd $D
cp ../isodata .
printf '*\n2\n%s\n\n4s,4p,3d\n%s\n0\nn\n' "$CFG" "$JR" | rcsfgenerate > csf.log 2>&1
cp rcsf.out rcsf.inp
# per-block "1-NCSF" lists (all levels of every block)
BL=$(awk '/block  J\/P/{f=1;next} f&&NF==3{print "1-"$3} f&&NF!=3&&NR>1{if(f)exit}' csf.log)
NB=$(echo "$BL" | wc -l | tr -d ' ')
printf 'y\n' | rangular > ang.log 2>&1
printf 'y\n1\n%s\n*\n' "$4" | rwfnestimate > est.log 2>&1
{ echo y; echo "$BL"; echo 5; echo '*'; echo '*'; echo 200; } | rmcdhf > scf.log 2>&1
rsave $N > /dev/null 2>&1
{ echo y; echo $N; echo y; echo y; echo 1.d-6; echo y; echo n; echo n; echo y; echo 4; echo "$BL"; } | rci > rci.log 2>&1
echo "$N: $NB blocks, iterations $(grep -c 'Iteration number' scf.log)"
rlevels $N.cm 2>&1 | awk '/^-+$/{c++;next} c==2'
