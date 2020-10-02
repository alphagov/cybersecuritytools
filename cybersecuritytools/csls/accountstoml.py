from typing import Any, MutableMapping, Set

import toml


def load_accounts_loggroup_index_toml(path: str) -> MutableMapping[str, Any]:
    with open(path) as f:
        return toml.load(f)


def indexes_from_accounts(accounts: MutableMapping[str, Any]) -> Set[str]:
    """Reduce the accounts log group mapping to a set of index names."""
    indexes: Set[str] = {
        log_group.get("index")
        for account in accounts.values()
        if isinstance(account, dict)
        for log_group in account.values()
        if isinstance(log_group.get("index"), str)
    }
    return indexes
