import typing

# Useful Docs:
# - https://docs.python.org/2/library/logging.html#module-logging
# - https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python
CONFIG: typing.Dict[str, typing.Union[str, int]] = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {'format': '%(asctime)s %(levelname)-6s %(message)s'},
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'DEBUG',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'level': 'DEBUG',
            'filename': 'code.log',
        },
    },
    'root': {
        'level': 'INFO',
        # Enable LOG in both local file and console
        'handlers': ['console', 'file'],
    }
}
