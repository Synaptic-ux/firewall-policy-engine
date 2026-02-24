from engine.core.reconcile import reconcile_snapshots


def reconcile(firewall_domain: str, baseline: dict, current: dict) -> dict:
    return reconcile_snapshots(firewall_domain, baseline, current)
