"""pick.py <dir/tag> 'occ' : for each J block, the root whose leading CSF has occupation 'occ'
(e.g. '3d9 4s2 4p6'; CSFs using correlation orbitals excluded). Prints J, root, weight, energy."""
import re, sys, os, subprocess, collections
ALL = '--all' in sys.argv; sys.argv = [a for a in sys.argv if a != '--all']
path, occ = sys.argv[1], dict((m[0], int(m[1])) for m in re.findall(r'(\d[spdf])(\d+)', sys.argv[2]))
d, t = os.path.dirname(path), os.path.basename(path)
# CSF occupations per block
blocks, cur, lines = [], [], open(f'{path}.c').read().splitlines()[5:]
for i, l in enumerate(lines):
    if l.strip() == '*': blocks.append(cur); cur = []; continue
    if re.match(r'^\s+\d[spdf][ -]\(', l):
        o = collections.Counter()
        for sh, n in re.findall(r'(\d[spdf])[ -]\(\s*(\d+)\)', l): o[sh] += int(n)
        cur.append(o)
blocks.append(cur)
isref = [[all(o.get(k, 0) == v for k, v in occ.items()) and not any(o.get(k) for k in ('5s','5p','4d','4f','5d','5f')) for o in b] for b in blocks]
# csum: per block, levels with weights and CSF indices
txt = open(f'{path}.csum').read().split('Level J Parity')[1:]
o = subprocess.run([os.path.expanduser('~/grasp/bin/rlevels'), f'{t}.cm'], cwd=d, capture_output=True, text=True).stdout
E = {}; s = 0
byJ = collections.defaultdict(list)
for l in o.splitlines():
    if l.startswith('-----'): s += 1; continue
    p = l.split()
    if s == 2 and len(p) >= 4:
        k = next((i for i, t in enumerate(p) if t in ('+', '-')), None)   # parity token; J before, energy after
        if k is None or k + 1 >= len(p): continue
        byJ[p[k - 1]].append(float(p[k + 1]))
for J, es in byJ.items():                       # position within the J block = energy order (as in .csum)
    for pos, e in enumerate(sorted(es), 1): E[(J, pos)] = e
for bi, chunk in enumerate(txt):
    ls = [l for l in chunk.splitlines() if l.strip()]
    best = None
    for k in range(1, len(ls) - 1):
        p = ls[k].split()
        if len(p) >= 4 and re.match(r'^\d+$', p[0]) and '/' in p[1] or (len(p) >= 4 and p[0].isdigit() and p[2] in '+-'):
            try: lev, J = int(p[0]), p[1]; w = [float(x) for x in p[3:]]; idx = [int(x) for x in ls[k + 1].split()]
            except ValueError: continue
            wr = sum(wi * wi for wi, ii in zip(w, idx) if isref[bi][ii - 1])   # weights = squared CI coefficients
            if ALL:
                if isref[bi][idx[0] - 1] and abs(w[0]) > 0.5: print(f'J={J:4s} root {lev:3d}  lead {w[0]:+.3f}  E={E[(J, lev)]:.7f}')
                continue
            # lowest root dominated (>=50 %) by the reference configuration; fallback: largest weight
            if wr >= 0.5 and (best is None or best[2] < 0.5): best = (J, lev, wr)
            elif best is None or (best[2] < 0.5 and wr > best[2]): best = (J, lev, wr)
    if ALL: continue
    J, lev, wr = best
    print(f'J={J:4s} root {lev:3d}  ref weight {wr:.3f}  E={E[(J, lev)]:.7f}')
