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
8. `ai/recovery-tiers.json`
9. `ai/minimum-recoverable-substrate.json`
10. task-specific canonical specimen manifest
11. human documentation
12. derived artifacts

## NON-NEGOTIABLE RULES

- PUBLIC_REPOSITORY=true
- DECLARED_MAINTAINER_REQUIRED=true
- MAINTAINER_SOURCE=manifest.json#maintainer
- IMPORT_PRIVATE_CONTEXT=false
- EXPLICIT_PUBLIC_EXPORT_REQUIRED=true
- QSOL_CONTEXT_CLEARANCE_EVIDENCE_REQUIRED=true
- THIRD_PARTY_BYTE_IMPORT_REQUIRES_RESOLVED_LICENSE=true
- UNKNOWN_VISIBILITY=FAIL_CLOSED
- UNKNOWN_PROVENANCE=FAIL_CLOSED
- UNKNOWN_LICENSE=FAIL_CLOSED
- AMBIGUOUS_CANONICAL_STATUS=FAIL_CLOSED
- INVENT_MISSING_HISTORY=false
- INVENT_CITATIONS=false
- INVENT_RECOVERY_CAPABILITIES=false
- PROMOTE_DERIVED_TO_CANONICAL=false
- PROMOTE_SATIRE_TO_FACT=false
- HASH_VERIFICATION_REQUIRED_WHEN_RECEIPT_EXISTS=true
- MRS_CAPABILITIES_EXPLICIT_ONLY=true
- MRS_UNAVAILABLE=FAIL_CLOSED
- AMBIENT_TIME_IN_CANONICAL_OUTPUT=false
- AMBIENT_RANDOMNESS_IN_CANONICAL_OUTPUT=false

## SOFTWARE CONSTITUTION

`ai/software-commandments.json` is normative for repository implementation style unless a documented technical requirement requires an exception.

## RECOVERY TIER RULES

1. declare environment assumptions explicitly;
2. declare capabilities explicitly;
3. never inherit a capability merely because another tier has it;
4. mark planned tiers `implemented=false`;
5. MRS selects only implemented tiers;
6. keep offline surfaces free of hidden network dependencies;
7. validate deterministic canaries against receipts rather than prose descriptions.

## ADDING A RECOVERY SPECIMEN

1. add/update its machine-readable manifest;
2. declare source provenance and license;
3. declare epistemic class;
4. declare deterministic recipe when determinism is claimed;
5. declare expected hashes when stable outputs exist;
6. separate canonical source from derived projections;
7. add validation;
8. update human documentation where meaning changes;
9. never copy QSOL-CONTEXT material without auditable public-export clearance;
10. never copy third-party bytes while license evidence is unresolved.

## PROHIBITED SHORTCUTS

- undocumented model memory as evidence;
- hidden prompts as canonical meaning;
- model self-report as verification;
- secrets, credentials, or private context;
- treating public visibility as export authorization;
- treating repository prose as license evidence when the declared license artifact is absent;
- generated embeddings, latent projections, or KV caches as sole canonical source;
- claiming cross-runtime byte identity without a declared canonicalizer;
- accepting persuasive prose as deterministic reproduction.

END CONTRACT.
