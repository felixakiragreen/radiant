#!/bin/zsh
# The neck sitting's scout — commits authored as Felix across every repo under
# ~/code, as a proxy for when a session was active (agents commit as him, so this is
# desk time, not thinking time). Run from anywhere; prints the three tables the
# Radiant charts. Window: the sixty days before 2026-09-04.
set -u
SINCE="2026-07-06"
AUTHOR="Felix Green"
repos() { find ~/code -maxdepth 3 -name .git -type d 2>/dev/null | sed 's|/.git$||'; }

echo "# by hour (local), all repos, since $SINCE"
for r in $(repos); do
	git -C "$r" log --all --author="$AUTHOR" --since="$SINCE" --format="%ad" --date=format-local:"%H" 2>/dev/null
done | sort | uniq -c | awk '{printf "%s\t%s\n", $2, $1}'

echo "# by weekday (1=Mon), since $SINCE"
for r in $(repos); do
	git -C "$r" log --all --author="$AUTHOR" --since="$SINCE" --format="%ad" --date=format-local:"%u" 2>/dev/null
done | sort | uniq -c | awk '{printf "%s\t%s\n", $2, $1}'

echo "# by week: output buildings vs the shop that builds the shop"
OUTPUT=(universal_robots_sdk/cap-mega universal_robots_sdk/bob whiteboardy rooted thg/turnout)
PROCESS=(agents stigmergon)
printf '%s\n' "2026-07-27 2026-08-02" "2026-08-03 2026-08-09" "2026-08-10 2026-08-16" \
	"2026-08-17 2026-08-23" "2026-08-24 2026-08-30" "2026-08-31 2026-09-06" | while read a b; do
	out=0; proc=0
	for r in $OUTPUT; do
		n=$(git -C ~/code/$r log --all --author="$AUTHOR" --since="${a}T00:00:00" --until="${b}T23:59:59" --oneline 2>/dev/null | wc -l | tr -d ' ')
		out=$((out + n))
	done
	for r in $PROCESS; do
		n=$(git -C ~/code/$r log --all --author="$AUTHOR" --since="${a}T00:00:00" --until="${b}T23:59:59" --oneline 2>/dev/null | wc -l | tr -d ' ')
		proc=$((proc + n))
	done
	printf "%s\t%s\t%d\t%d\n" "$a" "$b" "$out" "$proc"
done
