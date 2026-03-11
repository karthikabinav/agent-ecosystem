# Release Train Notes (Week 1)

## Purpose
Create predictable delivery by moving all components on a regular release cadence.

## Proposed Cadence
- **Weekly train**: every Friday UTC
- **Cut window**: Thu 18:00 UTC
- **Stabilization**: Thu cut → Fri release

## Initial Quality Gates
- Lint passing
- Unit/integration test suite passing
- Security scan passing (dependency + static checks)
- Release notes updated for changed components

## Branching (Initial)
- `main` as protected trunk
- Short-lived feature branches
- PR required with at least one approval

## Ownership (to finalize)
- ecosystem-core: TBD
- agent-platform: TBD
- workops agents: TBD
- knowledgeops agents: TBD
- ops-playbooks: TBD
- experiments: TBD

## Next Actions
1. Decide default language/toolchain per directory
2. Implement real lint/test/security jobs
3. Add semantic versioning + changelog flow
4. Enable artifact publishing for releasable modules
