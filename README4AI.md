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
- bootstrap_contract: `ai/bootstrap.json`
- recovery_tier_registry: `ai/recovery-tiers.json`
- mrs_contract: `ai/minimum-recoverable-substrate.json`
- cultural_policy: `ai/cultural-artifact-policy.json`
- culture_index: `culture/index.json`
- meme_archaeology: `docs/MEME-ARCHAEOLOGY.md`
- historical_system_policy: `ai/historical-system-policy.json`
- historical_system_index: `systems/index.json`

## Required load order

1. `manifest.json`
2. `ai/bootstrap.json`
3. `ai/recovery-contract.json`
4. `ai/epistemic-policy.json`
5. `ai/context-sources.json`
6. `ai/software-commandments.json`
7. `ai/recovery-tiers.json`
8. `ai/minimum-recoverable-substrate.json`
9. `ai/cultural-artifact-policy.json`
10. `culture/index.json`
11. `ai/historical-system-policy.json`
12. `systems/index.json`
13. relevant schemas
14. task-selected specimen manifests, historical-system profiles, and receipts only

Do not recursively ingest the repository unless a recovery stage explicitly requires it.

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
- `MEME != DECORATIVE_IMAGE`.
- `CAPTION != CONTEXT`.
- `DEPICTION != HISTORICAL_EVENT`.
- `MEME_HISTORY_REFERENCE != CREATOR_SOURCE`.
- `DERIVED_INTERPRETATION != UNIVERSAL_MEANING`.
- `KNOWN_HASH != BYTE_COPY_PERMISSION`.
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
- Follow `ai/software-commandments.json` when implementing repository software.

## Computational archaeology status

Implemented tiers: `T0`, `T1`, `T2`, `T3`, `T4`.

Reference validation:

```sh
python3 tools/archaeology.py validate
```

## Cultural recovery status

Current cultural seed:

- `culture.television.red_dwarf.ouroboros`
- `culture.television.red_dwarf.cassandra_canaries`
- `culture.meme.this_is_fine`
- `culture.qsol.open_source.permission_not_endorsement`

The Cassandra record preserves a derived cultural parallel with `ARK-CANARY.txt`; it does not claim naming provenance.

The `This Is Fine` record is the first Meme Archaeology specimen. It separates creator/source metadata, an observed hash-described crop, third-party meme transmission history, derived cultural interpretation, fictional depiction, and byte-copy rights. The supplied image bytes are not stored in the public repository.

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
