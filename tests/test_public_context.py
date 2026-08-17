# SPDX-License-Identifier: Apache-2.0
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("public_context", ROOT / "tools" / "public_context.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


class PublicContextTests(unittest.TestCase):
    def index(self):
        return mod.load(ROOT / "context/public-seeds.json")

    def seed(self, data, seed_id):
        return next(s for s in data["seeds"] if s["id"] == seed_id)

    def test_full_validation(self):
        mod.validate(self.index())

    def test_private_context_payload_import_is_rejected(self):
        data = self.index()
        data["selection_policy"]["private_payload_imported"] = True
        with self.assertRaisesRegex(ValueError, "ARK_PRIVATE_CONTEXT_IMPORT_FORBIDDEN"):
            mod.validate(data)

    def test_private_context_cannot_become_authority(self):
        data = self.index()
        data["seeds"][0]["source_repository"] = "https://github.com/QSOLKCB/QSOL-CONTEXT"
        with self.assertRaisesRegex(ValueError, "ARK_PRIVATE_CONTEXT_AUTHORITY_FORBIDDEN"):
            mod.validate(data)

    def test_visibility_fails_closed(self):
        data = self.index()
        data["seeds"][0]["visibility"] = "unknown"
        with self.assertRaisesRegex(ValueError, "ARK_PUBLIC_CONTEXT_SEED_VISIBILITY_INVALID"):
            mod.validate(data)

    def test_source_hash_is_required(self):
        data = self.index()
        data["seeds"][1]["source_hash_when_available"]["value"] = ""
        with self.assertRaisesRegex(ValueError, "ARK_PUBLIC_CONTEXT_SOURCE_HASH_INVALID"):
            mod.validate(data)

    def test_seed_set_is_bound(self):
        data = self.index()
        data["seeds"].pop()
        with self.assertRaisesRegex(ValueError, "ARK_PUBLIC_CONTEXT_SEED_SET_INVALID"):
            mod.validate(data)

    def test_duplicate_seed_is_rejected(self):
        data = self.index()
        data["seeds"].append(copy.deepcopy(data["seeds"][0]))
        with self.assertRaisesRegex(ValueError, "ARK_PUBLIC_CONTEXT_SEED_IDS_INVALID"):
            mod.validate(data)

    def test_byte_copy_promotion_is_rejected(self):
        data = self.index()
        data["seeds"][2]["byte_imported"] = True
        with self.assertRaisesRegex(ValueError, "ARK_PUBLIC_CONTEXT_BYTE_IMPORT_FORBIDDEN"):
            mod.validate(data)

    def test_public_record_binding_cannot_drift(self):
        data = self.index()
        project = self.seed(data, "seed:project:deepseekc64")
        project["public_record_id"] = "project:whoami-18437"
        with self.assertRaisesRegex(ValueError, "ARK_PUBLIC_CONTEXT_SEED_BINDING_INVALID"):
            mod.validate(data)

    def test_source_refs_are_semantically_bound(self):
        data = self.index()
        project = self.seed(data, "seed:project:e8-music")
        project["source_refs"] = ["src:made-up-but-shape-valid"]
        with self.assertRaisesRegex(ValueError, "ARK_PUBLIC_CONTEXT_SEED_BINDING_INVALID"):
            mod.validate(data)

    def test_invalid_release_commit_is_rejected(self):
        data = self.index()
        project = self.seed(data, "seed:project:games")
        project["release"]["commit"] = "main"
        with self.assertRaisesRegex(ValueError, "ARK_PUBLIC_CONTEXT_RELEASE_INVALID"):
            mod.validate(data)

    def test_invalid_doi_is_rejected(self):
        data = self.index()
        project = self.seed(data, "seed:project:uff")
        project["publication"]["doi"] = "probably-a-doi"
        with self.assertRaisesRegex(ValueError, "ARK_PUBLIC_CONTEXT_PUBLICATION_INVALID"):
            mod.validate(data)

    def test_saw_uses_pinned_first_party_public_authority(self):
        data = self.index()
        saw = self.seed(data, "seed:project:saw-1")
        self.assertEqual(saw["source_id"], "source.related_repositories")
        self.assertEqual(saw["source_repository"], "https://github.com/QSOLKCB/SAW-1")
        self.assertEqual(saw["release"]["tag"], "v1.0.1")
        self.assertFalse(saw["byte_imported"])
        mod.validate(data)

    def test_saw_first_party_commit_cannot_drift(self):
        data = self.index()
        saw = self.seed(data, "seed:project:saw-1")
        saw["source_ref_or_commit"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "ARK_PUBLIC_CONTEXT_SOURCE_COMMIT_INVALID"):
            mod.validate(data)

    def test_saw_citation_is_bound(self):
        data = self.index()
        saw = self.seed(data, "seed:project:saw-1")
        saw["citation"]["version"] = "v9.9.9"
        with self.assertRaisesRegex(ValueError, "ARK_PUBLIC_CONTEXT_CITATION_INVALID"):
            mod.validate(data)

    def test_saw_metadata_discrepancy_cannot_be_erased(self):
        data = self.index()
        saw = self.seed(data, "seed:project:saw-1")
        saw["publication"]["repository_metadata_version"] = "v1.0.1"
        with self.assertRaisesRegex(ValueError, "ARK_PUBLIC_CONTEXT_PUBLICATION_INVALID"):
            mod.validate(data)


if __name__ == "__main__":
    unittest.main()
