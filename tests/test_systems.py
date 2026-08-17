# SPDX-License-Identifier: Apache-2.0
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("systems", ROOT / "tools" / "systems.py")
m = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(m)


class HistoricalSystemTests(unittest.TestCase):
    def test_full(self):
        m.validate()

    def test_t4_declares_historical_validation(self):
        tier = m.validate_recovery_tier_binding()
        self.assertEqual(tier["id"], "T4")
        self.assertIn("tools/systems.py", tier["entrypoints"])
        self.assertIn("validate_historical_system_contracts", tier["capabilities"])

    def test_undeclared_top_level_payload_rejected(self):
        p = m.load("systems/profiles/amiga500.json")
        p["kickstart_bytes"] = "AAECAwQ="
        with self.assertRaisesRegex(ValueError, "ARK_SYSTEM_PROFILE_SHAPE_INVALID"):
            m.validate_profile(p)

    def test_undeclared_nested_payload_rejected(self):
        p = m.load("systems/profiles/amiga500.json")
        p["technical_context"]["totally_not_rom"] = {"payload": "AAECAwQ="}
        with self.assertRaisesRegex(ValueError, "ARK_SYSTEM_PROFILE_SHAPE_INVALID"):
            m.validate_profile(p)

    def test_emulator_not_history(self):
        p = m.load("systems/profiles/amiga500.json")
        p["emulator_or_reimplementation"]["used_for_canonical_profile"] = True
        with self.assertRaisesRegex(ValueError, "ARK_EMULATOR_PROMOTED_TO_HISTORY"):
            m.validate_profile(p)

    def test_exact_not_claimed(self):
        p = m.load("systems/profiles/pc_xt.json")
        p["recovery_equivalence"]["exact_reproduction_claimed"] = True
        with self.assertRaisesRegex(ValueError, "ARK_SYSTEM_EXACT_REPRODUCTION_UNSUPPORTED"):
            m.validate_profile(p)

    def test_cpm_not_one_machine(self):
        p = m.load("systems/profiles/cpm.json")
        p["scope_notes"]["hardware_variability"] = False
        with self.assertRaisesRegex(ValueError, "ARK_SOFTWARE_ENVIRONMENT_CANONICAL_MACHINE_FORBIDDEN"):
            m.validate_profile(p)

    def test_unix_not_one_machine(self):
        p = m.load("systems/profiles/unix.json")
        p["scope_notes"]["canonical_machine"] = "PDP-11/70"
        with self.assertRaisesRegex(ValueError, "ARK_SOFTWARE_ENVIRONMENT_CANONICAL_MACHINE_FORBIDDEN"):
            m.validate_profile(p)

    def test_tier_not_native(self):
        p = m.load("systems/profiles/c64.json")
        p["computational_archaeology_mapping"]["native_execution_claimed"] = True
        with self.assertRaisesRegex(ValueError, "ARK_SYSTEM_NATIVE_EXECUTION_FALSE_CLAIM"):
            m.validate_profile(p)

    def test_mapping_requires_declared_capability(self):
        p = m.load("systems/profiles/c64.json")
        p["computational_archaeology_mapping"]["profile_validation_capability"] = "python_exists_so_surely_it_works"
        with self.assertRaisesRegex(ValueError, "ARK_SYSTEM_ARCHAEOLOGY_MAPPING_INVALID"):
            m.validate_profile(p)

    def test_evidence_partition_exact(self):
        p = m.load("systems/profiles/c64.json")
        p["claim_partitions"]["historical_vibes"] = []
        with self.assertRaisesRegex(ValueError, "ARK_SYSTEM_EVIDENCE_PARTITION_INVALID"):
            m.validate_profile(p)

    def test_source_url_required(self):
        p = m.load("systems/profiles/c64.json")
        p["source_evidence"][0]["url"] = "nope"
        with self.assertRaisesRegex(ValueError, "ARK_SYSTEM_SOURCE_INVALID"):
            m.validate_profile(p)

    def test_source_provenance_fields_required(self):
        p = m.load("systems/profiles/c64.json")
        del p["source_evidence"][0]["license"]
        with self.assertRaisesRegex(ValueError, "ARK_SYSTEM_SOURCE_INVALID"):
            m.validate_profile(p)

    def test_unresolved_source_cannot_import_bytes(self):
        p = m.load("systems/profiles/c64.json")
        p["source_evidence"][0]["byte_import_allowed"] = True
        with self.assertRaisesRegex(ValueError, "ARK_SYSTEM_FORBIDDEN_BYTES"):
            m.validate_profile(p)

    def test_task_boundaries(self):
        t = m.load("systems/tasks/minimum-reconstruction-probe.json")
        t["global_boundaries"]["exact_reproduction_claimed"] = True
        with self.assertRaisesRegex(ValueError, "ARK_SYSTEM_TASK_INVALID"):
            m.validate_task(t, set(m.PROFILE_IDS))

    def test_task_prompt_must_be_nonempty_string(self):
        t = m.load("systems/tasks/minimum-reconstruction-probe.json")
        t["cases"][0]["prompt"] = {"text": "not executable prompt text"}
        with self.assertRaisesRegex(ValueError, "ARK_SYSTEM_TASK_INVALID"):
            m.validate_task(t, set(m.PROFILE_IDS))

    def test_task_case_shape_is_closed(self):
        t = m.load("systems/tasks/minimum-reconstruction-probe.json")
        t["cases"][0]["hidden_payload"] = "surprise"
        with self.assertRaisesRegex(ValueError, "ARK_SYSTEM_TASK_INVALID"):
            m.validate_task(t, set(m.PROFILE_IDS))

    def test_manifest_schema_requires_historical_entrypoints(self):
        schema = json.loads((ROOT / "schema" / "ark-manifest.schema.json").read_text(encoding="utf-8"))
        required = set(schema["properties"]["entrypoints"]["required"])
        self.assertTrue({
            "historical_system_policy",
            "historical_system_index",
            "ancient_systems",
            "historical_system_validator",
        }.issubset(required))

    def test_ai_entrypoint_loads_historical_layer(self):
        text = (ROOT / "README4AI.md").read_text(encoding="utf-8")
        self.assertIn("ai/historical-system-policy.json", text)
        self.assertIn("systems/index.json", text)
        self.assertIn("validate_historical_system_contracts", text)


if __name__ == "__main__":
    unittest.main()
