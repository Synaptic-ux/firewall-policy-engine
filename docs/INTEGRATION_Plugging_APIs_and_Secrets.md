# Integration: Plugging APIs and Secrets

## 1) Purpose and audience
This document is for:
- engine integrators,
- platform engineering teams,
- security automation engineers,
- governance/control-plane implementers.

It explains how to wire real client APIs and secret sources into the engine through adapters, while keeping core workflow logic unchanged.

It covers:
- integration patterns aligned to canonical contracts,
- adapter responsibilities by port,
- runtime secret injection models,
- onboarding and go-live controls.

It does **not** cover:
- production credential values,
- client-specific endpoint inventories,
- vendor hardening runbooks,
- environment-specific network implementation details.

## 2) Integration principles

### 2.1 Contract-first intake
All inbound requests must be normalized into canonical contracts before core processing:
- `ChangeRequest`
- `MappingReport`

The engine should not process client-native payloads directly.

### 2.2 Ports/adapters pattern
Core workflow logic depends on abstract ports (interfaces). Adapters implement environment-specific behavior for ticketing, firewall, topology/policy, secrets, artifacts, and observability.

This isolates:
- client schema variance,
- API protocol differences,
- authentication mechanism differences,
- deployment model differences.

### 2.3 Least privilege and segregation of duties
Integration identities must follow least privilege and governance controls:
- requester/approver/executor duties remain separated,
- adapter identities only receive minimal API scopes,
- apply operations are blocked unless approval and policy gates pass.

### 2.4 Demo-safe vs client deployment
- Demo mode: mock adapters, local artifact storage, synthetic data.
- Client mode: real adapters + runtime secrets + managed observability, still using the same canonical contracts and lifecycle controls.

## 3) Integration architecture overview

```text
+----------------------+        +----------------------+        +----------------------+
| Ticketing / CMDB     | -----> | Normalizer           | -----> | firewall-policy-     |
| (ServiceNow-like)    |        | (client boundary)    |        | engine core workflow |
+----------------------+        +----------------------+        +----------+-----------+
                                                                         | ports
                                                                         v
                      +-------------------+   +-------------------+   +-------------------+
                      | Policy/Topology   |   | Firewall Mgmt APIs|   | Ticket Adapter    |
                      | Adapter (NSPM)    |   | Adapter           |   | (status/approvals)|
                      +-------------------+   +-------------------+   +-------------------+
                                ^                     ^                         ^
                                |                     |                         |
                                +----------+----------+------------+------------+
                                           |                       |
                              +------------+---------+   +---------+------------+
                              | Secrets Provider     |   | Observability Sink   |
                              | (runtime retrieval)  |   | + Artifact Store      |
                              +----------------------+   +-----------------------+
```

**Important:** no secrets are stored in this repository. Secret material is injected at runtime only.

## 4) External systems to integrate (capabilities and typical APIs)

### 4.1 Ticketing / CMDB (ServiceNow-like)
Typical capabilities:
- read change request metadata,
- fetch approval states and approver identity/role metadata,
- post lifecycle status updates and artifact references.

Typical API patterns:
- REST/JSON read/update operations,
- filtered queries by source reference,
- idempotent status update methods.

### 4.2 NSPM (Tufin-like) - optional
Typical capabilities:
- topology/risk context lookup,
- policy conflict pre-checks,
- compliance or path intelligence for planning/verification enrichment.

Typical API patterns:
- policy analysis endpoints,
- topology/path query endpoints,
- normalized risk scoring retrieval.

### 4.3 Firewall management planes
Examples: Palo Alto Panorama/PAN-OS, Check Point Management API.

Typical capabilities:
- read existing rulebase and object references,
- apply planned policy changes,
- collect effective-state data for verification,
- retrieve hit count / usage metadata (if available).

Typical API patterns:
- auth token/session bootstrap,
- object/rule CRUD or patch semantics,
- commit/publish workflows,
- read-back verification endpoints.

### 4.4 Secrets provider options
Supported deployment styles:
- environment variables,
- local file-based secrets for non-production development,
- Vault-style secret managers,
- cloud managers such as AWS Secrets Manager.

### 4.5 Artifact storage
Options:
- local filesystem (demo/development),
- S3-like object store (client environments),
- optional git-based evidence store for governance traceability.

### 4.6 Observability
Required signal types:
- structured logs,
- metrics/counters/timers,
- audit event stream (`AuditEvent` lineage).

Demo usually emits to stdout/local files; client environments should publish to managed logging/metrics/event platforms.

## 5) Adapter implementation guide (ports mapping)

### 5.1 Ticket Port
**Purpose**
- Bridge intake/status/approval context between ticketing systems and canonical lifecycle state.

**Minimum methods (conceptual)**
- `fetch_change_request(source_reference_id)`
- `fetch_approvals(change_request_id)`
- `update_change_status(change_request_id, state, artifact_refs)`

**Canonical inputs/outputs**
- Input: `change_request_id`, `source_reference_id`
- Output: normalized ticket metadata and `ApprovalRecord` data needed for state gating.

**Error handling expectations**
- Fail non-destructively on read errors,
- block state advancement requiring missing ticket evidence,
- emit `AuditEvent` with clear error class and correlation IDs.

### 5.2 Firewall Port
**Purpose**
- Execute plan/apply/verify operations against firewall management plane APIs.

**Minimum methods (conceptual)**
- `read_policy_snapshot(firewall_domain)`
- `apply_policy_plan(plan_id, operations)`
- `verify_applied_state(plan_id, snapshot_before_id, snapshot_after_id)`

**Canonical inputs/outputs**
- Input: `PolicyPlan`, scoped `ChangeRequest` fields (`firewall_domain`, `device_group`/`policy_scope`)
- Output: `PolicySnapshot`, `VerificationResult`, adapter invocation metadata.

**Error handling expectations**
- Fail closed for apply operations,
- never report silent partial success,
- persist failure artifacts and emit `AuditEvent`.

### 5.3 Policy/Topology Port (NSPM)
**Purpose**
- Provide optional pre/post policy intelligence (path/risk/topology/context).

**Minimum methods (conceptual)**
- `evaluate_topology(change_request)`
- `assess_policy_risk(change_request, snapshot)`
- `reconcile_expected_vs_effective(expected, current)`

**Canonical inputs/outputs**
- Input: `ChangeRequest`, `PolicySnapshot`
- Output: policy intelligence metadata, reconciliation findings, optional enrichment for risk decisions.

**Error handling expectations**
- optional enrichment failures should be explicit,
- if policy gating depends on NSPM signal, block progression and emit `AuditEvent`.

### 5.4 Secrets Port
**Purpose**
- Resolve runtime credentials/tokens/certs for other adapters.

**Minimum methods (conceptual)**
- `get_secret(secret_name)`
- `get_adapter_credentials(adapter_id)`
- `refresh_secret(secret_name)`

**Canonical inputs/outputs**
- Input: secret key names / adapter identity
- Output: ephemeral credential material (never written to canonical artifacts).

**Error handling expectations**
- deny adapter calls when secret retrieval fails,
- emit `AuditEvent` with sanitized messages (no secret values),
- support rotation without engine restart where possible.

### 5.5 Artifact Port
**Purpose**
- Persist governance evidence generated by the engine.

**Minimum methods (conceptual)**
- `write_artifact(change_request_id, artifact_type, payload)`
- `read_artifact(artifact_ref)`
- `list_artifacts(change_request_id)`

**Canonical inputs/outputs**
- Input: validation/planning/verification/reconciliation payloads
- Output: durable artifact references used by ticketing and audit trails.

**Error handling expectations**
- artifact write failures must block closure of dependent workflow stages,
- emit `AuditEvent` and retain local fallback buffer only if policy allows.

### 5.6 Observability Port
**Purpose**
- Emit logs, metrics, traces, and lifecycle/audit telemetry.

**Minimum methods (conceptual)**
- `emit_audit_event(audit_event)`
- `emit_metric(metric_name, value, labels)`
- `emit_log(level, message, context)`

**Canonical inputs/outputs**
- Input: lifecycle transitions and adapter outcomes
- Output: `AuditEvent` stream + metrics aligned to state transitions.

**Error handling expectations**
- observability emission failures must be visible,
- should not create silent success conditions,
- critical audit sink failures may block close-out based on governance policy.

## 6) Normalization layer guidance (client boundary)

### 6.1 Why normalization happens before engine processing
Client payload formats vary by ITSM/CMDB/process model. Normalization converts them into stable canonical contracts so the engine remains deterministic and reusable.

### 6.2 Minimal normalizer behavior
A minimal normalizer should:
1. parse source payload(s) from ticket/CMDB APIs,
2. map fields into canonical `ChangeRequest`,
3. produce `MappingReport` including:
   - mapped fields,
   - missing fields,
   - assumptions/defaults applied,
   - ambiguity flags,
4. reject or quarantine non-actionable payloads before engine ingest.

### 6.3 Contract tests for normalizers
At minimum, implement tests that validate:
- schema compliance against canonical contracts,
- mandatory field presence for actionable requests,
- deterministic mapping outcomes for same input,
- explicit handling of ambiguities and defaults.

## 7) Secrets and configuration model (no leakage)

### 7.1 Approved secret delivery mechanisms
- environment variables,
- `.env` file for local development only (must be gitignored),
- runtime retrieval from external secret manager APIs.

### 7.2 Recommended configuration keys (synthetic)
```text
ENGINE_MODE=plan_only
SECRETS_PROVIDER=env
TICKET_ADAPTER=servicenow
FIREWALL_ADAPTER=paloalto
POLICY_ADAPTER=tufin
ARTIFACT_STORE=s3_like
OBSERVABILITY_SINK=client_stack
```

Allowed value patterns:
- `ENGINE_MODE=plan_only|apply_enabled`
- `SECRETS_PROVIDER=env|vault|aws_secrets`
- `TICKET_ADAPTER=servicenow|mock`
- `FIREWALL_ADAPTER=paloalto|checkpoint|mock`
- `ARTIFACT_STORE=local|s3_like`

### 7.3 Secret name mapping examples (synthetic)
- `TICKET_API_TOKEN`
- `TICKET_API_BASE_URL`
- `FW_API_TOKEN`
- `FW_API_BASE_URL`
- `NSPM_API_TOKEN`
- `NSPM_API_BASE_URL`
- `ARTIFACT_STORE_ACCESS_KEY`
- `ARTIFACT_STORE_SECRET_KEY`

These names are placeholders; actual secret keys should follow platform naming standards.

### 7.4 Rotation and logging controls
- Rotate tokens/keys on a defined schedule and on incident response triggers.
- Prefer short-lived credentials where supported.
- Never log secret values; redact tokens, headers, and credential fields in all logs/events.

## 8) End-to-end onboarding checklist (client deployment)

### 8.1 Prerequisites
- Agree canonical schema versions for `ChangeRequest`, `ApprovalRecord`, `AuditEvent`, `PolicySnapshot`, `MappingReport`.
- Define firewall domains and scope taxonomy (`firewall_domain`, `device_group`/`policy_scope`).
- Define approval roles and segregation-of-duties controls.

### 8.2 Recommended onboarding steps
1. Implement and test normalizer (`source` -> canonical contracts).
2. Implement adapters for ticketing, firewall, optional NSPM, artifacts, observability, secrets.
3. Configure secrets provider and runtime config keys.
4. Run in `plan_only` mode for initial validation period.
5. Validate generated artifacts, approvals handling, and observability quality.
6. Enable `apply_enabled` for a controlled scope/domain.
7. Establish reconciliation schedule and drift response process.

### 8.3 Go-live gating checklist
- Validation success rate meets threshold (example policy target: >= 99% on qualified requests).
- Drift baseline established for in-scope domains.
- Audit artifacts reviewed by governance/security stakeholders.
- Approval-role enforcement and SoD checks verified.
- Rollback/compensating workflow tested with synthetic scenarios.

## 9) Failure modes and safe defaults
- **Missing approvals** -> do not apply; remain blocked until approvals satisfy policy.
- **Ambiguous scope** (`firewall_domain`/target mismatch) -> fail validation before plan/apply.
- **Adapter errors** -> emit `AuditEvent`, preserve artifacts, and do not treat partial execution as success.
- **Out-of-band changes** -> emit drift finding; optionally block new changes per policy until resolved.

Safe default posture:
- deny by default for apply,
- preserve auditability on every failure path,
- require explicit governance evidence to move lifecycle forward.

## 10) Minimal synthetic configuration and run flow example

### 10.1 Selected adapters (synthetic)
```text
ENGINE_MODE=plan_only
SECRETS_PROVIDER=vault
TICKET_ADAPTER=servicenow
FIREWALL_ADAPTER=checkpoint
POLICY_ADAPTER=tufin
ARTIFACT_STORE=local
OBSERVABILITY_SINK=stdout
```

### 10.2 Runtime secret source mapping (synthetic)
- Ticket adapter reads: `secret/integration/ticket/api_token`
- Firewall adapter reads: `secret/integration/firewall/api_token`
- NSPM adapter reads: `secret/integration/nspm/api_token`

No secret values are checked into code or artifacts.

### 10.3 Example run flow (conceptual)
1. Normalizer pulls ticket `sn-chg-910001` and produces:
   - `ChangeRequest.change_request_id = crq-2026-000410`
   - `MappingReport.mapping_report_id = map-demo-servicenow-2026-000410`
2. Engine validates and plans in `plan_only` mode.
3. Artifacts are written to local path namespace (example):
   - `out/validation/crq-2026-000410.json`
   - `out/plans/pln-2026-000410-v1.json`
   - `out/audit/evt-*.json`
4. Ticket adapter posts plan status + artifact references back to source ticket.
5. Observability sink emits transition metrics and `AuditEvent` telemetry.

This demonstrates wiring real API surfaces and secrets providers without changing core workflow logic.
