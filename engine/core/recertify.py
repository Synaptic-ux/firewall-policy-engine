def build_recertification_queue(rule_metadata: list[dict], as_of: str) -> dict:
    due = []
    for item in rule_metadata:
        if not item.get("owner") or not item.get("expiry") or item.get("expiry") <= as_of:
            due.append(item)
    return {"as_of": as_of, "due_count": len(due), "items": due}
