# GRASP2018 binaries; override with GRASP_BIN=/path/to/grasp/bin
export PATH="${GRASP_BIN:-$HOME/grasp/bin}:$PATH"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNS="$ROOT/runs"
