#!/bin/bash
# Order of the full pipeline (several hours on a laptop; the largest CIs have ~100k CSFs).
set -e; S="$(cd "$(dirname "$0")" && pwd)"
"$S/layers.sh"          # nucleus, reference runs, correlation layers, single-hole CIs
"$S/lmm_direct.sh"      # Kr+ 2p^-1 and Kr2+ states: core CIs
"$S/val_fixed.sh"       # valence CIs (fixed core) for the LMM states
"$S/val_fix2.sh"        # 3p^4 valence CI and 2p^-1 with enough roots
"$S/final_states.sh"    # Kr3+ final states: reference runs, core CIs, valence CIs
"$S/finish_4s.sh"       # 4s-hole valence CIs with more roots (fragmented levels)
"$S/extract_rmx.sh"     # eigenvectors for the overlap analysis
( cd "$S/fac_ref" && python3 fac_states.py . && python3 fac_avg.py . && python3 fac_d9p4.py . && python3 test1.py . )
python3 "$S/plot_lmm.py"; python3 "$S/plot_secondary.py"; python3 "$S/ke_table.py" > "$S/cascade_KE_table.md"
python3 "$S/state_table.py"; python3 "$S/spectator.py"
