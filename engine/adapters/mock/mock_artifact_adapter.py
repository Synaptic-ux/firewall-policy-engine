import json
from pathlib import Path

from engine.ports.artifact_port import ArtifactPort


class MockArtifactAdapter(ArtifactPort):
    def __init__(self, root: str = "out") -> None:
        self.root = Path(root)

    def write_artifact(self, artifact_type: str, filename: str, payload: dict) -> str:
        target = self.root / artifact_type
        target.mkdir(parents=True, exist_ok=True)
        path = target / filename
        path.write_text(json.dumps(payload, indent=2, sort_keys=True))
        return str(path)
