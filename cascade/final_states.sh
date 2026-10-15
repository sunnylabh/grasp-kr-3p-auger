#!/bin/bash
# Kr3+ final states of the second step: SC + core CI (compact layer) + valence CI (fixed core)
export PATH=~/grasp/bin:$PATH; B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd $B
source ./ci_fn.sh
LOG=$B/final_states.log
sc() {  # name config 2Jrange start.w
  ./run_ion2.sh $1 "$2" "$3" $4 > /dev/null 2>&1
  if [ ! -f $1/$1.cm ]; then   # SCF failed: restart from the given orbitals with a 100-cycle cap
    ( cd $1 && BL=$(awk '/block  J\/P/{f=1;next} f&&NF==3{print "1-"$3}' csf.log) && printf 'y\n1\n%s\n*\n' "$4" | rwfnestimate > est.log 2>&1 && \
      { echo y; echo "$BL"; echo 5; echo '*'; echo '*'; echo 100; } | rmcdhf > scf.log 2>&1; rsave $1 > /dev/null 2>&1; \
      { echo y; echo $1; echo y; echo y; echo 1.d-6; echo y; echo n; echo n; echo y; echo 4; echo "$BL"; } | rci > rci.log 2>&1 )
  fi
  echo "SC $1: $(grep -c 'Iteration number' $1/scf.log) it, $( [ -f $1/$1.cm ] && echo ok || echo FAILED) $(date +%T)" >> $LOG; }
sc d9sp "3s(2,i)3p(6,i)3d(9,i)4s(1,i)4p(5,i)"  "1,13" ../d9p5/d9p5.w &
sc d9p4 "3s(2,i)3p(6,i)3d(9,i)4s(2,i)4p(4,i)"  "1,13" ../d9p5/d9p5.w &
sc d9s0 "3s(2,i)3p(6,i)3d(9,i)4s(0,i)4p(6,i)"  "1,5"  ../d9/d9.w &
sc sp4  "3s(2,i)3p(6,i)3d(10,i)4s(1,i)4p(4,i)" "1,5"  ../sp/sp.w &
sc s0p5 "3s(2,i)3p(6,i)3d(10,i)4s(0,i)4p(5,i)" "1,3"  ../ss/ss.w &
sc p3   "3s(2,i)3p(6,i)3d(10,i)4s(2,i)4p(3,i)" "1,5"  ../p4/p4.w &
sc d8s1 "3s(2,i)3p(6,i)3d(8,i)4s(1,i)4p(6,i)"  "1,11" ../d8x/d8x.w &
wait
C=../neu_corr3/neucorr3.w; V=../val_neu/valneu.w; A='4s,5p,5d,5f'; AV='5s,5p,4d,4f'
# core CIs (direct)
ci F_c_d9s0 "*\n2\n3s(2,i)3p(6,i)3d(9,*)4s(0,i)4p(6,i)\n\n$A\n1,5\n2\nn\n"   ../d9s0/d9s0.w $C 4 &
ci F_c_sp4  "*\n2\n3s(2,i)3p(6,i)3d(10,*)4s(1,i)4p(4,i)\n\n$A\n1,5\n2\nn\n"  ../sp4/sp4.w $C 6 &
ci F_c_s0p5 "*\n2\n3s(2,i)3p(6,i)3d(10,*)4s(0,i)4p(5,i)\n\n$A\n1,3\n2\nn\n"  ../s0p5/s0p5.w $C 3 &
ci F_c_p3   "*\n2\n3s(2,i)3p(6,i)3d(10,*)4s(2,i)4p(3,i)\n\n$A\n1,5\n2\nn\n"  ../p3/p3.w $C 6 &
ci F_c_d8s1 "*\n2\n3s(2,i)3p(6,i)3d(8,*)4s(1,i)4p(6,i)\n\n$A\n1,11\n2\nn\n"  ../d8s1/d8s1.w $C 8 &
wait
ci F_c_d8p5 "*\n2\n3s(2,i)3p(6,i)3d(8,*)4s(2,i)4p(5,i)\n\n$A\n1,13\n2\nn\n"  ../d8p5/d8p5.w $C 14 &
# valence CIs (direct, fixed core)
ci F_v_d9s0 "*\n2\n3s(2,i)3p(6,i)3d(9,i)4s(0,*)4p(6,*)\n\n$AV\n1,5\n2\nn\n"  ../d9s0/d9s0.w $V 60 &
ci F_v_sp4  "*\n2\n3s(2,i)3p(6,i)3d(10,i)4s(1,*)4p(4,*)\n\n$AV\n1,5\n2\nn\n" ../sp4/sp4.w $V 60 &
ci F_v_s0p5 "*\n2\n3s(2,i)3p(6,i)3d(10,i)4s(0,*)4p(5,*)\n\n$AV\n1,3\n2\nn\n" ../s0p5/s0p5.w $V 60 &
ci F_v_p3   "*\n2\n3s(2,i)3p(6,i)3d(10,i)4s(2,*)4p(3,*)\n\n$AV\n1,5\n2\nn\n" ../p3/p3.w $V 10 &
wait
ci F_v_d9sp "*\n2\n3s(2,i)3p(6,i)3d(9,i)4s(1,*)4p(5,*)\n\n$AV\n1,13\n2\nn\n" ../d9sp/d9sp.w $V 60 &
ci F_v_d9p4 "*\n2\n3s(2,i)3p(6,i)3d(9,i)4s(2,*)4p(4,*)\n\n$AV\n1,13\n2\nn\n" ../d9p4/d9p4.w $V 15 &
ci F_v_d8s1 "*\n2\n3s(2,i)3p(6,i)3d(8,i)4s(1,*)4p(6,*)\n\n$AV\n1,11\n2\nn\n" ../d8s1/d8s1.w $V 40 &
wait
ci F_v_d8p5 "*\n2\n3s(2,i)3p(6,i)3d(8,i)4s(2,*)4p(5,*)\n\n$AV\n1,13\n2\nn\n" ../d8p5/d8p5.w $V 16 &
ci F_v_pds  "*\n2\n3s(2,i)3p(5,i)3d(9,i)4s(1,*)4p(6,*)\n\n$AV\n1,13\n2\nn\n" ../pds/pds.w $V 40 &
wait
ci F_v_pdp  "*\n2\n3s(2,i)3p(5,i)3d(9,i)4s(2,*)4p(5,*)\n\n$AV\n1,15\n2\nn\n" ../pdp/pdp.w $V 20
echo "ALL DONE $(date +%T)" >> $LOG
