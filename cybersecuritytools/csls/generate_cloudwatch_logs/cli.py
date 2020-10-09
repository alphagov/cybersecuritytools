#!/usr/bin/env python3
"""
Command line interface for the log testing scripts.

When new formats are added to put_cloudwatch_logs, add them to the long_options list,
and add a short single letter version to the format argument's `choices` list.

Note that the way it works right now, two different formats MUST NOT start with
the same first letter. If that happens, the main() function must be modified.
"""

import os
import sys
from datetime import datetime
from pprint import pprint
from time import sleep

import click

from cybersecuritytools.splunk.credentials import credentials
from cybersecuritytools.splunk.search import Search

from .put_cloudwatch_logs import send_logs_to_cloudwatch, setup_cloudwatch_log_groups
from .query_splunk import load_test_found, payload_found, search_query


@click.group()
def generate_cloudwatch_logs() -> None:
    pass


@generate_cloudwatch_logs.command()
@click.option("-d", "--destination-arn", required=True, type=str)
@click.option("-r", "--role-arn", required=True, type=str)
def create_log_groups(destination_arn: str, role_arn: str) -> None:
    setup_cloudwatch_log_groups(dest_arn=destination_arn, role_arn=role_arn)


@generate_cloudwatch_logs.command()
def send_logs() -> None:
    """Send test data to Cloudwatch log-groups based on selected format."""
    send_logs_to_cloudwatch()


@generate_cloudwatch_logs.command()
@click.option("-t", "--timeout", type=int, default=600)
@click.option("--ssm", required=True, help="SSM root path")
def smoke_test(ssm_root: str, timeout: int) -> None:
    """Run an end to end test on the pipeline"""
    cloudwatch_results = send_logs_to_cloudwatch()
    print("Sent logs to CloudWatch")
    start_timestamp = int(datetime.now().timestamp())
    print("Polling splunk to find our logs...")

    splunk_credentials = credentials(ssm_root, "search")
    splunk = Search(splunk_credentials)

    while True:
        duration = int(datetime.now().timestamp()) - start_timestamp
        splunk_results = splunk.search(search_query(test_type="smoke_test"))

        if payload_found(cloudwatch_results, splunk_results):
            print(f"\n✔️ Pipeline smoketest succeeded in {duration} seconds")
            sys.exit(0)

        if duration > timeout:
            print(
                f"\n❌TIMEOUT searching for payload in splunk after {duration} seconds",
                file=sys.stderr,
            )
            print("CloudWatch results: ")
            pprint(cloudwatch_results)
            print("\n\n\n\n")
            print("Splunk results: ")
            pprint(splunk_results)
            print(
                f"\n❌ TIMEOUT searching for payload in splunk after {duration} seconds",
                file=sys.stderr,
            )
            sys.exit(1)

        sleep(1)
        print(".", end="", flush=True)


@generate_cloudwatch_logs.command()
@click.option("-t", "--timeout", type=int, default=600)
@click.option("--ssm", required=True, help="SSM root path")
def load_test(ssm: str, timeout: int) -> None:
    """Check Splunk for artillery payloads on the pipeline"""
    start_timestamp = float(datetime.now().timestamp())

    splunk_credentials = credentials(ssm, "search")
    splunk = Search(splunk_credentials)

    while True:

        duration = float(datetime.now().timestamp()) - start_timestamp
        artillery_config = 80000
        requests_completed = int(os.environ.get("requests_completed", artillery_config))

        splunk_results = splunk.search(search_query(test_type="smoke_test"))

        if load_test_found(splunk_results, artillery_config, requests_completed):
            print(f"\n✔️ Pipeline load test succeeded in {duration} seconds")
            sys.exit(0)

        if requests_completed < int(artillery_config * 0.9):
            print(
                f"\n❌INSUFFICIENT DATA Artillery has only sent {requests_completed}"
                f"requests from a config of {artillery_config}"
            )
            sys.exit(0)

        if duration > timeout:
            print(
                f"\n❌TIMEOUT searching for payload in splunk after {duration} seconds",
                file=sys.stderr,
            )
            print("Splunk results: ")
            pprint(splunk_results)
            print(
                f"\n❌TIMEOUT searching for payload in splunk after {duration} seconds",
                file=sys.stderr,
            )
            sys.exit(1)

        sleep(1)
        print(".", end="", flush=True)
