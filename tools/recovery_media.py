#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Build and verify derived printable, QR-source, and audio recovery carriers."""
from __future__ import annotations

import argparse
import base64
import hashlib
import math
import struct
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANARY = ROOT / "capsules" / "minimal" / "ARK-CANARY.txt"
RECEIPT = ROOT / "capsules" / "minimal" / "SHA256SUMS"
CONTRACT = ROOT / "ai" / "recovery-media.json"
PROTOCOL = "QSOL-ARK-CARRIER/1"
AUDIO_MAGIC = b"ARKA"
SAMPLE_RATE = 8000
SAMPLES_PER_BIT = 40
ZERO_HZ = 800
ONE_HZ = 1600
AMPLITUDE = 12000


def receipt_hash(name: str) -> str:
    for line in RECEIPT.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1] == name:
            return parts[0].lower()
    raise ValueError(f"ARK_MEDIA_RECEIPT_MISSING:{name}")


def build_envelope(payload: bytes, name: str, expected_hash: str) -> bytes:
    actual = hashlib.sha256(payload).hexdigest()
    if actual != expected_hash.lower():
        raise ValueError(
            f"ARK_MEDIA_PAYLOAD_HASH_MISMATCH expected={expected_hash} actual={actual}"
        )
    encoded = base64.b64encode(payload).decode("ascii")
    text = (
        f"{PROTOCOL}\n"
        f"payload-name={name}\n"
        f"payload-length={len(payload)}\n"
        f"payload-sha256={actual}\n"
        f"payload-base64={encoded}\n"
    )
    return text.encode("ascii")


def parse_envelope(envelope: bytes) -> tuple[str, bytes, str]:
    try:
        text = envelope.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("ARK_MEDIA_ENVELOPE_NOT_ASCII") from exc
    lines = text.splitlines()
    if len(lines) != 5 or lines[0] != PROTOCOL:
        raise ValueError("ARK_MEDIA_ENVELOPE_SHAPE_INVALID")
    fields = {}
    for line in lines[1:]:
        if "=" not in line:
            raise ValueError("ARK_MEDIA_ENVELOPE_SHAPE_INVALID")
        key, value = line.split("=", 1)
        if key in fields:
            raise ValueError("ARK_MEDIA_ENVELOPE_DUPLICATE_FIELD")
        fields[key] = value
    if set(fields) != {
        "payload-name",
        "payload-length",
        "payload-sha256",
        "payload-base64",
    }:
        raise ValueError("ARK_MEDIA_ENVELOPE_FIELDS_INVALID")
    name = fields["payload-name"]
    if not name or "/" in name or "\\" in name or name in {".", ".."}:
        raise ValueError("ARK_MEDIA_PAYLOAD_NAME_INVALID")
    try:
        declared_length = int(fields["payload-length"], 10)
    except ValueError as exc:
        raise ValueError("ARK_MEDIA_PAYLOAD_LENGTH_INVALID") from exc
    digest = fields["payload-sha256"].lower()
    if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
        raise ValueError("ARK_MEDIA_PAYLOAD_DIGEST_INVALID")
    try:
        payload = base64.b64decode(fields["payload-base64"], validate=True)
    except Exception as exc:
        raise ValueError("ARK_MEDIA_PAYLOAD_BASE64_INVALID") from exc
    if len(payload) != declared_length:
        raise ValueError("ARK_MEDIA_PAYLOAD_LENGTH_MISMATCH")
    actual = hashlib.sha256(payload).hexdigest()
    if actual != digest:
        raise ValueError("ARK_MEDIA_PAYLOAD_DIGEST_MISMATCH")
    return name, payload, digest


def verify_against_canonical(envelope: bytes) -> None:
    name, payload, digest = parse_envelope(envelope)
    canonical = CANARY.read_bytes()
    expected = receipt_hash(CANARY.name)
    if name != CANARY.name:
        raise ValueError("ARK_MEDIA_CANONICAL_NAME_MISMATCH")
    if digest != expected or hashlib.sha256(canonical).hexdigest() != expected:
        raise ValueError("ARK_MEDIA_CANONICAL_RECEIPT_MISMATCH")
    if payload != canonical:
        raise ValueError("ARK_MEDIA_CANONICAL_BYTES_MISMATCH")


def bytes_to_bits(data: bytes):
    for byte in data:
        for shift in range(7, -1, -1):
            yield (byte >> shift) & 1


def bits_to_bytes(bits: list[int]) -> bytes:
    if len(bits) % 8:
        raise ValueError("ARK_MEDIA_AUDIO_BIT_LENGTH_INVALID")
    out = bytearray()
    for i in range(0, len(bits), 8):
        value = 0
        for bit in bits[i:i + 8]:
            value = (value << 1) | bit
        out.append(value)
    return bytes(out)


def encode_audio(envelope: bytes, output: Path) -> None:
    framed = AUDIO_MAGIC + struct.pack(">I", len(envelope)) + envelope
    frames = bytearray()
    for bit in bytes_to_bits(framed):
        freq = ONE_HZ if bit else ZERO_HZ
        for n in range(SAMPLES_PER_BIT):
            sample = int(round(AMPLITUDE * math.sin(2.0 * math.pi * freq * n / SAMPLE_RATE)))
            frames.extend(struct.pack("<h", sample))
    with wave.open(str(output), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(bytes(frames))


def _tone_energy(samples: tuple[int, ...], freq: int) -> float:
    sin_sum = 0.0
    cos_sum = 0.0
    for n, sample in enumerate(samples):
        angle = 2.0 * math.pi * freq * n / SAMPLE_RATE
        sin_sum += sample * math.sin(angle)
        cos_sum += sample * math.cos(angle)
    return sin_sum * sin_sum + cos_sum * cos_sum


def decode_audio(path: Path) -> bytes:
    with wave.open(str(path), "rb") as wav:
        if (
            wav.getnchannels() != 1
            or wav.getsampwidth() != 2
            or wav.getframerate() != SAMPLE_RATE
        ):
            raise ValueError("ARK_MEDIA_AUDIO_FORMAT_INVALID")
        raw = wav.readframes(wav.getnframes())
    if len(raw) % (2 * SAMPLES_PER_BIT):
        raise ValueError("ARK_MEDIA_AUDIO_FRAME_LENGTH_INVALID")
    samples = struct.unpack("<" + "h" * (len(raw) // 2), raw)
    bits = []
    for start in range(0, len(samples), SAMPLES_PER_BIT):
        chunk = samples[start:start + SAMPLES_PER_BIT]
        e0 = _tone_energy(chunk, ZERO_HZ)
        e1 = _tone_energy(chunk, ONE_HZ)
        if e0 == e1:
            raise ValueError("ARK_MEDIA_AUDIO_AMBIGUOUS_BIT")
        bits.append(1 if e1 > e0 else 0)
    framed = bits_to_bytes(bits)
    if len(framed) < 8 or framed[:4] != AUDIO_MAGIC:
        raise ValueError("ARK_MEDIA_AUDIO_MAGIC_INVALID")
    size = struct.unpack(">I", framed[4:8])[0]
    if len(framed) != 8 + size:
        raise ValueError("ARK_MEDIA_AUDIO_PAYLOAD_LENGTH_INVALID")
    return framed[8:]


def canonical_envelope() -> bytes:
    payload = CANARY.read_bytes()
    return build_envelope(payload, CANARY.name, receipt_hash(CANARY.name))


def build_outputs(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    envelope = canonical_envelope()
    (out_dir / "ARK-CANARY-CARRIER.txt").write_bytes(envelope)
    (out_dir / "ARK-CANARY-QR-PAYLOAD.txt").write_bytes(envelope)
    encode_audio(envelope, out_dir / "ARK-CANARY-AUDIO.wav")
    verify_against_canonical(envelope)
    verify_against_canonical(decode_audio(out_dir / "ARK-CANARY-AUDIO.wav"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("envelope")
    verify = sub.add_parser("verify-envelope")
    verify.add_argument("path")
    audio = sub.add_parser("decode-audio")
    audio.add_argument("path")
    build = sub.add_parser("build")
    build.add_argument("out_dir")
    args = parser.parse_args(argv)

    try:
        if args.command == "envelope":
            sys.stdout.buffer.write(canonical_envelope())
        elif args.command == "verify-envelope":
            verify_against_canonical(Path(args.path).read_bytes())
            print("ARK_MEDIA_ENVELOPE_OK")
        elif args.command == "decode-audio":
            envelope = decode_audio(Path(args.path))
            verify_against_canonical(envelope)
            sys.stdout.buffer.write(envelope)
        elif args.command == "build":
            build_outputs(Path(args.out_dir))
            print("ARK_MEDIA_BUILD_OK")
        return 0
    except (OSError, ValueError, wave.Error) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
