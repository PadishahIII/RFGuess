import os
import unittest
from importlib import reload

import Parser.Config as Config


class TestConfigRuntime(unittest.TestCase):
    fallback_database_url = "mysql://root:root@127.0.0.1:3307/rfguess"

    def test_database_url_defaults_to_non_personal_value(self):
        old = os.environ.pop("RFGUESS_DATABASE_URL", None)
        try:
            reload(Config)
            self.assertEqual(Config.get_database_url(), self.fallback_database_url)
        finally:
            if old is not None:
                os.environ["RFGUESS_DATABASE_URL"] = old
            reload(Config)

    def test_database_url_uses_environment_value_when_present(self):
        env_database_url = "mysql://rfguess:rfguess@db.example:3306/rfguess_env"
        old = os.environ.get("RFGUESS_DATABASE_URL")
        os.environ["RFGUESS_DATABASE_URL"] = env_database_url
        try:
            reload(Config)
            self.assertEqual(Config.get_database_url(), env_database_url)
        finally:
            if old is None:
                os.environ.pop("RFGUESS_DATABASE_URL", None)
            else:
                os.environ["RFGUESS_DATABASE_URL"] = old
            reload(Config)

    def test_legacy_database_url_attribute_tracks_runtime_value(self):
        original = Config.get_database_url()
        try:
            runtime_database_url = "mysql://root:root@127.0.0.1:3308/rfguess_legacy"
            Config.set_database_url(runtime_database_url)
            self.assertEqual(Config.DatabaseUrl, runtime_database_url)
        finally:
            Config.set_database_url(original)

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
