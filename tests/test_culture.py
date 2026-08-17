# SPDX-License-Identifier: Apache-2.0
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("culture", ROOT / "tools" / "culture.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)

class CultureTests(unittest.TestCase):
    def test_full_validation(self):
        mod.validate()

    def test_third_party_script_bytes_are_forbidden(self):
        record = mod.load(ROOT / "culture/television/red-dwarf/ouroboros.json")
        record["rights"]["source_bytes_copied"] = True
        with self.assertRaisesRegex(ValueError, "ARK_THIRD_PARTY_BYTES_WITHOUT_RESOLVED_LICENSE"):
            mod.validate_record(record)

    def test_fiction_cannot_be_promoted_to_history(self):
        record = mod.load(ROOT / "culture/television/red-dwarf/ouroboros.json")
        record["fiction_boundary"]["narrative_events_are_historical_evidence"] = True
        with self.assertRaisesRegex(ValueError, "ARK_FICTION_PROMOTED_TO_HISTORY"):
            mod.validate_record(record)

    def test_official_metadata_source_is_required(self):
        record = mod.load(ROOT / "culture/television/red-dwarf/ouroboros.json")
        record["sources"] = [s for s in record["sources"] if s["role"] != "official_metadata"]
        with self.assertRaisesRegex(ValueError, "ARK_CULTURE_OFFICIAL_SOURCE_REQUIRED"):
            mod.validate_record(record)

    def test_unavailable_transcript_is_not_contradicted_and_no_bytes_are_copied(self):
        record = mod.load(ROOT / "culture/television/red-dwarf/ouroboros.json")
        transcript = next(s for s in record["sources"] if s["id"].endswith("ouroboros_transcript"))
        self.assertEqual(transcript["verification_status"], "unavailable_at_ingest")
        self.assertFalse(transcript["source_bytes_copied"])

    def test_permission_is_not_endorsement(self):
        record = mod.load(ROOT / "culture/positions/permission-not-endorsement.json")
        self.assertFalse(record["normalized_position"]["permission_is_endorsement"])
        mod.validate_record(record)

    def test_personal_dislike_does_not_override_license(self):
        record = mod.load(ROOT / "culture/positions/permission-not-endorsement.json")
        self.assertTrue(record["license_effect"]["applicable_repository_licenses_remain_governing"])
        self.assertFalse(record["license_effect"]["reuse_permission_depends_on_personal_approval"])

    def test_first_person_position_is_not_objective_fact(self):
        record = mod.load(ROOT / "culture/positions/permission-not-endorsement.json")
        record["claim_boundary"]["objective_claims_about_named_entities_verified"] = True
        with self.assertRaisesRegex(ValueError, "ARK_OPINION_PROMOTED_TO_OBJECTIVE_FACT"):
            mod.validate_record(record)

    def test_tasks_bind_to_known_records(self):
        index = mod.load(ROOT / "culture/index.json")
        known = {r["id"] for r in index["records"]}
        for entry in index["tasks"]:
            task = mod.load(ROOT / entry["path"])
            mod.validate_task(task, known)

if __name__ == "__main__":
    unittest.main()
