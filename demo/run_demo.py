import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.core.engine import run_scenario


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True, choices=["happy_path", "drift_detection", "recertification"])
    args = parser.parse_args()

    scenario_path = Path("demo/scenarios") / f"{args.scenario}.json"
    scenario = json.loads(scenario_path.read_text())
    result = run_scenario(scenario, run_id=f"{args.scenario}-001")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
