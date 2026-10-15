#!/bin/bash
# Valence correlation: 4s,4p SD into {5s,5p,4d,4f}; 3s,3p,3d (and 2p) occupations fixed. Same scheme for all states.
export PATH=~/grasp/bin:$PATH; B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd $B
source ./ci_fn.sh
V=../val_neu/valneu.w; AV='5s,5p,4d,4f'
ci W_neu  "*\n2\n3s(2,i)3p(6,i)3d(10,i)4s(2,*)4p(6,*)\n\n$AV\n0,0\n2\nn\n" ../neutral/neutral.w $V 3 &
ci W_p2   "*\n1\n2s(2,i)2p(5,i)3s(2,i)3p(6,i)3d(10,i)4s(2,*)4p(6,*)\n\n$AV\n1,3\n2\nn\n" ../p2/p2.w $V 3 &
ci W_d8   "*\n2\n3s(2,i)3p(6,i)3d(8,i)4s(2,*)4p(6,*)\n\n$AV\n0,8\n2\nn\n" ../d8x/d8x.w $V 6 &
ci W_p4s  "*\n2\n3s(2,i)3p(4,i)3d(10,i)4s(2,*)4p(6,*)\n\n$AV\n0,4\n2\ny\n3s(1,i)3p(6,i)3d(9,i)4s(2,*)4p(6,*)\n\n$AV\n0,4\n2\nn\n" ../p4s/p4s.w $V 8 &
wait
ci W_p5d9 "*\n2\n3s(2,i)3p(5,i)3d(9,i)4s(2,*)4p(6,*)\n\n$AV\n0,10\n2\nn\n" ../p5d9/p5d9.w $V 6 &
ci W_d9p5 "*\n2\n3s(2,i)3p(6,i)3d(9,i)4s(2,*)4p(5,*)\n\n$AV\n0,8\n2\nn\n" ../d9p5/d9p5.w $V 30 &
wait
echo "VAL DONE $(date +%T)" >> lmm_direct.log
