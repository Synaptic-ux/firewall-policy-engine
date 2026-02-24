import unittest

from engine.core.workflow_state_machine import transition


class WorkflowStateTests(unittest.TestCase):
    def test_valid_transition(self):
        transition("Draft", "Validated")

    def test_invalid_transition(self):
        with self.assertRaises(ValueError):
            transition("Draft", "Closed")


if __name__ == "__main__":
    unittest.main()
