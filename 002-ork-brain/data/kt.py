"""KT24 shoot/fight expectation engine + deterministic candidate formulas. Read-only scout."""
import json, re, itertools, functools
from math import comb

D = json.load(open('/Users/felix/Projects/KillTeam/BattleData/generator/json/kt24.json'))
TEAMS = ['Angels Of Death','Hierotek Circle','Kommandos','Wrecka Krew','Corsair Voidscarred','Void-Dancer Troupe','Blades Of Khaine']
OPS = {}
for t in D:
    if t['killteamName'] in TEAMS:
        for op in t['opTypes']:
            OPS[(t['killteamName'], op['opTypeName'])] = op

def num(s): return int(re.match(r'\d+', s).group())

def parse_wr(wr):
    r = {}
    for tok in (wr or '').split(','):
        tok = tok.strip()
        if not tok: continue
        m = re.match(r'Lethal (\d)\+', tok);       
        if m: r['lethal'] = int(m.group(1)); continue
        m = re.match(r'PrcCrit(\d)', tok)
        if m: r['prccrit'] = int(m.group(1)); continue
        m = re.match(r'Prc(\d)', tok)
        if m: r['prc'] = int(m.group(1)); continue
        m = re.match(r'(?:\d"\s*)?Dev\s?(\d)', tok)
        if m: r['dev'] = int(m.group(1)); continue
        if tok == 'Rnd': r['rending'] = 1
        elif tok == 'Ceaseless': r['ceaseless'] = 1
        elif tok == 'Relentless': r['relentless'] = 1
        elif tok == 'Brutal': r['brutal'] = 1
        elif tok == 'Severe': r['severe'] = 1
        elif tok == 'Sat': r['sat'] = 1
        elif tok == 'Shock': r['shock'] = 1
    return r

def dice_dist(n, p_norm, p_crit):
    out = {}
    p_fail = max(0.0, 1 - p_norm - p_crit)
    for c in range(n + 1):
        for m in range(n - c + 1):
            f = n - c - m
            out[(m, c)] = out.get((m, c), 0) + comb(n, c) * comb(n - c, m) * p_crit**c * p_norm**m * p_fail**f
    return out

def attack_dist(atk, hit, r):
    crit_at = r.get('lethal', 6)
    p_succ = (7 - hit) / 6
    p_crit = (7 - crit_at) / 6
    if r.get('ceaseless'):   # re-roll one fail value: each die gets 1/6 extra chance
        p_succ = p_succ + p_succ / 6; p_crit = p_crit + p_crit / 6
    if r.get('relentless'):
        p_succ = p_succ + (1 - p_succ) * p_succ; p_crit = p_crit + (1 - (7 - hit) / 6) * p_crit
    A = dice_dist(atk, p_succ - p_crit, p_crit)
    if r.get('rending') or r.get('severe'):
        B = {}
        for (m, c), p in A.items():
            if r.get('rending') and c >= 1 and m >= 1: m, c = m - 1, c + 1
            elif r.get('severe') and c == 0 and m >= 1: m, c = m - 1, 1
            B[(m, c)] = B.get((m, c), 0) + p
        A = B
    return A

def defence_dist(save, n_dice, cover):
    s_all = (7 - save) / 6; s_crit = 1 / 6
    if cover and n_dice >= 1:
        base = dice_dist(n_dice - 1, s_all - s_crit, s_crit)
        return {(m + 1, c): p for (m, c), p in base.items()}
    return dice_dist(n_dice, s_all - s_crit, s_crit)

def best_block(an, ac, dn, dc, dmg_n, dmg_c, brutal):
    best = None
    if brutal: dn = 0
    for cs_c in range(min(dc, ac) + 1):
        for cs_n in range(min(dc - cs_c, an) + 1):
            for ns_n in range(min(dn, an - cs_n) + 1):
                pairs = min((dn - ns_n) // 2, ac - cs_c)
                dmg = (an - cs_n - ns_n) * dmg_n + (ac - cs_c - pairs) * dmg_c
                if best is None or dmg < best: best = dmg
    return best

def expected_shot(atk, hit, dmg, wr, save, cover=False):
    r = parse_wr(wr)
    dn, dc = dmg
    A = attack_dist(atk, hit, r)
    cov = cover and not r.get('sat')
    e = 0.0
    for (an, ac), pa in A.items():
        n_dice = 3 - r.get('prc', 0) - (r.get('prccrit', 0) if ac >= 1 else 0)
        n_dice = max(0, n_dice)
        Dd = defence_dist(save, n_dice, cov)
        dev = ac * r.get('dev', 0)
        for (dn_, dc_), pd in Dd.items():
            e += pa * pd * (best_block(an, ac, dn_, dc_, dn, dc, r.get('brutal')) + dev)
    return e

def profiles(kind):
    for (team, opn), op in OPS.items():
        for w in op['weapons']:
            if w['wepType'] != kind: continue
            for p in w['profiles']:
                if not re.match(r'\d+/\d+', p['DMG']): continue
                dn, dc = map(int, p['DMG'].split('/'))
                yield dict(team=team, op=opn, name=w['wepName'] + (f" [{p['profileName']}]" if p['profileName'] else ''),
                           atk=int(p['ATK']), hit=num(p['HIT']), dmg=(dn, dc), wr=p['WR'] or '')

DEFENDERS = [
    ('Angels Of Death', 'Intercessor Warrior'),
    ('Angels Of Death', 'Heavy Intercessor Gunner'),
    ('Hierotek Circle', 'Immortal Guardian'),
    ('Hierotek Circle', 'Plasmacyte Accelerator'),
    ('Kommandos', 'Kommando Boy'),
    ('Wrecka Krew', 'Breaka Boy Fighter'),
    ('Corsair Voidscarred', 'Voidscarred Warrior'),
    ('Blades Of Khaine', 'Striking Scorpion Warrior'),
]
def defender(team, opn):
    op = OPS[(team, opn)]
    return dict(team=team, op=opn, save=num(op['SAVE']), move=num(op['MOVE']), w=op['WOUNDS'])

# ---------------- melee: minimax over the strike/block sequence ----------------
@functools.lru_cache(maxsize=None)
def fight(an, ac, dn, dc, aw, dw, turn, a_dmg, d_dmg, a_brutal, d_brutal):
    """Returns attacker utility. turn 0 = attacker resolves, 1 = defender. Dice: normals/crits per side.
    Utility: +1000 kill, -1000 killed, else dealt - taken."""
    if dw <= 0: return 1000 + (aw)      # defender dead; prefer keeping wounds
    if aw <= 0: return -1000 - (dw)
    if an + ac == 0 and dn + dc == 0: return 0
    me_n, me_c, op_n, op_c = (an, ac, dn, dc) if turn == 0 else (dn, dc, an, ac)
    if me_n + me_c == 0:               # opponent resolves all remaining
        return fight(an, ac, dn, dc, aw, dw, 1 - turn, a_dmg, d_dmg, a_brutal, d_brutal)
    dmg = a_dmg if turn == 0 else d_dmg
    opp_brutal = d_brutal if turn == 0 else a_brutal   # opponent's weapon Brutal → I block only with crits
    opts = []
    def rec(me_n2, me_c2, op_n2, op_c2, aw2, dw2):
        if turn == 0: return fight(me_n2, me_c2, op_n2, op_c2, aw2, dw2, 1, a_dmg, d_dmg, a_brutal, d_brutal)
        return fight(op_n2, op_c2, me_n2, me_c2, aw2, dw2, 0, a_dmg, d_dmg, a_brutal, d_brutal)
    # strike normal / crit
    if me_n: opts.append(rec(me_n - 1, me_c, op_n, op_c, aw, dw - dmg[0]) if turn == 0 else rec(me_n - 1, me_c, op_n, op_c, aw - dmg[0], dw))
    if me_c: opts.append(rec(me_n, me_c - 1, op_n, op_c, aw, dw - dmg[1]) if turn == 0 else rec(me_n, me_c - 1, op_n, op_c, aw - dmg[1], dw))
    # block: normal blocks normal (unless opp brutal); crit blocks normal or crit
    if me_n and op_n and not opp_brutal: opts.append(rec(me_n - 1, me_c, op_n - 1, op_c, aw, dw))
    if me_c and op_n: opts.append(rec(me_n, me_c - 1, op_n - 1, op_c, aw, dw))
    if me_c and op_c: opts.append(rec(me_n, me_c - 1, op_n, op_c - 1, aw, dw))
    return max(opts) if turn == 0 else min(opts)

def fight_outcome(an, ac, dn, dc, aw, dw, a_dmg, d_dmg, a_brutal, d_brutal):
    """Replay the minimax line to get (dealt, taken)."""
    state = (an, ac, dn, dc, aw, dw, 0)
    while True:
        an, ac, dn, dc, aw, dw, turn = state
        if dw <= 0 or aw <= 0 or (an + ac == 0 and dn + dc == 0): break
        me_n, me_c, op_n, op_c = (an, ac, dn, dc) if turn == 0 else (dn, dc, an, ac)
        if me_n + me_c == 0: state = (an, ac, dn, dc, aw, dw, 1 - turn); continue
        dmg = a_dmg if turn == 0 else d_dmg
        opp_brutal = d_brutal if turn == 0 else a_brutal
        cands = []
        def nxt(me_n2, me_c2, op_n2, op_c2, aw2, dw2):
            return (me_n2, me_c2, op_n2, op_c2, aw2, dw2, 1) if turn == 0 else (op_n2, op_c2, me_n2, me_c2, aw2, dw2, 0)
        if me_n: cands.append(nxt(me_n - 1, me_c, op_n, op_c, aw, dw - dmg[0]) if turn == 0 else nxt(me_n - 1, me_c, op_n, op_c, aw - dmg[0], dw))
        if me_c: cands.append(nxt(me_n, me_c - 1, op_n, op_c, aw, dw - dmg[1]) if turn == 0 else nxt(me_n, me_c - 1, op_n, op_c, aw - dmg[1], dw))
        if me_n and op_n and not opp_brutal: cands.append(nxt(me_n - 1, me_c, op_n - 1, op_c, aw, dw))
        if me_c and op_n: cands.append(nxt(me_n, me_c - 1, op_n - 1, op_c, aw, dw))
        if me_c and op_c: cands.append(nxt(me_n, me_c - 1, op_n, op_c - 1, aw, dw))
        vals = [fight(*s, a_dmg, d_dmg, a_brutal, d_brutal) for s in cands]
        state = cands[vals.index(max(vals) if turn == 0 else min(vals))]
    an, ac, dn, dc, aw, dw, _ = state
    return aw, dw

def expected_fight(a, d):
    """a, d: dict(atk,hit,dmg,wr,w). Returns E[attacker wounds left], E[defender wounds left], P(kill def), P(att dies)."""
    ra, rd = parse_wr(a['wr']), parse_wr(d['wr'])
    A = attack_dist(a['atk'], a['hit'], ra); Dd = attack_dist(d['atk'], d['hit'], rd)
    e_aw = e_dw = pk = pd_ = 0.0
    for (an, ac), pa in A.items():
        for (dn, dc), pd in Dd.items():
            aw, dw = fight_outcome(an, ac, dn, dc, a['w'], d['w'], a['dmg'], d['dmg'], bool(ra.get('brutal')), bool(rd.get('brutal')))
            e_aw += pa * pd * aw; e_dw += pa * pd * dw
            pk += pa * pd * (dw <= 0); pd_ += pa * pd * (aw <= 0)
    return e_aw, e_dw, pk, pd_
