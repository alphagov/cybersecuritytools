from dataclasses import dataclass

from cybersecuritytools.aws.ssm import env_or_param


@dataclass
class SplunkCredentials:
    hostname: str
    port: str
    password: str
    username: str


def credentials(ssm_root: str, service: str) -> SplunkCredentials:
    """Retrieves details for connecting to Splunk. It will use prefer
    local environment variables if configured, or it will fetch the
    parameters from AWS SSM.

    The environment variables are:
    SPLUNK_SEARCH_HOSTNAME
    SPLUNK_SEARCH_PORT
    SPLUNK_SEARCH_USERNAME
    SPLUNK_SEARCH_PASSWORD

    The AWS SSM parameter names are:
    '/{ssm_root}/splunk_hostname'
    '/{ssm_root}/splunk_port'
    '/{ssm_root}/splunk_username'
    '/{ssm_root}/splunk_password'

    If a complete set of credentials can't be collected this function will error.
    """
    assert ssm_root

    service = service.lower()
    assert service in ["api", "search"]

    hostname = env_or_param(ssm_root, "splunk_{service}_hostname_query")
    port = env_or_param(ssm_root, "splunk_{service}_port_query")
    username = env_or_param(ssm_root, "splunk_{service}_username_query")
    password = env_or_param(ssm_root, "splunk_{service}_password_query")

    return SplunkCredentials(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
    )
