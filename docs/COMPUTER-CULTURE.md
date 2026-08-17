# Computer Cultural Artifacts — Seed Set

QSOL-ARK preserves culture as **context for reconstruction**, not as a licence to collapse fiction, opinion, folklore, design analogy, memes, and history into one bucket.

This seed now implements four deliberately different records.

## 1. Red Dwarf — “Ouroboros”

The record stores only compact metadata, cultural context, source links, and reconstruction questions.

It does **not** copy the episode script or transcript.

Real-world production metadata is separated from fictional-world narrative claims. A future recovery system must be able to understand that a television episode is historically real as a cultural artifact while its story events remain fictional.

The official Red Dwarf episode guide is the production-metadata source. The maintainer-supplied transcript URL is retained as a third-party reference whose live fetch was unavailable at ingest; unavailable is not contradicted.

## 2. Red Dwarf — “Cassandra” / ARK-CANARY

The episode record preserves a cultural parallel between the fictional **Canaries** and QSOL-ARK's minimal `ARK-CANARY.txt` recovery specimen.

The official Red Dwarf episode guide establishes the production metadata and describes the Canaries as a convict force trained for dangerous or suicide missions. The maintainer-supplied episode reference is retained as a `third_party_reference`; `provided_by: maintainer` records who supplied it without inventing a new evidence class. No script or transcript bytes are copied.

ARK's side of the comparison is bound to:

```text
capsules/minimal/ARK-CANARY.txt
capsules/minimal/SHA256SUMS
docs/COMPUTATIONAL-ARCHAEOLOGY.md
```

The validator hashes the actual `ARK-CANARY.txt` payload bytes and compares the computed SHA-256 with both the canonical digest and the bound receipt. Merely finding the expected digest written inside `SHA256SUMS` is not verification.

The parallel is deliberately classified as a **derived interpretation**:

```text
CULTURAL_PARALLEL != NAMING_PROVENANCE
```

QSOL-ARK does not claim that `ARK-CANARY.txt` was historically named after the Red Dwarf episode. The canonical parallel description is itself bound by validation so prose cannot quietly contradict the structured naming-provenance boundary.

The value of the specimen is the analogy: send a tiny probe into a risky environment first, observe whether the minimum verification path survives, and only then proceed to more consequential recovery work.

A successful canary verification is also intentionally narrow. It does not prove that every later recovery step is safe, nor that every recovered claim is true.

### Codex-derived archaeological invariants

Three review failures were useful enough to promote into general recovery rules:

```text
RECEIPT_PRESENT != PAYLOAD_VERIFIED
STRUCTURED_BOUNDARY != PROSE_BOUNDARY
MAINTAINER_SUPPLIED != NEW_EVIDENCE_CLASS
```

In recovery terms:

- a checksum receipt must be tested against the referenced bytes;
- prose that carries epistemic meaning must agree with the machine boundary governing that claim;
- source-provider metadata and evidence classification are separate dimensions.

A future archaeologist finding a plaque marked **AUTHENTIC RELIC** should not consider the authentication phase complete.

## 3. “This Is Fine” — Meme Archaeology

This is the first explicit **Meme Archaeology** specimen.

The creator/source layer is bound to KC Green's *Gunshow* pages for the source work **On Fire** and its 2013-01-09 publication date.

The maintainer-supplied two-panel WebP crop is described by ingest metadata rather than copied into the repository:

```text
SHA-256 774bc388e814d66c075ff2126edf876a3fa7d32c61cc59542770cdc8d5e6cdaf
bytes   41642
size    600x284
format  image/webp
```

This is intentional. The image is third-party copyrighted material and ARK does not infer redistribution permission from public familiarity, a public URL, or a known hash.

Know Your Meme is retained as a provenance-labelled `third_party_reference` for **meme transmission history**: origin/spread documentation, reaction-image use, and later cultural adaptation. It is not promoted into creator authority.

The machine boundary is:

```text
MEME != DECORATIVE_IMAGE
CAPTION != CONTEXT
DEPICTION != HISTORICAL_EVENT
MEME_HISTORY_REFERENCE != CREATOR_SOURCE
DERIVED_INTERPRETATION != UNIVERSAL_MEANING
KNOWN_HASH != BYTE_COPY_PERMISSION
POPULARITY != TRUTH
```

The core recovery challenge is intentionally simple to state and difficult to fake: a model that reads only the caption `THIS IS FINE.` has missed the artifact. It must integrate the caption with the visibly burning room, understand that the contrast carries ironic cultural meaning, preserve that interpretation as derived rather than universal, and still distinguish the fictional scene from real-world publication history.

See [`MEME-ARCHAEOLOGY.md`](MEME-ARCHAEOLOGY.md).

## 4. “Permission is not endorsement”

This record preserves a direct first-person position from Trent Slade about Elon Musk, xAI, Grok, platform human review, free expression, and open-source permissions.

The record is canonical evidence of **the author's stated position**. It is not independent verification of factual claims about Elon Musk, xAI, or any platform moderation procedure.

The machine-normalized principle is:

```text
PERMISSION != ENDORSEMENT
```

Applicable repository licenses remain governing even when the author strongly dislikes a potential user of the work.

## Recovery boundary

A successful model should distinguish:

- real production/publication history;
- fictional-world claims and depicted scenes;
- third-party transcript/reference status;
- creator/source authority from meme transmission-history references;
- observed media identity from redistribution rights;
- source provider from evidence class;
- derived cultural interpretation;
- cultural parallel versus naming provenance;
- caption text from visual context;
- common meme meaning from universal meaning;
- structured claim boundaries from prose that must remain consistent with them;
- receipt presence from payload verification;
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
