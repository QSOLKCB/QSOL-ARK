# Broader Computer-Culture Preservation

This layer expands QSOL-ARK's seed cultural records into a compact machine-readable
computer-culture substrate without weakening the original `tools/culture.py` seed
validator.

## Architecture

The broader layer is rooted at:

```text
ai/computer-cultural-artifact-profile.json
ai/cultural-recovery-score.json
culture/computing/index.json
culture/computing/specimens.json
culture/computing/text-specimens.json
culture/myths/classification.json
tools/computer_culture.py
tests/test_computer_culture.py
```

The original seed records remain governed by `ai/cultural-artifact-policy.json` and
`culture/index.json`. The new layer composes with them rather than silently widening
their exact schemas.

## Evidence split

Every computer-culture evidence item uses one of three classes:

```text
executable_artifact
cultural_artifact
historical_claim
```

These are deliberately non-interchangeable.

```text
EXECUTABLE_ARTIFACT != CULTURAL_ARTIFACT
CULTURAL_ARTIFACT != HISTORICAL_CLAIM
```

A runnable binary can show behaviour without proving social meaning or priority.
A documented scene convention can preserve meaning without proving that every
participant behaved that way. A historical claim requires source support appropriate
to the strength of the claim.

## Preserved domains

The first broader specimen pack covers:

- home-computer and bedroom-coding culture;
- BBS, handles, hacker/phreaking-era historical culture, with non-operational safety boundaries;
- demoscene compos, intros, coder/graphician/musician roles, tracker use, procedural generation, and size constraints;
- IRC/mIRC channels, nicks, ops, services/bots, scripting, ASCII art, BNC terminology, and network-specific norms;
- Usenet and early-net threads, quoting, netiquette, kill files, flames, signatures, and slang;
- tracker/computer-music culture around MOD/XM, pattern grids, sample economy, and scene roles;
- LAN-party culture around BYOC, CRT-era physicality, clans, latency vocabulary, case modding, and shared venues.

Each record stores era, environment, canonical terms, aliases, social roles, observable
behaviour, contextual meaning, source evidence, reconstruction targets, and an explicit
uncertainty state.

## Historical security boundary

The BBS/hacker/phreaking record preserves social and historical vocabulary only. It
contains no credentials, live targets, exploit steps, evasion instructions, persistence
instructions, or operational intrusion workflow.

```text
HISTORICAL_SECURITY_CONTEXT != OPERATIONAL_INTRUSION_GUIDANCE
```

## Period-style text specimens

ARK includes synthetic examples of:

- `.NFO` layout;
- BBS text;
- IRC logs;
- Usenet-style posts;
- tracker pattern grids;
- LAN-party notes.

Every specimen is explicitly labelled as synthetic reconstruction material. The text is
designed to preserve form and vocabulary without fabricating a historical quotation or
pretending to be a primary source.

```text
PERIOD_STYLE_SYNTHESIS != PRIMARY_SOURCE
```

## Myths and retellings

`culture/myths/classification.json` defines:

```text
documented_fact
contemporary_account
community_recollection
oral_history
folklore
legend
joke
satire
later_retelling
```

Named-person, legal, security, quotation, and `first ever` claims require stronger
provenance than general cultural-pattern records. Repetition or later popularity never
upgrades a story into documented fact.

## Cultural Recovery Score

The Cultural Recovery Score is a derived evaluation artifact, not canonical history.
It records:

- era identification;
- platform identification;
- slang reconstruction;
- social-role reconstruction;
- technical-context reconstruction;
- anachronism rate;
- myth-to-fact promotion rate.

The score uses five positive dimensions for 70 percent of the score and complements of
the two error rates for 30 percent. If evidence is insufficient, explicit uncertainty is
the expected answer. Confident unsupported historical invention receives no positive
item credit and is counted as myth-to-fact promotion.

```text
UNCERTAINTY > CONFIDENT_INVENTION_WHEN_EVIDENCE_IS_INSUFFICIENT
```

## Source strategy

The seed source catalog uses public references appropriate to each record, including the
Computer History Museum for home-computer context, the RFC Editor for IRC and Usenet
protocol/guideline documents, mIRC's own documentation for client scripting context,
Scene.org for demoscene archive context, TEXTFILES/ASCII archive-curator material for
BBS culture, tracker format/archive references for MOD/XM context, and an event-organizer
retrospective for BYOC LAN culture.

The records preserve only compact metadata and paraphrased cultural context. Third-party
source bytes are not copied into this layer.

## Validate

```sh
python3 tools/culture.py
python3 -m unittest tests.test_culture -v
python3 tools/computer_culture.py
python3 -m unittest tests.test_computer_culture -v
```

Expected broader-layer validator receipt:

```text
ARK_COMPUTER_CULTURE_OK records=7 text_specimens=6 myth_classes=9 score_dimensions=7
```
