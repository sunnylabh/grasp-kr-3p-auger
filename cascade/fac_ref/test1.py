import sys; sys.path.insert(0, sys.argv[1]); from run import run, ai
ini=('3s2 3p5 3d10 4s2 4p6','ini')
fins={'M45N23':'3s2 3p6 3d9 4s2 4p5','M45N1':'3s2 3p6 3d9 4s1 4p6','N23N23':'3s2 3p6 3d10 4s2 4p4','M45M45':'3s2 3p6 3d8 4s2 4p6'}
for ch,f in fins.items():
    for v,opt in [('both(prod)',['fin','ini']),('ini-only',['ini']),('fin-only',['fin'])]:
        tag=f'{ch}_{v[:3]}'
        E0,L=run(tag,[(f,'fin'),ini],opt,ai=[['ini'],['fin']])
        A=ai(tag)
        for j,h in [(3,'M3'),(1,'M2')]:
            a=[x for x in A if x[1]==j]; s=max(a,key=lambda x:x[5]); cen=sum(x[4]*x[5] for x in a)/sum(x[5] for x in a)
            print(f'{ch:7s} {v:11s} {h}: strongest {s[4]:7.2f}  centroid {cen:7.2f}  range {min(x[4] for x in a):6.1f}-{max(x[4] for x in a):6.1f}')
