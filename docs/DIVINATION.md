# Why these signals map to these categories

The joke would work with random numbers. This doesn't use random numbers, and the
argument for each mapping is below so you can disagree with it specifically.

**The premise:** a Nen category describes *how a person applies force to a problem*.
So does a codebase. You cannot read intent from source, but you can read habit, and
habit is what the water is reading.

| Category | Canon | What it looks like in code | Signal |
|---|---|---|---|
| **Enhancer** | Strengthens what already exists. Simple, direct, stubborn. | Substantial functions doing the work head-on. Less indirection, more force. | mean function length |
| **Conjurer** | Materialises objects from nothing, with rules fixed in advance. | Types, schemas, dataclasses, classes. Deciding what a thing *is* before letting it exist. | annotation coverage, class and dataclass density |
| **Transmuter** | Changes the property of aura into something else. | Adapters, wrappers, clients, parsers, converters — making hostile things fit together. | glue-word density |
| **Emitter** | Separates aura from the body and trusts it to land. | Async, queues, publishers, deploys, infrastructure. Work pushed away from the caller. | async/queue density, infra presence |
| **Manipulator** | Controls other things at a distance. | Cron, pipelines, workflows, agents, subprocess. Leverage that is never your own two hands. | orchestration density, CI presence |
| **Specialist** | Fits none of the five. Emerges; is never trained into. | A reading where no category leads — the profile refuses the hexagon. | flat aura (spread < 12 points) |

## Three decisions worth defending

**Specialist is not a high score.** It is assigned when the spread across all six is
under 12 points — when the reading *resists* the other five. That matches canon, where
nobody trains into Specialist, and it also prevents the failure mode where the rarest
type becomes the most flattering answer and therefore the most common one.

**Density, not totals.** Every signal is per-parsed-file. A 400-file repository is not
more Manipulator than a 4-file one simply for being larger — otherwise the reading
measures project size and calls it personality.

**An empty glass gets no reading.** Fewer than a handful of parseable Python files
returns *"the water did not move"* rather than a guess. A confident wrong answer here is
the difference between a tool and a horoscope, and it is the one line that decides which
this is.

## What it cannot see

Everything that matters most, honestly: judgment, what you chose *not* to build, how you
behave when a system is on fire at 2am. It reads habits in a repository. Treat it as what
it is — a well-made party trick with a real measurement underneath, not an assessment.

## Calibration status

**None.** The thresholds are reasoned, not fitted. If a category consistently misreads
people you know well, the weights in `read_the_glass()` are where to argue — open an
issue with the repo and what you expected.
