import pathlib
from typing import Any, MutableMapping

import pytest

from .accountstoml import indexes_from_accounts, load_accounts_loggroup_index_toml


@pytest.fixture
def accounts_toml_path() -> str:
    """Path to the test data TOML"""
    current_path = pathlib.Path(__file__).parent.absolute()
    path = f"{current_path}/accounts_loggroup_index_test.toml"
    return path


def test_load_accounts_log_group_index_toml(accounts_toml_path: str) -> None:
    """Check the loaded TOML matches the format we expect. This is a sense
    check for further tests.
    """
    loaded = load_accounts_loggroup_index_toml(accounts_toml_path)
    assert loaded

    account1 = "1111111111"
    assert account1 in loaded

    log_group1 = "/log_group1"
    assert log_group1 in loaded[account1]

    index1 = "index1"
    assert loaded[account1][log_group1]["index"] == index1

    account2 = "2222222222"
    assert account2 in loaded

    log_group2 = "/log_group2"
    assert log_group1 in loaded[account1]

    index2 = "index2"
    assert loaded[account2][log_group2]["index"] == index2


@pytest.fixture
def accounts() -> MutableMapping[str, Any]:
    """The accounts TOML object as a python Dict"""
    current_path = pathlib.Path(__file__).parent.absolute()
    path = f"{current_path}/accounts_loggroup_index_test.toml"
    loaded = load_accounts_loggroup_index_toml(path)
    return loaded


def test_indexes_from_accounts(accounts: MutableMapping[str, Any]) -> None:
    """The set returned from this function should include all indexes
    listed in the accounts TOML"""
    indexes = indexes_from_accounts(accounts)
    expected = set(["index1", "index2"])
    assert indexes == expected
