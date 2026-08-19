# SPDX-License-Identifier: Apache-2.0
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("australian_culture", ROOT / "tools" / "australian_culture.py")
ac = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(ac)


class AustralianCultureTests(unittest.TestCase):
    def setUp(self):
        self.policy = ac.load(ac.POLICY_PATH)
        self.sources_doc = ac.load(ac.SOURCES_PATH)
        self.sources = self.sources_doc["sources"]
        self.records_doc = ac.load(ac.RECORDS_PATH)
        self.tasks_doc = ac.load(ac.TASKS_PATH)

    def record(self, record_id):
        return next(record for record in self.records_doc["records"] if record["id"] == record_id)

    def test_full_validator(self):
        ac.validate()

    def test_planned_invariants_are_canonical(self):
        self.assertEqual(set(self.policy["canonical_invariants"]), ac.INVARIANTS)

    def test_preprint_remains_cc_by_preprint_not_peer_reviewed(self):
        source = self.sources["src.antipodean_jester"]
        self.assertEqual(source["license_status"], "CC-BY-4.0")
        self.assertEqual(source["publication_state"], "preprint")
        self.assertFalse(source["peer_reviewed"])
        self.assertEqual(source["doi"], "10.22541/au.176780580.02987307/v1")

    def test_informal_governance_is_not_formal_authority(self):
        record = self.record("culture.australia.australian_informal_governance")
        self.assertFalse(record["scope"]["formal_authority"])
        self.assertFalse(record["boundaries"]["humour_as_governance_is_formal_legal_authority"])
        self.assertIn("src.legislation.constitution", {sid for item in record["evidence"] for sid in item["source_ids"]})

    def test_fatalistic_humour_is_not_nihilism_or_emotion_proof(self):
        record = self.record("culture.australia.irreverent_fatalism")
        boundary = record["boundaries"]
        self.assertFalse(boundary["fatalistic_humour_is_nihilism"])
        self.assertFalse(boundary["humour_proves_absence_of_grief"])
        self.assertFalse(boundary["humour_proves_absence_of_fear"])
        self.assertFalse(boundary["humour_proves_disregard_for_life"])
        self.assertTrue(boundary["retained_agency_is_derived_interpretation"])

    def test_breaker_morant_quote_is_film_dialogue_only(self):
        record = self.record("culture.australia.breaker_morant_history_and_film")
        quote = record["quotation"]
        self.assertEqual(quote["text"], "Shoot straight, you bastards!")
        self.assertEqual(quote["context"], "film_dialogue")
        self.assertEqual(quote["source_id"], "src.aso.breaker_morant_clip3")
        self.assertFalse(quote["historical_primary_testimony"])
        self.assertFalse(quote["full_script_copied"])
        self.assertFalse(quote["audiovisual_bytes_copied"])

    def test_breaker_morant_history_and_film_sources_stay_separate(self):
        record = self.record("culture.australia.breaker_morant_history_and_film")
        self.assertEqual(record["historical_person"]["historical_source_id"], "src.awm.breaker_morant")
        self.assertEqual(record["film_representation"]["dialogue_source_id"], "src.aso.breaker_morant_clip3")
        self.assertFalse(record["boundaries"]["film_can_override_official_historical_metadata"])
        self.assertFalse(record["boundaries"]["cultural_admiration_is_historical_exoneration"])

    def test_hawke_record_is_paraphrase_only(self):
        record = self.record("culture.australia.bob_hawke_irreverence")
        self.assertEqual(record["public_persona"]["quotation_storage"], "none")
        self.assertTrue(record["public_persona"]["paraphrase_only"])
        self.assertFalse(record["boundaries"]["public_persona_is_formal_authority"])
        self.assertFalse(record["boundaries"]["larrikin_persona_excludes_grief_or_gentleness"])

    def test_preprint_peer_review_promotion_fails_closed(self):
        altered = copy.deepcopy(self.sources_doc)
        altered["sources"]["src.antipodean_jester"]["peer_reviewed"] = True
        with self.assertRaisesRegex(ValueError, "ARK_AUS_PREPRINT_PEER_REVIEW_PROMOTED"):
            ac.validate_sources(altered, self.policy)

    def test_evidence_support_must_be_declared_by_source(self):
        evidence = {
            "class": "documented_cultural_pattern",
            "source_ids": ["src.abc.original_humour"],
            "supports": ["formal_constitutional_authority"],
        }
        with self.assertRaisesRegex(ValueError, "ARK_AUS_EVIDENCE_SUPPORT_NOT_SOURCE_BOUND"):
            ac.validate_evidence(evidence, self.sources, self.policy)

    def test_film_dialogue_promotion_fails_closed(self):
        altered = copy.deepcopy(self.record("culture.australia.breaker_morant_history_and_film"))
        altered["quotation"]["historical_primary_testimony"] = True
        with self.assertRaisesRegex(ValueError, "ARK_AUS_FILM_PROMOTED_TO_HISTORY"):
            ac.validate_morant(altered, self.sources, self.policy)

    def test_governance_formal_authority_promotion_fails_closed(self):
        altered = copy.deepcopy(self.record("culture.australia.australian_informal_governance"))
        altered["scope"]["formal_authority"] = True
        with self.assertRaisesRegex(ValueError, "ARK_AUS_SCOPE_INVALID"):
            ac.validate_informal_governance(altered, self.sources, self.policy)

    def test_task_expected_answer_cannot_be_reversed(self):
        altered = copy.deepcopy(self.tasks_doc)
        altered["tasks"][0]["questions"][0]["expected"] = "yes"
        with self.assertRaisesRegex(ValueError, "ARK_AUS_TASK_SEMANTIC_BINDING_INVALID"):
            ac.validate_tasks(altered, ac.RECORD_IDS)


if __name__ == "__main__":
    unittest.main()
