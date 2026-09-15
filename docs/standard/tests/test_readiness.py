import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "readiness", Path(__file__).resolve().parents[1] / "readiness.py"
)
readiness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(readiness)


class Readiness(unittest.TestCase):
    def receipt(self, **changes):
        evidence = {key: [] for key in readiness.PHASES}
        evidence["configured"] = ["receipt://configured/1"]
        value = readiness.build_receipt(
            repository="semcod/example", standard="wellmanifest/docs", standard_version="0.6.0",
            standard_revision="a" * 40, policy_sha256="b" * 64, checker_sha256="c" * 64,
            covered_roots=["workspace/semcod"], base_sha="d" * 40, head_sha="e" * 40,
            phase="configured", observed_at="2026-09-15T12:00:00Z", evidence=evidence,
            generator_id="docs-readiness", generator_version="1.0.0")
        value.update(changes)
        return value

    def test_valid_receipt_has_exact_coverage_and_phase_evidence(self):
        receipt = self.receipt()
        self.assertEqual(readiness.validate_receipt(receipt), [])
        self.assertEqual(set(receipt["evidence"]), set(readiness.PHASES))

    def test_generator_is_idempotent_for_same_inputs(self):
        first = self.receipt()
        second = self.receipt()
        self.assertEqual(first, second)
        command = [sys.executable, str(Path(readiness.__file__)), "generate",
                   "--repository", "semcod/example", "--standard", "wellmanifest/docs",
                   "--standard-version", "0.6.0", "--standard-revision", "a" * 40,
                   "--policy-sha256", "b" * 64, "--checker-sha256", "c" * 64,
                   "--covered-root", "workspace", "--base-sha", "d" * 40, "--head-sha", "e" * 40,
                   "--phase", "configured", "--observed-at", "2026-09-15T12:00:00Z",
                   "--generator-id", "docs-readiness", "--generator-version", "1.0.0",
                   "--evidence", "configured=receipt://configured/1"]
        result = subprocess.run(command, check=False, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {**first, "covered_roots": ["workspace"]})

    def test_missing_phase_or_future_evidence_fails_ci_canary(self):
        receipt = self.receipt()
        del receipt["evidence"]["verified"]
        self.assertIn("DOCS_READINESS_EVIDENCE", {item["code"] for item in readiness.validate_receipt(receipt)})
        receipt = self.receipt()
        receipt["evidence"]["deployed"] = ["receipt://deployed/1"]
        self.assertIn("DOCS_READINESS_EVIDENCE", {item["code"] for item in readiness.validate_receipt(receipt)})

    def test_unsafe_or_duplicate_roots_fail(self):
        for roots in [["/absolute"], ["one/../two"], ["one", "one"]]:
            receipt = self.receipt(covered_roots=roots)
            self.assertIn("DOCS_READINESS_ROOTS", {item["code"] for item in readiness.validate_receipt(receipt)})

    def test_hostile_nested_values_fail_closed_without_type_errors(self):
        for field, value in [
            ("covered_roots", [{"path": "workspace"}]),
            ("evidence", {key: ([{"ref": "receipt://x"}] if key == "configured" else []) for key in readiness.PHASES}),
            ("compatibility_review", {"required": False, "status": "not-required", "reviewer": None, "evidence": [{"ref": "receipt://x"}]}),
        ]:
            receipt = self.receipt(**{field: value})
            findings = readiness.validate_receipt(receipt)
            self.assertTrue(findings)
            self.assertTrue(all(isinstance(item["code"], str) for item in findings))

    def test_dedup_key_is_stable_and_changes_for_a_new_observation(self):
        first = self.receipt()
        self.assertEqual(readiness.dedup_key(first), readiness.dedup_key(self.receipt()))
        changed = self.receipt(head_sha="f" * 40)
        self.assertNotEqual(readiness.dedup_key(first), readiness.dedup_key(changed))
        changed = self.receipt(covered_roots=["workspace/autogrammar"])
        self.assertNotEqual(readiness.dedup_key(first), readiness.dedup_key(changed))

    def test_same_version_source_change_requires_accepted_review(self):
        previous = self.receipt()
        current = self.receipt(standard_revision="f" * 40)
        findings = readiness.validate_receipt(current, previous)
        self.assertIn("DOCS_READINESS_REVIEW", {item["code"] for item in findings})
        current["compatibility_review"] = {
            "required": True, "status": "accepted", "reviewer": "human@example.org",
            "evidence": ["receipt://review/1"],
        }
        self.assertEqual(readiness.validate_receipt(current, previous), [])

    def test_phase_cannot_regress_or_change_coverage(self):
        previous = self.receipt(phase="deployed")
        previous["evidence"]["deployed"] = ["receipt://deployed/1"]
        current = self.receipt()
        findings = readiness.validate_receipt(current, previous)
        self.assertIn("DOCS_READINESS_CHAIN", {item["code"] for item in findings})
        current["phase"] = "deployed"
        current["evidence"]["deployed"] = ["receipt://deployed/1"]
        current["covered_roots"] = ["other"]
        self.assertIn("DOCS_READINESS_CHAIN", {item["code"] for item in readiness.validate_receipt(current, previous)})


if __name__ == "__main__":
    unittest.main()
