import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "system_architecture_validator",
    ROOT / "tools" / "system_architecture.py",
)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validator)


class SystemArchitectureTests(unittest.TestCase):
    def test_canonical_architecture_validates(self):
        report = validator.validate()
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["roles"], 9)
        self.assertEqual(report["deterministic_search_status"], "planned-not-yet-implemented")
        self.assertFalse(report["t5_ai_reconstruction_implemented"])

    def test_ascii_file_is_strict_7_bit(self):
        raw = (ROOT / "ARCHITECTURE.txt").read_bytes()
        raw.decode("ascii")
        self.assertNotIn(b"\r", raw)
        self.assertNotIn(b"\t", raw)
        self.assertTrue(raw.endswith(b"\n"))

    def test_machine_contract_names_ark_as_cross_repo_role_authority(self):
        machine = json.loads(
            (ROOT / "ai" / "system-architecture.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            machine["authority"]["cross_repository_roles"],
            "QSOLKCB/QSOL-ARK/ARCHITECTURE.txt",
        )
        self.assertEqual(
            machine["authority"]["local_implementation_status"],
            "live state of each local repository",
        )

    def test_lattice_fingerprint_is_pinned(self):
        machine = json.loads(
            (ROOT / "ai" / "system-architecture.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            machine["lattice"]["profile_fingerprint"],
            "sha256:6e7c4a9a781d552a2b561d334a8435c12efe2908fcd24a0f152935aded555bcf",
        )

    def test_atari_search_is_not_claimed_implemented(self):
        machine = json.loads(
            (ROOT / "ai" / "system-architecture.json").read_text(encoding="utf-8")
        )
        self.assertEqual(machine["deterministic_search"]["status"], "planned-not-yet-implemented")
        ascii_text = (ROOT / "ARCHITECTURE.txt").read_text(encoding="ascii")
        self.assertIn(
            "PLANNED / NOT YET IMPLEMENTED AS A CANONICAL QSOL-CONTROL PRIMITIVE",
            ascii_text,
        )


if __name__ == "__main__":
    unittest.main()
