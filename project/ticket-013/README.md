# Ticket 013: Separate verified standard copies from consumer document discovery

- **ID**: ticket-013
- **Owner**: tom-sapletta-com
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-09-15

## Goal and scope

Fix Docs adoption in consumers with immutable managed standard documentation. Add an explicit trusted copy inventory with hash/path validation, without allowing consumer reports to escape completion.

## Acceptance criteria

- [x] AC-01: Verified external standard copies are reported separately; wrong digest, unsafe path and explicit result exclusions fail.
- [x] AC-02: Preparation and completion bind the same inventory; all regressions and governance pass.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
