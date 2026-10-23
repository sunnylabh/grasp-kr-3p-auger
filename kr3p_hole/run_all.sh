#!/bin/bash
# Full pipeline: nucleus -> single-configuration ions -> 4f correlation orbital -> Kr+ CI -> energies
set -e
S="$(cd "$(dirname "$0")" && pwd)/scripts"
"$S/nucleus.sh"
"$S/run_ion.sh" neutral "3s(2,i)3p(6,i)3d(10,i)4s(2,i)4p(6,i)" "0,0"
"$S/run_ion.sh" p5      "3s(2,i)3p(5,i)3d(10,i)4s(2,i)4p(6,i)" "1,3"
"$S/run_ion.sh" d9p5    "3s(2,i)3p(6,i)3d(9,i)4s(2,i)4p(5,i)"  "0,8"
"$S/neu_corr.sh"
"$S/p5_ci.sh"
python3 "$S/energies.py"
