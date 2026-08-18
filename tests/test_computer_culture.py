# SPDX-License-Identifier: Apache-2.0
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
        self.myths = cc.load(cc.MYTHS_PATH)

    def test_full_validator(self):
        cc.validate()

    def test_seven_domains_are_covered(self):
        ids = cc.validate_specimens(self.pack, self.profile)
        self.assertEqual(len(ids), 7)
        self.assertEqual({r["domain"] for r in self.pack["records"]}, cc.EXPECTED_DOMAINS)

    def test_evidence_classes_stay_distinct(self):
        classes = set(self.profile["evidence_classes"])
        self.assertEqual(classes, {"executable_artifact", "cultural_artifact", "historical_claim"})
        self.assertIn("EXECUTABLE_ARTIFACT != CULTURAL_ARTIFACT", self.profile["canonical_invariants"])
        self.assertIn("CULTURAL_ARTIFACT != HISTORICAL_CLAIM", self.profile["canonical_invariants"])

    def test_bbs_record_is_non_operational(self):
        record = next(r for r in self.pack["records"] if r["domain"] == "bbs_hacker_handle_and_phreaking_history")
        self.assertEqual(record["safety"], {
            "operational_intrusion_instructions": False,
            "live_targets": False,
            "credentials": False,
            "exploit_steps": False,
        })

    def test_synthetic_text_never_becomes_primary_source(self):
        cc.validate_text_specimens(self.text, {r["id"] for r in self.pack["records"]})
        self.assertFalse(self.text["historical_primary_source"])
        self.assertTrue(all(s["label"].startswith("SYNTHETIC RECONSTRUCTION") for s in self.text["specimens"]))

    def test_strong_first_ever_claim_fails_closed(self):
        evidence = {
            "class": "historical_claim",
            "status": "documented_reference",
            "claim_category": "first_ever",
            "source_ids": ["src.sceneorg"],
            "supports": ["unsupported priority claim"],
        }
        with self.assertRaisesRegex(ValueError, "ARK_CC_STRONG_CLAIM_PROVENANCE_INSUFFICIENT"):
            cc.validate_evidence(evidence, self.pack["source_catalog"], self.profile)

    def test_strong_claim_must_be_historical_claim_class(self):
        evidence = {
            "class": "cultural_artifact",
            "status": "primary_source",
            "claim_category": "quotation",
            "source_ids": ["src.rfc1459"],
            "supports": ["quoted words"],
        }
        with self.assertRaisesRegex(ValueError, "ARK_CC_STRONG_CLAIM_WRONG_EVIDENCE_CLASS"):
            cc.validate_evidence(evidence, self.pack["source_catalog"], self.profile)

    def test_myth_taxonomy_is_complete(self):
        cc.validate_myths(self.myths)
        self.assertEqual({x["id"] for x in self.myths["classes"]}, cc.MYTH_CLASSES)

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

    def test_uncertainty_scores_above_confident_invention(self):
        explicit_uncertainty = {
            "era_identification": 1.0,
            "platform_identification": 1.0,
            "slang_reconstruction": 1.0,
            "social_role_reconstruction": 1.0,
            "technical_context_reconstruction": 1.0,
            "anachronism_rate": 0.0,
            "myth_to_fact_promotion_rate": 0.0,
        }
        confident_invention = dict(explicit_uncertainty)
        confident_invention["myth_to_fact_promotion_rate"] = 1.0
        self.assertGreater(
            cc.calculate_score(explicit_uncertainty, self.score),
            cc.calculate_score(confident_invention, self.score),
        )


if __name__ == "__main__":
    unittest.main()
