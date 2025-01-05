import sys
from unittest.mock import patch

import pytest

from mcp_server_duckdb.config import Config


def test_config_required_db_path():
    with patch.object(sys, "argv", ["prog"]):
        with pytest.raises(SystemExit):
            Config.from_arguments()


def test_config_from_arguments_readonly_false(tmp_path):
    test_db_file = tmp_path / "test.duckdb"
    test_args = [
        "--db-path",
        str(test_db_file),
    ]
    with patch.object(sys, "argv", ["prog"] + test_args):
        config = Config.from_arguments()
        assert config.db_path == test_db_file
        assert config.readonly is False


def test_config_from_arguments_readonly_true(tmp_path):
    test_db_file = tmp_path / "test.duckdb"
    test_args = [
        "--db-path",
        str(test_db_file),
        "--readonly",
    ]
    with patch.object(sys, "argv", ["prog"] + test_args):
        config = Config.from_arguments()
        assert config.readonly is True
