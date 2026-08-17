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
11. relevant schemas
12. task-selected specimen manifests and receipts only

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
- Applicable repository licence terms remain governing even when a potential user is strongly disliked.
- Ambiguous provenance, visibility, alias resolution, canonical status, or license evidence fails closed.
- QSOL-CONTEXT imports require explicit public-export clearance evidence; `visibility: public` alone is insufficient.
- Third-party source bytes require resolved license evidence. Metadata, hashes, observations, and paraphrase do not imply byte-copy permission.
- A public transcript URL does not grant ARK permission to copy the script.
- Verify hashes before trusting deterministic claims when receipts exist.
- Recovery tiers have only capabilities explicitly declared in `ai/recovery-tiers.json`.
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

Initial cultural seed:

- `culture.television.red_dwarf.ouroboros`
- `culture.qsol.open_source.permission_not_endorsement`

Reference validation:

```sh
python3 tools/culture.py
```

## Mutation rule

Preserve both human and machine layers. Changes to canonical semantics require synchronized machine contracts and human documentation where interpretation changes.
