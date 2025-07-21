from lithops import FunctionExecutor
from lithops.wait import wait

from gumeter.backend.code_engine import get_docker_username_from_config
from gumeter.config import (
    BACKEND_MEMORY,
    DOCKER_BACKENDS,
    MAX_TASKS,
    RUNTIME_NAMES,
    TAGS,
    BACKEND_STORAGE,
    Backend
)


def mock(x):
    return x


def run_warm_up(
    backend,
    times: int = 3,
    log_level: str = "INFO"
):
    storage = BACKEND_STORAGE[backend]
    runtime = RUNTIME_NAMES.get(backend)
    tag = TAGS.get(backend)
    memory = BACKEND_MEMORY.get(backend)
    runtime = f"{runtime}:{tag}"
    if backend in DOCKER_BACKENDS:
        docker_username = get_docker_username_from_config()
        runtime = f"{docker_username}/{runtime}"

    for _ in range(times):
        fexec = FunctionExecutor(
            backend=backend,
            storage=storage,
            runtime_memory=memory,
            log_level=log_level,
            runtime=runtime
        )

        futures = fexec.map(
            mock,
            list(range(MAX_TASKS))
        )
        fexec.wait(futures)
