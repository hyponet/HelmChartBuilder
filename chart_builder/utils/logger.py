import logging.config

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': [],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'chart_builder': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
}


def configure_logging():
    logging.config.dictConfig(DEFAULT_LOGGING)
