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

    def completion_fixture(self):
        self.meta.update(scope='repository', owner='subactor/example')
        self.write_doc()
        self.git('add', '.')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.com', 'commit', '-qm', 'base')
        base = self.git('rev-parse', 'HEAD')
        prepared = checker.prepare_delivery(self.root, REV, self.meta['kind'], self.meta['id'],
                                             'repository', self.name)
        self.assertTrue(prepared['ok'], prepared)
        return base, prepared

    def complete(self, base, prepared, paths=None):
        return checker.complete_delivery(self.root, REV, [self.name] if paths is None else paths, base, prepared)

    def managed_copy(self):
        import hashlib
        name = '.governance/docs/UPSTREAM.md'
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((self.root / self.name).read_bytes())
        self.git('add', name)
        return {name: hashlib.sha256(path.read_bytes()).hexdigest()}

    def test_external_copy_requires_explicit_verified_inventory(self):
        copies = self.managed_copy()
        self.assertIn('DOCS_LOCATION', self.codes())
        result = self.check(managed_copies=copies)
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['managed_copies_verified'][0]['path'], next(iter(copies)))
        (self.root / next(iter(copies))).write_text('tampered')
        self.assertIn('DOCS_MANAGED_COPY', self.codes(managed_copies=copies))

    def test_managed_copy_cannot_hide_deliverables_or_product_documents(self):
        copies = self.managed_copy()
        self.assertIn('DOCS_MANAGED_COPY', self.codes(managed_copies=copies, deliverables=list(copies)))
        self.assertIn('DOCS_MANAGED_COPY', self.codes(managed_copies={self.name: 'a' * 64}))
        self.assertIn('DOCS_MANAGED_COPY', self.codes(managed_copies=[]))

    def test_managed_copy_rejects_untracked_symlink_and_unsafe_path(self):
        copies = self.managed_copy()
        name = next(iter(copies))
        self.git('rm', '--cached', name)
        self.assertIn('DOCS_MANAGED_COPY', self.codes(managed_copies=copies))
        path = self.root / name
        path.unlink()
        path.symlink_to(self.root / self.name)
        self.git('add', name)
        self.assertIn('DOCS_MANAGED_COPY', self.codes(managed_copies=copies))
        for invalid in ('/etc/passwd', '.governance/docs/../../report.md'):
            self.assertIn('DOCS_MANAGED_COPY', self.codes(managed_copies={invalid: 'a' * 64}))

    def test_completion_binds_managed_copy_inventory(self):
        base, _ = self.completion_fixture()
        copies = self.managed_copy()
        plan = checker.prepare_delivery(self.root, REV, self.meta['kind'], self.meta['id'],
                                        'repository', self.name, managed_copies=copies)
        self.assertTrue(plan['ok'], plan)
        good = checker.complete_delivery(self.root, REV, [self.name], base, plan, managed_copies=copies)
        self.assertTrue(good['ok'], good)
        bad = checker.complete_delivery(self.root, REV, [self.name], base, plan)
        self.assertFalse(bad['ok'])

    def test_completion_requires_explicit_result_and_preflight(self):
        base, prepared = self.completion_fixture()
        self.assertFalse(self.complete(base, prepared, [])['ok'])
        self.assertFalse(self.complete(base, {})['ok'])
        self.assertFalse(self.complete(None, prepared)['ok'])

    def test_completion_binds_actual_files(self):
        base, prepared = self.completion_fixture()
        result = self.complete(base, prepared)
        self.assertTrue(result['ok'], result)
        self.assertFalse(result['completion']['publication_verified'])
        self.assertEqual(len(result['completion']['artifacts']), 2)
        (self.root / self.name).unlink()
        self.assertFalse(self.complete(base, prepared)['ok'])

    def test_completion_rejects_recovery_only_result(self):
        base, prepared = self.completion_fixture()
        self.assertFalse(self.complete(base, prepared, ['/tmp/report.md'])['ok'])
        self.git('rm', '--cached', self.name)
        self.assertFalse(self.complete(base, prepared)['ok'])

    def test_completion_rejects_tampered_plan_or_identity(self):
        base, prepared = self.completion_fixture()
        prepared['plan']['owner'] = 'another/repository'
        self.assertFalse(self.complete(base, prepared)['ok'])
        prepared = checker.prepare_delivery(self.root, REV, self.meta['kind'], self.meta['id'], 'repository', self.name)
        self.meta['owner'] = 'role:other'
        self.meta['version'] += 1
        self.write_doc()
        self.assertFalse(self.complete(base, prepared)['ok'])

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


class CompactConformance(unittest.TestCase):
    def setUp(self):
        self.fixture = Conformance()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.git = self.fixture.git
        self.name = 'docs/FEATURE/PROVIDER_DNS_CHANGE_DETECTION.md'
        self.meta = {
            'schema': checker.POLICY['compact']['document_schema'],
            'id': 'provider-dns-change-detection', 'kind': 'feature',
            'version': 1, 'title': 'Detect provider DNS changes',
            'status': 'proposed', 'owner': 'subactor/example',
            'scope': 'repository', 'updated': '2026-09-14',
            'priority': 'P2', 'source_revision': 'b' * 40,
            'evidence': ['receipt:dns-regression']
        }
        self.write()

    def write(self, body=None):
        path = self.root / self.name
        path.parent.mkdir(parents=True, exist_ok=True)
        if body is None:
            body = '# DNS change detection\n' + '\n'.join(
                '<!-- docs:section ' + section + ' -->\nConcrete bounded observation.\n'
                for section in checker.POLICY['compact']['sections'])
        path.write_text('---\n' + json.dumps(self.meta) + '\n---\n' + body)
        (self.root / 'docs/README.md').write_text(
            '[Legacy](refactoring/publication.md)\n[DNS](' + self.name[5:] + ')\n')
        self.git('add', '.')

    def codes(self, **kwargs):
        return self.fixture.codes(**kwargs)

    def base(self):
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.org',
                 'commit', '-qm', 'baseline')
        return self.git('rev-parse', 'HEAD')

    def changelog(self, text):
        (self.root / 'CHANGELOG.md').write_text(text)
        self.git('add', 'CHANGELOG.md')

    def test_compact_and_legacy_coexist(self):
        self.assertEqual(self.codes(), set())

    def redirect(self, target=None, body=None):
        meta = {'schema': checker.POLICY['redirect_schema'], 'owner': 'subactor/example',
                'version': 2, 'updated': '2026-09-14', 'targets': [target or self.name]}
        path = self.root / 'docs/old-guide.md'
        path.write_text('---\n' + json.dumps(meta) + '\n---\n'
                        + (body or '# Old guide\n[Current guide](FEATURE/PROVIDER_DNS_CHANGE_DETECTION.md)\n'))
        self.git('add', '.')
        return path

    def test_legacy_map_preserves_entry_and_is_discovered(self):
        (self.root / 'docs/old-guide.md').write_text('# Old guide\nHistorical prose.')
        self.git('add', '.')
        base = self.base()
        self.redirect()
        self.assertEqual(self.codes(base=base), set())
        self.assertEqual(self.codes(), set())  # Structural audit without provenance.

    def test_new_map_cannot_invent_legacy_path(self):
        base = self.base()
        self.redirect()
        self.assertIn('DOCS_REDIRECT_BASE', self.codes(base=base))

    def test_map_cannot_hide_prose_or_external_destination(self):
        for body in ['New hidden report', '[External](https://example.org/guide.md)',
                     '[Alias](alias.md)', '[Broken](http://[bad)']:
            self.redirect(body=body)
            self.assertIn('DOCS_REDIRECT_BODY', self.codes())

    def test_map_targets_are_canonical_and_tracked(self):
        for target in ['docs/missing.md', 'docs/old-guide.md', '../outside.md']:
            self.redirect(target=target)
            self.assertIn('DOCS_REDIRECT_TARGET', self.codes())

    def test_map_requires_version_increment(self):
        self.redirect()
        base = self.base()
        path = self.redirect()
        path.write_text(path.read_text().replace('# Old guide', '# Renamed heading'))
        self.assertIn('DOCS_VERSION', self.codes(base=base))

    def test_non_string_schema_is_a_finding_not_a_crash(self):
        self.meta['schema'] = [checker.POLICY['compact']['document_schema']]
        self.write()
        self.assertIn('DOCS_METADATA', self.codes())

    def test_all_kinds_have_uppercase_paths(self):
        for kind, directory in checker.POLICY['compact']['directories'].items():
            path, index = checker.layout('subactor/example', kind, 'dns-change', True)
            self.assertEqual(str(path), 'docs/' + directory + '/DNS_CHANGE.md')
            self.assertEqual(index, 'docs/README.md')
        path, index = checker.layout('subactor/docs', 'analysis', 'dns-change', True)
        self.assertEqual(str(path), 'architecture/ANALYSIS/DNS_CHANGE.md')
        self.assertEqual(index, 'README.md')

    def test_wrong_case_and_urgent_directory_fail(self):
        old = self.root / self.name
        self.name = 'docs/URGENT/provider_dns_change_detection.md'
        old.unlink()
        self.write()
        self.assertTrue({'DOCS_FILENAME', 'DOCS_LOCATION'} <= self.codes())

    def test_priority_changes_preserve_path(self):
        self.meta['priority'] = 'P0'
        self.write()
        self.assertEqual(self.codes(), set())
        self.meta['priority'] = 'urgent'
        self.write()
        self.assertIn('DOCS_METADATA', self.codes())

    def test_compact_requires_owner_scope_and_no_unknown_fields(self):
        original = dict(self.meta)
        for key, value, expected in [
                ('owner', 'subactor/other', 'DOCS_OWNER'),
                ('scope', 'organization', 'DOCS_OWNER'),
                ('review_after', '2026-10-01', 'DOCS_METADATA'),
                ('source_revision', 'main', 'DOCS_METADATA')]:
            with self.subTest(key=key):
                self.meta = dict(original, **{key: value})
                self.write()
                self.assertIn(expected, self.codes())

    def test_compact_size_limits_include_metadata_and_code(self):
        for padding in ['\n' * 121, 'word ' * 601, 'ą' * 6200]:
            with self.subTest(size=len(padding)):
                self.write()
                path = self.root / self.name
                path.write_text(path.read_text() + padding)
                self.assertIn('DOCS_SIZE', self.codes())

    def test_compact_missing_section_fails(self):
        self.write(body='<!-- docs:section summary -->\nOnly a summary.')
        self.assertIn('DOCS_SECTIONS', self.codes())

    def test_compact_rejects_extra_sections(self):
        path = self.root / self.name
        path.write_text(path.read_text() + '\n<!-- docs:section extra -->\nMore prose.')
        self.assertIn('DOCS_SECTIONS', self.codes())

    def test_compact_version_increment_is_required(self):
        base = self.base()
        self.meta['title'] = 'Updated findings'
        self.write()
        self.assertIn('DOCS_VERSION', self.codes(base=base))
        self.meta['version'] = 2
        self.write()
        self.assertEqual(self.codes(base=base), set())

    def test_compact_metadata_removal_is_not_discovery_escape(self):
        base = self.base()
        (self.root / self.name).write_text('# No metadata')
        self.assertIn('DOCS_METADATA', self.codes(base=base))

    def test_compact_symlink_is_not_discovery_escape(self):
        base = self.base()
        path = self.root / self.name
        path.unlink()
        path.symlink_to(self.root / 'docs/refactoring/publication.md')
        self.assertIn('DOCS_LOCATION', self.codes(base=base))

    def test_prepare_compact_format_and_existing_default(self):
        result = checker.prepare_delivery(self.root, REV, 'bugfix', 'dns-timeout',
                    'repository', 'docs/BUGFIX/DNS_TIMEOUT.md', compact=True)
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['plan']['document_schema'], self.meta['schema'])
        result = checker.prepare_delivery(self.root, REV, 'feature', 'dns-timeout',
                    'repository', 'docs/FEATURE/DNS_TIMEOUT.md')
        self.assertFalse(result['ok'])

    def test_compact_cli_preparation(self):
        command = [sys.executable, str(checker.PACK / 'check.py'), '--root', str(self.root),
                   '--standard-revision', REV, '--prepare', '--format', 'v2',
                   '--kind', 'feature', '--id', 'dns-timeout', '--scope', 'repository',
                   '--deliverable', 'docs/FEATURE/DNS_TIMEOUT.md']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_changelog_inline_and_reference_links(self):
        self.changelog('- DNS [description](' + self.name + ').\n'
                       '- [Details][dns]\n[dns]: ' + self.name + '\n')
        self.assertEqual(self.codes(), set())

    def test_changelog_missing_untracked_deleted_and_symlink_targets(self):
        self.changelog('[DNS](' + self.name + ')')
        path = self.root / self.name
        path.unlink()
        self.assertIn('DOCS_CHANGELOG_LINK', self.codes())
        path.write_text('untracked target')
        self.git('rm', '--cached', '-f', self.name)
        self.assertIn('DOCS_CHANGELOG_LINK', self.codes())
        path.unlink()
        path.symlink_to(self.root / 'docs/refactoring/publication.md')
        self.git('add', self.name)
        self.assertIn('DOCS_CHANGELOG_LINK', self.codes())

    def test_changelog_ignores_external_links_and_code_examples(self):
        self.changelog('[Web](https://example.org/missing.md)\n'
                       '```markdown\n[Example](docs/FEATURE/EXAMPLE.md)\n```\n')
        self.assertEqual(self.codes(), set())

    def test_changelog_rejects_encoded_path_escape(self):
        self.changelog('[Escape](%2e%2e/outside.md)')
        self.assertIn('DOCS_CHANGELOG_LINK', self.codes())

    def test_uppercase_extension_cannot_escape_discovery(self):
        (self.root / self.name).rename(self.root / self.name.replace('.md', '.MD'))
        self.git('add', '.')
        self.assertIn('DOCS_LOCATION', self.codes())

    def test_distributed_example_conforms(self):
        self.git('remote', 'set-url', 'origin', 'https://github.com/wellmanifest/docs.git')
        self.fixture.adoption['repository'] = 'wellmanifest/docs'
        self.fixture.write_adoption()
        (self.root / self.fixture.name).unlink()
        (self.root / self.name).unlink()
        self.name = 'docs/ANALYSIS/COMPACT_DOCUMENTATION.md'
        path = self.root / self.name
        path.parent.mkdir(parents=True)
        path.write_text((checker.PACK.parent / 'ANALYSIS/COMPACT_DOCUMENTATION.md').read_text())
        (self.root / 'docs/README.md').write_text('[Analysis](ANALYSIS/COMPACT_DOCUMENTATION.md)')
        self.git('add', '.')
        self.assertEqual(self.codes(), set())

    def test_distributed_template_renders_valid_compact_document(self):
        template = (checker.PACK / 'templates/COMPACT.md').read_text()
        replacements = {
            'stable_slug': self.meta['id'], 'kind': 'feature',
            'one_sentence_title': 'Detect DNS changes', 'org_repo': 'subactor/example',
            'YYYY_MM_DD': '2026-09-14', 'full_source_commit': 'b' * 40,
            'immutable_evidence_reference': 'receipt:dns-regression',
            'problem_and_expected_or_observed_result': 'Detect changed provider addresses.',
            'one_topic_cause_or_decision_with_links_to_other_topics': 'Observe DNS on reload.',
            'acceptance_criterion_command_result_and_evidence_or_explicit_gap': 'Regression test pending.',
            'compatibility_rollback_owner_and_next_action_or_reasoned_not_applicable': 'Owner: subactor/example; revert the observer if needed.'
        }
        for key, value in replacements.items():
            template = template.replace('{{' + key + '}}', value)
        (self.root / self.name).write_text(template)
        self.assertEqual(self.codes(), set())


if __name__ == '__main__':
    unittest.main()
