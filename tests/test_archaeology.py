# SPDX-License-Identifier: Apache-2.0
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

    def test_unimplemented_model_tier_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "ARK_MRS_UNAVAILABLE"):
            archaeology.select_mrs(["model_reconstruction"])


if __name__ == "__main__":
    unittest.main()
