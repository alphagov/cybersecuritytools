import re
import sys
import json
from typing import List, Dict
from pprint import pprint

ACTION = re.compile("((?<=DEBUG: Request\s)(\w*\W\w*))")
SERVICE = re.compile("(\w*(?=\:))")
PERMISSION = re.compile("((?<=\:)\w*)")


def main():
    input = sys.argv[1]
    with open(input, "r") as raw_log:
        debug_log = raw_log.readlines()

    requests = extract_requests(debug_log)

    with open("aws_requests.json", "w") as aws_requests:
        aws_requests.write(grouped_permissions(requests))


def extract_requests(raw_log: List[str]) -> str:
    """
    >>> extract_requests(['2021-01-25T16:25:56.957Z [DEBUG] plugin.terraform-provider-aws_v2.70.0_x4: 2021/01/25 16:25:56 [DEBUG] [aws-sdk-go] DEBUG: Request rds/DescribeDBInstances Details:'])
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
    >>> grouped_permissions('acm:DescribeCertificate\\racm:ListTagsForCertificate\\racm:RequestCertificate\\rec2:AuthorizeSecurityGroupEgress\\rec2:AuthorizeSecurityGroupIngress\\rec2:CreateSecurityGroup')
    '{"acm": ["DescribeCertificate", "ListTagsForCertificate", "RequestCertificate"], "ec2": ["AuthorizeSecurityGroupEgress", "AuthorizeSecurityGroupIngress", "CreateSecurityGroup"]}'
    """
    grouped_permissions = {}
    for request in requests.splitlines():
        match_service = re.search(SERVICE, request).group(1)
        match_permission = re.search(PERMISSION, request).group(1)
        if match_service not in grouped_permissions:
            grouped_permissions[match_service] = []
            grouped_permissions[match_service].append(match_permission)
        else:
            grouped_permissions[match_service].append(match_permission)
    return json.dumps(grouped_permissions)


if __name__ == "__main__":
    main()
