# HLD: Canonical Graph and System Relationships

## 1) Purpose and scope
This document defines the high-level design (HLD) for the canonical governance graph and system interactions used by `firewall-policy-engine`.

The design is **contract-first** and **demo-safe**:
- No vendor credentials, client-identifying records, or production infrastructure details are embedded.
- Integration points are modeled through stable interfaces (ports) with interchangeable adapters.
- Canonical schemas are consumed and produced as **versioned contracts**:
  - `ChangeRequest`
  - `ApprovalRecord`
  - `AuditEvent`
  - `PolicySnapshot`
  - `MappingReport`

## 2) Canonical graph model

### 2.1 Node types (entities)
The canonical graph is a logical model that links change intent, approvals, policy state, and verification outcomes.

- **ChangeRequest**
  - Canonical expression of requested policy change intent.
  - Stable identifier format (synthetic example): `crq-2026-000184`.
- **ApprovalRecord**
  - Approval decision and signer metadata associated with a `ChangeRequest`.
  - Synthetic ID: `apr-2026-000184-01`.
- **PolicyPlan** (engine-internal logical artifact)
  - Deterministic intended action plan derived from validated request.
  - Synthetic ID: `pln-2026-000184-v1`.
- **PolicySnapshot**
  - Captured effective policy state at a point in time (before/after apply; periodic reconciliation).
  - Synthetic ID: `psn-fwA-2026-03-01T120000Z`.
- **VerificationResult** (engine artifact)
  - Outcome comparing planned vs. effective post-apply state.
  - Synthetic ID: `ver-2026-000184-v1`.
- **DriftFinding** (engine artifact)
  - Detected divergence between expected and effective policy state.
  - Synthetic ID: `drf-fwA-2026-03-02-007`.
- **AuditEvent**
  - Immutable event entries for lifecycle transitions, decisions, and failures.
  - Synthetic ID: `evt-7f2a9d10`.
- **MappingReport**
  - Translation lineage from client payload(s) to canonical `ChangeRequest`.
  - Synthetic ID: `map-bankA-servicenow-2026-000184`.
- **RuleMetadata** (for recertification)
  - Ownership, justification, review date, expiry, and exception metadata.
  - Synthetic ID: `rmd-rule-88421`.

### 2.2 Edge types (relationships)
- `ChangeRequest` **REQUIRES_APPROVAL** `ApprovalRecord`
- `ChangeRequest` **GENERATES_PLAN** `PolicyPlan`
- `PolicyPlan` **TARGETS** `PolicySnapshot` (expected state model)
- `PolicyPlan` **APPLIES_TO** `FirewallDomain` (logical target scope)
- `PolicySnapshot` **CAPTURES_EFFECTIVE_STATE_OF** `FirewallDomain`
- `PolicyPlan` **VERIFIED_BY** `VerificationResult`
- `VerificationResult` **EMITS** `AuditEvent`
- `ChangeRequest` **EMITS** `AuditEvent` (state transitions)
- `PolicySnapshot` **COMPARED_WITH** `PolicySnapshot` (reconciliation baseline vs current)
- `DriftFinding` **DERIVED_FROM** (`PolicySnapshot`, expected state)
- `ChangeRequest` **MAPPED_FROM** `MappingReport`
- `RuleMetadata` **GOVERNS** `PolicyRule`

### 2.3 Canonical identifiers and referential rules
- Every node is globally referenceable with stable synthetic IDs.
- All child artifacts include `changeRequestId` or equivalent lineage pointers where applicable.
- Idempotency keys are derived from normalized canonical request content and operation context.
- Time semantics use UTC ISO-8601 timestamps for replay consistency.

### 2.4 Example relationship instances (synthetic)
- `crq-2026-000184` **REQUIRES_APPROVAL** `apr-2026-000184-01`
- `crq-2026-000184` **GENERATES_PLAN** `pln-2026-000184-v1`
- `pln-2026-000184-v1` **VERIFIED_BY** `ver-2026-000184-v1`
- `crq-2026-000184` **MAPPED_FROM** `map-bankA-servicenow-2026-000184`
- `drf-fwA-2026-03-02-007` **DERIVED_FROM** `psn-fwA-2026-03-01T120000Z`

## 3) Systems and responsibilities

### 3.1 External and platform systems
- **Ticketing / CMDB systems** (e.g., ServiceNow-like systems)
  - Origin of requested intent, requester attributes, and change governance context.
- **NSPM / policy governance platforms** (e.g., Tufin-like systems)
  - Optional source for topology context, policy analysis, and compliance insight.
- **Firewall platforms**
  - Enforcement points where intended policy changes become effective state.
- **Secrets provider**
  - Runtime retrieval of credentials/tokens/certificates for adapters.
- **Artifact storage**
  - Durable storage of reports and generated evidence.
- **Observability stack**
  - Metrics, traces, logs, event streams, and alerting for control-plane health.

### 3.2 Engine architecture (ports and adapters)
The engine core remains vendor-agnostic by depending on ports (interfaces). Adapters implement environment-specific integration logic.

```text
                    +----------------------------------------------+
                    |          Client Environment Systems          |
                    |----------------------------------------------|
                    | Ticketing/CMDB | NSPM | Firewall APIs        |
                    | Secrets Vault  | Artifact Store | Monitoring |
                    +--------------------+-------------------------+
                                         |
                                         | Adapter implementations
                                         v
+--------------------------------------------------------------------------------+
|                          firewall-policy-engine                                |
|--------------------------------------------------------------------------------|
|  API / Entry Points                                                            |
|      |                                                                         |
|      v                                                                         |
|  +------------------------------ Core Workflow ------------------------------+  |
|  | Validate -> Approve -> Plan -> Apply -> Verify -> Reconcile -> Recertify|  |
|  +-------------------------------------------------------------------------+  |
|      ^                 ^                 ^                ^                    |
|      |                 |                 |                |                    |
|  +---+---------+ +-----+---------+ +-----+---------+ +----+--------------+    |
|  | Ticket Port | | Policy Port   | | Firewall Port | | Observability Port|    |
|  +-------------+ +---------------+ +---------------+ +--------------------+    |
|  +-------------+ +---------------+ +---------------+                          |
|  | Secrets Port| | Artifact Port | | Topology Port |                          |
|  +-------------+ +---------------+ +---------------+                          |
+--------------------------------------------------------------------------------+
```

## 4) System of Record (SoR) by data category
- **Ticket intent**
  - **SoR:** Ticketing/CMDB system.
  - Canonical representation is `ChangeRequest` after normalization.
- **Approvals**
  - **SoR:** Approval workflow source (ticketing/governance system), with canonical evidence in `ApprovalRecord` artifacts.
- **Effective policy state**
  - **SoR:** Firewall platform runtime/effective configuration, sampled as `PolicySnapshot`.
- **Audit events**
  - **SoR:** Engine audit event stream/store, represented as `AuditEvent`.
- **Secrets**
  - **SoR:** Dedicated secrets manager (never persisted in canonical artifacts).
- **Artifacts**
  - **SoR:** Artifact storage managed by artifact adapter (validation reports, diffs, verification output, drift reports).

## 5) End-to-end data flow and lifecycle

### 5.1 Lifecycle states
1. **Draft**
   - Request exists but is not yet accepted for processing.
2. **Validated**
   - Schema, policy, and mandatory governance checks passed.
3. **Approved**
   - Required approvals recorded and policy gates satisfied.
4. **Planned**
   - Deterministic policy plan generated; no enforcement action yet.
5. **Applied**
   - Plan execution attempted via firewall adapter(s).
6. **Verified**
   - Effective state compared to planned intent; mismatch escalates.
7. **Closed**
   - Workflow complete with full artifact trail.

### 5.2 Data flow sequence
1. Inbound payload is ingested from ticketing/CMDB or API.
2. Normalization translates source payload to canonical `ChangeRequest` and emits `MappingReport`.
3. Validation runs against contract and governance controls.
4. Approval state is checked and persisted as `ApprovalRecord` evidence.
5. Planning generates a deterministic policy plan and diff artifacts.
6. Apply uses firewall provider adapters (if enabled for execution mode).
7. Verification collects post-change `PolicySnapshot` and computes match/mismatch.
8. Reconciliation periodically compares expected vs. effective state and emits drift findings.
9. Recertification evaluates rule metadata for ownership, justification, and expiry review queues.
10. Lifecycle transitions emit immutable `AuditEvent` entries and metrics.

### 5.3 Failure and rollback behavior
- Validation failure: transition halts before plan/apply; emit failure `AuditEvent`.
- Approval failure/missing approval: remain non-executable; no apply allowed.
- Apply partial failure: mark as failed, capture granular adapter outcomes, preserve compensating action guidance.
- Verify mismatch: state does not close automatically; emit drift/verification failures for investigation.
- Rollback model: either explicit compensating plan generation or controlled manual remediation tracked by audit events.

## 6) Normalization layer (client separation boundary)
Normalization is a distinct pre-engine layer converting client-specific payloads (CMDB, ServiceNow-like tickets, custom forms) into canonical contracts:
- Primary outputs: `ChangeRequest` + `MappingReport`.
- The engine core only accepts canonical forms and does not embed client-specific field logic.

Why this separation is required:
- Protects engine stability from client schema churn.
- Enables independent testing and contract validation of mappings.
- Supports multi-client onboarding without changing core workflow logic.
- Preserves deterministic behavior because planning/verification operate on normalized data only.

## 7) Trust boundaries and security design

### 7.1 Trust boundaries
- Boundary A: External request producers -> API ingress.
- Boundary B: Engine core -> external adapters (ticket, firewall, NSPM, artifact, secrets, observability).
- Boundary C: Engine runtime -> secrets provider.
- Boundary D: Artifact generation -> immutable storage and audit domains.

### 7.2 Security and governance principles
- Least privilege for every adapter identity.
- Segregation of duties between requester, approver, and executor roles.
- Immutable auditing with traceable lineage IDs.
- No secrets in logs/artifacts; runtime retrieval only.
- Deny-by-default execution when preconditions are not met.

## 8) Non-functional requirements
- **Auditability:** Every state transition and decision emits `AuditEvent` with correlation IDs.
- **Determinism:** Same canonical input and baseline state produce same plan outputs.
- **Idempotency:** Repeat submissions with same idempotency key avoid duplicate effect.
- **Least privilege:** Adapter scopes restricted to minimal read/write actions.
- **Segregation of duties:** Approval and execution controls enforce governance separation.
- **Reproducibility:** Artifacts and snapshots allow replay/forensic reconstruction.

## 9) Observability model

### 9.1 Events emitted by state transition
At each lifecycle transition (`Draft` -> `Validated` -> `Approved` -> `Planned` -> `Applied` -> `Verified` -> `Closed`), emit:
- transition event (`AuditEvent`)
- duration metrics per state and end-to-end latency
- success/failure counters by adapter and reason class
- correlation fields (`changeRequestId`, `planId`, adapter invocation IDs)

### 9.2 Drift and reconciliation reporting
- Reconciliation jobs emit summary metrics:
  - rules evaluated
  - drift findings count
  - severity distribution
  - mean time to detect drift
- Detailed drift findings are persisted as artifacts and linked to source snapshots and expected baseline IDs.

## 10) Key risks and mitigations
- **Topology model accuracy risk**
  - *Risk:* incorrect path/context assumptions lead to unsafe or ineffective plans.
  - *Mitigation:* topology validation gates, confidence scoring, and explicit unknown-state handling.
- **Bypass risk (out-of-band firewall changes)**
  - *Risk:* effective state diverges from intended state.
  - *Mitigation:* periodic reconciliation, drift alerts, and governance escalation workflows.
- **Metadata discipline risk**
  - *Risk:* missing owner/justification/expiry degrades recertification quality.
  - *Mitigation:* mandatory metadata checks at validation and recertification SLAs.
- **Drift accumulation risk**
  - *Risk:* unmanaged drift reduces trust in automation.
  - *Mitigation:* threshold-based blocking of new changes until critical drift is resolved.
- **Scale/performance risk**
  - *Risk:* large rulebases slow planning and verification.
  - *Mitigation:* partitioned processing, bounded snapshots, caching, and async reconciliation workers.
- **Concurrency/locking risk**
  - *Risk:* overlapping changes on shared policy objects create race conditions.
  - *Mitigation:* optimistic concurrency checks, per-domain change locks, and deterministic conflict resolution.

## 11) Design principles summary
1. Canonical contracts are the only stable interface into core processing.
2. Ports/adapters isolate environmental variance from governance logic.
3. Plan/apply separation preserves control and audit confidence.
4. Observability and audit artifacts are first-class outputs, not side effects.
5. Reconciliation and recertification are continuous controls, not one-time checks.
