#!/bin/bash
export PATH=~/grasp/bin:$PATH; B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd $B
source ./ci_fn.sh
V=../val_neu/valneu.w; AV='5s,5p,4d,4f'
rm -rf W_p4 W_p2
ci W_p4 "*\n2\n3s(2,i)3p(4,i)3d(10,i)4s(2,*)4p(6,*)\n\n$AV\n0,4\n2\nn\n" ../p4x/p4x.w $V 6 &
ci W_p2 "*\n1\n2s(2,i)2p(5,i)3s(2,i)3p(6,i)3d(10,i)4s(2,*)4p(6,*)\n\n$AV\n1,3\n2\nn\n" ../p2/p2.w $V 400 &
wait
