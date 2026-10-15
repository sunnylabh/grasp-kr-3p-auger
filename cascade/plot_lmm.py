# -*- coding: utf-8 -*-
"""
Kr L-MM / L-MN Auger spectrum after 2p ionisation: GRASP and FAC.

GRASP line energies come directly from GRASP level energies,
    KE = E(Kr+ 2p^-1 level) - E(Kr2+ level),
with each level energy = single-configuration DHF/RCI + core-correlation CI increment
(compact layer {5p,4d,5d,4f,5f}) + valence-correlation CI increment (layer {5s,5p,4d,4f}),
all computed directly for every level (runs D_c_*, D_v_*, ci_d9p5). The 3d^-1 4p^-1 state also
gets the second-valence-layer and own-orbital increments of the 4p hole (+0.33 eV in binding energy).
Line intensities: FAC rates (kr_LMM, kr_M45N23); GRASP and FAC levels matched by configuration, 2J and
energy order. L3 : L2 = 2 : 1 (statistical 2p photoionisation). Lorentzian width = Gamma(2p) +
Gamma(Kr2+ level) from the FAC secondary sessions; Gaussian instrument width 0.5 eV.
3s-hole final states (L-M1M2,3, L-M1M4,5) are not included: no GRASP 3s-hole calculation.

Outputs: figures/GRASP_LMM.{png,pdf}, figures/GRASP_vs_FAC_LMM.{png,pdf}
"""
import os, re, sys, subprocess, collections
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

B = os.path.dirname(os.path.abspath(__file__))
K = os.environ.get('FAC_KR2P', os.environ.get('FAC_KR2P', os.path.expanduser('~/Desktop/FAC/Kr 2p'))) + '/kr_output'
OUT = os.path.join(B, 'figures')
H = 27.211386245988; HBAR = 6.582119569e-16
sys.path.insert(0, os.environ.get('FAC_KR2P', os.environ.get('FAC_KR2P', os.path.expanduser('~/Desktop/FAC/Kr 2p'))) + '/05_spectrum_and_summary')
import kr_spectrum as ks

INK, INK2, GRID_C, SURF = '#0b0b0b', '#52514e', '#e4e3df', '#fcfcfb'
STATES = [('3d8', '3d⁻²', 'L-M₄,₅M₄,₅', '#2a78d6'), ('3p5.3d9', '3p⁻¹3d⁻¹', 'L-M₂,₃M₄,₅', '#eb6834'),
          ('3p4', '3p⁻²', 'L-M₂,₃M₂,₃', '#1baf7a'), ('3d9.4p5', '3d⁻¹4p⁻¹', 'L-M₄,₅N₂,₃', '#eda100')]
# GRASP runs per state: (SC dir/cm, core CI, valence CI, reference occupation, extra BE increment eV)
RUNS = {  # SC levels, core CI, valence CI, SC baseline of the valence CI, reference occupation, extra BE increment (eV)
    '2p5':     ('p2/p2',     'D_c_p2/D_c_p2',     'W_p2/W_p2',     'p2/p2',     '2p5 3d10 4s2 4p6', 0.0),
    '3d8':     ('d8x/d8x',   'D_c_d8/D_c_d8',     'W_d8/W_d8',     'd8x/d8x',   '3d8 4s2 4p6', 0.0),
    '3p5.3d9': ('p5d9/p5d9', 'D_c_p5d9/D_c_p5d9', 'W_p5d9/W_p5d9', 'p5d9/p5d9', '3p5 3d9 4s2 4p6', 0.0),
    '3p4':     ('p4s/p4s',   'D_c_p4s/D_c_p4s',   'W_p4/W_p4',     'p4x/p4x',   '3p4 3d10 4s2 4p6', 0.0),
    '3d9.4p5': ('d9p5/d9p5', 'D_c_d9p5/D_c_d9p5', 'W_d9p5/W_d9p5', 'd9p5/d9p5', '3d9 4s2 4p5', 0.33)}

def j2(j): return int(j.split('/')[0]) if '/' in j else 2 * int(j)
def sc_levels(path, occ):
    """SC levels {(2J, rank): E}, keeping only levels whose leading CSF has the reference occupation."""
    d = os.path.join(B, os.path.dirname(path)); cm = os.path.basename(path)
    o = subprocess.run([os.path.expanduser('~/grasp/bin/rlevels'), cm], cwd=d, capture_output=True, text=True).stdout
    r, s = collections.defaultdict(list), 0
    for l in o.splitlines():
        if l.startswith('-----'): s += 1; continue
        p = l.split()
        if s == 2 and len(p) >= 5: r[j2(p[2])].append(float(p[4]))
    return r
def ci_roots(path, occ):
    o = subprocess.run(['python3', os.path.join(B, 'pick.py'), os.path.join(B, path), occ, '--all'], capture_output=True, text=True).stdout
    r = collections.defaultdict(list)
    for j, e in re.findall(r'J=(\S+)\s+root.*E=(\S+)', o): r[j2(j)].append(float(e))
    return {k: sorted(v) for k, v in r.items()}
COVERAGE = {}   # (state, 2J, k) -> (weight of main fragment, total captured weight)
FRAG = {}       # (state, 2J, k) -> [(E_fragment - E_main, weight)]
def grasp_state(key):
    """E(level) = E_SC + [E_coreCI - E_SC] + [<E>_valCI - E_SC(valence baseline)] + extra/H.
    <E>_valCI = energy of the main fragment: the valence-CI root with the largest overlap^2 with the SC level (overlap.py)."""
    import overlap as ov
    scp, cp, vp, vb, occ, extra = RUNS[key]
    S, C = ci_roots(scp, occ), ci_roots(cp, occ)
    fr = ov.fragments(vb + '.rmx', vp + '.rmx'); Sv = ov.vectors(vb + '.rmx')
    out = {}
    for j, es in S.items():
        for k, e in enumerate(es):
            if j not in C or k >= len(C[j]) or (j, k) not in fr or not fr[(j, k)]:
                raise RuntimeError(f'{key}: missing root 2J={j} rank {k}')
            F = fr[(j, k)]; Em, wm = F[0]                     # main fragment = line position
            COVERAGE[(key, j, k)] = (wm, sum(w for _, w in F)); FRAG[(key, j, k)] = [(E - Em, w) for E, w in F]
            out[(j, k)] = e + (C[j][k] - e) + (Em - Sv[j][k][0]) + extra / H
    return out

def fac(fn):
    L = {}
    for l in open(os.path.join(K, fn + '.lev')):
        p = l.split()
        if len(p) >= 8 and p[0].isdigit():
            try: L[int(p[0])] = (float(p[2]), int(p[5]), p[7])
            except ValueError: pass
    A = [(int(p[0]), int(p[2]), float(p[4]), float(p[5])) for p in (l.split() for l in open(os.path.join(K, fn + '.ai'))) if len(p) == 7 and p[0].isdigit()]
    return L, A
def ranks(L, cfg):
    r = {}
    for j in set(v[1] for v in L.values() if v[2] == cfg):
        for k, i in enumerate(sorted([i for i in L if L[i][2] == cfg and L[i][1] == j], key=lambda i: L[i][0])): r[i] = (j, k)
    return r

def main():
    # GRASP level energies
    ini = grasp_state('2p5')
    E = {cfg: grasp_state(cfg) for cfg, *_ in STATES}
    # Kr2+ level widths from the FAC secondary sessions
    G2 = {}
    for cfg, sess in [('3d8', 'sec_M45M45'), ('3p5.3d9', 'sec_M23M45'), ('3p4', 'sec_M23M23'), ('3d9.4p5', 'sec_M45N23')]:
        L, A = fac(sess); ri = ranks(L, cfg); t = collections.Counter()
        for b, f, e, r in A:
            if b in ri and 0 < e < 300: t[ri[b]] += r
        G2.update({(cfg,) + k: HBAR * v for k, v in t.items()})
    lines = collections.defaultdict(list)            # cfg -> [(KE_fac, KE_grasp, weight, width)]
    tot = collections.Counter()
    for fn in ['kr_LMM', 'kr_M45N23']:
        L, A = fac(fn); rk = {}
        for cfg in set(v[2] for v in L.values()): rk.update({i: (cfg,) + r for i, r in ranks(L, cfg).items()})
        for b, f, e, r in A:
            if 900 < e < 2000: tot['L3' if L[b][1] == 3 else 'L2'] += r
    for fn in ['sec_CK_L2L3N23', 'sec_CK_L2L3N1']:
        L, A = fac(fn); tot['L2'] += sum(r for b, f, e, r in A if L[b][1] == 1 and e < 100)
    for fn in ['kr_LMM', 'kr_M45N23']:
        L, A = fac(fn); rk = {}
        for cfg in set(v[2] for v in L.values()): rk.update({i: (cfg,) + r for i, r in ranks(L, cfg).items()})
        for b, f, e, r in A:
            if not 900 < e < 2000: continue
            cfg = L[f][2]
            if cfg not in E: continue
            g = 'L3' if L[b][1] == 3 else 'L2'
            jb = L[b][1]; kf = rk[f][1:]
            ke_g = (ini[(jb, 0)] - E[cfg][kf]) * H
            w = (2 / 3 if g == 'L3' else 1 / 3) * r / tot[g] * 100
            lines[cfg].append((e, ke_g, w, {'L3': 1.11, 'L2': 1.17}[g] + G2.get(rk[f], 0.0), g))
    grid = np.arange(1150, 1650, 0.1)
    spec = lambda ke, w, g: ks.synth_spectrum(np.array(ke), np.array(w), np.array(g), grid, gauss_fwhm=0.5)
    curves = {cfg: (spec([x[1] for x in v], [x[2] for x in v], [x[3] for x in v]),
                    spec([x[0] for x in v], [x[2] for x in v], [x[3] for x in v])) for cfg, v in lines.items()}

    plt.rcParams.update({'font.size': 11, 'axes.edgecolor': INK, 'axes.labelcolor': INK, 'xtick.color': INK, 'ytick.color': INK})
    def frame(ax):
        ax.set_facecolor(SURF); ax.set_xlim(grid[0], grid[-1])
        ax.xaxis.set_minor_locator(AutoMinorLocator(5)); ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        ax.tick_params(which='both', direction='in', top=True, right=True)
        ax.tick_params(which='major', length=6, width=1); ax.tick_params(which='minor', length=3, width=0.8)
        ax.grid(axis='y', color=GRID_C, lw=0.6); ax.set_axisbelow(True)
        ax.set_xlabel('Auger electron kinetic energy (eV)'); ax.set_ylabel('Intensity (arb. u.)')

    # ---- Figure 1: GRASP only ----
    fig, ax = plt.subplots(figsize=(10, 5.2), facecolor=SURF); frame(ax)
    for cfg, lab, tr, c in STATES:
        y = curves[cfg][0]
        ax.fill_between(grid, y, color=c, alpha=0.12, lw=0)
        ax.plot(grid, y, color=c, lw=1.6, label=f'{lab}  ←  {tr}')
    ymax = max(curves[c][0].max() for c, *_ in STATES); ax.set_ylim(0, ymax * 1.25)
    ax.legend(title='Kr²⁺ final state  ←  Auger transition', frameon=False, fontsize=9.5, title_fontsize=9.5, loc='upper left')
    ax.set_title('Kr 2p⁻¹ L-MM / L-MN Auger spectrum, GRASP (2p₃/₂ : 2p₁/₂ = 2 : 1)', loc='left', fontsize=12)
    ax.text(0.995, 0.97, 'L₃ and L₂ series', transform=ax.transAxes, ha='right', va='top', fontsize=9, color=INK2)
    for ext in ('png', 'pdf'): fig.savefig(os.path.join(OUT, f'GRASP_LMM.{ext}'), dpi=200, bbox_inches='tight', facecolor=SURF)

    # ---- Figure 2: GRASP vs FAC (total spectra) ----
    yg = sum(curves[c][0] for c, *_ in STATES); yf = sum(curves[c][1] for c, *_ in STATES)
    fig, ax = plt.subplots(figsize=(10, 5.2), facecolor=SURF); frame(ax)
    ax.plot(grid, yf, color='#8a8984', lw=1.4, ls=(0, (4, 2)), label='FAC')
    ax.plot(grid, yg, color='#2a78d6', lw=1.8, label='GRASP')
    ax.set_ylim(0, max(yg.max(), yf.max()) * 1.2)
    # state labels above the strongest GRASP peak of each feature, per series
    for cfg, lab, tr, c in STATES:
        for g, sub in [('L3', '₃'), ('L2', '₂')]:          # one label per series, above the strongest GRASP line
            v = [x for x in lines[cfg] if x[4] == g]
            if not v: continue
            k = max(v, key=lambda x: x[2])[1]; i = np.argmin(abs(grid - k))
            if yg[i] < 0.04 * yg.max(): continue
            ax.annotate(f'L{sub}: {lab}', (grid[i], max(yg[i], yf[i])), xytext=(0, 6), textcoords='offset points', ha='center', fontsize=8.5, color=INK2)
    ax.legend(frameon=False, fontsize=10, loc='upper left')
    ax.set_title('Kr 2p⁻¹ L-MM / L-MN Auger spectrum: GRASP vs FAC (same FAC intensities)', loc='left', fontsize=12)
    for ext in ('png', 'pdf'): fig.savefig(os.path.join(OUT, f'GRASP_vs_FAC_LMM.{ext}'), dpi=200, bbox_inches='tight', facecolor=SURF)

    # ---- table of line ranges ----
    print(f"{'line':22s} {'FAC range (eV)':>18s} {'GRASP range (eV)':>18s} {'strongest FAC':>14s} {'strongest GRASP':>16s}")
    for cfg, lab, tr, c in STATES:
        for g in ['L3', 'L2']:
            v = [x for x in lines[cfg] if x[4] == g]
            if not v: continue
            mx = max(x[2] for x in v); s = [x for x in v if x[2] >= 0.03 * mx]; b = max(v, key=lambda x: x[2])
            print(f"{g + '-' + tr[2:] + ' (' + lab + ')':22s} {min(x[0] for x in s):8.1f}–{max(x[0] for x in s):7.1f} "
                  f"{min(x[1] for x in s):8.1f}–{max(x[1] for x in s):7.1f} {b[0]:14.1f} {b[1]:16.1f}")
    return lines, curves

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    main()
