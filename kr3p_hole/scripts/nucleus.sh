#!/bin/bash
# Kr-84 nucleus (Fermi distribution, default radius), written to runs/isodata
set -e; source "$(dirname "$0")/env.sh"
mkdir -p "$RUNS"; cd "$RUNS"
printf '36\n84\nn\n83.9115\n0\n0\n0\n' | rnucleus > rnucleus.log 2>&1
