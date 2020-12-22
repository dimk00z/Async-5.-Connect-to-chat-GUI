watchdog_fmt: str = "{levelname} : {message}"
app_fmt: str = "{levelname}.{module}:{funcName}:{lineno} - (name) -  - {message}"
loggers_config: dict = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'std_formatter': {
            'format': app_fmt,
            'style': '{'

        },
        'watchdog_formatter': {
            'format': watchdog_fmt,
            'style': '{'
        },

    },
    'handlers': {
        'app_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'std_formatter',
        },

        'watchdog_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'watchdog_formatter',
        },
    },
    'loggers': {
        'app_logger': {
            'level': 'DEBUG',
            'handlers': ['app_handler'],
        },
        'watchdog_logger': {
            'level': 'INFO',
            'handlers': ['watchdog_handler'],

        },
    },
}
