#!/bin/bash
# Failed approach, kept for reference: optimise 4f directly on the 3p^-1 roots
# (root 8 of J=1/2, root 7 of J=3/2) of the 3p5 + 3d8 4f expansion. The 3d^-2 4f states lie
# just below 3p^-1, so the targeted roots flip to pure 3d^-2 4f states during the SCF
# (3p occupation returns to 6). rmcdhf has no root tracking.
set -e; source "$(dirname "$0")/env.sh"
mkdir -p "$RUNS/p5_rootflip"; cd "$RUNS/p5_rootflip"; cp ../isodata .
cp ../p5_ci/rcsf.inp .
printf 'y\n' | rangular > ang.log 2>&1
printf 'y\n1\n../p5/p5.w\n*\n2\n*\n' | rwfnestimate > est.log 2>&1
printf 'y\n1-8\n1-14\n5\n4f*\n*\n100\n' | rmcdhf > scf_eol.log 2>&1      # 4f on all levels
cp rwfn.out rwfn.inp
printf 'y\n8\n7\n5\n4f*\n\n200\n' | rmcdhf > scf_root.log 2>&1         # 4f on the 3p roots
grep -A3 'Generalised occupation' scf_root.log | tail -3
