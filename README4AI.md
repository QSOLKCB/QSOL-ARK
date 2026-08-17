# QSOL-ARK — AI BOOTSTRAP

MACHINE-FIRST ENTRYPOINT.

## Identity

- protocol: `QSOL-ARK`
- purpose: public vendor-neutral AI civilisation recovery archive and deterministic reconstruction benchmark
- repository: `QSOLKCB/QSOL-ARK`
- human_entrypoint: `README.md`
- canonical_manifest: `manifest.json`
- agent_contract: `AGENTS.md`
- bootstrap_contract: `ai/bootstrap.json`

## Required load order

1. `manifest.json`
2. `ai/bootstrap.json`
3. `ai/recovery-contract.json`
4. `ai/epistemic-policy.json`
5. `ai/context-sources.json`
6. `ai/software-commandments.json`
7. `schema/ark-manifest.schema.json`
8. task-selected specimen manifests and receipts only

Do not recursively ingest the repository unless a recovery stage explicitly requires it.

## Hard rules

- Live repository state is authoritative for live repository software state.
- Do not invent missing fields, chronology, provenance, releases, identities, or citations.
- Distinguish observation, repository evidence, primary source, owner assertion, inference, theory, preprint, satire, fiction, contradiction, and unknown.
- `ADJACENT_TRUTH != INHERITED_TRUTH`.
- `UNAVAILABLE != UNVERIFIED != CONTRADICTED`.
- Derived artifacts are not canonical merely because they are useful.
- Model summaries and model self-reports are not primary verification.
- Satire and fiction may be benchmark specimens but never factual evidence.
- Ambiguous provenance, visibility, alias resolution, or canonical status fails closed.
- QSOL-CONTEXT is not automatically public source material; only explicit public exports may be imported.
- QSOL-SUBSTRATE is authoritative only for an explicitly imported published public payload.
- Verify hashes before trusting deterministic claims when receipts exist.
- Prefer the smallest sufficient context slice.
- Follow `ai/software-commandments.json` when implementing repository software.

## Recovery objective

A cold-start model should identify the archive, resolve terminology, rank source authority, classify claims, reproduce deterministic specimens, detect contradictions, reconstruct declared missing outputs when possible, refuse unsupported reconstruction, and emit an auditable machine-readable report.

## Planned interface

`./ark awaken <model>`

Do not claim this exists until executable repository state proves it.

## Mutation rule

Preserve both human and machine layers. Changes to canonical semantics require synchronized machine contracts and human documentation where interpretation changes.
