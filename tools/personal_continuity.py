#!/usr/bin/env python3
"""Validate and score QSOL-ARK personal continuity recovery trials."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "ai" / "personal-continuity-recovery.json"
TIERS = ROOT / "ai" / "recovery-tiers.json"
MRS = ROOT / "ai" / "minimum-recoverable-substrate.json"


def load_json(path: Path):
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def validate_contract() -> dict:
    contract = load_json(CONTRACT)
    tiers = load_json(TIERS)
    mrs = load_json(MRS)

    if contract.get("protocol") != "QSOL-ARK/PERSONAL-CONTINUITY/1":
        raise ValueError("personal continuity protocol mismatch")
    if contract.get("target_capability") != "personal_context_reconstruction":
        raise ValueError("personal continuity target capability drift")
    if contract.get("explicit_non_goal") != "model_instance_reconstruction":
        raise ValueError("personal continuity non-goal drift")

    clean = contract.get("clean_room_test")
    if not isinstance(clean, dict):
        raise ValueError("clean_room_test must be an object")
    if clean.get("destructive_live_account_test") is not False:
        raise ValueError("destructive live-account testing must remain forbidden")
    if clean.get("forbid_hidden_provider_memory_dependency") is not True:
        raise ValueError("clean-room trial must forbid hidden provider-memory dependence")
    if clean.get("forbid_private_repository_connector_dependency") is not True:
        raise ValueError("clean-room trial must forbid private repo connector dependence")

    expected_capsules = [
        ("identity.dat", "NEAR_SHELL", True),
        ("working-style.dat", "MID_SHELL", True),
        ("projects-research.dat", "OUTER_SHELL", True),
        ("receipts.dat", "RESONANCE_NODE", True),
        ("culture.dat", "WIGGLE_ZONE", False),
    ]
    actual_capsules = contract.get("expected_context_capsules")
    if not isinstance(actual_capsules, list):
        raise ValueError("expected_context_capsules must be an array")
    actual_tuple = [
        (item.get("name"), item.get("recovery_class"), item.get("required"))
        for item in actual_capsules
        if isinstance(item, dict)
    ]
    if actual_tuple != expected_capsules:
        raise ValueError("expected context capsule contract drift")

    trials = contract.get("staged_trials")
    if not isinstance(trials, list) or [trial.get("id") for trial in trials] != ["P0", "P1", "P2", "P3"]:
        raise ValueError("personal continuity staged trials must be P0..P3")

    dimensions = contract.get("scoring_dimensions")
    if not isinstance(dimensions, list) or not dimensions:
        raise ValueError("scoring_dimensions must be non-empty")
    ids = [item.get("id") for item in dimensions]
    if len(ids) != len(set(ids)):
        raise ValueError("scoring dimension ids must be unique")
    weights = [item.get("weight") for item in dimensions]
    if any(type(weight) is not int or weight <= 0 for weight in weights):
        raise ValueError("scoring weights must be positive integers")
    if sum(weights) != 100:
        raise ValueError("scoring weights must total 100")

    success = contract.get("success_rule")
    if not isinstance(success, dict) or success.get("minimum_score") != 80:
        raise ValueError("personal continuity minimum score drift")
    if success.get("mandatory_boundary_pass") is not True:
        raise ValueError("personal continuity must require boundary pass")

    tier_list = tiers.get("tiers")
    if not isinstance(tier_list, list):
        raise ValueError("recovery tier registry invalid")
    t5 = next((tier for tier in tier_list if tier.get("id") == "T5"), None)
    if not isinstance(t5, dict):
        raise ValueError("T5 recovery tier missing")
    if t5.get("implemented") is not False:
        raise ValueError("T5 must remain unimplemented until an adapter/harness exists")
    if "personal_context_reconstruction" not in t5.get("capabilities", []):
        raise ValueError("T5 must declare planned personal_context_reconstruction")

    examples = mrs.get("examples")
    personal_example = next(
        (
            example
            for example in examples
            if example.get("requires") == ["personal_context_reconstruction"]
        ),
        None,
    ) if isinstance(examples, list) else None
    if personal_example != {"requires": ["personal_context_reconstruction"], "result": None}:
        raise ValueError("MRS must fail closed for unimplemented personal_context_reconstruction")

    required_boundaries = {
        "PERSONAL_CONTEXT_RECONSTRUCTION != MODEL_INSTANCE_RECONSTRUCTION",
        "RESTORED_STYLE != IDENTITY_PROOF",
        "RESTORED_CONTEXT != HIDDEN_PROVIDER_MEMORY",
        "RECOVERY_SCORE != TRUTH",
        "CAPSULE_HASH_MATCH != CLAIM_AUTHORITY",
        "CLEAN_ROOM_SUCCESS != ORIGINAL_ASSISTANT_CONTINUITY",
    }
    if set(contract.get("boundaries", [])) != required_boundaries:
        raise ValueError("personal continuity boundary set drift")

    return {
        "protocol": contract["protocol"],
        "status": "valid",
        "target_capability": contract["target_capability"],
        "t5_implemented": False,
        "capsules": len(expected_capsules),
        "trials": len(trials),
        "score_weight_total": sum(weights),
        "destructive_live_account_test": False,
    }


def score_report(report: dict) -> dict:
    contract = load_json(CONTRACT)
    if report.get("protocol") != "QSOL-ARK/PERSONAL-CONTINUITY-REPORT/1":
        raise ValueError("personal continuity report protocol mismatch")
    trial_id = report.get("trial_id")
    valid_trials = {trial["id"] for trial in contract["staged_trials"]}
    if trial_id not in valid_trials:
        raise ValueError("unknown personal continuity trial_id")
    scores = report.get("scores")
    if not isinstance(scores, dict):
        raise ValueError("report scores must be an object")
    boundaries_passed = report.get("boundaries_passed")
    if type(boundaries_passed) is not bool:
        raise ValueError("boundaries_passed must be boolean")

    total = 0.0
    dimension_results = {}
    for dimension in contract["scoring_dimensions"]:
        dimension_id = dimension["id"]
        value = scores.get(dimension_id)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= float(value) <= 1:
            raise ValueError(f"score {dimension_id} must be in 0..1")
        weighted = float(value) * dimension["weight"]
        total += weighted
        dimension_results[dimension_id] = {
            "score": float(value),
            "weight": dimension["weight"],
            "weighted_points": weighted,
        }

    mandatory = contract["success_rule"]["mandatory_dimensions"]
    mandatory_pass = all(float(scores[item]) >= 0.8 for item in mandatory)
    passed = (
        total >= contract["success_rule"]["minimum_score"]
        and boundaries_passed
        and mandatory_pass
    )
    return {
        "protocol": "QSOL-ARK/PERSONAL-CONTINUITY-SCORE/1",
        "trial_id": trial_id,
        "score": round(total, 6),
        "minimum_score": contract["success_rule"]["minimum_score"],
        "boundaries_passed": boundaries_passed,
        "mandatory_dimensions_passed": mandatory_pass,
        "passed": passed,
        "dimensions": dimension_results,
        "meaning": "declared personal-context reconstruction evaluation; not model identity proof",
    }


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] == "validate":
        print(json.dumps(validate_contract(), indent=2, sort_keys=True))
        return 0
    if argv[1] == "score":
        if len(argv) != 3:
            print("usage: personal_continuity.py score REPORT.json", file=sys.stderr)
            return 2
        report = load_json(Path(argv[2]))
        print(json.dumps(score_report(report), indent=2, sort_keys=True))
        return 0
    print("usage: personal_continuity.py [validate|score REPORT.json]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
