# UI State And Lifecycle Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove brittle DB configuration and import-time engine binding, make the UI shut down cleanly on window close and `Ctrl+C`, clarify task/state flow, and fix the targeted correctness/test-signal issues identified in review.

**Architecture:** Keep the existing Qt UI and `Slots` wiring, but extract a narrow set of lifecycle/config helpers so state and shutdown behavior have explicit ownership. Refactor the DB layer to lazy engine/session creation, introduce shutdown-aware worker tracking in the UI, and make the smallest generator/test fixes needed to restore correctness and improve verification signal.

**Tech Stack:** Python 3.11, PyQt5, SQLAlchemy, unittest, uv

---

### Task 1: Stabilize Database Configuration

**Files:**
- Modify: `Parser/Config.py`
- Test: `Tests/test_config_runtime.py`

- [ ] **Step 1: Write the failing test**

```python
import os
import unittest
from importlib import reload

import Parser.Config as Config


class TestConfigRuntime(unittest.TestCase):
    def test_database_url_defaults_to_non_personal_value(self):
        old = os.environ.pop("RFGUESS_DATABASE_URL", None)
        try:
            reload(Config)
            self.assertNotIn("914075", Config.get_database_url())
        finally:
            if old is not None:
                os.environ["RFGUESS_DATABASE_URL"] = old

    def test_runtime_setter_overrides_active_database_url(self):
        original = Config.get_database_url()
        try:
            Config.set_database_url("mysql://root:root@127.0.0.1:3307/rfguess")
            self.assertEqual(
                Config.get_database_url(),
                "mysql://root:root@127.0.0.1:3307/rfguess",
            )
        finally:
            Config.set_database_url(original)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run python -m unittest Tests.test_config_runtime -v`
Expected: FAIL because `get_database_url` and `set_database_url` do not exist and the hardcoded password is still present.

- [ ] **Step 3: Write minimal implementation**

```python
import os

_DEFAULT_DATABASE_URL = os.environ.get(
    "RFGUESS_DATABASE_URL",
    "mysql://root:root@127.0.0.1:3307/rfguess",
)

DatabaseUrl = _DEFAULT_DATABASE_URL


def get_database_url() -> str:
    return DatabaseUrl


def set_database_url(url: str) -> None:
    global DatabaseUrl
    DatabaseUrl = url
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run python -m unittest Tests.test_config_runtime -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add Parser/Config.py Tests/test_config_runtime.py
git commit -m "refactor: stabilize runtime database config"
```

### Task 2: Make Database Engine Binding Lazy

**Files:**
- Modify: `Scripts/databaseInit.py`
- Test: `Tests/test_database_runtime.py`

- [ ] **Step 1: Write the failing test**

```python
import unittest
from unittest.mock import patch

from Parser import Config
from Scripts import databaseInit


class TestDatabaseRuntime(unittest.TestCase):
    def test_get_engine_is_lazy_and_uses_current_config(self):
        with patch("Scripts.databaseInit.sqlalchemy.create_engine") as create_engine:
            databaseInit.reset_engine_cache()
            Config.set_database_url("mysql://root:root@127.0.0.1:3307/rfguess")
            databaseInit.get_engine()
            create_engine.assert_called_once_with(Config.get_database_url())

    def test_update_engine_rebinds_cached_factory(self):
        with patch("Scripts.databaseInit.sqlalchemy.create_engine") as create_engine:
            databaseInit.reset_engine_cache()
            databaseInit.update_engine("mysql://root:root@127.0.0.1:3307/rfguess")
            databaseInit.get_engine()
            create_engine.assert_called_with("mysql://root:root@127.0.0.1:3307/rfguess")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run python -m unittest Tests.test_database_runtime -v`
Expected: FAIL because `reset_engine_cache` and `get_engine` do not exist, and import-time engine creation bypasses the patch expectations.

- [ ] **Step 3: Write minimal implementation**

```python
engine = None
sessionFactory = None
Session = None


def reset_engine_cache():
    global engine, sessionFactory, Session
    engine = None
    sessionFactory = None
    Session = None


def get_engine():
    global engine, sessionFactory, Session
    if engine is None:
        engine = sqlalchemy.create_engine(Config.get_database_url())
        sessionFactory = sessionmaker(bind=engine)
        Session = scoped_session(sessionFactory)
    return engine


def get_session():
    get_engine()
    return Session()


def update_engine(url: str | None = None):
    if url is not None:
        Config.set_database_url(url)
    reset_engine_cache()
    get_engine()
```

- [ ] **Step 4: Update database call sites to use lazy access**

```python
with get_session() as session:
    ...
```

Apply this pattern anywhere `Session()` or the eager globals were assumed to already exist.

- [ ] **Step 5: Run test to verify it passes**

Run: `uv run python -m unittest Tests.test_database_runtime -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add Scripts/databaseInit.py Tests/test_database_runtime.py
git commit -m "refactor: make database engine binding lazy"
```

### Task 3: Introduce Explicit UI Task State

**Files:**
- Modify: `ui/slots.py`
- Test: `Tests/test_ui_task_state.py`

- [ ] **Step 1: Write the failing test**

```python
import unittest

from ui.slots import UiTaskState


class TestUiTaskState(unittest.TestCase):
    def test_cannot_start_new_task_when_running(self):
        state = UiTaskState()
        self.assertTrue(state.start("Load PII Data"))
        self.assertFalse(state.start("Train Model"))

    def test_shutdown_prevents_new_tasks(self):
        state = UiTaskState()
        state.begin_shutdown()
        self.assertFalse(state.start("Generate Pattern"))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run python -m unittest Tests.test_ui_task_state -v`
Expected: FAIL because `UiTaskState` does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
class UiTaskState:
    def __init__(self):
        self.status = "idle"
        self.task_name = ""
        self.lock = threading.Lock()

    def start(self, task_name: str) -> bool:
        with self.lock:
            if self.status in {"running", "stopping", "closed"}:
                return False
            self.status = "running"
            self.task_name = task_name
            return True

    def complete(self):
        with self.lock:
            self.status = "completed"
            self.task_name = ""

    def fail(self):
        with self.lock:
            self.status = "failed"
            self.task_name = ""

    def reset_idle(self):
        with self.lock:
            if self.status != "closed":
                self.status = "idle"

    def begin_shutdown(self):
        with self.lock:
            if self.status != "closed":
                self.status = "stopping"

    def close(self):
        with self.lock:
            self.status = "closed"
            self.task_name = ""
```

- [ ] **Step 4: Replace `TaskRecorder`/decorator-driven task cleanup with the new state object**

```python
self.task_state = UiTaskState()
```

Update task start paths to call `start(...)` and completion/failure paths to call explicit state transitions instead of relying on decorator side effects.

- [ ] **Step 5: Run test to verify it passes**

Run: `uv run python -m unittest Tests.test_ui_task_state -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add ui/slots.py Tests/test_ui_task_state.py
git commit -m "refactor: add explicit ui task state"
```

### Task 4: Add Worker Ownership And Stoppable Consumers

**Files:**
- Modify: `ui/slots.py`
- Test: `Tests/test_ui_workers.py`

- [ ] **Step 1: Write the failing test**

```python
import queue
import unittest

from ui.slots import StoppableConsumer


class TestUiWorkers(unittest.TestCase):
    def test_consumer_stops_after_stop_request(self):
        handled = []
        q = queue.Queue()
        consumer = StoppableConsumer(q, handled.append)
        consumer.start()
        q.put("hello")
        consumer.stop()
        consumer.join(timeout=1)
        self.assertFalse(consumer.is_alive())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run python -m unittest Tests.test_ui_workers -v`
Expected: FAIL because `StoppableConsumer` does not exist or the current `Consumer` never exits.

- [ ] **Step 3: Write minimal implementation**

```python
class StoppableConsumer(threading.Thread):
    def __init__(self, queue: Queue, handler: typing.Callable):
        super().__init__(daemon=True)
        self.queue = queue
        self.handler = handler
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()
        self.queue.put(None)

    def run(self):
        while not self.stop_event.is_set():
            item = self.queue.get(timeout=None)
            if item is None:
                continue
            self.handler(item)
```

- [ ] **Step 4: Introduce a simple worker registry**

```python
class WorkerRegistry:
    def __init__(self):
        self._threads = []

    def register_thread(self, thread):
        self._threads.append(thread)
        return thread

    def stop_all(self):
        for thread in self._threads:
            stop = getattr(thread, "stop", None)
            if callable(stop):
                stop()

    def join_all(self, timeout: float = 1.0):
        for thread in self._threads:
            if hasattr(thread, "join"):
                thread.join(timeout=timeout)
```

Use this registry for consumer threads and progress threads created by `Slots`.

- [ ] **Step 5: Run test to verify it passes**

Run: `uv run python -m unittest Tests.test_ui_workers -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add ui/slots.py Tests/test_ui_workers.py
git commit -m "refactor: add stoppable ui workers"
```

### Task 5: Unify UI Shutdown For Window Close And Ctrl+C

**Files:**
- Modify: `ui/slots.py`
- Modify: `main.py`
- Test: `Tests/test_ui_shutdown.py`

- [ ] **Step 1: Write the failing test**

```python
import unittest
from unittest.mock import MagicMock

from ui.slots import Slots


class TestUiShutdown(unittest.TestCase):
    def test_shutdown_marks_state_and_stops_workers(self):
        slots = object.__new__(Slots)
        slots.task_state = MagicMock()
        slots.worker_registry = MagicMock()
        Slots.shutdown(slots)
        slots.task_state.begin_shutdown.assert_called_once()
        slots.worker_registry.stop_all.assert_called_once()
        slots.worker_registry.join_all.assert_called_once()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run python -m unittest Tests.test_ui_shutdown -v`
Expected: FAIL because `Slots.shutdown` does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
def shutdown(self):
    self.task_state.begin_shutdown()
    self.worker_registry.stop_all()
    self.worker_registry.join_all()
    self.task_state.close()
```

- [ ] **Step 4: Wire shutdown into Qt and SIGINT**

```python
app.aboutToQuit.connect(slots.shutdown)
signal.signal(signal.SIGINT, lambda *_: app.quit())
```

Also make the main window close path call the same shutdown routine once, without duplicate teardown.

- [ ] **Step 5: Fix known state-flow bugs while wiring shutdown**

Apply these exact cleanups in `ui/slots.py`:

- remove `self.progressSignal = pyqtSignal(int)` from `Slots`
- ensure assess progress loop checks `self.assessProgressExitFlag`, not `self.trainModelProgressExitFlag`
- block new foreground tasks when task state is `stopping`
- move long-lived worker startup out of implicit ad hoc code paths into tracked creation points

- [ ] **Step 6: Run test to verify it passes**

Run: `uv run python -m unittest Tests.test_ui_shutdown -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add main.py ui/slots.py Tests/test_ui_shutdown.py
git commit -m "refactor: unify ui shutdown behavior"
```

### Task 6: Fix Generator Correctness Defects

**Files:**
- Modify: `Generators/DatasetGenerator.py`
- Modify: `Generators/DictionaryGenerator.py`
- Test: `Tests/test_generator_regressions.py`

- [ ] **Step 1: Write the failing test**

```python
import tempfile
import unittest
from pathlib import Path

from Generators.DatasetGenerator import DatasetGenerator
from Generators.DictionaryGenerator import DictionaryGenerator


class TestGeneratorRegressions(unittest.TestCase):
    def test_dictionary_generator_does_not_share_default_seed_list(self):
        a = DictionaryGenerator()
        b = DictionaryGenerator()
        a._seeds.append("x")
        self.assertEqual([], b._seeds)

    def test_dataset_generator_limit_is_exact(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "pw.txt"
            file.write_text("a\nb\nc\n", encoding="utf-8")
            gen = DatasetGenerator(str(file), limit=2)
            seen = []
            gen.resolvePassword = seen.append
            gen.save = lambda _: None
            gen._build()
            self.assertEqual(["a", "b"], seen)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run python -m unittest Tests.test_generator_regressions -v`
Expected: FAIL because the seed list is shared and `_build()` processes one extra password.

- [ ] **Step 3: Write minimal implementation**

```python
def __init__(self, seedList=None, saveFile: str = "passwordDic.txt") -> None:
    ...
    self._seeds = list(seedList) if seedList is not None else []
```

```python
for p in pl:
    if self._i >= self.limit:
        break
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run python -m unittest Tests.test_generator_regressions -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add Generators/DatasetGenerator.py Generators/DictionaryGenerator.py Tests/test_generator_regressions.py
git commit -m "fix: correct generator boundary and default state bugs"
```

### Task 7: Reduce Test Noise From Placeholder Failures

**Files:**
- Modify: `Tests/test_DatasetGenerator.py`
- Modify: `Tests/test_DictionaryGenerator.py`
- Modify: `Tests/test_PIIDataTypes.py`
- Modify: `Tests/test_PasswordGuessGenerator.py`
- Modify: `Tests/test_PasswordParsers.py`
- Modify: `Tests/test_Trawling_Mode.py`
- Modify: `Tests/test_Utils.py`
- Modify: `Tests/test_DatabaseLayer.py`
- Modify: any other `Tests/*.py` files that contain direct placeholder `self.fail()`

- [ ] **Step 1: Write the failing test inventory**

Run:

```bash
rg -n "self\\.fail\\(\\)" Tests
```

Expected: a list of placeholder tests that are not real assertions yet.

- [ ] **Step 2: Replace placeholder failures with explicit skips**

Use this exact pattern in placeholder-only tests:

```python
import unittest


@unittest.skip("placeholder test not implemented yet")
def test_example(self):
    ...
```

If a class is entirely placeholder coverage, skip the whole class instead of each method.

- [ ] **Step 3: Keep real tests real**

Do not skip tests that already exercise behavior. Only replace known placeholders that exist solely as `self.fail()` stubs.

- [ ] **Step 4: Run the suite to verify signal improves**

Run: `uv run python -m unittest discover -q`
Expected: significantly fewer false-negative failures; remaining failures should reflect real behavior or DB setup issues.

- [ ] **Step 5: Commit**

```bash
git add Tests
git commit -m "test: skip placeholder unittest stubs"
```

### Task 8: End-to-End Verification

**Files:**
- Modify: `Readme.md` only if runtime configuration docs need correction to match implemented behavior

- [ ] **Step 1: Verify focused helper tests**

Run:

```bash
uv run python -m unittest \
  Tests.test_config_runtime \
  Tests.test_database_runtime \
  Tests.test_ui_task_state \
  Tests.test_ui_workers \
  Tests.test_ui_shutdown \
  Tests.test_generator_regressions -v
```

Expected: PASS

- [ ] **Step 2: Verify broad suite signal**

Run:

```bash
uv run python -m unittest discover -q
```

Expected: no placeholder-driven failure flood; any remaining failures must be investigated and either fixed or documented.

- [ ] **Step 3: Verify UI launch**

Run:

```bash
uv run python main.py
```

Expected: app starts without import/config errors.

- [ ] **Step 4: Verify keyboard shutdown**

Manual verification:

- launch `uv run python main.py`
- press `Ctrl+C`
- confirm the main window closes and the process exits without hanging

- [ ] **Step 5: Verify normal window close**

Manual verification:

- launch `uv run python main.py`
- close the main window directly
- confirm worker threads do not keep the process alive

- [ ] **Step 6: Commit final verification/documentation adjustments**

```bash
git add Readme.md
git commit -m "docs: align runtime behavior after ui lifecycle refactor"
```
