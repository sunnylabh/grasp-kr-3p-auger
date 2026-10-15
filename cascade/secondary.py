# -*- coding: utf-8 -*-
"""
Second step of the Kr 2p cascade (Kr2+ -> Kr3+), GRASP line energies vs FAC.

KE = E(Kr2+ level) - E(Kr3+ level), both from GRASP:
  E = E_SC + dE_core + dE_val + dE_L2
  dE_core : direct core CI (compact layer {5p,4d,5d,4f,5f}), or
            - 3d-1 + valence holes: core shift of Kr+ 3d-1 (valence holes are spectators, checked to 0.01 eV)
            - 3p-1 3d-1 + valence hole: level-resolved first-order projection of the Kr2+ 3p-1 3d-1 core shifts
              (project_core.py; reproduces the parent exactly, validated on 3d-2 -> 3d-2 4p-1)
  dE_val  : direct valence CI (4s,4p SD into {5s,5p,4d,4f}, core occupations fixed)
  dE_L2   : second valence layer {6s,6p,5d,5f} and own-orbital increments, from the computed hole values
            (4p, 4s, 4s4p, 4p-2, 4s-2); not computed for 3-hole valence combinations -> pair + single.
Intensities: FAC rates (secondary sessions) x parent-level population from the FAC primary step (per gate),
divided by the parent level's total rate. Levels matched by configuration, 2J and energy order.
"""
import os, re, sys, subprocess, collections
import numpy as np
B = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, B)
import project_core as pc
import plot_lmm as pl
H = 27.211386245988
K = os.environ.get('FAC_KR2P', os.environ.get('FAC_KR2P', os.path.expanduser('~/Desktop/FAC/Kr 2p'))) + '/kr_output'; CI = os.environ.get('FAC_KR2P', os.environ.get('FAC_KR2P', os.path.expanduser('~/Desktop/FAC/Kr 2p'))) + '/02_secondary_Kr3+/CI'

# valence-hole increments beyond layer 1 (eV, in binding energy): L2 layer + own orbitals where computed
L2 = {'4p': 0.23 + 0.10, '4s': -0.08 - 0.22, 'sp': 0.33, 'pp': 0.45, 'ss': 0.03}
def l2_shift(holes):
    h = list(holes); e = 0.0
    while '4s' in h and '4p' in h: h.remove('4s'); h.remove('4p'); e += L2['sp']
    while h.count('4s') >= 2: h.remove('4s'); h.remove('4s'); e += L2['ss']
    while h.count('4p') >= 2: h.remove('4p'); h.remove('4p'); e += L2['pp']
    return e + sum(L2[x] for x in h if x in L2)

FINAL = {  # FAC label: (SC run, occ, core source, valence run, valence holes)
 '3d9.4s1.4p5': ('d9sp/d9sp', '3d9 4s1 4p5', ('uniform', 'd9/d9', 'c3_d9/d9', '3d9 4s2 4p6'), 'F_v_d9sp/F_v_d9sp', ['4s', '4p']),
 '3d9.4p4':     ('d9p4/d9p4', '3d9 4s2 4p4', ('uniform', 'd9/d9', 'c3_d9/d9', '3d9 4s2 4p6'), 'F_v_d9p4/F_v_d9p4', ['4p', '4p']),
 '3d9':         ('d9s0/d9s0', '3d9 4s0 4p6', ('direct', 'F_c_d9s0/F_c_d9s0'), 'F_v_d9s0/F_v_d9s0', ['4s', '4s']),
 '4s1.4p4':     ('sp4/sp4', '3d10 4s1 4p4', ('direct', 'F_c_sp4/F_c_sp4'), 'F_v_sp4/F_v_sp4', ['4s', '4p', '4p']),
 '4p5':         ('s0p5/s0p5', '3d10 4s0 4p5', ('direct', 'F_c_s0p5/F_c_s0p5'), 'F_v_s0p5/F_v_s0p5', ['4s', '4s', '4p']),
 '4p3':         ('p3/p3', '3d10 4s2 4p3', ('direct', 'F_c_p3/F_c_p3'), 'F_v_p3/F_v_p3', ['4p', '4p', '4p']),
 '3d8.4p5':     ('d8p5/d8p5', '3d8 4s2 4p5', ('direct', 'F_c_d8p5/F_c_d8p5'), 'F_v_d8p5/F_v_d8p5', ['4p']),
 '3d8.4s1':     ('d8s1/d8s1', '3d8 4s1 4p6', ('direct', 'F_c_d8s1/F_c_d8s1'), 'F_v_d8s1/F_v_d8s1', ['4s']),
 '3p5.3d9.4p5': ('pdp/pdp', '3p5 3d9 4s2 4p5', ('project', 'p5d9/p5d9.rmx', 'p5d9/p5d9', 'D_c_p5d9/D_c_p5d9', '3p5 3d9 4s2 4p6', 'pdp/pdp.rmx'), 'F_v_pdp/F_v_pdp', ['4p']),
 '3p5.3d9.4s1': ('pds/pds', '3p5 3d9 4s1 4p6', ('project', 'p5d9/p5d9.rmx', 'p5d9/p5d9', 'D_c_p5d9/D_c_p5d9', '3p5 3d9 4s2 4p6', 'pds/pds.rmx'), 'F_v_pds/F_v_pds', ['4s'])}
PARENT_HOLES = {'3d8': [], '3p5.3d9': [], '3p4': [], '3d9.4p5': ['4p']}   # valence holes (L2 increments)

FILLED = {}   # (state, 2J, k) -> (valence shift used, sd of certified levels) for levels filled by the spectator rule
def roots(p, occ): return pl.ci_roots(p, occ)
def j2s(j2): return f'{j2}/2' if j2 % 2 else str(j2 // 2)

def final_levels(lab):
    scp, occ, core, vp, vh = FINAL[lab]
    import overlap as ov
    S = roots(scp, occ)
    fr = ov.fragments(scp + '.rmx', vp + '.rmx'); Sv = ov.vectors(scp + '.rmx')
    if core[0] == 'direct':
        C = roots(core[1], occ); dc = lambda j, k: C[j][k] - S[j][k]
    elif core[0] == 'uniform':
        Sp, Cp = roots(core[1], core[3]), roots(core[2], core[3])
        m = np.mean([Cp[j][k] - Sp[j][k] for j in Sp for k in range(len(Sp[j]))]); dc = lambda j, k: m
    else:
        dH = pc.parent_operator(os.path.join(B, core[1]), core[2], core[3], core[4])
        pr = collections.defaultdict(list)
        for g, E, s in pc.project(dH, os.path.join(B, core[5])): pr[g - 1].append((E, s))
        P = {j: [s for E, s in sorted(v)] for j, v in pr.items()}
        # pick the reference-dominated SC levels: match SC energies to the rmx eigen-energies
        allE = {j: sorted(v) for j, v in pr.items()}
        def dc(j, k, S=S, allE=allE):
            e = S[j][k]; i = int(np.argmin([abs(x[0] - e) for x in allE[j]])); return allE[j][i][1]
    # main-fragment valence shifts for the levels whose main fragment is certain (bound: w_main > 1 - captured)
    shifts, todo = {}, []
    for j, es in S.items():
        for k, e in enumerate(es):
            kk = min(range(len(Sv[j])), key=lambda i: abs(Sv[j][i][0] - e))
            F = fr[(j, kk)]; cap = sum(w for _, w in F)
            if F and F[0][1] > 1.0 - cap:
                shifts[(j, k)] = F[0][0] - Sv[j][kk][0]
                pl.COVERAGE[(lab, j, k)] = (F[0][1], cap); pl.FRAG[(lab, j, k)] = [(E - F[0][0], w) for E, w in F]
            else:
                todo.append((j, k))
    if todo:   # spectator rule: the valence shift is level-independent if the certified levels show it
        v = list(shifts.values()); m = sum(v) / len(v); sd = (sum((x - m) ** 2 for x in v) / len(v)) ** 0.5
        if len(v) < 0.7 * (len(v) + len(todo)) or sd * H > 0.1:
            raise RuntimeError(f'{lab}: {len(todo)} levels uncertain and valence shifts not uniform (sd {sd * H:.2f} eV)')
        for key in todo:
            shifts[key] = m; FILLED[(lab,) + key] = (m * H, sd * H)
    out = {}
    for j, es in S.items():
        for k, e in enumerate(es):
            out[(j, k)] = e + dc(j, k) + shifts[(j, k)] + l2_shift(vh) / H
    return out

def main():
    # initial Kr2+ levels (direct GRASP, as in plot_lmm) + their L2 increments
    INIT = {cfg: pl.grasp_state(cfg) for cfg in ['3d8', '3p5.3d9', '3p4', '3d9.4p5']}
    # plot_lmm.grasp_state already applies the 4p-hole increment (0.33 eV = L2['4p']) to 3d9.4p5
    FIN = {}
    for lab in FINAL:
        try: FIN[lab] = final_levels(lab)
        except Exception as err: FIN[lab] = {}; print('#', lab, 'not available:', str(err)[:80])
    # populations of Kr2+ levels from the FAC primary step
    pop = {'L3': collections.Counter(), 'L2': collections.Counter()}
    for fn in ['kr_LMM', 'kr_M45N23']:
        L, A = pl.fac(fn); rk = {}
        for cfg in set(v[2] for v in L.values()): rk.update({i: (cfg,) + r for i, r in pl.ranks(L, cfg).items()})
        for b, f, e, r in A:
            if 900 < e < 2000: pop['L3' if L[b][1] == 3 else 'L2'][rk[f]] += r
    SEC = [('3d8', os.path.join(K, 'sec_M45M45')), ('3d9.4p5', os.path.join(CI, 'd9p5_sc')),
           ('3p5.3d9', os.path.join(K, 'sec_M23M45')), ('3p4', os.path.join(K, 'sec_M23M23'))]
    lines = collections.defaultdict(list)    # (parent, final) -> [(KE_fac, KE_grasp, w_L3, w_L2, Gamma)]
    for pcfg, path in SEC:
        L = {}; A = []
        for l in open(path + '.lev'):
            p = l.split()
            if len(p) >= 8 and p[0].isdigit():
                try: L[int(p[0])] = (float(p[2]), int(p[5]), p[7])
                except ValueError: pass
        A = [(int(p[0]), int(p[2]), float(p[4]), float(p[5])) for p in (l.split() for l in open(path + '.ai')) if len(p) == 7 and p[0].isdigit()]
        ri = pl.ranks(L, pcfg); tot = collections.Counter()
        for b, f, e, r in A:
            if b in ri: tot[b] += r
        rf = {}
        for lab in FINAL:
            rf.update({i: (lab,) + v for i, v in pl.ranks(L, lab).items()})
        for b, f, e, r in A:
            if b not in ri or f not in rf or e <= 0: continue
            lab = rf[f][0]; kf = rf[f][1:]; ki = ri[b]
            keg = (INIT[pcfg][ki] - FIN[lab][kf]) * H if (kf in FIN[lab] and ki in INIT[pcfg]) else None
            w3 = pop['L3'][(pcfg,) + ki] * r / tot[b]; w2 = pop['L2'][(pcfg,) + ki] * r / tot[b]
            lines[(pcfg, lab)].append((e, keg, w3, w2, 6.582119569e-16 * tot[b], kf))
    return lines

NAME = {'3d8': '3d⁻²', '3p5.3d9': '3p⁻¹3d⁻¹', '3p4': '3p⁻²', '3d9.4p5': '3d⁻¹4p⁻¹',
        '3d9.4s1.4p5': '3d⁻¹4s⁻¹4p⁻¹', '3d9.4p4': '3d⁻¹4p⁻²', '3d9': '3d⁻¹4s⁻²', '4s1.4p4': '4s⁻¹4p⁻²', '4p5': '4s⁻²4p⁻¹',
        '4p3': '4p⁻³', '3d8.4p5': '3d⁻²4p⁻¹', '3d8.4s1': '3d⁻²4s⁻¹', '3p5.3d9.4p5': '3p⁻¹3d⁻¹4p⁻¹', '3p5.3d9.4s1': '3p⁻¹3d⁻¹4s⁻¹'}

if __name__ == '__main__':
    lines = main()
    print('| Parent | Kr³⁺ final | Share L3 / L2 | FAC range L3 | GRASP range L3 | GRASP range L2 | strongest FAC → GRASP (L3) |')
    print('|---|---|---|---|---|---|---|')
    for pcfg in ['3d8', '3d9.4p5', '3p5.3d9', '3p4']:
        tot3 = sum(x[2] for (p, l), v in lines.items() if p == pcfg for x in v); tot2 = sum(x[3] for (p, l), v in lines.items() if p == pcfg for x in v)
        for (p, lab), v in sorted(lines.items(), key=lambda kv: -sum(x[2] for x in kv[1])):
            if p != pcfg: continue
            s3, s2 = sum(x[2] for x in v) / tot3 * 100, sum(x[3] for x in v) / tot2 * 100
            def rng(idx, wi):
                mx = max(x[wi] for x in v); s = [x[idx] for x in v if x[wi] >= 0.03 * mx]; return f'{min(s):.1f}–{max(s):.1f}'
            b = max(v, key=lambda x: x[2])
            print(f'| {NAME[pcfg]} | {NAME[lab]} | {s3:.0f}% / {s2:.0f}% | {rng(0, 2)} | **{rng(1, 2)}** | **{rng(1, 3)}** | {b[0]:.1f} → {b[1]:.1f} |')
