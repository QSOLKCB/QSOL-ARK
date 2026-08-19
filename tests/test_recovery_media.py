# SPDX-License-Identifier: Apache-2.0
import importlib.util
import tempfile
import unittest
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "recovery_media", ROOT / "tools" / "recovery_media.py"
)
rm = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(rm)


class RecoveryMediaTests(unittest.TestCase):
    def test_canonical_envelope_round_trip(self):
        envelope = rm.canonical_envelope()
        rm.verify_against_canonical(envelope)
        name, payload, digest = rm.parse_envelope(envelope)
        self.assertEqual(name, rm.CANARY.name)
        self.assertEqual(payload, rm.CANARY.read_bytes())
        self.assertEqual(digest, rm.receipt_hash(rm.CANARY.name))

    def test_printable_card_is_exact_envelope(self):
        card = ROOT / "recovery" / "printable" / "ARK-CANARY-CARD.txt"
        self.assertEqual(card.read_bytes(), rm.canonical_envelope())

    def test_audio_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "carrier.wav"
            envelope = rm.canonical_envelope()
            rm.encode_audio(envelope, path)
            decoded = rm.decode_audio(path)
            self.assertEqual(decoded, envelope)
            rm.verify_against_canonical(decoded)

    def test_audio_format_is_explicit_pcm(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "carrier.wav"
            rm.encode_audio(rm.canonical_envelope(), path)
            with wave.open(str(path), "rb") as wav:
                self.assertEqual(wav.getnchannels(), 1)
                self.assertEqual(wav.getsampwidth(), 2)
                self.assertEqual(wav.getframerate(), 8000)

    def test_tampered_payload_fails_closed(self):
        envelope = bytearray(rm.canonical_envelope())
        index = envelope.index(b"payload-base64=") + len(b"payload-base64=")
        envelope[index] = ord("A") if envelope[index] != ord("A") else ord("B")
        with self.assertRaises(ValueError):
            rm.verify_against_canonical(bytes(envelope))

    def test_carrier_protocol_is_not_payload_identity(self):
        envelope = rm.canonical_envelope()
        altered = envelope.replace(b"QSOL-ARK-CARRIER/1", b"QSOL-ARK-CARRIER/2", 1)
        with self.assertRaisesRegex(ValueError, "ARK_MEDIA_ENVELOPE_SHAPE_INVALID"):
            rm.parse_envelope(altered)


if __name__ == "__main__":
    unittest.main()
