#!/bin/bash
# Single-configuration DHF + RCI for Kr4+ parents and Kr5+ finals (cross-check of FAC energetics)
cd "$(dirname "${BASH_SOURCE[0]}")"
[ -f isodata ] || cp ../kr3p_hole/runs/isodata .   # Kr-84 nucleus written by kr3p_hole/run_all.sh
R() { ./run_ion.sh "$1" "$2" "$3" > "$1.out" 2>&1 || echo "$1 FAILED"; }
# 4s-hole configurations that do not converge from Thomas-Fermi orbitals: start from a converged neighbour
S() { rm -rf "$1"; ./run_ion_start.sh "$1" "$2" "$3" "$4" > "$1.out" 2>&1 || echo "$1 FAILED"; }
R q4_d8p4   "3s(2,i)3p(6,i)3d(8,i)4s(2,i)4p(4,i)"  "0,12" &
R q4_d9sp4  "3s(2,i)3p(6,i)3d(9,i)4s(1,i)4p(4,i)"  "0,10" &
R q4_d9p3   "3s(2,i)3p(6,i)3d(9,i)4s(2,i)4p(3,i)"  "0,8" &
wait
R q5_d9p2   "3s(2,i)3p(6,i)3d(9,i)4s(2,i)4p(2,i)"  "1,9" &
R q5_d9sp3  "3s(2,i)3p(6,i)3d(9,i)4s(1,i)4p(3,i)"  "1,9" &
R q5_d8p3   "3s(2,i)3p(6,i)3d(8,i)4s(2,i)4p(3,i)"  "1,11" &
wait
R q5_p1     "3s(2,i)3p(6,i)3d(10,i)4s(2,i)4p(1,i)" "1,3" &
R q5_sp2    "3s(2,i)3p(6,i)3d(10,i)4s(1,i)4p(2,i)" "1,5" &
R q5_p3     "3s(2,i)3p(6,i)3d(10,i)4s(0,i)4p(3,i)" "1,3" &
wait
S q4_d8sp5  "3s(2,i)3p(6,i)3d(8,i)4s(1,i)4p(5,i)"  "0,12" ../q4_d8p4/q4_d8p4.w
S q5_d9p4   "3s(2,i)3p(6,i)3d(9,i)4s(0,i)4p(4,i)"  "1,9"  ../q5_d9p2/q5_d9p2.w
echo ALL DONE
