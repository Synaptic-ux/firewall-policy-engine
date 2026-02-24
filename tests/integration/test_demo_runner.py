import json
import subprocess
import sys
import unittest
from pathlib import Path


class DemoRunnerTests(unittest.TestCase):
    def test_happy_path_runs(self):
        cmd = [sys.executable, "demo/run_demo.py", "--scenario", "happy_path"]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        payload = json.loads(result.stdout.strip().splitlines()[-1])
        self.assertEqual(payload["status"], "Closed")
        self.assertTrue(Path("out/plans/crq-2026-000321-happy_path-001.json").exists())


if __name__ == "__main__":
    unittest.main()
