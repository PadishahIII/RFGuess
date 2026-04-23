import unittest
from importlib import reload
from threading import Event, Thread
from time import sleep
from unittest.mock import patch, sentinel

import Parser.Config as Config
from Scripts import databaseInit


def _set_database_url(url: str) -> None:
    setter = getattr(Config, "set_database_url", None)
    if callable(setter):
        setter(url)
        return
    Config.DatabaseUrl = url


def _get_database_url() -> str:
    getter = getattr(Config, "get_database_url", None)
    if callable(getter):
        return getter()
    return Config.DatabaseUrl


class TestDatabaseRuntime(unittest.TestCase):
    def setUp(self) -> None:
        self.original_database_url = _get_database_url()
        databaseInit.reset_engine_cache()

    def tearDown(self) -> None:
        _set_database_url(self.original_database_url)
        databaseInit.reset_engine_cache()

    def test_import_does_not_create_engine(self):
        with patch("sqlalchemy.create_engine") as create_engine:
            reload(databaseInit)
        create_engine.assert_not_called()

    def test_get_engine_is_lazy_and_uses_current_config(self):
        databaseInit.reset_engine_cache()
        url = "mysql://root:root@127.0.0.1:3307/rfguess"
        _set_database_url(url)
        lazy_engine = unittest.mock.Mock()

        with patch("Scripts.databaseInit.sqlalchemy.create_engine", return_value=lazy_engine) as create_engine:
            engine = databaseInit.get_engine()
            self.assertIs(engine, lazy_engine)
            self.assertIs(databaseInit.get_engine(), lazy_engine)

        create_engine.assert_called_once_with(url)
        lazy_engine.dispose.assert_not_called()

    def test_update_engine_rebinds_cached_factory(self):
        databaseInit.reset_engine_cache()
        first_url = "mysql://root:root@127.0.0.1:3307/first"
        second_url = "mysql://root:root@127.0.0.1:3307/second"
        _set_database_url(first_url)
        first_engine = unittest.mock.Mock()
        second_engine = unittest.mock.Mock()

        with patch(
            "Scripts.databaseInit.sqlalchemy.create_engine",
            side_effect=[first_engine, second_engine],
        ) as create_engine:
            self.assertIs(databaseInit.get_engine(), first_engine)
            self.assertIs(databaseInit.update_engine(second_url), second_engine)
            self.assertIs(databaseInit.get_engine(), second_engine)

        self.assertEqual(_get_database_url(), second_url)
        self.assertEqual(create_engine.call_args_list[0].args, (first_url,))
        self.assertEqual(create_engine.call_args_list[1].args, (second_url,))
        first_engine.dispose.assert_called_once_with()
        second_engine.dispose.assert_not_called()

    def test_reset_engine_cache_removes_sessions_and_disposes_engine(self):
        session_scope = type("SessionScopeStub", (), {"remove": lambda self: None})()
        session_scope.remove = unittest.mock.Mock()
        old_engine = unittest.mock.Mock()

        databaseInit._session_scope = session_scope
        databaseInit.sessionFactory = object()
        databaseInit.engine = old_engine

        databaseInit.reset_engine_cache()

        session_scope.remove.assert_called_once_with()
        old_engine.dispose.assert_called_once_with()
        self.assertIsNone(databaseInit.engine)
        self.assertIsNone(databaseInit.sessionFactory)
        self.assertIsNone(databaseInit._session_scope)

    def test_session_wrapper_supports_with_usage(self):
        fake_session = unittest.mock.MagicMock()
        fake_session.__enter__.return_value = sentinel.entered_session
        fake_session.__exit__.return_value = False
        session_scope = unittest.mock.Mock(return_value=fake_session)
        wrapper_engine = unittest.mock.Mock()

        databaseInit._session_scope = session_scope
        databaseInit.sessionFactory = object()
        databaseInit.engine = wrapper_engine

        with databaseInit.Session() as session:
            self.assertIs(session, sentinel.entered_session)

        session_scope.assert_called_once_with()
        fake_session.__enter__.assert_called_once_with()
        fake_session.__exit__.assert_called_once()

    def test_get_engine_is_thread_safe(self):
        url = "mysql://root:root@127.0.0.1:3307/threadsafe"
        _set_database_url(url)
        created_engines = []
        results = []
        start = Event()

        def create_engine(_url):
            sleep(0.05)
            engine = unittest.mock.Mock()
            created_engines.append(engine)
            return engine

        def load_engine():
            start.wait()
            results.append(databaseInit.get_engine())

        with patch("Scripts.databaseInit.sqlalchemy.create_engine", side_effect=create_engine) as create_engine_mock:
            threads = [Thread(target=load_engine) for _ in range(2)]
            for thread in threads:
                thread.start()
            start.set()
            for thread in threads:
                thread.join()

        self.assertEqual(create_engine_mock.call_count, 1)
        self.assertEqual(len(created_engines), 1)
        self.assertEqual(results, [created_engines[0], created_engines[0]])
