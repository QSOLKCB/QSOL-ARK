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

## Required load order

1. `manifest.json`
2. `ai/bootstrap.json`
3. `ai/recovery-contract.json`
4. `ai/epistemic-policy.json`
5. `ai/context-sources.json`
6. `ai/software-commandments.json`
7. `ai/recovery-tiers.json`
8. `ai/minimum-recoverable-substrate.json`
9. relevant schemas
10. task-selected specimen manifests and receipts only

Do not recursively ingest the repository unless a recovery stage explicitly requires it.

## Hard rules

- Live repository state is authoritative for live repository software state.
- Do not invent missing fields, chronology, provenance, releases, identities, citations, capabilities, or license evidence.
- `ADJACENT_TRUTH != INHERITED_TRUTH`.
- `UNAVAILABLE != UNVERIFIED != CONTRADICTED`.
- Derived artifacts are not canonical merely because they are useful.
- Satire and fiction may be benchmark specimens but never factual evidence.
- Ambiguous provenance, visibility, alias resolution, canonical status, or license evidence fails closed.
- QSOL-CONTEXT imports require explicit public-export clearance evidence; `visibility: public` alone is insufficient.
- Third-party source bytes require resolved license evidence. Metadata, hashes, observations, and paraphrase do not imply byte-copy permission.
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

## Mutation rule

Preserve both human and machine layers. Changes to canonical semantics require synchronized machine contracts and human documentation where interpretation changes.
