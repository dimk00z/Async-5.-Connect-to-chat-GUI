import logging


def setup_logger(
        logger_name,
        level=logging.INFO,
        fmt="%(levelname)s : %(message)s",
        datefmt="%H:%M:%S"):
    log_file_name = f'{logger_name}.log'

    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    file_handler = logging.FileHandler(log_file_name)

    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()

    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


setup_logger('app_logger', level=logging.DEBUG)
setup_logger('watchdog_logger',
             fmt="[%(asctime)s] %(message)s", datefmt="%s")


app_logger = logging.getLogger("app_logger")
watchdog_logger = logging.getLogger("watchdog_logger")
