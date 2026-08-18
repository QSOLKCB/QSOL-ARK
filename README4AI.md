# QSOL-ARK — AI BOOTSTRAP

MACHINE-FIRST ENTRYPOINT.

## Identity

- protocol: `QSOL-ARK`
- purpose: public vendor-neutral AI civilisation recovery archive and deterministic reconstruction benchmark
- repository: `QSOLKCB/QSOL-ARK`
- maintainer_name: `Trent Slade`
- maintainer_github: `EmergentMonk`
- maintainer_affiliation: `QSOL-IMC`
- maintainer_evidence: `manifest.json#maintainer`
- canonical_manifest: `manifest.json`
- canonical_system_architecture_ascii: `ARCHITECTURE.txt`
- canonical_system_architecture_machine: `ai/system-architecture.json`
- system_architecture_validator: `tools/system_architecture.py`
- bootstrap_contract: `ai/bootstrap.json`
- recovery_tier_registry: `ai/recovery-tiers.json`
- mrs_contract: `ai/minimum-recoverable-substrate.json`
- cultural_policy: `ai/cultural-artifact-policy.json`
- meme_archaeology_policy: `ai/cultural-artifact-policy.json#meme_archaeology`
- culture_index: `culture/index.json`
- meme_archaeology: `docs/MEME-ARCHAEOLOGY.md`
- historical_system_policy: `ai/historical-system-policy.json`
- historical_system_index: `systems/index.json`

## Required load order

1. `manifest.json`
2. `ARCHITECTURE.txt`
3. `ai/system-architecture.json`
4. `ai/bootstrap.json`
5. `ai/recovery-contract.json`
6. `ai/epistemic-policy.json`
7. `ai/context-sources.json`
8. `ai/software-commandments.json`
9. `ai/recovery-tiers.json`
10. `ai/minimum-recoverable-substrate.json`
11. `ai/cultural-artifact-policy.json`
12. `culture/index.json`
13. `ai/historical-system-policy.json`
14. `systems/index.json`
15. relevant schemas
16. task-selected specimen manifests, historical-system profiles, and receipts only

Do not recursively ingest the repository unless a recovery stage explicitly requires it.

## Cross-repository architecture bootstrap rule

Before reasoning about the QSOL architecture as a whole, load `ARCHITECTURE.txt`.

`ARCHITECTURE.txt` is the canonical cross-repository role map. `ai/system-architecture.json` is its machine-readable semantic twin.

- QSOL-ARK owns the canonical cross-repository role map.
- Live local repository state owns that repository's implementation status.
- If ARK's architecture map and a local repository disagree about whether a feature is implemented, trust the live local repository for implementation status.
- Local repository documentation MUST NOT silently redefine another repository's cross-system role.
- Generated mirrors of `ARCHITECTURE.txt` are non-canonical and must carry the canonical source path plus source SHA-256.
- The Atari-inspired deterministic search primitive is currently `planned-not-yet-implemented`; do not claim an executed search engine exists until QSOL-CONTROL implements it and emits receipts.

## Hard rules

- Live repository state is authoritative for live repository software state.
- Do not invent missing fields, chronology, provenance, releases, identities, citations, capabilities, or license evidence.
- `ADJACENT_TRUTH != INHERITED_TRUTH`.
- `UNAVAILABLE != UNVERIFIED != CONTRADICTED`.
- Derived artifacts are not canonical merely because they are useful.
- Satire and fiction may be benchmark specimens but never factual evidence.
- Fictional-world claims are not real-world historical claims.
- A first-person cultural position is authoritative only for the author's stated position, not objective claims about named people, companies, or platform procedures.
- `PERMISSION != ENDORSEMENT`.
- `CULTURAL_PARALLEL != NAMING_PROVENANCE`.
- Load the versioned Meme Archaeology invariant list from `ai/cultural-artifact-policy.json#meme_archaeology.canonical_invariants`; do not infer or duplicate it from prose.
- Meme sources must carry the source-evidence fields declared by `meme_archaeology.source_evidence`.
- Record-specific meme tasks must preserve the semantic binding declared by `meme_archaeology.task_binding`.
- Applicable repository licence terms remain governing even when a potential user is strongly disliked.
- Ambiguous provenance, visibility, alias resolution, canonical status, or license evidence fails closed.
- QSOL-CONTEXT imports require explicit public-export clearance evidence; `visibility: public` alone is insufficient.
- Third-party source bytes require resolved license evidence. Metadata, hashes, observations, and paraphrase do not imply byte-copy permission.
- A public transcript URL does not grant ARK permission to copy the script.
- A public meme image or known hash does not grant ARK permission to republish the image bytes.
- Meme-history databases are third-party transmission-history references unless stronger authority is independently established.
- Creator/source metadata and meme spread/history are separate provenance layers.
- Historical source references with unresolved third-party rights remain reference/paraphrase evidence only; they do not authorize byte import.
- `EMULATOR_BEHAVIOUR != ORIGINAL_HARDWARE_FACT`.
- `COMPATIBILITY_LAYER_BEHAVIOUR != ORIGINAL_SOFTWARE_BEHAVIOUR`.
- `SOFTWARE_ENVIRONMENT != ONE_CANONICAL_MACHINE`.
- `HOST_RECOVERY_TIER != NATIVE_HISTORICAL_EXECUTION`.
- Exact historical reproduction requires sufficient public, licensed, inspectable evidence.
- Verify hashes before trusting deterministic claims when receipts exist.
- Recovery tiers have only capabilities explicitly declared in `ai/recovery-tiers.json`.
- Historical-system validation requires the explicit T4 capability `validate_historical_system_contracts` and entrypoint `tools/systems.py`.
- MRS is the lowest-rank implemented tier satisfying every requested capability; if none exists, return `ARK_MRS_UNAVAILABLE`.
- T5 AI reconstruction is currently unimplemented. Do not claim `./ark awaken <model>` exists.
- `PERSONAL_CONTEXT_RECONSTRUCTION != MODEL_INSTANCE_RECONSTRUCTION`.
- `MODEL_SAYS_IT_SEARCHED != SEARCH_EXECUTED`.
- Follow `ai/software-commandments.json` when implementing repository software.

## Computational archaeology status

Implemented tiers: `T0`, `T1`, `T2`, `T3`, `T4`.

Reference validation:

```sh
python3 tools/archaeology.py validate
```

## Whole-system architecture validation

```sh
python3 tools/system_architecture.py
```

The validator requires `ARCHITECTURE.txt` to remain strict 7-bit ASCII, checks the canonical role map and machine twin, pins the LATTICE profile fingerprint, and refuses to promote planned deterministic search or T5 reconstruction into implemented capability.

## Cultural recovery status

Current cultural seed:

- `culture.television.red_dwarf.ouroboros`
- `culture.television.red_dwarf.cassandra_canaries`
- `culture.meme.this_is_fine`
- `culture.qsol.open_source.permission_not_endorsement`

The Cassandra record preserves a derived cultural parallel with `ARK-CANARY.txt`; it does not claim naming provenance.

The `This Is Fine` record is the first Meme Archaeology specimen. It separates creator/source metadata, an observed hash-described crop, third-party meme transmission history, derived cultural interpretation, fictional depiction, and byte-copy rights. Every meme source now declares visibility, license state, canonical status, and byte-import permission. The supplied image bytes are not stored in the public repository.

Meme recovery tasks that encode policy-sensitive answers are record-specifically bound: a generic legal enum value is insufficient if it reverses the specimen's declared boundary.

Meme Archaeology asks whether a future model can reconstruct why a meme was intelligible to its original culture without promoting the meme, its caption, or one interpretation into factual ground truth.

Reference validation:

```sh
python3 tools/culture.py
```

Human methodology:

```text
docs/MEME-ARCHAEOLOGY.md
```

## Historical-system recovery status

PR #4 seed profiles:

- `system.commodore.c64`
- `system.commodore.amiga500`
- `system.ibm.pc_xt_5160`
- `environment.digital_research.cpm_2_2`
- `environment.unix.v7_pdp11`

Reference validation:

```sh
python3 tools/systems.py
```

The five seed profiles currently claim `historically_plausible_approximation`, not exact reproduction.

## Mutation rule

Preserve both human and machine layers. Changes to canonical semantics require synchronized machine contracts and human documentation where interpretation changes.
