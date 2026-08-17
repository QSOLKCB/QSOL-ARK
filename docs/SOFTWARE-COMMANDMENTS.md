# The Ten Software Commandments

QSOL-ARK's mildly sacrilegious engineering constitution.

The jokes are human-facing; the constraints are real. The normative machine representation is `ai/software-commandments.json`.

## I — Thou shalt not write bloat

Prefer the smallest clear implementation that satisfies the declared contract. Do not build an abstraction cathedral to shelter three lines of code.

## II — Thou shalt not hide state

Inputs, outputs, configuration, caches, mutable state, and side effects must be explicit enough to inspect and reproduce.

## III — Thou shalt not confuse projection with source

A summary, embedding, scorecard, sonification, adapter, or latent representation does not become canonical because it is convenient.

## IV — Thou shalt not summon a dependency for what ten clear lines can do

Dependencies are allowed when they improve correctness, security, portability, or maintainability. Dependency-count golf is also a form of stupidity.

## V — Thou shalt make failure loud, typed, and useful

Fail closed where the contract requires it. Errors should explain what failed and what evidence/input is missing. `something went wrong lol` is not an error model.

## VI — Thou shalt make determinism explicit, not mystical

State the inputs, runtime, canonicalization rules, ambient-state exclusions, and output byte scope. “It seemed deterministic on my laptop” is not a specification.

## VII — Thou shalt preserve provenance

Imported material keeps its source identity, version/ref, path/artifact identity, license, epistemic class, and canonical/derived status.

## VIII — Thou shalt not worship the network

Core verification and recovery should function offline where practical. Network requirements must be necessary, explicit, and replaceable.

## IX — Thou shalt make machine-readable truth inspectable by humans

Canonical machine contracts should remain reviewable with boring ordinary tools. No opaque latent state may be the sole source of truth.

## X — Thou shalt leave the repository simpler than thou found it

A change should reduce accidental complexity or clearly justify every new moving part it introduces.

---

### Zeroth footnote, because software engineers cannot count

Correctness, safety, provenance, and evidence outrank cleverness. The Commandments are not an excuse to hand-roll cryptography, parsers, security primitives, or anything else where a mature audited dependency is plainly safer.
