import typing
import logging
import functools
import time


def repeat(
    logger: logging.Logger,
    max_retries: int,
    sleep_between_retries: int,
    retry_exceptions: typing.List[typing.Any] = None,
):
    """
    Retry function decorator.

    Default behaviour is to retry on any Exception if no retry_exceptions are defined.

    Example usage:
        # Retry if we hit Google RetryError/TransportError exceptions:
        #   - Up to 3 times
        #   - Sleeping 10 seconds between each retry
        RETRY = retry(
            logger=LOG,
            max_retries=3,
            sleep_between_retries=10,
            retry_exceptions=[
                google.api_core.exceptions.RetryError,
                google.auth.exceptions.TransportError,
            ],
        )

        @RETRY
        def example(projects, filter_):
            # Expecting google cloud to throw some Exceptions in request
            results = google.cloud.logging.list_entries(projects=projects, filter_=filter_)
            return results
    """
    retry_exceptions = [Exception] if not retry_exceptions else retry_exceptions

    def wrapper(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            def raise_execption(execption: Exception):
                logger.error(f'Max retries exceeded for {func.__name__}')
                raise execption

            retries = 0

            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if retries == max_retries:
                        # All retries completed - raise
                        raise_execption(e)

                    retriable = False

                    for re in retry_exceptions:
                        if isinstance(e, re):
                            retriable = True

                    if retriable:
                        retries += 1
                        logger.error(
                            f'Failure on function {func.__name__} with exeception: {e}'
                            f'\nRetry {retries} of {max_retries}'
                            f'\nSleeping for {sleep_between_retries} seconds before retrying'
                        )
                        time.sleep(sleep_between_retries)
                    else:
                        # Exception is not retriable - raise
                        raise_execption(e)

        return wrapped

    return wrapper
