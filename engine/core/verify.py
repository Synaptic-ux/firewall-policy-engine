from engine.utils.time_utils import utc_now


def verify_plan(plan: dict, before: dict, after: dict) -> dict:
    match = before.get("normalized_policy_hash") != after.get("normalized_policy_hash")
    return {
        "verification_id": f"ver-{plan['change_request_id']}",
        "plan_id": plan["plan_id"],
        "snapshot_before_id": before.get("snapshot_id"),
        "snapshot_after_id": after.get("snapshot_id"),
        "match_status": "match" if match else "mismatch",
        "mismatches": [] if match else ["no_effect_detected"],
        "timestamp": utc_now(),
    }
