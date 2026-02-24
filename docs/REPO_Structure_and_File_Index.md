# Repository Structure and File Index

## 1) Purpose
This document is the practical structure index for `firewall-policy-engine`.

Use it to:
- understand the intended repository layout,
- locate where responsibilities belong,
- identify what each file should consume/produce,
- keep canonical boundaries clean as the repository is scaffolded iteratively.

This index aligns with the repository contract-first model and is consistent with:
- `README.md` (scope, execution model, high-level layout),
- `docs/HLD_Canonical_Graph_and_System_Relationships.md` (systems, lifecycle, ports/adapters),
- `docs/LLD_Variables_and_Mandatory_Fields.md` (canonical field models and mandatory gates),
- `docs/INTEGRATION_Plugging_APIs_and_Secrets.md` (adapter wiring and runtime secrets model).

## 2) Expected repository tree (authoritative target layout)

Legend for directory classification:
- **Core**: engine workflow and canonical processing logic
- **Contracts**: versioned canonical schemas
- **Demo**: deterministic synthetic harness and fixtures
- **Testing**: automated verification suites
- **CI**: pipeline definitions
- **Docs**: architecture and implementation guidance
- **Generated**: runtime outputs/artifacts

```text
firewall-policy-engine/
├── README.md                                   # (Docs) project scope and execution model
├── docs/                                       # (Docs) HLD/LLD/integration/index references
│   ├── HLD_Canonical_Graph_and_System_Relationships.md
│   ├── LLD_Variables_and_Mandatory_Fields.md
│   ├── INTEGRATION_Plugging_APIs_and_Secrets.md
│   └── REPO_Structure_and_File_Index.md
├── schemas/                                    # (Contracts) versioned canonical contracts
│   └── v1/
│       ├── ChangeRequest.schema.json
│       ├── ApprovalRecord.schema.json
│       ├── AuditEvent.schema.json
│       ├── PolicySnapshot.schema.json
│       └── MappingReport.schema.json
├── engine/                                     # (Core) canonical control-plane implementation
│   ├── api/                                    # (Core) entrypoints for submission/reporting/reconcile
│   │   ├── submit_change.py
│   │   ├── get_status.py
│   │   └── reconcile.py
│   ├── core/                                   # (Core) validation->plan->apply->verify lifecycle
│   │   ├── workflow_state_machine.py
│   │   ├── validate.py
│   │   ├── plan.py
│   │   ├── apply.py
│   │   ├── verify.py
│   │   ├── reconcile.py
│   │   └── recertify.py
│   ├── ports/                                  # (Core) external dependency interfaces
│   │   ├── ticket_port.py
│   │   ├── firewall_port.py
│   │   ├── policy_topology_port.py
│   │   ├── secrets_port.py
│   │   ├── artifact_port.py
│   │   └── observability_port.py
│   ├── adapters/
│   │   └── mock/                               # (Demo/Core-adapter) deterministic local adapter set
│   │       ├── mock_ticket_adapter.py
│   │       ├── mock_firewall_adapter.py
│   │       ├── mock_policy_topology_adapter.py
│   │       ├── mock_secrets_adapter.py
│   │       ├── mock_artifact_adapter.py
│   │       └── mock_observability_adapter.py
│   └── utils/                                  # (Core) shared helpers
│       ├── hashing.py
│       ├── time_utils.py
│       └── structured_logging.py
├── demo/                                       # (Demo) deterministic run harness
│   ├── run_demo.py
│   ├── fixtures/
│   │   ├── change_requests/
│   │   ├── policy_snapshots/
│   │   └── rule_metadata/
│   └── scenarios/
│       ├── happy_path.yaml
│       ├── drift_detection.yaml
│       └── recertification.yaml
├── out/                                        # (Generated) runtime artifacts written by demo/engine
│   ├── validation/
│   ├── approvals/
│   ├── plans/
│   ├── diffs/
│   ├── verification/
│   ├── drift/
│   ├── recertification/
│   └── audit/
├── tests/                                      # (Testing) validation of core, contracts, integrations
│   ├── unit/
│   │   ├── test_validate.py
│   │   ├── test_plan.py
│   │   └── test_workflow_state_machine.py
│   ├── contract/
│   │   ├── test_change_request_schema.py
│   │   ├── test_approval_record_schema.py
│   │   └── test_mapping_report_schema.py
│   └── integration/
│       ├── test_happy_path.py
│       ├── test_drift_detection.py
│       └── test_recertification.py
└── .github/
    └── workflows/                              # (CI) build/test/lint pipeline automation
        ├── ci.yml
        ├── contract-tests.yml
        └── docs-check.yml
```

> Notes:
> - File names above are the authoritative **target pattern** for contributors; exact implementation language may vary.
> - Directory responsibilities are fixed even if actual file presence is partial in early commits.

## 3) File-by-file index (core sections)

## 3.1 Root

### `README.md`
- **Role:** Doc
- **Purpose:** Defines repository intent, scope boundaries, lifecycle model, artifact types, and high-level layout.
- **Inputs:** N/A (authoritative project description).
- **Outputs:** Contributor alignment and implementation direction.
- **Notes:** Treat as source of truth for control-plane scope; avoid vendor-specific logic drift.

## 3.2 `docs/`

### `docs/HLD_Canonical_Graph_and_System_Relationships.md`
- **Role:** Doc
- **Purpose:** High-level architecture for canonical graph, systems, lifecycle, trust boundaries, SoR, and risks.
- **Inputs:** Canonical concepts from README and contract-first architecture.
- **Outputs:** Shared architectural vocabulary for engine and adapters.
- **Notes:** Keep aligned to lifecycle states (`Draft` -> `Closed`) and ports/adapters model.

### `docs/LLD_Variables_and_Mandatory_Fields.md`
- **Role:** Doc
- **Purpose:** Canonical field catalog, required/optional gates, validation expectations, and synthetic examples.
- **Inputs:** Versioned contract definitions and workflow gates.
- **Outputs:** Implementable variable model for normalizers, validators, and adapters.
- **Notes:** Any new canonical field requires schema/version updates and LLD revision.

### `docs/INTEGRATION_Plugging_APIs_and_Secrets.md`
- **Role:** Doc
- **Purpose:** Practical integration guide for plugging real APIs and runtime secrets into adapter ports.
- **Inputs:** Port interface expectations, security model, runtime config patterns.
- **Outputs:** Adapter onboarding guidance for client environments.
- **Notes:** No credentials or production endpoints; runtime injection only.

### `docs/REPO_Structure_and_File_Index.md`
- **Role:** Doc
- **Purpose:** This index; maps structure to responsibilities and extension points.
- **Inputs:** README + HLD + LLD + integration guidance.
- **Outputs:** Deterministic contributor map for file placement and ownership.
- **Notes:** Keep updated as new directories/files are added.

## 3.3 `schemas/`

### `schemas/v1/ChangeRequest.schema.json`
- **Role:** Contract
- **Purpose:** Canonical intake schema for actionable firewall governance requests.
- **Inputs:** Normalized source requests from normalizer layer.
- **Outputs:** Validation contract enforcing required fields and enum/type constraints.
- **Notes:** Changes require versioning discipline and backward-compatibility assessment.

### `schemas/v1/ApprovalRecord.schema.json`
- **Role:** Contract
- **Purpose:** Defines approval evidence structure and governance decision metadata.
- **Inputs:** Approval signals from ticketing/governance systems.
- **Outputs:** Canonical approval artifacts tied to `change_request_id`.
- **Notes:** Required for apply gates and audit traceability.

### `schemas/v1/AuditEvent.schema.json`
- **Role:** Contract
- **Purpose:** Defines lifecycle/audit event payload shape.
- **Inputs:** Core transitions, adapter outcomes, failure reasons.
- **Outputs:** Immutable audit event entries used by observability and evidence workflows.
- **Notes:** Keep event taxonomy stable; extend via additive versioning.

### `schemas/v1/PolicySnapshot.schema.json`
- **Role:** Contract
- **Purpose:** Canonical snapshot of effective policy state for verify/reconcile.
- **Inputs:** Firewall or NSPM adapter readbacks.
- **Outputs:** Deterministic policy-state representation and policy hash.
- **Notes:** Raw config blobs should be referenced, not embedded, in canonical records.

### `schemas/v1/MappingReport.schema.json`
- **Role:** Contract
- **Purpose:** Normalization lineage and mapping quality report.
- **Inputs:** Source payload refs + mapping logic outcomes.
- **Outputs:** Missing fields, assumptions/defaults, ambiguity flags.
- **Notes:** Critical for contract-first intake quality and troubleshooting.

## 3.4 `engine/`

## 3.4.1 `engine/api/`

### `engine/api/submit_change.py`
- **Role:** Core
- **Purpose:** Entry point for receiving normalized `ChangeRequest` submissions.
- **Inputs:** `ChangeRequest`, `MappingReport`, optional correlation metadata.
- **Outputs:** Initial workflow state transition and submission acknowledgment.
- **Notes:** Must reject non-canonical payloads.

### `engine/api/get_status.py`
- **Role:** Core
- **Purpose:** Query current lifecycle state and artifacts for a request.
- **Inputs:** `change_request_id`.
- **Outputs:** State summary + artifact references.
- **Notes:** Should be read-only and auditable.

### `engine/api/reconcile.py`
- **Role:** Core
- **Purpose:** Trigger reconciliation run for expected vs effective state.
- **Inputs:** Scope identifiers (`firewall_domain`, snapshot references).
- **Outputs:** Drift findings and reconciliation artifacts/events.
- **Notes:** Must preserve deterministic comparison logic.

## 3.4.2 `engine/core/`

### `engine/core/workflow_state_machine.py`
- **Role:** Core
- **Purpose:** Enforces allowed state transitions (`Draft`, `Validated`, `Approved`, `Planned`, `Applied`, `Verified`, `Closed`).
- **Inputs:** Current state + gate evaluation results.
- **Outputs:** Next-state decisions + transition events.
- **Notes:** Central guardrail; avoid bypass paths.

### `engine/core/validate.py`
- **Role:** Core
- **Purpose:** Schema and governance validation for canonical requests.
- **Inputs:** `ChangeRequest`, `MappingReport`, policy rules.
- **Outputs:** Validation report artifact + pass/fail signals.
- **Notes:** Missing mandatory fields must fail with `AuditEvent`.

### `engine/core/plan.py`
- **Role:** Core
- **Purpose:** Build deterministic `PolicyPlan` from validated canonical intent.
- **Inputs:** `ChangeRequest`, baseline policy context.
- **Outputs:** `PolicyPlan`, policy diff artifacts, plan hash.
- **Notes:** Plan/apply separation must remain strict.

### `engine/core/apply.py`
- **Role:** Core
- **Purpose:** Execute plan through firewall adapters when mode is `apply_enabled`.
- **Inputs:** `PolicyPlan`, approval evidence, runtime lock context.
- **Outputs:** Apply results, adapter invocation records, audit events.
- **Notes:** Fail closed on adapter errors; no silent partial success.

### `engine/core/verify.py`
- **Role:** Core
- **Purpose:** Compare expected plan outcomes against effective post-apply state.
- **Inputs:** `PolicyPlan`, before/after `PolicySnapshot`.
- **Outputs:** `VerificationResult`, mismatch artifacts/events.
- **Notes:** `match_status` governs progression to `Closed`.

### `engine/core/reconcile.py`
- **Role:** Core
- **Purpose:** Detect drift between expected and observed policy state over time.
- **Inputs:** Baseline/current `PolicySnapshot`, expected state references.
- **Outputs:** Drift findings and reconciliation reports.
- **Notes:** Drift severity may block new applies by policy.

### `engine/core/recertify.py`
- **Role:** Core
- **Purpose:** Generate recertification queues based on rule metadata and expiry.
- **Inputs:** Rule metadata snapshots, ownership/justification/expiry fields.
- **Outputs:** Recertification queue artifacts and reminders/events.
- **Notes:** Metadata quality is critical to accuracy.

## 3.4.3 `engine/ports/`

### `engine/ports/ticket_port.py`
- **Role:** Core
- **Purpose:** Interface for ticket and approval retrieval/update.
- **Inputs:** Source refs, request IDs.
- **Outputs:** Approval/status payloads for core flow.
- **Notes:** Adapter implementations must preserve canonical semantics.

### `engine/ports/firewall_port.py`
- **Role:** Core
- **Purpose:** Interface for policy read/apply/verify operations.
- **Inputs:** `PolicyPlan` operations and scope.
- **Outputs:** Effective state readbacks and apply results.
- **Notes:** Must support idempotent retries where possible.

### `engine/ports/policy_topology_port.py`
- **Role:** Core
- **Purpose:** Interface for optional NSPM/topology/risk enrichment.
- **Inputs:** Canonical requests/snapshots.
- **Outputs:** Risk/topology assessments and reconciliation context.
- **Notes:** Optional adapter, but required if policy gates depend on it.

### `engine/ports/secrets_port.py`
- **Role:** Core
- **Purpose:** Interface for runtime secret retrieval.
- **Inputs:** Secret name keys and adapter identity.
- **Outputs:** Ephemeral auth material for adapter use.
- **Notes:** Never serialize secret values to artifacts.

### `engine/ports/artifact_port.py`
- **Role:** Core
- **Purpose:** Interface for writing and reading audit/validation/plan/verify artifacts.
- **Inputs:** Artifact payloads + metadata (`change_request_id`, type).
- **Outputs:** Durable artifact references.
- **Notes:** Artifact failures should block closure of dependent workflow steps.

### `engine/ports/observability_port.py`
- **Role:** Core
- **Purpose:** Interface for logs/metrics/audit emissions.
- **Inputs:** Transition and adapter outcome context.
- **Outputs:** Observability signals and event publications.
- **Notes:** Ensure correlation IDs propagate consistently.

## 3.4.4 `engine/adapters/mock/`

### `engine/adapters/mock/mock_ticket_adapter.py`
- **Role:** Demo
- **Purpose:** Synthetic ticket/approval behavior for local deterministic runs.
- **Inputs:** Demo fixture references.
- **Outputs:** Mock approval/status payloads.
- **Notes:** Keep deterministic; avoid real API coupling.

### `engine/adapters/mock/mock_firewall_adapter.py`
- **Role:** Demo
- **Purpose:** Simulates firewall read/apply/verify operations.
- **Inputs:** `PolicyPlan` operations and fixture state.
- **Outputs:** Synthetic snapshots and apply results.
- **Notes:** Should model both success and controlled-failure branches.

### `engine/adapters/mock/mock_policy_topology_adapter.py`
- **Role:** Demo
- **Purpose:** Simulates topology/risk lookups and reconciliation hints.
- **Inputs:** Canonical scope and flow data.
- **Outputs:** Synthetic risk/topology insights.
- **Notes:** Keep outputs reproducible for tests.

### `engine/adapters/mock/mock_secrets_adapter.py`
- **Role:** Demo
- **Purpose:** Provides fake runtime secret values in local mode.
- **Inputs:** Secret key names.
- **Outputs:** Synthetic credential placeholders.
- **Notes:** Never mirror real secret formats.

### `engine/adapters/mock/mock_artifact_adapter.py`
- **Role:** Demo
- **Purpose:** Writes artifacts to local deterministic storage paths.
- **Inputs:** Artifact payloads.
- **Outputs:** Local artifact references (e.g., under `out/`).
- **Notes:** Maintain stable path conventions for tests.

### `engine/adapters/mock/mock_observability_adapter.py`
- **Role:** Demo
- **Purpose:** Emits synthetic logs/metrics/events for demo visibility.
- **Inputs:** Lifecycle and adapter context.
- **Outputs:** Local or stdout telemetry records.
- **Notes:** Ensure event schemas remain canonical.

## 3.4.5 `engine/utils/`

### `engine/utils/hashing.py`
- **Role:** Core
- **Purpose:** Deterministic hashing utilities for plans/snapshots/idempotency.
- **Inputs:** Normalized payload fragments.
- **Outputs:** Stable hashes.
- **Notes:** Canonical serialization order matters.

### `engine/utils/time_utils.py`
- **Role:** Core
- **Purpose:** UTC timestamp handling and consistent time-window utilities.
- **Inputs:** Runtime clock or injected test clock.
- **Outputs:** ISO-8601 UTC values and comparisons.
- **Notes:** Avoid local timezone ambiguity.

### `engine/utils/structured_logging.py`
- **Role:** Core
- **Purpose:** Structured log helper with correlation metadata.
- **Inputs:** Message + context fields.
- **Outputs:** Log records suitable for observability ingestion.
- **Notes:** Redact sensitive fields by default.

## 3.5 `demo/`

### `demo/run_demo.py`
- **Role:** Demo
- **Purpose:** Orchestrates deterministic scenario execution with mock adapters.
- **Inputs:** Scenario definitions + fixture data.
- **Outputs:** Generated artifacts under `out/` and state transition telemetry.
- **Notes:** Must remain environment-independent.

### `demo/fixtures/change_requests/`
- **Role:** Demo
- **Purpose:** Synthetic input payload fixtures aligned to canonical contracts.
- **Inputs:** Curated test cases.
- **Outputs:** Repeatable request datasets for demo and tests.
- **Notes:** No client identifiers or real addresses.

### `demo/fixtures/policy_snapshots/`
- **Role:** Demo
- **Purpose:** Synthetic baseline/current policy-state fixture sets.
- **Inputs:** Curated policy-state snapshots.
- **Outputs:** Reconcile/verify inputs.
- **Notes:** Keep deterministic policy hashes where possible.

### `demo/fixtures/rule_metadata/`
- **Role:** Demo
- **Purpose:** Synthetic ownership/justification/expiry metadata for recertification.
- **Inputs:** Rule metadata fixture records.
- **Outputs:** Recertification queue scenarios.
- **Notes:** Ensure metadata completeness for meaningful demo output.

### `demo/scenarios/happy_path.yaml`
- **Role:** Demo
- **Purpose:** Scenario definition for standard successful lifecycle flow.
- **Inputs:** Fixture refs and expected outcomes.
- **Outputs:** Validation/plan/apply/verify artifacts.
- **Notes:** Primary baseline scenario.

### `demo/scenarios/drift_detection.yaml`
- **Role:** Demo
- **Purpose:** Scenario definition for reconciliation and drift findings.
- **Inputs:** Baseline/current snapshot fixture refs.
- **Outputs:** Drift report artifacts and events.
- **Notes:** Validate severity handling and block policies.

### `demo/scenarios/recertification.yaml`
- **Role:** Demo
- **Purpose:** Scenario definition for metadata-driven recertification workflows.
- **Inputs:** Rule metadata fixtures.
- **Outputs:** Recertification queues and audit events.
- **Notes:** Ensure ownership/expiry edge cases are represented.

## 3.6 `out/` (generated)

### `out/validation/`
- **Role:** Generated
- **Purpose:** Stores validation reports.
- **Inputs:** `ChangeRequest` + validation engine results.
- **Outputs:** Validation artifacts.
- **Notes:** Regenerated per run; do not treat as source code.

### `out/approvals/`
- **Role:** Generated
- **Purpose:** Stores approval evidence artifacts.
- **Inputs:** `ApprovalRecord` data.
- **Outputs:** Approval artifact files.
- **Notes:** Keep synthetic for demo contexts.

### `out/plans/`
- **Role:** Generated
- **Purpose:** Stores generated `PolicyPlan` artifacts.
- **Inputs:** Validated requests and planning logic.
- **Outputs:** Plan payloads and plan hashes.
- **Notes:** Determinism checks often read from here.

### `out/diffs/`
- **Role:** Generated
- **Purpose:** Stores expected-state diff artifacts.
- **Inputs:** Baseline and planned state representations.
- **Outputs:** Policy diff files.
- **Notes:** Useful for approval and review workflows.

### `out/verification/`
- **Role:** Generated
- **Purpose:** Stores verification outputs and mismatches.
- **Inputs:** Before/after snapshots + plan expectations.
- **Outputs:** `VerificationResult` artifacts.
- **Notes:** Required evidence before closure.

### `out/drift/`
- **Role:** Generated
- **Purpose:** Stores reconciliation drift findings.
- **Inputs:** Baseline/current snapshots.
- **Outputs:** Drift report artifacts.
- **Notes:** May drive policy blocking decisions.

### `out/recertification/`
- **Role:** Generated
- **Purpose:** Stores recertification queue outputs.
- **Inputs:** Rule metadata and recertification logic.
- **Outputs:** Due-for-review artifacts.
- **Notes:** Ownership and expiry quality impacts output value.

### `out/audit/`
- **Role:** Generated
- **Purpose:** Stores emitted `AuditEvent` records.
- **Inputs:** Lifecycle transitions and failure events.
- **Outputs:** Immutable-semantics event artifacts.
- **Notes:** Must remain traceable by `change_request_id` and correlation IDs.

## 3.7 `tests/`

### `tests/unit/test_validate.py`
- **Role:** Test
- **Purpose:** Unit tests for field and governance validation logic.
- **Inputs:** Canonical payload fixtures.
- **Outputs:** Pass/fail test outcomes.
- **Notes:** Cover mandatory-gate edge cases.

### `tests/unit/test_plan.py`
- **Role:** Test
- **Purpose:** Unit tests for deterministic plan generation behavior.
- **Inputs:** Validated request fixtures + baseline state.
- **Outputs:** Determinism and correctness assertions.
- **Notes:** Guard against non-deterministic ordering bugs.

### `tests/unit/test_workflow_state_machine.py`
- **Role:** Test
- **Purpose:** Unit tests for allowed/blocked lifecycle transitions.
- **Inputs:** State and gate condition combinations.
- **Outputs:** Transition safety assertions.
- **Notes:** Must prevent invalid state shortcuts.

### `tests/contract/test_change_request_schema.py`
- **Role:** Test
- **Purpose:** Contract tests for `ChangeRequest` schema conformance.
- **Inputs:** Positive/negative canonical examples.
- **Outputs:** Schema validity assertions.
- **Notes:** Update alongside schema version increments.

### `tests/contract/test_approval_record_schema.py`
- **Role:** Test
- **Purpose:** Contract tests for approval evidence payloads.
- **Inputs:** Approval fixtures.
- **Outputs:** Validation assertions.
- **Notes:** Ensure role and decision enums remain controlled.

### `tests/contract/test_mapping_report_schema.py`
- **Role:** Test
- **Purpose:** Contract tests for normalization lineage payloads.
- **Inputs:** Mapping report fixtures.
- **Outputs:** Required-field and type assertions.
- **Notes:** Validate missing field/ambiguity reporting quality.

### `tests/integration/test_happy_path.py`
- **Role:** Test
- **Purpose:** End-to-end scenario tests for standard lifecycle progression.
- **Inputs:** Demo fixtures + mock adapters.
- **Outputs:** Multi-stage artifact and state assertions.
- **Notes:** Baseline for regression confidence.

### `tests/integration/test_drift_detection.py`
- **Role:** Test
- **Purpose:** End-to-end reconciliation and drift detection test coverage.
- **Inputs:** Snapshot fixture sets.
- **Outputs:** Drift artifact and event assertions.
- **Notes:** Ensure severity and block-policy behavior is validated.

### `tests/integration/test_recertification.py`
- **Role:** Test
- **Purpose:** End-to-end recertification queue behavior validation.
- **Inputs:** Rule metadata fixtures.
- **Outputs:** Queue generation and audit assertions.
- **Notes:** Include expiry/ownership edge conditions.

## 3.8 `.github/workflows/`

### `.github/workflows/ci.yml`
- **Role:** CI
- **Purpose:** Main CI pipeline for linting/testing.
- **Inputs:** Repository source + test configuration.
- **Outputs:** Build/test status signals.
- **Notes:** Keep deterministic and fast.

### `.github/workflows/contract-tests.yml`
- **Role:** CI
- **Purpose:** Dedicated pipeline for schema/contract validation.
- **Inputs:** `schemas/` + contract tests.
- **Outputs:** Contract compatibility status.
- **Notes:** Run on schema/doc updates affecting contracts.

### `.github/workflows/docs-check.yml`
- **Role:** CI
- **Purpose:** Documentation sanity checks (formatting/spell/lint if configured).
- **Inputs:** `README.md` and `docs/` content.
- **Outputs:** Docs quality status.
- **Notes:** Useful for keeping architecture docs coherent.

## 4) What exists vs what is planned
Early repository commits may intentionally contain only `README.md` and `docs/` content while core directories are scaffolded in phases.

Contributor guidance when adding new files:
1. Place files in the correct boundary directory (contracts/core/adapters/demo/tests/ci).
2. Keep external-system logic behind ports and adapters only.
3. Keep canonical schemas/versioning authoritative for field contracts.
4. Update this index when adding/removing key files.
5. Avoid introducing placeholder production details; keep demo artifacts synthetic.

## 5) Extension points and companion repositories
Conceptual integration boundaries:
- **`firewall-policy-library`**
  - Holds vendor-agnostic policy definitions, baselines, exception models, and recertification controls.
  - Consumed conceptually by planning/validation policy logic.
- **`firewall-vendor-adapters`**
  - Holds vendor-specific translation and API adapters for firewall platforms.
  - Connects through `engine/ports/firewall_port.py` interface contracts.

Boundary rule:
- vendor-specific logic belongs in adapter implementations,
- policy intent models belong in policy-library artifacts,
- this engine remains canonical and contract-first.

## 6) Contribution guardrails
1. **No secrets in repository**
   - No tokens, credentials, private keys, or production endpoints in code/docs/fixtures.
2. **All external integrations behind ports**
   - Core must never call vendor APIs directly.
3. **Canonical contract governance**
   - Any new canonical field requires schema versioning and LLD updates.
4. **Synthetic demo data only**
   - Demo fixtures must remain non-identifying and deterministic.
5. **Plan/apply separation remains explicit**
   - `plan_only` and `apply_enabled` modes must remain auditable and distinct.
6. **Auditability first**
   - Validation failures, adapter failures, and drift events must emit canonical `AuditEvent` evidence.
