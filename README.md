Purpose
firewall-policy-engine is a canonical, contract-first firewall governance automation engine. It models firewall policy change as an auditable workflow and produces deterministic artifacts for validation, approval, planning, application, verification, reconciliation, and recertification. External integrations such as ServiceNow or CMDB systems, NSPM platforms like Tufin, firewall vendor APIs, and secrets backends are implemented through adapter interfaces and are placeholders in the public demo version.

Scope
This repository focuses on the governance control plane, not vendor-specific configuration syntax. It defines canonical contracts, workflow logic, and reconciliation mechanisms. All external systems must conform to the defined ports and schemas before interacting with the engine.

What this repository demonstrates
It demonstrates a canonical ChangeRequest contract used to drive all firewall governance automation.
It implements a workflow state machine with states Draft, Validated, Approved, Planned, Applied, Verified, and Closed.
It enforces separation between plan and apply phases.
It generates auditable artifacts such as validation reports, approval records, policy diffs, and verification reports.
It performs reconciliation between expected policy state and effective firewall state to detect drift.
It supports recertification logic based on rule ownership, justification, and expiry metadata.

High level repository layout
Root contains the main documentation and configuration files.
The docs directory contains architectural and integration documentation.
The schemas directory contains versioned canonical contracts.
The engine directory contains core workflow logic, validation, reconciliation, and adapter interfaces.
The demo directory contains a deterministic demo harness with fixtures and predefined scenarios.
The out directory is generated at runtime and contains artifacts produced by demo runs.
The tests directory contains unit, integration, and contract tests.
The .github directory contains CI workflow definitions.

Documentation directory
HLD_Canonical_Graph_and_System_Relationships.md describes the canonical data model, system relationships, and data flows between ticketing systems, policy controllers, firewall providers, secrets backends, and artifact storage.
LLD_Variables_and_Mandatory_Fields.md describes the canonical variables, mandatory and optional fields, validation rules, idempotency logic, and processing requirements for actionable change requests.
INTEGRATION_Plugging_APIs_and_Secrets.md explains how to implement adapters for client environments and how to inject secrets securely at runtime.
REPO_Structure_and_File_Index.md contains a detailed description of each directory and file in the repository.

Schemas directory
This directory contains versioned canonical contracts including ChangeRequest, ApprovalRecord, AuditEvent, PolicySnapshot, and MappingReport.
All inputs must be normalized into these schemas before processing by the engine.
All outputs produced by the engine conform to these contracts to ensure traceability and compatibility.

Engine directory
The api subdirectory exposes endpoints or callable entry points for change submission, reporting, and reconciliation.
The core subdirectory implements the workflow state machine, validation logic, planning logic, apply logic, verification logic, reconciliation logic, and recertification logic.
The ports subdirectory defines interfaces for all external dependencies such as ticket stores, policy controllers, firewall providers, secrets providers, artifact stores, and observability sinks.
The adapters subdirectory contains mock implementations of the defined ports to allow deterministic local execution without real infrastructure.
The utils subdirectory contains helper modules such as hashing, time utilities, and structured logging.

Demo directory
The demo directory provides a runnable environment that uses predefined fixtures compatible with the canonical schemas.
Fixtures represent synthetic change requests, policy snapshots, and rule metadata.
Scenarios include a happy path change lifecycle, a drift detection case, and a recertification case.
The demo runner executes scenarios end to end using mock adapters and writes generated artifacts to the out directory.

Artifacts produced during execution
Validation reports describing whether a change request meets schema and policy requirements.
Approval records documenting who approved a change and when.
Policy plans representing normalized intended changes.
Policy diffs comparing previous and intended state.
Verification results confirming that applied state matches the planned state.
Drift reports identifying out of band changes.
Recertification queues listing rules due for review.

What this repository intentionally does not include
It does not contain real ServiceNow, CMDB, Tufin, Palo Alto, or Check Point credentials.
It does not contain real client data models.
It does not contain production Terraform, AWS, or secrets configuration.
All such integrations must be implemented through the defined ports and injected at runtime.

Relationship to companion repositories
firewall-policy-library contains vendor agnostic policy definitions, baseline controls, exception models, and recertification rules.
firewall-vendor-adapters contains vendor specific translation layers and contract tested implementations of the firewall provider interface.
firewall-policy-engine consumes canonical contracts and remains independent of vendor and client specifics.

Execution model
All change requests must conform to the canonical ChangeRequest schema before processing.
The engine validates the request, generates a plan, optionally applies the plan through the firewall provider interface, verifies the resulting state, and emits audit artifacts.
Reconciliation compares expected state with effective policy state and produces drift findings.
Recertification logic evaluates rule metadata and generates review queues.

Roadmap
Initial version provides canonical schemas, workflow skeleton, mock adapters, and a happy path scenario.
Subsequent versions extend reconciliation and recertification logic.
Later versions add adapter stubs for real systems and reference integration guidance.