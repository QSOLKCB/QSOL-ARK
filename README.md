# QSOL-ARK

**An AI civilisation recovery kit and deterministic reconstruction benchmark.**

> Assume the current AI ecosystem disappears tomorrow. Can an unknown future model reconstruct enough context, terminology, provenance, tests, software, and demonstrations to understand what the hell we were doing?

QSOL-ARK is a public, vendor-neutral recovery archive and benchmark. It asks whether knowledge can survive the model, vendor, runtime, and interface that originally created or consumed it.

**Maintainer:** Trent Slade (`EmergentMonk`), QSOL-IMC founder and maintainer. This identity is also declared canonically in `manifest.json` so cold-start recovery does not depend on repository-owner inference or undocumented model memory.

The repository deliberately exposes two synchronized layers:

- **Human layer:** `README.md`, `ROADMAP.md`, `docs/`
- **AI/machine layer:** `README4AI.md`, `AGENTS.md`, `manifest.json`, `ai/`, `schema/`

## Core recovery test

A cold-start model should be able to determine from evidence:

1. what QSOL-ARK is and who maintains it;
2. which terminology is canonical;
3. which claims are verified, inferred, theoretical, satirical, fictional, contradicted, or unknown;
4. which artifacts are canonical and which are derived;
5. which sources are authoritative for each claim;
6. whether deterministic artifacts reproduce byte-for-byte;
7. whether planted contradictions and unsupported claims are detected;
8. whether a missing artifact can be reconstructed from its recipe;
9. when the correct answer is **insufficient evidence**; and
10. whether the result survives transfer across models and runtimes.

## Repository layers

| Layer | Entrypoint | Purpose |
|---|---|---|
| Human | `README.md` | concept, orientation, status, licensing |
| AI | `README4AI.md` | compact model bootstrap |
| Agent | `AGENTS.md` | coding/recovery operating contract |
| Canonical | `manifest.json`, `ai/*.json` | structured authority and policy |
| Schema | `schema/` | machine validation |
| Protocol | `docs/RECOVERY-PROTOCOL.md` | staged examination |
| Constitution | `docs/SOFTWARE-COMMANDMENTS.md` | the Ten Software Commandments |
| Roadmap | `ROADMAP.md` | implementation sequence |

## Public context boundary

QSOL-ARK is **public by construction**.

- Live QSOL-ARK repository state is authoritative for ARK software and contracts.
- Public QSOL-SUBSTRATE payloads may be imported only as explicit provenance-tracked slices.
- QSOL-CONTEXT may inform selection, provenance, and deterministic metadata discipline, but **must never be recursively copied or treated as automatically public**.
- QSOL-CONTEXT records require explicit public-export clearance evidence; `visibility: public` alone is not sufficient authorization for ARK import.
- Only material explicitly cleared for public export may enter an ARK capsule.
- Repository software state overrides cached context about that software.
- Derived bundles, embeddings, adapters, summaries, scorecards, sonifications, and model-specific projections are not canonical unless an explicit contract says otherwise.
- Ambiguous visibility, provenance, or canonical status fails closed.

## The Ten Software Commandments

ARK has rules. Naturally, they are engraved on digital stone tablets.

1. **Thou shalt not write bloat.**
2. **Thou shalt not hide state.**
3. **Thou shalt not confuse derived artifacts with canonical source.**
4. **Thou shalt not summon a dependency for what ten clear lines can do.**
5. **Thou shalt make failure loud, typed, and useful.**
6. **Thou shalt make determinism explicit, not mystical.**
7. **Thou shalt preserve provenance.**
8. **Thou shalt not make the network a requirement without necessity.**
9. **Thou shalt make the machine-readable truth inspectable by humans.**
10. **Thou shalt leave the repository simpler than thou found it.**

The normative versions live in `docs/SOFTWARE-COMMANDMENTS.md` and `ai/software-commandments.json`.

## Planned command

```sh
./ark awaken <model>
```

This is a **planned interface**, not yet implemented. It will stage a cold-start recovery examination, capture evidence, score the run, and emit deterministic reports.

A future report might look like:

```text
QSOL-ARK RECOVERY REPORT

Identity reconstruction       100%
Terminology reconstruction     97%
Provenance discipline         100%
Epistemic classification       94%
Deterministic reproduction    100%
Cross-domain contamination      0%
Hallucinated history            0%
Satire detection               88%

CIVILISATION RECOVERY SCORE: 96.9%

STATUS:
Humanity may be rebooted.
```

And yes: a later phase deterministically sonifies the score.

## Status

**Phase 0 — bootstrap.** The contracts come first. Executable recovery tooling and specimen packs come next.

See [`ROADMAP.md`](ROADMAP.md).

## Licensing

QSOL-ARK uses a dual-license structure:

- **Software, scripts, executable tooling, tests, and code:** Apache License 2.0.
- **Original documentation, benchmark specifications, schemas, manifests, substrate records, and original datasets:** Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Third-party material:** retains its original copyright and license and must be identified explicitly.

See [`LICENSES/README.md`](LICENSES/README.md). The root [`LICENSE`](LICENSE) contains Apache-2.0.

---

**QSOL-ARK asks one slightly alarming question: _can knowledge survive the model that created it?_**
