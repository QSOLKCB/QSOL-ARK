# SPDX-License-Identifier: Apache-2.0
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("culture", ROOT / "tools" / "culture.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)

class CultureTests(unittest.TestCase):
    def ouroboros(self):
        return mod.load(ROOT / "culture/television/red-dwarf/ouroboros.json")

    def cassandra(self):
        return mod.load(ROOT / "culture/television/red-dwarf/cassandra-canaries.json")

    def position(self):
        return mod.load(ROOT / "culture/positions/permission-not-endorsement.json")

    def known_records(self):
        index = mod.load(ROOT / "culture/index.json")
        return {r["id"] for r in index["records"]}

    def test_full_validation(self):
        mod.validate()

    def test_third_party_script_bytes_are_forbidden(self):
        record = self.ouroboros()
        record["rights"]["source_bytes_copied"] = True
        with self.assertRaisesRegex(ValueError, "ARK_THIRD_PARTY_BYTES_WITHOUT_RESOLVED_LICENSE"):
            mod.validate_record(record)

    def test_undeclared_third_party_payload_field_is_rejected(self):
        record = self.ouroboros()
        record["script_text"] = "undeclared third-party payload"
        with self.assertRaisesRegex(ValueError, "ARK_CULTURE_RECORD_SHAPE_INVALID"):
            mod.validate_record(record)

    def test_fiction_cannot_be_promoted_to_history(self):
        record = self.ouroboros()
        record["fiction_boundary"]["narrative_events_are_historical_evidence"] = True
        with self.assertRaisesRegex(ValueError, "ARK_FICTION_PROMOTED_TO_HISTORY"):
            mod.validate_record(record)

    def test_derived_interpretation_cannot_be_promoted(self):
        record = self.ouroboros()
        record["cultural_context"]["interpretation_status"] = "official_metadata"
        with self.assertRaisesRegex(ValueError, "ARK_CULTURE_INTERPRETATION_PROMOTED"):
            mod.validate_record(record)

    def test_epistemic_status_cannot_promote_interpretation(self):
        record = self.ouroboros()
        record["epistemic_status"] = "verified_history"
        with self.assertRaisesRegex(ValueError, "ARK_CULTURE_INTERPRETATION_PROMOTED"):
            mod.validate_record(record)

    def test_official_metadata_source_identity_is_bound(self):
        record = self.ouroboros()
        official = next(s for s in record["sources"] if s["role"] == "official_metadata")
        official["url"] = "https://example.invalid/unrelated"
        with self.assertRaisesRegex(ValueError, "ARK_CULTURE_OFFICIAL_SOURCE_REQUIRED"):
            mod.validate_record(record)

    def test_official_metadata_supports_are_bound(self):
        record = self.ouroboros()
        official = next(s for s in record["sources"] if s["role"] == "official_metadata")
        official["supports"] = ["series"]
        with self.assertRaisesRegex(ValueError, "ARK_CULTURE_OFFICIAL_SOURCE_REQUIRED"):
            mod.validate_record(record)

    def test_unavailable_transcript_is_not_contradicted_and_no_bytes_are_copied(self):
        record = self.ouroboros()
        transcript = next(s for s in record["sources"] if s["id"].endswith("ouroboros_transcript"))
        self.assertEqual(transcript["verification_status"], "unavailable_at_ingest")
        self.assertFalse(transcript["source_bytes_copied"])

    def test_cassandra_record_is_validated(self):
        mod.validate_record(self.cassandra())

    def test_cassandra_parallel_is_not_naming_provenance(self):
        record = self.cassandra()
        record["cultural_context"]["ark_parallel"]["naming_origin_claimed"] = True
        with self.assertRaisesRegex(ValueError, "ARK_CULTURAL_PARALLEL_PROMOTED_TO_NAMING_PROVENANCE"):
            mod.validate_record(record)

    def test_cassandra_boundary_rejects_naming_provenance_promotion(self):
        record = self.cassandra()
        record["fiction_boundary"]["cultural_parallel_is_naming_provenance"] = True
        with self.assertRaisesRegex(ValueError, "ARK_CULTURAL_PARALLEL_PROMOTED_TO_NAMING_PROVENANCE"):
            mod.validate_record(record)

    def test_cassandra_official_source_is_bound(self):
        record = self.cassandra()
        official = next(s for s in record["sources"] if s["id"] == "source.red_dwarf.official.cassandra")
        official["supports"] = ["series"]
        with self.assertRaisesRegex(ValueError, "ARK_CULTURE_OFFICIAL_SOURCE_REQUIRED"):
            mod.validate_record(record)

    def test_cassandra_ark_canary_receipt_is_bound(self):
        record = self.cassandra()
        internal = next(s for s in record["sources"] if s["id"] == "source.qsol_ark.ark_canary")
        internal["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "ARK_CULTURE_ARK_CANARY_BINDING_INVALID"):
            mod.validate_record(record)

    def test_cassandra_copies_no_third_party_script_bytes(self):
        record = self.cassandra()
        self.assertFalse(record["rights"]["source_bytes_copied"])
        self.assertFalse(record["rights"]["script_text_copied"])

    def test_permission_is_not_endorsement(self):
        record = self.position()
        self.assertFalse(record["normalized_position"]["permission_is_endorsement"])
        mod.validate_record(record)

    def test_normalized_human_review_position_is_bound(self):
        record = self.position()
        record["normalized_position"]["supports_meaningful_human_review_for_serious_platform_enforcement"] = False
        with self.assertRaisesRegex(ValueError, "ARK_CULTURE_POSITION_NORMALIZATION_INVALID"):
            mod.validate_record(record)

    def test_normalized_open_source_position_is_bound(self):
        record = self.position()
        record["normalized_position"]["supports_open_source_permissions_even_for_strongly_disliked_parties"] = False
        with self.assertRaisesRegex(ValueError, "ARK_CULTURE_POSITION_NORMALIZATION_INVALID"):
            mod.validate_record(record)

    def test_verbatim_statement_is_hash_bound(self):
        record = self.position()
        record["verbatim_statement"] += " altered"
        with self.assertRaisesRegex(ValueError, "ARK_CULTURE_QUOTATION_MISMATCH"):
            mod.validate_record(record)

    def test_personal_dislike_does_not_override_license(self):
        record = self.position()
        self.assertTrue(record["license_effect"]["applicable_repository_licenses_remain_governing"])
        self.assertFalse(record["license_effect"]["reuse_permission_depends_on_personal_approval"])

    def test_first_person_position_is_not_objective_fact(self):
        record = self.position()
        record["claim_boundary"]["objective_claims_about_named_entities_verified"] = True
        with self.assertRaisesRegex(ValueError, "ARK_OPINION_PROMOTED_TO_OBJECTIVE_FACT"):
            mod.validate_record(record)

    def test_unsupported_task_schema_version_fails_closed(self):
        task = mod.load(ROOT / "culture/tasks/ouroboros-boundary.json")
        task["schema_version"] = "999.0.0"
        with self.assertRaisesRegex(ValueError, "ARK_CULTURE_TASK_SCHEMA_UNSUPPORTED"):
            mod.validate_task(task, self.known_records())

    def test_bootstrap_loads_all_cultural_schemas(self):
        bootstrap = mod.load(ROOT / "ai/bootstrap.json")
        load_order = set(bootstrap["load_order"])
        self.assertIn("schema/cultural-artifact-policy.schema.json", load_order)
        self.assertIn("schema/culture-index.schema.json", load_order)
        self.assertIn("schema/cultural-record.schema.json", load_order)
        self.assertIn("schema/cultural-recovery-task.schema.json", load_order)

    def test_cultural_record_schema_rejects_additional_top_level_fields(self):
        schema = mod.load(ROOT / "schema/cultural-record.schema.json")
        self.assertFalse(schema["additionalProperties"])

    def test_tasks_bind_to_known_records(self):
        index = mod.load(ROOT / "culture/index.json")
        known = {r["id"] for r in index["records"]}
        for entry in index["tasks"]:
            task = mod.load(ROOT / entry["path"])
            mod.validate_task(task, known)

if __name__ == "__main__":
    unittest.main()
