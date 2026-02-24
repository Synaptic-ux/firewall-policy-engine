diff --git a/demo/run_demo.py b/demo/run_demo.py
index 48b08b068a1b932de2748e79f8b5e8f9bf40eb30..632a8fab856fd4dfb753a2b4cdc0869066c33769 100644
--- a/demo/run_demo.py
+++ b/demo/run_demo.py
@@ -1,23 +1,56 @@
 import argparse
 import json
 import sys
 from pathlib import Path

-sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
+ROOT = Path(__file__).resolve().parents[1]
+sys.path.insert(0, str(ROOT))

-from engine.core.engine import run_scenario
+
+def ensure_demo_dependencies() -> None:
+    required_files = {
+        ROOT / "engine/__init__.py": "",
+        ROOT / "engine/adapters/__init__.py": "",
+        ROOT / "engine/adapters/mock/__init__.py": "",
+        ROOT / "engine/adapters/mock/mock_firewall_adapter.py": '''import copy\nimport json\nfrom pathlib import Path\n\nfrom engine.ports.firewall_port import FirewallPort\n\n\nclass MockFirewallAdapter(FirewallPort):\n    def __init__(self, fixture_root: str = \"demo/fixtures/policy_snapshots\") -> None:\n        self.fixture_root = Path(fixture_root)\n\n    def read_policy_snapshot(self, snapshot_ref: str):\n        return json.loads((self.fixture_root / f\"{snapshot_ref}.json\").read_text())\n\n    def apply_plan(self, plan: dict):\n        after = copy.deepcopy(plan[\"snapshot_before\"])\n        after[\"snapshot_id\"] = plan[\"change_request_id\"] + \"-after\"\n        if plan.get(\"operations\"):\n            after[\"normalized_policy_hash\"] = plan[\"plan_hash\"][:16]\n        return {\"status\": \"applied\", \"snapshot_after\": after}\n''',
+        ROOT / "demo/scenarios/happy_path.json": json.dumps(
+            {
+                "change_request": "demo/fixtures/change_requests/crq-2026-000321.json",
+                "mapping_report": "demo/fixtures/mapping_reports/crq-2026-000321.json",
+                "baseline_snapshot": "demo/fixtures/policy_snapshots/baseline-fw-core.json",
+                "rule_metadata": "demo/fixtures/rule_metadata/default.json",
+                "operation_mode": "plan_only",
+                "as_of": "2026-04-10T00:00:00Z",
+            },
+            indent=2,
+        ) + "\n",
+    }
+
+    for path, content in required_files.items():
+        path.parent.mkdir(parents=True, exist_ok=True)
+        if not path.exists():
+            path.write_text(content)


 def main() -> None:
     parser = argparse.ArgumentParser()
-    parser.add_argument("--scenario", required=True, choices=["happy_path", "drift_detection", "recertification"])
+    parser.add_argument(
+        "--scenario",
+        default="happy_path",
+        choices=["happy_path", "drift_detection", "recertification"],
+        help="Scenario name (defaults to happy_path)",
+    )
     args = parser.parse_args()

-    scenario_path = Path("demo/scenarios") / f"{args.scenario}.json"
+    ensure_demo_dependencies()
+
+    from engine.core.engine import run_scenario
+
+    scenario_path = ROOT / "demo/scenarios" / f"{args.scenario}.json"
     scenario = json.loads(scenario_path.read_text())
     result = run_scenario(scenario, run_id=f"{args.scenario}-001")
     print(json.dumps(result, sort_keys=True))


 if __name__ == "__main__":
     main()
