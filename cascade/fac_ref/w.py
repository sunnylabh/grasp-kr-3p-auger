# one FAC session: groups=[[cfg,name],...], opt=[names], prints lowest/centroid energy per group (eV)
import sys, json, os
from pfac import fac
c=json.load(open(sys.argv[1])); os.chdir(c['dir'])
fac.SetAtom('Kr'); fac.Closed(*c.get('closed',['1s','2s','2p']))
for s,g in c['groups']: fac.Config(s, group=g)
fac.ConfigEnergy(0); fac.OptimizeRadial(c['opt']); fac.ConfigEnergy(1)
names=[g for _,g in c['groups']]
fac.Structure(c['tag']+'.lev.b', names); fac.MemENTable(c['tag']+'.lev.b'); fac.PrintTable(c['tag']+'.lev.b', c['tag']+'.lev', 1)
if c.get('ai'):
    fac.AITable(c['tag']+'.ai.b', c['ai'][0], c['ai'][1]); fac.PrintTable(c['tag']+'.ai.b', c['tag']+'.ai', 1)
