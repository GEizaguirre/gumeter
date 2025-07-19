from enum import Enum


TENSEI_VERSION = 1.0

DEFAULT_MEMORY = 1769  # in MB
MAX_TASKS = 1
PLOTS_DIR = "plots"
RESULTS_DIR = "benchmark_results"


class Backend(Enum):
    AWS_LAMBDA = "aws_lambda"
    AWS_BATCH = "aws_batch"
    LOCALHOST = "localhost"


class StorageBackend(Enum):
    AWS_S3 = "aws_s3"
    MINIO = "minio"


# Mapping of Backend to supported StorageBackends
BACKEND_STORAGE = {
    Backend.AWS_LAMBDA.value: StorageBackend.AWS_S3.value,
    Backend.AWS_BATCH.value: StorageBackend.AWS_S3.value,
    Backend.LOCALHOST.value: StorageBackend.MINIO.value,
}


DISTRIBUTED_BACKENDS = [
    Backend.AWS_LAMBDA,
    Backend.AWS_BATCH
]


RUNTIME_NAMES = {
    Backend.AWS_LAMBDA.value: "tensei-lambda-runtime",
    Backend.AWS_BATCH.value: "tensei-batch-runtime"
}


TAGS = {
    Backend.AWS_LAMBDA.value: "1.0",
    Backend.AWS_BATCH.value: "1",
}


BACKEND_MEMORY = {
    Backend.AWS_LAMBDA.value: 1769,
    Backend.AWS_BATCH.value: 2048,
    Backend.LOCALHOST.value: 2048
}
