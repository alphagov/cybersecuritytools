# Aws Permissions Helper 

This script will read the a logfile and extract all the requests made to create the resources and output them formatted as JSON to `aws_requests.json`

## Usage

Firstly, you will need to enable the correct logging level by terraform, before the next step run:

```bash
export TF_LOG=TRACE
``` 

Generate a logfile by running terraform and outputting everything to a file

```bash
aws-vault exec <account> -- terraform init
aws-vault exec <account> -- terraform plan
aws-vault exec <account> -- terraform apply --auto-approve 2>&1 | tee log.log
```

extract the requests by either moving the log file to `aws_requests.py` or vice versa and run

```bash
python aws_requests.py log.log
```

This will generate a JSON file grouped by service and ordered alphabeticaly eg:

```json
{
    "acm": [
        "DescribeCertificate",
        "ListTagsForCertificate",
        "RequestCertificate"
    ],
    "ec2": [
        "AuthorizeSecurityGroupEgress",
        "AuthorizeSecurityGroupIngress",
        "CreateSecurityGroup",
    ],
    "ecs": [
        "CreateCluster",
        "CreateService",
        "DescribeClusters",
        "DescribeServices",
    ]
}
```

