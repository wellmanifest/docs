#!/usr/bin/env python3
"""Validate and generate inert wellmanifest/docs adopter readiness receipts."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCHEMA = "wellmanifest.docs/readiness/v1"
PHASES = ("unavailable", "unadopted", "configured", "deployed", "verified")
RECEIPT_FIELDS = {
    "schema", "repository", "standard", "standard_version", "standard_revision",
    "policy_sha256", "checker_sha256", "covered_roots", "base_sha", "head_sha",
    "phase", "observed_at", "evidence", "compatibility_review", "generator",
}
EVIDENCE_PREFIX = ("repo://", "github://", "receipt://", "artifact://", "knowledge://")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
ROOT = re.compile(r"^[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*$")
WHEN = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
GENERATOR = re.compile(r"^[A-Za-z0-9_.-]+$")


def _error(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def validate_receipt(receipt: object, previous: object | None = None) -> list[dict[str, str]]:
    """Return deterministic findings; this function grants no deployment authority."""
    findings: list[dict[str, str]] = []
    if not isinstance(receipt, dict):
        return [_error("DOCS_READINESS_SCHEMA", "Receipt must be an object")]
    if set(receipt) != RECEIPT_FIELDS:
        findings.append(_error("DOCS_READINESS_SCHEMA", "Receipt fields must match the v1 contract exactly"))

    def require(condition: bool, code: str, message: str) -> None:
        if not condition:
            findings.append(_error(code, message))

    require(receipt.get("schema") == SCHEMA, "DOCS_READINESS_SCHEMA", "Unsupported readiness schema")
    require(isinstance(receipt.get("repository"), str) and REPO.fullmatch(receipt["repository"] or "") is not None,
            "DOCS_READINESS_REPOSITORY", "repository must be an org/repo identifier")
    require(isinstance(receipt.get("standard"), str) and bool(receipt["standard"]),
            "DOCS_READINESS_STANDARD", "standard must be a non-empty identifier")
    require(isinstance(receipt.get("standard_version"), str) and VERSION.fullmatch(receipt["standard_version"] or "") is not None,
            "DOCS_READINESS_VERSION", "standard_version must be semantic MAJOR.MINOR.PATCH")
    for key, pattern in (("standard_revision", SHA40), ("base_sha", SHA40), ("head_sha", SHA40),
                         ("policy_sha256", SHA256), ("checker_sha256", SHA256)):
        require(isinstance(receipt.get(key), str) and pattern.fullmatch(receipt[key] or "") is not None,
                "DOCS_READINESS_DIGEST", f"{key} must be a lowercase immutable digest")
    roots = receipt.get("covered_roots")
    require(isinstance(roots, list) and 1 <= len(roots) <= 128 and len(set(roots)) == len(roots)
            and all(isinstance(item, str) and ROOT.fullmatch(item) is not None and ".." not in item.split("/")
                    for item in roots),
            "DOCS_READINESS_ROOTS", "covered_roots must be unique, relative, non-empty paths")
    phase = receipt.get("phase")
    require(phase in PHASES, "DOCS_READINESS_PHASE", "phase must be one of the five readiness levels")
    observed = receipt.get("observed_at")
    require(isinstance(observed, str) and WHEN.fullmatch(observed or "") is not None,
            "DOCS_READINESS_TIME", "observed_at must be a UTC second timestamp")

    evidence = receipt.get("evidence")
    if not isinstance(evidence, dict) or set(evidence) != set(PHASES):
        findings.append(_error("DOCS_READINESS_EVIDENCE", "evidence must contain each phase exactly once"))
        evidence = {}
    for name in PHASES:
        items = evidence.get(name)
        valid = (isinstance(items, list) and len(items) <= 64 and len(set(items)) == len(items)
                 and all(isinstance(item, str) and 0 < len(item) <= 512
                         and "\n" not in item and item.startswith(EVIDENCE_PREFIX) for item in items))
        require(valid, "DOCS_READINESS_EVIDENCE", f"evidence.{name} must contain safe unique references")
    if phase in PHASES and isinstance(evidence, dict):
        current = evidence.get(phase, [])
        require(bool(current), "DOCS_READINESS_EVIDENCE", f"current phase {phase} requires evidence")
        later = PHASES[PHASES.index(phase) + 1:] if phase in PHASES else ()
        for name in later:
            require(evidence.get(name) == [], "DOCS_READINESS_EVIDENCE", f"future phase {name} must remain empty")

    review = receipt.get("compatibility_review")
    if not isinstance(review, dict) or set(review) != {"required", "status", "reviewer", "evidence"}:
        findings.append(_error("DOCS_READINESS_REVIEW", "compatibility_review must match the v1 contract exactly"))
        review = {}
    required = review.get("required")
    status = review.get("status")
    review_evidence = review.get("evidence")
    require(isinstance(required, bool), "DOCS_READINESS_REVIEW", "compatibility_review.required must be boolean")
    require(status in {"not-required", "pending", "accepted", "rejected"},
            "DOCS_READINESS_REVIEW", "compatibility_review.status is invalid")
    require(review.get("reviewer") is None or (isinstance(review.get("reviewer"), str)
                                                and 0 < len(review["reviewer"]) <= 200),
            "DOCS_READINESS_REVIEW", "compatibility_review.reviewer must be null or a bounded name")
    require(isinstance(review_evidence, list) and len(review_evidence) <= 64
            and len(set(review_evidence)) == len(review_evidence)
            and all(isinstance(item, str) and item.startswith(EVIDENCE_PREFIX) and "\n" not in item
                    for item in review_evidence),
            "DOCS_READINESS_REVIEW", "compatibility_review.evidence must contain safe references")
    if required is True:
        require(status == "accepted" and isinstance(review.get("reviewer"), str) and bool(review.get("reviewer"))
                and bool(review_evidence), "DOCS_READINESS_REVIEW",
                "A required compatibility review must be accepted by a named reviewer with evidence")
    else:
        require(status == "not-required" and review.get("reviewer") is None and review_evidence == [],
                "DOCS_READINESS_REVIEW", "A non-required review must be explicitly empty")

    generator = receipt.get("generator")
    require(isinstance(generator, dict) and set(generator) == {"id", "version"}
            and isinstance(generator.get("id"), str) and GENERATOR.fullmatch(generator.get("id") or "") is not None
            and isinstance(generator.get("version"), str) and 0 < len(generator["version"]) <= 80,
            "DOCS_READINESS_GENERATOR", "generator must identify a bounded deterministic producer")

    if isinstance(previous, dict):
        require(previous.get("repository") == receipt.get("repository"), "DOCS_READINESS_CHAIN", "Receipt repository differs from previous evidence")
        require(previous.get("covered_roots") == receipt.get("covered_roots"), "DOCS_READINESS_CHAIN", "covered_roots changed without a new receipt chain")
        if previous.get("phase") in PHASES and phase in PHASES:
            require(PHASES.index(phase) >= PHASES.index(previous["phase"]),
                    "DOCS_READINESS_CHAIN", "Readiness phase cannot regress")
        same_version_changed_source = (previous.get("standard_version") == receipt.get("standard_version")
                                       and previous.get("standard_revision") != receipt.get("standard_revision"))
        if same_version_changed_source:
            require(required is True and status == "accepted", "DOCS_READINESS_REVIEW",
                    "A same-version source change requires an accepted compatibility review")
        if previous.get("standard_version") == receipt.get("standard_version") and previous.get("standard_revision") == receipt.get("standard_revision"):
            require(required is False, "DOCS_READINESS_REVIEW", "Unchanged source must not invent a compatibility review")
    return findings


def build_receipt(*, repository: str, standard: str, standard_version: str,
                  standard_revision: str, policy_sha256: str, checker_sha256: str,
                  covered_roots: list[str], base_sha: str, head_sha: str, phase: str,
                  observed_at: str, evidence: dict[str, list[str]], generator_id: str,
                  generator_version: str, compatibility_review: dict[str, object] | None = None) -> dict[str, object]:
    """Build a canonical receipt; callers must validate it before persistence."""
    review = compatibility_review or {"required": False, "status": "not-required", "reviewer": None, "evidence": []}
    receipt = {
        "schema": SCHEMA, "repository": repository, "standard": standard,
        "standard_version": standard_version, "standard_revision": standard_revision,
        "policy_sha256": policy_sha256, "checker_sha256": checker_sha256,
        "covered_roots": list(covered_roots), "base_sha": base_sha, "head_sha": head_sha,
        "phase": phase, "observed_at": observed_at, "evidence": {key: list(evidence.get(key, [])) for key in PHASES},
        "compatibility_review": review, "generator": {"id": generator_id, "version": generator_version},
    }
    return receipt


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise SystemExit(f"Cannot decode {path}: {type(error).__name__}") from error


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="validate a receipt and optional previous receipt")
    validate.add_argument("--receipt", type=Path, required=True)
    validate.add_argument("--previous", type=Path)
    generate = sub.add_parser("generate", help="emit a deterministic receipt to stdout")
    for name in ("repository", "standard", "standard-version", "standard-revision", "policy-sha256", "checker-sha256", "base-sha", "head-sha", "phase", "observed-at", "generator-id", "generator-version"):
        generate.add_argument("--" + name, required=True)
    generate.add_argument("--covered-root", action="append", required=True)
    generate.add_argument("--evidence", action="append", default=[], metavar="PHASE=REFERENCE")
    generate.add_argument("--review-required", action="store_true")
    generate.add_argument("--review-status", choices=["not-required", "pending", "accepted", "rejected"], default="not-required")
    generate.add_argument("--reviewer")
    generate.add_argument("--review-evidence", action="append", default=[])
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "validate":
        findings = validate_receipt(_read_json(args.receipt), _read_json(args.previous) if args.previous else None)
        print(json.dumps({"ok": not findings, "findings": findings}, indent=2, sort_keys=True))
        return 0 if not findings else 1
    evidence = {key: [] for key in PHASES}
    for item in args.evidence:
        if "=" not in item:
            print("evidence must use PHASE=REFERENCE", file=sys.stderr)
            return 2
        key, reference = item.split("=", 1)
        if key not in evidence:
            print("evidence phase is unknown", file=sys.stderr)
            return 2
        evidence[key].append(reference)
    receipt = build_receipt(repository=args.repository, standard=args.standard,
                             standard_version=args.standard_version, standard_revision=args.standard_revision,
                             policy_sha256=args.policy_sha256, checker_sha256=args.checker_sha256,
                             covered_roots=args.covered_root, base_sha=args.base_sha, head_sha=args.head_sha,
                             phase=args.phase, observed_at=args.observed_at, evidence=evidence,
                             generator_id=args.generator_id, generator_version=args.generator_version,
                             compatibility_review={"required": args.review_required, "status": args.review_status,
                                                   "reviewer": args.reviewer, "evidence": args.review_evidence})
    findings = validate_receipt(receipt)
    if findings:
        print(json.dumps({"ok": False, "findings": findings}, indent=2, sort_keys=True))
        return 1
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
