from abc import ABC, abstractmethod


class TicketPort(ABC):
    @abstractmethod
    def fetch_approvals(self, change_request_id: str):
        raise NotImplementedError
