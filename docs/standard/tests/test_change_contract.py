import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import test_check

checker = test_check.checker

contract = checker.CONTRACT
SOURCE = '''DOCUMENT DOCS_FEATURE
VERSION 1
MODE STRICT
POLICY "wellmanifest.docs/change/v1"
SUBJECT = "change-contract"
COMPATIBILITY = "Plain compact documents remain valid"
INPUTS IN ["RESULT"]
RULE AC-01 TYPE REQUIRED
WHEN TRUE
ASSERT RESULT = "valid"
DO VALIDATE "tests/acceptance.py"
'''


class FenceTests(unittest.TestCase):
    def test_plain_markdown_does_not_require_runtime(self):
        self.assertIsNone(contract.check("# Plain guide", {}, Path("."), set(), None))

    def test_missing_runtime_is_explicit_failure(self):
        with self.assertRaises(contract.ContractError) as result:
            contract.check("```dsl\n" + SOURCE + "```", {}, Path("."), set(), None)
        self.assertEqual(result.exception.code, "DOCS_DSL_RUNTIME")

    def test_outer_example_is_not_a_contract(self):
        self.assertEqual(contract.blocks("````text\n```dsl\nexample\n```\n````"), [])

    def test_invalid_or_unclosed_fences_fail(self):
        for text in ["```dsl\nDOCUMENT X", "```DSL\nX\n```", "```dsl example\nX\n```"]:
            with self.subTest(text=text), self.assertRaises(contract.ContractError):
                contract.blocks(text)

    def test_duplicate_contracts_fail_before_loading_code(self):
        with self.assertRaises(contract.ContractError) as result:
            contract.check(("```dsl\n" + SOURCE + "```\n") * 2, {}, Path("."), set(), None)
        self.assertEqual(result.exception.code, "DOCS_DSL_CONTRACT")


class ProfileIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        selected = os.environ.get("POLICY_DSL_ROOT")
        if not selected:
            raise unittest.SkipTest("Set POLICY_DSL_ROOT to the pinned canonical checkout for integration tests")
        cls.runtime = Path(selected)
        cls.parser = contract.load_parser(cls.runtime)

    def setUp(self):
        self.fixture = test_check.Conformance()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.name = "docs/FEATURE/CHANGE_CONTRACT.md"
        self.meta = dict(schema="wellmanifest.docs/document/v2", id="change-contract",
                         kind="feature", version=1, title="Change contract", status="proposed",
                         owner="subactor/example", scope="repository", updated="2026-09-14",
                         source_revision="b" * 40, priority="P2", evidence=["receipt:contract/tests"])
        (self.root / "tests").mkdir()
        (self.root / "tests/acceptance.py").write_text("# Referenced only; never executed\nraise RuntimeError('must not execute')\n")
        (self.root / "docs/README.md").write_text("[Old](refactoring/publication.md)\n[Contract](FEATURE/CHANGE_CONTRACT.md)\n")
        self.write(SOURCE)
        self.fixture.git("add", ".")

    def write(self, source):
        path = self.root / self.name
        path.parent.mkdir(parents=True, exist_ok=True)
        sections = ["Concrete purpose.", "Behavior.\n```dsl\n" + source + "```",
                    "File references are not test results.", "No authority or execution."]
        text = "---\n" + json.dumps(self.meta) + "\n---\n"
        for section, body in zip(["summary", "details", "validation", "risks"], sections):
            text += "\n<!-- docs:section " + section + " -->\n" + body + "\n"
        path.write_text(text)

    def codes(self, source=None, runtime=True):
        if source is not None:
            self.write(source)
        return self.fixture.codes(policy_dsl_root=self.runtime if runtime else None)

    def test_valid_feature_and_plain_v1_coexist(self):
        self.assertEqual(self.codes(), set())

    def test_public_cli_requires_explicit_verified_runtime(self):
        command = [sys.executable, str(checker.PACK / "check.py"),
                   "--root", str(self.root), "--standard-revision", test_check.REV]
        for runtime, expected in [(False, 1), (True, 0)]:
            with self.subTest(runtime=runtime):
                args = command + (["--policy-dsl-root", str(self.runtime)] if runtime else [])
                result = subprocess.run(args, text=True, capture_output=True, check=False)
                report = json.loads(result.stdout)
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                self.assertEqual(report["ok"], runtime)
                if not runtime:
                    self.assertIn("DOCS_DSL_RUNTIME", {f["code"] for f in report["findings"]})

    def test_legacy_v1_dsl_is_not_reinterpreted(self):
        with (self.root / self.fixture.name).open("a") as stream:
            stream.write("\n```dsl\nLEGACY CONTENT\n```\n")
        self.assertEqual(self.codes(), set())

    def test_runtime_required_for_selected_contract(self):
        self.assertIn("DOCS_DSL_RUNTIME", self.codes(runtime=False))

    def test_invalid_metadata_is_a_finding_not_a_crash(self):
        del self.meta['version']
        self.assertIn('DOCS_METADATA', self.codes(SOURCE))

    def test_runtime_symlink_is_rejected(self):
        path = self.root / 'linked-runtime'
        path.symlink_to(self.runtime, target_is_directory=True)
        with self.assertRaises(contract.ContractError) as result:
            contract.load_parser(path)
        self.assertEqual(result.exception.code, 'DOCS_DSL_RUNTIME')

    def test_valid_bugfix(self):
        self.meta["kind"] = "bugfix"
        self.meta["id"] = "regression"
        self.name = "docs/BUGFIX/REGRESSION.md"
        source = SOURCE.replace("DOCS_FEATURE", "DOCS_BUGFIX").replace('"change-contract"', '"regression"')
        source = source.replace('INPUTS IN', 'REPRODUCTION = "Duplicate contract blocks"\nBEFORE = "Ambiguous input"\nAFTER = "Rejected input"\nINPUTS IN')
        self.write(source)
        with (self.root / "docs/README.md").open("a") as stream:
            stream.write("[Fix](BUGFIX/REGRESSION.md)\n")
        self.fixture.git("add", ".")
        self.assertEqual(self.codes(), set())

    def test_header_and_identity_rejected(self):
        for old, new in [("DOCS_FEATURE", "DOCS_BUGFIX"), ("VERSION 1", "VERSION 2"),
                         ("STRICT", "PROCEDURAL"), ("change/v1", "unknown/v1"),
                         ('"change-contract"', '"other"')]:
            with self.subTest(new=new):
                self.assertIn("DOCS_DSL_CONTRACT", self.codes(SOURCE.replace(old, new)))

    def test_missing_bugfix_fields(self):
        self.meta["kind"] = "bugfix"
        self.assertIn("DOCS_DSL_CONTRACT", self.codes(SOURCE.replace("DOCS_FEATURE", "DOCS_BUGFIX")))

    def test_effects_and_ambient_environment_rejected(self):
        for source in [
            SOURCE.replace('INPUTS IN', 'ENV_FILE ".env" OPTIONAL\nINPUTS IN'),
            SOURCE.replace("DO VALIDATE", "DO EXECUTE"),
            SOURCE.replace("DO VALIDATE", "FORBID EXECUTE"),
            SOURCE + "NEXT DONE\n", SOURCE + "STATE DONE\n",
            SOURCE.replace("DO VALIDATE \"tests/acceptance.py\"", "DO VALIDATE"),
        ]:
            with self.subTest(source=source):
                self.assertTrue(self.codes(source) & {"DOCS_DSL_CONTRACT", "DOCS_DSL_SYNTAX"})

    def test_undeclared_observation_and_vacuous_assertion_rejected(self):
        for assertion in ['ASSERT UNKNOWN = "valid"', "ASSERT TRUE", "ASSERT RESULT EXTRA"]:
            with self.subTest(assertion=assertion):
                self.assertTrue(self.codes(SOURCE.replace('ASSERT RESULT = "valid"', assertion))
                                & {"DOCS_DSL_CONTRACT", "DOCS_DSL_SYNTAX"})

    def test_missing_or_unknown_bindings_and_assertions_rejected(self):
        for source in [SOURCE.replace('COMPATIBILITY = "Plain compact documents remain valid"\n', ""),
                       SOURCE.replace('INPUTS IN', 'EXTRA = "invalid"\nINPUTS IN'),
                       SOURCE.replace('ASSERT RESULT = "valid"\n', ""),
                       SOURCE.replace('DO VALIDATE "tests/acceptance.py"\n', "")]:
            with self.subTest(source=source):
                self.assertIn("DOCS_DSL_CONTRACT", self.codes(source))

    def test_test_reference_boundary(self):
        for target in ["../tests/acceptance.py", "/tests/acceptance.py", "tests/missing.py", "docs/README.md",
                       "tests/acceptance.py::test_name", "tests/acceptance.py; echo side-effect"]:
            with self.subTest(target=target):
                self.assertIn("DOCS_DSL_TEST", self.codes(SOURCE.replace("tests/acceptance.py", target)))

    def test_untracked_or_symlink_test_rejected(self):
        self.fixture.git("rm", "--cached", "tests/acceptance.py")
        self.assertIn("DOCS_DSL_TEST", self.codes())
        path = self.root / "tests/acceptance.py"
        path.unlink()
        path.symlink_to(self.root / "docs/README.md")
        self.fixture.git("add", ".")
        self.assertIn("DOCS_DSL_TEST", self.codes())

    def test_runtime_tampering_rejected_before_execution(self):
        runtime = self.root / "runtime"
        (runtime / "tests").mkdir(parents=True)
        (runtime / "tests/policy_dsl_check.py").write_text("raise RuntimeError('must not execute')")
        with self.assertRaises(contract.ContractError) as result:
            contract.load_parser(runtime)
        self.assertEqual(result.exception.code, "DOCS_DSL_RUNTIME")

    def test_unknown_syntax_and_duplicate_rules_rejected(self):
        for source in [SOURCE + "garbage\n", SOURCE + SOURCE[SOURCE.index("RULE"):]]:
            with self.subTest(source=source):
                self.assertIn("DOCS_DSL_SYNTAX", self.codes(source))

    def test_result_is_not_test_evidence(self):
        result = contract.check("```dsl\n" + SOURCE + "```", self.meta, self.root,
                                checker.tracked(self.root), checker.safe_path, self.runtime)
        self.assertEqual(result["authority"], "none")
        self.assertFalse(result["assertions_evaluated"])
        self.assertFalse(result["tests_executed"])

    def test_distributed_examples(self):
        root = checker.PACK.parent.parent
        for name in ['docs/FEATURE/CHANGE_CONTRACTS.md', 'docs/BUGFIX/DUPLICATE_DSL_CONTRACT.md']:
            text = (root / name).read_text()
            meta, body = checker.metadata(text)
            with self.subTest(name=name):
                result = contract.check(body, meta, root, checker.tracked(root), checker.safe_path, self.runtime)
                self.assertEqual(result['criteria'], ['AC-01'])
                self.assertLessEqual(len(text.splitlines()), 120)
                self.assertLessEqual(len(text.split()), 600)
                self.assertLessEqual(len(text.encode()), 12288)


if __name__ == "__main__":
    unittest.main()
