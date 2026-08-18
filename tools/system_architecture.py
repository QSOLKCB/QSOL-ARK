#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Validate the canonical QSOL whole-system architecture map."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ASCII_PATH = ROOT / "ARCHITECTURE.txt"
MACHINE_PATH = ROOT / "ai" / "system-architecture.json"

EXPECTED_PROTOCOL = "QSOL-ARK/SYSTEM-ARCHITECTURE/1"
EXPECTED_LATTICE_FINGERPRINT = (
    "sha256:6e7c4a9a781d552a2b561d334a8435c12efe2908fcd24a0f152935aded555bcf"
)
EXPECTED_ROLES = {
    "QSOL-SUBSTRATE": "KNOWS",
    "QSOL-ARK": "SURVIVES",
    "QSOL-INT": "COMPOSES",
    "QSOL-ORACLE": "WITNESSES",
    "QSOL-NEXUS": "REASONS",
    "QSOL-CONTROL": "OPERATES",
    "QSOL-CORPUS": "PRESERVES",
    "QSOL-CONTEXT": "CURATES",
    "LATTICE": "REMEMBERS STRUCTURE",
}
EXPECTED_BOUNDARIES = {
    "OPERATOR_AUTHORITY != EPISTEMIC_AUTHORITY",
    "CONTROL_DISPLAY != AUTHORITY",
    "VOTE != EVIDENCE",
    "CONSENSUS != TRUTH",
    "CONFIDENCE != PROBABILITY",
    "STORED != TRUE",
    "PERSISTED != CANONICAL_FOR_TRUTH",
    "MODEL_STATE != MODEL_MIND",
    "VISIBLE_OUTPUT != HIDDEN_REASONING",
    "GEOMETRY != TRUTH",
    "REPLAY != REPRODUCTION",
    "ARCHIVED_MESSAGE != FACT",
    "RESTORE_SUCCESS != FACTUAL_TRUTH",
    "PERSONAL_CONTEXT_RECONSTRUCTION != MODEL_INSTANCE_RECONSTRUCTION",
}
EXPECTED_HONESTY = {
    "CLAIMED_EXECUTION != EXECUTED",
    "SCRIPT_WRITTEN != SCRIPT_RUN",
    "PARSER_AVAILABLE != PARSED",
    "CAPABILITY_CLAIM != CAPABILITY_RECEIPT",
    "MODEL_SELF_REPORT != TOOL_RECEIPT",
    "IDENTITY_LABEL != SAME_MACHINE",
    "CONFIDENCE != EVIDENCE",
    "CORRECTION != COVER_STORY",
    "HUMOUR != EXEMPTION_FROM_PROVENANCE",
}


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


def read_ascii() -> bytes:
    if not ASCII_PATH.is_file():
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_ASCII_MISSING")
    raw = ASCII_PATH.read_bytes()
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


def _expect(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise ValueError(
            f"ARK_SYSTEM_ARCHITECTURE_{label}:expected={expected!r}:found={actual!r}"
        )


def validate() -> dict[str, Any]:
    raw = read_ascii()
    text = raw.decode("ascii")
    machine = load_json(MACHINE_PATH)

    _expect(machine.get("protocol"), EXPECTED_PROTOCOL, "PROTOCOL_MISMATCH")
    _expect(machine.get("canonical_owner"), "QSOLKCB/QSOL-ARK", "OWNER_MISMATCH")
    _expect(machine.get("canonical_ascii"), "ARCHITECTURE.txt", "ASCII_PATH_MISMATCH")

    authority = machine.get("authority")
    if not isinstance(authority, dict):
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_AUTHORITY_INVALID")
    _expect(
        authority.get("cross_repository_roles"),
        "QSOLKCB/QSOL-ARK/ARCHITECTURE.txt",
        "ROLE_AUTHORITY_MISMATCH",
    )
    _expect(
        authority.get("local_implementation_status"),
        "live state of each local repository",
        "LOCAL_STATUS_AUTHORITY_MISMATCH",
    )
    _expect(
        authority.get("local_repositories_may_silently_redefine_other_repository_roles"),
        False,
        "LOCAL_REDEFINITION_POLICY_MISMATCH",
    )

    ascii_contract = machine.get("ascii_contract")
    if not isinstance(ascii_contract, dict):
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_ASCII_CONTRACT_INVALID")
    _expect(ascii_contract.get("encoding"), "US-ASCII", "ENCODING_MISMATCH")
    _expect(ascii_contract.get("seven_bit_only"), True, "SEVEN_BIT_POLICY_MISMATCH")
    _expect(ascii_contract.get("newline"), "LF", "NEWLINE_POLICY_MISMATCH")
    _expect(ascii_contract.get("tabs_allowed"), False, "TAB_POLICY_MISMATCH")

    roles = machine.get("roles")
    if not isinstance(roles, list) or len(roles) != len(EXPECTED_ROLES):
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_ROLE_COUNT_MISMATCH")
    role_map: dict[str, str] = {}
    for index, role in enumerate(roles):
        if not isinstance(role, dict):
            raise ValueError(f"ARK_SYSTEM_ARCHITECTURE_ROLE_NOT_OBJECT:{index}")
        name = role.get("short_name")
        verb = role.get("verb")
        if not isinstance(name, str) or not isinstance(verb, str):
            raise ValueError(f"ARK_SYSTEM_ARCHITECTURE_ROLE_INVALID:{index}")
        if name in role_map:
            raise ValueError(f"ARK_SYSTEM_ARCHITECTURE_ROLE_DUPLICATE:{name}")
        role_map[name] = verb
    _expect(role_map, EXPECTED_ROLES, "ROLE_MAP_MISMATCH")

    for name, verb in EXPECTED_ROLES.items():
        line = f"  {name:<15} = {verb}"
        if line not in text:
            raise ValueError(f"ARK_SYSTEM_ARCHITECTURE_ASCII_ROLE_MISSING:{name}")

    lattice = machine.get("lattice")
    if not isinstance(lattice, dict):
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_LATTICE_INVALID")
    _expect(
        lattice.get("profile_id"),
        "qsol-3x3x3-sierpinski-derived-memory/1",
        "LATTICE_PROFILE_MISMATCH",
    )
    _expect(
        lattice.get("profile_fingerprint"),
        EXPECTED_LATTICE_FINGERPRINT,
        "LATTICE_FINGERPRINT_MISMATCH",
    )
    _expect(lattice.get("top_level_cells"), 27, "LATTICE_CELL_COUNT_MISMATCH")
    _expect(lattice.get("phi_stride"), 17, "LATTICE_STRIDE_MISMATCH")
    _expect(lattice.get("modulus"), 27, "LATTICE_MODULUS_MISMATCH")
    if EXPECTED_LATTICE_FINGERPRINT not in text:
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_ASCII_LATTICE_FINGERPRINT_MISSING")

    search = machine.get("deterministic_search")
    if not isinstance(search, dict):
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_SEARCH_INVALID")
    _expect(search.get("status"), "planned-not-yet-implemented", "SEARCH_STATUS_MISMATCH")
    _expect(search.get("intended_owner"), "QSOL-CONTROL", "SEARCH_OWNER_MISMATCH")
    _expect(
        search.get("required_invariant"),
        "UNDO(APPLY(STATE,ACTION)) == STATE",
        "SEARCH_REVERSIBILITY_MISMATCH",
    )
    if "PLANNED / NOT YET IMPLEMENTED AS A CANONICAL QSOL-CONTROL PRIMITIVE" not in text:
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_ASCII_SEARCH_STATUS_MISSING")

    continuity = machine.get("personal_continuity")
    if not isinstance(continuity, dict):
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_CONTINUITY_INVALID")
    _expect(
        continuity.get("target_capability"),
        "personal_context_reconstruction",
        "CONTINUITY_TARGET_MISMATCH",
    )
    _expect(
        continuity.get("non_goal"),
        "model_instance_reconstruction",
        "CONTINUITY_NON_GOAL_MISMATCH",
    )
    _expect(
        continuity.get("t5_ai_reconstruction_currently_implemented"),
        False,
        "T5_STATUS_MISMATCH",
    )

    boundaries = machine.get("hard_boundaries")
    if not isinstance(boundaries, list) or set(boundaries) != EXPECTED_BOUNDARIES:
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_BOUNDARY_SET_MISMATCH")
    honesty = machine.get("empirical_honesty")
    if not isinstance(honesty, list) or set(honesty) != EXPECTED_HONESTY:
        raise ValueError("ARK_SYSTEM_ARCHITECTURE_HONESTY_SET_MISMATCH")
    for invariant in EXPECTED_BOUNDARIES | EXPECTED_HONESTY:
        if invariant not in text:
            raise ValueError(
                f"ARK_SYSTEM_ARCHITECTURE_ASCII_INVARIANT_MISSING:{invariant}"
            )

    required_ascii_phrases = [
        "CROSS_REPOSITORY_ROLE_AUTHORITY = QSOL-ARK/ARCHITECTURE.txt",
        "LOCAL_IMPLEMENTATION_AUTHORITY  = live state of each local repository",
        "ONE CANONICAL ARCHITECTURE + MANY VERIFIED MIRRORS != MANY AUTHORITIES",
        "THE SYSTEM DOES NOT ATTEMPT TO PRESERVE A MODEL'S SOUL.",
        "PROVE IT, MATE.",
    ]
    for phrase in required_ascii_phrases:
        if phrase not in text:
            raise ValueError(f"ARK_SYSTEM_ARCHITECTURE_ASCII_PHRASE_MISSING:{phrase}")

    return {
        "protocol": EXPECTED_PROTOCOL,
        "status": "valid",
        "canonical_ascii": "ARCHITECTURE.txt",
        "ascii_sha256": hashlib.sha256(raw).hexdigest(),
        "ascii_bytes": len(raw),
        "roles": len(role_map),
        "lattice_profile_fingerprint": EXPECTED_LATTICE_FINGERPRINT,
        "deterministic_search_status": search["status"],
        "t5_ai_reconstruction_implemented": False,
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2, sort_keys=True))
