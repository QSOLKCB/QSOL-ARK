import copy
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


def machine_contract():
    return json.loads(
        (ROOT / "ai" / "system-architecture.json").read_text(encoding="utf-8")
    )


def ascii_bytes():
    return (ROOT / "ARCHITECTURE.txt").read_bytes()


class SystemArchitectureTests(unittest.TestCase):
    def test_canonical_architecture_validates(self):
        report = validator.validate()
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["roles"], 9)
        self.assertEqual(report["deterministic_search_status"], "planned-not-yet-implemented")
        self.assertFalse(report["t5_ai_reconstruction_implemented"])

    def test_ascii_file_is_strict_7_bit(self):
        raw = ascii_bytes()
        raw.decode("ascii")
        self.assertNotIn(b"\r", raw)
        self.assertNotIn(b"\t", raw)
        self.assertTrue(raw.endswith(b"\n"))

    def test_machine_contract_is_single_semantic_source(self):
        machine = machine_contract()
        self.assertEqual(machine["semantic_source"], "ai/system-architecture.json")
        self.assertEqual(
            machine["authority"]["cross_repository_semantics"],
            "ai/system-architecture.json",
        )
        self.assertEqual(
            machine["authority"]["local_implementation_status"],
            "live state of each local repository",
        )

    def test_ascii_receipt_rejects_contradictory_append(self):
        machine = machine_contract()
        corrupted = ascii_bytes() + b"DETERMINISTIC SEARCH IS IMPLEMENTED\n"
        with self.assertRaisesRegex(ValueError, "ASCII_SHA_MISMATCH"):
            validator.validate_machine(machine, corrupted)

    def test_semantic_receipt_rejects_role_authority_drift(self):
        machine = machine_contract()
        mutated = copy.deepcopy(machine)
        mutated["roles"][5]["authority_boundary"] = "owns universal truth"
        with self.assertRaisesRegex(ValueError, "SEMANTIC_SHA_MISMATCH"):
            validator.validate_machine(mutated, ascii_bytes())

    def test_lattice_fingerprint_is_computed_from_payload(self):
        machine = machine_contract()
        self.assertEqual(
            machine["lattice"]["profile_fingerprint"],
            "sha256:6e7c4a9a781d552a2b561d334a8435c12efe2908fcd24a0f152935aded555bcf",
        )
        mutated = copy.deepcopy(machine)
        mutated.pop("semantic_sha256")
        mutated["lattice"]["conformance_payload"]["phi_stride"] = 16
        mutated["semantic_sha256"] = validator.sha256_ref(
            validator.canonical_json_bytes(mutated)
        )
        with self.assertRaisesRegex(ValueError, "LATTICE_FINGERPRINT_MISMATCH"):
            validator.validate_machine(mutated, ascii_bytes())

    def test_complete_role_record_is_closed(self):
        machine = machine_contract()
        mutated = copy.deepcopy(machine)
        mutated["roles"][0]["unexpected"] = "drift"
        mutated.pop("semantic_sha256")
        mutated["semantic_sha256"] = validator.sha256_ref(
            validator.canonical_json_bytes(mutated)
        )
        with self.assertRaisesRegex(ValueError, "ROLE_0_FIELDS"):
            validator.validate_machine(mutated, ascii_bytes())

    def test_atari_search_is_not_claimed_implemented(self):
        machine = machine_contract()
        self.assertEqual(machine["deterministic_search"]["status"], "planned-not-yet-implemented")
        self.assertIn(
            "PLANNED / NOT YET IMPLEMENTED AS A CANONICAL QSOL-CONTROL PRIMITIVE",
            ascii_bytes().decode("ascii"),
        )


if __name__ == "__main__":
    unittest.main()
