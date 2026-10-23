#!/bin/bash
# Single-configuration DHF + RCI (Breit, VP, SE; run_ion_base.sh recipe) for the Kr4+, Kr5+ and Kr6+
# configurations of the later cascade steps (Kr3+ -> Kr4+ -> Kr5+ -> Kr6+). Used for the GRASP energies
# of the Kr3+ -> Kr4+ electrons in the coincidence-data overlays. Run after final_states.sh.
# A run that does not converge from Thomas-Fermi starting orbitals is repeated with run_ion2.sh,
# seeded with the orbitals of a converged neighbour (needed for several 4s-hole configurations).
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd "$B"
run() {   # name config 2Jmin,2Jmax seed.w
  rm -rf "$1"; ./run_ion_base.sh "$1" "$2" "$3" > "$1.out" 2>&1
  if [ ! -s "$1.out" ] || grep -qi 'convergence not' "$1/scf.log"; then
    rm -rf "$1"; ./run_ion2.sh "$1" "$2" "$3" "$4" > "$1.out" 2>&1; echo "$1: reran seeded from $4"
  fi
  echo "$1: $(head -1 "$1.out")"
}
# Kr4+ (parents of the Kr4+ -> Kr5+ step and finals of Kr3+ 3p-1 3d-1 4p-1 / 3d-2 4p-1 decay)
run d8p4      "3s(2,i)3p(6,i)3d(8,i)4s(2,i)4p(4,i)"  "0,12" ../d9p5/d9p5.w
run d8sp5     "3s(2,i)3p(6,i)3d(8,i)4s(1,i)4p(5,i)"  "0,12" ../d8p4/d8p4.w
run d9p3      "3s(2,i)3p(6,i)3d(9,i)4s(2,i)4p(3,i)"  "0,10" ../d8p4/d8p4.w
run d9sp4     "3s(2,i)3p(6,i)3d(9,i)4s(1,i)4p(4,i)"  "0,10" ../d9p3/d9p3.w
run d9s0p5    "3s(2,i)3p(6,i)3d(9,i)4s(0,i)4p(5,i)"  "0,8"  ../d9p3/d9p3.w
run d8s0      "3s(2,i)3p(6,i)3d(8,i)4s(0,i)4p(6,i)"  "0,8"  ../d8p4/d8p4.w
run v4_p2     "3s(2,i)3p(6,i)3d(10,i)4s(2,i)4p(2,i)" "0,4"  ../d9p3/d9p3.w
run v4_sp3    "3s(2,i)3p(6,i)3d(10,i)4s(1,i)4p(3,i)" "0,6"  ../d9p3/d9p3.w
run v4_s0p4   "3s(2,i)3p(6,i)3d(10,i)4s(0,i)4p(4,i)" "0,4"  ../d9p3/d9p3.w
# Kr5+
run k5_d9p2   "3s(2,i)3p(6,i)3d(9,i)4s(2,i)4p(2,i)"  "1,9"  ../d9p3/d9p3.w
run k5_d9sp3  "3s(2,i)3p(6,i)3d(9,i)4s(1,i)4p(3,i)"  "1,11" ../d9p3/d9p3.w
run k5_d9s0p4 "3s(2,i)3p(6,i)3d(9,i)4s(0,i)4p(4,i)"  "1,9"  ../d9p3/d9p3.w
run k5_p1     "3s(2,i)3p(6,i)3d(10,i)4s(2,i)4p(1,i)" "1,3"  ../d9p3/d9p3.w
run k5_sp2    "3s(2,i)3p(6,i)3d(10,i)4s(1,i)4p(2,i)" "1,5"  ../d9p3/d9p3.w
run k5_p3     "3s(2,i)3p(6,i)3d(10,i)4s(0,i)4p(3,i)" "1,5"  ../d9p3/d9p3.w
# Kr6+
run k6_s2     "3s(2,i)3p(6,i)3d(10,i)4s(2,i)4p(0,i)" "0,0"  ../k5_p1/k5_p1.w
run k6_sp     "3s(2,i)3p(6,i)3d(10,i)4s(1,i)4p(1,i)" "0,4"  ../k5_p1/k5_p1.w
run k6_p2     "3s(2,i)3p(6,i)3d(10,i)4s(0,i)4p(2,i)" "0,4"  ../k5_p1/k5_p1.w
