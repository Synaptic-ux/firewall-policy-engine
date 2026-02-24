import json
import unittest
from pathlib import Path


class SchemaPresenceTests(unittest.TestCase):
    def test_schemas_exist_and_valid_json(self):
        names = [
            "ChangeRequest.schema.json",
            "ApprovalRecord.schema.json",
            "AuditEvent.schema.json",
            "PolicySnapshot.schema.json",
            "MappingReport.schema.json",
        ]
        for name in names:
            p = Path("schemas/v1") / name
            self.assertTrue(p.exists(), msg=f"missing {p}")
            data = json.loads(p.read_text())
            self.assertIn("$schema", data)


if __name__ == "__main__":
    unittest.main()
