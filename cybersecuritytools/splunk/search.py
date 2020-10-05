from time import sleep
from typing import Any, Dict, List

from splunklib import client  # type: ignore
from splunklib.results import ResultsReader  # type: ignore

from .credentials import SplunkCredentials


class Search:
    def __init__(self, credentials: SplunkCredentials):
        self.credentials = credentials
        self.client = self.client()

    def client(self) -> Any:
        """Create a client to connect to Splunk."""
        return client.connect(
            host=self.credentials.hostname,
            port=self.credentials.port,
            username=self.credentials.username,
            password=self.credentials.password,
        )

    def search(
        self, search_query: str, search_kwargs: Dict[str, str] = {}
    ) -> List[Dict[Any, Any]]:
        """Make a splunk search on `service`."""

        if not search_kwargs:
            search_kwargs = self.search_defaults()

        job = self.client.jobs.create(search_query, **search_kwargs)

        query_results: List[Dict[Any, Any]] = []
        while not job.is_done():
            sleep(0.1)
        query_results = [r for r in ResultsReader(job.results())]
        job.cancel()

        return query_results

    def search_defaults(self, minutes: int = 15) -> Dict[str, str]:
        """Query Splunk for the latest CloudWatch test data."""
        return {
            "exec_mode": "normal",
            "earliest_time": f"-{minutes}m",
            "latest_time": "now",
        }
