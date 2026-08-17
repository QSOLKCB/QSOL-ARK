#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fail-closed validator for QSOL-ARK PR #4 historical-system profiles."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_IDS = {
    "system.commodore.c64",
    "system.commodore.amiga500",
    "system.ibm.pc_xt_5160",
    "environment.digital_research.cpm_2_2",
    "environment.unix.v7_pdp11",
}
SCOPES = {"hardware_system", "software_environment"}
EVIDENCE = {
    "hardware_fact",
    "documented_software_behaviour",
    "emulator_behaviour",
    "compatibility_layer_behaviour",
    "reconstruction_inference",
    "unknown",
}
HRE = {
    "exact_reproduction",
    "functional_equivalence",
    "historically_plausible_approximation",
    "emulator_assisted_reproduction",
    "modern_compatibility_layer",
    "impossible_or_unsupported",
}
RULES = {
    "hardware_fact_is_not_emulator_behaviour",
    "emulator_behaviour_is_not_original_hardware_fact",
    "compatibility_layer_behaviour_is_not_original_software_behaviour",
    "reconstruction_inference_must_remain_labelled_inference",
    "software_environment_must_not_be_rewritten_as_one_canonical_machine",
    "exact_reproduction_requires_sufficient_public_licensed_inspectable_evidence",
    "rom_firmware_os_and_disk_image_bytes_are_not_embedded_without_resolved_rights",
    "historical_system_profiles_are_metadata_and_context_not_original_system_images",
    "computational_archaeology_tiers_describe_ark_recovery_hosts_not_native_historical_execution",
    "unknown_or_model_dependent_hardware_details_remain_unknown_or_variable",
}
RIGHTS = {
    "source_bytes_copied",
    "rom_bytes_copied",
    "firmware_bytes_copied",
    "proprietary_software_copied",
    "disk_image_bytes_copied",
    "binary_distribution_copied",
}
VALIDATION_TIER = "T4"
VALIDATION_CAPABILITY = "validate_historical_system_contracts"
VALIDATION_ENTRYPOINT = "tools/systems.py"

PROFILE_BASE_KEYS = {
    "type",
    "protocol",
    "schema_version",
    "id",
    "name",
    "scope",
    "era",
    "introduced_or_release_year",
    "reconstruction_target",
    "technical_context",
    "claim_partitions",
    "source_evidence",
    "uncertainties",
    "rights",
    "emulator_or_reimplementation",
    "recovery_equivalence",
    "computational_archaeology_mapping",
}
TECHNICAL_CONTEXT_KEYS = {
    "cpu_family",
    "architecture_word_size_bits",
    "endianness",
    "logical_address_space",
    "memory",
    "storage_model",
    "display_hardware",
    "audio_hardware",
    "input_model",
    "executable_or_load_model",
    "filesystem",
    "boot_process",
    "programming_environment",
    "timing_constraints",
    "rom_or_os_assumptions",
}
TECHNICAL_CONTEXT_EXTRA = {
    "system.ibm.pc_xt_5160": {"external_data_bus_bits"},
}
SOURCE_KEYS = {
    "id",
    "source_type",
    "title",
    "url",
    "supports",
    "visibility",
    "license",
    "epistemic_class",
    "canonical_or_derived",
    "byte_import_allowed",
}
EMULATOR_KEYS = {"used_for_canonical_profile", "identity", "version", "source", "license", "limitations"}
RECOVERY_EQUIVALENCE_KEYS = {"current_class", "exact_reproduction_claimed", "reason"}
ARCHAEOLOGY_MAPPING_KEYS = {
    "profile_validation_tier",
    "profile_validation_capability",
    "tiers_are_ark_recovery_hosts_not_native_historical_execution",
    "native_execution_claimed",
}
SCOPE_NOTES_KEYS = {"hardware_variability", "canonical_machine", "reason"}
TASK_KEYS = {"type", "protocol", "schema_version", "id", "purpose", "systems", "cases", "global_boundaries"}
CASE_KEYS = {"system_id", "prompt", "expected_equivalence"}
BOUNDARY_KEYS = {
    "third_party_system_bytes_required",
    "emulator_output_is_original_history",
    "exact_reproduction_claimed",
    "ark_recovery_tier_is_native_historical_execution",
    "software_environment_must_preserve_hardware_variability",
}


def load(path: str | Path) -> dict:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return json.loads(p.read_text(encoding="utf-8"))


def req(ok: bool, code: str) -> None:
    if not ok:
        raise ValueError(code)


def exact_keys(value: object, keys: set[str], code: str) -> dict:
    req(isinstance(value, dict) and set(value) == keys, code)
    return value


def nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: object, *, allow_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(nonempty_string(item) for item in value)
    )


def safe_path(value: object) -> Path:
    req(nonempty_string(value), "ARK_SYSTEM_PATH_INVALID")
    p = Path(value)
    req(not p.is_absolute() and ".." not in p.parts and p.parts[0] == "systems", "ARK_SYSTEM_PATH_INVALID")
    full = ROOT / p
    req(full.is_file(), "ARK_SYSTEM_PATH_MISSING")
    return full


def validate_recovery_tier_binding(registry: dict | None = None) -> dict:
    if registry is None:
        registry = load("ai/recovery-tiers.json")
    tiers = registry.get("tiers")
    req(isinstance(tiers, list) and tiers, "ARK_SYSTEM_ARCHAEOLOGY_MAPPING_INVALID")
    candidates = []
    for tier in tiers:
        req(isinstance(tier, dict), "ARK_SYSTEM_ARCHAEOLOGY_MAPPING_INVALID")
        capabilities = tier.get("capabilities", [])
        entrypoints = tier.get("entrypoints", [])
        if tier.get("implemented") is True and VALIDATION_CAPABILITY in capabilities:
            candidates.append(tier)
        if tier.get("id") == VALIDATION_TIER:
            req(tier.get("implemented") is True, "ARK_SYSTEM_ARCHAEOLOGY_MAPPING_INVALID")
            req(VALIDATION_CAPABILITY in capabilities, "ARK_SYSTEM_ARCHAEOLOGY_MAPPING_INVALID")
            req(VALIDATION_ENTRYPOINT in entrypoints, "ARK_SYSTEM_ARCHAEOLOGY_MAPPING_INVALID")
    req(candidates, "ARK_SYSTEM_ARCHAEOLOGY_MAPPING_INVALID")
    selected = min(candidates, key=lambda tier: tier.get("rank", 10**9))
    req(selected.get("id") == VALIDATION_TIER, "ARK_SYSTEM_ARCHAEOLOGY_MAPPING_INVALID")
    return selected


def validate_policy(p: dict) -> None:
    exact_keys(
        p,
        {
            "type",
            "protocol",
            "schema_version",
            "purpose",
            "profile_scopes",
            "evidence_classes",
            "historical_recovery_equivalence",
            "rules",
            "forbidden_embedded_byte_classes",
            "seed_exact_reproduction_allowed",
        },
        "ARK_SYSTEM_POLICY_INVALID",
    )
    req(
        p.get("type") == "qsol-ark-historical-system-policy"
        and p.get("protocol") == "QSOL-ARK"
        and p.get("schema_version") == "0.4.0",
        "ARK_SYSTEM_POLICY_INVALID",
    )
    req(nonempty_string(p.get("purpose")), "ARK_SYSTEM_POLICY_INVALID")
    req(set(p.get("profile_scopes", [])) == SCOPES, "ARK_SYSTEM_POLICY_INVALID")
    req(set(p.get("evidence_classes", [])) == EVIDENCE, "ARK_SYSTEM_POLICY_INVALID")
    req(set(p.get("historical_recovery_equivalence", [])) == HRE, "ARK_SYSTEM_POLICY_INVALID")
    req(set(p.get("rules", [])) == RULES, "ARK_SYSTEM_POLICY_INVALID")
    req(string_list(p.get("forbidden_embedded_byte_classes")), "ARK_SYSTEM_POLICY_INVALID")
    req(p.get("seed_exact_reproduction_allowed") is False, "ARK_SYSTEM_EXACT_REPRODUCTION_UNSUPPORTED")


def validate_technical_context(profile_id: str, value: object) -> None:
    keys = TECHNICAL_CONTEXT_KEYS | TECHNICAL_CONTEXT_EXTRA.get(profile_id, set())
    ctx = exact_keys(value, keys, "ARK_SYSTEM_PROFILE_SHAPE_INVALID")
    scalar_strings = {
        "cpu_family",
        "endianness",
        "logical_address_space",
        "memory",
        "executable_or_load_model",
        "filesystem",
        "boot_process",
        "rom_or_os_assumptions",
    }
    list_strings = {"storage_model", "display_hardware", "audio_hardware", "input_model", "programming_environment", "timing_constraints"}
    req(all(nonempty_string(ctx[key]) for key in scalar_strings), "ARK_SYSTEM_PROFILE_SHAPE_INVALID")
    req(all(string_list(ctx[key]) for key in list_strings), "ARK_SYSTEM_PROFILE_SHAPE_INVALID")
    req(isinstance(ctx["architecture_word_size_bits"], int) and ctx["architecture_word_size_bits"] > 0, "ARK_SYSTEM_PROFILE_SHAPE_INVALID")
    if "external_data_bus_bits" in ctx:
        req(isinstance(ctx["external_data_bus_bits"], int) and ctx["external_data_bus_bits"] > 0, "ARK_SYSTEM_PROFILE_SHAPE_INVALID")


def validate_source(source: object) -> None:
    s = exact_keys(source, SOURCE_KEYS, "ARK_SYSTEM_SOURCE_INVALID")
    req(nonempty_string(s["id"]), "ARK_SYSTEM_SOURCE_INVALID")
    req(nonempty_string(s["source_type"]), "ARK_SYSTEM_SOURCE_INVALID")
    req(nonempty_string(s["title"]), "ARK_SYSTEM_SOURCE_INVALID")
    req(isinstance(s["url"], str) and s["url"].startswith("https://"), "ARK_SYSTEM_SOURCE_INVALID")
    req(string_list(s["supports"]), "ARK_SYSTEM_SOURCE_INVALID")
    req(s["visibility"] == "public", "ARK_SYSTEM_SOURCE_INVALID")
    req(nonempty_string(s["license"]), "ARK_SYSTEM_SOURCE_INVALID")
    req(s["license"] == "UNRESOLVED", "ARK_SYSTEM_SOURCE_INVALID")
    req(s["epistemic_class"] == "external_historical_documentation", "ARK_SYSTEM_SOURCE_INVALID")
    req(s["canonical_or_derived"] == "derived", "ARK_SYSTEM_SOURCE_INVALID")
    req(s["byte_import_allowed"] is False, "ARK_SYSTEM_FORBIDDEN_BYTES")


def validate_profile(p: dict) -> None:
    scope = p.get("scope")
    expected_top = set(PROFILE_BASE_KEYS)
    if scope == "software_environment":
        expected_top.add("scope_notes")
    exact_keys(p, expected_top, "ARK_SYSTEM_PROFILE_SHAPE_INVALID")
    req(
        p.get("type") == "qsol-ark-historical-system-profile"
        and p.get("protocol") == "QSOL-ARK"
        and p.get("schema_version") == "0.4.0",
        "ARK_SYSTEM_PROFILE_INVALID",
    )
    req(p.get("id") in PROFILE_IDS and scope in SCOPES, "ARK_SYSTEM_PROFILE_INVALID")
    req(nonempty_string(p.get("name")) and string_list(p.get("era")), "ARK_SYSTEM_PROFILE_INVALID")
    req(isinstance(p.get("introduced_or_release_year"), int), "ARK_SYSTEM_PROFILE_INVALID")
    req(nonempty_string(p.get("reconstruction_target")), "ARK_SYSTEM_PROFILE_INVALID")

    validate_technical_context(p["id"], p["technical_context"])

    partitions = exact_keys(p["claim_partitions"], EVIDENCE, "ARK_SYSTEM_EVIDENCE_PARTITION_INVALID")
    req(all(string_list(value, allow_empty=True) for value in partitions.values()), "ARK_SYSTEM_EVIDENCE_PARTITION_INVALID")

    req(string_list(p["uncertainties"], allow_empty=True), "ARK_SYSTEM_PROFILE_SHAPE_INVALID")

    rights = exact_keys(p["rights"], RIGHTS, "ARK_SYSTEM_FORBIDDEN_BYTES")
    req(all(rights[key] is False for key in RIGHTS), "ARK_SYSTEM_FORBIDDEN_BYTES")

    emulator = exact_keys(p["emulator_or_reimplementation"], EMULATOR_KEYS, "ARK_EMULATOR_PROMOTED_TO_HISTORY")
    req(emulator["used_for_canonical_profile"] is False, "ARK_EMULATOR_PROMOTED_TO_HISTORY")
    req(all(emulator[key] is None for key in ("identity", "version", "source", "license")), "ARK_EMULATOR_PROMOTED_TO_HISTORY")
    req(nonempty_string(emulator["limitations"]), "ARK_EMULATOR_PROMOTED_TO_HISTORY")

    equivalence = exact_keys(p["recovery_equivalence"], RECOVERY_EQUIVALENCE_KEYS, "ARK_SYSTEM_EQUIVALENCE_INVALID")
    req(equivalence["current_class"] == "historically_plausible_approximation", "ARK_SYSTEM_EQUIVALENCE_INVALID")
    req(equivalence["exact_reproduction_claimed"] is False, "ARK_SYSTEM_EXACT_REPRODUCTION_UNSUPPORTED")
    req(nonempty_string(equivalence["reason"]), "ARK_SYSTEM_EQUIVALENCE_INVALID")

    mapping = exact_keys(p["computational_archaeology_mapping"], ARCHAEOLOGY_MAPPING_KEYS, "ARK_SYSTEM_ARCHAEOLOGY_MAPPING_INVALID")
    req(mapping["profile_validation_tier"] == VALIDATION_TIER, "ARK_SYSTEM_ARCHAEOLOGY_MAPPING_INVALID")
    req(mapping["profile_validation_capability"] == VALIDATION_CAPABILITY, "ARK_SYSTEM_ARCHAEOLOGY_MAPPING_INVALID")
    req(mapping["tiers_are_ark_recovery_hosts_not_native_historical_execution"] is True, "ARK_SYSTEM_ARCHAEOLOGY_MAPPING_INVALID")
    req(mapping["native_execution_claimed"] is False, "ARK_SYSTEM_NATIVE_EXECUTION_FALSE_CLAIM")
    validate_recovery_tier_binding()

    if scope == "software_environment":
        notes = exact_keys(p["scope_notes"], SCOPE_NOTES_KEYS, "ARK_SOFTWARE_ENVIRONMENT_CANONICAL_MACHINE_FORBIDDEN")
        req(notes["hardware_variability"] is True and notes["canonical_machine"] is None, "ARK_SOFTWARE_ENVIRONMENT_CANONICAL_MACHINE_FORBIDDEN")
        req(nonempty_string(notes["reason"]), "ARK_SOFTWARE_ENVIRONMENT_CANONICAL_MACHINE_FORBIDDEN")

    sources = p["source_evidence"]
    req(isinstance(sources, list) and sources, "ARK_SYSTEM_SOURCE_INVALID")
    ids = []
    for source in sources:
        validate_source(source)
        ids.append(source["id"])
    req(len(ids) == len(set(ids)), "ARK_SYSTEM_SOURCE_INVALID")

    facts = {
        "system.commodore.c64": ("MOS 6510", "little", "64 KiB"),
        "system.commodore.amiga500": ("Motorola MC68000", "big", "Agnus"),
        "system.ibm.pc_xt_5160": ("Intel 8088", "little", "1 MiB"),
        "environment.digital_research.cpm_2_2": ("Intel 8080-compatible", "little", "0100h"),
        "environment.unix.v7_pdp11": ("PDP-11", "little", "a.out"),
    }[p["id"]]
    blob = json.dumps(p["technical_context"], sort_keys=True)
    req(all(item in blob for item in facts), "ARK_SYSTEM_PROFILE_FACT_INVALID")


def validate_task(t: dict, known: set[str]) -> None:
    exact_keys(t, TASK_KEYS, "ARK_SYSTEM_TASK_INVALID")
    req(
        t.get("type") == "qsol-ark-historical-system-recovery-task"
        and t.get("protocol") == "QSOL-ARK"
        and t.get("schema_version") == "0.4.0"
        and t.get("id") == "task.systems.minimum_reconstruction_probe",
        "ARK_SYSTEM_TASK_INVALID",
    )
    req(nonempty_string(t.get("purpose")), "ARK_SYSTEM_TASK_INVALID")
    systems = t.get("systems")
    req(isinstance(systems, list) and set(systems) == known and len(systems) == len(known), "ARK_SYSTEM_TASK_INVALID")

    cases = t.get("cases")
    req(isinstance(cases, list) and len(cases) == len(known), "ARK_SYSTEM_TASK_INVALID")
    ids = []
    for case in cases:
        c = exact_keys(case, CASE_KEYS, "ARK_SYSTEM_TASK_INVALID")
        req(c["system_id"] in known, "ARK_SYSTEM_TASK_INVALID")
        req(nonempty_string(c["prompt"]), "ARK_SYSTEM_TASK_INVALID")
        req(c["expected_equivalence"] == "historically_plausible_approximation", "ARK_SYSTEM_TASK_INVALID")
        ids.append(c["system_id"])
    req(set(ids) == known and len(ids) == len(set(ids)), "ARK_SYSTEM_TASK_INVALID")

    boundaries = exact_keys(t.get("global_boundaries"), BOUNDARY_KEYS, "ARK_SYSTEM_TASK_INVALID")
    req(
        boundaries
        == {
            "third_party_system_bytes_required": False,
            "emulator_output_is_original_history": False,
            "exact_reproduction_claimed": False,
            "ark_recovery_tier_is_native_historical_execution": False,
            "software_environment_must_preserve_hardware_variability": True,
        },
        "ARK_SYSTEM_TASK_INVALID",
    )


def validate() -> None:
    validate_policy(load("ai/historical-system-policy.json"))
    validate_recovery_tier_binding()

    idx = load("systems/index.json")
    exact_keys(idx, {"type", "protocol", "schema_version", "policy", "profiles", "tasks"}, "ARK_SYSTEM_INDEX_INVALID")
    req(
        idx.get("type") == "qsol-ark-historical-system-index"
        and idx.get("protocol") == "QSOL-ARK"
        and idx.get("schema_version") == "0.4.0"
        and idx.get("policy") == "ai/historical-system-policy.json",
        "ARK_SYSTEM_INDEX_INVALID",
    )

    entries = idx.get("profiles")
    req(isinstance(entries, list) and len(entries) == 5, "ARK_SYSTEM_INDEX_INVALID")
    ids = []
    for entry in entries:
        exact_keys(entry, {"id", "path", "scope"}, "ARK_SYSTEM_INDEX_INVALID")
        req(entry["id"] in PROFILE_IDS and entry["scope"] in SCOPES, "ARK_SYSTEM_INDEX_INVALID")
        profile = load(safe_path(entry["path"]))
        req(profile.get("id") == entry["id"] and profile.get("scope") == entry["scope"], "ARK_SYSTEM_INDEX_BINDING_INVALID")
        validate_profile(profile)
        ids.append(entry["id"])
    req(set(ids) == PROFILE_IDS and len(ids) == len(set(ids)), "ARK_SYSTEM_INDEX_INVALID")

    tasks = idx.get("tasks")
    req(isinstance(tasks, list) and len(tasks) == 1, "ARK_SYSTEM_INDEX_INVALID")
    task_entry = exact_keys(tasks[0], {"id", "path"}, "ARK_SYSTEM_INDEX_INVALID")
    task = load(safe_path(task_entry["path"]))
    req(task.get("id") == task_entry["id"], "ARK_SYSTEM_INDEX_BINDING_INVALID")
    validate_task(task, set(ids))

    print("ARK_SYSTEMS_OK profiles=5 tasks=1 exact_reproduction=0")


def main() -> int:
    try:
        validate()
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
