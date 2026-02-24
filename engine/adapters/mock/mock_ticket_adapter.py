import json
from pathlib import Path

from engine.ports.ticket_port import TicketPort


class MockTicketAdapter(TicketPort):
    def __init__(self, fixture_root: str = "demo/fixtures/approvals") -> None:
        self.fixture_root = Path(fixture_root)

    def fetch_approvals(self, change_request_id: str):
        path = self.fixture_root / f"{change_request_id}.json"
        if not path.exists():
            return []
        return json.loads(path.read_text())
