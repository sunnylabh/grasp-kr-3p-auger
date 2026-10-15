# -*- coding: utf-8 -*-
"""Kinetic-energy ranges of the Kr 2p cascade, organised as initial state -> final state, FAC vs GRASP."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plot_lmm as pl, secondary as sc
NAME = sc.NAME

def rng(v, idx, wi):
    mx = max(x[wi] for x in v); s = [x[idx] for x in v if x[wi] >= 0.03 * mx and x[idx] is not None]
    return f'{min(s):.1f}–{max(s):.1f}' if s else 'pending'

# step 1 (from plot_lmm)
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    lines1, _ = pl.main()
TR = {'3d8': 'L-M₄,₅M₄,₅', '3p5.3d9': 'L-M₂,₃M₄,₅', '3p4': 'L-M₂,₃M₂,₃', '3d9.4p5': 'L-M₄,₅N₂,₃'}
print('### Step 1: LMM Auger decay of the 2p hole (Kr⁺ → Kr²⁺)\n')
print('| Initial state | Transition | Final state (Kr²⁺) | KE range FAC (eV) | KE range GRASP (eV) |')
print('|---|---|---|---|---|')
for g, ini in [('L3', 'Kr⁺ 2p₃/₂⁻¹'), ('L2', 'Kr⁺ 2p₁/₂⁻¹')]:
    for cfg in ['3p4', '3p5.3d9', '3d8', '3d9.4p5']:
        v = [x for x in lines1[cfg] if x[4] == g]
        print(f'| {ini} | {g[0]}{g[1]}-{TR[cfg][2:]} | {NAME[cfg]} | {rng(v, 0, 2)} | **{rng(v, 1, 2)}** |')

# step 2
lines2 = sc.main()
CH = {('3d8', '3d9.4s1.4p5'): 'M₄,₅-N₁N₂,₃', ('3d8', '3d9.4p4'): 'M₄,₅-N₂,₃N₂,₃', ('3d8', '3d9'): 'M₄,₅-N₁N₁',
      ('3d9.4p5', '4s1.4p4'): 'M₄,₅-N₁N₂,₃', ('3d9.4p5', '4p3'): 'M₄,₅-N₂,₃N₂,₃', ('3d9.4p5', '4p5'): 'M₄,₅-N₁N₁',
      ('3p5.3d9', '3d8.4p5'): 'CK M₂,₃-M₄,₅N₂,₃', ('3p5.3d9', '3d8.4s1'): 'CK M₂,₃-M₄,₅N₁',
      ('3p4', '3p5.3d9.4p5'): 'CK M₂,₃-M₄,₅N₂,₃', ('3p4', '3p5.3d9.4s1'): 'CK M₂,₃-M₄,₅N₁'}
print('\n### Step 2: Auger / Coster–Kronig decay of the Kr²⁺ states (Kr²⁺ → Kr³⁺)\n')
print('| Initial state (Kr²⁺) | Populated by | Transition | Final state (Kr³⁺) | Branching | KE range FAC (eV) | KE range GRASP (eV) |')
print('|---|---|---|---|---|---|---|')
for pcfg in ['3p4', '3p5.3d9', '3d8', '3d9.4p5']:
    tot = sum(x[2] + x[3] for (p, l), v in lines2.items() if p == pcfg for x in v)
    rows = sorted([(l, v) for (p, l), v in lines2.items() if p == pcfg], key=lambda kv: -sum(x[2] + x[3] for x in kv[1]))
    for lab, v in rows:
        br = 100 * sum(x[2] + x[3] for x in v) / tot
        if br < 2 or (pcfg, lab) not in CH: continue
        # combined L3 + L2 weights (2:1 statistical through the populations)
        vv = [(x[0], x[1], x[2] * 2 / 3 + x[3] / 3) for x in v]   # main-fragment energies
        print(f'| {NAME[pcfg]} | {TR[pcfg]} | {CH[(pcfg, lab)]} | {NAME[lab]} | {br:.0f}% | {rng(vv, 0, 2)} | **{rng(vv, 1, 2)}** |')
