import unittest

from ui.slots import UiTaskState


class TestUiTaskState(unittest.TestCase):
    def test_cannot_start_new_task_when_running(self):
        state = UiTaskState()
        self.assertTrue(state.start("Load PII Data"))
        self.assertEqual(state.status, UiTaskState.RUNNING)
        self.assertFalse(state.start("Train Model"))
        self.assertEqual(state.task_name, "Load PII Data")

    def test_complete_preserves_last_task_until_reset(self):
        state = UiTaskState()
        state.start("Generate Pattern")
        state.complete()
        self.assertEqual(state.status, UiTaskState.COMPLETED)
        self.assertEqual(state.task_name, "Generate Pattern")
        state.reset_idle()
        self.assertEqual(state.status, UiTaskState.IDLE)
        self.assertEqual(state.task_name, "")

    def test_shutdown_prevents_new_tasks(self):
        state = UiTaskState()
        state.begin_shutdown()
        self.assertEqual(state.status, UiTaskState.STOPPING)
        self.assertFalse(state.start("Generate Pattern"))
