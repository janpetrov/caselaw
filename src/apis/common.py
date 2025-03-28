import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Callable, Collection

import tqdm


def get_api_key(key: str | None, key_name: str | None) -> str:
    if key is None and key_name is None:
        raise ValueError("Either key or key_name must be provided.")
    if key is not None:
        return key
    return os.environ[key_name]  # type: ignore


def run_inference_parallel(
    texts: Collection[str],
    infer_func: Callable[..., str | None],
    max_workers: int = 10,
    **infer_kwargs,
) -> list[str | None]:
    """Run inference in parallel for a list of texts

    Args:
        texts: Strings to process
        infer_func: Inference function to call on each text
        max_workers: Maximum number of parallel workers
        **infer_kwargs: Additional keyword arguments to pass to the inference function

    Returns:
        List of inference results
    """
    run_infer = partial(infer_func, **infer_kwargs)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        thread_iterator = executor.map(run_infer, texts)
        tqdm_iterator = tqdm.tqdm(thread_iterator, total=len(texts))
        results = list(tqdm_iterator)
    return results
