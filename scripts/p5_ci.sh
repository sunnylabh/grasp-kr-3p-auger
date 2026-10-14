#!/bin/bash
# Kr+ 3p^-1 with the 3p^-1 <-> 3d^-2 4f interaction (super-Coster-Kronig fluctuation).
# CSFs: 3p5 3d10 4s2 4p6 + 3p6 3d8 4s2 4p6 4f (8 CSFs J=1/2, 14 CSFs J=3/2).
# Orbitals: core from runs/p5, 4f from runs/neu_corr; RCI only (no orbital optimisation),
# with the same Breit/QED settings as run_ion.sh.
set -e; source "$(dirname "$0")/env.sh"
mkdir -p "$RUNS/p5_ci"; cd "$RUNS/p5_ci"; cp ../isodata .
printf '*\n2\n3s(2,i)3p(5,i)3d(10,i)4s(2,i)4p(6,i)\n\n4s,4p,3d,4f\n1,3\n0\ny\n3s(2,i)3p(6,i)3d(8,i)4s(2,i)4p(6,i)4f(1,i)\n\n4s,4p,3d,4f\n1,3\n0\nn\n' | rcsfgenerate > csf.log 2>&1
cp rcsf.out rcsf.inp
printf 'y\n' | rangular > ang.log 2>&1
printf 'y\n1\n../p5/p5.w\n*\n1\n../neu_corr/neucorr.w\n4f*\n' | rwfnestimate > est.log 2>&1
cp rwfn.inp p5ci.w; cp rcsf.inp p5ci.c
printf 'y\np5ci\ny\ny\n1.d-6\ny\nn\nn\ny\n4\n1-8\n1-14\n' | rci > rci.log 2>&1
echo "p5_ci: done"
