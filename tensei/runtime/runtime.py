import os
import subprocess
import sys


from tensei.backend.aws_lambda import set_lithops_config_aws
from tensei.config import (
    BACKEND_STORAGE,
    RUNTIME_NAMES,
    TAGS,
    Backend
)


def _create_tensei_zip():

    print("Creating tensei.zip archive...")
    zip_filename = "tensei.zip"
    # Define patterns for files and directories to exclude from the zip
    exclude_patterns = [
        "data/*", ".git/*", "tests/*", "tensei.egg-info/*", "runtime/*",
        "venv/*", "tensei.zip", "test*", ".ipynb*", ".venv/*", "__pycache__/*",
        "*/__pycache__/*", "**/__pycache__/*", "*.egg-info/*", "*.egg",
        "*.whl", ".vscode/*", "build/*", "img/*", "benchmark_results/*",
        "plots/*"
    ]

    try:
        zip_command = [
            "zip", "-r", "tensei.zip", "."
        ]
        for pattern in exclude_patterns:
            zip_command.extend(["-x", pattern])
        _run_command(zip_command)
        print(f"'{zip_filename}' created successfully.")
    except Exception as e:
        print(f"Error creating zip file: {e}")
        sys.exit(1)


def _run_command(command: list, cwd: str = None):

    print(f"Executing command: {' '.join(command)}")
    try:
        # Run the command, capture output, and check for errors
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd
        )
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            # if output:
            #     print(output, end='')
        stderr = process.stderr.read()
        if stderr:
            print(f"Stderr: {stderr}")
        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode,
                command,
                output,
                stderr
            )

    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print(
            f"Error: Command '{command[0]}' not found.",
            "Make sure it's in your PATH."
        )
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while running command: {e}")
        sys.exit(1)


def deploy_aws_lambda(
    runtime_name: str = RUNTIME_NAMES[Backend.AWS_LAMBDA.value],
    tag: str = TAGS[Backend.AWS_LAMBDA.value]
):

    print(f"Building AWS Lambda runtime for tensei: {runtime_name}:{tag}")

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
    _run_command(
        [
            "lithops", "runtime", "build",
            "-f", "tensei/runtime/Dockerfile_lambda",
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

    print(f"Building AWS Batch runtime for tensei: {runtime_name}:{tag}")

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
            "-f", "tensei/runtime/Dockerfile_batch",
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


def deploy_runtime(
    backend: str,
    runtime_name: str = None,
    tag: str = None
):

    if runtime_name is None:
        runtime_name = RUNTIME_NAMES.get(backend)
    if tag is None:
        tag = TAGS.get(backend)

    _create_tensei_zip()

    if backend == "aws_lambda":
        deploy_aws_lambda(
            runtime_name,
            tag
        )
    elif backend == "aws_batch":
        deploy_aws_batch(
            runtime_name,
            tag
        )

    print("Cleaning up tensei.zip...")
    try:
        os.remove("tensei.zip")
        print("Cleanup complete.")
    except OSError as e:
        print(f"Error removing tensei.zip: {e}")
