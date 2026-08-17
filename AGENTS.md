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
10. `ai/cultural-artifact-policy.json`
11. `culture/index.json`
12. `ai/historical-system-policy.json`
13. `systems/index.json`
14. task-specific canonical specimen or recovery-task manifest
15. human documentation
16. derived artifacts

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
- PROMOTE_FICTION_TO_HISTORY=false
- FIRST_PERSON_POSITION_IS_NOT_OBJECTIVE_EXTERNAL_FACT=true
- PERMISSION_IS_NOT_ENDORSEMENT=true
- PERSONAL_DISLIKE_DOES_NOT_SILENTLY_REWRITE_LICENSE=true
- PUBLIC_URL_IS_NOT_COPY_PERMISSION=true
- HASH_VERIFICATION_REQUIRED_WHEN_RECEIPT_EXISTS=true
- MEME_ARCHAEOLOGY_POLICY=ai/cultural-artifact-policy.json#meme_archaeology
- MEME_SOURCE_EVIDENCE_REQUIRED=true
- MEME_TASK_SEMANTIC_BINDING_REQUIRED=true
- MRS_CAPABILITIES_EXPLICIT_ONLY=true
- MRS_UNAVAILABLE=FAIL_CLOSED
- AMBIENT_TIME_IN_CANONICAL_OUTPUT=false
- AMBIENT_RANDOMNESS_IN_CANONICAL_OUTPUT=false
- EMULATOR_BEHAVIOUR_IS_NOT_ORIGINAL_HARDWARE_FACT=true
- COMPATIBILITY_LAYER_BEHAVIOUR_IS_NOT_ORIGINAL_SOFTWARE_BEHAVIOUR=true
- SOFTWARE_ENVIRONMENT_IS_NOT_ONE_CANONICAL_MACHINE=true
- HOST_RECOVERY_TIER_IS_NOT_NATIVE_HISTORICAL_EXECUTION=true

## CODEX-DERIVED ARCHAEOLOGICAL INVARIANTS

These rules were promoted from concrete validator failures into recovery doctrine:

```text
RECEIPT_PRESENT != PAYLOAD_VERIFIED
STRUCTURED_BOUNDARY != PROSE_BOUNDARY
MAINTAINER_SUPPLIED != NEW_EVIDENCE_CLASS
SOURCE_PRESENT != EVIDENCE_COMPLETE
ENUM_VALID != SEMANTICALLY_BOUND
```

Interpretation:

1. a receipt is evidence to test, not a substitute for hashing the referenced payload bytes;
2. canonical prose must not contradict the machine fields that constrain the same claim;
3. who supplied a source is provenance metadata, not permission to invent a new epistemic class;
4. a source record is incomplete until visibility, license state, canonical/derived status, and byte-import permission are explicit where the governing policy requires them;
5. an answer that belongs to a legal enum is not necessarily the correct answer for a specific benchmark question: task semantics must be bound to the record they test.

A future recovery system that finds a label reading `AUTHENTIC RELIC` must still inspect the relic.

## REVIEW-DERIVED IMPLEMENTATION CONSTRAINTS

Useful review pressure also produced these implementation rules:

```text
FAIL_CLOSED != FREEZE_SCHEMA_FOREVER
CANONICAL_INVARIANT != COPY_PASTED_INVARIANT
POLICY_STRING_BAG != VERSIONED_POLICY
```

Interpretation:

1. fail closed on missing required evidence, but allow explicitly non-normative inner metadata to evolve without rewriting a validator for every harmless annotation;
2. canonical invariant lists have one machine-readable source of truth and other documents point to it instead of copying it;
3. subsystem rules that are expected to grow belong in a structured, versioned policy section rather than an ever-growing flat list of magic strings.

## SOFTWARE CONSTITUTION

`ai/software-commandments.json` is normative for repository implementation style unless a documented technical requirement requires an exception.

## RECOVERY TIER RULES

1. declare environment assumptions explicitly;
2. declare capabilities explicitly;
3. never inherit a capability merely because another tier has it;
4. mark planned tiers `implemented=false`;
5. MRS selects only implemented tiers;
6. keep offline surfaces free of hidden network dependencies;
7. when a receipt exists, hash the referenced payload bytes and compare the computed digest with the bound receipt rather than trusting receipt text or prose;
8. historical-system validation exists only because T4 explicitly declares `validate_historical_system_contracts` and `tools/systems.py`.

## CULTURAL RECORD RULES

1. distinguish executable artifacts, cultural artifacts, historical claims, fictional-world claims, authored positions, and derived interpretations;
2. preserve real production history separately from narrative fiction;
3. treat a direct maintainer statement as evidence of the maintainer's stated position, not independent evidence about named third parties;
4. do not infer endorsement from permission, interoperability, compatibility, or product preference;
5. do not alter applicable licence permissions based on personal approval or dislike;
6. do not copy third-party scripts, transcripts, audiovisual media, ROMs, meme images, or other source bytes without resolved rights;
7. unavailable third-party reference material is unavailable, not contradicted;
8. add reconstruction tasks that test cultural meaning and evidence boundaries;
9. bind canonical prose that expresses an epistemic boundary so prose cannot silently contradict the structured claim;
10. record `provided_by` separately from the source's declared evidence class; maintainer supply does not create a new evidence class.

## MEME ARCHAEOLOGY RULES

The canonical, versioned Meme Archaeology invariant list lives only at:

```text
ai/cultural-artifact-policy.json#meme_archaeology.canonical_invariants
```

Do not duplicate that list in documentation or bootstrap surfaces.

1. preserve creator/source-work metadata separately from meme transmission history;
2. prefer creator-controlled or official sources for creator and source-work claims when available;
3. treat meme-history databases as provenance-labelled third-party history/reference sources unless stronger authority is independently established;
4. every meme source must declare the evidence fields required by `meme_archaeology.source_evidence`;
5. an observed variant may be hash-described without being stored when third-party byte-copy rights are unresolved;
6. an observed variant hash identifies bytes only; it does not establish canonical-master status or redistribution permission;
7. preserve visual summaries and cultural interpretations as bounded derived context, not universal meaning;
8. a caption must be interpreted with visual and cultural context rather than promoted to standalone ground truth;
9. fictional or illustrative scenes remain fictional/illustrative and do not become historical events because the meme was culturally important;
10. record-specific recovery tasks must bind question IDs, prompts, and expected answers when changing them could reverse the governing policy;
11. future meme specimens should reuse the same source / observed-variant / transmission-history / interpretation / rights separation where applicable.

See `docs/MEME-ARCHAEOLOGY.md`.

## HISTORICAL SYSTEM RULES

1. historical profiles are strict machine records; undeclared fields fail closed;
2. distinguish `hardware_fact`, `documented_software_behaviour`, `emulator_behaviour`, `compatibility_layer_behaviour`, `reconstruction_inference`, and `unknown`;
3. do not promote emulator output to original hardware history;
4. do not promote compatibility-layer behaviour to original software behaviour;
5. do not rewrite CP/M, UNIX, or another multi-hardware software environment as one canonical physical machine;
6. source-evidence records must declare public visibility, license status, epistemic class, canonical/derived status, and byte-import permission;
7. unresolved third-party rights permit citation, metadata, observation, and paraphrase only; source-byte import remains forbidden;
8. exact reproduction requires sufficient public, licensed, inspectable evidence;
9. Computational Archaeology tiers describe ARK recovery hosts, not native execution on the historical machine;
10. recovery-task prompts must remain executable non-empty text, not arbitrary structured payloads.

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
- treating a public URL as copyright permission;
- treating repository prose as license evidence when the declared license artifact is absent;
- treating a receipt line as proof without hashing the referenced payload;
- allowing canonical prose to contradict its structured epistemic boundary;
- inventing an evidence class from source-provider metadata;
- accepting a meme source whose required visibility, license, canonical status, or byte-import state is absent;
- accepting a record-specific benchmark answer merely because the answer belongs to a generic enum;
- treating a meme-history database as automatic creator authority;
- treating a familiar meme image as public-domain or freely redistributable merely because it is ubiquitous;
- treating a meme caption as literal factual ground truth while ignoring the image;
- treating one common meme interpretation as universal meaning;
- treating fictional narrative as historical evidence;
- treating opinion about a named person/company as verified objective fact;
- treating permission to fork or reuse as endorsement;
- generated embeddings, latent projections, or KV caches as sole canonical source;
- claiming cross-runtime byte identity without a declared canonicalizer;
- accepting persuasive prose as deterministic reproduction;
- inventing a recovery capability because a compatible runtime happens to exist;
- hiding third-party payloads under renamed or nested undeclared fields.

END CONTRACT.
