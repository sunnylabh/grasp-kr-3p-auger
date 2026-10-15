import sys; sys.path.insert(0, sys.argv[1]); from run import run, ai
E0, L = run('fd_3d_4p4', [('3s2 3p6 3d10 4s2 4p4', 'fin'), ('3s2 3p6 3d9 4s2 4p6', 'ini')], ['fin', 'ini'], ai=[['ini'], ['fin']])
print(len(ai('fd_3d_4p4')), 'lines')
