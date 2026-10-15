"""First-order transfer of level-resolved core-correlation shifts from a core-hole parent ion to a final
state that has the same core holes plus spectator valence holes.

The core-correlation correction is represented in the parent's core CSF space as
    dH^J = sum_k |k> delta_k <k|          (k = parent levels of total J, delta_k = E_coreCI - E_SC, direct)
and, because the valence holes are spectators (checked: 3d-1 vs 3d-1 4p-1 differ by 0.01 eV), it acts on the
core part of each final-state CSF only:
    <a|dH|b> = [valence parts of a and b identical] * dH^{J1}(core_a, core_b),
J1 being the intermediate coupling of the core subshells. The final-level shift is the expectation value
c^T dH c over the full GRASP eigenvector (from rmixextract, cut-off 0).

usage: project_core.py <parent rmx> <parent SC dir/name> <parent coreCI dir/name> <parent occ> <final rmx>
"""
import re, sys, os, subprocess, collections

CORE = ['3s', '3p-', '3p', '3d-', '3d']
VAL = ['4s', '4p-', '4p']

def parse_csf(l1, l2, l3):
    """-> dict subshell -> (occ, j or '', coupling or ''), final J (with parity)."""
    fields = [(m.group(1).strip(), int(m.group(2)), m.end()) for m in re.finditer(r'(\d[spdf][ -])\(\s*(\d+)\)', l1)]
    ends = {name: end for name, occ, end in fields}
    j = {}; c = {}
    for m in re.finditer(r'\S+', l2):
        for name, end in ends.items():
            if m.end() == end: j[name] = m.group()
    toks = list(re.finditer(r'\S+', l3))
    final = toks[-1].group() if toks else ''
    for m in toks[:-1]:
        for name, end in ends.items():
            if m.end() == end + 3 or m.end() == end + 4: c[name] = m.group()
    sub = {name: (occ, j.get(name, ''), c.get(name, '')) for name, occ, end in fields}
    return sub, final

def keys(sub, final):
    core = tuple((s, sub[s]) for s in CORE if s in sub)
    # intermediate coupling of the core: last coupling printed among core subshells, else the j of the single open one
    J1 = ''
    for s in CORE:
        if s in sub and sub[s][2]: J1 = sub[s][2]
    if not J1:
        opens = [sub[s][1] for s in CORE if s in sub and sub[s][1]]
        J1 = opens[-1] if len(opens) == 1 else (final.rstrip('+-') if not any(v in sub for v in VAL) else '')
    val = tuple((s, sub[s]) for s in VAL if s in sub) + (final,)
    corekey = tuple((s, o[0], o[1]) for s, o in core) + (J1,)
    return corekey, val, J1

def read_rmx(fn):
    """-> list of (2J+1, energy, [(coef, corekey, valkey, J1)])"""
    L = open(fn).read().splitlines(); out = []; i = 0; g = None
    while i < len(L):
        l = L[i]
        m = re.search(r'2J\+1 =\s+(\d+)', l)
        if m: g = int(m.group(1))
        m = re.match(r'\s+Energy =\s+(-?\d+\.\d+)', l)
        if m:
            E = float(m.group(1)); vec = []; i += 1
            while i < len(L) and not L[i].strip().startswith('Energy') and not L[i].startswith('   ====='):
                mm = re.match(r'\s+\d+\s+(-?\d+\.\d+)\s*$', L[i])
                if mm:
                    sub, fin = parse_csf(L[i + 1], L[i + 2], L[i + 3])
                    ck, vk, J1 = keys(sub, fin); vec.append((float(mm.group(1)), ck, vk, J1)); i += 4; continue
                i += 1
            out.append((g, E, vec)); continue
        i += 1
    return out

def parent_operator(rmx, scp, ccp, occ):
    """dH[J1][(core_a, core_b)] from the parent eigenvectors and the direct core-CI shifts."""
    B = os.path.dirname(os.path.abspath(__file__))
    def roots(p):
        o = subprocess.run(['python3', os.path.join(B, 'pick.py'), os.path.join(B, p), occ, '--all'], capture_output=True, text=True).stdout
        r = collections.defaultdict(list)
        for j, e in re.findall(r'J=(\S+)\s+root.*E=(\S+)', o): r[j].append(float(e))
        return {k: sorted(v) for k, v in r.items()}
    S, C = roots(scp), roots(ccp)
    states = read_rmx(rmx)
    byJ = collections.defaultdict(list)
    for g, E, vec in states: byJ[g].append((E, vec))
    dH = collections.defaultdict(lambda: collections.defaultdict(float))
    for g, lst in byJ.items():
        J = str(g - 1) + '/2' if (g - 1) % 2 else str((g - 1) // 2)
        lst.sort(key=lambda x: x[0])
        for k, (E, vec) in enumerate(lst):
            if J not in S or k >= len(S[J]): continue
            d = C[J][k] - S[J][k]
            for ca, a, _, Ja in vec:
                for cb, b, _, Jb in vec:
                    dH[J][(a, b)] += ca * cb * d
    return dH

def project(dH, rmx_final):
    res = []
    for g, E, vec in read_rmx(rmx_final):
        s = 0.0
        for ca, a, va, Ja in vec:
            for cb, b, vb, Jb in vec:
                if va == vb and Ja == Jb and Ja in dH: s += ca * cb * dH[Ja].get((a, b), 0.0)
        res.append((g, E, s))
    return res

if __name__ == '__main__':
    prmx, scp, ccp, occ, frmx = sys.argv[1:6]
    dH = parent_operator(prmx, scp, ccp, occ)
    H = 27.211386245988
    for g, E, s in sorted(project(dH, frmx), key=lambda x: (x[0], x[1])):
        print(f'2J+1={g:2d}  E_SC={E:.7f}  core shift {s * H:+.3f} eV')
