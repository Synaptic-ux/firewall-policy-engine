diff --git a/tests/unit/test_workflow_state_machine.py b/tests/unit/test_workflow_state_machine.py
new file mode 100644
index 0000000000000000000000000000000000000000..bc2b60c3766990e82421fdc4a7add419fcdf71cb
--- /dev/null
+++ b/tests/unit/test_workflow_state_machine.py
@@ -0,0 +1,16 @@
+import unittest
+
+from engine.core.workflow_state_machine import transition
+
+
+class WorkflowStateTests(unittest.TestCase):
+    def test_valid_transition(self):
+        transition("Draft", "Validated")
+
+    def test_invalid_transition(self):
+        with self.assertRaises(ValueError):
+            transition("Draft", "Closed")
+
+
+if __name__ == "__main__":
+    unittest.main()
