def apply_plan(change_request: dict, plan: dict, firewall_adapter) -> dict:
    if change_request.get("operation_mode", "plan_only") != "apply_enabled":
        return {"status": "skipped", "reason": "plan_only"}
    return firewall_adapter.apply_plan(plan)
