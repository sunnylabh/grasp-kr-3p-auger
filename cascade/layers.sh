#!/bin/bash
# Setup for the cascade calculations: nucleus, single-configuration reference runs, correlation layers
# (all optimised on the neutral ground state) and the single-hole core/valence CIs.
set -e; export PATH=~/grasp/bin:$PATH; B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd $B
printf '36\n84\nn\n83.9115\n0\n0\n0\n' | rnucleus > rnucleus.log 2>&1                      # 84Kr
# --- single-configuration references (DHF EOL + RCI Breit/VP/SE)
./run_ion_base.sh neutral "3s(2,i)3p(6,i)3d(10,i)4s(2,i)4p(6,i)" "0,0"
./run_ion_base.sh p5_sc   "3s(2,i)3p(5,i)3d(10,i)4s(2,i)4p(6,i)" "1,3"; cp p5_sc/p5_sc.w p5.w; cp p5_sc/p5_sc.c p5.c
( cd p5_sc && for x in cm csum; do cp p5_sc.$x ../p5.$x; done )
./run_ion_base.sh d9p5    "3s(2,i)3p(6,i)3d(9,i)4s(2,i)4p(5,i)"  "0,8"
./run_ion_base.sh np5     "3s(2,i)3p(6,i)3d(10,i)4s(2,i)4p(5,i)" "1,3"
./run_ion_base.sh d9      "3s(2,i)3p(6,i)3d(9,i)4s(2,i)4p(6,i)"  "3,5"
./run_ion_base.sh p4      "3s(2,i)3p(6,i)3d(10,i)4s(2,i)4p(4,i)" "0,4"
./run_ion2.sh p5d9 "3s(2,i)3p(5,i)3d(9,i)4s(2,i)4p(6,i)"  "0,10" ../neutral/neutral.w
./run_ion2.sh p4x  "3s(2,i)3p(4,i)3d(10,i)4s(2,i)4p(6,i)" "0,4"  ../neutral/neutral.w
./run_ion2.sh s1   "3s(2,i)3p(6,i)3d(10,i)4s(1,i)4p(6,i)" "1,1"  ../neutral/neutral.w
./run_ion2.sh sp   "3s(2,i)3p(6,i)3d(10,i)4s(1,i)4p(5,i)" "0,4"  ../neutral/neutral.w
./run_ion2.sh ss   "3s(2,i)3p(6,i)3d(10,i)4s(0,i)4p(6,i)" "0,0"  ../neutral/neutral.w
./run_ion_he.sh p2 "2s(2,i)2p(5,i)3s(2,i)3p(6,i)3d(10,i)4s(2,i)4p(6,i)" "1,3" ../neutral/neutral.w
# --- layer optimisation helper: MCDHF on the neutral, orbitals varied step by step (NaN-safe)
opt_layer() {  # dir  active-set  "rcsfgenerate config"  start.w  steps...
  D=$1; AS=$2; CFG=$3; W=$4; shift 4
  mkdir -p $D; cd $D; cp ../isodata .
  printf '*\n2\n%s\n\n%s\n0,0\n2\nn\n' "$CFG" "$AS" | rcsfgenerate > csf.log 2>&1; cp rcsf.out rcsf.inp
  printf 'y\n' | rangular > ang.log 2>&1
  printf "y\n1\n%s\n*\n2\n*\n" "$W" | rwfnestimate > est.log 2>&1
  for step in "$@"; do cp rwfn.inp rwfn.bak; printf "y\n1\n5\n$step\n\n300\n" | rmcdhf > scf.log 2>&1
    if grep -q "NaN\|Error" scf.log; then cp rwfn.bak rwfn.inp; else cp rwfn.out rwfn.inp; fi; done
  cp rwfn.inp rwfn.out; cd $B; }
# valence layer {5s,5p,4d,4f}: 4s,4p SD (3d at most one) on the neutral
opt_layer val_neu '5s,5p,4d,4f' '3s(2,i)3p(6,i)3d(10,9)4s(2,*)4p(6,*)' ../neutral/neutral.w '4d*' '5p*' '5s*' '4f*' '5s*,5p*,4d*,4f*'
( cd val_neu && rsave valneu > /dev/null )
# second valence layer {6s,6p,5d,5f}: 4s,4p SD, 3d fixed
opt_layer val2_neu '6s,6p,5d,5f' '3s(2,i)3p(6,i)3d(10,i)4s(2,*)4p(6,*)' ../val_neu/valneu.w '5d*' '6p*' '6s*' '5f*' '6s*,6p*,5d*,5f*'
( cd val2_neu && rsave val2neu > /dev/null )
# compact core layer {5p,4d,5d,4f,5f}: 3d^2 pair excitations on the neutral
opt_layer neu_corr3 '4s,5p,5d,5f' '3s(2,i)3p(6,i)3d(10,*)4s(2,i)4p(6,i)' ../neutral/neutral.w '4f*' '5p*' '5f*' '5d*' '4d*' '4d*,5d*'
( cd neu_corr3 && rsave neucorr3 > /dev/null )
# --- single-hole core CIs (compact layer) and valence CIs (fixed core)
./ci_core3.sh neu "3s(2,i)3p(6,i)3d(10,*)4s(2,i)4p(6,i)" 0,0 ../neutral/neutral.w 1
./ci_core3.sh d9  "3s(2,i)3p(6,i)3d(9,*)4s(2,i)4p(6,i)"  3,5 ../d9/d9.w 3
./ci_core3.sh np5 "3s(2,i)3p(6,i)3d(10,*)4s(2,i)4p(5,i)" 1,3 ../np5/np5.w 2
./ci_core3.sh s1  "3s(2,i)3p(6,i)3d(10,*)4s(1,i)4p(6,i)" 1,1 ../s1/s1.w 2
./ci_core3.sh p4  "3s(2,i)3p(6,i)3d(10,*)4s(2,i)4p(4,i)" 0,4 ../p4/p4.w 2
for L in L1 L12; do
  ./ci_v2.sh neu "3s(2,i)3p(6,i)3d(10,i)4s(2,*)4p(6,*)" 0,0 ../neutral/neutral.w 1 $L
  ./ci_v2.sh np5 "3s(2,i)3p(6,i)3d(10,i)4s(2,*)4p(5,*)" 1,3 ../np5/np5.w 3 $L
  ./ci_v2.sh s1  "3s(2,i)3p(6,i)3d(10,i)4s(1,*)4p(6,*)" 1,1 ../s1/s1.w 30 $L
  ./ci_v2.sh p4  "3s(2,i)3p(6,i)3d(10,i)4s(2,*)4p(4,*)" 0,4 ../p4/p4.w 3 $L
  ./ci_v2.sh sp  "3s(2,i)3p(6,i)3d(10,i)4s(1,*)4p(5,*)" 0,4 ../sp/sp.w 30 $L
  ./ci_v2.sh ss  "3s(2,i)3p(6,i)3d(10,i)4s(0,*)4p(6,*)" 0,0 ../ss/ss.w 30 $L
done
./own_opt.sh neu "3s(2,i)3p(6,i)3d(10,i)4s(2,*)4p(6,*)" 0,0 ../neutral/neutral.w "1"
./own_opt.sh s1  "3s(2,i)3p(6,i)3d(10,i)4s(1,*)4p(6,*)" 1,1 ../s1/s1.w "1"
./own_opt.sh np5 "3s(2,i)3p(6,i)3d(10,i)4s(2,*)4p(5,*)" 1,3 ../np5/np5.w "$(printf '1\n1')"
# 3p hole core CI: 3d pairs + explicit 3p6 3d8 X (3p^-1 <-> 3d^-2 X coupling)
A='4s,5p,5d,5f'; mkdir -p c3_p5; ( cd c3_p5 && cp ../isodata . && \
  printf "*\n2\n3s(2,i)3p(5,i)3d(10,*)4s(2,i)4p(6,i)\n\n$A\n1,3\n2\ny\n3s(2,i)3p(6,i)3d(8,i)4s(2,i)4p(6,i)5p(1,i)\n\n$A\n1,3\n0\ny\n3s(2,i)3p(6,i)3d(8,i)4s(2,i)4p(6,i)4f(1,i)\n\n$A\n1,3\n0\ny\n3s(2,i)3p(6,i)3d(8,i)4s(2,i)4p(6,i)5f(1,i)\n\n$A\n1,3\n0\nn\n" | rcsfgenerate > csf.log 2>&1 && \
  cp rcsf.out rcsf.inp && printf 'y\n' | rangular > ang.log 2>&1 && \
  printf 'y\n1\n../p5.w\n*\n1\n../neu_corr3/neucorr3.w\n*\n' | rwfnestimate > est.log 2>&1 && cp rwfn.inp p5.w && cp rcsf.inp p5.c && \
  { echo y; echo p5; echo y; echo y; echo 1.d-6; echo y; echo n; echo n; echo y; echo 4; echo 1-3; echo 1-3; } | rci > rci.log 2>&1 )
# valence CIs of the diagram-line initial states (spectator analysis) and Kr2+ 3p^-1 4p^-1 (interaction energies)
source ./ci_fn.sh; V=../val_neu/valneu.w; AV='5s,5p,4d,4f'
ci W_p5 "*\n2\n3s(2,i)3p(5,i)3d(10,i)4s(2,*)4p(6,*)\n\n$AV\n1,3\n2\nn\n" ../p5.w $V 6
ci W_d9 "*\n2\n3s(2,i)3p(6,i)3d(9,i)4s(2,*)4p(6,*)\n\n$AV\n3,5\n2\nn\n" ../d9/d9.w $V 6
./run_ion2.sh p5np5 "3s(2,i)3p(5,i)3d(10,i)4s(2,i)4p(5,i)" "0,6" ../p5d9/p5d9.w
