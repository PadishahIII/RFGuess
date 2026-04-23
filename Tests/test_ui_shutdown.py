import unittest
from unittest.mock import MagicMock, patch

import main
from ui.slots import Slots


class TestUiShutdown(unittest.TestCase):
    def test_shutdown_marks_state_and_stops_workers(self):
        slots = object.__new__(Slots)
        slots.task_state = MagicMock()
        slots.worker_registry = MagicMock()

        Slots.shutdown(slots, timeout=0.5)

        slots.task_state.begin_shutdown.assert_called_once_with()
        slots.worker_registry.stop_all.assert_called_once_with()
        slots.worker_registry.join_all.assert_called_once_with(timeout=0.5)
        slots.task_state.close.assert_called_once_with()

    def test_shutdown_is_idempotent(self):
        slots = object.__new__(Slots)
        slots.task_state = MagicMock()
        slots.worker_registry = MagicMock()

        Slots.shutdown(slots)
        Slots.shutdown(slots)

        slots.task_state.begin_shutdown.assert_called_once_with()
        slots.worker_registry.stop_all.assert_called_once_with()
        slots.worker_registry.join_all.assert_called_once_with(timeout=1.0)
        slots.task_state.close.assert_called_once_with()

    def test_main_routes_about_to_quit_and_sigint_through_same_shutdown_path(self):
        app = MagicMock()
        slots = MagicMock()

        with patch.object(main.signal, "signal") as register_signal:
            main.install_shutdown_handlers(app, slots)

        shutdown_callback = app.aboutToQuit.connect.call_args.args[0]
        app.quit.side_effect = shutdown_callback

        shutdown_callback()
        slots.shutdown.assert_called_once_with()
        slots.shutdown.reset_mock()

        sigint_handler = register_signal.call_args.args[1]
        sigint_handler(None, None)

        app.quit.assert_called_once_with()
        slots.shutdown.assert_called_once_with()
