import sys, json; sys.path.insert(0, sys.argv[1]); from run import run
neu = '3s2 3p6 3d10 4s2 4p6'
ST = [('2p5', '2s2 2p5 3s2 3p6 3d10 4s2 4p6'),
      ('3d8', '3s2 3p6 3d8 4s2 4p6'), ('3p5.3d9', '3s2 3p5 3d9 4s2 4p6'), ('3p4', '3s2 3p4 3d10 4s2 4p6'), ('3d9.4p5', '3s2 3p6 3d9 4s2 4p5'),
      ('3d9.4s1.4p5', '3s2 3p6 3d9 4s1 4p5'), ('3d9.4p4', '3s2 3p6 3d9 4s2 4p4'), ('3d9', '3s2 3p6 3d9 4s0 4p6'),
      ('4s1.4p4', '3s2 3p6 3d10 4s1 4p4'), ('4p5', '3s2 3p6 3d10 4s0 4p5'), ('4p3', '3s2 3p6 3d10 4s2 4p3'),
      ('3d8.4p5', '3s2 3p6 3d8 4s2 4p5'), ('3d8.4s1', '3s2 3p6 3d8 4s1 4p6'), ('3p5.3d9.4p5', '3s2 3p5 3d9 4s2 4p5'), ('3p5.3d9.4s1', '3s2 3p5 3d9 4s1 4p6')]
out = {}
for tag, cfg in ST:
    closed = ['1s'] if tag == '2p5' else None
    n = ('2s2 2p6 ' + neu) if tag == '2p5' else neu
    E0, L = run('fs_' + tag.replace('.', '_'), [(n, 'n'), (cfg, 'h')], ['n', 'h'], closed=closed)
    e0 = min(v[0] for v in L.values() if v[3].endswith('(0)0') or v[2] in ('4p6', '2p6.4p6') ) if False else None
    nl = [v[0] for v in L.values() if v[2] in ('4p6', '2p6')]   # neutral level (label of the closed shell)
    if not nl: nl = [min(v[0] for v in L.values())]
    e0 = nl[0]
    lv = sorted(v[0] - e0 for v in L.values() if v[0] != e0)
    out[tag] = (lv[0], lv[-1], len(lv))
    print(f'{tag:12s} lowest {lv[0]:9.2f}  highest {lv[-1]:9.2f}  ({len(lv)} levels)')
json.dump(out, open(sys.argv[1] + '/fac_states.json', 'w'))
