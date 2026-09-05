#!/usr/bin/env python3
"""Read-only placement and structure checks; not semantic or authority approval."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
from pathlib import Path

PACK = Path(__file__).resolve().parent
POLICY_BYTES = (PACK / 'policy.json').read_bytes()
POLICY = json.loads(POLICY_BYTES)
POLICY_SHA256 = hashlib.sha256(POLICY_BYTES).hexdigest()
SHA = re.compile(r'^[0-9a-f]{40}$')
REPO = re.compile(r'^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')
MARKER = re.compile(r'<!-- docs:section ([a-z_]+) -->')


def origin(root):
    result = subprocess.run(['git', 'remote', 'get-url', 'origin'], cwd=root,
                            capture_output=True, text=True, check=False)
    match = re.search(r'github\.com[:/]([\w.-]+/[\w.-]+?)(?:\.git)?$', result.stdout.strip())
    return match.group(1) if result.returncode == 0 and match else None


def tracked(root):
    result = subprocess.run(['git', 'ls-files', '-z'], cwd=root, capture_output=True, check=False)
    if result.returncode:
        raise ValueError('DOCS_GIT_REQUIRED')
    return set(result.stdout.decode().split('\0')) - {''}


def layout(repository, kind, slug):
    profile = POLICY['profile']
    override = profile['repository_overrides'].get(repository, {})
    root = override.get('docs_root', profile['docs_root'])
    directory = POLICY['kinds'][kind]['directory']
    return Path(root) / override.get('prefix', '') / directory / (slug + '.md'), override.get('index', profile['index'])


def metadata(text):
    match = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)', text, re.S)
    if not match:
        raise ValueError('DOCS_METADATA_REQUIRED')
    value = json.loads(match.group(1))
    if not isinstance(value, dict):
        raise ValueError('DOCS_METADATA_OBJECT_REQUIRED')
    return value, text[match.end():]


def valid_value(kind, value):
    if kind == 'positive_integer':
        return type(value) is int and value > 0
    if kind in {'repositories', 'references'}:
        if not isinstance(value, list) or not value or len(value) > 128:
            return False
        if not all(isinstance(v, str) and v.strip() == v and v for v in value):
            return False
        if len(set(value)) != len(value):
            return False
        if kind == 'repositories':
            return all(REPO.fullmatch(v) for v in value)
        return all(v.startswith(('repo://', 'github://', 'https://', 'receipt:', 'artifact://', 'knowledge://'))
                   and not re.search(r'://[^/]*@|[?&](token|key|password)=', v, re.I) for v in value)
    if not isinstance(value, str) or value.strip() != value or not value:
        return False
    if kind == 'slug':
        return bool(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value))
    if kind == 'sha40':
        return bool(SHA.fullmatch(value))
    if kind == 'kind':
        return value in POLICY['kinds']
    if kind == 'status':
        return value in POLICY['statuses']
    if kind == 'date':
        try:
            return dt.date.fromisoformat(value).isoformat() == value
        except ValueError:
            return False
    return kind == 'string'


def safe_path(root, path):
    path = Path(path)
    candidate = path if path.is_absolute() else root / path
    try:
        relative = candidate.relative_to(root)
        if '..' in relative.parts:
            return None
        current = root
        for part in relative.parts:
            current /= part
            if current.is_symlink():
                return None
        candidate.resolve().relative_to(root)
    except ValueError:
        return None
    return relative


def check(root, revision, deliverables=(), today=None, base=None):
    root = Path(root).resolve()
    findings, warnings = [], []
    def fail(code, path, message):
        findings.append({'code': code, 'path': str(path), 'message': message})
    if not SHA.fullmatch(revision):
        raise ValueError('Trusted standard revision must be a full immutable SHA')
    repository = origin(root)
    try:
        files = tracked(root)
    except ValueError as error:
        return {'ok': False, 'repository': repository, 'findings': [{'code': str(error)}], 'warnings': []}
    config_path = '.governance/docs.json'
    if safe_path(root, config_path) is None:
        fail('DOCS_ADOPTION', config_path, 'Adoption path must not use symlinks')
        config = {}
    else:
        try:
            config = json.loads((root / config_path).read_text())
        except (OSError, ValueError):
            config = {}
    expected = {'schema': POLICY['adoption_schema'], 'repository': repository,
                'standard': POLICY['id'], 'source_revision': revision, 'policy_sha256': POLICY_SHA256}
    if not repository or config != expected or config_path not in files:
        fail('DOCS_ADOPTION', config_path, 'Missing or divergent tracked adoption; pin the trusted revision and policy digest')
    index = layout(repository, "information", "placeholder")[1]
    if safe_path(root, index) is None or index not in files or not (root / index).is_file():
        fail("DOCS_INDEX", index, "Tracked documentation index required for every adopter")
    if base and not SHA.fullmatch(base):
        raise ValueError("Base must be a full commit SHA")
    if base:
        resolved = subprocess.run(['git', 'cat-file', '-t', base], cwd=root, capture_output=True, text=True, check=False)
        if resolved.returncode or resolved.stdout.strip() != 'commit':
            fail('DOCS_BASE', base, 'Trusted base commit must be available locally')
    selected = set()
    for declared in deliverables:
        relative = safe_path(root, declared)
        if relative is None:
            fail('DOCS_LOCATION', declared, 'Deliverable must remain inside its owning repository without symlinks')
        else:
            selected.add(relative.as_posix())
    for name in files:
        if not name.endswith('.md') or safe_path(root, name) is None:
            continue
        path = root / name
        if path.is_file() and path.read_text(errors='replace').startswith('---') and POLICY['document_schema'] in path.read_text(errors='replace')[:8192]:
            selected.add(name)
    ids = set()
    for name in sorted(selected):
        if safe_path(root, name) is None:
            fail('DOCS_LOCATION', name, 'Symlink or escaped path')
            continue
        if name not in files:
            fail('DOCS_UNTRACKED', name, 'Stage the documentation in Git before completing delivery')
        try:
            text = (root / name).read_text()
            meta, body = metadata(text)
        except (OSError, ValueError) as error:
            fail('DOCS_METADATA', name, type(error).__name__)
            continue
        if '{{' in text or '}}' in text:
            fail('DOCS_PLACEHOLDER', name, 'Replace template placeholders with actual findings or a reasoned not-applicable statement')
        if base:
            old = subprocess.run(['git', 'show', base + ':' + name], cwd=root,
                                 capture_output=True, text=True, check=False)
            if old.returncode == 0 and old.stdout != text:
                try:
                    previous, _ = metadata(old.stdout)
                    if previous.get('schema') == POLICY['document_schema'] and type(meta.get('version')) is int and type(previous.get('version')) is int and meta['version'] <= previous['version']:
                        fail('DOCS_VERSION', name, 'Changed document must increase its declared version')
                except ValueError:
                    pass
        fields = POLICY['metadata']
        if set(meta) != set(fields) or any(not valid_value(t, meta.get(k)) for k, t in fields.items()) or meta.get('schema') != POLICY['document_schema']:
            fail('DOCS_METADATA', name, 'Metadata fields, types or values violate document/v1')
            continue
        if meta['id'] in ids:
            fail('DOCS_DUPLICATE_ID', name, 'One canonical owner and one document for this id')
        ids.add(meta['id'])
        expected_path, index = layout(repository, meta['kind'], meta['id'])
        if Path(name) != expected_path:
            fail('DOCS_LOCATION', name, 'Expected ' + expected_path.as_posix())
        if meta['affected_repositories'] != [repository] and repository != POLICY['profile']['cross_repository_home']:
            fail('DOCS_OWNER', name, 'Cross-repository deliverables belong to subactor/docs; reference dependencies in scope instead')
        if not meta['created'] <= meta['updated'] <= meta['review_after']:
            fail('DOCS_DATES', name, 'Expected created <= updated <= review_after')
        if dt.date.fromisoformat(meta['review_after']) < (today or dt.date.today()):
            warnings.append({'code': 'DOCS_REVIEW_DUE', 'path': name})
        matches = list(MARKER.finditer(body))
        sections = [m.group(1) for m in matches]
        required = POLICY['kinds'][meta['kind']]['sections']
        if len(sections) != len(set(sections)) or any(s not in sections for s in required):
            fail('DOCS_SECTIONS', name, 'Required section markers must each occur once')
        for i, match in enumerate(matches):
            content = body[match.end():matches[i+1].start() if i+1 < len(matches) else len(body)]
            content = re.sub(r'^\s*#+[^\n]*$', '', content, flags=re.M).strip()
            if not content:
                fail('DOCS_EMPTY_SECTION', name, match.group(1))
        if safe_path(root, index) is None or index not in files or not (root / index).is_file():
            fail('DOCS_INDEX', index, 'Tracked documentation index required')
        else:
            index_text = (root / index).read_text()
            relative_link = expected_path.relative_to(Path(index).parent).as_posix()
            if not re.search(r'\]\(' + re.escape(relative_link) + r'(?:#[^)]*)?\)', index_text):
                fail('DOCS_INDEX', name, 'Link the canonical document from ' + index)
    return {'ok': not findings, 'repository': repository, 'documents_checked': len(selected),
            'scope': POLICY['adoption_scope'], 'findings': findings, 'warnings': warnings}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    targets = p.add_mutually_exclusive_group(required=True)
    targets.add_argument('--root', type=Path)
    targets.add_argument('--fleet', type=Path, help='Read-only audit of immediate local subactor/* Git checkouts')
    p.add_argument('--standard-revision', required=True, help='Full revision selected by trusted CI, never by the candidate document')
    p.add_argument('--base', help='Trusted base SHA for version-increment checks')
    p.add_argument('--deliverable', action='append', default=[])
    args = p.parse_args()
    if args.fleet:
        if args.deliverable or args.base:
            p.error('--deliverable applies to a single --root')
        reports = [check(path, args.standard_revision) for path in sorted(args.fleet.iterdir())
                   if path.is_dir() and not path.is_symlink() and (path / '.git').exists()
                   and (origin(path) or '').startswith(POLICY['profile']['required_namespace'])]
        result = {'ok': bool(reports) and all(r['ok'] for r in reports), 'coverage': 'local-checkouts-only',
                  'repositories_checked': len(reports), 'reports': reports}
    else:
        result = check(args.root, args.standard_revision, args.deliverable, base=args.base)
    print(json.dumps(result, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
