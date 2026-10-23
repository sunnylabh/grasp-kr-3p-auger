# -*- coding: utf-8 -*-
"""3p-hole CK lines of the Kr2+ 3p-1 3d-1 and 3p-2 parents split into 3p3/2 (M3) and 3p1/2 (M2), FAC vs GRASP.

Uses the line list of secondary.py (GRASP KE per FAC line, FAC weights). The 3p sub-shell is taken from the FAC jj
label of the matched FAC level: for 3p-1 3d-1 the initial level (hole the CK fills), for 3p-2 the final level
(spectator 3p hole). '3p+3' = hole in 3p3/2, '3p-1' = hole in 3p1/2.
"""
import os, sys, inspect, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import secondary as sc

src = inspect.getsource(sc.main).replace('def main():', 'def main_bf():').replace(
    '6.582119569e-16 * tot[b], kf))', '6.582119569e-16 * tot[b], kf, b, f))')
exec(src, sc.__dict__)

def jj(path):
    d = {}
    for l in open(path + '.lev'):
        p = l.split()
        if len(p) > 6 and p[0].isdigit() and p[1] == '-1': d[int(p[0])] = p[-1]
    return d

def sub(label):
    t = label.split('.')[0]
    return 'M3 (3p3/2)' if t.startswith('3p+3') else 'M2 (3p1/2)' if t.startswith('3p-1') else 'mixed'

lines = sc.main_bf()
CH = {'3d8.4p5': 'CK M2,3-M4,5N2,3', '3d8.4s1': 'CK M2,3-M4,5N1',
      '3p5.3d9.4p5': 'CK M2,3-M4,5N2,3', '3p5.3d9.4s1': 'CK M2,3-M4,5N1'}
for pcfg, sess, on in [('3p5.3d9', 'sec_M23M45', 'initial'), ('3p4', 'sec_M23M23', 'final')]:
    J = jj(os.path.join(sc.K, sess))
    print(f'\n{sc.NAME[pcfg]} parent (split on {on} level), L3 gate:')
    print('| Channel | Component | FAC KE (eV) | GRASP KE (eV) | centroid FAC → GRASP (eV) |')
    print('|---|---|---|---|---|')
    g = collections.defaultdict(list)
    for (p, lab), v in lines.items():
        if p != pcfg or lab not in CH: continue
        for x in v:
            g[(CH[lab], sub(J[x[6] if on == 'initial' else x[7]]))].append(x)
    for k in sorted(g):
        v = [x for x in g[k] if x[1] is not None]; mx = max(x[2] for x in v); mx2 = max(x[3] for x in v); s2 = [x for x in v if x[3] >= 0.03 * mx2]
        s = [x for x in v if x[2] >= 0.03 * mx]; W = sum(x[2] for x in v)
        cf, cg = sum(x[0] * x[2] for x in v) / W, sum(x[1] * x[2] for x in v) / W
        print(f'| {k[0]} | {k[1]} | {min(x[0] for x in s):.1f}–{max(x[0] for x in s):.1f} | '
              f'{min(x[1] for x in s):.1f}–{max(x[1] for x in s):.1f} | {cf:.1f} → {cg:.1f} | L2: FAC {min(x[0] for x in s2):.1f}–{max(x[0] for x in s2):.1f}, GRASP {min(x[1] for x in s2):.1f}–{max(x[1] for x in s2):.1f} |')
