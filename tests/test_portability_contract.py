# SPDX-License-Identifier: Apache-2.0
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "portability_contract", ROOT / "tools" / "portability_contract.py"
)
pc = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(pc)


class PortabilityContractTests(unittest.TestCase):
    def setUp(self):
        self.portability = pc.load(pc.PORTABILITY_PATH)
        self.media = pc.load(pc.MEDIA_PATH)
        self.emulator = pc.load(pc.EMULATOR_PATH)

    def test_full_contracts(self):
        pc.validate()

    def test_limited_compiler_and_alternate_libc_are_declared(self):
        classes = {target["class"] for target in self.portability["compiler_targets"]}
        libcs = {target["libc"] for target in self.portability["compiler_targets"]}
        self.assertIn("small-limited-compiler", classes)
        self.assertIn("alternate-libc", classes)
        self.assertIn("musl", libcs)
        self.assertIn("glibc", libcs)

    def test_reduced_word_size_target_is_i386_static(self):
        target = next(
            target for target in self.portability["compiler_targets"]
            if target["id"] == "gcc-i386-static"
        )
        self.assertEqual(target["architecture"], "i386-static")
        self.assertEqual(target["compiler"], target["compile_argv"][0])
        self.assertIn("-m32", target["compile_argv"])
        self.assertIn("-static", target["compile_argv"])

    def test_emulator_is_not_promoted_to_historical_hardware(self):
        self.assertEqual(
            self.portability["emulator_target"]["historical_recovery_equivalence"],
            "functional_equivalence_only",
        )
        self.assertIn(
            "EMULATED_I386 != HISTORICAL_PC",
            self.emulator["boundaries"],
        )

    def test_emulator_requires_clean_bounded_execution(self):
        runtime = self.emulator["runtime_constraints"]
        self.assertTrue(runtime["clean_environment"])
        self.assertFalse(runtime["network_required"])
        self.assertGreater(runtime["file_size_limit_blocks"], 0)
        self.assertLessEqual(runtime["wall_clock_timeout_seconds"], 30)

    def test_media_carriers_can_never_be_canonical(self):
        altered = copy.deepcopy(self.media)
        altered["carriers"]["qr"]["canonical_carrier_bytes"] = True
        with self.assertRaisesRegex(ValueError, "ARK_MEDIA_CARRIER_PROMOTED_TO_CANONICAL"):
            pc.validate_media(altered)

    def test_portability_claim_cannot_promote_emulator_equivalence(self):
        altered = copy.deepcopy(self.portability)
        altered["emulator_target"]["historical_recovery_equivalence"] = "exact_reproduction"
        with self.assertRaisesRegex(ValueError, "ARK_EMULATOR_EQUIVALENCE_PROMOTED"):
            pc.validate_portability(altered)

    def test_generated_vector_bytes_are_bound_to_digest(self):
        altered = copy.deepcopy(self.portability)
        vector = next(v for v in altered["required_vectors"] if "generated_bytes_utf8" in v)
        vector["generated_bytes_utf8"] = "abd"
        with self.assertRaisesRegex(ValueError, "ARK_PORTABILITY_VECTOR_DECLARATION_MISMATCH"):
            pc.validate_portability(altered)

    def test_canary_vector_is_bound_to_canonical_payload_and_receipt(self):
        altered = copy.deepcopy(self.portability)
        altered["canonical_payload"] = "recovery/printable/ARK-CANARY-CARD.txt"
        with self.assertRaisesRegex(ValueError, "ARK_PORTABILITY_CANARY_VECTOR_BINDING_INVALID"):
            pc.validate_portability(altered)

    def test_compiler_label_cannot_drift_from_executable(self):
        altered = copy.deepcopy(self.portability)
        target = next(t for t in altered["compiler_targets"] if t["id"] == "host-clang-glibc")
        target["compile_argv"][0] = "gcc"
        with self.assertRaisesRegex(ValueError, "ARK_PORTABILITY_COMPILER_COMMAND_DRIFT"):
            pc.validate_portability(altered)

    def test_libc_class_cannot_drift_from_compiler_binding(self):
        altered = copy.deepcopy(self.portability)
        target = next(t for t in altered["compiler_targets"] if t["id"] == "musl-gcc-static")
        target["compiler"] = "gcc"
        target["compile_argv"][0] = "gcc"
        with self.assertRaisesRegex(ValueError, "ARK_PORTABILITY_MUSL_BINDING_INVALID"):
            pc.validate_portability(altered)

    def test_media_contract_paths_must_match_execution_tool(self):
        altered = copy.deepcopy(self.media)
        altered["canonical_payload"] = "recovery/printable/ARK-CANARY-CARD.txt"
        with self.assertRaisesRegex(ValueError, "ARK_MEDIA_TOOL_PAYLOAD_PATH_DRIFT"):
            pc.validate_media(altered)


if __name__ == "__main__":
    unittest.main()
