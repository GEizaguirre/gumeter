import os
import subprocess
import sys

from lithops import Storage

from gumeter.config import INPUT_BUCKET, StorageBackend, Backend


def remove_objects(
        storage: Storage,
        bucket: str,
        prefix: str
):
    objects = storage.list_objects(
        bucket,
        prefix=prefix
    )
    storage.delete_objects(
        bucket,
        [obj['Key'] for obj in objects]
    )
    print(
        f"Removed all objects with prefix '{prefix}'",
        f"from bucket '{bucket}'."
    )


def get_fname_w_replica_num(
        fname: str
) -> str:
    if not fname.endswith(".json"):
        raise ValueError("Filename must end with .json")

    base = os.path.splitext(fname)[0]
    directory = os.path.dirname(fname)
    if directory == "":
        directory = "."
    prefix = os.path.basename(base)

    files = [
        f for f in os.listdir(directory)
        if f.startswith(prefix) and f.endswith(".json")
    ]

    replica_num = len(files)
    new_fname = f"{base}_replica{replica_num}.json"
    return new_fname


def _run_command(command: list, cwd: str = None, out=True):
    print(f"Executing command: {' '.join(command)}")
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            cwd=cwd
        )

        stdout_lines = []
        for line in process.stdout:
            stdout_lines.append(line)
            if out:
                print(line, end='', flush=True)

        process.wait()
        stdout = ''.join(stdout_lines)

        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode,
                command,
                stdout,
                ""
            )
        return stdout

    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Stdout: {e.stdout}")
        raise e
    except FileNotFoundError:
        print(
            f"Error: Command '{command[0]}' not found.",
            "Make sure it's in your PATH."
        )
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while running command: {e}")
        raise e


def push_data_to_storage():
    storage = Storage(backend="aws_s3")
    storage.create_bucket(bucket=INPUT_BUCKET.get("aws_lambda"))
    filename = "terasort-5g"
    if storage.list_objects(bucket=INPUT_BUCKET.get("aws_lambda"), prefix=filename):
        print(f"Terasort file already exists in AWS S3 bucket '{INPUT_BUCKET.get('aws_lambda')}'. Skipping generation.")
    else:
        _run_command([
            sys.executable, "teragen/teragen.py",
            "-s", "5g",
            "-b", INPUT_BUCKET.get("aws_lambda"),
            "-k", filename,
            "-p", "100",
            "--unique-file"
        ])
        print(f"Terasort pushed to AWS S3")
    print("Downloading terasort file from AWS S3...")
    storage.download_file(
        bucket=INPUT_BUCKET.get("aws_lambda"),
        key=filename,
        file_name="/tmp/" + filename
    )
    print(f"Terasort downloaded from AWS S3")
    for sb, cb in zip([StorageBackend.IBM_COS, StorageBackend.GCP_STORAGE],
                      [Backend.CODE_ENGINE, Backend.GCP_CLOUDRUN]):
        storage = Storage(backend=sb.value)
        storage.create_bucket(bucket=INPUT_BUCKET.get(cb.value))
        print(f"Bucket '{INPUT_BUCKET.get(cb.value)}' created in {sb.value}.")
        print(f"Uploading terasort file to {sb.value}...")
        storage.put_object(
            bucket=INPUT_BUCKET.get(cb.value),
            key=filename,
            body=open("/tmp/" + filename, "rb")
        )
        print(f"Terasort pushed to {sb.value}")


if __name__ == "__main__":
    push_data_to_storage()
