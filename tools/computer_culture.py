#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Validate QSOL-ARK broader computer-culture records."""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "ai/computer-cultural-artifact-profile.json"
SCORE_PATH = ROOT / "ai/cultural-recovery-score.json"
INDEX_PATH = ROOT / "culture/computing/index.json"
SPECIMENS_PATH = ROOT / "culture/computing/specimens.json"
TEXT_PATH = ROOT / "culture/computing/text-specimens.json"
TASKS_PATH = ROOT / "culture/computing/recovery-tasks.json"
MYTHS_PATH = ROOT / "culture/myths/classification.json"
MANIFEST_PATH = ROOT / "manifest.json"
BOOTSTRAP_PATH = ROOT / "ai/bootstrap.json"

VERSION = "1.0.0"
RECORD_TYPE = "computer_cultural_artifact"
EVIDENCE_CLASSES = {"executable_artifact", "cultural_artifact", "historical_claim"}
STRONG_CLAIM_CATEGORIES = {"named_person", "legal", "security", "quotation", "first_ever"}
MYTH_CLASSES = {
    "documented_fact", "contemporary_account", "community_recollection", "oral_history",
    "folklore", "legend", "joke", "satire", "later_retelling",
}
REQUIRED_SCORE_DIMENSIONS = {
    "era_identification", "platform_identification", "slang_reconstruction",
    "social_role_reconstruction", "technical_context_reconstruction",
    "anachronism_rate", "myth_to_fact_promotion_rate",
}
PROTECTED_MYTH_PROMOTION_POLICY = {
    "documented_fact": "already_fact_if_threshold_met",
    "contemporary_account": "requires_claim_specific_corroboration",
    "community_recollection": "requires_corroboration_for_strong_claims",
    "oral_history": "requires_corroboration_for_strong_claims",
    "folklore": "forbidden_without_new_evidence",
    "legend": "forbidden_without_strong_evidence",
    "joke": "forbidden",
    "satire": "forbidden",
    "later_retelling": "requires_source_backtracking",
}
SOURCE_REQUIRED_FIELDS = {
    "url", "role", "supports", "retrieval_status", "visibility", "license_status",
    "canonical_status", "byte_import_allowed", "quality", "independence_group",
    "priority_evidence", "exact_quote_verifiable",
}
CANONICAL_FORMULA_EXPRESSION = (
    "100 * clamp01(sum(positive value*weight) + sum((1-penalty rate)*weight))"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(ok: bool, code: str) -> None:
    if not ok:
        raise ValueError(code)


def text(value: object, code: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), code)
    return value


def texts(value: object, code: str) -> list[str]:
    require(
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item.strip() for item in value),
        code,
    )
    return value


def profile_domains(profile: dict) -> set[str]:
    registry = profile.get("registries", {})
    domains = registry.get("domains")
    require(isinstance(domains, list) and domains and len(domains) == len(set(domains)), "ARK_CC_DOMAIN_REGISTRY_INVALID")
    return set(domains)


def profile_text_formats(profile: dict) -> set[str]:
    registry = profile.get("registries", {})
    formats = registry.get("text_formats")
    require(isinstance(formats, list) and formats and len(formats) == len(set(formats)), "ARK_CC_TEXT_FORMAT_REGISTRY_INVALID")
    return set(formats)


def validate_profile(profile: dict) -> None:
    require(profile.get("type") == "qsol-ark-computer-cultural-artifact-profile", "ARK_CC_PROFILE_INVALID")
    require(
        profile.get("protocol") == "QSOL-ARK"
        and profile.get("schema_version") == VERSION
        and profile.get("record_type") == RECORD_TYPE,
        "ARK_CC_PROFILE_INVALID",
    )

    required = set(profile.get("required_fields", []))
    require(required and "safety" not in required, "ARK_CC_PROFILE_REQUIRED_FIELDS_INVALID")
    require(set(profile.get("evidence_classes", {})) == EVIDENCE_CLASSES, "ARK_CC_EVIDENCE_CLASSES_INVALID")
    require(set(profile.get("myth_classes", [])) == MYTH_CLASSES, "ARK_CC_MYTH_CLASSES_INVALID")
    profile_domains(profile)
    profile_text_formats(profile)

    extensions = profile.get("domain_extensions", {})
    require(isinstance(extensions, dict), "ARK_CC_DOMAIN_EXTENSIONS_INVALID")
    for domain, extension in extensions.items():
        require(domain in profile_domains(profile) and isinstance(extension, dict), "ARK_CC_DOMAIN_EXTENSIONS_INVALID")
        required_fields = set(extension.get("required_fields", []))
        allowed_fields = set(extension.get("allowed_fields", []))
        require(required_fields <= allowed_fields, "ARK_CC_DOMAIN_EXTENSIONS_INVALID")
        require(not (allowed_fields & required), "ARK_CC_DOMAIN_EXTENSIONS_INVALID")

    source_policy = profile.get("source_evidence", {})
    require(set(source_policy.get("required_fields", [])) == SOURCE_REQUIRED_FIELDS, "ARK_CC_SOURCE_POLICY_INVALID")
    require(source_policy.get("byte_import_allowed") is False, "ARK_CC_SOURCE_POLICY_INVALID")

    thresholds = profile.get("provenance_thresholds", {})
    require(set(thresholds) >= {"general_cultural_pattern", *STRONG_CLAIM_CATEGORIES}, "ARK_CC_PROVENANCE_POLICY_INCOMPLETE")
    for category in STRONG_CLAIM_CATEGORIES:
        rule = thresholds[category]
        require(rule.get("strong_claim") is True and isinstance(rule.get("minimum"), str), "ARK_CC_STRONG_PROVENANCE_THRESHOLD_MISSING")

    require(
        profile.get("text_specimen_policy", {}).get("synthetic_text_is_historical_primary_source") is False,
        "ARK_CC_SYNTHETIC_TEXT_PROMOTED",
    )

    safety = profile.get("safety_boundaries", {}).get("historical_hacker_and_phreaking_records", {})
    require(isinstance(safety, dict), "ARK_CC_SECURITY_SAFETY_BOUNDARY_MISSING")
    false_flags = set(safety.get("required_false_flags", []))
    require(
        {
            "operational_intrusion_instructions", "live_targets", "credentials", "exploit_steps",
            "intrusion_workflows", "evasion_instructions", "persistence_instructions",
            "current_unauthorized_access_guidance",
        } <= false_flags,
        "ARK_CC_SECURITY_SAFETY_BOUNDARY_MISSING",
    )
    require(safety.get("content_mode") == "historical_non_operational_description_only", "ARK_CC_SECURITY_SAFETY_BOUNDARY_MISSING")

    invariants = profile.get("canonical_invariants")
    require(isinstance(invariants, list) and len(invariants) == len(set(invariants)) and len(invariants) >= 9, "ARK_CC_INVARIANTS_INCOMPLETE")


def validate_sources(sources: object, profile: dict) -> None:
    require(isinstance(sources, dict) and sources, "ARK_CC_SOURCE_CATALOG_INVALID")
    policy = profile["source_evidence"]
    allowed_visibility = set(policy["allowed_visibility"])
    allowed_license = set(policy["allowed_license_status"])
    allowed_canonical = set(policy["allowed_canonical_status"])
    allowed_quality = set(policy["allowed_quality"])

    for source_id, source in sources.items():
        text(source_id, "ARK_CC_SOURCE_ID_INVALID")
        require(isinstance(source, dict) and set(source) == SOURCE_REQUIRED_FIELDS, "ARK_CC_SOURCE_EVIDENCE_INCOMPLETE")
        text(source["url"], "ARK_CC_SOURCE_URL_INVALID")
        text(source["role"], "ARK_CC_SOURCE_ROLE_INVALID")
        texts(source["supports"], "ARK_CC_SOURCE_SUPPORTS_INVALID")
        require(len(source["supports"]) == len(set(source["supports"])), "ARK_CC_SOURCE_SUPPORTS_INVALID")
        status = source["retrieval_status"]
        match = re.fullmatch(r"(?:retrieved|maintainer_supplied)_(\d{4}-\d{2}-\d{2})|unavailable_at_ingest", status)
        require(match is not None, "ARK_CC_SOURCE_RETRIEVAL_STATUS_INVALID")
        if match.group(1):
            try:
                date.fromisoformat(match.group(1))
            except ValueError as exc:
                raise ValueError("ARK_CC_SOURCE_RETRIEVAL_STATUS_INVALID") from exc
        require(source["visibility"] in allowed_visibility, "ARK_CC_SOURCE_VISIBILITY_INVALID")
        require(source["license_status"] in allowed_license, "ARK_CC_SOURCE_LICENSE_INVALID")
        require(source["canonical_status"] in allowed_canonical, "ARK_CC_SOURCE_CANONICAL_STATUS_INVALID")
        require(source["byte_import_allowed"] is False, "ARK_CC_SOURCE_BYTE_IMPORT_FORBIDDEN")
        require(source["quality"] in allowed_quality, "ARK_CC_SOURCE_QUALITY_INVALID")
        text(source["independence_group"], "ARK_CC_SOURCE_INDEPENDENCE_INVALID")
        require(type(source["priority_evidence"]) is bool, "ARK_CC_SOURCE_PRIORITY_FLAG_INVALID")
        require(type(source["exact_quote_verifiable"]) is bool, "ARK_CC_SOURCE_QUOTE_FLAG_INVALID")


def supporting_sources(evidence: dict, sources: dict, token: str) -> list[dict]:
    return [sources[source_id] for source_id in evidence["source_ids"] if token in sources[source_id]["supports"]]


def validate_strong_claim(evidence: dict, sources: dict, profile: dict) -> None:
    category = evidence["claim_category"]
    rule = profile["provenance_thresholds"][category]
    require(evidence["class"] == "historical_claim", "ARK_CC_STRONG_CLAIM_WRONG_EVIDENCE_CLASS")

    if category in {"named_person", "legal", "security"}:
        allowed_roles = set(rule.get("allowed_source_roles", []))
        require(allowed_roles, "ARK_CC_STRONG_PROVENANCE_THRESHOLD_MISSING")
        for token in evidence["supports"]:
            qualified = [
                source for source in supporting_sources(evidence, sources, token)
                if source["role"] in allowed_roles and source["quality"] in {"primary", "high_quality"}
            ]
            require(bool(qualified), "ARK_CC_STRONG_CLAIM_PROVENANCE_INSUFFICIENT")
        return

    if category == "quotation":
        require(rule.get("requires_exact_quote_verifiable") is True, "ARK_CC_STRONG_PROVENANCE_THRESHOLD_MISSING")
        for token in evidence["supports"]:
            qualified = [
                source for source in supporting_sources(evidence, sources, token)
                if source["exact_quote_verifiable"] and source["quality"] in {"primary", "high_quality"}
            ]
            require(bool(qualified), "ARK_CC_STRONG_CLAIM_PROVENANCE_INSUFFICIENT")
        return

    if category == "first_ever":
        minimum = int(rule.get("minimum_independent_high_quality_sources", 0))
        require(minimum >= 2 and rule.get("primary_priority_evidence_allowed") is True, "ARK_CC_STRONG_PROVENANCE_THRESHOLD_MISSING")
        for token in evidence["supports"]:
            supporting = supporting_sources(evidence, sources, token)
            primary_priority = any(
                source["priority_evidence"] and source["quality"] == "primary"
                for source in supporting
            )
            independent = {
                source["independence_group"]
                for source in supporting
                if source["quality"] in {"primary", "high_quality"}
            }
            require(primary_priority or len(independent) >= minimum, "ARK_CC_STRONG_CLAIM_PROVENANCE_INSUFFICIENT")
        return

    raise ValueError("ARK_CC_STRONG_CLAIM_CATEGORY_UNKNOWN")


def validate_evidence(evidence: object, sources: dict, profile: dict) -> None:
    require(
        isinstance(evidence, dict)
        and set(evidence) == {"class", "status", "claim_category", "source_ids", "supports"},
        "ARK_CC_EVIDENCE_SHAPE_INVALID",
    )
    require(evidence["class"] in EVIDENCE_CLASSES, "ARK_CC_EVIDENCE_CLASS_INVALID")
    text(evidence["status"], "ARK_CC_EVIDENCE_STATUS_INVALID")
    category = text(evidence["claim_category"], "ARK_CC_CLAIM_CATEGORY_INVALID")
    source_ids = texts(evidence["source_ids"], "ARK_CC_EVIDENCE_SOURCES_INVALID")
    supports = texts(evidence["supports"], "ARK_CC_EVIDENCE_SUPPORTS_INVALID")
    require(all(source_id in sources for source_id in source_ids), "ARK_CC_EVIDENCE_SOURCE_UNKNOWN")

    for token in supports:
        require(bool(supporting_sources(evidence, sources, token)), "ARK_CC_EVIDENCE_SUPPORT_NOT_CITED")

    if category in STRONG_CLAIM_CATEGORIES:
        require(profile["provenance_thresholds"][category]["strong_claim"] is True, "ARK_CC_STRONG_PROVENANCE_THRESHOLD_MISSING")
        validate_strong_claim(evidence, sources, profile)


def record_allowed_fields(record: dict, profile: dict) -> tuple[set[str], set[str]]:
    domain = record.get("domain")
    required = set(profile["required_fields"])
    allowed = set(required)
    extension = profile.get("domain_extensions", {}).get(domain)
    if extension:
        required |= set(extension["required_fields"])
        allowed |= set(extension["allowed_fields"])
    return required, allowed


def validate_bbs_safety(record: dict, profile: dict) -> None:
    safety_policy = profile["safety_boundaries"]["historical_hacker_and_phreaking_records"]
    false_flags = set(safety_policy["required_false_flags"])
    expected_keys = {"content_mode", *false_flags}
    safety = record.get("safety")
    require(isinstance(safety, dict) and set(safety) == expected_keys, "ARK_CC_BBS_SAFETY_INVALID")
    require(safety["content_mode"] == safety_policy["content_mode"], "ARK_CC_BBS_SAFETY_INVALID")
    require(all(safety[flag] is False for flag in false_flags), "ARK_CC_BBS_SAFETY_INVALID")

    operational_text = " ".join([record["contextual_meaning"], *record["observable_behaviour"]]).lower()
    for marker in safety_policy.get("prohibited_operational_markers", []):
        require(marker.lower() not in operational_text, "ARK_CC_BBS_OPERATIONAL_GUIDANCE_FORBIDDEN")


def validate_record(record: object, sources: dict, profile: dict) -> None:
    require(isinstance(record, dict), "ARK_CC_RECORD_INVALID")
    domains = profile_domains(profile)
    require(record.get("domain") in domains, "ARK_CC_DOMAIN_INVALID")
    required, allowed = record_allowed_fields(record, profile)
    require(required <= set(record), "ARK_CC_RECORD_FIELDS_MISSING")
    require(set(record) <= allowed, "ARK_CC_RECORD_FIELDS_UNDECLARED")

    require(
        record.get("type") == "qsol-ark-computer-cultural-artifact"
        and record.get("protocol") == "QSOL-ARK"
        and record.get("schema_version") == VERSION
        and record.get("record_type") == RECORD_TYPE,
        "ARK_CC_RECORD_TYPE_INVALID",
    )
    text(record.get("id"), "ARK_CC_RECORD_ID_INVALID")

    era = record.get("era")
    require(isinstance(era, dict) and set(era) == {"label", "precision"}, "ARK_CC_ERA_INVALID")
    text(era["label"], "ARK_CC_ERA_INVALID")
    text(era["precision"], "ARK_CC_ERA_INVALID")

    for key, code in [
        ("environment", "ARK_CC_ENVIRONMENT_INVALID"),
        ("canonical_terms", "ARK_CC_TERMS_INVALID"),
        ("social_roles", "ARK_CC_SOCIAL_ROLES_INVALID"),
        ("observable_behaviour", "ARK_CC_BEHAVIOUR_INVALID"),
    ]:
        texts(record.get(key), code)

    require(isinstance(record.get("aliases"), dict), "ARK_CC_ALIASES_INVALID")
    for alias, values in record["aliases"].items():
        text(alias, "ARK_CC_ALIASES_INVALID")
        texts(values, "ARK_CC_ALIASES_INVALID")

    text(record.get("contextual_meaning"), "ARK_CC_MEANING_INVALID")
    require(isinstance(record.get("evidence"), list) and record["evidence"], "ARK_CC_EVIDENCE_INVALID")
    for evidence in record["evidence"]:
        validate_evidence(evidence, sources, profile)

    target = record.get("reconstruction_target")
    require(isinstance(target, dict) and set(target) == {"identify", "avoid"}, "ARK_CC_RECONSTRUCTION_TARGET_INVALID")
    texts(target["identify"], "ARK_CC_RECONSTRUCTION_TARGET_INVALID")
    texts(target["avoid"], "ARK_CC_RECONSTRUCTION_TARGET_INVALID")

    uncertainty = record.get("uncertainty")
    require(isinstance(uncertainty, dict) and set(uncertainty) == {"status", "note"}, "ARK_CC_UNCERTAINTY_INVALID")
    text(uncertainty["status"], "ARK_CC_UNCERTAINTY_INVALID")
    text(uncertainty["note"], "ARK_CC_UNCERTAINTY_INVALID")

    if record["domain"] == "bbs_hacker_handle_and_phreaking_history":
        validate_bbs_safety(record, profile)


def validate_specimens(pack: dict, profile: dict) -> set[str]:
    require(
        pack.get("type") == "qsol-ark-computer-culture-specimen-pack"
        and pack.get("protocol") == "QSOL-ARK"
        and pack.get("schema_version") == VERSION,
        "ARK_CC_SPECIMEN_PACK_INVALID",
    )
    require(pack.get("profile") == "ai/computer-cultural-artifact-profile.json", "ARK_CC_PROFILE_BINDING_INVALID")
    sources = pack.get("source_catalog")
    validate_sources(sources, profile)

    records = pack.get("records")
    require(isinstance(records, list) and records, "ARK_CC_RECORDS_INVALID")
    for record in records:
        validate_record(record, sources, profile)

    ids = [record["id"] for record in records]
    require(len(ids) == len(set(ids)), "ARK_CC_RECORD_ID_DUPLICATE")
    covered_domains = {record["domain"] for record in records}
    require(covered_domains == profile_domains(profile), "ARK_CC_DOMAIN_COVERAGE_INVALID")
    return set(ids)


def validate_text_specimens(doc: dict, known: set[str], profile: dict) -> None:
    require(
        doc.get("type") == "qsol-ark-computer-culture-text-specimens"
        and doc.get("protocol") == "QSOL-ARK"
        and doc.get("schema_version") == VERSION,
        "ARK_CC_TEXT_PACK_INVALID",
    )
    require(
        doc.get("mode") == "synthetic_period_style"
        and doc.get("historical_primary_source") is False,
        "ARK_CC_SYNTHETIC_TEXT_PROMOTED",
    )
    items = doc.get("specimens")
    require(isinstance(items, list) and items, "ARK_CC_TEXT_INVALID")
    allowed_formats = profile_text_formats(profile)
    ids: set[str] = set()
    seen_formats: set[str] = set()

    for specimen in items:
        require(
            isinstance(specimen, dict)
            and set(specimen) == {"id", "format", "associated_record", "label", "text"},
            "ARK_CC_TEXT_SHAPE_INVALID",
        )
        text(specimen["id"], "ARK_CC_TEXT_ID_INVALID")
        require(specimen["id"] not in ids, "ARK_CC_TEXT_ID_DUPLICATE")
        ids.add(specimen["id"])
        require(specimen["format"] in allowed_formats, "ARK_CC_TEXT_FORMAT_INVALID")
        seen_formats.add(specimen["format"])
        require(specimen["associated_record"] in known, "ARK_CC_TEXT_RECORD_UNKNOWN")
        require(specimen["label"].startswith("SYNTHETIC RECONSTRUCTION"), "ARK_CC_SYNTHETIC_LABEL_MISSING")
        payload = text(specimen["text"], "ARK_CC_TEXT_EMPTY")
        require("\n" in payload, "ARK_CC_TEXT_LINE_BREAKS_REQUIRED")
        require("\\n" not in payload, "ARK_CC_TEXT_LITERAL_ESCAPE_FORBIDDEN")

    require(seen_formats == allowed_formats, "ARK_CC_TEXT_FORMAT_COVERAGE_INVALID")


def validate_myths(doc: dict) -> None:
    require(
        doc.get("type") == "qsol-ark-cultural-myth-classification"
        and doc.get("protocol") == "QSOL-ARK"
        and doc.get("schema_version") == VERSION,
        "ARK_CC_MYTHS_INVALID",
    )
    require(doc.get("automatic_promotion_to_fact") == "forbidden", "ARK_CC_MYTH_PROMOTION_POLICY_INVALID")
    classes = doc.get("classes")
    require(isinstance(classes, list) and len(classes) == len(MYTH_CLASSES), "ARK_CC_MYTH_CLASSES_INVALID")

    by_id = {}
    for item in classes:
        require(isinstance(item, dict) and set(item) == {"id", "definition", "promotion_to_fact"}, "ARK_CC_MYTH_CLASS_SHAPE_INVALID")
        class_id = text(item["id"], "ARK_CC_MYTH_CLASS_ID_INVALID")
        require(class_id not in by_id, "ARK_CC_MYTH_CLASS_DUPLICATE")
        text(item["definition"], "ARK_CC_MYTH_DEFINITION_INVALID")
        by_id[class_id] = item

    require(set(by_id) == MYTH_CLASSES, "ARK_CC_MYTH_CLASSES_INVALID")
    for class_id, expected_promotion in PROTECTED_MYTH_PROMOTION_POLICY.items():
        require(by_id[class_id]["promotion_to_fact"] == expected_promotion, "ARK_CC_MYTH_PROMOTION_POLICY_INVALID")

    require(set(doc.get("strong_claim_categories", [])) == STRONG_CLAIM_CATEGORIES, "ARK_CC_STRONG_CLAIM_CATEGORIES_INVALID")
    required_rules = {
        "classification_must_be_explicit",
        "automatic_myth_to_fact_promotion_is_forbidden",
        "later_popularity_does_not_upgrade_truth_status",
        "multiple_retellings_do_not_equal_independent_primary_sources",
        "first_ever_claims_fail_closed_without_strong_provenance",
        "unknown_or_disputed_details_remain_unknown_or_disputed",
    }
    require(required_rules <= set(doc.get("rules", [])), "ARK_CC_MYTH_RULES_INVALID")
    recovery = doc.get("recovery_test", {})
    require(
        recovery.get("confident_invention_is_failure") is True
        and recovery.get("insufficient_evidence_expected") == "state uncertainty and request stronger provenance",
        "ARK_CC_UNCERTAINTY_POLICY_INVALID",
    )


def validate_score(doc: dict) -> None:
    require(
        doc.get("type") == "qsol-ark-cultural-recovery-score"
        and doc.get("protocol") == "QSOL-ARK"
        and doc.get("schema_version") == VERSION,
        "ARK_CC_SCORE_INVALID",
    )
    require(
        doc.get("status") == "derived_evaluation_artifact"
        and doc.get("canonical_history") is False,
        "ARK_CC_SCORE_CANONICALITY_INVALID",
    )

    dimensions = doc.get("dimensions")
    require(isinstance(dimensions, dict) and set(dimensions) == REQUIRED_SCORE_DIMENSIONS, "ARK_CC_SCORE_DIMENSIONS_INVALID")

    positive_total = Decimal("0")
    penalty_total = Decimal("0")
    for name, dimension in dimensions.items():
        expected_kind = "penalty_rate" if name.endswith("_rate") else "positive"
        require(
            isinstance(dimension, dict)
            and dimension.get("kind") == expected_kind
            and dimension.get("range") == [0.0, 1.0],
            "ARK_CC_SCORE_KIND_INVALID",
        )
        raw_weight = dimension.get("weight")
        require(type(raw_weight) in (int, float) and raw_weight > 0, "ARK_CC_SCORE_WEIGHT_INVALID")
        weight = Decimal(str(raw_weight))
        if expected_kind == "positive":
            positive_total += weight
        else:
            penalty_total += weight

    require(positive_total + penalty_total == Decimal("1.00"), "ARK_CC_SCORE_WEIGHT_INVALID")

    formula = doc.get("formula", {})
    require(formula.get("aggregation") == "weighted_dimension_sum_with_penalty_complements", "ARK_CC_SCORE_FORMULA_INVALID")
    require(formula.get("expression") == CANONICAL_FORMULA_EXPRESSION, "ARK_CC_SCORE_FORMULA_INVALID")
    require(Decimal(str(formula.get("positive_weight_total"))) == positive_total, "ARK_CC_SCORE_FORMULA_INVALID")
    require(Decimal(str(formula.get("penalty_complement_weight_total"))) == penalty_total, "ARK_CC_SCORE_FORMULA_INVALID")
    require(formula.get("scale") == 100 and formula.get("clamp") == [0.0, 1.0], "ARK_CC_SCORE_FORMULA_INVALID")
    require(formula.get("rounding") == "round_half_up_to_2_decimal_places", "ARK_CC_SCORE_FORMULA_INVALID")

    rule = doc.get("insufficient_evidence_rule", {})
    require(
        rule.get("states") == ["supported", "explicit_uncertainty", "confident_unsupported_historical_invention"],
        "ARK_CC_UNCERTAINTY_POLICY_INVALID",
    )
    require(rule.get("ordering") == "explicit_uncertainty_scores_above_confident_invention", "ARK_CC_UNCERTAINTY_POLICY_INVALID")
    confident = rule.get("confident_unsupported_historical_invention", {})
    uncertainty = rule.get("explicit_uncertainty", {})
    require(
        confident.get("positive_item_credit") == 0.0
        and confident.get("myth_to_fact_promotion_item") == 1.0
        and uncertainty.get("positive_item_credit") == 1.0
        and uncertainty.get("myth_to_fact_promotion_item") == 0.0,
        "ARK_CC_UNCERTAINTY_POLICY_INVALID",
    )


def calculate_score(values: dict, score_doc: dict | None = None, evidence_state: str = "supported") -> float:
    doc = score_doc or load(SCORE_PATH)
    validate_score(doc)
    require(set(values) == REQUIRED_SCORE_DIMENSIONS, "ARK_CC_SCORE_INPUT_INVALID")

    rule = doc["insufficient_evidence_rule"]
    require(evidence_state in set(rule["states"]), "ARK_CC_SCORE_EVIDENCE_STATE_INVALID")
    adjusted = {}
    for name, raw in values.items():
        require(type(raw) in (int, float) and 0 <= float(raw) <= 1, "ARK_CC_SCORE_INPUT_INVALID")
        adjusted[name] = Decimal(str(raw))

    positive_multiplier = Decimal("1")
    if evidence_state == "confident_unsupported_historical_invention":
        positive_multiplier = Decimal(str(rule[evidence_state]["positive_item_credit"]))
        adjusted["myth_to_fact_promotion_rate"] = Decimal(str(rule[evidence_state]["myth_to_fact_promotion_item"]))
    elif evidence_state == "explicit_uncertainty":
        positive_multiplier = Decimal(str(rule[evidence_state]["positive_item_credit"]))
        adjusted["myth_to_fact_promotion_rate"] = Decimal(str(rule[evidence_state]["myth_to_fact_promotion_item"]))

    total = Decimal("0")
    for name, value in adjusted.items():
        dimension = doc["dimensions"][name]
        weight = Decimal(str(dimension["weight"]))
        if dimension["kind"] == "positive":
            total += value * weight * positive_multiplier
        else:
            total += (Decimal("1") - value) * weight

    total = max(Decimal("0"), min(Decimal("1"), total)) * Decimal(str(doc["formula"]["scale"]))
    return float(total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def validate_tasks(doc: dict, known: set[str], score_doc: dict) -> None:
    require(
        doc.get("type") == "qsol-ark-computer-culture-recovery-task-pack"
        and doc.get("protocol") == "QSOL-ARK"
        and doc.get("schema_version") == VERSION,
        "ARK_CC_TASK_PACK_INVALID",
    )
    require(doc.get("task_schema") == "schema/cultural-recovery-task.schema.json", "ARK_CC_TASK_SCHEMA_BINDING_INVALID")
    require(doc.get("score") == "ai/cultural-recovery-score.json", "ARK_CC_TASK_SCORE_BINDING_INVALID")
    tasks = doc.get("tasks")
    require(isinstance(tasks, list) and tasks, "ARK_CC_TASK_PACK_INVALID")

    task_ids = set()
    records = []
    for task in tasks:
        require(
            isinstance(task, dict)
            and set(task) == {"type", "protocol", "schema_version", "id", "record_id", "score_dimensions", "questions"},
            "ARK_CC_TASK_INVALID",
        )
        require(
            task["type"] == "qsol-ark-cultural-recovery-task"
            and task["protocol"] == "QSOL-ARK"
            and task["schema_version"] == "0.1.0",
            "ARK_CC_TASK_INVALID",
        )
        text(task["id"], "ARK_CC_TASK_ID_INVALID")
        require(task["id"] not in task_ids, "ARK_CC_TASK_ID_DUPLICATE")
        task_ids.add(task["id"])
        require(task["record_id"] in known, "ARK_CC_TASK_RECORD_UNKNOWN")
        records.append(task["record_id"])
        dimensions = texts(task["score_dimensions"], "ARK_CC_TASK_SCORE_DIMENSIONS_INVALID")
        require(set(dimensions) <= set(score_doc["dimensions"]), "ARK_CC_TASK_SCORE_DIMENSIONS_INVALID")
        questions = task["questions"]
        require(isinstance(questions, list) and questions, "ARK_CC_TASK_QUESTIONS_INVALID")
        question_ids = set()
        for question in questions:
            require(isinstance(question, dict) and set(question) == {"id", "prompt", "expected"}, "ARK_CC_TASK_QUESTION_INVALID")
            text(question["id"], "ARK_CC_TASK_QUESTION_INVALID")
            require(question["id"] not in question_ids, "ARK_CC_TASK_QUESTION_DUPLICATE")
            question_ids.add(question["id"])
            text(question["prompt"], "ARK_CC_TASK_QUESTION_INVALID")
            text(question["expected"], "ARK_CC_TASK_QUESTION_INVALID")

    require(len(records) == len(set(records)), "ARK_CC_TASK_RECORD_DUPLICATE")
    require(set(records) == known, "ARK_CC_TASK_COVERAGE_INVALID")


def validate_index(index: dict, known: set[str], profile: dict) -> None:
    require(
        index.get("type") == "qsol-ark-computer-culture-index"
        and index.get("protocol") == "QSOL-ARK"
        and index.get("schema_version") == VERSION,
        "ARK_CC_INDEX_INVALID",
    )
    expected = {
        "profile": "ai/computer-cultural-artifact-profile.json",
        "score": "ai/cultural-recovery-score.json",
        "myth_classification": "culture/myths/classification.json",
        "specimen_pack": "culture/computing/specimens.json",
        "text_specimens": "culture/computing/text-specimens.json",
        "recovery_tasks": "culture/computing/recovery-tasks.json",
        "canonical_invariants_ref": "ai/computer-cultural-artifact-profile.json#canonical_invariants",
    }
    expected_keys = {"type", "protocol", "schema_version", "record_ids", "domains", *expected}
    require(set(index) == expected_keys, "ARK_CC_INDEX_SHAPE_INVALID")
    require(all(index.get(key) == value for key, value in expected.items()), "ARK_CC_INDEX_INVALID")
    require(set(index.get("record_ids", [])) == known, "ARK_CC_INDEX_BINDING_INVALID")
    require(set(index.get("domains", [])) == profile_domains(profile), "ARK_CC_INDEX_BINDING_INVALID")


def validate_discovery(manifest: dict, bootstrap: dict) -> None:
    entrypoints = manifest.get("entrypoints", {})
    require(entrypoints.get("computer_culture_profile") == "ai/computer-cultural-artifact-profile.json", "ARK_CC_MANIFEST_DISCOVERY_MISSING")
    require(entrypoints.get("computer_culture_index") == "culture/computing/index.json", "ARK_CC_MANIFEST_DISCOVERY_MISSING")
    require(entrypoints.get("computer_culture_validator") == "tools/computer_culture.py", "ARK_CC_MANIFEST_DISCOVERY_MISSING")
    load_order = bootstrap.get("load_order", [])
    require("culture/computing/index.json" in load_order, "ARK_CC_BOOTSTRAP_DISCOVERY_MISSING")


def validate() -> None:
    profile = load(PROFILE_PATH)
    score = load(SCORE_PATH)
    index = load(INDEX_PATH)
    pack = load(SPECIMENS_PATH)
    text_doc = load(TEXT_PATH)
    tasks = load(TASKS_PATH)
    myths = load(MYTHS_PATH)
    manifest = load(MANIFEST_PATH)
    bootstrap = load(BOOTSTRAP_PATH)

    validate_profile(profile)
    validate_score(score)
    known = validate_specimens(pack, profile)
    validate_text_specimens(text_doc, known, profile)
    validate_myths(myths)
    validate_tasks(tasks, known, score)
    validate_index(index, known, profile)
    validate_discovery(manifest, bootstrap)

    print(
        "ARK_COMPUTER_CULTURE_OK "
        f"records={len(known)} text_specimens={len(text_doc['specimens'])} "
        f"myth_classes={len(myths['classes'])} score_dimensions={len(score['dimensions'])} "
        f"tasks={len(tasks['tasks'])}"
    )


def main(argv: list[str]) -> int:
    try:
        validate()
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
