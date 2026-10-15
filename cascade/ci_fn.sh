ci() {  # tag  rcsfgenerate-input  core.w  layer.w  nroots
  T=$1; IN=$2; CORE=$3; LAY=$4; NR=$5
  mkdir -p $B/$T; cd $B/$T; cp $B/isodata .
  printf "$IN" | rcsfgenerate > csf.log 2>&1; cp rcsf.out rcsf.inp
  BL=$(awk -v n=$NR '/block  J\/P/{f=1;next} f&&NF==3{m=($3<n)?$3:n; print "1-"m}' csf.log)
  printf 'y\n' | rangular > ang.log 2>&1
  printf 'y\n1\n%s\n*\n1\n%s\n*\n' "$CORE" "$LAY" | rwfnestimate > est.log 2>&1
  N=$(basename $T); cp rwfn.inp $N.w; cp rcsf.inp $N.c
  { echo y; echo $N; echo y; echo y; echo 1.d-6; echo y; echo n; echo n; echo y; echo 4; echo "$BL"; } | rci > rci.log 2>&1
  echo "$T done $(awk '/block  J\/P/{f=1;next} f&&NF==3{s+=$3} END{print s}' csf.log) CSFs $(date +%T)" >> ${LOG:-$B/lmm_direct.log}; cd $B; }
