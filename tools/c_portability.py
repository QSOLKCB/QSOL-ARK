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
CANARY = ROOT / "capsules" / "minimal" / "ARK-CANARY.txt"
RECEIPT = ROOT / "capsules" / "minimal" / "SHA256SUMS"


def load_contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def receipt_hash(name: str) -> str:
    for line in RECEIPT.read_text(encoding="utf-8").splitlines():
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


def compile_target(target: dict, work: Path) -> Path:
    output = work / target["id"]
    argv = expand(target["compile_argv"], ROOT / "retro" / "c" / "ark-verify.c", output)
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


def verify_binary(prefix: list[str], work: Path, *, timeout: int | None = None,
                  clean_env: bool = False, file_size_limit_blocks: int | None = None) -> None:
    require_tools(prefix)
    expected = receipt_hash(CANARY.name)
    actual = hashlib.sha256(CANARY.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError("ARK_PORTABILITY_CANONICAL_HASH_MISMATCH")
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin")} if clean_env else None
    run_vector(prefix, CANARY, expected, timeout=timeout, env=env,
               file_size_limit_blocks=file_size_limit_blocks)
    abc = work / "abc"
    abc.write_bytes(b"abc")
    run_vector(
        prefix,
        abc,
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        timeout=timeout,
        env=env,
        file_size_limit_blocks=file_size_limit_blocks,
    )


def run_compiler_target(target: dict, work: Path) -> Path:
    binary = compile_target(target, work)
    prefix = expand(target["run_argv"], ROOT / "retro" / "c" / "ark-verify.c", binary)
    verify_binary(prefix, work)
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
    binary = compile_target(targets[target_id], work)
    emulator = contract["emulator_target"]
    prefix = expand(emulator["run_argv"], ROOT / "retro" / "c" / "ark-verify.c", binary)
    verify_binary(
        prefix,
        work,
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
                        run_compiler_target(target, work)
            elif args.target == "emulator":
                run_emulator(contract, work)
            elif args.target in targets:
                run_compiler_target(targets[args.target], work)
            else:
                print(f"unknown target: {args.target}", file=sys.stderr)
                return 2
        return 0
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
