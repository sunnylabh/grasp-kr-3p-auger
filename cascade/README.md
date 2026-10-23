# Kr 2p Auger cascade: steps 1 and 2, and single-configuration runs to Kr⁶⁺

GRASP kinetic energies for the first step (Kr⁺ 2p⁻¹ → Kr²⁺, L-MM / L-MN) and the second step
(Kr²⁺ → Kr³⁺, M-NN and Coster–Kronig) of the Kr 2p Auger cascade, compared with FAC.
Results: [`cascade_KE_table.md`](cascade_KE_table.md); figures in `figures/`.

## Binding energies (correlated GRASP vs experiment)

| Hole | GRASP | Experiment |
|---|---|---|
| 2p₃/₂ / 2p₁/₂ | 1678.37 / 1731.24 eV | 1678.4 / 1730.9 eV |
| 3p₃/₂ / 3p₁/₂ | 214.51 / 222.37 eV | 214.4 / 222.2 eV |
| 3d₅/₂ / 3d₃/₂ | 94.01 / 95.25 eV | 93.80 / 95.04 eV |
| 4p₃/₂ | 13.74 eV | 14.00 eV |
| 4s | 28.32 eV | 27.51 eV |
| Kr³⁺ 4p⁻³ ⁴S₃/₂ | 72.98 eV | 74.20 eV |

## Method

| Part | Treatment |
|---|---|
| Level energies | single-configuration DHF + RCI (Breit, VP, SE), then CI increments per level |
| Core correlation | 3d pair excitations into a compact layer {5p,4d,5d,4f,5f}; 3p-hole states also include 3p⁻¹ ↔ 3d⁻²X |
| Valence correlation | 4s,4p single and double excitations into {5s,5p,4d,4f}, core occupations fixed; second layer {6s,6p,5d,5f} and state-specific orbitals for valence holes |
| Correlation orbitals | optimised on the neutral ground state (`layers.sh`) |
| Fragmented levels | 4s-hole levels split over several CI roots; the line position is the root with the largest overlap² with the uncorrelated level (`overlap.py`), accepted when its weight exceeds the uncaptured remainder |
| 3p⁻¹3d⁻¹ + valence hole | core correction transferred level by level from Kr²⁺ 3p⁻¹3d⁻¹ (`project_core.py`; 0.014 eV rms against the direct result for 3d⁻²4p⁻¹) |
| Kinetic energy | E(initial level) − E(final level) |
| Intensities | FAC rates and FAC primary-step populations; levels matched by configuration, 2J and energy order |

## Spectator shifts (`spectator.py`)

Shift of a transition in the presence of a spectator vacancy relative to the diagram line, from
configuration-average energies and from intensity-weighted feature centroids:

| Spectator transition | Diagram line | Average shift | Centroid shift |
|---|---|---|---|
| 3p⁻¹3d⁻¹ → 3d⁻²4p⁻¹ | 3p⁻¹ → 3d⁻¹4p⁻¹ | −15.6 eV | −8.0 eV |
| 3p⁻² → 3p⁻¹3d⁻¹4p⁻¹ | 3p⁻¹ → 3d⁻¹4p⁻¹ | −12.0 eV | −13.7 eV |
| 3d⁻¹4p⁻¹ → 4p⁻³ | 3d⁻¹ → 4p⁻² | −9.9 eV | −8.7 eV |
| 3d⁻² → 3d⁻¹4p⁻² | 3d⁻¹ → 4p⁻² | −0.1 eV | +1.7 eV |

To first order the shift is U(s,i) − U(s,f₁) − U(s,f₂), with U the hole–hole interaction energy between
the spectator s and the initial (i) and final (f) holes (n = 3 pairs ≈ 26–27 eV, n = 3/4p ≈ 12–13 eV,
4p/4p ≈ 11 eV). FAC gives the same shifts within 0.4 eV except the 3p-spectator case (2 eV).

## Kr⁴⁺ to Kr⁶⁺ (`run_kr4_kr6.sh`)

Single-configuration DHF + RCI runs (same recipe as the step-1/2 reference runs, `run_ion_base.sh`) for the
Kr⁴⁺, Kr⁵⁺ and Kr⁶⁺ configurations of the later cascade steps. Their level energies give direct GRASP kinetic
energies for the Kr³⁺ → Kr⁴⁺ step (levels matched to FAC by parity, 2J and energy order; FAC rates). No
correlation increments are added to these runs.

## Running

`run_cascade.sh` lists the full order (several hours; largest CIs ~100k CSFs). The analysis
scripts read the FAC project through `FAC_KR2P` (default `~/Desktop/FAC/Kr 2p`). Run directories and
GRASP output files are not tracked.

## Limitations

- Intensities are FAC's; GRASP gives energies only.
- 4s⁻² pair states remain ~1–2 eV over-bound; Kr³⁺ 4p⁻³ is 1.2 eV below experiment.
- Three high-lying 3p⁻¹3d⁻¹4s⁻¹ levels lie above the computed CI roots and use the mean valence shift of
  the other 20 levels of that state (spread ±0.04 eV).
- 3s-hole states (L-M₁M₂,₃, L-M₁M₄,₅) are not computed.
