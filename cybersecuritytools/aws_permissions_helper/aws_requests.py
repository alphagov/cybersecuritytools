import re
import sys

pattern = "((?<=DEBUG: Request\s)(\w*\W\w*))"

input = sys.argv[1]

with open(input,"r") as raw_log:
    with open('aws_requests.txt','w') as aws_requests:
        for sorted_request in sorted(set([re.search(pattern,d).group(1)
            for d in raw_log if re.search(pattern, d)])):
                aws_requests.write(sorted_request.replace("/",":")+"\n")
