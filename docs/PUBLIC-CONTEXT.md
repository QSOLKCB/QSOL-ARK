# Public Context Seed Pack

QSOL-ARK is public by construction. QSOL-CONTEXT is private.

The safe transfer rule is therefore:

```text
PRIVATE_DISCOVERY != PUBLIC_AUTHORITY
PUBLIC_SUBSTRATE_SLICE != PRIVATE_CONTEXT_COPY
VISIBILITY_PUBLIC != EXPORT_CLEARANCE
POST_SNAPSHOT_PUBLIC_EVIDENCE != PRIVATE_CONTEXT_EXPORT
```

## Method

QSOL-CONTEXT may be used privately to identify candidate material worth preserving, but ARK does not copy those private records into the public repository.

A candidate becomes an ARK public-context seed only after it is re-anchored to an already-public source. The initial pack prefers the public QSOL-SUBSTRATE registries and their pinned first-party source references. A newer artifact that post-dates the pinned substrate snapshot may instead use independently public, commit-pinned first-party evidence when the repository, release, source hash, licence boundary, and publication identity are all explicit.

The canonical seed index is:

```text
context/public-seeds.json
```

Validation is offline and deterministic:

```sh
python3 tools/public_context.py
python3 -m unittest tests.test_public_context -v
```

## Initial seed set

The first pack deliberately covers different reconstruction roles:

- `seed:identity:trent-slade` — public identity anchor;
- `seed:project:qsol-substrate` — public-context and provenance anchor;
- `seed:project:whoami-18437` — deterministic software-art and satire boundary;
- `seed:project:deepseekc64` — transcript provenance and bounded Lean formalization;
- `seed:project:e8-music` — deterministic sonification;
- `seed:project:games` — deterministic browser games;
- `seed:project:uff` — scientific reproducibility and formal assurance;
- `seed:project:saw-1` — provenance-bounded sonification, industrial transformation, and an accidental `(3,2)` formal correspondence.

This is a seed set, not a complete catalogue.

## SAW-1 post-snapshot seed

SAW-1 was released after the QSOL-SUBSTRATE snapshot pinned by this seed pack, so ARK does not pretend that the older substrate already contained it. The seed is instead anchored directly to the public first-party repository and release:

```text
repository: QSOLKCB/SAW-1
release: v1.0.1
release commit: db4166e8903ccee055f8d847d846b591012641f2
CITATION.cff blob: ed5d748e1e8d828be00ffd5766182f69bb315894
DOI: 10.5281/zenodo.21984110
```

The preserved citation is:

> Slade, T. (2026). *SAW-1 — Spooky Action at Work: A Lightweight Formalization of ETQ-101 Sonification, Industrial Transformation, and an Accidental (3,2) Correspondence* (Version v1.0.1). Zenodo. https://doi.org/10.5281/zenodo.21984110

ARK also preserves a visible metadata discrepancy rather than silently normalising it away: the public GitHub release tag is `v1.0.1`, while `CITATION.cff`, `.zenodo.json`, and the tagged README still declare the embedded technical-note metadata version as `1.0.0`. The seed therefore records both the supplied citation version and the repository-declared metadata version.

This is useful archaeology: a future recovery system should preserve conflicting public version surfaces as evidence, not choose whichever one makes the record look tidier.

## What is deliberately not imported

- no QSOL-CONTEXT file bytes;
- no private QSOL-CONTEXT commit or path receipts;
- no field merely because it exists in QSOL-CONTEXT;
- no private-only chronology, environment, profile, identity, relationship, or project detail;
- no inferred public-export permission;
- no private SAW-1 source-lab archive, song recordings, or excluded audio bytes.

The public seed record stores normalized metadata and provenance pointers only. Authoritative evidence comes from the pinned public QSOL-SUBSTRATE snapshot or explicitly pinned first-party public evidence.

## Fail-closed behavior

The validator rejects:

- a seed whose authority points directly at QSOL-CONTEXT;
- any claim that private payload bytes were imported;
- unknown or non-public visibility;
- missing or substituted source hashes;
- unpinned or substituted release commits;
- malformed or substituted DOI records;
- duplicate or substituted seed IDs;
- source-reference semantic drift;
- promotion of metadata-only seeds into copied source bytes;
- mutation of the SAW-1 citation, source commit, or recorded version discrepancy.

A future explicit QSOL-CONTEXT export can be admitted only when it carries the clearance evidence required by `ai/context-sources.json`. Until then, the public substrate or independently public first-party route is the safe bridge.
