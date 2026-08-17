# Computer Cultural Artifacts — Seed Set

QSOL-ARK preserves culture as **context for reconstruction**, not as a licence to collapse fiction, opinion, folklore, design analogy, and history into one bucket.

This seed now implements three deliberately different records.

## 1. Red Dwarf — “Ouroboros”

The record stores only compact metadata, cultural context, source links, and reconstruction questions.

It does **not** copy the episode script or transcript.

Real-world production metadata is separated from fictional-world narrative claims. A future recovery system must be able to understand that a television episode is historically real as a cultural artifact while its story events remain fictional.

The official Red Dwarf episode guide is the production-metadata source. The maintainer-supplied transcript URL is retained as a third-party reference whose live fetch was unavailable at ingest; unavailable is not contradicted.

## 2. Red Dwarf — “Cassandra” / ARK-CANARY

The episode record preserves a cultural parallel between the fictional **Canaries** and QSOL-ARK's minimal `ARK-CANARY.txt` recovery specimen.

The official Red Dwarf episode guide establishes the production metadata and describes the Canaries as a convict force trained for dangerous or suicide missions. The maintainer-supplied episode reference is retained as a third-party reference only; no script or transcript bytes are copied.

ARK's side of the comparison is bound to:

```text
capsules/minimal/ARK-CANARY.txt
capsules/minimal/SHA256SUMS
docs/COMPUTATIONAL-ARCHAEOLOGY.md
```

The parallel is deliberately classified as a **derived interpretation**:

```text
CULTURAL_PARALLEL != NAMING_PROVENANCE
```

QSOL-ARK does not claim that `ARK-CANARY.txt` was historically named after the Red Dwarf episode. The value of the specimen is the analogy: send a tiny probe into a risky environment first, observe whether the minimum verification path survives, and only then proceed to more consequential recovery work.

A successful canary verification is also intentionally narrow. It does not prove that every later recovery step is safe, nor that every recovered claim is true.

## 3. “Permission is not endorsement”

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
- cultural parallel versus naming provenance;
- first-person opinion;
- objective claims requiring independent evidence;
- licence permission;
- endorsement;
- successful minimal verification versus universal safety or truth.

## Validate

```sh
python3 tools/culture.py
python3 -m unittest tests.test_culture -v
```
