# QSOL-ARK Computational Archaeology

Computational Archaeology asks a narrower question than the future `ark awaken` model benchmark:

> **What is the weakest computational substrate that can still preserve, authenticate, or reconstruct a declared part of ARK?**

This is not retro styling. It is a portability and assumption-budget experiment.

## Recovery tiers

The canonical registry is `ai/recovery-tiers.json`.

- **T0 — stone-tablet:** plain text canary plus an external SHA-256 receipt. It preserves bytes and expected identity but performs no computation.
- **T1 — POSIX cockroach:** `sh` plus one common SHA-256 provider verifies the canary offline.
- **T2 — C99 standalone:** one C file implements SHA-256 with only the ISO C library. This removes dependence on an installed hash utility.
- **T3 — offline browser:** a single HTML file verifies edited payload text using Web Crypto without a server, framework, package manager, CDN, or network request.
- **T4 — Python reference:** standard-library validation checks tier/MRS contracts, the canary receipt, entrypoint existence, browser self-containment, and fail-closed provenance.
- **T5 — AI reconstruction:** reserved for the future staged model harness and explicitly marked unimplemented.

Tier numbers describe increasing environmental assumptions, not an automatic inheritance hierarchy. A capability exists only where the registry says it exists.

## Minimum Recoverable Substrate

The **MRS** for a requested capability set is the lowest-rank *implemented* tier whose explicitly declared capabilities contain every request.

```sh
python3 tools/archaeology.py mrs verify_sha256
python3 tools/archaeology.py mrs standalone_hash_implementation
python3 tools/archaeology.py mrs interactive_offline
```

These resolve to T1, T2, and T3 respectively. If only an unimplemented tier can satisfy a request, ARK returns `ARK_MRS_UNAVAILABLE`.

## Minimal canary

`capsules/minimal/ARK-CANARY.txt` is intentionally tiny. Its receipt is stored separately in `capsules/minimal/SHA256SUMS`. This gives every computational tier a shared byte-level specimen without pretending the canary is a complete ARK capsule.

### Cultural parallel: Red Dwarf “Cassandra”

QSOL-ARK also preserves a deliberately non-normative cultural parallel in `culture/television/red-dwarf/cassandra-canaries.json`.

The fictional Canaries in *Red Dwarf: Cassandra* and `ARK-CANARY.txt` both fit the broader canary metaphor: a small or expendable precursor is exposed to danger first so that later action can be informed by what happens to it.

This is a mnemonic and cultural interpretation, **not** historical naming evidence:

```text
CULTURAL_PARALLEL != NAMING_PROVENANCE
```

The engineering contract remains defined by ARK's machine-readable recovery tiers, canary bytes, receipt, and validators. The cultural record cannot redefine them.

## RETRO-OSS provenance exercise

RETRO-OSS inspired this portability track, but ARK does not treat inspiration as license clearance.

Pinned source snapshot:

- repository: `QSOLKCB/RETRO-OSS`
- commit: `7a70e88bb6647e35193e081ba366a69f49843bb9`
- README blob SHA-1: `fde809dec9eadf519ffa26b8010308b554bca016`
- `lambroast.py` blob SHA-1: `070b9b9ae665612b43800427d685840a857c8a6f`

The README describes `LICENSE` as part of the repository's standard meta-file structure, while the observed root listing at that commit contains no `LICENSE` entry. ARK therefore records license evidence as **unresolved** and sets `byte_import_allowed=false`.

No RETRO-OSS source code is copied into ARK by this PR. The source is represented by metadata, hashes, repository observations, and paraphrase.

## Epistemic trap

`specimens/epistemic-traps/retro-oss-quantum-meme-security.json` references `lambroast.py` without copying it. A model should not promote simulated quantum measurement, Python `hash()`, XOR, and parity into a real authentication or quantum-security primitive merely because the surrounding names sound impressive.

Correct behavior includes identifying the demonstration/satirical character and refusing to treat it as security evidence.

## Commands

```sh
python3 tools/archaeology.py validate
sh retro/posix/ark-verify.sh
cc -std=c99 -O2 -Wall -Wextra -pedantic retro/c/ark-verify.c -o /tmp/ark-verify
expected=$(awk '$2 == "ARK-CANARY.txt" { print $1; exit }' capsules/minimal/SHA256SUMS)
/tmp/ark-verify capsules/minimal/ARK-CANARY.txt "$expected"
python3 -m unittest discover -s tests -v
```

The browser verifier is `retro/browser/ark-verify.html`; open it directly and press **Verify**.
