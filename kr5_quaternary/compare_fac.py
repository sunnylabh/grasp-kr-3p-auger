"""GRASP single-config vs FAC SC: Kr4+ -> Kr5+ Auger energetics.
For every parent -> final configuration pair: (2J+1)-weighted average KE and the full KE span
(max parent level - min final level, min parent - max final). FAC from
$FAC_KR2P/kr_output/quat_<Q>_SC.lev (FAC-Kr-2p, stage 06;
default FAC_KR2P = ~/Desktop/FAC/Kr 2p)."""
import os, re, subprocess
H2EV = 27.211386245988
G = os.path.dirname(os.path.abspath(__file__))
FAC = os.environ.get('FAC_KR2P', os.path.expanduser('~/Desktop/FAC/Kr 2p')) + '/kr_output'

def grasp(name):
    out = subprocess.run([os.path.expanduser('~/grasp/bin/rlevels'), f'{name}.cm'],
                         cwd=f'{G}/{name}', capture_output=True, text=True).stdout
    lv = []
    for l in out.splitlines():
        p = l.split()
        if len(p) >= 5 and p[0].isdigit() and re.match(r'^-?\d+\.\d+$', p[4]):
            j = p[2]; j2 = int(j.split('/')[0]) if '/' in j else 2 * int(j)
            lv.append((float(p[4]) * H2EV, j2))
    return lv

def fac(tag, nr):
    lv, cur = [], None
    for l in open(f'{FAC}/{tag}.lev'):
        p = l.split()
        if len(p) > 6 and p[0].isdigit() and p[1] == '-1' and p[-2] == nr:
            lv.append((float(p[2]), int(p[5])))
    return lv

avg = lambda lv: sum(e * (j + 1) for e, j in lv) / sum(j + 1 for e, j in lv)

PAIRS = {  # parent: (label, grasp run, FAC label, [(final label, grasp run, FAC label)])
 'Q1': ('3d-2 4p-2', 'q4_d8p4', '3d8.4p4', [('3d-1 4p-4', 'q5_d9p2', '3d9.4p2'), ('3d-1 4s-1 4p-3', 'q5_d9sp3', '3d9.4s1.4p3'), ('3d-1 4s-2 4p-2', 'q5_d9p4', '3d9.4p4')]),
 'Q2': ('3d-2 4s-1 4p-1', 'q4_d8sp5', '3d8.4s1.4p5', [('3d-1 4s-1 4p-3', 'q5_d9sp3', '3d9.4s1.4p3'), ('3d-1 4s-2 4p-2', 'q5_d9p4', '3d9.4p4'), ('3d-2 4p-3 (N-NN CK)', 'q5_d8p3', '3d8.4p3')]),
 'Q3': ('3d-1 4s-1 4p-2', 'q4_d9sp4', '3d9.4s1.4p4', [('4s-1 4p-4', 'q5_sp2', '4s1.4p2'), ('4s-2 4p-3', 'q5_p3', '4p3'), ('3d-1 4p-4 (N-NN CK)', 'q5_d9p2', '3d9.4p2')]),
 'Q4': ('3d-1 4p-3', 'q4_d9p3', '3d9.4p3', [('4p-5', 'q5_p1', '4p1'), ('4s-1 4p-4', 'q5_sp2', '4s1.4p2'), ('4s-2 4p-3', 'q5_p3', '4p3')]),
}
print('| Parent | Kr5+ final | <KE> GRASP | <KE> FAC | GRASP-FAC | KE span GRASP | KE span FAC |')
print('|---|---|---|---|---|---|---|')
for q, (pl, pg, pf, fins) in PAIRS.items():
    P, PF = grasp(pg), fac(f'quat_{q}_SC', pf)
    for fl, fg, ff in fins:
        F, FF = grasp(fg), fac(f'quat_{q}_SC', ff)
        kg, kf = avg(P) - avg(F), avg(PF) - avg(FF)
        sg = (min(e for e, _ in P) - max(e for e, _ in F), max(e for e, _ in P) - min(e for e, _ in F))
        sf = (min(e for e, _ in PF) - max(e for e, _ in FF), max(e for e, _ in PF) - min(e for e, _ in FF))
        print(f'| {q} {pl} | {fl} | {kg:.1f} | {kf:.1f} | {kg-kf:+.1f} | {sg[0]:.1f} to {sg[1]:.1f} | {sf[0]:.1f} to {sf[1]:.1f} |')
