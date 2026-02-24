from engine.utils.hashing import stable_hash
from engine.utils.time_utils import utc_now


def generate_plan(change_request: dict, snapshot_before: dict) -> dict:
    operations = []
    for flow in change_request.get("flows", []):
        operations.append({
            "op": change_request.get("action"),
            "src": flow["src"],
            "dst": flow["dst"],
            "service": flow["service"],
            "direction": flow["direction"],
        })
    plan_seed = {"change_request_id": change_request["change_request_id"], "operations": operations}
    return {
        "plan_id": f"pln-{change_request['change_request_id']}",
        "change_request_id": change_request["change_request_id"],
        "operations": operations,
        "plan_hash": stable_hash(plan_seed),
        "generated_time": utc_now(),
        "snapshot_before": snapshot_before,
    }
