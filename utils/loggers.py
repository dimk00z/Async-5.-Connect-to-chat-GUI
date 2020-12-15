import logging


def setup_logger(
        logger_name: str,
        level: int = logging.INFO,
        fmt: str = "%(levelname)s : %(message)s",
        datefmt: str = "%H:%M:%S") -> None:
    log_file_name = f'{logger_name}.log'
    formatter: logging.Formatter = logging.Formatter(fmt=fmt,
                                                     datefmt=datefmt)

    logger: logging.Logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    file_handler: logging.FileHandler = logging.FileHandler(
        log_file_name)

    file_handler.setFormatter(formatter)
    stream_handler: logging.StreamHandler = logging.StreamHandler()

    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


setup_logger('app_logger', level=logging.DEBUG)
setup_logger('watchdog_logger',
             fmt="[%(asctime)s] %(message)s", datefmt="%s")


app_logger: logging.Logger = logging.getLogger(
    "app_logger")
watchdog_logger: logging.Logger = logging.getLogger(
    "watchdog_logger")
