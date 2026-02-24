from engine.ports.observability_port import ObservabilityPort
from engine.utils.structured_logging import log


class MockObservabilityAdapter(ObservabilityPort):
    def emit_event(self, event: dict) -> None:
        log("info", "audit_event", event=event)
