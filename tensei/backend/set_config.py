from tensei.backend.aws_lambda import set_lithops_config_aws


def set_config(backend: str):

    if backend == "aws_lambda":
        set_lithops_config_aws()
    else:
        print(f"Configuration for backend '{backend}' is not implemented.")