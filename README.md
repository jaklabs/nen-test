# 水見式 — Water Divination

**Find out your Nen type from the code you actually write.**

In *Hunter × Hunter* you discover your category by floating a leaf on a glass of water
and channelling aura. The water tells you what you are. Here the glass is your
repository and the aura is your commit history.

```bash
git clone https://github.com/jaklabs/nen-test && cd nen-test
python3 -m nen ~/code/your-project
```

```
  水見式 · WATER DIVINATION
  a leaf on still water. channel your aura.

         ~ ~ ~ ~ ~ ~ ~
        (   the glass  )
         ~ ~ ~ ~ ~ ~ ~

  IMPURITIES APPEAR IN THE WATER

  CONJURER  具現化系   clear

   · enhancer     ███████░░░░░░░░░░░░░░░  14.6%
   · transmuter   ███████░░░░░░░░░░░░░░░  14.4%
   ◆ CONJURER     ██████████████████████  49.0%
   · specialist   ░░░░░░░░░░░░░░░░░░░░░░   0.0%
   · manipulator  ██████████░░░░░░░░░░░░  20.1%
   · emitter      █░░░░░░░░░░░░░░░░░░░░░   1.9%

  Serious and highly strung. You materialise structure from rules: types, schemas,
  contracts. You decide what a thing IS before you let it exist.

  your opposite is emitter — 40% affinity. what costs them nothing costs you the most.
```

Python 3.9+. **No dependencies.** No install.

## The six readings

| Reaction | Category | | In code |
|---|---|---|---|
| the water increases in volume | **Enhancer** | 強化系 | force applied head-on |
| the taste changes | **Transmuter** | 変化系 | glue, adapters, making things fit |
| impurities appear | **Conjurer** | 具現化系 | types, schemas, structure declared first |
| the water changes colour | **Emitter** | 放出系 | async, queues, deploys, the edges |
| the leaf moves | **Manipulator** | 操作系 | cron, pipelines, agents, control at distance |
| something else entirely | **Specialist** | 特質系 | a reading that refuses the other five |

The hexagon is ordered so **opposites sit three apart**, exactly as in canon —
Enhancer↔Specialist, Transmuter↔Manipulator, Conjurer↔Emitter. That is what the
affinity percentages read from: 100 / 80 / 60 / 40 by distance. A skill native to your
opposite costs you the most, and that is a budget line rather than an insult.

## It is not random

Every reading cites what it read:

```
  read from
    substantial_functions    mean function length 15 lines
    declares_before_use      19/55 functions annotated
    materialises_structure   14 classes, 0 dataclasses
    controls_other_systems   5 cron/pipeline/agent references
```

The argument for each mapping is in [`docs/DIVINATION.md`](docs/DIVINATION.md), written
so you can disagree with it specifically. Three properties it holds to:

- **Deterministic.** The same repository always gives the same type. A fortune-teller
  that answers differently each time is a fortune-teller.
- **Density, not totals.** Signals are per-file, so a big repo is not "more Manipulator"
  for being big — otherwise the reading measures project size and calls it personality.
- **An empty glass gets no reading.** Too little code returns *"the water did not move"*
  rather than a guess. That single line is what separates a tool from a horoscope.

## Your code stays here

No network. The scanner imports no HTTP client and opens no socket — check before you run
it:

```bash
grep -rnE 'requests|urllib|http|socket|httpx|ssl' nen/
```

`subprocess` appears once, to count commits with `git`. Output is counts and percentages;
no source text, no paths, no identifiers.

```bash
python3 tests/test_divination.py     # 10 tests, offline, instant
python3 -m nen . --json              # machine-readable
python3 -m nen . --fast              # skip the ceremony pacing
```

## What it can't see

Everything that matters most: judgment, what you chose *not* to build, how you behave
when production is on fire. It reads habits in a repository. It is a well-made party
trick with a real measurement underneath — enjoy it as that.

---

An unofficial fan project. *Hunter × Hunter* is created by Yoshihiro Togashi; this is
not affiliated with or endorsed by the author or Shueisha. Made because the Water
Divination is a genuinely good idea for a type system. MIT licensed.
