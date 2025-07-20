import os

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
