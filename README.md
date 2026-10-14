# Kr 3p hole and M2,3-M4,5N2,3 Auger energies with GRASP2018

Relativistic atomic-structure calculations for krypton with [GRASP2018](https://github.com/compas/grasp):
the 3p binding energies of Kr⁺ and the kinetic energies of the M2,3-M4,5N2,3 Coster–Kronig
electrons (Kr⁺ 3p⁻¹ → Kr²⁺ 3d⁻¹4p⁻¹ + e⁻).

The calculations check a systematic offset found in FAC (Flexible Atomic Code) results for the
Kr 2p/3p/3d Auger cascade, where this channel lies about 5 eV above experiment.

## Results

| | Single configuration | With 3p⁻¹–3d⁻²4f correlation | Experiment |
|---|---|---|---|
| 3p₃/₂ binding energy | 217.04 eV | 215.01 eV | 214.4 eV |
| 3p₁/₂ binding energy | 225.05 eV | 222.93 eV | 222.2 eV |
| 3p spin-orbit splitting | 8.01 eV | 7.92 eV | 7.8 eV |
| KE, 3p₃/₂ → 3d⁻¹4p⁻¹ | 96.1–99.4 eV | 94.1–97.4 eV | 90–94 eV |
| KE, 3p₁/₂ → 3d⁻¹4p⁻¹ | 104.1–107.4 eV | 102.0–105.3 eV | 98–102 eV |

- At the single-configuration level GRASP agrees with FAC to about 0.2 eV
  (FAC: 3p binding energies 216.91 / 224.81 eV, KE 96.3–99.6 / 104.2–107.5 eV).
- Coupling of the 3p hole to 3d⁻²4f configurations (super-Coster–Kronig fluctuation) lowers the
  3p levels by 2.0–2.1 eV and reduces the binding-energy error from +2.6 to +0.6 eV.
- The remaining ~3 eV KE offset comes from the final state: the 3d and 4p holes of Kr²⁺ are
  under-bound without correlation (FAC errors: 3d −1.8 eV, 4p −1.1 eV per hole).

Full table: [`results/energies.md`](results/energies.md).

## Method

| Step | Script | Details |
|---|---|---|
| Nucleus | `scripts/nucleus.sh` | ⁸⁴Kr, Fermi distribution, default radius |
| Single-configuration ions | `scripts/run_ion.sh` | Ne core; DHF with extended optimal level (all levels, 2J+1 weights); RCI with Breit (transverse photon), vacuum polarisation and self-energy (n ≤ 4) |
| 4f correlation orbital | `scripts/neu_corr.sh` | MCDHF on the neutral ground state with 3d² → 4f² pair excitations (22 CSFs); only 4f varied |
| Correlated Kr⁺ 3p⁻¹ | `scripts/p5_ci.sh` | CI over 3p⁵ + 3p⁶3d⁸4f (8 CSFs J=1/2, 14 CSFs J=3/2); core orbitals from `p5`, 4f from `neu_corr` |
| Energies | `scripts/energies.py` | Binding energy = E(Kr⁺) − E(Kr); KE = E(Kr⁺ 3p⁻¹) − E(Kr²⁺ 3d⁻¹4p⁻¹) |

The 3p⁻¹ levels are the lowest roots of the CI (99.7 % 3p⁻¹ character).

Optimising 4f directly on the 3p⁻¹ roots does not work: the 3d⁻²4f states lie just below 3p⁻¹ and
the targeted roots flip to pure 3d⁻²4f states during the SCF (`rmcdhf` has no root tracking).
`scripts/rootflip_demo.sh` reproduces this.

## Running

Requires GRASP2018 binaries (default `~/grasp/bin`, override with `GRASP_BIN`) and Python 3.

```sh
./run_all.sh
```

The full pipeline takes a few seconds. Outputs go to `runs/<name>/`: `.c` (CSF list), `.w`
(radial orbitals), `.cm` (RCI mixing), `.sum` / `.csum` (summaries).

Building GRASP2018 on macOS with Homebrew gfortran 15 needs `-fallow-argument-mismatch`:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_Fortran_FLAGS="-fallow-argument-mismatch" -DCMAKE_DISABLE_FIND_PACKAGE_MPI=ON
cd build && make -j8 install
```

## Limitations

- One 4f correlation orbital; the expansion is not converged (5f, 6f, … not included).
- The neutral atom and the Kr²⁺ final state are uncorrelated, so the treatment is not balanced.
- GRASP gives energies only. Auger rates (line intensities) need a separate code such as JAC or RATIP.
- The Auger continuum is not included; the super-Coster–Kronig width of the 3p hole is not computed.

## References

- C. Froese Fischer, G. Gaigalas, P. Jönsson, J. Bieroń, Comput. Phys. Commun. **237**, 184 (2019) — GRASP2018.
- P. Jönsson et al., *An introduction to relativistic theory as implemented in GRASP*, Atoms **11**, 7 (2023).
