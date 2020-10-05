import os
from copy import deepcopy

from .put_cloudwatch_logs import CloudWatchLogResult
from .query_splunk import log_group_name_to_splunk_format, payload_found, search_query


def test_log_group_name_to_splunk_format() -> None:
    assert "aws:group:name" == log_group_name_to_splunk_format("/aws/group/name")


def test_payload_found_true() -> None:
    """Test that all log lines sent to CloudWatch are found by
    Splunk. Check for a positive result"""
    base = CloudWatchLogResult(
        payload="abcde",
        timestamp_ms=12345,
        log_group_name="group_name",
        log_line="line",
        log_stream_name="stream.name",
    )
    cloudwatch_results = {}

    for payload in ["abc", "123", "foobarbaz"]:
        c = deepcopy(base)
        c.payload = payload
        c.log_line = f"---{payload}---"
        cloudwatch_results["payload"] = c

    splunk_results = [
        {"_raw": "---abc---"},
        {"_raw": "--123---"},
        {"_raw": "---foobarbaz---"},
        {"_raw": "zxcvb"},
        {"_raw": "qwffpg[]"},
    ]

    assert payload_found(cloudwatch_results, splunk_results)


def test_payload_found_false() -> None:
    """
    Function should return false if not all loglines are contained in the Splunk query.
    """
    base_result = CloudWatchLogResult(
        payload="abcde",
        timestamp_ms=12345,
        log_group_name="group_name",
        log_line="line",
        log_stream_name="stream.name",
    )
    cloudwatch_results = {}

    for payload in ["ZZZZZ", "YYYY"]:
        c = deepcopy(base_result)
        c.payload = payload
        c.log_line = f"---{payload}---"
        cloudwatch_results["payload"] = c

    splunk_results = [
        {"_raw": "foobarbaz"},
        {"_raw": "abcde"},
        {"_raw": "12345"},
        {"_raw": "zxcvb"},
        {"_raw": "qwffpg[]"},
    ]

    assert not payload_found(cloudwatch_results, splunk_results)


def test_search_querty() -> None:
    uuid = 80000
    random_uuid = os.environ.get("random_uuid", uuid)
    expected = (
        'search index IN ("test_data") '
        "sourcetype IN (aws:test:general, gds:test:raw, "
        "gds:test:json, gds:test:csv, gds:test:syslog) "
        "|eval indextime = _indextime "
        "|eval latency=_indextime - _time"
    )

    load_expected = (
        'search index IN ("test_data") '
        f'source="HOSTWHO:LOGWHAT:{random_uuid}"'
        "| stats count(source)"
    )
    assert search_query(test_type="smoke_test") == expected
    assert search_query(test_type="load_test") == load_expected
