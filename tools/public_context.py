#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Validate the QSOL-ARK Phase-1 public context seed pack."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "context" / "public-seeds.json"

SUBSTRATE_REPO = "https://github.com/QSOLKCB/QSOL-SUBSTRATE"
SUBSTRATE_COMMIT = "60e8cfeefa859df375f9f4d2fdb735edb1249db8"
SUBSTRATE_LICENSE = "Apache-2.0 source repository; ARK stores normalized metadata only"
SAW_REPO = "https://github.com/QSOLKCB/SAW-1"
SAW_COMMIT = "db4166e8903ccee055f8d847d846b591012641f2"
SAW_LICENSE = "MPL-2.0 repository code; CC-BY-4.0 technical note and metadata; ARK stores normalized metadata only"
SAW_TITLE = "SAW-1 — Spooky Action at Work: A Lightweight Formalization of ETQ-101 Sonification, Industrial Transformation, and an Accidental (3,2) Correspondence"
SAW_CITATION = "Slade, T. (2026). SAW-1 — Spooky Action at Work: A Lightweight Formalization of ETQ-101 Sonification, Industrial Transformation, and an Accidental (3,2) Correspondence (Version v1.0.1). Zenodo. https://doi.org/10.5281/zenodo.21984110"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
DOI = re.compile(r"^10\.5281/zenodo\.[0-9]+$")


def sb(record, path, blob, refs, release=None, publication=None):
    out = {
        "authority": "substrate",
        "public_record_id": record,
        "source_id": "source.qsol_substrate",
        "source_repository": SUBSTRATE_REPO,
        "source_ref_or_commit": SUBSTRATE_COMMIT,
        "source_path_or_artifact": path,
        "source_hash": blob,
        "source_refs": refs,
        "epistemic_class": "known_public_record",
        "canonical_or_derived": "explicit_public_source_export",
        "license": SUBSTRATE_LICENSE,
    }
    if release is not None:
        out["release"] = release
    if publication is not None:
        out["publication"] = publication
    return out


EXPECTED = {
    "seed:identity:trent-slade": sb(
        "person:trent-slade", "identity/public.json#person:trent-slade",
        "7d5af9f17cd1c202ac44afbf73a1f3de9d862560",
        ["src:github-profile-emergentmonk", "src:spectral-readme"]),
    "seed:project:qsol-substrate": sb(
        "project:qsol-substrate", "projects/index.json#project:qsol-substrate",
        "3ae2d0c46f8d763b81bf81a7e78218ca1a3dec4b",
        ["src:qsol-substrate-readme", "src:qsol-substrate-v1.0.0-release"],
        {"tag": "v1.0.0", "commit": "4483582173abf62f61bcc18076b22c1db10b26ca"},
        {"doi": "10.5281/zenodo.21959180", "version": "1.0.0"}),
    "seed:project:whoami-18437": sb(
        "project:whoami-18437", "projects/index.json#project:whoami-18437",
        "3ae2d0c46f8d763b81bf81a7e78218ca1a3dec4b",
        ["src:whoami-readme", "src:whoami-v1.0.1-release"],
        {"tag": "v1.0.1", "commit": "18c3a6441a2c2d262cb0b4b3e5f9403f5a5827ee"}),
    "seed:project:deepseekc64": sb(
        "project:deepseekc64", "projects/index.json#project:deepseekc64",
        "3ae2d0c46f8d763b81bf81a7e78218ca1a3dec4b",
        ["src:deepseekc64-readme", "src:deepseekc64-v1.0.0-release"],
        {"tag": "v1.0.0", "commit": "bb0ee535c64de0f65255111f334dbe770d387392"},
        {"doi": "10.5281/zenodo.21935097", "version": "1.0.0"}),
    "seed:project:e8-music": sb(
        "project:e8-music", "projects/index.json#project:e8-music",
        "3ae2d0c46f8d763b81bf81a7e78218ca1a3dec4b",
        ["src:e8-music-readme", "src:e8-music-v1.1.0-release"],
        {"tag": "v1.1.0", "commit": "d8e5983d84af03f03a969abe3356dcf80c0e0e97"}),
    "seed:project:games": sb(
        "project:games", "projects/index.json#project:games",
        "3ae2d0c46f8d763b81bf81a7e78218ca1a3dec4b",
        ["src:games-v1.2.0-release"],
        {"tag": "v1.2.0", "commit": "e4ececc36529e7cca56c87bc18191f7ef322d695"}),
    "seed:project:uff": sb(
        "project:uff", "projects/index.json#project:uff",
        "3ae2d0c46f8d763b81bf81a7e78218ca1a3dec4b",
        ["src:uff-readme", "src:uff-v5.2.0-release"],
        {"tag": "v5.2.0", "commit": "3db10dbc4e9756360252ec32b80d9610d7b31adc"},
        {"doi": "10.5281/zenodo.21911644", "version": "5.2.0"}),
    "seed:project:saw-1": {
        "authority": "first_party",
        "public_record_id": "github-release:371906058",
        "source_id": "source.related_repositories",
        "source_repository": SAW_REPO,
        "source_ref_or_commit": SAW_COMMIT,
        "source_path_or_artifact": "CITATION.cff#preferred-citation",
        "source_hash": "ed5d748e1e8d828be00ffd5766182f69bb315894",
        "source_refs": ["src:saw-1-v1.0.1-release", "src:saw-1-citation-v1.0.1"],
        "epistemic_class": "known_public_record_with_metadata_discrepancy",
        "canonical_or_derived": "first_party_public_evidence",
        "license": SAW_LICENSE,
        "release": {"tag": "v1.0.1", "commit": SAW_COMMIT},
        "publication": {
            "doi": "10.5281/zenodo.21984110",
            "version": "v1.0.1",
            "repository_metadata_version": "1.0.0",
            "version_state": "release_tag_and_embedded_publication_metadata_differ",
        },
        "citation": {
            "author": "Slade, T.",
            "year": 2026,
            "title": SAW_TITLE,
            "version": "v1.0.1",
            "publisher": "Zenodo",
            "doi": "10.5281/zenodo.21984110",
            "text": SAW_CITATION,
            "provenance": "maintainer_supplied_citation; DOI, title, public release tag, commit, and repository metadata independently pinned; embedded CITATION.cff and .zenodo.json at v1.0.1 still declare publication version 1.0.0",
        },
    },
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(ok: bool, code: str) -> None:
    if not ok:
        raise ValueError(code)


def validate(index: dict | None = None) -> None:
    data = load(INDEX) if index is None else index
    require(data.get("type") == "qsol-ark-public-context-seed-index", "ARK_PUBLIC_CONTEXT_TYPE_INVALID")
    require(data.get("protocol") == "QSOL-ARK", "ARK_PUBLIC_CONTEXT_PROTOCOL_INVALID")
    require(data.get("schema_version") == "0.1.0", "ARK_PUBLIC_CONTEXT_SCHEMA_UNSUPPORTED")
    require(data.get("visibility") == "public", "ARK_PUBLIC_CONTEXT_VISIBILITY_INVALID")

    policy = data.get("selection_policy")
    require(isinstance(policy, dict), "ARK_PUBLIC_CONTEXT_SELECTION_INVALID")
    require(policy.get("private_payload_imported") is False, "ARK_PRIVATE_CONTEXT_IMPORT_FORBIDDEN")
    require(policy.get("private_repository_authoritative") is False, "ARK_PRIVATE_CONTEXT_AUTHORITY_FORBIDDEN")
    require(policy.get("authority_rule") == "PRIVATE_DISCOVERY != PUBLIC_AUTHORITY", "ARK_PUBLIC_CONTEXT_AUTHORITY_RULE_INVALID")

    substrate = data.get("substrate_binding")
    require(isinstance(substrate, dict), "ARK_PUBLIC_CONTEXT_SUBSTRATE_INVALID")
    require(substrate.get("repository") == SUBSTRATE_REPO, "ARK_PUBLIC_CONTEXT_SUBSTRATE_INVALID")
    require(substrate.get("commit") == SUBSTRATE_COMMIT, "ARK_PUBLIC_CONTEXT_SUBSTRATE_COMMIT_INVALID")
    require(substrate.get("visibility") == "public", "ARK_PUBLIC_CONTEXT_SUBSTRATE_INVALID")
    require(substrate.get("source_license") == "Apache-2.0", "ARK_PUBLIC_CONTEXT_LICENSE_INVALID")
    receipts = substrate.get("registry_files")
    require(isinstance(receipts, list) and receipts, "ARK_PUBLIC_CONTEXT_RECEIPTS_INVALID")
    receipt_paths = set()
    for receipt in receipts:
        require(isinstance(receipt, dict), "ARK_PUBLIC_CONTEXT_RECEIPTS_INVALID")
        path = receipt.get("path")
        digest = receipt.get("git_blob_sha1")
        require(isinstance(path, str) and path and path not in receipt_paths, "ARK_PUBLIC_CONTEXT_RECEIPTS_INVALID")
        require(HEX40.fullmatch(str(digest or "")) is not None, "ARK_PUBLIC_CONTEXT_RECEIPTS_INVALID")
        receipt_paths.add(path)
    require({"identity/public.json", "projects/index.json", "publications/index.json", "sources/index.json"}.issubset(receipt_paths), "ARK_PUBLIC_CONTEXT_RECEIPTS_INVALID")

    seeds = data.get("seeds")
    require(isinstance(seeds, list), "ARK_PUBLIC_CONTEXT_SEEDS_INVALID")
    ids = [seed.get("id") for seed in seeds if isinstance(seed, dict)]
    require(len(ids) == len(seeds) == len(set(ids)), "ARK_PUBLIC_CONTEXT_SEED_IDS_INVALID")
    require(set(ids) == set(EXPECTED), "ARK_PUBLIC_CONTEXT_SEED_SET_INVALID")

    for seed in seeds:
        require(isinstance(seed, dict), "ARK_PUBLIC_CONTEXT_SEED_INVALID")
        expected = EXPECTED[seed["id"]]
        repo = seed.get("source_repository")

        require(seed.get("kind") in {"identity", "project"}, "ARK_PUBLIC_CONTEXT_SEED_KIND_INVALID")
        require(seed.get("visibility") == "public", "ARK_PUBLIC_CONTEXT_SEED_VISIBILITY_INVALID")
        require("QSOL-CONTEXT" not in str(repo), "ARK_PRIVATE_CONTEXT_AUTHORITY_FORBIDDEN")
        require(seed.get("epistemic_class") == expected["epistemic_class"], "ARK_PUBLIC_CONTEXT_EPISTEMIC_INVALID")
        require(seed.get("canonical_or_derived") == expected["canonical_or_derived"], "ARK_PUBLIC_CONTEXT_CANONICAL_STATUS_INVALID")
        require(seed.get("source_id") == expected["source_id"], "ARK_PUBLIC_CONTEXT_SOURCE_INVALID")
        require(repo == expected["source_repository"], "ARK_PUBLIC_CONTEXT_SOURCE_INVALID")
        require(seed.get("source_ref_or_commit") == expected["source_ref_or_commit"], "ARK_PUBLIC_CONTEXT_SOURCE_COMMIT_INVALID")
        require(HEX40.fullmatch(str(seed.get("source_ref_or_commit", ""))) is not None, "ARK_PUBLIC_CONTEXT_SOURCE_COMMIT_INVALID")
        require(seed.get("public_record_id") == expected["public_record_id"], "ARK_PUBLIC_CONTEXT_SEED_BINDING_INVALID")
        require(seed.get("source_path_or_artifact") == expected["source_path_or_artifact"], "ARK_PUBLIC_CONTEXT_SEED_BINDING_INVALID")
        require(seed.get("source_refs") == expected["source_refs"], "ARK_PUBLIC_CONTEXT_SEED_BINDING_INVALID")
        require(all(isinstance(ref, str) and ref.startswith("src:") for ref in seed["source_refs"]), "ARK_PUBLIC_CONTEXT_SOURCE_REFS_INVALID")

        digest = seed.get("source_hash_when_available")
        require(isinstance(digest, dict) and digest.get("algorithm") == "git_blob_sha1", "ARK_PUBLIC_CONTEXT_SOURCE_HASH_INVALID")
        require(digest.get("value") == expected["source_hash"], "ARK_PUBLIC_CONTEXT_SOURCE_HASH_INVALID")
        require(HEX40.fullmatch(str(digest.get("value", ""))) is not None, "ARK_PUBLIC_CONTEXT_SOURCE_HASH_INVALID")
        require(seed.get("license") == expected["license"], "ARK_PUBLIC_CONTEXT_LICENSE_INVALID")
        require(seed.get("byte_imported") is False, "ARK_PUBLIC_CONTEXT_BYTE_IMPORT_FORBIDDEN")
        require(isinstance(seed.get("subject_url"), str) and seed["subject_url"].startswith("https://github.com/"), "ARK_PUBLIC_CONTEXT_SUBJECT_INVALID")
        require(isinstance(seed.get("recovery_role"), str) and seed["recovery_role"], "ARK_PUBLIC_CONTEXT_RECOVERY_ROLE_INVALID")

        if expected["authority"] == "substrate":
            require(repo == SUBSTRATE_REPO and seed["source_ref_or_commit"] == substrate["commit"], "ARK_PUBLIC_CONTEXT_SOURCE_INVALID")
        elif expected["authority"] == "first_party":
            require(repo == SAW_REPO and seed["source_ref_or_commit"] == SAW_COMMIT, "ARK_PUBLIC_CONTEXT_FIRST_PARTY_SOURCE_INVALID")
        else:
            raise ValueError("ARK_PUBLIC_CONTEXT_AUTHORITY_CLASS_INVALID")

        require(seed.get("release") == expected.get("release"), "ARK_PUBLIC_CONTEXT_RELEASE_INVALID")
        if seed.get("release") is not None:
            require(isinstance(seed["release"].get("tag"), str), "ARK_PUBLIC_CONTEXT_RELEASE_INVALID")
            require(HEX40.fullmatch(str(seed["release"].get("commit", ""))) is not None, "ARK_PUBLIC_CONTEXT_RELEASE_INVALID")

        require(seed.get("publication") == expected.get("publication"), "ARK_PUBLIC_CONTEXT_PUBLICATION_INVALID")
        if seed.get("publication") is not None:
            require(DOI.fullmatch(str(seed["publication"].get("doi", ""))) is not None, "ARK_PUBLIC_CONTEXT_PUBLICATION_INVALID")
            require(isinstance(seed["publication"].get("version"), str) and seed["publication"]["version"], "ARK_PUBLIC_CONTEXT_PUBLICATION_INVALID")

        require(seed.get("citation") == expected.get("citation"), "ARK_PUBLIC_CONTEXT_CITATION_INVALID")
        if seed.get("citation") is not None:
            require(seed["citation"].get("doi") == seed["publication"].get("doi"), "ARK_PUBLIC_CONTEXT_CITATION_INVALID")

    print(f"ARK_PUBLIC_CONTEXT_OK seeds={len(seeds)} private_bytes=0 authority=public")


def main() -> int:
    try:
        validate()
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
