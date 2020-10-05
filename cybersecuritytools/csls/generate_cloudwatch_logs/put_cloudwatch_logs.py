"""Module for generating test data of various types, send data to Cloudwatch."""
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any, Dict, List
from uuid import uuid4

import boto3
import mypy_boto3_logs as logs
from mypy_boto3_logs.type_defs import PutLogEventsResponseTypeDef


class LogEventResponseReal(PutLogEventsResponseTypeDef):
    ResponseMetadata: Dict[Any, Any]


@lru_cache(maxsize=None)
def logs_client() -> logs.CloudWatchLogsClient:
    return boto3.client("logs")


@dataclass
class LogLines:
    logs: Dict[str, str]
    payload: str
    datetime: datetime


def log_lines(payload: str = "") -> LogLines:
    """The log lines to send to CloudWatch logs. This generates all the
    supported log formats with an embedded UUID which can be used to
    identify the logs at a later date.

    Parameters
    ----------
    payload: A custom payload to add into the generated log lines

    """
    payload = payload or str(uuid4())
    now = datetime.now()

    logs = {
        "raw": f"Hello {payload} {now}",
        "json": json.dumps({"Hello": payload, "time": str(now)}),
        "csv": (f"An Example [{payload}] logged in,192.168.1.1," f'"{now}",Unknown'),
        "syslog": (
            f"{now.strftime('%b %d %H:%M:%S')} ip-192-168-1-1 bash[1644]: "
            f"#01 [{payload}] java.lang.Thread.run(Thread.java:748) [?:1.8.0_172]"
        ),
    }
    return LogLines(logs, payload, now)


@lru_cache()
def log_formats() -> List[str]:
    """Logging output formats"""
    return [*log_lines().logs]


def create_cloudwatch_log_group(group_name: str, dest_arn: str, role_arn: str) -> None:
    """Create a cloudwatch group and subscribe it to the Kinesis stream.
    Ignore any log groups that already exist.

    See https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/Subscriptions.html

    Parameters
    ----------
    group_name: The Cloudwatch log group name to create.
    dest_arn: The arn of the Kinesis stream to subscribe the newly created
              log group to.
    role_arn: The role arn to use when shipping logs to Kinesis

    """
    cwl = logs_client()
    try:
        cwl.create_log_group(logGroupName=group_name)
    except cwl.exceptions.ResourceAlreadyExistsException:
        pass

    cwl.put_subscription_filter(
        logGroupName=group_name,
        filterName=f"ship-logs-for-{group_name}",
        filterPattern="",
        destinationArn=dest_arn,
        roleArn=role_arn,
    )


def log_group_name(postfix: str) -> str:
    return f"/gds/test/{postfix}"


def setup_cloudwatch_log_groups(dest_arn: str, role_arn: str) -> None:
    """Create all the required cloudwatch log groups"""
    for fmt in ["general"] + log_formats():
        create_cloudwatch_log_group(log_group_name(fmt), dest_arn, role_arn)


@dataclass
class LogStream:
    name: str
    timestamp_ms: int


def log_stream_name() -> LogStream:
    """Generate an appropriately named log group of the format
    '{timestamp_ms}-{invocation}-test-data'
    """
    timestamp_seconds = datetime.now().replace(tzinfo=timezone.utc).timestamp()
    timestamp_ms = int(timestamp_seconds * 1000)
    name = f"{timestamp_ms}-test-data"
    return LogStream(name, timestamp_ms)


def create_log_stream(group_name: str) -> LogStream:
    """Create a log stream with the a name genreated by log_stream_name()"""
    ls = log_stream_name()
    logs_client().create_log_stream(logGroupName=group_name, logStreamName=ls.name)
    return ls


@dataclass
class CloudWatchLogResult:
    timestamp_ms: int
    log_group_name: str
    log_line: str
    log_stream_name: str
    payload: str


def send_logs_to_cloudwatch() -> Dict[str, CloudWatchLogResult]:
    """Send logs to Cloudwatch, creating a new logstream for those events"""
    lines = log_lines()

    results = {}

    for file_format, line in lines.logs.items():

        group_name = log_group_name(file_format)
        stream = create_log_stream(group_name)

        logs_client().put_log_events(
            logGroupName=group_name,
            logStreamName=stream.name,
            logEvents=[{"timestamp": stream.timestamp_ms, "message": line}],
        )

        results[file_format] = CloudWatchLogResult(
            timestamp_ms=stream.timestamp_ms,
            log_group_name=group_name,
            log_line=line,
            log_stream_name=stream.name,
            payload=lines.payload,
        )

    return results
