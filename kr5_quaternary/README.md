# Kr⁴⁺ → Kr⁵⁺ Auger energies: GRASP vs FAC

Cross-check of the FAC energetics of the Kr⁴⁺ → Kr⁵⁺ cascade step (FAC-Kr-2p, `kr2p/06_quaternary_Kr5+`)
with single-configuration GRASP2018 runs at the same level of theory.

## Method

| Step | Script | Details |
|---|---|---|
| Runs | `run_all.sh` → `run_ion.sh` | Ne core; DHF (EOL, all levels) + RCI with Breit, VP and SE, one configuration per run |
| 4s-hole runs | `run_ion_start.sh` | Same recipe, starting orbitals from a converged neighbouring run (Thomas-Fermi starts do not converge) |
| Comparison | `compare_fac.py` | (2J+1)-weighted mean KE and full KE span for every parent → final configuration pair |

The FAC levels are read from `$FAC_KR2P/kr_output/quat_<Q>_SC.lev` (default `FAC_KR2P = ~/Desktop/FAC/Kr 2p`).

## Running

```sh
../kr3p_hole/run_all.sh        # once, for the nucleus file (isodata)
./run_all.sh                   # 11 runs, a few seconds
python3 compare_fac.py > compare_fac.md
```

## Results

[`compare_fac.md`](compare_fac.md): GRASP and FAC mean kinetic energies agree to within 0.7 eV for all
twelve configuration pairs, and the KE spans to within about 1.5 eV.
