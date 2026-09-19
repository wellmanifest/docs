"""Real Git/CLI fleet canaries; no network or consumer writes."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))

from test_check import checker, REV


class Fleet(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def repo(self, name, identity='subactor/example', parent=None):
        root = (parent or self.root) / name
        root.mkdir(parents=True)
        self.git(root, 'init', '-q')
        self.git(root, 'remote', 'add', 'origin', 'https://github.com/' + identity + '.git')
        (root / '.governance').mkdir()
        (root / '.governance/docs.json').write_text(json.dumps({
            'schema': checker.POLICY['adoption_schema'], 'repository': identity,
            'standard': checker.POLICY['id'], 'source_revision': REV,
            'policy_sha256': checker.POLICY_SHA256}))
        (root / 'docs').mkdir()
        (root / 'docs/README.md').write_text('# Documentation\n')
        self.git(root, 'add', '.')
        self.git(root, '-c', 'user.name=Test', '-c', 'user.email=test@example.org', 'commit', '-qm', 'seed')
        return root

    def git(self, root, *args):
        return subprocess.check_output(['git', *args], cwd=root, stderr=subprocess.DEVNULL, text=True).strip()

    def audit(self, **kwargs):
        return checker.check_fleet([self.root], REV, **kwargs)

    def test_default_stays_subactor_and_reports_exclusion(self):
        self.repo('a')
        self.repo('b', 'semcod/other')
        result = self.audit()
        self.assertTrue(result['ok'])
        self.assertEqual(result['namespace_counts'], {'subactor': 1})
        self.assertEqual(result['skipped'][0]['reason'], 'namespace-not-selected')

    def test_distributed_pilot_report_conforms(self):
        root = self.repo('standard', 'wellmanifest/docs')
        name = 'docs/ANALYSIS/FLEET_COVERAGE_PILOT.md'
        path = root / name
        path.parent.mkdir(parents=True)
        path.write_text((checker.PACK.parent / 'ANALYSIS/FLEET_COVERAGE_PILOT.md').read_text())
        (root / 'docs/README.md').write_text('[Pilot](ANALYSIS/FLEET_COVERAGE_PILOT.md)')
        self.git(root, 'add', '.')
        result = checker.check(root, REV)
        self.assertTrue(result['ok'], result)

    def test_explicit_namespaces_are_case_insensitive_and_unique(self):
        self.repo('a', 'semcod/example')
        self.repo('b', 'autogrammar/example')
        result = self.audit(namespaces=['Semcod', 'autogrammar', 'semcod'])
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['namespace_counts'], {'autogrammar': 1, 'semcod': 1})
        self.assertEqual(result['unique_repositories_checked'], 2)

    def test_empty_selected_namespace_fails_even_if_another_passes(self):
        self.repo('a', 'semcod/example')
        result = self.audit(namespaces=['semcod', 'autogrammar'])
        self.assertFalse(result['ok'])
        self.assertIn({'code': 'DOCS_FLEET_EMPTY', 'namespace': 'autogrammar'}, result['findings'])

    def test_no_checkouts_is_not_compliance(self):
        self.assertFalse(self.audit()['ok'])

    def test_no_adoption_is_not_skipped(self):
        root = self.repo('a', 'semcod/example')
        (root / '.governance/docs.json').unlink()
        result = self.audit(namespaces=['semcod'])
        self.assertFalse(result['ok'])
        self.assertEqual(result['repositories_checked'], 1)
        self.assertEqual(result['reports'][0]['findings'][0]['code'], 'DOCS_ADOPTION')

    def test_duplicate_origin_does_not_mask_bad_copy(self):
        self.repo('a')
        bad = self.repo('b')
        (bad / '.governance/docs.json').unlink()
        result = self.audit()
        self.assertFalse(result['ok'])
        self.assertEqual(result['repositories_checked'], 2)
        self.assertEqual(result['unique_repositories_checked'], 1)
        self.assertEqual(len(result['duplicates'][0]['checkouts']), 2)
        self.assertEqual([r['ok'] for r in result['reports']], [True, False])

    def test_nested_container_requires_explicit_root(self):
        container = self.root / 'taskand'
        self.repo('glm53', 'semcod/taskand-glm53', container)
        self.assertFalse(self.audit(namespaces=['semcod'])['ok'])
        result = checker.check_fleet([self.root, container], REV, ['semcod'])
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['repositories_checked'], 1)
        self.assertEqual(result['skipped'][0]['reason'], 'not-immediate-checkout')

    def test_repeated_root_does_not_double_count_same_path(self):
        self.repo('a')
        result = checker.check_fleet([self.root, self.root], REV)
        self.assertTrue(result['ok'])
        self.assertEqual(result['repositories_checked'], 1)
        self.assertEqual(result['skipped'][0]['reason'], 'repeated-path')

    def test_symlink_child_is_reported_not_followed(self):
        root = self.repo('a')
        (self.root / 'b').symlink_to(root, target_is_directory=True)
        result = self.audit()
        self.assertEqual(result['repositories_checked'], 1)
        self.assertEqual(result['skipped'][0]['reason'], 'symlink')

    def test_invalid_and_symlink_root_fail(self):
        self.repo('a')
        alias = self.root / 'alias'
        alias.symlink_to(self.root, target_is_directory=True)
        for root in [self.root / 'missing', alias, alias / 'a']:
            result = checker.check_fleet([root], REV)
            self.assertFalse(result['ok'])
            self.assertEqual(result['findings'][0]['code'], 'DOCS_FLEET_ROOT')

    def test_unresolved_origin_is_visible_failure(self):
        root = self.repo('a')
        self.git(root, 'remote', 'remove', 'origin')
        result = self.audit()
        self.assertFalse(result['ok'])
        self.assertEqual(result['findings'][0]['code'], 'DOCS_FLEET_ORIGIN')

    def test_origin_parser_rejects_spoofed_host_and_credentials(self):
        root = self.repo('a')
        for url in ['https://evilgithub.com/subactor/example',
                    'https://evil.test/github.com/subactor/example',
                    'https://user:secret@github.com/subactor/example',
                    'https://github.com/subactor/example?ref=fixture']:
            self.git(root, 'remote', 'set-url', 'origin', url)
            self.assertIsNone(checker.origin(root))

    def test_supported_origins(self):
        root = self.repo('a')
        for url in ['https://github.com/subactor/example.git',
                    'git@github.com:subactor/example.git',
                    'ssh://git@github.com/subactor/example',
                    'https://GITHUB.COM/subactor/example']:
            self.git(root, 'remote', 'set-url', 'origin', url)
            self.assertEqual(checker.origin(root), 'subactor/example')

    def test_checkout_read_error_does_not_abort_other_observations(self):
        self.repo('a')
        self.repo('b')
        with patch.object(checker, 'check', side_effect=[UnicodeError('bad'), {'ok': True}]):
            result = self.audit()
        self.assertFalse(result['ok'])
        self.assertEqual(len(result['reports']), 2)
        self.assertEqual(result['reports'][0]['findings'][0]['code'], 'DOCS_CHECKOUT_READ')

    def test_invalid_namespace_and_revision_are_rejected(self):
        for namespaces in [[], ['*'], ['semcod/'], ['../semcod'], [''], [None]]:
            with self.assertRaises(ValueError):
                self.audit(namespaces=namespaces)
        with self.assertRaises(ValueError):
            checker.check_fleet([self.root], 'main')

    def test_cli_multiple_roots_and_namespace(self):
        self.repo('a', 'semcod/example')
        result = subprocess.run([sys.executable, str(checker.PACK / 'check.py'),
            '--fleet', str(self.root), '--fleet', str(self.root),
            '--namespace', 'semcod', '--standard-revision', REV], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(json.loads(result.stdout)['repositories_checked'], 1)

    def test_cli_namespace_cannot_change_single_repository_policy(self):
        result = subprocess.run([sys.executable, str(checker.PACK / 'check.py'),
            '--root', str(self.root), '--namespace', 'semcod', '--standard-revision', REV],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('--namespace requires --fleet', result.stderr)

    def test_cli_missing_fleet_root_is_json_failure(self):
        result = subprocess.run([sys.executable, str(checker.PACK / 'check.py'),
            '--fleet', str(self.root / 'missing'), '--standard-revision', REV],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)['findings'][0]['code'], 'DOCS_FLEET_ROOT')
        self.assertNotIn('Traceback', result.stderr)

    def test_cli_wildcard_namespace_is_usage_error(self):
        result = subprocess.run([sys.executable, str(checker.PACK / 'check.py'),
            '--fleet', str(self.root), '--namespace', '*', '--standard-revision', REV],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('Namespaces must be explicit', result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_linked_checkout_is_a_separate_observation(self):
        root = self.repo('a')
        self.git(root, 'worktree', 'add', '--detach', str(self.root / 'b'), 'HEAD')
        result = self.audit()
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['repositories_checked'], 2)
        self.assertEqual(result['unique_repositories_checked'], 1)

    def test_dirty_checkout_and_exact_head_are_explicit(self):
        root = self.repo('a')
        before = self.audit()['reports'][0]
        self.assertFalse(before['working_tree_dirty'])
        self.assertEqual(before['head_sha'], self.git(root, 'rev-parse', 'HEAD'))
        (root / 'untracked.txt').write_text('preserve me')
        after = self.audit()['reports'][0]
        self.assertTrue(after['working_tree_dirty'])
        self.assertEqual(before['head_sha'], after['head_sha'])

    def test_unborn_checkout_is_not_verified_revision(self):
        root = self.repo('a')
        self.git(root, 'checkout', '--orphan', 'unborn')
        result = self.audit()
        self.assertFalse(result['ok'])
        self.assertIsNone(result['reports'][0]['head_sha'])
        self.assertIn({'code': 'DOCS_FLEET_OBSERVATION', 'path': str(root)}, result['findings'])


if __name__ == '__main__':
    unittest.main()
