# SPDX-License-Identifier: Apache-2.0
import importlib.util, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S = importlib.util.spec_from_file_location("systems", ROOT/"tools/systems.py")
m = importlib.util.module_from_spec(S); S.loader.exec_module(m)

class Tests(unittest.TestCase):
    def test_full(self): m.validate()
    def test_rom_injection(self):
        p=m.load("systems/profiles/c64.json"); p["rom_bytes"]="x"
        with self.assertRaisesRegex(ValueError,"ARK_SYSTEM_FORBIDDEN_BYTES"): m.validate_profile(p)
    def test_emulator_not_history(self):
        p=m.load("systems/profiles/amiga500.json"); p["emulator_or_reimplementation"]["used_for_canonical_profile"]=True
        with self.assertRaisesRegex(ValueError,"ARK_EMULATOR_PROMOTED_TO_HISTORY"): m.validate_profile(p)
    def test_exact_not_claimed(self):
        p=m.load("systems/profiles/pc_xt.json"); p["recovery_equivalence"]["exact_reproduction_claimed"]=True
        with self.assertRaisesRegex(ValueError,"ARK_SYSTEM_EXACT_REPRODUCTION_UNSUPPORTED"): m.validate_profile(p)
    def test_cpm_not_one_machine(self):
        p=m.load("systems/profiles/cpm.json"); p["scope_notes"]["hardware_variability"]=False
        with self.assertRaisesRegex(ValueError,"ARK_SOFTWARE_ENVIRONMENT_CANONICAL_MACHINE_FORBIDDEN"): m.validate_profile(p)
    def test_unix_not_one_machine(self):
        p=m.load("systems/profiles/unix.json"); p["scope_notes"]["canonical_machine"]="PDP-11/70"
        with self.assertRaisesRegex(ValueError,"ARK_SOFTWARE_ENVIRONMENT_CANONICAL_MACHINE_FORBIDDEN"): m.validate_profile(p)
    def test_tier_not_native(self):
        p=m.load("systems/profiles/c64.json"); p["computational_archaeology_mapping"]["native_execution_claimed"]=True
        with self.assertRaisesRegex(ValueError,"ARK_SYSTEM_NATIVE_EXECUTION_FALSE_CLAIM"): m.validate_profile(p)
    def test_evidence_partition_exact(self):
        p=m.load("systems/profiles/c64.json"); p["claim_partitions"]["historical_vibes"]=[]
        with self.assertRaisesRegex(ValueError,"ARK_SYSTEM_EVIDENCE_PARTITION_INVALID"): m.validate_profile(p)
    def test_source_required(self):
        p=m.load("systems/profiles/c64.json"); p["source_evidence"][0]["url"]="nope"
        with self.assertRaisesRegex(ValueError,"ARK_SYSTEM_SOURCE_INVALID"): m.validate_profile(p)
    def test_task_boundaries(self):
        t=m.load("systems/tasks/minimum-reconstruction-probe.json"); t["global_boundaries"]["exact_reproduction_claimed"]=True
        with self.assertRaisesRegex(ValueError,"ARK_SYSTEM_TASK_INVALID"): m.validate_task(t,set(m.PROFILE_IDS))

if __name__=="__main__": unittest.main()
