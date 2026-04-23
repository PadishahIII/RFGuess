# UI State And Lifecycle Refactor Design

## Goal

Refactor the RFGuess desktop application to remove brittle global configuration, make database access lazily configurable, improve shutdown behavior for keyboard and window close paths, and clean up UI task/state flow without redesigning the whole application.

## Scope

This design covers:

- `Parser/Config.py` database configuration defaults
- `Scripts/databaseInit.py` engine/session lifecycle
- `ui/slots.py` task state, worker ownership, and shutdown handling
- targeted correctness fixes in generator classes
- test-suite cleanup where placeholder failures currently drown out real regressions

This design does not cover:

- a full per-tab controller rewrite
- replacing PyQt with another toolkit
- a full job scheduling framework
- deep ML/parser algorithm changes unrelated to lifecycle or correctness defects already identified

## Problems Being Solved

### 1. Hardcoded database configuration

`Parser/Config.py` currently hardcodes a specific username, password, and local host-only URL. This breaks the documented Docker workflow, breaks DB-backed tests by default, and makes runtime configuration depend on manual UI override.

### 2. Import-time engine creation

`Scripts/databaseInit.py` creates a SQLAlchemy engine when the module is imported. Because UI and tests import that module early, they inherit a stale or invalid engine before the user can configure anything.

### 3. Unowned background threads

`ui/slots.py` creates consumer threads and progress threads with no centralized ownership boundary and no reliable shutdown path. Some loops are infinite and block process exit.

### 4. Confused state flow

Task status is currently spread across:

- `Slots.currentTask`
- several ad hoc exit flags
- nested closures
- widget state
- side effects in decorators

This makes behavior hard to reason about, especially around cancellation, shutdown, and failure paths.

### 5. Correctness bugs in utility/generator code

- `DatasetGenerator` has an off-by-one limit check
- `DictionaryGenerator` uses a mutable default list

### 6. Tests do not provide usable signal

Many tests intentionally call `self.fail()`, which means the suite reports large numbers of known fake failures and hides real regressions.

## Proposed Architecture

### A. Configuration Layer

Introduce a small configuration access pattern around database settings.

Requirements:

- `Parser/Config.py` must stop hardcoding a developer-specific database URL
- the default database URL should come from an environment variable when available
- the module should expose a stable runtime setter/getter so the UI can update the active DB URL without directly mutating globals in multiple places
- defaults should remain simple enough for non-UI scripts

Recommended shape:

- keep `Parser/Config.py` as the canonical place for DB URL configuration
- replace the literal URL with:
  - an environment-backed default such as `RFGUESS_DATABASE_URL`
  - a safe fallback that is explicit and local
- add a small helper API:
  - `get_database_url()`
  - `set_database_url(url: str)`

This keeps compatibility with existing import sites while removing the magic literal.

### B. Lazy Database Binding

Refactor `Scripts/databaseInit.py` so engine/session objects are initialized lazily rather than at import time.

Requirements:

- importing the module must not try to connect to the database
- the active engine must always reflect the current configured DB URL
- rebinding the engine from the UI should be explicit and idempotent
- tests must be able to set a DB URL before first use

Recommended shape:

- replace the eager module-level `create_engine(...)` with a tiny manager:
  - `get_engine()`
  - `get_session()`
  - `update_engine(url: str | None = None)`
  - internal cache fields for engine/session factory
- `update_engine()` should rebuild the cached engine/session factory
- DB query helpers should obtain sessions through the manager rather than assuming import-time globals are already correct

This is intentionally a small refactor, not a full repository pattern rewrite.

### C. UI Lifecycle Ownership

Refactor `ui/slots.py` so `Slots` remains the signal wiring façade, but lifecycle and task execution move into dedicated helpers.

Requirements:

- all long-lived background activity must have an owner
- shutdown must be centralized
- new tasks must be blocked once shutdown begins
- current task transitions must be explicit rather than inferred from scattered side effects

Recommended helper boundaries:

#### 1. `UiTaskState`

Responsible for:

- current task name
- task phase/status
- whether the app is idle, running, stopping, or closed

It becomes the single source of truth for task flow instead of `Slots.currentTask` plus decorator cleanup.

#### 2. `WorkerRegistry`

Responsible for:

- tracking created `threading.Thread` and `QThread` workers
- starting named workers
- signalling stop
- bounded join/wait on shutdown

This avoids ad hoc thread creation that disappears into local variables.

#### 3. `StoppableConsumer`

Replace the current infinite-loop `Consumer` thread with a stoppable variant.

Requirements:

- waits with timeout or sentinel-based queue consumption
- supports explicit stop request
- exits promptly during shutdown

### D. Unified Shutdown Path

Define one shutdown routine used by:

- window close
- `QApplication.aboutToQuit`
- keyboard interrupt / `SIGINT`

Expected behavior:

1. mark app state as `stopping`
2. prevent new tasks from starting
3. set stop signals for consumers and progress workers
4. ask worker registry to wait bounded time
5. allow Qt shutdown to continue cleanly

Result:

- `Ctrl+C` should close the UI without hanging
- closing the window should not leave background threads alive
- shutdown should avoid noisy tracebacks where possible

## State Flow Design

### Current issues

- `currentTask` is global-ish and reset by decorator side effects
- several progress loops use separate exit flags with inconsistent naming/usage
- at least one assess-progress path checks the wrong exit flag
- state is sometimes carried in widget text or closure-local variables rather than in a model

### Proposed state model

Define explicit task lifecycle states:

- `idle`
- `running`
- `stopping`
- `completed`
- `failed`

Rules:

- only one foreground task may be `running` at a time
- transitions happen through task-state methods, not raw string assignment
- shutdown forces `running -> stopping`
- completion/failure transitions are explicit and logged once

Expected simplifications:

- no decorator-based “maybe clear current task”
- less duplication across pattern generation, PII loading, analysis, training, and assessment flows
- clearer checks for “can a new task start now?”

## Additional UI Problems To Address During Refactor

The implementation should also address these UI-related issues discovered during investigation:

1. Consumer threads are started in `Slots.__init__` with no teardown path.
2. Progress threads are created ad hoc and are not centrally registered.
3. `pyqtSignal` is assigned as an instance attribute in `Slots`, which is not a proper Qt object pattern and should be removed or relocated.
4. Task completion currently relies on decorator cleanup rather than explicit workflow ownership.
5. UI defaults and backend configuration can diverge, causing confusing startup behavior.
6. Mixed `threading.Thread` and `QThread` usage lacks a consistent ownership model.
7. Long-running operations use nested local functions, which makes lifecycle wiring and cleanup harder to reason about and test.

## Correctness Fixes

### Dataset generator

Fix the limit check so exactly `limit` items are processed, not `limit + 1`.

### Dictionary generator

Replace the mutable default `seedList=list()` with a non-shared default such as `None`, then normalize inside the constructor.

## Test Strategy

The test suite currently contains many placeholder failures. The goal is to improve signal, not pretend these are real tests.

Plan:

- convert obvious placeholder `self.fail()` tests into explicit skipped tests with a short reason
- keep any real behavioral tests intact
- add focused tests for new helper behavior where practical:
  - config getter/setter behavior
  - lazy engine initialization/rebinding
  - stoppable consumer shutdown behavior
  - task-state transition guards
  - dataset limit boundary
  - dictionary generator default isolation

This should reduce noise enough that true regressions become visible.

## Verification Plan

Implementation will not be considered complete until these checks run successfully:

- focused unit tests for newly introduced helpers
- targeted test commands for corrected generator behavior
- regression checks for config/DB binding behavior
- `uv run python main.py` with a controlled shutdown path
- manual verification that `Ctrl+C` exits the app cleanly while background workers are idle or active

## Risks And Mitigations

### Risk: refactor expands too far

Mitigation:

- keep the helper extraction narrow
- preserve the current widget wiring layout
- avoid redesigning all tab logic at once

### Risk: Qt/thread lifecycle regressions

Mitigation:

- introduce a single worker registry and shutdown path
- prefer explicit ownership over more concurrency
- verify with live app launch plus forced shutdown

### Risk: DB layer churn breaks unrelated code

Mitigation:

- keep the existing `update_engine()` concept
- add compatibility wrappers around lazy engine/session access
- update imports minimally

## Recommendation

Proceed with the targeted refactor:

- fix config and DB binding first
- extract lifecycle/state helpers next
- patch shutdown and worker ownership
- then address the small correctness bugs and test cleanup

This is the smallest design that fixes the root causes instead of only treating symptoms.
