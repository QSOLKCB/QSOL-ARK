# SPDX-License-Identifier: Apache-2.0
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import computer_culture as cc  # noqa: E402


class ComputerCultureTests(unittest.TestCase):
    def setUp(self):
        self.profile = cc.load(cc.PROFILE_PATH)
        self.pack = cc.load(cc.SPECIMENS_PATH)
        self.score = cc.load(cc.SCORE_PATH)
        self.text = cc.load(cc.TEXT_PATH)
        self.tasks = cc.load(cc.TASKS_PATH)
        self.myths = cc.load(cc.MYTHS_PATH)

    def test_full_validator(self):
        cc.validate()

    def test_coverage_comes_from_profile_registry(self):
        ids = cc.validate_specimens(self.pack, self.profile)
        self.assertEqual({r["domain"] for r in self.pack["records"]}, set(self.profile["registries"]["domains"]))
        self.assertEqual(len(ids), len(self.pack["records"]))
        self.assertNotEqual(len(ids), 0)

    def test_evidence_classes_stay_distinct(self):
        self.assertEqual(set(self.profile["evidence_classes"]), {"executable_artifact", "cultural_artifact", "historical_claim"})
        self.assertIn("EXECUTABLE_ARTIFACT != CULTURAL_ARTIFACT", self.profile["canonical_invariants"])
        self.assertIn("CULTURAL_ARTIFACT != HISTORICAL_CLAIM", self.profile["canonical_invariants"])

    def test_source_evidence_state_is_complete(self):
        cc.validate_sources(self.pack["source_catalog"], self.profile)
        required = set(self.profile["source_evidence"]["required_fields"])
        self.assertTrue(all(set(source) == required for source in self.pack["source_catalog"].values()))
        self.assertTrue(all(source["byte_import_allowed"] is False for source in self.pack["source_catalog"].values()))

    def test_retrieval_date_is_validated_by_shape_not_frozen_constant(self):
        pack = copy.deepcopy(self.pack)
        pack["source_catalog"]["src.sceneorg"]["retrieval_status"] = "retrieved_2026-08-17"
        cc.validate_sources(pack["source_catalog"], self.profile)

    def test_strong_first_ever_claim_cannot_self_promote_by_status(self):
        evidence = {
            "class": "historical_claim",
            "status": "primary_source",
            "claim_category": "first_ever",
            "source_ids": ["src.sceneorg"],
            "supports": ["demos_and_scene_material"],
        }
        with self.assertRaisesRegex(ValueError, "ARK_CC_STRONG_CLAIM_PROVENANCE_INSUFFICIENT"):
            cc.validate_evidence(evidence, self.pack["source_catalog"], self.profile)

    def test_first_ever_can_pass_with_two_independent_high_quality_sources(self):
        sources = copy.deepcopy(self.pack["source_catalog"])
        sources["src.sceneorg2"] = copy.deepcopy(sources["src.sceneorg"])
        sources["src.sceneorg2"]["url"] = "https://example.invalid/independent"
        sources["src.sceneorg2"]["independence_group"] = "independent_archive"
        evidence = {
            "class": "historical_claim",
            "status": "corroborated_high_quality_sources",
            "claim_category": "first_ever",
            "source_ids": ["src.sceneorg", "src.sceneorg2"],
            "supports": ["demos_and_scene_material"],
        }
        cc.validate_evidence(evidence, sources, self.profile)

    def test_strong_claim_must_be_historical_claim_class(self):
        evidence = {
            "class": "cultural_artifact",
            "status": "primary_source",
            "claim_category": "quotation",
            "source_ids": ["src.rfc1459"],
            "supports": ["irc_protocol"],
        }
        with self.assertRaisesRegex(ValueError, "ARK_CC_STRONG_CLAIM_WRONG_EVIDENCE_CLASS"):
            cc.validate_evidence(evidence, self.pack["source_catalog"], self.profile)

    def test_record_rejects_undeclared_top_level_payload(self):
        record = copy.deepcopy(self.pack["records"][0])
        record["transcript_payload"] = "third party bytes"
        with self.assertRaisesRegex(ValueError, "ARK_CC_RECORD_FIELDS_UNDECLARED"):
            cc.validate_record(record, self.pack["source_catalog"], self.profile)

    def test_bbs_record_enforces_all_safety_flags(self):
        record = next(r for r in self.pack["records"] if r["domain"] == "bbs_hacker_handle_and_phreaking_history")
        required = set(self.profile["safety_boundaries"]["historical_hacker_and_phreaking_records"]["required_false_flags"])
        self.assertTrue(all(record["safety"][flag] is False for flag in required))
        cc.validate_bbs_safety(record, self.profile)

    def test_bbs_operational_marker_is_rejected(self):
        record = copy.deepcopy(next(r for r in self.pack["records"] if r["domain"] == "bbs_hacker_handle_and_phreaking_history"))
        record["contextual_meaning"] += " Includes step-by-step exploit material."
        with self.assertRaisesRegex(ValueError, "ARK_CC_BBS_OPERATIONAL_GUIDANCE_FORBIDDEN"):
            cc.validate_bbs_safety(record, self.profile)

    def test_synthetic_text_uses_real_line_breaks(self):
        cc.validate_text_specimens(self.text, {r["id"] for r in self.pack["records"]}, self.profile)
        self.assertTrue(all("\n" in s["text"] for s in self.text["specimens"]))
        self.assertTrue(all("\\n" not in s["text"] for s in self.text["specimens"]))

    def test_myth_taxonomy_semantics_are_bound(self):
        cc.validate_myths(self.myths)
        mutated = copy.deepcopy(self.myths)
        next(item for item in mutated["classes"] if item["id"] == "folklore")["promotion_to_fact"] = "automatic"
        with self.assertRaisesRegex(ValueError, "ARK_CC_MYTH_PROMOTION_POLICY_INVALID"):
            cc.validate_myths(mutated)

    def test_index_references_single_canonical_invariant_list(self):
        index = cc.load(cc.INDEX_PATH)
        self.assertEqual(index["canonical_invariants_ref"], "ai/computer-cultural-artifact-profile.json#canonical_invariants")
        self.assertNotIn("invariants", index)

    def test_recovery_tasks_cover_every_record(self):
        known = {r["id"] for r in self.pack["records"]}
        cc.validate_tasks(self.tasks, known, self.score)
        self.assertEqual({task["record_id"] for task in self.tasks["tasks"]}, known)

    def test_manifest_and_bootstrap_discover_broader_culture(self):
        cc.validate_discovery(cc.load(cc.MANIFEST_PATH), cc.load(cc.BOOTSTRAP_PATH))

    def test_score_rejects_booleans(self):
        values = {
            "era_identification": True,
            "platform_identification": 1.0,
            "slang_reconstruction": 1.0,
            "social_role_reconstruction": 1.0,
            "technical_context_reconstruction": 1.0,
            "anachronism_rate": 0.0,
            "myth_to_fact_promotion_rate": 0.0,
        }
        with self.assertRaisesRegex(ValueError, "ARK_CC_SCORE_INPUT_INVALID"):
            cc.calculate_score(values, self.score)

    def test_score_formula_is_bound_to_dimension_weights(self):
        cc.validate_score(self.score)
        mutated = copy.deepcopy(self.score)
        mutated["formula"]["positive_weight_total"] = 0.71
        with self.assertRaisesRegex(ValueError, "ARK_CC_SCORE_FORMULA_INVALID"):
            cc.validate_score(mutated)

    def test_score_perfect_and_zero(self):
        perfect = {
            "era_identification": 1.0,
            "platform_identification": 1.0,
            "slang_reconstruction": 1.0,
            "social_role_reconstruction": 1.0,
            "technical_context_reconstruction": 1.0,
            "anachronism_rate": 0.0,
            "myth_to_fact_promotion_rate": 0.0,
        }
        worst = {
            "era_identification": 0.0,
            "platform_identification": 0.0,
            "slang_reconstruction": 0.0,
            "social_role_reconstruction": 0.0,
            "technical_context_reconstruction": 0.0,
            "anachronism_rate": 1.0,
            "myth_to_fact_promotion_rate": 1.0,
        }
        self.assertEqual(cc.calculate_score(perfect, self.score), 100.0)
        self.assertEqual(cc.calculate_score(worst, self.score), 0.0)

    def test_confident_invention_gets_no_positive_credit(self):
        values = {
            "era_identification": 1.0,
            "platform_identification": 1.0,
            "slang_reconstruction": 1.0,
            "social_role_reconstruction": 1.0,
            "technical_context_reconstruction": 1.0,
            "anachronism_rate": 0.0,
            "myth_to_fact_promotion_rate": 0.0,
        }
        explicit = cc.calculate_score(values, self.score, "explicit_uncertainty")
        invention = cc.calculate_score(values, self.score, "confident_unsupported_historical_invention")
        self.assertEqual(invention, 15.0)
        self.assertGreater(explicit, invention)


if __name__ == "__main__":
    unittest.main()
