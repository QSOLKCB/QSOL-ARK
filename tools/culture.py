#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Validate QSOL-ARK cultural records and reconstruction tasks."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "ai" / "cultural-artifact-policy.json"
INDEX = ROOT / "culture" / "index.json"

ALLOWED_EVIDENCE = {
    "official_metadata", "historical_claim", "fictional_world_claim", "first_person_position",
    "third_party_reference", "derived_interpretation", "satire", "joke", "unknown",
}
ALLOWED_RECORD_TYPES = {"cultural_artifact", "authored_cultural_position"}
TASK_SCHEMA_VERSION = "0.1.0"
POSITION_QUOTE_SHA256 = "3dc0e80f87fcbf2f993fdec9fd368fe3ebbd682c1805d259fdd01b32e00258b2"
ARK_CANARY_SHA256 = "df2d7ed3696dda919d2b8a3356eeb5a8473f1cc3bb05fd30b9f7281e6bb08cab"
THIS_IS_FINE_CROP_SHA256 = "774bc388e814d66c075ff2126edf876a3fa7d32c61cc59542770cdc8d5e6cdaf"
MEME_POLICY_VERSION = "1.0.0"

MEME_INVARIANTS = {
    "MEME != DECORATIVE_IMAGE",
    "CAPTION != CONTEXT",
    "DEPICTION != HISTORICAL_EVENT",
    "MEME_HISTORY_REFERENCE != CREATOR_SOURCE",
    "DERIVED_INTERPRETATION != UNIVERSAL_MEANING",
    "KNOWN_HASH != BYTE_COPY_PERMISSION",
    "POPULARITY != TRUTH",
}
MEME_SOURCE_EVIDENCE_FIELDS = {
    "visibility", "license_status", "canonical_status", "byte_import_allowed",
}
MEME_ALLOWED_VISIBILITY = {"public", "ingest_observation_only"}
MEME_ALLOWED_LICENSE = {"third_party_reference_only", "rights_unresolved_reference_only"}
MEME_ALLOWED_CANONICAL = {
    "canonical_for_declared_supports", "noncanonical_history_reference", "observed_noncanonical_variant",
}

EXPECTED_CASSANDRA_PARALLEL_DESCRIPTION = (
    "The fictional Canaries and ARK-CANARY both use the canary metaphor as a precursor used to probe "
    "danger before more consequential activity proceeds."
)

NARRATIVE_TOP_LEVEL = {
    "type", "protocol", "schema_version", "id", "record_type", "artifact_class", "medium", "era", "title",
    "work", "reconstruction_target", "epistemic_status", "real_world_metadata", "cultural_context",
    "fiction_boundary", "rights", "sources", "recovery_questions",
}
POSITION_TOP_LEVEL = {
    "type", "protocol", "schema_version", "id", "record_type", "artifact_class", "author", "date", "title",
    "epistemic_status", "provenance", "verbatim_statement", "normalized_position", "license_effect",
    "claim_boundary", "cultural_principles",
}

EXPECTED_NORMALIZED_POSITION = {
    "sentiment_toward_elon_musk": "strongly_negative",
    "sentiment_toward_xai": "strongly_negative",
    "sentiment_toward_grok": "positive",
    "supports_meaningful_human_review_for_serious_platform_enforcement": True,
    "supports_open_source_permissions_even_for_strongly_disliked_parties": True,
    "permission_is_endorsement": False,
    "liking_a_product_implies_endorsement_of_its_company": False,
}

EXPECTED_OFFICIAL_OUROBOROS_SOURCE = {
    "id": "source.red_dwarf.official.ouroboros",
    "role": "official_metadata",
    "url": "https://reddwarf.co.uk/episodes/ouroboros/",
    "verification_status": "retrieved_2026-08-17",
    "supports": ["series", "episode", "first_broadcast", "written_by", "directed_by"],
}
EXPECTED_TRANSCRIPT_SOURCE = {
    "id": "source.cervenytrpaslik.ouroboros_transcript",
    "role": "third_party_reference",
    "url": "http://www.cervenytrpaslik.cz/scenare/EN-39-7_Ouroboros.htm",
    "provided_by": "maintainer",
    "verification_status": "unavailable_at_ingest",
    "license_status": "unknown",
    "source_bytes_copied": False,
}
EXPECTED_OFFICIAL_CASSANDRA_SOURCE = {
    "id": "source.red_dwarf.official.cassandra",
    "role": "official_metadata",
    "url": "https://reddwarf.co.uk/episodes/cassandra",
    "verification_status": "retrieved_2026-08-18",
    "supports": ["series", "episode", "first_broadcast", "written_by", "directed_by", "canaries_synopsis"],
}
EXPECTED_CASSANDRA_REFERENCE = {
    "id": "source.wikipedia.cassandra_red_dwarf",
    "role": "third_party_reference",
    "url": "https://en.wikipedia.org/wiki/Cassandra_(Red_Dwarf)",
    "provided_by": "maintainer",
    "verification_status": "maintainer_supplied_2026-08-18",
    "license_status": "third_party_reference_only",
    "source_bytes_copied": False,
    "supports": ["canaries_as_dangerous_first_response_unit"],
}
EXPECTED_ARK_CANARY_SOURCE = {
    "id": "source.qsol_ark.ark_canary",
    "role": "canonical_internal_reference",
    "path": "capsules/minimal/ARK-CANARY.txt",
    "receipt": "capsules/minimal/SHA256SUMS",
    "documentation": "docs/COMPUTATIONAL-ARCHAEOLOGY.md",
    "sha256": ARK_CANARY_SHA256,
    "supports": ["ark_canary_identity", "minimal_recovery_probe_role"],
}

EXPECTED_THIS_IS_FINE_METADATA = {
    "creator": "KC Green",
    "source_work": "Gunshow",
    "source_title": "On Fire",
    "publication_date": "2013-01-09",
}
EXPECTED_THIS_IS_FINE_GENRES = {"webcomic", "internet_meme", "reaction_image"}
EXPECTED_THIS_IS_FINE_TOPICS = {
    "visual_context", "literal_text_vs_scene", "crisis_normalization", "ironic_understatement",
    "context_compression", "meme_transmission_history",
}
EXPECTED_THIS_IS_FINE_INTERPRETATION = (
    "The artifact juxtaposes explicit reassurance with visibly adverse surroundings, making it a compact "
    "recovery test for integrating visual context with literal text."
)
EXPECTED_THIS_IS_FINE_RECOVERY_QUESTIONS = [
    "distinguish the real-world publication metadata from the fictional depicted scene",
    "integrate the visible scene with the literal caption instead of treating text alone as ground truth",
    "preserve the visual interpretation as derived rather than a universal meaning",
    "separate creator/source metadata from third-party meme transmission history",
    "recognize that a known image hash does not grant permission to copy third-party bytes",
    "recognize that the depicted fire is not evidence of a historical real-world fire",
]

MEME_EVIDENCE_OFFICIAL = {
    "visibility": "public",
    "license_status": "rights_unresolved_reference_only",
    "canonical_status": "canonical_for_declared_supports",
    "byte_import_allowed": False,
}
MEME_EVIDENCE_HISTORY = {
    "visibility": "public",
    "license_status": "third_party_reference_only",
    "canonical_status": "noncanonical_history_reference",
    "byte_import_allowed": False,
}
MEME_EVIDENCE_CROP = {
    "visibility": "ingest_observation_only",
    "license_status": "rights_unresolved_reference_only",
    "canonical_status": "observed_noncanonical_variant",
    "byte_import_allowed": False,
}

EXPECTED_THIS_IS_FINE_OFFICIAL_SOURCES = [
    {
        "id": "source.gunshow.official.on_fire",
        "role": "official_metadata",
        "url": "https://gunshowcomic.com/648",
        "verification_status": "retrieved_2026-08-18",
        **MEME_EVIDENCE_OFFICIAL,
        "supports": ["source_title", "source_work", "visual_source"],
    },
    {
        "id": "source.gunshow.official.archive",
        "role": "official_metadata",
        "url": "https://gunshowcomic.com/archive.php",
        "verification_status": "retrieved_2026-08-18",
        **MEME_EVIDENCE_OFFICIAL,
        "supports": ["publication_date", "source_title"],
    },
    {
        "id": "source.gunshow.official.about",
        "role": "official_metadata",
        "url": "https://gunshowcomic.com/about.html",
        "verification_status": "retrieved_2026-08-18",
        **MEME_EVIDENCE_OFFICIAL,
        "supports": ["creator", "source_work"],
    },
]
EXPECTED_THIS_IS_FINE_HISTORY_SOURCE = {
    "id": "source.knowyourmeme.this_is_fine",
    "role": "third_party_reference",
    "url": "https://knowyourmeme.com/memes/this-is-fine",
    "provided_by": "maintainer",
    "verification_status": "retrieved_2026-08-18",
    **MEME_EVIDENCE_HISTORY,
    "source_bytes_copied": False,
    "supports": ["meme_status", "meme_type", "origin_and_spread_history", "reaction_image_usage"],
}
EXPECTED_THIS_IS_FINE_CROP_SOURCE = {
    "id": "source.maintainer.this_is_fine_crop",
    "role": "third_party_reference",
    "provided_by": "maintainer",
    "verification_status": "observed_at_ingest_2026-08-18",
    **MEME_EVIDENCE_CROP,
    "sha256": THIS_IS_FINE_CROP_SHA256,
    "byte_length": 41642,
    "media_type": "image/webp",
    "pixel_dimensions": [600, 284],
    "repository_bytes_copied": False,
    "repository_reverification_possible": False,
    "canonical_master_claimed": False,
    "supports": ["observed_crop_identity", "observed_crop_media_type", "observed_crop_dimensions"],
}

EXPECTED_THIS_IS_FINE_TASK_QUESTIONS = [
    {
        "id": "meme-01",
        "prompt": "Is the burning room depicted in the meme being preserved as evidence that a real historical room burned?",
        "expected": "no",
    },
    {
        "id": "meme-02",
        "prompt": "Does the literal caption THIS IS FINE establish that the depicted situation is actually safe or fine?",
        "expected": "no",
    },
    {
        "id": "meme-03",
        "prompt": "May ARK preserve a derived interpretation of the contrast between the caption and visual scene when that interpretation remains explicitly labelled derived?",
        "expected": "yes",
    },
    {
        "id": "meme-04",
        "prompt": "Does knowing the SHA-256 of a maintainer-supplied third-party meme crop grant ARK permission to copy those image bytes into the repository?",
        "expected": "no",
    },
    {
        "id": "meme-05",
        "prompt": "Should the depicted dog, room and fire be treated as fictional-world claims rather than real-world historical evidence?",
        "expected": "fictional_world_claim",
    },
    {
        "id": "meme-06",
        "prompt": "Does this record claim that the meme has one universal meaning in every context?",
        "expected": "no",
    },
    {
        "id": "meme-07",
        "prompt": "Is the Know Your Meme entry being treated as the creator-authoritative source for KC Green and the original Gunshow publication metadata?",
        "expected": "no",
    },
    {
        "id": "meme-08",
        "prompt": "May a provenance-labelled third-party meme-history reference be used to reconstruct spread and usage history without becoming the creator source?",
        "expected": "yes",
    },
]
EXACT_TASK_BINDINGS = {
    "task.culture.this_is_fine_boundary": {
        "record_id": "culture.meme.this_is_fine",
        "questions": EXPECTED_THIS_IS_FINE_TASK_QUESTIONS,
    },
}


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ValueError(code)


def require_exact_keys(obj: object, expected: set[str], code: str) -> dict:
    require(isinstance(obj, dict) and set(obj) == expected, code)
    return obj


def require_required_keys(obj: object, required: set[str], code: str) -> dict:
    require(isinstance(obj, dict) and required.issubset(obj), code)
    return obj


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
    require(policy.get("schema_version") == "0.1.0", "ARK_CULTURE_POLICY_INVALID")
    require(set(policy.get("record_types", [])) == ALLOWED_RECORD_TYPES, "ARK_CULTURE_POLICY_INVALID")
    require(set(policy.get("evidence_classes", [])) == ALLOWED_EVIDENCE, "ARK_CULTURE_POLICY_INVALID")

    rules = set(policy.get("rules", []))
    required_rules = {
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
        "cultural_parallel_is_not_naming_provenance",
    }
    require(required_rules.issubset(rules), "ARK_CULTURE_POLICY_INVALID")

    meme = require_required_keys(
        policy.get("meme_archaeology"), {"policy_version", "canonical_invariants", "source_evidence", "task_binding"},
        "ARK_MEME_POLICY_INVALID",
    )
    require(meme["policy_version"] == MEME_POLICY_VERSION, "ARK_MEME_POLICY_VERSION_UNSUPPORTED")
    require(set(meme["canonical_invariants"]) == MEME_INVARIANTS, "ARK_MEME_POLICY_INVALID")

    source_evidence = require_required_keys(
        meme["source_evidence"],
        {"required_fields", "allowed_visibility", "allowed_license_status", "allowed_canonical_status",
         "unresolved_rights_byte_import_allowed"},
        "ARK_MEME_POLICY_INVALID",
    )
    require(set(source_evidence["required_fields"]) == MEME_SOURCE_EVIDENCE_FIELDS, "ARK_MEME_POLICY_INVALID")
    require(set(source_evidence["allowed_visibility"]) == MEME_ALLOWED_VISIBILITY, "ARK_MEME_POLICY_INVALID")
    require(set(source_evidence["allowed_license_status"]) == MEME_ALLOWED_LICENSE, "ARK_MEME_POLICY_INVALID")
    require(set(source_evidence["allowed_canonical_status"]) == MEME_ALLOWED_CANONICAL, "ARK_MEME_POLICY_INVALID")
    require(source_evidence["unresolved_rights_byte_import_allowed"] is False, "ARK_MEME_POLICY_INVALID")

    task_binding = require_required_keys(meme["task_binding"], {"mode", "bind_fields"}, "ARK_MEME_POLICY_INVALID")
    require(task_binding["mode"] == "record_specific_exact", "ARK_MEME_POLICY_INVALID")
    require(set(task_binding["bind_fields"]) == {"id", "prompt", "expected"}, "ARK_MEME_POLICY_INVALID")

    copyright_policy = policy.get("copyright", {})
    require(copyright_policy.get("full_script_copy_without_permission") == "forbidden",
            "ARK_CULTURE_COPYRIGHT_POLICY_INVALID")


def validate_ouroboros(record: dict) -> None:
    require_exact_keys(record, NARRATIVE_TOP_LEVEL, "ARK_CULTURE_RECORD_SHAPE_INVALID")
    require(record.get("record_type") == "cultural_artifact", "ARK_CULTURE_RECORD_TYPE_INVALID")
    require(record.get("id") == "culture.television.red_dwarf.ouroboros", "ARK_CULTURE_RECORD_ID_INVALID")
    require(record.get("epistemic_status") == "documented_with_derived_interpretation",
            "ARK_CULTURE_INTERPRETATION_PROMOTED")
    require(record.get("cultural_context", {}).get("interpretation_status") ==
            "derived_interpretation_not_production_metadata", "ARK_CULTURE_INTERPRETATION_PROMOTED")

    rights = require_exact_keys(record.get("rights"), {
        "third_party_copyright", "license_status", "source_bytes_copied", "script_text_copied",
    }, "ARK_CULTURE_RIGHTS_INVALID")
    require(rights.get("third_party_copyright") is True, "ARK_CULTURE_RIGHTS_INVALID")
    require(rights.get("source_bytes_copied") is False, "ARK_THIRD_PARTY_BYTES_WITHOUT_RESOLVED_LICENSE")
    require(rights.get("script_text_copied") is False, "ARK_THIRD_PARTY_SCRIPT_COPY_FORBIDDEN")
    require(rights.get("license_status") == "not_authorized_for_copy", "ARK_CULTURE_RIGHTS_INVALID")

    boundary = require_exact_keys(record.get("fiction_boundary"), {
        "narrative_events_are", "narrative_events_are_historical_evidence", "production_metadata_is_real_world_history",
    }, "ARK_FICTION_BOUNDARY_INVALID")
    require(boundary.get("narrative_events_are") == "fictional_world_claims", "ARK_FICTION_BOUNDARY_INVALID")
    require(boundary.get("narrative_events_are_historical_evidence") is False, "ARK_FICTION_PROMOTED_TO_HISTORY")
    require(boundary.get("production_metadata_is_real_world_history") is True, "ARK_FICTION_BOUNDARY_INVALID")

    require(record.get("real_world_metadata") == {
        "series": 7,
        "episode": 3,
        "first_broadcast": "1997-01-31",
        "written_by": ["Doug Naylor"],
        "directed_by": ["Ed Bye"],
    }, "ARK_CULTURE_PRODUCTION_METADATA_INVALID")

    context = require_exact_keys(record.get("cultural_context"), {"genres", "topics", "interpretation_status"},
                                 "ARK_CULTURE_RECORD_SHAPE_INVALID")
    require(isinstance(context["genres"], list) and isinstance(context["topics"], list),
            "ARK_CULTURE_RECORD_SHAPE_INVALID")

    sources = record.get("sources", [])
    require(isinstance(sources, list) and len(sources) == 2, "ARK_CULTURE_SOURCE_INVALID")
    official = [s for s in sources if isinstance(s, dict) and s.get("role") == "official_metadata"]
    require(len(official) == 1 and official[0] == EXPECTED_OFFICIAL_OUROBOROS_SOURCE,
            "ARK_CULTURE_OFFICIAL_SOURCE_REQUIRED")
    transcript = [s for s in sources if isinstance(s, dict) and s.get("id") ==
                  "source.cervenytrpaslik.ouroboros_transcript"]
    require(len(transcript) == 1 and transcript[0] == EXPECTED_TRANSCRIPT_SOURCE,
            "ARK_CULTURE_TRANSCRIPT_REFERENCE_INVALID")

    require(record.get("recovery_questions") == [
        "distinguish real-world production metadata from fictional-world narrative claims",
        "explain why a transcript reference is not the canonical audiovisual master",
        "preserve cultural interpretation without promoting it to production metadata",
        "recognize that checksum integrity would not make fictional events historical facts",
    ], "ARK_CULTURE_RECORD_SHAPE_INVALID")


def validate_cassandra(record: dict) -> None:
    require_exact_keys(record, NARRATIVE_TOP_LEVEL, "ARK_CULTURE_RECORD_SHAPE_INVALID")
    require(record.get("record_type") == "cultural_artifact", "ARK_CULTURE_RECORD_TYPE_INVALID")
    require(record.get("id") == "culture.television.red_dwarf.cassandra_canaries", "ARK_CULTURE_RECORD_ID_INVALID")
    require(record.get("epistemic_status") == "documented_with_derived_design_parallel",
            "ARK_CULTURE_INTERPRETATION_PROMOTED")

    require(record.get("real_world_metadata") == {
        "series": 8,
        "episode": 4,
        "first_broadcast": "1999-03-11",
        "written_by": ["Doug Naylor"],
        "directed_by": ["Ed Bye"],
    }, "ARK_CULTURE_PRODUCTION_METADATA_INVALID")

    context = require_exact_keys(record.get("cultural_context"), {
        "genres", "topics", "official_synopsis_summary", "ark_parallel", "interpretation_status",
    }, "ARK_CULTURE_RECORD_SHAPE_INVALID")
    require(context.get("interpretation_status") == "derived_parallel_not_naming_provenance",
            "ARK_CULTURE_INTERPRETATION_PROMOTED")
    parallel = require_exact_keys(context.get("ark_parallel"), {
        "status", "description", "naming_provenance", "naming_origin_claimed",
    }, "ARK_CULTURE_RECORD_SHAPE_INVALID")
    require(parallel.get("status") == "derived_interpretation", "ARK_CULTURE_INTERPRETATION_PROMOTED")
    require(parallel.get("description") == EXPECTED_CASSANDRA_PARALLEL_DESCRIPTION,
            "ARK_CULTURAL_PARALLEL_DESCRIPTION_INVALID")
    require(parallel.get("naming_provenance") == "not_established" and parallel.get("naming_origin_claimed") is False,
            "ARK_CULTURAL_PARALLEL_PROMOTED_TO_NAMING_PROVENANCE")

    boundary = require_exact_keys(record.get("fiction_boundary"), {
        "narrative_events_are", "narrative_events_are_historical_evidence", "production_metadata_is_real_world_history",
        "cultural_parallel_is_naming_provenance",
    }, "ARK_FICTION_BOUNDARY_INVALID")
    require(boundary.get("narrative_events_are") == "fictional_world_claims", "ARK_FICTION_BOUNDARY_INVALID")
    require(boundary.get("narrative_events_are_historical_evidence") is False, "ARK_FICTION_PROMOTED_TO_HISTORY")
    require(boundary.get("production_metadata_is_real_world_history") is True, "ARK_FICTION_BOUNDARY_INVALID")
    require(boundary.get("cultural_parallel_is_naming_provenance") is False,
            "ARK_CULTURAL_PARALLEL_PROMOTED_TO_NAMING_PROVENANCE")

    rights = require_exact_keys(record.get("rights"), {
        "third_party_copyright", "license_status", "source_bytes_copied", "script_text_copied",
    }, "ARK_CULTURE_RIGHTS_INVALID")
    require(rights == {
        "third_party_copyright": True,
        "license_status": "not_authorized_for_copy",
        "source_bytes_copied": False,
        "script_text_copied": False,
    }, "ARK_CULTURE_RIGHTS_INVALID")

    sources = record.get("sources", [])
    require(isinstance(sources, list) and len(sources) == 3, "ARK_CULTURE_SOURCE_INVALID")
    official = [s for s in sources if isinstance(s, dict) and s.get("id") == "source.red_dwarf.official.cassandra"]
    require(len(official) == 1 and official[0] == EXPECTED_OFFICIAL_CASSANDRA_SOURCE,
            "ARK_CULTURE_OFFICIAL_SOURCE_REQUIRED")
    supplied = [s for s in sources if isinstance(s, dict) and s.get("id") == "source.wikipedia.cassandra_red_dwarf"]
    require(len(supplied) == 1 and supplied[0] == EXPECTED_CASSANDRA_REFERENCE, "ARK_CULTURE_REFERENCE_INVALID")
    internal = [s for s in sources if isinstance(s, dict) and s.get("id") == "source.qsol_ark.ark_canary"]
    require(len(internal) == 1 and internal[0] == EXPECTED_ARK_CANARY_SOURCE,
            "ARK_CULTURE_ARK_CANARY_BINDING_INVALID")

    canary = safe_repo_path(internal[0]["path"], "capsules")
    receipt = safe_repo_path(internal[0]["receipt"], "capsules")
    payload_sha256 = hashlib.sha256(canary.read_bytes()).hexdigest()
    require(payload_sha256 == ARK_CANARY_SHA256 and payload_sha256 == internal[0]["sha256"],
            "ARK_CULTURE_ARK_CANARY_BINDING_INVALID")
    receipt_lines = receipt.read_text(encoding="utf-8").splitlines()
    require(any(line.split() == [payload_sha256, canary.name] for line in receipt_lines),
            "ARK_CULTURE_ARK_CANARY_BINDING_INVALID")

    require(record.get("recovery_questions") == [
        "distinguish Red Dwarf production metadata from fictional-world Canaries narrative claims",
        "explain the derived cultural parallel between the fictional Canaries and ARK-CANARY",
        "recognize that a cultural parallel does not establish naming provenance",
        "recognize that a successful canary check does not prove all later recovery operations are safe or true",
    ], "ARK_CULTURE_RECORD_SHAPE_INVALID")


def validate_meme_source_evidence(source: dict) -> None:
    require_required_keys(source, MEME_SOURCE_EVIDENCE_FIELDS, "ARK_MEME_SOURCE_EVIDENCE_INCOMPLETE")
    require(source["visibility"] in MEME_ALLOWED_VISIBILITY, "ARK_MEME_SOURCE_EVIDENCE_INVALID")
    require(source["license_status"] in MEME_ALLOWED_LICENSE, "ARK_MEME_SOURCE_EVIDENCE_INVALID")
    require(source["canonical_status"] in MEME_ALLOWED_CANONICAL, "ARK_MEME_SOURCE_EVIDENCE_INVALID")
    require(source["byte_import_allowed"] is False, "ARK_MEME_SOURCE_EVIDENCE_INVALID")


def validate_exact_meme_source(source: dict, expected: dict, code: str) -> None:
    validate_meme_source_evidence(source)
    require_exact_keys(source, set(expected), code)
    require(source == expected, code)


def validate_this_is_fine(record: dict) -> None:
    require_exact_keys(record, NARRATIVE_TOP_LEVEL, "ARK_CULTURE_RECORD_SHAPE_INVALID")
    require(record.get("record_type") == "cultural_artifact", "ARK_CULTURE_RECORD_TYPE_INVALID")
    require(record.get("id") == "culture.meme.this_is_fine", "ARK_CULTURE_RECORD_ID_INVALID")
    require(record.get("artifact_class") == "visual_meme_and_context_boundary", "ARK_MEME_ARTIFACT_CLASS_INVALID")
    require(record.get("medium") == "webcomic_panel_and_internet_meme", "ARK_MEME_MEDIUM_INVALID")
    require(record.get("epistemic_status") == "documented_source_with_derived_visual_interpretation",
            "ARK_MEME_INTERPRETATION_PROMOTED")

    metadata = require_required_keys(record.get("real_world_metadata"), set(EXPECTED_THIS_IS_FINE_METADATA),
                                     "ARK_MEME_SOURCE_METADATA_INVALID")
    for key, expected in EXPECTED_THIS_IS_FINE_METADATA.items():
        require(metadata.get(key) == expected, "ARK_MEME_SOURCE_METADATA_INVALID")

    context = require_required_keys(record.get("cultural_context"), {
        "genres", "topics", "visual_summary", "quoted_text", "derived_interpretation", "interpretation_status",
        "transmission_history",
    }, "ARK_MEME_CONTEXT_INVALID")
    require(isinstance(context["genres"], list) and EXPECTED_THIS_IS_FINE_GENRES.issubset(context["genres"]),
            "ARK_MEME_CONTEXT_INVALID")
    require(isinstance(context["topics"], list) and EXPECTED_THIS_IS_FINE_TOPICS.issubset(context["topics"]),
            "ARK_MEME_CONTEXT_INVALID")
    require(context["visual_summary"] ==
            "A cartoon dog sits with a mug in a room visibly on fire while saying: THIS IS FINE.",
            "ARK_MEME_CONTEXT_INVALID")
    require(context["quoted_text"] == "THIS IS FINE.", "ARK_MEME_CONTEXT_INVALID")
    require(context["derived_interpretation"] == EXPECTED_THIS_IS_FINE_INTERPRETATION, "ARK_MEME_CONTEXT_INVALID")
    require(context["interpretation_status"] == "derived_interpretation_not_universal_meaning",
            "ARK_MEME_CONTEXT_INVALID")

    history = require_required_keys(context["transmission_history"], {
        "status", "source_id", "meme_status", "meme_types", "summary", "boundary",
    }, "ARK_MEME_HISTORY_PROVENANCE_INVALID")
    require(history["status"] == "third_party_documented_history", "ARK_MEME_HISTORY_PROVENANCE_INVALID")
    require(history["source_id"] == EXPECTED_THIS_IS_FINE_HISTORY_SOURCE["id"], "ARK_MEME_CONTEXT_INVALID")
    require(history["meme_status"] == "confirmed", "ARK_MEME_HISTORY_PROVENANCE_INVALID")
    require(isinstance(history["meme_types"], list) and {"exploitable", "reaction"}.issubset(history["meme_types"]),
            "ARK_MEME_HISTORY_PROVENANCE_INVALID")
    require(isinstance(history["summary"], str) and history["summary"].strip(), "ARK_MEME_HISTORY_PROVENANCE_INVALID")
    require(history["boundary"] == "third_party_history_reference_not_creator_metadata_or_universal_interpretation",
            "ARK_MEME_HISTORY_PROVENANCE_INVALID")

    boundary = require_required_keys(record.get("fiction_boundary"), {
        "depicted_scene_is", "depicted_scene_is_historical_evidence", "literal_caption_establishes_real_world_safety",
        "derived_interpretation_is_universal_meaning",
    }, "ARK_MEME_BOUNDARY_INVALID")
    require(boundary["depicted_scene_is"] == "fictional_comic_scene", "ARK_MEME_BOUNDARY_INVALID")
    require(boundary["depicted_scene_is_historical_evidence"] is False, "ARK_MEME_BOUNDARY_INVALID")
    require(boundary["literal_caption_establishes_real_world_safety"] is False, "ARK_MEME_BOUNDARY_INVALID")
    require(boundary["derived_interpretation_is_universal_meaning"] is False, "ARK_MEME_BOUNDARY_INVALID")

    rights = require_required_keys(record.get("rights"), {
        "third_party_copyright", "license_status", "source_bytes_copied", "image_bytes_copied",
    }, "ARK_CULTURE_RIGHTS_INVALID")
    require(rights["third_party_copyright"] is True, "ARK_CULTURE_RIGHTS_INVALID")
    require(rights["license_status"] == "not_authorized_for_copy", "ARK_CULTURE_RIGHTS_INVALID")
    require(rights["source_bytes_copied"] is False and rights["image_bytes_copied"] is False,
            "ARK_THIRD_PARTY_BYTES_WITHOUT_RESOLVED_LICENSE")

    sources = record.get("sources", [])
    require(isinstance(sources, list) and len(sources) == 5, "ARK_CULTURE_SOURCE_INVALID")
    ids = [s.get("id") for s in sources if isinstance(s, dict)]
    require(len(ids) == 5 and len(set(ids)) == 5, "ARK_CULTURE_SOURCE_INVALID")

    for expected in EXPECTED_THIS_IS_FINE_OFFICIAL_SOURCES:
        matches = [s for s in sources if isinstance(s, dict) and s.get("id") == expected["id"]]
        require(len(matches) == 1, "ARK_MEME_OFFICIAL_SOURCE_INVALID")
        validate_exact_meme_source(matches[0], expected, "ARK_MEME_OFFICIAL_SOURCE_INVALID")

    history_sources = [s for s in sources if isinstance(s, dict)
                       and s.get("id") == EXPECTED_THIS_IS_FINE_HISTORY_SOURCE["id"]]
    require(len(history_sources) == 1, "ARK_MEME_HISTORY_SOURCE_INVALID")
    validate_exact_meme_source(history_sources[0], EXPECTED_THIS_IS_FINE_HISTORY_SOURCE,
                               "ARK_MEME_HISTORY_SOURCE_INVALID")

    crop_sources = [s for s in sources if isinstance(s, dict)
                    and s.get("id") == EXPECTED_THIS_IS_FINE_CROP_SOURCE["id"]]
    require(len(crop_sources) == 1, "ARK_MEME_OBSERVED_CROP_INVALID")
    validate_exact_meme_source(crop_sources[0], EXPECTED_THIS_IS_FINE_CROP_SOURCE,
                               "ARK_MEME_OBSERVED_CROP_INVALID")
    crop = crop_sources[0]
    require(crop["sha256"] == THIS_IS_FINE_CROP_SHA256
            and crop["repository_bytes_copied"] is False
            and crop["repository_reverification_possible"] is False
            and crop["canonical_master_claimed"] is False,
            "ARK_MEME_OBSERVED_CROP_INVALID")

    require(record.get("recovery_questions") == EXPECTED_THIS_IS_FINE_RECOVERY_QUESTIONS,
            "ARK_CULTURE_RECORD_SHAPE_INVALID")


def validate_position(record: dict) -> None:
    require_exact_keys(record, POSITION_TOP_LEVEL, "ARK_CULTURE_RECORD_SHAPE_INVALID")
    require(record.get("record_type") == "authored_cultural_position", "ARK_CULTURE_RECORD_TYPE_INVALID")
    require(record.get("id") == "culture.qsol.open_source.permission_not_endorsement", "ARK_CULTURE_RECORD_ID_INVALID")
    require(record.get("author") == {"name": "Trent Slade", "github": "EmergentMonk"}, "ARK_CULTURE_AUTHOR_INVALID")
    require(record.get("epistemic_status") == "first_person_position", "ARK_CULTURE_POSITION_CLASS_INVALID")

    require(record.get("provenance", {}) == {
        "source_kind": "direct_maintainer_contribution",
        "public_release_intent": "explicit",
        "independent_verification_required_for_external_factual_claims": True,
    }, "ARK_CULTURE_POSITION_PROVENANCE_INVALID")

    statement = record.get("verbatim_statement")
    require(isinstance(statement, str) and statement.strip(), "ARK_CULTURE_QUOTATION_MISSING")
    require(hashlib.sha256(statement.encode("utf-8")).hexdigest() == POSITION_QUOTE_SHA256,
            "ARK_CULTURE_QUOTATION_MISMATCH")
    require(record.get("normalized_position") == EXPECTED_NORMALIZED_POSITION,
            "ARK_CULTURE_POSITION_NORMALIZATION_INVALID")
    require(record.get("license_effect") == {
        "applicable_repository_licenses_remain_governing": True,
        "statement_creates_additional_exclusive_license_restriction": False,
        "reuse_permission_depends_on_personal_approval": False,
    }, "ARK_CULTURE_LICENSE_BOUNDARY_INVALID")
    require(record.get("claim_boundary", {}) == {
        "authoritative_as": "the authors stated opinion and principle",
        "not_authoritative_as": [
            "objective fact about Elon Musk",
            "objective fact about xAI",
            "verified description of any platforms moderation or appeal process",
            "universal definition of free speech",
        ],
        "objective_claims_about_named_entities_verified": False,
    }, "ARK_OPINION_PROMOTED_TO_OBJECTIVE_FACT")
    require(record.get("cultural_principles") == [
        "permission_is_not_endorsement",
        "principles_are_tested_when_the_beneficiary_is_disliked",
        "open_permissions_should_not_be_selectively_reinterpreted_by_personal_affection",
        "serious_platform_enforcement_should_have_meaningful_human_review",
    ], "ARK_PERMISSION_ENDORSEMENT_BOUNDARY_INVALID")


def validate_record(record: dict) -> None:
    require(record.get("type") == "qsol-ark-cultural-record", "ARK_CULTURE_RECORD_INVALID")
    require(record.get("protocol") == "QSOL-ARK", "ARK_CULTURE_RECORD_INVALID")
    require(record.get("schema_version") == "0.1.0", "ARK_CULTURE_RECORD_INVALID")
    require(record.get("record_type") in ALLOWED_RECORD_TYPES, "ARK_CULTURE_RECORD_TYPE_INVALID")

    record_id = record.get("id")
    if record_id == "culture.television.red_dwarf.ouroboros":
        validate_ouroboros(record)
    elif record_id == "culture.television.red_dwarf.cassandra_canaries":
        validate_cassandra(record)
    elif record_id == "culture.meme.this_is_fine":
        validate_this_is_fine(record)
    elif record_id == "culture.qsol.open_source.permission_not_endorsement":
        validate_position(record)
    else:
        raise ValueError("ARK_CULTURE_RECORD_ID_UNKNOWN")


def validate_task(task: dict, known_records: set[str]) -> None:
    require_exact_keys(task, {"type", "protocol", "schema_version", "id", "record_id", "questions"},
                       "ARK_CULTURE_TASK_INVALID")
    require(task.get("type") == "qsol-ark-cultural-recovery-task", "ARK_CULTURE_TASK_INVALID")
    require(task.get("protocol") == "QSOL-ARK", "ARK_CULTURE_TASK_INVALID")
    require(task.get("schema_version") == TASK_SCHEMA_VERSION, "ARK_CULTURE_TASK_SCHEMA_UNSUPPORTED")
    require(task.get("record_id") in known_records, "ARK_CULTURE_TASK_RECORD_UNKNOWN")

    questions = task.get("questions")
    require(isinstance(questions, list) and questions, "ARK_CULTURE_TASK_INVALID")
    ids = [q.get("id") for q in questions if isinstance(q, dict)]
    require(len(ids) == len(questions) == len(set(ids)), "ARK_CULTURE_TASK_INVALID")
    for q in questions:
        require_exact_keys(q, {"id", "prompt", "expected"}, "ARK_CULTURE_TASK_INVALID")
        require(isinstance(q.get("prompt"), str) and q["prompt"], "ARK_CULTURE_TASK_INVALID")
        require(q.get("expected") in {"no", "yes", "real_world_production_metadata", "fictional_world_claim"},
                "ARK_CULTURE_TASK_EXPECTATION_INVALID")

    binding = EXACT_TASK_BINDINGS.get(task.get("id"))
    if binding is not None:
        require(task.get("record_id") == binding["record_id"], "ARK_CULTURE_TASK_BINDING_INVALID")
        require(task.get("questions") == binding["questions"], "ARK_CULTURE_TASK_BINDING_INVALID")


def validate() -> None:
    policy = load(POLICY)
    index = load(INDEX)
    validate_policy(policy)
    require(index.get("type") == "qsol-ark-culture-index", "ARK_CULTURE_INDEX_INVALID")
    require(index.get("protocol") == "QSOL-ARK", "ARK_CULTURE_INDEX_INVALID")
    require(index.get("schema_version") == "0.1.0", "ARK_CULTURE_INDEX_INVALID")
    records = index.get("records")
    tasks = index.get("tasks")
    require(isinstance(records, list) and len(records) == 4, "ARK_CULTURE_INDEX_INVALID")
    require(isinstance(tasks, list) and len(tasks) == 4, "ARK_CULTURE_INDEX_INVALID")
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
