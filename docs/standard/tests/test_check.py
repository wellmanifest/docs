import datetime
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('docs_check', Path(__file__).resolve().parents[1] / 'check.py')
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)
REV = 'a' * 40


class Conformance(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git('init', '-q')
        self.git('remote', 'add', 'origin', 'https://github.com/subactor/example.git')
        (self.root / '.governance').mkdir()
        self.adoption = {'schema': checker.POLICY['adoption_schema'], 'repository': 'subactor/example',
                         'standard': 'wellmanifest/docs', 'source_revision': REV,
                         'policy_sha256': checker.POLICY_SHA256}
        self.write_adoption()
        self.meta = {'schema': checker.POLICY['document_schema'], 'id': 'publication',
                     'kind': 'refactoring-plan', 'version': 1, 'title': 'Publication refactoring',
                     'status': 'proposed', 'owner': 'role:component-owner', 'created': '2026-09-05',
                     'updated': '2026-09-05', 'review_after': '2026-10-05',
                     'source_revision': 'b' * 40, 'affected_repositories': ['subactor/example'],
                     'evidence': ['receipt:tests/publication-v1']}
        self.name = 'docs/refactoring/publication.md'
        self.write_doc()
        (self.root / 'docs/README.md').write_text('[Plan](refactoring/publication.md)\n')
        self.git('add', '.')

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, stderr=subprocess.DEVNULL, text=True).strip()

    def write_adoption(self):
        (self.root / '.governance/docs.json').write_text(json.dumps(self.adoption))

    def write_doc(self, missing=None, empty=None):
        p = self.root / self.name
        p.parent.mkdir(parents=True, exist_ok=True)
        body = '# Plan\n'
        for section in checker.POLICY['kinds'][self.meta['kind']]['sections']:
            if section != missing:
                body += '\n<!-- docs:section ' + section + ' -->\n## ' + section + '\n'
                if section != empty:
                    body += '\nA concrete finding with bounded scope.\n'
        p.write_text('---\n' + json.dumps(self.meta) + '\n---\n' + body)

    def check(self, **kwargs):
        return checker.check(self.root, REV, today=datetime.date(2026, 9, 5), **kwargs)

    def codes(self, **kwargs):
        return {x['code'] for x in self.check(**kwargs)['findings']}

    def test_unavailable_base_is_rejected(self):
        self.assertIn('DOCS_BASE', self.codes(base='f' * 40))

    def test_deleted_tracked_index_is_rejected(self):
        (self.root / 'docs/README.md').unlink()
        self.assertIn('DOCS_INDEX', self.codes())

    def test_complete_plan_passes(self):
        self.assertTrue(self.check()['ok'])

    def test_outside_deliverable_is_rejected(self):
        self.assertIn('DOCS_LOCATION', self.codes(deliverables=['/tmp/report.md']))

    def test_wrong_location_is_rejected(self):
        target = self.root / 'project/report.md'
        target.parent.mkdir()
        (self.root / self.name).rename(target)
        self.git('add', '.')
        self.assertIn('DOCS_LOCATION', self.codes())

    def test_symlink_deliverable_is_rejected(self):
        (self.root / 'alias.md').symlink_to(self.root / self.name)
        self.assertIn('DOCS_LOCATION', self.codes(deliverables=['alias.md']))

    def test_missing_section_is_rejected(self):
        self.write_doc(missing='rollback')
        self.assertIn('DOCS_SECTIONS', self.codes())

    def test_empty_section_is_rejected(self):
        self.write_doc(empty='acceptance')
        self.assertIn('DOCS_EMPTY_SECTION', self.codes())

    def test_placeholder_is_rejected(self):
        self.meta['title'] = '{{TITLE}}'
        self.write_doc()
        self.assertIn('DOCS_PLACEHOLDER', self.codes())

    def test_missing_adoption_fails(self):
        (self.root / '.governance/docs.json').unlink()
        self.assertIn('DOCS_ADOPTION', self.codes())

    def test_changed_pin_and_policy_fail(self):
        for key, value in [('source_revision', 'main'), ('policy_sha256', 'c' * 64)]:
            old = self.adoption[key]
            self.adoption[key] = value
            self.write_adoption()
            self.assertIn('DOCS_ADOPTION', self.codes())
            self.adoption[key] = old

    def test_missing_index_fails_even_without_managed_documents(self):
        (self.root / self.name).unlink()
        (self.root / 'docs/README.md').unlink()
        self.git('add', '.')
        self.assertIn('DOCS_INDEX', self.codes())

    def test_missing_index_link_fails(self):
        (self.root / 'docs/README.md').write_text('# Index\n')
        self.assertIn('DOCS_INDEX', self.codes())

    def test_untracked_delivery_fails(self):
        self.git('rm', '--cached', self.name)
        self.assertIn('DOCS_UNTRACKED', self.codes(deliverables=[self.name]))

    def test_bad_metadata_types_fail(self):
        self.meta['version'] = True
        self.write_doc()
        self.assertIn('DOCS_METADATA', self.codes())

    def test_cross_repository_owner_is_explicit(self):
        self.meta['affected_repositories'].append('subactor/other')
        self.write_doc()
        self.assertIn('DOCS_OWNER', self.codes())
        path, index = checker.layout('subactor/docs', 'refactoring-plan', 'publication')
        self.assertEqual(path.as_posix(), 'architecture/refactoring/publication.md')
        self.assertEqual(index, 'README.md')

    def test_expired_review_is_visible_warning(self):
        self.meta.update(created='2026-01-01', updated='2026-01-01', review_after='2026-02-01')
        self.write_doc()
        result = self.check()
        self.assertTrue(result['ok'])
        self.assertEqual(result['warnings'][0]['code'], 'DOCS_REVIEW_DUE')

    def test_changed_document_requires_version_increase(self):
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'baseline')
        base = self.git('rev-parse', 'HEAD')
        self.meta['title'] = 'Changed finding'
        self.write_doc()
        self.assertIn('DOCS_VERSION', self.codes(base=base))
        self.meta['version'] = 2
        self.write_doc()
        self.assertNotIn('DOCS_VERSION', self.codes(base=base))

    def test_templates_cover_every_required_section(self):
        for kind, spec in checker.POLICY['kinds'].items():
            text = (checker.PACK / 'templates' / (kind + '.md')).read_text()
            meta, body = checker.metadata(text)
            self.assertEqual(meta['kind'], kind)
            self.assertEqual(set(meta), set(checker.POLICY['metadata']))
            self.assertEqual(set(checker.MARKER.findall(body)), set(spec['sections']))


if __name__ == '__main__':
    unittest.main()
