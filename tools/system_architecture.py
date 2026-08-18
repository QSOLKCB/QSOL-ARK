#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Validate the canonical QSOL whole-system architecture contract."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ASCII_PATH = ROOT / "ARCHITECTURE.txt"
MACHINE_PATH = ROOT / "ai" / "system-architecture.json"
SHA256_REF = re.compile(r"^sha256:[0-9a-f]{64}$")


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_ref(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"ARK_SYSTEM_ARCHITECTURE_FILE_MISSING:{path.relative_to(ROOT)}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"ARK_SYSTEM_ARCHITECTURE_JSON_INVALID:{path.relative_to(ROOT)}:{exc}"
        ) from exc
    if not isinstance(value, dict):
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_JSON_NOT_OBJECT")
    return value


def read_ascii(path: Path = ASCII_PATH) -> bytes:
    if not path.is_file():
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_ASCII_MISSING")
    raw = path.read_bytes()
    try:
        raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"ARK_SYSTEM_ARCHITECTURE_NOT_7BIT_ASCII:offset={exc.start}"
        ) from exc
    if b"\r" in raw:
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_NON_LF_NEWLINE")
    if b"\t" in raw:
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_TAB_FORBIDDEN")
    if not raw.endswith(b"\n"):
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_FINAL_NEWLINE_REQUIRED")
    return raw


def require_closed(record: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValueError(f"ARK_SYSTEM_ARCHITECTURE_{label}_NOT_OBJECT")
    actual = set(record)
    if actual != keys:
        raise ValueError(
            f"ARK_SYSTEM_ARCHITECTURE_{label}_FIELDS:expected={sorted(keys)!r}:found={sorted(actual)!r}"
        )
    return record


def require_nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"ARK_SYSTEM_ARCHITECTURE_{label}_INVALID:{value!r}")
    return value


def require_unique_strings(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ValueError(f"ARK_SYSTEM_ARCHITECTURE_{label}_INVALID")
    if any(not isinstance(item, str) or not item for item in value):
        raise ValueError(f"ARK_SYSTEM_ARCHITECTURE_{label}_NONSTRING")
    if len(value) != len(set(value)):
        raise ValueError(f"ARK_SYSTEM_ARCHITECTURE_{label}_DUPLICATE")
    return value


def validate_machine(machine: dict[str, Any], ascii_raw: bytes) -> dict[str, Any]:
    top_keys = {
        "type", "protocol", "schema_version", "canonical_owner", "semantic_source",
        "canonical_ascii", "ascii_sha256", "authority", "ascii_contract", "roles",
        "flows", "lattice", "cold_restore", "personal_continuity",
        "deterministic_search", "reversibility", "hard_boundaries",
        "empirical_honesty", "mirror_policy", "final_rule", "semantic_sha256",
    }
    require_closed(machine, top_keys, "ROOT")
    if machine["type"] != "qsol-system-architecture":
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_TYPE_MISMATCH")
    if machine["protocol"] != "QSOL-ARK/SYSTEM-ARCHITECTURE/1":
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_PROTOCOL_MISMATCH")
    if machine["schema_version"] != "1.1.0":
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_SCHEMA_VERSION_MISMATCH")
    if machine["canonical_owner"] != "QSOLKCB/QSOL-ARK":
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_OWNER_MISMATCH")
    if machine["semantic_source"] != "ai/system-architecture.json":
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_SEMANTIC_SOURCE_MISMATCH")
    if machine["canonical_ascii"] != "ARCHITECTURE.txt":
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_ASCII_PATH_MISMATCH")

    declared_ascii_sha = machine["ascii_sha256"]
    if not isinstance(declared_ascii_sha, str) or SHA256_REF.fullmatch(declared_ascii_sha) is None:
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_ASCII_SHA_INVALID")
    actual_ascii_sha = sha256_ref(ascii_raw)
    if declared_ascii_sha != actual_ascii_sha:
        raise ValueError(
            f"ARK_SYSTEM_ARCHITECTURE_ASCII_SHA_MISMATCH:expected={declared_ascii_sha}:found={actual_ascii_sha}"
        )

    declared_semantic_sha = machine["semantic_sha256"]
    if not isinstance(declared_semantic_sha, str) or SHA256_REF.fullmatch(declared_semantic_sha) is None:
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_SEMANTIC_SHA_INVALID")
    semantic_payload = {key: value for key, value in machine.items() if key != "semantic_sha256"}
    actual_semantic_sha = sha256_ref(canonical_json_bytes(semantic_payload))
    if declared_semantic_sha != actual_semantic_sha:
        raise ValueError(
            f"ARK_SYSTEM_ARCHITECTURE_SEMANTIC_SHA_MISMATCH:expected={declared_semantic_sha}:found={actual_semantic_sha}"
        )

    authority = require_closed(
        machine["authority"],
        {"cross_repository_semantics", "canonical_ascii_projection", "local_implementation_status", "conflict_rule", "local_repositories_may_silently_redefine_other_repository_roles"},
        "AUTHORITY",
    )
    for key in ("cross_repository_semantics", "canonical_ascii_projection", "local_implementation_status", "conflict_rule"):
        require_nonempty_string(authority[key], f"AUTHORITY_{key.upper()}")
    if authority["cross_repository_semantics"] != machine["semantic_source"]:
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_ROLE_AUTHORITY_SOURCE_MISMATCH")
    if authority["local_repositories_may_silently_redefine_other_repository_roles"] is not False:
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_LOCAL_REDEFINITION_POLICY_MISMATCH")

    ascii_contract = require_closed(
        machine["ascii_contract"],
        {"encoding", "seven_bit_only", "newline", "tabs_allowed", "unicode_box_drawing_allowed", "mermaid_required"},
        "ASCII_CONTRACT",
    )
    if ascii_contract != {
        "encoding": "US-ASCII", "seven_bit_only": True, "newline": "LF",
        "tabs_allowed": False, "unicode_box_drawing_allowed": False, "mermaid_required": False,
    }:
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_ASCII_CONTRACT_MISMATCH")

    roles = machine["roles"]
    if not isinstance(roles, list) or not roles:
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_ROLES_INVALID")
    role_fields = {"repository", "short_name", "verb", "role", "authority_boundary"}
    short_names: set[str] = set()
    repositories: set[str] = set()
    for index, item in enumerate(roles):
        role = require_closed(item, role_fields, f"ROLE_{index}")
        for key in role_fields:
            require_nonempty_string(role[key], f"ROLE_{index}_{key.upper()}")
        if role["short_name"] in short_names or role["repository"] in repositories:
            raise ValueError("ARK_SYSTEM_ARCHITECTURE_ROLE_DUPLICATE")
        short_names.add(role["short_name"])
        repositories.add(role["repository"])
        expected_repo = "QSOLKCB/LATTICE" if role["short_name"] == "LATTICE" else f"QSOLKCB/{role['short_name']}"
        if role["repository"] != expected_repo:
            raise ValueError(
                f"ARK_SYSTEM_ARCHITECTURE_ROLE_REPOSITORY_MISMATCH:{role['short_name']}:{role['repository']}"
            )

    flows = require_closed(machine["flows"], {"evidence_reasoning", "personal_continuity", "archival_enrichment"}, "FLOWS")
    for name, members in flows.items():
        values = require_unique_strings(members, f"FLOW_{name.upper()}")
        for member in values:
            if member != "external-private-vault" and member not in short_names:
                raise ValueError(f"ARK_SYSTEM_ARCHITECTURE_FLOW_UNKNOWN_ROLE:{name}:{member}")

    lattice = require_closed(machine["lattice"], {"profile_id", "profile_fingerprint", "conformance_payload", "authority"}, "LATTICE")
    require_nonempty_string(lattice["profile_id"], "LATTICE_PROFILE_ID")
    if lattice["authority"] != "storage-only":
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_LATTICE_AUTHORITY_MISMATCH")
    payload = require_closed(
        lattice["conformance_payload"],
        {"max_address_length", "max_recursive_depth", "modulus", "lexicographic_cells", "lexicographic_traversal_id", "phi_stride", "phi_stride_cells", "phi_traversal_id", "profile_id", "protocol"},
        "LATTICE_PAYLOAD",
    )
    if payload["profile_id"] != lattice["profile_id"]:
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_LATTICE_PROFILE_PAYLOAD_MISMATCH")
    lex = require_unique_strings(payload["lexicographic_cells"], "LATTICE_LEXICOGRAPHIC_CELLS")
    phi = require_unique_strings(payload["phi_stride_cells"], "LATTICE_PHI_CELLS")
    if len(lex) != 27 or len(phi) != 27 or set(lex) != set(phi):
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_LATTICE_BIJECTION_MISMATCH")
    computed_lattice_fp = sha256_ref(canonical_json_bytes(payload))
    if lattice["profile_fingerprint"] != computed_lattice_fp:
        raise ValueError(
            f"ARK_SYSTEM_ARCHITECTURE_LATTICE_FINGERPRINT_MISMATCH:expected={lattice['profile_fingerprint']}:found={computed_lattice_fp}"
        )

    cold = require_closed(machine["cold_restore"], {"architecture_target", "canonical_object", "dna_projection", "lattice_role", "recovery_authority", "implementation_status_rule"}, "COLD_RESTORE")
    for key, value in cold.items():
        require_nonempty_string(value, f"COLD_RESTORE_{key.upper()}")

    continuity = require_closed(machine["personal_continuity"], {"target_capability", "non_goal", "capsule_order", "trial_order", "t5_ai_reconstruction_currently_implemented"}, "PERSONAL_CONTINUITY")
    require_nonempty_string(continuity["target_capability"], "CONTINUITY_TARGET")
    require_nonempty_string(continuity["non_goal"], "CONTINUITY_NON_GOAL")
    require_unique_strings(continuity["capsule_order"], "CONTINUITY_CAPSULE_ORDER")
    require_unique_strings(continuity["trial_order"], "CONTINUITY_TRIAL_ORDER")
    if continuity["t5_ai_reconstruction_currently_implemented"] is not False:
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_T5_STATUS_MISMATCH")

    search = require_closed(machine["deterministic_search"], {"status", "intended_owner", "lineage", "architecture", "required_invariant", "receipt_rule"}, "DETERMINISTIC_SEARCH")
    for key in ("status", "intended_owner", "lineage", "required_invariant", "receipt_rule"):
        require_nonempty_string(search[key], f"SEARCH_{key.upper()}")
    require_unique_strings(search["architecture"], "SEARCH_ARCHITECTURE")
    if search["status"] != "planned-not-yet-implemented":
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_SEARCH_STATUS_MISMATCH")

    reversibility = require_closed(machine["reversibility"], {"protocol", "invariants"}, "REVERSIBILITY")
    require_nonempty_string(reversibility["protocol"], "REVERSIBILITY_PROTOCOL")
    require_unique_strings(reversibility["invariants"], "REVERSIBILITY_INVARIANTS")
    require_unique_strings(machine["hard_boundaries"], "HARD_BOUNDARIES")
    require_unique_strings(machine["empirical_honesty"], "EMPIRICAL_HONESTY")

    mirror = require_closed(machine["mirror_policy"], {"allowed", "canonical_count", "required_mirror_fields"}, "MIRROR_POLICY")
    if mirror["allowed"] is not True or mirror["canonical_count"] != 1:
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_MIRROR_POLICY_MISMATCH")
    require_unique_strings(mirror["required_mirror_fields"], "MIRROR_FIELDS")
    require_nonempty_string(machine["final_rule"], "FINAL_RULE")

    text = ascii_raw.decode("ascii")
    for role in roles:
        line = f"  {role['short_name']:<15} = {role['verb']}"
        if line not in text:
            raise ValueError(f"ARK_SYSTEM_ARCHITECTURE_ASCII_ROLE_MISSING:{role['short_name']}")
    for invariant in machine["hard_boundaries"] + machine["empirical_honesty"] + reversibility["invariants"]:
        if invariant not in text:
            raise ValueError(f"ARK_SYSTEM_ARCHITECTURE_ASCII_INVARIANT_MISSING:{invariant}")
    if "PLANNED / NOT YET IMPLEMENTED AS A CANONICAL QSOL-CONTROL PRIMITIVE" not in text:
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_ASCII_SEARCH_STATUS_MISSING")
    if "T5 AI RECONSTRUCTION:\n    NOT IMPLEMENTED" not in text:
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_ASCII_T5_STATUS_MISSING")
    if lattice["profile_fingerprint"] not in text:
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_ASCII_LATTICE_FINGERPRINT_MISSING")

    return {
        "protocol": machine["protocol"],
        "status": "valid",
        "semantic_sha256": declared_semantic_sha,
        "ascii_sha256": declared_ascii_sha,
        "roles": len(roles),
        "lattice_profile_fingerprint": lattice["profile_fingerprint"],
        "deterministic_search_status": search["status"],
        "t5_ai_reconstruction_implemented": continuity["t5_ai_reconstruction_currently_implemented"],
    }


def validate() -> dict[str, Any]:
    return validate_machine(load_json(MACHINE_PATH), read_ascii())


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2, sort_keys=True))
