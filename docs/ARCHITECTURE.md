# QSOL-ARK Architecture

QSOL-ARK is a **source-first recovery system**. Humans should be able to inspect it, but future models should not need to reverse-engineer its epistemology from prose.

## Two readable layers, one authority chain

The human layer (`README.md`, `ROADMAP.md`, `docs/`) explains intent and trade-offs. The AI/machine layer (`README4AI.md`, `AGENTS.md`, `manifest.json`, `ai/`, `schema/`) defines load order, source authority, visibility constraints, epistemic labels, and machine-verifiable structure.

Structured canonical contracts win if prose and machine metadata accidentally diverge.

## Canonical source vs projection

Canonical source includes repository source, explicit public context records, specimen inputs, deterministic recipes, manifests, schemas, and receipts.

Derived projections include summaries, embeddings/vector indexes, adapters, scorecards, report sonifications, UI views, soft prompts, and model-specific latent/KV representations.

A projection can be useful without becoming truth.

## Context boundary

ARK is public. QSOL-CONTEXT may inform **what** is selected and how provenance/determinism are represented, but it must never be recursively copied. Every imported record needs an explicit public-export decision and provenance.

QSOL-SUBSTRATE may provide public canonical substrate payloads. ARK records the exact imported slice and source identity rather than assuming an external repository is frozen forever.

## Authority order

1. live repository state for live software claims;
2. ARK canonical payload and receipts;
3. explicit public exports/import snapshots;
4. derived artifacts.

Authority is claim-specific.

## Fail closed

Fail closed on missing provenance, unknown visibility, ambiguous aliases, unclear canonical status, insufficient deterministic inputs, unavailable required evidence, or license ambiguity.

A correct `insufficient evidence` is successful recovery behavior.

## Determinism boundary

Harness orchestration, canonicalization, receipts, specimen generators, and report serialization may be deterministic while the evaluated model remains stochastic. Never conflate the two.

## Software constitution

Implementation is governed by the Ten Software Commandments in `docs/SOFTWARE-COMMANDMENTS.md` and `ai/software-commandments.json`: minimal machinery, explicit state, provenance, inspectability, useful failure, and no mystical determinism.
