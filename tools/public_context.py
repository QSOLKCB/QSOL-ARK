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

EXPECTED_SEEDS = {
    "seed:identity:trent-slade",
    "seed:project:qsol-substrate",
    "seed:project:whoami-18437",
    "seed:project:deepseekc64",
    "seed:project:e8-music",
    "seed:project:games",
    "seed:project:uff",
}
ALLOWED_KINDS = {"identity", "project"}
EXPECTED_BINDINGS = {
    "seed:identity:trent-slade": {
        "public_record_id": "person:trent-slade",
        "source_path_or_artifact": "identity/public.json#person:trent-slade",
        "source_refs": ["src:github-profile-emergentmonk", "src:spectral-readme"],
    },
    "seed:project:qsol-substrate": {
        "public_record_id": "project:qsol-substrate",
        "source_path_or_artifact": "projects/index.json#project:qsol-substrate",
        "source_refs": ["src:qsol-substrate-readme", "src:qsol-substrate-v1.0.0-release"],
        "release": {"tag": "v1.0.0", "commit": "4483582173abf62f61bcc18076b22c1db10b26ca"},
        "publication": {"doi": "10.5281/zenodo.21959180", "version": "1.0.0"},
    },
    "seed:project:whoami-18437": {
        "public_record_id": "project:whoami-18437",
        "source_path_or_artifact": "projects/index.json#project:whoami-18437",
        "source_refs": ["src:whoami-readme", "src:whoami-v1.0.1-release"],
        "release": {"tag": "v1.0.1", "commit": "18c3a6441a2c2d262cb0b4b3e5f9403f5a5827ee"},
    },
    "seed:project:deepseekc64": {
        "public_record_id": "project:deepseekc64",
        "source_path_or_artifact": "projects/index.json#project:deepseekc64",
        "source_refs": ["src:deepseekc64-readme", "src:deepseekc64-v1.0.0-release"],
        "release": {"tag": "v1.0.0", "commit": "bb0ee535c64de0f65255111f334dbe770d387392"},
        "publication": {"doi": "10.5281/zenodo.21935097", "version": "1.0.0"},
    },
    "seed:project:e8-music": {
        "public_record_id": "project:e8-music",
        "source_path_or_artifact": "projects/index.json#project:e8-music",
        "source_refs": ["src:e8-music-readme", "src:e8-music-v1.1.0-release"],
        "release": {"tag": "v1.1.0", "commit": "d8e5983d84af03f03a969abe3356dcf80c0e0e97"},
    },
    "seed:project:games": {
        "public_record_id": "project:games",
        "source_path_or_artifact": "projects/index.json#project:games",
        "source_refs": ["src:games-v1.2.0-release"],
        "release": {"tag": "v1.2.0", "commit": "e4ececc36529e7cca56c87bc18191f7ef322d695"},
    },
    "seed:project:uff": {
        "public_record_id": "project:uff",
        "source_path_or_artifact": "projects/index.json#project:uff",
        "source_refs": ["src:uff-readme", "src:uff-v5.2.0-release"],
        "release": {"tag": "v5.2.0", "commit": "3db10dbc4e9756360252ec32b80d9610d7b31adc"},
        "publication": {"doi": "10.5281/zenodo.21911644", "version": "5.2.0"},
    },
}
HEX40 = re.compile(r"^[0-9a-f]{40}$")
DOI = re.compile(r"^10\.5281/zenodo\.[0-9]+$")


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ValueError(code)


def validate(index: dict | None = None) -> None:
    data = load(INDEX) if index is None else index
    require(data.get("type") == "qsol-ark-public-context-seed-index", "ARK_PUBLIC_CONTEXT_TYPE_INVALID")
    require(data.get("protocol") == "QSOL-ARK", "ARK_PUBLIC_CONTEXT_PROTOCOL_INVALID")
    require(data.get("schema_version") == "0.1.0", "ARK_PUBLIC_CONTEXT_SCHEMA_UNSUPPORTED")
    require(data.get("visibility") == "public", "ARK_PUBLIC_CONTEXT_VISIBILITY_INVALID")

    selection = data.get("selection_policy")
    require(isinstance(selection, dict), "ARK_PUBLIC_CONTEXT_SELECTION_INVALID")
    require(selection.get("private_payload_imported") is False, "ARK_PRIVATE_CONTEXT_IMPORT_FORBIDDEN")
    require(selection.get("private_repository_authoritative") is False, "ARK_PRIVATE_CONTEXT_AUTHORITY_FORBIDDEN")
    require(selection.get("authority_rule") == "PRIVATE_DISCOVERY != PUBLIC_AUTHORITY",
            "ARK_PUBLIC_CONTEXT_AUTHORITY_RULE_INVALID")

    substrate = data.get("substrate_binding")
    require(isinstance(substrate, dict), "ARK_PUBLIC_CONTEXT_SUBSTRATE_INVALID")
    require(substrate.get("repository") == "https://github.com/QSOLKCB/QSOL-SUBSTRATE",
            "ARK_PUBLIC_CONTEXT_SUBSTRATE_INVALID")
    require(HEX40.fullmatch(str(substrate.get("commit", ""))) is not None,
            "ARK_PUBLIC_CONTEXT_SUBSTRATE_COMMIT_INVALID")
    require(substrate.get("visibility") == "public", "ARK_PUBLIC_CONTEXT_SUBSTRATE_INVALID")
    require(substrate.get("source_license") == "Apache-2.0", "ARK_PUBLIC_CONTEXT_LICENSE_INVALID")
    registry_files = substrate.get("registry_files")
    require(isinstance(registry_files, list) and registry_files, "ARK_PUBLIC_CONTEXT_RECEIPTS_INVALID")
    paths = set()
    for item in registry_files:
        require(isinstance(item, dict), "ARK_PUBLIC_CONTEXT_RECEIPTS_INVALID")
        path = item.get("path")
        digest = item.get("git_blob_sha1")
        require(isinstance(path, str) and path and path not in paths, "ARK_PUBLIC_CONTEXT_RECEIPTS_INVALID")
        require(HEX40.fullmatch(str(digest or "")) is not None, "ARK_PUBLIC_CONTEXT_RECEIPTS_INVALID")
        paths.add(path)
    require({"identity/public.json", "projects/index.json", "publications/index.json", "sources/index.json"}.issubset(paths),
            "ARK_PUBLIC_CONTEXT_RECEIPTS_INVALID")

    seeds = data.get("seeds")
    require(isinstance(seeds, list), "ARK_PUBLIC_CONTEXT_SEEDS_INVALID")
    ids = [s.get("id") for s in seeds if isinstance(s, dict)]
    require(len(ids) == len(seeds) == len(set(ids)), "ARK_PUBLIC_CONTEXT_SEED_IDS_INVALID")
    require(set(ids) == EXPECTED_SEEDS, "ARK_PUBLIC_CONTEXT_SEED_SET_INVALID")

    for seed in seeds:
        require(isinstance(seed, dict), "ARK_PUBLIC_CONTEXT_SEED_INVALID")
        require(seed.get("kind") in ALLOWED_KINDS, "ARK_PUBLIC_CONTEXT_SEED_KIND_INVALID")
        require(seed.get("visibility") == "public", "ARK_PUBLIC_CONTEXT_SEED_VISIBILITY_INVALID")
        require(seed.get("epistemic_class") == "known_public_record", "ARK_PUBLIC_CONTEXT_EPISTEMIC_INVALID")
        require(seed.get("canonical_or_derived") == "explicit_public_source_export",
                "ARK_PUBLIC_CONTEXT_CANONICAL_STATUS_INVALID")
        require(seed.get("source_id") == "source.qsol_substrate", "ARK_PUBLIC_CONTEXT_SOURCE_INVALID")
        repo = seed.get("source_repository")
        require(repo == "https://github.com/QSOLKCB/QSOL-SUBSTRATE", "ARK_PRIVATE_CONTEXT_AUTHORITY_FORBIDDEN")
        require("QSOL-CONTEXT" not in str(repo), "ARK_PRIVATE_CONTEXT_AUTHORITY_FORBIDDEN")
        require(seed.get("source_ref_or_commit") == substrate["commit"],
                "ARK_PUBLIC_CONTEXT_SOURCE_COMMIT_INVALID")
        artifact = seed.get("source_path_or_artifact")
        require(isinstance(artifact, str) and artifact and "#" in artifact,
                "ARK_PUBLIC_CONTEXT_SOURCE_PATH_INVALID")
        source_hash = seed.get("source_hash_when_available")
        require(isinstance(source_hash, dict) and source_hash.get("algorithm") == "git_blob_sha1",
                "ARK_PUBLIC_CONTEXT_SOURCE_HASH_INVALID")
        require(HEX40.fullmatch(str(source_hash.get("value", ""))) is not None,
                "ARK_PUBLIC_CONTEXT_SOURCE_HASH_INVALID")
        require(seed.get("license") == "Apache-2.0 source repository; ARK stores normalized metadata only",
                "ARK_PUBLIC_CONTEXT_LICENSE_INVALID")
        require(seed.get("byte_imported") is False, "ARK_PUBLIC_CONTEXT_BYTE_IMPORT_FORBIDDEN")
        require(isinstance(seed.get("subject_url"), str)
                and seed["subject_url"].startswith("https://github.com/"),
                "ARK_PUBLIC_CONTEXT_SUBJECT_INVALID")
        refs = seed.get("source_refs")
        require(isinstance(refs, list) and refs and all(isinstance(x, str) and x.startswith("src:") for x in refs),
                "ARK_PUBLIC_CONTEXT_SOURCE_REFS_INVALID")
        require(isinstance(seed.get("recovery_role"), str) and seed["recovery_role"],
                "ARK_PUBLIC_CONTEXT_RECOVERY_ROLE_INVALID")

        expected = EXPECTED_BINDINGS[seed["id"]]
        require(seed.get("public_record_id") == expected["public_record_id"],
                "ARK_PUBLIC_CONTEXT_SEED_BINDING_INVALID")
        require(seed.get("source_path_or_artifact") == expected["source_path_or_artifact"],
                "ARK_PUBLIC_CONTEXT_SEED_BINDING_INVALID")
        require(seed.get("source_refs") == expected["source_refs"],
                "ARK_PUBLIC_CONTEXT_SEED_BINDING_INVALID")
        if "release" in expected:
            require(seed.get("release") == expected["release"], "ARK_PUBLIC_CONTEXT_RELEASE_INVALID")
        else:
            require(seed.get("release") is None, "ARK_PUBLIC_CONTEXT_RELEASE_INVALID")
        if "publication" in expected:
            require(seed.get("publication") == expected["publication"], "ARK_PUBLIC_CONTEXT_PUBLICATION_INVALID")
        else:
            require(seed.get("publication") is None, "ARK_PUBLIC_CONTEXT_PUBLICATION_INVALID")

        release = seed.get("release")
        if release is not None:
            require(isinstance(release, dict) and isinstance(release.get("tag"), str),
                    "ARK_PUBLIC_CONTEXT_RELEASE_INVALID")
            require(HEX40.fullmatch(str(release.get("commit", ""))) is not None,
                    "ARK_PUBLIC_CONTEXT_RELEASE_INVALID")
        publication = seed.get("publication")
        if publication is not None:
            require(isinstance(publication, dict), "ARK_PUBLIC_CONTEXT_PUBLICATION_INVALID")
            require(DOI.fullmatch(str(publication.get("doi", ""))) is not None,
                    "ARK_PUBLIC_CONTEXT_PUBLICATION_INVALID")
            require(isinstance(publication.get("version"), str) and publication["version"],
                    "ARK_PUBLIC_CONTEXT_PUBLICATION_INVALID")

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
