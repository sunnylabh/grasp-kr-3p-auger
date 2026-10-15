import sys, json; sys.path.insert(0, sys.argv[1]); from run import run
neu = '3s2 3p6 3d10 4s2 4p6'
ST = {'3p': '3s2 3p5 3d10 4s2 4p6', '3d': '3s2 3p6 3d9 4s2 4p6', '4p': '3s2 3p6 3d10 4s2 4p5',
      '3p3d': '3s2 3p5 3d9 4s2 4p6', '3d3d': '3s2 3p6 3d8 4s2 4p6', '3p3p': '3s2 3p4 3d10 4s2 4p6',
      '3d4p': '3s2 3p6 3d9 4s2 4p5', '3p4p': '3s2 3p5 3d10 4s2 4p5', '4p4p': '3s2 3p6 3d10 4s2 4p4',
      '3d3d4p': '3s2 3p6 3d8 4s2 4p5', '3p3d4p': '3s2 3p5 3d9 4s2 4p5', '4p4p4p': '3s2 3p6 3d10 4s2 4p3', '3d4p4p': '3s2 3p6 3d9 4s2 4p4'}
out = {}
for tag, cfg in ST.items():
    E0, L = run('fa_' + tag, [(neu, 'n'), (cfg, 'h')], ['n', 'h'])
    e0 = [v[0] for v in L.values() if v[2] == '4p6'][0]
    lv = [(v[0] - e0, v[1]) for v in L.values() if v[2] != '4p6']
    out[tag] = sum((j + 1) * e for e, j in lv) / sum(j + 1 for e, j in lv)
    print(f'{tag:8s} {out[tag]:9.3f}')
json.dump(out, open(sys.argv[1] + '/fac_avg.json', 'w'))
