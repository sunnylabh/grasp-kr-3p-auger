#!/bin/bash
# Compact 4f correlation orbital: MCDHF on the neutral ground state with 3d^2 -> 4f^2
# pair excitations (22 CSFs). Only 4f is varied; all other orbitals come from runs/neutral.
set -e; source "$(dirname "$0")/env.sh"
mkdir -p "$RUNS/neu_corr"; cd "$RUNS/neu_corr"; cp ../isodata .
printf '*\n2\n3s(2,i)3p(6,i)3d(10,*)4s(2,i)4p(6,i)\n\n4s,4p,3d,4f\n0,0\n2\nn\n' | rcsfgenerate > csf.log 2>&1
cp rcsf.out rcsf.inp
printf 'y\n' | rangular > ang.log 2>&1
printf 'y\n1\n../neutral/neutral.w\n*\n2\n*\n' | rwfnestimate > est.log 2>&1
printf 'y\n1\n5\n4f*\n\n200\n' | rmcdhf > scf.log 2>&1
rsave neucorr > /dev/null 2>&1
echo "neu_corr: $(grep -c 'Iteration number' scf.log) SCF iterations"
