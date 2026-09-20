"""Shooting: the reference matrix, keyword worth, the ladder of schemes, cover, per-faction distortion.
Run: python3 shoot.py > shoot.txt   (read-only over ~/Projects/KillTeam/BattleData/generator/json/kt24.json)"""
import sys, math, re, collections, statistics as st; sys.path.insert(0, __file__.rsplit('/',1)[0])
from kt import *
DEFS=[defender(*d) for d in DEFENDERS]
R=list(profiles('R')); seen=set(); RU=[]
for p in R:
    k=(p['team'],p['name'])
    if k not in seen: seen.add(k); RU.append(p)
EX={(i,j):expected_shot(p['atk'],p['hit'],p['dmg'],p['wr'],d['save']) for i,p in enumerate(RU) for j,d in enumerate(DEFS)}
EXC={(i,j):expected_shot(p['atk'],p['hit'],p['dmg'],p['wr'],d['save'],cover=True) for i,p in enumerate(RU) for j,d in enumerate(DEFS)}
short={'Intercessor Warrior':'Intercessor 3+/14','Heavy Intercessor Gunner':'Hvy Intercessor 3+/18','Immortal Guardian':'Immortal 3+/10','Plasmacyte Accelerator':'Plasmacyte 5+/5','Kommando Boy':'Kommando 5+/10','Breaka Boy Fighter':'Breaka 4+/12','Voidscarred Warrior':'Corsair 4+/8','Striking Scorpion Warrior':'Scorpion 3+/8'}

print("## weapon space")
print("profiles", len(RU), "ATK", dict(collections.Counter(p['atk'] for p in RU)), "HIT", dict(collections.Counter(p['hit'] for p in RU)))
print("normal dmg", dict(sorted(collections.Counter(p['dmg'][0] for p in RU).items())), "crit dmg", dict(sorted(collections.Counter(p['dmg'][1] for p in RU).items())))
print("saves, 7 teams", dict(sorted(collections.Counter(num(op['SAVE']) for op in OPS.values()).items())))

print("\n## T1 reference matrix: exact expected damage, one shot, open [cover]")
curated=[('Angels Of Death','Bolt Rifle'),('Angels Of Death','Stalker Bolt Rifle [Heavy]'),('Angels Of Death','Heavy Bolter [Focused]'),('Angels Of Death','Plasma Pistol [Supercharge]'),('Hierotek Circle','Gauss Blaster'),('Hierotek Circle','Tesla Carbine'),('Hierotek Circle','Synaptic Disintegrator'),('Kommandos','Slugga'),('Kommandos','Dakka Shoota [Long Range]'),('Kommandos','Rokkit Launcha [Mobile]'),('Kommandos','Burna [Standard]'),('Wrecka Krew','Rokkit Launcha'),('Corsair Voidscarred','Shuriken Rifle'),('Corsair Voidscarred','Blaster'),('Corsair Voidscarred','Fusion Pistol'),('Blades Of Khaine','Twin Shuriken Catapult'),('Void-Dancer Troupe','Neuro Disruptor')]
print("weapon\t"+"\t".join(short[d['op']] for d in DEFS)+"\trules")
for team,name in curated:
    p=next(x for x in RU if x['team']==team and x['name']==name)
    cells=[]
    for d in DEFS:
        e=expected_shot(p['atk'],p['hit'],p['dmg'],p['wr'],d['save']); ec=expected_shot(p['atk'],p['hit'],p['dmg'],p['wr'],d['save'],cover=True)
        cells.append(f"{e:.1f} [{ec:.1f}]")
    print(f"{name} {p['atk']}/{p['hit']}+/{p['dmg'][0]}/{p['dmg'][1]}\t"+"\t".join(cells)+"\t"+p['wr'])

print("\n## T2 keyword worth: mean delta expected damage, weapon with vs without the keyword, over 3+/4+/5+ defenders in the open")
def strip(wr,tok): return ','.join(t for t in wr.split(',') if t.strip() and not re.sub(r'\d','x',t.strip()).startswith(tok))
kw=collections.defaultdict(list)
for p in RU:
    for t in [t.strip() for t in p['wr'].split(',') if t.strip()]:
        key=re.sub(r'\d+','x',t)
        if key not in ('Lethal x+','Prcx','PrcCritx','Rnd','Ceaseless','Relentless','Devx','Dev x','Severe','Sat'): continue
        for sv in (3,4,5):
            cov=(key=='Sat')
            full=expected_shot(p['atk'],p['hit'],p['dmg'],p['wr'],sv,cover=cov); less=expected_shot(p['atk'],p['hit'],p['dmg'],strip(p['wr'],key.replace('x','')[:3]),sv,cover=cov)
            kw[key].append((full-less,(full-less)/p['dmg'][0],sv))
print("keyword\tn\tvs3+\tvs4+\tvs5+\tmean\tin_hits")
for key,vals in sorted(kw.items(), key=lambda kv:-st.mean(v[0] for v in kv[1])):
    by={sv:st.mean(v[0] for v in vals if v[2]==sv) for sv in (3,4,5)}
    print(f"{key}\t{len(vals)//3}\t{by[3]:.2f}\t{by[4]:.2f}\t{by[5]:.2f}\t{st.mean(v[0] for v in vals):.2f}\t{st.mean(v[1] for v in vals):.2f}")

print("\n## the dice as numbers")
for a in (4,5,6): print(f"ATK{a} E[hits] "+" ".join(f"{h}+={a*(7-h)/6:.2f}" for h in (2,3,4,5))+"   half-hits rounded "+" ".join(f"{h}+={round(a*(7-h)/3+1e-9)}" for h in (2,3,4,5))+"   whole rounded "+" ".join(f"{h}+={round(a*(7-h)/6+1e-9)}" for h in (2,3,4,5)))
print("E[saves] 3 dice: "+" ".join(f"{s}+={3*(7-s)/6:.2f}" for s in (2,3,4,5,6))+" | in cover: "+" ".join(f"{s}+={1+2*(7-s)/6:.2f}" for s in (2,3,4,5,6)))
print("E[crits]=ATK/6, Lethal 5+: ATK/3; E[crit saves]=0.5")

# ---- the ladder ----
def Hr(p): return round(p['atk']*(7-p['hit'])/6+1e-9)
def H2(p): return round(p['atk']*(7-p['hit'])/3+1e-9)
def S1(d): return {2:3,3:2,4:1,5:1,6:0}[d['save']]
BIG=('Prc','Dev','Relentless')
def kw2(wr):
    t=[x.strip() for x in wr.split(',') if x.strip() and not re.match(r'(Rng|Blast|Tor|Hvy|Silent|Stun|Shock|Seek|Lim|Hot|Psychic|\*|Sat)',x.strip())]
    return sum(2 if x.startswith(BIG) else 1 for x in t)
def kwn(wr): return len([x for x in wr.split(',') if x.strip() and not re.match(r'(Rng|Blast|Tor|Hvy|Silent|Stun|Shock|Seek|Lim|Hot|Psychic|\*)',x.strip())])
def felix_written(p,d,cov=False):   # as written: (Dn + keywords) x ATK − (7−save) − move ; save read as successes, the charitable fix
    return max(0,(p['dmg'][0]+len([t for t in p['wr'].split(',') if t.strip()]))*p['atk']-(7-d['save'])-d['move'])
def whole_nofloor(p,d,cov=False):
    dn,dc=p['dmg']; net=Hr(p)-S1(d)-(1 if cov else 0)
    return 0 if net<=0 else net*dn+(dc-dn)
def felix_corrected(p,d,cov=False):  # Dn x (H−S) + crit + 1 per keyword AFTER the multiply
    dn,dc=p['dmg']; net=Hr(p)-S1(d)-(1 if cov else 0)
    return 0 if net<=0 else net*dn+(dc-dn)+kwn(p['wr'])
def whole(p,d,cov=False):            # whole hits, floor 1, two-tier keywords, cover = −2 damage
    dn,dc=p['dmg']; net=max(1,Hr(p)-S1(d)); v=net*dn+(dc-dn)+kw2(p['wr'])
    return max(0,v-2) if cov else v
def half(p,d,cov=False):             # half-hit units: Shots=round(ATK(7−HIT)/3), Armour=7−SV (+1 cover), floor 1, two-tier keywords, halve
    dn,dc=p['dmg']; s2=(7-d['save'])+(1 if cov else 0); net2=max(1,H2(p)-s2)
    return round(net2*dn/2+(dc-dn)+kw2(p['wr']))
def ratio(p,d,cov=False):            # multiplicative: E[hits] x Dn x (SV−1)/6, cover −1/6, crit + keywords
    dn,dc=p['dmg']; frac=min(1,max(0,(d['save']-1-(1 if cov else 0))/6)); h=p['atk']*(7-p['hit'])/6
    return round(h*frac*dn+(dc-dn)*frac+kw2(p['wr']))
def ev(p,d,cov=False): return round((EXC if cov else EX)[(RU.index(p),DEFS.index(d))])
LADDER=[('card row: printed rounded expectation','read a cell',ev),('half-hit units, floor, two-tier keywords','subtract, multiply, halve',half),('ratio: hits x dmg x (save−1)/6','multiply by a fraction',ratio),('whole hits, floor, two-tier keywords','subtract, multiply, add',whole),('Felix corrected: Dn x (H−S) + crit, +1 per keyword after','subtract, multiply, add',felix_corrected),('whole hits, no floor, no keywords','subtract, multiply',whole_nofloor),('as written, save read as successes, minus move','as written',felix_written)]
def stk(v,w): return math.inf if v<=0 else math.ceil(w/v)
for cov in (False,True):
    print(f"\n## T3 ladder · 73 profiles x 8 defenders · {'COVER' if cov else 'OPEN'}\nscheme\tarithmetic\tMAE\tbias\tmax\tdead_cells\tSTK_match")
    for name,arith,f in LADDER:
        errs=[];z=0;m=0
        for i,p in enumerate(RU):
            for j,d in enumerate(DEFS):
                e=(EXC if cov else EX)[(i,j)]; v=f(p,d,cov); errs.append(v-e); z+=(v==0); m+=(stk(v,d['w'])==stk(e,d['w']))
        print(f"{name}\t{arith}\t{st.mean(map(abs,errs)):.2f}\t{st.mean(errs):+.2f}\t{max(map(abs,errs)):.1f}\t{z}\t{100*m/len(errs):.0f}%")

print("\n## T4 cover rules under the whole-hit scheme (floor, two-tier keywords)")
def whole_cov(p,d,rule):
    dn,dc=p['dmg']; net=max(1,Hr(p)-S1(d)); v=net*dn+(dc-dn)+kw2(p['wr'])
    if rule=='+1 save': net=Hr(p)-S1(d)-1; return 0 if net<=0 else net*dn+(dc-dn)+kw2(p['wr'])
    if rule=='−1 dmg': return max(0,v-1)
    if rule=='−2 dmg': return max(0,v-2)
    if rule=='−half a hit': return max(0,v-round(dn/2))
    if rule=='−one hit': return max(0,v-dn)
print("rule\tMAE\tbias\tdead_cells\tSTK_match")
for rule in ('+1 save','−1 dmg','−2 dmg','−half a hit','−one hit'):
    errs=[];z=0;m=0
    for i,p in enumerate(RU):
        for j,d in enumerate(DEFS):
            e=EXC[(i,j)]; v=whole_cov(p,d,rule); errs.append(v-e); z+=(v==0); m+=(stk(v,d['w'])==stk(e,d['w']))
    print(f"{rule}\t{st.mean(map(abs,errs)):.2f}\t{st.mean(errs):+.2f}\t{z}\t{100*m/len(errs):.0f}%")

print("\n## T5 per-faction distortion, OPEN: mean signed error (scheme − exact); rows attacker faction, cols defender")
facs=['Angels Of Death','Hierotek Circle','Kommandos','Wrecka Krew','Corsair Voidscarred','Void-Dancer Troupe','Blades Of Khaine']
for name,_,f in LADDER[1:2]+LADDER[3:5]:
    print(f"[{name}]\nfaction\t"+"\t".join(short[d['op']] for d in DEFS)+"\tall")
    for fac in facs:
        ps=[(i,p) for i,p in enumerate(RU) if p['team']==fac]; alle=[]; row=[]
        for j,d in enumerate(DEFS):
            errs=[f(p,d)-EX[(i,j)] for i,p in ps]; alle+=errs; row.append(f"{st.mean(errs):+.1f}")
        print(fac+"\t"+"\t".join(row)+f"\t{st.mean(alle):+.1f}")

print("\n## T6 four factions: exact damage → shots to kill · card row STK · whole-hit scheme damage → STK")
A=[('Marine bolt rifle',('Angels Of Death','Bolt Rifle')),('Necron gauss blaster',('Hierotek Circle','Gauss Blaster')),('Ork slugga',('Kommandos','Slugga')),('Ork rokkit 6/4+',('Kommandos','Rokkit Launcha [Mobile]')),('Aeldari shuriken rifle',('Corsair Voidscarred','Shuriken Rifle')),('Aeldari blaster Prc2',('Corsair Voidscarred','Blaster'))]
Dd=[('Intercessor 3+/14',('Angels Of Death','Intercessor Warrior')),('Immortal 3+/10',('Hierotek Circle','Immortal Guardian')),('Kommando 5+/10',('Kommandos','Kommando Boy')),('Corsair 4+/8',('Corsair Voidscarred','Voidscarred Warrior'))]
print("attacker\t"+"\t".join(n for n,_ in Dd))
for an,(t,w) in A:
    p=next(x for x in RU if x['team']==t and x['name']==w); row=[]
    for dn_,(dt,do) in Dd:
        d=defender(dt,do); e=expected_shot(p['atk'],p['hit'],p['dmg'],p['wr'],d['save']); v=whole(p,d)
        row.append(f"{e:.1f}→{stk(e,d['w'])} | row {stk(round(e),d['w'])} | f {v}→{stk(v,d['w'])}")
    print(an+"\t"+"\t".join(row))

print("\n## Jensen: slugga 4/4+/3/4 into a 3+ save, the distribution of damage per shot")
p=next(x for x in RU if x['name']=='Slugga' and x['team']=='Kommandos'); r=parse_wr(p['wr'])
A_=attack_dist(4,4,r); dist=collections.Counter()
for (an,ac),pa in A_.items():
    for (dn_,dc_),pd in defence_dist(3,3,False).items():
        dist[best_block(an,ac,dn_,dc_,3,4,False)]+=pa*pd
for k in sorted(dist): print(f"dmg {k}\tP {dist[k]:.3f}")
print("E[hits]=2.00 E[saves]=2.00 → subtractive says 0; E[damage] =", f"{sum(k*v for k,v in dist.items()):.2f}", "P(zero) =", f"{dist[0]:.2f}")

print("\n## T7 his second formula, sent mid-build: (ATK x damage) − HIT, and variants · OPEN")
for name,f in [("(ATK x dmg) − HIT",lambda p,d: max(0,p['atk']*p['dmg'][0]-p['hit'])),
               ("(ATK x dmg) − HIT − (7−save)",lambda p,d: max(0,p['atk']*p['dmg'][0]-p['hit']-(7-d['save']))),
               ("((ATK x dmg) − HIT) / 2",lambda p,d: max(0,round((p['atk']*p['dmg'][0]-p['hit'])/2))),
               ("((ATK x dmg) − HIT) / 3",lambda p,d: max(0,round((p['atk']*p['dmg'][0]-p['hit'])/3)))]:
    errs=[];z=0;m=0
    for i,p in enumerate(RU):
        for j,d in enumerate(DEFS):
            e=EX[(i,j)]; v=f(p,d); errs.append(v-e); z+=(v==0); m+=(stk(v,d['w'])==stk(e,d['w']))
    print(f"{name}\tMAE {st.mean(map(abs,errs)):.2f}\tbias {st.mean(errs):+.2f}\tdead {z}\tSTK {100*m/len(errs):.0f}%")
for sv in (3,4,5):
    print(f"vs {sv}+: formula mean {st.mean(max(0,p['atk']*p['dmg'][0]-p['hit']) for p in RU):.1f} · truth {st.mean(EX[(i,j)] for i,p in enumerate(RU) for j,d in enumerate(DEFS) if d['save']==sv):.1f}")
