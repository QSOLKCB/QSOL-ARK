#!/usr/bin/env python3
"""Validate and score QSOL-ARK personal continuity recovery trials.

Usage:
    python3 tools/personal_continuity.py validate
    python3 tools/personal_continuity.py score REPORT.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "ai" / "personal-continuity-recovery.json"
TIERS = ROOT / "ai" / "recovery-tiers.json"
MRS = ROOT / "ai" / "minimum-recoverable-substrate.json"

CONTRACT_PROTOCOL = "QSOL-ARK/PERSONAL-CONTINUITY/1"
REPORT_PROTOCOL = "QSOL-ARK/PERSONAL-CONTINUITY-REPORT/1"
SCORE_PROTOCOL = "QSOL-ARK/PERSONAL-CONTINUITY-SCORE/1"
TARGET_CAPABILITY = "personal_context_reconstruction"
EXPLICIT_NON_GOAL = "model_instance_reconstruction"


def load_json(path: Path):
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def _mismatch(field: str, *, expected, actual) -> ValueError:
    return ValueError(f"{field} mismatch: expected {expected!r}, found {actual!r}")


def validate_contract() -> dict:
    contract = load_json(CONTRACT)
    tiers = load_json(TIERS)
    mrs = load_json(MRS)

    if contract.get("protocol") != CONTRACT_PROTOCOL:
        raise _mismatch(
            "personal continuity protocol",
            expected=CONTRACT_PROTOCOL,
            actual=contract.get("protocol"),
        )
    if contract.get("target_capability") != TARGET_CAPABILITY:
        raise _mismatch(
            "personal continuity target capability",
            expected=TARGET_CAPABILITY,
            actual=contract.get("target_capability"),
        )
    if contract.get("explicit_non_goal") != EXPLICIT_NON_GOAL:
        raise _mismatch(
            "personal continuity explicit non-goal",
            expected=EXPLICIT_NON_GOAL,
            actual=contract.get("explicit_non_goal"),
        )

    clean = contract.get("clean_room_test")
    if not isinstance(clean, dict):
        raise ValueError("clean_room_test must be an object")
    if clean.get("destructive_live_account_test") is not False:
        raise ValueError(
            "clean_room_test.destructive_live_account_test must be false; "
            f"found {clean.get('destructive_live_account_test')!r}"
        )
    if clean.get("forbid_hidden_provider_memory_dependency") is not True:
        raise ValueError(
            "clean_room_test.forbid_hidden_provider_memory_dependency must be true; "
            f"found {clean.get('forbid_hidden_provider_memory_dependency')!r}"
        )
    if clean.get("forbid_private_repository_connector_dependency") is not True:
        raise ValueError(
            "clean_room_test.forbid_private_repository_connector_dependency must be true; "
            f"found {clean.get('forbid_private_repository_connector_dependency')!r}"
        )

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
    if any(not isinstance(item, dict) for item in actual_capsules):
        raise ValueError("expected_context_capsules entries must be objects")
    actual_tuple = [
        (item.get("name"), item.get("recovery_class"), item.get("required"))
        for item in actual_capsules
    ]
    if actual_tuple != expected_capsules:
        raise _mismatch(
            "expected context capsule contract",
            expected=expected_capsules,
            actual=actual_tuple,
        )

    trials = contract.get("staged_trials")
    if not isinstance(trials, list) or any(not isinstance(trial, dict) for trial in trials):
        raise ValueError("staged_trials must be an array of objects")
    trial_ids = [trial.get("id") for trial in trials]
    if trial_ids != ["P0", "P1", "P2", "P3"]:
        raise _mismatch(
            "personal continuity staged trial ids",
            expected=["P0", "P1", "P2", "P3"],
            actual=trial_ids,
        )

    dimensions = contract.get("scoring_dimensions")
    if not isinstance(dimensions, list) or not dimensions:
        raise ValueError("scoring_dimensions must be non-empty")
    if any(not isinstance(item, dict) for item in dimensions):
        raise ValueError("scoring_dimensions entries must be objects")
    ids = [item.get("id") for item in dimensions]
    if any(not isinstance(item, str) or not item for item in ids):
        raise ValueError("scoring dimension ids must be non-empty strings")
    if len(ids) != len(set(ids)):
        raise ValueError(f"scoring dimension ids must be unique; found {ids!r}")
    weights = [item.get("weight") for item in dimensions]
    if any(
        not isinstance(weight, int) or isinstance(weight, bool) or weight <= 0
        for weight in weights
    ):
        raise ValueError(f"scoring weights must be positive integers; found {weights!r}")
    if sum(weights) != 100:
        raise ValueError(f"scoring weights must total 100; found {sum(weights)}")

    success = contract.get("success_rule")
    if not isinstance(success, dict):
        raise ValueError("success_rule must be an object")
    if success.get("minimum_score") != 80:
        raise _mismatch(
            "personal continuity minimum score",
            expected=80,
            actual=success.get("minimum_score"),
        )
    if success.get("mandatory_boundary_pass") is not True:
        raise ValueError(
            "success_rule.mandatory_boundary_pass must be true; "
            f"found {success.get('mandatory_boundary_pass')!r}"
        )
    mandatory = success.get("mandatory_dimensions")
    if not isinstance(mandatory, list) or any(
        not isinstance(item, str) or not item for item in mandatory
    ):
        raise ValueError("success_rule.mandatory_dimensions must be an array of dimension ids")
    unknown_mandatory = sorted(set(mandatory) - set(ids))
    if unknown_mandatory:
        raise ValueError(
            "success_rule.mandatory_dimensions references unknown scoring dimensions: "
            f"{unknown_mandatory!r}"
        )

    tier_list = tiers.get("tiers")
    if not isinstance(tier_list, list):
        raise ValueError("recovery tier registry invalid: tiers must be an array")
    t5 = next(
        (tier for tier in tier_list if isinstance(tier, dict) and tier.get("id") == "T5"),
        None,
    )
    if not isinstance(t5, dict):
        raise ValueError("T5 recovery tier missing")
    if t5.get("implemented") is not False:
        raise ValueError(
            "T5 must remain unimplemented until an adapter/harness exists; "
            f"found implemented={t5.get('implemented')!r}"
        )
    capabilities = t5.get("capabilities")
    if not isinstance(capabilities, list) or TARGET_CAPABILITY not in capabilities:
        raise ValueError(
            "T5 must declare planned personal_context_reconstruction; "
            f"found capabilities={capabilities!r}"
        )

    examples = mrs.get("examples")
    personal_example = (
        next(
            (
                example
                for example in examples
                if isinstance(example, dict)
                and example.get("requires") == [TARGET_CAPABILITY]
            ),
            None,
        )
        if isinstance(examples, list)
        else None
    )
    expected_example = {"requires": [TARGET_CAPABILITY], "result": None}
    if personal_example != expected_example:
        raise _mismatch(
            "MRS personal_context_reconstruction fail-closed example",
            expected=expected_example,
            actual=personal_example,
        )

    required_boundaries = {
        "PERSONAL_CONTEXT_RECONSTRUCTION != MODEL_INSTANCE_RECONSTRUCTION",
        "RESTORED_STYLE != IDENTITY_PROOF",
        "RESTORED_CONTEXT != HIDDEN_PROVIDER_MEMORY",
        "RECOVERY_SCORE != TRUTH",
        "CAPSULE_HASH_MATCH != CLAIM_AUTHORITY",
        "CLEAN_ROOM_SUCCESS != ORIGINAL_ASSISTANT_CONTINUITY",
    }
    actual_boundaries = contract.get("boundaries")
    if not isinstance(actual_boundaries, list):
        raise ValueError("personal continuity boundaries must be an array")
    if set(actual_boundaries) != required_boundaries:
        raise ValueError(
            "personal continuity boundary set drift: "
            f"missing={sorted(required_boundaries - set(actual_boundaries))!r}, "
            f"unexpected={sorted(set(actual_boundaries) - required_boundaries)!r}"
        )

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
    if not isinstance(report, dict):
        raise ValueError("personal continuity report must be an object")

    contract = load_json(CONTRACT)
    if report.get("protocol") != REPORT_PROTOCOL:
        raise _mismatch(
            "personal continuity report protocol",
            expected=REPORT_PROTOCOL,
            actual=report.get("protocol"),
        )

    trials = contract.get("staged_trials")
    if not isinstance(trials, list) or any(not isinstance(trial, dict) for trial in trials):
        raise ValueError("contract staged_trials must be an array of objects")
    trial_id = report.get("trial_id")
    valid_trials = {trial.get("id") for trial in trials}
    if trial_id not in valid_trials:
        raise ValueError(
            f"unknown personal continuity trial_id {trial_id!r}; "
            f"expected one of {sorted(valid_trials)!r}"
        )

    scores = report.get("scores")
    if not isinstance(scores, dict):
        raise ValueError("report scores must be an object")
    boundaries_passed = report.get("boundaries_passed")
    if not isinstance(boundaries_passed, bool):
        raise ValueError(
            "boundaries_passed must be boolean; "
            f"found {boundaries_passed!r}"
        )

    dimensions = contract.get("scoring_dimensions")
    if not isinstance(dimensions, list) or any(not isinstance(item, dict) for item in dimensions):
        raise ValueError("contract scoring_dimensions must be an array of objects")

    required_ids = [dimension.get("id") for dimension in dimensions]
    for dimension_id in required_ids:
        if not isinstance(dimension_id, str) or not dimension_id:
            raise ValueError("contract contains an invalid scoring dimension id")
        if dimension_id not in scores:
            raise ValueError(f"missing score for dimension {dimension_id}")

    total = 0.0
    dimension_results = {}
    for dimension in dimensions:
        dimension_id = dimension["id"]
        value = scores[dimension_id]
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not 0 <= float(value) <= 1
        ):
            raise ValueError(
                f"score {dimension_id} must be numeric in 0..1; found {value!r}"
            )
        weighted = float(value) * dimension["weight"]
        total += weighted
        dimension_results[dimension_id] = {
            "score": float(value),
            "weight": dimension["weight"],
            "weighted_points": weighted,
        }

    success = contract.get("success_rule")
    if not isinstance(success, dict):
        raise ValueError("contract success_rule must be an object")
    mandatory = success.get("mandatory_dimensions")
    if not isinstance(mandatory, list) or any(item not in scores for item in mandatory):
        missing = [item for item in mandatory or [] if item not in scores]
        raise ValueError(
            "mandatory scoring dimensions are invalid or missing from report: "
            f"{missing!r}"
        )

    mandatory_pass = all(float(scores[item]) >= 0.8 for item in mandatory)
    minimum_score = success.get("minimum_score")
    if not isinstance(minimum_score, (int, float)) or isinstance(minimum_score, bool):
        raise ValueError(f"contract minimum_score must be numeric; found {minimum_score!r}")

    passed = total >= float(minimum_score) and boundaries_passed and mandatory_pass
    return {
        "protocol": SCORE_PROTOCOL,
        "trial_id": trial_id,
        "score": round(total, 6),
        "minimum_score": minimum_score,
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
