#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fail-closed validator for QSOL-ARK PR #4 historical-system profiles."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_IDS = {
    "system.commodore.c64", "system.commodore.amiga500", "system.ibm.pc_xt_5160",
    "environment.digital_research.cpm_2_2", "environment.unix.v7_pdp11",
}
SCOPES = {"hardware_system", "software_environment"}
EVIDENCE = {
    "hardware_fact", "documented_software_behaviour", "emulator_behaviour",
    "compatibility_layer_behaviour", "reconstruction_inference", "unknown",
}
HRE = {
    "exact_reproduction", "functional_equivalence", "historically_plausible_approximation",
    "emulator_assisted_reproduction", "modern_compatibility_layer", "impossible_or_unsupported",
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
FORBIDDEN_KEYS = {
    "rom_bytes", "firmware_bytes", "disk_image_bytes", "software_bytes", "binary_payload",
    "base64_payload", "rom_image", "firmware_image", "proprietary_os_image",
    "copyrighted_disk_image", "binary_distribution",
}
RIGHTS = {
    "source_bytes_copied", "rom_bytes_copied", "firmware_bytes_copied",
    "proprietary_software_copied", "disk_image_bytes_copied", "binary_distribution_copied",
}

def load(path):
    p = Path(path)
    if not p.is_absolute(): p = ROOT / p
    return json.loads(p.read_text(encoding="utf-8"))

def req(ok, code):
    if not ok: raise ValueError(code)

def safe_path(value):
    req(isinstance(value, str) and value, "ARK_SYSTEM_PATH_INVALID")
    p = Path(value)
    req(not p.is_absolute() and ".." not in p.parts and p.parts[0] == "systems", "ARK_SYSTEM_PATH_INVALID")
    full = ROOT / p
    req(full.is_file(), "ARK_SYSTEM_PATH_MISSING")
    return full

def reject_payload(value):
    if isinstance(value, dict):
        for k, v in value.items():
            req(k not in FORBIDDEN_KEYS, "ARK_SYSTEM_FORBIDDEN_BYTES")
            reject_payload(v)
    elif isinstance(value, list):
        for v in value: reject_payload(v)

def validate_policy(p):
    req(p.get("type") == "qsol-ark-historical-system-policy" and p.get("protocol") == "QSOL-ARK"
        and p.get("schema_version") == "0.4.0", "ARK_SYSTEM_POLICY_INVALID")
    req(set(p.get("profile_scopes", [])) == SCOPES, "ARK_SYSTEM_POLICY_INVALID")
    req(set(p.get("evidence_classes", [])) == EVIDENCE, "ARK_SYSTEM_POLICY_INVALID")
    req(set(p.get("historical_recovery_equivalence", [])) == HRE, "ARK_SYSTEM_POLICY_INVALID")
    req(set(p.get("rules", [])) == RULES, "ARK_SYSTEM_POLICY_INVALID")
    req(p.get("seed_exact_reproduction_allowed") is False, "ARK_SYSTEM_EXACT_REPRODUCTION_UNSUPPORTED")

def validate_profile(p):
    req(p.get("type") == "qsol-ark-historical-system-profile" and p.get("protocol") == "QSOL-ARK"
        and p.get("schema_version") == "0.4.0", "ARK_SYSTEM_PROFILE_INVALID")
    req(p.get("id") in PROFILE_IDS and p.get("scope") in SCOPES, "ARK_SYSTEM_PROFILE_INVALID")
    req(isinstance(p.get("technical_context"), dict) and p["technical_context"], "ARK_SYSTEM_PROFILE_INVALID")
    req(isinstance(p.get("claim_partitions"), dict) and set(p["claim_partitions"]) == EVIDENCE
        and all(isinstance(v, list) for v in p["claim_partitions"].values()), "ARK_SYSTEM_EVIDENCE_PARTITION_INVALID")
    reject_payload(p)
    r = p.get("rights", {})
    req(set(r) == RIGHTS and all(r[k] is False for k in RIGHTS), "ARK_SYSTEM_FORBIDDEN_BYTES")
    e = p.get("emulator_or_reimplementation", {})
    req(e.get("used_for_canonical_profile") is False
        and all(e.get(k) is None for k in ("identity","version","source","license")), "ARK_EMULATOR_PROMOTED_TO_HISTORY")
    q = p.get("recovery_equivalence", {})
    req(q.get("current_class") == "historically_plausible_approximation", "ARK_SYSTEM_EQUIVALENCE_INVALID")
    req(q.get("exact_reproduction_claimed") is False, "ARK_SYSTEM_EXACT_REPRODUCTION_UNSUPPORTED")
    m = p.get("computational_archaeology_mapping", {})
    req(m.get("profile_validation_tier") == "T4"
        and m.get("tiers_are_ark_recovery_hosts_not_native_historical_execution") is True,
        "ARK_SYSTEM_ARCHAEOLOGY_MAPPING_INVALID")
    req(m.get("native_execution_claimed") is False, "ARK_SYSTEM_NATIVE_EXECUTION_FALSE_CLAIM")
    if p["scope"] == "software_environment":
        n = p.get("scope_notes", {})
        req(n.get("hardware_variability") is True and n.get("canonical_machine") is None,
            "ARK_SOFTWARE_ENVIRONMENT_CANONICAL_MACHINE_FORBIDDEN")
    src = p.get("source_evidence")
    req(isinstance(src, list) and src, "ARK_SYSTEM_SOURCE_INVALID")
    ids = []
    for s in src:
        ids.append(s.get("id"))
        req(isinstance(s.get("id"), str) and s["id"]
            and isinstance(s.get("url"), str) and s["url"].startswith("https://")
            and isinstance(s.get("supports"), list) and s["supports"], "ARK_SYSTEM_SOURCE_INVALID")
    req(len(ids) == len(set(ids)), "ARK_SYSTEM_SOURCE_INVALID")
    facts = {
        "system.commodore.c64": ("MOS 6510", "little", "64 KiB"),
        "system.commodore.amiga500": ("Motorola MC68000", "big", "Agnus"),
        "system.ibm.pc_xt_5160": ("Intel 8088", "little", "1 MiB"),
        "environment.digital_research.cpm_2_2": ("Intel 8080-compatible", "little", "0100h"),
        "environment.unix.v7_pdp11": ("PDP-11", "little", "a.out"),
    }[p["id"]]
    blob = json.dumps(p["technical_context"], sort_keys=True)
    req(facts[0] in blob and facts[1] in blob and facts[2] in blob, "ARK_SYSTEM_PROFILE_FACT_INVALID")

def validate_task(t, known):
    req(t.get("type") == "qsol-ark-historical-system-recovery-task" and t.get("protocol") == "QSOL-ARK"
        and t.get("schema_version") == "0.4.0" and t.get("id") == "task.systems.minimum_reconstruction_probe",
        "ARK_SYSTEM_TASK_INVALID")
    req(set(t.get("systems", [])) == known and len(t["systems"]) == len(known), "ARK_SYSTEM_TASK_INVALID")
    cases = t.get("cases", [])
    ids = [c.get("system_id") for c in cases if isinstance(c, dict)]
    req(set(ids) == known and len(ids) == len(set(ids)) == len(known), "ARK_SYSTEM_TASK_INVALID")
    req(all(c.get("expected_equivalence") == "historically_plausible_approximation" and c.get("prompt")
            for c in cases), "ARK_SYSTEM_TASK_INVALID")
    b = t.get("global_boundaries", {})
    req(b == {
        "third_party_system_bytes_required": False,
        "emulator_output_is_original_history": False,
        "exact_reproduction_claimed": False,
        "ark_recovery_tier_is_native_historical_execution": False,
        "software_environment_must_preserve_hardware_variability": True,
    }, "ARK_SYSTEM_TASK_INVALID")

def validate():
    validate_policy(load("ai/historical-system-policy.json"))
    idx = load("systems/index.json")
    req(idx.get("type") == "qsol-ark-historical-system-index" and idx.get("protocol") == "QSOL-ARK"
        and idx.get("schema_version") == "0.4.0" and idx.get("policy") == "ai/historical-system-policy.json",
        "ARK_SYSTEM_INDEX_INVALID")
    entries = idx.get("profiles", [])
    ids = [x.get("id") for x in entries if isinstance(x, dict)]
    req(len(entries) == 5 and set(ids) == PROFILE_IDS and len(ids) == len(set(ids)), "ARK_SYSTEM_INDEX_INVALID")
    for x in entries:
        p = load(safe_path(x.get("path")))
        req(p.get("id") == x.get("id") and p.get("scope") == x.get("scope"), "ARK_SYSTEM_INDEX_BINDING_INVALID")
        validate_profile(p)
    tasks = idx.get("tasks", [])
    req(len(tasks) == 1, "ARK_SYSTEM_INDEX_INVALID")
    t = load(safe_path(tasks[0].get("path")))
    req(t.get("id") == tasks[0].get("id"), "ARK_SYSTEM_INDEX_BINDING_INVALID")
    validate_task(t, set(ids))
    print("ARK_SYSTEMS_OK profiles=5 tasks=1 exact_reproduction=0")

def main():
    try: validate()
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
        print(str(e), file=sys.stderr); return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
