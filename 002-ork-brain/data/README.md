# data — the ork-brain sitting's scout

Run 2026-09-19 by mentat-09. Read-only over his files; every number in `../index.html`
is reproducible from here.

- `kt.py` — the engine: exact KT24 shoot expectation (attack and defence dice distributions,
  optimal blocking, the damage-relevant weapon rules — Lethal, Piercing, Piercing Crits, Rending,
  Ceaseless, Relentless, Brutal, Severe, Saturate, Devastating; cover) and the fight (minimax over
  strike/block, exact over both rolls or deterministic on rounded hits). Reads
  `~/Projects/KillTeam/BattleData/generator/json/kt24.json` (a KTDash export) for the seven teams.
- `shoot.py` → `shoot.txt` — the weapon space; T1 reference matrix; T2 keyword worth; T3 the ladder
  of schemes, open and cover; T4 cover rules; T5 per-faction distortion; T6 the four-faction
  shots-to-kill; the Jensen distribution (slugga into a 3+ save).
- `fight.py` → `fight.txt` — the 4×4 melee matrix, symmetric fights, the narrated deterministic line.
- `log.py` → `log.tsv` — his reporter's battle log by month
  (`~/Projects/KillTeam/BattleData/reporter/data/battle-results.txt`).

Caveats the Radiant repeats (chapter 13): abilities, ploys and equipment absent; Blast and Torrent
scored single-target; Hot ignored; obscured unmodelled; Ceaseless and Relentless closed-form
approximations; eight defenders; rounding to nearest; the melee utility is the office's.
