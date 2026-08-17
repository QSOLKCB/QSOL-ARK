# QSOL-ARK Roadmap

QSOL-ARK is built from contracts outward: first define what survives, what is authoritative, and how a future model is allowed to know it; then add executable recovery machinery and increasingly hostile reconstruction tests.

## Phase 0 — Dual human / AI bootstrap

- [x] Human-facing project premise.
- [x] `README4AI.md` AI bootstrap entrypoint.
- [x] `AGENTS.md` machine-first agent contract.
- [x] Canonical root `manifest.json`.
- [x] Structured bootstrap, recovery, epistemic, context-source, and software-commandment contracts.
- [x] Root manifest JSON Schema.
- [x] Public-context boundary.
- [x] Apache-2.0 + CC BY 4.0 license mapping.
- [x] Architecture and recovery-protocol docs.
- [x] Ten Software Commandments in human + machine form.
- [x] Establish roadmap.

## Phase 0.5 — Computational Archaeology / Retro Recovery

Implemented early because it provides an independent portability test surface before the model harness exists.

- [x] Define T0-T5 recovery tier registry with T5 explicitly unimplemented.
- [x] Define Minimum Recoverable Substrate (MRS) selection contract.
- [x] Add T0 plain-text canary and SHA-256 receipt.
- [x] Add T1 POSIX-compatible shell verifier with explicit hash-provider requirement.
- [x] Add T2 standalone C99 SHA-256 verifier with ISO C library only.
- [x] Add T3 single-file offline browser verifier with no server/CDN/framework.
- [x] Add T4 Python stdlib archaeology validator and MRS selector.
- [x] Add unit tests for MRS selection and fail-closed unimplemented tiers.
- [x] Add CI for Python, POSIX, C99, canary receipt, and SHA-256 standard vector.
- [x] Pin RETRO-OSS source commit/blob identities as a provenance specimen.
- [x] Refuse RETRO-OSS byte import while source license evidence is unresolved.
- [x] Add metadata-only security-flavoured epistemic trap from RETRO-OSS.
- [ ] Test additional old/limited C compilers and libc implementations.
- [ ] Add an actually constrained emulator/hardware target after the portable contracts stabilize.
- [ ] Add printable/QR/audio recovery experiments without weakening canonical provenance.

## Phase 1 — Public context capsule

- [ ] Define explicit allow-list public export format.
- [ ] Add deterministic public export from QSOL-CONTEXT without private/excluded material.
- [ ] Add canonical QSOL terminology and alias capsule.
- [ ] Add compact public project registry.
- [ ] Add publication / DOI records required by selected specimens.
- [ ] Add provenance receipts for imported context records.
- [ ] Record repository, ref/tag, commit, path, and hash for source snapshots.
- [ ] Fail closed on unknown visibility/provenance.
- [ ] Import QSOL-SUBSTRATE as explicit canonical public slices, never recursive copies.

## Phase 2 — Canonicalisation, receipts, fingerprinting

- [ ] Implement deterministic canonical JSON serialization.
- [ ] Select a fully specified cross-runtime canonicalizer where practical.
- [ ] Implement repository/capsule fingerprinting.
- [ ] Add SHA-256 receipt generation and verification beyond the minimal archaeology canary.
- [ ] Exclude timestamps, locale, randomness, network state, and filesystem ordering from canonical bytes unless source data requires them.
- [ ] Add `ark verify` for manifests, schemas, receipts, and licenses.
- [ ] Add corruption/tamper tests.

## Phase 3 — Recovery specimen pack v1

- [ ] Identity/context specimen.
- [ ] Terminology/alias specimen.
- [ ] Deterministic text transformation.
- [ ] Deterministic scientific/simulation specimen.
- [ ] Deterministic WAV/sonification specimen.
- [ ] Tiny deterministic browser game.
- [ ] Mathematical/formal specimen.
- [ ] Provenance-chain specimen.
- [x] Initial clearly labelled epistemic/satire-style trap metadata from RETRO-OSS.
- [ ] One reconstructable missing artifact.
- [ ] One intentionally unrecoverable specimen where `insufficient evidence` is correct.

## Phase 4 — `ark awaken` cold-start harness

```sh
./ark awaken <model>
```

- [ ] Model-adapter interface.
- [ ] Ollama adapter first.
- [ ] Generic stdin/stdout adapter.
- [ ] Stage context rather than dumping the archive.
- [ ] Record exact prompts, inputs, model identifiers, parameters, and responses.
- [ ] Separate harness evidence from model self-report.
- [ ] Deterministic replay of non-model orchestration.
- [ ] Machine-readable recovery transcript.

## Phase 5 — Epistemic adversarial suite

- [ ] Mix supported and unsupported claims.
- [ ] Plant recoverable contradictions.
- [ ] Test `ADJACENT_TRUTH != INHERITED_TRUTH`.
- [ ] Test `UNAVAILABLE`, `UNVERIFIED`, and `CONTRADICTED` distinctly.
- [ ] Test owner assertions without upgrading them to independent verification.
- [ ] Test primary source vs summary vs generated commentary.
- [x] Add first metadata-only satire/security-language isolation trap.
- [ ] Test stale cached context against newer repository state.
- [ ] Test ambiguous aliases with fail-closed behavior.
- [ ] Measure hallucinated-history rate.

## Phase 6 — Recovery scoring and evidence report

- [ ] Freeze scoring dimensions before tuning against results.
- [ ] Identity reconstruction.
- [ ] Terminology reconstruction.
- [ ] Provenance discipline.
- [ ] Epistemic classification.
- [ ] Deterministic reproduction.
- [ ] Contradiction detection.
- [ ] Satire/fiction isolation.
- [ ] Cross-domain contamination.
- [ ] Hallucinated-history rate.
- [ ] Human + canonical machine reports.
- [ ] Every score traceable to evidence.

## Phase 7 — Deterministic score sonification

Because apparently a numeric report is not enough.

- [ ] Deterministic mapping from recovery dimensions to musical parameters.
- [ ] Canonical PCM WAV without generative services.
- [ ] Record sample rate, bit depth, mapping, seeds if any, and hash.
- [ ] Identical canonical report bytes must produce identical canonical WAV bytes under the declared runtime.
- [ ] Keep artistic renders separate from canonical reference sonification.

## Phase 8 — Portability / hostile environment

- [x] Initial POSIX shell recovery surface (T1).
- [x] Initial Python reference recovery surface (T4).
- [x] Initial browser-only offline verifier (T3).
- [x] Minimal-dependency standalone C99 verifier (T2).
- [ ] Single-file full capsule export.
- [ ] Full air-gapped ARK workflow beyond the minimal canary.
- [ ] Linux/common CPU architecture tests.
- [ ] Document cross-platform limits from real runs.

## Phase 9 — Cross-model civilisation recovery matrix

- [ ] Run multiple open-weight families through identical examination versions.
- [ ] Pin prompts, adapters, temperatures, seeds where supported, context limits, and model hashes.
- [ ] Separate deterministic harness behavior from stochastic model behavior.
- [ ] Compare small vs large models.
- [ ] Compare tool vs no-tool runs.
- [ ] Publish scorecards as derived evaluation artifacts.
- [ ] Never let a leaderboard become canonical source.

## Phase 10 — Archival release

- [ ] Freeze ARK protocol v1.0.0.
- [ ] Produce self-contained release capsule.
- [ ] Generate full SHA-256 manifests.
- [ ] Verify clean-room recovery from release artifact.
- [ ] Archive source, spec, receipts, and selected deterministic outputs.
- [ ] Mint DOI if stable enough to cite.
- [ ] Record exact tag, commit, release artifact, and checksum.

## Deferred / experimental

- QR-sized / printable micro-capsules.
- Audio-only recovery representation.
- Error-correcting archival media.
- Ada / Fortran / COBOL independent implementations.
- Lean 4 formalisation of selected invariants.
- Vector indexes / embedding projections.
- Soft prompts, latent projections, KV-cache projections.
- Offline authenticity experiments.
- Distributed multi-model courtroom adjudication.
- QSOL-BABEL cross-language canonical-hash convergence.
- Long-horizon unknown-future-model challenge releases.

## Definition of success

ARK succeeds when a model with **no privileged prior context** can reconstruct the intended knowledge boundary from the archive, reproduce what is reproducible, refuse what is unsupported, expose uncertainty cleanly, and leave an auditable receipt.

If it merely tells a convincing story, it has failed.
