#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Validate QSOL-ARK cultural records and reconstruction tasks."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "ai" / "cultural-artifact-policy.json"
INDEX = ROOT / "culture" / "index.json"

ALLOWED_EVIDENCE = {
    "official_metadata","historical_claim","fictional_world_claim","first_person_position",
    "third_party_reference","derived_interpretation","satire","joke","unknown"
}
ALLOWED_RECORD_TYPES = {"cultural_artifact", "authored_cultural_position"}

def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def require(condition: bool, code: str) -> None:
    if not condition:
        raise ValueError(code)

def safe_repo_path(value: object, prefix: str) -> Path:
    require(isinstance(value, str) and value, "ARK_CULTURE_PATH_INVALID")
    path = Path(value)
    require(not path.is_absolute() and ".." not in path.parts, "ARK_CULTURE_PATH_INVALID")
    require(path.parts and path.parts[0] == prefix, "ARK_CULTURE_PATH_INVALID")
    full = ROOT / path
    require(full.exists() and full.is_file(), "ARK_CULTURE_PATH_MISSING")
    return full

def validate_policy(policy: dict) -> None:
    require(policy.get("protocol") == "QSOL-ARK", "ARK_CULTURE_POLICY_INVALID")
    require(set(policy.get("record_types", [])) == ALLOWED_RECORD_TYPES, "ARK_CULTURE_POLICY_INVALID")
    require(set(policy.get("evidence_classes", [])) == ALLOWED_EVIDENCE, "ARK_CULTURE_POLICY_INVALID")
    rules = set(policy.get("rules", []))
    required = {
        "cultural_artifact_is_not_historical_claim",
        "fictional_world_claim_is_not_real_world_fact",
        "first_person_position_is_authoritative_only_for_the_authors_stated_position",
        "named_entity_opinion_is_not_objective_fact_about_the_named_entity",
        "permission_is_not_endorsement",
        "applicable_license_terms_govern_reuse_permissions",
        "third_party_source_bytes_require_resolved_license_evidence",
        "unavailable_source_is_not_contradicted_source",
        "derived_interpretation_must_remain_labelled_derived",
        "cultural_significance_does_not_upgrade_folklore_or_fiction_to_fact",
    }
    require(required.issubset(rules), "ARK_CULTURE_POLICY_INVALID")
    require(policy.get("copyright", {}).get("full_script_copy_without_permission") == "forbidden",
            "ARK_CULTURE_COPYRIGHT_POLICY_INVALID")

def validate_ouroboros(record: dict) -> None:
    require(record.get("record_type") == "cultural_artifact", "ARK_CULTURE_RECORD_TYPE_INVALID")
    require(record.get("id") == "culture.television.red_dwarf.ouroboros", "ARK_CULTURE_RECORD_ID_INVALID")
    rights = record.get("rights", {})
    require(rights.get("third_party_copyright") is True, "ARK_CULTURE_RIGHTS_INVALID")
    require(rights.get("source_bytes_copied") is False, "ARK_THIRD_PARTY_BYTES_WITHOUT_RESOLVED_LICENSE")
    require(rights.get("script_text_copied") is False, "ARK_THIRD_PARTY_SCRIPT_COPY_FORBIDDEN")
    require(rights.get("license_status") == "not_authorized_for_copy", "ARK_CULTURE_RIGHTS_INVALID")
    boundary = record.get("fiction_boundary", {})
    require(boundary.get("narrative_events_are") == "fictional_world_claims", "ARK_FICTION_BOUNDARY_INVALID")
    require(boundary.get("narrative_events_are_historical_evidence") is False, "ARK_FICTION_PROMOTED_TO_HISTORY")
    require(boundary.get("production_metadata_is_real_world_history") is True, "ARK_FICTION_BOUNDARY_INVALID")
    metadata = record.get("real_world_metadata", {})
    require(metadata == {
        "series": 7,
        "episode": 3,
        "first_broadcast": "1997-01-31",
        "written_by": ["Doug Naylor"],
        "directed_by": ["Ed Bye"],
    }, "ARK_CULTURE_PRODUCTION_METADATA_INVALID")
    sources = record.get("sources", [])
    require(isinstance(sources, list) and len(sources) >= 1, "ARK_CULTURE_SOURCE_INVALID")
    official = [s for s in sources if s.get("role") == "official_metadata"]
    require(len(official) == 1 and official[0].get("verification_status") == "retrieved_2026-08-17",
            "ARK_CULTURE_OFFICIAL_SOURCE_REQUIRED")
    transcript = [s for s in sources if s.get("id") == "source.cervenytrpaslik.ouroboros_transcript"]
    require(len(transcript) == 1, "ARK_CULTURE_TRANSCRIPT_REFERENCE_MISSING")
    require(transcript[0].get("verification_status") == "unavailable_at_ingest",
            "ARK_CULTURE_TRANSCRIPT_STATUS_INVALID")
    require(transcript[0].get("source_bytes_copied") is False, "ARK_THIRD_PARTY_SCRIPT_COPY_FORBIDDEN")

def validate_position(record: dict) -> None:
    require(record.get("record_type") == "authored_cultural_position", "ARK_CULTURE_RECORD_TYPE_INVALID")
    require(record.get("id") == "culture.qsol.open_source.permission_not_endorsement",
            "ARK_CULTURE_RECORD_ID_INVALID")
    require(record.get("author") == {"name": "Trent Slade", "github": "EmergentMonk"},
            "ARK_CULTURE_AUTHOR_INVALID")
    require(record.get("epistemic_status") == "first_person_position",
            "ARK_CULTURE_POSITION_CLASS_INVALID")
    provenance = record.get("provenance", {})
    require(provenance.get("source_kind") == "direct_maintainer_contribution",
            "ARK_CULTURE_POSITION_PROVENANCE_INVALID")
    require(provenance.get("public_release_intent") == "explicit",
            "ARK_CULTURE_POSITION_PROVENANCE_INVALID")
    normalized = record.get("normalized_position", {})
    require(normalized.get("permission_is_endorsement") is False,
            "ARK_PERMISSION_ENDORSEMENT_BOUNDARY_INVALID")
    require(normalized.get("liking_a_product_implies_endorsement_of_its_company") is False,
            "ARK_PERMISSION_ENDORSEMENT_BOUNDARY_INVALID")
    license_effect = record.get("license_effect", {})
    require(license_effect.get("applicable_repository_licenses_remain_governing") is True,
            "ARK_CULTURE_LICENSE_BOUNDARY_INVALID")
    require(license_effect.get("statement_creates_additional_exclusive_license_restriction") is False,
            "ARK_CULTURE_LICENSE_BOUNDARY_INVALID")
    require(license_effect.get("reuse_permission_depends_on_personal_approval") is False,
            "ARK_CULTURE_LICENSE_BOUNDARY_INVALID")
    boundary = record.get("claim_boundary", {})
    require(boundary.get("objective_claims_about_named_entities_verified") is False,
            "ARK_OPINION_PROMOTED_TO_OBJECTIVE_FACT")
    require("the authors stated opinion and principle" == boundary.get("authoritative_as"),
            "ARK_CULTURE_POSITION_CLASS_INVALID")
    require("permission_is_not_endorsement" in record.get("cultural_principles", []),
            "ARK_PERMISSION_ENDORSEMENT_BOUNDARY_INVALID")
    require(isinstance(record.get("verbatim_statement"), str) and record["verbatim_statement"].strip(),
            "ARK_CULTURE_QUOTATION_MISSING")

def validate_record(record: dict) -> None:
    require(record.get("type") == "qsol-ark-cultural-record", "ARK_CULTURE_RECORD_INVALID")
    require(record.get("protocol") == "QSOL-ARK", "ARK_CULTURE_RECORD_INVALID")
    require(record.get("schema_version") == "0.1.0", "ARK_CULTURE_RECORD_INVALID")
    rt = record.get("record_type")
    require(rt in ALLOWED_RECORD_TYPES, "ARK_CULTURE_RECORD_TYPE_INVALID")
    if record.get("id") == "culture.television.red_dwarf.ouroboros":
        validate_ouroboros(record)
    elif record.get("id") == "culture.qsol.open_source.permission_not_endorsement":
        validate_position(record)
    else:
        raise ValueError("ARK_CULTURE_RECORD_ID_UNKNOWN")

def validate_task(task: dict, known_records: set[str]) -> None:
    require(task.get("type") == "qsol-ark-cultural-recovery-task", "ARK_CULTURE_TASK_INVALID")
    require(task.get("protocol") == "QSOL-ARK", "ARK_CULTURE_TASK_INVALID")
    require(task.get("record_id") in known_records, "ARK_CULTURE_TASK_RECORD_UNKNOWN")
    questions = task.get("questions")
    require(isinstance(questions, list) and questions, "ARK_CULTURE_TASK_INVALID")
    ids = [q.get("id") for q in questions if isinstance(q, dict)]
    require(len(ids) == len(questions) == len(set(ids)), "ARK_CULTURE_TASK_INVALID")
    for q in questions:
        require(isinstance(q.get("prompt"), str) and q["prompt"], "ARK_CULTURE_TASK_INVALID")
        require(q.get("expected") in {"no","yes","real_world_production_metadata","fictional_world_claim"},
                "ARK_CULTURE_TASK_EXPECTATION_INVALID")

def validate() -> None:
    policy = load(POLICY)
    index = load(INDEX)
    validate_policy(policy)
    require(index.get("type") == "qsol-ark-culture-index", "ARK_CULTURE_INDEX_INVALID")
    require(index.get("protocol") == "QSOL-ARK", "ARK_CULTURE_INDEX_INVALID")
    records = index.get("records")
    tasks = index.get("tasks")
    require(isinstance(records, list) and len(records) == 2, "ARK_CULTURE_INDEX_INVALID")
    require(isinstance(tasks, list) and len(tasks) == 2, "ARK_CULTURE_INDEX_INVALID")
    record_ids = [r.get("id") for r in records if isinstance(r, dict)]
    task_ids = [t.get("id") for t in tasks if isinstance(t, dict)]
    require(len(record_ids) == len(records) == len(set(record_ids)), "ARK_CULTURE_INDEX_INVALID")
    require(len(task_ids) == len(tasks) == len(set(task_ids)), "ARK_CULTURE_INDEX_INVALID")
    known = set(record_ids)
    for entry in records:
        require(entry.get("record_type") in ALLOWED_RECORD_TYPES, "ARK_CULTURE_INDEX_INVALID")
        record = load(safe_repo_path(entry.get("path"), "culture"))
        require(record.get("id") == entry.get("id"), "ARK_CULTURE_INDEX_BINDING_INVALID")
        require(record.get("record_type") == entry.get("record_type"), "ARK_CULTURE_INDEX_BINDING_INVALID")
        validate_record(record)
    for entry in tasks:
        task = load(safe_repo_path(entry.get("path"), "culture"))
        require(task.get("id") == entry.get("id"), "ARK_CULTURE_INDEX_BINDING_INVALID")
        require(task.get("record_id") == entry.get("record_id"), "ARK_CULTURE_INDEX_BINDING_INVALID")
        validate_task(task, known)
    print(f"ARK_CULTURE_OK records={len(records)} tasks={len(tasks)}")

def main(argv: list[str]) -> int:
    try:
        validate()
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
