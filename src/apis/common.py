import json
import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Callable, Collection, Sequence

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


def is_invalid_json(s: str | None) -> bool:
    if s is None:
        return True
    try:
        json.loads(s.replace("```json", "").replace("```", "").strip())
    except json.JSONDecodeError:
        return True
    return False


def run_inference_parallel_with_retry(
    texts: Sequence[str],
    infer_func: Callable[..., str | None],
    max_workers: int = 10,
    retries=3,
    **infer_kwargs,
):
    """Retry inference for texts that returned invalid JSON

    Args:
        texts: Strings to process
        infer_func: Inference function to call on each text
        max_workers: Maximum number of parallel workers
        retries: Number of retries for invalid JSON
        **infer_kwargs: Additional keyword arguments to pass to the inference function

    Returns:
        List of inference results
    """

    results_raw = run_inference_parallel(texts, infer_func, max_workers, **infer_kwargs)

    for _ in range(retries):
        invalid_indices = [
            i for i, result in enumerate(results_raw) if is_invalid_json(result) or not result
        ]

        if not invalid_indices:
            break

        sub_templatize = [texts[i] for i in invalid_indices]

        repair_results = run_inference_parallel(
            sub_templatize, infer_func, max_workers, **infer_kwargs
        )

        for idx, result in zip(invalid_indices, repair_results, strict=True):
            results_raw[idx] = result

    return results_raw
