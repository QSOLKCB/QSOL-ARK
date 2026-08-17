# QSOL-ARK AGENT CONTRACT

MACHINE-FIRST OPERATING CONTRACT.

## PRIORITY

1. live repository state
2. `manifest.json`
3. `ai/bootstrap.json`
4. `ai/recovery-contract.json`
5. `ai/epistemic-policy.json`
6. `ai/context-sources.json`
7. `ai/software-commandments.json`
8. task-specific canonical specimen manifest
9. human documentation
10. derived artifacts

## NON-NEGOTIABLE RULES

- PUBLIC_REPOSITORY=true
- IMPORT_PRIVATE_CONTEXT=false
- EXPLICIT_PUBLIC_EXPORT_REQUIRED=true
- UNKNOWN_VISIBILITY=FAIL_CLOSED
- UNKNOWN_PROVENANCE=FAIL_CLOSED
- AMBIGUOUS_CANONICAL_STATUS=FAIL_CLOSED
- INVENT_MISSING_HISTORY=false
- INVENT_CITATIONS=false
- PROMOTE_DERIVED_TO_CANONICAL=false
- PROMOTE_SATIRE_TO_FACT=false
- REPOSITORY_STATE_OVERRIDES_CACHED_SOFTWARE_CONTEXT=true
- HASH_VERIFICATION_REQUIRED_WHEN_RECEIPT_EXISTS=true
- AMBIENT_TIME_IN_CANONICAL_OUTPUT=false
- AMBIENT_RANDOMNESS_IN_CANONICAL_OUTPUT=false

## SOFTWARE CONSTITUTION

`ai/software-commandments.json` is normative for repository implementation style unless a documented technical requirement requires an exception. Exceptions must be explicit and reviewable.

## ADDING A RECOVERY SPECIMEN

1. add/update its machine-readable manifest;
2. declare source provenance and license;
3. declare epistemic class;
4. declare deterministic recipe when determinism is claimed;
5. declare expected hashes when stable outputs exist;
6. separate canonical source from derived projections;
7. add validation;
8. update human documentation where meaning changes;
9. never copy QSOL-CONTEXT material unless specifically cleared for public export.

## PROHIBITED SHORTCUTS

- undocumented model memory as evidence;
- hidden prompts as canonical meaning;
- model self-report as verification;
- secrets, credentials, or private context;
- generated embeddings, latent projections, or KV caches as sole canonical source;
- claiming cross-runtime byte identity without a declared canonicalizer;
- accepting persuasive prose as deterministic reproduction.

END CONTRACT.
