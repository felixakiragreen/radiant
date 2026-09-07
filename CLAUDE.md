# radiant — the Mentat's maps

A Radiant is the visual capture of a Mentat sitting: the map a sitting drew, made for
the reader who wasn't there — Felix at human speed, or a Mentat with no memory of it.
The book (`~/code/agents/SAPHO.md`) is the office's diary; a Radiant is one sitting's
chart. Voice, never law.

**Read `MAP.md` before any work** — what a Radiant is, its anatomy, how one is made,
and the index. The tail of `LEDGER.md` says where we are; blessed choices live in
`DECISIONS.md`; field reports go to `ISSUES.md` — file it and move on.

## Hard laws (project physics; Felix's global directives also apply)

1. **Voice, never law.** A Radiant blesses nothing and binds nothing; every claim in
   it cites its evidence or reads as a draft. Law lives in the canon and the
   buildings — a durable fact living only here is a promotion failure.
2. **Sealed at the close.** A Radiant is edited only during its sitting. After the
   sitting closes it is appended (a dated coda) and never rewritten — the book's own
   rule. A later sitting draws a later Radiant.
3. **Felikai.** Colors are felikai tokens (`~/code/hexwright/canon/felikai.css`,
   inlined verbatim — the page must stand alone). Type follows the glass law:
   Iosevka Felix for everything titled, numbered, labeled, or tabled; Inter for
   running prose. Dark, always — the Radiant is read in a dark room.
4. **Self-contained and reproducible.** One `index.html` per Radiant, no build step,
   no network but Google Fonts for Inter. Every number about Felix ships with the
   script that produced it, in `data/` beside the page.
5. **Show, don't describe.** Felix has aphantasia — he cannot preview images mentally
   (hexwright's law 5). A Radiant renders the mechanism; it never asks him to imagine
   one, and a figure beats a paragraph that describes a figure.
6. **Two readers, three depths.** The head reads in two minutes, the body in an
   hour, the rabbit holes for a lifetime. A Radiant that only does the third has
   failed the first two.

## Session protocol

- Declare your office or mantle. The Mentat writes here, in a sitting, by Felix's
  summons (`~/code/agents/canon/mantles/mentat.md`); a Builder or Fixer touches a
  Radiant only at Felix's word — tooling or repair, never content. This building runs
  the work doctrine where it applies: `~/code/agents/canon/work/DOCTRINE.md`.
- No board: Radiants are drawn in sittings, not laid as work (MAP §6).
- End every session: the Radiant's state written, `LEDGER.md` appended (date · office ·
  changed · decided · next), commits in Felix's git style. The book's entry points at
  the Radiant; the Radiant's colophon points at the book.
- Repo: branch `master`, never main. Published pages are the glass; the file is the
  truth.
- Register: this building is declared in `~/code/agents/canon/BUILDINGS.md` when the
  Grand Architect sweeps the founding inbox entry (agents `ISSUES.md`, 2026-09-04).
  Until then the rig does not know it.
