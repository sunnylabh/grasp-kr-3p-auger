#!/bin/bash
# Direct GRASP calculations for the Kr+ 2p^-1 and Kr2+ (LMM final) states:
# single-configuration levels + core CI (compact layer {5p,4d,5d,4f,5f}, from layers.sh).
# Valence CIs: val_fixed.sh / val_fix2.sh.
export PATH=~/grasp/bin:$PATH; B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd $B
source ./ci_fn.sh
LOG=$B/lmm_direct.log
./run_ion2.sh d8x "3s(2,i)3p(6,i)3d(8,i)4s(2,i)4p(6,i)" "0,8" ../d9/d9.w
# Kr2+ 3p4 + 3s1 3d9 (J=1,2 mixing): CI with the 3p4-optimised orbitals (no averaged SCF)
mkdir -p p4s; ( cd p4s && cp ../isodata . && \
  printf '*\n2\n3s(2,i)3p(4,i)3d(10,i)4s(2,i)4p(6,i)\n\n4s,4p,3d\n0,4\n0\ny\n3s(1,i)3p(6,i)3d(9,i)4s(2,i)4p(6,i)\n\n4s,4p,3d\n0,4\n0\nn\n' | rcsfgenerate > csf.log 2>&1 && \
  cp rcsf.out rcsf.inp && BL=$(awk '/block  J\/P/{f=1;next} f&&NF==3{print "1-"$3}' csf.log) && printf 'y\n' | rangular > ang.log 2>&1 && \
  cp ../p4x/p4x.w p4s.w && cp rcsf.inp p4s.c && \
  { echo y; echo p4s; echo y; echo y; echo 1.d-6; echo y; echo n; echo n; echo y; echo 4; echo "$BL"; } | rci > rci.log 2>&1 )
C=../neu_corr3/neucorr3.w; A='4s,5p,5d,5f'
ci D_c_d8   "*\n2\n3s(2,i)3p(6,i)3d(8,*)4s(2,i)4p(6,i)\n\n$A\n0,8\n2\nn\n" ../d8x/d8x.w $C 4 &
ci D_c_d9p5 "*\n2\n3s(2,i)3p(6,i)3d(9,*)4s(2,i)4p(5,i)\n\n$A\n0,8\n2\nn\n" ../d9p5/d9p5.w $C 6 &
ci D_c_p5d9 "*\n2\n3s(2,i)3p(5,i)3d(9,*)4s(2,i)4p(6,i)\n\n$A\n0,10\n2\ny\n3s(2,i)3p(6,i)3d(7,i)4s(2,i)4p(6,i)5p(1,i)\n\n$A\n0,10\n0\ny\n3s(2,i)3p(6,i)3d(7,i)4s(2,i)4p(6,i)4f(1,i)\n\n$A\n0,10\n0\ny\n3s(2,i)3p(6,i)3d(7,i)4s(2,i)4p(6,i)5f(1,i)\n\n$A\n0,10\n0\nn\n" ../p5d9/p5d9.w $C 5 &
ci D_c_p4s  "*\n2\n3s(2,i)3p(4,i)3d(10,*)4s(2,i)4p(6,i)\n\n$A\n0,4\n2\ny\n3s(1,i)3p(6,i)3d(9,*)4s(2,i)4p(6,i)\n\n$A\n0,4\n2\ny\n3s(2,i)3p(5,i)3d(8,i)4s(2,i)4p(6,i)5p(1,i)\n\n$A\n0,4\n0\ny\n3s(2,i)3p(5,i)3d(8,i)4s(2,i)4p(6,i)4f(1,i)\n\n$A\n0,4\n0\ny\n3s(2,i)3p(5,i)3d(8,i)4s(2,i)4p(6,i)5f(1,i)\n\n$A\n0,4\n0\nn\n" ../p4s/p4s.w $C 8 &
ci D_c_p2   "*\n1\n2s(2,i)2p(5,i)3s(2,i)3p(6,i)3d(10,*)4s(2,i)4p(6,i)\n\n$A\n1,3\n2\nn\n" ../p2/p2.w $C 2 &
wait
echo "LMM core CIs done $(date +%T)" >> $LOG
