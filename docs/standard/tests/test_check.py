import datetime
import importlib.util
import json
import subprocess
import sys
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

    def test_nested_json_is_not_a_template_placeholder(self):
        path = self.root / self.name
        path.write_text(path.read_text() + '\n```json\n{"budget":{"deadline_ms":8000,"concurrency":3}}\n```\n')
        self.assertTrue(self.check()['ok'], self.check()['findings'])

    def test_code_braces_and_literal_single_delimiters_are_not_placeholders(self):
        path = self.root / self.name
        for example in ['if (ready) {{run();}}', 'nested JSON closes with }}', 'opening delimiters {{']:
            with self.subTest(example=example):
                self.write_doc()
                path.write_text(path.read_text() + '\n```text\n' + example + '\n```\n')
                self.assertNotIn('DOCS_PLACEHOLDER', self.codes())

    def test_actual_placeholder_is_rejected_in_prose_and_code(self):
        path = self.root / self.name
        for example in ['Owner: {{OWNER}}', '```json\n{"owner":"{{OWNER}}"}\n```', '{{ OWNER_NAME }}', '{{title}}']:
            with self.subTest(example=example):
                self.write_doc()
                path.write_text(path.read_text() + '\n' + example + '\n')
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

    def commit_base(self):
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 'commit', '-qm', 'baseline')
        return self.git('rev-parse', 'HEAD')

    def test_new_plain_report_is_discovered_from_base(self):
        base = self.commit_base()
        (self.root / 'REPORT.md').write_text('# Analysis without metadata\n')
        self.git('add', 'REPORT.md')
        result = self.check(base=base)
        self.assertFalse(result['ok'])
        self.assertTrue(any(x['path'] == 'REPORT.md' and x['code'] == 'DOCS_METADATA'
                            for x in result['findings']))

    def test_metadata_removal_is_rejected_without_declaration(self):
        base = self.commit_base()
        (self.root / self.name).write_text('# Plain replacement\n')
        self.assertIn('DOCS_METADATA', self.codes(base=base))

    def test_symlink_replacement_is_rejected_without_declaration(self):
        base = self.commit_base()
        (self.root / self.name).unlink()
        (self.root / self.name).symlink_to(self.root / 'docs/README.md')
        self.git('add', self.name)
        self.assertIn('DOCS_LOCATION', self.codes(base=base))

    def test_unchanged_legacy_is_preserved_but_edit_requires_migration(self):
        path = self.root / 'legacy.md'
        path.write_text('# Historical analysis\n')
        self.git('add', '.')
        base = self.commit_base()
        self.assertTrue(self.check(base=base)['ok'])
        path.write_text('# Changed analysis\n')
        self.assertIn('DOCS_METADATA', self.codes(base=base))

    def test_organizational_files_are_exempt_but_explicit_delivery_is_not(self):
        base = self.commit_base()
        for name in ['README.md', 'AGENTS.md', 'project/ticket-002/README.md']:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('# Organizational file\n')
        self.git('add', '.')
        self.assertTrue(self.check(base=base)['ok'])
        self.assertIn('DOCS_METADATA', self.codes(base=base, deliverables=['README.md']))

    def test_renamed_legacy_report_requires_migration(self):
        (self.root / 'legacy.md').write_text('# Old report\n')
        self.git('add', '.')
        base = self.commit_base()
        self.git('mv', 'legacy.md', 'REPORT.md')
        self.assertIn('DOCS_METADATA', self.codes(base=base))

    def test_templates_cover_every_required_section(self):
        for kind, spec in checker.POLICY['kinds'].items():
            text = (checker.PACK / 'templates' / (kind + '.md')).read_text()
            meta, body = checker.metadata(text)
            self.assertEqual(meta['kind'], kind)
            self.assertEqual(set(meta), set(checker.POLICY['metadata']) | {'scope'})
            self.assertEqual(set(checker.MARKER.findall(body)), set(spec['sections']))

    def explicit_scope(self, scope='repository', repository='subactor/example'):
        self.git('remote', 'set-url', 'origin', 'https://github.com/' + repository + '.git')
        self.adoption['repository'] = repository
        self.write_adoption()
        self.meta.update(scope=scope, owner=repository)
        self.write_doc()

    def prepare(self, **kwargs):
        options = dict(kind='analysis', slug='new-report', scope='repository',
                       destination='docs/analysis/new-report.md')
        options.update(kwargs)
        return checker.prepare_delivery(self.root, REV, **options)

    def test_report_home_resolves_any_organization(self):
        for org in ['subactor', 'semcod', 'wellmanifest']:
            self.assertEqual(checker.report_home(org + '/core', 'organization'), org + '/report')
            self.assertEqual(checker.report_home(org + '/core', 'repository'), org + '/core')
        for repo, scope in [(None, 'repository'), ('invalid', 'repository'), ('subactor/core', 'guess')]:
            with self.assertRaises(ValueError):
                checker.report_home(repo, scope)

    def test_repository_owned_report_can_reference_other_repositories(self):
        self.explicit_scope()
        self.meta['affected_repositories'].append('subactor/other')
        self.write_doc()
        self.assertTrue(self.check()['ok'])

    def test_organization_report_requires_report_repository(self):
        self.explicit_scope('organization')
        self.assertIn('DOCS_OWNER', self.codes())
        self.explicit_scope('organization', 'semcod/report')
        self.assertTrue(self.check()['ok'])

    def test_explicit_owner_and_scope_are_validated(self):
        self.explicit_scope()
        self.meta['owner'] = 'role:component-owner'
        self.write_doc()
        self.assertIn('DOCS_OWNER', self.codes())
        self.meta['scope'] = ['organization']
        self.write_doc()
        self.assertIn('DOCS_METADATA', self.codes())

    def test_legacy_scope_is_preserved_until_changed(self):
        base = self.commit_base()
        self.assertTrue(self.check(base=base)['ok'])
        self.meta.update(version=2, title='New findings')
        self.write_doc()
        self.assertIn('DOCS_SCOPE', self.codes(base=base))
        self.explicit_scope()
        self.assertTrue(self.check(base=base)['ok'])

    def test_scope_removal_and_new_unscoped_document_fail(self):
        self.explicit_scope()
        self.git('add', '.')
        base = self.commit_base()
        del self.meta['scope']
        self.meta['version'] = 2
        self.write_doc()
        self.assertIn('DOCS_SCOPE', self.codes(base=base))
        self.meta['id'] = 'new-report'
        self.name = 'docs/refactoring/new-report.md'
        self.write_doc()
        self.git('add', '.')
        self.assertTrue(any(f['path'] == self.name and f['code'] == 'DOCS_SCOPE'
                            for f in self.check(base=base)['findings']))

    def test_preflight_is_read_only_and_deterministic(self):
        before = self.git('status', '--porcelain')
        result = self.prepare()
        self.assertTrue(result['ok'], result)
        self.assertEqual(result, self.prepare())
        self.assertEqual(result['plan']['owner'], 'subactor/example')
        self.assertEqual(result['plan']['authority'], 'read-only-placement-evidence')
        self.assertFalse((self.root / 'docs/analysis/new-report.md').exists())
        self.assertEqual(before, self.git('status', '--porcelain'))

    def test_preflight_blocks_wrong_owner_missing_adoption_and_index(self):
        self.assertFalse(self.prepare(scope='organization')['ok'])
        (self.root / '.governance/docs.json').unlink()
        self.assertFalse(self.prepare()['ok'])
        self.write_adoption()
        self.git('rm', '--cached', 'docs/README.md')
        self.assertFalse(self.prepare()['ok'])

    def test_preflight_blocks_external_traversal_and_symlink_paths(self):
        for destination in ['/tmp/report.md', '../report.md', 'docs/analysis/../analysis/new-report.md', 'REPORT.md']:
            self.assertFalse(self.prepare(destination=destination)['ok'], destination)
        (self.root / 'docs/analysis').symlink_to(self.root / 'docs/refactoring', target_is_directory=True)
        self.assertFalse(self.prepare()['ok'])

    def test_preflight_organization_report_passes_in_owning_repository(self):
        self.explicit_scope('organization', 'subactor/report')
        self.assertTrue(self.prepare(scope='organization')['ok'])

    def test_missing_root_or_origin_fails_closed(self):
        result = checker.prepare_delivery(self.root / 'absent', REV, 'analysis', 'new-report',
                                          'repository', 'docs/analysis/new-report.md')
        self.assertFalse(result['ok'])
        self.explicit_scope()
        self.git('remote', 'remove', 'origin')
        self.assertFalse(self.check()['ok'])

    def test_preflight_cli_requires_complete_declaration(self):
        command = [sys.executable, str(checker.PACK / 'check.py'), '--root', str(self.root),
                   '--standard-revision', REV, '--prepare']
        invalid = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(invalid.returncode, 2)
        result = subprocess.run(command + ['--kind', 'analysis', '--id', 'new-report',
                               '--scope', 'repository', '--deliverable', 'docs/analysis/new-report.md'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)['ok'])


if __name__ == '__main__':
    unittest.main()
