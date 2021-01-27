import re
import sys
from typing import List

ACTION = re.compile("((?<=DEBUG: Request\s)(\w*\W\w*))")


def main():
    input = sys.argv[1]
    with open(input, "r") as raw_log:
        debug_log = raw_log.readlines()

    requests = extract_requests(debug_log)

    with open("aws_requests.txt", "w") as aws_requests:
        aws_requests.write(requests)


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


if __name__ == "__main__":
    main()
