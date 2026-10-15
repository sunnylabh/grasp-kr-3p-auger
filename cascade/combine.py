"""E(state) = E_SC + dE_val + dE_core (incremental correlation); BE = E(ion) - E(neutral)."""
import subprocess, os, re
H = 27.211386245988; B = os.path.dirname(os.path.abspath(__file__))
def pick(path, occ):
    o = subprocess.run(['python3', f'{B}/pick.py', f'{B}/{path}', occ], capture_output=True, text=True).stdout
    return {m[0]: float(m[1]) for m in re.findall(r'J=(\S+)\s+root.*E=(\S+)', o)}
def sc(path):
    o = subprocess.run([os.path.expanduser('~/grasp/bin/rlevels'), os.path.basename(path)], cwd=os.path.dirname(f'{B}/{path}'),
                       capture_output=True, text=True).stdout
    r, s = {}, 0
    for l in o.splitlines():
        if l.startswith('-----'): s += 1; continue
        p = l.split()
        if s == 2 and len(p) >= 5 and p[2] not in r: r[p[2]] = float(p[4])
    return r
def state(scp, val, core, occ):
    S, V, C = sc(scp), pick(val, occ), pick(core, occ)
    return {j: (S[j], S[j] + (V[j] - S[j]), S[j] + (C[j] - S[j]), S[j] + (V[j] - S[j]) + (C[j] - S[j])) for j in V}
neu = state('neutral/neutral.cm', 'ci_neu/neu', 'c3_neu/neu', '3d10 4s2 4p6')['0']
rows = [('4p⁻¹', 'np5/np5.cm', 'ci_np5/np5', 'c3_np5/np5', '3d10 4s2 4p5', {'3/2': 14.000, '1/2': 14.666}),
        ('3d⁻¹', 'd9/d9.cm', 'ci_d9/d9', 'c3_d9/d9', '3d9 4s2 4p6', {'5/2': 93.80, '3/2': 95.04}),
        ('3p⁻¹', 'p5.cm', 'ci_p5/p5', 'c3_p5/p5', '3p5 3d10 4s2 4p6', {'3/2': 214.4, '1/2': 222.2}),
        ('4s⁻¹', 's1/s1.cm', 'ci_s1/s1', 'c3_s1/s1', '3d10 4s1 4p6', {'1/2': 27.51}),
        ('4p⁻² ³P₂', 'p4/p4.cm', 'ci_p4/p4', 'c3_p4/p4', '3d10 4s2 4p4', {'2': 38.36})]
print(f"{'state':10s}{'J':5s}{'SC':>9s}{'+val':>9s}{'+core':>9s}{'+both':>9s}{'exp':>9s}  err SC -> both")
for name, scp, v, c, occ, ex in rows:
    st = state(scp, v, c, occ)
    for j, x in ex.items():
        e = [(st[j][k] - neu[k]) * H for k in range(4)]
        print(f"{name:10s}{j:5s}" + ''.join(f'{y:9.2f}' for y in e) + f"{x:9.2f}  {e[0]-x:+.2f} -> {e[3]-x:+.2f}")
