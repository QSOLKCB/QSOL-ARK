# SPDX-License-Identifier: Apache-2.0
import importlib.util
import tempfile
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

    def this_is_fine(self):
        return mod.load(ROOT / "culture/memes/this-is-fine.json")

    def this_is_fine_task(self):
        return mod.load(ROOT / "culture/tasks/this-is-fine-boundary.json")

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

    def test_cassandra_parallel_prose_cannot_invent_naming_history(self):
        record = self.cassandra()
        record["cultural_context"]["ark_parallel"]["description"] = "ARK-CANARY was named after the Red Dwarf Canaries."
        with self.assertRaisesRegex(ValueError, "ARK_CULTURAL_PARALLEL_DESCRIPTION_INVALID"):
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

    def test_cassandra_maintainer_reference_uses_declared_evidence_class(self):
        record = self.cassandra()
        supplied = next(s for s in record["sources"] if s["id"] == "source.wikipedia.cassandra_red_dwarf")
        self.assertEqual(supplied["role"], "third_party_reference")
        supplied["role"] = "maintainer_supplied_reference"
        with self.assertRaisesRegex(ValueError, "ARK_CULTURE_REFERENCE_INVALID"):
            mod.validate_record(record)

    def test_cassandra_ark_canary_receipt_is_bound(self):
        record = self.cassandra()
        internal = next(s for s in record["sources"] if s["id"] == "source.qsol_ark.ark_canary")
        internal["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "ARK_CULTURE_ARK_CANARY_BINDING_INVALID"):
            mod.validate_record(record)

    def test_cassandra_ark_canary_payload_is_hashed_not_just_receipt(self):
        record = self.cassandra()
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            capsule = temp_root / "capsules" / "minimal"
            capsule.mkdir(parents=True)
            (capsule / "ARK-CANARY.txt").write_text("ALTERED CANARY\n", encoding="utf-8")
            (capsule / "SHA256SUMS").write_text(f"{mod.ARK_CANARY_SHA256}  ARK-CANARY.txt\n", encoding="utf-8")
            old_root = mod.ROOT
            mod.ROOT = temp_root
            try:
                with self.assertRaisesRegex(ValueError, "ARK_CULTURE_ARK_CANARY_BINDING_INVALID"):
                    mod.validate_record(record)
            finally:
                mod.ROOT = old_root

    def test_cassandra_copies_no_third_party_script_bytes(self):
        record = self.cassandra()
        self.assertFalse(record["rights"]["source_bytes_copied"])
        self.assertFalse(record["rights"]["script_text_copied"])

    def test_this_is_fine_record_is_validated(self):
        mod.validate_record(self.this_is_fine())

    def test_meme_caption_cannot_be_promoted_to_ground_truth(self):
        record = self.this_is_fine()
        record["fiction_boundary"]["literal_caption_establishes_real_world_safety"] = True
        with self.assertRaisesRegex(ValueError, "ARK_MEME_BOUNDARY_INVALID"):
            mod.validate_record(record)

    def test_meme_depicted_scene_cannot_be_promoted_to_history(self):
        record = self.this_is_fine()
        record["fiction_boundary"]["depicted_scene_is_historical_evidence"] = True
        with self.assertRaisesRegex(ValueError, "ARK_MEME_BOUNDARY_INVALID"):
            mod.validate_record(record)

    def test_meme_interpretation_cannot_be_promoted_to_universal_meaning(self):
        record = self.this_is_fine()
        record["fiction_boundary"]["derived_interpretation_is_universal_meaning"] = True
        with self.assertRaisesRegex(ValueError, "ARK_MEME_BOUNDARY_INVALID"):
            mod.validate_record(record)

    def test_meme_context_prose_is_bound(self):
        record = self.this_is_fine()
        record["cultural_context"]["derived_interpretation"] = "The caption proves the room is safe."
        with self.assertRaisesRegex(ValueError, "ARK_MEME_CONTEXT_INVALID"):
            mod.validate_record(record)

    def test_meme_history_reference_cannot_be_promoted_to_creator_source(self):
        record = self.this_is_fine()
        source = next(s for s in record["sources"] if s["id"] == "source.knowyourmeme.this_is_fine")
        source["role"] = "official_metadata"
        with self.assertRaisesRegex(ValueError, "ARK_MEME_HISTORY_SOURCE_INVALID"):
            mod.validate_record(record)

    def test_meme_transmission_history_source_id_is_bound(self):
        record = self.this_is_fine()
        record["cultural_context"]["transmission_history"]["source_id"] = "source.example.invalid"
        with self.assertRaisesRegex(ValueError, "ARK_MEME_CONTEXT_INVALID"):
            mod.validate_record(record)

    def test_known_meme_hash_does_not_grant_copy_permission(self):
        record = self.this_is_fine()
        crop = next(s for s in record["sources"] if s["id"] == "source.maintainer.this_is_fine_crop")
        self.assertEqual(crop["sha256"], mod.THIS_IS_FINE_CROP_SHA256)
        self.assertFalse(crop["repository_bytes_copied"])
        record["rights"]["image_bytes_copied"] = True
        with self.assertRaisesRegex(ValueError, "ARK_THIRD_PARTY_BYTES_WITHOUT_RESOLVED_LICENSE"):
            mod.validate_record(record)

    def test_observed_meme_crop_is_not_claimed_as_canonical_master(self):
        record = self.this_is_fine()
        crop = next(s for s in record["sources"] if s["id"] == "source.maintainer.this_is_fine_crop")
        crop["canonical_master_claimed"] = True
        with self.assertRaisesRegex(ValueError, "ARK_MEME_OBSERVED_CROP_INVALID"):
            mod.validate_record(record)

    def test_meme_sources_declare_complete_evidence_state(self):
        record = self.this_is_fine()
        for source in record["sources"]:
            with self.subTest(source=source["id"]):
                self.assertTrue(mod.MEME_SOURCE_EVIDENCE_FIELDS.issubset(source))
                mod.validate_meme_source_evidence(source)

    def test_meme_source_missing_evidence_fails_closed(self):
        record = self.this_is_fine()
        source = record["sources"][0]
        del source["visibility"]
        with self.assertRaisesRegex(ValueError, "ARK_MEME_SOURCE_EVIDENCE_INCOMPLETE"):
            mod.validate_record(record)

    def test_meme_source_canonical_status_is_bound(self):
        record = self.this_is_fine()
        source = next(s for s in record["sources"] if s["id"] == "source.knowyourmeme.this_is_fine")
        source["canonical_status"] = "canonical_for_declared_supports"
        with self.assertRaisesRegex(ValueError, "ARK_MEME_HISTORY_SOURCE_INVALID"):
            mod.validate_record(record)

    def test_meme_task_answer_is_semantically_bound(self):
        task = self.this_is_fine_task()
        next(q for q in task["questions"] if q["id"] == "meme-04")["expected"] = "yes"
        with self.assertRaisesRegex(ValueError, "ARK_CULTURE_TASK_BINDING_INVALID"):
            mod.validate_task(task, self.known_records())

    def test_meme_task_prompt_and_answer_cannot_drift_together(self):
        task = self.this_is_fine_task()
        q = next(q for q in task["questions"] if q["id"] == "meme-04")
        q["prompt"] = "Does a known hash prove redistribution permission?"
        q["expected"] = "yes"
        with self.assertRaisesRegex(ValueError, "ARK_CULTURE_TASK_BINDING_INVALID"):
            mod.validate_task(task, self.known_records())

    def test_meme_record_allows_benign_inner_metadata_extension(self):
        record = self.this_is_fine()
        record["real_world_metadata"]["archive_note"] = "non-normative extension"
        record["cultural_context"]["regional_notes"] = []
        record["rights"]["review_note"] = "non-normative extension"
        mod.validate_record(record)

    def test_meme_policy_is_structured_and_versioned(self):
        policy = mod.load(ROOT / "ai/cultural-artifact-policy.json")
        meme = policy["meme_archaeology"]
        self.assertEqual(meme["policy_version"], mod.MEME_POLICY_VERSION)
        self.assertEqual(set(meme["canonical_invariants"]), mod.MEME_INVARIANTS)
        self.assertEqual(set(meme["source_evidence"]["required_fields"]), mod.MEME_SOURCE_EVIDENCE_FIELDS)
        mod.validate_policy(policy)

    def test_meme_invariant_list_has_one_machine_source(self):
        for rel in ["README.md", "README4AI.md", "AGENTS.md", "docs/MEME-ARCHAEOLOGY.md", "docs/COMPUTER-CULTURE.md"]:
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertNotIn("MEME != DECORATIVE_IMAGE", text, rel)
        policy = mod.load(ROOT / "ai/cultural-artifact-policy.json")
        self.assertIn("MEME != DECORATIVE_IMAGE", policy["meme_archaeology"]["canonical_invariants"])

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
