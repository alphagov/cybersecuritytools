from os import environ

import boto3


def get_param_from_ssm(param: str) -> str:
    """Retrieve a decrypted SSM parameter and return the value"""
    ssm_client = boto3.client("ssm")
    response = ssm_client.get_parameter(Name=param, WithDecryption=True)
    value: str = response["Parameter"]["Value"]
    return value


def env_or_param(ssm_root: str, parameter_name: str) -> str:
    return environ.get(
        parameter_name.upper(),
        get_param_from_ssm(f"/{ssm_root}/{parameter_name.lower()}"),
    )
