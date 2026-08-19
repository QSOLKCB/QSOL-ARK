#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Validate compiler/emulator portability and derived recovery-media contracts."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORTABILITY_PATH = ROOT / "ai" / "archaeology-portability.json"
MEDIA_PATH = ROOT / "ai" / "recovery-media.json"
EMULATOR_PATH = ROOT / "retro" / "emulator" / "qemu-i386.json"
MEDIA_TOOL_PATH = ROOT / "tools" / "recovery_media.py"
VERSION = "1.0.0"

REQUIRED_COMPILER_CLASSES = {
    "baseline",
    "independent-compiler",
    "small-limited-compiler",
    "alternate-libc",
    "reduced-word-size",
}
REQUIRED_PORTABILITY_INVARIANTS = {
    "COMPILER_SUCCESS != HISTORICAL_HARDWARE_EQUIVALENCE",
    "LIBC_VARIANCE != PAYLOAD_VARIANCE",
    "EMULATOR_SUCCESS != ORIGINAL_HARDWARE_EXECUTION",
    "T2_VERIFIER_OUTPUT_MUST_MATCH_CANONICAL_SHA256",
}
REQUIRED_MEDIA_INVARIANTS = {
    "CARRIER != CANONICAL_PAYLOAD",
    "CARRIER_HASH != PAYLOAD_HASH",
    "DECODED_PAYLOAD_MUST_MATCH_CANONICAL_BYTES",
    "QR_RENDERER_VERSION_MUST_NOT_DEFINE_PAYLOAD_IDENTITY",
    "AUDIO_WAV_BYTES_ARE_DERIVED_NOT_AUTHORITY",
    "PRINTABLE_TRANSCRIPTION_REQUIRES_SHA256_VERIFICATION",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(ok: bool, code: str) -> None:
    if not ok:
        raise ValueError(code)


def nonempty(value, code: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), code)
    return value


def repo_file(value, code: str) -> Path:
    text = nonempty(value, code)
    path = Path(text)
    require(not path.is_absolute() and ".." not in path.parts, code)
    full = ROOT / path
    require(full.exists() and full.is_file(), code)
    return full


def argv(value, code: str) -> list[str]:
    require(
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item for item in value),
        code,
    )
    return value


def receipt_hash(receipt: Path, name: str, code: str) -> str:
    for line in receipt.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1] == name:
            digest = parts[0].lower()
            require(len(digest) == 64 and all(c in "0123456789abcdef" for c in digest), code)
            return digest
    raise ValueError(code)


def validate_target_semantics(target: dict, baseline_compiler: str, baseline_libc: str) -> None:
    compiler = target["compiler"]
    libc = target["libc"]
    architecture = target["architecture"]
    klass = target["class"]
    compile_argv = target["compile_argv"]

    require(compile_argv[0] == compiler, "ARK_PORTABILITY_COMPILER_COMMAND_DRIFT")
    if architecture.endswith("-static"):
        require("-static" in compile_argv, "ARK_PORTABILITY_STATIC_BINDING_INVALID")
    if klass == "independent-compiler":
        require(compiler != baseline_compiler, "ARK_PORTABILITY_INDEPENDENT_COMPILER_INVALID")
    elif klass == "small-limited-compiler":
        require(compiler == "tcc", "ARK_PORTABILITY_LIMITED_COMPILER_BINDING_INVALID")
    elif klass == "alternate-libc":
        require(libc != baseline_libc, "ARK_PORTABILITY_ALTERNATE_LIBC_INVALID")
        if libc == "musl":
            require(compiler == "musl-gcc" and "-static" in compile_argv,
                    "ARK_PORTABILITY_MUSL_BINDING_INVALID")
    elif klass == "reduced-word-size":
        require(architecture.startswith("i386") and "-m32" in compile_argv,
                "ARK_PORTABILITY_WORD_SIZE_BINDING_INVALID")


def validate_vectors(vectors: object, canonical_payload: Path, canonical_receipt: Path) -> None:
    require(isinstance(vectors, list) and len(vectors) >= 2, "ARK_PORTABILITY_VECTORS_INVALID")
    ids: list[str] = []
    canary_bound = False
    generated_count = 0
    for vector in vectors:
        require(isinstance(vector, dict), "ARK_PORTABILITY_VECTOR_INVALID")
        vid = nonempty(vector.get("id"), "ARK_PORTABILITY_VECTOR_ID_INVALID")
        ids.append(vid)
        keys = set(vector)
        if keys == {"id", "path", "expected_from"}:
            path = repo_file(vector["path"], "ARK_PORTABILITY_VECTOR_PATH_INVALID")
            receipt = repo_file(vector["expected_from"], "ARK_PORTABILITY_VECTOR_RECEIPT_INVALID")
            expected = receipt_hash(receipt, path.name, "ARK_PORTABILITY_VECTOR_RECEIPT_INVALID")
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            require(actual == expected, "ARK_PORTABILITY_VECTOR_SOURCE_MISMATCH")
            if vid == "ark-canary":
                require(path == canonical_payload and receipt == canonical_receipt,
                        "ARK_PORTABILITY_CANARY_VECTOR_BINDING_INVALID")
                canary_bound = True
        elif keys == {"id", "generated_bytes_utf8", "sha256"}:
            raw_text = nonempty(vector["generated_bytes_utf8"], "ARK_PORTABILITY_VECTOR_BYTES_INVALID")
            digest = nonempty(vector["sha256"], "ARK_PORTABILITY_VECTOR_DIGEST_INVALID").lower()
            require(len(digest) == 64 and all(c in "0123456789abcdef" for c in digest),
                    "ARK_PORTABILITY_VECTOR_DIGEST_INVALID")
            actual = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
            require(actual == digest, "ARK_PORTABILITY_VECTOR_DECLARATION_MISMATCH")
            generated_count += 1
        else:
            raise ValueError("ARK_PORTABILITY_VECTOR_SHAPE_INVALID")
    require(len(ids) == len(set(ids)), "ARK_PORTABILITY_VECTOR_ID_DUPLICATE")
    require(canary_bound, "ARK_PORTABILITY_CANARY_VECTOR_MISSING")
    require(generated_count >= 1, "ARK_PORTABILITY_GENERATED_VECTOR_MISSING")


def validate_portability(doc: dict) -> None:
    require(doc.get("type") == "qsol-ark-archaeology-portability", "ARK_PORTABILITY_CONTRACT_INVALID")
    require(doc.get("protocol") == "QSOL-ARK" and doc.get("schema_version") == VERSION,
            "ARK_PORTABILITY_CONTRACT_INVALID")
    verifier = repo_file(doc.get("canonical_verifier"), "ARK_PORTABILITY_VERIFIER_MISSING")
    payload = repo_file(doc.get("canonical_payload"), "ARK_PORTABILITY_PAYLOAD_MISSING")
    receipt = repo_file(doc.get("canonical_receipt"), "ARK_PORTABILITY_RECEIPT_MISSING")
    require(verifier.suffix == ".c", "ARK_PORTABILITY_VERIFIER_TYPE_INVALID")

    targets = doc.get("compiler_targets")
    require(isinstance(targets, list) and targets, "ARK_PORTABILITY_TARGETS_INVALID")
    ids = []
    classes = set()
    baseline = [t for t in targets if isinstance(t, dict) and t.get("class") == "baseline"]
    require(len(baseline) == 1, "ARK_PORTABILITY_BASELINE_INVALID")
    baseline_compiler = nonempty(baseline[0].get("compiler"), "ARK_PORTABILITY_COMPILER_INVALID")
    baseline_libc = nonempty(baseline[0].get("libc"), "ARK_PORTABILITY_LIBC_INVALID")

    for target in targets:
        require(isinstance(target, dict), "ARK_PORTABILITY_TARGET_INVALID")
        tid = nonempty(target.get("id"), "ARK_PORTABILITY_TARGET_ID_INVALID")
        ids.append(tid)
        klass = nonempty(target.get("class"), "ARK_PORTABILITY_TARGET_CLASS_INVALID")
        classes.add(klass)
        nonempty(target.get("compiler"), "ARK_PORTABILITY_COMPILER_INVALID")
        nonempty(target.get("libc"), "ARK_PORTABILITY_LIBC_INVALID")
        nonempty(target.get("architecture"), "ARK_PORTABILITY_ARCH_INVALID")
        require(target.get("ci_required") is True, "ARK_PORTABILITY_TARGET_NOT_CI_REQUIRED")
        compile_argv = argv(target.get("compile_argv"), "ARK_PORTABILITY_COMPILE_ARGV_INVALID")
        run_argv = argv(target.get("run_argv"), "ARK_PORTABILITY_RUN_ARGV_INVALID")
        require("{source}" in compile_argv and "{output}" in compile_argv,
                "ARK_PORTABILITY_COMPILE_BINDING_INVALID")
        require("{output}" in run_argv, "ARK_PORTABILITY_RUN_BINDING_INVALID")
        validate_target_semantics(target, baseline_compiler, baseline_libc)
    require(len(ids) == len(set(ids)), "ARK_PORTABILITY_TARGET_ID_DUPLICATE")
    require(REQUIRED_COMPILER_CLASSES.issubset(classes), "ARK_PORTABILITY_TARGET_CLASS_MISSING")

    emulator = doc.get("emulator_target")
    require(isinstance(emulator, dict), "ARK_EMULATOR_TARGET_INVALID")
    require(emulator.get("id") == "qemu-i386-pentium3", "ARK_EMULATOR_TARGET_INVALID")
    require(emulator.get("binary_target") in set(ids), "ARK_EMULATOR_BINARY_TARGET_UNKNOWN")
    require(emulator.get("execution_class") == "constrained_cpu_emulation",
            "ARK_EMULATOR_EXECUTION_CLASS_INVALID")
    require(emulator.get("historical_recovery_equivalence") == "functional_equivalence_only",
            "ARK_EMULATOR_EQUIVALENCE_PROMOTED")
    require(emulator.get("ci_required") is True, "ARK_EMULATOR_NOT_CI_REQUIRED")
    repo_file(emulator.get("contract"), "ARK_EMULATOR_CONTRACT_MISSING")
    run_argv = argv(emulator.get("run_argv"), "ARK_EMULATOR_RUN_ARGV_INVALID")
    require(run_argv[:3] == ["qemu-i386", "-cpu", "pentium3"] and "{output}" in run_argv,
            "ARK_EMULATOR_RUN_BINDING_INVALID")
    require(isinstance(emulator.get("timeout_seconds"), int) and 0 < emulator["timeout_seconds"] <= 30,
            "ARK_EMULATOR_TIMEOUT_INVALID")
    require(isinstance(emulator.get("file_size_limit_blocks"), int)
            and emulator["file_size_limit_blocks"] > 0,
            "ARK_EMULATOR_FILE_LIMIT_INVALID")
    require(emulator.get("clean_environment") is True, "ARK_EMULATOR_ENVIRONMENT_NOT_CONSTRAINED")

    validate_vectors(doc.get("required_vectors"), payload, receipt)

    require(REQUIRED_PORTABILITY_INVARIANTS.issubset(set(doc.get("invariants", []))),
            "ARK_PORTABILITY_INVARIANTS_INCOMPLETE")


def validate_emulator(doc: dict, portability: dict) -> None:
    require(doc.get("type") == "qsol-ark-constrained-emulator-target", "ARK_EMULATOR_CONTRACT_INVALID")
    require(doc.get("protocol") == "QSOL-ARK" and doc.get("schema_version") == VERSION,
            "ARK_EMULATOR_CONTRACT_INVALID")
    require(doc.get("id") == portability["emulator_target"]["id"], "ARK_EMULATOR_ID_DRIFT")
    require(doc.get("emulator") == "qemu-i386", "ARK_EMULATOR_ENGINE_INVALID")
    require(doc.get("mode") == "linux_user_mode_cpu_emulation", "ARK_EMULATOR_MODE_INVALID")
    require(doc.get("guest_architecture") == "i386" and doc.get("cpu_model") == "pentium3",
            "ARK_EMULATOR_GUEST_INVALID")
    binary = doc.get("binary", {})
    require(binary.get("source") == portability["canonical_verifier"], "ARK_EMULATOR_SOURCE_DRIFT")
    require(binary.get("libc") == "glibc" and binary.get("dynamic_host_libraries") is False,
            "ARK_EMULATOR_BINARY_BOUNDARY_INVALID")
    runtime = doc.get("runtime_constraints", {})
    emu = portability["emulator_target"]
    require(runtime.get("clean_environment") is True, "ARK_EMULATOR_RUNTIME_INVALID")
    require(runtime.get("wall_clock_timeout_seconds") == emu["timeout_seconds"],
            "ARK_EMULATOR_TIMEOUT_DRIFT")
    require(runtime.get("file_size_limit_blocks") == emu["file_size_limit_blocks"],
            "ARK_EMULATOR_LIMIT_DRIFT")
    require(runtime.get("network_required") is False, "ARK_EMULATOR_NETWORK_DEPENDENCY_INVALID")
    require(doc.get("recovery_equivalence") == "functional_equivalence_only",
            "ARK_EMULATOR_EQUIVALENCE_PROMOTED")
    boundaries = set(doc.get("boundaries", []))
    require({
        "USER_MODE_CPU_EMULATION != FULL_SYSTEM_EMULATION",
        "EMULATED_I386 != HISTORICAL_PC",
        "PASSING_SHA256_VECTOR != PROOF_OF_HISTORICAL_EXECUTION",
    }.issubset(boundaries), "ARK_EMULATOR_BOUNDARIES_INCOMPLETE")


def load_media_tool():
    spec = importlib.util.spec_from_file_location("recovery_media", MEDIA_TOOL_PATH)
    require(spec is not None and spec.loader is not None, "ARK_MEDIA_TOOL_LOAD_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_media(doc: dict) -> None:
    require(doc.get("type") == "qsol-ark-recovery-media-contract", "ARK_MEDIA_CONTRACT_INVALID")
    require(doc.get("protocol") == "QSOL-ARK" and doc.get("schema_version") == VERSION,
            "ARK_MEDIA_CONTRACT_INVALID")
    require(doc.get("status") == "derived_recovery_carrier_experiment",
            "ARK_MEDIA_CANONICALITY_INVALID")
    payload = repo_file(doc.get("canonical_payload"), "ARK_MEDIA_CANONICAL_PAYLOAD_MISSING")
    receipt = repo_file(doc.get("canonical_receipt"), "ARK_MEDIA_CANONICAL_RECEIPT_MISSING")
    require(doc.get("envelope_protocol") == "QSOL-ARK-CARRIER/1", "ARK_MEDIA_PROTOCOL_INVALID")
    require(doc.get("tool") == "tools/recovery_media.py", "ARK_MEDIA_TOOL_BINDING_INVALID")
    repo_file(doc.get("tool"), "ARK_MEDIA_TOOL_MISSING")

    carriers = doc.get("carriers")
    require(isinstance(carriers, dict) and set(carriers) == {"printable", "qr", "audio"},
            "ARK_MEDIA_CARRIERS_INVALID")
    for carrier in carriers.values():
        require(carrier.get("canonical_carrier_bytes") is False,
                "ARK_MEDIA_CARRIER_PROMOTED_TO_CANONICAL")
        require(carrier.get("round_trip_required") is True,
                "ARK_MEDIA_ROUNDTRIP_NOT_REQUIRED")
    require(carriers["qr"].get("binary_artifact_committed") is False,
            "ARK_MEDIA_QR_BINARY_PROMOTED")
    require(carriers["audio"].get("binary_artifact_committed") is False,
            "ARK_MEDIA_AUDIO_BINARY_PROMOTED")

    tool = load_media_tool()
    require(tool.CONTRACT_PATH == MEDIA_PATH, "ARK_MEDIA_TOOL_CONTRACT_PATH_DRIFT")
    require(tool.CANARY == payload, "ARK_MEDIA_TOOL_PAYLOAD_PATH_DRIFT")
    require(tool.RECEIPT == receipt, "ARK_MEDIA_TOOL_RECEIPT_PATH_DRIFT")
    audio = carriers["audio"]
    require(
        (audio.get("sample_rate"), audio.get("samples_per_bit"), audio.get("zero_hz"), audio.get("one_hz"))
        == (tool.SAMPLE_RATE, tool.SAMPLES_PER_BIT, tool.ZERO_HZ, tool.ONE_HZ),
        "ARK_MEDIA_AUDIO_PARAMETERS_DRIFT",
    )
    require(tool.PROTOCOL == doc["envelope_protocol"], "ARK_MEDIA_ENVELOPE_PROTOCOL_DRIFT")
    printable_path = repo_file(carriers["printable"].get("committed_example"),
                               "ARK_MEDIA_PRINTABLE_PATH_INVALID")
    expected = tool.canonical_envelope()
    require(printable_path.read_bytes() == expected, "ARK_MEDIA_PRINTABLE_DRIFT")
    tool.verify_against_canonical(expected)

    require(REQUIRED_MEDIA_INVARIANTS.issubset(set(doc.get("invariants", []))),
            "ARK_MEDIA_INVARIANTS_INCOMPLETE")


def validate() -> None:
    portability = load(PORTABILITY_PATH)
    media = load(MEDIA_PATH)
    emulator = load(EMULATOR_PATH)
    validate_portability(portability)
    validate_emulator(emulator, portability)
    validate_media(media)
    print(
        "ARK_PORTABILITY_CONTRACTS_OK "
        f"compiler_targets={len(portability['compiler_targets'])} "
        f"carriers={len(media['carriers'])}"
    )


def main(argv: list[str]) -> int:
    try:
        validate()
    except (ValueError, KeyError, TypeError, json.JSONDecodeError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
