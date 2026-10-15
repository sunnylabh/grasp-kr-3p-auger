# -*- coding: utf-8 -*-
"""Spectator-vacancy shifts of Auger kinetic energies in the Kr 2p cascade (GRASP, FAC for comparison).

Shift definitions
  (1) configuration-average shift:  dKE = [E(i+s) - E(f+s)] - [E(i) - E(f)]
      E = (2J+1)-weighted mean of the correlated GRASP level energies of the configuration (main fragments);
  (2) feature-centroid shift: intensity-weighted centroid of the spectator feature minus that of the diagram
      feature (FAC intensities; spectator features weighted with the cascade populations, L3:L2 = 2:1).
Decomposition: U(x,y) = E(xy) - E(x) - E(y) + E(0)  (hole-hole interaction energy, configuration averages);
      to first order  dKE ~ U(s,i) - U(s,f1) - U(s,f2).
"""
import os, sys, json, collections
import numpy as np
B = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, B)
import plot_lmm as pl, secondary as sc, overlap as ov
H = 27.211386245988
SCR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fac_ref')
FACAVG = json.load(open(os.path.join(SCR, 'fac_avg.json')))

def single(scp, occ, core, val_sc_rmx, val_rmx, extra=0.0):
    """levels {(2J,k): E} = SC + core-CI shift + valence main-fragment shift (+ extra BE increment, eV)."""
    S, C = pl.ci_roots(scp, occ), pl.ci_roots(core, occ)
    fr = ov.fragments(val_sc_rmx, val_rmx); Sv = ov.vectors(val_sc_rmx)
    out = {}
    for j, es in S.items():
        for k, e in enumerate(es):
            Em = fr[(j, k)][0][0]
            out[(j, k)] = e + (C[j][k] - e) + (Em - Sv[j][k][0]) + extra / H
    return out

def avg(levels):
    return sum((j + 1) * e for (j, k), e in levels.items()) / sum(j + 1 for (j, k) in levels)

def neutral():
    n_sc = pl.ci_roots('neutral/neutral', '3d10 4s2 4p6')[0][0]
    n_c = pl.ci_roots('c3_neu/neu', '3d10 4s2 4p6')[0][0]
    n_v = pl.ci_roots('W_neu/W_neu', '3d10 4s2 4p6')[0][0]
    return n_sc + (n_c - n_sc) + (n_v - n_sc)

def grasp_states():
    L = {}
    L['3p'] = single('p5', '3p5 3d10 4s2 4p6', 'c3_p5/p5', 'p5.rmx', 'W_p5/W_p5.rmx')
    L['3d'] = single('d9/d9', '3d9 4s2 4p6', 'c3_d9/d9', 'd9/d9.rmx', 'W_d9/W_d9.rmx')
    L['4p'] = single('np5/np5', '3d10 4s2 4p5', 'c3_np5/np5', 'np5/np5.rmx', 'vL1_np5/np5.rmx', sc.L2['4p'])
    L['4p4p'] = single('p4/p4', '3d10 4s2 4p4', 'c3_p4/p4', 'p4/p4.rmx', 'vL1_p4/p4.rmx', sc.L2['pp'])
    for k, key in [('3p3d', '3p5.3d9'), ('3d3d', '3d8'), ('3p3p', '3p4'), ('3d4p', '3d9.4p5')]:
        L[k] = pl.grasp_state(key)
    for k, key in [('3d3d4p', '3d8.4p5'), ('3p3d4p', '3p5.3d9.4p5'), ('4p4p4p', '4p3'), ('3d4p4p', '3d9.4p4')]:
        L[k] = sc.final_levels(key)
    return L

def sc_avg(path):
    """configuration average of single-configuration GRASP levels (for the U decomposition only)."""
    d = os.path.join(B, os.path.dirname(path)); cm = os.path.basename(path)
    import subprocess
    o = subprocess.run([os.path.expanduser('~/grasp/bin/rlevels'), cm], cwd=d, capture_output=True, text=True).stdout
    r, s = [], 0
    for l in o.splitlines():
        if l.startswith('-----'): s += 1; continue
        p = l.split()
        if s == 2 and len(p) >= 5:
            k = next(i for i, t in enumerate(p) if t in '+-'); j = p[k - 1]
            j2 = int(j.split('/')[0]) if '/' in j else 2 * int(j); r.append((j2, float(p[k + 1])))
    return sum((j + 1) * e for j, e in r) / sum(j + 1 for j, e in r)

PAIRS = [  # (label, spectator, diagram initial, diagram final, spectator initial, spectator final, holes for U)
    ('A', '3d', '3p', '3d4p', '3p3d', '3d3d4p', ('3d', '3p', '3d', '4p')),
    ('B', '3p', '3p', '3d4p', '3p3p', '3p3d4p', ('3p', '3p', '3d', '4p')),
    ('C', '4p', '3d', '4p4p', '3d4p', '4p4p4p', ('4p', '3d', '4p', '4p')),
    ('D', '3d', '3d', '4p4p', '3d3d', '3d4p4p', ('3d', '3d', '4p', '4p'))]
TXT = {'A': '3p⁻¹3d⁻¹ → 3d⁻²4p⁻¹  vs  3p⁻¹ → 3d⁻¹4p⁻¹   (spectator 3d)',
       'B': '3p⁻² → 3p⁻¹3d⁻¹4p⁻¹  vs  3p⁻¹ → 3d⁻¹4p⁻¹   (spectator 3p)',
       'C': '3d⁻¹4p⁻¹ → 4p⁻³  vs  3d⁻¹ → 4p⁻²   (spectator 4p)',
       'D': '3d⁻² → 3d⁻¹4p⁻²  vs  3d⁻¹ → 4p⁻²   (spectator 3d)'}

if __name__ == '__main__':
    E0 = neutral(); L = grasp_states()
    A = {k: (avg(v) - E0) * H for k, v in L.items()}; A['0'] = 0.0
    F = dict(FACAVG); F['0'] = 0.0
    print('Configuration-average energies above neutral Kr (eV):  GRASP / FAC')
    for k in A:
        if k != '0': print(f'  {k:8s} {A[k]:9.2f}  {F.get(k, float("nan")):9.2f}')
    print('\nSpectator shifts from configuration averages (eV):')
    res = {}
    for lab, s, i, f, is_, fs, _ in PAIRS:
        g = (A[is_] - A[fs]) - (A[i] - A[f]); fa = (F[is_] - F[fs]) - (F[i] - F[f])
        res[lab] = g
        print(f'  {lab}: {TXT[lab]}:  diagram KE GRASP {A[i] - A[f]:7.2f}, spectator {A[is_] - A[fs]:7.2f}  ->  shift GRASP {g:+.2f}, FAC {fa:+.2f}')
    # hole-hole interaction energies from single-configuration GRASP (decomposition)
    SCP = {'0': 'neutral/neutral.cm', '3p': 'p5.cm', '3d': 'd9/d9.cm', '4p': 'np5/np5.cm', '3p3d': 'p5d9/p5d9.cm',
           '3d3d': 'd8x/d8x.cm', '3p3p': 'p4x/p4x.cm', '3d4p': 'd9p5/d9p5.cm', '3p4p': 'p5np5/p5np5.cm', '4p4p': 'p4/p4.cm'}
    Es = {k: sc_avg(v) for k, v in SCP.items()}
    U = lambda x, y: (Es[''.join(sorted([x, y], key=['3p', '3d', '4p'].index))] - Es[x] - Es[y] + Es['0']) * H \
        if x != y else (Es[x + y] - 2 * Es[x] + Es['0']) * H
    print('\nHole-hole interaction energies U(x,y) (eV, single-configuration GRASP):')
    for x, y in [('3p', '3p'), ('3p', '3d'), ('3p', '4p'), ('3d', '3d'), ('3d', '4p'), ('4p', '4p')]:
        print(f'  U({x},{y}) = {U(x, y):6.2f}')
    print('\nFirst-order estimate  dKE ~ U(s,i) - U(s,f1) - U(s,f2):')
    for lab, s, i, f, is_, fs, (sp, ih, f1, f2) in PAIRS:
        print(f'  {lab}: U({sp},{ih}) - U({sp},{f1}) - U({sp},{f2}) = {U(sp, ih):.2f} - {U(sp, f1):.2f} - {U(sp, f2):.2f} = {U(sp, ih) - U(sp, f1) - U(sp, f2):+.2f}   (full GRASP {res[lab]:+.2f})')

# ---------------- observable (intensity-weighted) centroids ----------------
def diagram_lines(Li, Lf, fac_tag, cfg_i, cfg_f):
    """GRASP KE and FAC KE of the diagram lines, weight (2J_i+1) * A / sum_f A (FAC rates, clean single session)."""
    lev, A = {}, []
    for l in open(os.path.join(SCR, 't', fac_tag + '.lev')):
        p = l.split()
        if len(p) >= 8 and p[0].isdigit():
            try: lev[int(p[0])] = (float(p[2]), int(p[5]), p[7])
            except ValueError: pass
    A = [(int(p[0]), int(p[2]), float(p[4]), float(p[5])) for p in (l.split() for l in open(os.path.join(SCR, 't', fac_tag + '.ai'))) if len(p) == 7 and p[0].isdigit()]
    ri, rf = pl.ranks(lev, cfg_i), pl.ranks(lev, cfg_f); tot = collections.Counter()
    for b, f, e, r in A:
        if b in ri and f in rf: tot[b] += r
    out = []
    for b, f, e, r in A:
        if b in ri and f in rf:
            out.append((e, (Li[ri[b]] - Lf[rf[f]]) * H, (lev[b][1] + 1) * r / tot[b], lev[b][1]))
    return out

def cen(lines, idx, sel=None):
    v = [x for x in lines if sel is None or sel(x)]; W = sum(x[2] for x in v)
    return sum(x[idx] * x[2] for x in v) / W

def rngs(lines, idx, sel=None):
    v = [x for x in lines if sel is None or sel(x)]; mx = max(x[2] for x in v); s = [x[idx] for x in v if x[2] >= 0.03 * mx]
    return min(s), max(s)

if __name__ == '__main__':
    d3p = diagram_lines(L['3p'], L['3d4p'], 'M45N23_bot', '3p5', '3d9.4p5')
    d3d = diagram_lines(L['3d'], L['4p4p'], 'fd_3d_4p4', '3d9', '4p4')
    sec = sc.main()
    def sl(p, f): return [(x[0], x[1], 2 / 3 * x[2] + 1 / 3 * x[3]) for x in sec[(p, f)]]
    SP = {'A': (d3p, sl('3p5.3d9', '3d8.4p5')), 'B': (d3p, sl('3p4', '3p5.3d9.4p5')),
          'C': (d3d, sl('3d9.4p5', '4p3')), 'D': (d3d, sl('3d8', '3d9.4p4'))}
    LIT = {'A': ((90, 94), (98, 102)), 'B': ((90, 94), (98, 102)), 'C': ((51.3, 55.3), (52.5, 56.3)), 'D': ((51.3, 55.3), (52.5, 56.3))}
    print('\nObservable feature centroids (intensity-weighted) and shifts (eV):')
    for lab in 'ABCD':
        dg, sp = SP[lab]
        cg, cf = cen(dg, 1), cen(dg, 0); sg, sf = cen(sp, 1), cen(sp, 0)
        r = rngs(sp, 1); rd = rngs(dg, 1)
        print(f'  {lab}: diagram GRASP {cg:6.2f} (range {rd[0]:.1f}–{rd[1]:.1f}) | spectator GRASP {sg:6.2f} (range {r[0]:.1f}–{r[1]:.1f}) '
              f'-> shift GRASP {sg - cg:+.2f}, FAC {sf - cf:+.2f}')
    # literature anchoring: diagram lines from experiment, shifted by the GRASP spectator shift
    print('\nLiterature-anchored spectator positions (lit. diagram range + GRASP shift, eV):')
    for lab in 'ABCD':
        dg, sp = SP[lab]
        s_c = cen(sp, 1) - cen(dg, 1); s_a = res[lab]
        (a1, a2), (b1, b2) = LIT[lab]
        print(f'  {lab}: lit. diagram {a1}–{a2} / {b1}–{b2}  ->  centroid shift {s_c:+.1f}: {a1 + s_c:.1f}–{b2 + s_c:.1f};  config-average shift {s_a:+.1f}: {a1 + s_a:.1f}–{b2 + s_a:.1f}')
