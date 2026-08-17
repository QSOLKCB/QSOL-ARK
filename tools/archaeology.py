#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""QSOL-ARK computational-archaeology validator and MRS selector."""
from __future__ import annotations

import hashlib
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "manifest.json"
TIERS_PATH = ROOT / "ai" / "recovery-tiers.json"
MRS_PATH = ROOT / "ai" / "minimum-recoverable-substrate.json"
CONTEXT_POLICY_PATH = ROOT / "ai" / "context-sources.json"
CANARY = ROOT / "capsules" / "minimal" / "ARK-CANARY.txt"
RECEIPT = ROOT / "capsules" / "minimal" / "SHA256SUMS"
RETRO = ROOT / "specimens" / "retro-oss" / "source-manifest.json"
BROWSER = ROOT / "retro" / "browser" / "ark-verify.html"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def reconcile_implemented_tiers(manifest: dict, tier_list: list[dict]) -> None:
    declared = manifest.get("implemented_recovery_tiers")
    actual = [tier["id"] for tier in tier_list if tier["implemented"]]
    if declared != actual:
        raise ValueError(
            f"ARK_IMPLEMENTED_TIER_MISMATCH declared={declared} registry={actual}"
        )


def tiers() -> list[dict]:
    tier_list = load_json(TIERS_PATH)["tiers"]
    reconcile_implemented_tiers(load_json(MANIFEST_PATH), tier_list)
    return tier_list


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


def validate_import_record(policy: dict, record: dict) -> None:
    required = policy["required_import_fields"]
    missing = [field for field in required if field not in record]
    if missing:
        raise ValueError(f"ARK_PROVENANCE_FIELDS_MISSING:{','.join(missing)}")

    known_sources = {source["id"] for source in policy["sources"]}
    if record["source_id"] not in known_sources:
        raise ValueError(f"ARK_SOURCE_ID_UNKNOWN:{record['source_id']}")
    if record["visibility"] != "public":
        raise ValueError(f"ARK_VISIBILITY_FAIL_CLOSED:{record['visibility']}")
    if not isinstance(record["license"], str) or not record["license"].strip():
        raise ValueError("ARK_LICENSE_FIELD_INVALID")
    if record["canonical_or_derived"] not in {"canonical", "derived"}:
        raise ValueError(
            f"ARK_CANONICAL_STATUS_INVALID:{record['canonical_or_derived']}"
        )

    if record["source_id"] == "source.retro_oss":
        evidence = record["license_evidence"]
        resolved = evidence["status"] == "resolved"
        if not resolved and evidence["byte_import_allowed"]:
            raise ValueError("ARK_LICENSE_FAIL_CLOSED_BROKEN")
        if record["source_bytes_copied"] and not resolved:
            raise ValueError("ARK_THIRD_PARTY_BYTES_WITHOUT_RESOLVED_LICENSE")


def validate_mrs_contract(mrs: dict) -> None:
    examples = mrs.get("examples")
    if not isinstance(examples, list) or not examples:
        raise ValueError("ARK_MRS_EXAMPLES_INVALID")
    for index, example in enumerate(examples):
        if not isinstance(example, dict):
            raise ValueError(f"ARK_MRS_EXAMPLE_NOT_OBJECT:{index}")
        if set(example) != {"requires", "result"}:
            raise ValueError(f"ARK_MRS_EXAMPLE_SHAPE_INVALID:{index}")
        requires = example["requires"]
        result = example["result"]
        if (
            not isinstance(requires, list)
            or not requires
            or any(not isinstance(item, str) or not item for item in requires)
        ):
            raise ValueError(f"ARK_MRS_REQUIRES_INVALID:{index}")
        if result is not None and not isinstance(result, str):
            raise ValueError(f"ARK_MRS_RESULT_INVALID:{index}")


class BrowserProjectionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_payload = False
        self.payload_parts: list[str] = []
        self.expected: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        if tag == "textarea" and attr.get("id") == "payload":
            self.in_payload = True
        if tag == "input" and attr.get("id") == "expected":
            self.expected = attr.get("value")

    def handle_endtag(self, tag: str) -> None:
        if tag == "textarea" and self.in_payload:
            self.in_payload = False

    def handle_data(self, data: str) -> None:
        if self.in_payload:
            self.payload_parts.append(data)

    @property
    def payload(self) -> str:
        return "".join(self.payload_parts)


def validate_browser_projection(expected_hash: str) -> None:
    html = BROWSER.read_text(encoding="utf-8")
    lowered = html.lower()
    forbidden = ["<script src=", "<link rel=", "http://", "https://"]
    hit = next((token for token in forbidden if token in lowered), None)
    if hit:
        raise ValueError(f"ARK_BROWSER_NOT_SELF_CONTAINED:{hit}")

    parser = BrowserProjectionParser()
    parser.feed(html)
    canonical = CANARY.read_text(encoding="utf-8")
    if parser.payload != canonical:
        raise ValueError("ARK_BROWSER_CANARY_DRIFT")
    if parser.expected is None or parser.expected.strip().lower() != expected_hash:
        raise ValueError("ARK_BROWSER_RECEIPT_DRIFT")


def validate() -> None:
    manifest = load_json(MANIFEST_PATH)
    registry = load_json(TIERS_PATH)
    mrs = load_json(MRS_PATH)
    policy = load_json(CONTEXT_POLICY_PATH)
    retro = load_json(RETRO)
    tier_list = registry["tiers"]

    reconcile_implemented_tiers(manifest, tier_list)

    ids = [t["id"] for t in tier_list]
    ranks = [t["rank"] for t in tier_list]
    if any(not isinstance(tier_id, str) for tier_id in ids):
        raise ValueError("ARK_TIER_ID_NOT_STRING")
    if len(ids) != len(set(ids)) or len(ranks) != len(set(ranks)):
        raise ValueError("ARK_TIER_ID_OR_RANK_DUPLICATE")
    if ranks != sorted(ranks):
        raise ValueError("ARK_TIER_ORDER_INVALID")

    for tier in tier_list:
        if tier["implemented"]:
            for entrypoint in tier["entrypoints"]:
                if entrypoint.startswith("./ark "):
                    raise ValueError(
                        f"ARK_IMPLEMENTED_TIER_HAS_PLANNED_ENTRYPOINT:{tier['id']}"
                    )
                if not (ROOT / entrypoint).exists():
                    raise ValueError(f"ARK_ENTRYPOINT_MISSING:{tier['id']}:{entrypoint}")

    actual = hashlib.sha256(CANARY.read_bytes()).hexdigest()
    expected = receipt_hash(CANARY.name)
    if actual != expected:
        raise ValueError(f"ARK_HASH_MISMATCH expected={expected} actual={actual}")

    validate_mrs_contract(mrs)
    for example in mrs["examples"]:
        try:
            result = select_mrs(example["requires"])["id"]
        except ValueError as exc:
            if str(exc) != "ARK_MRS_UNAVAILABLE":
                raise
            result = None
        if result != example["result"]:
            raise ValueError(f"ARK_MRS_EXAMPLE_MISMATCH:{example}")

    validate_import_record(policy, retro)
    validate_browser_projection(expected)

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
        print(
            json.dumps(
                {"requires": argv[2:], "tier": tier["id"], "name": tier["name"]},
                sort_keys=True,
            )
        )
        return 0
    print("usage: archaeology.py [validate|mrs CAPABILITY ...]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
