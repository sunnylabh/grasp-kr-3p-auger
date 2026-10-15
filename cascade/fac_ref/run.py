import json, subprocess, os, sys, collections
S=os.path.dirname(os.path.abspath(__file__)); T=S+'/t'
def run(tag, groups, opt, ai=None, closed=None):
    c=dict(tag=tag,groups=groups,opt=opt,dir=T,ai=ai)
    if closed: c['closed']=closed
    fn=f'{T}/{tag}.json'; json.dump(c,open(fn,'w'))
    r=subprocess.run(['conda','run','-n','fac_env','python',S+'/w.py',fn],capture_output=True,text=True)
    if r.returncode: print(r.stderr[-500:]); raise SystemExit
    E0=None; L={}
    for line in open(f'{T}/{tag}.lev'):
        if line.startswith('E0'): E0=float(line.split(',')[1])  # absolute energy of level 0 in eV
        p=line.split()
        if len(p)>=8 and p[0].isdigit():
            try: L[int(p[0])]=(float(p[2]),int(p[5]),p[7],p[-1])
            except: pass
    return E0,L
def ai(tag):
    return [(int(p[0]),int(p[1]),int(p[2]),int(p[3]),float(p[4]),float(p[5])) for p in (l.split() for l in open(f'{T}/{tag}.ai')) if len(p)==7 and p[0].isdigit()]
