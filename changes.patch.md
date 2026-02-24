diff --git a/docs/LLD_Variables_and_Mandatory_Fields.md b/docs/LLD_Variables_and_Mandatory_Fields.md
new file mode 100644
index 0000000000000000000000000000000000000000..6bd3ef0afcdc0780e7b7f6b5e8d13a6813ca445f
--- /dev/null
+++ b/docs/LLD_Variables_and_Mandatory_Fields.md
@@ -0,0 +1,348 @@
+# LLD: Variables and Mandatory Fields
+
+## 1) Purpose and scope
+This low-level design (LLD) defines the canonical variables (fields), validation constraints, and processing requirements used by `firewall-policy-engine` to process actionable firewall governance requests.
+
+The document is contract-first and demo-safe:
+- It specifies canonical input/output fields expected by the engine.
+- It defines mandatory minimum field sets by lifecycle gate.
+- It uses synthetic identifiers and placeholders only (no real credentials, client identifiers, or production infrastructure details).
+
+## 2) Canonical contracts covered
+This LLD covers field models for these versioned contracts:
+- `ChangeRequest`
+- `ApprovalRecord`
+- `AuditEvent`
+- `PolicySnapshot`
+- `MappingReport`
+
+For completeness, it also includes minimal field sets for engine-internal artifacts:
+- `PolicyPlan` (internal engine artifact)
+- `VerificationResult` (internal engine artifact)
+- `DriftFinding` (internal engine artifact)
+
+## 3) Definitions and conventions
+
+### 3.1 Field naming convention
+All canonical examples in this repository use **snake_case** field names.
+
+### 3.2 Timestamp format
+All timestamps are UTC ISO-8601 strings, e.g. `2026-04-08T14:32:10Z`.
+
+### 3.3 Identifier format
+Identifiers are synthetic, deterministic-friendly strings with human-readable prefixes.
+Examples:
+- `change_request_id`: `crq-2026-000321`
+- `approval_record_id`: `apr-2026-000321-01`
+- `mapping_report_id`: `map-demo-servicenow-2026-000321`
+- `snapshot_id`: `psn-fw-core-2026-04-08T143500Z`
+- `event_id`: `evt-9ab41d2f`
+
+### 3.4 Idempotency key
+An idempotency key is a stable key derived from canonical request intent and scope (for example, normalized payload hash + source reference). It is:
+- stored on `ChangeRequest.idempotency_key`,
+- used during ingest/validation to prevent duplicate effects,
+- referenced by audit events for replay and traceability.
+
+## 4) ChangeRequest v1 field model
+
+### 4.1 Top-level structure
+`ChangeRequest` groups fields into:
+- `identity`
+- `actors`
+- `scope`
+- `intent`
+- `flows`
+- `constraints`
+- `governance`
+- `metadata`
+
+### 4.2 Field catalog
+| Field name | Type | Required | Description | Validation rules | Example (synthetic) |
+|---|---|---|---|---|---|
+| `change_request_id` | string | Yes | Canonical request identifier. | Regex `^crq-[0-9]{4}-[0-9]{6}$`; globally unique per tenant/scope. | `crq-2026-000321` |
+| `idempotency_key` | string | Yes | Duplicate-submission control key. | Non-empty; max 128 chars; deterministic for same normalized intent. | `idem-1c90d4f8f6` |
+| `source_system` | string | Yes | Origin system for request ingest. | Enum: `servicenow`, `cmdb`, `api`, `mock`. | `servicenow` |
+| `source_reference_id` | string | Yes | Source-side reference for traceability. | Non-empty; max 128 chars. | `sn-chg-900321` |
+| `requester` | object | Yes | Initiating actor identity. | Must include `requester.id`; email optional but if present valid format. | `{"id":"usr-req-001","email":"requester@example.invalid"}` |
+| `business_owner` | object | Yes | Accountability owner for business approval. | Must include `business_owner.id`. | `{"id":"usr-biz-010"}` |
+| `technical_owner` | object | Yes | Technical accountability owner. | Must include `technical_owner.id`. | `{"id":"usr-tech-020"}` |
+| `environment` | string | Yes | Target environment context. | Enum: `dev`, `test`, `uat`, `prod`, `shared`. | `prod` |
+| `firewall_domain` | string | Yes | Logical firewall policy domain. | Non-empty; lowercase slug recommended. | `fw-domain-core` |
+| `device_group` | string | Conditional | Logical device group target. | Required if `policy_scope` absent. | `edge-dc1` |
+| `policy_scope` | string | Conditional | Alternative scope token for policy engine. | Required if `device_group` absent. | `zone-internet-to-app` |
+| `tenant` | string | Optional | Multi-tenant context label. | Slug format; max 64 chars. | `tenant-alpha` |
+| `action` | string | Yes | Requested policy operation type. | Enum: `allow`, `deny`, `modify`, `remove`. | `allow` |
+| `operation_mode` | string | Yes | Execution mode gate. | Enum: `plan_only`, `apply_enabled`. | `plan_only` |
+| `priority` | string | Yes | Processing urgency class. | Enum: `low`, `normal`, `high`, `urgent`. | `normal` |
+| `flows` | array<object> | Yes | Requested traffic/service entries. | Min 1 element; each entry must pass flow rules below. | See `flow_entry` rows. |
+| `flows[].flow_id` | string | Yes | Client-visible flow reference. | Non-empty; unique within request. | `flow-001` |
+| `flows[].src` | string | Yes | Canonical source object token. | Non-empty; object token, not raw IP literal. | `net-frontend` |
+| `flows[].dst` | string | Yes | Canonical destination object token. | Non-empty; object token, not raw IP literal. | `obj-appA` |
+| `flows[].service` | string | Yes | Canonical service token. | Non-empty; service catalog token. | `svc-https` |
+| `flows[].direction` | string | Yes | Traffic direction semantics. | Enum: `ingress`, `egress`, `east_west`. | `ingress` |
+| `flows[].application_id` | string | Optional | Application registry reference. | Slug format; max 64 chars. | `app-payments-ui` |
+| `flows[].comment` | string | Optional | Human rationale note per flow. | Max 512 chars. | `Allow frontend to app over HTTPS.` |
+| `justification` | string | Yes | Business/security justification. | Non-empty; min 15 chars recommended. | `New payment API path requires approved frontend connectivity.` |
+| `expiry` | string(timestamp) | Conditional | Exception expiry date/time. | Required for temporary exceptions or `risk_class=exception`; UTC ISO-8601; future time. | `2026-06-30T23:59:59Z` |
+| `time_window` | object | Optional | Allowed execution window constraints. | If present, requires `start` and `end` UTC timestamps; `start < end`. | `{"start":"2026-04-09T01:00:00Z","end":"2026-04-09T03:00:00Z"}` |
+| `compliance_tags` | array<string> | Optional | Regulatory/control tags. | Allowed examples: `pci`, `swift`, `sox`; deduplicated values. | `["pci","swift"]` |
+| `required_approvals` | integer | Yes | Minimum number of approvals needed. | Integer >=1; policy may require >=2 for prod/high risk. | `2` |
+| `approver_roles` | array<string> | Yes | Roles allowed/required to approve. | Min 1; enum subset: `security`, `network`, `application_owner`, `risk`. | `["security","network"]` |
+| `segregation_of_duties_flags` | object | Optional | SoD control toggles/assertions. | Boolean values only if present. | `{"requester_cannot_approve":true}` |
+| `labels` | array<string> | Optional | Freeform metadata tags. | Max 20 entries; each max 64 chars. | `["portfolio-demo","quarterly-change"]` |
+| `cost_center` | string | Optional | Chargeback/cost attribution. | Pattern `^cc-[0-9]{4}$` preferred. | `cc-1042` |
+| `risk_class` | string | Optional | Risk class for governance behavior. | Enum: `standard`, `elevated`, `exception`. | `standard` |
+
+## 5) Mandatory minimum set for an actionable request
+
+### 5.1 Minimum required to reach **Planned**
+The following must be present and valid:
+- Identity: `change_request_id`, `idempotency_key`, `source_system`, `source_reference_id`
+- Actors: `requester.id`, `business_owner.id`, `technical_owner.id`
+- Scope: `environment`, `firewall_domain`, and one of (`device_group` or `policy_scope`)
+- Intent: `action`, `operation_mode`, `priority`
+- Flows: at least one valid flow entry with `flow_id`, `src`, `dst`, `service`, `direction`
+- Constraints: `justification`
+- Governance: `required_approvals`, `approver_roles`
+
+### 5.2 Additional required to reach **Applied**
+In addition to Planned minimum:
+- `operation_mode` must be `apply_enabled`
+- Required approval evidence must exist in `ApprovalRecord` count/roles according to governance policy
+- Any policy-mandated execution window constraints must be satisfied at runtime (`time_window` if required by policy)
+- If exception/risk policy applies, `expiry` must be present and valid future timestamp
+
+### 5.3 Additional required to reach **Verified** and **Closed**
+In addition to Applied requirements:
+- `PolicySnapshot` captured pre/post apply for targeted `firewall_domain`
+- `VerificationResult.match_status` evaluated and persisted
+- At least one `AuditEvent` for each state transition
+- Artifact references generated and stored for validation/plan/verify outcomes
+
+### 5.4 Mandatory-field failure rule
+If mandatory fields are missing or invalid at any gate:
+- validation fails,
+- state transition is blocked,
+- an `AuditEvent` is emitted with failure severity and reason class.
+
+## 6) ApprovalRecord v1 field model
+| Field name | Type | Required | Description | Validation rules | Example |
+|---|---|---|---|---|---|
+| `approval_record_id` | string | Yes | Approval evidence identifier. | Regex `^apr-[0-9]{4}-[0-9]{6}-[0-9]{2}$` preferred. | `apr-2026-000321-01` |
+| `change_request_id` | string | Yes | Parent request reference. | Must reference existing `ChangeRequest.change_request_id`. | `crq-2026-000321` |
+| `decision` | string | Yes | Approval decision. | Enum: `approved`, `rejected`, `conditional`. | `approved` |
+| `approver_id` | string | Yes | Approver identity. | Non-empty. | `usr-sec-003` |
+| `approver_role` | string | Yes | Governance role of approver. | Enum subset: `security`, `network`, `application_owner`, `risk`. | `security` |
+| `timestamp` | string(timestamp) | Yes | Decision time. | UTC ISO-8601. | `2026-04-08T15:00:00Z` |
+| `rationale` | string | Yes | Decision explanation. | Non-empty; min 10 chars recommended. | `Control review complete; approved for production window.` |
+| `conditions` | array<string> | Optional | Conditions attached to approval. | Max 20 items. | `["apply within approved window"]` |
+| `expiry` | string(timestamp) | Optional | Approval validity end. | UTC ISO-8601; future timestamp if set. | `2026-04-15T00:00:00Z` |
+| `delegation` | object | Optional | Delegated authority metadata. | If present include `delegated_by` and `reason`. | `{"delegated_by":"usr-risk-001","reason":"on_call rotation"}` |
+| `evidence_links` | array<string> | Optional | Synthetic artifact refs. | Use internal reference URIs/keys only. | `["artifact://approvals/apr-2026-000321-01.json"]` |
+
+## 7) PolicySnapshot v1 field model
+| Field name | Type | Required | Description | Validation rules | Example |
+|---|---|---|---|---|---|
+| `snapshot_id` | string | Yes | Snapshot identifier. | Non-empty; unique per capture event. | `psn-fw-core-2026-04-08T153000Z` |
+| `firewall_domain` | string | Yes | Captured policy domain. | Must match canonical domain taxonomy. | `fw-domain-core` |
+| `capture_time` | string(timestamp) | Yes | Snapshot capture timestamp. | UTC ISO-8601. | `2026-04-08T15:30:00Z` |
+| `source` | string | Yes | Snapshot source system. | Enum: `firewall`, `tufin`, `mock`. | `mock` |
+| `normalized_policy_hash` | string | Yes | Deterministic hash of normalized effective state. | Non-empty hex/string; stable for identical state. | `hash-a13f77c8` |
+| `rule_inventory_summary` | object | Optional | Aggregated rule statistics. | Numeric counts only. | `{"total_rules":1240,"disabled_rules":31}` |
+| `object_inventory_summary` | object | Optional | Aggregated object statistics. | Numeric counts only. | `{"network_objects":420,"service_objects":95}` |
+| `raw_reference` | string | Optional | Pointer to raw source evidence (not raw config payload). | Internal reference token/URI only. | `artifact://snapshots/fw-core/2026-04-08T153000Z` |
+| `confidence_score` | number | Optional | Confidence in normalization completeness. | Range `0.0` to `1.0`. | `0.98` |
+
+## 8) MappingReport v1 field model (normalization lineage)
+| Field name | Type | Required | Description | Validation rules | Example |
+|---|---|---|---|---|---|
+| `mapping_report_id` | string | Yes | Mapping lineage identifier. | Non-empty; unique per normalization run. | `map-demo-servicenow-2026-000321` |
+| `change_request_id` | string | Yes | Canonical request produced by mapping. | Must match generated `ChangeRequest`. | `crq-2026-000321` |
+| `source_payload_refs` | array<string> | Yes | References to source payloads/records. | Min 1; synthetic refs only. | `["src://servicenow/change/sn-chg-900321"]` |
+| `mapped_fields` | array<string> | Yes | Canonical field paths successfully populated. | Min 1. | `["change_request_id","flows[0].service"]` |
+| `missing_fields` | array<string> | Yes | Required canonical paths missing from source. | Can be empty list if none missing. | `[]` |
+| `assumptions_defaults_applied` | array<string> | Yes | Defaulting/assumption list used during mapping. | Explicit text entries required even when none (`[]`). | `["environment defaulted to prod by source profile"]` |
+| `ambiguity_flags` | array<string> | Yes | Ambiguities requiring review or policy handling. | Explicit list required; may be empty. | `[]` |
+| `enrichment_sources` | array<string> | Optional | Additional non-authoritative enrichment inputs. | Synthetic source names only. | `["cmdb_service_catalog"]` |
+| `confidence_score` | number | Optional | Mapper confidence score. | Range `0.0` to `1.0`. | `0.93` |
+
+## 9) AuditEvent v1 field model
+| Field name | Type | Required | Description | Validation rules | Example |
+|---|---|---|---|---|---|
+| `event_id` | string | Yes | Event identifier. | Non-empty, unique. | `evt-9ab41d2f` |
+| `change_request_id` | string | Yes | Correlated request identifier. | Must reference existing request. | `crq-2026-000321` |
+| `event_type` | string | Yes | Event class. | Enum: `state_transition`, `validation_failure`, `adapter_call`, `verification_result`, `drift_detected`. | `state_transition` |
+| `state_from` | string | Yes | Prior lifecycle state. | Enum from lifecycle set; use `none` for initial ingest. | `validated` |
+| `state_to` | string | Yes | New lifecycle state. | Enum from lifecycle set. | `approved` |
+| `timestamp` | string(timestamp) | Yes | Event time. | UTC ISO-8601. | `2026-04-08T15:05:00Z` |
+| `severity` | string | Yes | Event severity level. | Enum: `info`, `warning`, `error`, `critical`. | `info` |
+| `message` | string | Yes | Human-readable event summary. | Non-empty. | `Required approvals satisfied; moved to approved state.` |
+| `correlation_ids` | object | Optional | Cross-system correlation metadata. | Key-value string map. | `{"trace_id":"trc-01","idempotency_key":"idem-1c90d4f8f6"}` |
+| `adapter_invocation_ids` | array<string> | Optional | Adapter call references. | String list; max 100 entries. | `["adp-fw-00092"]` |
+| `error_class` | string | Optional | Error category. | Enum examples: `validation_error`, `policy_conflict`, `adapter_timeout`. | `validation_error` |
+| `artifact_refs` | array<string> | Optional | Related artifact pointers. | Internal refs only. | `["artifact://validation/crq-2026-000321.json"]` |
+
+## 10) Internal artifact fields (engine outputs)
+
+### 10.1 PolicyPlan minimal fields
+- `plan_id` (string)
+- `change_request_id` (string)
+- `operations` (array of normalized operations)
+- `plan_hash` (string)
+- `generated_time` (UTC ISO-8601 timestamp)
+
+### 10.2 VerificationResult minimal fields
+- `verification_id` (string)
+- `plan_id` (string)
+- `snapshot_before_id` (string)
+- `snapshot_after_id` (string)
+- `match_status` (enum: `match`, `mismatch`, `partial_match`)
+- `mismatches` (array of mismatch descriptors)
+
+### 10.3 DriftFinding minimal fields
+- `drift_id` (string)
+- `firewall_domain` (string)
+- `baseline_snapshot_id` (string)
+- `current_snapshot_id` (string)
+- `drift_type` (string; e.g., `rule_added`, `rule_removed`, `rule_modified`)
+- `severity` (enum: `low`, `medium`, `high`, `critical`)
+
+## 11) Validation rules and failure behavior
+
+### 11.1 Field-level validation
+- Enforce types (string/object/array/integer/number/boolean).
+- Enforce non-empty required strings and minimum list lengths.
+- Enforce allowed enums (`action`, `operation_mode`, `priority`, `decision`, state names, severity).
+- Enforce identifier and timestamp patterns.
+
+### 11.2 Governance validation
+- `expiry` required when request is an exception/temporary allowance.
+- `business_owner` and `technical_owner` required for accountable governance.
+- `required_approvals` and role coverage required before `Approved`.
+- SoD controls (for example requester cannot self-approve) enforced by policy gates.
+
+### 11.3 Idempotency behavior
+- Duplicate submission with same `idempotency_key` and equivalent canonical payload:
+  - must not produce duplicate apply effects,
+  - should return/associate existing processing context.
+- Duplicate key with materially different payload:
+  - validation/policy conflict event emitted,
+  - request blocked pending operator review.
+
+### 11.4 Concurrency and locking notes
+- Engine applies per-`firewall_domain` change lock concept during plan/apply windows.
+- Concurrent changes targeting same domain/scope are serialized or rejected with retry guidance.
+- Lock outcomes are captured in `AuditEvent` and observability metrics.
+
+## 12) Example canonical ChangeRequest payloads (synthetic)
+
+### 12.1 Minimal actionable example for Planned
+```json
+{
+  "change_request_id": "crq-2026-000321",
+  "idempotency_key": "idem-1c90d4f8f6",
+  "source_system": "servicenow",
+  "source_reference_id": "sn-chg-900321",
+  "requester": {"id": "usr-req-001", "email": "requester@example.invalid"},
+  "business_owner": {"id": "usr-biz-010"},
+  "technical_owner": {"id": "usr-tech-020"},
+  "environment": "prod",
+  "firewall_domain": "fw-domain-core",
+  "policy_scope": "zone-internet-to-app",
+  "action": "allow",
+  "operation_mode": "plan_only",
+  "priority": "normal",
+  "flows": [
+    {
+      "flow_id": "flow-001",
+      "src": "net-frontend",
+      "dst": "obj-appA",
+      "service": "svc-https",
+      "direction": "ingress",
+      "comment": "Permit frontend to app over HTTPS."
+    }
+  ],
+  "justification": "Approved release requires frontend-to-app API connectivity.",
+  "required_approvals": 2,
+  "approver_roles": ["security", "network"],
+  "labels": ["portfolio-demo"]
+}
+```
+
+### 12.2 Applied/Verified-ready example (with apply_enabled and approvals context)
+```json
+{
+  "change_request_id": "crq-2026-000322",
+  "idempotency_key": "idem-4f1193ce2a",
+  "source_system": "api",
+  "source_reference_id": "api-req-20260408-22",
+  "requester": {"id": "usr-req-002"},
+  "business_owner": {"id": "usr-biz-011"},
+  "technical_owner": {"id": "usr-tech-021"},
+  "environment": "prod",
+  "firewall_domain": "fw-domain-core",
+  "device_group": "edge-dc1",
+  "action": "modify",
+  "operation_mode": "apply_enabled",
+  "priority": "high",
+  "flows": [
+    {
+      "flow_id": "flow-101",
+      "src": "net-partner-a",
+      "dst": "obj-appA",
+      "service": "svc-https",
+      "direction": "ingress",
+      "application_id": "app-payments-ui"
+    }
+  ],
+  "justification": "Migration wave requires updated partner ingress policy.",
+  "time_window": {
+    "start": "2026-04-10T01:00:00Z",
+    "end": "2026-04-10T03:00:00Z"
+  },
+  "compliance_tags": ["pci"],
+  "required_approvals": 2,
+  "approver_roles": ["security", "network"],
+  "segregation_of_duties_flags": {"requester_cannot_approve": true},
+  "risk_class": "standard",
+  "labels": ["wave-2", "controlled-change"],
+  "approval_records": [
+    {
+      "approval_record_id": "apr-2026-000322-01",
+      "decision": "approved",
+      "approver_id": "usr-sec-003",
+      "approver_role": "security",
+      "timestamp": "2026-04-09T18:20:00Z",
+      "rationale": "Security review completed; no blocking issues."
+    },
+    {
+      "approval_record_id": "apr-2026-000322-02",
+      "decision": "approved",
+      "approver_id": "usr-net-004",
+      "approver_role": "network",
+      "timestamp": "2026-04-09T18:25:00Z",
+      "rationale": "Network policy impact assessed and accepted."
+    }
+  ]
+}
+```
+
+## 13) Integration boundary notes
+
+### 13.1 Normalization boundary
+Client-native payloads (CMDB, ServiceNow-like tickets, or custom intake APIs) must be normalized into:
+- canonical `ChangeRequest`
+- canonical `MappingReport`
+
+before entering core engine processing.
+
+This keeps the core stable against client schema variance and preserves deterministic behavior.
+
+### 13.2 Adapter consumption of canonical fields
+- **ticket port**: reads source references, writes workflow/approval status back to ticketing systems.
+- **firewall port**: consumes `PolicyPlan.operations` and target scope (`firewall_domain`, `device_group`/`policy_scope`) for apply/verify flows.
+- **policy port**: consumes normalized intent and policy state for planning/reconciliation logic.
+- **secrets port**: retrieves runtime credentials/tokens only; no secret material in canonical artifacts.
+- **artifact port**: persists validation outputs, plans, verification reports, and drift artifacts.
+- **observability port**: emits transition events, metrics, and correlation fields at each lifecycle step.
