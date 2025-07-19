import os

import yaml
from lithops.config import (
    get_default_config_filename,
    load_yaml_config
)


AWS_CONFIG_FILE = ".aws/credentials"
AWS_LITHOPS_EQUIVALENCES = {
    "aws_access_key_id": "access_key_id",
    "aws_secret_access_key": "secret_access_key",
    "aws_session_token": "session_token"
}
AWS_LAMBDA_COST_MB = 0.00001667 / 1024
AWS_LAMBDA_REQ_COST = 0.2 / 10 ** 6
AWS_S3_PUT_COST = 0.005 / 1000
AWS_S3_GET_COST = 0.0004 / 1000


def set_lithops_config_aws(
    aws_config_path: str = None,
    lithops_config_path: str = None
):
    if lithops_config_path is None:
        config_filename = get_default_config_filename()
        if config_filename:
            lithops_config = load_yaml_config(config_filename)

    home_dir = os.path.expanduser("~")
    if aws_config_path is None:
        aws_config_path = os.path.join(home_dir, AWS_CONFIG_FILE)

    aws_config = {}
    with open(aws_config_path, 'r') as f:
        lines = f.readlines()[1:]  # Skip the first line with the profile
        for line in lines:
            key, value = line.strip().split('=', 1)
            aws_config[key] = value

    if "aws" not in lithops_config:
        lithops_config["aws"] = {}

    for aws_key, lithops_key in AWS_LITHOPS_EQUIVALENCES.items():
        if aws_key in aws_config:
            lithops_config["aws"][lithops_key] = aws_config[aws_key]

    with open(config_filename, 'w') as f:
        yaml.dump(lithops_config, f)
