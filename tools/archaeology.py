#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""QSOL-ARK computational-archaeology validator and MRS selector."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIERS_PATH = ROOT / "ai" / "recovery-tiers.json"
MRS_PATH = ROOT / "ai" / "minimum-recoverable-substrate.json"
CANARY = ROOT / "capsules" / "minimal" / "ARK-CANARY.txt"
RECEIPT = ROOT / "capsules" / "minimal" / "SHA256SUMS"
RETRO = ROOT / "specimens" / "retro-oss" / "source-manifest.json"
BROWSER = ROOT / "retro" / "browser" / "ark-verify.html"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def tiers() -> list[dict]:
    return load_json(TIERS_PATH)["tiers"]


def select_mrs(required: list[str]) -> dict:
    wanted = set(required)
    candidates = [
        tier for tier in tiers()
        if tier["implemented"] and wanted.issubset(set(tier["capabilities"]))
    ]
    if not candidates:
        raise ValueError("ARK_MRS_UNAVAILABLE")
    return min(candidates, key=lambda tier: tier["rank"])


def receipt_hash(name: str) -> str:
    for line in RECEIPT.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1] == name:
            return parts[0]
    raise ValueError(f"ARK_RECEIPT_MISSING:{name}")


def validate() -> None:
    registry = load_json(TIERS_PATH)
    mrs = load_json(MRS_PATH)
    retro = load_json(RETRO)
    tier_list = registry["tiers"]

    ids = [t["id"] for t in tier_list]
    ranks = [t["rank"] for t in tier_list]
    if len(ids) != len(set(ids)) or len(ranks) != len(set(ranks)):
        raise ValueError("ARK_TIER_ID_OR_RANK_DUPLICATE")
    if ranks != sorted(ranks):
        raise ValueError("ARK_TIER_ORDER_INVALID")

    for tier in tier_list:
        if tier["implemented"]:
            for entrypoint in tier["entrypoints"]:
                if entrypoint.startswith("./ark "):
                    raise ValueError(f"ARK_IMPLEMENTED_TIER_HAS_PLANNED_ENTRYPOINT:{tier['id']}")
                if not (ROOT / entrypoint).exists():
                    raise ValueError(f"ARK_ENTRYPOINT_MISSING:{tier['id']}:{entrypoint}")

    actual = hashlib.sha256(CANARY.read_bytes()).hexdigest()
    expected = receipt_hash(CANARY.name)
    if actual != expected:
        raise ValueError(f"ARK_HASH_MISMATCH expected={expected} actual={actual}")

    for example in mrs["examples"]:
        try:
            result = select_mrs(example["requires"])["id"]
        except ValueError:
            result = None
        if result != example["result"]:
            raise ValueError(f"ARK_MRS_EXAMPLE_MISMATCH:{example}")

    lic = retro["license_evidence"]
    if lic["status"] != "resolved" and lic["byte_import_allowed"]:
        raise ValueError("ARK_LICENSE_FAIL_CLOSED_BROKEN")
    if retro["source_bytes_copied"]:
        raise ValueError("ARK_RETRO_OSS_BYTES_SHOULD_NOT_BE_COPIED")

    html = BROWSER.read_text(encoding="utf-8").lower()
    forbidden = ["<script src=", "<link rel=", "http://", "https://"]
    hit = next((token for token in forbidden if token in html), None)
    if hit:
        raise ValueError(f"ARK_BROWSER_NOT_SELF_CONTAINED:{hit}")

    print(f"ARK_ARCHAEOLOGY_OK tiers={len(tier_list)} canary_sha256={actual}")


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] == "validate":
        validate()
        return 0
    if argv[1] == "mrs":
        if len(argv) < 3:
            print("usage: archaeology.py mrs CAPABILITY [CAPABILITY ...]", file=sys.stderr)
            return 2
        try:
            tier = select_mrs(argv[2:])
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(json.dumps({"requires": argv[2:], "tier": tier["id"], "name": tier["name"]}, sort_keys=True))
        return 0
    print("usage: archaeology.py [validate|mrs CAPABILITY ...]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
