# Public Context Seed Pack

QSOL-ARK is public by construction. QSOL-CONTEXT is private.

The safe transfer rule is therefore:

```text
PRIVATE_DISCOVERY != PUBLIC_AUTHORITY
PUBLIC_SUBSTRATE_SLICE != PRIVATE_CONTEXT_COPY
VISIBILITY_PUBLIC != EXPORT_CLEARANCE
```

## Method

QSOL-CONTEXT may be used privately to identify candidate material worth preserving, but ARK does not copy those private records into the public repository.

A candidate becomes an ARK public-context seed only after it is re-anchored to an already-public source. The initial pack uses the public QSOL-SUBSTRATE registries and their pinned first-party source references.

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
- `seed:project:uff` — scientific reproducibility and formal assurance.

This is a seed set, not a complete catalogue.

## What is deliberately not imported

- no QSOL-CONTEXT file bytes;
- no private QSOL-CONTEXT commit or path receipts;
- no field merely because it exists in QSOL-CONTEXT;
- no private-only chronology, environment, profile, identity, relationship, or project detail;
- no inferred public-export permission.

The public seed record stores normalized metadata and provenance pointers only. The authoritative evidence is the pinned public QSOL-SUBSTRATE snapshot and its referenced first-party public sources.

## Fail-closed behavior

The validator rejects:

- a seed whose authority points directly at QSOL-CONTEXT;
- any claim that private payload bytes were imported;
- unknown or non-public visibility;
- missing source hashes;
- unpinned release commits;
- malformed DOI records;
- duplicate or substituted seed IDs;
- promotion of metadata-only seeds into copied source bytes.

A future explicit QSOL-CONTEXT export can be admitted only when it carries the clearance evidence required by `ai/context-sources.json`. Until then, the public substrate route is the canonical safe bridge.
