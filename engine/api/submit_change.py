from engine.core.engine import run_scenario


def submit_change(scenario: dict, run_id: str = "api-run") -> dict:
    return run_scenario(scenario, run_id=run_id)
