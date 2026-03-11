# Agent Ecosystem — Week 1 Foundation

[![Lint](https://github.com/karthikabinav/agent-ecosystem/actions/workflows/lint.yml/badge.svg)](https://github.com/karthikabinav/agent-ecosystem/actions/workflows/lint.yml)

This repository is the initial scaffold for an agent-software ecosystem.

## Structure

- `ecosystem-core/` — shared primitives, protocols, and core libraries
- `agent-platform/` — runtime/platform services and orchestration surfaces
- `agents/workops/` — operations-focused agents (execution, delivery, runbooks)
- `agents/knowledgeops/` — knowledge-focused agents (indexing, retrieval, memory)
- `ops-playbooks/` — operational playbooks, SRE/incident guides, SOPs
- `experiments/` — fast iteration and research spikes
- `.github/workflows/` — CI placeholders (lint/test/security)

## Week 1 Goals

1. Establish repository shape and ownership boundaries
2. Stand up baseline CI checks (lint, tests, security scanning)
3. Define release cadence and quality gates

## Getting Started

- Add language/tooling decisions (Python/TS/etc.) per module
- Replace CI placeholders with runnable project-specific jobs
- Add CODEOWNERS, contribution guidelines, and branch protections

