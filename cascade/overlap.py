"""Strength-weighted valence-CI level energies.

For each single-configuration (SC) level k and each valence-CI root r of the same J,
    w_kr = <SC_k | root_r>^2   (overlap over the reference CSFs, matched by their full jj coupling)
and the correlated level energy is the strength-weighted centroid  E_k = sum_r w_kr E_r / sum_r w_kr.
For an unfragmented level this is the single dominant root; for a fragmented one (e.g. 4s-hole states mixing
with 4p^-2 nd) it is the first moment of the fragment distribution, i.e. what a broadened spectrum shows.
The coverage sum_r w_kr tells how much of the level's strength the computed roots contain.
"""
import os, collections
import project_core as pc

B = os.path.dirname(os.path.abspath(__file__))

def vectors(rmx):
    """-> {2J: [(E, {csfkey: coef})]} sorted by energy."""
    out = collections.defaultdict(list)
    for g, E, vec in read_full(os.path.join(B, rmx)):
        out[g - 1].append((E, vec))
    return {j: sorted(v, key=lambda x: x[0]) for j, v in out.items()}

def read_full(fn):
    import re
    L = open(fn).read().splitlines(); res = []; i = 0; g = None
    while i < len(L):
        l = L[i]
        m = re.search(r'2J\+1 =\s+(\d+)', l)
        if m: g = int(m.group(1))
        m = re.match(r'\s+Energy =\s+(-?\d+\.\d+)', l)
        if m:
            E = float(m.group(1)); vec = {}; i += 1
            while i < len(L) and not L[i].strip().startswith('Energy') and not L[i].startswith('   ====='):
                mm = re.match(r'\s+\d+\s+(-?\d+\.\d+)\s*$', L[i])
                if mm:
                    sub, fin = pc.parse_csf(L[i + 1], L[i + 2], L[i + 3])
                    key = tuple(sorted((s, v) for s, v in sub.items() if v[0] > 0)) + (fin,)
                    vec[key] = vec.get(key, 0.0) + float(mm.group(1)); i += 4; continue
                i += 1
            res.append((g, E, vec)); continue
        i += 1
    return res

def centroids(sc_rmx, ci_rmx):
    """-> {(2J, k): (E_centroid, coverage)} for the SC levels (k = energy order within 2J)."""
    S, C = vectors(sc_rmx), vectors(ci_rmx)
    out = {}
    for j, levs in S.items():
        for k, (Es, a) in enumerate(levs):
            num = den = 0.0
            for Er, b in C.get(j, []):
                s = sum(c * b.get(key, 0.0) for key, c in a.items())
                num += s * s * Er; den += s * s
            out[(j, k)] = (num / den if den > 0 else float('nan'), den)
    return out

def fragments(sc_rmx, ci_rmx):
    """-> {(2J, k): [(E_r, w_kr), ...] sorted by weight}: the CI roots carrying the SC level's strength."""
    S, C = vectors(sc_rmx), vectors(ci_rmx)
    out = {}
    for j, levs in S.items():
        for k, (Es, a) in enumerate(levs):
            fr = []
            for Er, b in C.get(j, []):
                s = sum(c * b.get(key, 0.0) for key, c in a.items())
                if s * s > 1e-4: fr.append((Er, s * s))
            out[(j, k)] = sorted(fr, key=lambda x: -x[1])
    return out
