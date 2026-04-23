import queue
import threading
import unittest

from ui.slots import StoppableConsumer, WorkerRegistry


class JoinableWorker:
    def __init__(self):
        self.stop_calls = 0
        self.join_calls = []

    def stop(self):
        self.stop_calls += 1

    def join(self, timeout=None):
        self.join_calls.append(timeout)


class WaitableWorker:
    def __init__(self):
        self.quit_calls = 0
        self.wait_calls = []

    def quit(self):
        self.quit_calls += 1

    def wait(self, timeout_ms):
        self.wait_calls.append(timeout_ms)


class TestUiWorkers(unittest.TestCase):
    def test_consumer_stops_after_stop_request(self):
        handled = []
        consumed = threading.Event()
        q = queue.Queue()

        def handle(item):
            handled.append(item)
            consumed.set()

        consumer = StoppableConsumer(q, handle)
        consumer.start()
        q.put("hello")
        self.assertTrue(consumed.wait(timeout=1))

        consumer.stop()
        consumer.join(timeout=1)

        self.assertEqual(handled, ["hello"])
        self.assertFalse(consumer.is_alive())

    def test_registry_stops_and_waits_on_registered_workers(self):
        registry = WorkerRegistry()
        joinable = registry.register_thread(JoinableWorker())
        waitable = registry.register_thread(WaitableWorker())

        registry.stop_all()
        registry.join_all(timeout=0.25)

        self.assertEqual(joinable.stop_calls, 1)
        self.assertEqual(joinable.join_calls, [0.25])
        self.assertEqual(waitable.quit_calls, 1)
        self.assertEqual(waitable.wait_calls, [250])
