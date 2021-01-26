import re
import sys

pattern = "((?<=DEBUG: Request\s)(\w*\W\w*))"

with open(sys.argv[1],"r") as data:
    with open('aws_requests.txt','w') as aws:
        for s in sorted(set([re.search(pattern,d).group(1) for d in data if re.search(pattern, d)])):
            aws.write(s.replace("/",":")+"\n")
