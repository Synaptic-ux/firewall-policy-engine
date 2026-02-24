def reconcile_snapshots(firewall_domain: str, baseline: dict, current: dict) -> dict:
    drift = baseline.get("normalized_policy_hash") != current.get("normalized_policy_hash")
    return {
        "drift_id": f"drf-{firewall_domain}",
        "firewall_domain": firewall_domain,
        "baseline_snapshot_id": baseline.get("snapshot_id"),
        "current_snapshot_id": current.get("snapshot_id"),
        "drift_type": "hash_changed" if drift else "none",
        "severity": "medium" if drift else "low",
    }
