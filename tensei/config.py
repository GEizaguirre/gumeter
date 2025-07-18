from enum import Enum

DEFAULT_MEMORY = 1769  # in MB
MAX_TASKS = 10
PLOTS_DIR = "plots"
RESULTS_DIR = "benchmark_results"


class Backend(Enum):
    AWS_LAMBDA = "aws_lambda"
    LOCALHOST = "localhost"


class StorageBackend(Enum):
    AWS_S3 = "s3"
    MINIO = "minio"


# Mapping of Backend to supported StorageBackends
BACKEND_STORAGE = {
    Backend.AWS_LAMBDA.value: StorageBackend.AWS_S3.value,
    Backend.LOCALHOST.value: StorageBackend.MINIO.value,
}


DISTRIBUTED_BACKENDS = [
    Backend.AWS_LAMBDA
]
