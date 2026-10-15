# -*- coding: utf-8 -*-
"""Second-step spectra (Kr2+ -> Kr3+): GRASP only, and GRASP vs FAC. Single panels.
Line energies from secondary.py (direct GRASP levels); fragmented 4s-hole levels are drawn as their fragments
with >= 10 % of the level's strength. Intensities: FAC rates x parent populations, L3 : L2 = 2 : 1.
Lorentzian width = natural width of the Kr2+ parent level (FAC); Gaussian instrument width 0.5 eV."""
import os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
B = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, B)
import secondary as sc, plot_lmm as pl, kr_spectrum as ks
H = 27.211386245988
INK, INK2, GRID_C, SURF = '#0b0b0b', '#52514e', '#e4e3df', '#fcfcfb'
PAR = [('3d8', '3d⁻²', 'L-M₄,₅M₄,₅', '#2a78d6'), ('3p5.3d9', '3p⁻¹3d⁻¹', 'L-M₂,₃M₄,₅', '#eb6834'),
       ('3p4', '3p⁻²', 'L-M₂,₃M₂,₃', '#1baf7a'), ('3d9.4p5', '3d⁻¹4p⁻¹', 'L-M₄,₅N₂,₃', '#eda100')]
lines = sc.main()
grid = np.arange(0, 200, 0.05)
def spec(ke, w, g):
    ke, w, g = np.array(ke), np.array(w), np.array(g)
    m = (ke > grid[0] + 1) & (ke < grid[-1] - 1)          # lines outside the plotted window are not drawn
    return ks.synth_spectrum(ke[m], w[m], g[m], grid, gauss_fwhm=0.5)
cur = {}
for pcfg, *_ in PAR:
    kf, wf, gf, kg, wg, gg = [], [], [], [], [], []
    for (p, lab), v in lines.items():
        if p != pcfg: continue
        for e, keg, w3, w2, gam, kfin in v:
            w = 2 / 3 * w3 + 1 / 3 * w2
            kf.append(e); wf.append(w); gf.append(gam)
            if keg is None: continue
            # fragmented final levels: fragments with >= 10 % of the strength, as separate lines (KE shifts by -dE)
            fr = [(dE, fw) for dE, fw in pl.FRAG.get((lab, kfin[0], kfin[1]), [(0.0, 1.0)]) if fw >= 0.10]
            tw = sum(fw for _, fw in fr)
            for dE, fw in fr:
                kg.append(keg - dE * H); wg.append(w * fw / tw); gg.append(gam)
    cur[pcfg] = (spec(kg, wg, gg), spec(kf, wf, gf))
norm = max(sum(c[1] for c in cur.values()).max(), 1e-30)
cur = {k: (a / norm * 100, b / norm * 100) for k, (a, b) in cur.items()}
plt.rcParams.update({'font.size': 11, 'axes.edgecolor': INK, 'axes.labelcolor': INK, 'xtick.color': INK, 'ytick.color': INK})
def frame(ax):
    ax.set_facecolor(SURF); ax.set_xlim(0, 200)
    ax.xaxis.set_minor_locator(AutoMinorLocator(5)); ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax.tick_params(which='both', direction='in', top=True, right=True)
    ax.tick_params(which='major', length=6, width=1); ax.tick_params(which='minor', length=3, width=0.8)
    ax.grid(axis='y', color=GRID_C, lw=0.6); ax.set_axisbelow(True)
    ax.set_xlabel('Secondary electron kinetic energy (eV)'); ax.set_ylabel('Intensity (arb. u.)')
fig, ax = plt.subplots(figsize=(10, 5.2), facecolor=SURF); frame(ax)
for pcfg, lab, tr, c in PAR:
    y = cur[pcfg][0]; ax.fill_between(grid, y, color=c, alpha=0.12, lw=0); ax.plot(grid, y, color=c, lw=1.6, label=f'{lab}  ←  {tr}')
ax.set_ylim(0, max(cur[p][0].max() for p, *_ in PAR) * 1.25)
ax.legend(title='Kr²⁺ initial state  ←  populated by', frameon=False, fontsize=9.5, title_fontsize=9.5, loc='upper right')
ax.set_title('Kr 2p⁻¹ cascade, second step (Kr²⁺ → Kr³⁺), GRASP', loc='left', fontsize=12)
for ext in ('png', 'pdf'): fig.savefig(os.path.join(B, 'figures', f'GRASP_secondary.{ext}'), dpi=200, bbox_inches='tight', facecolor=SURF)
yg = sum(c[0] for c in cur.values()); yf = sum(c[1] for c in cur.values())
fig, ax = plt.subplots(figsize=(10, 5.2), facecolor=SURF); frame(ax)
ax.plot(grid, yf, color='#8a8984', lw=1.4, ls=(0, (4, 2)), label='FAC'); ax.plot(grid, yg, color='#2a78d6', lw=1.8, label='GRASP')
ax.set_ylim(0, max(yg.max(), yf.max()) * 1.2); ax.legend(frameon=False, fontsize=10, loc='upper right')
ax.set_title('Kr 2p⁻¹ cascade, second step (Kr²⁺ → Kr³⁺): GRASP vs FAC (same FAC intensities)', loc='left', fontsize=12)
for ext in ('png', 'pdf'): fig.savefig(os.path.join(B, 'figures', f'GRASP_vs_FAC_secondary.{ext}'), dpi=200, bbox_inches='tight', facecolor=SURF)
print('wrote figures/GRASP_secondary.* and figures/GRASP_vs_FAC_secondary.*')
