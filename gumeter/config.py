from enum import Enum


gumeter_VERSION = 1.0

DEFAULT_MEMORY = 1769  # in MB
MAX_TASKS = 200
PLOTS_DIR = "plots"
RESULTS_DIR = "benchmark_results"


class Backend(Enum):
    AWS_LAMBDA = "aws_lambda"
    AWS_BATCH = "aws_batch"
    CODE_ENGINE = "code_engine"
    GCP_CLOUDRUN = "gcp_cloudrun"
    LOCALHOST = "localhost"


class StorageBackend(Enum):
    AWS_S3 = "aws_s3"
    IBM_COS = "ibm_cos"
    GCP_STORAGE = "gcp_storage"
    MINIO = "minio"


# Mapping of Backend to supported StorageBackends
BACKEND_STORAGE = {
    Backend.AWS_LAMBDA.value: StorageBackend.AWS_S3.value,
    Backend.AWS_BATCH.value: StorageBackend.AWS_S3.value,
    Backend.CODE_ENGINE.value: StorageBackend.IBM_COS.value,
    Backend.GCP_CLOUDRUN.value: StorageBackend.GCP_STORAGE.value,
    Backend.LOCALHOST.value: StorageBackend.MINIO.value
}


DISTRIBUTED_BACKENDS = [
    Backend.AWS_LAMBDA,
    Backend.AWS_BATCH,
    Backend.GCP_CLOUDRUN,
    Backend.CODE_ENGINE
]


RUNTIME_NAMES = {
    Backend.AWS_LAMBDA.value: "gumeter-lambda-runtime",
    Backend.AWS_BATCH.value: "gumeter-batch-runtime",
    Backend.CODE_ENGINE.value: "gumeter-code-engine-runtime",
    Backend.GCP_CLOUDRUN.value: "gumeter-gcp-cloudrun-runtime"
}


TAGS = {
    Backend.AWS_LAMBDA.value: "1.0",
    Backend.AWS_BATCH.value: "1",
    Backend.CODE_ENGINE.value: "1",
    Backend.GCP_CLOUDRUN.value: "1"
}


BACKEND_MEMORY = {
    Backend.AWS_LAMBDA.value: 1769,
    Backend.AWS_BATCH.value: 2048,
    Backend.CODE_ENGINE.value: 2048,
    Backend.GCP_CLOUDRUN.value: 2048,
    Backend.LOCALHOST.value: 2048
}

DOCKER_BACKENDS = [
    Backend.CODE_ENGINE.value,
    Backend.GCP_CLOUDRUN.value
]

INPUT_BUCKET = {
    Backend.AWS_LAMBDA.value: 'gumeter-data',
}
