# grasp-kr-3p-auger

Relativistic atomic-structure calculations for krypton with [GRASP2018](https://github.com/compas/grasp),
used as an energy cross-check of the FAC calculations of the Kr 2p Auger cascade
([FAC-Kr-2p](https://github.com/sunnylabh/FAC-Kr-2p)). GRASP gives level energies only; where line
intensities are needed they are taken from FAC.

## Repository layout

```
grasp-kr-3p-auger/
├── kr3p_hole/          Kr+ 3p binding energies and M2,3-M4,5N2,3 Coster-Kronig energies, 3p-1 / 3d-2 4f correlation
│   ├── scripts/        run scripts (nucleus, single-configuration ions, correlation orbital, CI, energies)
│   ├── runs/           GRASP output of the reference runs (.c, .w, .cm, .sum)
│   ├── results/        energies.md
│   └── run_all.sh      full pipeline (a few seconds)
├── cascade/            Kr 2p cascade, steps 1-2 (Kr+ 2p-1 -> Kr2+ -> Kr3+) with core and valence correlation,
│                       spectator shifts, and single-configuration runs of the Kr4+ to Kr6+ configurations
├── kr5_quaternary/     Kr4+ -> Kr5+ step: single-configuration GRASP vs FAC
├── CITATION.cff
└── LICENSE
```

Each folder has its own README with the method, the run order and the limitations.

## Results

| Part | Main result | File |
|---|---|---|
| `kr3p_hole/` | 3p⁻¹–3d⁻²4f coupling lowers the 3p levels by 2.0–2.1 eV; 3p₃/₂ binding energy 215.01 eV (exp. 214.4 eV) | [`kr3p_hole/results/energies.md`](kr3p_hole/results/energies.md) |
| `cascade/` | Correlated single-hole binding energies within 0.8 eV of experiment; first- and second-step kinetic energies vs FAC | [`cascade/cascade_KE_table.md`](cascade/cascade_KE_table.md) |
| `kr5_quaternary/` | Mean Kr⁴⁺ → Kr⁵⁺ kinetic energies agree with FAC to within 0.7 eV | [`kr5_quaternary/compare_fac.md`](kr5_quaternary/compare_fac.md) |

At the single-configuration level GRASP and FAC agree to 0.2–0.7 eV, so the larger offsets between FAC and
experiment come from correlation, not from the FAC setup.

## Requirements

- GRASP2018 (built from [compas/grasp](https://github.com/compas/grasp), master branch, commit `9006157`,
  September 2025). The scripts look for the binaries in `~/grasp/bin`; `kr3p_hole/` also reads `GRASP_BIN`.
- Python 3 with NumPy and Matplotlib.
- `cascade/` and `kr5_quaternary/` read FAC output through `FAC_KR2P` (default `~/Desktop/FAC/Kr 2p`).

Building GRASP2018 on macOS with Homebrew gfortran 15:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_Fortran_FLAGS="-fallow-argument-mismatch" -DCMAKE_DISABLE_FIND_PACKAGE_MPI=ON
cd build && make -j8 install
```

## Running

```sh
kr3p_hole/run_all.sh            # also writes the nucleus file used by the other parts
kr5_quaternary/run_all.sh
cascade/run_cascade.sh          # several hours; the largest CIs have ~100k CSFs
cascade/run_kr4_kr6.sh
```

Run directories, GRASP scratch files and logs are not tracked (see `.gitignore`).

## References

- C. Froese Fischer, G. Gaigalas, P. Jönsson, J. Bieroń, Comput. Phys. Commun. **237**, 184 (2019) — GRASP2018.
- P. Jönsson et al., *An introduction to relativistic theory as implemented in GRASP*, Atoms **11**, 7 (2023).

## License

BSD 3-Clause, see [`LICENSE`](LICENSE).
