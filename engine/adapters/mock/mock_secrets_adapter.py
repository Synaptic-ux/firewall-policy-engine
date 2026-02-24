from engine.ports.secrets_port import SecretsPort


class MockSecretsAdapter(SecretsPort):
    def get_secret(self, name: str) -> str:
        return f"dummy-{name.lower()}"
