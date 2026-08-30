"""Tests for the divination.

The one property that matters most: **a repository always gives the same reading.**
A fortune-teller that answers differently each time is a fortune-teller.
"""
import ast
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from nen.divination import (HEXAGON, REACTIONS, affinity, divine,  # noqa: E402
                            opposite, read_the_glass)

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_the_hexagon_holds_the_canonical_opposites():
    assert opposite("enhancer") == "specialist"
    assert opposite("transmuter") == "manipulator"
    assert opposite("conjurer") == "emitter"
    assert all(opposite(opposite(c)) == c for c in HEXAGON)


def test_affinity_matches_the_canon_percentages():
    assert affinity("enhancer", "enhancer") == 100
    assert affinity("enhancer", "transmuter") == 80    # adjacent
    assert affinity("enhancer", "conjurer") == 60      # two steps
    assert affinity("enhancer", "specialist") == 40    # opposite


def test_every_category_has_its_reaction():
    assert set(REACTIONS) == set(HEXAGON)
    assert REACTIONS["enhancer"] == "the water increases in volume"
    assert REACTIONS["manipulator"] == "the leaf moves"


def test_the_same_repository_always_reads_the_same():
    a, b = divine(ROOT), divine(ROOT)
    assert a["category"] == b["category"]
    assert a["aura"] == b["aura"]


def test_the_aura_sums_to_one_hundred():
    r = divine(ROOT)
    assert r["ok"] and abs(sum(r["aura"].values()) - 100) < 0.5


def test_an_empty_glass_refuses_to_read():
    """No Python to read means no reading. It must not invent a type -- a made-up
    answer here is exactly what turns this from a toy into a horoscope."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        (pathlib.Path(d) / "notes.txt").write_text("nothing here")
        r = divine(pathlib.Path(d))
    assert r["ok"] is False
    assert "did not move" in r["reason"]


def test_specialist_emerges_and_is_never_assigned_by_strength():
    """In canon nobody trains into Specialist -- it is what is left when a reading
    refuses the other five. Here that is a flat aura, not a high score."""
    src = pathlib.Path(ROOT / "nen" / "divination.py").read_text()
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "divine")
    body = ast.get_source_segment(src, fn) or ""
    assert "spread" in body and "specialist" in body


def test_a_failed_git_call_returns_none_not_an_empty_string():
    """Absent and empty are different facts. An empty string reads downstream as
    'no history', which would score an active repository as dormant."""
    from nen.divination import _git
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        assert _git(pathlib.Path(d), "rev-list", "--count", "HEAD") is None


def test_nothing_here_touches_the_network():
    """Your code is the glass. It does not leave the room."""
    banned = {"requests", "urllib", "http", "socket", "httpx", "aiohttp", "ssl"}
    for f in (ROOT / "nen").glob("*.py"):
        tree = ast.parse(f.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    assert a.name.split(".")[0] not in banned, f"{f.name}: {a.name}"
            elif isinstance(node, ast.ImportFrom):
                assert (node.module or "").split(".")[0] not in banned, f.name


def test_the_reading_cites_what_it_read():
    """Every claim carries evidence, or it is astrology with a terminal."""
    r = divine(ROOT)
    assert r["traces"] and all(note for _, note in r["traces"])


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print(f"  PASS  {name}")
            except AssertionError as e:
                fails += 1; print(f"  FAIL  {name}: {e}")
    print(f"\n{'all passed' if not fails else str(fails) + ' FAILED'}")
    sys.exit(1 if fails else 0)
