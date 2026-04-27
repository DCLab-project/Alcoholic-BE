from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from app.config.settings import Settings, get_settings
from app.db import build_engine_options


class DatabaseConfigTest(unittest.TestCase):
    def tearDown(self) -> None:
        get_settings.cache_clear()

    def test_default_database_uses_sqlite(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            get_settings.cache_clear()
            settings = Settings.from_env()

        self.assertEqual("sqlite:///./alcoholic.db", settings.database_url)
        self.assertEqual(1800, settings.database_pool_recycle_seconds)

    def test_mysql_url_is_normalized_for_pymysql_and_utf8mb4(self) -> None:
        with patch.dict(
            os.environ,
            {"DATABASE_URL": "mysql://user:pass@127.0.0.1:3306/alcoholic"},
            clear=True,
        ):
            settings = Settings.from_env()

        self.assertEqual(
            "mysql+pymysql://user:pass@127.0.0.1:3306/alcoholic?charset=utf8mb4",
            settings.database_url,
        )

    def test_mysql_url_keeps_existing_query_parameters(self) -> None:
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": (
                    "mysql+pymysql://user:pass@127.0.0.1:3306/alcoholic"
                    "?ssl_disabled=true"
                )
            },
            clear=True,
        ):
            settings = Settings.from_env()

        self.assertEqual(
            "mysql+pymysql://user:pass@127.0.0.1:3306/alcoholic"
            "?ssl_disabled=true&charset=utf8mb4",
            settings.database_url,
        )

    def test_engine_options_are_sqlite_and_mysql_aware(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            sqlite_settings = Settings.from_env()
        mysql_settings = sqlite_settings.model_copy(
            update={
                "database_url": "mysql+pymysql://user:pass@127.0.0.1:3306/alcoholic",
                "database_pool_recycle_seconds": 900,
            }
        )

        sqlite_options = build_engine_options(sqlite_settings)
        mysql_options = build_engine_options(mysql_settings)

        self.assertEqual({"check_same_thread": False}, sqlite_options["connect_args"])
        self.assertNotIn("pool_recycle", sqlite_options)
        self.assertEqual({}, mysql_options["connect_args"])
        self.assertEqual(900, mysql_options["pool_recycle"])


if __name__ == "__main__":
    unittest.main()
