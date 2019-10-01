import logging
import unittest.mock

import pytest

import code.lib.retry


@pytest.fixture()
def logger():
    return unittest.mock.Mock(logging.getLogger('test'))


class CustomException(Exception):
    pass


@pytest.mark.parametrize('max_retries, sleep_between_retries', [(2, 0), (3, 0)])
def test_retry_no_retry_exceptions(logger, max_retries, sleep_between_retries):
    mock = unittest.mock.Mock()

    @code.lib.retry.repeat(logger, max_retries, sleep_between_retries)
    def func():
        mock()
        # Default exception - we didn't define any special ones
        raise Exception

    with pytest.raises(Exception):
        # Enable continue after error raised
        func()

    assert mock.call_count == (max_retries + 1)


@pytest.mark.parametrize('max_retries, sleep_between_retries', [(2, 0), (3, 0)])
def test_retry_defined_exception(logger, max_retries, sleep_between_retries):
    mock = unittest.mock.Mock()

    # Added retry_exceptions to decorator
    @code.lib.retry.repeat(logger, max_retries, sleep_between_retries, retry_exceptions=[CustomException])
    def func():
        mock()
        # Custom exception
        raise CustomException('Custom error')

    with pytest.raises(CustomException):
        # Enable continue after error raised
        func()

    assert mock.call_count == (max_retries + 1)


@pytest.mark.parametrize('max_retries, sleep_between_retries', [(2, 0), (3, 0)])
def test_retry_undefined_exception_raised(logger, max_retries, sleep_between_retries):
    mock = unittest.mock.Mock()

    @code.lib.retry.repeat(logger, max_retries, sleep_between_retries, retry_exceptions=[CustomException])
    def func():
        mock()
        raise Exception('This is not a CustomException')

    with pytest.raises(Exception):
        # Enable continue after error raised
        func()

    assert mock.call_count == 1, 'We defined CustomException, so should only try once as Exception raised'
