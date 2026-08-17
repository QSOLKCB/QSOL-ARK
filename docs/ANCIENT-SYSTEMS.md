# Preserve the Ancient Systems

PR #4 asks a deliberately narrower question than “can we emulate an old computer?”

> Can a future system recover enough execution context to understand how software ran, while preserving the difference between original hardware, original software, emulator behaviour, compatibility behaviour, and reconstruction inference?

## Seed profiles

The initial machine-readable set contains five profiles:

- Commodore 64 — hardware system
- Commodore Amiga 500 — hardware system
- IBM Personal Computer XT (5160) — hardware system
- CP/M 2.2 — software environment spanning multiple hardware systems
- UNIX Seventh Edition on PDP-11-class systems — software environment with model-dependent host details

CP/M and UNIX are intentionally **not** flattened into one canonical machine.

## Evidence classes

Every profile separates:

- `hardware_fact`
- `documented_software_behaviour`
- `emulator_behaviour`
- `compatibility_layer_behaviour`
- `reconstruction_inference`
- `unknown`

An emulator result is useful evidence about that emulator run. It does not become original hardware history merely because the screen looks right.

## Historical Recovery Equivalence

PR #4 defines six derived reconstruction classes:

1. `exact_reproduction`
2. `functional_equivalence`
3. `historically_plausible_approximation`
4. `emulator_assisted_reproduction`
5. `modern_compatibility_layer`
6. `impossible_or_unsupported`

The seed profiles claim only `historically_plausible_approximation`.

**Exact reproduction is not available merely because the metadata is detailed.**

## Rights boundary

This repository does not become a ROM collection.

The seed includes no Commodore ROM image, Amiga Kickstart/Workbench image, IBM BIOS image, DOS image, CP/M binary distribution, UNIX distribution image, copyrighted disk image, or other third-party system payload.

Profiles preserve metadata, public source references, evidence boundaries, and reconstruction questions.

## Computational Archaeology boundary

The T0–T5 Computational Archaeology tiers describe environments in which **ARK itself can be recovered or validated**.

They do not mean a historical system natively runs the corresponding ARK implementation.

```text
HOST_RECOVERY_TIER != NATIVE_HISTORICAL_EXECUTION
EMULATOR_BEHAVIOUR != ORIGINAL_HARDWARE_FACT
SOFTWARE_ENVIRONMENT != ONE_CANONICAL_MACHINE
```

## Minimum reconstruction probe

`systems/tasks/minimum-reconstruction-probe.json` asks a cold-start model to describe a minimum execution flow for each seed profile without importing proprietary bytes or erasing hardware variability.

## Validation

```sh
python3 tools/systems.py
python3 -m unittest tests.test_systems -v
```

Expected validator status:

```text
ARK_SYSTEMS_OK profiles=5 tasks=1 exact_reproduction=0
```
