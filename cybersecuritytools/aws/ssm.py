import boto3  # type: ignore


def get_param_from_ssm(param: str) -> str:
    """Retrieve a decrypted SSM parameter and return the value"""
    ssm_client = boto3.client("ssm")
    response = ssm_client.get_parameter(Name=param, WithDecryption=True)
    value: str = response["Parameter"]["Value"]
    return value
