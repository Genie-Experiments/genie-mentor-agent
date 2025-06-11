import time


def reduce_context(
    context: str, reduction_percent: float, retries: int, target_length: int = 6000
) -> str:
    reduction_factor = 1 - (reduction_percent * retries)
    reduced_length = max(int(len(context) * reduction_factor), target_length)
    return context[:reduced_length]


def error_check_fn_rate_limit(error_message):
    return (
        "rate_limit_exceeded" in error_message
        and "TPM" in error_message
        and "Request too large" not in error_message
    )


def error_check_fn_request_too_large(error_message):
    return (
        "Request too large" in error_message
        or "reduce your message size" in error_message
    )


def retry_with_reduction_and_backoff(
    process_fn,
    context: str,
    max_retries: int = 3,
    reduction_percent: float = 0.1,
    delay_for_rate_limit: int = 3,
):
    retries = 0

    while retries < max_retries:
        try:
            return process_fn(context), context
        except Exception as e:
            error_message = str(e)

            if error_check_fn_rate_limit(error_message):
                retries += 1
                if retries < max_retries:
                    time.sleep(delay_for_rate_limit)
                else:
                    raise RuntimeError(
                        f"Rate limit error after {max_retries} retries: {error_message}"
                    )

            elif error_check_fn_request_too_large(error_message):
                retries += 1
                context = reduce_context(context, reduction_percent, retries)
                if len(context) < 100:
                    raise RuntimeError("Context reduced too much to process.")
            else:
                raise RuntimeError(f"Unrecoverable error: {error_message}")

    raise RuntimeError(f"Failed after {max_retries} retries.")
