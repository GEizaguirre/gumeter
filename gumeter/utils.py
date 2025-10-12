import os
import subprocess
import sys

from lithops import Storage
from lithops.constants import LITHOPS_TEMP_DIR

from gumeter.config import INPUT_BUCKET, BACKEND_STORAGE


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


def push_data_to_storage(compute_backend: str = None, force: bool = False):
    print(
        "\033[93m\033[1mDisclaimer: "
        "This step can take a while (several minutes) and use up to 5GB of disk space.\033[0m"
    )
    aux_filename = "terasort-100m"
    aux_filepath = "/tmp/" + aux_filename
    if compute_backend and compute_backend not in BACKEND_STORAGE:
        raise ValueError(
            f"Unsupported backend '{compute_backend}'. Supported backends are: {list(BACKEND_STORAGE.keys())}")

    # Step 1: Generate teragen file locally (100m)
    final_filename = "terasort-5g"
    final_filepath = "/tmp/" + final_filename
    if os.path.exists(final_filepath) and not force:
        print(f"Terasort file already exists locally at '{final_filepath}'. Skipping generation.")
    else:
        _run_command([
            sys.executable, "teragen/teragen.py",
            "-s", "100m",
            "-b", "teragen-data",
            "-k", aux_filename,
            "-p", "8",
            "--localhost"
        ])

        # Join parts in a single file
        lithops_temp_path = os.path.join(LITHOPS_TEMP_DIR, "teragen-data")
        part_files = [os.path.join(lithops_temp_path, f) for f in os.listdir(lithops_temp_path) if
                      f.startswith(aux_filename)]

        with open(aux_filepath, 'wb') as outfile:
            for part_file in part_files:
                with open(part_file, 'rb') as infile:
                    outfile.write(infile.read())

        # Create final 5G file by repeating the 100M file 50 times (just for speeding up gumeter init)
        with open(final_filepath, "wb") as outfile:
            for _ in range(50):
                with open(aux_filepath, "rb") as infile:
                    outfile.write(infile.read())

    # Step 2: Compose backends list
    backends_to_upload = [compute_backend] if compute_backend else list(BACKEND_STORAGE.keys())

    # Step 3: Upload to each backend in the list
    for cb in backends_to_upload:
        storage_backend = BACKEND_STORAGE.get(cb)
        storage = Storage(backend=storage_backend)
        bucket_name = INPUT_BUCKET.get(cb)
        storage.create_bucket(bucket=bucket_name)

        if storage.list_objects(bucket=bucket_name, prefix=final_filename):
            print(
                f"Terasort file already exists in {storage_backend} bucket '{bucket_name}'. Skipping upload.")
        else:
            print(f"Uploading terasort file to {storage_backend}...")
            storage.put_object(
                bucket=bucket_name,
                key=final_filename,
                body=open(final_filepath, "rb")
            )
            print(f"Terasort pushed to {storage_backend}")


if __name__ == "__main__":
    push_data_to_storage("gcp_cloudrun")
