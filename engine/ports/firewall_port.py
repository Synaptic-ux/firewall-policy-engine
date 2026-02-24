from abc import ABC, abstractmethod


class FirewallPort(ABC):
    @abstractmethod
    def read_policy_snapshot(self, snapshot_ref: str):
        raise NotImplementedError

    @abstractmethod
    def apply_plan(self, plan: dict):
        raise NotImplementedError
