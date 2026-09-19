"""Opt-in, immutable published corpus pilots; never modify consumer checkouts.

DOCS_PILOT_WORKSPACE points to an existing local GitHub workspace. Temporary
fixtures simulate adoption and deliberate defects; this is not consumer CI.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from test_check import checker, REV

PILOTS = [
    ('semcod/koru', 'semcod/koru', '31ad18f9a78c1912ba12dd97b7e90c913c0c1e83', [
        'docs/SERVICE/COMMAND_EXECUTION.md', 'docs/SERVICE/CI_COMPLETION_GATES.md',
        'docs/SERVICE/POST_RUN_VERIFICATION.md', 'docs/auto-execute-commands.md',
        'docs/post-run-verify.md']),
    ('semcod/goal', 'semcod/goal', 'd0b4ff013d225f1c2cc2b29f9a4a3d34735f68a7', [
        'docs/FEATURE/MARKDOWN_OUTPUT.md', 'docs/SERVICE/MARKDOWN_OUTPUT_INTEGRATION.md',
        'docs/markdown-output.md', 'docs/markdown-output-guide.md']),
    ('semcod/taskand-glm53', 'semcod/taskand/glm53', '0f9df49f33d6cd85006fe4e41378f06b7347d7dd', [
        'docs/REFACTORING/HISTORY_INTENT_ANALYSIS.md', 'docs/REFACTORING/OFFLINE_NODE_UPDATES.md',
        'docs/REFACTORING/RUNTIME_PACKAGE_CONTRACT.md', 'docs/REFACTORING/LOCAL_CI_DELIVERY.md',
        'docs/REFACTORING/PERFORMANCE_EVOLUTION.md', 'docs/REFACTORING/SDLC_PRIORITY_POLICY.md',
        'docs/REFACTORING/REPOSITORY_ONBOARDING.md', 'docs/refactoring/continuous-evolution-plan.md']),
]


@unittest.skipUnless(os.environ.get('DOCS_PILOT_WORKSPACE'), 'Set DOCS_PILOT_WORKSPACE for published consumer corpus pilots')
class ConsumerCorpus(unittest.TestCase):
    def fixture(self, pilot):
        repository, local, revision, names = pilot
        source = Path(os.environ['DOCS_PILOT_WORKSPACE']) / local
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.git(root, 'init', '-q')
        self.git(root, 'remote', 'add', 'origin', 'https://github.com/' + repository + '.git')
        index = self.git(source, 'show', revision + ':docs/README.md')
        links = []
        for name in names:
            text = self.git(source, 'show', revision + ':' + name)
            meta, _ = checker.metadata(text)
            if meta['schema'] == checker.POLICY['compact']['document_schema']:
                self.assertIn('](' + name[5:] + ')', index, 'Published index must link the canonical document')
                links.append('[Topic](' + name[5:] + ')')
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text)
        (root / 'docs/README.md').write_text('\n'.join(links))
        (root / 'CHANGELOG.md').write_text('[Pilot topic](' + names[0] + ')\n')
        (root / '.governance').mkdir()
        (root / '.governance/docs.json').write_text(json.dumps({
            'schema': checker.POLICY['adoption_schema'], 'repository': repository,
            'standard': checker.POLICY['id'], 'source_revision': REV,
            'policy_sha256': checker.POLICY_SHA256}))
        self.git(root, 'add', '.')
        self.git(root, '-c', 'user.name=Test', '-c', 'user.email=test@example.org', 'commit', '-qm', 'corpus fixture')
        return root

    def git(self, root, *args):
        return subprocess.check_output(['git', *args], cwd=root, text=True, stderr=subprocess.PIPE)

    def test_published_topics_and_maps_pass_idempotently(self):
        for pilot in PILOTS:
            with self.subTest(repository=pilot[0]):
                root = self.fixture(pilot)
                base = self.git(root, 'rev-parse', 'HEAD').strip()
                first = checker.check(root, REV, base=base)
                self.assertTrue(first['ok'], first)
                self.assertEqual(first['documents_checked'], len(pilot[3]))
                self.assertEqual(first, checker.check(root, REV, base=base))
                self.assertEqual(self.git(root, 'status', '--porcelain'), '')

    def test_preflight_rejects_missing_adoption_before_generation(self):
        for pilot in PILOTS:
            with self.subTest(repository=pilot[0]):
                root = self.fixture(pilot)
                destination = 'docs/FEATURE/NEXT_PILOT.md'
                good = checker.prepare_delivery(root, REV, 'feature', 'next-pilot', 'repository', destination, compact=True)
                self.assertTrue(good['ok'], good)
                (root / '.governance/docs.json').unlink()
                bad = checker.prepare_delivery(root, REV, 'feature', 'next-pilot', 'repository', destination, compact=True)
                self.assertFalse(bad['ok'])
                self.assertIn('DOCS_ADOPTION', {f['code'] for f in bad['findings']})
                self.assertFalse((root / destination).exists())

    def test_wrong_pin_fails_each_corpus(self):
        for pilot in PILOTS:
            with self.subTest(repository=pilot[0]):
                result = checker.check(self.fixture(pilot), 'b' * 40)
                self.assertFalse(result['ok'])
                self.assertIn('DOCS_ADOPTION', {f['code'] for f in result['findings']})

    def test_removed_metadata_cannot_escape_final_base_check(self):
        for pilot in PILOTS:
            with self.subTest(repository=pilot[0]):
                root = self.fixture(pilot)
                base = self.git(root, 'rev-parse', 'HEAD').strip()
                (root / pilot[3][0]).write_text('# Missing metadata\n')
                result = checker.check(root, REV, base=base)
                self.assertFalse(result['ok'])
                self.assertIn('DOCS_METADATA', {f['code'] for f in result['findings']})

    def test_removed_map_target_fails_each_corpus(self):
        for pilot in PILOTS:
            with self.subTest(repository=pilot[0]):
                root = self.fixture(pilot)
                (root / pilot[3][0]).unlink()
                result = checker.check(root, REV)
                self.assertFalse(result['ok'])
                self.assertIn('DOCS_REDIRECT_TARGET', {f['code'] for f in result['findings']})


if __name__ == '__main__':
    unittest.main()
