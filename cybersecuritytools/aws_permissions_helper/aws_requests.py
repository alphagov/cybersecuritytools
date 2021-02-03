import re
import sys
import json
from typing import List, Dict, Pattern, Any

ACTION = re.compile("((?<=DEBUG: Request\s)(\w*\W\w*))")  # noqa: W605
SERVICE = re.compile("(\w*(?=\:))")  # noqa: W605
PERMISSION = re.compile("((?<=\:)\w*)")  # noqa: W605


def main() -> None:
    input = sys.argv[1]
    with open(input, "r") as raw_log:
        debug_log = raw_log.readlines()

    requests = extract_requests(debug_log)

    with open("aws_requests.json", "w") as aws_requests:
        aws_requests.write(grouped_permissions(requests))


def regex_check(pattern: Pattern, text: str) -> Any:
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    else:
        return "No Match"


def extract_requests(raw_log: List[str]) -> str:
    """
    >>> extract_requests(['2021-01-25T16:25:56.957Z [DEBUG] \
    plugin.terraform-provider-aws_v2.70.0_x4:2021/01/2516:25:56 \
    [DEBUG] [aws-sdk-go] DEBUG: Request rds/DescribeDBInstances Details:'])
    'rds:DescribeDBInstances'
    """
    iam_actions = set()

    for line in raw_log:
        match = re.search(ACTION, line)
        if match:
            iam_action = match.group(1).replace("/", ":")
            iam_actions.add(iam_action)

    return "\n".join(sorted(iam_actions))


def grouped_permissions(requests: str) -> str:
    """
    >>> grouped_permissions(\
    'acm:DescribeCertificate\\racm:ListTagsForCertificate\\racm:RequestCertificate\
    \\rec2:AuthorizeSecurityGroupEgress\\rec2:AuthorizeSecurityGroupIngress\
    \\rec2:CreateSecurityGroup')
    '\
{"acm": ["DescribeCertificate", "ListTagsForCertificate", \
"RequestCertificate"], "ec2": ["AuthorizeSecurityGroupEgress", \
"AuthorizeSecurityGroupIngress", "CreateSecurityGroup"]}'
    """
    grouped_permissions: Dict[str, List[str]] = {}
    for request in requests.splitlines():
        match_service = regex_check(SERVICE, request)
        match_permission = regex_check(PERMISSION, request)
        if match_service not in grouped_permissions:
            grouped_permissions[match_service] = []
            grouped_permissions[match_service].append(match_permission)
        else:
            grouped_permissions[match_service].append(match_permission)
    return json.dumps(grouped_permissions)


if __name__ == "__main__":
    main()
