import os
import sys

from gumeter.backend.aws_lambda import set_lithops_config_aws
from gumeter.backend.code_engine import get_docker_username_from_config
from gumeter.config import (
    BACKEND_STORAGE,
    RUNTIME_NAMES,
    TAGS,
    Backend
)
from gumeter.utils import _run_command


def _create_gumeter_zip():

    print("Creating gumeter.zip archive...")
    zip_filename = "gumeter.zip"
    # Define patterns for files and directories to exclude from the zip
    exclude_patterns = [
        "data/*", ".git/*", "tests/*", "gumeter.egg-info/*", "runtime/*",
        "venv/*", "gumeter.zip", "test*", ".ipynb*", ".venv/*",
        "__pycache__/*", "*/__pycache__/*", "**/__pycache__/*", "*.egg-info/*",
        "*.egg", "*.whl", ".vscode/*", "build/*", "img/*",
        "benchmark_results/*", "plots/*"
    ]

    try:
        zip_command = [
            "zip", "-r", "gumeter.zip", "."
        ]
        for pattern in exclude_patterns:
            zip_command.extend(["-x", pattern])
        _run_command(
            zip_command,
            out=False
        )
        print(f"'{zip_filename}' created successfully.")
    except Exception as e:
        print(f"Error creating zip file: {e}")
        sys.exit(1)


def deploy_aws_lambda(
    runtime_name: str = RUNTIME_NAMES[Backend.AWS_LAMBDA.value],
    tag: str = TAGS[Backend.AWS_LAMBDA.value],
    dockerfile: str = None
):

    print(f"Building AWS Lambda runtime for gumeter: {runtime_name}:{tag}")

    set_lithops_config_aws()

    _run_command(
        [
            "lithops", "runtime", "delete",
            "-b", "aws_lambda",
            "-s", BACKEND_STORAGE["aws_lambda"],
            f"{runtime_name}:{tag}",
            "--debug"
        ]
    )
    dockerfile = dockerfile or "gumeter/runtime/Dockerfile_lambda"
    _run_command(
        [
            "lithops", "runtime", "build",
            "-f", dockerfile,
            "-b", "aws_lambda",
            f"{runtime_name}:{tag}",
            "--debug"
        ]
    )
    _run_command(
        [
            "lithops", "runtime", "update",
            "-b", "aws_lambda",
            "-s", BACKEND_STORAGE["aws_lambda"],
            f"{runtime_name}:{tag}",
            "--debug"
        ]
    )
    print(f"AWS Lambda runtime '{runtime_name}:{tag}' deployment complete.")


def deploy_aws_batch(
    runtime_name: str = RUNTIME_NAMES[Backend.AWS_BATCH.value],
    tag: str = TAGS[Backend.AWS_BATCH.value]
):

    print(f"Building AWS Batch runtime for gumeter: {runtime_name}:{tag}")

    set_lithops_config_aws()

    _run_command(
        [
            "lithops", "runtime", "delete",
            "-b", "aws_batch",
            "-s", BACKEND_STORAGE["aws_batch"],
            f"{runtime_name}:{tag}",
            "--debug"
        ]
    )
    _run_command(
        [
            "lithops", "runtime", "build",
            "-f", "gumeter/runtime/Dockerfile_batch",
            "-b", "aws_batch",
            f"{runtime_name}:{tag}",
            "--debug"
        ]
    )
    _run_command(
        [
            "lithops", "runtime", "update",
            "-b", "aws_batch",
            "-s", BACKEND_STORAGE["aws_batch"],
            f"{runtime_name}:{tag}",
            "--debug"
        ]
    )
    print(f"AWS Batch runtime '{runtime_name}:{tag}' deployment complete.")


def deploy_code_engine(
    runtime_name: str = RUNTIME_NAMES[Backend.CODE_ENGINE.value],
    tag: str = TAGS[Backend.CODE_ENGINE.value]
):

    print(
        "Building AWS Code Engine runtime for gumeter:",
        f"{runtime_name}:{tag}"
    )

    docker_username = get_docker_username_from_config()

    _run_command(
        [
            "lithops", "runtime", "delete",
            "-b", "code_engine",
            "-s", BACKEND_STORAGE["code_engine"],
            f"{docker_username}/{runtime_name}:{tag}",
            "--debug"
        ]
    )
    _run_command(
        [
            "lithops", "runtime", "build",
            "-f", "gumeter/runtime/Dockerfile_code_engine",
            "-b", "code_engine",
            f"{docker_username}/{runtime_name}:{tag}",
            "--debug"
        ]
    )
    _run_command(
        [
            "lithops", "runtime", "update",
            "-b", "code_engine",
            "-s", BACKEND_STORAGE["code_engine"],
            f"{docker_username}/{runtime_name}:{tag}",
            "--debug"
        ]
    )
    print(
        f"AWS Code Engine runtime '{runtime_name}:{tag}'",
        "deployment complete."
    )


def deploy_cloudrun(
    runtime_name: str = RUNTIME_NAMES[Backend.GCP_CLOUDRUN.value],
    tag: str = TAGS[Backend.GCP_CLOUDRUN.value]
):

    print(f"Building GCP Cloud Run runtime for gumeter: {runtime_name}:{tag}")

    _run_command(
        [
            "lithops", "runtime", "delete",
            "-b", "gcp_cloudrun",
            "-s", BACKEND_STORAGE["gcp_cloudrun"],
            f"{runtime_name}:{tag}",
            "--debug"
        ]
    )
    _run_command(
        [
            "lithops", "runtime", "build",
            "-f", "gumeter/runtime/Dockerfile_cloudrun",
            "-b", "gcp_cloudrun",
            f"{runtime_name}:{tag}",
            "--debug"
        ]
    )
    _run_command(
        [
            "lithops", "runtime", "update",
            "-b", "gcp_cloudrun",
            "-s", BACKEND_STORAGE["gcp_cloudrun"],
            f"{runtime_name}:{tag}",
            "--debug"
        ]
    )

    print(
        f"GCP Cloud Run runtime '{runtime_name}:{tag}'",
        "deployment complete."
    )


def deploy_runtime(
    backend: str,
    runtime_name: str = None,
    tag: str = None
):

    if runtime_name is None:
        runtime_name = RUNTIME_NAMES.get(backend)

    if tag is None:
        tag = TAGS.get(backend)

    _create_gumeter_zip()

    if backend == "aws_lambda":
        deploy_aws_lambda(
            runtime_name,
            tag
        )
    elif backend == "aws_lambda_redis":
        deploy_aws_lambda(
            runtime_name,
            tag,
            dockerfile="gumeter/runtime/Dockerfile_lambda_redis"
        )
    elif backend == "aws_batch":
        deploy_aws_batch(
            runtime_name,
            tag
        )
    elif backend == "code_engine":
        deploy_code_engine(
            runtime_name,
            tag
        )
    elif backend == "gcp_cloudrun":
        deploy_cloudrun(
            runtime_name,
            tag
        )
    else:
        raise ValueError(
            f"Unsupported backend: {backend}. "
            "Supported backends are:"
            "aws_lambda, aws_batch, code_engine, gcp_cloudrun."
        )

    print("Cleaning up gumeter.zip...")
    try:
        os.remove("gumeter.zip")
        print("Cleanup complete.")
    except OSError as e:
        print(f"Error removing gumeter.zip: {e}")
