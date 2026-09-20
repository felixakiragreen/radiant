"""Melee: exact expectation over both rolls with a minimax strike/block policy, against the deterministic fight (rounded hits, same minimax).
Run: python3 fight.py > fight.txt"""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from kt import *
def m(team,opn,wn):
    op=OPS[(team,opn)]; w=[w for w in op['weapons'] if w['wepName']==wn][0]; p=w['profiles'][0]; dn,dc=map(int,p['DMG'].split('/'))
    return dict(atk=int(p['ATK']),hit=num(p['HIT']),dmg=(dn,dc),wr=p['WR'] or '',w=op['WOUNDS'],name=opn)
def det(a):
    r=parse_wr(a['wr']); n=round(a['atk']*(7-a['hit'])/6+1e-9); c=min(n,2 if r.get('lethal') else 1); return n-c,c
F=[('Marine chainsword 5/3+/4/5 W14',m('Angels Of Death','Assault Intercessor Warrior','Chainsword')),('Necron bayonet 4/3+/3/4 W10',m('Hierotek Circle','Immortal Guardian','Bayonet')),('Ork choppa 4/3+/4/5 W10',m('Kommandos','Kommando Boy','Choppa')),('Aeldari power weapon 4/3+/4/6 Lethal W8',m('Corsair Voidscarred','Voidscarred Warrior','Power Weapon'))]
print("## 4x4 melee · row charges column · exact P(kill) P(die) E[att W left] E[def W left] · det att W, def W\nattacker\t"+"\t".join(n for n,_ in F))
for an,a in F:
    row=[]
    for dn_,d in F:
        eaw,edw,pk,pd_=expected_fight(a,d); an_,ac=det(a); dn,dc=det(d); ra,rd=parse_wr(a['wr']),parse_wr(d['wr'])
        aw,dw=fight_outcome(an_,ac,dn,dc,a['w'],d['w'],a['dmg'],d['dmg'],bool(ra.get('brutal')),bool(rd.get('brutal')))
        row.append(f"{pk:.0%} {pd_:.0%} {eaw:.1f} {edw:.1f} | det {aw} {dw}")
    print(an+"\t"+"\t".join(row))
print("hits used (normal,crit):",{n.split()[0]:det(a) for n,a in F})
print("\n## symmetric fights, exact vs deterministic")
for team,opn,wn in [('Kommandos','Kommando Boy','Choppa'),('Angels Of Death','Assault Intercessor Warrior','Chainsword'),('Corsair Voidscarred','Voidscarred Warrior','Power Weapon'),('Hierotek Circle','Immortal Guardian','Bayonet'),('Wrecka Krew','Breaka Boy Fighter','Smash Hammer')]:
    a=m(team,opn,wn); eaw,edw,pk,pd_=expected_fight(a,a); n,c=det(a); r=parse_wr(a['wr'])
    aw,dw=fight_outcome(n,c,n,c,a['w'],a['w'],a['dmg'],a['dmg'],bool(r.get('brutal')),bool(r.get('brutal')))
    print(f"{opn} {wn} {a['atk']}/{a['hit']}+/{a['dmg'][0]}/{a['dmg'][1]} W{a['w']}\tatt kills {pk:.0%}\tatt dies {pd_:.0%}\tE W left {eaw:.1f} {edw:.1f}\tdet {aw} {dw}")
print("\n## the line the deterministic fight plays: Marine chainsword charges Ork choppa")
a=F[0][1]; d=F[2][1]; an_,ac=det(a); dn,dc=det(d); state=(an_,ac,dn,dc,a['w'],d['w'],0)
while True:
    an,ac_,dn_,dc_,aw,dw,turn=state
    if dw<=0 or aw<=0 or (an+ac_==0 and dn_+dc_==0): break
    me_n,me_c,op_n,op_c=(an,ac_,dn_,dc_) if turn==0 else (dn_,dc_,an,ac_)
    if me_n+me_c==0: state=(an,ac_,dn_,dc_,aw,dw,1-turn); continue
    dmg=a['dmg'] if turn==0 else d['dmg']; cands=[]
    def nxt(me_n2,me_c2,op_n2,op_c2,aw2,dw2,lab): return ((me_n2,me_c2,op_n2,op_c2,aw2,dw2,1) if turn==0 else (op_n2,op_c2,me_n2,me_c2,aw2,dw2,0),lab)
    if me_n: cands.append(nxt(me_n-1,me_c,op_n,op_c,aw,dw-dmg[0],f"strike normal {dmg[0]}") if turn==0 else nxt(me_n-1,me_c,op_n,op_c,aw-dmg[0],dw,f"strike normal {dmg[0]}"))
    if me_c: cands.append(nxt(me_n,me_c-1,op_n,op_c,aw,dw-dmg[1],f"strike crit {dmg[1]}") if turn==0 else nxt(me_n,me_c-1,op_n,op_c,aw-dmg[1],dw,f"strike crit {dmg[1]}"))
    if me_n and op_n: cands.append(nxt(me_n-1,me_c,op_n-1,op_c,aw,dw,"block a normal with a normal"))
    if me_c and op_n: cands.append(nxt(me_n,me_c-1,op_n-1,op_c,aw,dw,"block a normal with the crit"))
    if me_c and op_c: cands.append(nxt(me_n,me_c-1,op_n,op_c-1,aw,dw,"block the crit with the crit"))
    vals=[fight(*s[0],a['dmg'],d['dmg'],False,False) for s in cands]; best=cands[vals.index(max(vals) if turn==0 else min(vals))]
    print(f"{'Marine' if turn==0 else 'Ork'}\t{best[1]}\tMarine {best[0][4]}W\tOrk {best[0][5]}W"); state=best[0]
