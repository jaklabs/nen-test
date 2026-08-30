"""The Water Divination ceremony, rendered for a terminal.

    python3 -m nen ~/code/your-project
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from .divination import (HEXAGON, JAPANESE, affinity, divine, opposite)

# Category colour, chosen to match how each reaction reads.
COLOUR = {
    "enhancer": "\033[38;5;203m",     # red — force applied directly
    "transmuter": "\033[38;5;213m",   # pink — property changed
    "conjurer": "\033[38;5;117m",     # pale blue — something made from nothing
    "specialist": "\033[38;5;186m",   # pale gold — rare
    "manipulator": "\033[38;5;150m",  # green — control at a distance
    "emitter": "\033[38;5;215m",      # amber — aura thrown outward
}
DIM, BOLD, RESET = "\033[2m", "\033[1m", "\033[0m"


def _bar(pct: float, width: int = 22) -> str:
    filled = int(round(pct / 100 * width * 2.2))
    filled = min(filled, width)
    return "█" * filled + "░" * (width - filled)


def _hexagon(aura: dict[str, float], category: str, c: str) -> list[str]:
    """The six categories in wheel order, so opposites sit across from each other."""
    rows = []
    for cat in HEXAGON:
        pct = aura[cat]
        mark = f"{c}◆{RESET}" if cat == category else f"{DIM}·{RESET}"
        name = f"{c}{cat.upper():<12}{RESET}" if cat == category else f"{cat:<12}"
        tint = c if cat == category else DIM
        rows.append(f"   {mark} {name} {tint}{_bar(pct)}{RESET} {pct:>5.1f}%")
    return rows


def ceremony(result: dict, slow: bool = True) -> None:
    if not result["ok"]:
        print(f"\n  {result['reason']}\n")
        return

    cat = result["category"]
    c = COLOUR[cat]
    say = (lambda s, d=0.0: (print(s), time.sleep(d))) if slow else (lambda s, d=0.0: print(s))

    print()
    say(f"  {DIM}水見式 · WATER DIVINATION{RESET}", 0.4)
    say(f"  {DIM}a leaf on still water. channel your aura.{RESET}\n", 0.9)
    say(f"  {DIM}       ~ ~ ~ ~ ~ ~ ~{RESET}", 0.5)
    say(f"  {DIM}      (   the glass  ){RESET}", 0.5)
    say(f"  {DIM}       ~ ~ ~ ~ ~ ~ ~{RESET}\n", 1.1)

    say(f"  {c}{BOLD}{result['reaction'].upper()}{RESET}\n", 0.9)
    say(f"  {c}{BOLD}{cat.upper()}{RESET}  {c}{result['japanese']}{RESET}   "
        f"{DIM}{result['certainty']}{RESET}\n", 0.5)

    for row in _hexagon(result["aura"], cat, c):
        say(row, 0.08)

    opp = opposite(cat)
    print()
    say(f"  {DIM}{result['description']}{RESET}\n", 0.3)
    say(f"  {DIM}your opposite is {RESET}{COLOUR[opp]}{opp}{RESET}"
        f"{DIM} — {affinity(cat, opp)}% affinity. what costs them nothing costs you"
        f" the most.{RESET}\n", 0.2)

    print(f"  {DIM}read from{RESET}")
    for key, note in result["traces"]:
        print(f"    {DIM}{key:<24} {note}{RESET}")
    if result.get("commits"):
        print(f"    {DIM}{'commits':<24} {result['commits']}{RESET}")
    print(f"\n  {DIM}nothing left this machine · divination v{result['version']}{RESET}\n")


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="nen", description="Water Divination — read your Nen type from your code.")
    ap.add_argument("path", nargs="?", default=".", help="a repository to read")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--fast", action="store_true", help="skip the ceremony pacing")
    a = ap.parse_args()

    repo = Path(a.path).expanduser().resolve()
    if not repo.is_dir():
        raise SystemExit(f"not a directory: {repo}")

    result = divine(repo)
    if a.json:
        print(json.dumps(result, indent=2))
    else:
        ceremony(result, slow=not a.fast)
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
