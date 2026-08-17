# QSOL-ARK

**An AI civilisation recovery kit and deterministic reconstruction benchmark.**

> Assume the current AI ecosystem disappears tomorrow. Can an unknown future model reconstruct enough context, terminology, provenance, tests, software, and demonstrations to understand what the hell we were doing?

QSOL-ARK is a public, vendor-neutral recovery archive and benchmark. It asks whether knowledge can survive the model, vendor, runtime, and interface that originally created or consumed it.

**Maintainer:** Trent Slade (`EmergentMonk`), QSOL-IMC founder and maintainer. This identity is also declared canonically in `manifest.json` so cold-start recovery does not depend on repository-owner inference or undocumented model memory.

The repository exposes two synchronized layers:

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

## Computational Archaeology

PR #2 adds the first executable recovery paths.

> **How far can the computational environment collapse before ARK stops being independently verifiable?**

| Tier | Environment | Status |
|---|---|---|
| T0 | plain text / printable bytes | implemented |
| T1 | POSIX-compatible shell + SHA-256 provider | implemented |
| T2 | standalone C99 + ISO C library | implemented |
| T3 | single-file offline browser + Web Crypto | implemented |
| T4 | Python standard library reference validator | implemented |
| T5 | staged AI reconstruction | planned |

The canonical registry is `ai/recovery-tiers.json`. The **Minimum Recoverable Substrate (MRS)** contract in `ai/minimum-recoverable-substrate.json` selects the lowest-rank implemented tier whose explicitly declared capabilities satisfy a request.

The minimal canary is:

```text
capsules/minimal/ARK-CANARY.txt
SHA-256 df2d7ed3696dda919d2b8a3356eeb5a8473f1cc3bb05fd30b9f7281e6bb08cab
```

Quick checks:

```sh
python3 tools/archaeology.py validate
sh retro/posix/ark-verify.sh

cc -std=c99 -O2 -Wall -Wextra -pedantic retro/c/ark-verify.c -o /tmp/ark-verify
expected=$(awk '$2 == "ARK-CANARY.txt" { print $1; exit }' capsules/minimal/SHA256SUMS)
/tmp/ark-verify capsules/minimal/ARK-CANARY.txt "$expected"
```

See [`docs/COMPUTATIONAL-ARCHAEOLOGY.md`](docs/COMPUTATIONAL-ARCHAEOLOGY.md).

## Meme Archaeology

Memes are treated as **compressed cultural artifacts**, not as disposable images.

A future model may be able to read every pixel and still miss the culture that made the image intelligible. ARK therefore separates:

- creator/source-work evidence;
- an observed meme variant;
- transmission history;
- cultural interpretation;
- rights and epistemic boundaries;
- recovery questions testing whether those layers remain distinct.

The first seed is `culture.meme.this_is_fine`. The source work is KC Green's *Gunshow* comic **On Fire**. The maintainer-supplied two-panel WebP crop is hash-described but not copied into the repository because ARK does not infer redistribution permission from ubiquity, a public URL, or a known hash.

Know Your Meme is used as a provenance-labelled third-party history/reference source for meme spread and usage, while creator-controlled Gunshow pages remain the stronger source for creator and original-publication metadata.

The recovery boundary is deliberately blunt:

```text
MEME != DECORATIVE_IMAGE
CAPTION != CONTEXT
DEPICTION != HISTORICAL_EVENT
MEME_HISTORY_REFERENCE != CREATOR_SOURCE
DERIVED_INTERPRETATION != UNIVERSAL_MEANING
KNOWN_HASH != BYTE_COPY_PERMISSION
POPULARITY != TRUTH
```

The next obvious specimen is **BTW, I Use Arch**: very little literal text, but a dense packet of Linux culture, technical identity signalling, perceived elitism, self-parody, and community history.

See [`docs/MEME-ARCHAEOLOGY.md`](docs/MEME-ARCHAEOLOGY.md).

## RETRO-OSS archaeological source

`QSOLKCB/RETRO-OSS` is used as a pinned provenance and epistemic specimen, **not copied as trusted source**.

At the pinned commit, its README names `LICENSE` as a standard meta file, while the observed root snapshot contains no `LICENSE` entry. ARK therefore records the license evidence as unresolved and sets `byte_import_allowed=false`.

The deliberately unserious security-flavoured `lambroast.py` is referenced by metadata and paraphrase as an epistemic trap: a recovery model should recognize that simulated quantum measurement, Python `hash()`, XOR, and parity are not evidence of quantum-secure authentication.

See `specimens/retro-oss/` and `specimens/epistemic-traps/`.

## Repository layers

| Layer | Entrypoint | Purpose |
|---|---|---|
| Human | `README.md` | concept, orientation, status, licensing |
| AI | `README4AI.md` | compact model bootstrap |
| Agent | `AGENTS.md` | coding/recovery operating contract |
| Canonical | `manifest.json`, `ai/*.json` | structured authority and policy |
| Schema | `schema/` | machine validation |
| Protocol | `docs/RECOVERY-PROTOCOL.md` | staged examination |
| Archaeology | `docs/COMPUTATIONAL-ARCHAEOLOGY.md` | constrained-environment recovery |
| Meme archaeology | `docs/MEME-ARCHAEOLOGY.md` | cultural-context and transmission recovery |
| Constitution | `docs/SOFTWARE-COMMANDMENTS.md` | Ten Software Commandments |
| Roadmap | `ROADMAP.md` | implementation sequence |

## Public context boundary

QSOL-ARK is **public by construction**.

- Live QSOL-ARK repository state is authoritative for ARK software and contracts.
- Public QSOL-SUBSTRATE payloads may be imported only as explicit provenance-tracked slices.
- QSOL-CONTEXT may inform selection, provenance, and deterministic metadata discipline, but must never be recursively copied or treated as automatically public.
- QSOL-CONTEXT records require explicit public-export clearance evidence; `visibility: public` alone is not sufficient authorization.
- Third-party source bytes require resolved license evidence; ambiguity fails closed.
- Derived bundles, embeddings, adapters, summaries, scorecards, sonifications, and model-specific projections are not canonical unless an explicit contract says otherwise.

## The Ten Software Commandments

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

## Planned model command

```sh
./ark awaken <model>
```

This remains a **planned interface**, not yet implemented.

## Status

**Phase 0 complete. Computational Archaeology T0-T4 is implemented early as an independent portability track.** Public context capsules, canonical receipts, the broader specimen pack, and the staged model harness remain on the roadmap.

See [`ROADMAP.md`](ROADMAP.md).

## Licensing

QSOL-ARK uses a dual-license structure:

- **Software, scripts, executable tooling, tests, and code:** Apache License 2.0.
- **Original documentation, benchmark specifications, schemas, manifests, substrate records, and original datasets:** Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Third-party material:** retains its original copyright and license and must be identified explicitly.

See [`LICENSES/README.md`](LICENSES/README.md). The root [`LICENSE`](LICENSE) contains Apache-2.0.

---

**QSOL-ARK asks one slightly alarming question: _can knowledge survive the model that created it?_**
