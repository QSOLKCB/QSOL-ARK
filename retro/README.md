# Retro Recovery Implementations

These are independent recovery surfaces for QSOL-ARK's Computational Archaeology track.

- `posix/ark-verify.sh` — T1, shell plus an available SHA-256 provider.
- `c/ark-verify.c` — T2, standalone C99 SHA-256 verifier with no non-standard library dependency.
- `browser/ark-verify.html` — T3, single-file offline browser verifier using Web Crypto.

They share `capsules/minimal/ARK-CANARY.txt` and its `SHA256SUMS` receipt.

A tier may claim only capabilities declared in `ai/recovery-tiers.json`.
