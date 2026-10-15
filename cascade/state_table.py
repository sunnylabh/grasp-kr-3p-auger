# -*- coding: utf-8 -*-
"""Energies of the cascade states relative to the neutral ground state: FAC vs GRASP.
GRASP: E = E_SC + dE_core + dE_val (+ second-valence-layer/own-orbital increments for valence holes), the same
construction as plot_lmm.py / secondary.py; the neutral gets the same core (c3_neu) and valence (W_neu) CIs."""
import os, sys, json, collections
B = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, B)
import plot_lmm as pl, secondary as sc
H = 27.211386245988
FAC = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fac_ref', 'fac_states.json')))

n_sc = pl.ci_roots('neutral/neutral', '3d10 4s2 4p6')[0][0]
n_c = pl.ci_roots('c3_neu/neu', '3d10 4s2 4p6')[0][0]
n_v = pl.ci_roots('W_neu/W_neu', '3d10 4s2 4p6')[0][0]
E_neu = n_sc + (n_c - n_sc) + (n_v - n_sc)

ROWS = [('Kr⁺', '2p5', '2p⁻¹', 'initial (photoionisation)'),
        ('Kr²⁺', '3d8', '3d⁻²', 'L-M₄,₅M₄,₅'), ('Kr²⁺', '3p5.3d9', '3p⁻¹3d⁻¹', 'L-M₂,₃M₄,₅'),
        ('Kr²⁺', '3p4', '3p⁻²', 'L-M₂,₃M₂,₃'), ('Kr²⁺', '3d9.4p5', '3d⁻¹4p⁻¹', 'L-M₄,₅N₂,₃'),
        ('Kr³⁺', '3d9.4s1.4p5', '3d⁻¹4s⁻¹4p⁻¹', 'from 3d⁻²'), ('Kr³⁺', '3d9.4p4', '3d⁻¹4p⁻²', 'from 3d⁻²'),
        ('Kr³⁺', '3d9', '3d⁻¹4s⁻²', 'from 3d⁻²'), ('Kr³⁺', '4s1.4p4', '4s⁻¹4p⁻²', 'from 3d⁻¹4p⁻¹'),
        ('Kr³⁺', '4p5', '4s⁻²4p⁻¹', 'from 3d⁻¹4p⁻¹'), ('Kr³⁺', '4p3', '4p⁻³', 'from 3d⁻¹4p⁻¹'),
        ('Kr³⁺', '3d8.4p5', '3d⁻²4p⁻¹', 'from 3p⁻¹3d⁻¹ (CK)'), ('Kr³⁺', '3d8.4s1', '3d⁻²4s⁻¹', 'from 3p⁻¹3d⁻¹ (CK)'),
        ('Kr³⁺', '3p5.3d9.4p5', '3p⁻¹3d⁻¹4p⁻¹', 'from 3p⁻² (CK)'), ('Kr³⁺', '3p5.3d9.4s1', '3p⁻¹3d⁻¹4s⁻¹', 'from 3p⁻² (CK)')]
EXP = {'2p5': ('1678.4 / 1730.9', 'NIST 2p₃/₂ / 2p₁/₂'), '4p3': ('74.20', 'Kr³⁺ ⁴S₃/₂ (sum of IPs)')}

print('| Ion | State | Populated by | FAC lowest | FAC range | GRASP lowest | GRASP range | GRASP − FAC (lowest) | Experiment |')
print('|---|---|---|---|---|---|---|---|---|')
for ion, key, name, via in ROWS:
    try:
        lv = pl.grasp_state(key) if key in pl.RUNS else sc.final_levels(key)
    except Exception as err:
        f = FAC[key]; print(f'| {ion} | {name} | {via} | {f[0]:.2f} | {f[0]:.1f}–{f[1]:.1f} ({f[2]}) | pending (rerun) | | | |'); continue
    e = sorted((v - E_neu) * H for v in lv.values())
    f = FAC[key]
    ws = [c[0] for (k2, j, i), c in pl.COVERAGE.items() if k2 == key]
    frag = f' (main fragment ≥{min(ws):.2f})' if ws and min(ws) < 0.85 else ''
    if key == '2p5':
        g32 = (lv[(3, 0)] - E_neu) * H; g12 = (lv[(1, 0)] - E_neu) * H
        print(f'| {ion} | {name} | {via} | {f[0]:.2f} / {f[1]:.2f} | — | **{g32:.2f} / {g12:.2f}** | — | {g32 - f[0]:+.2f} / {g12 - f[1]:+.2f} | {EXP[key][0]} |')
        continue
    ex = EXP.get(key, ('—', ''))[0]
    print(f'| {ion} | {name} | {via} | {f[0]:.2f} | {f[0]:.1f}–{f[1]:.1f} ({f[2]}) | **{e[0]:.2f}** | {e[0]:.1f}–{e[-1]:.1f} ({len(e)}) | {e[0] - f[0]:+.2f}{frag} | {ex} |')
