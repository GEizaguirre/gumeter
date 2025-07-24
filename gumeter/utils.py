import os
import subprocess
import sys

from lithops import Storage


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
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd
        )
        stdout_lines = []
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                stdout_lines.append(output)
                if out:
                    print(output, end='')
        stderr = process.stderr.read()
        process.wait()
        stdout = ''.join(stdout_lines)
        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode,
                command,
                stdout,
                stderr
            )
        return stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
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
