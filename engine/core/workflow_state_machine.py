ALLOWED = {
    "Draft": {"Validated"},
    "Validated": {"Approved"},
    "Approved": {"Planned"},
    "Planned": {"Applied", "Verified"},
    "Applied": {"Verified"},
    "Verified": {"Closed"},
    "Closed": set(),
}


def transition(current: str, nxt: str) -> None:
    if nxt not in ALLOWED.get(current, set()):
        raise ValueError(f"invalid transition {current} -> {nxt}")
