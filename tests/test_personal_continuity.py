import unittest

from tools.personal_continuity import score_report, validate_contract


class PersonalContinuityTests(unittest.TestCase):
    def valid_report(self):
        return {
            "protocol": "QSOL-ARK/PERSONAL-CONTINUITY-REPORT/1",
            "trial_id": "P3",
            "scores": {
                "identity": 0.95,
                "working_style": 0.95,
                "project_state": 0.9,
                "research_context": 0.9,
                "epistemic_discipline": 1.0,
                "style_continuity": 0.85,
            },
            "boundaries_passed": True,
        }

    def test_contract_validates_and_t5_remains_unimplemented(self):
        result = validate_contract()
        self.assertEqual(result["status"], "valid")
        self.assertFalse(result["t5_implemented"])
        self.assertFalse(result["destructive_live_account_test"])

    def test_high_quality_clean_room_report_passes(self):
        result = score_report(self.valid_report())
        self.assertTrue(result["passed"])
        self.assertGreaterEqual(result["score"], 80)

    def test_model_identity_boundary_failure_forces_failure(self):
        report = self.valid_report()
        report["boundaries_passed"] = False
        result = score_report(report)
        self.assertFalse(result["passed"])

    def test_mandatory_dimension_below_threshold_forces_failure(self):
        report = self.valid_report()
        report["scores"]["identity"] = 0.79
        result = score_report(report)
        self.assertFalse(result["mandatory_dimensions_passed"])
        self.assertFalse(result["passed"])

    def test_missing_scoring_dimension_fails_with_explicit_error(self):
        report = self.valid_report()
        del report["scores"]["research_context"]
        with self.assertRaisesRegex(
            ValueError,
            "missing score for dimension research_context",
        ):
            score_report(report)

    def test_score_outside_unit_interval_fails_closed(self):
        report = self.valid_report()
        report["scores"]["style_continuity"] = 1.01
        with self.assertRaisesRegex(ValueError, "numeric in 0..1"):
            score_report(report)

    def test_boolean_score_is_rejected(self):
        report = self.valid_report()
        report["scores"]["identity"] = True
        with self.assertRaisesRegex(ValueError, "numeric in 0..1"):
            score_report(report)

    def test_unknown_trial_fails_closed(self):
        report = self.valid_report()
        report["trial_id"] = "P9000"
        with self.assertRaisesRegex(ValueError, "unknown personal continuity trial_id"):
            score_report(report)


if __name__ == "__main__":
    unittest.main()
