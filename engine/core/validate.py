def validate_change_request(change_request: dict, mapping_report: dict) -> list[str]:
    errors = []
    required = [
        "change_request_id","idempotency_key","source_system","source_reference_id",
        "requester","business_owner","technical_owner","environment","firewall_domain",
        "action","operation_mode","priority","flows","justification","required_approvals","approver_roles"
    ]
    for f in required:
        if f not in change_request or change_request[f] in (None, "", []):
            errors.append(f"missing:{f}")
    if "device_group" not in change_request and "policy_scope" not in change_request:
        errors.append("missing:device_group_or_policy_scope")
    if not isinstance(change_request.get("flows", []), list) or len(change_request.get("flows", [])) < 1:
        errors.append("invalid:flows")
    if mapping_report.get("change_request_id") != change_request.get("change_request_id"):
        errors.append("mapping_report_mismatch")
    return errors


def approvals_sufficient(change_request: dict, approvals: list[dict]) -> bool:
    approved = [a for a in approvals if a.get("decision") == "approved"]
    needed = int(change_request.get("required_approvals", 1))
    roles_needed = set(change_request.get("approver_roles", []))
    roles_have = {a.get("approver_role") for a in approved}
    return len(approved) >= needed and roles_needed.issubset(roles_have)
