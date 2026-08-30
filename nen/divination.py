"""Water Divination — determine a developer's Nen type from the code they write.

    In canon you float a leaf on a glass of water, channel aura, and read the
    reaction. Here the glass is your repository and the aura is your commit history.

    NO NETWORK. Your source never leaves this machine; only counts are computed.

The six reactions are canon:

    Enhancer      the water increases in volume
    Transmuter    the taste of the water changes
    Conjurer      impurities appear in the water
    Emitter       the water changes colour
    Manipulator   the leaf moves
    Specialist    something else entirely happens

The mapping from code to category is the interesting part and is argued in
`docs/DIVINATION.md`. Short version: Nen categories describe *how you apply force*,
and so does a codebase. An Enhancer strengthens what is already there; in code that
looks like direct, substantial functions doing the work head-on. A Conjurer
materialises objects from nothing; in code that is types, schemas and contracts
declared before use. Neither is better. That is the whole point of the hexagon.
"""

from __future__ import annotations

import ast
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import NamedTuple

DIVINATION_VERSION = "1.0.0"

SKIP = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build",
        ".next", "target", "vendor", ".mypy_cache", ".pytest_cache", "coverage"}

# Clockwise on the hexagon. Opposites are three apart, exactly as in canon.
HEXAGON: tuple[str, ...] = (
    "enhancer", "transmuter", "conjurer", "specialist", "manipulator", "emitter",
)

REACTIONS = {
    "enhancer":    "the water increases in volume",
    "transmuter":  "the taste of the water changes",
    "conjurer":    "impurities appear in the water",
    "specialist":  "something else entirely happens",
    "manipulator": "the leaf moves",
    "emitter":     "the water changes colour",
}

JAPANESE = {
    "enhancer": "強化系", "transmuter": "変化系", "conjurer": "具現化系",
    "specialist": "特質系", "manipulator": "操作系", "emitter": "放出系",
}

DESCRIPTIONS = {
    "enhancer": ("Simple, determined, and direct. You make things stronger by going at "
                 "them head-on, and you keep going after other people have stopped."),
    "transmuter": ("Whimsical and cunning. You change the property of what you are given "
                   "— glue, adapters, wrappers — and you make hostile things fit together."),
    "conjurer": ("Serious and highly strung. You materialise structure from rules: types, "
                 "schemas, contracts. You decide what a thing IS before you let it exist."),
    "specialist": ("Individualistic and charismatic. You do not fit the other five, and "
                   "the problem tends to change shape around you rather than the reverse."),
    "manipulator": ("Logical and argumentative. You control other systems — automation, "
                    "pipelines, agents. Your leverage is never your own two hands."),
    "emitter": ("Impatient and short-tempered. You push work away from yourself and trust "
                "it to land — queues, deploys, async, the edges of the system."),
}


class Trace(NamedTuple):
    """One measurable habit, and which category it is evidence of."""
    key: str
    weight: dict[str, float]
    note: str


# ---------------------------------------------------------------------------
# Reading the glass
# ---------------------------------------------------------------------------

def _walk(repo: Path):
    import os
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs
                   if d not in SKIP and not (Path(root) / d / ".git").exists()]
        for f in files:
            yield Path(root) / f


def _git(repo: Path, *args: str) -> str | None:
    """Returns None on failure -- never an empty string.

    A timeout that returns "" reads downstream as "no history", which would score
    an active repository as dormant. Absent and empty are different facts.
    """
    try:
        r = subprocess.run(["git", "-C", str(repo), *args],
                           capture_output=True, text=True, timeout=45)
        return r.stdout if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


_ASYNC = re.compile(r"\b(async |await |asyncio|celery|queue|publish|emit|producer|"
                    r"consumer|kafka|sqs|pubsub)\b", re.I)
_INFRA = re.compile(r"\b(terraform|dockerfile|kubernetes|helm|deploy|lambda|cloudfront|"
                    r"cdk|serverless|ansible)\b", re.I)
_ORCH = re.compile(r"\b(cron|schedul|workflow|pipeline|orchestrat|agent|subprocess|"
                   r"launchd|systemd|automat)\b", re.I)
_GLUE = re.compile(r"\b(adapter|wrapper|client|sdk|integrat|bridge|shim|connector|"
                   r"transform|convert|parse)\b", re.I)


def read_the_glass(repo: Path, cap: int = 400) -> tuple[dict[str, float], list[Trace]]:
    """Gather the traces. Numbers only -- no source text is retained."""
    py: list[Path] = []
    names: list[str] = []
    for f in _walk(repo):
        rel = str(f.relative_to(repo)).lower()
        names.append(rel)
        if f.suffix == ".py":
            py.append(f)

    blob = "\n".join(names)
    fn_lengths: list[int] = []
    annotated = total_fns = 0
    classes = dataclasses = 0
    async_hits = glue_hits = orch_hits = 0
    parsed = 0

    for f in py[:cap]:
        try:
            src = f.read_text(errors="ignore")
            tree = ast.parse(src)
        except (OSError, SyntaxError, ValueError):
            continue
        parsed += 1
        async_hits += len(_ASYNC.findall(src))
        glue_hits += len(_GLUE.findall(src))
        orch_hits += len(_ORCH.findall(src))
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                total_fns += 1
                if n.end_lineno and n.lineno:
                    fn_lengths.append(n.end_lineno - n.lineno + 1)
                args = list(n.args.args) + list(n.args.kwonlyargs)
                if n.returns is not None or (args and all(a.annotation for a in args)):
                    annotated += 1
            elif isinstance(n, ast.ClassDef):
                classes += 1
                if any(getattr(d, "id", getattr(d, "attr", "")) == "dataclass"
                       for d in n.decorator_list):
                    dataclasses += 1

    if not parsed:
        return {}, []

    mean_fn = sum(fn_lengths) / len(fn_lengths) if fn_lengths else 0
    per_file = lambda n: n / parsed

    traces = [
        Trace("substantial_functions", {"enhancer": min(1.0, mean_fn / 40)},
              f"mean function length {mean_fn:.0f} lines"),
        Trace("declares_before_use",
              {"conjurer": min(1.0, (annotated / total_fns) if total_fns else 0)},
              f"{annotated}/{total_fns} functions annotated"),
        Trace("materialises_structure",
              {"conjurer": min(1.0, per_file(classes + dataclasses * 2) / 1.5)},
              f"{classes} classes, {dataclasses} dataclasses"),
        Trace("bends_what_exists", {"transmuter": min(1.0, per_file(glue_hits) / 4)},
              f"{glue_hits} adapter/parse/convert references"),
        Trace("pushes_work_away", {"emitter": min(1.0, per_file(async_hits) / 4)},
              f"{async_hits} async/queue/emit references"),
        Trace("controls_other_systems", {"manipulator": min(1.0, per_file(orch_hits) / 4)},
              f"{orch_hits} cron/pipeline/agent references"),
        Trace("shapes_the_ground",
              {"emitter": 0.6 if _INFRA.search(blob) else 0.0,
               "manipulator": 0.4 if ".github/workflows" in blob else 0.0},
              "infrastructure and CI present" if _INFRA.search(blob) else "no infra"),
    ]

    aura = {t: 0.0 for t in HEXAGON}
    for tr in traces:
        for cat, v in tr.weight.items():
            aura[cat] += v
    return aura, traces


def divine(repo: Path) -> dict:
    """The reading. Deterministic: the same repository always gives the same type."""
    aura, traces = read_the_glass(repo)
    if not aura or sum(aura.values()) <= 0:
        return {"ok": False,
                "reason": "The water did not move. Too little Python here to read."}

    total = sum(aura.values())
    pct = {k: round(v / total * 100, 1) for k, v in aura.items()}
    ranked = sorted(pct.items(), key=lambda kv: -kv[1])
    (first, fv), (second, sv) = ranked[0], ranked[1]

    # Specialist is never trained into and never assigned by strength -- in canon it
    # emerges when a reading refuses the other five. Here that is a flat aura: no
    # category clearly leads, so the water does something else entirely.
    spread = fv - ranked[-1][1]
    if spread < 12:
        category, certainty = "specialist", "the reading resists the other five"
    elif fv - sv >= 8:
        category, certainty = first, "clear"
    else:
        category, certainty = first, f"leaning {first}, shading {second}"

    commits = _git(repo, "rev-list", "--count", "HEAD")
    return {
        "ok": True,
        "version": DIVINATION_VERSION,
        "category": category,
        "certainty": certainty,
        "aura": pct,
        "reaction": REACTIONS[category],
        "japanese": JAPANESE[category],
        "description": DESCRIPTIONS[category],
        "traces": [(t.key, t.note) for t in traces],
        "commits": int(commits.strip()) if commits and commits.strip().isdigit() else None,
    }


def opposite(category: str) -> str:
    return HEXAGON[(HEXAGON.index(category) + 3) % 6]


def affinity(a: str, b: str) -> int:
    """Canon percentages: 100 / 80 / 60 / 40 by distance around the hexagon."""
    i, j = HEXAGON.index(a), HEXAGON.index(b)
    d = min(abs(i - j), 6 - abs(i - j))
    return {0: 100, 1: 80, 2: 60, 3: 40}[d]
