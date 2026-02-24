from abc import ABC, abstractmethod


class ObservabilityPort(ABC):
    @abstractmethod
    def emit_event(self, event: dict) -> None:
        raise NotImplementedError
