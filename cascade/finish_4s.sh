#!/bin/bash
# Clean sequential reruns of the three 4s-hole valence CIs with per-block root counts; verifies the output.
export PATH=~/grasp/bin:$PATH; B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; LOG=$B/finish_4s.log
rr() {  # dir  "2J:nroots ..."  default
  cd $B/$1; MAP="$2"; DEF=$3
  BL=$(awk -v map="$MAP" -v def=$DEF 'BEGIN{n=split(map,a," "); for(i=1;i<=n;i++){split(a[i],b,":"); M[b[1]]=b[2]}}
       /block  J\/P/{f=1;next} f&&NF==3{j=$2; sub(/[+-]$/,"",j); split(j,q,"/"); j2=(q[2]=="2")?q[1]:2*q[1];
       want=(j2 in M)?M[j2]:def; m=($3<want)?$3:want; print "1-"m}' csf.log)
  rm -f $1.cm $1.rmx
  { echo y; echo $1; echo y; echo y; echo 1.d-6; echo y; echo n; echo n; echo y; echo 4; echo "$BL"; } | rci > rci.log 2>&1
  printf "0\n$1\ny\n0.03\nn\n" | rmixextract > rmx.log 2>&1
  echo "$1 done $(date +%T); blocks requested: $(echo $BL | tr '\n' ' '); eigenvectors in rmx: $(grep -c 'Energy =' $1.rmx 2>/dev/null); rmx errors: $(grep -ci error rmx.log)" >> $LOG; }
rr F_v_d9sp "" 60
rr F_v_d8s1 "1:135" 40
rr F_v_pds "1:165 3:165 5:185 7:165" 40
echo "ALL DONE $(date +%T)" >> $LOG
