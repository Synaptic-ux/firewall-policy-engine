from abc import ABC, abstractmethod


class ArtifactPort(ABC):
    @abstractmethod
    def write_artifact(self, artifact_type: str, filename: str, payload: dict) -> str:
        raise NotImplementedError
