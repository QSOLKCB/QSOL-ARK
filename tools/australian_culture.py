#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Validate QSOL-ARK Australian governance and irreverence cultural records."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "ai" / "australian-governance-policy.json"
INDEX_PATH = ROOT / "culture" / "australia" / "index.json"
SOURCES_PATH = ROOT / "culture" / "australia" / "sources.json"
RECORDS_PATH = ROOT / "culture" / "australia" / "records.json"
TASKS_PATH = ROOT / "culture" / "australia" / "recovery-tasks.json"
MANIFEST_PATH = ROOT / "manifest.json"
BOOTSTRAP_PATH = ROOT / "ai" / "bootstrap.json"
MANIFEST_SCHEMA_PATH = ROOT / "schema" / "ark-manifest.schema.json"
VERSION = "1.0.0"

RECORD_IDS = {
    "culture.australia.australian_informal_governance",
    "culture.australia.irreverent_fatalism",
    "culture.australia.breaker_morant_history_and_film",
    "culture.australia.bob_hawke_irreverence",
}

EXPECTED_TASKS = {
    "task.australia.informal_governance.boundary": {
        "record_id": "culture.australia.australian_informal_governance",
        "questions": [
            {"id": "aus-gov-01", "prompt": "Does the proposed Australian humour-as-governance pattern have formal legal, constitutional, or administrative authority?", "expected": "no"},
            {"id": "aus-gov-02", "prompt": "Does mocking authority establish that governance or legitimate authority is absent?", "expected": "no"},
            {"id": "aus-gov-03", "prompt": "Is The Antipodean Jester stored as a peer-reviewed established sociological result?", "expected": "preprint_not_peer_reviewed"},
            {"id": "aus-gov-04", "prompt": "What kind of claim is humour-as-informal-governance in this ARK record?", "expected": "proposed_cultural_framework"},
        ],
    },
    "task.australia.irreverent_fatalism.boundary": {
        "record_id": "culture.australia.irreverent_fatalism",
        "questions": [
            {"id": "aus-fat-01", "prompt": "Does fatalistic humour establish nihilism or disregard for life?", "expected": "no"},
            {"id": "aus-fat-02", "prompt": "Does outward humour under danger or grief prove that the person felt no fear or grief?", "expected": "no"},
            {"id": "aus-fat-03", "prompt": "May ARK interpret humour under constraint as retained agency when the interpretation remains explicitly derived and contextual?", "expected": "yes"},
        ],
    },
    "task.australia.breaker_morant.boundary": {
        "record_id": "culture.australia.breaker_morant_history_and_film",
        "questions": [
            {"id": "aus-morant-01", "prompt": "What is the evidence class of the stored words Shoot straight, you bastards!?", "expected": "film_dialogue_rights_aware_short_quotation"},
            {"id": "aus-morant-02", "prompt": "May the film dialogue be treated as primary historical testimony of Morant's exact final words?", "expected": "no"},
            {"id": "aus-morant-03", "prompt": "Does cultural admiration or folk-hero status historically exonerate Morant?", "expected": "no"},
            {"id": "aus-morant-04", "prompt": "Which source class governs the court-martial, conviction, and execution metadata in this record?", "expected": "official_historical_metadata"},
        ],
    },
    "task.australia.bob_hawke.boundary": {
        "record_id": "culture.australia.bob_hawke_irreverence",
        "questions": [
            {"id": "aus-hawke-01", "prompt": "Does Hawke's larrikin public persona constitute formal prime-ministerial or constitutional authority?", "expected": "no"},
            {"id": "aus-hawke-02", "prompt": "Does this record preserve direct Bob Hawke quotations?", "expected": "no_paraphrase_only"},
            {"id": "aus-hawke-03", "prompt": "Can a larrikin public persona coexist with gentleness, grief response, and formal consensus governance?", "expected": "yes"},
        ],
    },
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(ok: bool, code: str) -> None:
    if not ok:
        raise ValueError(code)


def require_exact_keys(obj: object, keys: set[str], code: str) -> dict:
    require(isinstance(obj, dict) and set(obj) == keys, code)
    return obj


def text(value: object, code: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), code)
    return value


def texts(value: object, code: str, *, allow_empty: bool = False) -> list[str]:
    require(isinstance(value, list), code)
    require(allow_empty or bool(value), code)
    require(all(isinstance(item, str) and item.strip() for item in value), code)
    require(len(value) == len(set(value)), code)
    return value


def safe_path(value: object, code: str) -> Path:
    raw = text(value, code)
    path = Path(raw)
    require(not path.is_absolute() and ".." not in path.parts, code)
    full = ROOT / path
    require(full.is_file(), code)
    return full


def validate_policy(policy: dict) -> None:
    require(policy.get("type") == "qsol-ark-australian-governance-policy", "ARK_AUS_POLICY_INVALID")
    require(policy.get("protocol") == "QSOL-ARK" and policy.get("schema_version") == VERSION,
            "ARK_AUS_POLICY_INVALID")

    record_types = texts(policy.get("record_types"), "ARK_AUS_RECORD_TYPES_INVALID")
    require({"cultural_pattern", "historical_cultural_bundle", "public_persona_context"}.issubset(record_types),
            "ARK_AUS_RECORD_TYPES_INVALID")
    evidence_classes = texts(policy.get("evidence_classes"), "ARK_AUS_EVIDENCE_CLASSES_INVALID")

    schema = require_exact_keys(
        policy.get("source_schema"),
        {"required_fields", "optional_metadata_fields", "allowed_visibility", "allowed_roles", "allowed_license_status", "allowed_canonical_status", "byte_import_allowed"},
        "ARK_AUS_SOURCE_POLICY_INVALID",
    )
    required = set(texts(schema["required_fields"], "ARK_AUS_SOURCE_POLICY_INVALID"))
    optional = set(texts(schema["optional_metadata_fields"], "ARK_AUS_SOURCE_POLICY_INVALID", allow_empty=True))
    require(required == {"url", "role", "visibility", "license_status", "canonical_status", "byte_import_allowed", "supports"},
            "ARK_AUS_SOURCE_POLICY_INVALID")
    require(not required.intersection(optional), "ARK_AUS_SOURCE_POLICY_INVALID")
    for key in ("allowed_visibility", "allowed_roles", "allowed_license_status", "allowed_canonical_status"):
        texts(schema[key], "ARK_AUS_SOURCE_POLICY_INVALID")
    require(schema["byte_import_allowed"] is False, "ARK_AUS_SOURCE_POLICY_INVALID")

    role_policy = policy.get("evidence_role_policy")
    require(isinstance(role_policy, dict) and set(role_policy) == set(evidence_classes),
            "ARK_AUS_EVIDENCE_ROLE_POLICY_INVALID")
    allowed_roles = set(schema["allowed_roles"])
    for evidence_class, roles in role_policy.items():
        declared = set(texts(roles, "ARK_AUS_EVIDENCE_ROLE_POLICY_INVALID", allow_empty=True))
        require(declared.issubset(allowed_roles), "ARK_AUS_EVIDENCE_ROLE_POLICY_INVALID")
        if evidence_class != "unknown":
            require(bool(declared), "ARK_AUS_EVIDENCE_ROLE_POLICY_INVALID")

    preprint = require_exact_keys(
        policy.get("preprint_policy"),
        {"required_publication_state", "required_peer_reviewed", "required_label", "authored_preprint_license", "preprint_framework_is_established_fact"},
        "ARK_AUS_PREPRINT_POLICY_INVALID",
    )
    require(preprint == {
        "required_publication_state": "preprint",
        "required_peer_reviewed": False,
        "required_label": "preprint / not peer-reviewed",
        "authored_preprint_license": "CC-BY-4.0",
        "preprint_framework_is_established_fact": False,
    }, "ARK_AUS_PREPRINT_POLICY_INVALID")

    quote = require_exact_keys(
        policy.get("quotation_policy"),
        {"exact_words_require_verifiable_source", "maximum_stored_words", "full_script_copy_without_permission", "audiovisual_bytes_copied_by_default", "film_dialogue_is_primary_historical_testimony"},
        "ARK_AUS_QUOTE_POLICY_INVALID",
    )
    require(quote["exact_words_require_verifiable_source"] is True, "ARK_AUS_QUOTE_POLICY_INVALID")
    require(isinstance(quote["maximum_stored_words"], int) and 1 <= quote["maximum_stored_words"] <= 12,
            "ARK_AUS_QUOTE_POLICY_INVALID")
    require(quote["full_script_copy_without_permission"] is False, "ARK_AUS_QUOTE_POLICY_INVALID")
    require(quote["audiovisual_bytes_copied_by_default"] is False, "ARK_AUS_QUOTE_POLICY_INVALID")
    require(quote["film_dialogue_is_primary_historical_testimony"] is False,
            "ARK_AUS_FILM_PROMOTED_TO_HISTORY")

    require(policy.get("formal_authority_boundary") == {
        "cultural_pattern_has_formal_legal_force": False,
        "cultural_pattern_can_replace_constitution_or_legislation": False,
        "formal_authority_requires_official_legal_source": True,
    }, "ARK_AUS_FORMAL_AUTHORITY_BOUNDARY_INVALID")
    require(policy.get("fatalism_boundary") == {
        "humour_under_constraint_proves_nihilism": False,
        "humour_under_constraint_proves_absence_of_grief": False,
        "humour_under_constraint_proves_absence_of_fear": False,
        "humour_under_constraint_proves_disregard_for_life": False,
        "retained_agency_is_allowed_as_derived_interpretation": True,
    }, "ARK_AUS_FATALISM_BOUNDARY_INVALID")

    uncertainty = policy.get("uncertainty_registry")
    require(isinstance(uncertainty, dict) and uncertainty, "ARK_AUS_UNCERTAINTY_POLICY_INVALID")
    seen_records = set()
    for status, entry in uncertainty.items():
        text(status, "ARK_AUS_UNCERTAINTY_POLICY_INVALID")
        require_exact_keys(entry, {"record_id", "note"}, "ARK_AUS_UNCERTAINTY_POLICY_INVALID")
        require(entry["record_id"] in RECORD_IDS and entry["record_id"] not in seen_records,
                "ARK_AUS_UNCERTAINTY_POLICY_INVALID")
        seen_records.add(entry["record_id"])
        text(entry["note"], "ARK_AUS_UNCERTAINTY_POLICY_INVALID")
    require(seen_records == RECORD_IDS, "ARK_AUS_UNCERTAINTY_POLICY_INVALID")

    invariants = texts(policy.get("canonical_invariants"), "ARK_AUS_INVARIANTS_INVALID")
    require(all(" != " in invariant for invariant in invariants), "ARK_AUS_INVARIANTS_INVALID")

    require(policy.get("task_binding") == {
        "mode": "record_specific_exact",
        "bind_fields": ["id", "prompt", "expected"],
    }, "ARK_AUS_TASK_BINDING_INVALID")


def validate_sources(doc: dict, policy: dict) -> dict[str, dict]:
    require_exact_keys(doc, {"type", "protocol", "schema_version", "sources"}, "ARK_AUS_SOURCES_INVALID")
    require(doc["type"] == "qsol-ark-australian-governance-source-catalog", "ARK_AUS_SOURCES_INVALID")
    require(doc["protocol"] == "QSOL-ARK" and doc["schema_version"] == VERSION, "ARK_AUS_SOURCES_INVALID")
    sources = doc["sources"]
    require(isinstance(sources, dict) and len(sources) >= 10, "ARK_AUS_SOURCE_CATALOG_INVALID")

    schema = policy["source_schema"]
    required = set(schema["required_fields"])
    permitted = required | set(schema["optional_metadata_fields"])
    allowed_roles = set(schema["allowed_roles"])
    allowed_visibility = set(schema["allowed_visibility"])
    allowed_licenses = set(schema["allowed_license_status"])
    allowed_canonical = set(schema["allowed_canonical_status"])

    for sid, source in sources.items():
        text(sid, "ARK_AUS_SOURCE_ID_INVALID")
        require(isinstance(source, dict), "ARK_AUS_SOURCE_INVALID")
        require(required.issubset(source), "ARK_AUS_SOURCE_STATE_INCOMPLETE")
        require(set(source).issubset(permitted), "ARK_AUS_SOURCE_UNDECLARED_FIELD")
        require(source["url"].startswith("https://"), "ARK_AUS_SOURCE_URL_INVALID")
        require(source["role"] in allowed_roles, "ARK_AUS_SOURCE_ROLE_INVALID")
        require(source["visibility"] in allowed_visibility, "ARK_AUS_SOURCE_VISIBILITY_INVALID")
        require(source["license_status"] in allowed_licenses, "ARK_AUS_SOURCE_LICENSE_INVALID")
        require(source["canonical_status"] in allowed_canonical, "ARK_AUS_SOURCE_CANONICAL_STATUS_INVALID")
        require(source["byte_import_allowed"] is schema["byte_import_allowed"], "ARK_AUS_THIRD_PARTY_BYTES_FORBIDDEN")
        texts(source["supports"], "ARK_AUS_SOURCE_SUPPORTS_INVALID")
        if "retrieval_status" in source:
            require(source["retrieval_status"].startswith("retrieved_"), "ARK_AUS_SOURCE_RETRIEVAL_STATUS_INVALID")

    preprint = sources.get("src.antipodean_jester", {})
    require(preprint.get("role") == "author_preprint", "ARK_AUS_PREPRINT_SOURCE_INVALID")
    require(preprint.get("title") == "The Antipodean Jester: Australian Humor as Informal Governance in a Comparative Sociological Framework",
            "ARK_AUS_PREPRINT_SOURCE_INVALID")
    require(preprint.get("author") == "Trent Slade", "ARK_AUS_PREPRINT_SOURCE_INVALID")
    require(preprint.get("publication_platform") == "Authorea Preprints", "ARK_AUS_PREPRINT_SOURCE_INVALID")
    require(preprint.get("publication_date") == "2026-01-07", "ARK_AUS_PREPRINT_SOURCE_INVALID")
    require(preprint.get("publication_state") == policy["preprint_policy"]["required_publication_state"],
            "ARK_AUS_PREPRINT_STATE_PROMOTED")
    require(preprint.get("peer_reviewed") is policy["preprint_policy"]["required_peer_reviewed"],
            "ARK_AUS_PREPRINT_PEER_REVIEW_PROMOTED")
    require(preprint.get("license_status") == policy["preprint_policy"]["authored_preprint_license"],
            "ARK_AUS_PREPRINT_LICENSE_INVALID")
    require(preprint.get("version") == "v1" and preprint.get("doi") == "10.22541/au.176780580.02987307/v1",
            "ARK_AUS_PREPRINT_IDENTITY_INVALID")

    require(sources.get("src.legislation.constitution", {}).get("role") == "official_legal_authority",
            "ARK_AUS_FORMAL_AUTHORITY_SOURCE_INVALID")
    require(sources.get("src.awm.breaker_morant", {}).get("role") == "official_historical_metadata",
            "ARK_AUS_MORANT_HISTORY_SOURCE_INVALID")
    require(sources.get("src.screen_australia.breaker_morant", {}).get("role") == "official_production_metadata",
            "ARK_AUS_MORANT_FILM_SOURCE_INVALID")
    require(sources.get("src.aso.breaker_morant_clip3", {}).get("role") == "official_audiovisual_heritage_transcript",
            "ARK_AUS_MORANT_QUOTE_SOURCE_INVALID")
    return sources


def validate_evidence(item: dict, sources: dict[str, dict], policy: dict) -> None:
    require_exact_keys(item, {"class", "source_ids", "supports"}, "ARK_AUS_EVIDENCE_SHAPE_INVALID")
    evidence_class = text(item["class"], "ARK_AUS_EVIDENCE_CLASS_INVALID")
    require(evidence_class in policy["evidence_classes"], "ARK_AUS_EVIDENCE_CLASS_INVALID")
    source_ids = texts(item["source_ids"], "ARK_AUS_EVIDENCE_SOURCE_IDS_INVALID")
    supports = texts(item["supports"], "ARK_AUS_EVIDENCE_SUPPORTS_INVALID")
    require(all(sid in sources for sid in source_ids), "ARK_AUS_EVIDENCE_SOURCE_UNKNOWN")

    declared_supports = set()
    roles = set()
    for sid in source_ids:
        declared_supports.update(sources[sid]["supports"])
        roles.add(sources[sid]["role"])
    require(set(supports).issubset(declared_supports), "ARK_AUS_EVIDENCE_SUPPORT_NOT_SOURCE_BOUND")

    allowed_roles = set(policy["evidence_role_policy"][evidence_class])
    require(bool(allowed_roles) and roles.issubset(allowed_roles), "ARK_AUS_EVIDENCE_ROLE_MISMATCH")
    if evidence_class == "proposed_sociological_framework":
        require(all(sources[sid].get("peer_reviewed") is False for sid in source_ids),
                "ARK_AUS_PREPRINT_PEER_REVIEW_PROMOTED")


def validate_common_record(record: dict, sources: dict[str, dict], policy: dict) -> None:
    require(record.get("id") in RECORD_IDS, "ARK_AUS_RECORD_ID_INVALID")
    require(record.get("record_type") in policy["record_types"], "ARK_AUS_RECORD_TYPE_INVALID")
    text(record.get("title"), "ARK_AUS_RECORD_TITLE_INVALID")
    evidence = record.get("evidence")
    require(isinstance(evidence, list) and evidence, "ARK_AUS_EVIDENCE_INVALID")
    for item in evidence:
        validate_evidence(item, sources, policy)
    target = require_exact_keys(record.get("reconstruction_target"), {"identify", "avoid"},
                                "ARK_AUS_RECONSTRUCTION_TARGET_INVALID")
    texts(target["identify"], "ARK_AUS_RECONSTRUCTION_TARGET_INVALID")
    texts(target["avoid"], "ARK_AUS_RECONSTRUCTION_TARGET_INVALID")
    uncertainty = require_exact_keys(record.get("uncertainty"), {"status", "note"}, "ARK_AUS_UNCERTAINTY_INVALID")
    status = text(uncertainty["status"], "ARK_AUS_UNCERTAINTY_INVALID")
    registry = policy["uncertainty_registry"]
    require(status in registry, "ARK_AUS_UNCERTAINTY_STATUS_UNKNOWN")
    expected = registry[status]
    require(expected["record_id"] == record["id"] and uncertainty["note"] == expected["note"],
            "ARK_AUS_UNCERTAINTY_BOUNDARY_DRIFT")


def validate_informal_governance(record: dict, sources: dict[str, dict], policy: dict) -> None:
    require_exact_keys(record, {"id", "record_type", "title", "scope", "pattern", "evidence", "boundaries", "reconstruction_target", "uncertainty"},
                       "ARK_AUS_RECORD_SHAPE_INVALID")
    validate_common_record(record, sources, policy)
    require(record["record_type"] == "cultural_pattern", "ARK_AUS_RECORD_TYPE_INVALID")
    scope = require_exact_keys(record["scope"], {"jurisdiction", "status", "formal_authority"}, "ARK_AUS_SCOPE_INVALID")
    require(scope == {"jurisdiction": "Australia", "status": "proposed_cultural_pattern_not_universal_trait", "formal_authority": False},
            "ARK_AUS_SCOPE_INVALID")
    pattern = require_exact_keys(record["pattern"], {"canonical_terms", "social_functions", "interpretation_status", "cautions"},
                                 "ARK_AUS_PATTERN_INVALID")
    required_terms = {"larrikinism", "taking the piss", "anti-pretension", "egalitarian correction", "deadpan", "self-deprecation", "authority mockery"}
    require(set(texts(pattern["canonical_terms"], "ARK_AUS_PATTERN_INVALID")) == required_terms,
            "ARK_AUS_PATTERN_TERMS_INVALID")
    texts(pattern["social_functions"], "ARK_AUS_PATTERN_INVALID")
    texts(pattern["cautions"], "ARK_AUS_PATTERN_INVALID")
    require(pattern["interpretation_status"] == "proposed_sociological_framework_with_secondary_corroboration",
            "ARK_AUS_FRAMEWORK_PROMOTED")
    require(record["boundaries"] == {
        "humour_as_governance_is_formal_legal_authority": False,
        "mocking_authority_means_governance_is_absent": False,
        "irreverence_means_ignorance": False,
        "pattern_is_universal_australian_trait": False,
    }, "ARK_AUS_GOVERNANCE_BOUNDARY_INVALID")
    cited = {sid for item in record["evidence"] for sid in item["source_ids"]}
    require("src.antipodean_jester" in cited and "src.legislation.constitution" in cited,
            "ARK_AUS_GOVERNANCE_PROVENANCE_INCOMPLETE")


def validate_irreverent_fatalism(record: dict, sources: dict[str, dict], policy: dict) -> None:
    require_exact_keys(record, {"id", "record_type", "title", "scope", "pattern", "evidence", "boundaries", "reconstruction_target", "uncertainty"},
                       "ARK_AUS_RECORD_SHAPE_INVALID")
    validate_common_record(record, sources, policy)
    require(record["record_type"] == "cultural_pattern", "ARK_AUS_RECORD_TYPE_INVALID")
    require(record["scope"] == {
        "jurisdiction": "Australia",
        "status": "derived_cultural_interpretation_not_psychological_diagnosis",
        "formal_authority": False,
    }, "ARK_AUS_FATALISM_SCOPE_INVALID")
    pattern = require_exact_keys(record["pattern"], {"canonical_terms", "social_functions", "interpretation_status", "cautions"},
                                 "ARK_AUS_PATTERN_INVALID")
    require("irreverent fatalism" in texts(pattern["canonical_terms"], "ARK_AUS_PATTERN_INVALID"),
            "ARK_AUS_FATALISM_TERM_MISSING")
    texts(pattern["social_functions"], "ARK_AUS_PATTERN_INVALID")
    texts(pattern["cautions"], "ARK_AUS_PATTERN_INVALID")
    require(pattern["interpretation_status"] == "derived_interpretation", "ARK_AUS_FATALISM_PROMOTED")
    require(record["boundaries"] == {
        "fatalistic_humour_is_nihilism": False,
        "humour_proves_absence_of_grief": False,
        "humour_proves_absence_of_fear": False,
        "humour_proves_disregard_for_life": False,
        "retained_agency_is_derived_interpretation": True,
    }, "ARK_AUS_FATALISM_BOUNDARY_INVALID")


def validate_morant(record: dict, sources: dict[str, dict], policy: dict) -> None:
    require_exact_keys(record, {"id", "record_type", "title", "historical_person", "film_representation", "quotation", "evidence", "boundaries", "reconstruction_target", "uncertainty"},
                       "ARK_AUS_RECORD_SHAPE_INVALID")
    validate_common_record(record, sources, policy)
    require(record["record_type"] == "historical_cultural_bundle", "ARK_AUS_RECORD_TYPE_INVALID")
    person = require_exact_keys(record["historical_person"], {"name", "historical_source_id", "court_martial_recorded", "convictions_recorded", "execution_date", "historical_exoneration_claimed"},
                                "ARK_AUS_MORANT_HISTORY_INVALID")
    require(person["name"] == "Henry Harbord (Harry) 'The Breaker' Morant", "ARK_AUS_MORANT_IDENTITY_INVALID")
    require(person["historical_source_id"] == "src.awm.breaker_morant", "ARK_AUS_MORANT_HISTORY_SOURCE_INVALID")
    require("morant_identity" in sources[person["historical_source_id"]]["supports"], "ARK_AUS_MORANT_IDENTITY_NOT_SOURCE_BOUND")
    require(person["court_martial_recorded"] is True and person["convictions_recorded"] is True,
            "ARK_AUS_MORANT_HISTORY_INVALID")
    require(person["execution_date"] == "1902-02-27", "ARK_AUS_MORANT_HISTORY_INVALID")
    require(person["historical_exoneration_claimed"] is False, "ARK_AUS_MORANT_EXONERATION_PROMOTED")

    film = require_exact_keys(record["film_representation"], {"title", "completion_year", "cultural_circulation", "director", "production_source_id", "dialogue_source_id", "representation_status"},
                              "ARK_AUS_MORANT_FILM_INVALID")
    require(film["title"] == "Breaker Morant" and film["completion_year"] == 1979 and film["director"] == "Bruce Beresford",
            "ARK_AUS_MORANT_FILM_INVALID")
    require(film["production_source_id"] == "src.screen_australia.breaker_morant",
            "ARK_AUS_MORANT_FILM_SOURCE_INVALID")
    production_supports = set(sources[film["production_source_id"]]["supports"])
    require({"breaker_morant_feature_film", "completion_year_1979", "director_bruce_beresford"}.issubset(production_supports),
            "ARK_AUS_MORANT_FILM_NOT_SOURCE_BOUND")
    circulation = require_exact_keys(film["cultural_circulation"], {"year", "status", "source_id", "support"},
                                     "ARK_AUS_MORANT_CIRCULATION_INVALID")
    require(circulation == {
        "year": 1980,
        "status": "documented_festival_circulation",
        "source_id": "src.screen_australia.breaker_morant",
        "support": "cannes_film_festival_1980",
    }, "ARK_AUS_MORANT_CIRCULATION_INVALID")
    require(circulation["support"] in sources[circulation["source_id"]]["supports"],
            "ARK_AUS_MORANT_CIRCULATION_NOT_SOURCE_BOUND")
    require(film["dialogue_source_id"] == "src.aso.breaker_morant_clip3",
            "ARK_AUS_MORANT_QUOTE_SOURCE_INVALID")
    require(film["representation_status"] == "dramatic_cultural_representation_not_primary_historical_record",
            "ARK_AUS_MORANT_FILM_INVALID")

    quote = require_exact_keys(record["quotation"], {"text", "source_id", "context", "rights_mode", "historical_primary_testimony", "full_script_copied", "audiovisual_bytes_copied"},
                               "ARK_AUS_MORANT_QUOTE_INVALID")
    require(quote["text"] == "Shoot straight, you bastards!", "ARK_AUS_MORANT_QUOTE_DRIFT")
    require(len(quote["text"].split()) <= policy["quotation_policy"]["maximum_stored_words"],
            "ARK_AUS_QUOTE_TOO_LONG")
    require(quote["source_id"] == "src.aso.breaker_morant_clip3" and quote["context"] == "film_dialogue",
            "ARK_AUS_MORANT_QUOTE_SOURCE_INVALID")
    require(quote["rights_mode"] == "rights_aware_short_quotation", "ARK_AUS_MORANT_QUOTE_RIGHTS_INVALID")
    require(quote["historical_primary_testimony"] is False, "ARK_AUS_FILM_PROMOTED_TO_HISTORY")
    require(quote["full_script_copied"] is False and quote["audiovisual_bytes_copied"] is False,
            "ARK_AUS_MORANT_RIGHTS_INVALID")
    require("film_dialogue_shoot_straight_you_bastards" in sources[quote["source_id"]]["supports"],
            "ARK_AUS_MORANT_QUOTE_NOT_SOURCE_BOUND")
    require("historical_last_words_reported_differently_from_film" in sources[person["historical_source_id"]]["supports"],
            "ARK_AUS_MORANT_HISTORY_FILM_BOUNDARY_INCOMPLETE")
    require(record["boundaries"] == {
        "film_dialogue_is_primary_historical_testimony": False,
        "cultural_admiration_is_historical_exoneration": False,
        "historical_person_equals_film_character": False,
        "film_can_override_official_historical_metadata": False,
    }, "ARK_AUS_MORANT_BOUNDARY_INVALID")


def validate_hawke(record: dict, sources: dict[str, dict], policy: dict) -> None:
    require_exact_keys(record, {"id", "record_type", "title", "formal_office", "public_persona", "evidence", "boundaries", "reconstruction_target", "uncertainty"},
                       "ARK_AUS_RECORD_SHAPE_INVALID")
    validate_common_record(record, sources, policy)
    require(record["record_type"] == "public_persona_context", "ARK_AUS_RECORD_TYPE_INVALID")
    office = require_exact_keys(record["formal_office"], {"name", "office", "ordinal", "term_start", "term_end", "formal_governance_summary", "source_id"},
                                "ARK_AUS_HAWKE_OFFICE_INVALID")
    require(office["office"] == "Prime Minister of Australia" and office["ordinal"] == 23,
            "ARK_AUS_HAWKE_OFFICE_INVALID")
    require(office["term_start"] == "1983-03-11" and office["term_end"] == "1991-12-20",
            "ARK_AUS_HAWKE_OFFICE_INVALID")
    require(office["source_id"] == "src.nma.bob_hawke", "ARK_AUS_HAWKE_OFFICE_SOURCE_INVALID")
    require("government by consensus" in office["formal_governance_summary"], "ARK_AUS_HAWKE_GOVERNANCE_INVALID")
    persona = require_exact_keys(record["public_persona"], {"description", "source_ids", "quotation_storage", "paraphrase_only"},
                                 "ARK_AUS_HAWKE_PERSONA_INVALID")
    texts(persona["source_ids"], "ARK_AUS_HAWKE_PERSONA_INVALID")
    require(set(persona["source_ids"]) == {"src.australian_museum.bob_hawke", "src.nma.hawke_larrikin_grief"},
            "ARK_AUS_HAWKE_PERSONA_SOURCE_INVALID")
    require(persona["quotation_storage"] == "none" and persona["paraphrase_only"] is True,
            "ARK_AUS_HAWKE_QUOTATION_BOUNDARY_INVALID")
    require(record["boundaries"] == {
        "public_persona_is_formal_authority": False,
        "irreverence_is_government_policy": False,
        "drinking_reputation_proves_governing_competence": False,
        "larrikin_persona_excludes_grief_or_gentleness": False,
    }, "ARK_AUS_HAWKE_BOUNDARY_INVALID")


def validate_records(doc: dict, sources: dict[str, dict], policy: dict) -> set[str]:
    require_exact_keys(doc, {"type", "protocol", "schema_version", "records"}, "ARK_AUS_RECORD_PACK_INVALID")
    require(doc["type"] == "qsol-ark-australian-governance-record-pack", "ARK_AUS_RECORD_PACK_INVALID")
    require(doc["protocol"] == "QSOL-ARK" and doc["schema_version"] == VERSION, "ARK_AUS_RECORD_PACK_INVALID")
    records = doc["records"]
    require(isinstance(records, list) and len(records) == 4, "ARK_AUS_RECORD_COUNT_INVALID")
    ids = [record.get("id") for record in records if isinstance(record, dict)]
    require(len(ids) == len(records) == len(set(ids)) and set(ids) == RECORD_IDS, "ARK_AUS_RECORD_IDS_INVALID")
    for record in records:
        if record["id"] == "culture.australia.australian_informal_governance":
            validate_informal_governance(record, sources, policy)
        elif record["id"] == "culture.australia.irreverent_fatalism":
            validate_irreverent_fatalism(record, sources, policy)
        elif record["id"] == "culture.australia.breaker_morant_history_and_film":
            validate_morant(record, sources, policy)
        elif record["id"] == "culture.australia.bob_hawke_irreverence":
            validate_hawke(record, sources, policy)
        else:
            raise ValueError("ARK_AUS_RECORD_ID_UNKNOWN")
    return set(ids)


def validate_tasks(doc: dict, known_records: set[str]) -> None:
    require_exact_keys(doc, {"type", "protocol", "schema_version", "tasks"}, "ARK_AUS_TASKS_INVALID")
    require(doc["type"] == "qsol-ark-australian-governance-recovery-tasks", "ARK_AUS_TASKS_INVALID")
    require(doc["protocol"] == "QSOL-ARK" and doc["schema_version"] == VERSION, "ARK_AUS_TASKS_INVALID")
    tasks = doc["tasks"]
    require(isinstance(tasks, list) and len(tasks) == len(EXPECTED_TASKS), "ARK_AUS_TASK_COUNT_INVALID")
    ids = [task.get("id") for task in tasks if isinstance(task, dict)]
    require(len(ids) == len(tasks) == len(set(ids)) and set(ids) == set(EXPECTED_TASKS), "ARK_AUS_TASK_IDS_INVALID")
    for task in tasks:
        require_exact_keys(task, {"id", "record_id", "questions"}, "ARK_AUS_TASK_SHAPE_INVALID")
        expected = EXPECTED_TASKS[task["id"]]
        require(task["record_id"] == expected["record_id"] and task["record_id"] in known_records,
                "ARK_AUS_TASK_RECORD_BINDING_INVALID")
        require(task["questions"] == expected["questions"], "ARK_AUS_TASK_SEMANTIC_BINDING_INVALID")
        qids = [question["id"] for question in task["questions"]]
        require(len(qids) == len(set(qids)), "ARK_AUS_TASK_QUESTION_ID_DUPLICATE")


def validate_index(index: dict, known_records: set[str]) -> None:
    require_exact_keys(index, {"type", "protocol", "schema_version", "policy", "sources", "records", "recovery_tasks", "record_ids", "canonical_invariants_ref"},
                       "ARK_AUS_INDEX_INVALID")
    require(index["type"] == "qsol-ark-australian-governance-index", "ARK_AUS_INDEX_INVALID")
    require(index["protocol"] == "QSOL-ARK" and index["schema_version"] == VERSION, "ARK_AUS_INDEX_INVALID")
    expected_paths = {
        "policy": "ai/australian-governance-policy.json",
        "sources": "culture/australia/sources.json",
        "records": "culture/australia/records.json",
        "recovery_tasks": "culture/australia/recovery-tasks.json",
    }
    for key, expected in expected_paths.items():
        require(index[key] == expected, "ARK_AUS_INDEX_PATH_DRIFT")
        safe_path(index[key], "ARK_AUS_INDEX_PATH_INVALID")
    require(set(index["record_ids"]) == known_records, "ARK_AUS_INDEX_RECORD_BINDING_INVALID")
    require(index["canonical_invariants_ref"] == "ai/australian-governance-policy.json#canonical_invariants",
            "ARK_AUS_INDEX_INVARIANT_REF_INVALID")


def validate_discovery(manifest: dict, bootstrap: dict, manifest_schema: dict) -> None:
    expected = {
        "australian_governance_policy": "ai/australian-governance-policy.json",
        "australian_culture_index": "culture/australia/index.json",
        "australian_culture_doc": "docs/AUSTRALIAN-GOVERNANCE-CULTURE.md",
        "australian_culture_validator": "tools/australian_culture.py",
    }
    entrypoints = manifest.get("entrypoints")
    require(isinstance(entrypoints, dict), "ARK_AUS_MANIFEST_DISCOVERY_INVALID")
    for key, path in expected.items():
        require(entrypoints.get(key) == path, "ARK_AUS_MANIFEST_DISCOVERY_INVALID")
        safe_path(path, "ARK_AUS_MANIFEST_DISCOVERY_INVALID")

    load_order = bootstrap.get("load_order")
    require(isinstance(load_order, list) and len(load_order) == len(set(load_order)),
            "ARK_AUS_BOOTSTRAP_DISCOVERY_INVALID")
    policy_path = expected["australian_governance_policy"]
    index_path = expected["australian_culture_index"]
    require(policy_path in load_order and index_path in load_order,
            "ARK_AUS_BOOTSTRAP_DISCOVERY_INVALID")
    require(load_order.index(policy_path) < load_order.index(index_path),
            "ARK_AUS_BOOTSTRAP_DISCOVERY_INVALID")

    entrypoint_schema = manifest_schema.get("properties", {}).get("entrypoints", {})
    required = set(entrypoint_schema.get("required", []))
    properties = entrypoint_schema.get("properties", {})
    for key, path in expected.items():
        require(key in required and properties.get(key, {}).get("const") == path,
                "ARK_AUS_MANIFEST_SCHEMA_DISCOVERY_INVALID")


def validate() -> None:
    policy = load(POLICY_PATH)
    sources_doc = load(SOURCES_PATH)
    records_doc = load(RECORDS_PATH)
    tasks_doc = load(TASKS_PATH)
    index = load(INDEX_PATH)
    manifest = load(MANIFEST_PATH)
    bootstrap = load(BOOTSTRAP_PATH)
    manifest_schema = load(MANIFEST_SCHEMA_PATH)

    validate_policy(policy)
    sources = validate_sources(sources_doc, policy)
    known = validate_records(records_doc, sources, policy)
    validate_tasks(tasks_doc, known)
    validate_index(index, known)
    validate_discovery(manifest, bootstrap, manifest_schema)
    print(f"ARK_AUSTRALIAN_GOVERNANCE_OK records={len(known)} tasks={len(tasks_doc['tasks'])} sources={len(sources)}")


def main(argv: list[str]) -> int:
    try:
        validate()
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
