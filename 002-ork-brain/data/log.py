"""His battle log by month — the datum about Felix. Reads ~/Projects/KillTeam/BattleData/reporter/data/battle-results.txt. Run: python3 log.py > log.tsv"""
import re, collections
txt=open('/Users/felix/Projects/KillTeam/BattleData/reporter/data/battle-results.txt').read()
games=[g for g in txt.split('——————————') if '⚔️' in g]
per=collections.Counter(); fel=collections.Counter(); teams=collections.Counter(); res=collections.Counter(); n=0
for g in games:
    date=re.search(r'🗓️ (\d{4}-\d{2})',g); pl=re.search(r'👥 (.*)',g); tm=re.search(r'⚔️ (.*)',g); out=re.search(r'Outcome: (.*)',g)
    if not (date and pl and tm): continue
    m=date.group(1); per[m]+=1; n+=1
    p=[x.strip().lstrip('@') for x in pl.group(1).split('&')]; t=[re.sub(r'\s*\(\d+VP\)','',x).strip() for x in tm.group(1).split(' v. ')]
    if 'Felix' in p:
        fel[m]+=1; i=p.index('Felix')
        if i<len(t): teams[t[i]]+=1
        if out:
            r=re.findall(r'(Win|Loss|Tie)',out.group(1))
            if i<len(r): res[r[i]]+=1
print("month\tall\tfelix")
for m in sorted(per): print(f"{m}\t{per[m]}\t{fel.get(m,0)}")
print(f"# games {n} · felix {sum(fel.values())} · record {dict(res)} · teams {len(teams)}: {dict(teams.most_common())}")
