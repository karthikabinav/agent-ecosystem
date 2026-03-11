# RFC v0: Agent-Native Ecosystem Platform Architecture

- **Status:** Draft (v0)
- **Authors:** Architecture Working Group
- **Date:** 2026-03-11
- **Audience:** Platform, infra, product, safety, and applied-agent teams
- **Scope:** Defines the initial architecture and contracts for an agent-native platform spanning identity/auth, tool gateway, memory, orchestration runtime, eval harness, observability, and policy/safety.

---

## 1) Motivation

Current agent systems are often assembled as loosely-coupled scripts with implicit contracts, weak policy boundaries, and ad hoc observability. This RFC proposes a coherent platform architecture with explicit interfaces and enforcement points so agents can be:

- **Composable** (tools, memory, and runtimes can evolve independently)
- **Safe-by-default** (policy and auth enforced on every side effect)
- **Evaluable** (offline and online quality/safety measurement)
- **Operable at scale** (traceable, debuggable, and auditable)

---

## 2) Goals / Non-Goals

### Goals

1. Define minimal v0 contracts between core services.
2. Standardize identity and authorization for users, agents, and tools.
3. Establish a tool invocation path with policy enforcement and auditability.
4. Provide a memory architecture supporting short-term context + long-term retrieval.
5. Define orchestration runtime semantics (turn lifecycle, delegation, retries, budgets).
6. Introduce eval harness for pre-merge and in-prod quality/safety checks.
7. Define observability primitives for traces, logs, metrics, and replays.

### Non-Goals (v0)

- Multi-region active-active consistency guarantees.
- Full formal verification of policies.
- Universal tool schema standardization across all external providers.
- End-user product UX specification.

---

## 3) High-Level Architecture

```text
[Client surfaces]
   |  (chat, API, workflow triggers)
   v
[Identity/AuthN/AuthZ] ---> [Policy Engine]
   |                              |
   v                              |
[Orchestration Runtime] ----------+
   |        |           |
   |        |           +--> [Memory Service]
   |        +--------------> [Tool Gateway]
   |                            |
   |                            +--> [External/Internal Tools]
   |
   +--> [Observability Pipeline] --> [Trace store / metrics / logs / replay]
   |
   +--> [Eval Harness] (offline suites + online canaries + regressions)
```

### Core Principle

Every side effect (tool write, message send, file mutation, external API action) flows through:

1. **Identity binding** (who/what initiated)
2. **Policy check** (allowed?)
3. **Execution with scoped credentials**
4. **Structured audit event emission**

---

## 4) Identity & Auth

### 4.1 Principal Model

All requests execute as a **Principal** with immutable identity claims:

- `user` principal (human)
- `agent` principal (automation identity)
- `subagent` principal (ephemeral child of agent)
- `service` principal (platform internal)

Each principal gets a globally unique `principal_id` + typed namespace.

### 4.2 Credential Types

- **Session tokens** (short-lived, user initiated)
- **Agent run tokens** (ephemeral, minted per run/turn)
- **Tool capability tokens** (scoped to tool/action/resource/time)
- **Service-to-service mTLS/JWT** for internal APIs

### 4.3 Authorization

Hybrid model:

- **RBAC** for coarse roles (e.g., maintainer/operator)
- **ABAC/Rego-style policies** for contextual controls (channel, tool action, sensitivity level, risk score)
- **Delegation constraints**: subagents can only inherit subset scopes of parent

### 4.4 v0 Requirements

- Default-deny for tool writes
- Explicit allowlists per action family
- Token TTL <= run lifetime
- Full principal chain in every audit event

---

## 5) Tool Gateway

### 5.1 Responsibilities

Tool Gateway is the sole execution boundary for tool calls. It handles:

- Request validation (schema + version)
- AuthZ + policy hook
- Rate limiting / concurrency control
- Credential brokering (just-in-time scoped creds)
- Retry/idempotency semantics
- Result normalization
- Audit emission

### 5.2 Tool Contract (v0)

`ToolRequest`:

```json
{
  "request_id": "uuid",
  "principal": {"principal_id": "...", "type": "agent|subagent|user"},
  "run_context": {"run_id": "...", "turn_id": "..."},
  "tool": {"name": "message", "action": "send", "version": "v1"},
  "input": {},
  "idempotency_key": "optional",
  "deadline_ms": 30000
}
```

`ToolResult`:

```json
{
  "request_id": "uuid",
  "status": "ok|error|denied|timeout",
  "output": {},
  "error": {"code": "...", "message": "..."},
  "usage": {"latency_ms": 1234, "retries": 0},
  "policy": {"decision_id": "...", "applied_rules": ["..."]}
}
```

### 5.3 Safety Hooks

- Pre-exec policy check (hard deny, soft require-confirmation)
- Post-exec classifier hooks (data loss, exfil, PII leakage)
- Tamper-evident audit chain hash (optional v0.5)

---

## 6) Memory Architecture

### 6.1 Memory Types

1. **Working memory**: run/turn-local context (ephemeral)
2. **Session memory**: short-horizon continuity
3. **Long-term memory**: curated durable facts/preferences/decisions
4. **Knowledge memory**: indexed docs/artifacts/code
5. **Episodic memory**: past trajectories and outcomes

### 6.2 Memory Service APIs (v0)

- `memory.write(event|fact|summary, scope, ttl, provenance)`
- `memory.search(query, scope_filters, top_k)`
- `memory.get(id)`
- `memory.promote(candidate_id -> long_term)`
- `memory.forget(id|selector)` (policy-controlled)

### 6.3 Data & Governance

Required metadata per record:

- `owner_principal`
- `visibility_scope`
- `source_trace_id`
- `confidence`
- `created_at`, `expires_at`
- `sensitivity_label`

Retention defaults:

- Working/session memory: bounded TTL
- Long-term memory: explicit promotion only
- Hard-delete + tombstone for compliance paths

---

## 7) Orchestration Runtime

### 7.1 Turn Lifecycle

1. Ingest input/event
2. Build execution context (identity + memory retrieval + policy context)
3. Plan (single-shot or multi-step)
4. Execute actions/tool calls
5. Observe outcomes
6. Reflect/update memory
7. Emit final response + telemetry

### 7.2 Runtime Semantics

- Deterministic state machine for run/turn transitions
- Configurable budgets (tokens, wall-clock, tool calls, spend)
- Interruptibility (human override, policy stop, kill switch)
- Structured retries with backoff + idempotency keys
- Delegation API: spawn subagent with narrowed scopes + explicit objective

### 7.3 Failure Domains

- Tool failure should not corrupt run state
- Partial completion should be persisted with resumable checkpoints
- Policy-denied actions should return typed denial reasons

---

## 8) Eval Harness

### 8.1 Objectives

Measure quality, reliability, and safety before and after deployment.

### 8.2 Eval Layers

1. **Unit evals**: tool adapters, policy decisions, parsers
2. **Scenario evals**: multi-turn task trajectories
3. **Regression suites**: golden tasks + historical failures
4. **Safety evals**: prompt injection, exfiltration attempts, unsafe tool usage
5. **Online evals**: canary slices, shadow runs, A/B policies

### 8.3 Scorecard (v0)

- Task success rate
- Cost and latency distribution
- Tool error/denial rate
- Safety violation rate (by severity)
- Human override/escalation frequency
- Memory precision/contamination rate

### 8.4 Release Gates

- Block deploy if safety regression > threshold
- Warn on latency/cost regressions beyond SLO budget
- Require approval for policy rule changes impacting write actions

---

## 9) Observability

### 9.1 Unified Telemetry Model

Each run emits correlated:

- **Traces** (run -> turn -> step -> tool spans)
- **Logs** (structured JSON events)
- **Metrics** (latency, throughput, errors, cost)
- **Artifacts** (prompts, responses, tool I/O snapshots with redaction)

### 9.2 Required IDs

- `trace_id`, `span_id`
- `run_id`, `turn_id`, `step_id`
- `principal_id`, `session_id`
- `policy_decision_id`, `tool_request_id`

### 9.3 Replay & Debug

- Deterministic replay mode using captured model/tool fixtures
- Diff tooling between two runs (prompt, plan, tool outputs, policy decisions)
- Redaction-at-ingest for sensitive content

---

## 10) Policy & Safety

### 10.1 Enforcement Planes

- **Input plane:** sanitize and classify inbound content
- **Planning plane:** constrain forbidden strategies/actions
- **Execution plane:** enforce tool/action/resource policies
- **Output plane:** redact or block disallowed responses

### 10.2 Policy Decision Outcomes

- `allow`
- `deny`
- `allow_with_confirmation`
- `allow_with_redaction`
- `escalate_to_human`

### 10.3 v0 Safety Invariants

1. No side-effecting tool call without policy evaluation.
2. No privileged delegation without explicit scope narrowing.
3. No persistence of sensitive memory without sensitivity tag + retention rule.
4. Every denial/escalation must be explainable via decision trace.

---

## 11) Contract Boundaries

This section is normative for v0.

### 11.1 Runtime ↔ Tool Gateway

- Runtime must provide principal chain + run context.
- Tool Gateway must return typed status and policy metadata.
- Tool calls should be idempotent where feasible; otherwise explicitly marked non-idempotent.

### 11.2 Runtime ↔ Memory Service

- Runtime must provide provenance on writes.
- Memory service must enforce visibility scope on reads.
- Promotion to long-term memory is explicit action, never implicit by volume.

### 11.3 Runtime ↔ Policy Engine

- Runtime sends `ActionIntent` before execution.
- Policy returns decision + rationale + obligations (confirm/redact/escalate).
- Policy decisions are immutable and auditable.

### 11.4 Eval Harness ↔ Platform

- Harness consumes replayable traces + labeled outcomes.
- Harness outputs versioned scorecards + regression deltas.
- Release controller consumes gate outcomes as hard/soft checks.

### 11.5 Observability ↔ All Services

- All services must emit schema-versioned telemetry.
- Trace context propagation is mandatory across all RPC boundaries.

---

## 12) Minimal Data Schemas (v0)

### 12.1 ActionIntent

```json
{
  "intent_id": "uuid",
  "principal_chain": ["user:...", "agent:...", "subagent:..."],
  "action": {"domain": "tool", "name": "message.send"},
  "resource": {"type": "discord_channel", "id": "1480944778467217479"},
  "risk": {"level": "medium", "labels": ["external_write"]},
  "context": {"run_id": "...", "turn_id": "..."}
}
```

### 12.2 PolicyDecision

```json
{
  "decision_id": "uuid",
  "intent_id": "uuid",
  "result": "allow|deny|allow_with_confirmation|allow_with_redaction|escalate_to_human",
  "reason_codes": ["RULE_123"],
  "obligations": ["require_user_confirmation"],
  "expires_at": "2026-03-11T05:30:00Z"
}
```

---

## 13) Rollout Plan

### Phase 0 (v0 bootstrap)

- Implement contracts + schema registry
- Stand up policy decision point in tool path
- Emit baseline tracing + audit events
- Launch initial eval suite (golden tasks + safety probes)

### Phase 1

- Add deterministic replay tooling
- Add memory promotion workflows + curation UI/API
- Add canary deploy gates tied to eval scorecards

### Phase 2

- Cross-agent memory sharing with explicit trust policies
- Fine-grained cost/perf optimizers in runtime planner
- Cryptographic audit attestations

---

## 14) Risks

- Policy latency can bottleneck tool throughput.
- Overly strict policies reduce task completion.
- Memory contamination can degrade planning quality.
- Incomplete telemetry breaks root-cause analysis.

Mitigations: caching for low-risk decisions, staged policy rollout, memory validation + confidence scoring, telemetry conformance tests.

---

## 15) Open Decisions

1. **Policy engine implementation:** Rego/OPA vs Cedar vs custom DSL?
2. **Identity substrate:** central IAM service vs embedded auth in runtime?
3. **Memory backend split:** single multi-model store vs separate vector + relational + object stores?
4. **Replay fidelity target:** deterministic-enough vs strict determinism with recorded model outputs?
5. **Delegation limits:** static scope templates vs dynamic per-task synthesis?
6. **Safety posture:** default `allow_with_confirmation` vs stricter `deny` for external writes in early rollout?
7. **Eval governance:** who owns thresholds and sign-off (platform vs applied teams)?

---

## 16) Appendix: v0 Success Criteria

- 100% of side-effecting tool calls include policy decision IDs.
- 95%+ run traces have complete span linkage across runtime/tool/memory/policy.
- Regression suite runs on every release candidate.
- External write actions achieve auditable principal chain coverage.
- Incident triage can reconstruct any run with replay artifacts within 15 minutes.

---

**End of RFC v0**
