#!/bin/bash
# Full eigenvectors for the overlap analysis (overlap.py): cut-off 0 for single-configuration runs, 0.03 for CIs.
export PATH=~/grasp/bin:$PATH; B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd $B
x() { ( cd $1 && printf "0\n$2\ny\n$3\nn\n" | rmixextract > rmx.log 2>&1 ); }
( printf "0\np5\ny\n0.0\nn\n" | rmixextract > rmx_p5.log 2>&1 )
for d in p2 d8x p5d9 p4x d9p5 d9sp d9p4 d9s0 sp4 s0p5 p3 d8p5 d8s1 pds pdp d9 p4 np5; do [ -d $d ] && x $d $d 0.0; done
for d in W_p2 W_d8 W_p5d9 W_p4 W_d9p5 W_p5 W_d9 F_v_d9sp F_v_d9p4 F_v_d9s0 F_v_sp4 F_v_s0p5 F_v_p3 F_v_d8p5 F_v_d8s1 F_v_pds F_v_pdp; do [ -d $d ] && x $d $d 0.03; done
x vL1_p4 p4 0.03; x vL1_np5 np5 0.03
