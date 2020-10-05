import os
from typing import Any, Dict, List
from uuid import uuid4

from .put_cloudwatch_logs import CloudWatchLogResult, log_formats, log_group_name


def log_group_name_to_splunk_format(group_name: str) -> str:
    """Transform the standard Cloudwatch log group name to the format used
    by Splunk.

    /aws/foo/bar -> aws:foo:bar
    """
    return group_name.replace("/", ":").strip(":")


# TODO: Search for the exact cloudwatch log payload instead of this wide search.
def search_query(test_type: str, index: str = "test_data") -> str:
    """Generate search query to find the test data."""
    sourcetypes = ", ".join(
        [log_group_name_to_splunk_format(log_group_name(f)) for f in log_formats()]
    )
    random_uuid = os.environ.get("random_uuid", str(uuid4()))
    if test_type == "smoke_test":
        return (
            f'search index IN ("{index}") '
            f"sourcetype IN (aws:test:general, {sourcetypes}) "
            f"|eval indextime = _indextime "
            f"|eval latency=_indextime - _time"
        )
    else:
        return (
            f'search index IN ("{index}") '
            f'source="HOSTWHO:LOGWHAT:{random_uuid}"'
            f"| stats count(source)"
        )


def payload_found(
    cloudwatch_results: Dict[str, CloudWatchLogResult],
    splunk_results: List[Dict[Any, Any]],
) -> bool:
    sr = set([r["_raw"] for r in splunk_results])
    cwr = set([c.log_line for c in cloudwatch_results.values()])
    return sr >= cwr


def load_test_found(
    splunk_results: List[Dict[Any, Any]], requests_completed: int, artillery_config: int
) -> bool:
    values = [r["count(source)"] for r in splunk_results]
    for result in values:
        threshold = requests_completed * 0.9
        if int(result) >= threshold:
            if requests_completed < artillery_config:
                print(
                    f"Not all {artillery_config} requests were sent by artillery, "
                    f"only {requests_completed} sent."
                )
            return True
    return False


# TODO: Check that logs are appearing in the correct log groups.
# TODO: Compute delta between Cloudwatch ingestion and Splunk index time.
