import json
from pathlib import Path

from engine.adapters.mock.mock_artifact_adapter import MockArtifactAdapter
from engine.adapters.mock.mock_firewall_adapter import MockFirewallAdapter
from engine.adapters.mock.mock_observability_adapter import MockObservabilityAdapter
from engine.adapters.mock.mock_ticket_adapter import MockTicketAdapter
from engine.core.apply import apply_plan
from engine.core.plan import generate_plan
from engine.core.recertify import build_recertification_queue
from engine.core.reconcile import reconcile_snapshots
from engine.core.validate import approvals_sufficient, validate_change_request
from engine.core.verify import verify_plan
from engine.core.workflow_state_machine import transition
from engine.utils.time_utils import utc_now


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text())


def _audit(change_request_id: str, event_type: str, state_from: str, state_to: str, message: str) -> dict:
    return {
        "event_id": f"evt-{change_request_id}-{state_to.lower()}",
        "change_request_id": change_request_id,
        "event_type": event_type,
        "state_from": state_from,
        "state_to": state_to,
        "timestamp": utc_now(),
        "severity": "info",
        "message": message,
    }


def run_scenario(scenario: dict, run_id: str = "run-001") -> dict:
    artifact = MockArtifactAdapter()
    obs = MockObservabilityAdapter()
    firewall = MockFirewallAdapter()
    ticket = MockTicketAdapter()

    cr = _load(scenario["change_request"])
    mr = _load(scenario["mapping_report"])
    baseline = _load(scenario["baseline_snapshot"])

    state = "Draft"
    events = []

    errors = validate_change_request(cr, mr)
    validation_report = {"change_request_id": cr["change_request_id"], "errors": errors, "valid": not errors}
    artifact.write_artifact("validation", f"{cr['change_request_id']}-{run_id}.json", validation_report)
    if errors:
        ev = _audit(cr["change_request_id"], "validation_failure", state, state, ";".join(errors))
        obs.emit_event(ev); events.append(ev)
        artifact.write_artifact("audit", f"{cr['change_request_id']}-{run_id}-validation_fail.json", ev)
        return {"status": "failed_validation", "errors": errors}

    transition(state, "Validated"); ev = _audit(cr["change_request_id"], "state_transition", state, "Validated", "validation passed"); state = "Validated"
    obs.emit_event(ev); events.append(ev)

    approvals = ticket.fetch_approvals(cr["change_request_id"])
    artifact.write_artifact("approvals", f"{cr['change_request_id']}-{run_id}.json", {"records": approvals})
    if not approvals_sufficient(cr, approvals):
        fail = _audit(cr["change_request_id"], "approval_failure", state, state, "missing approvals")
        fail["severity"] = "error"
        obs.emit_event(fail)
        artifact.write_artifact("audit", f"{cr['change_request_id']}-{run_id}-approval_fail.json", fail)
        return {"status": "failed_approval"}

    transition(state, "Approved"); ev = _audit(cr["change_request_id"], "state_transition", state, "Approved", "approvals satisfied"); state = "Approved"
    obs.emit_event(ev); events.append(ev)

    plan = generate_plan(cr, baseline)
    artifact.write_artifact("plans", f"{cr['change_request_id']}-{run_id}.json", plan)
    artifact.write_artifact("diffs", f"{cr['change_request_id']}-{run_id}.json", {"operations": plan["operations"]})
    transition(state, "Planned"); ev = _audit(cr["change_request_id"], "state_transition", state, "Planned", "plan generated"); state = "Planned"
    obs.emit_event(ev); events.append(ev)

    apply_result = apply_plan(cr, plan, firewall)
    after_snapshot = baseline
    if apply_result.get("status") == "applied":
        after_snapshot = apply_result["snapshot_after"]
        transition(state, "Applied"); ev = _audit(cr["change_request_id"], "state_transition", state, "Applied", "plan applied"); state = "Applied"
        obs.emit_event(ev); events.append(ev)
    artifact.write_artifact("verification", f"{cr['change_request_id']}-{run_id}-apply.json", apply_result)

    verification = verify_plan(plan, baseline, after_snapshot)
    artifact.write_artifact("verification", f"{cr['change_request_id']}-{run_id}.json", verification)
    transition(state, "Verified"); ev = _audit(cr["change_request_id"], "state_transition", state, "Verified", "verification complete"); state = "Verified"
    obs.emit_event(ev); events.append(ev)

    current_ref = scenario.get("current_snapshot")
    current = _load(current_ref) if current_ref else after_snapshot
    drift = reconcile_snapshots(cr["firewall_domain"], baseline, current)
    artifact.write_artifact("drift", f"{cr['change_request_id']}-{run_id}.json", drift)

    metadata = _load(scenario["rule_metadata"])
    recert = build_recertification_queue(metadata, as_of=scenario.get("as_of", utc_now()))
    artifact.write_artifact("recertification", f"{cr['change_request_id']}-{run_id}.json", recert)

    transition(state, "Closed"); ev = _audit(cr["change_request_id"], "state_transition", state, "Closed", "workflow closed"); state = "Closed"
    obs.emit_event(ev); events.append(ev)
    artifact.write_artifact("audit", f"{cr['change_request_id']}-{run_id}.json", {"events": events})

    return {"status": state, "change_request_id": cr["change_request_id"], "run_id": run_id}
