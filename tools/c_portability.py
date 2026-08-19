#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compile and execute the T2 verifier across declared portability targets."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "ai" / "archaeology-portability.json"


def load_contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def repo_file(value: object) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError("ARK_PORTABILITY_PATH_INVALID")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("ARK_PORTABILITY_PATH_INVALID")
    full = ROOT / path
    if not full.is_file():
        raise ValueError(f"ARK_PORTABILITY_PATH_MISSING:{value}")
    return full


def resolve_contract_paths(contract: dict) -> tuple[Path, Path, Path]:
    return (
        repo_file(contract.get("canonical_verifier")),
        repo_file(contract.get("canonical_payload")),
        repo_file(contract.get("canonical_receipt")),
    )


def receipt_hash(receipt: Path, name: str) -> str:
    for line in receipt.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1] == name:
            return parts[0].lower()
    raise ValueError(f"ARK_PORTABILITY_RECEIPT_MISSING:{name}")


def expand(argv: list[str], source: Path, output: Path) -> list[str]:
    mapping = {"{source}": str(source), "{output}": str(output)}
    return [mapping.get(item, item) for item in argv]


def require_tools(argv: list[str]) -> None:
    exe = argv[0]
    if shutil.which(exe) is None:
        raise ValueError(f"ARK_PORTABILITY_TOOL_UNAVAILABLE:{exe}")


def run_vector(prefix: list[str], path: Path, expected: str, *, timeout: int | None = None,
               env=None, file_size_limit_blocks: int | None = None) -> None:
    cmd = [*prefix, str(path), expected]
    preexec_fn = None
    if file_size_limit_blocks is not None:
        import resource
        limit_bytes = int(file_size_limit_blocks) * 512

        def _limit() -> None:
            resource.setrlimit(resource.RLIMIT_FSIZE, (limit_bytes, limit_bytes))

        preexec_fn = _limit
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        env=env,
        preexec_fn=preexec_fn,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        check=False,
    )
    if result.returncode != 0 or "ARK_HASH_OK" not in result.stdout:
        raise ValueError(
            "ARK_PORTABILITY_VECTOR_FAILED:"
            + " ".join(cmd)
            + f":rc={result.returncode}:stdout={result.stdout!r}:stderr={result.stderr!r}"
        )


def compile_target(target: dict, work: Path, contract: dict) -> Path:
    source, _, _ = resolve_contract_paths(contract)
    output = work / target["id"]
    argv = expand(target["compile_argv"], source, output)
    require_tools(argv)
    result = subprocess.run(
        argv,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(
            f"ARK_PORTABILITY_COMPILE_FAILED:{target['id']}:"
            f"stdout={result.stdout!r}:stderr={result.stderr!r}"
        )
    if not output.is_file():
        raise ValueError(f"ARK_PORTABILITY_OUTPUT_MISSING:{target['id']}")
    return output


def materialize_vectors(contract: dict, work: Path) -> list[tuple[Path, str]]:
    _, canonical_payload, canonical_receipt = resolve_contract_paths(contract)
    materialized: list[tuple[Path, str]] = []
    for index, vector in enumerate(contract["required_vectors"]):
        if "path" in vector:
            path = repo_file(vector["path"])
            receipt = repo_file(vector["expected_from"])
            expected = receipt_hash(receipt, path.name)
        else:
            raw = vector["generated_bytes_utf8"].encode("utf-8")
            expected = vector["sha256"].lower()
            actual = hashlib.sha256(raw).hexdigest()
            if actual != expected:
                raise ValueError(f"ARK_PORTABILITY_VECTOR_DECLARATION_MISMATCH:{vector['id']}")
            path = work / f"vector-{index}"
            path.write_bytes(raw)
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"ARK_PORTABILITY_VECTOR_SOURCE_MISMATCH:{vector['id']}")
        materialized.append((path, expected))

    canary_expected = receipt_hash(canonical_receipt, canonical_payload.name)
    if hashlib.sha256(canonical_payload.read_bytes()).hexdigest() != canary_expected:
        raise ValueError("ARK_PORTABILITY_CANONICAL_HASH_MISMATCH")
    return materialized


def verify_binary(prefix: list[str], work: Path, contract: dict, *, timeout: int | None = None,
                  clean_env: bool = False, file_size_limit_blocks: int | None = None) -> None:
    require_tools(prefix)
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin")} if clean_env else None
    for path, expected in materialize_vectors(contract, work):
        run_vector(
            prefix,
            path,
            expected,
            timeout=timeout,
            env=env,
            file_size_limit_blocks=file_size_limit_blocks,
        )


def run_compiler_target(target: dict, work: Path, contract: dict) -> Path:
    binary = compile_target(target, work, contract)
    source, _, _ = resolve_contract_paths(contract)
    prefix = expand(target["run_argv"], source, binary)
    verify_binary(prefix, work, contract)
    print(
        f"ARK_PORTABILITY_OK target={target['id']} compiler={target['compiler']} "
        f"libc={target['libc']} arch={target['architecture']}"
    )
    return binary


def run_emulator(contract: dict, work: Path) -> None:
    target_id = contract["emulator_target"]["binary_target"]
    targets = {target["id"]: target for target in contract["compiler_targets"]}
    if target_id not in targets:
        raise ValueError("ARK_PORTABILITY_EMULATOR_BINARY_TARGET_UNKNOWN")
    binary = compile_target(targets[target_id], work, contract)
    emulator = contract["emulator_target"]
    source, _, _ = resolve_contract_paths(contract)
    prefix = expand(emulator["run_argv"], source, binary)
    verify_binary(
        prefix,
        work,
        contract,
        timeout=int(emulator["timeout_seconds"]),
        clean_env=bool(emulator["clean_environment"]),
        file_size_limit_blocks=int(emulator["file_size_limit_blocks"]),
    )
    print(
        f"ARK_EMULATOR_OK target={emulator['id']} "
        f"equivalence={emulator['historical_recovery_equivalence']}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="target id, all, or emulator")
    args = parser.parse_args(argv)
    contract = load_contract()
    targets = {target["id"]: target for target in contract["compiler_targets"]}
    try:
        with tempfile.TemporaryDirectory(prefix="ark-portability-") as tmp:
            work = Path(tmp)
            if args.target == "all":
                for target in contract["compiler_targets"]:
                    if target.get("ci_required"):
                        run_compiler_target(target, work, contract)
            elif args.target == "emulator":
                run_emulator(contract, work)
            elif args.target in targets:
                run_compiler_target(targets[args.target], work, contract)
            else:
                print(f"unknown target: {args.target}", file=sys.stderr)
                return 2
        return 0
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
