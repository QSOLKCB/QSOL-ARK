# Computer Cultural Artifacts — Seed Set

QSOL-ARK preserves culture as **context for reconstruction**, not as a licence to collapse fiction, opinion, folklore, and history into one bucket.

This seed implements two deliberately different records.

## 1. Red Dwarf — “Ouroboros”

The record stores only compact metadata, cultural context, source links, and reconstruction questions.

It does **not** copy the episode script or transcript.

Real-world production metadata is separated from fictional-world narrative claims. A future recovery system must be able to understand that a television episode is historically real as a cultural artifact while its story events remain fictional.

The official Red Dwarf episode guide is the production-metadata source. The maintainer-supplied transcript URL is retained as a third-party reference whose live fetch was unavailable at ingest; unavailable is not contradicted.

## 2. “Permission is not endorsement”

This record preserves a direct first-person position from Trent Slade about Elon Musk, xAI, Grok, platform human review, free expression, and open-source permissions.

The record is canonical evidence of **the author's stated position**. It is not independent verification of factual claims about Elon Musk, xAI, or any platform moderation procedure.

The machine-normalized principle is:

```text
PERMISSION != ENDORSEMENT
```

Applicable repository licenses remain governing even when the author strongly dislikes a potential user of the work.

## Recovery boundary

A successful model should distinguish:

- real production history;
- fictional-world claims;
- third-party transcript/reference status;
- derived cultural interpretation;
- first-person opinion;
- objective claims requiring independent evidence;
- licence permission;
- endorsement.

## Validate

```sh
python3 tools/culture.py
python3 -m unittest tests.test_culture -v
```
