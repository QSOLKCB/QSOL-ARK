# SPDX-License-Identifier: Apache-2.0
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("archaeology", ROOT / "tools" / "archaeology.py")
archaeology = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(archaeology)


class ArchaeologyTests(unittest.TestCase):
    def test_contracts(self):
        archaeology.validate()

    def test_mrs_hash_is_t1(self):
        self.assertEqual(archaeology.select_mrs(["verify_sha256"])["id"], "T1")

    def test_mrs_standalone_hash_is_t2(self):
        self.assertEqual(archaeology.select_mrs(["standalone_hash_implementation"])["id"], "T2")

    def test_mrs_browser_is_t3(self):
        self.assertEqual(archaeology.select_mrs(["interactive_offline"])["id"], "T3")

    def test_mrs_archaeology_validation_is_t4(self):
        self.assertEqual(archaeology.select_mrs(["validate_archaeology_contracts"])["id"], "T4")

    def test_mrs_portability_validation_is_t4(self):
        self.assertEqual(archaeology.select_mrs(["validate_portability_contracts"])["id"], "T4")

    def test_mrs_recovery_media_is_t4(self):
        self.assertEqual(
            archaeology.select_mrs(["build_recovery_media", "verify_recovery_carrier"])["id"],
            "T4",
        )

    def test_mrs_audio_decode_is_t4(self):
        self.assertEqual(archaeology.select_mrs(["decode_audio_recovery_carrier"])["id"], "T4")

    def test_unimplemented_model_tier_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "ARK_MRS_UNAVAILABLE"):
            archaeology.select_mrs(["model_reconstruction"])

    def test_manifest_registry_divergence_fails_closed(self):
        manifest = archaeology.load_json(archaeology.MANIFEST_PATH)
        tier_list = archaeology.load_json(archaeology.TIERS_PATH)["tiers"]
        altered = copy.deepcopy(manifest)
        altered["implemented_recovery_tiers"] = ["T0"]
        with self.assertRaisesRegex(ValueError, "ARK_IMPLEMENTED_TIER_MISMATCH"):
            archaeology.reconcile_implemented_tiers(altered, tier_list)

    def test_missing_provenance_field_fails_closed(self):
        policy = archaeology.load_json(archaeology.CONTEXT_POLICY_PATH)
        record = archaeology.load_json(archaeology.RETRO)
        altered = copy.deepcopy(record)
        del altered["visibility"]
        with self.assertRaisesRegex(ValueError, "ARK_PROVENANCE_FIELDS_MISSING"):
            archaeology.validate_import_record(policy, altered)

    def test_invalid_mrs_example_shape_fails_closed(self):
        mrs = archaeology.load_json(archaeology.MRS_PATH)
        altered = copy.deepcopy(mrs)
        altered["examples"] = [42]
        with self.assertRaisesRegex(ValueError, "ARK_MRS_EXAMPLE_NOT_OBJECT"):
            archaeology.validate_mrs_contract(altered)

    def test_browser_projection_matches_canary_and_receipt(self):
        archaeology.validate_browser_projection(
            archaeology.receipt_hash(archaeology.CANARY.name)
        )


if __name__ == "__main__":
    unittest.main()
